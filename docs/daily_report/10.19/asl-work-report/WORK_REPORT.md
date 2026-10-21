# ASL / Uni-Sign Work Report: tasks a–e

**Date:** 2026-10-19 (updated with the final P0-18 development result; model case review and P0-19 Stage 0 status added 2026-10-20) · **Branch:** `baobao/visual-production-research-2026-10-05`
**System under study:** the public Uni-Sign pose-only How2Sign checkpoint. No model was trained or modified.

This report only summarises existing files. It does not change any recorded verdict. Every result in the Uni-Sign
line so far is **exploratory or validation-level, not confirmatory** (P0-16). The first confirmatory evaluation was
planned as P0-18 on the sealed holdout H18. P0-18 stopped at development (NOT SUPPORTED), so H18 is still sealed
and no confirmatory evaluation has been run.

## Executive summary

- **a. Timing / crop diagnosis: done.** All conditions use the **same public Uni-Sign checkpoint**; only the input
  preparation differs. Our **old pipeline** used the **original How2Sign speech timestamps + full frame + our pose
  extractor**. It did **not** use the re-aligned signing timing or the official signer crop. **"Official
  preprocessing"** means the How2Sign / Uni-Sign experimental inputs: clips cut at the **re-aligned signing timing**
  and the **official signer-crop videos** (dataset-author inputs, not a new model and not preprocessing we invented).
  P0-12 showed that our old low score came mostly from this **input preparation**, not from our pose extractor: feeding
  the official timing + crop to our extractor recovered **≈ 86 % of the BLEU-4 gap** (5.47 → 8.61 vs 9.13). This used
  the official (oracle) inputs **as a diagnosis; it was not an automatic fix**. Most of the gain is **timing** (+3.15
  BLEU-4 on the 128 clips; +7.4 on the full test set in P0-18); the crop effect is small.
- **b. Representation / fusion: P0-14 and P0-15 done; P0-19 Stage 0 prepared and frozen; GPU feasibility run
  pending.** P0-14: **PARTIAL SUPPORT**, read as exploratory evidence because of a documented sanity-gate
  inconsistency. Uni-Sign's mT5 encoder states carry concept information the translation sometimes drops. P0-15:
  **NOT SUPPORTED**; a verifier could not make safe additions. **No translation improvement has been shown.**
  - **P0-19** (the final representation/fusion follow-up) tests whether mT5 evidence can safely improve the output by
    **confidence-gated reranking of Uni-Sign's own top-k hypotheses**, with abstention. It is **not** a lexical union
    and never appends concepts to the translation. Uni-Sign is not retrained.
  - **Stage 0** (headroom check: are the top-k candidates diverse and good enough for reranking to matter?) is
    designed, implemented locally, frozen and smoke-tested. **It has not been run on the 2,209 clips.** The run
    (≈ 1.3–2 h on one T4, decoding only) is postponed because the GPU VM was just stopped; no GPU job is running.
  - **P0-19 is not complete and fusion is not supported.** H18 and H19 remain sealed.
- **c. Automatic preprocessing (P0-18): Development completed — NOT SUPPORTED; H18 remains sealed for a stronger
  candidate.**
  - Final candidate: original timing + automatic signer crop. On the full test set (2,347 clips) it gives
    **BLEU-4 +0.39 [0.17, 0.62]**, **chrF +0.48 [0.24, 0.73]**, **WER −0.14 [−1.30, +1.01]**, length ratio 0.903 vs
    0.900.
  - It recovers **about 5 %** of the Old→Oracle BLEU gap on full test (**27 %** on the reused 128-clip subset).
  - Criteria: **P1 fail, P2 fail, P3 pass, P4 pass, P5 pass → NOT SUPPORTED.** The earlier automatic-timing candidate
    (+0.92 BLEU-4) failed P5 because it raised WER by about 9 points.
  - **The automatic crop gives a clean but small gain; pose-only timing is the main unresolved bottleneck** (correct
    timing alone is worth +7.4 BLEU-4).
  - **H18 and H19 remain sealed.** Next: a stronger timing/alignment method, e.g. a learned segmenter or
    transcript/sign alignment.
