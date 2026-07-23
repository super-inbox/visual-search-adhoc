# Run Log — Template Discovery Top 10 V2 Revision (2026-07-23)

## Addendum — targeted consistency fix (same day, follow-up pass)
A small follow-up pass fixed 3 issues found after the initial V2 revision, without rerunning the benchmark, redoing
the analysis, or changing any candidate's ID, priority, status, score, or the ranking rule:

1. **Candidate-ID typo**: `12_TOP10_TEMPLATE_DISCOVERY_REPORT_ZH.md` line 178 said "T05（价格标签）优先于
   T04（证书）" — Certificates is T01, not T04. Searched the entire V2 directory (excluding `working_input_v1/`)
   for every other Certificate/证书 mention; found exactly one instance of the typo (this one) and fixed it to T01.
   No other file had the mismatch, and no T04/Flyer reference was altered.
2. **Stale image-evidence fields for T03 and T06**: `_candidates.json` (`competitor_evidence`, `competitor_confidence`,
   `image_status`) and `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv` (`competitor_evidence`, `image_availability`,
   `missing_evidence`) still described T03 as having only text-only/no-image competitor evidence, predating the
   original V2 pass's discovery of the real Canva phonics-worksheets screenshot. T06's fields were largely already
   correct but were tightened to explicitly state ADJACENT_REFERENCE / not-exact / exact-match-still-missing in the
   same structure as T03. `11_IMAGE_EVIDENCE_INDEX.csv` and `11_MISSING_IMAGE_EVIDENCE.md` were checked and found
   already accurate (no change needed there) — both already listed T03/T06 under "adjacent reference available."
   Neither candidate's image evidence was upgraded to EXACT — both remain explicitly labeled adjacent-only, with an
   exact-match reference still recorded as missing.
3. **T04 manager-wording refinement**: `13_MANAGER_REVIEW_SUMMARY.md`, `12_TOP10_TEMPLATE_DISCOVERY_REPORT_ZH.md`,
   and `13_MANAGER_REVIEW_TOP10.csv` ("review first" section / item 1-2, `one_line_reason`, `review_first`) were
   reworded so T03 is framed as the candidate to prioritize first, and T04 is framed as a strong P0 candidate that
   should get a quick alias/retrieval check before production approval (because "event flyer" retrieves an
   existing Curify template) rather than being bundled with T03 as "approve both first." T04's rank (#2), priority
   (P0), status (CONFIRMED), and both scores (85 / 85.0) were verified unchanged before and after this edit.

Verification performed after these edits: all 14 CSV files re-parsed with no ragged rows; ranks in
`_candidates.json`, `09_TEMPLATE_CANDIDATE_SCORING.csv`, `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv`, and
`13_MANAGER_REVIEW_TOP10.csv` remain unique and sequential 1–10; T01 confirmed mapped to Certificates and T04 to
Flyer everywhere; no EXACT_REFERENCE claim exists for T03 or T06 anywhere in the package; `working_input_v1/`
re-verified byte-identical to the original v1 package (`diff -rq`, zero differences); `docs/daily_report/7.22/`
(Task A source) confirmed untouched; no frontend file opened or modified; no git commit/push/PR performed.
`MANIFEST.json` and `SHA256SUMS.txt` were regenerated to cover the files touched in this pass.

## Scope
Targeted correction and visual-evidence enhancement of the existing v1 package
(`docs/daily_report/7.23/template-discovery-top10-2026-07-23/`). Not a re-analysis from scratch; not a re-run of
the Task A 326-query benchmark.

## Steps performed
1. Created `docs/daily_report/7.23/template-discovery-top10-2026-07-23-v2/` (did not exist previously — no version
   suffix collision).
2. Copied the full v1 package into `working_input_v1/` inside the V2 directory as a read-only working reference
   (verified byte-identical via `diff -rq` against the original v1 directory — zero differences).
