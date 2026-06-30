# Template Recall Audit: All Candidate Queries

> **Generated:** 2026-06-23
> **Branch:** baobao/multi-intent-topic-cooccurrence
> **Scope:** template-level recall audit — NOT inspiration-level recall
> **Simulation:** strict-AND + relaxed-AND inspiration scoring + template i18n blob matching (mirrors `app/[locale]/(public)/search/page.tsx`)

---

## Executive Summary

| Metric | Count |
|---|---|
| Total candidate queries audited | **42** |
| TEMPLATE_RECALL_ISSUE | **14** |
| CONTENT_GAP_EXISTING_TEMPLATE | **1** |
| TRUE_TEMPLATE_GAP | **1** |
| ADEQUATE_TEMPLATE_RECALL | **26** |
| UNCERTAIN | **0** |

---

## Key Finding

> **This audit processes template-level recall, not inspiration-level recall.**
> The question is: does the production search pipeline surface the *right templates* for each query?

Several queries previously marked as "template gaps" or "P0 content gaps" are **not true template gaps**. Curify already has relevant templates and inspiration examples, but the production search pipeline does not recall them reliably.

Root causes fall into these buckets:
1. **Multi-token plural stem gap** — page.tsx only stems plurals for single-token queries; "bilingual flashcards" keeps "flashcards" unstemmed, missing records tagged with "flashcard"
2. **CJK / synonym mapping gap** — Chinese queries don't find English-only template blobs; "词汇闪卡" has no Chinese alias in inspiration records
3. **Template i18n blob coverage gap** — template descriptions (title/category/what/who) don't include the exact English terms users type
4. **Inspiration alias gaps** — relevant inspirations exist but their search_aliases don't include common user-typed synonyms

---

## Priority Examples

### bilingual flashcards

- **Source:** boss feedback / external signal report
- **Original classification:** P1 template gap (boss report)
- **New classification:** `ADEQUATE_TEMPLATE_RECALL`
- **Current template recall:** 21 templates (i18n match: 2, inspiration-derived: 21)
- **Current inspiration recall:** 455 strict
- **Inventory:** 19 templates, 585 inspirations
- **Missed templates:** 0
- **Top recalled template IDs:** template-detailed-vocab-flashcard; template-chinese-idiom-learning-card; template-species-science; template-species; template-word-scene
- **Top missed template IDs:** template-cuisine-food-vocab-poster; template-multilingual-vocabulary-poster-watercolor; template-verb-action-learning-cards; template-english-phrasal-verb; template-chinese-verb-opposite-infographic
- **Root cause:** none identified
- **Recommended action:** No action needed. Monitor for diversity regression.

---

### education flashcards

- **Source:** boss feedback
- **Original classification:** P1 template gap
- **New classification:** `ADEQUATE_TEMPLATE_RECALL`
- **Current template recall:** 7 templates (i18n match: 1, inspiration-derived: 6)
- **Current inspiration recall:** 9 strict
- **Inventory:** 29 templates, 113 inspirations
- **Missed templates:** 22
- **Top recalled template IDs:** template-chinese-idiom-learning-card; template-species-science; template-vocabulary; template-detailed-vocab-flashcard; template-daily-essentials-learning-card
- **Top missed template IDs:** template-education; template-education-card; template-solar-term; template-city-miniature; template-english-top5-phrases
- **Root cause:** none identified
- **Recommended action:** No action needed. Monitor for diversity regression.

---

### ESL flashcards printable

- **Source:** docs/external-signal-pilot/curify-gap-analysis-58.csv #49
- **Original classification:** P1 / Already covered (10 results in eval)
- **New classification:** `ADEQUATE_TEMPLATE_RECALL`
- **Current template recall:** 1 templates (i18n match: 0, inspiration-derived: 1)
- **Current inspiration recall:** 3 strict
- **Inventory:** 3 templates, 0 inspirations
- **Missed templates:** 2
- **Top recalled template IDs:** template-children-english-vocab-spelling
- **Top missed template IDs:** template-detailed-vocab-flashcard; template-cartoon-english-vocabulary-flashcards; template-verb-action-learning-cards
- **Root cause:** template i18n blob does not match query tokens (missing description/title coverage); multi-token plural stem not applied (page.tsx only stems single-token queries)
- **Recommended action:** No action needed. Monitor for diversity regression.

