# Next product direction — Phase 3 goal (not yet executed)

**Status: planning document only. No experiment described here has been
run.** This defines the goal and hard requirements for the next phase,
based on everything established in Phase 1 (ground truth + OpenSLT) and
Phase 2 (Uni-Sign) — see `ASL_EVALUATION_SUMMARY.md` for the full
evidence base this builds on.

---

## Why not just keep tuning OpenSLT or Uni-Sign

Both released academic checkpoints have now been characterized well
enough to stop here, deliberately:

- **Absolute quality ceiling is established, not a tuning artifact.**
  Topic fabrication is universal or near-universal in both systems across
  the full frozen benchmark — this is a content/semantic failure, not a
  decoding-parameter problem. Uni-Sign's `max_new_tokens=100` truncation
  issue is real but explains *incompleteness*, not the *wrong-topic*
  failure that occurs on every clip regardless of length.
- **Licensing already rules out production use, independent of any
  accuracy result.** Uni-Sign's checkpoint is CC BY-NC-4.0 with no code
  license at all; OpenSLT's data/checkpoint is CC BY-NC-ND 4.0. No amount
  of further tuning changes this.
- **Tuning on the frozen benchmark would contaminate the one clean
  evaluation asset this project has.** The 19-clip set was deliberately
  frozen before any model saw it, specifically so it could keep serving
  as an unbiased comparison point. Iterating decoding parameters against
  it to chase a better number would destroy that property for future
  comparisons.

The next phase is therefore a **new search**, not a continuation of
tuning either existing checkpoint.

---

## Goal

**Find a production-usable ASL→English translation approach** — one that
could realistically become a candidate to address Curify's confirmed
frame-based weakness, not merely another research data point.

---

## Hard requirements

1. **Continuous/native video input or an explicit motion representation**
   — the same bar Phase 2's search used, and the property directly
   implicated in Curify's diagnosed weakness (fingerspelling, continuous
   motion).
2. **ASL → English** output, not another sign language, not isolated-sign
   recognition.
3. **Commercially compatible license or API terms.** This is a hard
   requirement, not a nice-to-have, given both academic checkpoints
   evaluated so far were disqualified on licensing alone regardless of
   accuracy. This includes: an open-weight model under an Apache-2.0 /
   MIT / commercially-licensable-on-request model license, **or** a
   commercial API/vendor whose terms of service permit the intended
   product use (data handling, redistribution of outputs, usage volume).
4. **Runnable on new video** — not a fixed research demo, not something
   that only works on a specific pre-packaged dataset.
5. **Evaluable on our clean, frozen benchmark** — either the internal
   verified-gold clips (155, 1252) or the 19-clip How2Sign set, without
   needing to modify either.
6. **Realistic latency/cost for product use.** Uni-Sign's ~20.6 minutes
   CPU-only for 19 short clips (~65s average per clip) is a research-pass
   number, not a product-latency number — any candidate needs a credible
   path to production-viable latency (GPU inference, a hosted API, or a
   materially lighter model), not just "it eventually finishes."

---

## Recommended next experiment category (not a specific checkpoint)

Rather than searching for a third academic from-scratch-ASL checkpoint
(the search in Phase 2 already found the field thin — most candidates
were `NO_PUBLIC_WEIGHTS` or `REQUIRES_TRAINING`; see
`docs/daily_report/8.31/asl-next-baseline/SECOND_BASELINE_CANDIDATES.md`),
the recommended next category is:

**A commercially-licensable native-video vision-language model (VLM),
evaluated zero-shot or with a small ASL-specific adapter, rather than a
from-scratch ASL-only architecture.**

Rationale:
- The two purpose-built ASL-specific systems found late in Phase 2's
  search (RVLF, AttnSign — both explicitly VLM-based, both reporting
  How2Sign numbers) are exactly this category, but neither has released
  code yet. This direction should be re-checked periodically for a
  release, since it's the closest fit found to what a state-of-the-art
  system in this space now looks like.
- General-purpose commercial video-capable models (accessed via API
  under normal commercial terms, or open-weight models under a
  commercially-permissive license) sidestep the licensing dead-end that
  closed off both OpenSLT and Uni-Sign, without waiting on an academic
  group's release schedule.
- This also directly tests a hypothesis this project has not yet
  addressed: whether a large, general video-understanding model — not
  specifically trained on ASL — already has enough latent capability
  (from broad video pretraining) to outperform small, ASL-specific,
  from-scratch checkpoints. Phase 2's two academic baselines both had
  well under 1B ASL-specific parameters doing the heavy lifting (I3D
  encoder + light Fairseq transformer for OpenSLT; RTMPose + mT5-base for
  Uni-Sign) — a frontier-scale VLM is a genuinely different bet, not just
  a bigger version of the same approach.

**Concretely, the next phase should:**
1. Identify 2–3 candidate commercially-licensable native-video VLMs
   (open-weight with a permissive license, or API-accessible under
   acceptable commercial terms).
2. Verify each against the hard requirements above **before** running
   anything — same discipline as Phase 2's candidate search.
3. Design a small, bounded first experiment (e.g. one clip, then the
   19-clip benchmark) with the same guardrails used in Phase 2: no
   tuning against the frozen benchmark, explicit licensing sign-off
   before any production consideration, clear disclosure of any
   prompt/setup choices made.

**This document does not select a specific model or vendor and does not
authorize running anything.** That is the next approval step, not part
of this summary.
