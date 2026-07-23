# RUN LOG — Cluster A/B Latest-Fix Full-326 Evaluation (chronological)

Date: 2026-07-22. Timezone: Asia/Shanghai (CST, UTC+8). Operator: automated eval agent, reusing the
`collector.mjs`/`judge.mjs`/`run_eval_single.mjs` methodology from the 7/19 and 7/21 sessions with **no changes** to
collection/judging logic.

## 1. Preflight (Step 0) — 15:15
- `git branch --show-current` → `baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19`
- `git rev-parse HEAD` → `0e794cd91396a96cd56fd1d8f7f1495909f3adc5`
- `git rev-parse origin/<same branch>` → identical SHA
- `git status --short` → empty (clean)
- Node v26.3.0; package manager npm 11.16.0 (package-lock.json present, no pnpm/yarn)
- All preflight expectations met — proceeded.

## 2. Benchmark input verification (Step 1) — 15:16
- Located `easy_query_bank_v2_2026-07-16.csv` — single match in the eval repo (no conflicting duplicates).
- SHA-256 `c5b1368e33ab601884ad91aff21802c64391bee781b6daa2f3ef50e4d54a08c6`, 326 data rows, 326 unique queries, 0
  duplicates, 0 missing values, UTF-8 CSV, columns `query,language,scenario,category,reason`.

## 3. Pipeline identification (Step 2) — 15:16-15:17
- Inspected `docs/daily_report/7.21/scorer-v1.1-evaluation-2026-07-21/` — found `RUN_LOG.md`,
  `SCORER_V1_1_EVALUATION_SUMMARY.md`, `REGRESSION_ANALYSIS.md`, `eval_raw/{BASELINE,CANDIDATE}_EASY326.csv`.
  Runner scripts (`collector.mjs`, `judge.mjs`, `run_eval_single.mjs`) live in
  `docs/daily_report/7.19/search-relevance-prod-main-v2/scripts/` and were reused byte-identical (checksums
  verified) by the 7/21 run too — same lineage, reused again here.
- Confirmed OPENAI_API_KEY present in `.env.local` (real LLM judge calls required and available).

## 4. Fix-context review (Step 3) — 15:17
- Diffed `6efdd904..0e794cd9`: `lib/searchSubject.ts` (new file), `relevanceScorerConfig.ts` (version bump only, no
  weight changes), `page.tsx` (34 lines, wires `subjectUnits()` in), `docs/search-relevance-v2r3-r1-2026-07-21.md`
  (+32 lines documenting Fix A), plus 2 test files.
- Catalog: `public/data/nano_inspiration.json` changed content (SHA `7ec2983a...` → `32015cab...`) in commit
  `b4116648`, same record count (3403) both before/after — a **data content change** (4 templates' hallucinated
  merch/POD aliases stripped), not a code/scorer change and not a count change. Disclosed prominently in
  `00_CONFIG_LOCK.json` and the final report.

## 5. Engineering gate (Step 4) — 15:17:50-15:19:07
- `npx vitest run ... relevanceScorer.test.ts searchSubject.test.ts` → 53/53 passed, exit 0.
- `npx tsc --noEmit` → clean, exit 0.
- `npm run build` → succeeded, exit 0 ("Compiled successfully in 8.0s"); pre-existing unrelated
  `MISSING_MESSAGE: blog.qaBotToTask` warnings documented, non-blocking.
- **ENGINEERING_GATE_PASS.** Full detail: `16_ENGINEERING_VALIDATION.md`.

## 6. Output directory (Step 5) — 15:20
- Created `/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.22/cluster-ab-latest-fix-full326-2026-07-22/`
  (did not exist before; no version-suffix collision).

## 7. Config lock (Step 6) — 15:20-15:21
- Wrote `00_CONFIG_LOCK.json` and `00_RUN_CONTEXT.md` recording repo paths, SHAs, benchmark input checksum, runner
  script checksums, catalog checksums (both commits), scoring thresholds, LLM judge config, and the historical
  baseline/previous-candidate identities to reuse.

## 8. Candidate server start
- Reused the `.next` build from the engineering-gate build (BUILD_ID `f-pp5Q3gQdRK6AuBomZkF-`, not rebuilt a second
  time). Ports 4520/4521 (used by the 7/21 baseline/candidate servers) intentionally left alone — this run does not
  reuse or restart them, since those CSVs are reused as static artifacts. Started `npm run start -- -p 4522`
  (port 4522 confirmed free beforehand). Verified `coffee cup` query → HTTP 307 redirect (`/en/search`→`/search`),
  same behavior documented in the 7/21 RUN_LOG.

## 9. Automated sanity check (Step 7)
- Ran 7 queries (笔袋, 人体图解, 促销海报, 日历, logo, movie poster, product photo) directly through `collector.mjs`
  against `http://localhost:4522`. All returned `ok=true`, HTTP 200, populated fields, non-zero results.
