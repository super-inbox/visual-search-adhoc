# Label leakage in the ASL corpus — found 2026-08-30

Two of the thirteen corpus videos had the reference answer burned into the frame the
model was reading. One of them was the corpus's primary accuracy anchor.

## What happened

`videos/155_demo_asl-demo-translation_26.7s.mp4` was byte-identical
(md5 `d714db71628698cd99c3b6bcfadfe2c1`) to
`curify-frontend/public/video/asl-demo-translation.mp4` — the **published marketing demo,
which is the tool's own output with English captions burned in**. The corpus took the
*output* video as the *input*.

The manifest even recorded the provenance — *"Curify's own demo asset, already public at
/video/asl-demo-translation.mp4"* — but read it as low risk rather than as the answer key.

## Evidence

1. **The prediction is the reference, verbatim.** `predictions_eval/155_..._temperature0.json`
   reproduces the gold SRT word for word including punctuation
   ("My family has five, including my father."), with **0 substitutions and 0 deletions**.
2. **PSNR against the clean twin**: 28.1 dB full-frame, **47.1 dB excluding the bottom
   third**. Same footage; all the difference is in the caption band.
3. **The "duplicate segments" were two batches reading the same caption.** Segments 3+4
   span 8.88–12.65 against a caption window of 8.867–12.833; segments 6+7 span 18.48–20.42
   against 18.2–20.3. The union of each pair is the on-screen caption's display window.
4. **OCR**: sampling the caption band returns the gold text at every timestamp on the
   contaminated file, and nothing but noise on the clean one.

`1320_1000022357_137.2s.mp4` carries burned-in captions the same way, across ~69% of its
duration. It had correctly been walled off as a `candidate_reference`, but for a different
reason ("production direction unconfirmed") — not because the input leaks the label.

**No other corpus video is affected.** All 13 were re-checked frame by frame; the result
matches `VIDEO_TYPE_AUDIT.csv`'s own `burned_in_captions` column, which had recorded the
burn-in on exactly these two and still marked both
`suitable_for_asl_translator_evaluation = yes`, citing the captions as corroboration that
the signing matched. The fact was captured; the consequence was never drawn.

## What is retracted

Everything scored on 155:

| Retracted | Was |
|---|---|
| 155 baseline0 | WER 0.3704 / CER 0.3485 / IoU 0.7095 |
| 155 temperature0 | WER 0.3333 / CER 0.3409 / IoU 0.7049 |
| 155 temperature0 **after dedup** | WER 0.0000 / CER 0.0000 — the "exact match against the human reference" |
| Pooled/micro WER over "79 reference words" | baseline0 0.7342, temperature0 0.7215 — pooled a clean case with an OCR case |
| "On well-framed slow content the recogniser is essentially correct" | rested entirely on 155 |

Deduplication itself is **not** retracted. Batch-boundary duplication is a real artifact of
the stateless `frames[i:i+BATCH_SIZE]` batching and the fix stays in production. Only its
*measured* benefit is withdrawn: it is now an unmeasured fix.

## What still stands

- **1252** — clean input, verified human reference. WER 0.9231 under both configs. This is
  now the **only** defensible accuracy measurement in the corpus, n=1.
- **`DETERMINISM_EXPERIMENT_V1.md`** — 1466/1467 are clean. Repeatability WER 0.9706 → 0.1786
  and IoU 0.4631 → 0.9085 under `temperature=0` are unaffected.
- **`SIGNCAPTION_COMPARISON_V1.md`** — 1467/1474/1477 are clean, and those comparisons were
  never accuracy claims to begin with.
- The corpus authenticity audit (12 confirmed signing, 1 uncertain, 0 non-ASL).

## What changed on disk

