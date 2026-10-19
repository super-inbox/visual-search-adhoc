# ASL / Uni-Sign Work Report: tasks a–e

**Date:** 2026-10-19 (status as of 02:39 CDT; updated with the P0-18 128-clip development comparison) · **Branch:** `baobao/visual-production-research-2026-10-05`
**System under study:** the public Uni-Sign pose-only How2Sign checkpoint. No model was trained or modified.

This report only summarises existing files. It does not change any recorded verdict. Every result in the Uni-Sign
line so far is **exploratory or validation-level, not confirmatory** (P0-16). The first confirmatory evaluation will
be P0-18 on the sealed holdout H18.

## Executive summary

- **a. Timing / crop diagnosis: done.** P0-12 showed that our old low score came mostly from **input preparation**,
  not from our pose extractor. Using the official timing + crop recovered **≈ 86 % of the BLEU-4 gap** (5.47 → 8.61
  vs 9.13). This used the official (oracle) inputs **as a diagnosis; it was not an automatic fix**. A later
  exploratory split on the same 128 clips attributes most of the gain to **timing** (+3.15 BLEU-4). The crop effect
  is small (+0.69) and its confidence interval includes zero.
- **b. Representation / fusion: done, paused.** P0-14: **PARTIAL SUPPORT**, read as exploratory evidence because of a
  documented sanity-gate inconsistency. Uni-Sign's mT5 encoder states carry concept information the translation
  sometimes drops. P0-15: **NOT SUPPORTED**; a verifier could not make safe additions. **No translation improvement
  has been shown.** P0-19 has not started.
- **c. Automatic preprocessing (P0-18): IN PROGRESS.**
  - Done: GPU pose extraction (184 test videos, 0 failures), the automatic timing detector and crop, all conditions
    built, and the **128-clip development comparison**.
  - On the 128 clips, Automatic improves over Old by **+1.53 BLEU-4 / +3.14 chrF**. That recovers about **42 % of the
    Old→Oracle BLEU gap (54 % of chrF)**.
  - **Timing is the main weakness, not crop.** The automatic crop is already close to the official crop.
  - There is a **WER trade-off**: WER rises, because the automatic window is longer and so are the outputs.
  - **This is a development result on the reused 128-clip set, not the P0-18 conclusion.**
  - Still pending: the full-test 6-arm decode, the freeze and the H18 dry run. H18/H19 remain sealed.
- **d. ASL-fluent reviewer: materials prepared; no recruitment recorded.** The review package and instructions exist.
  The repository has **no record that a reviewer was recruited or contacted**, and no manual ASL label exists.
- **e. Inspection sheet: done and pushed.** It has 45 clips, 21 highlighted examples and 7 categories. All labels are
  automatic weak labels; every reviewer field is blank. The "production" column is a provisional stand-in.

---

## a. Timing / crop diagnosis (P0-12): COMPLETED

**What was done.** The Uni-Sign checkpoint, the 128 benchmark clips, the references and the evaluation code were held
fixed. Only the pose source and the input preparation were changed: timing, crop and coordinate normalisation. The
goal was to explain why our pipeline scored far below the official one. The **official re-aligned timing and the
official signer crop are oracle inputs**: they come from the dataset authors, not from any automatic method. P0-12 used
them **diagnostically**, to measure how much of the gap they explain. It did **not** produce an automatic fix. Building
that fix is task c.

**Formal P0-12 results** (committed; T4 / fp16; single run per condition; 128 clips):

| Condition | Pose source | Timing / crop | BLEU-4 | ROUGE | BLEURT |
|---|---|---|---|---|---|
| A_official | official poses | official timing + signer crop | **9.13** | 29.00 | 0.4407 |
| B_ours_5p39 | our extractor | original timestamps, full frame | **5.47** | 18.69 | 0.3767 |
| B_aspect | our extractor | as B + aspect / coordinate fix | **5.80** | 20.59 | 0.3849 |
| C_ours_on_official_crop | our extractor | official timing + signer crop | **8.61** | n/a | n/a |

- B → C (timing + crop + normalisation, same extractor) recovers **85.7 %** of the BLEU-4 gap (ROUGE 87.1 %,
  BLEURT 75.1 %).
