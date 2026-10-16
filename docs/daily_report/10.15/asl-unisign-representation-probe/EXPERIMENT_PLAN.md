# P0-14: Uni-Sign Representation Probe for Specialist Fusion — Experiment Plan

**Date:** 2026-10-15 · **Branch:** `baobao/visual-production-research-2026-10-05` · **Status: PLAN. Nothing
extracted, nothing probed.** The concept list, split manifest and low-data draws are built and frozen
(`splits/SPLITS.sha256`). The probe and analysis code has been run **only on synthetic data** (self-test, §12).
Not committed.

Background: `DATA_AUDIT.md` (data, checkpoint, leakage); `../UNISIGN_FAILURE_ANALYSIS_SUMMARY.md` (P0-12 closed);
`../../10.07/asl-p0-13-representation-swap/` (the earlier frozen-feature experiment this builds on).

---

## 1. Question

> Do Uni-Sign's pretrained representations contain lexical / semantic information, beyond what raw pose already
> carries, that a lightweight specialist head could read? If so, at which point in the network?

This is the go / no-go question for a **specialist fusion architecture**: small task heads (concept detectors,
later fingerspelling or entity heads) that read frozen Uni-Sign states and feed or correct the translator.

- If frozen Uni-Sign states do **not** make concepts more linearly accessible than raw pose, a specialist head
  gains nothing from tapping them.
- If they do, the comparison between Fsign and mT5 states tells us **where to tap**.

## 2. The three representations (exactly three, one processing chain)

All three come from **one frozen forward pass** of the existing checkpoint, on **the same sampled frames** per clip.
The sampling rule is the upstream one: ≤ 256 frames, `random.sample` seeded with `int(sha256(clip_id)[:8], 16)`,
identical to P0-13.

| ID | Name | Tensor | Dim / frame | Temporal context | Where |
|---|---|---|---|---|---|
| **R1** | Raw RTMPose | Uni-Sign's own normalised input: body 9 + left hand 21 + right hand 21 + face 18 keypoints × (x, y, conf), after `load_part_kp` (signer crop/scale normalisation, hands relative to wrist, face relative to nose, conf ≤ 0.3 zeroed) | 207 | none | `datasets.load_part_kp` output |
| **R2** | Uni-Sign **Fsign** | 4 part streams after spatial GCN → temporal GCN (kernel 5) → mean over keypoints → concat + `part_para` | 1024 | local (temporal conv) | **input of `pose_proj`** (forward pre-hook) |
| **R3** | mT5 encoder states | mT5-Base encoder `last_hidden_state` at the T pose positions (8 prefix-token rows dropped) | 768 | global (12 self-attention layers) | `mt5_model.encoder(...)` |

- R1 is exactly what R2 is computed from, and R2 (via the linear `pose_proj`) is exactly what R3 is computed from.
  So any difference between arms is due to the learned Uni-Sign layers, not to different inputs, timing, crop or
  normalisation.
- `pose_proj`'s output (768-d) is saved as a diagnostic only. It is a linear map of R2, so a linear probe cannot
  extract more from it than from R2.
- Precision: **fp32**, the same as P0-13's validated path (fp32 vs official bf16: mean per-frame cosine 0.9994).
- Not in scope for v1: intermediate mT5 layers, the decoder, RGB.

## 3. Task: high-frequency lexical / semantic concepts from English references

- One **binary** label per (clip, concept): does the clip's English reference contain the concept?
- **Selected from train references only.** Script: `scripts/build_concepts.py`; rules frozen in
  `concepts/concept_rules_v1.json`.
- Val and test counts were computed only afterwards, for reporting.
- No fingerspelling and no ASL-specific manual labels.

**Selection rules (Tier L, lexical lemmas):**
1. Lowercase; delete `going to` / `gonna`; tokenise; fold regular inflections and a short irregular list into
   lemma families.
2. Exclude:
   - stopwords;
   - discourse fillers ("actually", "okay", "kind", "bit", …);
   - light / auxiliary verbs (go, get, make, take, put, want, need, see, look, know, think, use, …);
   - generic nouns and adjectives (one, thing, way, good, new, …);
   - URL fragments ("com").
