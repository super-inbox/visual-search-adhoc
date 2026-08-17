# BENCHMARK_PROPOSAL.md — Visual Direction / Creative Exploration

Research artifact. Proposes a benchmark design; does not implement scoring code, a harness, or a
labeled dataset. Builds on the stage vocabulary in `TRAJECTORY_SCHEMA.md` and the schema fields
each dimension below reads from. This is the **small internal pilot benchmark** described throughout
this document (§6) — see §8 for how it relates to the much larger, not-yet-built future Curify
Design Agent Benchmark the manager-provided discussion describes (`DISCUSSION_ANALYSIS.md` §9).
Updated in this incremental pass to add dimensions and a robustness section from that discussion —
see `DISCUSSION_ANALYSIS.md` §4–5.

## 0. Core position

Final-image quality alone cannot benchmark this task, for the same reason `gc-minimal-zine-poster`'s
own eval set (`evals/evals.json`, see `REPO_ANALYSIS.md` A.7) is written as behavioral rubrics, not
image scorers: a single output image cannot reveal whether the brief was actually understood,
whether real alternatives were considered, or whether a weak candidate was caught and fixed versus
never generated in the first place. A trajectory that skips evaluation and gets lucky on one
generation is indistinguishable from a rigorous one if only the final image is graded. The benchmark
therefore has three separate layers, scored separately and never collapsed into one number.

## 1. Three benchmark layers

### 1.1 Step-level evaluation
Grades individual `Step` objects (schema in `TRAJECTORY_SCHEMA.md` §5) in isolation: given the
`state_summary` going into a step, is the `decision`/`action`/`evaluation`/`critique` at that step
good, independent of what happens later in the trajectory.

### 1.2 Trajectory-level evaluation
Grades the *trajectory as a whole*: does the sequence of steps make sense as a coherent process —
did evaluation actually inform selection, did a critique actually get addressed by the following
revision, did direction_generation actually produce a diverse spread rather than cosmetic variants.
This is where the coffee-shop example's step_04→step_05→step_06→step_07 chain (evaluation → selection with
stated rejection → critique → capped revision) would be graded as a unit.

### 1.3 Final-output evaluation
Grades only the `final_output` object against the original `user_input.brief_text` — the layer
closest to "does the deliverable work," but treated as necessary, not sufficient.

## 2. Evaluation dimensions

For each dimension: what's evaluated, the observable evidence in the schema, a possible automated
metric or judge, when a human must review instead, and common failure modes (cross-referenced to
the `failure_mode` enum in `TRAJECTORY_SCHEMA.md` §4 where applicable).

