# ASL evaluation scaffold

A small local, deterministic evaluator for comparing an ASL reference SRT
against a prediction JSON, plus a status command that reports which
reference items are actually ready to score. Standard library only — no
network calls, no model calls, no third-party dependencies. Never opens
the corpus `.mp4` files.

Companion to `asl-translator/asl-ground-truth-annotator/` (which builds references)
and `asl-translator/data/asl_corpus/evaluation_set.json` (which lists them).

## Privacy

`asl-translator/data/asl_corpus/` contains identifiable real-user video (see
`asl-translator/data/asl_corpus/README.md`). This scaffold only reads local text/JSON
files (SRTs and prediction JSONs) — it does not touch, upload, or link to
any video, and requires no network access to run.

## What the evaluation set currently contains

`asl-translator/data/asl_corpus/evaluation_set.json` lists three items:

| video_id | reference_status | reference_kind |
|---|---|---|
| `155_demo_asl-demo-translation_26.7s` | `verified_gold` | human-translated |
| `1252_1000016397_76.8s` | `verified_gold` | human-translated (fingerspelling case) |
| `1320_1000022357_137.2s` | `candidate_reference` | burned-caption-derived candidate reference, `verified: false` |

`1434_screenrec_youtube_16.6s` is deliberately **excluded**. Its clip
covers only the greeting exchange — the highest-prior content in ASL — so
a model can score ~65% by guessing without decoding any signing. Do not
add it back as an acceptance item; see `asl-translator/data/asl_corpus/README.md`.

### Verified vs. candidate

- **`verified_gold`** (155, 1252): human-translated, `usable_for_official_metrics: true`. These are the only items whose scores should be reported as real accuracy numbers once matching predictions exist.
- **`candidate_reference`** (1320): a **burned-caption-derived candidate reference** — the English text was read directly off the burned-in caption band via local ffmpeg frame sampling and manual visual inspection (see `ground_truth_candidates/1320_1000022357_137.2s.json → meta.extraction_method`); **no OCR was used**. `verified: false`, `usable_for_official_metrics: false`. The evaluator will happily score against it for debugging, but **1320 must not enter official metrics until the production direction is confirmed** (ASL rendition that was captioned, vs. English source that was interpreted — see `asl-translator/data/asl_corpus/README.md` and `ground_truth_candidates/1320_1000022357_137.2s.json → meta`). Treat any 1320 number as a sanity check, not a benchmark result.

## Running the evaluator

```
python3 asl-translator/asl-eval/evaluate.py \
    --reference asl-translator/data/asl_corpus/ground_truth/155_demo_asl-demo-translation_26.7s.srt \
    --prediction /path/to/prediction.json \
    [--json-out /tmp/eval.json] [--no-alignment]
```

`--prediction` can point anywhere — it does not need to live under
`predictions_baseline0/`. Prediction JSON is expected in the baseline0
shape: `{..., "segments": [{"line", "start", "end", "text"}, ...]}`.

## Checking what's ready to evaluate

```
python3 asl-translator/asl-eval/status.py [--json-out /tmp/status.json]
```

For each manifest item this reports whether its reference file exists, whether
a same-basename prediction exists under `predictions_baseline0/`, and an
`eligibility` value: `waiting_prediction`, `reference_not_official`,
`reference_missing`, or `ready_for_official_metrics`. **A missing
prediction is reported as `waiting_prediction`, never as a zero or failing
score.**

## Metrics

### WER (word error rate)

Reference and prediction segment texts are each joined into one full
transcript, normalized (lowercase, ordinary punctuation replaced with a
space, whitespace collapsed — no paraphrase matching, no number-word
rewriting), then split on whitespace. A standard word-level Levenshtein
alignment gives substitutions/deletions/insertions; `WER = (S+D+I) /
reference_word_count`. If the reference is empty, WER is `0.0` when the
prediction is also empty, else `1.0`.

### CER (character error rate)

