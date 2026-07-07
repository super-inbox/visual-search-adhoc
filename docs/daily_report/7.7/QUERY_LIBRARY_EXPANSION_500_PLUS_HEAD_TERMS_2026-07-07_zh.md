# Query/Carry 库扩展报告 — Step 3D（2026-07-07）

_范围：扩展 high-signal niche query 候选到约 500 条规模，并新增 simple head term 基础词库。未进行 Curify 搜索测试，未跑 recall/filtering 回测，未修改 curify-frontend 或任何生产代码，未做 ranking，未做大规模新爬虫。_

## 1. 为什么需要 high-signal long-tail query

Step 3C 的 127 条已经证明了"黑话/趋势词/意图歧义"这类 query 比工整分类词更能暴露 Curify 的真实短板，但 127 条的样本量对于覆盖"文创/品牌/营销电商/教育"四大场景下的具体子领域（二次元同人、汉服国风、非遗工艺、DTC新消费、小红书运营、抖音直播电商、跨境电商、教师资源黑话、家庭教育、STEM教育……）来说还太薄——很多子领域只有 1-2 条代表 query，不足以支撑该子领域的回测判断。本轮的核心诉求就是**在保持"真实、小众、长尾"质感的前提下把样本量做厚**，让每个子领域都有 15-30 条可用于交叉验证的 query，而不是孤例。

## 2. 为什么也需要 simple head terms

Step 3A-3C 的所有 query 都是"成品"——已经是一句完整、具体的搜索词。这类成品 query 有两个问题：(1) 它们是我基于当前认知设计的，覆盖范围受限于我能想到的场景；(2) 它们不方便被再次组合、变形，产出新的长尾变体。

`simple_head_term_seed_bank` 解决的是另一层需求：提供一批**积木式的基础词**（鲜花、金属、书、玻璃、木头、咖啡、猫、植物……），这些词本身不构成一个完整的、有测评价值的 query，但具备强组合潜力——同一个"玻璃"，配合"品牌+茶饮"能长成"玻璃罐装茶饮品牌包装设计"，配合"文创+非遗"能长成"玻璃工艺品插画"，配合"教育"能长成"玻璃材质科普信息图"。这批词是未来批量生产更多 query 的**生成器**，而不是待测的 query 本身。

## 3. 两者的区别

| 维度 | high-signal niche query（500条） | simple head term（328条） |
|---|---|---|
| 完整度 | 完整、可直接送入 Curify 测试的 query | 未完成的基础词，需要再组合才能变成可测 query |
| 来源 | 竞品平台真实内容形态+行业黑话+趋势词，人工精心设计每一条 | 日常语言中最基础的对象/材料/风格/场景/行业词 |
| 数量级 | 500 条封顶，追求"每条都有具体的测评价值" | 328 条，追求"覆盖面广、颗粒度细，方便二次生产" |
| 用途 | 直接作为 stress-test 候选池，筛选后送回测 | 作为长尾生成的原材料，配合 modifier（风格/材质/场景）组合出更多 query |
| 复用方式 | 一次性消耗（测过一次就有结果了） | 可反复复用（同一个词能生出几十种组合） |

两者是"鱼"和"渔"的关系：500 条 query 是本轮能直接交付验证的"鱼"，328 个 head term 是保证未来能持续"钓"到更多真实长尾 query 的基础设施。

## 4. 如何后续组合使用

`simple_head_term_seed_bank` 的每个词都标注了 3 个 `example_expansion`，展示了该词的组合逻辑，具体有三种组合路径：

1. **head term × style（风格词）**：如"木头"(object/material) × "北欧"(style) → "北欧风原木家居摄影图"
2. **head term × industry/scene（行业/场景）**：如"猫"(object) × "教室"(scene，可类比教育场景) → "猫咪主题课堂奖励贴纸"
3. **head term × format（内容形态）**：如"鲜花"(object) × "贴纸"(format) → "鲜花图案贴纸设计"

后续可以用脚本做笛卡尔积式的组合生成（如 41 个 object × 40 个 style = 1640 种理论组合），但**不建议无差别生成**——应该先人工挑选组合逻辑合理、有真实场景支撑的对（比如"陶瓷+茶饮品牌"合理，"陶瓷+抖音直播电商"就比较牵强），再产出下一批 expanded query。这也是为什么本轮的 `expansion_potential` 字段很重要：`high` 潜力的词（如"极简""复古""咖啡""海报"）应该优先用于组合生产，`low` 潜力的词（如"围巾""云朵"）组合空间有限，可以少投入精力。

## 5. 四大场景覆盖情况

### File 1：05_high_signal_niche_query_candidates_500_2026-07-07.csv（504条，含 Step 3C 原 127 条 + 本轮新增 377 条）

| 场景 | 数量 | 说明 |
|---|---|---|
| 文创 | 142 | 新增覆盖二次元同人(24)、汉服国风穿搭(27)、非遗传统工艺(20)、AI绘画风格黑话(20)、谷圈潮玩周边(15)等子领域 |
| 品牌 | 129 | 新增覆盖小微本地品牌(25)、DTC新消费品牌(20)、网红IP品牌(15)、联名焕新(15)、垂类品牌矩阵(21)等子领域 |
| 营销电商 | 128 | 新增覆盖小红书运营(26)、抖音直播电商(20)、跨境电商metadata(20)、私域会员运营(21)、电商大促节点(10)等子领域 |
| 教育 | 105 | 新增覆盖教师资源黑话(25)、家庭教育homeschool(15)、STEM科学教育(15)、ESL双语教育(10)、特教SEL(13)等子领域 |

