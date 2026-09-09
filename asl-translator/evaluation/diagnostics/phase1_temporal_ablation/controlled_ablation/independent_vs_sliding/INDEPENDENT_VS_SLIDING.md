# Phase 3B — Controlled Batch/Context Ablation: Independent Batches vs. Overlapping Sliding Windows

**Research question:** Does replacing the current independent 24-frame batches
with overlapping/sliding temporal windows materially improve Gemini ASL
translation, while keeping the sampled frames, sampling strategy, model,
prompt, and decoding settings fixed?

**Scope:** the same 12 fixed diagnostic clips (`diagnostic_12_clips.json`)
used in Phase 3A. Not the 40-clip taxonomy, not the 128-clip benchmark.

## Design

| | Arm A — existing baseline | Arm B — new controlled arm |
|---|---|---|
| config | `evaluation_2026_09_04_gemini_3_6` | `phase3b_independent_vs_sliding_window24_stride12_2026_09_07` |
| sampled frames | production adaptive/motion-weighted sampler | **identical** — reused, NOT resampled |
| batching | independent, non-overlapping, 24 frames/batch | **overlapping sliding windows**, size=24, stride=12 (50% overlap) |
| model / prompt / decoding | gemini-3.6-flash, thinking_level=medium, `PRODUCTION_PROMPT`, temperature unset | identical (read directly from `run_current_model.CONFIGS["evaluation_2026_09_04_gemini_3_6"]`, not duplicated by value) |
| dedup | `merge_adjacent_duplicates()`, exact-text adjacent match | same function, applied AFTER ownership-based merge (see below) |
| predictions | **REUSED**, not rerun | **NEW** real Gemini calls, this experiment |

The single controlled variable is batch/window construction over the same
frame sequence. `asl-eval/run_current_model.py` was **not modified at all**
for this experiment (confirmed by `git diff` showing zero changes to that file
in this task) — it is imported strictly read-only for its sampler and prompt
functions.

## Pre-flight validation (before any Gemini call — `design_check.json`)

