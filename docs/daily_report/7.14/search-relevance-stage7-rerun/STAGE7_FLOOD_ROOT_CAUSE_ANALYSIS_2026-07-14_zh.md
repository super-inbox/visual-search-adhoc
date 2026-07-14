# Stage 7 Flood Root Cause Analysis

分析时间：2026-07-14。本报告为只读根因分析，未修改任何 production 代码、未修改任何 7.13 产出文件、未重跑完整 68 条实验、未批量调用 LLM、未 Commit / Push。本阶段仅在 `docs/daily_report/7.14/search-relevance-stage7-rerun/` 目录新增 3 个文件（本报告 + CSV + JSON）。

## 1. Executive Summary

- **23 条 d+g 洪泛 Case 的主要根因分布**：`EMPTY_PRIMARY_VACUOUS_MATCH`（空 primary 平凡为真）2 条（Q39、Q40，均为满目录 3209）；`GENERIC_STANDALONE_REWRITE`（通用独立 slot 单独构成检索路径）15 条；`DECOMPOSITION_TOO_BROAD`（多个中等宽泛路径联合放大）6 条。全部 23 条均带有 `MERGE_UNION_FLOODING`（多路径 Union 合并）作为共同的次要/放大原因。
- **通用独立 slot 能解释的数量**：直接可归因 15/23（65%），另有 6/23 属于"无单一通用词但多路径联合放大"的变体，二者合计 21/23 与"通用/低信息量独立检索路径"这一大类相关；真正独立于该机制的只有 Q39、Q40 这 2 条空 primary case（虽然它们的洪泛表现也恰好是通过一个恰为停用词的 generic slot 值"template"触发）。
- **原始核心实体丢失情况**：**0/23 判定为 LOST**。全部 23 条在 Rewrite 整体输出层面（`rewrites` 数组 + `decomposition.subject`）都至少保留了一个原始实体/高信息量 token，判定为 `PRESERVED_PARTIAL`。真正的问题不是"实体被删除"，而是"decomposition 把 style/scene/output/era/mood 当作与 subject 平级的独立检索路径分别执行，这些非 subject 路径本身从不携带实体"——这是一个比"实体丢失假设"更精确的机制描述，详见第 8、10 节。
- **空 primary token / vacuous match 是否为真实问题**：**是，已在代码层面直接确认**。`app/[locale]/(public)/search/page.tsx` 的 `scoreBlob()` 函数中 `requiredSlots = tokens.primary.length + aliasGroups.length`，`allPrimary = (primaryHits+groupHits === requiredSlots)`；当某个 decomposition slot 的值被停用词过滤后变为空数组时，`requiredSlots=0`，`0===0` 恒真，导致该路径对全部 3209 条记录判定为 strict 匹配。该 bug 在当前工作区（Stage 6 版本）与 `git show HEAD`（pre-Stage-6 版本）中逐字相同——**不是 Stage 6/7 新引入的问题，是一个此前从未被触发过的既存缺陷**，只有 P0.2 的 decomposition-slot 独立路径机制才会产生恰好变空的 token 集合从而触发它。
- **洪泛是否依赖 g（Rewrite）**：**是，严格依赖**。Mode A（d=OFF,g=OFF）与 Mode B（d=ON,g=OFF）在全部 68 条 Query 上 `result_count>=1000` 的数量均为 **0**；`d_only_result_count` 在全部 68 条中的最大值为 844（未达到 1000 门槛）。只有 g=ON 的 Mode C、D 才出现洪泛（C=4 条，D=23 条）。
- **d 的交互作用**：**未发现 d 能一致性地缓解或放大洪泛**。d 单独（Mode B）从不洪泛；d+g（Mode D）洪泛数量（23）远高于 g 单独在同一批次可比较的 Mode C（4，且与 D 的 23 条几乎不重叠，仅 Q16、Q42 两条同时出现在 C 与 D）。根本原因是 **Mode C 与 Mode D 是两次独立、非确定性（temperature=0.4）的 LLM 调用**，同一 Query 在两次调用中可能得到不同的 rewrite/decomposition 文本（已用 Q01、Q39、Q42、Q53 四个具体案例的 `rewrite_output_json` 逐字比对证实）。因此"d 缓解/放大洪泛"这一问题在当前数据下**无法给出因果结论**，只能确认"洪泛现象与 d 无关，只与 g 输出内容的具体措辞有关"。
- **Full-catalog 的具体原因**：Q39、Q40 在 Mode D 均因 `decomposition.output` 恰好解析为裸词 `"template"`（该词是 STOPWORDS 集合成员）触发空 primary 平凡为真。Q42 在 Mode C 命中同一 bug（`output:"template"`），但在 Mode D 的独立调用中 `output` 变为两词短语 `"cover template"`（"template"被过滤后剩余"cover"，非空），因此 Mode D 未触发该 bug，而是通过"cover"这一高频通用词以 `GENERIC_STANDALONE_REWRITE` 机制达到 2291（未到满目录）。
- **推荐的最小修复组合**：按优先级 Guard D（空 primary fail-closed，单行代码修复）→ Guard H（目录词频统计基础设施）→ Guard A（基于词频的低信息量独立 slot 过滤）→ Guard C（非 subject slot 必须与实体绑定或合并回 subject 路径）。详见第 12、13 节与 JSON 输出。
- **是否具备进入 Prompt 2 的条件**：**READY_WITH_LIMITATIONS**。详见第 16 节。

## 2. Inputs and Method

### 2.1 输入文件与哈希

