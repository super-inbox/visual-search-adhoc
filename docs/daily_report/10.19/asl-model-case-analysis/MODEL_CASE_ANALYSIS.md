# ASL model case analysis: 45 review clips

**Status: model_review / unverified.** A model (Claude Opus 5.5, `claude-opus-5-5`) reviewed each of the 45 clips of
the 10.18 review package. This is **not** an ASL-fluent human verification. No row is `human_verified`, and the human
review fields are copied through blank (`review_status = not_started`). Every model diagnosis is in a `model_*` column
with `model_label_source = model_review` and `model_label_status = unverified`, kept separate from the automatic weak
labels (`initial_*`, `automatic_weak`) and from the human fields.

## What the model saw

- **Input:** timestamped contact sheets of each clip (`scripts/build_contact_sheets.py`): 4 fps, centre 720×720 signer
  crop scaled to 300 px, 24 frames (6 s) per sheet, 80 sheets for 360 s of video. Stills only: **no motion, no audio,
  no mouthing detail**. Fingerspelled letters and the movement of signs (shake, circling, headshake) cannot be read at
  this resolution and frame rate.
- **Text per clip:** ground truth, our/old output (`B_ours_5p39`, **provisional**, not confirmed as live production),
  official Uni-Sign output, and the existing automatic error types and weak labels.
- **Rule:** `model_visible_description` lists only physical observations (hand location, handshape type, timing,
  rest periods). Readings such as "fits ASL NINE" appear only in `model_evidence`, always worded as consistent with or
  unverified. Where the video does not settle the question, it goes in `model_unresolved_ambiguity`.
- **Window caveat:** the videos are the clips cut at the original How2Sign timestamps, which is our input window. On
  R03, R18, R36 and R42 the official input window is different (re-aligned), so the official model saw material that
  is not in the video, or less of it.

## Main findings (model, unverified)

1. **The reference often does not fit the visible signing.** R10 is idle for 15 s of its 25 s (hands in the lap; the
   signer yawns). R29 is mostly idle, with about 0.5 s of signing for a full question. Long idle stretches also occur in
   R03, R04, R14, R23, R36, R38 and R44. In R02, R04, R29 and R38 the reference contains more than the signing in the
   window could hold. Some "errors" here are alignment or segmentation problems, not translation errors.
2. **Some references and weak labels are artifacts.**
   - R08: "ALVIN DEDEUX:" is a transcript speaker label, which explains its fingerspelling label.
   - R11: the reference contains a parenthetical song lyric.
   - R28: the reference has mojibake ("you?re").
   - Weak-label false positives: R07 (the name *Barbie* is kept as "Barbie's") and R10 ("two parts" for
     "double-stops" counted as a number).
   - R22: the "negation inserted" weak label may not be an error, because a thumb-under-chin handshape (the NOT
     location) is visible at 0.5–0.75 s.
3. **The two systems usually fail together.** Shared failure is yes in 22 clips, partial in 16 and no in 7. Both lose
   names and fingerspelled content (R02, R04, R05, R06, R14), numbers (R17 TEN, R19 ordinals, R21 45/8) and visible
   content (R27 nose grasp). Where they differ, the official output is usually the closer one (R30, R32, R33, R40,
   R41, R43, R45). The official output also invents a "Hi, I'm <name>" introduction where none exists (R04, R13).
4. **Partial letter recovery.** Both systems produce "Albur(n)…" for *Albondigas* (R06) and an A-initial word for
   *ascot* (R14). The official output gives "IgG" for *Yu-Gi-Oh* (R09), "Lisa" for *Les* (R05) and "Colin" for
   *CarolAnn* (R35). This is consistent with spelled input being partly decoded, but unverified.
5. **Location-driven substitutions.**
   - Mouth and teeth signing gives "lipstick" (R34).
   - Head and face signing gives "eyes / ears / face" (R42).
   - Brow signing gives "eye" (R44).
   - Hand-on-palm push-up movement gives a repeated "squeeze down" (R35).

## The 9 official-output repetition cases

