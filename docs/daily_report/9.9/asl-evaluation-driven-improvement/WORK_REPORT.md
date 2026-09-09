# ASL Temporal Architecture Diagnosis — Work Report

**Date:** 2026-09-09
**Branch:** `baobao/asl-temporal-ablation-2026-09-06`
**Delivered commit:** `22bb867dd080eab8b68b4962200ea5c217c4071f`
**Primary artifact directory:** `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/`

**Document status:** Documentation only. No Gemini/API call was made, no
experimental result was modified, and no code was changed to produce this
report. Every number below is read from an already-committed artifact; the
source file is cited next to each claim. Where a statement is an
interpretation rather than a measurement, it is labeled **Interpretation**;
where something remains unknown, it is labeled **Limitation / Not
established**.

---

## 0. Purpose of this report

This report consolidates all ASL work performed since the manager's original
requirements (Sections A–C below) through the temporal-architecture diagnosis
and the subsequent gap analysis against a shared "evaluation-driven
self-improvement" ASL pipeline. It is written so the manager can see, in one
place: what was asked, what was done, what the numbers were, what hypotheses
were rejected, what remains open, and what the smallest defensible next step
is.

---

## 1. Manager's original requirements (starting point)

### A. Concrete case analysis

Manager asked to look at specific examples rather than only aggregate WER
("有像我上次一样 看几个例子吗？分析具体的例子"), and referenced an existing
private-corpus frame inspector at
`curify-studio/dev/asl_mvp/inspector/asl-1252-frame-inspector.html` as the
format to work from. **Note:** that exact file lives outside this repository
(it is not present in this worktree) — the diagnostic team instead built a
new, generalized frame inspector for the frozen How2Sign v2 benchmark
(`inspector/build_inspector.py`), matching the manager's stated intent
(frame-by-frame inspection of representative failures) rather than reusing
the literal file.

### B. P0-2 — Test whether temporal information fixes the architecture

Manager's framing: "Don't jump to training a model yet. Your current 2 fps /
independent 24-frame batches are such obvious bottlenecks that they deserve
controlled ablations first." Requested ideas: 2 fps → 5/10 fps or direct
video input; independent batches → overlapping/sliding windows with context;
preserve temporal ordering; do not optimize sampling around motion peaks.

Research question posed: **"Does giving Gemini materially better temporal
evidence move WER / semantic accuracy?"** Interpretation thresholds
suggested: ~0.92→0.85 not very interesting; ~1.0→0.6–0.7 potentially worth
engineering. Manager also raised the Gemini spend limit, but asked not to
simply finish every remaining benchmark run — instead focus on
representative/typical examples, categorize clips if possible, inspect where
2fps/frame-based input fails, and test whether higher frame rate / better
temporal evidence solves specific failures.

### C. P0-3 — Build a small qualitative error taxonomy

Manager requested ~30–50 benchmark clips with candidate failure categories:
handshape, motion, fingerspelling, numbers, facial & non-manual markers,
segmentation, hallucinated topic, repetition, correct-meaning-different-English.
Manager explicitly flagged: **"WER alone is particularly misleading here
because all systems can produce fluent hallucinations,"** and asked to track
semantic adequacy and hallucination rate specifically, to determine whether
the next intervention belongs in vision, temporal modeling, decoding, or
post-processing.

### Later follow-up — shared "evaluation-driven self-improvement" conversation

