# Search Query & Event Data — Privacy and Data-Risk Notes

Repository: `curify-studio` @ `7b3fa5b40b03da3056536257ead2200dab031247`. Engineering/privacy risk observations only — no legal conclusions are drawn here per audit scope.

## 1. Raw search queries may contain personal data
The `content_id` column on `user_interactions` stores the **raw, unredacted text** a user typed into the search box, with no filtering, redaction, or sensitive-content classification applied before storage (`curify_background/app/routers/interactions.py` → `crud_interactions.create_interaction()` performs a direct `db.add()` with no content inspection). Search boxes routinely capture names, locations, health/relationship terms, or other sensitive free text typed by users, intentionally or not. This is a plausible risk, not a confirmed incident — no query content was inspected during this audit.

## 2. Raw query strings are visible in the admin dashboard
The `search_queries` section of `GET /admin/interaction-analytics` (rendered in `admin_portal/index.html`'s `#analyticsSearchQueries` table) displays the **literal query text** per row (`query, searches, no_results, users, ...`). This is an aggregated view (grouped by query, not by user), so it does not attach a query to a specific person in the UI itself — but if a rare/unique query string was typed by only one user, the aggregation provides little practical anonymity (a "k-anonymity" style risk: low-frequency queries are effectively single-user data even though the query is technically grouped).

## 3. Raw user IDs are exposed in one admin surface
The **Project History** tab (`GET /admin/project-history` → `crud/admin.py::get_recent_projects()`) returns raw `user_id` values alongside per-project data (job type, status, language, runtime_config). This is not part of the search/click funnel reporting, but it is a raw user-level identifier exposed in an admin UI and should be scoped to admins who need it.

Additionally, `GET /interactions/user/{user_id}` (`curify_background/app/routers/interactions.py`) is a **publicly routed** endpoint (no authentication decorator observed in the router) that returns a specific user's raw interaction history by `user_id`. This is not used by the admin dashboard UI itself, but it is live and reachable, and should be reviewed for access control before this audit is treated as complete on the privacy dimension — the audit's scope was read-only static inspection, not live endpoint testing, so its actual auth behavior at runtime was not verified.

## 4. Email/name fields
`User.email`, `first_name`, `last_name` exist on the `users` table (`curify_background/app/models/user.py`) but were **not observed being selected in any of the search/click/generate analytics queries** inventoried in this audit (`crud/admin.py`'s interaction-analytics functions select only `user_id`/`session_id`/behavioral fields, not name/email). No unnecessary email/name selection was found in the funnel-reporting code path specifically.

## 5. Aggregation and pseudonymization
- Aggregated reporting exists (all 9 sections of `_compute_interaction_analytics()` group by query/day/cohort/route rather than exposing raw per-event rows in the dashboard UI).
- Identifiers **can** be hashed/pseudonymized relatively easily — `user_id` is already an opaque integer (not directly identifying on its own), and `session_id` is already a generated string. The raw exposure risk is concentrated in (a) the query text itself (#1, #2) and (b) the two raw-row-level endpoints noted in #3, not in the identifier columns.
- No evidence of existing hashing/pseudonymization applied to `user_id`/`session_id` before storage — they are stored as received.

## 6. Raw query retention
No retention/expiry policy or scheduled deletion job was found for `user_interactions` rows. Combined with #1/#2, raw search query text — including any sensitive text a user typed — appears to be retained indefinitely by default. This should be reviewed against whatever data-retention policy the company has adopted (not assessed here; that's outside engineering scope).

## 7. Report exports
`GET /proposals/export` (`curify_background/app/routers/proposals.py`) exports proposal records, which include query text (for `search_no_result`-sourced proposals) but are aggregate/curated proposals, not raw per-user event rows. No other export endpoint was found in the search/click/generate surface. No evidence of a raw `user_interactions` row-level export endpoint.

## 8. Hybrid Search and external providers — engineering/privacy considerations for the future
No external search provider integration exists in this codebase today, so all points below are prospective, to be addressed **before** any Hybrid Search launch:

- **Would original queries be sent externally?** Not currently applicable (no external provider wired up yet) — but if implemented by simply forwarding the same raw `content_id` string used internally today, the same unredacted, unfiltered text described in #1 would be transmitted to a third party.
- **Would rewritten queries be sent externally?** **[SECONDARY — curify-frontend]** A query-rewrite mechanism (`lib/searchRewrite.ts`, referenced in docs) already exists for internal search; if reused for a hybrid external call, rewritten queries carry the same raw-text risk as the original, and would need the same review.
- **Is sensitive-query filtering needed?** Yes, recommended before any external call is made — no such filtering exists anywhere in the current pipeline (internal or external).
- **Is query redaction needed?** Recommended for the same reason — no redaction step exists today.
- **Consent/policy review?** Sending user-typed search text to a third-party API is a meaningful change in data handling that should go through whatever privacy/consent review process the company uses before launch — this audit does not have visibility into that process and makes no claim about what's required, only that the technical change (raw text leaving the system) is significant enough to warrant one.
- **Should query logging avoid raw external-response data?** Recommended — if an external provider's raw response payload (which could include arbitrary third-party content/metadata) is logged verbatim into `user_interactions` or a new event table, that introduces an additional, currently-nonexistent category of externally-sourced data into the system that would need its own review.

## Summary of concrete, code-evidenced risks (not hypothetical)

1. Raw, unfiltered search query text is stored indefinitely with no redaction (`user_interactions.content_id`).
2. That raw text is visible in an aggregated admin dashboard table, with a practical re-identification risk for rare/unique queries.
3. A publicly-routed endpoint (`GET /interactions/user/{user_id}`) returns raw per-user interaction history by ID; its actual authentication behavior was not verified live (out of scope for a read-only static audit) and should be checked.
4. A hardcoded production database credential exists in source control (`curify_background/scripts/migrate_content_type_enum.py`, a fallback default `DATABASE_URL` value) — unrelated to search/click/generate specifically, but a real, currently-existing credential-exposure risk discovered during this audit. The value itself is not reproduced in any audit output.
