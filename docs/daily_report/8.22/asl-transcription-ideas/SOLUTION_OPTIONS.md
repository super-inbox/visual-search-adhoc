# Architecture Options — Baseline Comparison Framework

> **Update 2026-08-23:** Reframed around a concrete baseline ladder per
> boss-provided ground truth: the current/recent live approach is
> **Baseline 0** (frame-sampling + generic VLM), it has real SEO-driven user
> demand, and quality is currently poor / not commercially satisfactory. The
> options below are staged as incremental steps away from that live baseline
> rather than as an unordered menu, so it's clear which comparisons actually
> tell us something (see `CURRENT_VLM_BASELINE_DIAGNOSIS.md` for the
> underlying technical failure analysis and the recommended first
> experiment). This supersedes the original six-option (A–F) framing from
> the first pass of this research; those options map onto the baselines
> below and aren't repeated separately.

Grounded in current SOTA literature (see citations) and the hard cases in
`ASL_PROBLEM_FRAMING.md`.

---

## BASELINE 0 — Current: sampled-frame + generic VLM (reference point)

**How it works:** Extract a sparse set of frames from the video (per
boss-provided context, this is the current/recent live approach), pass them
to a general-purpose VLM (GPT/Gemini/Qwen-VL class) with a prompt asking it
to infer the signed meaning.

- **Likely quality improvement over itself:** N/A — this *is* the reference.
- **Implementation effort:** None (already live, per boss).
- **Inference cost:** Low-moderate — one or a few VLM calls per video.
- **Latency:** Low — a handful of API calls.
- **Open-model availability:** N/A (uses a hosted general VLM, not an
  open/specialized sign model).
- **Commercial feasibility today:** Poor, per boss — not commercially
  satisfactory quality.
- **Biggest risk:** This is exactly the architecture class the current
  SOTA literature flags as weak for continuous sign translation (see
  AttnSign, arXiv:2608.00235: general VLMs "demonstrate limited performance
  on sign language translation" without task-specific adaptation) — risk is
  that further prompt-tuning on this baseline has a low ceiling regardless
  of effort spent, because the weakness is structural (see
  `CURRENT_VLM_BASELINE_DIAGNOSIS.md`), not just a matter of a better prompt.

---

## BASELINE 1 — Denser / adaptive frame or clip sampling + current VLM

**How it works:** Same generic VLM, but increase frame sampling density
and/or switch from fixed-interval sampling to motion-aware keyframe
selection (peak hand velocity, handshape-change events), plus overlapping
sliding windows instead of independent frame grabs.

- **Likely quality improvement:** Moderate, specifically on errors caused by
  sparse-frame aliasing and transition-frame artifacts (see diagnosis doc,
  Section 2 error taxonomy); unlikely to fix direction/argument-structure,
  non-manual-grammar, or long-discourse errors, since those aren't primarily
  sampling-rate problems.
- **Implementation effort:** Low — a sampling/prompting change, no new
  model.
- **Inference cost:** Moderate increase (more frames per call, or more
  calls for overlapping windows) — still one hosted VLM, no new
  infrastructure.
- **Latency:** Slightly higher (more frames per request).
- **Open-model availability:** N/A — same hosted VLM as Baseline 0.
- **Commercial feasibility:** Plausibly still short of commercial-grade,
  but the fastest, cheapest experiment to run to find out how much of the
  current failure is sampling-rate-driven vs. structural.
- **Biggest risk:** Diminishing returns — if the dominant errors turn out to
  be grammar/discourse/vocabulary rather than motion-aliasing, this
  investment doesn't move the needle much (this is exactly what the
  recommended first experiment in `CURRENT_VLM_BASELINE_DIAGNOSIS.md` is
  designed to detect quickly and cheaply).

---

## BASELINE 2 — Video-native VLM preserving temporal information

**How it works:** Use a VLM/provider that accepts native video input (short
clips, not discrete frames) so the model itself processes motion within a
window, rather than reconstructing it from independent stills.

- **Likely quality improvement:** Moderate — preserves true motion within
  each window (fixes some transition/direction errors within-window) but
  still has no ASL-specific training and no cross-window discourse memory.
- **Implementation effort:** Low-moderate — mostly a provider/API choice
  and clip-chunking logic, not a new model to build.
