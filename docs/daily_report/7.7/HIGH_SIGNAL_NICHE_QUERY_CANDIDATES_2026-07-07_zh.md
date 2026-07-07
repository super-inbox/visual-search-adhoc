# High-Signal / Niche / Stress-Test Query Candidates 报告 — Step 3C（2026-07-07）

_范围：仅生成高信号/小众/长尾的 query 候选，用于后续 Curify 搜索压力测试输入准备。未进行 Curify 搜索测试，未跑 recall/filtering 回测，未修改 curify-frontend 或任何生产代码，未做 ranking，未做大规模新爬虫。_

## 1. 为什么 Step 3C 是必要的

Step 3B 的 98 条 net-new query 解决了"品牌场景选题空白"的问题，但复盘发现它们整体偏**工整分类词库**——大量条目是"行业 + 设计类型"的标准组合（如 `coffee shop brand logo`、`skincare brand visual identity`），这类 query 更像是给场景做穷举分类，而不是真实用户/竞品平台上会出现的搜索词。

工整分类词库有一个结构性问题：它测不出 Curify 真正的搜索短板。标准词组合通常语义清晰、无歧义，就算 Curify 做简单的关键词匹配也能勉强给出结果，无法暴露"多语言混合""行业黑话""风格修饰词""意图歧义""内容形态罕见"这些真实会让搜索系统失灵的场景。我们要的不是更多分类词，而是**能打到竞品流量高地、真实反映用户/运营者实际怎么搜的 query**——这正是 Step 3C 要补的。

## 2. 和 Step 3A / Step 3B 的区别

| 维度 | Step 3A（188条） | Step 3B（98条） | Step 3C（127条，本轮） |
|---|---|---|---|
| 起点 | 原 58 query 的标签改写 | 四大场景的行业/机构穷举 | 竞品平台真实内容形态 + 圈层黑话 + 趋势热词 |
| 典型形态 | "水果中文"→"水果中文拼音识字卡" | "咖啡店品牌logo设计" | "谷子店品牌视觉设计"、"拼多多百亿补贴主图角标设计"、"Montessori butterfly life cycle 3 part cards" |
| 语言特征 | 沿用原 query 语种 | 中英文分布均衡，措辞规整 | 大量中英文混合在同一语境下出现的黑话/缩写（DTI、A+页面、IEP、九宫格） |
| 覆盖逻辑 | 深度（同一 query 问得更细） | 广度（场景穷举，行业齐全） | **信号强度**（是否是竞品真实高频/高转化内容，是否有具体行业实践支撑） |
| 目标 | 验证已知 query 能否问得更细 | 验证场景库是否够全 | 验证 Curify 在真实压力场景下的召回/过滤边界在哪里 |
| query 分布要求 | 每 seed 3-4 条，追求覆盖 | 四场景尽量均衡（各20+，品牌30+） | **不追求均衡**，文创36/品牌33/营销电商31/教育27，按信号密度自然分布 |

三轮是递进关系：3A 深挖已知，3B 补全场景骨架，3C 往骨架里灌真实、有杀伤力的压力测试内容。三份文件合并使用（58+188+98+127 = 471 条候选）才是完整的 query/carry 库雏形。

## 3. 为什么上一轮偏 baseline，本轮偏 stress-test

Step 3B 的方法学是"给定场景，穷举行业/内容类型的标准组合"，这个过程本质上是分类学练习，产出的 query 天然会收敛到语法工整、语义无歧义的形式——因为设计者（我）在按模板造句。这类 query 适合做**覆盖率基线**：验证 Curify 对"常见、明确"的品牌/营销/教育/文创需求是否有基本覆盖。

但真实用户/运营者的搜索输入是不规整的：会用平台黑话（"福袋""种草""九宫格"）、会中英混杂（"抖音团长带货海报"里"团长"是黑话、"A+页面"是英文缩写嵌入中文句子）、会用有时效性的网络热词（"brain rot""dopamine dressing""Gen Alpha slang"）、会有语义歧义（"dress to impress"字面是"穿得体面"，实际指 Roblox 游戏梗）。这些特征恰恰是搜索系统最容易出问题的地方——简单的关键词/向量匹配在这里会退化成"忽略修饰词、召回泛化结果"或"完全召回为0"。Step 3C 的每一条 query 都是刻意针对某一种失败模式设计的，因此天然偏"压力测试"而非"基线"。

## 4. 高信号 query 的筛选标准

本轮遵循以下几条筛选逻辑（对应 CSV 中 `likely_recall_challenge` / `likely_filtering_challenge` / `content_gap_hypothesis` 三个字段）：

