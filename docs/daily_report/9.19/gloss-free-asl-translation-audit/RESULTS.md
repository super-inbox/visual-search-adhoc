# gloss-free-asl-translation audit — task (c)

Date: 2026-09-19 · Scope: local R&D audit only. **No training, no commit, no push, no task (b).**
Classification: **B — PIPELINE WORKS, NO TRAINED CHECKPOINT**

> The code and the MediaPipe pipeline run. **The trained ASL→English model does not exist**, so no translation was produced and no evaluation was run. These are two different statements.

## 1. Upstream repository

`https://github.com/yyouretoast/gloss-free-asl-translation` · cloned at `/Users/baobaoli/Desktop/gloss-free-asl-translation` · branch `main`, working tree clean before and after (tracked files unmodified). Description: "Landmark-based continuous ASL-to-English translation system using MediaPipe Holistic landmarks, a Conformer encoder, and a fine-tuned pretrained T5 decoder." Solo project by one author; 94 commits, 2 stars, 0 forks, 0 issues, last push 2026-07-01.

## 2. Exact commit SHA

**`5b7eb92ff90c4ac5907bc6328edb79c24cec6c77`** ("Update kaggle_training.ipynb path resolvers and add generation tuning options to README", 2026-07-01). Confirmed equal to `origin/main` via `git ls-remote`.

## 3. License

