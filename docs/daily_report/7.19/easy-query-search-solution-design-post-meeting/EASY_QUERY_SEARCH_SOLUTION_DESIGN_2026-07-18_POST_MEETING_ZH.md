# Curify 搜索问题 · 解决方案 Design（会后最终版）

日期：2026-07-18　性质：**只读分析 + 设计文档**。本次任务未修改任何生产代码，未新建开发分支，未提交 commit，未 push，未创建 PR，未重跑 326/68/328 条查询评测。本文档是对会前最终版 Design 的会后修订，信息来源与优先级为：

```
会议最终决定  >  老板书面反馈  >  会前最终版 Design  >  历史评测和旧方案背景
```

凡会议已修改的内容，均以本文档为准，会前版本中相应表述不再作为最终要求。历史数据、案例和代码定位保留作为背景，但不重新计算、不重新采集。

**源文件**：`docs/daily_report/7.17/easy-query-search-solution-design-v1/EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-17_zh.md`（会前最终版，明确标注"2026-07-17 基线重置修订"）。该文件与 `docs/daily_report/7.17/easy-query-search-solution-design/EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-17_zh.md` 内容逐字相同；本文档以前者所在目录为准，因为文中引用的 `RUN_LOG.md` 等支撑文件仅存在于该目录。未使用同目录下的 `EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-17_zh.before-reset-baseline.md`（该文件是基线重置前的旧版本，已被会前版本本身废弃）。

**标注约定**：全文中，`[会议决定]` 表示会上明确拍板的内容；`[老板反馈]` 表示书面反馈中的原话或直接对应；`[沿用会前]` 表示会前 Design 中未被会议改动、继续有效的内容；`[本次新增/proposed]` 表示本文档为落实会议决定而新增的设计建议，尚未实现、尚未经工程验证，权重/阈值等具体参数待首轮实验后校准；`UNKNOWN` 表示当前材料无法确认，需工程阶段核实。

---

## 1. Executive Summary

1. **`[会议决定]`** 开发基线维持"回到 Production main"的方向，但落地方式做了明确澄清：**不直接在 main 分支上写代码**，而是从当前 Production main 创建一个新的干净开发分支（V2 分支），main 本身作为对照 Baseline（V0），新分支作为本次内部修复的 Candidate，与 V0 做整体对比评测。
2. **`[会议决定]`** 旧候选分支（`baobao/search-relevance-phrase-alias-2026-07-09`）继续冻结，作为历史参照（V1），不整体 merge、不大块 cherry-pick，不作为新分支起点——这一点与会前 Design 完全一致，会议未做改动。
3. **`[老板反馈]` + `[会议决定]`** 修复方向 1、2、6 已获认可，按会前 Design 中的方案直接实施，未做实质性改动。
4. **`[老板反馈]` + `[会议决定]`** 方向 3、4、5 不再作为三套互相独立的规则，改为由一套**统一的轻量文本相关性打分机制**协同处理——这是本次修订相对会前 Design 最大的结构性变化，详见第 9、10 节。
5. **`[老板反馈]` + `[会议决定]`** 方向 7（高频广谱噪声模板降权）不能只停留在"建立降权名单"。新 Design 要求先做根因调查（这些模板为什么被广泛召回、命中的是什么字段/token/路径），降权名单只作为短期配置级补丁，同时必须给出长期机制方案。详见第 11 节。
6. **`[老板反馈]` + `[会议决定]`** 会前 Design 中"每项修复必须单独挂 Feature Flag、默认可单独关闭回退"的硬性要求被**正式撤销**。改为：从 Production main 新建一个 V2 分支，整体与 V0 做对比评测；开发过程中建议使用独立 commit 便于 Code Review、定位回归和必要时 revert；内部消融可通过独立 commit、临时配置或离线评测脚本完成，不要求为每个实验组构建正式运行时开关；上线后如出现严重问题，允许整体回滚部署或 revert PR。
7. **`[老板反馈]`** 整体替换线上 Production 是被认可的路径，不要求灰度式的逐项开关上线。
8. **`[老板反馈]` + `[会议决定]`** 鉴于此前曾发生 LLM rewriter、multi-path retrieval 在新版本替换 Production 时被意外删除或 disable 的情况，本次新 Design 把"现有功能是否仍然存在且可正常触发"列为正式上线门禁，覆盖 LLM rewriter、multi-path retrieval、decomposition、L2 层级内容、多段落展示等，且要求行为级验证，不能只检查代码文件是否存在。详见第 12 节。
9. **`[老板反馈]`** 当前阶段只做不带 Hybrid Search 的版本（V2），基于 Production main 整体修复；只有评测结果显著优于 Production main 才允许上线。Hybrid Search / HyperResearch 推迟到 V3，本文档只保留边界说明。详见第 17 节。
10. 会议未确认固定的百分点提升门槛（如 8%、10%）。"显著优于 main prod" 在本文档中定义为一组定性 + 统计标准的组合（见第 14 节），具体数值门槛留待首轮 V2 实验后与管理层确认。

---

## 2. 会后最终决策（逐条对照会议纪要）

本节完整转述第五部分给出的会议结论，作为全文的最高优先级依据。