| 文件 | 所属 repo | SHA-256（独立重算） | 与 Prompt 0 审计是否一致 |
|---|---|---|---|
| `hard_queries_68_baseline.csv` | adhoc | `904ea6a5a17a28dbafe3948de6f5bcb958674e518280e5eaad079b150453d233` | 一致（本阶段开始前与结束前均重新计算，见第 15 节） |
| `hard_queries_68_before_after.csv` | adhoc | 未在本报告重复列出（Prompt 0 已记录 `fc4cbb9d...`），本阶段直接读取该文件的 68 行原始字段独立解析 | 使用同一份文件，未修改 |
| `hard_queries_68_refreshed.csv` | adhoc | 同上，使用 Prompt 0 记录的 `579d1bfb...` 版本 | 使用同一份文件，未修改 |
| `hard_queries_68_ablation.csv` | adhoc | 同上，使用 Prompt 0 记录的 `e9a3a21d...` 版本，272 行 A/B/C/D 逐模式数据 | 使用同一份文件，未修改 |
| `gold_query_test_set_2026-07-07.csv` | adhoc | Prompt 0 记录的 `00bd2cff...` | 用于核对 68 条权威 Query 文本，未修改 |
| `app/[locale]/(public)/search/page.tsx` | curify-frontend（working tree） | 直接 `Read` 全文 1010 行 | 只读，未修改 |
| `app/[locale]/(public)/search/page.tsx` | curify-frontend（`git show HEAD`） | 直接 `git show HEAD:...` 只读比对 | 只读，未修改 |
| `lib/searchRewrite.ts` | curify-frontend（working tree） | 直接 `Read` 全文 697 行 | 只读，未修改 |

### 2.2 方法

- 全部 23 条洪泛 Case 逐条读取 `rewrite_output_json`、`primary_tokens_json`、`alias_groups_json`、`final_search_queries_json`（`hard_queries_68_refreshed.csv`）与 `d_only/g_only/d_plus_g` 计数、`attribution`、`final_verdict`（`hard_queries_68_before_after.csv`），用 Python `json.loads` 正确解析字符串化 JSON 字段，未仅凭字符串搜索下结论。
- A/B/C/D 数量与 full-catalog 数量从 `hard_queries_68_ablation.csv` 的 272 行原始数据独立重新分组统计（`result_count` 字段），未照抄 7.13 或 Prompt 0 报告的数字。
- 空 primary / vacuous match 机制通过直接 `Read` 生产代码 `page.tsx` 的 `scoreBlob`/`buildSearchTokens`/`STOPWORDS` 定义，并用 `git show HEAD:...` 读取 pre-Stage-6 版本逐行比对确认。
- 通用词假设通过自动化脚本对全部 68 条（不只是 23 条洪泛 Case）的 `decomposition` 字段做 token 级统计，计算每个候选通用词的总出现次数、洪泛占比、平均/最大 `d_plus_g_result_count`，而非仅检查预设词表。
- 直接证据（direct evidence）：CSV 原始字段值、生产代码逐行读取、`git show` 比对。
- 推断证据（inferred evidence）：per-slot 独立结果数（未被 harness 单独记录，通过 `strict_result_count`/`relaxed_result_count`/`decomposition` 内容 + 代码逻辑推断）、原始 LLM 响应的未解析全文（未被持久化，只有解析后的 JSON）。

### 2.3 未执行的操作（按 Scope 强制排除）

- 未重跑 68 条完整实验（全部数据来自 7.13 既有产出文件）。
- 未批量调用生产搜索接口或 LLM API（本阶段 0 次网络调用）。
- 未修改 `page.tsx`/`searchRewrite.ts`/`query_phrase_aliases.ts` 等任何 production 文件。
- 未实现任何 Guard（仅设计与评估，见第 12 节）。

## 3. A/B/C/D Flooding Comparison

独立重算（`hard_queries_68_ablation.csv` 272 行，按 `mode` 分组，`result_count>=1000` 计数）：

| Mode | 定义 | `>=1000` 数量 | Full-catalog(3209) 数量 |
|---|---|---:|---:|
| A | d=OFF, g=OFF | 0 | 0 |
| B | d=ON, g=OFF | 0 | 0 |
| C | d=OFF, g=ON | 4（Q01, Q16, Q42, Q53） | 1（Q42） |
| D | d=ON, g=ON | 23（详见第 4 节） | 2（Q39, Q40） |

- **g 依赖关系**：洪泛只在 g=ON 的两组（C、D）出现，A、B 均为 0。结论：洪泛严格依赖 Rewrite/Decomposition 机制（g），d（Stage 6 分词/短语保护）本身从不产生洪泛。
- **d 交互关系**：C 与 D 的洪泛集合几乎不重叠（仅 Q16、Q42 同时出现），且 Q01、Q53 只在 C 洪泛、D 未洪泛，Q39、Q40 只在 D 洪泛、C 未洪泛。已逐条核实 `rewrite_output_json`：C 与 D 对同一 Query 拿到的是**两次独立的、内容不同的 LLM 输出**（例如 Q39：C 的 `output` slot="素材"，D 的 `output` slot="template"）。这证明 C/D 差异主要由 LLM 非确定性（temperature=0.4）驱动，而非 d 的分词逻辑对同一文本产生了不同的匹配结果。**因此本报告不对"d 缓解/放大洪泛"给出因果结论**，只确认洪泛现象与 d 无关。
- **A/C 离线重建限制重申**：Mode A、C 的 d=OFF 分支是通过 `git show HEAD` 读取 pre-Stage-6 版本的 `page.tsx` 文本重建，而非导入真实运行过的旧版本模块（Prompt 0 §6/§12 已声明的已知限制）。本阶段已直接核实 `scoreBlob` 的 `requiredSlots`/`allPrimary` 公式在两个版本中逐字相同（见第 7 节），因此这一限制不影响本报告对空 primary bug 本身的诊断结论，但仍适用于任何基于 A/C 计数差异的更细颗粒度推断。

## 4. All 23 D-Mode Flooding Cases

以下为全部 23 条 `d_plus_g_result_count >= 1000` 的 Case（来源：`hard_queries_68_before_after.csv` + `hard_queries_68_refreshed.csv` 独立解析，逐条列出，非抽样）：

