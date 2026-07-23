# Repeated-Query Demand Pattern Summary

All 31 tracked candidate-family queries appear in the original `easy_query_bank_v2` (created 2026-07-16) and have
persisted, unchanged, through all 4 known benchmark rounds since (v2r3_easy326 7/19, scorer_v1.1_full326 7/21,
latest_full326 Cluster-A/B fix 7/22). This means every query in the pool has been re-evaluated at least 4
independent times over a 6-day span, and every FAIL/zero-result signal used as content-gap evidence in this report
reflects a *persistent*, not a one-off, condition.

## Why this matters for gap vs. regression classification
A query that is FAIL only in the very latest run, but PASSed or had substantial results in earlier rounds
(e.g. `diploma`: 101 -> 6 -> 0; `puzzle` EN: 162 -> 0; `优惠券`: 8 -> 0), is behaving like a **regression** --
something the search pipeline used to handle and now does not. These are excluded from content-gap claims.

A query that is FAIL at **every** round, including the earliest (7/16-origin) round, and additionally shows only
irrelevant fallback content in the 7/17 live-screenshot ground truth, has never worked -- consistent with an
actual catalog content gap rather than a recent regression. All 22 queries feeding T01-T10 fall into this second
pattern (see `03_QUERY_VERTICAL_MAPPING.csv` for the mapping and `_candidates.json` for full per-candidate detail).

## Cross-validation strength
Two queries in the pool (算盘/abacus, 练习册/workbook) are additionally corroborated by a **wholly separate**
evaluation methodology: the 7/20 regression-50 root-cause report used a V0-vs-candidate identical-top5-set
comparison (distinct from the latest-326 zero/low-result methodology) and independently reached the same
CATALOG_GAP conclusion. This cross-validation is why T02 and T03 carry the highest confidence and rank #1/#3
in the final Top 10.
