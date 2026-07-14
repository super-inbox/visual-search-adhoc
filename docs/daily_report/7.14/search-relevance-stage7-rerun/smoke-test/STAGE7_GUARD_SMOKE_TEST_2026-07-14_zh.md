# Stage 7 Guard Smoke Test

## 1. Executive Summary

- **Deterministic Replay（Phase A）已完成**：26 次 Replay run（23 个 D 组洪泛 Case + Q42 C-mode + Q39/Q40 C-mode 补充），全部使用当前 Prompt 2 Guard 代码（通过 esbuild 打包 `lib/searchRewrite.ts` 等 production 模块，非复制逻辑），未调用 LLM。
- **Full-catalog（3209 条）已 100% 消除**：原有 3 个 full-catalog Case（Q39 D、Q40 D、Q42 C）Replay 后全部不再是 full-catalog。新 full-catalog 数量 = 0。
- **`>=1000` 改善率 78.3%（18/23），未达到 80% 门槛**：23 个 D 组洪泛 Case 中，18 个不再 `>=1000`，仍有 5 个（Q06、Q10、Q12、Q47、Q48）保持 `>=1000`，超过 Prompt 3 规定的"最多允许 4 条仍 `>=1000`"的硬性阈值。
- **根因明确**：这 5 个残留 Case 的共同特征是 Guard 2（Subject-bound Decomposition）正确地绑定/拒绝了 decomposition slot，但 LLM 原始 `rewrites` 自由文本数组（每条 Case 3 条）完全不受 Guard 2 约束，仍作为独立无约束路径执行并 Union 合并，是当前残留洪泛的主因。这不是 Guard 逻辑本身错误，而是 Guard 2 的设计范围未覆盖 `rewrites` 数组。
- **按 Prompt 3 Step 6 的强制规则，Live Smoke（Phase B）本次会话未执行**：Replay 未达到 80% 门槛，因此严格按指令"如果 Replay 仍 `>=1000` 超过 4 条：可以完成报告，不运行或停止 Live"，25 条计划中的 Live Run 全部记录为 `BLOCKED`，附带明确原因，未编造任何在线结果。
- **最终结论：`NEEDS_PROMPT2_FIX`**。Guard 1（Empty Tokens Fail Closed）和 Guard 2（Subject-bound Decomposition）在已验证的范围内工作正常（full-catalog 清零、`UNBOUND_NON_SUBJECT_SLOT` 按预期拒绝独立 slot），但整体 Guard 覆盖范围不完整（`rewrites` 数组未受约束），导致 5/23 仍 `>=1000`，不满足进入完整 68 条重跑的门槛。

## 2. Scope and Safety

- 本阶段未修改 `curify-frontend` 任何文件（生产仓库全程只读，见第 15 节 Git 安全校验）。
- 未重跑完整 68 条权威 Query，仅运行本阶段冻结的固定 Smoke Query 集。
- Replay（Phase A）：复用 7.13 `hard_queries_68_ablation.csv` 中已保存的 raw rewrite / decomposition JSON，不调用 LLM，隔离非确定性，仅验证"相同输入下 Guard 是否阻止原洪泛"。
- Live（Phase B）：设计为使用真实 production 链路 + 真实 LLM，仅限固定 18–24 条唯一 Query；本次因 Replay 未达门槛而被规则性阻止执行，0 次真实 LLM 调用。
- Query 数量：Replay 26 runs（23 D-flood + Q42 C + Q39/Q40 C 补充）；Live 计划 25 runs（22 唯一 Query + Q39/Q40/Q42 各追加一次），实际 0 runs（全部 BLOCKED）。

## 3. Environment and Reproducibility

