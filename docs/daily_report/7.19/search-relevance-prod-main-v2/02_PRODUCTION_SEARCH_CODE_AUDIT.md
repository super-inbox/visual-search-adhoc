# Stage 2: Production (V0) Search Code Audit

Date: 2026-07-19. Scope: read-only audit of `/Users/baobaoli/Desktop/curify-frontend-v0-baseline-2026-07-19` (SHA `05e5f2d332778ac52c712dd2429f4a8f4e7c3673`). No files in this worktree were modified. Old Candidate branch (`/Users/baobaoli/Desktop/curify-frontend`) consulted read-only only for historical context, never as a source of truth for V0 structure.

V0 build status (re-verified this session): `next build` succeeds, `tsc --noEmit` reports zero errors, existing Vitest unit suite (`lib/__tests__/**`, 7 files) is 111/111 passing.

## Entry point

`app/[locale]/(public)/search/page.tsx` (897 lines) — a Next.js App Router Server Component. All retrieval, scoring, merge, rewrite-gating, and rail-building logic for `/search` lives inline in this one file (there is no separate `lib/searchScoring.ts` or similar module — this differs from what the 7.17 design doc describes as the *old Candidate's* refactored `lib/searchTokens.ts`; **V0/Production main does not have that module**, confirmed by its absence from `find . -name searchTokens.ts` in this worktree).

Rendering is handed off to the client component `SearchResultsClient.tsx` (482 lines), which receives fully-computed props (`inspirations`, `matchedTemplates`, `galleryPrompts`, `usedRewrites`, `pathsUsed`, etc.) — no client-side re-fetching or re-scoring occurs.

## Query normalize

Two distinct, non-interacting normalizers exist:
- **`normalizeSearchQuery`** (`lib/query_normalize.ts:51-64`) — trims, lowercases, collapses whitespace, normalizes smart quotes/dashes, then does an exact-match lookup against a tiny hardcoded `QUERY_ALIASES` table (`cats→cat`, `kittens→kitten`). Used only for Business Override routing (`lib/search_business_override.ts`) and topic-redirect consistency — **not** used in the retrieval/scoring path.
- **`normalizeForSearch`** (inlined in `page.tsx:133-135`) — `tsToSc(s.toLowerCase().replace(/×/g,"x"))`: lowercases, `×→x`, and Traditional→Simplified Chinese via `lib/zh_normalize.ts`. This is the normalizer actually used for all blob/token matching (query tokens and catalog blobs alike).

## Tokenization

`buildSearchTokens()` (`page.tsx:137-188`): splits on whitespace + structural punctuation (`, ， 、 。 . : ： = · / | ( ) [ ] + *`), filters stopwords (`STOPWORDS`, `page.tsx:120-126`, includes English/Chinese function words + meta-words like "topic"/"guide"), applies a conservative English single-token plural-stem (`-ies→-y`, sibilant `-es`→strip, else strip trailing `-s`, guarded against `-ss/-us/-is/-os/-as`, only fires when the whole query reduces to exactly one token). For unsegmented CJK queries (single token, ≥2 Chinese characters), also generates character bigrams as a fallback signal (`page.tsx:175-186`).

**No phrase protection or subject-binding exists in tokenization today** — a multi-word query is just split into independent primary tokens; there is no mechanism to keep a known-risky phrase (e.g. "coffee cup", "咖啡杯") atomic. This is the gap Direction 6 targets.

## Protected phrase / Alias

- **No protected-phrase dictionary exists in V0.** Confirmed by absence of any "protected phrase" or phrase-atomicity concept in `page.tsx`, `lib/searchRewrite.ts`, or any lib file found by the audit subagent's grep sweep.
- **Alias** exists at the per-record level only: `InspRecord.search_aliases?: string[]` (`page.tsx:434-438`), a hidden synonym list baked into the catalog data (`public/data/nano_inspiration.json`), populated offline by `scripts/enrich_search_aliases.cjs`. It is folded into each inspiration's search blob (`page.tsx:523`) and matched with the same token-in-blob rule as everything else — aliases get **no separate weight tier**, they're just additional blob text.
- Separately, `lib/template_concept_expansion.ts`'s `CONCEPT_SYNONYMS` provides a query-side (not catalog-side) synonym expansion, applied only to the **template rail** when the strict template set is thin (`page.tsx:667-701`), not to inspirations.

## Strict / Relaxed retrieval

Both computed inside `scoreQueryTokens()` (`page.tsx:470-578`), one call per retrieval path (original query, each rewrite phrasing, each decomposition slot):
- **Strict**: `allPrimary` (every primary token found in blob, word-boundary-checked for ASCII / substring for CJK) OR `bigramHits >= bigramHitThreshold`. Templates whose i18n blob strict-matches get **all** of their inspirations auto-promoted to `score=100, strict=true` when `promoteAllUnderStrictTpl=true` (the default, used only for the *original* query pass — rewrite/decomposition passes use `promoteAllUnderStrictTpl=false` for precision).
- **Relaxed**: `primaryHits >= relaxedPrimaryThreshold(n)` where the threshold is `n<=1 ? 1 : ceil(n/2)` — i.e. roughly half the tokens must hit.
- A **compound-noun precision guard** (`page.tsx:531-570`) demotes a would-be-strict inspiration match to relaxed when the only reason it strict-matched is a single ASCII token appearing inside a multi-word param value (e.g. query `snake` matching param `plant_name: "snake plant"`) and the topical fields (template_id/tags/topics/aliases) don't independently carry the token.

## Current scoring function

There is **no unified numeric relevance score** in V0. Scoring is a two-tier bucket system (`strict: boolean`, `score: number` where `score = primaryHits + bigramHits`, or `100` for template-promoted strict hits), not a continuous, explainable, multi-factor score. Fields participating: **title/name is not scored directly** — the record blob (`page.tsx:517-529`) is built from `id, template_id, tags, mergedTopics (inspiration+template topics), search_aliases, params values, locale title/category` — so `title`/`category` (via `locales[].title`/`locales[].category`) **do** participate, and `tags`/`topics`/`description` (template-level, via the separate `templateSearchBlob`) **do** participate, but there is **no per-field weighting** — a hit in `title` counts identically to a hit in a low-signal `tags` entry. This directly answers the design doc's UNKNOWN #7 ("是否已经融合title+tags+category多字段支持"): **yes, multiple fields are merged into one blob, but with zero field-level weight differentiation** — confirmed by reading, not assumed.

Exact-phrase vs. whole-token vs. substring vs. stemming/alias are **not differentiated in score** today: `tokenInBlob` (`page.tsx:210-216`) does word-boundary matching for ASCII tokens (so it is whole-token, not raw substring, for English) but CJK tokens match by raw substring (`page.tsx:213`, `blob.includes(t)`) — this is the direct mechanism behind the coffee-cup/black-friday-style substring collisions for **Chinese** queries specifically (e.g. "咖啡杯" tokenized and any single-char/bigram overlap with an unrelated blob can register a hit), while English collisions like "cup" inside "World Cup" are prevented by the word-boundary regex for single ASCII tokens **but not** for multi-token AND-matches where a irrelevant record happens to contain all the individual words. No score differentiates "matched as a complete phrase" from "matched all tokens scattered across the blob."

## `LOW_RESULT_THRESHOLD`

`= 5`, defined at `page.tsx:47`, gates the LLM rewrite/multi-path expansion call (`initialThinCount < LOW_RESULT_THRESHOLD`, `page.tsx:611-625`). A duplicate constant of the same value exists client-side in `SearchResultsClient.tsx:204`, but it only gates the analytics tracking beacon (`search_lowresult` event), it does **not** control any retrieval behavior. Re-verified directly in V0 source (not assumed from history) — matches the historically-documented value.

## LLM rewriter

`lib/searchRewrite.ts`. Two entry points: `rewriteQuery()` (single-shot, 1-3 paraphrases, `SYSTEM_PROMPT`) is defined but **not actually called from `page.tsx`** — `page.tsx` only calls `getMultiQueryPaths()` (`page.tsx:626`), which uses `SYSTEM_PROMPT_MULTI` (an extension of `SYSTEM_PROMPT`) and returns both `rewrites` (up to 3) and a `decomposition` object (subject/style/scene/output/era/mood, each optional). Model: `gpt-4o-mini`, `temperature=0.4`, `TIMEOUT_MS=8000`, `MAX_TOKENS_MULTI=600`. On any failure (missing key, timeout, JSON parse failure, non-object response) it returns `{rewrites: [], decomposition: {}}` — a safe empty fallback, never throws.

## Rewrite Guard

**No separate "Guard" module or function exists in V0** — there is no `rejected_rewrites` counter, no post-hoc rewrite-rejection step referenced anywhere in `lib/searchRewrite.ts` or `page.tsx`. The only "guard-like" mechanisms present are: (a) the LLM's own Path A/Path B decision tree baked into the system prompt (self-censoring — the model itself returns `[]` for un-mappable queries), (b) `looksLikeGarbageQuery()` (`page.tsx:60-70`, a pre-call heuristic that skips the paid LLM call entirely for version-string/ID-shaped queries), and (c) `BOT_UA_REGEX` (`page.tsx:53`, skips the LLM call for known crawler user agents). **The `rejected_rewrites` / explicit Guard-rejection mechanism described in the historical design docs is an old-Candidate-branch concept (`lib/searchRewrite.ts` on that branch) — it does not exist in V0.** This is an important audit finding: Stage 6's "Rewrite Guard未被删除、未被默认关闭" functional-regression gate must be interpreted as "the *existing* guard mechanisms in V0 (Path A/B prompt logic + garbage/bot pre-filters) remain intact," not as "a `rejected_rewrites` counter exists" — because it never existed in V0 to begin with.

## Multi-path retrieval

`getMultiQueryPaths()` returns up to 3 rewrites + up to 6 decomposition slots → `flattenPaths()` (`lib/searchRewrite.ts:421-436`) dedupes against the original and against each other, yielding up to 9 extra paths (1 original + up to 9 = up to 10 total, matching the "up to 10 paths in practice" comment at `searchRewrite.ts:375`). Each path is independently re-scored via `scoreQueryTokens(pathTokens, false)` (`page.tsx:635`) and merged into `inspirationById` by max-score-wins with strict-promotion-wins (`page.tsx:638-647`). A **multi-hit rerank boost** (`page.tsx:654-665`) adds +8% per extra path a record was hit by, capped at +40% (5+ hits) — this is the only "cross-path agreement" signal in V0 today, and it is **purely multiplicative on top of the existing score**, with no cap on how many records can receive it and no distinction between a high-quality path and a noise path.

## Decomposition

Part of the same `getMultiQueryPaths()` call (see above) — not a separate LLM call. Each non-empty decomposition slot (subject/style/scene/output/era/mood) becomes one additional retrieval path, scored identically to a rewrite path.

## Original vs. Rewrite result merge, and the central bug mechanism

This is the most safety-critical finding of the audit. The merge/gating logic (`page.tsx:703-709`):

```
const allScored = Array.from(inspirationById.values());
const hasStrict = allScored.some((x) => x.strict);
let inspirations = allScored
  .filter((x) => (hasStrict ? x.strict : true))
  .sort((a, b) => b.score - a.score)
  .slice(0, 80)
  .map((x) => x.rec);
```

`inspirationById` is a union map: the original query's scored results are inserted first (`page.tsx:587-588`), then each rewrite/decomposition path's results are merged in by `id` (max-score-wins, `page.tsx:638-647`) — so **individual records from the original query are never deleted** by the merge step itself (Direction 2's "merge not replace, dedupe by id" is already structurally true for the union step). However, the **final `hasStrict` filter is global and binary**: if *any* record across *any* path (original or rewrite/decomposition) is `strict`, then **every non-strict record — including original-query records that were only ever `relaxed` — is filtered out of the final `inspirations` array**, regardless of whether that original relaxed content was the only relevant material and the strict hit came from an unrelated rewrite/decomposition path. This is the exact mechanism the design doc's Direction 1/2 unvariant ("`original_results` must be preserved as a floor when non-empty") is written to close. Whether it actually reproduces the specific "1-2 results → 0" collapse observed on the old Candidate branch is re-tested empirically in Stage 4 (`07_V0_TARGET_CASE_RECONFIRMATION.csv`) rather than assumed — the V0 mechanism, while structurally hazardous, is not identical to the old Candidate's `lib/searchTokens.ts`-based implementation referenced in the design doc's historical case data, so the *specific* zero-result outcome must be independently confirmed on V0, not inherited from V1 findings.

Deduplication: by stable `InspRecord.id` (a real catalog record id), confirmed via `inspirationById: Map<string, ScoredInspiration>` keyed on `.rec.id` — dedup is safe and correct today. Source-path tracking (which of original/strict/relaxed/rewrite/decomposition/multi-path a given result came from) is **not recorded anywhere** — `pathHitsById` tracks only a *count* of how many paths hit a record, not *which* paths. This is a gap relative to Direction 2's "record source paths" requirement.

## Cache / timeout

See `00_PRODUCTION_BASELINE_MANIFEST.json` `cache_configuration` — process-local in-memory Maps (256 entries / 7-day TTL) for both the rewrite cache and the template-matcher cache; 8s timeout for rewrite/multi-path, 15s for the template matcher. No Redis or persistent cache is wired up for search (the `redis` package is a dependency but unused by the search path per the design doc's own audit, not re-verified independently here as it was out of scope).

## Search result cards / click / Generate / Remix

- **Cards**: `ExampleImagesGrid` (imported `SearchResultsClient.tsx:9`), fed `gridItems` — inspirations capped at 3 per `template_id` (`SearchResultsClient.tsx:138-146`) for grid diversity, mapped with a caption-fallback chain (locale title → EN/ZH title → category → first param value → id-tail humanization).
- **Templates rail**: `NanoTemplateDetailClient` (imported `SearchResultsClient.tsx:10`), fed `matchedTemplates`.
- **Click**: handled by the shared `ExampleImagesGrid`/`NanoTemplateDetailClient` components (not re-implemented on the search page) — out of this audit's line-level scope but structurally the same click/share/remix wiring used on `/topics` and `/nano-template/[slug]`, confirmed by the comment at `SearchResultsClient.tsx:402-404` ("same UI used on /topics, /nano-template detail... Tracking, share, remix all carry over for free").
- **Generate**: `GenerableTemplatesSection.tsx` (rendered twice — empty state and populated state, `SearchResultsClient.tsx:322,421`) — a **separate feature**, not multi-path retrieval: it POSTs to `/api/search-generation-plan`, which calls `lib/searchGenerationPlan.ts`'s `buildSearchGenerationPlan()`, which in turn calls `matchTemplatesForQuery` / `rerankTemplateCandidatesForQuery` from **`lib/searchTemplateMatch.ts`** — a third, independent `gpt-4o-mini` call distinct from the rewriter. "Generate yourself" click → `runSearchGenerationBatch` (`services/searchGenerationBatch.ts`), auth/credit-gated, polls generation status.
- **Remix**: not a search-page-specific concept — surfaced via the shared card components' existing remix affordance (same code path as topic/template pages); no search-specific remix logic exists to audit separately.

## L2 hierarchical content / multi-paragraph display

**UNKNOWN — could not be mapped to any code artifact.** A full-repo grep (excluding node_modules) for "L2", "level2", "hierarchical", "multi-paragraph", "paragraph" across `app/`, `lib/`, `components/`, plus targeted full reads of `GenerableTemplatesSection.tsx`, `NanoTemplateDetailClient.tsx`, and `ExampleImagesGrid.tsx`, found no component, prop, or concept matching these names. Critically, **the source design document itself admits this is unresolved** (`EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-18_POST_MEETING_ZH.md:433,552`: "L2 具体指代的页面层级/组件，需工程阶段结合现有代码结构确认" / listed explicitly under open UNKNOWNs). Per the task's explicit instruction ("无法证明的内容标记UNKNOWN，不得猜测"), this is recorded as UNKNOWN rather than mapped to a guessed component. Plausible candidates that were considered and explicitly rejected as unconfirmed: the `TIER1/TIER2/TIER3` suggestion hierarchy in `lib/searchIndex.ts` (a data-tiering concept, not a content-display concept), and the topic-page intro paragraph in `app/[locale]/(public)/topics/[slug]/page.tsx` (unrelated to `/search`). **Functional-regression handling**: since this cannot be verified as either present or absent in a targeted way, Stage 3/11's regression baseline records this gate as UNKNOWN rather than PASS or FAIL, and V2 development does not touch any code that could plausibly be "L2 content" (no changes to `NanoTemplateDetailClient.tsx`, `ExampleImagesGrid.tsx`, `GenerableTemplatesSection.tsx`, or the topics page), so the risk of an undetected regression in whatever this term refers to is minimized by scope discipline even though it cannot be positively verified.

## Answers to the audit's required questions (summary)

| Question | Answer |
|---|---|
| Fields participating in scoring | id, template_id, tags, merged topics, search_aliases, param values, locale title/category (inspiration blob); category/title/description/content.sections.what/who (template blob). Confirmed by reading `page.tsx:517-529` and `:320-341`. |
| title/name/tags/description/category/topic participate? | Yes to all, via blob concatenation — see above. No field-level weight. |
| Per-field weights | **None.** Every field contributes equally once concatenated into one blob string. |
| exact phrase / whole token / alias / stemming / substring distinction | Not distinguished in score. ASCII tokens get word-boundary matching (whole-token); CJK tokens match by raw substring (no word boundaries in Chinese). Aliases are blob text, no separate tier. Stemming is a single conservative English suffix rule, pre-tokenization. |
| Strict vs Relaxed merge | Binary global gate: `hasStrict` (any path) ⇒ relaxed-only records from ANY path (including the original query) are dropped entirely from the final result set. |
| Does Rewrite replace original results? | Not via deletion (union map preserves original ids) — but effectively yes via the `hasStrict` filter described above, which can silently drop all-relaxed original records once *any* path anywhere produces a strict hit. |
| How are multiple Rewrite paths merged? | Union by record id, max-score-wins + strict-promotion-wins, plus a multiplicative multi-hit boost (+8%/hit, capped +40%). No per-path quality distinction, no per-path candidate cap, no template-family saturation control. |
