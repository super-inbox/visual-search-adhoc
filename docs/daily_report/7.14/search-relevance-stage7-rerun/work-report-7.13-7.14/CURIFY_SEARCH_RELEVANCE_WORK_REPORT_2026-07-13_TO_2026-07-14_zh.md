# Curify Search Relevance Optimization Work Report
## 2026-07-13 至 2026-07-14

```text
Project:        Curify Search Relevance Optimization
Date Range:      2026-07-13 至 2026-07-14
Candidate Branch: baobao/search-relevance-phrase-alias-2026-07-09
Candidate HEAD:   c062e618bce4044bedf718aadf59ff69f0999344
Current Status:   候选版本已冻结，等待 300+ Easy Query Validation 完成
Prepared By:      Baobao Li
```

本报告为只读历史结果整合，基于两天内已冻结的正式产出撰写，未新增代码修改、未重新运行搜索、未调用 LLM。与并行运行的 300+ Easy Query Validation 完全隔离，未读取其结果。

**阅读指南**：本报告是关于这两天工作的唯一推荐阅读文档，面向工程管理者，预计阅读时长 10-15 分钟。第 1-12 节聚焦决策与结果；技术实现细节、Hash、Gate 历史、术语定义统一收录在第 13 节附录。

---

## 1. Executive Summary

这两天完成了 Curify 搜索相关性优化的一个完整闭环：**7.13 用真实生产代码跑通第一轮端到端验证，结果不理想**（Strict PASS 0.0%，Broad 改善率仅 5.9%，远低于 60%-80% 目标），并暴露出一个此前从未被量化的系统性问题——LLM Rewrite 产生的通用词与新分词逻辑结合后，在 34% 的困难查询上把搜索结果灌成上千条甚至整个 3209 条目录。**7.14 针对性做了四轮 Guard 补强、修复了实验设计本身的一处合法性问题、完成了合法的 68 条查询完整重跑、独立人工验收、12 个代表性案例的真实截图对比、剩余问题的根因整理，并生成了清晰的优化前后数据材料。**

**主要发现**：结果洪泛问题得到最明确的机制性改善——超过 1000 条结果的异常从 23 条降至 2 条（-91.3%），"返回整个目录"这种最严重的失败形式已清零。

**主要改善**：68 条 Hard Query 的 Broad 改善率（PASS+PARTIAL）从 5.9% 提升到 67.6%，FAIL 数量从 64 条降至 22 条（-65.6%）。

**主要限制**：Broad 67.6% **不是**完全修复率——42 条 PARTIAL 中约 21-23 条仍是 0 结果的目录内容缺口案例，对用户不可用。12 个代表性案例的真实截图验证结果为 **0 PASS / 5 PARTIAL / 7 FAIL**，没有一条完全修复；剩余 22 条 Verified FAIL 中 14 条（64%）是目录内容缺口，需要 Content 团队长期投入，非搜索代码可独立解决。

**当前状态**：候选版本已冻结，300+ Easy Query Validation 正在并行运行中（本报告未读取其结果，标注 `IN PROGRESS / PENDING FINAL RESULT`）。

**一段话结论**：这两天的技术验证工作已完整闭环，搜索机制层面的核心缺陷（结果洪泛、实验合法性）已解决，但距离满足完整任务清单（普通查询验证、Taxonomy、内容缺口、PR）仍有明确差距，**当前尚未完全满足全部原始要求**。

---

## 2. Objectives

**项目目标**：解决 Curify 搜索在中文复合短语、CJK 分词、低召回识别、LLM Rewrite 质量等环节的已知缺陷，并用固定的 68 条 Hard Query 做真实的 Before/After 验证——而非仅凭代码改动宣称问题已解决。

**完整搜索链路**：

```text
Query 输入
→ 中文分词与专有名词保护（Protected Phrase / CJK Tokenizer）
→ 首次召回（buildSearchTokens / scoreBlob）
→ Low-result Detection（LOW_RESULT_THRESHOLD=5）
→ LLM Rewrite（getMultiQueryPaths，gpt-4o-mini）
→ 二次召回（decomposition/rewrite 多路径执行）
→ Merge / Dedup / Ranking（inspirationById Union 合并）
→ 相关性验证（人工 Top10 判定 / LLM Judge）
```

**本轮重点问题**：

