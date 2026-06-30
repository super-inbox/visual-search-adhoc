# Curify Search Architecture Review — P0.5 Gap Analysis
**Date:** 2026-06-30  
**Branch:** `baobao/multi-intent-topic-cooccurrence`  
**Author:** Baobao  
**Supporting evidence:** `../p0-p1-gap-retest-2026-06-30/report.md` (PASS=101, WARN=24, FAIL=0 on 125-query eval set)

---

## 1. Architecture Overview

Curify's search pipeline is a **multi-surface, server-rendered retrieval system** backed entirely by static JSON catalogs. There are **no database queries at search time** — all recall is derived from blobs built from `public/data/nano_inspiration.json` (3,071 records) and `public/data/nano_templates.json` (287 templates, 227 generatable).

The system has four independently-operating result sections:

| Section | Source | Matching | Gating |
|---------|--------|----------|--------|
| **Inspirations grid** | `nano_inspiration.json` | Server-side blob+token scoring | Strict-AND or relaxed-OR |
| **Template rail** | `nano_templates.json` + i18n | Server-side strict-AND on i18n blob | Strict-AND only (relaxed unused) |
| **Generable templates** | `nano_templates.json` + GPT-4o-mini | LLM (client-side fetch post-mount) | Confidence ≥ 0.4 |
| **Gallery prompts** | Redis (nano-banana tags) | Exact tag match only | Query must exactly equal a known tag |

---

## 2. Current Search Flow — Step by Step

```
User types query
       │
       ▼
[1] WC Country Bypass
    matchBareWcCountryQuery() / matchWcCountryQuery()
    → If bare country name or "X world cup": redirect to /topics/<country>-world-cup
       │ (no match)
       ▼
[2] Topic-Match Redirect
    ALL_SUGGESTIONS.find() — slug/label/alias/localized exact match
    → Single unambiguous substring match also triggers redirect
    → shouldSkipTopicRedirect() — Business Override suppresses redirect
    → searchFallback entries stay on search page
       │ (no match, or override/searchFallback)
       ▼
[3] Query Normalization + Tokenization
    normalizeSearchQuery(): trim/lowercase/smart-quote/alias table (2 entries)
    buildSearchTokens(): split on whitespace+punctuation, filter STOPWORDS,
      single-token plural stemming (–s/–es/–ies), CJK bigram generation
       │
       ▼
[4] Template i18n Blob Build (per request)
    Load messages/<locale>/nano.json + en/nano.json + zh/nano.json
    Concatenate: category + title + description + what + who + topic slugs
    → Map<template_id, blob>
       │
       ▼
[5] Template Scoring (strict-AND only for rail)
    scoreBlob() on each template blob
    → strictTpl: all primary tokens present, OR bigram threshold met
    → relaxedTpl: ≥⌈N/2⌉ tokens (intentionally UNUSED for template rail)
    → Concept expansion (CONCEPT_SYNONYMS) if strictTpl < 10 templates
       │
       ▼
[6] Inspiration Scoring
    For each nano_inspiration record, build blob:
      id + template_id + tags + mergedTopics + search_aliases + params + localeFields
    scoreBlob() → strict or relaxed classification
    Compound-noun precision guard: demote if match is only via multi-word param value
    Template bulk-promotion: if parent template is in strictTpl → score=100, strict=true
       │
       ▼
[7] LLM Rewrite Fallback (fires if strict+template hits < 3)
    rewriteQuery() → gpt-4o-mini → 0–3 alternate phrasings
    Re-score each rewrite with promoteAllUnderStrictTpl=false
    Merge into inspirationById (max score per record wins across passes)
       │
       ▼
[8] Result Assembly
    Select strict pool (or relaxed if no strict)
    Sort by score desc, cap at 80 records
    Within/intent filtering (?within=slug, ?intent=cluster)
    Template rail: union of i18n-matched + inspiration-owning template IDs
       │
       ▼
[9] Intent Chip Aggregation
    calculateTopicCooccurrence() on top-20 inspirations
    rankIntentClusters() → 8 high-level cluster chips
    Business Override can promote one cluster to position 0
    Fallback: topIntentChipsFromTopicCounts() (raw output-type chips)
       │
       ▼
[10] Related Topics Fallback
    Aggregate Tier-2/3 topics from matched template IDs
    Falls back to TIER2_SUGGESTIONS.slice(0,8) on zero results
       │
       ▼
[11] Gallery Prompts (exact-tag only)
    NANO_PROMPT_TAG_SET.has(query or rewrite)
    → Redis fetch via nanoPromptsService (capped at 12, revealing-female filtered)
       │
       ▼
[12] Client Renders SearchResultsClient
    Diversity cap: max 3 inspirations per template_id in grid
    GenerableTemplatesSection: client-side POST to /api/search-template-match
    Tracks search_noresult / search_lowresult events
```

