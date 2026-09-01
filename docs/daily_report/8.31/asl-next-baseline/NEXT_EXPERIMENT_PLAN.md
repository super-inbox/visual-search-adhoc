# Next experiment plan — Uni-Sign as second ASL baseline

**Status: Stages 0-3 EXECUTED, 2026-08-31 (research/evaluation only).**
Both the single-clip smoke test (Stage 2) and the full 19-clip benchmark
run (Stage 3) were approved by the requester and run to completion.
Results: `results/UNISIGN_ONE_CLIP_RESULT.md` and
`results/UNISIGN_19CLIP_RESULTS.md`. Stage 4 (BOSS_SUMMARY-style write-up
across both milestones) was **not** run in this pass. No production code
was touched; nothing was committed or pushed.

---

## Why Uni-Sign, restated briefly

Full reasoning is in `SECOND_BASELINE_CANDIDATES.md`. In one line: it is
the only system found that is (a) trained and evaluated specifically on
How2Sign/ASL, (b) has a released, downloadable pretrained checkpoint
(released 2025-12-20, one day before this search would have missed it
entirely on the 8/30 pass), (c) has a documented raw-video inference path
requiring no training, and (d) uses a genuinely different mechanism
(explicit continuous skeletal motion) from both Curify (frame-by-frame,
no temporal model) and OpenSLT (single I3D feature extractor).

---

## Staged plan (nothing below has been run)

### Stage 0 — Decision checkpoint (this document) — ✅ APPROVED 2026-08-31

Approved: ~3.5GB download, one new isolated conda environment, one fixed
How2Sign clip, CPU/Mac attempt first. No private Curify videos, no
training, no 19-clip run, no decoding tuning, no production code changes,
no commit/push.

### Stage 1 — Environment setup — ✅ DONE

- New isolated conda env `unisign-cpu-arm64`, **Python 3.10** (deviates
  from documented 3.9 — forced by needing conda-forge's native osx-arm64
  `decord==0.6.0` build, which only exists for Python 3.10+; PyPI has no
  osx-arm64 wheel for `decord` at all). Base conda's first `conda create`
  silently resolved **Intel/Rosetta (osx-64)** packages despite this being
  Apple Silicon hardware — the same trap Phase 1 hit with OpenSLT — caught
  immediately (before installing anything else) and rebuilt with
  `CONDA_SUBDIR=osx-arm64`; confirmed `platform.machine() == 'arm64'`
  before proceeding.
- `decord==0.6.0` installed via `conda-forge` (`CONDA_OVERRIDE_OSX=14.0`
  needed to work around a virtual-package mismatch), not pip — genuinely
  needed at import time (`utils.py` imports it unconditionally, even
  though pose-only inference never calls its functions).
- `deepspeed==0.16.3` installed via pip with **no source compilation** —
  it resolved a pure-Python wheel (no CUDA detected, so its native
  op-builder extensions were skipped) and imported cleanly. Also a real
  import-time dependency of `utils.py`, unused at runtime for single-clip
  inference. This resolved cleanly, unlike the anticipated risk.
- `tensorflow` confirmed unnecessary and never installed — verified by
  reading every file in the actual `online_inference.py` import chain;
  it's not imported anywhere in that chain.
- Two **undisclosed-until-now, forced** deviations surfaced during Stage
  1 that weren't anticipated when this plan was first written:
  `numpy` ended up at `2.2.6` (not documented `1.22.4` — conda-forge's
  `decord` build required NumPy 2.x ABI) and `opencv-python` had to be
  bumped from documented `4.6.0.66` to `4.10.0.84` (the old build's C
  extension breaks on `cv2.resize()` under numpy 2.x — see full account
  in `results/UNISIGN_ONE_CLIP_RESULT.md`).
- `rtmlib` installed from `demo/rtmlib-main` via `pip install -e .`,
  using plain CPU `onnxruntime` (not `onnxruntime-gpu`) — confirmed via
  reading `rtmlib`'s own `base.py` that `device="cpu"` maps directly to
  onnxruntime's `CPUExecutionProvider`, no GPU package needed.

### Stage 2 — Smallest meaningful experiment — ✅ DONE, SUCCESS

