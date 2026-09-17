# Text-Semantic Review Summary — Phase 1, 40-clip taxonomy

**Method: LLM-assisted text semantic review (automated text-level qualitative review).**
This is **not** human annotation and **not** ASL/visual expert annotation. It was produced
by Claude (this Claude Code session) reading only two English strings per clip — the
ground-truth reference and the baseline Gemini prediction — and judging semantic
agreement between them. No video was watched, no ASL expertise was applied, no model/API
call or new inference was run. Source data: `taxonomy_40_clips.csv` (unchanged).
Output: `taxonomy_40_text_semantic_review.csv` / `.json` (new files; `taxonomy_40_clips.csv`
and `taxonomy_40_human_review.csv/json` were not modified).

Every field below is `review_source: claude_code_text_semantic_review`,
`review_scope: english_reference_vs_prediction_only`.

## 1. Total clips reviewed

**40 / 40** clips from `taxonomy_40_clips.csv`.

## 2. Semantic adequacy distribution

| score | meaning | count | % |
|---|---|---|---|
| 2 | core meaning substantially correct | 0 | 0% |
| 1 | partially correct / important omission | 3 | 7.5% |
| 0 | wrong meaning or essentially unrelated | 37 | 92.5% |

**No clip scored a 2.** This baseline (2fps/adaptive sampling) is producing text that is
almost never even a loose paraphrase of the reference — the near-total failure documented
in the WER numbers (most clips near or above WER 1.0) reflects genuine semantic failure,
not just wording/style mismatch.

## 3. reference_topic_mismatch rate

**36 / 40 (90%)** marked `yes` — the prediction's topic is clearly inconsistent with the
reference. The remaining 4 (`no`) are: one empty prediction (no topic to compare), and
three predictions that retain a fragment of the reference's topic (a name, a "want to
learn" phrase, a vague "talking about a name") without conveying the full message.

This is a **text-based** measure of topic disagreement — it makes no claim about whether
the signed video itself supports or contradicts the prediction.

## 4. correct_meaning_different_english count / rate

**0 / 40 (0%).** No clip in this baseline preserves the reference's core meaning while
merely rephrasing it in different English. This baseline shows no evidence of the
"good paraphrase penalized by WER" pattern that motivated adding this field — every
error here is a meaning-level failure, not a wording-level one.

## 5. Obvious output repetition count / rate

**0 / 40 (0%).** None of the 40 baseline predictions show the repeated-word/phrase pattern
described in the taxonomy as a known Gemini-on-ASL failure mode. This check is text-only
(scanning the prediction string itself) and does not rule out other failure modes.

## 6. Review confidence distribution

| confidence | count | meaning |
|---|---|---|
| high | 33 | reference and prediction are unambiguously about different things (or unambiguously aligned) from text alone |
| medium | 6 | a coincidental word/number overlap, or a partial/fragmentary match, makes the text-only call less clear-cut |
| low | 1 | prediction is too vague/garbled to confidently classify from text alone |

