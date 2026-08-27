# Inspiration Candidate Quality Rubric — Summary

## What was formalized

We've been grading inspiration candidates A/B/C across several pilots (8.8, 8.14), but the
grading logic only ever existed as an in-the-moment human judgment call — no written
definition, no way to reproduce a grade later or check two reviewers agree. This task turned
that heuristic into a fixed, versioned rubric (`RUBRIC.md`), a reusable scoring template
(`RUBRIC_TEMPLATE.csv`), and a calibration set proving the rubric reproduces real prior grades
(`CALIBRATION_EXAMPLES.csv`), all grounded in our existing evaluation data — no invented
criteria.

## Current dimensions (each scored 0–2)

1. **Query Relevance** — does the candidate actually match the query's subject/format/intent?
2. **Design / Source Evidence** — how much real design detail is shown (process, system,
   stated rationale) vs. a single bare finished image?
3. **Attribution / Context Completeness** — is there a named, trustworthy creator, and is that
   attribution independently verifiable (not just self-stated)?

## How A/B/C is assigned

Deterministic, not another judgment call: sum the three 0–2 scores (0–6 range).

- Any hard-fail (blocked source, no thumbnail, unverified marketing claim stated as fact,
  attribution to a re-poster not the real designer, exact duplicate) → **C**, always.
- Any single dimension scoring 0 → **C**, regardless of the sum (one real failure isn't
  averaged away by the other two).
- Otherwise: sum 5–6 → **A**, sum 3–4 → **B**, sum 0–2 → **C**.

Checked against 11 real candidates pulled from the 8.8 pilot data: the rubric reproduces every
prior grade **except two**, where it's intentionally *stricter* than the old informal pass —
one certificate candidate was previously graded A but drops to B once "independently verified"
is actually enforced for a top attribution score; another was previously graded B but drops to
C once the rubric formally treats "credited party is a recipient, not the designer" as a
hard-fail. Both deltas are the kind of inconsistency this rubric exists to catch.

## Status

**v1.0**, dated 2026-08-19. This is a human evaluation rubric — reviewers apply it by hand,
nothing here is an automatic/model score. It's built to be iterated: every future change gets a
new versioned entry in `RUBRIC.md`, and any change that would flip a calibration example's
grade requires regenerating the calibration set in the same change, so the rubric and its
worked examples never drift apart.

Full detail: `RUBRIC.md`, `RUBRIC_TEMPLATE.csv`, `CALIBRATION_EXAMPLES.csv`, `README.md` in
`docs/daily_report/8.19/inspiration-quality-rubric/`.
