# ASL reviewer instructions — 8 short clips, 5 cases

Thank you for helping. Our sign-language-to-English model makes mistakes on these clips. Before we change anything, we
need an ASL-fluent person to tell us **what is actually in the video and when**. Please answer only from what you see.
There are no right answers we are hoping for.

The work has **two steps**. Step 2 is a separate file that you open **only after Step 1 is finished and saved**.

## What you receive

`step1_blind/`:
- `clips/` — 8 short video clips (no sound, full camera frame, original resolution).
- `reviewer_labels.csv` — the answer sheet. One row per clip. The first columns (up to `clip_sha256`) are already
  filled in for our records. Please leave them unchanged.
- `reviewer_package_manifest.csv`, `SHA256SUMS` — file checksums, for our records.

`step2_unblind/` (sent separately, or open only when Step 1 is done): `UNBLIND_REFERENCES.md`.

**Times:** give all times in **seconds from the start of the clip file you are watching**, to 0.1 s (e.g. `2.4`). A
player that shows tenths of a second helps (VLC, mpv or QuickTime with frame stepping). If a span starts before the clip or
runs past its end, write `0` or the clip length and say so in the notes.

**Several spans in one clip:** copy the row, keep the first 12 columns, and set `span_no` to 2, 3 and so on.

## Step 1 — blind (do not open Step 2 yet)

### Rows R02-old, R02-official, R05-old, R05-official, R35-old, R35-official

Each case has two clips, called `old` and `official`, cut from the same source video. They may overlap, partly overlap or
not overlap at all. Please answer each clip on its own.

| Column | Question | Allowed answers |
|---|---|---|
| `fs_present` | 1. Is there fingerspelling in this clip? | `yes` / `no` / `unsure` |
| `fs_start_s` | 2. Exact start time of the fingerspelling | seconds from clip start |
| `fs_end_s` | 3. Exact end time of the fingerspelling | seconds from clip start |
| `letters_seen_blind` | 4. Blind letter reading: the letters you read, in order. Use `?` for each letter you cannot read. Please do not guess letters to complete a word. | e.g. `M?KE` |
| `fs_type` | 5. Type of what you see in that span | `fingerspelling` / `name sign` / `lexicalized fingerspelling` / `unsure` |
| `hand_visibility` | 6. Hand visibility during that span | `good` / `partial` (blurred, cut off or occluded) / `poor` |
| `notes_blind` | anything else (e.g. the hand leaves the frame, a name sign follows the spelling) | free text |

If `fs_present` is `no`, leave questions 2–6 empty, or use them for a `name sign` span if you see one.

### Rows R26-context, R29-context

These are longer clips of continuous signing. Without any English text yet:

| Column | Question | Answer |
|---|---|---|
| `utterance_boundaries_blind_s` | Where does one sentence or utterance end and the next begin? List the boundary times you see. | e.g. `1.2; 3.8; 7.5` |
| `notes_blind` | Optional: a rough gloss or summary of each part, in your own words | free text |

When Step 1 is complete for all 8 rows, fill `step1_completed_at` (date and time), and save the sheet. If possible,
send a copy to us before you open Step 2.

## Step 2 — unblinded

Open `step2_unblind/UNBLIND_REFERENCES.md`. **Do not change any Step 1 answer.** Put any second thoughts in
`notes_after_unblind`.

- **R02 / R05 / R35 rows:** `reference_name_after_unblind` = the person's name in the English reference sentence;
  `matches_reference_name` = does what you saw in Step 1 match that name? `yes` / `partly` / `no` / `cant_tell`.
- **R26 / R29 rows:** the file shows one **target** English sentence (and, for orientation, the sentences said just
  before and after it).
  - `target_found`: is the target sentence signed in this clip? `yes` / `partly` / `no` / `unsure`
  - `target_start_s`, `target_end_s`: where its signing starts and ends (seconds from clip start)
  - `target_confidence`: `high` / `medium` / `low`

Then fill `step2_completed_at`.

## About you (once, on any row)

`reviewer_id` (initials are fine), `asl_background` (e.g. Deaf native signer, CODA, certified interpreter, years of
use).

## Use of the videos

The clips come from the How2Sign dataset (CC BY-NC 4.0, research use only). Please do not share or upload them, and
delete them when you are done.
