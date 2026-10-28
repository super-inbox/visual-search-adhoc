# Production 45-Case Evaluation

**Date:** 2026-10-27.
**Status:** run complete, automatic metrics only. Human semantic labels are pending for every case.

## Executive Summary

**What was tested:** the current production ASL path, curify-studio `origin/main` `4220e03c` (2026-10-26),
`asl_utils.transcribe_asl()`.
- Model: `gemini-2.5-flash`, temperature 0, JSON response, with motion-probed adaptive frame sampling.
- It ran on the R01–R45 inspection-sheet videos.
- The production code was invoked as-is from a read-only export; it was not ported.

**Coverage:**
- **45 cases processed; this is not 45 clean transcripts.**
  - 44 produced transcript text.
  - **R29 is a valid EMPTY / no-signing result:** the model returned no segments ("No signing was observed…"), which
    production surfaces as "no signing detected". It is scored as an empty output and was not re-run.
  - **R03 is a PARTIAL result:** one of its two batches returned malformed JSON, production's real parser dropped it,
    and only "I know now." remains. This is observed end-to-end production behaviour; it was not repaired or re-run.
- No transport errors and no retries.
- **57 Gemini calls, 1,233 frames, 457,707 total tokens.**

**Corpus metrics (45 cases; production vs Uni-Sign).**
- Production: chrF **9.27**, BLEU-4 0.17, WER 98.25, mean length ratio **0.38**.
- Uni-Sign on the same B-window video, P0-A CPU: chrF 18.22, BLEU-4 1.70, WER 99.81, length ratio 1.02.
- Uni-Sign on the official A-domain input: chrF 23.76.

**Comparison:**
- Production has lower sentence chrF than Uni-Sign on 41/45 (B, P0-A CPU) and 44/45 (A, P0-A CPU) cases.
- Its outputs are much shorter: median 5 words vs 15 in the reference, and 17 outputs have ≤ 3 words.
- Its slightly lower WER mainly reflects producing fewer words; it does not indicate more correct content.
- It produces no repetition loops (0 vs 11/9 for Uni-Sign).

**Limitations:**
- automatic metrics are not semantic judgement;
- production and Uni-Sign use different inputs and preprocessing;
- this is an end-to-end comparison, not an ablation;
- n = 45, and this is a worst-first exploratory sample.

## Production-Path Verification

| Item | Value | How verified |
|---|---|---|
| Code | curify-studio `origin/main` `4220e03c0c0c5c4010ddc6ffc8c0d5379d0dc48b`, `curify_background/app/utils/asl_utils.py` (sha256 `90df9563…`) | `git fetch` then `git archive origin/main` (read only). The local checkout is 111 commits behind and was not touched |
| Product entry | `pipelines/asl_pipeline.py` → `transcribe_asl(paths.local_video_path)` with defaults (`provider="gemini"`, `frame_budget=None`) | read on `origin/main` |
| Model | `gemini-2.5-flash` (`ASL_MODEL`). Every response reports `model_version` `gemini-2.5-flash` | code + 57/57 responses |
| Prompt | `_PROMPT` (sha256 `ea8c5cb1…`): translate to natural English, timestamped caption segments, omit non-signing, report doubt in `notes`, STRICT JSON. It does **not** say to ignore on-screen text | code |
| Generation | `response_mime_type="application/json"`, `temperature=0.0`. Thinking left at the model default | code + recorded config of all 57 calls |
| Sampling | 4 fps grayscale motion probe (160 px) → active/idle runs (35th-percentile threshold, absolute floor 2.0) → budget = clamp(round(2 × duration), 24, 240) frames, allocated across active runs by motion energy (≥ 2 per run) → 512 px JPEGs with `[t=…s]` labels, 24 frames per call | code |
| Post-processing | segments sorted, empty dropped, adjacent identical captions within 1.0 s merged; flags `low_density` (< 1 frame/s) and `degenerate_repetition` | code |
| Retry | Only at the job-queue level, on transport errors. Not reproduced here (none occurred) | `asl_pipeline.py` |

**Historical offline runner:** `asl-eval/run_current_model.py --config production_2026_08_29` **still matches**.
- Production changed after its parity point `f42a3a44`, but only in the docstring, error classification
  (`had_transport_error`, `NoSigningDetectedError`), runtime-config merging and image watermarking. None of these
  changes what reaches the model.
- Its `TestProductionParity` passes **6/6** against the current `origin/main` file: constants, model, prompt, budget
  curve, normalization, dedup.

