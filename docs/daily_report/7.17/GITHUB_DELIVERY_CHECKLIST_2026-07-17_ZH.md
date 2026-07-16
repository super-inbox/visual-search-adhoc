# Curify 搜索优化调查 — GitHub 交付清单（2026-07-17）

性质：**交付准备文档**，用于确定本轮 `docs/daily_report/7.16/` 与 `docs/daily_report/7.17/` 下哪些内容应提交到
`visual-search-adhoc` 仓库。本文档只做盘点与建议，**不执行任何 `git add`/`commit`/`push`**，不删除、不移动、
不重命名任何文件，不修改任何源代码。

依据（source of truth）：
- `docs/daily_report/7.17/CURIFY_SEARCH_OPTIMIZATION_WORK_REPORT_2026-07-15_TO_2026-07-17_ZH.md`（管理层工作报告）
- `docs/daily_report/7.17/FILE_CLEANUP_AND_PROJECT_STRUCTURE_AUDIT_2026-07-15_TO_2026-07-17_ZH.md`（项目文件清点审计）

审查范围：`docs/daily_report/7.16/`（405 个文件）+ `docs/daily_report/7.17/`（35 个文件），合计 **440 个文件**，
总大小约 **8.9M**（7.16：8.5M，7.17：444K）。范围内单个最大文件为 648K，**远低于任何 GitHub 大文件阈值，
本次交付范围内不需要 Git LFS**。

---

## 1. 待提交文件（KEEP_FOR_GITHUB）—— 共 377 个文件

判定标准：面向管理层 / 属于最终报告 / 是重要证据 / 复现所需 / 被最终报告直接引用。

### 1.1 `docs/daily_report/7.16/easy-query-bank-v3/`（3 个文件，92K）

Easy Query Benchmark v2 的查询库来源文件，被 `easy-query-v2-validation/` 评测直接依赖，体量小。

| 文件 | 理由 |
|---|---|
| `easy_query_audit_v2_2026-07-16.csv` | 326 条查询的筛选审计记录 |
| `easy_query_bank_v2_2026-07-16.csv` | 评测实际使用的查询库 |
| `easy_query_bank_v2_generation_report_2026-07-16.md` | 查询库生成方法说明 |

### 1.2 `docs/daily_report/7.16/easy-query-v2-validation/`（341 个文件中的 339 个，排除 2 个 `__pycache__`）

Easy Query Benchmark v2 的完整评测产出，本轮调查的核心证据链。

**面向管理层（任务明确点名）**：
- `EASY_QUERY_V2_ROOT_CAUSE_ANALYSIS_ZH.md` —— 根因分析正文
- `HYBRID_SEARCH_CORE80_CANDIDATE_SET.csv` —— Hybrid Search 80 条候选查询集
- `HYBRID_SEARCH_QUERY_SELECTION_RATIONALE.md` —— 候选集筛选方法论
- `easy_query_v2_evaluation_summary.md` —— 评测结果摘要

**评测明细证据（工作报告直接引用其汇总数字，属于"重要证据"）**：
- `easy_query_v2_relevance_evaluation.csv`（326 行全字段评测结果）
- `easy_query_v2_top_results.csv`（1343 行结果明细）
- `easy_query_v2_manual_review_queue.csv`（244 行人工复核队列）
- `RELEVANCE_RUBRIC.md`（锁定的评分规则，方法论依据）

**复现证据链（体量小，判定标准明确要求"reproducibility required"）**：
- `checkpoints/runs/V001.json` … `V326.json`（326 个文件，合计约 3.6M，单个查询的原始采集快照）
- `query_input/easy_query_v2_input_with_ids.csv`（评测输入文件）
- `scripts/build_v2_eval.py`、`scripts/scoring.py`、`scripts/v2_judgments.py`（评分/构建脚本，锁定的 rubric-v1.1 引擎）

**排除**：`scripts/__pycache__/scoring.cpython-311.pyc`、`scripts/__pycache__/v2_judgments.cpython-311.pyc`（见第 3 节）。

