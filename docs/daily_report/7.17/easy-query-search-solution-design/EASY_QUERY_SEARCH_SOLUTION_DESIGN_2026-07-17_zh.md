# Curify 搜索问题 · 解决方案 Design（面向今日评审）

日期：2026-07-17　性质：**只读分析 + 设计文档，本次任务未修改任何生产代码，未提交 commit，未 push，未创建 PR，未重跑全量326/328查询测试**。所有结论均可追溯到本目录 `RUN_LOG.md` 中列出的源文件；无法从现有材料证明的内容，一律标注 **UNKNOWN**，不做推测性填充。

---

## Executive Summary（先看这一段）

1. **候选分支（`baobao/search-relevance-phrase-alias-2026-07-09`）不是净改善。** 在新的326条 Benchmark v2 上：PASS 率从生产的23.9%只涨到25.2%（统计上**不显著**，McNemar p=0.69），连续分数上有小幅、勉强显著的提升（Wilcoxon p=0.018），但**零结果率从2.45%涨到10.43%，翻了4.25倍**。同样的"零结果暴涨"模式在更早的328条旧种子库对比中也出现过一次（3.66%→14.33%，约3.9倍）——**这是被两次独立评测重复验证的回归，不是偶然噪声**。一句话：候选分支是"拿零结果问题换了一点点分数提升"，这笔交易不划算，**不建议在当前状态下合并**。
2. **零结果回归是当前最大的风险**，其次是"改写后结果数爆炸但相关性不涨"（虚假成功，196次触发改写中53次/27.0%属于此类）。这两个问题都有明确、范围可控的修复点（见方案A）。
3. 四类根因（排序问题31.6%、查询理解/改写问题29.1%、目录缺口27.5%、词义歧义11.9%，分母是244条FAIL+PARTIAL记录）**必须理解为"Top-5综合失败诊断"，不是可以精确拆分的工程指标**——因为评测方法学从未采集过Top-5之后的结果，无法把"排序"和"召回"干净地分开。31.6%这个数字是真实可追溯的，但它的精确含义有边界，详见第2节。
4. 本文档区分**两个不同的查询库**：旧的328条种子库（7.14/7.15产出，用于7.16的production-vs-optimized-comparison-v1）和新的326条 Benchmark v2（7.16产出，用于本次manager-follow-up-analysis的核心对比）。**两者从未被混用，本文档中所有数字都标注了具体来源。**
5. 提出两套方案：**方案A（不含Hybrid的内部修复）**优先修4个已定位的具体bug和2个可配置的低垂果实，风险低、可回退、可用现有326库直接回归验证；**方案B（含Hybrid Search）**在方案A验证通过之后叠加，作为无法通过内部优化解决的"目录真实缺口"（约34/67个零结果查询）的兜底方案。**两者都是设计建议，代码、Hybrid Search 均未实现，Google Search API 也未在代码中接入**（现有 `@google/genai` 只用于图片生成，不是外部图片搜索）。
6. 推荐实施顺序：**先方案A独立落地评测，达标后再启动方案B开发**，不建议管理层提议的"直接跳到含Hybrid的最终版本"。

---

## 1. 数据身份确认（做区分，不做假设）

| 数据集 | 文件 | 条数 | 用途 |
|---|---|---|---|
| **旧 328 条种子库** | `docs/daily_report/7.15/easy-query-production-baseline-v1/query_input/easy_queries_cleaned_300_plus_2026-07-14.csv` | 328 | 用于7.15生产基线 + 7.16 `easy-query-production-vs-optimized-comparison-v1`（Run A/B），**与本节其余内容是两套不同的评测**，本文档第2-6节的核心数字均不引用这套对比，仅在第7节"历史交叉验证"中引用其结论 |
| **新 326 条 Benchmark v2** | `docs/daily_report/7.16/easy-query-bank-v3/easy_query_bank_v2_2026-07-16.csv` | 326 | 4个场景（Creative/Cultural/Merch、Brand/Business、Marketing/Ecommerce、Education，各约82/82/82/80条），中英文各163条，完全均衡。本文档第2-6节全部数字来自这套查询库 |
| **68条 Hard Query 回归集** | `docs/daily_report/7.14/search-relevance-stage7-rerun/full-68-rerun-v2/hard_queries_baseline_locked_68_2026-07-14.csv` | 68 | 已有的困难查询回归基线，本次任务未重新分析其当前表现，仅作为方案A/B的回归检查集纳入评测计划（见 `EVALUATION_PLAN_2026-07-17.md`） |

