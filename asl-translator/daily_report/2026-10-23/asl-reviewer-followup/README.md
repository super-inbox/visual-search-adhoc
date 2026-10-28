# ASL reviewer package — fingerspelling (R02/R05/R35) and utterance context (R26/R29)

**INTERNAL. Do not send this file.** It names targets, windows and model results that the reviewer must not see.
Read [REVIEWER_PACKAGE_MANIFEST.md](REVIEWER_PACKAGE_MANIFEST.md) for exactly what to send.

**Status (2026-10-27):** finalized for sending; **not yet sent**. All reviewer fields are blank. No ASL answer was
inferred or filled by us.
- The 2026-10-24 version was restructured after the boss's review ([PROGRESS_REVIEW.md](../../2026-10-25/PROGRESS_REVIEW.md)
  §3): its Step 2 located targets **after showing the reference text**.
- The clips are unchanged: the same 8 files with the same sha256.

## 1. Purpose

Independent human ASL annotation of the clips behind the open fingerspelling question (R02, R05, R35) and the
utterance-timing question (R26, R29).

The returned labels are the evidence that the saved Task 3 outputs (OpenFS letter strings, FS-Detection spans) and the
translation outputs can later be scored against. Those model outputs stay hidden from the reviewer.

## 2. Blind vs reference-conditioned

| Stage | What the reviewer sees | What it can support |
|---|---|---|
| **Step 1: blind** | Clips only. Each row has a clip file, its duration and a row type ("fingerspelling check" / "utterance boundaries") | **Independent human labels:** fingerspelling present, span, letters read, confidence, visibility; utterance boundaries |
| **Step 2: REFERENCE-CONDITIONED FOLLOW-UP** | A target the team selected **after consulting the English reference** (R02/R05/R35: the person name and reference sentence; R26/R29: the target sentence plus the sentences said before and after it) | **Annotation refinement only:** is the target actually signed, corrected span and letters. **Cannot** support any claim of blind detection, reference-free localization, or that an automatic system could find the span |

- Step 1 answers are never overwritten by Step 2.
- The two stages are separate files, separate pages and separate packages. Step 2 is sent only after the Step 1 file is
  returned.

## 3. Cases (8 clips, unchanged since 2026-10-24)

| row_id | Case / clip | Source span (s) | Window: what it is (internal) | Provenance (Task 2) |
|---|---|---|---|---|
| R02-old | R02 `G3OMdQo1zjY_0-10-rgb_front` | 3.31–7.50 (100 fr @24) | original-timing window = the B_ours_5p39 model-input window, full frame | B VERIFIED 3.333–7.500 (same 100 frames) |
| R02-official | same | 1.43–11.69 (246 fr) | realigned window = A_official window, **shown full frame** (not the official crop) | A VERIFIED 1.458–11.708 (246 frames) |
| R05-old | R05 `G3VM7etNABI_0-10-rgb_front` | 1.22–6.47 (125 fr) | B window, full frame | B VERIFIED 1.250–6.458 (125) |
| R05-official | same | 0.76–8.33 (181 fr) | A window, full frame | A VERIFIED 0.792–8.375 (182; the cut is 1 frame shorter) |
| R35-old | R35 `G2kVb4gINSI_1-10-rgb_front` | 6.50–12.48 (144 fr) | B window, full frame | B VERIFIED 6.500–12.500 (144) |
| R35-official | same | 13.11–16.90 (91 fr) | **annotation-defined realigned window**, full-frame cut of the raw video. Not the official crop clip | **A UNRESOLVED**: the official crop clip (93 frames) could not be uniquely placed in the source (Amendment 2 box margin 0.034 < 0.05) |
| R26-context | `G3EfBFwsOpE_3-10-rgb_front` | 11.75–16.75 (120 fr) | full-frame source context | — |
| R29-context | `92V3oH63zbQ_5-1-rgb_front` | 5.00–25.80 (624 fr @30) | one continuous clip, so a gap cannot hint at the target window | — |

All clips are cut from How2Sign **test** raw videos: native 1280×720 and fps, H.264 CRF 18, no audio, no overlays. The
holdout guard passed; there is no H18/H19 material. Source time = `source_start_s` (internal manifest) + clip time.

**R35 caveat:**
- The old (6.50–12.48) and official (13.11–16.90) windows **do not overlap**. They are separate events and must never
  be compared as the same signing.
- The official clip's timing is the realigned **annotation**. It is not a verified original-source alignment of the
  official input.
- If labels are later compared with outputs from the official crop clip (Task 3 ran OpenFS on both), that comparison
  is descriptive only.

## 4. Files