- **Same 12 diagnostic IDs**, confirmed against `diagnostic_12_clips.json`.
- **Baseline frame_budget and frame count reproduced exactly for all 12
  clips** — recomputed locally via the unmodified
  `probe_motion`/`segment_runs`/`allocate_timestamps` and asserted equal to
  each clip's own saved baseline `run_metadata.frame_budget` /
  `frames_sampled`. 0 mismatches. (Baseline's real-run JSON does not persist
  the timestamp array itself — this is documented, pre-existing behavior, not
  changed here — so exact reuse is verified by reproducing it deterministically
  from the same unmodified sampler on the same video, the same method already
  used throughout this repo's inspector and Phase 3A.)
- **4 of 12 clips are multi-batch** (frame count > 24):
  `FzmL8SL6Bow_1-8-rgb_front` (51 frames, 3 baseline batches, 4 windows),
  `fzNnTgHa1lM_2-5-rgb_front` (50, 3, 4), `fZM3IcM2Xs4_14_15_16-10-rgb_front`
  (37, 2, 3), `G05uFub3YFc_9-2-rgb_front` (34, 2, 2). The remaining 8 are
  single-batch (exactly 24 frames, MIN_FRAME_BUDGET floor) and therefore
  produce exactly **1** sliding window each — architecturally identical to
  their single baseline batch. These 8 clips were still run as fresh, real
  Gemini calls (not reused from baseline) so any delta on them is an honest,
  empirical measurement of pure decoding noise, not an assumption.
- **Pre-flight estimate:** 21 total sliding-window model calls across the 12
  clips (13 for the 4 multi-batch clips + 8 for the single-window clips), 364
  unique frames, 472 total frame exposures with overlap (108 repeated
  exposures). **Actual: 21 calls**, matching exactly.
- **No confound identified.**

## Merge strategy (designed and documented BEFORE any Gemini call)

1. **What each window sees:** window *i* sees `frames[i·stride : i·stride+24)`
   of the *same* chronologically-ordered sampled-frame sequence baseline A
   used — identical images, identical `[t=...s]` labels, identical
   prompt/model/decoding.
2. **What temporal region each window is responsible for:** a disjoint,
   gap-free "ownership" partition of the clip's time axis, computed **purely
   from window position** (known before any inference): window 0 owns from
   the start of the clip; window *i>0* owns starting at its own first frame's
   timestamp; every window except the last owns up to (not including) the
   next window's first frame's timestamp; the last window owns to the end of
   the clip.
3. **How overlapping outputs are merged:** for each window's returned
   segments, **keep** a segment iff its own reported `start` time falls
   inside that window's owned time range, else discard it. Kept segments from
   all windows are sorted by start time, then passed through the existing,
   unmodified `merge_adjacent_duplicates()` (same `dedup=True` setting
   baseline uses) as a final tidy pass for genuine within-window exact-text
   repeats — **not** as the mechanism for resolving overlap, which the
   ownership partition already does before dedup ever runs. Applying dedup to
   *raw* overlapping output (rather than to the already-disjoint,
   ownership-filtered list) was explicitly avoided, since exact-text matching
   cannot safely resolve two windows describing the same moment in different
   words.
4. **Why it cannot look at ground truth:** the ownership partition is fixed
   entirely by window start/end frame indices — computed from
   `window_size`/`stride`/`n_frames` alone, before any Gemini call is made and
   therefore before any model output exists to consult. The only per-segment
   decision (keep vs. discard) uses that segment's own `start` field, part of
   the model's normal output schema, regardless of correctness — never the
   reference SRT, and never a comparison between what two windows said.
5. **Why the comparison remains fair:** Arm A's predictions are untouched.
   Arm B's merge rule cannot see the reference and cannot selectively keep a
   "better" overlapping segment over a "worse" one — ownership is a fixed
   geometric partition decided in advance, so the final transcript reflects
   exactly one window's read of each moment, chosen only by position. This
   mirrors how a real deployed sliding-window pipeline would have to work (no
   reference available at inference time).

Full per-clip window/ownership geometry: `design_check.json`. A concrete
worked example (`FzmL8SL6Bow_1-8-rgb_front`, 4 windows): window 0 kept 2/3 raw
segments, window 1 kept 1/2, window 2 kept 3/4, window 3 kept 1/1 — the
discarded segments in each case were ones whose reported start fell inside a
neighboring window's owned region, exactly as designed.

## Scoring

| metric | Arm A (independent) | Arm B (sliding) | delta (B − A) |
|---|---|---|---|
| corpus WER (pooled) | 1.0524 | 0.9545 | **-0.0979** |
| mean per-clip WER | 1.0825 | 0.9542 | **-0.1283** |
| median per-clip delta | — | — | **0.0000** |

Per-clip outcome: **4 improved, 2 worsened, 6 unchanged** (out of 12).

**Multi-batch subset (n=4):** mean baseline WER 1.2113 → mean sliding WER
0.9610 (mean delta **-0.2503**, median delta -0.0441); 2 improved, 0 worsened,
2 unchanged.

**Single-batch subset (n=8, architecturally identical to baseline — 1 window
== 1 batch):** mean baseline WER 1.0181 → mean sliding WER 0.9508 (mean delta
**-0.0673**, median delta 0.0000); 2 improved, 2 worsened, 4 unchanged. Since
these 8 clips have zero architectural difference from Arm A, **every non-zero
delta here is decoding noise from a fresh non-deterministic Gemini call, not a
sliding-window effect** — this subset serves as this experiment's own noise
floor.

**Manifest hint buckets** (reference-derived heuristics, not confirmed visual
ASL categories):

| bucket | n | mean delta | n improved / worsened / unchanged |
|---|---|---|---|
| fingerspelling_candidate | 6 | -0.1394 | 1 / 1 / 4 |
| number_token | 2 | -0.0441 | 1 / 0 / 1 |
| question | 2 | +0.0416 | 0 / 1 / 1 |
| plain_no_flag | 2 | -0.3492 | 2 / 0 / 0 |

Sample sizes (n=2–6) are too small for a category-level conclusion; the
`plain_no_flag` bucket's large mean delta is entirely the two single-batch
noise-floor clips discussed below, not a fingerspelling/number/question
effect.

### Side-by-side

| clip_id | reference | baseline_prediction | sliding_prediction | baseline_WER | sliding_WER | delta | n_baseline_calls | n_sliding_calls | diagnostic_reason | hint bucket |
|---|---|---|---|---|---|---|---|---|---|---|
| `FzmL8SL6Bow_1-8-rgb_front` | You want to go and clean up that hole you just made and now we are goi... | I looked and saw a dog approaching. It just stood there, completely fr... | I looked over and noticed, turned the key to pay, What if a bear comes... | 0.9615 | 0.9615 | +0.0000 | 3 | 4 | long_multi_batch_boundary_risk | fingerspelling_candidate |
| `fzNnTgHa1lM_2-5-rgb_front` | So you can tune the G with the lower G and the D with the lower D. So ... | Whenever you go with someone... chronic friend | That one goes with that one. Cronies are people you socialize with. | 0.9412 | 0.9412 | +0.0000 | 3 | 4 | long_multi_batch_boundary_risk | fingerspelling_candidate |
| `fZM3IcM2Xs4_14_15_16-10-rgb_front` | Look at that. Morris sings(Ready to rock and roll today) Kind of feels... | People have many different perspectives and situations, and sharing va... | There are many different ways to combine things, with various options ... | 1.9130 | 1.0000 | -0.9130 | 2 | 3 | fingerspelling_candidate;very_high_wer | fingerspelling_candidate |
| `-g0iPSnQt6w_0-1-rgb_front` | Buenos Dias, I'm Bobby Larew, you didn't know I spoke Spanish, did you... | Back in Barcelona | Bronx | 1.0000 | 1.0000 | +0.0000 | 1 | 1 | fingerspelling_candidate;fast_signing_or_question | fingerspelling_candidate |
| `G05uFub3YFc_9-2-rgb_front` | Again, do maybe twenty breaths, little flow, inhaling and exhaling the... | She smooths out the cloth and places it flat on the table. She sets th... | If your kayak capsizes and you are flipped upside down underwater, kee... | 1.0294 | 0.9412 | -0.0882 | 2 | 2 | number_token | number_token |
| `-g0sqksgyc4_3-2-rgb_front` | So whenever you're moving forward, try to move the front foot first wh... | A spider was crawling on me! | A bug crawled and jumped right into my mouth. | 1.0000 | 1.0000 | +0.0000 | 1 | 1 | number_token;fast_signing_or_question | number_token |
| `92V3oH63zbQ_5-1-rgb_front` | What is keeping your hands inside the baseball? | *(empty)* | *(empty)* | 1.0000 | 1.0000 | +0.0000 | 1 | 1 | fast_signing_or_question | question |
| `Fz-N1S0swh8_2-8-rgb_front` | I'm not going to use a lot, I'm going to use very very little. | Angry | Soup | 1.0000 | 1.0000 | +0.0000 | 1 | 1 | fast_signing_or_question | fingerspelling_candidate |
| `g0TkUiO7t4I_6-8-rgb_front` | Cause wrinkle is the problem with the dry skin. | A cat and a friend a sweet girl comes to a full stop. | The cat and the girl walked under the tree. | 1.4444 | 0.8889 | -0.5555 | 1 | 1 | very_high_wer | plain_no_flag |
| `g2ELiaFjKfs_3-10-rgb_front` | Now we're going to teach them to stay before walking in the road. | After that, then, and lastly, it crawls forward and sits on the edge, ... | After flying, I had a transfer, and finally met my friend. | 1.1429 | 1.0000 | -0.1429 | 1 | 1 | very_high_wer | plain_no_flag |
| `g2NA_eBUcH8_0-3-rgb_front` | Hi, have you ever wanted to learn a new game of poker? | If you want to learn | Who taught you to read? | 0.7500 | 0.8333 | +0.0833 | 1 | 1 | low_wer_contrast | question |
| `G19uBylwQww_1-2-rgb_front` | Hi, my name is Robert Segundo and today I'm going to teach you how to ... | My name is Robert. I was born in California. | My name is Robbie. | 0.8077 | 0.8846 | +0.0769 | 1 | 1 | low_wer_contrast | fingerspelling_candidate |

Full text and all fields: `paired_results.csv` / `.json`. As in Phase 3A, the
LLM-assisted text-semantic-review fields are carried for **Arm A (baseline)
only**, descriptive context — no equivalent semantic review was performed on
Arm B's predictions, and no human or ASL-expert label exists for either arm.

## Interpretation

### 1. Does overlapping context materially improve the 12 diagnostic clips?

**Numerically, yes on aggregate (corpus WER -0.0979, mean WER -0.1283); not
materially in the sense that matters (semantic correctness).** Every single
"improvement" in the side-by-side table above is a swap from one severe
hallucination/topic-mismatch to a *different* severe hallucination or
topic-mismatch that happened to land closer in word count to a short
reference (see question 4 below for detail on every case). Zero of the 12
sliding-arm predictions describe the same real content as their reference.
The two single-batch clips with the largest deltas (`g0TkUiO7t4I` at -0.5555,
`g2ELiaFjKfs` at -0.1429) have **no architectural difference from baseline
at all** — same one batch, same frames — so their movement is 100% decoding
noise, not a sliding-window effect. That noise floor (mean delta -0.0673
across all 8 single-batch clips) is not small relative to the multi-batch
subset's mean delta (-0.2503), so a meaningful fraction of the apparent
"aggregate improvement" cannot be attributed to the windowing change at all.

### 2. Do multi-batch/longer clips benefit more than single-batch clips?

**Directionally yes, but the gap is not large relative to the noise floor and
n is too small to be confident.** Multi-batch mean delta -0.2503 vs.
single-batch mean delta -0.0673 — a real difference in aggregate, and
multi-batch clips had 0 worsened vs. single-batch's 2 worsened, which is a
mildly encouraging pattern. But n=4 for the multi-batch subset is very small,
one of those four clips (`fZM3IcM2Xs4`, -0.9130) dominates the multi-batch
mean by itself, and — as with question 1 — the "improvement" there is not a
semantic correction (see question 4). Two of the four multi-batch clips
(`FzmL8SL6Bow`, `fzNnTgHa1lM`) showed **exactly zero** WER change despite
completely different generated text under the sliding arm, illustrating that
even a WER match here reflects near-total-failure arithmetic, not stability
of a correct-ish output.

### 3. Are there concrete examples where a failure near a baseline batch seam improves?

**No.** None of the 4 multi-batch clips' baseline predictions were previously
tagged (in either the Phase-1 human-review pass or the LLM-assisted
text-semantic review) as having a segmentation/seam-artifact failure
(truncated idea, duplicated fragment at a batch boundary) to begin with —
their dominant failure mode was total topic hallucination, present already in
a single batch's output, not a batch-boundary-specific symptom. The
comparison inspectors (`inspectors/*.html`) show the sliding windows
correctly gaining additional temporal context at each seam (see the worked
`FzmL8SL6Bow` example in the Merge Strategy section — window boundaries and
ownership assignment behave exactly as designed), but that extra context did
not produce any inspectable case of "a previously cut-off idea is now
completed correctly." This is a negative finding, reported honestly rather
than reached for.

### 4. Does the dominant topic-level semantic failure remain?

**Yes, unambiguously, in all 12 clips under both arms.** Walking the full
side-by-side table: `FzmL8SL6Bow` (hole/wall repair reference) stays a
completely different animal narrative (dog/bear → turtle/boat) under both
arms; `fzNnTgHa1lM` (violin tuning) stays unrelated nonsense under both arms;
`fZM3IcM2Xs4` (festive music reference) goes from one hallucination
(interpersonal conflict + chest pain) to another (combining things + racing
heart) — both entirely unrelated to the reference, this is the -0.9130
"biggest win" and it is not a semantic win at all; `G05uFub3YFc` (breathing
exercise) goes from a cloth/container/fire narrative to a kayak-capsizing
narrative — again fully unrelated, just shorter and closer in length to a
long reference; `g0TkUiO7t4I` (wrinkle/dry-skin reference, 8 words) goes from
"a cat and a friend, a sweet girl comes to a full stop" to "the cat and the
girl walked under the tree" — same fabricated cat/girl characters persist,
this is the largest single-batch (noise-floor) delta and is clearly not a
correction. Every remaining clip is similarly unrelated under both arms. This
confirms, for the third time across Phase 3A and 3B, that the benchmark's
dominant failure mode is topic-level content hallucination that neither
sampling-strategy nor batch-context changes have touched.

### 5. Is the effect large enough to justify scaling to more than 12 clips?

**No, not as a claim of semantic improvement.** The numeric aggregate
movement is larger than Phase 3A's uniform-sampling result, which makes it
worth distinguishing carefully: **this is a genuine WER-metric effect from
architecture** (more model calls per multi-batch clip, more chances to
produce a shorter/differently-worded fabrication that happens to score
better against a short-ish reference under edit-distance WER) but **not
evidence the model is reading the signing any better.** Scaling this arm to
more clips *could* be worth doing specifically to get a larger, less
noise-dominated read on the multi-batch subset's WER delta (n=4 is too small
here to trust -0.2503 as a stable number) — but only framed as "does
overlapping context change the WER-scoring numbers," not as "does it fix
translation quality," since nothing in this pass shows any genuine semantic
recovery to chase. Any future scaling should also budget real API cost:
extrapolating this run's ~1.17x call multiplier for multi-batch clips (13
sliding calls vs. 9 baseline-equivalent calls for the same 4 clips) is cheap
at 12 clips but should be estimated properly (via a `design_check_sliding.py`
run) before committing to a larger corpus.

