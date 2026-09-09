# Final Temporal-Architecture Diagnosis — Curify/Gemini ASL Translation

**Status: consolidation only. No inference was run to produce this report.**
Every number below is read from an already-completed, already-saved artifact
(see `EXPERIMENT_INDEX.md` for the full file map). No Gemini/API call, no new
model run, no repeat trial.

---

## Task 1 — Consolidated evidence, in chronological order

### A. Frozen Gemini baseline

- **128/128** Curify/Gemini 3.6 predictions exist for the frozen 128-clip
  How2Sign v2 benchmark (`curify_gemini_3_6_2026_09_04/corpus_summary.json`:
  `n_total=128, n_success=128, n_failure=0`). Nothing is missing on the
  Curify side.
- A separate file, `corpus_summary_matched_126.json`, restricts to the
  126-clip intersection where OpenSLT and Uni-Sign *also* have usable
  predictions (OpenSLT failed on 2 clips; Uni-Sign failed on 0). **This is a
  cross-model comparability restriction, not a Curify missing-prediction
  issue** — Curify's own corpus WER is nearly identical on both denominators
  (0.9762 on 128, 0.9761 on the matched 126). See `TASK0_baseline_denominator.md`
  for the full mechanism.
- **Baseline corpus WER: 0.9762** (128-clip denominator).
- **Architecture:** motion-weighted/adaptive frame-timestamp allocation
  (`allocate_timestamps`, energy-weighted over segmented active/idle motion
  runs); target frame density `TARGET_FRAMES_PER_SEC = 2.0`, duration-scaled
  budget clamped to `[MIN_FRAME_BUDGET=24, MAX_FRAME_BUDGET=240]` (so very
  short clips sample well above a literal 2 fps — this floor matters for
  interpreting several results below); frames sent to Gemini in chronological
  order; independent, non-overlapping `BATCH_SIZE=24`-frame Gemini calls with
  no cross-batch context; model `gemini-3.6-flash`, `thinking_level=medium`,
  exact-text adjacent-duplicate dedup enabled.

### B. 40-clip LLM-assisted text-semantic review

**Method label: "LLM-assisted text semantic review" — English reference vs.
Gemini prediction text only. This is NOT ASL-fluent visual annotation and
makes no claim about what is visible in the signed video.** Produced by the
assistant reading only two English strings per clip; no video was watched, no
ASL expertise applied, no model/API call made to produce it.

| metric | value |
|---|---|
| clips reviewed | 40 / 40 |
| semantic_adequacy = 2 (core meaning correct) | 0 / 40 (0%) |
| semantic_adequacy = 1 (partial) | 3 / 40 (7.5%) |
| semantic_adequacy = 0 (wrong/unrelated) | 37 / 40 (92.5%) |
| reference_topic_mismatch = yes | 36 / 40 (90%) |
| correct_meaning_different_english = yes | 0 / 40 (0%) |
| obvious text-level repetition | 0 / 40 (0%) |

Full detail, confidence distribution, representative examples, and
manifest-hint cross-tabs: `TEXT_SEMANTIC_REVIEW_SUMMARY.md`.

### C. Frame-density probe (paired 76, adaptive ~2fps vs. adaptive ~8fps)

Same sampling *strategy* (motion-weighted/adaptive), same batching
(independent 24-frame), same model/prompt — only `target_frames_per_sec`
differs (2.0 vs. 8.0). **Preliminary and confounded**: Experiment B only
completed 76/128 clips before hitting an external Gemini billing/spend cap
(`docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md`); baseline A
is re-scored on the identical 76-clip subset for a fair pairing, but this is
not the full 128-clip result and the file's own "Confounds" section should be
read before citing it further.

| metric | 2 fps | 8 fps |
|---|---|---|
| corpus WER | 0.9730 | 0.9715 |

- Absolute corpus WER delta: **-0.0015**
- 15 improved / 20 worsened / 41 unchanged (of 76)
- Median per-clip delta: **0.0000**

**Conclusion: essentially flat.** Increasing the current adaptive sampler's
frame budget ~4x did not materially move the benchmark.

### D. Sampling-strategy probe (12 diagnostic clips, adaptive 2fps vs. uniform 2fps)

Same target density, model, prompt, batching, decoding — only the
timestamp-allocation *formula* differs (motion-weighted vs. evenly-spaced,
ignoring motion energy). Full design and per-clip timestamp comparison:
`controlled_ablation/adaptive_vs_uniform_2fps/design_check.json` and
`ADAPTIVE_VS_UNIFORM_2FPS.md`.

| metric | adaptive | uniform |
|---|---|---|
| corpus WER | 1.0524 | 1.0594 |
| mean WER | 1.0825 | 1.0590 |

- Median per-clip delta: **0.0000**
- 2 improved / 5 worsened / 5 unchanged
- The single largest numerical "improvement" (`fZM3IcM2Xs4`, WER 1.9130 →
  1.0000) remained a complete semantic/topic failure under both arms — one
  fabricated narrative replaced by a different fabricated narrative, not a
  correction.

