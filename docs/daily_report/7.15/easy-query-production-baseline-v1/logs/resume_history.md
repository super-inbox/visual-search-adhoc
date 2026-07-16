# Resume History

## Interruption 1

- Detected at: 2026-07-15T08:59:54.852Z (system time; background task `bkd8yjzv3` reported status `killed`)
- Last completed query_index before interruption: 151 (checkpoint file `checkpoints/checkpoint_after_150.json` confirms 150 completed via checkpoint; query 151 "珠宝" also completed per run_log.md before the browser was closed mid-navigation on query 152 "服装")
- Cause: background process was killed (browser context/page closed underneath the running script — "Target page, context or browser has been closed"), consistent with the harness environment restarting between turns, not a collector bug.
- 151 raw JSON files present in `raw/` at time of interruption, all independently written and valid (verified: each is a complete JSON object with `final_status` set).
- Action taken: restarted `node collect_easy_query_baseline.mjs --full` from the `scripts/` directory. Per its resume logic, queries 1-151 (all with `final_status` in {SUCCESS, ZERO_RESULT, LOW_RESULT}) were skipped via `RESUME: reusing prior completed record` log lines — no re-execution, no duplicate raw files, no browser navigation for those 151. Execution continued from query_index 152 onward.

## Targeted repair — broaden-banner text extraction bug (not an interruption)

- Detected: post-run review of `final/easy_query_production_baseline_broadened_queries.csv` showed 17/139 `query_broadened=true` records had an over-long `broadened_query`/`raw_rewrite_visible` value (>=150 chars vs. a median of 62), caused by a DOM-selection heuristic in `extractResults()` sometimes matching a large ancestor `<div>` (which is a text superset of the actual banner) instead of the self-contained banner div itself.
- This bug affected ONLY the informational `raw_rewrite_visible`/`broadened_query` text fields. It did NOT affect `result_count_observed`, `zero_result`, `low_result`, `top_results`, or the `query_broadened` boolean itself (all extracted via separate, unaffected logic) for any record.
- Fix: `noResultOrBroadenText` selection now picks the SHORTEST candidate containing "also showing results for" (the most specific / least-ancestor-polluted match) instead of the longest. See inline comment in `collect_easy_query_baseline.mjs`.
- Affected 17 query_ids: E008, E010, E013, E014, E018, E020, E022, E035, E058, E081, E144, E145, E290, E297, E301, E304, E317.
- Action: deleted only these 17 `raw/*.json` files and re-ran `node collect_easy_query_baseline.mjs --full`. Resume logic correctly skipped the other 311 already-valid records (`resumed_from_checkpoint=311`); only the 17 targeted queries were genuinely re-executed against live production. Verified all 17 now have clean, correctly-scoped `broadened_query` text.
- Note: `final_status`/`result_count_observed` for a few of these 17 differ slightly from their first-pass values (e.g. E290 "保健品" was `LOW_RESULT` on first pass, `ZERO_RESULT` on re-collection). This reflects genuine live-system non-determinism (production's LLM rewriter runs at `temperature: 0.4`, confirmed in `CODE_VERSION_AUDIT.md`/prior manifest evidence, so repeated live queries are not guaranteed byte-identical), not a collector defect. The re-collected (second) values are the ones retained in `final/`, since they reflect the corrected extraction logic end-to-end for this record.
