# Pinterest & Canva Missing Data Report
**Generated:** 2026-06-23  
**Pilot:** External Signal 5-Platform Comparison (58 queries)  
**Scope:** Pinterest + Canva data gaps identified from observations.csv, summary.csv, and gap-analysis-58.csv

---

## Executive Summary

| Platform | Total Queries | Deficient Queries | Deficiency Rate | Primary Issue |
|----------|--------------|-------------------|-----------------|---------------|
| Pinterest | 58 | **40** | 69% | Labels/chips = 0 (login modal suppresses chips) |
| Canva | 58 | **23** | 40% | 21 login_required + 2 partial results |
| **Combined** | **116** | **63** | **54%** | — |

---

## 1. Pinterest — Missing Data Analysis

### 1.1 Overview

- **All 58 queries** have `topResultsCount = 10` (top-10 pin results are present)
- **40 out of 58 queries** have `labelsCount = 0` — category chips/related-search labels are missing
- **18 queries** have `labelsCount = 2` (the only non-zero value observed), which is still very low compared to Google avg (16–19.7) and Bing avg (39.9–40.0)
- Root cause: Pinterest shows a login modal on every search page. The modal is dismissible enough to reveal pin results behind it, but it suppresses the category chip rail that normally appears above search results.
- Collection note in all rows: `"login modal present but results visible behind it"`

### 1.2 Pinterest — Queries with Missing Labels (40 queries)

| # | Query | Intent | labelsCount | topResultsCount | Missing Type |
|---|-------|--------|------------|-----------------|--------------|
| 3 | 吉伊卡哇 | consumer | 0 | 10 | missing_labels |
| 4 | 家居装饰 | consumer | 0 | 10 | missing_labels |
| 7 | 水果中文 | creative | 0 | 10 | missing_labels |
| 8 | 电商详情图 | creative | 0 | 10 | missing_labels |
| 10 | 葡萄酒 | consumer | 0 | 10 | missing_labels |
| 11 | 蔬菜 | consumer | 0 | 10 | missing_labels |
| 13 | 趣味经济学知识科普 | creative | 0 | 10 | missing_labels |
| 15 | 食物 | consumer | 0 | 10 | missing_labels |
| 16 | 香薰 | consumer | 0 | 10 | missing_labels |
| 17 | 唯美春天 | consumer | 0 | 10 | missing_labels |
| 18 | 证件照 | creative | 0 | 10 | missing_labels |
| 19 | 手作 | creative | 0 | 10 | missing_labels |
| 20 | historical character | consumer | 0 | 10 | missing_labels |
| 21 | future characters | consumer | 0 | 10 | missing_labels |
| 22 | homophones and homonyms | creative | 0 | 10 | missing_labels |
| 23 | english-chinese | creative | 0 | 10 | missing_labels |
| 24 | language learning expressions | creative | 0 | 10 | missing_labels |
| 26 | remote destination | consumer | 0 | 10 | missing_labels |
| 27 | unique cultural experiences | consumer | 0 | 10 | missing_labels |
| 28 | short city escapes | consumer | 0 | 10 | missing_labels |
| 29 | creative comfort food | consumer | 0 | 10 | missing_labels |
| 30 | mbti marvel | creative | 0 | 10 | missing_labels |
| 33 | paper cutting | creative | 0 | 10 | missing_labels |
| 35 | 动物 词汇 | creative | 0 | 10 | missing_labels |
| 38 | infj vs entp dating compatibility chart | creative | 0 | 10 | missing_labels |
| 39 | cuban sandwich recipe poster | creative | 0 | 10 | missing_labels |
| 42 | monstera plant care guide infographic | creative | 0 | 10 | missing_labels |
| 43 | marvel mbti character chart 16 types | creative | 0 | 10 | missing_labels |
| 45 | 1950s vintage diner illustration retro poster | creative | 0 | 10 | missing_labels |
| 46 | before after kitchen organization makeover | creative | 0 | 10 | missing_labels |
| 47 | phonics worksheets kindergarten | creative | 0 | 10 | missing_labels |
| 48 | Spanish vocabulary printable | creative | 0 | 10 | missing_labels |
| 49 | ESL flashcards printable | creative | 0 | 10 | missing_labels |
| 50 | easy weeknight dinners healthy | creative | 0 | 10 | missing_labels |
| 51 | gluten free dinner ideas | creative | 0 | 10 | missing_labels |
| 52 | meal prep weekly recipes | creative | 0 | 10 | missing_labels |
| 53 | cozy reading aesthetic | consumer | 0 | 10 | missing_labels |
| 55 | chiikawa | consumer | 0 | 10 | missing_labels |
| 56 | samurai | consumer | 0 | 10 | missing_labels |
| 58 | maps | consumer | 0 | 10 | missing_labels |

