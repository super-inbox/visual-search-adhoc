# P0 protocol freeze — P0-A / P0-B / P0-C (2026-10-23)

**Status: FROZEN 2026-10-23, before any decode.** Source of truth:
[2026-10-21 boss report](../2026-10-21/UNISIGN_CASE_REVIEW_AND_P0_PLAN.md) §7–§10.
No candidate, rerank, fingerspelling or corrected-input output exists at freeze time.

This is **not** a P0-19 start and does not change the P0-19 protocol. The frozen
[P0-19 Stage 0](../../../docs/daily_report/10.20/asl-p0-19-safe-rerank/EXPERIMENT_PLAN.md) (2,209 clips, GPU) is
**not run**.

## 0. Rules for all three P0s

| Rule | Frozen requirement |
|---|---|
| Compute | Local CPU only (Apple M3 Pro, env `unisign-cpu-arm64`). No GPU, no VM, no cloud spend. |
| Training | None. No probe fitting, no reranker fitting, no fine-tuning, no specialist recognizer training. |
| Holdouts | **No H18/H19 access.** Every clip ID passes the P0-16 `holdout_guard.assert_not_holdout`. Never open How2Sign val material: `val_raw_videos.zip`, `how2sign_val.csv`, val poses, `crop_val_index.tsv`. |
| Reference text | References are used **only to score outputs after decoding**. No reference-derived candidate list, lexicon, name list, window boundary or correction. P0-B never receives the reference name as a vocabulary. |
| Data role | All 45 cases are P0-16 `exploratory` (test_clean, in the frozen 128). Results are **diagnostic/development only**. No confirmatory or population-rate claim. |
| Thresholds | Every threshold below is fixed now. **No threshold, arm, case list or metric changes after any result is seen.** An amendment must be a dated section added *before* the decode it affects. Results already produced keep their original rules. |
| Outcome reporting | Every arm-vs-control comparison reports **wrong→right, right→wrong, unchanged, changed-same-status and can't-tell**, never only improvements. Abstention (keeping top-1) is counted separately from correct output. |
| Not success | A drop in repetition, shorter output or a single higher text score alone is not success. |
| Licence | How2Sign videos and derived frames (CC BY-NC 4.0) are not committed. |

## 1. P0-A — candidate upper bound → simple rerank → mT5-probe rerank

### 1.1 Allowed cases (frozen)

`p0a-candidate-rerank/case_list.csv`, built by `scripts/build_provenance.py`:

| Role | Cases | Human review |
|---|---|---|
| Focus (boss §7) | R01, R15, R18, R24, R40, R42 | yes |
| Named do-no-harm control (boss §7) | R41 | yes |
| Ordinary controls: the 6 lowest `sha256(clip_id)` among cases that are not focus, named or another P0's case (reference-free rule) | R04, R09, R20, R22, R27, R45 | yes |
| Decode-only (automatic metrics) | the other 32 cases | no |

Decode set = all **45** cases. Human review set = **13** cases. No case is added or dropped after decoding.

### 1.2 Input domains (frozen)

| Domain | Inputs | Role |
|---|---|---|
| **D-A (primary)** | P0-12 `prepared_inputs/A_official/test-pose-rtmpose-192/<clip>.pkl` (official poses, realigned timing, official crop) | Matches the inspection sheet's "official" column. Only domain where the probe arm runs. |
| **D-B (secondary)** | P0-12 `prepared_inputs/B_ours_5p39/test-pose-rtmpose-192/<clip>.pkl` (our extractor, original timing, full frame) | Matches the inspection sheet's "old / our" column. |

Neither domain is customer-deployable (D-A uses official benchmark timing). Inputs must equal
`CHECKSUMS.sha256` (verified 45/45 for both on 2026-10-23).

### 1.3 Decoding (frozen)

Uni-Sign `eed438bcb49e30405cd6ccdfcccca330c134e830`. Checkpoint `how2sign_pose_only_slt.pth`, sha256
`1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d`. mT5-base snapshot
`2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f`. CPU, fp32, batch 1, seed 42, `max_new_tokens=100`.
Clips with more than 256 frames are subsampled exactly as P0-14/P0-19 do:
`random.seed(int(sha256(clip_id)[:8], 16))`. One forward pass per clip feeds both generations.

- **T (control top-1):** `num_beams=4`, 1 sequence.
- **Candidate pool:** T first, then the 5 sequences of a `num_beams=5, num_return_sequences=5` run, with
  `output_scores=True`. Exact-text deduplication keeps the first occurrence. The pool is **truncated to ≤ 5 unique**.
  Pre- and post-deduplication counts are recorded. A pool with fewer than 5 is reported as is.

### 1.4 Arms (frozen, all reference-free)

`loop_out(x)`: lowercase `x` and tokenize with `[a-z0-9']+`. `rep3_ratio_out = 1 − distinct word 3-grams / total
word 3-grams` (0 if there are fewer than 3 tokens). `loop_out` holds if `rep3_ratio_out ≥ 0.15`. It is **output
only**: no reference exclusion. The old 10.13 flag is reported beside it, unchanged.

