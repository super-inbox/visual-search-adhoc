# Curify Multi-Intent Topic Co-occurrence 实现报告

**分支：** `baobao/multi-intent-topic-cooccurrence`  
**日期：** 2026-06-18  
**作者：** Claude Sonnet 4.6

---

## 1. 实现结果概览

本次实现完成了 Curify Multi-Intent 系统的数据基础层，具体包括：

- **Part A**：创建纯函数模块 `lib/topic_resolver.ts`，负责从 inspiration 记录和其父模板中解析、标准化和合并 topic 列表。
- **Part B**：创建纯函数模块 `lib/topic_cooccurrence.ts`，计算 Top 20 排名结果的 topic 共现频率，并追踪每个 slug 的来源结果 ID，支持同义词折叠后的精确去重。
- **Part C**：重构 `app/[locale]/(public)/search/page.tsx`，使用 `buildTemplateTopicsMap` + `resolveTopics` 替代手动构建的 `TEMPLATE_TOPICS` 和内联展开逻辑，并在排名后计算 topic 共现。
- **Part D**：在 `lib/intent_clusters.ts` 中新增 `topIntentChipsFromTopicCounts`，基于 Top 20 结果的 topic 共现证据（而非仅 matched template）生成 intent chip，同义词折叠通过 result-ID Set 并集保证精确的每结果一票语义。
- **Part E**：创建 `vitest.unit.config.ts` 及三个测试文件，共 42 条测试，全部通过。
- **Part F**：`npx vitest run --config vitest.unit.config.ts` 42/42 通过；`npx tsc --noEmit` 零错误；`git diff --check` 无空白问题。

工作树干净：未修改任何 JSON 数据集、lockfile、环境文件或 `vitest.config.ts`。

---

## 2. 修改文件列表

### 新增文件

#### `lib/topic_resolver.ts`
- **状态**：新建
- **职责**：纯函数 topic 解析器；接受 record/map 作为参数，不直接导入大型 JSON 数据集，可被单独单元测试，也不会将 JSON 打包进客户端 bundle。
- **重要函数**：
  - `normalizeTopicList(input: unknown): string[]` — 清洗、去重、标准化为小写 slug 数组
  - `buildTemplateTopicsMap(templates: TemplateTopicRecord[]): Map<string, string[]>` — 构建 template id → normalized topics 映射
  - `resolveTopics(inspiration, templateMap): ResolvedTopics` — 返回 `{ inspirationTopics, templateTopics, mergedTopics }`
- **导出类型**：`TemplateTopicRecord`, `InspirationTopicRecord`, `ResolvedTopics`

#### `lib/topic_cooccurrence.ts`
- **状态**：新建
- **职责**：纯函数共现计算器；分析前 N 条排名结果，输出三个维度（inspiration-only、template-only、merged）的 topic 频率计数，每个 `TopicCount` 附带 `resultIds: string[]`，供下游同义词折叠时做 Set 并集去重。
- **重要函数**：
  - `calculateTopicCooccurrence(rankedInspirations, templateMap, limit?): TopicCooccurrenceResult`
- **导出类型**：`TopicCount`, `TopicCooccurrenceResult`

#### `vitest.unit.config.ts`
- **状态**：新建
- **职责**：独立的 Vitest 配置文件，用于运行 `lib/__tests__/**/*.test.ts` 中的纯 Node 单元测试；不修改原有 `vitest.config.ts`（该文件依赖不存在的 `.storybook/` 目录，当前已处于无法运行状态）。

#### `lib/__tests__/topic_resolver.test.ts`
- **状态**：新建
- **职责**：`normalizeTopicList`、`buildTemplateTopicsMap`、`resolveTopics` 的单元测试，共 20 条。

#### `lib/__tests__/topic_cooccurrence.test.ts`
- **状态**：新建
- **职责**：`calculateTopicCooccurrence` 的单元测试，覆盖 limit 行为、source-specific 计数、merged 去重、resultIds 追踪、确定性排序，共 10 条。

#### `lib/__tests__/intent_clusters.test.ts`
- **状态**：新建
- **职责**：`topIntentChips`（向后兼容验证）和 `topIntentChipsFromTopicCounts`（新逻辑）的单元测试，共 12 条；包含同义词折叠去重的精确验证。

### 修改文件