MIT, © 2026 Yassin (`LICENSE` present). Commercially usable for the code. **This licence covers code only.** There are no weights, and any future weights would also be bound by the licences of their training data (How2Sign's terms were not re-checked here) and of the base T5.

Files: `README.md`, `LICENSE`, `requirements.txt`, `pyproject.toml` all exist. No `setup.py`, `configs/`, or shell scripts. There is a `.github/workflows/ci.yml` (ruff + pytest on 3.10–3.12).

## 4. Architecture (answers to the Phase 1 questions)

| # | Question | Answer (with source) |
|---|---|---|
| 1 | Uses MediaPipe? | **YES.** `src/data_pipeline.py` imports `mediapipe` and pins `mediapipe==0.10.14`. |
| 2 | Which API? | Legacy **`mediapipe.solutions.holistic.Holistic`** (removed in newer MediaPipe, hence the pin). |
| 3 | Holistic? | **YES**, `static_image_mode=False`, `model_complexity=1`, `refine_face_landmarks=False`, detection/tracking confidence 0.5. |
| 4 | Landmarks used | Pose, left hand, right hand, and a **92-point subset of the 468-point face mesh** (lips 40, each eye 16, each eyebrow 10). |
| 5 | Counts | pose **33**, left hand **21**, right hand **21**, face **92** (of 468). Total 167 landmarks. |
| 6 | Model feature dim | **501** with face (99+63+63+276), **225** without (`--no_face`). Measured on real extracted clips, see §9/§10. |
| 7 | x/y or x/y/z | **x/y/z** for every stream (MediaPipe z = relative depth). |
| 8 | Visibility used? | The extractor **stores** pose visibility (`pose` is `(T,33,4)`), but `ASLLandmarkDataset` slices `[..., :3]` for `.npz`, so **visibility never reaches the model**. Hand and face have no confidence at all. |
| 9 | Missing landmarks | **All zeros** for the missing stream in that frame. There is no mask channel and no flag. Hands stay exactly 0 after normalisation, so the model sees a missing hand as an all-zero block. |
| 10 | Normalisation | Pose: subtract mid-shoulder (idx 11, 12), divide by 3D shoulder width (fallback 0.25 if < 0.05). Hands: subtract own wrist (idx 0), divide by shoulder width. Face: subtract face centroid, divide by shoulder width. So hand and face streams are **local-frame only**. Absolute hand position is carried by the pose wrists. |
| 11 | Pad / truncate | Frames: uniform stride `ceil(T/150)` down to ≤ `max_len`=150 (`src/dataset.py`), then batch zero-padding with an attention mask. Text: tokenised to `max_target_len`=30 tokens. |
| 12 | Long videos | **No chunking or segmentation.** A 618-frame clip becomes 124 frames (stride 5) → 62 encoder frames. At generation, `scripts/inference.py` and `scripts/evaluate.py` hard-code `max_new_tokens=30`, so any output is capped at 30 tokens (the LONG reference is 78 words). |
| 13 | Architecture | Landmarks → Linear+LayerNorm → strided Conv1d (÷2) → sinusoidal PE → 4 Conformer blocks (d_model 512, 4 heads, kernel 31) → optional gated fusion with I3D → MLP "modality bridge" → T5 decoder cross-attention. |
| 14 | Conformer part | `src/models/manual_encoder.py`, a from-scratch Macaron-style encoder (**randomly initialised, must be trained**). |
| 15 | T5 part | `src/models/translation_model.py` loads pretrained `T5ForConditionalGeneration`, **deletes the T5 encoder**, and uses only the decoder. Default `t5-small`; the notebook uses `google/flan-t5-base`. |
| 16 | Raw video into inference? | **NO.** `scripts/inference.py` and `evaluate.py` accept only `.npz`/`.npy` landmark files. |
| 17 | Landmarks first? | **YES.** `ASLLandmarkExtractor` has no CLI (`data_pipeline.py` has no `__main__`), so a single-video run needs a small driver (`run_mediapipe_extraction.py`). |

Two input formats are supported: (a) `.npz` from this repo's own extractor (pose/left_hand/right_hand/face dict), and (b) `.npy` `(T,543,3)` from the Kaggle "How2Sign Holistic" dataset (assumed layout pose 0:33, face 33:501, LH 501:522, RH 522:543). The training data path the notebook actually uses is (b) plus precomputed I3D features (44 GB + 8 GB).

**README/code discrepancy found:** the README says `.npz` input gives **534** dims (and 258 without face). Measured on a freshly extracted `.npz`, the repo's own loader yields **501 / 225**, because it drops pose visibility. The `input_dim=534` default in `ASLTranslationModel` and the tests is stale. If a checkpoint were ever published, `input_dim` must be taken from the checkpoint, not the README.

## 5. MediaPipe landmark schema

| Stream | Extractor output | After `ASLLandmarkDataset` | Model dims |
|---|---|---|---|
| pose | `(T,33,4)` x,y,z,visibility | `(T,33,3)` | 99 |
| left_hand | `(T,21,3)` | `(T,21,3)` | 63 |
| right_hand | `(T,21,3)` | `(T,21,3)` | 63 |
| face | `(T,92,3)` | `(T,92,3)` | 276 |
| **concat** | | | **501** (225 without face) |

x,y are normalised image coordinates in [0,1]; z is MediaPipe relative depth.

## 6. Comparison with our RTMPose pipeline

Both were run on the **same LONG clip** (`FzmL8SL6Bow_1-8-rgb_front`); RTMPose data is the existing `trajectory_probe/…/landmarks.json`. Raw numbers: `mediapipe_vs_rtmpose_comparison.json`.

| Aspect | Our RTMPose / rtmlib | This repo (MediaPipe Holistic) |
|---|---|---|
| Schema | `coco_wholebody_133` | MediaPipe Holistic 33 + 21 + 21 + 468 (92 used) |
| Pose | COCO-17 body + 6 feet | 33-point BlazePose (incl. mouth, eye inner/outer, hand-tip points, heels, foot index) |
| Hands | 21 + 21 (indices 91:133) | 21 + 21 (separate streams) |
| Face | 68-point (23:91) | 468-point mesh, 92-point subset |
| Coordinates | **2D pixels** `(133,2)` (x up to 1034, **y up to 909 on a 720-px-tall frame**, i.e. it extrapolates off-frame) | **3D**, normalised [0,1] + relative-depth z |
| Confidence | `keypoints_score` `(133,)`, SimCC scores, observed range 0.09–1.23 (**not** a probability) | pose visibility [0,1] (present in extractor output, **unused by model**); none for hand/face |
| Normalisation | none in the raw JSON | mid-shoulder/wrist/centroid + shoulder-width scaling |
| Missing points | RTMPose emitted hands in **all 618 frames** (0 frames with mean hand score < 0.3) | zero-fill; **LONG: left hand missing 210/618 (34.0%), right 251/618 (40.6%)**; SHORT: 1/141 (0.7%) and 8/141 (5.7%) |
| Sequence shape | `(T,133,2)` + `(T,133)`, all frames, JSON | `(T,501)`, uniform-stride ≤150 frames |
| Speed (CPU, Apple Silicon; **not a controlled benchmark**: different days, different load) | 37.2 s for 618 frames (recorded 2026-09-10 in the JSON) | 15.2 s for 618 frames (40.7 fps) |
| Downstream input | our own trajectory/diagnostic code | Conformer expecting a `(B,T,501)` float tensor |

**Agreement on shared joints (LONG, 618 frames, error as fraction of frame size, after x/W, y/H):** shoulders 0.006, nose 0.008, pose wrists 0.016–0.022, hand wrists 0.015–0.017 (median ≈ 0.009). Left/right conventions match: same-side wrist error ≈ 0.015 vs ≈ 0.146 cross-side. The two trackers therefore localise shared joints to within about 1–2 % of the frame.

**Caveat on the missing-hand rates:** there is no ground truth. RTMPose always emits all 133 keypoints for the detected person, so "never missing" is partly by design and does not prove it is more accurate.

Explicit answers:

1. **Schema-compatible? No.** Different keypoint sets, coordinate space (pixels vs normalised), dimensionality (2D vs 3D), face topology (68 vs 468), confidence semantics, and container (JSON vs `.npz`/`.npy`).
2. **Can our RTMPose JSON be fed directly into this repo? No.** `ASLLandmarkDataset` only reads `.npz`/`.npy` with the MediaPipe keys or the `(T,543,3)` layout. Feeding the JSON would fail or, if force-reshaped, give meaningless input.
3. **Adapter possible in principle? Partly.** Hands (21↔21, wrist agreement verified above; finger order assumed identical, not verified beyond the wrist) and the shared body joints (shoulders, elbows, wrists, hips, knees, ankles, nose, eyes, ears) map cleanly. Pixel→normalised is trivial. The rest would need to be fabricated or approximated.
4. **Would an adapter lose information the model needs? Yes.** (a) z-depth: RTMPose is 2D only, so z would be zero or estimated, a distribution shift for a model whose 1/3 of input channels are z. (b) Face: 68-point iBUG → the 92-of-468 mesh subset has no exact correspondents for most lip/eyelid points; the very non-manual detail the repo advertises would be degraded. (c) BlazePose extra points (mouth, hand tips, heel/foot index) missing. (d) Visibility. And since **there are no trained weights**, an adapter would only be useful for a from-scratch retraining, where using MediaPipe directly is simpler and consistent with the public MediaPipe How2Sign landmark dataset the repo expects. **No adapter was built.**

## 7. Environment setup

| Item | Value |
|---|---|
| Machine | macOS 14.1, arm64 (Apple Silicon), CPU only (`CUDA is NOT available`) |
| Python | **3.12.4** (Homebrew) in `.venv` inside the repo (gitignored). Repo says ≥3.10; CI matrix 3.10/3.11/3.12 |
| pip | 24.0 in fresh venv → upgraded to 26.2.1 |
| Method | `pip install -r requirements.txt` (README) then `pip install -e .` (from repo CI) |
| Key versions | torch 2.10.0, transformers 4.57.6, mediapipe 0.10.14, numpy 2.5.3, opencv-python 4.14.0.94 + opencv-contrib-python 5.0.0.93 (pulled by mediapipe; `cv2.__version__` = 5.0.0), protobuf 4.25.9, sacrebleu 2.6.0, jiwer 3.1.0, safetensors 0.8.0, onnx 1.22.0, pytest 9.1.1 |
| Install result | **SUCCESS**, ~37 s, no errors |
| `python -m scripts.check_environment` | Runs. torch, mediapipe 0.10.14, onnx, safetensors, jiwer, sacrebleu import OK. `onnxruntime` **not installed** (listed by `check_environment.py` but absent from requirements.txt; nothing else in the repo imports it, so it is harmless) |

Workarounds (no source edits): (1) README's install steps omit `pip install -e .`, without which `pytest tests/` fails on `ModuleNotFoundError: No module named 'src'` (the repo's own CI runs it). (2) None needed for numpy 2.x or the dual OpenCV wheels; both worked. **Diff to tracked files: none.**

