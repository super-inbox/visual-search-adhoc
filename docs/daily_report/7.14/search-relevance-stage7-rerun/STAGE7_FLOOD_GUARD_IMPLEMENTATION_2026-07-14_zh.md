# Stage 7 Flood Guard Implementation

实现时间：2026-07-14。本阶段修改了 production 搜索代码和对应单元测试，实现了 Prompt 1 确认的三个最小 Guard。未重跑完整 68 条、未批量调用 LLM、未 Commit / Push、未修改 7.13 / Prompt 0 / Prompt 1 文件。

## 1. Executive Summary

- 实现了 Prompt 1 确认的全部三个 Guard：
  - **Guard 1**：空可执行 Token Fail Closed（`page.tsx` 的 `scoreBlob`）
  - **Guard 2**：非 Subject Decomposition Slot 绑定 Subject（`searchRewrite.ts` 的 `flattenPathsWithDiagnostics`）
  - **Guard 3**：结构化诊断与安全回退（两个文件协同，日志 + Cache TTL 分类修正）
- 未实现（按 Prompt 2 第 1 节明确排除）：全目录 IDF/词频基础设施、静态 generic-term 黑名单、第二个 LLM Judge、Rewrite confidence model、固定 Top N 截断、大规模 Ranking 重写、Merge 架构重构。全部记录在第 11 节 Deferred。
- **单元测试：全部通过**——7 个测试文件、**260/260** 通过，其中新增/修改测试覆盖 Guard 1（14 条新用例）、Guard 2（14 条新用例）、Cache 回归（2 条新用例）、1 条既有测试的必要断言更新（见第 4/5/7 节）。
- **TypeScript：通过**（`npx tsc --noEmit`，exit code 0，零错误）。
- **Production Build：通过**（`npx next build`，exit code 0）。构建日志中出现的 `MISSING_MESSAGE: blog.contentTaggingSystem...` 属于 pre-existing、与本阶段无关的 Blog i18n 缺口（本阶段完全未触碰任何 Blog 文件，已用哈希逐一核实，见第 10 节），不属于本次改动引入的问题。
- **具备进入定向 Smoke Test（Prompt 3）的条件**：是（见第 13 节 READY_WITH_LIMITATIONS）。
- **本阶段尚不能证明什么**：单元测试证明的是"Guard 逻辑在受控输入下按预期工作"，不证明"真实 68 条 Query 的相关性分数会提升"——这需要 Prompt 3 的定向 Smoke Test（对少量真实 Query 实际跑一次 production 路径）才能观察，本阶段禁止执行且未执行。同样不证明"没有引入任何未被 68 条覆盖的新回归"，因为 68 条从未被本阶段重跑。

## 2. Confirmed Root Causes

继承自 Prompt 1《STAGE7_FLOOD_ROOT_CAUSE_ANALYSIS_2026-07-14_zh.md》：

- **empty primary vacuous match**：`scoreBlob()` 中 `requiredSlots = tokens.primary.length + aliasGroups.length`，`allPrimary = (primaryHits+groupHits === requiredSlots)`。当某路径的可执行 token 完全为空（如 decomposition slot 值恰为停用词 `"template"`）时，`requiredSlots=0`，`0===0` 恒真，导致该路径对全部目录记录判定为 strict 匹配。已直接确认为 Q39、Q40 满目录（3209）洪泛的根因，且该 bug 在 pre-Stage-6 与 Stage 6 版本中逐字相同（非本阶段引入，属于此前从未被触发的既存缺陷）。
- **unbound non-subject slots**：decomposition 将 `style`/`scene`/`output`/`era`/`mood` 当作与 `subject` 平级、彼此独立的检索路径；每个非 subject slot 的值单独执行完整的 `buildSearchTokens → scoreQueryTokens`，从设计上就不携带任何实体约束。确认解释 15/23 洪泛 Case（`GENERIC_STANDALONE_REWRITE` 分类）。
- **union merge amplification**：`inspirationById` 是跨 1 个原始 Query + 最多 3 个 rewrite + 最多 6 个 decomposition slot（实践中约 6-7 条不重复路径）的按记录 ID 取最高分 Union 合并，没有单路径结果预算上限，多个中等宽泛路径可以联合放大到 1000+（确认解释剩余 6/23 `DECOMPOSITION_TOO_BROAD` Case）。本阶段的 Guard 1/2 从源头上减少了会进入这个 Union 的"坏路径"数量，但没有改动 Union 合并机制本身（未在批准范围内）。

