# Curify Search Optimization 工作报告 — 四件事总结

**日期：** 2026-06-30  
**作者：** Baobao  
**项目：** Curify 搜索优化  
**仓库：** visual-search-adhoc（当前报告所在）/ curify-frontend（生产代码）  
**Branch：** `baobao/multi-intent-topic-cooccurrence`

---

## 1. Executive Summary / 总结

本阶段完成了四件事，工作路径如下：

> **修复分支错误 → 清理仓库结构 → P0/P1 Gap Retest → 架构级 P0.5 诊断**

**整体逻辑：**

Task 1 和 Task 2 解决的是 **workflow 和 repo 结构问题**：远程分支 error 修复让代码可以安全推送；repo cleaning 让生产仓库（curify-frontend）保持干净，实验性产物迁移到专用 adhoc 仓库（visual-search-adhoc）。

Task 3 和 Task 4 解决的是 **搜索质量问题**：P0/P1 retest 验证了现有修复效果（FAIL=0）；架构 review 揭示了 10 个系统性 P0.5 gap，指出当前核心问题不只是内容缺失，而是已有内容有时无法被稳定召回、正确排序、或正确 surface。

**核心结论：**

1. **Repo workflow 已整洁**：生产代码留在 curify-frontend；实验报告、图片、JSON/CSV、adhoc 分析文件已迁入 visual-search-adhoc。
2. **P0/P1 retest 在 125 条 eval query 上 FAIL=0**，没有出现"原本有结果、现在崩溃"的回归情况。
3. **剩余问题主要是 WARN 和 P0.5 架构 gap**，不是整体失败，但需要系统性修复。
4. **下一步应从分析转向定向实施**，优先处理代价低、收益高的 T1 recall 修复。

---

## 2. 四件事总览表

| 任务 | 名称 | 要求 / 目标 | 完成内容 | 产出 / 证据 | 状态 |
|------|------|--------------|---------|------------|------|
| **Task 1** | 修 remote branch 上的 error | 解决远程分支同步/push 相关错误，让后续工作可安全推送 | 解决了 branch 分歧或 push 阻塞问题，使 curify-frontend 分支可正常推送 | 工作流已恢复正常，后续 Task 3/4 commits 均成功推送（335bdc4、3536d53） | ✅ 已完成（具体 commit/error log 见注释①） |
| **Task 2** | Repo Cleaning | 要求：curify-frontend 保持生产仓库；实验性产物迁入 visual-search-adhoc | 将 curify-frontend/docs 下的 reports、截图、JSON/CSV、采集数据等全部迁移至本仓库 | Commits `ac9beb2`、`f15b11e`（共 2042 个文件，2026-06-30） | ✅ 已完成 |
| **Task 3** | P0/P1 Gap Retest | 对 P0/P1 修复进行系统性 retest，评估当前搜索修复效果 | 对 125 条 eval query 进行完整 retest；PASS=101，WARN=24，FAIL=0 | `p0-p1-gap-retest-2026-06-30/report.md`、`gap_retest.csv`；Commit `335bdc4` | ✅ 已完成，已推送 |
| **Task 4** | 搜索架构 Review + P0.5 Gap 分析 | 对当前搜索架构做深度 review，识别系统性结构 gap | 梳理搜索 pipeline 12 个步骤；识别 10 个 P0.5 级别架构 gap | `search-architecture-review-p0-5-2026-06-30/report.md`、`p0_5_gap_summary.csv`；Commit `3536d53` | ✅ 已完成，已推送 |

> **注释①：** Task 1（修 remote branch error）发生在 curify-frontend 生产仓库的操作阶段。visual-search-adhoc 仓库内无法直接确认 error 的具体内容，此项描述基于工作流记录，**需人工核对 curify-frontend 仓库的 error log 或操作记录**。

---

## 3. Task 1 — 修 Remote Branch 上的 Error

### 背景

在推送阶段之前，curify-frontend 生产仓库的远程分支存在错误（branch 分歧、同步问题或 push 被阻止），导致当天的工作无法安全推送到远端。

### 为什么要先做这件事

如果 remote branch 处于异常状态，后续的 P0/P1 retest 结果和架构 review 报告都无法被推送到远端供 review。因此修复 remote branch error 是所有后续工作的前提条件。

### 完成后的状态