- **d. ASL-fluent reviewer: materials prepared; no recruitment recorded.** The review package and instructions exist.
  The repository has **no record that a reviewer was recruited or contacted**, and no manual ASL label exists.
- **e. Inspection sheet: done; review package and repetition audit committed and pushed (`a9d00552`).** 45 clips, 21 highlighted
  examples, 7 categories. The **45 diagnostic videos** now ship with the sheet as a reproducible review package
  (sha256-verified, 60,239,549 bytes, kept out of git; GitHub Release asset `asl-review-package-2026-10-19`, see e.
  below; How2Sign CC BY-NC 4.0); the page plays each clip next to the ground truth, our/old output and
  official output. All labels are automatic weak labels; every reviewer field is blank. The "production" column is a
  provisional stand-in.
  - **Model case review: complete (two model passes; unverified).** A Claude first pass and an independent Codex blind
    second pass each covered all 45 clips (`10.19/asl-model-case-analysis/`, see **Model case review** below).
    Claude vs Codex coding agreement: **4 full / 28 partial / 13 disagreements**; primary categories match on
    **21 / 45**. These are model-review consistency numbers, **not ASL accuracy**. Official-output analysis is
    text-only for all 45 clips. **Neither model review is human ASL verification; ASL-fluent review remains pending.**
  - **Repetition:** **official preprocessing does not eliminate repetition; repetition is not purely a long-input
    failure.** The official output loops on **9 of the 45** clips, with official input lengths of 4.0–32.5 s (1 short,
    3 medium, 5 long). Over the 128-clip benchmark the official loop rate rises with input length (7 % short, 12 %
    medium, 27 % long) but is not zero on short clips. Input length / preparation may raise the risk; the Uni-Sign
    decoder / generation also has an intrinsic repetition failure mode.

---

## a. Timing / crop diagnosis (P0-12): COMPLETED

**What was done.** The Uni-Sign checkpoint, the 128 benchmark clips, the references and the evaluation code were held
fixed. Only the pose source and the input preparation were changed: timing, crop and coordinate normalisation.
- **Old pipeline (`B_ours_5p39`):** original How2Sign **speech** timestamps, **full frame**, **our pose extractor**,
  the same Uni-Sign checkpoint. It did not use the re-aligned signing timing or the official signer crop.
- **Official preprocessing (`A_official`, `C_ours_on_official_crop`):** the How2Sign / Uni-Sign experimental inputs,
  i.e. clips cut at the **re-aligned signing timing** and the **official signer-crop videos** (with the official poses,
  or with our extractor run on those videos). These are dataset-author inputs, not a new model and not something we
  built. The
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
- The P0-18 full-test development run (task c, 2,347 clips, GPU poses) confirms this:
  - oracle timing alone: +7.43 BLEU-4 [+6.18, +8.68] (O_time − A_old);
  - automatic crop on top of oracle timing: +0.87 [+0.53, +1.23] (O_time_crop − O_time);
  - automatic crop at the original timing: +0.39 [+0.17, +0.62] (B_crop_only − A_old).

  H18 was not opened (P0-18 stopped at development), so there is no confirmatory split.

## b. Representation / fusion (P0-14, P0-15 completed; P0-19 Stage 0 prepared and frozen, GPU run pending)

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

**P0-19: safe fusion by gated reranking. Status: P0-19 Stage 0 prepared and frozen; GPU feasibility run pending.**
Plan: `10.20/asl-p0-19-safe-rerank/EXPERIMENT_PLAN.md` (local, not committed).

- **Design.** Uni-Sign generates top-k hypotheses. A reranker may pick a different one using decoder confidence plus
  agreement with the mT5 probe, with a repetition filter, and replaces Uni-Sign's top-1 **only above a frozen
  margin; otherwise it abstains**. The auxiliary representation only **selects among Uni-Sign's own hypotheses**; it
  never generates or appends words (the P0-15 failure mode). **No model is retrained.**
