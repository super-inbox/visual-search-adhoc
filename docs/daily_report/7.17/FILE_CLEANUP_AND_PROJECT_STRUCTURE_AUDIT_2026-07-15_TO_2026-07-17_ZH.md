# Curify Search Optimization 项目文件清点与结构清理审计（2026-07-15 至 2026-07-17）

审计日期：2026-07-17
审计性质：**纯分析性审计，仅盘点与建议，不执行任何删除/移动/重命名操作**。
审计范围：`~/Desktop/visual-search-adhoc`（主文档仓库）+ `~/Desktop` 下与本项目相关的所有目录/克隆。
方法：只读遍历（`ls`/`find`/`du`/`git status`/`git rev-parse`），未修改任何文件，未执行任何 git 变更命令，未联网调用任何 API。

---

## 1. 执行摘要

过去三天（7/15–7/17）围绕 Curify 搜索优化课题，共产生了 **3 个已完成的正式调查环节**（Session 1/2/3），全部输出都已落盘在 `visual-search-adhoc/docs/daily_report/` 下对应日期目录中，**没有任何被遗漏、丢失或散落在错误位置的最终交付物**。

同时，本次盘点在 `~/Desktop` 发现：

- **3 个用于支持这些审计的临时只读代码克隆**（`curify-studio`、`curify-frontend-hybrid-audit`、以及更早的 `curify-production-baseline-2026-07-15`），三者 `git status` 均为**完全干净、零改动**，且其中引用的全部证据（文件路径、行号、commit hash）已经完整记录进已提交的 Markdown/CSV 报告中——**三者均可安全归档或删除**，不会丢失任何审计结论。
- **1 个极易被误认为"临时克隆"、但实际是正在进行中的真实工程分支**：`~/Desktop/curify-frontend`（`baobao/search-relevance-phrase-alias-2026-07-09` 分支，26 处未提交改动）。这是 Task 5（Easy Query Benchmark v2 采集）实际运行验证过的候选分支代码，**绝对不能删除或视为可清理项**，必须与上面三个只读克隆明确区分。
- 主文档仓库内存在少量**纯执行产物噪音**（浏览器 profile 缓存 104M、Python 字节码缓存、遗留 `node_modules`、孤立日志文件），均不影响任何已交付报告的完整性，建议清理但**不属于本次审计执行范围**（仅给建议）。
- 未发现重复或冲突的最终报告版本；三个 Session 的目录命名与内容边界清晰，无需重新组织即可直接支撑经理汇报报告的撰写。

**给下一步（撰写 Manager Work Report）的结论：可以直接基于现有目录结构撰写，无需先做任何清理动作。** 本报告中的清理建议属于"锦上添花的卫生工作"，不是撰写工作报告的前置阻塞项。

---

## 2. 当前文件夹现状

### 2.1 `~/Desktop` 下与 Curify 相关的目录全景

通过对 `~/Desktop` 按 `curify` / `visual-search` / `search` / `audit` / `hybrid` 关键词搜索，加上人工核查每个目录的 git 身份，得到以下完整清单：

