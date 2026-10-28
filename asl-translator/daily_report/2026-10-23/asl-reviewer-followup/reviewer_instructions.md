# ASL review — Step 1 (blind)

Thank you for helping. We need an ASL-fluent person to annotate **what is actually signed in 8 short video clips**,
especially any fingerspelling. Your annotations are independent human labels. **There are no expected answers.**

## What you receive now

- `clips/`: 8 short clips, no sound, full camera frame.
- `review_blind.html`: the form (Chrome, Edge or Firefox; no internet needed). Click **Load clips…** and select the 8
  `.mp4` files.
- `blind_review.csv`: the same form as a spreadsheet, if you prefer not to use the page.
- `SHA256SUMS`: file checksums, for our records.

**A second step will follow later.** Please do not ask for it, and do not look for any other material, until Step 1 is
finished and returned.

## How to annotate

- Watch each clip at normal speed first, then slow down as needed (0.5× / 0.25× buttons on the page).
- Annotate **only what is visible and signed**. Do not infer letters or words from context or from what the person
  might be saying.
- Mark **unsure** whenever you are not certain. An honest "unsure" is more useful than a guess.
- Times are **seconds from the start of the clip**, to about 0.1 s. Approximate to the nearest visible signing boundary
  is fine. The page's "start = now" / "end = now" buttons fill the current playback time.
- Answer each clip on its own. Two clips from the same case may show different, partly overlapping or unrelated
  moments.

### Rows marked "fingerspelling check" (R02-*, R05-*, R35-*)

1. **Is fingerspelling present?** `yes` / `no` / `unsure`
2. If yes: **start** and **end** time.
3. **Letters or word fingerspelled.** Free text. Write `?` for each letter you cannot read (e.g. `M?KE`), or `unsure`.
   Do not complete a partial word by guessing.
4. **Confidence** in your answer: `high` / `medium` / `low`
5. Optional:
   - **type**: fingerspelling / name sign / lexicalized fingerspelling / unsure;
   - **hand visibility**: good / partial / poor;
   - **issues**: occlusion, hand out of frame, fast signing, unclear letter, other;
   - **notes**.

If there is more than one fingerspelled span in a clip, use **+ span** on the page (or copy the row in the CSV and set
`span_no` to 2, 3, …).

### Rows marked "utterance boundaries" (R26-context, R29-context)

These are longer clips of continuous signing.

- **Boundaries:** list the times where one sentence or utterance ends and the next begins, e.g. `1.2; 3.8; 7.5`.
- **Confidence:** `high` / `medium` / `low`.
- **Notes (optional):** a rough gloss or summary of each part, in your own words.

## When you finish Step 1

Fill in your reviewer ID (initials are fine) and ASL background, for example "Deaf native signer", "CODA" or "certified
interpreter, 10 yrs". Then click **Export** (or save the CSV) and send the file back to us. Partial files are fine.

## Use of the videos

The clips come from the How2Sign dataset (CC BY-NC 4.0, research use only). Please do not share or upload them, and
delete them when you are done.
