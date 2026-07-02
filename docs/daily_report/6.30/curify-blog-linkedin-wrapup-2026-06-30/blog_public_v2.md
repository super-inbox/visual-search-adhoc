# Visual Search for Creative Queries: A 58-Query Pilot Study Across 5 Platforms

> **Scope:** 58 queries × 5 platforms (Google Images, Bing Images, Pinterest, Canva, Curify)
> **Nature:** Small-scale pilot study — qualitative + semi-quantitative. Not a rigorous full benchmark. Findings are directional.
> **Collection period:** June 2026

---

## 1. Executive Summary

- **58 queries** were evaluated across 5 platforms. The query set spans 8 topic categories — with Vocabulary & Language (21%) and Character / IP / Pop Culture (19%) as the two largest — covering English, CJK, and bilingual content.

- **The core insight from this pilot: visual search platforms fall on a clear consumption-to-creation spectrum.** Google Images and Bing Images anchor the consumption end, excelling at broad visual recall. Canva and Curify anchor the creation end, serving users who want to generate or adapt a template. Pinterest occupies the middle, offering the richest visual diversity and the most granular sub-intent signal.

- **Google Images and Bing Images** provide the strongest broad recall baseline. Bing's related-search label chips (average 39.9 per query) are the richest external taxonomy signal of any platform in this pilot.

- **Pinterest** offers the best visual diversity and the most granular sub-intent discovery. Its One Bar sub-intent label chips reveal how users actually decompose a query — a qualitatively different signal from Bing's broad taxonomy chips.

- **Canva** is the most direct external benchmark for English creation-oriented queries. Template categories and filter label chips directly reflect what users expect from a template-first search surface. The structural limitation: 21 of 58 queries (all CJK and Japanese pop-culture queries) are blocked by a login wall.

- **Curify** is template-first and imposes no login barrier on CJK queries. Educational and character/IP queries perform particularly well. The primary growth area is creation-oriented queries in the food/recipe and niche design categories.

- **Next directions:** expand the query set from 58 to ~200 with stratified sampling; operationalize a quarterly platform benchmarking cadence; use Bing label chips and Pinterest One Bar chips as taxonomy and sub-intent seed signals.

---

## 2. Data Scope

| Item | Value |
|---|---|
| Query count | **58 queries** |
| Platforms | Google Images, Bing Images, Pinterest, Curify, Canva |
| Collection period | June 2026 (automated browser collection); Pinterest label chips manually verified June 23, 2026 |
| Google coverage | 58/58 queries |
| Bing coverage | 58/58 queries |
| Pinterest coverage | 58/58 queries (Top-10 results); 36/58 queries have manually verified label chips; 22/58 have no label chips |
| Canva coverage | 36/58 accessible; 21/58 blocked by login wall |
| Report nature | Pilot study (qualitative + semi-quantitative) |

**Data quality notes:**
- Canva's 21 blocked queries are all CJK queries (`单词`, `卡通`, `植物`, etc.) and two Japanese pop-culture queries (`chiikawa`, `genshin`).
- Pinterest's automated label chip collection was intercepted by Pinterest's login modal. The 36/58 query label chip data in this report was manually collected and verified; it is not reproducible at scale by automated means.

---

## 3. 58-Query Overview

The query set spans **8 topic categories**:

| Topic Category | Queries | Share | Primary Orientation | Example Queries |
|---|---|---|---|---|
| Vocabulary & Language | 12 | 21% | Creation-oriented | phonics worksheets, ESL flashcards, bilingual flashcards, 单词 |
| Character / IP / Pop Culture | 11 | 19% | Consumption-oriented | 卡通, chiikawa, genshin, mbti marvel, samurai |
| Lifestyle & Aesthetics | 8 | 14% | Consumption-oriented | 家居装饰, met gala, cozy reading aesthetic, music |
| Art & Design | 7 | 12% | Creation-oriented | watercolor map, vintage poster, red envelope design |
| Food & Recipes | 6 | 10% | Mixed | cuban sandwich recipe poster, meal prep weekly recipes |
| DIY / How-To / Crafts | 5 | 9% | Creation-oriented | paper cutting, kitchen makeover, 手作 |
| Nature & Plants | 5 | 9% | Consumption-oriented | 植物, spring flowers, monstera care guide infographic |
| Travel / Places / Culture | 4 | 7% | Consumption-oriented | remote destination, unique cultural experiences |