1. **黑话/缩写优先**：query 里包含一个只有圈内人才懂的具体词（"谷子""团长""A+页面""IEP""sub tub""3 part cards"），测试 Curify 是否能理解术语而非字面匹配。
2. **风格修饰词优先于品类词**：如"低饱和""陶瓷感""新中式""quiet luxury"，测试 Curify 的标签体系里是否存在"风格/质感"这一维度，而不只是"品类/形态"。
3. **趋势热词的时效性**：如"brain rot""Gen Alpha slang""cold plunge wellness"，故意选近 1-2 年才流行起来的词，测试语料更新速度。
4. **意图歧义**：如"dress to impress"（穿搭建议 vs Roblox游戏梗）、"谷子店"（谷物店 vs 动漫周边店），测试字面匹配是否会导致完全错误的召回方向。
5. **跨圈层/跨IP组合**：如"Sanrio x Chiikawa crossover"、"赛博朋克国潮"、"MBTI+手账贴纸"，测试组合类需求是否会被简化为单一维度召回。
6. **具体到荒诞边界的冷门场景**：如"宠物殡葬服务品牌视觉设计""白牌代工厂品牌焕新"，故意测试覆盖率下限——如果这类内容也能有基本响应，说明 Curify 底层召回能力较强；如果连常见细分场景都测不出问题，再逐步收窄到更极端案例。
7. **可追溯到已有数据的信号优先标 `existing_external_data`**：本轮 12 条直接引用了 Step 1-3A 已采集的 Google/Bing/Pinterest 原始标签（如"吉伊卡哇 奇美拉""Astolfo, Fate"等具体信号），这些不是凭空编造，可信度更高；其余 113 条基于人工趋势/行业常识推断（`manual_trend_inference`），确定性天然更低，已体现在 confidence 字段上。

`keep_or_review` 字段是筛选结果的第一层判断：`keep`（67条）是我认为信号足够扎实、可以直接进入下一步小规模回测的；`review`（60条）是信号更冷门/更投机、建议人工复核后再决定是否保留的。

## 5. 各场景样例（每场景 8-10 条代表性 query）

### 文创（36条）
| Query | query_style | 为什么是好的压力测试 |
|---|---|---|
| genshin impact Furina fanart wallpaper 4k | Pinterest-like | 具体角色专有名词+分辨率规格，测试小众游戏IP的embedding覆盖 |
| dress to impress historical royalty outfit inspo | Pinterest-like | "DTI"字面义与Roblox游戏梗的双重语义，意图歧义压力测试 |
| blind box toy character sticker sheet | Pinterest-like | "sticker sheet"成套排版格式 vs 单张贴纸，内容形态区分测试 |
| 低饱和国风茶包装设计 | Liblib-like | 风格修饰词("低饱和")而非品类词，测试色彩风格过滤能力 |
| 汉服马面裙插画设计 | Xiaohongshu-like | 2023-24现象级流行的具体服装款式名，测试趋势对象词覆盖 |
| 谷子店品牌视觉设计 | Xiaohongshu-like | "谷子"是谐音黑话(goods)，与"谷物"字面义完全无关，极端歧义测试 |
| meme格式国风梗图模板 | Xiaohongshu-like | "梗图"格式(留白排版给文字) vs 完整插画，格式识别测试 |
| Chiikawa 奇美拉 同人壁纸 | Pinterest-like | 需理解IP内部剧情梗，深度粉丝向长尾测试 |
| 赛博朋克国潮插画海报 | Liblib-like | 跨文化风格叠加(西方赛博朋克+中式国潮)，组合召回测试 |
| Reverse 1999 aesthetic moodboard | Pinterest-like | 冷门二次元游戏名，测试"冷门IP召回是否为0" |

### 品牌（33条）
| Query | query_style | 为什么是好的压力测试 |
|---|---|---|
| Y2K chrome skincare launch poster | Pinterest-like | 年代风格词+质感词叠加，测试双重风格限定的匹配能力 |
| farmer's market sourdough bakery brand kit | Canva-template-like | 细分定位组合(农夫市集+酸种)，测试是否退化为泛化烘焙素材 |
| quiet luxury jewelry brand visual identity | Pinterest-like | "quiet"限定词容易被忽略，测试能否区分静奢 vs 传统炫耀式奢华 |
| 谷子店品牌视觉设计 | Xiaohongshu-like | 圈层黑话品牌命名，测试品牌类query的黑话理解能力 |
| 自然系香薰品牌视觉手册 | Xiaohongshu-like | 风格定位词+具体文档格式(视觉手册)组合 |
| 白牌代工厂品牌焕新设计 | ecommerce-ops | B2B供应链黑话，测试非C端场景的理解能力 |
| 预制菜品牌包装设计 | ecommerce-ops | 2023-24爆发的新兴品类黑话，测试语料时效性 |
| plant-based butcher brand packaging concept | Canva-template-like | 矛盾修辞式品类("植物基肉店")，测试语义理解而非关键词匹配 |
| 宠物殡葬服务品牌视觉设计 | mixed | 极冷门服务品类，测试覆盖率下限 |
| Korean cafe menu board template | Canva-template-like | 地域风格+具体物料格式组合

