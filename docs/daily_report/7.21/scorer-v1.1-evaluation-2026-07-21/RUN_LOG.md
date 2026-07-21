# Scorer v1.1 Evaluation — RUN LOG (chronological)

Date: 2026-07-21. Operator: automated eval agent. Method reused from the 7/19 V2 / V2-R3 sessions
(`collector.mjs`, `judge.mjs`, `run_eval_single.mjs`) with no changes to the collection/judging logic.

## Worktrees / SHAs (both verified clean at start AND end)
- **Candidate** (scorer v1.1): `/Users/baobaoli/Desktop/curify-frontend-search-v2-r3-2026-07-19`
  branch `baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19`, HEAD `1e56e3f04da96c040c711efb54883e6d16d3ba0f`. node_modules pre-installed. NOT modified.
- **Baseline** (current production `main`): `/Users/baobaoli/Desktop/curify-frontend-main-baseline-2026-07-21`,
  detached HEAD `c550856e07c2c7058f955799beb9738e7a9b4f0a`. NOT the old V0 (`05e5f2d3`). NOT modified.

## Datasets
- Benchmark: `/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.16/easy-query-bank-v3/easy_query_bank_v2_2026-07-16.csv` (326 queries).
- Catalogs cross-referenced for path inference: `public/data/nano_inspiration.json` (3403 recs), `public/data/nano_templates.json` (335 recs).

## Ports
- Baseline `next start` on **4520**, Candidate `next start` on **4521**. Both ports confirmed free before start.

## Timeline
1. Verified worktree statuses, ports 4520/4521 free. Read `run_eval.mjs`, `run_eval_single.mjs`, `collector.mjs`, `judge.mjs`, the 7/19 gate report (`16_...GATE_RESULT.md`).
2. `npm install` in baseline **failed** first attempt — puppeteer postinstall tried to download chrome-headless-shell and rolled back all of node_modules (exit non-zero, node_modules absent). Re-ran with `PUPPETEER_SKIP_DOWNLOAD=true` → success, `node_modules/.bin/next` present.
3. Built candidate (`npm run build`, ✓ compiled ~26s) and baseline (`PUPPETEER_SKIP_DOWNLOAD=true npm run build`, ✓ ~32s). Note: an early attempt to `next start` the candidate raced the still-finishing build (missing `prerender-manifest.json`); restarted after BUILD_ID + manifest present.
4. Started both servers. Verified each returns a real RSC flight payload via `collector.mjs`:
   - Candidate 4521 `coffee cup` → HTTP 200, 80 inspirations, 188 total.
   - Baseline 4520 `coffee cup` → HTTP 200, 80 inspirations, 352 total (the `/en/search` → `/search` 307 redirect is followed by the collector).
5. **Targeted collection** (collector-only, no LLM): `scripts/targeted.mjs` dumped full per-item id/title/tags/topics for all 9 targeted queries from BOTH servers → `eval_raw/targeted/*.json`. Repeat-sampled 笔袋 x3 on candidate and x2 on baseline — deterministic (rewrites are cached identically per server).
6. **Full-326 candidate run**: `run_eval_single.mjs ... http://localhost:4521` → `eval_raw/CANDIDATE_EASY326.csv`. 326/326, 0 technical/judge errors.
7. **Full-326 baseline run** (started only AFTER candidate finished, to avoid the OpenAI-network contention documented in `judge.mjs`): `run_eval_single.mjs ... http://localhost:4520` → `eval_raw/BASELINE_EASY326.csv`. 326/326, 0 technical/judge errors.
8. **Analysis**: `scripts/analyze.py` joined the two per-query CSVs on row_index (query alignment verified NONE-mismatch across all 326), produced `FULL326_COMPARISON.csv`, `scripts/summary.json`, the transition matrix, improved/regressed lists, new/recovered zero-result lists, and the 5 headline gate conditions. Judge-noise vs real-transition split computed by comparing byte-identical top-5 title lists.
9. Path-attribution root cause for 笔袋 investigated by catalog cross-reference (disclosed inference — see below).

## Judging
- Model `gpt-4o-mini`, rubric-v1.1 deterministic scoring, textual (title/tags/topics) evidence only — same disclosed limitation as the 7/19 runs. Every PASS/PARTIAL/FAIL/UNJUDGABLE in this report comes from an actual `judgeResultSet` call in runs (6)/(7). No numbers fabricated or extrapolated. No section was reduced to a smaller sample — full 326 on both sides.

## Path-attribution method (disclosure)
The unified scorer is inlined as closures inside `app/[locale]/(public)/search/page.tsx` (references outer-scope
`templateSearchBlob`, `scoreBlob`, `buildSearchTokens`), so `scoreRecord` cannot be exercised in isolation without
reconstructing the whole retrieval pipeline — and instrumenting `page.tsx` would violate the no-edit constraint on the
frozen worktree. Per the charter's sanctioned fallback, per-candidate original-vs-non-original attribution is therefore
**inference**, cross-referencing each returned item's title/tags/topics/id and the record's full catalog entry
(`nano_inspiration.json`) against the original query tokens and `usedRewrites`. Where a conclusion rests on this
inference rather than direct scorer output, it is labelled as such in `TARGETED_CASE_ANALYSIS.md` / `REGRESSION_ANALYSIS.md`.

## Cleanup
- Both `next start` servers stopped; ports 4520/4521 confirmed free.
- Both worktrees `git status` clean at expected SHAs (candidate byte-for-byte `1e56e3f0`, baseline `c550856e`).

## NOT_RUN / limitations
- Screenshot-grade visual judging not performed (textual only) — same disclosed tradeoff as prior sessions.
- Exact internal token that satisfied `subjectPresent` for the 笔袋 western-food candidate not confirmable without
  scorer instrumentation; reported as disclosed inference, not direct measurement.
- No statistical significance tests (McNemar/bootstrap/Wilcoxon) were computed this run; the gate is applied on the
  raw label/zero/improved-regressed counts as in `16_...GATE_RESULT.md`. Flagged as a scope reduction vs the 7/19 statistical companion.
