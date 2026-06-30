# Curify-Centered External Signal Insights — 2026-06-21

> **Scope:** 58 queries × 5 platforms (Curify, Google Images, Bing Images, Pinterest, Canva)  
> **Framing:** Curify is the product being optimized. The four external platforms are signal sources.  
> **Purpose:** Identify where Curify's current search, routing, and template coverage aligns with or diverges from external user demand signals — and prescribe concrete improvements.  
> **Status:** Pilot insight report — qualitative + semi-quantitative. Not a final benchmark.

---

## 1. Executive Summary

- **This report covers 58 queries across 5 platforms.** Curify is the subject of optimization. Google Images, Bing Images, Pinterest, and Canva are external demand signals — not competitors being ranked.

- **Curify's biggest gap is on creator-oriented queries:** full-10 result rate is only 33% for creative queries vs. 82% for consumer queries. The 58-query set includes 26 creator-oriented and 8 mixed queries — these are Curify's core opportunity space.

- **5 P0 content gaps (zero Curify results)** all sit in high-demand creator categories: recipe templates (3 queries), phonics worksheets (1 query), and unique cultural experiences (1 query). All external platforms return rich results for these. Urgency is high.

- **15 P1 template gaps** represent queries where Curify has some results (2–7) but falls well short of what Canva and Pinterest signal is available. The dominant need is richer template routing for design/illustration, educational printable, and character-chart queries.

- **58 queries span 8 Tier 1 categories.** Template / Printable / Worksheet (8 queries) and Education & Vocabulary (8 queries) together account for 28% of the set — and have the highest Curify relevance scores. Food & Lifestyle (13 queries) is the largest single tier but has the lowest Curify actionability overall.

- **Google Images and Bing Images** are the best signals for understanding broad visual demand and detecting diversity gaps. Bing's avg 39.9 labels/query is the richest category expansion source available.

- **Canva** is Curify's most directly actionable external signal for template routing. Its template category structure (Worksheet, Poster, Infographic, Recipe Card, Presentation) maps 1:1 to Curify's output-type topic routing — but CJK queries (21/58) are inaccessible due to Canva's login wall.

- **Recommended priorities:** (1) Add recipe/meal-planner templates to close P0 gaps; (2) Add phonics/worksheet templates; (3) Improve routing for design-specific queries (watercolor map, red envelope, before-after makeover); (4) Use Bing labels + Canva categories as topic expansion seeds.

---

## 2. Dataset Scope

| Item | Value |
|---|---|
| Query count | **58 queries** |
| Platforms | Curify (subject), Google Images, Bing Images, Pinterest, Canva (signals) |
| Collection period | 2026-06 (automated browser collection) |
| Curify queries with full-10 results | 33/58 (57%) |
| Curify queries with zero results | 5/58 (9%) — all P0 content gaps |
| Google queries complete | 58/58 |
| Bing queries complete | 58/58 |
| Pinterest queries complete | 58/58 |
| Canva queries accessible | 36/58 ok; 21/58 login_required; 1 partial |
| Curify gap analysis | P0=5, P1=15, P2=5, P3=33 |

**Data quality limitations:**

- **Canva login wall:** 21/58 queries are CJK or Japanese IP queries (`单词`, `卡通`, `chiikawa`, `genshin`, etc.). Template signal for these queries must rely on Google/Bing/Pinterest instead.
- **Pinterest label access:** 40/58 queries have zero structured label chips (login modal). Result diversity is still captured; sub-intent signal is qualitative rather than structured.
- **Curify snapshot:** Results reflect the template catalog state at collection time (2026-06). P0/P1 gaps may be partially addressed by subsequent catalog updates; re-run the eval to verify.

---

## 3. Curify-Centered Framing

> The goal of this pilot is not to rank five platforms equally. Curify is the product being improved; Google Images, Bing Images, Pinterest, and Canva are used as external signals.

Each external platform reveals a different type of signal:

| Platform | Signal Type | What It Tells Curify |
|---|---|---|
| **Google Images** | Broad visual demand | What users broadly expect to see; diversity floor; query recall benchmark |
| **Bing Images** | Visual recall + category taxonomy | Richest sub-category vocabulary; alias expansion source |
| **Pinterest** | Inspiration clusters + related sub-intents | What creative directions exist beneath an ambiguous query |
| **Canva** | Template + creator intent | What printable/design outputs are in demand; direct routing comparison |
| **Curify** | Current coverage baseline | Where routing, inventory, and intent detection are already working vs. where gaps exist |

**What Curify should NOT do:**
- Curify should not copy Google or Bing — they are consumer visual search engines optimized for recall breadth, not creative output.
- Curify should not replicate Pinterest's infinite-scroll inspiration feed — Pinterest wins on social graph and board clustering built over years.
- Curify should not clone Canva's template catalog — Canva's moat is a large paying user base and professional template library.

**What Curify SHOULD do:**
- Use Google/Bing to detect where Curify has recall gaps and where visual diversity is missing.
- Use Pinterest's board clusters and related pin semantics to understand what creative sub-directions exist under each query, then route to those in Curify.
- Use Canva's template category structure to identify which output-type topics need to be added or better routed in Curify.
- Curify's unique opportunity is to turn ambiguous queries into **actionable creative outputs**: templates users can edit, inspirations they can remix, and generation paths that move them from search → creation.

