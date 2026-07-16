# Easy Query Benchmark v2 -- Relevance Evaluation Summary

Date: 2026-07-17

Input: `easy_query_bank_v2_2026-07-16.csv` (326 queries, 4-scenario benchmark from `docs/daily_report/7.16/easy-query-bank-v3/`), via adapter `query_input/easy_query_v2_input_with_ids.csv` (adds `easy_id`, source file untouched).

Pipeline: identical config to the prior 300+ easy-query validation -- catalog snapshot (catalog_size=3209), LOW_RESULT_THRESHOLD=5, model gpt-4o-mini, temperature=0.4, Mode D (d=true, g=true), rewrite guard enabled. Scoring: locked rubric-v1.1 (`scripts/scoring.py`, byte-identical to the 7/15 production-baseline evaluation).

## Overall

- Total queries: 326
- Completed queries: 326 (326/326 checkpoints collected, 0 errors, 0 timeouts)
- PASS: 82 (25.2%)
- PARTIAL: 111 (34.0%)
- FAIL: 133 (40.8%)
- Mean relevance score: 35.4
- Median relevance score: 33.0
- Low-result count (first_pass_count < 5): 196 (60.1%)
- Rewrite trigger count: 196 (60.1%)

## By Scenario

| Scenario | N | PASS | PARTIAL | FAIL | Mean Score | Median Score | Low-Result | Rewrite Triggered |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Creative / Cultural / Merch | 82 | 14 (17.1%) | 33 (40.2%) | 35 (42.7%) | 31.2 | 27.5 | 43 (52.4%) | 43 (52.4%) |
| Brand / Business Visual Assets | 82 | 18 (22.0%) | 38 (46.3%) | 26 (31.7%) | 35.5 | 36.0 | 60 (73.2%) | 60 (73.2%) |
| Marketing / Ecommerce | 82 | 24 (29.3%) | 24 (29.3%) | 34 (41.5%) | 38.0 | 30.0 | 54 (65.9%) | 54 (65.9%) |
| Education / Learning Material | 80 | 26 (32.5%) | 16 (20.0%) | 38 (47.5%) | 37.0 | 12.0 | 39 (48.8%) | 39 (48.8%) |

## Manual Review Queue

- P0 (FAIL / UNJUDGABLE): 133
- P1 (PARTIAL with MODERATE+ drift or <3 judgeable results): 38
- P2 (other PARTIAL, or PASS with residual drift): 73
- Total flagged: 244 / 326

## Data Integrity

- Checkpoint files present: 326/326
- Missing checkpoints: none
- Queries missing independent judgment (non-zero-result): none
- Zero-result queries (mechanically scored FAIL/0 via scoring.py, no judgment needed): 34
- Original query bank file untouched throughout (read-only via adapter CSV).
- Prior evaluation outputs (7.15 production baseline, 7.16 comparison, bank v2/v3) untouched.
