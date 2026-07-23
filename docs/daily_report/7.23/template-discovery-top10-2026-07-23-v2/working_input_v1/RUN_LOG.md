# Run Log — Curify Template Discovery Top 10 (2026-07-23)

## Interruption
The initial session was interrupted mid-stream by an API error ("Response stalled mid-stream") after
generating a subset of deliverables but before completing the full required file set.

## Recovery — audit performed 2026-07-23

### Files found intact before recovery began
| file | status | verification performed |
|---|---|---|
| `_candidates.json` | COMPLETE (10/10 candidates, fully scored/ranked) | JSON parses; all 10 candidates have complete fields (queries, evidence, scores, rank, priority); one leftover scratch-reasoning fragment found in T03's `latest_evidence` field ("-> wait, actually 9 in v2r3 lineage / re-check") and cleaned during recovery, replaced with the verified fact (`workbook` total_results=0, row 297 of `03_FULL326_LATEST_RESULTS.csv`) |
| `01_SOURCE_INVENTORY.csv` | COMPLETE | 28 data rows, 14 columns, no ragged rows, parses cleanly |
| `02_UNIFIED_QUERY_INVENTORY.csv` | COMPLETE | 31 data rows, parses cleanly, covers all queries referenced by `_candidates.json` plus all excluded/ambiguous queries |
| `images/` (26 files across 12 subfolders) | COMPLETE, ALL VERIFIED AUTHENTIC | Every file passed `file` type validation (all valid PNG/JPEG, no zero-byte or corrupt files). All 17 `curify_current` images hash-matched byte-for-byte against their originals in `docs/daily_report/7.17/easy-query-v2-production-baseline/screenshots/`. The 3 T07 competitor images hash-matched byte-for-byte against `docs/daily_report/7.9/competitor_screenshots/xiaohongshu_aromatherapy_product_teaser_image/`. The 3 excluded-search-issue images (`flashcard`, `map`, `笔袋`) hash-matched (after rename) against `248_V248_flashcard.png`, `254_V254_map.png` (both in the 7/17 screenshots dir) and `docs/daily_report/7.21/scorer-v1.1-evaluation-2026-07-21/screenshot/笔袋.png` respectively. The 2 canva-manual-review.jpg copies hash-matched against `docs/daily_report/7.2/canva_manual_review/screenshots/049-esl-flashcards-printable/` (flashcard) and `.../041-watercolor-map-of-europe-travel-destinat/` (map). No fabricated or unrelated filler images found. |
| `cards/` | EMPTY (directory existed, no files) | confirmed via `find` |

### Files missing before recovery (generated in this recovery pass)
`00_RUN_CONTEXT.md`, `03_VERTICAL_TAXONOMY.md`, `03_QUERY_VERTICAL_MAPPING.csv`,
`04_LATEST326_CONTENT_GAP_SIGNALS.csv`, `04_LATEST326_CONTENT_GAP_SUMMARY.md`,
`05_REPEATED_QUERY_DEMAND.csv`, `05_DEMAND_PATTERN_SUMMARY.md`,
`06_COMPETITOR_EVIDENCE_INDEX.csv`, `06_COMPETITOR_ANALYSIS_SUMMARY.md`,
`07_SEARCH_VS_CONTENT_GAP_CLASSIFICATION.csv`, `08_TEMPLATE_CANDIDATE_POOL.csv`,
`09_TEMPLATE_CANDIDATE_SCORING.csv`, `09_SCORING_METHOD.md`,
`10_TOP10_TEMPLATE_RECOMMENDATIONS.csv`, `11_IMAGE_EVIDENCE_INDEX.csv`,
`11_MISSING_IMAGE_EVIDENCE.md`, `12_TOP10_TEMPLATE_DISCOVERY_REPORT_ZH.md`,
`13_MANAGER_REVIEW_SUMMARY.md`, `13_MANAGER_REVIEW_TOP10.csv`,
`TOP10_TEMPLATE_CONTACT_SHEET.png`, `cards/T01..T10_*.png` (10 files),
`MANIFEST.json`, `SHA256SUMS.txt`.

All of the above were generated in this recovery pass, deriving every fact from `_candidates.json` (already
vetted, evidence-complete) and cross-referencing `02_UNIFIED_QUERY_INVENTORY.csv` / `01_SOURCE_INVENTORY.csv` /
the Task A 7/22 result files. No new benchmark data was collected; no historical source file was read-write
modified.

### Files preserved unmodified
`01_SOURCE_INVENTORY.csv`, `02_UNIFIED_QUERY_INVENTORY.csv`, all 26 files under `images/`.

### Files regenerated (data correction, not a rewrite of conclusions)
`_candidates.json` — one field (T03 `latest_evidence`) had its text cleaned to remove a leftover
scratch-reasoning fragment from the interrupted session. The underlying fact (workbook: 0 results, confirmed
gap) and the T03 rank/score/classification were **not** changed.

## What this recovery did NOT do
- Did not rerun the Task A 326-query benchmark.
- Did not delete or overwrite `_candidates.json`'s core evidence, scores, ranks, or the 10-candidate list itself.
- Did not add `map` or generic `flashcard` as confirmed content gaps — both remain excluded, documented in
  `images/00_excluded-search-issues/` and `07_SEARCH_VS_CONTENT_GAP_CLASSIFICATION.csv`.
- Did not modify any file under `docs/daily_report/7.22/` or any other historical daily-report directory.
- Did not modify frontend source code, commit, push, or open a PR.

## Integrity checks performed at the end of this recovery
- `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv` verified to contain exactly 10 data rows.
- All CSV files verified to parse without ragged rows.
- All image paths referenced in `11_IMAGE_EVIDENCE_INDEX.csv` verified to exist on disk.
- `MANIFEST.json` and `SHA256SUMS.txt` generated/updated at the end of this run (see below) to checksum the full
  final deliverable set.