## 3. Implementation Scope

### 修改文件（Prompt 2 本阶段实际改动，均为 2 个 production 源文件 + 2 个测试文件）

```text
/Users/baobaoli/Desktop/curify-frontend/app/[locale]/(public)/search/page.tsx
/Users/baobaoli/Desktop/curify-frontend/lib/searchRewrite.ts
/Users/baobaoli/Desktop/curify-frontend/lib/__tests__/searchRewrite.test.ts
/Users/baobaoli/Desktop/curify-frontend/lib/__tests__/stage6_dictionary_hybrid.test.ts
```

### 新增文件

无新增 production 文件。仅新增本阶段的 ad-hoc 报告（见第 14 节）。

### 修改的函数

| 文件 | 函数 | 改动性质 |
|---|---|---|
| `page.tsx` | `scoreBlob` | Guard 1：新增 `requiredSlots > 0 &&` 前置条件 |
| `page.tsx` | `hasExecutableConstraint`（新增小型纯函数） | Guard 1：判断一个 token 集合是否携带任何真实约束 |
| `page.tsx` | `SearchPage`（decomposition-path 迭代循环，约 719-800 行） | Guard 2/3：改用 `flattenPathsWithDiagnostics` 消费绑定后的路径 + 拒绝 slot 的结构化诊断日志 + 空 token 路径的诊断日志与合并前拦截 |
| `searchRewrite.ts` | `flattenPathsWithDiagnostics`（新增） | Guard 2：subject 绑定核心逻辑；返回 `{executed, rejected}` |
| `searchRewrite.ts` | `flattenPaths`（保留，改为委托新函数） | 向后兼容：签名/返回类型不变（仍是 `string[]`），内容自动反映 Guard 2 的绑定结果 |
| `searchRewrite.ts` | `getMultiQueryPaths` 中的 `hasExecutablePath` 计算 | Guard 3：改为委托 `flattenPathsWithDiagnostics(trimmed, out).executed.length > 0`，使 Cache 分类与 Guard 2 后的真实可执行路径一致 |

### 未修改部分

- `lib/query_phrase_aliases.ts`、`lib/cjk_tokenizer.ts`、`lib/zh_normalize.ts` — 未改动（哈希核实，见第 10 节）。
- `lib/__tests__/search_metadata_scenarios.test.ts` — 未改动（本次未涉及其覆盖的场景，哈希核实见第 10 节）。
- Stage 7 harness（`scripts/curify-search-collect-stage7/*`）— 未修改。诊断信息通过 `console.error` 结构化日志（`errorType=` key/value 风格，与 `searchRewrite.ts` 已有的日志约定一致）暴露，harness 若要读取只需解析日志文本，不需要 harness 代码改动，因此按 Prompt 第 8 节"若无需修改 harness 即可保存诊断，则不要修改 harness"的要求，未触碰 harness。
- Merge/dedup/ranking 架构、最终 `.slice(0, 80)` 截断、目录词频/IDF 基础设施 — 均未改动（按 Prompt 第 1 节明确排除）。

## 4. Guard 1 — Empty Tokens Fail Closed

**修改前**（`app/[locale]/(public)/search/page.tsx`）：

```ts
return {
  primaryHits: primaryHitsOnly + groupHits,
  bigramHits,
  allPrimary: primaryHitsOnly + groupHits === requiredSlots,
  relaxedOk,
};
```

**修改后**：

```ts
return {
  primaryHits: primaryHitsOnly + groupHits,
  bigramHits,
  // Guard 1 (Stage 7R Prompt 2): requiredSlots === 0 means zero primary
  // tokens AND zero alias groups survived buildSearchTokens (e.g. a
  // decomposition slot that reduced to the bare stopword "template").
  // ...An empty constraint has nothing to test a blob against and must
  // fail closed, never match-everything.
  allPrimary: requiredSlots > 0 && primaryHitsOnly + groupHits === requiredSlots,
  relaxedOk,
};
```

**判断条件**：`requiredSlots = tokens.primary.length + aliasGroups.length`。当此值为 0（既没有 primary token，也没有 alias group），`allPrimary` 现在显式为 `false`，而不是落入 `0 === 0` 的 JavaScript 相等比较恒真分支。这不是字面的 `[].every(...)`，但数学效果完全等价，已在修改中以注释明确说明原因。