1. 中文复合词误拆（`小红书`、`手冲咖啡`、`二手奢侈品` 等被 bigram 兜底错误切分）。
2. Low-result 判定缺陷（只看数量不看质量）。
3. Rewrite 空输出与意图漂移（品牌到品类过度泛化，如 NCT Dream → ILLIT 错误实体）。
4. Full-catalog / Result Flooding（通用词触发"零必需 token 恒真"边界情形）。
5. 68 条真实困难查询的端到端相关性表现。
6. 12 条代表性高优先级案例的真实截图验证。
7. Easy Query 回归风险（已上线 Tokenizer 是否影响普通查询，当前仍在验证）。

**范围边界**：本轮不包含 Taxonomy 体系建设、Content/Catalog 内容采购、生产环境部署——这些作为后续步骤记录在第 12 节。

---

## 3. Timeline

### 2026-07-13

| 步骤 | 内容 | 结果 |
|---|---|---|
| 数据/代码/Baseline 盘点 | 确认 Fix1/Fix2 从未合并推送，68 条 Baseline 权威来源确认，12 张截图/300+ 集合均不存在 | 审计完整关闭 |
| 中文复合短语审计与修复 | 发现并修复繁简转换 bug（`手沖咖啡`无法触发保护规则） | 65/65 测试通过 |
| CJK 分词方案评估 | 5 方案 × 55 query 对照实验 | 选定 Dictionary-first Scoped Hybrid |
| Low-result 判定审计 | 发现 2 处生产缺陷 | 审计完整关闭 |
| LLM Rewrite 稳定性加固 | 修复解析/缓存 bug，10 条真实 API 调用验证 | 184/184 测试通过，发现 2 处模型幻觉 |
| Dictionary-first Scoped Hybrid 实现 | 落地分词/别名分母修复方案 | 232/232 测试通过 |
| **68 条 Hard Query 首次 A/B/C/D 消融** | 真实生产代码端到端验证 | **验收未通过**（Broad 5.9%），发现 Generic Decomposition Catalog Flood |

### 2026-07-14

| 步骤 | 内容 | 结果 |
|---|---|---|
| Flood Guard 实现（Prompt 2） | 修复 7.13 发现的洪泛问题（Guard 1/2/3） | 260/260 测试通过，不证明真实相关性提升 |
| Rewrite Array Guard（Prompt 2B） | 修复 Replay 测试发现的 5 个残留洪泛 Case | 295/295 测试通过 |
| 弱数字锚点 + Subject 校验（Prompt 2C） | 修复 Live Smoke 暴露的 3 类新问题 | 335/335 测试通过，Live Human FAIL 仍 30.4% |
| Anchor Provenance 修复（Prompt 2D） | 修复 Piggyback 漏洞根因 | Live Human FAIL 降至 13.0%，READY_FOR_FULL_68 |
| Runtime Toggle 缺失（Prompt 4，首次停止） | 发现无合法 d-off 开关，主动停止 | BLOCKED_INVALID_ABLATION_MODE |
| Runtime Toggle 新增（Prompt 4A） | 新增类型安全 dEnabled 开关 | READY_FOR_PROMPT4 |
| **68 条完整重跑**（Prompt 4 V3） | 合法 Baseline 恢复 + 272 次运行 | 272/272 完整，PASS_WITH_LIMITATIONS |
| **独立人工验收**（Prompt 5） | 重新读取原始数据复核标签 | Q54 下调，最终 4/42/22 |
| **12 P0 截图验证**（Prompt 6） | 真实截图逐条判读 | 0 PASS/5 PARTIAL/7 FAIL |
| **Remaining Hard Cases 整合**（Prompt 7） | 65 条去重案例根因/Owner/优先级分类 | READY_WITH_OWNER_HANDOFFS |
| 优化前后数据对比 | 生成可读材料 | 完成 |
| **候选版本冻结** | 停止修改搜索代码 | 启动 300+ Easy Query Validation（并行运行中） |

---

## 4. Work Completed on 2026-07-13

**做了什么**：完成 Stage 1-7 全部工作——数据/代码盘点、Protected Phrase 审计修复、CJK 分词方案选型、Low-result 判定审计、LLM Rewrite 稳定性加固、Dictionary-first Scoped Hybrid 完整实现、68 条 Hard Query 首次 A/B/C/D 消融验证。

**如何验证**：单元测试逐阶段递增（65/65 → 184/184 → 232/232）、TypeScript 0 错误、本地 Build 通过、10 条真实 LLM API 调用抽样验证；68 条 Hard Query 用 272 次 A/B/C/D 运行 + 272 次独立 LLM Judge 盲判（非人工视觉审核）。

**首轮结果**：

