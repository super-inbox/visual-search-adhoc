# Curify Frontend 数据驱动 Multi-Intent 搜索系统 — 仓库审计报告

---

## 1. 仓库状态

| 项目 | 详情 |
|------|------|
| 当前分支 | `jwang/vercel` |
| 远程追踪 | `origin/jwang/vercel`，与远程同步 |
| 工作树状态 | **干净（无未提交修改）** |
| 最新提交 | `151c8759` — `gallery: strip scraping-artifact trailers from nanobanana.json (3090 prompts)` |
| 前5条提交 | 151c875 strip trailers / 95be162 search within= / 17b5668 intent chip Phase1 / af768fe LLM-tag output-type / 81896ca taxonomy 14 slugs |

---

## 2. 关键文件地图

| 用途 | 精确路径 | 关键函数/字段 | 重要性 |
|------|---------|--------------|--------|
| 搜索页服务端 | `app/[locale]/(public)/search/page.tsx` | `SearchPage`, `buildSearchTokens`, `scoreQueryTokens`, `normalizeForSearch`, `looksLikeGarbageQuery` | 整条搜索管道的入口，含分词/匹配/LLM重写/意图芯片 |
| 搜索结果客户端 | `app/[locale]/(public)/search/SearchResultsClient.tsx` | `SearchResultsClient` | 渲染例子网格、模板列、意图芯片行、低结果跟踪 |
| 意图芯片聚合器 | `lib/intent_clusters.ts` | `topIntentChips`, `OUTPUT_TYPE_SLUGS`, `SYNONYM_FOLDS` | **Multi-Intent 核心**：从匹配模板的 `topics[]` 聚合 19 个 output-type slug，Phase 1 实现 |
| 搜索索引 & 跳转 | `lib/searchIndex.ts` | `TIER2_SUGGESTIONS`, `ALL_SUGGESTIONS`, `SuggestionEntry` | 拼写建议、别名（含 "cat" 别名导致跳转）、tier 分层 |
| LLM 查询重写 | `lib/searchRewrite.ts` | `rewriteQuery` | 结果<3 时调用 gpt-4o-mini 提出备选短语，回退为空列表 |
| LLM 模板匹配 | `lib/searchTemplateMatch.ts` | `matchTemplatesForQuery` | 懒加载：客户端挂载后才触发，渲染"Generate from template"卡片 |
| 生成模板区块 | `app/[locale]/(public)/search/GenerableTemplatesSection.tsx` | `GenerableTemplatesSection` | 客户端发 POST 到 `/api/search-template-match` |
| 搜索模板匹配 API | `app/api/search-template-match/route.ts` | POST handler | 节点路由，代理 `matchTemplatesForQuery` |
| 灵感数据 | `public/data/nano_inspiration.json` | `id`, `template_id`, `topics`, `tags`, `search_aliases`, `params`, `locales` | 3071 条灵感记录，61.5% 有 topics |
| 模板数据 | `public/data/nano_templates.json` | `id`, `topics`, `rank_score`, `locales`, `batch` | 287 条模板，100% 有 topics |
| 分类法 | `lib/taxonomy.json` | `tier1`, `tier2`, `tier3`, `tier4`, `content_shapes`, `gallery_tag_to_topics` | 10 个 tier-1 主题，107 个唯一模板话题 |
| 主题注册中心 | `lib/topicRegistry.ts` | `buildTopicRegistry` | 服务端专用，从 nano JSON 推导 topic→template 索引 |
| 中文标准化 | `lib/zh_normalize.ts` | `tsToSc` | 繁→简字符规范化，在 `normalizeForSearch` 中调用 |
| 搜索评估集 | `scripts/configs/search_eval_set.json` | `queries[].query`, `expected`, `expected_templates` | 125 条评估查询，含 PASS/WARN/FAIL 判定基准 |
| 搜索评估脚本 | `scripts/eval_search.cjs` | `scoreOnce`, `verdict`, `templateVerdict` | 主要离线回归测试，可用 `--matcher` 标志增加 LLM 成本 |
| 别名补充脚本 | `scripts/topup_search_aliases.py` | `_inspiration_matches_filter`, `fields_any` | 按家族批量追加 `search_aliases` |
| 预填词池 | `lib/popularPrefillQueries.ts` | `POPULAR_PREFILL_QUERIES` | ~42 条 SearchBar 旋转占位词，6 条问题查询来源于此 |
| 预填词检查器 | `scripts/inspect_prefill_pool_quality.cjs` | `scoreOnce`, verdict GOOD/WEAK/NARROW/OK/THIN/EMPTY | 核验每条占位词的结果质量 |
| 搜索质量文档 | `docs/search-quality.md` | 已发布项目 + 周期表 | 主要搜索改进记录 |
| 搜索伞状追踪器 | `docs/search-and-content.md` | Thread a/b/c/d | 最全面的跨线程追踪文档 |
| 评估集渲染文档 | `docs/search-eval-set.md` | 125 条查询评估表 | 自动从 JSON 渲染，人工可读 |

