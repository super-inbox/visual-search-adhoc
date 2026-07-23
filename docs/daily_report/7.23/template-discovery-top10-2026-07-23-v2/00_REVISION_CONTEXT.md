# Revision Context — Template Discovery Top 10 V2 (2026-07-23)

## What this is
A targeted correction and visual-evidence enhancement of the existing Curify Template Discovery Top-10 package.
This is **not** a re-run of Template Discovery from scratch and **not** a re-run of the Task A 326-query benchmark.

- **Source package (unmodified, preserved as working input)**: `docs/daily_report/7.23/template-discovery-top10-2026-07-23/`
- **Primary Task A benchmark source (read-only, not re-run)**: `docs/daily_report/7.22/cluster-ab-latest-fix-full326-2026-07-22/`
- **Tested frontend commit**: `0e794cd91396a96cd56fd1d8f7f1495909f3adc5`
- **This output directory**: `docs/daily_report/7.23/template-discovery-top10-2026-07-23-v2/`
- A verbatim copy of the v1 package was placed in `working_input_v1/` inside this directory as a working
  reference only; it is not part of the deliverable set and was never modified in place.

## Why this revision
Five issues were identified in the v1 package by manager review:
1. Recommendation cards didn't clearly separate "Curify's current gap" from "what the recommended template should
   look like" — most cards showed only Curify screenshots or a generic "no competitor evidence" placeholder.
2. Displayed rank order was inconsistent with a documented ranking rule — two pairs of candidates were ordered by
   raw/adjusted score alone, ignoring CONFIRMED-vs-PROVISIONAL status.
3. The manager summary overgeneralized "zero/low results at every historical timepoint" to all 10 candidates, when
   several are PARTIAL-coverage cases (never fully zero) rather than CONFIRMED zero-everywhere cases.
4. Puzzle's English-language zero-result was being used as if it were confirmed content-gap evidence, when it is
   better explained as a candidate-build/regression artifact distinct from the Chinese-language signal.
5. Coupon's Chinese/English discrepancy needed a documented, evidence-based explanation rather than an implicit
   asymmetric treatment.

## What changed in V2
See `01_CURRENT_PACKAGE_AUDIT.csv` for the full file-by-file, issue-by-issue diff. In summary:
- **Ranking rule formalized and applied**: Priority (P0>P1>P2) > Status (CONFIRMED>PROVISIONAL) > Evidence-Adjusted
  Score (desc) > Candidate ID (tie-break). Two rank swaps resulted: T05 (Price Tag) now outranks T01 (Certificates)
  within P1 CONFIRMED; T08 (Puzzle) now outranks T09 (Coupon) within P2 PROVISIONAL. All other ranks were already
  consistent with this rule and are unchanged.
- **Score labels disambiguated**: every file now uses `raw_opportunity_score`, `evidence_adjusted_score`,
  `evidence_completeness_pct`, and a `ranking_rule` field/column — no bare "Score" column remains.
- **Manager summary corrected**: replaced the "zero/low at every historical timepoint" overgeneralization with
  language distinguishing CONFIRMED (content completely absent at every timepoint) from PARTIAL (adjacent/general
  content exists, specific sub-type is what's missing) candidates.
- **Puzzle clarified**: 拼图 (ZH) is the sole basis for T08's content-gap justification; English "puzzle"'s
  zero-result is explicitly excluded (it is STILL_ZERO vs production, not a regression from a working baseline —
  its only nonzero data point was itself irrelevant travel-landmark filler).
- **Coupon clarified**: "discount coupon" (EN) is the sole basis for T09's content-gap justification; 优惠券 (ZH)
  is explicitly excluded (production was zero in both languages; the ZH-only nonzero data point was itself
  irrelevant mythology/demographics filler, ruling out "content exists but Chinese retrieval fails").
- **Repository image search expanded**: found 1 new real adjacent-competitor image (T03, Canva phonics-worksheets),
  re-verified and included 1 previously-excluded adjacent image (T06, tea gift-box Pinterest), added 6 new
  Curify-gap/context screenshots, and surfaced 2 important honest caveats (T04 "event flyer" shows partial
  content; T03/T05 adjacent queries show relevant content exists outside the exact gap scope). No exact-match
  competitor image was found for any of the 10 candidates.
- **Cards regenerated**: all 10 cards now show three labeled panels — CURIFY CURRENT GAP, REFERENCE EXAMPLE
  (exact/adjacent/needed), RECOMMENDED VISUAL DIRECTION (a text/spec panel, explicitly labeled "not a photograph") —
  plus both score fields, ranking basis, and reference-image status.
- **Contact sheet regenerated** with corrected ranks and a footer explaining the ranking rule and the 6 remaining
  reference-image gaps.
- **Neither the 10-candidate list, nor any candidate's priority/status, nor any raw/adjusted score was changed**
  except where explicitly noted above (Puzzle/Coupon wording) — the underlying scores were re-verified, not
  recalculated, and no calculation error was found.

## What this revision did NOT do
- Did not rerun the Task A 326-query benchmark (all evidence is read from `docs/daily_report/7.22/.../`, read-only).
- Did not modify any file under `docs/daily_report/7.22/` or any other historical daily-report directory.
- Did not modify frontend source code.
- Did not create a git commit, push, or PR.
- Did not overwrite the v1 package (`docs/daily_report/7.23/template-discovery-top10-2026-07-23/` is untouched).
- Did not add `map` or `flashcard` back as content gaps — both remain excluded as search regressions.
- Did not fabricate any competitor image, source URL, or benchmark evidence. Six candidates remain honestly
  labeled "REFERENCE IMAGE NEEDED."