## Files in this directory

- `design_check.json` — LOCAL-ONLY (no model calls) window/ownership geometry,
  baseline-timestamp-reuse verification, and call/frame estimate, produced by
  `design_check_sliding.py` before any inference.
- `predictions/` — the 12 new Arm-B (sliding-window) prediction JSONs,
  including full per-window `window_reports` (raw/kept/discarded segment
  counts) for auditability. Arm A's predictions are read directly from
  `curify_gemini_3_6_2026_09_04/predictions/` and are not copied here.
- `paired_results.csv` / `.json` — per-clip WER for both arms, deltas,
  multi-batch/single-batch and hint-bucket subset stats, and descriptive-only
  baseline text-semantic-review fields, produced by `score_and_report_sliding.py`.
- `inspectors/` — one HTML page per clip (baseline independent-batch timeline
  vs. sliding-window timeline with overlap lanes, over the identical sampled
  frame sequence) plus `index.html`, produced by
  `build_comparison_inspector_sliding.py`. No model call; reuses the existing
  Phase-1 inspector's thumbnail/timeline helpers.
- `design_check_sliding.py`, `run_sliding_arm.py`, `score_and_report_sliding.py`,
  `build_comparison_inspector_sliding.py` (in the parent `controlled_ablation/`
  directory) — the four scripts that produced everything above, run in that
  order.
