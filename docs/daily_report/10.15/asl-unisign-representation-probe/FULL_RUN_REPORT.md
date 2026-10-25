# P0-14 full run: frozen feature extraction, Uni-Sign decoder baseline, frozen probes

**Date:** 2026-10-15 · **Status:** Stage 3 and Stage 4 complete, verified, copied back. The frozen LR probe and the
pre-registered analysis have been run. No fusion was built, no Uni-Sign model was trained, and no criterion,
concept, seed or threshold was changed. **Formal verdict: PARTIAL SUPPORT** for both Uni-Sign representations
(S1 sanity gate missed, §4.1). All numbers below were re-checked against the compact metrics and checksum
artifacts in `full_run/`.

Design: `EXPERIMENT_PLAN.md` (criteria §9). Evidence: `full_run/`. Bulk artifacts are kept outside the repo in
`~/Desktop/curify/p014-work/` (see §8).

## 1. Headline

| | Tier L macro-F1 | Tier L macro-AUROC | Verdict vs raw (frozen rules) |
|---|---|---|---|
| A. Raw RTMPose (414-d) | 0.125 | 0.750 | – |
| B. Uni-Sign Fsign (2048-d) | 0.256 | 0.834 | **PARTIAL SUPPORT**: C1–C6 all pass; S1 failed |
| C. Uni-Sign mT5 encoder states (1536-d) | **0.416** | **0.886** | **PARTIAL SUPPORT**: C1–C6 all pass; S1 failed |
| D. Uni-Sign's own translation (binary) | **0.548** (CI 0.501–0.578) | 0.759 (single-point) | not part of the rules |
| clip length only | 0.060 | 0.645 | – |
| shuffled labels (mT5) | 0.041 | **0.5302** | S1 band [0.47, 0.53] → **fails by 0.0002** |

- Both Uni-Sign representations pass **every substantive criterion (C1–C6)**, by wide margins (§3).
- They are capped at PARTIAL **only** because the sanity gate S1 is missed. The shuffled-label control's
  macro-AUROC is 0.53017, against an upper bound of 0.53. Per the frozen rule this is a formal sanity-gate
  failure, and it is reported as such. The rule was not edited.
- Layer choice (frozen rule): **mT5 encoder states**. They beat Fsign by +16.0 F1 points (CI +12.9 to +19.3).
- **Fusion readiness: mixed.**
  - mT5 states carry real information about the concepts Uni-Sign's translation drops. AUROC on the translation's
    misses is 0.78.
  - At the frozen probe thresholds, however, adding probe detections to the translation **lowers** macro-F1
    (−6.2 points for mT5). Details in §5.

**What this does not show.**
- It does not show that translation quality improves. No fusion was built and no BLEU / chrF was measured.
- It does not show a better Uni-Sign model. Uni-Sign was frozen; only linear probes on its features were trained.
- The stand-alone probes do not beat Uni-Sign's own translation as concept detectors (best probe F1 0.416 vs 0.548).

## 2. Execution, runtime, storage

| Step | Where | Result | Wall time |
|---|---|---|---|
| Preflight | T4 VM `baobao-training-t4` | Tesla T4 visible; Uni-Sign `eed438bcb49e30405cd6ccdfcccca330c134e830`; ckpt sha256 `1bfd5f33…683fb00d`; mT5-base present. Free disk before the run was ≈ 24 GB (50 GB disk). | – |
| Disk gate | VM | Archive read **directly from the 4 parts** (virtual concatenation, `ConcatParts`), so no 17 GB join peak. Actual peak: 8.5 GB archive + 3.0 GB features + 3.2 GB tar. Free disk now: 9.8 GB. | – |
| Download, 4 official parts | VM | sizes 2,147,483,648 ×3 + 2,023,023,631; **sha256 match the HF LFS hashes** (`full_run/archive/`) | ≈ 6 min |
| Stage 3 extraction | VM, T4, fp32, deterministic cuDNN | **33,295 / 33,295** clips, exit 0 | **4,329 s (72.2 min)**, 0.13 s/clip |
| Stage 4 decoder baseline | VM, T4, fp32 | **2,209 / 2,209**, exit 0, 0 empty outputs | **2,628 s (43.8 min)**, 1.19 s/clip |
| Determinism repeat | VM | 200 clips (100 train, 100 test) re-extracted; 40 clips re-decoded | 27 s + 40 s |
| Copy back to Mac | gcloud scp | `features.tar` + `extras.tar`, sha256 verified on both ends, plus per-file SHA256SUMS | ≈ 46 min (an earlier interrupted partial copy was set aside as `features.tar.partial_prev`, not used) |
| LR probes (ms pool, 5 arms × 17 draws) | Mac CPU | 85 / 85, exit 0 | 3,395 s (56.6 min) |
| Decision + fusion analysis (B = 2,000) | Mac CPU | exit 0 | 4.3 min |

