# Easy Query Benchmark v2 生成报告（四大场景版）

日期：2026-07-16

## 0. 文件清单

| 文件 | 说明 |
|---|---|
| `easy_query_audit_v2_2026-07-16.csv` | 对原始 328 条 seed bank 逐条审计（KEEP_AS_REFERENCE / REMOVE / REPLACE） |
| `easy_query_bank_v2_2026-07-16.csv` | 新版 326 条 Easy Query Benchmark（四大场景） |
| `easy_query_bank_v2_generation_report_2026-07-16.md` | 本报告 |

**原始文件 `docs/daily_report/7.7/05_simple_head_term_seed_bank_2026-07-07.csv` 全程只读，
未被修改/覆盖/删除/重命名**（SHA-256 `393da01404746614a81ef5e2096cbf632cc2c851a711f132bec224947bfcf5b0`，
读取前后一致）。

**说明**：本目录（`easy-query-bank-v3/`）与此前生成的 `easy-query-bank-v2/`（5 大类目
Object/Merch/Education/Food/Nature 版本）是两套不同分类体系下的独立产出，均未相互覆盖。本轮
任务要求的是四大场景体系（Creative/Merch, Brand/Business, Marketing/Ecommerce, Education），
文件名沿用任务指定的 `..._v2_...` 命名，但存放于新目录以避免覆盖此前版本。

## 1. 老 Query Bank 存在的问题

原始 328 条 seed bank 是为"内容生成长尾扩展"设计的 head term 库（`term_type` 分为 object/
material/style/scene/industry/format/audience/festival/product_category/action 十类），其
设计目标是"可与场景/风格/物料自由组合成长尾营销 query"，与本任务"模拟真实用户在视觉搜索产品中
输入的简单、有清晰视觉目标、面向四大真实场景（创意周边/品牌商业/营销电商/教育学习）的 query"
存在本质差异，因此包含大量不适合的词：

1. **抽象风格词**（如 `极简`/`minimalist`、`复古`/`vintage`、`侘寂`/`wabi-sabi`）——无清晰
   单一视觉目标，属于任务明确列出的 abstract style words。
2. **材质/质感修饰词**（如 `cork`、`terrazzo`、`金属`、`玻璃`）——描述"用什么做的"而非独立
   可搜索对象。
3. **受众/人群词**（如 `student`/`学生`、`家庭主妇`、`宝妈`）——描述"给谁看"而非"画的是什么"，
   属于任务明确要求移除的 audience/person words。
4. **抽象行业/产业词**（如 `房地产`、`金融`、`教育培训`、`hospitality`）——是商业分类概念，
   非视觉对象。
5. **动作/行为词**（如 `打卡`、`种草`、`促销`、`撸铁`）——动词性，无单一视觉主体。
6. **过于宽泛/歧义的裸词**（如 `卡片`/`card`、`海报`/`poster`）——任务明确点名的反面示例，
   需要替换为有清晰上下文的具体组合表达（如 flashcard、movie poster）才可用。
7. **场景/地点词、节日词**（如 `教室`、`春节`）——虽有一定视觉识别度，但不落在本轮四大场景
   范围内。

## 2. 审计结果统计

对全部 328 条逐条判定（详见 `easy_query_audit_v2_2026-07-16.csv`）：

| decision | 数量 | 说明 |
|---|---:|---|
| REMOVE | 170 | 明确不适合：全部 `style`（40）、全部 `material`（30）、全部 `audience`（30）、
全部 `action`（24）、多数 `industry`（约 30）、少量 `format`/`product_category` 中过于宽泛
的词（如 `头像`/`avatar`、`壁纸`/`wallpaper`、`家纺`、`保健品`） |
| REPLACE | 19 | 概念有价值但裸词歧义/宽泛，需替换为更具体组合表达（如 `卡片`/`card` →
`flashcard`/`business card`；`海报`/`poster` → `movie poster`/`sale poster`；`婚礼`/
`wedding` → `wedding cake`；`咖啡`/`coffee` → `coffee package`；`香水`/`perfume` →
`perfume bottle`） |
| KEEP_AS_REFERENCE | 139 | 具体、视觉目标清晰的词，但多数不落在本轮四大场景范围内（如
`猫`、`书`、`太阳`、`婚纱` 类日常/自然物体，以及场景词、节日词），或已在新 Bank 中被直接沿用
（如 `贴纸`/`sticker`、`名片`/`business card`、`菜单`/`menu`、`潮玩`、`玩具`/`toy`） |

**移除词示例（含理由）**：
- `minimalist` / `极简` → REMOVE：抽象风格/美学描述词，无清晰单一视觉目标
- `wabi-sabi` / `侘寂` → REMOVE：抽象风格词
- `student` / `学生` → REMOVE：受众/人群词，任务明确要求移除类别
- `家庭主妇` → REMOVE：受众/人群词
- `terrazzo`、`金属`、`玻璃` → REMOVE：材质/质感修饰词，非独立视觉对象
- `房地产`、`金融`、`教育培训` → REMOVE：抽象行业/产业词
- `打卡`、`种草`、`促销`（动词用法）→ REMOVE：动作/行为词，无单一视觉对象主体
- `头像`/`avatar`、`壁纸`/`wallpaper`、`表情包` → REMOVE：数字内容形态词，高度抽象/多用途

