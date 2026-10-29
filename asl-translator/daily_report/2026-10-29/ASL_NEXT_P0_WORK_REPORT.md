# ASL NEXT_P0 work report, 2026-10-29

**Scope:** the work done after the 2026-10-28 [PROGRESS_REVIEW.md](../2026-10-28/PROGRESS_REVIEW.md) and
`NEXT_P0_PLAN.md` (commit `292e15ec`, branch `origin/codex/asl-next-p0-20261028`).
- Branch: `baobao/visual-production-research-2026-10-05`. Five commits, all pushed (§10).
- This report is a summary. Every number below is taken from the committed report linked in its section; nothing was
  re-run for this report.

## 1. Executive summary

All currently executable internal NEXT_P0 work is substantially complete. The project is not complete: the
human-label-dependent part of P0-1 is still pending.

- **No production code was changed or deployed** in any of this work.
- **R03 reliability (review item 2):** root cause found offline. A malformed Gemini batch is silently dropped and the
  partial result looks like a full success. An explicit PARTIAL status and a failed-batch-only retry are proposed and
  regression-tested offline.
- **5 unresolved provenance rows (review item 3):** each source time is now supported by an AI visual anchor. The frozen
  automatic status stays `UNRESOLVED`.
- **P0-3:** **KEEP** the frozen loop trigger; **STOP** the current `no_repeat_ngram_size=3` regeneration method.
- **P0-2:** frozen verdict **C / PAUSE**. Round 2 is not justified.
- **P0-1 Stage A:** the infrastructure is prepared (baselines, decoder, blind package, metrics, gates). The recognition
  evaluation itself has **not** been run and is blocked on blind human ASL labels. Stage A is not complete.
- **Blocker:** there is currently no available ASL-fluent reviewer (§7).

## 2. Boss request → what was done

| Request (source) | Status | Where |
|---|---|---|
| R03 partial-transcription reliability (review item 2; plan "confirmation rule" 5) | **COMPLETE** | below, and [R03 report](../2026-10-28/R03_PARTIAL_TRANSCRIPTION_REGRESSION.md) |
| Verify the 5 unanchored inputs (review item 3) | **COMPLETE as supporting evidence** | §3 |
| P0-3 conditional anti-repeat (plan P0-3) | **COMPLETE: STOP current regeneration** | §4 |
| P0-2 OpenAI same-input Round 1 (plan P0-2) | **COMPLETE: C / PAUSE** | §5 |
| P0-1 Stage A preparation (plan P0-1; review item 1) | **PREPARATION COMPLETE; EVALUATION PENDING HUMAN LABELS** | §6, §7 |
| Specialist-model replacement on an independent sample with human review and deployment inputs (review item 4) | **NOT STARTED**; it needs human review | — |

**Cost of this round:**
- **P0-2 Round 1** used 58 benchmark inference calls (29 OpenAI + 29 Gemini), at an estimated list-price cost of about
  $0.67.
- **Before the benchmark**, two more OpenAI requests were made, neither of them benchmark inference:
  - one model-metadata lookup (`models.retrieve`), a metadata/access request;
  - one capability smoke test on a synthetic image (not benchmark data), costing about $0.0005.
- **R03, provenance, P0-3 and P0-1** made no API calls. P0-1 ran only a local CPU forward pass on synthetic frames.

### A. R03 partial-transcription reliability: COMPLETE

Offline replay of the saved 10/27 production response through production's real code path (curify-studio `4220e03c`,
loaded read-only). No model call.

**What happens today:**
- R03 was sent as **2 Gemini batches** (24 + 6 frames).
- Batch 0 returned JSON with one missing `}`. The reply was otherwise complete (`STOP`, 4 segments). The parse failed.
- Production caught the parse error together with transport errors, then discarded the note because batch 1 produced a
  segment.
- **Production returned only "I know now."** with `error=None`, and the pipeline treated it as a normal completed
  transcript.
- **24 of the 30 frame inputs** (3.2–12.8 s of the clip) were omitted, and no partial flag was set.

**What is proposed (design only):**
- An explicit **`partial`** video status: at least 1 batch is valid and at least 1 batch failed. `success` is unreachable
  while any batch has failed.
- **Retry the failed batch only**, with the same frames, prompt, model and config. Limits: 1 retry per batch, at most 2
  per video. Quota and spend-cap errors are never retried.