---

## 3. 当前搜索数据流

```
用户输入查询
    │
    ▼ [server] app/[locale]/(public)/search/page.tsx
    │
    ├─ (1) 参数解析
    │      q.trim().toLowerCase() → query  [line 231]
    │      within.trim().toLowerCase() → withinSlug  [line 231]
    │      无 query → redirect 首页
    │
    ├─ (2) WC 国家快速跳转  [line 250-262]
    │      matchBareWcCountryQuery(query) → lib/wcCountryRouting.ts
    │      matchWcCountryQuery(query) → lib/wcCountryRouting.ts
    │      命中 → redirect /topics/<country>-world-cup
    │
    ├─ (3) 分词规范化  buildSearchTokens(query)  [line 264]
    │      normalizeForSearch = toLowerCase + ×→x + tsToSc(繁→简)
    │      按 [\s,..:=·/|()\[\]+*]+ 分词，过滤停用词
    │      单词 ASCII 单 token：保守复数还原（-s/-es/-ies）
    │      CJK 无空格长串 → 字符 bigram
    │
    ├─ (4) Topic slug 精确跳转 (ALL_SUGGESTIONS) [line 330-384]
    │      lib/searchIndex.ts: TIER2_SUGGESTIONS + 其他 tier
    │      精确匹配 slug/label/alias/本地化名称 → redirect /topics/<slug>
    │      单一子串无歧义命中 → redirect
    │      searchFallback=true 的条目不跳转，继续到搜索页
    │
    ├─ (5) i18n 模板 blob 构建  [line 297-318]
    │      messages/{locale,en,zh}/nano.json
    │      每个 template_id → blob(category+title+description+what+who)
    │      normalizeForSearch 处理，多 locale 拼接
    │
    ├─ (6) 双 pass 匹配  scoreQueryTokens()  [line 430-537]
    │   ┌─ Template pass
    │   │   strictTpl: allPrimary 或 bigramHits ≥ bigramThr → template_id
    │   │   relaxedTpl: primaryHits ≥ ⌈N/2⌉（暂不用于模板 rail）
    │   │
    │   └─ Inspiration pass (逐条 nano_inspiration.json)
    │       blob = id + template_id + tags + topics + TEMPLATE_TOPICS + search_aliases + params + locales
    │       strict → 模板 strict 提升所有子灵感（promoteAllUnderStrictTpl=true 原始 pass）
    │       compound-noun 精度守卫：仅 param 命中 → 降为 relaxed
    │       最终：strict 非空用 strict，否则用 relaxed，截取 top 80
    │
    ├─ (7) LLM 查询重写（按需）  rewriteQuery()  [line 557-597]
    │      条件：严格命中 < 3 && !isBot && !isGarbage && query.length ≥ 2
    │      lib/searchRewrite.ts → gpt-4o-mini → 最多 3 条备选短语
    │      每条重写：promoteAllUnderStrictTpl=false 的 scoreQueryTokens
    │      结果按 inspiration id 合并（最高分胜出）
    │      usedRewrites 传给客户端用于"Also showing results for"提示
    │
    ├─ (8) ?within= 意图缩窄  [line 607-619]
    │      过滤 inspirations：template topics 或 inspiration topics/tags 含 withinSlug
    │      同样过滤 matchedTemplates
    │
    ├─ (9) Related topics 聚合  [line 623-643]
    │      匹配 inspiration 的 template_id → TEMPLATE_TOPICS → tier2/3 slug 计数
    │      取 top 8，无结果则回退 TIER2_SUGGESTIONS 前 8
    │
    ├─ (10) 模板 rail 构建  buildNanoFeedCards()  [line 650-689]
    │       lib/nano_page_data.ts：以匹配灵感优先覆盖默认预览图
    │
    ├─ (11) Gallery prompts（Redis）  [line 692-716]
    │       NANO_PROMPT_TAG_SET 中存在 query → nanoPromptsService.getNanoPromptsByTag
    │       过滤 revealing-female tag，限 12 条
    │
    ├─ (12) Intent Chip 聚合  topIntentChips()  [line 718-728]
    │       lib/intent_clusters.ts
    │       matchedTemplates.topics → 19 output-type slug 计数
    │       minCount=2，topN=5，synonym fold（art-prints→wall-art）
    │       withinSlug 激活时跳过（只显示激活 pill）
    │
    └─ (13) 渲染  <SearchResultsClient>  [line 730-744]
            [client] SearchResultsClient.tsx
            examples grid → ExampleImagesGrid（每个 template_id 最多 3 个）
            templates rail → NanoTemplateDetailClient
            lazy generable templates → GenerableTemplatesSection（POST /api/search-template-match）
            gallery prompts → PromptCard grid
            intent chips → "Explore further" 行
            related topics → 底部 Browse 行
            低结果 / 零结果 → track 事件
```

