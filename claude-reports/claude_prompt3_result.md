# Curify Prompt 3 实现报告 — 8 高层 Intent Cluster 映射与搜索意图 Pills

**日期：** 2026-06-18  
**分支：** `baobao/multi-intent-topic-cooccurrence`  
**最后提交：** `ca338b48 feat(search): add topic co-occurrence intent evidence`

---

## 1. 实现结果概览

本次 Prompt 3 在 Prompt 2（Topic Co-occurrence 基础设施）之上，新增了从 Top-20 搜索结果 topic 证据到 8 个高层创作意图集群（Cluster）的映射，并在搜索 UI 中以 Chip Pills 形式呈现。

主要成果：

| 项目 | 状态 |
|---|---|
| `lib/intent_taxonomy.ts` 新建 | ✅ 327 行 |
| `lib/intent_clusters.ts` 更新 | ✅ 260 行 |
| `app/[locale]/(public)/search/page.tsx` 更新 | ✅ |
| `app/[locale]/(public)/search/SearchResultsClient.tsx` 更新 | ✅ |
| `lib/__tests__/intent_clusters.test.ts` 更新 | ✅ 583 行，44 tests |
| 全部 74 unit tests 通过 | ✅ |
| `npx tsc --noEmit` 零错误 | ✅ |
| 受保护文件（JSON datasets、taxonomy.json、lockfiles）零变动 | ✅ |
| 无 runtime LLM 调用 | ✅ |
| 无 Business Override | ✅ |

---

## 2. 八个 Intent Cluster 配置

### 2.1 完整配置表

| Slug | English Label | 中文标签 | 映射 topic 数 |
|---|---|---|---|
| `learning-materials` | Learning Materials | 学习材料 | 35 个 |
| `visual-art` | Visual & Art | 视觉与艺术 | 25 个 |
| `merch-commerce` | Merch & Commerce | 商品与商业 | 9 个 |
| `social-personal` | Social & Personal | 社交与个人 | 24 个 |
| `storytelling-identity` | Storytelling & Identity | 故事与身份 | 43 个 |
| `travel-place` | Travel & Place | 旅行与地点 | 12 个 |
| `events-hot-now` | Events & Hot Now | 活动与热点 | 25 个 |
| `diy-guides` | DIY & Guides | DIY 与指南 | 9 个 |

### 2.2 详细映射与数据来源证明

#### learning-materials（学习材料）

```
learning         — nano_templates.json ✓ | taxonomy.json tier1 ✓
vocabulary       — nano_templates.json ✓
kids-vocabulary  — nano_inspiration.json ✓
language         — nano_templates.json ✓ | taxonomy.json tier1 ✓
language-english — nano_templates.json ✓
dialogue         — nano_templates.json ✓ | nano_inspiration.json ✓
expressions      — nano_templates.json ✓ | nano_inspiration.json ✓
asl              — nano_templates.json ✓
phonics          — nano_inspiration.json ✓
english-chinese  — nano_inspiration.json ✓
english-spanish  — nano_inspiration.json ✓
english-korean   — nano_inspiration.json ✓
english-japanese — nano_inspiration.json ✓
english-french   — nano_inspiration.json ✓
beginner         — nano_templates.json ✓
intermediate     — nano_templates.json ✓
advanced         — nano_templates.json ✓
infographic      — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
information-card — nano_templates.json ✓
flashcards       — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
mind-maps        — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
study-sheets     — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
comparison       — nano_templates.json ✓ | nano_inspiration.json ✓
matching-chart   — nano_inspiration.json ✓
science          — nano_templates.json ✓ | nano_inspiration.json ✓
evolution        — nano_templates.json ✓ | nano_inspiration.json ✓
anatomy          — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
history          — nano_templates.json ✓ | nano_inspiration.json ✓
reading          — nano_templates.json ✓ | nano_inspiration.json ✓
insight          — nano_templates.json ✓ | nano_inspiration.json ✓
fact             — nano_inspiration.json ✓
school           — nano_inspiration.json ✓
timeline         — nano_templates.json ✓ | nano_inspiration.json ✓
step-by-step-tutorial — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS, 与 diy-guides 合理重叠)
```

#### visual-art（视觉与艺术）

