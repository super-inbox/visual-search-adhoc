# ASL Translator

- [Canonical ASL index](asl-translation-mvp-spec.md) — research progress, evaluation evidence, decisions, and next steps.
- [Research summary — 2026-10-20 (PDF)](asl-research-retrospective-2026-10-20.pdf) — dated retrospective.

Evaluation and optimization work for Curify's ASL (American Sign Language)
translation feature. This directory consolidates the reusable corpus and
tooling; historical daily-report writeups stay under `docs/daily_report/`.

---

# Data status — 2026-09-01

> Snapshot of what data exists, what it can support, and what it cannot.
> Assembled by inspecting the files, not by reading the docs — several docs
> lag behind this. Supersedes status claims elsewhere in this tree.

## Bottom line

**The evaluation harness is fully built and currently has nothing it can
score.** `asl-eval/status.py` reports `0 of 2 evaluation-set items ready`.
Every saved prediction came from `baseline0` (production as it ran
2026-08-16 → 08-29); the two `155` predictions are retracted for label
leakage; and no model run has been made since. **No number in this
repository describes the configuration production runs today.**

Separately, and more serious: the single "verified gold" that every Curify
accuracy claim rests on is **circular** — see [Reference
independence](#reference-independence).

## Two corpora, deliberately separated

|  | Private corpus | Public benchmark |
|---|---|---|
| Path | `data/asl_corpus/` | `data/public_benchmarks/how2sign/` |
| Content | 13 real Curify user uploads | 19 clips, How2Sign official test split |
| Volume | ~1,635 s (27 min) | 351.6 s (5.9 min) |
| Legal | Unconsented personal data, identifiable faces | CC BY-NC 4.0 — **non-commercial only** |
| In git | videos committed (private repo) | references committed, **videos gitignored** (local-only, 56 MB) |

`public_benchmarks/how2sign/README.md` forbids merging the two manifests.
Respect that — they have opposite privacy properties and unrelated provenance.

## Private corpus — 13 videos

| Video | Dur | Reference | Prediction | Leak |
|---|---|---|---|---|
| `155_demo` | 26.7 s | human SRT (6 lines) + SignCaption | b0, t0 — **retracted** | clean now |
| `1252_…16397` | 76.8 s | human SRT (11 lines) + SignCaption | b0, t0 | no |
| `1252_…16402` | 250.8 s | — | — | no |
| `1320_…22357` | 137.2 s | burned-caption SRT + JSON + SignCaption | — | **yes → masked** |
| `1415_unit7` | 200.6 s | — | — | no |
| `1434_screenrec` | 16.6 s | JSON — *excluded, greeting-only* | — | no |
| `1442_clip01` | 300.0 s | — | b0 | no |
| `1457_10426` | 28.3 s | — | — | no |
| `1466_half1` | 189.5 s | SignCaption (via the 1467 file) | b0, t0 ×2 | no |
| `1466_half2` | 190.0 s | — | — | no |
| `1467_half1` | 189.5 s | SignCaption | b0 | no |
| `1474_…04432` | 11.5 s | SignCaption | b0 | no |
| `1477_recording` | 6.7 s | SignCaption | b0 | no |

**8 of 13 have no reference of any kind. 5 of 13 have no prediction.**

## Reference independence

The axis `manifest.json` does not track, and the one that decides whether a
score means anything. A reference is only usable if its **source is
independent of the thing being scored**.

| Reference | Source | Independent? |
|---|---|---|
| **1320** | third-party interpreter-certification answer key — its own title cards read *"Certificate Program for Sign Language Interpreters — RECEPTIVE SKILLS EVALUATION / SIGN TO VOICE"* | **Yes.** Authored by a certification body with no knowledge of Curify. The strongest reference in the corpus. |
| **155** | captions burned into the published marketing demo | **Unknown.** Job `155` itself FAILED (`GOOGLE_API_KEY` missing, 0 credits), so the captions did not come from that run. Whether a human wrote them or an earlier model run did is unresolved — and it decides whether this case is usable. |
| **1252** | Curify's own outreach translation | **No.** Verified by OCR 2026-09-01: `ground_truth/1252_…_burned.mp4` reproduces the gold SRT verbatim. It is the render we produced *from* that translation to email the submitter. The clean source carries no captions (OCR of the lower band returns noise at all 26 sample points), and the submitter's second video shows an on-screen keyboard, not captions. |
| 6 × SignCaption | external commercial tool | Independent, but `usable_for_official_metrics: false` throughout. Cross-tool signal, never gold. |
| 1434 | — | Excluded: greeting-only, guessable from priors without decoding any signing. |

**1252's three artifacts — the gold SRT, the burned video, and the frame
inspector's embedded gold — are one translation counted three times.** They
agree because they share a source, not because they corroborate each other.
Its provenance is a single manifest string, `"human-translated by Curify,
verified"`, with no named annotator, no stated ASL qualification, no date, no
method, and no second-annotator check.

Note the asymmetry: every SignCaption *candidate* carries a detailed
`.provenance.json` (tool, workflow, date, source path, input file). **Neither
human gold has one.** The references everything is scored against have less
recorded provenance than the external-tool outputs they are used to judge.

`ANNOTATION_PLAN.md` additionally instructs *"Do NOT re-annotate these — they
are existing verified anchors."* That protects the wrong thing and should be
lifted for 1252.

## What is scoreable right now

```
1252   verified_gold        no prediction   waiting_prediction
1320   candidate_reference  no prediction   waiting_prediction

0 of 2 evaluation-set items are ready for official metrics.
```

`155` is still marked `excluded: label_was_burned_into_input` in
`evaluation_set.json`. That describes a file the corpus **no longer holds** —
`videos/155_….mp4` was swapped to the clean raw source (md5 `d71313d0…`) on
2026-08-30, and SignCaption has already been scored against it. The retracted
*prediction* should stay refused; the *video* should not. Re-admitting it is
free and takes the corpus from one anchor to two.

## Accuracy evidence that exists

| System | Set | n | WER | Fingerspelling |
|---|---|---|---|---|
| Curify `baseline0` / `temperature0` | 1252 | 1 | 0.9231 | ✗ ✗ |
| SignCaption | 155 | 1 | 0.4815 | n/a |
| SignCaption | 1252 | 1 | 0.5192 | ✓ ✓ (Greg, Sara) |
| Uni-Sign | How2Sign | 19 | 0.9480 | ✗ |
| OpenSLT | How2Sign | 18 | 1.1637 | ✗ |

**No system has been scored on both corpora.** Curify and SignCaption exist
only on internal clips; OpenSLT and Uni-Sign only on How2Sign. The two
evidence bases share no common point and cannot be joined — Curify's 0.9231
and Uni-Sign's 0.9480 are *not* comparable numbers despite looking like they
are.

What survives 1252's reference problem: **the fingerspelling comparison.**
SignCaption and the Curify hand translation independently produced "Greg" and
"Sara"; two unrelated readers agreeing on two proper nouns is real evidence
those names are in the video. What does not survive: the absolute WER for any
system scored against that reference.

## Public benchmark

Better constructed than the internal corpus. 19/19 references matched against
the official test-split TSV; 19/19 visually checked for burned-in answer text;
selection **frozen before any model was evaluated** and untouched since;
sourced from "English Translation (original)" rather than the re-aligned file,
with the reason recorded.

The blocker is licensing, not quality — CC BY-NC 4.0 benchmarks fine but can
never ship. Same for both checkpoints scored on it: Uni-Sign (CC BY-NC-4.0
checkpoint, no code LICENSE file) and OpenSLT (MIT code, CC BY-NC-ND weights).

## Guards in place

- `asl-eval/check_leakage.py` — OCR detector, **two passes per frame** (whole
  frame upscaled, and bottom third upscaled), because tesseract reads nothing
  from 155's captions at native 640×360 and reads them perfectly from an
  upscaled crop. A full-frame-only checker would have cleared the very file
  that caused the contamination. Validated against both known positives on
  every run. Measured separation: contaminated 0.85–0.97, clean 0.00,
  threshold 0.30 — nothing near the line. Five clean videos *do* have on-screen
  text and are correctly not flagged; detecting text is not detecting leakage.
- `asl-eval/corpus_guard.py` — refuses leaky inputs and retracted predictions.
- `input_md5` recorded in `run_metadata`, so a prediction traces to the file it
  actually read.
- `TestProductionParity` — loads curify-studio's `asl_utils.py` directly by path
  and diffs constants, prompt, budget curve and dedup behaviour. Confirmed to
  fail on drift, not merely to pass in sync. Skips cleanly when curify-studio is
  not checked out alongside.
- 79 tests passing in the eval harness.

## Gaps, ranked

1. **No prediction from any current config on any clean input.** The harness is
   built and has nothing to score.
2. **The gold driving every Curify accuracy claim is circular** (1252), and the
   other's provenance is unresolved (155).
3. **1320 is the best reference in the corpus and has never been run.** Masked
   input is built and verified exhaustively — band fully black in 4112 of 4112
   frames, cost measured at 8 frames (0.3 s of 137) where the hands enter the
   band during active signing. The reference still needs an annotator confirming
   the caption text against the signing; production direction is already settled.
4. **8 videos have no reference.** Annotating 1477 + 1474 is ~18 s of video and
   both already have predictions, so each yields an immediately scored case.
5. **Curify has never been run on How2Sign**, so nothing connects the internal
   and public evidence.
6. **Everything commercially licensed is unmeasured** (Gemini native video);
   everything measured is non-commercial or license-blocked.

---

## Layout

```
asl-translator/
├── data/
│   ├── asl_corpus/                 # 13 real ASL videos + references + predictions — see its own README
│   └── public_benchmarks/
│       └── how2sign/               # 19-clip frozen public benchmark (references in git, videos local-only)
├── asl-ground-truth-annotator/     # local browser tool for creating/correcting timestamped English ground truth
└── asl-eval/                       # local scorer (WER/CER/timing) + offline production-config-equivalent runner
```

## Where things live

- **Corpus** — `data/asl_corpus/`. 13 real user-submitted videos, with ground truth where it exists and production-model predictions where a job ran. See `data/asl_corpus/README.md` for per-video notes and `manifest.json` for machine-readable metadata. Contamination history in `data/asl_corpus/CONTAMINATION.md`.
- **Public benchmark** — `data/public_benchmarks/how2sign/`. Frozen 19-clip subset of the official How2Sign test split, for apples-to-apples comparison against open-source SLT baselines. Videos are gitignored; see its README to stage them.
- **Manual ground-truth annotation tool** — `asl-ground-truth-annotator/`. Static HTML/JS, no server/network component, used to create and correct timestamped English references against a loaded video. See its README to launch it.
- **Evaluation tool** — `asl-eval/`. Stdlib-only scorer (`evaluate.py`) comparing a reference SRT against a prediction JSON (WER/CER/timing), a readiness checker (`status.py`), a leakage detector (`check_leakage.py`), a corpus guard (`corpus_guard.py`), and an offline production-configuration-equivalent runner (`run_current_model.py`, dry-run by default, gated real calls). See its README for usage and test instructions.

## Workflow

```
video → independent ground truth → prediction → evaluation → failure analysis → optimization experiment
```

1. Pick a corpus video (or add a new one) under `data/asl_corpus/videos/`.
2. Establish a reference whose **source is independent of what it will score** — see [Reference independence](#reference-independence). Use `asl-ground-truth-annotator/` to create or correct a timestamped English reference, exported into `data/asl_corpus/ground_truth/`. Record provenance alongside it; the `.provenance.json` files under `ground_truth_candidates/signcaption/` are the format to copy.
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
files.** See `data/asl_corpus/README.md` for the full sensitivity notice and
the few lower-risk items that are separable if something shareable is ever
needed.

Note that `155` and `1252` were uploaded to SignCaption (Sign-Speak) on
2026-08-31 to produce the external-reference comparisons above. Sign-Speak's
public Customer ToS licenses uploaded content back to them on a "worldwide,
non-exclusive, perpetual, irrevocable, royalty-free" basis "for developing and
training our AI Models." That is a completed disclosure, not a hypothetical
one, and it should inform any further third-party upload decision.

`data/public_benchmarks/` is **not** covered by this notice — it is public
research data under CC BY-NC 4.0. Keep the two directories distinct.
