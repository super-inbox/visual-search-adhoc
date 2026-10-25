# Independent second model pass (Codex or another vision model)

Use this to get a **second, blind** model review of the 45 clips to compare with `model_case_analysis.csv`. Do not
give the second model `model_case_analysis.csv`, `model_case_analysis.html` or `MODEL_CASE_ANALYSIS.md`.

## Inputs to supply

1. **Video, as images.** Codex CLI and most coding agents cannot play mp4, so supply the contact sheets:
   `contact_sheets/<review_id>_<nn>.jpg`. These are 4 fps stills with a timestamp on each tile, 6 s per sheet. Build
   them first with `python3 -I scripts/build_contact_sheets.py ../../10.18/asl-review-inspection-sheet contact_sheets`.
   Attach every sheet of a clip with that clip, e.g. `codex -i contact_sheets/R20_01.jpg -i contact_sheets/R20_02.jpg …`.
   A model that accepts video can take `../../10.18/asl-review-inspection-sheet/videos/<clip_id>.mp4` (or the zip)
   instead.
2. **Text per clip:** these columns of `../../10.18/asl-review-inspection-sheet/inspection_sheet.csv`: `review_id`,
   `clip_id`, `duration_s`, `ground_truth`, `prod_output`, `unisign_output`, `auto_error_type_prod`,
   `auto_error_type_unisign`, `initial_error_category`, `evidence_notes`. Also
   `../../10.18/asl-review-inspection-sheet/repetition_audit.csv` for the 9 official repetition cases.

Process one clip per request, or at most five clips, so the frames and the text stay together.

## Prompt

> You are reviewing American Sign Language video clips for a translation-error study. You are **not** an ASL-fluent
> human reviewer, and your output will be labelled `model_review / unverified`.
>
> For each clip you get timestamped stills (4 fps, no motion, no audio) and four texts: the English ground truth (a
> translation, not a gloss), "our/old output" (a provisional historical pipeline output), the "official" Uni-Sign
> output, and an automatic weak label.
>
> Rules:
> - Describe only what is physically visible: hand location, handshape type, one or two hands, holds, rest periods,
>   with timestamps. Do not state what a sign means in the description.
> - Put any linguistic reading in `evidence` as "consistent with X (unverified)". If the stills do not settle it,
>   say so in `unresolved_ambiguity`.
> - Do not read fingerspelled letters unless they are clearly legible. Do not judge headshakes, brow raises or
>   movement-dependent signs from stills.
> - Note idle periods, signing that leaves the frame, and references that are longer than the visible signing.
> - For clips whose official output loops (repetition), say whether anything visible actually repeats and at which
>   timestamps.
>
> Return one CSV row per clip with these columns:
> `review_id, clip_id, model_visible_description, model_visible_description_confidence (low|medium|high),
> model_gt_vs_our_error, model_gt_vs_official_error, model_shared_failure (yes|partial|no),
> model_shared_failure_note, model_primary_error_category, model_error_categories_all (;-separated, primary first),
> model_evidence, model_confidence (low|medium|high), model_unresolved_ambiguity, model_observation_flags,
> model_repetition_analysis`.
> Categories: fingerspelling, name, number, negation, question, spatial_relation, repetition, general_semantic.

## Output

Save the result as `model_case_analysis__<model>.csv` next to this file, and never overwrite
`model_case_analysis.csv`. Compare the two passes on `model_primary_error_category`, `model_shared_failure` and
`model_repetition_analysis`. Where the passes disagree, the case goes to the ASL-fluent reviewer first. Neither pass
writes any human-review field, and no row becomes `human_verified`.
