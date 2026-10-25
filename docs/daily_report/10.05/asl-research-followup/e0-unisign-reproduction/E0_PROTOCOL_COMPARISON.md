# E0 — Official How2Sign protocol vs. our Curify Uni-Sign setup

Sources: upstream repo @ `eed438bc` (`fine_tuning.py`, `datasets.py`, `utils.py`, `config.py`,
`SLRT_metrics.py`, `external_metrics/sacrebleu.py`, `script/eval_stage3.sh`, `docs/DATASET.md`,
`demo/`), paper arXiv 2501.15187 (§4.2, App. A.1, Table 6/21), HF model repo file listing.
Ours: recovered `batch_inference_cpu_patched.py` and the 9.2 run metadata (see `E0_ENVIRONMENT_AUDIT.md` §4).

## 1. Protocol items

| Item | Official How2Sign evaluation | Ours (5.39 run) | Match? |
|---|---|---|---|
| Checkpoint | `how2sign_pose_only_slt.pth` from HF `ZechengLi19/Uni-Sign` (pose-only, `rgb_support` off) | Same file; sha256 equals the HF LFS oid | **Same released file.** Not proven to be the exact weights behind 14.5 |
| Base LM | `google/mt5-base` at `./pretrained_weight/mt5-base` | HF snapshot `2eb15465…` | Likely same; not hash-verified against the authors |
| Pose source | Pre-extracted `how2sign_pose_format` pkl from HF. Paper App. A.1: "We employ the **RTMPose-x** … from MMPose" | Extracted live with rtmlib `lightweight` (YOLOX-tiny + **RTMW-dw-l-m 256×192**) | **No.** Largest known difference |
| Pose normalization | keypoints / (W, H) per frame (same as `demo/pose_extraction.py`) | Same code | Yes (assuming the official pkls were made the same way) |
| Split | How2Sign **test**, 2,349 clips (`data/How2Sign/labels.test`); no dev set (`fine_tuning.py:51,64`) | 128-clip subset of the same test split, hand-selected toward hard categories | **No** (subset); all 128 are in the official test labels |
| References | `labels.test` `text` field | How2Sign official English TSV | 125/128 byte-identical; 3 differ only by mojibake (`â` vs `’`) in the *official* labels. BLEU on our subset is identical either way (9.59 / 5.39) |
| Dataset loader | `S2T_Dataset` (pkl from disk) | `S2T_Dataset_online` (in-memory dict) | Logic is line-for-line the same for pose-only (`datasets.py:461-497` vs `634-665`) |
| Frame cap | `max_length=256`; longer clips → `random.sample` to 256, sorted | Same | Yes in rule. RNG stream differs (see below) |
| RNG | `set_seed(42)` once; test `DataLoader` with `num_workers` default (8 workers → per-worker RNG); sequential over 2,349 clips | `set_seed(42)` once; no workers; sequential over our 128 | **No.** Subsample draws for clips >256 frames differ. Affects 34/128 of our clips |
| Precision | deepspeed engine, `dtype=bf16` default → bf16 model; inputs `.to(bf16).cuda()` | `model.to(bf16)`, inputs bf16, **CPU** | bf16 on both sides; CPU vs CUDA kernels not bit-identical |
| Batch | `--batch-size 8` (eval script), padded batches | batch 1 | **No.** Effect depends on padding/masking in `Base_Dataset.collate_fn`, not measured |
| Forward | `model(src_input, tgt_input)` with refs (computes loss), then `generate` | `model(src_input, tgt_input)` with empty text, then `generate` | Generation inputs (`inputs_embeds`) don't depend on refs, so this should not matter (not separately tested) |
| Decoding | `generate(max_new_tokens=100, num_beams=4)` (`fine_tuning.py:263-266`) | Same literals | Yes |
| Post-processing | pad first output to 150 with EOS, `pad_sequence`, `batch_decode(skip_special_tokens=True)`; CSL-only char split does **not** apply to How2Sign | Same | Yes |
| Eval script | `deepspeed … fine_tuning.py --dataset How2Sign --task SLT --eval --finetune <ckpt>` (pose-only block of `script/eval_stage3.sh`, with `--dataset` changed) | Custom batch driver built from `demo/online_inference.py` | **No.** Different entry point, same model/decoding code |
| BLEU | `SLRT_metrics.translation_performance` → `sableu(..., tokenizer='13a')` → vendored **sacrebleu 1.4.2** `corpus_bleu`; reported BLEU-4 = `scores[3]` = standard corpus BLEU, exp smoothing, mixed case | `sacrebleu==2.3.1` corpus BLEU, 13a | **Yes, numerically.** Official outputs: vendored 1.4.2 = 14.4988, pip 2.2.0 = 14.4988; ours: both 5.39 |
| Other metrics | ROUGE-L (`rouge` pkg), BLEURT-20 | WER/CER/chrF | n/a for the BLEU comparison |

