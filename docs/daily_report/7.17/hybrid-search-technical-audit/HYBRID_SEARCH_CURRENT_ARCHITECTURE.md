# Hybrid Search — Current Architecture Audit

Repository: `/Users/baobaoli/Desktop/curify-frontend-hybrid-audit` (shallow clone, isolated read-only research checkout)
Remote: `https://github.com/super-inbox/curify-frontend.git`
Branch: `main` · Commit: `5a59c4beba7856136396d8d0d249d5355c85322f` ("Merge pull request #530 from super-inbox/jwang/vercel")
Working tree: clean, unmodified throughout this audit
Framework: Next.js 15.3.6 (App Router, React 19), TypeScript, deployed on Vercel
Audit date: 2026-07-17

This document is Deliverable 1 of 18. It is a **read-only technical audit** — no source file was modified, no dependency installed, no external API called. Facts below are cited to exact file/line locations found on the commit above; interpretive statements are explicitly marked as recommendation/assumption, not fact.

---

## 1. Executive Framing

The manager's requirement ("run LLM Rewriter and Google Image Search in parallel when results are thin, merge while preserving external links") is **not a new idea for this codebase** — it is already drafted, in detail, as **"Extension C — Hybrid Google results"** inside `docs/eval-framework-visual-search-benchmark-2026-06-14.md` (lines 220-260, filed 2026-06-27, owner Baobao). That doc already specifies:
- trigger = `LOW_RESULT_THRESHOLD=5` gate (the same constant the current LLM rewriter uses)
- source = Google Custom Search API (Image search)
- placement = a labeled rail *below* Curify results ("Inspiration from elsewhere")
- caching = 7-day key by (query, locale)
- no image proxying — hotlink + show source domain (copyright mitigation)
- CTA: "Make with Curify" routes the click back into Curify's generation flow
- tracking: new `nano_external_inspiration_click` event, `content_id = "google:<url-hash>"`
- kill condition: if `external_click → curify_create` conversion < 8%, kill the rail
- scheduled for "B-Phase 4," weeks 7-8 of an 8-week plan, explicitly **not P0**, "post-WC"

**This existing doc is a design proposal, not shipped code.** Section 10 of the code-entrypoint inventory confirms zero implementation footprint: no Google Custom Search client, no external-image types, no external-result UI component, and the `nano_external_inspiration_click` event does not exist in `services/useTracking.ts`'s `ActionType` enum. Treat Extension C as valuable prior art to build on, not as evidence the feature is ready — this audit's job is to independently re-derive a testable plan per the Session-3 brief, using Extension C as a cross-check rather than an authority.

A second, unrelated proposal doc uses the word "hybrid" for a different concept — flag this naming collision explicitly (see §4).

---

## 2. What Exists Today (Verified)

### 2.1 Internal search is a static, in-process linear scan — no DB, no index service
There is no database and no external search-index (Elasticsearch/Algolia/Typesense/pgvector — none found in a full-repo dependency and code grep). `/search` runs entirely inside a **Next.js Server Component** (`app/[locale]/(public)/search/page.tsx`) that:
1. Statically imports `public/data/nano_inspiration.json` and `public/data/nano_templates.json` at module load.
2. Builds per-request search "blobs" (id + tags + topics + params + i18n title/category + hidden `search_aliases`).
3. Tokenizes the query (`buildSearchTokens`, page.tsx:137) with whitespace/punctuation splitting, English plural stemming, CJK bigram fallback, and a stopword list.
4. Scores every inspiration record with a linear `for` loop (`scoreQueryTokens`, page.tsx:470-578) — strict (all tokens present) vs. relaxed (partial) two-tier gate, strict wins if any exist (precision-first).

This is a synchronous, server-side, pre-render computation — the user never sees a loading state for the *first* pass.