---

## 4. 当前 Multi-Intent 实现结论

**结论：当前 Multi-Intent 是「内容衍生（content-derived） + 分类法词汇表（taxonomy-defined vocabulary）的混合实现」，已在 Phase 1 上线。不是 hardcoded，不是 LLM zero-shot 生成。**

### 确认证据

**文件：** `lib/intent_clusters.ts`（全文 84 行）

**机制（第 55–83 行）：**
```typescript
// 函数 topIntentChips(templates, options)
// 输入：当前查询匹配到的 templates 列表（各自携带 topics[]）
// 步骤：
//   1. 遍历每个 template 的 topics[]
//   2. 过滤只保留属于 OUTPUT_TYPE_SET 的 19 个 slug
//   3. 同义词折叠：art-prints → wall-art
//   4. 每 template 去重计数（不双计同一 template 的重复 slug）
//   5. filter count >= minCount(2), sort desc, slice topN(5)
```

**词汇表来源（第 17–42 行）：**  
`OUTPUT_TYPE_SLUGS` = 19 个 slug，包括 infographic / anatomy / comic / step-by-step-tutorial / illustration / flashcards / recipes / mind-maps / study-sheets / art-prints / wall-art / memes / social-media-posts / stickers / mascots / character-ip / fan-art / selfies / scrapbooks。  
这 19 个 slug 由 LLM（`scripts/tag_templates_output_types_2026-06-19.py`，gpt-4o-mini）在 commit `af768fe7` 中标注到 285/287 个模板，一次性操作，标注结果**已持久化到 `nano_templates.json` 的 `topics[]` 字段**。

**调用点（`page.tsx` 第 718–728 行）：**
```typescript
const intentChips = withinSlug
  ? []
  : topIntentChips(matchedTemplates, { topN: 5, minCount: 2 });
```
`matchedTemplates` 来自第 (6) 步匹配结果，故意图芯片**直接反映当前查询的检索结果**，而非预定义枚举。

**结论对应：**
- ✅ **content-derived**：chips 从当前查询命中的模板话题中实时聚合
- ✅ **taxonomy-defined vocabulary**：19 个 slug 是预定义词汇表的子集（taxonomy.json 中包含这些 slug）
- ✅ 不是 LLM zero-shot（生成阶段 LLM 仅标注，不参与运行时）
- ✅ 不是 hardcoded（chip 内容按查询动态变化）
- ✅ topic co-occurrence：严格意义上是 "output-type slug 在结果集模板中的共现频率"

---

## 5. 两个 JSON 的 Topic 合并关系

### 文件概况

| 文件 | 记录数 | 顶层结构 | Topics 字段 | Topics 覆盖率 |
|------|-------|---------|------------|--------------|
| `nano_inspiration.json` | 3071 | `List[object]` | `topics?: string[]` | 61.5%（1889/3071） |
| `nano_templates.json` | 287 | `List[object]` | `topics: string[]` | **100%**（287/287） |

### 关键字段（nano_inspiration.json 单条示例）
```json
{
  "id": "template-herbal-dragon's-blood",
  "template_id": "template-herbal",
  "asset": { "image_url": "...", "preview_image_url": "..." },
  "params": { "herb_name": "dragon's blood" },
  "locales": { "zh": { "category": "中草药类", "title": "dragon's blood" } },
  "tags": ["botanical", "food", "herbal", "illustration"],
  "topics": ["school", "food-and-drink"],
  "search_aliases": ["当归", "中草药", "herbal remedy"],
  "allow_i18n": true
}
```

### 关键字段（nano_templates.json 单条示例）
```json
{
  "id": "template-herbal",
  "topics": ["learning", "science", "information-card", "infographic", "anatomy", "illustration", "art-prints", "wall-art"],
  "rank_score": 80.75,
  "batch": "hongjie28_patch2",
  "locales": { "zh": { "base_prompt": "...", "parameters": [...] }, "en": { ... } }
}
```

### 灵感与模板的链接关系
- **链接字段**：`nano_inspiration.json[n].template_id == nano_templates.json[m].id`
- **覆盖率**：3071 条灵感中有 285 个唯一 `template_id` 存在于 287 个模板中（2 个例外：`template-cultural-relic`, `template-dog-breed`，存在于灵感中但不在模板文件里）

### Topic 合并逻辑（搜索管道中的实际执行路径）

**`app/[locale]/(public)/search/page.tsx` 第 60–65 行**（预构建映射）：
```typescript
const TEMPLATE_TOPICS = new Map<string, string[]>();
for (const t of nanoTemplates as any[]) {
  if (typeof t?.id === "string" && Array.isArray(t.topics)) {
    TEMPLATE_TOPICS.set(t.id, t.topics);
  }
}
```

