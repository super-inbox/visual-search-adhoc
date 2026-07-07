# Net-New Scenario Seed Queries 报告 — Step 3B（2026-07-07）

_范围：仅补充与原 58 query 不强绑定的 net-new seed query/carry 候选。未进行 Curify 搜索测试，未跑 recall/filtering 回测，未修改 curify-frontend 或任何生产代码，未做 ranking，未做大规模爬虫或新抓取。_

## 1. 为什么需要 Step 3B

上一轮（Step 1–3A）产出的 188 条 expanded query，全部是**对原 58 个 seed query 的长尾扩写**——即在"水果中文""电商详情图""葡萄酒"等已有 query 基础上，结合 Google/Bing/Pinterest/Canva 的真实标签做更具体化的改写（如"葡萄酒"→"葡萄酒品牌Logo设计"）。这种方法的局限是：**新 query 的语义空间完全被原 58 条的选题范围锁死**，如果原 58 条里某个场景本身就没有代表 query（如品牌），扩写再多也无法真正补上这个场景。

围绕「文创 / 品牌 / 营销电商 / 教育」四大**业务场景**把 query/carry 库做大，而不是让原 58 条变长。因此 Step 3B 的任务是：**不再以原 58 条为起点**，而是直接从四大场景的真实业务场景（行业垂类、内容形态、用户身份）出发，设计一批全新的 seed query。

## 2. 与上一轮 188 条 expanded query 的区别

| 维度 | 上一轮 Step 3A（188条） | 本轮 Step 3B（98条） |
|---|---|---|
| 起点 | 原 58 个 seed query | 四大场景的业务/行业场景定义，不绑定原 58 条 |
| 生成方式 | seed query + 该 query 的外部平台标签 → 具体化改写 | 场景定义 + 行业/内容形态知识 → 设计全新 query；部分辅以外部信号做延伸推断 |
| 与原 58 的关系 | 每条都能追溯到一个具体 seed | 完全独立，经查重与原 58 条、188 条 expanded query **零重复** |
| 品牌场景覆盖 | 仅 6 条（且全部是 secondary_scene 派生） | 30 条 primary_scene=品牌，系统覆盖咖啡/美妆/酒店/餐饮/初创/服装/宠物/科技/健身/酒类/烘焙/珠宝/法律/医美/儿童/环保/地产/婚庆/办公/播客/自媒体/App/花艺/旅行/音乐/公益/汽车/订阅盒/游戏共 30 个细分行业 |
| 定位 | query 库的"深度"扩展 | query 库的"广度"扩展 |

两轮结果是互补关系：188 条负责验证"已知 query 能否问得更细"，98 条负责验证"场景库本身够不够全"。后续回测应两者都覆盖，不能只用其中一份。

## 3. 四大场景各自补了什么

**输出文件**：`docs/daily_report/7.7/03_net_new_scenario_seed_queries_2026-07-07.csv`（98 条）

- **品牌（30条）**：小微/本地商户品牌（咖啡店、烘焙、花店、汽车美容）、垂类品牌（美妆/护肤、酒店、酒类、服装、珠宝、医美、健身）、B2B/机构品牌（律所、科技公司、公益组织、联合办公）、内容创作者品牌（自媒体 media kit、播客封面、音乐厂牌、游戏工作室）、事件/服务型品牌（婚礼摄影、旅行社、订阅盒）。
- **营销电商（24条）**：覆盖国内电商全场景（小红书种草图、抖音直播间背景图、微商朋友圈海报、淘宝直通车主图、拼多多详情页、双十一/618大促海报）与海外电商场景（Amazon infographic、TikTok shop banner、Shopify product page banner、跨境电商 listing 图），以及通用营销物料（会员卡、优惠券、展会背景板、邮件头图）。
- **教育（22条）**：在原 58 已验证的"识字卡/练习册"之外，补充学科教学海报类（乘法表、元素周期表、太阳系、历史时间轴、数学思维导图）、课堂管理类（行为图表、座位表、每日流程图）、新兴教育理念类（蒙氏教具、成长型思维、少儿编程、SEL情绪管理）。
- **文创（22条）**：聚焦"文创产品化"角度——博物馆伴手礼、文创包装、帆布包/书签/冰箱贴等周边、国潮插画、非遗纹样、传统节日贺卡、生肖吉祥物、戏曲脸谱、国风美妆包装，与原 58 的"角色IP插画"形成互补而非重复。

## 4. 为什么品牌场景需要单独补

上一轮报告已明确指出：**原始 58 query 中 primary_scene=品牌 的数量为 0**，expanded 之后也只有 6 条、且全部依附于其他 seed（葡萄酒、香薰、Met Gala、婚礼策划、1950s复古海报的 secondary_scene）。这说明品牌不是"扩写不够细"的问题，而是**选题源头上就没有品牌类 query**——继续在原 58 条基础上扩写，天花板就是 6 条左右。