| Query ID | Query | A | B | C | D | Rewrite 摘要 | Flooding slot | 实体保留 | Primary root cause | Guard 建议 | Confidence |
|---|---|---:|---:|---:|---:|---|---|---|---|---|---|
| Q06 | genshin impact Furina fanart wallpaper 4k | 2 | 2 | 5 | 1569 | subject=Furina, style=fanart, output=wallpaper | style/output 独立路径 | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | MEDIUM |
| Q09 | 低饱和国风茶包装设计 | 84 | 2 | 84 | 1023 | subject=tea packaging, style=traditional, mood=low saturation | style="traditional" | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | MEDIUM |
| Q10 | 光与夜之恋 卡面设计参考图 | 0 | 0 | 20 | 2687 | subject=Light and Night, output=character design | 无单一裸词，"character design"整体宽泛 | PRESERVED_PARTIAL | DECOMPOSITION_TOO_BROAD | C | MEDIUM |
| Q11 | 故障艺术风格海报 | 339 | 2 | 339 | 2814 | style=glitch art, output=poster | output="poster" | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | HIGH |
| Q12 | 松弛感生活方式插画 | 156 | 7 | 156 | 3154 | style=illustration, mood=relaxed | style/mood 独立单词 | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | MEDIUM |
| Q15 | K-beauty glass skin brand launch visual | 0 | 6 | 84 | 1026 | subject=K-beauty brand, style=visual, output=poster | style="visual", output="poster" | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | HIGH |
| Q16 | Y2K chrome skincare launch poster | 0 | 346 | 1192 | 1197 | style=Y2K, scene=skincare launch, output=poster | output="poster" | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | HIGH |
| Q19 | heritage brand rebrand moodboard | 8 | 8 | 25 | 1855 | subject=heritage brand, style=moodboard, output=design concept | style="moodboard" | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | MEDIUM |
| Q25 | 博物馆文创联名产品设计 | 198 | 0 | 198 | 1712 | subject=museum products, style=creative, output=design | style="creative", output="design" | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | HIGH |
| Q26 | 国货美妆联名限定包装 | 0 | 0 | 276 | 1766 | subject=beauty packaging, style=limited edition, output=collaboration design | 无裸词单词，"collaboration design"整体宽泛 | PRESERVED_PARTIAL | DECOMPOSITION_TOO_BROAD | C | MEDIUM |
| Q27 | 宠物摄影工作室品牌设计 | 131 | 0 | 131 | 1600 | subject=pet photography studio, output=brand design | "brand design"整体宽泛 | PRESERVED_PARTIAL | DECOMPOSITION_TOO_BROAD | C | MEDIUM |
| Q28 | 宠物殡葬服务品牌视觉设计 | 161 | 51 | 161 | 1602 | subject=pet funeral service, output=branding design | "branding design"整体宽泛 | PRESERVED_PARTIAL | DECOMPOSITION_TOO_BROAD | C | MEDIUM |
| Q33 | 美妆博主个人IP视觉设计 | 117 | 3 | 117 | 1670 | subject=beauty influencer, style=visual design, output=branding | output="branding" | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | HIGH |
| Q39 | 亚马逊评论截图水印素材 | 0 | 0 | 1 | **3209(full)** | subject=Amazon review screenshot, style=watermark, **output="template"（裸停用词）** | output="template" | PRESERVED_PARTIAL | **EMPTY_PRIMARY_VACUOUS_MATCH** | D+A | HIGH |
| Q40 | 小红书图文笔记模板 数字标题 | 0 | 0 | 8 | **3209(full)** | subject=Xiaohongshu post, style=graphic, **output="template"（裸停用词）** | output="template" | PRESERVED_PARTIAL | **EMPTY_PRIMARY_VACUOUS_MATCH** | D+A | HIGH |
| Q41 | 小红书对比图 use前后 | 0 | 1 | 7 | 1195 | subject=Xiaohongshu, output=comparison poster | subject="Xiaohongshu"单独作为路径，目录覆盖面广 | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | MEDIUM |
| Q42 | 小红书封面模板 白底大字 | 0 | 0 | **3209(full)** | 2291 | D: style=minimalist, output="cover template"（"template"被过滤，剩"cover"） | output="cover" | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE（D 模式）/ EMPTY_PRIMARY_VACUOUS_MATCH（仅 C 模式） | D+A+H | HIGH |
| Q43 | 小红书探店打卡九宫格 | 0 | 0 | 29 | 1726 | subject=store visit, output=photo grid | 无裸词单词，多路径联合放大 | PRESERVED_PARTIAL | DECOMPOSITION_TOO_BROAD | C | MEDIUM |
| Q45 | 小红书爆款封面 emoji风 | 0 | 0 | 26 | 1866 | subject=trending cover, style=emoji, output=cover design | style="emoji" | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | MEDIUM |
| Q46 | 小红书香薰产品种草图 | 6 | 6 | 943 | 2904 | subject=aromatherapy products, output=infographic | output="infographic" | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | HIGH |
| Q47 | 抖音小黄车商品卡片设计 | 9 | 2 | 9 | 2129 | subject=product card, output=design | output="design" | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | HIGH |
| Q48 | 抖音带货主播人设海报 | 0 | 0 | 544 | 2184 | subject=Douyin influencer, output=character poster | "character poster"整体宽泛 | PRESERVED_PARTIAL | DECOMPOSITION_TOO_BROAD | C | MEDIUM |
| Q52 | Gen Alpha slang classroom poster | 0 | 0 | 995 | 1056 | subject=Gen Alpha slang, scene=classroom, output=poster | scene="classroom", output="poster" | PRESERVED_PARTIAL | GENERIC_STANDALONE_REWRITE | A+H | HIGH |

Guard 建议列缩写：A=Guard A（低信息量独立 slot 过滤），C=Guard C（slot 实体绑定），D=Guard D（空 primary fail-closed），H=Guard H（目录词频统计）。完整字段（含 top10、has_strict、strict/relaxed 计数等）见 `stage7_flood_cases_diagnosis_2026-07-14.csv`。

## 5. Full-catalog Cases

### Q39 — 亚马逊评论截图水印素材

- Baseline=2, d_only=0, g_only=1, **d_plus_g=3209（满目录）**
- Mode D 的 `rewrite_output_json.decomposition` = `{"subject":"Amazon review screenshot","style":"watermark","output":"template"}`
- `output` slot 的值是裸词 `"template"`。`buildSearchTokens("template")` 先按空白/标点切分得到 `["template"]`，再经过 `STOPWORDS.has("template")` 过滤（`page.tsx` working tree 第 139 行，`git show HEAD` 版本第 135 行，两者逐字相同）——`primary` 变为 `[]`。该路径没有命中任何 Protected Phrase/概念组，`aliasGroups` 也是 `[]`。
- 代入 `scoreBlob()`：`requiredSlots = 0 + 0 = 0`；对**任意**记录的 blob，`primaryHitsOnly=0, groupHits=0`，`allPrimary = (0===0) = true`。这对 `nano_inspiration.json` 的全部 3209 条记录都成立。
- `strict_result_count=3209, relaxed_result_count=0`（`hard_queries_68_refreshed.csv` 字段），与理论推导完全吻合。
- `has_strict` 字段值为 `false`——这是因为 Stage 6 的 `hasStrict` 只看 `baseResult`（原始 Query 自身的评分结果），原始 Query "亚马逊评论截图水印素材"本身 baseline 只有 2 条，`baseResult.scored` 中没有 strict 命中，所以这个 3209 条的洪泛完全没有被 `hasStrict` 过滤逻辑挡住——它是通过 union 合并直接进入最终结果池的。
- **是否命中"空 primary 恒真"**：**是，直接证据**。