- **Stage 0 (headroom check)** asks whether the top-k candidates contain enough useful diversity for any reranker to
  matter. Official poses, the 2,209 test_clean clips, k = 4 and k = 8. **Frozen GO criteria** (all three, for k = 4
  or for k = 8):
  1. ≥ 10 % of clips have at least one candidate whose (Tier L) concept set differs from the top-1's;
  2. ≥ 50 of the 498 reference concepts missed by the top-1 appear in some top-k candidate;
  3. oracle-best-in-k corpus chrF ≥ top-1 chrF + 3.0.

  **If any criterion fails:** P0-19 stops at Stage 0, verdict **development NOT SUPPORTED**, H19 stays sealed.
  **If Stage 0 passes:** Stage 1 compares decoder-only vs representation-aware gated reranking on development data
  (in the H19 input domain: official crops + our extractor), with its own approval and freeze. H19 is still not opened
  during development.
- **Sanity gates** (any failure → VOID): baseline reproduction (4-beam top-1 = stored Uni-Sign output on all clips),
  determinism (independent 40-clip repeat), no holdout access (P0-16 guard + file tripwire; the val CSV is never
  read), input integrity, and concept-label reproduction (exactly 498 missed concepts).
- **Done:**
  - experiment plan written;
  - Stage 0 config, thresholds and k = 4 / 8 frozen (`STAGE0_FREEZE.json`);
  - baseline reproduction, determinism, holdout guard and verdict logic implemented;
  - verdict test passes all 2,048 gate/criterion combinations;
  - 5-clip Mac CPU smoke test passes all gates and reproduces the baseline outputs 5/5.
- **Not done:** Stage 0 has **not** been run on the 2,209 clips. It needs ≈ 1.3–2 h on one T4 (decoding only, no
  training). The run is intentionally postponed because the GPU VM was just stopped (it is stopped now, and no GPU job
  is running). It can be run directly from the frozen setup when a GPU is available again.
- **Protocol.** H18 cannot be used for P0-19 development: P0-16 allows that only after P0-18's one-shot run on H18,
  which never happened. H19 is P0-19's one-shot evaluation and remains sealed. NOT SUPPORTED or VOID on H19 would close
  the fusion line. P0-18 is NOT SUPPORTED, so P0-19's holdout input pipeline is official crops + our extractor.

## c. Automatic preprocessing (P0-18): DEVELOPMENT COMPLETED — NOT SUPPORTED

> **Development completed — NOT SUPPORTED; H18 remains sealed for a stronger candidate.**
> Final candidate (revision 2): **original timing + automatic signer crop** (`B_crop_only`). P0-18 stops at the
> development result; the H18 one-shot run was **not** opened. Full write-up:
> `10.16/asl-p0-18-auto-preprocessing/` (`P0_18_MANAGER_SUMMARY.md`, `DEVELOPMENT_RESULTS.md`, `EXPERIMENT_PLAN.md`,
> `FREEZE.json`).

**Goal:** replace the oracle timing + crop with an automatic method that uses only video frames and the original
timestamps (production-legal), and measure it against Old (original window, full frame) and Oracle (re-aligned
window; automatic or official crop). Development used How2Sign **test** only.

**Final result: full TEST, 2,347 evaluable clips** (canonical T4 GPU pose + decoder environment; paired bootstrap over
source videos, B = 2,000):

| Arm | Timing | Crop | BLEU-4 | chrF | WER | Length ratio |
|---|---|---|---|---|---|---|
| Old (`A_old`) | original | full frame | 4.85 | 22.08 | 101.1 | 0.900 |
| **Final candidate: crop-only (`B_crop_only`)** | original | automatic | **5.24** | **22.56** | **100.9** | **0.903** |
| Revision-1 candidate (`B_auto`, dropped) | automatic (widened) | automatic | 5.77 | 24.71 | 109.7 | 1.079 |
| Oracle timing + automatic crop (`O_time_crop`) | re-aligned | automatic | 13.15 | 32.97 | 87.2 | 0.951 |

Crop-only vs Old:
- **BLEU-4 +0.39 [+0.17, +0.62]**
- **chrF +0.48 [+0.24, +0.73]**
- **WER −0.14 [−1.30, +1.01]**
- **length ratio 0.903 vs 0.900** (no lengthening)
- Old→Oracle BLEU-4 gap recovered: **about 5 % on full TEST** (0.39 of 8.30); **27 % on the reused 128-clip subset**
  with official crops (0.98 of 3.67).

