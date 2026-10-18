import datetime as dt,io,json,math,pathlib,shutil
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
s=requests.Session();s.mount('https://',HTTPAdapter(max_retries=Retry(total=3,backoff_factor=2,status_forcelist=[429,500,502,503,504])))
now=dt.datetime.now(dt.timezone.utc);season=now.year if now.month>=3 else now.year-1
sources=[]
def get(url):
 r=s.get(url,timeout=180);r.raise_for_status();sources.append({'url':url,'retrieved':dt.datetime.now(dt.timezone.utc).isoformat(),'modified':r.headers.get('Last-Modified')});return r.content
urls=[]
for repo in ['nflverse-pbp','nflverse-data']:
 try:
  r=s.get(f'https://api.github.com/repos/nflverse/{repo}/releases/tags/{season}',timeout=60)
  if r.ok:urls += [a['browser_download_url'] for a in r.json().get('assets',[]) if a['name'].endswith('.parquet') and ('play_by_play' in a['name'] or 'pbp' in a['name'])]
 except requests.RequestException:pass
urls += [f'https://github.com/nflverse/nflverse-pbp/releases/download/{season}/play_by_play_{season}.parquet',f'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.parquet']
p=None
for url in dict.fromkeys(urls):
 try:
  candidate=pd.read_parquet(io.BytesIO(get(url)))
  assert {'game_id','play_id','week','posteam','defteam','epa','play_type','yards_gained'} <= set(candidate.columns)
  assert len(candidate)>0
  p=candidate;break
 except Exception as exc:print('Source failed:',url,str(exc))
if p is None:raise RuntimeError('Real NFL data download failed. No demo data will be published. Check upstream releases.')
def n(frame,col):return pd.to_numeric(frame[col],errors='coerce') if col in frame else pd.Series(float('nan'),index=frame.index)
p=p.drop_duplicates(['game_id','play_id'])
p=p[p.play_type.isin(['pass','run']) & n(p,'qb_kneel').fillna(0).eq(0) & n(p,'qb_spike').fillna(0).eq(0) & p.posteam.notna() & p.defteam.notna()].copy()
p['epa']=n(p,'epa');p['success']=(p.epa>0).astype(float).where(p.epa.notna());p['explosive']=((p.play_type.eq('pass') & n(p,'yards_gained').ge(20)) | (p.play_type.eq('run') & n(p,'yards_gained').ge(10))).astype(float).where(n(p,'yards_gained').notna())
assert p.epa.count()>0,'No valid EPA data'
def team(key,prefix):
 rows=[]
 for name,g in p.groupby(key):
  row={'team':name,prefix+'plays':len(g),prefix+'epa_plays':g.epa.count(),prefix+'epa':g.epa.mean(),prefix+'success':g.success.mean(),prefix+'explosive':g.explosive.mean(),prefix+'yards_per_play':n(g,'yards_gained').mean()}
  for kind in ['pass','run']:row[prefix+kind+'_epa']=g.loc[g.play_type.eq(kind),'epa'].mean()
  rows.append(row)
 return pd.DataFrame(rows)
t=team('posteam','off_').merge(team('defteam','def_'),on='team');t['net_epa']=t.off_epa-t.def_epa
players=[]
roles={'passer':{'attempts':'pass_attempt','completions':'complete_pass','passing_yards':'passing_yards','passing_tds':'pass_touchdown','interceptions':'interception','sacks':'sack'},'rusher':{'carries':'rush_attempt','rushing_yards':'rushing_yards','rushing_tds':'rush_touchdown'},'receiver':{'targets':None,'receptions':'complete_pass','receiving_yards':'receiving_yards','receiving_tds':'pass_touchdown'}}
for role,metrics in roles.items():
 idcol=role+'_player_id';namecol=role+'_player_name'
 if idcol not in p:continue
 for (pid,week,tm),g in p[p[idcol].notna()].groupby([idcol,'week','posteam']):
  row={'player':g[namecol].dropna().iloc[0] if namecol in g and g[namecol].notna().any() else pid,'player_id':pid,'team':tm,'week':int(week),'role':role}
  for label,col in metrics.items():row[label]=len(g) if col is None else n(g,col).sum(min_count=1)
  if role=='passer':
   attempts=n(g,'pass_attempt').sum(min_count=1)
   row.update(epa=g.epa.mean(),cpoe=n(g,'cpoe').mean(),air_yards=n(g,'air_yards').mean(),sack_rate=n(g,'sack').mean(),interception_rate=n(g,'interception').sum(min_count=1)/attempts if attempts>0 else None)
  players.append(row)
schedule=pd.read_csv(io.BytesIO(get('https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv')))
schedule=schedule[schedule.season.eq(season)];assert not schedule.empty,'Current schedule missing'
ratings=t.set_index('team');league=p.epa.mean();games=[]
def shr(tm,side):
 r=ratings.loc[tm];count=r[side+'_epa_plays'];return (count*r[side+'_epa']+200*league)/(count+200)
for _,g in schedule.iterrows():
 if pd.notna(g.get('home_score')) or pd.notna(g.get('away_score')):continue
 h,a=g.home_team,g.away_team
 row={'date':str(g.gameday),'week':int(g.week),'away':a,'home':h,'home_margin':None,'home_win_probability':None,'status':'Insufficient data'}
 if h in ratings.index and a in ratings.index and min(ratings.loc[x,side+'_epa_plays'] for x in [h,a] for side in ['off','def'])>=50:
  he=shr(h,'off')+shr(a,'def')-league;ae=shr(a,'off')+shr(h,'def')-league
  margin=60*(he-ae)+(0 if g.get('location')=='Neutral' else 1.5)
  row.update(home_offense_vs_defense_epa=he,away_offense_vs_defense_epa=ae,home_margin=margin,home_win_probability=1/(1+math.exp(-max(-30,min(30,margin/7)))),status='Experimental / uncalibrated')
 games.append(row)
def records(df):return json.loads(df.to_json(orient='records'))
data={'season':season,'published':now.isoformat(),'latest_week':int(p.week.max()),'latest_game_date':str(p.game_date.max()) if 'game_date' in p else None,'sources':sources,'teams':records(t),'players':records(pd.DataFrame(players)),'games':games}
assert len(data['teams'])>=2 and len(data['players'])>0
out=pathlib.Path('site');out.mkdir(exist_ok=True);shutil.copy('index.html',out/'index.html')
(out/'data.json').write_text(json.dumps(data,allow_nan=False));(out/'health.json').write_text(json.dumps({'ok':True,'published':data['published'],'teams':len(t),'players':len(players)}))
print(f'LIVE DATA BUILT: season={season}, teams={len(t)}, player rows={len(players)}, latest week={data["latest_week"]}')
