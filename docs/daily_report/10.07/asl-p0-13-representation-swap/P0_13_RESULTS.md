# P0-13: results (representation swap at fixed downstream data)

**Status: COMPLETE.** Frozen Uni-Sign features were extracted for all 3,264 clips, the treatment was
trained, and both arms were evaluated with the same code. Plan and decision rule: `P0_13_PLAN.md`
(written before treatment results). Audit: `UNISIGN_ENCODER_AUDIT.md`. Interface: `REPRESENTATION_INTERFACE.md`.

## 1. Run facts

| | Baseline (A) | Treatment (B) |
|---|---|---|
| Run | existing P0.2 padfix run (not retrained) | `scripts/train_p013_unisign.py`, CPU, 9,591 s wall |
| Input | 501-d MediaPipe landmarks + augmentation | 768-d frozen Uni-Sign mT5-encoder features, no augmentation |
| Trainable model | Conformer (4 blocks) + bridge + t5-small decoder | same (only the input Linear is 768→512) |
| Train / val / frozen | 2,751 / 366 / 147 | same IDs, order and references (verified) |
| Optimizer / lr / schedule / batch / seed | Adafactor 4 groups, 1e-4, linear warmup 0.1, bs 8, seed 42 | same |
| Planned epochs / early stopping | 30 / patience 10 on val loss | same |
| Epochs actually run | 30 (no early stop) | **20 (early-stopped)** |
| Val-selected epoch | 20 | **10** |
| Generation | greedy, max_length 30 | same |
| Diagnostics re-run | reproduces saved epoch-20 metrics exactly (val BLEU 0.99, frozen 1.02/11.12) | reproduces training-time epoch-10 metrics (3.25/17.05) |

The planned fixed-budget check was "epoch 30", but it does not exist for the treatment because the
unchanged recipe early-stopped it. The **last trained epoch** is used instead (A: 30, B: 20).

## 2. Translation metrics

### Frozen 147 (primary, clean: Uni-Sign never trained on these clips)

| Checkpoint | Arm | BLEU | chrF | WER | Unique preds | Top-1 share | distinct-1 / -2 |
|---|---|---|---|---|---|---|---|
| val-selected | A baseline (ep 20) | 1.02 | 11.12 | 1.025 | 102/147 | 6.8 % | 0.044 / 0.095 |
| val-selected | **B Uni-Sign (ep 10)** | **3.25** | **17.05** | **0.939** | **147/147** | 0.7 % | 0.210 / 0.486 |
| last trained | A (ep 30) | 0.99 | 11.43 | 1.022 | 137/147 | 2.7 % | — |
| last trained | B (ep 20) | 3.66 | 18.41 | 0.933 | 147/147 | 0.7 % | 0.260 / 0.635 |

Paired bootstrap of B − A over the 147 clips (10k resamples; `data/compare_frozen_*.json`):

| Comparison | ΔBLEU [95 % CI] | ΔchrF [95 % CI] | ΔWER |
|---|---|---|---|
| val-selected (primary) | **+2.23 [1.28, 3.39]** | **+5.93 [4.66, 7.34]** | −0.086 |
| last trained | +2.67 [1.53, 3.98] | +6.97 [5.65, 8.34] | −0.089 |

### Val 366 (contaminated for the treatment; reported, not used for the verdict)

| | BLEU | chrF | WER | Unique |
|---|---|---|---|---|
| A (ep 20) | 0.99 | 11.89 | 1.047 | 206/366 |
| B (ep 10) | 5.13 | 20.40 | 0.923 | 365/366 |
| B (ep 20) | 6.08 | 23.00 | 0.880 | 365/366 |

The frozen Uni-Sign encoder was fine-tuned on all 366 val clip–sentence pairs. That this gap is larger than the
frozen gap (+4.15 vs +2.23 BLEU) fits that contamination.

### Frame-timing confound check (128 How2Sign-v2 frozen clips)

The treatment's official frozen inputs use the re-aligned timings and the signer crop; the baseline used our
original-timing clips. To remove that, the **same treatment checkpoint** was evaluated on Uni-Sign features
computed from *our own* original-timing, full-frame rtmlib poses: the same video segments the baseline saw
(P0-12 condition `B_ours_5p39`). The 19 pilot clips have no such poses, so n = 128.

| On the same 128 clips | BLEU | chrF | WER |
|---|---|---|---|
| A baseline | 0.89 | 11.59 | 1.05 |
| B, our original-timing poses (timing-matched) | **3.07** | **15.55** | 0.97 |
| B, official re-aligned poses | 3.80 | 18.35 | 0.94 |
| **B (timing-matched) − A** | **+2.18 [1.03, 3.44]** | **+3.96 [2.52, 5.40]** | −0.08 |
| B official − B timing-matched | +0.74 [−0.23, 1.73] | +2.80 [1.51, 4.13] | — |

- The improvement **survives with identical video segments.**
- Better input alignment adds roughly another +2.8 chrF on top. About 40 % of the chrF gain on these 128 clips (2.80 of 6.76) comes
  from timing/crop, not from the representation itself.
- Split by P0-12 IoU (official input), B − A is positive in both halves: IoU ≥ 0.5 gives ΔBLEU +2.55
  [1.09, 4.24]; IoU < 0.5 gives +3.37 [0.98, 5.72].

### Context only: the same features with Uni-Sign's own decoder

| Frozen 147, same cached features | BLEU | chrF | WER |
|---|---|---|---|
| Uni-Sign own mT5-Base decoder, greedy max 30 | 6.38 | 23.85 | 0.881 |
| Uni-Sign own mT5-Base decoder, beam 4 max 100 (official) | 9.04 | 28.29 | 0.908 |