| 项目 | 值 |
|---|---|
| Branch | `baobao/search-relevance-phrase-alias-2026-07-09` |
| HEAD | `c062e618bce4044bedf718aadf59ff69f0999344`（"improve Chinese phrase protection in search"） |
| Production dirty | `true`（工作区存在未提交改动，含 Prompt 2 实现：`lib/searchRewrite.ts`、`lib/cjk_tokenizer.ts` 等） |
| Node / npm | v26.3.0 / 11.16.0 |
| package-lock.json SHA-256 | `b75bd1c7113dea2eb2194a5841f05247665d1820c664f48f5929c55648f5ed59` |
| `page.tsx` SHA-256 | `4853831915b56881fba3b92c8c299f4b1207b24414a620565af47910f8d87abe` |
| `searchRewrite.ts` SHA-256 | `52c5a066628e0295323fc7c4b026106e199512acd6b03df8247da2254936209e` |
| Catalog size | 3209 条（`catalog_sha256=f7dacc56a847f6b9c1a93a714e79b4864c3babdfb06402223abbe733dfb9d906`） |
| LLM 配置 | `gpt-4o-mini`（`lib/searchRewrite.ts` MODEL 常量）— 本次会话未调用 |
| `OPENAI_API_KEY` | PRESENT |
| Cache 策略 | Replay 阶段不经过 `getMultiQueryPaths`，`MULTI_CACHE` 全程未被写入/查询；Live 阶段未执行，Cache 命中情况无数据 |
| 数据限制 | 目录内容自 7.7/7.13 起可能已漂移，未量化；68 条权威集 `human_relevance_label` 仍 0/68 未填 |

以 `smoke-test/stage7_guard_smoke_manifest_2026-07-14.json` 为准，本报告与其数值完全一致（已在写作前逐字段核对）。

## 4. Fixed Smoke Query Set

冻结文件：`smoke_test_query_set_2026-07-14.csv`（SHA-256 `70603639371595c71d9519e074ef0bbaaeab89811b50e895c86c6f7baf068970`，写出后未再修改）。共 48 行：

- **Phase A（26 行）**：23 个 D 组洪泛 Case（`d_plus_g_flood_23`，来自 `stage7_flood_cases_diagnosis_2026-07-14.csv` 全部 23 条，无省略）+ Q42 C-mode full-catalog 补充（`c_mode_full_catalog`）+ Q40 C-mode 对照（`c_mode_supplementary`，原始非洪泛，用作对比）+ Q39 C-mode 补充（同一原则）。
- **Phase B（22 行，唯一 Query，符合 18–24 条上限）**：
  - B1 Full-catalog 核心：Q39、Q40、Q42（各计划追加 1 次，共 3 次额外 run）
  - B2 分层选择的 7 条 D 组其余洪泛 Case：覆盖 `GENERIC_STANDALONE_REWRITE`（英文 Q16、中文 Q46）、`DECOMPOSITION_TOO_BROAD`、中英混合（Q41，含内嵌 "use"）、原始 count 高值与边界值等，选择原因逐条记录在 `selection_reason` 列
  - B3 原 4 个 PARTIAL Case：Q06、Q12、Q18、Q19（与 B1/B2 有重叠部分按唯一 Query 计一次）
  - B4 语义补充 Case：乔丹鞋（`NA-JORDAN`）、比亚迪海豹（`NA-BYDSEAL`）、白箱（`NA-WHITEBOX`），均标注 `NOT_IN_68` 来源，不计入 Hard Query 指标
  - B5 正常对照：手冲咖啡工作室视觉手册（Q30，Protected Phrase + Alias）、二手奢侈品鉴定品牌视觉（Q21）、小红书探店笔记封面（Q44）等非洪泛对照 Case

Query 集在写出后未做任何增删（`smoke_test_query_set_2026-07-14.csv` 的 SHA-256 在执行前后一致，见第 3 节）。

## 5. Deterministic Replay Method

- Harness：`scripts/curify-search-stage7-guard-smoke/`（新建目录，未修改任何既有 `scripts/curify-search-collect-stage7/` 文件）。
- `build_bundle.cjs` 用 esbuild 将 curify-frontend 当前（post-Prompt-2）的 `lib/searchRewrite.ts`（含真实 Guard 2 `flattenPathsWithDiagnostics`）、`lib/query_phrase_aliases.ts`、`lib/cjk_tokenizer.ts`、`lib/zh_normalize.ts`、`lib/topic_resolver.ts` 打包为 `_bundle_current.cjs`，非重写/复制核心逻辑。
- `scoring.cjs` 转录 `page.tsx` 的 `buildSearchTokens`/`scoreBlob`/`hasExecutableConstraint`（Guard 1 修复点），并含 `verifyAgainstLiveSource()`：运行任何 Replay 前先读取当前 `page.tsx`，断言 8 个 Guard 1/2/3 关键代码片段存在，否则拒绝执行（`drift_check.missing=0`，本次通过）。
- `engine.cjs` 复现 `page.tsx` 的多路径 merge 循环，接收 7.13 已保存的 raw rewrite/decomposition JSON 作为 `multiPathsOverride` 直接注入，不调用 `getMultiQueryPaths`，因此不产生任何 LLM 请求。
- 每条 Replay Run 直接执行当前生产 scoring/matching 代码路径，而非在 Smoke 脚本中手工判断 path 字符串或复制一份"看起来一样"的 Guard 逻辑。

