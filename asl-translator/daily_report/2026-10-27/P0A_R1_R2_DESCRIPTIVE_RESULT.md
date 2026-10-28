# P0-A R1/R2 Descriptive Arms

**Status:** reporting gap closed by **deterministic selection and scoring on the existing candidate pools**.
- No Uni-Sign decode or other model run. No human labels (none exist).
- **The P0-A STOP decision is unchanged.**

Structured evidence: [`p0a_r1_r2_descriptive.json`](../../experiments/p0-2026-10-27/results/p0a_r1_r2_descriptive.json).
Script: [`p0a_r1_r2_descriptive.py`](../../experiments/p0-2026-10-27/p0a_r1_r2_descriptive.py).

## Why this follow-up exists

- **What the protocol required.** The frozen protocol ([P0_PROTOCOL_FREEZE.md](../2026-10-23/P0_PROTOCOL_FREEZE.md),
  commit `c644bc3d`) §1.7 rule 1: on a headroom failure, "**STOP — no headroom**. R1/R2 are reported descriptively,
  with no rerank training and no further work on this fusion version."
- **What was actually reported.** P0-A stopped at rule 1(a): the sentence-level chrF maximum within the pool (the
  protocol's "oracle", a reference-chosen descriptive selection, not an upper bound) gave +2.24 corpus chrF over T on
  A_official, below +3.0. But [RESULTS.md](../2026-10-23/p0a-candidate-rerank/RESULTS.md) §9 records "R1 simple
  rerank: **not run**. R2 mT5-probe rerank: **not run**. The §1.7 provision to report R1/R2 'descriptively' is not
  exercised", following a 2026-10-24 instruction.
- **The boss's note.** [PROGRESS_REVIEW.md](../2026-10-25/PROGRESS_REVIEW.md) item 2: the frozen §1.7 requires R1/R2
  to be reported descriptively even when stopped. The state should be "gate ended, descriptive arms incomplete".
  If filled in, use only existing candidates and frozen probe outputs: no threshold change, no training, no new decode.
- **What this note does.** It closes exactly that gap. It does not reopen P0-A or change the STOP decision.

## Evidence used (all pre-existing)

| Input | Source | Check |
|---|---|---|
| Candidate pools (T + beam-5, ≤ 5 unique, `beam5_seq_score` per candidate) | `p0a-candidate-rerank/runs/full45/{A_official,B_ours_5p39}/run1/candidates.jsonl` (canonical decode) | A sha256 `aeb81764…` = P0-A canonical. Both pools hold 45/45 cases. T metrics equal `headroom_summary.json` top-1 exactly |
| References | 10.13 `inputs_128.jsonl` (scoring only) | same file P0-A used |
| Probe predictions `P` | P0-14 `results/lr/mt5_ms_testcv_r0.json` (local `p014-work`, not committed) | sha256 `ab1f932d…7528146` = the frozen value. r1/r2 seeds `606fe1e5…`, `c794dcb7…` = frozen |
| `test_pred` row order | P0-14 `splits/manifest.csv`, `test_clean` rows (2,209) | the 45 clips are all present. This is the order `run_probe.py` writes `test_pred` in |
| Concept matcher `K(x)` | `p019_common.load_matcher` (P0-14 `build_concepts.py`, Tier L = 24 concepts) | reproduces the manifest's concept labels from the references on 45/45 |
| Metrics | §1.6 functions copied verbatim from `headroom_oracle.py` | — |

**Did this need a model run?** No. Both arms are selection rules over pools that were already decoded and scored by
P0-A.
- The beam-5 scores R1 needs are stored per candidate.
- The probe predictions R2 needs exist with the frozen hashes.

The holdout guard and the P0-19 open() tripwire ran on all 45 IDs, and no val, H18 or H19 path was opened.

## R1

**Protocol definition (§1.4):**
- "If `loop_out(T)` is false, keep T."
- "Otherwise choose the non-loop pool candidate with the highest HF `sequences_scores` from the `num_beams=5` run."
- "If there is none, keep T."
- `loop_out`: word-3-gram repetition ratio ≥ 0.15, output only. Ties go to the earlier pool position.

**Result (45 cases; automatic metrics, §1.6):**

| Domain | Arm | chrF | BLEU-4 | WER | len ratio | loop_out | old flag | changed vs T |
|---|---|---|---|---|---|---|---|---|
| **A_official** (deciding) | T | 23.7634 | 5.7246 | 95.4369 | 0.9997 | 9 | 7 | — |
| | **R1** | 23.8516 (+0.09) | 5.7482 (+0.02) | 95.3398 (−0.10) | 1.0003 | 8 | 7 | **1** (R23) |
| B_ours_5p39 | T | 18.2174 | 1.6959 | 99.8058 | 1.0215 | 11 | 9 | — |
| | **R1** | 18.5191 (+0.30) | 1.7162 (+0.02) | 97.6699 (−2.14) | 0.9156 | 8 | 7 | **3** (R15, R10, R16) |

**Which cases change:**
- R1 changes only cases where T loops **and** the pool has a non-loop alternative. These are exactly the cases P0-A's
  repetition analysis listed: R23 (A); R15, R10, R16 (B).
- In every other looping case (8 per domain) R1 keeps T, because every pool candidate also loops.
- Sentence chrF on the changed cases:
  - A R23: 21.68 → 23.10;
  - B R10: 12.63 → 17.56;
  - B R16: 14.45 → 18.09;
  - B R15: 5.31 → 9.12 (a review case, so its text is withheld as in RESULTS.md).
- R1 changes no control case (R41 + 6 ordinary) in either domain.
- Per-clip CPU: R1 needs the beam-5 pool, so it costs 5.76 s/clip mean (A) and 5.73 (B), against 2.88 for T alone,
  from the recorded decode times. Selection itself adds nothing.

**Interpretation:**
- On A_official, R1 is a one-case change worth +0.09 chrF: it removes one loop (R23) and nothing else.
- On B_ours_5p39 it touches 3 looping cases. The WER and length drop mostly comes from removing loops (shorter
  outputs).
- P0-A's own automatic reading of these alternatives (RESULTS.md §8) found none that looks like a meaning recovery.

**Limitations:**
- Automatic metrics only.
- §1.7 rules 2–4 need human wrong→right / right→wrong statuses on the 13 review cases. `candidate_review.csv` has
  none, so those rules are **not evaluable**.
- The automatic sub-limits of rule 2 are shown in the JSON for information only. They hold for A. For B the length
  ratio moves −10.4 %, outside the ±10 % limit.

## R2

**Protocol definition (§1.4, D-A only):**
- `P` = the concepts predicted positive (`test_pred`) for the clip in P0-14 `mt5_ms_testcv_r0.json`.
- `K(x)` = P0-14 Tier L concepts mentioned in `x` (frozen matcher).
- `support(x) = |K(x)∩P| − |K(x)\P|`.
- Start from R1's choice `x1`. Switch to the non-loop candidate with maximal support (ties go to the earlier pool
  position) **only if** `support ≥ support(x1) + 1`. Otherwise keep `x1`. The probe never adds words.