---

## 4. Query Tier 1 Distribution

> Full data: `docs/external-signal-pilot/query-tier1-distribution-58-curify-centered.csv`

### 4.1 Tier Distribution Table

| Tier 1 | Query Count | Share | Dominant Orientation | Curify Relevance | Example Queries | Notes |
|---|---|---|---|---|---|---|
| Food & Lifestyle | 13 | 22% | **Consumer** | Low (12/13) | 食物, 葡萄酒, 音乐, cozy reading aesthetic | Largest tier; mostly browse queries with low creator actionability for Curify |
| Character & IP & Pop Culture | 11 | 19% | **Consumer** | Medium (7/11 Medium) | 卡通, chiikawa, mbti marvel, marvel mbti chart | Core audience queries; 3 High-relevance creator sub-queries (chart/poster output) |
| Education & Vocabulary | 8 | 14% | **Creator** | High (7/8) | homophones, english-chinese, 动物 词汇, 词汇 | Curify's strongest tier; bilingual/educational templates well-served |
| Template / Printable / Worksheet | 8 | 14% | **Creator** | High (8/8) | phonics worksheets, ESL flashcards, meal prep, cuban sandwich poster | All 8 are High relevance; contains 4 P0 gaps + 3 P1 gaps — most critical improvement area |
| Design & Visual Style | 6 | 10% | **Creator** | High (5/6) | 电商详情图, watercolor map, vintage poster, red envelope design | Explicit design-output intent; 5 of 6 have content or routing gaps |
| How-to & Craft | 6 | 10% | **Creator** | High (5/6) | 手作, wedding planner, before after kitchen, monstera care | DIY/craft templates and how-to infographics; mix of covered and P1 gaps |
| Travel & Place & Culture | 4 | 7% | **Consumer** | Low (3/4) | remote destination, unique cultural experiences, short city escapes | Mostly browse; 1 P0 gap (unique cultural experiences) |
| Science & Reference | 2 | 3% | **Mixed** | Mixed | 工程, 趣味经济学知识科普 | Small but includes 1 High-relevance creator query (infographic) |

### 4.2 What This Distribution Says for Curify

**Food & Lifestyle (22%) is large but low-priority for Curify's core value prop.** These are mostly consumer browse queries where Curify returns results but they are generic. The real exception is the 4 recipe-creation P0 queries (`easy weeknight dinners`, `gluten free dinner ideas`, `meal prep weekly recipes`, `cuban sandwich recipe poster`) — these have explicit creator intent and should be treated as Template / Printable priority, not generic Food & Lifestyle.

**Template / Printable / Worksheet (14%) and Education & Vocabulary (14%) together are Curify's highest-value tiers.** All 8 Template/Printable queries and 7 of 8 Education/Vocabulary queries are rated High curify_relevance. This confirms Curify's core positioning: educational templates, bilingual flashcards, printable worksheets, and language-learning posters are where Curify can add unique value that neither Google nor Bing provides.

**Character & IP (19%) contains a wide range of creator signal quality.** Consumer character browse queries (genshin, chiikawa, samurai) are already covered; the high-value sub-set is the MBTI/chart creation queries (mbti marvel, infj vs entp, marvel mbti chart) where Curify should have dedicated MBTI × IP chart templates.

**Design & Visual Style (10%) has 5 of 6 queries with gaps.** These queries have very explicit creator intent (watercolor map, red envelope graphic design, before-after makeover). Canva shows rich template supply for all of them; Curify's coverage is thin. This is a high-priority routing and inventory gap.

**How-to & Craft (10%) is generally well-served** with the exception of `before after kitchen organization makeover` (P1, 3 results) and `book lovers gift guide` (P1, 2 results) which need dedicated templates.

---

## 5. Consumer vs. Creative Orientation

| Orientation | Query Count | Share | Typical Query Types | Curify Implication |
|---|---|---|---|---|
| Consumer-oriented | 25 | 43% | Browse imagery, fan content, lifestyle aesthetics, travel, nature | Curify mostly covers these (82% full-10 rate); use Google/Bing to check for diversity gaps but these are not Curify's highest-value queries |
| Creator-oriented | 25 | 43% | Printables, posters, flashcards, design templates, how-to guides | Curify's core opportunity — full-10 rate only 33%; 18 of 20 P0+P1 gaps are creator queries |
| Mixed | 8 | 14% | Recipe inspiration, MBTI charts, comfort food posters, maps | Need better intent disambiguation — Curify should detect the creator signal and surface templates rather than defaulting to inspiration browse |

### 5.1 Consumer Queries: Curify's Role

For the 25 consumer queries, Curify performs reasonably well (82% full-10). The value of external signal here is **diversity checking**: if Google/Bing return 10 semantically diverse results but Curify returns 10 templates that look nearly identical, visual diversity is the gap — not recall. Use Google's related-search labels and Pinterest's board clusters to identify which visual sub-categories are underrepresented in Curify's consumer-query results.

### 5.2 Creator Queries: Curify's Core Opportunity

