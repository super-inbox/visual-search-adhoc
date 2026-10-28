# Source-position follow-up for the 5 unresolved inputs

**Status:** [PROGRESS_REVIEW.md](PROGRESS_REVIEW.md) item 3.
- No model run (no Uni-Sign, no Gemini). No reference text or model predictions used.
- Frozen thresholds unchanged. No Amendment 3.
- The committed 10/27 manifest is **not modified**.

Results: [`unresolved_source_position_verification.json`](../../experiments/p0-2026-10-28/results/unresolved_source_position_verification.json).
Helper: [`blind_anchor.py`](../../experiments/p0-2026-10-28/blind_anchor.py).

## Result

**Status:** all 5 rows get **SOURCE_TIME_SUPPORTED_BY_AI_VISUAL_ANCHOR**: the source time is supported by a unique visual match.
- **Judge:** the AI assistant running this session, **not a human** (`visual_anchor_judge_type = "AI assistant"`,
  `judge_count = 1`, `second_rater = false`).
- **What this is:** additional visual evidence for source-time placement.
- **What it is not:**
  - **not** human verification;
  - **not** independent second-rater confirmation;
  - **not** a replacement for the frozen automatic provenance result;
  - **not** evidence that the automatic thresholds passed.
- **Automatic status:** kept as `provenance_status_auto = UNRESOLVED` for all 5. It is not overwritten.
- **Before relying on these anchors:** human confirmation or an independent second-rater check would be required
  before treating them as human-verified provenance.

| Row | Source frames | Source time (s) | Uncertainty | Blinding | Expected-time exposure | Reference-text exposure | Crop-box source position |
|---|---|---|---|---|---|---|---|
| R26 `A_official` | 364–399 @24 (36 fr) | 15.167–16.667 | ±1 fr (±0.04 s) | **PARTIAL** | yes | **yes** (incidental) | UNKNOWN |
| R28 `A_official` | 1293–1333 @24 (41 fr) | 53.875–55.583 | ±2 fr (±0.08 s) | **FULL** | no | no | UNKNOWN |
| R35 `A_official` | 315–407 @24 (93 fr) | 13.125–17.000 | ±2 fr (±0.08 s) | **PARTIAL** | yes | no | UNKNOWN |
| R42 `A_official` | 2470–2568 @24 (99 fr) | 102.917–107.042 | ±3 fr (±0.13 s) | **FULL** | no | no | UNKNOWN |
| R32 `B_ours_5p39` | 1046–1101 @30 (56 fr) | 34.867–36.733 | ±3 fr (±0.10 s) | **PARTIAL** | yes | no | n/a (full frame) |

Blinding is with respect to expected source times.

**Totals:**
- 0 resolved by metadata;
- 5 `SOURCE_TIME_SUPPORTED_BY_AI_VISUAL_ANCHOR`;
- 0 still without source-time evidence.

**Interpretation per row:**
- **R26 A:**
  - source time visually supported (AI judge);
  - PARTIAL blinding;
  - incidental reference-text exposure (one sentence, not used);
  - crop-box source position still unknown.
- **R28 A:** source time visually supported (AI judge); FULL blinding; crop-box source position still unknown.
- **R35 A:**
  - source time visually supported (AI judge);
  - PARTIAL blinding;
  - the official and old windows remain separate signing events;
  - crop-box source position still unknown.
- **R42 A:** source time visually supported (AI judge); FULL blinding; crop-box source position still unknown.
- **R32 B:**
  - source time visually supported (AI judge);
  - PARTIAL blinding;
  - the AI visual anchor is consistent with the original annotation and the earlier best automatic offset, but **the
    frozen automatic criterion remains failed** (grid motion r = 0.896 < 0.90). It is not rounded or reinterpreted as
    passing.

## Limitations (read before using these anchors)

- **AI judge only.** One judge, the AI assistant, not a human. No second-rater confirmation.
- **Three anchors are not fully blind** (R26, R32, R35). Their expected times had been seen earlier in the session: the
  R26 reviewer context window, the R32 earlier automatic offset, and the R35 re-aligned window. The sheet design (random
  sheet codes, random order, opaque labels, no times or indices) limits but does not remove that influence.