---

### homophones and homonyms

- **Source:** docs/external-signal-pilot/curify-gap-analysis-58.csv #22
- **Original classification:** P1 template gap (4 results in eval)
- **New classification:** `ADEQUATE_TEMPLATE_RECALL`
- **Current template recall:** 1 templates (i18n match: 1, inspiration-derived: 1)
- **Current inspiration recall:** 6 strict
- **Inventory:** 39 templates, 748 inspirations
- **Missed templates:** 38
- **Top recalled template IDs:** template-english-grammar-wordlist-infographic
- **Top missed template IDs:** template-word-scene; template-vocabulary; template-english-top5-phrases; template-english-error-correction; template-english-dialogue-scene
- **Root cause:** multi-token plural stem not applied (page.tsx only stems single-token queries)
- **Recommended action:** No action needed. Monitor for diversity regression.

---

### paris travel itinerary

- **Source:** docs/daily_report/2026-06-19.md
- **Original classification:** WARN / REAL_CONTENT_GAP + EVAL_FALSE_POSITIVE
- **New classification:** `ADEQUATE_TEMPLATE_RECALL`
- **Current template recall:** 2 templates (i18n match: 0, inspiration-derived: 2)
- **Current inspiration recall:** 2 strict
- **Inventory:** 29 templates, 286 inspirations
- **Missed templates:** 27
- **Top recalled template IDs:** template-city-miniature; template-tourist-spot-watercolor-map-infographic
- **Top missed template IDs:** template-travel; template-weather; template-mbti-contrast; template-series-travel; template-city-mbti
- **Root cause:** none identified
- **Recommended action:** No action needed. Monitor for diversity regression.

---

### before after kitchen organization makeover

- **Source:** docs/external-signal-pilot/curify-gap-analysis-58.csv #46
- **Original classification:** P1 template gap (3 results in eval)
- **New classification:** `TEMPLATE_RECALL_ISSUE`
- **Current template recall:** 1 templates (i18n match: 0, inspiration-derived: 1)
- **Current inspiration recall:** 2 strict
- **Inventory:** 11 templates, 20 inspirations
- **Missed templates:** 10
- **Top recalled template IDs:** template-home-organization-before-after
- **Top missed template IDs:** template-species; template-character-analysis; template-book-series; template-portrait-retouching-blueprint; template-guofeng-scroll
- **Root cause:** template i18n blob does not match query tokens (missing description/title coverage); multi-token plural stem not applied (page.tsx only stems single-token queries); inspiration blobs missing relevant aliases/topics for these query tokens
- **Recommended action:** Fix recall: add search_aliases to inspirations; add query terms to template i18n description/title. Root cause: template i18n blob does not match query tokens (missing description/title coverage); multi-token plural stem not applied (page.tsx only stems single-token queries); inspiration blobs missing relevant aliases/topics for these query tokens

---

### phonics worksheets kindergarten

- **Source:** docs/external-signal-pilot/curify-gap-analysis-58.csv #47
- **Original classification:** P0 content gap (zero results)
- **New classification:** `ADEQUATE_TEMPLATE_RECALL`
- **Current template recall:** 1 templates (i18n match: 0, inspiration-derived: 1)
- **Current inspiration recall:** 50 strict
- **Inventory:** 3 templates, 71 inspirations
- **Missed templates:** 2
- **Top recalled template IDs:** template-phonics-consonant-blend
- **Top missed template IDs:** template-CVC-english-word-coloring-flower-card; template-kids-theme-fill-in-worksheet
- **Root cause:** template i18n blob does not match query tokens (missing description/title coverage); multi-token plural stem not applied (page.tsx only stems single-token queries)
- **Recommended action:** No action needed. Monitor for diversity regression.

---

### easy weeknight dinners healthy

