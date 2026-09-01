# Uni-Sign — 19-clip frozen How2Sign benchmark, aggregate result, 2026-08-31

**Status: SUCCESS — 19/19 clips scored.** Full frozen How2Sign benchmark
run through the same environment, checkpoint, CPU patches, and decoding
configuration validated in the one-clip smoke test
(`UNISIGN_ONE_CLIP_RESULT.md`). No tuning, no training, no changes to the
frozen clip selection, no private Curify data, no production code
touched.

**This is a research/evaluation experiment only.** See "Licensing
limitation" — result quality does not change that boundary.

## Run summary

| Field | Value |
|---|---|
| Inference success | **19/19** (100%) |
| Total wall-clock | **1235.7s (~20.6 minutes)**, including one-time model/checkpoint load (~16.3s) |
| Sum of per-clip processing time | 1219.2s |
| Peak RSS observed | **~3.79GB** |
| Environment | Same as one-clip smoke test — `unisign-cpu-arm64` conda env, no changes |
| Checkpoint | `how2sign_pose_only_slt.pth`, same file, same SHA256 as before |
| Decoding config | `num_beams=4`, `max_new_tokens=100` — identical to the one-clip test, not tuned |

## Corpus-level metrics (pooled — same methodology as OpenSLT's own corpus numbers)

| Metric | Uni-Sign (this run, 19/19) | Uni-Sign (18-clip subset, excluding the clip OpenSLT skipped) | **OpenSLT (Phase 1, 18/19)** |
|---|---|---|---|
| Clips scored | 19/19 | 18/18 | 18/19 |
| Corpus WER | **0.9480** | 0.9477 | **1.1637** |
| Corpus CER | **0.7606** | 0.7613 | **0.8675** |
| Corpus SacreBLEU | **3.13** | 3.35 | **~0.93–0.96** |
| Corpus chrF | **20.34** | 20.88 | **~17.11–19.59** |

Corpus WER = total edit operations (substitutions + deletions +
insertions) pooled across all clips, divided by total reference words
pooled across all clips — the exact same pooled-aggregation methodology
`OPENSLT_19CLIP_RESULTS.md` used (not an average of per-clip WER). Corpus
CER computed the same way at the character level. SacreBLEU/chrF computed
corpus-style with `sacrebleu==2.2.0` (the Uni-Sign-pinned version) using
its default `13a` tokenizer, matching OpenSLT's own scoring tokenizer
choice.

**The 18-clip subset column exists because Uni-Sign scored one clip
(`G33aqW3DLpc_1-10-rgb_front`, 30.67s) that OpenSLT's official pipeline
could not — its own `max_source_positions=1024` config hard-limit dropped
that clip's 1034 I3D feature frames, exactly as documented in Phase 1.
Uni-Sign's `max_length=256` pose-frame cap (with random subsampling for
longer clips, not a hard reject) handled it without incident.** Both the
full 19/19 and the strict 18/18-matched-to-OpenSLT numbers are reported
so this genuine "handles a clip the other system can't" difference is
visible rather than hidden by a footnote — and both give essentially the
same conclusion.

## Full per-clip results

See `UNISIGN_19CLIP_RESULTS.csv` for all 19 rows (index, clip_id,
duration, status, reference, prediction, WER, CER, sentence-BLEU,
sentence-chrF, substitutions/deletions/insertions/ref_words/hyp_words,
pose-frame count, and per-clip pose-extraction/generation/total runtime).

## Best 3 / worst 3 (selected by WER, not cherry-picked)

### Best 3 (lowest WER)

| Rank | Clip | Duration | WER | Reference | Prediction |
|---|---|---|---|---|---|
| 1 | `37ZtKNf6Yd8_0-1-rgb_front` | 9.74s | **0.6923** | "Now this here, although it looks like a guitar, it's still in the guitar family of instruments, this is called ukulele not technically a guitar." | "This is a really interesting guitar, and it's still a very interesting guitar family, and this is called the Ruckel." |
| 2 | `FZbyRzy4huk_1-8-rgb_front` | 24.45s | **0.7846** | "We're going to use 1/2 of cup of chickpeas soak in 1 1/2 cup of water..." | "We're going to use one of the bottles of tomatoes and we're going to make sure that we have the same amount of water that we're going to be using, we're going to" |
| 3 | `G1lNlhjWC1I_16_17-8-rgb_front` | 30.9s | **0.8125** | "So what I'm going to do is show you a little technique i just call the 'c'..." | "I'm going to show you a few pictures of Cichlids. What we're going to do is we're going to have a little bit of Cichlids. We're going to" |

