# ASL Work Report — 2026-10-27

**Scope:** ASL research work completed through 2026-10-27. That covers the follow-up to the boss's 10/27 handoff
(Tasks 1–3), set against the earlier P0 work. No new experiment was run to write this report.

**Source of truth:** the committed result files and git history on `baobao/visual-production-research-2026-10-05`.

**All 45 cases** (R01–R45) are a P0-16 *exploratory* development set. Every number below is diagnostic, not a
population-level or production claim.

> This report is intentionally a living work report. Sections under Open Items will be updated when those tasks are
> completed.

## 1. Executive Summary

**Boss's 10/27 handoff** ([THREE_P0_EXECUTION_REPORT.md](THREE_P0_EXECUTION_REPORT.md)) set three P0 follow-ups:
1. **Task 1, anti-repetition:** run the prepared paired decode (control vs `no_repeat_ngram_size=3`).
2. **Task 2, sampling:**
   - first resolve R10's conflicting timestamps and anchor which source interval actually entered Uni-Sign;
   - then compare random / uniform / coverage+motion 256-frame sampling on matched pose inputs.
3. **Task 3, fingerspelling specialist:**
   - reproduce the boss's OpenFS outputs;
   - run the R02/R05 official windows;
   - check whether the FS-Detection temporal detector can run.

**What is now complete:** all three tasks, in 5 commits. Every task finished with a measured result, and none
produced a translation-quality improvement.

**Main conclusions:**
- Anti-repetition removes loops but rewrites normal sentences.
- Input provenance is resolved for R10 and anchored for most of the 45 cases.
- Changing the sampler gives no stable gain.
- The fingerspelling recognizers produce technical output that cannot be trusted without ASL-fluent blind labels.

**Still open:** the production-model 45-case evaluation, the ASL reviewer follow-up, and the P0-A R1/R2 descriptive
gap.

| Item | Status | Basis |
|---|---|---|
| P0-A candidate headroom | **COMPLETE / STOP** | Sentence-level maximum Δ corpus chrF +2.24 (official) / +2.26 (old) < frozen +3.0 |
| Task 1 anti-repetition | **COMPLETE / DIAGNOSTIC ONLY** | Loops 9 → 0, chrF +1.73, but 15 loop-free outputs rewritten; no confirmed wrong→right |
| Task 2 input provenance | **COMPLETE / DIAGNOSTIC ONLY** | R10 resolved; 38/45 cases VERIFIED, 2 MISMATCH, 5 UNRESOLVED; all 90 model-input hashes reproduce |
| Task 2 sampling quality | **COMPLETE / NO STABLE GAIN** | A mildly positive, B mildly negative; no paired test convincing (p ≥ 0.23) |
| Task 3 fingerspelling specialist | **COMPLETE / DIAGNOSTIC ONLY** | OpenFS partially reproduced (10/18 windows); official outputs recorded; FS-Detection runs only with shims |
| ASL reviewer package | **BLOCKED ON HUMAN REVIEW** | Built and checksummed, not yet sent; labels blank |
| Production-model 45-case evaluation | **OPEN / NOT YET RUN** | — |
| P0-A R1/R2 descriptive gap | **OPEN / NOT YET RUN** | Frozen descriptive arms never reported (boss review) |

## 2. Context and Boss Handoff

- **Earlier P0 work (10/23–10/25).** P0-A, P0-B and P0-C, plus the reviewer package, were reported in
  [ASL_P0_WORK_REPORT.md](../2026-10-25/ASL_P0_WORK_REPORT.md). The boss reviewed them in
  [PROGRESS_REVIEW.md](../2026-10-25/PROGRESS_REVIEW.md):
  - the P0-A STOP stays valid under its frozen gate;
  - but the "oracle" is a reference-chosen **sentence-level chrF maximum** (descriptive selection), not a strict upper
    bound on corpus chrF;
  - the frozen R1/R2 descriptive arms were never reported;
  - reviewer Step 2 boundaries are reference-conditioned;
  - equal original/realigned times do not prove a row was never realigned;
  - the "old" column is Uni-Sign on old preprocessing, not a Gemini baseline.
