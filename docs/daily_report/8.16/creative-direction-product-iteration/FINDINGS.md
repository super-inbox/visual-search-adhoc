# FINDINGS.md

Task C product iteration: minimal optional preference input for the real Brand Direction Explorer
(`curify-frontend-brand-direction-explorer`, branch `baobao/brand-direction-explorer-tool-demo-2026-08-04`).
Evidence: `real_paired_runs.jsonl` (6 real Stage-1 OpenAI calls), `real_paired_evaluation.csv` (3
scored pairs), `gallery.html`. All findings below are drawn only from those files plus direct code
inspection — nothing here is carried over from the prior `creative-direction-trajectory` research
pass's synthetic experiment.

**Repository policy:** the frontend worktree (`curify-frontend-brand-direction-explorer`) was used
only as a local implementation and validation environment. No frontend commit was created and no
frontend push was performed — the 7 changed files remain uncommitted local working-tree changes
there. The reproducible record of the implementation is archived in this directory instead, as
`IMPLEMENTATION_PATCH.diff` (full patch, verified to apply cleanly to a clean checkout) and
`IMPLEMENTATION_FILES.md` (prose documentation). All official Task C deliverables for this iteration
live under `visual-search-adhoc/docs/daily_report/8.16/creative-direction-product-iteration/`.

## 1. What actual product behavior changed?

On the implementation branch (`baobao/brand-direction-explorer-tool-demo-2026-08-04`, uncommitted,
not pushed/merged/deployed), the Brand Direction Explorer's actual Stage 1 generation path
(creative-direction generation) now accepts an optional, stateless `preferenceProfile`
(`{likes?, dislikes?}`) alongside the existing `{caseId, fieldValues}` request. When supplied, it is normalized, validated, and appended to the real OpenAI system/user
prompt as a `VISUAL PREFERENCE` section that materially shapes the 3 generated directions —
confirmed by real captured output (`real_paired_runs.jsonl`), not by code inspection alone. A new
"Visual preference (optional)" UI section (two textareas: Prefer / Avoid) was added to the page. A
request with no `preferenceProfile` is unaffected: the assembled OpenAI user message is byte-for-byte
identical to before this change (see `buildPreferenceSection` returning `null` when there is nothing
to add — verified by a unit test).

## 2. Which frontend files changed?

- `lib/brand_direction_explorer.ts` — added `PreferenceProfile` type, `MAX_PREFERENCE_FIELD_LEN`,
  `normalizePreferenceProfile()`.
- `lib/brandDirectionOpenAI.ts` — `generateCreativeDirections()` gained an optional third parameter;
  `buildUserMessage()`/new `buildPreferenceSection()` append the `VISUAL PREFERENCE` section;
  `SYSTEM_PROMPT` gained preference-handling rules and a title-distinctness rule;
  `parseAndValidateDirections()` gained a duplicate-title gate.
- `app/api/brand-direction-explorer/directions/route.ts` — accepts and strictly validates an optional
  `preferenceProfile` field before calling `generateCreativeDirections`.
- `app/[locale]/(public)/brand-direction-explorer/BrandDirectionExplorerClient.tsx` — new preference
  state, a debounced-refetch dependency on it, and the "Visual preference (optional)" UI section
  (EN/ZH copy).
- Tests: `lib/__tests__/brand_direction_explorer.test.ts` (added `normalizePreferenceProfile` cases),
  `lib/__tests__/brandDirectionOpenAI.test.ts` (added preference-in-prompt and duplicate-title cases),
  new `lib/__tests__/brand_direction_explorer_route.test.ts` (request-shape validation).

No other file changed. Stage 2 (`services/useFreeformGenerate.ts`, the Gemini-backed final-image
call) was not touched. 7 files total (6 modified + 1 new) — see `IMPLEMENTATION_FILES.md` for the
full per-file breakdown and `IMPLEMENTATION_PATCH.diff` for the actual reproducible patch, both
archived in this directory since the frontend worktree holds these changes only as uncommitted local
edits.

## 3. What preference request contract was added?

```json
{
  "caseId": "coffee-opening",
  "fieldValues": { "...": "..." },
  "preferenceProfile": { "likes": "...", "dislikes": "..." }
}
```

`preferenceProfile` is fully optional; both `likes`/`dislikes` are optional strings capped at
`MAX_PREFERENCE_FIELD_LEN` (400 chars). The route rejects (400) anything that isn't a plain object,
any key other than `likes`/`dislikes`, non-string values, and over-length values — it does not
silently accept arbitrary nested objects (verified: a `referenceImages` key or a nested object value
is rejected, see `brand_direction_explorer_route.test.ts`). Content normalization (whitespace
collapse, trim, empty→undefined) happens downstream in `normalizePreferenceProfile`, reused by both
the route-adjacent OpenAI module and (via the same trimming logic reimplemented client-side) the UI.