```text
PASS / PARTIAL / FAIL = 0 / 4 / 64
Strict PASS rate = 0.0%    Broad improvement rate = 5.9%    Weighted = 2.9%
D 模式 >=1000 结果 = 23/68（33.8%）    D Full-catalog = 2 条    C Full-catalog = 1 条
```

**为什么第一轮效果差**：

1. Rewrite decomposition 常退化为单个高频通用英文词（`poster`/`template`），单独就能命中目录中大量标签文案。
2. 当通用词恰好落入停用词集合，分词后 token 数组为空，打分公式在双方均为 0 时对任意记录恒为真，相当于把整个目录当作命中结果。
3. Guard 覆盖不足——Stage 5/6 此前只用 2 个手选样例标记过这类风险，从未在全量数据上量化。
4. 实验模式本身存在合法性问题：Mode A/C（d=OFF）是通过 `git show HEAD` 文本重建旧逻辑实现的，不是同一份生产代码的两种运行时状态（这一问题直到 7.14 才被发现并处理）。
5. 全程使用自动化 LLM Judge，不是完整人工视觉审核。

**7.13 的价值（不是一次失败且无价值的工作）**：首次在全量数据上量化了 Generic Decomposition Catalog Flood 这一系统性问题；确认 3 个 Full-catalog 灾难性失败案例；为 7.14 的 Runtime Toggle 新增和 Guard 加固提供了明确证据；提供了 SHA-256 锁定的合法 Baseline，供 7.14 直接复用。

**结论**：7.13 的结果不适合直接作为最终效果结论，但可作为问题发现、Baseline、风险识别和后续修复依据。

---

## 5. Work Completed on 2026-07-14

**问题发现**：7.13 暴露的 Generic Decomposition Catalog Flood——LLM Rewrite 产生的通用词与真实分词逻辑结合后，在 23/68 条查询上把结果灌成上千条甚至整个目录。

**Guard 改进**（四轮迭代，Prompt 编号见括号）：

| 轮次 | 发现的问题 | 修复 | 结果 |
|---|---|---|---|
| 第一轮（Prompt 2） | Flood 根因确认 | Guard 1（空 Token Fail Closed）+ Guard 2（Subject 绑定）+ Guard 3（诊断/Cache 修正） | 260/260 测试通过 |
| 第二轮（Prompt 2B） | 5 个残留 `>=1000` Case | Guard R（Rewrite 候选锚点校验） | 295/295 测试通过 |
| 第三轮（Prompt 2C） | 弱数字误判/Subject 从未校验/跨语言无条件放行 | Guard N + Guard S + 跨语言修复 | 335/335 测试通过，Live Human FAIL 仍 30.4% |
| 第四轮（Prompt 2D） | Anchor Piggyback 根因确认 | Anchor Provenance 最小化修复 | Live Human FAIL 降至 **13.0%**，356/356 测试通过，`READY_FOR_FULL_68` |

**Runtime Toggle**（Prompt 4 首次停止 → Prompt 4A）：正式运行前发现当前代码无任何开关可关闭"d"特性，构造对照组唯一已知方法是被规则禁止的技术——**主动停止，未伪造消融**。随后新增 `lib/searchTokens.ts` 类型安全的 `dEnabled` 开关，使 A/B/C/D 四模式首次可由同一份生产代码构造（32/32 Smoke 通过，375/375 全量测试通过）。

**68 条重跑**（Prompt 4 V3）：从合法 Baseline Checkpoint 恢复，272 次运行（194 行复用已验证成功记录，78 行新执行，1 次瞬时超时重试成功），272/272 完整无缺失。首次人工判定 PASS=5/PARTIAL=41/FAIL=22。

**独立人工验收**（Prompt 5）：重新读取原始 Run Checkpoint JSON（而非仅信任派生 CSV），发现 Q54 应从 PASS 下调为 PARTIAL，最终 **PASS=4/PARTIAL=42/FAIL=22**；并发现并纠正了 V3 报告一处 Rewrite 拒绝统计口径遗漏。

**P0 验证**（Prompt 6）：12 条代表性案例真实截图（Before 线上生产 / After 本地 dev server，同一 branch/HEAD）逐条人工判读，不直接照搬 Stage 7 标签。结果 **0 PASS / 5 PARTIAL / 7 FAIL**，与 Stage 7 标签存在 3 处差异（均为截图标签更保守）。

**Remaining Hard Cases**（Prompt 7）：对约 45 条 Catalog Gap 案例做生产 Catalog 数据直接检索复核（非仅推断），65 条去重案例全部完成根因/Owner/优先级/处理路线分类，发现 2 条被 PARTIAL 标签掩盖的真实回归。

