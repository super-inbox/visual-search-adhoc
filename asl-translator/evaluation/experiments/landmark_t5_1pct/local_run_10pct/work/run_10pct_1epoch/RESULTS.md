# 10% How2Sign landmark→T5 probe — results

**Classification: `GO WITH WEAK / INCONCLUSIVE LANDMARK SIGNAL`**  *(completed 10% scale-up run; landmark evidence is WEAK, see control section)*

- stable; finite; credible downward trend; NORMAL directionally beats at least one corrupted control, but NORMAL beats only ZERO_LANDMARKS; the other control is tied, inconclusive or lacks statistical support (and is NOT clearly better than NORMAL). This is the completed 10% run; the landmark evidence is explicitly WEAK. NORMAL beats ZERO_LANDMARKS but is approximately indistinguishable from TEMPORAL_SHUFFLE: possible use of landmark/frame CONTENT without yet any evidence of temporal-order dependence. TEMPORAL_SHUFFLE: delta=-0.0000 (per-example mean -0.0001, 95% CI [-0.0006, +0.0003], normal better in 185, control better in 181, sign p=0.875); ZERO_LANDMARKS: delta=+6.9366 (per-example mean +6.7845, 95% CI [+6.6730, +6.8940], normal better in 366, control better in 0, sign p=0.000)

> **Do not overclaim.** A falling loss after ONE epoch is necessary but NOT sufficient. Amendments A1/A2: the decision also uses an evaluation-only control (NORMAL vs TEMPORAL_SHUFFLE vs ZERO_LANDMARKS, same checkpoint, no retraining) whose DIRECTION must favour NORMAL. Statistical diagnostics are reported but are not a gate at this n; when they are inconclusive the label is GO WITH WEAK / INCONCLUSIVE LANDMARK SIGNAL and the evidence must be described as weak. Even a strong result is one epoch on ~3,117 clips and 366 validation examples: it supports 'the model uses landmark information', not 'the pipeline translates sign language'.
> This is one epoch on 3,117 clips (10% of official realigned TRAIN metadata); the validation split has only 366 samples. This document describes the **completed** 10% run.
>
> Note: this run reused the 1% package, so `run_config.json` / `metrics.json` record `mode = full_1pct_1epoch`. That inherited mode name is left unmodified in the raw artifacts; the actual run is the 10% run (fraction 0.1, 3,117 selected, 344 steps).

## Run
| | |
|---|---|
| status | ok |
| upstream | `yyouretoast/gloss-free-asl-translation` @ `5b7eb92ff90c4ac5907bc6328edb79c24cec6c77` (unmodified; commit matches registered: True) |
| GPU / driver | None (None) |
| CUDA (torch build) / cuDNN | None / None |
| torch / transformers / python | 2.10.0 / 4.57.6 / 3.12.4 |
| precision | fp16=False (autocast + GradScaler) |
| parameters total / trainable | 67,176,192 / 67,176,192 (encoder 25,287,168, bridge 263,680, t5 41,625,344); Conformer blocks 4; I3D params 0 |

## Data and leakage guard
| | |
|---|---|
| full train count (unique IDs) | 31165 (raw rows 31165) |
| 10% selected | 3117 |
| post-holdout training / validation | 2751 / 366 |
| seed | 20260921 |
| frozen-benchmark overlap (clip / video / text) | **0** / 0 / 0 (guard status: PASS) |
| subset IDs SHA-256 | `149426a50ee31cc9a8291e668c65b35ce43426d14b3160a6ce62d7a04688a0ac` |
| deny-list SHA-256 | `428d6e8bf9a97f984fa711064c1240f95b37d0d6e8e51ad4157ff84dc6cc7fb1` |
| landmark frames (min/median/max) | 2 / 128.0 / 1518; 42% exceed max_len=150 (stride-downsampled) |
| hand all-zero frames (mean L/R) | 10.7% / 9.3% |

## Deviation from upstream (intentional)
- gradient_accumulation_steps: upstream 8 -> 1 (effective batch 64 -> 8)
- logging_steps: upstream 10 -> 1
- data: 10% deterministic subset of official TRAIN, staged as symlinks; upstream then holds out ~15% of it as validation via its own split_by_signer
- single GPU forced via CUDA_VISIBLE_DEVICES=0 (upstream on Kaggle T4x2 would silently use DataParallel)
- metadata passed as a custom-named subset_metadata.csv (avoids upstream merging train/val/test manifests by filename)
- instrumentation only: per-step .item() sync, callbacks, one manual validation-loss pass before training
- Kaggle env installs only the training deps (no mediapipe/opencv/onnx): none is imported on the train path