| 路径 | 大小 | Git 身份 | 分支 @ commit | 工作区状态 | 与本次三个 Session 的关系 |
|---|---:|---|---|---|---|
| `~/Desktop/visual-search-adhoc` | — | 主文档仓库（git 仓库，见 2.2） | `main` | 大量未提交新增文件（详见 2.2） | **主仓库，所有最终交付物所在地** |
| `~/Desktop/curify-studio` | 285M | `super-inbox/curify-studio.git` 浅克隆 | `main` @ `7b3fa5b` | 干净，0 改动 | **Session 2 审计用临时克隆** |
| `~/Desktop/curify-frontend-hybrid-audit` | 767M | `super-inbox/curify-frontend.git` 浅克隆 | `main` @ `5a59c4b` | 干净，0 改动 | **Session 3 审计用临时克隆** |
| `~/Desktop/curify-production-baseline-2026-07-15` | 1.8G | `super-inbox/curify-frontend.git` 完整克隆 | detached @ `72b55b6` | 干净，0 改动 | 7/15 生产基线评测（早于 Session 1/2/3，但同属本次日期窗口）用的验证克隆 |
| `~/Desktop/curify-frontend` | 4.9G | `super-inbox/curify-frontend.git` 完整克隆 | `baobao/search-relevance-phrase-alias-2026-07-09` @ `c062e618` | **26 处未提交改动（真实工程 WIP，非审计产物）** | Easy Query Benchmark v2 采集时实际运行验证的候选分支代码——**不是审计克隆，是活跃开发分支** |
| `~/Desktop/curify-blog-fix` | 3.0G | `super-inbox/curify-frontend.git` 完整克隆 | `baobao/multi-intent-topic-cooccurrence` @ `bfdcd2f` | 干净 | **超出本次日期窗口**（目录 mtime 为 7/13），与搜索优化课题无关的另一项独立工作，本次审计不做处理 |
| `~/Desktop/curify-frontend.zip` | 1.5G | 压缩包 | — | — | 6/18 的旧备份，早于窗口，**超出范围** |
| `~/Desktop/visual-search-adhoc.zip` | 2.2G | 压缩包 | — | — | 6/30 的旧备份，早于窗口，**超出范围** |

**关键澄清（易混淆点）**：`curify-frontend` 与 `curify-frontend-hybrid-audit` 名字高度相似，且都克隆自同一个远程仓库 `super-inbox/curify-frontend.git`，但用途完全不同——前者是承载真实候选分支未提交代码的活跃工作目录，后者是 Session 3 用完即可丢弃的只读架构审计克隆。后续清理时必须以 **git 身份和未提交改动数量**而非名字来判断，避免误删。

此外，`~/Desktop` 下没有发现除以上 7 项之外、mtime 落在 7/15–7/17 窗口内、且与 curify/搜索优化相关的其他目录。

### 2.2 `visual-search-adhoc` 主仓库内部现状

主仓库本身（`git status`）存在大量**尚未提交**的新增内容，这是预期状态（三个 Session 的输出均是本窗口内新写入、还未 `git add/commit` 的文件），不是异常：

- `docs/daily_report/7.15/`、`7.16/`、`7.17/` 整体未跟踪（`??`）——本次审计的核心交付物均在此列
- 仓库根目录**没有 `.gitignore` 文件**（只有一个只包含 `.DS_Store` 的规则），导致 `node_modules`、`.cache/`、`__pycache__` 等纯构建产物会被 `git status` 一并列出，增加噪音
- 若干与本次三个 Session **无关**的历史改动/删除（如 `docs/daily_report/6.18/`、`docs/daily_report/7.2/` 下的 `.DS_Store` 增删、`7.9/` 工作报告更新）——这些是仓库里并行存在的其他日常工作痕迹，本次审计不做评估，仅确认它们不会干扰三个 Session 的交付物。

---

## 3. Session 1 / 2 / 3 交付物映射

### 3.1 Session 1 — Easy Query Benchmark v2

**核心目录**：`docs/daily_report/7.16/easy-query-v2-validation/`（341 个文件，4.3M）

