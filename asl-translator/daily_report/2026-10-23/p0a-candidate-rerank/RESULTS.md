# P0-A results — candidate headroom (2026-10-24)

## Verdict

**P0-A STOP / NOT ENOUGH CANDIDATE HEADROOM.**

The oracle-best candidate in the pool raises corpus chrF by **+2.24** (A_official, the deciding domain) and **+2.26**
(B_ours_5p39) over today's CPU top-1. The frozen threshold is **+3.0**. P0-A therefore fails the frozen
candidate-headroom criterion (§1.7 rule 1a).

As a result, **no simple rerank (R1), no mT5-probe rerank (R2), no reranker training and no GPU experiment are run.**
This verdict is final under the frozen protocol. The optional human candidate review below is diagnostic only and
**cannot change or override it**.

Scope: 45 exploratory test_clean cases (P0-16), diagnostic/development only. No confirmatory or population claim.

## 1. Experimental question

Is a better sentence already among Uni-Sign's beam candidates but not chosen as top-1? If so, could a simple,
reference-free reranker pick it? Source: [boss report 2026-10-21 §7](../../2026-10-21/UNISIGN_CASE_REVIEW_AND_P0_PLAN.md).
The question is answered here only up to its first gate: is there enough headroom in the pool at all?

## 2. Frozen stop criterion

From [P0_PROTOCOL_FREEZE.md](../P0_PROTOCOL_FREEZE.md) §1.7 rule 1, frozen 2026-10-23 before any decode and not
modified:

> **Headroom.** (a) Oracle corpus chrF − T corpus chrF ≥ **+3.0** on 45, **and** (b) in ≥ 3 of 13 reviewed cases, a
> pool candidate is rated strictly better than T. If either fails: **STOP — no headroom**. R1/R2 are reported
> descriptively, with no rerank training and no further work on this fusion version.

D-A (A_official) decides. D-B (B_ours_5p39) is reported with the same rule.

| Part | A_official | B_ours_5p39 |
|---|---|---|
| (a) Δ corpus chrF ≥ +3.0 | +2.24 → **FAIL** | +2.26 → **FAIL** |
| (b) human, ≥ 3 / 13 strictly better | not needed (a failed); optional diagnostic | same |

## 3. Setup (what was decoded)

- **Model:** Uni-Sign `eed438bc`, checkpoint sha256 `1bfd5f33…`, mT5-base `2eb15465`.
- **Compute:** local CPU fp32, batch 1. Per-clip frame seed for clips over 256 frames. Inputs are the P0-12 PKLs
  (A_official 45/45 and B_ours_5p39 45/45, sha256-verified).
- **T (control) = today's deterministic CPU top-1** (`num_beams=4`) in both domains. The historical T4 fp16 /
  inspection-sheet output is descriptive only and is **not** the B-domain control.
- **Pool:** T, then the 5 sequences of `num_beams=5`. Exact-text deduplication, truncated to at most 5. Built without
  references.
- **Canonical decode:** `runs/full45/<domain>/run1/`. `run2/` is an independent repeat: identical on 45/45 per domain
  (count, order, token ids, text, frame indices, model-input hash; score difference 0.0).
- **D-A control check:** T equals the stored P0-14 CPU fp32 control on 45/45, including all 14 clips over 256 frames
  (R04 and R20 among them).
- **Holdouts:** P0-16 guard passed on all ids. Val/holdout and reference open() blocks were active in every decode
  process. H18/H19 were not opened.
- **Runtime:** total wall clock 22.3 min (21:49:48–22:12:07, 2026-10-23).

## 4. Automatic-metric oracle — an upper bound, not a system

The **oracle** is the pool candidate with the highest sentence chrF against the **reference** (ties go to T). It needs
the reference to choose, so it is **a reference-based upper bound on what any reranker over this pool could reach, not
a deployable system**, and it is never reported as a system result.

Metrics are the ones frozen in §1.6.

| Metric | A_official T | A_official oracle | Δ | B_ours_5p39 T | B_ours_5p39 oracle | Δ |
|---|---|---|---|---|---|---|
| corpus chrF | 23.76 | 26.00 | **+2.24** | 18.22 | 20.48 | **+2.26** |
| corpus BLEU-4 (13a) | 5.72 | 7.05 | +1.33 | 1.70 | 2.48 | +0.79 |
| WER (×100) | 95.44 | 93.88 | −1.55 | 99.81 | 96.50 | −3.30 |
| mean length ratio | 1.000 | 1.037 | +0.04 | 1.022 | 0.948 | −0.07 |
| `loop_out` count | 9 | 9 | 0 | 11 | 10 | −1 |
| old 10.13 flag count | 7 | 7 | 0 | 9 | 8 | −1 |

Even choosing with the reference, the best candidate in a 5-candidate pool lifts corpus chrF by less than the frozen
bar. A deployable, reference-free reranker can only do worse than this bound.

## 5. Candidate diversity

| | A_official | B_ours_5p39 |
|---|---|---|
| Pool size | 5 on 45/45 | 5 on 44/45; **R42 = 4** |
| Unique texts among the 6 generated (before truncation) | 5 on 34, 6 on 11 | 4 on 1, 5 on 26, 6 on 18 |
| 5-beam rank-0 ≠ 4-beam top-1 | 16 / 45 | 23 / 45 |
| Some candidate scores above T (sentence chrF) | 36 / 45 (80 %) | 34 / 45 (76 %) |
| T already oracle-best | 9 / 45 | 11 / 45 |
| Median per-case Δ sentence chrF | +1.38 | +1.54 |
| Cases with Δ ≥ 5 | 8 | 9 |