- **R26 incidental reference exposure.** One R26 reference sentence appeared in terminal output while checking Uni-Sign's
  `labels.test` for start/end fields. It was not used.
- **The 2-per-second contact-sheet scan could miss very short look-alikes.** A stretch under about 1 s could be missed.
  This matters most for R26 (1.5 s).
- **The crop-box source position for the 4 A rows is still UNKNOWN.** Only source time is visually supported.
- **No threshold changes. No Amendment 3.** The 10/27 manifest is not modified.

## 1. Method

1. **Tier 1, metadata.** Every available upstream record was searched for an explicit mapping from the input file to
   source frames (§2).
2. **Tier 2, AI visual anchoring with a blinded procedure.** This ran because Tier 1 found nothing. The helper
   renders frames only; every match was judged visually by the AI assistant. The procedure hides times, but the judge was only fully blind
   for R28 and R42 (see Limitations).
   - **Query sheet:** every frame of the unresolved input (≤ 60 frames, otherwise 60 evenly spaced).
   - **Coarse sheets:** cover the **whole** raw video at 2 frames per second, using a fixed central 720×720 signer
     region (not the ambiguous crop box).
     - Sheets have random 3-letter codes and are listed in random order.
     - Cells are numbered only within a sheet.
     - Adjacent sheets overlap by one row.
     - No sheet shows a time, a frame index, an annotation, or an earlier candidate offset.
   - **Fine sheets:** for each candidate picked by eye ("sheet X cell k looks like query frame Qi"), raw frames at full
     frame rate, ±13 frames around the implied FIRST / MID / LAST query frame. Labels are opaque letters (e.g. `F-OZ`),
     placed next to the query frame.
   - **Decision:** the matching labels for the first, middle and last query frame, the cues, and each rejected
     competitor were written to a decisions file **before unblinding**. The combined file's sha256 is in the JSON.
3. **Unblinding.** Only afterwards were labels mapped to frames and the manifest annotations and earlier automatic
   evidence read for comparison.

**Inputs checked against the manifest:**
- The 4 official crop clips (the HF range-fetched copies from 10/27) and the R32 B clip.
- The 5 raw videos re-extracted from `test_raw_videos.zip`.
- All sha256 values match (in the JSON).
- Holdout material: none (How2Sign test only).

## 2. Evidence hierarchy

### Tier 1: metadata. No row resolved.

| Source checked | What it contains | Source position? |
|---|---|---|
| HF `ZechengLi19/Uni-Sign` @ `eab251b7` file list | weights, pose zips, `how2sign_rgb_format.zip.aa–ae`, `README.md` | no crop or cut metadata file |
| rgb zip central directory (read from `.ae`, sha256 in JSON) | 35,176 entries: `crop_train/` 31,087, `crop_test/` 2,350, `crop_val/` 1,739 | **only `.mp4`**: no box, index or command file |
| Release README | weights + pose files | no cutting description |
| Crop clip containers (4) | `start_time 0`, `start_pts 0`, `Lavf58.29.100`, `Mainconcept Video Media Handler` | no timecode, offset or comment |
| R32 B clip container | `start_pts 507` @ 1/15360 = 0.033 s encoder delay, `Lavf57.83.100` | no source offset |
| Uni-Sign repo `eed438bc` | no crop/cut script. `labels.test` = name, path, text only | no start/end, no box |
| Official pose `.pkl` | `keypoints`, `scores`, `w_h` | no source frame index |
| How2Sign original / re-aligned CSV | per-sentence START/END | expected times, not a record of how the file was cut (R10/R14 show archive clips can follow either CSV, with frame offsets) |
| P0-12 indexes, B-vs-C alignment | zip offsets; a derived measurement (R42 residual 0.137 failed) | not metadata |

### Tier 2: AI visual anchoring. All 5 have source-time support (2 fully blind, 3 partially blind).

Per-case cues and the rejected competitors are in §3. In every case:
- **Before deciding:** the coarse scan covered the whole source video, and each look-alike stretch was checked at full
  frame rate.