### 2.1 开发基线

- 上次的新开发候选分支（V1，`baobao/search-relevance-phrase-alias-2026-07-09`）正式废弃，不再在其上修补。
- 后续开发基于当前实际 Production main，但**不是直接在 main 分支上写代码**。
- 应从当前 Production main 创建一个新的干净开发分支（下称 V2 分支）。
- Production main 作为对照 Baseline（V0）。
- V2 分支作为本次内部修复 Candidate。
- V2 分支与 V0（main prod）做对比评测。

这一条相对会前 Design 是**澄清而非推翻**：会前 Design 第 9 节步骤 4 已写明"从 Production main 新建干净分支"，会议在此基础上进一步明确了"不是直接在 main 上写代码"这一容易被误读的点，避免团队理解为"直接向 main 提交改动"。

### 2.2 修复方向

- 方向 1、2、6：方案已认可，按现有方向实施，无需重新设计。
- 方向 3、4、5：不再各自独立成规则，进一步研究是否由一套轻量相关性打分机制统一处理。
- 完整精准的相关性打分体系成本高，本阶段不做。先设计一套**轻量、基于文本、可解释、低成本、确定性**的相关性评分机制。
- 该评分机制应尽可能统一处理方向 3、4、5，而不是继续维护三套互相独立的规则。

### 2.3 高频广谱噪声模板

对器官健康信息图、MBTI 角色卡等在无关 Query 中反复进入 Top Results 的广谱模板，不能只写"增加降权名单"。新 Design 必须：

1. 调查这些模板为什么会被广泛召回；
2. 定位具体命中字段；
3. 定位命中的 token、phrase、alias、substring；
4. 定位是 original、strict、relaxed、rewrite、decomposition 还是 multi-path 路径引入；
5. 判断是否因为模板元数据过宽；
6. 判断是否因为同一模板族数量优势；
7. 判断相关性评分能否自动将其压到后排；
8. 降权名单只能作为短期、配置级、soft penalty 补充；
9. 必须给出长期机制方案；
10. 长期目标是未来新增相似噪声模板时也能被系统自动降到后排，不再持续人工加黑名单。

### 2.4 Feature Flag 与回滚

会议**否定**了"每项改动必须单独挂运行时 Feature Flag"的硬性要求。改为：

- 不要求方向 1—7 分别增加运行时 Feature Flag；
- 从 Production main 创建一个新的 V2 开发分支；
- 用 V0（Production main）和 V2（新分支）做整体对比；
- 开发过程中仍建议使用独立 commit，用于 Code Review、定位回归、必要时 revert；
- 内部如需消融，用独立 commit、临时配置或评测脚本完成，不构建正式运行时开关；
- 上线后出现严重问题时，允许整体回滚部署或 revert PR。

本文档不再出现"每项修复必须单独 Feature Flag"这一表述作为最终要求；会前版本中的相关文字已被本条会议决定覆盖，仅在第 15 节以"会前要求，已被会议修改"的方式做历史引用。

### 2.5 现有功能回归

会议特别指出，此前新版本替换 Production 时曾发生 LLM rewriter 被删除或 disable、multi-path retrieval 被删除或 disable、L2 层级内容失效、多段落展示功能失效等问题——新代码覆盖旧代码后，原本已有功能丢失。因此新 Design 把以下内容列为正式上线门禁（详见第 12 节）：

- LLM rewriter 代码仍存在且实际可触发；
- Rewrite Guard 未被删除或默认关闭；
- multi-path retrieval 实际可运行；
- decomposition 等原有路径正常；
- L2 层级内容正常展示；
- 多段落内容正常展示；
- 页面结果卡片、点击、Generate/Remix 等现有功能正常；
- 不能只检查代码文件是否存在，必须做行为级回归测试；
- Production build、TypeScript、自动测试通过；
- Preview 或本地真实页面验证通过。

### 2.6 分阶段版本

- **V2（当前版本）**：基于 Production main，只做内部检索修复，不接 Hybrid Search，不接 HyperResearch，只有评测明显优于 main prod 才允许上线。
- **V3（后续版本）**：在锁定并验证通过的 V2 基础上叠加 Hybrid Search / HyperResearch，不建立在旧 Candidate（V1）上，不允许 Hybrid 掩盖内部搜索排序/改写/Matching 问题，V2 和 V3 必须分别评测。本文档只保留 V3 的边界说明（第 17 节），不展开完整 Hybrid 实现细节。

---

## 3. 数据身份与历史结论 `[沿用会前，历史事实，不重新计算]`

### 3.1 数据集

| 数据集 | 文件 | 条数 | 用途 |
|---|---|---|---|
| 旧 328 条种子库 | `docs/daily_report/7.15/easy-query-production-baseline-v1/query_input/easy_queries_cleaned_300_plus_2026-07-14.csv` | 328 | 7.15 生产基线 + 7.16 Run A/B 历史对比，仅作历史交叉验证引用 |
| 新 326 条 Benchmark v2 | `docs/daily_report/7.16/easy-query-bank-v3/easy_query_bank_v2_2026-07-16.csv` | 326 | 核心评测查询库，4 场景中英文各半，本文档历史数字均来自此库 |
| 68 条 Hard Query 回归集 | `docs/daily_report/7.14/search-relevance-stage7-rerun/full-68-rerun-v2/hard_queries_baseline_locked_68_2026-07-14.csv` | 68 | 复杂 Query / flooding 回归检查集 |