After the temporal diagnosis was delivered, the manager shared a ChatGPT
conversation
(`https://chatgpt.com/share/6aa01bf5-adac-83ee-a24e-54c22ef8a849`) and asked
whether its proposed ASL pipeline could help ("这个 GPT 的会话里有 ASL 的
pipeline 看是否对提升效果有帮助"). That conversation's ASL-relevant content is
summarized in Section 9 and analyzed against our completed work in Section
10.

---

## 2. Benchmark / baseline status

**Measured** (`TASK0_baseline_denominator.md`, `MANAGER_SUMMARY.md`):

- The frozen How2Sign v2 benchmark contains **128 clips**.
- Curify/Gemini 3.6 has **128/128** successful predictions on this benchmark
  (`curify_gemini_3_6_2026_09_04/corpus_summary.json`: `n_total=128,
  n_success=128, n_failure=0`). Nothing is missing on the Curify side.
- **Baseline corpus WER: 0.9762** (128-clip denominator).

**Why "128" and "matched 126" both appear:** a second file,
`corpus_summary_matched_126.json`, restricts the comparison to the 126-clip
intersection where OpenSLT and Uni-Sign *also* have usable predictions.
OpenSLT failed on 2 clips (`G3EfBFwsOpE_3-10-rgb_front`,
`fZK9hW81XCU_9-10-rgb_front`); Uni-Sign failed on 0. **This is a cross-model
comparability restriction, not a Curify shortfall** — Curify's own corpus WER
is nearly identical on both denominators (0.9762 on 128, 0.9761 on the
matched 126). Rule going forward: use the 128-clip file for any Curify-only
analysis (all diagnostics in this report use it); use the matched-126 file
only when citing OpenSLT/Uni-Sign numbers side by side with Curify's.

---

## 3. Architecture investigation

**Measured, by reading `asl-eval/run_current_model.py` directly**
(`PHASE1_SUMMARY.md` §1–3):

The current pipeline is **not** simple fixed-rate 0.5s-interval sampling.
The actual mechanism:

1. `TARGET_FRAMES_PER_SEC = 2.0` sets a **total frame budget** for the clip:
   `budget_for_duration()` = `round(duration_s * 2.0)`, clamped to
   `[MIN_FRAME_BUDGET=24, MAX_FRAME_BUDGET=240]`.
2. That budget is spent **non-uniformly**: a motion probe
   (`probe_motion`, 4 fps grayscale whole-frame pixel-diff) is segmented into
   active/idle runs (`segment_runs`), and `allocate_timestamps()` gives each
   active run a share of the budget proportional to its motion energy.
   High-motion stretches get many frames; static stretches get few or none.
3. Frames are extracted as chronologically-ordered JPEGs and sent to Gemini
   in **independent, non-overlapping `BATCH_SIZE=24`-frame batches** — each
   batch is a fresh, single-turn `generate_content` call with no conversation
   history, no prior segments, and no prior frames passed between batches
   (confirmed by direct code reading of `run_real()`). The only cross-batch
   step is a client-side, text-only `merge_adjacent_duplicates()` applied
   *after* all batches have already returned independently.
4. Because of the `MIN_FRAME_BUDGET=24` floor, **"2 fps" is not literally
   true for short clips** — e.g. a 1.5s clip still samples 24 frames, i.e.
   16 fps — so density claims must be read per-clip, not as a flat rate.

**Interpretation — why this changed how the manager's original hypothesis had
to be read:** the manager's ablation request explicitly asked to preserve
temporal order and *not* optimize sampling around motion peaks. But the
existing production/baseline path already does the opposite: it is a
motion-peak-adaptive sampler, not a naive fixed-rate one. This meant a
"uniform 5/10 fps" experiment would change **two** things at once (density
*and* allocation strategy) unless sampling strategy and frame density were
deliberately separated into two different ablation arms. This observation
directly shaped the three-arm experiment design in Sections 6–8.

---

## 4. Representative diagnostic cases / frame inspector

This directly addresses manager request (A) — "看几个具体例子" — by building
a deterministic, reusable set of representative clips with frame-by-frame
inspection, rather than ad hoc example-pulling.

**12-clip diagnostic subset** (`select_12_diagnostic_clips.py`,
`diagnostic_12_clips.json/.csv`, `PHASE1_SUMMARY.md` §4): selected
deterministically from the full 128-clip baseline results, six categories, 2
clips each (overlap allowed) — long/multi-batch, fingerspelling-candidate +
very-high-WER, number-token, fast-signing/question, very-high-WER, and
low-WER contrast. This set is reused unchanged across every later ablation
(Sections 6–8) for continuity.

**Frame inspector** (`inspector/build_inspector.py`, one HTML page per clip
plus `index.html`): for each of the 12 clips, shows the actual sampled
timestamps, extracted frames, the motion trace used to derive them, batch
boundaries (flagging any model output segment whose nearest frame sits within
1 frame of a batch seam — "near_batch_seam"), and a reference-vs-prediction
word diff. **Validation performed:** for every clip, re-deriving sampling
(`probe_motion → segment_runs → allocate_timestamps`) reproduced the exact
`frames_sampled` count recorded in that clip's saved baseline prediction
(0 mismatches across 12 clips) — confirming the inspector shows the actual
frames the real run used, not an approximation.

**Observation** (`PHASE1_SUMMARY.md` §1): frames cluster where the signer is
moving fastest — this is a measured property of the sampler, not an
inference. **Hypothesis / risk, not yet measured:** fast-motion intervals may
also be a comparatively poor place for a still image to carry legible
handshape, since fast transitions can blur — this is a plausible risk worth
checking against the frame inspectors, not a conclusion this diagnosis has
verified. Multi-batch clips in the set
(`FzmL8SL6Bow_1-8-rgb_front`, `fzNnTgHa1lM_2-5-rgb_front`,
`fZM3IcM2Xs4_14_15_16-10-rgb_front`, `G05uFub3YFc_9-2-rgb_front`) show real
candidate batch-seam-crossing cases available for frame-by-frame review.

---

## 5. 40-clip qualitative / semantic diagnostic set

**Construction** (`select_40_taxonomy_clips.py`, `taxonomy_40_clips.json/.csv`,
`PHASE1_SUMMARY.md` §5): the 12 diagnostic clips above, unconditionally
included, plus 28 more chosen by manifest heuristic category quotas (number
token: 6, proper-noun/fingerspelling: 6, fast signing: 4, question: 4,
15–31s duration: 3, <2s duration: 2, no-heuristic-tag control: 3 — 28/28
filled exactly), ranked alphabetically within category (not WER-ranked, so
this expansion adds coverage, not additional worst-case bias).

**Important distinction — machine hints vs. confirmed ASL labels**
(`PHASE1_SUMMARY.md` §6, `HUMAN_REVIEW_GUIDE.md`): the `hint_*` columns
(number_token, fingerspelling_candidate, fast_signing, question) are
manifest text heuristics computed from the **English reference translation**
— they are hints for a reviewer, not confirmed visual content. All
ASL-specific visual tags (`content__handshape_sensitive`, `content__motion`,
`content__fingerspelling`, `failure__handshape`, `failure__motion`,
`failure__segmentation`, `failure__facial_non_manual`, etc.) were left
**entirely blank**, per instruction not to auto-invent labels — they require
an ASL-fluent reviewer, which this diagnosis explicitly does not have.

**Reviewer limitation, stated explicitly:** because the reviewer performing
the text-based pass is not ASL-fluent, this diagnosis does **not** claim to
have verified handshape failure, motion failure, true fingerspelling visual
failure, facial/non-manual failure, or visually-grounded hallucination.
Instead, an explicitly-labeled **"LLM-assisted text semantic review"**
(`TEXT_SEMANTIC_REVIEW_SUMMARY.md`, method label
`claude_code_text_semantic_review`, scope
`english_reference_vs_prediction_only`) was performed by reading only two
English strings per clip — the ground-truth reference and the Gemini
prediction — with no video watched and no ASL expertise applied.

**Measured results** (`TEXT_SEMANTIC_REVIEW_SUMMARY.md`, `FINAL_TEMPORAL_DIAGNOSIS.md` §B):

| metric | value |
|---|---|
| clips reviewed | 40 / 40 |
| semantic_adequacy = 2 (core meaning correct) | 0 / 40 (0%) |
| semantic_adequacy = 1 (partial) | 3 / 40 (7.5%) |
| semantic_adequacy = 0 (wrong/unrelated) | 37 / 40 (92.5%) |
| reference_topic_mismatch = yes | 36 / 40 (90%) |
| correct_meaning_different_english = yes | 0 / 40 (0%) |
| obvious text-level repetition | 0 / 40 (0%) |

**Interpretation:** the dominant failure is a **meaning/topic-level**
failure, not WER penalizing a correct-but-differently-worded paraphrase — the
0/40 rate on "correct meaning, different English" rules out the "good
translation penalized by raw WER" hypothesis for this baseline. Secondary,
rarer patterns observed: occasional fabricated specifics not present in the
reference (an invented number sequence, an invented birthplace, an invented
name), and a small number of empty/near-empty outputs. No text-level
repetition was observed anywhere in the sample.

---

## 6. Frame-density experiment (adaptive ~2fps vs. adaptive ~8fps)

**Design:** same sampling strategy (motion-weighted/adaptive), same batching
(independent 24-frame), same model/prompt — only `target_frames_per_sec`
differs (2.0 vs. 8.0). Paired on the **identical 76-clip subset**
(`PAIRED_76_PRELIMINARY_ANALYSIS.md`), because Experiment B (8fps) only
completed 76/128 clips before hitting an external Gemini monthly billing cap
(`docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md`) — not a
code defect.

**Measured results:**

| metric | 2 fps | 8 fps |
|---|---|---|
| corpus WER | 0.9730 | 0.9715 |

- Absolute corpus WER delta: **-0.0015**
- 15 improved / 20 worsened / 41 unchanged (of 76)
- Median per-clip delta: **0.0000**

**Interpretation:** essentially flat. Raising the current adaptive sampler's
frame budget ~4x did not materially move the benchmark.

**Limitation / confounds** (`PAIRED_76_PRELIMINARY_ANALYSIS.md`, stated
conservatively): (1) both configs use the same motion-weighted allocation —
this measures "more frames under the same motion-weighted rule," not
"denser uniform sampling"; (2) a fixed 24-frame batch spans different amounts
of video time at different target fps (~12s at 2fps vs. ~3s at 8fps), so any
delta conflates density with shorter, more self-contained call windows; (3)
76/128 is a manifest-order prefix, not a random sample — no claim generalizes
to the full 128 without the remaining 52 clips.

---

## 7. Sampling-strategy controlled experiment (adaptive 2fps vs. uniform 2fps)

**Design** (`controlled_ablation/adaptive_vs_uniform_2fps/ADAPTIVE_VS_UNIFORM_2FPS.md`):
same fixed 12 diagnostic clips, same target density (2fps), same model,
prompt, batching, decoding — only the timestamp-allocation formula differs
(motion-weighted `allocate_timestamps()` vs. new, additive
`allocate_timestamps_uniform()`, evenly spaced). Frame counts matched exactly
for all 12 clips before any Gemini call; `pytest test_run_current_model.py`
passed before and after the additive code change (56 passed, 6 skipped).

**Measured results:**

| metric | adaptive | uniform |
|---|---|---|
| corpus WER | 1.0524 | 1.0594 |
| mean WER | 1.0825 | 1.0590 |

- Median per-clip delta: **0.0000**
- 2 improved / 5 worsened / 5 unchanged (of 12)

**Interpretation:** the single largest numerical "improvement"
(`fZM3IcM2Xs4_14_15_16-10-rgb_front`, WER 1.9130 → 1.0000) remained a complete
semantic/topic failure under both arms — a hallucination about "different
perspectives and situations" replaced by a hallucination about "crawling
around for two hours," neither related to the reference (a festive musical
performance). This is a swap between two failure modes, not a correction.
With that outlier's influence discounted, the result is flat and mixed.

