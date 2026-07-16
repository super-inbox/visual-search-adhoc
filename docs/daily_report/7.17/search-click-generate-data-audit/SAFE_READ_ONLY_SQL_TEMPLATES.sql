-- ============================================================================
-- SAFE READ-ONLY SQL TEMPLATES — Search -> Click -> Generate Funnel
-- Repository audited: curify-studio @ 7b3fa5b40b03da3056536257ead2200dab031247
-- ============================================================================
-- THESE TEMPLATES WERE NOT EXECUTED. This is a static audit deliverable only.
-- Do not run against production without separate authorization and review.
--
-- Schema basis (evidenced, not invented):
--   user_interactions(id uuid, user_id int NULL, user_ip text, user_agent text,
--                      content_id text, content_type enum, action_type enum,
--                      session_id text NULL, view_mode text, referrer text,
--                      current_page_url text, current_page_route text,
--                      created_at timestamptz)
--     source: curify_background/app/models/interactions.py
--   project(project_id text PK, user_id int, status enum, job_settings_raw jsonb,
--            runtime_config jsonb, cost_credits numeric, created_at, started_at, updated_at)
--     source: curify_background/app/models/project.py
--
-- Join-key convention used throughout the real codebase (crud/admin.py):
--   who = COALESCE(user_id::text, session_id)
--
-- Assumptions/placeholders are called out explicitly with [PLACEHOLDER] where
-- the required column does not exist in the evidenced schema.
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1. Daily search volume
-- Caveat: undercounts true search volume — a healthy, un-narrowed search with
-- >=5 results never fires a SEARCH-family event per curify-frontend evidence
-- (SearchResultsClient.tsx), so this measures "notable" searches, not all searches.
-- ----------------------------------------------------------------------------
SELECT
    DATE_TRUNC('day', created_at) AS day,
    COUNT(*) AS search_events,
    COUNT(*) FILTER (WHERE action_type = 'SEARCH')          AS healthy_narrowed_searches,
    COUNT(*) FILTER (WHERE action_type = 'SEARCH_NORESULT') AS zero_result_searches,
    COUNT(*) FILTER (WHERE action_type = 'SEARCH_LOWRESULT') AS low_result_searches
FROM user_interactions
WHERE action_type IN ('SEARCH', 'SEARCH_NORESULT', 'SEARCH_LOWRESULT')
  AND created_at >= :start_date  -- bounded date filter, e.g. NOW() - INTERVAL '30 days'
  AND created_at <  :end_date
  AND (user_id IS NULL OR user_id NOT IN (:test_user_ids))  -- e.g. (155, 1117, 1267); confirm current list before use
GROUP BY 1
ORDER BY 1;


-- ----------------------------------------------------------------------------
-- 2. Unique search users
-- Aggregated only; no raw user_id list is selected.
-- ----------------------------------------------------------------------------
SELECT
    DATE_TRUNC('day', created_at) AS day,
    COUNT(DISTINCT COALESCE(user_id::text, session_id)) AS unique_search_identities
FROM user_interactions
WHERE action_type IN ('SEARCH', 'SEARCH_NORESULT', 'SEARCH_LOWRESULT')
  AND created_at >= :start_date
  AND created_at <  :end_date
GROUP BY 1
ORDER BY 1;


-- ----------------------------------------------------------------------------
-- 3. Unique queries
-- Caveat: content_id may carry unstripped suffixes (|within=, |n=, |rw=, |paths=)
-- per curify-frontend evidence, so this may overcount distinct logical queries.
-- ----------------------------------------------------------------------------
SELECT
    COUNT(DISTINCT LOWER(TRIM(content_id))) AS unique_query_strings
FROM user_interactions
WHERE action_type IN ('SEARCH', 'SEARCH_NORESULT', 'SEARCH_LOWRESULT')
  AND content_id IS NOT NULL
  AND created_at >= :start_date
  AND created_at <  :end_date;


-- ----------------------------------------------------------------------------
-- 4. Zero-result rate
-- Caveat: denominator excludes un-narrowed healthy searches (see template 1) —
-- this rate is inflated relative to the true share of all search attempts.
-- ----------------------------------------------------------------------------
SELECT
    DATE_TRUNC('day', created_at) AS day,
    COUNT(*) FILTER (WHERE action_type = 'SEARCH_NORESULT') AS zero_result_count,
    COUNT(*) AS tracked_search_events,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE action_type = 'SEARCH_NORESULT')
        / NULLIF(COUNT(*), 0), 1
    ) AS zero_result_pct
FROM user_interactions
WHERE action_type IN ('SEARCH', 'SEARCH_NORESULT', 'SEARCH_LOWRESULT')
  AND created_at >= :start_date
  AND created_at <  :end_date