- **Source:** docs/external-signal-pilot/curify-gap-analysis-58.csv #50
- **Original classification:** P0 content gap (zero results)
- **New classification:** `TEMPLATE_RECALL_ISSUE`
- **Current template recall:** 0 templates (i18n match: 0, inspiration-derived: 0)
- **Current inspiration recall:** 0 strict
- **Inventory:** 9 templates, 136 inspirations
- **Missed templates:** 9
- **Top recalled template IDs:** (none)
- **Top missed template IDs:** template-recipe; template-fruit; template-premium-recipe-card-infographic; template-nutrition-food-guide-poster; template-food-recipe-tip-infographic
- **Root cause:** template i18n blob does not match query tokens (missing description/title coverage); multi-token plural stem not applied (page.tsx only stems single-token queries); inspiration blobs missing relevant aliases/topics for these query tokens
- **Recommended action:** Fix recall: add search_aliases to inspirations; add query terms to template i18n description/title. Root cause: template i18n blob does not match query tokens (missing description/title coverage); multi-token plural stem not applied (page.tsx only stems single-token queries); inspiration blobs missing relevant aliases/topics for these query tokens

---

### unique cultural experiences

- **Source:** docs/external-signal-pilot/curify-gap-analysis-58.csv #27
- **Original classification:** P0 content gap (zero results)
- **New classification:** `TEMPLATE_RECALL_ISSUE`
- **Current template recall:** 0 templates (i18n match: 0, inspiration-derived: 0)
- **Current inspiration recall:** 0 strict
- **Inventory:** 34 templates, 224 inspirations
- **Missed templates:** 34
- **Top recalled template IDs:** (none)
- **Top missed template IDs:** template-intangible-heritage; template-costume; template-cultural-relic-retro-infographic; template-food; template-solar-term
- **Root cause:** template i18n blob does not match query tokens (missing description/title coverage); multi-token plural stem not applied (page.tsx only stems single-token queries); inspiration blobs missing relevant aliases/topics for these query tokens
- **Recommended action:** Fix recall: add search_aliases to inspirations; add query terms to template i18n description/title. Root cause: template i18n blob does not match query tokens (missing description/title coverage); multi-token plural stem not applied (page.tsx only stems single-token queries); inspiration blobs missing relevant aliases/topics for these query tokens

---

### iCard

- **Source:** boss feedback
- **Original classification:** P1 template gap
- **New classification:** `TRUE_TEMPLATE_GAP`
- **Current template recall:** 0 templates (i18n match: 0, inspiration-derived: 0)
- **Current inspiration recall:** 0 strict
- **Inventory:** 0 templates, 0 inspirations
- **Missed templates:** 0
- **Top recalled template IDs:** (none)
- **Top missed template IDs:** (none)
- **Root cause:** no matching template in inventory (true gap)
- **Recommended action:** Add new template(s) to cover this query intent. No existing template serves this need.

---

## Full Audit Table