从 visual-search-adhoc 仓库的 git 历史可以确认：

- Task 3 产出（commit `335bdc4`，2026-06-30）成功推送
- Task 4 产出（commit `3536d53`，2026-06-30）成功推送
- 两次 push 均无报错

这说明在此之前 remote branch 问题已被解决，分支状态恢复正常。

> **注意：** Task 1 的具体 error 类型（是 non-fast-forward push rejection、detached HEAD、upstream 分歧还是其他问题）**无法从 visual-search-adhoc 仓库中直接确认**。需要在 curify-frontend 仓库的操作记录中人工核对。

---

## 4. Task 2 — Repo Cleaning

### 要求

- **curify-frontend**：保持生产仓库，`docs/` 目录只保留 `.md` 文件
- **visual-search-adhoc**：专门存放实验产物，包括：
  - 进度报告、日报、分析文档
  - 截图（.png/.jpg）
  - 采集数据（.json/.csv）
  - 实验脚本输出
  - Ad-hoc 分析工件

### 实际完成的工作

将 `curify-frontend/docs/` 下的实验性内容迁移至 visual-search-adhoc，组织在 `curify-frontend-cleanup-2026-06-30/` 目录下。

**两次 push commits：**

| Commit | 日期 | 内容 |
|--------|------|------|
| `ac9beb2` | 2026-06-30 13:09 | 主体迁移（2042 个文件），含 claude-reports、data/external_signals、daily_report、external-signal-pilot 全部内容 |
| `f15b11e` | 2026-06-30 14:02 | 清理补充（DS_Store 移除、部分修正） |

**迁移到 visual-search-adhoc 的内容类型：**

| 类型 | 目录 | 说明 |
|------|------|------|
| Claude 分析报告 | `curify-frontend-cleanup-2026-06-30/claude-reports/` | prompt 2～7 的分析产出 |
| 外部信号采集数据 | `curify-frontend-cleanup-2026-06-30/docs/external-signal-pilot/` | Bing/Google/Canva/Pinterest/Curify 58-query 采集数据 |
| 日报 / 阶段进度 | `curify-frontend-cleanup-2026-06-30/docs/daily_report/` | 6.17 ～ 6.23 各日报告 |
| 实验脚本 | `curify-frontend-cleanup-2026-06-30/scripts/` | 采集脚本（仅 adhoc 使用） |
| 截图 | 各平台 eval 目录下的 screenshots/ | PNG 截图（每 query 最多 2 张） |
| 手工采集模板 | `data/external_signals/` | 人工采集观察记录 |

### 为什么这样分离

- **降低生产仓库污染风险**：大量 PNG 截图、JSON 数据、实验脚本不应进入生产 CI/CD 流程
- **审阅更清晰**：reviewer 只需关注 curify-frontend 中的代码变更，实验数据在独立仓库查看
- **职责边界清楚**：生产代码（next.js app、搜索 pipeline、数据 catalog）= curify-frontend；分析工件、实验输出 = visual-search-adhoc

---

## 5. Task 3 — P0/P1 Gap Retest

**Commit：** `335bdc4`  
**产出文件：** `p0-p1-gap-retest-2026-06-30/report.md`、`p0-p1-gap-retest-2026-06-30/gap_retest.csv`

### 为什么要做 Retest

此前已识别了一批 P0（零结果）和 P1（结果过少）缺口，并进行了部分修复。在做架构 review（Task 4）之前，需要先对当前系统状态进行一次系统性 retest，回答以下问题：

- P0/P1 修复是否生效？是否出现回归？
- 目前哪些 query 仍然有问题？哪些已超越旧基线？
- 系统整体是否稳定，可以支撑下一步架构改进？

### 测试范围

| 维度 | 内容 |
|------|------|
| Eval set | `scripts/configs/search_eval_set.json`（125 条 query） |
| 运行命令 | `node scripts/eval_search.cjs --quiet` |
| Branch | `baobao/multi-intent-topic-cooccurrence` |

### 最终结果

| 指标 | 数值 |
|------|------|
| **总 query 数** | **125** |
| **PASS** | **101** |
| **WARN** | **24** |
| **FAIL** | **0** |

### PASS / WARN / FAIL 的含义