**候选版本冻结**：用户决定停止修改搜索代码，转入 300+ Easy Query Validation（并行运行中）。

---

## 6. Search Improvements

按模块整理，实现细节见附录（第 13.5 节）。

| 模块 | 原始问题 | 解决方案 | 影响 | 验证 | 当前限制 |
|---|---|---|---|---|---|
| **Protected Phrase** | 小红书/手冲咖啡/二手奢侈品等中文复合词被 bigram 错误切分 | 4 条 CJK 规则最长匹配优先提取；繁简转换表补 5 组字符对 | 繁体输入触发规则 bug 修复；D 模式命中 8/68 查询 | 65/65 测试通过 | 未加别名注入意图闸门（产品策略决策） |
| **Tokenizer** | 滑动窗口 bigram 误报率高（最高 625 条无关结果） | 引入真实 jieba 分词器 + Protected Dictionary + ASCII/型号保留 + 别名分母修复 | 手冲咖啡 0/16→0/17；极简主义海报 625→6 | 5 方案×55 query + 48/48 测试 | Precision/Recall Tradeoff（部分通用词仍单独清阈值） |
| **Low Result** | 只看数量不看质量，bigram 误报绕过 Rewrite 安全网 | 阈值定义未变（`LOW_RESULT_THRESHOLD=5`），修复触发判定与误报识别 | 消除 2 处已确认生产缺陷 | 审计+回归测试 | 前端独立声明的同值常量需人工同步 |
| **Rewrite** | 空输出（26.5%）、意图漂移、通用词槽位退化 | 多候选 rewrites + decomposition 拆解 + Safe Fallback | 50/68 返回可执行路径；Fallback 按设计工作（Q30/Q46 验证） | 单测 + 10 条真实 API 调用 | 模型幻觉无法确定性捕获（比亚迪海豹→BYD Seagull等） |
| **Guard** | Generic Decomposition Catalog Flood（洪泛/Full-catalog） | 四轮迭代（Guard 1/2/3→R→N/S→Anchor Provenance），见第 5 节 | D `>=1000` 23→2；Full-catalog 2/1→0/0 | 356/356 测试；Live Human FAIL 30.4%→13.0% | Q10/Q12 等少数 Case 明确记录为范围外限制 |
| **Runtime Toggle** | 无法用同一生产代码构造 d=OFF 对照组 | `lib/searchTokens.ts` 新增类型安全 `dEnabled` 开关 | A/B/C/D 首次由同一代码构造 | 32/32 Smoke + 375/375 全量测试 | — |

---

## 7. Results

### 7.1 68 Hard Query

| 指标 | 7.13 | 7.14 | 变化 |
|---|---:|---:|---:|
| PASS | 0 | 4 | +4 |
| PARTIAL | 4 | 42 | +38 |
| FAIL | 64 | 22 | -42（-65.6%） |
| Strict（PASS/68） | 0.0% | 5.9% | +5.9pp |
| Broad（(PASS+PARTIAL)/68） | 5.9% | 67.6% | +61.7pp |
| Weighted | 2.9% | 36.8% | +33.9pp |
| D `>=1000` | 23 | 2 | -21（-91.3%） |
| D Full-catalog | 2 | 0 | -2（-100%） |
| C Full-catalog | 1 | 0 | -1（-100%） |
| Zero-result | 11 | 23 | +12 |
| Low-result（1-4） | 9 | 5 | -4（-44.4%） |

**重要说明（仅在此处与 Executive Summary 强调，不重复展开）**：Broad 67.6% 是 PASS+PARTIAL 的占比，**不是完全修复率**——42 条 PARTIAL 中约 21-23 条仍是 0 结果的目录内容缺口案例，对用户不可用；真正代表用户可感知改善的比例约 18/68（26.5%）。Zero-result 增加是 Guard 拦截危险泛化的预期副作用（诚实返回 0 优于洪泛无关大结果），不代表质量下降，但对用户而言仍是"看不到结果"。

### 7.2 12 个 P0

