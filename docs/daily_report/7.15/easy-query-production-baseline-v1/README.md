# PRODUCTION PRE-OPTIMIZATION EASY-QUERY BASELINE — 2026-07-15

## 1. Why this test

The 2026-07-15 meeting required re-running the full 300+ Easy Query set against the **current live production Curify search**, before search-relevance optimization work is merged, so the team has a trustworthy "before" baseline that later optimized-version results can be compared against. The only prior full run of this exact 328-query set (`docs/daily_report/7.14/.../easy_query_validation_manifest_2026-07-14.json`) used the **local, uncommitted, unpushed** search-optimization branch — not production — so no valid pre-optimization baseline existed until this run.

## 2. Definition of "original version"

"原始版本" = the code currently deployed and serving `https://www.curify-ai.com`, confirmed via GitHub Deployments API + `origin/main` HEAD + `vercel.json` deployment rules to be commit `72b55b667bb5173cab87fcec377198064dc3ac28`. It is **not** `origin/main` by assumption — that equivalence was independently corroborated (see `CODE_VERSION_AUDIT.md`), and it is explicitly **not** the local `baobao/search-relevance-phrase-alias-2026-07-09` branch (uncommitted, never pushed to GitHub — confirmed via a 404 on that commit SHA against the remote).

## 3. Why the live production site is the authoritative test target

Per task priority order: production website > deployed commit > local checkout. The production site was reachable, functional, unauthenticated, and served real rendered results throughout this run, so Choice 1 (direct browser automation against the live site) was used — no fallback to a local checkout was needed. All queries were executed as real `GET https://www.curify-ai.com/search?q=<query>` page loads through a real Chromium browser (Playwright), i.e. exactly what a human visitor would trigger.

## 4. Production URL used

`https://www.curify-ai.com` — search page pattern `https://www.curify-ai.com/search?q={query}`.

## 5. Production commit confirmation

**Confirmed**, `production_commit_confidence: HIGH`, cross-validated via (a) GitHub Deployments API (most recent `environment: "Production"`, `state: "success"` deployment), (b) exact match with `origin/main` HEAD, (c) `vercel.json`'s `git.deploymentEnabled` rules (only `main` auto-deploys). Full evidence chain in `CODE_VERSION_AUDIT.md`.

## 6. Query file used

`query_input/easy_queries_cleaned_300_plus_2026-07-14.csv` — 328 data rows (`E001`–`E328`), SHA-256 `682ed08a97f69ff39317c923ac859fe2f085ab8e8d7b9dc7b1a0f31fa0b32f3e`, identical (byte-for-byte, hash-verified) to the file consumed by the prior optimized-code run per that run's own manifest. Full selection chain in `QUERY_FILE_AUDIT.md`.

## 7. Collection method

Playwright/Chromium browser automation, adapted from a previously-proven production collector (`scripts/curify-search-collect/collect_curify_search.mjs`, already used successfully for the 68 gold hard queries). Full method rationale in `COLLECTION_METHOD.md`; adaptation details and audit in `COLLECTOR_AUDIT.md`.

## 8. Is an LLM used?

- **By the collector**: No. `scripts/collect_easy_query_baseline.mjs` has zero LLM/OpenAI dependency — it is a pure browser driver.
- **By production search itself**: **Yes.** `lib/searchRewrite.ts` (confirmed present at the production commit) calls OpenAI `gpt-4o-mini` server-side for thin-result queries, and has done so since 2026-05-18 — this is pre-existing baseline production behavior, not part of the unpushed optimization branch. See `CODE_VERSION_AUDIT.md` §3.

## 9. Rewrite/broaden behavior observed

Whenever production renders its "Few results for X. Also showing results for: Y, Z" banner, the collector records it verbatim (`raw_rewrite_visible`, `broadened_query`, `rewrite_observed=true`). See `final/easy_query_production_baseline_rewrite_observed.csv` for the full list and `final/easy_query_production_baseline_summary.md` for the count.

## 10. Optimization features confirmed NOT present in this baseline

All 26 items on the task's optimization checklist were audited against the production commit and found `NOT_FOUND` (no Rewrite Guard, no protected-phrase dictionary, no d/g toggles, no A/B/C/D mode, no dedicated CJK tokenizer, no niche-vertical rules, no negative-cache fixes, no anchor-piggyback fix). Full item-by-item table in `CODE_VERSION_AUDIT.md` §2.

## 11. How to resume this run

Re-run `node scripts/collect_easy_query_baseline.mjs --full` from the `scripts/` directory. The collector treats any existing `raw/<idx>_<easy_id>.json` file with `final_status` ∈ {SUCCESS, ZERO_RESULT, LOW_RESULT, INPUT_INVALID} as already complete and skips it; anything else (network error, timeout, parse error, or a missing file) is genuinely re-executed, up to 2 attempts. Checkpoints are written every 10 completed queries to `checkpoints/`.

## 12. How to verify result completeness

Run `python3 scripts/build_final_outputs.py` — it reads every `raw/*.json`, cross-checks `query_index` uniqueness/contiguity/order against the input CSV, and writes `final/easy_query_production_baseline_integrity_report.md`.

## 13. Output files

See `final/` for delivered results (full results CSV/JSONL, summary, zero/low-result/error/timeout/broadened/rewrite subsets, top-results long table, integrity report, file manifest, run log) and `summaries/` for the manual-review priority queue and (if confirmed available) the baseline-vs-optimized join-ready comparison file. `RUN_MANIFEST.json` at the run root has the full machine-readable run record.

## 14. Main limitations / uncertainties

- Production does not render a visible numeric "N results found" total anywhere in the DOM; `result_count_reported` is therefore recorded as `null` throughout, and `result_count_observed` (actual rendered card count, capped at 200 for extraction sanity) is used as the operative count instead. This is a real limitation of what the UI exposes, not a collector gap.
- `filter_state` / `pagination_state` are `null` throughout — production's search results page has neither a filter UI nor pagination (confirmed by source audit), so there is nothing to record.
- `spelling_correction_visible` could not be positively confirmed as a distinct signal separate from the general rewrite/broaden banner; recorded as `null` rather than guessed.
- The comparison against the 2026-07-14 optimized-code run is informational only (different code path — local optimized vs. live production) and is explicitly marked as such; see `summaries/baseline_vs_optimized_join_ready.csv` and its warnings column.
- A DOM-extraction bug was found post-run affecting `broadened_query`/`raw_rewrite_visible` text (over-capture of a larger ancestor element) for 17/139 broadened records. It never affected `result_count_observed`/`zero_result`/`low_result`. Fixed and those 17 records were re-collected live (resume logic left the other 311 untouched). Because production's rewriter runs at non-zero temperature, a handful of the 17 re-collected records show a slightly different `final_status`/count than their first pass — this is genuine live-system variance, not a defect. Full detail in `logs/resume_history.md`.
