# Manager request C — `gloss-free-asl-translation` bring-up and evaluation

Date: 2026-09-18
Scope: Phase C only, per manager's confirmed priority order A -> C -> B. Phase A
(`UNI_SIGN_REAL_E2E.md`, this session's prior work) is not modified or weakened by
anything below. No segmentation work (Phase B), no `curify-studio` modification, no
commit/push.

## C1 — Our current tracker

Inspected directly: `asl-translator/asl-eval/trajectory_probe/extract_trajectory.py`,
`keypoint_schema.py`, `summarize_trajectory.py` (this repo, unmodified this session).

- **Tracker library**: `rtmlib` (version `0.0.13`, pinned in this repo's own
  `unisign-cpu-arm64` conda env — same env/weights previously used for the Uni-Sign
  benchmark).
- **Detector/model**: `rtmlib.Wholebody()`, `mode="lightweight"`, `backend="onnxruntime"`
  — internally RTMDet-tiny (detector) + RTMW-l (pose model). Confirmed by the actual
  cached weight filenames referenced in code:
  `yolox_tiny_8xb8-300e_humanart-6f3252f9.onnx` (detector),
  `rtmw-dw-l-m_simcc-cocktail14_270e-256x192_20231122.onnx` (pose).
- **Keypoint schema**: COCO-WholeBody, 133 points, as documented in
  `keypoint_schema.py` and confirmed against the pinned rtmlib version's own output
  ordering.
- **Raw point count**: **133** = 17 body (COCO-17) + 6 feet + 68 face + 21 left hand +
  21 right hand. Confirmed by reading `keypoint_schema.py`'s index ranges directly
  (`BODY_START:BODY_END=0:17`, `FEET_START:FEET_END=17:23`, `FACE_START:FACE_END=23:91`,
  `LEFT_HAND_START:LEFT_HAND_END=91:112`, `RIGHT_HAND_START:RIGHT_HAND_END=112:133`).
- **Downstream-used regions**: grepped `summarize_trajectory.py` for every reference to
  `ks.BODY_*`, `ks.FEET_*`, `ks.FACE_*`, `ks.LEFT_HAND_*`, `ks.RIGHT_HAND_*` — only
  `ks.BODY_START:ks.BODY_END`, `ks.LEFT_HAND_START:ks.LEFT_HAND_END`, and
  `ks.RIGHT_HAND_START:ks.RIGHT_HAND_END` appear anywhere in that file. **Face (68 pts)
  and feet (6 pts) are extracted and stored in `landmarks.json` but never sliced or
  referenced by the summary/derived-feature code.**

**Are we currently using MediaPipe? NO.** We use `rtmlib.Wholebody()`
(RTMDet-tiny + RTMW-l, COCO-WholeBody 133), confirmed directly from the import
statement (`from rtmlib import Wholebody`) and the cached ONNX model filenames — no
`mediapipe` import appears anywhere in `asl-translator/asl-eval/trajectory_probe/`.

## C2 — Clone and inspect the new repo

Cloned to `/Users/baobaoli/Desktop/gloss-free-asl-translation-2026-09-18` — a sibling
directory outside both `curify-studio` and `visual-search-adhoc-asl-task-c`, not
vendored into either. This follows the same "dated sibling clone" convention already
used elsewhere on this machine for external/scratch repos.

- **Commit hash**: `5b7eb92ff90c4ac5907bc6328edb79c24cec6c77`
- **Branch**: `main` (only branch; `git branch -a` shows no other refs)
- **Last pushed**: `2026-07-01T20:27:13Z` (per GitHub API `pushed_at`) — **over 2.5
  months stale** relative to today (2026-09-18).
- **License**: MIT (`LICENSE` file present, `Copyright (c) 2026 Yassin`). No usage
  restriction, unlike Uni-Sign's CC BY-NC-4.0 checkpoint from Phase A.
- **Repository structure** (top level, 311 KB total per GitHub API):
  ```
  LICENSE  README.md  kaggle_training.ipynb  pyproject.toml  requirements.txt
  scripts/  (check_environment.py, evaluate.py, export_onnx.py, inference.py, profile_memory.py)
  src/      (data_pipeline.py, dataset.py, train.py, validate_dataset.py,
             models/{manual_encoder.py, translation_model.py},
             utils/{io_utils.py, metadata.py, splits.py})
  tests/    (conftest.py, test_dataset.py, test_model.py, test_pipeline.py)
  ```
  `data/` and `results/` are declared in README's "Project Structure" but are
  **`.gitignore`'d and not present in the clone** (`.gitignore`: `.venv/`, `data/`,
  `results/`, `*.safetensors`, `*.log`).
