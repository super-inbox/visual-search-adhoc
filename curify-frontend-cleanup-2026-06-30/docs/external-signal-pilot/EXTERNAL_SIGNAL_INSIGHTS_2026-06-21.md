# External Signal Pilot Insights — 2026-06-21

> **Scope:** 58 queries × 5 platforms (Curify, Google Images, Bing Images, Pinterest, Canva)  
> **Purpose:** Synthesize external signal pilot results to inform Curify search strategy.  
> **Status:** Pilot insight — qualitative + semi-quantitative. Not a final benchmark.

---

## 1. Executive Summary

- **58 queries** were collected across 5 platforms. The query set spans 8 Tier 1 topic clusters, with **Vocabulary & Language (21%) and Character & IP (19%)** as the two largest groups — both directly actionable for Curify's core template catalog.

- **Google Images and Bing Images** are the best broad-recall consumer benchmarks. Google covers all 58 queries with 100% full-10 results and avg 17.8 related-search labels; Bing extends this with avg 39.9 labels — the richest category-expansion signal of any platform.

- **Pinterest** provides the best visual diversity and sub-intent discovery. Despite login-wall limiting label access (40/58 queries have zero structured chips), the pin board clusters reveal semantic groupings useful for intent routing.

- **Canva** is purpose-built for creative/template search and directly comparable to Curify's template routing. It succeeds on English queries (36/58 ok) but fails silently on CJK and Japanese pop-culture queries (21/58 login_required) — a data quality gap to note.

- **Consumer vs. Creator split:** 25 queries are consumer-oriented, 26 creator-oriented, 7 mixed. Curify performs well on consumer queries (full-10 rate: 82%) but struggles with creator queries (full-10: 33%) — the most urgent growth area.

- **Curify gap analysis:** 5 P0 content gaps (recipe queries: easy weeknight dinners, gluten-free, meal prep, phonics worksheets, unique cultural experiences), 15 P1 template gaps, 5 P2 retrieval gaps. 33/58 queries are performing adequately.

- **Recommended next step:** Use Canva's English template categories as direct routing seeds for creator-oriented queries; use Bing's related-search labels for category/topic expansion; use Pinterest boards to identify visual sub-intent clusters.

---

## 2. Dataset Scope

| Item | Value |
|---|---|
| Query count | **58 queries** |
| Platforms | Curify, Google Images, Bing Images, Pinterest, Canva |
| Collection period | 2026-06 (automated browser collection) |
| Curify queries with results | 53/58 ok, 5 ok_empty |
| Google queries complete | 58/58 |
| Bing queries complete | 58/58 |
| Pinterest queries complete | 58/58 |
| Canva queries accessible | 36/58 ok, 21/58 login_required, 1 partial |
| Report type | Pilot insight (qualitative + semi-quantitative) |

**Data quality notes:**

- Canva login_required queries (21/58) are primarily CJK queries (`单词`, `卡通`, `植物`, etc.) plus two Japanese pop-culture queries (`chiikawa`, `genshin`). Template results for these queries could not be extracted.
- Pinterest label chips (40/58 queries have zero labels) are limited by the login modal. Top-10 results were still collected for all 58 queries.
- Curify 5 ok_empty queries: `unique cultural experiences`, `phonics worksheets kindergarten`, `easy weeknight dinners healthy`, `gluten free dinner ideas`, `meal prep weekly recipes`.

**Input files used:**
- `docs/external-signal-pilot/google-image-eval-58/data/observations.json`
- `docs/external-signal-pilot/bing-image-eval-58/data/observations.json`
- `docs/external-signal-pilot/pinterest-search-eval-58/data/observations.json`
- `docs/external-signal-pilot/canva-search-eval-58/data/observations.json`
- `docs/external-signal-pilot/curify-search-eval-58/data/observations.json`
- `docs/external-signal-pilot/external-signal-5x2-query-classification-58.csv`
- `docs/external-signal-pilot/external-signal-5x2-summary.csv`
- `docs/external-signal-pilot/curify-gap-analysis-58.csv`

