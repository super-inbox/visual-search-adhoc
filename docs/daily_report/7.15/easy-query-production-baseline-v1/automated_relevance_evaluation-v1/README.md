# automated_relevance_evaluation-v1

Automated (offline) relevance evaluation of the 328-query Curify Easy Query production baseline
collected on 2026-07-15 (`../` = `easy-query-production-baseline-v1`). This directory does not
modify, duplicate into, or overwrite any file in the parent baseline directory — see
`../AUTOMATED_RELEVANCE_EVALUATION_ADDED.md` for the pointer file added at the baseline root.

**Status: FULL_AUTOMATED_RELEVANCE_EVALUATION_COMPLETE** (328/328 queries evaluated, calibrated,
second-pass reviewed, integrity-checked). See `final/automated_relevance_integrity_report.md` and
the terminal summary in this session for the full checklist.

## Read this first

- `final/CURIFY_EASY_QUERY_AUTOMATED_RELEVANCE_REPORT_2026-07-15_zh.md` — the formal Chinese report
- `MODEL_AND_METHOD.md` — what evidence was actually used (text vs. real screenshot reads), and what wasn't done
- `RELEVANCE_RUBRIC.md` — the locked scoring rubric (rubric-v1.1)
- `CALIBRATION_REPORT.md` — 30-query calibration, 100% two-pass agreement
- `review/adjudication_report.md` — the 328-query second-pass review and its 4 label flips

## Directory structure

```
automated_relevance_evaluation-v1/
├── README.md                          (this file)
├── RELEVANCE_EVALUATION_MANIFEST.json  (run-level manifest: what ran, when, versions)
├── RELEVANCE_RUBRIC.md
├── INPUT_AUDIT.md / input_integrity.json
├── MODEL_AND_METHOD.md
├── CALIBRATION_REPORT.md / calibration_results.csv
├── WORKTREE_SAFETY_REPORT.md
├── scripts/          (01-09, deterministic data/aggregation/scoring code only)
├── batches/           (17 batches of the 328-query first pass, ~20 queries each)
├── checkpoints/       (intermediate state: master first-pass + final adjudicated datasets)
├── logs/              (consistency_audit.json)
├── evidence/           (query_packets.json: structured per-query evidence packets)
├── review/            (second_pass_review.csv, disagreement_cases.csv, adjudication_report.md,
│                        random_pass_audit.csv, automated_relevance_manual_review_queue.csv)
├── summaries/          (rewrite / zero-result / low-result专项分析)
└── final/              (18 formal deliverables — see automated_relevance_file_manifest.json)
```

## Evaluation pipeline (see `final/automated_relevance_run_log.md` for full timeline)

1. Input integrity audit (328/328 verified, no blocking issues)
2. Rubric definition and lock (rubric-v1 → v1.1, one pre-calibration clarification)
3. Evidence packet extraction (328 packets)
4. Calibration (30 queries, two independent passes, 100% label agreement)
5. First pass (328 queries, 17 batches, Claude Code direct reasoning against the locked rubric)
6. Second-pass population selection (tier1 54 / tier2 219, covering all mandatory categories)
7. Second-pass execution (tier1 deep-reverify + tier3 random-PASS audit + tier2 mechanical
   consistency audit) — 4 label flips, all documented in `review/adjudication_report.md`
8. Final adjudicated 328-query dataset built
9. All `final/` deliverables generated and integrity-verified
10. Reports (this README, the Chinese report, safety report, baseline-root pointer)

## Key numbers

PASS 93 (28.4%) / PARTIAL 106 (32.3%) / FAIL 129 (39.3%) / UNJUDGABLE 0 — mean score 34.54,
median 23.0. Full breakdown in `final/automated_relevance_summary.md`.
