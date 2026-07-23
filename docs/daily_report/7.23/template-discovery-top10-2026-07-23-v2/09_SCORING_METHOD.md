# Scoring Method — Template Candidate Prioritization (V2, revised 2026-07-23)

Each of the 10 pool candidates is scored on a 100-point raw rubric (`raw_opportunity_score`), then adjusted by an
evidence-completeness multiplier to produce `evidence_adjusted_score`. This penalizes candidates whose evidence is
thin (e.g. a single supporting query, no competitor evidence, no cross-validation) relative to candidates with
deep, cross-validated support.

**V2 correction:** the v1 package used a single ambiguous column named `confidence_adjusted_score`/"Score" across
files, and used only the evidence-adjusted score (ignoring status) to sort within a priority band. This produced
inconsistent ranks (e.g. a CONFIRMED P1 candidate with a lower score outranking a CONFIRMED P1 candidate with a
higher score; a PROVISIONAL P2 candidate outranking another PROVISIONAL P2 candidate with a stronger score). See
`00_REVISION_CONTEXT.md` and `01_CURRENT_PACKAGE_AUDIT.csv` for the full before/after diff.

## Raw rubric (100 pts) — unchanged from v1
| component | max pts | basis |
|---|---|---|
| `demand_25` | 25 | Number and cross-language/cross-version repetition of supporting queries; frequency in the 326-query bank |
| `severity_25` | 25 | How completely absent the content is (zero-result & persistently-irrelevant-top5 scores highest; partial/declining coverage scores lower) |
| `vertical_20` | 20 | Whether the surrounding Task A vertical (10_VERTICAL_SUMMARY.csv) is broadly weak (low PASS rate), supporting that this is a systemic catalog gap rather than an isolated query quirk |
| `competitor_15` | 15 | Strength and directness of competitor evidence (image > text-only > adjacent-category > NOT_FOUND) |
| `scalability_10` | 10 | How many distinct template variants a single design investment could produce |
| `feasibility_5` | 5 | Production complexity (flat layout = easy; 3D mockup/product photography = harder) |

## Evidence-completeness adjustment
`evidence_completeness_pct` scores what fraction of the ideal evidence bundle is actually on file for a candidate:
multiple independent benchmark rounds, a 7/17 live screenshot, cross-validation from a second methodology (e.g.
regression-50), and competitor evidence (image or text).

`evidence_adjusted_score = raw_opportunity_score * evidence_completeness_pct / 100`

Field names used consistently across all V2 files: `raw_opportunity_score`, `evidence_adjusted_score`,
`evidence_completeness_pct`. No file uses a bare, ambiguous "Score" column.

## Ranking rule (V2 — explicit, applied uniformly across all files)
Final rank = sort by, in this exact order:
1. **Priority**: P0 before P1 before P2
2. **Status**: CONFIRMED before PROVISIONAL, within the same priority
3. **Evidence-Adjusted Score**: descending, within the same priority and status
4. **Candidate ID**: ascending, as the final tie-breaker (not needed in this run — no ties occurred)

This is stricter than v1's implicit rule (which sorted by priority band, then by evidence-adjusted score alone,
without a documented status step) — the status step is what corrects the two ranking errors found in v1 (see
`01_CURRENT_PACKAGE_AUDIT.csv`).

## Why this reorders the raw ranking
T02 (STEM classroom teaching aids) has the highest raw score (80) but ranks #3 after adjustment (66.4) because its
competitor evidence is NOT_FOUND. T03 (workbook) and T04 (flyer) have slightly lower raw scores (86, 85) but full
evidence completeness, so they rank #1 and #2. Within P1, T05 (Price Tag, CONFIRMED, 62.2) now correctly outranks
T01 (Certificates, CONFIRMED, 50.2); both outrank T07 (Perfume, PROVISIONAL, 71.0) and T06 (Chocolate, PROVISIONAL,
43.5) despite T07's higher raw and evidence-adjusted score, because status is applied before score. Within P2, T08
(Puzzle, 29.5) now correctly outranks T09 (Coupon, 20.1).

## Priority banding (P0/P1/P2) — unchanged from v1
- **P0**: confirmed content gap, HIGH confidence, cross-validated or fully evidence-complete (T02, T03, T04)
- **P1**: confirmed or partial gap, HIGH-to-MEDIUM confidence, single-methodology evidence (T01, T05, T06, T07)
- **P2**: partial/weaker-evidence gap, MEDIUM-to-LOW confidence, single supporting query (T08, T09, T10)