- **Inference cost:** Higher than frame-based (video tokens are more
  expensive than a handful of images per most current provider pricing
  models).
- **Latency:** Moderate — video-native calls are typically slower than
  multi-image calls.
- **Open-model availability:** Depends entirely on provider; not
  self-hostable today at the open-source tier.
- **Commercial feasibility:** Better than Baseline 0/1 on motion-dependent
  errors, still capped by the same lack of ASL specialization (general VLM
  literature caveat applies here too).
- **Biggest risk:** Cost/latency scale with video length in a way frame
  sampling doesn't, and this still doesn't address non-manual grammar or
  long-discourse referent tracking — real ceiling may not be much higher
  than Baseline 1 for the effort/cost involved.

---

## BASELINE 3 — Pose/hand/face landmark temporal model

**How it works:** Extract structured keypoints (MediaPipe Holistic: hand
joints, body skeleton, face landmarks) per frame at a rate suited to signing
speed, feed the resulting coordinate sequence into a sequence model
(transformer/seq2seq) trained or fine-tuned to output English text. This is
architecturally similar to what Google DeepMind's SL2T uses (pose-landmark
coordinates → gloss-free text), which is cited here only as **validation
that this class of approach is a strong direction** — not as a dependency
Curify currently has access to (SL2T's weights/API are not available to
Curify at this time).

- **Likely quality improvement:** Potentially the largest structural
  improvement of any option that doesn't require heavy compute, *if* a
  usable open checkpoint or a viable fine-tuning path exists — directly
  targets motion/direction/transition errors by construction (the model
  input already *is* a temporal trajectory, not independent stills).
- **Implementation effort:** Moderate — pose extraction is a solved,
  off-the-shelf problem; the open question is whether a usable
  pretrained decoder exists or needs fine-tuning on open datasets
  (YouTube-ASL, How2Sign).
- **Inference cost:** Low — MediaPipe extraction is cheap CPU work; the
  decoder is a modest transformer, far cheaper than a hosted general VLM
  per video.
- **Latency:** Low — small model, no large hosted API round-trip.
- **Open-model availability:** **Unverified — this is the single biggest
  unknown in this entire research set.** No specific open ASL pose-to-text
  checkpoint has been confirmed loadable/adequate; this must be resolved by
  landscape research before committing here.
- **Commercial feasibility:** Unknown until open-checkpoint availability is
  resolved; architecturally promising, not yet proven for Curify's use case.
- **Biggest risk:** No suitable open checkpoint exists, or the ones that do
  are trained on a narrow domain (e.g., weather-report-style Phoenix data)
  that doesn't generalize to real user videos — this is a real possibility
  and must not be assumed away. **Do not treat pose/landmark modeling as
  the definitively final solution — it is one strong candidate to test,**
  contingent on what the landscape search actually finds.

---

## BASELINE 4 — RGB + pose hybrid sign-language translation model

**How it works:** Combine both signal types — a video/RGB encoder (captures
facial detail, subtle handshape, appearance cues pose-only models miss) and
pose landmarks (captures clean motion/trajectory) — fused into one
translation model, closer to the SpaMo/Sign2GPT/SSVP-SLT gloss-free
research line, which decouples spatial and motion features and feeds them
into an LLM decoder.

- **Likely quality improvement:** Potentially higher ceiling than Baseline 3
  alone, since it can recover non-manual grammar (facial detail) that pure
  pose-landmark extraction may lose or under-resolve, on top of pose's
  motion fidelity — this is the design intent of the current gloss-free SLT
  research line's best-performing systems.
- **Implementation effort:** High — requires either reproducing a research
  system or fine-tuning fusion components; no simple off-the-shelf
  integration path today.
- **Inference cost:** Moderate-high — two encoders instead of one.
- **Latency:** Moderate — more compute per video than pose-only.
- **Open-model availability:** Low — these are largely research
  checkpoints (SpaMo, Sign2GPT, SSVP-SLT), not production-ready open
  releases; reproduction effort would be substantial.
- **Commercial feasibility:** Best ceiling among self-hosted options per
  published benchmarks, but not close to a near-term prototype without
  significant research investment.
