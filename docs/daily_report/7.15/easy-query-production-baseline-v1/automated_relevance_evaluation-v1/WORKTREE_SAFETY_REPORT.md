# WORKTREE_SAFETY_REPORT.md

Generated: 2026-07-16T07:30Z (end of the automated relevance evaluation run)

## Checks

- **production_code_modified: false** — this repository is a docs/evaluation workspace; it
  contains no Curify application source to modify. No file outside
  `docs/daily_report/7.15/easy-query-production-baseline-v1/automated_relevance_evaluation-v1/`
  was written by this run.
- **authoritative_query_modified: false** — `query_input/easy_queries_cleaned_300_plus_2026-07-14.csv`
  was only opened for reading (via Bash/Python `csv.DictReader`); never opened in write mode.
  SHA256 unchanged (matches the value already recorded in `INPUT_AUDIT.md` /
  `input_integrity.json`).
- **baseline_results_modified: false** — verified by filesystem mtime: every file under
  `../final/easy_query_production_baseline_*` still shows its original 2026-07-15 16:xx/17:xx
  timestamp (spot-checked all 14 files in `../final/`), vs. this run's outputs which are all
  timestamped 2026-07-16. No `Write`/`Edit` tool call in this session targeted any path outside
  `automated_relevance_evaluation-v1/`.
- **existing_screenshots_modified: false** — `../screenshots/*.png` (328 files) only opened via
  the `Read` tool (for calibration/zero-result/spot-audit visual checks) or left untouched;
  spot-checked mtimes remain 2026-07-15 16:44. 0 files under `../screenshots/` are newer than
  `RUN_MANIFEST.json`.
- **existing_raw_records_modified: false** — `../raw/*.json` (328 files) only opened for reading;
  0 files newer than `RUN_MANIFEST.json`.
- **commit_created: false** — no `git commit` was run in this session.
- **push_performed: false** — no `git push` (or any network git operation) was run in this session.
- **lockfile_modified: false** — no lockfile (`package-lock.json`, `requirements.txt`, etc.)
  exists in or near this evaluation directory; none was touched.
- **files_deleted: none** — no `rm`, no destructive git operation, was run against any existing
  file in this session. All new files were created with `Write`, all edits with `Edit`, both
  confined to `automated_relevance_evaluation-v1/` (plus one new pointer file at the baseline
  root, `AUTOMATED_RELEVANCE_EVALUATION_ADDED.md`, which is an addition, not a modification of
  any existing file).
- **new_files_confined_to_eval_dir: true** — the only file created outside
  `automated_relevance_evaluation-v1/` in this session is
  `../AUTOMATED_RELEVANCE_EVALUATION_ADDED.md`, a new pointer file (see task spec Sec.22); no
  existing baseline-root file (`README.md`, `RUN_MANIFEST.json`, `CODE_VERSION_AUDIT.md`, etc.)
  was edited.
- **network_requests_made: false** — no script in `scripts/01`-`09` contains any HTTP client
  code (no `requests`, no `urllib`, no `fetch`); all operate exclusively on local files under
  `raw/`, `screenshots/`, `evidence/`, `checkpoints/`, `final/`. No request was made to
  `https://www.curify-ai.com` or any other host during this run.

## Verdict

All safety conditions satisfied. This run only read from the existing baseline and wrote new
files inside `automated_relevance_evaluation-v1/` (plus the one disclosed pointer file at the
baseline root).