> 说明：326 个 checkpoint JSON 文件数量较多，但单文件 4-16K、总量约 3.6M，不构成"大文件"问题。若未来仓库
> 卫生标准收紧，这批文件是本清单中**唯一**可以从"必须保留"降级为"可选归档"的候选（详见第 5 节备选方案），
> 但本次判定为保留，因为评分结果的可复现性直接依赖它们。

### 1.3 `docs/daily_report/7.17/` 根目录（2 个文件）

| 文件 | 理由 |
|---|---|
| `CURIFY_SEARCH_OPTIMIZATION_WORK_REPORT_2026-07-15_TO_2026-07-17_ZH.md` | 管理层最终工作报告，本次交付的核心产出 |
| `FILE_CLEANUP_AND_PROJECT_STRUCTURE_AUDIT_2026-07-15_TO_2026-07-17_ZH.md` | 项目结构清点审计，工作报告的支撑依据 |

### 1.4 `docs/daily_report/7.17/search-click-generate-data-audit/`（15 个文件，172K，全部保留）

已在此前审计中确认为无噪音、体量小、结构清晰的最终交付目录，无需筛选，整体保留：
`SEARCH_CLICK_GENERATE_DATA_AUDIT.md`、`SEARCH_CLICK_GENERATE_EXECUTIVE_SUMMARY_ZH.md`、
`SEARCH_TO_GENERATE_MEASUREMENT_PROPOSAL_ZH.md`、`SEARCH_FUNNEL_METRIC_DEFINITIONS.md`、
`HYBRID_SEARCH_INSTRUMENTATION_REQUIREMENTS.md`、`SEARCH_ATTRIBUTION_FEASIBILITY.md`、
`SEARCH_TRACKING_GAPS.md`、`SEARCH_QUERY_PRIVACY_RISK_NOTES.md`、`SAFE_READ_ONLY_SQL_TEMPLATES.sql`、
`SEARCH_ADMIN_DASHBOARD_INVENTORY.csv`、`SEARCH_DASHBOARD_CAPABILITY_MATRIX.csv`、`SEARCH_EVENT_FIELD_MAP.csv`、
`SEARCH_SQL_QUERY_INVENTORY.csv`、`AUDIT_MANIFEST.json`、`FINAL_AUDIT_LOG.md`

### 1.5 `docs/daily_report/7.17/hybrid-search-technical-audit/`（18 个文件，212K，全部保留）

同样已确认无噪音，整体保留：`HYBRID_SEARCH_EXECUTIVE_SUMMARY_ZH.md`、`HYBRID_SEARCH_CURRENT_ARCHITECTURE.md`、
`HYBRID_SEARCH_CALL_GRAPH.md`、`HYBRID_SEARCH_CODE_ENTRYPOINTS.csv`、`HYBRID_SEARCH_MODE_MATRIX.md`、
`HYBRID_SEARCH_MERGE_AND_RANKING_SPEC.md`、`HYBRID_SEARCH_INTERNAL_RESULT_CONTRACT.md`、
`HYBRID_SEARCH_EXTERNAL_RESULT_CONTRACT.md`、`HYBRID_SEARCH_FAILURE_CACHE_COST_SPEC.md`、
`HYBRID_SEARCH_TRIGGER_EXPERIMENT.md`、`HYBRID_SEARCH_CORE80_EXPERIMENT_PLAN.md`、
`HYBRID_SEARCH_ONLINE_METRICS_AND_AB_TEST.md`、`HYBRID_SEARCH_SAFE_ROLLOUT_PLAN.md`、
`HYBRID_SEARCH_INSTRUMENTATION_PLAN.md`、`HYBRID_SEARCH_RISK_REGISTER.csv`、`EXTERNAL_IMAGE_PROVIDER_OPTIONS.md`、
`AUDIT_MANIFEST.json`、`FINAL_AUDIT_LOG.md`

---

## 2. 建议本次暂不提交（ARCHIVE_OPTIONAL）—— 共 58 个文件