### 营销电商（31条）
| Query | query_style | 为什么是好的压力测试 |
|---|---|---|
| 小红书香薰产品种草图 | Xiaohongshu-like | "种草图"平台专属格式(场景真实感) vs 电商精修图，格式区分测试 |
| 拼多多百亿补贴主图角标设计 | ecommerce-ops | 平台专属促销活动名称+局部设计元素(角标)，双重具体化 |
| 亚马逊A+页面模块设计 | ecommerce-ops | 平台官方专属术语，测试对具体电商平台规范格式的理解 |
| 618预售海报 定金膨胀 | ecommerce-ops | 具体促销机制黑话，字面无法直接映射视觉元素 |
| 小红书种草文案配图 无中生有 | Xiaohongshu-like | 圈层调侃式黑话，字面义与实际所指完全不同，极端歧义案例 |
| 抖音团长带货海报 | ecommerce-ops | 社区团购模式专属角色黑话("团长")，测试本土商业模式术语理解 |
| 跨境电商黑五购物车弃单挽回邮件头图 | ecommerce-ops | 极具体DTC运营场景+节点组合，行业黑话压力测试的极端案例 |
| 小红书封面模板 白底大字 | Xiaohongshu-like | 具体排版惯例描述(而非风格词)，测试版式精确匹配 |
| 生鲜团购接龙海报 | ecommerce-ops | 极具本土化特色的社区团购模式("接龙")，海外语料几乎不可能覆盖 |
| 亚马逊评论截图水印素材 | ecommerce-ops | 非常规内容形态(截图+水印)，测试边缘品类理解 |

### 教育（27条）
| Query | query_style | 为什么是好的压力测试 |
|---|---|---|
| Montessori butterfly life cycle 3 part cards | teacher-resource | "3 part cards"是蒙氏教学法专属格式术语(三件套结构)，非单张卡片 |
| morning meeting slides editable Google Slides | teacher-resource | 具体教学环节+具体可编辑文件格式，格式匹配精度测试 |
| sub tub emergency lesson plan folder cover | teacher-resource | 美国教师圈层黑话，字面完全无法理解，圈层黑话识别测试 |
| number bonds to 10 ten frame worksheet | teacher-resource | 具体数学教学法专有名词组合，测试术语精确匹配 vs 泛化数学题 |
| dopamine classroom rules poster | teacher-resource | 趋势美学词跨场景迁移(从穿搭到课堂规则)，语义泛化能力测试 |
| Gen Alpha slang classroom poster | teacher-resource | 最新网络流行语进入教育场景，语料时效性测试 |
| IEP goal tracking data sheet template | teacher-resource | 特殊教育专业法律术语缩写，测试专业垂类覆盖 |
| toddler busy book quiet book pages printable | teacher-resource | 细分早教产品术语(强调互动元素)，区别于普通worksheet |
| homeschool morning basket printable checklist | teacher-resource | 家庭教育圈层具体流程术语，测试homeschool细分圈层覆盖 |

## 6. 下一步建议：人工 review 筛出 50-80 条 gold stress-test set

1. **先看 `keep_or_review=keep` 且 `priority=P0` 的交集**：这是信号最强、最值得优先验证的子集，预计在 30-40 条之间，可作为第一批人工复核对象。
2. **人工复核时重点确认三件事**：(a) 该黑话/趋势词是否真实存在且当前仍在使用（部分网络热词迭代很快，需要2026年时间点复核）；(b) `content_gap_hypothesis` 的猜测是否合理，不合理的应该修正或降级为 review；(c) 是否有更贴切的中文/英文表达替换（本轮部分中文黑话翻译成英文表达可能不准确，需要母语者复核，尤其是 Xiaohongshu-like 类目）。
3. **目标产出**：从 127 条中筛出 50-80 条组成 gold stress-test set，字段结构建议参照 `docs/daily_report/6.17/multi-intent-eval-v0_副本.md` 的 gold eval 格式，为每条补充 expected sub-intent，再分批送入 Curify 做 recall/filtering 实测。
4. **回测时按 `likely_recall_challenge` 和 `likely_filtering_challenge` 归因**：如果某条 query 的实测结果证实了假设的召回/过滤问题，应将其加入正式回归测试集；如果结果比预期好，说明该压力点已被现有系统覆盖，可以标记为"已验证无问题"而不必反复测试。
5. **与 Step 3A(188条)/Step 3B(98条) 合并维护**：三轮共 471 条候选，建议统一编号、统一维护在一份主表中，避免后续回测各批次互相重复或遗漏。

## 7. 本轮明确不做的事情

- ❌ 未在 Curify 上运行任何 query（含本轮 127 条）
- ❌ 未跑 recall/filtering 回测，未生成任何"Curify 结果好坏"的判断
- ❌ 未修改 `curify-frontend` 任何生产代码或搜索逻辑
- ❌ 未做 ranking/排序
- ❌ 未做大规模爬虫，未新抓取 Liblib/Pinterest/小红书等任何外部数据；`existing_external_data` 引用的均为 Step 1-3A 已采集并保存在 `docs/external-signal-pilot/` 下的历史数据，"Liblib-like"/"Xiaohongshu-like" 等 `query_style` 标签仅描述 query 的语言风格特征，不代表本轮抓取了这些平台的真实数据
- ❌ 未修改此前任何一轮的文件（Step 1-3A 的三个文件、Step 3B 的两个文件），本轮只新增文件