Same normalized transcripts, aligned character-by-character (including
the collapsed single spaces between words) with the same Levenshtein
algorithm. Reported as `substitutions`/`deletions`/`insertions`/`cer`
under `text_metrics.char_level`.

WER/CER are English-transcript comparison metrics only. **They do not
measure ASL semantic correctness** — they cannot tell you whether the
model actually understood the signing, only whether its English output
string matches the reference string.

### Timing / coverage metrics

Independent of what the captions say — only *when* something is captioned:

- `reference_coverage_s` / `prediction_coverage_s`: total duration covered by each set's segments, after merging overlapping segments within that set.
- `overlap_s`: total duration where reference and prediction coverage intersect.
- `temporal_precision` = overlap / prediction_coverage (0.0 if prediction_coverage is 0)
- `temporal_recall` = overlap / reference_coverage (0.0 if reference_coverage is 0)
- `temporal_iou` = overlap / union (1.0 if both are empty — trivially nothing to disagree about)

Temporal overlap says nothing about translation correctness — a
prediction can have perfect timing and completely wrong text.

### Segment alignment (diagnostic only)

`--no-alignment` to skip. For each reference segment, finds the
best-overlapping prediction segment by duration and reports both texts
side by side plus overlap/IoU. This is for eyeballing failure cases, not
a scored metric — it is not folded into WER/CER/timing.

## Output format

Human-readable text to stdout by default. Pass `--json-out <path>` for
the machine-readable form:

```json
{
  "reference": "...",
  "prediction": "...",
  "text_metrics": {
    "reference_words": 0, "prediction_words": 0,
    "substitutions": 0, "deletions": 0, "insertions": 0,
    "wer": 0.0, "cer": 0.0,
    "char_level": {"reference_chars": 0, "prediction_chars": 0, "substitutions": 0, "deletions": 0, "insertions": 0},
    "reference_transcript_normalized": "...", "prediction_transcript_normalized": "..."
  },
  "timing_metrics": {
    "reference_coverage_s": 0.0, "prediction_coverage_s": 0.0, "overlap_s": 0.0,
    "temporal_precision": 0.0, "temporal_recall": 0.0, "temporal_iou": 0.0
  },
  "segment_alignment": [...]
}
```

No hidden model scoring, no LLM-as-judge.

## Limitations

- WER/CER measure English-text overlap, not ASL comprehension.
- Normalization is conservative by design (no semantic matching), so a
  correct paraphrase scores as errors.
- Timing metrics measure "when," not "what" — high IoU with garbage text
  is possible and expected to happen.
- `1320`'s reference is unverified; scores against it are debugging
  signal only, not benchmark results, until production direction is
  confirmed.
- `1434` is out of the evaluation set entirely — do not add it back.

## Offline production-equivalent runner

`run_current_model.py` reproduces the CURRENT production sampler / prompt /
request construction from `curify-studio`'s `asl_utils.py` closely enough to
evaluate, while excluding every product side effect by construction — it never
imports Supabase, Azure, credit/billing, or project/job code, so it cannot
create a project, write `projectsegment`, charge credits, or touch storage.
Wording note: this is **production-configuration-equivalent**, not literal
output reproducibility — Gemini decoding is non-deterministic even at
`temperature=0` in practice (see the determinism-pair finding in
`asl-translator/data/asl_corpus/README.md`).

### Source provenance

Copied (not imported) from `curify-studio`, inspected read-only via
`git -C <curify-studio> show origin/main:curify_background/app/utils/asl_utils.py`:

- source repo/ref: `curify-studio` @ `origin/main`
- commit at inspection time: `ac21f24fd25357f859741421f10775f6800c6c1c`
- file: `curify_background/app/utils/asl_utils.py`
- last commit touching that file on `origin/main`: `08d12fb fix(asl): keep the provider error message; classify spend-cap failures`

curify-studio was not checked out, pulled, merged, or modified to build this
runner. The full provenance block, including why `app.config.Settings` /
Supabase / Azure imports are avoided, is in the module docstring of
`run_current_model.py` itself.