#### `lib/intent_clusters.ts`
- **状态**：修改
- **职责**：新增 `topIntentChipsFromTopicCounts`；保留原 `topIntentChips` 不变（向后兼容）。
- **重要变更**：
  - 顶部新增 `import type { TopicCooccurrenceResult } from "./topic_cooccurrence"`
  - 新增函数：遍历 `mergedTopicCounts`，过滤 `OUTPUT_TYPE_SET`，应用 `SYNONYM_FOLDS`，将 source/target slug 的 `resultIds` 并集后取 `.size` 作为计数

#### `app/[locale]/(public)/search/page.tsx`
- **状态**：修改
- **职责**：使用新模块替代手动 TEMPLATE_TOPICS 构建和内联 topic 展开；在排名结果确定后计算共现，更新 intent chip 生成逻辑。
- **重要变更**（四处）：
  1. imports：替换 `topIntentChips` → `topIntentChipsFromTopicCounts`；新增 `buildTemplateTopicsMap`, `resolveTopics`, `calculateTopicCooccurrence`
  2. `TEMPLATE_TOPICS`：从手动 for 循环改为 `buildTemplateTopicsMap(nanoTemplates as any[])`（一行）
  3. blob 构建（主 blob 和 topical blob 各一处）：`...(r.topics ?? []), ...(TEMPLATE_TOPICS.get(r.template_id) ?? [])` → `const { mergedTopics } = resolveTopics(r, TEMPLATE_TOPICS); ...mergedTopics`
  4. `intentChips`：`topIntentChips(matchedTemplates, ...)` → `topIntentChipsFromTopicCounts(calculateTopicCooccurrence(inspirations, TEMPLATE_TOPICS, 20), { topN: 5, minCount: 2 })`

---

## 3. Topic Resolver 逻辑

### `inspirationTopics`
来源：inspiration 记录自身的 `topics` 字段（不包括 `tags`、`search_aliases`）。经过 `normalizeTopicList` 处理：只保留字符串、trim、toLowerCase、去重、丢弃空串。

### `templateTopics`
来源：通过 `inspiration.template_id` 查找父模板的 topics（从 `buildTemplateTopicsMap` 返回的 Map 中查找）。Map 在构建时已对每条模板的 topics 做一次 `normalizeTopicList` 标准化。

### `mergedTopics`
`inspirationTopics` 和 `templateTopics` 的并集（Set 去重）。某个 slug 在两个来源中都出现时，在 `mergedTopics` 中只出现一次。

### 去重保证
- `normalizeTopicList`：单次遍历，用 `Set<string>` 跟踪已见 slug，保证单源内去重，保留首次出现顺序。
- `resolveTopics`：用 `Set<string>(inspirationTopics)` 初始化后追加 `templateTopics`，天然实现跨源去重。

### 缺失数据处理
- `inspiration.topics` 为 undefined/null/非数组：`normalizeTopicList` 返回 `[]`，不抛出。
- `inspiration.template_id` 缺失或非字符串：`templateId = ""`，`templateTopics = []`，不抛出。
- `template_id` 在 Map 中不存在：`templateMap.get(templateId) ?? []`，不抛出。
- inspiration 记录完全没有 topics 字段：安全返回 `{ inspirationTopics: [], templateTopics: [...], mergedTopics: [...] }`。

---

## 4. Topic Co-occurrence 逻辑

### Top 20 限制
`calculateTopicCooccurrence` 第一步执行 `rankedInspirations.slice(0, limit)`（默认 `limit = 20`）。只有这个切片中的结果参与计数；`analyzedResultCount` 记录实际分析的条数（当结果少于 20 条时等于实际数量）。

### Source-specific 计数
对于切片中的每条结果：
1. 调用 `resolveTopics(inspiration, templateMap)` 得到三个数组
2. **inspiration 计数**：遍历 `inspirationTopics`，用 per-result `seenInsp` Set 保证每个 slug 至多 +1；更新 `inspirationCounts` 和 `inspirationIds`
3. **template 计数**：遍历 `templateTopics`，同理，更新 `templateCounts` 和 `templateIds`
4. **merged 计数**：遍历 `mergedTopics`（已是两源的去重并集），用 per-result `seenMerged` Set 保证每个 slug 至多 +1；更新 `mergedCounts` 和 `mergedIds`

三路计数独立维护，互不干扰。一个同时出现在 inspiration 和 template 中的 slug，在 `inspirationCounts` +1、在 `templateCounts` +1、在 `mergedCounts` 只 +1（不是 +2）。