## 3. 新 Query Bank 设计原则

1. **简单名词或短 noun phrase**，不含风格/材质/人群修饰语。
2. **每条 query 必须有清晰、单一的视觉目标**（如 `coffee cup` 而非 `beautiful`）。
3. **严格排除任务明确列出的四类禁用词**（已对全部 326 条做逐条程序化核查，**零违反**）：
   - 抽象风格词：minimalist, vintage, modern, retro, wabi-sabi, aesthetic, cute, beautiful,
     simple, creative（及中文对应词）
   - 泛化设计术语：design, graphic, visual, artwork, creative design, illustration design
   - 受众/人群词：student, teacher, designer, housewife, customer
   - 歧义裸词：card, box, line, style, thing, poster（裸词形式）——仅在有清晰上下文的组合词
     中出现（如 `business card`、`gift box`、`movie poster`）
4. **围绕四大真实使用场景组织，场景边界清晰**：
   - Creative/Merch：文创、IP、潮玩、收藏品、周边
   - Brand/Business：品牌商业视觉资产（包装、标签、菜单、名片、瓶身等具体实物）
   - Marketing/Ecommerce：营销/电商物料（横幅、传单、海报组合词、产品图、社交媒体内容）
   - Education：教学/学习物料（识字卡、练习册、图表、证书等）
5. **保留中英双语对照**，延续本项目一贯的 CJK/EN 评估方法论，便于复用既有分词/rewrite/
   matching 测试基础设施。

## 4. 场景分布

`easy_query_bank_v2_2026-07-16.csv` 共 **326 条**，四大场景分布如下（目标各 25%，实际分布
高度均衡）：

| scenario | 数量 | 占比 |
|---|---:|---:|
| Creative / Cultural / Merch | 82 | 25.2% |
| Brand / Business Visual Assets | 82 | 25.2% |
| Marketing / Ecommerce | 82 | 25.2% |
| Education / Learning Material | 80 | 24.5% |
| **合计** | **326** | **100%** |

语言分布：中文 163 条 / 英文 163 条（完全均衡）。

## 5. 代表性 Query 示例

**Creative / Cultural / Merch**：figure, plush, blind box, keychain, sticker, teddy bear,
capsule toy, tote bag, museum souvenir, cultural relic figure, IP figure, 手办, 盲盒, 泰迪熊,
文创手办, 国潮公仔

**Brand / Business Visual Assets**：logo, package, label, bottle, coffee cup, business card,
perfume bottle, chocolate box, wine label, product tag, coffee package, restaurant menu,
香水瓶, 咖啡包装, 首饰盒, 门店招牌

**Marketing / Ecommerce**：banner, flyer, catalog, sale banner, movie poster, restaurant flyer,
product banner, sale poster, product listing image, unboxing photo, membership card,
促销海报, 电影海报, 开箱照, 会员卡, 双十一促销海报

**Education / Learning Material**：flashcard, worksheet, alphabet card, calendar, certificate,
science poster, world map, periodic table, report card, classroom poster, 识字卡, 练习册,
科学海报, 荣誉证书, 元素周期表

## 6. 完整性与规则核查结果

- Audit 文件：328 行（与原始 seed bank 行数一致），字段 `query, decision, scenario, reason`。
- Bank 文件：326 行（落在任务要求的 300-350 范围内），字段 `query, language, scenario,
  category, reason`。
- `decision` 取值仅限 `KEEP_AS_REFERENCE` / `REMOVE` / `REPLACE`，程序化核验通过。
- `scenario` 取值仅限四大场景标识，程序化核验通过。
- 326 条 query 与原始 328 条无重复冲突（新 Bank 中的沿用词均来自 KEEP_AS_REFERENCE 判定，
  REPLACE 判定的词均已转换为更具体的组合表达，不以裸词形式出现）。
- 对全部 326 条 query 做小写精确匹配 + 裸词匹配的禁用词程序化核查，**结果：零违反**。
- 原始文件 SHA-256 读取前后一致，确认未被修改。

## 7. 后续建议

- Audit 中 139 条 `KEEP_AS_REFERENCE`（多为日常物体、自然词、场景词、节日词）是未来可考虑
  单独建立"通用物体类"或"场景/节日类"评估子集的候选池，本版四大场景体系下未直接采用。
- 若后续需要将本 Bank 用于生产 Baseline / 候选版本对比评估（可参考本项目
  `docs/daily_report/7.15/`、`docs/daily_report/7.16/easy-query-production-vs-optimized-comparison-v1/`
  已建立的方法论），建议在正式采集前对本文件计算并记录 SHA-256，作为后续复现核验的基准。
