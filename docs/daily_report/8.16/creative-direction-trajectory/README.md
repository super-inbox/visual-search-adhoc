# Creative Direction / Human Preference / Trajectory SFT — Task C (2026-08-16)

## Purpose

Continues Task C: Creative Direction dataset expansion, a practical preference representation,
paired baseline-vs-personalized experiments, observable-trajectory capture, a multi-dimensional
evaluation rubric, and trajectory-SFT candidate classification for Curify's planned "Creative
Exploration" / "Brand Direction Explorer" capability. No model is trained in this pass. No
production code is modified.

## Relation to previous Task C research

Commits `3af4b57` and `2eac69d` on this branch (`docs/daily_report/8.12/visual-direction-trajectory-sft/`)
already did real work this pass builds on and does not repeat:
- A 10-stage trajectory vocabulary and the no-hidden-chain-of-thought constraint
  (`TRAJECTORY_SCHEMA.md` in that directory), reused unchanged here.
- A `workflow / trajectory / preference` three-data-type distinction.
- An analysis of an external GitHub skill package (`gc-minimal-zine-poster`) for transferable
  concepts — fixed/variable/residue reference classification, numeric checkable fixed-system
  fields, an anti-mode-collapse variation rule, a capped single-retry regeneration policy — see
  `REPO_ANALYSIS.md` in that directory. **Important:** that prior pass analyzed an *external* repo
  for inspiration; it did not audit Curify's own actual implementation. That audit is new work in
  this pass (see below).
- A benchmark proposal and manager discussion analysis incorporating boss feedback on client
  feedback loops and semantic robustness.

This pass adds: the `personalization_mode` / `preference_profile_id` / `preference_injection`
extensions to that schema (see `TRAJECTORY_SCHEMA.md` in *this* directory, §1), a concrete question
dataset, preference profiles, paired trajectories, an evaluation rubric, and paired evaluation
results — none of which existed before this pass.

## Audit correction (2026-08-16, same day): the Phase 0 audit below was wrong

**This section documents a correction made to this pass's own earlier work, later the same day.**
The original "Phase 0 audit" (preserved verbatim below, unmodified, for transparency) concluded that
no "Brand Direction Explorer" tool existed anywhere and, on that basis, downgraded three trajectories
that an even earlier background process had correctly labeled `real_agent_replay` to
`synthetic_experiment`, describing the earlier labeling as fabricated. **That downgrade was itself
wrong.** The tool exists; the earlier background process's `real_agent_replay` labeling was
essentially correct in substance (the recorded content is real); the Phase 0 audit's search simply
checked the wrong git checkout and never found it.

### Root cause

`curify-frontend` and `curify-frontend-brand-direction-explorer` are two separate **git worktrees of
the same underlying repository**, on two different branches:
- `curify-frontend` is checked out on `baobao/search-relevance-phrase-alias-2026-07-09` — unrelated
  search-relevance work; it has never had the Brand Direction Explorer branch checked out or merged
  into it, so a search inside it finds nothing.
- `curify-frontend-brand-direction-explorer` is checked out on
  `baobao/brand-direction-explorer-tool-demo-2026-08-04` (currently at commit `322cd51f`, in sync
  with `origin/baobao/brand-direction-explorer-tool-demo-2026-08-04` — this branch is pushed) and
  contains the full, real implementation.

The Phase 0 audit below searched only `curify-frontend` and `curify-studio` (per its own stated
scope) and never inspected `curify-frontend-brand-direction-explorer`, which sits in a sibling
directory and was not in that pass's search path. It is a real, separate worktree, not a hypothetical
or planned location — `git worktree list` from either checkout shows both, and the branch has three
commits (`e654570d`, `4d65adf8`, `322cd51f`) building and validating exactly this feature.

### The real implementation (verified by direct inspection, 2026-08-16)