### 3.2 V0 vs V1 历史评测结论（2026-07-17 快照，不代表新 V2）

326 条 Benchmark v2：

- PASS：Production（V0）23.9% → Candidate（V1）25.2%，**统计上不显著**（McNemar p=0.69）；
- 零结果率：Production 2.45% → Candidate **10.43%，4.25 倍**；
- 结论：V1 用零结果大幅增加换取有限的 PASS/均分改善，是净负面交易。

旧 328 条：零结果率 3.66% → 14.33%，约 3.9 倍，同一模式在独立数据集上复现。

**这些数字是 2026-07-17 时点对旧候选分支（V1）的历史快照，与本次将要开发的 V2（新分支）无关，不得包装成 V2 的结果，也不重新计算。**

### 3.3 改写（Rewrite）历史指标（V1 上采集）

- 触发改写 196/326（60.1%），零结果救援成功率 82.5%（占 171 条零结果起点）；
- 虚假成功（结果数暴涨但相关性判定仍 FAIL）53/196（27.0%）；
- **净负面 bug（改写前有 1-2 条结果，改写后变成 0 条）4 条，已精确定位**：V125（烘焙包装）、V127（咖啡馆菜单）、V153（饮料瓶）、V271（课程表）。这 4 条是方向 1、2 的直接证据来源，也是 V2 的 P0 修复项。

### 3.4 四类根因（分母 244 条 FAIL+PARTIAL，V1 历史评测）

| 根因类别 | 数量 | 占 244 条 |
|---|---:|---:|
| RETRIEVAL_RANKING（排序/召回混合问题） | 77 | 31.6% |
| QUERY_UNDERSTANDING_REWRITE（查询理解/改写问题） | 71 | 29.1% |
| CATALOG_GAP（目录内容缺口，含全部 34 条零结果） | 67 | 27.5% |
| AMBIGUOUS_INTENT（词义歧义/错误义项压过正确义项） | 29 | 11.9% |

### 3.5 代表案例（保留，作为 V2 修复方向和评分维度设计的依据）

- **噪声模板压制真实结果**：V009 吉祥物、V275/V276 元素周期表、V013 贴纸、V084 logo、V165 横幅——原始召回量大（26-147 条），但 Top-5 被"器官健康信息图""MBTI 角色卡"等高频广谱模板系统性占满。
- **改写结果数暴涨**：V268 globe（0→3205）、V032 statue（0→2748）、V058 plush pillow（0→819）、V154 drink bottle（0→3134）、V078 bobblehead（0→1777），均为某条过宽改写路径把结果拉爆但相关性未同步提升。
- **子串/词形碰撞**：V147 咖啡杯→World Cup、V242 black friday banner→Black Widow、V054 charm→charming、V083 标志→landmark、V045 迷你手办→city miniature。
- **CATALOG_GAP（目录确实没有）**：V259 证书、V221 优惠券、V005 毛绒玩具、V289 白板——改写已尝试多条路径仍救不回，属于内容缺口，不是算法能修复的范围。

### 3.6 方法学限制 `[沿用会前，必须继续遵守]`

- 现有相关性评分只覆盖 **Top-5**，第 6 名及以后从未被采集、从未被人工看到；
- 没有完整人工 Ground Truth，没有 Top-5 之后的统一人工标注；
- 因此 Recall@K、MRR、nDCG **不应作为当前已具备的正式验收指标**；
- 可继续使用的指标：PASS/PARTIAL/FAIL、Top-5 加权相关性、零结果率、低结果率、Rewrite 指标、噪声模板 Top-3/Top-5 出现次数、V0→V2 改善与回归 Query 数量；
- 可继续使用 McNemar、Wilcoxon 或 paired bootstrap 做显著性检验，但**统计显著性不能代替产品实际意义**。

---

## 4. 本阶段目标与范围

**目标**：在 Production main 基础上，新建一个干净的 V2 开发分支，只做内部检索/改写/排序修复，不接 Hybrid Search，不接 HyperResearch。通过与 V0（Production main）的整体对比评测，验证 V2 是否在不引入新回归（尤其是零结果回归和已有功能丢失）的前提下取得明确、可感知的相关性改善。评测明显优于 V0 才允许整体替换 Production。

**范围内**：
- 方向 1、2、6（第 8 节）；
- 统一轻量相关性评分机制，覆盖方向 3、4、5（第 9、10 节）；
- 方向 7 的根因调查 + 短期降权 + 长期机制（第 11 节）；
- 现有功能（LLM rewriter、multi-path、L2、多段落等）的行为级回归保护（第 12 节）；
- V0 vs V2 的统一采集、统一评测方案（第 13 节）。