| 子集 | 文件 | 面向经理 / 仅用于复现 |
|---|---|---|
| 根因分析与 Hybrid Search 候选集（管理层核心结论） | `EASY_QUERY_V2_ROOT_CAUSE_ANALYSIS_ZH.md`、`HYBRID_SEARCH_QUERY_SELECTION_RATIONALE.md`、`HYBRID_SEARCH_CORE80_CANDIDATE_SET.csv`、`easy_query_v2_evaluation_summary.md` | **面向经理**——这 4 份是撰写工作报告时应直接引用的一手结论 |
| 评测明细数据 | `easy_query_v2_relevance_evaluation.csv`（326 行全字段）、`easy_query_v2_top_results.csv`（1343 行结果明细）、`easy_query_v2_manual_review_queue.csv`（244 行人工复核队列） | 半面向经理——数据量大，经理汇报应引用其**汇总数字**而非原始表格，但表格本身是结论的一手证据，应保留并在报告中给出路径引用 |
| 评分规则文档 | `RELEVANCE_RUBRIC.md` | 仅用于复现/方法论说明 |
| 原始采集数据 | `checkpoints/runs/V001.json` … `V326.json`（326 个文件）、`query_input/easy_query_v2_input_with_ids.csv`、`logs/collection_run.log` | **仅用于复现**——这是 326 次真实搜索请求的原始 JSON 快照，是评测结果可追溯、可复算的证据链底座，体量小（JSON 总计数十 KB 级别/条）不构成清理负担，但不应出现在经理汇报的正文引用中 |
| 评分/构建脚本 | `scripts/scoring.py`（与 7/15 生产基线评测锁定的 rubric-v1.1 引擎字节级一致）、`scripts/v2_judgments.py`（326 条独立相关性判定）、`scripts/build_v2_eval.py` | 仅用于复现 |
| **执行产物噪音** | `scripts/__pycache__/scoring.cpython-311.pyc`、`scripts/__pycache__/v2_judgments.cpython-311.pyc` | 纯 Python 字节码缓存，无任何内容价值，**建议清理**（见第 5 节） |

**上游输入（不在本目录内，但被本 Session 直接依赖）**：`docs/daily_report/7.16/easy-query-bank-v3/`（3 个文件，92K：`easy_query_audit_v2_2026-07-16.csv`、`easy_query_bank_v2_2026-07-16.csv`、生成报告）——这是 Session 1 评测所用的 326 条查询库的来源文件，体量小、结构清晰，**建议保留在当前位置**，工作报告中应明确引用它作为"评测输入"而非 Session 1 自己的产出。

**同日期下的相关但独立产出**：`docs/daily_report/7.16/easy-query-production-vs-optimized-comparison-v1/`（60 个文件，4.1M）——这是 7/16 完成的"生产基线 vs 本地候选分支"对比评测（早于本次严格意义上的 Session 1，但同属"新 Benchmark 体系建立"这条故事线的一部分），工作报告撰写时应作为背景铺垫引用，但不属于任务指定的三个 Session 范围。

### 3.2 Session 2 — Search → Click → Generate Audit

**核心目录**：`docs/daily_report/7.17/search-click-generate-data-audit/`（15 个文件，172K）

全部 15 个文件均为文本/表格类小文件，**没有执行产物噪音**，无需清理：

| 子集 | 文件 |
|---|---|
| 面向经理 | `SEARCH_CLICK_GENERATE_EXECUTIVE_SUMMARY_ZH.md`（中文执行摘要）、`SEARCH_TO_GENERATE_MEASUREMENT_PROPOSAL_ZH.md`（中文测量方案建议） |
| 详细审计正文 | `SEARCH_CLICK_GENERATE_DATA_AUDIT.md`（英文完整审计，含逐问题编号 Q1-Q22）、`SEARCH_ATTRIBUTION_FEASIBILITY.md`、`SEARCH_FUNNEL_METRIC_DEFINITIONS.md`、`SEARCH_TRACKING_GAPS.md` |
| 工程落地参考 | `HYBRID_SEARCH_INSTRUMENTATION_REQUIREMENTS.md`、`SAFE_READ_ONLY_SQL_TEMPLATES.sql`、`SEARCH_QUERY_PRIVACY_RISK_NOTES.md` |
| 数据表 | `SEARCH_ADMIN_DASHBOARD_INVENTORY.csv`、`SEARCH_DASHBOARD_CAPABILITY_MATRIX.csv`、`SEARCH_EVENT_FIELD_MAP.csv`、`SEARCH_SQL_QUERY_INVENTORY.csv` |
| 审计留痕 | `AUDIT_MANIFEST.json`（含全部输出文件的 SHA-256）、`FINAL_AUDIT_LOG.md`（含完整安全校验清单） |

