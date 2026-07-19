# Curify 搜索相关性优化工作报告

**报告周期**：2026-07-18 ～ 2026-07-20
**提交对象**：Jay（管理层评审）
**报告性质**：只读汇总。本报告不涉及任何代码修改、配置修改、评测重跑或服务启动，全部数据取自已冻结的设计文档、代码审计记录与评测归档。

---

## 1. 执行摘要

- 本轮工作严格按照上次会议的决定执行：以 Production main 为唯一基线（下称 **V0**），从 V0 新建干净分支做内部修复（下称 **候选版本**），旧候选分支继续冻结不再修补，未新增逐项 Feature Flag，未接入 Hybrid Search / HyperResearch。
- 共完成三轮工作：**第一轮内部修复**（统一相关性评分、subject binding、phrase protection、广谱噪声根因调查）、**第二轮回归根因调查**（对第一轮产生的 50 条回归查询做候选级证据分析）、**第三轮真实根因修复**（模板 sibling 独立评分 + 多词查询上下文覆盖）。
- 专项改善明确可见：**PASS 数量由 26 条增至 36 条（+10，+38.5%）**；广谱噪声查询由 151 条降至 124 条（-17.9%）；结果泛滥（flooding）由 23 条降为 0（-100%）；全目录级泛滥由 9 条降为 0（-100%）；第一轮遗留的 50 条回归查询中有 17 条（约 34%）被第三轮修复。
- 但在最核心、覆盖率 100% 的 326 条 Easy Query 评测集上，候选版本相对 V0 **未形成整体净改善**：FAIL 由 200 条增至 206 条，零结果查询由 17 条增至 23 条，回归查询数（47）多于改善查询数（44），三项统计检验（McNemar、paired bootstrap、Wilcoxon）均未达到统计显著。
- 会议要求的实现、评测和根因调查工作基本完成，但**没有产出一个整体明显优于 Production 的可上线版本**。
- 结论：**当前候选版本（V2-R3）不建议替换 Production**，Production 继续保持 V0 不变。本轮工作可以作为阶段性工程成果提交，但不能作为上线 Candidate 提交。

---

## 2. 背景与会议目标

上次会议对搜索相关性问题给出了明确的书面反馈和会议决定，核心包括：以 Production main 为唯一基线重新开发；不要求逐项 Feature Flag；用一套统一、轻量、确定性的文本相关性评分取代原本三套独立规则；对高频广谱噪声模板（如器官健康信息图、MBTI 角色卡等在无关查询中反复出现）做根因调查而非简单拉黑名单；把 LLM rewriter、multi-path retrieval 等既有功能的行为级验证列为正式上线门禁；当前阶段不接入 Hybrid Search；只有评测结果明显优于 Production 才允许上线。

本报告即是对这些会议要求的执行情况、实际完成的代码与评测工作、以及最终 Go/No-Go 结论的完整汇报。

---

## 3. 会议要求完成情况