3. Keep a lemma only if all of these hold:
   - train clip frequency ≥ 400 and ≤ 30 % of clips;
   - positives come from ≥ 100 distinct train videos;
   - ≤ 20 % of positives come from the 10 most frequent videos (this removes topic-locked words such as "hair",
     "ball").
4. Take at most 40, ranked by frequency. 24 pass.

**Tier L (24, primary):**

HAND, WORK, TIME, TALK, NICE, PEOPLE, SHOW, FIND, TOP, FOOT, LINE, WATER, HELP, CALL, TYPE, CUT, MOVE, TURN, BODY,
PLACE, PIECE, LEG, PULL, ADD

**Tier S (6 fixed semantic groups, secondary / exploratory):** NUMBER, COLOR, FOOD_COOKING, BODY_PART, TIME_UNIT,
WATER_LIQUID. Word lists are fixed in the script. Ambiguous members are removed: back, face, second, one.

**Deliberate exclusion.** WANT, NEED, SEE, LOOK, KNOW, THINK and USE are real ASL signs. In the English references,
however, they are dominated by discourse use ("you want to", "you know"), so the English token is a poor label. They
are excluded from v1 and recorded as a possible v2 change. The manager's examples BOOK, READ, SCHOOL and MONEY do not
reach the frequency floor in How2Sign train (How2Sign is instructional how-to video). Forcing them in would leave
tiny positive sets.

Counts per concept: `concepts/concept_list_v1.csv`, `splits/concept_counts_by_role.csv`.
- Tier L train positives: 404–847.
- p10 draw positives: 27–91.
- test_clean positives: 22–105, from 11–37 videos.

## 4. Splits and leakage control

**Key constraint (DATA_AUDIT §4):** Uni-Sign was fine-tuned on every How2Sign train clip. Only How2Sign test is
clean.

| Role | Clips | Use |
|---|---|---|
| `probe_train` | 31,086 (How2Sign train ∩ official poses, 2,192 videos) | probe fitting, CV, thresholds (Design A) |
| `test_clean` | 2,209 (How2Sign test ∩ official poses, minus 140 exact / near duplicates of a train reference; 149 videos) | **all evaluation** |
| `test_dup_excluded` | 140 | not used (listed in `audit/near_duplicates_test.csv`) |
| How2Sign val | 1,741 | not used (no official poses; see §13, optional extension) |

**Design A (primary): train on probe_train, evaluate on test_clean.**
- This mirrors the real fusion setting: specialist heads would be trained on labeled How2Sign-style data and applied
  to new video.
- Groups are source videos (`VIDEO_ID`). The official splits share no video (audit).
- Probe-internal CV uses 5 video-grouped folds (`cv_fold` in the manifest).

**Design B (required leakage control): train and evaluate inside test_clean only.**
- 5 outer folds by video; 4 inner folds by video choose L2 and the threshold; repeated with 3 fold seeds.
- No representation has seen any of these clips or sentences. If the Uni-Sign advantage in Design A came only from
  memorized train features, it would shrink or vanish here.

**Other protections:**
- Concept vocabulary from train only.
- Duplicate and near-duplicate test references removed.
- No test labels used for any choice: hyper-parameters and thresholds come from probe-train out-of-fold predictions.
- Splits frozen and hashed before any feature exists.
- Signer: How2Sign publishes no signer IDs, and the official splits share signers, so **signer-independent
  evaluation is not possible in the primary design**. Secondary check: the 257 test_clean clips whose (unverified)
  signer proxy never occurs in train.

## 5. Probe (identical for all three representations)

**Probe A: primary, logistic regression.**
- One independent L2-regularised binary logistic regression per concept. They are implemented jointly as a K-output
  linear layer with full-batch L-BFGS, which is mathematically the same as K separate regressions.
- Features are standardised with probe-train statistics.
- Class imbalance: `pos_weight = n_neg / n_pos` per concept.
- L2 strength λ ∈ {1e-4, 1e-3, 1e-2, 1e-1, 1}, chosen **per concept** by 5-fold grouped CV on the probe-train draw
  (out-of-fold AUROC).
- Decision threshold per concept: the one maximising out-of-fold F1 at the chosen λ.

