# Trajectory-probe QA — `92V3oH63zbQ_5-1-rgb_front`

**Classification: USABLE**

- 55/55 frames (100%) had body, left-hand, and right-hand detection above the
  majority-of-points threshold; 0 frames with more than one person detected.
- Mean confidence: body 0.906, left hand 0.885, right hand 0.880 — all comfortably above
  the 0.3 per-point detection floor.
- Visual sanity check (frame 25 of 55, `trajectory_overlay.mp4` — a local visual QA aid
  generated during this review, intentionally not part of the committed deliverable):
  skeleton lines correctly follow the signer's shoulders/arms; face landmarks correctly
  sit on the eyes/nose/mouth; hands are correctly located at the signer's lap where they
  visibly are in the source frame. See the exported still in this session's transcript —
  no visible mistracking.
- Right-hand velocity (mean 0.57 normalized-diagonal/s) is notably higher than left
  (mean 0.18) and than every other clip in this probe — consistent with this clip's
  `fast_signing_or_question` tag; the tracker kept up (no missing-tracking increase
  despite the faster motion).
- 5 left-hand / 14 right-hand discontinuity candidates flagged (self-calibrated,
  >4x this clip's own median step) out of 54 possible steps — worth a closer look given
  the elevated right-hand speed, but not a missing-tracking problem; could be genuine
  fast motion rather than a tracking error (not further adjudicated here — geometry only,
  no motion-type judgment made).
- Both the frame-baseline and native-video Gemini predictions on this clip were
  completely empty (see native-video `BLOCKER_STATUS.md` and the frame-baseline
  inspector page) — this trajectory probe shows there *was* clean, continuous,
  trackable motion the whole time, so the text-model failure here is not explained by
  "nothing happened on screen."
