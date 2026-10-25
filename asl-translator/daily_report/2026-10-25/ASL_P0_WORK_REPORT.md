# ASL P0 Follow-up Work Report

**Scope:** the three low-cost P0 follow-ups from the
[2026-10-21 case review and P0 plan](../2026-10-21/UNISIGN_CASE_REVIEW_AND_P0_PLAN.md), plus the ASL reviewer package
built to unblock them. Covers the work committed from 2026-10-23 to 2026-10-24. No new experiment was run to write this
report.

**Protocol:** [P0_PROTOCOL_FREEZE.md](../2026-10-23/P0_PROTOCOL_FREEZE.md), frozen 2026-10-23 before any decode
(commit `c644bc3d`) and not modified since. All 45 cases are P0-16 `exploratory` test_clean clips. Every result here
is **diagnostic/development evidence**, not a confirmatory or population-level claim.

## 1. Executive Summary

The 2026-10-21 plan named three low-cost directions for the Uni-Sign failure cases:

- **P0-A:** is a better sentence already in Uni-Sign's beam candidates, so that reranking could recover it?
- **P0-B:** does hand RGB video carry fingerspelled letters (proper names) that the pose path loses?
- **P0-C:** does a human-corrected input window or framing recover meaning on a few specific cases?

**Completed:**
- **P0-A** ran to its first frozen gate and **stopped**. The reference-based oracle over the candidate pool raises
  corpus chrF by only +2.24 (official preprocessing, the deciding domain) and +2.26 (old preprocessing). The frozen bar
  is +3.0.
- **P0-B** finished its technical feasibility survey. Existing recognizers with public ASL weights exist, but none has
  been run. Whether R02/R05/R35 contain fingerspelling at all is not yet established.
- **P0-C** finished raw-video source checks for R26 and R29:
  - R26's failure is not explained by a crop.
  - R29's target window is mostly rest, and its timing metadata looks un-realigned.
  - No correction has been defined and nothing has been decoded.
- **Reviewer package:** a blind two-step ASL reviewer package (8 clips) is built, checksummed and reproducible.

**Remaining blocker:** P0-B and P0-C now both wait on **an ASL-fluent human reviewer**, not on compute.

| Item | Status | Basis |
|---|---|---|
| **P0-A** candidate headroom / reranking | **COMPLETE / STOP** — *P0-A STOP / NOT ENOUGH CANDIDATE HEADROOM* | Oracle Δ corpus chrF +2.24 / +2.26 < frozen +3.0 |
| **P0-B** fingerspelling / proper names | **TECHNICAL FEASIBILITY COMPLETE / REVIEWER BLOCKED** | Recognizer survey done; spans unconfirmed; nothing run |
| **P0-C** input correction | **SOURCE DIAGNOSTICS COMPLETE (R26, R29) / REVIEWER BLOCKED** | No correction defined; no corrected decode. R10 and R35 blocked separately |
| **ASL reviewer package** | **BUILT, NOT YET SENT** | 8 blind clips; Step 1 / Step 2; blank labels |

## 2. P0-A — Candidate Headroom / Reranking

**Question:** is a better sentence already among Uni-Sign's beam candidates but not chosen as top-1, so that a
reference-free reranker (simple, then with the P0-14 mT5 probe) could pick it?

### 2.1 Frozen setup

| Item | Value |
|---|---|
| Cases | 45 (R01–R45, the inspection-sheet set): 6 focus + 1 named control (R41) + 6 hash-selected ordinary controls (13 human-review cases) + 32 decode-only |
| Domains | **A_official** (official poses, realigned timing, official crop; deciding) and **B_ours_5p39** (our extractor, original timing, full frame). Inputs are the P0-12 prepared pose PKLs, 45/45 sha256-verified per domain |
| Model | Uni-Sign `eed438bc`; checkpoint `how2sign_pose_only_slt.pth` (sha256 `1bfd5f33…`); mT5-base snapshot `2eb15465` |
| Compute | Local CPU, fp32, batch 1, seed 42. Clips over 256 frames use the per-clip seed `sha256(clip_id)` |
| Control T | Deterministic CPU top-1, `num_beams=4`. On A_official, T equals the stored P0-14 CPU fp32 control on 45/45. The historical T4/fp16 inspection-sheet text is descriptive only |
| Candidate pool | T + the 5 sequences of `num_beams=5`, exact-text dedup, ≤ 5 unique. Built without references |
| Pool size | A_official 5 on 45/45. B_ours_5p39 5 on 44/45 (R42 = 4) |
| Go/no-go (frozen §1.7 rule 1) | (a) oracle − T corpus chrF ≥ **+3.0**, **and** (b) a better pool candidate in ≥ 3 of 13 human-reviewed cases |