**Conclusion:** no evidence that replacing motion-weighted sampling with
uniform sampling fixes the dominant failure, at this sample size and target
density. Manifest-hint-bucket breakdowns (n=2–6 per bucket) show no
sample-size-credible category-level win for either sampler.

---

## 8. Batch/context controlled experiment (independent batches vs. overlapping sliding windows)

**Design** (`controlled_ablation/independent_vs_sliding/INDEPENDENT_VS_SLIDING.md`):
same 12 diagnostic clips, same sampled frames (not resampled), same
model/prompt/decoding — only frame *grouping* differs: independent
non-overlapping 24-frame batches vs. overlapping 24-frame sliding windows
(stride 12, 50% overlap), merged via a deterministic, reference-free
frame-index ownership partition (fixed before any inference, cannot see
model output or ground truth). `run_current_model.py` was not modified at
all for this experiment (imported strictly read-only).

**Measured results:**

| metric | independent (baseline) | sliding (overlap) |
|---|---|---|
| corpus WER | 1.0524 | 0.9545 |
| mean WER | 1.0825 | 0.9542 |

- Median per-clip delta: **0.0000**
- 4 improved / 2 worsened / 6 unchanged (of 12)

**This numeric movement must NOT be read as a quality improvement.** Four
tempering facts, in order of importance:

1. **All 12 clips remain topic-mismatched under both arms.** Walking the full
   side-by-side table, every prediction — under both independent batching and
   sliding windows — describes content unrelated to its reference. Zero
   clips recovered correct meaning under either arm.
2. **The largest WER "win" swaps one hallucination for another.** The single
   largest delta (`fZM3IcM2Xs4`, -0.9130) replaces a hallucination about
   "interpersonal conflict + chest pain" with one about "combining things +
   a racing heart" — both fully unrelated to the reference (a festive
   musical performance). It scores better only because the new fabrication
   happens to be closer in word count under edit-distance WER.
3. **The multi-batch subset is only n=4.** Mean delta on this subset is
   -0.2503, but one clip dominates it, and two of the four
   (`FzmL8SL6Bow`, `fzNnTgHa1lM`) show **exactly zero** WER change despite
   producing completely different fabricated text under the sliding arm.
4. **Single-batch clips are architecturally identical between the two
   arms** (1 window = 1 batch = the same frames, same call) — any
   difference in their output is decoding noise from a fresh,
   non-deterministic Gemini call, not an architecture effect. Empirically,
   across these 8 single-batch clips: **2 improved, 2 worsened, 4
   unchanged, mean WER delta -0.0673.** This is used as an empirical noise
   floor for interpreting the multi-batch subset's -0.2503 mean delta —
   the two are not far apart in magnitude.