### 2.2 An LLM query-rewrite system is already shipped in production
`lib/searchRewrite.ts` — `getMultiQueryPaths(query)` calls OpenAI `gpt-4o-mini` (`OPENAI_API_KEY` env var), returns up to 3 paraphrase rewrites **plus** a 6-slot query decomposition (subject/style/scene/output/era/mood), for up to 10 total retrieval paths. It is gated by:
```
if (initialThinCount < LOW_RESULT_THRESHOLD && query.length >= 2 && !isBot && !isGarbage)
```
(`page.tsx:620-625`, `LOW_RESULT_THRESHOLD = 5`, `page.tsx:47`). It fails safe — any error, timeout (8s), missing key, or malformed JSON returns `[]`/`{rewrites:[],decomposition:{}}` and the original empty/thin-result experience is preserved. It has a 256-entry, 7-day, process-local (non-shared, non-persistent across Vercel serverless invocations) LRU cache.

This is the natural analog for how a hybrid design should treat the *external* call: same fail-safe posture, same trigger gate, same cache philosophy — but a shared/persistent cache (Redis) is recommended for the external leg since it is billed per-call (§ Provider options doc) whereas the LLM leg's caching is best-effort only.

### 2.3 Zero/low-result branching already exists and is precisely where a hybrid trigger should hook
- Server-side thinness signal: `initialThinCount` (page.tsx:611-613), computed **before** any rewrite runs.
- Client-side result count: `totalResults = gridItems.length + matchedTemplates.length + galleryPrompts.length` (`SearchResultsClient.tsx:194-196`).
- Duplicated threshold constant `LOW_RESULT_THRESHOLD = 5` exists independently in both page.tsx:47 and SearchResultsClient.tsx:204 — a maintenance smell to flag, not fix, in this audit (not shared from one source of truth).
- Zero-result UI branch: `SearchResultsClient.tsx:319-329`, `!hasResults` → renders `TopicStrip` ("Try browsing a topic instead"). **This exact branch is the current empty-state and the natural mount point for a labeled external-results rail** — it already knows it has nothing else to show.
- Existing tracking events already distinguish `search_noresult` / `search_lowresult`, and already append `|rw=1` (rewrite fired) / `|paths=N` (path count) suffixes to a single `content_id` string (`SearchResultsClient.tsx:243-263`) — direct precedent for a future `|hybrid=1` suffix, discussed in the instrumentation plan (Deliverable 12).

### 2.4 No merge/dedup/ranking logic exists across *different sources* today
The only existing "merge" is a same-source union: multiple LLM-rewrite retrieval paths are merged by record id, keeping max score, with a `+8%`-per-extra-path-hit boost capped at `+40%` (page.tsx:654-665). This operates entirely within `nano_inspiration.json` — there is no code anywhere that merges two structurally different result sets (e.g., internal + external). **This is a genuine build-from-scratch gap**, not a refactor of something existing.

### 2.5 No external-image or Google Search integration exists
Full-repo grep for `customsearch`, `serpapi`, `SERP_API`, `GOOGLE_CSE`, `cse.google` → zero code hits. `@google/genai` (package.json) is a real dependency but is used exclusively for **image generation** (`app/api/illustrator-demo/generate/route.ts`, `app/api/progseo-demo/generate/route.ts`), not search or grounding. No `.env.example` exists in the repo to reserve a naming convention for a future Google Search key.

### 2.6 No unified result data contract exists
Three structurally different, independently-typed arrays are rendered as separate page sections: inline `InspRecord` (page.tsx), `NanoInspirationCardType` (`lib/nano_pure.ts:115-135`), and `TemplateMatch` (`lib/searchTemplateMatch.ts:113-124`), plus a fourth gallery type `NanoPromptBase`. None has a `source`, `destination_url`, or `score` field usable for cross-source ranking. See Deliverable 4 for the full field inventory.

### 2.7 No `search_id` exists anywhere in the codebase
Full-repo grep for `search_id`/`searchId` returns zero hits. The tracking system (`services/useTracking.ts`) has `session_id` (per-browser-tab, sessionStorage) and `user_id`, but no per-search-request identifier. Search-result clicks are not currently attributable to the specific search request that produced them except by joining on `(session_id, query-string, rough-timestamp)` — a fragile, lossy join. This is the single most important instrumentation gap for the manager's "did users click and generate" question — see Deliverable 12.