### Q40 — 小红书图文笔记模板 数字标题

- Baseline=10, d_only=0, g_only=8, **d_plus_g=3209（满目录）**
- Mode D 的 `decomposition` = `{"subject":"Xiaohongshu post","style":"graphic","output":"template"}`
- 机制与 Q39 完全相同：`output="template"` → 空 primary → 全目录平凡匹配。
- `strict_result_count=3209, relaxed_result_count=0`，与 Q39 一致。
- **是否命中"空 primary 恒真"**：**是，直接证据**。

### Q42 — 小红书封面模板 白底大字

- Baseline=10, d_only=0, **g_only(Mode C)=3209（满目录）**, **d_plus_g(Mode D)=2291（非满目录）**
- 这是本报告发现的最关键的"看似矛盾"案例，逐字比对两次独立 LLM 调用的输出：
  - Mode C：`{"subject":"Xiaohongshu cover","style":"minimalist","output":"template"}` —— `output="template"` 裸词，触发与 Q39/Q40 相同的空 primary bug → 3209。
  - Mode D：`{"style":"minimalist","output":"cover template"}` —— 注意这里**没有 subject slot**，且 `output` 的值是**两词短语** `"cover template"`。`buildSearchTokens("cover template")` 切分为 `["cover","template"]`，`"template"` 被停用词过滤掉，但 `"cover"` **不是**停用词，`primary=["cover"]`，非空。因此 `requiredSlots=1`，只有当记录 blob 包含"cover"这个词时才会 `allPrimary=true`——这是一次真实的（非平凡的）宽泛匹配，命中 2291 条记录，因为"cover"在目录里是一个高频通用词（同时出现在很多"cover template"/"cover design"类模板的 tag/topic 中），属于 `GENERIC_STANDALONE_REWRITE` 而非 `EMPTY_PRIMARY_VACUOUS_MATCH`。
- **重要结论**：Q42 在 D 模式"只有 2291 而不是 3209"**不能解释为"d（Stage 6 分词器）缓解了洪泛"**。真实原因是两次独立的、非确定性的 LLM 调用为同一个原始 Query 生成了两段不同的 decomposition 文本，其中一次恰好触发了空 primary bug，另一次没有触发但仍然通过一个真实的通用词触发了大规模（但非满目录）洪泛。这一发现同时也回答了 Prompt 0 第 14 节问题 7（"核实 Q42 与 Q39/Q40 之间 d 分词逻辑的介入差异"）——**差异不在 d，而在两次 LLM 调用本身的文本差异**。

## 6. Generic Slot Analysis

对全部 68 条 Query（不仅是 23 条洪泛 Case）的 `decomposition` 字段做 token 级统计（停用词表与生产代码 `STOPWORDS` 一致）：

| Token | 总出现次数 | 洪泛 Case 中出现 | 洪泛占比 | 平均 d+g | 最大 d+g |
|---|---:|---:|---:|---:|---:|
| design | 9 | 9 | **100%** | 1876 | 2687 |
| poster | 7 | 6 | 86% | 1496 | 2814 |
| products | 2 | 2 | 100% | 2308 | 2904 |
| pet | 2 | 2 | 100% | 1601 | 1602 |
| influencer | 2 | 2 | 100% | 1927 | 2184 |
| xiaohongshu | 2 | 2 | 100% | 2202 | 3209 |
| brand | 4 | 3 | 75% | 1194 | 1855 |
| visual | 5 | 2 | 40% | 625 | 1670 |
| branding | 4 | 2 | 50% | 902 | 1670 |
| graphic | 2 | 1 | 50% | 2040 | 3209 |
| cover | 4 | 2 | 50% | 1228 | 2291 |
| template（裸值，未经切词，作为完整 slot 值） | **2**（Q39、Q40，全68条中唯一两处） | **2** | **100%** | **3209** | **3209** |

（预设的 Prompt 关注词表核对结果：`fashion`、`playful`、`modern`、`layout`、`inspiration`、`style`、`image` 在 68 条 decomposition 数据中要么完全不出现（`NO_EVIDENCE`），要么只出现在非洪泛 Case 中（如 `fashion`→Q05, d+g=413, 未洪泛；`aesthetic`→Q18, d+g=360, 未洪泛）——说明 Prompt 里列出的这份预设词表**不完全准确**，真正与洪泛强相关的是 `design`、`poster`、`branding`、`brand`、`visual`、`graphic`、`cover` 等词，以及最关键的裸值 `"template"`。)

**回答任务五问题**：