## 8. Tests

| Command | Result |
|---|---|
| `pytest tests/ -v -m "not slow"` (the README command) | **6 passed, 5 deselected**, 1 warning (expected empty-label warning). Before `pip install -e .`: 2 collection errors (see above) |
| `pytest tests/ -v -m "slow"` (extra) | **5 passed**, incl. `test_pipeline_extraction` (MediaPipe on a synthetic noise video), `test_model_forward`, `test_model_generate`, `test_model_multi_stream_fusion` (each with untrained `t5-small` + random Conformer) |
| Total | **11/11 pass** |

Note: the README-recommended `-m "not slow"` **skips the only test that exercises MediaPipe**. The slow extraction test uses random noise (no person), so it validates output shapes only, not detection. Real detection was verified in §9/§10. The slow model tests confirm plumbing on untrained weights and say nothing about translation quality.

## 9. SHORT clip MediaPipe extraction — SUCCESS

`g0uGWjwdOIw_1-8-rgb_front` · `asl-translator/data/public_benchmarks/how2sign_v2/videos/g0uGWjwdOIw_1-8-rgb_front.mp4` · SHA256 matches freeze (`75d6a67f…c8c78`).

| | |
|---|---|
| Video | 1280×720 @ 24 fps, 141 frames, 5.875 s ffprobe (5.91 s manifest) |
| Frames processed | **141 / 141** |
| Extraction runtime | **3.7 s** (38.2 fps, CPU) |
| Output | `data/e2e_landmarks/g0uGWjwdOIw_1-8-rgb_front.npz` (305,560 B, in the third-party repo's gitignored `data/`, not copied) |
| Shapes | pose `(141,33,4)`, left_hand `(141,21,3)`, right_hand `(141,21,3)`, face `(141,92,3)` |
| Model input | `(141, 501)` (with face) / `(141, 225)` (no face); stride 1; |x| max 6.00 |
| Missing frames | pose 0, face 0, **left hand 1 (0.7 %), right hand 8 (5.7 %)** |
| NaN / Inf | 0 / 0 |
| Real data? | Yes: non-zero, pose visibility up to 0.99999, x∈[0.39,0.65], face y∈[0.30,0.44] |
| English reference | "It got a lot to do with math and geometry, geometric designs." |

## 10. LONG clip MediaPipe extraction — SUCCESS

`FzmL8SL6Bow_1-8-rgb_front` · `…/videos/FzmL8SL6Bow_1-8-rgb_front.mp4` · SHA256 matches freeze (`7f42f568…3817f`).

| | |
|---|---|
| Video | 1280×720 @ 24 fps, 618 frames, 25.75 s ffprobe (25.77 s manifest) |
| Frames processed | **618 / 618** |
| Extraction runtime | **15.2 s** (40.7 fps, CPU) |
| Output | `data/e2e_landmarks/FzmL8SL6Bow_1-8-rgb_front.npz` (1,228,009 B) |
| Shapes | pose `(618,33,4)`, left_hand `(618,21,3)`, right_hand `(618,21,3)`, face `(618,92,3)` |
| Model input | **`(124, 501)`** (with face) / `(124, 225)`; **stride 5, so 494 of 618 frames (79.9 %) dropped by uniform stride** before the encoder; then ÷2 → 62 encoder frames; |x| max 6.64 |
| Missing frames | pose 0, face 0, **left hand 210 (34.0 %), right hand 251 (40.6 %)** |
| NaN / Inf | 0 / 0 |
| English reference | "You want to go and clean up that hole you just made and now we are going to go and start winding our hole you just made and start spreading it out just like that and all the while I am pulling it out while my hands here are watching this wall here because this wall here is going to want to get out of control but I'm not going to let it, my hands are there." (78 words) |

Encoder-only plumbing check on the real LONG landmarks (random-init Conformer, hidden states, **not a translation**): input `(1,124,501)` → output `(1,62,512)`, all finite.

Comparison with Uni-Sign on the same clip (from the earlier E2E report): Uni-Sign randomly drops 59 % of frames, this repo uniformly strides away 80 %. Neither feeds the full clip to the model.

## 11. Trained checkpoint availability — **C: no trained ASL translation checkpoint published**

Full evidence in `checkpoint_search.json`. Summary:

- No weight file in the tree or in any of 94 commits (no blob > 500 kB ever; no `.pt/.pth/.bin/.safetensors/.ckpt/.onnx` in history). No LFS.
- `.gitignore` excludes `results/` and `*.safetensors`.
- README Demo and Results sections are literal placeholders ("will be added here once training is fully complete", "…reported here after the full training run completes").
- GitHub: 0 releases, 0 tags, 0 Actions artifacts, 1 branch, 0 issues.
- Hugging Face: the author's account has only deepfake/other models and Spaces, **no ASL model or Space**. Search for the repo name returns nothing.
- No Drive/Zenodo/wandb/gdown links anywhere.
- `kaggle_training.ipynb` has **0 saved outputs**, so there are no recorded logs or metrics from any real run. Deleted design docs in history show only mock-data dry runs (1 epoch: eval_loss 12.68, BLEU 0.0, WER 1.0; plus an 80-epoch memorisation test on mock data).
- Vanilla T5 weights (`t5-small`, `flan-t5-base`) do exist on Hugging Face but **do not count**: they lack the Conformer and modality bridge trained on landmarks.
- Four other "asl-translation" models turned up on Hugging Face (`elpeeee/asl_translation_model`, `Muthukumar045454/asl-translation-t5`, `pedrofalconi/asl-translation`, `AlexD281/Gemma4-ASL-Translation-LoRA`). They are unrelated third-party projects, not referenced by this repo, and not trained with this architecture. **Not used.**

Residual uncertainty: the author may hold private Kaggle output from a real run. That cannot be verified from public sources.

## 12. Real inference result

**Not performed. Not possible.** With no trained checkpoint, running `scripts/inference.py` would require either a random-init Conformer or a vanilla-T5-plus-random bridge, either of which emits garbage. Per the task rules, no untrained output was presented as translation. No WER/CER/BLEU/chrF were computed, and there is no `predictions.json` or `metrics.json` (deliberately). **No evaluation was fabricated and no real translation inference was performed.**

## 13. Small evaluation result

**Not performed** (gated on §12). No subset, no metrics.

## 14. Blockers

**One blocker: the trained artifact is missing.** Specifically: a `model.safetensors` / `pytorch_model.bin` produced by `python -m src.train` on MediaPipe landmarks + English text (state_dict keys `encoder.*`, `modality_bridge.*`, `t5.*`, optionally `i3d_projection.*`/`gate_conv.*`). Anything published would also need to state `input_dim` (501/225/…), the T5 variant (`t5-small` vs `google/flan-t5-base`), and whether I3D fusion was used, because `inference.py` needs all of these to rebuild the model.

There is no technical blocker in the code or environment. It installs, tests pass, and MediaPipe extraction works on both clips. **This is an upstream-artifact blocker (the author has not published trained weights), not a local pipeline failure.** No training was started on our side.

What training would need (documented in repo; **not attempted**):
- Data: How2Sign "Holistic" MediaPipe landmarks (Kaggle dataset, ~44 GB), plus the I3D features (~8 GB) for the fusion variant, plus `realigned_train` CSV/TSV metadata (with signer IDs for the signer-independent split). Sentence-level; ~31,000 folders; preprocessing ≈ 2 h if starting from video.
- Compute: written for Kaggle GPUs; the default run is 50 epochs, batch 8 × grad-accum 8 (effective 64), Adafactor, fp16, gradient checkpointing. The repo documents **no** exact GPU hours or VRAM requirement (a memory profiler exists but no numbers are recorded).
- Cost: not documented by the repo and not estimated here. Training was out of scope.
- Expected quality: the author's own notes say benchmark SOTA is ≈12 BLEU and to expect lower for a solo build. Do not expect a strong model.

Contacting the author for weights is a **reasonable, cheap next step**: the repo is small, recently active (last push 2026-07-01), the notebook is written for exactly this run, and GitHub Issues is enabled on the repo. Whether any full-data run was ever completed is unknown.

## 15. Recommendation

1. **Report "B — PIPELINE WORKS, NO TRAINED CHECKPOINT".** Do not report this repo as an evaluable ASL→English system.
2. **Optionally ask the author** (GitHub issue) whether a trained checkpoint exists and, if so, its `input_dim`, T5 variant, and I3D setting. Nothing else is required from us to be ready: the loader and extractor already run on our clips.
3. **Do not train it on our side** without an explicit decision: it needs multi-GB data and GPU time for a landmark→T5 model whose author expects low absolute scores, and whose 30-token generation cap and 150-frame stride would truncate a 78-word / 618-frame clip like our LONG one.
4. **Do not build an RTMPose→MediaPipe adapter now.** There are no weights to feed, and an adapter would drop z-depth and dense-face information.
5. Proceed to task (b) per the manager's a → c → b order.

---

## Files created (research repo, this folder only)

`RESULTS.md`, `MANAGER_SUMMARY.md`, `checkpoint_search.json`, `mediapipe_short_summary.json`, `mediapipe_long_summary.json`, `mediapipe_vs_rtmpose_comparison.json`, `run_mediapipe_extraction.py`, `compare_mediapipe_vs_rtmpose.py`.
Third-party repo: only gitignored artefacts (`.venv/`, `*.egg-info/`, `.pytest_cache/`, `__pycache__/`, `data/e2e_landmarks/*.npz`). No tracked file changed.