**`curify-studio` 克隆能否安全删除？——可以。** 依据：
1. `FINAL_AUDIT_LOG.md` 自证工作区在审计开始和结束时均为 `git status` 干净、`origin/main` 同步，期间零改动。
2. 审计正文的每一条结论都以"文件路径 + 精确行号/函数名"的形式引用（如 `curify_background/app/crud/admin.py::_section_search_queries`），且关键 SQL 逻辑（如 5 分钟归因窗口的完整查询语句）已**逐字复制**进 `SEARCH_CLICK_GENERATE_DATA_AUDIT.md` 正文，不依赖克隆本身才能理解结论。
3. `AUDIT_MANIFEST.json` 记录了全部 14 个产出文件的 SHA-256，具备完整性校验能力，删除克隆不影响已交付内容的可信度。
4. 该克隆是从公开远程仓库 `https://github.com/super-inbox/curify-studio.git` 浅克隆而来，若未来需要重新核对某个细节，可在几秒内用同一 commit（`7b3fa5b`）重新克隆复现，**没有任何本地独有、不可再生的内容**。

### 3.3 Session 3 — Hybrid Search Technical Audit

**核心目录**：`docs/daily_report/7.17/hybrid-search-technical-audit/`（18 个文件，212K）

同样全部为小体量文本/表格文件，无执行产物噪音：

| 子集 | 文件 |
|---|---|
| 面向经理 | `HYBRID_SEARCH_EXECUTIVE_SUMMARY_ZH.md`（中文执行摘要） |
| 架构现状 | `HYBRID_SEARCH_CURRENT_ARCHITECTURE.md`、`HYBRID_SEARCH_CALL_GRAPH.md`、`HYBRID_SEARCH_CODE_ENTRYPOINTS.csv` |
| 设计规范（均为"仅设计，未实现"） | `HYBRID_SEARCH_MODE_MATRIX.md`（5 种实验模式）、`HYBRID_SEARCH_MERGE_AND_RANKING_SPEC.md`、`HYBRID_SEARCH_INTERNAL_RESULT_CONTRACT.md`、`HYBRID_SEARCH_EXTERNAL_RESULT_CONTRACT.md`、`HYBRID_SEARCH_FAILURE_CACHE_COST_SPEC.md`、`HYBRID_SEARCH_TRIGGER_EXPERIMENT.md` |
| 实验与上线规划 | `HYBRID_SEARCH_CORE80_EXPERIMENT_PLAN.md`、`HYBRID_SEARCH_ONLINE_METRICS_AND_AB_TEST.md`、`HYBRID_SEARCH_SAFE_ROLLOUT_PLAN.md`（11 个分阶段 Stage）、`HYBRID_SEARCH_INSTRUMENTATION_PLAN.md`、`HYBRID_SEARCH_RISK_REGISTER.csv`（22 项风险登记） |
| 供应商选型参考 | `EXTERNAL_IMAGE_PROVIDER_OPTIONS.md` |
| 审计留痕 | `AUDIT_MANIFEST.json`、`FINAL_AUDIT_LOG.md` |

**`curify-frontend-hybrid-audit` 克隆能否安全删除？——可以，理由与 3.2 完全对称。** 额外补充：
- `FINAL_AUDIT_LOG.md` 明确记录"审计开始与结束时 commit 均为 `5a59c4beba7856136396d8d0d249d5355c85322f`，工作区干净"，并逐条列出未直接逐行读取的次要文件（`lib/nano_page_data.ts` 等）作为"已知未验证项"，这些空白点不依赖保留克隆——它们本身就是**留给未来某个 Stage 6（真正写代码）阶段去解决**的已知事项，而不是本次审计因为克隆被删而"来不及看"的遗漏。
- 该克隆同样来自公开远程仓库 `https://github.com/super-inbox/curify-frontend.git`，可用同一 commit（`5a59c4b`）随时重新克隆复现。
- **特别提醒**：删除时务必确认操作的是 `curify-frontend-hybrid-audit`，而不是 2.1 节强调过的、名字相似但内容完全不同的活跃工作目录 `curify-frontend`。