**Storage**

| Location | Item | Size |
|---|---|---|
| VM | official archive (4 parts) | 7.9 GiB |
| VM | `features/` | 3.0 GiB |
| VM | `features.tar` | 3.0 GiB |
| Mac `p014-work/full/features` | pooled shards | 1.7 GiB |
| Mac `p014-work/full/features` | test_clean per-frame sequences (fp16) | 1.2 GiB |
| Mac `p014-work/results/lr` | probe outputs (incl. per-clip test scores) | 129 MB |
| repo `full_run/` | evidence | 2.1 MB |

Per-frame sequences were saved **only for the 2,209 test_clean clips**: raw `[T,207]`, Fsign `[T,1024]`, mT5 `[T,768]`.
Train sequences were not stored.

Decoding configuration (exact, `full_run/vm_decode/decode_config.json`):
- `Uni_Sign.generate` → `mt5_model.generate(inputs_embeds, attention_mask, max_new_tokens=100, num_beams=4)`;
- `do_sample=False`, batch size 1, fp32, `U.set_seed(42)`, `cudnn.deterministic=True`;
- same ≤ 256-frame per-clip sampling seed as extraction;
- torch 2.1.1+cu121, transformers 4.40.0.

## 3. Verification

`full_run/transfer/validate_full.log` and `full_run/vm_extract/VALIDATION.json`: **all pass.**

| Check | Result |
|---|---|
| Records | **31,086 probe_train + 2,209 test_clean = 33,295**, in manifest order |
| Duplicate / missing / extra clip IDs | 0 / 0 / 0 |
| Split, source-video and role metadata vs CSVs | match (no train/test mix) |
| Pose came from its own split's archive directory | yes, every clip |
| NaN / Inf | 0 |
| Dimensions: pooled mean+std | exactly 414 / 2048 / 1536 |
| Frames | T = min(raw frames, 256) for every clip (6,350 clips subsampled) |
| Concept labels re-derived from the English references vs frozen manifest | 23,636 positive labels, **0 mismatches** |
| Determinism: 200-clip re-extraction (separate process) | max \|diff\| **0.0** on every pooled array and every per-frame sequence |
| Determinism: 40-clip re-decode | **40 / 40 identical** strings |
| Transfer | `features.tar` sha256 `554d3c8b…`, `extras.tar` `d4e177b0…`, match VM; per-file SHA256SUMS OK; predictions sha256 `0116a41a…` matches the VM |

## 4. Probe results (LR, pool `ms`, test_clean, Tier L = 24 concepts)

### 4.1 Pre-registered decision (`full_run/results/DECISION.json`, paired video-cluster bootstrap, B = 2,000)

| Criterion | Fsign vs raw | mT5 vs raw |
|---|---|---|
| C1 Δ macro-F1 ≥ +5 pts, CI > 0 | +13.0 (10.2, 15.4) ✅ | +29.1 (25.1, 32.3) ✅ |
| C2 Δ macro-AUROC ≥ +0.03, CI > 0 | +0.084 (0.069, 0.099) ✅ | +0.136 (0.118, 0.155) ✅ |
| C3 per-concept AUROC up ≥ 17/24 | 24/24 ✅ | 24/24 ✅ |
| C4 p10 Δ F1 | +6.1 (5.0, 7.0) ✅ | +26.7 (24.1, 28.7) ✅ |
| C4 p25 Δ F1 | +9.4 (7.4, 10.8) ✅ | +28.5 (25.3, 30.7) ✅ |
| C5 AUROC over length ≥ 0.05 | +0.188 ✅ | +0.241 ✅ |
| C6 Design B (test-only) Δ AUROC > 0, CI > 0 | +0.084 (0.063, 0.102) ✅ | +0.181 (0.160, 0.202) ✅ |
| S1 shuffle AUROC in [0.47, 0.53] | 0.5302 ❌ | 0.5302 ❌ |
| **Verdict** | **PARTIAL SUPPORT** | **PARTIAL SUPPORT** |
| Secondary: unseen-signer proxy (257 clips) Δ AUROC | +0.074 (0.024, 0.107) | +0.097 (0.048, 0.147) |
| Secondary: Tier S Δ macro-F1 | +8.7 (6.1, 11.5) | +34.2 (29.0, 39.8) |