3. Read and audited every file listed in the task: `_candidates.json`, `07_SEARCH_VS_CONTENT_GAP_CLASSIFICATION.csv`,
   `09_TEMPLATE_CANDIDATE_SCORING.csv`, `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv`, `11_IMAGE_EVIDENCE_INDEX.csv`,
   `11_MISSING_IMAGE_EVIDENCE.md`, `12_TOP10_TEMPLATE_DISCOVERY_REPORT_ZH.md`, `13_MANAGER_REVIEW_SUMMARY.md`,
   `13_MANAGER_REVIEW_TOP10.csv`, `cards/`, `images/`, `TOP10_TEMPLATE_CONTACT_SHEET.png`. Findings recorded in
   `00_REVISION_CONTEXT.md` and `01_CURRENT_PACKAGE_AUDIT.csv`.
4. Cross-checked Puzzle (T08) and Coupon (T09) against the Task A source files directly
   (`03_FULL326_LATEST_RESULTS.csv`, `05_STATUS_TRANSITIONS_VS_PRODUCTION.csv`,
   `06_STATUS_TRANSITIONS_VS_PREVIOUS_CANDIDATE.csv`, `09_ZERO_LOW_RESULT_ANALYSIS.csv`,
   `12_REMAINING_FAILURE_ROOT_CAUSES.csv`, `09_ZERO_LOW_RESULT_REPORT.md`, `12_ROOT_CAUSE_SUMMARY.md`) — all
   read-only, none modified.
5. Attempted a background research-agent run for the repository-wide image search (Step 3). **The agent failed
   mid-stream with an API connection error and produced no output files.** Rather than retry the same agent, the
   search was performed directly: `find`/`grep` filename and directory keyword matching across
   `docs/daily_report/` (~1,600 image files) for all 10 candidate keyword groups (EN+ZH), followed by direct
   visual inspection (via the Read tool) of every new filename/keyword match not already accounted for in v1.
   Results in `02_REPOSITORY_IMAGE_SEARCH_INDEX.csv` / `02_IMAGE_SEARCH_SUMMARY.md`.
6. Built the revised `images/` directory structure (`curify_current_gap/`, `exact_reference/`, `adjacent_reference/`,
   `selected/` per candidate slug, plus `00_excluded-search-issues/` carried over unchanged) and copied in: all 26
   images from v1 (re-copied from their original source paths, not moved) plus 10 newly found images. Two adjacent
   images required visual re-verification before inclusion (T03 Canva phonics-worksheets screenshot; T06 tea
   gift-box Pinterest screenshot vs. its off-topic Canva sibling, which was checked and rejected).
7. Recomputed ranks under the documented rule (Priority > Status > Evidence-Adjusted Score > Candidate ID) via a
   Python script operating on the v1 CSVs/JSON (`build_v2.py`, run once, output discarded after use — logic
   reproduced in `09_SCORING_METHOD.md`). Two rank swaps resulted (T05↔T01 within P1/CONFIRMED; T08↔T09 within
   P2/PROVISIONAL). Raw and evidence-adjusted score *values* were not recalculated — no calculation error was
   found, only the sort order.
8. Rewrote Puzzle (T08) and Coupon (T09) evidence fields in `_candidates.json`, `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv`,
   and `07_SEARCH_VS_CONTENT_GAP_CLASSIFICATION.csv` per the cross-check in step 4. Neither candidate's status
   (PROVISIONAL) or priority (P2) was changed.
9. Generated all 10 recommendation cards (`cards/*.png`, 1600×1400px, PIL/Pillow + PingFang system font) with the
   required 3-panel layout (CURIFY CURRENT GAP / REFERENCE EXAMPLE / RECOMMENDED VISUAL DIRECTION) and explicit
   raw/evidence-adjusted score fields plus ranking-basis footer.
10. Generated the revised contact sheet (`TOP10_TEMPLATE_CONTACT_SHEET.png`, 1996×1248px) with corrected ranks,
    per-tile reference-image status, and a footer explaining both the ranking rule and remaining reference gaps.
