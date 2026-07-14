# Remaining Hard Cases — Root Cause / Owner / Priority / Treatment Route（Prompt 7）

**分析日期**: 2026-07-14 | **状态**: COMPLETED | **Final Gate**: READY_WITH_OWNER_HANDOFFS

---

## 1. Executive Summary

本报告正式整合 Stage 7 68 条 Hard Query 中的 22 条 Verified FAIL、7 条 Regression、42 条 PARTIAL（全部审阅，非抽样）以及 12 个 P0 的截图结果，为 **65 条去重后的 Remaining Hard Case** 逐条确认根因、证据、Owner、优先级和处理路线。

核心结论：

- 12 个 P0 中 **0 PASS / 5 PARTIAL / 7 FAIL**（截图标签）；Stage 7 broad 67.6%（PASS+PARTIAL）**不能**直接对项目负责人陈述为"67.6% 完全修复"。
- 22 条 Verified FAIL 中：Catalog/Content Gap 14、Matching Threshold 4、Tokenizer Precision 2、Tokenizer Recall 1、Wrong Entity 1。
- 通过对生产 Catalog 数据（`nano_inspiration.json` + `nano_templates.json`，共 3517 条资产）的直接只读检索复核，本 Prompt 将此前多数"疑似"Catalog Gap 升级为 **CONFIRMED**（0 命中），显著提高了证据置信度。
- 发现 2 条被 PARTIAL 标签掩盖的真实 Regression（Q25、Q32：baseline 10 条结果 → after 0 条结果，仍标记 PARTIAL 而非 FAIL），以及 1 条 P0 内部的 Stage7-PASS/截图-PARTIAL 不一致（Q46/P0_05）。
- 仅有 **6 条**案例（1 条 WRONG_ENTITY + 5 条 TOKENIZER 回归）具备"范围窄、证据 HIGH、可限定测试"的直接代码修复条件；其余绝大多数（42/65）为 Catalog/Content 缺口，需要内容团队介入，非检索机制问题。

## 2. Current Project Status

Prompt 0–2D、4A、Stage 7R Prompt 4 V3、Prompt 5（独立人工验收）、Prompt 6（12 个 P0 截图验证）均已完成，权威事实见本报告输入快照（第 3 节）。本 Prompt（Prompt 7）为只读整合分析，未修改任何上游产出。

## 3. Input Integrity

见 `remaining_hard_cases_manifest_v2_2026-07-14.json` 中 `input_hashes`。所有输入文件（Stage 7 CSV、Prompt 5 CSV/MD、Prompt 6 CSV/MD/JSON、权威 P0 清单、截图目录）在分析开始前后哈希/大小/mtime 一致，未发生修改。Baseline hash 校验通过：
`904ea6a5a17a28dbafe3948de6f5bcb958674e518280e5eaad079b150453d233`。

**目录状态说明**：`remaining-hard-cases/` 目录在本次任务开始前已存在一个文件 `remaining_hard_cases_2026-07-14.csv`（66 行，含表头），其内容与本 Prompt 要求的字段结构高度一致，但本次会话对话历史中没有创建该文件的记录，无法确认其来源与产生时间的可信链条。按 Prompt 规定（"若该目录已存在：检查内容；不覆盖不同内容；使用 `_v2` 或明确版本后缀；在报告中记录"），本次分析**未覆盖或删除**该文件，全部新产出统一使用 `_v2` 后缀，作为本 Prompt 的权威交付版本。

## 4. Analysis Scope