**Orientation breakdown:**

| Orientation | Queries | Share | Typical query types |
|---|---|---|---|
| Consumption-oriented | 25 | 43% | Browsing, fan content, lifestyle, travel, nature |
| Creation-oriented | 26 | 45% | Printables, posters, flashcards, design templates |
| Mixed | 7 | 12% | Recipe inspiration, MBTI charts, maps |

The query set intentionally skews slightly creation-oriented (45% vs 43%). This is by design: the pilot was constructed to stress-test how platforms handle users who want to *make* something, not just *look* at something. Consumer-browsing queries serve as a recall baseline — verifying that optimizing for creation intent doesn't degrade basic visual coverage.

**Vocabulary & Language (12 queries, 21%)** is the largest single category. Nearly all queries explicitly seek printable or educational materials. **Character / IP (11 queries, 19%)** is the largest consumption-oriented category — fan and lifestyle queries where users browse rather than create.

---

## 4. Consumption vs. Creation Analysis

### The Core Spectrum

The most useful framing for comparing these five platforms is a consumption-to-creation spectrum:

```
Consumption-oriented ◄────────────────────────────► Creation-oriented

  Google Images   Bing Images   Pinterest   Curify   Canva
```

| Category | Platforms | What they do |
|---|---|---|
| Consumption baseline | Google Images, Bing Images | Measure broad visual recall; reveal what users expect to *see* for a query |
| Discovery / inspiration | Pinterest | Surface sub-intent label chips and visual clusters; bridge browsing to creation |
| Creation-first | Curify, Canva | Template-first results; users expect to *make* something, not just view it |

### Why Google and Bing Are the Consumption Baseline

Google Images and Bing Images index the open web. Their results reflect what users broadly expect to *see* when they enter a query — photographs, editorial images, web screenshots. They do not curate for creative use; they optimize for visual recall and relevance. For this pilot, they serve as the coverage floor: if a platform returns zero results for a query that Google returns ten rich results for, that indicates a fundamental content or routing gap.

### Why Pinterest Bridges the Middle

Pinterest serves consumers (browsing, saving, building boards), but a significant share of pins are tutorials, templates, infographics, and step-by-step guides. Pinterest's One Bar sub-intent label chips — when available — reveal how users subdivide a broad query in practice, making it the most informative external signal for intent decomposition. Its position in the middle of the spectrum reflects this dual role: strong on visual inspiration, partial on creation routing.

### Why Canva and Curify Anchor the Creation End

Canva's entire product is template search. Its results are things users can generate and export — not images to look at. Curify follows the same template-first model. The key difference between the two: Canva covers English queries well but blocks CJK queries behind a login wall. Curify has no login barrier for any query.

### Orientation by Query Type

This pilot's query set is intentionally weighted toward creation-oriented queries. Consumer queries (fan content, lifestyle, travel, nature) are well-served by every platform in this pilot. Creation-oriented queries — educational printables, recipe posters, design templates — show the sharpest differentiation between platforms, and represent the highest-value use case for template-first search.

---

## 5. Platform Star Rating Table

Ratings across 5 dimensions, based on observed behavior across the 58-query pilot:

| Platform | Broad Recall | Creative / Template Orientation | Visual Diversity | Intent Label Clarity | Actionability for Creators |
|---|---|---|---|---|---|
| **Google Images** | ★★★★★ | ★★☆☆☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| **Bing Images** | ★★★★★ | ★★☆☆☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| **Pinterest** | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ | ★★★★☆ |
| **Curify** | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| **Canva** | ★★☆☆☆ | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★★★ |

**Dimension definitions (1–5 stars):**

- **Broad Recall** — Does the platform return results for the full query range, including CJK and niche creative topics, without login barriers?
- **Creative / Template Orientation** — Does the platform surface templates, printables, and generatable content rather than open-web images?
- **Visual Diversity** — Do results span multiple styles, formats, and use cases within a single query?
- **Intent Label Clarity** — Does the platform provide label chips, sub-categories, or filters that clarify and refine user intent?
- **Actionability for Creators** — Can users move from search result directly to something they can generate or adapt?

