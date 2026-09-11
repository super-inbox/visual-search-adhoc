# Phase D1 (POC design) + D2 (experiment design) — Trajectory Tracking

**Date:** 2026-09-10. Design/proposal only — **nothing in this document has been
installed, run, committed, or pushed.** No Gemini calls. `curify-studio` untouched.
See `PHASE_D0_RESEARCH_AND_AUDIT.md` for the research/audit this builds on.

---

## Phase D1 — Minimal trajectory-inspection POC

**Question this POC answers, and only this question:** *"Can we reliably recover useful
continuous hand/body trajectories from the same videos where our frame-based translator
fails?"* It does not attempt ASL translation. No model is trained. No Gemini call is made.

### D1.1 — Exact clips (5 of the diagnostic-12, chosen for coverage, not cherry-picked for a favorable result)

| clip_id | duration_s | why chosen |
|---|---|---|
| `92V3oH63zbQ_5-1-rgb_front` | 1.83 | Shortest clip; **both** the frame-baseline and native-video Gemini predictions were completely empty on this clip. If a tracker can recover a clean, continuous trajectory here, it tells us the text-model failure is not "there was nothing to see" — a sharp, falsifiable test. |
| `Fz-N1S0swh8_2-8-rgb_front` | 2.27 | Tagged `fast_signing` + `fingerspelling_candidate`; frame-baseline collapsed to a single wrong word ("Angry"). Stress-tests whether the tracker keeps up with fast/fine motion at the short end. |
| `-g0iPSnQt6w_0-1-rgb_front` | 3.51 | Tagged `fingerspelling_candidate` + `question`; also this session's prepared (not-yet-executed) native-video retry candidate's sibling in the 8-blocked set — independent of that blocker since trajectory extraction never touches Gemini. |
| `G19uBylwQww_1-2-rgb_front` | 4.53 | Richest combined heuristic tags (`number_token` + `fingerspelling_candidate` + `fast_signing`) and the *least bad* frame-baseline WER (0.8077) in the whole diagnostic-12 — useful contrast case. |
| `FzmL8SL6Bow_1-8-rgb_front` | 25.77 | Longest diagnostic clip; already has the deepest existing cross-referenced artifact trail (frame-baseline inspector page, Uni-Sign prediction, native-video Stage-1 result). Tests tracker robustness over a long multi-batch-boundary clip and lets every new trajectory artifact be viewed side-by-side with everything we already have on this one clip. |

Total: ~38s of video, small enough to run and review in minutes once the tracker is set up.

### D1.2 — Tracker

**RTMPose via `rtmlib`** (see D0 §5). Concretely: re-fetch just the `rtmlib` package
(pinned to the same `0.0.13` release already validated) into the existing
`unisign-cpu-arm64` conda env — the heavy dependencies (`onnxruntime`, `opencv-python`,
`decord`, `torch`) are already installed and confirmed importable in that env; nothing
else needs touching. Use `rtmlib`'s `Wholebody` detector (COCO-WholeBody, 133 keypoints:
17 body + 6 foot + 68 face + 21×2 hand), the same detector Uni-Sign's own pipeline already
used to process this exact video corpus successfully.

**Not part of D1 execution yet** (this is a design document): the actual `pip`/`git`
re-fetch of `rtmlib` is an install step, explicitly out of scope per "do not install
anything yet."

### D1.3 — Extracted signals

Per frame, per tracked point, from the raw COCO-WholeBody output:
- Left/right wrist position (x, y, confidence)
- Left/right hand-center position (mean of the 21 hand keypoints per hand, confidence-weighted)
- All 21 per-hand finger keypoints (kept raw; reliability assessed in D1.6, not assumed usable)
- Shoulder/chest/nose position (body reference points, for relative-position signals)
- Optional: coarse face-contour points from COCO-WholeBody (not a dedicated face mesh — flagged low-confidence per D0 §6)