---

## 3. Observed Issues from the P0/P1 Retest

**Overall:** 7 FAIL (0 hits), 10 WARN (1–2 hits, thin), 15 resolved-beyond-baseline.

### Gap classification distribution

| Gap type | Count | Root |
|----------|-------|------|
| c1 (alias/tokenizer fix) | 2 | `水果中文`, `warmup routine running checklist` alias sub-fix |
| c2 (content generation) | 14 | All recipe, food, vocab, map, architecture, then-vs-now |
| c3 (template discovery) | 1 | `unique cultural experiences` |

**Key pattern:** 82% of remaining gaps are c2 — the search algorithm can't rescue queries when the matching content doesn't exist in the catalog.

### Individual retest highlights relevant to architecture

| Query | Hits | Architecture lesson |
|-------|------|---------------------|
| `水果中文` | 0 | Bigram `果中` is generated but is not a real Chinese term; inspiration blobs have `水果` OR `中文` but not both → c1 alias needed |
| `meal prep weekly recipes` | 0 | `recipes` plural doesn't stem (plural-stem only fires on single-token queries) → `recipes` never matches `recipe` in blobs |
| `easy weeknight dinners healthy` | 0 | 4-token strict AND fails; recipe templates exist but 0 matching inspirations |
| `gluten free dinner ideas` | 0 | Same: gluten-free is a content family that exists conceptually but has no catalog instances |
| `bilingual flashcards for kids learning korean fruits` | 1 | 169 vocab inspirations, but only 1 has all 6 tokens together; concept expansion fires for `bilingual/flashcards` but doesn't reach the specific en-ko-fruits record |

---

## 4. Major P0.5 Gap Candidates

These are **systemic architectural deficiencies** — patterns that affect many queries, not just the 17 currently flagged.

| # | Gap ID | Short Title | Affected Surface |
|---|--------|-------------|-----------------|
| G1 | plural-stem | Plural stemming is single-token-only | Inspiration + Template |
| G2 | catalog-density | Entire content families have 0–1 inspirations | Inspiration |
| G3 | flat-scoring | Token-count scoring with no field weighting | Inspiration ranking |
| G4 | bulk-promo-precision | Template bulk-promotion creates score-100 floods | Inspiration ranking |
| G5 | rank-score-orphaned | rank_score unused in search; drives only template feed | Template ordering |
| G6 | concept-expand-inspections | Concept expansion only covers templates, not inspirations | Inspiration |
| G7 | gallery-exact-only | Gallery prompts require exact tag match | Gallery rail |
| G8 | alias-table-empty | QUERY_ALIASES has 2 entries; no systematic coverage | All |
| G9 | cjk-bigram-fragility | Naive character sliding window generates non-words | CJK queries |
| G10 | generable-duplication | LLM generable-template section is isolated from other rails | UX coherence |

---

## 5. Root Cause Analysis

### G1 — Plural Stemming Single-Token-Only

**Location:** `app/[locale]/(public)/search/page.tsx:buildSearchTokens()` (lines 156–168)