```
design           — nano_templates.json ✓
posters          — nano_templates.json ✓ | nano_inspiration.json ✓
digital-canvas   — nano_templates.json ✓ | nano_inspiration.json ✓
art              — nano_templates.json ✓
illustration     — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
watercolor       — nano_templates.json ✓ | nano_inspiration.json ✓
ink              — nano_templates.json ✓
cartoon          — nano_templates.json ✓ | nano_inspiration.json ✓
kawaii           — nano_templates.json ✓ | nano_inspiration.json ✓
vintage          — nano_inspiration.json ✓
vintage-retro    — nano_inspiration.json ✓
retro            — nano_templates.json ✓
pastel           — nano_inspiration.json ✓
y2k              — nano_inspiration.json ✓
abstract         — nano_templates.json ✓
monochrome       — nano_templates.json ✓ | nano_inspiration.json ✓
isometric        — nano_templates.json ✓
composition      — nano_templates.json ✓ | nano_inspiration.json ✓
photorealistic   — nano_templates.json ✓ (与 social-personal 合理重叠)
artistic         — nano_inspiration.json ✓
wall-art         — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
art-prints       — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
fan-art          — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS, 与 storytelling 合理重叠)
event-poster     — nano_inspiration.json ✓（4 inspirations）
promotional-poster — nano_inspiration.json ✓（2 inspirations）
```

#### merch-commerce（商品与商业）

```
product          — nano_templates.json ✓ | nano_inspiration.json ✓
merch            — nano_templates.json ✓
ecommerce        — nano_templates.json ✓
mockups          — nano_templates.json ✓ | nano_inspiration.json ✓
packaging        — nano_templates.json ✓
showcase         — nano_templates.json ✓
stickers         — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
mascots          — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS, 与 storytelling 合理重叠)
character-ip     — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS, 与 storytelling 合理重叠)
```

#### social-personal（社交与个人）

```
lifestyle        — nano_templates.json ✓
fashion          — nano_templates.json ✓ | nano_inspiration.json ✓
high-fashion     — nano_templates.json ✓ | nano_inspiration.json ✓
portrait         — nano_templates.json ✓ | nano_inspiration.json ✓
photorealistic   — nano_templates.json ✓（与 visual-art 合理重叠）
chic             — nano_inspiration.json ✓
memes            — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
social-media-posts — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
selfies          — OUTPUT_TYPE_SLUGS ✓
beauty           — nano_templates.json ✓ | nano_inspiration.json ✓
fitness          — nano_templates.json ✓（与 diy-guides 合理重叠）
wellness         — nano_templates.json ✓（与 diy-guides 合理重叠）
lookbook         — nano_templates.json ✓
outfit           — nano_templates.json ✓
profile          — nano_templates.json ✓
groups           — nano_templates.json ✓ | nano_inspiration.json ✓
athleisure       — nano_inspiration.json ✓
denim            — nano_inspiration.json ✓
sneakers         — nano_inspiration.json ✓
soft-girl        — nano_inspiration.json ✓
casual           — nano_inspiration.json ✓
elegant          — nano_inspiration.json ✓
stylish          — nano_inspiration.json ✓
mood             — nano_templates.json ✓ | nano_inspiration.json ✓（情绪/氛围）
natural-beauty   — nano_inspiration.json ✓
```

#### storytelling-identity（故事与身份）

```
character        — nano_templates.json ✓ | taxonomy.json tier1 ✓
personality      — nano_templates.json ✓
mbti             — nano_templates.json ✓ | nano_inspiration.json ✓
film             — nano_templates.json ✓ | nano_inspiration.json ✓
anime            — nano_templates.json ✓ | nano_inspiration.json ✓
comic            — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
fan-art          — nano_templates.json ✓（与 visual-art 合理重叠）
character-ip     — nano_templates.json ✓（与 merch-commerce 合理重叠）
mascots          — nano_templates.json ✓（与 merch-commerce 合理重叠）
quiz             — nano_templates.json ✓
story            — nano_templates.json ✓
scrapbooks       — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
relationship     — nano_templates.json ✓ | nano_inspiration.json ✓
nostalgia        — nano_templates.json ✓ | nano_inspiration.json ✓
gaming           — nano_templates.json ✓
quote            — nano_templates.json ✓
disney           — nano_templates.json ✓ | nano_inspiration.json ✓
marvel           — nano_inspiration.json ✓
naruto           — nano_inspiration.json ✓
ghibli           — nano_inspiration.json ✓
harry-potter     — nano_inspiration.json ✓
friends          — nano_inspiration.json ✓
silicon-valley   — nano_inspiration.json ✓
yellowstone      — nano_inspiration.json ✓
genshin          — nano_inspiration.json ✓
journey-to-the-west — nano_inspiration.json ✓
breaking-bad     — nano_inspiration.json ✓
mbti-infj/infp/intj/intp/enfj/enfp/entj/entp
mbti-isfj/isfp/istj/istp/esfj/esfp/estj/estp — nano_inspiration.json ✓（全 16 型）
```

