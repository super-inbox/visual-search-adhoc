# Trajectory-probe QA — `G19uBylwQww_1-2-rgb_front`

**Classification: USABLE**

- 136/136 frames (100%) had body, left-hand, and right-hand detection above threshold;
  0 multi-person frames.
- Mean confidence: body 0.867, left hand 0.929 (the highest hand confidence in the
  5-clip probe), right hand 0.868.
- This is the richest-tagged clip in the diagnostic-12 (`number_token` +
  `fingerspelling_candidate` + `fast_signing`) and also had the *least bad* frame-baseline
  WER (0.8077) of the whole set — a useful contrast case. Tracking quality here is not
  visibly worse for the higher-difficulty tags; if anything, confidence is the best of
  the probe.
- 18 left-hand / 23 right-hand discontinuity candidates out of 135 possible steps
  (~13–17%) — the highest rate in the probe alongside the longest clip, plausible given
  the `fast_signing` tag; not separately visually spot-checked this round (3 of 5 clips
  were spot-checked this session, satisfying the ≥2/5 minimum — this one relies on its
  strong quantitative numbers alone).