### 2.2 Reproducibility and runtime

- An independent second decode matched the canonical run **on 45/45 clips in each domain**:
  - pool order, token ids and texts;
  - frame indices and model-input hashes;
  - max |Δ sequence score| = 0.0.
  - Gate G3 passed ([DETERMINISM.json](../2026-10-23/p0a-candidate-rerank/runs/full45/DETERMINISM.json)).
- Canonical decode time: 260.7 s (A_official) and 259.2 s (B_ours_5p39). Total wall clock for both domains, both
  runs: **22.3 min** on local CPU. Cloud spend $0.

### 2.3 Results (automatic metrics; oracle = reference-chosen upper bound)

The **oracle** picks, per clip, the pool candidate with the highest sentence chrF **against the reference**. It is an
**upper bound** on any reranker over this pool. It is **not a deployable system** and is not reported as one.

| Metric (45 clips) | Official prep. T | Official prep. oracle | Δ | Old prep. T | Old prep. oracle | Δ |
|---|---|---|---|---|---|---|
| corpus chrF | 23.76 | 26.00 | **+2.24** | 18.22 | 20.48 | **+2.26** |
| corpus BLEU-4 (13a) | 5.72 | 7.05 | +1.33 | 1.70 | 2.48 | +0.79 |
| WER (×100) | 95.44 | 93.88 | −1.55 | 99.81 | 96.50 | −3.30 |
| mean length ratio | 1.000 | 1.037 | +0.04 | 1.022 | 0.948 | −0.07 |
| `loop_out` count | 9 | 9 | 0 | 11 | 10 | −1 |

Official prep. = A_official; old prep. = B_ours_5p39. Source:
[RESULTS.md](../2026-10-23/p0a-candidate-rerank/RESULTS.md),
[headroom_summary.json](../2026-10-23/p0a-candidate-rerank/headroom/headroom_summary.json).

**Candidate diversity:**
- The pools are diverse in wording. Some candidate beats T on sentence chrF in 36/45 (official) and 34/45 (old) cases.
- The gains are small: median per-case Δ is +1.38 / +1.54.
- They are mostly rewordings, not recovered content.

**Repetition loops:**
- A looping top-1 rarely has a non-looping alternative in the pool:
  - 1 of 9 on official preprocessing (R23);
  - 3 of 11 on old preprocessing (R15, R10, R16).
- Where one exists, automatic inspection does not show a meaning recovery.
- Less repetition alone is not counted as success (protocol §0).

### 2.4 Decision

The official-preprocessing oracle gain (+2.24) is below the frozen +3.0, so rule 1(a) fails. The old-preprocessing
domain fails the same rule (+2.26).

**P0-A STOP / NOT ENOUGH CANDIDATE HEADROOM.**

Consequences:
- **Not pursued:** the simple rerank (R1), mT5-probe fusion (R2), reranker training and any GPU follow-up.
- **Human review:** the blinded 26-row candidate sheet
  ([candidate_review.csv](../2026-10-23/p0a-candidate-rerank/candidate_review.csv)) is optional diagnostic evidence
  and cannot change the verdict.

**Reading:** this is a **useful negative result**. Even with the reference choosing, a 5-candidate pool cannot lift
corpus chrF by the frozen amount, and any reference-free reranker can only do worse. The failures are mostly not
"right sentence ranked second", so selection-side fixes on this pool are closed.

## 3. P0-B — Fingerspelling / Proper-name Feasibility

**Cases:** R02, R05 and R35. Their references contain person names, which Uni-Sign replaces with other names.
**Source of truth:** [FEASIBILITY.md](../2026-10-23/p0b-fingerspelling-feasibility/FEASIBILITY.md).

**Why a reviewer comes first:** a recognizer is only meaningful on confirmed fingerspelled spans. Nobody has verified
that the names are fingerspelled, that they are in the windows the model saw, or that the frames are readable. For R35
the two preprocessing windows do not overlap (IoU 0.00). Claude does not infer spans. `interval_labels.csv` is blank.

**Recognizer survey (desk research only):** 8 entries were assessed. The shortlist:

| Rank | System | Weights | Licence | Input | Notes |
|---|---|---|---|---|---|
| 1 | **OpenFS** (CVPR 2026) | Public (ChicagoFSWild, ChicagoFSWild+, FSboard checkpoints) | Non-commercial research only | MediaPipe Holistic hand pose | Best fit for a research diagnostic |
| 2 | **HandReader**, keypoint variant | Public (ChicagoFSWild / +) | Code Apache-2.0; weights licence unstated | MediaPipe keypoints | Paper reports a CPU timing of 3.9 ms per sample |
| 3 | Fingerspelling PoseNet | Public | **No licence file** | MediaPipe pose | Only if the authors grant a licence |

Not suitable:
- the Kaggle 2023 1st place solution: no weights;
- the FSboard ByT5 baseline: no weights;
- Shi et al. 2019: no weights, obsolete stack;
- static single-letter classifiers: not continuous;
- fingerspelling detectors: no usable weights.

**Input mismatch:** our stored P0-12 poses are **RTMPose COCO-WholeBody-133**. All shortlisted recognizers expect
**MediaPipe** landmarks. The confirmed spans would need a MediaPipe re-extraction, which is cheap on CPU for a few
seconds of video. All candidates expect a pre-trimmed fingerspelling segment and cannot localize it themselves.

**Status:**
- **Technically feasible:** an existing recognizer with public ASL weights could run on CPU over confirmed spans,
  without training. Usage rules are pre-registered: open-vocabulary letters, LM/lexicon off, and reference names never
  given as candidates.
- **Not demonstrated:** no recognizer has been installed or run, and nothing has been trained. **There is no evidence
  yet that P0-B improves proper-name translation.**
- **None of the shortlist is commercially cleared.**

**Blocker:** an ASL-fluent reviewer must confirm, per case and per window:
- whether fingerspelling exists;
- its exact span;
- a blind letter reading;
- hand visibility;
- the type: fingerspelling / name sign / lexicalized fingerspelling.

## 4. P0-C — Input-correction Diagnostics

**Target cases:** R10, R26, R29, R35.

**Design:** one human-confirmed corrected input per case versus the original, same model and decoding, as an upper
bound only. Corrections must come from video, never from reference text or by copying official boundaries. Uniform
window widening is excluded (P0-18: WER 100.9 → 109.7).
**Sources:** [CASE_SHEET.md](../2026-10-23/p0c-input-correction/CASE_SHEET.md),
[source_check.md](../2026-10-23/p0c-input-correction/source_check.md),
[case_inputs.csv](../2026-10-23/p0c-input-correction/case_inputs.csv).

### 4.1 R26 — `G3EfBFwsOpE_3-10-rgb_front` (source checked)

**Old preprocessing, full frame (13.16–15.01 s):**
- Both hands are raised to the **top edge of the camera frame**.
- A hand keypoint lies within 15 px of the top in 43 of 44 source frames (minimum y −12 px).
- Fingertips are visibly cut off at capture in several frames.
- The hands are still mostly detected: 0 frames with a mostly low-confidence hand.

**Why a crop cannot fix it:** this input is already the full frame. Missing fingertips are a capture limit, and a
larger crop cannot recover them.

**Official window (15.15–16.62 s, crop 698×598):**
- The crop box, fitted from poses, is **x 299–1001, y 114–711** (median residual 2.1 px).
- The hands sign at chest/face height (minimum hand y 178 px), fully inside both the crop and the frame.
- **Framing therefore does not explain the official-input failure.**

**Remaining question:** timing.
- The realigned annotation of the previous sentence (`_2`, 8.56–15.15 s) contains the whole original window.
- Which span carries the target sentence needs an ASL-fluent mark within about 11.75–16.75 s.
- If it lies inside 15.15–16.62, R26 has no correction and stops.

### 4.2 R29 — `92V3oH63zbQ_5-1-rgb_front` (source checked)

**Target window 10.03–11.86 s** (identical in both domains):
- About **46 % is full rest** (10.55–11.40 s, 0.85 of 1.83 s).
- The remainder is the end of a hand-at-face hold, transitions, and the onset of the next signing run.
- Signing runs continuously before the window (from at least 5.0 s to ~10.0 s) and after it (~11.67 s to ~25.5 s).

**Timing metadata:**
- The target's "realigned" times equal its original speech times. This is true of 170 of 2,357 test rows (7.2 %), so
  the row appears never to have been realigned.
- The previous sentence (`_4`) is realigned to 11.70–16.51 s, i.e. after the target window.
- If that annotation is consistent, the target signing lies after the window. This is metadata, not visual or
  linguistic verification.