`docs/daily_report/7.16/easy-query-production-vs-optimized-comparison-v1/`（生产基线 vs. 本地候选分支对比评测，
60 个文件中的 58 个，排除 2 个 `__pycache__`）

**判定依据**：这是 2026-07-16 完成的一项独立、高质量的对比评测（内容包括 `final/` 下的完整对比报告与
7 张图表、`comparison/`、`normalized/`、`review/`、`summaries/`、`scripts/` 等完整子目录），但**不在本次任务
明确列出的六项交付范围内**（Easy Query v2 evaluation / Root cause analysis / Search→Click→Generate audit /
Hybrid Search technical audit / Final Work Report / Cleanup audit），管理层工作报告的"交付物清单"表格
（第 9 节）中也未将其单列为一行。

- 内容真实、完整、无质量问题，**不是"应删除"的内容**，故不归入 DO_NOT_COMMIT；
- 但属于"有价值的详细产出，非本次任务点名的核心交付物"，符合 ARCHIVE_OPTIONAL 的判定标准；
- 建议：**本次提交范围不包含该目录**，作为独立的后续提交处理（如果管理层希望将其一并归档到 GitHub，
  可用同样干净的方式单独提交，不影响本次交付的范围清晰度）。

若后续决定一并提交，同样需要排除其内部的 2 个 `__pycache__` 文件（见第 3 节）。

---

## 3. 明确排除（DO_NOT_COMMIT）—— 共 5 个文件

| 文件 | 大小 | 排除理由 |
|---|---:|---|
| `docs/daily_report/7.16/.DS_Store` | 8K | macOS 目录元数据，无内容价值。**注意**：这是仓库里已被跟踪（tracked）的历史遗留文件，`git status` 显示为"已修改"而非"未跟踪"——本次交付**不触碰**它（不新增、不修改、不删除），维持原状，仅在提交时不主动 `git add` 它的改动 |
| `docs/daily_report/7.16/easy-query-v2-validation/scripts/__pycache__/scoring.cpython-311.pyc` | 8K | Python 字节码缓存，运行 `scoring.py` 自动生成 |
| `docs/daily_report/7.16/easy-query-v2-validation/scripts/__pycache__/v2_judgments.cpython-311.pyc` | 60K | 同上 |
| `docs/daily_report/7.16/easy-query-production-vs-optimized-comparison-v1/scripts/__pycache__/run_b_judgments.cpython-311.pyc` | 68K | 同上（该目录本身已整体列为 ARCHIVE_OPTIONAL，此处单独列出是为了在"若后续决定提交该目录"时明确仍需排除它） |
| `docs/daily_report/7.16/easy-query-production-vs-optimized-comparison-v1/scripts/__pycache__/scoring.cpython-311.pyc` | 8K | 同上 |

审查范围内**没有发现** `node_modules`、浏览器 profile 缓存、原始截图（screenshots）——这些噪音类别集中在
`docs/daily_report/7.15/` 与仓库根目录的 `.cache/`，均不在本次 7.16/7.17 的交付范围内，此前的项目清理审计
已单独记录，不重复处理。

---

## 4. 大文件检查结论

- 审查范围内（7.16 + 7.17，440 个文件，共 8.9M）**没有任何文件超过 1M**，最大单文件为 648K
  （`easy_query_production_vs_optimized_paired_comparison.jsonl`，属于第 2 节 ARCHIVE_OPTIONAL 范围）；
  本次建议提交范围（第 1 节，377 个文件）内最大单文件为 `easy_query_v2_top_results.csv`（492K）。
- **结论：不需要 Git LFS，不需要额外压缩或拆分，可直接常规 `git add`/`commit`。**
- 唯一体积相关的观察点是 `checkpoints/runs/` 下 326 个小文件（见 1.2 节说明），是文件**数量**而非**体积**
  的考量，本次判定为保留。

---

## 5. 推荐最终 GitHub 目录结构

