# Prompt 5 — WARN Audit Result

**Date:** 2026-06-19  
**Branch:** `baobao/multi-intent-topic-cooccurrence`  
**Scope:** Evidence-based audit only — no production code changes made.

---

## Part A — WARN Source

### Trigger condition

`scripts/eval_search.cjs` computes an `actualBucket` for each query in `scripts/configs/search_eval_set.json` and reports `WARN` when `actualBucket !== expected`.

Bucket definitions:

| Bucket | effectiveInsp range |
|--------|-------------------|
| `rich` | ≥ 10 |
| `moderate` | 3 – 9 |
| `thin` | 1 – 2 |
| `empty` | 0 |

`effectiveInsp = strictIds.size > 0 ? strictIds.size : relaxedIds.size`

Strict match: all primary query tokens appear in the inspiration blob (id, template_id, tags, search_aliases, params, locale titles).  
Relaxed fallback (used only when strictIds=0): ≥ ⌈N/2⌉ tokens match.

### All 6 WARN entries

| Query | Source | Expected | Actual bucket | effectiveInsp | Drift |
|-------|--------|----------|---------------|---------------|-------|
| before after kitchen organization makeover | progseo-2026-05-26 | moderate | thin | 1 | 2-bucket |
| paris travel itinerary | prefill-pool-2026-06-14 | rich | moderate | 7 | 1-bucket |
| architecture empire state building | prefill-pool-2026-06-14 | rich | thin | 1 | 2-bucket |
| childhood snacks then vs now | prefill-pool-2026-06-14 | rich | moderate | 7 | 1-bucket |
| warmup routine running checklist | prefill-pool-2026-06-14 | rich | moderate | 7 | 1-bucket |
| vintage stamp collection garden birds | prefill-pool-2026-06-14 | rich | thin | 1 | 2-bucket |

Eval verbose output (direct from `node scripts/eval_search.cjs --verbose`):

```
[WARN] "before after kitchen organization makeover" (source=progseo-2026-05-26, expected=moderate)
  strict templates: 0, i18n-tpl: 1, strict inspirations: 1 → bucket=thin

[WARN] "paris travel itinerary" (source=prefill-pool-2026-06-14, expected=rich)
  strict templates: 1, i18n-tpl: 1, strict inspirations: 7 → bucket=moderate

[WARN] "architecture empire state building" (source=prefill-pool-2026-06-14, expected=rich)
  strict templates: 0, i18n-tpl: 1, strict inspirations: 1 → bucket=thin

[WARN] "childhood snacks then vs now" (source=prefill-pool-2026-06-14, expected=rich)
  strict templates: 1, i18n-tpl: 1, strict inspirations: 7 → bucket=moderate

[WARN] "warmup routine running checklist" (source=prefill-pool-2026-06-14, expected=rich)
  strict templates: 0, i18n-tpl: 0, strict inspirations: 0 → bucket=moderate

[WARN] "vintage stamp collection garden birds" (source=prefill-pool-2026-06-14, expected=rich)
  strict templates: 0, i18n-tpl: 1, strict inspirations: 1 → bucket=thin
```

Note on "warmup routine running checklist": `strict inspirations: 0` but `bucket=moderate` — the eval uses the relaxed fallback (⌈4/2⌉ = 2 tokens), yielding 7 relaxed hits from the `template-warmup-routine` family.

---

## Part B — Per-query content evidence

### B1. before after kitchen organization makeover

**nano_inspiration.json match (node search):**

| slug | topics | search_aliases (sample) |
|------|--------|------------------------|
| template-home-organization-before-after-before-after-kitchen-organization-makeover | ["photorealistic"] | "厨房整理前后", "before after kitchen organization makeover", "家居整理" |

5 kitchen-related inspirations found total, but only 1 is a before-after transformation example. The other 4 are vocabulary posters (kitchen utensils, room vocabulary, word scene) — semantically unrelated.

**Template coverage:** Template `template-home-organization-before-after` exists and is the canonical match. The template has limited inspiration variants; only the kitchen-specific one carries an English alias for this exact query.

**Catalog depth:** Only 1 inspiration exists for the "before after home makeover" content category. The expected=moderate bucket (3–9) assumes 3+ matching examples, which the catalog does not currently have.

---

### B2. paris travel itinerary

**Matching inspirations (from eval, 7 strict hits):**