1. **通用独立 slot 能解释多少个 D 组洪泛 Case？** 直接可归因 15/23（65%，`GENERIC_STANDALONE_REWRITE` 分类），另有 6/23 属于"无单一裸词但多个 2 词短语联合放大"（`DECOMPOSITION_TOO_BROAD`），二者合计 21/23 与"低信息量/宽泛检索路径"这一大类直接相关。
2. **是否能解释全部 23 条？** 不完全是同一机制：Q39、Q40 是纯粹的空 primary 平凡为真（`requiredSlots=0`），与"generic 但非空"的通用词洪泛（如"design"单独命中 100% 目录相关记录里的一部分）在代码路径上是同一个 `allPrimary` 判断，但触发条件不同（`0===0` 恒真 vs 真实高频词的量级匹配）。
3. **哪些 Case 没有明显通用词却仍然洪泛？** Q10、Q26、Q27、Q28、Q43、Q48 这 6 条没有单一裸词/单一高频词标志，而是通过多个 2 词短语（如"collaboration design"、"brand design"、"character poster"）经 Union 合并联合放大，归类为 `DECOMPOSITION_TOO_BROAD`。
4. **同一个通用词与实体绑定时是否安全？** 是。例如"design"单独作为独立路径时是 100% 洪泛关联，但在 rewrite 顶层短语（如"museum product design"、"pet photography studio design"）中与 subject 实体结合出现时，该短语作为一个整体被 `buildSearchTokens` 切分为多 token AND 匹配，不会导致同等程度的洪泛（这类顶层短语路径的 `strict_result_count` 均显著低于对应的裸 slot 路径贡献量，见 CSV 中 `strict_match_behavior`/`relaxed_match_behavior` 字段）。
5. **单独执行与实体绑定执行之间有什么差异？** 单独执行时 `requiredSlots` 只包含该通用词自身（1 个 token），命中门槛极低，一旦目录中大量记录标注了这个通用词（如"design"/"poster"广泛存在于 tags/topics/params），几乎必然 strict 命中；实体绑定执行时 `requiredSlots` 包含通用词 + 实体词（≥2 个 token 的 AND），命中门槛显著提高。这正是 Guard C（slot 实体绑定）提出的直接依据。

## 7. Empty-primary and Vacuous-match Audit

- **文件**：`app/[locale]/(public)/search/page.tsx`
- **函数**：`scoreBlob`
- **行号**：working tree 第 301-326 行；`git show HEAD` 版本（pre-Stage-6）第 254-273 行，两者公式逐字相同：
  ```
  const requiredSlots = tokens.primary.length + aliasGroups.length;
  ...
  allPrimary: primaryHitsOnly + groupHits === requiredSlots,
  ```
- **逻辑**：当 `tokens.primary` 长度为 0 且 `aliasGroups` 长度为 0 时，`requiredSlots=0`；无论 `blob` 内容是什么，`primaryHitsOnly=0, groupHits=0`，`0===0` 恒真，`allPrimary` 恒为 `true`。这是一个数学上的"空集合上的全称量词平凡为真"问题，与 `[].every(...) === true` 在语义上完全等价（虽然生产代码实现为求和相等比较，而非字面 `.every()` 调用）。
- **命中 Case**：Q39（`output="template"`）、Q40（`output="template"`）直接命中；Q42 仅在 Mode C 的独立 LLM 调用中命中（Mode D 未命中，因为 D 的 `output` slot 值是"cover template"而非裸"template"）。经过对全部 68 条 `decomposition` 字段的穷举检查，**这是全部 68 条 Query 中唯一两处（Q39、Q40）在 Mode D 触发的裸值 `"template"` 实例**，未发现其他停用词裸值实例（`STOPWORDS` 集合中的其他词——the/a/an/of/in/on/is/are/and/or/to/for/with/by/at/as/be/this/that/的/了/和/及/topic/topics/theme/themes/category/categories/insights/highlights/guide/guides——均未在任何 Query 的 decomposition/rewrite 输出中单独出现）。
- **是否充分原因**：**是**，Q39/Q40 两例均直接 100% 复现（`strict_result_count` 恰好等于目录总量 3209，`relaxed_result_count=0`），无需其他因素配合。
- **是否必要原因**：**否**，对其余 21 条洪泛 Case 不是必要条件——那 21 条洪泛不依赖任何 token 集合变空，而是依赖非空但过于宽泛/通用的 token 单独或联合造成大规模（但非平凡为真）的真实匹配。
- **风险等级**：**高**（一旦触发即 100% 全目录污染，且完全不受 `hasStrict` 门控保护，因为 `hasStrict` 只看原始 Query 自身的 baseResult，不会因为某个 rewrite/decomposition 路径洪泛而被拦截）。
- **该问题是充分/必要/共同/仅理论风险**：对 Q39/Q40 是**充分原因**；对整体 23 条洪泛现象是**共同原因之一**（与 `GENERIC_STANDALONE_REWRITE`、`DECOMPOSITION_TOO_BROAD`、`MERGE_UNION_FLOODING` 并列的四类根因之一，占比 2/23）；不是"仅理论风险"——已有 2 个真实数据案例（且 Q42 在另一模式下是第 3 个）实际触发。

## 8. Original Entity Preservation

统计口径：在 `rewrites` 数组 + `decomposition.subject`（若存在）构成的"Rewrite 整体输出"层面判断实体是否保留；同时单独标注"哪些具体 slot 路径缺乏实体"。

| 状态 | 数量（23 条中） |
|---|---:|
| PRESERVED_ALL | 0 |
| PRESERVED_PARTIAL | **23** |
| LOST | 0 |
| UNKNOWN | 0 |

**与洪泛关系**：全部 23 条洪泛 Case 的原始核心实体在 Rewrite 整体层面都**至少保留一次**（要么在 `decomposition.subject`，要么在某条 `rewrites[]` 的完整短语中）——这直接推翻了"Rewrite 把实体完全丢了导致洪泛"这一朴素假设。真正导致洪泛的是：**decomposition 把 style/scene/output/era/mood 当作与 subject 平级、彼此独立的检索路径**（见 `flattenPaths()`，`lib/searchRewrite.ts:494-509`），每个非 subject slot 的值单独执行 `buildSearchTokens()` → `scoreQueryTokens()`，这些路径从设计上就不携带任何实体信息——不是"丢失"，而是"从未被设计为携带"。这是 `PRESERVED_PARTIAL` 与"实体丢失"两种描述的关键区别：前者准确描述了当前架构的实际行为（有些路径携带实体、有些路径设计上就不携带），后者是不准确的简化。

**实体未丢失但仍洪泛的 Case**：全部 23 条都属于此类（因为 0 条被判定为 LOST）——这本身就是本报告最重要的架构级发现之一：**修复方向不应该是"防止 Rewrite 丢弃实体"（因为它本来就没丢），而应该是"防止非实体绑定的独立 slot 路径单独宽泛检索"**（对应 Guard C）。

## 9. Count-increased-but-worse