同时在 `SearchPage` 的 decomposition-path 迭代循环中新增前置检查（`hasExecutableConstraint`），在调用 `scoreQueryTokens` **之前**就拒绝空约束路径——这既是性能优化（避免对 3209 条记录做一次注定全零的扫描），也是 Guard 3 诊断的挂载点。

**Q39/Q40/Q42 机制如何被阻止**：

- **Q39/Q40**：decomposition 的 `output` slot 恰为裸词 `"template"`。`buildSearchTokens("template")` 经 `STOPWORDS.has("template")` 过滤后 `primary=[]`，且未命中任何 Protected Phrase/概念组，`aliasGroups=[]`。修复前：`requiredSlots=0`，`allPrimary` 对全部 3209 条记录恒为 `true`。修复后：`requiredSlots=0` 时 `allPrimary` 直接为 `false`，该路径不产生任何 strict/relaxed 命中，也不会进入 Union 合并。
- **Q42**：在 D 模式的独立 LLM 调用中，`output` slot 值为两词短语 `"cover template"`；即使 Guard 1 单独存在，`buildSearchTokens("cover template")` 本身就会产生 `primary=["cover"]`（非空，"template"被过滤但"cover"存活），所以这一具体案例的洪泛主要由 Guard 2（见第 5 节）处理——"cover"不再脱离 subject 独立执行，而是绑定为 `"<subject> cover template"`，限制了匹配范围。若换一次 LLM 调用恰好返回裸 `"template"`（如 Prompt 0 审计记录到的 Mode C 独立调用），Guard 1 同样会拦截。

**测试**（新增于 `lib/__tests__/stage6_dictionary_hybrid.test.ts`，`describe("Guard 1 (Stage 7R Prompt 2): empty executable tokens fail closed")`，14 条）：

- 空字符串、纯空白、单个停用词（`"the"`）、多个停用词（`"the and or"`）
- 裸 `"template"`（Q39/Q40 的确切根因形状）——显式断言 `strictCount` 不等于目录总记录数（不硬编码 3209，使用 `INSP.length`/`ALL_TEMPLATE_IDS.size` 动态引用）
- `"cover template"`——断言 `primary=["cover"]`，是真实的非空约束
- 有效 token + 停用词（`"the poster"` vs `"poster"` 结果一致）
- 纯 alias-group 约束（`"手冲咖啡"`，`primary=[]` 但 `aliasGroups.length>0`）——显式断言这类路径**不**被 Guard 1 误伤，仍可正常 `allPrimary=true`
- 正常英文（`"basketball shoes"`）、正常中文（`"小红书"`）、中英文混合（`"小红书cover设计"`）——断言行为不受影响
- `scoreBlob` 直接调用：空约束对任意 blob 内容（含空字符串、纯 poster/template/design、纯中文）均返回 `allPrimary=false`

## 5. Guard 2 — Subject-bound Decomposition

**修改前 path**（`lib/searchRewrite.ts` 原 `flattenPaths`）：每个非空 decomposition slot（含 `style`/`scene`/`output`/`era`/`mood`）都被直接 `push` 为独立路径，与 `subject` 平级，无绑定：

```text
输入: { subject: "小红书营销", output: "poster", style: "playful" }
执行 paths: ["小红书营销", "poster", "playful"]   // poster/playful 完全无约束
```

**修改后 path**（新函数 `flattenPathsWithDiagnostics`）：

```text
输入: { subject: "小红书营销", output: "poster", style: "playful" }
执行 paths: ["小红书营销", "小红书营销 poster", "小红书营销 playful"]
被拒绝: []  (因为 subject 存在，两个非 subject slot 都成功绑定)
```

- `subject` slot 本身仍可独立执行（它就是实体锚点，语义上安全，行为不变）。
- 每个非 subject slot 独立与 `subject` 文本拼接（`${subject} ${slotValue}`），生成**一个**新的绑定路径，不是把所有非 subject slot 一次性 AND 拼接成单一超长字符串（已用测试验证：`{subject:"咖啡品牌", style:"极简", scene:"门店", output:"海报"}` 产生 3 个独立的 `"咖啡品牌 X"` 绑定路径，而不是 1 个 `"咖啡品牌 极简 门店 海报"`）。
- 原有的 `original`-去重（`compareKey` + `seen` Set）逻辑完整保留，绑定后的新字符串仍会与原始 Query 及已有路径去重。

