# OpenSLT — 19-clip frozen How2Sign benchmark, aggregate baseline result

**2026-08-31.** Runs the official OpenSLT How2Sign checkpoint
(`checkpoint.best_reduced_sacrebleu_3.5401.pt`) on all 19 clips of the frozen
`asl-translator/data/public_benchmarks/how2sign/manifest.csv` benchmark, CPU
only, official decoding config, same environment/checkpoint as the one-clip
milestone (`OPENSLT_ONE_CLIP_RESULT.md`) — **that one clip's result is
reproduced identically here as row 0**, not treated as a separate run.
Nothing trained, no private Curify data, no parameter tuned against results,
19-clip selection untouched, nothing committed.

---

## A. Reproduction / engineering conclusion

**The pipeline reproduces cleanly and deterministically at batch scale.**
Same environment (`openslt-cpu-arm64`), same checkpoint, same official
`Taskfile.yml` `generate:` flags (`--seed 48151623 --beam 5 --max-tokens
16000 --sacrebleu-tokenizer 13a`, etc.), with the same two zero-effect
additions as the one-clip run (`--cpu`, `--num-workers 0` — see
`OPENSLT_ONE_CLIP_RESULT.md` for why `--num-workers 0` is required on
macOS). One new engineering fact surfaced at batch scale that a single clip
couldn't reveal:

**18 of 19 clips produced output; 1 was excluded by the official config
itself, not by any choice made here.** `G33aqW3DLpc_1-10-rgb_front` (30.67s,
our longest clip, 1034 I3D feature frames) exceeds the official
`--max-source-positions 1024` limit embedded in the checkpoint's own config
and the Taskfile's documented `generate:` target. Confirmed directly (not
inferred) by re-running that one clip without
`--skip-invalid-size-inputs-valid-test`:
```
Exception: Size of sample #0 is invalid (=(1034, 426)) since max_positions=(1024, 1024),
skip this example with --skip-invalid-size-inputs-valid-test
```
Per instructions, **this was not worked around** — raising
`--max-source-positions` would be tuning the official config against a
specific clip, which was explicitly out of bounds. `--skip-invalid-size-inputs-valid-test`
is itself part of the official documented command, so the batch run behaved
exactly as the released model+config is meant to behave: it silently drops
inputs it cannot process. This is a genuine, disclosed limitation of the
released checkpoint on our benchmark, not a bug in this reproduction.