The 6 "medium" clips are exactly the ones with a coincidental lexical overlap (e.g. the
number "four" appearing in both an unrelated prediction and a four-stringed-instrument
reference, or "first" appearing in both an unrelated prediction and "first string/first
fret") — these are flagged in their `semantic_review_rationale` and are good candidates
for a second look.

## 7. Representative examples

| clip_id | reference (shortened) | prediction (shortened) | score | rationale |
|---|---|---|---|---|
| `FzmL8SL6Bow_1-8-rgb_front` | "...clean up that hole...winding our hole...this wall here..." | "I looked and saw a dog approaching...a large, fierce bear walked slowly forward." | 0 | Unrelated animal narrative vs. a DIY/wall-repair narration. |
| `G0Q6AlvH96I_8-2-rgb_front` | "OK, meanwhile you see how I'm closing the gap?" | "One, two, three, four." | 0 | Prediction fabricates a number count where the reference contains no numbers at all — a candidate false-positive number pattern. |
| `92V3oH63zbQ_5-1-rgb_front` | "What is keeping your hands inside the baseball?" | *(empty)* | 0 | Empty output — looks like a pipeline/generation failure rather than a topic mismatch. |
| `FZbyRzy4huk_3-8-rgb_front` | "We cook it with 3 cups of water, 1 cup...1/2 tablespoon of pepper..." | "Tablecloth Coffee" | 0 | A numerically dense recipe reference collapses to two unrelated words; all quantities lost. |
| `g2NA_eBUcH8_0-3-rgb_front` | "Hi, have you ever wanted to learn a new game of poker?" | "If you want to learn" | 1 | Retains the "want to learn" fragment but drops the topic (poker) and question framing. |
| `G19uBylwQww_1-2-rgb_front` | "Hi, my name is Robert Segundo and today I'm going to teach you how to make...paper airplanes..." | "My name is Robert. I was born in California." | 1 | Correctly recovers the first name "Robert" but drops "Segundo," the paper-airplane topic, and adds an unverified birthplace. |
| `fZgWKh3ENoE_0-8-rgb_front` | "I'll be talking about Yu-Gi-Oh today." | "Chatting Name" | 1 (low confidence) | Vague overlap with "talking about a name," but doesn't reliably convey "Yu-Gi-Oh." |
| `-g0iPSnQt6w_0-1-rgb_front` | "Buenos Dias, I'm Bobby Larew, you didn't know I spoke Spanish, did you?" | "Back in Barcelona" | 0 (medium confidence) | Thematic echo (Spanish/Barcelona) but the actual self-introduction/joke is not conveyed. |

## 8. Clips worth ASL-expert / visual follow-up

**39 / 40** clips are flagged `requires_asl_expert_review: yes`, using this rule: strong
topic mismatch, OR `semantic_adequacy = 0`, OR the clip is especially relevant to the
temporal/fingerspelling/number hypotheses and needs visual diagnosis. Given this
baseline's near-total semantic failure rate, almost the entire set qualifies under the
first two conditions alone.

The single clip **not** flagged is `g2NA_eBUcH8_0-3-rgb_front` (semantic_adequacy=1,
clear partial-topic match, no fingerspelling/number hint) — a text-only reviewer can
already say enough about it without visual input.

Two clips (`G19uBylwQww_1-2-rgb_front`, `fZgWKh3ENoE_0-8-rgb_front`) score
semantic_adequacy=1 but are still flagged for ASL-expert review because they carry a
`fingerspelling_candidate` manifest hint and their partial name/topic match is exactly the
kind of case where confirming whether the fingerspelled name was actually visible (vs.
guessed from context) requires watching the signing.

**Because this baseline's WER is close to 1.0 for nearly every clip, "worth ASL-expert
follow-up" is a low bar here — almost everything qualifies.** The more useful signal is
*which subset* to prioritize for an ASL-fluent reviewer's limited time: start with the 6
"medium-confidence" coincidental-overlap clips (word/number look-alikes) and the
`number_token`-hinted clips, since those are the ones where a text-only reviewer's
judgment is most likely to be wrong, and where a real numbers/fingerspelling failure (vs.
total hallucination) would be visually distinguishable.

**36 / 40 (90%)** are additionally flagged `visually_grounded_hallucination:
requires_asl_review` — i.e., strongly unrelated predictions where an ASL-fluent reviewer
could, in principle, confirm true visual hallucination (no basis at all in the signing).
This is deliberately **not** asserted as `yes` anywhere in this review, per the
methodology rule: a text-only reviewer cannot establish "no basis in the video."

## 9. Cross-tab: text-semantic results vs. machine-derived manifest hints

**Manifest hints (`hint_number_token`, `hint_fingerspelling_candidate`, `hint_fast_signing`,
`hint_question`) are machine-derived from the English reference text only. They are NOT
confirmed visual ASL categories** — they describe what the reference text contains, not
what a reviewer (ASL-fluent or not) confirmed was visible in the signing. Cross-tabbing
them against the text-semantic results shows only whether reference content-type
correlates with baseline failure — it says nothing about whether the failure is visually
groundable.

Priority manifest-hint bucket assigned per clip (first match wins, in this priority order:
fingerspelling_candidate > number_token > fast_signing > question > plain_no_flag):

| manifest hint bucket | n | semantic_adequacy=0 | semantic_adequacy=1 | topic_mismatch=yes |
|---|---|---|---|---|
| fingerspelling_candidate | 14 | 12 | 2 | 12 |
| number_token | 9 | 9 | 0 | 9 |
| question | 5 | 4 | 1 | 3 |
| fast_signing | 4 | 4 | 0 | 4 |
| plain_no_flag | 8 | 8 | 0 | 8 |

Observations (descriptive only — no causal or visual claim):
- Every one of the 9 `number_token`-hinted clips scored semantic_adequacy=0, including two
  where the prediction fabricated numbers not present in the reference at all
  (`G0Q6AlvH96I_8-2-rgb_front`) and two with coincidental single-number text overlaps
  (`37ZtKNf6Yd8_1-1-rgb_front`, `8kAWy2YodzQ_10-1-rgb_front`) that still failed overall.
- Both semantic_adequacy=1 clips outside the `question` bucket carry the
  `fingerspelling_candidate` hint — the only bucket where any partial success occurred,
  though 12/14 fingerspelling-hinted clips still failed completely.
- `fast_signing` and `plain_no_flag` clips failed uniformly (0/4 and 0/8 partial or better).
- This distribution cannot distinguish "the model can't read fingerspelling/numbers from
  the sampled frames" from "the model is failing for unrelated reasons and these clips
  just happen to contain numbers/names" — that distinction needs the ASL/visual review
  this document explicitly does not attempt.

## 10. Paired-76 temporal ablation (already-produced result, integrated for context)

From the previously completed paired-76 experiment (not re-run or altered by this
review):

- 2fps/adaptive sampling, same 76-clip corpus: **WER ≈ 0.9730**
- 8fps/adaptive sampling, same 76-clip corpus: **WER ≈ 0.9715**
- Per-clip: **15 improved, 20 worsened, 41 unchanged**

Simply raising the frame budget from the current adaptive 2fps target to adaptive 8fps
(same motion-weighted sampling strategy, same independent 24-frame batching) produced
**essentially no aggregate improvement** (a ~0.0015 WER difference, within noise for this
corpus size) and a roughly even split of clips getting better vs. worse rather than a
consistent gain.

**No causal claim is made here.** The existing 8fps experiment varies frame budget only
while holding sampling strategy and batching fixed, and remains confounded with those two
other axes (see `MANAGER_FINDINGS_DRAFT.md`, section E) — it cannot by itself say whether
temporal density, sampling strategy, or batch/context structure is the dominant lever.
