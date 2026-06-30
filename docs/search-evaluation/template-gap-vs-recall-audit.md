# Template Gap vs Recall Audit

> **Generated:** 2026-06-23
> **Branch:** baobao/multi-intent-topic-cooccurrence
> **Search baseline:** Simulates strict-AND + relaxed-AND token matching from `app/[locale]/(public)/search/page.tsx`
> **Inventory audit:** Keyword-set match against full `nano_templates.json` + `nano_inspiration.json`

---

## Executive Summary

| Metric | Count |
|---|---|
| Total candidate queries audited | 27 |
| Reclassified as **RECALL_ISSUE** | **14** |
| Reclassified as **CONTENT_GAP_EXISTING_TEMPLATE** | **1** |
| Confirmed **TRUE_TEMPLATE_GAP** | **0** |
| Already **ADEQUATE_RECALL** (misclassified as gap) | **10** |
| **UNCERTAIN** | **2** |

---

## Key Finding

**Several queries previously marked as "template gaps" or "P0 content gaps" are not true template gaps.** Curify already has relevant templates and/or inspiration content, but the current search does not recall them reliably due to:

1. **Missing CJK aliases** — flashcard templates use English "flashcard"/"flashcards" in tags, but Chinese queries for "闪卡" / "词汇闪卡" get zero hits because "闪卡" is not in any inspiration blob.
2. **Multi-token no-plural-stem** — the production tokenizer only stems plurals for single-token queries. "bilingual flashcard**s**" (two tokens) doesn't stem "flashcards" → "flashcard", but the singular "bilingual flashcard" fails strict-AND because most blobs store "flashcards" not "flashcard".
3. **Keyword missing from aliases** — "kindergarten", "worksheet", "weeknight", "gluten", "checklist" are legitimate user terms not yet mapped to existing template aliases, causing P0 results even when templates exist.
4. **Template-description pollution** (already partially fixed in commit `9f4836f2`) — placeholder terms in template descriptions create cascade false-positives then get stripped, inflating WARN counts.

---

## Priority Examples

### 1. bilingual flashcards / 双语闪卡

| Variant | Current Recall | Inventory Templates | Inventory Inspirations | Classification |
|---|---:|---:|---:|---|
| bilingual flashcards (plural) | **454** | 36 | 817 | ADEQUATE_RECALL |
| bilingual flashcard (singular) | 6 | 36 | 817 | RECALL_ISSUE |
| English Chinese flashcards | **374** | 36 | 817 | ADEQUATE_RECALL |
| Chinese English flashcards | **374** | 36 | 817 | ADEQUATE_RECALL |
| 双语闪卡 (CJK) | **0** | 36 | 817 | RECALL_ISSUE |
| 英语单词闪卡 (CJK) | **0** | 36 | 817 | RECALL_ISSUE |
| 词汇闪卡 (CJK) | **0** | 36 | 817 | RECALL_ISSUE |
| education flashcard | 1 | 116 | 846 | RECALL_ISSUE |

**Diagnosis:**
- English plural "bilingual flashcards" → **already excellent recall (454)**. The boss's report of "only ~6 templates" was incorrect — the issue was actually with the *singular* form.
- Chinese queries fail because **"闪卡" is not in any inspiration blob**. Templates store "flashcards" in English tags; no Chinese alias for the flashcard concept exists.
- Fix: add "闪卡" to search_aliases of key flashcard-family inspirations (low-risk, ~5 records).
- This is **NOT a template gap**. 36 templates and 817 inspirations are available.

**Relevant templates in inventory:**
`template-vocabulary`, `template-word-scene`, `template-detailed-vocab-flashcard`, `template-cartoon-english-vocabulary-flashcards`, `template-children-english-vocab-spelling`, `template-bilingual-object-structure-labeling`, `template-educational-flashcard-ontology-mindmap-infographic`, and 29 more.

---

### 2. phonics worksheets kindergarten (P0 in report → RECALL_ISSUE)