P0 106 / P1 288 / P2 110，满足"P0 至少 100 条"的要求。**说明**：Step 3C 原 127 条本轮直接并入本文件（保留原始字段值，`subdomain` 留空以标记来源），本轮新增的 377 条全部带有具体 `subdomain` 标签；377 条新增内容与原始 58 / 188 / 98 / 127 逐条查重，**零重复**。

### File 2：06_simple_head_term_seed_bank_2026-07-07.csv（328条）

| 场景(primary) | 数量 |
|---|---|
| 文创 | 125 |
| 品牌 | 122 |
| 营销电商 | 55 |
| 教育 | 26 |

按 `term_type` 分布：object 41 / style 40 / scene 35 / industry 35 / format 35 / product_category 34 / material 30 / audience 30 / festival 24 / action 24。中文词 267 / 英文词 61（风格词、行业词、格式词等国际通用概念优先保留英文原词，如 minimalist、cottagecore、planner）。

场景分布不均是预期结果：head term 本身（尤其是 style/format/object 类）天然更容易先长成"文创/品牌"方向的组合（视觉风格化内容），而"营销电商/教育"的组合更依赖具体行业/教学法术语，所以在基础词层面覆盖会薄一些——这一层的场景差距应该通过后续组合生成、以及 Step 3B/3C 已经积累的营销电商/教育类完整 query 来补足，而不是强行在基础词层面拉平。

## 6. 样例展示

### File 1 样例（每类选 2 条）

| Query | Scene | Subdomain | 为什么有价值 |
|---|---|---|---|
| Love and Deepspace card pack design | 文创 | 二次元同人 | 女性向乙女游戏卡包设计，测试新兴细分游戏类型IP覆盖 |
| 汉服马面裙叠穿灵感图 | 文创 | 汉服国风穿搭 | 2023-24现象级流行款式+具体穿搭手法(叠穿)组合 |
| 谷子店品牌视觉设计 | 品牌 | （Step 3C原有） | 圈层黑话"谷子"与字面义完全无关，极端歧义测试 |
| adaptogen wellness brand identity | 品牌 | DTC新消费品牌 | 小众健康成分黑话(adaptogen)，测试新兴保健品类覆盖 |
| 小红书爆款封面 emoji风 | 营销电商 | 小红书运营 | 具体封面视觉惯例(emoji装饰标题)，而非泛化"封面设计" |
| Amazon EBC enhanced brand content layout | 营销电商 | 跨境电商metadata | 亚马逊官方专属术语缩写(EBC)，测试平台规范格式理解 |
| Montessori butterfly life cycle 3 part cards | 教育 | （Step 3C原有） | 蒙氏教学法专属三件套格式术语 |
| zones of regulation poster classroom | 教育 | 特教SEL | 具体情绪调节教学法专有名词，非泛化"情绪海报" |

### File 2 样例（每类选 2 条）

| Term | Type | Scene | 扩展示例 |
|---|---|---|---|
| 鲜花 | object | 文创/营销电商 | 鲜花插画海报 / 鲜花品牌包装设计 / 鲜花种草配图 |
| 玻璃 | material | 品牌/文创 | 玻璃质感包装设计 / 玻璃器皿产品摄影图 / 玻璃工艺品插画 |
| Y2K | style | 文创/品牌 | Y2K chrome skincare launch poster / Y2K aesthetic sticker design / Y2K packaging concept |
| 咖啡馆 | scene | 品牌/营销电商 | 咖啡馆品牌logo设计 / 咖啡馆菜单板模板 / 咖啡馆室内摄影图 |
| 潮玩 | industry | 文创/营销电商 | 潮玩手办摄影海报 / 潮玩包装设计 / 潮玩品牌视觉设计 |
| planner | format | 教育/文创 | weekly planner template / homeschool planner printable / brand planner design concept |
| Gen Z | audience | 文创/营销电商 | Gen Z slang classroom poster / Gen Z aesthetic moodboard / Gen Z brand tone visual |
| 双十一 | festival | 营销电商/品牌 | 双十一促销海报设计 / 双十一预售定金尾款流程图 / 双十一电商banner设计 |

## 7. 本轮明确不做的事情

- ❌ 未在 Curify 上运行任何 query（含本轮全部 832 条：504 条 high-signal query + 328 条 head term）
- ❌ 未跑 recall/filtering 回测，未生成任何"Curify 结果好坏"的判断
- ❌ 未修改 `curify-frontend` 任何生产代码或搜索逻辑
- ❌ 未做 ranking/排序
- ❌ 未做大规模爬虫，未新抓取 Liblib/Pinterest/小红书等任何外部数据；文中引用的具体外部信号（`existing_external_data`/`existing_report_observation`）均来自 Step 1-3A 已采集并保存在 `docs/external-signal-pilot/` 下的历史数据
- ❌ 未修改此前任何一轮的文件（Step 1-3A 三个文件、Step 3B 两个文件、Step 3C 两个文件），本轮只新增文件
