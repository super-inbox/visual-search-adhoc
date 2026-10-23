# P0-C — input-correction upper bound: case sheet (2026-10-23)

**Status: setup only. No corrected input built, no decode run.** Source: [boss report §9](../../2026-10-21/UNISIGN_CASE_REVIEW_AND_P0_PLAN.md).
Protocol: [P0_PROTOCOL_FREEZE.md §3](../P0_PROTOCOL_FREEZE.md). Machine-readable sheet: `case_inputs.csv`.

Manual corrections only show an **upper bound**; they are not a deployable method. Corrections are defined from
video, never from reference text. Do not re-run uniform window widening (P0-18: WER 100.9 → 109.7).

The source raw videos for all 4 cases are present in `~/Desktop/curify/p018-work/downloads/test_raw_videos.zip`.
P0-12 pose inputs for both domains are present and sha256-verified. Times are in source-video seconds.

| ID | Original window (page video) | Realigned (official input) | IoU | Frames A / B | What must be checked before any correction | Status |
|---|---|---|---|---|---|---|
| **R10** | 31.03–56.34 | 31.03–56.34 | 1.00 | 608 / 608 | (1) **Uni-Sign keeps 256 of 608 frames at random**: compute which frames the frozen seed rule keeps, which is the literal "sampling budget" the boss asked about. (2) A person marks the rest span(s) (around 5–18 s into the clip per the boss's contact sheet), keeping held handshapes and face. (3) **Timing conflict:** P0-18's downloaded How2Sign test CSV (sha256 `ecc73526…`) lists this sentence at 23.38–42.38, while the repo subset TSV and the realigned CSV give 31.03–56.34. Resolve this before defining "original". | **Blocked** (timing conflict, rest labels) |
| **R26** | 13.16–15.01 | 15.15–16.62 | **0.00** | 36 / 45 | The boss saw hands leaving the top of the frame in the **original** window. The official input is a different window that does not overlap it, with a 698×598 crop. Check the raw source frames for both windows: are the hands cut off at capture (a larger crop cannot fix that) or only by the crop? P0-18 whole-video poses exist (`p018-work/dev/vid_all/G3EfBFwsOpE-10-rgb_front.npz`) to check keypoints near the frame edge. | Ready for source check |
| **R29** | 10.03–11.86 | 10.03–11.86 | 1.00 | 55 / 55 | Hands rest mid-clip and move only at the start and end. View the neighbouring sentences (`92V3oH63zbQ_4`, `_6`) in the raw source and decide by video only whether the target sentence is signed inside this window. Add context only if it is not. | Ready for source check |
| **R35** | 6.50–12.48 | 13.11–16.90 | **0.00** | 93 / 144 | The boss saw a 3–5 s hold in the **original** window (about 9.5–11.5 s source), which lies outside the official window. Find which window holds the sentence and the name. This depends on the P0-B reviewer's answer for "CarolAnn". | **Blocked** on the P0-B reviewer |

## Before each corrected decode (frozen order)

1. Write the correction definition and date into `case_inputs.csv` (`correction_definition`, `correction_frozen_on`)
   and choose the decode domain.
2. Build the corrected pose input with the existing P0-18 extractor (`docs/daily_report/10.16/asl-p0-18-auto-preprocessing/scripts/pose_extract.py`) on CPU.
3. Decode the original and corrected inputs with the frozen T settings (protocol §1.3).
4. Report key content recovered, new omissions, outcome labels, and whether the correction could be automated
   without the reference or official boundaries.