| query | original classification | new classification | current templates | current inspirations | inventory templates | missed templates | recommended action |
|---|---|---|---:|---:|---:|---:|---|
| bilingual flashcards | P1 template gap (boss report) | **ADEQUATE_TEMPLATE_RECALL** | 21 | 455 | 19 | 0 | No action needed. Monitor for diversity regression. |
| bilingual flashcard | P1 template gap | **ADEQUATE_TEMPLATE_RECALL** | 3 | 6 | 19 | 16 | No action needed. Monitor for diversity regression. |
| English Chinese flashcards | P1 template gap | **ADEQUATE_TEMPLATE_RECALL** | 20 | 374 | 19 | 0 | No action needed. Monitor for diversity regression. |
| Chinese English flashcards | P1 template gap | **ADEQUATE_TEMPLATE_RECALL** | 20 | 374 | 19 | 0 | No action needed. Monitor for diversity regression. |
| 双语闪卡 | P1 recall issue | **ADEQUATE_TEMPLATE_RECALL** | 7 | 176 | 20 | 13 | No action needed. Monitor for diversity regression. |
| 英语单词闪卡 | P1 recall issue | **ADEQUATE_TEMPLATE_RECALL** | 7 | 10 | 40 | 33 | No action needed. Monitor for diversity regression. |
| 词汇闪卡 | P1 recall issue | **ADEQUATE_TEMPLATE_RECALL** | 9 | 119 | 40 | 31 | No action needed. Monitor for diversity regression. |
| education flashcards | P1 template gap | **ADEQUATE_TEMPLATE_RECALL** | 7 | 9 | 29 | 22 | No action needed. Monitor for diversity regression. |
| education flashcard | P1 template gap | **ADEQUATE_TEMPLATE_RECALL** | 2 | 1 | 29 | 27 | No action needed. Monitor for diversity regression. |
| EdTech flashcards | P1 template gap | **TEMPLATE_RECALL_ISSUE** | 1 | 2 | 32 | 31 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| iCard flashcards | P1 template gap | **TEMPLATE_RECALL_ISSUE** | 0 | 0 | 5 | 5 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| iCard | P1 template gap | **TRUE_TEMPLATE_GAP** | 0 | 0 | 0 | 0 | Add new template(s) to cover this query intent. No existing template serves this… |
| animal vocabulary | P1 template gap | **ADEQUATE_TEMPLATE_RECALL** | 14 | 165 | 48 | 34 | No action needed. Monitor for diversity regression. |
| phonics worksheets kindergarten | P0 content gap (zero results) | **ADEQUATE_TEMPLATE_RECALL** | 1 | 50 | 3 | 2 | No action needed. Monitor for diversity regression. |
| easy weeknight dinners healthy | P0 content gap (zero results) | **TEMPLATE_RECALL_ISSUE** | 0 | 0 | 9 | 9 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| gluten free dinner ideas | P0 content gap (zero results) | **TEMPLATE_RECALL_ISSUE** | 0 | 0 | 28 | 28 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| meal prep weekly recipes | P0 content gap (zero results) | **TEMPLATE_RECALL_ISSUE** | 0 | 0 | 29 | 29 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| unique cultural experiences | P0 content gap (zero results) | **TEMPLATE_RECALL_ISSUE** | 0 | 0 | 34 | 34 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| 电商详情图 | P1 template gap (4 results in eval) | **ADEQUATE_TEMPLATE_RECALL** | 1 | 21 | 6 | 5 | No action needed. Monitor for diversity regression. |
| 趣味经济学知识科普 | P1 template gap (6 results in eval) | **ADEQUATE_TEMPLATE_RECALL** | 3 | 2 | 181 | 178 | No action needed. Monitor for diversity regression. |
| 证件照 | P1 template gap (6 results in eval) | **ADEQUATE_TEMPLATE_RECALL** | 3 | 16 | 1 | 0 | No action needed. Monitor for diversity regression. |
| homophones and homonyms | P1 template gap (4 results in eval) | **ADEQUATE_TEMPLATE_RECALL** | 1 | 6 | 39 | 38 | No action needed. Monitor for diversity regression. |
| wedding planner | P1 template gap (7 results in eval) | **ADEQUATE_TEMPLATE_RECALL** | 4 | 28 | 5 | 1 | No action needed. Monitor for diversity regression. |
| cuban sandwich recipe poster | P1 template gap (4 results in eval; 1 after fix) | **TEMPLATE_RECALL_ISSUE** | 1 | 1 | 173 | 172 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| bilingual flashcards for kids learning korean fruits | P1 template gap (6 results in eval) | **TEMPLATE_RECALL_ISSUE** | 1 | 1 | 22 | 21 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| watercolor map of europe travel destinations | P1 template gap (2 results in eval) | **TEMPLATE_RECALL_ISSUE** | 1 | 1 | 9 | 8 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| marvel mbti character chart 16 types | P1 template gap (7 results in eval) | **TEMPLATE_RECALL_ISSUE** | 0 | 0 | 80 | 80 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| lunar new year red envelope graphic design | P1 template gap (4 results in eval) | **ADEQUATE_TEMPLATE_RECALL** | 1 | 8 | 1 | 0 | No action needed. Monitor for diversity regression. |
| before after kitchen organization makeover | P1 template gap (3 results in eval) | **TEMPLATE_RECALL_ISSUE** | 1 | 2 | 11 | 10 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| Spanish vocabulary printable | P1 / Better routing needed (6 results in eval) | **ADEQUATE_TEMPLATE_RECALL** | 1 | 15 | 1 | 0 | No action needed. Monitor for diversity regression. |
| ESL flashcards printable | P1 / Already covered (10 results in eval) | **ADEQUATE_TEMPLATE_RECALL** | 1 | 3 | 3 | 2 | No action needed. Monitor for diversity regression. |
| book lovers gift guide | P1 / Need content generation (2 results in eval) | **ADEQUATE_TEMPLATE_RECALL** | 3 | 7 | 12 | 9 | No action needed. Monitor for diversity regression. |
| mbti marvel | P1 template gap (5 results in eval) | **ADEQUATE_TEMPLATE_RECALL** | 2 | 74 | 28 | 26 | No action needed. Monitor for diversity regression. |
| historical character | P1 retrieval gap (5 results) | **ADEQUATE_TEMPLATE_RECALL** | 10 | 36 | 113 | 103 | No action needed. Monitor for diversity regression. |
| 反义词 | P2 retrieval gap (9 results) | **ADEQUATE_TEMPLATE_RECALL** | 6 | 57 | 39 | 33 | No action needed. Monitor for diversity regression. |
| paper cutting | P2 retrieval gap (9 results) | **ADEQUATE_TEMPLATE_RECALL** | 6 | 49 | 0 | 0 | No action needed. Monitor for diversity regression. |
| samurai | P2 retrieval gap (8 results) | **ADEQUATE_TEMPLATE_RECALL** | 5 | 9 | 0 | 0 | No action needed. Monitor for diversity regression. |
| paris travel itinerary | WARN / REAL_CONTENT_GAP + EVAL_FALSE_POSITIVE | **ADEQUATE_TEMPLATE_RECALL** | 2 | 2 | 29 | 27 | No action needed. Monitor for diversity regression. |
| architecture empire state building | WARN / RETRIEVAL_GAP | **TEMPLATE_RECALL_ISSUE** | 1 | 1 | 60 | 59 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| childhood snacks then vs now | WARN / RETRIEVAL_GAP + EVAL_FALSE_POSITIVE | **TEMPLATE_RECALL_ISSUE** | 1 | 1 | 7 | 6 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| warmup routine running checklist | WARN / RETRIEVAL_GAP | **TEMPLATE_RECALL_ISSUE** | 1 | 1 | 9 | 8 | Fix recall: add search_aliases to inspirations; add query terms to template i18n… |
| vintage stamp collection garden birds | WARN / RETRIEVAL_GAP + EVAL_FALSE_POSITIVE | **CONTENT_GAP_EXISTING_TEMPLATE** | 1 | 1 | 2 | 1 | Batch-generate inspiration examples under existing template(s). Fix aliases firs… |

