# P0-A headroom / automatic-metric oracle (2026-10-24)

**Scope:** headroom analysis only. No simple rerank (R1), no mT5-probe rerank (R2), no training, no GPU, no H18/H19.
Protocol: [P0_PROTOCOL_FREEZE.md](../../P0_PROTOCOL_FREEZE.md) §1.6 metrics, §1.7 rule 1 (unchanged).

**Inputs:**
- canonical CPU fp32 decode `runs/full45/<domain>/run1/candidates.jsonl` (run2 = determinism evidence only, identical);
- references: frozen-128 `docs/daily_report/10.13/asl-unisign-error-taxonomy/inputs_128.jsonl`, used **only to score
  candidates that already exist**. The pool was built at decode time without references and is not filtered or
  reordered here.
- **Control = today's deterministic CPU top-1 (T) in both domains.** The historical fp16 / inspection-sheet text is
  not a control.

Script: `scripts/headroom_oracle.py`. Outputs: `headroom_by_case.csv` (90 rows), `headroom_summary.json`,
`../candidate_review.csv` (26 rows), `../review_key/candidate_review_key.csv` (local only, not committed until the review is done).

---

## A. Automatic-metric oracle upper bound (NOT a system result)

Oracle = the pool candidate with the highest sentence chrF against the reference (ties → earliest pool position, so
ties keep T). It uses the reference to *choose*, so it is an upper bound on what any reranker over this pool could
reach on chrF. **It is not deployable and is never reported as a system result.**

### Corpus metrics (45 cases per domain)

| Metric (§1.6) | A_official T | A_official oracle | Δ | B_ours_5p39 T | B_ours_5p39 oracle | Δ |
|---|---|---|---|---|---|---|
| corpus chrF | 23.76 | 26.00 | **+2.24** | 18.22 | 20.48 | **+2.26** |
| corpus BLEU-4 (13a) | 5.72 | 7.05 | +1.33 | 1.70 | 2.48 | +0.79 |
| WER (×100) | 95.44 | 93.88 | −1.55 | 99.81 | 96.50 | −3.30 |
| mean length ratio | 1.000 | 1.037 | +0.037 | 1.022 | 0.948 | −0.073 |
| `loop_out` count | 9 | 9 | 0 | 11 | 10 | −1 |
| old 10.13 flag count | 7 | 7 | 0 | 9 | 8 | −1 |
| cases where the oracle differs from T | | 36 / 45 (80 %) | | | 34 / 45 (76 %) | |
| T already oracle-best | | 9 / 45 | | | 11 / 45 | |

Pool size: A_official 5 on all 45. B_ours_5p39 5 on 44, and **R42 has 4 unique candidates** (the 6 generated sequences
contained only 4 distinct texts). R42 is scored over its 4.

Median per-case Δ sentence chrF: A +1.38, B +1.54. Cases with Δ ≥ 5: A 8, B 9.

### Frozen rule 1 (headroom) — §1.7

| Part | Requirement | A_official (decides) | B_ours_5p39 (same rule, reported) |
|---|---|---|---|
| 1(a) | oracle corpus chrF − T corpus chrF ≥ **+3.0** | **+2.24 → FAIL** | **+2.26 → FAIL** |
| 1(b) | ≥ 3 of 13 reviewed cases with a pool candidate rated strictly better than T | pending (not needed for the outcome) | pending |

Rule 1 needs **(a) and (b)**. With (a) failing, the frozen outcome is **STOP — no headroom** for this pool
(num_beams 4 top-1 + num_beams 5, ≤ 5 candidates). Under the frozen protocol, R1 / R2 may only be reported descriptively,
and there is no rerank training and no further work on this fusion version. Human review cannot reverse 1(a).

### Largest per-case automatic gains (descriptive; not evidence that the candidate is better)

| Domain | ID (role) | T | Oracle candidate | sent. chrF T → oracle |
|---|---|---|---|---|
| A | R09 (ordinary control) | *(withheld — blind review case)* | *(withheld — blind review case)* | 30.3 → 51.4 |
| A | R33 | For the point of humor, I'm going to go ahead and show you what's going on. | For the purpose of a cartoon, … what happens. | 18.2 → 35.1 |
| A | R41 (named control) | *(withheld — blind review case)* | *(withheld — blind review case)* | 63.7 → 76.8 |
| A | R30 | … divide and take care of your hair. | … break down keeping your hair moving. | 30.3 → 40.6 |
| B | R01 (focus) | *(withheld — blind review case)* | *(withheld — blind review case)* | 16.4 → 38.0 |
| B | R09 (ordinary control) | *(withheld — blind review case)* | *(withheld — blind review case)* | 21.6 → 42.4 |
| B | R26 | It's going to go up and down. | We're going to go ahead and raise it up here. | 2.5 → 14.1 |
| B | R28 | And the knees are rounded. | And then he's going to lower his knees up. | 8.2 → 18.2 |

