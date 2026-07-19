# Final Delivery Manifest — 2026-07-20

本清单覆盖 Curify Search Relevance V2 交付涉及的全部文件：代码仓库（`curify-frontend`，worktree `curify-frontend-search-v2-r3-2026-07-19`，branch `baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19`）与评测仓库（`visual-search-adhoc`，worktree `visual-search-adhoc-v2-delivery-2026-07-20`，branch `baobao/search-relevance-v2-delivery-2026-07-20`）。

- 类别 A（必须提交）：37 项，全部已提交并 push
- 类别 B（报告引用证据）：62 项，全部已提交并 push
- 类别 C（可选中间结果）：5 项，已提交并 push（体量不大，判断保留有利于复现）
- 类别 D（不应提交，已确认排除）：6 项（按目录/模式分组列出，非逐文件）
- 类别 E（其他任务文件，已确认排除）：2 项（按目录/模式分组列出，非逐文件）

完整机器可读版本见同目录 `FINAL_DELIVERY_MANIFEST_2026-07-20.csv` / `.json`。

---

## A. 必须提交的正式产物（代码 + 核心报告 + 门禁结果）

| Repo | 路径 | 用途 | 报告引用 | sha256 (前12位) | 大小(bytes) |
|---|---|---|---|---|---:|
| visual-search-adhoc | `docs/daily_report/7.19/easy-query-search-solution-design-post-meeting/EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-18_CHANGELOG.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `6cc11843d48d` | 9334 |
| visual-search-adhoc | `docs/daily_report/7.19/easy-query-search-solution-design-post-meeting/EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-18_POST_MEETING_ZH.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `e8286128db19` | 39445 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/08_RELEVANCE_SCORER_DESIGN.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `28654f491ee7` | 7028 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/15_BROAD_TEMPLATE_ROOT_CAUSE_ANALYSIS.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `b5b443b2e961` | 9529 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/16_BROAD_NOISE_BEFORE_AFTER_SUMMARY.csv` | Directly cited by Work Report appendix (§18) as primary evidence | True | `6e27c0e7994e` | 3498 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/31_STATISTICAL_COMPARISON.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `3a180ac6dce6` | 8565 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/33_GO_NO_GO_RECOMMENDATION_ZH.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `5580a5c743b7` | 9306 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r1-328-completion/04_OLD328_STATISTICAL_COMPARISON.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `6eb65fd3275c` | 11053 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r1-328-completion/05_V2_R1_STATUS_AFTER_328_ZH.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `db0004a01ceb` | 6724 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r2-relaxed-gate/01_RELAXED_REGRESSION_ROOT_CAUSE.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `1c807a9f3229` | 14610 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r2-relaxed-gate/02_REGRESSED_QUERY_RELAXED_TRACE.csv` | Directly cited by Work Report appendix (§18) as primary evidence | True | `7cadb0583791` | 44681 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/01_V2_R3_ROOT_CAUSE_REVALIDATION.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `11afd315ba4a` | 22825 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/03_V2_R3_CASE_SPLIT.csv` | Directly cited by Work Report appendix (§18) as primary evidence | True | `d23b7a36680e` | 33619 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/05_V2_R3_MINIMAL_FIX_DESIGN.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `4bb6aa8c51de` | 25399 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/08_V2_R3_TARGETED_GATE_RESULT.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `6599e59d690a` | 14440 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/10_V2_R3_IMPLEMENTATION_SUMMARY.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `b23a4a98e0c1` | 9619 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/11_V2_R3_ENGINEERING_CHECKS.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `0f3456bc43ff` | 4417 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/13_V2_R3_EASY326_RESULTS.csv` | Directly cited by Work Report appendix (§18) as primary evidence | True | `edb57d081c16` | 137568 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/14_V0_V2_R1_V2_R3_EASY326_PAIRED.csv` | Directly cited by Work Report appendix (§18) as primary evidence | True | `fb4ee94e528a` | 58792 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/15_V2_R3_EASY326_STATISTICAL_COMPARISON.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `7f83bbe29411` | 10835 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/16_V2_R3_EASY326_GATE_RESULT.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `af6f4d79a882` | 5892 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/17_V2_R3_EASY326_RUN_MANIFEST.json` | Directly cited by Work Report appendix (§18) as primary evidence | True | `b646bfb78052` | 6896 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/18_V2_R3_FREEZE_AND_ARCHIVE_MANIFEST.json` | Directly cited by Work Report appendix (§18) as primary evidence | True | `3423a39791bf` | 2597 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/FULL326_RUN_LOG.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `b4a948ce67a2` | 5676 |
| visual-search-adhoc | `docs/daily_report/7.20/curify-search-relevance-v2-work-report/CURIFY_SEARCH_RELEVANCE_V2_WORK_REPORT_2026-07-18_TO_2026-07-20_ZH.md` | Directly cited by Work Report appendix (§18) as primary evidence | True | `4522199da03e` | 30239 |
| curify-frontend | `lib/relevanceScorer.ts` | Unified relevance scorer implementation (directions 3/4/5) | True | `b8a555c514f9` | 13824 |
| curify-frontend | `lib/relevanceScorerConfig.ts` | Frozen scorer weight configuration | True | `ee897467a188` | 6436 |
| curify-frontend | `lib/searchPhraseProtection.ts` | Protected-phrase list and matching logic (direction 6) | True | `3a15bdd92bb9` | 5403 |
| curify-frontend | `lib/__tests__/relevanceScorer.test.ts` | 143-test unit suite covering scorer, phrase protection, multi-path, sibling scoring, coverage gate | True | `dc7cddf45171` | 20960 |
| curify-frontend | `app/[locale]/(public)/search/page.tsx` | Search page wiring: candidate merge, scorer invocation, sibling/coverage integration | True | `ba3d212e146a` | 62996 |
| visual-search-adhoc | `docs/daily_report/7.20/curify-search-relevance-v2-work-report/FINAL_DELIVERY_REQUIREMENT_AUDIT_2026-07-20.md` | Requirement-by-requirement coverage audit against boss's 2026-07-20 delivery ask | N/A (this session's own output) | `(generated after this manifest; see file directly)` | 0 |
| visual-search-adhoc | `docs/daily_report/7.20/curify-search-relevance-v2-work-report/FINAL_DELIVERY_REQUIREMENT_AUDIT_2026-07-20.csv` | Machine-readable version of the same audit | N/A (this session's own output) | `(generated after this manifest; see file directly)` | 0 |
| visual-search-adhoc | `docs/daily_report/7.20/curify-search-relevance-v2-work-report/FINAL_DELIVERY_MANIFEST_2026-07-20.md` | Full file-level delivery manifest (this document set) | N/A (this session's own output) | `(generated after this manifest; see file directly)` | 0 |
| visual-search-adhoc | `docs/daily_report/7.20/curify-search-relevance-v2-work-report/FINAL_DELIVERY_MANIFEST_2026-07-20.csv` | Machine-readable manifest | N/A (this session's own output) | `(generated after this manifest; see file directly)` | 0 |
| visual-search-adhoc | `docs/daily_report/7.20/curify-search-relevance-v2-work-report/FINAL_DELIVERY_MANIFEST_2026-07-20.json` | Machine-readable manifest (JSON) | N/A (this session's own output) | `(generated after this manifest; see file directly)` | 0 |
| visual-search-adhoc | `docs/daily_report/7.20/curify-search-relevance-v2-work-report/CODE_VALIDATION_FINAL_2026-07-20.md` | Independently re-run TypeScript / unit test / production build results | N/A (this session's own output) | `(generated after this manifest; see file directly)` | 0 |
| visual-search-adhoc | `docs/daily_report/7.20/curify-search-relevance-v2-work-report/FINAL_ARTIFACT_INTEGRITY_CHECK_2026-07-20.md` | CSV/JSON/path/hash integrity verification of evaluation repo artifacts | N/A (this session's own output) | `(generated after this manifest; see file directly)` | 0 |

## B. 报告引用、因此必须一并提交的证据（原始评测数据与采集脚本）

<details><summary>展开查看全部 62 项（原始评测 CSV/JSON 与采集脚本）</summary>

| Repo | 路径 | 用途 | sha256 (前12位) | 大小(bytes) |
|---|---|---|---|---:|
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/00_PRODUCTION_BASELINE_MANIFEST.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `9e8ca0c0fe0a` | 10222 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/01_WORKTREE_AND_BRANCH_SETUP.md` | Underlying evaluation data or harness script that the report's cited files were computed from | `4379a9f10bed` | 3478 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/02_PRODUCTION_SEARCH_CODE_AUDIT.md` | Underlying evaluation data or harness script that the report's cited files were computed from | `4595c5fe7906` | 18938 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/03_PRODUCTION_SEARCH_CALL_GRAPH.md` | Underlying evaluation data or harness script that the report's cited files were computed from | `0385baf3562e` | 7224 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/04_EXISTING_FEATURE_REGRESSION_TARGETS.md` | Underlying evaluation data or harness script that the report's cited files were computed from | `03008696e8cf` | 5392 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/05_PRODUCTION_BEHAVIOR_BASELINE.md` | Underlying evaluation data or harness script that the report's cited files were computed from | `a17f0c4368f7` | 4585 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/06_REGRESSION_CASE_MANIFEST.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `a4e9ae592d5d` | 3580 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/07_V0_TARGET_CASE_RECONFIRMATION.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `772c3f9e0a4e` | 12313 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/09_SCORE_FEATURE_AUDIT.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `0b0530d900fc` | 6056 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/10_ISSUE_3_4_5_SCORING_MAPPING.md` | Underlying evaluation data or harness script that the report's cited files were computed from | `ee033d030778` | 5923 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/11_SCORER_CALIBRATION_SET.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `06ef89cc60a3` | 3569 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/12_SCORER_CALIBRATION_RESULTS.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `f8fd4e425497` | 6152 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/13_SCORER_CONFIG_LOCK.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `cbdd2bf88763` | 4600 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/14_BROAD_TEMPLATE_QUERY_RESULT_TRACE.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `8b05b3ad28ed` | 4250 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/18_BUILD_AND_TEST_LOG.md` | Underlying evaluation data or harness script that the report's cited files were computed from | `8fa61b68cf16` | 4923 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/19_FUNCTIONAL_REGRESSION_RESULTS.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `1b9bc6eea028` | 3801 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/32_REGRESSION_AND_IMPROVEMENT_CASEBOOK.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `eee56e109d07` | 3537 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/34_RUN_MANIFEST.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `e2869994ec3e` | 7180 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/RUN_LOG.md` | Underlying evaluation data or harness script that the report's cited files were computed from | `3d4651763e15` | 5315 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/EASY326_PAIRED.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `23cdba310783` | 21403 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/EASY326_V0.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `276a404c4cbc` | 86870 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/EASY326_V2.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `4dc038465721` | 94617 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/HARD68_PAIRED.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `943a522ebb85` | 5692 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/HARD68_V0.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `f19915fb525e` | 18174 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/HARD68_V2.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `394539136a32` | 18959 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/P0_12_PAIRED.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `183b1e6c0cbb` | 1126 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/P0_12_V0.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `a88508e829db` | 3889 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/P0_12_V2.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `5317a63d8892` | 3532 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/TARGETED_PAIRED.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `120efd612eb2` | 1546 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/TARGETED_V0.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `132b4c8be00d` | 5799 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/TARGETED_V2.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `8123497eeb06` | 7134 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/p0_12_queries.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `bec37fdbac4f` | 549 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/eval_raw/targeted_regression_queries.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `147981b9afd6` | 894 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/scripts/backfill_failed.mjs` | Underlying evaluation data or harness script that the report's cited files were computed from | `26af8e8b0c0e` | 6441 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/scripts/collector.mjs` | Underlying evaluation data or harness script that the report's cited files were computed from | `ded59e398185` | 6538 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/scripts/judge.mjs` | Underlying evaluation data or harness script that the report's cited files were computed from | `9a66c98e0bbe` | 9648 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/scripts/run_eval.mjs` | Underlying evaluation data or harness script that the report's cited files were computed from | `3de6d5ca08d1` | 8953 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/scripts/stage4_batch.mjs` | Underlying evaluation data or harness script that the report's cited files were computed from | `b385d7b6a597` | 2359 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/scripts/stats.mjs` | Underlying evaluation data or harness script that the report's cited files were computed from | `79807445f51b` | 7012 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r1-328-completion/00_V2_R1_FREEZE_MANIFEST.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `6db1059183e1` | 5802 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r1-328-completion/01_V0_OLD328_RESULTS.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `e81a1c8e51f2` | 84659 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r1-328-completion/02_V2_R1_OLD328_RESULTS.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `90ef08219f96` | 82727 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r1-328-completion/03_V0_V2_R1_OLD328_PAIRED.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `23a644ee9cec` | 20258 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r1-328-completion/RUN_LOG.md` | Underlying evaluation data or harness script that the report's cited files were computed from | `cec5abb33d65` | 4192 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r1-328-completion/RUN_MANIFEST.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `f80f6b87c7b0` | 3933 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r1-328-completion/eval_raw/OLD328_PAIRED.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `23a644ee9cec` | 20258 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r1-328-completion/eval_raw/OLD328_V0.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `e81a1c8e51f2` | 84659 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r1-328-completion/eval_raw/OLD328_V2.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `90ef08219f96` | 82727 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r2-relaxed-gate/00_V2_R2_BRANCH_AND_WORKTREE_MANIFEST.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `ffb1b0b49247` | 1466 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/00_V2_R3_BRANCH_AND_WORKTREE_MANIFEST.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `8d829b8af104` | 2644 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/02_V2_R3_REGRESSION_TRACE.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `f1bac1af71fa` | 128728 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/04_CATALOG_GAP_POLICY_PROPOSAL.md` | Underlying evaluation data or harness script that the report's cited files were computed from | `42d4b0e567d6` | 5296 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/06_V2_R3_DESIGN_MANIFEST.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `f62c09279143` | 7639 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/07_V0_R1_R3_TARGETED_COMPARISON.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `04026092e9f7` | 65190 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/09_V2_R3_CONFIG_LOCK.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `24b0c3187c08` | 5245 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/12_V2_R3_TARGETED_RUN_MANIFEST.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `f7e669c1c0fe` | 5589 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/RUN_LOG.md` | Underlying evaluation data or harness script that the report's cited files were computed from | `c7ac1ad0ecd0` | 4033 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/eval_raw/full326/EASY326_V2R3.csv` | Underlying evaluation data or harness script that the report's cited files were computed from | `7dec70a579ca` | 92197 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/eval_raw/full326/_extra_diagnostics.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `5f160e6a0dd4` | 1071 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/eval_raw/full326/_reg50_and_new5_and_flagged.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `ce58efc24234` | 4442 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/eval_raw/full326/_summary_stats.json` | Underlying evaluation data or harness script that the report's cited files were computed from | `27ed280e1949` | 3680 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/scripts_analysis/build_reports.py` | Underlying evaluation data or harness script that the report's cited files were computed from | `9283003a5083` | 14063 |