- 22/22 Verified FAIL（不抽样，全覆盖）
- 7/7 Regression（Q24, Q25, Q32, Q36, Q41, Q47, Q67；独立重新计算后确认与已知列表一致，无差异）
- 12/12 P0（全部整合 Stage 7 标签 + P0 截图标签 + 根因 + 是否可作为汇报证据）
- 42/42 PARTIAL（超出"至少覆盖高风险子集+另抽查10条"的最低要求，本次对全部 42 条 PARTIAL 逐条复核，因为所有必需子集——P0 PARTIAL(5)、0 结果 PARTIAL(23)、>5x PARTIAL(8)、Q54——合并后已覆盖 34/42，剩余 8 条一并纳入不增加额外成本）
- 2/2 `>=1000` Case（Q10-D=1324, Q12-D=1593；Q08-C=1600 不在本次 68 条最终数据集的 D 模式统计中出现，经核实 Q08 的 D 模式 after_result_count=88，`>=1000` 的权威口径以 `hard_queries_before_after_68_2026-07-14.csv` 的 D 模式结果为准，Prompt 6 已知统计中列出的 "Q08-C=1600" 属于 C 模式而非最终 D 模式结果，两者不冲突，已在案例记录中以 D 模式数值为准并标注）
- 39 条结果数变化 ≥5× 或由非零跌至零的高风险 Case（含 Wrong Entity、Rewrite、Guard 相关异常复核）

## 5. Root Cause Methodology

区分用户可见结果 / 技术根因 / 责任归属三层。对 `CATALOG_CONTENT_GAP` 类别，本 Prompt 未止步于"结果数低"的推断，而是对生产 Catalog 数据文件（`/Users/baobaoli/Desktop/curify-frontend/public/data/nano_inspiration.json` + `nano_templates.json`，只读）进行了针对性检索（按 `tags`/`search_aliases`/`topics`/`locales.*.title`/`locales.*.category` 字段精确匹配查询的关键词组合），对约 45 条案例独立验证了 Catalog 是否存在对应资产。凡直接检索到 0 命中的，标记 `CATALOG_CONTENT_GAP_CONFIRMED`；未独立复核的沿用 Stage 7 人工标签，标记为 `SUSPECTED` 或按 Stage 7 分类原样保留并降级置信度为 MEDIUM/LOW。

## 6. 22 Verified FAIL Analysis

详见 `remaining_verified_failures_22_v2_2026-07-14.csv`。根因分布：Catalog/Content Gap Confirmed 14、Matching Threshold 4、Tokenizer Precision 2、Tokenizer Recall 1、Wrong Entity 1（与 Prompt 6 已知初步统计完全一致，独立复核未发现差异）。其中 Wrong Entity（Q02）与全部 4 条 Matching Threshold（Q08, Q10, Q12, Q67）具备清晰、范围可限定的修复路径；14 条 Catalog Gap 中本 Prompt 通过直接 Catalog 检索独立确认全部 14 条均为真实 0 命中（CONFIRMED），不可通过检索机制修复。

## 7. 7 Regression Analysis

独立重新核算后确认列表不变：Q24, Q25, Q32, Q36, Q41, Q47, Q67。其中 5 条（Q24, Q25, Q32, Q41, Q47）通过 A/B/C/D 消融拆解**直接锁定**为已上线（Stage 6，非本阶段新改动）字典分词器（d=ON）相对评测专用的 bigram-fallback（d=OFF，从未上线生产）出现精度/召回下降，证据等级 HIGH，是本次分析中最具体、最可操作的修复候选。Q36 为 Catalog Gap 叠加轻微 Ranking 漂移（baseline 中较接近意图的资产在 after 消失）；Q67 为系统性 Matching Threshold 通用词碰撞的一部分。

## 8. 12 P0 Analysis

详见 `p0_12_root_cause_owner_priority_v2_2026-07-14.csv`。Stage 7 verified_label 分布：PASS 1（Q46）/ PARTIAL 6 / FAIL 5；P0 截图标签分布：PARTIAL 5 / FAIL 7 / **PASS 0**。值得注意：Q46（P0_05）在 Stage 7 harness 中为 PASS，但独立截图复现时降级为 PARTIAL，Prompt 6 审阅者笔记将差异归因于同一生产代码路径下的 LLM 非确定性（同一 rewrite 调用在不同请求间结果不同）——这是一个必须披露的标签稳定性风险，不应在项目负责人汇报中将 Q46 简单陈述为"已通过"。另有 2 例（Q60/P0_08、Q53/P0_11）Stage 7 标签为 PARTIAL 但截图标签为 FAIL，进一步说明基于结果计数的自动标签与严格视觉判断存在系统性差异。