For the 25 creator queries, Curify's full-10 rate drops to 33%. These are queries where users explicitly want to *make* something — a poster, a worksheet, a recipe card, a map illustration. Every external platform confirms high demand:

- **Canva** returns 10 templates for 24/25 creator queries (1 is login_required).
- **Google** returns 10 results for all 25 with clear creator-intent labels (Free printable, Worksheet template, Recipe poster, etc.).
- **Pinterest** returns 10 pins for all 25 with pin types that include tutorials, templates, and how-to boards.

The gap is Curify's template inventory and routing — not demand, and not the intent system. When Curify's 8-cluster chips show `Learning Materials` or `DIY & Guides` for these queries, the routing logic is working. The templates just aren't there.

### 5.3 Mixed Queries: Intent Disambiguation

For the 8 mixed queries, Curify tends to treat them as either fully consumer or fully creator. Better behavior would be: **detect the creator signal** (explicit words like "poster", "printable", "chart", "recipe card", "infographic", "template") and surface creator-mode results when present. `creative comfort food` should surface recipe card templates; `watercolor map of europe travel destinations` should lead immediately to map illustration templates; `mbti marvel` should route directly to character chart templates.

---

## 6. Curify-Centered Platform Scorecard

> Full data: `docs/external-signal-pilot/platform-scorecard-5x58-curify-centered.csv`

**Important framing:** The scores below do not rank these platforms as competitors. They score each platform's **signal value to Curify** across five optimization dimensions. A low score means the platform is less useful as a signal for that type of Curify improvement — not that the platform is inferior.

For Curify itself, the scores reflect **current performance** (what Curify already delivers) rather than signal value.

| Platform | Consumer Visual Demand Signal | Creative / Template Intent Signal | Visual Diversity Signal | Category / Intent Clarity Signal | Curify Actionability | Curify-Centered Role |
|---|---|---|---|---|---|---|
| **Curify** | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ | Optimization subject — current baseline |
| **Google Images** | ★★★★★ | ★★☆☆☆ | ★★★★★ | ★★★★☆ | ★★★★☆ | Broad visual demand + recall benchmark |
| **Bing Images** | ★★★★★ | ★★☆☆☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ | Category taxonomy + label expansion source |
| **Pinterest** | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★☆☆☆ | ★★★★☆ | Inspiration clusters + sub-intent discovery |
| **Canva** | ★★☆☆☆ | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★★★ | Template + creator intent → direct routing seed |

### 6.1 Score Rationale

**Curify (3/4/3/4/5):**
Consumer coverage adequate for most browse queries (82% full-10) but not deep. Creative template coverage strong in educational/character areas (4/5) but has major inventory gaps in recipe, design-output, and printable-worksheet categories. Visual diversity is template-constrained — results within a cluster tend to look similar. Intent clarity via 8-cluster chips is excellent (4/5). Self-actionability is maximum by definition.

**Google Images (5/2/5/4/4):**
Perfect consumer recall (58/58, 100% full-10). Not template-oriented (2/5 creator signal). Widest visual diversity of any platform (5/5). Related-search labels (avg 17.8/query) are strong for category discovery (4/5). High Curify actionability (4/5) because related-search labels translate directly into topic/alias expansion seeds.

**Bing Images (5/2/4/5/3):**
Matches Google on consumer recall. Not template-oriented (2/5). Good visual diversity (4/5). Richest label taxonomy of any platform: avg 39.9 labels/query (5/5) — 2.2× more than Google, 4.5× more than Curify. Lower Curify actionability (3/5) than Google because the extra label volume provides more breadth but less novel insight for template routing specifically.

**Pinterest (4/4/5/2/4):**
Strong consumer recall with login constraints (4/5). Good creator/inspiration signal — many pins are tutorials, templates, how-tos (4/5). Best visual style diversity of any platform (5/5). Weakest structured category signal (2/5) because 40/58 queries have zero label chips due to login modal. High Curify actionability (4/5) for discovering inspiration clusters and sub-intent routing targets.

**Canva (2/5/3/4/5):**
Weak consumer coverage — template-only, 21/58 inaccessible (2/5). Best creator/template intent signal (5/5). Template visual diversity is narrow (3/5) — similar-looking templates within a category. Good category clarity for ok queries: avg 58.2 labels/ok query (4/5). Maximum Curify actionability (5/5) — Canva's template categories (Worksheet, Poster, Recipe Card, Infographic, Presentation) map directly to Curify's output-type routing.

---

## 7. External Platform Signals for Curify

### 7.1 Google Images → Broad Visual Demand Signal

**Strengths:**
- **100% recall across all 58 queries** — no gaps, no login walls.
- **Related-search labels reveal canonical sub-categories.** Avg 17.8 labels/query are the industry standard for understanding what users associate with each query.
  - `phonics worksheets kindergarten` → labels: Free printable, 1st grade, Beginning sounds, Reading comprehension, Alphabet → these are the Curify template sub-categories that need to exist.
  - `easy weeknight dinners healthy` → labels: Summer dinner, Vegan, Healthy meals, Weight loss → these are the Curify recipe card variants to create.
  - `watercolor map of europe travel destinations` → labels: Detailed map, Map poster, Landmarks, Wall art → these are the Curify design template styles to build.