**subject 缺失时行为**：

```text
输入: { output: "poster", style: "playful" }   // 没有 subject
执行 paths: []
被拒绝: [
  { slotKey: "output", slotValue: "poster", reason: "UNBOUND_NON_SUBJECT_SLOT" },
  { slotKey: "style", slotValue: "playful", reason: "UNBOUND_NON_SUBJECT_SLOT" }
]
```

不猜测、不臆造锚点（例如不会退回去用原始 Query 文本当锚点）——严格按 Prompt 2 第 7 节要求：没有 subject 时非 subject slot 一律拒绝，安全回退到原始 Query 路径（`baseResult`，本来就总是先被计算并写入 `inspirationById`）。

**stopword-only slot 行为**：Guard 2 只做**文本层面**（是否非空字符串）的 subject 有效性判断，不重复实现 `STOPWORDS`/CJK 分词逻辑（避免跨模块耦合、避免逻辑重复）。若 `subject` 本身恰好是纯停用词（如 `"the"`），Guard 2 仍会按文本绑定（`"the playful"`），但 **Guard 1 是下游的真正安全网**——`buildSearchTokens("the playful")` 会把 `"the"` 过滤掉，剩下 `"playful"` 是真实、非空的约束，不会洪泛；若不巧两侧都是停用词（如 `subject:"the", output:"template"` → `"the template"`），Guard 1 在 `page.tsx` 层面会正确判定该绑定路径 `hasExecutableConstraint=false` 并拒绝进入 merge。这是有意的分层设计（文本层 Guard 2 + token 层 Guard 1 互补），已在代码注释和测试中明确说明。

**英文/CJK/混合 Query 行为**：

- English subject + English output：`{subject:"basketball shoes", output:"poster"}` → `"basketball shoes poster"`，`"poster"` 不再独立执行。
- Chinese subject + English output（`乔丹鞋 → 篮球鞋` 场景）：`{subject:"篮球鞋", output:"poster"}` → `"篮球鞋 poster"`；`"篮球鞋"` 本身作为 subject 仍可独立执行——**合理的字面到更宽类别的泛化路径完全保留**，Guard 2 不touch `rewrites` 数组，也不阻止 subject 本身的合理泛化值。
- English subject + Chinese modifier：`{subject:"BYD Seal", style:"国风"}` → `"BYD Seal 国风"`。
- 型号/缩写/数字 token（`蔚来es6`）：`{subject:"蔚来es6", output:"poster"}` → `"蔚来es6 poster"`，正常绑定，空格拼接不破坏 ASCII/数字/CJK 混排。

**测试**（新增于 `lib/__tests__/searchRewrite.test.ts`，`describe("Guard 2 (Stage 7R Prompt 2): subject-bound decomposition paths")`，14 条）：基础绑定、Template Case、Cover Template Case、无 Subject、合法 Subject-only、English+English、Chinese+English、English+Chinese、型号 token、stopword-only subject、stopword-only 非 subject slot、多修饰词独立绑定（非拼接）、plain rewrites 不受影响。

## 6. Guard 3 — Diagnostics and Fallback

### 实际字段

`lib/searchRewrite.ts` 新增导出类型：

```ts
export type FlattenedPath = {
  text: string;                                    // 最终实际执行的 Query/path
  slotKey: keyof QueryDecomposition | "rewrite";    // 原始 slot key（或 "rewrite"）
  slotValue: string;                                // 原始 slot 内容
  subjectBound: boolean;                            // 是否绑定 subject/entity
};

export type RejectedSlot = {
  slotKey: keyof QueryDecomposition;
  slotValue: string;
  reason: "UNBOUND_NON_SUBJECT_SLOT";               // 拒绝原因
};

export type FlattenPathsResult = {
  executed: FlattenedPath[];   // 进入 Merge 的路径
  rejected: RejectedSlot[];    // 未进入 Merge 的路径 + 原因
};
```

`page.tsx` 侧通过 3 条结构化 `console.error` 日志（沿用 `searchRewrite.ts` 既有的 `[模块名] errorType=<reason> key=value ...` 风格，未引入新 schema）：

```text
[search.multiPath] errorType=UNBOUND_NON_SUBJECT_SLOT query=<原始Query> slotKey=<slot名> slotValue=<slot内容>
[search.multiPath] errorType=EMPTY_EXECUTABLE_TOKENS query=<原始Query> slotKey=<slot名> path=<最终执行文本>
[search.multiPath] errorType=NO_VALID_REWRITE_PATH query=<原始Query>
```