| # | 会议要求 | 执行动作 | 完成状态 | 证据/结果 |
|---|---|---|---|---|
| 1 | 冻结旧 Candidate，不继续修旧候选分支 | 旧候选分支 `baobao/search-relevance-phrase-alias-2026-07-09` 保持冻结，未新增提交、未合并、未 cherry-pick | 已完成 | 会后设计文档第 6 节 |
| 2 | 以 Production main 作为唯一 V0 基线 | 全程以 Production main（SHA `05e5f2d3...c3673`）作为对照基线，未修改 | 已完成 | `00_PRODUCTION_BASELINE_MANIFEST.json` |
| 3 | 从 Production 建立干净的新实验分支 | 从 V0 新建 `baobao/search-relevance-prod-main-v2-2026-07-19`（第一轮），后续两轮均基于同一父 SHA 建立独立分支 | 已完成 | `01_WORKTREE_AND_BRANCH_SETUP.md` |
| 4 | Rewrite 不得清空原始非空结果 | 实现 original 结果存在性保底不变量（`selectFinalCandidates`），4 条历史净负面 Case 在 V0 上均未复现为零结果，仍做防御性实现 | 已完成 | `07_V0_TARGET_CASE_RECONFIRMATION.csv` |
| 5 | 安全合并 original 和 rewrite 候选池 | 按稳定 ID 去重合并，保留命中来源，禁止单一路径靠数量主导排序 | 已完成 | `08_RELEVANCE_SCORER_DESIGN.md` |
| 6 | subject binding 与 phrase protection | 基于实证案例的小型保护词表（coffee cup、black friday，均有 V0 直接证据）；rewrite 侧 subject binding 经核实为 V0 已基本满足，未重复实现 | 已完成 | `33_GO_NO_GO_RECOMMENDATION_ZH.md` |
| 7 | 方向 3、4、5 使用统一、轻量、确定性、可解释的相关性评分 | 实现统一评分器 `lib/relevanceScorer.ts` + `lib/relevanceScorerConfig.ts`，无新增 LLM 调用、无学习型 reranker，权重集中配置并冻结 | 已完成但结果未达上线标准 | 第一轮评分器在 326 集合上产生净回归，第三轮做了修正但仍未整体转正 |
| 8 | exact phrase / whole token / substring 分层 | 评分维度中体现优先级差异（`exact_phrase` / `whole_token` / `substring_penalty`） | 已完成 | `10_ISSUE_3_4_5_SCORING_MAPPING.md` |
| 9 | 控制 rewrite path 和候选质量 | 单路径候选数上限、候选池总上限、模板族数量控制（Family Saturation）均已实现 | 已完成 | `10_ISSUE_3_4_5_SCORING_MAPPING.md` |
| 10 | 调查广谱噪声（器官健康信息图、MBTI 卡片等）为何被大量匹配 | 完成 Query→Result Trace 级根因调查，定位到字段级证据过宽（模板描述文本被等权匹配） | 已完成 | `15_BROAD_TEMPLATE_ROOT_CAUSE_ANALYSIS.md` |
| 11 | 提供短期与长期噪声治理方向 | 未使用人工降权名单；长期方案落地为 `templateTitleCategoryBlob` 字段拆分打分 + Template Family Saturation | 已完成 | 同上 |
| 12 | 不要求每项独立 Feature Flag | 未构建任何逐项运行时开关，内部消融通过独立 commit/临时配置完成 | 已完成 | 会后设计文档第 15 节 |
| 13 | 使用独立分支、独立 commit 与 Production 对比 | 三轮均使用独立分支与独立 commit，整体与 V0 做对比评测 | 已完成 | 各轮 RUN_LOG |
| 14 | 验证 LLM rewriter、Rewrite Guard、multi-path、decomposition、phrase protection、subject binding 和页面构建 | 上述项目均完成行为级验证并 PASS；L2 层级内容与多段落展示未在代码中定位到对应概念，完整 Playwright 端到端点击模拟因时间限制未执行，改以代码级证据替代 | 部分完成 | 第 7 节工程验证 |
| 15 | V2 不加入 Hybrid Search / HyperResearch | 全程未接入任何 Hybrid / HyperResearch 相关代码 | 已完成 | 会后设计文档第 17 节 |
| 16 | V0 与 Candidate 使用一致的采集和评测方法 | 两侧均为真实 `next start` 生产构建 + 真实 HTTP 请求采集（`collector.mjs`）+ 真实 LLM 裁判（`judge.mjs`，rubric-v1.1），同一查询集、同一模型、同一 Prompt、同一阈值 | 已完成 | 各轮 STATISTICAL_COMPARISON |
| 17 | 使用 PASS/PARTIAL/FAIL、Top-5、zero/low、rewrite、noise、flooding 等指标 | 全部报告均采用上述指标体系，未使用 Recall@K/MRR/nDCG 作为强制指标 | 已完成 | 各轮评测报告 |
| 18 | 只有明显优于 Production 才允许上线 | 三轮均严格套用此门禁做 Go/No-Go 判定，最终结论为不满足门禁、不建议上线 | 已完成 | 第 13 节 Go/No-Go 结论 |