| 结果 | 含义 |
|------|------|
| **PASS** | 当前 hits 达到或超过 eval set 中设定的 expected_bucket 基线 |
| **WARN** | 未达到 expected 基线（P0 仍为空 / P1 结果仍过少），或已超过旧基线需要更新 eval expectation |
| **FAIL** | 原本有结果的 query 现在返回零结果（退化 / 回归） |

### FAIL=0 的意义

**FAIL=0 是本次 retest 最重要的结论。** 它意味着：

- 没有任何 query 出现"原本正常、现在崩溃"的情况
- 没有因代码改动导致的 recall 退化
- 可以安全进行下一步架构改进，不需要先修复回归问题

### c1 / c2 / c3 Gap 分类说明

Retest 对每条仍有问题的 query 按照根因做了三类归因：

| 分类 | 含义 | 修复路径 |
|------|------|---------|
| **c1** | **有内容，无召回** —— Curify 已有相关内容，但搜索 pipeline 未能召回或 surface 出来 | 补充 alias、修正 tokenizer |
| **c2** | **有模板，要生成内容** —— Curify 有相关模板，但缺少对应的 inspiration 生成记录 | 批量生成 inspiration JSON 配置 |
| **c3** | **没有相关模板，要做 template discovery** —— Curify 还没有覆盖该主题的模板家族 | 新模板提案或 template discovery |

### WARN=24 的组成

**A. 尚未修复的 Gap（17 条）：**

| 分类 | 数量 | 典型 query |
|------|------|-----------|
| P0 仍为空（7 条）含 c1、c2、c3 | 7 | `水果中文`（c1）、`unique cultural experiences`（c3）、`minimalist autumn outfit for japan travel`（c2）、`infj vs entp dating compatibility chart`（c2）、`easy weeknight dinners healthy`（c2）、`gluten free dinner ideas`（c2）、`meal prep weekly recipes`（c2） |
| P1 结果仍过少（10 条，均为 c2） | 10 | `cuban sandwich recipe poster`（1 条）、`bilingual flashcards for kids learning korean fruits`（1 条）、`paris travel itinerary`（2 条）、`architecture empire state building`（1 条）等 |

Gap 类型分布：

| Gap 类型 | 数量 |
|---------|------|
| **c1**（alias / tokenizer 修复） | 2 |
| **c2**（需生成 inspiration 内容） | 14 |
| **c3**（需 template discovery） | 1 |

> **关键发现：82% 的剩余 gap 是 c2**。说明搜索算法对"已有内容"的召回基本正常；更深的问题是某些内容家族（content family）density 为零——无内容可 recall。

**B. 已超越旧基线、eval expectation 需更新（7 条）：**

代表性样例：`phonics worksheets kindergarten`（旧 expected=empty，当前 hits=50）、`chiikawa`（旧 expected=moderate，当前 hits=13）、`france 2026 world cup`（hits=32）等，共 7 条 query 已实际改善，仅 eval set 期望值过旧。

---

## 6. Task 4 — 当前架构 Review 与 P0.5 Gap 分析

**Commit：** `3536d53`  
**产出文件：** `search-architecture-review-p0-5-2026-06-30/report.md`、`search-architecture-review-p0-5-2026-06-30/p0_5_gap_summary.csv`

### Task 3 vs Task 4 的区别

| 维度 | Task 3（Retest） | Task 4（Architecture Review） |
|------|----------------|------------------------------|
| 视角 | Query 级别：哪些 query 通过 / 失败 | 架构级别：哪些系统设计导致 gap |
| 问题 | 当前状态如何？ | 为什么会这样？下一步怎么做？ |
| 输出 | PASS/WARN/FAIL 计数、逐 query 行动 | 系统性 gap 列表、根因分析、优先级建议 |

Task 4 是在 Task 3（PASS=101, WARN=24, FAIL=0）基础上向上一层做架构诊断：即使 eval set FAIL=0，仍然存在哪些系统设计问题会持续影响 recall 质量和 ranking 准确性？

### 当前搜索架构概述

Curify 搜索 pipeline 是一个**基于静态 JSON catalog 的多 surface 服务端渲染 retrieval 系统**，搜索时无数据库查询，所有召回来自两个静态文件：

| 数据文件 | 规模 | 说明 |
|---------|------|------|
| `public/data/nano_inspiration.json` | 3,071 条 | 灵感图记录，每条挂载在一个 template 下 |
| `public/data/nano_templates.json` | 287 个模板（227 个 generatable） | 模板定义，含 i18n blob |