**Code evidence:**
```typescript
if (primary.length === 1) {   // ← only fires for single-token queries
  let t = primary[0];
  if (/^[a-z]+s$/.test(t) && t.length >= 4 && !/(ss|us|is|os|as)$/.test(t)) {
    // ... stem logic
  }
}
```

**Impact:** For multi-word queries, every token stays in its original form. `meal prep weekly recipes` → tokens `["meal","prep","weekly","recipes"]`. The blob contains `recipe` (singular), so `recipes` never matches. This affects any multi-word query where a content-word is plural. Frequency: common in natural English ("healthy dinners", "recipe ideas", "fruit flashcards", "animal cards").

**Estimated blast radius:** ~15–25% of multi-word English queries contain at least one plural content token. Of those, some fraction will hit a blob that has only the singular form. Currently masked because most templates use singular slug-form tags.

---

### G2 — Catalog Density: Entire Content Families at 0–1 Inspirations

**Data evidence:**
- 2 templates have 0 inspirations; 7 templates have exactly 1
- Median inspirations per template: 6
- Recipe family: templates for weeknight meals, gluten-free, meal-prep exist but have 0 concrete inspiration records
- Architecture landmark family: 4 inspirations total (only ESB, Colosseum, Sagrada, Eiffel-ish)
- Vintage stamp: 5 inspirations, all narrow topics
- Then-vs-now: 7 inspirations, only 1 per subtopic

**Root cause:** Content generation is a parallel bottleneck to search quality. The blob-matching system requires content to exist before it can be recalled. Templates are declared, but the inspiration records that populate them are sparse for newer or less-prioritized families.

**Why this is a P0.5 gap, not just a c2 todo:** The architecture has no graceful degradation between "template exists" and "inspiration exists". When only a template exists (no inspirations), the template rail shows the empty template card but the inspiration grid shows nothing — giving users no concrete examples of what the template produces. This is a UX cliff edge.

---

### G3 — Flat Token-Count Scoring Without Field Weighting

**Location:** `page.tsx:scoreBlob()` — counts token presence as 1 per token regardless of which field it appears in.

**Current score formula:**
```
strict: score = primaryHits + bigramHits
relaxed: score = primaryHits
```

**Problem:** A match in `template_id` (e.g. the template slug directly encodes the content) carries the same weight as a match in a locale description that mentions the term incidentally. Example: searching `"warmup routine running"` — an inspiration whose `template_id` is `template-warmup-routine-running` scores the same as one whose description is "A running-themed warmup routine guide for athletes". The first is a much stronger topical match.

**Impact on ranking:** Within a strict pool of 30+ results, ordering is essentially arbitrary (JSON file order after score tie). Users see random results rather than the best-matching examples.

---

### G4 — Template Bulk-Promotion Creates Score-100 Floods

**Location:** `page.tsx:scoreQueryTokens()` lines 499–502:
```typescript
if (promoteAllUnderStrictTpl && strictTpl.has(r.template_id)) {
  scored.push({ rec: r, score: 100, strict: true });
  continue;  // skip individual blob scoring
}
```

**Intent:** Gives broad recall when a template's i18n blob matches but some of its inspirations don't contain all query tokens individually.

**Problem:**
1. A template with 168 inspirations (the max in current catalog) would promote ALL 168 to score=100 with a single query match
2. Within the score=100 group, order is determined by JSON array position (effectively insertion order, not quality)
3. The diversity cap (max 3 per template in UI) mitigates visible impact but wastes the score sort — 165 inspirations are scored 100 but never shown
4. For queries that match 2+ templates via bulk-promotion, the relative ordering between templates is undefined (both produce score=100 records mixed together)

**Concrete case:** Query `"bilingual flashcards for kids learning korean fruits"` → `template-vocabulary-english-korean` strictly matches → 169 inspirations bulk-promoted to score=100 → only the first 3 by JSON order are shown → the one *exactly* matching all 6 tokens (en-ko-fruits) may be in position 57 in the JSON and gets dropped by the 80-record cap.

---