GROUP BY 1
ORDER BY 1;


-- ----------------------------------------------------------------------------
-- 5. Low-result rate
-- Threshold (5 results) is a frontend constant [SECONDARY evidence], not stored
-- as a backend column — this query cannot re-derive the threshold, only counts
-- events the frontend already classified as SEARCH_LOWRESULT.
-- ----------------------------------------------------------------------------
SELECT
    DATE_TRUNC('day', created_at) AS day,
    COUNT(*) FILTER (WHERE action_type = 'SEARCH_LOWRESULT') AS low_result_count,
    COUNT(*) AS tracked_search_events,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE action_type = 'SEARCH_LOWRESULT')
        / NULLIF(COUNT(*), 0), 1
    ) AS low_result_pct
FROM user_interactions
WHERE action_type IN ('SEARCH', 'SEARCH_NORESULT', 'SEARCH_LOWRESULT')
  AND created_at >= :start_date
  AND created_at <  :end_date
GROUP BY 1
ORDER BY 1;


-- ----------------------------------------------------------------------------
-- 6. Search CTR (as currently measurable — matches crud/admin.py::_section_search_queries)
-- Attribution window: 5 minutes, same user_id/session_id key, click must occur
-- on current_page_route = '/search'. This is a heuristic, not a hard link.
-- ----------------------------------------------------------------------------
WITH search_events AS (
    SELECT
        id,
        LOWER(TRIM(content_id)) AS query,
        COALESCE(user_id::text, session_id) AS who,
        created_at AS searched_at,
        action_type::text AS atype
    FROM user_interactions
    WHERE action_type::text IN ('SEARCH', 'SEARCH_NORESULT', 'SEARCH_LOWRESULT')
      AND content_id IS NOT NULL
      AND created_at >= :start_date
      AND created_at <  :end_date
      AND (user_id IS NULL OR user_id NOT IN (:test_user_ids))
),
clicks_on_search AS (
    SELECT
        COALESCE(user_id::text, session_id) AS who,
        created_at AS clicked_at,
        content_type::text AS ctype
    FROM user_interactions
    WHERE action_type::text IN ('CLICK', 'VIDEO_CLICK', 'VIDEO_PLAY')
      AND current_page_route = '/search'
      AND created_at >= :start_date
      AND created_at <  :end_date
      AND (user_id IS NULL OR user_id NOT IN (:test_user_ids))
),
attributed AS (
    SELECT
        s.id, s.who,
        BOOL_OR(
            c.ctype IN ('NANO_INSPIRATION_EXAMPLE_GRID', 'NANO_INSPIRATION_TEMPLATE_CARD')
        ) AS had_result_click
    FROM search_events s
    LEFT JOIN clicks_on_search c
      ON c.who = s.who
     AND c.clicked_at BETWEEN s.searched_at AND s.searched_at + INTERVAL '5 minutes'
    WHERE s.atype = 'SEARCH'
    GROUP BY s.id, s.who
)
SELECT
    COUNT(*) AS attributable_searches,
    COUNT(*) FILTER (WHERE had_result_click) AS searches_with_result_click,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE had_result_click) / NULLIF(COUNT(*), 0), 1
    ) AS search_ctr_pct
FROM attributed;


-- ----------------------------------------------------------------------------
-- 7. Search-to-Generate rate
-- [PLACEHOLDER — INSUFFICIENT SCHEMA EVIDENCE TO WRITE A TRUE VERSION OF THIS QUERY]
-- Missing facts required before this can be written for real:
--   - No search_id column exists on user_interactions or project.
--   - project has no session_id column, so anonymous generations cannot be
--     joined at all via the existing identity model.
--   - No code path links a GENERATE click-log row to the project row it
--     supposedly corresponds to (see SEARCH_ATTRIBUTION_FEASIBILITY.md).
-- The query below is the closest APPROXIMATION achievable today: it treats
-- "searched at all" and "generated at all" as same-user, same-week flags,
-- matching the existing surface_cohorts pattern in crud/admin.py. It is a
-- population-level correlation, NOT a per-session Search-to-Generate rate,
-- and should be labeled as such wherever it is reported.
-- ----------------------------------------------------------------------------
WITH identity_activity AS (
    SELECT
        COALESCE(user_id::text, session_id) AS who,
        BOOL_OR(action_type IN ('SEARCH', 'SEARCH_NORESULT', 'SEARCH_LOWRESULT')) AS searched,
        BOOL_OR(action_type = 'GENERATE') AS clicked_generate  -- click-log signal only, NOT verified against project.status
    FROM user_interactions
    WHERE created_at >= :start_date
      AND created_at <  :end_date
      AND (user_id IS NULL OR user_id NOT IN (:test_user_ids))
    GROUP BY 1
)
SELECT
    COUNT(*) FILTER (WHERE searched) AS searchers,
    COUNT(*) FILTER (WHERE searched AND clicked_generate) AS searchers_who_also_clicked_generate,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE searched AND clicked_generate)
        / NULLIF(COUNT(*) FILTER (WHERE searched), 0), 1
    ) AS approx_search_to_generate_click_pct  -- NOTE: measures GENERATE click-log event, not confirmed project.status='COMPLETED'
