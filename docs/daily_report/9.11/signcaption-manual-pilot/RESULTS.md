# SignCaption Manual Pilot — Results (How2Sign v2, 5 Clips)

**Date:** 2026-09-12
**Branch:** `baobao/asl-temporal-ablation-2026-09-06`
**Status:** Scored. `score_pilot.py --write-results` has been run against all 5 manually
placed SignCaption exports. No SignCaption API call, no Gemini call, no trajectory
experiment was run to produce this report — everything below is read-only scoring of
already-existing prediction files against the frozen How2Sign v2 reference.

Raw outputs consulted:
- `asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/results/per_clip_comparison.json`
- `asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/results/per_clip_comparison.csv`

## Pre-run safety checks

1. **Stale process from the prior move/verification step:** the backgrounded verification
   shell (task `b3cs0ccly`) had already exited on its own — it hit a `grep -F` call whose
   pattern argument was the dash-prefixed clip id (`-g0sqksgyc4_3-2-rgb_front`), which BSD
   grep misparsed as an option and errored out on. `ps -ef` showed no process for that
   task, for `shasum`, or for `grep -F` — nothing needed to be killed; it was stale, not
   hung.
2. **No process touching the 5 SRT files:** `lsof` against the `clips/` directory returned
   zero open file handles immediately before scoring.
3. SignCaption itself was not called, Gemini was not called, and no trajectory inference
   was run to produce this report.

## Method notes

- SignCaption is scored strictly as a **system prediction** against the frozen How2Sign v2
  reference — never as ground truth, and it never corrects or overwrites any other
  system's existing recorded result.
- Reference, Curify frame-baseline, Uni-Sign, and Gemini native-video predictions are
  read-only, pulled from their own already-scored `per_clip_results.json` files — none of
  those three systems was rerun.
- Trajectory-augmented Gemini predictions exist for only 2 of these 5 clips
  (`FzmL8SL6Bow_1-8-rgb_front`, `92V3oH63zbQ_5-1-rgb_front`) — the other 3 were never part
  of the D1/D2 trajectory probe set. Trajectory numbers are reported only for those 2 clips
  and are **never merged into the 5-clip aggregate** as if directly comparable.
- WER/CER via the repo's own `asl-eval/lib.text_metrics`; BLEU/chrF via `sacrebleu.BLEU()` /
  `sacrebleu.CHRF()` `.corpus_score()`, called per-clip with a single-sentence list (n=1) —
  the same call shape `score_pilot.py` and the other benchmark runners already use.
- All raw `signcaption_result.srt` files were preserved unmodified (verified below).

---

## 1. SRT parse verification

All 5 manually-placed SignCaption exports parsed successfully — no `missing`, no
`empty_prediction`, no `parse_failure`:

| clip_id | signcaption_status | source file |
|---|---|---|
| `FzmL8SL6Bow_1-8-rgb_front` | success | `clips/FzmL8SL6Bow_1-8-rgb_front/signcaption_result.srt` |
| `92V3oH63zbQ_5-1-rgb_front` | success | `clips/92V3oH63zbQ_5-1-rgb_front/signcaption_result.srt` |
| `G05uFub3YFc_9-2-rgb_front` | success | `clips/G05uFub3YFc_9-2-rgb_front/signcaption_result.srt` |
| `fzNnTgHa1lM_2-5-rgb_front` | success | `clips/fzNnTgHa1lM_2-5-rgb_front/signcaption_result.srt` |
| `-g0sqksgyc4_3-2-rgb_front` | success | `clips/-g0sqksgyc4_3-2-rgb_front/signcaption_result.srt` |

## 2. Per-clip results

### `FzmL8SL6Bow_1-8-rgb_front` (duration 25.77s)

- **Reference:** You want to go and clean up that hole you just made and now we are going
  to go and start winding our hole you just made and start spreading it out just like that
  and all the while I am pulling it out while my hands here are watching this wall here
  because this wall here is going to want to get out of control but I'm not going to let
  it, my hands are there.