**核心结论（不得混淆）**：会议要求的实现、评测、根因调查和 Go/No-Go 操作**基本完成**，但**没有获得一个整体显著优于 Production 的上线版本**。这不是"全部要求成功完成"，而是"该做的工作和该走的流程都做了，产品结果尚未达标"。

---

## 4. 实验版本与基线

为便于管理层理解，全文使用以下自然表述，不使用内部阶段编号：

- **V0（Production 基线）**：当前线上生产版本，SHA `05e5f2d332778ac52c712dd2429f4a8f4e7c3673`，全程未修改。
- **第一轮实验（内部代号 V2-R1）**：从 V0 新建干净分支，完成统一评分器、subject binding、phrase protection、广谱噪声根因调查等全部第一轮设计目标，SHA `32f6282a240edfa87edae5a0ba5308aecf462466`，已冻结。
- **根因调查阶段（内部代号 V2-R2）**：不产出新代码，仅对第一轮遗留的 50 条回归查询做候选级证据分析，确认真实根因。
- **第二轮修复（内部代号 V2-R3）**：基于第一轮同一父 SHA 新建分支，实现两个真实根因修复机制，SHA `a811f06f8838e330e08caa4d3c4952d6ab10554d`，已冻结。

三者关系：第一轮解决了一批经实证确认的具体问题（子串碰撞、广谱噪声压制等），但在最大评测集上引入了净回归；根因调查阶段用真实候选级证据证明"稀释是主因"的最初猜测并不成立，避免了在错误方向上继续加固修补；第二轮修复针对被证实的真实机制做了修正，在定向评测中通过全部门禁，但在完整评测集上仍未转为整体净改善。

---

## 5. 已完成的实现

### 5.1 Original 与 Rewrite 候选安全合并

Original 候选池与各类 Rewrite/Decomposition 候选池按稳定结果 ID 去重合并，保留每条结果的命中来源（original / strict / relaxed / rewrite / decomposition / multi-path），任一路径都不能单纯凭结果数量主导最终排序。4 条历史"改写后清空结果"的净负面案例（烘焙包装、咖啡馆菜单、饮料瓶、课程表）在当前 V0 上均未复现为零结果，但仍在候选版本中实现了防御性的存在性保底机制。

### 5.2 Subject Binding 与 Phrase Protection

保护词表基于真实案例构建，目前包含 `coffee cup`、`black friday` 两条，均有 V0 直接证据支撑，未按早期设计草稿机械扩展成人工词典。Rewrite 侧的 subject binding 经实测评估，V0 已基本满足要求，未重复实现。

### 5.3 统一相关性评分

第一轮实现了统一评分器 `relevanceScorer.ts` + `relevanceScorerConfig.ts`，将原本三套独立规则（strict/relaxed 二元门禁、短语/整词/子串优先级、rewrite 候选数控制）统一为一套确定性、基于文本特征的评分机制，权重集中配置并冻结存档，全程无新增 LLM 调用、无学习型 reranker。这套评分器成功修复了多个经实证确认的具体问题（如 coffee cup → World Cup 子串碰撞、black friday banner → Marvel Black Widow 碰撞），但在 326 条评测集的全量运行中，也暴露出一个新问题：移除原有的二元 strict 门禁后，一批此前"干净"的简单实物名词类查询（如手办、娃娃、泰迪熊、盲盒）被允许混入较弱的 relaxed 候选，稀释了原本纯净的结果集。

### 5.4 Template Sibling 独立评分

根因调查发现，326 集合回归中 44%（22/50）的问题并非来自 relaxed 候选稀释，而是**模板级证据被机械复制**：一旦某个模板的标题/分类/标签/描述文本命中查询，该模板下的**全部 sibling（同模板下的其他素材）都会被赋予相同的统一高分**，而不管每个 sibling 本身是否真的与查询相关。第二轮修复的核心机制是：为每个 sibling 补充"自身标题、标签、文本"的独立证据（若 sibling 自身内容确实命中则维持高分，若仅是模板整体命中而 sibling 自身毫无关联则降低证据权重）。这一修改**只影响评分，不影响候选池**——original 候选的"存在"保底不变量完全未被触碰，只是"存在"不再自动等同于"必须进入 Top-5"。