**Why a correction is plausible but not defined:**
- A time-shifted window over the actual signing is plausible.
- Its start and end cannot be set by a non-signer from video alone.
- Copying the neighbours' realigned boundaries would be oracle information. `correction_definition` is blank.

### 4.3 R10 and R35 (not source-checked)

- **R10** (608 frames; Uni-Sign keeps 256 by seeded subsampling) is blocked by a timestamp provenance conflict:
  - the downloaded How2Sign test CSV gives 23.38–42.38 s;
  - the repo subset TSV and the realigned CSV give 31.03–56.34 s.
  - Rest spans also need human labels.
- **R35** depends on the P0-B reviewer. Its two windows (6.50–12.48 s and 13.11–16.90 s) do not overlap, and the
  observed hold lies only in the original window.

**No corrected-input decode has been run for any P0-C case.** No ASL meaning was inferred in the source checks.

## 5. ASL Reviewer Follow-up Package

**Location:** [asl-reviewer-followup/](../2026-10-23/asl-reviewer-followup/) (metadata and builder tracked; videos
local only). It covers the open blockers of P0-B and P0-C.

**Contents (8 rows, one per clip):**

| row_id | Clip | Domain | Source span (s) |
|---|---|---|---|
| R02-old / R02-official | `G3OMdQo1zjY_0-10-rgb_front` | old (B_ours_5p39) / official (A_official) | 3.31–7.50 / 1.43–11.69 |
| R05-old / R05-official | `G3VM7etNABI_0-10-rgb_front` | old / official | 1.22–6.47 / 0.76–8.33 |
| R35-old / R35-official | `G2kVb4gINSI_1-10-rgb_front` | old / official | 6.50–12.48 / 13.11–16.90 |
| R26-context | `G3EfBFwsOpE_3-10-rgb_front` | full-frame source context | 11.75–16.75 |
| R29-context | `92V3oH63zbQ_5-1-rgb_front` | full-frame source context | 5.00–25.80 |

All clips are full frame at native 1280×720 and native fps, with no audio or overlays. They are cut from the How2Sign
**test** raw videos.

**Two-step design:**
- **Step 1, blind (clips only):**
  - P0-B rows: fingerspelling presence, start/end, blind letter reading (`?` for unreadable letters), type, and hand
    visibility.
  - P0-C rows: natural utterance boundaries.
- **Step 2, unblind (text only, sent after Step 1 is returned):**
  - P0-B reference names, shown within their full reference sentences, for a name-match judgement;
  - the P0-C target sentence with the sentences said before and after it, for target start/end and confidence.

**Why two steps:** blind observation comes first, so the letter readings and boundaries are not shaped by the expected
answer. Reference-conditioned localization comes second. Step 1 leaks none of the following, which was verified by
search before commit:
- reference names or target sentences;
- the R26 official window;
- R29's neighbour timings or our hypotheses.

R26 containment in the official window is not asked. It is derived after the review by the builder (`derive` mode).

**Reproducibility and checksums:**
- `build_reviewer_package.py` rebuilds byte-identical outputs: manifest, labels, both checksum files and both zips,
  verified by two rebuilds.
- Every clip has a source-video and clip sha256 in
  [reviewer_package_manifest.csv](../2026-10-23/asl-reviewer-followup/reviewer_package_manifest.csv).
- P0-B rows also record the P0-12 model-input PKL and its sha256.
- All 8 clip checksums verify.

| Package | Size | SHA-256 |
|---|---|---|
| `step1_blind.zip` | 20,669,433 B | `8a2f18552ef6698530a29ae3c365a9a49350bd42db2f9f8331c0258fb3437212` |
| `step2_unblind.zip` | 2,136 B | `7bdcbbf5bbd6189f9c58692937c199effade41cf5358342bda776bafd1117edd` |

Raw videos, clips and zips are excluded from git (How2Sign is CC BY-NC 4.0). `reviewer_labels.csv` is committed
blank.

## 6. Experimental Integrity

What the repository evidence supports:

- **H18/H19:**
  - The P0-16 `holdout_guard.assert_not_holdout` passed on every clip ID used:
    - all 45 P0-A cases;
    - the 8 P0-C target and neighbour IDs;
    - the 5 reviewer-package clips.
  - The P0-A decodes ran with open() tripwires that block val/holdout and reference paths (`tripwires_installed: true`
    in `DETERMINISM.json`).
  - The reviewer-package builder refuses any val/H18/H19 path and reads only `test_raw_videos.zip`.
  - The implemented guards and recorded runs do not access H18/H19.
