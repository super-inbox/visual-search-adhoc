# Latest-326 Content-Gap Signal Summary

Source: Task A latest-326 result (commit `0e794cd9`, reused verbatim, NOT rerun) -- 326 total queries,
38 PASS / 86 PARTIAL / 195 FAIL / 7 UNJ, 20 zero-result queries, 18 low-result queries overall.

This document summarizes the subset of 31 queries tracked in `02_UNIFIED_QUERY_INVENTORY.csv` that were
identified as candidate signals for template discovery (i.e. queries with FAIL status and either zero or
persistently low, irrelevant results).

## Headline counts (within the 31-query candidate-family pool)
- Queries with `latest_result_count == 0` at the 7/22 run: 19
- Queries classified `catalog_content_gap` (any strength) by the latest-326 root-cause labels:
  21
- Queries classified as a SEARCH regression / candidate-loss (NOT used as content-gap evidence):
  10
- Queries flagged AMBIGUOUS / insufficient evidence:
  2

## Critical false-positive check: map and flashcard
Both `map`/`地图` and `flashcard` initially look like content gaps in the raw latest-326 numbers (map: 0-2 results;
flashcard: 12 queries in the Task A `flashcard` vertical at only 8.3% PASS with 2 zero-result queries). Cross-checking
against the 7/17 production-baseline screenshots and prior benchmark rounds shows both had **abundant relevant
Curify content historically**:
- `map`/`地图`: the 7/17 screenshot (`254_V254_map.png`, preserved at
  `images/00_excluded-search-issues/map/curify_7.17_map_60plus_results.png`) shows 60+ genuinely relevant map
  results. The zero/low-result status in the latest run is therefore a **search regression**, not a missing
  template category.
- `flashcard`: the 7/17 screenshot (`248_V248_flashcard.png`, preserved at
  `images/00_excluded-search-issues/flashcard/curify_7.17_flashcard_680_results.png`) shows 680+ relevant flashcard
  results. Same conclusion: **search regression**, not a content gap.

Both are therefore **excluded from the Top-10 template recommendations**. They are flagged instead as urgent
search-engineering findings (see Section 18 of `12_TOP10_TEMPLATE_DISCOVERY_REPORT_ZH.md`).

## Queries retained as genuine content-gap evidence
The 22 queries mapped to Top-10 candidates T01-T10 (see `03_QUERY_VERTICAL_MAPPING.csv`) all show either:
1. Zero/near-zero results at **every** historical benchmark timepoint (not just the latest run), confirmed by the
   7/17 live screenshot showing only irrelevant fallback content -- i.e. the gap predates the recent search fix
   cycle and cannot be a side-effect of it; or
2. Consistent irrelevant top-5 titles across 2+ independent evaluation methodologies (e.g. 算盘/abacus, 练习册/workbook
   cross-validated via both the 7/20 regression-50 report and the 7/22 latest run).

Full per-candidate detail: `_candidates.json` (source of truth) and `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv`.