- The aspect fix alone adds **+0.32** BLEU-4.
- The remaining extractor gap (C → A) is **+0.52** BLEU-4.
- Caveats:
  - T4/fp16, not the official bf16: A_official scores 9.13 here vs 9.59 for the authors' released predictions.
  - The contrasts between conditions are the result; the absolute values are not.
- As recorded in P0-12, **timing and crop could not be separated in that design.**

**Later factorial timing-vs-crop split** (P0-18 development run, 2026-10-16):
- Exploratory and not committed. The scores are in the local P0-18 work directory (`dev/score128.json`).
- Inputs: the same 128 clips and the existing P0-12 poses. Only crop width/height is varied, because Uni-Sign is
  translation-invariant.
- Decoding ran on the Mac CPU, so absolute values differ slightly from P0-12.
- Single run. Paired bootstrap over source videos (B = 2000).

| Condition | Timing | Crop | BLEU-4 | Δ vs A_old [95 % CI] |
|---|---|---|---|---|
| A_old (= B_ours_5p39) | original | full frame | 5.13 | n/a |
| A_oraclecrop | original | official crop | 5.82 | +0.69 [−0.25, +1.58] |
| C_fullframe | re-aligned | full frame | 8.28 | **+3.15 [+1.69, +4.72]** |
| C_oracle (= C_ours_on_official_crop) | re-aligned | official crop | 8.97 | **+3.84 [+2.37, +5.45]** |

Crop given correct timing (C_oracle − C_fullframe): +0.70 [−0.43, +1.79].

**Current conclusion:**
- **Timing is the main driver.** Timing alone gives ≈ 82 % of the combined timing + crop gain (3.15 / 3.84).
- The crop adds a small gain whose CI includes zero, with or without corrected timing.
- This split is exploratory: single run, on the 128 clips that also generated the hypothesis, and not yet
  confirmatory.
- The P0-18 128-clip run with GPU poses (task c) points the same way:
  - oracle timing alone: +2.44 BLEU-4 [+1.00, +4.09] (O_time − A_old);
  - automatic crop on top of oracle timing: +0.76 [−0.13, +1.74] (O_time_crop − O_time).

  The full-test run and H18 will give the final split.

## b. Representation / fusion (P0-14, P0-15): COMPLETED, PAUSED

**P0-14 representation probe** (2,209 clean test clips, 24 lexical concepts, linear probes on frozen features):

| Representation | Concept macro-F1 | Macro-AUROC |
|---|---|---|
| Raw RTMPose pose | 0.125 | 0.750 |
| Uni-Sign Fsign | 0.256 | 0.834 |
| **Uni-Sign mT5 encoder states** | **0.416** | **0.886** |
| Uni-Sign's own translation (reference) | 0.548 | n/a |

- The translation misses 498 of 1,032 positive concept mentions.
- At its frozen threshold, the mT5 probe recovers 90 of them, at the cost of 581 wrong additions.
- On those misses, the probe still ranks true over false at **AUROC 0.78**.
- **Recorded verdict: PARTIAL SUPPORT** (kept). The shuffled-label sanity control S1 missed its bound narrowly
  (0.53017 vs 0.53).
- **Sanity-gate inconsistency** (P0-16 H1):
  - The plan's prose said an S1 failure means "nothing is interpreted".
  - The frozen code returned PARTIAL instead.
  - All of C1–C6 passed, so the PARTIAL label matches neither the prose nor the plan's own PARTIAL definition.
  - Under the new P0-16 policy this would be **VOID**.
  - The verdict is not rewritten; P0-14 is read as **exploratory evidence**.

**P0-15 high-precision fusion** (development half):
- Naive union of probe detections: 331 additions, 50 correct, **net −231**.
- The learned verifier ranks better than the raw mT5 margin: AP 0.110 vs 0.094, and 11/20 vs 7/20 correct in the
  top 20.
- The best Wilson 90 % lower bound on add-precision is 0.393, below the required 0.50. **Nothing was added.**
- **Verdict: NOT SUPPORTED** (kept).
- P0-16 later found (H2) that the P0-15 "sealed" final half had already been observed. It is now **retired from
  confirmatory use**. The verdict is unaffected, because it was decided on dev.

**What was learned:**
- Uni-Sign's internal states, especially the mT5 encoder, carry complementary lexical information that the translation
  sometimes omits.
- Uni-Sign's own translation is still the best stand-alone concept detector.

