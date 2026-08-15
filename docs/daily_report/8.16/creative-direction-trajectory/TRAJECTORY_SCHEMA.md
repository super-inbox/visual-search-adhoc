# TRAJECTORY_SCHEMA.md — Creative Direction Trajectories (baseline vs. personalized)

Research artifact. Extends, does not replace, the schema in
`docs/daily_report/8.12/visual-direction-trajectory-sft/TRAJECTORY_SCHEMA.md` (prior Task C pass).
That schema already defines the 10-stage vocabulary, the no-hidden-CoT constraint, and the
`workflow / trajectory / preference` three-data-type distinction — all reused here unchanged. This
document adds exactly what that schema was missing for the current experiment: a **personalization
axis** (baseline vs. personalized) and a **preference-profile input**, distinct from the prior
schema's `human_preference` field (which is a pairwise *comparison judgment*, not a standing
*preference profile* fed into generation). No training pipeline, backend, or frontend change is
implied.

## 1. What's new vs. the prior schema

The prior schema's `human_preference` field answers "given two outputs, which did a human prefer" —
a comparison recorded *after* generation. This experiment needs a different thing: a preference
**input** fed *into* generation, so a baseline and a personalized trajectory for the *same* brief can
be compared. Two fields are added at the trajectory top level to support this:

- `personalization_mode`: `"baseline"` or `"personalized"` — which arm of the paired experiment this
  trajectory belongs to.
- `preference_profile_id`: the `profile_id` from `preference_profiles.jsonl` used as input, or `null`
  for baseline trajectories.

And one field is added to record how the trajectory was produced, since this experiment mixes real
product output with synthetic construction (see `README.md` §Execution methodology):

- `execution_source`: `"real_current_agent"` | `"synthetic_experiment"` — see §3. (Corrected
  2026-08-16: this enum was originally `"real_agent_replay" | "synthetic_experiment"`; renamed to
  `real_current_agent` when 3 trajectories were corrected onto it, to name what it actually is — a
  real response from the *current* implementation — rather than a generic "replay" that could be
  confused with a replayed/simulated run.)

**Added 2026-08-16, alongside the correction (Phase 8 schema extension), for `real_current_agent`
trajectories only — `null`/absent on synthetic ones:**
- `capture_method`: `"live_this_pass"` | `"archived_prior_validation_run"` — whether the real output
  was captured by this pass executing the tool directly, or reused from an existing, already-archived
  real run of the same (unchanged-since) code. All 3 current real trajectories are
  `archived_prior_validation_run` (see `README.md` "Real-execution safety decision").
- `implementation_version`: `{worktree, branch, commit}` — exactly which checkout/commit produced
  this output, since the tool lives in a worktree distinct from this repo.
- `source_reference`: path to the archived raw response file this trajectory was verified against.
- `real_execution_captured_at_utc`: when the real call was actually made (not when this trajectory
  record was written).

Everything else below is a light adaptation of the prior schema's `steps` stage vocabulary, with one
new conditional stage (`preference_injection`) inserted between `reference_analysis` and
`direction_generation` for personalized trajectories only.

## 2. Design constraint: no hidden chain-of-thought (unchanged)

Same constraint as the prior schema. Every field is something a person could point to in the
transcript and check — `decision` and `evaluation` are one to two short, structured, observable
sentences, never an unrestricted internal reasoning trace. Nothing in this dataset was obtained by
attempting to recover a model's private reasoning; observable/reproducible fields only.

## 3. `execution_source`: corrected audit trail (2026-08-16, corrected same day)

**This section was rewritten after a same-day correction. See `README.md` "Audit correction" for the
full account; summarized here for the schema's own audit trail.**

A same-day-earlier version of this document claimed no "Brand Direction Explorer" tool existed
anywhere and that all 20 trajectories were `execution_source: "synthetic_experiment"`. **That claim
was wrong.** The real tool exists at `lib/brand_direction_explorer.ts`, `lib/brandDirectionOpenAI.ts`,
and `app/api/brand-direction-explorer/directions/route.ts`, in a separate git worktree
(`curify-frontend-brand-direction-explorer`, branch `baobao/brand-direction-explorer-tool-demo-2026-08-04`,
commit `322cd51f`) that the search behind the earlier claim never checked — it only searched
`curify-frontend` (a different worktree, different branch) and `curify-studio`.

That worktree also contains a real, dated validation report,
`docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/`, with 3 archived real runs
(`01-morrow-coffee`, `02-shanlan-tea`, `03-afterglow-market`) against the actual local dev server —
`input.txt`, `notes.txt`, `stage1-directions.json` (raw response body), and screenshots per case.

