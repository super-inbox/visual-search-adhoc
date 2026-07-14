# Stage 7 Final Independent Manual Spot-check and Gate Acceptance

## 1. Executive Summary

本阶段（Prompt 5）对 Stage 7R Prompt 4 V3 的全部 7 个正式产出文件进行了独立、只读的复核，未重新运行搜索、未调用 LLM、未修改任何 Production 代码或 V3 原始文件。

独立复核结果：
- **数据完整性**：272/272 Run、68/68 Query、A/B/C/D 各 68、0 缺行、0 重复、0 未记录错误——独立重新统计与 V3 报告一致。
- **标签复核**：68 条中 **1 条标签被下调**（Q54：PASS → PARTIAL，独立重新计数发现 Top 10 中仅 2/6 明确相关，未达到 PASS 所需的"多数相关"门槛）。其余 67 条经独立复核确认合理，无 PASS 被高估或 FAIL 被误判的情况。
- **重要修正发现**：V3 报告"Rewrite rejection = 0/192"仅统计了 `slotKey="rewrite"` 类别的拒绝，**遗漏了 20 条真实存在的 `slotKey∈{style,output,mood}` 拒绝记录**（reason 均为 `UNBOUND_NON_SUBJECT_SLOT`，Prompt 2D 新增的 decomposition-modifier native-constraint 检查），涉及 Q04/Q08/Q11/Q12/Q16/Q18 共 10 个 (query,mode) 组合。这是 Guard **按设计正确拒绝**裸露的通用 style/output 修饰词单独作为可执行路径（防止更严重的洪泛），但 V3 报告的字段命名和叙述掩盖了这一真实 Guard 活动。已在本报告中修正披露，不影响任何 FAIL/PARTIAL 标签（这些 Query 本就因 Top10 无关被独立判为 FAIL）。
- **12 个 P0 Query**：在 `docs/daily_report/7.9/manual_review/external_screenshot_queries_12_2026-07-09.csv` 中找到权威清单，全部 12 条均可在 68 条子集中精确匹配。其中仅 **2 条（Q46/Q06）达到可直接用于 Stage 8 截图展示的质量**，其余 10 条仍存在内容缺口、洪泛或错误实体问题，**不适合**在未处理前用于 Before/After 截图展示。
- **Full-catalog**：确认 7.13 记录的全部 3 个历史 Full-catalog 案例（Q39 D、Q40 D、Q42 C，均为 3209）现已确认为 0，独立复核成立。
- **回归**：独立复核确认 V3 报告的 7 条回归（Q24/Q25/Q32/Q36/Q41/Q47/Q67）根因定位合理，未发现遗漏的额外回归。

**独立标签重新统计**：PASS=4（原 5）、PARTIAL=42（原 41）、FAIL=22（不变）→ strict 5.9%、broad 67.6%（不变）、weighted 36.8%（原 37.5%）。

**最终 Gate：`PASS_WITH_LIMITATIONS`**。**流程选择：B**——Stage 7 部分通过，需要先完成 Remaining Hard Cases 根因分类/修复（已在本阶段完成分类），再进入 Stage 8；12 个 P0 Query 中 10 条尚不适合直接用于截图展示。

## 2. Input Integrity

| 文件 | 状态 |
|---|---|
| `hard_queries_baseline_locked_68_2026-07-14.csv` | 存在，69 行，SHA-256 `904ea6a5...` 与给定值精确一致，阶段前后未变 |
| `hard_queries_refreshed_dg_guarded_68_2026-07-14.csv` | 存在，69 行 |
| `hard_queries_before_after_68_2026-07-14.csv` | 存在，69 行 |
| `hard_queries_ablation_abcd_68_2026-07-14.csv` | 存在，273 行（1 header + 272 数据行） |
| `hard_queries_manual_review_68_2026-07-14.csv` | 存在，69 行 |
| `STAGE7_RERUN_SUMMARY_2026-07-14_zh.md` | 存在，可读 |
| `stage7_rerun_manifest_2026-07-14.json` | 存在，合法 JSON |