**范围外（推迟到 V3 或不在本次讨论）**：
- Hybrid Search（外部图片检索、去重、合并、埋点）；
- HyperResearch；
- 完整精准相关性打分体系（学习型 reranker、向量相关性模型）；
- 按 Easy/Hard Query 分层设置不同 matching threshold（沿用会前 Design 的"暂不新增阈值，先摸清盲区规模"结论，未被会议改动）；
- 中英文分词/别名扩展路径的统一（会前 Design 标注为 P2，未被会议提及，维持原状）。

---

## 5. V0 / V1 / V2 / V3 定义

| 版本 | 定义 | 定位 |
|---|---|---|
| **V0** | 当前 Production main | 对照 Baseline，所有评测的锚点 |
| **V1** | 旧 Candidate（`baobao/search-relevance-phrase-alias-2026-07-09` 历史快照） | 仅历史参照，已冻结，不再开发；用于验证 V2 是否重蹈 V1 的回归模式（尤其是零结果回归） |
| **V2** | 从 Production main 新建的干净分支，本次内部修复的 Candidate | 当前阶段的开发主线；只做内部检索修复，不接 Hybrid；评测明显优于 V0 才允许上线 |
| **V3** | V2（锁定后）+ Hybrid Search / HyperResearch | 后续版本，不建立在 V1 上，不允许掩盖 V2 应修复的问题；V2、V3 分别评测 |

V2、V3 均尚未实现，本文档不预先填入两者的评测数字。

---

## 6. 旧 Candidate（V1）处置 `[沿用会前，会议未改动]`

1. **归档，不继续开发。** V1 分支（含其历史上 26 处未提交改动）冻结，作为历史实验记录归档，不再接受新提交。
2. **不整体 merge。** 第 3 节的评测结果已两次证明整体改动是净负面交易（零结果率 4 倍级上升）。
3. **不直接 cherry-pick 大块提交。** 不允许把 V1 的大块 commit（如 `lib/searchRewrite.ts` 的 1013 行 diff、`page.tsx` 的 299 行 diff）整体搬运到 V2 分支，即便部分改动"看起来是好的"。
4. **只允许经独立证据验证的思路，在 V2 分支重新实现。** "独立证据"指能追溯到具体 FAIL/PARTIAL 案例（如 V125/V127/V153/V271、V147/V242/V054 等），且该问题在 Production main 上被重新确认存在——不能假设 V1 上的问题在 V0 上以相同形式存在，需要在 V2 分支开发时重新验证。
5. **V1 只保留为历史比较基线**，用于新 V2、V3 与之对比，证明新路线是否真的避免了旧路线的回归模式，不用于其他目的。

---

## 7. V2 搜索链路（现状背景，非 V2 已实现描述）`[部分沿用会前，UNKNOWN 标注保留]`

以下代码定位来自会前 Design 对 V1（旧候选分支）历史快照的复核，用于理解现有逻辑长什么样、V2 分支需要动哪些位置，**不代表 V2 分支的最终实现，行号在 Production main 上必须重新核对**：

| 环节 | 现状（历史参照，需在 Production main 重新核对） | 与本次修复方向的关系 |
|---|---|---|
| 低结果判定 | `LOW_RESULT_THRESHOLD=5`，纯计数阈值，无法区分"5 条精准结果"和"5 条勉强相关结果" | 方向 3；不新增触发阈值本身，保持该值不变 |
| 分词/归一化 | 单字/单 token 打分，未对已知高频短语做原子化保护 | 方向 4、6 |
| 打分 | token 命中即计分，子串命中与整词命中权重差距不够大 | 方向 4，统一评分机制核心改造点 |
| 严格/宽松匹配合并 | `hasStrict` 门禁为二元式：只要存在任意 strict 命中，全部 relaxed 结果被过滤掉 | 方向 3，改为质量/数量门禁 |
| 改写 | 多路径改写候选缺少结果数上限和"必须保留原始核心 token"的强约束 | 方向 1、2、5、6 |
| 结果来源 | 100% 来自内部目录 | CATALOG_GAP 类问题不是本次内部修复能解决的，属于 V3/内容补充范畴 |
| 外部检索能力 | 不存在 | 与 V2 无关，属于 V3 |
| 埋点 | 缺少 `search_id` 等能支撑结果来源归因的字段 | 属于 V3 前置项，V2 阶段不要求补齐，但不应阻碍 V2 独立评测（V2 评测不依赖 Hybrid 埋点） |

**UNKNOWN**：现有打分逻辑是否已融合 title+tags+category 多字段支持，本次未逐行确认，需工程实现阶段核实。

---

## 8. 已确认修复方向：1、2、6 `[老板反馈：没问题，就应该这样；会议：已认可]`

### 8.1 方向 1：Rewrite 不能清空已有结果

**不变量**：当 `original_results` 非空时，final candidate pool 必须保留 `original_results`。

对应历史案例：V125（烘焙包装）、V127（咖啡馆菜单）、V153（饮料瓶）、V271（课程表）——均为改写前有 1-2 条结果，改写后变成 0 条的净负面 bug。

**澄清**：保留原始结果的"存在"是下限保证，**不等于必须保留原始排名**——原始结果可以与 Rewrite 结果一起进入统一评分（第 9 节），按最终分数重新排序。