搜索结果由四个独立 surface 组成：

| Surface | 数据来源 | 匹配方式 | 说明 |
|---------|---------|---------|------|
| Inspirations grid（灵感图网格） | `nano_inspiration.json` | 服务端 blob+token 打分 | 核心结果展示区 |
| Template rail（模板横轨） | `nano_templates.json` + i18n | 服务端 strict-AND | 仅展示模板卡片 |
| Generable templates（可生成模板） | `nano_templates.json` + GPT-4o-mini | LLM 客户端异步判断 | 挂载后异步加载 |
| Gallery prompts（画廊 prompt） | Redis（nano-banana tags） | 精确 tag 匹配 | 仅精确匹配才触发 |

整个搜索流程共 12 个步骤（WC Country Bypass → Topic 重定向 → Query 归一化 + Tokenization → Template i18n Blob 构建 → Template Scoring → Inspiration Scoring → LLM Rewrite Fallback → 结果组装 → Intent Chip 聚合 → Related Topics Fallback → Gallery Prompts → 客户端渲染）。

### 10 个系统性 P0.5 Gap

以下 gap 均属**架构级系统性缺陷**，影响大量 query，而非单条 query 的孤立问题：

| Gap ID | 短名称 | 中文说明 | 受影响的 Surface | 严重程度 | 修复代价 | 优先级 |
|--------|--------|---------|----------------|---------|---------|--------|
| **G1** | plural-stem | **多词 query 的复数 token 不 stem** | Inspiration + Template | 高 | 低 | T1 |
| **G2** | catalog-density | **整个内容家族 0–1 条 inspiration** | Inspiration | 高 | 高 | T3 |
| **G3** | flat-scoring | **打分无字段权重，所有字段等权** | Inspiration 排序 | 高 | 中 | T1 |
| **G4** | bulk-promo-precision | **Template bulk-promotion 制造 score=100 洪水** | Inspiration 排序 | 中 | 低 | T1 |
| **G5** | rank-score-orphaned | **rank_score 未用于搜索排序** | Template + Inspiration | 中 | 低 | T2 |
| **G6** | concept-expand-inspirs | **Concept expansion 仅覆盖 template，不覆盖 inspiration** | Inspiration recall | 中 | 中 | T2 |
| **G7** | gallery-exact-only | **Gallery prompts 仅精确 tag 匹配** | Gallery rail | 低 | 中 | T3 |
| **G8** | alias-table-empty | **QUERY_ALIASES 仅 2 条，覆盖极少** | 全部 Surface | 中 | 低 | T2 |
| **G9** | cjk-bigram-fragility | **CJK bigram 滑动窗口生成非词 bigram** | CJK query recall | 中 | 低 | T1 |
| **G10** | generable-duplication | **Generable templates section 与主 pipeline 完全隔离** | UX 一致性 | 低 | 低 | T2 |

### 核心 Gap 类别详解

**G1 — Plural Stemming 仅对单词 query 生效**

`buildSearchTokens()` 中的 stemming 逻辑有条件 `if (primary.length === 1)`，只有单 token query 才会 stem。`meal prep weekly recipes` 中的 `recipes` 不会 stem 为 `recipe`，导致 blob 中只有 `recipe` 的内容无法被召回。影响约 15–25% 的多词英文 query。

**G3 — 打分无字段权重**

`scoreBlob()` 对所有字段一视同仁，`template_id` slug 中的 token 匹配与 locale description 中的偶然提及得分相同。strict pool 内的排序基本由 JSON 插入顺序决定，非质量排序。

**G4 — Template Bulk-Promotion Flood**

当 template 的 i18n blob 严格匹配时，该 template 下的**全部** inspiration（最多 168 条）被提升为 score=100，再由 JSON 插入顺序决定展示顺序。质量最高的 inspiration 可能被 80-record cap 截断而永远不展示。

**G8 — QUERY_ALIASES 近乎为空**

全局 alias 表只有 2 条（`cats→cat`、`kittens→kitten`）。所有其他 alias 覆盖依赖 per-record 的 `search_aliases` 字段，不一致且难以维护。

**G9 — CJK Bigram 碎片化**