**Why fusion is not solved:**
- The specialist signal is not precise enough to add safely.
- Naive fusion adds far more wrong concepts than right ones.
- No fused sentence has been produced or measured.
- **No sentence-translation improvement is claimed.**

**Remaining for P0-19** (final fusion experiment; **not started**):
- Pre-register the design, gates and the **explicit exit criteria** (NOT SUPPORTED or VOID on H19 closes the fusion
  line).
- Use the input pipeline that P0-18 freezes if P0-18 is SUPPORTED; otherwise official crops + our extractor.
- Candidate next signal from the 10.16 recommendation: decoder confidence / sequence score. It is untested.
- Evaluate once on **H19**. Development may use test data, and H18 only after P0-18's one-shot run.

## c. Automatic preprocessing (P0-18): IN PROGRESS

> **IN PROGRESS — this section will be updated after the final Old vs Automatic vs Oracle comparison finishes.**

**Goal:** replace the oracle timing + crop with an automatic method that uses only video frames and the original
timestamps (production-legal), and measure it against both extremes:
- **Old:** `A_old`, original window, full frame.
- **Automatic:** `B_auto`, automatic interval + automatic crop.
- **Oracle:** `O_time_crop` / `C_official`, re-aligned window, official crop.

Ablation arms: `B_time_only`, `B_crop_only`, `B_lag_only`, `O_time`.

Development uses How2Sign **test** only; **H18 and H19 remain sealed**. Sources:
- scripts: `docs/daily_report/10.16/asl-p0-18-auto-preprocessing/scripts/` (untracked);
- outputs: the local P0-18 work directory, `~/Desktop/curify/p018-work/dev/` (outside the repo, not committed).

**1. GPU full-video pose extraction: completed**

| Item | Value |
|---|---|
| Test videos | **184 / 184 completed, 0 failed** (all 2,357 test clips) |
| Frames | 521,219 · 31.3 fps · ≈ 4.6 h of pose time |
| Environment | Tesla T4; onnxruntime-gpu 1.23.2 (CUDA EP active); rtmlib 0.0.13; same two ONNX models (sha256 recorded) |
| Oracle arm `C_official` | official crop videos posed in the same environment: **128 / 128 clips, 0 failed** (29,113 frames) |

**Determinism caveat:**
- ONNX Runtime logs a "non-deterministic TopK kernel" warning on the GPU.
- I found **no recorded result** of the planned determinism preflight (extract the same video twice, require
  identical arrays).
- This must be shown by the G1/G2 gates before the freeze.

**2. Timing detector: current result** (interval IoU with the re-aligned window; 2,357 clips; 5-fold CV grouped by
video; no translation metric read). This is an intermediate note, not the P0-18 conclusion.

| Detector | Mean IoU | Median IoU | IoU ≥ 0.5 | IoU = 0 | Median start / end error |
|---|---|---|---|---|---|
| Original timing (old pipeline) | 0.335 | 0.195 | 35.3 % | 42.3 % | 2.73 s / 3.48 s |
| **Selected: original + offsets + activity snap** | **0.350** | **0.317** | **38.4 %** | **35.3 %** | 2.58 s / 2.68 s |
| Per-video constant lag (pose-estimated) | 0.275 | 0.064 | 29.7 % | 47.2 % | 5.33 s / 5.17 s |
| Per-video linear warp (pose-estimated) | 0.292 | 0.107 | 31.4 % | 44.6 % | 4.73 s / 4.45 s |

- The gain over the original timestamps is modest: +0.015 mean IoU and 7 points fewer zero-overlap clips.
- Estimating the drift from pose activity does not work, because signers are active 92–99 % of the time.
- An oracle-fitted warp would reach about 0.61 mean IoU, so **most of the timing gap is not recovered by pose-only
  timing**.
- Given task a's finding that timing is the main driver, this is the key risk for P0-18.

**3. Crop: current result** (box IoU with the official crop; 128 clips; 5-fold CV grouped by video):

| | Mean box IoU | Median abs. log-aspect error |
|---|---|---|
| Full frame (old) | 0.301 | 0.783 |
| **Automatic crop (selected)** | **0.868** (CV) | **0.098** |

**4. Conditions built:**
- All 7 arms built for all 2,357 test clips. **2,347 are evaluable**: 8 clips have too few frames in every arm, and 2
  have too few in the automatic-timing arms.
- The automatic interval fell back on 15 clips (0.64 %).