FROM identity_activity;


-- ----------------------------------------------------------------------------
-- 8. Click-to-Generate rate
-- [PLACEHOLDER — INSUFFICIENT SCHEMA EVIDENCE]
-- Missing facts required:
--   - No shared key between a search-result click event and a project row.
--   - No time-window convention is established in any existing code for this
--     specific link (unlike Search->Click, which has a documented 5-minute rule).
-- Any query attempting this join today would require an arbitrary, unvalidated
-- window choice and would only cover logged-in users (project.user_id has no
-- session_id counterpart for anonymous users). Do not report a number from
-- this without first getting product/eng sign-off on the window and on
-- explicitly excluding anonymous users from the denominator.
-- Illustrative (NOT VALIDATED) shape, using user_id only:
-- ----------------------------------------------------------------------------
-- WITH result_clicks AS (
--     SELECT user_id, created_at AS clicked_at
--     FROM user_interactions
--     WHERE action_type IN ('CLICK', 'VIDEO_CLICK', 'VIDEO_PLAY')
--       AND current_page_route = '/search'
--       AND user_id IS NOT NULL          -- anonymous clicks CANNOT be joined here — project has no session_id
--       AND created_at >= :start_date AND created_at < :end_date
-- ),
-- generations AS (
--     SELECT user_id, created_at AS generated_at, status
--     FROM project
--     WHERE created_at >= :start_date AND created_at < :end_date
-- )
-- SELECT COUNT(DISTINCT rc.user_id) AS clickers,
--        COUNT(DISTINCT g.user_id) FILTER (WHERE g.status = 'COMPLETED') AS clickers_who_generated
-- FROM result_clicks rc
-- LEFT JOIN generations g
--   ON g.user_id = rc.user_id
--  AND g.generated_at BETWEEN rc.clicked_at AND rc.clicked_at + INTERVAL ':window'  -- window is UNDEFINED, needs sign-off
-- ;
-- Do not run until the window and anonymous-exclusion caveat are explicitly approved.


-- ----------------------------------------------------------------------------
-- 9. Generation success rate
-- Fully supported by existing schema — independent of search attribution.
-- ----------------------------------------------------------------------------
SELECT
    DATE_TRUNC('day', created_at) AS day,
    COUNT(*) FILTER (WHERE status = 'COMPLETED') AS completed,
    COUNT(*) FILTER (WHERE status = 'FAILED') AS failed,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE status = 'COMPLETED')
        / NULLIF(COUNT(*) FILTER (WHERE status IN ('COMPLETED', 'FAILED')), 0), 1
    ) AS generation_success_pct
FROM project
WHERE created_at >= :start_date
  AND created_at <  :end_date
GROUP BY 1
ORDER BY 1;


-- ----------------------------------------------------------------------------
-- 10. Breakdown by query (top queries, search + no-result + click attribution)
-- Matches crud/admin.py::_section_search_queries, aggregated, LIMIT applied.
-- ----------------------------------------------------------------------------
WITH search_events AS (
    SELECT id, LOWER(TRIM(content_id)) AS query,
           COALESCE(user_id::text, session_id) AS who,
           created_at AS searched_at, action_type::text AS atype
    FROM user_interactions
    WHERE action_type::text IN ('SEARCH', 'SEARCH_NORESULT', 'SEARCH_LOWRESULT')
      AND content_id IS NOT NULL
      AND created_at >= :start_date AND created_at < :end_date
),
clicks_on_search AS (
    SELECT COALESCE(user_id::text, session_id) AS who,
           created_at AS clicked_at, content_type::text AS ctype
    FROM user_interactions
    WHERE action_type::text IN ('CLICK', 'VIDEO_CLICK', 'VIDEO_PLAY')
      AND current_page_route = '/search'
      AND created_at >= :start_date AND created_at < :end_date
),
attributed AS (
    SELECT s.query, s.atype, s.who,
           BOOL_OR(c.ctype IN ('NANO_INSPIRATION_EXAMPLE_GRID','NANO_INSPIRATION_TEMPLATE_CARD')) AS had_result_click
    FROM search_events s
    LEFT JOIN clicks_on_search c
      ON c.who = s.who AND s.atype = 'SEARCH'
     AND c.clicked_at BETWEEN s.searched_at AND s.searched_at + INTERVAL '5 minutes'
    GROUP BY s.query, s.atype, s.who
)
SELECT
    query,
    COUNT(*) FILTER (WHERE atype = 'SEARCH') AS searches,
    COUNT(*) FILTER (WHERE atype IN ('SEARCH_NORESULT','SEARCH_LOWRESULT')) AS no_or_low_results,
    COUNT(DISTINCT who) AS distinct_users,
    COUNT(*) FILTER (WHERE had_result_click) AS result_clicks