### 5.5 多词 Query 上下文覆盖

根因调查还发现，326 集合回归中 36%（18/50）的问题来自**词义歧义碰撞**：判断"查询主体是否被覆盖"的逻辑此前只检查查询中最长的单个 token，导致像 `banner` 命中漫威角色 `Bruce Banner`、`tag` 命中元数据标签而非服装标签这类命中了错误义项的候选，也能拿到与真实匹配同等的高分。第二轮修复引入了"多词覆盖率"机制：多词查询要求查询中多数（非全部）核心词在候选自身文本中出现；仅命中单个孤立词、且无短语/多信号佐证的候选，其评分会被设置上限。该机制对中英文使用统一原则（中文按 bigram 拆分单元，英文按空格分词单元），不使用人工歧义词黑名单，不增加 LLM 调用。

### 5.6 广谱噪声与 Flooding 治理

对器官健康信息图、MBTI 角色卡等广谱模板做了 Query→Result Trace 级根因调查，确认问题出在模板描述文本被等权匹配、字段证据过宽。治理方式是将标题/分类字段与宽泛的标签/描述文本拆分打分（`templateTitleCategoryBlob`），而非建立人工降权名单——6 个调查案例中 4 个（吉祥物、贴纸等）经此机制明确改善，2 个（元素周期表、logo）诊断为目录内容缺口或需要产品判断的边界案例，均未使用人工降权。长期机制（模板族饱和度控制 Family Saturation）已实现并在评测中确认持续压制结果泛滥（flooding）。

---

## 6. 回归根因调查（第一轮遗留 50 条回归查询）

第一轮实现上线后，在 326 集合上产生了 50 条净回归查询。根因调查阶段对这 50 条查询逐一做了候选级证据分析（而非仅看聚合标签/分数），结论明确推翻了"weak relaxed 候选稀释是主因"的最初假设：

| 根因类别 | 数量 | 占比 | 说明 |
|---|---:|---:|---|
| Original/模板 sibling 过度提升（Original Template Overpromotion） | 22 | 44% | 模板级证据被机械复制到全部 sibling，与 relaxed 准入机制无关 |
| 词义碰撞（Sense Collision） | 18 | 36% | 候选已远高于任何合理准入门槛，问题在"覆盖了错误义项"而非"门槛太松" |
| 目录缺口 + 保底机制（Catalog Gap + Never-zero） | 5 | 10% | 目录中确实不存在更好候选，属内容缺口而非排序缺陷 |
| Weak Relaxed 候选稀释 | 5 | 10% | 唯一真正可被"松紧门禁"调整触及的部分，且只能部分修复 |

这一发现的工程价值在于：如果按最初假设强行收紧或重建一个 strict/relaxed 门禁，最多只能触及这 10% 的问题，反而会重新破坏第一轮已验证有效的改善（如 coffee cup、吉祥物等）。团队据此**没有强行实施错误方向的 Gate**，转而对真正的两个主因（模板证据复制、词义覆盖不足）做了针对性修复，避免了进一步误修和过拟合。

---

## 7. 工程验证

第二轮修复完成后，进行了完整的工程门禁检查，结果如下：

| 检查项 | 结果 |
|---|---|
| TypeScript 类型检查 | PASS（0 错误） |
| 单元测试 | 143/143 PASS |
| Production build | PASS |
| Rewrite Guard | PASS |
| Multi-path retrieval | PASS |
| Decomposition | PASS |
| Phrase protection | PASS |
| Subject binding | PASS（已核实 V0 基线本身满足要求） |
| 技术性失败 | 0 |
| L2 层级内容 / 多段落展示 | 未发现可靠专项证据 —— 代码库中未定位到对应概念，本轮修改也未触及任何可能相关代码，如实标注为 UNKNOWN，非猜测性 PASS |
| 完整 Playwright 端到端点击模拟 | 未完全闭环 —— 受时间限制未执行真实浏览器点击/Generate/Remix 模拟，改用代码级 diff（确认交互组件文件字节级未变）与 RSC payload 数据验证作为替代证据 |