**第 475–488 行**（灵感 blob 构建）：
```typescript
const blob = normalizeForSearch([
  r.id,
  r.template_id,
  ...(r.tags ?? []),
  ...(r.topics ?? []),                          // ← 灵感自身 topics
  ...(TEMPLATE_TOPICS.get(r.template_id) ?? []), // ← 父模板 topics（合并！）
  ...(r.search_aliases ?? []),
  ...Object.values(r.params ?? {}),
  ...localeFields,
].filter(Boolean).join(" "))
```

**合并结论**：
1. 搜索 blob 将灵感自身 `topics[]` 与其父模板 `topics[]` **手动拼接**，实现合并
2. 主题不去重（同一 slug 若同时出现在灵感和模板，会在 blob 中出现两次，但不影响 tokenInBlob 的匹配结果）
3. 灵感的 topics 是**内容贡献性**（如 school / food-and-drink / china / anime）
4. 模板的 topics 是**创作输出类型** + **内容领域**混合（如 infographic / learning / science）
5. 两套 topics 词汇表**不完全重叠**：
   - 灵感专有 topics 276 个（如 argentina-world-cup / athleisure / before-after / 各国家名）
   - 模板专有 topics 47 个（如 art-prints / character-ip / ecommerce / gaming / mind-maps）
   - 共有 60 个

---

## 6. cat / cats 问题分析

### 确认行为差异

运行模拟发现：
- `"cat"` → query = `"cat"` → **跳转** `/topics/animal`（190+ 例子）
- `"cats"` → query = `"cats"` → **留在 /search**，匹配到 13 条 strict 灵感

两者最终用户体验**完全不同**。

### 根本原因

**原因 A（最可能，最高影响）：跳转检查使用原始 query，而非规范化后的 tokens**

`page.tsx` 第 231 行：`const query = q.trim().toLowerCase();`  
第 264 行：`const tokens = buildSearchTokens(query);`（tokens 中 "cats" → "cat"）  
第 330–383 行：跳转检查使用 `query`（原始字符串），NOT `tokens.primary[0]`。

`lib/searchIndex.ts` 第 40 行：`{ slug: "animal", aliases: ["pet", "pets", "wildlife", "creature", "dog", "cat"] }`

- `"cat"` 精确命中 `animal.aliases` → **redirect /topics/animal**
- `"cats"` 不在 aliases 中 → 子串检查：`animal.slug/label/aliases.includes("cats")` → 也无命中 → **不跳转**

**结论**：plural 规范化（buildSearchTokens 内）与 topic slug 跳转检查（使用原始 query）存在职责割裂，plural 规范化对跳转路径无效。

**原因 B（次要）：alias 列表仅覆盖 "cat"，未覆盖 "cats"**

即使跳转检查使用了 normalized token，当前 alias 列表也只明确写了 `"cat"`（未写 `"cats"`）。两个入口（cats as alias 和 plural-normalized cats → cat 的跳转检查）均缺失。

**原因 C（结果层面）：/topics/animal 与 /search?q=cats 的内容来源完全不同**

- `/topics/animal` 由 `lib/topicRegistry.ts` 驱动，加载**所有** `topics[] 包含 "animal"` 的模板，提供数百个例子
- `/search?q=cats` 仅返回 blob 中含 `\bcat\b` 的 13 条灵感，缺少 "animal" tagged 的整个大类

### 三个最可能根本原因总结

| # | 原因 | 具体证据 |
|---|------|---------|
| 1 | **跳转检查使用原始 query，plural 规范化在分词层，两者互不可见** | `page.tsx:231` query 赋值 vs `page.tsx:264` buildSearchTokens 赋值顺序；跳转检查在 `line 330` 用 query 做比对 |
| 2 | **alias 列表只注册单数形式 "cat"，未注册 "cats"** | `searchIndex.ts:40` animal.aliases 数组内容 |
| 3 | **跳转目标（/topics/animal）的 topic 索引与搜索页的 blob 匹配机制完全独立** | topicRegistry 按 topics[] 字段聚合；search 按 blob 字符串匹配；两者对同一 token 的命中集合不同 |

---

## 7. 六条 WARN Query 审计

### WARN 的定义来源

六条查询的注册来源为 `scripts/configs/search_eval_set.json` 中 `source: "prefill-pool-2026-06-14"`，被标注为 `expected: "rich"` 或 `"moderate"`。

**WARN 判定规则**（`scripts/eval_search.cjs` 第 316 行）：
```javascript
return actualBucket === expected ? "PASS" : "WARN";
```
- `before after kitchen organization makeover`：expected=`moderate`，actual（模拟）= `thin`（1 strict hit）→ **WARN**
- 其余5条：expected=`rich`，actual（模拟）= `moderate`（7 hits）或 `thin`（1 hit）→ **WARN**