### 8.2 方向 2：原始候选池与 Rewrite 候选池安全合并

- 合并，不替换；
- 通过稳定结果 ID 去重；
- 保留每条结果的命中来源（original / strict / relaxed / rewrite / decomposition / multi-path）；
- 某一条宽泛 Rewrite 路径不能凭结果数量主导最终排序；
- Original、Rewrite、decomposition、relaxed 等路径的结果最终都进入统一评分（第 9 节），由评分决定去留和排序，而不是按路径来源硬性优先。

### 8.3 方向 6：Subject binding + phrase protection

- Rewrite 生成时必须保留原始查询的主体（subject binding）；
- 完整短语不能被拆散后发生错误义项扩展（phrase protection）；
- 保护词表必须由真实案例支撑（如"咖啡杯""标志""charm"），不能无限扩展成人工词典；
- 需要与第 9 节的统一相关性评分共同工作：subject binding 提供生成侧约束，评分中的 Subject Coverage / Rewrite Drift 维度提供事后检测，两者互为验证。

---

## 9. 统一轻量文本相关性评分设计 `[老板反馈 + 会议决定，本节为本次修订核心新增内容]`

### 9.1 为什么需要统一评分

会前 Design 把方向 3（strict/relaxed 门禁）、方向 4（短语/整词/子串优先级）、方向 5（Rewrite 路径候选数控制）写成三套互相独立的规则。老板书面反馈明确提出"是否需要引入相关性打分，或者用相关性打分统一一下"，会议确认：**完整精准的相关性打分体系成本高，本阶段不做；但应设计一套轻量、基于文本、可解释、低成本、确定性的相关性评分，尽可能统一处理 3、4、5，而不是继续维护三套独立规则。**

评分机制的用途（`[proposed]`）：

- 评价 Strict 命中的真实质量，决定是否/如何补充 Relaxed 结果；
- 区分完整短语、整词和子串命中；
- 判断结果是否覆盖 Query 主体，是否只命中了宽泛修饰词；
- 判断 Rewrite 是否发生主体漂移；
- 判断某条 Rewrite Path 是否过宽；
- 压低广谱噪声模板，控制同一模板族重复占位；
- 对 original、rewrite、decomposition、relaxed 等路径统一排序，替代"哪条路径来的就怎么处理"的分路径规则。

### 9.2 评分维度结构（proposed，权重待校准）

```
Final Relevance Score
=
  Base Retrieval Score
+ Exact Phrase Match
+ Whole Token Match
+ Subject Coverage
+ Modifier Coverage
+ Field Support
+ Category / Topic Consistency
+ High-quality Multi-path Agreement
- Substring Collision
- Missing Subject
- Rewrite Drift
- Over-broad Rewrite Path
- Broad Noise Template
- Template Family Saturation
```

**必须强调的边界**：

- 当前阶段先确认评分维度，不是先确认具体权重；权重需要在代表案例（第 3.5 节）上校准，且校准过程应避免"看到全量结果后逐 Query 过拟合调参"；
- 评分权重集中配置（单一配置源，而不是散落在各个路径的判断逻辑里）；
- 每条结果输出 score breakdown（见 9.3），保证可解释、可复核；
- 不增加新的 LLM 请求（评分本身是确定性、基于文本特征的计算，不调用模型）；
- 不使用学习型 reranker（沿用会前 Design 对 Hybrid 排序策略的同一原则，本阶段没有相关性标注数据支撑训练/校准）。

### 9.3 Score Breakdown（proposed 结构，非已实现的 TypeScript 类型）

每条候选结果的评分输出应至少包含以下字段（字段名和结构为设计建议，非最终实现）：

```
- base_retrieval
- exact_phrase
- whole_token
- subject_coverage
- modifier_coverage
- field_support
- category_topic_consistency
- path_agreement
- substring_penalty
- missing_subject_penalty
- rewrite_drift_penalty
- broad_noise_penalty
- over_broad_path_penalty
- family_saturation_penalty
- final_score
- reasons: string[]   // 人类可读的评分理由，便于回归排查和会议复核
```

`reasons` 字段是可解释性的关键：应能回答"这条结果为什么排在这里"，尤其用于第 11 节噪声模板压制效果的验证，以及后续回归排查时快速定位是哪个维度导致排序变化。

---

## 10. 方向 3、4、5 如何被评分统一

### 10.1 方向 3：Strict / Relaxed —— 由二元门禁改为质量/数量门禁

- Strict 和 Relaxed 候选统一进入同一候选池，由第 9 节的评分决定去留，Strict 不再是"存在即自动最终胜出"；
- 当高质量 Strict 结果已经足够（数量和分数达到一定水平）时，不大量补充 Relaxed；
- 当 Strict 数量少，或整体质量低（评分低）时，从 Relaxed 中按分数补充；
- Relaxed 不得无限 flooding——受第 9 节的候选数上限和噪声惩罚约束；
- 如果全部结果都较弱，**不通过硬过滤制造新的零结果**——这是与方向 1、2 共享的底线（原始结果不得被清空的不变量同样适用于这里）。

### 10.2 方向 4：Phrase / Whole Token / Substring —— 优先级顺序

