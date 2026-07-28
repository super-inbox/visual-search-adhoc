# Progress Status — Vertical Page SEO Research

**Status:** IN_PROGRESS
**Date:** 2026-07-29
**Computed from:** `TOP_PAGE_INPUT.csv` and `screenshots/` in this folder (counts below are derived by
parsing the CSV with Python's `csv` module and listing the screenshot directories, not hand-entered).

This document is a snapshot of where the manual research stands, generated to accompany a routine
copy of this folder into the `visual-search-adhoc` repo. It is **not** the final Vertical Page SEO
Research and Design deliverable.

## 1. Completed so far

- Repo-side audit complete: `CURRENT_CURIFY_PAGE_AUDIT.md` (gap analysis of the current
  `nano-template/[slug]` template/example pages against `VerticalPageSchema v1`, 7 sections).
- Research rubric defined: `RESEARCH_RUBRIC.md` (identification, on-page SEO structure, core content
  modules, site architecture signals, category-specific differentiators, assessment — not yet
  applied to individual competitor pages, see §4).
- Search Query Plan finalized: `SEARCH_QUERY_PLAN.md` — **4 categories × 6 queries = 24 queries**
  (MBTI, Education, Creative Merch, Ecommerce Content).

## 2. Query completion — by the numbers

| Category | Queries in plan | Queries filled in | Remaining |
|---|---|---|---|
| MBTI | 6 | 6 | 0 |
| Education | 6 | 4 | 2 |
| Creative Merch | 6 | 0 | 6 |
| Ecommerce Content | 6 | 0 | 6 |
| **Total** | **24** | **10** | **14** |

"Filled in" = row in `TOP_PAGE_INPUT.csv` has a non-empty `rank_observed` (and the rest of the row
populated). Verified: no row has `rank_observed` empty while other result fields are filled, and no
row has `rank_observed` filled while other fields are empty — the filled/empty split is clean.

## 3. FINAL SELECTED / NOT SELECTED — by category

| Category | FINAL SELECTED | NOT SELECTED |
|---|---|---|
| MBTI | 5 | 1 |
| Education | 4 | 0 |
| Creative Merch | 0 | 0 |
| Ecommerce Content | 0 | 0 |
| **Total** | **9** | **1** |

(MBTI's one NOT SELECTED row — `MBTI compatibility chart Pinterest` — was intentionally passed over
because Pinterest was already selected for a different MBTI query in the same category, per
`manual_notes` in the CSV; kept as supporting SERP evidence.)

## 4. Not yet done

- **14 remaining queries**: 2 in Education (`printable phonics worksheet`,
  `Teachers Pay Teachers commercial use license worksheet`), all 6 in Creative Merch, all 6 in
  Ecommerce Content.
- **Competitor page deep-dive analysis**: `RESEARCH_RUBRIC.md` has not yet been applied to any of the
  9 FINAL SELECTED pages (or the 1 NOT SELECTED page). Only the Google SERP-level selection has been
  recorded so far — no per-page rubric scoring exists yet.
- **Pattern matrix**: no cross-category pattern/comparison matrix has been produced yet.
- **Four vertical-page design proposals**: no design proposal (for MBTI, Education, Creative Merch,
  or Ecommerce Content) has been written yet — this depends on the rubric analysis and pattern matrix
  above, neither of which is complete.

## 5. Screenshot naming — important caveat

Screenshots under `screenshots/<category>/<category>-NN-page.png` (e.g.
`screenshots/mbti/mbti-01-page.png`) are **Google SERP screenshots**, not screenshots of the selected
competitor page's own content. This is confirmed directly in the CSV's `manual_notes` for the
Education rows ("The screenshot_path is a Google SERP screenshot, not a competitor-page screenshot.")
and is consistent across the MBTI rows as well (notes describe SERP features — Images pack, AI
Overview, People also ask — not the destination page). This is the existing naming convention used by
the researcher; it has **not** been renamed or altered as part of this copy/validation pass.

## 6. Snapshot disclaimer

This folder, as copied into `visual-search-adhoc`, reflects the state of the research at the time of
copy (2026-07-29). It is a phased/in-progress snapshot — 10 of 24 queries researched, 0 of 9-10
selected pages rubric-scored, no pattern matrix, no design proposals — and should not be read as the
completed Vertical Page SEO Research and Design deliverable.