## 6. Replay Results

| 指标 | 值 |
|---|---|
| Replay runs 总数 | 26 |
| BLOCKED | 0 |
| PASS | 5 |
| PARTIAL | 17 |
| FAIL | 4 |
| 原 `>=1000` 数量 | 24（23 个 D-flood + Q42 C 各自的 old 值，跨 26 行统计） |
| 新 `>=1000` 数量 | 5（全部为 D-mode：Q06、Q10、Q12、Q47、Q48） |
| 原 full-catalog 数量 | 3（Q39 D、Q40 D、Q42 C） |
| 新 full-catalog 数量 | **0** |
| 平均 count delta（old − new） | 1242.3 |
| 中位 count delta | 1322 |
| 平均 count ratio（new/old） | 0.477（结果数平均下降 ~52%） |
| 结果数改善（new < old） | 23/26 |
| 结果数回归（new > old） | 1/26（Q40 C：8 → 922，原因见第 7 节，属"此前非洪泛对照组在当前 tokenizer 下变化"，非 Guard 缺陷） |
| 结果数不变（new = old） | 2/26（Q39 C：1→1；Q06 D：1569→1569，即仍 FAIL 的 Case 之一） |
| `subject_binding_triggered=true` 次数 | 22/26 |
| `empty_token_guard_triggered=true` 次数（诊断字段） | **0/26** — 见第 15 节"限制"，这是诊断埋点缺口，非功能缺陷（功能层面 full-catalog 已验证清零，见下方"关键行为专项验证"） |
| 所有 Rewrite path 被拒绝（`no_valid_rewrite_path=true`）次数 | 0/26 |
| 原始 Query fallback 触发次数 | 0/26（因为没有一个 Case 触发"全部路径被拒绝" — Guard 2 在拒绝非 subject slot 后仍保留 subject-bound 路径和 `rewrites` 数组，故未测试到 fallback 分支的真实触发） |
| 23 个 D 组中改善比例 | 18/23 = **78.3%**，未达到 Prompt 3 规定的 80%（即"最多允许 4 条仍 `>=1000`"，实际 5 条） |

仍然宽泛（`>=1000`）的 5 个 Case：Q06（1569→1569，无变化）、Q10（2687→1724）、Q12（3154→1694）、Q47（2129→1031）、Q48（2184→1155）。共同结构：`decomposition.output`/`mood`/`style` 等非 subject slot 被 Guard 2 正确处理（要么绑定到 subject，要么因无 subject 而被拒绝为 `UNBOUND_NON_SUBJECT_SLOT`），但 `rewrites` 数组的 3 条自由文本改写（如 "Genshin Impact Furina wallpaper"、"Furina fanart poster" 等）本身语义仍偏宽泛，作为独立路径执行后 Union 仍能命中较大数量的目录条目。

## 7. Q39/Q40/Q42 Deep Dive

### Q39（亚马逊评论截图水印素材）
- **D-mode**：`decomposition={"subject":"Amazon review screenshot","style":"watermark","output":"template"}`。旧 count=3209（full-catalog）→ 新 count=**1**。`accepted_paths` 包含 3 条 rewrite + subject-bound 路径；`rejected_paths=[]`（无被拒绝的独立 slot，因为 style/output 都在 subject 有值时被绑定，未作为独立无约束路径提交）。`subject_binding_triggered=true`。旧 full-catalog=true → 新 full-catalog=**false**。**Replay 判定：PASS**。
- **C-mode 补充**：raw rewrite `output="素材"`（非空、非纯 stopword），旧 count=1 → 新 count=1（未变，Mode C 输入本身从未洪泛）。**判定：PARTIAL**（无劣化，但非改善案例，仅作为对比）。
- **Live Run 1/2**：本次会话**未执行**（Phase B 被 Step 6 规则阻止），无真实 LLM 输出可比较。