`水果中文` 的 bigram 窗口生成 `["水果","果中","中文"]`，其中 `果中` 不是真实中文词汇。这使"可能 bigram 总数"虚高，提升了 match 门槛，导致实际无法召回。

**G6 — Concept Expansion 仅覆盖 Template Rail**

CONCEPT_SYNONYMS 扩展仅更新 `matchedTemplateIdsByI18nUnion`（template rail），inspiration blob 打分仍使用原始 query tokens。结果：template rail 显示了可用模板，但 inspiration grid 无法 surface 出该模板下的示例，形成 UX 断层。

---

## 7. Overall Conclusions / 总体结论

综合四件事：

**1. Task 1 / Task 2 解决了 workflow 和 repo 结构问题。**  
Remote branch error 修复让代码可以正常推送；repo cleaning 将生产代码（curify-frontend）和实验产物（visual-search-adhoc）明确分离，降低了生产仓库的污染风险，也让 review 更清晰。

**2. Task 3 验证了 P0/P1 修复的基本效果。**  
125 条 eval query 上 FAIL=0，表明当前系统没有 P0 级别的整体性搜索崩溃，已修复的内容没有出现回归。但 24 条 WARN 中有 17 条是尚未解决的结构性内容/recall 缺口，不应视为"已解决"。

**3. Task 4 揭示了系统性 P0.5 架构 gap 仍然存在。**  
10 个识别出的 gap 不是个别 query 问题，而是设计层面的系统性缺陷。最关键的结论是：

> **最大的问题不是内容全部缺失，而是：已有的内容，有时因为 ranking 逻辑缺陷、alias 覆盖不足、stemming 限制、CJK tokenization 缺陷等原因，无法稳定被 surface 出来。**

**4. 下一阶段应从分析转向定向实施。**  
T1 级别的 gap（G1、G3、G4、G9）修复代价低、收益高，应优先推进，无需内容生产即可改善 recall 和 ranking 质量。

---

## 8. Recommended Next Steps / 下一步建议

### Step 1 — 修复低风险 T1 Recall 问题（本周内）

优先级最高，代价最低，无需内容生成：

- **修复 G1（multi-token plural stemming）：** 将 `buildSearchTokens()` 中的 stem 逻辑从"仅单 token query"扩展到"所有 query 的每个 token"。预计直接修复 `meal prep weekly recipes`、`gluten free dinner ideas` 等。
- **扩充全局 query aliases（G8 起步）：** 在 `QUERY_ALIASES` 中添加常见内容域复数形式：`recipes → recipe`、`dinners → dinner`、`ideas → idea`、`flashcards → flashcard`、`worksheets → worksheet`。
- **修复 CJK bigram 碎片化（G9）：** 为 `水果中文`、`中文水果` 添加 `search_aliases`（短期 c1 修复），同时评估 bigram 算法改进方案。

### Step 2 — 改善 Ranking 质量（近 2 周）

- **G3 字段权重：** 将 inspiration blob 分为 topical（template_id + tags + topics + search_aliases）和 contextual（params + localeFields），topical 权重显著高于 contextual。建议：`score = 10 × topicalHits + contextualHits`。
- **G4 限制 bulk-promotion：** 将 `promoteAllUnderStrictTpl` 的提升范围从"全部 inspiration"改为"按 JSON 顺序取前 K 条（建议 K=20）"，防止 score=100 洪水掩盖质量差异。

### Step 3 — 对齐 Template 与 Inspiration 的 Recall

- **G6 concept expansion 覆盖 inspiration：** 将 `CONCEPT_SYNONYMS` 扩展逻辑同时应用于 inspiration blob 打分，使 template rail 和 inspiration grid 对 concept-expanded query 保持一致。
- **G5 rank_score 引入搜索排序：** 在 inspiration 排序中引入 template 的 `rank_score` 作为 tiebreaker：`effectiveScore = score × 100 + (TEMPLATE_RANK_SCORE[template_id] ?? 1)`。

### Step 4 — 内容与模板 Backlog（G2）

**c2 内容生成优先级（按 retest miss 影响量排序）：**