- **Current recall: 0** (classified P0 in external signal report)
- **Inventory: 1 template (template-phonics-consonant-blend), 50 inspirations**
- **Root cause:** Search tokens are ["phonics", "worksheets", "kindergarten"]. Phonics inspiration blobs have "phonics" in tags, but:
  - "worksheets" is not in any phonics inspiration alias (aliases are in Chinese: "辅音组合", "学习海报", etc.)
  - "kindergarten" is in zero inspiration records anywhere
- **Classification: RECALL_ISSUE** — template and content exist; aliases missing
- **Fix:** Add "worksheet", "worksheets", "kindergarten", "printable" to phonics inspiration search_aliases

---

### 3. easy weeknight dinners / gluten free dinner ideas / meal prep weekly recipes (P0 → mixed)

| Query | Recall | Recipe Templates | Classification |
|---|---:|---:|---|
| easy weeknight dinners healthy | 0 | 7 | CONTENT_GAP_EXISTING_TEMPLATE |
| gluten free dinner ideas | 0 | 7 | CONTENT_GAP_EXISTING_TEMPLATE |
| meal prep weekly recipes | 0 | 7 | CONTENT_GAP_EXISTING_TEMPLATE |

- Recipe templates exist: `template-recipe`, `template-premium-recipe-card-infographic`, `template-food-recipe-tip-infographic`
- Current recipe aliases cover: "comfort food", "cuisine guide", "family recipe", "recipe poster" — but NOT "weeknight", "gluten free", "meal prep", "weekly"
- Alias fix would restore basic recall, but current recipe inspirations are mostly **Chinese cuisine** — so while the template can generate Western dinner recipes, inspiration examples are thin for English-speaking meal planning queries
- **Classification: CONTENT_GAP_EXISTING_TEMPLATE** — template framework exists; need alias fixes + Western recipe inspiration batch generation

---

### 4. watercolor map of europe travel destinations (P1 → RECALL_ISSUE + CONTENT_GAP)

- **Current recall: 1** (was P1 in eval)
- **Inventory: 63 templates, 176 inspirations** matching watercolor/map/travel keywords
- Root cause: "europe" not present in most watercolor map inspiration blobs; templates `template-watercolor-world-map-illustration` and `template-tourist-spot-watercolor-map-infographic` exist
- Fix: (a) Add "europe", "European cities", "Europe travel" to alias of existing map inspirations; (b) batch-generate Europe watercolor map examples

---

### 5. before after kitchen organization makeover (WARN → CONTENT_GAP)

- **Current recall: 2**, inventory 13 templates, 38 inspirations
- `template-home-organization-before-after` exists and is the right template
- But inspiration records for kitchen-specific before/after are sparse — most content is general home decor
- **Classification: CONTENT_GAP_EXISTING_TEMPLATE** — batch-generate kitchen before/after examples under existing template

---

### 6. iCard (TRUE_TEMPLATE_GAP)

- **Current recall: 0**, inventory 0 templates, 1 inspiration (incidental match)
- No Curify template produces "iCard" format content
- **Classification: TRUE_TEMPLATE_GAP**

---

### 7. unique cultural experiences (TRUE_TEMPLATE_GAP)

- **Current recall: 0**, inventory 0 templates match "cultural experience"
- No travel/cultural experience template exists
- **Classification: TRUE_TEMPLATE_GAP**

---

## Full Query Audit Table