### Default: dry-run, zero network

```
python3 asl-translator/asl-eval/run_current_model.py \
    --video asl-translator/data/asl_corpus/videos/155_demo_asl-demo-translation_26.7s.mp4
```

This does local ffmpeg/numpy work only: motion probe → active/idle
segmentation → timestamp allocation → report. It never imports `google.genai`
and never requires `GEMINI_API_KEY`. Output always starts and ends with:

```
DRY RUN ONLY — NO MODEL CALL WAS MADE.
```

Add `--extract-frames` to actually pull the sampled JPEGs into a
`tempfile.TemporaryDirectory` (auto-deleted on exit) as a parity check — still
no network. Add `--json-out <path>` to also write the report as JSON
(`"dry_run": true`, `"segments": []`, `"model_calls": 0`).

Frames may show identifiable people. `--extract-frames` alone never persists
them anywhere. `--keep-frames-dir <DIR>` (requires `--extract-frames`) writes
them to a directory you name instead, is **not** auto-deleted, and prints a
privacy warning — prefer not to use it.

### Configs

A config is the **full knob set**, not just the temperature. It has to be: on
2026-08-29 production changed three things at once, and a harness that pinned
only temperature would quietly stop reproducing either the old runs or the new
ones.

| | `baseline0` | `temperature0` | `production_2026_08_29` |
|---|---|---|---|
| temperature | omitted | `0.0` | `0.0` |
| budget | absolute 96 | absolute 96 | duration-scaled |
| dedup | no | no | **yes** |
| what it is | production 08-16 → 08-29 | the 8.26 A/B arm | production today |

- **`baseline0` (default) and `temperature0` are historical and must not be
  "modernised".** Every prediction JSON under `data/asl_corpus/` and every number
  in `docs/daily_report/8.26/asl-ground-truth-eval/` was produced with them; edit
  them and that evidence becomes unverifiable. Shared knobs: `gemini-2.5-flash`,
  `FRAME_BUDGET=96`, `KEYFRAME_WIDTH=512`, `BATCH_SIZE=24`, `PROBE_FPS=4.0`,
  `IDLE_QUANTILE=0.35`, `ABS_MOTION_FLOOR=2.0`. In `baseline0` the `temperature`
  argument is **genuinely omitted** from `GenerateContentConfig`, not defaulted to
  a number in code, and is reported as `"temperature_unset_provider_default"`.
  (The corpus manifest's note that the provider default is numerically 1.0 is an
  existing corpus assumption, not something this runner asserts.)
- **`production_2026_08_29`** mirrors curify-studio `f42a3a44`: `temperature=0.0`,
  a duration-derived budget (`TARGET_FRAMES_PER_SEC=2.0`, floor
  `MIN_FRAME_BUDGET=24`, ceiling `MAX_FRAME_BUDGET=240`), and adjacent-duplicate
  caption merging (`DEDUP_MAX_GAP_S=1.0`). It is dated rather than called
  "current" so the parity claim carries its own expiry — if production changes
  again, add another dated config instead of editing this one.

Runs now also report **sampling density** (frames/sec) against
`DENSITY_FLOOR_FPS=1.0`, and flag `low_density` below it. That floor is empirical:
across this corpus every job at or below 0.51 f/s was degenerate or
suspected-fabricated, and every job at or above 1.25 was neither. What the budget
change does to a real video, e.g. `1320_1000022357_137.2s`:

```
--config baseline0               96 frames,  0.700 f/s,  4 calls   ⚠️ below floor
--config production_2026_08_29  240 frames,  1.749 f/s, 10 calls
```

⚠️ `low_density` is the only signal that catches the *dangerous* failure. The
`degenerate_repetition` flag catches a read that collapsed into one repeated
caption (the ~190s jobs), but job 1442 — 300s, the sparsest sampling in the
corpus — produced fifteen distinct fluent sentences and is the output we most
suspect of being invented outright. Repetition cannot see that.

