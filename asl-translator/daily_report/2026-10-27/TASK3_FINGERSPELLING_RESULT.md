# Task 3 — fingerspelling specialist follow-up (2026-10-27)

**Bottom line**
- **OpenFS:** runs locally and is deterministic run-to-run.
  - The boss's old-window strings **partially** reproduce. His exact input videos are not on this machine.
  - R02/R05 official-window outputs are recorded. R35 is run but kept separate.
- **FS-Detection:** does **not** run as published on this machine (CUDA hard-coded; PyTorch 1.1 and Warp-CTC not
  installable). With three runtime shims it **loads its pretrained checkpoint and produces stage-1 proposals on
  CPU**.
- **Nothing here is ground truth:**
  - OpenFS strings are technical recognizer output;
  - FS-Detection intervals are unvalidated proposals;
  - `fs_present` stays **unknown**;
  - there is no accuracy claim and no translation-improvement claim.

**Task definition:** [THREE_P0_EXECUTION_REPORT.md](THREE_P0_EXECUTION_REPORT.md) §任务三 and
[PROTOCOL.md](../../experiments/p0-2026-10-27/PROTOCOL.md) §B.

**Rules followed:**
- No reference name, lexicon or candidate list was supplied to any model.
- No human labels were used.
- CPU only.
- No production/Gemini path was touched. Anti-repetition and sampling were not reopened.

## A. OpenFS setup and reproduction of the boss's old-window outputs

| Item | Value |
|---|---|
| Repo / commit | github.com/AIRC-KETI/OpenFS @ `0d6fa3fa9b5aeaf99171e8c77e89531a22a6fd27` (same as boss) |
| Checkpoint | `download_ckpts.sh` → Google Drive `1Ox2sIOtDsafn1TcVg6LQlt7m-gq9xVuq` (recognizer.zip sha256 `b7a562e1…`). `recognizer/best_model.pth` sha256 `c8e4c227…2925` = **boss's checkpoint** |
| Archived config | 2D input, `input_dim` 42 (21 hand points × xy), d_model 256, 8 heads, 3 layers, ff 2048 |
| Runner | boss's `specialist.py`, **unchanged**. Both of his torch shims activate here too (torch 2.2.2 lacks `F._check_key_padding_mask` and `torch.backends.mha`); no weight change |
| Input representation / preprocessing | Video → MediaPipe Holistic (complexity 1, full frame, single signer, no YOLO crop) → hands kept only if wrist above elbow → per-hand upstream `normalize` → greedy open-vocabulary letters (max 32). Whole clip + fixed 2 s windows at 1 s stride |
| Environment | Apple M3 Pro; Python 3.11.7 **x86_64 under Rosetta**; torch 2.2.2 CPU; mediapipe 0.10.9; numpy 1.26.4; opencv 4.11; 2 threads. Boss: Intel macOS, same Python/torch/mediapipe pins |
| Licence | OpenFS Non-Commercial Research License (code and checkpoints). Research diagnostic only; weights, code and videos are not committed |

**The boss's inputs are not available.** He ran on compressed OLD-window display re-encodes (R02 sha256 `33a0432e…`,
R05 `f0c93833…`, R35 `e9eef614…`, R41 `f0018ceb…`). None is on this machine. Two closest local inputs were used:
1. the B clip the display video was re-encoded from (`how2sign_v2/videos`, same frame count; provenance B VERIFIED);
2. the reviewer-package raw cut at the original annotation.