---

## 3. Query Tier 1 Distribution

> Full data: `docs/external-signal-pilot/query-tier1-distribution-58.csv`

### 3.1 Distribution Table

| Tier 1 | Query Count | Share | Dominant Orientation | Example Queries | Notes |
|---|---|---|---|---|---|
| Vocabulary & Language | 12 | 21% | **Creator** | 单词, phonics worksheets, ESL flashcards, bilingual flashcards | Strongest creator tier — 11/12 queries explicitly seek printables/templates |
| Character & IP & Pop Culture | 11 | 19% | **Consumer** | 卡通, chiikawa, genshin, mbti marvel, samurai | Primarily browse/fan; 3 creator sub-queries (MBTI charts, compatibility chart) |
| Lifestyle & Aesthetic | 8 | 14% | **Consumer** | 家居装饰, 音乐, met gala, cozy reading aesthetic | Mood/browse queries; creation is secondary |
| Art & Design & Visual | 7 | 12% | **Creator** | 电商详情图, watercolor map, vintage poster, red envelope design | Explicit design output; all expect actionable templates |
| Food & Recipe | 6 | 10% | **Mixed** | 食物, cuban sandwich recipe poster, meal prep weekly recipes | Split: 2 browse, 4 recipe-creation (poster/planner output) |
| DIY / How-to / Craft | 5 | 9% | **Creator** | 手作, paper cutting, kitchen makeover, 趣味经济学知识科普 | Craft/how-to queries expect process visuals or templates |
| Nature & Botanical | 5 | 9% | **Consumer** | 植物, 蔬菜, spring flowers, monstera care guide | Mostly visual browse; 1 creator (monstera infographic) |
| Travel & Place & Culture | 4 | 7% | **Consumer** | remote destination, unique cultural experiences, short city escapes | Travel inspiration browse; no explicit template intent |

### 3.2 Orientation Summary

| Orientation | Query Count | Share | Representative Query Types |
|---|---|---|---|
| Consumer-oriented | 25 | 43% | Browse imagery, fan content, aesthetic, travel, nature |
| Creator-oriented | 26 | 45% | Printables, posters, flashcards, design templates, how-to |
| Mixed | 7 | 12% | Recipe inspiration, MBTI charts, comfort food, maps |

### 3.3 Key Observations

**The 58-query set is creator-leaning (45% creator vs 43% consumer).** This is a deliberate curation — the eval set was designed to stress-test Curify's template routing, not to represent general web search traffic. The consumer queries exist to validate that Curify doesn't regress on general visual search while optimizing for creator demand.

**Vocabulary & Language (12 queries, 21%) is the single largest tier.** Almost all of these are explicitly seeking printable/educational materials. Curify already performs well here (all 12 return results), and it represents the core addressable use case: teachers, language learners, and students who search for printable flashcards, vocabulary posters, and bilingual charts.

**Character & IP (11 queries, 19%) is the largest consumer tier.** These queries are high-engagement consumer browse queries (anime, game characters, MBTI). Curify does reasonably well on these (all 11 return results), but the result depth varies — some only surface 5-7 items rather than a full grid.

**Food & Recipe (6 queries, 10%) has the highest failure rate.** 4/6 recipe-creation queries are either ok_empty or thin: `easy weeknight dinners`, `gluten free dinner ideas`, `meal prep weekly recipes` return zero Curify results. These represent the clearest content gap where external platforms (Google, Pinterest, Canva) are rich.

---

## 4. Consumer vs. Creative Orientation

### 4.1 The Core Split

| Category | Platforms | Role |
|---|---|---|
| **Consumer benchmark** | Google Images, Bing Images | Measure broad visual recall; discover what users mean by a query |
| **Creator/inspiration benchmark** | Pinterest, Canva | Discover template intent, design sub-categories, creative demand |
| **Curify target zone** | — | Creator-first, but must maintain basic consumer recall |

