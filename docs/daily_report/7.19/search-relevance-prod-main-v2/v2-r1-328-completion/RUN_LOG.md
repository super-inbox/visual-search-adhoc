# Run Log — V2-R1 Freeze + Old-328 Backfill

Date: 2026-07-19. Chronological log of this stage's execution (session-relative order, accurate).

1. Verified V2-R1 worktree state: `git status --short` clean, branch = `baobao/search-relevance-prod-main-v2-2026-07-19`, HEAD = `32f6282a240edfa87edae5a0ba5308aecf462466` (matches expected short SHA `32f6282a`). No state mismatch — proceeded without blocking.
2. Confirmed no pre-existing `baobao/search-relevance-prod-main-v2-r1-frozen-2026-07-19` branch.
3. Created the frozen branch: `git branch baobao/search-relevance-prod-main-v2-r1-frozen-2026-07-19 32f6282a240edfa87edae5a0ba5308aecf462466`. Did not check it out — worktree remained on the original branch, which already points at the identical SHA.
4. Read `34_RUN_MANIFEST.json`, `RUN_LOG.md`, `33_GO_NO_GO_RECOMMENDATION_ZH.md`, `13_SCORER_CONFIG_LOCK.json`, and the prior run's `scripts/run_eval.mjs`, `scripts/collector.mjs`, `scripts/judge.mjs`, `scripts/stats.mjs` in full to confirm exact reproducibility of collection method, judge method, model, prompts, rubric, thresholds, timeout, retry, and cache policy. All confirmed reproducible without modification — no `BLOCKED_PREVIOUS_EVAL_CONFIG_NOT_REPRODUCIBLE`.
5. Verified the old-328 query file (`easy_queries_cleaned_300_plus_2026-07-14.csv`) — 328 data rows, SHA-256 `682ed08a...b32f3e`, `query`/`language` columns matching `run_eval.mjs` defaults.
6. Confirmed both worktrees already had a production build (`.next/`) and `node_modules` from the prior session's run — no rebuild needed, no dependency changes.
7. Started both production servers fresh (`npx next start -p 4501` for V0, `-p 4502` for V2-R1) so both sides began from symmetric (cold) in-memory rewrite-cache state, matching the prior run's practice. Verified both return HTTP 200 (after the expected 307 locale redirect) before starting the batch.
8. Ran `scripts/run_eval.mjs` against the 328-query file. First invocation passed the literal string `"Infinity"` for the `limit` positional arg, which `parseInt`'d to `NaN` and silently produced 0 queries — caught immediately (0/0 output), corrected by passing an empty string instead (falls through to the script's own `Infinity` default), re-ran successfully.
9. Batch completed 328/328 queries, concurrency 6, 0 technical collection failures, 0 error rows, 11 legitimate UNJUDGABLE per side. Output written to `eval_raw/OLD328_{V0,V2,PAIRED}.csv`.
10. Ran `scripts/stats.mjs` (unmodified) on the paired CSV: McNemar, paired bootstrap (2000 resamples), Wilcoxon signed-rank — all computed on real paired data, no fabricated values.
11. Computed mean/median relevance score and full improved/regressed query lists directly from the paired CSV (small one-off Node script, not committed to `scripts/` since it duplicates no reusable logic — read-only analysis, not part of the eval pipeline).
12. Copied `eval_raw/OLD328_{V0,V2,PAIRED}.csv` to `01_V0_OLD328_RESULTS.csv`, `02_V2_R1_OLD328_RESULTS.csv`, `03_V0_V2_R1_OLD328_PAIRED.csv` per the required output naming. No file under the parent `search-relevance-prod-main-v2/` directory (prior 326-query report) was modified.
13. Wrote `04_OLD328_STATISTICAL_COMPARISON.md` — full statistical comparison, improved/regressed query lists, and explicit reasoning for why the 328 result (net-positive on PASS/FAIL/score, net-negative on zero-result/low-result) does not overturn the 326-set regression finding.
14. Wrote `05_V2_R1_STATUS_AFTER_328_ZH.md` — Chinese-language status summary covering all 7 required points (freeze confirmed, 328 backfilled, consistency with 326, NOT_READY_TO_REPLACE_PRODUCTION unchanged, V2-R1 retained as first-round experimental result, not deployable, V0 remains production fallback).
15. Wrote `00_V2_R1_FREEZE_MANIFEST.json` and this `RUN_MANIFEST.json`/`RUN_LOG.md`.
16. Final verification: both worktrees `git status --short` clean, no commits/amends/resets/rebases/pushes/PRs/merges/deploys performed at any point in this stage, no V2-R2 created, no Strict/Relaxed scorer changes started.

See `RUN_MANIFEST.json` for the authoritative machine-readable record of this stage's results and completion status.