- **README claims** (motivation, architecture, feature dims, CLI flags) — cross-checked
  against source in the subsections below; every claim checked matched the code, with
  **one exception** noted under "Bugs/discrepancies found."

### Source-code-verified architecture (not just README)

- **MediaPipe API**: `src/data_pipeline.py::ASLLandmarkExtractor` uses
  `mp.solutions.holistic.Holistic(static_image_mode=False, model_complexity=1,
  refine_face_landmarks=False, min_detection_confidence=0.5,
  min_tracking_confidence=0.5)` — i.e. **MediaPipe Holistic**, not MediaPipe Tasks API.
- **Pose landmark count**: 33 (`results.pose_landmarks.landmark`), 4D per point
  (x, y, z, visibility).
- **Left/right hand counts**: 21 each (x, y, z; no visibility channel — MediaPipe hands
  don't expose one).
- **Facial landmark subset**: 92 of MediaPipe's 468-point face mesh, explicit hardcoded
  index lists for lips (40), left eye (16), right eye (16), left eyebrow (10), right
  eyebrow (10) — deduplicated/sorted in `data_pipeline.py` and duplicated verbatim in
  `src/utils/io_utils.py::MEDIAPIPE_FACE_SUBSET_INDICES` (used for `.npy`-format Kaggle
  Holistic files, which store the full 468 and must be sliced on load).
- **Feature dimensions**: concatenated per frame as
  `pose_flat + left_hand_flat + right_hand_flat [+ face_flat]`
  (`src/dataset.py::__getitem__`). README claims 501 dims for `.npy` and 534 for
  `.npz`. **Verified discrepancy**: see "Bugs/discrepancies found" below — the actual
  `.npz` load path also produces 501, not 534.
- **Coordinate dimensions**: pose is 4D (x,y,z,visibility) as extracted by
  `data_pipeline.py`, but `dataset.py`'s `.npz` load path explicitly slices
  `data["pose"][..., :3]`, dropping visibility before it ever reaches the model.
- **Visibility/confidence usage**: extracted (pose has a visibility channel) but, per
  the point above, **discarded before model input on the `.npz` path** actually
  exercised in this session's smoke test. Not used as an attention/masking signal
  anywhere in `dataset.py` or `manual_encoder.py`.
- **Normalization** (`src/dataset.py::_normalize_landmarks`): mid-shoulder centering
  using MediaPipe pose indices `11`/`12` (left/right shoulder), shoulder-width scaling
  with a `0.25` fallback when width `< 0.05`, hands centered on their own wrist
  (index 0 of the 21-point hand), face centered on its own centroid. Matches the
  README's "Mathematical Formulation of Coordinate Normalization" section exactly.
- **Sequence representation**: flattened per-frame feature vector, `stride`-based
  downsampling in `dataset.py::__getitem__` if `seq_len > max_len` (evenly-spaced
  stride via Python slicing `features[::stride]`, then hard-truncated to `max_len` if
  still over — **not** random subsampling, in contrast to Uni-Sign's approach observed
  in Phase A).
- **Conformer architecture** (`src/models/manual_encoder.py`): Gulati-style Conformer,
  Macaron FFN sandwich (`FeedForwardModule`, half-step residual), multi-head self-attn
  (`ConformerAttentionModule`, default 4 heads) with **absolute** sinusoidal positional
  encoding (explicitly documented in-code as a deliberate simplification vs. the
  original paper's relative encoding), depthwise-separable conv module with GLU
  (kernel size 31, `LayerNorm` instead of `BatchNorm1d` specifically to avoid padding
  bias), 4 blocks by default, `d_model=512`, plus a learned strided (`stride=2`) Conv1d
  temporal downsampler before the blocks.
- **T5 architecture/integration** (`src/models/translation_model.py`):
  `transformers.T5ForConditionalGeneration.from_pretrained(t5_model_name)`, then
  `del self.t5.encoder` (the T5 text encoder is deleted — Conformer output is fed
  directly as `BaseModelOutput(last_hidden_state=...)` into T5's decoder
  cross-attention, bypassing T5's own encoder entirely). A `modality_bridge`
  (`Linear -> GELU -> LayerNorm`) projects `d_model=512` Conformer output to T5's own
  `d_model` (512/768/1024 depending on `t5-small`/`base`/`large`).
- **Optional RGB/I3D path**: present and real, not a stub. `input_i3d_dim` (default
  1024) triggers `i3d_projection` (strided Conv1d) + `i3d_norm` + `i3d_act`, then a
  **Gated Multimodal Fusion**: `gate_conv` (Conv1d over concatenated
  `[conformer_out, i3d_proj]`) produces a sigmoid gate, `outputs = gate*conformer_out +
  (1-gate)*i3d_proj`, followed by `fusion_norm`. Verified working end-to-end in this
  session (`test_model_multi_stream_fusion` — see C4).
- **Max sequence length**: `--max_len` default `150` frames (input feature sequence,
  caps via stride+truncate before the model ever sees it);
  `--max_target_len` default `30` output tokens.
- **Training entry point**: `python -m src.train` (`src/train.py`) — a
  `transformers.Seq2SeqTrainer` subclass with a custom 4-group Adafactor optimizer
  (differential LR for Conformer vs. T5 params), signer-independent train/val split
  (`src/utils/splits.py::split_by_signer`), gradient checkpointing, `predict_with_generate`.
- **Inference entry point**: `python -m scripts.inference --checkpoint <dir> --input
  <npz/npy>` (`scripts/inference.py`) — requires a local checkpoint directory
  containing `model.safetensors` or `pytorch_model.bin`.
- **Evaluation entry point**: `python -m scripts.evaluate --checkpoint <dir> --data-dir
  <landmarks> --metadata <csv>` (`scripts/evaluate.py`) — same checkpoint-file
  requirement as above, computes WER (`jiwer`) and BLEU-4 (`sacrebleu`).

### Bug/discrepancy found (documented, not patched — see policy below)

- **Bug**: README's "Feature Dimension Breakdown" claims `.npz` files yield **534**
  dimensions (`Pose 33×4=132 + LH 63 + RH 63 + Face 276`), but
  `src/dataset.py::ASLLandmarkDataset._load_landmarks`'s `.npz` branch explicitly runs
  `pose = data["pose"][..., :3]` — hard-slicing away the 4th (visibility) channel
  before concatenation. The actual `.npz` output is therefore **501** dims
  (`99 + 63 + 63 + 276`), identical to the `.npy` path, not 534.
- **Evidence**: `src/dataset.py` lines in the `else:` branch of `_load_landmarks`
  (non-`.npy` case); directly reproduced in this session's own smoke test (see C4) —
  loading a real `.npz` file produced by this repo's own
  `ASLLandmarkExtractor.save_landmarks()` (which does store the full 4D pose) yielded a
  `features` tensor of width **501**, confirmed printed and asserted false against the
  534 hypothesis.
- **Minimal proposed patch** (not applied): either (a) fix the README's `.npz` dims
  claim to 501, or (b) if 534 was the intended real behavior, change
  `pose = data["pose"][..., :3]` to `pose = data["pose"]` in the `.npz` branch of
  `_load_landmarks`. This is a **documentation-vs-code mismatch, not a blocker** — the
  code runs correctly and consistently at 501 dims regardless of which file format is
  used; it just doesn't match one README table cell. Per instructions, this is
  documented only; **no upstream tracked code was changed**, since it does not block
  bring-up in any way (all downstream code — the Conformer's `input_dim` — is derived
  dynamically from the actual tensor shape at runtime, not hardcoded to 501 or 534).

## C3 — Real trained checkpoint search

Searched thoroughly, all methods return the same conclusion:

- **In-repo**: no `.pt`/`.pth`/`.ckpt`/`.safetensors`/`.bin` file anywhere in the clone.
  `results/` (the documented checkpoint output directory) is gitignored and doesn't
  exist in this clone (nothing to gitignore — never populated/committed).
- **GitHub Releases**: `gh api repos/yyouretoast/gloss-free-asl-translation/releases`
  → `[]` (zero releases). `gh release list` → empty.
- **Tags**: `git tag -l` → empty (no tags at all).
- **Hugging Face / Google Drive / Kaggle model links**: grepped the entire source tree
  (`*.py`, `*.md`, `*.ipynb`, `*.toml`) for `huggingface.co/`, `drive.google.com`,
  `kaggle.com/models`, `.pt'`/`.pth'`/`.ckpt`, "checkpoint...url", "release" — the only
  matches are unrelated (`cap.release()`/`out.release()`, OpenCV `VideoCapture`
  cleanup calls, not model releases). The only Hugging Face references anywhere are the
  **stock pretrained T5 decoder IDs** (`t5-small`, `t5-base`, `google/flan-t5-base`,
  etc.) passed to `T5ForConditionalGeneration.from_pretrained()` — a generic pretrained
  language model, not an ASL-translation-trained checkpoint.
- **Config defaults**: `--resume_from_checkpoint` defaults to `None`;
  `--output_dir` defaults to `results/checkpoints` (a local path the trainer would
  create during a real training run, empty/nonexistent until then).
- **Kaggle training notebook** (`kaggle_training.ipynb`, inspected cell-by-cell): its
  entire purpose is to run training **on Kaggle's own infrastructure** against
  Kaggle-hosted datasets (`how2sign-holistic`, `how2sign-i3d-features`, referenced via
  `/kaggle/input`), producing checkpoints only under `/kaggle/working` — **zipped and
  offered for manual download by the notebook's own author, never published back to
  this GitHub repo**. The notebook itself is the closest thing to a "checkpoint
  pipeline" that exists, and it explicitly produces nothing usable without first
  running a full Kaggle GPU training job.
- **README's own "Results" section**: literally a placeholder —
  `*(Placeholder: BLEU-4 and WER metrics on the validation splits will be reported here
  after the full training run completes.)*` — and "Demo" is likewise a placeholder.
  This is the author's own explicit statement that training has not been completed.

**Classification: NO.** No real trained MediaPipe-landmarks → ASL-to-English checkpoint
exists anywhere reachable from this repository — not in-repo, not in Releases, not
linked externally. The only real, loadable weights anywhere in this pipeline are the
**stock pretrained T5 decoder** (general-purpose English language model, never
fine-tuned on any sign-language data) — per the task's explicit instruction, this does
**not** count as a trained ASL translation checkpoint.

## C4 — Local bring-up

**Isolated environment**: `python -m venv .venv` inside the cloned repo (not
`curify-studio`, not `visual-search-adhoc-asl-task-c`), `pip install -r
requirements.txt`.

- **Python version**: 3.11.7. Note: this machine's base interpreter
  (`/opt/anaconda3/bin/python3`, used to create the venv) is itself an **x86_64 build**
  running under Rosetta 2 emulation on this Apple M3 Pro (arm64) host — confirmed via
  `file` on both the base interpreter and the venv's own `python3.11` binary (both
  `Mach-O 64-bit executable x86_64`) and `platform.machine()` inside the venv returning
  `x86_64`. Every dependency below therefore installed as an **x86_64 wheel**
  (`mediapipe-0.10.14-cp311-cp311-macosx_11_0_x86_64.whl`,
  `torch-2.2.2-cp311-none-macosx_10_9_x86_64.whl`, etc.), not a native arm64 build.
- **Apple Silicon compatibility**: works, but **only via Rosetta 2 translation, not
  natively**. This is a real, disclosed performance caveat (translated x86_64 code runs
  slower than native arm64 would) — but it did not block any step in this session; every
  install, test, and smoke script below completed successfully.
- **Key dependency versions actually installed** (requirements.txt gives ranges; these
  are what `pip`'s resolver actually picked, newest-compatible-first, no version
  pinning by us): `torch==2.2.2`, `mediapipe==0.10.14` (exact-pinned by
  requirements.txt), `transformers==4.57.6`, `numpy==2.4.6`, `opencv-python==4.14.0.94`,
  `sentencepiece==0.2.2`, `jiwer==3.1.0`, `sacrebleu==2.6.0`, `onnx==1.22.0`,
  `safetensors==0.8.0`, `accelerate==1.15.0`.
- **Real, observed (non-blocking) issue**: `torch==2.2.2` was compiled against NumPy
  1.x's C-API; with `numpy==2.4.6` installed (satisfying requirements.txt's
  `numpy>=2.0.0,<3.0.0`), every `import torch` emits
  `UserWarning: Failed to initialize NumPy: _ARRAY_API not found`. This is a real
  upstream dependency-range issue (torch's own numpy-2 compatibility shim wasn't
  complete until later torch releases; requirements.txt's `torch<2.11.0` upper bound
  is loose enough that pip can resolve an older, only-partially-numpy-2-compatible
  torch). **Observed impact: none** — every test and smoke script below (including
  ones that convert numpy arrays to `torch.tensor`) ran and passed correctly despite the
  warning. Documented here as instructed ("platform issues"), not patched (no crash
  observed, so no fix was necessary for bring-up; changing the upstream
  `requirements.txt` pin was not required).

### Import smoke checks and test suite

`pytest tests/ -v -m "not slow"` (6 tests, no network/model downloads):
```
tests/test_dataset.py::test_dataset_loading_and_normalization PASSED
tests/test_dataset.py::test_dataset_missing_labels PASSED
tests/test_dataset.py::test_dataset_holistic_loading PASSED
tests/test_dataset.py::test_dataset_multi_stream_loading_and_collation PASSED
tests/test_model.py::test_encoder_forward PASSED
tests/test_model.py::test_long_sequence_positional_encoding PASSED
======================== 6 passed, 5 deselected in 27.78s ========================
```

`pytest tests/ -v -m "slow"` (5 tests, downloads real `t5-small` weights from HF Hub —
real network access, real pretrained weights, no mocking):
```
tests/test_dataset.py::test_collate_landmarks PASSED
tests/test_model.py::test_model_forward PASSED
tests/test_model.py::test_model_generate PASSED
tests/test_model.py::test_model_multi_stream_fusion PASSED
tests/test_pipeline.py::test_pipeline_extraction FAILED
=================== 1 failed, 4 passed in 10.44s ===================
```

- `test_model_forward` / `test_model_generate` / `test_model_multi_stream_fusion`
  passing means: **real Conformer construction, real pretrained T5-small decoder
  loading, a real forward pass with loss computation, real autoregressive `.generate()`
  decoding, and the real Gated Multimodal Fusion (I3D) path all work end-to-end on this
  machine**, with real (if untrained-encoder) tensors, not mocks.
- `test_pipeline_extraction` **failed**, but **not on a MediaPipe or model issue**: the
  test's own `cv2.VideoWriter(..., cv2.VideoWriter_fourcc(*"mp4v"), ...)` call silently
  produced a file OpenCV itself then couldn't reopen
  (`OSError: Failed to open video file`) — a synthetic-test-fixture codec/backend quirk
  specific to writing throwaway test videos with this OpenCV build on this platform,
  unrelated to reading real video files (see next section, where reading a real local
  `.mp4` worked without issue).

### Real MediaPipe extraction on a real local ASL clip

Ran `ASLLandmarkExtractor.extract_landmarks()` directly (not the failing synthetic-video
test) against `1477_recording_6.7s.mp4` — the same short clip used for Uni-Sign in
Phase A, a real Curify user recording, 640x480, 25fps, 167 frames, 6.68s:

```
pose       (167, 33, 4) float64
left_hand  (167, 21, 3) float64
right_hand (167, 21, 3) float64
face       (167, 92, 3) float64
n_frames=167
pose detected frames:       167/167 (100%)
left_hand detected frames:   14/167 (8.4%)
right_hand detected frames: 102/167 (61.1%)
face detected frames:       167/167 (100%)
wall_clock_s=7.64
```

**MediaPipe extraction: SUCCESS.** Real video in, real per-frame landmarks out, at
~real-time speed (7.64s wall clock for a 6.68s clip) despite running under Rosetta
emulation. Pose and face were detected on every frame; left-hand detection was
comparatively low (this clip shows one-handed number/counting handshapes per the
Phase A provenance audit, consistent with the right hand being the dominant signing
hand and the left hand frequently out of frame or resting).

### Full pipeline smoke: video → MediaPipe → tensor → model construction → generate()

Chained the above real extraction into the repo's own `ASLLandmarkDataset` load +
normalize path, then into `ASLTranslationModel` construction and `.generate()`, using
the **same real video and real landmarks** as above (no synthetic/mock data):

```
=== 2. Save to .npz then load through ASLLandmarkDataset (real pipeline path) ===
features tensor shape: torch.Size([84, 501]) torch.float32   (84 frames after stride-downsample from 167 > max_len=150... actually stride triggered at 167 vs max_len=150? see note)

=== 3. Model construction (Conformer -> T5-small), UNTRAINED encoder ===
model constructed in 0.36s
total params: 67,176,192 (of which T5 decoder: 41,625,344)

=== 4. generate() through untrained Conformer + pretrained T5 decoder ===
generate() wall clock: 0.84s
UNTRAINED-ENCODER prediction: 'spektspektspektspekt...' (repeated garbage token)
```

Note on the 84-frame count: `max_len` default is 150 and the clip only has 167 raw
frames, but `dataset.py`'s stride-downsample uses `stride = ceil(seq_len/max_len)`; for
`seq_len=167, max_len=150` that gives `stride=2`, halving to 84 frames (then no further
truncation needed, `84 <= 150`) — this is the documented stride behavior, not a bug.

**Model construction: SUCCESS** — 67.18M total parameters, of which 41.6M are the real
pretrained T5-small decoder weights (downloaded from Hugging Face, not random) and
~25.5M are the Conformer encoder + fusion/bridge layers (**randomly initialized** — no
ASL training data exists anywhere to have trained them). **`generate()` runs
end-to-end without error** and returns a real (degenerate, repeated-token) string —
exactly the expected outcome for an untrained encoder: T5's decoder receives
directionless/noisy cross-attention context and falls into a repetition loop. **This is
not a translation and is not presented as one** — it is proof that the full
mechanical pipe (video → landmarks → normalized tensor → Conformer → fusion bridge →
T5 cross-attention → beam search → tokenizer decode) wires together correctly on real
data, nothing more.

### No upstream code was modified

`git status --short` / `git diff --stat` inside the clone after all of the above:
clean except gitignored build artifacts (`.venv/`, `__pycache__/`, `.pytest_cache/`).
Zero tracked files touched.

## C5/C6 — Evaluation

Per C3, **no trained ASL translation checkpoint exists (Case: C6 applies, not C5)**.
No full or small-scale real translation evaluation was run, and none was fabricated.

**Maximum meaningful pipeline achieved** (per C6 instructions):
- Code/environment bring-up: **SUCCESS** (venv, deps, `check_environment.py`, non-slow
  and slow test suites — 10/11 passed, the 1 failure is an unrelated test-fixture codec
  issue, not a pipeline issue).
- MediaPipe extraction: **SUCCESS** (real local video, real landmarks, all 4 streams,
  documented shapes exactly matched).
- Model construction: **SUCCESS** (real Conformer + real pretrained T5-small decoder +
  real Gated Multimodal Fusion, 67.18M params, verified by both the repo's own
  `slow`-marked unit tests and an independent smoke script on real extracted data).
- Inference/evaluation: **BLOCKED** — mechanically reachable (`generate()` runs and
  returns real token IDs), but with a randomly-initialized encoder, so no output is
  meaningful and none is reported as a translation result. `scripts/evaluate.py`
  requires `--checkpoint <dir>` containing `model.safetensors`/`pytorch_model.bin`,
  which does not exist for this model.

**Exact reason real translation evaluation cannot be performed**: no trained ASL
translation checkpoint is published anywhere reachable from this repository (C3), and
training one from scratch was explicitly out of scope for this session
("Do NOT launch full training").

**From repo evidence — dataset/training feasibility**:
- **Expected dataset**: How2Sign, via two specific Kaggle-hosted datasets referenced by
  name in the README and notebook: "How2Sign Holistic" (`.../how2sign-holistic`, 44 GB)
  and "How2Sign I3D Features" (`how2sign-i3d-features`, 8 GB). YouTube-ASL is mentioned
  once in the README as another possible MediaPipe-Holistic-format source but has no
  concrete dataset link or notebook cell.
- **How2Sign supported**: **YES**, natively — the entire notebook and `.npy` loading
  path (`load_holistic_npy`, the 543-landmark combined format) is built specifically
  around the "How2Sign Holistic" Kaggle dataset's file format.
- **Training command**: `python -m src.train [--data_dir ...] [--i3d_dir ...]
  [--epochs N] [--t5_model t5-small|t5-base|...] ...` locally, or the equivalent cells
  in `kaggle_training.ipynb` on Kaggle (the notebook is the author's own documented,
  intended way to actually run a full training job — `/kaggle/input` dataset paths are
  resolved dynamically, GPU-optimized torch/torchvision are kept instead of the CPU
  wheels this session installed).
- **Expected preprocessing**: MediaPipe Holistic extraction (`ASLLandmarkExtractor`, or
  pre-extracted Kaggle `.npy` Holistic files) → geometric normalization
  (mid-shoulder/wrist/face-centroid centering, shoulder-width scaling) → optional I3D
  feature alignment via linear interpolation to match landmark frame count.
- **Checkpoint output format**: standard Hugging Face `Seq2SeqTrainer` checkpoint
  directories (`model.safetensors` preferred, `pytorch_model.bin` fallback), consumed
  directly by `scripts/evaluate.py`/`scripts/inference.py`.
- **Documented compute requirements**: none stated numerically in the README beyond
  "Kaggle GPUs" and `scripts/profile_memory.py` existing as "a GPU memory estimator for
  small/base T5 decoders" (not run in this session — out of scope, would not change the
  YES/NO/UNCLEAR checkpoint-availability finding). No stated GPU-hours, epoch count
  needed for convergence, or dataset-size-vs-time figures anywhere in the repo.