**Conclusion, stated exactly as required:** do **not** read this experiment
as evidence that sliding windows improved ASL translation quality. It moved a
WER number; it did not recover meaning, and part of the movement is
indistinguishable from generation noise.

---

## 9. Overall temporal diagnosis

Three frame-based temporal interventions were tested against the frozen
adaptive-2fps/independent-batch baseline:

1. **~4x higher adaptive frame density** (Section 6) — essentially flat.
2. **Uniform instead of adaptive/motion-weighted sampling** (Section 7) —
   essentially flat, single outlier is not a meaningful semantic win.
3. **Overlapping sliding windows instead of independent batches** (Section 8)
   — larger numeric WER movement, but **no demonstrated semantic recovery**
   on any of the 12 clips, and a meaningful share of the movement is
   indistinguishable from decoding noise.

**Stated conservatively, exactly as required:**

> None of the three tested interventions demonstrated reliable semantic
> recovery. This is **not** a claim that "temporal information is useless" —
> it is a claim that these three frame-based interventions, tested at these
> sample sizes, on these clips, did not materially resolve the pipeline's
> dominant semantic/topic failure.

**What remains unknown / not established** (`FINAL_TEMPORAL_DIAGNOSIS.md`
Task 2.6):

- The true ASL-specific failure taxonomy (handshape / motion / fingerspelling
  / numbers / facial-non-manual / genuine visually-grounded hallucination)
  — requires an ASL-fluent reviewer; nothing in this diagnosis establishes it.
- **Native/direct video input** (as opposed to manually extracted independent
  frames) is completely untested by any experiment in this diagnosis.
- **Model choice** — every experiment used the same `gemini-3.6-flash`
  model; nothing here shows whether a different/stronger model would help.
- Small-n architecture ablations are affected by measurable generation
  noise (the sliding-window probe's own single-batch control shows a mean
  WER delta of -0.0673 from decoding variance alone) — any future small-n
  ablation should budget for and report this noise floor.

---

## 10. Evaluation-driven self-improvement follow-up

After delivering the temporal diagnosis, the manager shared a ChatGPT
conversation framing "evaluation-driven self-improvement" as a general
pattern, with ASL as one of two worked examples. The conversation's ASL
pipeline was extracted and read in full (transcript retrieved via browser
rendering of the share link, since the URL is a JS-rendered page). Its
content:

1. **Structured/adaptive sampling** — low-fps global scan; detect hand
   velocity/direction-change/pauses; dense sampling in informative
   intervals; continuous clips preserved for fingerspelling; full-body +
   high-resolution hand crops provided together.
2. **Multi-channel recognition** — separate channels for continuous signing,
   fingerspelling, mouthing/facial cues, pose/motion trajectory, and
   linguistic context, fused rather than handled by one general VLM.
3. **Change the VLM's role** — specialized recognizers produce
   candidates/confidences; the VLM does contextual reranking, correction,
   error explanation, and low-confidence routing, instead of carrying the
   entire visual-recognition burden itself.
4. **Evaluation-driven improvement loop** — failure cases → error grouping →
   candidate workflow changes → replay on a frozen benchmark → overall +
   subgroup regression checks → human approval → versioned workflow policy.
5. **The conversation's own P0 recommendation** — do not build unrestricted
   automatic evolution yet; first build a diagnostic set and understand
   failure sources.

