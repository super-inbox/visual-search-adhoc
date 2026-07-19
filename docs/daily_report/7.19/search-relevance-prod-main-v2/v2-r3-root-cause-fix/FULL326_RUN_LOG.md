# Full Easy326 Run Log — V2-R3 Stage

Chronological log of this stage's execution (session-relative order, accurate; wall-clock times approximate).

1. Read charter/task spec in full. Confirmed scope: full-326 comparison only, no code/config changes, no tuning
   from full-326 results, no Hard68/old-328/P0-12, no push/PR/merge/deploy.
2. **Preconditions (charter §二)**, all verified before any execution:
   - V0 worktree HEAD = `05e5f2d332778ac52c712dd2429f4a8f4e7c3673`, clean.
   - V2-R1 worktree HEAD = `32f6282a240edfa87edae5a0ba5308aecf462466`, clean.
   - V2-R3 worktree HEAD = `a811f06f8838e330e08caa4d3c4952d6ab10554d` (matches required SHA), clean, on branch
     `baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19`.
   - `09_V2_R3_CONFIG_LOCK.json` exists, `frozen: true`.
   - `08_V2_R3_TARGETED_GATE_RESULT.md` verdict = `FINAL_STATUS: V2_R3_TARGETED_FIX_COMPLETE`, all 20 conditions PASS.
   - No process listening on ports 4500-4509 or 3000; no stray `next start`/`next dev`/eval-runner node processes.
   - All preconditions satisfied — proceeded (no `BLOCKED_V2_R3_FULL326_PRECONDITION`).
3. **Reuse-eligibility check (charter §三)**: located the existing full-326 V0 and V2-R1 results from the
   2026-07-19 03:31 run (`docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/EASY326_V0.csv`,
   `EASY326_V2.csv`). Verified via `00_PRODUCTION_BASELINE_MANIFEST.json` and `34_RUN_MANIFEST.json` that: V0 SHA,
   V2-R1 SHA, query file (`easy_query_bank_v2_2026-07-16.csv`, SHA-256 re-verified this stage), catalog file
   hashes (re-verified identical across all three worktrees this stage), model (gpt-4o-mini), collection method
   (`scripts/collector.mjs`), judge method/prompt/rubric (`scripts/judge.mjs`, rubric-v1.1), retry/cache policy —
   all identical to what would be used for a fresh V2-R3 run. Concluded: V0 and V2-R1 results are reusable as-is;
   only V2-R3 needs a fresh collection.
4. Rebuilt V2-R3 (`npm run build`) to guarantee the production build reflects the exact committed HEAD (source
   file mtimes 21:45-21:50 predated the existing `.next` build at 22:06, so this was a belt-and-suspenders
   rebuild, not a fix for a detected staleness).
5. Started V2-R3 `next start` on port 4503; live-verified with a real `/en/search?q=coffee cup` request
   (HTTP 200, valid RSC flight payload present).
6. Wrote `scripts/run_eval_single.mjs` — a single-target wrapper that imports the SAME `collectQuery` (from
   `collector.mjs`) and `judgeResultSet`/`loadEnv` (from `judge.mjs`) used by the morning's `run_eval.mjs`, with
   no reimplementation of collection or judging logic, differing only in querying one base URL instead of two.
7. Ran the full 326-query bank against V2-R3 (port 4503), concurrency 6, retry-on-failure per the existing
   collector/judge retry policy. Completed 326/326, 0 technical errors, in-progress output written incrementally
   every 5 completions. Final log line: `[run_eval_single] DONE 326/326`.
8. Stopped the V2-R3 server; confirmed port 4503 clear and no zombie node processes remained.
9. Ran the analysis pipeline (`scripts_analysis/build_reports.py`): verified query-text alignment across the
   query bank and all three result sets for all 326 row indices (exact match, 0 mismatches); verified 0 duplicate
   row_index and 0 empty labels in all three sets; built the per-row V2-R3 results file, the 3-way paired file,
   and the McNemar/paired-bootstrap/Wilcoxon statistics for all three pairwise comparisons (V0→V2-R1, V0→V2-R3,
   V2-R1→V2-R3).
10. Ran supplementary diagnostics: flooding/full-catalog-flooding/broad-noise counts per version; language (zh/en)
    and query-shape (single-word vs multi-word) slice breakdowns; rewrite-triggered-only R1→R3 comparison; and a
    direct diff of zero-result query sets across all three versions to identify newly-introduced zero-result
    cases. This last check surfaced 5 queries (`online store banner`, `积分卡`, `证书`, `microscope`, plus the
    already-documented `算盘`) that flip from non-zero on V2-R1 to zero on V2-R3 — the key negative finding.
11. Cross-referenced the original 50-query V0→V2-R1 regression set (`02_V2_R3_REGRESSION_TRACE.csv`) and the
    targeted-stage's 5 flagged new holdout regressions and 4 flagged score-softening cases (coffee cup, 贴纸,
    咖啡馆菜单, 吉祥物) against the full-326 live data.
12. Applied the 15 gate conditions of charter §六 mechanically to the computed numbers: 4 fail outright (#2 FAIL
    count, #3 zero-result count, #4 improved≥regressed vs V0, #15 clear net improvement), 1 is mixed (#5,
    clearly-better-than-V2-R1 holds for relevance labels but not for zero-result count). Verdict:
    `NOT_READY_TO_REPLACE_PRODUCTION`.
13. Wrote `13_V2_R3_EASY326_RESULTS.csv`, `14_V0_V2_R1_V2_R3_EASY326_PAIRED.csv`,
    `15_V2_R3_EASY326_STATISTICAL_COMPARISON.md`, `16_V2_R3_EASY326_GATE_RESULT.md`,
    `17_V2_R3_EASY326_RUN_MANIFEST.json`, this run log.
14. Per charter §六 ("若不通过：立即停止..."), stopped here. Did not run Hard68, old-328, or P0-12. Did not adjust
    any scorer parameter or `09_V2_R3_CONFIG_LOCK.json`. Did not modify any code. Did not push, open a PR, merge,
    or deploy.
15. **Cleanup verification (charter §八)**: V2-R3 server process confirmed stopped, port 4503 confirmed clear, no
    other stray eval-related processes found. All three worktrees (`V0`, `V2-R1`, `V2-R3`) re-verified clean
    (`git status --porcelain` empty) and at their expected SHAs (`05e5f2d3...`, `32f6282a...`, `a811f06f...`
    respectively) at the end of this stage. No new git commit created in any worktree.
