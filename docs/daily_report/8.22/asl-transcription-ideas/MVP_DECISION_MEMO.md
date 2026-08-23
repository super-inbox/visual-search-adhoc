# ASL MVP — Decision Memo

> **Revised 2026-08-23** per boss-provided ground truth received after the
> initial draft of this memo. See `CURRENT_APPROACH_GAPS.md` for the full
> reconciliation between repo-observed evidence and boss context.

## 1. Current state (reconciled)

- **Repo-observed (Tier A):** the general-purpose dubbing pipeline
  (`has_speech()` → ElevenLabs Scribe) explicitly treats silent/sign-language
  video as a no-speech input and skips it. No frame-sampling or VLM code
  exists anywhere in `curify-studio`.
- **Boss-described (Tier B), higher authority for what's actually live:**
  the dedicated ASL tool uses **frame extraction/sampling → generic VLM →
  inferred sign meaning**, has real, meaningful SEO-driven user demand, and
  its quality is currently poor / not commercially satisfactory. This tool
  most plausibly lives in `curify-frontend` (registry routes are defined
  there, per `docs/tool-inventory.md`), a separate repo not accessible in
  this research pass.
- **Both are true simultaneously:** the `has_speech()` gate applies to a
  different code path than the one actually serving ASL users today. The
  MVP problem is therefore not "make an automated path exist" — one already
  does — it's **"raise the quality of the existing live baseline (Baseline
  0) toward commercial-grade."**
- The existing downstream subtitle/translation/voiceover pipeline
  (`subtitle_utils.py`, `alignment_utils.py`, `translation_utils.py`,
  `voiceover_utils.py`) remains reusable as-is regardless of which
  recognition approach is used.

## 2. Recommended MVP

Improve the live baseline in place, rather than building a parallel path:

```
video
  → signer detection/cropping
  → denser / motion-aware frame sampling (Baseline 1) — replacing whatever
    fixed-interval sampling the live tool currently uses
  → current VLM, with ASL-aware prompting + self-consistency confidence flagging
  → LLM refinement pass: glossary injection, whole-video context (Baseline 5)
  → existing subtitle segmentation/alignment
  → SRT/VTT
```

In parallel: search for a usable open pose-based checkpoint (Baseline 3) to
evaluate as a potential medium-term replacement for the VLM recognition
step, contingent on what the search finds.

## 3. Why this direction

- **Targets the actual diagnosed weakness:** sparse, fixed-interval frame
  sampling into a generic VLM loses motion, direction, and non-manual
  grammar signal — denser/motion-aware sampling and ASL-aware prompting
  directly address the mechanisms in `CURRENT_VLM_BASELINE_DIAGNOSIS.md`,
  without requiring a new model.
- **Cheapest path to a measurable answer:** modifying the live tool's
  sampling/prompting is far lower effort than building a new pipeline, and
  tells us quickly how much of the current poor quality is fixable this way.
- **Pose/landmark modeling (Baseline 3) is a strong candidate for the next
  step, not assumed final:** its architecture is validated at scale by
  Google DeepMind's SL2T (Aug 2026) — cited only as evidence the *approach
  class* (pose-landmark coordinates → text) is sound. **SL2T's weights and
  API are not currently available to Curify**; this is architectural
  validation, not an available dependency.
- **Compatible with the current downstream pipeline:** whichever
  recognition approach wins, everything from English text onward is
  unchanged.

## 4. Immediate experiment

Run **5–10 real ASL videos** through, per `EXPERIMENT_PRIORITY.md`:

- **Baseline 0 (control)** — the current live approach, unmodified, to
  establish the reference failure rate and error-type distribution.
- **Baseline 1** — same VLM, denser/motion-aware sampling — isolates
  whether the dominant failures are sampling-rate/aliasing artifacts.
- **Baseline 2** — video-native VLM input, preserving temporal continuity —
  isolates whether motion continuity itself, not just sampling density, is
  the bottleneck.
- **Baseline 3, added to the same round only if a real, loadable checkpoint
  is found without significant implementation work** — MediaPipe Holistic
  pose extraction feeding a candidate open sign-translation checkpoint.
  Skipped this round if no such checkpoint exists — not simulated.

Score all runs with the shared error taxonomy in
`CURRENT_VLM_BASELINE_DIAGNOSIS.md` §2 / `EVAL_PLAN.md`.

## 5. Decision gate

- **If Baseline 1 closes most of the gap versus Baseline 0** → the fix is
  cheap; ship the improved sampling/prompting to the live tool and treat
  further specialized-model work as lower priority.
- **If Baseline 2 materially beats Baseline 1** → motion continuity, not
  sampling density, is the real bottleneck; prioritize a video-native VLM
  path over further sampling tuning.
- **If Baseline 3 is available this round and clearly beats Baseline 2 with
  acceptable latency/cost** → prototype the full pose-based ASL routing
  path as the medium-term recognition engine (`app/utils/asl_utils.py` + a
  thin pipeline wrapper).
- **If no baseline approaches commercial quality** (including no usable
  open checkpoint for Baseline 3) → keep the best-performing near-term
  approach as a clearly labeled best-effort option, and consider
  specialized fine-tuning, a model partnership, or a proprietary-data
  strategy as the next-tier decision — a business call, not a purely
  technical one.

## 6. Biggest unknowns

- **Open checkpoint availability** — whether any pose-to-text or
  video-to-text ASL model is actually loadable and good enough today; this
  is the single largest unresolved unknown in the whole research set.
- **The live tool's actual current implementation** — exact sampling rate,
  prompt, and VLM provider are not verifiable from this research pass since
  the code most plausibly lives in `curify-frontend`, which was
  inaccessible here.
- **Real user-volume distribution** — SEO traffic and "many users trying
  it" are confirmed qualitatively; exact volume and failure-rate at scale
  are not yet quantified.
- **Subtitle timestamp quality** — whether any candidate recognition
  approach can emit segment boundaries accurate enough for the existing
  alignment step to produce usable SRT/VTT timing.
- **Fingerspelling accuracy** — the most commonly cited failure mode for
  any candidate model, and the case most likely to break names/terms that
  matter most to users.