**5. Decoding** (Mac CPU, 3 shards × 4 threads, frozen settings):

| Set | Arms | Status at 02:39 CDT |
|---|---|---|
| 128 benchmark clips | 8 (A_old, B_auto, C_official, B_time_only, B_crop_only, O_time, O_time_crop, B_lag_only) | **Decoded and scored** (`dev/score_gpu/score128.json`, 02:28) |
| Full test (2,347 clips) | 6 (A_old, B_auto, B_time_only, B_crop_only, O_time_crop, O_time) | **Not completed.** No full-test output exists yet, and no local decode process was running at 02:39 |

**6. Old vs Automatic vs Oracle: 128-clip development comparison**

> **Development result on the reused 128-clip benchmark (exploratory, single run). Not the P0-18 conclusion and not
> confirmatory.** These clips generated the earlier hypotheses. The full-test comparison and the H18 one-shot run
> decide P0-18.

Setup: GPU poses; Mac CPU decoding; paired bootstrap over source videos (B = 2000; 128 clips / 128 videos).

| Arm | Timing | Crop | BLEU-4 | chrF | WER | Length ratio |
|---|---|---|---|---|---|---|
| **A_old (Old)** | original | full frame | **5.12** | 21.99 | 97.7 | 0.83 |
| B_crop_only | original | automatic | 6.09 | 23.53 | 95.6 | 0.82 |
| B_time_only | automatic | full frame | 6.49 | 25.08 | 102.3 | 0.96 |
| **B_auto (Automatic)** | automatic | automatic | **6.65** | 25.13 | 103.1 | 0.98 |
| B_lag_only | automatic (lag variant) | automatic | 6.75 | 25.16 | 103.5 | 0.97 |
| O_time | oracle (re-aligned) | full frame | 7.56 | 27.07 | 94.7 | 0.91 |
| O_time_crop | oracle | automatic | 8.32 | 27.23 | 92.6 | 0.89 |
| **C_official (Oracle)** | oracle | official crop | **8.79** | 27.76 | 93.1 | 0.89 |

What the 128-clip result shows:
- **Automatic beats Old:** B_auto − A_old = **+1.53 BLEU-4** [+0.18, +2.80] and **+3.14 chrF** [+1.70, +4.70].
- **It recovers about 42 % of the Old→Oracle BLEU-4 gap** (1.53 of 3.67) and **54 % of the chrF gap** (3.14 of 5.77).
  Oracle − Automatic is still +2.14 BLEU-4 [+0.68, +3.90].
- **Automatic timing carries most of the BLEU gain:**
  - B_time_only − A_old = +1.38 BLEU-4 [+0.12, +2.44].
  - Adding the automatic crop on top of automatic timing adds only +0.16 [−0.73, +1.03] (B_auto − B_time_only).
- **The automatic crop alone** gives +0.97 BLEU-4 [−0.18, +2.20] and +1.54 chrF [+0.35, +2.92] (B_crop_only − A_old).
- **The automatic crop is already close to the official crop:**
  - With oracle timing, it reaches 8.32 BLEU-4, vs 8.79 with the official crop.
  - The difference is +0.47 [−0.25, +1.21] (C_official − O_time_crop).
- **The main current weakness is timing, not crop.**
  - With the same automatic crop, oracle timing (O_time_crop, 8.32) is well ahead of automatic timing (B_auto, 6.65).
  - This matches the timing-agreement result above (mean IoU 0.350 vs 0.335).
- **WER trade-off:** WER gets worse with automatic timing. B_auto − A_old = **+5.39 WER** [+1.74, +9.22].
  - The selected automatic window is longer: median 6.86 s, vs 5.15 s for the original window and 6.05 s for the
    oracle window on these 128 clips.
  - Outputs get longer too: length ratio 0.83 → 0.98, a change of +0.15 [+0.09, +0.21].
  - BLEU-4 and chrF rise while WER also rises. This is consistent with the longer outputs adding both correct and
    incorrect words.
  - Oracle timing does not have this cost: O_time_crop's WER is 92.6, vs 97.7 for Old.
- **So P0-18 currently shows a BLEU/chrF improvement with a WER trade-off.** Under the planned criterion P5 (length /
  WER guard), this trade-off would matter. The P5 thresholds are not frozen yet.
- **It is still a development result** on the reused 128-clip set. It is not the full-test estimate, not frozen, and
  not confirmatory.

