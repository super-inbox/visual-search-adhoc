# Easy Query Benchmark v2 vs. 生产网站 -- Relevance Evaluation Summary

Date: 2026-07-17

Input: 326 queries from `easy_query_v2_input_with_ids.csv`, executed as real browser navigations against the live production site `https://www.curify-ai.com` (Playwright/Chromium), identical methodology to the 7/15 production baseline (328 queries).

Scoring: locked rubric-v1.1 (`scoring.py`, byte-identical, reused unmodified from `easy-query-v2-validation`).

## Overall

- Total queries: 326
- Completed queries: 326 (326/326 collected, 0 errors, 0 timeouts)
- PASS: 78 (23.9%)
- PARTIAL: 137 (42.0%)
- FAIL: 111 (34.0%)
- Mean relevance score: 32.2
- Median relevance score: 26.0
- Zero-result count: 8 (2.5%)
- Low-result count: 33 (10.1%)
- Rewrite (broaden) trigger count: 181 (55.5%)

## By Scenario

| Scenario | N | PASS | PARTIAL | FAIL | Mean Score | Median Score | Zero-Result | Low-Result | Rewrite Triggered |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Creative / Cultural / Merch | 82 | 14 (17.1%) | 36 (43.9%) | 32 (39.0%) | 26.6 | 23.0 | 1 (1.2%) | 12 (14.6%) | 39 (47.6%) |
| Brand / Business Visual Assets | 82 | 19 (23.2%) | 45 (54.9%) | 18 (22.0%) | 34.2 | 33.0 | 2 (2.4%) | 8 (9.8%) | 58 (70.7%) |
| Marketing / Ecommerce | 82 | 18 (22.0%) | 35 (42.7%) | 29 (35.4%) | 33.7 | 23.0 | 3 (3.7%) | 9 (11.0%) | 45 (54.9%) |
| Education / Learning Material | 80 | 27 (33.8%) | 21 (26.2%) | 32 (40.0%) | 34.1 | 16.5 | 2 (2.5%) | 4 (5.0%) | 39 (48.8%) |

## Data Integrity

- Raw collection files present: 326/326
- Queries missing independent judgment (non-zero-result): none
- Zero-result queries (mechanically scored FAIL/0 via scoring.py): 8
- Collected via real Playwright/Chromium browser navigation to https://www.curify-ai.com (GET only, no writes).
- Original query bank and prior evaluation outputs untouched.