### Staying in sync with production

This file is a hand-copied port, so the thing that actually keeps it honest is
`TestProductionParity` in `test_run_current_model.py`. It loads
`curify-studio/curify_background/app/utils/asl_utils.py` **directly by path** and
diffs the constants, the prompt, the budget curve, the dedup normalizer and the
dedup behaviour against it. This works because `asl_utils` keeps every heavy
import (numpy, `google.genai`, `imagen_service`) function-local, so it loads with
no environment and no provider config — `app.config` would not.

The check **skips** when curify-studio is not checked out next door, so CI
without it still runs everything else. If you change production, run the tests
here: a drifted constant fails with the constant's name.

### The explicit real-run gate (NOT executed by this phase)

```
python3 asl-translator/asl-eval/run_current_model.py \
    --video <local .mp4> \
    --output <local .json> \
    --run \
    --acknowledge-private-data-upload
```

Both `--run` and `--acknowledge-private-data-upload` are required together —
sampled frames contain identifiable people and a real run sends them to
Gemini, off this machine. Without `--run`, `google.genai` is never imported
and `GEMINI_API_KEY` is never required. With `--run`, `GEMINI_API_KEY` must be
set or the script exits with a clear error before any client is constructed.
This command was written and gated but **not executed** while building this
runner.

### Future evaluation workflow

1. Dry-run a video to sanity-check sampling before spending a real call.
2. When ready, run the gated `--run` command above. Use
   `--config production_2026_08_29` to evaluate what users actually get today;
   use `baseline0` / `temperature0` only to reproduce a historical result.
3. Score it with `evaluate.py` / check readiness with `status.py`, as above.

## Adding a future prediction

1. Generate a prediction JSON in the baseline0 shape (see any file under
   `asl-translator/data/asl_corpus/predictions_baseline0/` for the exact shape) — this
   scaffold does not generate predictions itself (see repo-level
   instructions: no production model calls in this phase).
2. Run `python3 asl-translator/asl-eval/evaluate.py --reference <ref.srt>
   --prediction <your.json>` to score it, or drop it into
   `predictions_baseline0/<video_id>.json` so `status.py` auto-detects it.
3. Re-run `python3 asl-translator/asl-eval/status.py` to confirm the item now
   shows `ready_for_official_metrics` before treating any number as a
   benchmark result.

## Tests

```
python3 -m unittest asl-translator/asl-eval/test_evaluate.py -v
python3 -m unittest asl-translator/asl-eval/test_run_current_model.py -v
```

`test_evaluate.py`: 16 tests, stdlib `unittest`, deterministic. Covers SRT
parsing on the real 155/1252 references (6 and 11 segments respectively,
read-only), WER identity/substitution/insertion/deletion cases,
empty-prediction handling, timing-coverage identity and partial-overlap
cases, and manifest status checks (155/1252 `verified_gold`, 1320
`candidate_reference`, 1434 absent). No corpus source file is modified by
the tests.

`test_run_current_model.py`: 25 tests, stdlib `unittest` + `unittest.mock`,
no network calls, no Gemini invocation. Covers: default is dry-run;
dry-run needs no `GEMINI_API_KEY` and never imports `google.genai`;
`baseline0` leaves `temperature` unset while `temperature0` sets `0.0`;
expected batch counts (1→1, 24→1, 25→2, 96→4, ...); dry-run JSON schema;
`--run` without `--acknowledge-private-data-upload` refuses with no call
made; the acknowledgement flag alone (no `--run`) still makes no call;
`--run` with both flags but no `GEMINI_API_KEY` fails clearly before any
client is constructed; URL inputs (`http(s)://`, `s3://`, `gs://`,
`ftp://`, Azure blob URLs) are rejected; and a static scan of actual
`import`/`from...import` statements confirms no `app.crud`,
`app.pipelines`, `app.orchestrators`, `app.config`, `app.services`,
`sqlalchemy`, `supabase`, or `azure` import is present.