- **Curify frame baseline:** I looked and saw a dog approaching. It just stood there,
  completely frozen. A large, fierce bear walked slowly forward.
- **Uni-Sign:** So I'm going to take this hole because it's going to be nice and clean and
  then I'm going to go ahead and take this hole and I'm going to go ahead and take this
- **Gemini native-video:** An ugly frog a big, fat frog
- **SignCaption:** It's just a little slow. Take a deep breath. Let's also walk down the
  road.
- **Trajectory-augmented Gemini:** I looked and reached into my pocket. Then I just froze
  in shock. A heavy creature slowly shuffled and walked forward, emerging into a wide open
  area, struggling with great difficulty.
- **SignCaption WER:** 0.9744 · **CER:** 0.8371 · **BLEU:** 0.0954 · **chrF:** 7.0265

### `92V3oH63zbQ_5-1-rgb_front` (duration 1.83s)

- **Reference:** What is keeping your hands inside the baseball?
- **Curify frame baseline:** (empty)
- **Uni-Sign:** We're going to do a couple of drills here.
- **Gemini native-video:** (empty)
- **SignCaption:** I'm here.
- **Trajectory-augmented Gemini:** (empty)
- **SignCaption WER:** 1.0000 · **CER:** 0.8696 · **BLEU:** 0.0000 · **chrF:** 2.4956

### `G05uFub3YFc_9-2-rgb_front` (duration 17.49s) — see deep dive in §6

- **Reference:** Again, do maybe twenty breaths, little flow, inhaling and exhaling the
  whole time you go breath is important and see if you would like, you can keep it up for
  a minute or more.
- **Curify frame baseline:** She smooths out the cloth and places it flat on the table. She
  sets the container down on the surface. She puts on her gear and fastens it securely
  around her back. The tree caught on fire.
- **Uni-Sign:** You want to make sure both of your stomachs are nice and soft and you want
  to make sure both of your stomachs are on top and the bottom and your stomach are on top
  and the bottom.
- **Gemini native-video:** I was terrified and my heart was pounding. Then I looked closely
  and saw what was actually there.
- **SignCaption:** Keep both feet flat on the floor. Keep your hips up and your arms
  relaxed.
- **Trajectory-augmented Gemini:** not available for this clip
- **SignCaption WER:** 0.9412 · **CER:** 0.7427 · **BLEU:** 0.8866 · **chrF:** 11.6467

### `fzNnTgHa1lM_2-5-rgb_front` (duration 25.31s)

- **Reference:** So you can tune the G with the lower G and the D with the lower D. So
  unlike some of the other double-stops, with this particular double-stop you have a
  choice.
- **Curify frame baseline:** Whenever you go with someone... chronic friend
- **Uni-Sign:** Going to google and the D with a low D, with a low D, which is a double
  stop with a particular location.
- **Gemini native-video:** The first one told me... If you have three books...
- **SignCaption:** E-G and low G-D, with the low D. It sounds like, with some of the double
  stops, you have a choice for this particular one.
- **Trajectory-augmented Gemini:** not available for this clip
- **SignCaption WER:** 0.7353 · **CER:** 0.5924 · **BLEU:** 13.7582 · **chrF:** 45.4836

### `-g0sqksgyc4_3-2-rgb_front` (duration 5.35s)

- **Reference:** So whenever you're moving forward, try to move the front foot first when
  moving forward, okay?
- **Curify frame baseline:** A spider was crawling on me!
- **Uni-Sign:** Well, you just dropped it off or you just got it out.
- **Gemini native-video:** Whoa, I was so terrified!
- **SignCaption:** Just take a chance; you might fail or get it.
- **Trajectory-augmented Gemini:** not available for this clip
- **SignCaption WER:** 1.0000 · **CER:** 0.8022 · **BLEU:** 0.0000 · **chrF:** 8.3134