### 1.3 Pinterest — Queries with Partial Labels (18 queries, labelsCount=2)

These have some labels but only 2 each — extremely sparse compared to competitors. They are not flagged as "missing" since a value exists, but they warrant attention.

| # | Query | labelsCount | Notes |
|---|-------|------------|-------|
| 1 | 单词 | 2 | |
| 2 | 卡通 | 2 | |
| 5 | 工程 | 2 | |
| 6 | 植物 | 2 | |
| 9 | 自行车 | 2 | |
| 12 | 词汇 | 2 | |
| 14 | 音乐 | 2 | |
| 25 | global influence | 2 | |
| 31 | spring flowers | 2 | |
| 32 | 反义词 | 2 | |
| 34 | met gala | 2 | |
| 36 | wedding planner | 2 | |
| 37 | minimalist autumn outfit for japan travel | 2 | |
| 40 | bilingual flashcards for kids learning korean fruits | 2 | |
| 41 | watercolor map of europe travel destinations | 2 | |
| 44 | lunar new year red envelope graphic design | 2 | |
| 54 | book lovers gift guide | 2 | |
| 57 | genshin | 2 | |

### 1.4 Pinterest — Root Cause Analysis

Pinterest enforces a login modal on all search pages for non-authenticated crawlers. The category chip labels (e.g., "Infographic", "Educational poster", "Vocabulary worksheet") are part of a secondary UI element that the login modal physically overlaps or causes to not render. Pin thumbnails and titles load via lazy-load behind the modal, so `topResultsCount = 10` is achievable, but the chip rail requires an authenticated session to render.

**Impact on signal quality:** Pinterest labels are a proxy for how Pinterest's own relevance model categorizes query intent. Missing 40/58 queries means we cannot use Pinterest label co-occurrence as an external signal for most queries in the pilot.

---

## 2. Canva — Missing Data Analysis

### 2.1 Overview

- **21 queries** are `login_required`: Canva's template search returned a hard login wall — zero templates and zero labels extracted
- **1 query** is `partial`: Q10 (葡萄酒), `topResultsCount=2`, `labelsCount=23` — login modal partially visible but only 2 of 10 templates extracted
- **1 query** is `ok` but incomplete: Q15 (食物), `topResultsCount=9` (not 10), `labelsCount=30`
- **Total deficient: 23 queries**

Platform-level summary from `external-signal-5x2-summary.csv`:

| Intent | Total | ok | login_required | topResults<10 | fullTop10Rate |
|--------|-------|----|----------------|---------------|---------------|
| creative | 30 | 22 | 8 | 0 | 73% |
| consumer | 28 | 14 | 13 | 2 | 46% |

### 2.2 Canva — login_required Queries (21 queries)

**Pattern:** Almost entirely CJK-character queries (Chinese). Canva's template search returns a login wall for Chinese-language queries. Two English queries (chiikawa, genshin) also triggered login_required — likely due to IP/session context during collection.

