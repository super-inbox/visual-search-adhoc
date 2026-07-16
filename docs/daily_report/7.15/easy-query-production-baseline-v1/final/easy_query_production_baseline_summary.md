# Easy Query Production Baseline — Summary

- Authoritative query count: **328**
- Actual completed records: **328**
- Successful searches (SUCCESS/ZERO_RESULT/LOW_RESULT): **328**
- Zero-result: **12** (3.66%)
- Low-result (<5): **43** (13.11%)
- Missing records: **0**
- Query broadened (server-side rewrite/broaden banner observed): **138**
- Rewrite observed: **138**
- Network errors: **0**, Timeouts: **0**, Rate-limited: **0**, Captcha: **0**, Parse errors: **0**
- Login required encountered: **0**

## Result-count distribution

- 0: 12
- 1: 1
- 2-5: 44
- 6-10: 42
- 11-20: 53
- 20+: 176
- unavailable: 0

## Response time

- Average: 3884.9 ms
- Median: 3301.5 ms
- P90: 5403.7 ms
- P95: 5920.0 ms

## final_status breakdown

- SUCCESS: 273
- LOW_RESULT: 43
- ZERO_RESULT: 12

## By category

| category | count | zero | low | error | broadened |
|---|---|---|---|---|---|
| action | 24 | 1 | 3 | 0 | 9 |
| audience | 30 | 0 | 2 | 0 | 13 |
| festival | 24 | 0 | 0 | 0 | 20 |
| format | 35 | 1 | 2 | 0 | 8 |
| industry | 35 | 3 | 4 | 0 | 5 |
| material | 30 | 4 | 7 | 0 | 14 |
| object | 41 | 0 | 9 | 0 | 21 |
| product_category | 34 | 1 | 6 | 0 | 22 |
| scene | 35 | 0 | 3 | 0 | 13 |
| style | 40 | 2 | 7 | 0 | 13 |

## Duplicate-query consistency

- Distinct queries appearing more than once in the input: 0
- Of those, with inconsistent result counts across occurrences: 0

This is a **factual baseline summary only** — no relevance pass/fail judgement is made here. See `summaries/manual_review_queue.csv` for the human-review priority list.