无文件缺失或损坏。Baseline hash 校验通过，未触发 `BLOCKED_BASELINE_HASH_MISMATCH`。

## 3. Audit Methodology

- 独立读取全部 7 个 V3 输出文件与权威输入（`gold_query_test_set_2026-07-07.csv`、`hard_queries_68_baseline.csv`）。
- 独立重新统计行数、模式分布、标签分布、唯一性。
- 直接读取 `/tmp/curify-stage7r-prompt4-v2/runs/*.json` 原始 Run Checkpoint（V3 CSV 的上游数据源），核对 CSV 派生字段（尤其是 Guard 拒绝相关字段）与原始 `diagnostics.rejectedSlots` 是否一致。
- 对 68 条 Query 逐条重新审视 Baseline Top Results 与 D 模式 Top 10，独立判断是否认同 V3 的 `human_relevance_label`。
- 对 A/B/C/D 四模式的 `final_result_count` 逐条交叉核对，识别 tokenizer(d) 与 rewrite(g) 各自的贡献，验证 V3 §15 的根因归因。
- 检索 7.9 目录下的既有清单文件，确认 12 个 P0 Query 的权威来源（非 68 条 Baseline 内部的 priority 列，两者是不同的清单）。
- 未执行任何写操作于 Production 或 V3 原始文件。

## 4. Data Consistency Results

独立重新计算：

```text
Query count = 68（确认）
Expected Runs = 272（确认）
Actual Runs = 272（确认）
Missing = 0（确认）
Duplicates = 0（确认）
Errors = 0（确认）
A = 68, B = 68, C = 68, D = 68（确认）
D guarded = 68（确认）
Before/After rows = 68（确认）
Manual Review rows = 68（确认）
Human labels filled = 68/68，全部属于 {PASS, PARTIAL, FAIL}，无空值/N/A/UNKNOWN（确认）
```

Query ID 唯一性、Query 文本与权威 68 条逐行一致（gold set vs baseline 顺序比对，0 处不匹配）、无重复 Query 文本、无错误合并——全部确认，无发现新增不一致。Summary/Manifest 的统计数字与独立重新计算完全吻合。

## 5. PASS Review

V3 标注 5 条 PASS（Q05/Q19/Q46/Q54/Q61）。独立复核：

| Query | 复核结论 | 说明 |
|---|---|---|
| Q05 | **确认 PASS** | Top 10 全部为朝代/皇室服饰模板，与"历史皇室服饰灵感"高度吻合，无错误实体，无洪泛 |
| Q19 | **确认 PASS** | Top 8/10 为 strict 品牌视觉 moodboard 模板，直接对应"品牌重塑 moodboard"意图 |
| Q46 | **确认 PASS** | 6/6 结果全部为香薰相关条目，精确匹配，非靠数量伪装 |
| Q54 | **下调为 PARTIAL** | 独立重新计数：6 条结果中仅 2 条（insects butterflies/butterfly）明确相关，1 条勉强相关（water cycle），2 条（en-zh×2）与 1 条（kitchen utensils）为噪音——多数相关门槛未达标，虽相比 Baseline 的重复 generic infographic 仍是改善，但不足以判 PASS |
| Q61 | **确认 PASS** | Top 6/10 为 strict CVC 拼读词族精确命中，多数相关门槛达标；总数 364 偏高但不影响 Top 10 判断 |

**结论**：无 PASS 依赖无关大结果数伪装改善的情况（Q61 总数虽高但 Top10 本身真实相关）；1 条（Q54）被高估，已下调。

## 6. PARTIAL Review

V3 原 41 条 PARTIAL（复核后为 42 条，含 Q54）逐条复核，按以下子类型分布：

| 子类型 | 数量（近似） | 说明 |
|---|---:|---|
| 零结果，确认为目录缺口（非 Guard 回归） | 23 条 | Q23/Q25/Q26/Q27/Q29/Q32/Q35/Q38/Q39/Q40/Q42/Q44/Q45/Q48/Q49/Q50/Q51/Q53/Q55/Q56/Q57/Q60/Q62 |
| 真实部分改善（格式或类目命中，垂直细节未确认） | 约 14 条 | Q03/Q09/Q13/Q17/Q18/Q20/Q22/Q28/Q30/Q34/Q58/Q59/Q54(新) 等 |
| 与 Baseline 同一质量层级，无实质变化 | 约 5 条 | Q14/Q43/Q52/Q68/Q07 |

