# SignCaption Manual Pilot — Batch 2 Results & Combined 15-Clip Pilot (How2Sign v2)

**Date:** 2026-09-14
**Branch:** `baobao/asl-temporal-ablation-2026-09-06`
**Status:** Scored. `score_batch2_and_combined.py --write-results` has been run against all
10 manually placed Batch-2 SignCaption exports. No SignCaption API call, no Gemini call,
and no other inference was run to produce this report — everything below is read-only
scoring of already-existing prediction files against the frozen How2Sign v2 reference.

Raw outputs consulted (all read-only, none modified):
- `asl-translator/data/public_benchmarks/how2sign_v2/references/*.srt` — frozen reference manifest
- `asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/<clip_id>/signcaption_result.srt` — the 10 raw Batch-2 exports
- `asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/results/per_clip_comparison.json` — original 5-clip pilot, read-only
- `asl-translator/evaluation/results/how2sign_v2/curify_gemini_3_6_2026_09_04/per_clip_results.json`
- `asl-translator/evaluation/results/how2sign_v2/unisign/per_clip_results.json`
- `asl-translator/evaluation/results/how2sign_v2/curify_gemini_native_video_2026_09_10/per_clip_results.json`

## Pre-run safety checks (before scoring)

1. **Reference provenance:** `score_batch2_clip()` reads reference text only from
   `REFERENCES_DIR / f"{clip_id}.srt"` under the frozen `how2sign_v2` benchmark manifest
   (128 clips total). No reference text is ever passed into a SignCaption inference call —
   there is no inference call in this script at all; it only scores already-placed files.
2. **SignCaption provenance:** `load_signcaption_result()` reads only from
   `clips/<clip_id>/signcaption_result.srt` (or `.txt` fallback) — the raw files placed by
   the human operator, copied byte-for-byte from `~/Downloads` and verified via SHA-256 in
   the prior turn. Nothing in the scoring path edits, normalizes, or regenerates this text.
3. **No model/API calls:** `asl-translator/asl-eval/lib.py` (parsing + WER/CER) is pure
   standard library — no network calls. BLEU/chrF use local `sacrebleu` (installed,
   v2.6.0), also no network calls. Confirmed by reading both modules before running.
4. **Original 5 pilot is read-only:** `load_original5_rows()` only reads
   `how2sign_v2_5clip/results/per_clip_comparison.json`; it is never recomputed, and its
   own `clips/*/signcaption_result.srt` files were not touched by this task.
5. **True native-video overlap:** verified independently (not just trusting the docstring)
   by loading `curify_gemini_native_video_2026_09_10/per_clip_results.json` directly and
   checking `status == "success"` for each of the 15 pilot clip ids. Result: **exactly 8**
   — `FzmL8SL6Bow_1-8-rgb_front`, `92V3oH63zbQ_5-1-rgb_front`, `G05uFub3YFc_9-2-rgb_front`,
   `fzNnTgHa1lM_2-5-rgb_front`, `-g0sqksgyc4_3-2-rgb_front`, `g2NA_eBUcH8_0-3-rgb_front`,
   `G19uBylwQww_1-2-rgb_front`, `fZM3IcM2Xs4_14_15_16-10-rgb_front` — matching the expected
   list exactly. The other 7 Batch-2 clips have no native-video prediction; none is used or
   fabricated for them.
6. **No 128-clip extrapolation:** all reference lookups resolve against the same 128-clip
   `how2sign_v2/references/` directory used elsewhere in the repo; nothing in this report
   claims a result beyond these 15 manually-scored clips.

## Commands run

```bash
# Inspect without writing anything
python3 asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/score_batch2_and_combined.py --dry-run

# Score and persist batch2_per_clip.json / combined15_per_clip.json
python3 asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/score_batch2_and_combined.py --write-results
```

