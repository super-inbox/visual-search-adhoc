# Easy Query Benchmark v2 根因分析报告（面向 Hybrid Search 规划）

日期：2026-07-17
数据来源：`easy_query_v2_relevance_evaluation.csv` / `easy_query_v2_top_results.csv` / `easy_query_v2_manual_review_queue.csv`
（326 条查询，7/16 采集，rubric-v1.1 锁定评分口径，与既往 300+ easy query 评测可比）

**说明**：本报告为纯分析性文档，不重新运行采集、不修改 query bank、不修改搜索代码。所有结论均来自对
既有评测结果（326 条 checkpoint + 独立相关性判定）的二次分析。

---

## 0. 总体结论摘要

| 指标 | 数值 |
|---|---:|
| 总查询数 | 326 |
| PASS | 82（25.2%） |
| PARTIAL | 111（34.0%） |
| FAIL | 133（40.8%） |
| 综合失败率（FAIL+PARTIAL） | 74.8% |
| 平均分 / 中位分 | 35.4 / 33.0 |
| 零结果查询 | 34（10.4%） |
| 触发 rewrite 的查询 | 196（60.1%，与 low_result 计数完全一致） |

四个场景的失败率（FAIL+PARTIAL 占比）从高到低：

| 场景 | N | PASS | PARTIAL | FAIL | 失败率 |
|---|---:|---:|---:|---:|---:|
| Creative / Cultural / Merch | 82 | 14 | 33 | 35 | 82.9% |
| Brand / Business Visual Assets | 82 | 18 | 38 | 26 | 78.0% |
| Marketing / Ecommerce | 82 | 24 | 24 | 34 | 70.7% |
| Education / Learning Material | 80 | 26 | 16 | 38 | 67.5% |

**关键发现**：Creative/Merch 场景失败率最高（82.9%），但 Education 场景 FAIL 绝对数最高（38条，且零结果
查询集中在此场景，16/34）。四个场景失败率均超过 65%，说明当前纯 token/关键词检索 + LLM rewrite 的架构
性短板是**跨场景的系统性问题**，而非某个场景独有。

---

## 1. 哪些查询类目 / 场景对 FAIL 和 PARTIAL 贡献最大

### 1.1 按细分类目（category）排序（失败率=1.0 的类目，即全军覆没）

| category | N | 说明 |
|---|---:|---|
| certificate | 8 | 证书类目录，几乎全部零结果或被无关内容淹没 |
| menu | 6 | 菜单，检索到的是"菜谱卡片"而非"菜单版式" |
| membership_card | 6 | 会员卡/积分卡/礼品卡，被通用 education-card / MBTI 模板淹没 |
| signage | 4 | 店招/门店招牌，与"手语教学"模板发生词义碰撞 |
| cup | 4 | 咖啡杯，与"World Cup"发生词义碰撞 |
| social_post | 4 | 社交媒体帖子，检索不到任何社媒版式内容 |
| advertisement | 4 | 广告，语义过于宽泛 |
| plush | 4 | 毛绒玩具，目录内几乎无对应模板 |
| toy / textbook / keychain / doll / logo / globe / coupon / business_card | 各 2 | 同样 100% 失败 |

高失败率（>0.75）的类目还包括：figure（92%）、flyer（90%）、collectible（85%）、product_box（83%）、
bottle（83%）、blind_box（83%）、merch_item（80%）、classroom_material（80%）、chart（79%）、
product_display（75%）、calendar（75%）。

**相对健康**的类目：flashcard（失败率 25%）、poster_specific（38%）——这两类是目录内容覆盖最充分、
模板命名与查询词高度重合的类目，说明**目录内容覆盖密度**是决定检索表现的第一变量。

### 1.2 按场景

四个场景失败率差距不大（67.5%–82.9%），但**失败的性质不同**：
- Creative/Merch：主要是"目录里确实缺少这类周边/收藏品模板"（潮玩、盲盒、拼图等）。
- Brand/Business：主要是"重写（rewrite）把查询带偏"，包裹类、标签类查询触发 rewrite 后经常返回
  上百甚至上千条结果，但相关率反而更低。