### `resultIds` 追踪
每个 `TopicCount` 包含 `resultIds: string[]`，记录哪些结果 ID 贡献了该 slug。这一设计是同义词折叠正确去重的关键（见第 5 节）。

### 确定性排序
`sortCounts` 实现：
```
降序 count → 相同 count 时按 slug 升序（localeCompare）
```
同等条件下排序稳定且与输入顺序无关，每次运行结果一致。

---

## 5. Intent Chips 数据来源变化

### Before（旧行为）
```
topIntentChips(matchedTemplates, { topN: 5, minCount: 2 })
```
- 数据来源：与查询匹配的**模板集合**的 `topics` 字段
- 每个模板贡献其 output-type topics，per-template 去重（同一模板的 `art-prints` + `wall-art` 只计 +1）
- 不包含 inspiration 自身的 topics
- 覆盖范围：匹配查询的所有模板（可能超过 20 个）

### After（新行为）
```
topIntentChipsFromTopicCounts(
  calculateTopicCooccurrence(inspirations, TEMPLATE_TOPICS, 20),
  { topN: 5, minCount: 2 }
)
```
- 数据来源：**排名后前 20 条 inspiration 结果**，每条结果的 `mergedTopics`（inspiration 自身 topics ∪ 父模板 topics）
- inspiration-level output-type topics 现在也可以贡献 chip（之前不行）
- 父模板 topics 依然贡献
- 每条结果对每个 slug 至多贡献 +1（per-result 去重）
- 同义词折叠通过 result-ID Set 并集精确去重（见下节）

### 同义词折叠去重保证
`topIntentChipsFromTopicCounts` 内部：
```typescript
const foldedResultIds = new Map<string, Set<string>>();
for (const { slug, resultIds } of cooccurrence.mergedTopicCounts) {
  if (!OUTPUT_TYPE_SET.has(slug)) continue;
  const folded = SYNONYM_FOLDS[slug] ?? slug;  // "art-prints" → "wall-art"
  // Union the resultIds sets
  for (const id of resultIds) foldedResultIds.get(folded)!.add(id);
}
// Count = size of the unioned set (not sum of counts)
return [...foldedResultIds.entries()]
  .map(([slug, ids]) => ({ slug, count: ids.size }))
  ...
```

若某结果 `insp-X` 的 `mergedTopics` 同时包含 `art-prints` 和 `wall-art`（因为父模板两者都有）：
- `mergedTopicCounts` 中 `art-prints.resultIds = ["insp-X"]`（count=1）
- `mergedTopicCounts` 中 `wall-art.resultIds = ["insp-X"]`（count=1）
- 折叠后：`foldedResultIds.get("wall-art") = Set {"insp-X"}`（Set 去重，size=1）
- 最终 `wall-art.count = 1`，不是 2 ✓

### 保留的现有行为
| 特性 | 是否保留 |
|------|---------|
| `OUTPUT_TYPE_SLUGS` 词汇过滤 | ✓ 保留 |
| `SYNONYM_FOLDS` 同义词折叠 | ✓ 保留（语义一致，实现改进） |
| `minCount` 最小计数阈值 | ✓ 保留 |
| `topN` 最大 chip 数量 | ✓ 保留 |
| `IntentChip` 输出类型 `{ slug, count }` | ✓ 保留 |
| `withinSlug` 激活时返回 `[]` | ✓ 保留 |
| 确定性排序 | ✓ 保留（count 降序，slug 升序） |

---

## 6. 搜索行为是否发生变化

### 未改变的检索/排名行为

以下逻辑**完全未修改**：

1. **查询标准化**：`buildSearchTokens`、停用词过滤、英文复数还原、CJK 双字节分词 — 未改变
2. **严格/宽松双通道匹配**：strict-AND + relaxed-OR + bigram 阈值 — 未改变
3. **相关度评分**：`scoreBlob` 函数 — 未改变
4. **复合词精度防护（compound-noun guard）**：topical blob 逻辑 — 未改变（仅将 `[...(r.topics ?? []), ...(TEMPLATE_TOPICS.get(r.template_id) ?? [])]` 替换为等价的 `mergedTopics`）
5. **LLM rewrite 路径**：`rewriteQuery` 触发条件、多轮 merge — 未改变
6. **结果排序**：score 降序 — 未改变
7. **80 条结果上限**：`.slice(0, 80)` — 未改变
8. **withinSlug 过滤**：inspiration 和 template 两侧过滤 — 未改变
9. **related topics**：`topicCounts` 逻辑 — 未改变
10. **matched templates rail**：`buildNanoFeedCards` + i18n blob — 未改变
11. **WC country 重定向**：未改变
12. **gallery prompts**：Redis 查询逻辑 — 未改变
13. **topic 页面重定向**：未改变