### 2.8 Generation IS already tracked, just disconnected from search
`ActionType` includes `"generate"` (`services/useTracking.ts:31`), fired via `trackAction(tracking, "generate")` at multiple destination-page sites: `app/[locale]/_components/ReproduceWorkbench.tsx:233`, `app/[locale]/(public)/nano-template/[slug]/example/[exampleId]/ExampleGeneratePanel.tsx:86,108`, `ExampleRightColumn.tsx:137,323`, `UnifiedActionBar.tsx:125`. These all fire on the **destination** `/nano-template/[slug]#reproduce` (or example/tool) page — none of them currently carry a `search_id` or any breadcrumb back to the search request that led there. The manager's "search → click → generate" question is answerable today only by a lossy heuristic join, not a real join key.

---

## 3. Framework / Runtime Facts

- Next.js 15.3.6, App Router, React 19, TypeScript strict-ish (`tsconfig.json`).
- Rendering: `/search` is a Server Component (async, does all retrieval + LLM-rewrite server-side before HTML is sent); `SearchResultsClient.tsx` is a client component that only renders and tracks.
- No dedicated backend search service is called for free-text search. A real backend (`services/api.ts` `apiClient`, `API_BASE`) is called only for exact-tag gallery-prompt lookups (`nanoPromptsService.getNanoPromptsByTag`, page.tsx:823-842) and for the tracking beacon (`/interactions/track`).
- OpenAI SDK (`openai` npm package, v6.33.0) is a first-class dependency already used server-side with a real production API key convention (`OPENAI_API_KEY`).
- Deployment target: Vercel (serverless functions — relevant to caching design, since in-process caches do not persist or share across invocations).

---

## 4. Naming Collision — Two Different "Hybrid" Concepts

