# MANAGER_SUMMARY.md — Visual Direction / Creative Exploration Trajectory SFT (research only)

Research task, per manager direction: "可以看看 visual direction / creative exploration 怎么用
trajectory SFT 的方法." No frontend, backend, SFT pipeline, or model training was built or changed.
This is an **incremental correction-and-completion pass**: the manager-shared ChatGPT discussion,
previously inaccessible, has now been incorporated (see "Discussion access — corrected" below).
Source-attributed detail for everything from the discussion is in `DISCUSSION_ANALYSIS.md`.

## 1. What did gc-minimal-zine-poster teach us?

It's a Codex Skill (markdown instructions for an LLM), not code or a trained agent, and contains
**no executed trajectory logs** — useful only as a source of *stage vocabulary*, not trajectory
examples. Genuinely reusable: a **fixed / variable / sample-residue** three-way split for reference
analysis; **numeric, checkable fixed-system fields** over vague adjectives; a named **variation-axis
set with an explicit anti-repetition rule**; and a **capped single-retry regeneration loop** that
reports a remaining limitation instead of overclaiming success. Full detail in `REPO_ANALYSIS.md`.

## 2. What did the manager-provided trajectory discussion add?

A set of claims not derivable from the external repo or from Curify's own prior research: distill
observable **behavior/trajectory**, not hidden chain-of-thought; a **harness → trajectory →
preference** three-layer data model; the insight that the valuable asset may be "100k decisions about
what changes next," not "100k design images"; an explicit **BEFORE → HUMAN/CLIENT FEEDBACK → AFTER**
data pattern; a caution that trajectory SFT risks **interface memorization** over tool-use semantics;
a two-phase pilot-then-MVP roadmap; a **Workflow × Data × Evaluation** moat framing; a **Brief →
Design System → Product Family → Production** product-niche hypothesis; the idea of a future
Curify Design Agent Benchmark as a strategic asset; and a data-provenance/compliance caveat for any
real distillation experiment. Full detail, each claim source-attributed, in `DISCUSSION_ANALYSIS.md`.

## 3. What trajectory SFT should mean for Curify

