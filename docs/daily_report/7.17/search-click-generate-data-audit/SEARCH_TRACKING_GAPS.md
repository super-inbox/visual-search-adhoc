# Search → Click → Generate: Instrumentation Gap Analysis

Repository: `curify-studio` @ `7b3fa5b40b03da3056536257ead2200dab031247`

This document lists missing instrumentation independent of any specific future Hybrid Search rollout (see `HYBRID_SEARCH_INSTRUMENTATION_REQUIREMENTS.md` for that specific, forward-looking checklist). These are gaps in the *current* system that already limit today's reporting.

## 1. No stable `search_id`
No search event is ever assigned a persisted, passed-through identifier. The closest thing (a SQL-local UUID alias in one analyst script) never leaves that single query. **Impact:** every downstream link (click, generate) can only ever be approximated via time-window + user/session key heuristics, which are demonstrably lossy (see `SEARCH_ATTRIBUTION_FEASIBILITY.md`).

## 2. No search result impression event
There is no event fired when result cards are rendered/visible to the user. **Impact:** true CTR (clicks / impressions) cannot be computed; the current "CTR" is really clicks / search-events, a different and less meaningful denominator, and one that is itself undercounted (see #6 below).

## 3. No `result_rank` / `result_id` on click events
Clicks only carry a generic `content_id` (the clicked item's identifier) and `content_type`. **Impact:** no rank-level CTR, no way to tell if users click top results vs. scroll deep, no way to evaluate ranking-algorithm changes.

## 4. No `result_source` (internal vs. external)
Not yet needed today because all results are internal, but its absence means the schema is not ready to distinguish sources the moment Hybrid Search ships. **Impact:** any Hybrid Search rollout done without this field first will make Search CTR and Internal CTR indistinguishable, hiding the specific risk described in the manager's business question (Q22).

## 5. `GENERATE` click-log event is disconnected from the real generation pipeline
`action_type='GENERATE'` rows in `user_interactions` are written by the frontend's tracking wrapper (a `track()` call), while the actual `Project` row that represents a real generation attempt is created by a completely separate call to `/nano-templates/generate` or `/nano-freeform/generate`. Neither code path calls the other. **Impact:** even the coarse "did they generate" signal used in `surface_cohorts`/`engagement_funnel`/`replication_analysis` may not correspond 1:1 with an actual successful (or even attempted) generation in the `project` table — it only proves the user clicked something the frontend labeled a generate action.

## 6. Frontend search-event firing is conditional, not universal **[SECONDARY — curify-frontend, out of scope, cited for context]**
Per `SearchResultsClient.tsx`, a healthy plain search (≥5 results, no topic-chip narrowing) never fires any `SEARCH`-family event — only zero-result, low-result, or chip-narrowed searches are logged. **Impact:** every volume-based metric (#1–#9 in `SEARCH_FUNNEL_METRIC_DEFINITIONS.md`) is built on a denominator that systematically excludes a likely-large share of successful top-of-funnel searches, biasing the reported zero-/low-result rate upward and CTR in an unknown direction.

## 7. No `session_id` on the generation record (`Project` table)
`Project` (`curify_background/app/models/project.py`) has `user_id` but no `session_id`. **Impact:** anonymous (not-logged-in) generations can never be linked back to any anonymous search/click history, even if a `search_id`/time-window join were built — this is a structural, not just a missing-field, gap.

## 8. No numeric `result_count` column
Result count is only encoded as a string suffix (`|n=<count>`) inside `content_id`, and only for low-result events. **Impact:** cannot bucket/aggregate by exact result count, cannot compute a true low-result threshold sensitivity analysis without brittle string parsing.

## 9. Query text is not normalized at write time
Normalization (`LOWER(TRIM(...))`) happens only ad hoc, inside individual SQL queries at read time, and does not strip the `|within=`/`|n=`/`|rw=`/`|paths=` suffixes. **Impact:** "unique queries" and per-query rollups can fragment the same logical query into multiple rows, and any change to the suffix format silently breaks every downstream query that assumes the current format.

## 10. No scheduled/precomputed reporting layer
There is no cron job or scheduled task that computes or refreshes funnel metrics. The one materialized view built for this purpose (`bot_free_30d`) is dead code because Supabase's `pg_cron` is not enabled — nothing refreshes it, and the code reverted to computing everything live (with a 30-minute in-process cache) on 2026-06-08. **Impact:** no historical metric snapshots exist for trend analysis beyond what's recomputable from raw event history; every dashboard load recomputes from scratch, which will not scale as event volume grows.

## 11. Inconsistent test-user exclusion lists
Hardcoded test-user ID exclusion differs across files: `(155, 1117, 1267)` in some queries, `(155, 1117)` in others. **Impact:** a data-quality/reproducibility risk — different analytics sections may include or exclude the same test traffic inconsistently, making cross-metric comparisons unreliable at the margins.

## 12. A referenced analysis script is missing from the repo
`dev/jayw/admin_analysis/use_case_chip_clicks_pull.py` references a `session_funnel_30d_pull.py` file that does not exist in this checkout. **Impact:** unclear whether this represents lost/uncommitted analysis work relevant to the funnel question — worth asking the analyst (Jay W.) directly rather than assuming its contents.

---

## Priority summary (cross-reference with `HYBRID_SEARCH_INSTRUMENTATION_REQUIREMENTS.md`)

| Gap | Priority | Blocks |
|---|---|---|
| #1 No search_id | P0 | All precise funnel attribution; any A/B test |
| #2 No impression event | P0 | True CTR; impression-based ranking evaluation |
| #3 No result_rank/result_id on clicks | P0 | Rank CTR; ranking algorithm evaluation |
| #5 GENERATE event disconnected from Project | P0 | Any Click→Generate or Search→Generate metric |
| #7 No session_id on Project | P0 | Anonymous-user funnel coverage |
| #4 No result_source | P1 (P0 before Hybrid Search ships) | Internal vs. external CTR; external exit rate |
| #6 Conditional search-event firing | P1 | Accuracy of all volume/rate metrics |
| #8 No numeric result_count | P2 | Result-count bucket analysis |
| #9 No write-time query normalization | P2 | Unique-query accuracy |
| #10 No scheduled reporting layer | P2 | Historical trend analysis, scale |
| #11 Inconsistent test-user exclusion | P2 | Cross-metric reproducibility |
| #12 Missing referenced script | P2 (informational) | Unknown — needs follow-up with author |
