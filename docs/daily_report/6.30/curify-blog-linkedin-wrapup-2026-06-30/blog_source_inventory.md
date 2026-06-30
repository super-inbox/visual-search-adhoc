# Blog Source Inventory — Curify Search Benchmark & Refresh
**Prepared:** 2026-06-30  
**Purpose:** Ground truth for blog, LinkedIn, and updated comparison report

---

## 1. Query Set

**The benchmark used 58 queries, not 57.**

Source: `curify-frontend-cleanup-2026-06-30/docs/external-signal-pilot/external-signal-5x2-query-classification-58.csv`  
- 58 queries total: 30 primaryIntent=creative, 28 primaryIntent=consumer, 11 hybrid (split into primary above)
- Queries span CJK, English, and mixed-language educational/creative/consumer categories

The current `scripts/configs/search_eval_set.json` in curify-frontend is a **different, larger set (125 queries)** — expanded over time for regression testing. The 58-query benchmark is the external-signal pilot set and is the correct baseline for 5-platform comparison.

---

## 2. Old 5-Platform Benchmark Data (Baseline — June 2026, pre-PR #512)

| File | Content |
|------|---------|
| `docs/external-signal-pilot/platform-scorecard-5x58.csv` | Platform scorecard (6 dimensions × 5 platforms) |
| `docs/external-signal-pilot/platform-scorecard-5x58-curify-centered.csv` | Curify-centered version of the scorecard |
| `docs/external-signal-pilot/external-signal-5x2-comparison-58.md` | Full 5-platform narrative report (generated 2026-06-21) |
| `docs/external-signal-pilot/external-signal-5x2-query-classification-58.csv` | Intent classification for all 58 queries |
| `docs/external-signal-pilot/external-signal-5x2-summary.csv` | Per-query summary across 5 platforms |
| `docs/external-signal-pilot/curify-search-eval-58/data/observations.csv` | Curify per-query observations (baseline) |
| `docs/external-signal-pilot/bing-image-eval-58/data/observations.csv` | Bing Images per-query observations |
| `docs/external-signal-pilot/canva-search-eval-58/data/observations.csv` | Canva per-query observations |
| `docs/external-signal-pilot/pinterest-search-eval-58/data/observations.csv` | Pinterest per-query observations |
| `docs/external-signal-pilot/google-image-eval-58/data/collection_progress.csv` | Google Images collection status |
| `docs/external-signal-pilot/label-count-statistics-report-2026-06-23.md` | Verified label count stats (Bing=39.9, Canva=58.2, Google=17.8, Curify=8.8, Pinterest=0.6) |
| `docs/external-signal-pilot/label-count-by-query-2026-06-23.csv` | Per-query label counts for all 5 platforms |

All files are under: `curify-frontend-cleanup-2026-06-30/`  
All external platform data (Google, Bing, Pinterest, Canva) is from June 19–23, 2026. This is the stable baseline — do NOT re-crawl.

---

## 3. Curify-Specific Gap Analysis (Baseline, pre-PR #512)

| File | Content |
|------|---------|
| `docs/external-signal-pilot/curify-gap-analysis-58.csv` | Per-query gap classification (P0/P1/ok) |
| `docs/external-signal-pilot/p1-template-gap-retest-2026-06-23.csv` | P1 template gap retest results |
| `docs/external-signal-pilot/p1-template-gap-retest-2026-06-23.md` | P1 template gap retest narrative |
| `docs/external-signal-pilot/pinterest-canva-missing-data-report-2026-06-23.md` | Pinterest/Canva data gaps explained |
| `docs/external-signal-pilot/CURIFY_CENTERED_EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md` | Curify-centered insights (English) |
| `docs/external-signal-pilot/EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md` | Full 5-platform insights (English) |

---

## 4. Post-PR #512 Curify Refresh (New — 2026-06-30)

| File | Content |
|------|---------|
| `curify-blog-linkedin-wrapup-2026-06-30/curify_refresh_after_pr512.csv` | All 58-query programmatic refresh results |
| `curify-blog-linkedin-wrapup-2026-06-30/curify_refresh_after_pr512_report.md` | Refresh narrative with delta analysis |

**Methodology:** Programmatic scoring only (local tokenizer + nano_inspiration.json + template i18n blobs). No LLM calls. Mirrors `eval_search.cjs` logic. Run on `main` at commit `a1a60bc5` after PR #512 merge.

---

## 5. PR #512 Sanity Retest (10 Queries, Manual Live Verification)