Two supplementary, read-only computations were then run on top of the scorer's own JSON
output (not part of the tracked script, no re-scoring performed):
- A Batch-2-only SignCaption corpus aggregate (§A below) — the shipped script only prints
  Batch-2 *per-clip* rows plus the *combined-15* and *native-video-8* aggregates, not a
  Batch-2-only aggregate, so this was computed using the same `_corpus_wer_cer_from_texts`
  / `_corpus_bleu_chrf_multi` helpers already defined in the script, restricted to the 10
  Batch-2 rows.
- A text-semantic review (§5-style 0/1/2 rubric) applied to the 10 Batch-2 clips (§B/§A
  below) — see the labeling note there.

---

## A. Batch-2 (10 new clips) — per-clip results

**Semantic-adequacy scoring key** (same rubric as the original 5-clip pilot's RESULTS.md
§5): 0 = unrelated/hallucinated topic, 1 = partial/domain-level match without matching
specific content, 2 = accurate topic and substantially correct specific content.

> **Labeling note:** the original 5-clip semantic review was written by the human pilot
> operator. No equivalent human review exists yet for Batch-2. The adequacy/mismatch
> values below are **Claude's own text-only application of the same documented rubric**
> (English reference vs. English SignCaption prediction — no ASL video was watched, exactly
> as the rubric's own stated scope requires). This is **not** an independent second human
> reviewer and should be treated as a provisional, single-annotator pass, not a
> human-verified label.

`score_batch2_and_combined.py`'s own output (`results/batch2_per_clip.json` and
`results/combined15_per_clip.json`) intentionally leaves `semantic_adequacy` /
`topic_mismatch` unset (`None`) for all 10 Batch-2 clips, reserving those fields for a
future human review; the text-only judgments shown in the table below and used in §B/§C
are instead persisted separately in
[`semantic_review_batch2.csv`](./semantic_review_batch2.csv) (`reviewer =
claude_text_only_v1`, `review_type = reference_vs_prediction_text_only`) — this is **not**
fluent-ASL human annotation.