---

## 3. Matched-5 aggregate metrics (all systems, same 5 clips)

**Methodology audit (2026-09-12), before committing anything:** the existing How2Sign v2
benchmark scorer (`asl-translator/evaluation/run_curify_how2sign_v2_benchmark.py`,
`_corpus_wer_cer` / `_corpus_bleu_chrf`, also used unmodified by
`run_native_video_how2sign_v2_benchmark.py`) does **not** average per-clip WER/CER/BLEU/chrF.
It computes:
- **corpus WER** = `sum(substitutions + deletions + insertions across all clips) / sum(reference_words across all clips)` — a single division after summing counts (length-weighted / micro-averaged), not a mean of per-clip WER.
- **corpus CER** = the same construction at the character level.
- **corpus BLEU / corpus chrF** = `sacrebleu.BLEU().corpus_score(all_hyps, [all_refs])` / `sacrebleu.CHRF().corpus_score(...)` called **once over the full list of hypotheses and references**, not per-clip scores averaged.

The table originally published here computed BLEU/chrF via `sacrebleu.corpus_score()`
called **per clip** (n=1 each) and then WER/CER/BLEU/chrF were all combined via a **simple
arithmetic mean across the 5 clips** — this is a *macro mean*, not the benchmark's own
corpus-level convention, and it weights every clip equally regardless of length (e.g. the
78-reference-word `FzmL8SL6Bow_1-8-rgb_front` clip counts the same as the 8-word
`92V3oH63zbQ_5-1-rgb_front` clip). Both tables are kept below, explicitly labeled, and the
official corpus-level table is used for the manager-facing conclusion in §7.

### 3a. Macro mean — SECONDARY / DIAGNOSTIC ONLY (simple average of per-clip metrics; NOT the benchmark's own convention; not used for any manager-facing conclusion)

| System | mean WER ↓ | mean CER ↓ | mean BLEU ↑ | mean chrF ↑ |
|---|---|---|---|---|
| Curify frame baseline | 0.9864 | 0.8489 | 0.42 | 9.21 |
| Uni-Sign | 0.9781 | **0.6967** | 2.93 | **18.38** |
| Gemini native-video | 0.9706 | 0.8507 | 0.79 | 6.10 |
| **SignCaption** | **0.9302** | 0.7688 | **2.95** | 14.99 |

### 3b. Official corpus-level aggregation — PRIMARY / MANAGER-FACING (same convention as `run_curify_how2sign_v2_benchmark.py` / `run_native_video_how2sign_v2_benchmark.py`)

Edit counts and reference lengths summed across all 5 clips first, then divided once;
BLEU/chrF computed as one `sacrebleu.corpus_score()` call over all 5 hypothesis/reference
pairs together:

| System | corpus WER ↓ | corpus CER ↓ | corpus BLEU ↑ | corpus chrF ↑ |
|---|---|---|---|---|
| Curify frame baseline | 0.9766 | 0.8136 | 0.28 | 11.60 |
| **Uni-Sign** | **0.9064** | **0.6845** | **3.15** | **20.85** |
| Gemini native-video | 0.9708 | 0.8514 | 0.18 | 6.36 |
| SignCaption | 0.9240 | 0.7686 | 1.98 | 15.91 |

n=5 for every system/metric in both tables (all 5 clips have a scored result for all 4
systems).

