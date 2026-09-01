# How2Sign mini benchmark (19 clips, official test split)

**This is public research data, not Curify user data.** It lives in
`public_benchmarks/` deliberately separate from `../asl_corpus/`, which holds
real, private, identifiable Curify user videos. Never point a script at both
directories interchangeably, and never merge this folder's manifest with
`asl_corpus/manifest.json` / `evaluation_set.json` — they are two unrelated
corpora with unrelated privacy properties.

## What this is

19 clips (5.9 minutes total) drawn from How2Sign's official, human-translated
**test split**, for apples-to-apples comparison between Curify's current model
and open-source SLT baselines on the same public, licensed, citable clips —
with no training and no per-clip download cost beyond what's staged here.

Full dataset research: `docs/daily_report/8.30/asl-data/PUBLIC_ASL_DATASET_RESEARCH.md`.
Selection methodology and results: `docs/daily_report/8.30/asl-data/HOW2SIGN_MINI_BENCHMARK.md`.

## Source and license

- Official page: https://how2sign.github.io/
- Paper: Duarte et al., "How2Sign: A Large-scale Multimodal Dataset for
  Continuous American Sign Language," CVPR 2021 (arXiv:2008.08143).
- **License: CC BY-NC 4.0** — non-commercial research use, with attribution.
  Do not use for anything commercial without separately confirming terms.
- Videos: extracted from the official "Green Screen RGB clips (frontal view)"
  test-split archive (`test_rgb_front_clips.zip`, ~2.2GB on Google Drive) —
  only the 19 needed clips were retained locally; the full archive was deleted
  immediately after extraction and was never committed anywhere.
- References: sourced from the official **"English Translation (original)"**
  test-split file, not the "manually re-aligned" one — see
  `HOW2SIGN_MINI_BENCHMARK.md` §"A correction found during this pilot" for why.

## Structure

```
how2sign/
├── README.md              this file
├── manifest.csv            one row per clip: ID, split, duration, source
│                           artifact, reference text, local paths, leakage
│                           check result, inclusion reason
├── videos/                 19 .mp4 clips (56MB total)
├── references/              19 single-segment .srt files (one per clip;
│                           start=00:00:00,000, end=clip duration, text=the
│                           official English sentence)
├── source_metadata/         the exact 19 rows of the official test-split TSV
│                           these clips/references came from, for
│                           reproducibility independent of this repo
└── run_smoke_test.py        isolated data-pipeline smoke test (reference
                            fed back as its own "prediction") — confirms the
                            existing, UNMODIFIED asl-eval/evaluate.py and
                            lib.py read this format correctly. Not a model
                            evaluation.
```

## Why this structure and not something else

How2Sign's own official distribution is exactly "one clip = one directory
entry, plus a separate TSV of sentence-level text/timestamps" — the structure
here mirrors that directly, and mirrors this repo's own `asl_corpus/` layout
(`videos/`, a reference-text directory, per-item single-segment SRTs) closely
enough that the existing `asl-eval` tooling needs zero modification to read
it. No better official structure was suggested by the source data, so the
originally-proposed layout was kept as-is.

## How to score something against this benchmark

Each clip is scored individually with the existing, unmodified evaluator —
exactly the same tool and semantics used for Curify's own corpus:

```
python3 asl-translator/asl-eval/evaluate.py \
    --reference asl-translator/data/public_benchmarks/how2sign/references/<clip_id>.srt \
    --prediction /path/to/your_prediction.json
```

`--prediction` must be a JSON with `{"segments": [{"start", "end", "text"}, ...]}`
— the same baseline0 shape used everywhere else in this repo. No code in
`asl-eval/` was changed to support this; the format already matched.

To confirm the pipeline itself (not a model) reads this benchmark correctly:

```
python3 asl-translator/data/public_benchmarks/how2sign/run_smoke_test.py
```

This feeds each reference back in as a trivial "prediction" and expects
WER=0/CER=0/IoU=1.0 for all 19 clips — a data-pipeline check, not an
evaluation of any model.

## What is deliberately NOT here

- The full 2,322-clip official test split, or any other How2Sign split
  (train/val) — only this 19-clip subset was downloaded and retained.
- Any modification to `asl-eval/evaluate.py`, `lib.py`, or `corpus_guard.py`
  — this benchmark's format needed none.
- Any model prediction — this is data staging only; running a model against
  these clips is a separate, later step requiring its own authorization.