这些查询由 `scripts/inspect_prefill_pool_quality.cjs` 在 2026-06-14 检查后采纳入 eval set（注解"Adopted to pool (path A)"），但其 `expected` 值与当前实际匹配结果存在偏差，代表**实际结果低于预期**的 WARN 状态。

`scripts/eval_search.cjs` 的 bucket 定义：

| Bucket | 含义 |
|--------|------|
| `rich` | ≥ 10 条有效灵感（strict 优先，否则 relaxed） |
| `moderate` | 3–9 条有效灵感 |
| `thin` | 1–2 条，应触发 search_lowresult 事件 |
| `empty` | 0 条，触发 search_noresult 事件 |

### 六条查询详细审计

| Query | 灵感证据 | 模板证据 | 当前失效点 | 初步分类 | 建议修复 |
|-------|---------|---------|----------|---------|---------|
| `before after kitchen organization makeover` | **有**：`template-home-organization-before-after-before-after-kitchen-organization-makeover`（6 关键词命中）等约 20 条关联灵感；expected=`moderate`；实际 strict=1，relaxed=4 | 有：`template-home-organization-before-after`（narrow but precise） | **strict 失效**：5 词 AND 匹配要求所有词同时出现在 blob，当前只有 relaxed 匹配通过⌈5/2⌉=3 词；期望 moderate(3+) 但 strict 仅1 | **E. 排名/严格度间隙** | 为 home-organization 模板添加 `search_aliases: ["before after makeover", "before-after transformation"]`，以通过 topical 严格匹配 |
| `paris travel itinerary` | **有**：`template-tourist-spot-watercolor-map-infographic-historic-landmarks-of-paris`（4 关键词），约 173 条相关灵感；strict=7（moderate），expected=`rich`(≥10) | 有：`template-tourist-spot-watercolor-map-infographic`, `template-travel-packing-guide-infographic`, `template-whimsical-travel-map` | **B. 灵感检索间隙**："itinerary" token 要求同时命中 paris + travel + itinerary；paris 出现在城市 params，itinerary 出现在模板 i18n，blob 不一定三者同时具备 | **B. 灵感检索间隙** | 在 paris 相关灵感上追加 `search_aliases: ["paris travel itinerary", "paris day trip"]`；或将 itinerary 模板别名扩展覆盖城市名 |
| `architecture empire state building` | **有**：`template-architecture-empire-state-building`（4 关键词命中，直接命中）；strict=1，expected=`rich` | 有：`template-architecture`, `template-world-landmark-vintage-info-poster`, `template-3d-region-landmark-map` | **B/E 复合**：`empire` 和 `state` 是高频停用词语境词汇（但未在停用词列表），`building` token 有字符边界问题；strict template=0（blob 不含 empire state 完整组合） | **B. 灵感检索间隙** | 对 architecture 类模板追加 `search_aliases: ["empire state building", "nyc landmark", "skyscraper"]`；为已有的单条 inspiration 补充 aliases |
| `childhood snacks then vs now` | **有**：`template-then-vs-now-comparison-infographic-childhood-snacks`（5 关键词命中）；但 "childhood" 不在停用词，5 词 AND 匹配；strict template=1（then-vs-now）；strict insp=7（moderate），expected=`rich` | 有：`template-then-vs-now-comparison-infographic` | **量级间隙**：有主题模板（then-vs-now）并有直接匹配灵感，但 strict 灵感仅7条（moderate），expected rich 需≥10 | **E. 排名间隙** | 为 then-vs-now 模板批量生成更多 childhood snack 主题的灵感例子；或降低 expected 到 `moderate` |
| `warmup routine running checklist` | **有**：`template-warmup-routine-running`（4 关键词命中）；但 strict templates=0（i18n blob 不含 "checklist"）；relaxed=7（moderate），expected=`rich` | 有：`template-warmup-routine`（narrow） | **D/B 复合**：`checklist` 不在 warmup 模板 i18n blob 中；全靠 relaxed-OR（⌈4/2⌉=2 词）提供 moderate 结果；strict 路径为空 | **D. 重写/同义词间隙** | 在 `template-warmup-routine` i18n 描述或 `search_aliases` 中加入 "checklist"; 或把 expected 修正为 `moderate` |
| `vintage stamp collection garden birds` | **有**：`template-vintage-stamp-collection-illustration-garden-birds`（5 关键词直接命中）；strict=1，relaxed=4，expected=`rich` | 有：`template-vintage-stamp-collection-illustration` | **B. 灵感检索间隙**：5 词严格 AND，"garden" 和 "birds" 需同时出现在 topical blob；当前只1条 strict 精确灵感，其余近义灵感（ocean-life / mountain-flora）只有 3 词命中 → relaxed | **B. 灵感检索间隙** | 为 vintage-stamp-collection 模板下所有灵感追加 `search_aliases: ["vintage stamp", "stamp collection illustration"]`，降低多 token strict 匹配门槛 |