Effective settings confirmed from `TrainingArguments`: accumulation=1, logging_steps=1, per-device batch=8.
This is a feasibility probe, **not** a reproduction of upstream's effective batch size of 64.

## Metrics
| | |
|---|---|
| optimizer steps (expected) | 344 (344) |
| first / final / min train loss | 12.764 / 5.030 / 4.829 (min at step 186) |
| mean first-k / last-k (k=69) | 7.231 / 5.409 → change -25.2% |
| OLS slope (loss / step) | -0.0063 |
| validation loss before → after | 12.347 → 5.173 (n=366) |
| validation BLEU / WER after (near-meaningless) | 0.04 / 1.03 |
| parameter update L2 (encoder / bridge / t5) | encoder=31.644, bridge=0.935, t5=12.733 |
| non-finite grad_norm steps | 0 / 344 (median grad_norm 6.8) |
| peak CUDA allocated / reserved (train phase) | n/a / n/a MiB |
| peak CUDA allocated / reserved (whole run incl. eval) | n/a / n/a MiB |
| samples/sec (train loop) / steady-state excl. first 2 steps | 12.96 / 13.37 |
| steps/sec | 1.621 |
| wall-clock: total script / init / train loop / eval | 269.0 s / 17.5 s / 212.2 s / 38.5 s |

HF's own `train_samples_per_second` (10.40) is lower because HF's `train_runtime` includes the epoch-end evaluation; the train-loop numbers above exclude it.

## Landmark-dependence control (Amendments A1/A2: added before the real run)

Added because a dry-run on pure random-noise landmarks met the original GO criterion (falling loss alone cannot show landmark use). Evaluation-only, on the **same checkpoint** and the **same held-out validation examples**; no weight updates. Decision uses the **direction** of the raw differences; the bootstrap CI and sign test are **diagnostics**, not a gate (the validation set is small, so power is low).

**Raw eval losses:** NORMAL **5.1690** · TEMPORAL_SHUFFLE **5.1690** · ZERO_LANDMARKS **12.1056** (n=366 held-out examples)\
**delta_shuffle = shuffled_eval_loss − normal_eval_loss = -0.0000**\
**delta_zero = zero_eval_loss − normal_eval_loss = +6.9366**\
(positive ⇒ NORMAL landmarks are better than the corrupted control)

| condition | n | seed | eval loss | control − normal | direction (NORMAL vs control) | per-example mean Δ [bootstrap 95% CI] | normal better / control better / tie | sign-test p | diagnostics conclusive for NORMAL? | wall s | BLEU / WER (optional) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NORMAL | 366 | n/a | 5.1690 | — | — | — | — | — | — | 7.916 | 0.04 / 1.03 |
| TEMPORAL_SHUFFLE | 366 | 20260921 | 5.1690 | -0.0000 | worse | -0.0001 [-0.0006, +0.0003] | 185/181/0 | 0.875 | no | 7.901 | 0.04 / 1.03 |
| ZERO_LANDMARKS | 366 | n/a | 12.1056 | +6.9366 | better | +6.7845 [+6.6730, +6.8940] | 366/0/0 | 0.000 | yes | 8.039 | 0.00 / 1.03 |

**Per-control reading:** TEMPORAL_SHUFFLE → `indistinguishable`; ZERO_LANDMARKS → `beaten_conclusive`.\
**Interpretation:** NORMAL beats ZERO_LANDMARKS but is approximately indistinguishable from TEMPORAL_SHUFFLE: possible use of landmark/frame CONTENT without yet any evidence of temporal-order dependence.

**Evidence strength:** the bootstrap CI and/or sign test are **inconclusive** for at least one control. Any GO here rests on direction alone and must be read as WEAK evidence of landmark use.

**Definitions:** direction = sign of `control − normal` on BOTH the eval-loss delta and the mean per-example difference (disagreement = internally inconsistent). Diagnostics are conventional tests (bootstrap 95% CI excludes 0; exact two-sided sign test p < 0.05 with the majority on that side), reported but not required for GO. A control that is directionally better than NORMAL is `indistinguishable` if neither diagnostic supports it, `control_partial` if exactly one does, and clearly better (STOP) only if both do. No effect-size threshold. ZERO_LANDMARKS is out-of-distribution input, so beating it is weaker evidence than beating TEMPORAL_SHUFFLE. One shuffle draw, one checkpoint: 'reproducibly' cannot be tested within a single run.