- 字段：`hard_queries_68_before_after.csv` 的 `count_increased_but_relevance_decreased`，独立重算（非沿用 Prompt 0 数字，且发现与 Prompt 0 假设不一致，见下）。
- **实际数量**：22（与 Prompt 0 §7 独立重算的数字一致）。
- **与 23 条洪泛的交集**：**仅 7 条**（Q11, Q25, Q28, Q41, Q45, Q47, Q48）——**不是** Prompt 0 第 14 节"Next Analysis Priorities"第 3 条中假设性表述的"已知 22/23 重叠，唯一例外是 Q06"。
- **⚠️ 与 Prompt 0 文档的冲突记录**：Prompt 0 报告第 14 节将"22/23 重叠"列为一个**待验证的假设**（原文："确认这一数字关系背后的机制是否可推广"），而非一个已确认事实。本报告独立重新解析 `hard_queries_68_before_after.csv` 的 `count_increased_but_relevance_decreased` 与 `d_plus_g_result_count` 两列后发现，该假设**不成立**：22 条中只有 7 条同时出现在 23 条洪泛列表中；反过来 23 条洪泛 Case 中有 16 条的 `count_increased_but_relevance_decreased` 字段值为 `false`（例如 Q39、Q40 两个满目录 Case 该字段都是 `false`）。**本报告采用独立重算的 7/23 交集数字作为权威结果**，因为它直接来自对同一份原始 CSV 两个字段的逐行解析，而非转述。这提示 `count_increased_but_relevance_decreased` 字段本身可能有独立于"是否达到 1000+ 洪泛门槛"的判定逻辑（其触发的 22 条 Case 的 `d_plus_g_result_count` 集中在个位数到 900 左右的中等区间，例如 Q07=870、Q13=512、Q61=242，均远低于 1000），即该字段更侧重捕捉"中等规模的数量增长伴随相关性下降"，而非极端洪泛。
- **非 1000+ 但质量严重下降的 Case**：确认存在，共 15 条（22 减去与 23 条洪泛重叠的 7 条），例如 Q07（meme格式国风梗图模板，d+g=870）、Q13（汉服马面裙叠穿灵感图，d+g=512）、Q61（decodable readers CVC words，d+g=242）——这些应被归类为 `MODERATE_EXPANSION`（详见任务八分类），不属于本阶段 CSV 输出范围（CSV 仅覆盖 23 条 `>=1000` 的 D 组洪泛 Case），但作为"洪泛问题并非唯一的相关性风险来源"的佐证记录于此。

## 10. Control Cases

选择依据：从全部 68 条中按字段值排序挑选，非主观挑选支持结论的样例。

### 正常 Rewrite 生效但未洪泛（PARTIAL 判定，d+g<1000）
- **Q18**（clean girl aesthetic skincare packaging mockup）：`attribution=d_plus_g_joint_synergy`, `g_only=98`, `d_plus_g=360`, `final_verdict=PARTIAL`。是全部 68 条中唯一一个"PARTIAL + 非洪泛 + joint_synergy"组合，可作为"Rewrite 有效但未失控"的正面对照。

### d_only 正常 Case（未洪泛，`d_only` 有实质改进）
- **Q64**（maker space label set printable）：`d_only=109`（相对 baseline=10 有实质提升，且远低于 1000）
- **Q08**（weirdcore aesthetic sticker design）：`d_only=82`
- **Q21**（二手奢侈品鉴定品牌视觉）：`d_only=57`

（全部 68 条中 `d_only` 最大值为 844，即使是 d_only 表现最强的 Case 也从未接近 1000 门槛，进一步印证第 3 节"d 从不单独导致洪泛"的结论。）

### g_only 未洪泛 Case
- **Q66**（sub tub emergency lesson plan poster）：`g_only=100`, `d_plus_g=100`
- **Q30**（手冲咖啡工作室视觉手册）：`g_only=88`, `d_plus_g=112`——这正是 `scoreBlob` 注释中提到的"Stage 6 relaxed 阈值解耦"要修复的历史回归案例原型 Query，本阶段确认它在当前 Stage 7 D 模式下**没有洪泛**（112，远低于 1000）。
- **Q58**（behavior clip chart classroom management）：`g_only=64`, `d_plus_g=101`

### joint-synergy Case（`attribution=d_plus_g_joint_synergy`，全 68 条中共 3 条，非"假设存在"而是逐行核实存在）
- **Q06**（genshin impact Furina fanart wallpaper 4k）：`d+g=1569`，**本身就在 23 条洪泛列表中**——是"部分改进但同时洪泛"的矛盾案例：judge 认为结果聚焦到了 Genshin Impact 角色（`core_intent_preserved=true`），但仍缺乏 Furina 专属的 fanart/wallpaper，说明即使实体被部分保留，`GENERIC_STANDALONE_REWRITE`（fanart/wallpaper 独立路径）仍然会稀释精确度。
- **Q12**（松弛感生活方式插画）：`d+g=3154`，同样在洪泛列表中，同样的矛盾模式。
- **Q18**（clean girl aesthetic skincare packaging mockup）：`d+g=360`，**唯一未洪泛的 joint-synergy Case**——三者对比的关键差异在于 Q18 的 decomposition 未产生任何符合第 6 节"高洪泛关联词"清单的裸词/高频词独立路径（其 rewrites/decomposition 内容更贴近具体的 skincare packaging 场景短语，未拆出类似"design"/"poster"这类目录高频词作为独立 slot）。

**"good rewrite" vs "bad rewrite" 可区分特征（回答 Prompt 0 §14 第 5 条）**：三个 joint-synergy Case 的核心差异不在于"是否保留实体"（三者 subject 都保留），而在于**其余 decomposition slot 是否恰好是目录高频通用词**。Q06/Q12 的 style/mood/output slot（fanart/wallpaper/illustration/relaxed）本身就是全 68 条统计中与洪泛强相关的词；Q18 没有落入这一词表。这与第 6 节"通用独立 slot"结论完全一致，属于同一机制在"改进"与"洪泛"两个维度上的双重体现——**一个真正安全的 rewrite 不是"没有独立 slot"，而是"独立 slot 恰好不是目录高频通用词"**，这个特征目前完全依赖运气（LLM 输出内容），没有任何代码层面的保护。

## 11. Root Cause Distribution

**Primary root cause（23 条，每条恰好一个 primary）：**

| Root cause | 数量 | 占比 |
|---|---:|---:|
| GENERIC_STANDALONE_REWRITE | 15 | 65.2% |
| DECOMPOSITION_TOO_BROAD | 6 | 26.1% |
| EMPTY_PRIMARY_VACUOUS_MATCH | 2 | 8.7% |

