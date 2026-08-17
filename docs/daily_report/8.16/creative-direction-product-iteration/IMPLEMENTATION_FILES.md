# IMPLEMENTATION_FILES.md

Documents the 7 frontend files affected by this Task C product iteration, on
`curify-frontend-brand-direction-explorer` (branch `baobao/brand-direction-explorer-tool-demo-2026-08-04`,
base commit `322cd51f`). **This change exists only as an uncommitted, unpushed local diff in that
worktree** — see `IMPLEMENTATION_PATCH.diff` in this same directory for the full, reproducible patch
(verified to apply cleanly against a clean checkout of `322cd51f`). Repository policy: the frontend
worktree is a local implementation/validation environment only; the patch archived here, not the
frontend git history, is the official record of this change.

## The 7 files

| # | File | Type | What changed |
|---|---|---|---|
| 1 | `lib/brand_direction_explorer.ts` | modified | Added `PreferenceProfile` type, `MAX_PREFERENCE_FIELD_LEN` (400), and `normalizePreferenceProfile()` — a pure function that trims/collapses whitespace and caps length the same way an existing brief field is normalized, returning `undefined` when both `likes`/`dislikes` end up empty. |
| 2 | `lib/brandDirectionOpenAI.ts` | modified | `generateCreativeDirections()` gained an optional third parameter (`preferenceProfile?`). New `buildPreferenceSection()` renders a `VISUAL PREFERENCE` block, only when non-empty. `buildUserMessage()` appends it. `SYSTEM_PROMPT` gained preference-handling rules (brief priority, material influence, diversity preservation, no-imitation) and a title-distinctness rule. `parseAndValidateDirections()` gained a case-insensitive duplicate-`title.en` check. |
| 3 | `app/api/brand-direction-explorer/directions/route.ts` | modified | Accepts an optional `preferenceProfile` field; new `validatePreferenceProfile()` strictly rejects non-object values, unsupported keys, non-string values, and over-length values (400) before calling `generateCreativeDirections`. |
| 4 | `app/[locale]/(public)/brand-direction-explorer/BrandDirectionExplorerClient.tsx` | modified | New `preferenceLikes`/`preferenceDislikes` state, a `preferenceProfile` memo, a "Visual preference (optional)" UI section (Prefer/Avoid textareas, EN/ZH copy), threaded into the existing debounced direction-fetch flow. |
| 5 | `lib/__tests__/brand_direction_explorer.test.ts` | modified | +7 tests for `normalizePreferenceProfile` (undefined/non-object input, whitespace-only, trimming, likes-only/dislikes-only, length cap, non-string values). |
| 6 | `lib/__tests__/brandDirectionOpenAI.test.ts` | modified | +10 tests: duplicate-title rejection (direct + case-insensitive + retry-then-succeed), and preference-in-prompt coverage (likes-only, dislikes-only, both, whitespace-only→no section, malformed type→no throw, baseline→no section). |
| 7 | `lib/__tests__/brand_direction_explorer_route.test.ts` | **new file** | 10 tests for the route's request-shape validation: baseline backward compatibility, likes-only/dislikes-only/both accepted and threaded through, empty object accepted, non-object/unsupported-key/non-string/over-length rejected with 400, response shape unchanged. |

## preferenceProfile contract

```json
{
  "caseId": "coffee-opening",
  "fieldValues": { "...": "..." },
  "preferenceProfile": { "likes": "...", "dislikes": "..." }
}
```

- Fully optional — omitting it reproduces the pre-existing request/response exactly (verified: the
  assembled OpenAI user message is byte-identical to before this change when no preference is sent).
- Both `likes` and `dislikes` are optional strings, each capped at 400 characters
  (`MAX_PREFERENCE_FIELD_LEN`).
- The route rejects (400, before calling OpenAI) anything that isn't a plain object, any key other
  than `likes`/`dislikes`, non-string values, or over-length values — it does not silently accept
  arbitrary nested objects.
- Content normalization (whitespace collapse, trim, empty→undefined) happens in
  `normalizePreferenceProfile`, called from `generateCreativeDirections` after the route's shape
  check has already passed.

## Prefer/Avoid UI

A new "Visual preference (optional)" section renders below the existing brief-field inputs and above
the direction cards: two textareas (`Prefer` / `Avoid`), each mirroring the existing field styling and
character-count pattern, with EN/ZH copy following the component's existing locale convention. Editing
either textarea invalidates the current direction set and re-triggers the same 600ms-debounced fetch
the brief fields already use. Preference text is intentionally **not** cleared on scenario switch
(unlike brief fields) since it describes user taste, not a case-specific fact. The section is clearly
optional — helper text states "Optional — tell Curify what visual qualities you prefer or want to
avoid" — and the tool remains fully usable with both fields blank (this is the pre-existing baseline
path, unchanged).

