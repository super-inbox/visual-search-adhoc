# P0-B — fingerspelling / proper-name local fusion: feasibility (2026-10-23)

**Status: setup only. Blocked on an ASL-fluent reviewer.** No spans have been inferred, no hand video extracted,
no recognizer run. Source: [boss report §8](../../2026-10-21/UNISIGN_CASE_REVIEW_AND_P0_PLAN.md).
Protocol: [P0_PROTOCOL_FREEZE.md §2](../P0_PROTOCOL_FREEZE.md).

## Question

Does the continuous hand RGB video contain letter information that the current pose path does not keep, and can it
be recovered with few false positives?

## Cases and matched inputs

Windows come from `../p0a-candidate-rerank/provenance/case_provenance.csv`, in source-video seconds. The page video
in the inspection sheet is the **original** window only.

| ID | clip_id | Reference name (scoring only, never a lexicon) | Original window (D-B, page video) | Realigned window (D-A, official input) | IoU | Source raw video (test) |
|---|---|---|---|---|---|---|
| R02 | G3OMdQo1zjY_0-10-rgb_front | Mike Camelin (+ school / place names) | 3.31–7.50 | 1.43–11.69 | 0.41 | `raw_videos/G3OMdQo1zjY-10-rgb_front.mp4` |
| R05 | G3VM7etNABI_0-10-rgb_front | Les Whitley | 1.22–6.47 | 0.76–8.33 | 0.69 | `raw_videos/G3VM7etNABI-10-rgb_front.mp4` |
| R35 | G2kVb4gINSI_1-10-rgb_front | CarolAnn | 6.50–12.48 | 13.11–16.90 | **0.00** | `raw_videos/G2kVb4gINSI-10-rgb_front.mp4` |

The raw videos are present locally in `~/Desktop/curify/p018-work/downloads/test_raw_videos.zip` (test split; listed,
not extracted).

**R35:** the two windows do not overlap. If a fingerspelled name exists, it can be in either window or in neither.
The reviewer must see both.

## Feasibility steps (in order; each gated by the previous)

1. **Reviewer spans (blocking).** Send `asl_reviewer_request.md`. The reviewer fills `interval_labels.csv` blind
   first (letters seen), then unblinded (does it match the reference name?). Claude does not fill this file.
2. **Matched clip export (after reviewer agreement on the format).** Cut both windows from the raw source at native
   resolution with `ffmpeg`, with no re-scaling and no contact sheets. Kept local, not committed.
3. **Recognizer survey (can run in parallel with step 1).** List existing fingerspelling recognizers: input type
   (RGB vs landmarks), licence, whether weights are available, CPU runnability, and expected input format. Nothing
   is assumed to exist until verified.
4. **Dev comparison (only on confirmed spans).** Character error rate and exact name match, recognizer vs the
   current Uni-Sign output, on confirmed spans only.
5. **Local replacement test.** Replace a name only above a fixed confidence. Low confidence means no change. Log
   every replacement, wrong replacements, uncovered cases, and any whole-sentence damage.

## Exit conditions (frozen)

Pause P0-B if any of these hold:
- the name is not in the matched window;
- it is not fingerspelled;
- the frames are insufficient;
- no recognizer gives a reliable gain.

Never feed reference names as a candidate list, and never guess-complete a name. Needing a specialist trained from
scratch is not a low-cost fix and goes back to the boss.

## Blockers

| Blocker | Owner | Notes |
|---|---|---|
| ASL-fluent reviewer for 3 cases × 2 windows | Baobao / boss | The 45-clip ASL review is still pending. This request is small (about 6 short windows). |
| Recognizer availability and licence | Claude (survey) | Not yet surveyed. Commercial-use licence needed if it ever ships. |
| Official crop RGB is not stored locally | — | D-A windows can be cut full-frame from raw. The official crop box is not available as video. |
