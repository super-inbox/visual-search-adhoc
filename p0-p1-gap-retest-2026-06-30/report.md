# P0/P1 Gap Retest — 2026-06-30

**Branch:** `baobao/multi-intent-topic-cooccurrence`  
**Eval set:** `scripts/configs/search_eval_set.json` (125 queries)  
**Run command:** `node scripts/eval_search.cjs --quiet`  
**Overall:** PASS=101, WARN=24, FAIL=0

---

## Gap Classification Key

| Code | Meaning | Fix path |
|------|---------|----------|
| **c1** | Content exists but search/recall does not surface it | Alias top-up or tokenizer fix |
| **c2** | Template exists, but content generation is needed | Batch-gen a `scripts/configs/<theme>_<date>.json` |
| **c3** | No suitable template/content — template discovery needed | New template proposal |

---

## P0 — Still Empty (7 queries)

These queries returned 0 hits against the current catalog.

| Query | Hits | Relevant content exists? | Template exists? | Gap type | Suggested action |
|-------|------|--------------------------|------------------|----------|-----------------|
| `水果中文` | 0 | Yes (13 zh-fruits items) | Yes (`template-vocabulary`) | **c1** | Add `水果中文`, `中文水果` as direct aliases on en-zh fruit vocabulary items. Root cause: bigram path generates `水果`/`果中`/`中文` but no single inspiration blob contains BOTH `水果` AND `中文`, so the 2-of-3 threshold is never met. |
| `unique cultural experiences` | 0 | No | No | **c3** | Template discovery needed. Concept is too abstract for current catalog. Possible anchor: a destination-experience or cultural-guide template. File as new template proposal. |
| `minimalist autumn outfit for japan travel` | 0 | No | Yes (`template-fashion-ecommerce`, `template-fashion-before-after-outfit-annotation-card`, `template-wc-fan-outfit-poster`) | **c2** | Batch-gen: `template-fashion-ecommerce` with params `{style: "minimalist", season: "autumn", destination: "japan"}`. |
| `infj vs entp dating compatibility chart` | 0 | No | Yes (`template-mbti-relationship-infographic`, `template-mbti-comparison-infographic`, `template-mbti-personality-compatibility-infographic`) | **c2** | Batch-gen: `template-mbti-relationship-infographic` with `{type_a: "INFJ", type_b: "ENTP", topic: "dating compatibility"}`. |
| `easy weeknight dinners healthy` | 0 | No | Yes (`template-recipe`, `template-premium-recipe-card-infographic`, `template-food-recipe-tip-infographic`) | **c2** | Batch-gen: `template-recipe` with weeknight/healthy dinner params. Also add `weeknight`, `healthy` aliases to existing recipe items. |
| `gluten free dinner ideas` | 0 | No | Yes (`template-recipe`, `template-premium-recipe-card-infographic`) | **c2** | Batch-gen: `template-recipe` with gluten-free dinner params; add `gluten free`, `gluten-free` alias family. |
| `meal prep weekly recipes` | 0 | No | Yes (`template-recipe`, `template-food-recipe-tip-infographic`) | **c2** | Batch-gen: `template-recipe` with meal-prep/weekly params; add `meal prep`, `weekly meal`, `batch cooking` aliases. Note: `recipes` (plural) also misses `recipe` (singular) in strict path — secondary tokenizer issue. |

---

## P1 — Still Thin (10 queries)

These queries returned 1–2 hits, below their expected baseline.

| Query | Hits | Expected | Relevant content exists? | Template exists? | Gap type | Suggested action |
|-------|------|----------|--------------------------|------------------|----------|-----------------|
| `cozy reading aesthetic` | 1 | thin (at baseline) | Marginally (1 relaxed via cozy-winter-tea watercolor) | Yes (`template-book-recommendation-grid-poster`, `template-lifestyle-watercolor-infographic`) | **c2** | Batch-gen: `template-lifestyle-watercolor-infographic` with `{theme: "cozy reading corner"}`. Adds dedicated reading-aesthetic examples. |
| `cuban sandwich recipe poster` | 1 | rich | Yes (1 exact match: `template-food-cuban-sandwich`) | Yes (`template-food`, `template-recipe`) | **c2** | 62 food inspirations exist but only 1 is Cuban sandwich. Batch-gen more food poster variants (sandwich series: philly cheesesteak, reuben, banh mi) so relaxed-match pool grows. Expected `rich` requires 10+ items. |
| `bilingual flashcards for kids learning korean fruits` | 1 | rich | Yes (1 exact match: `template-vocabulary-english-korean-fruits`) | Yes (`template-vocabulary`, `template-kids-vocabulary-poster`) | **c2** | 169 vocab inspirations exist but only 1 en-ko-fruits item has all 6 tokens. Batch-gen more en-ko vocab sets (vegetables, animals, colors, body parts) so sibling items reach strict threshold via bilingual/flashcards/kids aliases they already carry. |
| `watercolor map of europe travel destinations` | 1 | moderate | Yes (1 exact: `template-watercolor-world-map-illustration-europe`) | Yes (`template-watercolor-world-map-illustration`) | **c2** | 7 watercolor world map inspirations; only the Europe one has `destinations` alias. Batch-gen more regional watercolor maps (Asia, North America, Latin America) with `travel destinations` aliases. |
| `before after kitchen organization makeover` | 2 | moderate | Yes (2 kitchen before-after items) | Yes (`template-home-organization-before-after`) | **c2** | 5 before-after inspirations, 2 are kitchen. Need more room variants (living room, bathroom, closet, office) with `makeover` alias. Batch-gen 3+ new before-after organization items. |
| `paris travel itinerary` | 2 | rich | Yes (2 paris items with itinerary context) | Yes (`template-tourist-spot-watercolor-map-infographic`, `template-city-miniature`) | **c2** | 2 Paris-specific inspirations. Need more city travel itinerary content. Batch-gen: `template-tourist-spot-watercolor-map-infographic` for other Paris neighborhoods/routes, or add `itinerary` alias to broader Paris travel items. |
| `architecture empire state building` | 1 | rich | Yes (1 exact: `template-architecture-empire-state-building`) | Yes (`template-architecture`) | **c2** | 4 architecture inspirations. Only 1 ESB. Batch-gen: more landmark architecture cards (Eiffel Tower, Colosseum, Big Ben, Sagrada Familia). |
| `childhood snacks then vs now` | 1 | rich | Yes (1 exact: `template-then-vs-now-comparison-infographic-childhood-snacks`) | Yes (`template-then-vs-now`) | **c2** | 7 then-vs-now inspirations; only 1 has `childhood snacks`. Batch-gen more comparison topics: tech gadgets, fashion styles, music formats, school life. |
| `warmup routine running checklist` | 1 | rich | Yes (1 exact: `template-warmup-routine-running`) | Yes (`template-warmup-routine`) | **c2** | 7 warmup-routine inspirations; only the running one has `checklist` in its aliases. Add `checklist` alias to gym, yoga, cycling, swimming variants (c1 fix); and/or batch-gen more running-specific warmup variants (5K, trail run, sprint). |
| `vintage stamp collection garden birds` | 1 | rich | Yes (1 exact: `template-vintage-stamp-collection-illustration-garden-birds`) | Yes (`template-vintage-stamp-collection-illustration`) | **c2** | 5 vintage stamp inspirations; only 1 is garden birds. Batch-gen more stamp collection topics: ocean life, butterflies, autumn foliage, wildflowers. |