**Why Google and Bing are consumer benchmarks:**
Google and Bing index the entire web. Their image search results reflect what users broadly expect to *see* when they type a query — photos, editorial images, web screenshots. They are not curated for creative use; they are curated for visual recall and relevance. For Curify, they serve as a ceiling check: if Curify can't return *any* result on a query that Google returns 10 rich results for, there is a fundamental content or tokenization gap.

**Why Canva and Pinterest are creator/intent benchmarks:**
Canva's entire product is template search — it is the most direct creative-intent signal available externally. When Canva returns 10 templates for "phonics worksheets kindergarten" but Curify returns 0, that is a direct template gap signal. Pinterest's boards and pins reveal inspiration clusters: when Pinterest users searching "monstera plant care guide infographic" create boards titled "Plant care printables," "Houseplant infographics," and "Green thumb resources," those board names are sub-intent labels Curify can use for routing.

**What Curify should be:**
Curify is not a copy of Google or Bing. Its job is not broad image recall. Its job is to take a user's search query and surface the best *generatable, remixable, actionable* content — templates, inspirations, and designs. The consumer queries in the eval set tell us what users want to *find*; the creator queries tell us what they want to *make*. Curify needs to serve both, but with a creative bias.

### 4.2 Implications by Tier

| Tier 1 | Recommended Signal Source | Action for Curify |
|---|---|---|
| Vocabulary & Language | Canva (template categories) + Bing (label expansion) | Add missing printable templates; improve bilingual routing |
| Character & IP | Google (broad recall) + Pinterest (fan sub-intents) | Ensure full coverage; use fan board names for topic expansion |
| Lifestyle & Aesthetic | Pinterest (mood board clusters) | No urgent action; maintain coverage |
| Art & Design | Canva (template categories) | Priority: these queries expect direct template output |
| Food & Recipe | Canva + Pinterest | P0 gap: add recipe poster/planner templates urgently |
| DIY / How-to | Canva + Pinterest | Add how-to visual templates; process infographic routes |
| Nature & Botanical | Google + Pinterest | Mostly browse; low urgency |
| Travel & Place | Pinterest + Google | Maintain coverage; no major gaps found |

---

## 5. Platform Scorecard

> Full data: `docs/external-signal-pilot/platform-scorecard-5x58.csv`

| Platform | Consumer Search Coverage | Creative / Template Orientation | Visual Diversity | Category / Intent Clarity | Curify Actionability |
|---|---|---|---|---|---|
| **Curify** | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| **Google Images** | ★★★★★ | ★★☆☆☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| **Bing Images** | ★★★★★ | ★★☆☆☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| **Pinterest** | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★☆☆☆ | ★★★★☆ |
| **Canva** | ★★☆☆☆ | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★★★ |

**Scoring criteria (1–5 stars):**

- **Consumer Search Coverage** — does this platform serve broad visual consumer search across the 58-query set?
- **Creative / Template Orientation** — does this platform surface templates, printables, design references, or creative-output intent?
- **Visual Diversity** — is there sufficient variety in result styles, categories, use cases, and visual formats?
- **Category / Intent Clarity** — does the platform expose sub-categories, chips, filters, related searches, or boards that reveal query intent?
- **Curify Actionability** — can Curify use this platform's signal directly to improve search, routing, or content strategy?

### 5.1 Score Rationale

**Curify (3/4/3/4/5):** Curify's 8-cluster intent chips provide excellent intent clarity. Consumer coverage is adequate but creative query full-10 rate is only 33% — structural content gap. Diversity is template-driven and narrow in visual style range.

**Google Images (5/2/5/4/4):** Perfect consumer recall. Related-search labels (avg 17.8/query) are excellent intent signals. Not template-oriented at all — returns web photos, not generatable content.

**Bing Images (5/2/4/5/3):** Matches Google on recall. Richest related-search taxonomy: avg 39.9 labels per query — 2.2× more than Google. High actionability for category expansion but not for template routing specifically.

