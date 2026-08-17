# DAILY_REPORT.md — Task C product iteration (2026-08-17)

Product follow-up to `docs/daily_report/8.16/creative-direction-trajectory/` (Task C research). That
pass's top recommendation (P0-0) was: add a minimal optional preference input to the real Brand
Direction Explorer. This pass implements exactly that on the implementation branch
(`curify-frontend-brand-direction-explorer`, branch `baobao/brand-direction-explorer-tool-demo-2026-08-04`,
uncommitted, not pushed/merged/deployed), and validates it with 6 real Stage-1 OpenAI calls against
that branch's actual generation path.

## Repository policy

The frontend worktree (`curify-frontend-brand-direction-explorer`) was used **only as a local
implementation and validation environment** — where the code was written, tested, and exercised
against real OpenAI calls. **No frontend commit was created. No frontend push was performed.** The
implementation is archived here instead, as `IMPLEMENTATION_PATCH.diff` (full reproducible patch,
verified to apply cleanly to a clean checkout) and `IMPLEMENTATION_FILES.md` (per-file documentation).
**All official Task C deliverables for this iteration live under
`visual-search-adhoc/docs/daily_report/8.16/creative-direction-product-iteration/`** — this directory
is the complete, self-contained record; nothing required from frontend git history to review or
reproduce the change.

## Counts

| Metric | Count |
|---|---|
| Frontend files changed | 7 total — 6 modified (`lib/brand_direction_explorer.ts`, `lib/brandDirectionOpenAI.ts`, `app/api/brand-direction-explorer/directions/route.ts`, `BrandDirectionExplorerClient.tsx`, `lib/__tests__/brand_direction_explorer.test.ts`, `lib/__tests__/brandDirectionOpenAI.test.ts`) + 1 added (`lib/__tests__/brand_direction_explorer_route.test.ts`, untracked — `git diff --stat` alone only shows the 6 modified files since an untracked file has no diff against HEAD; see `git status --short` for the 7th) |
| Frontend test files added | 1 (`lib/__tests__/brand_direction_explorer_route.test.ts`, 10 tests) |
| Frontend test files updated | 2 (`brand_direction_explorer.test.ts` +7 tests, `brandDirectionOpenAI.test.ts` +10 tests) |
| Total unit tests passing (repo-wide) | 277 / 277 |
| Pre-existing brand-direction-explorer tests still passing | 54 / 54, unchanged |
| New brand-direction-explorer tests added | 27 |
| TypeScript | clean (`tsc --noEmit`, 0 errors in touched files, 0 repo-wide) |
| Lint | blocked — pre-existing `eslint`/`typescript-eslint` version-mismatch config error, unrelated to this change (fails at config-load time for any file) |
| Scenarios validated (real) | 3 of 3 (`coffee-opening`, `tea-brand-exploration`, `event-poster` — all scenarios the real tool has) |
| Baseline real runs attempted | 3 |
| Personalized real runs attempted | 3 |
| Successful real runs | 6 / 6 (HTTP 200, exactly 3 valid uniquely-titled directions each) |
| Personalized wins | 2 (coffee-opening medium confidence, event-poster high confidence) |
| Baseline wins | 1 (tea-brand-exploration, medium confidence) |
| Ties / inconclusive | 0 |
| Screenshots captured | 0 — blocked, Chrome extension not connected (see `screenshots/BLOCKED.md`) |
| API backward compatibility | Confirmed — request with no `preferenceProfile` unchanged, unit-tested and confirmed with 3 real baseline calls |
| Secrets exposed | 0 — `.env.local`'s `OPENAI_API_KEY` was checked for presence/length only, never read or printed |
| Frontend commits created | 0 |
| Frontend pushes performed | 0 |
| Implementation patch archived | Yes — `IMPLEMENTATION_PATCH.diff` (7 files, verified to apply cleanly to a clean checkout of base commit `322cd51f`) |

## What changed in Brand Direction Explorer

On the implementation branch (uncommitted, not pushed/merged/deployed), the actual Brand Direction
Explorer Stage 1 generation path (OpenAI creative-direction generation) now accepts an optional
`preferenceProfile: {likes?, dislikes?}` in the directions request. When present, it's validated (reject malformed shapes, no
arbitrary nested objects), normalized, and appended to the real system/user prompt as a `VISUAL
PREFERENCE` section with explicit rules: brief always outranks preference, preference must materially
shape at least one concrete visual decision without just restating itself, the 3 directions must stay
distinct even under a strong preference, and preference is stylistic guidance only (no imitating a
named artist/brand). A duplicate-title validation gate was added, reusing the existing retry loop — a
direct fix for a real quality gap the prior research pass documented (`coffee-opening`'s "Morrow
Coffee ×3" real captured run). A new optional "Visual preference (optional)" UI section (Prefer/Avoid
textareas, EN/ZH copy) was added to the page. Final visual generation (Stage 2, Gemini-backed) is
completely unchanged.

## What we learned

Preference materially and traceably changes real model output in checkable ways (typography,
composition, material choices) — confirmed with real, not synthetic, executions. It does not
uniformly help: 1 of 3 real pairs showed reduced direction diversity and a partial internal
preference contradiction (introducing "gold accents" while the preference explicitly asked to avoid
"generic luxury black-and-gold"). This is consistent with, and independently observed from, the prior
research pass's synthetic-experiment finding of the same failure shape (over-constraint / partial
misfire). n=3 real pairs is a small real validation, not a benchmark.

## Best before/after example

**event-poster** (see `gallery.html`, pair-3): 2 of 3 personalized directions concretely reflected
"bold modular typography" and "community collage energy" (explicit "bold modular fonts," "vibrant
collage... tapestry of activity" language) while the 3rd direction stayed in a distinct, calmer
register — real influence without collapsing the 3-way spread. High confidence win.

## Current limitation

**tea-brand-exploration** (pair-2): the clearest weak spot. All 3 personalized directions converged on
the same "hero product shot + palette swatch strip" composition (a real diversity reduction vs.
baseline), and 2 of 3 introduced gold-accent language that sits close to what the preference itself
asked to avoid. The prompt-level diversity/no-imitation rules did not fully prevent this in this one
case — a real, observed limit of a prompt-only safeguard (no deterministic diversity/self-consistency
check exists).

## Next step

Direction-selection telemetry (log which of the 3 directions a user picks) is the cheapest next real
signal — no new input schema needed. A larger real paired sample (10+) and a real
human/designer/client judgment (replacing this pass's own evaluator scoring) are the actual
prerequisites before any personalization claim stronger than "small real validation" is warranted.
Trajectory SFT remains explicitly future work.
