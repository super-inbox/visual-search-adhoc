# Root-Cause Summary — Remaining FAIL / Regressed-PARTIAL (0e794cd9)

Full row-level classification: `12_REMAINING_FAILURE_ROOT_CAUSES.csv` (203 rows: all 195 FAIL rows + 8 PARTIAL rows
that regressed vs. production baseline). Method: automated, evidence-based heuristic over row-level fields
(`total_results`, `zero_result`, `low_result`, `rewrite_triggered`, format-word lexicon match, query shape) — **not**
manual per-query adjudication. This is disclosed inference, consistent with the established methodology's own
"disclosed inference" standard (see 7/21 `RUN_LOG.md` "Path-attribution method" section). Uncertain cases are
deliberately left in `insufficient_evidence` rather than forced into a confident bucket.

## Counts and percentages (n=203)
| root-cause category | count | % | fixable by search logic? |
|---|---:|---:|---|
| insufficient_evidence | 65 | 32.0% | Unknown — needs manual Top-5 read to classify further. |
| subject_binding_or_coverage_gap | 47 | 23.2% | **Yes** — same Cluster-A mechanism (coverage-ratio gate / isolated-hit cap), search-logic fixable. |
| rewrite_or_decomposition_issue | 28 | 13.8% | **Yes** — rewrite/decomposition path admitting off-subject content; search-logic fixable. |
| retrieval_scoring_relevance_issue | 24 | 11.8% | **Yes** — large pool, wrong-sense content outranking; scoring/ranking fixable. |
| catalog_content_gap | 16 | 7.9% | **No** — zero-result in production, previous candidate, AND latest candidate; matching content likely does not exist. Needs template discovery, not search-logic changes. |
| candidate_loss | 11 | 5.4% | **Likely yes** — sparse pool (1-4 results) despite FAIL; upstream retrieval/expansion issue. |
| partial_regression_vs_production | 8 | 3.9% | Mixed — see `08_REGRESSIONS.csv` for per-case detail. |
| candidate_loss_regression | 4 | 2.0% | **Yes, and urgent** — NEW zero-result where an earlier version had results (`diploma`, `会员卡`, `puzzle`, `优惠券`). |

## Search-relevance-fixable vs. catalog/content-gap split
- **Search-logic-fixable (subject_binding_or_coverage_gap + rewrite_or_decomposition_issue +
  retrieval_scoring_relevance_issue + candidate_loss + candidate_loss_regression): 114 / 203 (56.2%)** — the majority
  of remaining failures are, on this evidence, attributable to scorer/retrieval/rewrite mechanics rather than missing
  content.
- **Catalog/content-gap (catalog_content_gap): 16 / 203 (7.9%)** — a meaningful but minority share. These are the
  candidates for the separate template-discovery task, not further scorer tuning.
- **Insufficient evidence: 65 / 203 (32.0%)** — the largest single bucket. This is a genuine limitation of row-level
  automated classification (no Top-5 relevance read was performed at the per-query level for this bucket); flagged
  honestly rather than force-classified.

## What this means for next steps
- The `subject_binding_or_coverage_gap` bucket (47 rows, 23.2%) is the largest **actionable, already-diagnosed**
  category — it maps directly onto the Cluster-A mechanism the team already understands (coverage-ratio gate +
  isolated-hit cap), and Fix A only partially addressed it (see `11_CLUSTER_AB_OUTCOME_ANALYSIS.md`).
- `candidate_loss_regression` (4 rows) is small in count but high-urgency: these are NEW zero-result cases, not
  pre-existing gaps, and should be looked at before wider promotion regardless of the aggregate PASS-rate story.
- The `insufficient_evidence` bucket is a genuine evaluation limitation (see charter Step 16) — recommend a follow-up
  manual Top-5 read on a sample of this bucket before treating the 56.2%/7.9% split above as final.