## 2. Reproduction checklist

| # | Check | Result |
|---|---|---|
| C1 | Official repo pinned, same commit as our run | ✅ `eed438bc` (= upstream HEAD today) |
| C2 | Checkpoint is the released file | ✅ sha256 = HF LFS oid |
| C3 | Checkpoint is provably what produced 14.5 | ⚠️ Not provable from public material |
| C4 | Test labels = official, our clips covered | ✅ 2,349 entries; 128/128 present |
| C5 | Official BLEU implementation reproduces the published number from the authors' own released predictions | ✅ **14.50** (BLEU-1..4 = 39.38 / 26.44 / 19.22 / 14.50; BP 0.932, hyp_len 42,943, ref_len 45,980) |
| C6 | Official released predictions on our 128 clips | ✅ computed: **9.59** |
| C7 | Official poses on disk | ❌ not downloaded (public, 8.47 GB) |
| C8 | CUDA GPU for `fine_tuning.py --eval` | ❌ **blocker** |
| C9 | BLEURT installed (needed for the unmodified How2Sign `--eval` to write outputs) | ❌ **blocker** for the unmodified script |
| C10 | `config.py` How2Sign pose path fixed | ⏸ trivial local edit, not done (nothing to point it at yet) |
| C11 | Official inference re-run on full test → ≈14.5 | ❌ not run (C7–C9) |
| C12 | Official inference on our 128 with official poses | ❌ not run (C7–C8) |

## 3. Gap table (what explains 14.5 → 5.39)

| Gap component | Evidence | Size (BLEU) | Status |
|---|---|---|---|
| Scoring / BLEU implementation / tokenizer | Official code and pip sacrebleu agree to 4 decimals on both prediction sets | **0.0** | Ruled out |
| Reference text differences | 3/128 mojibake only; subset BLEU identical with either reference set | **0.0** | Ruled out |
| Benchmark difficulty (our 128 vs. full 2,349) | Authors' own predictions: 14.50 on full test → **9.59** on our 128 | **≈ −4.9** | Measured |
| Our inference pipeline vs. the authors' (same clips, same refs, same scorer) | Authors' predictions 9.59 vs. ours **5.39** on the identical 128 clips; 0/128 predictions identical | **≈ −4.2** | Measured; cause not yet isolated |
| ↳ frame subsampling / truncation | Gap is similar on clips with ≤256 frames (no subsampling, n=94: 10.54 vs 6.22) and >256 frames (n=34: 7.71 vs 4.30); also similar across <5 s / 5–15 s / 15–31 s | Not the main driver | Largely ruled out as *the* cause |
| ↳ pose extractor (RTMPose-x pkl vs rtmlib lightweight RTMW-dw-l-m) | Only systematic input difference; checkpoint was trained on the former | Unknown | **Leading hypothesis, untested** |
| ↳ CPU bf16 vs CUDA bf16, batch 8 vs 1 | Numeric differences can flip beam choices, but usually don't cut BLEU by ~40% relative | Unknown, likely small | Untested |
| Release vs. paper | Released predictions score exactly 14.50 = paper Table 6/21 pose-only | 0.0 at the prediction level | Consistent; full inference re-run not done |