- Marketing/Ecommerce：会员卡/礼品卡集群 100% 失败，是本场景最大单一贡献源；另有多起 rewrite
  过度扩张导致的"淹没型"失败（如 unboxing photo 最终 1284 条结果，几乎全部不相关）。
- Education：零结果集中爆发（16/34 全局零结果落在本场景），多为证书、白板、显微镜、算盘、
  书签等目录里几乎不存在的实体教具。

---

## 2. 失败根因分类

我们对全部 244 条 FAIL/PARTIAL 记录，基于（a）result_count 是否为 0，（b）reason 文本中的关键信号
（"word collision""unrelated""flooding""adjacent"等），（c）rewrite_triggered 与最终 result_count
的关系，做了规则化的根因归类（一条查询只标注**主要**根因，多数失败案例实际上有多个叠加因素）：

| 根因类型 | 数量 | 占比 | 定义 |
|---|---:|---:|---|
| RETRIEVAL_RANKING（排序/召回问题） | 77 | 31.6% | 目录中可能存在相关内容，但高频"噪声模板"在排序中压过了它 |
| QUERY_UNDERSTANDING_REWRITE（查询理解/重写问题） | 71 | 29.1% | LLM rewrite 触发后偏离原始查询主体，或把结果集过度扩张到成百上千条 |
| CATALOG_GAP（目录内容缺口） | 67 | 27.5% | 目录里没有与查询对象匹配的模板族，包括全部 34 条零结果查询 |
| AMBIGUOUS_INTENT（意图歧义/词义碰撞） | 29 | 11.9% | 查询词本身有多个目录内含义，错误义项系统性压过正确义项 |

四个根因大致均分，但性质完全不同，需要不同的技术对策（见第 4 节候选集设计逻辑）。

### 2.1 CATALOG_GAP（目录缺口）—— 典型案例

- **完全缺口（34 条零结果查询）**：证书（证书/certificate/荣誉证书/achievement certificate/毕业证）、
  优惠券（优惠券/discount coupon）、白板（白板/whiteboard）、显微镜（microscope）、算盘对应的
  抽象数据（虽 abacus 有 1 条弱结果）、书签（书签，虽 bookmark 英文有极弱召回）、笔袋（pencil case，
  仅命中"AI dilemma case"纯词形碰撞）、毛绒玩具（毛绒玩具/plush 系列）、盲盒（盲盒/puzzle/积木/
  diorama 等）、烘焙包装、茶叶罐、饮料瓶、班级课程表、展会展架、直播预告横幅等。这些是目录中**确实
  没有对应模板族**的实体对象或文档类型。
- **近似缺口（有结果但对象/版式不匹配）**：如"菜单/menu"检索到的是"中式菜谱卡片"而非菜单版式；
  "教科书/textbook"检索到的是"历史人物教育海报"而非教科书封面/内页；"产品盒/product box"检索到的是
  文创周边包装 mockup 而非通用产品盒。这类失败**目录里有主题相关内容，但没有对应的具体版式**。

### 2.2 QUERY_UNDERSTANDING_REWRITE（重写问题）—— 典型案例

Rewrite 触发后经常大幅扩张结果集规模，但相关率不升反降，是本次评测中**最戏剧性的失败模式**：

| 查询 | result_count | 说明 |
|---|---:|---|
| drink bottle | 3134 | rewrite 后混入大量中式食谱卡片 |
| globe | 3205 | rewrite 导致命中一批"领袖人物 MBTI"卡片，与地球仪无关 |
| alphabet poster | 3034 | rewrite 命中化学反应图表/建筑/圣诞节等无关内容 |
| statue | 2748 | rewrite 后仅"自由女神像"1 条直接相关，其余为西游记人物卡 |
| 艺术微喷/art print | 2762/193 | rewrite 把"艺术微喷"这一具体印刷品类型泛化成宽泛的"艺术"检索 |
| bobblehead | 1777 | rewrite 后仍未命中摇头公仔专属模板 |
| unboxing photo | 1284 | rewrite 命中"世界杯球队海报""人像精修蓝图"等无关模板 |
| plush pillow | 819 | rewrite 后被无关内容淹没 |
| membership card / loyalty card | 838/838 | rewrite 未能锁定"会员卡"这一具体版式 |