按 Prompt 5 §八 的明确要求，**"目录缺口"不自动等同于"用户可用"**：本报告为全部 23 条零结果 PARTIAL 单独记录了 `quality_assessment`（"0 results -- objectively unusable for the end user"）与 `root_cause_category`（`CATALOG_CONTENT_GAP`）两个独立字段（见 `stage7_final_manual_labels_68_2026-07-14.csv`），不将"系统责任归因"等同于"搜索质量已改善"。

未发现"Recall 改善但 Precision 下降"被误判为 PASS 的情况；未发现"仅结果数量增加但质量未改善"被误判为改善的情况（该类情况均已在 V3 与本次复核中判为 FAIL，例如 Q01/Q04/Q11/Q15/Q16/Q21/Q37/Q64/Q66）。

## 7. FAIL Review

22 条 FAIL 逐条复核，确认标签合理性与证据。分类分布见 §17。重点确认：

- **错误实体**（1 条）：Q02——NCT Dream 被泛化为通用"kpop group"后误匹配到 ILLIT 组合，证据明确（Top 10 直接显示 illit iroha/minju/moka/yunah）。
- **通用词 relaxed 碰撞导致洪泛**（4 条：Q08/Q10/Q11/Q12 + Q67 计入回归）：均有 A/B/C/D 拆解或 raw diagnostics 证据支持。
- **Tokenizer 精度问题**（2 条：Q24/Q47，均在 §11 回归中重复出现）。
- **目录内容缺口**（14 条）：Top 10 与 Baseline 均无关，属于目录未收录对应内容，非本阶段检索机制可解决。

全部 22 条 FAIL 标签在独立复核中均确认合理，无发现证据不足或根因缺失的情况。

## 8. Guard Review

**关键发现（修正 V3 报告的一处不完整表述）**：直接读取 136 个 C/D 模式的原始 Run JSON（`/tmp/curify-stage7r-prompt4-v2/runs/*-C.json` 与 `*-D.json`）中的 `result.diagnostics.rejectedSlots` 原始字段，独立统计：

```text
总 rejectedSlots 条目（原始，未经 V3 CSV 派生字段过滤）: 20
按 slotKey 分布: style=10, output=9, mood=1
按 reason 分布: UNBOUND_NON_SUBJECT_SLOT=20（全部）
涉及 (query,mode) 组合: 10 个，涉及 Query: Q04, Q08, Q11, Q12, Q16, Q18
总 candidatePaths（存活/被执行）: 314
```

V3 报告的 `rejected_rewrites`/`rewrite_rejection_reasons` 字段口径仅统计 `slotKey==="rewrite"` 的拒绝（该口径下确实为 0），`rejected_subject` 字段仅统计 `slotKey==="subject"` 的拒绝（该口径下也确实为 0）——两个字段本身没有计算错误，但 V3 Summary 中"Rewrite rejection = 0/192"的**叙述**遗漏了第三类拒绝（`decompRejected`，即 style/output/mood 等非 subject/非 rewrite 修饰词槽位的拒绝），该数据在 `compile_outputs.cjs` 的 `deriveGuardFields()` 中已被计算但从未写入任何输出列。

语义澄清：
- **Guard evaluation**：136 次触发中每次都执行了完整评估（含 decomposition modifier 的 native-constraint 检查）。
- **Guard triggered**（本报告口径，含全部三类槽位）：10/136 个 (query,mode) 组合触发了实际拒绝（7.4%），而非 V3 报告字面暗示的 0%。
- **candidate accepted/bound**：与 V3 报告一致，未发现遗漏。
- **candidate rejected**：真实存在（20 条，见上），均为 `UNBOUND_NON_SUBJECT_SLOT`——这是 Guard **按 Prompt 2D 设计正确工作**（阻止裸露的通用 style/output 词单独作为可执行路径，防止更严重的洪泛），不是 Guard 缺陷。
- **fallback used**：Q46/Q30 等案例中 `final_query_paths=[]`（全部候选路径被判定不可执行）但最终仍返回非零结果，确认 Safe Fallback（回退到原始 Query 自身匹配）按设计工作。
- **executable rewrite produced**：122/136 触发案例中有候选路径存活（64/122 最终判定为"success"，见 V3 §13 定义）。