---

## 4. 临时克隆分析汇总

| 克隆 | 大小 | 状态 | 证据是否已完整落盘到 `visual-search-adhoc` | 建议 |
|---|---:|---|---|---|
| `curify-studio` | 285M | 干净，0 改动 | 是（14 个文件 + SHA-256 清单） | **ARCHIVE / 可安全删除** |
| `curify-frontend-hybrid-audit` | 767M | 干净，0 改动 | 是（18 个文件 + SHA-256 清单） | **ARCHIVE / 可安全删除** |
| `curify-production-baseline-2026-07-15` | 1.8G | 干净，0 改动 | 是（`docs/daily_report/7.15/.../CODE_VERSION_AUDIT.md` 等已引用其全部关键证据） | **ARCHIVE / 可安全删除** |
| `curify-frontend` | 4.9G | **26 处未提交改动** | 否——这些改动本身就是尚未合并的候选分支实现，不是"审计证据"，是"待处理的真实代码" | **KEEP，严禁删除或清理** |

三个只读克隆合计约 **2.85GB** 磁盘空间，删除后不影响任何已完成审计结论的可读性、可追溯性或可信度——因为三份审计报告的写作方式本身就是"自包含"的（file:line 级别引用 + 关键代码片段直接摘录 + SHA-256 完整性记录），这是这三次审计设计上就要求的交付标准，不是事后才发现可以删除。

---

## 5. Keep / Archive / Remove 建议清单

逐项分类，**均为建议，本次审计不执行任何操作**：

### 5.1 KEEP（原样保留，无需任何动作）

| 项 | 理由 |
|---|---|
| `docs/daily_report/7.16/easy-query-bank-v3/` | Session 1 评测输入源文件，体量小（92K），无冗余 |
| `docs/daily_report/7.16/easy-query-production-vs-optimized-comparison-v1/` | 独立完整的对比评测产出，工作报告背景素材 |
| `docs/daily_report/7.16/easy-query-v2-validation/` 内除 `__pycache__` 外的全部 341 个文件 | Session 1 完整交付物 + 复现证据链，体量小（4.3M），无冗余 |
| `docs/daily_report/7.17/search-click-generate-data-audit/` 全部 15 个文件 | Session 2 完整交付物，已经是干净、无噪音的最终形态 |
| `docs/daily_report/7.17/hybrid-search-technical-audit/` 全部 18 个文件 | Session 3 完整交付物，已经是干净、无噪音的最终形态 |
| `docs/daily_report/7.15/easy-query-production-baseline-v1/` 中除 `screenshots/`、`scripts/node_modules` 外的全部文件 | 7/15 生产基线评测的核心结论、评分脚本、manifest，是 Session 1 方法论一致性的直接前情 |
| `~/Desktop/curify-frontend`（活跃分支，26 处未提交改动） | **真实工程 WIP，非清理对象** |

### 5.2 ARCHIVE（建议移入冷存储或压缩保留，不建议直接删除）

| 项 | 大小 | 理由 |
|---|---:|---|
| `docs/daily_report/7.15/easy-query-production-baseline-v1/screenshots/` | 484M | Playwright 原始截图证据，体量大但可能有审计留档价值（例如未来法务/合规复查需要"眼见为实"的截图），建议整体压缩后移入独立的 `archive/` 目录，不建议直接删除 |
| `docs/daily_report/7.15/easy-query-production-baseline-v1/raw/` | 3.3M | 原始采集 JSON 转储，复现证据链一部分，体量不大，可保留原位或一并归档 |
| `~/Desktop/curify-studio` | 285M | 见第 4 节 |
| `~/Desktop/curify-frontend-hybrid-audit` | 767M | 见第 4 节 |
| `~/Desktop/curify-production-baseline-2026-07-15` | 1.8G | 见第 4 节 |

### 5.3 REMOVE_CANDIDATE（纯执行产物噪音，建议清理，对任何已交付结论零影响）