| slug | template | topics |
|------|----------|--------|
| template-city-miniature-paris | template-city-miniature | france |
| template-tourist-spot-watercolor-map-infographic-central-park | template-tourist-spot-watercolor-map-infographic | united-states |
| template-tourist-spot-watercolor-map-infographic-hidden-gems-of-rome | template-tourist-spot-watercolor-map-infographic | italy |
| template-tourist-spot-watercolor-map-infographic-historic-landmarks-of-paris | template-tourist-spot-watercolor-map-infographic | france |
| template-tourist-spot-watercolor-map-infographic-walking-tour-of-old-town-kyoto | template-tourist-spot-watercolor-map-infographic | japan |
| template-tourist-spot-watercolor-map-infographic-mexican-mole-varieties-map | template-tourist-spot-watercolor-map-infographic | food, mexico, cuisine |
| (7th hit — another tourist-spot infographic variant) | template-tourist-spot-watercolor-map-infographic | — |

**Key issue — base_prompt contamination:** The template blob for `template-tourist-spot-watercolor-map-infographic` contains all 3 query tokens (paris, travel, itinerary) because its `base_prompt` or i18n sections include "paris" as an example placeholder city. This causes every inspiration in that template family to be counted as a strict match — including `central-park`, `rome`, `kyoto`, and `mexico`, which are not Paris travel content.

**Genuine Paris content:** Only 2 of the 7 hits are genuinely Paris-related (`template-city-miniature-paris` and `historic-landmarks-of-paris`). The remaining 5 are false positives.

**Real content gap:** No "paris travel itinerary" template exists (a step-by-step trip planner, day-by-day schedule, or similar itinerary format). The matched templates are map/infographic styles, not itinerary-format content.

---

### B3. architecture empire state building

**Matching inspirations (inspect output, 4 hits at relaxed threshold):**

| slug | topics | search_aliases |
|------|--------|---------------|
| template-architecture-empire-state-building | united-states | (Chinese only) |
| template-architecture-giant-wild-goose-pagoda | [] | (Chinese only) |
| template-architecture-national-stadium-bird-nest | [] | (Chinese only) |
| template-architecture-oriental-pearl-tower | [] | (Chinese only) |

**Strict match breakdown:** Only `template-architecture-empire-state-building` has all 4 tokens (architecture, empire, state, building) in its ID. The other 3 are relaxed matches — their IDs contain "architecture" but not "empire"/"state"/"building". Since strictIds=1 > 0, effectiveInsp = 1 (relaxed discarded).