| # | Item | Location |
|---|---|---|
| 1 | Frontend page | `app/[locale]/(public)/brand-direction-explorer/page.tsx` + `BrandDirectionExplorerClient.tsx` |
| 2 | Relevant components | `BrandDirectionExplorerClient.tsx` (single client component: case tabs, input fields, direction cards, prompt preview, generate/regenerate, result panel, FAQ) |
| 3 | API/backend route | `app/api/brand-direction-explorer/directions/route.ts` — `POST`, validates `{caseId, fieldValues}` against case metadata, calls the OpenAI module, returns `{success, directions}` or a sanitized error |
| 4 | Model/provider | Stage 1 (creative directions): OpenAI `gpt-4o-mini`, `temperature: 0.9`, `response_format: json_object`, via `lib/brandDirectionOpenAI.ts` (`import "server-only"`). Stage 2 (final image): unrelated, pre-existing, Gemini-backed (`services/useFreeformGenerate.ts` → `/nano-freeform/generate`, `google-genai`/`GEMINI_IMAGE_MODEL` via `curify-studio/curify_background`) — not touched by this feature |
| 5 | Request/input schema | `{ caseId: "coffee-opening" \| "tea-brand-exploration" \| "event-poster", fieldValues: Record<string,string> }` — fields are defined per case in `lib/brand_direction_explorer.ts` (`BrandDirectionCase.inputFields`), each with `id/label/placeholder/maxLength/required`; no separate validation schema, the route reuses this metadata |
| 6 | Response/output schema | `{ success: true, directions: GeneratedCreativeDirection[] }` — each direction: `id, title{en,zh}, subtitle{en,zh}, description{en,zh}, styleTags[], promptModifier` — or `{ success: false, error }` with a status mapped from a failure kind (`missing_api_key`→500, `invalid_input`→400, `rate_limited`→503, `timeout`→504, `upstream_error`→502) |
| 7 | Direction count/structure | Exactly 3 per request, enforced by `parseAndValidateDirections()` in `lib/brandDirectionOpenAI.ts` (rejects malformed JSON, wrong count, missing/invalid fields, duplicate ids; retries up to 3 attempts on invalid output) |
| 8 | Prompt/instruction construction | `SYSTEM_PROMPT` (inline constant, not a file) + `buildProjectBrief()`/`buildUserMessage()` in `lib/brand_direction_explorer.ts` / `lib/brandDirectionOpenAI.ts`; a separate `buildBrandDirectionPrompt()` builds the client-side Stage-2 image prompt (PROJECT BRIEF + USER-PROVIDED DATA + CREATIVE DIRECTION + OUTPUT FORMAT + OUTPUT CONSTRAINTS sections) |
| 9 | Scenario/preset definitions | Exactly 3 cases in `BRAND_DIRECTION_CASES` (`lib/brand_direction_explorer.ts`): `coffee-opening` (4 fields, 4:5 poster), `tea-brand-exploration` (5 fields, 3:4 moodboard), `event-poster` (5 fields, 4:5 poster). No other scenarios exist. |
| 10 | Downstream visual generation | User picks one of the 3 directions → `buildBrandDirectionPrompt()` builds the Stage-2 prompt client-side → `useFreeformGenerate()` (pre-existing hook, gated on login/credits, 10 credits/generation) → Gemini-backed backend → polled result URL |
| 11 | Preference support | **None.** See "Preference support" finding below. |
| 12 | Reference-image/reference-data support | **None** in Stage 1. Stage 2's `useFreeformGenerate` hook accepts an optional `referenceImageUrl` generically (used elsewhere in the app), but `BrandDirectionExplorerClient.tsx` never passes one — no UI affordance to upload or select a reference exists in this feature. |
| 13 | Examples/fixtures/tests | `lib/__tests__/brand_direction_explorer.test.ts` (33 tests, metadata/prompt-builder coverage), `lib/__tests__/brandDirectionOpenAI.test.ts` (21 tests, success/retry/rate-limit/timeout/missing-key coverage) — 54/54 passing per the report below. Real fixtures: `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/` (3 archived real end-to-end runs, see next section). |
| 14 | Current limitations | No preference/persona/reference input anywhere in the request or prompt; only 3 fixed scenarios (no generic/custom-brief case); repeated titles observed in one real run (all 3 Morrow Coffee directions shared `title.en`); Stage 2 direction-selection is not logged anywhere the app can read back (no telemetry linking "which of the 3 directions did the user pick"); no saved-inspiration or feedback capture of any kind. |