- **Compute and training:** every recorded decode ran on local CPU (`device: cpu`, `precision: fp32` in `run_meta.json`).
  No GPU was used and no model, probe, reranker or recognizer was trained in this round.
- **P0-B:** no recognizer was installed or run on any clip. Reference names were not supplied as candidate lists; the
  pre-registered rules forbid it. `interval_labels.csv` is blank.
- **P0-C:** `correction_definition` and `correction_frozen_on` are blank for all four cases. No corrected input was
  built or decoded.
- **Frozen artifacts:**
  - the protocol file is unchanged since its freeze commit;
  - P0-12, P0-14, P0-18 and the 10.18 inspection sheet were read, not modified;
  - the P0-A unblinding key and the second determinism run are kept local and uncommitted, as documented.
- **Reference use:** in P0-A, references were used only to score decoded outputs and to compute the oracle upper
  bound. In P0-C, realigned neighbour timings are reported as metadata and not used as corrections.

## 7. Main Conclusions

1. **P0-A is closed.** Under the frozen +3.0 threshold, candidate reranking has too little upper-bound headroom (+2.24 /
   +2.26 corpus chrF), even with the reference choosing.
2. **P0-B** is technically feasible with existing recognizers and public ASL weights. Whether it is useful depends on
   ASL-fluent confirmation of the target spans; runtime feasibility for the selected recognizer still needs a small
   setup check. No translation improvement is demonstrated.
3. **P0-C:**
   - R26 is not explained by a simple crop fix.
   - R29 shows concrete evidence of a timing/input issue: a mostly-rest window and un-realigned metadata.
   - Neither proceeds to a corrected decode until an ASL span is confirmed.
4. **The next blocker is human ASL review, not another large model or GPU run.**

## 8. Deliverables / Commits

| Commit | Content |
|---|---|
| `c644bc3d704c1af86b8eb6da170a9a582728c9c0` (context) | P0 protocol freeze; P0-A case list and provenance; P0-B request and blank label sheet; P0-C case sheet |
| `4b36b0a36518f2d1094416e44927be06cae4aae1` | P0-A result: candidate decodes (run1, both domains), determinism record, headroom analysis, blinded review sheet, scripts, STOP verdict |
| `6133f747a55ff4adf76c3b0f0a0ea62a4606deff` | P0-B recognizer survey and shortlist; P0-C R26/R29 source checks, updated case sheet and case inputs, source-check scripts; README status |
| `6e177aad4c0b5d61b89a264f252601474967cac2` | ASL reviewer follow-up package: README, instructions, blank labels, manifest, reproducible builder |

Key files (relative to `asl-translator/daily_report/`):

- **Protocol and status:**
  - `2026-10-23/P0_PROTOCOL_FREEZE.md`
  - `2026-10-23/README.md`
- **P0-A:**
  - `2026-10-23/p0a-candidate-rerank/RESULTS.md`
  - `headroom/HEADROOM_RESULTS.md`, `headroom/headroom_summary.json`, `headroom/headroom_by_case.csv`
  - `runs/full45/DETERMINISM.json`
  - `scripts/`
- **P0-B:**
  - `2026-10-23/p0b-fingerspelling-feasibility/FEASIBILITY.md`
  - `asl_reviewer_request.md`
  - `interval_labels.csv` (blank)
- **P0-C:**
  - `2026-10-23/p0c-input-correction/CASE_SHEET.md`, `source_check.md`, `case_inputs.csv`
  - `scripts/`
- **Reviewer package:**
  - `2026-10-23/asl-reviewer-followup/README.md`
  - `reviewer_instructions.md`, `reviewer_labels.csv`, `reviewer_package_manifest.csv`, `build_reviewer_package.py`

## 9. Next Step

Send the **Step-1 blind reviewer package** to an ASL-fluent reviewer. Send Step 2 only after the Step-1 labels are
returned.

After the labels return:
- **P0-B:** each case either stops under the frozen exit conditions (not fingerspelled, not in the matched window, poor
  frames), or a very small recognizer test runs on the confirmed spans only.
- **P0-C:** each case either stops (R26 if the target is inside the official window; R29 if the target is inside its
  window or unclear), or one corrected input is defined from the reviewer's span. That definition is written and dated
  in `case_inputs.csv` before decoding, followed by the frozen original-vs-corrected decode.
