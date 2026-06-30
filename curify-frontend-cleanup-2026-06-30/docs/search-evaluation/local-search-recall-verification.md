# Local Search Recall Verification

> **Date:** 2026-06-23  
> **Dev server:** http://localhost:3001 (pre-existing process, no restart needed)  
> **Method:** curl + HTML parsing — CDN preview image URLs as per-card marker; reproduce-links for Section B  
> **Before baseline:** Zero-result page (xyznonexistent12345) = 0 cards, shows "No results" / "no inspiration" text  

---

## Result Summary

| Query | Section A Cards (After Fix) | Before Fix | Relevant Templates Shown |
|---|---:|---|---|
| bilingual flashcards (plural) | **8** | 8 (unchanged) | detailed-vocab-flashcard, word-scene, species-science |
| bilingual flashcard (singular) | **5** | 5 (unchanged) | detailed-vocab-flashcard, chinese-idiom-learning-card |
| 双语闪卡 | **9** | **0 → 9** ✓ | bilingual-object-structure-labeling, cartoon-english-vocab-flashcards, children-english-vocab-spelling, detailed-vocab-flashcard, vocabulary |
| 词汇闪卡 | **11** | **0 → 11** ✓ | CVC-english-word-coloring-flower-card, bilingual-object-structure-labeling, cartoon-english-vocab-flashcards |
| 英语单词闪卡 | **8** | **0 → 8** ✓ | CVC-english-word-coloring-flower-card, cartoon-english-vocab-flashcards, daily-essentials-learning-card |
| phonics worksheets kindergarten | **3** | **0 → 3** ✓ | phonics-consonant-blend-bl, phonics-consonant-blend-ch, phonics-consonant-blend-gr |

---

## Verification Steps

1. Confirmed dev server live on port 3001 — full Curify HTML returned (2MB page).
2. Confirmed `nano_inspiration.json` diff is purely additive — 3071 records unchanged; spot-checked 3 IDs still present with asset URLs intact.
3. Established zero-result baseline: `xyznonexistent12345` returns 0 CDN preview cards and shows "No results" text.
4. Queried all 6 target URLs; counted unique CDN preview images (`cdn.curify-ai.com/images/nano_insp_preview/`) as Section A card proxy.
5. Confirmed none of the "no inspiration" text instances in fixed-query pages are in the search-results section (all are in embedded blog content).

---

## Remaining Gap: bilingual flashcard (singular) vs bilingual flashcards (plural)

- **bilingual flashcards**: 8 cards shown (adequate)
- **bilingual flashcard**: 5 cards shown (lower, but non-zero)
- **flashcards** (single token): 0 cards shown
- **flashcard** (single token): 0 cards shown

**Root cause:** The tokenizer stems single-token `flashcards` → `flashcard`, but the word-boundary regex `(?![a-z0-9])` then prevents `flashcard` from matching `flashcards` in the blob (the trailing `s` triggers the negative lookahead). This is a tokenizer-level issue, not a data issue.

**Recommended fix:** When stemming a token, also accept it as a prefix match — i.e., allow `flashcard` to match `flashcards` in blobs. This would require a code change in `app/[locale]/(public)/search/page.tsx` tokenInBlob function. Low risk, targeted change. Alternatively, add "flashcard" (singular) as an alias alongside "flashcards" (plural) in the relevant inspiration records.

The plural form `bilingual flashcards` has adequate recall (8 cards). The singular form `bilingual flashcard` is not P0 (5 cards > 3 threshold), so this is a P2/P3 improvement, not urgent.

---

## Data Safety Confirmation

```
Total inspiration records: 3071 (unchanged)
template-bilingual-object-structure-labeling-hamburger: EXISTS ✓
template-bilingual-object-structure-labeling-lily-flower: EXISTS ✓
template-phonics-consonant-blend-bl: EXISTS ✓
```

Diff is: +闪卡 alias added to 366 flashcard-family records, +6 English aliases added to 50 phonics records. No deletions.

---

## Lint & Tests

```
npm run lint  → 0 errors (pre-existing tseslint config warning only)
vitest run    → 188 tests passed / 188 (7 test files)
```