**What actually ran:** `asl-eval/run_production_45.py`, which loads the **production `asl_utils.py` itself** and
calls `transcribe_asl`. Only one dependency is stubbed:
- `app.services.imagen_service.get_gemini_client`, mirroring production (`genai.Client(api_key=GEMINI_API_KEY,
  HttpOptions(timeout=60000))`);
- `is_quota_exhausted`.

Two pass-through wrappers record data without changing behaviour:
- the selected timestamps;
- each call's model version, usage, latency and raw response.

**Not exercised:**
- the DB/credits/storage side effects;
- the later translate/subtitle/mux steps;
- the "[AI-generated ASL translation — unverified]" caption prefix.

The English text of `transcribe_asl` is what those steps consume. No production code was modified and nothing was
deployed. The API key was loaded only from the user-designated file, only `GEMINI_API_KEY`, into the wrapper process;
it appears in no log or output file (checked programmatically).

## Dataset / Input Set

- **Cases:** R01–R45, the 10.18 inspection-sheet set (= 10.13 package order). The P0-16 holdout guard passed; no
  H18/H19.
- **Input:** each case's inspection-sheet video `docs/daily_report/10.18/asl-review-inspection-sheet/videos/<clip>.mp4`.
  - This is the How2Sign v2 clip, full frame 1280×720, i.e. the **B_ours_5p39 window**: original How2Sign timing,
    except R10/R14.
  - sha256 matches the sheet manifest on 45/45.
  - This is the representation the inspection workflow plays and the closest to a user upload.
  - The official A crops are **not** mixed in.
- **Provenance of the B window:**
  - 42 VERIFIED;
  - **R10, R14: timing-label MISMATCH** (the window is the measured re-aligned interval, not original timing);
  - R32: source interval UNRESOLVED (the video itself is fixed and hash-verified).
- **Duration:** 1.15–25.77 s, 360 s in total.
- **Frames sent:** 24–51 per case (the 24-frame minimum governs every clip under 12.25 s), 1–3 calls per case.
- **References:** 10.13 `inputs_128.jsonl` (sha256 `1c7336c4…`). These equal the sheet's `ground_truth` on 45/45 and
  are How2Sign English translations, not glosses. They were used only for scoring and **never sent to the model**:
  each request is the fixed prompt plus a `[t=…]` label and an image per frame.

Manifest: `asl-translator/asl-eval/production_45/production_45_manifest.csv`.

## Results

**Run:**
- 57 calls, all `gemini-2.5-flash`, the same config throughout, 0 transport errors.
- 1 response was unparseable by production's JSON parser: R03 batch 0, missing `}` after the first segment. Production
  drops that batch's 4 captions and keeps batch 1.

**Tokens:**
- prompt 343,373;
- output 6,007;
- thinking 108,327;
- total **457,707**.

**Latency per case** (probe + extraction + calls): min 3.2 s, median 11.1 s, max 43.5 s, sum 678 s.

**Flags:**
- `low_density`: 0;
- `degenerate_repetition`: 0;
- the model self-reported confidence "high" on 47/57 calls and "medium" on 10. This is not ground truth.

### Corpus metrics

All rows cover the same 45 cases; R29 counts as an empty output. Metrics are the P0-A definitions: chrF/BLEU-4 with
sacrebleu defaults, WER on lowercase whitespace tokens ×100, mean output/reference word ratio, and `loop_out` per
§1.4.

| System | Input | chrF | BLEU-4 | WER | len ratio | loop_out | empty |
|---|---|---|---|---|---|---|---|
| **Production (gemini-2.5-flash)** | B-window video, adaptive frames | **9.27** | **0.17** | **98.25** | **0.38** | 0 | 1 |
| Uni-Sign B, P0-A CPU (reproducible) | B-window pose (`B_ours_5p39`) | 18.22 | 1.70 | 99.81 | 1.02 | 11 | 0 |
| Uni-Sign B, sheet `prod_output` (P0-12 T4/fp16, historical) | same | 18.35 | 2.25 | 99.61 | 0.98 | 12 | 0 |
| Uni-Sign A, P0-A CPU (reproducible) | official pose (`A_official`, re-aligned window) | 23.76 | 5.72 | 95.44 | 1.00 | 9 | 0 |
| Uni-Sign A, sheet `unisign_output` (T4/fp16, historical) | same | 23.58 | 5.92 | 96.70 | 1.01 | 11 | 0 |

### Case level (production)

- **Sentence chrF:** min 0.0, median 6.03, max 19.24 (mean 8.05).
- **Sentence WER:** min 87.5, median 100.0, max 131.8. 29/45 are exactly 100.
- **Output length:** median 5 words (0–29). The reference median is 15. In total, 376 output words vs 1,030 reference
  words.