| clip_id | reference text | raw SignCaption transcript | WER | CER | BLEU | chrF | semantic adequacy | topic mismatch | error note |
|---|---|---|---|---|---|---|---|---|---|
| `g2NA_eBUcH8_0-3-rgb_front` | Hi, have you ever wanted to learn a new game of poker? | Hello! Do you want to learn something new? | 0.6667 | 0.5769 | 7.0737 | 24.8753 | 1 | no | Correct greeting + "want to learn something new" register; drops "poker" — domain match, not specific-content match. |
| `G19uBylwQww_1-2-rgb_front` | Hi, my name is Robert Segundo and today I'm going to teach you how to make one of my favorite paper airplanes, the simple one. | My name is Robert Sgundo, and today... | 0.7692 | 0.7236 | 4.0685 | 23.0775 | 1 | no | Correct name + "today I'm..." opening; transcript is truncated before the actual subject (paper airplanes) is stated. |
| `fZM3IcM2Xs4_14_15_16-10-rgb_front` | Look at that. Morris sings(Ready to rock and roll today) Kind of feels festive almost like Christmas time. Simple mash right there. | I'm ready to sing. I feel happy. | 0.913 | 0.811 | 0.7599 | 9.4143 | 1 | no | Plausible simplification (singing / festive-happy mood) but drops all specific content (Morris, Christmas, "mash"). |
| `g2nvBjp0loQ_4-3-rgb_front` | It's a good idea to get a nice easy body sweat. | That's a good idea. It's nice and easy on the body. | 0.6667 | 0.5 | 14.6941 | 47.0621 | **2** | no | Near-exact paraphrase; only drops "sweat" — strongest specific-content match in Batch-2. |
| `g05yGRoZE10_1-8-rgb_front` | There is a median that you need to use when doing this and, it's called flux. | What is the name of the fluid the painter needs to use for this? | 0.9412 | 0.6933 | 5.1174 | 23.4361 | 1 | no | Recovers the domain (naming a substance used in a process) but substitutes "fluid"/"painter" for the reference's specific term "flux". |
| `FzQPg4aqNYc_13-1-rgb_front` | What I'll do then is just push some freshly ground black pepper on this all around. | I have enough now. | 0.9412 | 0.8659 | 0.9691 | 4.6613 | **0** | **yes** | Reference is a cooking/seasoning instruction; prediction shares no topic content. |
| `G3RvsnzQrXQ_3-10-rgb_front` | Now with the fold facing you so that you can open it up outwards, you're going to take the palm of your hand and I'm going to remove my ring, and about the middle palm of your hand you're going to place on your paper like so. | The book folds closed like a lid, and then the lever turns upward. | 0.94 | 0.7928 | 0.6409 | 10.433 | **0** | **yes** | Invents an unrelated "book"/"lid"/"lever" mechanism; shared word "fold" is superficial overlap, not a topic match. |
| `g0UUmEkoT1w_2-10-rgb_front` | They may feel very tired, sleepy, lacking energy. | The juice has a very specific look, and you can't taste the bitterness. | **1.625** | 1.087 | 3.4586 | 15.5532 | **0** | **yes** | Reference is fatigue/symptoms; prediction is juice flavor/appearance — unrelated. Also the worst WER in Batch-2. |
| `FZCEymcpq7I_14-1-rgb_front` | I hit that one a little fat, so we're going to take one more swing, but that's what you want to get rid of in your swing when you practice a lot is getting rid of these fat balls. | The ball is going straight, and it's fine. I don't want to try the draw fade. | 0.9268 | 0.7102 | 1.6505 | 15.1446 | 1 | no | Correctly stays in the golf-swing domain and reproduces real golf vocabulary ("draw fade"), but the specific narrative (hitting "fat", practicing to fix it) doesn't match. |
| `G1jsDl1mVvk_1-1-rgb_front` | When it comes to the main referee, the main referee usually wears a jersey that can be a black or a type of neon green or pink but the official referee, he'll come to you at the beginning of the game... | The referee is the main official. They wear black with neon colors like green and pink. The official has a whistle. | 0.8889 | 0.7649 | 0.6845 | 18.3301 | **2** | no | Correctly identifies the referee topic and reproduces the specific uniform colors near-verbatim; "has a whistle" is an unverified addition. |

All 10 clips: `signcaption_status = success` (no `missing`, `empty_prediction`, or
`parse_failure`).

### Batch-2-only aggregate (n=10, corpus-level / length-weighted, same convention as §3b of the original pilot)

| metric | value |
|---|---|
| corpus WER ↓ | 0.9029 |
| corpus CER ↓ | 0.7595 |
| corpus BLEU ↑ | 1.2751 |
| corpus chrF ↑ | 16.9463 |

### Batch-2 semantic distribution (n=10, provisional single-annotator text review — see labeling note above)

| adequacy | count |
|---|---|
| 0 (unrelated/hallucinated) | 3 |
| 1 (partial/domain-level) | 5 |
| 2 (accurate + specific) | 2 |

Topic mismatch rate: **3/10 (30%)**.

---

## B. Combined SignCaption pilot (15 clips = original 5 + Batch-2 10)

**This is a manual 15-clip pilot, not a representative 128-clip benchmark.** The 15 clips
were not drawn as a uniform random sample of the 128-clip How2Sign v2 set (Batch-2 was
stratified-sampled with 3/10 intentionally drawn from the diagnostic-12 subset; see
`docs/daily_report/9.13/signcaption-batch2-manual-pilot/README.md` for the selection
rationale). None of the aggregate numbers below should be read as an estimate of
SignCaption's performance across the full benchmark.

### Combined-15 aggregate (n=15, corpus-level / length-weighted)

| system | corpus WER ↓ | corpus CER ↓ | corpus BLEU ↑ | corpus chrF ↑ | n |
|---|---|---|---|---|---|
| Curify frame baseline | 0.9978 | 0.8637 | 0.548 | 12.6151 | 15 |
| Uni-Sign | 0.9332 | 0.7217 | 5.0763 | 20.6589 | 15 |
| **SignCaption** | **0.9109** | 0.7631 | 1.4654 | 16.5482 | 15 |