Derived, per clip, from the raw per-frame points:
- Wrist/hand-center velocity and acceleration (finite difference over time, in normalized-frame units/second — not pixels, so it's resolution-independent)
- Motion direction (angle of the velocity vector) per hand
- Pause/hold detection: contiguous spans where a hand's speed stays below a small threshold for ≥N frames
- Repetition detection: simple periodicity check on the hand-center trajectory (autocorrelation peak) — flagged as a heuristic, not a claim of linguistic repetition
- Two-hand relative position: vector and distance between left and right hand-centers over time
- Hand-to-body relative position: each hand-center's position relative to shoulder midpoint / nose (face-adjacent vs. chest-height vs. below-waist bands)
- Missing-tracking percentage: fraction of frames where a given point's detection confidence falls below a fixed threshold (this is the single most important quality signal — see D1.6)

### D1.4 — Trajectory data schema

`trajectory_probe/<clip_id>/landmarks.json` — raw per-frame output, one row per frame:

```json
{
  "clip_id": "92V3oH63zbQ_5-1-rgb_front",
  "tracker": "rtmlib.Wholebody",
  "tracker_version": "rtmlib==0.0.13",
  "model": "<exact RTMPose ONNX model name/checksum used>",
  "source_video": "asl-translator/data/public_benchmarks/how2sign_v2/videos/92V3oH63zbQ_5-1-rgb_front.mp4",
  "fps_extracted_at": 24.0,
  "frame_width": 1280,
  "frame_height": 720,
  "frames": [
    {
      "frame_idx": 0,
      "t_s": 0.0,
      "keypoints": {
        "left_wrist":  {"x": 0.412, "y": 0.531, "conf": 0.91},
        "right_wrist": {"x": 0.588, "y": 0.540, "conf": 0.89},
        "left_hand":   [{"x": 0.40, "y": 0.53, "conf": 0.9}, "...21 points..."],
        "right_hand":  [{"x": 0.59, "y": 0.54, "conf": 0.9}, "...21 points..."],
        "nose": {"x": 0.50, "y": 0.20, "conf": 0.97},
        "left_shoulder": {"x": 0.45, "y": 0.35, "conf": 0.95},
        "right_shoulder": {"x": 0.55, "y": 0.35, "conf": 0.95},
        "face_contour": ["...optional, low-confidence flag if used..."]
      }
    }
  ]
}
```

`trajectory_probe/<clip_id>/trajectory_summary.json` — the derived signals, small enough
to read at a glance and to later hand to Gemini as structured text (D2):

```json
{
  "clip_id": "92V3oH63zbQ_5-1-rgb_front",
  "duration_s": 1.83,
  "n_frames_extracted": 44,
  "missing_tracking_pct": {"left_wrist": 4.5, "right_wrist": 0.0, "left_hand": 6.8, "right_hand": 2.3},
  "mean_confidence": {"left_wrist": 0.88, "right_wrist": 0.93},
  "wrist_velocity_summary": {
    "left": {"mean": 0.12, "max": 0.41, "unit": "normalized_frame_widths_per_s"},
    "right": {"mean": 0.15, "max": 0.38, "unit": "normalized_frame_widths_per_s"}
  },
  "pauses_detected": [{"hand": "right", "start_s": 0.9, "end_s": 1.1}],
  "repetition_score": {"left": 0.12, "right": 0.31, "note": "heuristic autocorrelation peak, not a linguistic claim"},
  "two_hand_distance_summary": {"mean": 0.22, "min": 0.05, "max": 0.38, "unit": "normalized_frame_width"},
  "hand_relative_to_body_band": {
    "left":  {"face_pct": 10, "chest_pct": 70, "below_pct": 20},
    "right": {"face_pct": 5,  "chest_pct": 80, "below_pct": 15}
  }
}
```

### D1.5 — Visualization

`trajectory_probe/<clip_id>/trajectory_overlay.mp4`: the source clip re-encoded with
skeleton/keypoint overlay drawn per frame (standard `rtmlib`/OpenCV draw utilities — no
new visualization code needed beyond a thin wrapper), plus a small trailing-path overlay
(last ~15 frames of each hand-center, faded) so continuous motion is visible in a still
frame, not just in playback. Given effort constraints, an acceptable cheaper fallback
(matching this repo's existing inspector pattern, which already uses static JPEG
thumbnails rather than embedded video — see `build_inspector.py`) is a **static trajectory
plot**: hand-center x/y paths over time as an SVG/PNG, in the same visual language as the
existing inspector's motion-timeline SVG. (Note, added post-run: where an overlay `.mp4`
was produced, it was used only as a local, one-off visual QA aid during review and is
intentionally not part of the committed deliverable — the static SVG plot, `landmarks.json`,
and `trajectory_summary.json` are the committed per-clip outputs.) Recommend building the
static plot first (cheap, reuses the existing SVG-rendering approach in `build_inspector.py`)
and only building the
overlay `.mp4` if the static plot leaves open questions the team needs to see in motion.