| 项 | 大小 | 理由 |
|---|---:|---|
| `docs/daily_report/7.16/easy-query-v2-validation/scripts/__pycache__/` | 数 KB | Python 字节码缓存，自动生成，删除后重新运行脚本会自动重建 |
| `docs/daily_report/7.15/easy-query-production-baseline-v1/scripts/node_modules/` | 20M | 已被 vendored 的 npm 依赖（含 Playwright），应通过 `npm install` 重新生成，不应留存在文档仓库中 |
| `~/Desktop/visual-search-adhoc/.cache/` | 104M | `external-screenshot-p0-12` 脚本产生的 Chrome 浏览器 profile 运行时缓存（Google/Bing/Canva 三个 profile），纯运行时状态，无内容价值 |
| `scripts/curify-search-collect-stage7/{judge.log,mode_C.log,mode_D.log}` | ~28K | 7/13（早于本次窗口）的孤立运行日志，其功能已被 7/14 建立的 `curify-search-stage7-full-rerun-v2` 取代，当前采集的正式日志已规范落盘在 `docs/daily_report/7.16/easy-query-v2-validation/logs/collection_run.log` |
| `scripts/curify-search-collect-stage7/node_modules/`、`scripts/curify-search-stage7-full-rerun-v2/node_modules/`、`scripts/curify-search-stage7-guard-smoke/node_modules/`、`scripts/curify-search-stage7-mode-contract/node_modules/`、`scripts/external-screenshot-p0-12/node_modules/`、`scripts/curify-search-collect/node_modules/` | 合计约 37M（4 个为空目录，2 个分别 17M/20M） | 全部为可通过 `npm install` 重新生成的依赖目录，不应留在文档仓库中长期存在 |
| `docs/daily_report/7.16/.DS_Store` | 6K | macOS 目录元数据文件，无内容价值 |

### 5.4 流程性建议（不属于"文件"，但影响后续清理的可持续性）

- **仓库根目录建议新增 `.gitignore`**，至少包含 `node_modules/`、`.cache/`、`__pycache__/`、`*.pyc`、`.DS_Store`——这样 5.3 节列出的噪音类别未来会自动被排除，不需要每次人工审计后手动清理。

### 5.5 明确排除在本次分类之外（不属于 Session 1/2/3，不评估）

- `~/Desktop/curify-blog-fix`（不同分支、不同课题，早于窗口）
- `~/Desktop/curify-frontend.zip`、`~/Desktop/visual-search-adhoc.zip`（早于窗口的整体备份压缩包，体量巨大，若需要清理建议作为独立的"磁盘空间盘点"任务另行评估，不应与本次搜索优化课题审计混在一起处理）
- `docs/daily_report/7.11/search-optimization-stage-1` … `7.12/search-optimization-stage-6`：这是同一个"Search Optimization"大课题**更早期**（早于 7/15）的阶段性产出，与本次 Session 1/2/3 属于同一条故事线的前传，建议在撰写最终 Manager Work Report 时视情况在"背景"部分简要提及其存在，但不属于本次 7/15–7/17 窗口的清理范围

---

## 6. 推荐最终交付结构

基于以上盘点，当前 `docs/daily_report/7.15/7.16/7.17` 的既有组织方式**已经足够清晰**，核心 Session 目录之间没有命名冲突、没有内容重复，不需要大规模重组。以下是在现状基础上的**最小改动式**推荐结构（新增 `archive/` 承接大体积证据文件，其余保持原位）：