**Secondary root causes（每条可有多个）：**

| Root cause | 数量 |
|---|---:|
| MERGE_UNION_FLOODING | 23（全部） |
| RANKING_CANNOT_RECOVER | 19 |
| GENERIC_STANDALONE_REWRITE（作为 Q42 的次要标注，因其在 Mode C 下的另一表现） | 1 |
| OR_GROUP_TOO_PERMISSIVE | 1（Q16，含两个 alias group + 独立 output slot 叠加） |

**Responsible layer：**

| Layer | 数量 |
|---|---:|
| decomposition_validation | 21（GENERIC_STANDALONE_REWRITE + DECOMPOSITION_TOO_BROAD 两类） |
| query_planning | 2（EMPTY_PRIMARY_VACUOUS_MATCH，Q39/Q40，因为该 bug 位于 `scoreBlob`，属于检索路径构造/评分环节） |

## 12. Candidate Guard Evaluation

逐项评估见 `stage7_flood_guard_design_2026-07-14.json` 的 `candidate_guards` 数组（Guard A-K 共 11 项，含 id/name/status/target_layer/cases_addressed/risks/implementation_notes/test_requirements 全部字段）。摘要：

| Guard | 状态 | 可解决 Case 数 |
|---|---|---:|
| D — 空 primary fail-closed | **RECOMMENDED** | 2（Q39、Q40）+ 消除 Q42 在 Mode C 下的同类风险 |
| H — 目录词频统计 | **RECOMMENDED**（Guard A 的依赖基础设施） | 支撑 A，间接覆盖 15 |
| A — 低信息量独立 slot 过滤 | **RECOMMENDED** | 15（GENERIC_STANDALONE_REWRITE 全部） |
| C — slot 实体绑定 | **RECOMMENDED** | 6（DECOMPOSITION_TOO_BROAD 全部）+ 对 A 类 Case 的额外防御 |
| B — Rewrite 必须保留实体 | SUPPORTING | 0（因为 23/23 已经是 PRESERVED_PARTIAL，此 Guard 主要是防止未来回归，不解决当前已观测到的 Case） |
| G — 分层 Merge，原始结果优先 | SUPPORTING | 0（不减少匹配集合大小，只改变展示顺序） |
| E — 单路径候选预算 | DEFERRED | 理论上可覆盖全部 23，但被判定为治标不治本 |
| F — 结果膨胀回退 | DEFERRED | 理论上可覆盖全部 23，需要运行时基线比较，本阶段未验证可行性 |
| I — 静态通用词黑名单 | **NOT_RECOMMENDED** | 会硬编码到 68 条 Query 的具体词表，且不支持 CJK 对称词表 |
| J — 二次 LLM Judge/Confidence | **NOT_RECOMMENDED** | 增加延迟成本且引入第二层非确定性，无法可靠判断这是一个确定性的 token 计数 bug |
| K — 仅截断 Top N | **NOT_RECOMMENDED** | 已经存在（`.slice(0,80)`）且已被证明不足以解决问题——Q39/Q40 是在这个截断**之前**的匹配集合层面就已经污染为全目录，截断只是隐藏了匹配集合错误的规模，不修复错误本身 |

## 13. Recommended Minimal Fix

**推荐 Guard 集**（按执行顺序）：

1. **Guard D**（空 primary fail-closed）——在 `scoreBlob()` 中，当 `requiredSlots === 0`（即 `tokens.primary.length === 0` 且 `aliasGroups.length === 0`）时显式返回 `allPrimary: false`，而非落入 `0 === 0` 的平凡为真分支。这是单行级别的、无回归风险的修复，直接解决 Q39、Q40 及 Q42 在 Mode C 下的同类风险。
2. **Guard H**（目录词频统计基础设施）——为 Guard A 提供判断依据：统计每个 token 在 `templateSearchBlob`/`nanoInspiration` 中的文档频率。
3. **Guard A**（低信息量独立 slot 过滤）——基于 Guard H 的频率信号，拒绝"单 token 且目录频率超过阈值"的独立 decomposition slot 路径，覆盖 15 条 `GENERIC_STANDALONE_REWRITE` Case。
4. **Guard C**（slot 实体绑定）——要求非 subject 的 decomposition slot（style/scene/output/era/mood）必须与 subject 或原始 Query 的高信息量 token 共享至少一个 token，否则合并回 subject 路径或丢弃，覆盖剩余 6 条 `DECOMPOSITION_TOO_BROAD` Case。

**Reject 后 fallback**：
- Guard D 触发时：该路径对该记录返回 `allPrimary:false`，路径本身仍然执行，只是不再对空目录集平凡匹配——原始 Query 自身路径不受影响。
- Guard A/H 触发时：该 decomposition slot 被从 `flattenPaths()` 输出中剔除，不作为独立路径执行；原始 Query 与其余幸存的 rewrite/slot 路径正常执行。
- Guard C 触发时：该 slot 要么与 subject 合并成一个联合路径执行，要么被丢弃（无 subject 时）。
- **全部 Guard 都拒绝时的兜底行为**：与今天 `getMultiQueryPaths` 现有的"无可执行路径"行为完全一致（等同于 Path B/refusal/empty-decomposition 响应）——不引入新的失败模式。

**结构化诊断字段**：`guard_id`、`query_id`、`rejected_path_text`、`rejection_reason`、`catalog_frequency_at_reject_time`、`fallback_action_taken`、`path_result_count_before_reject`、`timestamp`（完整定义见 JSON `diagnostic_fields`）。

**需要修改的 production 文件**：仅 `app/[locale]/(public)/search/page.tsx`（`scoreBlob`、`buildSearchTokens`、`scoreQueryTokens`、`SearchPage` 中约 719-745 行的 decomposition-slot 路径迭代逻辑）。

**暂不应实施的高风险方案**：Guard I（静态黑名单，硬编码风险）、Guard J（二次 LLM Judge，延迟/成本/非确定性风险）、Guard K（仅 Top N 截断，治标不治本）。

## 14. Required Test Matrix

完整清单见 JSON `required_tests`（16 项），涵盖：