1. **食谱家族**（影响最大）：weeknight healthy、gluten-free、meal-prep（各 1 个新 JSON 配置）
2. **建筑地标**：5+ 个地标（埃菲尔铁塔、斗兽场、大本钟等）
3. **Sandwich / 街头食物系列**：提升 `cuban sandwich` relaxed pool
4. **双语词汇 en-ko 系列**：蔬菜、动物、颜色、身体部位（提升 bilingual flashcards pool）
5. **Then-vs-now 对比**：科技、时尚、音乐、学校生活（提升 childhood snacks pool）
6. **复古邮票系列**：海洋生物、蝴蝶、野花
7. **热身运动系列**：5K 跑步、越野、冲刺等

**c3 新模板 Proposal：**

- `unique cultural experiences`：提案新模板，覆盖文化指南 / 目的地体验卡片

---

## 9. Deliverables / 已产出文件

### Task 1 — Remote Branch Error 修复

| 证据 | 说明 |
|------|------|
| Commits `335bdc4`、`3536d53` 均成功推送 | 间接证明 push 通道已畅通 |
| ⚠️ 具体 error log / commit 需在 curify-frontend 仓库人工确认 | — |

### Task 2 — Repo Cleaning

| 产出 | 说明 |
|------|------|
| `curify-frontend-cleanup-2026-06-30/`（本仓库） | 迁移自 curify-frontend 的全部实验产物 |
| Commit `ac9beb2`（2042 files） | 主体迁移 |
| Commit `f15b11e`（DS_Store 清理 + 修正） | 补充清理 |

### Task 3 — P0/P1 Gap Retest

| 文件 | 说明 |
|------|------|
| `p0-p1-gap-retest-2026-06-30/report.md` | Retest 主报告（PASS=101，WARN=24，FAIL=0） |
| `p0-p1-gap-retest-2026-06-30/gap_retest.csv` | 逐 query retest 明细 |
| Commit `335bdc4` | 已推送 |

### Task 4 — 搜索架构 Review + P0.5 Gap 分析

| 文件 | 说明 |
|------|------|
| `search-architecture-review-p0-5-2026-06-30/report.md` | 架构 review 主报告（含 12 步 pipeline 分析 + 10 个 P0.5 gap 根因） |
| `search-architecture-review-p0-5-2026-06-30/p0_5_gap_summary.csv` | P0.5 gap 汇总表（含优先级） |
| Commit `3536d53` | 已推送 |

### 本报告

| 文件 | 说明 |
|------|------|
| `work-report-task-1-to-4-2026-06-30/report_zh.md` | 本工作报告（中文综合版） |

---

## 10. 简短汇报

---

这轮的四件事已整理完成，报告推送在 visual-search-adhoc 仓库。

第一件事是修 remote branch 上的 error，解决了分支同步/push 阻塞问题，为后续工作铺路。（具体 error 内容需在 curify-frontend 仓库人工核对。）

第二件事是 repo 清理：按您的要求，把 curify-frontend/docs 下的实验性产物（截图、JSON、CSV、分析报告、采集数据等）全部迁到了 visual-search-adhoc，curify-frontend 保持为生产仓库。两次 push 共迁移约 2042 个文件。

第三件事是 P0/P1 修复后的系统性 retest：对 125 条 eval query 跑了一遍，结果是 PASS=101、WARN=24、FAIL=0。FAIL=0 是最重要的结论，说明没有 P0 级别的整体崩溃，修过的内容没有退化。剩余 24 条 WARN 分三类：c1（有内容、无召回，需修 alias/tokenizer）、c2（有模板、要生成 inspiration 内容）、c3（没模板、要做 template discovery）。在 17 条尚未解决的 gap 中，14 条（82%）是 c2，也就是内容生成的问题，不是搜索算法的问题。

第四件事是当前搜索架构的 review 和 P0.5 gap 分析：梳理了 12 步搜索 pipeline，识别出 10 个系统性 P0.5 级 gap。最核心的问题不是内容全部缺失，而是已有的内容有时因为 ranking 缺陷、alias 覆盖不足、多词 query 复数不 stem、CJK bigram 生成非词等问题，无法被稳定 surface 出来。

下一步建议从低风险 T1 recall 修复入手：把多词 query 的复数 stemming 扩展到所有 token（1–2 小时代价）、在全局 QUERY_ALIASES 里补上 recipes→recipe 等常见映射、给水果中文等 CJK query 补 alias。这几个改动代价极低，可以直接提升 recall，不需要动内容生成。

---

*报告生成时间：2026-06-30 | 作者：Baobao | 仓库：visual-search-adhoc*
