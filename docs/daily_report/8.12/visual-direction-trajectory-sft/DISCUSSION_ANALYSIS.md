# DISCUSSION_ANALYSIS.md — Manager-Provided Trajectory-SFT Discussion

**Source status.** The public ChatGPT share link
(`https://chatgpt.com/share/6a7bbf58-43b8-83e8-8968-e0c4662840bf`) was not machine-readable during
the initial pass of this research (see `MANAGER_SUMMARY.md` for the corrected access history). Its
transcript content was subsequently provided directly by the user/manager as text and is analyzed
below. Everything in this file is **analysis of that manager-provided discussion content**, kept
separate from `REPO_ANALYSIS.md` (which is analysis of the external `gc-minimal-zine-poster` GitHub
repo) and from `TRAJECTORY_SCHEMA.md`/`BENCHMARK_PROPOSAL.md` (which are Curify-specific proposals
we author, informed by both sources). Where a claim below is this research's own extrapolation
rather than a restatement of the discussion, it is marked "We propose."

No content beyond what was supplied is asserted here. No frontend, backend, training pipeline, or
production benchmark was built as part of incorporating this discussion.

---

## 1. Core thesis — distill behavior/trajectory, not hidden CoT

The manager-provided discussion argues that for an agent product, the useful thing to distill from a
capable "teacher" is **not hidden chain-of-thought**. The useful target is **behavior**: trajectory,
tool-use policy, taste/preference, and recovery behavior.

It frames a design agent's capability as a combination of **model + context + tools + harness** —
not the model alone. Because of that, the first thing worth capturing is *observable* agent behavior,
structured as:

```
State / Observation → selected tool → tool arguments → tool result / screenshot
→ next action → artifact → evaluation / user correction
```

A suitable SFT training unit, per the discussion, is:

```
Task + Environment state + Available tools + Previous actions
→ predict next action / tool / arguments / concise decision summary
```

The discussion is explicit that this should **not** require or store unrestricted hidden
chain-of-thought — only observable structured decisions and concise rationales. This is consistent
with, and reinforces, the "no hidden CoT" design constraint this research already independently
adopted in `TRAJECTORY_SCHEMA.md` §3 (derived there from `gc-minimal-zine-poster`'s own
checklist-style, non-deliberative output pattern) — two different sources converging on the same
constraint, not one copying the other.

## 2. Three-layer model — harness, trajectory/action policy, taste/preference

The discussion proposes thinking about design-agent data in three layers:

1. **Harness** — designed and logged *before* any model training: the workflow itself. For a design
   agent this can look like: brand brief → understand need → find references/assets → propose
   creative directions → generate prototype → visual inspection → detect problems → change
   prompt/parameters/layout → regenerate → expand to packaging/poster/sticker/merch.
2. **Trajectory / action policy** — expert trajectories used to train a next-action/tool policy,
   rather than hidden CoT.
3. **Taste / preference** — creative exploration generates many candidates; pairwise preference data
   (e.g. "A > C", "D > B", "F > A") is collected from a model judge, designer vote, client vote, or
   user behavior, for use in reward/judge models, preference models, DPO-style training, candidate
   reranking, or agent self-critique.

A strategic insight the discussion states directly: **the valuable asset may not be "100k design
images" — it may be "100k decisions about what should change next in a specific design state."**
This reframes what counts as a data asset for a design-agent product: not a media library, but a
decision log.

**We propose** mapping this three-layer model onto the existing schema/benchmark work as follows —
`TRAJECTORY_SCHEMA.md` §1 already distinguishes workflow data from trajectory data (layers 1 and 2);
this discussion adds the third layer (taste/preference) as a distinct data type that neither prior
document covered, and the schema is updated accordingly (§4).

## 3. Valuable trajectory data — observable fields, and before → feedback → after

The discussion recommends logging: task, state, reference, tool, action, artifact, feedback,
preference, revision, final acceptance — and specifically calls out the shape:

```
BEFORE → HUMAN / CLIENT FEEDBACK → AFTER
```