| Input | Windows | Exact string match with boss |
|---|---|---|
| B clip (how2sign_v2) | 18 (all of the boss's) | **10 / 18**: fixed windows 9/14, whole-clip 1/4 |
| Reviewer-package raw cut (R02/R05/R35 only) | 15 | 6 / 15 |
| Same B-clip inputs, second run | 18 | **identical to the first run** (deterministic) |

Per window, B clip vs boss:

| Case | Window (clip s) | Boss | Ours | Match |
|---|---|---|---|---|
| R02 | whole 0–4.21 | `camilian surtite` | `cammilian surtite` | no |
| R02 | 0–2 / 1–3 / 2–4 | `camilian` / `linsusti` / `sustitie` | `camilian` / `linsusti` / `sustie` | yes / yes / no |
| R05 | whole 0–5.25 | `liswithey guor` | `liswithey gurer` | no |
| R05 | 0–2 / 1–3 / 2–4 / 3–5 | `lisw hill` / `whailey` / `eygu` / `viter` | `lisw hill` / `whattey` / `eygu` / `revitor` | yes / no / yes / no |
| R35 | whole 0–6 | `bag yoga` | `pig` | no |
| R35 | 0–2 / 1–3 / 2–4 / 3–5 / 4–6 | `back` / `is` / `if` / `so` / `fo` | `back` / `if` / `if` / `mare` / `fo` | yes / no / yes / no / yes |
| R41 | whole / 0–2 / 1–3 | `ship` / `bs` / `shi` | `ship` / `bs` / `shi` | **all yes** |

**Why they differ.** The MediaPipe hand-observation counts differ from the boss's (R02 left hand 58 vs 57; R05 52 vs
49; R41 78/88 vs 73/83). The input pixels differ (re-encode vs source clip), and so does the platform (x86 under
Rosetta vs native Intel). Greedy decoding then amplifies small landmark changes into different letters. **Conclusion:
the setup is reproduced (same commit, checkpoint, code path), and the boss's strings reproduce only partially.**
Every difference is visible in `specialist_openfs_reproduction.json`.

## B. OpenFS on official-window inputs

Same runner and checkpoint. Inputs are the full-resolution reviewer-package official clips (full frame, 1280×720,
24 fps).

| Run | Source clip | Source span (s) | Span basis | Frames | Runtime (CPU) |
|---|---|---|---|---|---|
| R02 official | reviewer `R02-official.mp4` (sha256 `47ce8742…`) | 1.43–11.69 | realigned cut. A_official provenance **VERIFIED** slice 1.4583–11.7083, same 246 frames | 246 | 12.0 s |
| R05 official | reviewer `R05-official.mp4` (`1a394bf2…`) | 0.76–8.33 | realigned cut. A_official **VERIFIED** slice 0.7917–8.375 (182 vs 181 frames) | 181 | 8.7 s |
| R35 official (A) | official Uni-Sign crop clip `crop_test/G2kVb4gINSI_1-10-rgb_front.mp4` (`5dd48161…`), the exact A model-input video | **UNRESOLVED** | Amendment 2 crop-box margin 0.034 < 0.05 | 93 | 4.4 s |
| R35 official (B) | reviewer `R35-official.mp4` (`20383848…`) | 13.11–16.90 | annotation cut, **not provenance-verified** | 91 | 4.5 s |

Exact output strings (fixed windows are clip-relative seconds; uncalibrated mean token probability in parentheses):

| Run | Whole clip | 0–2 | 1–3 | 2–4 | 3–5 | 4–6 | 5–7 | 6–8 | 7–9 | 8–10 |
|---|---|---|---|---|---|---|---|---|---|---|
| **R02 official** | `gnikcal mannnyestile filllba` | `gnikc` | `mile camel` | `camilians` (0.82) | `ynosuretive` | `stie` | `elity` | `yllib back` | `app` | `kcaf` |
| **R05 official** | `blisswity grourt` | `lisw` | `swhattey` (0.76) | `tiley` | `gunits` | `volor` | `rt` | | | |
| R35 crop clip | `linling gos` | `fillion` | `lingo` | | | | | | | |
| R35 reviewer cut | `linling` | `fillion` | `ling` | | | | | | | |

Every window has status `unverified_proposal`, `fs_present` null/unknown, and character timestamps null.

**R35 is kept separate:**
- Its old window (6.50–12.48 s) and official window (realigned 13.11–16.90 s) do not overlap.
- Its official source span is UNRESOLVED.
- So no old-vs-official comparison is made.
- The two official-window inputs (crop clip vs full-frame annotation cut) give similar strings. That says nothing
  about correctness.

### Old vs official (R02, R05): descriptive only

Both slices are provenance VERIFIED, so the old windows can be placed in official-clip time. The 2 s windows overlap
by 1.875 s (R02) or 1.542 s (R05) but are **not identical**, so these pairs are descriptive only:

| Case | Old window (source s) | Old (ours / boss) | Nearest official window (source s) | Official |
|---|---|---|---|---|
| R02 | 3.33–5.33 | `camilian` / `camilian` | 3.46–5.46 | `camilians` |
| R02 | 4.33–6.33 | `linsusti` / `linsusti` | 4.46–6.46 | `ynosuretive` |
| R02 | 5.33–7.33 | `sustie` / `sustitie` | 5.46–7.46 | `stie` |
| R05 | 1.25–3.25 | `lisw hill` / `lisw hill` | 0.79–2.79 | `lisw` |
| R05 | 2.25–4.25 | `whattey` / `whailey` | 1.79–3.79 | `swhattey` |
| R05 | 3.25–5.25 | `eygu` / `eygu` | 2.79–4.79 | `tiley` |
| R05 | 4.25–6.25 | `revitor` / `viter` | 3.79–5.79 | `gunits` |