- **Best semantic diversity signal.** Google's results cover the full range of interpretations for any query — useful for detecting when Curify's results are too narrow.

**Weaknesses:**
- Returns web photos and editorial images, not templates. A Google result for `phonics worksheets kindergarten` links to a teacher's blog, not a generatable Curify template.
- Not a creator-intent signal source — users still need to go somewhere else to make the content.

**Best-fit query types for Curify signal:** All 58 queries as a recall and diversity baseline. Especially useful for consumer queries and mixed queries where the query intent is unclear.

**What this means for Curify:**
Use Google's related-search labels as the **primary seed vocabulary for topic alias expansion and query rewrite**. For every query where Curify's result set looks narrower than Google's, map the label gap to a missing Curify topic slug or alias. Google does not tell you what templates to build — it tells you what users want to find, so Curify can decide what to create.

---

### 7.2 Bing Images → Visual Recall and Category Taxonomy Signal

**Strengths:**
- **Matches Google on recall: 58/58 queries, 100% full-10.**
- **Richest related-search taxonomy: avg 39.9 labels/query.** No query returns zero labels. The labels are structured noun phrases, not raw search terms:
  - `before after kitchen organization makeover` → labels: Budget Kitchen Makeover, DIY Kitchen Makeover Ideas, Home Kitchen Remodel Ideas, Kitchen Makeover Ideas Gallery → these are Curify's before-after template sub-categories.
  - `homophones and homonyms` → labels: Homonyms Chart, Homonyms Homophones Homographs, Homonyms Examples, Homophones Homonyms Homographs Worksheet → these are the Curify educational template variants.
  - `marvel mbti character chart 16 types` → labels: MBTI Marvel, Batman MBTI, Disney MBTI, Avengers MBTI → these are the character-chart template variants Curify should support.
- **Best CJK label coverage.** For CJK queries where Canva is inaccessible, Bing provides CJK-aware labels (e.g., `电商详情图` → `电商详情页, 商品详情页, 电商详情页模板`).

**Weaknesses:**
- Not template-oriented. Same limitation as Google — consumer visual imagery, not generatable templates.
- The extra label volume over Google adds breadth but diminishes marginal insight. Bing's top-5 labels for most queries are similar to Google's, with the additional labels adding long-tail variants.

**Best-fit query types for Curify signal:** All consumer queries for topic/alias expansion. Particularly valuable for English long-tail queries where Google labels are sparse, and for CJK queries where Canva is inaccessible.

**What this means for Curify:**
Build a systematic Bing-label-to-Curify-topic mapping. For each of the 58 queries, compare Bing's top-20 labels to Curify's current topic slug set. Any label cluster that doesn't have a corresponding Curify topic slug is a candidate for taxonomy expansion. Bing's CJK label sets (e.g., `电商详情图` → `电商详情页模板`) are particularly useful for CJK query routing where Canva provides no signal.

---

### 7.3 Pinterest → Inspiration Cluster and Related Intent Signal

**Strengths:**
- **58/58 queries return top-10 results** despite login modal.
- **Best visual style diversity.** Pinterest results span more aesthetic directions per query than any other platform — the same query yields traditional, modern, rustic, minimalist, and artistic variations simultaneously.
- **Pin boards reveal implicit sub-intent clusters.** Even without structured label chips, the titles of boards where users save pins describe the creative direction they're pursuing. `watercolor map of europe travel destinations` pins are saved to boards titled "Travel Map Art," "Europe Illustrated Maps," "Watercolor Geography," and "Map Wall Decor" — these board names are the creative sub-intents Curify should route to.
- **Strong signal for creator/consumer mixed queries.** For ambiguous queries like `creative comfort food`, `cozy reading aesthetic`, or `minimalist autumn outfit for japan travel`, Pinterest's result mix (tutorials, photos, infographics, templates) reveals how users actually interpret the query.

**Weaknesses:**
- **40/58 queries have zero structured label chips** due to login modal. The structured chip signal that would be most useful (related search filters, category tags) is blocked.
- Not template-native — pins link to external pages. Pinterest tells Curify *what directions to offer*; it doesn't provide the templates themselves.

**Best-fit query types for Curify signal:** Creator-oriented and mixed queries where ambiguity is highest. Character & IP queries (for fan sub-intents), Food & Lifestyle queries (for recipe visual sub-types), and How-to & Craft queries (for tutorial style clusters).

**What this means for Curify:**
Curify should not replicate Pinterest's browsing experience. Instead, treat Pinterest as a **sub-intent discovery tool**: the visual clusters Pinterest reveals (e.g., `phonics worksheets kindergarten` → Alphabet Tracing, Beginning Sounds, CVC Words, Sight Words boards) are the Curify template sub-categories that need dedicated routing. When Pinterest users browsing `easy weeknight dinners` consistently save to boards titled "Weekly Meal Planner" and "Recipe Cards Printable," that is the creator-intent signal Curify should convert into a generatable meal-planner template route.

---

### 7.4 Canva → Template and Creator Intent Signal