这类失败的共同特征：rewrite 生成的 2–3 个改写候选**丢失了原始查询的核心名词约束**（如"地球仪"被
泛化为"地球/世界"相关的宽泛检索路径），导致检索路径数量（executedPathCount/usedPathsCount）和最终
结果集急剧膨胀，但膨胀出来的结果与原始意图无关。

### 2.3 RETRIEVAL_RANKING（排序/召回问题）—— 高频"噪声模板"

对全部 244 条 FAIL/PARTIAL 查询的 top-5 结果做模板级别统计，出现频率最高的"噪声模板"（即在不相关
结果中反复出现、挤占相关内容排位的模板）：

| 模板 | 在 FAIL/PARTIAL 结果中出现次数 |
|---|---:|
| template-food-photo-doodle-sticker-overlay（食物涂鸦贴纸） | 70 |
| template-ip-creative-cultural-goods-mockup-set（文创周边 mockup） | 65 |
| template-fashion-ecommerce（时尚电商) | 36 |
| template-brand-identity-moodboard-visual-system-poster（品牌 VI 展板） | 28 |
| template-product-theme-promotional-poster（促销海报） | 28 |
| template-word-scene（双语情景词汇） | 25 |
| template-recipe（中式菜谱） | 22 |
| template-education-card（通用教育卡片） | 21 |
| template-book-series（西游记书系列） | 18 |
| template-vocabulary（词汇卡） | 18 |

这些模板在目录中**数量多、标签覆盖广**，容易在宽松匹配（relaxed tier）阶段被召回，但对具体查询而言
往往是弱相关或不相关。这是纯 token 检索 + tag 匹配架构的结构性弱点：**高频广谱模板系统性挤占低频
精准模板的排位**，属于排序/重排（reranking）问题，而非目录缺口或 rewrite 问题——因为这类失败中很多
查询根本没有触发 rewrite（如 V009 吉祥物、V013 贴纸、V084 logo、V165 横幅等），说明问题出在基础检索
排序本身。

### 2.4 AMBIGUOUS_INTENT（词义碰撞）—— 典型案例

查询词在目录标签体系中存在多个"合法但不同"的义项，且错误义项因模板数量/标签权重占优而系统性压过
正确义项：

| 查询 | 碰撞双方 |
|---|---|
| 咖啡杯 / coffee cup | 咖啡杯 vs "World Cup"（世界杯球队海报系列） |
| 标志 / logo | 品牌标志 vs "landmark"地标建筑 |
| 店招 / storefront sign | 店铺招牌 vs "手语教学"（sign language） |
| charm | 首饰吊坠 vs "charming character"（迷人角色） |
| 迷你手办 / mini figure | 迷你手办 vs "city miniature"城市微缩景观 |
| black friday banner | 黑五促销 vs "Marvel Black Widow"（黑寡妇，"black"词形碰撞） |
| 礼品卡 / gift card | 礼品卡 vs 通用"education-card"/"flashcard"模板命名碰撞 |
| 报告单 / report card | 学生成绩单 vs 通用科学教育卡片（同样是模板命名碰撞，非查询本身歧义） |
| 元素周期表 / periodic table | 周期表 vs "Breaking Bad MBTI"人物卡（无实际词形关联，纯标签共现巧合） |
| 贴纸奖励表 | 奖励表贴纸 vs "食物涂鸦贴纸"（"贴纸"泛化碰撞） |

这类失败**不是排序算法的锅**，而是查询词/模板标签体系本身存在语义歧义，需要在检索前做**意图判别**
（而非仅靠关键词匹配）才能解决。

---

## 3. 四类重点查询的专项分析

### 3.1 设计相关查询（design-related：label / package / logo / banner / poster_specific / product_box /
business_card / product_display / catalog / signage）

- 样本量：112，失败率 68%（PASS 36 / PARTIAL 42 / FAIL 34）。
- 是四个专项分类中**表现相对较好**的一类，因为目录内本身就以"设计交付物类模板"（促销海报、品牌 VI
  展板、产品标签）为主力内容，命中率天然更高。