## 4. How does preference enter the actual OpenAI Stage-1 prompt?

`generateCreativeDirections()` normalizes the profile, then `buildUserMessage()` appends a
`VISUAL PREFERENCE` section (only when non-empty) to the existing `PROJECT BRIEF` + output-format
user message. `SYSTEM_PROMPT` carries the interpretation rules (brief priority, material influence,
diversity-preservation, no-imitation) — see `lib/brandDirectionOpenAI.ts`. This is confirmed by real
executed prompts, not just static code: `real_paired_runs.jsonl`'s personalized-mode directions show
concrete, checkable content shifts traceable to the supplied preference (see item 10 below).

## 5. How is brief integrity protected?

Three layers, all pre-existing plus one new rule: (a) `buildProjectBrief`/`normalizeAndValidateFields`
still throw on any missing/blank required field regardless of preference — untouched by this change;
(b) the `USER-PROVIDED DATA` section (Stage-2 prompt) and the `PROJECT BRIEF` section (Stage-1 prompt)
are unchanged and still appear before any preference content; (c) the new `SYSTEM_PROMPT` rule
explicitly states "the PROJECT BRIEF's explicit requirements always take priority over [preference] —
preference shapes interpretation, it never overrides or drops a brief requirement." In the 3 real
pairs run, brief_integrity scored 4–5/5 in every personalized case (see `real_paired_evaluation.csv`)
— no case dropped a required brief fact. One real, mild tone-drift was observed (event-poster
direction 2 skewed "energetic/celebratory" vs. the brief's "laid-back" — a soft mood interpretation
stretch, not a dropped fact), scored `brief_integrity: 4` rather than 5 for that pair.

## 6. How is direction diversity protected?

A prompt-level rule ("apply [preference] differently across the 3 directions... never collapse all 3
into one preferred look with only superficial variation; each direction must still satisfy the
diversity rule above") plus the pre-existing diversity rule, both in `SYSTEM_PROMPT`. No new
deterministic diversity gate was added — this is intentionally prompt-only per the task's "no
expensive multi-agent review system" constraint. Real evidence shows this is necessary but not
sufficient: 2 of 3 real pairs preserved good diversity (`direction_diversity` 4/5), but 1 pair
(tea-brand-exploration) showed a real, observed diversity reduction — all 3 personalized directions
converged on the same "hero product shot + palette swatch strip" compositional structure, scoring
`direction_diversity: 3` vs. the baseline's `5`. See item 13.

## 7. How are duplicate titles handled?

`parseAndValidateDirections()` now checks all 3 `title.en` values for case-insensitive, trimmed
distinctness after the existing per-direction field checks; a collision returns
`{ ok: false, reason: "duplicate_direction_title_..." }`, which the existing retry loop in
`generateCreativeDirections` (up to `MAX_ATTEMPTS = 3`) already re-requests on, identically to how it
already handles malformed JSON or a wrong direction count — no new retry mechanism was built. Unit
tests cover: a direct duplicate rejected, a case-insensitive duplicate rejected, and a full
retry-then-succeed cycle. In the 6 real captured runs, no duplicate titles occurred (all 18 real
directions across the 6 runs had distinct `title.en` values) — a good sign, though this doesn't prove
the fix's necessity retroactively, since the specific `coffee-opening`/"Morrow Coffee" repeat
documented in the prior research pass was observed on a different real run (2026-08-06/07,
`docs/daily_report/8.16/creative-direction-trajectory/`), not this pass's.

## 8. Does the old baseline flow remain backward compatible?

Yes, on three levels: (a) unit test — a request with no `preferenceProfile` produces a user message
containing no `VISUAL PREFERENCE` text at all (byte-identical prompt shape to pre-change code); (b)
real execution — `run-001-coffee-baseline`, `run-003-tea-baseline`, `run-005-event-baseline` in
`real_paired_runs.jsonl` are real, successful, unmodified-request calls; (c) all 54 pre-existing unit
tests still pass unchanged, plus 33 new/modified tests, for 277 tests passing repo-wide.

## 9. Were real baseline/personalized runs executed?

Yes. 6 real Stage-1 OpenAI (`gpt-4o-mini`) calls against the actual local dev server's
`/api/brand-direction-explorer/directions` route, running this pass's own code (not archived/replayed
output) — 3 scenarios × {baseline, personalized}, all HTTP 200, all returning exactly 3 valid,
uniquely-titled directions. See `real_paired_runs.jsonl`. These are genuinely
`real_current_agent_output` per the task's own labeling convention, captured 2026-08-17.

## 10. Did preference materially change the directions?

