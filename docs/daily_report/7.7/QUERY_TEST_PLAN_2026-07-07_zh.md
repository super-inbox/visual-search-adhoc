# Query Test Plan 报告 — 2026-07-07

_范围：仅完成 Curify 搜索回测的方案设计 + 第一批 gold test set 筛选。**本轮没有运行任何 Curify 搜索**，未跑 recall/filtering eval，未修改 curify-frontend 或任何生产代码，未做 ranking 优化。_

> 路径说明：任务中提到的源文件路径为 `docs/daily_report/7.7/05_high_signal_niche_query_candidates_500_2026-07-07.csv`，经核实该文件在磁盘上的当前实际路径为 `docs/daily_report/7.7/04_high_signal_niche_query_candidates_500_2026-07-07.csv`（此前 `04_..._v1_...csv` 127条版本已被移除，序号整体前移一位）。内容与用户描述的 504 条完全一致，本报告统一使用实际路径。

---

## 1. Step 1：504 条候选统计

| 维度 | 分布 |
|---|---|
| **总数** | 504 |
| **primary_scene** | 文创 142 / 品牌 129 / 营销电商 128 / 教育 105 |
| **priority** | P1 288 / P2 110 / P0 106 |
| **confidence** | medium 258 / low 242 / high 4 |
| **keep_or_review** | keep 337 / review 167 |
| **priority=P0 且 keep_or_review=keep** | **105 条** |

P0&keep 的 105 条内部分布：品牌 32 / 教育 27 / 营销电商 26 / 文创 20；confidence 分布 medium 91 / low 10 / high 4。

---

## 2. Step 2：测试指标设计

### 2.1 后续正式回测需要记录的字段

| 字段 | 说明 |
|---|---|
| `query` | 测试的 query 原文 |
| `primary_scene` | 场景标签，沿用候选库 |
| `planned_test_type` | 沿用 gold set 的预判类型（recall/filtering/both/content_gap），用于事后对比"预判是否准确" |
| `expected_content_type` | 预期内容形态，用于判断返回结果是否匹配格式预期 |
| `top_results_count` | 实际返回结果总数（建议统一看前 10 或前 20，需先固定 N 值再开始测试，避免不同 query 口径不一致） |
| `relevant_results_count` | 人工判断为"相关"的结果数量 |
| `irrelevant_results_count` | 人工判断为"明显不相关"的结果数量 |
| `recall_status` | PASS / WARN / FAIL（判断标准见 2.2） |
| `filtering_status` | PASS / WARN / FAIL（判断标准见 2.3） |
| `content_gap` | yes / no / unclear（判断方法见 2.5） |
| `issue_type` | recall_gap / filtering_issue / content_gap / no_issue（归因结论，见 2.5） |
| `alt_query_tried` | 为判断 content_gap 而尝试的替代/上位/翻译 query，记录具体尝试了什么，便于复现 |
| `evidence_note` | 具体观察证据，如"前3条是电商主图但风格是英文snack而非国货美妆"这类可复核的描述 |
| `tested_by` / `test_date` | 测试人/日期，便于追溯 |

### 2.2 recall 怎么判断

**定义**：在返回结果的前 N 名（建议统一 N=10）中，是否出现了满足 `expected_content_type` 和 query 核心意图的相关内容。

- **PASS**：前10名中有 ≥3 条高度相关结果，能覆盖 `expected_content_type` 预期的形态。
- **WARN**：前10名中只有 1-2 条勉强相关，或相关结果排名靠后（第7-10名才出现）——说明内容可能存在但匹配/召回较弱。
- **FAIL**：前10名中 0 条相关结果。

**注意**：FAIL 不等于"内容缺口"，只代表"这次搜索没召回到"，具体归因需要走 2.5 的判断流程。

### 2.3 filtering 怎么判断

**定义**：返回结果中"明显不应该出现"的内容占比与错误类型。

- **PASS**：不相关结果占比低（<20%），且没有出现严重的语义误判（比如黑话被按字面意思错误匹配，如"谷子店"被匹配成农产品谷物）。
- **WARN**：不相关结果占比中等（20%-50%），存在几条明显跑题的结果，但不占主流。
- **FAIL**：不相关结果占多数（>50%），或出现"语义完全错位"的严重误判（比如"dress to impress historical royalty"被理解成职场穿搭建议而非 Roblox 游戏梗），这种情况即使 recall 名义上有结果也应判 FAIL。

### 2.4 为什么本阶段不优先测 ranking