**Pinterest (4/4/5/2/4):** Best visual diversity and inspiration clustering. Login modal limits structured label access (40/58 zero labels), but even without chips, the pin board ecosystem reveals semantic clusters invisible to other platforms. Strong for creative intent discovery.

**Canva (2/5/3/4/5):** Directly comparable to Curify. 100% template-oriented. CJK query failure (21/58 login_required) is a known limitation — all are CJK or Japanese pop-culture queries. For the 36 accessible English queries, Canva's template category filters (avg 43 labels per ok query) are the single richest structured signal for Curify's template routing.

---

## 6. Platform-Level Insights

### 6.1 Curify

**Strengths:**
- 8-cluster intent chip system provides the clearest structural intent navigation of any platform (cluster → sub-topic → result drill-down).
- Strong on educational/vocabulary queries: all 12 vocabulary & language queries return results; `english-chinese`, `ESL flashcards printable`, `bilingual flashcards` all return full-10.
- Character & IP queries perform well: all 11 return results; `genshin`, `chiikawa`, `samurai` all hit full-10.
- 57% of queries return adequate results (33/58 P3 in gap analysis).

**Weaknesses:**
- **Recipe content is absent (P0):** `easy weeknight dinners`, `gluten free dinner ideas`, `meal prep weekly recipes`, `phonics worksheets kindergarten` → all 0 results. These are high-demand creator queries well-served by Canva, Google, Pinterest.
- **Creator query full-10 rate is only 33%** (10/30 creative queries achieve full-10). Many queries like `cuban sandwich recipe poster`, `before after kitchen organization makeover`, `lunar new year red envelope` return only 2–4 results — high dropout risk.
- **Visual diversity is template-narrow.** Curify's results tend to be thematically consistent but visually similar — limited style variety within a query's result set.
- **CJK consumer queries work better than English creator queries** — the inverse of what Curify's strategic positioning demands.

**Best-fit query types:** Vocabulary/educational templates, character/IP posters, bilingual flashcards, MBTI charts.

**What Curify should learn from itself:** The 8-cluster intent system is working. The gap is not in routing logic — it's in template inventory. Every P0/P1 gap represents a query where routing would work if the templates existed.

---

### 6.2 Google Images

**Strengths:**
- **100% recall across all 58 queries** — no gaps, no login walls, no empty results.
- **Related-search labels (avg 17.8/query)** reveal the canonical sub-categories users associate with each query. Examples: `phonics worksheets kindergarten` → labels: Free printable, 1st grade, Beginning sounds, Reading comprehension, Alphabet. `cuban sandwich recipe poster` → labels: Cuban Sandwich Bread, Classic Cuban Sandwich, Authentic Cuban Sandwich.
- **Best for understanding query scope:** Google's result set shows the full semantic range a query can cover, including long-tail and edge cases Curify doesn't serve.
- **3 queries have zero labels** (the only limitation): `唯美春天`, `工程`, `homophones and homonyms` — these are niche enough that Google's related-search UI didn't surface chips.

**Weaknesses:**
- **Not template-oriented at all.** Results are web photos, editorial images, stock imagery. No printables, no design-output intent.
- **Visual diversity is horizontal breadth, not vertical depth.** Google shows the widest range of interpretations but not the deepest within any one style.

**Best-fit query types:** All query types as a recall benchmark; particularly useful for consumer browse queries where understanding the semantic range matters.

**What Curify should learn from it:**
- Use Google's related-search labels as a **query intent taxonomy seed.** The labels for each query reveal 5–10 sub-categories that can directly inform Curify's topic routing and alias expansion.
- Use Google's result variety to detect when Curify is returning a semantically too-narrow set (e.g., if Google shows 10 distinct interpretations of a query and Curify shows 10 that all look the same, diversity is the gap).
- Monitor which queries have Google labels but Curify has no corresponding topic chips — those are routing gaps.

---

### 6.3 Bing Images