## 9. High-risk PARTIAL Analysis

42 条 PARTIAL 全部复核（详见第 4 节范围说明）。其中 **23 条为 0 结果**（约占全部 PARTIAL 的 55%），对终端用户而言与 FAIL 在体验上并无区别，仅因"baseline 同样低/零、未构成相对退化"而未被计入 FAIL。这是 Broad 67.6% 指标必须谨慎解读的核心原因（见第 23 节）。另有 2 条 0 结果 PARTIAL（Q25, Q32）经 A/B/C/D 拆解证实为真实 Tokenizer 回归（baseline 10 条 → after 0 条），是被 PARTIAL 标签直接掩盖的退化案例。

## 10. `>=1000` and >5× Analysis

`>=1000`：Q10（1324，MATCHING_THRESHOLD，CONFIRMED 通用词"night"碰撞）、Q12（1593，MATCHING_THRESHOLD，同一机制）。两者均为已知系统性通用词 relaxed-match 碰撞的代表案例，且 Q10 同时是 P0（P0_12）。

>5× 变化（含 0 结果场景）：共 39 条纳入分析（详见 `remaining_hard_cases_v2_2026-07-14.csv` 的 `case_scope` 含 `GT5X` 标记）。其中相当比例（23 条）是"从个位数/十位数结果跌至 0"，而非从少变多的 flood——这部分被计入"高风险 PARTIAL"而非单纯"结果暴涨"。

## 11. Root Cause Distribution（65 条 Remaining Hard Case，primary_root_cause）

```
CATALOG_CONTENT_GAP_CONFIRMED: 41
TAXONOMY_COVERAGE:              7
MATCHING_THRESHOLD:             5
TOKENIZER_PRECISION:            5
FORMAT_INTENT_COVERAGE:         2
WRONG_ENTITY:                   1
VERTICAL_INTENT_COVERAGE:       1
RANKING:                        1
TOKENIZER_RECALL:               1
SCREENSHOT_ENVIRONMENT:         1
CATALOG_CONTENT_GAP_SUSPECTED:  0
------------------------------------
Total:                          65
```

## 12. Owner Distribution

```
CONTENT_CATALOG: 43
TAXONOMY:         8
SEARCH:           6
TOKENIZER:        6
RANKING:          1
DATA_EVAL:        1
PRODUCT:          0
CROSS_FUNCTIONAL: 0
UNKNOWN:          0
```

## 13. Priority Distribution

```
P0: 1   (Q02 — P0 场景下的 Wrong Entity，范围窄、证据 HIGH、直接影响已展示给项目负责人的截图)
P1: 19  (P0 标记的 Catalog Gap 8 条 + P0 标记的 Taxonomy 1 条 + 系统性 Matching Threshold 4 条 + Tokenizer 回归 5 条 + Q36 回归 1 条)
P2: 45  (非 P0 单条/长尾 Catalog Gap、Taxonomy Dry-run 候选、低置信度或范围模糊案例)
P3: 0
```

## 14. Treatment Route Distribution

```
CONTENT_HANDOFF:          42
TAXONOMY_DRY_RUN:          8
MATCHING_EXPERIMENT:       5
FIX_NOW_TOKENIZER:         5
SHOW_AS_LIMITATION:        2
FIX_NOW_SEARCH:            1
RANKING_INVESTIGATION:     1
DATA_VALIDATION_REQUIRED:  1
DEFER / NO_ACTION / NEEDS_OWNER_DECISION: 0
```