- **After deciding:** the match was compared with the annotation (§4).

### Tier 3: remain unresolved.

None.

## 3. Per-case result and cues

**R26 `A_official`** (36-frame crop).
- **Match:** frames 364–399.
- **Cues:**
  - both hands sweep from forehead to mouth with elbows out;
  - then hands open to the sides, one fist at the shoulder;
  - a blurred inward sweep;
  - then fists close together at the chest while the head tilts up.
- **Rejected competitor:** one stretch on another sheet, rejected at full frame rate. Its raised hands use a pointing
  index, and it ends with crossed hands at the lips.
- **Uniqueness:** no other stretch shows the sides → chest-fists sequence.

**R28 `A_official`** (41 frames).
- **Match:** frames 1293–1333.
- **Cues:**
  - both forearms horizontal, fingertips together;
  - one flat hand drops under the other forearm;
  - a hand rises to the chin and back under the forearm;
  - a grimace follows the clip.
- **Rejected competitors (2):** both have hands hanging palms-in. The raised hand is a fist at the mouth or an F/O hand
  at the shoulder, not the index at the chin.
- **Note:** a long stretch with forearms horizontal exists, but only one position continues into the hand-to-chin move.

**R35 `A_official`** (93 frames).
- **Match:** frames 315–407.
- **Cues:**
  - a raised fingerspelling-like hand at the shoulder cycling C/L shapes, with the other forearm low;
  - a blurred downward sweep;
  - low crossed pointing hands;
  - open hands raised;
  - a diagonal forearm crossing;
  - a fist at the chin, then fists at the chest.
- **Rejected competitors (2):** an index at the chin with the other hand low and a raised open palm; stacked horizontal
  hands, then a raised index.
- **Caveat kept from 10/27:** this official window and the old window (6.50–12.48 s) **do not overlap**. They are
  different signing events and must not be compared as the same event.

**R42 `A_official`** (99 frames).
- **Match:** first frame 2470, so 2470–2568.
- **Cues:**
  - claw hands closing at the chest;
  - flat palms together;
  - one hand raised to the side;
  - a fist beside a vertical flat hand (repeated);
  - open hands overlapping;
  - a raised index;
  - palms spreading upward;
  - hands dropping.
- **Rejected competitors (2):** raised pushing palms; a hand on the chest, then fists at the shoulders.
- **Reconciliation:** the FIRST, MID and LAST blocks pointed to starts 2–5 frames apart, because the claw-hand start is
  nearly static. The chosen first and last labels span 98 frames, not 99. The start is therefore given ±3 frames.

**R32 `B_ours_5p39`** (56 frames, full frame).
- **Match:** frames 1046–1101.
- **Cues:**
  - hands at the chest with the mouth wide open;
  - a hand rises to the mouth/nose;
  - spread fingers beside the face;
  - an open 5-hand raised beside the face;
  - both fists raised at the chest.
- **Rejected competitors (4):** a palm out to the side, a raised fist, flapping hands, and a fist beside the head. None
  has this order.
- **Limit on the check:** all three blocks gave the same offset, so the end check is not independent of the start.

## 4. After unblinding: comparison with metadata and earlier candidates

- **A rows:**
  - All 4 AI visual anchors sit at the **re-aligned** annotation: |Δstart| ≤ 0.06 s, |Δend| ≤ 0.17 s, all within the
    0.20 s tolerance.
  - None matches the original annotation. The original intervals are 2–8 s away (R26 13.16–15.01, R28 45.63–48.88,
    R35 6.50–12.48, R42 96.49–103.02).
  - The four previously unanchored A rows now have AI visual-anchor evidence consistent with the re-aligned timing.
    They sit alongside the 41 rows previously supported by the frozen provenance procedure.
  - These are different evidence standards and should not be collapsed into a single VERIFIED count.
  - Of the 4, R28 and R42 are fully blind and R26 and R35 partially blind.
- **R32 B:** the AI visual anchor is consistent with the original annotation (34.81–36.71, not re-aligned 43.35–45.68)
  and with the earlier best automatic offset (1045, 1 frame away). But **the frozen automatic criterion remains
  failed** (grid motion r 0.896 < 0.90). The anchor is partially blind because that offset had been seen earlier.