| Dimension | Layer | What is evaluated | Observable evidence | Automated metric / judge | Human review needed when | Common failure modes |
|---|---|---|---|---|---|---|
| Brief understanding | Step | Did `brief_understanding` correctly extract the stated mood/constraints/format? | `state_summary`, `decision` fields of the brief_understanding step vs. `user_input.brief_text` | LLM-judge: given brief text + extracted attributes, flag omissions/hallucinated constraints | Ambiguous or culturally-loaded briefs where "correct" extraction is itself debatable | `weak_brief_parse` — misses explicit constraint or invents one not stated |
| Reference relevance | Step | Are retrieved/supplied references actually relevant to the brief's domain and mood? | `references[].role`, `reference_retrieval` step's `tool_input`/`observation` | Embedding similarity between brief text and reference metadata, as a weak pre-filter only | Any case near the similarity threshold, or when zero/one reference is returned (as in the packaging example) | Thin retrieval (packaging example, step_02) — logged as a limitation, not silently passed |
| Reference understanding | Step | Does `reference_analysis` correctly separate fixed / variable / residue, with observed vs. inferred labeled? | `reference_analysis` step's `observation`/`evaluation` vs. actual reference content | LLM-judge re-deriving fixed/variable split from the same reference and diffing | Always for the observed-vs-inferred distinction — this is a judgment call template alone cannot verify | Treating single-sample residue as a generalized fixed rule (the exact failure `references/reference-analysis.md` A.2 warns against) |
| Visual-system extraction | Step | Is the extracted visual system (`intermediate_output`) checkable and specific, not just adjectives? | `visual_system_*.json` intermediate outputs | Rule-based check: does the system include ≥1 numeric/enumerable field (not only free-text mood words)? | When the domain has no established numeric convention yet (new domain, first pilot) | Vague, unfalsifiable system descriptions ("modern," "clean") with no checkable field |
| Direction diversity | Step / Trajectory | Do generated candidates differ on real axes (layout, palette, construction logic), not just cosmetically? | `direction_generation` step's `observation` across candidates; count of distinct axes changed | Pairwise perceptual/structural distance between candidate images or between their recipe/axis tags | Always for final confirmation — distance metrics are a proxy, not ground truth for "meaningfully different" | `low_direction_diversity` — N candidates that are the same idea restyled |
| Direction-to-brief alignment | Step | Does each candidate's `evaluation` correctly identify match/mismatch against brief attributes? | `direction_evaluation` step's `observation`/`evaluation`/`critique` | LLM-judge given brief + candidate description, predict match/mismatch, compare to logged evaluation | Any mismatch verdict close to a subjective line (e.g. "loud" vs. "energetic") | `selection_misaligned_to_brief` — evaluation reasoning is present but selection contradicts it |
| Selection quality | Step | Is the chosen candidate actually the one the evaluation step supports, with rejected candidates given real reasons? | `selection` step's `selected_candidate` / `rejected_candidates` vs. prior `direction_evaluation` | Rule-based consistency check: does the selected candidate have the best evaluation outcome logged? | When two candidates are close enough that either choice is defensible | Selecting a candidate the evaluation step itself flagged as weaker, without stated justification |
| Critique correctness | Step | When a critique is raised, is it a real, checkable issue (not invented, not missed)? | `critique` step's `critique` field vs. independent inspection of the flagged asset | LLM-judge or rule-based check (e.g. actual thumbnail-scale legibility test, actual dimension check) reproducing the claimed defect | Any critique based on subjective quality rather than a checkable defect | `critique_missed_mismatch` — a real defect exists but no critique step catches it |
| Revision effectiveness | Step / Trajectory | Did the revision fix the specific issue the critique raised, without introducing a new one, and without looping indefinitely? | `revision` step's `revision_reason` vs. the prior `critique`; step count of revision loop | Rule-based: re-run the same defect check that triggered the critique against the revised asset | Always for "no new issue introduced" — that requires holistic re-inspection | `revision_failed_to_fix` — revised but the flagged issue persists; also flag any revision loop exceeding one retry as a process violation, per the quality-gate.md single-retry precedent in `REPO_ANALYSIS.md` |
| Tool/action efficiency | Trajectory | Are tool calls purposeful — no redundant retrieval/generation calls, no skipped step that later causes rework? | Count and sequence of `tool`/`action` fields across `steps` | Rule-based: flag repeated identical `tool_input` calls, or a `revision` step with no preceding `critique` | When an apparently redundant call is actually a deliberate diversity-generation choice (e.g. intentionally regenerating for spread, not fixing an error) | `tool_error`; also "phantom revision" (regenerating without a stated reason) |
| Final visual quality | Final-output | Does the final asset look professionally acceptable on domain-appropriate craft criteria (composition, legibility, production-readiness)? | `final_output.asset_refs`, rendered at both full size and thumbnail scale | Domain-specific automated checks only for the checkable subset (dimension/aspect-ratio compliance, text legibility/OCR-based contrast check, color-area measurement) | Always for anything beyond the checkable subset — aesthetic craft judgment is not reducible to a scalar, consistent with `REPO_ANALYSIS.md` C's caution against over-copying this repo's numeric fixed-system as if numbers alone equal quality | Passes all checkable criteria but still reads as generic/low-craft to a human reviewer |
| **Recovery rate / quality** | Trajectory | Given a detected problem (`critique` or `client_feedback` step), did the agent correctly diagnose it, change the right tool/prompt/parameter, and re-verify — as its own named metric, distinct from whether the revision's *content* happened to work | `critique`/`client_feedback` step → following `revision` step's `revision_reason` → that revision's `evaluation` confirming re-check | Rule-based: does every `critique`/`client_feedback` step have a following `revision` step with a stated `revision_reason`, and does that step's `evaluation` field show a re-verification, not just a restated intent | When the recovery took a defensibly different path than the critique literally named | `revision_failed_to_fix`; also "no recovery attempted" — a critique or client_feedback step exists with no following revision step |
| **Tool-call correctness** | Step | Was the tool selected, and its arguments, actually appropriate for the state at that step — not merely "did a tool call execute without erroring" | `tool` / `tool_input` vs. `state_summary` at that step | Rule-based: `tool_input` schema/argument validation; LLM-judge: given state + `harness.available_tools`, would this tool/argument choice be a reasonable expert choice | When multiple tools are defensibly correct for the same state | `tool_error`; also silent misuse — tool executes successfully but is the wrong tool for the state |
| **Turns to completion** | Trajectory | How many steps did the trajectory take to reach `final_output`, given the task's actual difficulty | count of the `steps` array; count of `revision` recurrences | Rule-based: raw step count plus revision-loop count | When comparing across tasks of different inherent difficulty — raw counts are not comparable across domains without a difficulty baseline | unexplained extra turns with no stated `decision`/`revision_reason` justifying them |
| **Cost / efficiency** | Trajectory | Compute/generation cost incurred to reach `final_output` | count and type of `tool` calls across `steps`, each generation-type call carrying an associated cost | Rule-based: sum of tool calls by type against a per-tool cost table maintained outside this schema | Cost tables need periodic human update as tool/model pricing changes — never treat a stale table as ground truth | redundant generation calls that inflate cost without adding diversity or fixing a stated defect |
| **Human preference** | Final-output | Given two trajectories, or two final candidates within one trajectory, for the same brief, which does a human prefer | `human_preference` field (`TRAJECTORY_SCHEMA.md` §5) | Not automatable as ground truth; an LLM-judge proxy may be trained against accumulated `human_preference` labels but is never itself treated as ground truth | Always — this dimension is definitionally human-sourced by construction | none dedicated — this dimension exists to catch what the other, more checkable dimensions miss |
| **Cross-asset consistency** | Trajectory / Final-output | When a trajectory (or a family of related trajectories) expands one selected direction into multiple assets — e.g. packaging + poster + sticker — do the assets share the same fixed-system traits rather than drifting per-asset | Multiple `final_output` entries traceable to the same upstream `selected_candidate` / visual-system reference | Rule-based: do the fixed-system fields (palette, wordmark, motif) match across asset outputs generated from the same selection | Always for the subjective "reads as one identity system" judgment, beyond the checkable fixed fields | asset-family drift — each asset individually passes brief-alignment but the set doesn't read as one brand |
| **Production readiness** | Final-output | Is the deliverable actually usable in its stated production context (print-safe line weights, exact required dimensions, required content present) — not just visually appropriate | Domain-specific hard constraints already in `user_input.constraints`, checked at generation (e.g. `vd-brandlogo-0001`'s press-safe check, `vd-packaging-0001`'s 3in x 4in check) | Rule-based: constraint-specific automated checks, one per domain's known hard constraints | When a domain's production constraints aren't yet codified (new domain, first pilot) | passing brief-alignment/mood checks while still failing a hard production constraint |