- 但集中暴露出**QUERY_UNDERSTANDING_REWRITE 问题最严重**：包装（package）、标签（label）、月饼礼盒、
  蛋糕盒等具体包装/礼盒查询，rewrite 后结果集从个位数暴涨到几十上百，相关率不升反降（如 chocolate box
  166 条、wine label 286 条、bakery package 297 条）。
- 典型词义碰撞：标志/logo→landmark，咖啡杯/coffee cup→World Cup，店招→手语教学。
- **对 Hybrid Search 的启示**：这一类是 rewrite 治理（收紧改写候选与原查询主体的绑定约束）最值得优先
  投入的场景，因为目录内容本身够用，问题主要出在检索路径生成阶段。

### 3.2 教学材料查询（teaching material：flashcard / worksheet / classroom_material / textbook /
certificate / calendar）

- 样本量：46，失败率 67%（PASS 15 / PARTIAL 10 / FAIL 21）。
- 内部分化极大：flashcard 子类几乎全部 PASS（识字卡、字母卡、单词卡、拼读卡、拼写卡均为模板库中
  数量最多、命名最直接的一类），但 certificate（证书）子类 8 条查询中 7 条 FAIL、其余目录中**完全
  没有证书类模板**（体现为本场景 16 条零结果中证书相关占了 5 条：证书/certificate/成绩单/荣誉证书/
  achievement certificate/毕业证，实际 6 条）。
- classroom_material 子类（黑板/白板/显微镜/算盘）同样是目录空白区——这些是"实体教具"，与目录
  以海报/卡片/信息图为主的内容形态本质不匹配。
- **对 Hybrid Search 的启示**：教学材料查询的失败高度两极化——flashcard/worksheet 这类"版式类"内容
  目录覆盖好，几乎不需要额外投入；certificate/classroom_material 这类"实体教具/文档类"内容是纯粹的
  CATALOG_GAP，rewrite 无法解决，是 Google 图片兜底最具性价比的场景。

### 3.3 绘图/图解类查询（drawing/illustration，映射为 diagram / chart / map / globe 四个子类目，本次
benchmark 无独立"手绘/简笔画"类目，故以图解、图表、地图、地球仪作为该语义簇的代表）

- 样本量：24，失败率 71%（PASS 7 / PARTIAL 4 / FAIL 13）。
- chart 子类（14 条）失败率高达 79%，且几乎全部是**词义碰撞或噪声模板挤占**：元素周期表被"绝命毒师
  MBTI 人物卡"挤占（纯标签巧合，无语义关联）；数字表被"时尚礼服设计图"挤占（"表"字在目录标签体系中
  同时对应"时间表""设计图纸"两种义项）；人体图解（3 条弱结果但恰好全部相关）与解剖图对比图
  （anatomy chart，被"建筑信息图"的"anatomy"标签误伤）形成鲜明对比。
- globe（地球仪）是本次评测**rewrite 扩张最失控**的案例之一：中文"地球仪"零结果，英文"globe"触发
  rewrite 后暴涨到 3205 条结果，但全部与地球仪无关（命中"领袖人物 MBTI"系列）。
- world map / 世界地图 表现优异（PASS，100 分），说明"地图"这一具体版式在目录内覆盖良好，问题集中在
  chart/globe 这两个更抽象或更冷门的子类目。
- **对 Hybrid Search 的启示**：这一簇是 RETRIEVAL_RANKING 和 AMBIGUOUS_INTENT 两种问题的重灾区，且
  普遍不涉及真正的目录缺口（世界地图、人体图解证明目录里有大量合格的信息图/图解内容）——核心问题是
  **标签体系的语义精度不足**，导致宽泛标签（如"anatomy""infographic""chart"）把明显不相关的内容拉
  进候选池。这是重排序（reranking）模型最适合发力的地方。

### 3.4 玩具/周边/创意商品查询（toy/merch/creative product：figure / toy / plush / blind_box / doll /
mascot / character / keychain / collectible / merch_item / sticker）

- 样本量：86，失败率 83%——是四个专项分类中**表现最差**的一类，也是 creative_merch 场景失败率
  全场景最高（82.9%）的主因。
