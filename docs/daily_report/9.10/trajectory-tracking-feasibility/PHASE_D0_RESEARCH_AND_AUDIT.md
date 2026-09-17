# Phase D0 — Trajectory-Tracking Direction: Research & Audit

**Date:** 2026-09-10
**Scope:** Research/audit only. No installs, no Gemini calls, no code changes to the
evaluation pipeline, no commits. Read-only inspection of this repo's git history/docs and
of two already-installed local conda environments (`openslt-cpu-arm64`,
`unisign-cpu-arm64`) that predate this session.

**Framing correction, stated precisely (per explicit instruction):** Trajectory
representation is **genuinely new for the Curify/Gemini pipeline specifically** — no
pose/keypoint/trajectory code exists anywhere in `run_current_model.py` or
`run_native_video.py`, and Gemini has never been given any structured motion signal in
any experiment run on this branch. It is **NOT new across our benchmarked systems as a
whole**, because **Uni-Sign — already one of our 4 scored systems — is itself built on
RTMPose-extracted skeleton keypoints** (see §4 below). These are two different claims and
must not be conflated: "new to Curify/Gemini" is true; "new to this project" is not. §4
spells out exactly what Uni-Sign's existing pipeline already proves and what it does not.

## 1. Manager's direction, restated precisely

The manager saw a CV tennis example where raw video is converted into **structured,
continuous spatiotemporal trajectories** (ball/body path, velocity, etc.) and is asking
whether an analogous representation — explicit, continuous hand/body/face tracking over
time, not just still frames — could help ASL recognition. Candidate signals listed:
wrist/hand-center trajectories, finger/hand landmarks, motion direction, velocity/
acceleration, pauses/repetitions, two-hand relative position, hand-relative-to-body
location, body/pose trajectory, optional facial/non-manual keypoints. The manager
explicitly does not assume trajectory alone is sufficient — handshape, orientation,
fingerspelling, non-manual markers, and language context still matter.

## 2. Audit of the existing pipeline and previous temporal experiments

Three prior experiments (all on this branch, all already scored) varied **when** Gemini
looks, never **where** or **what structure** it's given:

| Experiment | Axis varied | Mechanism | Result |
|---|---|---|---|
| Motion-weighted vs. uniform sampling | which discrete frame *timestamps* get chosen | `allocate_timestamps()` — a scalar per-probe-frame "motion energy" (mean abs. grayscale pixel diff, whole-frame, no spatial localization) biases frame density toward high-energy time spans | No semantic recovery (`docs/daily_report/9.9/.../WORK_REPORT.md` §7) |
| ~2fps vs. ~8fps sampling density | how many discrete frames | Same scalar motion-energy signal, denser budget | No semantic recovery (§6) |
| Independent vs. overlapping/sliding-window batches | how frames are grouped into model calls | Batch boundary logic in the frame driver | WER moved, semantics did not (§8) |
| Native/direct video input (this session, Stage 1–2) | whole `.mp4` via Files API vs. sampled JPEGs | No sampling at all — Gemini sees the raw video stream itself | 4/12 scored as of Stage 1–2, 0/4 semantic recovery (same failure class); updated to 5/12 scored, 0/5 semantic recovery after a Stage-3 retry recovered one more clip — see `docs/daily_report/9.10/asl-native-video-evaluation/BLOCKER_STATUS.md`. The conclusion (no semantic recovery) is unchanged. |

The motion-energy signal (`run_current_model.py:probe_motion`, lines 324–351) is: decode
the clip at low resolution/grayscale/reduced fps, take the mean absolute pixel difference
between consecutive frames, and use that **one scalar per timestep** to decide which
whole-frame timestamps to keyframe. It has **no concept of a hand, a wrist, a body part,
or a spatial coordinate** — it cannot say *where* the motion is, only *when* motion (of any
kind, anywhere in frame, including camera noise, clothing, or background) exceeds a
quantile threshold.

## 3. Is trajectory tracking technically distinct from the motion-energy sampler? Yes — precisely why

