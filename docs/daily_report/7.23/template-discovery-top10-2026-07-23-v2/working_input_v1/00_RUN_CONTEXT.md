# Run Context — Curify Template Discovery Top-10 (2026-07-23)

## What this run is
This is the **Template Discovery** analysis that turns the confirmed Task A latest-326 evaluation into a
prioritized Top-10 list of new template categories Curify should produce, distinguishing genuine catalog
content gaps from search-engineering regressions that only look like gaps.

## Recovery notice (interrupted session)
This run resumes a session interrupted by an API error ("Response stalled mid-stream") partway through
deliverable generation. See `RUN_LOG.md` for the full recovery audit. In summary: the structured 10-candidate
dataset (`_candidates.json`), the source inventory (`01_SOURCE_INVENTORY.csv`), the unified 31-query inventory
(`02_UNIFIED_QUERY_INVENTORY.csv`), and 26 copied evidence images under `images/` all survived the interruption
intact and were verified byte-for-byte against their original source files before being reused. No analysis was
redone from scratch; only the remaining, previously-unwritten deliverables were generated in this recovery pass.

## What this run does NOT do
- Does **not** rerun the Task A 326-query benchmark. The authoritative result (commit `0e794cd9`, 326 total,
  38 PASS / 86 PARTIAL / 195 FAIL / 7 UNJ, 20 zero-result / 18 low-result queries) is reused verbatim from
  `docs/daily_report/7.22/cluster-ab-latest-fix-full326-2026-07-22/`.
- Does **not** modify, overwrite, or re-collect any file under `docs/daily_report/7.22/` or any other historical
  daily-report directory. All historical sources are read-only inputs.
- Does **not** modify any frontend source file, run `git commit`, `git push`, or open a pull request.
- Does **not** present `map` or generic `flashcard` as confirmed content gaps. Both were cross-checked against
  historical benchmark results and the 7/17 production-baseline screenshots and found to have abundant relevant
  Curify content historically, meaning their current zero/low-result status is a search regression, not a
  catalog gap. Both are excluded from the Top 10 and documented in `images/00_excluded-search-issues/`.

## Primary sources reused (read-only)
| role | path | commit / version |
|---|---|---|
| Task A latest-326 result | `docs/daily_report/7.22/cluster-ab-latest-fix-full326-2026-07-22/03_FULL326_LATEST_RESULTS.csv` | `0e794cd9` |
| Root-cause labels | `docs/daily_report/7.22/.../12_REMAINING_FAILURE_ROOT_CAUSES.csv`, `.../09_ZERO_LOW_RESULT_ANALYSIS.csv` | `0e794cd9` |
| Vertical pass-rate summary | `docs/daily_report/7.22/.../10_VERTICAL_SUMMARY.csv` | `0e794cd9` |
| Historical query bank | `docs/daily_report/7.16/easy-query-bank-v3/easy_query_bank_v2_2026-07-16.csv` | origin of 326-query bank |
| Historical regression sample | `docs/daily_report/7.20/regression-50-second-round-root-cause-analysis/` | regression-50 |
| Historical scorer v1.1 result | `docs/daily_report/7.21/scorer-v1.1-evaluation-2026-07-21/` | scorer_v1.1_full326 |
| Live visual ground-truth | `docs/daily_report/7.17/easy-query-v2-production-baseline/screenshots/` | 326 real Curify screenshots |
| Competitor evidence | `docs/daily_report/7.9/competitor_screenshots/`, `docs/external-signal-pilot/`, `docs/daily_report/7.2/canva_manual_review/` | various |

Full source-by-source detail with relevance notes: `01_SOURCE_INVENTORY.csv`.

## Directory
All artifacts for this run live under this directory only:
`/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.23/template-discovery-top10-2026-07-23`