```
完整短语
>
多个核心整词
>
单个核心整词
>
合理 Alias / 词形
>
子串
```

该优先级通过第 9 节评分中的 `exact_phrase` / `whole_token` / `substring_penalty` 三个维度体现为分数差，而不是硬编码的"命中即通过/命中即拒绝"规则。覆盖历史案例：coffee cup → World Cup、black friday → Black Widow、charm → charming、标志 → landmark、迷你手办 → city miniature——这些均属于子串或宽泛词形命中被评分机制压低的目标场景。

### 10.3 方向 5：Rewrite Path 与候选数控制

不是简单加一个固定上限，而是多层控制的组合（`[proposed]`）：

- 单路径候选数上限；
- 所有 Rewrite 路径合并后的候选池总上限；
- 单个模板族在候选池中的数量控制（与第 11 节 Template Family Saturation 共用同一机制）；
- 路径与原 Query 主体一致性（对应 Subject Coverage / Rewrite Drift 评分维度）；
- 路径结果数量、路径高相关结果比例、路径平均相关性——作为 `path_agreement` 和 `over_broad_path_penalty` 的输入；
- 必要时拒绝严重漂移或过宽的路径（不是拒绝整个改写机制，而是拒绝某一条具体路径的贡献）；
- **某条路径失败不得影响原始候选结果**——这一点与方向 1 的不变量一致，是安全前提，不是可选项。

对应历史案例：V268 globe（0→3205）、V032 statue（0→2748）、V058 plush pillow（0→819）、V154 drink bottle（0→3134）、V078 bobblehead（0→1777）——均为某条过宽路径主导结果数但相关性未同步提升，属于本节机制的直接目标场景。

---

## 11. 方向 7：高频广谱噪声模板 `[老板反馈：为什么被广泛匹配到？是否有长期方案？会议：拆成根因调查+短期+长期三层]`

会前 Design 把方向 7 写成"建立降权名单是可以快速上线的配置级改动"。老板书面反馈和会议都明确指出：**这只是可以做的短期动作，核心问题是没有说清楚这些模板为什么被广泛召回，以及有没有长期方案**。本节将方向 7 拆成三层。

### 11.1 根因调查（proposed，Query→Result Trace 设计）

对代表案例（V009 吉祥物、V275/V276 元素周期表、V013 贴纸、V084 logo、V165 横幅等）需要输出一份 Query→Result Trace，至少包含以下字段：

```
- query
- normalized_query
- query_tokens
- protected_phrase
- result_title
- result_tags
- result_description
- result_category / result_topic
- matched_field
- match_type            // exact_phrase / whole_token / substring / alias
- source_path           // original / strict / relaxed / rewrite / decomposition / multi-path
- rewrite_text
- original_retrieval_score
- relevance_score_breakdown   // 即第9.3节的 score breakdown
- rank_before_scorer
- rank_after_scorer
- template_family
- same_family_top5_count
```

用这份 Trace 回答老板提出的问题：这些噪声模板究竟是通过哪个字段（title/tags/description/category）、哪种匹配类型（子串/整词/短语）、哪条路径（strict/relaxed/rewrite/decomposition/multi-path）被召回的；是否因为模板元数据本身过宽（标签堆砌、描述覆盖面大）；是否因为同一模板族在目录中数量占优势，天然获得更多召回机会。

### 11.2 统一评分验证（proposed）

在第 9 节评分机制设计出来后，针对已知噪声模板案例逐条验证：

- `rank_before_scorer` vs `rank_after_scorer`：评分前后排名变化；
- 是否仍进入 Top-3 / Top-5；
- 真正相关的结果排名是否相应提升；
- 是否对正常 Query（即该模板确实相关的场景）引入误伤——降权不能变成对该模板族的全局封杀。

如果评分机制本身已经能把这些模板稳定压到后排，短期降权名单的必要性和范围应相应缩小。

### 11.3 短期降权（proposed，仅在评分机制仍不足时补充）

- 小规模、配置级、soft penalty（不是硬性排除）；
- 基于重复出现的真实案例，以模板族或模式为单位，不逐个堆 template ID；
- 每条降权规则记录原因和证据（对应哪些案例、哪次评测观察到）；
- 明确标注为短期补丁，不是长期主方案，不能替代第 9 节评分机制和 11.4 的长期治理。

### 11.4 长期方案（proposed，方向性设计，非本次实现范围）

- 字段级权重（title 权重高于宽泛的 tags/description 堆砌内容）；
- phrase / whole-word 优先于 substring（与第 10.2 节同一机制）；
- Subject Coverage、Category/Topic Consistency 评分维度持续压制主体不匹配的宽泛模板；
- Rewrite Drift 控制，避免改写路径把宽泛模板意外引入；
- Relaxed 质量控制（第 10.1 节），避免宽泛模板通过 Relaxed 通道无限进入；
- Template Family Saturation（第 9.2 节）：限制同一模板族在候选池/Top 展示中的占位数量；
- 模板元数据治理：评估是否需要在内容侧收紧过宽的标签/描述，这一点需要与内容/模板团队协作，超出搜索算法能单独解决的范围；
- 目标：未来新增结构类似的噪声模板（例如新的信息图系列、新的角色卡系列）时，评分机制和 Family Saturation 机制能自动将其压到后排，而不需要每次都人工新增黑名单条目。