**Pre-registered criteria** (thresholds frozen before the revision and not changed):

| Criterion | Requirement | Crop-only | Status |
|---|---|---|---|
| P1 improvement | Δ BLEU-4 ≥ +0.5 and CI lower bound > 0 | +0.39 (CI > 0) | **FAIL** |
| P2 gap recovery | ≥ 33 % of the Old→official-oracle gap | 27 % (128 subset) | **FAIL** |
| P3 reliability | failure rate ≤ 5 % | 0.34 % | PASS |
| P4 cost | ≤ 15 s preprocessing per clip | 7.1 s (one T4) | PASS |
| P5 do no harm | length 0.8–1.2×; Δ WER CI upper ≤ +5 | 0.903; +1.01 | PASS |

**Final development verdict: NOT SUPPORTED.** The revision-1 candidate (automatic widened timing + crop) was also NOT
SUPPORTED: +0.92 BLEU-4 [+0.49, +1.37] but WER +8.6 [+6.8, +10.5] (fails P5), because the wider window lengthens the
output (0.90 → 1.08).

**What was learned:**
- **The automatic crop gives a clean but small gain.** BLEU-4 and chrF rise with no WER or length cost. It agrees with
  the official crop at box IoU 0.868 (full frame 0.301) and is close to it in translation (+0.47 BLEU-4 for the
  official crop at oracle timing, CI includes 0).
- **Pose-only timing is the main unresolved bottleneck.** Correct (re-aligned) timing alone is worth +7.4 BLEU-4 on
  full TEST. The pose-only detector barely improves timing agreement (interval IoU 0.350 vs 0.335 for the original
  timestamps); estimating the per-video drift from pose activity fails because signers are active 92–99 % of the time.
- Full-TEST timing-vs-crop split (automatic): timing only +0.55 BLEU-4 with WER +9.7; crop only +0.39 with WER −0.1;
  both +0.92.

**Engineering and integrity:**
- Canonical GPU environment (T4) for pose extraction and decoding: 184/184 test videos (521,219 frames, 31.3 fps),
  oracle crop arm 128/128, 0 failures. Pose extraction is deterministic on the reference video (identical arrays in
  every run, including the dry runs). The T4 decoder reproduces the Mac CPU decoder exactly (128/128 identical predictions).
- Gates passed on development: G1 environment reproduction (24/24 decodes, pose arrays identical), G2 decode
  determinism (16/16), G3 integrity. Plan-code verdict test: 256/256 combinations.
- `FREEZE.json` (sha256 `3bcbf271…`, 59 files) freezes the algorithm, thresholds, verdict logic, environments and code.
  The H18 runner was dry-run end to end on test data with the final candidate (all gates PASS); an earlier dry run
  found and fixed a bug that would have stopped the H18 run.
- **H18 and H19 remain sealed.** No H18/H19 frame, reference, timing row or output was opened. (The H18 unit list,
  VIDEO_IDs only, was read once to confirm all units are single videos; nothing was printed.)

**Future direction:** a stronger candidate needs a better timing / alignment method — for example a learned
sign/no-sign segmenter, or alignment between the transcript and the signing. H18 is kept sealed for that candidate;
the frozen runner and environments can be reused.

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

Committed and pushed: `5775f276` (sheet) and `c94e9c4c` (rebuild dependencies). Inspection-sheet update, review
package builder, video manifest and repetition audit: committed and pushed in
`a9d005522aa957f7ea82ba0eae0252ffed519c4a`. The videos and the zip are not in git; the zip is a GitHub Release asset
(see **Videos** below).
Folder: <https://github.com/super-inbox/visual-search-adhoc/tree/baobao/visual-production-research-2026-10-05/docs/daily_report/10.18/asl-review-inspection-sheet>