---

## 8. 文档整理建议

### 现有日报文件

当前**不存在** `docs/daily_report/` 目录。以下文件为带日期的专项文档，风格接近日报：

| 文件 | 日期 | 性质 |
|------|------|------|
| `docs/seo-flashcard-learning-batch-2026-06-10.md` | 2026-06-10 | SEO 批生成日报 |
| `docs/seo-travel-batch-2026-06-10.md` | 2026-06-10 | SEO 批生成日报 |
| `docs/seo-business-news-visualization-batch-2026-06-12.md` | 2026-06-12 | SEO 批生成日报 |
| `docs/content-gap-corporate-news-editorial-2026-06-12.md` | 2026-06-12 | 内容缺口分析 |
| `docs/home-discoverability-ideas-2026-06-14.md` | 2026-06-14 | 主页发现性想法 |
| `docs/eval-framework-visual-search-benchmark-2026-06-14.md` | 2026-06-14 | 搜索评估框架 |
| `docs/taxonomy-gap-canva-pinterest-2026-06-14.md` | 2026-06-14 | 分类法缺口 |
| `docs/eval-framework-visual-intent-routing-2026-06-15.md` | 2026-06-15 | 意图路由评估框架 |

### 现有搜索相关重叠文档

| 文件 | 内容 | 是否重叠 |
|------|------|---------|
| `docs/search-and-content.md` | 四线程综合追踪器，最权威 | 主文档（正典） |
| `docs/search-quality.md` | 搜索质量改进记录表 + 周期日志 | 是 search-and-content 的子集 |
| `docs/search-eval-set.md` | 125 条评估查询渲染文档（自动生成） | 派生文档，保留 |
| `docs/search-generation-bridge.md` | Generation Bridge（GenerableTemplatesSection）规格 | 子专题 |
| `docs/gap-classifier-phase1.md` | 缺口分类器 Phase 1 规格 | 子专题 |

### 建议正典搜索评估文档

**`docs/search-and-content.md`** 应作为正典（canonical）搜索评估文档。它已包含：
- 四线程综合追踪
- 已发布改进历史
- 周期评审记录
- 下游规格文档的索引

### 建议合并目标

| 操作 | 说明 |
|------|------|
| 创建 `docs/daily_report/` | 将 8 个带日期文档移入（不执行，建议操作） |
| `docs/search-quality.md` → 合并入 `docs/search-and-content.md` Thread a 节 | 内容高度重叠 |
| `docs/eval-framework-visual-search-benchmark-2026-06-14.md` + `docs/eval-framework-visual-intent-routing-2026-06-15.md` → 合并为 `docs/eval-framework.md` | 同一评估工作流两个维度 |
| `docs/taxonomy-gap-canva-pinterest-2026-06-14.md` → 合并入 `docs/search-and-content.md` Thread b 节 | 分类法缺口属于 Thread b |

**当前未执行任何合并。**

---

## 9. 建议修改的文件

（注：仅为未来规划，当前不执行任何修改）

| 文件状态 | 路径 | 拟议职责 | 需要理由 |
|---------|------|---------|---------|
| **新建** | `lib/topic_resolver.ts` | 统一的话题解析器：输入 inspiration id + template id，输出合并去重后的 topic 数组 | 当前合并逻辑散落在 `page.tsx` blob 构建处，无独立抽象；未来 co-occurrence 计数需要单一调用点 |
| **新建** | `lib/topic_cooccurrence.ts` | 接收 Top-N 结果集，计算话题共现频率，返回排名 topic 列表 | 实现需求 6（cross-result topic co-occurrence），当前 `topIntentChips` 只做 output-type 过滤，不做全话题共现 |
| **修改** | `lib/intent_clusters.ts` | 扩展聚合器：增加高级意图簇映射（Learning/EdTech, Merch/Commerce 等业务覆盖层） | 当前只有 19 个 output-type slug；boss 要求的消费 vs 创作意图簇、Business Override 需要新映射 |
| **新建** | `lib/intent_taxonomy.ts` / `lib/intent_taxonomy.json` | 新的高级意图簇配置文件：定义 Learning Materials / Visual & Art / Merch & Commerce 等簇及其 slug 映射 | boss 指定的高级意图簇当前**不存在**于 taxonomy.json，需要独立配置 |
| **修改** | `lib/searchIndex.ts` | 在 animal.aliases 中增加 "cats"（或在跳转检查前先运行 plural 规范化） | 修复 cat/cats 行为不一致，防止 "cats" 绕过 topic 跳转落到 free-text |
| **修改** | `app/[locale]/(public)/search/page.tsx` | 跳转检查前对 query 运行 buildSearchTokens 并用 primary[0] 做别名匹配（单 token 情况），OR 在跳转匹配中额外检查 tokens.primary | 修复 cat/cats 根本原因 A |
| **新建** | `lib/business_override.ts` | 可配置的 business override 层：当检索结果包含 Learning/EdTech 或 Merch/Commerce 证据时优先提升对应意图簇 | 需求 9，当前无优先级覆盖机制 |
| **新建** | `docs/daily_report/` 目录 | 容纳日报文件 | boss 明确要求创建 |
| **修改** | `docs/search-and-content.md` | 新增 Multi-Intent 系统章节，指向 lib/topic_resolver.ts、lib/intent_clusters.ts | 作为正典文档需保持最新 |
| **修改** | `scripts/eval_search.cjs` | 增加 Multi-Intent chip 验证：检查特定查询的 topIntentChips 输出 | 验收标准实现 |