以上结果与最初计划完全一致：**该验证的功能都已按行为级标准验证通过，唯一的缺口是 L2/多段落这两项无法定位对应实现、以及端到端点击模拟未完整跑完**，均已如实标注，未夸大为全部 PASS。

---

## 8. 定向评测结果

第二轮修复完成后，先对一个 63 条的定向样本集（14 条校准集 + 37 条留出集 + 8 条既有改善保护集 + 4 条 rewrite 不变量集）做了定向门禁检查，用于判断该修复方向是否值得进入完整 326 条评测：

- 校准集（calibration，14 条）：平均分由 19.3 升至 30.3，4 次标签升级，0 次降级；
- 留出集（holdout，37 条）：平均分由 12.4 升至 14.5，5 次标签升级，5 次标签降级；
- 历史回归修复：第一轮 50 条回归查询中（校准+留出子集内），9 条修复、5 条新增回归；
- 既有改善保护：8 条历史已验证改善案例（coffee cup、吉祥物、贴纸等），标签层面 8/8 保留或提升，无一降级；
- 广谱噪声改善保留（吉祥物进一步改善，元素周期表/横幅未恶化）；
- Flooding 改善保留，未发现新的全目录级泛滥；
- 零结果查询在该定向集合中无新增（V2-R1 与 V2-R3 均为 5 条，且是完全相同的 5 条查询）；
- 定向门禁全部 20 项条件均通过。

**必须明确说明**：定向门禁通过（`V2_R3_TARGETED_FIX_COMPLETE`）**仅代表这一修复方向值得进入完整 326 条评测**，不代表可以上线，也不代表已经通过了替换 Production 所需的整体门禁。63 条定向样本是围绕两个已知根因刻意挑选的验证集，并非对 326 条查询库的无偏随机抽样。

---

## 9. 完整 326 对比结果

完整 326 条 Easy Query 评测集是覆盖率 100%、无偏采样的核心评测数据，是判断能否替换 Production 的最终依据。

| 指标 | V0 Production | 第一轮实验（V2-R1） | 第二轮修复（V2-R3） | V0→V2-R3 变化 |
|---|---:|---:|---:|---:|
| PASS | 26 | 24 | 36 | +10（7.98%→11.04%，+3.07pp，相对增长约 38.5%） |
| PARTIAL | 94 | 85 | 80 | -14 |
| FAIL | 200 | 210 | 206 | +6（61.35%→63.19%，+1.84pp，变差） |
| UNJUDGABLE | 6 | 7 | 4 | -2 |
| Zero-result | 17 | 19 | 23 | +6（5.21%→7.06%，+1.84pp，变差） |
| Low-result（1-4条） | 15 | 11 | 13 | -2 |
| Mean score | 15.89 | 15.76 | 17.05 | +1.16 |
| Median score | 0.0 | 0.0 | 0.0 | 0 |

（标签总和核对：V0 = 26+94+200+6 = 326；V2-R1 = 24+85+210+7 = 326；V2-R3 = 36+80+206+4 = 326，三侧均无缺行、无重复、无技术性采集失败。）

V0→V2-R3 逐查询对比：改善 44 条，回归 47 条，未变 235 条，标签升级 44 次，标签降级 47 次。

统计检验：McNemar（PASS 转移）χ²=3.12，p≈0.078，未达显著；配对 bootstrap 均分差 +1.28（n=316 可判定配对，95% CI [-1.33, +4.04]，区间跨越 0）；Wilcoxon 符号秩检验 z=-0.37，p≈0.71，未达显著。

**需要特别说明的口径差异**：表格中的均分变化（15.89→17.05，简单差值 +1.16）与统计检验中配对 bootstrap 的均分差（+1.28）不是同一个数字，也不矛盾——前者是两个版本各自 326 条的聚合均分之差，后者是**逐条配对**后仅取两侧均可判定的 316 对样本计算的配对差值，分母和计算口径不同。两个数字都是真实数据，未混用、未择优选择。

**结论**：三项统计检验均未达到常规显著性水平，且回归查询数（47）多于改善查询数（44），零结果查询净增加 6 条——**不能因为 PASS 数量上升就忽略 FAIL 和零结果同步恶化的事实**。

