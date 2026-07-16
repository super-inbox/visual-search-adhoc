# automated_relevance_summary.md
Generated: 2026-07-16T07:23:55Z

Total queries: 328 (328/328 evaluated)

## Label distribution
- PASS: 93 (28.35%)
- PARTIAL: 106 (32.32%)
- FAIL: 129 (39.33%)
- UNJUDGABLE: 0 (0.0%)

Mean relevance_score: 34.54 | Median: 23.0 | P25: 0.0 | P75: 64.0

Confidence: {'HIGH': 13, 'MEDIUM': 299, 'LOW': 16}

needs_manual_review: 171 | zero_result: 12 | low_result: 43

Rewrite observed: 138 -> {'PARTIAL': 42, 'FAIL': 62, 'PASS': 34}
Non-rewrite: 190 -> {'PARTIAL': 64, 'FAIL': 67, 'PASS': 59}

Calibration label agreement: 100.0% (30/30 queries)
Second-pass (tier1 deep-reverify 54 + tier3 random-PASS-audit 10 = 54) label agreement: 83.33% (45/54); 4 label flips (all PASS->PARTIAL) after adjudication.