Checkpoint: `work/run_10pct_1epoch/checkpoints/checkpoint-344` (step 344, sha256 `c04425b6adc7ebbf…`). Precision: fp32 (cpu self-test). Shuffle seed 20260921; bootstrap 10000 resamples, seed 20260921.

Sanity checks:
- PASS NORMAL_shape_and_mask_preserved
- PASS TEMPORAL_SHUFFLE_shape_and_mask_preserved
- PASS TEMPORAL_SHUFFLE_is_a_permutation_of_original_frames
- PASS ZERO_LANDMARKS_shape_and_mask_preserved
- PASS weights_unchanged_by_evaluation
- PASS same_heldout_examples_as_manifest
- PASS examples_aligned_across_conditions
- PASS shuffle_changed_at_least_one_example
- PASS NORMAL_reproduces_trainer_eval_loss

## Loss curve
`▇▇▇▇▆▅▄▄▃▃▃▃▃▃▂▃▂▂▃▂▂▂▂▂▂▂▂▂▃▂▂▂▃▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▁▂▂▂▂▂▂▁▁▂▂▁▂▂▂▁▂▂▁▂▁▁▁▁▁▂▁▂▁▁▁▁▂▂▂▁▂▁▂▁▁▁▁▁▂▂▁▁▁▁▂▁▁▁▂▁▂▁▁▁▁▁▁▂▁▁▁▁▁▁▁▁▂▁▁▁▁▁▁▂▁▁▁▁▂▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▂▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▂▁▁▁▁▁▁▁▁▁▁▁▁▂▁▁▁▁▁▁▁▁▁▁▂▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▂▁▂▁▁▂▁▁▁▁`

![loss](loss_curve.png)