**Three-state correction history for `traj-001-baseline` / `traj-002-baseline` /
`traj-003-baseline`:**
1. An earlier background process on this branch labeled these three `execution_source:
   "real_agent_replay"`, citing the path above.
2. A same-day-earlier pass on this dataset, unable to find that path (because it never checked the
   right worktree), concluded step 1 was fabricated and relabeled all three `synthetic_experiment`,
   paraphrasing/trimming the `promptModifier` text in the process.
3. **This correction:** the path in step 1 is real. Each of the three trajectories'
   `creative_directions` was verified programmatically, field-for-field, against the corresponding
   `stage1-directions.json` — `id`/`title`/`subtitle`/`description`/`styleTags` matched exactly; only
   `promptModifier` had been altered by step 2's paraphrase, and has been restored to the byte-exact
   archived text. All three are now `execution_source: "real_current_agent"`.

`execution_source` values used in the current dataset:
- **`real_current_agent`** (3 records: `traj-001/002/003-baseline`): a real, verbatim response from
  the current real Brand Direction Explorer implementation. Always paired with `capture_method` (see
  §1 below) stating how it was captured.
- **`synthetic_experiment`** (17 records: all 10 personalized trajectories, plus the other 7
  baselines): hand-authored to a plausible, self-consistent JSON response shape — exactly 3
  directions each with `id`/`title`/`subtitle`/`description`/`styleTags`/`promptModifier`, bilingual
  `en`/`zh` text fields — a shape chosen to match the real tool's actual documented output shape (see
  §1), not because it was observed from a real system for these specific cases. The 10 personalized
  trajectories are synthetic **because the real tool has no preference input field to send them
  through**, not because no tool exists at all — a distinct and more specific blocker than the
  earlier (wrong) "no tool exists" framing implied.

Where a trajectory's underlying **brief** is real (see `creative_direction_questions.jsonl`
`source_type: "project_derived_case_study"` or the corrected `real_current_agent_brief`), the brief
being real does not by itself make the *directions* real — only the 3 `real_current_agent` records
above have real directions; every other trajectory's directions remain hand-authored even when its
brief is real or real-derived.

## 4. Top-level schema

```json
{
  "trajectory_id": "string, unique, e.g. 'trj-bd-001-baseline'",
  "query_id": "string, references creative_direction_questions.jsonl id",
  "domain": "enum: merch | packaging | ecommerce | edtech | brand_design",
  "topic": "string, matches the question's topic field",
  "personalization_mode": "enum: baseline | personalized",
  "preference_profile_id": "string, references preference_profiles.jsonl profile_id, or null for baseline",
  "execution_source": "enum: real_current_agent | synthetic_experiment — 3 of 20 trajectories in the current dataset (all baselines) are real_current_agent; the other 17 are synthetic_experiment (see §3)",
  "capture_method": "enum or absent, real_current_agent trajectories only: live_this_pass | archived_prior_validation_run — see §1",
  "implementation_version": "object or absent, real_current_agent trajectories only: {worktree, branch, commit} identifying exactly which build produced this output — see §1",
  "source_reference": "string or absent, real_current_agent trajectories only: path to the archived raw response this trajectory was verified against — see §1",
  "real_execution_captured_at_utc": "string or absent, real_current_agent trajectories only: when the real call was actually made — see §1",
  "user_input": {
    "brief_text": "string, the brief actually sent (matches the question's task_context/query)",
    "constraints": ["string, from the question's constraints field"],
    "input_images": ["string, path or id — empty in every trajectory in this dataset; the real tool has no reference-image input to exercise (see README.md 'Preference support')"]
  },
  "preference_input": "object or null — the full preference_profiles.jsonl record injected for this trajectory, verbatim; null for baseline, and never real (the real tool has no preference input field, so this is always a synthetic hypothesis when non-null)",
  "reference_inputs": ["array — always empty in this dataset; the real tool has no reference-retrieval or reference-upload path (confirmed by code inspection, see README.md 'Preference support')"],
  "harness": {
    "available_tools": ["string — tool/capability names this trajectory assumes are available; for real_current_agent trajectories, the real chain (POST /api/brand-direction-explorer/directions -> generateCreativeDirections() -> openai.chat.completions.create); for synthetic trajectories, a single hypothetical 'direction_generation' call plus reasoning-only stages with tool=null, per the prior schema's convention"],
    "environment_notes": "string or null"
  },
  "steps": ["array of Step objects, see section 5"],
  "creative_directions": ["array — exactly 3 GeneratedCreativeDirection-shaped objects (id, title{en,zh}, subtitle{en,zh}, description{en,zh}, styleTags[], promptModifier). For the 3 real_current_agent trajectories, this is the byte-exact real response body. For synthetic trajectories, a plausible hand-authored shape matching the real tool's actual documented output shape (see README.md 'Audit correction'), not one observed for that specific case."],
  "final_answer": {
    "asset_refs": ["string or null — null/placeholder throughout in this dataset (Stage 2 image generation was not captured by any trajectory here, real or synthetic); retained for a future trajectory that captures Stage 2 too"],
    "rationale": "string, short observable summary of the selected/returned direction set",
    "brief_alignment_summary": "string, short statement of how the output maps back to the brief"
  },
  "execution_status": "enum: success | partial_success | failure",
  "error": "string or null",
  "evaluator_results": "object or null — set post-hoc from paired_evaluation.csv; see EVALUATION_RUBRIC.md",
  "preferred_output": "string or null — trajectory_id of the paired trajectory judged better, filled in by paired_evaluation.csv, not by this file",
  "selection_reason": "string or null — short observable reason, filled in alongside preferred_output",
  "sft_candidate_status": "enum or null: strong_positive | usable_positive | generic_redundant | preference_misaligned | brief_conflict | insufficiently_actionable | execution_failure | needs_human_review",
  "notes": "string"
}
```

