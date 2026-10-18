# Publish your LIVE NFL website — no terminal needed

This is REAL DATA ONLY. There is no demo mode, no sample dataset and no API key to enter.

## Do these steps once

1. Create a **public** GitHub repository named `nfl-live`. Keep its default branch named `main`.
2. Extract this ZIP on your computer. Open the extracted folder. Upload `index.html`, `build.py`, `requirements.txt`, and this README into the ROOT of the repository using Add file → Upload files. Do not upload the ZIP itself or a containing folder.
3. Create the workflow: on GitHub choose Add file → Create new file. Enter this EXACT filename: `.github/workflows/live.yml`. Open the included `WORKFLOW.txt` on your computer, copy its ENTIRE contents into the GitHub editor, and commit to `main`.
4. Open repository Settings → Pages. Under Build and deployment, set Source to **GitHub Actions**. No branch/folder selection is needed.
5. Open Actions → Publish live NFL site → Run workflow → Run workflow. If an automatic first run failed before you enabled Pages, this new run retries after configuration.
6. Wait for the green check mark. Open Settings → Pages → Visit site, or the github-pages deployment link on the workflow run. This is your public URL.

Done. You can close your browser. Scheduled refreshes run on GitHub about once per hour. An open site checks for new published snapshots every five minutes.

### Already using Git or a desktop uploader?

The archive ALSO includes `.github/workflows/live.yml`. If your upload method preserves hidden folders, upload it with the other files and skip step 3. GitHub's browser uploader and some operating systems may hide `.github`, so the copy/paste instructions above avoid that problem. WORKFLOW.txt is only a visible convenience copy, not an automatically executed workflow.

## If something goes wrong

- No workflow listed? The file must be `.github/workflows/live.yml`, not WORKFLOW.txt and not inside another folder.
- Pages not publishing? Settings → Pages → Source must be GitHub Actions. Then rerun the workflow.
- Data download failed? Open the red workflow run and expand Download real NFL data. Upstream data may be temporarily unavailable or have changed. No synthetic data is substituted. An existing successful site stays published.
- No public URL? Publication has not yet succeeded. Check Actions rather than guessing a URL.
- No scheduled updates? Workflows must be on the default `main` branch. GitHub schedules are best effort and can be delayed. Inactive public repositories can have scheduled workflows disabled; check Actions periodically.
- Organization restrictions can block Actions or Pages. Check repository permissions with your administrator if applicable.

## What's included

Team offense/defense EPA, success, explosive rates, pass/run splits, net EPA, yards/play; weekly passing, rushing, receiving and touchdowns; upcoming matchup predictions with explainable EPA components; QB EPA, CPOE where present, air yards, sack and interception rates. Charts requiring a separate provider are labeled unavailable. Search, week filters, sortable tables and mobile layout are built in.

## What LIVE means

The scheduled job downloads real current-season nflverse data and publishes calculated results. Upstream publication determines freshness: this is NOT guaranteed real-time play-by-play streaming. Retrieval time, latest game date/week, upstream source headers and stale-publication warnings are displayed. The season switches automatically in March (January/February use the previous season).

Predictions are experimental heuristics, NOT trained or calibrated forecasts. No accuracy percentage is claimed. See Sources & Model in the website for formulas and omissions. Player stats are play-by-play-derived rather than certified official totals. No injuries, weather, lineup changes or proprietary charting are modeled.

## Verification status

The package's Python syntax was checked during creation. Its real upstream download, GitHub deployment, browser rendering and scheduled operation have NOT been executed by the assistant. Your first green workflow run performs the actual download and deployment, then HTTP-checks the public site and health endpoint. A failed final HTTP check can occur after publication, so inspect the workflow logs. Those checks are not a full browser test.

## Sources

nflverse: https://github.com/nflverse/nflverse-data and https://github.com/nflverse/nflverse-pbp
Schedules: https://github.com/nflverse/nfldata
Check upstream data licenses/attribution before redistribution or commercial use. This independent project includes no NFL logos and is not an official NFL service.
