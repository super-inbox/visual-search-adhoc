# Uni-Sign Failure Analysis & Lightweight Intervention Summary

**Date:** 2026-10-15 · **Branch:** `baobao/visual-production-research-2026-10-05`
**System under study:** the existing, publicly released Uni-Sign pose-only How2Sign checkpoint
(`how2sign_pose_only_slt.pth`). No new model was built and no model was retrained. All work is diagnosis of that
system plus inference-time or post-processing changes around it.
**Benchmark:** the frozen 128-clip How2Sign subset used in all earlier reports.
**Runtime:** Tesla T4, fp16 (the official configuration is bf16; see §2).

Source reports (all committed):

| Topic | Report |
|---|---|
| P0-12 preprocessing gap | `../10.13/asl-p0-12-full128-fp16/P0_12_RESULTS.md` |
| Error taxonomy | `../10.13/asl-unisign-error-taxonomy/ERROR_ANALYSIS_REPORT.md` |
| Decode-length test | `../10.13/asl-unisign-decode-length-cap/DECODE_LENGTH_RESULTS.md` |
| Repetition cleanup | `../10.14/asl-unisign-repetition-cleanup/STAGE1_RESULT.md`, `CLEANUP_RULE.md` |
| Chunked decoding | `../10.14/asl-unisign-chunked-decoding-pilot/PILOT_RESULTS.md`, `PILOT_PLAN.md` |

---

## 1. Goal

1. **Find where the existing Uni-Sign system fails** on the frozen How2Sign benchmark. First, explain why our own
   pipeline scored much lower than the official one. Then characterise the errors that remain once the inputs are
   correct.
2. **Test whether a few cheap changes help**: changes to decoding settings, post-processing or input chunking, with
   no full-model retraining.

Every intervention had its decision rules written and frozen before any metric was computed, so a negative result
could not be re-tuned into a positive one.

## 2. What we established first: the preprocessing gap (P0-12)

**Plain language.** Our old score (5.39 BLEU-4) was far below the official pipeline mainly because of how we cut and
cropped the video before pose extraction. Our pose extractor was not the main problem.

**Design.** Four conditions used the same 128 clips, references, checkpoint and evaluation code. Only the pose source
and the input preparation differed.

| Condition | Pose source | Timing / crop | BLEU-4 | ROUGE | BLEURT |
|---|---|---|---|---|---|
| A_official | official poses | official timing + signer crop | **9.13** | 29.00 | 0.441 |
| B_ours_5p39 | our extractor | original timestamps, full frame | **5.47** | 18.69 | 0.377 |
| B_aspect | our extractor | as B, aspect / coordinate fix | **5.80** | 20.59 | 0.385 |
| C_ours_on_official_crop | our extractor | official timing + signer crop | **8.61** | 27.67 | 0.425 |

**Observed evidence**
- Running *our* extractor on the official timing and crop (B → C) recovers **85.7 % of the BLEU-4 gap** to A_official.
  ROUGE recovers 87 % and BLEURT 75 %.
- Once timing and crop are matched, swapping our poses for the official ones (C → A) adds only **+0.52 BLEU-4**.
- The aspect / coordinate fix alone (B → B_aspect) adds only +0.32 BLEU-4.

**Caveats**
- **T4 / fp16, not an exact bf16 reproduction.** A_official scores 9.13 here vs 9.59 for the authors' released
  predictions, and B scores 5.47 vs our historical 5.39. The *contrasts* between conditions are the result. The
  absolute values are not.
- "Official timing + crop" changes timestamps, crop and normalisation together. The gain cannot be split between
  timing and crop.
- Single run per condition, no bootstrap CIs. The small deltas (+0.32, +0.52) may be within noise.

**Conclusion.** The old 5.39-vs-9.x gap was mainly a **preprocessing / timing / crop** issue, not primarily a
pose-extractor failure. The practical fix is input preparation: segment to the signing and crop to the signer.

## 3. Error taxonomy (automated first pass, 128 clips)

> **Status: automated / weak-label observations only.** Every category label was produced by heuristics on the
> English reference text or by proxies computed from pose files. None of them was checked against the videos by an
> ASL-fluent reviewer.

**Plain language.** With correct inputs, Uni-Sign usually produces fluent English that is wrong or only partly
related to what was signed. It also sometimes loops, drops names, and comes out too short on long sentences.

**Observed error profile (A_official, n = 128; primary type, one per clip)**

| Primary error type | Clips | Meaning |
|---|---|---|
| Substitution / fluent-but-wrong | **67** | fluent output, partial overlap, wrong content words |
| Hallucination candidate | 26 | < 20 % of predicted content words appear in the reference |
| Repetition loop | 18 | repeated 3-gram not present in the reference |
| Omission | 13 | output < 0.6× reference length |
| Over-generation | 4 | output > 1.6× reference length |