326条 Benchmark v2 上的 **Production** 与 **Candidate** 身份：

- **Production** = 当前 `main` 分支，真实线上站点 `curify-ai.com`，用 Playwright/Chromium 浏览器实际导航采集。数据：`docs/daily_report/7.17/easy-query-v2-production-baseline/relevance_evaluation.csv`。
- **Candidate** = 分支 `baobao/search-relevance-phrase-alias-2026-07-09`（**未合并、未push到远程、当前还带有26处未提交的本地改动**），用 Node.js in-process harness 直接调用该分支的搜索库采集（不经过浏览器）。数据：`docs/daily_report/7.16/easy-query-v2-validation/easy_query_v2_relevance_evaluation.csv`。
- **重要方法学局限（已在既有分析中披露，本文档如实转述）**：两侧采集的传输机制不同（浏览器 vs. in-process），这是统计分析明确承认"无法控制"的因素，不是刻意隐瞒。同时，本次代码复核发现该分支当前工作区还有**26个文件的未提交改动**（包括 `lib/searchRewrite.ts` 一份1013行的diff、`page.tsx` 一份299行的diff，均在7月16日21:43之后），**意味着实际工作区状态可能比任何一次评测捕获的候选分支快照更新**——这是一个需要在会议上提醒的时效性风险，不是评测本身的错误。

---

## 2. 326条评测：事实清单

### 2.1 判定口径

**全程使用 Top-5 加权相关性**（rubric-v1.1，排位权重 1:0.30 / 2:0.25 / 3:0.20 / 4:0.15 / 5:0.10），第6名及以后的结果**从未被采集、从未被人工看到、从未参与任何判定**。这个口径从旧328库的校准阶段沿用至今，未变更，是本项目所有评测报告共享的基准，不是本次新引入。

标签体系为 **PASS / PARTIAL / FAIL / UNJUDGABLE**（rubric锁定的四分类），**全仓库检索确认从未出现过"WARN"或"UNKNOWN"标签**——文档中如出现"PASS/WARN/FAIL/UNKNOWN"式的提法，指的应是"PASS/PARTIAL/FAIL"（UNJUDGABLE在本次326数据中未被实际使用）。本文档不做"WARN=PARTIAL"这类推测性等价假设。

### 2.2 标签分布（326条，Production vs Candidate）

| 标签 | Production | Candidate |
|---|---:|---:|
| PASS | 78（23.9%） | 82（25.2%） |
| PARTIAL | 137（42.0%） | 111（34.0%） |
| FAIL | 111（34.0%） | 133（40.8%） |

标签迁移矩阵（Production → Candidate，326条）：

| Prod ＼ Cand | FAIL | PARTIAL | PASS | 行合计 |
|---|---:|---:|---:|---:|
| FAIL | 87 | 18 | 6 | 111 |
| PARTIAL | 37 | 75 | 25 | 137 |
| PASS | 9 | 18 | 51 | 78 |
| 列合计 | 133 | 111 | 82 | 326 |

### 2.3 零结果 / 低结果

- **零结果**：Production 8条（2.45%）→ Candidate 34条（10.43%），**4.25倍**。
- **低结果阈值**：项目内唯一明确使用的阈值是 `LOW_RESULT_THRESHOLD = 5`（即 `first_pass_count < 5` 触发改写），代码中 `page.tsx:47` 定义，`SearchResultsClient.tsx` 内有重复定义。**没有 `<3` 这个阈值在任何现有文档中被使用。**
- 用该阈值对最终展示结果数重新计算（**注：这一步是本次任务的独立复算，不是原始文档直接给出的数字**）：Candidate 的 `result_count<5` 共73条（其中34条为0，39条为1-4）；Production 共41条（8条为0，33条为1-4）。

### 2.4 改写（Rewrite）指标——全部来自 Candidate 分支的196次改写触发记录

