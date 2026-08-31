# Uni-Sign — one-clip CPU inference result, 2026-08-31

**Status: SUCCESS.** A real English prediction was obtained from the
released Uni-Sign How2Sign pose-only checkpoint
(`how2sign_pose_only_slt.pth`), run entirely on CPU on this Apple Silicon
Mac, on the same clip used for Phase 1's OpenSLT one-clip test. Per
instructions, this stops here — the remaining 18 clips were **not** run,
no decoding was tuned, and the frozen benchmark/production code were not
touched.

**This is a research/evaluation experiment only.** See "Licensing
limitation" below before drawing any production conclusion.

## Clip

| Field | Value |
|---|---|
| CLIP_ID | `-g0iPSnQt6w_11-1-rgb_front` |
| Selection | First row of the frozen `manifest.csv` (row order, not cherry-picked) — same clip Phase 1 used for OpenSLT's one-clip test, enabling a direct comparison |
| Duration | 5.27s (manifest) / 5.26s (ffprobe) |
| Source | official How2Sign test split |
| Source path | `asl-translator/data/public_benchmarks/how2sign/videos/-g0iPSnQt6w_11-1-rgb_front.mp4` (local frozen benchmark copy, no private Curify data used) |

## Reference vs. prediction

**REFERENCE** (official How2Sign test-split translation, also our benchmark's own reference text):
> what you're going to do is you're going to take both your arms and they're going to come underneath your legs.

**PREDICTION** (Uni-Sign `how2sign_pose_only_slt.pth`, pose-only mode, CPU, beam=4, max_new_tokens=100, documented decoding params, untuned):
> So we're going to take our mascara brush and take our mascara brush and we're going to take our mascara brush and we're going to take our mascara brush.

## Metrics

| Metric | Uni-Sign (this run) | OpenSLT (Phase 1, same clip) |
|---|---|---|
| WER | 0.8750 (13 substitutions, 0 deletions, 8 insertions / 24 reference words) | 0.8333 |
| CER | 0.8349 | 0.6789 |
| sacreBLEU | 7.23 (30.0/13.8/3.6/1.9 n-gram precisions, BP=1.000) | 7.67 |
| chrF | 39.08 | 15.97 |
| Temporal IoU | **not computed** — Uni-Sign produces sentence-level translation only, no timestamps; not meaningful here (per instructions) | not computed |

WER/CER computed with this repo's own `asl-eval/lib.py` — the exact same
tool used for every other WER/CER comparison in this project
(SignCaption, baseline0, temperature0, and OpenSLT's own one-clip result
above), so these numbers are on identical footing. sacreBLEU/chrF
computed directly with the `sacrebleu==2.2.0` Python package (the pinned
version from Uni-Sign's own `requirements.txt`) on the same two strings.

**Do NOT read this table as "Uni-Sign is better/worse than OpenSLT."**
This is n=1 on a 5-second clip; see the Interpretation section below.

## Interpretation (n=1 — no general quality claim)

- **WER/CER/sacreBLEU are roughly comparable between the two systems on
  this one clip** — Uni-Sign is marginally worse on all three, well within
  what one clip's noise can explain.
- **chrF is much higher for Uni-Sign (39.08 vs. 15.97).** This tracks a
  real qualitative difference: Uni-Sign's output is composed of complete,
  correctly-spelled English words and grammatical clauses, while OpenSLT's
  output contains broken/malformed tokens ("i' be/", "from all together
  pressure the kick") that share very few character n-grams with the
  reference. chrF rewards fluency at the character level even when the
  content is wrong.
- **Neither system tracks the reference's actual content.** The reference
  is about taking both arms underneath the legs; OpenSLT's output drifts
  into unrelated fragments after "what"; Uni-Sign's output confidently
  describes an unrelated topic ("mascara brush") not present in the
  reference at all — a fabrication, not a paraphrase.
- **Uni-Sign shows a severe repetition-loop failure mode not present in
  OpenSLT's output on this clip**: the clause "take our mascara brush" is
  produced four times near-verbatim. This is a well-known failure mode of
  beam search on short/low-signal inputs and is worth understanding before
  scaling up, not just averaging over.
- **This does not establish which system is "better."** Both are wrong on
  content, in different ways, on one 5-second clip. See Q16 in the final
  report for the recommendation this supports.

## Qualitative checklist (for this one prediction)

| Check | Uni-Sign | OpenSLT (Phase 1) |
|---|---|---|
| Semantic topic preservation | No — fabricated an unrelated topic (makeup/mascara) | No — drifts into unrelated fragments |
| Major omissions | Yes — "both your arms," "underneath your legs" entirely absent | Yes — arms/legs content entirely absent |
| Unsupported additions | Yes — "mascara brush" invented outright | Minor — fragments don't clearly assert false content, mostly incoherent |
| Repetition | **Yes, severe** — same clause repeated 4x | No repetition observed |
| Number errors | N/A — no numbers in reference | N/A |
| Fluency (surface English) | High — grammatical, real words throughout | Low — malformed tokens/fragments |

## Runtime & resource usage

- **Total wall-clock (pose extraction start → inference complete): 74.0s**
  on CPU, on this Apple Silicon Mac, no GPU/MPS compute used.
  - Pose extraction (rtmlib, 263 frames): 11.8s
  - Model construction (mT5-base load): 14.3s (cumulative t=26.1s)
  - Checkpoint load (`how2sign_pose_only_slt.pth`, strict, 627 keys, **0
    missing, 0 unexpected**): 1.6s (cumulative t=27.7s)
  - mT5 beam-search generation (beam=4, max_new_tokens=100): 46.1s
    (dominates total runtime)
- **Peak RSS observed: ~3.69GB** (at checkpoint-load point;
  `psutil.Process().memory_info().rss` sampled at each stage — see
  `raw_output.txt` for every sample). Consistent with an independent
  model-load-only test run earlier in this session (peak 3.63GB).
- For comparison, OpenSLT's equivalent one-clip run took ~4 seconds total
  and ~197MB peak RSS — Uni-Sign is substantially heavier on both time and
  memory, primarily due to the mT5-base decoder (a much larger language
  model than OpenSLT's from-scratch Fairseq transformer) plus the
  additional pose-extraction stage OpenSLT doesn't need (OpenSLT consumes
  pre-extracted I3D features).

## Exact command run

```bash
# environment: conda env "unisign-cpu-arm64" (new, isolated - see below)
cd <scratchpad>/unisign_run/repo   # Uni-Sign repo, pinned to commit eed438bcb49e30405cd6ccdfcccca330c134e830
PYTHONPATH="$(pwd)" python demo/online_inference_cpu_patched.py \
  --online_video "asl-translator/data/public_benchmarks/how2sign/videos/-g0iPSnQt6w_11-1-rgb_front.mp4" \
  --finetune "<scratchpad>/unisign_run/checkpoints/how2sign_pose_only_slt.pth" \
  --dataset How2Sign
```

`demo/online_inference_cpu_patched.py` is a copy of the pinned repo's
`demo/online_inference.py`, patched **only** to remove 4 hardcoded
`.cuda()`/`device="cuda"` calls (this Mac has no CUDA GPU) plus
non-functional timing/RAM logging. No model architecture, checkpoint,
decoding parameters (`num_beams=4`, `max_new_tokens=100` — both left
exactly as documented, not tuned against the reference), or
dataset/reference handling was changed. Full diff is reproducible from the
pinned commit; every changed line is marked `# CPU-PATCH` in the file.
`PYTHONPATH="$(pwd)"` was needed because `python demo/<script>.py` does
not put the repo root (where `models.py`, `config.py`, etc. live) on
Python's import path by default — a run-invocation detail, not a code
change.

## Environment & dependency deviations (all disclosed, all forced by Apple Silicon)

Full narrative in `NEXT_EXPERIMENT_PLAN.md`. Summary:

1. **New isolated conda env `unisign-cpu-arm64`, Python 3.10** (documented
   env is Python 3.9). The first `conda create` silently resolved
   **Intel/Rosetta (osx-64) packages** despite running on this Apple
   Silicon Mac — caught before installing anything further (same trap
   Phase 1 hit and caught with OpenSLT) and rebuilt with
   `CONDA_SUBDIR=osx-arm64`, confirmed via `platform.machine() == 'arm64'`.
   Python was bumped from the documented 3.9 to 3.10 specifically because
   `decord==0.6.0` has no native osx-arm64 wheel on PyPI, and conda-forge's
   native osx-arm64 build of `decord==0.6.0` only exists for Python
   3.10+.
2. **`decord` installed via `conda-forge`, not `pip`**, using
   `CONDA_OVERRIDE_OSX=14.0` to work around a virtual-package version
   mismatch in the base conda install. This is the package `utils.py`
   imports unconditionally at module load time (even though pose-only,
   non-RGB-support inference never calls its `VideoReader`/`cpu`
   functions at runtime) — so it's a real, unavoidable import-time
   dependency, not an unused one we could skip.
3. **`numpy` ended up at 2.2.6, not the documented `1.22.4`.** The
   conda-forge `decord` build was compiled against NumPy 2.x's ABI
   (`np2py310` in its build string) and pulled numpy 2.2.6 in as a
   dependency, silently overriding the `numpy==1.22.4` we had pinned
   earlier. This was caught (not left silent) and verified non-breaking
   for every other pinned library **except** opencv-python (next item).
4. **`opencv-python` bumped from the documented `4.6.0.66` to `4.10.0.84`.**
   The pinned 4.6.0.66 (a 2022-era build, pre-dating NumPy 2.0) has a C
   extension compiled against NumPy 1.x's ABI: it imports fine under numpy
   2.2.6, but calling `cv2.resize()` on a real array fails with
   `cv2.error: ... Overload resolution failed: src is not a numpy array`
   — this is exactly the failure mode this pipeline hit on frame 1 of
   pose extraction. Bumping to a NumPy-2.x-safe release fixed it with no
   observed behavior change on the basic operations this pipeline uses
   (`VideoCapture` frame reads + `resize` for model preprocessing).
5. **`deepspeed==0.16.3` installed successfully with no source
   compilation needed** — pip resolved a pure-Python wheel (deepspeed's
   own setup detected no CUDA and skipped its native op-builder
   extensions) and it imported cleanly, auto-detecting `mps` as its
   accelerator backend (unused — we drive everything from plain CPU
   PyTorch, not through deepspeed's runtime). Also a real, unavoidable
   import-time dependency of `utils.py`, not functionally exercised
   during single-clip inference.
6. **`tensorflow` (pinned in `requirements.txt`) was never installed** —
   confirmed by reading every file in the actual import chain
   (`online_inference.py` → `models.py`/`utils.py`/`datasets.py`/
   `config.py`/`stgcn_layers/*`/`deformable_attention_2d.py`); tensorflow
   is not imported anywhere in that chain, so it was correctly skippable
   per the "treat as optional unless the inference path actually imports
   it" instruction (unlike decord/deepspeed, which are imported even
   though unused at runtime).
7. **`torch`/`torchvision`/`torchaudio` installed at the documented
   `2.1.1`/`0.16.1`/`2.1.1` version numbers but as CPU wheels**, dropping
   the documented `+cu121` CUDA build tag (no CUDA on this Mac) — same
   version, different build target, not a version change.
8. **4 hardcoded `.cuda()`/`device="cuda"` calls patched to CPU** in a
   copy of `demo/online_inference.py` (never the original) — see "Exact
   command run" above.

None of these deviations touched model weights, model architecture, or
decoding parameters. All are recorded here rather than applied silently.

## Licensing limitation for production use

**This experiment does not authorize or suggest any Uni-Sign code or
checkpoint be integrated into Curify's production translator.**

- The `how2sign_pose_only_slt.pth` checkpoint is released under
  **CC BY-NC-4.0** (per its Hugging Face model card) — non-commercial use
  only. Curify's production ASL translator is a commercial product;
  deploying this checkpoint (or a model trained/fine-tuned starting from
  it) in production would violate this license.
- The Uni-Sign **code repository has no LICENSE file** (`license: null`
  via the GitHub API, confirmed at the pinned commit
  `eed438bcb49e30405cd6ccdfcccca330c134e830`) — meaning there is no
  explicit grant even for research redistribution/modification beyond
  conventional academic-code norms. This is a real gap, not a formality.
- **No Curify production code was modified or touched by this
  experiment.** Everything above ran in an isolated conda environment and
  an isolated scratch directory outside this repository; only this
  results documentation and the (already-approved) `.gitignore`-adjacent
  planning docs were written under version control.
- **Result quality does not change this boundary.** Even if a future
  larger-scale run showed Uni-Sign clearly outperforming both Curify and
  OpenSLT, the licensing terms above would still need to be independently
  resolved (e.g., contacting the authors, training a from-scratch
  replacement, or a commercial-license negotiation) before any production
  path could be considered — this document does not represent that as
  having happened.