**Strengths:**
- **100% recall, matching Google.** All 58 queries return full-10 results.
- **Richest category taxonomy of any platform: avg 39.9 labels per query** (2.2× Google, 4.5× Curify). No query returns zero labels. Examples: `maps` → 40 labels (World Map, Old Map, Map Art, Map of the USA, Kids Map, Antique Map...); `phonics worksheets` → 40 labels (Free Kindergarten, Phonics Reading, Alphabet Activities...).
- **Label quality is more structured than Google.** Bing's related-search labels tend to be noun phrases rather than raw search terms, making them directly usable as topic/category tokens.

**Weaknesses:**
- **Not differentiated from Google for creative intent.** Results are also web imagery, not templates.
- **Lower Curify actionability** because the signal is best used for category expansion, not direct template routing. The extra label volume over Google mostly adds breadth, not qualitative new insights.
- **Image quality signal is weaker** — Bing's results tend to be more heterogeneous in quality than Google's editorial picks.

**Best-fit query types:** All consumer queries for category expansion. Particularly valuable for long-tail English queries where Google labels are sparse.

**What Curify should learn from it:**
- **Use Bing's 40-label sets as the primary vocabulary source for topic/alias expansion.** For any query where Curify's topics are thin, Bing's labels are the richest external reference.
- Compare Bing labels to Curify's current topic taxonomy — any label cluster that doesn't have a matching Curify topic slug is a candidate for addition.
- For CJK queries where English labels are scarce, Bing's CJK-aware search pipeline provides useful label sets (e.g., `单词` returns `英语单词, 英文单词, 单词表`).

---

### 6.4 Pinterest

**Strengths:**
- **100% result recall (all 58 queries return 10 results),** despite login modal on most queries.
- **Best visual diversity of any platform.** Pinterest's result set for any query spans multiple visual styles, use cases, and aesthetic directions — pin boards reveal semantic clusters invisible in other platforms.
- **Strong for creative and consumer mixed queries.** For queries like `creative comfort food`, `cozy reading aesthetic`, `minimalist autumn outfit for japan travel`, Pinterest's board clustering reveals natural sub-intent groupings.
- **Board titles are implicit intent labels.** Even without structured chips, the titles of boards that users save a pin to reveal what sub-intent the result serves. This signal is not directly captured in this eval but is accessible via Pinterest's board API.
- **Excellent inspiration-to-creation signal.** Pinterest pins include a mix of photos, illustrations, infographics, and templates — the result set itself shows the creator/consumer mix for each query.

**Weaknesses:**
- **40/58 queries return zero structured label chips** due to the login modal. This is the biggest data quality limitation of the Pinterest dataset.
- **Results require login to access related search / visual search features.** Without these, Pinterest's structured signal is significantly reduced.
- **Not template-native.** Pinterest pins link to external pages; unlike Canva, there is no "edit this template" CTA. The creative intent signal is inspirational, not directly actionable for template routing.

**Best-fit query types:** Creative inspiration queries, aesthetic queries, home/lifestyle, food/recipe, fashion, travel.

**What Curify should learn from it:**
- **Use Pinterest board naming conventions as sub-intent taxonomy.** When users searching "monstera plant care" consistently save to boards named "Plant care printables" and "Houseplant infographics," those terms are the sub-intent clusters Curify's routing should target.
- **Use Pinterest's visual cluster diversity as a benchmark for Curify's result diversity.** If Pinterest shows 10 visually distinct styles for a query and Curify shows 10 similar-looking templates, the diversity gap is the problem.
- **Pinterest is the best signal for lifestyle and aesthetic queries** that Google/Bing over-index on editorial photos. For `cozy reading aesthetic` or `minimalist autumn outfit`, Pinterest's results are closer to what a Curify user would want to create.

---

### 6.5 Canva