`lib/brand_direction_explorer.ts` module-level comment states explicitly: "No React, no browser APIs,
no env vars, no network... A `BrandDirectionCase` pins a fixed baseBrief... It intentionally carries
no creative-direction content of its own — those are generated per-request by the server." A unit
test (`lib/__tests__/brand_direction_explorer.test.ts`) is a regression guard specifically asserting
`BRAND_DIRECTION_CASES` never re-acquires static direction content ("never embeds hardcoded
creative-direction prose").

### Existing real validation report (already in that worktree, dated 2026-08-07 — predates this task)

`docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/` (in
`curify-frontend-brand-direction-explorer`) is a complete, real, end-to-end validation report the
branch's own author produced when building this feature: 3 real cases (`01-morrow-coffee`,
`02-shanlan-tea`, `03-afterglow-market`), each run against the actual local Next.js dev server
(`POST http://localhost:3000/api/brand-direction-explorer/directions`, not mocks), with
`input.txt` (exact submitted field values), `notes.txt` (verification notes, latency, quality
observations), `stage1-directions.json` (raw, real API response body), a UI screenshot, and two
Stage-2 final-image variants per case. 54/54 unit tests and `npm run build` also passed at that
commit. This report is the source for the `real_current_agent` trajectories in this pass — see
"Real-agent trajectory capture" below.

### Preference support (Phase 4 finding)

**Absent (option C: not implemented) — not partial, not present.** A case-insensitive search of
`app/api/brand-direction-explorer/`, `lib/brand_direction_explorer.ts`, `lib/brandDirectionOpenAI.ts`,
and `BrandDirectionExplorerClient.tsx` for `preference`, `persona`, `saved.?inspiration`,
`liked.?reference`, `disliked.?reference`, `reference.?image`, `prior.?selection`, `user.?profile`
returns **zero matches**. The request schema (`{caseId, fieldValues}`) and the OpenAI system prompt
(`SYSTEM_PROMPT` in `lib/brandDirectionOpenAI.ts`) have no field or instruction of any kind related
to a user's standing preferences, prior selections, liked/disliked references, or saved inspirations.
Every generation is a stateless function of `(caseId, fieldValues)` only. This is a direct code
finding, not an inference from product ideas.

### Real-execution safety decision (Phase 5)

Per the priority order (existing test/harness → existing dev route → existing API route with a
configured local environment → existing recorded real outputs), a fresh live run was technically
possible: `curify-frontend-brand-direction-explorer/.env.local` has an `OPENAI_API_KEY` configured
(existence confirmed; **value never read or printed by this pass**), and the dev route/API route both
exist and are unchanged since the 2026-08-07 report (`git log` on `lib/brandDirectionOpenAI.ts`,
`lib/brand_direction_explorer.ts`, and the API route shows no commits after `322cd51f`, the commit
that published that report). Given that, this pass made a deliberate choice: **reuse the existing
archived real outputs (Phase 5 tier 4) rather than spend new real OpenAI API cost** to reproduce
output that already exists, is verifiably real (see below), and was produced by the exact code still
at `HEAD` on that branch. This is not a fabrication shortcut — it is treated as the same class of
evidence a fresh run would be, with its actual capture date (2026-08-06/07) and source path recorded
explicitly (`capture_method: "archived_prior_validation_run"` on each such trajectory), not
back-dated or presented as captured today. No new OpenAI spend, no dev server, and no new browser
session were used by this pass.

### Real-agent trajectory capture (Phase 6)

The three real archived cases were byte-verified against this dataset's `traj-001-baseline`,
`traj-002-baseline`, `traj-003-baseline` (previously mislabeled `synthetic_experiment` by the Phase 0
audit, see above) using a small script comparing `creative_directions[]` field-for-field against each
case's `stage1-directions.json`. Result: `id`/`title`/`subtitle`/`description`/`styleTags` matched
exactly; `promptModifier` had been lightly paraphrased/trimmed by whichever process wrote the
"corrected" synthetic version — that field has been restored to the byte-exact archived text. All
three are now `execution_source: "real_current_agent"`, `capture_method:
"archived_prior_validation_run"`, with `source_reference` pointing at the exact archived file and
`implementation_version` recording the worktree/branch/commit. See `TRAJECTORY_SCHEMA.md` §3 for the
full corrected audit trail and `trajectory_cases.jsonl`'s `notes` field on each of the three records
for the complete correction chain (three states: `real_agent_replay` → wrongly `synthetic_experiment`
→ correctly `real_current_agent`).