### Combined-15 semantic distribution (5 original human-reviewed + 10 Batch-2 provisional single-annotator, see §A labeling note)

| adequacy | count |
|---|---|
| 0 (unrelated/hallucinated) | 6 |
| 1 (partial/domain-level) | 6 |
| 2 (accurate + specific) | 3 |

Topic mismatch rate: **6/15 (40%)**. The 3 adequacy=2 clips are `fzNnTgHa1lM_2-5-rgb_front`
(original 5, guitar/double-stops), `g2nvBjp0loQ_4-3-rgb_front` (Batch-2, body-sweat
paraphrase), and `G1jsDl1mVvk_1-1-rgb_front` (Batch-2, referee uniform colors).

**Note on comparability of the semantic column:** the original-5 values are the human
pilot operator's own judgment (9.11 RESULTS.md §5); the Batch-2 values are Claude's
single-pass text review using the same rubric. They are reported together because the
rubric and scope (English text vs. English text, no ASL judgment) are identical, but they
were not produced by the same reviewer or in the same sitting — treat the combined
distribution as indicative, not as a single controlled annotation pass.

---

## C. Matched-15 model comparison (SignCaption / Curify frame baseline / Uni-Sign)

Same table as §B's aggregate (all three systems have a `success` prediction for all 15
clips by construction of the Batch-2 eligibility filter — no clip is dropped or
extrapolated):

| system | corpus WER ↓ | corpus CER ↓ | corpus BLEU ↑ | corpus chrF ↑ |
|---|---|---|---|---|
| Curify frame baseline | 0.9978 | 0.8637 | 0.548 | 12.6151 |
| Uni-Sign | 0.9332 | 0.7217 | **5.0763** | **20.6589** |
| **SignCaption** | **0.9109** | 0.7631 | 1.4654 | 16.5482 |

SignCaption has the best (lowest) corpus WER of the three; Uni-Sign has the best CER, BLEU,
and chrF, both by clear margins (BLEU 5.08 vs. 1.47; chrF 20.66 vs. 16.55).

---

## D. True native-video overlap comparison (matched 8/15 clips only)

Only these 8 of the 15 pilot clips have a valid Gemini native-video prediction — reported
**separately**, never merged into the 15-clip tables above, and never extrapolated to the
other 7 Batch-2 clips:

`FzmL8SL6Bow_1-8-rgb_front`, `92V3oH63zbQ_5-1-rgb_front`, `G05uFub3YFc_9-2-rgb_front`,
`fzNnTgHa1lM_2-5-rgb_front`, `-g0sqksgyc4_3-2-rgb_front`, `g2NA_eBUcH8_0-3-rgb_front`,
`G19uBylwQww_1-2-rgb_front`, `fZM3IcM2Xs4_14_15_16-10-rgb_front`

### Matched-8 four-way comparison (n=8, corpus-level)

| system | corpus WER ↓ | corpus CER ↓ | corpus BLEU ↑ | corpus chrF ↑ |
|---|---|---|---|---|
| Curify frame baseline | 1.0388 | 0.9003 | 0.9038 | 14.0855 |
| Uni-Sign | 0.9181 | **0.6812** | **2.5923** | **19.5469** |
| Gemini native-video | 0.9784 | 0.8486 | 0.1868 | 7.467 |
| **SignCaption** | **0.8922** | 0.7596 | 1.9084 | 16.3896 |

SignCaption has the best WER of all four systems on this true 8-clip overlap, and beats
Gemini native-video on **all 4 metrics** (WER, CER, BLEU, chrF). It does not beat Uni-Sign
on CER, BLEU, or chrF.

---

## E. Interpretation