- **Empty or ≤ 3 words:** 17 cases — R01, R02, R03, R04, R15, R17, R22, R24, R25, R26, R27, R28, R29 (empty), R32, R33,
  R37, R41.

## Comparison with Uni-Sign

Pairs are per case (production − Uni-Sign). A and B are kept separate. Each Uni-Sign source has its own row.

| Production vs … | chrF higher / lower | WER better / worse / tie | mean / median Δ chrF | mean / median Δ WER |
|---|---|---|---|---|
| sheet `prod_output` (B, T4/fp16, historical) | 5 / 40 | 13 / 21 / 11 | −9.73 / −10.73 | −11.69 / 0.00 |
| P0-A CPU B (`B_ours_5p39`) | 4 / 41 | 13 / 21 / 11 | −9.35 / −10.48 | −16.97 / 0.00 |
| P0-A CPU A (`A_official`) | 1 / 44 | 15 / 25 / 5 | −17.42 / −15.21 | −2.14 / +6.82 |
| sheet `unisign_output` (A, T4/fp16, historical) | 3 / 42 | 14 / 27 / 4 | −17.34 / −15.20 | −3.00 / +7.27 |

**How to read WER here:** production's "WER better" cases are mostly short outputs. Deleting words costs at most the
reference length, while Uni-Sign's long or looping outputs add insertions. Example: R26 "Various things", ΔWER −40.
So the B-domain mean WER gain (−17) is a length effect, not more correct words. chrF, which credits matched
characters, falls in 40–44 of 45 cases.

**Different inputs:**
- Production and the B Uni-Sign rows see the **same video window**, but production reads RGB frames and Uni-Sign reads
  RTMPose keypoints.
- The A rows use a **different window** (re-aligned) and the official crop.

## Notable Cases (automatic, descriptive only)

**Largest apparent production wins** (Δ sentence chrF vs P0-A CPU B):

| Case | Δ chrF | Production | Uni-Sign B (P0-A CPU) |
|---|---|---|---|
| R11 | +5.99 (also +7.46 vs A) | "Let's discuss. Are you ready? What should we do? How do we interact? …" | "I'm getting ready to go, I'm ready to go, …" (loop) |
| R26 | +4.40 | "Various things" | "It's going to go up and down." |
| R41 | +2.91 | "Always save, always." | "We're going to recycle these boats." |
| R12 | +1.59 | "What's happening? Tell me, I have something to give. …" | "If you're going to wait for a long period of time, …" |

- R11 is the only case where production beats both P0-A CPU Uni-Sign outputs, mostly by avoiding Uni-Sign's loop.
- No production output matches its reference in content by inspection of the automatic scores.
- Production's highest sentence chrF is 19.24.

**Largest apparent production regressions:**

| Case | Δ chrF | Production | Comparison |
|---|---|---|---|
| R40 | −59.04 vs A | "First, connect. Understand your friend." | A: "So from here, one, two, three, and then down on your stomach…" |
| R32 | −50.93 vs A | "Two, three, four." | A: "Okay, while you see how I'm close." |
| R41 | −46.09 vs A | "Always save, always." | A: "We always save these drawings and that's where they come from." |
| R35 | −40.36 vs A | "Squeeze. Keep squeezing. Then release." | A: "Hi, I'm Colin and I'm going to show you how…" |
| R10 | −32.14 vs sheet B | "What time is L.P.Q.G.N.D.F.P.P.D.? All of my past life. First, two" | sheet B prod_output |
| R43 | −22.91 vs B | "Welcome to this first class. About with..." | B: "It's a nice way to start getting up and practice with." |

**Patterns observed (descriptive):**
- **Short, generic outputs.** 17 outputs have ≤ 3 words. Frequent words include "what" (14), "first" (9) and "help"
  (7). 13 outputs contain "?" while 7 references do.
- **Name/fingerspelling cases** come out as letter strings or other names:
  - R02 "NSD DEF";
  - R04 "Bruno SM";
  - R05 "Jerry. I like joy.";
  - R10 "L.P.Q.G.N.D.F.P.P.D.".
  - They are not compared with the reference names, and no accuracy is claimed.
