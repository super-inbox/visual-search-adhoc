# ASL P0-11 / P0-12 / P0-13 Work Report

Date: 2026-10-09. A consolidated report; no new training or inference was run to write it. All numbers come from
the result files listed in §11. Nothing was committed.

**Update 2026-10-11.** The P0-11 same-init 2,751-clip control (`ref_sameinit`) was run to completion: one new CPU
training run plus its diagnostics. Its results are added to §1, §2, §3, §6, §9–11, and P0-11 is now **COMPLETE**.
P0-12 and P0-13 are unchanged. Detail: `10.08/asl-p0-11-data-scaling/P0_11_RESULTS.md`.

| Experiment | Question | Status |
|---|---|---|
| P0-11 | Does more supervised How2Sign data help the current baseline? | **COMPLETE**: main runs plus same-init control (2026-10-11) |
| P0-12 | Why does our Uni-Sign path score 5.39 where the authors' predictions score 9.59? | **PARTIAL**: diagnosis done, controlled GPU run blocked |
| P0-13 | Does a better representation help at fixed supervised data? | **COMPLETE** |

## 1. Executive Summary

- **Representation is the larger bottleneck in our current setup (strong current evidence, not final proof).**
  - P0-13 kept the 2,751 supervised clips fixed and swapped landmarks for frozen Uni-Sign features. Frozen-147
    BLEU went 1.02 → **3.25** (+2.23, 95 % CI [1.28, 3.39]) and chrF 11.12 → **17.05** (+5.93, CI [4.66, 7.34]).
  - P0-11 kept the representation fixed and grew supervised How2Sign data up to 9.6×. With initialization
    matched across sizes, frozen-147 BLEU went 0.80 → 1.15 → 0.54 → **0.52** (no BLEU difference significant).
    The best size gained +0.36 BLEU (CI [−0.28, 1.01]). No size came close to the P0-13 gain.
- **More supervised How2Sign data made the model fit better but not translate better.**
  - Val and frozen loss improved steadily with data.
  - BLEU was flat within noise. chrF rose about 1.7 at 2.4–4.8× data, then fell below the start at 9.6×.
  - Output diversity fell at the larger sizes: distinct predictions on frozen-147 went 63 → 73 → 35 → 29
    (same init).
  - Reliance on the video stayed near zero: the shuffled-video loss gap was 0.05–0.07 at every size, vs 1.28
    for P0-13.
  - The same-init control **confirmed** the earlier conclusion. It shrank some earlier magnitudes ("BLEU halves",
    "102 → 29"), which were partly the P0.2 reference's initialization.
- **Our Uni-Sign path loses about 4.2 BLEU in input preparation, not in the model.**
  - Of the 14.50 → 5.39 gap, about 4.9 BLEU is subset difficulty and about 4.2 BLEU is our pipeline.
  - The leading explanation is timestamp alignment: 28/128 of our clips contain none of the signed sentence.
  - Crop and normalization is a strong second candidate.
  - Our pose extractor matches the official one to within about 1–2 % of shoulder width.
  - None of this is confirmed at translation level yet: the controlled run needs a CUDA GPU we don't have.
- **Uni-Sign is a promising research base, not a product.**
- **The two required next steps are:**
  1. Run the P0-12 controlled inference on one CUDA GPU (about 1–2 GPU-hours, already scripted).
  2. ~~Finish the P0-11 same-init control.~~ Done 2026-10-11.

## 2. Manager Questions

| # | Question | Short answer | Confidence |
|---|---|---|---|
| 1 | Are we mainly limited by labeled data or by representation? | **Representation**, in this setup. A better pretrained representation gave about 3× BLEU at fixed data; up to 9.6× more supervised How2Sign data gave no BLEU gain. | Strong current evidence. P0-11 init confound now removed; caveat: single seeds. |
| 2 | Does scaling How2Sign supervised data help? | **Not for translation quality, with this model and recipe.** Loss improves, but BLEU is flat within noise and chrF rises modestly then falls; diversity drops at larger sizes. Holds with initialization controlled. | Strong evidence. See §3 caveats (single seed, compute-matched budget). |
| 3 | What is wrong with our Uni-Sign pipeline? | **Input preparation, most likely.** Clips are cut at the original rather than the re-aligned timestamps, and the full frame is normalized instead of a signer crop. The pose model itself is not the leading suspect. | Observational. No translation-level split of the 4.2 BLEU yet. |
| 4 | Can Uni-Sign be a useful research base? | **Yes, as a research base. No, not yet as a product.** | Moderate to high for research use. |
| 5 | What remains unresolved? | See §9. Mainly the controlled size of each P0-12 factor, seed variance, and real-user generalization. (The P0-11 init confound is resolved.) | — |
| 6 | What next? | Run the P0-12 GPU contrasts, then fix the canonical Uni-Sign preprocessing (§10). The P0-11 control is done. | — |

