# E0 — Results

Date: 2026-10-05. No training, no new model inference, no product/frontend changes, nothing committed.

## 1. Bottom line

- **Official *inference* reproduction: not done. Blocked.** The official
  `fine_tuning.py --eval` path needs a CUDA GPU (hardcoded `.cuda()` + deepspeed
  engine) and BLEURT. Neither is on this machine. The official pose files
  (public, 8.47 GB) were not downloaded, because they don't unblock the path
  without a GPU. Per the stop rule, I did not run a patched CPU approximation.
- **Official *scoring* reproduction: succeeded exactly.** Re-scoring the
  authors' released How2Sign predictions (`out/eval_how2sign_pose_only/`)
  with the official BLEU code gives **14.50**, the paper's pose-only number.
- **The 14.5 vs 5.4 gap now splits roughly in half**, measured on the same 128 clips,
  same references, same scorer:

| Predictions | Clips | BLEU-4 |
|---|---|---|
| Authors' released predictions | full How2Sign test (2,349) | **14.50** (paper: 14.5) |
| Authors' released predictions | **our 128 clips** | **9.59** |
| Our predictions (9.2 run) | our 128 clips | **5.39** |

So: **≈ 4.9 BLEU from benchmark difficulty, ≈ 4.2 BLEU from our inference pipeline.**
Both are measured, not estimated.

## 2. What was run

| Run | Command (from the Uni-Sign repo root @ `eed438bc`) | Output |
|---|---|---|
| R1: score official released outputs, official BLEU | `python <this dir>/scripts/score_official_out.py` | BLEU-1..4 = 39.38 / 26.44 / 19.22 / **14.50**; pip sacrebleu 2.2.0 = 14.4988 (identical); signature `42.3/19.1/10.9/6.7 BP=0.932 ratio=0.934 hyp_len=42943 ref_len=45980` |
| R2: official vs ours on our 128 | `python <this dir>/scripts/subset_analysis.py <Uni-Sign dir> out.json` (run from the visual-search-adhoc repo root) | see §1 table and `data/official_vs_ours_128clip_per_clip.json` |
| R3: length breakdown | inline script; buckets from `manifest.csv` duration and frame counts in `batch_run_128.log` | `data/length_bucket_breakdown.json` |

Python: `/opt/anaconda3/envs/unisign-cpu-arm64` (torch 2.1.1, sacrebleu 2.2.0; the official vendored sacrebleu 1.4.2 is imported from the repo).

## 3. Detailed findings

### 3.1 Scoring, labels, and references are not the problem

- Official vendored sacrebleu 1.4.2 and pip sacrebleu give the same BLEU to 4 decimals on both prediction sets.
- All 128 of our clips are in the official `labels.test`. 125/128 references are byte-identical. The other 3 differ only by mojibake in the *official* file (`â` for `’`). Subset BLEU is the same with either reference set (9.59 / 5.39).

### 3.2 Benchmark difficulty is real and large

Our 128 clips were deliberately chosen toward hard categories (long, questions,
numbers, names, fast signing). On those clips the authors' own predictions drop
from 14.50 to **9.59**. So ~5 BLEU of the gap is not ours.

### 3.3 The remaining gap appears within our inference/preprocessing path, and it isn't frame subsampling or truncation

Same 128 clips, authors' predictions vs ours:

| Bucket | n | Authors | Ours | Ours / Authors |
|---|---|---|---|---|
| ≤256 frames (never subsampled) | 94 | 10.54 | 6.22 | 0.59 |
| >256 frames (random subsample to 256) | 34 | 7.71 | 4.30 | 0.56 |
| <5 s | 61 | 9.60 | 5.79 | 0.60 |
| 5–15 s | 47 | 12.39 | 7.17 | 0.58 |
| 15–31 s | 20 | 4.83 | 2.34 | 0.48 |
| **All** | 128 | **9.59** | **5.39** | 0.56 |

