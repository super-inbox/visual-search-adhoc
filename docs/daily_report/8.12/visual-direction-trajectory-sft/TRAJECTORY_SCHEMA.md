# TRAJECTORY_SCHEMA.md — Curify Visual Direction / Creative Exploration

Research artifact. Defines a proposed (not implemented) data schema for future trajectory-SFT and
benchmark work. No training pipeline, backend, or frontend change is implied or included. Updated
in this incremental pass to incorporate the manager-provided trajectory-SFT discussion — see
`DISCUSSION_ANALYSIS.md` for the source-attributed analysis behind the additions in §1, §3.5, §4–5.

## 1. Three data types: workflow, trajectory, preference

The existing 8.8 workflow research (`curify-frontend-workflow-inspiration-2026-08-09/docs/daily_report/8.8/workflow-research-5-domains/`)
extracted **workflow data**: a professional's *stated process*, reconstructed as an ordered list of
named steps, each with an `input` / `action` / `output` and a source citation. See e.g.
`cases/brand_logo_001/workflow_extraction.json` — `step_04_creative_device`: input = personas,
action = "designed and applied a keyline-square treatment," output = "a repeatable visual device."
This is a **linear content pipeline**:

```
brief → concepts → design → final result
```

It records *what was produced at each stage*, not *how the agent decided, what alternatives it
considered, or how it judged its own output*. It has no branching, no rejected candidates, no
observation of intermediate output quality, and no record of revision triggers — because it's a
case-study reconstruction of a finished project, not a log of a decision process.

**Trajectory data** is a different object: a record of an *acting agent's* decision process over
time, structured so each step is independently observable and gradable.

```
state → decision → action/tool → observation → evaluation → next decision → revision → final output
```

The difference that matters for SFT: workflow data teaches "what a good creative process produces."
Trajectory data teaches "what a good agent does *next*, given the state so far" — including what it
does when its own output is weak, which is exactly the case workflow data (finished-project case
studies) structurally cannot contain, since failed/rejected paths are invisible in a published
case study.

`gc-minimal-zine-poster` (see `REPO_ANALYSIS.md`) sits in between: it's a *procedure specification*
(what stages should exist, what a fixed/variable/residue split looks like, what a quality gate
checks) but contains zero *executed* trajectories — no logs of an actual run. It's a source of stage
vocabulary and step I/O shape, not of trajectory examples.

**Preference / taste data** is a third, distinct object, per the manager-provided discussion (see
`DISCUSSION_ANALYSIS.md` §2–3): not a record of one agent's process, but a *comparison* between two
or more candidates or trajectories for the same task — e.g. "A > C", "D > B" — collected from a model
judge, a designer, a client, or observed user behavior. It answers "which output is better," not
"how did the agent get there." The schema's `human_preference` field (§4) and pairwise-example
guidance in `BENCHMARK_PROPOSAL.md` §4 are this data type; it is not interchangeable with trajectory
data, since a strong trajectory can still lose a pairwise comparison on subjective craft grounds that
the trajectory log itself never flagged as a defect.

## 2. Proposed trajectory stages for Curify Visual Direction / Creative Exploration

Derived from three inputs: (a) the workflow-stage vocabulary implicit across all five 8.8 domain
case studies (objective/brief → persona/audience → concept variants scored against criteria →
production → launch), (b) `gc-minimal-zine-poster`'s explicit stage list (parse content → choose
metaphor → select recipe → compile prompt → generate → inspect → regenerate-or-report-limitation),
and (c) the brief's requirement that at least one example show a weak direction being caught and
revised — which requires an explicit evaluation-before-selection step, not just a linear pipeline.

