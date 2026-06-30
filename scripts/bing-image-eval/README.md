# Bing Images Eval — 58 Query Collector

Playwright-based batch collector for Bing Images, collecting labels/chips, top-10 image results, and 2 screenshots per query across the fixed 58-query eval set.

## Quick start

```bash
# Dry run: print query list, verify count/order
npm run collect:bing-images -- --dry-run

# Single query test
npm run collect:bing-images -- --query-id 58

# Full collection (headful, default)
npm run collect:bing-images -- --force

# Headless mode
npm run collect:bing-images -- --force --headless

# Validate
npm run validate:bing-images
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--dry-run` | — | Print queries, exit |
| `--force` | — | Re-collect already-ok queries |
| `--headless` | — | Run headless (default: headful) |
| `--query-id N` | — | Collect a single query by ID |
| `--start N` | 1 | First query ID |
| `--end N` | 58 | Last query ID |
| `--delay-min N` | 3000 | Min inter-query delay (ms) |
| `--delay-max N` | 6000 | Max inter-query delay (ms) |
| `--pause-every N` | 6 | Pause 15–30 s every N queries |

## Files

```
scripts/bing-image-eval/
  queries.ts        — 58 canonical queries (same as google-image-eval)
  types.ts          — TypeScript types
  browser.ts        — Browser context, Bing Images URL builder
  bingConsent.ts    — Consent / block detection & handling
  extractLabels.ts  — Chip/label extraction from Bing Images DOM
  extractResults.ts — Top-10 image result extraction
  screenshots.ts    — Two-screenshot helper
  storage.ts        — observations.json, CSVs, per-query JSONs
  collect.ts        — Main collector entrypoint
  validate.ts       — Validation & report generation
```

## Blocked / CAPTCHA handling

- Cookie consent pages: auto-accept via `#bnp_btn_accept` and similar selectors.
- CAPTCHA / unusual-traffic pages: script pauses and prompts you to resolve manually in the open browser, then press Enter to continue. The query is marked `blocked` only if unresolved.
- Consent redirects (consent.microsoft.com): auto-detect; if not auto-resolved, marked `blocked`.

## Status values

| Status | Meaning |
|---|---|
| `ok` | Successfully collected labels + ≥5 results + screenshots |
| `ok_empty` | Page loaded but no image results found |
| `blocked` | CAPTCHA / consent / unusual traffic not resolved |
| `error` | Unhandled exception (network error, timeout, etc.) |
| `partial` | Some data collected but not complete |
| `pending` | Not yet collected |