Curify's 8.8 workflow research (five domains) captured **workflow data**: a finished project's
stages (`brief → concepts → design → final result`). Trajectory SFT needs a different object —
**trajectory data**: a record of an agent's actual decision process (`state → decision → action/tool
→ observation → evaluation → next decision → revision → final output`), including paths tried and
rejected — which a published case study structurally cannot contain. The discussion adds a third
object, **preference/taste data**: pairwise comparisons ("A > C") between candidates or trajectories,
used for judge/reward models, DPO-style training, or reranking — not a record of process, a record of
comparison. All three are now distinguished in `TRAJECTORY_SCHEMA.md` §1. Per the discussion's
training-unit framing, trajectory SFT should train `state + tools + history → next action/tool/
arguments/concise decision`, never unrestricted reasoning traces — see `TRAJECTORY_SCHEMA.md` §4.

## 4. Why Harness → Trajectory → Preference is a useful framing

It separates three things that are otherwise easy to conflate into one training target: the
**harness** (the workflow/tool design itself, decided before any model touches it), the **trajectory
policy** (what to do next given state + tools + history), and **taste** (which of several valid
outputs is better — inherently comparative, not something a single trajectory log can express on its
own). Collapsing these loses information: a trajectory can follow a perfectly correct policy and
still lose a pairwise preference on subjective craft grounds the trajectory log never flagged as a
defect. Keeping them separate also clarifies what each is good for training — action policy vs. a
judge/reward model — rather than trying to get one dataset to teach both.

## 5. Why recovery trajectories matter

The discussion's `wrong result → detect problem → diagnose → change tool/prompt/parameter → verify
again` pattern is, per the discussion, a meaningful distinction between a strong agent and a simple
demo — a model that only ever executes clean first-try paths hasn't demonstrated it can notice and
fix its own weak output. This was already present in the coffee-shop example
(`vd-coffee-0001`, step_04–step_07: reject a mismatched candidate, then catch and fix a separate
thumbnail-legibility defect on the winner) before this discussion was incorporated — it needed no
change. What's new is naming **Recovery** as its own first-class benchmark dimension, separate from
general "revision effectiveness," so a trajectory's ability to *notice* a problem is graded
independently from whether its fix happened to work. Added in `BENCHMARK_PROPOSAL.md` §2.

## 6. Why interface perturbation matters

Trajectory SFT trained against one fixed tool schema risks a model that has memorized *tokens*
(a specific tool name, a specific argument shape) rather than learned *when a capability is needed*.
That failure mode is invisible on the training distribution and only shows up when the interface
changes — a different UI, a renamed tool, a different image generator. Testing this now, as an
explicit benchmark category (tool rename, schema perturbation, ordering change, alternate
generators/asset sources, harness variation — `BENCHMARK_PROPOSAL.md` §4), is cheap to plan for and
expensive to retrofit after a model has already been trained on a single rigid interface.

## 7. Curify's possible moat: Workflow × Data × Evaluation

The discussion's strategic argument: don't compete as another generic image generator, graphic
editor, or prompt-to-design tool — the underlying model (Claude/GPT/Gemini/OSS) stays replaceable.
What's defensible is **workflow moat + trajectory data moat + evaluation moat → agent policy**:
Curify's own workflow library, evaluation system, trajectory data, preference data, and real task
feedback. This is a strategic framing, not a schema requirement — it doesn't change any field
definition in `TRAJECTORY_SCHEMA.md`, but it's the lens under which this directory's schema/benchmark
work should be understood as building a data/evaluation asset, not just model-training input.

## 8. Product niche this points toward: Brief → Design System → Product Family → Production

Rather than "Curify = generic Design Agent," the discussion suggests a narrower workflow: brief →
design system → product family → production (e.g. "young women's oriental tea brand" → reference
research → 4 directions → pick one → refine identity → packaging/poster/sticker → cup/tote/social →
production-ready output). **This is recorded as a strategic product hypothesis the discussion
supports — not something scoped, implemented, or committed in this research pass.**

## 9. What should be logged now

Independent of any training decision, the discussion's recommended logging fields — task, state,
reference, tool, action, artifact, feedback, preference, revision, final acceptance — are cheap to
start capturing in Curify's existing Creative Exploration flow today, without waiting on Phase 0/1
below. The `BEFORE → HUMAN/CLIENT FEEDBACK → AFTER` pattern specifically (e.g. "this feels too
cheap" → concrete design changes → "this is right") is called out as an especially valuable long-term
dataset because it turns qualitative client feedback into observable design actions — something
neither workflow data nor a self-detected critique captures. `TRAJECTORY_SCHEMA.md` now has fields
for all of these (`harness`, `user_feedback`, `preference`, `final_acceptance`), and
`CURIFY_TRAJECTORY_EXAMPLES.jsonl`'s packaging example (`vd-packaging-0001`) now demonstrates the
before → feedback → after pattern end to end.

## 10. Phase 0 and Phase 1 next steps

**Phase 0 (recommended now, unchanged in substance from the original pilot recommendation):**
10–20 real Creative Exploration tasks across 2–3 domains, manually reviewed as full trajectories
(not just final images), including both clean successes and failed/revised examples — testing
whether the schema's intermediate states/actions/evaluations are actually gradable by a human
reviewer. No model training in Phase 0.

**Phase 1 (only if Phase 0 succeeds — not a committed plan, a next-stage MVP shape the discussion
proposes):** on the order of 300–500 real design briefs, a teacher agent running 4–8 trajectories
per brief (~2k–4k trajectories total), recording observation/tool call/parameters/screenshots/
artifacts/evaluation/correction, auto- and manually selecting the top 20–30%, training a permitted/
open-weight student on the same harness as the teacher, then a blind teacher-vs-student evaluation
across task success, visual quality, brand consistency, tool-call correctness, recovery rate, turns
to completion, cost, and human preference. **Compliance caveat carried forward from the discussion:**
before any real Phase 1 run, verify the teacher model/provider's terms permit training a
(potentially competing) student on its outputs — prefer permitted teacher sources or Curify's own
task data where terms are unclear. No legal conclusion is offered here; this is a provenance
requirement to check before data collection, not after.

## Discussion access — corrected

The original pass of this research reported the shared ChatGPT link
(`https://chatgpt.com/share/6a7bbf58-43b8-83e8-8968-e0c4662840bf`) as inaccessible — WebFetch
returned only the page title, and interactive browser access wasn't available in that environment.
**That was accurate as a description of the initial access attempt, but it is no longer the final
state.** The discussion's transcript was subsequently provided directly by the user/manager as text
and has now been incorporated throughout this directory (`DISCUSSION_ANALYSIS.md` and the updates to
`TRAJECTORY_SCHEMA.md`, `CURIFY_TRAJECTORY_EXAMPLES.jsonl`, `BENCHMARK_PROPOSAL.md`, `overview.html`
summarized above). No content from the discussion was invented; everything attributed to it in this
directory is a restatement of the supplied transcript, kept source-labeled and separate from the
`gc-minimal-zine-poster` findings and from this research's own Curify-specific proposals.