| P0 | Query | Stage7 标签 | 截图标签 | 根因 | Owner | 优先级 |
|---|---|---|---|---|---|---:|
| P0_01 | NCT Dream photocard template | FAIL | **FAIL** | WRONG_ENTITY | SEARCH | P0 |
| P0_02 | maker space label set printable | FAIL | **FAIL** | CATALOG_CONTENT_GAP | CONTENT_CATALOG | P1 |
| P0_03 | Y2K chrome skincare launch poster | FAIL | **FAIL** | CATALOG_CONTENT_GAP | CONTENT_CATALOG | P1 |
| P0_04 | K-beauty glass skin brand launch visual | FAIL | **FAIL** | CATALOG_CONTENT_GAP | CONTENT_CATALOG | P1 |
| P0_05 | 小红书香薰产品种草图 | PASS | **PARTIAL** | SCREENSHOT_ENVIRONMENT | DATA_EVAL | P2 |
| P0_06 | 低饱和国风茶包装设计 | PARTIAL | **PARTIAL** | CATALOG_CONTENT_GAP | CONTENT_CATALOG | P1 |
| P0_07 | zones of regulation poster classroom | PARTIAL | **PARTIAL** | CATALOG_CONTENT_GAP | CONTENT_CATALOG | P1 |
| P0_08 | coding unplugged activity cards | PARTIAL | **FAIL** | CATALOG_CONTENT_GAP | CONTENT_CATALOG | P1 |
| P0_09 | genshin impact Furina fanart wallpaper 4k | PARTIAL | **PARTIAL** | CATALOG_CONTENT_GAP | CONTENT_CATALOG | P1 |
| P0_10 | Amazon EBC enhanced brand content layout | PARTIAL | **PARTIAL** | CATALOG_CONTENT_GAP | CONTENT_CATALOG | P1 |
| P0_11 | IEP accommodations checklist visual | PARTIAL | **FAIL** | CATALOG_CONTENT_GAP | CONTENT_CATALOG | P1 |
| P0_12 | 光与夜之恋 卡面设计参考图 | FAIL | **FAIL** | MATCHING_THRESHOLD | SEARCH | P1 |

```text
PASS=0  PARTIAL=5  FAIL=7  Comparable=12/12
Success Evidence=0  Partial Improvement Evidence=4  Limitation Evidence=8
```

（Evidence 计数采用 Prompt 7 `_v2` 口径；Prompt 6 原始口径为 3/9，差异原因是 Prompt 7 将 P0_05 因截图复现不稳定重新归类，并将 P0_07/P0_10 上调，两版本均保留在技术 CSV 中不隐藏。）

### 7.3 剩余 22 条 FAIL 根因分布

```text
CATALOG_CONTENT_GAP: 14    MATCHING_THRESHOLD: 4    TOKENIZER_PRECISION: 2
TOKENIZER_RECALL: 1        WRONG_ENTITY: 1
```

---

## 8. Before vs After

```text
FAIL:            64 → 22   （-65.6%）
D >=1000 洪泛:     23 → 2    （-91.3%，最明确的机制性改善）
Full-catalog:     3 个历史案例 → 0（D/C 模式均清零）
Broad:            5.9% → 67.6%
Strict:           0.0% → 5.9%
P0（截图验证）:    无历史数据 → 0 PASS / 5 PARTIAL / 7 FAIL
```

**为什么 Broad 大幅提升但 P0 没有 PASS**：Broad 是宽松指标，42 条 PARTIAL 中约一半仍是 0 结果但被归类为目录缺口（非算法回归）；P0 截图是更严格的用户可见效果检查，不依赖结果计数，且 P0 本身是高优先级难例（fandom IP、错误实体风险），难度天然高于平均水平。两套指标回答的是不同问题，不矛盾，但不应只用 Broad 单一数字做汇报。

图表（位于 `before-after-data-comparison/charts/`）：`hard_68_labels_before_after.png`、`hard_68_rates_before_after.png`、`flooding_before_after.png`、`p0_12_status.png`、`remaining_root_cause_distribution.png`。

---

## 9. Remaining Issues

### 9.1 Root Cause 分布（65 条去重 Remaining Hard Cases）

```text
CATALOG_CONTENT_GAP_CONFIRMED: 41   TAXONOMY_COVERAGE: 7   MATCHING_THRESHOLD: 5
TOKENIZER_PRECISION: 5   FORMAT_INTENT_COVERAGE: 2   WRONG_ENTITY: 1
VERTICAL_INTENT_COVERAGE: 1   RANKING: 1   TOKENIZER_RECALL: 1   SCREENSHOT_ENVIRONMENT: 1
```

### 9.2 Owner 分布

```text
CONTENT_CATALOG: 43   TAXONOMY: 8   SEARCH: 6   TOKENIZER: 6   RANKING: 1   DATA_EVAL: 1
```

### 9.3 Priority 分布

