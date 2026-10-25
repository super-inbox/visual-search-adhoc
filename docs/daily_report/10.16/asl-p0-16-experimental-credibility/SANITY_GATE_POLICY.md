# Sanity-gate and verdict policy (P0-16, applies to P0-18 onward)

**Status:** approved 2026-10-16. Applies to every experiment planned after this document. **No historical verdict
is changed** (§6).

## 1. Two kinds of checks

| Kind | What it tests | Examples | If it fails |
|---|---|---|---|
| **Sanity gate** | Whether the *evidence pipeline* can be trusted: data, code, controls | shuffled-label control at chance; length-only control does not "work"; reproduction of a baseline output; data-integrity checks (hashes, no train/test mix) | **VOID**: nothing is interpreted |
| **Criterion** | Whether the *intervention or hypothesis* meets its goal, including safety requirements | Δ metric ≥ threshold with CI > 0; do-no-harm bounds; "the rule must not alter human references" | counts toward SUPPORTED / PARTIAL / NOT SUPPORTED per the verdict table |

The plan must label every check as one or the other.

A safety requirement on the intervention, such as the repetition-cleanup G1 and G2 guards, is a **criterion**.
Failing one means the intervention fails; it does not mean the pipeline is broken.

## 2. Outcomes

- **Each sanity gate:** PASS or FAIL.
  - A gate that cannot be computed, or is computed on the wrong data, is a FAIL.
  - The comparison uses the unrounded value. Band boundaries are inclusive unless the plan says otherwise.
- **Experiment verdict**, one of:
  - **SUPPORTED**: every gate passes and every criterion the plan requires for SUPPORTED passes.
  - **PARTIAL**: allowed **only if the frozen plan's verdict table defines it**, with the exact combination of
    criteria. With all gates passing, it applies to exactly that combination and nothing else.
  - **NOT SUPPORTED**: every gate passes, and the criteria match neither of the above. This includes an intervention
    that abstains or fails a safety criterion.
  - **VOID**: **any sanity gate fails.** No PARTIAL, no directional claim, no headline numbers. Numbers may appear only
    in an appendix headed "descriptive, uninterpretable: sanity gate failed".

There is no other verdict word. "Promising", "mechanism-positive" and the like may describe exploratory analyses,
never a pre-registered verdict.

## 3. The plan and the code must agree

1. **Truth table in the plan.** The plan contains a complete verdict table: every combination of gates (PASS/FAIL)
   and criteria, with its verdict. Combinations may be grouped only by explicit rules, such as "any gate FAIL →
   VOID".
2. **Lookup in the code.** The scoring code implements that table as a lookup, not as hand-written `if/else`.
3. **Consistency test before the freeze.** A unit test enumerates every combination and asserts that code = plan
   table. The test file and its passing output are hashed into `FREEZE.json`. If the test is missing or failing, the
   freeze is not allowed.
4. **Prose loses.** If the prose ever disagrees with the table, the table governs and the disagreement is reported
   as a protocol deviation.

**Reference implementation:** `scripts/verdict_policy.py` provides:
- `verdict()`: gates → VOID; ordered SUPPORTED / PARTIAL rules; otherwise NOT SUPPORTED. Rejects any other verdict
  word, any undefined criterion, and a plan with no gate.
- `null_gate()`: at least 20 seeds, median, inclusive band, unrounded.
- `truth_table()` and `assert_plan_matches_code()`.

`scripts/test_verdict_policy.py` checks this file against the rules above (39 checks, all passing). It covers:
- VOID on any gate failure, including a gate that could not be computed;
- PARTIAL only where defined;
- a full 32-combination plan-code comparison, with the P0-14 pattern detected as a mismatch;
- the P0-14 pattern → VOID and the P0-15 pattern → NOT SUPPORTED;
- null-gate seed count, boundaries and rounding (0.53017 is outside [0.47, 0.53]).

P0-18 and P0-19 should import these functions, or copy them unchanged with their tests.

## 4. How null controls must be designed

The P0-14 lesson: one permutation compared with a narrow fixed band is too fragile.
- **Null distribution.** A null control (shuffled labels, random features) is evaluated over **at least 20 seeds**.
  The pre-registered statistic is the **median** (or mean) across seeds.
- **Expected band.** The band comes from the expected chance-level variability, written down before any real number
  exists. Example: "median shuffled macro-AUROC in [0.45, 0.55] across 20 permutations".
- **Within-concept permutation.** When several labels are permuted, each label column is permuted independently.
  One shared row permutation makes the per-label controls dependent.
- **Abstaining controls pass.** For "the control must not succeed" gates (P0-15 N1 and N2 style), a control that
  abstains passes.

## 5. After a gate fails

- **No re-running.** Do not re-run, re-seed, widen or redefine the gate. Do not swap in a different control.
- **Diagnostics are separate.** Diagnostics may be run and reported in a separate, clearly labelled section, and the
  verdict stays VOID.
- **A repaired pipeline is a new experiment.** It needs a new plan and fresh confirmatory data, or else it is
  labelled exploratory.

## 6. Historical verdicts under this policy (record only, nothing is changed)

| Experiment | Recorded verdict | Under this policy | Note |
|---|---|---|---|
| **P0-14** | **PARTIAL SUPPORT** (kept) | would be **VOID** | See `EXPERIMENT_PROTOCOL.md` §5 H1. The plan's prose said an S1 failure means "nothing is interpreted"; the frozen code returned PARTIAL. Also, the plan defined PARTIAL as "C1 and C2 pass but at least one of C3–C6 fails", while all of C1–C6 passed, so the PARTIAL label matches neither the prose nor the plan's own PARTIAL definition. It is the code's output. Read P0-14 as **exploratory evidence**: the effects are large and far from the control, but they are formally unconfirmed. |
| **P0-15** | **NOT SUPPORTED** (kept) | NOT SUPPORTED | N1 and N2 passed (all abstained). The primary arm abstained, so P1 failed. Consistent. |
| Repetition cleanup | negative result, metrics not computed (kept) | NOT SUPPORTED | G1 and G2 are safety criteria (§1), so this is consistent. |
| Chunked decoding | no arm passes; T4 failed (kept) | NOT SUPPORTED | The U36 reproduction gate passed. Consistent. |
| Decode-length cap | hypothesis rejected (kept) | NOT SUPPORTED | R100 reproduced the committed outputs byte for byte. Consistent. |
| P0-12 / error taxonomy | diagnostic, no pre-registered verdict (kept) | n/a (exploratory) | |