- 目录内容与真实电商周边品类（手办、盲盒、毛绒玩具、亚克力立牌、徽章、挂件、马克杯等）之间存在
  **系统性错配**：目录里的"周边"内容以`template-ip-creative-cultural-goods-mockup-set`（文创周边
  mockup 展示图）为主，是场景化的整体产品陈列图，而不是单一品类的产品摄影图，导致几乎所有具体品类
  查询（钥匙扣、徽章、冰箱贴、马克杯等）只能拿到"泛周边 mockup"的弱相关（PARTIAL）而非精准命中。
- 一个值得注意的**中英文不对称案例**：吉祥物（中文，FAIL，命中器官健康信息图）vs mascot（英文，
  PASS，满分）——同一概念在中英文下命中完全不同的检索路径，说明中文分词/别名扩展在这一品类上落后于
  英文路径，这不是目录缺口而是**中文查询理解链路的欠缺**。
- **对 Hybrid Search 的启示**：这是全部四个场景中最需要"多技术手段组合"的一类——真正缺失的品类
  （毛绒玩具、盲盒、拼图、积木、场景模型摆件）需要 Google 图片兜底；"泛周边 mockup 淹没具体品类"
  需要重排序；中英文不对称案例需要改进中文查询理解/别名扩展。

---

## 4. Hybrid Search 候选集设计逻辑

详见配套文件 `HYBRID_SEARCH_CORE80_CANDIDATE_SET.csv`（80 条候选查询明细）与
`HYBRID_SEARCH_QUERY_SELECTION_RATIONALE.md`（英文，含选取方法论与逐条建议的完整说明）。

候选集按 4 个场景各分配 20 条（Education 因零结果高度集中，零结果配额略高于其余三场景），每个场景内部
包含：
1. **零结果查询**（21 条）——验证 Hybrid Search / Google 图片兜底能否在"完全无结果"场景产出可用候选；
2. **低结果查询**（20 条，最终结果数 1–4 条）——验证能否提升召回深度与置信度；
3. **代表性 FAIL/PARTIAL 查询**（27 条）——覆盖四类根因（目录缺口/词义碰撞/重写偏移/排序问题）与
   四个专项簇（设计/教学材料/图解/玩具周边），包含若干"戏剧性淹没案例"（如 globe 3205 条、drink bottle
   3134 条、statue 2748 条）作为 Hybrid Search 收益上限的压力测试样本；
4. **健康基线查询**（12 条，当前 PASS）——作为回归防护，确保 Hybrid Search 上线不会破坏当前已经工作
   良好的查询路径。

每条候选查询均标注：预期失败模式、Google 图片兜底是否可能有帮助、LLM rewrite 是否可能有帮助——判断
依据统一遵循以下决策框架：

| 根因 | Google 图片兜底 | LLM rewrite 改进 |
|---|---|---|
| CATALOG_GAP（目录缺口） | **是**——真实世界常见实物/文档，外部图片源覆盖充分 | **否**——重写无法凭空生成目录里不存在的模板 |
| AMBIGUOUS_INTENT（词义碰撞） | **部分**——需先做意图判别，否则外部检索继承同样歧义 | **是**——需要判别式改写而非泛化式改写 |
| QUERY_UNDERSTANDING_REWRITE（重写偏移） | **否**——问题在内部重写环节本身，外部兜底不对症 | **是**——需要收紧重写与原查询主体的绑定约束 |
| RETRIEVAL_RANKING（排序问题） | **否**——目录内容可能已存在，缺的是排序能力 | **否**——多数此类查询未触发 rewrite 或 rewrite 未改变结果 |

---

## 5. 数据完整性声明

- 本报告基于 `easy_query_v2_relevance_evaluation.csv`（326 行）、`easy_query_v2_top_results.csv`
  （1343 行）、`easy_query_v2_manual_review_queue.csv`（244 行）的二次分析，未重新采集任何数据。
- 根因分类采用规则化启发式方法（见第 2 节），基于评测阶段记录的独立相关性判定文本（`reason` 字段）
  与量化信号（result_count / rewrite_triggered / label）联合判断，单条查询仅标注**主要**根因，
  存在归类边界模糊的情况（如某些查询同时具备词义碰撞与排序问题特征），已在正文中说明。
- 未修改 `easy_query_bank_v2_2026-07-16.csv`、未修改任何搜索代码、未重新运行采集或评测流程。