## 3. P0-11 — Supervised Data Scaling

### Goal

Vary only the amount of supervised How2Sign training data, keeping the P0.2 landmark representation, model and
recipe fixed. Measure whether translation on the frozen test set improves.

### Setup

| Item | Value |
|---|---|
| Input | 501-d MediaPipe Holistic landmarks (same archive as P0.2), unchanged normalization and augmentation |
| Model | 4-block Conformer + MLP bridge + t5-small decoder, `set_seed(42)` |
| Budget | **Compute-matched:** 10,320 optimizer steps × batch 8 for every condition (P0.2's total), eval every 344 steps, patience 10 |
| Selection | best val loss; primary endpoint = frozen-147 (official How2Sign test) at the val-selected checkpoint |
| Subsets | nested prefixes: 2,751 ⊂ 6,605 ⊂ 13,210 ⊂ 26,419 clips (10.4 / 25 / 50 / 100 % of the 26,419-clip eligible pool; 8.8–84.8 % of official train) |
| Val / frozen | 366 / 147, unchanged and video-disjoint from all training subsets |
| Initialization | p25/p50/p100 and the same-init control: `set_seed(42)` under `OMP_NUM_THREADS=4` → init `c328ad26…`. Historical P0.2 reference: default threads → `e651b023…` |
| Hardware | Apple M3 Pro, CPU. p25/p50/p100 ran three concurrent (about 8.2 h wall each); the same-init control ran alone (2.1 h) |

Because the budget is fixed in steps, larger subsets see each clip fewer times: about 30 passes at 2,751, 12.5 at
p25, 6.2 at p50 and 3.1 at p100.

### Results

Frozen-147 at the val-selected checkpoint (`10.08/.../metrics.csv`, `data/diagnostics_summary.csv`):

| Condition | Train clips | Best val loss | Frozen loss | BLEU | chrF | WER | Distinct preds /147 | Top-1 share | Shuffled-video Δloss |
|---|---|---|---|---|---|---|---|---|---|
| P0.2 reference (existing run, other init) | 2,751 | 3.6415 | 3.7224 | **1.02** | 11.12 | 1.025 | 102 | 6.8 % | 0.067 |
| **Same-init control `ref_sameinit` (2026-10-11)** | 2,751 | 3.6418 | 3.7146 | **0.80** | 10.60 | 1.056 | 63 | 30.6 % | 0.048 |
| p25 | 6,605 | 3.5908 | 3.6676 | **1.15** | 12.37 | 1.005 | 73 | 8.8 % | 0.073 |
| p50 | 13,210 | 3.5866 | 3.6650 | **0.54** | 12.25 | 1.047 | 35 | 36.7 % | 0.066 |
| p100 | 26,419 | 3.5760 | 3.6534 | **0.52** | 9.51 | 1.056 | 29 | 20.4 % | 0.061 |

Paired bootstrap against the P0.2 reference (10k resamples, frozen-147; `data/bootstrap_frozen147.json`):

| Comparison | ΔBLEU [95 % CI] | ΔchrF [95 % CI] |
|---|---|---|
| p25 − ref | +0.13 [−0.44, +0.77] | +1.25 [+0.37, +2.12] |
| p50 − ref | −0.48 [−0.97, +0.10] | +1.13 [+0.34, +1.95] |
| p100 − ref | −0.51 [−0.98, +0.02] | **−1.61 [−2.42, −0.83]** |
| p100 − p50 | −0.02 [−0.44, +0.36] | **−2.74 [−3.35, −2.16]** |

Paired bootstrap against the **same-init control** (the controlled comparison; same file):

| Comparison | ΔBLEU [95 % CI] | ΔchrF [95 % CI] |
|---|---|---|
| p25 − ref_sameinit | +0.36 [−0.28, +1.01] | **+1.78 [+0.96, +2.61]** |
| p50 − ref_sameinit | −0.26 [−0.71, +0.28] | **+1.66 [+1.07, +2.29]** |
| p100 − ref_sameinit | −0.28 [−0.71, +0.21] | **−1.08 [−1.74, −0.45]** |
| *Init effect: ref_sameinit − P0.2 reference (same 2,751 clips)* | *−0.22 [−0.86, +0.42]* | *−0.53 [−1.45, +0.39]* |

The trainable encoder's output also became more collapsed at the larger sizes. Its participation ratio on
frozen-147 (effective dimensions) went **3.8 → 3.9 → 2.4 → 2.3** from the same-init control. The P0.2 reference,
with a different init, is at 7.7, so the earlier "7.7 → 2.3" was partly initialization.

### Interpretation

- **Loss improves with data, translation does not.** Best val loss and frozen loss both fall at every size.
  Against the same-init control, BLEU is flat within noise (0.80 → 1.15 → 0.54 → 0.52, no pairwise BLEU delta
  significant). chrF gains about 1.7 points at p25/p50, then drops below the start at p100. The earlier "BLEU
  roughly halves" reading (vs the P0.2 reference) does not survive init control. "No sustained gain" does.
- **The model does not learn to use the video more.** The shuffled-video loss gap stays at 0.05–0.07 throughout
  (0.048 same-init 2,751; 0.061–0.073 larger).
  The extra data is absorbed as a better *language prior*: lower loss from predicting generic How2Sign sentences,
  not from reading the signing.
- **Output diversity falls at the larger sizes.** With init matched, distinct predictions go 63 → 73 → 35 → 29,
  and encoder effective dimension goes 3.8 → 3.9 → 2.4 → 2.3. The model drifts toward a few generic outputs from
  p50 on.
- **Pre-registered rule (`P0_11_PLAN.md`), first applied with the P0.2 reference.** The same-init control gives
  the same verdict: A fails (p100 ΔchrF CI excludes 0 on the negative side), C is literally met, D in spirit.
  - Outcome A ("flat") misses by 0.006 BLEU (|ΔBLEU| 0.506 vs < 0.5), and its chrF condition fails because the
    p100 CI excludes 0 on the negative side.
  - Literally, outcome C ("rise then plateau") is met: p25 has a chrF CI excluding 0, and p100 − p50 has
    ΔBLEU < 0.3.
  - The data actually show **rise-then-decline, with loss improving.** That is closest in spirit to D ("fits more,
    generalizes no better"), which the rules did not fully anticipate.
- Video coverage saturates early (p25 already covers 1,667 of 1,826 pool videos). Larger subsets add more sentences
  from videos already seen, not new topics or signers.

### Caveats

- **Initialization confound: resolved.** The historical P0.2 reference used init hash `e651b023…`. The
  p25/p50/p100 runs used `OMP_NUM_THREADS=4`, which changed PyTorch's random initialization (`c328ad26…`). The
  completed same-init control removes this confound. It also measures the init effect at fixed data: −0.22 BLEU,
  −0.53 chrF, distinct predictions 102 vs 63. That is the same size as the BLEU differences between data sizes.
- **Single seed per condition.** Bootstrap CIs cover test-sample noise, not training noise. Frozen BLEU also
  fluctuates by about 0.6–0.9 between late checkpoints within each run. BLEU differences under about 0.5 are not
  meaningful. A multi-seed matrix would be needed to pin down the curve's shape, but not to answer the question.
- **Compute-matched budget.** At p100 each clip is seen only about 3 times. p25, p50 and p100 all selected their best
  checkpoint in the last two evaluations, so by the pre-registered rule their points are **lower bounds** on what a
  longer run could reach. This could plausibly matter at p100. It does not explain falling BLEU alongside falling
  loss, or the growing collapse.
- **Val text overlap grows with subset size** (6 → 90 clips with a normalized text also in val). This slightly
  inflates val metrics for larger subsets. It is the reason frozen-147 is the primary endpoint.
- **Scope.** This tests *supervised How2Sign scaling for this model and recipe*. It does not test broad
  sign-language pretraining data.

### Status

**COMPLETE (2026-10-11).** The p25/p50/p100 main runs, the same-init 2,751-clip control and all diagnostics are
complete. With initialization controlled, the answer is the same: more supervised How2Sign data gives no
material, sustained translation gain with this model and recipe. Remaining caveats are single seeds and the
compute-matched lower bounds, which do not reopen the question.

**Same-init control, completed run (`ref_sameinit`).**

| Item | Value |
|---|---|
| Run | 2026-10-11 15:56 → 18:03, alone on CPU (`OMP_NUM_THREADS=4`, 4 intra-op threads), under `caffeinate -ims`; same command as `run_p011.sh` with the 2,751 P0.2 IDs |
| Init | `c328ad26…`, identical to p25/p50/p100 |
| Resume vs restart | Restarted from scratch rather than resuming `ref_omp4` from `checkpoint-688`, because an HF-Trainer resume does not replay the augmentation / dataloader-worker RNG stream exactly. The restart is bit-identical to `ref_omp4` on all 1,032 overlapping steps (loss and grad-norm), on evals 1–2, and on the epoch-2 frozen predictions |
| Training | early stopping at eval 27 (step 9,288 of 10,320); best eval 17 (step 5,848), val loss 3.6418; train loss at best 3.663, at stop 3.465 (overfitting after eval 17); 7,584 s wall |
| Frozen-147 at best | BLEU 0.80, chrF 10.60, WER 1.056, 63/147 distinct, top-1 share 30.6 % |
| Diagnostics | shuffled-video Δloss 0.048 (frozen) / 0.077 (val); encoder participation ratio 3.84 |
| Files | `10.08/asl-p0-11-data-scaling/data/runs/ref_sameinit/`, `data/diagnostics/ref_sameinit_best.json`, `P0_11_RESULTS.md`; checkpoints in `$P011/runs/ref_sameinit/` (scratchpad, not durable) |

**Earlier partial attempt (`ref_omp4`, 2026-10-09): record (kept for provenance; superseded).**

| Item | Value |
|---|---|
| Location (outside repo) | `$P011/runs/ref_omp4/`, log `$P011/logs/train_ref_omp4.log`, where `$P011` is the P0-11 working directory in a temporary Claude session scratchpad (outside the repo, not durable) |
| Started | 2026-10-09 11:44 (run_config written), same 2,751 IDs (sha256 `900929628d3e…`), planned 10,320 steps |
| Last completed optimizer step | **1,032** of 10,320 (end of epoch 3; `step_log.jsonl`) |
| Last completed evaluation | **epoch 2, step 688**: val loss 4.9533, frozen loss 4.9845 (best so far). Epoch 1 (step 344): val 5.5670, frozen 5.6445 |
| Interrupted during | epoch-3 val eval (batch 20/46); no epoch-3 metrics or checkpoint |
| Preserved | `checkpoints/checkpoint-344`, `checkpoint-688`; `epoch_log.jsonl`; `step_log.jsonl`; `frozen_predictions/epoch_0{1,2}.json`; `val_predictions/epoch_0{1,2}.json`; full log. Nothing was deleted or modified. |
| Wall time | 17,289 s (4.8 h) from start to step 1,032. **Most of it was system sleep:** the lid was closed at 11:49 (`pmset` log: clamshell sleep) and epoch 2 shows 16,783 s wall vs 279 s for epoch 1. Actual compute was about 15 min. |
| Ended | 2026-10-09 16:32:40, about 4 min after the machine resumed. When this report session checked at 16:33, **no process belonged to the run** (`ps`, `pgrep`, `lsof` on its log, checked with the sandbox disabled). So this session did not terminate anything, and no other process was touched. The log has no traceback, only a Python `resource_tracker` shutdown warning. That fits the run being shut down along with the earlier session that launched it, but **the exact cause is not verified.** |
| Why stopped | The work was paused to write this report (by instruction). In practice the run had already exited before it could be stopped deliberately. |
| Outcome | Superseded by the completed from-scratch restart `ref_sameinit` above. `ref_omp4` itself was not modified. |

## 4. P0-12 — Uni-Sign Pipeline Gap

### Goal

Explain why our Uni-Sign inference scores 5.39 BLEU on our 128 hard How2Sign test clips, when the authors' released
predictions score 9.59 on the same clips.

### E0 Baseline

| Predictions | Clips | BLEU-4 |
|---|---|---|
| Authors' released, full How2Sign test | 2,349 | **14.50** (paper: 14.5; reproduced exactly with the official scorer) |
| Authors' released, our 128 clips | 128 | **9.59** |
| Our pipeline, same 128 clips | 128 | **5.39** |

- **≈ 4.9 BLEU** of the original 14.5 vs 5.4 gap comes from benchmark/subset difficulty: our 128 clips are
  deliberately hard.
- **≈ 4.2 BLEU** (4.20, paired-bootstrap CI 2.42–6.15) remains in our inference/preprocessing path.
- E0 ruled out several causes:
  - scoring and references
  - frame subsampling (the ours/authors ratio is 0.56–0.60 in every length bucket)
  - truncation (comparable rates)

### Diagnostics

Full 128-clip pose diagnostics plus re-analysis of existing predictions; no new inference.

| Variable | Evidence | Size |
|---|---|---|
| **V1 Timestamp alignment** | Ours use the original How2Sign timestamps, official uses re-aligned (128/128 within 0.25 s). Overlap IoU median 0.555; **28/128 clips have zero overlap**; 61/128 have IoU < 0.5. | Large |
| **V2 Crop / normalization** | We feed the full 1280×720 frame; official uses signer crops. Uni-Sign divides x/y by frame W/H, so our skeleton's shoulder-width/neck-height is 0.90 vs 2.06, about **0.44×** the trained geometry. | Large, systematic |
| **V3 Pose extractor model** | On identical frames our rtmlib lightweight model matches the official RTMPose keypoints within **0.85 % (body) / 1.5–1.7 % (hands)** of shoulder width. After a crop shift the difference is about 0.7 % / 1.05 %. | Small |
| **V4 Runtime** | Both bf16. CPU vs CUDA and batch 1 vs 8 are untested. | Unknown, expected small |

**Observational evidence for V1.** The authors' predictions all use re-aligned clips, so their per-bucket score
controls for sentence difficulty:

| Our clip overlap with the re-aligned window | n | Authors BLEU | Ours BLEU | Ours / Authors |
|---|---|---|---|---|
| IoU = 0 | 28 | 8.84 | **0.71** | 0.08 |
| (0, 0.5) | 33 | 13.06 | 6.90 | 0.53 |
| [0.5, 0.9) | 51 | 8.29 | 5.76 | 0.70 |
| ≥ 0.9 | 16 | 8.45 | 7.01 | 0.83 |

- Ours − authors is −7.09 BLEU for IoU < 0.5 vs −2.25 for IoU ≥ 0.5. The CI of the difference, 1.0–9.0,
  excludes 0.
- Sentence-level ρ(IoU, our chrF deficit) = 0.42, p < 1e-4. The control, ρ(IoU, authors' chrF) = 0.04, means IoU
  is not standing in for difficulty.
- **This is correlation, not a controlled result.**

### Current Leading Causes

1. **Timestamp alignment (V1)**: leading explanation, with observational support.
2. **Crop / coordinate normalization (V2)**: strong candidate, large input distortion, no translation evidence yet.
3. **Pose extractor (V3)**: no longer the leading suspect.
4. **Runtime (V4)**: untested.

**No share of the 4.20 BLEU gap is assigned to any of these until the controlled run.**

### Controlled Experiment Design

One variable per contrast, every contrast with a paired-bootstrap CI and decision rules fixed in `P0_12_PLAN.md`:

| Contrast | Arms | Isolates |
|---|---|---|
| Path check | official pose input vs authors' released 9.59 | does the official path reproduce on the subset |
| V3 | official extractor vs ours, on identical official crops | pose model |
| V1 | ours on official crop (re-aligned) vs ours with original timing, aspect-corrected | timestamps |
| V2 | aspect-corrected vs our current 5.39 input | crop/normalization |
| V4a / V4b | batch 8 vs 1; GPU vs historical CPU | runtime |
| Noise | official arm with seeds 43, 44 | run-to-run band |

All four pose conditions are built and pass the unmodified official `S2T_Dataset` loader (128/128 clips).
`scripts/run_p012_gpu.sh` runs the whole sequence; estimated 1–2 GPU-hours.

### Blocker

**No CUDA GPU.** The official `fine_tuning.py --eval` uses hardcoded `.cuda()` and deepspeed. By instruction, no
CPU approximation of the official path was run. The prepared inputs (284 MB) are in a temporary session scratchpad
and should be copied out, or regenerated from `scripts/`.

### Status

**PARTIAL.** Diagnosis complete; leading causes identified; controlled translation experiment designed and
prepared but not run. **Experimentally unresolved.**

## 5. P0-13 — Representation Swap

### Goal

Hold the supervised downstream data fixed at P0.2's 2,751 clips and change only the input representation.

### Controlled Setup

| | Baseline (A) | Treatment (B) |
|---|---|---|
| Input | 501-d MediaPipe landmarks + augmentation | 768-d **frozen** Uni-Sign pretrained encoder features (no augmentation) |
| Trainable model | Conformer + bridge + t5-small decoder | same (input Linear 768→512) |
| Data | 2,751 train / 366 val / 147 frozen | identical IDs, order, references |
| Recipe | Adafactor, lr 1e-4, bs 8, seed 42, patience 10 | same |
| Selected epoch | 20 (no early stop) | 10 (early-stopped at 20) |

### Results

Frozen-147, val-selected checkpoints:

| Arm | BLEU | chrF | WER | Distinct preds |
|---|---|---|---|---|
| A landmarks | 1.023 | 11.121 | 1.025 | 102/147 |
| **B Uni-Sign features** | **3.249** | **17.049** | **0.939** | **147/147** |
| **Δ (B − A)** | **+2.23 [1.28, 3.39]** | **+5.93 [4.66, 7.34]** | −0.086 | — |

- **Robustness.**
  - With the last trained checkpoints the gain is +2.67 BLEU [1.53, 3.98].
  - In the timing-matched check, the treatment is fed features from *our own* original-timing poses, the same video
    segments as the baseline. On 128 clips the gain is still **+2.18 BLEU [1.03, 3.44]** and +3.96 chrF.
  - About 40 % of the chrF gain on those 128 clips (2.80 of 6.76) came from better input timing/crop rather than the
    representation.
- **Context only, not part of the controlled comparison.** The same frozen features with Uni-Sign's own
  How2Sign-fine-tuned mT5-Base decoder score 6.38 BLEU (greedy) and 9.04 BLEU (official beam 4). The features hold
  more than the small t5-small path recovers from 2,751 clips.

### Representation Diagnostics

| Measure (frozen-147) | A landmarks | B Uni-Sign |
|---|---|---|
| Correct-vs-shuffled video Δloss | **+0.067** | **+1.280** (19×) |
| Input mean pairwise cosine (clip-pooled) | ~0.96 | **~0.29** |
| Input effective dimensions (participation ratio) | 2.8 | 46.2 |
| Effective dimensions after our trainable encoder + bridge | **~7.7** | **~26** |

- The baseline barely uses the video. The treatment depends on it heavily: shuffled input drops its BLEU to about
  0.6.
- In both arms our Conformer and bridge still compress heavily (post-bridge cosine 0.998 vs 0.988). The treatment's
  residual is higher-rank, and the decoder uses it.

### Interpretation

In this setup, the frozen Uni-Sign representation materially improves translation while supervised downstream data
stays fixed: about 3× BLEU, +6 chrF, full output diversity, and real dependence on the input. By the pre-registered
rule this **supports representation as an important bottleneck.**

### Caveats

- **Not "data doesn't matter".** Uni-Sign's representation was learned from far more sign-language data:
  - about 984 h of YouTube-ASL pretraining
  - fine-tuning on all of How2Sign train (about 31k pairs, including our 3,117 train+val clips)

  The experiment fixes *downstream supervised* data, not total data.
- Val-366 is contaminated for the treatment (the encoder saw those pairs). The verdict uses frozen-147 only, which
  Uni-Sign never trained on.
- Single seed per arm.
- Pretraining vs architecture is not separated: no randomly initialized Uni-Sign encoder arm.
- How2Sign test shares signers with train. Real Curify-user video was not tested.
- Absolute quality is still low: 3.25 BLEU is not usable translation, and outputs are often repetitive.

### Status

**COMPLETE.**

## 6. P0-11 vs P0-13

Same model family, same recipe, same frozen-147 endpoint. P0-11 rows are compared with the same-init 2,751 control.
P0-13 is compared with the P0.2 reference, its own baseline.

| Lever | Supervised clips | Representation | Frozen BLEU | Frozen chrF | WER | Distinct /147 | Shuffled Δloss |
|---|---|---|---|---|---|---|---|
| Starting point (P0.2 reference; P0-13 baseline) | 2,751 | landmarks | 1.02 | 11.12 | 1.025 | 102 | 0.067 |
| Starting point, same init as P0-11 (`ref_sameinit`) | 2,751 | landmarks | 0.80 | 10.60 | 1.056 | 63 | 0.048 |
| More data (P0-11 p25) | 6,605 (2.4×) | landmarks | 1.15 | 12.37 | 1.005 | 73 | 0.073 |
| More data (P0-11 p50) | 13,210 (4.8×) | landmarks | 0.54 | 12.25 | 1.047 | 35 | 0.066 |
| More data (P0-11 p100) | 26,419 (9.6×) | landmarks | 0.52 | 9.51 | 1.056 | 29 | 0.061 |
| **Better representation (P0-13)** | **2,751 (1×)** | **frozen Uni-Sign** | **3.25** | **17.05** | **0.939** | **147** | **1.280** |

| | Best ΔBLEU vs start | Best ΔchrF vs start | Effect on video reliance | Effect on diversity |
|---|---|---|---|---|
| Up to 9.6× supervised How2Sign data (vs same-init control) | +0.36 [−0.28, +1.01] (p25); −0.28 at 9.6× | +1.78 [+0.96, +2.61] (p25); −1.08 at 9.6× | negligible (0.048 → 0.061–0.073) | falls at larger sizes (63 → 29) |
| Pretrained representation, same data | **+2.23 [1.28, 3.39]** | **+5.93 [4.66, 7.34]** | 19× larger | full (147/147) |

**Reading.** In our current experiments, a better pretrained representation is worth far more than up to 9.6× more
supervised How2Sign clips.
- The best supervised-scaling BLEU CI lies entirely below the P0-13 CI (1.01 < 1.28).
- The best chrF gain is about 30 % of P0-13's.
- At 9.6×, both metrics are at or below the start.

The init effect is now measured: −0.22 BLEU / −0.53 chrF at fixed data. That is about a tenth of the P0-13 effect,
so init variance cannot explain the comparison. Single seeds remain a caveat. This is **strong evidence, not final
causal proof.**

## 7. What This Says About "Data vs Representation"

- **Supported:** at our scale, the current landmark → Conformer → t5-small model cannot turn more How2Sign
  sentences into better translation. It learns a better language prior instead of a better mapping from motion to
  meaning, and its outputs collapse. The bottleneck is in how the video is represented.
- **Also supported:** that better representation came from *more data of a different kind*. That means broad
  sign-language pretraining: YouTube-ASL plus all of How2Sign, through Uni-Sign's pretraining stages.
- **Not supported:** "data does not matter."
- **The supported conclusion:**

  > *Broad sign-language pretraining that learns a better representation is much more effective in our current
  > experiments than simply scaling the same supervised How2Sign baseline.*

- **Practical consequence:** collecting or labelling more How2Sign-style sentence pairs for the current baseline
  is not a good use of effort. Effort should go to building on a pretrained sign representation, and to getting
  its input preprocessing right (P0-12).

## 8. What This Says About Uni-Sign

**Why it is promising as a research base**

- It is the strongest ASL baseline we have. The authors' predictions score 14.50 on full How2Sign test and 9.59 on
  our hard 128 clips.
- Its frozen representation alone lifts our small model from 1.02 to 3.25 BLEU at fixed data (P0-13).
- Its features make the model actually depend on the video: shuffled-video Δloss is 1.28 vs 0.067.
- Nothing found so far points to a defect in the checkpoint or decoder. The P0-12 gap looks like preprocessing.

**Why it is not product-ready**

- Our own inference path still loses 9.59 → 5.39 on the same clips, and the fix is not yet confirmed.
- The timestamp and crop preprocessing mismatch must be fixed. For live input that means segmenting to the actual
  signing and cropping to the signer before normalization.
- Generalization to real users or domains is weak and untested: How2Sign test shares signers with train, and no
  Curify-user video has been evaluated.
- Decoding repetition remains: 33.6 % of the authors' and 37.5 % of our predictions contain a repeated 3-gram.
- Long-video handling is weak. For clips over 256 frames, repetition is 68–74 % and truncation is up to 65 %.
- Quality is far below reliable translation: single-digit BLEU on hard clips.
- No ASL-fluent human evaluation has been done.

**Verdict:** use Uni-Sign as the research base, conditional on the P0-12 GPU run confirming that the gap is
preprocessing. Do not present it as deployable.

## 9. Remaining Risks / Unknowns

| Unknown | Why it matters | Resolved by |
|---|---|---|
| P0-11 under-training at large subsets | p25/p50/p100 best checkpoints at the last evals (lower bounds) | longer or fixed-epoch run at p100 (optional) |
| Seed variance (P0-11 and P0-13) | all CIs are test-sample only; P0-11 init alone moves BLEU by about 0.2 at fixed data | multi-seed runs |
| Size of each P0-12 factor (timing, crop, extractor, runtime) | decides the canonical preprocessing path | P0-12 CUDA run |
| Does the released checkpoint reproduce the released predictions? | E0 caveat; the link is plausible, not proven | P0-12 path-check arm |
| Pretraining vs architecture in P0-13 | the gain might be partly architectural | random-init Uni-Sign encoder arm |
| Real-user / domain generalization | How2Sign test shares signers with train | Curify-user video evaluation |
| Human-judged quality | BLEU/chrF at this level say little about usefulness | ASL-fluent human evaluation |
| Temporary storage | P0-11 runs, P0-12 condition inputs, P0-13 features/checkpoints live only in temporary Claude session scratchpads (outside the repo) | copy to durable storage |

## 10. Recommended Next Steps

**Required to close the current manager questions**

1. **P0-12 controlled inference on one CUDA GPU.** Run `scripts/run_p012_gpu.sh`: timestamp, crop/normalization,
   pose extractor and runtime/batch, one variable at a time, plus the path check and noise arms. About 1–2
   GPU-hours. Copy the prepared inputs out of the scratchpad first.
2. ~~**P0-11 same-init control.**~~ **Done 2026-10-11** (`ref_sameinit`; §3). Optional follow-up: a multi-seed
   P0-11 matrix to pin down the curve's shape.
3. **Decide the canonical Uni-Sign preprocessing path** from the P0-12 results (expected: re-aligned segmentation
   plus signer crop before normalization).

**Future research (lower priority)**

- Multi-seed P0-13.
- Uni-Sign decoder fine-tuning on top of the representation.
- Random-initialized Uni-Sign architecture control (separate pretraining from architecture).
- Real Curify-user video adaptation.
- ASL-fluent human evaluation.

See `NEXT_STEPS.md`.

## 11. Reproducibility / Deliverables

**Sources (all under `docs/daily_report/`)**

| Experiment | Files used |
|---|---|
| E0 | `10.05/asl-research-followup/e0-unisign-reproduction/E0_RESULTS.md` |
| P0-11 | `10.08/asl-p0-11-data-scaling/` (`P0_11_PLAN.md`, `DATASET_SPLITS.md`, `metrics.csv`, `learning_curve.csv`, `data/diagnostics_summary.csv`, `data/bootstrap_frozen147.json`, `data/runs/*/summary.json`, `figures/`) |
| P0-12 | `10.06/asl-p0-12-unisign-pose-gap/` (`P0_12_RESULTS.md`, `BOSS_SUMMARY.md`, `POSE_DIAGNOSTICS.md`, `per_clip_results.csv`, `pose_diagnostics.csv`) |
| P0-13 | `10.07/asl-p0-13-representation-swap/` (`P0_13_RESULTS.md`, `metrics.csv`, `representation_diagnostics.csv`) |
| P0-11 same-init control | `10.08/asl-p0-11-data-scaling/P0_11_RESULTS.md`, `data/runs/ref_sameinit/`, `data/diagnostics/ref_sameinit_best.json`; checkpoints `$P011/runs/ref_sameinit/` (scratchpad) |
| P0-11 same-init partial (superseded) | `$P011/runs/ref_omp4/` and `$P011/logs/train_ref_omp4.log` (temporary session scratchpad, outside the repo; see §3) |

**Path placeholders in the committed P0-11 run metadata.** `data/runs/*/run_config.json` and `summary.json`
record the original run paths with two placeholders:

- `$WORK` is the P0-11 working directory in a temporary Claude session scratchpad. It held the extracted
  landmarks, `full_train_metadata.csv`, checkpoints and logs. It is not durable, and nothing under it is in the
  repo.
- `~/Desktop/...` is the original machine's home-relative checkout:
  - `~/Desktop/visual-search-adhoc/...` is this repository.
  - `~/Desktop/curify/visual-search-adhoc-asl-task-c/...` is the separate P0.2 checkout, which holds the val split,
    frozen benchmark and denylist.

Both are kept as provenance. To rerun, substitute local paths (see `10.08/asl-p0-11-data-scaling/scripts/run_p011.sh`).

**Deliverables in this directory**

| File | Content |
|---|---|
| `WORK_REPORT.md` | this report |
| `BOSS_SUMMARY.md` | one-page manager summary |
| `EXPERIMENT_STATUS.csv` | per-experiment status, result, blocker, next step |
| `KEY_RESULTS.csv` | consolidated metrics from E0 / P0-11 / P0-12 / P0-13 |
| `NEXT_STEPS.md` | prioritized action list |

**What was not done (by instruction)**

- No new training or inference when this report was first written (2026-10-09). The 2026-10-11 update added
  exactly one training run: the P0-11 same-init control and its diagnostics.
- No changes to P0-11 p25/p50/p100, P0-12 or P0-13 outputs.
- No deletion of the partial `ref_omp4` outputs.
- No commit or push.
