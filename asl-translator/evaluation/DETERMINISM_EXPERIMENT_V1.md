# Determinism experiment v1 — does `temperature=0` improve baseline0 repeatability?

**Status: COMPLETE.** Both gated real model calls (Step 1, below) were
executed in a prior turn of this task (outside this document's authorship);
this update performs the analysis those two runs unblocked — comparisons
B, C, D — and answers the primary question. Section "What actually ran"
is authoritative about what did and did not happen, and has been updated
from the prior PLANNED/GATED version of this document to reflect that the
two real runs now exist on disk.

## Why this experiment

From `asl-translator/evaluation/SIGNCAPTION_COMPARISON_V1.md`: `1466_nohead-half1_189.5s`
and `1467_nohead-half1_189.5s` are documented (`asl-translator/data/asl_corpus/README.md`)
as the *same underlying video content*, submitted as two independent
production jobs 11 seconds apart. Their existing `predictions_baseline0`
outputs disagree with each other (WER 0.9706) at least as much as either
disagrees with an unrelated external tool (SignCaption, WER 0.9505 both).
That is evidence *for* baseline0's own non-determinism as a major driver of
observed disagreement, but it doesn't by itself test whether pinning
`temperature=0` (instead of baseline0's unset/default temperature) reduces
that non-determinism. This experiment tests that directly, on the same
video, holding content fixed.

**Primary success criterion: repeatability (run-to-run consistency), not
closeness to SignCaption or any other accuracy claim.** SignCaption
comparisons (C, D below) are secondary context only, per instructions, and
SignCaption is not human-verified ground truth (see
`asl-translator/evaluation/SIGNCAPTION_COMPARISON_V1.md` provenance note).

## Step 0: inspect the existing runner (done, no network)

`asl-translator/asl-eval/run_current_model.py` was inspected before writing
any new code — no new runner was built. Relevant facts confirmed by reading
the source (`asl-translator/asl-eval/README.md` documents the same):

- `--config {baseline0,temperature0}` — `temperature0` passes
  `temperature=0.0` explicitly to `GenerateContentConfig`; `baseline0` omits
  the argument (provider default, empirically ~1.0).
- Default mode is dry-run: local ffmpeg/numpy motion-probe → segment →
  timestamp-allocation only. Never imports `google.genai`, never requires
  `GEMINI_API_KEY`, makes no network call.
- The real-call path requires **both** `--run` and
  `--acknowledge-private-data-upload` together, plus `GEMINI_API_KEY` in the
  environment, plus `--output <path>`. `google.genai` is imported only
  inside that gated function.

Dry-run preview executed prior to any real call (no network — the documented
safe path):

```
$ python3 asl-translator/asl-eval/run_current_model.py \
    --video asl-translator/data/asl_corpus/videos/1466_nohead-half1_189.5s.mp4 \
    --config temperature0

DRY RUN ONLY — NO MODEL CALL WAS MADE.
video                 : asl-translator/data/asl_corpus/videos/1466_nohead-half1_189.5s.mp4
config                : temperature0
model                 : gemini-2.5-flash
temperature mode      : 0.0
duration_s            : 189.504
motion probe count    : 757 (probe_fps=4.0)
active runs           : 46
idle runs             : 47
frame_budget          : 96
sampled frame count   : 96
used full budget      : True
expected Gemini calls : 4 (batch_size=24)
```

## Chosen video for both new runs

**`1466_nohead-half1_189.5s`** (not 1467) — per instructions, "prefer the
same underlying video associated with the existing 1466/1467 determinism
pair"; 1466 is the lower-numbered / first-listed member of that pair and
already has an existing `baseline0` prediction to compare against for
comparison A. Since 1466 and 1467 are documented content-identical, either
video file would exercise the same underlying signing; 1466 was picked
arbitrarily between two equivalent options, not for any content reason.

## What actually ran

| Step | Action | Status |
|---|---|---|
| 0 | Inspect `run_current_model.py` CLI | **Done** (no network) |
| 0 | Dry-run preview on 1466's video, `--config temperature0` | **Done** (no network, shown above) |
| 1 | Real run 1 (`temperature0`, `--run`) on 1466's video → `predictions_eval/1466_nohead-half1_189.5s_temperature0_repeat1.json` | **Done** — 18 segments, 4 model calls |
| 1 | Real run 2 (`temperature0`, `--run`) on 1466's video → `predictions_eval/1466_nohead-half1_189.5s_temperature0_repeat2.json` | **Done** — 15 segments, 4 model calls |
| 2 | Preserve both outputs separately, no overwrite | **Done** — two distinct `_repeat1`/`_repeat2` files, neither overwrites the other or any pre-existing file |
| 3A | Compare baseline0 1466 vs baseline0 1467 | **Done** |
| 3B | Compare temperature0 repeat1 vs repeat2 | **Done** |
| 3C | Compare temperature0 repeat1 vs SignCaption | **Done** |
| 3D | Compare temperature0 repeat2 vs SignCaption | **Done** |

Run metadata (from each prediction JSON's own `run_metadata` block — both
runs used identical settings, differing only in the model's own sampling):

| Field | repeat1 | repeat2 |
|---|---|---|
| config | temperature0 | temperature0 |
| temperature | 0.0 | 0.0 |
| model | gemini-2.5-flash | gemini-2.5-flash |
| frame_budget / frames_sampled | 96 / 96 | 96 / 96 |
| batch_size | 24 | 24 |
| model_calls | 4 | 4 |
| segments produced | 18 | 15 |

No file under `predictions_baseline0/`, `ground_truth/`, or
`evaluation_set.json` was touched by these runs. No pre-existing file under
`predictions_eval/` was overwritten; both outputs are new filenames. No
further API calls were made beyond the two runs already completed.

All four comparisons below were computed locally, no network calls, by
reusing `asl-eval/lib.py`'s existing `parse_prediction_json` /
`parse_srt` / `text_metrics` / `timing_metrics` / `align_segments`
functions directly (a one-off script, not added to the repo, mirroring the
approach already used for comparison A in
`SIGNCAPTION_COMPARISON_V1.md` § "3c"). `evaluate.py` itself was not used
unmodified for B, since both sides are prediction JSONs rather than an SRT
reference; for C and D the SignCaption SRT plays the reference role, exactly
as in `SIGNCAPTION_COMPARISON_V1.md` § "3a"/"3b".

---

## Comparison A: baseline0 1466 vs. baseline0 1467 (control — the pre-existing pair)

Recomputed here (not re-run) from the two pre-existing `predictions_baseline0`
files, for direct side-by-side reference against B/C/D. Matches
`SIGNCAPTION_COMPARISON_V1.md` § "3c" exactly.

| Metric | Value |
|---|---|
| 1466 segment count | 24 |
| 1467 segment count | 29 |
| 1466 words | 68 |
| 1467 words | 71 |
| Substitutions | 63 |
| Deletions | 0 |
| Insertions | 3 |
| **WER** | **0.9706** |
| **CER** | **0.7088** |
| 1466 coverage | 85.970s |
| 1467 coverage | 71.090s |
| Overlap | 49.710s |
| **Temporal IoU** | **0.4631** |
| Segment-count difference | 5 (24 vs. 29) |

Major textual differences: essentially total — 63 of 68 words substituted;
almost nothing survives alignment intact. Timing/segmentation also diverges
substantially: 24 vs. 29 segments, moderate temporal IoU (0.4631). This is
baseline0's own (temperature unset, ≈1.0) run-to-run disagreement and serves
as the **control** for this experiment.

---

## Comparison B: temperature0 repeat1 vs. repeat2 (the actual repeatability test)

| Metric | Value |
|---|---|
| repeat1 segment count | 18 |
| repeat2 segment count | 15 |
| repeat1 words | 84 |
| repeat2 words | 82 |
| Substitutions | 13 |
| Deletions | 2 |
| Insertions | 0 |
| **WER** | **0.1786** |
| **CER** | **0.1335** |
| repeat1 coverage | 107.360s |
| repeat2 coverage | 110.280s |
| Overlap | 103.600s |
| Temporal precision | 0.9394 |
| Temporal recall | 0.9650 |
| **Temporal IoU** | **0.9085** |
| Segment-count difference | 3 (18 vs. 15) |

### Segment-by-segment alignment (repeat1 as reference index)

| # | Time (repeat1) | repeat1 text | repeat2 text (best overlap) | IoU |
|---|---|---|---|---|
| 0 | 1.12–14.29 | "Explain what is wrong with you." | "You explain and show." | 0.71 |
| 1 | 20.25–20.75 | "You hit." | "You get ready, join, and start to practice." | 0.04 |
| 2 | 22.75–25.31 | "Build together." | "You get ready, join, and start to practice." | 0.21 |
| 3 | 27.59–32.51 | "Give to rub." | "You get ready, join, and start to practice." | 0.40 |
| 4 | 33.74–38.66 | "Build three, then two." | "Three, start. Two. Well done, you." | 0.59 |
| 5 | 41.06–42.15 | "Clap for you." | "Three, start. Two. Well done, you." | 0.13 |
| 6 | 44.75–49.31 | "Talking about payment." | "Talking about payment." | **1.00** |
| 7 | 59.50–64.44 | "Talking about payment." | "Talking about payment." | **1.00** |
| 8 | 70.62–75.69 | "Talking about payment." | "Talking about payment." | **1.00** |
| 9 | 80.69–84.44 | "Talking about payment." | "Talking about payment." | **1.00** |
| 10 | 89.65–94.81 | "Wash your hands, finished." | "Wash your hands, finished." | **1.00** |
| 11 | 98.75–105.44 | "I am good, all three of us." | "I am good, all three of us." | **1.00** |
| 12 | 109.4–116.19 | "You have nothing to worry about." | "You have nothing to worry about." | **1.00** |
| 13 | 120.5–133.83 | "It's good. Two people walk across calmly." | (identical, word-for-word) | **1.00** |
| 14 | 135.88–146.19 | "Hands join, then open and close. Two items are placed here." | (identical, word-for-word) | **1.00** |
| 15 | 157.31–163.06 | "Stop, it's over." | (identical, word-for-word) | **1.00** |
| 16 | 172.0–175.0 | "Good, strong." | (identical, word-for-word) | **1.00** |
| 17 | 177.32–188.17 | "Two items are here, they open and close. With two." | (identical, word-for-word) | **1.00** |

### Major textual and timing/segmentation differences

- **Segments 6–17 (12 of repeat1's 18 segments) are byte-for-byte identical**
  in both text and start/end timestamps between the two runs. This spans
  44.75s–188.17s — **~143.4s of the clip's 189.25s duration (~76%)**.
- All disagreement is concentrated in the **first ~42 seconds** of the clip
  (repeat1 segments 0–5, repeat2 segments 0–2): repeat1 splits this window
  into 6 short segments ("Explain what is wrong with you." / "You hit." /
  "Build together." / "Give to rub." / "Build three, then two." / "Clap for
  you."), repeat2 merges the same window into 3 longer segments ("You
  explain and show." / "You get ready, join, and start to practice." /
  "Three, start. Two. Well done, you."). The two versions describe
  related but not identical content in that window (both mention explaining/
  showing, readiness/starting, counting to two/three) — this looks like a
  genuine content/segmentation disagreement in the opening stretch, not
  pure noise, but it is real disagreement nonetheless.
- Segment counts differ only because of this opening-window split (6 vs. 3
  segments); every segment after that point is 1:1 and identical.
- 13 substitutions and 2 deletions, all confined to that opening window; 0
  insertions.

---

## Comparison C: temperature0 repeat1 vs. SignCaption (secondary context only)

Uses the same SignCaption reference file as `SIGNCAPTION_COMPARISON_V1.md`
§ "3a"/"3b" (`ground_truth_candidates/signcaption/1467_nohead-half1_189.5s.mp4.srt`
— named after 1467 despite 1466/1467 being documented content-identical; see
that document's file-naming-discrepancy note, unchanged here).

| Metric | Value |
|---|---|
| SignCaption segment count | 16 |
| repeat1 segment count | 18 |
| SignCaption words | 101 |
| repeat1 words | 84 |
| Substitutions | 79 |
| Deletions | 17 |
| Insertions | 0 |
| **WER** | **0.9505** |
| **CER** | **0.7305** |
| SignCaption coverage | 126.932s |
| repeat1 coverage | 107.360s |
| Overlap | 76.335s |
| Temporal precision | 0.7110 |
| Temporal recall | 0.6014 |
| **Temporal IoU** | **0.4833** |

Major textual differences: SignCaption's transcript is the same lizard
narrative documented in `SIGNCAPTION_COMPARISON_V1.md` ("Its tail is short
and stubby... It looks like a giant lizard... The leaves grow slowly and
become small and round"). repeat1's transcript is the same
collaborative/procedural register as baseline0's runs ("Explain what is
wrong with you.", "Talking about payment." ×4, "Wash your hands,
finished.", etc.) — a different register from SignCaption entirely, same as
both baseline0 comparisons. WER (0.9505) is numerically identical to the
existing baseline0-vs-SignCaption result to 4 decimals — again very likely
coincidence given differing sub/del counts (79/17 here vs. 63/33 and
66/30 for baseline0), not evidence of agreement in content.

## Comparison D: temperature0 repeat2 vs. SignCaption (secondary context only)

| Metric | Value |
|---|---|
| SignCaption segment count | 16 |
| repeat2 segment count | 15 |
| SignCaption words | 101 |
| repeat2 words | 82 |
| Substitutions | 77 |
| Deletions | 19 |
| Insertions | 0 |
| **WER** | **0.9505** |
| **CER** | **0.7243** |
| SignCaption coverage | 126.932s |
| repeat2 coverage | 110.280s |
| Overlap | 78.632s |
| Temporal precision | 0.7130 |
| Temporal recall | 0.6195 |
| **Temporal IoU** | **0.4959** |

Same pattern as C: near-total text disagreement with SignCaption (WER
0.9505, identical to C and to both baseline0-vs-SignCaption results to 4
decimals — coincidental, not meaningful agreement), moderate temporal IoU
(0.4959, marginally higher than C's 0.4833 and higher than either baseline0
run's IoU against SignCaption, 0.3654/0.3344).

---

## Cross-comparison table (all four pairs plus the control)

| Pair | WER | CER | Temporal IoU | Segment counts |
|---|---|---|---|---|
| **Control: baseline0 1466 vs. 1467 (self-disagreement)** | **0.9706** | **0.7088** | **0.4631** | 24 vs. 29 |
| **B: temperature0 repeat1 vs. repeat2 (self-disagreement)** | **0.1786** | **0.1335** | **0.9085** | 18 vs. 15 |
| C: temperature0 repeat1 vs. SignCaption | 0.9505 | 0.7305 | 0.4833 | 18 vs. 16 |
| D: temperature0 repeat2 vs. SignCaption | 0.9505 | 0.7243 | 0.4959 | 15 vs. 16 |
| (reference) baseline0 1466 vs. SignCaption | 0.9505 | 0.7119 | 0.3654 | 24 vs. 16 |
| (reference) baseline0 1467 vs. SignCaption | 0.9505 | 0.7016 | 0.3344 | 29 vs. 16 |

---

## Primary question: did `temperature=0` materially improve repeatability?

### Observed fact

- Self-disagreement WER drops from **0.9706** (baseline0, temperature
  unset/≈1.0) to **0.1786** (temperature0) on the same underlying video
  content — an 82% relative reduction in word error rate between a system's
  own two independent runs.
- Self-disagreement CER drops from **0.7088** to **0.1335** — an 81%
  relative reduction.
- Self-disagreement temporal IoU rises from **0.4631** to **0.9085** — the
  two temperature0 runs agree on segment timing almost completely, versus
  only moderate agreement at baseline0.
- **12 of repeat1's 18 segments (67% of segments, ~76% of the clip's
  duration) are word-for-word and timestamp-for-timestamp identical**
  between the two temperature0 runs. No segment in the baseline0 1466-vs-1467
  pair reaches that bar; the closest baseline0 gets is two isolated IoU=1.0
  segments with *related-but-not-identical* text (per
  `SIGNCAPTION_COMPARISON_V1.md` § 3c), not exact text matches.
- All remaining temperature0 disagreement (13 substitutions, 2 deletions) is
  concentrated in a single ~42-second opening window; nothing outside that
  window disagrees at all.
- Comparisons C and D (temperature0 vs. SignCaption) still show near-total
  text disagreement (WER 0.9505 both, matching baseline0's own WER against
  SignCaption to 4 decimals) and only moderate temporal IoU (0.48–0.50) —
  essentially unchanged from the baseline0-vs-SignCaption result.

### Inference (directly supported by the numbers above, low speculation)

- On this video's content, pinning `temperature=0` **substantially reduces**
  Curify's own run-to-run non-determinism, on both text content and
  segment timing. This is a large, one-sided effect (WER 0.97 → 0.18,
  IoU 0.46 → 0.91), not a marginal or ambiguous one — it is the opposite of
  the earlier hypothesis raised in `SIGNCAPTION_COMPARISON_V1.md` that
  1466/1467's content might behave like 1252 (WER 0.82 baseline0-vs-temperature0,
  large residual disagreement) rather than like 155 (WER 0.09, near-total
  agreement). It instead behaves like the 155 case.
- The bulk of the residual repeat1/repeat2 disagreement is localized to one
  short window early in the clip, not spread uniformly across the whole
  189s duration. That is consistent with temperature=0 not eliminating
  sampling noise everywhere, but sharply reducing its *frequency* — most of
  the clip's captioned content is now fully reproducible run-to-run, and a
  minority is not.
- Because C and D (temperature0 vs. SignCaption) remain at essentially the
  same WER/IoU as the pre-existing baseline0-vs-SignCaption comparisons,
  the large baseline0-vs-SignCaption gap documented in
  `SIGNCAPTION_COMPARISON_V1.md` is **not** primarily explained by
  temperature-driven noise alone — fixing self-repeatability did not close
  the gap to SignCaption at all. Either SignCaption and Curify (at any
  temperature) genuinely describe this content differently, or SignCaption
  itself is the less reliable side, or some mixture of both. This
  experiment cannot distinguish those possibilities — it was not designed
  to, and SignCaption is not verified gold (see Provenance note in
  `SIGNCAPTION_COMPARISON_V1.md`).

### Hypothesis (plausible, not established by this data alone)

- The one-off, ~42-second opening-window disagreement between repeat1 and
  repeat2 may be tied to something specific about that segment of content
  (e.g., a passage with more visually ambiguous or rapid signing that the
  motion-adaptive frame sampler and/or the model handles less
  deterministically even at temperature=0) rather than being a uniform
  residual noise floor spread evenly through the video. This experiment's
  single repeat pair cannot confirm that — it would need a third
  temperature0 run on the same video to see whether the *same* opening
  window is again the outlier, or a different window is, before treating
  "the opening is harder" as an established pattern rather than a
  one-time coincidence.
- Because only one video (1466's content) was tested at temperature=0 with
  a real repeat pair, it remains unknown whether this magnitude of
  improvement (WER 0.97 → 0.18) generalizes to other videos, or whether
  1466/1467's content happens to be an easy case for temperature=0 the same
  way 155 was in the earlier baseline0-vs-temperature0 spot-check (WER
  0.09) while 1252 was not (WER 0.82 even comparing across different
  temperatures, not even same-temperature self-repeatability). No claim
  here should be read as "temperature=0 always yields ~0.18 WER
  self-disagreement" — it is this-video evidence, not a general law.
- This experiment says nothing about whether temperature=0's transcripts
  are more *accurate* (closer to what was actually signed) than
  baseline0's — only that they are more *repeatable*. Comparisons C/D show
  temperature=0 is no closer to SignCaption than baseline0 was, and
  SignCaption itself is unverified, so no accuracy claim is supported
  either way. Resolving accuracy requires a human-verified reference,
  which does not exist for this video today.

---

## Secondary context: existing 155/1252 baseline0-vs-temperature0 evidence

Unchanged from the prior version of this document — kept here for
continuity, not mixed into the repeatability analysis above (this is a
different comparison shape: baseline0-vs-temperature0 on two different
configs, not temperature0-vs-temperature0 self-repeatability):

| Video | WER (baseline0 vs. temperature0) | CER | Temporal IoU |
|---|---|---|---|
| `155_demo_asl-demo-translation_26.7s` | 0.0909 | 0.1274 | 0.8283 |
| `1252_1000016397_76.8s` | 0.82 | 0.6429 | 0.7129 |

This experiment's result (WER 0.18 self-disagreement on 1466 at
temperature0) sits closer to 155's low-disagreement pattern than to 1252's
high-disagreement pattern — consistent with, though not proof of, the
earlier speculative framing that temperature's effect is content-dependent
rather than uniform.

---

## Recommendation

1. **Does `temperature=0` materially improve stability?** Yes, on the
   evidence gathered here. Self-disagreement WER fell from 0.9706 to 0.1786
   and temporal IoU rose from 0.4631 to 0.9085 on the same video content —
   a large, one-sided effect, not a marginal one. This is an **observed
   fact for this one video**, not yet a general claim about all corpus
   content (see Hypothesis above).

2. **Is it sufficient by itself?** No. Two gaps remain even after pinning
   temperature=0: (a) residual non-determinism is still concentrated in
   part of the clip (repeat1/repeat2 disagree completely in the first ~42s,
   agree completely afterward) rather than eliminated, so temperature=0
   is a large improvement, not a full fix; and (b) closeness to SignCaption
   did not improve at all (WER still ~0.95, essentially unchanged from
   baseline0) — so temperature=0 addresses run-to-run *repeatability*, and
   says nothing about whether the model's transcripts are *accurate*, which
   is a separate, still-open question.

3. **Smallest next production optimization experiment:** Run a third
   `temperature0` repeat on the **same** 1466 video (same tooling, same
   `--config temperature0 --run --acknowledge-private-data-upload`,
   one more real call) to test whether the ~42-second opening-window
   disagreement seen between repeat1 and repeat2 recurs in the same
   location or moves — this is the cheapest way (one more real call, no
   new infrastructure, no new video) to learn whether that residual noise
   is content-localized (a specific hard passage) or just random which
   part of the clip is unstable on any given run. That result should
   directly inform whether further noise reduction (e.g., a fixed
   `seed` parameter if the API supports one, or lower `frame_budget`
   variance) is worth pursuing before moving to a different video.

4. **Is more SignCaption data necessary before proceeding?** Not yet, and
   not as the next spend. This experiment already shows that fixing
   Curify's own repeatability (temperature=0) does not narrow the gap to
   SignCaption at all (WER stayed ~0.95). Spending more SignCaption credits
   right now would very likely just reproduce that same "near-total
   disagreement, unmoved by temperature" finding on a new clip, without
   answering *why* the gap persists. The more informative next spend, once
   the temperature-0 opening-window question above is resolved, is a
   **human-verified reference** for 1466/1467 (or another already-tested
   clip) — the only evidence type that can tell whether Curify (at either
   temperature) or SignCaption is closer to the actual signing, which no
   further tool-vs-tool comparison, at any temperature, can establish on
   its own.

---

## Scope / non-modification note

- No file under `predictions_baseline0/`, `ground_truth/`, or
  `evaluation_set.json` was modified by this update.
- No existing file under `predictions_eval/` was modified or overwritten;
  the two `_repeat1`/`_repeat2` files used here were already present on
  disk when this analysis began (produced by a prior turn of this task, not
  by this update).
- No new API/model calls were made while producing this update — all four
  comparisons (A–D) were computed locally against files already on disk,
  reusing `asl-eval/lib.py`'s existing metric functions directly (a
  one-off script, not added to the repo), the same approach used for
  comparison A in `SIGNCAPTION_COMPARISON_V1.md`.
- SignCaption is not, and is not treated as, `verified_gold` anywhere in
  this document; comparisons C and D are explicitly secondary context, not
  the primary repeatability metric.
- This document was not committed or pushed, and no PR was created.