**7. Next steps through freeze and H18 dry run** (per the P0-18 scripts and the P0-16 rules):
1. Check Mac-vs-T4 decode equivalence. Decode and score the full test set (6 arms, 2,347 clips): BLEU-4, chrF, WER,
   length ratio, and paired bootstrap over source videos. The 128 set is done.
2. Write `DEVELOPMENT_RESULTS.md` and the P0-18 `EXPERIMENT_PLAN.md`: primary endpoint, arms, and the frozen
   thresholds for criteria **P1–P5**:
   - P1: Automatic beats Old on BLEU-4 with CI > 0;
   - P2: Automatic recovers a pre-registered fraction of the Old→Oracle gap;
   - P3: failure rate;
   - P4: preprocessing time per clip;
   - P5: length ratio and WER guard.

   Verdict: all pass → SUPPORTED; all but P2 → PARTIAL; any gate fails → VOID; otherwise NOT SUPPORTED.
   **The plan and its thresholds do not exist yet.**
3. Show GPU extraction and decoding determinism (gates G1–G3).
4. Run the plan-code verdict test, then `make_freeze.py` → `FREEZE.json`. Commit the plan, code and freeze.
5. **H18 dry run:** `run_h18_oneshot.py --mode dryrun` on development (test) videos only, to exercise the full
   one-shot path.
6. **H18 one-shot run only after explicit approval** (`--mode h18 --confirm OPEN-H18`).
7. **H18 and H19 remain sealed.** No H18/H19 clip, frame, reference or output has been opened, and none was opened
   for this report.

## d. ASL-fluent reviewer

**Prepared:**

| Item | Status |
|---|---|
| Two-role review package for the 45 queued clips (`10.13/.../manual_review/`): review page, blank forms, video checksums | Exists locally. Only `review_packet.csv`, `weak_labels.csv` and the builder are committed (`c94e9c4c`) |
| Reviewer instructions for the ASL-fluent role (`ASL_REVIEWER_INSTRUCTIONS.md`, ≈ 1.5–3 h of work) | Exists locally, untracked |
| Task-e inspection sheet with a human-review box, locked until the reviewer's ASL background is entered | Committed and pushed |

**Recruitment / contact:**
- **There is no record in the repository that an ASL-fluent reviewer has been recruited or contacted.** If contact
  happened outside the repository, it is not recorded here.
- No reviewer export (`labels/`) exists. **No manual ASL verification has been done.**
- Every ASL-linguistic category is still an unverified weak label: fingerspelling, number signs, name signs,
  non-manual negation and question marking, use of space.

## e. Inspection sheet: COMPLETED

Committed and pushed: `5775f276` (sheet) and `c94e9c4c` (rebuild dependencies).
Folder: <https://github.com/super-inbox/visual-search-adhoc/tree/baobao/visual-production-research-2026-10-05/docs/daily_report/10.18/asl-review-inspection-sheet>

**Contents:** 45 clips, one row each, with:
- video id and path;
- ground truth;
- production output and Uni-Sign output, with chrF scores and automatic error types;
- an initial error category with evidence;
- blank reviewer fields.

Deliverables: `inspection_sheet.csv`, `inspection_sheet.html` (offline review page), `README.md` and a deterministic
builder.

**Categories:** fingerspelling, names, numbers, negation, questions, spatial relations, general semantic.

| Initial category (automatic) | Clips |
|---|---|
| General semantic | 13 |
| Negation | 8 (5 lost, 3 inserted by an output) |
| Numbers | 7 (6 lost, 1 inserted) |
| Names | 6 |
| Questions | 5 |
| Fingerspelling | 3 |
| Spatial relations | 3 |

**21 highlighted examples:** 3 per category, where the ground truth, prod output and Uni-Sign output all differ.

**Weak vs human labels:**
- Every category is an **automatic weak label** (`automatic_weak` / `candidate_unverified`), derived from English
  text only. It does not say what was signed.
- Spatial relations uses a new, weakest text proxy.
- A label counts as **human-verified** only when a reviewer sets it; the export then writes `human_verified`.
- All reviewer fields are blank; `review_status = not_started` on all 45 rows.

**Production column caveat:**
- `prod_output` is **B_ours_5p39 (= P0-18 `A_old`)**, the historical our-pipeline baseline.
- It is a **provisional stand-in**, **not verified as the current live production system**.
- It will be replaced if the actual production output is identified.