## 15. Search-fixable Cases

仅 **1 条**：Q02（NCT Dream photocard template，P0_01）。根因 WRONG_ENTITY（HIGH 置信度），修复范围：在 Rewrite 接受逻辑中加入主体身份校验，禁止/惩罚将一个具名 IP/实体在零命中时静默替换为同类别下的另一具名实体（本例中 NCT Dream → ILLIT）。

## 16. Tokenizer Cases

**5 条 HIGH 置信度、可限定范围修复**：Q24, Q25, Q32, Q41, Q47。全部通过 A/B/C/D 消融直接锁定为已上线 Stage 6 字典分词器（d=ON）相对评测专用 bigram-fallback（d=OFF，从未上线）的精度/召回损失，且全部为已确认 Regression。另有 1 条（Q56）疑似同机制但未经 A/B/C/D 单独拆解，置信度 MEDIUM，路线为 `DATA_VALIDATION_REQUIRED`（需先做拆解验证，不直接归入修复批次）。

## 17. Taxonomy Cases

**8 条**：Q13(TAXONOMY 为次要根因)、Q17, Q20, Q30, Q43, Q52, Q58, Q59（均为 MEDIUM 置信度，沿用 Stage 7 人工分类，未逐条独立复核）+ Q68（P0_07，HIGH 置信度，主根因为 CATALOG_CONTENT_GAP_CONFIRMED，Taxonomy 为次要根因——因存在一条弱相关 SEL 资产提示可能通过别名/模式映射部分改善）。

## 18. Catalog / Content Cases

**42 条**（含 Q34/P0_10、Q53/P0_11、Q68/P0_07 等 8 条 P0），是数量最大的一类。本 Prompt 独立对约 45 条 Catalog Gap 相关案例做了生产 Catalog 直接检索复核，其中 41 条最终以 `CATALOG_CONTENT_GAP_CONFIRMED`（HIGH 置信度）落地，包含一个值得注意的整簇发现：**Xiaohongshu/抖音/私域社交电商运营格式类查询（15 条）**，Catalog 中甚至连"小红书""抖音""私域"平台名本身都是 **0 命中**，建议 Content/Catalog 团队将其作为一个统一的内容采购计划处理，而非 15 个孤立的长尾缺口。

## 19. Matching Threshold Cases

**5 条**（4 条 FAIL：Q08, Q10, Q12, Q67；1 条 PARTIAL：Q07），均指向同一机制：relaxed-match 阈值（当前为 `ceil(n/2)`）叠加无停用词表的绑定锚点/改写短语，导致单个通用词（如"night""lifestyle""design""schedule"）即可触发大量不相关结果的 relaxed 匹配。其中 Q10（P0_12）被 Prompt 6 审阅者明确记录为"已知限制，明确在本阶段修复范围之外"，因此本 Prompt 将该组整体路线定为 `MATCHING_EXPERIMENT`（需要独立实验验证收紧阈值/加停用词表的影响，而非直接上线修复）。

## 20. Wrong Entity Cases

仅 **1 条**：Q02（P0_01）。详见第 15 节。

## 21. P0 Project-report Usage

```
LIMITATION_EVIDENCE|ROOT_CAUSE_EVIDENCE:            8   (Q02,Q64,Q16,Q15,Q60,Q53,Q10 以及 Q46 的截图不稳定披露)
PARTIAL_IMPROVEMENT_EVIDENCE|ROOT_CAUSE_EVIDENCE:   4   (Q09,Q68,Q06,Q34)
SUCCESS_EVIDENCE:                                    0   (当前 12 个 P0 中不存在，未为美化报告而虚构)
```

## 22. What Is Resolved

严格意义上，本阶段（Stage 7 + Prompt 5/6）**没有**已完全解决的 P0（0 PASS）。在 65 条 Remaining Hard Case 范围内，"已解决"应理解为"根因已明确锁定、证据等级 HIGH、且有清晰有限的下一步"，而非"用户体验已修复"——严格区分见第 9 节方法论。