### rejection reason

- `UNBOUND_NON_SUBJECT_SLOT`：Guard 2 拒绝——非 subject slot 且无有效 subject 可绑定。
- `EMPTY_EXECUTABLE_TOKENS`：Guard 1 拒绝——路径文本 tokenize 后零 primary token 且零 alias group。
- `NO_VALID_REWRITE_PATH`：Guard 3 汇总——本次 rewrite/decomposition 展开尝试后，没有任何路径存活到实际执行（可能是 Guard 2 拒绝了全部 slot，也可能是 Guard 1 又拒绝了 Guard 2 放行的路径，或 LLM 本来就没返回任何 rewrite/decomposition）。

### fallback

- 原始 Query 的 `baseResult`（`scoreQueryTokens(tokens)`，未经任何 Guard 过滤）始终在 decomposition/rewrite 展开逻辑运行**之前**就已经计算并写入 `inspirationById`（`page.tsx` 第 673/681 行，本阶段未改动这两行本身的位置和逻辑）。因此无论 Guard 1/2 拒绝多少个候选路径，原始 Query 结果永远保留，不会因为 Guard 而丢失。
- 所有候选路径都被拒绝时：`executedPathCount === 0`，不会有任何空路径进入 `inspirationById`/`strictTemplateMatchesUnion`/`matchedTemplateIdsByI18nUnion`（因为 `continue` 直接跳过该候选，从不执行 `scoreQueryTokens`），不返回完整目录，不抛出未处理异常（`hasExecutableConstraint`/`flattenPathsWithDiagnostics` 均为纯函数，无 I/O、无 throw）。

### merge 行为

- 被拒绝的路径（`rejected` 数组中的 slot，或 Guard 1 判定 `hasExecutableConstraint=false` 的候选）**从不**调用 `scoreQueryTokens`，因此绝不可能写入 `inspirationById`/`strictTemplateMatchesUnion`/`matchedTemplateIdsByI18nUnion`——不存在"先算出全目录结果再事后过滤"的路径，是在合并**之前**拦截。
- 存活的绑定路径正常调用 `scoreQueryTokens(pathTokens, false)`，走原有的 `promoteAllUnderStrictTpl=false` 精度分支，与本阶段之前完全一致（未改动这部分逻辑本身）。
- `usedPathsCount` 从"全部展开路径数"改为"实际执行（未被 Guard 拒绝）的路径数 + 1"，更准确地反映真实参与 Union 的路径数量，用于下游的 multi-hit 排序加权（`+8%/额外路径`，未改动加权公式本身）。

## 7. Cache Semantics

### Success Cache / Negative Cache

- **修改前**：`hasExecutablePath = rewrites.length > 0 || Object.keys(decomposition).length > 0`——只要 decomposition 有任意非空 key（哪怕全部是无 subject 可绑定的独立 slot），就判定为"有可执行路径"，缓存 7 天。
- **修改后**：`hasExecutablePath = flattenPathsWithDiagnostics(trimmed, out).executed.length > 0`——直接复用 Guard 2 的真实绑定/拒绝逻辑，两者永远不会不一致（单一事实来源）。

### 各场景验证结果

| 场景 | Cache 分类 | 验证方式 |
|---|---|---|
| 至少一个 Rewrite 或 decomposition 路径真正可执行 | Success Cache（7 天） | 既有测试 1/10/baseline，全部保持通过 |
| Guard 后没有可执行 path（decomposition 只有非 subject slot，无 subject） | **Negative Cache（10 分钟）** | **新增测试 9b**——修改前此场景会被误判为 Success Cache，现已修正 |
| decomposition 含有效 subject（即使只有 subject，无其他 slot，或 subject+非 subject 绑定） | Success Cache（7 天） | **新增测试 9c** |
| Empty output | Negative Cache | 既有测试 4/5，未受影响，仍通过 |
| Model refusal | Negative Cache | 既有测试 6，未受影响 |
| Same-query-only | Negative Cache | 既有测试 7/8，未受影响 |
| 所有 decomposition slot 被拒绝（无 subject） | Negative Cache | 同上新增测试 9b |
| 合法部分候选存活 | Success Cache | 既有测试 10，未受影响 |