| 指标 | 数值 |
|---|---:|
| 触发改写 | 196 / 326（60.1%） |
| 触发前为零结果 | 171 / 196（87.2%） |
| **零结果救援成功**（0→>0） | 141 / 196（71.9%），占171条零结果起点的 **82.5%** |
| 改写后仍为零结果 | 30 / 171（17.5%） |
| 低结果逃逸（<5→≥5） | 125 / 196（63.8%） |
| 改写后最终 PASS 或 PARTIAL | 109 / 196（55.6%） |
| **虚假成功**（结果数暴涨但相关性判定仍FAIL） | 53 / 196（**27.0%**） |
| 中重度语义漂移（`intent_drift_flag=True`） | 61 / 196（31.1%）；漂移分布 NONE=103 / MINOR=32 / MODERATE=61 / SEVERE=0（本数据集中未出现SEVERE） |
| **净负面bug**（改写前有1-2条结果，改写后变成0条） | **4条，已精确定位**：V125（烘焙包装）、V127（咖啡馆菜单）、V153（饮料瓶）、V271（课程表） |

### 2.5 四类根因（分母=244条 FAIL+PARTIAL 记录，不是全部326条）

| 根因类别 | 数量 | 占244条的% | 占全部326条的% |
|---|---:|---:|---:|
| RETRIEVAL_RANKING（排序/召回混合问题） | 77 | 31.6% | 23.6% |
| QUERY_UNDERSTANDING_REWRITE（查询理解/改写问题） | 71 | 29.1% | 21.8% |
| CATALOG_GAP（目录内容缺口，含全部34条零结果） | 67 | 27.5% | 20.6% |
| AMBIGUOUS_INTENT（词义歧义/错误义项压过正确义项） | 29 | 11.9% | 8.9% |

**关于"排序问题占31.6%"的口径澄清（必须在会上讲清楚）**：这个数字基于 **Top-5**，是"Top-5综合失败诊断"，**不是**可以精确拆分成"排序贡献X%、召回贡献Y%"的工程指标——因为方法学从未采集Top-5之后的结果，没有 Recall@K/NDCG，没有人工标注的"这个查询本该匹配哪些模板"的ground truth。同时 AMBIGUOUS_INTENT 的11.9%被原分析明确认定为**下界不是上界**——未被评测员写出"词义碰撞"字样的碰撞案例会默认落入RETRIEVAL_RANKING。"改写本该触发但没触发"（`first_pass_count>=5`但这5条本身很差）是当前四分类体系的**已知盲区**，同样被动计入RETRIEVAL_RANKING，未单独统计。

### 2.6 历史交叉验证（旧328库，仅作为佐证，不与326条数字混用）

同一候选分支在**更早的、独立的、328条旧种子库**上也做过一次对比（`docs/daily_report/7.16/easy-query-production-vs-optimized-comparison-v1/`）：PASS 28.35%→31.71%，零结果 3.66%→14.33%（约3.9倍），低结果 13.11%→18.9%。该报告的最终结论原文引用："**本地优化候选版本...是真正意义上的混合结果：相关性PASS率和平均分小幅改善...但0结果率增至近4倍、FAIL率同时上升...不建议在当前状态下合并或提交PR**"，回归门禁（Regression Gate）四项中三项判定为 FAIL（严格相关性门禁FAIL、零结果门禁FAIL、改写安全门禁PASS_WITH_LIMITATIONS）。这次326条的独立评测**复现了同样的模式**，说明零结果回归不是某一次评测的偶然噪声。

---

## 3. 代表案例（吉祥物、periodic table，以及每类3-5个代表性案例）

全部案例详情、字段见同目录 `ROOT_CAUSE_CASES_FOR_SOLUTION_DESIGN_2026-07-17.csv`（共25条，取自既有 `ROOT_CAUSE_CASEBOOK.csv`），此处只摘要说明"为什么不是单个case问题"：

### 3.1 吉祥物 / periodic table（RETRIEVAL_RANKING 的典型代表，不是孤立案例）

- **V009 吉祥物**（zh）：42条原始命中，未触发改写，最终展示34条，FAIL，评分0。Top-5被"器官健康信息图"这类高频广谱模板占满。
- **V275 元素周期表**（zh）/ **V276 periodic table**（en）：均为26条原始命中，未触发改写，最终25条，FAIL，评分0。Top-5被同一批"MBTI/性格分类"角色卡片系列占满。**中英文两个语言对照版本表现一致，说明这是排序/模板降权问题，不是某个语言specific的分词问题。**
- 同类还有 V013贴纸、V084 logo、V165横幅——**同一个模式反复出现：原始召回量很大（26-147条），但Top-5被少数几个"高频广谱噪声模板"（如器官健康信息图、MBTI角色卡、动漫工作室对比图）系统性压过真正相关的内容**。这不是某一个查询词的偶发问题，而是"排序公式对高频模板缺乏降权机制"这一类问题，**全局修复方向：对历史评测中反复出现在不相关结果里的模板建立降权名单或噪声分数**。