---

## 12. 现有功能回归保护 `[老板反馈 + 会议决定，正式上线门禁]`

老板书面反馈中特别提到："之前遇到过 LLM rewriter、multi-path retrieval 在新上线时候被删除或 disable 的情况，这个要留意。" 会议将其列为正式门禁，要求行为级验证，不能只检查代码文件是否存在。

### 12.1 门禁清单

- LLM rewriter 代码仍存在且实际可被触发（不是文件存在但调用路径被短路）；
- Rewrite Guard 未被删除、未被默认关闭；
- multi-path retrieval 实际可运行，各路径确实参与候选池合并；
- decomposition 等原有路径行为正常；
- L2 层级内容正常展示（UNKNOWN：L2 具体指代的页面层级/组件，需工程阶段结合现有代码结构确认）；
- 多段落内容正常展示；
- 页面结果卡片、点击、Generate/Remix 等现有功能正常；
- Production build、TypeScript 类型检查、既有自动化测试全部通过；
- Preview 环境或本地真实页面人工验证通过。

### 12.2 验证方式

- **不能只检查代码文件是否存在**——必须实际触发对应路径（如构造一个已知会触发改写的 Query，确认改写真的发生；构造一个已知会走 multi-path 的 Query，确认多路径结果真的被合并），观察行为结果，而不是静态审查代码。
- 建议复用第 3 节列出的 12 条 P0 页面截图 Case（`[沿用会前评测数据集]`）作为页面级人工回归集的一部分，覆盖点击、Generate/Remix 等交互路径。
- 该门禁适用于 V2 分支开发全程（每次合并到 V2 主线前建议检查一次），也是 V2 → Production 整体替换前的最后一道门禁。

---

## 13. V0 vs V2 评测方案

### 13.1 正式对比范围

正式对比只需要：

```
V0（Production main）  vs.  V2（新内部修复分支）
```

不要求把内部消融的各个变体（如"只开评分机制不开降权名单""只开方向1/2不开方向3/4/5"等）都实现为正式运行时版本对外发布。内部为了分析评分器和噪声降权各自的贡献，可以通过独立 commit、临时配置、离线脚本、本地评测运行完成消融——**不重新引入逐项 Feature Flag**（呼应第 2.4 节会议决定）。

### 13.2 采集方式必须一致 `[会前 Design 已披露的方法学局限，本次要求修正]`

会前 Design 明确披露过 V0/V1 历史对比中存在的采集方式不一致问题：

```
Production（V0）：Playwright 浏览器实际导航采集
Candidate（V1）：Node.js in-process harness 直接调用搜索库（不经过浏览器）
```

这一传输/执行路径不一致的问题**必须在 V0 vs V2 的正式评测中修正**。V0 与 V2 必须使用：

- 同一采集工具；
- 同一页面或调用路径；
- 同一 Catalog；
- 同一 Query 集合（326 条 Easy Query Benchmark v2 + 68 条 Hard Query）；
- 同一模型（如涉及 LLM 改写/判分）；
- 同一 Prompt；
- 同一阈值（如 `LOW_RESULT_THRESHOLD`）；
- 同一缓存策略；
- 同一评测 Rubric（Top-5 加权相关性，rubric-v1.1）。

具体采用浏览器导航还是 in-process harness 待工程阶段确认，但**两侧必须选择同一种**，不能像 V0/V1 历史对比那样各用一种。

---

## 14. 成功门禁

以下门禁适用于 V2 相对 V0 的评测判定，`V3 相对 V2` 的门禁待 V3 阶段单独制定（第 17 节）。

- 4 条 Rewrite 净负面 Case（V125/V127/V153/V271）全部修复——既有已定位案例，非 proposed；
- V2 零结果率不得高于 V0；
- PASS 率不能下降（相对 V0）；
- FAIL 率不能上升（相对 V0）；
- 不出现新的 full-catalog flooding（对应 V268/V032/V058/V154/V078 等历史模式，V2 不能重现）；
- 高频噪声模板占据 Top Results 的情况明显减少（可用第 11.2 节的 rank_before/after_scorer 和 Top-3/Top-5 出现次数衡量）；
- 326 条 Easy Query 不能被针对 68 条 Hard Query 的优化所伤害；
- 68 条 Hard Query 不出现新的严重回归；
- LLM rewriter、multi-path retrieval、L2、多段落等现有功能正常（第 12 节门禁）；
- build / test / TypeScript 检查通过；
- 新版本必须有明确净改善，**不能再次以零结果或 FAIL 增加换取小幅均分提升**（即不能重蹈 V1 的模式）。

**关于"显著优于 main prod"**：会议没有确认固定的 8%、10% 等百分点门槛，本文档不自行写死这类数值。"显著优于 main prod"在本阶段应理解为：配对评测存在正向统计证据（如 McNemar/Wilcoxon/paired bootstrap）+ 产品质量改善可感知（噪声模板压制、净负面 case 修复等定性证据）+ 不通过增加零结果或严重回归换取。具体数值门槛留待首轮 V2 实验产出数据后，与管理层确认。

