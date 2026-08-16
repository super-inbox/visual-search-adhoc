# Creative Direction — Product Iteration (2026-08-17)

This is the **product follow-up** to `docs/daily_report/8.16/creative-direction-trajectory/` (Task C
research). That pass audited the real Brand Direction Explorer, ran a synthetic preference
experiment, and recommended (P0-0) adding a minimal optional preference input to the real product as
the highest-priority next step. This directory documents that iteration actually being built and
validated with real execution — not more research, not another synthetic experiment.

## Repository policy

**All official Task C deliverables for this iteration live under
`visual-search-adhoc/docs/daily_report/8.16/creative-direction-product-iteration/` (this directory).
Nothing was committed or pushed to the frontend repository.**

- `curify-frontend-brand-direction-explorer` (branch
  `baobao/brand-direction-explorer-tool-demo-2026-08-04`) was used **only as a local implementation
  and validation environment** — the place where the actual code was written, unit-tested, typechecked,
  and exercised against the real live local dev server for the 6 real Stage-1 calls.
- **No frontend commit was created.** The 7 changed files (6 modified, 1 new) remain uncommitted,
  local working-tree changes in that worktree.
- **No frontend push was performed.** Nothing left the local machine via that worktree.
- The complete implementation is archived here, not in frontend git history, as
  **`IMPLEMENTATION_PATCH.diff`** — a full, reviewable `git diff` (verified to apply cleanly via
  `git apply --check` against a clean checkout of the base commit) covering all 7 files, including the
  1 file that is still untracked in the frontend worktree. **`IMPLEMENTATION_FILES.md`** documents
  what changed in each of those 7 files in prose.
- This is the reproducible, reviewable record of the change: apply `IMPLEMENTATION_PATCH.diff` to a
  clean checkout of `curify-frontend-brand-direction-explorer` at commit `322cd51f` to reproduce it
  exactly, without needing frontend git history to carry the change.

```
Frontend worktree (local implementation/validation environment only — not committed, not pushed):
/Users/baobaoli/Desktop/curify-frontend-brand-direction-explorer
branch: baobao/brand-direction-explorer-tool-demo-2026-08-04
```

## Product change (summary)

On the implementation branch (uncommitted, not pushed/merged/deployed), the actual Brand Direction
Explorer Stage 1 generation path (OpenAI creative-direction generation) now accepts an optional,
stateless `preferenceProfile: { likes?: string; dislikes?: string }` alongside the existing
`{ caseId, fieldValues }` request. See `FINDINGS.md` for the full file-by-file breakdown, the exact
request contract, and how preference enters the real system/user prompt sent to `gpt-4o-mini`. A
baseline request (no `preferenceProfile`) is fully backward compatible — the assembled OpenAI prompt
is byte-identical to before this change.

A duplicate-title validation gate was also added (reusing the existing retry mechanism), directly
fixing a real quality gap the prior research pass documented (a real captured run where all 3
`coffee-opening` directions shared the title "Morrow Coffee").

## Validation methodology

1. **Static**: 27 new/updated unit tests (`lib/__tests__/brand_direction_explorer.test.ts`,
   `brandDirectionOpenAI.test.ts`, new `brand_direction_explorer_route.test.ts`) plus all 54
   pre-existing tests, 277/277 passing repo-wide. TypeScript clean.
2. **Real Stage-1 execution**: 6 real POST requests to the live local dev server's
   `/api/brand-direction-explorer/directions` route (`gpt-4o-mini`, live OpenAI calls, not mocks, not
   replayed archives) — 3 scenarios × {baseline, personalized}, all succeeded. This is genuinely
   `real_current_agent_output`, captured 2026-08-17 running this pass's own code.
3. **Paired evaluation**: each of the 3 scenario pairs scored on 8 dimensions (relevance,
   brief_integrity, direction_diversity, specificity, actionability, preference_fit,
   visual_distinctiveness, redundancy) by this pass's own evaluator (not a human designer/client —
   see limitations below), following the same rubric shape as the prior research pass's
   `EVALUATION_RUBRIC.md`.

## Evidence files

- `IMPLEMENTATION_PATCH.diff` — the full, reproducible patch for all 7 changed frontend files (6
  modified + 1 new), archived here per repository policy since nothing was committed to frontend.
- `IMPLEMENTATION_FILES.md` — file-by-file prose documentation of what changed and why.
- `real_paired_runs.jsonl` — 6 real run records (brief input, synthetic preference input where
  applicable, real directions returned, execution status).
- `real_paired_evaluation.csv` — 3 scenario pairs × {baseline, personalized}, 8-dimension scores,
  winner, confidence, rationale.
- `gallery.html` — open directly in a browser (no server required, data is inlined). Shows each
  scenario's identical brief, the synthetic preference input, both direction sets side by side, scores,
  and winner, with visible `REAL CURRENT AGENT OUTPUT` / `SYNTHETIC PREFERENCE INPUT` badges.
- `FINDINGS.md` — direct answers to the 16 boss-level questions this iteration was scoped against.
- `DAILY_REPORT.md` — manager-readable summary with exact counts.
- `screenshots/BLOCKED.md` — UI screenshots were attempted but blocked (Chrome extension not
  connected); documented honestly rather than fabricated.

## How to open the gallery

```
open gallery.html
```
(or drag it into any browser — it's a self-contained static file, same convention as the prior
research pass's `creative-direction-trajectory/gallery.html`.)

## Limitations

- n=3 real paired cases. This is a **small real validation**, explicitly not a benchmark or
  statistically powered claim — see `FINDINGS.md` §15.
- All scoring is this pass's own evaluator judgment, not a real human/designer/client preference
  judgment. No human labels exist yet for the real personalized output.
- Only the 3 fixed scenarios the real tool supports were tested (`coffee-opening`,
  `tea-brand-exploration`, `event-poster`) — no other domain has a real scenario to test against.
- 1 of 3 real pairs showed a real, observed weakness (diversity reduction + a partial preference
  self-contradiction) — preference does not uniformly help; see `FINDINGS.md` §12–13.

## Why trajectory SFT remains future work

This pass adds real, preference-bearing Stage-1 trajectories (6 of them) that could eventually feed a
trajectory-SFT dataset, but: no model is trained here, no human/target-user judgment exists on any of
these 6 real trajectories, and the sample is far too small (n=3 pairs) to be training-ready. The prior
research pass's own conclusion — real preference input, more real scenarios, real human judgments, and
real paired volume at 10+ pairs are all needed before SFT training is warranted — still holds. This
iteration satisfies exactly one of those four prerequisites (a real preference input now exists in the
product); the other three remain open.