| step | loss |
|---|---|
| 1 | 12.7635 |
| 2 | 12.1210 |
| 3 | 12.1630 |
| 4 | 12.3474 |
| 5 | 11.2668 |
| 6 | 10.3128 |
| 7 | 9.2355 |
| 8 | 8.5833 |
| 9 | 7.9875 |
| 10 | 7.8371 |
| 11 | 7.6709 |
| 12 | 7.4753 |
| 13 | 7.3496 |
| 14 | 7.3146 |
| 15 | 6.8206 |
| 16 | 7.2134 |
| 17 | 6.7731 |
| 18 | 6.5508 |
| 19 | 7.3657 |
| 20 | 6.9790 |
| 21 | 6.5322 |
| 22 | 6.8727 |
| 23 | 6.9707 |
| 24 | 6.8269 |
| 25 | 6.7597 |
| 26 | 6.3785 |
| 27 | 6.8447 |
| 28 | 6.7180 |
| 29 | 7.2641 |
| 30 | 6.7979 |
| 31 | 6.7949 |
| 32 | 6.4589 |
| 33 | 7.1945 |
| 34 | 7.0408 |
| 35 | 6.7675 |
| 36 | 6.7267 |
| 37 | 6.2678 |
| 38 | 6.9070 |
| 39 | 6.6007 |
| 40 | 6.5068 |
| 41 | 6.4074 |
| 42 | 6.6210 |
| 43 | 6.7559 |
| 44 | 6.2015 |
| 45 | 6.6742 |
| 46 | 6.7426 |
| 47 | 6.3616 |
| 48 | 6.6642 |
| 49 | 6.7715 |
| 50 | 6.5661 |
| 51 | 6.4434 |
| 52 | 6.7126 |
| 53 | 6.3466 |
| 54 | 6.3641 |
| 55 | 6.7072 |
| 56 | 6.7251 |
| 57 | 6.1967 |
| 58 | 6.1930 |
| 59 | 6.8399 |
| 60 | 6.7090 |
| 61 | 6.6627 |
| 62 | 6.1708 |
| 63 | 6.4246 |
| 64 | 6.1035 |
| 65 | 6.3382 |
| 66 | 6.3642 |
| 67 | 6.3549 |
| 68 | 5.9626 |
| 69 | 6.1837 |
| 70 | 6.3392 |
| 71 | 6.1921 |
| 72 | 6.6582 |
| 73 | 6.1216 |
| 74 | 6.0925 |
| 75 | 5.9412 |
| 76 | 5.9530 |
| 77 | 6.0532 |
| 78 | 6.2196 |
| 79 | 5.8674 |
| 80 | 6.0431 |
| 81 | 6.4455 |
| 82 | 6.0118 |
| 83 | 5.7810 |
| 84 | 6.5153 |
| 85 | 5.9801 |
| 86 | 5.9403 |
| 87 | 6.2249 |
| 88 | 5.8204 |
| 89 | 5.9004 |
| 90 | 5.8303 |
| 91 | 5.8095 |
| 92 | 5.8398 |
| 93 | 6.2472 |
| 94 | 5.6852 |
| 95 | 6.0695 |
| 96 | 5.5854 |
| 97 | 5.8393 |
| 98 | 5.6745 |
| 99 | 5.7918 |
| 100 | 6.4270 |
| 101 | 6.0068 |
| 102 | 6.0347 |
| 103 | 5.7874 |
| 104 | 6.3148 |
| 105 | 5.6455 |
| 106 | 5.9962 |
| 107 | 5.8887 |
| 108 | 5.8797 |
| 109 | 5.3965 |
| 110 | 5.7795 |
| 111 | 5.8534 |
| 112 | 6.0089 |
| 113 | 6.3752 |
| 114 | 5.8989 |
| 115 | 5.6741 |
| 116 | 5.9025 |
| 117 | 5.4811 |
| 118 | 6.1155 |
| 119 | 5.5515 |
| 120 | 5.9481 |
| 121 | 5.4413 |
| 122 | 6.0376 |
| 123 | 5.7884 |
| 124 | 6.1229 |
| 125 | 5.7730 |
| 126 | 5.8849 |
| 127 | 5.5714 |
| 128 | 5.6002 |
| 129 | 5.7478 |
| 130 | 5.7713 |
| 131 | 6.0064 |
| 132 | 5.3664 |
| 133 | 5.6199 |
| 134 | 5.5507 |
| 135 | 5.8388 |
| 136 | 5.7376 |
| 137 | 5.4516 |
| 138 | 5.6748 |
| 139 | 5.6528 |
| 140 | 6.0324 |
| 141 | 5.7530 |
| 142 | 5.6684 |
| 143 | 5.7065 |
| 144 | 5.5534 |
| 145 | 5.8403 |
| 146 | 5.8106 |
| 147 | 6.3706 |
| 148 | 5.5938 |
| 149 | 5.4030 |
| 150 | 5.4595 |
| 151 | 5.8793 |
| 152 | 6.2049 |
| 153 | 5.8249 |
| 154 | 5.3539 |
| 155 | 5.6567 |
| 156 | 5.7660 |
| 157 | 5.6429 |
| 158 | 5.8475 |
| 159 | 5.4260 |
| 160 | 5.5895 |
| 161 | 5.5427 |
| 162 | 5.6389 |
| 163 | 5.5069 |
| 164 | 5.2276 |
| 165 | 5.5871 |
| 166 | 5.1292 |
| 167 | 5.6355 |
| 168 | 5.4046 |
| 169 | 5.2683 |
| 170 | 5.5545 |
| 171 | 5.5114 |
| 172 | 5.8305 |
| 173 | 5.4598 |
| 174 | 6.1614 |
| 175 | 5.3553 |
| 176 | 5.5503 |
| 177 | 5.4825 |
| 178 | 5.7245 |
| 179 | 5.9100 |
| 180 | 5.5511 |
| 181 | 5.4822 |
| 182 | 5.3720 |
| 183 | 5.8374 |
| 184 | 5.1520 |
| 185 | 5.7070 |
| 186 | 4.8292 |
| 187 | 5.6354 |
| 188 | 5.7042 |
| 189 | 5.7552 |
| 190 | 5.8568 |
| 191 | 5.6538 |
| 192 | 5.4714 |
| 193 | 5.3244 |
| 194 | 5.9402 |
| 195 | 5.5940 |
| 196 | 5.2440 |
| 197 | 5.8416 |
| 198 | 5.3012 |
| 199 | 5.3838 |
| 200 | 5.6487 |
| 201 | 5.7587 |
| 202 | 6.0255 |
| 203 | 5.5683 |
| 204 | 5.8188 |
| 205 | 5.2832 |
| 206 | 5.2544 |
| 207 | 5.6539 |
| 208 | 5.4169 |
| 209 | 5.4296 |
| 210 | 5.6755 |
| 211 | 5.1939 |
| 212 | 5.4247 |
| 213 | 5.4722 |
| 214 | 5.1859 |
| 215 | 6.2759 |
| 216 | 5.6082 |
| 217 | 5.6311 |
| 218 | 5.8644 |
| 219 | 5.6489 |
| 220 | 5.7875 |
| 221 | 5.4976 |
| 222 | 5.5525 |
| 223 | 4.9066 |
| 224 | 5.1061 |
| 225 | 5.6788 |
| 226 | 6.1022 |
| 227 | 5.1470 |
| 228 | 5.3583 |
| 229 | 5.5342 |
| 230 | 5.1152 |
| 231 | 5.0862 |
| 232 | 5.2295 |
| 233 | 5.6592 |
| 234 | 5.5959 |
| 235 | 5.8344 |
| 236 | 5.5183 |
| 237 | 5.3729 |
| 238 | 5.7391 |
| 239 | 5.2349 |
| 240 | 5.2746 |
| 241 | 5.5539 |
| 242 | 5.4178 |
| 243 | 5.8935 |
| 244 | 5.6824 |
| 245 | 5.2455 |
| 246 | 5.1762 |
| 247 | 5.2350 |
| 248 | 5.2423 |
| 249 | 5.2894 |
| 250 | 5.6867 |
| 251 | 5.7254 |
| 252 | 5.1605 |
| 253 | 4.8728 |
| 254 | 5.1456 |
| 255 | 5.4877 |
| 256 | 5.1853 |
| 257 | 5.7270 |
| 258 | 4.9673 |
| 259 | 5.1253 |
| 260 | 5.3373 |
| 261 | 5.6027 |
| 262 | 5.1660 |
| 263 | 5.0846 |
| 264 | 5.4172 |
| 265 | 5.7560 |
| 266 | 5.0456 |
| 267 | 5.0196 |
| 268 | 5.1586 |
| 269 | 5.3785 |
| 270 | 5.5074 |
| 271 | 5.4691 |
| 272 | 5.6151 |
| 273 | 5.3318 |
| 274 | 5.5405 |
| 275 | 5.8342 |
| 276 | 5.8830 |
| 277 | 5.3339 |
| 278 | 5.2784 |
| 279 | 5.5768 |
| 280 | 4.9854 |
| 281 | 4.9687 |
| 282 | 5.5988 |
| 283 | 5.5475 |
| 284 | 5.1937 |
| 285 | 5.2885 |
| 286 | 5.8744 |
| 287 | 5.4145 |
| 288 | 5.4540 |
| 289 | 5.1454 |
| 290 | 5.3737 |
| 291 | 5.3345 |
| 292 | 5.6536 |
| 293 | 5.2713 |
| 294 | 5.1099 |
| 295 | 5.0826 |
| 296 | 5.9512 |
| 297 | 5.1594 |
| 298 | 5.8470 |
| 299 | 5.7228 |
| 300 | 5.1237 |
| 301 | 5.2494 |
| 302 | 5.2416 |
| 303 | 4.9728 |
| 304 | 5.7411 |
| 305 | 5.8436 |
| 306 | 5.4792 |
| 307 | 5.2411 |
| 308 | 5.2477 |
| 309 | 5.8624 |
| 310 | 5.2299 |
| 311 | 5.5628 |
| 312 | 5.3170 |
| 313 | 5.3322 |
| 314 | 5.1802 |
| 315 | 5.6046 |
| 316 | 5.2961 |
| 317 | 5.4261 |
| 318 | 5.6068 |
| 319 | 4.9817 |
| 320 | 5.2838 |
| 321 | 5.3083 |
| 322 | 5.4035 |
| 323 | 4.9505 |
| 324 | 4.8747 |
| 325 | 5.8202 |
| 326 | 5.6432 |
| 327 | 5.3967 |
| 328 | 5.8225 |
| 329 | 5.4891 |
| 330 | 5.2445 |
| 331 | 5.8682 |
| 332 | 4.9785 |
| 333 | 4.9134 |
| 334 | 5.5158 |
| 335 | 6.1596 |
| 336 | 4.9349 |
| 337 | 6.1466 |
| 338 | 5.3740 |
| 339 | 5.4640 |
| 340 | 6.1281 |
| 341 | 5.0347 |
| 342 | 5.2857 |
| 343 | 5.5424 |
| 344 | 5.0303 |

Raw data: `metrics.json`, `step_metrics.jsonl`, `trainer_state.json`, `run_config.json`, `control_eval.json`, `control_predictions.json`, `../subset_manifest.json`.