| | Motion-energy sampler (already tested) | Trajectory tracking (manager's new proposal) |
|---|---|---|
| Output type | One scalar per timestep (frame-level "how much changed") | A structured per-landmark time series: `(x, y, [z], confidence)` per joint/keypoint, every frame |
| Spatial localization | None — cannot distinguish a hand moving from a shirt fluttering | Explicit — each point is tied to a named body part (left wrist, right index fingertip, nose, etc.) |
| What it changes | *Which* still frames Gemini sees (temporal sampling policy) | *What* Gemini (or another model) is given *in addition to* frames — a new, structured input modality |
| Consumable derived signals | None beyond "was there motion in this window" | Velocity, acceleration, direction, pause/hold detection, two-hand relative position, hand-to-face/chest distance, repetition detection — all per named part |
| Prior test coverage | Adaptive vs. uniform (Section 7), 2fps vs. 8fps (Section 6) — both exhausted, no effect | **Zero prior test coverage** — confirmed by code search: no pose/hand-detection/keypoint code exists anywhere in `run_current_model.py`, `run_native_video.py`, or any evaluation driver in this repo |

**Conclusion: these are not the same axis measured twice.** The motion-energy experiments
already falsified "does biasing *which frames* Gemini sees toward motion help" — that
question is closed (§6–8 results). The manager's new proposal is a different question:
"does giving the model explicit *structured spatial* information about hands/body over
time help" — an axis this project has not touched. `docs/daily_report/9.9/.../WORK_REPORT.md`
§11 independently reached the same conclusion before this task existed, filing
"Pose/mouthing/multi-channel recognition" as **GENUINELY NEW** (no pose/channel-fusion
code exists) and "Hand-specific velocity/direction/pause detection" as only
**PARTIALLY IMPLEMENTED** (the *mechanism class* — motion-weighted density — exists; the
*signal* is coarse and non-spatial; refining the temporal-sampling axis further is
unproven, exactly because two separate ablations on that axis already failed).

## 4. Major finding: this repo already has direct, proven local evidence bearing on this question

This is not a cold start. **Uni-Sign — already one of the 4 systems in our own
scorecard — is itself a trajectory/keypoint-based ASL architecture**, and it was already
built, run, and scored end-to-end on this exact machine:

- Architecture (`docs/daily_report/8.31/asl-next-baseline/SECOND_BASELINE_CANDIDATES.md`):
  raw video → **RTMPose-extracted 2D skeleton keypoints (body, hands, face — COCO-WholeBody,
  133 points/frame)** → a graph/temporal skeleton encoder → an mT5-base decoder producing
  English text. This is explicit continuous skeletal motion over time, the closest existing
  artifact to "trajectory representation" already in this project.
- **It was successfully run on all 128 How2Sign v2 clips** (`asl-translator/evaluation/results/how2sign_v2/unisign/`,
  already one of our 4 comparison systems), including all 12 diagnostic clips.
- Confirmed still on disk on this machine: a working conda environment,
  `unisign-cpu-arm64`, with `rtmlib==0.0.13` (metadata), `onnxruntime==1.23.2`,
  `opencv-python==4.10.0.84`, `decord==0.6.0`, and `torch==2.1.1` genuinely importable —
  verified live this session (`onnxruntime.get_available_providers()` even lists
  `CoreMLExecutionProvider`, i.e. Apple Neural Engine/GPU acceleration is available, not
  just CPU).
- One real caveat found: `rtmlib` itself is installed **editable**, pointing at a
  session-scratchpad path (`/private/tmp/.../unisign_run/repo/demo/rtmlib-main/rtmlib`)
  that no longer exists (that scratchpad was cleaned up after the prior session ended). So
  the *heavy* dependencies (onnxruntime, opencv, decord, torch — the parts with historical
  Apple-Silicon wheel friction, see §5) are genuinely installed and working; only the thin
  `rtmlib` wrapper package itself (a small, self-contained ONNX-inference wrapper around
  RTMPose, not a heavy framework) needs to be re-fetched.
- Documented, concrete performance number for pose extraction alone (no decoder):
  **11.8s to extract 133 COCO-WholeBody keypoints/frame across 263 frames** of a 5.27s
  clip (`docs/daily_report/8.31/asl-next-baseline/NEXT_EXPERIMENT_PLAN.md`) — extraction
  is fast; the 74s total end-to-end time in that test was dominated by mT5 decoding
  (~46s), which a trajectory-only probe would not need at all.

**What this means for the manager's question:** Uni-Sign's own WER (0.9480 corpus-wide,
19-clip run; individual diagnostic-12 WERs already in our inspector, ranging 0.5–2.07) is
*suggestive* but **not a clean answer** — it swaps the entire architecture and decoder
(mT5 instead of Gemini) at the same time it swaps the input representation, so a WER
difference vs. the Curify frame baseline cannot be attributed to "trajectory information"
specifically. It does, however, already prove two things empirically on this exact
machine and this exact corpus: (a) RTMPose keypoint extraction from our How2Sign clips
is technically reliable at 100% success (19/19, then scaled further), and (b) skeleton-only
input, decoded by a *different* language model, does not obviously solve the semantic
failure either — Uni-Sign's one-clip qualitative result shows the same failure class
(fabricated unrelated topic, here with a 4x repetition loop) as the Gemini frame baseline.
This argues for treating trajectory info as a **candidate additional signal to test
inference-side with Gemini specifically** (Phase D2), not as a reason to expect an easy
win — consistent with the manager's own caveat that trajectory alone is not assumed
sufficient.

## 5. Tracker candidates for a fresh probe — comparison

| Candidate | Raw video in | Continuous per-frame keypoints | Hands | Body | Face | macOS/arm64 local feasibility | Pretrained, no training | Verdict |
|---|---|---|---|---|---|---|---|---|
| **RTMPose via `rtmlib`** | Yes (`rtmlib` wraps ONNX Runtime, reads frames directly) | Yes | Yes (21 pts/hand) | Yes (body) | Optional (COCO-WholeBody face contour, coarser than dedicated face models) | **Proven on this exact machine** — heavy deps (onnxruntime, opencv, decord, torch) already genuinely installed and importable in `unisign-cpu-arm64`; only the thin `rtmlib` wrapper needs re-fetching (small pip/git package, not a framework) | Yes — pretrained ONNX RTMPose models, no training | **Primary recommendation** — lowest incremental risk, only untested component is a small wrapper re-fetch |
| **MediaPipe (Tasks API — `HolisticLandmarker`, 543 landmarks combining pose+hand+face)** | Yes | Yes | Yes (21 pts/hand) | Yes (33-pt pose) | Yes (dedicated face mesh, denser than RTMPose's face) | Not installed in this repo/session. Per current web search: official `mediapipe` PyPI wheels now ship native arm64 builds (e.g. `mediapipe-1.0.1-py3-none-macosx_11_0_arm64.whl`) — `pip install mediapipe` is expected to work directly on this Mac without the older `mediapipe-silicon` workaround, but this has **not been verified locally this session** (nothing installed) | Yes — pretrained, single `pip install` | **Secondary/fallback** — likely easy, but unverified on this machine; better face-mesh density than RTMPose if facial/non-manual signal becomes a priority later |
| **MMPose (full framework) / ViTPose** | Yes (via `mmcv`/`mmdet` pipeline) | Yes | Yes (with a hand-specific config) | Yes | Only with a separate face model, not integrated | Heaviest option — `mmcv`/`mmdet`/`mmpose` full install; none of these are installed here; historically more install friction on macOS than the lightweight `rtmlib` wrapper (which exists specifically to avoid needing the full `mmpose`/`mmcv` stack — confirmed by our own prior-session notes: *"a lightweight ONNX-runtime-based RTMPose wrapper — not the heavier `mmpose` full framework"*) | Yes — pretrained checkpoints (ViTPose, RTMPose-in-mmpose) available | **Not recommended for the probe** — same underlying RTMPose weights are reachable through the much lighter `rtmlib` path we've already proven; the full framework adds install surface with no signal-quality benefit for a first probe |

**Recommendation for D1: RTMPose via `rtmlib`, primary.** It is the only candidate with
direct, proven, on-this-machine evidence (not just "should work" from documentation) —
the exact same extraction step already produced the Uni-Sign benchmark's inputs. If
`rtmlib`'s re-fetch or a specific ONNX model hits an unexpected snag, MediaPipe's
Tasks-API `HolisticLandmarker` is the fallback (single `pip install mediapipe`,
officially arm64-native per current docs, richer face mesh) — not MMPose/ViTPose, which
add install surface for no proven benefit here.

## 6. What D0 does NOT establish

- Whether trajectory-derived signals, given to *Gemini specifically* (not a from-scratch
  skeleton encoder + mT5), change semantic outcomes — untested, that's D2's question.
- Whether RTMPose's hand/finger keypoints are precise enough for fingerspelling-relevant
  detail — that's exactly what D1's tracking-quality checks need to establish before D2
  is worth running.
- Face/non-manual keypoint reliability — RTMPose's WholeBody face keypoints are coarser
  than a dedicated face-mesh model (MediaPipe); flagged as optional/lower-confidence in
  D1, not assumed to work.

## Sources consulted (web, current as of this session)

- [Holistic landmark detection guide | Google AI Edge](https://ai.google.dev/edge/mediapipe/solutions/vision/holistic_landmarker) — confirms the current Tasks-API `HolisticLandmarker` (543 combined landmarks) is the up-to-date, non-legacy path.
- [mediapipe · PyPI](https://pypi.org/project/mediapipe/) and [Apple silicon (M1) prebuilt mediapipe wheels released on PyPI · Issue #3277](https://github.com/google-ai-edge/mediapipe/issues/3277) — confirms official arm64/macOS wheel availability.