| ID | official input | loop | what the video shows (model) | reading |
|---|---|---|---|---|
| R03 | 19.52 s (long) | mild phrase repeat ("my C.V.") | varied signing, 2.75 s idle start; clip ≠ official window | decoder repeat, not visually seeded |
| R11 | 18.20 s (long) | "ready to go" ×6, **same loop in ours** | only 0–2.5 s is repetitive (cyclic mashing); rest varied | lock-in after a partly correct prefix ("Ready to" is in the reference); preparation-independent |
| R16 | 8.32 s (= ours) | "doesn't matter where you are" ×2+ | palms-up gesture recurs twice | possible visual seed; window/length not the cause |
| R18 | 5.91 s | "four sleeves" ×2 | one FOUR handshape (3.0 s), recovered by both | mild; number itself correct |
| R20 | 16.42 s (long) | "bounce back and forth" ×3 | **repeated side-to-side flat-hand movement 12–17.5 s** | loop may be a mis-worded but genuinely repetitive depicting movement |
| R36 | **32.54 s** (longest) | "typical" ×30 | varied content, fingerspelling-like runs, no repeats | single-token degenerate loop; clearest long-input case |
| R39 | 5.76 s (≈ ours) | "hit the ball with your index finger" ×3 | same hand-on-palm configuration twice | visual seed possible; 3 long repeats exceed it |
| R42 | **4.02 s** (shorter than this clip) | "a lot of that in literacy" ×2 | dense face/head signing | **loops on a short input**: not a long-input failure |
| R44 | 23.39 s (long) | "top of the eye" phrase repeats | brow/eye-region signing recurs | grounded in repeated locations, "brow" mis-worded as "eye" |

From the video, the model reads these repetition cases as follows. The official repetition is not explained by input
length alone. R42 loops on a 4 s input, R16 and R39 loop on medium inputs where both systems saw the same window, and
R11 gives the same loop under both preparations. In R20, R44 and possibly R16 and R39, the repeated phrase lines up
with something that really does repeat on screen. In R36, R03 and R11, nothing on screen repeats. This supports the
10.18 audit reading: the decoder has its own repetition failure, and long inputs raise the risk. The R01 official
output also loops ("a D," ×22), but its automatic primary type is *hallucination*, so it is not among the 9. R19
("the brew" ×4) is in the same position.

## Model categories (primary, unverified)

general_semantic 11, repetition 9, number 6, fingerspelling 5, name 4, question 4, negation 3, spatial_relation 3.
Confidence: medium 23, low 22, high 0. The model rated no diagnosis high, because stills cannot settle what is signed.

## Cases the model cannot confidently interpret

- **Low-confidence diagnoses (22):** R01 R03 R09 R12 R14 R15 R16 R17 R19 R20 R21 R22 R24 R25 R26 R28 R33 R35 R38
  R39 R41 R45.
- **Too short or too occluded to describe reliably:**
  - R09 and R15 have 5 frames each.
  - R26 has its hands above the frame.
- **Spelled content not legible:** R02, R04, R05, R06, R09, R14, R35, R36 and R38. The model could not read any
  fingerspelled letters.
- **Negation and questions need motion or non-manual markers** (headshake, brows) that stills do not show: R04, R12,
  R14, R15, R22, R23, R24, R25, R26, R27 and R29.

All of these need an ASL-fluent reviewer working from the video, through the 10.18 `inspection_sheet.html`.

## Files

| File | What it is |
|---|---|
| `model_case_analysis.csv` | 45 rows: context + automatic labels + `model_*` analysis + blank human fields (38 columns) |
| `model_case_analysis.html` | Review page: video, three texts, AUTO (yellow), MODEL (purple) and HUMAN (green, blank) panels shown separately; filter by model category, confidence, official loops |
| `MODEL_CASE_ANALYSIS.md` | This summary |
| `CODEX_REVIEW_PROMPT.md` | Instructions for an independent second model pass (e.g. Codex) on the same inputs |
| `scripts/build_contact_sheets.py` | Builds `contact_sheets/` from the 10.18 package (byte-identical rebuilds) |
| `scripts/build_model_case_analysis.py` | Holds the per-case model analysis; writes the CSV and HTML, and checks that human fields stay blank |
| `contact_sheets/` (**local only, git-ignored**) | 80 JPEG sheets derived from How2Sign clips (CC BY-NC 4.0) |

```
python3 -I scripts/build_contact_sheets.py ../../10.18/asl-review-inspection-sheet contact_sheets
python3 -I scripts/build_model_case_analysis.py
```

The inputs were the 10.18 `inspection_sheet.csv`, `repetition_audit.csv` and `videos/`, plus the review package zip
`~/Desktop/curify/asl-review-package/asl_inspection_review_package.zip`, which was not modified. Before the review the
zip had sha256 `b1728e39b8d139a9160bcfc813c240521f3865668700195ef76846652deea02a`, was 60,239,549 bytes, and all 45
internal checksums were OK. No H18/H19 data or P0-18 files were opened or changed.
