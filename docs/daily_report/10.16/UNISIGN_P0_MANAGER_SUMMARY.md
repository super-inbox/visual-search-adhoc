# Uni-Sign P0 Summary

**Date:** 2026-10-16 · **Branch:** `baobao/visual-production-research-2026-10-05`
**System under study:** the publicly released Uni-Sign pose-only How2Sign checkpoint (`how2sign_pose_only_slt.pth`).
No new translation model was built or retrained in any of this work.

Every number below comes from these committed reports:

| Work | Report |
|---|---|
| P0-12, error analysis, decode length, repetition cleanup, chunking | `../10.15/UNISIGN_FAILURE_ANALYSIS_SUMMARY.md` and the reports it links |
| P0-14 representation probe | `../10.15/asl-unisign-representation-probe/FULL_RUN_REPORT.md` |
| P0-15 high-precision fusion | `asl-unisign-high-precision-fusion/P0_15_RESULTS.md` |

## 1. Executive summary

- **P0-12 is not a new model architecture.** It is a controlled diagnosis of the existing Uni-Sign system. It found
  that our earlier low score came mostly from video timing and cropping, and fixing those closed most (≈ 86 %) of
  the gap to the official pipeline.
- With correct inputs, the error analysis and three cheap inference-time fixes left one question open: **does
  Uni-Sign's internal representation contain useful information that its decoder sometimes fails to put into the
  translation?**
- **P0-14 found partial support for that.** Uni-Sign's mT5 encoder states carry concept information that the final
  translation sometimes omits.
- **P0-15 tested a lightweight verifier to turn that signal into safe additions.** The current signals are **not
  reliable enough for safe fusion**: under the pre-registered safety rule, the verifier added nothing.
- **Bottom line:** the direction is promising at the representation level. **We have not improved Uni-Sign, and we
  have not improved sentence translation quality.**

## 2. P0-12: what it is and how it differs from Uni-Sign

- **Uni-Sign** is the pretrained, publicly released pose-based sign-language translation model. It is the system
  under study.
- **P0-12 did not propose a new backbone or a competing model.** It held the Uni-Sign checkpoint, the clips, the
  references and the evaluation code fixed. It changed only the pose source and the input preparation (timing, crop,
  coordinate normalization), to diagnose why our pipeline scored far below the official one.

Results on the frozen 128-clip How2Sign subset:

| Condition | Pose source | Timing / crop | BLEU-4 |
|---|---|---|---|
| A_official | official poses | official timing + signer crop | **9.13** |
| B_ours_5p39 | our extractor | original timestamps, full frame | **5.47** |
| B_aspect | our extractor | as B, with aspect / coordinate fix | **5.80** |
| C_ours_on_official_crop | our extractor | official timing + signer crop | **8.61** |

- Timing, crop and preprocessing (B → C) recovered **≈ 86 % (85.7 %) of the BLEU-4 gap**. ROUGE (87 %) and BLEURT
  (75 %) agree.
- The remaining pose-extractor gap is small: **+0.52 BLEU-4** once timing and crop are matched.
- **Caveats:**
  - **T4 / fp16, not the official bf16.** A_official scores 9.13 here vs 9.59 for the authors' released predictions.
    The contrasts between conditions are the result; the absolute values are not.
  - Single run per condition, no confidence intervals.
  - The timing and crop effects cannot be separated.

**Conclusion:** P0-12 largely closed the pipeline and preprocessing discrepancy (≈ 86 % of the BLEU-4 gap). It is
a diagnosis, **not a competing model** to Uni-Sign.

## 3. Error analysis: what we learned

Automated first pass on the 128 clips with correct inputs. **All labels are heuristic or weak labels. None was
verified against the videos by an ASL-fluent reviewer.**

| Primary error type (A_official, one per clip) | Clips |
|---|---|
| Substitution / fluent-but-wrong | **67** |
| Hallucination candidate | 26 |
| Repetition loop | 18 |
| Omission | 13 |
| Over-generation | 4 |