## API validation

`validatePreferenceProfile()` in `route.ts` runs after the existing `validateFieldValues()` check and
before calling `generateCreativeDirections`:
- `preferenceProfile === undefined` → passes (no preference case).
- Not a plain object (string, array, number, null) → 400.
- Any key besides `likes`/`dislikes` → 400 (rejects arbitrary nested objects, e.g. a hypothetical
  `referenceImages` field).
- `likes`/`dislikes` present but not a string → 400.
- `likes`/`dislikes` longer than 400 chars → 400.
- An empty object `{}` is accepted at the route layer (shape-valid) and normalized to "no preference"
  downstream by `normalizePreferenceProfile`, rather than being rejected — this keeps the route's
  validation purely structural and pushes the "is this actually empty" judgment to one place.

## OpenAI prompt integration

`buildUserMessage(brandCase, brief, preferenceProfile)` appends a `VISUAL PREFERENCE` section only
when `preferenceProfile` is non-empty after normalization — otherwise the message is unchanged from
before this feature existed. `SYSTEM_PROMPT` carries the interpretation rules the model must follow:
brief requirements always outrank preference; preference should meaningfully shape at least one
concrete visual decision (typography, composition, palette, imagery, materials, density, cultural
references) rather than being restated verbatim; preference must be applied differently across the 3
directions so they stay distinct; and preference is stylistic guidance only, never a request to
imitate a named artist, studio, or brand. Confirmed with real (not synthetic) execution — see
`real_paired_runs.jsonl` and `FINDINGS.md` items 4 and 10 for concrete traced examples (e.g.
"editorial typography" → a real compositional shift from product-photo-led to typography-led
directions in the `coffee-opening` case).

## Brief-integrity safeguard

Unchanged pre-existing mechanism (`normalizeAndValidateFields` still throws on any missing/blank
required brief field regardless of preference) plus one new prompt-level rule stating explicitly that
the project brief's requirements always take priority over preference. No new code-level enforcement
was added beyond the existing field-validation path — this is intentionally prompt-only per the
task's "no expensive multi-agent review system" scope constraint. Real evidence: `brief_integrity`
scored 4–5/5 across all 3 real personalized pairs (`real_paired_evaluation.csv`).

## Diversity safeguard

A new prompt-level rule instructing the model to apply preference differently across the 3 directions
rather than collapsing them into one preferred look, layered on top of the pre-existing diversity
rule. Also prompt-only, no deterministic gate. Real evidence is mixed and disclosed honestly: 2 of 3
real pairs preserved good diversity; 1 pair (`tea-brand-exploration`) showed a real, observed
diversity reduction (all 3 personalized directions converged on the same "hero shot + palette swatch
strip" composition) — see `FINDINGS.md` items 6 and 13 for the full account, including why this is
evidence the prompt-only approach is necessary but not sufficient.

## Duplicate-title validation

`parseAndValidateDirections()` now checks all 3 `title.en` values for case-insensitive, trimmed
distinctness after the existing per-direction field checks. A collision returns
`{ ok: false, reason: "duplicate_direction_title_..." }`, which the existing retry loop in
`generateCreativeDirections` (up to `MAX_ATTEMPTS = 3`) already re-requests on — no new retry
mechanism was built; this reuses the exact same path that already handles malformed JSON or a wrong
direction count. This is a direct fix for a real, previously-documented quality gap: a real captured
`coffee-opening` run (2026-08-06/07, predating this pass) where all 3 directions shared the title
"Morrow Coffee." None of this pass's own 6 real captured runs reproduced that specific failure, so the
gate's retry path was not exercised in real execution this pass — it is covered directly by 3 unit
tests instead (direct duplicate, case-insensitive duplicate, retry-then-succeed).

## Test coverage

- 27 new/updated tests specific to this feature: 7 in `brand_direction_explorer.test.ts`, 10 in
  `brandDirectionOpenAI.test.ts`, 10 in the new `brand_direction_explorer_route.test.ts`.
- All 54 pre-existing brand-direction-explorer tests pass unchanged.
- **277 / 277 tests passing repo-wide** (`npx vitest run --config vitest.unit.config.ts`), confirming
  no regression outside the touched feature.
- TypeScript: `tsc --noEmit` clean, 0 errors, repo-wide.
- Lint: blocked by a pre-existing `eslint`/`typescript-eslint` config-load error unrelated to these
  files (fails identically on any target in this repo) — documented, not fixed, since it is out of
  this task's scope.