| # | Stage | What happens | Drawn from |
|---|---|---|---|
| 1 | `brief_understanding` | Parse the user's brief into an explicit target: subject, audience/mood, constraints, format. | 8.8 "define objectives" steps (all 5 domains); SKILL.md "Parse the content" |
| 2 | `reference_retrieval` | Select or receive reference material (user-supplied images, or retrieved inspiration) relevant to the brief. | Curify's existing inspiration/reference surfaces (topic mapping work, Task 1) |
| 3 | `reference_analysis` | Extract fixed system / variable system / sample residue from references, with observed-vs-inferred separation. | `references/reference-analysis.md` (A.2/A.3 in REPO_ANALYSIS.md) |
| 4 | `direction_generation` | Produce 2+ candidate visual directions, each a distinct combination on named axes (not cosmetic variants of one idea). | `references/variation-engine.md` anti-repetition rule; 8.8 "generate N concepts scored against named criteria" (packaging, brand_logo) |
| 5 | `direction_evaluation` | Score/critique each candidate against the brief on named, observable dimensions. | 8.8 "concepts scored against 3 named goals" (packaging_001); quality-gate.md checklist pattern |
| 6 | `selection` | Choose one direction (or shortlist), with an explicit, stated reason tied to the evaluation. | Inferred — no source has an executed selection log; this is the connective step evaluation data requires |
| 7 | `critique` *(conditional)* | If the selected/generated candidate has an observable mismatch vs. the brief, state what's wrong in checkable terms. | quality-gate.md "if a central check fails..."; brief's explicit weak-direction requirement |
| 8 | `revision` *(conditional)* | Regenerate or adjust, addressing the stated critique **or** stated client feedback (see stage 10a). Capped — do not loop indefinitely. | quality-gate.md's single-retry-then-report-limitation policy; manager-provided discussion's recovery-loop pattern (`DISCUSSION_ANALYSIS.md` §4) |
| 9 | `generation` | Produce the actual visual asset(s) for the selected (post-revision) direction. | All sources |
| 10a | `client_feedback` *(conditional)* | A human/client reviews a delivered artifact and gives feedback in their own words; the agent translates it into concrete, checkable design changes before any revision. | Manager-provided discussion's `BEFORE → HUMAN/CLIENT FEEDBACK → AFTER` pattern (`DISCUSSION_ANALYSIS.md` §3) — not present in either prior source |
| 10 | `final_output` | Return the asset plus a short, checkable rationale — not hidden reasoning. May follow `generation` directly, or follow a `client_feedback` → `revision` → `generation` loop. | quality-gate.md's returned "interpretation note" |

Stages 7–8 are conditional: a strong first direction may skip straight from `selection` to
`generation`. Stage 10a is also conditional and, when present, can trigger another pass through
`revision` (stage 8) and `generation` (stage 9) before reaching `final_output` — a trajectory's
`revision` stage may therefore recur, once triggered by self/model critique (stage 7) and again
triggered by client feedback (stage 10a), each capped independently rather than looping indefinitely.
This is why the schema below stores stage as a per-step field rather than assuming a fixed-length
trajectory — trajectories will vary in length and do not all touch every stage.

## 3. Design constraint: no hidden chain-of-thought

Every field below is something a person (or a judge model) could point to in a transcript and
check. `decision` and `critique` are **short, structured, observable rationales** — e.g. "selected
direction B: brief calls for 'energetic,' direction A scored low-saturation/high-negative-space" —
not an unrestricted internal reasoning trace. This mirrors `gc-minimal-zine-poster`'s own pattern:
its `quality-gate.md` produces checklist-style pass/fail statements, not free-form deliberation, and
its final output includes a "short interpretation note," not a reasoning transcript.

## 4. Training target

Per the manager-provided discussion (`DISCUSSION_ANALYSIS.md` §1), trajectory SFT on this schema
should primarily train:

```
state + tools + history → next action / tool / arguments / concise decision summary
```