**未破坏已有 Stage 5 测试**：`describe("Cache Completion Patch...")` 整个 describe block 的全部原有 11+ 条测试保持通过（见第 9 节验证结果），仅新增 2 条（9b/9c），未删除、未跳过、未降低任何既有断言强度。

## 8. Test Matrix

### 新增测试（本阶段新增，共 30 条）

**`lib/__tests__/stage6_dictionary_hybrid.test.ts`**（新增 describe block，14 条）：
空字符串 / 纯空白 / 单停用词 / 多停用词 / 裸 `template`（Q39/Q40 根因形状） / `cover template`（Q42 相关形状） / 有效 token+停用词 / alias-group-only 约束不被误伤 / 正常英文 / 正常中文 / 中英文混合 / `scoreBlob` 直接空约束（4 种 blob 内容） / 目录非空的健全性检查

**`lib/__tests__/searchRewrite.test.ts`**（新增 describe block，14 条 + Cache 回归 2 条）：
基础绑定 / Template Case / Cover Template Case / 无 Subject（含拒绝诊断断言） / 合法 Subject-only / English+English / Chinese+English（含 `乔丹鞋→篮球鞋` 场景说明） / English+Chinese / 型号 token / stopword-only subject / stopword-only 非 subject slot / 多修饰词独立绑定 / plain rewrites 不受影响 / Cache: 无 subject 全拒绝→Negative / Cache: 有 subject→Success

### 修改的既有测试（1 条，必要的断言更新）

`lib/__tests__/searchRewrite.test.ts` 的 `"never includes the original query itself in the flattened extra-paths list"`：原断言期望裸 `"brand"` 独立路径（Guard 2 存在的目的正是消除这类路径），现更新为期望绑定后的 `"<subject> brand"`，并附带详细注释说明这是 Guard 2 刻意改变的行为，非放松断言。

### 既有测试（全部保持不变、全部通过，未删除/未跳过/未降低断言）

`lib/__tests__/searchRewrite.test.ts` 原有 62 条（Stage 5 硬化测试全集）、`lib/__tests__/stage6_dictionary_hybrid.test.ts` 原有 ~54 条（segmentCJKToken/协议短语/CJK 分词/merge-and-filter/concept-group 等 7 个既有 describe block）、`lib/__tests__/search_metadata_scenarios.test.ts` 全部 65 条（未触碰）、`lib/__tests__/thin_recall_queries.test.ts` 28 条、`lib/__tests__/topic_resolver.test.ts` 20 条、`lib/__tests__/topic_cooccurrence.test.ts` 10 条、`lib/__tests__/intent_clusters.test.ts` 12 条。

## 9. Validation Results

| 命令 | 结果 | 数量 |
|---|---|---|
| `npx vitest run --config vitest.unit.config.ts lib/__tests__/searchRewrite.test.ts` | **PASS** | 64/64 |
| `npx vitest run --config vitest.unit.config.ts lib/__tests__/stage6_dictionary_hybrid.test.ts` | **PASS** | 61/61 |
| `npx vitest run --config vitest.unit.config.ts lib/__tests__/search_metadata_scenarios.test.ts` | **PASS** | 65/65 |
| `npx vitest run --config vitest.unit.config.ts`（全部 7 个测试文件） | **PASS** | **260/260**，0 失败 |
| `npx tsc --noEmit` | **PASS** | exit code 0，0 错误 |
| `npx next build` | **PASS** | exit code 0，构建产物正常生成 |
| `npx next lint` | **FAIL（pre-existing 配置问题）** | `tseslint.config()` 报告 `next/core-web-vitals` extends 数组与 typescript-eslint 不兼容，这是仓库级 ESLint 9 flat-config 与 Next.js 插件版本不匹配的既有配置问题，发生在**任何文件级 lint 规则执行之前**（config 加载阶段即失败），与本阶段改动的 3 个文件内容无关。未尝试修复（超出本阶段允许范围：修复需要改动 `eslint.config.js`/依赖版本，不在允许文件列表内）。 |

**本轮引入问题 vs pre-existing 问题的区分**：Lint 的 config 级失败是 pre-existing（`eslint.config.js`/`package.json` 均未被本阶段触碰，问题在改动前后表现一致）。Build 日志中的 `MISSING_MESSAGE: blog.contentTaggingSystem...` 同样是 pre-existing（Blog 相关 i18n 缺口，本阶段未改动任何 Blog 文件，见第 10 节哈希核实）。本阶段自身改动（Guard 1/2/3）未引入任何新的测试失败、TypeScript 错误或 Build 失败。