**结论**：Guard 未出现"错误接受漂移 Rewrite"或"错误拒绝合理 Rewrite"的证据；Q04/Q08/Q11/Q12/Q16 虽然 Guard 正确拒绝了裸露修饰词，但其余被接受的多词组合改写候选仍含通用英文词，未能阻止 relaxed 阈值层面的洪泛——这确认了 V3 §14/§15 的结论："`MATCHING_THRESHOLD_LIMITATION` 是本阶段范围外的独立限制，Guard 修复本身未失效"，而非新发现的 Guard 缺陷。

## 9. Rewrite Review

**Rewrite 被拒绝 Case**：`slotKey="rewrite"` 或 `slotKey="subject"` 口径下确认为 **0 cases**——这是数据事实（已通过原始 JSON 独立验证，非字段解析错误）。若计入 decomposition-modifier 槽位（`style`/`output`/`mood`），则为 **20 条拒绝，涉及 10 个 (query,mode) 组合**（见 §8）。

**Rewrite Failure Case 检查**（空输出/无可执行路径/parse failure/model refusal/same-query-only/invalid shape/空 decomposition/全部候选被过滤/API failure/fallback）：
- 空输出（`multi.rewrites=[]` 且 `decomposition={}`）：未在抽样中发现。
- 无可执行路径但仍返回结果（fallback 生效）：Q30、Q46（见 §8，确认为正常 Safe Fallback 行为，非失败）。
- Parse failure / invalid shape / model refusal：抽样与全量错误统计（0 errors）均未发现。
- API failure：1 处（Q49-D 首次尝试 `Request timed out`），重试后成功，非最终失败。

**Rewrite Success 抽样**（10 条，覆盖要求的多样性维度）：

| Query | 语言 | 类型 | final paths（节选） | 结果 |
|---|---|---|---|---|
| Q05 dress to impress historical royalty outfit inspo | 英文 | 长 Query/普通 Query | historical royal fashion inspiration 等 6 条 | 164，PASS |
| Q09 低饱和国风茶包装设计 | 中文 | 普通 Query | 低 tea packaging low saturation... 等 | 94，PARTIAL |
| Q13 汉服马面裙叠穿灵感图 | 中英混合改写 | 专有名词（汉服） | 汉服 hanfu hanfu layering inspiration 等 | 5，PARTIAL |
| Q19 heritage brand rebrand moodboard | 英文 | 品牌/普通 Query | heritage brand mood board 等 6 条 | 278，PASS |
| Q22 健身教练私教工作室品牌 | 中英混合改写 | 普通 Query | 健身 fitness coach studio branding 等 | 40，PARTIAL |
| Q30 手冲咖啡工作室视觉手册 | 中文（Fallback） | 普通 Query | `[]`（全部候选不可执行，Fallback 生效） | 17，PARTIAL |
| Q46 小红书香薰产品种草图 | 中文（Fallback） | 品牌/平台 IP | `[]`（Fallback 生效） | 6，PASS |
| Q52 Gen Alpha slang classroom poster | 英文 | 长 Query/俚语 | Gen Alpha slang infographic 等 6 条 | 307，PARTIAL |
| Q54 Montessori butterfly life cycle 3 part cards | 英文 | 专有名词（Montessori） | Montessori butterfly life cycle cards 等 4 条 | 6，PARTIAL（本次下调） |
| Q61 decodable readers CVC words printable | 英文 | 缩写/专有概念（CVC） | CVC words printable worksheets 等 5 条 | 364，PASS |

**数据限制**：本 68 条 Hard Query 集合中不存在"含数字/型号"的查询样式（如"iPhone 15"式查询），无法从该维度抽样，已如实标注为限制，未虚构此类 Case。

