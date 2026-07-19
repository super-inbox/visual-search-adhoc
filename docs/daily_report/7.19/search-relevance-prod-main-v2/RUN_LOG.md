# Run Log — Curify 搜索 V2 内部修复项目

Date: 2026-07-19. Chronological log of this session's execution. All timestamps approximate (session-relative, no wall-clock timestamps were captured at each step; ordering is accurate).

1. Re-read all three authoritative design documents in full (7.17 pre-meeting, 7.18 post-meeting, changelog).
2. Verified V0/V2 worktree state: SHAs match manifest, `diff -rq` empty, original repo untouched (26 uncommitted files confirmed exactly).
3. Copied `.env.local` into both worktrees (content only, never printed); live-verified `OPENAI_API_KEY` (200 from gpt-4o-mini) and `GEMINI_API_KEY` (200 from /models) — no `BLOCKED_LLM_EVALUATION_ENVIRONMENT`.
4. Verified all 3 query file SHA-256 hashes and line counts against the spec — exact match.
5. Wrote `00_PRODUCTION_BASELINE_MANIFEST.json`, `01_WORKTREE_AND_BRANCH_SETUP.md`.
6. Deep-read V0 search pipeline (`page.tsx`, `lib/searchRewrite.ts`, `lib/searchTemplateMatch.ts`, `SearchResultsClient.tsx`) directly; dispatched a research subagent for remaining files (L2/multi-paragraph search, `searchIndex.ts`, catalog files, tests, Playwright, P0 case list).
7. `npm install` in both worktrees (required `PUPPETEER_SKIP_DOWNLOAD=true` workaround for a broken local Puppeteer browser-cache download — unrelated to app code).
8. V0 baseline established: `tsc --noEmit` clean, 111/111 vitest tests pass, `next build` succeeds.
9. Wrote `02_PRODUCTION_SEARCH_CODE_AUDIT.md`, `03_PRODUCTION_SEARCH_CALL_GRAPH.md`, `04_EXISTING_FEATURE_REGRESSION_TARGETS.md`.
10. Located the 4 historical net-negative query texts (V125/V127/V153/V271) from `docs/daily_report/7.16/easy-query-v2-validation/`.
11. Built `scripts/collector.mjs` — a real-pipeline HTTP+RSC-flight-payload collector against running `next start` servers (same method for V0 and V2). Debugged two real parsing bugs (double-increment in a hand-rolled bracket scanner; two-level JS/JSON escaping) before it worked correctly.
12. Started V0 production server (port 4501), ran the Stage 4 target/calibration case batch — found the 4 historical bugs do NOT reproduce as zero-result on V0 (`NOT_REPRODUCIBLE_ON_V0`), but found and confirmed live two real, currently-present collisions: "coffee cup" → World Cup posters (284/335 templates matched), "black friday banner" → Marvel Black Widow card ranked #1. Wrote `07_V0_TARGET_CASE_RECONFIRMATION.csv`.
13. Implemented the unified relevance scorer in V2 (`lib/relevanceScorer.ts`, `lib/relevanceScorerConfig.ts`, `lib/searchPhraseProtection.ts`), integrated into `page.tsx`, replacing the binary `hasStrict` merge gate. Iterated through several real bugs found via live testing against the running V2 server (path-agreement overriding subject-coverage penalty; narrow decomposition slots leaking subject-presence across paths; overly strict literal-phrase requirement penalizing genuinely relevant near-matches) — each documented with its specific triggering case in the code comments and `08_RELEVANCE_SCORER_DESIGN.md`.
14. Added 17 new unit tests (`lib/__tests__/relevanceScorer.test.ts`). Verified `tsc`/vitest/build clean throughout. Committed: `feat(search): unified explainable relevance scorer (directions 1, 2, 4, 5, 6, 9)`.
15. Wrote `08_RELEVANCE_SCORER_DESIGN.md`, `09_SCORE_FEATURE_AUDIT.csv`, `10_ISSUE_3_4_5_SCORING_MAPPING.md`, `11_SCORER_CALIBRATION_SET.csv`, `12_SCORER_CALIBRATION_RESULTS.csv`, `13_SCORER_CONFIG_LOCK.json`.
16. Direction 7 investigation: traced 6 broad-noise-template cases, found and confirmed the root cause (a template's `content.sections.what` description field literally contains the collision phrase as a decorative motif description). Implemented a scorer-level fix (`templateTitleCategoryBlob` field split) — no manual penalty list needed for the 4 of 6 cases it resolved. Committed: `fix(search): reduce broad template ranking noise via title/category field-split scoring (direction 7)`.
17. Wrote `14_BROAD_TEMPLATE_QUERY_RESULT_TRACE.csv`, `15_BROAD_TEMPLATE_ROOT_CAUSE_ANALYSIS.md`, `16_BROAD_NOISE_BEFORE_AFTER_SUMMARY.csv`.
18. Stage 11: re-ran `tsc`/vitest/build (clean), confirmed via `git diff --stat` that only 5 files changed across both commits (no LLM rewriter/Guard/multi-path/decomposition/UI component files touched). Wrote `18_BUILD_AND_TEST_LOG.md`, `19_FUNCTIONAL_REGRESSION_RESULTS.csv`.
19. Built the Stage 12 evaluation harness: `scripts/judge.mjs` (rubric-v1.1 LLM judge, deterministic scoring computed in code not by the LLM) + `scripts/run_eval.mjs` (concurrent batch runner, same collection method for V0/V2). Debugged a slow-sequential-run issue and added bounded concurrency.
20. Launched full evaluations in priority order per task instructions (Hard68 first, then 12 P0 + 23 targeted-regression, then Easy326, Old328 as time permits). See `34_RUN_MANIFEST.json` for exact completion status of each.
21. Statistical analysis (`scripts/stats.mjs`): McNemar's test, paired bootstrap CI, Wilcoxon signed-rank on whatever query sets completed.
22. Wrote `31_STATISTICAL_COMPARISON.md`, `32_REGRESSION_AND_IMPROVEMENT_CASEBOOK.csv`, `33_GO_NO_GO_RECOMMENDATION_ZH.md`, `34_RUN_MANIFEST.json`.

See `34_RUN_MANIFEST.json` for the authoritative record of exactly what was and was not completed, with no fabrication of unrun results.