**The ranking changes under the official convention.** Under the macro mean, SignCaption
had the lowest (best) WER. Under the benchmark's own corpus-level (length-weighted)
convention, **Uni-Sign has the best score on all 4 metrics** — including WER (0.9064 vs.
SignCaption's 0.9240). The reason: `FzmL8SL6Bow_1-8-rgb_front` has 78 reference words, by
far the longest of the 5 clips (the other 4 have 8–34), so it dominates the length-weighted
sum. On that one clip Uni-Sign scores WER 0.8462 vs. SignCaption's 0.9744 — a large gap on
the clip that matters most once clips are weighted by length instead of counted equally.
SignCaption's per-clip-mean WER advantage was real but came from clips being weighted
equally at n=5, which is not how the existing benchmark itself scores accuracy.

## 4. Matched-2 comparison, trajectory-eligible clips only (`FzmL8SL6Bow_1-8-rgb_front`, `92V3oH63zbQ_5-1-rgb_front`)

This subset is **not comparable to the 5-clip tables above** — reported separately, at n=2,
so the trajectory-augmented condition can be seen against the same clips fairly. Both
aggregation conventions are shown for consistency with §3.

### 4a. Macro mean — SECONDARY / DIAGNOSTIC ONLY

| System | mean WER ↓ | mean CER ↓ | mean BLEU ↑ | mean chrF ↑ |
|---|---|---|---|---|
| Curify frame baseline | 0.9808 | 0.8932 | 0.14 | 5.58 |
| Uni-Sign | 1.0481 | **0.7246** | **1.20** | **17.52** |
| Gemini native-video | 1.0000 | 0.9649 | 0.00 | 0.87 |
| SignCaption | 0.9872 | 0.8534 | 0.05 | 4.76 |
| Trajectory-augmented Gemini | 0.9808 | 0.8750 | 0.25 | 7.17 |

### 4b. Official corpus-level aggregation

| System | corpus WER ↓ | corpus CER ↓ | corpus BLEU ↑ | corpus chrF ↑ |
|---|---|---|---|---|
| Curify frame baseline | 0.9651 | 0.8109 | 0.19 | 9.89 |
| **Uni-Sign** | **0.8837** | **0.6965** | **2.58** | **21.55** |
| Gemini native-video | 1.0000 | 0.9378 | 0.00 | 1.53 |
| SignCaption | 0.9767 | 0.8408 | 0.11 | 6.48 |
| Trajectory-augmented Gemini | 0.9651 | 0.7786 | 0.39 | 12.76 |

Under both conventions, on exactly these 2 clips Uni-Sign is the strongest system on every
metric; trajectory-augmented Gemini improves over plain native-video on all 4 metrics under
the official aggregation but does not catch Uni-Sign; SignCaption is unremarkable here
(middle of the pack) under either convention.

## 5. Semantic review — SignCaption (English reference vs. prediction only)

Per the benchmark's existing philosophy: this is a **text-semantic** comparison of English
reference vs. English prediction only. No claim is made here about which ASL signs were
correctly or incorrectly recognized — that requires an ASL-fluent reviewer, which none of
this pilot's participants are.

| clip_id | semantic adequacy | topic mismatch | genuine recovery vs. existing systems | rationale |
|---|---|---|---|---|
| `FzmL8SL6Bow_1-8-rgb_front` | 0 | yes | no | Reference is about filling/smoothing a hole in a wall by hand. SignCaption's "slow... deep breath... walk down the road" shares no content with that. Uni-Sign, despite being repetitive, actually keeps "hole" and "clean" — a real (if crude) topic anchor SignCaption doesn't have. |
| `92V3oH63zbQ_5-1-rgb_front` | 0 | yes | no | Reference asks about hand position "inside the baseball." SignCaption's "I'm here" is a content-free filler with no topic connection. Uni-Sign's "a couple of drills" is weak but at least sports-adjacent; SignCaption is not. |
| `G05uFub3YFc_9-2-rgb_front` | 1 | no (domain-level) | qualified yes — see §6 | SignCaption stays inside a physical-exercise instruction register ("feet flat," "hips up," "arms relaxed") that is plausible for the same video, unlike baseline's cloth/gear/fire hallucination or native-video's fear narrative. It never mentions breathing, inhaling/exhaling, or duration, so it is not a specific-content match — see the dedicated analysis below for why this is called "qualified." |
| `fzNnTgHa1lM_2-5-rgb_front` | 2 | no | yes | Reference is guitar tuning/double-stops language (G, D, low D, double-stop, choice). SignCaption reproduces essentially all of that vocabulary correctly ("E-G and low G-D, with the low D... double stops... you have a choice"). This is the one clip where SignCaption is unambiguously, specifically on-topic and close to the reference's actual wording — clearly the strongest result of any system on this clip (lowest WER of the 4, and by far the highest BLEU/chrF). |
| `-g0sqksgyc4_3-2-rgb_front` | 0 | yes | no | Reference is about which foot moves first when stepping forward. SignCaption's "take a chance; you might fail or get it" is a generic risk-taking aphorism, unrelated to foot/leg movement. No system recovers this topic. |

**Scoring key:** semantic adequacy 0 = unrelated/hallucinated topic, 1 = partial/domain-level
match without matching the specific content, 2 = accurate topic and substantially correct
specific content.

## 6. Deep dive — `G05uFub3YFc_9-2-rgb_front`

Reference is breathing/exercise instruction. The three other systems that are not
SignCaption diverge as follows:
- **Curify frame baseline** hallucinates an unrelated craft/sewing scene that ends with
  "the tree caught on fire" — cloth, gear, fire: no relationship to the reference at all.
- **Gemini native-video** hallucinates a fear narrative — "terrified," "heart was
  pounding" — also unrelated to breathing/exercise instruction.
- **SignCaption** produces "Keep both feet flat on the floor. Keep your hips up and your
  arms relaxed." — body-position, exercise-instruction language.

**Is this a genuine topic/semantic recovery, or only superficially closer?** My assessment:
**qualified/partial recovery, with a real caveat, not a clean win.**

Reasons to call it genuine, partial recovery:
- It is the only one of the three non-Uni-Sign systems that lands in the correct broad
  domain (physical-exercise instruction) rather than inventing an unrelated scene or
  narrative.
- "Feet flat, hips up, arms relaxed" is coherent, internally consistent cueing language of
  the kind that plausibly co-occurs in an actual exercise-instruction video alongside
  breathing cues — it is not nonsense and not off-domain.

Reasons this should not be reported as a clean semantic win:
- It never mentions breathing, inhaling, exhaling, or duration — the specific content of
  the reference — so it is not a content match, only a register/domain match.
- "Keep your feet flat / hips up / arms relaxed" is generic, boilerplate
  exercise-instruction phrasing that a captioning system could plausibly produce as a
  fallback for *any* fitness-looking video, independent of whether it actually understood
  the signed content. There is no way to distinguish "SignCaption correctly recovered part
  of this specific video's content" from "SignCaption defaulted to generic
  fitness-instruction phrasing that happens to sound plausible here" from the English text
  alone.
- Uni-Sign's output ("both of your stomachs... on top and the bottom") is also
  domain-adjacent (body-position instruction) even though it is less fluent — so
  SignCaption is not the only system with any domain-level signal here, just the most
  coherently worded one.

**Bottom line for this clip:** SignCaption is clearly the least-wrong of the four systems
in the sense of "not inventing an unrelated scene," and its language is genuinely
plausible for the video's real domain. But calling it a confirmed semantic recovery would
overclaim — it is better characterized as a topically-compatible but not
content-verified output. Adequacy is scored 1 (partial), not 2.

## 7. Manager question

> On these same 5 frozen benchmark clips, is SignCaption materially better than Curify
> frame baseline, Uni-Sign, and Gemini native-video?

**Short answer: No — and under the benchmark's own corpus-level metric convention (§3b),
SignCaption is not even the best-scoring system on lexical metrics; Uni-Sign is.**

**A. Lexical metric improvement:** No, using the official aggregation. Under corpus-level
WER/CER/BLEU/chrF (§3b — the same convention the existing benchmark scorer uses), **Uni-Sign
has the best score on all 4 metrics**: corpus WER 0.9064 vs. SignCaption's 0.9240, corpus
CER 0.6845 vs. 0.7686, corpus BLEU 3.15 vs. 1.98, corpus chrF 20.85 vs. 15.91. SignCaption
is second-best on WER and BLEU/chrF, ahead of the frame baseline and native-video, but it
does not lead the field. (The earlier, simple per-clip-mean table in §3a did show
SignCaption with the lowest mean WER — that ranking does not survive switching to the
benchmark's own length-weighted convention, because it let the short guitar clip count
equally with the much longer `FzmL8SL6Bow_1-8-rgb_front` clip, where Uni-Sign is
substantially stronger.) This is not a systematic lexical improvement over the existing
systems; on the metric convention this repo already uses everywhere else, SignCaption
trails Uni-Sign.

**B. Semantic/topic recovery:** Also mixed, not a general win. On 3 of 5 clips
(`FzmL8SL6Bow_1-8-rgb_front`, `92V3oH63zbQ_5-1-rgb_front`, `-g0sqksgyc4_3-2-rgb_front`)
SignCaption is just as off-topic as, or offers no more topic signal than, the other
systems — no recovery. On 1 of 5 (`G05uFub3YFc_9-2-rgb_front`) it shows a partial,
domain-level recovery that cannot be confirmed as content-accurate from English text alone
(§6). On 1 of 5 (`fzNnTgHa1lM_2-5-rgb_front`) it shows a genuine, specific, unambiguous
semantic and lexical recovery — the clearest positive result in this whole pilot.

**Overall:** A single clip (the guitar/double-stops clip) is a real, well-supported win for
SignCaption, and it remains the clearest positive signal in this pilot regardless of
aggregation method. But at the aggregate level, once the benchmark's own corpus-level
convention is used instead of an equally-weighted per-clip mean, **Uni-Sign — not
SignCaption — is the strongest system on this matched-5 set on every lexical metric**. A
pilot of this size (n=5, one outlier clip, one long clip that dominates the length-weighted
average) is not sufficient grounds to conclude SignCaption is materially better than the
existing systems; if anything, the corrected aggregation is evidence *against* that claim.
The guitar-clip result is worth a larger, controlled follow-up on its own merits, but it
should not be generalized into a claim that SignCaption outperforms Uni-Sign or the other
systems on this benchmark. Given the one clear semantic recovery observed in this 5-clip
pilot, a larger controlled evaluation is justified once the SignCaption API trial becomes
available; however, the current 5-clip evidence is not sufficient to claim that SignCaption
is generally better than Uni-Sign.

---

## Methodology audit addendum (2026-09-12)

Before committing, a separate audit checked whether this report's matched-5 aggregation
matched the existing How2Sign v2 benchmark's own convention. It did not (macro mean vs.
corpus-level/length-weighted — see §3). §3, §4, and §7 above have been corrected in place
to show both conventions and to base the manager-facing conclusion on the official one. No
raw SRT, no prediction file, and no other system's existing result was touched by this
audit — it only added read-only recomputation and this documentation. A stray shell process
flagged in the prior turn (`b3cs0ccly`) was checked and found already exited before this
audit began; nothing needed to be terminated.

## Files created/modified by this task

- **Created:** `asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/results/per_clip_comparison.json`
- **Created:** `asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/results/per_clip_comparison.csv`
- **Created:** `docs/daily_report/9.11/signcaption-manual-pilot/RESULTS.md` (this file)
- **Modified:** `docs/daily_report/9.11/signcaption-manual-pilot/pilot_manifest.csv`
  (`signcaption_status` updated from `not_started` to `success` for all 5 rows;
  `signcaption_output_path` unchanged, already correct)
- **Unmodified (verified byte-identical to the manually-placed exports):** all 5
  `asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/clips/<clip_id>/signcaption_result.srt`
  files

No source video, no frozen reference `.srt`, and no other system's existing result file
was modified. Nothing was staged, committed, or pushed.