Recovery rate/quality and cross-asset consistency were absent from the original dimension table;
tool-call correctness, turns to completion, cost, human preference, and production readiness
sharpen or split out what was previously folded into "tool/action efficiency" or "final visual
quality" alone. All seven additions are per the manager-provided discussion's evaluation-dimension
list (`DISCUSSION_ANALYSIS.md` §4, §6).

## 3. Automated vs. human judge split

- **Rule-based / deterministic** (cheap, run on every trajectory): dimension constraint checks
  (aspect ratio, required text present, press-safe line weight, label dimensions), tool-call
  redundancy checks, revision-loop-length checks, selection-consistency checks. These map directly
  to fields already in the schema and need no model call.
- **LLM-judge** (moderate cost, run on every trajectory or a sampled subset): brief-understanding
  accuracy, reference-understanding correctness, direction-to-brief alignment, critique correctness.
  These require reading text fields against the brief/reference content — a good fit for a judge
  model, but the judge's own error rate must be spot-checked against human review periodically, not
  assumed reliable.
- **Human review** (expensive, sampled): direction diversity's *meaningfulness* (not just distance),
  final visual quality's craft dimension, and any trajectory flagged as borderline or high-stakes by
  the automated layers. Human review is mandatory for the pilot (Part 7) precisely because none of
  the automated proxies above are validated yet for Curify's domains.