11. Rewrote `12_TOP10_TEMPLATE_DISCOVERY_REPORT_ZH.md` and `13_MANAGER_REVIEW_SUMMARY.md` per the 10-point/8-point
    requirements (ranking rule explained, both scores shown, overgeneralization replaced, Puzzle/Coupon clarified,
    image evidence honesty, CONFIRMED/PROVISIONAL distinction, production-readiness caveats).
12. Copied unchanged, still-valid v1 files verbatim into the V2 root: `01_SOURCE_INVENTORY.csv`,
    `02_UNIFIED_QUERY_INVENTORY.csv`, `03_VERTICAL_TAXONOMY.md`, `03_QUERY_VERTICAL_MAPPING.csv`,
    `04_LATEST326_CONTENT_GAP_SIGNALS.csv`, `04_LATEST326_CONTENT_GAP_SUMMARY.md`, `05_REPEATED_QUERY_DEMAND.csv`,
    `05_DEMAND_PATTERN_SUMMARY.md`, `08_TEMPLATE_CANDIDATE_POOL.csv`.
13. Ran integrity verification (see below) and fixed 3 CSV files that had unescaped-comma quoting bugs from
    manual authoring (`01_CURRENT_PACKAGE_AUDIT.csv`, `06_COMPETITOR_EVIDENCE_INDEX.csv`,
    `02_REPOSITORY_IMAGE_SEARCH_INDEX.csv`) by rebuilding them through Python's `csv` module.
14. Generated `MANIFEST.json` and `SHA256SUMS.txt` covering all 86 deliverable files (excludes `working_input_v1/`,
    which is a reference copy, not a deliverable).

## Integrity verification results
- Exactly 10 rows in `09_TEMPLATE_CANDIDATE_SCORING.csv`, `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv`,
  `13_MANAGER_REVIEW_TOP10.csv`, and `_candidates.json`; ranks are unique and sequential 1–10 in all four, and
  identical across all four (verified programmatically, not just visually).
- All 14 CSV files parse with no ragged rows (verified via `csv.reader` after fixing the 3 files noted above).
- All 10 card PNGs and the contact sheet PNG open and verify successfully (PIL `Image.open().verify()`).
- All 36 image paths referenced in `11_IMAGE_EVIDENCE_INDEX.csv` exist on disk (copied path + original absolute
  path both checked).
- Puzzle and Coupon cross-language caveats present in `_candidates.json`, `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv`,
  `07_SEARCH_VS_CONTENT_GAP_CLASSIFICATION.csv`, `12_TOP10_TEMPLATE_DISCOVERY_REPORT_ZH.md` (lines 90 and 116),
  `13_MANAGER_REVIEW_SUMMARY.md`, and both candidates' cards.
- `map` and `flashcard` confirmed absent from the candidate list (programmatic check on `_candidates.json`).
- `working_input_v1/` verified byte-identical to the original v1 package via `diff -rq` (zero differences) —
  confirms no original v1 (Task B source) file was overwritten in place.
- No file under `docs/daily_report/7.22/` (Task A benchmark source) was written to — all access was read-only.
- No frontend source file was opened or modified during this session.
- No `git commit`, `git push`, or PR was created during this session.

## What this run did NOT do
- Did not rerun the Task A 326-query benchmark.
- Did not overwrite or delete the v1 package.
- Did not change any candidate's priority or status except leaving Puzzle (P2/PROVISIONAL) and Coupon
  (P2/PROVISIONAL) exactly as they were — only their supporting-evidence wording was corrected.
- Did not fabricate any competitor image, source URL, or benchmark evidence. Six candidates (T01, T02, T05, T08,
  T09, T10) remain honestly labeled "REFERENCE IMAGE NEEDED" — no placeholder was replaced with an unrelated or
  invented image.
- Did not modify frontend code, commit, push, or open a PR.
