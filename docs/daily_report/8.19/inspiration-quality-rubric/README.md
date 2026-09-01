# Inspiration Candidate Quality Rubric

## What this is

A fixed, reusable A/B/C grading rubric for **inspiration candidates** — the images/case-study
pages sourced for a specific query as potential Curify inspiration content. Grading has been
done for several weeks across multiple pilots, but always as an informal, per-session judgment
call with no written definition of what separates an A from a B from a C, and no rule for how
partial evidence should combine into an overall grade. This directory formalizes that judgment
call into a fixed procedure (`RUBRIC.md`) plus the templates needed to apply and re-check it
(`RUBRIC_TEMPLATE.csv`, `CALIBRATION_EXAMPLES.csv`).

## Where it came from

The rubric's three dimensions and scoring anchors are reverse-engineered from how A/B/C grades
were actually assigned in three prior evaluation artifacts, not invented from scratch:

- `docs/daily_report/8.8/inspiration-source-pilot/SOURCE_QUALITY_REVIEW.csv` — the richest
  prior record: 47 candidates each with an `automated_quality` (A/B/C) grade alongside
  `authority_signals`, `originality_signals`, `content_depth`, `visual_relevance`,
  `traceability`, and `recommended_long_term_role` fields. This is the primary source for the
  rubric's dimension anchors and for every worked example in `CALIBRATION_EXAMPLES.csv`.
- `docs/daily_report/8.8/inspiration-source-pilot/INSPIRATION_INTEGRATION_FINDINGS.md` — the
  narrative explanation of *why* those 47 candidates got the grades they did (point 4 and point
  5), which is where the rubric's "a well-known platform is not itself evidence" rule and the
  A-grade bar ("independently-verifiable real client, studio, or personal site, or a
  distinctive stated design rationale") come from directly.
- `docs/daily_report/8.14/inspiration-scale/run_*.py` — a later, larger pilot where A/B/C
  grades were assigned per-candidate by a human reviewer directly in code
  (`quality_score="B"`, etc.), with no rubric attached at all. This is the clearest evidence
  that the heuristic needed formalizing: the grading judgment existed only in a reviewer's head
  at the moment of assignment, with nothing written down to reproduce it later.
- `docs/daily_report/8.16/creative-direction-product-iteration/real_paired_evaluation.csv` —
  not an A/B/C source itself (it uses a 1–5 multi-dimension scale for a different, pairwise
  creative-direction evaluation), but the template for the *style* this rubric follows:
  numeric per-dimension scores plus a required rationale, so a grade is always reproducible
  from a written reason, not just a gut call.

Full grounding detail and how each example was derived is in `RUBRIC.md` §3–§6 and in the
`reviewer_notes` / `source_reference` columns of `CALIBRATION_EXAMPLES.csv`.

## How to use it

1. Read `RUBRIC.md` once, in full — it's short. Pay particular attention to §4 (the
   deterministic A/B/C rule) and §5 (hard-fail conditions), since those two sections are what
   makes the grade reproducible rather than a judgment call.
2. For a new batch of candidates, copy `RUBRIC_TEMPLATE.csv` and fill one row per candidate:
   - Score `query_relevance_score`, `design_source_evidence_score`, and
     `attribution_context_score` each 0/1/2 using the anchors in `RUBRIC.md` §3.
   - Compute `dimension_sum` (sum of the three scores).
   - Check the hard-fail conditions in `RUBRIC.md` §5; set `hard_fail` = TRUE/FALSE and fill
     `hard_fail_reason` if TRUE.
   - Derive `overall_grade` from `RUBRIC.md` §4 (hard-fail → C; any dimension = 0 → C; else sum
     5–6 → A, 3–4 → B, 0–2 → C).
   - Always fill `reviewer_notes` with the concrete evidence behind each score — an unexplained
     numeric score is not sufficient for the grade to be trusted later.
3. Before trusting a new reviewer's output (or your own after a gap), spot-check a few of their
   graded rows against `CALIBRATION_EXAMPLES.csv` — if the same evidence produces a different
   grade, that's a sign the anchors need to be re-read, not that the rubric is wrong.

## How future iterations should update/version it

- Treat `RUBRIC.md` §8 (Versioning) as the changelog. Every substantive change to the
  dimensions, anchors, hard-fail list, or the A/B/C threshold rule gets a new `## vX.Y` entry
  appended there — never edit a previously shipped version's text in place.
- If a change would flip the grade on any row in `CALIBRATION_EXAMPLES.csv`, regenerate that
  file in the same change. The calibration set exists to prove the rubric is self-consistent;
  it must never silently drift out of sync with the rubric text.
- Bump the minor version (v1.1, v1.2, …) for anchor clarifications or new ambiguous-case
  guidance that don't change how existing graded data would score. Bump the major version (v2.0)
  for changes that would re-grade a meaningful share of existing candidates (e.g., adding a
  fourth dimension, changing the 0–2 scale, or changing the sum thresholds).
- This is a **human evaluation rubric**. If a future iteration introduces automated or
  model-assisted scoring, that should be a new, explicitly-labeled artifact (e.g.,
  `RUBRIC_AUTOMATED_v1.md`) that is validated against this human rubric's calibration set before
  it replaces or supplements human grading — not a silent edit to this rubric's meaning.
