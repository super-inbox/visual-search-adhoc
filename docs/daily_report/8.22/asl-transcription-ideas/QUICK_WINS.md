# Quick Wins — No New Model Training Required

> **Update 2026-08-23:** Reframed given boss-provided ground truth that a
> live frame-sampling + generic VLM approach (**Baseline 0**) already exists
> with real user demand and currently poor quality. These quick wins are now
> improvements *to that live baseline* (Baselines 1/2/5 in
> `SOLUTION_OPTIONS.md`), not fixes to a nonexistent audio-only path. Items
> below are cross-referenced to the specific structural weakness they target
> in `CURRENT_VLM_BASELINE_DIAGNOSIS.md`.

Ranked roughly by effort. None require training a model from scratch.

1. **Denser or motion-aware frame sampling (Baseline 1).** If the live tool
   samples at a fixed low rate, raise the rate and/or switch to
   keyframe-selection at peak hand velocity / handshape-change points
   instead of fixed intervals. Directly targets **sparse-frame aliasing**
   and **transition-frame artifacts** — the diagnosis doc's top mechanical
   failure modes. Config/prompting change, not a new model.

2. **Overlapping sliding-window clips.** Feed the VLM short overlapping
   windows of consecutive frames instead of independent stills, so
   consecutive calls share context and the model sees some real motion
   within each window rather than isolated snapshots.

3. **Video-native VLM input where available (Baseline 2).** If the current
   provider/integration only sends discrete images, check whether switching
   to a native video-input mode (where the provider supports it) preserves
   more motion information for the same or similar cost.

4. **Signer-focused crop.** Run a person/face detector first and crop to
   the signer's bounding box before sampling frames — cheap, off-the-shelf,
   and reduces wasted visual capacity spent on background instead of
   hand/face detail, addressing the "occlusion / multiple people / camera
   framing" hard cases.

5. **Prompt engineering for ASL-awareness.** Explicitly instruct the VLM
   that the input is continuous ASL (not generic gesture or body language),
   ask it to attend to eyebrow/head/mouth movement as grammatically
   meaningful (negation, question type) rather than incidental expression,
   and ask it to flag low-confidence spans instead of guessing silently.
   Directly targets the **generic-VLM-lacks-ASL-specialization** and
   **facial/non-manual-marker** failure modes.

6. **Self-consistency / ensembling.** Call the VLM multiple times (or at
   varied sampling rates/windows) and flag disagreement across runs as
   low-confidence rather than presenting one confident-sounding answer —
   cheap way to surface the "confident hallucination" failure mode
   identified as the most product-damaging error class.

7. **Auxiliary pose overlay.** Run MediaPipe Holistic and draw the
   hand/body/face skeleton onto sampled frames before sending them to the
   VLM — an explicit structured visual cue that doesn't require replacing
   the model, and produces a useful byproduct (extracted pose data) for
   evaluating Baseline 3 later regardless of whether it helps Baseline 0.

8. **Context window spanning the whole video, not per-clip.** If the
   current tool translates short clips independently, pass the whole
   video's sampled frames/draft output into one LLM context for a
   refinement pass — mitigates the long-context discourse hard case
   (referent tracking, topic maintenance) without touching the base
   recognizer.

9. **Fingerspelling-specific handling.** Fingerspelling is the failure mode
   most sensitive to frame rate (see diagnosis doc §1) and the case that
   matters most for product usefulness (names, places, brands). Flag likely
   fingerspelling segments heuristically (rapid, small, one-handed motion
   near the face) and either raise their sampling rate specifically or mark
   them lower-confidence rather than letting the model guess a plausible
   but wrong word.

10. **Terminology/name preservation via glossary injection.** Reuse the
    Baseline 5 refinement pass to inject a per-customer or per-domain
    glossary into the LLM prompt so fingerspelled or ambiguous proper nouns
    get corrected against a known list instead of guessed.

11. **Confidence-based fallback / human-in-the-loop labeling.** Emit a
    confidence score (or use self-consistency as a proxy, item 6); below a
    threshold, label the output clearly as "auto-generated, unverified" or
    route to the existing manual-translation fallback already used for user
    1252 — an explicit, intentional product tier instead of a silent
    quality gap.

12. **Audiovisual fusion when speech is present.** When audio has real
    speech (e.g., interpreter-on-stage, sign-supported speech), run both
    the sign-recognition path and the existing Scribe transcription in
    parallel and use the higher-confidence channel per segment, or use the
    audio transcript to disambiguate fingerspelled names the sign channel
    is unsure about. Pure orchestration — no new model.