### 有意改变的行为（Multi-Intent 证据层）

1. **blob 内容**：从 `[...r.topics, ...TEMPLATE_TOPICS.get(r.template_id)]`（可能含重复）改为 `resolveTopics(...).mergedTopics`（已去重）。搜索得分不受影响（重复 token 不增加 `primaryHits` 计数）。
2. **intent chip 来源**：从 matched template topics → Top 20 ranked result 的 merged topic 共现证据。chip 内容可能不同（inspiration-level output-type topics 现在也有贡献），但 chip 的用途（`/search?within=<slug>` 过滤导航）完全不变。

---

## 7. 测试结果

### 运行命令

```bash
npx vitest run --config vitest.unit.config.ts
```

### 输出结果

```
 RUN  v3.2.4 /Users/baobaoli/Desktop/curify-frontend

 ✓ |unit| lib/__tests__/topic_resolver.test.ts (20 tests) 4ms
 ✓ |unit| lib/__tests__/intent_clusters.test.ts (12 tests) 12ms
 ✓ |unit| lib/__tests__/topic_cooccurrence.test.ts (10 tests) 13ms

 Test Files  3 passed (3)
      Tests  42 passed (42)
   Start at  20:03:13
   Duration  394ms
```

**42 / 42 通过，0 失败，0 跳过。**

### TypeScript 类型检查

```bash
npx tsc --noEmit
```

输出：无（零错误，零警告）。

### 空白检查

```bash
git diff --check
```

输出：`no whitespace errors`

### 覆盖的测试用例（按任务要求编号）

| # | 用例描述 | 测试文件 |
|---|---------|---------|
| 1 | Topic resolver 合并 inspiration 和 template topics | `topic_resolver.test.ts` |
| 2 | 重复 topics 被去除 | `topic_resolver.test.ts` |
| 3 | 缺失 inspiration topics 被安全处理 | `topic_resolver.test.ts` |
| 4 | 缺失 template topics 被安全处理 | `topic_resolver.test.ts` |
| 5 | 未知 template_id 被安全处理 | `topic_resolver.test.ts` |
| 6 | 无效和空 topic 值被忽略 | `topic_resolver.test.ts` |
| 7 | Co-occurrence 默认只分析前 20 条结果 | `topic_cooccurrence.test.ts` |
| 8 | 同时出现在 inspiration 和 template 的 topic 在 merged 中只计一次 | `topic_cooccurrence.test.ts` |
| 9 | Inspiration 和 template 来源计数保持独立 | `topic_cooccurrence.test.ts` |
| 10 | 相同 count 时按 slug 升序确定性排序 | `topic_cooccurrence.test.ts` |
| 11 | `art-prints` 同义词折叠遵循 `wall-art` 折叠行为 | `intent_clusters.test.ts` |
| 12 | 现有 minCount 过滤仍然有效 | `intent_clusters.test.ts` |
| 13 | 现有 topN 行为仍然有效 | `intent_clusters.test.ts` |
| 14 | Inspiration-level output topics 现在可贡献 intent chip | `intent_clusters.test.ts` |
| 15 | Template-level output topics 仍然可贡献 intent chip | `intent_clusters.test.ts` |

**额外验证：**
- 同一结果同时含 `art-prints` + `wall-art` 时折叠后 count = 1，不是 2（`intent_clusters.test.ts`）
- 跨不同结果的同义词折叠（各来自不同 template）后 count = 2（不是 1 也不是 4）（`intent_clusters.test.ts`）

### 已知的无关错误

原有 `vitest.config.ts` 中的 storybook 项目因 `.storybook/` 目录不存在而**在本次工作前已经无法运行**（`MainFileMissingError`）。本次未修改 `vitest.config.ts`，该问题与本次变更无关。

---

## 8. Git Diff 摘要

### `git status --short`

```
 M app/[locale]/(public)/search/page.tsx
 M lib/intent_clusters.ts
?? lib/__tests__/
?? lib/topic_cooccurrence.ts
?? lib/topic_resolver.ts
?? vitest.unit.config.ts
```

### `git diff --stat`（已跟踪文件）