**Conclusion: no evidence that replacing motion-weighted sampling with
uniform sampling fixes the dominant failure**, at this sample size and
target density.

### E. Batch/context probe (12 diagnostic clips, independent batches vs. overlapping sliding windows)

Same sampled frames (not resampled), same model/prompt/decoding — only frame
*grouping* differs: independent, non-overlapping 24-frame batches vs.
overlapping 24-frame sliding windows (stride 12, 50% overlap), merged via a
deterministic, reference-free frame-index ownership partition (full
5-point design rationale in
`controlled_ablation/independent_vs_sliding/INDEPENDENT_VS_SLIDING.md`).

| metric | independent (baseline) | sliding (overlap) |
|---|---|---|
| corpus WER | 1.0524 | 0.9545 |
| mean WER | 1.0825 | 0.9542 |

- Median per-clip delta: **0.0000**
- 4 improved / 2 worsened / 6 unchanged

**This numeric movement must NOT be read as a quality improvement.** Four
things temper it, in order of importance:

1. **All 12 clips remain topic-mismatched under both arms.** Walking the full
   side-by-side table (`paired_results.csv`), every prediction — under
   independent batching *and* under sliding windows — describes content
   unrelated to its reference. Zero clips recovered correct meaning under
   either arm.
2. **The largest WER improvements replace one severe hallucination with
   another**, not a recovery of reference meaning. The single largest delta
   (`fZM3IcM2Xs4`, -0.9130) swaps a hallucination about "interpersonal
   conflict + chest pain" for a hallucination about "combining things + a
   racing heart" — both fully unrelated to the reference (a festive musical
   performance). The result scores better only because the new fabrication
   happens to be closer in word count to the reference under edit-distance
   WER.
3. **The multi-batch subset is only n=4** (`FzmL8SL6Bow`, `fzNnTgHa1lM`,
   `fZM3IcM2Xs4`, `G05uFub3YFc` — the only 4 of the 12 diagnostic clips with
   more than 24 sampled frames). Mean delta on this subset is -0.2503, but
   one clip (`fZM3IcM2Xs4`) dominates it, and two of the four
   (`FzmL8SL6Bow`, `fzNnTgHa1lM`) show **exactly zero** WER change despite
   producing completely different fabricated text under the sliding arm —
   illustrating that even a WER *match* here reflects near-total-failure
   arithmetic, not output stability.
4. **Single-batch clips are architecturally identical between the two arms**
   (1 window = 1 batch = the same frames, same call) — any difference in
   their output can only be decoding noise from a fresh, non-deterministic
   Gemini call, not an architecture effect. Empirically, across these 8
   single-batch clips: **2 improved, 2 worsened, 4 unchanged, mean WER delta
   -0.0673.** This is used below as an empirical noise floor: it shows that a
   ±0.07-to-0.56 WER swing on an individual short clip can occur from
   decoding variance alone, with zero architectural cause — which is not
   small relative to several of the "improvements" attributed to the
   multi-batch subset.

**Do not read this experiment as evidence that sliding windows improved ASL
translation quality.** It moved a WER number; it did not recover meaning, and
part of the movement is indistinguishable from generation noise.

---

## Task 2 — The manager's original questions, answered

### 1. What do concrete failures look like?

Reading the 12-clip frame inspectors (`inspector/`,
`controlled_ablation/*/inspectors/`) alongside the 40-clip text-semantic
review, the dominant, overwhelming failure mode is **topic-level semantic
mismatch**: the model produces fluent English that describes a different
scene or topic than what was signed (92.5% of the 40-clip sample scores
semantic_adequacy=0; 90% shows a clear reference-topic mismatch). This is not
primarily a wording-precision problem — 0/40 clips show the "correct meaning,
different English" pattern that would indicate the model understood but
phrased differently. Secondary, much rarer patterns observed in the
side-by-side tables: occasional fabricated specifics not present in the
reference (an invented number sequence, an invented birthplace, an invented
name), and a small number of empty/near-empty outputs. No text-level
repetition was observed anywhere in the 40-clip sample.

### 2. Can the benchmark be categorized?

Only into **reference-derived heuristic groups**, computed from the English
reference text (does it contain a number token, a proper-noun/acronym
fingerspelling candidate, above-median signing speed, or a question mark):
`fingerspelling_candidate`, `number_token`, `fast_signing`, `question`, and
`plain_no_flag` for everything else. **These are explicitly NOT
ASL-expert-confirmed visual categories** — a clip tagged `number_token` is
one whose *reference text* happens to contain a number, not one an ASL-fluent
reviewer confirmed shows number-handshape content in the video. Every report
in this diagnosis repeats this caveat wherever these buckets are used, and
none of the three architecture ablations found a bucket-level effect credible
at their sample sizes (n=2–24 per bucket depending on the experiment).

### 3. Does raising frame density fix the problem?

**No material evidence.** Paired-76 (2fps vs. ~8fps): corpus WER 0.9730 →
0.9715, a -0.0015 absolute delta, median per-clip delta 0.0000, roughly even
split of per-clip winners/losers (15/20/41). Flat.

