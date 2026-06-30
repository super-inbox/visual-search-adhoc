# Google Images Eval Collector

Collects Google Images labels (chips) and top-10 organic results for a fixed set of **58 queries**.

## Setup

```bash
npm install
npx playwright install chromium
```

## Dry run

Print all 58 queries without starting a browser:

```bash
npm run collect:google-images -- --dry-run
```

Output:

```
1. 单词
2. 卡通
3. 吉伊卡哇
...
55. chiikawa
56. samurai
57. genshin
58. maps
```

## Run a single query

```bash
npm run collect:google-images -- --query-id 1
npm run collect:google-images -- --query "maps"
```

## Run a range

```bash
npm run collect:google-images -- --start 1 --end 10
```

## Run all 58

```bash
npm run collect:google-images
```

## Resume (default behavior)

`complete` queries are skipped automatically:

```bash
npm run collect:google-images
```

## Force re-run a query

```bash
npm run collect:google-images -- --query-id 3 --force
```

## Validate results

```bash
npm run validate:google-images
```

## Stop

Press `Control + C`. Progress is saved after each query — no results are lost.

## CAPTCHA / Google verification

If Google shows a verification page:

1. Do **not** close the browser window.
2. Complete the verification manually in the open browser.
3. Wait until the Google Images results page is fully visible.
4. Return to this terminal and press **Enter**.
5. The script resumes automatically from this query.

The script will **never** attempt to bypass verification automatically.

## Output

Results are saved to `docs/external-signal-pilot/google-image-eval-58/`:

```
data/
  observations.json          — all 58 queries, structured results
  collection_progress.csv    — CSV progress tracker
  collection_errors.json     — per-query error log
  run.log                    — full run log
  validation-report.json     — validation check results
  per-query/
    001-q001.json            — per-query doc (camelCase, matches task spec format)
    ...
    058-maps.json
screenshots/
  001-q001/
    google-images-page1.png  — first viewport screenshot
    google-images-page2.png  — after scrolling one viewport
  ...
  058-maps/
    google-images-page1.png
    google-images-page2.png
```

## Why 58 queries

The previous collection (`google-image-eval-57`) excluded `maps`. This run adds `maps` (group: `user-report-2026-06-05`) as query #58 per external-signal pilot requirements.

`cat` is **not** in the formal eval set — it was used only as a field-format example in earlier docs.

## Browser profile

Stored in `.cache/google-image-eval-profile/` — excluded from git.

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--dry-run` | — | Print queries, no browser |
| `--start N` | 1 | First query_id to run |
| `--end N` | 58 | Last query_id to run |
| `--query-id N` | — | Run single query by ID |
| `--query "text"` | — | Run single query by text |
| `--force` | — | Re-run complete queries |
| `--headless` | — | Headless browser (default: headful) |
| `--delay-min N` | 4000 | Min delay between queries (ms) |
| `--delay-max N` | 8000 | Max delay between queries (ms) |
| `--pause-every N` | 5 | Extra pause every N queries |
| `--validate-only` | — | Run validation only |