## 10. Git Diff Scope

### Prompt 2 修改的文件（本阶段实际改动，4 个）

```text
/Users/baobaoli/Desktop/curify-frontend/app/[locale]/(public)/search/page.tsx
/Users/baobaoli/Desktop/curify-frontend/lib/searchRewrite.ts
/Users/baobaoli/Desktop/curify-frontend/lib/__tests__/searchRewrite.test.ts
/Users/baobaoli/Desktop/curify-frontend/lib/__tests__/stage6_dictionary_hybrid.test.ts
```

### Prompt 2 新增的文件

无（`lib/__tests__/searchRewrite.test.ts`、`lib/__tests__/stage6_dictionary_hybrid.test.ts`、`lib/cjk_tokenizer.ts` 三个 untracked 文件早在 Prompt 2 开始前就已存在于工作区——只有前两者的**内容**被本阶段修改，`lib/cjk_tokenizer.ts` 完全未被触碰，哈希核实见下）。

### Prompt 2 前已存在的文件改动（不归因于本阶段）

以下 17 个文件的修改/新增早于本阶段开始，本阶段未新增改动（`page.tsx`/`searchRewrite.ts` 的 diff 行数在本阶段增加是因为 Guard 实现，其余全部无变化）：

```text
app/[locale]/(public)/blog/[slug]/components/GenericBlogContent.tsx  (Blog, 未触碰)
app/[locale]/(public)/blog/[slug]/page.tsx                            (Blog, 未触碰)
lib/query_phrase_aliases.ts                                          (未触碰)
lib/zh_normalize.ts                                                   (未触碰)
messages/{de,en,es,fr,hi,ja,ko,ru,tr,zh}/blog.json  (10 个 Blog 文件, 未触碰)
next.config.ts                                                        (未触碰)
package-lock.json                                                     (未触碰)
package.json                                                           (未触碰)
scripts/eval_search.cjs                                                (未触碰)
lib/__tests__/search_metadata_scenarios.test.ts                       (未触碰)
```

### Blog 文件未触碰的证明

逐文件 SHA-256 哈希在本阶段执行前、执行后完全一致（`GenericBlogContent.tsx`、`blog/[slug]/page.tsx`、10 个 `messages/*/blog.json`）——已在第 16 节执行后校验中逐项列出并核对。`lib/query_phrase_aliases.ts`、`lib/zh_normalize.ts`、`lib/cjk_tokenizer.ts`、`lib/__tests__/search_metadata_scenarios.test.ts` 同样哈希前后一致。

## 11. Deferred Options

以下方案已在 Prompt 1 的 Guard Design JSON 中评估过，本阶段按 Prompt 2 第 1 节明确指示**未实现**，理由摘要如下（详细评估见 Prompt 1 报告第 12 节）：

- **IDF/目录词频基础设施（Guard H）**：需要预计算并维护 `templateSearchBlob`/`nanoInspiration` 的 token 文档频率表，属于新的运行时状态和基础设施，本阶段范围明确排除。
- **Candidate budget（单路径结果预算，Guard E）**：治标（限制单路径贡献的记录数上限）不治本（不解决"为什么会宽泛匹配"），且阈值本身是新的硬编码风险点。
- **Layered merge（原始结果分层优先，Guard G）**：改变的是展示排序而非匹配集合本身的正确性，且属于 Merge 架构改动，本阶段范围明确排除大规模 Merge 重构。
- **Second judge（二次 LLM Judge/Confidence Model）**：增加延迟和成本，且引入第二层非确定性去判断一个本质上是确定性 token 计数问题（空 token/无实体绑定），层级不对。
- **Ranking redesign（大规模 Ranking 重写）**：本阶段范围明确排除。
- **Generic denylist（静态 generic-term 黑名单）**：会硬编码到英文营销词汇，不支持 CJK 对称词表，且是本阶段第 1 节明确禁止的方案之一（"不要把 poster、cover、style 等词写入静态黑名单"）。

## 12. Risks and Limitations