**Contents:** 45 clips, one row each, with:
- video id and path;
- ground truth;
- our/old output (`B_ours_5p39`: speech timestamps, full frame, our extractor) and official output (`A_official`:
  re-aligned signing timing + official signer-crop inputs), both from the same Uni-Sign checkpoint, with chrF scores
  and automatic error types;
- an initial error category with evidence;
- blank reviewer fields.

Deliverables: `inspection_sheet.csv`, `inspection_sheet.html` (offline review page), `README.md` and a deterministic
builder.

**Videos (review package):**
- The 45 diagnostic clips are How2Sign test clips, so they are **not committed**. `scripts/build_review_package.py`
  copies them from the local How2Sign v2 directory after checking each against the committed How2Sign v2 manifest sha256, into
  `videos/<clip_id>.mp4` next to the page (git-ignored), and writes `videos_manifest.csv` (sha256, size, duration,
  source; committed).
- `--zip` writes a self-contained, deterministic package (page, CSV, README, repetition audit, manifest, `SHA256SUMS`,
  videos): `~/Desktop/curify/asl-review-package/asl_inspection_review_package.zip`.
- **GitHub Release asset (private repo, not in git history):**
  - Release: <https://github.com/super-inbox/visual-search-adhoc/releases/tag/asl-review-package-2026-10-19>
  - Direct download:
    <https://github.com/super-inbox/visual-search-adhoc/releases/download/asl-review-package-2026-10-19/asl_inspection_review_package.zip>
  - Tag on `a9d00552`. Size **60,239,549 bytes**, SHA-256
    `b1728e39b8d139a9160bcfc813c240521f3865668700195ef76846652deea02a` (uploaded asset re-downloaded and verified).
  - **The release asset is the reference copy.** The package README was edited after the zip was built, so
    rebuilding with `--zip` now gives a different checksum.
- The videos are **How2Sign data, licensed CC BY-NC 4.0** (non-commercial, attribution required); share the package
  only within those terms.
- The page plays `videos/<clip_id>.mp4` first, then the repo path, and otherwise asks for **Load videos…**. Reviewer
  flow: open page → play video → compare ground truth / our/old output / official output → tick the verified category.

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

**21 highlighted examples:** 3 per category, where the ground truth, our/old output and official output all differ.

**Repetition audit** (`repetition_audit.md` / `.csv`, committed 10.13 taxonomy rule, English text only):

> **Official preprocessing does not eliminate repetition; repetition is not purely a long-input failure.**

