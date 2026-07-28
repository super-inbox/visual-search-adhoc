# Encoding Conversion Note — TOP_PAGE_INPUT_TEMPLATE.csv

**Date:** 2026-07-29
**Scope:** target-directory copy only. The read-only source file at
`/Users/baobaoli/Desktop/curify-frontend-prod-template-qa/docs/daily_report/7.29/vertical-page-seo-research/TOP_PAGE_INPUT_TEMPLATE.csv`
was NOT modified.

## What was found

`TOP_PAGE_INPUT_TEMPLATE.csv` failed UTF-8 decoding (`UnicodeDecodeError` at byte offset 345,
byte `0xd1`).

## Encoding determination

Not guessed. Verified by decoding with `mac_roman` and diffing the result character-for-character
against the known-good, already-UTF-8 `TOP_PAGE_INPUT.csv` in the same folder (which contains the
same underlying text, filled in). The `mac_roman`-decoded text was identical to the UTF-8 file's
text for every overlapping character (only difference: a trailing-newline/whitespace tail, not a
content difference). This confirms `mac_roman` as the correct source encoding with high confidence,
rather than assuming it.

## Action taken

1. Original bytes backed up unmodified to `logs/TOP_PAGE_INPUT_TEMPLATE.csv.original-mac_roman.bak`
   (this file, still `mac_roman`-encoded).
2. The target-directory copy of `TOP_PAGE_INPUT_TEMPLATE.csv` was re-written as the same text,
   re-encoded as UTF-8. No field values, row order, or research conclusions were changed — only the
   byte encoding.
3. Re-parsed the converted file with Python's `csv` module and confirmed valid UTF-8 decoding and
   successful parse (see `PRE_COMMIT_VALIDATION.md`).