---

## 10. 实际提升

以下是本轮工作中经得起数据检验的专项改善，应与第 11 节的未达标项分开看待：

- **PASS 提升**：26 条 → 36 条，净增 10 条，相对增长约 38.5%，PASS 率提升约 3.07 个百分点。
- **广谱噪声查询（Broad-noise）**：151 条 → 124 条，减少 27 条，降幅约 17.9%。
- **结果泛滥（Flooding，单查询返回 ≥200 条）**：23 条 → 0 条，降幅 100%。
- **全目录级泛滥（Full-catalog flooding，≥300 条）**：9 条 → 0 条，降幅 100%。
- **第一轮遗留回归修复**：第一轮产生的 50 条回归查询中，第二轮修复了 17 条，约占 34%。
- **相比第一轮实验的改善**：PASS 由 24 条升至 36 条（+12）；FAIL 由 210 条降至 206 条（改善 4 条）；但零结果由 19 条升至 23 条（恶化 4 条）。

**准确总结：第二轮修复（V2-R3）明显优于第一轮实验（V2-R1），但仍未整体优于 V0 Production。** 这两句话都成立，且必须同时呈现，不能只强调前者。

---

## 11. 未达到上线标准的指标

- **FAIL 率**：200→206，+6 条，61.35%→63.19%，方向变差，未通过"FAIL 率不得上升"门禁。
- **零结果率**：17→23，+6 条，5.21%→7.06%，方向变差，未通过"零结果不得高于 V0"门禁。其中 5 条查询（`online store banner`、`积分卡`、`证书`、`microscope`、`算盘`）是本轮完整 326 评测中新发现的零结果案例，`算盘` 此前已被识别为已知目录缺口，其余 4 条不在此前任何定向样本或已知例外清单中——说明 63 条定向样本无法覆盖全部风险面，完整 326 评测是必要的、不可省略的一步。
- **改善/回归查询数**：改善 44 条 < 回归 47 条，未通过"改善数不得少于回归数"门禁。
- **统计显著性**：McNemar p≈0.078、配对 bootstrap 置信区间包含 0、Wilcoxon p≈0.71，三项检验均未达到 p<0.05 的常规显著性水平。
- **整体净提升**：完整 326 门禁 15 项条件中，4 项明确未通过（FAIL 率、零结果率、改善数<回归数、整体净改善不明确），1 项为"相对第一轮明显更好但相对 V0 混合"（因零结果同时恶化）。

综合以上，完整 326 评测**未形成清晰、可信的整体净提升**，这是本轮工作最终不建议上线的直接依据。

---

## 12. 旧 328 与其他验证补充

作为补充证据，第一轮实验还在一个更早的 328 条旧种子查询库上做了独立补跑：

| 指标 | V0 | 第一轮实验（V2-R1） |
|---|---:|---:|
| PASS | 56 | 60 |
| PARTIAL | 79 | 79 |
| FAIL | 182 | 178 |
| UNJUDGABLE | 11 | 11 |
| Zero-result | 27 | 29 |

配对结果：改善 24 条，回归 16 条。均分和 PASS/FAIL 率有小幅、统计上可检测的正向变化（配对 bootstrap 置信区间不含零，Wilcoxon p=0.007），但**零结果率依然从 27 条升至 29 条**，与 326 集合上诊断出的核心回归模式（简单实物名词类查询被稀释）完全一致。标签变化的 McNemar 检验本身不显著（p=0.42）。

**这一补充结果不能用来推翻 326 集合的主结论**：326 是覆盖率更高、更具代表性的核心评测集，且旧 328 上表现出的"零结果恶化"与 326 上的核心失败模式同源，是对同一根因的独立佐证，而非反证。主结论仍以完整 326 评测为准。

---

## 13. 为什么停止 Hard68 / 旧328 / 12条P0 的后续验证

