# G05uFub3YFc_9-2-rgb_front — SignCaption manual-pilot result slot

**Do not edit videos or references.** This directory holds only the manually exported
SignCaption result for this one clip.

- Source video (read-only, not modified): `asl-translator/data/public_benchmarks/how2sign_v2/videos/G05uFub3YFc_9-2-rgb_front.mp4`
- Frozen reference (read-only, not modified): `asl-translator/data/public_benchmarks/how2sign_v2/references/G05uFub3YFc_9-2-rgb_front.srt`
- Reference text: "Again, do maybe twenty breaths, little flow, inhaling and exhaling the whole time you go breath is important and see if you would like, you can keep it up for a minute or more."

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