- **Boss 10/27 handoff.** The boss introduced three experiments
  ([PROTOCOL.md](../../experiments/p0-2026-10-27/PROTOCOL.md)): **A Sampling**, **B Specialist**, **C Repetition**.
  He ran:
  - the sampling geometry on compressed OLD display videos;
  - OpenFS on 4 display videos (18 windows);
  - the repetition preflight, which was blocked on missing assets on his machine.

  He handed the three follow-up tasks to us.

## 3. Task 1 — Anti-Repetition Paired Evaluation

Source: [TASK1_REPETITION_RESULT.md](TASK1_REPETITION_RESULT.md) (commit `a6c7f66a`).

**Setup.**
- A_official, 45 cases, CPU only.
- Control: `num_beams=4, max_new_tokens=100`.
- Treatment: adds only `no_repeat_ngram_size=3`, which bans repeated **mT5 token** trigrams, not word trigrams.

**Control reproduction:** **45/45 text and 45/45 token ids** equal the saved P0-A CPU output. All 90 `generate`
calls ran on CPU.

| 45 cases | Control | no_repeat_ngram_size=3 |
|---|---|---|
| corpus chrF | 23.76 | 25.49 |
| BLEU-4 | 5.72 | 5.94 |
| WER | 95.44 | 92.91 |
| mean output/reference length ratio | 1.00 | 0.97 |
| `loop_out` | 9 | 0 |

**Regressions and side effects (measured):**
- 24 outputs changed. **15 of them had no loop in control.**
- `I'm` is three tokens (`▁I ' m`), so a second `I'm` in a sentence is banned. All 7 control outputs with ≥ 2 `I'm`
  were rewritten. The trigram ban therefore hits legitimate repeated token sequences.
- **R35**, one of the closest-to-reference controls, **loses "Hi, I'm Colin"** (Δ sentence chrF −5.14).
- **R01, R20 and R42** lose their loops but drop in sentence chrF.

**Conclusion:**
- A strong repetition diagnostic.
- **Not demonstrated as a translation-quality improvement:** no case is automatically confirmable as wrong→right, and
  human labels are pending.
- **Not recommended as a default decode policy.**

## 4. Task 2 — Input Provenance

Sources: [p0-input-provenance/README.md](p0-input-provenance/README.md),
[R10_PROVENANCE.md](p0-input-provenance/R10_PROVENANCE.md) (commits `3d495562`, `59b13d48`).

### 4.1 R10 resolution

- **23.38–42.38 s** comes from the How2Sign test **original, speech-aligned** CSV.
- **31.03–56.34 s** comes from the **manually re-aligned** CSV.
- **The original interval never entered Uni-Sign.** Both domains received the re-aligned interval:
  - A_official ≈ **31.04–56.38 s**;
  - B_ours_5p39 ≈ **31.21–56.54 s** (re-aligned +4 frames).
- Both inputs have **608 frames**. Uni-Sign received the **same 256 seeded frames** in both domains, and both
  model-input hashes reproduce exactly.
- B's status is **MISMATCH because of a timing label**: it is declared "original timestamps" but is the re-aligned
  interval. It is **not** an input-reproducibility failure.
- **R14** has the same class of issue: its B input is the re-aligned interval shifted −10 frames.

### 4.2 45-case provenance manifest

90 rows = 45 cases × {A_official, B_ours_5p39}. Status rules and matching thresholds were **frozen before
measurement**. Amendment 1 was written after a 2-case pilot. Amendment 2 was written before any Step 2 download or
measurement, and its positive control passed 5/5.

| | VERIFIED | MISMATCH | UNRESOLVED |
|---|---|---|---|
| A_official rows | 41 | 0 | 4 |
| B_ours_5p39 rows | 42 | 2 (R10, R14) | 1 |
| Cases (worse of two rows) | **38** | **2** | **5** |

**Remaining UNRESOLVED:**
- **R26 A, R28 A, R35 A, R42 A:** the official crop clip's position in the raw frame is not unique under the frozen
  margin.
- **R32 B:** the signer-region motion r is 0.896, below the frozen 0.90.

These were **not forced to pass**. Thresholds were not changed after results were seen. **All 90 model-input hashes
reproduce**, so what Uni-Sign received is reproducible everywhere. Only *where in the source video* 5 rows came from
remains unanchored.

## 5. Task 2 — Sampling Quality Evaluation

Source: [TASK2_SAMPLING_QUALITY_RESULT.md](TASK2_SAMPLING_QUALITY_RESULT.md) (commit `40cf0481`).