**Probe B: secondary, small MLP.**
- One hidden layer (256, ReLU, dropout 0.2), multi-label BCE with `pos_weight`, AdamW (lr 1e-3, wd 1e-2),
  batch 256, ≤ 100 epochs.
- Early stopping on video-grouped fold 0 by macro AUROC, patience 10. 3 seeds.
- Run on p10 / p25 (3 draws each) and p100.

**Sanity baselines, through the identical probe:**
- `length`: log T and log raw frame count. This addresses the 1.1–1.6× length confound (audit §5).
- `shuffle`: R3 features with permuted training labels. Must land at chance.

## 6. Pooling (identical operator for every representation)

Statistics are computed over the same T sampled frames:

| Pool | Definition | Probe input dim (R1 / R2 / R3) | Role |
|---|---|---|---|
| **ms** | [mean ; std] over time | 414 / 2048 / 1536 | **primary** |
| msd | [mean ; std ; mean \|x_t − x_{t−1}\|] | 621 / 3072 / 2304 | secondary: gives raw pose explicit motion, so R1 is not a straw man |
| seg4 | means of 4 equal temporal segments, concatenated | 828 / 4096 / 3072 | secondary: coarse temporal order |

- Pooling is over pose positions only. Padding never enters, and mT5 prefix rows are excluded.
- Dimensions differ between representations. The synthetic null test showed that extra uninformative dimensions
  *hurt* a probe (§12), so higher dimension does not automatically favour Uni-Sign.
- A PCA-to-256 dimension-matched variant is listed as an **optional** check if R1 wins (not implemented yet).

## 7. Metrics

Per concept on test_clean:
- precision, recall and F1 at the out-of-fold threshold;
- **AUROC**;
- AUPRC;
- F1 at a label-free *prevalence-matched* threshold (top-q scores, q = train prevalence). This is a sensitivity
  check against calibration shift.

Macro averages are reported separately for Tier L (primary) and Tier S. Uncertainty comes from a **paired
video-cluster bootstrap** over the 149 test videos (B = 2,000; the same resample for every arm). Low-data deltas are
averaged over draws before the bootstrap.

## 8. Low-data experiments

Nested draws of **whole source videos** from probe_train, filled to a clip-count target. They are frozen in
`splits/draws.json`.

| Fraction | Draws | Clips (draw 0) | Videos (draw 0) |
|---|---|---|---|
| 10 % | 5 | 3,110 | 218 |
| 25 % | 5 | 7,788 | 549 |
| 50 % | 3 | 15,546 | 1,108 |
| 100 % | 1 | 31,086 | 2,192 |

Within one draw seed the subsets are nested (10 ⊂ 25 ⊂ 50 ⊂ 100). Evaluation is always on the full test_clean set.

## 9. Pre-registered success criteria (frozen before any feature exists)

Primary endpoint: **Tier L macro-F1**, Design A, p100, Probe A (LR), pool `ms`, test_clean.
Two confirmatory comparisons: **R2 vs R1** and **R3 vs R1**.

| # | Criterion | Rule |
|---|---|---|
| C1 | Primary effect | Δ macro-F1 ≥ **+5.0 points** and the 95 % cluster-bootstrap CI lower bound > 0 |
| C2 | Threshold-free agreement | Δ macro-AUROC ≥ **+0.03**, CI lower bound > 0 |
| C3 | Consistency across concepts | per-concept AUROC higher than R1 for ≥ **17 / 24** Tier L concepts (≈ 70 %; one-sided sign test p ≈ 0.03) |
| C4 | Holds in low data | at **p10 and p25** (mean over 5 draws each): Δ macro-F1 ≥ +5.0 points, CI lower bound > 0 |
| C5 | Not just clip length | the representation's macro-AUROC exceeds the `length` baseline's by ≥ **0.05** |
| C6 | Not memorization | **Design B** Δ macro-AUROC (mean of 3 repeats) > 0, CI lower bound > 0 |
| S1 | Sanity gate | `shuffle` macro-AUROC within [0.47, 0.53]; otherwise the pipeline is broken and nothing is interpreted |

**Verdict per comparison:**
- **STRONG SUPPORT**: C1–C6 all pass, and S1 passes.
- **PARTIAL SUPPORT**: C1 and C2 pass, but at least one of C3–C6 fails. The report names which, because each one
  means something different. C4 failing means "only helps with lots of labels". C6 failing means "possibly
  memorization".
