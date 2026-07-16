# Search → Click → Generate Funnel Metric Definitions

Grain, formulas, and computability, based strictly on evidence gathered from `curify-studio` (event grain: rows in `user_interactions`; generation grain: rows in `project`). Where the recommended conceptual formula from the manager brief does not match what the current event grain supports, the deviation and reason are noted explicitly.

---

### 1. Total searches
- **Meaning:** Volume of search attempts.
- **Grain:** `user_interactions` row, `action_type IN ('SEARCH','SEARCH_NORESULT','SEARCH_LOWRESULT')`.
- **Numerator/denominator:** N/A (raw count).
- **Attribution window:** N/A.
- **Required fields:** `action_type`, `created_at`. Present.
- **Computable:** APPROXIMATE. Computable as written, but **[SECONDARY evidence]** indicates healthy plain searches (≥5 results, no chip narrowing) never fire any event, so this systematically undercounts true search volume.
- **Confidence:** Medium (mechanism is clear; magnitude of undercount is unknown without frontend instrumentation change).

### 2. Search sessions
- **Meaning:** Distinct sessions containing ≥1 search.
- **Grain:** `COUNT(DISTINCT session_id) WHERE action_type IN (search family)`.
- **Required fields:** `session_id`. Present but nullable (not always populated).
- **Computable:** APPROXIMATE — same undercount caveat as #1, plus null `session_id` rows are excluded by convention in existing queries.

### 3. Unique search users
- **Meaning:** Distinct people who searched.
- **Numerator:** `COUNT(DISTINCT COALESCE(user_id::text, session_id))` over search-family rows.
- **Required fields:** `user_id`, `session_id`. Present.
- **Computable:** APPROXIMATE — same undercount caveat; anonymous `session_id` may not be stable across visits (no persistence guarantee), risking double-counting distinct anonymous "users."

### 4. Unique queries
- **Meaning:** Distinct query strings searched.
- **Numerator:** `COUNT(DISTINCT LOWER(TRIM(content_id)))` over search-family rows.
- **Required fields:** `content_id`. Present.
- **Computable:** APPROXIMATE — existing normalization (`LOWER(TRIM(...))`, used in `crud/admin.py`) does not strip the `|within=`/`|n=`/`|rw=`/`|paths=` suffixes, so the same logical query can fragment into multiple "distinct" strings.

### 5. Zero-result rate
- **Meaning:** Share of searches returning no results.
- **Formula (as evidenced):** `COUNT(action_type='SEARCH_NORESULT') / COUNT(action_type IN ('SEARCH','SEARCH_NORESULT','SEARCH_LOWRESULT'))` — deviates from the brief's generic "result_count == 0 / all searches" because there is no numeric `result_count` column; zero-result is its own event type instead.
- **Required fields:** `action_type`. Present.
- **Computable:** YES for the ratio as currently defined, but **APPROXIMATE in absolute meaning** — because the denominator excludes healthy searches that never fire an event, the computed rate is inflated relative to true zero-result rate over all searches (see main audit report §5, §22).

### 6. Low-result rate
- **Meaning:** Share of searches returning a "low" (non-zero but small) result count.
- **Formula (as evidenced):** `COUNT(action_type='SEARCH_LOWRESULT') / COUNT(search-family rows)`. The threshold (5, per **[SECONDARY]** `SearchResultsClient.tsx`) is baked into the frontend's event-firing logic, not configurable from the backend/admin side.
- **Computable:** YES for the ratio as defined; same inflation caveat as #5.

### 7. Search result impression rate
- **Meaning:** Share of rendered results actually seen by the user.
- **Required fields:** an impression event with `search_id`/`result_id`. **MISSING entirely.**
- **Computable:** NO.

### 8. Search CTR
- **Recommended brief formula:** "search sessions with ≥1 result click / search sessions with ≥1 visible result." **Cannot be computed exactly as worded** — there is no "visible result" (impression) event, so the denominator must be approximated as "search sessions with ≥1 search event" instead, per the code's actual definition in `_section_search_queries` (`result_ctr_pct = result_clicks / searches`).
- **Grain:** per query string, 7-day window, `crud/admin.py::_section_search_queries`.
- **Attribution window:** 5 minutes, same-user/session key.
- **Computable:** APPROXIMATE (computable today via the existing query, but biased by the search-event undercount and the 5-minute heuristic).

### 9. Internal-result CTR
- **Meaning:** CTR restricted to internal (Curify-hosted) results.
- **Computable:** YES today, trivially — because 100% of current results are internal, this metric is numerically identical to metric #8 until Hybrid Search introduces external results with a `result_source` field.

### 10. External-result CTR (future Hybrid Search)
- **Required fields:** `result_source`/`destination_domain`. **MISSING** — no external results exist yet.
- **Computable:** NO (not yet applicable; needs new instrumentation before it means anything).