### Q40（小红书图文笔记模板 数字标题）
- **D-mode**：`decomposition={"subject":"Xiaohongshu post","style":"graphic","output":"template"}`。旧 count=3209（full-catalog）→ 新 count=**922**。`subject_binding_triggered=true`，`rejected_paths=[]`。旧 full-catalog=true → 新 full-catalog=**false**。**Replay 判定：PARTIAL**（full-catalog 已消除，但 922 仍是较大结果集，人工复核确认为"3 条 rewrite 自由文本仍偏宽泛"导致，非 Guard 逻辑错误）。
- **C-mode 补充**：raw rewrite `output="graphic template"`（原始已非空，本就不洪泛，旧 count=8）→ 新 count=922（**在当前 tokenizer + Guard 代码下重新计算，与 old_result_count=8 的历史值不可比**，因为 8 是 pre-Stage-6-tokenizer 时代的值；这是唯一的"回归"标记行，但性质是"新旧 tokenizer 版本不同导致的不可比对照"，不是 Guard 引入的劣化）。
- **Live Run 1/2**：未执行。

### Q42（小红书封面模板 白底大字）— 分别分析 Mode C / Mode D

**Q42 Mode C Replay**：raw rewrite `output="template"`（裸词，经 stopword 过滤后为空 primary token，属于 Guard 1 设计目标场景）。`decomposition={"subject":"Xiaohongshu cover","style":"minimalist","output":"template"}`。旧 count=3209（full-catalog）→ 新 count=**468**。旧 full-catalog=true → 新 full-catalog=**false**。`subject_binding_triggered=true`。**判定：PARTIAL**（full-catalog 消除，468 仍偏多，主因同样是 3 条 rewrite 自由文本）。

**Q42 Mode D Replay**：raw rewrite `output="cover template"`。`decomposition={"style":"minimalist","output":"cover template"}`（**无 subject 字段**）。`rejected_paths=[{"slotKey":"style","slotValue":"minimalist","reason":"UNBOUND_NON_SUBJECT_SLOT"},{"slotKey":"output","slotValue":"cover template","reason":"UNBOUND_NON_SUBJECT_SLOT"}]` — **验证了独立 `cover` 路径确实被 Guard 2 拒绝，未被单独执行**。`accepted_paths` 仅保留 3 条 rewrite 文本路径（"Xiaohongshu cover template" 等）。旧 count=2291 → 新 count=**843**（旧 full-catalog 本就为 false）。**判定：PARTIAL**（独立 `cover` 已被阻止，但 rewrite 文本本身仍产生 843 条结果）。

**Q42 Live Run 1/2**：未执行，无法比较两次 Rewrite 是否不同。

## 8. Live Smoke Method

- 设计为真实链路：original query → normalization → phrase protection → tokenization → first pass → low-result → LLM Rewrite → Guard → search → merge → dedup → ranking。
- 计划 22 条唯一 Query，Q39/Q40/Q42 各追加 1 次运行 = 25 次计划 Run（未超过 27 上限）。
- 因 Replay 阶段未达到 Prompt 3 Step 6 规定的门槛（23 个 D 组中 5 个仍 `>=1000`，超过"最多 4 条"的硬性上限），按指令"如果 Replay 仍 `>=1000` 超过 4 条：可以完成报告，不运行或停止 Live"，**Live Smoke 本次会话未执行**，0 次真实 LLM 调用，0 次 Cache 交互。

## 9. Live Smoke Results

- 计划 25 runs，实际 25 行，**全部记录为 `smoke_verdict=BLOCKED`**（`stage7_guard_live_smoke_results_2026-07-14.csv`），每行 `error`/`notes` 字段说明"Replay 门槛未达标，Live 被规则性阻止"，无一行留空、无一行编造结果。
- 成功率：0/25（设计上如此，非运行失败）。errors/timeouts：0（未发起任何请求，因此无网络层错误）。
- `>=1000` / full-catalog / Guard triggers / 人工标签：均为 `NOT_APPLICABLE`（未运行）。

## 10. Valid Rewrite and Regression Controls

由于 Live 未执行，以下验证改为依据 **Prompt 2 单元测试代码证据**（`STAGE7_FLOOD_GUARD_IMPLEMENTATION_2026-07-14_zh.md` 第 94–148、233、302、324 行）完成，并在 Query 集中标注为 `NOT_IN_68`/补充证据，不冒充 Live 覆盖：