#### travel-place（旅行与地点）

```
travel           — nano_templates.json ✓ | taxonomy.json tier1 ✓
city             — nano_templates.json ✓ | nano_inspiration.json ✓
itinerary        — nano_templates.json ✓ | nano_inspiration.json ✓
map              — nano_templates.json ✓
seasonal         — nano_templates.json ✓
architecture     — nano_templates.json ✓ | nano_inspiration.json ✓
food             — nano_templates.json ✓（与 diy-guides 合理重叠）
food-and-drink   — nano_inspiration.json ✓
culture          — nano_templates.json ✓ | taxonomy.json tier1 ✓
cultural-festivals — nano_templates.json ✓ | nano_inspiration.json ✓
weather          — nano_templates.json ✓ | nano_inspiration.json ✓
costumes         — nano_templates.json ✓
```

#### events-hot-now（活动与热点）

```
world-cup        — nano_templates.json ✓ | nano_inspiration.json ✓（95 inspirations）
sports           — nano_templates.json ✓ | nano_inspiration.json ✓（96 inspirations）
soccer           — nano_templates.json ✓ | nano_inspiration.json ✓（9 inspirations）
trending         — nano_templates.json ✓ | nano_inspiration.json ✓（4 inspirations）
schedule         — nano_templates.json ✓
olympics         — nano_inspiration.json ✓
tournament-bracket — nano_inspiration.json ✓
fifa             — nano_inspiration.json ✓
conmebol         — nano_inspiration.json ✓
uefa             — nano_inspiration.json ✓
nba              — nano_inspiration.json ✓
nfl              — nano_inspiration.json ✓
nhl              — nano_inspiration.json ✓
hockey           — nano_inspiration.json ✓
tennis           — nano_inspiration.json ✓
volleyball       — nano_inspiration.json ✓
basketball       — nano_inspiration.json ✓
baseball         — nano_inspiration.json ✓
badminton        — nano_inspiration.json ✓
swimming         — nano_inspiration.json ✓
athletics        — nano_inspiration.json ✓
winter-sports    — nano_inspiration.json ✓
women-sports     — nano_inspiration.json ✓
celebration      — nano_templates.json ✓ | nano_inspiration.json ✓
festival         — nano_inspiration.json ✓
```

#### diy-guides（DIY 与指南）

```
step-by-step-tutorial — nano_templates.json ✓（与 learning-materials 合理重叠）
recipes          — nano_templates.json ✓ (OUTPUT_TYPE_SLUGS)
guides           — nano_templates.json ✓
before-after     — nano_inspiration.json ✓（2 inspirations）
wellness         — nano_templates.json ✓（与 social-personal 合理重叠）
fitness          — nano_templates.json ✓（与 social-personal 合理重叠）
finance          — nano_templates.json ✓
food             — nano_templates.json ✓（与 travel-place 合理重叠）
process          — nano_templates.json ✓
```

### 2.3 重叠设计说明

跨 cluster 的 topic 重叠是刻意允许的（requirements 第 4 条）：

| Topic | 重叠的 Cluster |
|---|---|
| `step-by-step-tutorial` | learning-materials, diy-guides |
| `photorealistic` | visual-art, social-personal |
| `fan-art` | visual-art, storytelling-identity |
| `character-ip` | merch-commerce, storytelling-identity |
| `mascots` | merch-commerce, storytelling-identity |
| `food` | travel-place, diy-guides |
| `fitness` / `wellness` | social-personal, diy-guides |