### 11. Search-to-generate rate
- **Recommended brief formula:** "search sessions followed by successful generation within the attribution window / all search sessions."
- **Deviation required:** cannot be computed as an ordered, windowed, per-session sequence — no code joins `user_interactions` SEARCH rows to `project` COMPLETED rows at all, windowed or otherwise.
- **Nearest available proxy:** `surface_cohorts`'s `searcher` × `did_replicate` cross-tab — a same-week (7-day), unordered, cohort-level co-occurrence rate, not a per-session conversion rate.
- **Computable:** NO as specified. A rough population-level proxy exists but does not satisfy the metric's own definition (it is not ordered, not session-scoped, and "replicate" ≠ "successful generation" one-for-one since it also includes COPY/REMIX click-log events, not confirmed `Project.status='COMPLETED'`).

### 12. Click-to-generate rate
- **Recommended brief formula:** "search-result click sessions followed by successful generation / search-result click sessions."
- **Computable:** NO. No join exists between click events and `Project` rows at all (see attribution feasibility doc). Would require net-new engineering: a time-windowed join between `user_interactions` (`CLICK` on `/search`) and `project` (`status='COMPLETED'`) keyed by `user_id` only — and even that could not cover anonymous users, since `Project` lacks `session_id`.

### 13. Generation-start rate
- **Meaning:** Share of generation attempts that actually start processing.
- **Formula:** `COUNT(status IN ('STARTED','PREPROCESSING',...)) / COUNT(all project rows created)`.
- **Required fields:** `Project.status`. Present.
- **Computable:** YES — directly from the `project` table, but **entirely independent of search** (no search linkage).

### 14. Generation-success rate
- **Formula:** `COUNT(status='COMPLETED') / COUNT(status IN ('COMPLETED','FAILED'))`.
- **Required fields:** `Project.status`. Present.
- **Computable:** YES — directly from the `project` table, independent of search.

### 15. Search refinement/requery rate
- **Meaning:** Share of search sessions where the user issues a second, different query shortly after the first.
- **Required fields:** `session_id`, `content_id`, `created_at` on consecutive search-family rows. Present but no existing query computes this.
- **Computable:** APPROXIMATE / DERIVABLE — fields exist to build this query, but it is not currently implemented anywhere in the repo. Would need to define a "shortly after" window and a distinctness rule (accounting for the `|within=`/`|rw=` suffix noise in #4).

### 16. Search abandonment rate
- **Meaning:** Share of searches with no subsequent click at all.
- **Formula:** `1 − (searches with had_result_click OR had_chip_click OR had_escape_click) / searches`.
- **Computable:** APPROXIMATE — directly derivable as the complement of the existing `_section_search_queries` attribution logic; inherits the same undercount and 5-minute-window caveats.

### 17. Result-rank CTR
- **Required fields:** `result_rank`. **MISSING entirely.**
- **Computable:** NO.

### 18. Query-level conversion rate (query → generate)
- **Required fields:** a join from query text through to `Project.status='COMPLETED'`. **MISSING** — same gap as #11/#12, at query grain instead of session grain.
- **Computable:** NO.

### 19. Internal-result preservation rate (future Hybrid Search)
- **Meaning:** Share of queries where internal results remain visible/clicked after external results are introduced.
- **Required fields:** `result_source`, historical baseline. **MISSING** (no external results exist yet to compare against).
- **Computable:** NO (not applicable yet; needed before/during Hybrid Search rollout).

### 20. External exit rate (future Hybrid Search)
- **Meaning:** Share of users who click an external result and do not return to generate.
- **Required fields:** `destination_domain`, `external_click` flag, return/generate tracking. **MISSING entirely.**
- **Computable:** NO.

---

## Summary table

| # | Metric | Computable now | Confidence |
|---|---|---|---|
| 1 | Total searches | APPROXIMATE | Medium |
| 2 | Search sessions | APPROXIMATE | Medium |
| 3 | Unique search users | APPROXIMATE | Medium |
| 4 | Unique queries | APPROXIMATE | Medium |
| 5 | Zero-result rate | APPROXIMATE (ratio computable, magnitude biased) | Medium |
| 6 | Low-result rate | APPROXIMATE (ratio computable, magnitude biased) | Medium |
| 7 | Search result impression rate | NO | High (confirmed missing) |
| 8 | Search CTR | APPROXIMATE | Medium |
| 9 | Internal-result CTR | YES (== #8 today) | High |
| 10 | External-result CTR | NO (not yet applicable) | High |
| 11 | Search-to-generate rate | NO (proxy exists, doesn't meet definition) | High |
| 12 | Click-to-generate rate | NO | High |
| 13 | Generation-start rate | YES (search-independent) | High |
| 14 | Generation-success rate | YES (search-independent) | High |
| 15 | Search refinement/requery rate | APPROXIMATE / DERIVABLE (not built) | Medium |
| 16 | Search abandonment rate | APPROXIMATE (derivable from existing query) | Medium |
| 17 | Result-rank CTR | NO | High (confirmed missing) |
| 18 | Query-level conversion rate | NO | High |
| 19 | Internal-result preservation rate | NO (future) | High |
| 20 | External exit rate | NO (future) | High |
