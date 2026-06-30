# Pinterest Search Eval — 58 Query Collector

Playwright-based batch collector for Pinterest pin search, collecting labels/chips, top-10 pin results, and 2 screenshots per query across the fixed 58-query eval set.

## Quick start

```bash
# Dry run: print query list, verify count/order
npm run collect:pinterest-search -- --dry-run

# Single query test
npm run collect:pinterest-search -- --query-id 58

# Full collection (headful, default)
npm run collect:pinterest-search -- --force

# Headless mode
npm run collect:pinterest-search -- --force --headless

# Validate
npm run validate:pinterest-search
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
| `--pause-every N` | 8 | Pause 20–35 s every N queries |

## Files

```
scripts/pinterest-search-eval/
  queries.ts           — 58 canonical queries (same set as other collectors)
  types.ts             — TypeScript types
  browser.ts           — Browser context, Pinterest search URL builder
  pinterestConsent.ts  — Cookie consent / login wall detection & handling
  extractLabels.ts     — Guided search chip extraction
  extractResults.ts    — Top-10 pin result extraction
  screenshots.ts       — Two-screenshot helper
  storage.ts           — observations.json, CSVs, per-query JSONs
  collect.ts           — Main collector entrypoint
  validate.ts          — Validation & report generation
```

## Login wall / CAPTCHA handling

- **Cookie consent**: auto-accept via known selectors.
- **Login modal**: attempt to close via X/close button or Escape key.
- **Hard login wall** (page is fully blocked): script pauses and prompts you to handle it manually in the browser, then press Enter. Query is marked `login_required` only if unresolved.
- **CAPTCHA / bot block**: script pauses for manual resolution. Query marked `captcha` if unresolved.
- **Never** bypasses login, CAPTCHA, or bot detection programmatically.

## Status values

| Status | Meaning |
|---|---|
| `ok` | Successfully collected labels + ≥5 results + screenshots |
| `ok_empty` | Page loaded but no pin results |
| `login_required` | Login wall blocked and not cleared |
| `captcha` | CAPTCHA / bot block not cleared |
| `blocked` | Other access block |
| `error` | Unhandled exception |
| `partial` | Some data collected but not complete |
| `pending` | Not yet collected |