## 10. Regression Review

逐条复核 V3 报告的 7 条回归：

| Query | Baseline | D | 相关性变化 | 是否真实回归 | 严重程度 | 根因 | 是否影响本阶段 Guard 范围 | 是否需阻止进入 Stage 8 |
|---|---|---|---|---|---|---|---|---|
| Q24 | 10/10 咖啡相关 | 2/10 相关+flood | Precision 显著下降 | 是 | 中 | Tokenizer(d)，已上线 Stage 6 | 否，范围外 | 是（该 Query 若用于展示会误导） |
| Q25 | 198 条（噪声匹配） | 0 | 从噪声到诚实空结果 | 轻微（信号本身噪声居多） | 低 | Tokenizer(d)，已上线 Stage 6 | 否，范围外 | 否（Baseline 信号本就不可靠） |
| Q32 | 26 条（噪声匹配） | 0 | 同上 | 轻微 | 低 | Tokenizer(d)，已上线 Stage 6 | 否，范围外 | 否 |
| Q36 | 2 条（1 条较相关） | 1 条（较弱） | 次要条目丢失 | 是，但影响很小 | 低 | 非 Guard/非 d，样本量过小 | 否 | 否 |
| Q41 | 2 条强相关 before/after 模板 | 1 条弱相关 | 真实信号丢失 | 是 | 中 | Tokenizer(d)，已上线 Stage 6 | 否，范围外 | 是 |
| Q47 | 6 条（MBTI 卡片，弱相关） | 2 条（更弱） | Precision 下降 | 是，但较轻 | 低 | Tokenizer(d)，已上线 Stage 6 | 否，范围外 | 否 |
| Q67 | 课堂场景相关条目 | 通用配饰 flood | 意图丢失 | 是 | 中 | Rewrite subject-only 路径 + relaxed 阈值 | **是**，与本阶段 rewrite 路径相关 | 是 |

独立复核未发现 V3 遗漏的额外回归案例（已对全部 68 条逐一核对 Before/After 计数与 Top 10 内容）。**是否影响普通 Query**：7 条回归全部来自本身即"Hard Query"的 68 条集合，无独立证据表明会影响集合外的普通/常见 Query（见 §15）。**是否需阻止进入 Stage 8**：Q24/Q41/Q67 三条建议阻止用于该 Query 自身的 Before/After 展示（会产生误导性对比），其余 4 条影响较小可不阻止。

## 11. Result Count >5x Review

独立重新计算 `after/max(before,1)>5` 或 `before/max(after,1)>5`：命中 **39/68** 条（57.4%）。分布：

- **结果洪泛（数量上升但 Top10 多为无关，已判 FAIL/回归）**：Q01/Q02/Q04/Q07/Q08/Q10/Q11/Q12/Q15/Q16/Q21/Q37/Q52/Q58/Q64/Q66/Q67/Q68（约 18 条）
- **零结果下降（Baseline 非零→After 零，已判 PARTIAL 目录缺口或回归）**：Q23/Q25/Q27/Q29/Q32/Q40/Q42/Q44/Q45/Q48/Q56/Q60（12 条）
- **真实改善（数量上升且 Top10 确认相关）**：Q05/Q09/Q18/Q19/Q34/Q61（6 条，其中 Q05/Q19/Q61 为 PASS）
- **其他（次要丢失/持平）**：Q03/Q28/Q41（3 条）

**结论**：39 条中的多数（约 30/39）反映的是 relaxed matching 碰撞导致的洪泛或目录缺口导致的零结果，而非真实相关性改善——这与 V3 §17 的"PARTIAL_LABEL_CONVENTION"限制说明一致，独立复核确认该限制表述准确，未夸大。

## 12. `>=1000` Case Review

逐条复核当前 3 个 `>=1000` 案例（Q08-C=1600、Q10-D=1324、Q12-D=1593），均已在 V3 §14 详细记录 Query/Rewrite/Token/Guard/Top Results/根因。独立复核：