Layer choice: **mT5 states** preferred over Fsign. Δ F1 +16.0 (12.9, 19.3); Δ AUROC +0.052 (0.040, 0.065).

**About S1.** The shuffled-label control uses a single permutation of whole label rows, the same permutation for all
24 concepts.
- Because of this, the 24 per-concept AUROCs are not independent. Their macro average behaves more like one noisy
  draw than like an average of 24.
- The control sits above 0.5 at every fraction: 0.539 at p10, 0.560 at p25, 0.558 at p50, 0.530 at p100.
- In Design B it is 0.486.

This is far below every real arm (raw 0.750). It is still a measured, systematic offset, and under the frozen rule
it fails the gate.

The plan's prose (§9) is stricter than the frozen code. Its S1 row says that on a failure "the pipeline is broken
and nothing is interpreted". `scripts/analyze_probe.py` instead withholds only STRONG and returns PARTIAL when C1 and
C2 pass. The reported verdict is the code's output, unchanged. Read every result below in that light: the S1 miss is
small (0.0002) and the control is far below every real arm, but the gate was not met. I did not run extra seeds or alter the control, because that would amount to re-running a gate
after seeing it fail. If you want to, a multi-seed shuffle diagnostic can be run, reported separately, with the
verdict unchanged.

### 4.2 Macro results by train fraction (`full_run/results/tables/macro_by_fraction.csv`)

Means over draws; ± is the SD across draws.

| Fraction (clips) | Raw P / R / F1 / AUROC | Fsign P / R / F1 / AUROC | mT5 P / R / F1 / AUROC | Length F1 / AUROC |
|---|---|---|---|---|
| p10 (≈ 3.1k, 5 draws) | .050 / .222 / .071±.005 / .665 | .114 / .237 / .132±.004 / .754 | .336 / .389 / .338±.006 / .857 | .058 / .644 |
| p25 (≈ 7.8k, 5) | .069 / .185 / .089±.007 / .703 | .175 / .241 / .182±.012 / .791 | .366 / .417 / .373±.007 / .874 | .061 / .645 |
| p50 (≈ 15.5k, 3) | .080 / .195 / .105±.006 / .728 | .204 / .269 / .221±.005 / .816 | .395 / .438 / .401±.004 / .881 | .062 / .645 |
| p100 (31,086) | .102 / .192 / .125 / .750 | .233 / .300 / .256 / .834 | .410 / .443 / .416 / .886 | .060 / .645 |
| Design B, test-only (3 repeats) | .043 / .237 / .065 / .608 | .083 / .263 / .116 / .692 | .254 / .378 / .279 / .790 | .056 / .618 |
| D: Uni-Sign translation | – | – | P .596 / R .525 / F1 **.548** | – |

Low data:
- **mT5 with 10 % of the labels (F1 0.338) beats raw pose and Fsign at 100 %.**
- mT5 gains only 7.8 F1 points from p10 to p100. Raw gains 5.4 and Fsign 12.4. The mT5 states are already close
  to linearly separable for these concepts.

### 4.3 Per-concept (p100; `full_run/results/tables/per_concept_p100.csv`, which also has P and R)

Columns:
- **missed:** positives that Uni-Sign's translation does not contain.
- **rec:** fraction of the missed positives that each probe fires on.