```
visual-search-adhoc/
  docs/daily_report/
    7.15/
      easy-query-production-baseline-v1/        # KEEP（核心文件），screenshots/raw 建议迁入 archive/
    7.16/
      easy-query-bank-v3/                        # KEEP（Session 1 输入源）
      easy-query-production-vs-optimized-comparison-v1/  # KEEP（背景对比评测）
      easy-query-v2-validation/                   # KEEP（Session 1 核心交付，pycache 待清理）
    7.17/
      search-click-generate-data-audit/           # KEEP（Session 2 核心交付，原样即可）
      hybrid-search-technical-audit/               # KEEP（Session 3 核心交付，原样即可）
      CURIFY_SEARCH_OPTIMIZATION_WORK_REPORT_2026-07-15_TO_2026-07-17_ZH.md   # 待生成的经理汇报报告（下一步）
      FILE_CLEANUP_AND_PROJECT_STRUCTURE_AUDIT_2026-07-15_TO_2026-07-17_ZH.md # 本报告

  archive/                                         # 新增，仅承接体积大、纯证据类内容
    7.15-production-baseline-screenshots/          # 从 easy-query-production-baseline-v1/screenshots/ 迁入
    7.15-production-baseline-raw/                   # 从 easy-query-production-baseline-v1/raw/ 迁入
```

**说明**：本推荐刻意不引入用户示例中 `7.17/final-report/`、`7.17/search-quality/`、`7.17/search-measurement/`、`7.17/hybrid-search/` 这种按主题重新拆分子目录的方案——因为现有的 `search-click-generate-data-audit/` 与 `hybrid-search-technical-audit/` 两个目录名本身已经清楚对应"测量"与"Hybrid Search 可行性"两条主题，重新拆分/改名反而会打断三份 `FINAL_AUDIT_LOG.md`/`AUDIT_MANIFEST.json` 里记录的原始输出路径引用，得不偿失。**唯一建议新增的结构性变化，是把大体积、纯证据类的 `screenshots/`、`raw/` 迁出核心目录、迁入独立的 `archive/`**，让 `7.15/easy-query-production-baseline-v1/` 本身变轻。

---

## 7. 安全清理执行计划（供未来实际执行时参考，本次不执行）

若后续决定按第 5 节建议执行清理，推荐顺序如下（每一步都应独立可回滚）：

1. **第一步（零风险）**：在 `visual-search-adhoc` 根目录新增 `.gitignore`（见 5.4），不影响任何现有文件。
2. **第二步（零风险，纯新增）**：创建 `archive/` 目录，将 5.2 节中 `screenshots/`、`raw/` 两项**复制**（而非移动）过去，人工确认内容完整后再考虑是否删除原位置副本——即先做"双备份"再做"单一位置"，避免一步到位的移动操作出错。
3. **第三步（低风险）**：删除 5.3 节中的执行产物噪音（`__pycache__`、`node_modules`、`.cache/`、孤立日志、`.DS_Store`）——这些均可由对应工具链自动重新生成，风险最低，建议最先执行。
4. **第四步（需要人工确认后再执行）**：删除三个只读审计克隆（`curify-studio`、`curify-frontend-hybrid-audit`、`curify-production-baseline-2026-07-15`）——建议执行前由负责人再次确认 `visual-search-adhoc` 中对应的三份 `FINAL_AUDIT_LOG.md`/`CODE_VERSION_AUDIT.md` 已经过 review 且不再需要"回到克隆里再核对一次"，确认后再删除。
5. **全程严禁触碰**：`~/Desktop/curify-frontend`（活跃分支，26 处未提交改动）——不属于本清理计划的任何一步，任何清理脚本都应显式排除这个路径。

---

## 8. 结论：是否需要在撰写工作报告前先执行清理？

**不需要。** 本次盘点确认：
- 三个 Session 的最终交付物已经完整、干净、无重复地落在预期路径下；
- 本报告第 5 节列出的所有清理项都是"执行产物噪音"或"体积大但独立于结论的证据文件"，**没有一项会影响工作报告撰写时对结论的引用**；
- 唯一需要人工特别注意的是**不要混淆 `curify-frontend`（活跃工程分支）与 `curify-frontend-hybrid-audit`（审计克隆）**——这是本次盘点发现的最重要的一条风险提示。

建议：**直接基于当前目录结构撰写 `CURIFY_SEARCH_OPTIMIZATION_WORK_REPORT_2026-07-15_TO_2026-07-17_ZH.md`**，清理动作（第 7 节）可以作为撰写报告之后的独立后续任务，由负责人在方便的时间单独审批执行。