## 5. Step object

Reuses the prior schema's Step object fields (`step_id`, `stage`, `state_summary`, `decision`,
`action`, `tool`, `tool_input`, `observation`, `intermediate_output`, `evaluation`, `critique`,
`selected_candidate`, `rejected_candidates`, `revision_reason`, `user_feedback`, `preference`)
unchanged, plus one new stage:

| # | Stage | Condition | What happens |
|---|---|---|---|
| — | `brief_understanding` | always | Same as prior schema. |
| — | `reference_analysis` | if applicable | Same as prior schema; no trajectory in this dataset actually exercises reference-image input (see §3), so this stage is unused here but retained in the vocabulary for future real trajectories that do. |
| **new** | `preference_injection` | `personalization_mode == "personalized"` only | The preference profile's `structured_visual_preference` and relevant `evidence` entries are summarized into a short, observable instruction added to the generation input — analogous to how `reference_analysis` summarizes references into a visual system. This step's `observation` states exactly which preference fields were injected, so the personalized trajectory's downstream steps can be checked against a concrete, logged input rather than an implicit one. |
| — | `direction_generation` | always | For the 3 `real_current_agent` trajectories, this stage's `observation` is the literal recorded response (see §3). For the 17 `synthetic_experiment` trajectories, hand-authored to a plausible 3-direction JSON shape. |
| — | `direction_evaluation`, `selection`, `critique`, `revision`, `generation`, `client_feedback`, `final_output` | as in prior schema | Unchanged in shape; conditional stages remain conditional. |

One additional per-step field, defined for future use:

- `reconstructed`: `true` or absent. Intended for a trajectory that mixes a real recorded output with
  narrated steps around it (e.g. a real `direction_generation` response with a hand-narrated
  `brief_understanding` step, if the real product logs the former but not the latter). Not populated
  by any trajectory in the current dataset: the actual `trajectory_cases.jsonl` records use a flatter
  `tool_calls`/`tool_results`/`creative_directions` shape rather than the full `steps[]` Step-object
  array described in §4/§5 above — that granular per-step schema is defined here for future use but is
  not yet what this pass's data actually populates, real or synthetic. This is a pre-existing gap in
  this document vs. the actual data files, not something introduced or fixed by the 2026-08-16
  correction, and is noted here rather than silently left implicit.

## 6. Why `preference_injection` is its own stage, not folded into `reference_analysis`

The prior schema's `reference_analysis` stage summarizes *reference images* into a fixed/variable/
residue split. A preference profile is a different kind of input — a standing set of likes/dislikes
and structured dimensions, not a set of images to analyze — and, per this task's C2/C3 questions, is
exactly the thing whose effect this experiment needs to isolate. Keeping it a separate, clearly logged
step makes it possible to check directly whether a personalized trajectory's later steps
(`direction_generation`'s candidate spread, `direction_evaluation`'s stated reasoning) actually
reference what `preference_injection` logged, or whether the preference input was logged but had no
observable effect downstream — one of this experiment's core failure modes to detect (`FINDINGS.md`
§Preference, "does almost nothing").

## 7. Training-target note (unchanged from prior schema)

Per the prior schema's §4, any future trajectory-SFT training on this data should target
`state + tools + history → next action/tool/arguments/concise decision`, never unrestricted reasoning
traces. This experiment does not train anything; it only captures and evaluates trajectories against
that eventual target shape, and classifies which are plausible future training candidates
(`FINDINGS.md` §Trajectory, `sft_candidate_status` field above).