---

## Resolved Since Last Calibration — Baseline Updates Needed (15 queries)

These are WARN queries that **improved beyond their documented baseline** — they are not gaps; the eval set `expected` field should be updated.

| Query | Old expected | Current hits | New bucket | Notes |
|-------|-------------|-------------|-----------|-------|
| `lunar new year red envelope graphic design` | empty | 8 | moderate | Red envelope alias batch + graphic design aliases shipped ✅ |
| `phonics worksheets kindergarten` | empty | 50 | rich | Phonics template + alias top-up shipped ✅ |
| `ESL flashcards printable` | empty | 4 | moderate | Flashcard/printable aliases shipped ✅ |
| `book lovers gift guide` | thin | 7 | moderate | Book lovers + gift alias top-up shipped ✅ |
| `chiikawa` | moderate | 13 | rich | Chiikawa fandom batch shipped ✅ |
| `England 1966 World Cup` | thin | 5 | moderate | WC historical content shipped ✅ |
| `Brazil 2002 squad` | thin | 4 | moderate | WC historical content shipped ✅ |
| `Maradona Hand of God` | moderate | 11 | rich | WC content + alias batch shipped ✅ |
| `most memorable World Cup moments` | moderate | 10 | rich | WC moments content shipped ✅ |
| `watercolor travel journal collage` | moderate | 14 | rich | Travel journal batch shipped ✅ |
| `france 2026 world cup` | moderate | 32 | rich | France WC content shipped ✅ |
| `brazil 2026 national team` | thin | 27 | rich | Brazil national team content shipped ✅ |
| `brazil national team` | moderate | 33 | rich | Brazil team content shipped ✅ |
| `england football` | moderate | 15 | rich | England football content shipped ✅ |
| `brazil world cup squad poster` | moderate | 30 | rich | Brazil squad poster content shipped ✅ |

---

## Summary by Gap Type

| Gap type | Count | Queries |
|----------|-------|---------|
| **c1** (search/alias fix) | 2 | `水果中文`, `warmup routine running checklist` (alias sub-fix) |
| **c2** (content generation) | 14 | all recipe/food/vocab/map/architecture/template-thin gaps |
| **c3** (template discovery) | 1 | `unique cultural experiences` |
| **Resolved / baseline outdated** | 15 | see table above |

---

## Priority Action Items

**Immediate c1 fixes (no content gen cost):**
1. Add `水果中文`, `中文水果` aliases to `template-vocabulary-english-chinese-*` fruit items
2. Add `checklist` standalone alias to non-running warmup-routine items (gym, yoga, cycling)

**Batch-gen c2 queue (in priority order):**
1. Recipe family: weeknight healthy dinners, gluten-free, meal prep (3 new JSON configs)
2. Architecture landmarks: 5+ more landmark buildings (Eiffel, Colosseum, Big Ben…)
3. Food poster series: sandwich/street-food variants to lift `cuban sandwich` relaxed pool
4. Vocabulary en-ko series: vegetables, animals, colors, body parts (lift bilingual flashcards pool)
5. Then-vs-now comparison topics: tech, fashion, music, school (lift childhood snacks pool)
6. Vintage stamp topics: ocean life, butterflies, wildflowers (lift garden birds pool)
7. Warmup routine variants: 5K running, trail, sprint checklists
8. Paris travel itinerary: neighborhood/route variations
9. Watercolor world maps: Asia, North America, Latin America with `destinations` alias
10. Before-after room organization: living room, bathroom, closet with `makeover` alias

**c3 template proposal:**
- `unique cultural experiences`: propose new template covering cultural-guide or destination-experience card

---

*Generated 2026-06-30 · eval script: `scripts/eval_search.cjs` · data: `public/data/nano_inspiration.json`*
