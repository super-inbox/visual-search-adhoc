# Input/Output Integrity — Full-326 Latest Candidate Run (0e794cd9)

## Input
- Authoritative 326-query bank: `easy_query_bank_v2_2026-07-16.csv` (SHA-256
  `c5b1368e33ab601884ad91aff21802c64391bee781b6daa2f3ef50e4d54a08c6`), 326 data rows, 326 unique queries, 0 duplicates,
  0 missing query values (verified in Step 1).

## Output
- `eval_raw/CANDIDATE_LATEST_EASY326.csv`: 326 data rows (327 lines incl. header).
- `row_index` range 0–325, all 326 values present and unique — no gaps, no duplicates.
- Row-by-row query-text alignment against the bank verified: 326/326 match (`02_QUERY_COMPLETENESS.csv`).
- `ok=False` (collector error) rows: **0**.
- Timeout rows: 0 (collector timeout is 30000ms per query; no row hit it — max observed `elapsed_ms` well under 30s).
- Retries: `run_eval_single.mjs`'s collector retry (1x after a failed attempt, 500ms delay) is **not counted as a
  separate output row** — it only affects `elapsed_ms`/success of the single row it retries within. 0 rows show
  evidence of having needed the retry (all `ok=True` on presumed first attempt; the script does not log which
  attempt succeeded, consistent with the original 7/19/7/21 methodology which also does not log this).
- `run_eval_single.mjs` DONE marker: `DONE 326/326`. Wall-clock: 2026-07-22 15:25:58 → 15:29:43 (≈3m45s), concurrency 6.

## Label totals
| label | count |
|---|---:|
| PASS | 38 |
| PARTIAL | 86 |
| FAIL | 195 |
| UNJUDGABLE | 7 |
| **Total** | **326** |

PASS + PARTIAL + FAIL + UNJUDGABLE = 326 ✓ (matches total input query count).

## UNJUDGABLE rows (7) — all `NO_JUDGEABLE_RESULTS`, not technical/collector errors
| row | query | total_results | reason |
|---:|---|---:|---|
| 21 | action figure | 99 | NO_JUDGEABLE_RESULTS |
| 140 | 蜡烛标签 | 11 | NO_JUDGEABLE_RESULTS |
| 165 | banner | 114 | NO_JUDGEABLE_RESULTS |
| 216 | 开箱照 | 21 | NO_JUDGEABLE_RESULTS |
| 218 | 前后对比图 | 36 | NO_JUDGEABLE_RESULTS |
| 244 | 直播预告横幅 | 30 | NO_JUDGEABLE_RESULTS |
| 262 | 课堂装饰海报 | 41 | NO_JUDGEABLE_RESULTS |

`NO_JUDGEABLE_RESULTS` means the judge model returned zero labels it recognized as judgeable (all `UNJUDGABLE` labels
from the LLM itself, per `judge.mjs`'s rubric — not a call failure). This is a legitimate rubric outcome, defined
identically to the 7/19 and 7/21 runs, and occurred at a similar rate (7/326 ≈ 2.1% here vs. 10/326 ≈ 3.1% for the
7/21 previous-candidate run and 12/326 ≈ 3.7% for the 7/21 production-baseline run) — no anomaly.

## Zero-result / low-result reproducibility
Both `zero_result` and `low_result` are row-level boolean fields directly present in
`eval_raw/CANDIDATE_LATEST_EASY326.csv`, independently recomputable from `total_results` (`zero_result = total_results
== 0`; `low_result = 0 < total_results < 5`). See `09_ZERO_LOW_RESULT_ANALYSIS.csv` for the full reproduction.

## Conclusion
Run is **complete** — all 326 authoritative queries are represented exactly once, no silent skips, no unresolved
errors, aggregate totals reconcile with row-level data.