| File | Tracked | Send | What it is |
|---|---|---|---|
| `reviewer_instructions.md` | yes | **Step 1** | Short blind instructions. No targets, no model, no Step 2 content |
| `blind_review.csv` | yes (blank) | **Step 1** | Step 1 answer sheet: clip file, duration, row type; reviewer columns blank |
| `review_blind.html` | yes | **Step 1** | Step 1 form (loads clips locally, autosaves, exports `blind_review.csv`) |
| `package_local/clips/*.mp4` | no (excluded) | **Step 1** | The 8 clips |
| `package_local/send_step1_blind/` (+ `.zip`) | no | **Step 1** | Assembled Step 1: the 3 files above + `clips/` + `SHA256SUMS` |
| `reviewer_instructions_step2.md` | yes | **Step 2 only, after Step 1 returns** | Reference-conditioned instructions with the mandatory warning |
| `reference_conditioned_followup.csv` | yes (blank) | Step 2 only | Step 2 sheet: target + reference text pre-filled; reviewer columns blank |
| `review_reference_conditioned.html` | yes | Step 2 only | Step 2 form with a REFERENCE-CONDITIONED FOLLOW-UP banner |
| `package_local/send_step2_reference_conditioned/` (+ `.zip`) | no | Step 2 only | Assembled Step 2 + `SHA256SUMS` (no clips; the reviewer reuses Step 1's) |
| `README.md` | yes | **never** | This file |
| `REVIEWER_PACKAGE_MANIFEST.md` | yes | never | Send / internal list |
| `reviewer_package_manifest.csv` | yes | **never** (sent in the 2026-10-24 version; now internal) | Source spans, domains, source and clip sha256, P0-12 model-input paths |
| `reviewer_labels.csv` | yes | **never** (superseded) | 2026-10-24 combined sheet. It mixed Step 2 columns into Step 1. Kept blank for the record |
| `build_reviewer_package.py` | yes | never | `build` (cut clips + manifest), `package` (assemble both stages from sha-verified clips; byte-identical rebuilds), `derive` |
| `package_local/_superseded_2026-10-24/` | no | **never** | The previous local package, moved aside, not deleted |

## 5. What the evidence can and cannot support

**Step 1 can support** independent human labels per clip:
- `fs_present`;
- span (`fs_start_s` / `fs_end_s`);
- letters read (`fs_letters_or_word`, `?` = unreadable);
- `fs_confidence`, `fs_type`, `hand_visibility`, `issue_flags`;
- R26/R29 utterance boundaries.

These can serve as ground truth for scoring recognizers and detectors.

**Step 2 can support** annotation refinement only:
- is the reference-selected target actually signed;
- the corrected span and letters.

**Step 2 cannot support:**
- a claim that the span is recoverable without the reference;
- that a detector or any automatic method found it;
- that fingerspelling was detected blind.

R26/R29 target spans and the `derive` output are reference-conditioned diagnostics. Any input correction defined from
them must be labelled "human, reference-conditioned".

## 6. Scoring after labels return (internal; not run yet)

Time base: reviewer clip seconds. Add `source_start_s` from `reviewer_package_manifest.csv` for source seconds.

- **OpenFS** (`experiments/p0-2026-10-27/results/specialist_openfs_{official,reproduction}.json`):
  - The official R02/R05/R35 runs used **these exact reviewer clips** (same sha256), so the time base is the same.
  - The old-window runs used the How2Sign v2 B clips: same window, start within 0.03 s.
  - Score the character error rate of the window strings overlapping a Step 1 span against `fs_letters_or_word`.
  - Report separately against Step 2 `corrected_letters`, labelled reference-conditioned.
- **FS-Detection** (`experiments/p0-2026-10-27/results/fs_detection_feasibility.json`, R02/R05 official):
  - Its `clip_start_s` / `clip_end_s` are seconds in the same reviewer clips (resampled to 29.97 fps).
  - Score temporal IoU and hit@0.5 against Step 1 spans. Step 1 is the only valid ground truth for a detector.
- **Translation outputs:**
  - Uni-Sign (P0-A candidates, inspection sheet) and production (`inspection_sheet_with_production.csv`).
  - Whether a Step 1-read name or letters appear in the output is descriptive only. Matching against the reference
    name uses Step 2 and is reference-conditioned.
- The labels go into `../p0b-fingerspelling-feasibility/interval_labels.csv` by script:
  - Step 1 → blind fields;
  - Step 2 → `*_after_unblind` fields.
- With one reviewer, report agreement as not available.
- `fs_present` stays unknown for any clip without a returned label.

## 7. Rebuild

```bash
python -I build_reviewer_package.py package   # from package_local/clips (sha256-verified against the manifest)
python -I build_reviewer_package.py build     # only to re-cut clips from p018-work/downloads/test_raw_videos.zip
```

Both refuse to overwrite a sheet that already holds reviewer answers.