- **Fluent-but-wrong output is the most common failure.** Hallucination candidates and repetition loops also occur.
- **Long-reference outputs often stop early.** Outputs for references of ≥ 35 words end on their own, at a median
  of about 33 words.
- **Rare names and negation (weak-label, exploratory):**
  - only 2 of 21 rare names or acronyms appear in the output;
  - 7 of 13 references with a negation get an output without one.

  These are English-surface checks with small samples, not verified ASL findings.
- **No taxonomy category survived** length matching and multiple-comparison (Bonferroni) correction.
- **ASL-specific categories were not manually verified.** Fingerspelling, non-manual negation and question marking
  remain unverified.

Three lightweight inference-time interventions were tested. Each one's rules were frozen before any metric was
computed.

| Intervention | Result |
|---|---|
| Raise the decode length cap (100 → 150 → 256 tokens) | **Rejected.** 126/128 outputs identical; long outputs end on their own (EOS), not at the cap |
| Repetition text cleanup | **Rejected.** Failed both pre-metric safety guards; covered only 3 of 18 loops |
| Deterministic frame-count chunking | **Partial mechanism, failed as an intervention.** It largely fixes short outputs on long-reference clips (chrF +10.4), but it over-generates on control clips (length ≈ 1.58×, WER +42) |

## 4. P0-14: representation probing for fusion

**Question:** do Uni-Sign's internal representations expose concept information better than raw pose? Simple linear
probes were trained on frozen features. The test was 2,209 clean How2Sign test clips and 24 lexical concepts
(Tier L).

| Representation | Concept macro-F1 | Macro-AUROC |
|---|---|---|
| Raw RTMPose pose | 0.125 | 0.750 |
| Uni-Sign Fsign (pose features) | 0.256 | 0.834 |
| **Uni-Sign mT5 encoder states** | **0.416** | **0.886** |
| Uni-Sign's own translation (for reference) | **0.548** | – |

- **mT5 with only 10 % of the labels (F1 0.338) beats raw pose and Fsign trained on 100 %.**
- **The translation misses 498 of 1,032 positive concept mentions.**
  - At its frozen threshold, the mT5 probe recovers **90** of them.
  - The cost is 581 wrong additions.
- On the clips where the translation omits a concept, the mT5 probe still ranks true over false at **AUROC 0.78**.

**Interpretation:** mT5 encoder states contain complementary lexical signal that does not always appear in the final
translation.

**Caveats:**
- **Formal verdict: PARTIAL SUPPORT.** The shuffled-label sanity control (S1) narrowly failed: 0.5302 against an
  upper bound of 0.53. The rule was not changed to force a pass.
- **Uni-Sign's own translation remains the strongest standalone concept detector** (F1 0.548 vs 0.416).
- Naively adding probe detections to the translation **lowers** F1 (−6.2 points for mT5).
- **This does not show any translation improvement.**

## 5. P0-15: high-precision fusion

**Question:** can the mT5 specialist signal be filtered into safe additions, that is, concepts added to the
translation's output that are more often right than wrong, without hurting precision?

| Result (development half) | Value |
|---|---|
| Naive union (B) | 331 additions, 50 correct, **net −231** |
| Ranking quality: learned verifier (D) vs raw mT5 margin (C) | AP **0.110** vs **0.094** |
| Correct in the top 20 | verifier **11/20**, raw margin **7/20** |
| Best Wilson 90 % lower bound on add-precision (required ≥ 0.50) | C **0.244**, D **0.393**: both below 0.50 |
| Additions under the frozen rule | **none**: both C and D abstain, and so do both controls |
| **Verdict** | **NOT SUPPORTED** |

- **The held-out final set was never opened.** No final labels were read and no final metric exists.
- The verdict rests entirely on the development half and the pre-registered rule.
- The final split stays sealed and can be reused once by a future experiment.
- **No sentence-translation improvement is claimed.** P0-15 measures concept-set reliability only; no sentence was
  changed.