- **Is training our own checkpoint technically feasible?** Based on repo evidence
  alone: **plausibly yes, on Kaggle, with the two named Kaggle datasets attached** —
  the entire pipeline (data loading, signer-independent splitting, model construction,
  `Seq2SeqTrainer` loop, checkpoint saving, ONNX export, evaluation) is real, working
  code, verified in this session up to (but not including) the actual multi-epoch
  training run itself, which was explicitly out of scope this session. **No training
  cost/duration estimate is given here**, per instructions not to estimate without
  evidence — the repo itself provides no such evidence (no logged run, no stated
  GPU-hours).

## C7 — Comparison to our current trajectory work (D2)

**OUR CURRENT D2** (per `docs/daily_report/9.10/trajectory-tracking-feasibility/`):
RTMPose/COCO-WholeBody 133 raw landmarks → handcrafted body/hand trajectory summary
(velocity, pauses, hand-relative-to-body band, etc., converted to structured text) →
fed as extra prompt context to a generic, frozen, pretrained Gemini VLM → English.
**Result: 0/5 genuine semantic recoveries** (`PHASE_D2_RESULTS.md`).

**NEW REPO**: MediaPipe Holistic landmarks → learned normalization + linear projection
→ a **custom-trained** Conformer temporal encoder (self-attention + convolution,
learned downsampling) → optional learned Gated Multimodal Fusion with I3D features →
learned MLP bridge → T5 decoder cross-attention (pretrained T5 weights, but the
encoder/bridge that feeds it would be trained end-to-end on paired video/English data)
→ English.