- Q08-C：无 Guard 触发（`subject_binding/anchor/piggyback` 均 false），确认为改写候选本身含通用词，非 Guard 漏洞。
- Q10-D：Guard 已触发（`subject_binding=true, anchor=true, piggyback=true`），但仍洪泛——根因确认为锚点短语本身含通用英文词"night"，且该碰撞在 pre-fix Baseline 中已同样存在（Top 6 完全一致），非本阶段新增，非 Guard 漏洞。
- Q12-D：与 Prompt 2D 已记录案例完全一致（1593 vs 历史 Live 1598），确认无新漂移。

**三者均判定为 `MATCHING_THRESHOLD_LIMITATION`，均不构成 Result Flooding 意义上需要阻止进入下一阶段的新缺口**——因为三者均有明确、可复现、此前已记录的根因，且均非本阶段 Guard 代码引入的新问题。独立复核未发现任何新增或历史 `>=1000` 案例被遗漏。

## 13. Historical Full-catalog Case Review

| Query | 7.13 旧值 | 本次 D | 本次 C | 是否解决 |
|---|---:|---:|---:|---|
| Q39 | D=3209（Full-catalog） | 0 | 0 | 是 |
| Q40 | D=3209（Full-catalog） | 0 | 0 | 是 |
| Q42 | C=3209（Full-catalog） | 0 | 0 | 是 |

独立复核确认：三者均从"返回整个目录"变为"诚实返回 0 结果"，而非"结果减少但意图变差"（因为 3209/整表结果本身就是无意图可言的失效状态，0 结果虽然对用户不可用，但不是"变差"，是从"灾难性失败"变为"诚实的目录缺口"）。**Full-catalog 判定阈值**（`final_result_count >= catalog_size=3209`）在 V3 与本次复核中一致使用，未发现隐性 Full-catalog（即接近但略低于 3209 的可疑高计数，已逐一核对 68×4=272 行的 `final_result_count`，最高值为 1600，远低于 3209，无隐性 Full-catalog）。

**判定：`FULL_CATALOG_ISSUE_RESOLVED`**（针对这 3 个具体历史案例，且全量 272 行复查未发现任何新增 Full-catalog）。

## 14. 12 P0 Readiness Review

权威 12 条清单来源：`docs/daily_report/7.9/manual_review/external_screenshot_queries_12_2026-07-09.csv`（非 68 条 Baseline 内部的 `priority` 列——后者标注 64 条为"P0"，是不同的、更宽泛的业务优先级标注，与本清单是两个独立概念，未混淆）。

全部 12 条精确匹配到 68 条子集：

| P0 Query | Query ID | Verified Label | Before | After(D) | Stage 8 就绪度 |
|---|---|---|---:|---:|---|
| NCT Dream photocard template | Q02 | FAIL | 10 | 945 | 不适合（错误实体） |
| maker space label set printable | Q64 | FAIL | 10 | 109 | 不适合（洪泛无关） |
| Y2K chrome skincare launch poster | Q16 | FAIL | 10 | 446 | 不适合（洪泛无关） |
| K-beauty glass skin brand launch visual | Q15 | FAIL | 10 | 331 | 不适合（洪泛无关） |
| 小红书香薰产品种草图 | Q46 | **PASS** | 4 | 6 | **就绪** |
| 低饱和国风茶包装设计 | Q09 | PARTIAL | 10 | 94 | 谨慎可用（仅 Top 4 相关，需裁剪展示范围） |
| zones of regulation poster classroom | Q68 | PARTIAL | 10 | 70 | 不建议（与 Baseline 同质，无实质改善可展示） |
| coding unplugged activity cards | Q60 | PARTIAL（零结果） | 10 | 0 | 不适合（无结果可展示） |
| genshin impact Furina fanart wallpaper 4k | Q06 | PARTIAL | 6 | 12 | **就绪**（真实改善，非精确 PASS 但可展示改善对比） |
| Amazon EBC enhanced brand content layout | Q34 | PARTIAL | 0 | 6 | 谨慎可用（方向性相关，非精确匹配） |
| IEP accommodations checklist visual | Q53 | PARTIAL（零结果） | 3 | 0 | 不适合（无结果可展示） |
| 光与夜之恋 卡面设计参考图 | Q10 | FAIL（`>=1000`） | 10 | 1324 | 不适合（洪泛，且为已知 `MATCHING_THRESHOLD_LIMITATION` 案例） |

