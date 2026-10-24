# ASL daily report — 2026-10-23: P0-A / P0-B / P0-C setup

**Status (updated 2026-10-24): P0-A STOP / NOT ENOUGH CANDIDATE HEADROOM. P0-B and P0-C pending.**
- P0-A: local CPU fp32 candidate decode (45 cases × 2 domains, run twice, identical) and automatic headroom check only
  ([RESULTS.md](p0a-candidate-rerank/RESULTS.md)). No rerank, no training, no GPU or VM use.
- P0-B / P0-C: setup only, nothing decoded.
- H18/H19 not opened. The frozen protocol is unchanged.
- Historical reports stay in `docs/daily_report/` and are linked below, not moved.

**Source of truth:** [2026-10-21 boss report — Uni-Sign case review and P0 plan](../2026-10-21/UNISIGN_CASE_REVIEW_AND_P0_PLAN.md).
**Canonical index:** [asl-translation-mvp-spec.md](../../asl-translation-mvp-spec.md) (§18) and the
[2026-10-20 retrospective](../../asl-research-retrospective-2026-10-20.pdf).
**Frozen protocol:** [P0_PROTOCOL_FREEZE.md](P0_PROTOCOL_FREEZE.md).

## The three P0s

| P0 | Question | Plan | Status (2026-10-24) |
|---|---|---|---|
| **P0-A** (first) | Is a better sentence already among Uni-Sign's candidates but not chosen as top-1? | Candidate upper bound (≤ 5 candidates, oracle kept separate) → simple reference-free rerank (loop-aware, model score) → + P0-14 mT5 out-of-fold probe as a ranking aid only. Arms T / R1 / R2. | **STOP after headroom check: insufficient candidate upper bound** ([RESULTS.md](p0a-candidate-rerank/RESULTS.md)). The reference-based oracle-in-pool raises corpus chrF by only +2.24 (A_official, deciding) / +2.26 (B_ours_5p39), below the frozen +3.0 (§1.7 rule 1a). No simple rerank or probe rerank is run. The blinded human candidate review (`candidate_review.csv`) is optional diagnostic evidence and cannot change the verdict. |
| **P0-B** (parallel, feasibility) | Does hand RGB carry recoverable letters for fingerspelled names (R02, R05, R35)? | An ASL-fluent reviewer confirms spans in the matched windows (blind, then unblinded) → recognizer survey → character/name metrics → guarded local replacement. | **Feasibility pending an ASL-fluent reviewer.** Request and blank label sheet ready ([FEASIBILITY.md](p0b-fingerspelling-feasibility/FEASIBILITY.md)). Nothing run. |
| **P0-C** (after P0-A setup) | Does a human-corrected input (rest, framing, context) recover meaning? | R10 / R26 / R29 / R35: original vs one video-defined correction, same model. | **Input-correction diagnostics pending** ([CASE_SHEET.md](p0c-input-correction/CASE_SHEET.md)). R26 and R29 are ready for source checks. R10 is blocked on a timing-source conflict and rest labels. R35 is blocked on P0-B. No corrected input built, nothing decoded. |

**Not done here:**
- the P0-19 2,209-clip GPU Stage 0 (still frozen, unrun; P0-A is not a P0-19 start);
- decode-cap, deduplication or chunking reruns;
- uniform window widening;
- any H18/H19 access.

## Key setup findings

- The page video in the inspection sheet is the **original-timing** clip (= the "Our / old" input). For R15, R40,
  R42, R26, R35 and others, the **official input window does not overlap it** (IoU 0–0.02). Visual claims about the
  official output need matched windows.
- R10 has 608 frames. Uni-Sign randomly keeps 256, so the per-clip seed rule is frozen.
- The P0-14 mT5 probe has video-grouped out-of-fold scores for all test_clean clips, so P0-A's probe arm needs
  **no training**. It is valid only on official-pose inputs (domain D-A).

## Files