- **No-signing verdict:** R29, the window P0-C found about 46 % at rest, returned no segments ("No signing was
  observed… hands in their lap").
- **Repetition:** `loop_out` 0, `degenerate_repetition` 0. Production does not loop the way Uni-Sign does
  (11 B / 9 A loops). Its failure mode here is brevity and generic content, not repetition.
- **Partial batch loss:** in R03, one of 2 batches was unparseable JSON, so the user-visible text is only that
  batch's "I know now.".
- **Self-reported confidence** is "high" on 47/57 calls despite median chrF 6.0. Model confidence is not evidence of
  correctness.

## Limitations

- **References:** How2Sign English translations of the speech track, aligned to the signing. They are the dataset's
  reference, not ASL-fluent gold for these clips, and a few rows have known timing issues.
- **Automatic metrics are not semantic judgement.** No human label exists; `human_status` is pending on every case.
- **Different inputs and preprocessing:**
  - production: RGB frames, adaptive 24–51 frames, 512 px;
  - Uni-Sign: RTMPose keypoints, up to 256 frames.
- **End-to-end comparison,** not a controlled single-variable ablation. Model, modality, frame selection and decoding
  all differ.
- **Provenance:** R10/R14's B window is the re-aligned interval (timing-label MISMATCH), and R32's source interval is
  UNRESOLVED. The video inputs themselves are hash-fixed.
- **Sample:** the 45 cases are a worst-first exploratory sample (10.13), so counts are not population rates.
- **Reproducibility:** one run per case at temperature 0. Production's own notes record non-identical repeat runs, so
  case-level text may vary on a rerun.
- **What the product shows:**
  - the user-facing caption adds an "unverified" prefix and a target-language translation, which were not exercised
    here;
  - R29 would be shown as a "no signing detected" error, not as an empty caption.

## Conclusion

On these 45 How2Sign clips, current production (`gemini-2.5-flash`, adaptive frames) scores **lower than Uni-Sign on
every corpus metric except WER**:
- chrF 9.27 vs 18.22 (Uni-Sign B, same video window) and 23.76 (Uni-Sign A);
- it is lower in sentence chrF on 41/45 (vs B) and 44/45 (vs A) cases.

Its outputs are about a third of the reference length and frequently generic. It avoids Uni-Sign's repetition loops.
Its WER is not higher than Uni-Sign's only because short outputs incur fewer insertions.

Whether any output is semantically right cannot be settled by these metrics; that needs ASL-fluent review.

## Files

- `asl-translator/asl-eval/run_production_45.py`: wrapper (loads production `asl_utils.py` by path; `--dry-run`;
  `--env-file` loads only `GEMINI_API_KEY`).
- `asl-translator/asl-eval/production_45_tools.py`: manifest / score / sheet (P0-A metric definitions).
- `asl-translator/asl-eval/production_45/`:
  - `production_45_manifest.csv`;
  - `raw/R01…R45.json` + `raw/run_meta.json` (per case: input hash, timestamps sent, frames, each call's raw response,
    model version, usage, latency, retry count, status);
  - `production_45_predictions.json`;
  - `production_45_scores.json`;
  - `production_45_cases.csv`.
- `docs/daily_report/10.18/asl-review-inspection-sheet/inspection_sheet_with_production.csv`: an augmented copy of
  the inspection sheet.
  - All 45 rows, the row order and all 32 original columns are unchanged, verified value by value.
  - Appended columns: `production_model`, `production_output`, `production_chrF`, `production_WER`,
    `production_status`, `production_source`.
  - The original `inspection_sheet.csv` is **not modified**. It is a generated artifact: the builder writes a fixed
    `FIELDS` list, and the HTML page's Export writes a file of the same name from its embedded field list. Columns
    added in place would be lost on a rebuild or a reviewer export.
  - The sheet's existing `prod_output` column remains what its README says it is: a provisional Uni-Sign B stand-in,
    not production output.

## Reproduce

```bash
git -C <curify-studio> fetch origin && git -C <curify-studio> archive origin/main curify_background/app/utils/asl_utils.py | tar -x -C <export>
python3 -I asl-translator/asl-eval/run_production_45.py --prod-src <export> --prod-commit 4220e03c0c0c5c4010ddc6ffc8c0d5379d0dc48b \
    --out-dir asl-translator/asl-eval/production_45/raw --dry-run              # local preprocessing only
python3 -I asl-translator/asl-eval/run_production_45.py --prod-src <export> --prod-commit 4220e03c0c0c5c4010ddc6ffc8c0d5379d0dc48b \
    --out-dir asl-translator/asl-eval/production_45/raw --env-file <file with GEMINI_API_KEY>
python3 -I asl-translator/asl-eval/production_45_tools.py score --raw-dir asl-translator/asl-eval/production_45/raw
python3 -I asl-translator/asl-eval/production_45_tools.py sheet
```
(Anaconda Python with `google-genai` 2.20.0, numpy, sacrebleu; ffmpeg.)