1. **Is the new repo testing a meaningfully different hypothesis? YES.** D2 tested
   "hand a frozen, generic VLM a text summary of tracked kinematics." This repo tests
   "train a dedicated temporal encoder to consume raw (normalized, not-summarized)
   per-frame landmark coordinates directly, with gradients flowing all the way from the
   English loss back into the visual encoder." These are architecturally and
   methodologically distinct approaches, not variations of the same one.
2. **Does it consume face landmarks downstream? YES**, and directly in the trained
   model's own input — 92 face points are part of the concatenated per-frame feature
   vector fed into the Conformer's own input projection (`d_model=512` linear layer
   sees all of pose+hands+face together). This is a real, code-verified difference
   from our own D2 pipeline, where face landmarks are extracted but never enter
   `summarize_trajectory.py`'s output at all (C1, above).
3. **Does it learn temporal representation instead of converting trajectory into
   handcrafted text? YES.** There is no natural-language conversion step anywhere in
   this repo's pipeline before the T5 decoder; the Conformer operates directly on
   normalized numeric coordinate tensors, and its output is fed to T5 as continuous
   `encoder_outputs` (cross-attention hidden states), not as generated/inserted text.
4. **Can our RTMPose 133 landmarks be directly substituted? NO, not directly.**
   Different keypoint set (COCO-WholeBody 133 vs. MediaPipe Holistic 33/21/21/468),
   different per-part indexing (e.g. shoulders are COCO indices 5/6 in our schema vs.
   MediaPipe indices 11/12 used by this repo's own normalization code), and a
   different face subset (this repo's specific 92-index list is defined in MediaPipe's
   own 468-point mesh numbering, which has no direct correspondence to RTMPose's
   68-point COCO-WholeBody face block).
5. **Would an adapter be required? YES** — at minimum, an index-remapping /
   dimension-reconciling layer (or a from-scratch feature-vector assembly function
   mirroring `ASLLandmarkExtractor`'s output contract but fed by rtmlib instead of
   MediaPipe) would be needed before RTMPose landmarks could feed this repo's
   `ASLLandmarkDataset`/`ConformerEncoder` unmodified.
6. **Would retraining be required? YES, regardless of landmark source** — per C3,
   **no trained checkpoint exists at all** for this architecture with MediaPipe
   landmarks either. Using RTMPose landmarks would not "lose" a working pretrained
   model; there is no working pretrained model to lose. Any real use of this
   architecture — with MediaPipe or with substituted RTMPose landmarks — requires
   training from scratch.
7. **Does our prior D2 0/5 result invalidate this approach? NO — evidence does not
   support that conclusion, and this project's own D2 report says so explicitly.**
   Quoting `PHASE_D2_RESULTS.md` directly: *"D2 only tested handing raw kinematic text
   to a generic model that was never trained to use it. It does NOT test — and
   therefore does not rule out — a model architecture that **learns** to consume
   hand/body/face/handshape trajectory features directly (e.g., a trained
   temporal/graph encoder purpose-built for this signal...)."* This new repo's
   Conformer-encoder-trained-end-to-end architecture is precisely the class of approach
   D2 itself flagged as untested and still plausible. D2's negative result is scoped to
   one specific implementation (raw-text-to-frozen-generic-VLM) and provides no
   evidence either for or against a purpose-trained temporal encoder.

## Conclusion

1. **我们是不是 MediaPipe？** 不是。我们用的是 `rtmlib.Wholebody()`（RTMDet-tiny + RTMW-l，
   COCO-WholeBody 133 点），代码里没有任何地方导入过 `mediapipe`。
2. **新 repo 用什么？** MediaPipe Holistic（`mp.solutions.holistic.Holistic`），pose 33 +
   左右手各 21 + 脸部 468 点中精选的 92 点子集，直接作为可训练 Conformer 编码器的输入特征，
   不经过任何文字化步骤，再通过 T5 解码器 cross-attention 生成英文。
3. **本地是否调通？** 调通了到"模型能正确构造并跑通 generate() 调用"这一步（环境搭建、
   依赖安装、6/6 非慢速单测通过、4/5 慢速单测通过——含真实 T5-small 下载、真实前向、真实
   generate、真实 I3D 融合，唯一失败的 1 个测试是与 MediaPipe/模型无关的合成测试视频编解码
   器问题）。没有改动上游任何一行被跟踪的代码。
4. **MediaPipe landmarks 是否成功提取？** 成功。在真实本地 ASL 视频（Phase A 用过的同一条
   `1477_recording_6.7s.mp4`）上跑通，167 帧全部处理，pose/face 100% 检测率，输出形状与
   README 文档完全一致，耗时 7.64 秒（接近实时）。
5. **模型是否能构建？** 能。Conformer + 真实预训练 T5-small 解码器 + Gated Multimodal
   Fusion，共 6717 万参数（其中 4163 万是真实的预训练 T5 权重），构造和 `generate()` 调用
   全部真实跑通，无报错。
6. **有没有训练好的 ASL translation checkpoint？** **没有**。仓库内、GitHub Releases、
   tags、代码里的 Hugging Face/Google Drive/Kaggle 链接全部查过，唯一存在的真实权重是
   通用预训练 T5（从未在任何手语数据上训练过），README 的 Results/Demo 两节明确写着
   "占位符，等完整训练跑完后补"。仓库最后一次 push 是 2026-07-01，已经两个半月没有更新。
7. **是否真正跑了 evaluation？** 没有，也没有编造。因为没有真实训练好的 checkpoint，
   `scripts/evaluate.py`/`scripts/inference.py` 都要求一个包含 `model.safetensors` 或
   `pytorch_model.bin` 的本地 checkpoint 目录，这个目录不存在。本session额外做了一步
   （非manager要求的评测，只是工程验证）：用真实提取的 landmarks 跑通了"未训练编码器 +
   真实预训练T5解码器"的 generate() 调用，输出是无意义的重复token（"spektspekt..."）——
   这正是未训练编码器的预期表现，用来证明整条管线机械上能跑通，不是翻译结果，也没有当
   作翻译结果汇报。
8. **如果没有，具体 blocker 是什么？** 没有任何地方发布过这个 Conformer-T5 架构在
   MediaPipe landmarks 上训练好的真实 ASL 翻译 checkpoint。训练路径本身是真实可运行的代码
   （Kaggle notebook + `src/train.py`），但需要真正跑一次完整的 Kaggle GPU 训练（本session
   明确不允许启动），产出的 checkpoint 也从未被作者发布回这个仓库。
9. **和我们之前 trajectory 实验的关系是什么？** 不矛盾，也不能说互相验证。我们的 D2
   负结果（0/5）测的是"把轨迹转成文字塞给通用冻结 Gemini"这一条路径，D2 报告自己明确写
   了"没有测试、也没有排除"一个专门训练的时序编码器直接消费轨迹特征这条路径——而这正是
   新 repo 的架构本身。两者是不同的技术路线，新 repo 没有被验证有效（因为没有真实训练过），
   但也完全没有被我们的 D2 结果证伪。

## Phase C classification: **B — BRING-UP COMPLETE, EVAL BLOCKED**

Repo, environment, MediaPipe extraction, data pipeline, and model construction all
verified working with real code and real local data. No usable trained ASL translation
checkpoint exists anywhere reachable from this repository, so no real translation
evaluation could be run — and none was fabricated.
