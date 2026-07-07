# Query Expansion Step 1-3 报告 — 2026-07-07

_范围：仅完成 Step 1（资料盘点）/ Step 2（58 query 场景分类）/ Step 3（expanded query 候选生成）。未进行 Curify 搜索测试，未跑 recall/filtering 回测，未修改任何生产代码。_

## 0. 背景与目标

前几轮工作完成了 blog 首图修复与 query card UI。本轮进入下一条主线：围绕「文创 / 品牌 / 营销电商 / 教育」四大场景，扩展现有 58 个 query，为后续 Curify 搜索 recall/filtering 回测做输入准备。本轮只做资料盘点、分类、expanded query 候选生成三件事，不做测试和排序。

---

## 1. 资料盘点（Step 1）

### 1.1 原始 58 query 列表

| 文件 | 说明 |
|---|---|
| `docs/external-signal-pilot/query-tier1-distribution-58.csv` | **权威原始 58 query 列表**，含 `index/query/tier1/primaryIntent/consumer_or_creator/key_categories/short_reason` 字段，本轮分类的基础输入 |
| `docs/external-signal-pilot/query-tier1-distribution-58-curify-centered.csv` | 同一份 58 query 的 Curify 视角版本（tier1 分类口径略有不同） |
| `docs/daily_report/6.19-20/external-signal-pilot/...` | 上述文件在 6.19-20 日报目录下的历史副本，内容与 external-signal-pilot 主目录一致，本轮以主目录版本为准 |

### 1.2 5 平台对比数据

| 文件/目录 | 说明 |
|---|---|
| `docs/external-signal-pilot/external-signal-5x2-comparison-58.md` | 5 平台（Google Images / Bing Images / Pinterest / Canva / Curify）× 58 query 的综合对比报告，含数据采集状态、intent 分类法、gap 分析 |
| `docs/external-signal-pilot/platform-scorecard-5x58.csv` / `platform-scorecard-5x58-curify-centered.csv` | 5 平台评分表 |
| `docs/external-signal-pilot/{google-image,bing-image,pinterest-search,canva-search,curify-search}-eval-58/` | 每个平台各 58 条 per-query 原始数据目录，见 1.3 |
| `docs/external-signal-pilot/curify-gap-analysis-58.csv` | Curify 相对外部平台的召回缺口清单 |
| `docs/external-signal-pilot/label-count-by-query-2026-06-23.csv` / `label-count-summary-2026-06-23.csv` | 各平台标签数量统计（按 query / 按平台汇总） |

### 1.3 各平台标签、推荐词、截图、CSV/JSON 数据位置

每个平台目录结构一致：

```
docs/external-signal-pilot/<platform>-eval-58/
├── README.md
├── data/
│   ├── observations.csv / .json     # 汇总表
│   ├── collection_progress.csv      # 采集状态
│   ├── validation-report.json
│   └── per-query/                   # 58 个 per-query JSON，本轮核心输入
│       └── 001-q001.json ... 058-*.json
└── screenshots/                     # 每个 query 的搜索结果截图
```

本轮实际使用的信号字段：

- **Google Images** (`google-image-eval-58`)：`labels` = Google 相关搜索推荐词（如"水果中文"→`Fruit names / 水果词汇 / Chinese fruits`），信号质量最高、噪音最少。
- **Bing Images** (`bing-image-eval-58`)：`labels[].text`，其中 `href` 含 `FORM=IRMHRS` 的才是真正的"相关搜索"芯片（其余是尺寸/颜色/授权等筛选器 UI 文案，或结果详情页重复项，已在提取脚本中过滤）。芯片数量最多，是本轮 expanded query 的主要来源。
- **Pinterest** (`pinterest-search-eval-58`)：`labels` 字段本身因登录弹窗大多为空（40/58），但 `topResults[].title` 里包含大量 Pinterest 画板长标签（如"Chinese Fruit Vocabulary Practice, Fruits In Chinese Pinyin"），本轮当作等效的"推荐词"来源。
- **Canva** (`canva-search-eval-58`)：`labels` = 实际模板标题（英文 query 覆盖较好，纯 CJK/IP query 大量 `login_required`），是判断"内容类型/模板形态"最直接的证据。
- **Curify** (`curify-search-eval-58`)：本轮未使用其结果做判断（避免变相做了搜索测试），仅确认目录存在、留待后续回测阶段使用。