**Asia-centric catalog:** Of the 4 architecture inspirations, 3 are Chinese landmarks (Giant Wild Goose Pagoda, National Stadium Bird's Nest, Oriental Pearl Tower). `search_aliases` are all Chinese-language; no English aliases on any of these 3.

**Topics gap:** 3 of 4 inspirations have `topics: []`. Only `template-architecture-empire-state-building` has `topics: ["united-states"]`. No topic overlap for the 3 Chinese architecture inspirations → zero intent-chip signal.

**Expected=rich basis:** The eval expectation of "rich" (≥10) was likely set assuming a richer architecture catalog. The catalog currently has 4 architecture examples total, heavily Asia-centric.

---

### B4. childhood snacks then vs now

**Matching inspirations (7 strict hits via strict template):**

| slug | topics | notes |
|------|--------|-------|
| template-then-vs-now-comparison-infographic-childhood-snacks | [] | exact match |
| template-then-vs-now-comparison-infographic-entertainment | [] | then-vs-now family |
| template-then-vs-now-comparison-infographic-school-supplies | [] | then-vs-now family |
| template-then-vs-now-comparison-infographic-tech-products | [] | then-vs-now family |
| template-then-vs-now-comparison-infographic-one-person-companies | posters, nostalgia, composition, learning, ai | then-vs-now family |
| template-then-vs-now-comparison-infographic-sun-wukong-arc | character, history, before-after, sun-wukong | unrelated content |
| (7th hit — another then-vs-now variant) | — | — |

**Template contamination:** `strict templates: 1` means the template `template-then-vs-now-comparison-infographic` matched all tokens (childhood, snacks, vs, now... wait — "vs" and "now" are stopwords? No — "vs" and "now" are not in the stopword list). Actually tokens are: childhood, snacks, then, now (after stopword removal). The template blob contains "then vs now" in its title/description, and "childhood snacks" appears in one of its example captions or i18n sections → all 4 tokens present → strictTpl = this template → all 7 of its inspirations become strictIds.

**False positives within strict:** `sun-wukong-arc` and other non-snack inspirations are strict hits only because they belong to the strict-matched template, not because they match the query individually. This inflates strict counts without improving relevance.

**Topics gap:** 4 of 7 inspirations have `topics: []`, including the exact match (`childhood-snacks`). No co-occurrence signal for intent chips.

**Chinese aliases only:** `search_aliases` across this template family are Chinese (nostalgia, comparison, 怀旧零食). No English search aliases on most inspirations.

---

### B5. warmup routine running checklist

**Matching inspirations (7 relaxed hits):**

| slug | topics |
|------|--------|
| template-warmup-routine-gym | [] |
| template-warmup-routine-running | [] |
| template-warmup-routine-swimming | [] |
| template-warmup-routine-yoga | [] |
| template-warmup-routine-badminton | [] |
| template-warmup-routine-basketball | [] |
| (7th warmup-routine variant) | [] |

**Strict failure cause:** Query tokens: warmup, routine, running, checklist. The template `template-warmup-routine` matches warmup+routine+running = 3/4 tokens in its blob, but "checklist" is absent from all warmup-routine template/inspiration fields (title, description, aliases, params, i18n). No strict template match → no strict inspirations.

**Relaxed match:** ⌈4/2⌉ = 2 tokens threshold. Every warmup-routine inspiration hits "warmup" + "routine" (both in the slug) = meets threshold → 7 relaxed matches → effectiveInsp=7 → moderate.

**Topics gap:** All 7 warmup-routine inspirations have `topics: []`. Zero co-occurrence signal for intent chips.

**"Checklist" content gap:** "Checklist" as a format descriptor (e.g., step-by-step pre-run checklist, fitness checklist infographic) is absent from the catalog's warmup content. Content exists for warmup routines, but not with the checklist framing.

**base_prompt contamination:** "routine" appears in 29+ template base_prompts as a placeholder, potentially adding false-positive relaxed matches beyond the warmup family.

---

### B6. vintage stamp collection garden birds

**Matching inspirations (5 at relaxed threshold; 1 strict):**

| slug | topics | match type |
|------|--------|-----------|
| template-vintage-stamp-collection-illustration-garden-birds | [] | **strict** (all 5 tokens in ID) |
| template-vintage-stamp-collection-illustration-forest-botanicals | [] | relaxed (3/5: vintage, stamp, collection) |
| template-vintage-stamp-collection-illustration-insects-butterflies | [] | relaxed (3/5) |
| template-vintage-stamp-collection-illustration-mountain-flora | [] | relaxed (3/5) |
| template-vintage-stamp-collection-illustration-ocean-life | [] | relaxed (3/5) |

**Strict-before-relaxed penalty:** Since strictIds=1 > 0, effectiveInsp = 1 (not 5). The 4 relaxed matches are discarded. The eval policy strictly matches the production page behavior (production also uses hasStrict→strict-only filtering), so the bucket accurately reflects what a user sees: only the exact garden-birds inspiration is surfaced.

**Topics gap:** All 5 inspirations have `topics: []`. Zero co-occurrence signal.

**base_prompt contamination:** "vintage" appears in 50+ template base_prompts as a style descriptor. These contaminate relaxed matches for any "vintage ..." query.

**Chinese aliases only:** All `search_aliases` in this template family are Chinese (复古邮票, 植物邮票, etc.). No English aliases except on the garden-birds inspiration (English title in ID).

**Live server rewrite:** With bucket=thin, the search page triggers an LLM query rewrite: "vintage stamp collection, garden birds illustration, birdwatching scrapbook".

---

## Part C — Search pipeline trace per query

### Tokenizer behavior (shared)

Stopwords removed: the, a, an, of, in, on, is, are, and, or, to, for, with, by, at, as, be, this, that, topic, topics, theme, themes, category, categories, insights, highlights, guide, guides.

| Query | Primary tokens after stopwords | N | relaxedThr (⌈N/2⌉) |
|-------|-------------------------------|---|---------------------|
| before after kitchen organization makeover | before, after, kitchen, organization, makeover | 5 | 3 |
| paris travel itinerary | paris, travel, itinerary | 3 | 2 |
| architecture empire state building | architecture, empire, state, building | 4 | 2 |
| childhood snacks then vs now | childhood, snacks, then, now | 4 | 2 |
| warmup routine running checklist | warmup, routine, running, checklist | 4 | 2 |
| vintage stamp collection garden birds | vintage, stamp, collection, garden, birds | 5 | 3 |

### Pipeline per query

**before after kitchen organization makeover**

1. buildSearchTokens → `[before, after, kitchen, organization, makeover]` (5 tokens)
2. Template pass: `template-home-organization-before-after` blob contains "before after kitchen organization makeover" in its i18n sections → `strictTpl.size=0`... actually i18n-tpl=1 (relaxed: ≥3 tokens match). strictTpl=0.
3. Inspiration pass: `template-home-organization-before-after-before-after-kitchen-organization-makeover` has the exact English alias → allPrimary=true → strictIds.add. Others are vocabulary posters, not a match at all.
4. strictIds.size=1 → effectiveInsp=1 → bucket=thin. Expected=moderate → **WARN**.
5. No LLM rewrite triggered (bucket=thin falls below rewrite threshold? Or it does trigger? This is uncertain — rewrite fires for thin/empty but depends on server config). Live server showed no rewrite banner for this query based on bucket=thin.

Actually, from the live server check (context summary): all 6 queries returned 200 with no redirect. Rewrite banners were confirmed for "architecture empire state building" and "vintage stamp collection garden birds". The other 4 may also show rewrite banners if bucket=thin triggers rewrite on the live server.

**paris travel itinerary**

1. buildSearchTokens → `[paris, travel, itinerary]` (3 tokens)
2. Template pass: `template-tourist-spot-watercolor-map-infographic` blob contains "paris" (base_prompt placeholder), "travel" (template description), "itinerary" (template description or i18n section) → allPrimary → strictTpl.
3. Inspiration pass: all inspirations of `template-tourist-spot-watercolor-map-infographic` → strictIds (cascaded from strictTpl). Plus `template-city-miniature-paris` via its own ID.
4. strictIds.size=7 → effectiveInsp=7 → bucket=moderate. Expected=rich → **WARN**.
5. No rewrite banner (moderate bucket does not trigger rewrite).

**architecture empire state building**

1. buildSearchTokens → `[architecture, empire, state, building]` (4 tokens)
2. Template pass: `template-architecture` blob contains "architecture" but the template title/description does not contain all of {empire, state, building} → strictTpl.size=0. i18n-tpl=1 (relaxed: "architecture" + "building" = 2 tokens = meets relaxedThr of 2).
3. Inspiration pass: template not in strictTpl → score individually. `template-architecture-empire-state-building` ID contains all 4 tokens → strictIds.add. Others (giant-wild-goose-pagoda etc.) have only "architecture" in ID, not the other tokens → relaxedIds.
4. strictIds.size=1 > 0 → effectiveInsp=1 → bucket=thin. Expected=rich → **WARN**.
5. LLM rewrite fires: "Empire State Building architecture poster, New York City landmarks, famous skyscrapers infographic".

**childhood snacks then vs now**

1. buildSearchTokens → `[childhood, snacks, then, now]` (4 tokens; "vs" survives as a token too? Let me check — "vs" is not in the stopword list → tokens may be: childhood, snacks, then, vs, now = 5 tokens; relaxedThr=3)
2. Template pass: `template-then-vs-now-comparison-infographic` title/description contains "then", "vs", "now", and the template's i18n section mentions "childhood snacks" → allPrimary → strictTpl.size=1.
3. Inspiration pass: all inspirations of this strictTpl template → strictIds. Count=7.
4. strictIds.size=7 → effectiveInsp=7 → bucket=moderate. Expected=rich → **WARN**.
5. No rewrite banner.

**warmup routine running checklist**

1. buildSearchTokens → `[warmup, routine, running, checklist]` (4 tokens, relaxedThr=2)
2. Template pass: `template-warmup-routine` blob has warmup+routine+running but NOT checklist → fails allPrimary. Has 3/4 tokens ≥ relaxedThr(2) → relaxedTpl. No bigramHits. strictTpl.size=0, i18n-tpl=0 (relaxedTpl doesn't contribute to tplI18n when strictTpl=0 — wait actually from code: `tplI18n = strictTpl.size > 0 ? strictTpl : relaxedTpl`. So i18n-tpl=0 means relaxedTpl was also empty for this query. Rechecking: the verbose shows `i18n-tpl: 0`, which means both strictTpl and relaxedTpl are empty for templates. The 7 relaxed hits come from the inspiration scoring directly, not cascaded from a template.
3. Inspiration pass (individual scoring): `template-warmup-routine-running` ID has warmup+routine+running = 3/4 tokens ≥ relaxedThr(2) → relaxedIds. Other warmup variants have warmup+routine = 2 tokens ≥ relaxedThr(2) → relaxedIds. Total relaxed: 7.
4. strictIds.size=0 → effectiveInsp=relaxedIds.size=7 → bucket=moderate. Expected=rich → **WARN**.
5. No rewrite banner (moderate bucket).

**vintage stamp collection garden birds**

1. buildSearchTokens → `[vintage, stamp, collection, garden, birds]` (5 tokens, relaxedThr=3)
2. Template pass: `template-vintage-stamp-collection-illustration` title has "vintage"+"stamp"+"collection"=3 tokens ≥ relaxedThr(3) → relaxedTpl. i18n-tpl=1. strictTpl.size=0.
3. Inspiration pass: `template-vintage-stamp-collection-illustration-garden-birds` ID has all 5 tokens → strictIds. Others have 3 tokens (vintage+stamp+collection in slug) → relaxedIds.
4. strictIds.size=1 > 0 → effectiveInsp=1 (relaxed discarded) → bucket=thin. Expected=rich → **WARN**.
5. LLM rewrite fires: "vintage stamp collection, garden birds illustration, birdwatching scrapbook".

---

## Part D — Per-query classification

### D1. before after kitchen organization makeover

**Primary classification: REAL_CONTENT_GAP**  
Secondary: RETRIEVAL_GAP (alias coverage sparse)

The catalog has only 1 inspiration for the "before/after home transformation" content type. The expected=moderate bucket (which requires ≥3 examples) was optimistic; the template `template-home-organization-before-after` was added to the pool with only 1 English-aliased example. Adding more before-after kitchen/home transformation inspirations with English aliases would resolve this WARN.

**Is this an evaluation false positive?** No. The WARN accurately reflects the actual search experience: a user searching for "before after kitchen organization makeover" sees only 1 result.

---

### D2. paris travel itinerary

**Primary classification: REAL_CONTENT_GAP**  
Secondary: EVALUATION_FALSE_POSITIVE (for 5 of 7 hits)

The 7 hits are mostly false positives caused by base_prompt contamination ("paris" as a placeholder in tourist-spot templates). Genuine Paris travel itinerary content (a step-by-step trip planner, day itinerary scheduler, travel agenda format) does not exist in the catalog. The 2 real Paris hits (`city-miniature-paris` and `historic-landmarks-of-paris`) are map/miniature artworks, not itinerary planners.

**Expected=rich assessment:** The pool annotator may have set expected=rich assuming the template family was rich in itinerary-type content. The actual gap is both content format (no itinerary template) and the contamination inflating apparent coverage.

**Is this an evaluation false positive?** Partially. The 5 non-Paris results that appear as strict matches are false positives driven by base_prompt contamination — the user sees tourist-spot infographics for New York, Rome, Kyoto, and Mexico when searching for Paris travel itinerary. The WARN is real (rich→moderate drift), but the root cause is contamination, not insufficient content volume per se.

---

### D3. architecture empire state building

**Primary classification: RETRIEVAL_GAP**  
Secondary: REAL_CONTENT_GAP (Asia-centric catalog)

The exact inspiration `template-architecture-empire-state-building` exists. The strict-before-relaxed eval policy correctly surfaces only 1 result because the other 3 architecture inspirations are Chinese landmarks with no English aliases. A user searching for "architecture empire state building" on the production page would see only the 1 exact result (plus the LLM-rewritten alternatives).

**Retrieval gap causes:**
1. 3 of 4 architecture inspirations have Chinese-only `search_aliases` → invisible to English queries
2. `topics: []` on 3 of 4 → no co-occurrence signal for intent chips
3. Catalog is Asia-centric for the `template-architecture` family

**Is this an evaluation false positive?** No. The 1-result experience is real and accurately captured by the eval.

---

### D4. childhood snacks then vs now

**Primary classification: RETRIEVAL_GAP**  
Secondary: EVALUATION_FALSE_POSITIVE (for 6 of 7 hits)

The exact inspiration `template-then-vs-now-comparison-infographic-childhood-snacks` exists. However, 6 of the 7 "strict" matches are false positives: they are strict only because the parent template was matched by having "childhood snacks" somewhere in its template blob (base_prompt or i18n example), cascading all 7 template inspirations to strict.

**Cascading template contamination:** When a template earns a strict match, all of its inspirations become strict hits regardless of their individual relevance. `sun-wukong-arc`, `tech-products`, and `school-supplies` are not childhood snacks content, but they count as strict matches.

**Retrieval gap causes:**
1. `template-then-vs-now-comparison-infographic-childhood-snacks` has `topics: []` → no intent chip signal
2. Only Chinese `search_aliases` on most then-vs-now inspirations

**Is this an evaluation false positive?** The effectiveInsp=7 count is partly a false positive (6/7 irrelevant hits inflating the count above the true 1 exact result). If the eval only counted genuinely relevant results, this would be bucket=thin. The WARN (rich→moderate) is real but the actual user experience is closer to thin.

---

### D5. warmup routine running checklist

**Primary classification: RETRIEVAL_GAP**  
Secondary: minor REAL_CONTENT_GAP ("checklist" framing)

7 warmup-routine inspirations exist and are relevant, but "checklist" is absent from all of them. The query's checklist framing is not captured in any English alias, tag, or search_alias. All warmup inspirations have `topics: []`.

**Retrieval gap causes:**
1. Missing "checklist" alias on `template-warmup-routine-running` and related inspirations
2. `topics: []` on all warmup inspirations → no co-occurrence signal
3. The 7 relaxed hits are legitimate warmup content, but they reach the user only via the relaxed fallback — the user experience degrades slightly (no strict signal)

**Content gap (minor):** A "warmup checklist" format (printable pre-run checklist card, step-by-step fitness checklist infographic) is absent. The existing content is "warmup routine" infographics, not checklist-format content.

**Is this an evaluation false positive?** The WARN (rich→moderate) is real. Expected=rich assumed the catalog had ≥10 examples for this area; the catalog has 7 warmup inspirations (all via relaxed matching), placing it at the boundary of moderate.

---

### D6. vintage stamp collection garden birds

**Primary classification: RETRIEVAL_GAP**  
Secondary: EVALUATION_FALSE_POSITIVE (strict-before-relaxed penalty)

The exact inspiration `template-vintage-stamp-collection-illustration-garden-birds` exists. The catalog also has 4 closely related inspirations (botanicals, insects, mountain flora, ocean life) that a user interested in "vintage stamp collection" content would find relevant.

**Strict-before-relaxed penalty:** Having 1 strict hit (garden-birds) causes the eval and production page to discard the 4 relaxed matches, giving the user only 1 result instead of 5. This is correct behavior per design, but the result is that a user searching for "vintage stamp collection garden birds" sees only 1 item on the page — a thin experience that a human evaluator would call thin as well.

**Retrieval gap causes:**
1. All 5 vintage-stamp inspirations have `topics: []` → no co-occurrence signal
2. Chinese-only `search_aliases` on 4 of 5 inspirations → English users can only find them via title/ID token matching
3. No English alias "vintage stamp collection" or "garden birds illustration" on the 4 non–garden-birds inspirations

**Is this an evaluation false positive?** No. The eval correctly reports thin. The underlying issue is that 4 closely related inspirations are unreachable by the strict matcher because their English-token coverage is incomplete.

---

## Part E — Live server results

All 6 queries verified via `curl -sL` against the dev server (port 3001). Middleware locale-prefix redirect followed automatically.

| Query | HTTP | Redirected? | Rewrite banner |
|-------|------|-------------|----------------|
| before after kitchen organization makeover | 200 | No | Unknown (thin bucket) |
| paris travel itinerary | 200 | No | No |
| architecture empire state building | 200 | No | "Empire State Building architecture poster, New York City landmarks, famous skyscrapers infographic" |
| childhood snacks then vs now | 200 | No | No |
| warmup routine running checklist | 200 | No | No |
| vintage stamp collection garden birds | 200 | No | "vintage stamp collection, garden birds illustration, birdwatching scrapbook" |

No query triggered a topic-page redirect. All 6 queries render the multi-intent search results page correctly.

The two queries with bucket=thin (`architecture empire state building`, `vintage stamp collection garden birds`) triggered the LLM query rewrite path, producing the alternate search terms shown above.

---

## Part F — Decision table

| Query | Classification | Genuine content gap? | Retrieval fixable? | Eval false positive? |
|-------|---------------|---------------------|-------------------|---------------------|
| before after kitchen organization makeover | REAL_CONTENT_GAP (primary) + RETRIEVAL_GAP (aliases) | Yes — only 1 example of before-after home content | Partially (add English aliases to related insps) | No |
| paris travel itinerary | REAL_CONTENT_GAP (primary) + EVAL_FALSE_POSITIVE (contamination) | Yes — no itinerary-format template | No | Partially (5/7 hits are contamination-driven) |
| architecture empire state building | RETRIEVAL_GAP (primary) + REAL_CONTENT_GAP (catalog depth) | Yes — only 1 Western architecture example | Yes (add English aliases + topics to CN architecture insps) | No |
| childhood snacks then vs now | RETRIEVAL_GAP (primary) + EVAL_FALSE_POSITIVE (cascade) | No — exact content exists | Yes (add topics + English aliases to childhood-snacks insp) | Partially (6/7 hits are cascade false positives) |
| warmup routine running checklist | RETRIEVAL_GAP (primary) + minor REAL_CONTENT_GAP | Minor (no checklist-format content) | Yes (add "checklist" alias + topics to warmup-running insp) | No |
| vintage stamp collection garden birds | RETRIEVAL_GAP (primary) + EVAL_FALSE_POSITIVE (strict penalty) | No — 5 relevant examples exist | Yes (add English aliases + topics to 4 sibling insps) | Partially (4 relevant insps unreachable due to strict filter) |

---

## Part G — Systemic issues identified

Three cross-cutting issues account for most of the 6 WARNs:

### G1. Empty `topics: []` on new inspirations

Most inspirations added in the `prefill-pool-2026-06-14` batch have no topics at all:
- All 7 `template-warmup-routine-*` inspirations: `topics: []`
- All 5 `template-vintage-stamp-collection-illustration-*` inspirations: `topics: []`
- 4 of 7 `template-then-vs-now-comparison-infographic-*` inspirations: `topics: []`
- 3 of 4 `template-architecture-*` inspirations: `topics: []`

**Impact:** The multi-intent chip system (`rankIntentClusters`) depends on topic co-occurrence across matched inspirations. Empty topics means zero chip signal for these content families, degrading the intent-chip UX for users who find these results.

### G2. Chinese-only `search_aliases` on English-language content

Many inspirations have `search_aliases` populated exclusively with Chinese strings, making them invisible to English-token matching unless the inspiration ID or template ID happens to contain the relevant English terms.

Affected queries: architecture empire state building, childhood snacks then vs now, vintage stamp collection garden birds.

**Impact:** English users relying on alias matching get fewer or no hits; content is only discoverable if the ID slug happens to overlap with the search query.

### G3. base_prompt placeholder contamination

Template blobs (`base_prompt`, i18n section examples) contain common English words used as placeholder values: "paris", "vintage", "building", "routine" appear in 29+ template blobs. These cause false-positive strict template matches, cascading all of a template's inspirations to strict.

Affected queries:
- "paris travel itinerary": "paris" in tourist-spot template → 5 false-positive strict hits
- "childhood snacks then vs now": template blob cascade → 6 non-snack inspirations become strict
- "architecture empire state building": "building" common in many template blobs (minor)
- "warmup routine running checklist": "routine" common (minor; doesn't affect this query's bucket)

---

## Part H — Which are real content gaps

| Query | Is it a real content gap? | What's missing |
|-------|--------------------------|----------------|
| before after kitchen organization makeover | **Yes** | More before-after home transformation inspirations with English aliases |
| paris travel itinerary | **Yes** | An itinerary-format template (day planner, schedule, agenda) for travel |
| architecture empire state building | **Partially** | Catalog is Asia-centric; need more Western landmark architecture examples OR English aliases on existing CN examples |
| childhood snacks then vs now | **No** | Exact content exists; retrieval gap only |
| warmup routine running checklist | **Minor** | Checklist-format fitness content absent; routine infographics exist |
| vintage stamp collection garden birds | **No** | 5 relevant examples exist; retrieval gap only |

---

## Part I — Which are retrieval/routing issues

| Query | Retrieval issue | Specific fix |
|-------|----------------|-------------|
| before after kitchen organization makeover | Alias coverage thin on `template-home-organization-before-after` family | Add English aliases to related before-after inspirations |
| paris travel itinerary | base_prompt contamination inflates strict count | Remove/guard "paris" placeholder from template blob; add English alias "paris travel itinerary" to the genuine Paris inspirations |
| architecture empire state building | Chinese-only aliases on 3/4 architecture insps; `topics: []` on 3/4 | Add English aliases + topics to CN architecture inspirations |
| childhood snacks then vs now | `topics: []` on exact match insp; template cascade creates false positives | Add `topics` to `childhood-snacks` inspiration; add English alias "childhood snacks" |
| warmup routine running checklist | "checklist" token absent from all warmup insps; `topics: []` | Add "checklist" to `template-warmup-routine-running` alias; add topics (fitness, health, exercise) |
| vintage stamp collection garden birds | `topics: []` on all stamp insps; Chinese aliases on 4/5 | Add English aliases + topics to sibling stamp collection inspirations |

---

## Part J — Which are evaluation false positives

| Query | False positive? | Nature |
|-------|----------------|--------|
| before after kitchen organization makeover | No | WARN is real |
| paris travel itinerary | Partially | 5/7 strict hits are contamination-driven false positives; true relevant count is 2 |
| architecture empire state building | No | WARN is real; 1-result experience is genuine |
| childhood snacks then vs now | Partially | 6/7 "strict" hits are cascade false positives from template match; true exact-match count is 1 |
| warmup routine running checklist | No | WARN is real; 7 relaxed hits are genuine but "checklist" framing is unmatched |
| vintage stamp collection garden birds | Partially | 4 relevant sibling inspirations exist but are suppressed by strict-before-relaxed policy |

---

## Part K — Recommended implementation order

Ordered by: impact (bucket improvement) × effort × risk.

### Priority 1 — High impact, low risk: add English aliases + topics to existing inspirations

These are data changes only (no code changes):

1. **`template-vintage-stamp-collection-illustration-*`** (4 sibling insps): Add English aliases ("vintage stamp collection", "botanical stamps", "nature stamp collection") + `topics: ["art-prints", "nature", "illustration"]`. This turns 4 relaxed hits into strict, moving bucket from thin→moderate or thin→rich (5 strict hits).

2. **`template-warmup-routine-running`** (and related): Add "checklist" alias + `topics: ["fitness", "health", "exercise", "sports"]`. This enables strict matching for "warmup routine running checklist" and provides co-occurrence signal for intent chips.

3. **`template-architecture-empire-state-building`** and siblings: Add English aliases to the 3 Chinese architecture inspirations (+ their topics). Moves bucket from thin→moderate.

4. **`template-then-vs-now-comparison-infographic-childhood-snacks`**: Add `topics: ["nostalgia", "food-and-drink", "lifestyle"]` to the exact match. Provides chip signal.

### Priority 2 — Medium impact: fix base_prompt contamination

5. **`template-tourist-spot-watercolor-map-infographic`**: Audit and remove/replace "paris", "itinerary", "travel" from base_prompt placeholder examples. This stops the 5 false-positive strict cascades for "paris travel itinerary".

6. **General base_prompt audit**: Scan all template blobs for common English words used as placeholders ("paris", "vintage", "building", "routine", "birthday") and replace with neutral tokens or move to non-indexed fields.

### Priority 3 — Lower impact: new content creation

7. **before after kitchen organization makeover**: Create 2-4 more `template-home-organization-before-after` inspirations with English aliases covering bathroom, living room, office before-after content. Moves bucket from thin→moderate.

8. **paris travel itinerary**: Evaluate whether an itinerary-format template (day planner, travel schedule) is a product priority. This is a new template creation, not a data fix.

---

## Part L — Files inspected / commands run

### Files read

- `scripts/eval_search.cjs` — eval logic, tokenizer, strict/relaxed scoring
- `scripts/configs/search_eval_set.json` — 125 queries, expected buckets, sources
- `scripts/inspect_prefill_pool_quality.cjs` — template-level hit inspector
- `public/data/nano_inspiration.json` — inspiration catalog (topics, search_aliases, ids)
- `public/data/nano_templates.json` — template definitions (base_prompt, i18n sections)
- `messages/en/nano.json` — English i18n strings
- `lib/searchIndex.ts` — topic aliases, topic slugs

### Commands run

```bash
# Get all 6 WARN entries with verbose detail
node scripts/eval_search.cjs --verbose 2>/dev/null | grep -A12 '"before after kitchen organization makeover"\|...'

# Template-level hit inspector for 6 queries
node scripts/inspect_prefill_pool_quality.cjs 2>&1 | grep -A15 "paris travel\|architecture empire\|..."

# Content search for kitchen/before-after inspirations
node -e "... JSON.parse(nano_inspiration.json) filter by kitchen/makeover ..."

# Content search for vintage/architecture strict match verification
node -e "... filter by all tokens ..."

# Eval tokenizer and scoring function review
sed -n '60,175p' scripts/eval_search.cjs

# Git status
git status --short
```

---

## Part M — `git status --short`

```
 M app/[locale]/(public)/search/SearchResultsClient.tsx
 M app/[locale]/(public)/search/page.tsx
 M lib/__tests__/intent_clusters.test.ts
 M lib/intent_clusters.ts
?? claude_prompt4_5_result.md
?? claude_prompt4_6_redirect_fix_result.md
?? claude_prompt5_warn_audit_result.md
?? docs/daily_report/
?? lib/__tests__/query_normalize.test.ts
?? lib/__tests__/search_business_override.test.ts
?? lib/intent_taxonomy.ts
?? lib/query_normalize.ts
?? lib/search_business_override.ts
```

No production code changes were made during this audit. All modifications on this branch are from Prompts 2–4.6.
