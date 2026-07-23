# Scoring Method — Template Candidate Prioritization

Each of the 10 pool candidates is scored on a 100-point raw rubric, then adjusted by an evidence-completeness
multiplier to produce the final ranking. This penalizes candidates whose evidence is thin (e.g. a single
supporting query, no competitor evidence, no cross-validation) relative to candidates with deep, cross-validated
support -- so that the Top-10 order reflects confidence, not just raw opportunity size.

## Raw rubric (100 pts)
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
regression-50), and competitor evidence (image or text). Candidates with only 1 supporting query and no competitor
evidence (T09, T10) score 33%; candidates with full historical + cross-validated + competitor evidence (T03, T04,
T07) score 100%.

`confidence_adjusted_score = raw_total_100 * evidence_completeness_pct / 100`

## Why this reorders the raw ranking
T02 (STEM classroom teaching aids) has the highest raw score (80) but ranks #3 after adjustment (66.4) because its
competitor evidence is NOT_FOUND. T03 (workbook) and T04 (flyer) have slightly lower raw scores (86, 85) but full
evidence completeness, so they rank #1 and #2. This is intentional: the ranking rewards candidates the team can
defend with complete, traceable evidence over candidates that are merely high-severity but thinly documented.

## Priority banding (P0/P1/P2)
- **P0**: confirmed content gap, HIGH confidence, cross-validated or fully evidence-complete (T02, T03, T04)
- **P1**: confirmed or partial gap, HIGH-to-MEDIUM confidence, single-methodology evidence (T01, T05, T06, T07)
- **P2**: partial/weaker-evidence gap, MEDIUM-to-LOW confidence, single supporting query (T08, T09, T10)