### G5 — rank_score Field Orphaned from Search

**Data evidence:**
```
Templates with rank_score: 287/287
rank_score range: 1 to 155
```

**Usage check:**
- `nano_page_data.ts:buildNanoFeedCards()`: rank_score used for template card ordering in the template feed (browse/topic pages)
- `search/page.tsx`: rank_score **NOT used** — inspirations are ranked by token count only

**Impact:** A high-quality, high-traffic template (rank_score=155) gets no search ranking advantage over a low-quality one (rank_score=1). In the template rail, rank_score does determine order when multiple templates match. But within the inspiration grid, there's no quality signal at all.

---

### G6 — Concept Expansion Covers Templates Only, Not Inspirations

**Location:** `page.tsx` lines 643–668 — concept expansion updates only `matchedTemplateIdsByI18nUnion`, not the inspiration scored pool.

**Evidence from CONCEPT_SYNONYMS:**
```typescript
cuban:  { synonyms: ["cuisine", "recipe", "culinary"], ... }
```

For query `"cuban sandwich recipe poster"`:
- Template expansion: `template-food-recipe-tip-infographic` is added to template rail via `cuban → cuisine` expansion ✓
- Inspiration: the specific `template-food-cuban-sandwich` inspiration must independently have `cuisine`, `recipe`, or `culinary` in its blob to appear in the grid

**P0.5 implication:** Template rail and inspiration grid can systematically diverge. A user sees a template card ("use this template") but the inspiration grid below doesn't show matching examples from that template — because the inspiration blob didn't pass its own separate scoring.

---

### G7 — Gallery Prompts: Exact Tag Match Only

**Location:** `page.tsx:galleryTagCandidates` — only the raw query (lowercased) and LLM rewrite strings are checked against `NANO_PROMPT_TAG_SET`.

**Problem:** No fuzzy, alias, or token-overlap matching. A user searching `"watercolor travel"` won't see gallery prompts unless the exact string `"watercolor travel"` is a known tag. The tag `"watercolor travel journal"` exists, but the 2-word query doesn't match it.

**Impact:** Gallery prompts are the most creatively-rich section (user-generated prompts with high visual variety), but they're invisible for the majority of queries that aren't an exact tag match. Current NANO_PROMPT_TAG_SET coverage vs real query space is narrow.

---

### G8 — QUERY_ALIASES Has Only 2 Entries

**Location:** `lib/query_normalize.ts:QUERY_ALIASES`:
```typescript
const QUERY_ALIASES: Readonly<Record<string, string>> = {
  cats: "cat",
  kittens: "kitten",
};
```

**Design intent:** Conservative table for only "safe" plural→singular aliases on the full query string. But the result is that the canonical normalization layer is nearly empty. All alias coverage instead lives in:
1. `searchIndex.ts` SuggestionEntry `.aliases` arrays → only for topic navigation (redirect path), not for free-text search
2. `nano_inspiration.search_aliases` fields → per-record, LLM-generated, inconsistent coverage

**Impact:** Predictable alias patterns (singular/plural for common content terms, common spelling variations, language variants) that would help many queries go unregistered.

---

### G9 — CJK Bigram Window Generates Semantically Empty Bigrams

**Location:** `page.tsx:buildSearchTokens()` — naive sliding window:
```typescript
for (let i = 0; i < w.length - 1; i++) {
  const bg = w.slice(i, i + 2);
  if (/^[一-龥]{2}$/.test(bg)) bigrams.push(bg);
}
```

For `水果中文` (water+fruit = "fruit"; middle+text = "Chinese language"):
- Bigrams generated: `["水果", "果中", "中文"]`
- `果中` is not a real Chinese word; it appears at word boundaries in the query
- The threshold is 2/3 bigrams → a record with `水果` AND `中文` matches — but if no single record has both, 0 hits