1. **前置依赖关系**：ranking 优化的对象是"在一批基本相关的结果里调整先后顺序"。如果 recall 本身是 FAIL（压根没召回相关内容）或 filtering 是 FAIL（结果里大半是垃圾），此时讨论"第1条和第3条谁该排前面"没有意义——候选池质量不过关，排序无从谈起。
2. **评估成本不对等**：ranking 评估需要细粒度的分级相关性打分（而不是 recall/filtering 这种相关/不相关的二元判断）和位置加权指标（如 NDCG），标注成本显著更高。在还没搞清楚 Curify 基础召回/过滤能力之前投入这个成本，性价比低。
3. **符合本轮任务边界**：本轮明确要求聚焦 recall 和 filtering，ranking 是后续阶段的事，不在本轮范围内。

### 2.5 如何判断是"内容缺口"还是"召回问题"

这是最容易被误判的一步，必须走一套交叉验证流程，不能仅凭一次搜索结果为空就下结论：

1. **第一步：原始 query 测试**，记录 recall_status（如为 FAIL 或 WARN，进入下一步；如为 PASS，直接判定 `content_gap=no`）。
2. **第二步：替代 query 交叉验证**，至少尝试以下 2-3 种替代方式重新搜索：
   - **上位词泛化**：把具体细分词换成更宽泛的上位词（如把"K-beauty glass skin brand launch visual"换成"skincare brand poster"或"护肤品海报"）
   - **中英互译**：中文黑话换英文直译或反过来（如"谷子店"→"anime merch shop"）
   - **拆解为基础词组合**：复用 `06_simple_head_term_seed_bank_2026-07-07.csv` 里的 head term，把复合 query 拆成更简单的组成部分分别测（如"农夫市集酸种烘焙品牌套装"拆成"烘焙"+"品牌"分别测）
3. **归因判断**：
   - 替代 query 能找到明显相关内容 → 说明内容其实存在，只是原始 query 没匹配到 → **`content_gap=no`，`issue_type=recall_gap`**（这是搜索/召回算法问题，应该推动 query 理解/同义词映射优化）
   - 替代 query（包括最宽泛的上位词）依然搜不到任何相关内容 → **`content_gap=yes`，`issue_type=content_gap`**（这是内容库供给问题，应该推动内容采购/生成，而不是搜索算法调优）
   - 替代 query 只能找到很弱/勉强相关的结果 → **`content_gap=unclear`**，需要人工复核或等内容库更新后重测，不要武断下结论
4. 如果 filtering_status 是 WARN/FAIL（不管 recall 如何）→ 单独标记 `issue_type=filtering_issue`，这类问题的解决方向是精排/意图消歧，与 content_gap 无关，两者可以在同一条 query 上同时成立。

---

## 3. Step 3：第一批 Gold Test Set 筛选

**输出文件**：`docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv`（**68 条**，落在 50-80 目标区间内）

### 3.1 为什么要先筛 50-80 条，而不是测全部 504 条

- **504 条一次性全测的成本过高**：按 2.1 的记录字段，每条 query 至少需要人工看 10-20 条搜索结果、判断相关性、必要时再跑 2-3 条替代 query 做 content_gap 交叉验证——504 条全测意味着上千次人工判断，在还没验证这套测试方法本身是否可靠之前，这个投入不合理。
- **先小规模验证方法论，再决定是否扩大**：50-80 条足够覆盖四大场景、覆盖不同 `query_style`、覆盖不同的压力测试类型（黑话/歧义/专有名词/内容缺口疑似），如果这批测试暴露的问题模式和预判基本吻合，说明整套"用 priority/confidence/niche_signal 预判风险"的方法论是有效的，再决定是否值得把 504 条全部测完；如果预判和实测差异很大，也能及时调整筛选标准，避免用错误的方法论批量测试浪费更多成本。
- **先测高确定性、高优先级的子集**：P0&keep 是候选库里"最值得优先验证"的子集（105条），从中精选出规模适中、场景均衡、子领域分散的一批，能在最小成本下获得最大信息量。

### 3.2 筛选标准