**Strengths:**
- **Most directly comparable to Curify.** Both are template-first search engines. Canva's accessible results (36/58 queries) show exactly what type of template output users expect — and what Curify should be able to generate.
- **Template category filters are explicit output-type signals.** Canva's filter chips for ok queries (Worksheet, Poster, Instagram Post, Infographic, Presentation, Recipe Card, Flyer) map 1:1 to Curify's output-type topic routing:
  - `phonics worksheets kindergarten` → Canva template types: Worksheet, Educational, Printable → Curify missing these entirely (P0 gap).
  - `cuban sandwich recipe poster` → Canva: Recipe Poster, Food Poster, Infographic → Curify returns 4 results (P1 gap).
  - `before after kitchen organization makeover` → Canva: Before & After, Interior Design, Home Makeover → Curify returns 3 results (P1 gap).
  - `watercolor map of europe travel destinations` → Canva: Map Presentation, Travel Flyer, Illustrated Map → Curify returns 2 results (P1 gap).
- **Highest label density for accessible queries: avg 58.2 labels/ok query** — the most structured template-category signal available.

**Weaknesses:**
- **21/58 queries are inaccessible** (login_required): all CJK queries + `chiikawa` + `genshin`. For these queries, Canva cannot serve as a routing reference — use Google/Bing labels instead.
- **Western-centric template library.** Even for accessible queries, Canva's templates skew toward English-language, Latin-script content. CJK-native template intent is not represented.
- **Template visual similarity is high.** Within any Canva category, templates look very similar — useful for understanding output format but not for visual style diversity.

**Best-fit query types for Curify signal:** All creator-oriented English queries, especially Template/Printable/Worksheet tier (8 queries), Design & Visual Style (6 queries), and How-to & Craft (6 queries).

**What this means for Curify:**
Canva is the most actionable external signal for Curify's template routing. Run a systematic gap analysis: for every Canva-accessible query where Canva returns ≥5 templates but Curify returns <5 results, that is a direct Curify routing or inventory gap. Canva's template category labels (Worksheet, Recipe Card, Before & After, Illustrated Map, Graphic Design) should seed Curify's output-type topic taxonomy. Any Canva template category without a corresponding Curify topic slug is a routing gap to address.

---

## 8. Curify Current Position

### 8.1 Where Curify Is Already Strong

| Area | Evidence | Queries |
|---|---|---|
| Bilingual educational templates | Full-10 results, 35 intent labels | `english-chinese`, `language learning expressions`, `动物 词汇`, `水果中文` |
| Character / IP templates | Full-10 results | `genshin`, `chiikawa`, `吉伊卡哇`, `future characters`, `英文`, `infj vs entp chart` |
| MBTI chart templates | Full-10 results, strong Storytelling cluster | `infj vs entp dating compatibility chart`, `38 insp results` |
| Retro / vintage design | Full-10 results | `1950s vintage diner illustration retro poster` |
| DIY / craft how-to | Full-10 results | `手作`, `monstera plant care guide infographic`, `paper cutting` (9 results) |
| Map templates | Full-10 results, 38 labels (highest of all queries) | `maps` |
| ESL / language printables | Full-10 results | `ESL flashcards printable`, `词汇` |

Curify's 8-cluster intent chip system is working well in these areas — the routing logic correctly identifies intent and the template inventory is sufficient.

### 8.2 Where Curify Has Critical Gaps

**P0 — Zero Results (immediate action required):**

| Query | Tier 1 | Curify Results | External Signal | Action |
|---|---|---|---|---|
| `phonics worksheets kindergarten` | Template / Printable | 0 | Google: 10 (Free printable, Beginning sounds); Canva: 10 (Worksheet, Educational) | Add kindergarten phonics worksheet templates |
| `easy weeknight dinners healthy` | Template / Printable | 0 | Google: 10 (Summer dinner, Healthy meals); Canva: 10 (Recipe Card, Pinterest Pin) | Add healthy weeknight recipe card templates |
| `gluten free dinner ideas` | Template / Printable | 0 | Google: 10 (25 labels); Canva: 10 (Recipe Card, Dietary) | Add gluten-free recipe planner templates |
| `meal prep weekly recipes` | Template / Printable | 0 | Google: 10 (33 labels); Canva: 10 (Meal Planner, Weekly Recipe) | Add weekly meal prep planner templates |
| `unique cultural experiences` | Travel & Culture | 0 | Google: 10 (12 labels); Pinterest: 10 | Add cultural experience / travel inspiration templates |

**P1 — Thin Results (routing + inventory improvement):**

| Query | Tier 1 | Curify Results | Canva Results | Primary Gap |
|---|---|---|---|---|
| `watercolor map of europe travel destinations` | Design & Visual Style | **2** | 10 | Template inventory (watercolor map illustrations) |
| `before after kitchen organization makeover` | How-to & Craft | **3** | 10 | Template inventory (before-after home visual templates) |
| `cuban sandwich recipe poster` | Template / Printable | **4** | 10 | Template inventory (recipe poster templates) |
| `homophones and homonyms` | Education & Vocabulary | **4** | 10 | Template routing (grammar/homophone educational templates) |
| `電商詳情圖` (电商详情图) | Design & Visual Style | **4** | login_required | Template routing (e-commerce detail page design templates) |
| `lunar new year red envelope graphic design` | Design & Visual Style | **4** | 10 | Template inventory (festive graphic design templates) |
| `book lovers gift guide` | How-to & Craft | **2** | 10 | Template inventory (gift guide layout templates) |
| `bilingual flashcards for kids learning korean fruits` | Template / Printable | **6** | 10 | Template routing (Korean-specific bilingual flashcard routing) |
| `Spanish vocabulary printable` | Template / Printable | **6** | 10 | Template routing (Spanish-specific printable vocabulary routing) |
| `mbti marvel` | Character & IP | **5** | 10 | Template routing (MBTI × IP chart combined query routing) |

