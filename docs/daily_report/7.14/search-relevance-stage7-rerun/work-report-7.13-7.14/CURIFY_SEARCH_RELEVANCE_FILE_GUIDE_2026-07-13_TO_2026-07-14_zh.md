# Curify Search Relevance — 文件导航指南（2026-07-13 至 2026-07-14）

本指南整理两天内全部关键文件，标注优先级、内容、阅读对象与权威性，避免误把历史失败实验当作最终结果。

---

## 总表

| 优先级 | 文件名 | 日期 | 目录 | 类型 | 内容 | 何时看 | 技术人员何时看 | 是否最终权威 | 限制 |
|---|---|---|---|---|---|---|---|---|---|
| P0 | SEARCH_OPTIMIZATION_ONE_PAGE_SUMMARY_2026-07-14_zh.md | 7.14 | before-after-data-comparison/ | MD | 68+12优化一页摘要 | 第二 | — | 是 | — |
| P0 | SEARCH_OPTIMIZATION_BEFORE_AFTER_COMPARISON_2026-07-14_zh.md | 7.14 | before-after-data-comparison/ | MD | 68+12完整对比 | 第三 | 核实具体数字时 | 是 | — |
| P0 | P0_12_SCREENSHOT_VALIDATION_2026-07-14_zh.md | 7.14 | p0-12-before-after/ | MD | 12 P0截图人工判定 | 第四 | 核实P0具体问题时 | 是 | — |
| P0 | REMAINING_HARD_CASES_SUMMARY_v2_2026-07-14_zh.md | 7.14 | remaining-hard-cases/ | MD | 剩余问题根因/Owner整合 | 第五 | 分配后续工作时 | 是（_v2） | 见文件内§3目录状态说明 |
| P0 | CURIFY_SEARCH_RELEVANCE_WORK_REPORT_2026-07-13_TO_2026-07-14_zh.md | 7.14 | work-report-7.13-7.14/ | MD | 完整Work Report | 需要完整脉络时 | 全文 | 是 | 待300+完成后更新 |

---

## 18.1 优先看（同上 P0 六项，此处不重复）

---

## 18.2 68 条结果相关 CSV

| 文件 | 内容 |
|---|---|
| `hard_queries_baseline_locked_68_2026-07-14.csv` | Baseline（2026-07-07生产采集）锁定快照，SHA-256=904ea6a5...，只读不可覆盖 |
| `hard_queries_refreshed_dg_guarded_68_2026-07-14.csv` | D模式（d+g+Guard）刷新结果，含完整diagnostics与Top10 |
| `hard_queries_before_after_68_2026-07-14.csv` | Baseline vs D模式逐条对比，含zero/low/full_catalog/thousand_plus等标志位 |
| `hard_queries_ablation_abcd_68_2026-07-14.csv` | 272行（68×4）完整A/B/C/D消融原始数据 |
| `hard_queries_manual_review_68_2026-07-14.csv` | 68行结构化Top10人工判读（relevant/partial/irrelevant计数、entity保留等） |
| `stage7_final_manual_labels_68_2026-07-14.csv` | **权威最终标签**（Prompt5独立复核后 verified_label 列，PASS4/PARTIAL42/FAIL22） |
| `stage7_remaining_failures_2026-07-14.csv` | 22条FAIL的根因/建议修复/优先级/Owner |
| `stage7_rerun_manifest_2026-07-14.json` | 本轮全部输入/输出文件的hash、完整性记录 |

---

## 18.3 P0 文件

| 文件 | 内容 |
|---|---|
| `p0_12_before_after_2026-07-14.csv` | 12条P0逐条Before/After结构化数据 |
| `P0_12_SCREENSHOT_VALIDATION_2026-07-14_zh.md` | 人工截图判读报告（权威P0标签来源） |
| `P0_SCREENSHOT_INDEX_2026-07-14.md` | 截图文件索引 |
| `p0_12_screenshot_manifest_2026-07-14.json` | 截图完整性/hash记录 |
| `screenshots/p0-before/`（12张） | 线上生产环境Before截图（2026-07-07） |
| `screenshots/p0-after/`（24张，Full+Top各12） | 本地dev server After截图（2026-07-14） |

---

## 18.4 Remaining Hard Cases（7个 `_v2` 文件）

