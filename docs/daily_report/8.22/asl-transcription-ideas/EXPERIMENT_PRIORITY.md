# ASL Experiment Priority

Turns the research in this folder into a concrete experiment order and
decision tree. Assumes the ground truth established in
`CURRENT_APPROACH_GAPS.md`: the live/recent ASL approach is frame
extraction/sampling → generic VLM → transcription (**Baseline 0**), it has
real SEO-driven user demand, and quality is currently poor.

## 1. What we need to learn first

1. **How much of the current quality problem comes from sparse/naive frame
   sampling?** — i.e., is this a cheap sampling/prompting fix or something
   deeper?
2. **Does preserving temporal video information materially outperform
   independent-image-frame prompting?** — i.e., is motion continuity itself
   the bottleneck, separate from sampling density?
3. **Is there any usable ASL-specialized open model/checkpoint that beats
   generic VLMs enough to justify a specialized path?** — this is currently
   unverified and is the single largest unknown in the whole research set.

Every experiment below is designed to answer one of these three, as cheaply
as possible, in order.

## 2. Baselines to compare

**Baseline 0 — Current sampled-frame + generic VLM.** Reproduce the current
logic as closely as possible once the live tool's config is found (see
Section 8 — this is currently unverified from this research pass, since the
tool most plausibly lives in `curify-frontend`, outside this pass's access).
Serves as the control for every other baseline.

**Baseline 1 — Improved sampling + same VLM.** Denser sampling;
motion-aware/adaptive frame selection (keyframes at peak hand velocity or
handshape-change events, not fixed intervals); clip grouping instead of
independent frame grabs; prompts that preserve local temporal order
(frame-N-then-frame-N+1 sequencing, not an unordered image set). No new
model — same VLM as Baseline 0.

**Baseline 2 — Video-native VLM.** Feed temporal video/clip input directly
to a provider that supports it, instead of reducing the task to independent
still images. Still no ASL-specific training — isolates whether *motion
continuity itself*, independent of sampling density, is the bottleneck.

**Baseline 3 — Pose/landmark + open sign-language model.** MediaPipe (or
equivalent) hand/body/face landmarks fed into a temporal sequence model.
**Only test if a real, loadable checkpoint is actually found** — do not
fabricate or assume one exists. If the landscape search comes up empty,
this baseline is skipped, not simulated.

**Baseline 4 — RGB + pose hybrid / ASL-specialized model.** Research-heavy
reproduction (e.g., Sign2GPT/SpaMo/SSVP-SLT-style fusion). Not a first-round
experiment unless an immediately usable implementation already exists —
otherwise it's a multi-week-plus research bet, not a quick comparison.

## 3. Test set

Preferred: **5–10 real ASL user videos from historical projects**, if
privacy-safe access is available (see `EVAL_PLAN.md` for the safe-extraction
process — filter by non-PII signal, exclude account/email fields, get
sign-off before use). If that access isn't ready in time, use
internal/reference ASL videos first (public datasets — How2Sign,
YouTube-ASL clips — or the known demo asset `dev/jayw/raw/asl-demo-translation.mp4`)
rather than blocking the experiment on data-access approval.

Stratify the set across:
- pure silent ASL
- fingerspelling-heavy
- fast continuous signing
- facial/non-manual-marker-heavy
- longer sentence/discourse
- poor lighting / occlusion
- ASL + spoken audio present (where available)

For every video, record: duration, signer count, video quality
(resolution/lighting/camera stability), whether spoken audio exists, and a
reference transcript/subtitle if one can be produced or already exists.

## 4. Evaluation dimensions

- Semantic translation correctness
- Omission rate
- Hallucination rate
- Fingerspelling accuracy
- Named-entity preservation
- Long-context coherence
- Subtitle segmentation quality
- Timestamp/alignment quality
- Latency
- Inference cost