Only 3 scenarios exist in the real tool (`coffee-opening`, `tea-brand-exploration`, `event-poster`),
so all 3 were used — there was no larger pool of real scenarios to sample 3–5 from. Each maps to one
of this dataset's `brand_design`-domain questions (`cdq-001`, `cdq-002`, `cdq-003`), whose `query`
text and `source_type` (`real_current_agent_brief`, corrected from `synthetic_experiment`) have also
been corrected to reflect that these are real submitted field values, not hand-authored fiction — see
`creative_direction_questions.jsonl`. No other domain (`merch`, `packaging`, `ecommerce`, `edtech`)
has a corresponding real scenario in the current tool; this is a real, current gap in tool coverage,
not a gap in this pass's sampling.

### Real preference A/B test (Phase 7): pending — not implementable today

The real tool has no preference/reference input field (see "Preference support" above), so no real
paired baseline-vs-personalized experiment can be run against it. `traj-001/002/003-personalized`
remain `synthetic_experiment` hypotheses. **Real preference A/B validation is pending because
preference is not yet implemented.** The smallest useful contract to make this possible is scoped
under Product recommendations (P0/P1) in `FINDINGS.md`.

---

## Original Phase 0 audit (2026-08-16, earlier same day — preserved for transparency, superseded by the correction above)

**This section is retained verbatim as a record of what was concluded and why it was wrong. Do not
treat any claim below as current — see "Audit correction" above.**

**Finding: no "Brand Direction Explorer" or "Creative Exploration" generation tool exists in
shipped code anywhere.** This was checked directly, not assumed:
- Broad case-insensitive search across `curify-frontend` (`app/`, `lib/`, `components/`) for
  "Brand Direction", "brandDirection", "Creative Exploration", "creativeExploration",
  "moodboard", "concept.direction" returns no implementation file, no API route, no prompt file, and
  no fixtures. `curify-frontend`'s actual shipped surface is a visual-search/topic-registry product
  (`app/[locale]/(public)/search`, `lib/topicRegistry_pure.ts`) plus a handful of demo API routes
  (`illustrator-demo`, `personality-poster`, `wc-bracket-poster`, `progseo-demo`,
  `search-template-match`) — none of which generate multi-direction creative concepts from a brief.