**无需移动任何文件**——当前 `docs/daily_report/7.16/` 与 `docs/daily_report/7.17/` 的既有组织方式已经符合
清晰、无冲突的交付标准，本次交付按现状原样提交（仅排除第 3 节 5 个噪音文件）：

```
visual-search-adhoc/
  docs/daily_report/
    7.16/
      easy-query-bank-v3/                                   # 提交（1.1 节）
      easy-query-v2-validation/                              # 提交，排除 __pycache__（1.2 节）
      easy-query-production-vs-optimized-comparison-v1/      # 本次不提交（第 2 节，独立后续处理）
    7.17/
      CURIFY_SEARCH_OPTIMIZATION_WORK_REPORT_2026-07-15_TO_2026-07-17_ZH.md   # 提交（1.3 节）
      FILE_CLEANUP_AND_PROJECT_STRUCTURE_AUDIT_2026-07-15_TO_2026-07-17_ZH.md # 提交（1.3 节）
      GITHUB_DELIVERY_CHECKLIST_2026-07-17_ZH.md                              # 本文件，提交
      search-click-generate-data-audit/                       # 整体提交（1.4 节）
      hybrid-search-technical-audit/                           # 整体提交（1.5 节）
```

---

## 6. 推荐 Git 命令（仅供审批后执行，本次不运行）

```bash
# 1) 逐路径暂存，明确排除 __pycache__（不使用整目录 git add，避免误收纳噪音文件）
git add docs/daily_report/7.16/easy-query-bank-v3/

git add docs/daily_report/7.16/easy-query-v2-validation/ \
        ':(exclude)docs/daily_report/7.16/easy-query-v2-validation/scripts/__pycache__'

git add docs/daily_report/7.17/CURIFY_SEARCH_OPTIMIZATION_WORK_REPORT_2026-07-15_TO_2026-07-17_ZH.md
git add docs/daily_report/7.17/FILE_CLEANUP_AND_PROJECT_STRUCTURE_AUDIT_2026-07-15_TO_2026-07-17_ZH.md
git add docs/daily_report/7.17/GITHUB_DELIVERY_CHECKLIST_2026-07-17_ZH.md
git add docs/daily_report/7.17/search-click-generate-data-audit/
git add docs/daily_report/7.17/hybrid-search-technical-audit/

# 2) 暂存后核查：确认没有 __pycache__ / .DS_Store 被意外收纳
git status --porcelain | grep -i "pycache\|\.DS_Store"
# 期望输出为空

# 3) 核查暂存文件总数与总大小是否与本清单一致（应为 377 个文件）
git diff --cached --stat | tail -1

# 4) 提交（需管理层/负责人明确批准后再执行，本次任务不执行）
git commit -m "docs: add Curify search optimization investigation (2026-07-15~17)

- Easy Query Benchmark v2: 326-query relevance evaluation + root cause analysis
- Hybrid Search Core-80 candidate set and selection rationale
- Search-to-Click-to-Generate measurement audit and instrumentation requirements
- Hybrid Search technical architecture audit and safe rollout plan
- Manager-facing work report and project structure cleanup audit"

# 5) 推送（同样需明确批准后再执行）
git push origin main
```

> `easy-query-production-vs-optimized-comparison-v1/` 与 `.DS_Store` 的既有改动均**不在**以上 `git add`
> 命令列表中，不会被本次提交带上。

---

## 7. 本清单未覆盖但读者应知悉的事项

- `docs/daily_report/7.16/.DS_Store` 是仓库中已跟踪的历史文件，其当前"已修改"状态与本次交付无关，
  是否清理属于独立的仓库卫生任务，不在本次 GitHub 交付准备的处理范围内。
- 仓库根目录当前没有 `.gitignore` 规则覆盖 `__pycache__`/`.DS_Store`，此前的项目清理审计已提出
  "建议新增 `.gitignore`"，本次交付不重复处理，也不因此阻塞本次提交。
- `docs/daily_report/7.15/`（生产基线评测，含 484M 截图）不在本次任务的审查范围（`7.16/`、`7.17/`）内，
  未做评估，不影响本次交付的准确性。