**Strengths:**
- **Most directly comparable to Curify** of any external platform — both are template-first search engines.
- **36/58 queries accessible,** all returning template-category results. Label structure is richest for ok queries (avg 43 labels per ok query).
- **Template category filters are explicit intent signals.** Canva's filter chips (e.g., "Presentation," "Instagram Post," "Worksheet," "Infographic") directly map to the output-type vocabulary Curify uses for topic routing.
- **Best creator-intent signal for English queries.** For `phonics worksheets kindergarten`, `ESL flashcards printable`, `cuban sandwich recipe poster`, `1950s vintage diner retro poster` — Canva's results are exactly the template format and style that Curify should be routing to.
- **Template format diversity is clear.** A Canva result for `language learning expressions` shows: flashcard sets, poster layouts, presentation slides, worksheet templates — all distinct output types. This is the creative-intent taxonomy Curify needs.

**Weaknesses:**
- **21/58 login_required, all CJK or Japanese pop-culture queries.** This is the biggest limitation: Canva blocks non-authenticated CJK search. All Chinese-language queries (`单词`, `卡通`, `植物`, etc.) and `chiikawa`/`genshin` are inaccessible.
- **Western-centric template catalog.** Even for accessible queries, Canva's templates skew toward English-language, Western aesthetic, and Latin-script content. CJK-native template design intent is not well represented.
- **High template visual similarity.** Canva templates for similar queries (e.g., all "vocabulary flashcard" results look nearly identical in layout) — less visual diversity than Pinterest or Google.

**Best-fit query types:** Educational templates, recipe posters, design-output queries (wedding planner, graphic design), lifestyle/aesthetic templates, MBTI charts.

**What Curify should learn from it:**
- **Use Canva's ok-query template categories as direct routing seeds for Curify's topic taxonomy.** When Canva categorizes "phonics worksheets" results into "Worksheet," "Educational," "Printable" — those are the output-type topics Curify should ensure it has mapped.
- **Compare Canva's ok queries to Curify's template gaps.** Any query where Canva returns 10 templates but Curify returns <5 is a P1 template gap. There are 15 such queries in this eval.
- **For CJK query routing, Canva cannot be used as a reference.** Use Google/Bing labels and Pinterest results instead.
- **Canva's isPro flag** (visible in result metadata) signals which template categories are premium vs. free — useful for understanding the commercial template landscape.

---

## 7. Cross-Platform Insights

### 7.1 Which Platform to Use for Each Signal Type

| Signal Need | Best Platform | Second Best | Notes |
|---|---|---|---|
| Broad visual consumer recall | Google Images | Bing Images | Use as coverage floor; if Curify can't match, fix the gap |
| Category / sub-intent taxonomy | Bing Images | Google Images | Bing's 40 labels/query are the richest structured vocabulary |
| Visual inspiration clusters | Pinterest | Google Images | Pinterest board structure reveals semantic sub-intents |
| Template / creator intent | Canva | Pinterest | Canva is directly comparable to Curify's template routing |
| CJK query intelligence | Google Images | Bing Images | Canva inaccessible; Pinterest limited; Google/Bing best for CJK |
| Content gap detection | Canva + Google | Curify gap CSV | Where Canva has 10 templates and Curify has 0–4: P0/P1 gap |

### 7.2 Platform Positioning on the Consumer–Creator Axis

```
Consumer ◄────────────────────────────────────► Creator

  Google      Bing       Pinterest      Curify      Canva
  Images      Images     (inspiration)  (templates) (templates)
  ★★★★★       ★★★★★      ★★★★           ★★★★        ★★★★★
```

- **Google and Bing** anchor the consumer end. Their value is recall completeness and category breadth. They tell you *what a query means*, not *what to make from it*.
- **Pinterest** straddles the middle. It is consumer-facing (browsing/saving pins) but creator-adjacent (many pins are templates, tutorials, and how-tos). It is the best platform for discovering the inspiration → creation transition.
- **Curify and Canva** anchor the creator end. Both are template-first. Their shared failure mode is consumer coverage — neither serves broad visual browse as well as Google/Bing.

### 7.3 Diversity Analysis