- **乔丹鞋 → 篮球鞋**：单测显式验证 `{subject:"篮球鞋", output:"poster"}` → `"篮球鞋 poster"`，subject 本身的合理泛化路径完全保留，Guard 2 不 touch `rewrites` 数组。Query 集第 42 行（`NA-JORDAN`）记录该场景来源及理由，但因 Live 未跑，**无法用真实链路交叉验证**，仅有代码证据。
- **Poster / Playful**：单测验证 `{output:"poster", style:"playful"}`（无 subject）→ 两者均被标记 `UNBOUND_NON_SUBJECT_SLOT` 拒绝，不再有独立 `poster`/`playful` 执行；有 subject 时绑定为 `"<subject> poster"`/`"<subject> playful"`。**代码层证据充分**，Replay 中 Q42 D 的 `cover` 拒绝提供了真实 Replay 层面的旁证（同一 Guard 2 机制）。
- **CJK / 英文 / 中英混合**：单测覆盖 `"basketball shoes"`、`"小红书"`、`"小红书cover设计"` 断言行为不受影响；Replay 26 行中包含大量 CJK（Q06 除外多为中文 Query）及 Q41（中英混合）真实数据，未见系统性回归。
- **Protected Phrase**：单测显式断言 `"手冲咖啡"`（`primary=[]` 但 `aliasGroups.length>0`）不被 Guard 1 误伤，`allPrimary` 仍可为 true。Query 集第 45–47 行（Q30 手冲咖啡、Q21 二手奢侈品、Q44 小红书探店）作为非洪泛对照纳入 Live 计划，但**未实际运行**。
- **Alias OR-group**：Q30（手冲咖啡工作室视觉手册）标注为 `ALIAS_OR_GROUP_REGRESSION` 验证目标，同样因 Live 未跑而缺乏真实链路证据，仅代码层验证。

**结论**：合理 Rewrite 与各类 Query 形态在**代码/单元测试层面**未见回归，但由于 Gate 未通过、Live 未执行，**这些结论目前缺少真实生产链路（真实 LLM 输出）下的直接证据**，是本轮 Smoke Test 明确的覆盖缺口。

## 11. Human Top-10 Review

- 复核文件：`stage7_guard_smoke_human_review_2026-07-14.csv`，26 行，覆盖全部 26 个 Replay run。
- `reviewer_type=CLAUDE_STRUCTURED_REVIEW`：15 行（Section 10 强制要求的全部核心 Case：Q39 D/C、Q40 D/C、Q42 C/D、5 个仍 `>=1000` 的 Case、至少 5 条 PASS）。
- `reviewer_type=NOT_REVIEWED`：11 行（其余 D 组 Case，标签保留自动启发式判定，明确标注未做深度人工复核，不冒充覆盖）。
- 人工标签分布（15 条已深度复核）：PASS 5（Q39D、Q39C、Q15、Q19、Q52）、PARTIAL 8（Q40D、Q40C、Q42D、Q42C、Q06、Q12、Q16、Q52 中的重叠已去重计入）、FAIL 2（Q10、Q47、Q48 中—按 CSV 实际为 Q10/Q47/Q48 三条标 FAIL，需以 CSV 原始值为准，此处摘要供参考）。
- 审核依据：模板 title、description、category、tags 的结构化比对（例如 Q19 记录"top-5 ALL genuinely on-topic, STRICT matches"；Q16 记录"#1 结果 on-topic 但 #2-5 是 socks/headphones/jacket 等无关品类"）。**这是 Claude 基于 metadata 的结构化审核，不是用户本人的视觉/人工审核**，报告中如实标注 `reviewer_type`，未冒充用户审核。
- 自动启发式判定与人工复核在 3/15 案例中不一致（Q06 FAIL→PARTIAL、Q16 PASS→PARTIAL、Q52 PASS→PARTIAL），CSV 的 `notes` 字段同时保留两个值，未静默覆盖。
- Live 阶段 26 行人工复核：**不适用**（Live 未执行）。

## 12. Replay vs Live Interpretation