- **AUTOMATED_SANITY_PASS.** Flagged (not blocking) an odd top-2 result for 笔袋 (two unrelated tech-news templates)
  for later root-cause follow-up — see `01_AUTOMATED_SANITY_NOTES.md`.

## 10. Full-326 run (Step 8) — two attempts
- **First attempt (failed, caught before wasting the LLM budget):** invoked
  `run_eval_single.mjs ... http://localhost:4522 Infinity 6` — the literal string `"Infinity"` was passed for the
  `limit` argument. `run_eval_single.mjs` does `parseInt(args[5], 10)`, and `parseInt("Infinity", 10)` evaluates to
  `NaN` (not `Infinity`) — this made `dataRows.slice(0, NaN)` return **zero rows**. Caught immediately (`DONE 0/0` in
  the log), diagnosed the exact cause, and corrected the invocation to pass an **empty string** for that argument
  (which the script's `args[5] ? parseInt(...) : Infinity` correctly falls back to `Infinity` for) — no change to
  `run_eval_single.mjs` itself, this was purely an invocation-argument fix, not a modification of the established
  runner logic.
- Verified the fix with a 2-query smoke test (exit clean, 2/2 rows written), then a partial real run that was
  intentionally let run to a 2-minute foreground timeout to confirm sustained throughput (160/326 rows in ~120s at
  concurrency 6, 0 errors) before committing to the full background run.
- **Full run:** started 2026-07-22 15:25:58, `run_eval_single.mjs <bank.csv> query language
  eval_raw/CANDIDATE_LATEST_EASY326.csv http://localhost:4522 "" 6`. Completed 2026-07-22 15:29:43 (`DONE 326/326`),
  exit code 0, wall clock ≈3m45s. **0 collect errors, 0 timeouts.** Full worker log: `RUN_LOG_full326.txt`.

## 11. Completeness validation (Step 9) — 15:30
- 326/326 rows present, `row_index` 0-325 unique with no gaps, query-text alignment 326/326 against the bank.
- Label totals: PASS 38, PARTIAL 86, FAIL 195, UNJUDGABLE 7 — sums to 326.
- 7 UNJUDGABLE rows, all `NO_JUDGEABLE_RESULTS` (legitimate judge-rubric outcome, not a technical error) — rate
  consistent with the 7/21 runs (7/326 ≈ 2.1% here vs. 10-12/326 ≈ 3.1-3.7% previously).
- Full detail: `02_INPUT_OUTPUT_INTEGRITY.md`, `02_QUERY_COMPLETENESS.csv`.

## 12. Comparison baseline sourcing (Step 10)
- Reused `docs/daily_report/7.21/scorer-v1.1-evaluation-2026-07-21/eval_raw/BASELINE_EASY326.csv` (production main,
  `c550856e`, captured 2026-07-21) and `.../CANDIDATE_EASY326.csv` (previous candidate, pre-Cluster-A/B,
  `1e56e3f0`) **verbatim, not re-collected** — per the charter's instruction not to silently substitute current
  remote `main`. Both files' row_index alignment against the bank was independently re-verified in this run
  (`analyze_full326.py`), not merely assumed from the 7/21 report.

## 13. Analysis (Steps 11-17) — 15:30-15:40
- `scripts/analyze_full326.py`: three-way join on `row_index` (stable across all 3 runs, same bank file), alignment
  check (0 mismatches), produced `03`-`10`, `13` CSVs and `scripts/summary.json`.
- `scripts/root_cause.py`: automated, disclosed-heuristic root-cause classification over all 195 FAIL rows + 8
  regressed-PARTIAL rows → `12_REMAINING_FAILURE_ROOT_CAUSES.csv`.
- `scripts/cluster_ab_cases.py`: pulled the 17 named Cluster-A/B representative queries (from
  `search-relevance-v2r3-r1-2026-07-21.md` and the 7/21 `REGRESSION_ANALYSIS.md`) across all three runs →
  `11_CLUSTER_AB_REPRESENTATIVE_CASES.csv`.
- `scripts/key_cases.py`: compiled `14_KEY_CASES_FOR_MANAGER_REVIEW.csv` from the above outputs.

## 14. Cleanup
- Candidate server (port 4522) left running only as long as needed for the sanity check + full run; stopped before
  final integrity verification (Step 21 confirms this and confirms frontend worktree state).
- No files written into the frontend repository at any point in this run.

## Interruptions / retries / errors
- 1 invocation-level bug (the `"Infinity"`/`parseInt` issue above), caught and corrected before any LLM judge budget
  was spent (the failed attempt processed 0 queries, so 0 LLM calls were wasted).
- 0 collector timeouts, 0 collector errors, 0 unresolved judge-call failures in the final full run.
- No checkpoint/resume was needed (single uninterrupted 326/326 pass).

## Final completion state
**FULL_326_RUN = COMPLETE (326/326).**
