# P0-16: Experimental protocol and credibility audit

**Date:** 2026-10-16 · **Branch:** `baobao/visual-production-research-2026-10-05` · **Status: approved and
frozen.** No experiment was run for P0-16. No historical verdict or committed report was edited.

## 0. Decisions in force (approved 2026-10-16)

1. **Old conclusions are not rewritten.** Every recorded verdict and committed report stays as it is. This document
   records inconsistencies; it does not correct history.
2. **P0-14 stays PARTIAL SUPPORT, and is treated as exploratory evidence** under the new policy, under which it
   would be VOID (H1).
3. **The P0-15 final half is retired from confirmatory use.** It may be used for development in future
   experiments. P0-15 stays **NOT SUPPORTED**. The "sealed / reusable once" wording in `P0_15_RESULTS.md` and
   `UNISIGN_P0_MANAGER_SUMMARY.md` is **superseded by P0-16** (H2).
4. **All previous Uni-Sign work is exploratory or validation-level, not confirmatory.** That covers P0-11 through
   P0-15, the error taxonomy, decode length, repetition cleanup and chunking.
5. **H18 and H19 are the new confirmatory holdouts**: H18 (814 clips / 57 source videos) only for P0-18's one-shot
   evaluation, H19 (829 clips / 58 source videos) only for P0-19's. Before its run, no frames, references, labels or
   model outputs of a holdout may be inspected by development scripts. The holdout guard stays active
   (`HOLDOUT_PLAN.md` §4–§5).

**Companion files:**

| File | Contents |
|---|---|
| `DATA_USE_LEDGER.csv` | one row per (data subset, experiment) |
| `CLIP_STATUS.csv` | per-clip status of all 2,357 How2Sign test and 1,741 val clips |
| `ledger_summary.json` | headline overlap counts |
| `SANITY_GATE_POLICY.md` | the gate and verdict rules |
| `HOLDOUT_PLAN.md` | the new confirmatory holdout |
| `holdout/` | frozen holdout ID lists and hashes |
| `scripts/` | how all of the above were built; `verdict_policy.py` + `test_verdict_policy.py` implement and test the gate policy; `holdout_guard.py` is the deny-list |

## 1. Goal

1. Make the protocol internally consistent.
2. Record honestly which data have already been seen.
3. Freeze a confirmatory holdout that P0-18 and P0-19 can use, which no earlier work has observed.

## 2. Data roles

Every clip used from P0-18 on has exactly one role at any time. The roles only move down this list, never up.

| Role | Meaning | May be used for |
|---|---|---|
| **Training-only** | the model under study was trained on it (How2Sign train → Uni-Sign) | fitting probes, verifiers and preprocessing parameters. **Never** as evidence of translation quality |
| **Exploratory** | references and/or predictions were inspected per clip, or the data generated hypotheses | anything in development. Results are hypotheses |
| **Validation-used** | evaluated before in aggregate or under a pre-registered rule, so it has shaped later designs | development and tuning, and descriptive reporting. **Not** confirmatory |
| **Confirmatory (sealed)** | never decoded, no per-clip or aggregate model output seen, frozen ID list | **one** pre-registered evaluation, after which it becomes validation-used |

## 3. Audit result (`DATA_USE_LEDGER.csv`, `CLIP_STATUS.csv`)