**The deeper issue:** The bigram approach assumes CJK content is stored as continuous flowing text. But Curify's inspiration blobs store CJK in discrete field values (tags, aliases, locale titles). A record about "Chinese fruit vocabulary" might have `水果` in its alias and `中文` in its locale title — they're in the same blob but as separate field values, so bigram matching should work. However, `果中` (the cross-boundary bigram) would NOT appear in any well-authored Chinese text, and if the threshold calculation counts it as a "possible match" that never fires, it effectively raises the threshold by 1 for free.

**Practical fix path:** Strip cross-word-boundary bigrams by requiring that both characters of the bigram appear consecutively in at least one source field, or use segmented token matching for known CJK keyword aliases.

---

### G10 — Generable Templates Section Operates in Isolation

**Architecture:** The "Generable Templates" section (`searchTemplateMatch.ts`) is a client-side POST to `/api/search-template-match` — entirely separate from the server-side search pipeline.

**Problems:**
1. **No deduplication with the template rail**: GPT-4o-mini may recommend a template already shown in the main template rail. Users see the same card twice.
2. **No awareness of existing inspiration coverage**: LLM may recommend a template with strong existing inspirations (suggesting the user generate new ones when examples already exist) or vice versa.
3. **Second LLM call latency adds to page load**: rewriteQuery() (if fired) is already one LLM call; searchTemplateMatch is always a second async call. Under cold starts this adds 8–15 seconds before the generable section appears.
4. **Cache is process-local, not shared**: Both `searchRewrite` and `searchTemplateMatch` have their own in-process LRU caches (256 entries each). On Vercel serverless, every cold-start gets an empty cache — the 7-day TTL is functionally irrelevant in production. Real deduplication rate ≈ 0%.

---

## 6. Evidence Summary Table

| Gap | Code Location | Data Evidence |
|-----|---------------|---------------|
| G1 plural-stem | `page.tsx:buildSearchTokens():156` | `recipes` in 4-token query → never stemmed |
| G2 catalog-density | `public/data/nano_inspiration.json` | 7 templates with 1 inspiration; recipe family has 0 for major subcategories |
| G3 flat-scoring | `page.tsx:scoreBlob()` | score = primaryHits + bigramHits; no field weight |
| G4 bulk-promo | `page.tsx:scoreQueryTokens():499` | `promoteAllUnderStrictTpl` promotes all 168 inspirations of a top template to score=100 |
| G5 rank-score | `nano_page_data.ts:136`; absent from `page.tsx` search | rank_score 1–155 unused in inspiration ranking |
| G6 concept-expand-inspirs | `page.tsx:643–668` | Only `matchedTemplateIdsByI18nUnion` updated; inspiration pool unchanged |
| G7 gallery-exact | `page.tsx:galleryTagCandidates` | Raw query + rewrite strings only; no fuzzy/token overlap |
| G8 alias-table | `query_normalize.ts:24` | 2 entries total |
| G9 cjk-bigram | `page.tsx:buildSearchTokens():173–183` | `水果中文` produces `果中` (non-word) as a counted possible bigram |
| G10 generable-isolated | `searchTemplateMatch.ts`, `GenerableTemplatesSection.tsx` | No shared state with main pipeline; process-local cache irrelevant in serverless |

---

## 7. Recommended Priority Order for Fixes

### Tier 1 — High impact, low risk, no content gen required

**P1. Fix plural stemming for multi-token queries (G1)**
- Extend `buildSearchTokens()` to apply the existing stem logic to ALL tokens, not just single-token queries
- Same guard conditions (`-ss`, `-us`, `-is`, `-os`, `-as`) apply
- Expected impact: `meal prep weekly recipes → recipe`, `animal cards → card`, `fruit flashcards → flashcard`
- Risk: low. The guard conditions prevent misfires on irregular nouns. Test against eval set before shipping.
- Effort: 1–2 hours

**P2. Fix CJK bigram cross-boundary fragility (G9)**
- Filter out bigrams that span field-value boundaries by joining CJK-only substrings separately
- OR: add `水果中文`, `中文水果` as explicit `search_aliases` on all en-zh fruit vocabulary inspirations (c1 fix from retest)
- For now, the alias fix is the fastest path; the bigram algorithm fix has broader correctness implications
- Effort: 30 min (alias), 4 hours (algorithm)