Most large gains are paraphrases or wording shifts, not recovered content (R33 and R30 in A above; review-case texts are withheld until the blind human review is done). Single-case chrF gains
are not claims that a candidate is better. That needs human review.

**T is already oracle-best:** A — R40, R04, R02, R12, R16, R31, R32, R36, R39. B — R18, R41, R20, R45, R03, R11,
R12, R19, R25, R30, R39.

### Repetition (descriptive; nothing here is "fixed")

`loop_out` is output-only (§1.4). A non-loop alternative is any pool candidate other than T with `loop_out` false.

| Domain | Looping T | … with ≥ 1 non-loop alternative | Best non-loop alternative vs T (sentence chrF) |
|---|---|---|---|
| A_official | 9 (R01, R18, R42, R20, R03, R11, R36, R39, R23) | **1**: R23 | R23 +1.4. A near-identical sentence without the repeated tail; both are only partly on-topic ("hole"). |
| B_ours_5p39 | 11 (R15, R24, R42, R10, R11, R12, R16, R21, R23, R35, R36) | **3**: R15, R10, R16 | R15 +6.8 (review case; text withheld). R10 +4.9 (different, unrelated content). R16 +3.6 (shorter repeat, still off the reference topic). None of the three looks like it recovers the reference meaning; only R15 is a human-review case, so this is unconfirmed. |

In 8 of 9 (A) and 8 of 11 (B) looping cases, every candidate in the pool also loops. Less repetition or shorter
output alone is not success (§0).

The oracle's own loop count is unchanged in A (9) and −1 in B (10). The chrF oracle mostly picks among looping
variants.

## B. Human candidate comparison — PENDING

`../candidate_review.csv`: the 13 frozen review cases × 2 domains = 26 rows.
- Focus: R01, R15, R18, R24, R40, R42.
- Named control: R41.
- Ordinary controls: R04, R09, R20, R22, R27, R45.

Per §1.6 the reviewer sees the ground truth and the deduplicated pool as candidates A–E in an order shuffled by
`sha256(domain|clip_id)`, **with no rank or arm label. T is one of A–E and is not marked.** R42 / B_ours_5p39 has
candidates A–D only.

Blank fields to fill:
- per candidate: `status_X` (`correct` / `partial` / `wrong` / `cant_tell`) and `error_tags_X` (entity,
  negation/polarity scope, number owner, action object/participant, hallucinated content, loop);
- `best_candidate`, `top1_status`, `best_candidate_status`, `wrong_to_right`, `right_to_wrong`, `unchanged`,
  `changed_same_status`, `cant_tell`, `notes`.

The last group is meant to be filled, or derived, **after** unblinding with `../review_key/candidate_review_key.csv`.
That key maps each letter to pool position, source rank, `is_cpu_top1` and `is_auto_oracle`, and is not to be shown to
the reviewer. Nothing in the human fields was auto-filled. This is an English-meaning comparison, not ASL-fluent
verification.

Status after rule 1(a): the review no longer changes the rule-1 outcome. It remains the only way to say whether any
candidate is semantically better (descriptive, and needed if R1/R2 are reported descriptively per §1.7).

## C. Deployable reranker — NOT RUN

R1 (simple loop-aware rerank) and R2 (+ P0-14 mT5 probe) have not been run. No rerank output exists, and no reranker or
probe was trained.

## Answer to the Stage-1 question

*Is there enough candidate headroom to justify trying a simple deployable reranker?*

**No, under the frozen protocol.** Oracle-best-in-pool raises corpus chrF by only +2.24 (A_official, deciding domain)
and +2.26 (B_ours_5p39), below the frozen +3.0 threshold of rule 1(a). The frozen outcome is **STOP — no headroom**
for this candidate pool, independent of the pending human review. This is a diagnostic result on 45 exploratory
test_clean cases, not a population claim.