This is not part of the controlled comparison: it uses a different, 305M-parameter, How2Sign-fine-tuned
decoder. It shows that the features hold more than the small t5-small path recovers from 2,751 clips (3.25).

## 3. Representation diagnostics (`representation_diagnostics.csv`)

### Correct vs shuffled video (5 derangements; text stays with its sample)

| Set | A Δloss (shuffled − correct) | B Δloss | A ΔBLEU / ΔchrF | B ΔBLEU / ΔchrF |
|---|---|---|---|---|
| frozen 147 | **+0.067** | **+1.280** (19×) | −0.36 / −0.65 | −2.67 / −5.45 |
| val 366 | +0.095 | +1.710 | −0.26 / −0.79 | −4.72 / −8.31 |
| frozen 128, timing-matched (1 seed) | — | +0.828 | — | −2.55 / −4.32 |

The baseline barely uses the video (this matches P0's earlier ~0.1). The treatment relies on it heavily: on
shuffled input its frozen BLEU falls to about 0.6.

### Collapse statistics (mean-pooled per clip; frozen 147)

| Measurement point | Arm | Mean pairwise cos | Shared-component energy | PC1 share (centred) | Participation ratio (centred) |
|---|---|---|---|---|---|
| Input features | A landmarks | 0.956 | 0.946 | 0.554 | 2.8 |
| Input features | B Uni-Sign | **0.294** | **0.271** | **0.066** | **46.2** |
| Encoder output after bridge (seen by decoder) | A | **0.998** | 0.998 | 0.284 | 7.7 |
| Encoder output after bridge | B | **0.988** | 0.988 | 0.133 | 25.9 |

- The Uni-Sign input is far more spread across clips than landmarks (cosine 0.29 vs 0.96; about 16× more
  effective dimensions).
- After the trainable Conformer and bridge, **both arms are dominated by one shared direction** (raw cosine
  0.988 vs 0.998). The treatment's clip-specific residual is larger and higher-rank (participation ratio 26 vs
  7.7), and the decoder clearly uses it (shuffle test).
- **Reading: the Conformer + bridge still compresses heavily.** Raw pooled cosine near 1 is not, by itself,
  proof of a useless encoder. In the treatment a 1.2 % residual carries enough to move BLEU 1 → 3.3.

### Example frozen predictions (val-selected checkpoints)

| Reference (truncated) | A baseline | B Uni-Sign |
|---|---|---|
| We cook it with 3 cups of water, 1 cup of 1 tablespoon of salt… | So, you can do this, and you can do it, and you can do it… | We're putting a little water on your cup, a little bit of a cup of water… |
| Again, do maybe twenty breaths, little flow, inhaling and exhaling… | So, you can also do a little bit of a bit of a bit of a sleeve… | So again, you're going to do a little bit of exercise, but you're going to be able to keep your breath |
| Okay here we go our quick and easy spaghetti… | So, you can't get a lot of a lot of a lot of… | Now, we've got the easiest method to do with the slurry of wires… |
| So, this will set and seal the color… unruly brows… | And then you can use a lot of different things… | This is the same thing that's the same thing… the colors… |

The treatment output is input-specific and sometimes on topic (water/cup, breath). It is still far from
correct and often repetitive.

## 4. Verdict against the pre-registered rule

| Criterion (`P0_13_PLAN.md`) | Result | Met? |
|---|---|---|
| CI of frozen ΔchrF excludes 0 | [4.66, 7.34] | ✓ |
| Frozen ΔBLEU ≥ +2 | +2.23 (CI [1.28, 3.39]) | ✓, but the CI's lower end is below 2 |
| Shuffled-video Δloss clearly larger than baseline | 1.28 vs 0.067 | ✓ |
| Survives the timing-matched check | +2.18 BLEU [1.03, 3.44], +3.96 chrF [2.52, 5.40] | ✓ |

**Frozen Uni-Sign features materially improve translation at the same 2,751 supervised clips:** about 3×
BLEU, +4 to +6 chrF, much higher diversity, and real input dependence. By the rule fixed in advance, this
**supports a representation bottleneck** for the P0.2 setup.

### What this does *not* establish

- **Not "data doesn't matter".** The swapped-in representation was built with far more supervision: Uni-Sign was
  fine-tuned on about 31k How2Sign train pairs (including all 3,117 of our train+val clips) after 984 h of
  YouTube-ASL pretraining. The experiment holds *downstream* data fixed, not total data. The fair reading is:
  *at fixed downstream data, a representation learned from much more sign data beats one learned from the 2,751
  clips alone.*
- **Absolute quality is still low.** 3.25 BLEU / 17 chrF on frozen is not usable translation. The same features
  with Uni-Sign's own decoder reach 6.4–9.0 BLEU, so the small t5-small path with 2,751 clips recovers only part
  of what the representation holds. The downstream component, its data, or both remain a bottleneck *after* the
  swap.
- **Single seed per arm;** baseline variance across seeds is unmeasured. The bootstrap CIs cover test-sample
  noise, not training noise.
- **Augmentation differs** (the baseline had it, the treatment could not). That favours the baseline, so it
  works against the observed effect.
- **Pretraining vs architecture is not separated.** A randomly initialized Uni-Sign encoder arm (E1 arm C) was
  not run.
- How2Sign test shares signers with train (YouTube-ASL §5). Real Curify video was not tested.

## 5. Not done (by instruction or scope)

P0-11 not started; P0-12 files not modified; no extra supervised data; no hyperparameter changes; no
commit or push. Features (1.4 GB), poses (876 MB compressed, 1.5 GB unpacked) and checkpoints (8.2 GB) stay in the session
scratchpad and are not in the repo.