```text
P0: 1（Q02 Wrong Entity）   P1: 19   P2: 45   P3: 0
```

### 9.4 Treatment Route

```text
CONTENT_HANDOFF: 42   TAXONOMY_DRY_RUN: 8   MATCHING_EXPERIMENT: 5
FIX_NOW_TOKENIZER: 5   SHOW_AS_LIMITATION: 2   FIX_NOW_SEARCH: 1
RANKING_INVESTIGATION: 1   DATA_VALIDATION_REQUIRED: 1
```

**仅 6 条案例**（1 条 Wrong Entity + 5 条 Tokenizer 回归）具备范围窄、证据 HIGH、可直接代码修复的条件；其余绝大多数需要 Content/Taxonomy 团队介入。**用户已决定冻结当前版本，本轮不执行这些有限修复**，优先转向 300+ Easy Query Validation 确认整体风险面。

**内容缺口整簇发现**：小红书/抖音/私域社交电商运营格式类查询（15 条），Catalog 中连平台名本身都是 0 命中，建议作为统一采购计划处理，而非孤立长尾缺口。

---

## 10. Requirement Status

完整 21 项清单见 `CURIFY_SEARCH_RELEVANCE_REQUIREMENT_STATUS_2026-07-14.csv`。汇总：

```text
COMPLETE: 9      COMPLETE_WITH_LIMITATIONS: 2      IN_PROGRESS: 3      NOT_STARTED: 7
```

| 类别 | 代表项 | 状态 |
|---|---|---|
| 搜索机制（Fix2/Low-result/Rewrite/d+g/Guard） | R01-R07 | COMPLETE / COMPLETE_WITH_LIMITATIONS |
| 验证（68/P0/Remaining/对比） | R08-R11 | COMPLETE / COMPLETE_WITH_LIMITATIONS |
| 300+ Easy Query / 完整回归 | R13/R19 | IN_PROGRESS |
| Easy Low-result 清单 | R12 | NOT_STARTED |
| Taxonomy（审计/Dry-run/Topic Page Flag/导入） | R14-R17 | NOT_STARTED（4 项全部） |
| Content/Catalog 内容缺口处理 | R18 | NOT_STARTED |
| 最终报告 | R20 | IN_PROGRESS |
| PR/部署 | R21 | NOT_STARTED |

**证据**：所有状态均可追溯至具体产出文件（见 CSV `evidence_file` 列）。**限制**：搜索机制主线完成度高，但 Taxonomy 全套、内容缺口处理、PR 均未启动。

---

## 11. Current Status

**当前版本能否发布**：**不建议**。理由：(1) 300+ Easy Query Validation 尚未完成，无法排除对普通查询的系统性回归风险；(2) 12 个代表性 P0 案例 0 PASS；(3) 分支从未推送、无远程分支、无 PR。

**已解决**：Full-catalog（D/C 模式均清零）、大规模 Rewrite Flooding（-91.3%）、A/B/C/D 实验合法性问题、Rewrite 安全回退机制、Baseline 审计完整性。

**明显改善但未完全解决**：68 条 Broad 改善率、`>=1000` 结果异常（剩余 2 条已知根因未修复）、Rewrite 稳定性（Live Human FAIL 30.4%→13.0%）、部分 P0（4 条真实可见改善但均非完全修复）。

**未解决**：12 P0 无 PASS；Catalog 内容缺口（41-42 条）；Taxonomy（4 项全部未启动）；Tokenizer 回归（5 条，已上线非本阶段引入）；Wrong Entity（Q02）；Easy Query 系统性回归尚未证明。

**被阻塞**：PR/部署被 300+ Easy Query Validation 结果阻塞；Taxonomy 导入被 Dry-run 阻塞；Content Handoff 尚未排期。

**完成度（三种口径，不给单一可能误导的百分比）**：

```text
搜索机制技术主线（Guard/Tokenizer/d+g/A-B-C-D/68/P0/Root Cause）: 约 90-95%
7.13-7.14 两天计划内工作:                                        约 100%（衡量的是"计划要做的事是否做完"，不代表搜索质量达标）
完整任务清单（含 Easy Query/Taxonomy/PR 等后续）:                  约 40-45%（按工作量加权，非单纯数量占比）
```

---

## 12. Next Steps