### 3.2 查询理解/改写问题代表案例

- V268 globe（0→3205结果，FAIL）、V032 statue（0→2748，FAIL）、V058 plush pillow（0→819，FAIL）、V154 drink bottle（0→3134，FAIL）、V078 bobblehead（0→1777，PARTIAL）——**同一个模式：改写触发后，某一条过宽的改写路径把结果数拉爆到成百上千条，但相关性没有同步提升**。全局修复方向：改写多路径合并设置结果数硬上限 + 改写生成时增加"主体名词绑定"约束。

### 3.3 词义歧义/错误词项匹配代表案例

- V147 咖啡杯→World Cup（"cup"子串碰撞）、V242 black friday banner→Black Widow（"black"子串碰撞）、V054 charm→charming（词形变化碰撞）、V083 标志→landmark（多义词取错义项）、V045 迷你手办→city miniature（"迷你"泛化压过"手办"主体）——**同一个模式：精确/整词匹配的信号强度不够，子串或词根命中被当作与整词同等的匹配信号**。全局修复方向：精确token匹配优先于子串匹配 + 高频碰撞词的短语级保护词典。

### 3.4 基础召回/零结果代表案例（CATALOG_GAP）

- V259证书/V260 certificate、V221优惠券/V222 discount coupon、V005毛绒玩具、V289白板/V290 whiteboard——均为0结果，且**改写已尝试2-3条路径仍救不回来**，中英文对照版本表现一致，说明这是目录里**确实没有这个模板族**，不是分词或改写策略问题。这部分（34条零结果中约一半）**只能靠内容补充或Hybrid外部兜底解决，不是搜索算法能修复的**。

---

## 4. 根因 → 代码定位（已核实，非推测）

代码库：`/Users/baobaoli/Desktop/curify-frontend`（Next.js）。**重要提醒**：该分支当前工作区有26处未提交改动，以下行号已尽量核实为最新状态，但仍可能因后续本地编辑而漂移，落地前建议重新核对一次行号。

| 问题类别 | 当前逻辑位置 | 为什么会导致问题 |
|---|---|---|
| 低结果判定 | `page.tsx:47` `LOW_RESULT_THRESHOLD=5`；判定点约 `page.tsx:602`（`initialThinCount < LOW_RESULT_THRESHOLD`） | 纯计数阈值，无法区分"5条精准结果"和"5条勉强相关结果"，也无法覆盖"≥5条但Top-5仍很差"的盲区 |
| 分词/归一化 | `lib/searchTokens.ts`（`normalizeForSearch`约40行，`buildSearchTokens`约209行）——**此文件是候选分支相对生产的重构产物，生产版本这段逻辑内联在`page.tsx`中** | 当前是单字/单token打分，未对已知高频短语（"手办""咖啡杯"）做原子化保护，导致被拆解后子串误命中 |
| 打分 | `scoreQueryTokens`，`page.tsx`约449行 | token命中即计分，子串命中与整词命中权重差距不够大 |
| 严格/宽松匹配合并 | `hasStrict`门禁，`page.tsx`约747-749行（代码注释标注"Stage 6 hasStrict fix"，说明此逻辑此前已被修订过一次）：只要存在任意strict命中，全部relaxed结果被过滤掉 | 二元式全有全无逻辑：一旦有噪声模板命中strict，真正该走relaxed补充的内容被整体丢弃；反之如果完全没有strict命中，relaxed结果不受限地全部放行，是"排序问题"的重要诱因之一 |
| 改写 | `lib/searchRewrite.ts` `getMultiQueryPaths`（约1250行，该文件已从审计时的规模增长到1446行）+ 拒绝逻辑（`rejected_rewrites`，当前拒绝率仅6.1%，明显偏松） | 多路径改写候选缺少结果数上限和"必须保留原始核心token"的强约束，导致结果数暴涨与语义漂移 |
| 结果来源 | 100%来自内部目录，`InspRecord`/`ScoredInspiration`（`page.tsx`约405/429行） | 目录本身没有的模板族（证书、优惠券、毛绒玩具、白板等）无论怎么调整排序/改写都无法召回，是CATALOG_GAP的根本限制 |
| 缓存/超时 | `TIMEOUT_MS=8000`（27行）、`CACHE_MAX=256`/`CACHE_TTL_MS=7天`（307/308行）、新增`NEGATIVE_CACHE_TTL_MS=10分钟`（78行，此前审计未记录，是后续新增） | 与改写相关，非直接根因，但决定了修复方案上线后的缓存失效速度 |
| 外部检索能力 | **不存在**——全仓库检索 `customsearch/serpapi/SERP_API/GOOGLE_CSE/cse.google` 零命中；`@google/genai`（v1.48.0）已是依赖，但仅用于图片**生成**（`illustrator-demo/generate/route.ts`、`progseo-demo/generate/route.ts`），不涉及外部图片**搜索**；`redis`（^5.11.0）已是依赖但尚未用于任何外部检索缓存 | Hybrid Search 需要从零构建外部客户端、跨来源合并/去重、新的结果卡片组件——这在既有 `hybrid-search-technical-audit` 中已有详细设计，本次任务不重复设计，仅在方案B中摘要复用 |
| 埋点 | `search_id` 全仓库零命中；`user_interactions`表（`curify-studio/curify_background`）现有`action_type`枚举含SEARCH/SEARCH_NORESULT/SEARCH_LOWRESULT/CLICK/GENERATE，但搜索→点击靠`(user_id/session_id, 5分钟时间窗)`近似关联（Level 3），点击→生成完全断链（Level 4，不可靠） | 当前埋点无法支撑方案C/D评测所需的"这次结果来自内部还是外部""这次点击点的是哪一类结果"等问题，是Hybrid上线前必须补的P0项 |