## 4. Semantic robustness / interface perturbation

A caveat from the manager-provided discussion (`DISCUSSION_ANALYSIS.md` §5), not present in either
prior source: trajectory SFT trained on a fixed tool interface risks teaching a model to memorize
**interface patterns** — a specific tool name, a specific argument schema, a specific ordering —
rather than the underlying **tool-use semantics** (when a capability like "generate an image" should
be invoked at all). A model that has only ever seen `generate_image(prompt=...)` may fail the moment
the same underlying capability is exposed as `render_visual(...)`, `create_asset(...)`, or
`image_generate(...)` with a differently-shaped argument object — not because it lost the underlying
judgment, but because it pattern-matched on the token/schema rather than the semantics.

This benchmark should therefore include, as a distinct test category (not yet built — a future
addition to the pilot, tracked here as a requirement on any real benchmark run):

- **Tool rename**: same capability, different tool name, across otherwise-identical trajectories.
- **Schema perturbation**: same tool, different argument key names/shapes (e.g. `count` vs.
  `num_candidates`, flat args vs. nested `{params: {...}}`).
- **Tool ordering change**: presenting `available_tools` (`TRAJECTORY_SCHEMA.md` §5) in a different
  order than the trajectories used at training time.
- **Alternate image generators / asset sources**: swapping which underlying generation or retrieval
  backend a tool name maps to, without changing the tool's declared name or schema.