---

## 6. Platform Insights

### Google Images

**Strengths:** Perfect broad recall — 58/58 queries returned full results, no login barrier, no CJK block. Related-search label chips (average 17.8 per query) reveal standard sub-categories users associate with each query and serve as high-quality external taxonomy seeds. Example: `phonics worksheets kindergarten` → chips: Free Printable, 1st Grade, Beginning Sounds, Reading Comprehension, Alphabet.

**Best for:** Understanding the semantic range of a query; identifying which sub-topics users associate with a given search term; consumer-browsing baseline.

**Limitation:** Entirely open-web images — no template routing, no creation surface.

[Image placeholder: Google Images — "ESL flashcards printable" showing label chip bar and top results]

---

### Bing Images

**Strengths:** Broad recall matches Google (58/58 queries). Related-search label chips average **39.9 per query** — the highest of any platform in this pilot, and 2.2× Google's average. Chips are structured noun-phrase sub-categories rather than raw keyword suggestions, making them directly usable for taxonomy mapping. Example: `maps` → 40 label chips including World Map, Old Map, Map Art, Antique Map, Kids Map, Map of the USA. No query returned zero label chips.

**Best for:** Query taxonomy and sub-category mapping; alias and topic expansion; understanding the full category space around a query.

**Limitation:** Creation-oriented results no different from Google — open-web images with no template routing.

[Image placeholder: Bing Images — "ESL flashcards printable" showing label chip bar (39.9 avg)]

---

### Pinterest

**Strengths:** Full results for all 58 queries. Highest visual diversity of any platform — results for any query span a wider range of styles, formats, and use cases. Pinterest's **One Bar sub-intent label chips** are qualitatively distinct from Bing's taxonomy chips: they reveal how users specifically subdivide a query, not just what broad categories surround it. Among queries with label chips (36/58, 62%), the average was **19.9 label chips per query**. CJK query label chip coverage is particularly strong — short Chinese phrases like `香薰` and `植物` generate rich product/scene sub-intent chips that Canva (blocked) cannot provide.

**Example label chips:**

| Query | Pinterest label chips |
|---|---|
| `monstera plant care guide infographic` | Indoor, Swiss cheese, Adansonii, Thai constellation, Moss pole |
| `easy weeknight dinners healthy` | High protein, Low carb, Kid friendly, Gluten free, Clean eating |
| `samurai` | Tattoo, Japanese art, Pfp, Mask, Outfit, Wallpaper 4k |
| `香薰` | 包装, 氛围图, 新中式, 观夏, 祖马龙, 礼盒 |

**Best for:** Visual diversity and inspiration; sub-intent discovery; CJK query sub-intent signals.

**Limitation:** 22/58 queries had no label chips after manual verification — Pinterest itself does not generate One Bar chips for these queries (mainly niche English creation-oriented queries and some CJK short phrases). Label chip data is not reproducible at scale by automation.

[Image placeholder: Pinterest — "monstera plant care guide infographic" showing One Bar label chip row and pin grid]

---

### Canva

**Strengths:** Most direct external benchmark for creation-oriented English query handling — Canva is, like Curify, a template-first platform. For accessible queries (36/58), results are templates with an average of **43 label chips per accessible query** covering Format, Style, Size, Color, and Audience. These chips are explicit output-type signals (Presentation, Instagram Post, Worksheet, Infographic) — the clearest external signal for what types of creative output users expect for a given English query.

**Best for:** Benchmarking English creation-oriented query handling; understanding template category expectations; creative intent taxonomy for English queries.

**Limitation:** 21/58 queries (36%) blocked by login wall — all CJK queries and Japanese pop-culture queries. Not usable as a reference for CJK creative query handling.

[Image placeholder: Canva — "phonics worksheets kindergarten" showing template grid with Format/Style label chips]

---

### Curify

**Strengths:** Template-first with no login barrier for any query, including CJK. Returned results for 54/58 queries in the baseline collection period. Curify's **8-cluster intent label chip system** groups results by semantic sub-topic, enabling structured navigation within a query. Strong performance on Vocabulary & Language queries (12/12 with results) and Character / IP queries (11/11 with results), including bilingual flashcards, ESL printables, and fan/character content.