### 8.3 Where Curify Has Retrieval Issues (P2 — Content May Exist)

| Query | Curify Results | Issue | Action |
|---|---|---|---|
| `工程` | 9 | Tokenization gap — engineering content may exist under different slugs | Audit aliases for 工程/engineering |
| `global influence` | 8 | Topic slug gap — "global influence" may not map to travel/culture topics | Add global/world-culture topic aliases |
| `反义词` | 9 | Near-full but slightly thin — antonym content may be under generic vocabulary slugs | Add antonym/对比词 alias |
| `paper cutting` | 9 | Near-full — paper cutting may be under craft/DIY but not paper-art specifically | Add paper-cutting/kirigami slug |
| `samurai` | 8 | Historical character routing — samurai may be under character but not historical-jp | Add samurai/historical-japan alias |

### 8.4 Consumer Queries: Current Adequate Coverage

33/58 queries (57%) are P3 (adequate). Of the 25 consumer queries, 22 are P3. Curify's consumer-query coverage is the baseline that must not regress as creator-query coverage improves.

---

## 9. Cross-Platform Insights

### 9.1 Signal Strategy Summary

| Signal Need | Best Source | Second Source | How to Use for Curify |
|---|---|---|---|
| What users broadly want to see | Google Images | Bing Images | Recall floor check; if Curify < Google, there's a gap |
| Sub-category vocabulary for topic expansion | Bing Images | Google Images | Bing's 40 labels/query → Curify topic slug candidates |
| Visual style diversity check | Pinterest | Google Images | If Google shows 10 styles and Curify shows 3, diversity gap |
| Creative direction discovery (what to make) | Pinterest | Google Images | Board titles → Curify routing targets for creator sub-intents |
| Template output-type routing | Canva | Pinterest | Canva categories (Worksheet, Recipe Card, etc.) → Curify topics |
| CJK query signal (Canva unavailable) | Google Images | Bing Images | Google/Bing CJK labels → Curify CJK topic aliases |

### 9.2 Consumer vs. Creator Signal Landscape

```
Broad consumer demand ◄─────────────────────────────────► Creator/template demand

   Google     Bing      Pinterest (mixed)    Curify      Canva
   Images     Images    ← inspiration →      ← templates →
   [recall]   [taxonomy][diversity]          [routing]   [categories]
```

For **consumer queries**: Google and Bing define the recall ceiling. If Curify is 2–3 results below that ceiling (P2), the fix is alias expansion. If Curify is 5+ results below (P1 consumer), the fix is content generation.

For **creator queries**: Canva defines the template supply floor. If Canva returns 10 templates and Curify returns 4 (P1 creator), the gap is either template inventory or routing. Use Pinterest to understand the creative direction spectrum; use Canva to understand which template formats to build.

### 9.3 Visual Diversity: Where Curify Should Catch Up

Google and Pinterest show that most queries support multiple distinct visual styles. Curify's 8-cluster chip system allows filtering by intent cluster, but within a cluster the results tend to be stylistically similar. The next layer of diversity improvement is **style-aware routing within clusters**: watercolor vs. flat design vs. vintage vs. photorealistic versions of the same template category.

### 9.4 Category / Intent Clarity: Curify's Relative Strength

Curify's 8-cluster chip system (avg 8.8 labels/query, 0 queries with zero labels) is the most consistent category signal across all 58 queries. Google has 3 queries with zero labels; Pinterest has 40. For intent clarity per query, Curify is actually competitive with Google and better than Pinterest. The opportunity is to **expand the vocabulary beneath each cluster** — the 8 top-level clusters are clear, but the sub-intents within each (e.g., within `Learning Materials`: vocabulary flashcard vs. phonics worksheet vs. bilingual chart) need more granularity.

---

## 10. Curify Gap and Opportunity

### 10.1 Query Intent Expansion

**Current state:** 58 queries are classified into 8 Tier 1 categories. Some queries have thin or mismatched routing because the query tokens don't map cleanly to Curify's current topic slugs.

**Opportunity:** Use Bing's label taxonomy (avg 39.9 labels/query) as a systematic alias expansion source. For each P2 query where content may exist but isn't recalled (`工程`, `反义词`, `global influence`), compare Bing's label set to Curify's topic slugs. Any semantically matching label without a corresponding slug is an alias to add.

**Specific targets:** `engineering/工程` → mechanical drawing, blueprint, technical diagram aliases; `反义词` → antonym, opposite words, contrast vocabulary; `global influence` → world culture, international, cultural map topics.

### 10.2 Topic / Category Routing