| File | Content |
|------|---------|
| `curify-blog-linkedin-wrapup-2026-06-30/sanity_retest.csv` | 10-query manual live results |
| `curify-blog-linkedin-wrapup-2026-06-30/sanity_retest_report.md` | Manual live verification report |

Complementary to the 58-query programmatic refresh. These 10 queries were verified live in production (with LLM rewriter active, Redis gallery enabled).

---

## 6. Additional Supporting Reports

| File | Content |
|------|---------|
| `p0-p1-gap-retest-2026-06-30/report.md` | P0/P1 gap retest on 125-query eval set (branch: baobao/multi-intent-topic-cooccurrence) |
| `search-architecture-review-p0-5-2026-06-30/report.md` | Architecture review P0.5 |
| `docs/daily_report/6.22-23/label-count-statistics-report-2026-06-23.md` | Label count report (zh) |
| `docs/daily_report/6.21/CURIFY_CENTERED_EXTERNAL_SIGNAL_INSIGHTS_2026-06-21_zh.md` | Curify-centered insights (zh) |
| `docs/daily_report/6.21/EXTERNAL_SIGNAL_INSIGHTS_2026-06-21_zh.md` | Full insights (zh) |

---

## 7. Answers to Key Questions

### Was the benchmark 57 or 58 queries?
**58 queries.** The external-signal pilot set (`external-signal-5x2-query-classification-58.csv`) has exactly 58 entries. No record of a 57-query version.

### Which numbers are safe to use in the blog?

| Claim | Source | Safe? |
|-------|--------|-------|
| Bing avg 39.9 related-search chips/query | `label-count-statistics-report-2026-06-23.md` (verified, recomputed) | ✅ Yes |
| Google avg 17.8 related-search chips/query | Same report, verified | ✅ Yes |
| Canva avg 58.2 labels/ok query (36/58 accessible) | Same report, verified | ✅ Yes (cite 36/58 caveat) |
| Pinterest 40/58 queries = 0 labels (login modal) | Same report, verified | ✅ Yes |
| Curify avg 8.8 intent-cluster chips/query | Same report, verified | ✅ Yes |
| Curify baseline: 5/58 ok_empty (recipe cluster) | `platform-scorecard-5x58.csv` | ✅ Yes |
| Curify baseline creative rich rate: 33% | Computed from `observations.csv` | ✅ Yes |
| Curify post-PR #512 creative rich rate: 57% | `curify_refresh_after_pr512.csv` (programmatic) | ✅ Yes (note: programmatic, not live) |
| 18/58 queries improved bucket after PR #512 | `curify_refresh_after_pr512.csv` | ✅ Yes (programmatic) |
| ESL flashcards: thin(4) → rich(16) | Programmatic refresh | ✅ Yes |
| Spanish vocabulary: thin(4) → rich(15) | Programmatic refresh | ✅ Yes |
| Canva CJK queries: 21/58 login_required | `platform-scorecard-5x58.csv` | ✅ Yes |

### Which data is old baseline (do not freshen)?
All Google Images, Bing Images, Pinterest, Canva data — collected June 19–23, 2026. Do not re-crawl.

### Which data is new after PR #512?
- `curify_refresh_after_pr512.csv` — Curify programmatic re-score on 58-query set
- `sanity_retest.csv` — manual live verification on 10 representative queries

---

## 8. Curify Refresh Key Stats (Post-PR #512, Programmatic)

| Metric | Before PR #512 | After PR #512 | Delta |
|--------|---------------|---------------|-------|
| Empty queries (of 58) | ~8 | 6 | -2 |
| Rich queries (of 58) | ~35 | 41 | +6 |
| Creative rich rate (30 creative queries) | ~33% (10/30) | 57% (17/30) | +24pp |
| Consumer rich rate (28 consumer queries) | ~82% (23/28) | 86% (24/28) | +4pp |
| Improved bucket (↑) | — | 18/58 | — |
| Regressed bucket (↓) | — | 4/58 | — |
| Stable (=) | — | 36/58 | — |

Notable regressions (4 queries) warrant investigation:  
- `香薰`: rich→moderate (5 hits programmatic; may be P0.1 re-enrichment side-effect)  
- `phonics worksheets kindergarten`: thin→empty (alias fix shipped on a different branch, not yet in main)  
- `bilingual flashcards for kids learning korean fruits`: moderate→thin (strict token count issue with 6-token query)  
- `samurai`: rich→moderate (minor, 9 hits vs 10 threshold)