C (our extractor, same frames) has nearly the same profile and agrees with A's primary type on 99/128 clips.

**Weak-label observations (token-level; small n; exploratory)**
- **Rare-name / entity recovery is weak.** Only 2 of 21 rare multi-letter names or acronyms in the references
  appear in the output, with either pose source. This is **not a verified fingerspelling failure**: we did not check
  whether the signer fingerspelled these names or used a name sign, mouthing or nothing.
- **Negation cues are often missing.** In 7 of 13 references containing a negation, the output has none.
- **Question cues are often missing.** In 10 of 13 references ending in "?", the output has no question mark.
  These are English-surface checks. They are **not verified ASL findings** about non-manual negation or question
  marking.
- **Long references get outputs that are too short.** No prediction exceeds 50 words. 71 % (15/21) of outputs for
  references of ≥ 35 words lack terminal punctuation, against 6.5 % for shorter references.

**Negative / null observations**
- No broad category (linguistic or visual proxy) shows a sentence-level chrF penalty that survives length matching
  and Bonferroni correction. With n = 13–18 per category, only large effects would be detectable.
- No category depends specifically on the pose extractor (A vs C).

**Manual review.** A stratified 45-clip review queue was prepared (`manual_review_queue.csv`, all rows `PENDING`).
A fuller draft review package (`manual_review/`, a build script and an HTML template) exists **only locally and is
uncommitted**. ASL-specific manual verification was **not required for this iteration and was not completed**, so
none of the categories above is a manually verified or confirmed ASL linguistic finding.

## 4. Decode-length test

**Hypothesis.** Long outputs might be failing because inference stops at `max_new_tokens = 100`.

**Design.** Re-decode A_official with the cap at 100, 150 and 256 (R100 / R150 / R256) and change nothing else. R100
reproduced the committed P0-12 output byte for byte.

**Observed evidence**

| | R100 | R150 | R256 |
|---|---|---|---|
| BLEU-4 | 9.13 | 9.14 | 9.14 |
| chrF | 28.99 | 28.95 | 28.94 |
| BLEURT | 0.4407 | 0.4407 | 0.4408 |
| Clips hitting the cap | 2 / 128 | 1 / 128 | 0 / 128 |

- **126 of 128 outputs are byte-identical** across all three settings.
- Only **2/128** hit the 100-token cap, and both were already repetition loops ("a typical typical typical …",
  "a D, a D, a D, …"). A larger cap just extended the loops, and their sentence chrF fell slightly.
- **Long-reference outputs stop on their own by emitting EOS**, at a median of about 33 words, for references of
  ≥ 35 words. On those 21 clips the length ratio stays at about 0.64 and chrF moves by −0.07.

**Conclusion: rejected.** The 100-token inference cap is not the main cause of long-sequence failure. The model
predicts end-of-sentence early on its own.

**Untested hypothesis.** Uni-Sign truncates training targets to 50 mT5 tokens (`max_length = 50`). Generated lengths
cluster at 48–52 tokens (12 of the 21 long-reference clips), which is *consistent with* a learned length prior. Training
was not changed, so this remains a **plausible, untested hypothesis**.

## 5. Lightweight intervention 1: repetition cleanup

**Idea.** Delete runaway repeats from the output text with a deterministic rule. No model change.

**Design.** Rule v1 collapsed any phrase of ≤ 8 tokens repeated ≥ 3 times in a row. It was **frozen (sha256-pinned)
before any metric was computed**. Two safety guards had to pass before metrics would be allowed:
- G1: the rule must not change any human reference;
- G2: it must change only the clips the taxonomy flags as loops.

**Observed evidence**
- **G1 failed.** A human reference legitimately says "mixed and mixed and mixed", and the rule would collapse it.
- **G2 failed.** The rule changed two obvious loops that the taxonomy's reference-based definition does not count as
  loops. No reference-free rule can respect that boundary.
- **Coverage was small.** The rule touched only 3 of the 18 loop clips. Most loops are clause-level near-repeats
  ("we're going to put black spots on top of it and then we're going to put black spots on top of it") that a safe
  rule must leave alone. The pre-registered success criterion (halve the loop rate) was therefore unreachable.
- Broader n-gram rules that reach most loop clips also touch human references or non-loop outputs.

**Metrics were intentionally not computed.** The guards were designed to stop the run at that point.

**Conclusion: negative result.** Simple text post-processing cannot safely solve the repetition problem. A stricter
tandem rule (e.g. ≥ 4 copies) could serve as a **product guardrail against runaway loops**, but its threshold would be
chosen after seeing the failure. It should not be presented as a research-quality improvement.