| Path | Change |
|---|---|
| `ground_truth/155_..._burned_marketing.mp4` | the contaminated file, moved out of `videos/` |
| `videos/155_....mp4` | replaced with the raw demo source (md5 `d71313d0…`, 1,481,524 B) |
| `ground_truth_candidates/1320_..._burned.mp4` | the unmasked source, moved out of `videos/` |
| `videos/1320_....mp4` | conditionally masked render (see below) |
| `manifest.json` | `label_in_input` per video; `input_mask` and `input_provenance` blocks |
| `evaluation_set.json` | 155 moved to `excluded`; 1320 points at the masked input |

### How 1320 was masked

The caption band is masked **unconditionally, on every frame**, and the two
title/instruction cards are blacked out entirely.

- caption band `y=795 h=155`, full width, all 4112 frames
- full-frame black where the signer is absent: `t < 15.0` and `t > 132.1`
  (the cards leak the topic — `CATEGORY: RELIGIOUS` — and the exercise instructions)
- re-encoded libx264 crf 18; duration and frame count unchanged (137.203733s, 4112 frames)

**Masking only the captioned frames was tried first, and rejected.** The idea was to
preserve signing in caption-free stretches, since the signer's hands do enter the band
when she is at rest. It produced a video with **14 holes totalling ~22 seconds in which
the captions were still on screen** — the OCR-derived intervals missed caption onsets and
offsets, and a sampled OCR sweep of the result reported it clean. A verification that can
miss 22 seconds of visible answer is not a verification.

Unconditional masking has no intervals to get wrong, and the cost was measured before
choosing it: **8 frames — 0.3 seconds out of 137 — where the signer's hands are in the
band during active signing.** Everywhere else her hands are in the band only at rest, and
during captioned frames the caption box already occluded that region.

**Verified exhaustively, not by sampling**: crop the band, reduce to 16×4 grayscale, and
check every frame — the band is fully black in **4112 of 4112**. Sampled OCR is not
sufficient to verify a mask and should not be used for it.

### A resolved question, found along the way

OCR of 1320's title cards reads *"Certificate Program for Sign Language Interpreters —
RECEPTIVE SKILLS EVALUATION"*, *"SIGN TO VOICE"*, *"Record yourself voicing the video"*.
It is an **interpreter certification exercise**: the ASL is the source and the burned
captions are the answer key. That settles the production-direction question the spec had
recorded as blocking (§9.5). What remains before the candidate reference can be promoted
to gold is an annotator confirming the caption text against the actual signing.

## The guard

`asl-eval/check_leakage.py` OCRs a sample of frames from every corpus video and fails on
any video whose on-screen text overlaps its own reference. It runs **two passes per frame** —
the whole frame upscaled, and the bottom third upscaled — because tesseract reads nothing at
all from 155's captions on the native 640×360 frame and reads them perfectly from an upscaled
crop. A full-frame-only checker would have declared the very file that caused this problem
clean. It is validated against both known positives on every run.

**Measured separation**, whole corpus, 2026-08-30:

| File | frames with text | overlap with its own reference | verdict |
|---|---|---|---|
| `155_…_burned_marketing.mp4` | 7 | **0.97** | leaks |
| `1320_…_burned.mp4` | 55 | **0.85** | leaks |
| `videos/155_….mp4` (clean swap) | 0 | 0.00 | clean |
| `videos/1320_….mp4` (masked) | 0 | 0.00 | clean |
| `1415` (a "Professor Weingart" watermark) | 95 | 0.00 | text, but not the answer |
| `1457` (chat-app UI), `1434` (player chrome), `1442`, `1252_250.8s` | 2–14 | 0.00 | text, but not the answer |

The threshold is 0.30, and nothing lands near it: contaminated files sit at 0.85–0.97 and
incidental on-screen text at 0.00. **Detecting text is not the same as detecting leakage** —
five clean videos have text on screen, and flagging those would have made the check noise
that someone would eventually switch off.
`asl-eval/evaluate.py` refuses to score any item with `label_in_input: true` unless a
verified `input_mask` is declared, and `run_current_model.py` records the `input_md5` of
the file it actually read — the missing provenance field that let a prediction point at
the wrong file unnoticed.
