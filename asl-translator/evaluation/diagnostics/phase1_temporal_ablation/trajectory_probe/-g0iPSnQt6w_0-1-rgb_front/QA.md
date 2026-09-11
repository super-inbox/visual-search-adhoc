# Trajectory-probe QA — `-g0iPSnQt6w_0-1-rgb_front`

**Classification: USABLE (one caveat noted, not a tracking failure)**

- 175/175 frames (100%) had body, left-hand, and right-hand detection above the
  majority-of-points threshold; 0 multi-person frames.
- Mean confidence: body 0.877, right hand 0.877 — both strong. **Left hand mean 0.579**,
  the softest confidence number in this 5-clip probe, though every frame still cleared
  the majority-of-21-points threshold (min frame-mean was 0.47, only 5/175 frames dipped
  below 0.5 mean).
- Visual sanity check (frame 87 of 175, spot-check still): one hand is raised near the
  chin with clearly resolved finger-level detail and correct tracking; the other hand
  sits lower/less prominently in frame. This is consistent with the confidence asymmetry
  — it reads as **one hand being more visually active/prominent than the other in this
  particular clip**, not a tracking defect (the lower-confidence hand was still detected
  in every frame, just with less certainty).
- Left-hand velocity is the lowest in the probe (mean 0.055 normalized-diagonal/s) and
  0 discontinuity candidates flagged — consistent with it being the quieter, less active
  hand in this clip, not a defect.
- Right-hand: 12 discontinuity candidates out of 174 possible steps (~7%), the raised/
  active hand shows more motion, plausible for a `question`-tagged clip.
- Net read: reliable tracking on both hands; the asymmetric confidence reflects real,
  explainable asymmetric hand visibility in this clip, worth keeping in mind if this clip
  is used in D2 (a lower-confidence hand's derived signals should be flagged as
  lower-certainty in any downstream use, not silently treated as equally reliable).