```text
1. 等待 300+ Easy Query Validation 完成（IN PROGRESS / PENDING FINAL RESULT，本报告未读取其结果）
2. 完成后更新：Executive Summary、Results、Requirement Status、Current Status、Next Steps 共 5 个章节
3. 根据 Regression Gate 结果判断是否保留冻结候选版本
4. 启动 Taxonomy 审计 / Dry-run（8 条候选已识别）、Topic Page Flag 验证、Taxonomy 导入
5. 启动 Content/Catalog 内容缺口采购（42-43 条，含 15 条社交电商运营格式簇）
6. 完整回归（含 300+ 结果）
7. 更新最终报告
8. Commit / Push / PR（不自行 Merge）
```

不得把尚未执行的工作写成已完成。300+ Easy Query 相关的具体指标（Zero Rate/Low Rate/Regression Gate/PASS-FAIL 分布）在完成前不得填写或估计数字。

---

## 13. Appendix

### 13.1 关键 Hash 与 Git 状态

```text
Baseline SHA-256: 904ea6a5a17a28dbafe3948de6f5bcb958674e518280e5eaad079b150453d233
                   （7.13 与 7.14 两份 Baseline 文件字节级一致，确认连续性）
Production (curify-frontend): baobao/search-relevance-phrase-alias-2026-07-09 @ c062e618bce4044bedf718aadf59ff69f0999344
Adhoc (visual-search-adhoc):   main @ 39d8d0a1c6a1c3bd9d31fedfc2d51954cff44f18
```

### 13.2 Mode 定义

```text
A: d=false, g=false（无字典特性，无Rewrite）
B: d=true,  g=false（仅字典特性）
C: d=false, g=true（仅Rewrite）
D: d=true,  g=true（当前生产代码路径，候选版本）
```

### 13.3 标签与 Root Cause 定义

```text
PASS:    Top10多数/精确命中真实查询意图，无明显问题
PARTIAL: 部分相关或方向正确但未达PASS门槛（含0结果但归类为目录缺口的案例）
FAIL:    Top10多数不相关，或结果洪泛/Full-catalog，或错误实体

CATALOG_CONTENT_GAP_CONFIRMED: 生产Catalog数据直接检索复核确认0命中
MATCHING_THRESHOLD:            relaxed-match阈值(ceil(n/2))叠加无停用词表导致的通用词碰撞
TOKENIZER_PRECISION/RECALL:    Stage 6字典分词器相对评测bigram-fallback的精度/召回损失
WRONG_ENTITY:                  Rewrite将具名实体错误泛化替换为另一同类实体
TAXONOMY_COVERAGE:             目录层级/分类覆盖不足
SCREENSHOT_ENVIRONMENT:        LLM非确定性导致截图复现与harness记录不一致

Owner: SEARCH(Rewrite/Guard/匹配逻辑) / TOKENIZER(Stage6字典分词器) / CONTENT_CATALOG(内容采购)
       / TAXONOMY(分类层级) / RANKING(排序权重) / DATA_EVAL(评估方法/环境问题)
Priority: P0(直接影响已展示截图，范围窄证据HIGH) / P1(系统性或高优先级关联) / P2(长尾) / P3(未使用)
```

### 13.4 Gate 历史

```text
Stage 7(7.13):  FAILED_ACCEPTANCE
Prompt 2:        READY_WITH_LIMITATIONS
Prompt 2C:       NEEDS_ANOTHER_GUARD_FIX
Prompt 2D:       READY_FOR_FULL_68
Prompt 4:        BLOCKED_INVALID_ABLATION_MODE
Prompt 4A:       READY_FOR_PROMPT4
Prompt 4 V3:     PASS_WITH_LIMITATIONS
Prompt 5:        PASS_WITH_LIMITATIONS
Prompt 7:        READY_WITH_OWNER_HANDOFFS
Comparison:      COMPARISON_COMPLETE_WITH_LIMITATIONS
本 Work Report:  WORK_REPORT_COMPLETE_PENDING_EASY_QUERY_UPDATE
```

### 13.5 Search Improvements 实现细节

**Guard 完整清单**（Prompt 2→2D 累计）：Guard 1（Empty Tokens Fail Closed）、Guard 2（Subject-bound Decomposition）、Guard 3（结构化诊断+Cache TTL 分类修正）、Guard R（Rewrite 候选锚点校验：Option A 共享 subject token / B Protected Phrase 等价 / C 独立锚点）、Guard N（弱数字属性识别，区分 4k/1080p 与 es6/GPT-4 类强标识符）、Guard S（Decomposition Subject Validation，不安全时绑定回原 Query 锚点或整体拒绝）、Anchor Provenance 修复（防止候选与绑定前原始不安全文本共享 token 被误判已锚定）、Cross-language Guard（跨语言候选不再无条件放行）、Safe Fallback（全部路径不可执行时回退原始 Query 自身匹配）。