**Even the "best" prediction (WER 0.69) does not track its reference's
actual content** — `37ZtKNf6Yd8` at least stays on the general topic
("guitar-family instrument," correctly senses it's not really a guitar)
but invents a wrong instrument name ("Ruckel" vs. the reference's
"ukulele"). No clip in this benchmark produced a translation a viewer
could actually rely on.

### Worst 3 (highest WER)

| Rank | Clip | Duration | WER | Reference | Prediction |
|---|---|---|---|---|---|
| 1 | `8kAWy2YodzQ_16_17_18-1-rgb_front` | 21.13s | **7.75** | "That's pretty good." | "So, we're going to go ahead and take a brush, we're going to take a brush, we're going to take a brush, we're going to take a" |
| 2 | `-g45vqccdzI_5-1-rgb_front` | 7.01s | **5.25** | "We press this button, which opens the door." | "If you don't get enough out there, you're going to have to try to find a way to get out of it, and then you're going to have to try to find a way to get out of it." |
| 3 | `92V3oH63zbQ_12-1-rgb_front` | 6.79s | **1.037** | "Now if I do it the other way where we go, and I bar my hands out we're breaking many rules we've already talked about." | "This is almost like hitting the ball at the very end of the game, and it's almost like hitting the ball at the very end of the game." |

**The top two "worst" cases are a benchmark-construction artifact, not
evidence Uni-Sign is uniquely bad on them**: both references are
extremely short (3–9 words), so WER's denominator (reference word count)
is tiny — any normal-length generation registers as an astronomically
high error rate by construction. **This is the exact same clip
(`8kAWy2YodzQ`) that OpenSLT's own 19-clip result flagged as its own
"catastrophic outlier" for the identical reason** (Phase 1's
`OPENSLT_19CLIP_RESULTS.md`: "the single catastrophic outlier
(`8kAWy2YodzQ`, WER 17.0)"). Both systems are penalized by the same
short-reference artifact on the same clip — this is a property of the
benchmark's WER metric on very short references, not a Uni-Sign-specific
weakness.

## Failure-mode analysis (all 19 predictions)

- **Semantic/topic preservation: essentially zero across all 19 clips.**
  Every single prediction describes an activity or object unrelated to
  its reference (mascara instead of arm stretches, a wire cutter instead
  of a string winder, "Cichlids" instead of a makeup technique, etc.).
  This is not a few bad clips — it is universal across the full frozen
  benchmark.
- **Fluent, grammatical, unsupported English: the dominant style.**
  Every prediction reads as confident, well-formed spoken English. None
  of the malformed-token garbling OpenSLT's one-clip output showed. The
  fluency is real; the content is not.
- **Repetition loops: 8 of 19 clips (42%)** show a clear near-verbatim
  repeated clause within the same prediction — "mascara brush" (×4),
  "hitting the ball..." (×2), "find a way to get out of it" (×2), "wire
  cutter" (×3), "sand weed" (×4), "take a brush" (×4), "applying a
  foundation" (×2), "keep the load going" (×2). This is the same failure
  mode flagged in the one-clip smoke test, now confirmed to recur
  broadly, not a one-off.
- **Complete omissions: universal.** No prediction recovers the specific
  objects, actions, or steps named in its reference (buttons, tuning
  machines, ailerons, boxing footwork, chickpea soaking times, granular
  skin scrubs, cardio equipment, snout/feather shaping, clay thickness
  measurement — none of these specific reference contents appear in any
  prediction).
- **Numbers: never recovered.** The clearest test case is
  `FZbyRzy4huk_1-8-rgb_front`, whose reference is dense with quantities
  ("1/2 cup," "1 1/2 cup," "10 hours," "1 1/2 to 2 [hours]"). The
  prediction contains zero matching numbers ("one of the bottles of
  tomatoes"). No clip in this benchmark shows a correctly recovered
  number.
- **Names/fingerspelling: no confirmed correct recovery; one clear
  fabrication.** This 19-clip subset contains no reference with an
  obvious fingerspelled proper name to test against (unlike the internal
  corpus's `1252` case, where SignCaption correctly recovered "Greg" and
  "Sara" — not reproducible here, no equivalent example exists in this
  public subset, consistent with what OpenSLT's own 19-clip report also
  found). One prediction (`G1lNlhjWC1I_16_17-8-rgb_front`) invents a
  specific, unusual proper noun ("Cichlids," a fish genus) that appears
  nowhere in its reference — a fabrication, not a recovery.
- **Short vs. long clips — duration correlates strongly with
  truncation, not with topic accuracy:**
  - **Every clip ≥15.81s (12 of 12) was truncated mid-sentence** by the
    `max_new_tokens=100` decoding cap — predictions end mid-clause or
    mid-word with no terminal punctuation (e.g., "...because they're kind
    of like a b", "...we're going to go ahead and").
  - **Only 1 of the 7 clips under 10s** was truncated the same way; the
    other 6 completed a full sentence ending in a period (sometimes
    after repeating a clause, sometimes cleanly).
  - **Topic fabrication itself does not correlate with duration** — it is
    present in every clip regardless of length. Duration predicts
    whether the *output completes*, not whether it's *correct*.
  - This points at `max_new_tokens=100` being systematically too small
    for this benchmark's longer references (several reference sentences
    exceed 100 English words) — a decoding-budget mismatch, not
    something this evaluation tuned or worked around (per instructions:
    decoding parameters were left exactly as documented throughout).

## OpenSLT vs. Uni-Sign — same 19-clip benchmark, apples-to-apples

| | OpenSLT (Phase 1) | Uni-Sign (this run) |
|---|---|---|
| Clips scored | 18/19 | **19/19** |
| Corpus WER | 1.1637 | **0.948** (lower = better) |
| Corpus CER | 0.8675 | **0.7606** (lower = better) |
| Corpus SacreBLEU | ~0.93–0.96 | **3.13** (higher = better) |
| Corpus chrF | ~17.11–19.59 | **20.34** (higher = better, roughly tied at the high end) |
| Dominant failure style | Broken/malformed tokens, fluency itself breaks down | Fluent, grammatical, but topically fabricated; frequent repetition loops and mid-sentence truncation |
| Handles the 1024-frame-limit clip | No (hard config limit, clip dropped) | Yes (subsampling, no hard limit hit) |

**Uni-Sign has lower WER/CER and higher SacreBLEU/chrF than OpenSLT on
this identical 19-clip benchmark, and additionally scores one clip
OpenSLT's own pipeline cannot handle at all.** This is a clear,
apples-to-apples numerical improvement over the entire metric set — not
a mixed or ambiguous result. **This is a materially different picture
than the n=1 smoke test suggested** (where the two systems looked roughly
comparable, with OpenSLT even marginally ahead on WER/CER on that single
clip) — the n=1 result did not generalize to the corpus, which is exactly
why the fuller run was worth doing.

**Neither system produces meaningfully usable translations.** A corpus
WER near or above 1.0 means the total edit distance meets or exceeds the
total reference length — even Uni-Sign's improved 0.948 means, on
average, correcting a Uni-Sign prediction to match the reference would
require roughly as many edits as the reference has words. Both systems'
predictions consistently fabricate unrelated content; Uni-Sign's failure
mode is more fluent-sounding (higher chrF, no broken tokens) but not more
*correct* (topic preservation is ~0% for both).

## Interpretation

- **Uni-Sign materially improves over OpenSLT on this benchmark by every
  computed metric.** This is a real, disclosed, apples-to-apples finding
  on the frozen 19-clip corpus — not a marginal or noisy difference (WER
  gap 0.948 vs. 1.1637 is a ~19% relative reduction; SacreBLEU gap is
  roughly 3x).
- **This improvement does not amount to "good" or "usable" translation
  quality.** Both systems are far from production-viable on this
  benchmark: near-universal topic fabrication, no number recovery, no
  confirmed fingerspelling recovery, and (for Uni-Sign specifically) a
  decoding-budget truncation problem on every clip over 15 seconds.
- **The `max_new_tokens=100` truncation pattern is a concrete, fixable-in-
  principle lead** for anyone continuing this line of work (raising the
  token budget for longer clips) — but that would be a decoding-parameter
  change this evaluation was explicitly instructed not to make, so it is
  reported as an observation, not something acted on here.

## Licensing limitation for production use (restated — unchanged from the one-clip result)

**This experiment does not authorize or suggest Uni-Sign be integrated
into Curify's production translator, regardless of the metric
improvement documented above.**

- The `how2sign_pose_only_slt.pth` checkpoint is **CC BY-NC-4.0**
  (non-commercial only). Curify's production ASL translator is a
  commercial product.
- The Uni-Sign **code repository has no LICENSE file**
  (confirmed at the pinned commit
  `eed438bcb49e30405cd6ccdfcccca330c134e830`).
- This remains **research/evaluation only**. No Curify production code
  was modified or touched by this experiment. A clearer numeric win over
  OpenSLT does not change this boundary — the licensing terms would need
  to be independently resolved before any production path could even be
  considered.

## Exact command run

Same environment and checkpoint as the one-clip smoke test; a batch
driver (`demo/batch_inference_cpu_patched.py`, loads the model once and
loops over clips instead of reloading per clip — a pure batching
convenience, no model/decoding change) was used instead of 19 separate
process invocations, purely to avoid reloading mT5-base 19 times:

```bash
cd <scratchpad>/unisign_run/repo   # pinned to commit eed438bcb49e30405cd6ccdfcccca330c134e830
PYTHONPATH="$(pwd)" python demo/batch_inference_cpu_patched.py \
  --manifest_csv "asl-translator/data/public_benchmarks/how2sign/manifest.csv" \
  --videos_root "asl-translator/data/public_benchmarks/how2sign/videos" \
  --finetune "<scratchpad>/unisign_run/checkpoints/how2sign_pose_only_slt.pth" \
  --output_json "<scratchpad>/unisign_run/results_19clip.json" \
  --dataset How2Sign
```

Full raw stdout: `raw_output_19.txt` in this folder.
