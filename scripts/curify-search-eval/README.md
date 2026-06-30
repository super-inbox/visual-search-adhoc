# Curify Search Eval — scripts/curify-search-eval/

Playwright-based batch collector for the 58-query Curify search evaluation.
Produces per-query JSON, a master observations.json/CSV, and 2 screenshots per query
for side-by-side comparison with the Google Images eval.

## Files

| File | Purpose |
|------|---------|
| `queries.ts` | Fixed 58-query list (same as google-image-eval) |
| `types.ts` | TypeScript types for Curify observations |
| `browser.ts` | Browser context setup + `CURIFY_BASE_URL` resolution |
| `extractLabels.ts` | Extract intent chips / topic chips / related topics |
| `extractResults.ts` | Extract top-10 result cards from Examples + Templates sections |
| `screenshots.ts` | 2-screenshot workflow (page1 + scroll + page2) |
| `storage.ts` | JSON/CSV persistence and logging |
| `collect.ts` | Main entry point |
| `validate.ts` | Post-collection validation |

## Quick start

```bash
# 1. Start the dev server
npm run dev

# 2. Dry run (no browser)
npm run collect:curify-search -- --dry-run

# 3. Full collection (headful, all 58 queries)
CURIFY_BASE_URL=http://localhost:3000/en npm run collect:curify-search -- --force

# 4. Headless mode
CURIFY_BASE_URL=http://localhost:3000/en npm run collect:curify-search -- --force --headless

# 5. Single query test
CURIFY_BASE_URL=http://localhost:3000/en npm run collect:curify-search -- --query-id 58

# 6. Range
CURIFY_BASE_URL=http://localhost:3000/en npm run collect:curify-search -- --start 1 --end 10

# 7. Validate output
npm run validate:curify-search
```

## Environment variables

| Variable | Default | Example |
|----------|---------|---------|
| `CURIFY_BASE_URL` | `http://localhost:3000/en` | `http://localhost:3001/en` |

URL format: `${CURIFY_BASE_URL}/search?q=<encoded_query>`

## Query set

- 58 queries total (same as `scripts/google-image-eval/queries.ts`)
- Source: `scripts/configs/search_eval_set.json` (queries 1–58 in order)
- **cat is excluded** — cat was used only as a Google Images demo, not a formal eval query
- Why 58, not 57: query #58 (`maps`) was added on 2026-06-05 following a user-reported precision issue

## Output location

`docs/external-signal-pilot/curify-search-eval-58/`

## Redirect handling

Some queries (e.g. `maps`, `english-chinese`) may redirect from `/search?q=...` to `/topics/<slug>`.
The collector:
- Always navigates to `/search?q=<query>` first
- Records `finalUrl` after navigation settles
- Sets `redirected: true` and `redirectType: "topic"` when appropriate
- Collects labels and top-10 from whichever page the browser lands on

## Empty / error handling

- `status: "ok_empty"` — page loaded, no result cards found
- `status: "error"` — server error or navigation failure; screenshot saved, collection continues