1. **主池**：从 `priority=P0` 且 `keep_or_review=keep` 的 105 条候选中选取（占本批次 64/68 条）。
2. **子领域去重复限**：同一 `subdomain` 最多选 5 条，避免某个子领域（如"教师资源黑话"或"跨境电商metadata"）因为候选数量多而挤占过多测试配额，保证子领域覆盖的广度而不是深度堆叠。
3. **confidence 优先级**：4 条 high confidence 全部入选；medium confidence（91条可选）作为主力来源；少量 low confidence 但仍属于 P0&keep 的条目（7条）保留，因为它们本身往往就是黑话/歧义程度最高的样本。
4. **四大场景均要覆盖**，按各场景在 P0&keep 池中的体量分配名额（品牌18/营销电商17/教育16/文创13），确保没有场景被边缘化。
5. **人工补选 4 条"边界压力测试"样本**（不在主池选择规则内，单独补入）：
   - `sub tub emergency lesson plan folder cover`（教育，P1/low/review）
   - `宠物殡葬服务品牌视觉设计`（品牌，P2/low/review）
   - `亚马逊评论截图水印素材`（营销电商，P2/low/review）
   - `谷圈应援色贴纸设计`（文创，P1/low/review）

   这 4 条优先级和 confidence 都不高，之所以刻意补选，是因为它们是 504 条里"信号最极端"的边界案例（要么是完全冷门的服务品类，要么是圈层黑话，要么是非常规内容格式），专门用来测试"content_gap vs recall_gap"判断方法论在极端情况下是否依然成立——如果连这种查询 Curify 都有响应，说明底层召回能力比预期强；如果这种查询连替代 query 都测不出内容，则是内容库覆盖率下限的真实写照。这类样本不追求"测出好结果"，追求的是撑开测试方法论的边界。
6. **明确排除**：纯大词（如"logo design"这类原 504 条里已经很少见，因为候选库本身就是围绕"高信号/小众/长尾"设计的）、以及与已入选样本高度重复的同类型 query（子领域封顶规则已经处理了这一点）。

### 3.3 四大场景分布（gold set 68 条）

| 场景 | 数量 |
|---|---|
| 品牌 | 19 |
| 营销电商 | 18 |
| 教育 | 17 |
| 文创 | 14 |

### 3.4 planned_test_type 分布

`planned_test_type` 是本轮新增的预判字段，基于每条 query 的 `subdomain`、`niche_signal`、`content_gap_hypothesis` 综合判断该条 query 最适合验证哪一类问题（并非机械套用模板文本，而是结合子领域的性质做了判断）：

| planned_test_type | 数量 | 典型子领域/场景 |
|---|---|---|
| `content_gap` | 24 | 4条人工补选边界样本 + gap假设语气强烈的品类（如殡葬服务、垂类品牌矩阵、DTC新消费成分黑话等） |
| `recall` | 18 | 二次元同人IP名、教师资源缩写术语(IEP/RTI)、ESL/特教/STEM专业术语——核心风险是"专有名词/缩写能不能被识别"，而非"结果会不会跑题" |
| `both` | 16 | 垂类品牌矩阵、小微本地品牌、网红IP品牌等——兼具"细分品类召回不足"和"容易与相邻大类混淆"两种风险 |
| `filtering` | 10 | 小红书运营、抖音直播电商类平台黑话——核心风险是字面义/黑话被误读导致召回错误类目内容 |

- 优先级：P0 64 / P1 2 / P2 2
- confidence：medium 57 / low 7 / high 4
- keep_or_review：keep 64 / review 4（4条为人工补选的边界样本）

---

## 4. 后续正式执行 Curify 搜索时的操作提醒

1. 统一固定 N=10（看前10条结果）作为 recall/filtering 判断的基准窗口，避免不同 query 之间因为看的结果数不同导致判断口径不一致。
2. 先测 `planned_test_type=recall` 和 `content_gap` 的两类（本批 42 条），因为这两类的判断相对独立、不需要太多主观相关性打分；再测 `filtering` 和 `both`（本批 26 条），这两类需要更细致的"是否跑题"判断。
3. 每条 query 测试完成后，立即按 2.5 的流程做 content_gap 交叉验证（不要等全部测完再回头补），避免遗忘具体测试上下文。
4. 测试结果记录到符合 2.1 字段设计的新 CSV 中（建议命名 `gold_query_test_results_<日期>.csv`），本轮不生成该文件，留给实际执行阶段。

---

## 5. 本轮明确不做的事情

- ❌ **未运行任何 Curify 搜索**（68 条 gold set 和其余 504-68=436 条候选均未测试）
- ❌ 未跑 recall/filtering eval，本文档只是方案设计，不含任何实测结果
- ❌ 未修改 `curify-frontend` 任何生产代码或搜索逻辑
- ❌ 未做 ranking 优化，也未设计 ranking 评估方案（明确说明了为什么暂缓，见 2.4）
- ❌ 未测试全部 504 条候选，仅完成 68 条第一批 gold test set 的筛选
- ❌ 未修改此前任何一轮的文件（Step 1-3D 全部文件），本轮只新增 `gold_query_test_set_2026-07-07.csv` 和本报告