## 6. Lightweight intervention 2: chunked decoding

**Idea.** The model writes about one sentence per call. So split long pose inputs into shorter time chunks, translate
each chunk independently, and join the outputs in order. This is inference-only.

**Design** (all arms, chunk boundaries and pass/fail thresholds frozen before any GPU run):

| Arm | Role | Rule |
|---|---|---|
| U36 | control | unchunked baseline; reproduced the original R100 outputs exactly (36/36 pilot clips, 128/128 overall) |
| S1 | exploratory | two equal halves (some halves still > 256 frames, so the loader's random subsampling stays in) |
| S2 | primary | K = ⌈frames / 256⌉ equal windows, each ≤ 256 frames |
| S3 | primary | S2 with each boundary moved to the lowest hand-motion frame within ±24 frames (a pause proxy) |

Clips: all 36 clips with more than 256 frames, split into two groups.
- **Targets:** 21 clips with long references (≥ 35 words).
- **Controls:** 15 clips that are long in frames but have short references (< 35 words).

**Observed evidence: targets (21 long-reference clips), S2 vs U36, paired-bootstrap 95 % CI**

| Metric | U36 | S2 | Change |
|---|---|---|---|
| chrF | 24.16 | 34.61 | **+10.4** [+7.7, +13.0] |
| BLEU-4 | 5.57 | 7.38 | **+1.8** [+0.04, +3.6] |
| BLEURT | 0.342 | 0.410 | **+0.068** [+0.041, +0.093] |
| Output / reference length | 0.64 | 1.16 | |
| Outputs without terminal punctuation (unfinished proxy) | 71 % | 19 % | |
| WER | 86.3 | 103.3 | +17.0 (worse: extra words) |

Sentence chrF improves on 19 of 21 target clips.

**Observed evidence: controls (15 long-clip / short-reference clips)**
- The output / reference length ratio rises from 1.00 to **≈ 1.58** (S2) and 1.52 (S3).
- **WER worsens by ≈ 42 points** (S2: +42.3 [+21.9, +68.6]).
- BLEU-4 and BLEURT changes are about 0, with CIs that include 0.
- Per clip, the result is roughly a coin flip: 8 clips improve and 7 worsen.
- chrF rises somewhat, but sacrebleu chrF weights recall double, so extra text inflates it. We read that rise as a
  recall effect, not better translation.

**S3 vs S2.** Pause-snapped boundaries **do not outperform** plain equal windows. S3 is lower than S2 on chrF, BLEU-4
and BLEURT in every subset.

**Pre-registered thresholds**

| | T1 target length ≥ 0.85 | T2 target ΔchrF ≥ 2, CI > 0 | T3 target ΔBLEU-4 ≥ 0 | T4 control ΔchrF ≥ −2 **and** length ≤ 1.3 | T5 loops ≤ U36 + 2 | Overall |
|---|---|---|---|---|---|---|
| S1 | ✓ | ✓ | ✓ | ✗ (length 1.46) | ✓ | **fail** |
| S2 | ✓ | ✓ | ✓ | ✗ (length 1.58) | ✓ | **fail** |
| S3 | ✓ | ✓ | ✓ | ✗ (length 1.52) | ✓ | **fail** |

Every arm passes T1, T2, T3 and T5, and every arm fails T4. **No arm passes overall.**

**Disclosed confound.** Uni-Sign normalises each input with its own body bounding box, so each chunk gets slightly
different scaling (median ratio to the full clip 0.96–0.98). This is inherent to "translate each chunk as its own
clip" and cannot be separated from chunking.

**Conclusion.** Chunking can bypass Uni-Sign's short-output behaviour, so the result is **partially mechanism-positive**. But
frame-count-based chunking is **not a robust intervention**. It over-generates whenever a long video contains
relatively little linguistic content, because each chunk yields about one sentence regardless of what it contains.

## 7. What we ruled out

| Hypothesis / intervention | Result |
|---|---|
| Wrong preprocessing is the main source of the old 5.39 gap | **Largely confirmed** (≈ 86 % of the BLEU-4 gap recovered; T4/fp16) |
| `max_new_tokens = 100` causes long-output failure | **Rejected** (126/128 outputs identical; long outputs end by EOS) |
| Simple post-hoc repetition cleanup works safely | **Rejected** (failed pre-metric safety guards; covered 3/18 loops) |
| Deterministic frame-count chunking is a general fix | **Rejected as an intervention**; partial mechanism-positive result on long-reference clips |
| Pause-based boundary snapping improves simple chunking | **Not supported** (S3 ≤ S2 on every subset) |
| Pose extractor is the main remaining bottleneck | **Not supported by P0-12** (+0.52 BLEU-4 once timing/crop matched) |

## 8. What remains open

- **Why the model stops around ~50 tokens.** Early EOS is observed, but its cause is not established.
- **Whether the training target `max_length = 50` causes it.** The evidence is consistent with this but does not test
  it. Other explanations (training-data length distribution, long-context effects) are not ruled out.
- **How to estimate linguistic content, or the right number of chunks, at inference time** without using the
  reference. Frame count cannot do it.
- **Confidence / abstention.** There is currently no way to flag likely-bad outputs (loops, hallucinations,
  truncation) before they reach a user.
- **ASL-specific errors** need ASL-fluent verification against the videos. These include true fingerspelling,
  non-manual negation and question marking, and classifier constructions. The 45-clip queue exists, but the review
  was not done.
- **Generalisation beyond the frozen 128 clips.** All results come from one checkpoint and one seed, at T4/fp16. The
  chunking pilot used 21 + 15 selected clips.

## 9. Recommendation

**Stop tuning the two failed interventions on these same 128 clips.** Every further threshold or chunk-count rule
picked on these clips would be fitted to them. The pre-registered results should stand as reported.

The next most defensible directions are ranked below. The cost and value ratings are **judgment calls**, not measured
results.

| Rank | Direction | Engineering cost | Research value | Product value | New GPU training? |
|---|---|---|---|---|---|
| 1 | **Confidence-aware fallback / failure detection**: flag outputs that are probably loops, hallucinations or cut short (from signals such as repetition, length vs input duration, decoder scores), and abstain or fall back | **Low–medium** | Medium | **High**: limits the visible damage of the current failure modes regardless of their cause | **No** (inference only; needs held-out clips to validate thresholds) |
| 2 | **Content-aware segmentation / chunk-count prediction**: choose the number of chunks from a signal available at inference time (e.g. signing activity, a small predictor), not from frame count | Medium | Medium–high: directly targets the T4 failure | Medium–high, if it generalises | **No full retrain**; a small auxiliary predictor at most; **requires held-out data** not used in the pilot |
| 3 | **Controlled fine-tune with a longer target length** (e.g. `max_length` 50 → 100+, everything else fixed), to test the 50-token hypothesis directly | **High** | **High**: a direct test of *why* the model stops early | Uncertain until tested | **Yes** |

Suggested order: start with (1), because it is cheap and useful whatever causes the errors. Pursue (2) only with a
fresh held-out split. Run (3) when the team wants a causal answer on early stopping and GPU training time is available.

## 10. Manager TL;DR

We studied where the existing, publicly released Uni-Sign system fails on our frozen 128-clip How2Sign benchmark. No
new model was built. Our earlier low score was mostly caused by how we cut and cropped the video. Fixing timing and
crop recovers about 86 % of the gap, while our pose extractor accounts for only a small remainder (T4/fp16, not an
exact bf16 reproduction). With correct inputs, the main remaining failures are fluent-but-wrong output, occasional
repetition loops, and outputs that stop too early on long sentences. These labels are automated and have not been
verified by an ASL reviewer. Raising the decoding length limit changed nothing, so that is not the cause. Cleaning up
repetitions with a text rule failed our safety checks. Splitting long videos into chunks largely fixes the short
outputs on long sentences (a partial, mechanism-level positive), but it over-generates on long videos with little content, so it fails our pre-registered
criteria. Our recommendation is to stop tuning these two ideas on the same clips. Next we would build cheap failure
detection, then test smarter segmentation on held-out data, with a training-length fine-tune as the option if we want
to test the 50-token hypothesis directly.

| Experiment | Question | Result | Decision |
|---|---|---|---|
| P0-12 preprocessing gap | Is the old 5.39 gap from the pose extractor or the input preparation? | Timing / crop recovers ≈ 86 % of the BLEU-4 gap; extractor adds +0.52 | Fix input preparation; extractor is not the priority |
| Error taxonomy (weak labels) | Where does Uni-Sign fail with correct inputs? | Mostly fluent-but-wrong; loops, weak rare-name recovery, missing negation/question cues, short long-sentence outputs | Treat as hypotheses; ASL verification still open |
| Decode-length cap (R100/150/256) | Does `max_new_tokens = 100` cause short long outputs? | 126/128 identical; BLEU-4 ≈ 9.13 throughout; outputs end by EOS | Hypothesis rejected |
| Repetition cleanup (rule v1) | Can a text rule safely remove loops? | Failed both pre-metric guards; covered 3/18 loops | Closed as negative; at most a product guardrail |
| Chunked decoding (S1/S2/S3) | Can chunking recover long outputs without harming other clips? | Targets: chrF +10.4, length 0.64 → 1.16. Controls: length ≈ 1.58, WER +42. All arms fail T4 | Failed intervention; partial mechanism-positive; no re-tuning on these clips |
