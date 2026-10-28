# Reviewer package — what to send

Send **only** the two assembled folders (or their zips), **in order**. Do not send anything from the repo directly.

## SEND TO REVIEWER

### 1. Step 1: blind (send first)

`package_local/send_step1_blind/` (or `send_step1_blind.zip`), containing exactly:

| File | Purpose |
|---|---|
| `reviewer_instructions.md` | Step 1 instructions |
| `review_blind.html` | Step 1 form |
| `blind_review.csv` | Step 1 answer sheet (spreadsheet alternative) |
| `clips/R02-old.mp4`, `clips/R02-official.mp4`, `clips/R05-old.mp4`, `clips/R05-official.mp4`, `clips/R35-old.mp4`, `clips/R35-official.mp4`, `clips/R26-context.mp4`, `clips/R29-context.mp4` | The 8 clips |
| `SHA256SUMS` | Checksums of all of the above |

### 2. Step 2: reference-conditioned follow-up (send only after the Step 1 file has been returned)

`package_local/send_step2_reference_conditioned/` (or `send_step2_reference_conditioned.zip`), containing exactly:

| File | Purpose |
|---|---|
| `reviewer_instructions_step2.md` | Step 2 instructions with the reference-conditioned warning |
| `review_reference_conditioned.html` | Step 2 form (REFERENCE-CONDITIONED FOLLOW-UP banner) |
| `reference_conditioned_followup.csv` | Step 2 answer sheet |
| `SHA256SUMS` | Checksums |

Before sending, run `shasum -a 256 -c SHA256SUMS` inside each folder.

## INTERNAL ONLY: never send

- `README.md`, `REVIEWER_PACKAGE_MANIFEST.md` (this file).
- `reviewer_package_manifest.csv`: source spans, domain names, P0-12 model-input paths.
- `reviewer_labels.csv`: the superseded 2026-10-24 combined sheet.
- `build_reviewer_package.py`, `package_local/_superseded_2026-10-24/`.
- **Model outputs and automatic analysis:**
  - Uni-Sign outputs: P0-A candidates, inspection sheets;
  - production outputs: `asl-eval/production_45/`, `inspection_sheet_with_production.csv`;
  - OpenFS strings: `specialist*.json`, `specialist_cases.csv`;
  - FS-Detection outputs: `fs_detection_feasibility.json`;
  - model confidence;
  - automatic error and weak labels;
  - scoring notes, prior conclusions and daily reports.
- **Reference-conditioned metadata outside Step 2:** reference sentences, target names and sentences, R26 official
  window, R29 neighbour timings, `p0b-fingerspelling-feasibility/`, `p0c-input-correction/`.
- **The 10.13 45-clip review** (`docs/daily_report/10.13/asl-unisign-error-taxonomy/manual_review/`, untracked):
  **not part of this package and not blind.** Its Role B page shows the English reference and hides system predictions
  and weak labels only behind collapsed boxes.