not unrestricted reasoning traces. Concretely: the model of value is one that, given
`state_summary` (or `environment_state`, §5), `available_tools` (§5), and the prior `steps` array,
predicts the next step's `action`, `tool`, `tool_input`, and `decision` — where `decision` stays a
short, structured, observable rationale (§3), not a free-form deliberation transcript. This is the
same constraint §3 already states for `decision`/`critique`, restated here as the explicit shape of
the *training example*, not just the *logged field*. A trajectory-SFT dataset built from this schema
is therefore a set of `(state, tools, history) → next_action` pairs extracted from the `steps` array,
not a set of `(prompt) → full_reasoning_trace` pairs.

## 5. Top-level schema

```json
{
  "trajectory_id": "string, unique, e.g. 'vd-coffee-0001'",
  "task": "string, one-line task description",
  "domain": "enum: coffee_shop | brand_logo | poster | packaging | ecommerce | merch | education | other",
  "user_input": {
    "brief_text": "string, the user's original brief/request",
    "constraints": ["string, explicit constraints stated by the user, e.g. format, budget, must-include elements"],
    "input_images": ["string, path or id, optional — user-supplied photos/logos/products"]
  },
  "references": [
    {
      "ref_id": "string",
      "source": "string, e.g. 'user_upload' | 'curify_inspiration_topic:packaging' | 'external_url'",
      "role": "enum: style_reference | edit_target | supporting_insert"
    }
  ],
  "harness": {
    "available_tools": ["string, tool/capability names exposed to the agent for this trajectory, e.g. 'reference_analysis', 'direction_generation', 'generation'"],
    "environment_notes": "string or null, optional — UI/host/model-version context, if relevant to reproducing the trajectory"
  },
  "steps": ["array of Step objects, see section 6"],
  "final_output": {
    "asset_refs": ["string, path or id of final generated asset(s)"],
    "rationale": "string, short observable summary of why this is the final output",
    "brief_alignment_summary": "string, short statement of how the output maps back to the brief"
  },
  "outcome": "enum: success | partial_success | failure | revised_success",
  "quality_labels": {
    "brief_alignment": "1-5 or null",
    "direction_diversity": "1-5 or null",
    "visual_quality": "1-5 or null",
    "notes": "string, optional"
  },
  "human_preference": {
    "compared_to": "string, trajectory_id or null if not a pairwise judgment",
    "preferred": "boolean or null",
    "rater": "string, optional identifier"
  },
  "final_acceptance": "boolean or null — whether a human/client explicitly accepted the final_output (distinct from quality_labels, which are rater scores, not a client sign-off)",
  "failure_mode": "enum or null: none | weak_brief_parse | low_direction_diversity | selection_misaligned_to_brief | critique_missed_mismatch | revision_failed_to_fix | tool_error | other",
  "provenance": {
    "created_by": "enum: proposed_example | pilot_run | production_log",
    "created_at": "ISO 8601 date",
    "notes": "string, e.g. model/tool versions used, if a real run"
  }
}
```

`harness` and `final_acceptance` were added in this incremental update per the manager-provided
discussion (`DISCUSSION_ANALYSIS.md` §1, §3); both are optional/nullable, so trajectories authored
before this update (all four in `CURIFY_TRAJECTORY_EXAMPLES.jsonl` prior to this pass) remain valid
without retrofitting.

## 6. Step object

```json
{
  "step_id": "string, e.g. 'step_03'",
  "stage": "enum, one of the 10 stages in section 2",
  "state_summary": "string, short — what the agent knows going into this step",
  "decision": "string, short — what the agent decided to do next, and the observable reason",
  "action": "string, short verb phrase — what was actually done",
  "tool": "string or null — name of tool/capability invoked, e.g. 'image_generation', 'reference_search'",
  "tool_input": "object or null — structured input passed to the tool",
  "observation": "string — what came back / what was observed, factually",
  "intermediate_output": "string or null — path/id of any intermediate artifact produced this step",
  "evaluation": "string or null — observable check result, e.g. 'brief calls for warm/energetic; candidate uses cool desaturated palette — mismatch'",
  "critique": "string or null — specific, checkable issue statement, only present on critique steps",
  "selected_candidate": "string or null — id of the candidate chosen, only present on selection steps",
  "rejected_candidates": ["string, ids of candidates not chosen, with one-line reason each, only present on selection steps"],
  "revision_reason": "string or null — why a revision was triggered, references the triggering critique or client_feedback step_id, only present on revision steps",
  "user_feedback": "string or null — verbatim or lightly-summarized human/client feedback on a delivered artifact, only present on client_feedback steps",
  "preference": "object or null — pairwise preference judgment recorded at this step, e.g. {\"preferred\": \"candidate_A\", \"over\": \"candidate_B\", \"rater\": \"client\"}, only present when a comparative judgment (not a single-candidate evaluation) was made"
}
```