同一 cluster 内部不允许重复（T4 测试已验证）。

---

## 3. Cluster Ranking 逻辑

### 3.1 `rankIntentClusters(cooccurrence, options)` 实现

**函数签名：**
```typescript
rankIntentClusters(
  cooccurrence: TopicCooccurrenceResult,
  options?: { topN?: number; minCount?: number; locale?: string }
): ClusterChip[]
```

**完整 Ranking 流程：**

1. **仅使用 mergedTopicCounts**：从 `TopicCooccurrenceResult.mergedTopicCounts` 中建立 `topic → resultIds[]` 的快速查找 Map。

2. **对每个 Cluster 求 resultId 集合联集**：
   ```
   对每个 cluster.topicSlugs 中的 topicSlug：
     取 mergedTopicCounts 中该 slug 的 resultIds
     全部加入 Set<string> (unionIds)
   ```
   使用 `Set` 自动去重。

3. **一个 result 对同一 cluster 最多贡献 +1**：  
   即使某 result 同时携带 `learning`、`science`、`infographic`、`anatomy` 四个 topic，全部映射到 `learning-materials`，其 resultId 只被加入 unionIds 一次。最终 `cluster.count = unionIds.size = 1`，而非 4。

4. **同一 result 可对不同 cluster 各贡献 +1**：  
   若某 result 的 mergedTopics 为 `["science", "posters", "world-cup"]`，则：
   - `science` → `learning-materials` (+1)
   - `posters` → `visual-art` (+1)
   - `world-cup` → `events-hot-now` (+1)
   三个不同 cluster 各得 +1，这是允许的。

5. **过滤**：`unionIds.size < minCount` 的 cluster 被丢弃。

6. **排序**：count 降序，count 相同时按 slug 升序（字典序），确保输出完全确定性。

7. **截断**：取前 `topN` 个（默认 5）。

8. **无 Business Override**：无任何人工加权，完全由证据驱动。

9. **无 LLM 调用**：纯 TypeScript 计算。

### 3.2 判别联合类型设计

新增两种 chip 类型，以显式的 `kind` 字段区分：

```typescript
type TopicChip   = { kind: "topic";   slug: string; count: number };
type ClusterChip = { kind: "cluster"; slug: string; label: string; count: number };
type IntentChip  = TopicChip | ClusterChip;
```

- `topIntentChips` / `topIntentChipsFromTopicCounts` 返回 `TopicChip[]`（kind="topic"）
- `rankIntentClusters` 返回 `ClusterChip[]`（kind="cluster"，含预本地化 `label`）
- UI 对 `kind` 做 discriminated-union dispatch

---

## 4. 搜索过滤逻辑

### 4.1 新增 `intent` URL 参数

```
/search?q=science+poster&intent=learning-materials
/search?q=cats&intent=visual-art
```

### 4.2 验证

在 `page.tsx` 服务端：
```typescript
const rawIntent = intent.trim().toLowerCase();
const intentSlug = isIntentClusterSlug(rawIntent) ? rawIntent : "";
```

`isIntentClusterSlug` 检查 `CLUSTER_BY_SLUG` Map，未知值返回 `false`，`intentSlug` 保持为空字符串，安全 no-op。

### 4.3 Inspiration 过滤

```typescript
if (intentSlug) {
  const clusterTopicSet = getIntentClusterTopicSet(intentSlug);
  inspirations = inspirations.filter((r) => {
    const { mergedTopics } = resolveTopics(r, TEMPLATE_TOPICS);
    return mergedTopics.some((t) => clusterTopicSet.has(t));
  });
}
```

- 使用 `resolveTopics` 计算 inspiration + 父模板 topics 的并集（mergedTopics）
- 与 cluster 的 topicSlugs Set 求交集
- 保留原始排名顺序（filter 不重排序）

### 4.4 Template Rail 过滤

```typescript
.filter((c) => {
  if (!intentSlug) return true;
  const clusterTopicSet = getIntentClusterTopicSet(intentSlug);
  const directMatch = (c.topics ?? []).some((s) => clusterTopicSet.has(s));
  return directMatch || survivingInspTemplateIds.has(c.template_id);
})
```