| Concept | n pos | missed | D F1 | raw F1/AUROC | Fsign F1/AUROC | mT5 F1/AUROC | rec raw | rec Fsign | rec mT5 |
|---|---|---|---|---|---|---|---|---|---|
| HAND | 105 | 57 | 0.57 | 0.13/0.66 | 0.35/0.84 | 0.50/0.84 | 0.23 | 0.16 | 0.19 |
| WORK | 33 | 18 | 0.54 | 0.08/0.73 | 0.14/0.80 | 0.38/0.83 | 0.28 | 0.06 | 0.22 |
| TIME | 75 | 38 | 0.58 | 0.20/0.79 | 0.33/0.86 | 0.50/0.88 | 0.18 | 0.37 | 0.29 |
| TALK | 46 | 16 | 0.60 | 0.15/0.75 | 0.36/0.78 | 0.57/0.85 | 0.12 | 0.12 | 0.12 |
| NICE | 47 | 25 | 0.45 | 0.20/0.73 | 0.27/0.82 | 0.44/0.89 | 0.12 | 0.12 | 0.20 |
| PEOPLE | 29 | 7 | 0.75 | 0.15/0.82 | 0.31/0.89 | 0.53/0.95 | 0.29 | 0.00 | 0.14 |
| SHOW | 42 | 9 | 0.62 | 0.22/0.86 | 0.31/0.91 | 0.64/0.94 | 0.22 | 0.11 | 0.11 |
| FIND | 49 | 19 | 0.59 | 0.07/0.67 | 0.18/0.79 | 0.52/0.89 | 0.11 | 0.11 | 0.11 |
| TOP | 56 | 28 | 0.54 | 0.19/0.78 | 0.36/0.87 | 0.43/0.87 | 0.25 | 0.29 | 0.18 |
| FOOT | 38 | 16 | 0.65 | 0.10/0.82 | 0.37/0.87 | 0.43/0.92 | 0.12 | 0.12 | 0.19 |
| LINE | 47 | 18 | 0.62 | 0.17/0.78 | 0.34/0.85 | 0.47/0.90 | 0.17 | 0.22 | 0.17 |
| WATER | 22 | 5 | 0.77 | 0.22/0.80 | 0.33/0.84 | 0.64/0.90 | 0.00 | 0.00 | 0.00 |
| HELP | 39 | 12 | 0.66 | 0.09/0.74 | 0.30/0.89 | 0.57/0.94 | 0.08 | 0.33 | 0.25 |
| CALL | 30 | 6 | 0.70 | 0.29/0.83 | 0.42/0.86 | 0.59/0.95 | 0.00 | 0.00 | 0.17 |
| TYPE | 46 | 30 | 0.44 | 0.13/0.75 | 0.23/0.81 | 0.48/0.91 | 0.03 | 0.20 | 0.27 |
| CUT | 40 | 27 | 0.38 | 0.19/0.72 | 0.19/0.86 | 0.19/0.86 | 0.26 | 0.11 | 0.19 |
| MOVE | 52 | 29 | 0.53 | 0.10/0.73 | 0.19/0.85 | 0.35/0.90 | 0.10 | 0.14 | 0.07 |
| TURN | 32 | 26 | 0.21 | 0.07/0.70 | 0.09/0.79 | 0.12/0.86 | 0.15 | 0.19 | 0.12 |
| BODY | 40 | 14 | 0.68 | 0.05/0.80 | 0.23/0.87 | 0.36/0.90 | 0.07 | 0.21 | 0.07 |
| PLACE | 30 | 22 | 0.31 | 0.01/0.64 | 0.03/0.77 | 0.11/0.79 | 0.05 | 0.05 | 0.09 |
| PIECE | 32 | 22 | 0.35 | 0.07/0.72 | 0.11/0.79 | 0.18/0.82 | 0.09 | 0.00 | 0.14 |
| LEG | 32 | 10 | 0.80 | 0.03/0.76 | 0.24/0.84 | 0.37/0.93 | 0.10 | 0.00 | 0.10 |
| PULL | 34 | 27 | 0.28 | 0.03/0.72 | 0.14/0.78 | 0.20/0.85 | 0.07 | 0.22 | 0.33 |
| ADD | 36 | 17 | 0.55 | 0.08/0.69 | 0.33/0.78 | 0.43/0.87 | 0.18 | 0.24 | 0.24 |

