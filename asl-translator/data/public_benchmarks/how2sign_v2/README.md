# How2Sign v2 benchmark (128 clips, official test split)

**This is public research data, not Curify user data.** Same privacy
posture as `../how2sign/` (`pilot_v1`) — lives in `public_benchmarks/`,
separate from `../../asl_corpus/`, which holds real, private, identifiable
Curify user videos. Never merge this folder's manifest with
`asl_corpus/manifest.json` / `evaluation_set.json`.

## What this is

128 clips drawn from How2Sign's official, human-translated **test split**,
disjoint from `../how2sign/`'s 19-clip pilot (kept untouched as
`pilot_v1` — historical, not superseded). Selected by a deterministic,
metadata-only rule *before any video was viewed and before any model was
run*, then hard-validated against the physical archive (alignment,
leakage, duplicate-content checks) before freezing. Full methodology and
validation record: `SELECTION_METHODOLOGY.md`.

## Source and license

Same source and license as `pilot_v1` — see `../how2sign/README.md`'s
"Source and license" section. In short: https://how2sign.github.io/,
Duarte et al. CVPR 2021, **CC BY-NC 4.0** (non-commercial research use,
attribution required). Videos extracted from the official test-split
"Green Screen RGB clips (frontal view)" archive; references from the
official "English Translation (original)" TSV, with 2 clips using the
"English Translation (manually re-aligned)" TSV instead where physical
duration matched that file and not the original (see
`SELECTION_METHODOLOGY.md` §5).

## Structure

```
how2sign_v2/
├── README.md                 this file
├── SELECTION_METHODOLOGY.md  full selection rule + validation record (part
│                              of the frozen checksum)
├── manifest.csv               one row per clip; official-metadata columns
│                              and heuristic_*-prefixed columns are kept
│                              visually distinct — heuristic columns are
│                              NEVER "ground truth"
├── videos/                    128 .mp4 clips — LOCAL ONLY, gitignored
├── references/                128 single-segment .srt files, official
│                              English translation (mojibake-corrected
│                              where applicable, flagged in manifest.csv)
├── source_metadata/           the exact rows of the official TSV(s) these
│                              clips/references came from
├── validation/                pre-freeze validation artifacts: replacement
│                              audit trail, leakage-check results, pending
│                              manual-review CSVs for heuristic strata
├── run_smoke_test.py           data-pipeline smoke test (reference fed
│                              back as its own "prediction") — confirms the
│                              existing, UNMODIFIED asl-eval/evaluate.py
│                              and lib.py read this format correctly
├── FREEZE_CHECKSUMS.sha256    per-file SHA-256 for manifest.csv, every
│                              reference, source_metadata, this doc, and
│                              every local video
└── FREEZE.sha256              single fingerprint: SHA-256 of
                               FREEZE_CHECKSUMS.sha256's own contents
```

## How to score something against this benchmark

Identical to `pilot_v1` — same unmodified evaluator, same CLI:

```
python3 asl-translator/asl-eval/evaluate.py \
    --reference asl-translator/data/public_benchmarks/how2sign_v2/references/<clip_id>.srt \
    --prediction /path/to/your_prediction.json
```

To confirm the pipeline itself (not a model) reads this benchmark correctly:

```
python3 asl-translator/data/public_benchmarks/how2sign_v2/run_smoke_test.py
```

## What is deliberately NOT here

- The rest of the official test split (2,357 rows / 149 videos total) — only
  these 128 clips were retained.
- Any modification to `asl-eval/evaluate.py`, `lib.py`, `corpus_guard.py`,
  or `check_leakage.py` — this benchmark's format and validation needed
  none; `check_leakage.py`'s own OCR functions were imported and called
  directly, unmodified.
- Any model prediction — this is data staging and validation only.
- Any change to `pilot_v1` (`../how2sign/`) or `../../asl_corpus/`.