规则：
- **A. 直接匹配**：template 自身 topics 与 cluster topic set 有交集
- **B. 关联匹配**：该 template 的 ID 出现在存活 inspiration 的 template_id 中

### 4.5 优先级：intent vs within

- `intent` 优先级 > `within`
- 若两者同时存在：`effectiveWithin = intentSlug ? "" : withinSlug`
- within 只在无 intent 时生效
- 单向隔离：避免双重过滤

### 4.6 Chip 链接规则

| 操作 | 链接格式 |
|---|---|
| 点击 cluster chip | `?q=...&intent=<cluster-slug>` |
| 点击 topic chip | `?q=...&within=<topic-slug>` |
| 移除 intent pill | `?q=...`（无 intent、无 within） |
| 移除 within pill | `?q=...`（无 within、无 intent） |

---

## 5. UI 行为变化

### 5.1 旧行为（Prompt 2）

- 仅有 raw output-type topic chips（`kind="topic"`）
- chips 链接到 `?within=<slug>`
- active pill 为紫色，显示 "Narrowed to: \<topic-label\> ×"

### 5.2 新行为（Prompt 3）

**Explore further 行（无 active filter 时）：**

| 场景 | 显示内容 |
|---|---|
| 至少 1 个 cluster 通过 minCount | 显示 cluster chips（蓝紫 indigo 配色，含 `count`） |
| 所有 cluster 未过 minCount | 回退到 topic chips（紫色配色，原有行为） |
| 任何 active filter 存在 | 整行隐藏 |

**Active filter pills：**

| 场景 | 显示内容 |
|---|---|
| `?intent=<slug>` 有效 | 蓝紫 pill："Narrowed to: Learning Materials ×" |
| `?within=<slug>` 有效（无 intent） | 紫色 pill（原有行为不变） |
| 两者均存在 | 仅显示 intent pill（intent 优先级更高） |

**Cluster chip 样式差异：**
- Cluster chip：`border-indigo-200 bg-indigo-50 text-indigo-900`（有别于 topic chip 的 purple）
- Active intent pill：`bg-indigo-600 text-white`

### 5.3 Fallback 明确区分

```typescript
const clusterChips = rankIntentClusters(cooccurrence, { topN: 5, minCount: 2, locale });
if (clusterChips.length > 0) {
  intentChips = clusterChips;   // kind: "cluster"
} else {
  intentChips = topIntentChipsFromTopicCounts(cooccurrence, { topN: 5, minCount: 2 });
  // kind: "topic"
}
```

客户端通过 `chip.kind` discriminated union dispatch，无歧义。

---

## 6. 修改文件列表

| 文件路径 | 状态 | 职责 |
|---|---|---|
| `lib/intent_taxonomy.ts` | **新建** | 8 个 Cluster 的配置记录、helper 函数（getIntentCluster、isIntentClusterSlug、getIntentClusterLabel、getIntentClusterTopicSet） |
| `lib/intent_clusters.ts` | **修改** | 新增 TopicChip/ClusterChip/IntentChip 判别联合类型；更新 topIntentChips/topIntentChipsFromTopicCounts 返回类型；新增 rankIntentClusters、filterInspirationsByCluster、filterTemplatesByCluster |
| `app/[locale]/(public)/search/page.tsx` | **修改** | 解析并验证 `intent` URL param；intent-based filtering for inspirations + templates；cluster chip fallback 逻辑；向 SearchResultsClient 传递 intentSlug/activeIntentLabel |
| `app/[locale]/(public)/search/SearchResultsClient.tsx` | **修改** | 新增 intentSlug/activeIntentLabel Props；新增 cluster active pill；更新 chip row 为 kind-dispatch 渲染；tracking 新增 intentSuffix |
| `lib/__tests__/intent_clusters.test.ts` | **修改** | 44 unit tests 覆盖全部 21 项验收指标（含原有 topic chip 测试） |

---

## 7. 测试结果

### 运行命令

```bash
npx vitest run --config vitest.unit.config.ts
```

### 结果

```
 RUN  v3.2.4

 ✓ lib/__tests__/topic_resolver.test.ts   (20 tests)
 ✓ lib/__tests__/topic_cooccurrence.test.ts (10 tests)
 ✓ lib/__tests__/intent_clusters.test.ts  (44 tests)

 Test Files  3 passed (3)
      Tests  74 passed (74)
   Duration  501ms
```