- The official output (`A_official`) is a repetition loop on **9 of the 45** clips; the our/old output on 10; both on 5.
- Official input length of the 9 (re-aligned window): **4.0–32.5 s, median 16.4 s**; 1 short (≤ 5 s), 3 medium,
  5 long (> 10.67 s, Uni-Sign's 256-frame cap).
- Whole 128-clip benchmark, official arm: loops on 3 / 45 short (7 %), 6 / 50 medium (12 %), 9 / 33 long (27 %) clips.
- Conclusion: input length / preparation may raise the risk of a loop, but the Uni-Sign decoder / generation itself also
  has an intrinsic repetition failure mode that appears on short, officially prepared clips too. Earlier reports
  describing repetition as a long-clip problem (8.31, 10.09) describe a correlation, not the whole cause. Nothing here
  says what was signed.

**Model case review** (`10.19/asl-model-case-analysis/`; `model_review` / `codex_review`, all rows unverified):

- **Claude first pass: complete** (45 / 45 cases): `model_case_analysis.csv`, `MODEL_CASE_ANALYSIS.md`,
  `model_case_analysis.html`.
- **Independent Codex blind second pass: complete.** Codex reviewed **all 45 cases / 80 contact sheets** under
  `CODEX_REVIEW_PROMPT.md`: `codex_case_analysis.csv`, `CODEX_CASE_ANALYSIS.md`. Codex overall confidence:
  **34 medium, 11 low, 0 high**.
- **No matching official visual-input windows were established**, so the official-output analysis is **text-only for
  all 45 cases** in both passes.
- **Claude vs Codex coding agreement** (`MODEL_REVIEW_COMPARISON.md`, all 45 cases): **4 full / 28 partial /
  13 disagreements**; primary categories match in **21 / 45**. These are **model-review consistency numbers, not ASL
  accuracy**; the 13 disagreements are mostly category specificity / priority differences, not 13 proven mistakes.
- **Repetition:**
  - The **frozen automatic official repetition count remains 9**; the repetition audit is unchanged.
  - Codex independently identified **11** official English-repetition cases (Claude's row text notes the same 11).
    The two extras are **R01 and R19**.
  - R01 and R19 exceed the output repetition threshold (rep3 ratio 0.875 and 0.152 vs 0.15), but the frozen rule
    excludes them because **their references also contain repeated trigrams**. They stay `hallucination` in the frozen
    data. This is a definition difference (automatic selection vs model judgment), not a reason to change the audit.
- **Neither Claude nor Codex constitutes human ASL verification. ASL-fluent review remains pending.**

**Priority cases for human review:** R26, R29, R35, R10, R23, R38, R44, R36, R09, R15; then R22, R32, R40, R41.

**Protocol caveats:**
- **R03** had prior smoke-test exposure to its repetition-audit entry (and diagnostic notes), so it is not a pristine
  blinded case.
- The full Codex pass did **not reopen the prohibited prior-analysis files** (Claude first pass, repetition audit)
  until the blind review was complete.
- Contact sheets are **still-image approximations** (sampled frames); they cannot reliably establish motion-dependent
  ASL semantics or non-manual grammar.
- Historical diagnostic frames **cannot be treated as matching official-input visual evidence** when the timing windows
  differ (re-aligned official window vs original speech window).
- Contact sheets and videos are How2Sign-derived (CC BY-NC 4.0) and are kept out of git (`contact_sheets/` is
  git-ignored).

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
2. They play each clip (from the package) before reading the automatic evidence, and compare ground truth / our/old
   output / official output.
3. They tick the verified categories, comment with timestamps, set the status, and export.
4. Ideally a second reviewer works independently.

---

## Status

| Task | Status | Completed | Remaining |
|---|---|---|---|
| a. Timing / crop diagnosis | **Completed** | P0-12 formal result (≈ 86 % of the gap from input preparation); 128-clip factorial: timing +3.15, crop +0.69 (n.s.); P0-18 full test: oracle timing +7.43, auto crop +0.39 | None (no confirmatory split: H18 not opened) |
| b. Representation / fusion | **P0-19 Stage 0 prepared and frozen; GPU feasibility run pending** (P0-14/P0-15 exploratory / partial; P0-19 not complete; fusion not supported) | P0-14 PARTIAL SUPPORT (exploratory, gate inconsistency documented); P0-15 NOT SUPPORTED; P0-19 gated-reranking plan, Stage 0 config / thresholds / k = 4, 8 frozen, verdict test 2,048/2,048, 5-clip smoke test passes all gates (baseline 5/5) | Run Stage 0 on 2,209 clips (≈ 1.3–2 h, one T4); if GO → plan and freeze Stage 1 (decoder-only vs representation-aware gated reranking); if NO-GO → development NOT SUPPORTED; H19 one-shot only after a full freeze |
| c. Automatic preprocessing (P0-18) | **Development completed — NOT SUPPORTED; H18 remains sealed for a stronger candidate** | Final candidate crop-only on full test: BLEU-4 +0.39 [0.17, 0.62], chrF +0.48, WER −0.14, length 0.903 vs 0.900; ≈ 5 % of the Old→Oracle gap (27 % on the 128 subset); P1 fail, P2 fail, P3–P5 pass; T4 pose + decoder environment frozen (`FREEZE.json` `3bcbf271…`); H18 runner dry-run passed | Stronger timing/alignment method (learned segmenter or transcript/sign alignment), then a new candidate for the sealed H18 |
| d. ASL-fluent reviewer | **Recruitment not yet completed** (no contact recorded) | Review package, instructions, inspection sheet | Recruit / contact a reviewer; run the review; merge verified labels |
| e. Inspection sheet | **Completed**; review package builder + repetition audit committed and pushed (`a9d00552`); 45-video zip published as GitHub Release asset `asl-review-package-2026-10-19`; Claude first pass and Codex blind second pass complete (unverified model reviews); human ASL verification still pending | 45 clips, 21 examples, 7 categories, blank reviewer fields; 45 sha256-verified videos packaged (60,239,549 bytes, SHA-256 `b1728e39…a02a`, release asset, out of git history); repetition audit: official output loops on 9/45 (4.0–32.5 s; not only long clips; unchanged); model review: Claude vs Codex 4 full / 28 partial / 13 disagreements, primary match 21/45 (consistency, not accuracy); official-output analysis text-only for all 45 | ASL-fluent review, starting with priority cases R26, R29, R35, R10, R23, R38, R44, R36, R09, R15, then R22, R32, R40, R41; replace `prod_output` if the live production output is identified |

## Next Update

- **c. P0-18 is closed at development (NOT SUPPORTED).** H18 and H19 remain sealed. The next P0-18-line step is a
  stronger timing/alignment method (learned sign/no-sign segmenter or transcript/sign alignment), developed on test
  only and re-frozen before H18 is used.
- **b. P0-19: Stage 0 prepared and frozen; GPU feasibility run pending.** When a T4 is available again, run Stage 0
  from the frozen setup (≈ 1.3–2 h, decoding only). If any GO criterion fails, P0-19 stops at Stage 0 (development
  NOT SUPPORTED) and H19 stays sealed. If all pass, plan and freeze Stage 1 for separate approval. H18 is not available
  to P0-19. P0-18 is NOT SUPPORTED, so per P0-16 (HOLDOUT_PLAN §6) P0-19's holdout input pipeline is official crops +
  our extractor.
- **d.** Reviewer recruitment / contact still to be recorded.
- **e.** Both model passes are done; the next step is ASL-fluent human review of the 14 priority cases, then the rest.

## Sources

- P0-12: `10.13/asl-p0-12-full128-fp16/P0_12_RESULTS.md`; summaries `10.15/UNISIGN_FAILURE_ANALYSIS_SUMMARY.md` and
  `10.16/UNISIGN_P0_MANAGER_SUMMARY.md`.
- P0-14: `10.15/asl-unisign-representation-probe/FULL_RUN_REPORT.md`. P0-15:
  `10.16/asl-unisign-high-precision-fusion/P0_15_RESULTS.md`.
- P0-19 (local, not yet committed): `10.20/asl-p0-19-safe-rerank/` (`EXPERIMENT_PLAN.md`,
  `config/stage0_config.json`, `STAGE0_FREEZE.json`, `scripts/`).
- P0-16: `10.16/asl-p0-16-experimental-credibility/` (`EXPERIMENT_PROTOCOL.md`, `SANITY_GATE_POLICY.md`,
  `HOLDOUT_PLAN.md`).
- P0-18: `10.16/asl-p0-18-auto-preprocessing/` (`P0_18_MANAGER_SUMMARY.md`, `DEVELOPMENT_RESULTS.md`,
  `EXPERIMENT_PLAN.md`, `FREEZE.json`, `config/`, `ref/g1/`, `scripts/`). Local outputs in
  `~/Desktop/curify/p018-work/` (not in git): `dev/gpu_run/` (T4 poses, oracle arm, env records); `dev/tune_gpu/`
  (`TIMING_DETECTOR_NOTE.md`, interval + crop tuning); `dev/cond_gpu/` (all arms); `dev/dec_t4/` (T4 predictions,
  `decoder_env.json`, G1/G2 checks); `dev/score_t4/final_crop/DEV_COMPARISON.json` (final comparison and criteria);
  `dryrun3/RESULT.json` (final H18 dry run). Mac-CPU outputs (`dev/vid_all/`, `dev/dec_gpu/`, `dev/score_gpu/`) are
  cross-checks only.
- Review: `10.13/asl-unisign-error-taxonomy/manual_review/`; `10.18/asl-review-inspection-sheet/`.
- Model case review: `10.19/asl-model-case-analysis/` (`MODEL_CASE_ANALYSIS.md`, `CODEX_CASE_ANALYSIS.md`,
  `MODEL_REVIEW_COMPARISON.md`, CSVs, `scripts/`; contact sheets local only).
