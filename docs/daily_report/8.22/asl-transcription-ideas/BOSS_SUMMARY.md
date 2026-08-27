# ASL Transcription — Research & Optimization Thinking (Boss Summary)

> **Revised 2026-08-23** to incorporate boss-provided ground truth received
> after the first pass of this research. Ideation/research only — no code
> changed, no model built. Full detail in the sibling docs in this folder;
> `CURRENT_APPROACH_GAPS.md` has the full reconciliation of repo evidence vs.
> boss context.

## Why this is worth the investment

Real, meaningful, SEO-driven user demand already exists for ASL translation
— people are actively trying it despite today's poor quality, which is
itself a signal the underlying need is strong. Combined with the fact that
credible commercial/open-source options still fall short of a satisfying
result (per the SOTA research in `SOLUTION_OPTIONS.md`), solving this well
would be a genuine differentiator: **if Curify can reach a quality bar that
current SOTA and open models can't reliably hit, that's a real
technical/product moat opportunity** — not a commodity feature competitors
can trivially replicate by wiring up the same generic VLM Curify already
tried. This is framed here as an opportunity worth pursuing, not as
something already proven or achieved; nothing in this research demonstrates
Curify currently has, or is close to having, that differentiated quality.

## Corrected understanding of the current ASL approach

Two things are both true, and reconciling them matters:

1. **From the codebase (`curify-studio`):** the general-purpose dubbing
   pipeline (ElevenLabs Scribe-based) has a `has_speech()` check that
   explicitly treats silent/sign-language video as a no-speech input and
   skips it. No frame-sampling or VLM-based video understanding code exists
   anywhere in that backend, in any branch.
2. **Per your ground truth:** the live/recent ASL tool actually does
   something different and more active — **frame extraction/sampling →
   generic VLM → inferred sign meaning** — and it has real, meaningful
   demand (SEO-driven traffic, many users trying it), with quality currently
   poor / not commercially satisfactory.

These aren't a contradiction once you see they're two separate code paths:
the general dubbing pipeline correctly stays out of ASL's way, while the
dedicated ASL tool (which most plausibly lives in `curify-frontend` — a
separate repo not accessible in this research pass, since Curify's tool
registry routes are defined there) is the one actually serving users, and
is where the quality problem lives. **This doc's earlier framing — that
Curify's ASL handling is "audio-only" and fails closed — was accurate only
for the general dubbing pipeline, not for the dedicated ASL tool. Both
pieces of evidence are kept, not overwritten.**

## Why the current VLM baseline likely underperforms

The live approach (**Baseline 0**) asks a generic vision-language model to
infer meaning from a sparse set of independent still frames. This is
structurally weak for continuous ASL, independent of which VLM is used:

- Signs are trajectories, not poses — static frames lose the motion that
  disambiguates similar handshapes, movement direction (which flips verb
  meaning), and sign transitions.
- Below a sign-specific sampling-rate threshold, sparse frames don't degrade
  gracefully — they alias into different, confidently-wrong apparent motion.
- Fingerspelling's high rate makes it the most frame-rate-sensitive case,
  and dropped letters get "filled in" by the VLM with plausible-but-wrong
  words rather than flagged as missing.
- Facial/head non-manual markers that carry ASL grammar (negation,
  questions) are easy for a model with no ASL-specific training to miss or
  misweight relative to hand motion.
- No persistent memory across a video means long-discourse referent
  tracking breaks down.
- Generic VLMs simply haven't seen enough ASL to have learned its grammar —
  published research (AttnSign, arXiv:2608.00235) confirms general VLMs
  perform poorly on sign translation without task-specific adaptation.

Full mechanism-by-mechanism breakdown and expected error taxonomy in
`CURRENT_VLM_BASELINE_DIAGNOSIS.md`.

## 2–3 best candidate solution directions

Reframed as a baseline ladder (`SOLUTION_OPTIONS.md`) rather than an
unordered option list:

1. **Denser/adaptive frame sampling on the same VLM (Baseline 1)** — the
   cheapest possible experiment; isolates how much of the current failure
   is a fixable sampling-rate problem vs. something deeper. No new model,
   testable this week.
2. **Pose/hand/face landmark → sequence model (Baseline 3)** — the most
   architecturally promising longer-term direction. Google DeepMind's newly
   shipped SL2T (Aug 2026) validates that pose-landmark-to-text is a strong
   approach at scale — cited here strictly as evidence the *approach class*
   works, not as something Curify currently has access to (SL2T's
   weights/API are not available to Curify). Whether an adequate *open*
   checkpoint exists for Curify to actually use is the single biggest
   unresolved unknown in this research.
3. **LLM semantic/context refinement layered on any base recognizer
   (Baseline 5)** — cheap, always-on value-add for fluency, fingerspelled
   name correction, and discourse coherence, regardless of which base wins.