```
2026-10-23/
├── README.md
├── P0_PROTOCOL_FREEZE.md
├── p0a-candidate-rerank/
│   ├── RESULTS.md                       # P0-A verdict: STOP / not enough candidate headroom
│   ├── PROVENANCE.md
│   ├── case_list.csv                    # 6 focus + R41 + 6 hash-selected ordinary controls + 32 decode-only
│   ├── provenance/case_provenance.csv   # 45 rows: windows, P0-12 pkl paths, sha checks, frame counts
│   ├── provenance/provenance_summary.json
│   ├── runs/full45/<domain>/run1/       # canonical CPU fp32 candidate decode
│   ├── runs/full45/DETERMINISM.json     # run1 vs run2 identical 45/45 per domain (run2 kept local)
│   ├── headroom/                        # headroom_by_case.csv, headroom_summary.json, HEADROOM_RESULTS.md
│   ├── candidate_review.csv             # blinded human sheet (optional diagnostic; blank)
│   └── scripts/                         # build_provenance.py, decode_candidates.py, headroom_oracle.py, determinism_summary.py
│   (review_key/ — the unblinding key — stays local and uncommitted until the human review is filled)
├── p0b-fingerspelling-feasibility/
│   ├── FEASIBILITY.md
│   ├── asl_reviewer_request.md
│   └── interval_labels.csv              # blank, filled by the reviewer only
└── p0c-input-correction/
    ├── CASE_SHEET.md
    └── case_inputs.csv
```

## Earlier work this builds on (linked, not moved)

| Artifact | Used for |
|---|---|
| [P0-12 results](../../../docs/daily_report/10.13/asl-p0-12-full128-fp16/P0_12_RESULTS.md); [P0-12 prepared inputs manifest](../../../docs/daily_report/10.06/asl-p0-12-unisign-pose-gap/artifacts/prepared_inputs/MANIFEST.csv) | Exact P0-A inputs (A_official, B_ours_5p39) and stored T4/fp16 outputs |
| [10.13 error taxonomy](../../../docs/daily_report/10.13/asl-unisign-error-taxonomy/ERROR_ANALYSIS_REPORT.md) (`inputs_128.jsonl`) | Frozen 128 membership, references, stored predictions |
| [P0-14 full run](../../../docs/daily_report/10.15/asl-unisign-representation-probe/FULL_RUN_REPORT.md) | mT5 probe and Tier L concept matcher for R2 |
| [P0-15 results](../../../docs/daily_report/10.16/asl-unisign-high-precision-fusion/P0_15_RESULTS.md) | Why concepts are never appended (naive union net −231) |
| [P0-16 holdout plan](../../../docs/daily_report/10.16/asl-p0-16-experimental-credibility/HOLDOUT_PLAN.md) | Holdout guard; H18/H19 sealed |
| [P0-18 development results](../../../docs/daily_report/10.16/asl-p0-18-auto-preprocessing/DEVELOPMENT_RESULTS.md) | P0-C limits (timing is the gap; widening hurts WER); `pose_extract.py` |
| [P0-19 safe-rerank plan](../../../docs/daily_report/10.20/asl-p0-19-safe-rerank/EXPERIMENT_PLAN.md) | `decode_topk.py` / `p019_common.py` to adapt for P0-A (Stage 0 itself not run) |
| [45-case inspection sheet](../../../docs/daily_report/10.18/asl-review-inspection-sheet/README.md); [repetition audit](../../../docs/daily_report/10.18/asl-review-inspection-sheet/repetition_audit.md) | Case IDs, page videos; loop cases and the old repetition flag |
| [Model review comparison](../../../docs/daily_report/10.19/asl-model-case-analysis/MODEL_REVIEW_COMPARISON.md); [Codex case analysis](../../../docs/daily_report/10.19/asl-model-case-analysis/CODEX_CASE_ANALYSIS.md) | Case hypotheses (not accuracy, not ASL verification) |
| [10.19 work report](../../../docs/daily_report/10.19/asl-work-report/WORK_REPORT.md) | Prior status of all lines |
| [45-video release](https://github.com/super-inbox/visual-search-adhoc/releases/tag/asl-review-package-2026-10-19) | Page videos (CC BY-NC 4.0, not committed) |