**This is a Uni-Sign diagnostic, not a production-model result.** The production Gemini path does not use this
256-frame sampling.

**Arms** (frame budget 256). Only clips over 256 frames differ; shorter clips keep every frame and act as controls.
- **random:** Uni-Sign's own seeded draw.
- **uniform:** the boss's frozen `sampling.uniform`.
- **coverage+motion:** the boss's frozen `sampling.coverage_motion`, with motion energy from the video the pose came
  from.

Everything else is fixed: model, checkpoint, decode, pose, references and metrics.

**Random control:** reproduces the historical Uni-Sign inputs (90/90 model-input hashes) and outputs (45/45 text and
token ids per domain).

| corpus chrF, provenance-VERIFIED rows | random | uniform | coverage+motion |
|---|---|---|---|
| A_official (41) | 23.73 | 24.61 | 24.70 |
| B_ours_5p39 (42) | 18.26 | 17.65 | 17.73 |

**Interpretation:**
- A is mildly positive; B is mildly negative.
- **No paired comparison is statistically convincing.** On long clips the sign-test p is ≥ 0.23, with n = 14 (A) and
  11 (B).
- Smaller sampling gaps do not consistently mean better translation. Uniform shortens the longest gap in every long
  clip, yet the translation does not improve in most of them.
- **R10 drives much of the A gain.** Without it, the A long-clip mean Δ chrF falls to +0.92 (uniform) and +0.16
  (coverage+motion).
- **R04** changes output heavily after small frame substitutions: 235–236 of 256 frames are shared with random, yet
  the hallucinated name changes.

**Conclusion:** the sampling strategy shows no stable enough signal to justify further work.

## 6. Task 3 — Fingerspelling Specialist

Source: [TASK3_FINGERSPELLING_RESULT.md](TASK3_FINGERSPELLING_RESULT.md) (commit `ad574723`).

**OpenFS (recognizer):**
- Same repo commit `0d6fa3fa` and same checkpoint (sha256 `c8e4c227…`) as the boss. His `specialist.py` was used
  unchanged.
- **Old-window reproduction is partial: 10/18 windows exact.** His compressed display inputs are not available
  locally, so I ran on the B clips they were re-encoded from.
  - Repeat runs are deterministic.
  - The differences follow from video encode, platform and MediaPipe sensitivity: MediaPipe's hand-detection counts
    differ, and greedy decoding amplifies the difference.
- **Official R02/R05 outputs are recorded**, for example R02 `camilians` and R05 `swhattey`. The full strings are in
  the result file.
- **R35 is kept separate:** its old and official windows do not overlap, and its official source time remains
  UNRESOLVED.

**FS-Detection (temporal detector):**
- The published setup **does not run as-is**:
  - CUDA is hard-coded (`AssertionError: Torch not compiled with CUDA enabled` at `rpn.py:35`);
  - the PyTorch 1.1 and Warp-CTC pins cannot be installed on Python 3.11.
- **Three minimal runtime fixes** allow strict checkpoint loading (51 tensors, none missing or unexpected) and a CPU
  forward pass on R02/R05 official. None of the fixes changes the weights:
  - built-in CTC instead of Warp-CTC;
  - RPN on CPU;
  - the VGG19 initialization download skipped.
- The outputs are **unvalidated technical spans**. There is **no accuracy claim**.
- A full port is **not justified** for R02/R05/R35 alone.

**Conclusion:** the remaining evidence bottleneck is **ASL-fluent blind labels**, not another recognizer run.

## 7. Earlier P0 Status

- **P0-A:**
  - The STOP remains valid; candidate headroom is insufficient against the frozen +3.0 gate.
  - Per the boss's correction, the "oracle" is described as a **sentence-level maximum / descriptive selection**, not
    an upper bound.
  - The frozen R1/R2 descriptive arms remain an **open protocol/report gap** (§11.C).
- **P0-B and P0-C:**
  - The feasibility survey and the R26/R29 source diagnostics remain useful background.
  - The "nothing run" part of P0-B is superseded by the actual OpenFS execution in Task 3.
  - Reviewer-dependent conclusions remain blocked:
    - P0-B: whether fingerspelling is present, its spans and letters;
    - P0-C: corrected windows.

## 8. Experimental Integrity