`trajectory_probe/<clip_id>/QA.md`: one short per-clip write-up — missing-tracking %,
any visibly wrong tracking (e.g. hand fully occluded, tracker locking onto the wrong
object), and a plain-language one-paragraph read of what the trajectory shows, written by
whoever reviews it (not auto-generated commentary).

### D1.6 — Tracking-quality checks (must pass before D2 is worth running)

- **Missing-tracking percentage** per hand, per clip: report explicitly; do not silently
  interpolate over gaps in a way that hides them.
- **Confidence distribution**: histogram or summary stats of per-keypoint confidence;
  flag any clip where mean hand confidence falls below a fixed floor (e.g. 0.5) as
  unreliable for that clip, not silently included in aggregate numbers.
- **Sanity check against video**: for at least 2 of the 5 clips, a human (not
  ASL-fluent — same caveat as this project's existing text-semantic reviews) watches the
  overlay/plot next to the source video and confirms the tracked hand positions visually
  match, at a coarse level (tracker is on a hand, not on a shirt cuff or the background).
- **Frame-count consistency**: extracted frame count should match `ffprobe`'s own frame
  count for that clip (within the same class of rounding tolerance already documented for
  the existing motion-probe/frame-budget mismatch in `build_inspector.py`) — a large
  mismatch would indicate a decoding problem, not a tracking-quality problem, and should
  be diagnosed separately before trusting any derived signal.

### D1.7 — Failure criteria (explicit, falsifiable — not everything need succeed for D2 to proceed, but these must not happen)

**D1 fails / do not proceed to D2 if, on the 5-clip probe:**
- Missing-tracking percentage for either hand exceeds ~30% on more than 2 of the 5 clips
  (i.e. the tracker frequently cannot find the signer's hands at all on this video style —
  How2Sign is a controlled studio-style corpus, so this would be a genuine surprise, but
  must be checked, not assumed).
- The human sanity check finds the tracked points are not actually on the signer's
  hands/body on a majority of spot-checked frames (tracker locking onto background/wrong
  person/clothing).
- Extraction throughput is so slow that even a 5-clip probe cannot complete in a
  reasonable local session (the D0 reference point — 11.8s for 263 frames — suggests this
  is very unlikely, but it's a real go/no-go check, not an assumption).

**D1 passes (proceed to D2 design execution) if:** missing-tracking stays low
(rough target: <15% per hand across the 5 clips, allowing brief real occlusions), the
human sanity check confirms visually correct tracking, and at least the short/fast clips
(`92V3oH63zbQ`, `Fz-N1S0swh8`) show a plausible, non-degenerate trajectory (i.e. the
tracker isn't just returning a static or clearly-wrong point every frame).

### D1.8 — Inspector integration (additive only, matching the pattern already used for Uni-Sign/native-video)

Exactly the same pattern established earlier this session for adding Uni-Sign and
native-video predictions to `build_inspector.py`: read-only, no rerun of anything else,
new blocks appended to each existing clip page, nothing existing removed or reflowed.
Proposed additions per page (only for the 5 clips that have a trajectory probe — every
other page unaffected):
- A new `<h2>Trajectory probe (RTMPose)</h2>` section containing: the missing-tracking %
  summary, the static hand-path plot (same inline-SVG technique `render_timeline_svg`
  already uses, so no new rendering dependency), and a link to
  `trajectory_probe/<clip_id>/QA.md`.
- On `index.html`: one new column, "trajectory probe," showing "done ✓" / "not run" per
  clip (only 5 of 12 will show "done" — explicitly not implying full-corpus coverage,
  mirroring how the native-video column already handles partial coverage — 4/12 at plan
  time, 5/12 as of the Stage-3 retry documented in `BLOCKER_STATUS.md`).

---

## Phase D2 — Experiment design only (NOT executed; no training; no Gemini calls)

**Only proceed to actually running this if D1's failure criteria (§D1.7) are not
triggered.**

### D2.1 — Question

Does giving Gemini structured, trajectory-derived observations **in addition to** its
existing video/frame input change semantic outcomes, on the same clips where video/frame
input alone already fails?

### D2.2 — Design: inference-side only, two arms, same clips/references/scoring already established

- **Arm A (control):** whatever input formulation is already frozen and comparable —
  reuse the existing frame-baseline (`evaluation_2026_09_04_gemini_3_6`) or native-video
  predictions already on disk for the same clips. No new Gemini call needed for this arm.
- **Arm B (treatment):** the *same* input as Arm A, **plus** a short structured-text block
  derived from `trajectory_summary.json` appended to the prompt — e.g. "Left hand: mostly
  chest-height, moved rightward then paused for 0.2s at t=0.9s. Right hand: ..." Exact
  phrasing to be designed once D1's real summaries exist (do not pre-write ASL-specific
  interpretive labels — D1.4's schema is intentionally raw kinematic description, not
  gloss/handshape guesses, per the manager's "do not invent ASL-specific visual labels"
  constraint already established this session for the inspector).
- Only the diagnostic-12 clips that both (a) have a trajectory probe passing D1.6/D1.7 and
  (b) already have a comparable Arm-A prediction on disk are eligible — likely the 5 D1
  clips plus any of the other 7 once/if the probe is extended.
- Scoring: identical conservative semantic-adequacy method already used for native-video
  Stage 1/2 (reference-topic-recovered yes/no; semantic adequacy
  completely-wrong/partially/mostly/fully-correct), applied blind to condition, same
  reviewer process as the existing 40-clip taxonomy review.

### D2.3 — Proposed internal POC heuristic, NOT a manager-prescribed gate

**Correction from an earlier draft of this document:** the ≥3/12 semantic-recovery bar
and its rejection counterpart were manager-authored specifically for the native-video
experiment (source spec §7 P0-4). No manager text defines an equivalent gate for
trajectory tracking. The numbers below are this session's own **proposed internal POC
heuristic** — offered only because *some* falsifiable bar is needed to avoid an
open-ended experiment, and because reusing a shape the manager has already seen keeps the
process legible — but they carry no manager authority until reviewed and either approved
or replaced. If D2 is actually run, the manager should confirm or amend this bar first.

- **Proposed promotion heuristic:** ≥3 of the eligible clips move `semantic_adequacy`
  0→≥1, OR `reference_topic_mismatch` flips yes→no on ≥3 of the eligible clips —
  structurally the same shape as the native-video P0-4 gate, chosen for methodological
  consistency, not because the manager specified this number for this direction.
- **Proposed rejection heuristic:** 0 flips AND any WER movement stays inside the
  already-established decoding-noise floor (mean |delta| 0.029–0.107, per the source
  spec's §12.2, already cited in this session's native-video `run_metadata.json`) →
  record as inconclusive/not promising and do not scale further, pending manager review.

### D2.4 — Why inference-side, not training, and why this is the smallest version

No model weights are touched. No new architecture. The only new artifact Gemini receives
is a short text block — this isolates "does structured motion information help a general
VLM reason about signing" from every confound a trained skeleton encoder (like Uni-Sign's)
already carries (different decoder, different training data, different failure modes
entirely). If this smallest, cheapest version shows no effect, there is no basis for
jumping to a heavier bet (e.g. a fused video+skeleton model, or dual-stream training).

---

## Deliverables (summary, cross-referenced from D0 for the full detail)

1. **Gap analysis vs. work already done** — see `PHASE_D0_RESEARCH_AND_AUDIT.md` §2–4:
   motion-energy sampling (tested, exhausted, and *not* the same axis) vs. trajectory
   tracking (untested for Gemini, but a close cousin — Uni-Sign — already proves
   RTMPose extraction is reliable on this exact corpus/machine).
2. **Tracker candidate comparison** — D0 §5: RTMPose via `rtmlib` (primary, proven
   locally) vs. MediaPipe Holistic/Tasks API (fallback, likely easy but unverified this
   session) vs. MMPose/ViTPose full framework (not recommended, same weights reachable
   more cheaply through `rtmlib`).
3. **Recommended POC** — D1 above: 5 named clips, RTMPose/`rtmlib`, the schema in D1.4,
   additive inspector integration, explicit quality checks and failure criteria.
4. **Exact implementation files to add** (none created yet — this is the proposed set):
   - `asl-translator/asl-eval/trajectory_probe/extract_trajectory.py` — runs `rtmlib`
     Wholebody over one clip, writes `landmarks.json` (uses the existing
     `unisign-cpu-arm64` env; no changes to any file outside this new module)
   - `asl-translator/asl-eval/trajectory_probe/summarize_trajectory.py` — reads
     `landmarks.json`, computes D1.3's derived signals, writes `trajectory_summary.json`
   - `asl-translator/asl-eval/trajectory_probe/render_overlay.py` — writes the static
     hand-path plot (and optionally `trajectory_overlay.mp4`)
   - `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/trajectory_probe/<clip_id>/{landmarks.json,trajectory_summary.json,trajectory_plot.svg,QA.md}` —
     per-clip outputs for the 5 named clips, committed to the repo. A `trajectory_overlay.mp4`
     was additionally produced for one clip as a local visual QA aid only and is
     intentionally excluded from the committed deliverable (see D1.5 note above).
   - Additive changes only (no function bodies removed) to
     `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/inspector/build_inspector.py`
     for the new trajectory section (D1.8) — same pattern as this session's Uni-Sign/
     native-video additions
   - A new `run_trajectory_diagnostic_experiment.py` (D2 only, not built until D1 passes)
     mirroring `run_native_video_how2sign_v2_benchmark.py`'s CLI-gate conventions
     (`--plan-only`, `--run`, `--acknowledge-private-data-upload`, `GEMINI_API_KEY`
     required) for Arm B's Gemini calls
5. **Expected effort:**
   - `rtmlib` re-fetch + smoke test on 1 clip: well under an hour (heavy deps already
     proven working; this is a small, self-contained package)
   - D1 5-clip extraction + summaries + static plots: a few hours, given the 11.8s/clip
     reference extraction time and the need to hand-review each clip's QA
   - D1 inspector integration: comparable to this session's Uni-Sign/native-video
     inspector work (~1 focused session)
   - D2 (only if D1 passes): prompt design + a small number of real Gemini calls on the
     eligible clips — comparable in size to this session's native-video Stage 1/2, i.e. a
     few Gemini calls, gated the same way (`--acknowledge-private-data-upload`,
     explicit approval per stage)
6. **Risks:**
   - `rtmlib` re-fetch might not be a clean drop-in (version drift, a since-changed
     upstream repo) — mitigated by pinning to the exact `0.0.13` version already proven
     and by MediaPipe as a documented fallback
   - RTMPose's WholeBody face keypoints are coarse; if facial/non-manual signal turns out
     to matter, a dedicated face model would be a separate follow-up, not assumed solved
     by this POC
   - Fingerspelling-relevant fine finger detail may exceed RTMPose's resolution at 1280×720
     source video — this is exactly what D1.6's tracking-quality checks are designed to
     surface before any claim is made
   - D2's structured-text-block phrasing risks smuggling in interpretive (ASL-gloss-like)
     claims if not kept strictly kinematic — explicitly constrained in D2.2 for this reason
7. **Evidence that would justify a larger bet:** D1 passes cleanly (low missing-tracking,
   visually correct tracking, non-degenerate trajectories even on short/fast clips) **and**
   D2 clears the proposed internal POC heuristic in §D2.3 (≥3/N clips flip semantic
   category) — a heuristic shaped like the native-video P0-4 gate for consistency, not a
   manager-issued bar for this direction; the manager should confirm or amend it before
   it's treated as a real decision gate.
8. **Evidence that would reject/deprioritize this direction:** either D1 fails its
   tracking-quality criteria (§D1.7 — the representation itself isn't recoverable
   reliably from this video corpus, independent of any downstream model), or D1 passes but
   D2 hits the proposed rejection heuristic in §D2.3 (the representation is recoverable but doesn't
   move Gemini's semantic output) — in which case trajectory-as-context joins the other
   axes already tested and exhausted (temporal sampling, batching, native video), and the
   manager should be told plainly that three genuinely different representational/temporal
   axes have now been tried without semantic recovery, which is itself a significant,
   reportable finding about where the bottleneck likely is (upstream of input formulation
   — possibly the decoder/language-model side, or a training-data/domain gap — not
   something a from-scratch retest of another input-formulation variant is likely to fix).
