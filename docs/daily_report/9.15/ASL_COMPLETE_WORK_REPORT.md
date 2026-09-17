# Curify ASL Translation — Complete Work Report
Date: 2026-09-15
Repository: `visual-search-adhoc-asl-task-c`
Branch: `baobao/asl-temporal-ablation-2026-09-06` (HEAD `fdc2872`)

This report consolidates everything committed or in-progress on this branch through
2026-09-15, builds on `docs/daily_report/9.11/ASL_WORK_REPORT.md` (still current for the
temporal-ablation, native-video, and trajectory sections — nothing in those areas changed
between `01cfd05` and today), and adds: the SignCaption 5-clip and Batch-2/combined-15
pilots, the BLEU-rounding correction, and today's Uni-Sign inference-parameter audit.

---

## 1. Executive Summary

- We built a reproducible, frozen evaluation and diagnostic framework for ASL video
  translation (128-clip How2Sign v2 benchmark, matched cross-system scorecards, a
  12-clip qualitative inspector).
- Current generic Gemini frame/native-video approaches still show severe semantic/topic
  failures — corpus WER stays near or above 1.0 for the Curify/Gemini frame baseline and
  for Gemini native-video on the clips scored so far.
- Simple temporal sampling changes (2fps↔8fps, adaptive↔uniform, independent↔overlapping
  batches) did not materially resolve the semantic/topic mismatch in the tested setups.
- Pose/trajectory extraction itself is technically feasible on the 5-clip probe set
  (5/5 success, 0% missing tracking), but feeding trajectory-derived text back into a
  generic Gemini prompt produced no semantic recovery on the 5 clips tested.
- Specialized sign-language systems show stronger signal than generic Gemini prompting:
  Uni-Sign and SignCaption both meaningfully outperform the Curify/Gemini frame baseline
  on lexical metrics in every comparison run so far.
- Uni-Sign remains the strongest tested specialized baseline on most lexical metrics
  (CER, BLEU, chrF) across the matched-126, matched-15, and matched-8 comparisons.
- SignCaption beats the Curify frame baseline (all metrics, matched-15) and beats Gemini
  native-video (all metrics, matched-8) on the small manual pilot, but does not beat
  Uni-Sign overall — it wins WER only; Uni-Sign wins CER/BLEU/chrF in both pilots.
- Today's Uni-Sign inference-parameter audit confirms decoding parameters exist and are
  controllable in principle: our existing benchmark used the official, untuned defaults
  (`num_beams=4`, `max_new_tokens=100`), so a small beam-width ablation is a legitimate,
  low-cost next step before drawing conclusions about the model itself.
- The strongest remaining hypothesis, based on current evidence, is that a learned
  sign-specific temporal/linguistic representation is needed — not more generic
  frame/prompt engineering, larger beams, or textualized trajectories.
- None of the negative results above should be read as "the project failed" — they are
  the expected output of a systematic elimination process, and each one narrows the
  search space for what will actually work.

---

## 2. Project Goal

Curify's product goal is:

**ASL video → reliable sign-language understanding → accurate English caption/text.**

This body of work is currently **benchmark, evaluation, diagnosis, and architecture
exploration** — establishing what already works, what fails and why, and which direction
is best supported by evidence. It is **not yet** a project to train a new SignGemma-class
model; no training has been proposed or started. Every experiment described below is
either a frozen-benchmark evaluation of an existing system (Curify/Gemini frame baseline,
Uni-Sign, OpenSLT, SignCaption) or a small, controlled diagnostic probe (temporal
ablation, trajectory-as-context, native-video).

---

## 3. Evaluation Foundation

The center of this work is a **frozen How2Sign v2 benchmark**: 128 clips, fixed
English reference translations, a frozen manifest, and byte-verified inputs — so every
system is compared on exactly the same clips and references, and no result changes
retroactively.

Three systems have a full-benchmark corpus-level scorecard. OpenSLT and Uni-Sign both
have small coverage gaps (2 clips each, for different reasons), so the standard
comparison scope is **matched-126** — the 126 clips all three systems successfully
produced a prediction for.