## Recommended MVP architecture

Improve the **live** baseline in place, rather than building something new
from zero:

```
video → signer crop → denser/motion-aware frame sampling (Baseline 1)
  → current VLM (with ASL-aware prompting + confidence flagging)
  → LLM refinement (glossary injection, whole-video context, Baseline 5)
  → [existing subtitle/translate/voiceover utils, unchanged]
  → SRT/VTT (+ optional dub/burn-in)
```

In parallel, run the landscape search for a usable open pose-based
checkpoint (Baseline 3) — if one exists and clearly outperforms the improved
Baseline 0/1 in a head-to-head test, that becomes the medium-term
recognition engine. Full staging in `CURIFY_RECOMMENDED_ARCHITECTURE.md`.

## Quick wins (no training required)

Denser/motion-aware frame sampling · overlapping sliding-window clips ·
signer-focused cropping · ASL-aware prompt engineering · self-consistency
ensembling to catch confident hallucination · pose-skeleton overlay as an
auxiliary visual cue · whole-video context for discourse coherence ·
fingerspelling-specific handling · glossary injection for names/terminology ·
confidence-based fallback to human review · audiovisual fusion when speech
is also present. Full list (12 items) in `QUICK_WINS.md`.

## Recommended next experiment

Full experiment order and decision tree in `EXPERIMENT_PRIORITY.md`. Short
version: **run Baseline 0 (current live approach) vs. 1 (denser/motion-aware
sampling) vs. 2 (video-native VLM) together, on the same 5–10 real ASL
videos**, scored by human review against the shared error taxonomy. Add
Baseline 3 (pose/landmark + open model) to the same round only if a real,
loadable checkpoint is found without significant implementation work. This
one round of human review isolates, in a single pass, whether the current
poor quality is a sampling problem, a temporal-continuity problem, or a
deeper ASL-specialization problem — see `EXPERIMENT_PRIORITY.md` §7 for the
full reasoning and §8 for exactly what's needed from the team to run it.

## What should be tested next

1. **Run the Baseline 0 vs. 1 vs. 2 comparison** on 5–10 real ASL videos
   (`EXPERIMENT_PRIORITY.md` §7, `EVAL_PLAN.md` Priority 0) — the single
   highest-signal experiment available right now. Add Baseline 3 to the
   same round only if a real, loadable open checkpoint is found without
   significant implementation work.
2. Pull the actual implementation details of the live tool (sampling rate,
   prompt, VLM provider) from wherever it's actually implemented — most
   likely `curify-frontend`, which wasn't accessible in this research pass —
   so Baseline 1/2 experiments start from the real current configuration,
   not an assumed one.
3. Finish the intern spec's Stage 1 landscape review with a specific target
   question: is there a usable open pose-to-text (or RGB+pose hybrid)
   checkpoint good enough to build Baseline 3 on.

---

## Reported at end of task

- **Corrected understanding of current ASL approach:** it is not
  audio-only/silently-failing across the board — a dedicated frame-sampling
  + generic VLM tool is live, has real SEO-driven demand, and is what
  actually produces (poor-quality) output for users today. The
  `has_speech()`-gated failure applies to a separate, general dubbing
  pipeline, not to this tool.
- **Why current VLM baseline likely fails:** it reasons over sparse,
  independent still frames, which structurally discards the motion,
  direction, and non-manual-grammar signal that continuous ASL meaning
  depends on — and generic VLMs have not been specifically trained on
  enough ASL to compensate via general video-understanding priors.
- **Top 3 near-term experiments:** (1) Baseline 0 vs. 1 vs. 2 comparison on
  5–10 real videos, adding Baseline 3 to the same round only if a real
  checkpoint is trivially available; (2) pull the live tool's actual
  implementation details from `curify-frontend` (or wherever it lives) to
  ground further experiments in reality; (3) landscape search specifically
  for a usable open pose-to-text checkpoint.
- **Most promising longer-term architecture:** pose/landmark → temporal
  sequence model (Baseline 3), validated as an approach class by Google's
  SL2T — but explicitly *not* confirmed as available or sufficient for
  Curify yet; treat as the leading candidate to test, not a foregone
  conclusion.
- **Remaining unknowns:** (1) whether any open pose-based or hybrid
  RGB+pose ASL checkpoint is actually loadable and adequate today; (2) the
  live tool's exact sampling rate/prompt/provider, since its code lives
  outside this research pass's access; (3) real user-volume/failure-rate
  distribution at scale (only qualitative demand signal — SEO traffic, "many
  users trying it" — is confirmed so far, not a quantified volume); (4)
  whether Google will open SL2T/SignGemma access on any timeline relevant to
  Curify.