**1. Is SignCaption materially better than the current Curify frame baseline on this pilot?**
Yes, consistently, on this 15-clip pilot — SignCaption beats Curify on **all 4** corpus
metrics (WER 0.9109 vs. 0.9978, CER 0.7631 vs. 0.8637, BLEU 1.4654 vs. 0.548, chrF 16.5482
vs. 12.6151). This is the cleanest, least ambiguous result in the whole pilot. That said,
every system's WER is still ≥0.91 (i.e., ~91%+ of reference words are wrong under a
length-weighted count) — "better than Curify" here means "less bad," not "usably accurate."

**2. Is SignCaption better than Uni-Sign on this pilot?**
No, not overall. SignCaption only wins on corpus WER (0.9109 vs. 0.9332); Uni-Sign wins on
CER (0.7217 vs. 0.7631), and wins by a clear margin on BLEU (5.0763 vs. 1.4654, more than
3x) and chrF (20.6589 vs. 16.5482). This matches the direction of the original 5-clip
pilot's finding (Uni-Sign led on all 4 metrics there); adding Batch-2 lets SignCaption
close the gap enough to take the WER lead, but Uni-Sign remains ahead on the majority of
metrics, and by a larger margin on BLEU/chrF specifically.

**3. On the true 8-clip overlap, how does SignCaption compare with Gemini native-video?**
SignCaption beats Gemini native-video on all 4 metrics here (WER 0.8922 vs. 0.9784, CER
0.7596 vs. 0.8486, BLEU 1.9084 vs. 0.1868 — over 10x — and chrF 16.3896 vs. 7.467, more
than double). This is the single most consistent win for SignCaption over any one baseline
system in the whole pilot. It still trails Uni-Sign on the same 8 clips on CER, BLEU, and
chrF.

