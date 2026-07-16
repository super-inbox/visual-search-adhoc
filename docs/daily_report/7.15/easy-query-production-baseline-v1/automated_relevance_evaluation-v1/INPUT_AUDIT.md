# INPUT_AUDIT.md — Phase 1 Input Integrity Audit

Run against baseline root: `/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.15/easy-query-production-baseline-v1`

Query input SHA256: `682ed08a97f69ff39317c923ac859fe2f085ab8e8d7b9dc7b1a0f31fa0b32f3e` — matches RUN_MANIFEST.json value: **True**

## Checklist results (items 1-20 from task spec)

- [x] 1. Authoritative query count == 328 — 328
- [x] 2. full_results.csv has 328 query-level records — 328
- [x] 3. full_results.jsonl has 328 objects — 328
- [x] 4. Query order consistent between query_input and full_results — 0 mismatches
- [x] 5. query_index unique and contiguous 1..328 — unique=328, contiguous=True
- [x] 6. original_query matches authoritative input — 0 mismatches
- [x] 7. Top Results linkable by query_index — 0 unexplained gaps
- [x] 8. raw/ has 328 files — 328
- [x] 9. screenshots/ has 328 files — 328
- [x] 10. Screenshot/raw paths resolve for every query — missing_screenshot=0, missing_raw=0
- [x] 11. broaden/rewrite data relationally consistent — see notes
- [x] 12. zero/low-result data relationally consistent — see notes
- [x] 13. No empty queries — 0
- [x] 14/15. Duplicate queries identified and retained (not dropped) — 0 duplicate text value(s)
- [x] 16. No corrupt/suspicious screenshots — 0 flagged
- [x] 17. No corrupt raw records — 0 flagged
- [x] 18. No missing Top Results for queries with observed results — 0
- [x] 19. No screenshot/raw-record count conflicts — 0 conflicts
- [x] 20. All path references valid — see item 10

## Issues found

- None. All 20 checklist items pass.

## Notes

- Queries with zero visible Top Results rows: 12 (of which zero_result=true accounts for 12)
- No duplicate query text found in query_input (consistent with RUN_MANIFEST duplicate_query_count_in_input=0).

## Blocking decision

- Mapping failure rate across order/text/top-results checks: 0.0000
- BLOCKED_INPUT_MAPPING_FAILURE triggered: **False** (threshold: >50% of queries unmappable)
- Any individual query with unresolved issues will be marked EVIDENCE_INCOMPLETE and evaluated as UNJUDGABLE / NEEDS_MANUAL_REVIEW rather than blocking the whole run.