- **UI/harness variation**: the same task presented through a differently-structured harness
  (`TRAJECTORY_SCHEMA.md` §5's `harness.environment_notes`), where the stage sequence is logically
  equivalent but not textually identical to training-time trajectories.

The scoring question for each perturbation is not "did the model call the exact same tool," but "did
the model still correctly decide *when* a capability of this kind was needed" — i.e., whether
tool-call correctness (§2) is preserved under perturbation, not whether the literal call matches a
reference trace. This category is not part of the 10–20-task pilot in §7 (that pilot uses one fixed
harness); it is recorded here as a requirement for any Phase 1 evaluation that follows real
trajectory-SFT training (`MANAGER_SUMMARY.md` §Phase 1).

## 5. Example types to include in the benchmark set

- **Positive examples**: trajectories where every stage passes its checks with clean reasoning (see
  `vd-brandlogo-0001` and `vd-poster-0001` in `CURIFY_TRAJECTORY_EXAMPLES.jsonl`).
- **Negative examples**: trajectories with an injected, clearly identifiable failure at one stage
  (e.g., a `direction_generation` step that returns near-duplicate candidates, or a `selection` step
  that contradicts its own `direction_evaluation`) — used to test whether the step-level/trajectory-
  level judges actually catch the failure, not just to test the agent being benchmarked.
- **Revised trajectories**: trajectories containing a caught-and-fixed weak direction (see
  `vd-coffee-0001`), used to test whether revision-effectiveness judges correctly credit a fixed
  trajectory rather than penalizing it for having contained a flaw at all.
- **Pairwise preference examples**: two trajectories (or two final candidates within one trajectory)
  for the same brief, with a human preference label (`human_preference` field in the schema) —
  needed because absolute quality scores are noisy for subjective visual work, and relative
  comparison is usually more reliable to collect.
- **Partial-success cases**: trajectories where one stage is degraded (e.g. `vd-packaging-0001`'s
  thin single-reference retrieval) but the trajectory discloses the limitation rather than hiding
  it — used to test whether the benchmark rewards honest disclosure over confident overclaiming,
  which is the exact behavior `references/quality-gate.md`'s "state the remaining limitation
  briefly; do not describe failed preservation as successful" rule is designed to produce.

## 6. Explicit non-goal

This benchmark does not attempt to produce one scalar "visual direction quality score." Subjective
visual craft judgment is retained as a human-reviewed dimension throughout, not collapsed into an
automated number; the value of the benchmark is in the step-level and trajectory-level layers, which
are checkable in a way the final image alone is not.

## 7. Initial pilot recommendation (Phase 0)

Per the manager-provided discussion's two-stage roadmap (`DISCUSSION_ANALYSIS.md` §6), this pilot is
explicitly **Phase 0 — schema/benchmark validation** only, not the full trajectory-SFT experiment. A
possible Phase 1 (a real trajectory-SFT MVP, only if Phase 0 succeeds) is sketched in
`MANAGER_SUMMARY.md`; no Phase 1 work is scoped, committed, or started here.

Before building any scoring automation, run the benchmark's human-review layer manually against a
small, hand-collected trajectory set:

- **10–20 Creative Exploration tasks**, spanning **2–3 domains** (not all domains at once — start
  with domains that already have some Curify baseline context, e.g. coffee_shop/brand_logo/poster,
  consistent with the domains this task's examples cover).
- **Manually authored or manually reviewed trajectories** in the `TRAJECTORY_SCHEMA.md` format —
  either hand-run through the existing Curify Creative Exploration flow and logged after the fact,
  or hand-authored the way `CURIFY_TRAJECTORY_EXAMPLES.jsonl` was for this task, then checked
  against real outputs.
- **Explicit intermediate outputs required**, not just final images — a trajectory missing
  intermediate steps cannot be step-level or trajectory-level graded at all, only final-output
  graded, which defeats the point of piloting the three-layer design.
- **Both successful and failed/revised examples included deliberately** — a pilot set of only clean
  successes cannot validate whether the critique/revision dimensions or the failure-mode labels are
  usable at all.
- **Benchmark before training**: this pilot's only goal is to test whether the step-level and
  trajectory-level dimensions in Section 2 are gradable by a human reviewer with reasonable
  agreement, and whether an LLM-judge roughly tracks that human judgment on the subset of dimensions
  proposed for automation (Section 3). Do not proceed to any trajectory-SFT data collection or
  training until this benchmark pilot shows the dimensions are actually gradable — training on
  ungradable supervision cannot be evaluated for whether it helped.

This is deliberately smaller than a full benchmark rollout or any training pipeline; see
`MANAGER_SUMMARY.md` for the one-paragraph version of this recommendation.

## 8. Scope: this pilot benchmark vs. a possible future Curify Design Agent Benchmark

Everything in §1–§7 describes one thing: a **small internal pilot benchmark** — 10–20 tasks, 2–3
domains, hand-reviewed, built to test whether the dimensions above are gradable at all before any
training starts. This is not the same object as the **future Curify Design Agent Benchmark** the
manager-provided discussion describes (`DISCUSSION_ANALYSIS.md` §9): a much larger, category-spanning
benchmark (Brand Identity, Packaging, Merch, Marketing Creative, Industrial/Product) with
product-level dimensions (brief adherence, visual quality, creative diversity, brand consistency,
refinement ability, cross-asset consistency, production readiness, efficiency) that the discussion
suggests could double as an internal eval, a research/authority asset, and potentially a public
benchmark and long-term evaluation dataset.

**Curify has not built that benchmark.** It is recorded here as a future strategic direction the
discussion raises, not as work completed, scoped, or committed in this research pass. The dimension
table in §2 of this document is a plausible early contributor to such a benchmark's step/trajectory
layers, but §2's 11+ dimensions and §7's 10–20-task pilot remain the actual, much smaller scope of
this document.