| # | Query | Intent | Status | topResults | labelsCount | Language |
|---|-------|--------|--------|-----------|-------------|----------|
| 1 | 单词 | consumer | login_required | 0 | 0 | CJK |
| 2 | 卡通 | consumer | login_required | 0 | 0 | CJK |
| 3 | 吉伊卡哇 | consumer | login_required | 0 | 0 | CJK |
| 4 | 家居装饰 | consumer | login_required | 0 | 0 | CJK |
| 5 | 工程 | consumer | login_required | 0 | 0 | CJK |
| 6 | 植物 | consumer | login_required | 0 | 0 | CJK |
| 7 | 水果中文 | creative | login_required | 0 | 0 | CJK |
| 8 | 电商详情图 | creative | login_required | 0 | 0 | CJK |
| 9 | 自行车 | consumer | login_required | 0 | 0 | CJK |
| 11 | 蔬菜 | consumer | login_required | 0 | 0 | CJK |
| 12 | 词汇 | creative | login_required | 0 | 0 | CJK |
| 13 | 趣味经济学知识科普 | creative | login_required | 0 | 0 | CJK |
| 14 | 音乐 | consumer | login_required | 0 | 0 | CJK |
| 16 | 香薰 | consumer | login_required | 0 | 0 | CJK |
| 17 | 唯美春天 | consumer | login_required | 0 | 0 | CJK |
| 18 | 证件照 | creative | login_required | 0 | 0 | CJK |
| 19 | 手作 | creative | login_required | 0 | 0 | CJK |
| 32 | 反义词 | creative | login_required | 0 | 0 | CJK |
| 35 | 动物 词汇 | creative | login_required | 0 | 0 | CJK |
| 55 | chiikawa | consumer | login_required | 0 | 0 | EN (session issue) |
| 57 | genshin | consumer | login_required | 0 | 0 | EN (session issue) |

### 2.3 Canva — Partial / Incomplete Results (2 queries)

| # | Query | Intent | Status | topResults | labelsCount | Issue |
|---|-------|--------|--------|-----------|-------------|-------|
| 10 | 葡萄酒 | consumer | partial | 2 | 23 | Login modal partially visible; only 2 templates extracted |
| 15 | 食物 | consumer | ok | 9 | 30 | 9 results instead of 10; possible pagination/rendering cutoff |

### 2.4 Canva — Root Cause Analysis

Canva's template search `/templates/?query=...` requires authentication to display results for:
1. **CJK queries**: All 19 CJK-script queries consistently hit the login wall. Canva's search endpoint appears to require login when the query language is Chinese/Japanese/Korean.
2. **Session expiry / IP**: Queries `chiikawa` and `genshin` (English) also received login_required, likely because the collection session expired or the IP was rate-limited mid-collection, causing subsequent requests to drop into the unauthenticated state.
3. **Partial extraction**: `葡萄酒` (Q10) — the collector managed to extract 2 templates before the login wall fully rendered, producing a `partial` status. `食物` (Q15) — logged-in session but page rendering cut off before the 10th template loaded.

---

## 3. What Needs Manual Supplementation

### 3.1 Pinterest — Label Collection (40 queries)

**What is needed:** For each of the 40 queries with `labelsCount=0`, manually capture the category chips / related-search labels that appear in the Pinterest search result page when viewed as an authenticated user.

**What a Pinterest label looks like:** Horizontal pill-shaped chips above or below the first row of pins. Examples: "Infographic", "Educational poster", "Recipe card", "Worksheet", "Mood board".

**What to record per query:** The full list of visible chip text strings, and their count.

### 3.2 Canva — Full Template Collection (23 queries)

**What is needed:**
- For 21 `login_required` queries: Log in to Canva and manually retrieve the top 10 template results (title, template URL, page URL) plus the filter/category label chips visible on the results page.
- For Q10 (葡萄酒, partial): Re-visit while logged in and retrieve the remaining 8 templates.
- For Q15 (食物, ok-but-9): Re-visit and confirm whether a 10th template exists.

---

## 4. Manual Supplementation Steps

### Step 1 — Pinterest Labels (Priority: Medium)

1. Log in to a Pinterest account (any personal or test account).
2. For each of the 40 queries in Section 1.2, open the corresponding Pinterest search URL from `pinterest-search-eval-58/data/observations.csv` (`pinterestUrl` column).
3. Dismiss or ignore the login modal (you are already logged in).
4. Take a screenshot of the category chip rail visible above/around the search results.
5. Record the chip text strings in the `labelsCount` and `notes` columns of `pinterest-search-eval-58/data/observations.csv`.
6. Update the `pinterestLabelsCount` column in `curify-gap-analysis-58.csv` for each query.