| Arm | Selection rule |
|---|---|
| **T** | Current top-1 (control). |
| **R1 simple rerank** | If `loop_out(T)` is false, keep T. Otherwise choose the non-loop pool candidate with the highest HF `sequences_scores` from the `num_beams=5` run. If there is none, keep T. |
| **R2 = R1 + mT5 probe** (D-A only) | `P` = the concepts predicted positive (`test_pred`) for the clip in P0-14 `results/lr/mt5_ms_testcv_r0.json` (video-grouped out-of-fold, sha256 `ab1f932d…7528146`). `K(x)` = P0-14 Tier L concepts mentioned in `x` (frozen matcher, `p019_common.py`). `support(x) = |K(x)∩P| − |K(x)\P|`. Start from R1's choice `x1`. Switch to the non-loop candidate with maximal support (ties go to the earlier pool position) **only if** `support ≥ support(x1) + 1`. Otherwise keep `x1`. The probe never adds words. |

Descriptive only (no decision weight): beam-5 rank-0; probe fold seeds r1/r2 (sha256 `606fe1e5…`, `c794dcb7…`).

### 1.5 Gates (any FAIL → VOID: nothing interpreted, no re-run under the same name)

| Gate | Requirement |
|---|---|
| G1 input integrity | 45/45 pose sha256 equal `CHECKSUMS.sha256` in both domains at decode time |
| G2 holdout | The guard passes on all IDs. No val / H18 / H19 path is opened (open() tripwire as in `p019_common.py`). |
| G3 determinism | An independent second process on the first 5 `case_list.csv` clips per domain gives identical pool order, token IDs and texts. `\|Δ seq score\| ≤ 1e-5`. |

Descriptive, not a gate: T vs the stored P0-12 T4/fp16 text, and T vs the stored P0-14 fp32 prediction (D-A).

### 1.6 Metrics (frozen)

Automatic, all 45, per domain and arm:
- corpus chrF (sacrebleu `corpus_chrf` defaults) and corpus BLEU-4 (13a);
- WER (lowercase whitespace tokens, ×100);
- mean output/reference word-length ratio;
- `loop_out` count and old-flag count;
- number of cases changed vs T;
- per-clip CPU seconds per arm.

**Oracle** = the pool candidate with the highest sentence chrF against the reference. It is reported separately and
is **never** presented as a system result.

Human, on the 13 review cases per domain:
- The reviewer sees the reference plus the deduplicated pool in shuffled order, with no arm labels.
- Each candidate gets a critical-meaning status: `correct` > `partial` > `wrong`, or `cant_tell`.
- Error tags: entity, negation/polarity scope, number owner, action object/participant, hallucinated content, loop.
- Status changes vs T give wrong→right (status rises), right→wrong (status falls), unchanged (identical text),
  changed-same-status, and can't-tell.
- This is an English-meaning comparison, **not** ASL-fluent verification.

### 1.7 Decision rules (frozen; D-A decides, D-B reported with the same rules)

1. **Headroom.** (a) Oracle corpus chrF − T corpus chrF ≥ **+3.0** on 45, **and** (b) in **≥ 3 of 13** reviewed
   cases, a pool candidate is rated strictly better than T. If either fails: **STOP — no headroom**. R1/R2 are reported
   descriptively, with no rerank training and no further work on this fusion version.
2. **Allowed degradation** for R1 vs T and R2 vs T. All must hold:
   - human right→wrong ≤ **1** of 13;
   - **0** right→wrong among the 7 controls (R41 + 6 ordinary);
   - corpus WER Δ ≤ **+1.0** point;
   - corpus chrF Δ ≥ **−0.5**;
   - mean length ratio within **±10 %** of T's;
   - `loop_out` count ≤ T's.
3. **Useful arm:** degradation limits hold **and** wrong→right ≥ **2** **and** wrong→right ≥ 2 × right→wrong.
4. **Probe increment:** R2 continues only if net (wrong→right − right→wrong) ≥ R1 net **+ 1** and R2 is no worse
   than R1 on any limit in rule 2. Otherwise **STOP the probe version**.

### 1.8 Cost cap

The total P0-A decode wall-clock across both domains is at most **6 h** of local CPU. If any single clip takes more
than 10 min, abort and report. Cloud spend is $0. Human review takes about 13 cases × 2 domains.

## 2. P0-B — fingerspelling / name feasibility (no decoding, no training)

- Allowed cases: **R02, R05, R35** only.
- The first step is an ASL-fluent reviewer confirming the spans
  (`p0b-fingerspelling-feasibility/asl_reviewer_request.md`), done blind first and unblinded second. Claude does
  not infer or fill spans.
- Inputs are the **matched actual input windows** (D-A realigned and D-B original, cut from the How2Sign test raw
  video). The 4 fps contact sheets are not recognizer input.
- A recognizer may be evaluated only if it already exists, its licence permits the use, and it runs on CPU. Metrics:
  character error rate, exact name match, coverage, replacement precision, and sentence damage after local
  replacement.
- Low confidence means no change.
- **Stop:** the name is not in the window, it is not fingerspelled, the frames are insufficient, or there is no
  reliable recognizer gain. A specialist trained from scratch is not low-cost and needs a new decision.

## 3. P0-C — input-correction upper bound (after P0-A setup)

- Allowed cases: **R10, R26, R29, R35** only.
- Arms: original input vs **one** human-confirmed corrected input per case. Same model and T decoding as §1.3, in the
  domain recorded in `p0c-input-correction/case_inputs.csv`.
- Corrections come from video inspection only (rest interval, source framing, neighbouring context), never from
  reference text or by copying official boundaries as the "automatic" method.
- **Do not re-run uniform window widening.**
- The same outcome labels as §1.6, plus key content recovered and new omissions.
- Each correction's definition is written into `case_inputs.csv` and dated **before** its decode.
- **Stop / no automation:** no case shows semantic improvement, or the improvement depends on oracle information.
