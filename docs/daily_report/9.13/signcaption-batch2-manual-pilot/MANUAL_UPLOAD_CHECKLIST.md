# Manual SignCaption Upload Checklist — Batch 2 (10-clip expansion, n=5 → n=15)

Do this once per clip, for however many of the 10 clips you complete in one sitting. Order
doesn't matter. Nothing here is automated — every step below is a manual action on the
SignCaption website. Same workflow as the original 5-clip pilot's
`docs/daily_report/9.11/signcaption-manual-pilot/MANUAL_UPLOAD_CHECKLIST.md`.

**Do not edit, correct, or clean up the returned caption text at any step.** A wrong,
garbled, or empty result is a real result for this benchmark.

## Per-clip workflow

For each `clip_id` in:
- `g2NA_eBUcH8_0-3-rgb_front`
- `G19uBylwQww_1-2-rgb_front`
- `fZM3IcM2Xs4_14_15_16-10-rgb_front`
- `g2nvBjp0loQ_4-3-rgb_front`
- `g05yGRoZE10_1-8-rgb_front`
- `FzQPg4aqNYc_13-1-rgb_front`
- `G3RvsnzQrXQ_3-10-rgb_front`
- `g0UUmEkoT1w_2-10-rgb_front`
- `FZCEymcpq7I_14-1-rgb_front`
- `G1jsDl1mVvk_1-1-rgb_front`

### 1. Locate the video

Path (repo-relative, do not modify): `asl-translator/data/public_benchmarks/how2sign_v2/videos/<clip_id>.mp4`

Exact paths and durations for all 10 clips are in `pilot_manifest_batch2.csv` (same folder
as this file), columns `clip_id` / `video_path` / `duration_sec`.

### 2. Upload the video to the SignCaption website

Use the clip exactly as it is on disk — do not trim, re-encode, crop, or otherwise modify
it before upload.

### 3. Wait for the caption result

Let SignCaption finish processing before doing anything else. If it fails or times out,
note that instead of retrying with a different clip.

### 4. Export the result

- **If the website offers an SRT / subtitle-file export:** download it.
- **If it does not:** copy the exact English caption text SignCaption displayed —
  verbatim, including any odd wording, incomplete sentences, or repeated words.
- **If SignCaption returns nothing at all for this clip:** that is still a result — proceed
  to step 5 and save an empty file rather than skipping the clip.

### 5. Place the result into the prepared clip path

Save it as exactly one of:
- `asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/<clip_id>/signcaption_result.srt`
  (if you exported an SRT file)
- `asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/<clip_id>/signcaption_result.txt`
  (if you're pasting plain text — including an empty file for a genuinely empty result)

The exact target path for each clip is also listed in `pilot_manifest_batch2.csv`'s
`signcaption_output_path` column, and repeated in that clip's own
`asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/<clip_id>/README.md`.

### 6. Do not manually edit or correct the SignCaption text

Once saved, leave the file exactly as exported/pasted. Do not fix typos, do not remove
repeated words, do not translate/rephrase, do not delete a "wrong" answer and retry the
same clip through the website hoping for a better one.

## After you've done some or all of the 10 clips

Nothing else is required from you — do not run the scorer yourself unless asked. Report
back which clips you completed (all 10 or a subset) and whether any clip failed to produce
a result on the SignCaption website at all (as distinct from producing an empty caption).

## Do not touch the original 5-clip pilot

The original 5 clips' results
(`asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/clips/*/signcaption_result.srt`)
are already scored and audited. Do not re-upload, re-run, or edit any of them as part of
this batch — the combined n=15 scorer reads those 5 results read-only.
