# Final Audit Log — Search → Click → Generate Data Pipeline Audit

Audit date: 2026-07-17
Audited repository: `/Users/baobaoli/Desktop/curify-studio`
Branch: `main` · Commit: `7b3fa5b40b03da3056536257ead2200dab031247`
Output directory: `/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.17/search-click-generate-data-audit/`

## Validation checklist

| Check | Result |
|---|---|
| `curify-studio` working tree unchanged (start of session) | ✅ `git status` → clean, up to date with `origin/main` |
| `curify-studio` working tree unchanged (end of session) | ✅ `git status --porcelain` → empty output, confirmed after all writes |
| No repository file modified | ✅ Only `Read`/`grep`/`find`-class tools used inside the repo; all `Write`/`Edit` calls targeted the external output directory only |
| No dependency installed (`npm`/`pnpm`/`yarn`/`pip` install) | ✅ Not run |
| No application server started | ✅ Not run |
| No SQL executed | ✅ All SQL in `SAFE_READ_ONLY_SQL_TEMPLATES.sql` is a static template with placeholder bind parameters (`:start_date` etc.); nothing was run against any database |
| No live database accessed | ✅ No database connection attempted |
| No production write occurred | ✅ N/A — no write path was touched |
| No secret or `.env` value copied into reports | ✅ The one discovered hardcoded credential (`curify_background/scripts/migrate_content_type_enum.py`) is referenced by file path and variable name only; the value itself is not reproduced anywhere in these outputs |
| No raw user data appears in reports | ✅ All CSV/MD content is schema/code-level (column names, function names, aggregate query shapes); no query result rows, no real query text, no real user records were fetched or exposed |
| No raw email/name/user ID/session ID exposed | ✅ Only the hardcoded test-user ID constants already present in application source (`155, 1117, 1267`) are cited, for a data-quality finding — these are internal test-account literals in code, not extracted real-user records |
| All required output files exist | ✅ 14/14 present (verified via `ls`, see below) |
| All CSV files parse | ✅ Verified via Python `csv.reader` on all 4 CSVs — no parse errors |
| JSON parses | ✅ Verified via Python `json.load` on `AUDIT_MANIFEST.json` — no parse errors |
| SQL file contains no executed output | ✅ `SAFE_READ_ONLY_SQL_TEMPLATES.sql` is templates and comments only; no result sets, no execution log |
| Audited repository path recorded | ✅ `/Users/baobaoli/Desktop/curify-studio` |
| Branch and commit recorded | ✅ `main` @ `7b3fa5b40b03da3056536257ead2200dab031247` |
| Output file hashes recorded | ✅ See table below |
| Verified facts vs. assumptions distinguished | ✅ All `[SECONDARY]`-tagged claims (sibling `curify-frontend` repo) are explicitly marked throughout every output file; all schema/table/field claims are cited to a specific file path within `curify-studio` |
| Missing evidence and limitations listed | ✅ See `SEARCH_CLICK_GENERATE_DATA_AUDIT.md` §"Limitations of this audit" and `AUDIT_MANIFEST.json.limitations` |

## Output file inventory and hashes (SHA-256)

| File | SHA-256 |
|---|---|
| SEARCH_CLICK_GENERATE_DATA_AUDIT.md | `3128457c3c988eb28777880d29f225ac43578dd2c6b2fec9952f73d874d27df5` |
| SEARCH_ADMIN_DASHBOARD_INVENTORY.csv | `056e6380a37227bfffc5b05611335bb3154d21f0d8f76d4a9da0af867a85a96a` |
| SEARCH_SQL_QUERY_INVENTORY.csv | `2815439f09b3c1293a2f8a8d2109d5439463e664b9121dce268b67c382500c26` |
| SEARCH_EVENT_FIELD_MAP.csv | `7b8b0be61b805eb9c1e64e307fd1503993829f40f19c66f40a59195c9499c227` |
| SEARCH_ATTRIBUTION_FEASIBILITY.md | `60874a6a6366ed032c1cf2d77c26244267f59b4cd3a90595de0b660a88929647` |
| SEARCH_FUNNEL_METRIC_DEFINITIONS.md | `d81d02e39058e94c6a41aac389951167d614e35026b07e4b40e2ef8fbcc80e2a` |
| SEARCH_DASHBOARD_CAPABILITY_MATRIX.csv | `bfbe85417e9f8eaa2c64aba9f7d8e134d170d3376c15d11f14b3aadb5c257754` |
| SEARCH_TRACKING_GAPS.md | `77a7950b57bc0f4763ffa88679258ce2afafbc004f99d66361eea1b2e8c4cf67` |
| HYBRID_SEARCH_INSTRUMENTATION_REQUIREMENTS.md | `91af3f8935885f6718aae2cbd2a2c214142e312c1520e7b2804dcdfe77d3bf1d` |
| SEARCH_QUERY_PRIVACY_RISK_NOTES.md | `8cab50a4fb2aa819fd558f530d9f17e3b7977e9374adcb7c08bc205ba33da2b8` |
| SAFE_READ_ONLY_SQL_TEMPLATES.sql | `7fe78d92303df1dd99e1a752800a610674911228d308cd7ebe99eec70ab02efe` |
| SEARCH_CLICK_GENERATE_EXECUTIVE_SUMMARY_ZH.md | `62807c298e0554f38cb18a837fb5e21ce4f633e06642be85dea39320f94557c3` |
| AUDIT_MANIFEST.json | `4d4b4465a7acd5d8d6f48b4a107f6f2015889fa6a35bcb51b2c50a8664d4619b` |
| FINAL_AUDIT_LOG.md (this file) | not self-hashable (hash would change the moment it's written); all other 13 files' hashes above are final and were computed after their content was finalized |

## Methodology note

This audit used 4 parallel read-only research (`Explore`) subagents against `curify-studio`, each scoped to a distinct surface (search code/events; admin dashboard + SQL; click/generation tracking; DB schema + identity model). Their independent findings were cross-checked against each other for consistency (all 4 independently converged on the same core facts: single `user_interactions` event table, `COALESCE(user_id,session_id)` + 5-minute-window heuristic for Search→Click, and no linkage at all for Click→Generate) before being synthesized into the 14 files above by direct review of the underlying evidence, not by trusting agent summaries verbatim.

## Missing evidence / open questions for follow-up

1. `dev/jayw/admin_analysis/use_case_chip_clicks_pull.py` references a `session_funnel_30d_pull.py` file not present in this checkout — worth asking the author (Jay W.) whether it represents additional, uncommitted funnel analysis relevant to this audit.
2. Whether the enum migrations (`SEARCH_NORESULT`, `SEARCH_LOWRESULT`, etc.) have actually been applied against the live production database was not verified (would require a live connection, out of scope).
3. The exact frontend conditions under which `SEARCH`/`SEARCH_NORESULT`/`SEARCH_LOWRESULT` fire were confirmed via a read-only look at the sibling `curify-frontend` repository, which is formally out of this audit's scope; if the manager wants those specific claims independently re-verified strictly within `curify-studio`, they cannot be — `curify-studio` alone has no visibility into its own callers' firing conditions.
4. A hardcoded production database credential was found in `curify_background/scripts/migrate_content_type_enum.py` during this audit (unrelated to the search/click/generate question). This is flagged here for follow-up (rotation/removal) but is outside this audit's remit to remediate.

---

**FINAL_STATUS: COMPLETE_WITH_LIMITATIONS**