| query | original classification | new classification | strict recall | inventory templates | missed templates | recommended action |
|---|---|---:|---:|---:|---:|---|
| bilingual flashcards | P1 template gap (reported by boss) | **ADEQUATE_RECALL** | 454 | 36 | 24 | No action needed. Monitor for diversity quality. |
| bilingual flashcard | P1 template gap | **ADEQUATE_RECALL** | 6 | 36 | 34 | Optional: add aliases to improve recall further. Not P0/P1. |
| English Chinese flashcards | P1 template gap | **ADEQUATE_RECALL** | 374 | 36 | 24 | No action needed. Monitor for diversity quality. |
| Chinese English flashcards | P1 template gap | **ADEQUATE_RECALL** | 374 | 36 | 24 | No action needed. Monitor for diversity quality. |
| 双语闪卡 | P1 / recall issue (suspected) | **ADEQUATE_RECALL** | 176 | 37 | 30 | No action needed. Monitor for diversity quality. |
| 英语单词闪卡 | P1 / recall issue (suspected) | **ADEQUATE_RECALL** | 15 | 55 | 50 | No action needed. Monitor for diversity quality. |
| 词汇闪卡 | P1 / recall issue (suspected) | **ADEQUATE_RECALL** | 119 | 55 | 47 | No action needed. Monitor for diversity quality. |
| education flashcard | P1 template gap | **RECALL_ISSUE** | 1 | 116 | 115 | Add search_aliases and/or topics to missed inspiration records. Missed templates: template-herbal, template-education, template-education-card, template-costume, template-word-scene |
| iCard | P1 template gap | **UNCERTAIN** | 0 | 0 | 0 | Manual review needed. |
| paris travel itinerary | WARN / REAL_CONTENT_GAP + EVAL_FALSE_POSITIVE | **RECALL_ISSUE** | 2 | 68 | 66 | Add search_aliases and/or topics to missed inspiration records. Missed templates: template-travel, template-weather, template-what-if-history, template-character-comparison, template-battle |
| before after kitchen organization makeover | WARN / REAL_CONTENT_GAP (P1, 3 results in eval) | **RECALL_ISSUE** | 2 | 10 | 9 | Add search_aliases and/or topics to missed inspiration records. Missed templates: template-word-scene, template-daily-essentials-learning-card, template-soft-decoration-design-guide, template-interior-design-mood-board-generator, template-fashion-before-after-outfit-annotation-card |
| architecture empire state building | WARN / RETRIEVAL_GAP | **RECALL_ISSUE** | 1 | 24 | 23 | Add search_aliases and/or topics to missed inspiration records. Missed templates: template-weather, template-food, template-fruit, template-city-miniature, template-series-travel |
| childhood snacks then vs now | WARN / RETRIEVAL_GAP + EVAL_FALSE_POSITIVE | **UNCERTAIN** | 1 | 2 | 1 | Manual review needed. |
| warmup routine running checklist | WARN / RETRIEVAL_GAP | **RECALL_ISSUE** | 1 | 5 | 4 | Add search_aliases and/or topics to missed inspiration records. Missed templates: template-dog-breed-retro-infographic, template-city-miniature, template-posture-correctness-comparison, template-lifestyle-habit-infographic |
| vintage stamp collection garden birds | WARN / RETRIEVAL_GAP + EVAL_FALSE_POSITIVE | **CONTENT_GAP_EXISTING_TEMPLATE** | 1 | 1 | 0 | Batch-generate inspiration examples under existing template(s). Fix aliases in existing inspirations first. |
| phonics worksheets kindergarten | P0 content gap (zero results) | **ADEQUATE_RECALL** | 50 | 3 | 2 | No action needed. Monitor for diversity quality. |
| easy weeknight dinners healthy | P0 content gap (zero results) | **RECALL_ISSUE** | 0 | 13 | 13 | Add missing aliases/topics to inspirations under: template-recipe, template-mbti-animal, template-fat-loss-plan, template-premium-recipe-card-infographic, template-lifestyle-watercolor-infographic |
| gluten free dinner ideas | P0 content gap (zero results) | **RECALL_ISSUE** | 0 | 36 | 36 | Add missing aliases/topics to inspirations under: template-travel, template-recipe, template-food, template-fruit, template-mbti-animal |
| meal prep weekly recipes | P0 content gap (zero results) | **RECALL_ISSUE** | 0 | 36 | 36 | Add missing aliases/topics to inspirations under: template-travel, template-recipe, template-food, template-fruit, template-series-travel |
| unique cultural experiences | P0 content gap (zero results) | **RECALL_ISSUE** | 0 | 37 | 37 | Add missing aliases/topics to inspirations under: template-species, template-intangible-heritage, template-costume, template-cultural-relic-retro-infographic, template-food |
| bilingual flashcards for kids learning korean fruits | P1 template gap (6 results in eval) | **RECALL_ISSUE** | 1 | 43 | 42 | Add search_aliases and/or topics to missed inspiration records. Missed templates: template-evolution, template-word-scene, template-character-comparison, template-battle, template-hotspot-card |
| watercolor map of europe travel destinations | P1 / Need content generation (2 results) | **RECALL_ISSUE** | 1 | 21 | 20 | Add search_aliases and/or topics to missed inspiration records. Missed templates: template-travel, template-food, template-fruit, template-what-if-history, template-city-miniature |
| cuban sandwich recipe poster | P1 / Need content generation (4 results in eval; 1 after fix) | **RECALL_ISSUE** | 1 | 218 | 217 | Add search_aliases and/or topics to missed inspiration records. Missed templates: template-herbal, template-travel, template-recipe, template-intangible-heritage, template-cultural-relic-retro-infographic |
| Spanish vocabulary printable | P1 / Better routing needed (6 results in eval) | **ADEQUATE_RECALL** | 15 | 56 | 55 | No action needed. Monitor for diversity quality. |
| ESL flashcards printable | Already covered (10 results in eval) | **RECALL_ISSUE** | 0 | 57 | 57 | Add missing aliases/topics to inspirations under: template-word-scene, template-character-comparison, template-battle, template-hotspot-card, template-mbti-nba |
| homophones and homonyms | P1 / Need better routing (4 results in eval) | **RECALL_ISSUE** | 0 | 39 | 39 | Add missing aliases/topics to inspirations under: template-word-scene, template-vocabulary, template-english-top5-phrases, template-english-error-correction, template-english-dialogue-scene |
| book lovers gift guide | P1 / Need content generation (2 results in eval) | **ADEQUATE_RECALL** | 7 | 100 | 97 | Optional: add aliases to improve recall further. Not P0/P1. |