</details>

## C. 有价值但可选的中间结果（原始 LLM 裁判输出 / retry 记录）

| Repo | 路径 | 用途 | 报告引用 | sha256 (前12位) | 大小(bytes) |
|---|---|---|---|---|---:|
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/raw_targeted_eval/full_eval_out.json` | Raw LLM-judge output / retry harness artifact underlying the targeted-stage evaluation numbers | False | `3928d0f1d1e9` | 8954772 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/raw_targeted_eval/full_eval_run.log` | Raw LLM-judge output / retry harness artifact underlying the targeted-stage evaluation numbers | False | `36490ee42312` | 2934 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/raw_targeted_eval/retry.log` | Raw LLM-judge output / retry harness artifact underlying the targeted-stage evaluation numbers | False | `f56fe634a991` | 1839 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/raw_targeted_eval/retry_failed.mjs` | Raw LLM-judge output / retry harness artifact underlying the targeted-stage evaluation numbers | False | `71d78ebc916d` | 3742 |
| visual-search-adhoc | `docs/daily_report/7.19/search-relevance-prod-main-v2/v2-r3-root-cause-fix/raw_targeted_eval/run_targeted_eval.mjs` | Raw LLM-judge output / retry harness artifact underlying the targeted-stage evaluation numbers | False | `75c254a079e0` | 3744 |