`docs/eval-framework-visual-intent-routing-2026-06-15.md` (the "VIR" doc, Rong's track) also uses "hybrid" — but for combining *internal* retrieval paradigms (keyword + embedding + LLM-routing) with a reranker ("Phase 4 — Hybrid (E) + meta-routing"). This is **not** the manager's "Curify + Google Images" hybrid. **Do not conflate the two in implementation planning or in stakeholder communication** — recommend the manager's feature be internally named something unambiguous, e.g. "External Fallback" or "Hybrid Google Rail," to avoid cross-talk with the VIR workstream.

---

## 5. Summary Table — Answers to Primary Questions 1-14

| # | Question | Answer (file:line) | Confidence |
|---|---|---|---|
| 1 | Query entry point | `app/[locale]/(public)/search/page.tsx:237` (`SearchPage`, reads `searchParams.q`); also `app/[locale]/_components/SearchBar.tsx` (global autocomplete input, routes to `/search?q=`) | High |
| 2 | Normalization/tokenization | `lib/query_normalize.ts:51` (`normalizeSearchQuery`, deterministic pre-pass) and `page.tsx:133-188` (`normalizeForSearch`, `buildSearchTokens` — the real matching-time tokenizer) | High |
| 3 | Internal search execution | In-process linear scan, `page.tsx:503` (`for (const r of nanoInspiration...)`) inside `scoreQueryTokens` (`page.tsx:470-578`) — no DB/index service | High |
| 4 | Result count | Server: `initialThinCount` (`page.tsx:611-613`); Client: `totalResults` (`SearchResultsClient.tsx:194-196`) | High |
| 5 | Zero/low-result logic | `LOW_RESULT_THRESHOLD=5` gates in both `page.tsx:47/620` and `SearchResultsClient.tsx:204/249-263`; UI branch `SearchResultsClient.tsx:319-329` | High |
| 6 | LLM rewrite trigger | `page.tsx:620-625` `if (initialThinCount < LOW_RESULT_THRESHOLD && ...)` → `getMultiQueryPaths` | High |
| 7 | Rewritten query searched | Same in-process scorer re-invoked per path: `page.tsx:629-648`, `scoreQueryTokens(pathTokens, false)` | High |
| 8 | First/second pass merge | `inspirationById` Map keeps max score per record id across all paths, `page.tsx:587-651` | High |
| 9 | Dedup/ranking | Dedup by `rec.id` (Map key); ranking = raw token-hit score × multi-path-hit boost (+8%/hit, cap +40%), `page.tsx:654-665,703-709` | High |
| 10 | Internal result data contract | Three parallel types, no unified shape — see Deliverable 4 | High |
| 11 | UI result card components | `ExampleImagesGrid.tsx` (examples), `NanoTemplateDetailClient.tsx` (template rail), `PromptCard.tsx` (gallery), `GenerableTemplatesSection.tsx`/`GenerableCard` (LLM-matched generate bridge) | High |
| 12 | Actions on internal results | Click-through (carousel/detail), "Remix" → `/nano-template/[slug]?params#reproduce`, Share, "Download pack" (batch templates), "Copy prompt" (gallery) | High |
| 13 | Safe external insertion point | `SearchResultsClient.tsx:319-329` zero-result branch (extend to also render when `totalResults` is low, not just zero) — see Deliverable 3 for full call graph reasoning | Recommendation |
| 14 | External vs internal result differentiation | No existing card can represent a non-CDN image + non-Curify destination URL; a **new, separate card type** is safer than reusing internal cards — see Deliverable 4 | Recommendation, evidence-backed |

Questions 15-18 (five experimental modes, MVP design, instrumentation fields, CTR-vs-generation risk) are answered in Deliverables 7-11, 14.

---

## 6. Directory Inventory (search-relevant)

See Deliverable 2 (CSV) for the full entrypoint table. High-level tree:

```
app/[locale]/(public)/search/page.tsx                  # RSC: retrieval, scoring, LLM-rewrite orchestration
app/[locale]/(public)/search/SearchResultsClient.tsx    # client: render + tracking + zero-result branch
app/[locale]/(public)/search/GenerableTemplatesSection.tsx  # client: lazy LLM template-match bridge
app/[locale]/_components/SearchBar.tsx                  # global autocomplete input
app/[locale]/_components/TopicStrip.tsx                 # empty-state fallback chips
app/api/search-template-match/route.ts                  # POST: LLM generation-bridge matcher

lib/searchRewrite.ts             # OpenAI query rewrite + multi-query decomposition (SHIPPED)
lib/searchTemplateMatch.ts       # OpenAI query→generatable-template matcher (SHIPPED, separate feature)
lib/query_normalize.ts           # deterministic normalize + tiny alias table
lib/searchIndex.ts               # static suggestion/autocomplete index
lib/search_business_override.ts  # deterministic no-LLM override table
lib/template_concept_expansion.ts, taxonomy.json, intent_taxonomy.ts, zh_normalize.ts

services/useTracking.ts          # ContentType/ActionType enums, track()/trackAction()/trackOnUnload()
services/api.ts                  # apiClient — backend HTTP wrapper (used by tracking + gallery lookups)

types/nanoPrompts.ts             # NanoPromptBase (gallery contract)
public/data/nano_inspiration.json, nano_templates.json   # the "database" search scores against

docs/search-quality.md, search-retrieval-improvement-plan-2026-06-25.md,
docs/eval-framework-visual-search-benchmark-2026-06-14.md   # ← Extension C, the existing hybrid-Google proposal
docs/eval-framework-visual-intent-routing-2026-06-15.md     # ← sister doc, DIFFERENT "hybrid" meaning
```

---

## 7. Limitations of This Section

- `lib/nano_page_data.ts` `buildNanoFeedCards` / `lib/nano_utils.ts` `nanoRegistry` internals were confirmed used but not read line-by-line — flagged UNKNOWN for exact ranking internals of the template rail.
- `scripts/eval_search.cjs` / `scripts/configs/search_eval_set.json` (the existing offline eval harness) were referenced via docs but not opened in full this pass.
- Whether `OPENAI_API_KEY` (or any future Google Search key) is actually set in the deployed Vercel environment cannot be verified from a local shallow clone — and per the safety constraints, no `.env*` file was opened or would have been opened even if present (none exist locally).