因此本轮采用不同方法学：不从任何已有 query 出发，而是直接列举"什么样的商户/机构/个人会需要设计一套品牌视觉"，逐个行业垂类手工设计 query。同时对少量能追溯到已有信号的品牌 query（如 influencer personal brand kit 对应 Canva 模板标题 "modern beige influencer media kit"、children's brand mascot 对应原58强IP角色信号）标注为 `external_signal_inferred`，其余标注 `manual_scenario_design` 或 `scenario_gap_derived`，如实反映其证据强度低于 Step 3A 那种"平台标签直接改写"的做法——因此本轮品牌类 query 的 confidence 整体略低于上一轮，符合预期，不应被解读为不可靠。

## 5. 字段设计与统计

CSV 字段：`query, primary_scene, secondary_scene, source_type, source_signal, expected_content_type, user_intent, content_gap_hypothesis, priority, confidence, notes`

- `source_type` 四类含义：
  - `scenario_gap_derived`：直接从"该场景在现有 query 库中缺失"这一判断出发设计
  - `competitor_metadata_derived`：引用此前采集的 Canva 侧边栏导航类目（如 Logos / Card / Docs / Presentations），这些是本轮实际观察到的真实数据，不是新抓取
  - `external_signal_inferred`：从原 58 query 或上一轮 188 条的已有信号做行业/品类延伸推断（如从"葡萄酒品牌Logo"推广到"精酿啤酒品牌酒标"）
  - `manual_scenario_design`：纯粹基于行业/内容形态常识设计，没有具体外部数据点支撑，confidence 相应更保守

### 统计结果

- 总量：**98 条**（品牌 30 / 营销电商 24 / 教育 22 / 文创 22）
- Priority：P0 16 / P1 44 / P2 38
- Confidence：high 13 / medium 48 / low 37
- Source type：manual_scenario_design 74 / external_signal_inferred 17 / competitor_metadata_derived 4 / scenario_gap_derived 3
- 中英文 query 均有覆盖（本文件中含 CJK 字符的 query 45 条，英文 53 条）
- 与原 58 query、上一轮 188 条 expanded query **逐条查重，零重复**

## 6. 后续如何用于 recall/filtering 回测

1. **先测 P0**（16条，跨四个场景）：这批 query 都有相对明确的用户意图和内容形态假设，适合作为第一批 Curify recall 实测样本，验证"品牌类内容形态（brand kit / logo / mascot）"这种新内容类型 Curify 目前能否召回。
2. **按 source_type 分层看结果**：`competitor_metadata_derived` 和 `external_signal_inferred` 的两类（21条）有实际数据支撑，回测优先级和可信度应高于纯 `manual_scenario_design`；如果这两类回测效果差，说明 gap 是真实的，而不是本轮臆造的场景。
3. **品牌场景需要专门的 gap 分类法**：现有 `docs/search-evaluation/template-recall-audit-all-queries.md` 的根因分类（多token复数词干缺口/CJK同义词映射缺口/模板i18n描述缺口）是围绕已有内容类型设计的，品牌类 query 很可能会暴露一种新的根因——"内容形态本身缺失"（如 Curify 可能没有"brand kit""mascot design"这类多件套或角色化内容类型），回测时应留意这一新根因类别，不要生搬硬套旧分类。
4. **与 Step 3A 的 188 条合并使用**：建议后续统一维护一份"query 候选总表"（188 + 98 = 286 条），用同一份 gold eval 结构（参照 `docs/daily_report/6.17/multi-intent-eval-v0_副本.md`）标注 expected sub-intent，再统一送入 Curify 回测，避免分批测试导致口径不一致。

## 7. 本轮明确不做的事情

- ❌ 未在 Curify 上运行任何 query（含本轮 98 条）
- ❌ 未跑 recall/filtering 回测，未生成任何"Curify 结果好坏"的判断
- ❌ 未修改 `curify-frontend` 任何生产代码或搜索逻辑
- ❌ 未做 ranking/排序
- ❌ 未做大规模爬虫，未新抓取 Liblib/Pinterest 等任何外部数据；`competitor_metadata_derived`/`external_signal_inferred` 引用的信号均来自此前（Step 1–3A）已采集并保存在 `docs/external-signal-pilot/` 下的历史数据
- ❌ 未修改上一轮三个文件（`QUERY_EXPANSION_STEP1_3_2026-07-07_zh.md`、`01_original_58_query_scene_classification_2026-07-07.csv`、`02_expanded_from_58_query_candidates_2026-07-07.csv`），本轮只新增文件
