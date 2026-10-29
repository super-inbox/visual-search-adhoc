# P0-3: conditional anti-repeat, descriptive stage

**Status:** NEXT_P0_PLAN P0-3, first stage. Descriptive only, on the 45-case **dev set** (A_official).
- Built entirely from the **saved** Task 1 outputs: no new decode, no Gemini, OpenAI or other model call.
- No production change.
- This does **not** establish a translation-quality improvement.

Script: [`p0_3_conditional_anti_repeat.py`](../../experiments/p0-2026-10-28/p0_3_conditional_anti_repeat.py).
Results: [`p0_3_conditional_anti_repeat.json`](../../experiments/p0-2026-10-28/results/p0_3_conditional_anti_repeat.json).
Inputs:
- Task 1 decode `repetition_paired_decode_local_arm64.json` (sha256 `9de31696…`, checked);
- P0-A canonical T: control token ids equal on 45/45;
- 10.13 references, used for scoring only.

## Bottom line

**Verdict: KEEP the frozen loop trigger. STOP the current `no_repeat_ngram_size=3` regeneration method.**

- **The gate works.**
  - It fires on exactly the 9 Task 1 loop cases.
  - All 36 untriggered outputs stay byte-identical, so the global arm's **15 non-loop changes disappear**.
  - Every legitimate `I'm` repetition outside a loop is protected, **R35 included**.
- **The repair inside triggered cases is not clean.**
  - `no_repeat_ngram_size=3` re-decodes the whole sentence. In 7 of the 9 triggered cases it changes text that comes
    **before** the loop starts.
  - R42 drops by −5.97 sentence chrF.
  - Therefore the current regeneration method is not a safe local loop repair.

Automatic metrics improved descriptively, but semantic correctness was not established. Loop removal is a
decoding/reliability improvement and is not by itself a translation-accuracy gain. Translation-quality improvement
requires recovered content without semantic damage, and nothing here shows that.

## 1. Pre-registered trigger

Fixed before any conditional output or metric was computed. It is the frozen P0_PROTOCOL_FREEZE §1.4 `loop_out`,
unchanged:

| Item | Value |
|---|---|
| Input | the **control output** only (no reference, no model score) |
| Normalization | lowercase |
| Tokenizer | regex `[a-z0-9']+` |
| Count | word 3-grams over consecutive tokens; ratio = 1 − distinct / total |
| Threshold | **fire if ratio ≥ 0.15**; no 3-grams → no fire |
| Arm | fired → saved Task 1 treatment (`no_repeat_ngram_size=3`, beam 4, max 100 new tokens); not fired → control byte for byte |

The threshold was not changed or tuned. Per-case ratios and decisions are in the JSON.

**Negative controls**, also fixed in advance:
- every control output with two or more `I'm` (regex `\bI['’]m\b`);
- R35.

## 2. Trigger behaviour

- **Fired:** 9/45 (rate 0.20): R01, R03, R11, R18, R20, R23, R36, R39, R42. This is exactly the Task 1 loop set.
- **Existing Task 1 loop diagnostics on the fired cases:**
  - 7 of the 9 also carry the 10.13 repetition flag (R03, R11, R18, R20, R36, R39, R42).
  - R36 hit the 100-token limit.
  - R01 and R23 fire on `loop_out` only. R23 is the closest to the threshold, at ratio 0.194.
- **True abnormal loops:** none can be confirmed beyond these automatic diagnostics. No human loop labels exist.

**Legitimate-repetition negatives** (control outputs with two or more `I'm`, plus R35):

| Case | `I'm` in control | Trigger | Conditional changed? | `I'm` after conditional | Global arm |
|---|---|---|---|---|---|
| R02 | 2 | no (ratio 0) | **no** | 2 | changed, 2→1 |
| R04 | 2 | no | **no** | 2 | changed, 2→1 |
| R05 | 2 | no | **no** | 2 | changed, 2→1 |
| R13 | 2 | no | **no** | 2 | changed, 2→1 |
| **R35** | 2 | no | **no** | 2 | changed, 2→1 ("Hi, I'm Colin" lost) |
| R03 | 3 | **yes** (0.458) | yes | 0 | same as conditional |
| R23 | 3 | **yes** (0.194) | yes | 1 | same as conditional |

- **Not triggered:** all 5 of these negatives are protected and byte-identical.
- **Triggered:** R03 and R23 contain `I'm` inside the triggered text and lose 3 and 2 of them.
  - In R03 the repeats are part of the loop.
  - In R23 the repeated clause is a near-threshold case. Whether it is a loop or a legitimate restatement cannot be
    decided without a human label.

## 3. Loop outcome

| | Loops (`loop_out`) | 10.13 flag |
|---|---|---|
| Control | 9 | 7 |
| **Conditional** | **0** | 0 |
| Global `no_repeat_ngram_size=3` (Task 1) | 0 | 0 |

All 9 triggered loops are eliminated and none remain.

## 4. Automatic metrics (45 cases, P0-A §1.6 functions)

| Arm | chrF | BLEU-4 | WER | mean len ratio | outputs changed | non-loop outputs changed |
|---|---|---|---|---|---|---|
| Control | 23.7634 | 5.7246 | 95.4369 | 0.9997 | — | — |
| **Conditional** | **24.9343** (+1.17) | 5.8315 (+0.11) | 92.8155 (−2.62) | 0.9649 | **9** | **0** |
| Global (Task 1) | 25.4893 (+1.73) | 5.9436 (+0.22) | 92.9126 (−2.52) | 0.9714 | 24 | 15 |

