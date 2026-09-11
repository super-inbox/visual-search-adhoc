# Trajectory Tracking for ASL — Manager Summary

**Date:** 2026-09-10

## Hypothesis

You saw a CV tennis example where video is converted into structured motion
trajectories, and asked whether an analogous representation — explicit, continuous
hand/body/face tracking over time, not just still frames — could help our ASL
recognition. Handshape, fingerspelling, non-manual markers, and language context were
explicitly not assumed to be replaced by this — the question was whether trajectory is a
useful *additional* signal.

## D1 — Can we reliably track hands/body on our videos? Yes.

Ran RTMPose (an open pose-tracking model, via a lightweight wrapper called `rtmlib`) on
5 diagnostic clips chosen to stress-test the hardest cases (shortest clip, fastest
signing, fingerspelling-heavy, richest content, longest clip). Result: **0% missing
tracking** on hands/body across all 5 clips, every frame, with high confidence and
visually-confirmed-correct skeleton overlays (spot-checked against the actual video on 4
of 5 clips). Extraction is fast (roughly real-time on a laptop CPU). This part of the
direction is validated — the raw signal is there and recoverable.

One relevant piece of context: Uni-Sign, a system we already benchmark, is itself built
on this same kind of pose tracking. On these same 5 clips, its tracking is unlikely to be
the reason it translates poorly — but we have not checked this on the full 128-clip
corpus, so this is a narrow observation, not a general claim about Uni-Sign.

## D2 — Does giving Gemini this trajectory data as context help? No, not this way.

Controlled experiment: same 5 clips, same frames, same Gemini model, same sampling — the
**only** change was adding one short block of raw trajectory numbers (hand positions,
speed, which hand is doing what, roughly where relative to the body) to the prompt.
Reference text was never accessible to the model at any point. 7 total Gemini calls.

**Result: 0 of 5 clips showed genuine semantic recovery.** Where output changed at all,
it changed to a *different* wrong answer, not a more correct one. On one clip, standard
text-similarity scores (BLEU/chrF) went up — but only because the model wrote a longer
version of the exact same wrong guess; word-error-rate on that clip didn't move at all.
That's a known trap in these metrics (a wordier wrong answer scores better on some
metrics without being any more correct) — we're not fooled by it, and we're not counting
it as a result.

## What this rules out

Handing an off-the-shelf Gemini model a short text summary of tracked hand/body positions
does not fix the translation failures we've been seeing. This closes that specific,
cheap-to-test approach — no further calls, no prompt tuning, no expansion planned for it.

## What remains plausible, not ruled out

Trajectory/pose information in general is **not** shown to be useless for ASL — only this
one way of using it. The untested, still-live possibility is a model *trained* to consume
hand/body/face motion directly (closer to what Uni-Sign attempts architecturally), rather
than a generic model just being told about it after the fact in plain text. That's a
meaningfully bigger undertaking (training, not just an inference-time prompt change) and
isn't something we'd casually try next without your input.

## Recommended next step

Given three genuinely different axes have now been tested without semantic recovery on
this branch — temporal sampling (2fps/8fps, uniform/adaptive), native/direct video input,
and now trajectory-as-prompt-context — the pattern points toward the bottleneck sitting
somewhere other than "give the input model more/different visual information": most
likely the decoding/language side, or a training-data/domain gap, rather than something
another input-formulation tweak is likely to fix. We'd suggest pausing further input-side
probes and discussing with you whether the next move is (a) an ASL-fluent expert review
to properly diagnose failure type (we've flagged this as blocked on expertise we don't
have, repeatedly), (b) investigating a trained approach (bigger commitment), or (c)
something else entirely — rather than us picking the next experiment unilaterally.