- Expected cost for R03: +1 call, about +10.5k tokens (+2.3 % of the 45-case run's tokens), about +17 s.
- The reference policy passes 14 offline regression fixtures.

**Score:** the current 45-case production score is unchanged (corpus chrF 9.27). It already scores what production
returned, and R03 was already marked PARTIAL there.

**Production code was NOT changed.**

**Main conclusion: a format failure must never count as a full success.** Today it cannot be told apart from one.

## 3. Provenance follow-up: COMPLETE AS SUPPORTING EVIDENCE

Rows: **R26 A, R28 A, R35 A, R42 A, R32 B.**

| Field | Value for all 5 |
|---|---|
| `provenance_status_auto` | **`UNRESOLVED`** (frozen; not overwritten) |
| Additional evidence | **`SOURCE_TIME_SUPPORTED_BY_AI_VISUAL_ANCHOR`** |

**What this evidence is:** additional visual support for where each input sits in source time. It is **not** human
verification, **not** automatic verification, and **not** fully verified provenance.

**Limitations:**
- **Judge:** the AI assistant was the only visual judge. There was no second rater.
- **Blinding to expected timing:**
  - **Fully blind:** R28 and R42.
  - **Partially blind:** R26, R35 and R32. Their timing had been seen earlier in the session.
- **R26** also had incidental reference-text exposure (one sentence, not used).
- **A rows (R26, R28, R35, R42):** the source-time location is supported, but the raw-frame **crop-box position remains
  unknown**.
- **R32 B:** the AI anchor agrees with the original annotation, but the frozen automatic criterion still fails
  (motion r = 0.896 < 0.90) and is not reinterpreted.
- No thresholds were changed, and the 10/27 manifest is unmodified.

**Main conclusion:** the input hashes are reproducible, and additional AI visual evidence supports the source-time
placement, but the frozen automatic provenance status remains `UNRESOLVED`. Human or second-rater confirmation would be
needed before calling these rows human-verified.

Detail: [UNRESOLVED_SOURCE_POSITION_VERIFICATION.md](../2026-10-28/UNRESOLVED_SOURCE_POSITION_VERIFICATION.md).

## 4. P0-3 conditional anti-repeat: COMPLETE, STOP CURRENT REGENERATION

Descriptive only, on the 45-case dev set (A_official). It was built from saved Task 1 outputs, with no new decode and
no API call.

**Trigger (frozen, not tuned):**
- Word 3-gram repetition ratio **≥ 0.15** on the control output.
- It fired on **9 of 45** cases, which is **exactly the existing Task 1 loop set**.

**Conditional arm:**
- Triggered cases use the saved `no_repeat_ngram_size=3` treatment.
- Untriggered cases keep the original control output byte for byte.

**Results:**
- Loops: **9 → 0**.
- All **36 untriggered outputs are byte-identical**, so the global arm's 15 non-loop changes disappear.
- **R35 is protected**: "Hi, I'm Colin" is kept, and so are the other legitimate `I'm` repetitions outside loops.
- The conditional arm changed **9** outputs; the global arm changed **24**.

| Arm | chrF | BLEU-4 | WER | Length ratio |
|---|---|---|---|---|
| Control | 23.76 | 5.72 | 95.44 | 1.000 |
| Conditional | 24.93 | 5.83 | 92.82 | 0.965 |
| Global (Task 1) | 25.49 | 5.94 | 92.91 | 0.971 |

**Critical failure:**
- **7 of the 9 triggered outputs changed text *before* the loop began.** `no_repeat_ngram_size` re-decodes the whole
  sentence; it does not repair the loop locally.
- R42 regresses by −5.97 sentence chrF. R20 (−2.70) and R01 (−1.64) also regress.

**Conclusion: KEEP the frozen trigger. STOP the current `no_repeat_ngram_size=3` regeneration method.**

The automatic metric increase is **not** a semantic translation-quality improvement. Loop removal is a reliability
change, and the replacement text has not been reviewed.

Detail: [P0_3_CONDITIONAL_ANTI_REPEAT_RESULT.md](../2026-10-28/P0_3_CONDITIONAL_ANTI_REPEAT_RESULT.md).

## 5. P0-2 OpenAI vs Gemini, same input, Round 1: COMPLETE, C / PAUSE

**Pre-registered design:**
- **Data:** a 24-clip independent comparison subset from outside the 45-case dev set. It is **not a clean holdout**:
  every clip has prior research exposure.
- **Frames:** 656 frozen frames.
- **Calls:** 29 per provider.
- **Same input for both providers:**
  - the same frame timestamps;
  - the same JPEG bytes;
  - the same prompt semantics;
  - the same batch boundaries.
- **Failures:** no retries, and every failure stays in the denominator.

**Models:**
- OpenAI `gpt-6.1-sol`;
- Gemini `gemini-2.5-flash` (the production configuration).

**Status counts:**

| | success | no_signing | partial | parse failure | transport failure |
|---|---|---|---|---|---|
| OpenAI | 9 | **15** | 0 | 0 | 0 |
| Gemini | 24 | 0 | 0 | 0 | 0 |

**Automatic metrics:**

| | chrF | BLEU-4 | WER | Length ratio |
|---|---|---|---|---|
| Gemini | 13.21 | 0.50 | 94.74 | 0.418 |
| OpenAI | 1.36 | 0.00 | 100.00 | 0.053 |

**Paired comparison (sentence chrF, OpenAI − Gemini):**
- mean −9.72, median −10.06;
- wins / losses / ties: 1 / 22 / 1;
- bootstrap 95 % CI: **[−12.30, −7.20]**;
- signer-cluster CI: [−10.46, −8.82];
- regressions (≥ 10 chrF): **12**; gains: **0**.

**Latency and cost:**
- Median latency: OpenAI 22.9 s, Gemini 11.2 s.
- Estimated list-price cost: OpenAI about $0.45, Gemini about $0.22.

**Frozen gates:**

| Gate | Result |
|---|---|
| Reliability | **FAIL** (15 vs 0 non-answers) |
| Quality | **FAIL** |
| Safety | **FAIL** (12 regressions vs 0 gains) |
| Cost/latency | **FAIL**, narrowly on latency (22.9 s vs a limit of 22.4 s); cost passes |

**Final frozen verdict: C, PAUSE. Round 2 is not justified.**

**Interpretation:**
- OpenAI's main behaviour was abstention: valid replies saying it could not read the signing. Production's prompt asks
  for exactly that when unsure.
- These automatic results do not establish whether those abstentions are appropriate caution or a capability
  limitation.
- This is **not** a claim that OpenAI cannot understand ASL in general: one model, one prompt, one reasoning setting,
  24 clips.
- This is **not** a claim that Gemini's outputs are semantically correct. Its absolute level is also low, and no blind
  human review was done.
- Uni-Sign appears in the detailed report as **not input-matched / orientation only**. It supports no same-input
  comparison.

Detail: [P0_2_OPENAI_VS_GEMINI_ROUND1_RESULT.md](P0_2_OPENAI_VS_GEMINI_ROUND1_RESULT.md).
Pre-registration: [P0_2_OPENAI_SAME_INPUT_PREREGISTRATION.md](../2026-10-28/P0_2_OPENAI_SAME_INPUT_PREREGISTRATION.md).

## 6. P0-1 Stage A preparation

**Status: PREPARATION COMPLETE. EVALUATION PENDING HUMAN LABELS.**

**Keypoint baseline: OpenFS.**
- Commit `0d6fa3fa`; keypoint-only (21 hand points × 2D); existing checkpoint frozen (`c8e4c227…`).
- It runs locally and deterministically.
- Historical strings reproduce on **10 of 18** windows, because of platform and encoding sensitivity in the landmarks.

**RGB candidate: HandReader_RGB.**
- Repo commit `77d390d0`; RGB-only; checkpoint `chicago+/rgb/best.pt`.
- The weights load strictly and a CPU forward pass works (synthetic input only), so it is **technically viable**.
- **Its accuracy on How2Sign is unknown.**
- **Licence:** the code is Apache-2.0. The checkpoint was trained on ChicagoFSWild+, and its use remains subject to the
  relevant dataset and checkpoint terms.
- **Crop-source shift:** the upstream repo has no hand-crop code, so our MediaPipe crops will differ from its training
  crops. This will be reported as a crop-source shift.

**Decoder, frozen before any Stage A evaluation:**
- **Primary:** CTC beam search, beam size 5, no language model.
- **Greedy:** a secondary diagnostic only.
- This decoder choice was frozen before any Stage A evaluation output was produced, and therefore was not selected based
  on benchmark accuracy.

**Reviewer package:**
- **Items:** 36 blind clips, `FSA-001` … `FSA-036`, chosen by a letter-free, input-side hand-motion screen.
- **Testing:** the package is built, and the review page passed a browser export/import round trip with dummy labels,
  which were then cleared. In-browser video playback was not checked; every clip passed a full ffmpeg decode instead.
- **What the reviewer does not see:** no references, no model predictions, no target letters and no selection tiers.
  The automated leakage scan found 0 hits.
- **No Stage A recognizer has been run on these 36 items.**

**Already frozen in the pre-registration:**
- **Metrics:** CER, whole-word exact accuracy, abstain rate, and false-positive rate on negatives.
- **Confidence intervals:** bootstrap, clustered by source video.
- **Acceptance gates:** G0 validity, G1 CER, G2 word accuracy, G3 false positives, G4 breadth, and a readability check.

**No Stage A accuracy number is reported, because none exists.**

Detail: [P0_1_STAGE_A_PREPARATION.md](P0_1_STAGE_A_PREPARATION.md),
[P0_1_STAGE_A_REVIEWER_PACKAGE_AND_RGB_FEASIBILITY.md](P0_1_STAGE_A_REVIEWER_PACKAGE_AND_RGB_FEASIBILITY.md).

## 7. Current blocker

> **There is currently no available ASL-fluent human reviewer for the 36-item blind Step 1 package.**

**What cannot be obtained without a reviewer:**
- human-confirmed fingerspelling presence;
- human-confirmed spans;
- human-confirmed letters.

**What we should NOT do without those labels:**
- run the final Stage A comparison;
- report CER;
- report whole-word accuracy;
- decide whether RGB adds value;
- proceed to Stage B or Stage C (fusion).

**The package is ready to send as soon as an ASL-fluent reviewer is available.**

**Minimum label gate (G0):** at least **12 positive spans** and at least **8 negatives**. If the labels fall short,
the pre-registered expansion order applies: label the remaining clips by screen score, in batches of 8 (6 by score, 2
by hash). Going beyond the 61-clip pool would need new keypoints and a separate approval.

## 8. Next actions

| Task | Status | Next action |
|---|---|---|
| R03 reliability | COMPLETE | A production engineering fix (PARTIAL status plus failed-batch retry) can be considered separately |
| 5 provenance rows | COMPLETE as supporting AI evidence | Human or second-rater confirmation, only if stronger provenance is required |
| P0-3 | COMPLETE / STOP repair | Keep the trigger; do not continue the current regeneration |
| P0-2 | COMPLETE / PAUSE | Do not run Round 2, and do not tune OpenAI on this subset |
| P0-1 Stage A preparation | COMPLETE | Wait for an ASL reviewer |
| P0-1 Stage A evaluation | **BLOCKED** | Needs blind human labels |
| Stage B / C | NOT STARTED | Consider only after Stage A passes |

## 9. What I need

The remaining blocker is access to an ASL-fluent reviewer for the prepared 36-item blind Step 1 package. If there is an
internal or external reviewer we can use, I can send the package immediately.

Otherwise, all currently executable NEXT_P0 internal work is complete. I recommend pausing the Stage A evaluation rather
than substituting model-generated labels.

## 10. Commits and main reports

| Commit | Topic | Main report |
|---|---|---|
| `efef365c` | R03 partial transcription | [R03_PARTIAL_TRANSCRIPTION_REGRESSION.md](../2026-10-28/R03_PARTIAL_TRANSCRIPTION_REGRESSION.md) |
| `e4e987ae` | Source-time AI visual anchor evidence | [UNRESOLVED_SOURCE_POSITION_VERIFICATION.md](../2026-10-28/UNRESOLVED_SOURCE_POSITION_VERIFICATION.md) |
| `8abc1533` | Conditional anti-repeat | [P0_3_CONDITIONAL_ANTI_REPEAT_RESULT.md](../2026-10-28/P0_3_CONDITIONAL_ANTI_REPEAT_RESULT.md) |
| `a0200c9d` | OpenAI vs Gemini Round 1 | [P0_2_OPENAI_VS_GEMINI_ROUND1_RESULT.md](P0_2_OPENAI_VS_GEMINI_ROUND1_RESULT.md) |
| `63c1f395` | P0-1 Stage A preparation | [P0_1_STAGE_A_PREPARATION.md](P0_1_STAGE_A_PREPARATION.md), [P0_1_STAGE_A_REVIEWER_PACKAGE_AND_RGB_FEASIBILITY.md](P0_1_STAGE_A_REVIEWER_PACKAGE_AND_RGB_FEASIBILITY.md) |