**Cross-check against the paper's own official analysis script:**
`examples/sign_language/scripts/analyze_fairseq_generate.py` was run against
the same raw output (one path override needed — the script hardcodes the
original author's cluster path for `SignToTextConfig.data`; pointed at our
local I3D_DIR instead, the same class of override already applied via
`--sentencepiece-model`/`--data` on the CLI, not a decoding change). It
independently parsed the **same 18 clips** (confirming the exclusion is not
an artifact of this project's own parsing) and produced BLEU **0.93** vs.
fairseq's own built-in scorer's **0.96** for the same 18-clip set — both
very low, consistent with each other, the small gap explained by the
official script's additional truecasing/detokenization step before scoring.
One missing runtime dependency was found and installed to run this script:
the `truecase` package needs the NLTK `punkt_tab` tokenizer resource, not
listed in `environment.yml`; fetched via `nltk.download('punkt_tab')` (a
small, standard public NLP resource, not model weights, not private data).

**Runtime:** 25 seconds wall-clock for the full 18-clip batched
`fairseq-generate` call (model load + all decoding + scoring), on CPU, no
GPU/MPS. Per-clip timing is **not separately instrumented** in a single
batched run — fairseq's DataLoader processes the whole batch together, and
splitting into 19 individual invocations to get true per-clip timing would
multiply model-load overhead 19x and measure something different from how
the official pipeline is actually meant to run. The one-clip milestone's
isolated 4-second measurement (§ below) is the only true single-clip
reference point available.

**Engineering verdict: the release is reproducible end-to-end on this
platform**, with the `--num-workers 0` and Cython-build fixes from the
one-clip milestone still in force, plus one further, expected finding —
sequence-length limits from the model's own training config apply, and one
clip in our fixed benchmark exceeds them.

---

## B. Translation-quality conclusion

**The released checkpoint does not produce usable ASL→English translations
on this benchmark.** Every metric is far below anything indicating working
translation, and this is consistent across clips, not a few outliers pulling
down an otherwise-reasonable average.

| Metric | Value | N |
|---|---|---|
| Corpus WER (pooled: total edit ops / total ref words) | **1.1637** | 18 clips |
| Corpus CER (pooled) | **0.8675** | 18 clips |
| Corpus sacreBLEU (fairseq's own `--scoring sacrebleu`, cross-checked independently — exact match) | **0.96** (21.1/3.0/0.3/0.0, BP=1.000) | 18 clips |
| Corpus sacreBLEU (official `analyze_fairseq_generate.py`, truecased) | **0.93** | 18 clips |
| Corpus chrF | **19.59** | 18 clips |
| Corpus chrF (official script, word_order=2) | **17.11** (reduced/blacklist-filtered: 9.14) | 18 clips |

A corpus WER **above 1.0** means the total edit distance exceeds the total
reference word count — the predictions aren't just wrong, they're often
longer and more repetitive than the references they're supposed to match.

**This does not, by itself, mean OpenSLT is a bad model in general** — the
paper's own reported How2Sign test BLEU (from `ASL_PRETRAINED_BASELINE_SEARCH.md`)
is itself modest, and this checkpoint (`baseline_6_3_dp03_wd`, not the
paper's absolute best variant) was one of several released checkpoints. What
this result establishes is narrower and solid: **on this specific released
checkpoint, run exactly as documented, on our fixed 19-clip subset of the
official How2Sign test split, translation quality is very poor** — a
legitimate, reproducible baseline number, not a claim about the ceiling of
this class of model.

**No comparison to Curify's own model is made here.** Curify's model has
never been run on these exact 19 How2Sign clips (a separate, later,
explicitly-gated step) — comparing today's numbers to Curify's numbers on
different clips (e.g. the internal `asl_corpus`) would not be apples-to-apples
and is deliberately not done, per instructions.

---

## Qualitative error analysis

Based on all 18 scored predictions (`OPENSLT_19CLIP_RESULTS.csv`), reviewed
in full — not a sample.

- **Semantic correctness: effectively absent.** In all 18 cases, the
  prediction's actual topic/action does not match the reference's. E.g. ref
  "we press this button, which opens the door" → hyp about "the food"; ref
  about cardio exercise machines → hyp repeating "your together." The model
  produces syntactically English-shaped sentences with essentially no
  content overlap with what was actually signed.
- **Fluent but unsupported English — the dominant failure mode.** Nearly
  every hypothesis reads as plausible, grammatical-ish English on its own
  ("you're going to...", "we're going to...", "I want to...") while
  asserting content invented relative to the reference. This matches the
  fabrication-risk pattern this project's own internal work has already
  flagged for Curify's model (`asl-1252-frame-inspector.html`,
  `CONTAMINATION.md` discussion) — it appears to generalize across systems,
  not be specific to one architecture.
- **Numbers: not tested meaningfully — mostly tokenization artifacts.** No
  clip in this 19-item subset centers on numeric content the way the
  internal 1252 case does. What *does* appear repeatedly is a BPE
  detokenization artifact — digits merging into the following/preceding word
  with no space (`piece0`, `get2`, `into2`, `tom`, `toal`, `tomediapipe`,
  `thep`) — a formatting bug in how SentencePiece subword boundaries are
  rejoined, not evidence of numeric reasoning one way or the other.
- **Names / fingerspelling: no examples in this subset.** All 19 How2Sign
  clips are instructional content (aileron mechanics, ukulele, chickpea
  prep, boxing stance, cardio equipment, clay sculpture, etc.) — none
  contain a fingerspelled proper name. Unlike the internal corpus's 1252
  case (names "Greg"/"Sara"), this benchmark cannot speak to fingerspelling
  quality one way or the other.
- **Omissions: near-total.** Essentially none of the reference's actual
  content survives into any prediction — this isn't partial omission of
  detail, it's replacement with unrelated content.
- **Hallucination — one stark, unambiguous example.** Clip
  `8kAWy2YodzQ_16_17_18-1-rgb_front`: reference is three words, *"That's
  pretty good."* The prediction is a 122-word, heavily repetitive block
  ("...this one here, this is a put idea of this one here, this is this is
  a put idea of this one here...") — WER 17.0, the batch's worst result by
  more than 7x over the next-worst. This is the cleanest hallucination case
  in the set: a short reference, paired with a long, internally-repetitive,
  content-free generation.
- **Degenerate repetition loops — a systematic pattern, not isolated to one
  clip.** The same failure shape recurs across several of the longer clips:
  `FZbyRzy4huk_1-8` ("...a keeping of those, a keeping of those, a keeping
  of those..."), `G3VM7etNABI_2_3-10` ("...your together, your together,
  your together..."), `g3ZluRtRXVc_5-3`, `FzmL8SL6Bow_0-8`. Beam search
  appears to fall into repeating short phrase loops disproportionately on
  longer inputs — consistent with (though this data alone doesn't prove) the
  model's own attention/decoding losing traction over longer feature
  sequences.
- **Short vs. long clips:** the three best-WER clips span the duration range
  (5.27s, 9.23s, 19.19s) — duration alone does not predict WER. What *does*
  correlate with duration is the repetition-loop failure mode above: 4 of
  the 5 clips over ~24s show visible repetition loops; none of the clips
  under 10s do. The single catastrophic outlier (`8kAWy2YodzQ`, WER 17.0) is
  a mid-length clip (21.13s) whose reference is unusually short relative to
  its duration — likely a known How2Sign auto-alignment quirk (a short
  spoken interjection aligned to a longer video segment), not something this
  reproduction controls for, but worth naming as context rather than
  attributing entirely to model failure.
- **General action/topic preserved? No**, in any of the 18 cases, to any
  degree that would be useful. Even the "best" (lowest-WER) predictions
  don't track the reference topic — WER 0.82 is still catastrophic in
  absolute terms; "best" here is relative, not good.

---

## Best 3 / worst 3 (selected by WER, not cherry-picked)

Selection metric stated up front, not chosen after looking at content:
**word error rate**, ascending for best, descending for worst, over the 18
scored clips (the excluded clip has no WER and cannot be ranked).

### Best 3 (lowest WER)

| Rank | Clip | Duration | WER | Reference | Prediction |
|---|---|---|---|---|---|
| 1 | `FZCEymcpq7I_0_1-1-rgb_front` | 9.23s | 0.8182 | "ok. we're going to demonstrate the sand wedge here. so, we've got these nice targets out there..." | "no we're/ tovideo you how tove in here and we're/ tove a first d on there, and we're/ tove that first and difficult art." |
| 2 | `FzOQMA-CVPc_9-2-rgb_front` | 19.19s | 0.8246 | "but as far as that goes, you'll just want to make sure it's really fun, glamorous night..." | "as3 as the dog position know, you want to make see you're edge with your dark, and you're oil to play start..." |
| 3 | `-g0iPSnQt6w_11-1-rgb_front` | 5.27s | 0.8333 | "what you're going to do is you're going to take both your arms and they're going to come underneath your legs." | "so, what i' be/ to do is i' be/ to from all together pressure the kick." (= the one-clip milestone result) |

Even at "best," roughly 4 in 5 reference words are wrong, missing, or
displaced.

### Worst 3 (highest WER)

| Rank | Clip | Duration | WER | Reference | Prediction |
|---|---|---|---|---|---|
| 1 | `8kAWy2YodzQ_16_17_18-1-rgb_front` | 21.13s | **17.0** | "that's pretty good." | "now we're/ to three about this one here, this is what we're/ to do here is we're/ to right this one here, this is a put idea of this one here, this is this is a put idea of this one here, this is what we're/ to do here, this is this is this one here, this is this one here, this one here." |
| 2 | `-g45vqccdzI_5-1-rgb_front` | 7.01s | 2.25 | "we press this button, which opens the door." | "so, you'gb good, this is a allow am, thing is more measure love way the long of the food." |
| 3 | `FZbyRzy4huk_1-8-rgb_front` | 24.45s | 2.2 | "we're going to use 1/2 of cup of chickpeas soak in 1 1/2 cup of water..." | "i' be/ to make a rub in this anything and i' be/ to rightk a keeping of those in the body colors of those, and i want tove it in the body colors of more state or ak more state or ak state or ak more state..." |

---

## Excluded item

| Clip | Duration | Reason |
|---|---|---|
| `G33aqW3DLpc_1-10-rgb_front` | 30.67s | 1034 I3D feature frames > official `max_source_positions=1024`; dropped by the official `--skip-invalid-size-inputs-valid-test` flag. No prediction produced; excluded from all corpus-level metrics (N=18, not 19). Not worked around — see §A. |

---

## Files

- `OPENSLT_19CLIP_RESULTS.csv` — all 19 rows (18 scored + 1 excluded), per-clip WER/CER/sentence-BLEU/chrF.
- `raw_generation_19.txt` — unmodified `fairseq-generate` stdout for the full batch (T-/H-/D-/P- lines + final corpus BLEU line).
- `OPENSLT_ONE_CLIP_RESULT.md` / `raw_generation.txt` — the earlier one-clip milestone; its result is row 0 of this batch, reproduced identically here (same clip, same hypothesis, same WER 0.8333).

## Scope / non-modification note

- The frozen 19-clip selection (`manifest.csv`) was not modified.
- No decoding parameter was tuned, before or after seeing results — every
  flag matches the Taskfile's `generate:` target except `--cpu` and
  `--num-workers 0`, both zero-effect on decoding (see
  `OPENSLT_REPRODUCTION_PLAN.md` §11.6).
- No training or fine-tuning occurred.
- No private Curify video was used — all 19 clips are public How2Sign test-split data already staged in `public_benchmarks/`.
- Temporal IoU was not computed — OpenSLT outputs sentence-level text with no timestamps.
- Nothing was staged, committed, or pushed.