- **NOT SUPPORTED**: C1 or C2 fails.

**Layer choice (descriptive, answers "where to tap"):** R3 vs R2 on the same endpoint.
- Prefer **R3** only if Δ macro-F1 ≥ +2 points with CI > 0.
- Otherwise prefer **R2**: it is cheaper (no 12-layer encoder pass) and closer to the signing.

**Reported but not part of the decision:**
- Tier S;
- pools msd and seg4;
- MLP;
- AUPRC;
- prevalence-matched F1;
- the unseen-signer-proxy subset;
- per-concept tables.

If the MLP reverses the LR verdict, that is reported as a finding (non-linear accessibility). The verdict itself is
not changed.

`scripts/analyze_probe.py` encodes C1–C6, S1 and the layer rule verbatim. **These thresholds are not to be edited
once features exist.**

## 10. Compute, runtime, storage

| Stage | Where | Work | Runtime (estimate) | Storage |
|---|---|---|---|---|
| 0 Smoke test (128 committed test PKLs + 8 decodes) | Mac CPU | 128 forward passes | ~2–5 min | < 0.1 GB |
| 1 Download official pose archive | either | 8.46 GB download | 10–30 min (network) | 8.5 GB (deletable after stage 2) |
| 2 Extract R1 / R2 / R3, 33,295 clips | **Mac CPU, fp32** (default) or T4 | 1 frozen forward pass per clip, no decoding | **≈ 3.7 h on Mac CPU**: P0-13 measured 0.4 s/clip for the same forward pass. T4 fp32: ~0.5–1 h (unmeasured estimate) | pooled features ≈ 1.9 GB (float32); test_clean sequences ≈ 1.2–2.3 GB (float16) |
| 3 Probes: LR on all draws × 5 arms × 3 pools + Design B; MLP subset | Mac CPU | ≈ 30 L-BFGS fits per (arm, draw) | ≈ 1–2 h (synthetic self-test: 10 s at p10, 15–20 s at p25 per 2k-dim arm; ~30 s per Design B repeat) | < 1 GB (results JSON incl. test scores) |
| 4 Bootstrap + decision | Mac CPU | B = 2,000 | ≈ 5–15 min | negligible |

**GPU requirement: none.** The only heavy step is a frozen encoder forward pass with no decoding. P0-13 already ran
this exact pass on the Mac CPU at 0.4 s/clip. The T4 VM is sufficient if speed matters: one session, ≤ 1–1.5 h
including download, ~16 GB RAM, ~15 GB disk. It is not needed.

**Optional GPU run (recommended, not required):** decode the 2,209 test_clean clips with Uni-Sign's own decoder
(T4, fp16, beam 4; ~20–40 min), to get an **"output-text keyword" reference**: does the concept word appear in
Uni-Sign's own translation? If an R3 probe cannot beat simply reading Uni-Sign's output, a specialist head adds
nothing over the decoder for that concept. This is the most direct fusion-relevant comparison, and it is cheap. CPU
decoding is possible but slow (several s/clip).

## 11. Execution order and gates

