# OpenSLT + Uni-Sign — full frozen How2Sign v2 benchmark run, 2026-09-02

**Scope: Phase 2, first two systems only.** Runs the same OpenSLT and
Uni-Sign checkpoints/configs verified in the one-clip smoke tests against
the full frozen `how2sign_v2` benchmark (N=128, `FREEZE.sha256`
`16c41282b21928e36e4c5481d8c3de48d56794accbb091fde67698dd2963411a`,
unchanged — verified below). No decoding parameter was tuned after seeing
any benchmark output. No Gemini, SpaMo, or SSVP-SLT run. No PR, no commit
(pending review). Full per-clip raw predictions, status, and metadata live
under `asl-translator/evaluation/results/how2sign_v2/{openslt,unisign}/`.

---

**Reporting notes, stated explicitly up front:**
- The **primary OpenSLT-vs-Uni-Sign comparison is the matched-126 subset** (§3) — the only apples-to-apples set, since OpenSLT cannot process 2 of the 128 clips at all. Uni-Sign's full-128 result (§1) is preserved separately and is the correct number for any claim about Uni-Sign alone.
- **Both models remain far from production quality.** Corpus WER is at or above 1.0 for both on every subset in this report — the total edit distance meets or exceeds the total reference length. Neither produces translations a viewer could rely on.
- **"Number-token presence recovered" (§6) is not number correctness.** It only checks whether *any* digit/number-word appears anywhere in the prediction, not whether the *right* number was produced.
- **Uni-Sign's `max_new_tokens=100` truncation pattern (§6) was observed, not corrected.** The cap was not raised, and the frozen benchmark was not altered, truncated, or filtered in response.
- **The benchmark's `question`/`number_token`/`proper_noun_fingerspelling`/`fast_signing` tags are heuristics from `manifest.csv`, not human ground truth.** They are used here only as pre-existing, unmodified category labels for breakdown purposes.

## 1. Uni-Sign full-128 aggregate results

| | |
|---|---|
| n_total | 128 |
| n_success | **128** |
| n_failure | **0** |
| Corpus WER | **0.9819** |
| Corpus CER | **0.7608** |
| Corpus SacreBLEU | **5.39** |
| Corpus chrF | **22.75** |
| Total wall-clock | **4170.6s (~69.5 min)** (incl. one-time pose-extractor init 0.2s, mT5 model construction 14.4s, checkpoint load 1.4s) |
| Sum of per-clip processing time | 4154.4s |
| Mean per-clip runtime | 32.46s |
| Median per-clip runtime | 24.25s |
| Peak RSS | **3621.8 MB (~3.54GB)** |

No failures of any kind — all 128 clips produced a prediction.

## 2. OpenSLT 128-attempt / successful-subset results