## D. 不应提交的临时文件（已确认未被提交）

| Repo | 路径/模式 | 排除原因 |
|---|---|---|
| visual-search-adhoc | `.cache/ (main worktree, top level)` | D: regenerable local cache, not evaluation evidence |
| visual-search-adhoc | `**/.DS_Store (all locations, main worktree)` | D: OS artifact, never evaluation evidence |
| visual-search-adhoc | `scripts/curify-search-collect-stage7/node_modules, scripts/curify-search-stage7-*/node_modules, scripts/external-screenshot-p0-12/node_modules` | D: regenerable via npm install; not referenced by the V2 work report |
| visual-search-adhoc | `scripts/curify-search-collect-stage7/judge.log, mode_C.log, mode_D.log` | D: local server/run log from an unrelated earlier task, not V2-R3 evidence |
| curify-frontend | `.env.local, env.local (v2-r3 worktree and others)` | D: contains local secrets; already covered by .gitignore (.env*.local, .env, env.local); confirmed not tracked via git ls-files |
| curify-frontend | `node_modules/, .next/ (all worktrees)` | D: regenerable via npm install / next build; already covered by .gitignore |

## E. 属于其他任务、不得混入本次 commit 的文件（已确认未被提交）

| Repo | 路径/模式 | 排除原因 |
|---|---|---|
| visual-search-adhoc | `docs/daily_report/7.11/, 7.12/, 7.15/, 7.16/, 7.17/, 7.2/canva_manual_review/, 7.2/blog_public_v2.md, 7.2/linkedin_public_v2.md, 7.5/blog_public_v2.md, 7.9/WORK_REPORT_2026-07-09_zh.md (modified)` | E: belongs to other tasks / other dates, not part of the Search Relevance V2 deliverable; left untouched in the main worktree |
| curify-frontend | `baobao/search-relevance-phrase-alias-2026-07-09 working-tree modifications (26 files, main non-worktree checkout)` | E: belongs to the old frozen candidate line, out of scope for this V2-R3 delivery per boss decision to leave it frozen; not committed or discarded by this audit, left for user judgment |

---

## 说明

- 类别 A/B/C 的文件均已在此前会话中通过 `git add <具体路径>`（非 `git add .`）精确暂存、commit 并 push，本次审计对其重新计算 sha256 校验（见文件中的哈希列），确认与当前工作区文件字节一致，未被本次审计意外修改。
- 类别 D/E 按目录/glob 模式分组列出（而非逐文件枚举 node_modules 等再生成产物），因为逐文件枚举对成千上万个 node_modules 文件没有审计价值；已通过 `git status`/`git diff --stat` 确认这些路径**从未出现在**任何已 push 的 V2 相关 commit 中。
- 类别 E 中 `curify-frontend` 旧冻结候选分支的未提交修改，本次审计只读记录，未做任何 stash/commit/丢弃操作。
