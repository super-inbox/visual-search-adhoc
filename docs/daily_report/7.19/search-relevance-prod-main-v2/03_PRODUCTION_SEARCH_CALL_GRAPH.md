# Stage 2: Production (V0) Search Call Graph

Date: 2026-07-19. All paths relative to `/Users/baobaoli/Desktop/curify-frontend-v0-baseline-2026-07-19`.

```
GET /[locale]/search?q=...&within=...&intent=...
  └─ app/[locale]/(public)/search/page.tsx  (SearchPage, Server Component)
       ├─ normalizeSearchQuery(q)                          lib/query_normalize.ts
       ├─ matchBareWcCountryQuery / matchWcCountryQuery     lib/wcCountryRouting.ts   ─┐ (may redirect to /topics/<c>-world-cup)
       ├─ buildSearchTokens(query)                          inline page.tsx:137-188
       ├─ topic-slug exact/substring redirect check         ALL_SUGGESTIONS            lib/searchIndex.ts
       │                                                    (may redirect to /topics/<slug>)
       ├─ templateSearchBlob build (per-locale i18n scan)    messages/<locale>/nano.json
       │                                                    + buildTemplateTopicsMap    lib/topic_resolver.ts
       ├─ scoreQueryTokens(tokens, promoteAllUnderStrictTpl=true)   [ORIGINAL PASS]
       │     reads: nanoInspiration (public/data/nano_inspiration.json), templateSearchBlob
       │     └─ resolveTopics()                             lib/topic_resolver.ts
       │  → baseResult.scored, strictTpl, tplByI18n  ──────────────► inspirationById (seed)
       │
       ├─ initialThinCount = strict-count + i18n-template-count
       ├─ IF initialThinCount < LOW_RESULT_THRESHOLD(5)
       │    AND query.length>=2 AND !isBot AND !isGarbage:
       │      └─ getMultiQueryPaths(query)                   lib/searchRewrite.ts
       │           └─ OpenAI chat.completions (gpt-4o-mini, SYSTEM_PROMPT_MULTI)
       │           → { rewrites: string[0-3], decomposition: {subject,style,scene,output,era,mood} }
       │      └─ flattenPaths() → up to 9 extra path strings
       │      └─ FOR EACH path: buildSearchTokens(path) → scoreQueryTokens(pathTokens, false)  [REWRITE/DECOMP PASS]
       │           → merged into inspirationById (max-score-wins, strict-promotion-wins)
       │           → pathHitsById incremented (drives multi-hit boost)
       │
       ├─ multi-hit rerank boost (×1.08 per extra path hit, capped ×1.40)
       ├─ concept-expansion secondary pass (template rail only)   lib/template_concept_expansion.ts
       │      CONCEPT_SYNONYMS, only fires if matched template count < 10
       │
       ├─ FINAL GATE: hasStrict = any(x.strict for x in inspirationById.values())
       │      inspirations = filter(hasStrict ? x.strict : true) → sort by score desc → slice(0,80)
       │
       ├─ [optional] effectiveWithin filter (chip-narrow, ?within=)
       ├─ [optional] intentSlug filter (?intent=)                  lib/intent_taxonomy.ts, lib/intent_clusters.ts
       ├─ relatedTopics build (Tier-2/3 topic frequency over matchedTemplateIds)
       ├─ matchedTemplates rail build                              buildNanoFeedCards  lib/nano_page_data.ts
       ├─ galleryPrompts fetch (only if query or a rewrite is an exact known nano-prompt tag)
       │      nanoPromptsService.getNanoPromptsByTag()              services/nanoPrompts.ts (Redis-backed)
       ├─ intentChips build (topic co-occurrence over top-20 inspirations)
       │      calculateTopicCooccurrence()                         lib/topic_cooccurrence.ts
       │      rankIntentClusters() / topIntentChipsFromTopicCounts() lib/intent_clusters.ts
       │      getBusinessOverride() / applyBusinessOverride()       lib/search_business_override.ts
       │
       └─ render <SearchResultsClient inspirations, matchedTemplates, galleryPrompts,
                    usedRewrites, pathsUsed, intentChips, ... />

app/[locale]/(public)/search/SearchResultsClient.tsx  (Client Component)
  ├─ gridItems = inspirations, capped 3/template_id                 → <ExampleImagesGrid>
  ├─ rewrite hint banner (shown iff usedRewrites.length>0 && hasResults)
  ├─ intent chip row / within-narrow pill
  ├─ <GenerableTemplatesSection query locale>                       ["Generate" — SEPARATE from retrieval]
  │     └─ POST /api/search-generation-plan
  │           └─ buildSearchGenerationPlan()                        lib/searchGenerationPlan.ts
  │                ├─ getBenchmarkGenerationPlan() (hardcoded, checked first)
  │                ├─ matchTemplatesForQuery()                      lib/searchTemplateMatch.ts
  │                │     └─ OpenAI chat.completions (gpt-4o-mini, independent SYSTEM_PROMPT)
  │                └─ rerankTemplateCandidatesForQuery()             lib/searchTemplateMatch.ts (targeted rerank pass)
  │     └─ on "Generate yourself" click: runSearchGenerationBatch()  services/searchGenerationBatch.ts
  │           (auth/credit-gated; polls generation status; links to /nano-template/<slug>#reproduce)
  ├─ <NanoTemplateDetailClient otherNanoCards=matchedTemplates>      [Templates rail]
  ├─ PromptCard × galleryPrompts                                    [Gallery Prompts section]
  ├─ useTracking().track(...)                                       search / search_noresult / search_lowresult events
  └─ <TopicStrip> (empty-state + bottom "Browse" strip)              relatedTopics
```

## Independent LLM call sites (3 total, all `gpt-4o-mini`, all independently cached/timed-out)

1. `getMultiQueryPaths()` (`lib/searchRewrite.ts`) — the rewriter + decomposer. Triggered server-side, only when thin. 8s timeout.
2. `matchTemplatesForQuery()` (`lib/searchTemplateMatch.ts`) — the "Generate" matcher, global pass. Triggered client-side via `GenerableTemplatesSection` on every search page load (not gated by result thinness). 15s timeout.
3. `rerankTemplateCandidatesForQuery()` (`lib/searchTemplateMatch.ts`) — the "Generate" matcher, targeted rerank pass over the union of candidates. Same file, called from `lib/searchGenerationPlan.ts`.

`rewriteQuery()` (single-shot variant, also in `lib/searchRewrite.ts`) is defined but has **no call site** in the audited code — dead code from the retrieval path's perspective (kept, presumably, for another consumer not covered by this audit's scope, or a leftover from before `getMultiQueryPaths` superseded it).

## Data dependencies (static, build-time)

- `public/data/nano_inspiration.json` (3,403 records, 5,015,679 bytes)
- `public/data/nano_templates.json` (335 records, 1,104,275 bytes)
- `messages/{locale}/nano.json` (per-locale i18n template blob source, scanned for `[locale, "en", "zh"]`)
- `lib/taxonomy.json`, `lib/generated/nanobanana_prompts_metadata.json` (suggestion-index sources, `lib/searchIndex.ts`)
- `scripts/configs/template_capability_kb.json` (Generate-matcher evidence enrichment, `lib/searchTemplateMatch.ts`)

No database query occurs anywhere in the `/search` request path — everything is either in-process JSON or a cached OpenAI call. (Redis is used only for `nanoPromptsService.getNanoPromptsByTag()`, i.e. the Gallery Prompts section, not for inspiration/template retrieval.)