---

## 10. 最小可行实现计划

### Phase 1 — 数据加载器 / 话题解析器（基础）

**目标**：创建 `lib/topic_resolver.ts`，封装当前 `page.tsx` 中的 TEMPLATE_TOPICS 构建和 blob 合并逻辑。

**涉及文件**：新建 `lib/topic_resolver.ts`，修改 `app/[locale]/(public)/search/page.tsx`（使用封装函数）

**输入**：inspiration record + template id  
**输出**：`{ inspirationTopics: string[], templateTopics: string[], merged: string[] }`

---

### Phase 2 — Topic 共现计数

**目标**：为 Top-N 结果集建立话题共现频率计数，区分灵感贡献话题与模板创作话题。

**涉及文件**：新建 `lib/topic_cooccurrence.ts`

**算法**：
```
对每条 matched inspiration：
  resolved = topic_resolver(inspiration, template_id)
  对 resolved.inspirationTopics 中每个 topic：topicCounts[topic]++（内容贡献）
  对 resolved.templateTopics 中每个 output-type slug：intentCounts[slug]++（创作意图）
```

---

### Phase 3 — 高级意图簇映射

**目标**：新建 `lib/intent_taxonomy.json`，定义 boss 指定的 8 个高级意图簇及其 slug 映射；修改 `lib/intent_clusters.ts` 增加高级映射。

**映射示例（待定）**：
```json
{
  "Learning Materials": ["flashcards", "study-sheets", "mind-maps", "step-by-step-tutorial", "infographic", "anatomy"],
  "Visual & Art": ["illustration", "wall-art", "art-prints", "comic", "fan-art", "character-ip"],
  "Merch & Commerce": ["stickers", "mascots", "character-ip", "memes", "social-media-posts"],
  "Storytelling & Identity": ["selfies", "scrapbooks", "fan-art"],
  "DIY & Guides": ["step-by-step-tutorial", "recipes"]
}
```

---

### Phase 4 — Business Override

**目标**：新建 `lib/business_override.ts`，当检索结果包含 Learning/EdTech 或 Merch/Commerce 证据时，在意图簇排序中优先提升这些簇。

**规则示例**：若 intentCounts["flashcards"] + intentCounts["study-sheets"] ≥ threshold，则 Learning Materials 提升到列表首位。

---

### Phase 5 — UI 意图 Pills

**目标**：修改 `app/[locale]/(public)/search/SearchResultsClient.tsx`，使用高级意图簇标签（而非原始 slug）渲染 pills。

**现有基础**：Phase 1 chips 行已实现，只需更新标签映射和可选的分组渲染逻辑。

---

### Phase 6 — cat/cats 修复

**目标**：修复搜索结果行为不一致问题。

**方案 A（推荐）**：在 `app/[locale]/(public)/search/page.tsx` 的跳转检查中，对单 token 查询先运行 `buildSearchTokens(query).primary[0]` 做别名匹配，而非仅用原始 query。  
**方案 B（补充）**：在 `lib/searchIndex.ts` animal.aliases 中追加 `"cats"`（简单但治标）。

---

### Phase 7 — WARN 查询验证

**目标**：针对 6 条 WARN 查询执行别名补充（参见第 7 节建议），重新运行 `scripts/eval_search.cjs` 验证 bucket 提升。

**工具**：`scripts/topup_search_aliases.py` + `scripts/eval_search.cjs`

---

### Phase 8 — 测试

**目标**：为以下内容补充单元测试（Vitest）：
- `topic_resolver.ts` 的合并去重逻辑
- `topic_cooccurrence.ts` 的计数准确性
- `intent_clusters.ts` 的 topIntentChips 和 synonym fold
- `buildSearchTokens` 的 cat/cats 规范化行为
- 跳转检查与 plural 规范化的正确交互

---

### Phase 9 — 文档

**目标**：
1. 创建 `docs/daily_report/` 目录
2. 将 8 个带日期文档移入
3. 在 `docs/search-and-content.md` 追加 Multi-Intent 系统章节
4. 合并 `docs/search-quality.md` 中的历史部分

---

### Phase 10 — 本地演示