**P3. Add field weights to inspiration scoring (G3)**
- Split the blob into two sub-blobs: topical (template_id + tags + topics + search_aliases) vs. contextual (params + localeFields)
- Score topical blob first; use contextual as a secondary score only
- Formula proposal: `score = 10*topicalHits + contextualHits`
- This also reduces false-positive param matches more cleanly than the current compound-noun guard
- Effort: 4–6 hours

**P4. Limit template bulk-promotion to top-N inspirations (G4)**
- Instead of promoting ALL inspirations under a strictly-matched template to score=100, promote only the top-K by a secondary signal (e.g. JSON order, which is currently rank-ordered by editorial curation)
- Proposed: K=20 (matches the co-occurrence analysis window)
- Or: use the inspiration's individual blob score as a tiebreaker within the promoted group
- Effort: 2–3 hours

### Tier 2 — Medium impact, moderate effort

**P5. Incorporate rank_score into inspiration ranking (G5)**
- Add template rank_score as a tiebreaker when inspiration scores are equal
- Proposal: `effectiveScore = score * 100 + (TEMPLATE_RANK_SCORE[template_id] ?? 1)`
- This lifts high-quality template examples to the top of search results
- Effort: 2 hours

**P6. Apply concept expansion to inspiration rail (G6)**
- Extend the concept expansion pass to also score inspiration blobs with expanded token sets
- Use same `suppressWhen` guards to prevent false cuisine expansions on language-learning queries
- Effort: 3–4 hours

**P7. Expand QUERY_ALIASES with common content domain pairs (G8)**
- Add systematic entries for common plural/singular pairs: `recipes → recipe`, `dinners → dinner`, `ideas → idea`, `cards → card`, `posters → poster`, `templates → template`
- Also add common English spelling variants: `colour → color`, `travelling → traveling`
- Note: multi-token alias normalizer vs. per-token stemming (G1) serve different use cases; both needed
- Effort: 1 hour

### Tier 3 — Higher effort or LLM/external dependency

**P8. Gallery prompt fuzzy matching (G7)**
- Add token-overlap matching: a query matches a tag if ≥⌈N/2⌉ of the query's tokens appear in the tag
- Or: pre-index gallery tags → token→tag inverted index, do same two-pass as main search
- Effort: 4–6 hours

**P9. Deduplicate generable templates with main template rail (G10)**
- Pass the set of already-shown template IDs from server props to the client
- `GenerableTemplatesSection` filters out any LLM-suggested template_id that's already in the main template rail
- Effort: 2 hours

**P10. Content generation for thin families (G2)**
- This is a content operations task, not a code fix
- Priority batch queue (from retest):
  1. Recipe family: weeknight healthy, gluten-free, meal-prep (3 JSON configs)
  2. Architecture: 5+ landmark buildings
  3. Then-vs-now: tech, fashion, music, school
  4. Vintage stamps: ocean life, butterflies, wildflowers
  5. Warmup routine: 5K, trail, sprint variants
- Estimated: 2–3 days content generation + alias top-up pass

---

## 8. What Should Be Done Next

### Immediate (this week)

1. **Ship G1 (multi-token plural stemming)** — highest ratio of impact to effort. One code change, addresses a broad class of multi-word queries. Run `node scripts/eval_search.cjs` before and after to confirm no regressions.

2. **Ship c1 alias fix for `水果中文`** (already in retest action items) — add `水果中文`, `中文水果` to `search_aliases` of en-zh fruit vocabulary records. Quick win, addresses a documented P0 miss.

3. **Add `recipes → recipe` to QUERY_ALIASES** (G8 quick start) — directly fixes the `meal prep weekly recipes` plural issue as a belt-and-suspenders to G1.

### Short term (next 2 weeks)

