# P0-C source / input checks — R26 and R29 (2026-10-24)

**Status: source checks done. No correction defined, no corrected input built, nothing decoded.**
Protocol: [P0_PROTOCOL_FREEZE.md §3](../P0_PROTOCOL_FREEZE.md) (unchanged). Case sheet: [CASE_SHEET.md](CASE_SHEET.md).
Machine-readable result: `case_inputs.csv` (new columns `source_check_on`, `source_check_class`,
`source_check_finding`, `neighbour_windows_s`; `correction_definition` / `correction_frozen_on` stay blank).

## Method

- Sources: How2Sign **test** raw videos from `p018-work/downloads/test_raw_videos.zip`, extracted to a scratch
  directory and not committed. Their sha256:
  - `G3EfBFwsOpE-10-rgb_front.mp4`: `910f3918…e58d6e4`, 1280×720, 24 fps, 66.75 s
  - `92V3oH63zbQ-1-rgb_front.mp4`: `3179e17a…e858c7`, 1280×720, 30 fps, 122.5 s
- Timings: the original How2Sign test CSV (`how2sign_test.csv`) and the realigned test CSV (`how2sign_realigned_test.csv`,
  path in the P0-18 config). They are used only to **locate** windows, never as a correction. No val file was opened.
  `holdout_guard.assert_not_holdout` passed on all 8 target and neighbour IDs.
- Evidence (local only, git-excluded via `.git/info/exclude`): `source_check_local/*.png`, made with
  `scripts/sheet.py` (timestamped contact sheets; the red frame marks the window under test).
- Numbers: `scripts/edge_stats.py` gives the hand-keypoint distance to the top edge, from the P0-18 GPU-env whole-video pose
  `p018-work/dev/vid_all/G3EfBFwsOpE-10-rgb_front.npz`. `scripts/fit_crop.py` finds where the official crop sits by
  affine-fitting the P0-12 `A_official` keypoints to those full-frame poses. `scripts/motion.py` gives frame-difference
  motion energy over the signer box (R29 has no whole-video pose file).
- All times are source-video seconds. ASL meaning is **not** inferred anywhere.

## R26 — `G3EfBFwsOpE_3-10-rgb_front`

| Window | Span (s) | Input | What the video shows |
|---|---|---|---|
| Original (old preprocessing, D-B) | 13.16–15.01 | full frame 1280×720, 45 frames | Both hands are raised at or above head height, at the **top edge of the camera frame**. In 43/44 frames a hand keypoint is within 15 px of the top (min y −12 px). Fingertips are visibly cut off at capture at about 12.07, 13.07, 13.23, 14.40 and 14.57 s. The hands are still mostly visible: 0/44 frames have a mostly low-confidence hand. The same raised-hand signing already runs from about 11.75 s. |
| Official (D-A) | 15.15–16.62 | crop 698×598, 36 frames | The fitted crop box is **x 299–1001, y 114–711** (scale 0.994/1.002, median residual 2.1 px, offset 0 frames). The hands sign at chest/face height (min hand y 178 px, median 276 px), fully inside the crop and the camera frame. The signer is at rest from about 16.75 s to at least 19 s. |
| Previous neighbour `_2` | orig 5.90–13.16; realigned 8.56–15.15 | — | The realigned `_2` span **contains the whole original `_3` window**. Per the annotation, the raised-hand signing in 13.16–15.01 belongs to the previous sentence. This is metadata, not something I verified visually. |
| Next neighbour `_4` | orig 19.28–20.25; realigned 19.52–22.10 | — | Separated from the official `_3` window by the rest at 16.75–19.5 s. |

**Finding (classes a/b/c):**
- **Original window → (a), partial.** The hands reach and sometimes leave the top of the *original camera frame*.
  Because D-B is already full frame, no crop change can recover the missing fingertips. They are not lost by a crop.
- **Official window → none of a/b/c.** The hands are visible in the full frame and inside the official crop.
  Framing does not explain the D-A failure.
- **(b) applies only hypothetically:** if the official crop (top y = 114) were applied to the original window, it would
  cut off most of the raised hands.
- **(c):** the official window is itself the next time span (no overlap, IoU 0). It is the span where the hands are clearly
  visible. I cannot judge visually which span carries "the reverse" content.