---

## Classification Definitions

| Classification | Meaning |
|---|---|
| TEMPLATE_RECALL_ISSUE | Template inventory has ≥3 relevant templates but current search recalls <2 |
| CONTENT_GAP_EXISTING_TEMPLATE | Template framework exists but inspiration examples are thin (< 10 in inventory) |
| TRUE_TEMPLATE_GAP | No template in inventory matches the query intent |
| ADEQUATE_TEMPLATE_RECALL | Current search returns ≥2 templates or ≥3 inspirations |
| UNCERTAIN | Evidence insufficient for clear classification |

---

## Root Cause Groups

### 1. Multi-token plural stem gap
Queries where "flashcards" (plural) is a content word in a multi-token query but the stem "flashcard" is not applied.
- page.tsx only stems single-token queries
- Affects: "education flashcards", "ESL flashcards printable", "EdTech flashcards", "iCard flashcards"

**Fix:** In `buildSearchTokens` / `buildTokens`, extend singular stemming to individual tokens within multi-word queries (low-risk change).

### 2. CJK/synonym mapping gap
Chinese query tokens ("闪卡", "词汇", "证件照") not in English-only template/inspiration blobs.
- Affects: "双语闪卡", "英语单词闪卡", "词汇闪卡", "电商详情图", "证件照", "趣味经济学知识科普", "反义词"

**Fix:** Add Chinese aliases to relevant inspiration search_aliases fields (low-risk, targeted).

### 3. Template i18n description gap
Template descriptions don't use user-typed vocabulary.
- "recipe template" description doesn't mention "weeknight", "gluten free", "meal prep"
- "travel template" description doesn't mention "Paris", "itinerary"
- Affects: "easy weeknight dinners healthy", "gluten free dinner ideas", "paris travel itinerary"