FROM attributed
GROUP BY query
HAVING COUNT(*) FILTER (WHERE atype = 'SEARCH') > 0
ORDER BY no_or_low_results DESC, searches DESC
LIMIT 50;


-- ----------------------------------------------------------------------------
-- 11. Breakdown by language
-- [PLACEHOLDER — INSUFFICIENT SCHEMA EVIDENCE]
-- Missing schema fact: user_interactions has no `language` column, and no
-- other table observed during this audit carries a per-search language value.
-- Cannot be written without a new column or a reliable external language
-- detector applied at query time (out of scope for a read-only SQL template).
-- ----------------------------------------------------------------------------


-- ----------------------------------------------------------------------------
-- 12. Breakdown by result-count bucket
-- Only possible at the SEARCH_NORESULT / SEARCH_LOWRESULT / (implied "healthy") grain,
-- because no numeric result_count column exists — buckets below are event-type
-- proxies, not true count buckets.
-- ----------------------------------------------------------------------------
SELECT
    CASE action_type
        WHEN 'SEARCH_NORESULT'  THEN '0 results'
        WHEN 'SEARCH_LOWRESULT' THEN '1-4 results (approx, per frontend LOW_RESULT_THRESHOLD=5)'
        WHEN 'SEARCH'           THEN '5+ results (narrowed-by-chip searches only; healthy unchipped searches are not tracked)'
    END AS result_count_bucket,
    COUNT(*) AS event_count
FROM user_interactions
WHERE action_type IN ('SEARCH', 'SEARCH_NORESULT', 'SEARCH_LOWRESULT')
  AND created_at >= :start_date AND created_at < :end_date
GROUP BY 1
ORDER BY 1;


-- ----------------------------------------------------------------------------
-- 13. Breakdown by result rank
-- [PLACEHOLDER — INSUFFICIENT SCHEMA EVIDENCE]
-- Missing schema fact: no result_rank/position column exists anywhere in the
-- evidenced schema (user_interactions has no such column; no other table
-- carries it either). Requires new instrumentation before this query can be
-- written for real.
-- ----------------------------------------------------------------------------


-- ----------------------------------------------------------------------------
-- 14. Future: internal vs. external clicks
-- [PLACEHOLDER — INSUFFICIENT SCHEMA EVIDENCE]
-- Missing schema fact: no result_source/destination_domain column exists.
-- All current results are internal; this query has no meaning until Hybrid
-- Search introduces a source-tagged result and click event. See
-- HYBRID_SEARCH_INSTRUMENTATION_REQUIREMENTS.md for the exact fields needed
-- (result_source, provider, destination_domain) before this can be written.
-- ----------------------------------------------------------------------------


-- ----------------------------------------------------------------------------
-- 15. Future: Hybrid Search mode comparison (A/B)
-- [PLACEHOLDER — INSUFFICIENT SCHEMA EVIDENCE]
-- Missing schema facts: no search_mode column, no search_id, no result_source,
-- no generation linkage. This query cannot be written with real table/column
-- names because none of the underlying instrumentation exists in this
-- codebase today. Minimum required schema before this template can be
-- filled in for real (see HYBRID_SEARCH_INSTRUMENTATION_REQUIREMENTS.md):
--   search(search_id, search_mode, session_id, user_id, created_at, ...)
--   result_click(search_id, result_id, result_source, result_rank, ...)
--   generation(search_id, generation_id, status, created_at, ...)
-- Illustrative shape only, once those exist:
-- SELECT s.search_mode,
--        COUNT(DISTINCT s.search_id) AS searches,
--        COUNT(DISTINCT rc.search_id) AS searches_with_click,
--        COUNT(DISTINCT g.search_id) FILTER (WHERE g.status = 'COMPLETED') AS searches_with_generation
-- FROM search s
-- LEFT JOIN result_click rc ON rc.search_id = s.search_id
-- LEFT JOIN generation g ON g.search_id = s.search_id
-- WHERE s.created_at >= :start_date AND s.created_at < :end_date
-- GROUP BY s.search_mode;
-- ============================================================================