**Plausible manually corrected input:** **none for framing.** A capture-level clip cannot be fixed, and the official input is
not clipped. The only remaining correction type is *timing* (which span holds the target sentence). That needs an
ASL-fluent span mark over about 11.75–16.75 s and cannot be set from video by a non-signer.

**Evidence:** `R26_full_11-19s_4fps.png`, `R26_top-strip_11.9-15.2s_6fps.png` (top 220 px, full resolution),
`R26_officialcrop_13-16.75s_4fps.png` (fitted official crop box applied to both windows).

## R29 — `92V3oH63zbQ_5-1-rgb_front`

Target window **10.03–11.86** (55 frames; A and B identical).

| Span (s) | What the video shows (motion energy, signer box) |
|---|---|
| ≤ 9.45 | Continuous signing from at least 5.0 s (energy 2–4.5) |
| 9.45–10.17 | One hand is held at the nose/mouth (hold). Its meaning is not inferred. |
| 10.17–10.55 | The hands lower to the lap |
| **10.55–11.40** | **Full rest** (energy 0.5–0.8) |
| 11.40–11.67 | The hands rise |
| 11.67–~25.5 | Continuous signing with no further full rest (short dips only at about 15.1, 17.0, 20.0, 22.4 and 25.1 s) |
| ~26.0 | Brief rest before the next run |

So about **46 % of the target window is full rest** (0.85 of 1.83 s). The rest is the end of a hold, transitions, and about
0.2 s of the onset of the next signing run.

**Neighbouring clips (exact IDs and timings):**

| Clip | Original (speech) | Realigned | Note |
|---|---|---|---|
| `92V3oH63zbQ_2-1-rgb_front` | 3.55–4.97 | 6.69–9.17 | |
| `92V3oH63zbQ_3-1-rgb_front` | 5.37–7.07 | 5.37–7.07 | realigned == original |
| `92V3oH63zbQ_4-1-rgb_front` | 7.40–9.75 | **11.70–16.51** | the previous sentence is realigned to *after* the target window |
| **`92V3oH63zbQ_5-1-rgb_front`** | 10.03–11.86 | 10.03–11.86 | **realigned == original** |
| `92V3oH63zbQ_6-1-rgb_front` | 12.21–18.31 | 16.59–25.81 | |
| `92V3oH63zbQ_7-1-rgb_front` | 18.54–20.78 | 26.83–32.77 | |

The target row is one of **170 / 2,357 test rows (7.2 %)** whose "realigned" times equal the original speech times, so it
appears never to have been realigned. Its neighbours were shifted 4–8 s later.

**Finding (classes a/b/c/d):** **(d) cannot be determined from video alone.** **(a) is visually unlikely**, because the
window is mostly rest plus transitions. If the realigned annotation of the neighbours is consistent (`_4` signed at
11.70–16.51 and `_6` from 16.59), sentence order puts the target signing **after** the window **(c)**, most likely in about
11.7–25.8 s. This inference comes from timing metadata, not from the video, and is **not** used as a correction.

**Plausible manually corrected input:** **yes, in principle.** A time-shifted window over the target sentence's actual
signing (from the 11.67 s onset run, or earlier if the reviewer places it before the rest). Its start and end cannot be set
without an ASL-fluent span mark. Copying the neighbours' realigned boundaries would be oracle information (protocol §3).

**Evidence:** `R29_full_6-27s_2fps.png`, `R29_signer_9-13s_6fps.png`.

## Remaining blockers before any corrected decode

| Case | Blocker | Owner |
|---|---|---|
| R26 | Framing correction is ruled out. A timing correction needs an ASL-fluent reviewer to mark where "Which is basically the reverse?" is signed within about 11.75–16.75 s. If it is inside 15.15–16.62 (already the D-A input), P0-C has no correction for R26 → **stop R26**. | ASL-fluent reviewer |
| R29 | An ASL-fluent reviewer must mark the start and end of the target sentence's signing in about 5.0–10.0 s and 11.6–25.8 s, blind to the reference first. Then write `correction_definition` and `correction_frozen_on` into `case_inputs.csv` before decoding (protocol §3). | ASL-fluent reviewer, then Claude |
| Both | Building a corrected pose input with `pose_extract.py` on CPU and the T decode (§1.3) wait until the step above is done. | — |