Yes, in checkable, concrete ways — not just restated preference wording:
- **coffee-opening**: baseline directions are photography/product-shot led ("coffee cup placed
  artfully," "close-up of a minimalist coffee cup"); personalized directions shift to
  typography/editorial-led compositions ("large typography, the name... prominently," "ample negative
  space around the headline elements") with explicit "editorial" style tags and tactile/raw-paper
  materials — a real compositional shift traceable to "editorial typography... tactile natural
  materials."
- **tea-brand-exploration**: personalized direction 2 explicitly adds botanical illustration
  ("delicate botanical illustrations") — directly traceable to "subtle botanical detail."
- **event-poster**: 2 of 3 personalized directions explicitly use "bold modular fonts" and describe a
  "vibrant collage of community engagement... tapestry of activity" — directly traceable to "bold
  modular typography, community collage energy."

## 11. Where did personalization help most?

**event-poster** (pair-3, `personalized_win`, high confidence) — the cleanest case. 2 of 3 directions
concretely and materially reflected the preference (modular typography; collage composition) while
the 3rd stayed in a calmer, distinct register, preserving real choice rather than collapsing to one
look. No corporate-minimalism/startup-gradient language appeared anywhere. This is this pass's
strongest example.

## 12. Where was its effect weak?

**tea-brand-exploration** (pair-2, `baseline_win`, medium confidence) — the weakest case, and a
genuinely useful negative finding: preference was only partially honored (botanical detail landed;
"contemporary Chinese editorial design" and "generous negative space" did not land as concretely), 2
of 3 personalized directions introduced "gold accents"/"golden undertones" that sit close to the
preference's own explicitly-stated negative ("avoid generic luxury black-and-gold") — a real, internal
preference self-contradiction, not a hypothetical one — and all 3 personalized directions converged on
the same hero-shot + palette-swatch-strip composition, a measurable diversity reduction vs. baseline's
3 distinct compositions.

## 13. Did preference reduce diversity?

In 1 of 3 real pairs, yes, measurably: tea-brand-exploration's personalized set scored
`direction_diversity: 3` vs. baseline's `5` (see `real_paired_evaluation.csv`), driven by a shared
compositional device (hero product shot + palette swatch strip) appearing in all 3 personalized
directions instead of baseline's 3 distinct compositions. coffee-opening showed a smaller, real
narrowing (`4` vs. `5` — all 3 personalized directions sit in a warm/neutral editorial register vs.
baseline's rustic/gold-modern/vintage-whimsical spread) but did not collapse. event-poster preserved
diversity essentially intact (`4` vs. `5`, within the same small-sample noise band). This is a real,
observed pattern in a 3-pair sample — consistent in direction (some narrowing risk under preference)
with, but independently observed from, the prior pass's synthetic-experiment finding of the same
failure mode (`cdq-001`/`cdq-023` in `creative-direction-trajectory/FINDINGS.md`).

## 14. Were there repeated-title issues?

No, in this specific run: all 18 real directions across the 6 real calls had distinct `title.en`
values, so the new duplicate-title validation gate never had to trigger a retry in this sample. The
gate exists and is unit-tested (item 7) as a safeguard against the previously-documented real
"Morrow Coffee ×3" repeat, but this pass's own 6 real calls did not reproduce that specific failure —
absence of a failure in n=6 does not prove the gate is unnecessary; the prior occurrence (n=1, a
different real run) is the reason it exists.

## 15. Is this enough to claim personalization is validated?

No — and this section is deliberately cautious, matching the task's framing. What this pass supports:
a small, real (not synthetic) demonstration that (a) the preference contract works end-to-end against
the live OpenAI-backed route, (b) preference materially and traceably shapes real output in at least
some cases, (c) it can also partially misfire (tea-brand-exploration) in ways consistent with what the
prior synthetic research predicted (over-constraint, partial preference violation). What it does NOT
support: a general claim that personalization improves output quality, a statistically powered result
(n=3 pairs, one evaluator — this pass's own — no human/designer/client judgment), or a claim that the
specific failure modes seen here (gold-accent contradiction, compositional convergence) are
representative at scale. Call this a **small real validation**, not a benchmark, not proof, not a
validated personalization system.

## 16. What should be the next product iteration?

Future items only — none implemented in this pass:
- Direction-selection telemetry (log which of the 3 directions a user actually picks) — the cheapest
  real signal available today, requires no new input schema.
- A larger real paired sample (10+ pairs, matching the prior synthetic pass's scale) before any
  directional claim about personalization's real effect is treated as more than descriptive.
- A real human/designer/client preference judgment on at least a subset of real pairs, replacing this
  pass's own evaluator-assigned scores.
- Persistent preference memory / saved-inspiration ingestion, structured per the prior research pass's
  `preference_profiles.jsonl` schema (evidence[] + structured_preference), prioritizing
  feedback/rejection-derived evidence over stated-taste evidence per that pass's Finding 4.
- Trajectory SFT — remains explicitly future work; this pass adds one more layer of real, preference-
  bearing trajectories that could feed such a dataset later, but no model is trained here and none of
  today's 6 real runs is claimed as an SFT-ready candidate without a human judgment.