with a worked example: user says "This packaging feels too cheap" → agent actions (reduce
saturation, serif typography, more whitespace, reduce illustration density, matte packaging mockup)
→ user says "This is right." The discussion frames this as translating **qualitative design
feedback into observable design actions**, and calls it out as an especially valuable long-term
dataset — distinct from self-detected critique (§4 below), because it captures a human judgment call
rather than a rule-checkable defect.

This is a gap in the existing schema/examples: `TRAJECTORY_SCHEMA.md`'s original 10 stages and all
four original `CURIFY_TRAJECTORY_EXAMPLES.jsonl` trajectories model self/model-detected critique
(a checkable production defect) but none modeled human/client feedback as a distinct input. This
update adds a `user_feedback` field and a `client_feedback` stage to the schema, and extends the
packaging example (`vd-packaging-0001`) to demonstrate the before → feedback → after pattern — see
`TRAJECTORY_SCHEMA.md` §5 and `CURIFY_TRAJECTORY_EXAMPLES.jsonl`.

## 4. Failure/recovery trajectories are important

The discussion is explicit: do not keep only successful trajectories. Failure/recovery behavior is
particularly valuable and should be represented as:

```
wrong result → detect problem → diagnose → change tool / prompt / parameter → verify again
```

It states that recovery behavior is a meaningful distinction between a strong agent and a simple
demo, and recommends the benchmark include a clear Recovery metric/dimension. Examples should
preserve: weak direction → observable mismatch → rejection → revision → verification.

This is already substantially represented in the existing work: the `vd-coffee-0001` example's
step_04→step_07 chain (evaluate candidate B as a brief mismatch → reject with stated reason → detect
a separate thumbnail-legibility defect on the winning candidate → diagnose → capped revision →
re-verify) matches this pattern closely, and predates this discussion's incorporation — it was
derived independently from `gc-minimal-zine-poster`'s single-retry quality-gate pattern (see
`REPO_ANALYSIS.md` A.6) and the brief's own weak-direction requirement. **We preserve this example
as-is**; it did not need modification to satisfy this discussion's recovery requirement. What the
discussion adds on top is the explicit recommendation to name this a first-class **Recovery**
benchmark dimension rather than leaving it implicit inside "revision effectiveness" — added in
`BENCHMARK_PROPOSAL.md` §2.

## 5. Interface-memorization caveat

A major caveat from the discussion: trajectory SFT may cause a model to memorize **interface
patterns** instead of learning tool-use **semantics**. It recommends deliberately testing robustness
through perturbations: tool rename, schema perturbation, tool ordering change, different UI,
different image generators, different asset sources. Example: don't always expose only
`generate_image(prompt=...)` — also test semantically equivalent tools like `render_visual(...)`,
`create_asset(...)`, `image_generate(...)`. The goal is to test whether the model understands *when*
to generate an image, not *which token/schema* triggers a call it has memorized.

This is a genuinely new consideration not present anywhere in the prior research (neither
`gc-minimal-zine-poster`, which has a single fixed built-in image tool with no naming variation, nor
the original benchmark draft, which specified tool names as fixed schema fields without testing
robustness to their variation). Added as a dedicated "Semantic robustness / interface perturbation"
section in `BENCHMARK_PROPOSAL.md` §3.

## 6. Phase 0 vs. Phase 1 pilot

The existing research (`BENCHMARK_PROPOSAL.md` §6, `MANAGER_SUMMARY.md`) already recommended a small
10–20 task, 2–3 domain, manually-reviewed pilot before any training. The discussion's contribution is
to frame that pilot explicitly as **Phase 0** (schema/benchmark validation, no model training) and to
sketch what a **Phase 1** trajectory-SFT MVP could look like *if* Phase 0 succeeds:

- ~300–500 real design briefs
- a teacher agent runs 4–8 trajectories per brief (roughly 2k–4k trajectories total)
- record observation, tool call, parameters, screenshots, artifacts, evaluation, correction
- automatically + manually select the top 20–30%
- train a permitted/open-weight student on the same harness/tools as the teacher
- blind Teacher vs. Student evaluation across: task success, visual quality, brand consistency,
  tool-call correctness, recovery rate, turns to completion, cost, human preference