| Data | Clips / videos | Used by | Status now |
|---|---|---|---|
| How2Sign train | 31,086 + 79 / 2,192 | Uni-Sign fine-tuning (upstream); P0-11/P0-13 training (incl. their 366-clip "val"); P0-14 probes and concept selection | training-only |
| Test: pilot 19 + v2 benchmark 128 = frozen 147 | 147 / 128 | pilot, 9.2 baseline, E0, P0-11, P0-12, P0-13, taxonomy, decode length, repetition cleanup, P0-14 (inside test_clean) | **exploratory** |
| Test: chunking pilot | 36 (⊂ 128) | chunked decoding | **exploratory** |
| Test: test_clean | 2,209 / 149 | P0-14 (all decoded; aggregate and per-concept analysis), P0-15 | dev 1,052 = exploratory; other 1,157 = validation-used |
| Test: P0-15 final half | 1,157 / 74 | label counts only in P0-15; all in P0-14; 66 clips are 128-benchmark clips | **validation-used**: unopened *for P0-15*, but **previously observed** |
| Test: dup-excluded / no official pose | 140 / 8 | P0-14 text screening | excluded |
| **How2Sign val** | **1,741 / 115** | only P0-14 aggregate reference counts. Never decoded, no poses, never used upstream (Uni-Sign's How2Sign dev path is empty) | **confirmatory-eligible** → new holdout |

Video-level contamination of How2Sign test:
- **128 of its 149 source videos** contain at least one clip whose reference and prediction were inspected one by
  one. That covers 2,045 of the 2,357 test clips.
- The remaining 21 videos (290 clean clips) were all in P0-14's aggregate analysis.

**No How2Sign test clip is eligible for confirmatory use.**

## 4. Rules for every P0 from now on

1. **Declare data roles before running.** Each plan states which ledger rows it tunes on, which it reports
   descriptively, and which (if any) it evaluates once. The ledger is updated after every P0.
2. **Tune only on training-only, exploratory or validation-used data.** Confirmatory IDs are on a deny-list. Every
   development script must call the holdout guard (`HOLDOUT_PLAN.md` §5).
3. **Confirmatory data are one-shot:**
   - plan, code and `FREEZE.json` (thresholds, weights, code hashes, the plan-code verdict test) are committed first;
   - the evaluation script writes a lock file before it loads any confirmatory reference or produces any output;
   - it runs once;
   - the set then becomes validation-used.
4. **Gates and verdicts follow `SANITY_GATE_POLICY.md`:** a gate failure means VOID; PARTIAL exists only if the
   plan's table defines it; the plan and the code are tested for agreement before the freeze.
5. **Reporting language:**
   - "**unopened for P0-x**" (not evaluated in that experiment) is different from "**never previously observed**"
     (no earlier work saw any reference or output of it, per the ledger);
   - "held-out" or "confirmatory" may only describe data whose ledger status was confirmatory at the time of the run;
   - "clean" must say clean of *what*: model training, our inspection, or near-duplicates.
6. **Multiplicity and noise:** state the number of conditions, runs and comparisons. A single run with no CI is
   labelled "point estimate, single run".
7. **Near-duplicates:** confirmatory sets exclude exact and near duplicates (P0-14 rule) of training references
   **and** of all development references. Videos that share a sentence are merged into one unit.

## 5. Historical inconsistencies (documented, not rewritten)

No verdict is withdrawn. Each item states its effect on the recorded conclusions.

| # | Issue | Effect on recorded conclusion | Action |
|---|---|---|---|
| **H1** | **P0-14 S1 gate: the plan and the code disagree.** The plan's prose (§9) says an S1 failure means "the pipeline is broken and nothing is interpreted". The frozen `analyze_probe.py` withholds only STRONG and returns PARTIAL. The plan's own PARTIAL definition ("C1 and C2 pass, at least one of C3–C6 fails") also does not match: all of C1–C6 passed. S1 missed by 0.0002 (0.53017 vs 0.53), with a single shared-row permutation. | Verdict stays **PARTIAL SUPPORT** as recorded. Under the new policy it would be VOID. P0-14's findings are **exploratory evidence**: the mT5 > Fsign > raw ordering and AUROC 0.78 on misses are large effects far above the control, but they are formally unconfirmed. | Disclosed in `FULL_RUN_REPORT.md` §4.1 already; recorded here. New policy §3–§4 prevents a repeat |
| **H2** | **The P0-15 "sealed" final half had already been observed.** All 1,157 clips were in P0-14's aggregate analysis, which P0-15 plan §10 disclosed. **Not disclosed there:** 66 of its clips (66 of its 74 videos) are 128-benchmark clips whose references and predictions were inspected in P0-12, the taxonomy and later work, and 73 are in the frozen 147. `P0_15_RESULTS.md` and `UNISIGN_P0_MANAGER_SUMMARY.md` call it "sealed … reusable once". | P0-15 verdict **NOT SUPPORTED is unaffected**: it was decided on dev, and final was never opened. The "reusable once" statement is **superseded by P0-16**: the P0-15 final half is **retired from confirmatory use** (validation-used). It may be used for development. | Approved 2026-10-16; earlier reports not edited |
| **H3** | **P0-14's evaluation set contains the hypothesis-generating clips.** test_clean includes 127 of the 128 benchmark clips and 145 of the 147, which generated earlier hypotheses. P0-14 and P0-15 split by video but did not consider video overlap with the benchmark. | Small for P0-14: probe comparisons over 2,209 clips; the 128 are 6 % of them. No change. | Covered by the new holdout |
| **H4** | **The 128-clip benchmark served as discovery and as evaluation.** It was used for diagnosis (P0-12), hypothesis generation (taxonomy) and then the decode-length, cleanup and chunking evaluations. The chunking thresholds were frozen before its GPU runs, but on the clips that suggested the hypothesis. | These results are exploratory, as `UNISIGN_FAILURE_ANALYSIS_SUMMARY.md` already says ("no re-tuning on these clips"). The 128 were also deliberately skewed toward hard clips (E0), so they are not a representative sample. | Recorded |
| **H5** | **"Clean" was used without saying clean of what.** P0-11 and P0-13 call the frozen 147 "clean". That is true only with respect to Uni-Sign training; the clips had been inspected per clip before. | Wording only. P0-13's comparison was between two arms on the same clips. | Rule 4.5 |
| **H6** | **P0-15's split balance read final label counts.** | Disclosed in P0-15 plan §10. No effect. | — |
| **H7** | **The test-set signer proxies all occur in train, except proxy 10.** Val's signer proxies (1, 2, 3, 5, 8) all occur in train. | No experiment tests unseen signers; already stated as a caveat. | Stated in `HOLDOUT_PLAN.md` |

## 6. What this means

- **Nothing is withdrawn:**
  - P0-12's diagnosis stands as a single-run T4/fp16 comparison;
  - the error taxonomy stands as weak-label hypotheses;
  - decode length, cleanup and chunking stand as rejected or failed;
  - P0-14 stands as PARTIAL SUPPORT, best read as exploratory;
  - P0-15 stands as NOT SUPPORTED.
- **Superseded:** the claim that the P0-15 final half is a reusable sealed holdout.
- **Every result so far is exploratory or validation-level.** No result in the Uni-Sign line so far is
  confirmatory. The first confirmatory evaluations will be P0-18 on H18 and P0-19 on H19.