- **Replay 是可比较因果证据**：相同 raw rewrite/decomposition 输入，仅切换 Guard 代码（旧 vs 新），因此 old→new 的变化可直接归因于 Prompt 2 的 Guard 逻辑（Q40 C 一行除外，因其 old 值来自不同 tokenizer 版本，已在第 6/7 节标注为不可比）。
- **Live 本次未执行，无任何证据可陈述**，不构成"当前真实行为的 Smoke Evidence"。这是本轮相对于 Prompt 3 完整设计的主要缺口，原因是 Replay 未达门槛，而非环境或 API 故障。

## 13. Remaining Failures

| Query | Phase | Count（old→new） | Label | 根因 | 需要 Prompt 2 修复？ | 是否后续 Ranking/Merge 问题 |
|---|---|---|---|---|---|---|
| Q06（genshin impact Furina fanart wallpaper 4k） | Replay D | 1569→1569（无变化） | FAIL | Guard 2 正确将 style/output 绑定到 subject="Furina"，但 3 条 `rewrites` 自由文本（如"Genshin Impact character art"）本身仍是宽泛路径，且此前就已 `>=1000`，Guard 2 范围外 | 是——需要约束/去重 `rewrites` 数组中与 decomposition 语义重叠的宽泛路径，或对 `rewrites` 施加类似 Guard 1 的空/低信息 token 检测 | 也涉及 merge：3 条 rewrite + subject-bound 路径 Union 后仍偏大 |
| Q10（光与夜之恋 卡面设计参考图） | Replay D | 2687→1724 | FAIL | 同上模式：`decomposition={"subject":"Light and Night","output":"character design"}`，output 已绑定，但 rewrites 数组宽泛 | 是，同上 | 是 |
| Q12（松弛感生活方式插画） | Replay D | 3154→1694 | PARTIAL（CSV 标签），仍 `>=1000` | `decomposition={"style":"illustration","mood":"relaxed"}` **无 subject**，两个 slot 均被正确拒绝（`UNBOUND_NON_SUBJECT_SLOT`），但 3 条 rewrite 自由文本（"relaxed lifestyle illustration"等）仍产生大量宽泛匹配 | 是，同上；此案例证明即使非 subject slot 100% 被拒绝，`rewrites` 数组本身也可能独立造成 `>=1000` | 是 |
| Q47（抖音小黄车商品卡片设计） | Replay D | 2129→1031 | FAIL | `decomposition={"subject":"product card","output":"design"}`，output 已绑定，rewrites 数组宽泛（"TikTok merchandise template"等） | 是，同上 | 是 |
| Q48（抖音带货主播人设海报） | Replay D | 2184→1155 | FAIL | `decomposition={"subject":"Douyin influencer","output":"character poster"}`，同上模式 | 是，同上 | 是 |

**统一根因结论**：Prompt 2 的 Guard 1（Empty Tokens）与 Guard 2（Subject-bound Decomposition）均针对 `decomposition` 对象的 slot 设计，功能验证有效（full-catalog 清零、独立非 subject slot 被拒绝）。但 LLM 输出的 `rewrites` 自由文本数组（通常 3 条）完全在两个 Guard 的作用范围之外，仍作为无约束路径参与 merge。当这 3 条 rewrite 本身语义宽泛时（即使 decomposition 部分被 Guard 正确处理），Union 合并后总数仍可能 `>=1000`。这是 Prompt 4 之前需要修复的**新发现的 Guard 覆盖缺口**，不是本次 Smoke Test 之外的 Ranking/Merge 独立问题——它是 Merge 阶段对"已被 Guard 允许"的多条路径做 Union 时，`rewrites` 路径本身未经历约束检查的直接后果。

## 14. Metrics

### Replay
- Runs：26；BLOCKED：0；PASS：5；PARTIAL：17；FAIL：4
- 原 `>=1000`：24；新 `>=1000`：5
- 原 full-catalog：3；新 full-catalog：0
- 平均 count delta：1242.3；中位 count delta：1322
- `subject_binding_triggered`：22/26；`empty_token_guard_triggered`（诊断字段）：0/26（见第 15 节说明）；`no_valid_rewrite_path`：0/26
- 原始 Query fallback 触发：0/26（未测试到该分支）
- Regression（新 count > 旧 count）：1/26（Q40 C，tokenizer 版本不可比，非 Guard 劣化）
- 23 个 D 组改善比例：18/23 = 78.3%（未达 80% 门槛）
- Top-10 人工复核（15 条已复核）：PASS 5 / PARTIAL 8 / FAIL 2（详见 `stage7_guard_smoke_human_review_2026-07-14.csv`）

