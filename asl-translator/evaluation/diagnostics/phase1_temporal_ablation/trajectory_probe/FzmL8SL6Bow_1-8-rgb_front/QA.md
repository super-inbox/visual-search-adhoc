# Trajectory-probe QA — `FzmL8SL6Bow_1-8-rgb_front`

**Classification: USABLE**

- 618/618 frames (100%) had body, left-hand, and right-hand detection above threshold;
  0 multi-person frames — sustained over the full 25.75s, the longest clip in the probe.
- Mean confidence: body 0.861, left hand 0.841, right hand 0.851 — consistent with the
  rest of the probe, no degradation over the longer duration.
- Visual sanity check (frame 309 of 618, spot-check still): both hands tracked with
  visible finger-level detail, correctly positioned at the signer's actual two-handed
  gesture location; face landmarks correctly on the face. Confirms tracking quality holds
  on a *different* signer (this clip's signer differs from the other two spot-checked
  clips) and mid-clip, not just at an easy first frame.
- 98 left-hand / 132 right-hand discontinuity candidates out of 617 possible steps
  (~16%/~21%) — the highest raw count in the probe, expected given it has by far the
  most frames/steps; rate is in the same ballpark as the other clips, not disproportionate.
- This is the clip with the deepest existing cross-referenced artifact trail in this
  project (frame-baseline inspector page, Uni-Sign prediction, native-video Stage-1
  result — WER 1.0/CER 0.93, "An ugly frog a big, fat frog" vs. a reference about
  drywall repair). The trajectory probe shows clean, continuous, well-tracked two-hand
  motion throughout — reinforcing the same point as the other clips: whatever is causing
  the semantic failure on this clip, it is not an absence of trackable visual signal.