| System | WER | CER | BLEU | chrF |
|---|---|---|---|---|
| Curify / Gemini 3.6 (frame baseline) | 0.9761 | 0.8070 | 0.1346 (≈0.13) | 11.3033 |
| Uni-Sign (pose-only) | 0.9801 | 0.7601 | 5.40 | 22.8262 |
| OpenSLT | 1.0246 | 0.7689 | 0.962 (independently recomputed; fairseq's own self-reported figure is 0.98) | 18.5904 |

Sources: `asl-translator/evaluation/results/how2sign_v2/curify_gemini_3_6_2026_09_04/corpus_summary_matched_126.json`,
`asl-translator/evaluation/results/how2sign_v2/unisign/matched126_summary.json`,
`asl-translator/evaluation/results/how2sign_v2/openslt/corpus_summary.json`, reconciled by
`asl-translator/evaluation/compare_how2sign_v2_systems.py` (a read-only scorecard builder
— it only reads pre-written `corpus_summary*.json`/`matched126_summary.json` files, makes
no model calls).

**Why lexical metrics alone are insufficient here:** WER/CER/BLEU/chrF measure surface
token/character overlap with the reference. On ASL translation, a system can produce
fluent, grammatical English that is completely unrelated to the signed content — WER
near 1.0 does not distinguish "close paraphrase" from "confidently describes a different
topic." This is why every system evaluation in this project pairs the lexical scorecard
with a **semantic adequacy / topic-mismatch review** (0/1/2 scale, "does the prediction's
topic match the reference at all") on a manageable subset, rather than trusting the
corpus-level numbers alone.

---

## 4. Earlier Temporal Diagnostics

Three controlled ablations were run against the Curify/Gemini frame pipeline
(`asl-translator/evaluation/diagnostics/phase1_temporal_ablation/`):

- **Adaptive ~2fps vs. adaptive ~8fps** (paired, 76 clips): corpus WER moved from 0.9730
  to 0.9715 (Δ −0.0015), median per-clip Δ = 0.0000. Flat.
- **Adaptive vs. uniform sampling** (12-clip diagnostic set): corpus WER moved from
  1.0524 to 1.0594 — slightly worse, no semantic recovery.
- **Independent vs. overlapping (sliding-window) batches** (12-clip diagnostic set):
  corpus WER moved from 1.0524 to 0.9545, but an architecturally-inert single-batch
  control arm moved by a comparable amount on its own (mean WER Δ = −0.0673) — i.e. the
  observed shift is within the run-to-run noise floor, not a real effect. All 12 clips
  stayed topic-mismatched under both arms.

**Conservative conclusion (as stated in `FINAL_TEMPORAL_DIAGNOSIS.md`):** simple
frame-density and sampling changes did **not** materially resolve the semantic/topic
mismatch in the tested setups. This is **not** a claim that temporal information is
useless — only that these particular, simple manipulations of the existing
generic-Gemini pipeline didn't move the needle.

---

## 5. Diagnostic Inspector + Uni-Sign Integration

`asl-translator/evaluation/diagnostics/phase1_temporal_ablation/inspector/` (built by
`build_inspector.py`) is a static, read-only HTML inspector covering the 12-clip
diagnostic set. Each case page shows, side by side:

- Reference translation
- Curify/Gemini frame-baseline prediction
- Uni-Sign prediction
- Gemini native-video status/prediction (or an explicit "Unavailable — Gemini Files API
  processing failed before inference" label where the call never completed)
- Trajectory visualization, where available

It recomputes only the frame sampler locally to render diffs — it makes no model calls.
Word-level diffs and per-system WER/CER are shown per clip, which makes it possible to
see *how* each system fails (fabrication, omission, repetition, truncation) rather than
only *that* it fails, which is exactly the qualitative signal a single corpus-level
number can't provide.

**Status: COMPLETE.**

---

## 6. Gemini Native-Video Experiment

The native-video experiment (`asl-translator/asl-eval/run_native_video.py`,
`asl-translator/evaluation/run_native_video_how2sign_v2_benchmark.py`) uploads each
clip's whole `.mp4` via the Gemini Files API and makes **one model call per clip** (vs.
the frame-sampled pipeline's multi-frame-batch approach), using a prompt adapted from the
production frame prompt for native-video input. The harness is resumable (skips
already-scored clips on rerun), cleans up uploaded files after each call, and explicitly
acknowledges/logs that clip content is being uploaded to a third-party API before any
call is made.

**A real parser bug was found and fixed during this work:** Gemini's native-video
response for one clip came back as a top-level JSON array instead of the expected
`{"segments": [...]}` object, which the original parser did not handle
(`AttributeError: 'list' object has no attribute 'get'`). This was exposed by clip
`G05uFub3YFc_9-2-rgb_front` ("G05"), diagnosed from call timing (a genuine ~16.6s
inference call, not the ~3s pattern of a Files-API failure), fixed in
`parse_segments_response` to accept either shape, and validated end-to-end on a live
retry (`model_calls=1`, `inference_wall_clock_s≈17.5`, `status=success`).

**Current state** (`docs/daily_report/9.10/asl-native-video-evaluation/BLOCKER_STATUS.md`,
unchanged since 2026-09-10):
- **5/12** diagnostic clips valid and scored: `FzmL8SL6Bow_1-8-rgb_front` (WER 1.0000),
  `-g0sqksgyc4_3-2-rgb_front` (1.0000), `92V3oH63zbQ_5-1-rgb_front` (1.0000),
  `fzNnTgHa1lM_2-5-rgb_front` (0.9118), `G05uFub3YFc_9-2-rgb_front` (0.9412).
- **7/12** still blocked at the Gemini Files API before inference ever runs; root cause
  (transient service issue vs. clip-specific) is unresolved, and the same 7 clip IDs
  failed on both attempts.
- **0/5 genuine semantic recoveries** among the 5 scored clips.
- The manager's §7 P0-4 12-case promotion/rejection gate (promote on ≥3/12 flips, reject
  on 0/12 flips with WER inside the noise floor) **remains inconclusive** at 5/12 — there
  is no valid answer yet, not a negative one.

**Worked example — G05:**

| | Content |
|---|---|
| Reference | Breathing-exercise instructions |
| Frame baseline | Hallucinates cloth / gear / fire |
| Native video | Hallucinates fear / "heart was pounding" |
| WER | 1.0294 → 0.9412 (numerically improved) |
| Semantic adequacy | 0 → 0 (unchanged) |
| Topic mismatch | yes → yes (unchanged) |

**Key point: metric movement ≠ semantic recovery.** The WER improvement here comes from
surface token overlap, not from the model getting closer to the actual signed content —
both predictions fabricate an unrelated topic.

**Status: PARTIAL / INFRASTRUCTURE-BLOCKED.**

---

## 7. Trajectory-Tracking Direction

### D0 — Research / feasibility

Motivated by whether an explicit, structured skeletal-trajectory signal (in the spirit of
sports-analytics pose tracking) could give a generic Gemini prompt something more
concrete to reason over than raw video frames. This is new to *this evaluation
pipeline*, not new to the project overall — Uni-Sign's own architecture already runs an
RTMPose-based pose extractor internally.

### D1 — Pose / trajectory extraction

Verified results on a 5-clip probe set
(`docs/daily_report/9.10/trajectory-tracking-feasibility/PHASE_D1_RESULTS.md`):
- **5/5 clips succeeded**, no failures, no retries needed.
- **1,038 total frames** extracted (~38s of video), 62.2s total wall-clock.
- **0% missing tracking** on body, left hand, and right hand, on every one of the 5 clips.
- **0 multi-person frames.**
- Visual skeleton/finger QA passed on 4/5 clips (plan required ≥2 to pass).
- One weaker case: `-g0iPSnQt6w_0-1-rgb_front` had lower left-hand mean confidence
  (0.579) vs. right-hand (0.877), though still 100% above the detection threshold.

**Conclusion: tracking itself is technically feasible on this small probe set.** This
should **not** be extrapolated to all 128 clips — it is 5/128, chosen as a diagnostic
probe, not a random or representative sample.

### D2 — Trajectory-as-context to Gemini

A controlled experiment: the same Gemini frame pipeline, with trajectory-derived
structured observations added as extra text context, tested on the same 5 probe clips
(`PHASE_D2_RESULTS.md`).

**Result: 0/5 semantic-adequacy recoveries, 0/5 topic-mismatch recoveries, no genuine
semantic recovery on any clip.** Example: `FzmL8SL6Bow` moved BLEU 0.2719→0.5051 and
chrF 11.1616→14.3380 with WER byte-identical at 0.9615 — the model restated the same
fabricated content in more words; this was not counted as an improvement.

**Conclusion (quoted):** "trajectory-as-structured-text-context to a generic Gemini model
should be deprioritized." This does **not** conclude that pose/trajectory is useless for
ASL — the remaining, still-open hypothesis is a **learned, sign-specific temporal
representation** that models hands/fingers, handshape, orientation, body, face, motion,
and non-manual markers jointly and end-to-end, rather than handing a text summary of
trajectory to a generic multimodal LLM.

---

## 8. SignCaption / Sign-Speak Investigation

### 8.1 API / ToS research

Public/local research on SignCaption (vendor: Sign-Speak) is complete
(`docs/daily_report/9.10/signcaption-signspeak-research/CHECKLIST.md`). Still unresolved:
API credentials, endpoint/schema, auth, pricing, rate limits, and — the load-bearing
issue — **benchmark/competitive-product permission**. Sign-Speak's own ToS explicitly
bars using the service "to create a competitive product," prior outreach to
`management@sign-speak.com` went unanswered, and no written clearance has been obtained.
This repository being private does **not** resolve that use-permission question — ToS
compliance is about what the data/service may be used for, not who can see the repo.

Because of this, **raw Batch-2 vendor SRT exports remain local/untracked** (confirmed via
current `git status --short`) and are not treated as committed deliverables anywhere in
this report.

### 8.2 Original 5-clip manual pilot

An initial 5-clip manual pilot (`docs/daily_report/9.11/signcaption-manual-pilot/`,
scored 2026-09-12) compared SignCaption against Uni-Sign on 5 hand-collected clips.
Official corpus-level result (§3b): **Uni-Sign beat SignCaption on all 4 metrics** at
this small n=5 —Uni-Sign WER 0.9064 / CER 0.6845 / BLEU 3.15 / chrF 20.85 vs. SignCaption
WER 0.9240 / CER 0.7686 / BLEU 1.97 / chrF 15.91.

**BLEU rounding correction (kept separate and accurate):** the original RESULTS.md §3b
reported SignCaption's corpus BLEU as 1.98. An independent recalculation
(`docs/daily_report/9.13/signcaption-calculation-audit/CALCULATION_AUDIT.md`, built with
a fresh SRT parser/normalizer/Levenshtein implementation and direct `sacrebleu` calls,
deliberately not reusing the original `score_pilot.py`) found the true value rounds to
**1.97** — a manual double-rounding mistake, with no other number or ranking affected.
Fixed via commit `a66a222`.

This 5-clip pilot's numbers are **not** mixed into the official 128-clip matched-126
scorecard in §3 above — they are reported here as their own, separate, much smaller
result.

### 8.3 Batch-2 10-clip expansion

10 new How2Sign v2 clips were manually uploaded to the SignCaption website (no API, no
automation, no model call) and their exported captions saved byte-for-byte, SHA-256
verified. The Batch-2 scorer
(`asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/score_batch2_and_combined.py`)
uses the same canonical WER/CER/BLEU/chrF implementation as the frozen 128-clip
benchmark, so Batch-2's numbers are on the same footing as everything else in this
report.

Combined with the original 5, this gives **15 clips total**. Native-video overlap across
these 15 is **8/15**, not 5/15 — this was an earlier miscount (undercounting the original
5, which already had native-video coverage) that was corrected before any Batch-2
artifact was created; see `docs/daily_report/9.13/signcaption-batch2-manual-pilot/README.md`.

This 15-clip selection is **small and stratified, not random**, and should not be read
as representative of the full 128-clip benchmark.

---

## 9. SignCaption Comparative Results

### Matched-15

| System | WER | CER | BLEU | chrF |
|---|---|---|---|---|
| Curify (frame baseline) | 0.9978 | 0.8637 | 0.548 | 12.6151 |
| Uni-Sign | 0.9332 | 0.7217 | 5.0763 | 20.6589 |
| SignCaption | 0.9109 | 0.7631 | 1.4654 | 16.5482 |

**Interpretation:** SignCaption beats the Curify frame baseline on all four lexical
metrics. SignCaption does **not** beat Uni-Sign overall — it wins WER; Uni-Sign wins
CER, BLEU, and chrF, by a clear margin on the latter two.

### Matched-8 (native-video overlap)

| System | WER | CER | BLEU | chrF |
|---|---|---|---|---|
| Curify (frame baseline) | 1.0388 | 0.9003 | 0.9038 | 14.0855 |
| Uni-Sign | 0.9181 | 0.6812 | 2.5923 | 19.5469 |
| Gemini native-video | 0.9784 | 0.8486 | 0.1868 | 7.467 |
| SignCaption | 0.8922 | 0.7596 | 1.9084 | 16.3896 |

**Interpretation:** SignCaption beats Gemini native-video on all four metrics on these 8
clips. Uni-Sign still leads SignCaption on CER, BLEU, and chrF. This is evidence that
specialized sign-language systems show stronger signal than generic Gemini prompting on
this small pilot — it is **not** evidence of universal superiority or of how any system
would perform across the full 128-clip benchmark.

---

## 10. SignCaption Semantic Review

**Provenance matters here and is mixed — reported exactly, not smoothed over.**

The Batch-2 text-only semantic review (`semantic_review_batch2.csv`) was performed by
Claude, comparing English reference text against English SignCaption prediction text
only — **no ASL video was watched**, and this is explicitly not a fluent-ASL human
annotation. It is persisted separately from the original 5-clip review.

- **Batch-2 only (n=10):** adequacy 0 = 3, adequacy 1 = 5, adequacy 2 = 2 (30% clear
  topic mismatch).
- **Combined-15:** adequacy 0 = 6, adequacy 1 = 6, adequacy 2 = 3 (40% clear topic
  mismatch).

**The combined-15 figure mixes two different review processes and should not be
presented as one controlled human annotation pass:** the original-5 values come from the
9.11 pilot's own review (documented in `docs/daily_report/9.13/.../README.md` as "the
human pilot operator's own judgment"), while the Batch-2 values are Claude's single-pass
text-only review, done separately, not by the same reviewer or in the same sitting. Note
for anyone drilling into this further: the 9.11 RESULTS.md §5 review itself reads in the
first person ("my assessment"), so whether the "original-5" review is meaningfully
distinct from an LLM-assisted read is itself not fully resolved — flagged as an open
question in §15 below, not resolved by asserting either way here.

---

## 11. Latest Manager Follow-Up — Uni-Sign Prediction Parameters

Manager question: *"Uni-Sign prediction 这个模型在调用时 有参数 可以控制吗?"*
("Does this model have parameters that can be controlled at call time?")

### 11.1 Short answer

**Yes.**

The current Uni-Sign wrapper (`models.py::Uni_Sign.generate()`) directly wires exactly
two decoding parameters through to the underlying mT5 model:
- `num_beams`
- `max_new_tokens`

At both official call sites (`demo/online_inference.py:125-127` and
`fine_tuning.py:263-265`), these are **hardcoded literal values** —
`num_beams=4, max_new_tokens=100` — not command-line flags. Uni-Sign's complete argparse
definition (`utils.get_args_parser()`) has no `--num_beams` or `--max_new_tokens` flag at
all, so changing them today means editing the literal in the source file, not passing a
flag.

The underlying mT5 model (`MT5ForConditionalGeneration.generate()`) supports many more
decoding controls — `length_penalty`, `repetition_penalty`, `no_repeat_ngram_size`,
`early_stopping`, `do_sample`, `temperature`, `top_p`, `top_k` — but Uni-Sign's own
`generate()` wrapper does not forward any of them; they silently fall back to the
`transformers` library's defaults (effectively off: no repetition penalty, no n-gram
blocking, deterministic beam search). **Changing any of these would require a code
change to the wrapper**, not just varying an existing argument.

### 11.2 Our actual benchmark configuration

Verified from our own committed run provenance (`run_metadata.json`, `raw_output.txt`):

- Checkpoint: `how2sign_pose_only_slt.pth`
- Mode: pose-only (`rgb_support=False`)
- `num_beams=4`, `max_new_tokens=100`
- `seed=42` (argparse **default**, never deliberately overridden)
- Pose extractor: `rtmlib` `Wholebody` (RTMPose, 133 keypoints), **every video frame
  processed, no stride/subsampling** in extraction itself
- Input cap: `max_length=256` pose frames — clips whose pose sequence exceeds 256 frames
  are randomly subsampled down to 256, seeded by the same global `seed=42`

**Our current Uni-Sign benchmark matches the upstream default generation settings; we
did not tune beam width or output length at any point, on any clip.**

### 11.3 What could affect prediction?

| Category | Factors | Decoding-fixable? |
|---|---|---|
| Decoding / search | `num_beams`, `max_new_tokens`, repetition behavior (no penalty/n-gram blocking currently active) | Plausibly, for beam width and length; needs a code change for repetition controls |
| Input / preprocessing | pose-only vs. RGB+pose (`rgb_support`), checkpoint choice, the 256-frame input cap and its random subsampling, the pose extractor itself | No — decoding parameters can't touch this |
| Model / checkpoint | Learned language/sign representation, topic fabrication, semantic fit to our clip pool | No |

**No causal claim is made here.** The repetition-loop failure mode observed on our
one-clip pilot (a clause repeated 4x near-verbatim) is *consistent with* the decoding
config having no repetition suppression, but that is not the same as proving decoding is
the cause of our benchmark's overall low scores.

### 11.4 Proposed minimal ablation (NOT run)

| Arm | `num_beams` | `max_new_tokens` | Notes |
|---|---|---|---|
| U0 (baseline) | 4 | 100 | Reuse the frozen `unisign_predictions.jsonl` verbatim — exact-provenance match, no new inference needed |
| U1 | 1 | 100 | Requires new inference |
| U2 | 8 | 100 | Requires new inference |

Use the existing frozen diagnostic-12 subset (all 12 clips already confirmed present in
`unisign_predictions.jsonl`, so U0 needs no new run). Keep checkpoint, pose/RGB mode,
preprocessing, references, scorer, and clip set identical across arms — only
`num_beams` changes. Metrics to compare, if/when run: WER, CER, BLEU, chrF, output
length, empty-prediction rate, repetition/degeneration, and semantic adequacy/topic
mismatch where the existing review process already supports it.

**Conservative decision rule:** only proceed into `max_new_tokens`/repetition-control
experiments if beam width alone shows a meaningful signal on this 12-clip set.
Separately, flag that the 256-frame input cap and its random subsampling may deserve its
own input-side ablation later — that is a distinct experiment from the beam-width
question and should not be run or interpreted together with it.

---

## 12. What Worked

- A reproducible, frozen 128-clip benchmark with byte-verified inputs and matched
  cross-system scorecards.
- A working matched-126 comparison across Curify/Gemini frame baseline, Uni-Sign, and
  OpenSLT.
- A complete 12-clip diagnostic inspector integrating reference, Curify frame, Uni-Sign,
  and Gemini native-video side by side.
- Full Uni-Sign integration into the evaluation and diagnostic tooling.
- Native-video benchmark infrastructure (resumable, Files-API-aware, cleanup-safe) with a
  real parser bug discovered and fixed end-to-end.
- Pose/trajectory extraction shown technically viable on the 5-clip probe set (5/5,
  0% missing tracking).
- A clean negative result on trajectory-as-text-context to generic Gemini, tested and
  properly deprioritized rather than left ambiguous.
- SignCaption manual comparison expanded from 5 to 15 clips, with corrected metrics and a
  documented provenance trail.
- SignCaption shown to beat the generic Gemini/Curify baseline and Gemini native-video on
  the small matched pilot.
- A concrete Uni-Sign parameter/provenance audit identifying exactly which decoding
  knobs are controllable today and which require code changes.
- A clearer working distinction, across every experiment above, between infrastructure
  problems, decoding/search problems, input/preprocessing problems, and
  model/representation problems.

---

## 13. What Did Not Produce a Breakthrough

- Higher frame density (2fps → 8fps).
- Alternate sampling (adaptive vs. uniform).
- Overlap/sliding-window batching (effect indistinguishable from noise).
- Native video, on the clips scored so far (0/5 genuine semantic recoveries; 7/12 still
  blocked, so this remains an open question, not a closed negative).
- Trajectory-as-text-context to a generic Gemini prompt (0/5 recoveries).

None of these results should be read as universal — each was tested in one specific,
narrow setup, and each narrows (rather than closes) the space of remaining hypotheses.

---

## 14. Main Technical Finding

The accumulated evidence suggests the main bottleneck is unlikely to be solved only by:
more frames, simple sampling changes, broader beam search, generic multimodal prompting,
or textualized trajectories. The stronger remaining hypothesis is that **a learned,
sign-specific temporal/linguistic representation** — one that jointly models hands,
fingers, handshape, orientation, body, face, motion, and non-manual markers over time —
is what's actually missing from the generic-Gemini approaches tested so far.

**However**, this is a hypothesis supported by current evidence, not a proven
conclusion. Uni-Sign's own local results are markedly weaker than what its published
literature reports, and that gap has not yet been explained. Decoding configuration,
checkpoint choice, pose-only vs. RGB+pose mode, and the 256-frame input cap all remain
open, controlled-investigation questions that should be resolved (starting with the
minimal beam-width ablation in §11.4) before drawing a final architecture conclusion.

---

## 15. Current Blockers / Open Questions

- 7/12 Gemini native-video diagnostic clips remain blocked at the Files API stage;
  root cause (transient vs. clip-specific) unresolved.
- SignCaption vendor/API/ToS benchmark permission remains unresolved — no written
  clearance from Sign-Speak, and their ToS explicitly bars competitive-product use.
- No fluent-ASL expert has performed semantic review across the benchmark; all existing
  semantic-adequacy scoring (native-video, trajectory D2, SignCaption Batch-2) is
  text-only or single-reviewer, not independently verified ASL-fluent annotation.
- The provenance of the *original-5* SignCaption semantic review (human pilot operator
  vs. LLM-assisted first-person narration in 9.11 RESULTS.md §5) is not fully resolved —
  see §10.
- A full Uni-Sign inference environment (conda env, pinned repo checkout, checkpoint,
  mT5-base weights) no longer exists on this machine and would need to be rebuilt before
  the U1/U2 beam-width ablation could actually run.
- The Uni-Sign 256-frame pose-sequence cap and its random subsampling may materially
  affect longer clips and has not been separately investigated.
- Our local Uni-Sign metrics remain far below what its published research reports —
  whether this is a protocol, checkpoint, or configuration mismatch is still an open
  question, not yet attributed to any single cause.

---

## 16. Recommended Next Steps

1. Do not spend further time tuning generic Gemini prompts/frame sampling — the evidence
   from §4, §6, and §7 consistently shows this doesn't move semantic adequacy.
2. Run the minimal Uni-Sign beam-width ablation (U0/U1/U2, `num_beams` 1/4/8) on the
   diagnostic-12 subset described in §11.4.
3. If beam width shows no meaningful effect, investigate Uni-Sign's input-side factors
   next: the 256-frame cap/subsampling, pose-only vs. RGB+pose mode, and checkpoint/
   protocol fidelity against the published literature.
4. If SignCaption vendor permission is resolved, expand the specialized-system
   evaluation carefully and incrementally, keeping the same frozen-benchmark discipline
   used throughout this work.
5. Preserve the frozen benchmark and diagnostic inspector as the standing decision
   framework for any future system comparison.
6. If the trajectory direction continues, move toward a learned, sign-specific temporal
   model rather than any further trajectory-to-text-prompt approach.

Training a large new model is **not** recommended at this time — current evidence points
at needing a better-suited architecture/representation, not yet at needing more
scale, and the Uni-Sign audit shows there are still cheap, un-run configuration
experiments to exhaust first.

---

## 17. Deliverables / Git History

Recent commits on this branch (`baobao/asl-temporal-ablation-2026-09-06`, current HEAD
`fdc2872`):

```
fdc2872 eval(asl): add SignCaption Batch-2 manual pilot
a66a222 docs(asl): correct SignCaption pilot BLEU rounding
e21284f eval(asl): add SignCaption manual pilot
c360b8d docs(asl): add work report and manager summary
01cfd05 eval(asl): add native-video and trajectory diagnostics
4d23017 docs(asl): summarize evaluation-driven improvement work
22bb867 eval(asl): diagnose temporal architecture failures
```

No pull request exists for this branch (`gh pr list --head
baobao/asl-temporal-ablation-2026-09-06 --state all` returns empty).

Committed-file links, pinned to current HEAD (`fdc2872`) on
`https://github.com/super-inbox/visual-search-adhoc`:

- Diagnostic inspector: https://github.com/super-inbox/visual-search-adhoc/blob/fdc2872/asl-translator/evaluation/diagnostics/phase1_temporal_ablation/inspector/build_inspector.py
- Native-video blocker status: https://github.com/super-inbox/visual-search-adhoc/blob/fdc2872/docs/daily_report/9.10/asl-native-video-evaluation/BLOCKER_STATUS.md
- Trajectory manager summary: https://github.com/super-inbox/visual-search-adhoc/blob/fdc2872/docs/daily_report/9.10/trajectory-tracking-feasibility/MANAGER_SUMMARY.md
- 9.11 work report: https://github.com/super-inbox/visual-search-adhoc/blob/fdc2872/docs/daily_report/9.11/ASL_WORK_REPORT.md
- SignCaption Batch-2 RESULTS: https://github.com/super-inbox/visual-search-adhoc/blob/fdc2872/docs/daily_report/9.13/signcaption-batch2-manual-pilot/RESULTS.md
- Matched-15 CSV: https://github.com/super-inbox/visual-search-adhoc/blob/fdc2872/docs/daily_report/9.13/signcaption-batch2-manual-pilot/combined_15clip_comparison.csv
- Matched-8 CSV: https://github.com/super-inbox/visual-search-adhoc/blob/fdc2872/docs/daily_report/9.13/signcaption-batch2-manual-pilot/overlap_8clip_comparison.csv

**Uni-Sign inference-parameter audit** (`docs/daily_report/9.15/unisign-inference-parameter-audit/README.md`)
is **not yet committed** as of this report — it exists only locally
(`?? docs/daily_report/9.15/` in `git status`). No GitHub link is given for it here per
instructions not to invent a link for an uncommitted file; it will be linkable once
staged, committed, and pushed.

---

## 18. Final Status Table

| Area | Status |
|---|---|
| Evaluation foundation | COMPLETE |
| Uni-Sign inspector | COMPLETE |
| Temporal ablations | COMPLETE |
| Gemini native-video | PARTIAL / INFRASTRUCTURE-BLOCKED |
| Trajectory POC | COMPLETE / NEGATIVE D2 |
| SignCaption API research | RESEARCH COMPLETE / ACCESS PENDING |
| SignCaption 15-clip manual pilot | COMPLETE |
| Uni-Sign inference parameter audit | COMPLETE |
| Uni-Sign beam-width ablation | NOT RUN YET |

---

## 19. One-Paragraph Manager Takeaway

We now have enough evidence to separate several failure modes. Generic Gemini-based
approaches remain weak semantically even after frame-density, sampling, native-video,
and trajectory-context experiments. Specialized sign-language systems show stronger
signal: SignCaption beats Curify/Gemini on the small matched pilot, while Uni-Sign
remains stronger on most lexical metrics. The latest Uni-Sign audit also confirms that
prediction decoding parameters are controllable and that our benchmark used untuned
official defaults, so a small beam-width ablation is a low-cost next step before blaming
the model architecture itself. Longer-term, the evidence increasingly favors
sign-specific temporal/linguistic representations rather than further generic prompt
engineering.