---

## 5. 方案A：不含 Hybrid Search 的内部修复版（摘要，完整设计见既有 `manager-follow-up-analysis/` 文档，本节整合为落地口径）

**目标**：优先解决低垂果实，不引入外部依赖。全部改动挂 Feature Flag，默认可关闭，回退到当前候选分支行为。

| # | 改动 | 对应根因 | 优先级 |
|---|---|---|---|
| 1 | 修复"改写导致已有结果变成0"的4条净负面bug（V125/V127/V153/V271，已精确定位） | QUERY_UNDERSTANDING_REWRITE | P0 |
| 2 | 改写多路径合并结果数硬上限（`RESULT_COUNT_CAP_PER_PATH`） | QUERY_UNDERSTANDING_REWRITE | P0 |
| 3 | 高频噪声模板降权名单（`NOISE_TEMPLATE_DOWNWEIGHT_ENABLED`，配置级，非模型改动） | RETRIEVAL_RANKING | P1 |
| 4 | 实体短语保护词典（`PHRASE_PROTECTION_ENABLED`，如"咖啡杯""标志""charm"） | AMBIGUOUS_INTENT | P1 |
| 5 | 改写候选拒绝条件收紧（当前拒绝率仅6.1%偏松） | QUERY_UNDERSTANDING_REWRITE | P1 |

**任务书10问逐条回应**：