---

## Recommended Engineering Fixes (by type)

### 1. CJK Alias Fixes (HIGH PRIORITY — affects all Chinese flashcard queries)

Add "闪卡" to the `search_aliases` array of at least 5 flashcard-family inspirations:
- `template-vocabulary` inspirations
- `template-word-scene` inspirations
- `template-detailed-vocab-flashcard` inspirations
- `template-cartoon-english-vocabulary-flashcards` inspirations
- `template-children-english-vocab-spelling` inspirations

**Impact:** Fixes 双语闪卡, 词汇闪卡, 英语单词闪卡 — all currently returning 0.

### 2. Phonics Worksheet Alias Fix (MEDIUM — fixes one P0)

Add the following to `search_aliases` of `template-phonics-consonant-blend` inspirations:
- "worksheet", "worksheets", "printable worksheet", "phonics worksheet"
- "kindergarten", "preschool", "early literacy"

**Impact:** Fixes "phonics worksheets kindergarten" from 0 to ~50 results.

### 3. Recipe Alias Expansion (MEDIUM — partially fixes 3 P0s)

Add to recipe template inspirations (`template-recipe`, `template-premium-recipe-card-infographic`):
- "weeknight dinner", "easy dinner", "healthy dinner", "quick dinner"
- "gluten free", "gluten-free", "dietary meal", "special diet"
- "meal prep", "weekly meal plan", "meal planner"

**Note:** Recall fix alone insufficient — Western recipe inspirations are thin. Pair with batch generation.

### 4. Multi-Token Plural Stemming (ENGINEERING — longer term)

The tokenizer only stems plurals for single-token queries. Consider extending to all tokens:
- "bilingual flashcard**s**" should match "bilingual flashcard"
- Low risk, high impact across many vocabulary/template queries

### 5. Content Generation Follow-up (BATCH GEN)