- mT5 AUROC is higher than Fsign on 24/24 concepts (by under 0.005 on HAND, TOP and CUT).
- The translation's weakest concepts are TURN, PULL, PLACE, PIECE and CUT (D F1 0.21–0.38). These are also the
  weakest for every probe (mT5 F1 0.11–0.20). The hard concepts are hard for every representation; the probes do not
  fill exactly the translation's gaps.
- Per-concept recovery rests on 5–57 missed positives, so individual cells are noisy.

## 5. Fusion readiness: what the specialist probes recover that the translation misses

`full_run/results/fusion_readiness.json` (with CIs), `full_run/results/recovery_counts.json` (absolute counts).
All numbers are Tier L, test_clean and frozen thresholds.

Uni-Sign's translation has 1,032 positive (clip, concept) cells:
- **534 hit**;
- **498 missed (48 %)**;
- plus 354 false mentions.

| p100 probe | Missed positives recovered | Also fires on true negatives the translation left out ("false adds") | Precision of what the probe adds | AUROC among translation misses (D = 0) | OR-fusion Δ macro-F1 vs translation alone |
|---|---|---|---|---|---|
| Raw pose | 74 / 498 (14.9 %) | 1,981 | 3.6 % | 0.673 (0.634–0.715) | −22.2 (−24.2, −19.5) |
| Fsign | 82 / 498 (16.5 %) | 1,030 | 7.4 % | 0.718 (0.689–0.750) | −13.8 (−15.8, −11.4) |
| **mT5 states** | **90 / 498 (18.1 %)** | **581** | **13.4 %** | **0.780 (0.746–0.814)** | **−6.2 (−8.2, −4.0)** |
| Clip length (control) | 123 / 498 (24.7 %) | 7,151 | 1.7 % | 0.634 | −37.8 |

Low data (mean over draws; recovered / false adds / AUROC on translation misses):

| Fraction | Raw | Fsign | mT5 |
|---|---|---|---|
| p10 | 94.6 / 5,606 / 0.607 | 71.6 / 2,543 / 0.657 | 88.8 / 996 / 0.746 |
| p25 | 74.2 / 3,104 / 0.635 | 60.4 / 1,425 / 0.676 | 91.2 / 825 / 0.765 |
| p50 | 75.0 / 2,705 / 0.648 | 65.3 / 1,181 / 0.692 | 92.7 / 750 / 0.771 |
| p100 | 74 / 1,981 / 0.673 | 82 / 1,030 / 0.718 | 90 / 581 / 0.780 |

**Paired differences at p100 (bootstrap CI):**

| Comparison | Recovery rate (macro, unadjusted) | AUROC on misses | Recovery minus false-alarm rate | OR-fusion F1 |
|---|---|---|---|---|
| mT5 vs raw | not significant: +2.8 pts (−2.1, +7.5) | **+0.107 (0.074, 0.143)** | **+5.5 pts (0.7, 10.2)** | +16.0 pts (13.5, 17.9) |
| Fsign vs raw | not significant: +0.4 pts (−4.2, +4.1) | **+0.045 (0.019, 0.072)** | not significant: +2.2 pts (−2.3, 5.9) | +8.4 pts (6.4, 10.1) |
| mT5 vs Fsign | not significant: +2.4 pts (−0.7, +6.4) | **+0.061 (0.037, 0.088)** | +3.3 pts (0.1, 7.3) | +7.6 pts (5.7, 9.4) |

Overlap at p100:
- 157 / 498 missed positives (31.5 %) are recovered by at least one of the three probes.
- 36 are recovered only by mT5, 24 only by Fsign and 31 only by raw. 46 are recovered by both mT5 and Fsign.

How to read this:
1. **Raw recovery counts are not the right measure.**
   - The clip-length control "recovers" the most (123) simply by firing often.
   - The discriminating numbers are the AUROC among the translation's misses and the precision of what the
     probe adds.
2. **mT5 states are the only representation with clear complementary signal beyond the translation.**
   - On clips where the translation omits a concept, the mT5 probe still ranks the true positives above the true
     negatives with AUROC 0.78. This is significantly above raw pose and Fsign.
   - The information is present in the encoder states the decoder reads, but the decoder does not verbalise it.