### 1.4 已有分析报告

| 文件 | 用途 |
|---|---|
| `docs/external-signal-pilot/EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md` / `_zh.md` | 通用视角的外部信号洞察报告（英/中） |
| `docs/external-signal-pilot/CURIFY_CENTERED_EXTERNAL_SIGNAL_INSIGHTS_2026-06-21_zh.md` | **Curify 为核心视角**的洞察报告，含 tier1 分布、消费/创作分析、5 平台评分、Curify gap 与机会 —— 本轮场景分类方法论的主要参考 |
| `docs/external-signal-pilot/EXTERNAL_SIGNAL_INSIGHTS_2026-06-23_zh.md` | 后续更新版本 |
| `docs/external-signal-pilot/label-count-statistics-report-2026-06-23.md` | 标签数统计的可复现性说明，解释了 Bing/Canva 标签为何偏高 |
| `docs/external-signal-pilot/pinterest-canva-missing-data-report-2026-06-23.md` | Pinterest/Canva 缺失数据的原因分析（登录墙） |
| `docs/external-signal-pilot/p1-template-gap-retest-2026-06-23.md`、`template-recall-fix-report-2026-06-23.md` | P1 模板缺口与召回修复相关报告 |

### 1.5 Query eval set / 回测相关 markdown

| 文件 | 用途 |
|---|---|
| `docs/daily_report/6.17/multi-intent-eval-v0_副本.md` | **原始 query eval set（V0）**，逐 query 记录 expected sub-intents / 模型实际输出 / 5 维评分（相关性、多样性、语言一致性、可搜索性、可视化价值）+ 通过阈值定义。**建议作为后续更新 expanded query eval set 的模板文件**（结构已含"query → expected intents → 评分"的完整骨架，只需按 expanded query 补充条目） |
| `docs/search-evaluation/template-recall-audit-all-queries.md` | 已有的模板召回审计 markdown，逐 query 分析 Curify 召回缺口、根因分类（多token复数词干缺口/CJK同义词映射缺口/模板i18n描述缺口等），是"query→gap→根因"的现成范式，可复用于 expanded query 回测报告结构 |
| `docs/search-evaluation/template-gap-vs-recall-audit.md` | 模板缺口 vs 召回缺口对比审计 |
| `docs/search-evaluation/local-search-recall-verification.md` | 本地搜索召回验证记录 |

### 1.6 适合作为本轮 query 扩展输入的文件（结论）

1. `docs/external-signal-pilot/query-tier1-distribution-58.csv` — 58 query 原始清单 + 已有 tier1/intent 标注（Step 2 基础）
2. `docs/external-signal-pilot/{google-image,bing-image,pinterest-search,canva-search}-eval-58/data/per-query/*.json` — 逐 query 的标签/推荐词/模板标题（Step 3 信号来源）
3. `docs/external-signal-pilot/CURIFY_CENTERED_EXTERNAL_SIGNAL_INSIGHTS_2026-06-21_zh.md` — intent 分类法参考
4. `docs/search-evaluation/template-recall-audit-all-queries.md` — 未来回测报告的结构范式

---

## 2. 58 Query 场景分类方法（Step 2）

**输出文件**：`docs/daily_report/7.7/01_original_58_query_scene_classification_2026-07-07.csv`

### 2.1 方法

1. 以 `query-tier1-distribution-58.csv` 的 `tier1`（8 个原始类目：Vocabulary & Language / Character & IP & Pop Culture / Lifestyle & Aesthetic / DIY-How-to-Craft / Nature & Botanical / Food & Recipe / Travel & Place & Culture / Art & Design & Visual）与 `consumer_or_creator` 字段为基础输入。
2. 人工将 8 个原始 tier1 类目重新映射到「文创 / 品牌 / 营销电商 / 教育」四大场景，逐条判断 primary_scene，必要时给出 secondary_scene（如家居装饰=营销电商为主、文创为辅）。
3. `intent_type` 直接复用原始 `consumer_or_creator` 字段的语义（consumer→consumption，creator→creation，mixed→mixed），不重新判断，保持与既有分析口径一致。
4. `confidence` 反映场景映射的把握程度：query 本身带有明确产出物/学习意图词（如"打印""模板""练习""海报"）为 high；仅靠 tier1 类目推断、缺少直接场景词为 medium；query 过于抽象或与四大场景贴合度低（如"证件照""global influence"）为 low。