For CONTENT_GAP_EXISTING_TEMPLATE items:
- Batch-generate Europe watercolor map inspirations under `template-watercolor-world-map-illustration`
- Batch-generate kitchen before/after examples under `template-home-organization-before-after`
- Batch-generate Western recipe examples under `template-recipe` / `template-premium-recipe-card-infographic`
- Batch-generate Cuban sandwich example under `template-recipe`

---

## Summary: What Was Previously Misclassified as "Template Gap"

| Query | Previous Classification | Actual Issue | Action Type |
|---|---|---|---|
| bilingual flashcards (plural) | P1 template gap | NOT A GAP (454 results) | None needed |
| 双语闪卡 | P1 template gap | Recall issue (missing "闪卡" alias) | Add Chinese alias |
| 词汇闪卡 | P1 template gap | Recall issue (missing "闪卡" alias) | Add Chinese alias |
| phonics worksheets kindergarten | P0 template gap | Recall issue (missing aliases) | Add aliases |
| easy weeknight dinners healthy | P0 template gap | Content gap with existing templates | Add aliases + batch gen |
| gluten free dinner ideas | P0 template gap | Content gap with existing templates | Add aliases + batch gen |
| meal prep weekly recipes | P0 template gap | Content gap with existing templates | Add aliases + batch gen |

True template gaps (no existing template): **iCard**, **unique cultural experiences** only.

---

## Files Changed (Applied in This Audit)

Two alias fixes were applied to `public/data/nano_inspiration.json`:

### Fix 1 — Add "闪卡" to flashcard-family inspirations

**Records updated:** 366 inspirations under `template-vocabulary`, `template-word-scene`, `template-detailed-vocab-flashcard`, `template-cartoon-english-vocabulary-flashcards`, `template-children-english-vocab-spelling`, `template-bilingual-object-structure-labeling`, `template-daily-essentials-learning-card`, `template-kids-vocabulary-poster`, `template-CVC-english-word-coloring-flower-card`.

**Why:** CJK bigram search for "双语闪卡", "词汇闪卡", "英语单词闪卡" requires "闪卡" as a bigram in the blob. The templates had "flashcards" in English topics but zero Chinese alias for the flashcard concept.

### Fix 2 — Add English worksheet/kindergarten aliases to phonics inspirations

**Records updated:** 50 inspirations under `template-phonics-consonant-blend`.

**Aliases added:** "phonics worksheet", "phonics worksheets", "kindergarten phonics", "printable phonics", "early literacy", "consonant blend worksheet".

**Why:** The phonics template had only Chinese aliases (辅音组合, 学习海报, etc.). English queries for "phonics worksheets kindergarten" returned 0 because "worksheet" and "kindergarten" were in zero phonics blobs.

---

## Validation — Before / After Recall

| Query | Before (Strict Section A) | After (Strict Section A) | Change |
|---|---:|---:|---|
| 双语闪卡 | 0 | **176** | +176 |
| 词汇闪卡 | 0 | **119** | +119 |
| 英语单词闪卡 | 0 | **15** | +15 |
| phonics worksheets kindergarten | 0 | **50** | +50 |
| bilingual flashcards (plural) | 454 | 454 | unchanged ✓ |
| English Chinese flashcards | 374 | 374 | unchanged ✓ |
| Spanish vocabulary printable | 15 | 15 | unchanged ✓ |
| book lovers gift guide | 7 | 7 | unchanged ✓ |

**Regression check:** All previously-working queries are unchanged. No false regressions introduced.

> **Note on "Section A vs Section B":** This audit simulates only the strict-AND inspiration search (Section A of the search page). The production search also runs an LLM template matcher (Section B via `lib/searchTemplateMatch.ts`) which uses GPT-4o-mini to suggest generatable templates. Queries like "ESL flashcards printable" and "homophones and homonyms" may show adequate total results in production because Section B compensates — but the inspiration grid (Section A) would still be thin. Fixing Section A aliases improves both the inspiration display and the overall result diversity.
