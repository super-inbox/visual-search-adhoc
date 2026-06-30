# Canva Search Eval — 58-query collector

Playwright-based batch collector for Canva template search, using the fixed 58-query eval set.

## Structure

```
scripts/canva-search-eval/
  queries.ts          — 58-query list (identical to google/bing/pinterest/curify sets)
  types.ts            — TypeScript types
  browser.ts          — Playwright browser context + URL builder
  canvaConsent.ts     — Cookie consent, login wall, CAPTCHA handling
  extractLabels.ts    — Chip / filter / category label extraction
  extractResults.ts   — Top-10 template result extraction
  screenshots.ts      — Page1 / Page2 screenshot capture
  storage.ts          — observations.json, CSV, per-query JSON, logging
  collect.ts          — Main batch collector entry point
  validate.ts         — Validation script
```

## Canva URL Pattern

Primary: `https://www.canva.com/templates/?query=<encoded_query>`

The collector saves `finalUrl` because Canva may redirect to a canonical form. If this URL pattern breaks, update `CANVA_URL_PATTERN` in `browser.ts` and document the change here.

## Usage

```bash
# Dry run — print query list only
npm run collect:canva-search -- --dry-run

# Single query test
npm run collect:canva-search -- --query-id 58

# Full collection (headful — recommended first run)
npm run collect:canva-search -- --force

# Headless
npm run collect:canva-search -- --force --headless

# Range
npm run collect:canva-search -- --start 1 --end 10

# Validate
npm run validate:canva-search
```

## Browser Profile

Uses a persistent profile at `.cache/canva-search-eval-profile/` (in `.gitignore`). This preserves cookies across runs, so after handling a login wall once the session carries over.

## Login Wall / CAPTCHA Handling

- Cookie consent banners: auto-accepted.
- Login modals: the script attempts to dismiss (close button / Escape). If results are visible behind the modal, collection proceeds with a note.
- Hard login wall (results hidden): pauses and prompts the user to handle manually in the open browser window, then continues.
- CAPTCHA / bot detection: pauses for manual resolution. If running non-interactively (no TTY), marks `status = "captcha"` and moves on.
- `status = "blocked"` for geo/region restrictions.

## Empty / Error Handling

- `ok_empty` — page loaded but no templates found; screenshots saved.
- `error` — navigation or extraction failure; error logged, screenshots attempted.
- `partial` — some results extracted but below threshold.