### 测试覆盖点对应（需求 → 测试）

| 需求编号 | 测试名称 | 所在 describe |
|---|---|---|
| T1 | "has exactly eight intent clusters" | intent taxonomy |
| T2 | "all eight cluster slugs are unique" | intent taxonomy |
| T3 | "every cluster has non-empty English and Chinese labels" | intent taxonomy |
| T4 | "no duplicate topic slugs within any cluster" | intent taxonomy |
| T5 | "all topic slugs are normalized lowercase non-empty strings" | intent taxonomy |
| T6 | "unknown cluster slug returns undefined" + "returns empty set" | intent taxonomy |
| T7 | "returns English label as fallback" + "returns Chinese label for zh" | intent taxonomy |
| T8 | "multiple topics from one result count as +1 to a single cluster" | rankIntentClusters |
| T9 | "a result may contribute +1 to two different clusters" | rankIntentClusters |
| T10 | "ranking aggregates result IDs across all merged topics in a cluster" | rankIntentClusters |
| T11 | "respects minCount" | rankIntentClusters |
| T12 | "respects topN" | rankIntentClusters |
| T13 | "ties are broken by cluster slug ascending" | rankIntentClusters |
| T14 | "clusters with no matching evidence are not emitted" | rankIntentClusters |
| T15 | "counts reflect only evidence — no boost for any cluster" | rankIntentClusters |
| T16 | "filters inspirations whose mergedTopics intersect the cluster topic set" | filterInspirationsByCluster |
| T17 | "passes all inspirations through for an unknown cluster slug" | filterInspirationsByCluster |
| T18 | "preserves ranking order among surviving results" | filterInspirationsByCluster |
| T19a | "includes templates whose own topics intersect the cluster topic set" | filterTemplatesByCluster |
| T19b | "includes templates represented by surviving inspiration results" | filterTemplatesByCluster |
| T20 | "topIntentChipsFromTopicCounts returns topic chips independently" | raw topic fallback chips |
| T21 | 既有 topic_resolver/cooccurrence/intent_chips 20+ 测试全部仍然通过 | 多个 describe |

### TypeScript 检查

```bash
npx tsc --noEmit
# 输出：（无输出 = 零错误）
```

---

## 8. 手动验收步骤

启动开发服务器后访问以下 URL（端口 3001）：

### 8.1 无 filter — 应显示 cluster chips

**cats 搜索（预期：events-hot-now 或 storytelling/social 等 cluster 排首位）**
```
http://localhost:3001/en/search?q=cats
```
期望：Explore further 区域显示蓝紫 indigo chip pills（kind="cluster"），含 label 和 count。

**science poster（预期：learning-materials 和/或 visual-art cluster）**
```
http://localhost:3001/en/search?q=science+poster
```
期望：cluster chips 中应出现 "Learning Materials" 和 "Visual & Art"。

**dinosaur poster（预期：learning-materials/visual-art/events-hot-now）**
```
http://localhost:3001/en/search?q=dinosaur+poster
```

### 8.2 Active cluster filter — 应显示 active pill

**science poster + intent=learning-materials**
```
http://localhost:3001/en/search?q=science+poster&intent=learning-materials
```
期望：
- 显示蓝紫 pill："Narrowed to: Learning Materials ×"
- 无 chip row（已在 narrow 状态）
- 只显示含 learning/science 等主题的 inspirations
- 点击 × 返回 `?q=science+poster`

**science poster + intent=visual-art**
```
http://localhost:3001/en/search?q=science+poster&intent=visual-art
```
期望：
- 显示 pill："Narrowed to: Visual & Art ×"
- 只显示含 design/posters/illustration 等主题的 inspirations

### 8.3 Active within filter — 原有行为不变

```
http://localhost:3001/en/search?q=science+poster&within=infographic
```
期望：
- 显示紫色 pill："Narrowed to: infographic ×"（原有样式不变）
- 无 chip row
- 点击 × 返回 `?q=science+poster`

### 8.4 Both filters — intent 优先级验证