**Human review is the primary quality judge for this first small
experiment** (5–10 videos is too small a sample for automated metrics to be
reliable on their own). Automated metrics (chrF/COMET-style similarity;
BLEU only for comparability with published numbers) are secondary, and only
usable where a reference transcript exists. Full rubric detail in
`EVAL_PLAN.md`; full error taxonomy in `CURRENT_VLM_BASELINE_DIAGNOSIS.md` §2.

## 5. Decision thresholds

- **Case A** — If Baseline 1 gives a meaningful improvement over Baseline 0
  at low cost → **ship sampling/prompt optimization first** as a short-term
  fix to the live tool.
- **Case B** — If Baseline 2 materially beats Baseline 1 → **prioritize a
  video-native VLM path** (accept the added cost/latency for the quality
  gain).
- **Case C** — If Baseline 3 clearly beats Baseline 2 and has acceptable
  latency/cost → **prototype a dedicated pose-based ASL route**
  (`app/utils/asl_utils.py` + a thin pipeline wrapper).
- **Case D** — If no available baseline approaches commercial quality →
  **consider specialized fine-tuning, a model partnership (e.g. re-approach
  Sign-Speak or an equivalent vendor), or a proprietary-data strategy** —
  this is a build-vs-buy/business decision at that point, not a pure
  engineering one.

These cases are not mutually exclusive across time — e.g., ship Case A's fix
immediately while Case C's prototype runs in parallel.

## 6. Quick wins before model training

No-training changes, ranked by impact / effort / risk:

| Change | Impact | Effort | Risk |
|---|---|---|---|
| Motion-aware sampling (replace fixed sampling) | High | Low | Low |
| Preserve frame order + timestamps in prompts | Medium-High | Low | Low |
| Crop to signer / hands / face | Medium | Low | Low |
| Confidence-based fallback (flag low-confidence output) | Medium | Low | Low |
| Fingerspelling-specific handling | Medium | Medium | Low |
| Audiovisual fusion when speech also exists | Medium | Medium | Low |
| Subtitle segmentation / post-processing improvements | Medium | Low | Low |
| Preserve names/terms via glossary/context injection | Medium | Low | Low |

Full descriptions in `QUICK_WINS.md`.

## 7. Recommended immediate next experiment

**Run Baseline 0 vs. 1 vs. 2 first, on the same 5–10 videos.** Only add
Baseline 3 in the same round if a real open checkpoint is found and can be
executed without significant implementation work — otherwise run it as a
fast-follow once the landscape search resolves, not a blocker on this round.

**Why this ordering is fastest to isolate the real bottleneck:**
- If Baseline 1 ≈ Baseline 0 (no real gain from denser/adaptive sampling)
  but Baseline 2 clearly beats both → **sampling density wasn't the
  problem, motion continuity was** — points straight at Baseline 2/3
  investment, skip further sampling tuning.
- If Baseline 1 already closes most of the gap → **sampling was the main
  problem** — ship it now, deprioritize the harder baselines.
- If neither Baseline 1 nor 2 meaningfully improves on Baseline 0 →
  **the bottleneck is likely ASL specialization itself** (vocabulary,
  grammar, fingerspelling), not temporal representation — this is the
  strongest signal to invest in Baseline 3/4 rather than continuing to
  tune the generic-VLM approach.

Running all three in one round (rather than one-at-a-time sequentially)
means one batch of human review answers all three top-level unknowns from
Section 1 at once, instead of three separate review passes.

## 8. What we need from the boss/team

Concrete missing dependencies, nothing else:

- **Actual live ASL tool implementation/config**, or access to
  `curify-frontend` (or wherever the tool actually runs) — needed to make
  Baseline 0 a true reproduction rather than an assumed approximation.
- **5–10 historical user cases or privacy-safe sample IDs** — needed for
  the test set in Section 3.
- **Any internal reference transcripts** for those videos, if they exist —
  needed to make automated metrics usable at all.
- **Current model/provider/prompt/sampling settings** of the live tool —
  needed to know what "Baseline 0" and "Baseline 1" actually change,
  concretely.
- **Acceptable commercial-quality target** — needed to know what threshold
  turns a Case A/B/C result into "ship it" vs. "keep iterating."