- 空 primary token（Guard D 核心用例）
- 通用独立 slot（Guard A 核心用例）
- 通用词 + 实体组合（验证 Guard A 不误伤）
- 原始实体保留（回归防护）
- 错误实体替换回退（防御性用例，本次未观测到真实案例但属必测）
- 合理泛化路径保留（`乔丹鞋 → 篮球鞋` 类案例，来自 `lib/searchRewrite.ts` NAMED-ENTITY RELAXATION RULE 注释，本 68 条 Query 中未出现该具体 Query，但规则本身是生产代码的一部分，必须有独立测试覆盖，不能因为不在 68 条中就遗漏）
- 纯英文 Query
- 中英文混合 Query
- Protected Phrase（`lib/query_phrase_aliases.ts`）
- 合理 Alias（如 Q15 的 k-beauty/skincare alias group）
- CJK tokenizer fallback
- Empty rewrite / Path B 响应
- Refusal 场景回退
- Same-query-only 去重
- 合法多 slot rewrite 端到端
- Cache TTL 回归（7 天成功 TTL / 10 分钟负缓存 TTL 不应被新 Guard 影响，因为 Guard 运行在缓存读取之后）

## 15. Risks and Limitations

- **human label 覆盖率 0/68**：本报告引用的全部 PASS/PARTIAL/FAIL 判定均来自 LLM Judge（gpt-4o-mini），未经过人工复核（继承自 Prompt 0 §9 已确认的缺口）。
- **Mode A/C 离线重建**：pre-Stage-6 分支通过 `git show HEAD` 文本重建而非真实历史模块导入，虽然本报告已核实 `scoreBlob` 公式在两版本间逐字相同，但不能排除其他未被本次检查覆盖的函数存在同类差异。
- **目录漂移未量化**：baseline（2026-07-07）与 Stage 7 harness 运行（2026-07-13）之间 `nano_inspiration.json` 内容是否发生变化未被量化，本报告的洪泛计数可能部分反映目录内容变化而非纯代码/Rewrite 效应。
- **LLM 非确定性**：本报告已用 Q01、Q39、Q42、Q53 四个具体案例直接证实 Mode C 与 Mode D 对同一 Query 产生不同的 rewrite/decomposition 文本——这意味着"23 条洪泛 Case"本身是**某一次运行的快照**，而非一个稳定、可重现的固定集合。重跑（本阶段被禁止）大概率会得到一个内容重叠但不完全相同的洪泛集合。
- **缺失 per-slot 独立结果数**：harness 没有单独记录"每个 decomposition slot 单独执行时匹配多少条记录"，本报告中 `flooding_slot`/`flooding_token` 的归因是基于 decomposition 内容 + 代码逻辑 + 聚合 `strict_result_count`/`relaxed_result_count` 的推断（`INFERRED_FROM_CODE`/`INFERRED_FROM_RESULT_PATTERN`），而非直接测量值。
- **推断与直接证据的区别**：直接证据 = CSV 原始字段值、代码逐行读取、`git show` 比对；推断证据 = per-slot 独立计数归因、"normalized_query"字段（`normalizeForSearch()` 的确切输出未被任何 CSV 持久化，只能从代码逻辑推导）。CSV 输出中对应字段已标注 `INFERRED_FROM_CODE`。
- **不能仅凭本阶段宣布效果改善**：本报告只诊断根因、评估候选 Guard，未实现、未测试、未测量任何修复方案对 68 条 Query 实际结果的影响。任何"这样修后会变好"的判断都是基于代码逻辑推导，不是实测结果。
- **Prompt 0 假设的一处已发现且已修正的错误**：`count_increased_but_relevance_decreased` 与 23 条洪泛的重叠不是 22/23，而是 7/23（详见第 9 节）——这是本报告在方法论上最重要的一次"直接重新解析优先于转述"的产出。

## 16. Readiness for Prompt 2

**READY_WITH_LIMITATIONS**

理由：
- 23 条 d+g 洪泛 Case 已全部逐条分析（非抽样），Q39/Q40/Q42 三个 full-catalog 相关案例已完成完整机制级分析并给出确切代码证据（文件、函数、行号）。
- A/B/C/D 洪泛数量已从原始 ablation CSV 独立重算，且发现并记录了 Mode C/D 非确定性差异这一此前未被充分强调的重要限制。
- 空 primary / vacuous match 风险已在代码层面直接定位（`scoreBlob`，行号已给出），确认为 Q39/Q40 的充分原因，且已排除该 bug 是 Stage 6/7 新引入的可能性（pre-Stage-6 版本存在完全相同的公式）。
- 通用词假设已用全 68 条数据定量验证（而非仅检查预设词表），得到具体的量化占比（如"design"100%洪泛关联）。
- 原始实体保留已系统统计（0 LOST / 23 PRESERVED_PARTIAL / 0 PRESERVED_ALL），并给出了比"实体丢失"更精确的机制描述（slot 级别 vs bundle 级别的实体携带差异）。
- 根因分布已生成（primary/secondary/responsible_layer 三个维度）。
- 最小 Guard 集已明确（D→H→A→C 四步顺序，含 fallback 与诊断字段设计）。
- CSV 含 23 条唯一数据，JSON 合法，均已验证（见下方最终回复中的验证结果）。

不是纯粹 READY 的原因：
- (a) 人工验收仍然缺失（继承自 Prompt 0，未在本阶段解决，也不在本阶段范围内）；
- (b) Mode A/C 的"neither"基线仍是离线重建而非真实旧代码路径直接执行；
- (c) 目录内容漂移仍未量化；
- (d) 新发现的限制：23 条洪泛集合本身是一次非确定性 LLM 运行的快照，不是保证可重现的稳定集合——Prompt 2 在设计测试用例时应使用**确定性的合成/构造测试**（例如手工构造一个 decomposition 恰好为 `{"output":"template"}` 的场景）而非依赖能否在重跑中复现某个具体 Query 的洪泛表现。

这些限制不阻塞 Prompt 2 进入 Guard 设计与实现阶段，因为 Guard D/A/C/H 针对的是**代码层面的确定性机制**（token 计数、词频、slot 结构），不依赖于某次 LLM 调用是否恰好复现了某个具体 Query 的洪泛——只要机制成立（已用直接代码证据确认），Guard 就是有意义的，无论具体哪 23 条 Query 在下一次运行中洪泛。