### 2.2 结果分布

- 总计 58 条，`primary_scene` 分布：**文创 23 / 营销电商 18 / 教育 17 / 品牌 0**
- `confidence` 分布：high 32 / medium 24 / low 2
- `intent_type` 分布：creation 26 / consumption 25 / mixed 7

### 2.3 关键发现：原始 58 query 中没有「品牌」主场景

58 个原始 query 全部来自消费者/创作者的自然搜索词，没有一条是直接面向"品牌资产/品牌视觉系统"的查询（如"logo设计""品牌VI手册"）。品牌信号只在 6 条 query 中作为 **secondary_scene** 出现（电商详情图、葡萄酒、香薰、Met Gala、婚礼策划、1950s复古海报），说明品牌场景是**当前 query 集合的天然盲区**，需要在后续单独补充品牌类种子 query，而不是勉强从现有 58 条里凑数。

### 2.4 各场景样例

| 场景 | Query 样例 | Reason |
|---|---|---|
| 教育 | 水果中文、词汇、phonics worksheets kindergarten | 双语识字卡/练习册/打印品，教育意图明确 |
| 文创 | 卡通、吉伊卡哇、mbti marvel、watercolor map of europe | IP角色插画/图表化创作，文创设计素材来源 |
| 营销电商 | 电商详情图、meal prep weekly recipes、wedding planner | 明确的商用模板/产品图/导购内容需求 |
| 品牌（仅作为 secondary） | 葡萄酒→品牌、Met Gala→品牌、1950s vintage diner→品牌 | 品类/事件天然带有品牌调性，但原始 query 未直接指向品牌资产 |

完整 58 条见 CSV：`docs/daily_report/7.7/01_original_58_query_scene_classification_2026-07-07.csv`（字段：`index, query, primary_scene, secondary_scene, intent_type, reason, confidence, source_tier1`）

---

## 3. Expanded Query 候选生成方法（Step 3）

**输出文件**：`docs/daily_report/7.7/02_expanded_from_58_query_candidates_2026-07-07.csv`

### 3.1 方法

1. 对每个 seed query，从其 Google/Bing/Pinterest/Canva 的 per-query JSON 中提取真实推荐词/标签/模板标题（见 1.3 的提取规则，Bing 用 `FORM=IRMHRS` 过滤真实相关搜索芯片，剔除筛选器 UI 与视频时间戳等噪音）。
2. **不做同义词替换**：不是把"食物"换成"美食""食品"，而是结合信号中出现的**具体场景、受众、模板类型或内容格式**生成新 query，例如：
   - "食物" + Canva 模板标题 "Red and White Minimalist Chinese Food Menu" → **"餐厅菜单设计模板"**（而不是"美食图片"）
   - "monstera plant care guide infographic" + Bing chip "Monstera Basic Care Guide" → **"龟背竹养护指南信息图"**（品种本地化 + 具体载体）
3. 每条 expanded query 标注：`source_platform`（来自哪个平台）、`source_signal`（引用的具体标签/模板原文，可追溯验证）、`expected_content_type`（预期内容形态，如 flashcard/poster/template/infographic）、`expansion_reason`（为什么这样扩展，不是简单复述信号）、`confidence`。
4. 每个 seed 生成 3-4 条（未强行凑满 5 条）；当外部信号本身噪音较高或高度抽象（如 "global influence" "genshin" 的部分推断）时，标注 `low` confidence 并在 reason 中说明信号弱的原因，而不是编造。
5. **全程未提交任何 query 到 Curify 搜索**，`source_signal` 全部来自已采集的 Google/Bing/Pinterest/Canva 历史数据文件，不涉及本轮新抓取。

### 3.2 结果统计

- 覆盖全部 58 个 seed query（与官方列表逐条核对一致，无遗漏/无拼写偏差）
- 共生成 **188 条** expanded query 候选，平均每条 seed 3.2 条
- `primary_scene` 分布：营销电商 68 / 教育 67 / 文创 47 / **品牌 6**
- `source_platform` 分布：Bing 106 / Canva 33 / Pinterest 26 / Google 23
- `confidence` 分布：high 99 / medium 83 / low 6