**结论**：12/12 P0 Query 均可被准确识别，数据完整。**2 条（Q46/Q06）就绪**，**2 条（Q09/Q34）谨慎可用**，**8 条不适合**直接进入 Stage 8 截图展示（会产生误导性 Before/After 或无内容可展示）。未发现 `P0_LIST_NOT_PROVABLE` 情况。

## 15. Stable Control Query Review

**重要限制**：本 68 条 Query 集合按 7.13/7.14 一贯设计**全部为 Hard Query**（Baseline 首轮结果 <5，100% 触发 Rewrite Gate），集合内部**不存在**真正意义上"不需要 Rewrite 的普通 Query"。因此严格来说，本 68 条集合内无法产生真正的"Easy Query"对照组，不得虚构。

**可用的最接近证据**：
1. **集合外部真实对照**：Prompt 4A Mode Contract 报告（`prompt4a/STAGE7_PROMPT4A_MODE_CONTRACT_SUMMARY_2026-07-14_zh.md` §4）记录了 6 条独立的、真正意义上的"普通对照 Query"（English brand identity poster / Genshin Impact fanart 4k / ES6 / GPT-4 poster / watercolor spring flowers / 光与夜之恋 卡面设计），d=ON 与 d=OFF 逐字段完全相同，**0/6 回归**。
2. **集合内部最接近"普通语言"的 10 条代理 Query**（非严格 Easy Query，仅为本 68 条中最不依赖小众 IP/行业黑话的样本，标记为 **Stable Control Queries** 而非 Easy Query）：

| Query ID | Query | Verified Label |
|---|---|---|
| Q05 | dress to impress historical royalty outfit inspo | PASS |
| Q13 | 汉服马面裙叠穿灵感图 | PARTIAL |
| Q18 | clean girl aesthetic skincare packaging mockup | PARTIAL |
| Q19 | heritage brand rebrand moodboard | PASS |
| Q22 | 健身教练私教工作室品牌 | PARTIAL |
| Q24 | 功能性咖啡品牌包装 | FAIL（回归，Tokenizer 驱动） |
| Q43 | 小红书探店打卡九宫格 | PARTIAL |
| Q52 | Gen Alpha slang classroom poster | PARTIAL |
| Q54 | Montessori butterfly life cycle 3 part cards | PARTIAL |
| Q61 | decodable readers CVC words printable | PASS |

这 10 条中 3 条 PASS、6 条 PARTIAL、1 条 FAIL（Q24，已在 §10 定位为 Tokenizer 驱动，非本阶段 Guard 引入）。PASS 比例（30%）显著高于全量 68 条的 5.9%，说明"越接近普通语言表达"的 Query 质量越好，符合直觉，但样本量小（10/68），不构成统计学意义上的强证据。

**Stable Query Regression Risk：`NOT_PROVABLE`（严格意义，因本集合无真 Easy Query）；基于集合外部证据（Prompt 4A 的 6 条真实对照，0/6 回归）与集合内部代理证据（10 条中仅 1 条回归，且已根因归因为范围外的已上线 Tokenizer），倾向性判断为 `LOW`。**

## 16. Broad / Strict / Weighted Metric Interpretation

- **Broad = 67.6%**（独立复核后不变，(4+42)/68）：**不得**直接等同于"67.6% Query 明显改善"。构成中约 23/68（34%）是"零结果但确认为目录缺口"的 PARTIAL（按本项目既有标签约定，非 Guard 回归即可判 PARTIAL），这部分对用户而言**仍然是 0 结果、不可用**，只是系统责任被归因为内容缺口而非算法缺陷。真正代表"用户可感知的相关性提升"的 PARTIAL/PASS 约为 14-18 条（约 20-26%）。**Broad 67.6% 落入预注册 60-80% 区间是真实的，但其构成不应被误读为"多数 Query 搜索质量已改善"。**
- **Strict = 5.9%**（独立复核后由 7.4% 下调，因 Q54 降级）：代表严格意义上"Top 10 多数相关且无明显问题"的比例，是最保守、最贴近真实用户体验的指标。
- **Weighted = 36.8%**（独立复核后由 37.5% 微调）：PASS 计 1 分、PARTIAL 计 0.5 分的加权平均，同样受"零结果 PARTIAL"惯例影响而偏高估。