**Fix:** Update messages/en/nano.json descriptions for key templates to include common user terms (low-risk).

### 4. Inspiration alias gaps
Relevant inspirations exist but no search_alias for common user synonyms.
- "warmup routine" has the warmup template but "checklist", "running" not in alias
- "phonics worksheets kindergarten" has phonics template but "worksheet", "kindergarten" not in alias
- Affects: "warmup routine running checklist", "phonics worksheets kindergarten", "homophones and homonyms"

**Fix:** Add targeted aliases to existing inspiration records (same approach as commit `d25921dc`).

### 5. True content generation needed
Queries where inventory genuinely lacks templates.
- Affects: "iCard"

### 6. Adequate recall (misclassified as gap)
- "bilingual flashcards": 21 templates, 455 inspirations (was: P1 template gap (boss report))
- "bilingual flashcard": 3 templates, 6 inspirations (was: P1 template gap)
- "English Chinese flashcards": 20 templates, 374 inspirations (was: P1 template gap)
- "Chinese English flashcards": 20 templates, 374 inspirations (was: P1 template gap)
- "双语闪卡": 7 templates, 176 inspirations (was: P1 recall issue)
- "英语单词闪卡": 7 templates, 10 inspirations (was: P1 recall issue)
- "词汇闪卡": 9 templates, 119 inspirations (was: P1 recall issue)
- "education flashcards": 7 templates, 9 inspirations (was: P1 template gap)
- "education flashcard": 2 templates, 1 inspirations (was: P1 template gap)
- "animal vocabulary": 14 templates, 165 inspirations (was: P1 template gap)
- "phonics worksheets kindergarten": 1 templates, 50 inspirations (was: P0 content gap (zero results))
- "电商详情图": 1 templates, 21 inspirations (was: P1 template gap (4 results in eval))
- "趣味经济学知识科普": 3 templates, 2 inspirations (was: P1 template gap (6 results in eval))
- "证件照": 3 templates, 16 inspirations (was: P1 template gap (6 results in eval))
- "homophones and homonyms": 1 templates, 6 inspirations (was: P1 template gap (4 results in eval))
- "wedding planner": 4 templates, 28 inspirations (was: P1 template gap (7 results in eval))
- "lunar new year red envelope graphic design": 1 templates, 8 inspirations (was: P1 template gap (4 results in eval))
- "Spanish vocabulary printable": 1 templates, 15 inspirations (was: P1 / Better routing needed (6 results in eval))
- "ESL flashcards printable": 1 templates, 3 inspirations (was: P1 / Already covered (10 results in eval))
- "book lovers gift guide": 3 templates, 7 inspirations (was: P1 / Need content generation (2 results in eval))
- "mbti marvel": 2 templates, 74 inspirations (was: P1 template gap (5 results in eval))
- "historical character": 10 templates, 36 inspirations (was: P1 retrieval gap (5 results))
- "反义词": 6 templates, 57 inspirations (was: P2 retrieval gap (9 results))
- "paper cutting": 6 templates, 49 inspirations (was: P2 retrieval gap (9 results))
- "samurai": 5 templates, 9 inspirations (was: P2 retrieval gap (8 results))
- "paris travel itinerary": 2 templates, 2 inspirations (was: WARN / REAL_CONTENT_GAP + EVAL_FALSE_POSITIVE)

---

## Files Changed
*(Fixes applied in this run — see separate commit)*
None in this script run. This script is read-only and audit-only.

---

## Local UI Verification
Run the dev server and check template section (not just inspiration grid):
```
npm run dev
```

Key URLs to verify template results:
- http://localhost:3001/en/search?q=bilingual+flashcards
- http://localhost:3001/en/search?q=education+flashcards
- http://localhost:3001/en/search?q=paris+travel+itinerary
- http://localhost:3001/en/search?q=before+after+kitchen+organization+makeover
- http://localhost:3001/en/search?q=warmup+routine+running+checklist

Template results appear in the "Generate with these templates" / matched templates section below the inspiration grid.

---

## Tests
```bash
npm run lint
npm test -- --testPathPattern="search|intent|template"
```