The official window also covers time the old window did not:
- R02 adds 1.43–3.31 s and 7.50–11.69 s.
- R05 adds 0.76–1.22 s and 6.47–8.33 s.
- These add new strings such as R02 `mile camel` (source ≈ 2.46–4.46 s), `yllib back` and `kcaf`.

Whether any window contains fingerspelling, and what letters, can only come from ASL-fluent blind labels. **No
string is compared with the reference sentence here.**

## C. FS-Detection feasibility

| Item | Value |
|---|---|
| Repo / commit | github.com/chevalierNoir/FS-Detection @ `b386f04d90b88daf9f7bf598e5ca7075d8376421` (CVPR 2021). **No LICENSE file** (all rights reserved by default) |
| Checkpoint | README "Pretrained models": Google Drive `1zl1Pq54E55mrYQHE4qwZzVz-mBr3U0w5`. `fswild-plus.zip` (sha256 `640789ab…`) → `pwd/best-dev.pth` (`004d4abc…`, 51 tensors) + `train_conf.yaml`. ChicagoFSWild+ detector, README AP@0.5 0.448, stage 1 |
| Expected input | RGB video resampled to 29.97 fps, letterboxed to 640×360, center-cropped 360², ×0.3 → 108×108, ImageNet-normalized. Farneback optical-flow magnitude video. For data loading: OpenPose JSON (25 body + 42 hand) and a signer bbox file, plus a train `scp` only to size the feature map. Pose and bbox are **not used** at stage-1 inference |
| Model | VGG19-style 2D conv features → 3D conv → temporal RPN (proposals) + attention-LSTM recognizer head (training/reward only) |

**Setup test (`fs_detection_smoke.py`):**