## 17. Remaining Failure Root Causes

22 条 Verified FAIL 根因分布：

| 分类 | 数量 |
|---|---:|
| CATALOG_CONTENT_GAP | 14 |
| MATCHING_THRESHOLD | 4 |
| TOKENIZER_PRECISION | 2 |
| TOKENIZER_RECALL | 1 |
| WRONG_ENTITY | 1 |
| **合计** | **22** |

详见 `stage7_remaining_failures_2026-07-14.csv`（含 `recommended_fix`/`priority`/`expected_owner`/`blocks_stage8` 字段）。

## 18. Easy / Stable Query Regression Risk

见 §15。结论：**`NOT_PROVABLE`（严格）/ `LOW`（基于代理证据的倾向性判断）**。

## 19. Limitations

- 本阶段的"独立"复核由同一 Claude 实例执行（无法引入真正独立于 Prompt 4 V3 撰写者的第二人工审核者），存在确认偏误（confirmation bias）风险；已尽力通过重新读取原始 JSON（而非仅信任 V3 派生 CSV）来部分缓解此风险，并因此发现了 §8 的 Guard 拒绝口径遗漏。
- 68 条 Hard Query 集合本身不含真正"Easy/普通"Query，Stable Control 部分只能使用集合内代理样本+集合外部小样本证据，非严格对照实验。
- Rewrite Success 抽样（10 条）覆盖了中文/英文/中英混合/专有名词/长 Query/普通 Query/品牌 IP 维度，但该 68 条集合中**不存在**含数字/型号的查询，此维度无法抽样，已如实标注而非虚构。
- 12 个 P0 Query 的"就绪度"判断基于文本/标题层面的结构化复核（`CLAUDE_STRUCTURED_TOP10_REVIEW` 的复核，非图像可视化审核），最终截图前仍需人工肉眼确认实际渲染效果。
- Judge-human agreement 不适用（见 §12 正文与终端回复第 6 项）。

## 20. Final Gate

```text
PASS_WITH_LIMITATIONS
```

理由：数据完整、272/272 无缺失/重复/静默丢弃；68/68 人工标签独立复核后仅 1 处下调（无高估的 PASS 遗留，无被低估的 FAIL）；Full-catalog 历史 3 案例确认解决；`>=1000` 案例均有明确根因，无新增未解释案例；7 条回归均有清晰根因且非系统性；但 Broad/Weighted 改善率的构成含大量"零结果目录缺口"惯例，不能直接等同于用户可感知的搜索质量提升；12 个 P0 Query 中 10 条尚不适合直接用于 Stage 8 展示。

## 21. Stage 8 Recommendation

**流程选择：B**

```text
Stage 7 部分通过，需要先完成 Stage 9 Remaining Hard Cases 根因分类或修复，再进入 Stage 8。
```

具体建议：
- 12 个 P0 Query 中，**仅 Q46（小红书香薰产品种草图）与 Q06（genshin impact Furina fanart wallpaper 4k）适合直接用于 Stage 8 截图展示**；Q09/Q34 谨慎可用（需裁剪展示范围或补充说明）；其余 8 条（Q02/Q64/Q16/Q15/Q68/Q60/Q53/Q10）建议先处理（目录内容缺口需内容侧介入，Q02 需先修复错误实体风险，Q10 需等待未来 Matching Threshold 专项阶段）再进入截图阶段，否则会产生误导性 Before/After 对比。
- 22 条 Remaining FAIL 的根因分类（`stage7_remaining_failures_2026-07-14.csv`）可直接作为下一阶段（内容/Taxonomy/Tokenizer/Ranking 各专项阶段）的输入清单。
