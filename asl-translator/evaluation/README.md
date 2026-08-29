# Production evaluation workflow

This directory prepares the scoring workflow that runs once verified
ground truth exists. It does not create ground truth and it does not call
any model or API — it only reads local files under
`asl-translator/data/asl_corpus/` and writes results under
`asl-translator/evaluation/results/`.

The actual metric engine lives in `asl-translator/asl-eval/`
(`lib.py`, `evaluate.py`, `status.py` — see its own README for the full
metric definitions). This directory adds one thing on top: `run_ready.py`,
which auto-discovers and scores everything that has become scoreable,
instead of requiring a manual `--reference`/`--prediction` invocation per
item.

## Filename conventions

Both conventions below key off `video_id` — the video's filename with the
`.mp4` extension stripped (e.g. `1477_recording_6.7s`).

**Ground-truth reference** (created by a human via
`asl-translator/asl-ground-truth-annotator/`, per
`asl-translator/data/asl_corpus/ANNOTATION_PLAN.md`):

```
asl-translator/data/asl_corpus/ground_truth/<video_id>.srt
asl-translator/data/asl_corpus/ground_truth/<video_id>.json   (optional, canonical export)
```

`evaluate.py` reads the `.srt`. The `.json` export is the canonical
`{video, duration_s, meta:{gt_kind, source_file, verified}, segments}`
shape and is what carries `gt_kind`/`verified` provenance — keep both.

**Prediction** (model output, already produced by the live product):

```
asl-translator/data/asl_corpus/predictions_baseline0/<video_id>.json
```

`status.py` and `run_ready.py` look up a prediction by exact
`<video_id>.json` match under `predictions_baseline0/`. A prediction that
lives anywhere else can still be scored manually with `evaluate.py
--prediction <any path>`, but won't be auto-detected by `status.py` /
`run_ready.py`.

Unverified candidate references (built from something other than a human
watching the signing, e.g. burned-in captions) live in a parallel
directory and are never treated as official:

```
asl-translator/data/asl_corpus/ground_truth_candidates/<video_id>.{srt,json}
```

## Running `status.py`

Reports, per `evaluation_set.json` item, whether its reference file
exists, whether a same-basename prediction exists, and an eligibility
verdict (`waiting_prediction`, `reference_not_official`,
`reference_missing`, or `ready_for_official_metrics`). File-existence
checks only — never opens video or prediction content.

```
python3 asl-translator/asl-eval/status.py
python3 asl-translator/asl-eval/status.py --json-out /tmp/status.json
```

## Running `evaluate.py`

Scores one reference against one prediction: WER/CER text metrics,
timing/coverage metrics, and an optional per-segment alignment diagnostic.
Full metric definitions and caveats are in `asl-translator/asl-eval/README.md`.

```
python3 asl-translator/asl-eval/evaluate.py \
    --reference asl-translator/data/asl_corpus/ground_truth/<video_id>.srt \
    --prediction asl-translator/data/asl_corpus/predictions_baseline0/<video_id>.json \
    [--json-out /tmp/eval.json] [--no-alignment]
```

`--reference` and `--prediction` accept any path, so this also covers the
one-off case of scoring a reference against a *different* video's
prediction (e.g. 1466's reference against 1467's prediction, once 1466 is
verified — see `run_ready.py` below, which automates exactly this pairing).

## Running the automated workflow: `run_ready.py`

Scores every `evaluation_set.json` item whose reference file and a
matching prediction both already exist — no need to know or type any
path. Re-run it any time; it is idempotent and only reads existing files.

```
python3 asl-translator/evaluation/run_ready.py
python3 asl-translator/evaluation/run_ready.py --include-non-official
python3 asl-translator/evaluation/run_ready.py --results-dir /tmp/eval-results
```

- Skips (and reports why) any item whose reference doesn't exist yet,
  whose prediction doesn't exist yet, or whose reference exists but is
  marked `usable_for_official_metrics: false` (e.g. 1320's candidate
  reference) — unless `--include-non-official` is passed, in which case
  it's still scored but every printed/saved result is tagged
  `DEBUG-ONLY (not official)`.
- Also applies a small hand-maintained pairing table
  (`EXTRA_PREDICTION_PAIRINGS` in `run_ready.py`) for videos that are
  content-identical to an evaluation-set item but were processed as a
  separate production job (currently: 1466/1467, the documented
  determinism pair). Once `1466_nohead-half1_189.5s`'s reference exists,
  this scores *both* its own prediction and 1467's against that one
  reference automatically.