**Best for:** Template discovery with CJK support; educational and character/IP queries; queries where the user wants to generate, not just browse.

**Note on template coverage:** Food & Recipe and niche design queries showed thinner template coverage compared to Canva and Pinterest in this pilot — an identified growth area.

[Image placeholder: Curify — "ESL flashcards printable" showing template cards + 8-cluster intent label chip navigation]

---

## 7. Cross-Platform Insights

### 7.1 Best Platform by Signal Need

| Signal Need | Best Platform | Second Choice | Notes |
|---|---|---|---|
| Broad visual recall baseline | Google Images | Bing Images | Coverage floor — if a platform can't match Google, it's a fundamental gap |
| Query taxonomy / sub-category mapping | Bing Images | Google Images | Bing's 39.9 label chips/query is the richest structured taxonomy vocabulary |
| User-level sub-intent discovery | Pinterest (manual label chips) | Bing Images | Pinterest One Bar chips show how users decompose a query — qualitatively finer than Bing's category labels |
| Visual inspiration clusters | Pinterest | Google Images | Highest visual diversity per query; rich style and use-case variety |
| Template / creation intent (English) | Canva | Pinterest | Canva results are directly comparable to template-first search outputs |
| CJK query semantic signals | Pinterest (manual chips) + Google | Bing Images | Canva unavailable for CJK; Pinterest CJK chip coverage: 21/28 consumer-oriented queries |
| Content gap detection | Canva + Google | — | If Canva has 10 templates and a platform has 0–4, that is a clear creation-intent gap |

### 7.2 Consumption-to-Creation Spectrum

```
Consumption-oriented ◄────────────────────────────► Creation-oriented

  Google Images   Bing Images   Pinterest   Curify   Canva
       ★★★★★           ★★★★★        ★★★★       ★★★★      ★★★★★
```

- **Google and Bing** lock the consumption end. Their value is recall completeness and category breadth. They tell you what a query *means* to users — not what users want to *make* with it.

- **Pinterest** spans the middle. It is consumption-facing (browse and save) but is adjacent to creation — a large share of pins are tutorials, templates, and step-by-step guides. Manually verified One Bar label chips make it the most complete "inspiration → sub-intent → creation" signal in this pilot.

- **Curify and Canva** lock the creation end. Both are template-first. The shared gap is consumer-oriented recall — neither competes with Google or Bing on broad visual browsing. Their distinction from each other: Canva has deeper English template coverage and Curify has broader CJK query support without login barriers.

### 7.3 Diversity Analysis

| Platform | Diversity type | Rating | Notes |
|---|---|---|---|
| Google Images | Semantic breadth | ★★★★★ | Covers the widest range of query interpretations per query |
| Pinterest | Visual style breadth | ★★★★★ | Broadest aesthetic and format variety per query; One Bar label chips further structure sub-intent |
| Bing Images | Category depth | ★★★★☆ | Richest sub-category label chips; slightly narrower visual style range than Google |
| Curify | Template format diversity | ★★★☆☆ | 8-cluster chip system supports good categorical diversity; visual style range within clusters is narrower |
| Canva | Output type diversity | ★★★☆☆ | Clear output-type taxonomy (worksheet, poster, infographic); style variety is narrower than Pinterest or Google |

**Key observation:** Google and Pinterest are complementary diversity signals. Google provides the widest *semantic* interpretation of a query (what it can mean). Pinterest provides the widest *visual style* variety (how it can look). For query taxonomy work, using both together provides a more complete picture than either alone.

### 7.4 Intent / Label Clarity

| Platform | Label chip source | Avg label chips/query | Notes |
|---|---|---|---|
| Bing Images | Related-search label chips | **39.9** | Richest structured taxonomy; 100% query coverage; noun-phrase sub-categories |
| Canva | Template category filter chips | **43** (accessible queries only) | Explicit output-type signals; 21/58 queries inaccessible |
| Google Images | Related-search label chips | **17.8** | High quality; fewer than Bing; good semantic sub-category coverage |
| Pinterest | One Bar sub-intent label chips (manual) | **12.4** overall / **19.9** (queries with chips) | Highest chip quality — user-level sub-intent decomposition; 22/58 queries have no chips by design |
| Curify | 8-cluster intent label chips | **8.8** | Result-specific clusters reflecting actual catalog content; narrower vocabulary than Bing but higher semantic precision for in-platform navigation |