值得注意：expanded query 层面**品牌场景从 0 条（Step 2 原始 primary）提升到 6 条**——这是因为具体化后的 query（如"复古餐厅品牌Logo设计""葡萄酒品牌Logo设计""武士主题品牌Logo设计"）比抽象 seed 更容易触达品牌资产类需求，说明"场景扩展"本身能部分填补 Step 2 发现的品牌盲区，但仍需专门补充品牌类种子 query 才能系统性覆盖。

### 3.3 各场景样例

**教育**
| seed_query | expanded_query | source | expected_content_type |
|---|---|---|---|
| 水果中文 | 水果中文拼音识字卡 | Google labels: 拼音/水果词汇 | flashcard |
| homophones and homonyms | 同音词/同形词教学挂图 | Pinterest title: "Homonyms Anchor Chart" | poster |
| monstera plant care guide infographic | 龟背竹养护指南信息图 | Bing chip: Monstera Basic Care Guide | infographic |

**文创**
| seed_query | expanded_query | source | expected_content_type |
|---|---|---|---|
| mbti marvel | 漫威角色MBTI人格图表 | Bing chip: Marvel MBTI Chart | chart/infographic |
| paper cutting | 剪纸镂空花鸟图案设计 | Pinterest title: paper cut silhouettes with flowers and butterflies | illustration/template |
| chiikawa | chiikawa透明背景贴纸素材 | Bing chip: Chiikawa PNG | sticker/clipart |

**营销电商**
| seed_query | expanded_query | source | expected_content_type |
|---|---|---|---|
| 电商详情图 | 电商产品主图设计模板 | Bing chip: 产品主图设计 | template |
| wedding planner | 婚礼预算规划表 | Canva template: Wedding Budget Planner | planner document |
| meal prep weekly recipes | 一周备餐计划表模板 | Canva template: Weekly Meal Planner | planner template |

**品牌**
| seed_query | expanded_query | source | expected_content_type |
|---|---|---|---|
| 葡萄酒 | 葡萄酒品牌Logo设计 | Bing chip: 葡萄酒 Logo | logo |
| 1950s vintage diner illustration retro poster | 复古餐厅品牌Logo设计 | Canva template: Retro Diner Brand Logo | logo |
| samurai | 武士主题品牌Logo设计 | Canva template: Samurai Apparel Warrior Logo | logo |

---

## 4. 本轮明确不做的事情

- ❌ 未在 Curify 上运行任何 query（包括原始 58 条和 188 条 expanded query）
- ❌ 未跑 recall/filtering 回测，未生成任何"Curify 结果好坏"的判断
- ❌ 未修改 `curify-frontend` 任何生产代码或搜索逻辑
- ❌ 未做 ranking/排序
- ❌ 未做大规模爬虫或对 Liblib/Pinterest 的新抓取；所有信号均来自 `docs/external-signal-pilot/` 下已有的历史采集数据

---

## 5. 下一步建议

1. **回测准备**：以 `docs/daily_report/7.7/02_expanded_from_58_query_candidates_2026-07-07.csv` 的 188 条 expanded query 为输入，参照 `docs/daily_report/6.17/multi-intent-eval-v0_副本.md` 的 gold eval 结构，为每条（或抽样一批高 confidence 的）expanded query 建立 expected sub-intent，再在 Curify 上实测 recall/filtering。
2. **优先级建议**：先用 confidence=high 的 99 条做小规模回测（覆盖 4 个场景、4 个平台来源），验证方法论有效后再扩展到 medium/low 的部分。
3. **品牌场景补充**：鉴于原始 58 query 中品牌场景为空、expanded 后也只有 6 条，建议后续单独设计一批"品牌"主场景的种子 query（如 logo 设计、VI 视觉系统、品牌海报模板类），而不是继续从现有 58 条里勉强扩展。
4. **回测报告结构**：可直接复用 `docs/search-evaluation/template-recall-audit-all-queries.md` 的"query → Curify 结果 → gap → 根因分类"范式，保持与既有分析口径一致，便于与 6 月的 5 平台报告做纵向对比。