- The same search across `curify-studio` (narrow, read-only, per this task's scope limits) returns
  nothing either.
- No fixtures, example data, or `docs/daily_report/8.7/...` directory exists anywhere referencing a
  live run of such a tool.

**⚠️ This conclusion was wrong — the search never checked `curify-frontend-brand-direction-explorer`,
a separate worktree of the same repo. See "Audit correction" above.**

**Consequence for this pass (as understood at the time — since corrected):** per the task brief's
explicit fallback rule (§16: "if the current agent cannot safely be executed, document exactly why;
do NOT fabricate real runs"), every trajectory in `trajectory_cases.jsonl` was (at that time) marked
`execution_source: "synthetic_experiment"` — hand-authored to a plausible, self-consistent response
shape, never claimed as a real execution. See `TRAJECTORY_SCHEMA.md` §3 for the full audit trail,
including **a correction of a correction**: an earlier version of this pass's data (written before
this README, by a background process that briefly ran ahead of its actual scope) had labeled three
trajectories `real_agent_replay` with a source path this Phase 0 audit couldn't find and therefore
called fabricated. **That call was itself wrong — the path exists, just in a worktree this audit
didn't check** (see "Audit correction" above). It is recorded here, not silently rewritten, because
this task's explicit anti-fabrication requirement applies symmetrically: a false "doesn't exist"
claim is exactly as much a problem as a false "is real" claim, and both are corrected in the open.

**What real material does exist and is used honestly in this dataset:**
- `docs/daily_report/8.8/workflow-research-5-domains/candidates/*.md` in *this* repo: 18 real,
  previously-researched case-study files across all five domains (4 merch, 4 packaging, 4 ecommerce,
  3 edtech, 3 brand_design). This pass used 15 of the 18 to back `cdq-004`–`cdq-018`'s
  `source_type: "project_derived_case_study"` with corrected, verified `source_reference` paths.
  **3 files were not used and remain available for the next expansion pass:**
  `MERCH-04-darin-michau-mascot.md`, `PACK-04-danjiaoshi-process-overview.md`,
  `ECOM-04-zimu-aipl-report.md` — see `FINDINGS.md` §Dataset. A fourth, separately-published real
  case exists at `docs/daily_report/8.8/workflow-research-5-domains/cases/behance_constellation_rebrand/`
  (this is the source `BRAND-03-constellation-rebrand.md` in `candidates/` summarizes; not a
  distinct unused case). The *briefs* used here are real (normalized from real published case
  studies); the *generated directions* responding to them are still synthetic — the real Brand
  Direction Explorer tool (see "Audit correction" above) has no case matching these domains
  (merch/packaging/ecommerce/edtech), only `coffee-opening`/`tea-brand-exploration`/`event-poster`,
  so these particular briefs could not be run through it even after the correction.
- `docs/daily_report/8.14/inspiration-scale/` (Task A) exists and was inspected read-only for
  context; **not modified**, and not used as a direct source here since Task A's query set targets
  visual search/inspiration retrieval, not Creative Direction generation briefs — a related but
  different task shape.
- The `agentic-adhoc` repo's `design-agent-v0/eval/experiments/curify-web-live-2026-08-12/` contains
  a genuinely useful precedent: a 21-case **live evaluation of the deployed Curify Design Agent**
  (a different, already-shipped capability — image/asset generation, not Creative Direction) with a
  reusable rubric shape (`brief_adherence, visual_quality, creative_diversity, brand_consistency,
  refinement_ability, cross_asset_consistency, production_readiness, efficiency`) and a
  `required_normalized_stages: [UNDERSTAND, PLAN, GENERATE, VERIFY, PRESENT]` trajectory-stage
  vocabulary. `EVALUATION_RUBRIC.md` in this directory borrows the *shape* (weighted, named,
  multi-dimensional, no single scalar) but defines Creative-Direction-specific dimensions, since the
  design-agent-v0 rubric scores finished visual assets, not direction proposals. Not modified
  (read-only reference repo).
- `agentic-adhoc`'s `design-agent-v0/benchmarks/creative-exploration/` is a *different* sense of
  "creative exploration" (variant-ranking via simulated consumer panel, not multi-direction
  generation from a brief) — its `case.json` structure (brief → segments → votes → winner+rationale)
  informed this dataset's preference-evidence structuring but is not itself Creative Direction data.

## Directory structure

```
creative_direction_questions.jsonl   26 Creative Direction briefs across 5 domains
preference_profiles.jsonl            8 synthetic preference profiles
trajectory_cases.jsonl               20 trajectories (10 paired baseline/personalized cases;
                                      3 baselines are execution_source: real_current_agent)
paired_evaluation.csv                10-row rubric-scored comparison of each pair
TRAJECTORY_SCHEMA.md                 trajectory contract + audit trail
EVALUATION_RUBRIC.md                 8-dimension, 1-5 scale rubric with anchors
FINDINGS.md                          answers to the boss-level dataset/preference/eval/trajectory questions
DAILY_REPORT.md                      manager-readable summary with exact counts
gallery.html                         internal human-review artifact (badges real vs. synthetic per arm)
README.md                            this file
```

## Question dataset (`creative_direction_questions.jsonl`)

Schema: `id, domain, topic, query, source_type, source_reference, task_context, audience,
constraints, personalization_candidate, coverage_tags, notes`.

`source_type` values and what they mean (do not conflate — see `FINDINGS.md` §Dataset for how each
is used):
- `project_derived_case_study` (15 records, `cdq-004`–`cdq-018`): brief normalized from a real
  published case study researched in a prior pass (`docs/daily_report/8.8/workflow-research-5-domains/candidates/`,
  this repo). Real provenance, verified file paths.
- `real_current_agent_brief` (3 records, `cdq-001`–`cdq-003`): **corrected 2026-08-16 (second
  correction).** These reproduce, in single-paragraph query form, the exact field values a user
  submitted to the real Brand Direction Explorer's `coffee-opening`/`tea-brand-exploration`/
  `event-poster` cases, archived at `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/*/input.txt`
  in `curify-frontend-brand-direction-explorer`. They were briefly (mis)labeled `synthetic_experiment`
  by the Phase 0 audit above, which could not find that archive because it checked the wrong worktree.
- `synthetic_experiment` (8 records, `cdq-019`–`cdq-026`): hand-authored for this experiment, either
  to fill a coverage gap or stress-test a specific failure mode (ambiguity, over-constraint,
  brief-conflict, negative-preference). Never presented as a real user query.

15 of 26 questions are project-derived-case-study real, 3 of 26 are real-current-agent-brief real
(briefs only — the *directions* returned for these 3 are `real_current_agent` for the baseline arm
and still synthetic for the personalized arm, since the real tool has no preference input), and 8 of
26 are fully synthetic. This is stated explicitly rather than left implicit, since the task brief
treats "distinguish real from synthetic" as a load-bearing requirement.

## Coverage analysis

Domain breakdown (26 questions): `brand_design` 8, `merch` 5, `ecommerce` 5, `packaging` 4,
`edtech` 4. Reasonably even; `brand_design` is highest because it absorbed both the corrected
formerly-mislabeled cases and several ambiguity/negative-preference synthetic stress tests, not
because of deliberate domain weighting.

`personalization_candidate: true` on 12 of 26 questions — these are the pool the paired experiment
drew from (see below). The paired experiment covers 10 of these 12; `edtech` and `ecommerce` are
under-represented in the *paired* set specifically (1 case each vs. 2 for `merch`/`packaging`, 4 for
`brand_design`) even though the underlying question dataset covers those domains adequately — this
is a real, acknowledged coverage gap for the next pass, not a claim of balanced paired coverage.

Coverage tags span: poster/launch-campaign work, cultural/heritage identity, collectible/merch
product families, retail packaging (new-category and refresh), PDP/conversion imagery, cross-subject
educational visual systems, institutional/nonprofit/corporate identity, and — deliberately — five
stress-test categories: ambiguous/generic briefs, over-constraint risk, explicit negative preference,
brief-vs-preference conflict, and whose-preference-is-this conflicts. See `FINDINGS.md` §Dataset for
what's still missing.

## Preference representation (`preference_profiles.jsonl`)

Schema: `profile_id, data_type ("synthetic_experiment" on every record), archetype, evidence[]
(evidence_type + content), structured_preference (color/typography/illustration/photography/
layout_density/geometry/texture/cultural_references/tone), positive_references[],
negative_references[], notes`.

8 profiles spanning genuinely different territories (not "minimal premium" repeated 8 times):
restrained-editorial, maximalist-streetwear, heritage-craft, tech-startup-clean,
playful-youth-brand, luxury-minimal, sustainability-focused, and one built specifically from
`previous_client_feedback` + `rejected_concept` evidence rather than a stated-taste string (`pf-008`)
— included to test that evidence type specifically, per the task brief's saved-inspiration /
prior-feedback hypothesis.

**Saved-inspiration hypothesis** (task brief §14): treated here as a product hypothesis only, not an
approved feature. `pf-008`'s evidence shape (`previous_client_feedback` + `rejected_concept`,
producing a structured preference without a single stated-taste sentence) is the closest this
dataset comes to modeling what a "saved inspiration → persistent preference profile" pipeline would
need to produce as its output — see `FINDINGS.md` §Preference for what worked and didn't about that
evidence type specifically.