**目标**：在本地运行 `next dev`，验证：
- `cats` 和 `cat` 查询结果集一致
- `dinosaur` 返回 rich 结果
- `science poster` 出现 intent chips
- 6 条 WARN 查询达到 expected bucket

---

## 11. 验收标准

| 查询 | 当前状态 | 可测量验收标准 |
|------|---------|--------------|
| `cats` | `/search?q=cats` 返回 13 条 strict 结果 | 与 `cat` 行为一致；若 cat 跳转 /topics/animal 则 cats 也跳转同页；若 cat 进 /search 则两者均显示相同结果集（strict ≥ 10）|
| `cat` | `/search?q=cat` 跳转 `/topics/animal` | 跳转目的地不变；修复后 cats 应具备相同路径 |
| `dinosaur` | 需实际运行确认 | `eval_search.cjs` 对 "dinosaur" 输出 bucket ≥ `moderate`（≥3 条 strict）；`expected_templates ≥ thin` |
| `science poster` | 需实际运行确认 | 返回 ≥ 5 条 strict 灵感（包含 infographic 类模板）；intent chips 至少出现 "infographic" 或 "wall-art" |
| `before after kitchen organization makeover` | bucket=thin（1 strict），expected=moderate | 修复后 bucket ≥ moderate（≥3 strict），eval PASS |
| `paris travel itinerary` | bucket=moderate（7 strict），expected=rich | 修复后 bucket=rich（≥10 strict），eval PASS |
| `architecture empire state building` | bucket=thin（1 strict），expected=rich | 修复后 bucket ≥ moderate（≥3 strict），eval PASS（或修正 expected） |
| `childhood snacks then vs now` | bucket=moderate（7 strict），expected=rich | 修复后 bucket=rich（≥10 strict），eval PASS |
| `warmup routine running checklist` | bucket=moderate（7 relaxed only），expected=rich | 修复后 strict ≥ 3，bucket ≥ moderate，eval PASS |
| `vintage stamp collection garden birds` | bucket=thin（1 strict），expected=rich | 修复后 bucket ≥ moderate（≥3 strict），eval PASS |

---

## 12. 风险与待确认问题

以下问题**无法仅从仓库判断**：

1. **curify-studio 的 Admin Portal 状态**：`curify-studio` 是独立仓库，本仓库仅通过路径引用（`~/curify-studio/...`）提及其文件。Admin Portal 是否已集成 Agentic Eval（现改名为 Visual Intent Routing Eval）Tab？`taic_l1_candidates.json` 已存在于本仓库 `public/data/` 中（meta.catalog_size=227，125 条查询），但对应的 human labels 文件 `scripts/configs/taic_l1_human_labels_2026-06-16.json` 仅含 30 条标注（verdict_legend 为 accurate/biased/wrong/no_match），两者不一致。这个标注工作流在 curify-studio 侧是否完整？

2. **Redis 可用性**：Gallery prompts 依赖 Redis（`services/nanoPrompts.ts`），本地开发环境是否有 Redis 实例？`eval_search.cjs` 不测试 Redis 路径。

3. **`OPENAI_API_KEY` 的 Vercel 配置**：`lib/searchRewrite.ts` 和 `lib/searchTemplateMatch.ts` 均依赖此密钥。本地 `.env.local` 存在（已通过 `ls -la` 确认），但密钥值未查看（遵守只读约束）。生产环境 key 是否有效且未超额？

4. **intent taxonomy 新配置文件的业务优先级**：boss 要求的 8 个高级意图簇（Learning Materials / Visual & Art / Merch & Commerce 等）与当前 19 个 output-type slugs 的映射关系尚未确定。其中：
   - `Learning Materials` 对应的 slug 集合需要业务确认（现有 `learning` tier-1 但其 tier-2 子项与 output-type slugs 无直接映射）
   - `Events & Hot Now` 对应什么 output-type slug？现有分类中无直接对应
   - `Social & Personal` 中 selfies 和 social-media-posts 是否充分代表该簇？

5. **`template-cultural-relic` 和 `template-dog-breed` 的状态**：这两个 template_id 出现在灵感数据中但不在 `nano_templates.json`，属于遗留记录还是未发布模板？应该清理还是补充？

6. **灵感 topics 38.5% 无覆盖（1182 条灵感无 topics 字段）**：`scripts/enrich_example_topics.py` 已存在，是否计划对无 topics 灵感进行批量补充？在 topic co-occurrence 实现前需要明确这部分缺失数据的处理策略。

7. **`scripts/configs/taic_section_a_candidates.json`（`public/data/taic_section_a_candidates.json`）的用途**：文件存在但本次审计未深入检查其与 Admin Portal 的关联关系，以及其在 TAIC/VIRB benchmark 中的角色。

---

*本审计报告基于 commit `151c8759`（branch `jwang/vercel`，2026-06-18），所有结论均有代码证据支持，假设已明确标注。*