Field-level notes:
- Every field is a plain string/enum/object — no field is allowed to hold unrestricted
  chain-of-thought. `decision` and `evaluation` are one to two sentences, not paragraphs.
- `tool` / `tool_input` are null for steps that are pure reasoning-over-text (e.g.
  `brief_understanding`) and populated for steps that call an actual capability (e.g.
  `direction_generation` calling an image-generation tool, `reference_retrieval` calling a search
  tool).
- `state_summary` doubles as the per-step `environment_state` the manager-provided discussion's
  training-unit framing (§4) refers to — it is not a separate field, to avoid duplicating the same
  information under two names. Where a step's available tool set differs from the trajectory-level
  `harness.available_tools` (§5), that can be noted in `state_summary`; the schema does not duplicate
  a full tool list on every step.
- `user_feedback` and `preference` were added in this incremental update (`DISCUSSION_ANALYSIS.md`
  §3) and are optional — steps predating this update do not need to be retrofitted with these keys
  set to `null`; their absence is equivalent to `null`.
- Not every step has every field populated — most fields are step-type-conditional, kept optional
  rather than duplicated into stage-specific sub-schemas, to keep the schema small.

## 7. Abbreviated example

(Full worked examples are in `CURIFY_TRAJECTORY_EXAMPLES.jsonl`. This is a two-step excerpt to show
the shape.)

```json
{
  "trajectory_id": "vd-coffee-0001",
  "task": "Generate a visual direction for a new specialty coffee shop's Instagram launch post",
  "domain": "coffee_shop",
  "steps": [
    {
      "step_id": "step_01",
      "stage": "brief_understanding",
      "state_summary": "User brief: 'minimalist third-wave coffee shop, warm and calm, launch post for Instagram, square format.'",
      "decision": "Parse into target attributes: mood=warm+calm, style=minimalist, format=1:1 square, channel=Instagram launch.",
      "action": "Extracted structured brief target",
      "tool": null,
      "tool_input": null,
      "observation": "Brief has no explicit color or typography constraint; treat as open.",
      "intermediate_output": null,
      "evaluation": null,
      "critique": null,
      "selected_candidate": null,
      "rejected_candidates": null,
      "revision_reason": null
    },
    {
      "step_id": "step_04",
      "stage": "direction_evaluation",
      "state_summary": "Two candidate directions generated: A (warm neutral palette, hand-drawn mark, generous negative space), B (high-saturation duotone poster style, bold sans headline).",
      "decision": "Score both against brief target (warm+calm, minimalist).",
      "action": "Evaluated candidates against brief attributes",
      "tool": null,
      "tool_input": null,
      "observation": "A: warm neutral tones, generous whitespace — aligns with 'warm+calm+minimalist'. B: high-saturation duotone and bold headline read as energetic/loud, not calm.",
      "intermediate_output": null,
      "evaluation": "Candidate B mismatches brief on mood (loud vs. calm) and style (bold poster vs. minimalist); Candidate A aligns on both stated attributes.",
      "critique": null,
      "selected_candidate": null,
      "rejected_candidates": null,
      "revision_reason": null
    }
  ]
}
```

See `CURIFY_TRAJECTORY_EXAMPLES.jsonl` for complete trajectories, including one with a rejected
weak direction and a revision step.