| | |
|---|---|
| n_total (benchmark size) | 128 |
| n_success | **126** |
| n_failure | **2** |
| Corpus WER (over 126 successes) | **1.0246** |
| Corpus CER | **0.7689** |
| Corpus SacreBLEU | **0.96–0.98** (fairseq's own `--scoring sacrebleu`: 0.98; independent `sacrebleu==2.3.1` cross-check: 0.96 — same small tokenization-driven gap the pilot documented) |
| Corpus chrF | **18.59** |
| Total wall-clock | **96.55s** (single batched `fairseq-generate` call, `--batch-size 32`) |
| Batch-average per-clip | ~0.77s (not independently measured — see note below) |
| Peak RSS | **1,639,858,176 bytes (~1.53GB)** |

**Explicit failure list (2/128):**

| Clip | Reason |
|---|---|
| `G3EfBFwsOpE_3-10-rgb_front` (1.85s) | **MISSING_OFFICIAL_FEATURE** — not present in OpenSLT's officially released I3D test-feature archive (Dataverse file 51538, MD5 `ce7d020f...`, re-verified this session). Not regenerated, not substituted, per instructions. |
| `fZK9hW81XCU_9-10-rgb_front` (1.83s) | Same reason. |

Per-clip timing note: `fairseq-generate` decodes the whole batch in one call; splitting into 128 individual invocations to get true per-clip timing would multiply model-load overhead 128x and measure something different from how the pipeline is actually meant to run — same limitation the pilot's own 19-clip run documented. Total batch wall-clock (96.55s) and the batch-average derived from it are reported instead of a true per-clip distribution.

## 3. Matched-126 comparison — the primary apples-to-apples table

Uni-Sign recomputed on **exactly** the 126 clips OpenSLT has official features for (excludes the 2 `MISSING_OFFICIAL_FEATURE` clips from both sides).

| Metric | OpenSLT matched-126 | Uni-Sign matched-126 |
|---|---|---|
| Clips scored | 126 | 126 |
| Corpus WER | **1.0246** | **0.9801** (lower = better) |
| Corpus CER | **0.7689** | **0.7601** (lower = better) |
| Corpus SacreBLEU | **0.96–0.98** | **5.40** (higher = better) |
| Corpus chrF | **18.59** | **22.83** (higher = better) |
| Total runtime (this subset) | ~95.8s (batch, 126/128 of the full 96.55s batch call) | 4133.4s (~68.9 min, sum of per-clip) |
| Peak RSS | ~1.53GB | ~3.54GB |

**Uni-Sign has lower WER/CER and higher SacreBLEU/chrF than OpenSLT on the identical matched-126 subset** — consistent with, and now at ~7x the sample size of, the pilot's 19-clip finding (WER gap there: 0.948 vs 1.164; here: 0.980 vs 1.025 — a smaller relative gap on this benchmark, but the same direction on every metric). Neither system is close to usable translation quality (WER near/above 1.0 for both).

Uni-Sign's separately-preserved **full-128** result (§1) is the correct number for any claim about Uni-Sign alone, since it includes 2 clips OpenSLT cannot process at all.

## 4. Per-category breakdown

**Heuristic tags are heuristics, not ground-truth semantic categories** — `number_token`, `proper_noun_fingerspelling`, and `fast_signing` are text/duration-derived proxies from `manifest.csv`, exactly as labeled there. `question` is an official text feature (literal "?" suffix). Duration buckets are the official `duration_s` field. Denominators are shown for every category because OpenSLT's 2 missing-feature clips can and do reduce them.

### OpenSLT

| Category | n in benchmark | n scored | n failed | Corpus WER |
|---|---|---|---|---|
| duration <2s | 14 | 12 | 2 | 1.0204 |
| duration 2-5s | 47 | 47 | 0 | 1.0249 |
| duration 5-15s | 47 | 47 | 0 | 0.9832 |
| duration 15-31s | 20 | 20 | 0 | 1.0707 |
| question (official) | 12 | 11 | 1 | 1.1260 |
| number token [HEURISTIC] | 32 | 32 | 0 | 1.0750 |
| proper-noun/fingerspelling proxy [HEURISTIC] | 28 | 28 | 0 | 1.0768 |
| fast-signing proxy [HEURISTIC] | 13 | 13 | 0 | 0.9006 |
| plain/no-flag | 60 | 59 | 1 | 0.9912 |

Both `MISSING_OFFICIAL_FEATURE` clips are <2s; one is also tagged `question`, the other `plain/no-flag` — that's why those three categories each show exactly one fewer scored clip, not a parsing inconsistency.

### Uni-Sign

| Category | n in benchmark | n scored | n failed | Corpus WER |
|---|---|---|---|---|
| duration <2s | 14 | 14 | 0 | 1.3578 |
| duration 2-5s | 47 | 47 | 0 | 1.0706 |
| duration 5-15s | 47 | 47 | 0 | 0.9574 |
| duration 15-31s | 20 | 20 | 0 | 0.9057 |
| question (official) | 12 | 12 | 0 | 1.2500 |
| number token [HEURISTIC] | 32 | 32 | 0 | 0.9134 |
| proper-noun/fingerspelling proxy [HEURISTIC] | 28 | 28 | 0 | 0.9553 |
| fast-signing proxy [HEURISTIC] | 13 | 13 | 0 | 0.8619 |
| plain/no-flag | 60 | 60 | 0 | 1.0124 |

**Observation, not a claim about the tags' semantic validity:** both systems score *worse* on the shortest clips (<2s: OpenSLT 1.02, Uni-Sign 1.36) and *better* on longer ones (15-31s: OpenSLT 1.07 — noisy, small n; Uni-Sign 0.91) — likely the same short-reference WER-denominator artifact the pilot documented (a 1-3 word reference makes any normal-length output register as catastrophic WER), not evidence either system handles short clips worse in a meaningful sense. `question`-tagged clips score worse than average for both systems (OpenSLT 1.13 vs 1.02 overall; Uni-Sign 1.25 vs 0.98 overall) — questions in this benchmark tend to be short references, same caveat applies.

## 5. All failures/skips

**OpenSLT: 2/128**, both `MISSING_OFFICIAL_FEATURE` (§2 table). No other failure of any kind — no clip exceeded the `max_source_positions=1024` limit (max observed: 1034 frames does not occur in this benchmark's covered set; the largest was well under 1024 for every one of the 126 covered clips, checked before running).

**Uni-Sign: 0/128.** No failures.

No clip was silently dropped from either model's per-clip results file — both `MISSING_OFFICIAL_FEATURE` rows are present in `openslt/per_clip_results.csv` with `status=FAILED` and an explicit `failure_reason`, not omitted.

## 6. Qualitative failure summary

Deterministic selection criteria throughout: best/worst by WER; repetition = any 3-6 word n-gram appearing ≥2 times in a prediction; numbers = digit or spelled-out number word in reference/prediction; proper-noun cases = the benchmark's own heuristic tag; long-clip = the 8 longest clips by duration. No cherry-picking.

### Best / worst (both systems)

**OpenSLT best** (lowest WER, still catastrophic in absolute terms — WER 0.6-0.77):
- `g3ZgF8gdfLo_0-3` (WER 0.60): ref *"In this segment we're going to talk about how to load your still for d[istillation]..."* → *"in this enough we're/ to three about how to hours the flavor for the b..."* — topic partially echoed ("segment"→"enough", garbled) but not recovered.

**OpenSLT worst** (WER up to 2.25): `g1xdqxCZxTg_6-3` ref *"Do they speak English?"* → *"you want to make see that you' take got."* — short reference, unrelated fragment.

**Uni-Sign best**: `g2nvBjp0loQ_4-3` (WER **0.17**, the single best result across both systems) — ref *"It's a good idea to get a nice easy body sweat."* → *"It's a good idea to have a really nice, easy body sweat."* Near-perfect paraphrase; a genuine bright spot, not representative of the corpus.

**Uni-Sign worst**: `g1xdqxCZxTg_6-3` (WER **6.0**, same clip as OpenSLT's worst) → *"My favorite drink is iced iced iced iced iced iced iced iced iced iced..."* — repetition-loop hallucination on a 4-word reference.

### Topic fabrication / semantic drift

Universal in both systems, consistent with the pilot's own finding at 19 clips — e.g. Uni-Sign's `g3ZgF8gdfLo_0-3`: ref about *"load your still for distillation"* → pred about *"talk about how to fish"* (fabricated, unrelated topic, fluent delivery). OpenSLT's fabrications are typically less fluent (broken tokens) but equally off-topic.

### Repetition loops

| | OpenSLT | Uni-Sign |
|---|---|---|
| Rate (any 3-6gram repeated ≥2x) | **32.5%** (41/126) | **37.5%** (48/128) |

Most extreme case, either system: **OpenSLT `G06Irzcwxiw_5-1`** — the word "down," repeated **46 times** consecutively in one prediction, a stark degenerate-decoding case. Uni-Sign's worst repetition is the `g1xdqxCZxTg_6-3` "iced" loop above (10 repeats visible in the truncated excerpt).

### Number errors

| | OpenSLT | Uni-Sign |
|---|---|---|
| Reference clips containing a number | 48 (of scored) | 48 |
| Any number token recovered in prediction | 22/48 (45.8%) | 16/48 (33.3%) |

"Recovered" here means *any* digit/number-word appears in the prediction — not that the *correct* number was recovered; this is a coarse presence check, not a correctness check (neither system's raw predictions were manually verified for number *accuracy*, only number *presence*, given the volume). Even by this loose bar, most number-bearing references get no number back at all in the prediction.

### Proper-name/fingerspelling-proxy failures

Both systems score worse-than-average on this heuristic category: OpenSLT 1.077 (vs. 1.025 overall), Uni-Sign 0.955 (vs. 0.982 overall — here Uni-Sign is actually *slightly better* than its own overall average, unlike OpenSLT). Worst case for both: `g1xdqxCZxTg_6-3` (shared worst-overall clip, coincidental — its "proper noun" flag is a false-positive heuristic trigger on "English," not a real fingerspelling case). A cleaner example: Uni-Sign on `G3di9jJTqDs_0-10`, ref *"This cocktail is called Downshift."* → *"That's why we're going to use onion."* — the proper noun ("Downshift") is entirely absent, replaced with a fabricated topic.

### Long-clip degradation

**Uni-Sign shows a strong, reproducible truncation pattern tied to `max_new_tokens=100`** (not raised, per instructions):

| Duration bucket | Truncated (no terminal punctuation) |
|---|---|
| <5s | 2/61 (3.3%) |
| 5-15s | 5/47 (10.6%) |
| 15-31s | **13/20 (65.0%)** |

This directly reproduces the pilot's 19-clip finding (there: 12/12 clips ≥15.81s truncated) at a larger scale, with a somewhat lower rate here (65% vs 100%) — plausibly because more of this benchmark's "long" clips have shorter/simpler references than the pilot's selection. **OpenSLT shows no equivalent length-triggered truncation** (it isn't autoregressive-token-budget-limited the same way), but its longest clips do show elevated repetition-loop incidence, consistent with the pilot's own observation that beam search degrades on longer I3D feature sequences.

## 7. Total runtime and memory (both systems combined)

| | OpenSLT | Uni-Sign |
|---|---|---|
| Total wall-clock | 96.55s | 4170.6s (~69.5 min) |
| Peak RSS | ~1.53GB | ~3.62GB |

Combined wall-clock for both full runs: **~71 minutes**. Both ran sequentially on CPU only, no GPU/MPS, on the same Apple Silicon Mac used throughout this project.

## 8. Exact files created

All under the repo, all currently **untracked** (nothing staged or committed):

```
asl-translator/evaluation/results/how2sign_v2/
├── openslt/
│   ├── predictions/<128 files>.json      (per-clip prediction; 2 have empty segments + failure_reason)
│   ├── per_clip_results.csv / .json       (128 rows: 126 scored + 2 FAILED)
│   ├── corpus_summary.json
│   ├── category_breakdown.json
│   ├── failure_analysis.json
│   ├── run_metadata.json                  (checkpoint/repo/env/command/deviations)
│   └── raw_generation_126.txt             (unmodified fairseq-generate stdout, all 126)
└── unisign/
    ├── predictions/<128 files>.json
    ├── per_clip_results.csv / .json       (128 rows, all success)
    ├── corpus_summary.json                (full-128)
    ├── matched126_summary.json            (matched-126 subset)
    ├── category_breakdown.json
    ├── failure_analysis.json
    ├── run_metadata.json
    └── batch_run_128.log                  (full timing/RSS log, all 128 clips)

docs/daily_report/9.2/asl-baselines/
└── HOW2SIGN_V2_OPENSLT_UNISIGN_FULL_RESULTS.md   (this file)
```

**Repository-convention note:** `asl-translator/evaluation/.gitignore` still ignores `results/` wholesale, unmodified (the existing convention for regeneratable model-output data, same rule that already applies to Curify's own `asl_corpus` prediction outputs) — the full raw predictions/logs above stay untracked by design. A separate, compact **tracked evidence package** was created instead at `docs/daily_report/9.2/asl-baselines/results/` (predictions as JSONL, per-clip and aggregate metrics as CSV, failures as CSV, full run metadata as JSON — see that directory's own files) so the results are reproducible/auditable from git history without committing raw per-clip logs or requiring the `.gitignore` rule to change.

## 9. git status

```
$ git status --short
(no output for anything touched by this run except the two new,
 untracked directories/files below)

?? asl-translator/evaluation/results/how2sign_v2/   (gitignored by evaluation/.gitignore's "results/" rule — see §8 note)
?? docs/daily_report/9.2/
```

No file under `asl-translator/data/public_benchmarks/how2sign_v2/`, `asl-translator/data/public_benchmarks/how2sign/` (`pilot_v1`), `asl-translator/data/asl_corpus/`, or `asl-translator/asl-eval/` was modified. `git diff --stat` is empty.

## 10. FREEZE.sha256 confirmation

```
$ cat asl-translator/data/public_benchmarks/how2sign_v2/FREEZE.sha256
16c41282b21928e36e4c5481d8c3de48d56794accbb091fde67698dd2963411a
```

Independently recomputed from the tracked `FREEZE_CHECKSUMS.sha256` this session: **exact match**. `manifest.csv` still 128 data rows. **Unchanged.**