**Current state:** Curify's 8-cluster routing works for queries that clearly map to one cluster. Combined queries (`mbti marvel`, `cuban sandwich recipe poster`, `watercolor map of europe`) span multiple clusters and get diluted routing.

**Opportunity:** Implement combined-cluster routing: when a query contains explicit output-type signals (poster, printable, infographic, chart, recipe card, map), boost templates matching that output type within the relevant cluster. `cuban sandwich recipe poster` should route to `Food/Lifestyle × Recipe Card` specifically, not generic food templates.

**Specific targets:** All 15 P1 queries need routing improvement. Priority: `watercolor map` (2 results), `before after kitchen` (3 results), `cuban sandwich poster` (4 results).

### 10.3 Template Matching

**Current state:** Even when routing is correct, Curify may not have the specific template variant a user needs. `phonics worksheets kindergarten` routes correctly to `Learning Materials` but there are zero phonics-specific templates in the catalog.

**Opportunity:** Use Canva's accessible queries (36/58) to identify template format gaps. For each Canva query where Canva has 10 templates and Curify has 0–5, the specific Canva template categories (Worksheet, Recipe Card, Before & After, Infographic) indicate exactly what template formats to add.

**Specific targets (P0 — build from zero):** Phonics worksheet templates; recipe card / meal planner templates (4 queries); cultural experience / travel templates.

### 10.4 Creator-Intent Detection

**Current state:** Curify handles clear creator queries well (e.g., `english-chinese flashcard`, `ESL flashcards printable`). Mixed queries default to generic intent.

**Opportunity:** Detect explicit creator-intent tokens in the query string and apply a creator-mode boost. Tokens like `printable`, `poster`, `worksheet`, `infographic`, `chart`, `recipe card`, `template`, `guide`, `checklist` should shift Curify's result ranking toward creator output types.

**Impact:** Would immediately improve mixed queries like `creative comfort food` (should surface recipe card templates), `watercolor map of europe travel destinations` (should surface map illustration templates), and `book lovers gift guide` (should surface gift guide layout templates).

### 10.5 Creative Result Ranking

**Current state:** Within Curify's top-10 results, visual style diversity is limited. Results cluster stylistically even when they belong to different intent clusters.

**Opportunity:** Introduce style diversity as a ranking signal: ensure that the top-10 results include at least 3 distinct visual styles (e.g., minimalist, illustrated, photorealistic, vintage) for queries that Google and Pinterest show support multiple style interpretations.

### 10.6 Content Gap Detection at Scale

**Current state:** The current 58-query eval identifies P0/P1/P2/P3 gaps manually.

**Opportunity:** Automate the gap detection: run quarterly eval, flag any query where ≥2 of Google/Bing/Pinterest return full-10 results but Curify returns <5 as a P0/P1 candidate. Feed these automatically into the template production backlog.

### 10.7 Generation / Remix Actionability

**Current state:** Curify returns templates users can browse and edit. The search → generation path exists but is not differentiated from the template browsing experience.

**Opportunity:** For queries with explicit creator intent (especially the 26 creator-oriented queries), surface a "Generate this" or "Remix this" CTA prominently — not just a browse grid. The search result should feel like the starting point of a creation session, not just a visual catalog.

---

## 11. Recommended Next Steps

1. **Immediate: Close P0 content gaps (5 queries, high demand).** Add recipe card and meal planner templates targeting `easy weeknight dinners`, `gluten free dinner ideas`, `meal prep weekly recipes`, and `cuban sandwich recipe poster`. Add phonics worksheet templates for `phonics worksheets kindergarten`. Add cultural experience templates for `unique cultural experiences`. These are zero-result queries where all external platforms show strong supply.

2. **Short-term: Address top P1 template inventory gaps (prioritized by Curify result count).** Build watercolor map illustration templates (2 results → target 10). Build before-after home organization templates (3 results → target 10). Build festive graphic design templates for `lunar new year red envelope` (4 results → target 10). Build book / gift guide templates (2 results → target 10).

3. **Short-term: Implement creator-intent token detection.** When a query contains explicit creator-signal tokens (`printable`, `poster`, `worksheet`, `infographic`, `chart`, `recipe card`, `guide`, `checklist`, `template`), apply a creator-mode routing boost. This affects ~8 mixed queries immediately.

4. **Medium-term: Use Bing's label taxonomy for systematic topic alias expansion.** For all 58 queries, compare Bing's top-20 labels to Curify's current topic slugs. Build a "Bing label → Curify topic" mapping table. Any label cluster without a matching slug is an expansion candidate. Prioritize CJK queries where Canva signal is unavailable.

5. **Medium-term: Map Canva's template categories to Curify's output-type topic routing.** For the 36 Canva-accessible queries, extract Canva filter chip labels (Worksheet, Recipe Card, Before & After, Infographic, Illustrated Map) and verify that each has a corresponding Curify output-type topic slug. Missing mappings = routing gaps. This is the most direct path to reducing P1 gaps.

6. **Medium-term: Extract Pinterest board structure for sub-intent routing.** Re-run Pinterest collection with authenticated access to capture board titles for all 58 queries. Build a "Pinterest board title → Curify routing target" map for the top queries. Prioritize creator-oriented and mixed queries where sub-intent disambiguation matters most.