**4. Are improvements reflected only in WER/CER, or also in semantic adequacy/topic recovery?**
Both, partially. On the combined 15, 9/15 clips (60%) show at least domain-level semantic
signal (adequacy ≥ 1), and 3/15 (20%) show a clear, specific-content match (adequacy = 2):
the guitar/double-stops clip from the original pilot, plus two new Batch-2 clips
(`g2nvBjp0loQ_4-3-rgb_front`, `G1jsDl1mVvk_1-1-rgb_front`). So the lexical-metric edge over
Curify and native-video is not purely an artifact of WER/CER counting — there is genuine
topic/content recovery on a real minority of clips. But 6/15 (40%) are still a clear topic
mismatch (adequacy = 0), so this is not a general semantic win either. **Important caveat:**
this same 0/1/2 review was never applied to Curify's, Uni-Sign's, or native-video's outputs
in either pilot — so this pilot has no basis for a *comparative* semantic claim (e.g. "more
semantically adequate than Uni-Sign"), only a within-SignCaption characterization of when
its own lexical-metric wins do vs. don't correspond to real topic recovery.

**5. Strongest SignCaption successes:**
- `g2nvBjp0loQ_4-3-rgb_front` (Batch-2, adequacy 2) — near-exact paraphrase of the reference.
- `G1jsDl1mVvk_1-1-rgb_front` (Batch-2, adequacy 2) — correct topic (referee) and the
  reference's specific uniform colors reproduced almost verbatim.
- `fzNnTgHa1lM_2-5-rgb_front` (original 5, adequacy 2) — reproduces the reference's guitar
  double-stop vocabulary essentially in full; still the single clearest result across both
  pilots (lowest WER, by far the highest BLEU/chrF of any SignCaption clip in either batch).
- `FZCEymcpq7I_14-1-rgb_front` (Batch-2, adequacy 1) — worth calling out separately: it
  produces a real, specific golf term ("draw fade") not present in the reference, showing
  some genuine domain vocabulary even though it doesn't match the reference's specific
  narrative.

**6. Clearest SignCaption failures:**
- `g0UUmEkoT1w_2-10-rgb_front` (Batch-2, adequacy 0) — fatigue/symptoms reference vs. a
  juice-taste prediction; also the single worst WER (1.625) in either batch.
- `FzQPg4aqNYc_13-1-rgb_front` (Batch-2, adequacy 0) — cooking/seasoning reference vs. a
  content-free "I have enough now."
- `G3RvsnzQrXQ_3-10-rgb_front` (Batch-2, adequacy 0) — hallucinates an unrelated
  book/lid/lever mechanism against a paper-folding/hand-placement reference.
- `FzmL8SL6Bow_1-8-rgb_front`, `92V3oH63zbQ_5-1-rgb_front`, `-g0sqksgyc4_3-2-rgb_front`
  (original 5, all adequacy 0) — see 9.11 RESULTS.md §5 for rationale.

**7. Does this pilot provide evidence that a specialized sign-caption system has a higher ceiling than generic Gemini prompting?**
**Evidence, not proof, and only against Gemini specifically — not against every system
tested.** On this 15-clip (8-clip for native-video) manual pilot, SignCaption
consistently and, on the native-video subset, substantially outperforms both forms of
generic Gemini prompting tested here (Curify frame-based prompting: all 4 metrics on 15
clips; Gemini native-video prompting: all 4 metrics on the true 8-clip overlap). That is
real, if small-sample, evidence in favor of the specialized-system hypothesis relative to
*Gemini* prompting specifically. It is **not** evidence that SignCaption has the highest
ceiling of any system evaluated here: Uni-Sign — itself a specialized (non-Gemini)
sign-language system — still leads SignCaption on CER, BLEU, and chrF in both the
combined-15 and native-video-8 comparisons. So the honest reading is: *some* evidence that
specialized systems can beat generic Gemini prompting on this task, on these clips;
*no* evidence from this pilot that SignCaption in particular has a higher ceiling than
other specialized systems already in the benchmark. This remains a 15-clip (8-clip)
manual pilot on a stratified, non-random subset of one 128-clip benchmark — not grounds
for a general capability claim about SignCaption, and not a substitute for a full-benchmark
run.

---

## Files created/modified by this task

- **Created:** `asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/results/batch2_per_clip.json`
- **Created:** `asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/results/combined15_per_clip.json`
- **Created:** `docs/daily_report/9.13/signcaption-batch2-manual-pilot/RESULTS.md` (this file)
- **Created:** `docs/daily_report/9.13/signcaption-batch2-manual-pilot/per_clip_results.csv`
- **Created:** `docs/daily_report/9.13/signcaption-batch2-manual-pilot/combined_15clip_comparison.csv`
- **Created:** `docs/daily_report/9.13/signcaption-batch2-manual-pilot/overlap_8clip_comparison.csv`
- **Unmodified (verified byte-identical to the manually-placed exports in the prior turn):**
  all 10 `asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/<clip_id>/signcaption_result.srt` files
- **Unmodified:** the original 5-clip pilot's `clips/*/signcaption_result.srt` files and its
  `results/per_clip_comparison.json` (read-only source for §B/§C/§D)
- **Not modified further, reviewed only:** `docs/daily_report/9.11/signcaption-manual-pilot/RESULTS.md`
  — see note below.

## Why `docs/daily_report/9.11/signcaption-manual-pilot/RESULTS.md` shows as modified

This file's working-tree modification **predates this task** — it was made in the prior
session covering the independent calculation audit
(`docs/daily_report/9.13/signcaption-calculation-audit/CALCULATION_AUDIT.md`) and is
already fully explained and self-documented inside the file itself (see its own
"**Correction (2026-09-13)**" paragraph in §3b). Summary: SignCaption's corpus BLEU on the
original 5-clip matched set was originally published as `1.98`; a from-scratch,
independently-implemented recomputation found the true value rounds to `1.97` (a
double-rounding mistake, not a scoring-code bug), confirmed every other number in the
document, and corrected exactly that one figure in two places (§3b's table and §7's prose).
No ranking or conclusion in that document changed. I reviewed the diff (`git diff` against
that file) in this task and confirm it contains only that BLEU correction — nothing else
differs from HEAD. Per the task instructions, **no further changes were made to this file**;
it remains factually consistent as-is.

No source video, no frozen reference `.srt`, and no other system's existing result file was
modified by this task. Nothing was staged, committed, or pushed.