**Why the global arm scores higher:** about 0.56 chrF of its corpus gain comes from changing the 15 outputs that never
looped. Their meaning is unverified, and they include the R35 damage. The conditional arm gives that up by design.

**Per triggered case** (sentence chrF / WER delta, conditional − control; texts withheld under the P0-A convention):

| Case | Role | Ratio | ΔchrF | ΔWER | Words | Text before the loop changed? | Task 1 bin |
|---|---|---|---|---|---|---|---|
| R01 | focus | 0.531 | −1.64 | −55.6 | 34→23 | **yes** | small change |
| R03 | — | 0.458 | +6.80 | +2.4 | 26→36 | **yes** | improve candidate |
| R11 | — | 0.867 | +8.81 | +9.1 | 32→35 | **yes** | improve candidate |
| R18 | focus | 0.333 | +5.31 | −23.1 | 20→17 | no | improve candidate |
| R20 | ordinary control | 0.263 | −2.70 | +1.8 | 40→39 | **yes** | small change |
| R23 | — | 0.194 | +0.35 | +1.3 | 33→37 | **yes** | small change |
| R36 | — | 0.818 | +10.56 | −7.2 | 35→34 | **yes** | improve candidate |
| R39 | — | 0.625 | +2.27 | −63.2 | 34→20 | no | small change |
| R42 | focus | 0.385 | **−5.97** | −15.4 | 15→10 | **yes** | **regress candidate** |

Most of the WER gain comes from cutting looping text (R01, R39). An automatic chrF gain on a rewritten sentence is not
a recovered meaning: the replacement continuations are new model text and have not been reviewed.

## 5. Damage

- **Non-loop outputs changed:** **0** (global arm: 15). The gate removes the global side effect entirely.
- **Legitimate repetitions lost outside loops:** 0 (global arm: 5 cases lose one `I'm`, R35 included).
- **R35:** protected. Its control output, including "Hi, I'm Colin", is kept byte for byte.
- **Inside triggered cases:**
  - **7/9 have text altered before the loop begins**: R01, R03, R11, R20, R23, R36, R42. Measure: the common word
    prefix with the control ends before the first repeated 3-gram. This proxy was defined after reading the triggered
    texts and is descriptive only.
  - Only R18 and R39 keep their pre-loop text, so they are the only clean "cut the loop" repairs.
  - The cause: `no_repeat_ngram_size` changes beam search from the first token. It is a whole-sentence re-decode, not a
    local loop repair.
- **Sentence-level regressions among triggered cases:**
  - R42 −5.97 chrF (Task 1 regress candidate; the output shrinks from 15 to 10 words, and the opening clause changes);
  - R20 −2.70;
  - R01 −1.64.

  R01 and R20 also had their pre-loop text changed.
- **`I'm` lost inside triggered cases:** R03 (3→0) and R23 (3→1).

## 6. Cost

- **This stage:** 0 incremental model or API calls. It reuses saved outputs.
- **A real triggered-only regeneration path** would add one extra decode per triggered case: about 20 % of clips on this
  dev set, about 2.7 s CPU each (Task 1: 123 s for 45 no-repeat decodes). The 36 untriggered cases would add nothing
  beyond running the detector.

## 7. Stop condition

| Condition | Result |
|---|---|
| Non-triggered outputs byte-identical | **met** (36/36) |
| Legitimate-repetition negatives protected | **met** outside loops (R02, R04, R05, R13, R35) |
| Triggered loops substantially reduced | **met** (9 → 0) |
| No new major content damage | **not met**: 7/9 triggered outputs change text before the loop; R42 regresses (−5.97 chrF) |

**Recommendation: KEEP the frozen loop trigger. STOP the current `no_repeat_ngram_size=3` regeneration method.**
The gate solved the problem it was meant to solve: the 15 unnecessary changes and the R35 damage. The remaining damage
comes from the regeneration step itself: 7/9 triggered cases change text before the detected loop starts, so the
current regeneration method is not a safe local loop repair.

**Future redesign ideas only (neither was tested, run or tuned here):** a prefix-preserving repair that keeps the
control output unchanged up to the loop onset, so only the part after the onset can change. Simple truncation at the
onset would be a pure formatting baseline; a constrained continuation after the onset would be the content-recovery
variant.

The 45 cases remain the dev set. The trigger threshold must not be retuned on them. Any redesign needs its own
pre-registered damage check, and human review of the triggered cases, before claiming content recovery.

## 8. Context kept from Task 1

- Task 1's global `no_repeat_ngram_size=3` removed loops 9 → 0 but changed 15 non-loop outputs. Because it is a
  token-trigram ban, it also blocks a second `I'm` in a sentence.
- So the global setting is not suitable as the default.
- This stage shows that gating avoids those unnecessary changes. It does not make the regeneration itself safe.

## Limitations

- Automatic metrics only. No human labels for loop, content recovery or damage. The conditional metric increase is
  not a demonstrated translation-quality improvement.
- No new model decoding and no API calls occurred in this stage; incremental model/API cost is zero.
- n = 9 triggered cases. The dev set is worst-first and has been heavily studied, so none of this is a population
  estimate.
- The pre-loop-alteration proxy was defined after reading the triggered texts. It is descriptive and was not used to
  set any threshold.
- R23 sits just above the frozen threshold (0.194). Whether it is a true loop is unlabelled.