Ran the documented raw-video inference path (a CPU-patched copy of
`demo/online_inference.py` — 4 mechanical `.cuda()` → CPU edits only, no
model/decoding changes) on the first eligible clip of the frozen
benchmark, `-g0iPSnQt6w_11-1-rgb_front` (same clip Phase 1 used for
OpenSLT's one-clip test, enabling direct comparison). Full result, exact
command, and every environment deviation:
`results/UNISIGN_ONE_CLIP_RESULT.md`.

All four goals originally listed for this stage were resolved:

1. **Environment runs on this Mac: confirmed**, after the numpy/opencv-python
   fix above.
2. **`rtmlib` pose extraction produces sane output**: confirmed — 263
   frames, 133 COCO-WholeBody keypoints/frame, 11.8s.
3. **English output format**: a single plain-text sentence printed to
   stdout (`Prediction result is: ...`) — no timestamps, unlike
   OpenSLT's segment-level output style.
4. **Per-clip CPU runtime**: 74.0s end-to-end for this one 5.27s clip
   (11.8s pose extraction + ~14s model load + 46.1s beam-search
   generation) — substantially heavier than OpenSLT's ~4s one-clip run,
   dominated by mT5-base decoding.

**Result quality (n=1, no general claim):** WER 0.875, CER 0.8349,
sacreBLEU 7.23, chrF 39.08 — roughly comparable to OpenSLT's same-clip
numbers on WER/CER/BLEU, notably higher chrF (more fluent surface
English), but the prediction fabricates an unrelated topic and exhibits a
severe 4x verbatim repetition loop. Full qualitative breakdown in
`results/UNISIGN_ONE_CLIP_RESULT.md`.

### Stage 3 — Scale to the full frozen benchmark — ✅ DONE, SUCCESS

Approved and run: all 19 clips, same environment/checkpoint/CPU
patches/decoding config as Stage 2, via a batch driver
(`demo/batch_inference_cpu_patched.py` — loads the model once and loops
over clips instead of reloading per clip, a pure batching convenience, no
model/decoding change). Full result: `results/UNISIGN_19CLIP_RESULTS.md`,
per-clip data in `results/UNISIGN_19CLIP_RESULTS.csv`, raw stdout in
`results/raw_output_19.txt`.

**Headline: 19/19 scored, ~20.6 minutes total.** Corpus WER 0.948, CER
0.7606, SacreBLEU 3.13, chrF 20.34 — **all four metrics beat OpenSLT's
same-benchmark numbers** (WER 1.1637, CER 0.8675, SacreBLEU ~0.93–0.96,
chrF ~17.11–19.59), and Uni-Sign additionally scored the one clip
(`G33aqW3DLpc_1-10-rgb_front`) OpenSLT's pipeline couldn't handle at all.
This is a materially different picture than the n=1 smoke test suggested
(where the two systems looked roughly comparable) — confirming this was
the right call to run at scale rather than stop at n=1.

Failure-mode findings: topic fabrication is universal (0/19 predictions
track their reference's actual content); repetition loops occur in 8/19
clips (42%); every clip ≥15.81s (12/12) was truncated mid-sentence by the
`max_new_tokens=100` decoding cap, vs. only 1/7 of clips under 10s — a
clear decoding-budget effect, not something this evaluation tuned or
worked around. Full breakdown in `results/UNISIGN_19CLIP_RESULTS.md`.

### Stage 4 — Report — NOT DONE in this pass

A `BOSS_SUMMARY.md`-style write-up combining Phase 1 (OpenSLT) and Phase
2 (Uni-Sign) into one decision-maker document was not produced here — the
per-milestone results docs (`UNISIGN_ONE_CLIP_RESULT.md`,
`UNISIGN_19CLIP_RESULTS.md`) stand on their own for now. If/when Stage 4
is requested: explicitly do not claim a Curify comparison (Curify has
still not been run on these exact 19 clips — same caveat Phase 1 already
documented for OpenSLT).

### Fallback (not needed — Stage 1/2 succeeded)

The originally-planned fallback was a zero-shot general-purpose
native-video VLM experiment, to be used only if Uni-Sign proved
genuinely unrunnable on this Mac. **Not triggered** — `decord` and
`deepspeed` both installed and imported successfully (see Stage 1), and
the pose-only checkpoint produced a real, well-formed English prediction
(see Stage 2). This fallback remains documented in
`SECOND_BASELINE_CANDIDATES.md` in case a future blocker does arise.

---

## What was actually done in this phase (research/evaluation only)

- ~3.66GB downloaded: mT5-base weights (2.33GB, checksum-verified) +
  Uni-Sign How2Sign checkpoint (1.19GB, checksum-verified) + RTMPose
  lightweight-mode ONNX models (~139MB, auto-downloaded by `rtmlib`).
- One new isolated conda environment (`unisign-cpu-arm64`) created;
  `openslt-cpu-arm64`, base conda, and system Python were not touched.
- All 19 frozen How2Sign benchmark clips processed end-to-end on CPU
  (one clip in the Stage 2 smoke test, then all 19 in Stage 3).
- No training or fine-tuning performed.
- No private Curify user videos used — only the frozen public How2Sign
  benchmark clips already staged in this repo.
- No decoding tuned against any reference, on any clip (`num_beams=4`,
  `max_new_tokens=100` left exactly as documented throughout).
- The frozen benchmark (`manifest.csv`, reference `.srt` files) was read
  only, never modified.
- No Curify production code was touched or modified.
- No commit or push performed as part of this phase.