- The ratio is ~0.56–0.60 everywhere, including the 94 clips that are never
  subsampled. So the `max_length=256` random-subsampling RNG mismatch can't
  be the main cause.
- Truncation is comparable: 19.5% of the authors' predictions on these clips
  lack terminal punctuation vs 15.6% of ours. `max_new_tokens=100` hits both.
- 0/128 of our predictions are string-identical to the authors'.

The remaining known differences between the two pipelines (`E0_PROTOCOL_COMPARISON.md` §1):

1. **Pose extractor:** RTMPose-x via MMPose (paper App. A.1; official pkls) vs our rtmlib `lightweight` RTMW-dw-l-m 256×192. This is the only *systematic input* difference, and the checkpoint was fine-tuned on the former. **Leading hypothesis, untested.**
2. CPU bf16 vs CUDA bf16 kernels; batch 1 vs 8 (padding is masked via `attention_mask`, `models.py:279-280`). These could flip individual beams, but are unlikely to cost ~40% relative BLEU uniformly. Untested.
3. Generation does not depend on the reference text (`models.py:313-321` uses only `inputs_embeds`/`attention_mask`), so the empty-reference online path is not a factor.

### 3.4 Caveat on the authors' released predictions

`out/eval_how2sign_pose_only/` was uploaded upstream on 2026-01-03 ("upload pose only evaluation result"), after the pose-only checkpoints (2025-12-20). It scores exactly the paper's 14.5. Nothing public states that it was produced by the exact `how2sign_pose_only_slt.pth` file we hold. That link is plausible, but it is not proven until official inference is re-run (C3/C11 in the checklist).

## 4. Exact remaining mismatch (why official reproduction is incomplete)

1. **No CUDA GPU.** `fine_tuning.py` L69/L254/L276 `.cuda()`, deepspeed engine (`utils.py:404-429`), launched with `deepspeed --include localhost:0`.
2. **Official How2Sign pose files not on disk:** `how2sign_pose_format.zip.00–.03` from HF `ZechengLi19/Uni-Sign`, 8,465,474,575 B total, public.
3. **BLEURT not installed:** `bleurt` package + `BLEURT-20` checkpoint. The unmodified How2Sign `--eval` crashes in the BLEURT import before writing prediction files (`fine_tuning.py:292-322`).
4. `config.py` `pose_dirs["How2Sign"]` points at the WLASL directory (upstream bug; needs a local path edit, which the README sanctions).

Items 2–4 are setup work. Item 1 needs hardware.

## 5. Next step

**E0-b: run the official eval on a single CUDA GPU (~1 GPU-hour + ~8.5 GB download).**

1. Download and merge the 4 pose parts, fix `config.py` paths, install BLEURT + BLEURT-20 (or accept the ROUGE/BLEURT-only crash *after* BLEU prints and capture stdout).
2. Run `deepspeed --include localhost:0 fine_tuning.py --batch-size 8 --dataset How2Sign --task SLT --eval --finetune how2sign_pose_only_slt.pth --output_dir out/e0b` (pose-only block of `script/eval_stage3.sh`).
3. Expected: ≈14.5 on full test (confirms C3/C11). Then score our 128 from that output (expected ≈9.6).
4. **Pose-extractor isolation (cheap, same GPU session):** re-extract our 128 clips with the official extractor settings (RTMPose-x) *and* with rtmlib lightweight, feed both through the same official loader, and compare against the official pkls for those clips. That answers directly whether item 3.3-1 explains the 9.6 → 5.4 drop.

If no GPU is available, the fallback is a **documented CPU-patched** run of
the official `S2T_Dataset` + official pkls on our 128 clips only (~1–1.5 h
CPU), clearly labeled as an approximation. That needs your approval, since
it deviates from the official path.

**Implication for the build decision (10.05 boss summary):** the condition
"E0 must reproduce roughly the paper's number" is half-met. The released
outputs reproduce 14.5 exactly, but our own inference path is ~44% below the
authors' on identical clips. Fix or explain that before using Uni-Sign as a
base or deploying the current container.