The pool is diverse in wording: most cases have some candidate with a higher chrF. The gains are small, though. Most
are rewording of the same content rather than content the top-1 missed.

## 6. Cases with the largest automatic gains (descriptive)

Sentence chrF T → oracle. Texts of the 13 human-review cases are **withheld** until the blind review is complete.
Non-review texts are in `headroom/headroom_by_case.csv`.

| Domain | Case (role) | T → oracle chrF | Note |
|---|---|---|---|
| A | R09 (ordinary control) | 30.3 → 51.4 | review case |
| A | R33 | 18.2 → 35.1 | rewording ("point of humor" → "purpose of a cartoon") |
| A | R41 (named control) | 63.7 → 76.8 | review case |
| A | R30 | 30.3 → 40.6 | different wording, same topic |
| A | R05 | 20.5 → 30.4 | different surname, extra clause. Not a name fix (P0-B case). |
| B | R01 (focus) | 16.4 → 38.0 | review case |
| B | R09 (ordinary control) | 21.6 → 42.4 | review case |
| B | R26 | 2.5 → 14.1 | different sentence, still off-reference |
| B | R28 | 8.2 → 18.2 | different sentence, still off-reference |
| B | R34 | 21.4 → 30.2 | longer, more repetitive variant, still off-reference |

A higher chrF on one case does not show that a candidate is better.

## 7. Cases with no better candidate (T is already oracle-best)

- **A_official (9):** R40, R04, R02, R12, R16, R31, R32, R36, R39
- **B_ours_5p39 (11):** R18, R41, R20, R45, R03, R11, R12, R19, R25, R30, R39

## 8. Repetition analysis (descriptive; nothing is "fixed")

`loop_out` (§1.4) is output-only.

| | A_official | B_ours_5p39 |
|---|---|---|
| Looping T | 9: R01, R18, R42, R20, R03, R11, R36, R39, R23 | 11: R15, R24, R42, R10, R11, R12, R16, R21, R23, R35, R36 |
| … with ≥ 1 non-loop alternative in the pool | **1**: R23 | **3**: R15, R10, R16 |
| … where every candidate also loops | 8 | 8 |
| Best non-loop alternative, Δ sentence chrF | R23 +1.4 | R15 +6.8, R10 +4.9, R16 +3.6 |
| Does it preserve reference meaning (automatic view) | R23: the same sentence without the repeated tail, only partly on-topic | R10: different content, unrelated. R16: shorter repeat, off-topic. R15: review case, text withheld. None looks like a recovery. |

The beam pool rarely contains a non-looping alternative to a looping top-1. Where it does, the alternative does not
look like a meaning recovery by automatic metrics. Less repetition or shorter output alone is not success (§0). Only
R15 is a human-review case; the others are not verified by a person.

## 9. Not run

- R1 simple rerank: **not run**.
- R2 mT5-probe rerank: **not run**.
- No reranker or probe training. No GPU. No H18/H19.
- The §1.7 provision to report R1/R2 "descriptively" is not exercised; per the 2026-10-24 instruction, no rerank of
  any kind is run.

## 10. Optional human diagnostic review (cannot change the verdict)

`candidate_review.csv` holds 13 review cases × 2 domains = 26 rows:
- Focus: R01, R15, R18, R24, R40, R42.
- Named control: R41.
- Ordinary controls: R04, R09, R20, R22, R27, R45.

For each row the reviewer sees the ground truth and the pool as candidates A–E, shuffled by `sha256(domain|clip_id)`,
with no rank or arm label. T is one of A–E and is not marked. R42 / B has A–D only.

**Blinding:** until the sheet is filled, do not open `review_key/` (local only), `headroom/headroom_by_case.csv`,
`runs/` or the candidate texts in earlier chat reports. In the committed `headroom_by_case.csv` and `candidates.jsonl`,
pool position 0 is T by construction, so anyone reading them can unblind. Reviewers should work from
`candidate_review.csv` alone. Each of these identifies T and/or the automatic oracle. Unblind with
`review_key/candidate_review_key.csv` only after the human fields are filled.

The outcome is reported as qualitative/diagnostic evidence about the candidates (entity, negation, number, action,
hallucination, loop). It **does not reopen P0-A**.

## Files

| File | Content |
|---|---|
| `scripts/decode_candidates.py` | CPU fp32 candidate decoder (resumable, deterministic order, holdout and reference tripwires) |
| `runs/full45/{A_official,B_ours_5p39}/run1/` | Canonical decode: `candidates.jsonl` (every candidate's text, token ids, rank, sequence score, log-prob sum, seed, domain, pose provenance) and `run_meta.json` |
| `runs/full45/DETERMINISM.json` | G3 evidence: run1 vs independent run2, 45/45 identical per domain, score diff 0.0, with both files' sha256 |
| `scripts/determinism_summary.py` | Builds `DETERMINISM.json` |
| `scripts/headroom_oracle.py` | Oracle / metrics / blinded review sheet |
| `headroom/headroom_by_case.csv`, `headroom/headroom_summary.json`, `headroom/HEADROOM_RESULTS.md` | Per-case and corpus headroom analysis |
| `candidate_review.csv` | Blank blinded human sheet |
| `review_key/candidate_review_key.csv` | Unblinding key (letter → pool position, rank, is_cpu_top1, is_auto_oracle). **Local only, not committed** until the review is done. |

Not committed (local only): `runs/full45/*/run2/` (summarised in `DETERMINISM.json`), `runs/full45/*.log`, `runs/smoke5/` (5-case
smoke decode with an earlier script version without frame fingerprints; all 5 gates passed), `review_key/`.