**These 300–500/2k–4k numbers are the source discussion's proposed next-stage MVP scale, not a
committed Curify plan.** They are presented here, and in `BENCHMARK_PROPOSAL.md`/`MANAGER_SUMMARY.md`,
strictly as an illustrative Phase 1 shape to consider only after Phase 0's smaller pilot demonstrates
the benchmark dimensions are gradable — consistent with the "benchmark before training" position this
research already held independently of this discussion.

## 7. Workflow × Data × Evaluation moat

A significant strategic addition. The discussion argues Curify should not compete by building another
generic AI image generator, graphic editor, Figma agent, or prompt-to-design tool. The proposed
strategic position is closer to **design workflow intelligence** — knowing how a real design task
should move from requirement to deliverable:

```
Design Brief → Creative Exploration → Style Directions → Design Evaluation
→ Refinement → Asset Expansion → Production Output
```

The long-term moat is framed as **Workflow moat + Trajectory data moat + Evaluation moat → Agent
Policy**. The underlying model stays replaceable (Claude / GPT / Gemini / OSS); what belongs to
Curify is the workflow library, evaluation system, trajectory data, preference data, and real task
feedback.

**We note** this is a strategic/product framing, not a technical schema requirement — it does not by
itself change `TRAJECTORY_SCHEMA.md`'s field definitions, but it is the framing under which the
schema/benchmark/data work in this directory should be understood as building a moat, not just a
model-training input.

## 8. Product niche hypothesis — Brief → Design System → Product Family → Production

The discussion recommends narrowing the product abstraction from "Curify = generic Design Agent" to
a workflow more like:

```
Brief → Design System → Product Family → Production
```

Worked example given: "young women's oriental tea brand" → reference research → 4 creative
directions → choose #3 → refine identity → packaging / poster / sticker → cup / tote / social →
production-ready output.

**This is recorded here as a strategic product hypothesis supported by the discussion, not as
something implemented, scoped, or committed in this session.** No product or roadmap decision is
made by recording it.

## 9. Benchmark as an asset

The discussion proposes that a future Curify Design Agent Benchmark could itself become an asset —
potentially spanning Brand Identity, Packaging, Merch, Marketing Creative, and Industrial/Product
categories, with product-level dimensions like brief adherence, visual quality, creative diversity,
brand consistency, refinement ability, cross-asset consistency, production readiness, and efficiency.
It could serve simultaneously as an internal eval, a research/authority asset, a potentially public
benchmark, and a long-term evaluation dataset.

**Curify has not built this benchmark.** The small internal trajectory benchmark proposed in
`BENCHMARK_PROPOSAL.md` (11+ dimensions, 3 layers, over 10–20 pilot tasks) is a distinct, much
smaller, near-term artifact from this future public/product-level benchmark — the distinction is made
explicit in `BENCHMARK_PROPOSAL.md`'s new §7.

## 10. Compliance / provenance caveat

The discussion raises a practical caveat: do not assume output from a closed frontier model can
automatically be used to train a competing model. For any real trajectory-distillation/SFT
experiment, it recommends verifying applicable model/provider terms, preferring teacher sources and
data with appropriate permissions, preferring Curify's own user/task data where allowed, and
considering open/permitted models where appropriate.

This is recorded here as a **data/provenance/compliance requirement for future experiments**, not as
a legal conclusion — no legal judgment is offered by this research, and none should be inferred from
this section. Any real Phase 1 experiment should have its teacher-model choice and data-usage terms
reviewed before data collection begins, not after.

---

## Source hygiene summary

- Claims in §1–§10 above are attributed to "the manager-provided discussion" throughout, and are
  restatements/summaries of the supplied transcript content, not independent research findings.
- Claims about `gc-minimal-zine-poster` are cross-referenced to `REPO_ANALYSIS.md`, never merged into
  this discussion's claims.
- Wherever this file proposes a Curify-specific mapping (schema field, benchmark dimension, example
  extension) that is not itself stated in the discussion, it is marked "We propose" / "We note" to
  keep the source boundary visible.