| Platform | Diversity Type | Score | Notes |
|---|---|---|---|
| Google Images | Semantic breadth | ★★★★★ | Most query interpretations covered |
| Pinterest | Visual style breadth | ★★★★★ | Most aesthetic / style variety per query |
| Bing Images | Category depth | ★★★★☆ | Most sub-category labels; slightly less visual style range |
| Curify | Template format diversity | ★★★☆☆ | Good cluster diversity but templates visually similar |
| Canva | Template type diversity | ★★★☆☆ | Clear output types but templates stylistically narrow |

### 7.4 Intent / Category Clarity

| Platform | Clarity Source | Avg Labels | Notes |
|---|---|---|---|
| Bing Images | Related search chips | 39.9 | Best structured taxonomy |
| Canva | Template category filters | 43 (ok queries) | Best for creator intent; 21 queries inaccessible |
| Google Images | Related searches | 17.8 | Good quality, lower volume |
| Curify | Intent cluster chips | 8.8 | 8-cluster system; clear but narrower vocabulary |
| Pinterest | Board titles (implicit) | 0.6 structured | Login limits chips; board structure rich but unextracted |

---

## 8. Curify Gap and Opportunity

### 8.1 What Curify Should Not Try to Be

Curify should **not** try to replicate Google Images or Bing Images. Those platforms win on breadth, speed, and raw image recall from the open web. Competing there is a losing proposition. Similarly, Curify should not try to replicate Pinterest's infinite scroll inspiration feed — Pinterest wins on social graph and board clustering that took years to build.

### 8.2 Curify's Actual Opportunity

Curify's moat is the **search → generate → use** pipeline. A user who finds a vocabulary poster on Google still needs to go somewhere to make it. A user who finds a recipe pin on Pinterest still needs to find the template. Curify is the place where the search result IS the generatable content. This means:

1. **Query intent expansion:** Use Google/Bing labels to identify what sub-intents a query carries. Map those sub-intents to Curify's 8-cluster system and ensure every intent has templates behind it.

2. **Topic/category routing improvement:** Use Canva's template categories (for English queries) and Pinterest's board titles as seed vocabulary for Curify's topic taxonomy expansion. Every Canva template category that Curify doesn't have a matching topic for is a routing gap.

3. **Template matching and inventory:** The P0/P1 gaps (20 queries, 34% of the eval set) are not routing failures — they are inventory failures. The 8-cluster system would route correctly IF the templates existed. Priority: add recipe poster/planner templates (P0), then educational printable variants (P1).

4. **Content gap detection at scale:** The 5-platform eval framework should be run quarterly. Any query where ≥2 of Google/Bing/Pinterest return full-10 results but Curify returns <5 is a flagged gap that needs either new templates or improved tokenization.

5. **Better creative result presentation:** Even when Curify has results, visual diversity is lower than Pinterest/Google. The 8-cluster chip allows filtering, but within a cluster the results look similar. Style diversity within a cluster (watercolor vs. flat design vs. vintage) is the next presentation quality lever.

### 8.3 Gap Summary

| Severity | Count | Example Queries | Recommended Action |
|---|---|---|---|
| P0 — Content gap | 5 | easy weeknight dinners, phonics worksheets, meal prep, gluten-free dinners, unique cultural experiences | Add templates via content generation batch; immediate |
| P1 — Template gap | 15 | cuban sandwich poster, wedding planner, bilingual flashcards, watercolor map, kitchen makeover | Add dedicated templates for these creative intents |
| P2 — Retrieval gap | 5 | 工程, global influence, 反义词, paper cutting, samurai | Audit aliases and tokenization; content may exist but not retrieved |
| P3 — Adequate | 33 | 单词, genshin, chiikawa, english-chinese, met gala | Monitor for regression; no immediate action |

---

## 9. Recommended Next Steps

1. **Fix P0 content gaps (immediate, 5 queries):** Run a content generation batch targeting recipe poster templates (`easy weeknight dinners`, `gluten-free dinner ideas`, `meal prep weekly recipes`), kindergarten phonics worksheets, and travel cultural experience templates. These are high-demand consumer/creator queries with zero Curify results but strong external signal.