**Key observation:** this framework is **largely consistent with the workflow
already performed**, not a new methodology to adopt. Each of the three
temporal experiments (Sections 6–8) already followed exactly the loop in
item 4 above, manually and human-gated: identify a candidate change → replay
it on the frozen/shared 12-clip (or paired-76) set → evaluate against the
existing baseline → explicitly reject or (not yet) promote, with results
written up for review before any further step. The three completed
ablations are, in effect, three manually-executed, human-gated iterations of
an evaluation-driven improvement loop — this was independently arrived at
before the shared conversation was reviewed. Item 5's P0 (build a diagnostic
set before automating) is also already satisfied: the 12-clip and 40-clip
diagnostic sets (Sections 4–5) were built, and `FINAL_TEMPORAL_DIAGNOSIS.md`'s
own Task 4 recommendations (native-video probe, ASL-expert review) already
match this same P0 for ASL specifically, arrived at independently.

---

## 11. Gap analysis against the newly shared ASL pipeline

| Shared-pipeline idea | Classification | Evidence / reasoning |
|---|---|---|
| Motion-aware, non-uniform temporal sampling density | **ALREADY IMPLEMENTED, ALREADY TESTED** | `allocate_timestamps()` already does this; uniform-vs-adaptive (Section 7) and 2fps-vs-8fps (Section 6) both tested this axis with no semantic recovery |
| Higher frame density | **ALREADY TESTED, NOT PROMISING** | Section 6 |
| Generic additional context via re-batching / sliding windows | **ALREADY TESTED, NOT PROMISING** | Section 8 — WER moved, semantics did not |
| Build a diagnostic set before automating | **ALREADY IMPLEMENTED** | Sections 4–5; independently arrived at before this conversation was seen |
| Hand-specific velocity/direction/pause detection (vs. our whole-frame pixel-diff motion proxy) | **PARTIALLY IMPLEMENTED** | The mechanism *class* exists (motion-weighted density); the *signal* is coarser than hand-tracked kinematics. Refining it is unproven to matter, since both removing the motion signal (uniform) and quadrupling density under it (8fps) already failed to move the dominant failure |
| Continuous temporal context specifically for fingerspelling-flagged spans | **PARTIALLY IMPLEMENTED** | We tested generic sliding-window context (Section 8), not fingerspelling-targeted continuous/native video specifically |
| Manual evaluation-driven candidate/reject loop | **PARTIALLY IMPLEMENTED** | Already done manually (Section 10); the *automated* clustering/candidate-generation layer does not exist, but is explicitly not recommended yet even by the source conversation |
| Full-body + high-resolution hand-crop dual-stream input | **GENUINELY NEW** | No crop/hand-detection/dual-image-stream code exists anywhere in `run_current_model.py` (confirmed by code search) |
| Native/direct video input to Gemini | **GENUINELY NEW** | No video-upload code path exists; only `Part.from_bytes(image/jpeg)` per extracted frame. Already our own top recommendation independent of this conversation |
| Specialized fingerspelling recognizer + confidence candidates + VLM reranking | **GENUINELY NEW** | No candidate/confidence/reranking architecture exists. Targets a narrow bucket not shown to explain the dominant 92.5% topic-level failure |
| Pose/mouthing/multi-channel recognition | **GENUINELY NEW** | No pose, mouthing, or channel-fusion code exists |
| Verified handshape/motion/fingerspelling/facial failure taxonomy | **BLOCKED — REQUIRES ASL EXPERTISE** | Explicitly out of scope for a non-ASL-fluent, text-only reviewer (Section 5) |
| Validation of any specialized recognition channel's correctness | **BLOCKED — REQUIRES ASL EXPERTISE** | Cannot confirm a pose/fingerspelling/mouthing channel is producing correct output without someone who can watch and judge the signing |

---

## 12. Recommended next step

**Current recommendation: ASK MANAGER FIRST before new implementation or
additional Gemini/API usage.** Rationale: this report is documentation-only
by design; the recommended experiment below requires adding a new local
dependency (a hand/pose detector) and touching the production sampling code
again, and consumes additional Gemini quota after the project's monthly
billing cap was already hit once during the 8fps experiment
(`docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md`) — a
resource the manager controls, not this session.

### Recommended smallest next experiment

