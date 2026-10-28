# ASL review — Step 2 (REFERENCE-CONDITIONED FOLLOW-UP)

> **This step is reference-conditioned and is intended for annotation refinement only. It must not be used as
> evidence of blind detection or reference-free localization.**

Open this step **only after your Step 1 file has been sent back.** Do not change your Step 1 answers. Step 2 answers
go in a separate file.

## What is different in Step 2

- For each clip you now see a **target** taken from the English reference text: a name for R02/R05/R35, a sentence
  for R26/R29.
- **The target was selected by the research team after consulting the reference text.** It is not something detected
  in the video. It may not be signed in the clip at all, or it may be signed differently.

## What you receive

- `review_reference_conditioned.html`: the Step 2 form. Load the same 8 clips with **Load clips…**.
- `reference_conditioned_followup.csv`: the same form as a spreadsheet.
- `SHA256SUMS`

## Questions (each clip)

1. **Is the target actually visible / signed in this clip?** `yes` / `partly` / `no` / `unsure`
2. If yes or partly: **corrected start** and **end** time (seconds from the clip start).
3. **Corrected letters** (R02/R05/R35 rows): the letters as signed, `?` for unreadable letters. Leave empty if not
   fingerspelled.
4. **Confidence:** `high` / `medium` / `low`
5. **Notes:** e.g. "a name sign is used instead of fingerspelling", "only the first name is spelled", or "this sentence
   is signed in a different order".

Then fill `step2_completed_at` and export or save the file.