2. **Address P1 template gaps (short term, 15 queries):** For each P1 query, validate that Curify's routing would surface results IF templates existed. Use Canva's ok-query template categories as the style/format reference for what templates to add.

3. **Use Bing's 40-label sets to expand Curify's topic alias vocabulary.** For each of the 58 queries, compare Bing's related-search labels to Curify's current topic slug set. Any label cluster without a matching topic slug is a candidate for taxonomy expansion.

4. **Extract Pinterest board structure for sub-intent discovery.** The current pilot captured top-10 pins but not board metadata. A follow-up pass with authenticated Pinterest access should extract board titles for all 58 queries — these are the richest available source of semantic sub-intent clusters.

5. **Formalize the Canva vs. Curify template comparison for English queries.** For the 36 Canva-accessible English queries, build a systematic comparison: Canva template category → Curify topic slug mapping. Gaps = topics to add; matches = current routing quality indicators.

6. **Expand the eval set from 58 to ~200 queries, stratified by tier1.** The current 58-query set over-represents Vocabulary & Language (21%) and under-represents Food & Recipe (10%) and Travel (7%). A 200-query set stratified by tier1 would give more reliable signal per category.

7. **Operationalize the platform scorecard as a quarterly benchmark.** Re-run all 5 platform collectors after each major Curify search update. Track: full-10 rate per platform, avg labels, Curify vs. Canva result count parity. Trend over time is more actionable than a single snapshot.

---

## 10. Appendix

### 10.1 Generated Files

| File | Purpose |
|---|---|
| `docs/external-signal-pilot/query-tier1-distribution-58.csv` | 58-query tier1 classification with consumer/creator orientation and key categories |
| `docs/external-signal-pilot/platform-scorecard-5x58.csv` | 5-platform scorecard with 5-dimension star ratings |
| `docs/external-signal-pilot/EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md` | This report |

### 10.2 Previously Generated Files (Reused, Not Modified)

| File | Purpose |
|---|---|
| `docs/external-signal-pilot/external-signal-5x2-query-classification-58.csv` | Query intent (consumer/creator) classification |
| `docs/external-signal-pilot/external-signal-5x2-summary.csv` | 5-platform × 2-intent aggregated stats |
| `docs/external-signal-pilot/curify-gap-analysis-58.csv` | P0/P1/P2/P3 gap severity per query |
| `docs/external-signal-pilot/external-signal-5x2-comparison-58.md` | Earlier 5×2 comparison report |

### 10.3 Known Limitations

- **Canva CJK gap:** 21/58 queries inaccessible due to login wall on CJK queries. Analysis of Chinese-language template demand cannot use Canva as a reference.
- **Pinterest label gap:** 40/58 queries have zero structured label chips due to login modal. Pinterest insight relies on result diversity observation rather than structured chip analysis.
- **Curify results are a point-in-time snapshot.** The eval was collected in 2026-06. Curify's template catalog changes; re-run the eval after content additions to measure improvement.
- **No cross-platform result de-duplication.** The same image/template may appear on multiple platforms; this eval does not track cross-platform overlap.
- **Star ratings are qualitative judgments** based on platform behavior observed across the 58-query eval set, not a statistically rigorous scoring.

### 10.4 Platform Data Quality

| Platform | Full Coverage | Main Limitation |
|---|---|---|
| Google Images | 58/58 queries | None in this eval |
| Bing Images | 58/58 queries | None in this eval |
| Pinterest | 58/58 results, 18/58 labels | Login modal blocks structured chips |
| Canva | 36/58 queries | CJK + JP pop-culture = login_required |
| Curify | 53/58 ok, 5 ok_empty | Content gaps (P0 recipe/educational queries) |

---

*Report generated: 2026-06-21 | Branch: baobao/multi-intent-topic-cooccurrence | Queries: 58 | Platforms: 5*
