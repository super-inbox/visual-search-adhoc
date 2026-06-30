# 5-Platform Visual Search Comparison — Curify Refreshed Post-PR #512
**Date:** 2026-06-30  
**Baseline:** Google Images, Bing Images, Pinterest, Canva — June 19–23, 2026 (unchanged)  
**Curify:** Re-scored programmatically on `main` at commit `a1a60bc5` after PR #512 merge  
**Query set:** 58 queries — 30 creative / 28 consumer intent

> **Methodology note:** This is a Curify-only refresh update. External platform data (Google, Bing, Pinterest, Canva) is from the original June benchmark and has not been re-crawled. Numbers for those four platforms are the same as in `external-signal-5x2-comparison-58.md`. Only Curify's results have been updated.

---

## Platform Scorecard (Updated)

| Platform | Consumer visual demand | Creative template intent | Visual diversity | Category intent clarity | Curify actionability | Role |
|----------|----------------------|--------------------------|-----------------|------------------------|---------------------|------|
| **Google Images** | 5 | 2 | 5 | 4 | 4 | Broad visual demand signal — best recall reference; avg 17.8 related-search chips/query; 58/58 coverage |
| **Bing Images** | 5 | 2 | 4 | 5 | 3 | Category taxonomy signal — richest related-search vocabulary; avg 39.9 chips/query; 58/58 coverage |
| **Pinterest** | 4 | 4 | 5 | 2 | 4 | Inspiration cluster signal — best for aesthetic/lifestyle sub-intent; 40/58 queries returned 0 labels (login modal) |
| **Canva** | 2 | 5 | 3 | 4 | 5 | Template and creator intent signal — 36/58 accessible (21/58 CJK + fandom = login_required); avg 58.2 labels/ok query |
| **Curify (baseline, Jun 2026)** | 3 | 3 | 3 | 4 | 5 | Subject of optimization — 53/58 ok, 5 ok_empty; creative rich rate: 33%; avg 8.8 intent chips |
| **Curify (post-PR #512, Jun 30)** | 3 | **4** | 3 | 4 | 5 | Updated — creative rich rate: 57%; 18/58 queries improved; persistent recipe/map gaps remain |

---

## Query Coverage Comparison (Updated)

| Platform | Total coverage | Empty queries | Rich queries | Creative rich rate | CJK support |
|----------|---------------|--------------|-------------|-------------------|-------------|
| Google Images | 58/58 | 0 | 58 | 100% | Full |
| Bing Images | 58/58 | 0 | 58 | 100% | Full |
| Pinterest | 58/58 | 0 (results exist, labels unreliable) | 58 | ~100% (pin results) | Partial (login for some) |
| Canva | 36/58 accessible | 21 login_required | 36 (of accessible) | ~90% (English queries) | Blocked for CJK |
| Curify (baseline) | 53/58 ok, 5 empty | 5 (recipe cluster) | ~35/58 | 33% (10/30 creative) | Full |
| **Curify (post-PR #512)** | 52/58 ok | 6 empty | **41/58** | **57% (17/30 creative)** | Full |

---

## Creative Intent Deep Dive (30 Creative Queries)

The benchmark includes 30 queries with primary creative intent (user wants to produce/generate output: flashcards, posters, charts, vocabulary cards, infographics).

### Before PR #512 (June baseline)

| Bucket | Creative queries | Consumer queries |
|--------|----------------|----------------|
| Rich (≥10) | 10/30 (33%) | 23/28 (82%) |
| Moderate (5-9) | 8/30 (27%) | 3/28 (11%) |
| Thin (1-4) | 7/30 (23%) | 1/28 (4%) |
| Empty (0) | 5/30 (17%) | 1/28 (4%) |

### After PR #512 (2026-06-30)

| Bucket | Creative queries | Consumer queries |
|--------|----------------|----------------|
| Rich (≥10) | **17/30 (57%)** | **24/28 (86%)** |
| Moderate (5-9) | 4/30 (13%) | 3/28 (11%) |
| Thin (1-4) | 4/30 (13%) | 0/28 (0%) |
| Empty (0) | 5/30 (17%) | 1/28 (4%) |

Creative rich rate jumped 24 percentage points (33% → 57%). Consumer rich rate improved 4 pp. The 5 persistent creative empties are: recipe cluster (3), MBTI compatibility chart (1), and `水果中文` alias gap (1).

---

## Notable Query-Level Changes (Selected)

| Query | Intent | Baseline | Post-PR #512 | Change | Commentary |
|-------|--------|----------|--------------|--------|-----------|
| `ESL flashcards printable` | creative | thin (4) | rich (16) | +↑ | Core printable education query rescued |
| `Spanish vocabulary printable` | creative | thin (4) | rich (15) | +↑ | Bilingual vocab template now surfaces fully |
| `global influence` | consumer | empty (0) | rich (38) | +↑ | Cultural content expansion effective |
| `remote destination` | consumer | empty (0) | rich (177) | +↑ | Travel content expansion very effective |
| `cozy reading aesthetic` | hybrid | thin (1) | rich (103) | +↑ | Lifestyle + reading content now rich |
| `wedding planner` | creative | moderate (5) | rich (28) | +↑ | Wedding visual content expanded |
| `mbti marvel` | hybrid/creative | moderate (7) | rich (74) | +↑ | Marvel MBTI chart content now rich |
| `monstera plant care guide infographic` | hybrid/creative | moderate (8) | rich (105) | +↑ | Plant care infographic very rich |
| `easy weeknight dinners healthy` | hybrid/creative | empty (0) | empty (0) | = | Recipe gap persists — c2 content generation needed |
| `infj vs entp dating compatibility chart` | creative | empty (0) | empty (0) | = | MBTI compatibility chart — c2 batch needed |
| `phonics worksheets kindergarten` | creative | thin (4) | empty (0) | ↓ | Alias fix on separate branch not yet merged |
| `香薰` | consumer | rich (10) | moderate (5) | ↓ | Investigate P0.1 re-enrichment side-effect |

---

## Platform Differentiation Summary

### Google Images and Bing Images: recall floor for all categories
Full coverage (58/58), no auth barriers, richest label vocabulary. Use as ground truth for which queries have visual demand. Bing's 39.9 related-search chips/query vs Curify's 8.8 intent chips = 4.5× gap in structured category navigation.

### Pinterest: creative inspiration and fandom browse
Strong for sub-intent discovery, lifestyle aesthetic, fandom. Limited as a signal source (40/58 label=0 due to login modal). Top-10 results show content demand; chips are unreliable.

### Canva: English template routing benchmark
Most directly comparable to Curify for creative/template queries. 21/58 CJK + fandom queries are login_required — Curify has a structural advantage here. For English creative queries, Canva's 58.2 filter chips reflect its rich output-type taxonomy (Format × Style × Size).

### Curify: post-PR #512 position
Strongest at:
- **Bilingual/CJK educational content**: vocabulary flashcards, antonyms, language learning — 500–600+ results in core categories
- **Character/fandom templates**: MBTI, Marvel, cultural characters — now rich across the board
- **Travel and lifestyle visual content**: remote destinations, city escapes, seasonal aesthetics — greatly expanded

Still thin:
- **Recipe cluster**: easy dinners, gluten-free, meal prep — no visual recipe templates yet generated
- **Long-tail creative charts**: watercolor maps, before-after, compatibility charts — single-digit inventory
- **Phonics/specific printable**: phonics worksheets alias fix pending merge

---

## Intent-Based Routing: Where Each Platform Routes Creative Queries

For a query like `Spanish vocabulary printable`:

| Platform | What the user sees | Actionable? |
|----------|--------------------|------------|
| Google Images | 10 images of printable Spanish vocab sheets from external sites | No — browse only |
| Bing Images | 10 images + 40 related-search chips for sub-intent navigation | No — browse only |
| Pinterest | 10 pins from Etsy/TPT/external blogs; boards reveal sub-intents | No — redirects to external |
| Canva | Template search results with 59 filter chips; direct template access | Yes — template available |
| **Curify** | 15 bilingual vocabulary inspiration cards + Language Learning Card template | **Yes — generate one click away** |

Curify and Canva are the only platforms that route the user to an **actionable generative surface** rather than a browse feed. Curify's advantage is CJK support (Canva blocked on CJK) and tighter template-to-inspiration linking (the example cards show what generation produces).

---

## Persistent Gaps and Next Steps

### Immediate actions (c2 — content generation available)

| Gap | Queries affected | Template available | Action |
|-----|-----------------|-------------------|--------|
| Recipe visual content | 3 queries (weeknight, gluten-free, meal prep) | Yes (`template-recipe`, `template-food-recipe-tip-infographic`) | Batch-gen recipe content configs |
| MBTI compatibility chart | `infj vs entp dating compatibility chart` | Yes (`template-mbti-relationship-infographic`) | One-off batch |
| Watercolor regional maps | `watercolor map of europe travel destinations` | Yes (`template-watercolor-world-map-illustration`) | Multi-region map batch |
| Before-after room series | `before after kitchen organization makeover` | Yes (`template-home-organization-before-after`) | Room variant batch |

### Alias fixes (c1 — no content gen needed)

| Gap | Action |
|-----|--------|
| `水果中文` — bigram doesn't span compound | Add `水果中文`, `中文水果` as direct aliases on en-zh fruit vocabulary items |
| `phonics worksheets kindergarten` — alias fix on wrong branch | Merge phonics alias patch from `baobao/multi-intent-topic-cooccurrence` |
| `bilingual flashcards for kids learning korean fruits` — strict miss | Add `bilingual`/`flashcards`/`kids`/`learning` aliases to en-ko vocab sibling records |

### Eval expansion (next eval cycle)

1. Run `eval_search.cjs --matcher` on the 18 improved queries to confirm template routing quality
2. Incorporate top-50 thin GSC queries from `raw/gsc-audit-2026-06-26/Queries-all.csv` into eval set
3. Add a relevance quality score (1–5 per top-5 results) to distinguish rich-but-noisy from rich-and-precise

---

*External platform data: June 19–23, 2026 (unchanged). Curify data: 2026-06-30 programmatic re-score on main@a1a60bc5.*
