# Trajectory-probe QA — `Fz-N1S0swh8_2-8-rgb_front`

**Classification: USABLE**

- 54/54 frames (100%) had body, left-hand, and right-hand detection above threshold;
  0 multi-person frames.
- Mean confidence: body 0.861, left hand 0.835, right hand 0.811.
- Visual sanity check (frame 27 of 54, spot-check still): individual finger joints are
  clearly resolved on both hands mid-gesture, correctly overlaid on the signer's actual
  hand position; face landmarks correctly on the face. This is the clip tagged both
  `fingerspelling_candidate` and `fast_signing` — exactly the case D1 was most worried
  about for tracking quality — and the tracker held up with visibly correct per-finger
  detail, not just a coarse hand blob.
- Both hands show meaningfully elevated velocity (mean 0.47 left / 0.63 right
  normalized-diagonal/s) relative to the two longer, calmer clips in this probe,
  consistent with the `fast_signing` tag.
- 6 left-hand / 2 right-hand discontinuity candidates out of 53 possible steps — low
  relative to clip length.
- The frame-baseline prediction on this clip was a single wrong word ("Angry"); this
  probe shows continuous, well-tracked two-hand motion with visible finger articulation
  throughout, so — as with `92V3oH63zbQ` — the text-model failure is not explained by a
  lack of visible signing activity.