**Estimated effort:** ~2–3 min per query × 40 queries = ~80–120 min total.

### Step 2 — Canva CJK Queries (Priority: High — affects 21 data points)

1. Log in to a Canva account (free tier is sufficient for browsing templates).
2. For each of the 21 queries in Section 2.2, open the `canvaUrl` from `canva-search-eval-58/data/observations.csv`.
3. After authentication, the template grid should be visible. Scroll to capture at least 10 templates.
4. For each template, record:
   - `top1Title` through `top10Title` (template display name)
   - `top1TemplateUrl` through `top10TemplateUrl`
   - `labelsCount` (count of category filter chips visible on the page, e.g., "Presentation", "Poster", "Worksheet")
5. Take two screenshots (page1 = above-fold, page2 = scroll-down) and save to `canva-search-eval-58/screenshots/{query-id}/`.
6. Update `status` from `login_required` to `ok` or `partial` as appropriate.

**Estimated effort:** ~3–4 min per query × 21 queries = ~60–85 min total.

### Step 3 — Canva Partial Queries (Priority: Low)

1. For Q10 (葡萄酒): Re-visit while logged in, extract remaining 8 templates.
2. For Q15 (食物): Re-visit and confirm 10th template; update `topResultsCount` to 10 if found.

**Estimated effort:** ~5 min total.

---

## 5. Files to Update After Manual Completion

After collecting the missing data, update the following files in order:

| File | What to Update |
|------|---------------|
| `canva-search-eval-58/data/observations.csv` | Add top10 templates, labels, corrected status for 23 queries |
| `canva-search-eval-58/data/observations.json` | Sync JSON representation with observations.csv |
| `canva-search-eval-58/data/collection_progress.csv` | Mark previously failed queries as completed |
| `pinterest-search-eval-58/data/observations.csv` | Add labelsCount for 40 queries |
| `pinterest-search-eval-58/data/observations.json` | Sync JSON |
| `curify-gap-analysis-58.csv` | Update `pinterestLabelsCount` and `canvaLabelsCount` / `canvaTopResultsCount` for affected queries |
| `external-signal-5x2-summary.csv` | Recalculate `labelsZeroCount`, `avgLabelsCount`, `fullTop10Rate` for Pinterest and Canva |
| `external-signal-5x2-comparison-58.md` | Update platform comparison narrative and tables |
| `platform-scorecard-5x58.csv` | Update Pinterest/Canva label and result scores |
| `platform-scorecard-5x58-curify-centered.csv` | Update Curify-centered scoring that depends on competitor signals |

---

## 6. Prioritization

| Priority | Platform | Queries | Reason |
|----------|----------|---------|--------|
| P1 — High | Canva login_required CJK | 21 | Complete data blackout; these queries are entirely absent from Canva signal analysis |
| P2 — Medium | Pinterest missing labels | 40 | Labels needed to validate category signal; results exist but chips are null |
| P3 — Low | Canva partial (Q10, Q15) | 2 | Minor completeness gap; labels already captured |

---

## 7. Data Quality Context

For reference, the label counts currently observed across platforms:

| Platform | Avg Labels (creative) | Avg Labels (consumer) | Labels=0 count |
|----------|-----------------------|-----------------------|----------------|
| Google | 16.0 | 19.7 | 3/58 |
| Bing | 39.9 | 40.0 | 0/58 |
| Pinterest | 0.5 | 0.8 | **40/58** |
| Canva | 43.3 (ok queries) | 29.3 (ok queries) | **21/58 (login=0) + 8 partial** |

Pinterest's 0.5/0.8 average reflects the 40 zero-label queries dragging the mean down; the 18 queries that did get labels all recorded exactly 2, suggesting a consistent scraping limitation rather than a natural variation in Pinterest's chip count.

---

*Generated from: `external-signal-5x2-summary.csv`, `curify-gap-analysis-58.csv`, `pinterest-search-eval-58/data/observations.csv`, `canva-search-eval-58/data/observations.csv`*  
*Do not overwrite existing platform observation files — append or update specific rows only.*