1. **Easy Query vs Hard Query 是否应用不同matching threshold**：现有326库全部按当前生产的统一逻辑跑，没有按难度分层的阈值设计。建议方向：不新增触发阈值本身（保持`LOW_RESULT_THRESHOLD=5`不变，避免引入未经校准的新参数），而是新增一个诊断指标——统计"`first_pass_count>=5`但Top-5相关率仍很低"的查询数量，摸清"改写未触发"这个盲区的真实规模，再决定是否需要按难度分层。**这是既有分析给出的建议，本次未做进一步扩展**。
2. **Rewrite应只补充结果，不覆盖原始结果**：已确认为4条净负面bug的根本原因（改写后把已有的1-2条结果丢弃归零）。修复方向：改写结果应与原始结果**合并**而非**替换**，原始非空结果集在任何情况下都应作为下限被保留。
3. **Rewrite/Guard失败时保留原始结果**：与上一条同一逻辑，是P0修复的核心不变量。
4. **Strict不足时如何安全进入relaxed**：当前`hasStrict`门禁是二元式（有任意strict命中就完全排除relaxed），建议改为按strict命中的**数量或质量**分级决定是否补充relaxed结果，而不是"有任意一个就全排除"。**这是本次代码复核新增的具体观察，既有文档未展开讨论此门禁的二元性质，建议在方案A实现阶段进一步细化**。
5. **如何避免relaxed tier flooding**：与噪声模板降权（矩阵中第3项）配合，对relaxed tier的结果同样施加降权/上限，不能因为进入relaxed就无限放行。
6. **标题单词偶然命中权重是否过高**：是——已确认的子串碰撞（cup/black/charm）证明当前打分对"token命中"与"整词/精确匹配命中"的区分不够，需要提升精确匹配的权重占比。
7. **是否需要title+tags+category多字段共同支持**：现有代码打分逻辑细节（是否已经融合多字段）在本次复核范围内未逐行确认，标注 **UNKNOWN，需要工程实现阶段进一步确认现状**，不做假设性描述。
8. **中文短词/英文高歧义词**：短语级token保护（第4项）是主要应对手段；中英文分词/别名扩展路径目前是两套独立实现（CJK bigram回退 vs 英文stemming），统一是更结构性的修复，属于P2，需要独立评估工作量。
9. **修复Hard Query时不伤害Easy Query**：这是评测计划的核心约束（见`EVALUATION_PLAN_2026-07-17.md`）——326条Easy Query必须作为每一版改动的回归门禁,不能只看68条Hard Query是否改善。
10. **最低结果保底/fail-open策略**：与第2/3条一致——原始结果集是下限，改写/降权/上限等任何新逻辑都不能让结果数低于"改写前+降权前"的基线，这是方案A的安全前提，不是可选项。

---

## 6. 方案B：含 Hybrid Search 的版本（摘要，完整技术设计见既有 `hybrid-search-technical-audit/`，本节整合为落地口径，详细流程图见 `HYBRID_SEARCH_FLOW_2026-07-17.md`）

**前提：方案A必须先独立落地并评测通过，方案B在方案A基础上叠加，不能跳过方案A直接做方案B**——这是既有技术审计（11阶段安全上线计划）和本次任务共同的结论，管理层"先简化再落地"的诉求与此一致。

- **触发条件**：沿用现有`LOW_RESULT_THRESHOLD=5`作为MVP起点（即结果数<5才触发外部检索），T0(`==0`)、T3(`<3`)作为后续离线实验的备选，不在MVP阶段变更。
- **Google Top-N**：MVP阶段建议N=8-12（与既有Core-80候选集设计一致）。
- **统一数据结构**：`HybridSearchResult`，含`result_key`/`source_type`/内部专属字段(`internal_result_id`)/外部专属字段(`external_provider`/`source_domain`/`attribution_label`)/共享字段(`title`/`image_url`/`destination_url`)/排序簿记(`rank_before_merge`/`rank_after_merge`)/硬编码安全字段(`can_edit`/`can_generate`对外部结果恒为`false`)。
- **去重**：URL canonical / 归一化图片URL / 标题+域名组合，三种MVP方案均已知有各自的局限（改版镜像、resize图片、通用标题误判），感知哈希/embedding相似度检测已明确推迟，非MVP范围。
- **合并策略**：内部结果永远优先展示，外部结果只填补空缺，不做token级混合排序。
- **排序策略**：MVP阶段不引入学习型reranker，只用确定性规则——因为目前没有任何相关性标注数据支撑训练/校准。
- **外部结果的定位**：明确是"填补空缺"，不参与主排序竞争，不是"最后兜底"这种模糊定位。
- **LLM rewriter的位置**：与外部检索调用**并行**触发（`Promise.allSettled`，不是`Promise.all`也不是串行），共享同一个低结果触发点。
- **缓存/超时/失败回退**：LLM腿复用现有8秒超时+256条/7天内存缓存；外部腿建议3-6秒超时（未实测）+ 共享持久化Redis缓存（`redis`已是现有依赖，不需要新增供应商）；硬性不变量——内部结果在任何异步分支开始前已同步计算完毕，外部/LLM失败在架构上不可能影响内部结果展示。
- **成本与延迟控制**：fail-fast不重试；建议熔断器（阈值待用真实错误率数据校准，不凭空定）；5个独立Feature Flag（`ENABLE_LLM_REWRITE`/`ENABLE_EXTERNAL_IMAGE_FALLBACK`/`ENABLE_HYBRID_RESULT_MERGE`/`ENABLE_EXTERNAL_RESULT_UI`/`EXTERNAL_SEARCH_KILL_SWITCH`，最后一个是独立于总开关的秒级止损开关）。
- **安全与来源标记**：外部图片只做hotlink，不代理/不重新托管；区块级"来自外部的灵感"标注+逐卡片域名角标（双重标注）；用独立的外部结果卡片组件渲染，确保"Remix/编辑/生成"等内部专属操作**在类型层面**对外部结果结构性不可用，不是运行时条件隐藏。
- **埋点设计**：MVP最小新增集合——`search_id`（核心锚点，其余字段有意义的前提）、`search_mode`（internal_only/hybrid）、`google_triggered`（与`rewrite_triggered`并列而非合并，避免无法区分是内部改写还是外部兜底救回的结果）、`result_source`、`result_rank`。`generate_click`/`generation_success`已有数据源但与搜索完全断链，需要`search_id`透传才能有意义。
- **与现有埋点的兼容性**：现有`rewrite_triggered`（`content_id`后缀`|rw=1`）可直接复用；但**这套埋点从设计之初就只覆盖"内部改写"这一件事，无法回答"结果来自内部还是外部""点击点的是哪一类结果"**——这是Hybrid上线前必须新增而非复用的部分。

