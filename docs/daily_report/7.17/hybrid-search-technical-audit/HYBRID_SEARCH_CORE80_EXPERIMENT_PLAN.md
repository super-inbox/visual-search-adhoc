# Hybrid Search — Core-80 Offline Experiment Plan (Design Only, Not Executed)

This document specifies the plan for an 80-query × 5-mode = 400 mode-run offline experiment. **Nothing in this plan has been run.** Per the task brief, this audit assumes a *future* session will produce `hybrid_search_core_eval_80.csv`; this document defines what that session needs to do and measure.

## Core-80 query set composition (target distribution)

Reuses the existing seed philosophy already established in `docs/eval-framework-visual-search-benchmark-2026-06-14.md` ("~50 already calibrated in `lib/popularPrefillQueries.ts` + ~50 picked to span gaps," line 77) and the existing `scripts/configs/search_eval_set.json` regression buckets (`rich`/`moderate`/`thin`/`empty`/`rewrite_recovery`/`rewrite_empty`, per `docs/search-quality.md` lines 156-166) — cross-referencing existing eval infrastructure rather than inventing a disconnected new one.

| Dimension | Target coverage | Source |
|---|---|---|
| Category | Creative/Merch, Brand/Business, Marketing/Ecommerce, Education | New categorization needed — cross-reference against `lib/intent_taxonomy.ts` tier-1 topics for consistent labeling |
| Language | Chinese and English (minimum) | Matches the CJK-handling emphasis already built into `buildSearchTokens`/`normalizeForSearch`/`tsToSc` |
| Result-count band | zero-result, low-result, medium-result, strong-result | Directly reuses the `rich`/`moderate`/`thin`/`empty` bucket naming from `scripts/configs/search_eval_set.json` (referenced, not opened in full this pass — confirm exact bucket definitions before reuse) |
| Sub-domain examples | apparel/shirt, teaching materials, drawing/illustration, toys/merch/creative products | Should map to real `CATALOG_CONTEXT` families already enumerated in `lib/searchRewrite.ts:39-57` (vocabulary flashcards, MBTI cards, infographics, travel, watercolor, portraits, lifestyle/design) so query selection isn't arbitrary relative to what the catalog actually contains |

**Recommendation**: draw a meaningful fraction of the 80 from the *existing* `scripts/configs/search_eval_set.json` regression set (if its structure supports it) rather than building an entirely disjoint list — this lets the hybrid experiment also serve as a regression check against known-thin queries the search-quality team already tracks, doubling the value of the same 80-query effort. This requires opening that file in the execution session (not done in this audit pass) to confirm compatibility.

## 400 mode-runs = 80 queries × 5 modes (A/B/C/D/E per Mode Matrix, Deliverable 8)

## Required fields per mode-run (schema for `hybrid_search_core_eval_80.csv`)

