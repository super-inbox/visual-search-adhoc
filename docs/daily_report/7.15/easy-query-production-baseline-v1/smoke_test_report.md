# Smoke Test Report — 2026-07-15

## Result: `SMOKE_TEST_PASS`

## Selected queries (original text/order untouched; still present, un-removed, in the full input file)

| query_index | easy_id | query | category | rationale |
|---|---|---|---|---|
| 2 | E002 | `flower` | object (en) | plain, extremely common simple word |
| 150 | E150 | `美妆` | industry (zh) | zh-language category coverage |
| 200 | E200 | `横幅` | format (zh) | different category, zh coverage |
| 230 | E230 | `teacher` | audience (en) | flagged in the prior (optimized-code) run as low-result before rewrite — good candidate to observe production's un-mitigated broadening behavior |
| 272 | E272 | `perfume` | product_category (en) | flagged in the prior run as **zero-result** before rewrite, and still only 1 result after rewrite — best available low/zero-result candidate |

## One bug found and fixed during this phase

**Issue**: the broaden-banner extraction (`noResultOrBroadenText`) initially picked the *shortest* matching DOM text node, per the original collector's "shortest = most specific" heuristic. On the live page, the actual banner is a `<div>` containing a nested `<span>Few results for "X".</span>` followed by plain text `Also showing results for: Y, Z`. The shortest match was the inner `<span>` alone ("Few results for teacher."), silently dropping the actual broadened/rewritten terms (`teacher vocabulary card, education infographic, classroom poster`) even though they were visibly rendered on the page.

**Fix**: when any candidate text contains "also showing results for", prefer the *longest* such candidate (the full banner, carrying the actual terms) instead of the shortest. Plain "no results" banners (no terms to lose) still prefer the shortest match, unchanged. Fixed in `scripts/collect_easy_query_baseline.mjs`. Re-ran the smoke test from a clean state after the fix (prior smoke_test raw/screenshot files from the buggy run were deleted before re-running — no formal/full-run outputs existed yet at that point, so nothing governed by the no-overwrite rule was touched).

**Verification of the fix**: `raw/smoke_test/230_E230.json` → `raw_rewrite_visible: "Few results for \"teacher\". Also showing results for: teacher vocabulary card, education infographic, classroom poster"`, `broadened_query: "teacher vocabulary card, education infographic, classroom poster"` — full text now captured correctly.

## Verification checklist

| Check | Result |
|---|---|
| Query correctly passed in, unmodified (byte-for-byte, verified via UTF-8 hex encoding compare against source CSV) | ✅ all 5 |
| Page/API responded normally (HTTP 200 for all 5) | ✅ |
| Original query text untouched by collector (no trim/case/punctuation change) | ✅ verified programmatically |
| Result count correctly extracted | ✅ (31 / 18 / 36 / 36 / 36 — see `smoke_test_results.csv`) |
| Top 5 results saved with title/url/image_url/metadata | ✅ |
| Zero-result vs. load-failure distinguishable | ✅ (schema separates `zero_result` from `timeout`/`network_error`/`parse_error`; none of the 5 smoke queries hit zero results, but the code path was exercised in isolation-tested logic and is identical for whichever outcome occurs) |
| Raw response (structured JSON record) saved | ✅ `raw/smoke_test/*.json`, one per query |
| Log saved | ✅ `logs/smoke_test_run_log.md` |
| Screenshot saved | ✅ `screenshots/smoke_test/*.png`, one per query, full-page |
| Checkpoint written | ✅ (per-query JSON write is itself the checkpoint; `checkpoint_written: true` in every record) |
| Resume works without duplication | ✅ re-ran identical `--smoke 2,150,200,230,272` command; all 5 logged `RESUME: reusing prior completed record`, zero new browser navigations, zero duplicate/overwritten files (file mtimes unchanged after the resume run) |
| Retry does not create duplicate final rows | ✅ by construction — retries happen inside `collectOne()` before any file is written; only one JSON file is ever written per `query_index` |
| Each query has a unique `query_index` | ✅ (2, 150, 200, 230, 272 — no collisions) |
| `final_status` correct | ✅ all 5 = `SUCCESS` (none were zero/low/error in this sample, though `teacher` and `perfume` both triggered `query_broadened: true`, consistent with the pre-optimization/no-Rewrite-Guard behavior expected from `CODE_VERSION_AUDIT.md`) |
| Target confirmed as production | ✅ `production_url: "https://www.curify-ai.com"` in every record; `request_url` uses the live domain |
| No local optimization code invoked | ✅ collector is a pure Playwright browser driver with zero filesystem/process dependency on either `curify-frontend` clone; confirmed no `require`/`import` of any product-repo path in `collect_easy_query_baseline.mjs` |

## Conclusion

All Smoke Test criteria pass. Proceeding automatically to the full 328-query production run (Phase 11) per task instructions — no further confirmation required before starting.