**未解决/需要合规确认后才能推进的事项**：Google/外部图片供应商的合规、成本、配额目前仍是**unresolved**状态（既有`EXTERNAL_IMAGE_PROVIDER_OPTIONS.md`结论），现有Google API key的存在只解决了"能不能调用"，不解决"该怎么缓存、署名到什么程度、调用预算是多少"。

---

## 7. 推荐实施顺序

1. 方案A代码实现 + Feature Flag接入（工程）。
2. 方案A用锁定的326条Benchmark v2离线评测，产出与本次分析同构的对比数据，**这一步产出前不建议启动方案B开发**。
3. 方案A评测结果达标（相对Candidate分支有净改善、且不引入新回归，尤其零结果率不能上升）后，再启动方案B（含Hybrid）开发。
4. 方案B离线评测（见`EVALUATION_PLAN_2026-07-17.md`第4节Hybrid专属指标）。
5. 管理层基于方案A/B的离线评测数据，决定是否进入既有`HYBRID_SEARCH_SAFE_ROLLOUT_PLAN.md`的线上分阶段验证流程（Stage 7-10：预发布QA→小流量A/B→分阶段放量，本次任务不涉及）。

---

## 8. 今天会议需要决定的问题（详细版见 `DESIGN_REVIEW_CHECKLIST_2026-07-17.md`）

1. 是否认可"候选分支当前不建议合并"的结论，还是希望先单独修复4条净负面bug后重新评估？
2. 方案A的5项改动是否需要调整优先级或范围？
3. 是否认可"方案A必须先独立评测达标，才能启动方案B开发"这一顺序，还是希望并行推进？
4. 埋点改造（`search_id`等5个MVP新增字段）由谁、什么时间节点完成？这是方案B能否被有效评测的前提。
5. Google/外部供应商的合规、成本、配额确认，由谁负责推进？这是方案B Stage 2的前置条件。
6. 是否需要扩大评测范围到Top-10（会增加评测成本），还是维持现有Top-5口径？
7. `hasStrict`门禁的二元逻辑改造（第5节第4点）是否纳入方案A本轮范围，还是单独排期？
8. 34条CATALOG_GAP零结果查询的内容缺口清单，是否同步给内容/模板团队作为素材补充依据？
9. 候选分支当前26处未提交改动，是否需要先确认/合并/丢弃，再作为方案A/B的开发起点？

---

## 附：本文档明确不做的断言

- 不声称候选分支已部署、已合并、已上线。
- 不声称Hybrid Search已实现——目前是纯设计文档，代码中没有任何外部检索、合并、去重逻辑。
- 不把"有结果"等同于"相关"，也不把FAIL等同于"零结果"——两者是独立维度，本文档全程分别报告。
- 不把自动化/LLM辅助的相关性判断当作人工真值——所有326条评测均由同一套rubric+同一评测人执行,非双盲、无inter-rater reliability检验,这是本项目所有评测共享的已知局限。
- 不从离线相关性评测中得出关于CTR或生成转化率的结论——这需要真实用户行为埋点，当前埋点尚不支持。