- **Earlier A2 crop-box NCC:** it was about spatial position and was never turned into a temporal match. The visual
  anchors say nothing about which box was right.

## 5. Uncertainty and limitations

The main limitations are listed under Result. In addition:

- **Frame precision:** ±1 to ±3 frames (0.04–0.13 s), set by how static the signing is at the clip edges. That is
  enough for any claim made at the 0.20 s tolerance, but not for frame-exact claims.
- **Single AI judge.** All five visual judgements were made by the AI assistant running this session. No human and no
  second rater were involved, so there is no inter-rater agreement.
- **Imperfect blinding (disclosed):**
  - Before this task, the analyst had read some expected times in earlier session documents: the R35 re-aligned window,
    the R32 earlier automatic offset, and the R26 reviewer context window.
  - The sheet design (random codes, random order, opaque labels, no indices) limits, but does not remove, the chance
    of steering a decision toward a remembered time. R26, R32 and R35 are therefore PARTIAL blinding.
  - R28 and R42 are FULL blinding.
- **Reference text seen by accident:** while checking `labels.test` for start/end fields, one reference sentence (R26)
  appeared in terminal output. It was not used for anything.
- **Coverage limit of the uniqueness check:** the coarse scan sampled 2 frames per second at thumbnail size. A
  near-duplicate stretch shorter than about 1 s could in principle be missed. This matters most for the shortest clip,
  R26 (1.5 s).
- **Spatial box still open:** the crop box for the 4 A rows is still not uniquely placed (unchanged from 10/27).

## 6. Frozen thresholds

The frozen rules (A2.2 NCC ≥ 0.70 with margin 0.05; temporal match agree ±1 frame, r ≥ 0.90, margin ≥ 0.20; 0.20 s
annotation tolerance) were **not changed, re-run or reinterpreted**. No Amendment 3 was written. All 5 rows remain
UNRESOLVED **under the automatic rules** (`provenance_status_auto`). `SOURCE_TIME_SUPPORTED_BY_AI_VISUAL_ANCHOR` is additional, separately labelled
evidence. It does not mean any automatic threshold passed.

## 7. Do any source-time-sensitive conclusions need revision?

No. The new evidence agrees with every prior conclusion and narrows some caveats:

- **10/27 "A_official follows re-aligned":** the 4 previously unanchored rows now have AI visual-anchor evidence
  consistent with it. These are different evidence standards from the 41 automatically supported rows and are not
  added to a single VERIFIED count.
- **10/27 "B_ours_5p39 mostly original":** R32's AI visual anchor is also consistent with original timing, while its
  automatic status stays UNRESOLVED.
- **Task 2 Step 3 sampling evaluation:** it excluded these rows from timing-dependent claims. Its numbers stay as
  reported and are not recomputed. If they are re-run later, these rows could be added as a separately labelled tier.
- **Reviewer package R35-official clip:** the clip (13.11–16.90, the annotation-defined window, 91 frames) covers the
  anchored official input (13.125–17.000) except roughly its last 2 frames. That is close, but the clip is still **not**
  a cut of the official crop, and the existing caveat stays. The R26 context clip (11.75–16.75) contains the anchored
  R26 official input in full.
- **Fingerspelling time base:** OpenFS on the R35 official clip can now be placed in source time with about ±0.08 s
  precision. Any such comparison stays descriptive.
- **Uni-Sign and production evaluations:** not time-dependent; unchanged.

## 8. Manifest

**Recommendation:** update the 10/27 provenance manifest later, by adding columns, without overwriting the automatic
status:
- `provenance_status_auto` stays UNRESOLVED;
- add `source_time_evidence_status` = SOURCE_TIME_SUPPORTED_BY_AI_VISUAL_ANCHOR;
- add `visual_anchor_judge_type`, `judge_count`, `second_rater`, `blinding_level`, `prior_expected_time_exposure`,
  `reference_text_exposure` and `crop_box_source_position`;
- add the anchor frames, time and uncertainty, with a link to this report.

Nothing was changed now.