These statements are supported by the committed result files:

- **H18/H19 excluded.** Tasks 1 and 2 ran the P0-16 holdout guard on all 45 IDs and passed. Task 3 used only
  R02/R05/R35/R41 inputs from the 45-case exploratory set.
- **CPU only** for all new decode work:
  - Task 1: 90 `generate` calls on CPU;
  - Task 2: 283 calls on CPU, one parameter set;
  - Task 3: OpenFS and the FS-Detection smoke test ran on CPU.
- **No production/Gemini calls** in Tasks 1–3.
- **No reference names supplied to any recognizer.** The OpenFS run manifests carry only case id, video and domain.
  References were used only for scoring in Tasks 1–2.
- **Automatic metrics are kept separate from human semantic judgement.** Human labels are `pending`;
  `fs_present` is `unknown`.
- **Unresolved provenance rows were not forced to VERIFIED.** Thresholds were frozen before measurement.
- **The boss's existing files were not overwritten:** `sampling_45.json`, `sampling_summary.json`, `specialist.json`,
  `specialist.py`, `sampling.py`, `run_sampling.py`, `PROTOCOL.md`.
- **No downloaded videos or checkpoints are committed:** official crop clips, raw videos, OpenFS/FS-Detection code
  and weights stayed in scratch only.

## 9. Deliverables and Commits

| Commit | Description | Key report |
|---|---|---|
| `a6c7f66ac5b8c6984ba2403397678afa494af434` | Task 1: anti-repetition paired decode, scoring, CPU launcher | [TASK1_REPETITION_RESULT.md](TASK1_REPETITION_RESULT.md) |
| `3d495562f631ff3911a3357f45b8614e739cdb27` | Task 2 Step 1: 45-case provenance manifest, R10 resolved | [p0-input-provenance/README.md](p0-input-provenance/README.md), [R10_PROVENANCE.md](p0-input-provenance/R10_PROVENANCE.md) |
| `59b13d4814ef8f2fe74042551aaa9937df4df270` | Task 2 Step 2: Amendment 2, 9 of 14 unresolved cases anchored | [p0-input-provenance/README.md](p0-input-provenance/README.md) |
| `40cf0481503034a9016194233170dfb301653d2c` | Task 2 Step 3: same-domain sampling-quality decode and scoring | [TASK2_SAMPLING_QUALITY_RESULT.md](TASK2_SAMPLING_QUALITY_RESULT.md) |
| `ad5747235893c895ce52a1a43b0faff30f523d37` | Task 3: OpenFS reproduction / official runs, FS-Detection feasibility | [TASK3_FINGERSPELLING_RESULT.md](TASK3_FINGERSPELLING_RESULT.md) |

Structured outputs are under [`experiments/p0-2026-10-27/results/`](../../experiments/p0-2026-10-27/results/) and
[`p0-input-provenance/`](p0-input-provenance/).

## 10. Current Conclusions

1. **Anti-repetition** removes loops but is too blunt to recommend as default decoding.
2. **Input provenance:** R10 is resolved. Most of the 45-case provenance is now anchored, and all model inputs
   reproduce.
3. **Sampling:** changing the 256-frame sampler does not produce a stable translation-quality gain.
4. **Fingerspelling:** current recognizers give technical outputs, but those are not trustworthy evidence without
   ASL-fluent blind labels.
5. **The remaining work is no longer another large Uni-Sign model experiment.**

## 11. Open Items / Next Work

### A. Production-model 45-case evaluation — OPEN / NOT YET RUN

- Run the actual current production model on the same 45 videos.
- Add a real production-output column to the inspection sheet.
- Compare it against the Uni-Sign old/official outputs.

### B. ASL reviewer follow-up — HUMAN-DEPENDENT

- Fix the reviewer Step 2 wording/interpretation, so that reference-conditioned boundaries are not treated as
  reference-free evidence.
- Send the Step 1 blind package.
- Score OpenFS / fingerspelling only after blind labels return.

### C. P0-A R1/R2 descriptive gap — OPEN SMALL FOLLOW-UP

- The boss noted that these frozen descriptive arms were never reported.
- No new decode is expected if the existing candidate/probe outputs are sufficient. Otherwise, mark it explicitly as
  incomplete.

This report is intentionally a living work report. Sections under Open Items will be updated when those tasks are
completed.