---

## 15. 开发与提交建议 `[会议决定，替代会前 Design 中的逐项 Feature Flag 要求]`

- 从锁定的 Production main commit 新建一个干净的 V2 分支；不直接在 main 分支上开发。
- 方向 1、2、3、4、5、6、7 相关改动在 V2 分支上以**独立 commit** 方式提交，便于 Code Review、定位回归、必要时单独 revert。
- **不为每项改动分别构建正式运行时 Feature Flag**——会前 Design 第 6 节"每项均挂独立 Feature Flag，默认可单独关闭并回退"的表述是会前要求，已被本次会议修改，不再作为最终要求。
- 内部消融（例如验证评分机制单独的贡献、验证降权名单单独的贡献）通过独立 commit、临时配置文件或离线评测脚本完成，不要求上线时保留这些开关。
- 整体替换 Production 是被认可的上线方式，不强制要求逐项灰度。
- 上线后如出现严重问题，允许整体回滚部署或 revert PR；不要求"必须通过 runtime flag 回滚每一项"。
- 评分机制的权重等参数建议集中配置在单一位置（第 9.2 节），便于后续统一调整，而不是分散在各处硬编码。

---

## 16. 交付物

本阶段（V2 开发与评测周期）预期交付物：

- V2 开发分支（从 Production main 分叉，独立 commit 序列）；
- 统一相关性评分机制的设计说明与实现（第 9、10 节落地）；
- 方向 7 根因调查报告（Query→Result Trace，第 11.1 节）+ 短期降权规则清单（如需要）+ 长期方案设计说明；
- 现有功能回归检查清单及验证结果（第 12 节）；
- V0 vs V2 统一采集方式的评测报告（326 条 Easy Query + 68 条 Hard Query，第 13 节）；
- 成功门禁达成情况汇总（第 14 节）；
- 若门禁通过：整体替换 Production 的上线建议；若未通过：明确列出未达标项和下一步计划。

以上交付物均为**本阶段待产出**，本文档本身不包含以上任何一项的实际执行结果。

---

## 17. V3：Hybrid Search / HyperResearch 边界 `[老板反馈：当前先不做；会议：移到V3]`

本节只保留边界说明，不展开完整实现细节（完整 Hybrid 设计参考既有 `HYBRID_SEARCH_FLOW_2026-07-17.md` 等历史文档，本文档不重复展开）。

- V3 = 锁定并验证通过的 V2 + Hybrid Search / HyperResearch；
- 不建立在旧 Candidate（V1）上；
- Hybrid 只解决真实的 Catalog Gap 和低置信内部结果，**不允许掩盖 V2 应修复但未修复的内部排序/改写/Matching 问题**；
- V2 和 V3 必须分别评测，不能用 V3 的整体改善掩盖 V2 阶段遗留的内部问题；
- 正式接入、联调和评测必须等 V2 基线锁定之后，设计工作（数据结构、埋点方案、供应商合规评估）可以与 V2 部分并行；
- 当前阶段（V2）不做任何 Hybrid / HyperResearch 相关的代码接入。

---

## 18. 未决问题与明确不做的断言

### 18.1 未决问题（UNKNOWN / 待确认）

- Production main 具体的分叉 commit SHA：UNKNOWN，需在 V2 分支创建时由工程记录；
- 评分机制各维度的具体权重：UNKNOWN，待在代表案例上校准，proposed 阶段暂不写死；
- V0 vs V2 统一采集方式具体选用浏览器导航还是 in-process harness：UNKNOWN，待工程阶段确认，但两侧必须一致；
- "L2 层级内容"在当前代码结构中的具体指代：UNKNOWN，需结合现有页面组件结构确认；
- 现有打分逻辑是否已融合 title+tags+category 多字段支持：UNKNOWN，需逐行核实；
- "显著优于 main prod"的具体数值门槛：待首轮 V2 实验产出数据后与管理层确认，本文档不预先设定；
- 短期降权名单的具体覆盖范围和规则数量：待 11.1 根因调查产出后确定；
- 中英文分词/别名扩展路径的统一：沿用会前 Design 标注为 P2，本次会议未讨论，维持独立评估工作量的结论。

### 18.2 本文档明确不做的断言

- 不声称 V2 分支已创建；
- 不声称方向 1—7 或统一评分机制已实现；
- 不声称已重新运行 326 条或 68 条查询评测；
- 不声称已提交 commit、已 push、已创建 PR；
- 不声称 Hybrid Search / HyperResearch 已接入或已设计完整实现细节；
- 不声称候选分支（V1）已合并、已上线，也不声称 V1 会在未来以任何形式整体合并；
- 不把"有结果"等同于"相关"，也不把 FAIL 等同于"零结果"；
- 不把自动化/LLM 辅助的相关性判断当作人工真值——现有评测均由同一套 rubric、同一评测人执行，非双盲、无 inter-rater reliability 检验；
- 不从离线相关性评测中得出关于 CTR 或生成转化率的结论。