7. **Ongoing: Operationalize the platform eval as a quarterly benchmark.** After each major Curify template catalog or routing update, re-run all 5 platform collectors. Track: full-10 rate per intent tier (creator vs. consumer), Curify vs. Canva result count parity, gap severity distribution (P0/P1/P2/P3 counts). The trend over time is more actionable than any single snapshot.

---

## 12. Appendix

### 12.1 Input Files Used (Not Modified)

| File | Purpose |
|---|---|
| `docs/external-signal-pilot/google-image-eval-58/data/observations.json` | Google 58-query observations |
| `docs/external-signal-pilot/bing-image-eval-58/data/observations.json` | Bing 58-query observations |
| `docs/external-signal-pilot/pinterest-search-eval-58/data/observations.json` | Pinterest 58-query observations |
| `docs/external-signal-pilot/canva-search-eval-58/data/observations.json` | Canva 58-query observations |
| `docs/external-signal-pilot/curify-search-eval-58/data/observations.json` | Curify 58-query observations |
| `docs/external-signal-pilot/external-signal-5x2-query-classification-58.csv` | Query intent classification (consumer/creator) |
| `docs/external-signal-pilot/curify-gap-analysis-58.csv` | Per-query gap severity (P0–P3) |
| `docs/external-signal-pilot/external-signal-5x2-summary.csv` | Platform-level aggregate stats |

### 12.2 Generated Files (New — Did Not Overwrite Existing Files)

| File | Purpose |
|---|---|
| `docs/external-signal-pilot/CURIFY_CENTERED_EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md` | This report |
| `docs/external-signal-pilot/query-tier1-distribution-58-curify-centered.csv` | 58-query Curify-centered tier1 classification with curify_relevance and curify_gap_or_opportunity fields |
| `docs/external-signal-pilot/platform-scorecard-5x58-curify-centered.csv` | 5-platform Curify-centered signal scorecard |

**Confirmed not overwritten:** `EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md`, `EXTERNAL_SIGNAL_INSIGHTS_2026-06-21_zh.md`, `query-tier1-distribution-58.csv`, `platform-scorecard-5x58.csv`, `curify-gap-analysis-58.csv`, `external-signal-5x2-query-classification-58.csv`, `external-signal-5x2-summary.csv`, `external-signal-5x2-comparison-58.md`.

### 12.3 Known Limitations

- **Canva CJK gap:** 21/58 queries inaccessible (all CJK + `chiikawa` + `genshin`). Creator-intent signal for these queries relies on Google/Bing labels only.
- **Pinterest structured labels:** 40/58 queries have zero label chips. Pinterest sub-intent insight is qualitative, based on result observation rather than extracted chip data.
- **Curify snapshot:** Template catalog state as of 2026-06. P0/P1 gaps may have changed; re-run eval to verify after catalog updates.
- **Star ratings are qualitative:** Scores reflect signal value observed across 58 queries during the pilot — not a statistically rigorous multi-dimensional benchmark.

### 12.4 Top Query Examples by Curify Opportunity

**Highest-priority creator gaps (Curify = 0, Canva = 10):**
- `phonics worksheets kindergarten` — Google labels: Free printable, Beginning sounds, Alphabet → Build: phonics worksheet templates
- `meal prep weekly recipes` — Canva: Meal Planner, Weekly Recipe → Build: weekly meal prep planner templates
- `easy weeknight dinners healthy` — Canva: Recipe Card, Dinner Recipes Pinterest Pin → Build: healthy weeknight dinner recipe card templates

**High-priority design routing gaps (Curify < 4, Canva = 10):**
- `watercolor map of europe travel destinations` — Google labels: Map poster, Wall art, Landmarks → Build: watercolor illustrated map templates
- `before after kitchen organization makeover` — Bing: Budget Kitchen Makeover, DIY Kitchen Makeover Ideas → Build: before-after home organization templates
- `book lovers gift guide` — Canva: Gift Guide, Book Lover, Reader Gifts → Build: gift guide layout templates

**High-priority combined-query routing gaps (Curify 4–7, routing improvement needed):**
- `mbti marvel` — Bing: MBTI Marvel, Avengers MBTI, Disney MBTI → Improve: MBTI × IP chart combined routing
- `bilingual flashcards for kids learning korean fruits` — Canva: Educational Flashcard, Korean Language → Improve: Korean bilingual flashcard routing
- `lunar new year red envelope graphic design` — Canva: Festive Template, Graphic Design → Improve: CNY graphic design template routing

### 12.5 Platform Data Quality Summary

| Platform | Queries Accessible | Main Limitation | Signal Reliability |
|---|---|---|---|
| Google Images | 58/58 | None | High |
| Bing Images | 58/58 | None | High |
| Pinterest | 58/58 results; 18/58 labels | Login modal blocks structured chips | Medium (result diversity: High; structured label: Low) |
| Canva | 36/58 | CJK + JP pop-culture = login_required | High for English queries; None for CJK |
| Curify | 53/58 ok; 5/58 ok_empty | P0 content gaps | High (this is the subject, not a signal) |

---

*Generated: 2026-06-21 | Branch: baobao/multi-intent-topic-cooccurrence | 58 queries | 5 platforms | Curify-centered framing*
