# ASL-fluent reviewer follow-up — P0-B and P0-C blockers (2026-10-24)

**Status: package built locally and not yet sent. All reviewer fields are blank.** Claude does not infer or fill ASL answers.
Protocol: [P0_PROTOCOL_FREEZE.md](../P0_PROTOCOL_FREEZE.md) §2–§3 (unchanged). Background:
[P0-B FEASIBILITY.md](../p0b-fingerspelling-feasibility/FEASIBILITY.md), [P0-C source_check.md](../p0c-input-correction/source_check.md).

This team-facing file is **not** sent to the reviewer. It names hypotheses and windows that the reviewer must not see.

## Files

| File | Tracked | Sent to reviewer | Purpose |
|---|---|---|---|
| `README.md` | yes | **no** | This file |
| `reviewer_instructions.md` | yes | yes (step 1) | The exact questions |
| `reviewer_labels.csv` | yes (blank template) | yes (step 1) | The answer sheet: 8 rows, provenance pre-filled, reviewer columns blank |
| `reviewer_package_manifest.csv` | yes | yes (step 1) | Per clip: source video, domain, source span, frames, source and clip sha256, P0-12 model-input pkl and sha256 |
| `build_reviewer_package.py` | yes | no | Rebuilds everything below. Refuses to overwrite a label sheet that has answers. `derive` mode for R26 after the review |
| `package_local/` | **no** (`.git/info/exclude`) | yes | `step1_blind/` (+ `.zip`): 8 clips, instructions, blank labels, manifest, `SHA256SUMS`. `step2_unblind/` (+ `.zip`): `UNBLIND_REFERENCES.md` |

Rebuild: `python -I build_reviewer_package.py build` (local CPU; extracts 5 test raw videos from
`p018-work/downloads/test_raw_videos.zip` to a temporary folder and deletes them afterwards). It opens only test files.
The holdout guard runs on all 5 clip IDs, and any path containing val/H18/H19 is refused.

## Reviewer rows (8 clips)

| row_id | Clip ID | Domain | Source span (s) | Clip |
|---|---|---|---|---|
| R02-old | `G3OMdQo1zjY_0-10-rgb_front` | B_ours_5p39, old preprocessing (original timing) | 3.31–7.50 | 100 fr @24 |
| R02-official | same | A_official, official preprocessing (realigned timing) | 1.43–11.69 | 246 fr @24 |
| R05-old | `G3VM7etNABI_0-10-rgb_front` | B_ours_5p39 | 1.22–6.47 | 125 fr @24 |
| R05-official | same | A_official | 0.76–8.33 | 181 fr @24 |
| R35-old | `G2kVb4gINSI_1-10-rgb_front` | B_ours_5p39 | 6.50–12.48 | 144 fr @24 |
| R35-official | same | A_official | 13.11–16.90 (no overlap with old) | 91 fr @24 |
| R26-context | `G3EfBFwsOpE_3-10-rgb_front` | full-frame source context | 11.75–16.75 | 120 fr @24 |
| R29-context | `92V3oH63zbQ_5-1-rgb_front` | full-frame source context | 5.00–25.80 (one continuous clip covering ~5–10 and ~11.6–25.8 s, plus the target window between them) | 624 fr @30 |

All clips are full frame at native 1280×720 and native fps, H.264 CRF 18, no audio and no overlays. The start is frame-accurate
to ±1 frame. A_official clips are shown full frame because the official crop is not available as video. The reviewer
answers in **clip seconds**. Source time = `source_start_s` + clip time.

**R29 design choice.** The two requested spans (~5–10 s, ~11.6–25.8 s) are delivered as **one continuous clip** that
also contains 10.03–11.86. Two separate clips with a gap would mark the target window and hint at our hypothesis.

## Blinding

- **Step 1 (blind):** clips only. No English text, no reference names, no target sentence, no window hypotheses.
- **Step 2 (unblind, sent after step-1 answers are returned):** P0-B reference sentences (names), and the P0-C target
  sentence with the English sentences said immediately before and after it, as **text only**. No timestamps.
