# g0UUmEkoT1w_2-10-rgb_front — SignCaption manual-pilot result slot (Batch 2)

**Do not edit videos or references.** This directory holds only the manually exported
SignCaption result for this one clip. Part of Batch 2 (10 new clips, expanding the
SignCaption pilot from n=5 to n=15) — see
`docs/daily_report/9.13/signcaption-batch2-manual-pilot/` for the full batch context.

- Source video (read-only, not modified): `asl-translator/data/public_benchmarks/how2sign_v2/videos/g0UUmEkoT1w_2-10-rgb_front.mp4`
- Frozen reference (read-only, not modified): `asl-translator/data/public_benchmarks/how2sign_v2/references/g0UUmEkoT1w_2-10-rgb_front.srt`
- Reference text: "They may feel very tired, sleepy, lacking energy."

## Place your SignCaption export here

Save the exported result as **one** of the following, in this directory:

- `signcaption_result.srt` — if SignCaption's website offers an SRT/caption-file export
  (preferred: preserves segment timing).
- `signcaption_result.txt` — if no file export is available: paste the exact returned
  English caption text into this plain-text file, verbatim.

**Do not create both files for the same clip** — if both exist, the scorer will treat
`signcaption_result.srt` as the correct one and ignore the `.txt` file, but avoid the
ambiguity by only saving the one that actually corresponds to what the website gave you.

**Do not manually edit or correct the text after saving it** — typos, mis-hearings, and
garbled output are the point of the benchmark; correcting them would invalidate the score.

If SignCaption returns literally nothing (empty result) for this clip, still create
`signcaption_result.txt` containing nothing (an empty file) rather than leaving no file at
all — this lets the scorer distinguish "genuinely empty prediction" from "not attempted yet."