3. **Fsign adds less.**
   - Its edge over raw pose on the translation's misses is real but small (+0.045 AUROC).
   - Its recovery minus false-alarm rate is not significantly better than raw pose.
4. **The naive late fusion hurts.** OR-ing probe detections into the translation lowers macro-F1 for every arm, by
   −6.2 points for mT5.
   - The probe thresholds were tuned for stand-alone F1 at 1–3 % prevalence, not for a high-precision add-on. Their
     additions are 87 % wrong even for mT5.
   - The translation itself is still the strongest concept detector: F1 0.548 vs 0.416 for the best probe.
   - Any fusion therefore needs a high-precision learned combiner or verifier, not a simple OR of detections.

## 6. Answers

1. **Full extraction:** success. 33,295 / 33,295 clips; all checks pass; bit-exact determinism.
2. **Runtime:**
   - extraction 72.2 min and decoding 43.8 min (both on the T4);
   - download ≈ 6 min; copy back ≈ 46 min;
   - probes 56.6 min and analysis 4.3 min (both on the Mac).
3. **Storage:** 1.7 GiB pooled features + 1.2 GiB test sequences (Mac). The VM holds 7.9 GiB archive + 3.0 GiB
   features + 3.0 GiB tar.
4. **Macro F1 / AUROC (p100, Tier L):**
   - raw 0.125 / 0.750;
   - Fsign 0.256 / 0.834;
   - mT5 0.416 / 0.886;
   - Uni-Sign translation 0.548 F1;
   - length 0.060 / 0.645.
5. **Low data:** mT5 at p10 (F1 0.338) beats raw and Fsign at p100. The Uni-Sign advantage holds at every fraction
   and in the test-only Design B.
6. **Per concept:** see §4.3. mT5 AUROC beats raw on 24/24 concepts.
7. **Missed concepts recovered (p100, of 498):**
   - raw 74, at 1,981 false adds;
   - Fsign 82, at 1,030 false adds;
   - mT5 90, at 581 false adds;
   - 157 by at least one of the three.
8. **Complementary information beyond the translation:**
   - **mT5 states: yes, measurable** (AUROC 0.78 on the translation's misses, significantly above raw).
   - **Fsign: marginal.**
   - Neither is usable through naive OR-fusion at the frozen thresholds.
9. **Does the evidence justify a specialist-head + fusion architecture?** Recommendation:
   - **Justified, narrowly:** tap the **mT5 encoder states** (not Fsign or raw pose).
   - Fuse with a learned, calibrated combiner (translation evidence + probe score, high-precision operating point),
     not with a hard OR.
   - Success must be measured on translation quality (BLEU / chrF / concept recall) on held-out data.
   - Caveats:
     - the formal verdict is PARTIAL because of the S1 gate;
     - the only checkpoint was fine-tuned on How2Sign train;
     - the stand-alone probes do not beat Uni-Sign's own translation.
   - The case for a *separate* pose-based (Fsign/raw) specialist branch is **not** supported by this data.

## 7. Not run (secondary, per plan)

Pools `msd` / `seg4` and the MLP probe (Probe B) were not run in this pass. They are secondary and not part of the
decision. Each is ≈ 1 h of Mac CPU. No fusion model was trained.

## 8. Artifact locations

- **Repo `full_run/`:**
  - `vm_extract/`: run meta, extraction log, VALIDATION, per-file SHA256SUMS;
  - `vm_decode/`: `predictions.jsonl` with all 2,209 predictions, plus `decode_config.json` and logs;
  - `determinism/`, `archive/` (HF expected vs downloaded sizes and hashes), `transfer/`;
  - `results/`: DECISION, fusion readiness, recovery counts, tables, and per-run metrics in `lr_metrics/`, with
    `LR_FULL_OUTPUTS.sha256` covering the full score files.
- **`~/Desktop/curify/p014-work/`:**
  - `features.tar` / `extras.tar` (verified);
  - `full/features` (pooled + test sequences);
  - `results/lr` (full outputs including per-clip test scores and predictions).
- **Scripts added in this pass:** `scripts/summarize_full_run.py` (tables), `scripts/count_recovery.py`
  (absolute recovery counts). Both are descriptive only.