- Writes one JSON result per scored pair to
  `asl-translator/evaluation/results/<video_id>.json` (or
  `<video_id>__vs__<extra_id>.json` for a pairing), plus a human-readable
  summary to stdout.
- Run right now (verified independently while preparing this workflow):
  scores **0 pairs**. `155_demo_asl-demo-translation_26.7s` and
  `1252_1000016397_76.8s` are `verified_gold` but have no
  `predictions_baseline0/` file at all — both production jobs failed
  (`GOOGLE_API_KEY` missing / empty translation, per `manifest.json`), so
  they report `waiting_prediction`, not a score. 1320 has a candidate
  reference but no baseline0 prediction either, so it also reports
  `waiting_prediction` — `--include-non-official` only changes whether a
  non-official reference is *scored*, it can't invent a missing
  prediction. None of the six queued samples (1477, 1474, 1320, 1466,
  1442, 1457) has a manifest entry yet, so they don't appear in this
  output at all until step 2 below is done for each.

`asl-translator/evaluation/results/` is generated output, not source —
see `.gitignore` in this directory.

## How a newly verified sample becomes eligible for official metrics

1. An ASL-fluent human produces `ground_truth/<video_id>.srt` (+ `.json`)
   via the annotator, with `gt_kind: human` and `verified: true` set on
   every segment (per `asl-translator/data/asl_corpus/ANNOTATION_PLAN.md`).
   Nothing in this directory performs that step.
2. Add an entry for `<video_id>` to `evaluation_set.json` (see below).
   Until this entry exists, `status.py` and `run_ready.py` have no way to
   find the reference, even though the file is on disk.
3. Run `status.py` — the item should now report `ready_for_official_metrics`
   if a matching prediction already exists under `predictions_baseline0/`,
   or `waiting_prediction` if it doesn't yet (true today for 1320 and 1457,
   which have no baseline0 prediction).
4. Run `run_ready.py` (or `evaluate.py` directly) to get the actual score.

A reference existing on disk is *not* sufficient by itself — the
`evaluation_set.json` entry plus `usable_for_official_metrics: true` is
what the tooling treats as the "this is real, report it" signal.

## Adding a sample to `evaluation_set.json` safely

`evaluation_set.json` is a small hand-maintained JSON manifest, not
generated. To add an item without breaking the file or the tooling that
reads it:

1. Open `asl-translator/data/asl_corpus/evaluation_set.json` and copy the
   shape of an existing `items` entry, e.g.:

   ```json
   {
     "video_id": "1477_recording_6.7s",
     "video": "videos/1477_recording_6.7s.mp4",
     "reference": "ground_truth/1477_recording_6.7s.srt",
     "reference_status": "verified_gold",
     "reference_kind": "human_translated",
     "usable_for_official_metrics": true
   }
   ```

   Field notes:
   - `video_id` must exactly match the `.srt`/`.json` basename under
     `ground_truth/` and, if a prediction exists, the `.json` basename
     under `predictions_baseline0/` — this is the join key every tool
     in this workflow uses.
   - `reference` is relative to `asl-translator/data/asl_corpus/`
     (matches how existing entries are written), not repo-root-relative.
   - Only set `reference_status: "verified_gold"` and
     `usable_for_official_metrics: true` once the human annotator has
     actually checked `verified` in the exported JSON — don't set these
     ahead of that (this preparation task explicitly does not mark
     anything verified).
   - Use `reference_status: "candidate_reference"` and
     `usable_for_official_metrics: false` for anything not yet confirmed
     by a human (mirrors the existing 1320 entry).

2. Append the object to the `items` array — **do not edit or reorder the
   existing 155/1252/1320 entries.**
3. Validate the file is still well-formed JSON before running anything
   else:

   ```
   python3 -m json.tool asl-translator/data/asl_corpus/evaluation_set.json > /dev/null
   ```

4. Run `python3 asl-translator/asl-eval/status.py` and confirm the new
   row appears with the eligibility you expect.
5. Do not add `1434_screenrec_youtube_16.6s` — it is deliberately excluded
   (`excluded` block in `evaluation_set.json`; see
   `asl-translator/data/asl_corpus/README.md` for why: greeting-only
   content, ~65% guessable without decoding any signing).

## Scope of this directory

- No ASL transcript is generated here, ever.
- No existing prediction or verified ground-truth file is modified here.
- No sample is marked `verified` here — that is exclusively a human
  annotator action in `asl-translator/asl-ground-truth-annotator/`.
- No network or model API call is made anywhere in this workflow
  (`evaluate.py`, `status.py`, and `run_ready.py` are all stdlib-only).
- Nothing here commits or pushes; that remains a separate, explicit step.