**Workflow:**
1. An ASL-fluent reviewer opens the page and enters their name and ASL background.
2. They watch each clip before reading the automatic evidence.
3. They tick the verified categories, comment with timestamps, set the status, and export.
4. Ideally a second reviewer works independently.

---

## Status

| Task | Status | Completed | Remaining |
|---|---|---|---|
| a. Timing / crop diagnosis | **Completed** | P0-12 formal result (≈ 86 % of the gap from input preparation); 128-clip factorial: timing +3.15, crop +0.69 (n.s.) | Final timing-vs-crop split from the P0-18 full-test run and H18 |
| b. Representation / fusion | **Exploratory / partial**; final fusion remains P0-19 | P0-14 PARTIAL SUPPORT (exploratory, gate inconsistency documented); P0-15 NOT SUPPORTED | P0-19 not started: pre-register design and exit criteria, new reliability signal, one-shot on H19 |
| c. Automatic preprocessing (P0-18) | **IN PROGRESS**; 128-clip development comparison now available | GPU poses 184/184 + oracle arm 128/128; timing IoU 0.350 vs 0.335; crop IoU 0.868 vs 0.301; 128-clip comparison: Automatic +1.53 BLEU-4 / +3.14 chrF over Old (≈ 42 % / 54 % of the oracle gap), WER +5.4 | Full-test 6-arm decode, freeze and H18 dry run **still pending**; also Mac-vs-T4 decode equivalence, determinism gates, plan + thresholds, H18 one-shot (with approval) |
| d. ASL-fluent reviewer | **Recruitment not yet completed** (no contact recorded) | Review package, instructions, inspection sheet | Recruit / contact a reviewer; run the review; merge verified labels |
| e. Inspection sheet | **Completed and pushed**; human ASL verification still pending | 45 clips, 21 examples, 7 categories, blank reviewer fields | ASL-fluent review; replace `prod_output` if the live production output is identified |

## Next Update

The 128-clip development comparison is now included (task c, §6). The next update of this report will include:

1. **Mac-vs-T4 decode equivalence:** whether the two decode environments give the same predictions.
2. **Full-test 6-arm Old vs Automatic comparison** (2,347 clips; A_old, B_auto, B_time_only, B_crop_only, O_time,
   O_time_crop).
3. **Tighter confidence intervals** from the full test set (about 18× the clips of the 128 set, bootstrap over source
   videos).
4. **Final timing-vs-crop contribution** for the automatic pipeline, including whether the WER trade-off holds.
5. **Freeze status:** the P0-18 `EXPERIMENT_PLAN.md` thresholds (P1–P5), the determinism gates, the plan-code verdict
   test and `FREEZE.json`.
6. **H18 dry-run status** on development videos. H18 itself stays sealed until its approved one-shot run.
7. **The final P0-18 development verdict.**

## Sources

- P0-12: `10.13/asl-p0-12-full128-fp16/P0_12_RESULTS.md`; summaries `10.15/UNISIGN_FAILURE_ANALYSIS_SUMMARY.md` and
  `10.16/UNISIGN_P0_MANAGER_SUMMARY.md`.
- P0-14: `10.15/asl-unisign-representation-probe/FULL_RUN_REPORT.md`. P0-15:
  `10.16/asl-unisign-high-precision-fusion/P0_15_RESULTS.md`.
- P0-16: `10.16/asl-p0-16-experimental-credibility/` (`EXPERIMENT_PROTOCOL.md`, `SANITY_GATE_POLICY.md`,
  `HOLDOUT_PLAN.md`).
- P0-18: scripts in `10.16/asl-p0-18-auto-preprocessing/scripts/` (untracked). Local outputs in
  `~/Desktop/curify/p018-work/dev/` (not in git): `score128.json`; `gpu_run/` (`poses/SUMMARY.json`,
  `official_SUMMARY.json`, env records); `tune_gpu/` (`TIMING_DETECTOR_NOTE.md`, `interval_params.json`,
  `crop_tuning_gpu.json`); `cond_gpu/` (`build_meta.json`, `run_decode.log`); `score_gpu/score128.json` (128-clip
  Old vs Automatic vs Oracle).
- Review: `10.13/asl-unisign-error-taxonomy/manual_review/`; `10.18/asl-review-inspection-sheet/`.
