# Hybrid Search — Current End-to-End Call Graph

Evidence-based. UNKNOWN marks anything not directly confirmed in code. This graph is the union of (a) what exists today and (b) annotated insertion points for the future hybrid feature — the two are visually distinguished.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ USER TYPES QUERY                                                        │
│   Entry A: app/[locale]/_components/SearchBar.tsx (client, global header)│
│   Entry B: direct nav to /search?q=... (any link, bookmark, SEO)        │
└───────────────────────────────┬───────────────────────────────────────┘
                                 │  router.push(`/${locale}/search?q=`) or full nav
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ app/[locale]/(public)/search/page.tsx :: SearchPage() [SERVER, async]   │
│   Input: searchParams {q, within, intent}, params {locale}              │
│   EXISTS: yes · SYNC/ASYNC: async (awaits searchParams, headers(), and  │
│   conditionally the OpenAI call) · SIDE: server (RSC, pre-render)       │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ QUERY NORMALIZATION                                                     │
│   lib/query_normalize.ts :: normalizeSearchQuery(q)   [deterministic]   │
│   page.tsx:133 :: normalizeForSearch(s)  [lowercase + zh TS→SC + ×→x]  │
│   EXISTS: yes · SYNC · SERVER                                           │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ TOKENIZATION / ALIAS EXPANSION                                          │
│   page.tsx:137 :: buildSearchTokens(query) → {primary[], bigrams[]}    │
│   lib/template_concept_expansion.ts :: CONCEPT_SYNONYMS (secondary pass)│
│   lib/search_business_override.ts :: getBusinessOverride (deterministic)│
│   EXISTS: yes · SYNC · SERVER                                           │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ FIRST INTERNAL RETRIEVAL (pass 1, original query)                       │
│   page.tsx:470 :: scoreQueryTokens(tokens, promoteAllUnderStrictTpl=true)│
│   Linear scan over nanoInspiration (public/data/nano_inspiration.json)  │
│   Output: baseResult = {scored: ScoredInspiration[], strictTpl, tplByI18n}│
│   EXISTS: yes · SYNC · SERVER (in-process, no network/DB call)          │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ RESULT COUNT                                                            │
│   page.tsx:611 :: initialThinCount =                                    │
│     baseResult.scored.filter(strict).length + matchedTemplateIdsByI18n.size│
│   EXISTS: yes · SYNC · SERVER                                           │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ZERO/LOW-RESULT DECISION                                                │
│   page.tsx:47  LOW_RESULT_THRESHOLD = 5                                 │
│   page.tsx:617-625: isBot (UA regex) / isGarbage (heuristic) checks      │
│   if (initialThinCount < 5 && query.length>=2 && !isBot && !isGarbage)  │
│   EXISTS: yes · SYNC · SERVER                                           │
│                                                                          │
│   ★ HYBRID INSERTION POINT #1 ★                                         │
│   This same boolean gate is the natural trigger for the external call.  │
│   Today it ONLY gates the LLM rewrite. A hybrid design would branch     │
│   from here into BOTH the LLM rewrite AND the external image call,      │
│   run in parallel (Promise.allSettled), per the manager's requirement.  │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ LLM REWRITE (existing, shipped)                                         │
│   page.tsx:626 :: await getMultiQueryPaths(query)                       │
│     → lib/searchRewrite.ts :: getMultiQueryPaths()                      │
│       - OpenAI gpt-4o-mini, temp 0.4, 8s timeout, response_format=json  │
│       - process-local LRU cache, 256 entries, 7-day TTL                 │
│       - fails safe to {rewrites:[],decomposition:{}} on ANY error       │
│   Output: MultiQueryPaths {rewrites[], decomposition{}}                 │
│   EXISTS: yes · ASYNC (awaited) · SERVER                                │
│                                                                          │
│   ★ HYBRID INSERTION POINT #2 (parallel branch, NOT YET BUILT) ★        │
│   EXTERNAL IMAGE SEARCH — would run here, in parallel with the above,   │
│   using either the original query or (per Extension C) the LLM-rewritten│
│   query. UNKNOWN/NOT BUILT: no external provider client exists.         │
│   Recommended shape: Promise.allSettled([getMultiQueryPaths(query),     │
│     externalImageSearch(query)]) so a slow/failed external call never   │
│   blocks or breaks the LLM path, and vice versa.                        │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ SECOND INTERNAL RETRIEVAL (pass 2+, one per rewrite/decomposition path)│
│   page.tsx:629-648 :: for (path of extraPaths):                         │
│     scoreQueryTokens(buildSearchTokens(path), promoteAllUnderStrictTpl=false)│
│   EXISTS: yes · SYNC (loop) · SERVER — up to 9 additional passes        │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ MERGE (internal-only, same-source)                                      │
│   page.tsx:587-651 :: inspirationById Map<id, ScoredInspiration>         │
│     - keeps max score per record id across all internal passes          │
│     - promotes strict if ANY pass saw it strict                         │
│     - pathHitsById tracks how many paths hit each record                │
│   EXISTS: yes · SYNC · SERVER                                           │
│                                                                          │
│   ★ HYBRID INSERTION POINT #3 (NOT YET BUILT) ★                         │
│   CROSS-SOURCE MERGE — where internal results (from the map above) and  │
│   external results (from insertion point #2) would be combined into a   │
│   single ordered output structure. NO code today merges two different-  │
│   source result sets. See Deliverable 9 (Merge & Ranking Spec) for the  │
│   full policy design.                                                   │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ DEDUP AND RANKING (internal-only)                                       │
│   page.tsx:654-665 :: multi-hit boost, +8%/extra path hit, cap +40%     │
│   page.tsx:703-709 :: hasStrict gate — if any strict match exists,      │
│     relaxed matches are dropped entirely (precision-first, all-or-none) │
│   page.tsx:705-708 :: sort by score desc, slice(0,80)                   │
│   EXISTS: yes · SYNC · SERVER                                           │
│                                                                          │
│   Cross-source dedup (internal vs external) does NOT exist — would be   │
│   new, keyed on destination URL / image URL / title+domain (see         │
│   Deliverable 9).                                                       │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ SERIALIZATION — props passed from Server to Client Component            │
│   page.tsx renders <SearchResultsClient inspirations={...}              │
│     matchedTemplates={...} galleryPrompts={...} usedRewrites={...}      │
│     pathsUsed={...} relatedTopics={...} .../>                           │
│   EXISTS: yes · SERVER→CLIENT boundary (RSC prop serialization)         │
│                                                                          │
│   Hybrid would add: externalResults={...} externalTriggered={boolean}   │
│   externalProvider={string} as new serialized props (NOT YET BUILT).    │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ UI CARD RENDERING [CLIENT]                                              │
│   app/[locale]/(public)/search/SearchResultsClient.tsx:99               │
│   totalResults computed (line 194); hasResults = totalResults>0         │
│   if (!hasResults): render TopicStrip empty-state (lines 319-329)       │
│   else: render ExampleImagesGrid, NanoTemplateDetailClient (templates), │
│     PromptCard (gallery), GenerableTemplatesSection (lazy LLM matches)  │
│   EXISTS: yes · SYNC render · CLIENT                                    │
│                                                                          │
│   ★ HYBRID INSERTION POINT #4 (PRIMARY, NOT YET BUILT) ★                │
│   A new "Inspiration from elsewhere" rail would render here — either    │
│   replacing the TopicStrip-only zero-result branch, or as an ADDITIONAL │
│   section appended after existing internal sections when results are   │
│   low-but-nonzero. Needs a new card component (not a reuse of          │
│   ExampleImageCard/PromptCard — see Deliverable 4/5).                   │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ RESULT CLICK [CLIENT]                                                   │
│   Internal: useClickTracking() → trackAction(target,"click")            │
│     (services/useTracking.ts:227-237)                                   │
│   External: NOT YET BUILT — no external_click actionType exists in the  │
│     ActionType union (services/useTracking.ts:25-38). Extension C       │
│     proposes `nano_external_inspiration_click` as a NEW event name —    │
│     not implemented.                                                    │
│   EXISTS (internal): yes · ASYNC (fire-and-forget POST) · CLIENT        │
└───────────────────────────────┬───────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ EDIT / USE / GENERATE ACTION [CLIENT, on a DIFFERENT destination page]  │
│   Click on internal card → navigates to                                 │
│     /${locale}/nano-template/${slug}?params#reproduce                   │
│   Destination page fires actionType="generate" via:                     │
│     app/[locale]/_components/ReproduceWorkbench.tsx:233                 │
│     app/[locale]/(public)/nano-template/[slug]/example/[exampleId]/     │
│       ExampleGeneratePanel.tsx:86,108 ; ExampleRightColumn.tsx:137,323  │
│   EXISTS: yes · ASYNC · CLIENT                                          │
│                                                                          │
│   ★ CRITICAL GAP ★ None of these generate-tracking call sites carry a   │
│   search_id or any linkage back to the search request that produced the │
│   click. "search_id" does not exist anywhere in the codebase (confirmed │
│   by full-repo grep). Search→Click→Generate attribution is therefore    │
│   NOT currently possible as a clean join — only a lossy               │
│   (session_id, query-string, rough-timestamp) heuristic join. See       │
│   Deliverable 12 for the required fix.                                  │
│   External results: no "generate" or "click-out-then-generate" path     │
│   exists at all — would need Extension C's "Make with Curify" CTA       │
│   design (routes the external click through query-derived retrieval     │
│   into the same reproduce destination) to close this loop.              │
└─────────────────────────────────────────────────────────────────────────┘
```

## Step-by-step table (compact form)

| Step | File:Function | In | Out | Exists | Sync/Async | Side | Hybrid insertion point |
|---|---|---|---|---|---|---|---|
| Entry | SearchBar.tsx / direct nav | keystrokes/URL | navigation to /search?q= | Yes | sync UI | client | No |
| Route entry | page.tsx:237 SearchPage | searchParams | orchestrates all below | Yes | async | server | No |
| Normalize | query_normalize.ts:51, page.tsx:133 | raw q | normalized string | Yes | sync | server | No |
| Tokenize | page.tsx:137 buildSearchTokens | query | {primary,bigrams} | Yes | sync | server | No |
| Retrieval pass 1 | page.tsx:470 scoreQueryTokens | tokens | scored records | Yes | sync | server | No |
| Result count | page.tsx:611 initialThinCount | scored | number | Yes | sync | server | No |
| Low-result gate | page.tsx:620-625 | count, UA | boolean | Yes | sync | server | **#1 — branch point for parallel external call** |
| LLM rewrite | searchRewrite.ts:438 getMultiQueryPaths | query | rewrites+decomposition | Yes | async (awaited) | server | **#2 — parallel sibling for external call** |
| External image search | *(none)* | query/rewritten query | *(none)* | **NOT BUILT** | would be async | server | **#2 (twin of LLM call)** |
| Retrieval pass 2+ | page.tsx:629-648 | each path | scored records | Yes | sync loop | server | No |
| Internal merge | page.tsx:587-651 inspirationById | multi-pass results | merged map | Yes | sync | server | No |
| Cross-source merge | *(none)* | internal+external | *(none)* | **NOT BUILT** | — | server | **#3 — core new logic** |
| Dedup/rank | page.tsx:654-709 | merged map | sorted array | Yes (internal only) | sync | server | Extend for cross-source dedup |
| Serialize props | page.tsx JSX return | server data | client props | Yes | sync | server→client | Extend with externalResults prop |
| UI render | SearchResultsClient.tsx:99+ | props | DOM | Yes | sync render | client | **#4 — new rail component** |
| Result click | useClickTracking (useTracking.ts:227) | click event | POST /interactions/track | Yes (internal) | async | client | Add external_click actionType |
| Generate action | ReproduceWorkbench.tsx:233 etc. | click event | POST /interactions/track | Yes | async | client | Add search_id linkage (critical gap) |

## Explicit UNKNOWNs in this call graph

- Exact behavior of `lib/nano_page_data.ts buildNanoFeedCards` internals feeding the template rail — not read line-by-line.
- Whether any client-side re-fetch/hydration path exists beyond `GenerableTemplatesSection`'s lazy `/api/search-template-match` call — UNKNOWN if there are others.
- Whether Vercel Edge vs Node runtime is used for `/search` itself (the RSC) — `app/api/search-template-match/route.ts` explicitly declares Node runtime + force-dynamic; the `/search` page route config was not directly inspected for a `runtime` export.