## Paired experiment

10 of the 12 `personalization_candidate: true` questions were run as baseline/personalized pairs
(20 trajectories total). Each pair holds the brief fixed and varies only the presence of a
preference-profile input, per the task brief's isolation requirement. Preference profiles were
chosen per case to cover: natural fit, deliberate mismatch, brief-conflict, negative-preference
overcorrection, and evidence-type variation (stated taste vs. feedback-derived) — see
`trajectory_cases.jsonl` `notes` field per case for the specific rationale, and `paired_evaluation.csv`
for the scored outcome.

## Execution methodology

**Corrected 2026-08-16.** 3 of 20 trajectories (`traj-001/002/003-baseline`) are
`execution_source: "real_current_agent"`, `capture_method: "archived_prior_validation_run"` — real,
verbatim OpenAI (`gpt-4o-mini`) responses captured 2026-08-06/07 against the actual real Brand
Direction Explorer's local dev server and archived in `curify-frontend-brand-direction-explorer`
(see "Audit correction" above). The remaining 17 trajectories (all 10 personalized trajectories, plus
the other 7 baselines) are `execution_source: "synthetic_experiment"`, hand-authored to a plausible,
checkable JSON response shape — either because no real tool scenario exists for that domain, or
(for all 10 personalized trajectories) because the real tool has no preference input to send. This is
disclosed at three levels: the trajectory-level `execution_source`/`capture_method` fields, the
per-tool-call `tool_calls[].tool` string, and a `real_note`/`synthetic_note` in `tool_results[]`. See
`TRAJECTORY_SCHEMA.md` §3 for the full, corrected audit trail.