- **Biggest risk:** This is a research-reproduction project, not
  integration work — timeline and success are both uncertain, and it may
  still fall short of the SL2T-class results that motivated interest in
  this direction, since Curify would not have SL2T's ~100k-hour training
  scale.

---

## BASELINE 5 — ASL-specialized model + LLM semantic/context refinement

**How it works:** Take whichever specialized recognizer wins out (Baseline
3 or 4), and add a context-aware LLM refinement pass on top: inject
per-account/domain glossaries (names, terminology), give the LLM the whole
video's draft output at once (not per-clip) to fix discourse coherence and
referent consistency, and flag low-confidence spans for fallback.

- **Likely quality improvement:** Meaningful uplift on fluency, terminology
  correctness (especially fingerspelled names), and discourse coherence —
  but only on top of a recognizer that's already structurally sound; it
  cannot fix a recognizer that fundamentally misread the signing (risk of
  the LLM producing fluent, plausible-sounding hallucinated text if the
  underlying signal is weak — must be evaluated explicitly, not assumed
  away).
- **Implementation effort:** Low, once a base recognizer (3 or 4) is
  chosen — this is a prompting/orchestration layer, not new modeling.
- **Inference cost:** One extra LLM call per video/segment — low relative
  to the base recognizer's cost.
- **Latency:** Low addition on top of whichever base is used.
- **Open-model availability:** N/A — reuses whatever LLM Curify already
  calls elsewhere (e.g., `translation_utils.py`'s existing LLM usage
  pattern).
- **Commercial feasibility:** High-value, low-cost addition regardless of
  which base recognizer wins — should be planned as the default final stage
  in any medium-term architecture, not treated as a standalone competing
  option.
- **Biggest risk:** False confidence — a fluent refinement pass can mask a
  bad underlying transcription rather than exposing it; requires the
  omission/hallucination checks in `EVAL_PLAN.md` to catch this specifically.

---

## Summary ladder

| Baseline | Status | Quality vs. Baseline 0 | Effort | Cost/Latency | Open-model risk | Commercial feasibility |
|---|---|---|---|---|---|---|
| 0 — Sampled-frame + generic VLM | **Live today** (per boss) | reference | — | Low | N/A | Poor (current state) |
| 1 — Denser/adaptive sampling, same VLM | Proposed, testable this week | Modest, targeted | Very low | Slightly higher | N/A | Unknown, cheap to find out |
| 2 — Video-native VLM | Proposed | Modest-moderate | Low-moderate | Higher | N/A | Unknown, moderate cost to test |
| 3 — Pose/landmark temporal model | Proposed, one strong candidate (not confirmed final) | Potentially high, if checkpoint exists | Moderate | Low | **High — unresolved** | Unknown until checkpoint search resolves |
| 4 — RGB + pose hybrid | Research-heavy | Highest ceiling among self-hosted | High | Moderate-high | High | Long-horizon only |
| 5 — Specialized model + LLM refinement | Always-on final layer, not a standalone choice | Adds fluency/precision on top of 3 or 4 | Low (given a base) | Low addition | N/A | High-value regardless of base |

**How to read this table:** Baselines 1–2 are near-zero-risk experiments
that should run *this week* to find out how much of Baseline 0's poor
quality is fixable without any new model. Baseline 3 is the most promising
longer-term direction but is gated entirely on open-checkpoint availability,
which is unverified — treat it as the leading candidate to investigate, not
a foregone conclusion. Baseline 4 is a real research bet, appropriate only
if 3 proves insufficient and the business case justifies it. Baseline 5
should be planned into whichever of 3/4 gets built, regardless of outcome.

Sources consulted: VTaMo (arXiv:2607.09126), MSKA-SLT / Phoenix-2014T &
CSL-Daily benchmarks, SignMusketeers (arXiv:2406.06907), Sign2GPT /
SSVP-SLT / SpaMo (gloss-free SLT survey line, ACL 2025 NAACL-long.197,
arXiv:2403.12556), AttnSign (arXiv:2608.00235) on generic-VLM limitations
for SLT, How2Sign dataset (how2sign.github.io), YouTube-ASL
(ACM DL 3666122.3667386), and Google DeepMind's SL2T announcement
(deepmind.google/blog/putting-sign-language-ai-into-users-hands, Aug 2026) —
cited strictly as architectural validation, not as an available dependency.