## 23. What Is Partially Resolved

Broad 指标（PASS+PARTIAL = 46/68 = 67.6%）中的 42 条 PARTIAL：约 8 条（P0 PARTIAL 且截图确认有真实可见改善：Q09, Q68, Q06, Q34）具备可作为"部分改善"证据的资格；其余相当比例（尤其 23 条 0 结果 PARTIAL）在用户可用性上与 FAIL 无实质区别，不应被笼统计入"改善"。

## 24. What Is Not Resolved

- 12 个 P0 中 0 个真正 PASS。
- 22 条 Verified FAIL 全部未解决（本 Prompt 不执行修复）。
- 2 条被 PARTIAL 标签掩盖的真实 Regression（Q25, Q32）。
- 1 条 P0 内部 Stage7-PASS/截图-PARTIAL 不一致（Q46），暴露 LLM 非确定性风险尚未有系统性应对方案。

## 25. What Blocks the Original Project Requirements

- 尚未运行 300+ Easy Query 验证 → 无法排除已上线 Stage 6 字典分词器变更对常见/简单查询的系统性回归风险（5 条已确认的 Hard Query 回归已说明该风险真实存在）。
- Taxonomy Dry-run 尚未启动（8 条候选案例待验证）。
- Content/Catalog 尚未对 42 条内容缺口（含 15 条社交电商运营格式簇）启动采购/生产。
- 以上均不构成"无法交付阶段性报告"的阻塞条件，但构成"无法声称已完整满足项目负责人原始要求"的缺口（见第 26 节）。

## 26. Recommended Execution Order

**Primary Route: `ROUTE_A_LIMITED_REPAIR_FIRST`**（叠加 `ROUTE_D_PARALLEL_HANDOFF` 作为并行执行框架）

理由：本次分析产出了 6 条范围窄、证据 HIGH 的直接代码修复候选（1 条 Wrong Entity + 5 条 Tokenizer 回归），且均是"已上线生产代码"中的确认回归（非本阶段引入），修复价值高、范围可严格限定（各自要求的验证已写入 `required_validation`：需在合并前对 68 条 + 一批 Easy Query 样本回归测试）。与此同时，Content/Catalog（42 条）与 Taxonomy（8 条）轨道不依赖 Search/Tokenizer 修复即可独立并行推进——建议以 `ROUTE_D_PARALLEL_HANDOFF` 的方式同时启动，而非串行等待。

## 27. Limitations

- 本次目录发现的预存文件 `remaining_hard_cases_2026-07-14.csv` 来源不明，未被本次分析采信或覆盖（见第 3 节）。
- 42 条 PARTIAL 中约 34 条依据 Stage 7 既有人工判定（未在本 Prompt 中逐条重新人工目视复核截图），置信度标注为 MEDIUM/HIGH 视具体证据强度而定，未做的是"重新人工视觉判断"，而非"缺少数据"。
- Catalog 检索复核基于静态 JSON 字段匹配（tags/search_aliases/topics/locale 标题与分类），无法完全排除以图像语义/embedding 方式可召回但文本字段未覆盖的边缘情况；对应案例的置信度已相应标注（CONFIRMED 基于文本字段 0 命中，非基于图像内容分析）。
- `Q08-C=1600` 与本报告 `>=1000` 口径（D 模式）的差异已在第 4 节说明，不构成数据矛盾。

## 28. Final Gate

**`READY_WITH_OWNER_HANDOFFS`**

分类完整、Owner/优先级/处理路线均已明确；主要剩余问题（42 条 Catalog/Content + 8 条 Taxonomy）需要 Content/Catalog 与 Taxonomy 团队介入，Search 团队可继续处理其余 6 条范围窄的高置信度案例，两者应并行交接，而非相互阻塞。