**Reading the label chip gap carefully:**

The chip count gap (Bing 39.9 vs Curify 8.8) should not be read as a simple ranking. Bing's 40 label chips per query are web-wide sub-category suggestions generated for every query. Canva's 43 chips are a fixed platform-level filter panel (Format × Style × Color × Size × Audience) that appears regardless of the specific query. Neither number directly measures how well the platform understands the query.

Curify's 8.8 intent label chips are result-specific clusters — they reflect what the platform's own catalog actually contains for that query, clustered into a semantic intent taxonomy. Fewer chips means narrower catalog coverage, not less intent clarity. The direction for expanding this number is deeper catalog coverage, not padding the chip count.

Pinterest's sub-intent label chips are qualitatively different from both: they are not category labels or filter panels, but user-observed sub-intents that reflect how real users refine a query. A Pinterest chip like `Thai constellation` on a monstera query means users are actively filtering for that specific variety — a signal that neither Bing's category taxonomy nor Canva's output-type filters would surface.

---

## Limitations of This Pilot

- **58 queries is a small set.** Vocabulary & Language is overrepresented at 21%; Food & Recipes (10%) and Travel (7%) are underrepresented. Findings are directional — not statistically robust.
- **Data is a point-in-time snapshot** collected in June 2026. Platform behavior, label chip availability, and login requirements may differ at other times.
- **Pinterest label chip data** for this pilot was manually collected for 36 of 58 queries, as automated collection was intercepted by Pinterest's login modal. This data is not reproducible at scale by automated means; sessions at different times may yield different chip sets.
- **Canva's CJK coverage gap** means this pilot has limited external signal for how creation-oriented CJK queries are handled by template platforms.
- **Star ratings are qualitative judgments**, not statistically derived scores, based on observed behavior across the 58-query set.

---

## Image TODO

> *Local assets collected — CDN upload pending before publication.*
> *Asset folder: `docs/daily_report/6.30/curify-blog-linkedin-wrapup-2026-06-30/assets/esl_flashcards_printable/`*

| Section | Image needed | Query | Platform | Local asset | CDN status |
|---|---|---|---|---|---|
| §6 Google Images | Label chip bar + top results | ESL flashcards printable | Google Images | `assets/esl_flashcards_printable/google_esl_flashcards_printable.png` | Not uploaded |
| §6 Bing Images | Label chip bar showing 39.9-chip depth | ESL flashcards printable | Bing Images | `assets/esl_flashcards_printable/bing_esl_flashcards_printable.png` | Not uploaded |
| §6 Pinterest | One Bar label chip row + pin grid | ESL flashcards printable | Pinterest | `assets/esl_flashcards_printable/pinterest_esl_flashcards_printable.png` | Not uploaded |
| §6 Canva | Template grid with Format/Style label chips | ESL flashcards printable | Canva | `assets/esl_flashcards_printable/canva_esl_flashcards_printable.png` | Not uploaded |
| §6 Curify | Template result grid + 8-cluster label chips | ESL flashcards printable | Curify | `assets/esl_flashcards_printable/curify_esl_flashcards_printable_results.png` | Not uploaded |
| §6 Curify (generation) | Search-to-generation path | ESL flashcards printable | Curify | `assets/esl_flashcards_printable/curify_esl_flashcards_printable_generate.png` | Not uploaded — optional |
| §6 Pinterest (monstera) | One Bar label chip row + pin grid | monstera plant care guide infographic | Pinterest | Not yet collected | Not uploaded |
| §7.2 Spectrum | Optional side-by-side comparison | any single query | All 5 platforms | Not yet collected | Not uploaded |

---

*Pilot data collected June 2026 (Google Images, Bing Images, Pinterest, Canva). 58 queries × 5 platforms. Qualitative + semi-quantitative analysis.*