| Stage | Result |
|---|---|
| Install pinned deps: `torch==1.1.0`, `numpy==1.16.4`, `warpctc-pytorch==0.2.2+torch11.cpu` (Python 3.11) | **FAIL**: no torch 1.1.0 wheel (only 2.0.0–2.2.2 available); numpy 1.16.4 has no wheel; Warp-CTC wheel not found |
| A. As-is construction on CPU (torch 2.2.2) | **FAIL** at `rpn.py:35` `self.anchor_scales = ….to(self.device)`: `AssertionError: Torch not compiled with CUDA enabled` (RPN default `device=torch.device('cuda')`; `evaluate.py` also hard-codes `cuda`) |
| B. Construction with shims | PASS. Shims: `ctc_type='builtin'` (upstream's own option; CTC is a training loss), RPN `device=cpu`, VGG19 ImageNet init download skipped (overwritten by the checkpoint). No weight change |
| C. `load_state_dict(strict=True)` | PASS: 51 tensors, 0 missing, 0 unexpected |
| D. Stage-1 forward on CPU, R02 / R05 official | PASS: 307 / 226 frames at 29.97 fps; forward 26.2 s / 19.0 s; 49 / 48 valid proposals |

**Dependency matrix:**

| Component | Pinned | Here | Status |
|---|---|---|---|
| torch | 1.1.0 | 2.2.2 CPU | pin unavailable; model code runs on 2.2.2 |
| torchvision | 0.2.0 | 0.17.2 | transforms only |
| numpy / opencv | 1.16.4 / 4.1.0.25 | 1.26.4 / 4.11 | work |
| Warp-CTC | 0.2.2 (torch 1.1) | absent | training-only; `builtin` CTC substitutes |
| CUDA | hard-coded device | none | needs a 1-line device override |
| OpenPose JSON + bbox | required by the loader | bypassed | sample built in memory |
| Python | 3.6/3.7 era | 3.11.7 | imports fine |

**Smoke proposals** (uncalibrated scores, unvalidated; top 5 in the CSV, top 50 in the JSON):
- **R02 official:** the 8 proposals scoring ≥ 0.99 lie in clip 0.80–4.27 s (source ≈ 2.26–5.73 s) plus 9.34–10.21 s.
  Scores range 0.32–0.9997, median 0.68.
- **R05 official:** the 7 proposals scoring ≥ 0.99 lie in clip 0.73–3.40 s (source ≈ 1.53–4.19 s) plus 4.74–5.47 s.
  Scores range 0.05–0.9995, median 0.37.

These are `interval_source = detector`, `fs_present = unknown`. They were not run through upstream NMS / `measure.py`.
The detector was trained on ChicagoFSWild+ (YouTube, in the wild), not How2Sign studio video. CPU/torch-2.2 equivalence
to the paper's GPU/torch-1.1 outputs is **not verified**, because the repo ships no reference sample.

**Remaining work for a faithful pipeline:**
- stage-2 detector (needs signer bbox / local crops);
- upstream NMS and proposal post-processing;
- flow through an H.264 round trip as upstream does;
- a reference-equivalence check.

Estimated at about 0.5–1 day.

**Is porting justified for R02/R05/R35 only?** No.
- Its proposals cannot be validated without blind span labels.
- For three cases, a human reviewer marking spans directly is cheaper, and is the ground truth anyway.

FS-Detection is practical to continue only if a larger detection need appears (many clips, or a production path).
That would also need a licence answer from the authors.

## Task 3 conclusion

1. **Runnable:**
   - OpenFS recognizer on CPU, deterministic, same commit and checkpoint as the boss;
   - FS-Detection stage-1 on CPU with three shims.
2. **Diagnostic signal:**
   - OpenFS old-window strings reproduce only partially (10/18 windows) when the input encode or platform changes.
     So any single string is fragile and should not be trusted on its own.
   - The R02/R05 official windows produce different and longer strings than the old windows, including in the time
     ranges only the official window covers.
   - FS-Detection's highest-scoring proposals fall early in both official clips.
3. **Translation-quality improvement:** none claimed. No ground truth, no fusion, no sentence replacement.

**Next step that would turn this into evidence:** ASL-fluent blind labels for R02/R05 (both windows) and R35 (both
windows):
- `fs_present`;
- span;
- letters.

Against those labels, the OpenFS strings and FS-Detection proposals in the result files can be scored without
re-running anything.

## Files

`asl-translator/experiments/p0-2026-10-27/`:
- `fs_detection_smoke.py`: staged FS-Detection CPU setup test (as-is → shims → strict load → forward).
- `build_specialist_task3.py`: assembles the result files from the raw runs (no model).
- `results/specialist_openfs_reproduction.json`: setup, boss vs ours per window, determinism repeat, raw outputs.
- `results/specialist_openfs_official.json`: official-window runs (R02, R05; R35 separate), old-vs-official overlap
  table, raw outputs.
- `results/fs_detection_feasibility.json`: stages, exact errors, dependency matrix, pinned-install attempts, porting
  estimate, top-50 proposals.
- `results/specialist_cases.csv`: one row per window / proposal.

Not modified: the boss's `specialist.py` and `results/specialist.json`, `PROTOCOL.md`, provenance, Task 1/2 outputs.
OpenFS / FS-Detection code, checkpoints, the venvs and the R35 crop clip live in scratch only.

## Reproduce

```bash
# OpenFS: clone @0d6fa3fa, gdown 1Ox2sIOtDsafn1TcVg6LQlt7m-gq9xVuq; venv numpy==1.26.4 torch==2.2.2 mediapipe==0.10.9 omegaconf==2.3.0 scipy opencv-python
python -I asl-translator/experiments/p0-2026-10-27/specialist.py --openfs <OpenFS> \
  --checkpoint <OpenFS>/outputs_save/recognizer/best_model.pth --manifest <manifest.json> --out <raw.json>
# manifests: [{"case_id","video","domain"}] with the inputs listed in sections A and B
# FS-Detection: clone @b386f04d, gdown 1zl1Pq54E55mrYQHE4qwZzVz-mBr3U0w5; venv torch==2.2.2 torchvision==0.17.2 numpy==1.26.4 opencv-python ConfigArgParse==1.2.3 editdistance pyyaml
python -I asl-translator/experiments/p0-2026-10-27/fs_detection_smoke.py --src <FS-Detection>/src --ckpt-dir <pwd> \
  --clips R02=<R02-official.mp4>,R05=<R05-official.mp4> --spans R02=1.4583,R05=0.7917 --top-k 50 --out <fsdet.json>
python -I asl-translator/experiments/p0-2026-10-27/build_specialist_task3.py --old <raw_old> --repeat <raw_repeat> \
  --official <raw_official> --fsdet <fsdet.json> --env <env.json>
```