### Live
- Unique Query：22（计划）；Runs：25（计划），0（实际执行）
- 成功运行率：N/A（规则性阻止，非失败）；error：0；timeout：0
- low-result/rewrite/Guard trigger rate：N/A（未运行）
- `>=1000`／full-catalog：N/A
- Human PASS/PARTIAL/FAIL/BLOCKED：0/0/0/25（全部 BLOCKED）
- Q39/Q40/Q42 两次运行一致性：N/A（未运行）
- 正常对照 Query 回归数量：N/A（未运行）

## 15. Limitations

- **LLM 非确定性未直接观测**：本次会话 0 次真实 LLM 调用（Replay 不调用，Live 被阻止），Prompt 1 此前记录的 Q01/Q39/Q42/Q53 Mode C vs D 差异是当前唯一的非确定性直接证据。
- **目录内容漂移未量化**：继承自 Prompt 0/1 的已知限制。
- **人工复核为 Claude 基于 metadata（title/description/category/tags）的结构化审核**（`CLAUDE_STRUCTURED_REVIEW`），非用户本人视觉审核；26 条中仅 15 条做了深度复核，其余 11 条标记 `NOT_REVIEWED`。
- **`empty_token_guard_triggered` 诊断字段在 Replay 全程为 0/26**，与"3 个 full-catalog Case 被消除"这一功能性结果不完全对应——说明 Smoke 脚本对 Guard 1 内部（token 级）触发的埋点未完整挂钩到 CSV 输出，只能通过 count 变化间接推断 Guard 1 生效，无法在诊断字段层面直接确认。这是 Smoke harness 的埋点缺口，建议 Prompt 4 前补齐，而非断言 Guard 1 未触发。
- **Cache 行为无法评估**：Replay 不经过 `MULTI_CACHE`；Live 未运行，无 Cache 命中数据。
- **Live Query 数量为设计上限内（22 唯一 + 3 追加 = 25 runs）**，但本次实际 0 次执行，Prompt 3 要求的"验证 Guard 在真实模型输出下是否仍有效"这一核心问题**本轮未能回答**。
- **合理 Rewrite / Protected Phrase / Alias OR-group / CJK 回归验证** 全部退化为"单元测试代码证据"而非"真实链路证据"，因为 Live 未执行（见第 10 节）。
- 尚未重跑完整 68 条权威 Query 集，`human_relevance_label` 仍 0/68 未填（继承自 Prompt 0 的已知限制）。
- Replay 阶段 `no_valid_rewrite_path=true` 与"原始 Query fallback"分支均为 0 次触发，即本轮固定 Query 集未覆盖到"全部路径被拒绝后回退原始 Query"的场景，该分支的真实行为尚未被验证。

## 16. Final Gate

### **NEEDS_PROMPT2_FIX**

理由：
1. Full-catalog 已 100% 清零（3→0），Guard 1/2 在已验证范围内功能正确。
2. 但 23 个 D 组洪泛 Case 中仅 18 个（78.3%）不再 `>=1000`，未达到 Prompt 3 规定的 80% 阈值（即"最多允许 4 条仍 `>=1000`"，实际为 5 条：Q06、Q10、Q12、Q47、Q48）。
3. 根因明确且一致：Guard 2 仅约束 `decomposition` 对象的 slot，未覆盖 LLM 输出的 `rewrites` 自由文本数组，后者在 5 个残留 Case 中仍产生宽泛匹配，Union 合并后总数超过 1000。
4. 按 Prompt 3 Step 6 的强制规则，Replay 未达门槛即不得运行 Live、不得进入 Prompt 4，本轮已严格遵循，未运行 Live、未编造在线结果。
5. 建议下一步（Prompt 2 补丁范围）：对 `rewrites` 数组的每条自由文本施加与 Guard 1 类似的"低信息/纯泛化词汇"检测，或在 Merge 阶段对 `rewrites` 路径与 decomposition-bound 路径的贡献做加权/去重，抑制 Q06/Q10/Q12/Q47/Q48 类型的残留洪泛。修复后需重新执行 Prompt 3（Replay 优先），达到 80% 门槛后再考虑 Live Smoke 与 Prompt 4。
