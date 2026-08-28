# ASL Translator

Evaluation and optimization work for Curify's ASL (American Sign Language)
translation feature. This directory consolidates the reusable corpus and
tooling; historical daily-report writeups stay under
`docs/daily_report/8.26/asl-ground-truth-eval/`.

## Layout

```
asl-translator/
├── data/
│   └── asl_corpus/                 # 13 real ASL videos + references + predictions — see its own README
├── asl-ground-truth-annotator/     # local browser tool for creating/correcting timestamped English ground truth
└── asl-eval/                       # local scorer (WER/CER/timing) + offline production-config-equivalent runner
```

## Where things live

- **Corpus** — `asl-translator/data/asl_corpus/`. 13 real user-submitted videos, with ground truth where it exists and production-model predictions where a job ran. See `asl-translator/data/asl_corpus/README.md` for per-video notes and `manifest.json` for machine-readable metadata.
- **Manual ground-truth annotation tool** — `asl-translator/asl-ground-truth-annotator/`. Static HTML/JS, no server/network component, used to create and correct timestamped English references against a loaded video. See its README to launch it.
- **Evaluation tool** — `asl-translator/asl-eval/`. Stdlib-only scorer (`evaluate.py`) comparing a reference SRT against a prediction JSON (WER/CER/timing), a readiness checker (`status.py`), and an offline production-configuration-equivalent runner (`run_current_model.py`, dry-run by default, gated real calls). See its README for usage and test instructions.

## Workflow

```
video → human-verified ground truth → production prediction → evaluation → failure analysis → optimization experiment
```

1. Pick a corpus video (or add a new one) under `data/asl_corpus/videos/`.
2. Use `asl-ground-truth-annotator/` to create or correct a timestamped English reference, exported into `data/asl_corpus/ground_truth/`.
3. Obtain a prediction — either the live production output (`data/asl_corpus/predictions_baseline0/`) or an offline run via `asl-eval/run_current_model.py`.
4. Score the pair with `asl-eval/evaluate.py` (WER/CER/timing) and check overall readiness with `asl-eval/status.py`.
5. Read the failure cases (segment alignment, WER/CER breakdown) to identify concrete gaps — e.g. fingerspelled names, numbers, framing/motion sampling.
6. Turn a diagnosed gap into a scoped optimization experiment (e.g. a sampling or decoding-config change), then re-run the loop to measure it.

## Privacy — read before touching `data/asl_corpus/`

**This is personal data.** The corpus contains real, identifiable users
signing, submitted to a paid product. **Not consented for public release.**
ASL grammar is carried on the face, so faces cannot be blurred without
destroying the signal this corpus exists to measure — there is no
"anonymize it" option. **Do not push `data/asl_corpus/` to a public
repository, and do not point any other tool, script, or service at these
files.** See `data/asl_corpus/README.md` for the full sensitivity notice
and the few lower-risk items that are separable if something shareable is
ever needed.