| 文件 | 内容 |
|---|---|
| `remaining_hard_cases_v2_2026-07-14.csv` | 65条去重Case完整逐条数据（根因/证据/Owner/优先级/处理路线） |
| `remaining_verified_failures_22_v2_2026-07-14.csv` | 22条Verified FAIL的根因/Owner/优先级 |
| `p0_12_root_cause_owner_priority_v2_2026-07-14.csv` | **权威**12 P0根因/Owner/优先级/（本Work Report第8节采用此口径） |
| `remaining_hard_cases_owner_handoff_v2_2026-07-14.csv` | 按Owner分组的交接清单 |
| `remaining_hard_cases_repair_candidates_v2_2026-07-14.csv` | 具备直接代码修复条件的候选（仅6条） |
| `REMAINING_HARD_CASES_SUMMARY_v2_2026-07-14_zh.md` | 综合报告 |
| `remaining_hard_cases_manifest_v2_2026-07-14.json` | 完整性记录 |

**注意**：目录中存在一个来源不明的旧文件 `remaining_hard_cases_2026-07-14.csv`（无 `_v2` 后缀），已被 Prompt 7 明确标记为"未采信、未覆盖"，**不得使用**。

---

## 18.5 图表（5张，位于 `before-after-data-comparison/charts/`）

| 图表 | 用途 |
|---|---|
| `hard_68_labels_before_after.png` | 68条PASS/PARTIAL/FAIL Before vs After柱状图 |
| `hard_68_rates_before_after.png` | Strict/Broad/FAIL Rate Before vs After |
| `flooding_before_after.png` | D`>=1000`/D Full-catalog/C Full-catalog Before vs After |
| `p0_12_status.png` | 12 P0截图判定状态分布 |
| `remaining_root_cause_distribution.png` | 22条Verified FAIL根因分布 |

---

## 18.6 7.13 文件（历史/已被取代，不得当最终结论）

| 文件 | 标记 | 说明 |
|---|---|---|
| `docs/daily_report/7.13/WORK_REPORT_2026-07-13_zh.md` | **HISTORICAL** | 第一轮真实报告，如实记录0% Strict PASS，明确"不建议合并" |
| `docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_baseline.csv` | **BASELINE**（合法历史Baseline） | 与7.14的`hard_queries_baseline_locked_68`字节级一致，SHA-256=904ea6a5... |
| `docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_refreshed.csv` | **SUPERSEDED / INVALID_FOR_FINAL_CONCLUSION** | 7.13的D模式结果，Mode A/C通过`git show HEAD`重建（非合法同代码消融），已被7.14 Prompt4A+Prompt4V3的合法版本取代 |
| `docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_before_after.csv` | **SUPERSEDED / INVALID_FOR_FINAL_CONCLUSION** | 同上 |
| `docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_ablation.csv` | **SUPERSEDED / INVALID_FOR_FINAL_CONCLUSION** | 同上，A/C两组消融方法学存在缺陷 |
| `docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_summary.md` | **HISTORICAL**（作为"第一轮效果差"的证据保留） | PASS/PARTIAL/FAIL=0/4/64的权威出处，用于Before对比，不作为最终Search质量结论 |
| `docs/daily_report/7.13/search-optimization-stage-7/run_manifest.json` | **HISTORICAL** | 记录7.13的Mode定义（用于确认Prompt4发现的合法性冲突） |

**不得误把旧失败实验当最终结果**：7.13 的 `hard_queries_68_refreshed/before_after/ablation.csv` 三个文件的 A/C 模式数据存在实验设计缺陷（Mode A/C 通过 `git show HEAD` 文本重建而非同一份生产代码的运行时开关构造），Prompt 4 已明确发现并停止沿用此方法。**68 条 Hard Query 的最终权威结果，一律以 7.14 `full-68-rerun-v2/` 目录下的文件为准**，7.13 的 PASS/PARTIAL/FAIL=0/4/64 仅作为"Before"对比基准使用（该数字来自 7.13 的 Mode D，D 模式本身是合法的当前生产代码路径，不受 A/C 消融缺陷影响）。

---

## 18.7 300+ Easy Query Validation（进行中，仅列计划路径）

```text
scripts/easy-query-validation-300plus/          [IN PROGRESS — DO NOT USE YET]
docs/daily_report/7.14/search-relevance-stage7-rerun/easy-query-validation-300-plus/   [IN PROGRESS — DO NOT USE YET]
```

本报告未读取以上目录任何文件内容。完成后将在独立文件/章节中更新，见 `UPDATE_AFTER_EASY_QUERY_VALIDATION_2026-07-14.md`。

---