第一轮实验（V2-R1）已经完整跑完 Hard68（68 条复杂查询回归集）、旧 328 条种子库、以及 12 条 P0 页面回归案例，三者结果均已记录在案。第二轮修复（V2-R3）在完成定向门禁（63 条样本）后，按预先冻结的停止规则，优先运行了覆盖率最高、最具代表性的完整 326 条评测；**该评测门禁未通过后，按规则立即停止，未继续运行 Hard68、旧 328 或 12 条 P0**。

这是一次正确的 Go/No-Go 停止操作，不是遗漏：继续在一个已经未通过核心门禁的版本上消耗评测资源，既不产生新的决策价值，也存在把一个未过关的版本"包装"成看似更全面验证过的版本的风险。因此，本报告中第二轮修复（V2-R3）**没有** Hard68、旧 328、P0-12 的独立评测数据，这一点在此明确说明，避免误读。

---

## 14. Go/No-Go 结论

**第二轮修复（V2-R3）当前状态：**

- 定向门禁（63 条样本，20 项条件）：**通过**
- 完整 326 门禁（15 项条件）：**未通过**（4 项明确失败，1 项混合）
- 是否允许替换 Production：**不允许**
- 是否允许合并到 main：**不允许**
- 是否允许部署：**不允许**
- Production 当前版本：**继续保持 V0 不变**

正式状态标记：

```
V2_R3_TARGETED_FIX_COMPLETE
NOT_READY_TO_REPLACE_PRODUCTION
```

不使用"优化成功""全面提升""已达到上线标准""可以替换 Production""建议立即 merge"等表述——这些均不准确。准确的表述是：**专项改善明确，但整体尚未达到替换 Production 的标准。**

---

## 15. 当前可交付成果

本轮工作可以作为**阶段性工程成果**提交给管理层审阅，交付内容包括：

1. Production 基线确认（V0 SHA 锁定、代码审计）；
2. 会后方案设计文档（对齐会议决定的完整技术方案）；
3. 第一轮实现（统一评分器、subject binding、phrase protection、广谱噪声治理）；
4. 完整评测（326 + 旧 328 + Hard68 + 12 条 P0，第一轮）；
5. 50 条回归查询的候选级根因调查（推翻"weak relaxed 稀释"假设）；
6. 第二轮真实根因修复（模板 sibling 独立评分 + 多词覆盖机制）；
7. 工程验证（TypeScript、143 项单元测试、build、行为级功能回归）；
8. 定向评测（63 条样本，20 项门禁全部通过）；
9. 完整 326 复测（15 项门禁，含 3 项统计检验）；
10. 统计分析（McNemar / paired bootstrap / Wilcoxon）；
11. 两轮 Go/No-Go 正式结论；
12. 代码冻结（V2-R1、V2-R3 均已冻结分支，未删除、未 rebase）；
13. 全部报告与原始评测数据归档（`b8a0eee...` commit）。

同时需要明确：**本次成果可以提交给老板审阅，但不能作为上线 Candidate 提交，不能声称最终目标（产出一个明显优于 Production 的版本）已经完成**。这个最终目标仍未达成。

---

## 16. 尚未完成与后续建议

基于当前证据，建议下一阶段优先处理以下问题，不建议在此基础上展开新的大项目：

1. **V2-R3 新增的零结果与候选流失问题**：`online store banner`、`积分卡`、`证书`、`microscope` 四条查询从有结果（甚至过多结果）逐步流失到零结果，需要专项排查，确认是否违反了"原始非空结果不得被清空"的既定不变量在这些具体查询上的实际表现。
2. **如何在不恢复广谱噪声和 Flooding 的前提下保留合格候选**：即避免"矫枉过正"，重新引入已被证明有害的旧问题。
3. **继续将目录内容缺口（Catalog Gap）与排序缺陷分开处理**：泰迪熊、算盘等案例已确认是目录内容本身缺失，不应继续在排序算法上投入。
4. **对新增/恶化案例做专项分析**：`online store banner`、积分卡、证书、microscope、算盘，逐条确认是评分器缺陷还是目录缺口。
5. **L2 层级内容与多段落展示行为**尚未完全闭环，建议明确其在当前代码结构中的实际对应位置，并补充完整的 Playwright 端到端点击验证。
6. **继续优化前，应先建立新的固定校准集/留出集**，不基于完整 326 评测结果逐条过拟合调参——这正是本轮避免第一轮错误路径重演的关键纪律，应在下一轮延续。

