# Request for an ASL-fluent reviewer — fingerspelled names in 3 short clips

Thank you for helping. This is a small check, about 6 short video windows of 4–10 seconds each.

## Why

Our translation model replaces people's names with different names in these clips. Before we try to fix this, we need
to know whether the name is actually **fingerspelled** in the video the model saw, and if so **when**.

## What you will receive

For each case (R02, R05, R35), two video files cut from the same source video:

- **Window O** — the original sentence window.
- **Window R** — the re-aligned window that the official model input used.

These may overlap or may not. For R35 they do not overlap. File names follow `<ID>_<O|R>.mp4`. Times you report
are seconds **from the start of the file you are watching**.

## Step 1 — blind (do this before opening Step 2)

For each file, in `interval_labels.csv`:

- `fs_present`: is there fingerspelling? `yes` / `no` / `unclear`
- `fs_start_s`, `fs_end_s`: where the fingerspelling starts and ends (one row per span; add rows if there are
  several)
- `letters_seen_blind`: the letters you read, with `?` for any letter you cannot read
- `video_quality_for_handshape`: `good` / `partial` (hand blurred, cut off or occluded) / `poor`
- `notes`: anything else, e.g. a name sign instead of fingerspelling, a lexicalized sign, or the hand leaving the
  frame

Please do not guess letters to complete a word.

## Step 2 — unblinded

Only after Step 1 is saved, open the English reference sentence for each case (provided separately) and fill in:

- `reference_name_after_unblind`: the name in the reference
- `matches_reference_name`: `yes` / `partly` / `no` / `cant_tell`

Do not change your Step 1 answers. If you would like to add a note after unblinding, use `notes_after_unblind`.

## About you (once)

`reviewer_id` (initials are fine), `asl_background` (e.g. Deaf native signer, CODA, interpreter, years of
use), and `reviewed_at` (date).

## Use of the videos

The clips are from the How2Sign dataset (CC BY-NC 4.0, research use). Please do not redistribute them.