```
http://localhost:3001/en/search?q=science&intent=visual-art&within=infographic
```
期望：
- 仅显示 intent pill（"Visual & Art"），within 被 suppress
- 过滤结果基于 visual-art cluster topics，而非 infographic alone

### 8.5 Invalid intent — 安全忽略

```
http://localhost:3001/en/search?q=science&intent=not-a-cluster
```
期望：
- 无 active pill
- 显示正常 chip row（`not-a-cluster` 被忽略）
- 结果与 `?q=science` 完全相同

### 8.6 Fallback topic chips — 无 cluster 过阈值时

（可选：极短或极窄 query，Top-20 结果中各 topic 均不足 2 次）
```
http://localhost:3001/en/search?q=yellowstone
```
若 cluster 均未过 minCount，应显示原有紫色 topic chips（如 `fan-art`, `comic` 等 OUTPUT_TYPE_SLUGS）。

---

## 9. Git Diff 摘要

```
git diff --stat
 SearchResultsClient.tsx  | 133 ++++---
 page.tsx                 | 112 ++++--
 intent_clusters.test.ts  | 399 +++++++++++++++++++++
 intent_clusters.ts       | 149 +++++++-
 4 files changed, 708 insertions(+), 85 deletions(-)

?? lib/intent_taxonomy.ts   ← 新建，不在 Git tracking 中（未提交）
```

### 受保护文件验证

```bash
git diff -- lib/taxonomy.json public/data/nano_templates.json \
            public/data/nano_inspiration.json \
            package.json package-lock.json vitest.config.ts
# 输出：（无输出 = 零变动）
```

| 文件 | 变动 |
|---|---|
| `lib/taxonomy.json` | 无 |
| `public/data/nano_templates.json` | 无 |
| `public/data/nano_inspiration.json` | 无 |
| `package.json` | 无 |
| `package-lock.json` | 无 |
| `vitest.config.ts` | 无 |
| `vitest.unit.config.ts` | 无 |
| 任何 `.env` 文件 | 无 |

### 安全审计

- ✅ 无 API key 或 env 变量暴露
- ✅ 无 runtime LLM 调用新增
- ✅ 无 Business Override 逻辑
- ✅ Ranking 完全由证据驱动
- ✅ 每个 result 对同一 cluster 最多贡献 +1
- ✅ 原有 within 行为完全兼容

---

## 10. 下一步建议

### 建议下一阶段：Business Override 配置实现

当前 `rankIntentClusters` 纯粹基于 topic co-occurrence 证据排序，任何 cluster 的显示优先级完全由搜索结果决定。

**下一阶段目标**：为 Learning/EdTech 和 Merch/Commerce 实现可配置的 Business Override——在特定条件下（如查询词语义属于教育/商品领域时），允许运营团队通过配置文件（非代码修改）对这两个 cluster 施加优先级提升。

**建议技术路径**：

1. 在 `lib/intent_taxonomy.ts` 或单独的 `lib/intent_business_override.ts` 中定义 `BusinessOverrideConfig` 类型：
   ```typescript
   type BusinessOverrideConfig = {
     clusterSlug: IntentClusterSlug;
     boostWhenQueryMatchesSlugs?: string[];  // topic slugs
     boostWhenCountAbove?: number;            // evidence threshold
     minRankPosition?: number;                // force into top N
   };
   ```

2. `rankIntentClusters` 接受可选的 `overrides?: BusinessOverrideConfig[]` 参数，仅在参数存在时应用。默认行为（无 override）完全不变。

3. Override 逻辑完全确定性、可测试、无 LLM：
   - 先运行证据排序（当前逻辑）
   - 再按配置调整优先级
   - 测试：override 数组为空时结果与当前完全相同

4. Business Override 测试：
   - 有 override 时 learning-materials 提升到指定位置
   - 无 override 时行为不变（T15 依然成立）

---

## 附录：文件行数统计

| 文件 | 行数 |
|---|---|
| `lib/intent_taxonomy.ts`（新建） | 327 行 |
| `lib/intent_clusters.ts`（修改） | 260 行 |
| `lib/__tests__/intent_clusters.test.ts`（修改） | 583 行 |

**本报告行数（保存至 `/Users/baobaoli/Desktop/claude_prompt3_result.md`）：** 约 430 行