## 6. What this means for the fusion architecture

**Supported:**
- Uni-Sign's internal states, especially the mT5 encoder states, contain useful complementary semantic
  information.
- A specialist branch on top of Uni-Sign is technically plausible: the signal exists and is cheap to read out.

**Not yet supported:**
- Current specialist predictions are not precise enough to fuse directly into the output.
- Naive fusion hurts: it adds far more wrong concepts than right ones.
- The current lightweight verifier ranks candidates better, but it cannot yet make safe corrections.

**Recommended direction, if the work continues later** (a design hypothesis, **not an implemented or validated
system**):

```
Uni-Sign translation
  + mT5 encoder-state specialist signal
  + a stronger reliability / confidence signal (e.g. decoder confidence)
  → verifier
  → correction / fusion
```

**The current fusion architecture has not improved sentence translation.** No fused sentence has been produced or
measured.

## 7. Current recommendation

**Pause here.**
- Do not keep tuning the same fusion rule on the current data. Any further rule picked on these clips would be
  fitted to them.
- Keep the sealed P0-15 final set untouched.
- If the project resumes, the next logical signal to test is **decoder confidence or sequence score**, or another
  stronger reliability feature. It is untested, and it may not be enough. It would be specified in a new frozen plan
  before the sealed set is opened.
- **No further P0 is required before reporting the current findings.**

## 8. Manager TL;DR

P0-12 is not a new model but a controlled diagnosis of the existing Uni-Sign system, and it showed that our earlier
low score came mostly from video timing and cropping. Fixing those recovered about 86 % of the gap (T4/fp16, not an
exact reproduction). With correct inputs, Uni-Sign's main failures are fluent-but-wrong output, repetition loops and
early stopping on long sentences, and the simple inference-time fixes we tried did not solve them safely. We then
asked whether Uni-Sign's internal states know more than its translation says. P0-14 found partial support: the mT5
encoder states carry concept information the translation sometimes drops, although Uni-Sign's own translation is
still the best stand-alone concept detector. P0-15 tested a lightweight verifier for adding those concepts safely,
and the current signals are not reliable enough: under our pre-registered safety rule it added nothing. Our
recommendation is to pause here. The direction is promising at the representation level, but we have not improved
Uni-Sign or its sentence translations.

| Work | Question | Result | Decision |
|---|---|---|---|
| P0-12 | Is the old 5.39 BLEU-4 gap from our pose extractor or our input preparation? | Timing / crop recovers ≈ 86 % of the gap (5.47 → 8.61 vs 9.13); extractor adds +0.52. T4/fp16 | Diagnosis complete; fix input preparation. Not a new model |
| Error analysis | Where does Uni-Sign fail with correct inputs? | Mostly fluent-but-wrong; hallucinations, loops, early stopping on long sentences; no category survives correction; not ASL-verified | Treat as hypotheses |
| Decode length | Does the 100-token cap cause short outputs? | 126/128 outputs identical; outputs end by EOS | Rejected |
| Repetition cleanup | Can a text rule safely remove loops? | Failed both safety guards; covered 3/18 loops | Rejected |
| Chunking | Can chunking fix long outputs without harming others? | Long-reference chrF +10.4, but over-generates on controls (length ≈ 1.58×, WER +42) | Failed as an intervention; partial mechanism only |
| P0-14 | Do Uni-Sign's internal states expose concepts better than raw pose? | mT5 F1 0.416 vs Fsign 0.256 vs raw 0.125; AUROC 0.78 on translation misses; translation still best (0.548) | **PARTIAL SUPPORT** (S1 narrowly failed) |
| P0-15 | Can a verifier turn that signal into safe additions? | Naive union net −231; verifier AP 0.110 vs 0.094; best lower bound 0.393 < 0.50; nothing added | **NOT SUPPORTED** at dev stage; final set sealed |