| Field | Type | Notes |
|---|---|---|
| core_id | string | Stable id per query, independent of mode, so all 5 mode-runs for one query can be joined |
| query | string | Raw query text |
| language | string | ISO-ish locale tag (en/zh/...) |
| scenario | string | Free-text scenario label (e.g. "apparel/shirt") |
| category | string | One of the 4 target categories above |
| mode | string | A / B / C / D / E |
| initial_internal_count | int | Pre-rewrite internal count — corresponds to `initialThinCount` (page.tsx:611) |
| rewrite_triggered | bool | Whether `getMultiQueryPaths` fired (modes B/D/E only) |
| raw_rewrite | string | The raw LLM output before sanitization, for debugging |
| accepted_rewrite | string | The sanitized rewrite(s) actually used |
| second_internal_count | int | Internal count after rewrite-expanded retrieval (modes B/D/E) |
| external_triggered | bool | Whether the external call fired (modes C/D/E only) |
| external_provider | string | Provider used (or "none"/"mocked" if this run predates live provider access) |
| external_count | int | Raw external results returned |
| merged_count | int | Final merged result count shown |
| internal_count_top_12 | int | Internal results within the first-screen 12 positions |
| external_count_top_12 | int | External results within the first-screen 12 positions |
| latency_ms | float | Total wall-clock for this mode-run |
| rewrite_cost_estimate | float | Estimated $ cost of the LLM call, if any |
| external_cost_estimate | float | Estimated $ cost of the external call, if any |
| error | string/null | Any error encountered |
| timeout | bool | Whether any leg timed out |
| top_results | string (JSON) | Serialized top-N result summaries for manual/LLM review |
| automated_relevance | float/null | Any automatable relevance proxy score (e.g. tag-overlap heuristic) — NOTE per Extension B: Curify has no real relevance-label model yet, so this field is a heuristic proxy, not ground truth |
| manual_relevance | int/null | Human-scored relevance (0-5 scale, matching the existing benchmark doc's scoring convention) |
| intent_drift | bool | Reviewer flags whether the rewrite/external results drifted from the user's apparent intent |
| unsafe_or_irrelevant_external_result | bool | Safety/relevance flag for external content specifically |
| broken_image_or_link | bool | Whether any external result's image/link failed to load |
| internal_result_preserved | bool | Verifies the hard guarantee (Failure/Cache/Cost spec) — did internal results survive even when external/LLM legs were exercised |

## Evaluation metrics

**Relevance**
- Top-1 relevance, Top-5 relevance (from `manual_relevance` scores)
- PASS/PARTIAL/FAIL classification per mode-run (reviewer judgment, using a rubric to be defined at execution time — not defined in this audit)
- Zero-result reduction rate (mode C/D/E vs. mode A, per query in the zero-result band)
- Low-result reduction rate (same, for the low-result band)

**Product safety**
- Internal result preservation rate = `count(internal_result_preserved=true) / count(all mode-runs where internal results existed pre-hybrid)`
- External share in top 12 = `avg(external_count_top_12 / 12)` across mode C/D/E runs
- Intent drift rate = `count(intent_drift=true) / count(mode-runs with rewrite_triggered or external_triggered)`
- Misleading-source rate = manual audit of `top_results` for any case an external result was rendered without clear attribution (requires the actual UI mockup to exist, not just data — offline data alone cannot fully verify this; flag as a limitation)
- Unsafe/irrelevant external result rate = `count(unsafe_or_irrelevant_external_result=true) / count(external results reviewed)`
- Broken image/link rate = `count(broken_image_or_link=true) / count(external results reviewed)`

**Engineering**
- P50/P95 latency per mode (from `latency_ms`)
- Timeout rate = `count(timeout=true) / count(mode-runs)`
- Error rate = `count(error is not null) / count(mode-runs)`
- Estimated cost/query = `avg(rewrite_cost_estimate + external_cost_estimate)` per mode
- Cache potential = fraction of the 80 queries that are plausible repeats of common real-world queries (informed judgment, not measurable from this dataset alone)

**Business hypothesis** (explicitly hypotheses, not measured facts — offline data cannot prove business outcomes)
- Likely internal click opportunity — qualitative judgment from reviewers on whether internal results in view would plausibly be clicked
- Likely external click opportunity — same, for external results
- Likely generate opportunity — same, whether either result type plausibly leads to a "Make with Curify" or Remix click
- Risk of user leaving Curify — qualitative flag when an external result's destination is a strong content match that doesn't obviously funnel back
- Risk of internal click cannibalization — qualitative flag when an external result appears more visually compelling than a co-displayed internal result for the same query

## Explicit limitation (required statement)

**Offline evaluation cannot prove actual CTR or generation improvement.** The Core-80 plan produces relevance, safety, and engineering signal sufficient to select a candidate mode and trigger threshold for a staged rollout — it cannot substitute for the online experiment (Deliverable 13), which is the only way to observe real click and generation behavior.