### 4. Does changing sampling strategy fix the problem?

**No material evidence on the 12 diagnostic clips.** Adaptive vs. uniform:
corpus WER 1.0524 → 1.0594 (slightly worse, pooled), mean WER 1.0825 → 1.0590
(slightly better, pooled, driven by one non-meaningful outlier), median delta
0.0000, 2 improved / 5 worsened / 5 unchanged.

### 5. Does overlapping/sliding temporal context fix the problem?

**WER moves numerically (corpus WER 1.0524 → 0.9545), but no semantic
recovery is observed** — all 12 clips remain topic-mismatched under both
arms, and the result is confounded by generation noise visible even in the
architecturally-identical single-batch clips (mean delta -0.0673 there, from
decoding variance alone). This is the largest numeric movement of the three
frame-based interventions and the one most likely to be over-read if quoted
without its caveats.

### 6. What remains unknown?

- The **true ASL-specific failure taxonomy** — whether errors originate in
  handshape, motion/trajectory, fingerspelling, numbers, facial/non-manual
  markers, or genuine visually-grounded hallucination — requires an
  ASL-fluent reviewer watching the signing itself. Nothing in this diagnosis
  establishes this; it was explicitly out of scope for a non-ASL-fluent,
  text-only review (see `HUMAN_REVIEW_GUIDE.md`'s TEXT-BASED vs. ASL/VISUAL
  split).
- **Native/direct video input** (as opposed to manually extracted independent
  frames) is completely untested by any experiment in this diagnosis.
- **Model choice**: nothing here establishes whether a different or stronger
  vision-language model would perform materially better on this benchmark —
  every experiment used the same `gemini-3.6-flash` model.
- **Small-n architecture ablations are affected by generation noise.** The
  12-clip sliding-window probe's own single-batch control (n=8,
  architecturally inert) shows a mean WER delta of -0.0673 from decoding
  variance alone — any future small-n ablation should budget for and report
  this kind of noise floor, not just a raw before/after delta.

---

## Task 3 — Final scientific conclusion

The dominant failure mode on this benchmark is **semantic/topic mismatch**,
not wording variation. Three frame-based temporal interventions were tested
against the frozen adaptive-2fps/independent-batch baseline:

1. **substantially higher adaptive frame density** (paired-76, ~2fps → ~8fps)
2. **uniform instead of adaptive/motion-weighted sampling** (12 diagnostic
   clips, held at 2fps)
3. **overlapping temporal windows instead of independent batches** (12
   diagnostic clips, same frames, same density)

**None produced demonstrated semantic recovery on the diagnostic cases.**
Interventions (1) and (2) show essentially flat aggregate WER. Intervention
(3) shows a larger WER-metric movement, but inspection of the actual
predictions shows no clip recovering correct meaning under it, and a
meaningful share of that movement is indistinguishable from generation noise
(the architecturally-inert single-batch clips move by a comparable amount on
their own).

**Therefore, the evidence does not support further fine-grained tuning of
frame rate/sampling as the immediate next step.** This is a statement about
the three interventions actually tested, at the sample sizes tested — it is
**not** a claim that temporal information is universally irrelevant to this
task, nor that no frame-based intervention could ever help. It is a claim
that these three, on these clips, did not materially resolve the benchmark's
dominant failure.

---

## Task 4 — Recommended next options (not implemented)

**Option A — Small native/direct-video Gemini probe on a few representative clips.**
Rationale: this changes the input *formulation* more fundamentally than any
frame-sampling or batching variant tested so far — it removes the manually
extracted independent-image-frame representation entirely, rather than
varying a parameter within it. If the dominant failure is an artifact of the
frame-extraction/prompting formulation itself (rather than genuine ASL
recognition difficulty), this is the most direct way to find out. Should be
scoped small (a handful of clips, likely drawn from the existing 12-clip
diagnostic set for continuity) before any corpus-scale commitment.

**Option B — ASL-fluent expert review of a small representative subset.**
Rationale: this diagnosis has exhausted what a non-ASL-fluent, text-only
review can determine. Every unresolved question in Task 2.6 above —
handshape vs. motion vs. fingerspelling vs. facial/non-manual vs. true
visually-grounded hallucination, and whether the fps/sliding-window
hypotheses ever had visual merit — requires someone who can watch the signing
and judge it. The 12-clip diagnostic set (with its existing frame inspectors)
and the `requires_asl_expert_review` flags already set in the 40-clip
text-semantic review are a ready-made starting subset.

**5fps or 10fps is not recommended as the immediate next experiment.** The
2fps-vs-8fps result was already flat across a ~4x density change; there is no
new evidence in this diagnosis suggesting an intermediate or higher density
would behave differently, and doing so would repeat the same class of
frame-based tuning this diagnosis just found unproductive.

---

*Produced entirely by consolidating existing, already-completed artifacts —
see `EXPERIMENT_INDEX.md` for the full source map. No Gemini/API call was
made to produce this report.*