```
 app/[locale]/(public)/search/page.tsx | 33 +++++++++++++++------------
 lib/intent_clusters.ts                | 43 +++++++++++++++++++++++++++++++++++
 2 files changed, 61 insertions(+), 15 deletions(-)
```

### 新增未跟踪文件

| 文件 | 行数 |
|------|------|
| `lib/topic_resolver.ts` | 99 行 |
| `lib/topic_cooccurrence.ts` | 120 行 |
| `vitest.unit.config.ts` | 8 行 |
| `lib/__tests__/topic_resolver.test.ts` | ~140 行 |
| `lib/__tests__/topic_cooccurrence.test.ts` | ~130 行 |
| `lib/__tests__/intent_clusters.test.ts` | ~160 行 |

### 确认未修改

| 检查项 | 状态 |
|--------|------|
| `public/data/nano_inspiration.json` | ✓ 未修改 |
| `public/data/nano_templates.json` | ✓ 未修改 |
| `lib/taxonomy.json` | ✓ 未修改 |
| `package-lock.json` | ✓ 未修改 |
| `package.json` | ✓ 未修改 |
| `.env.local` | ✓ 未修改 |
| `vitest.config.ts` | ✓ 未修改 |
| 任何 daily report / 评估数据 | ✓ 未修改 |
| 无 `console.log` 调试代码 | ✓ 确认 |
| 无运行时 LLM 调用 | ✓ 确认 |
| 无 API key 暴露 | ✓ 确认 |
| 客户端组件不导入 JSON 数据集 | ✓ 确认（resolver 不导入 JSON） |

---

## 9. 手动验收步骤

以下 URL 路径在开发服务器启动后可用于手动验收（本报告不启动服务器，仅提供路径）：

### 查询：`cats`

```
http://localhost:3000/en/search?q=cats
```

预期行为：
- 搜索逻辑同之前（`cats` 经复数还原处理为 `cat`，或直接匹配带 `cat` 的记录）
- intent chips 由 Top 20 ranked inspiration 的 merged topic 共现计算；若结果中有含 `infographic`、`illustration` 等 output-type topic 的 inspiration，chips 应出现对应 slug

```
http://localhost:3000/zh/search?q=cats
```

### 查询：`dinosaur`

```
http://localhost:3000/en/search?q=dinosaur
```

预期行为：
- 匹配含 `dinosaur` 的 inspiration 和模板记录
- intent chips 基于 Top 20 ranked result；若排名前 20 含多个 `infographic` 或 `illustration` 模板，对应 chip 应出现

```
http://localhost:3000/zh/search?q=dinosaur
```

### 查询：`science poster`

```
http://localhost:3000/en/search?q=science+poster
```

预期行为：
- 多词 AND 匹配 `science` + `poster`
- 结果包含 `infographic`、`illustration`、`wall-art` 等 output-type 相关的模板
- intent chips 应出现 `infographic`（或 `illustration`、`wall-art`）等，且来自 inspiration 和模板两个层级的证据

### withinSlug 过滤验证

```
http://localhost:3000/en/search?q=science+poster&within=infographic
```

预期：intent chips 不显示（`withinSlug` 激活时返回 `[]`），页面顶部显示 `infographic` 可移除 pill，结果集仅含含 `infographic` topic 的 inspiration 和模板。

---

## 10. 下一步建议

**下一阶段：将 raw topic 证据映射到高层次创作意图集群（8 个 Creation Intent Clusters）**

当前 `mergedTopicCounts` 已提供了每条查询下 Top 20 结果的原始 topic 频率分布。下一步是在 `lib/intent_clusters.ts` 中定义 8 个高层次创作意图集群（如"学习内容"、"视觉艺术"、"社交媒体创作"等），将 `OUTPUT_TYPE_SLUGS` 词汇映射到对应集群，然后：

1. 在 `calculateTopicCooccurrence` 的输出基础上，按集群汇总 `mergedTopicCounts` 中的证据
2. 使用与当前 `topIntentChipsFromTopicCounts` 相同的 result-ID Set 并集机制，确保同一结果对同一集群只计一票
3. 以集群为单位生成新版 intent chips，并更新 `SearchResultsClient` 渲染侧
4. 集群显示名称通过 `topics` namespace i18n 配置，与现有 slug chip 方式一致

此阶段不需要修改数据集、不需要新的 LLM 调用，可在当前基础架构上直接叠加。