- **尚未进行真实 Smoke Test**：本阶段仅运行了单元测试（对 mock LLM 响应/构造的 decomposition 对象），未启动 dev/production server、未对任何真实 Query 执行端到端搜索请求。Prompt 3 的定向 Smoke Test 才会验证真实行为。
- **尚未重跑 68 条**：本阶段完全未执行 Stage 7 harness 或任何形式的 68 条批量评测，Guard 对 Q39/Q40/Q42 之外剩余 20 条洪泛 Case 的实际效果尚未被任何执行验证，只有代码逻辑层面的推断（Guard 2 的绑定机制理论上应该同样约束这些 Case 的非 subject slot，但未实测）。
- **单元测试不等于相关性改善**：全部 260 个单元测试通过只证明"给定构造好的输入，Guard 逻辑产生预期的中间结果（绑定路径文本、拒绝原因、token 集合）"，不证明"真实 68 条 Query 通过 Guard 后，人工或 LLM Judge 会打出更高的相关性分数"。这是两个不同层次的正确性，本报告不混淆二者。
- **LLM 非确定性**：Prompt 1 报告已确认同一 Query 在不同调用间会产生不同的 rewrite/decomposition 文本（Q01/Q39/Q42/Q53 均有实证）。Guard 1/2 对**任何**具体的 decomposition 输出内容都同样生效（不依赖某次调用恰好复现某个具体形状），但这意味着无法用"重跑一次看 Q39 是否还洪泛"来验证 Guard 效果——需要对同一批 LLM 输出（或固定 mock 输入）做前后对比，这也是本阶段测试全部采用构造/mock 输入而非依赖真实 LLM 调用的原因。
- **人工标签仍缺失**：继承自 Prompt 0/1，0/68 `human_relevance_label` 已填写，本阶段未产生任何新的人工判定。
- **数据目录漂移**：`nano_inspiration.json` 内容自 Stage 7 采集以来是否变化仍未量化，继承自 Prompt 1 的已知限制。
- **可能仍存在非 1000+ 的语义漂移**：本阶段的 Guard 只针对"结果数洪泛"这一具体症状（`>=1000`），Prompt 1 报告第 9 节确认存在 15 条"count increased but relevance decreased"且不在 23 条洪泛列表中的 Case（数量增长在个位数到 900 之间但相关性仍下降）——这类 Case 的根因可能与本阶段的 Guard 1/2 机制部分重叠（同样可能是 unbound slot 导致的中等规模噪音），但本阶段未针对性验证，也不在 Prompt 2 的三个 Guard 范围内。

## 13. Readiness for Prompt 3

**READY_WITH_LIMITATIONS**

理由：
- Empty-token fail-closed（Guard 1）已实现并有单元测试覆盖 Q39/Q40 的确切根因形状（裸 `"template"`）以及 Q42 相关的 `"cover template"` 形状。
- 非 subject decomposition slot 不再独立无约束执行（Guard 2），已用 14 条测试覆盖基础绑定、无 subject 拒绝、多语言组合、型号 token、多修饰词独立绑定（非拼接）等场景。
- 所有 Rewrite path 无效时的安全 fallback 已验证（原始 Query 结果保留、不返回空目录、不抛异常）。
- 结构化 rejection reason（`UNBOUND_NON_SUBJECT_SLOT`/`EMPTY_EXECUTABLE_TOKENS`/`NO_VALID_REWRITE_PATH`）已实现并在日志中可观测。
- Cache TTL 分类已修正为与 Guard 2 后的真实可执行路径一致，且不回归 Stage 5 既有测试。
- Protected Phrase、Alias OR-group、CJK tokenizer、纯英文/中文/混合 Query 均已用测试验证不回归。
- 定向测试、相关测试、全量单元测试、TypeScript、Production Build 全部通过。
- 未运行完整 68、未修改 7.13、未修改 Prompt 0/1、未 Commit/Push/PR/Merge、未切换分支。

不是纯粹 READY 的原因：
- (a) 尚未进行任何真实 Smoke Test（这正是 Prompt 3 的任务，本阶段被明确要求不执行）；
- (b) 全部验证证据来自单元测试和构造输入，尚无一条真实 68 Query 在 Guard 生效后的端到端观测数据；
- (c) Lint 存在 pre-existing 配置问题（与本阶段改动无关，但技术上"lint 命令本身不通过"这一事实需要如实记录）。

这些限制不阻塞 Prompt 3 进入定向 Smoke Test 阶段（Smoke Test 的目的正是弥补限制 (a)(b)），但 Prompt 3 应明确使用少量代表性 Query（包括 Q39/Q40/Q42 及其余 20 条洪泛 Case 的一个子集）做真实端到端观测，而非默认 Guard 已经"证明有效"。