**Full-body + high-resolution hand-crop dual-stream input**, on the existing
12-clip diagnostic set.

- Reuse the same 12 diagnostic clips, the same motion-weighted adaptive
  timestamps, the same frame budget, the same sampling strategy, the same
  batching, the same model, and the same decoding settings — do **not**
  touch the temporal-sampling axis at all (this is what distinguishes it
  from Sections 6–8, all of which varied a temporal axis already found
  unproductive).
- For each already-sampled frame, add one additional cropped, higher-resolution
  image of the signer's hand/arm region (a local hand/pose detector, e.g.
  mediapipe — no Gemini cost) alongside the existing full frame, with a
  parallel timestamp marker.
- Score with the same non-ASL-fluent, text-only semantic-adequacy method
  already used for the 40-clip review (Section 5), blind to condition,
  against the existing frozen 12-clip baseline predictions already on disk.

**Pre-registered promotion criterion:** at least 3 of 12 clips move from
`semantic_adequacy=0` to `≥1`, OR `reference_topic_mismatch` flips from
yes→no in ≥25% of the 12 clips — a bar set explicitly above the established
decoding-noise floor (mean WER delta ≈ -0.0673 on architecturally-inert
clips, Section 8; zero clips flipped topic-match status in any prior
ablation).

**Pre-registered rejection criterion:** 0/12 clips flip semantic-adequacy
category, or any movement stays within the established noise floor with no
topic-mismatch flips → conclude spatial hand-resolution is not the
bottleneck either, and do not scale to the full 128-clip benchmark.

**Why this axis, not another:** it tests a **spatial-resolution** axis,
orthogonal to the three temporal axes already exhausted (Sections 6–8), and
is implementable at low incremental Gemini cost (same call count, only
modestly larger per-call payload) — well below what triggered the prior
billing cap.

**Second-priority option (not recommended first):** a small native/direct-video
Gemini probe on a handful of clips — also genuinely new and already our own
top pick, but a larger, more expensive input-formulation change with an
unknown token/cost profile, carrying real risk of re-hitting the Gemini
billing cap.

**Explicitly not recommended as a next step:** further frame-rate tuning
(5fps/10fps — would likely repeat the flat 2fps-vs-8fps result); the
fingerspelling-recognizer+reranking pipeline, pose/mouthing channels, or the
full multi-channel system (all high-effort, all blocked on ASL expertise to
validate, and none shown to target the dominant topic-level failure); any
automated evaluation-driven workflow loop (premature — our own sliding-window
result shows WER can improve while semantics do not, so an automated loop
would need a trustworthy semantic metric we don't yet have).

---

## Appendix — source file map

| Topic | File |
|---|---|
| Baseline denominator explanation | `TASK0_baseline_denominator.md` |
| Architecture discovery, 12/40-clip selection rationale | `PHASE1_SUMMARY.md` |
| 12-clip diagnostic set | `diagnostic_12_clips.json` / `.csv`, `inspector/` |
| 40-clip taxonomy set | `taxonomy_40_clips.json` / `.csv` |
| Text-semantic review (40 clips) | `taxonomy_40_text_semantic_review.json` / `.csv`, `TEXT_SEMANTIC_REVIEW_SUMMARY.md` |
| Human-review schema (unfilled, ASL-expertise-gated) | `taxonomy_40_human_review.json` / `.csv`, `HUMAN_REVIEW_GUIDE.md` |
| Frame-density experiment (2fps vs 8fps, 76 clips) | `paired_76_2fps_vs_8fps.csv`, `PAIRED_76_PRELIMINARY_ANALYSIS.md` |
| Sampling-strategy experiment (adaptive vs uniform) | `controlled_ablation/adaptive_vs_uniform_2fps/` |
| Batch/context experiment (independent vs sliding) | `controlled_ablation/independent_vs_sliding/` |
| Full consolidated diagnosis | `FINAL_TEMPORAL_DIAGNOSIS.md` |
| Manager-facing short summary (temporal diagnosis) | `MANAGER_SUMMARY.md` |
| Full file map of the whole diagnosis | `EXPERIMENT_INDEX.md` |
| 8fps billing blocker record | `docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md` |

*All paths above are relative to
`asl-translator/evaluation/diagnostics/phase1_temporal_ablation/` unless
otherwise noted. No Gemini/API call, code change, or experimental-result
modification was made in the production of this report.*
