# Stage 7R Prompt 3 — Guard Smoke Test Harness

Read-only against `curify-frontend`. Bundles the real, current (post-Prompt-2)
production modules via esbuild and transcribes `page.tsx`'s page-local
scoring orchestration (the same established pattern already used by
`scripts/curify-search-collect-stage7/run_mode.cjs`), with a drift detector
that refuses to run if the live `page.tsx` no longer contains the expected
Guard 1/2/3 code.

## Files

- `build_bundle.cjs` — esbuild-bundles `lib/searchRewrite.ts` (incl. the real
  Guard 2 `flattenPathsWithDiagnostics`), `lib/query_phrase_aliases.ts`,
  `lib/cjk_tokenizer.ts`, `lib/zh_normalize.ts`, `lib/topic_resolver.ts` from
  curify-frontend into `_bundle_current.cjs`. Run this first (and re-run it
  if curify-frontend's source changes — it will silently go stale otherwise,
  exactly like the original Stage 7 bundle did across Prompt 2).
- `scoring.cjs` — transcription of `page.tsx`'s `buildSearchTokens`/
  `scoreBlob`/`hasExecutableConstraint` (Guard 1's fix), plus
  `verifyAgainstLiveSource()` which reads the live `page.tsx` and asserts
  8 critical substrings are present before any run proceeds.
- `engine.cjs` — shared Mode-D (d=ON, g=ON) search engine: loads the real
  catalog, real template i18n, and mirrors `page.tsx`'s decomposition-path
  merge loop including the Guard 1/2/3 wiring added in Prompt 2.
- `csv_utils.cjs` — minimal CSV parser/writer (refuses to overwrite existing
  files).
- `replay.cjs` — **Phase A: Deterministic Replay.** Reads the frozen
  `smoke_test_query_set_2026-07-14.csv` Phase-A rows, loads the exact raw
  rewrite/decomposition JSON already recorded in 7.13's
  `hard_queries_68_ablation.csv` (mode D for the 23 flood cases, mode C for
  Q39/Q40/Q42), and re-runs them through the current Guard code. **No LLM
  call is made.**
- `live.cjs` — **not created this run.** Phase B (Limited Live Smoke) was
  gated off per Prompt 3's Step 6 rule (Replay did not reach the 80%
  improvement threshold — see the summary report). If a future run reaches
  the Replay gate, a `live.cjs` companion to `replay.cjs` should be added
  that calls the real `bundle.getMultiQueryPaths` (a genuine OpenAI call)
  instead of injecting a `multiPathsOverride`.

## Usage

```bash
cd /Users/baobaoli/Desktop/visual-search-adhoc/scripts/curify-search-stage7-guard-smoke
node build_bundle.cjs   # rebuild the bundle from current curify-frontend source
node replay.cjs         # Phase A: deterministic replay, no LLM calls
```

Both scripts refuse to overwrite existing output files and never touch
`scripts/curify-search-collect-stage7/` (that directory's own bundle predates
Prompt 2 and must not be reused for testing the Guards — see `build_bundle.cjs`'s
header comment).

Do **not** run this harness against the full 68-query gold set — it is scoped
to the fixed Prompt-3 smoke query set only, and no CLI flag is provided to do
otherwise.