- **Never shown to the reviewer:**
  - the R26 official window 15.15–16.62 s and our framing finding;
  - R29's realigned neighbour boundaries (`_4` 11.70–16.51, `_6` 16.59–25.81) and the "realigned == original" observation;
  - any model output.
- **P0-C note.** Locating a sentence needs its English text, so the P0-C target is given only in step 2. Step 1 records
  blind utterance boundaries first, so the target placement can be checked against a reference-free segmentation.
- **R26 containment** in the official window is **not asked**, because asking would reveal the window. It is derived after the
  review: `python -I build_reviewer_package.py derive reviewer_labels.csv` prints the target source span, `fully_contained`
  and the overlap with 15.15–16.62 s.

## Exact reviewer questions

P0-B rows (each clip separately, blind):
1. `fs_present`: Is there fingerspelling in this clip? `yes` / `no` / `unsure`
2. `fs_start_s`: exact start time (clip seconds)
3. `fs_end_s`: exact end time (clip seconds)
4. `letters_seen_blind`: blind letter reading, `?` for unreadable letters, no guess-completion
5. `fs_type`: `fingerspelling` / `name sign` / `lexicalized fingerspelling` / `unsure`
6. `hand_visibility`: `good` / `partial` / `poor`

Plus `notes_blind`. Several spans go on extra rows (`span_no`). Unblinded: `reference_name_after_unblind`,
`matches_reference_name` (`yes` / `partly` / `no` / `cant_tell`), `notes_after_unblind`.

P0-C rows:
- Blind: `utterance_boundaries_blind_s` (sentence/utterance boundary times), optional gloss in `notes_blind`.
- Unblinded:
  - `target_found` (`yes` / `partly` / `no` / `unsure`);
  - `target_start_s` and `target_end_s` (clip seconds);
  - `target_confidence` (`high` / `medium` / `low`).

Reviewer: `reviewer_id`, `asl_background`, `step1_completed_at`, `step2_completed_at`.

## Decisions that become possible after the review

**P0-B (protocol §2 exits are applied in order):**
- `fs_present = no` in both windows, or only a name sign → the case **exits** ("not fingerspelled").
- Fingerspelling only in the window the model did *not* use → that domain exits ("name not in matched window"). R35
  matters most, because its windows do not overlap.
- `hand_visibility = poor` → exit ("frames insufficient").
- Otherwise the confirmed spans become recognizer input:
  - A tiny install check on the repos' own samples comes first.
  - Then OpenFS and HandReader-KP run on MediaPipe re-extractions of exactly those spans.
  - Character error rate is scored against `letters_seen_blind`, and separately against the reference name.
- If no case survives, **P0-B stops** with no recognizer run.
- The answers are copied verbatim into `../p0b-fingerspelling-feasibility/interval_labels.csv` by script. That file stays
  blank until then.

**P0-C:**
- **R26.** Compare the target span with the official window (`derive`).
  - Fully inside 15.15–16.62: the official input already covers it and framing is ruled out, so **R26 stops** with no correction.
  - Outside or partly outside: a single timing correction can be defined from the reviewer's span (not from official
    boundaries), written and dated in `case_inputs.csv`, then decoded once (protocol §1.3 T settings).
  - `target_found = no/unsure`: R26 stops.
- **R29.**
  - If the reviewer places the target outside 10.03–11.86: one corrected window = the reviewer's span, written and dated
    in `case_inputs.csv` before decode.
  - If it is inside, or `unsure`: R29 stops with no correction.
  - The blind boundaries show whether the span is recoverable without reference text, which is the "could this be
    automated" question in §3.
- **Either case.** A corrected decode still needs the P0-18 `pose_extract.py` CPU extraction of the corrected window.
  Results are reported with the §1.6 outcome labels plus recovered / omitted key content.