4. **G3 field weights** — redesign inspiration scoring to weight topical fields higher. This is the most impactful structural fix for precision and ranking quality.

5. **G4 bulk-promotion cap** — limit to top-K inspirations per bulk-promoted template. Prevents the score=100 flood that makes the 80-record cap meaningless for template-family queries.

6. **G10 generable template deduplication** — quick UX cleanup, prevents user confusion when the same template appears twice.

### Medium term (next 4 weeks)

7. **G5 rank_score in inspiration ranking** — incorporate editorial quality signal into search order.

8. **G6 concept expansion for inspirations** — extend the existing CONCEPT_SYNONYMS table to cover the inspiration blob (not just templates).

9. **Start content generation batch for G2** — prioritize recipe family (highest query volume impact based on retest misses).

### Watch list (future sprints)

10. **G7 gallery fuzzy matching** — lower priority because gallery prompts are a supplementary surface. Worth revisiting after the main inspiration quality is improved.

11. **G9 CJK bigram algorithm** — currently mitigated by alias additions; full algorithmic fix should wait until a CJK query corpus is large enough to test against.

12. **LLM rewrite process-local cache** — if Vercel KV becomes available, upgrading to a shared cache would eliminate redundant LLM calls for common queries. Not urgent but reduces cost.

---

## Appendix: Architecture Diagram (Text)

```
                        ┌─────────────────────────────────────────┐
                        │               User Query                 │
                        └──────────────────┬──────────────────────┘
                                           │
              ┌────────────────────────────▼──────────────────────────────┐
              │           SERVER-SIDE (search/page.tsx)                   │
              │                                                            │
              │  [1] WC Country Bypass ──────────────────────→ redirect   │
              │  [2] Topic-Match Redirect ────────────────────→ redirect   │
              │       (gated by Business Override)                         │
              │                                                            │
              │  [3] buildSearchTokens()                                  │
              │       tokenize + stem + CJK bigrams + STOPWORDS           │
              │                                                            │
              │  [4] Template i18n Blob Build                             │
              │       (en + zh + locale messages + topic slugs)           │
              │                                                            │
              │  [5] Template Scoring (strict-AND)              ┌─────┐  │
              │       strictTpl set (template rail source)       │Rail │  │
              │       Concept Expansion if < 10 hits             └──┬──┘  │
              │                                                      │     │
              │  [6] Inspiration Scoring                             │     │
              │       per-record blob: id+template_id+tags+          │     │
              │       mergedTopics+aliases+params+localeFields        │     │
              │       compound-noun precision guard                   │     │
              │       bulk-promotion from strictTpl ──────────────────┘    │
              │                                                            │
              │  [7] LLM Rewrite (if thin < 3)                           │
              │       gpt-4o-mini → 0–3 phrasings → re-score             │
              │                                                            │
              │  [8] Sort + cap (80) + within/intent filter              │
              │  [9] Intent Chip Aggregation (top-20 co-occurrence)       │
              │  [10] Related Topics Fallback                             │
              │  [11] Gallery Prompts (exact-tag Redis fetch)             │
              └──────────────────────────┬────────────────────────────────┘
                                         │ props: inspirations, matchedTemplates,
                                         │        galleryPrompts, intentChips, ...
              ┌──────────────────────────▼────────────────────────────────┐
              │          CLIENT-SIDE (SearchResultsClient.tsx)            │
              │                                                            │
              │  Inspirations grid (3-per-template diversity cap)         │
              │  Template rail (from matchedTemplates)                    │
              │  Intent chips (cluster or topic chips)                    │
              │  Gallery prompts (if any)                                 │
              │                                                            │
              │  ── Client-mount async ──                                 │
              │  GenerableTemplatesSection (POST /api/search-template-    │
              │    match → gpt-4o-mini, independent of above)             │
              └────────────────────────────────────────────────────────────┘
```

---

*Generated 2026-06-30 · Branch: baobao/multi-intent-topic-cooccurrence · Source: curify-frontend code review + p0-p1-gap-retest-2026-06-30 data*