**Result (A_official, 45 cases):**

| Arm | chrF | BLEU-4 | WER | len ratio | loop_out | old flag | changed vs T |
|---|---|---|---|---|---|---|---|
| T | 23.7634 | 5.7246 | 95.4369 | 0.9997 | 9 | 7 | — |
| R1 | 23.8516 | 5.7482 | 95.3398 | 1.0003 | 8 | 7 | 1 |
| **R2 (probe seed r0, frozen)** | 23.7152 (−0.05 vs T) | 5.6181 | 95.5340 | 0.9986 | 8 | 7 | **2** (R23 via R1, R12) |
| R2, seed r1 (descriptive) | 23.7152 | 5.6181 | 95.5340 | 0.9986 | 8 | 7 | 2 |
| R2, seed r2 (descriptive) | 23.8516 | 5.7482 | 95.3398 | 1.0003 | 8 | 7 | 1 (= R1) |

**How R2 behaves:**
- R2 keeps R1's choice in 36 cases.
- It has no non-loop candidate in 8 cases.
- It switches in **1 case: R12**. There the probe concepts are {TURN, PLACE, PIECE}, support rises from −2 to −1,
  and sentence chrF falls 20.63 → 17.65.
- With seed r2 the switch does not happen, so R2 = R1.
- R2 changes no control case.

**Interpretation:**
- The probe almost never acts: 1/45 cases.
- Where it acts (seed r0 and r1) it lowers automatic chrF on that case, leaving R2 slightly below T and R1 on corpus
  chrF.
- Whether it acts depends on the probe fold seed.
- There is no descriptive sign that the mT5 concept probe adds useful selection signal on this pool.

**Limitations:**
- Automatic metrics only. Human rules 2–4 are not evaluable, for the same reason as R1.
- **Reproducibility:** the probe files are local, uncommitted P0-14 artifacts (`p014-work/results/lr/`) and are not
  part of this commit. **Another machine needs the matching frozen probe files to reproduce R2.** R1 and the T
  baselines need only committed files. The required sha256 values are recorded in the JSON and the script:
  - `mt5_ms_testcv_r0.json` `ab1f932db2f1b33470544677d6d5004060901f1421de4d63e892c910b7528146`;
  - `r1` `606fe1e5d4d7710043b0c6272a21c7e5e83e7787b2dfe550ba3d20f86706b3ca`;
  - `r2` `c794dcb7049331875140af73d1ad48ce540ca52f0be7be53131c8914e013cacf`.

  The script stops with a clear message if a file is missing or its hash differs. A valid rerun reproduces the JSON
  byte for byte.
- R2 is defined for D-A only.

**Also descriptive (§1.4):** beam-5 rank-0 as an arm.
- A: chrF 23.58, 10 loops, 16 cases changed, including control R45.
- B: chrF 18.06, 14 loops, 23 cases changed, including 4 controls.
- It is worse than T on chrF and loops in both domains.

## Relationship to P0-A decision

- **R1 and R2 are descriptive only.** The STOP was decided by §1.7 rule 1(a), and rules 2–4 apply only after headroom
  passes. Nothing here enters a decision rule.
- **They do not affect the candidate-headroom conclusion; they agree with it.**
  - The reference-chosen sentence-level maximum within the pool was +2.24 (A).
  - The reference-free arms get **+0.09 (R1)** and **−0.05 (R2)**.
  - A rerank of this 5-candidate pool moves corpus metrics by about 0.1 chrF and changes 1–2 of 45 outputs on the
    deciding domain.
- **The P0-A STOP decision is unchanged.**

## Integrity / limitations

- **No human semantic labels are available.** `candidate_review.csv` status columns are blank, so no wrong→right /
  right→wrong count is reported, and the human parts of §1.7 rules 1(b) and 2–4 remain unevaluated.
- **No retrospective tuning:** the frozen rules, thresholds, probe file, seed and matcher are used as written.
- **No protocol change.** No new decode, no training, no GPU. The holdout guard passed.
- **No production claim:** this is Uni-Sign on the 45 exploratory cases (A_official / B_ours_5p39 inputs). The
  production Gemini path is unrelated.
- **No reviewer-dependent claim.** The texts of the 13 human-review cases are withheld, as in P0-A's RESULTS.md.
- n = 45 is a worst-first exploratory sample, so these are diagnostic numbers, not population estimates.