**Cache TTL**：executable success 7 天正向缓存；negative cache 10 分钟负向缓存（覆盖解析失败/shape 错误/全部拒绝/全部同 query/空 decomposition）。修复原因：此前 TTL 分类基于"JSON 是否解析成功"，会把合法空输出错误归为 7 天正向缓存；改为基于"是否存在至少一条可执行的二次检索路径"后，Guard 判定结果自动正确反映到 Cache 分类。

**实验与人工审核体系**：A/B/C/D 为固定 Mode Contract，4×68=272 次独立运行；Prompt 4 V3 从中断前已验证成功的 194 个 Run 恢复（Resume 而非重跑）；Prompt 5 直接读取原始 JSON 而非仅信任派生 CSV；Prompt 6 基于真实渲染截图逐条判读，不依赖结果计数；Prompt 7 对约 45 条 Catalog Gap 案例做生产 Catalog 数据直接检索复核。

### 13.6 Key Decisions

不接受非法 A/C 消融（主动停止而非沿用 `git show` 方法）；新增合法 Runtime Toggle 而非继续用 harness 重建；保留原始 Baseline（SHA-256 锁定全程未覆盖）；Resume 而非重跑（复用已验证成功的历史 Run）；独立人工审核与自动结果分开、重新读取原始数据；不隐藏 P0 FAIL；Root Cause 逐条 Owner 化；冻结当前代码，先跑 300+ Easy Query 再决定后续；暂不执行已识别的有限修复。

### 13.7 Lessons Learned

Guard 必须验证主体（Subject）和锚点本身，不仅是下游候选；结果数不是相关性，不能用计数代替质量判断；Fail closed 会增加 Zero-result 但可能提高 Precision，这是需要说明的权衡而非隐藏的缺陷；Catalog 内容不足不能靠 Rewrite/Tokenizer 解决；截图验证比聚合指标更严格，能捕获聚合指标掩盖的差异；消融必须来自同一生产代码；独立人工审核应重新读取原始数据而非仅信任派生结果；Root Cause 与 Quality Label 不能混为一谈；回归验证必须覆盖 Easy Query（Hard Query 集合按设计无法验证这一维度）。

### 13.8 常见问题

**7.13 为什么效果差？** 第一轮真实端到端验证如实暴露了 0% Strict PASS 和此前未量化的系统性洪泛问题——这是诊断本身在起作用，不是执行失误。

**67.6% 是什么？** 68 条中 PASS+PARTIAL 的占比，不是完全修复率，其中约三分之一是 0 结果但归类为目录缺口的 PARTIAL 案例。

**为什么 P0 没有 PASS？** P0 截图验证比聚合标签更严格，多数案例根因是目录内容缺口（9/12），检索机制改进无法制造未被创作的内容。

**普通 Query 是否安全？** 尚未证明。300+ Easy Query Validation 并行运行中，本报告未读取其结果；已知 68 条集合内有 5 条 Tokenizer 回归，说明风险类别真实存在，但样本本身不含真正的 Easy Query，无法外推。

**为什么还没 PR？** 300+ Easy Query Validation（用于排除对普通查询的系统性回归）尚未完成，在此之前提交 PR 存在未知风险。

### 13.9 文件与图表索引

完整文件导航见 `CURIFY_SEARCH_RELEVANCE_FILE_GUIDE_2026-07-13_TO_2026-07-14_zh.md`。核心技术文件：`CURIFY_SEARCH_RELEVANCE_REQUIREMENT_STATUS_2026-07-14.csv`（21 项要求）、`curify_search_relevance_work_report_manifest_2026-07-14.json`（输入/输出哈希）、`UPDATE_AFTER_EASY_QUERY_VALIDATION_2026-07-14.md`（300+ 完成后的更新说明）。

### 13.10 术语表

```text
d（Dictionary）: Stage 6 字典优先分词/打分特性
g（Generation/Rewrite）: Stage 5 LLM Rewrite
Full-catalog: final_result_count >= catalog_size(3209)，返回整个目录
Broad improvement rate: (PASS+PARTIAL)/68
Strict PASS rate: PASS/68
Weighted improvement rate: (PASS+0.5×PARTIAL)/68
Piggyback（Anchor Piggyback）: 候选与绑定前的原始不安全文本共享token被误判为已锚定的Guard漏洞
```

---

**报告状态：`WORK_REPORT_COMPLETE_PENDING_EASY_QUERY_UPDATE`**