本报告不建议直接上线任何当前版本。

---

## 17. 版本、分支与归档信息

| 项目 | 值 |
|---|---|
| V0 Production SHA | `05e5f2d332778ac52c712dd2429f4a8f4e7c3673` |
| 第一轮实验（V2-R1）冻结 SHA | `32f6282a240edfa87edae5a0ba5308aecf462466` |
| 第二轮修复（V2-R3）冻结 SHA | `a811f06f8838e330e08caa4d3c4952d6ab10554d` |
| Artifact 最新归档 commit | `b8a0eee0167928ae91fb0d301be365dc572b2dc8` |
| V0 只读参照 worktree | `curify-frontend-v0-baseline-2026-07-19` |
| 第一轮实验只读参照 worktree | `curify-frontend-search-v2-2026-07-19` |
| 第二轮修复只读参照 worktree | `curify-frontend-search-v2-r3-2026-07-19` |
| 归档 worktree | `visual-search-adhoc-v2-artifacts-2026-07-19` |

所有版本均未 push、未创建 PR、未 merge、未部署，均以本地分支和归档 commit 的形式保留，可完全追溯、可回滚。

---

## 18. 附录：主要文件索引

**会后设计**
- `easy-query-search-solution-design-post-meeting/EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-18_POST_MEETING_ZH.md`
- `easy-query-search-solution-design-post-meeting/EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-18_CHANGELOG.md`

**第一轮实验（V2-R1）**
- `search-relevance-prod-main-v2/08_RELEVANCE_SCORER_DESIGN.md`（评分器设计）
- `search-relevance-prod-main-v2/15_BROAD_TEMPLATE_ROOT_CAUSE_ANALYSIS.md`（广谱噪声根因）
- `search-relevance-prod-main-v2/16_BROAD_NOISE_BEFORE_AFTER_SUMMARY.csv`
- `search-relevance-prod-main-v2/31_STATISTICAL_COMPARISON.md`（Easy326/Hard68/P0-12 统计对比）
- `search-relevance-prod-main-v2/33_GO_NO_GO_RECOMMENDATION_ZH.md`（第一轮 Go/No-Go）
- `search-relevance-prod-main-v2/v2-r1-328-completion/04_OLD328_STATISTICAL_COMPARISON.md`
- `search-relevance-prod-main-v2/v2-r1-328-completion/05_V2_R1_STATUS_AFTER_328_ZH.md`

**回归根因调查（V2-R2）**
- `search-relevance-prod-main-v2/v2-r2-relaxed-gate/01_RELAXED_REGRESSION_ROOT_CAUSE.md`
- `search-relevance-prod-main-v2/v2-r2-relaxed-gate/02_REGRESSED_QUERY_RELAXED_TRACE.csv`

**第二轮修复（V2-R3）**
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/01_V2_R3_ROOT_CAUSE_REVALIDATION.md`
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/03_V2_R3_CASE_SPLIT.csv`
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/05_V2_R3_MINIMAL_FIX_DESIGN.md`
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/08_V2_R3_TARGETED_GATE_RESULT.md`
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/10_V2_R3_IMPLEMENTATION_SUMMARY.md`
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/11_V2_R3_ENGINEERING_CHECKS.md`
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/13_V2_R3_EASY326_RESULTS.csv`
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/14_V0_V2_R1_V2_R3_EASY326_PAIRED.csv`
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/15_V2_R3_EASY326_STATISTICAL_COMPARISON.md`
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/16_V2_R3_EASY326_GATE_RESULT.md`
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/17_V2_R3_EASY326_RUN_MANIFEST.json`
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/18_V2_R3_FREEZE_AND_ARCHIVE_MANIFEST.json`
- `search-relevance-prod-main-v2/v2-r3-root-cause-fix/FULL326_RUN_LOG.md`

以上文件均归档于 `visual-search-adhoc-v2-artifacts-2026-07-19` worktree，对应 commit `b8a0eee0167928ae91fb0d301be365dc572b2dc8`。