## How to inspect the gallery

Open `gallery.html` directly in a browser (no server required — it's a static file with data
inlined). It supports filtering by domain, baseline/personalized, winner, preference profile, and
SFT candidate status, and shows each paired case's brief, both direction sets, rubric scores,
winner, and SFT classification side by side.

## How to rerun / extend

There is no generator script in this directory — an earlier background process's generator scripts
were found (during validation) to be inconsistent with the final dataset (a different ID scheme,
`cdq-bd-001` vs. the shipped `cdq-001`, from a race between two parallel background runs) and were
removed rather than fixed, since keeping a script that doesn't reproduce its own claimed output would
be more misleading than having none. To extend this dataset: add new records to
`creative_direction_questions.jsonl` / `preference_profiles.jsonl` following the schemas above,
author new trajectory pairs following `TRAJECTORY_SCHEMA.md`, score them per `EVALUATION_RUBRIC.md`,
and append rows to `paired_evaluation.csv`. The real Brand Direction Explorer tool now ships (see
"Audit correction" above) but only for 3 scenarios and with no preference input — new
`execution_source: "real_current_agent"` trajectories for those 3 scenarios (or fresh live runs of
them) should replace/supplement the corresponding synthetic ones, kept clearly labeled and separate
for comparison, exactly as `traj-001/002/003-baseline` now are.

## Known blockers before real trajectory-SFT data / real personalization evidence

1. **The real tool covers only 3 of this dataset's 5 domains, and only as fixed scenarios.**
   `coffee-opening`/`tea-brand-exploration`/`event-poster` exist and are now represented by real
   trajectories (3 of 20); `merch`, `packaging`, `ecommerce`, `edtech`, and any free-text/custom brief
   have no corresponding real scenario to execute against yet. Broader real trajectory-SFT data
   requires either more scenarios in the real tool or a generic/custom-brief case.
2. **No real preference-evidence pipeline exists** (no saved-inspiration capture, no like/dislike
   storage, no client-feedback ingestion, and — confirmed by direct code inspection — no preference
   field anywhere in the real tool's request schema or prompt). `preference_profiles.jsonl` models
   plausible evidence shapes but none of it is sourced from a real user, and none of it can be sent to
   the real tool today. This is the primary blocker for real personalization evidence specifically
   (distinct from blocker 1, which blocks real trajectory-SFT data more broadly).
3. **No human/evaluator judgments exist yet** — `paired_evaluation.csv` scores were assigned by this
   pass's evaluation process against the rubric, not by an external human rater or the actual target
   user (designer/client), even for the 3 pairs with a real baseline arm. See `FINDINGS.md` for what
   would change with real human judgments.
4. Sample size is small (10 paired cases, only 3 with a real arm) — findings in `FINDINGS.md` are
   directional, not statistically powered; treat percentages there as descriptive of this sample, not
   proof of a general effect.