1. Re-clone Uni-Sign at `eed438bc`; verify the checkpoint sha256; verify `splits/SPLITS.sha256`.
2. **Stage 0 smoke** (`STAGE=0 bash scripts/run_p014.sh`). Pass if:
   - all shapes are `(T, 207) / (T, 1024) / (T, 768)` and finite;
   - the 8 own-decoder decodes track the committed P0-12 `A_official` predictions (P0-13's faithfulness check gave
     mean chrF 63 against the authors' predictions).

   **Stop if this fails.**
3. Stage 1 download, then stage 2 extraction (resumable, sharded). Pass if 33,295 / 33,295 clips have features.
4. Stage 3 probes, then stage 4 decision. Report every arm, including failures.

## 12. Validation already done (synthetic only)

`run_probe.py --synthetic` plants concept signal in random features:

| Self-test | Planted | Verdict produced |
|---|---|---|
| Positive | R3 > R2 > R1 information | R2 and R3: STRONG SUPPORT; `shuffle` and `length` at AUROC 0.48–0.52 |
| True null | R2 and R3 = random rotation of R1 + pure-noise padding (identical information) | R2 and R3: **NOT SUPPORTED** (Δ macro-F1 −0.12) |

This checks the code path and the decision logic only. It says nothing about the real result.

## 13. What this experiment can and cannot answer

**Can answer:**
- Whether frozen Uni-Sign states make English-lexical concepts **more linearly accessible** than raw pose, on clips
  Uni-Sign never trained on, at 10–100 % of the labels.
- **Which layer** (Fsign vs mT5 encoder) a specialist head should read.
- How fast each representation's advantage shrinks or grows with label count. This is the relevant number for
  small-data specialist heads.

**Cannot answer:**
- **Whether a fusion architecture improves translation.** A good probe is necessary, not sufficient. The fusion
  itself must be built and tested on BLEU/chrF in a later step.
- **Pretraining vs fine-tuning.** The only checkpoint was fine-tuned on How2Sign train with these exact sentences.
  A positive result is partly expected by construction, because Uni-Sign was optimised to produce these words. The
  informative part is **how large** the gap is on clean test clips and whether it **survives Design B and low data**.
- ASL-linguistic claims. Labels are English-translation proxies, not glosses.
- Generalisation to non-How2Sign video, or to unseen signers (only an unverified proxy subset).

**Optional extension (not in v1).** Extract RTMPose on How2Sign val (1,741 clips, never used by Uni-Sign) with our
own extractor on the re-aligned timing. P0-12 showed it is close to official once timing and crop match. This would
nearly double the clean evaluation pool. It requires val videos and a GPU/CPU pose-extraction run, and it brings a
pose-source shift, so it is a second-round option.

## 14. Risks

| Risk | Mitigation |
|---|---|
| Absolute F1 is low for every arm (1–3 % base rates, noisy English proxies) | Decision is on *deltas* with CIs; AUROC co-criterion; shuffle/length baselines show the floor |
| Wide CIs (22–105 test positives per concept) | Macro + cluster bootstrap + sign count (C3); Tier S has larger counts as secondary |
| Memorized train features distort thresholds for R2/R3 | AUROC co-criterion (C2), prevalence-matched F1 sensitivity, Design B (C6) |
| R1 handicapped by having no motion features | msd pool reported for all arms |
| Topic leakage (concept predictable from video topic) | ≤ 20 % top-10-video concentration rule; video-grouped splits; still a caveat |
| Upstream frame subsampling (> 256 frames, 15–20 % of clips) adds noise | Same frames for all three arms; seeded and reproducible |

## 15. File layout

```
10.15/asl-unisign-representation-probe/
├── EXPERIMENT_PLAN.md            this file
├── DATA_AUDIT.md                 data / checkpoint / leakage audit
├── README.md                     file index + commands
├── audit/
│   ├── data_audit.json           split sizes, overlaps, duplicate counts, CSV sha256
│   ├── near_duplicates_test.csv  140 test (+92 val) refs duplicating a train ref
│   └── official_pose_archive_index.csv   33,435 archive entries (offsets, sizes, CRC)
├── concepts/
│   ├── concept_list_v1.csv       24 Tier L + 6 Tier S concepts, forms, per-split counts
│   ├── candidate_vocab_train.csv top-300 train lemma families + exclusion reason
│   └── concept_rules_v1.json     every list and threshold used
├── splits/                       FROZEN (SPLITS.sha256)
│   ├── manifest.csv              35,263 rows: role, cv_fold, group, signer_proxy, length, 30 labels
│   ├── draws.json                low-data video draws
│   └── concept_counts_by_role.csv
├── scripts/
│   ├── build_concepts.py         [run]  audit + concept vocabulary (stdlib)
│   ├── list_pose_archive.py      [run]  zip central-directory listing (no download)
│   ├── build_splits.py           [run]  manifest + draws
│   ├── extract_representations.py [NOT RUN] one frozen pass -> R1/R2/R3 pooled (+ test sequences)
│   ├── run_probe.py              [synthetic self-test only] LR / MLP probes, Design A + B
│   ├── analyze_probe.py          [synthetic self-test only] bootstrap + C1–C6 verdicts
│   └── run_p014.sh               staged runner (0 smoke … 4 analyze)
```
