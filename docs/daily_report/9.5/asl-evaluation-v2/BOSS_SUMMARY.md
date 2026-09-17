# ASL How2Sign v2 Curify baseline — frozen milestone, 2026-09-05

**Audience:** decision-maker skim. **Scope:** evaluation only — no production
code changed, no model calls made in this report, nothing staged or
committed.

---

## 0. What this document is

This freezes the completed Curify How2Sign v2 evaluation as a clean
repository milestone, before starting a temporal (higher-FPS) sampling
ablation. **No Gemini calls were made and no benchmark clips were rerun to
produce this report** — every number below was independently re-read and
recomputed from the already-saved results in
`asl-translator/evaluation/results/how2sign_v2/curify_gemini_3_6_2026_09_04/`
and cross-checked against the pre-existing OpenSLT/Uni-Sign result files.
All figures matched exactly on re-verification (see `BASELINE_METRICS.json`
for the full trace).

---

## 1. Which config this is — and which one it is *not*

- **`production_2026_08_29`** (`gemini-2.5-flash`) is Curify's real,
  historical production configuration. **It is preserved and unchanged** in
  `asl-eval/run_current_model.py` — diffed directly to confirm its own
  config-dict entry was not touched by this work.
- It **could not be reproduced** with the credential available in this
  environment: `generate_content` on `gemini-2.5-flash` returns `404
  NOT_FOUND` ("no longer available to new users") for the current
  credential/project, even though `models.list()`/`models.get()` both list
  that model as generation-capable. This is a **server-side, provider-side
  entitlement block**, not a bug in our code, prompt, or sampling pipeline.
- **`evaluation_2026_09_04_gemini_3_6`** (`gemini-3.6-flash`) is a
  **separately labeled, runnable evaluation baseline** — everything below
  is measured on this config. **It is not `production_2026_08_29` and must
  never be reported as if it were.** It reuses production's exact
  prompt/sampling/batching/dedup/output-schema; only the model and its
  decoding knobs changed for the Gemini 3.x migration.

## 2. Frozen benchmark integrity

- 128/128 How2Sign v2 clips **succeeded**, 0 failed.
- The benchmark manifest and all 260 checksummed reference/metadata files
  under `public_benchmarks/how2sign_v2/` were re-verified against
  `FREEZE_CHECKSUMS.sha256` — **zero mismatches**. The stored
  `FREEZE.sha256` fingerprint (`16c41282...`) was independently recomputed
  and matches exactly.
- The raw results directory (`asl-translator/evaluation/results/`) remains
  git-ignored, as intended — predictions and per-clip artifacts are not
  meant to live in the repo.

## 3. Headline metrics (independently re-verified)

**ALL-128** (every attempted clip):

| Metric | Value |
|---|---:|
| WER | 0.9762 |
| CER | 0.8071 |
| BLEU (sacreBLEU) | 0.1341 |
| chrF | 11.2835 |
| Substitutions | 1095 |
| Deletions | 1779 |
| Insertions | 32 |
| Mean temporal precision | 0.9922 |
| Mean temporal recall | 0.5814 |

**MATCHED-126** (the subset both OpenSLT and Uni-Sign also successfully
scored — the only scope valid for cross-system comparison):

| Metric | Value |
|---|---:|
| WER | 0.9761 |
| CER | 0.8070 |
| BLEU | 0.1346 |
| chrF | 11.3033 |
| Substitutions | 1091 |
| Deletions | 1772 |
| Insertions | 32 |

Full machine-readable version: `BASELINE_METRICS.json`. Full comparison
table: `BASELINE_SCORECARD.csv`.

## 4. Apples-to-apples comparison (MATCHED-126 only)

| System | WER | BLEU | chrF |
|---|---:|---:|---:|
| Curify (`evaluation_2026_09_04_gemini_3_6`) | **0.9761** | 0.1346 | 11.30 |
| OpenSLT | 1.0246 | 0.962 | 18.59 |
| Uni-Sign | 0.9801 | **5.40** | **22.83** |

**Curify's WER must NOT be read as "Curify outperforms Uni-Sign."** WER
alone is misleading here because Curify's error profile is deletion-
dominated (below): a system that predicts very few words has fewer chances
to substitute the wrong word, which can produce a deceptively competitive
WER without saying anything correct. BLEU and chrF — both far more
sensitive to whether the actual *content* is right — tell the real story:
Uni-Sign's BLEU is **~40x** Curify's (5.40 vs. 0.1346) and its chrF is
roughly **double** (22.83 vs. 11.30). On content correctness, Curify is
clearly the weakest of the three systems on this benchmark, not the
strongest.

Neither OpenSLT nor Uni-Sign has a temporal precision/recall metric in
their saved results (they're text-only outputs), so the temporal figures
in Section 3 are Curify-only — not part of this three-way comparison.

## 5. Curify is deletion-dominated: short, thin outputs

Aggregated over all 128 clips:

- Reference text totals **2,977 words**; Curify's predictions total only
  **1,230 words** — predictions average **41% of reference length**.
- Of all 2,906 edit operations across the corpus, **61% are deletions**
  (1,779), vs. 38% substitutions (1,095) and just 1% insertions (32).

In plain terms: Curify is not primarily *misreading* the sign content —
it's *omitting* most of it. It stops early, skips stretches of signing, or
returns a short fragment instead of a full translation, far more often
than it substitutes a wrong word for a right one.

## 6. WER distribution — no clip is a clean pass

Per-clip, across all 128 clips:

- Mean WER **0.987**, median WER **1.0**.
- **0** clips scored WER < 0.5.
- **47** clips scored 0.5 ≤ WER < 1.0.
- **81** clips scored WER ≥ 1.0.
- **1** clip produced an empty prediction (`92V3oH63zbQ_5-1-rgb_front`,
  8-word reference, 0 predicted words).

Even the single best-scoring clip in the corpus (`g2NA_eBUcH8_0-3-rgb_front`,
WER 0.75) is a truncated partial reading, not a clean translation — see
`QUALITATIVE_REVIEW_CANDIDATES.csv` for that and six other hand-picked
examples, including two "low-WER but topically wrong" cases that show WER
alone can be a misleading local signal, and the highest-insertion outlier
(a 44-word fabricated passage against a 23-word reference).

**For `FZbyRzy4huk_3-8-rgb_front`, the frozen saved prediction is
`"Tablecloth" / "Coffee"`.** An earlier ad-hoc "Tuberculosis / Drive /
Nice" output for this clip exists somewhere in prior scratch work but is
**not** from this frozen baseline and must not be cited going forward.

## 7. Temporal recall vs. precision

- Mean temporal **precision**: 0.9922 — when Curify does emit a timed
  segment, it is almost always genuinely aligned with real reference
  signing time (very few false-positive time spans).
- Mean temporal **recall**: 0.5814 — but it only covers **~58%** of total
  reference signing duration.

Read together with Section 5: Curify isn't misplacing guesses in time,
it's simply **silent across a large fraction of the video**. This is the
same deletion-dominant pattern showing up on the time axis, not just the
word axis — which is exactly why the next experiment (below) targets frame
sampling density rather than the language model's reading behavior.

## 8. Security note

A Gemini API key was accidentally printed into local Claude session
history during verification of this baseline. The local transcript
containing it was removed, and local secret scans of this repository's
changed/untracked files are now clean — no credential value appears
anywhere in the files touched by this work (see `BASELINE_METRICS.json`
→ `security_note` and the audit checklist below). No claim is made about
provider-side deletion of the key from any external system; only the local
remediation described above is asserted. The credential value itself is
not reproduced in any document.

## 9. Next controlled experiment (proposed, NOT implemented here)

**Higher-FPS temporal sampling ablation:** re-run the frozen
`evaluation_2026_09_04_gemini_3_6` config with an increased
`target_frames_per_sec` (and/or a raised `max_frame_budget`) against the
same frozen 128-clip benchmark, holding prompt/model/dedup/schema fixed, to
test whether the low temporal recall (0.58) and deletion-dominant text
output are caused by frame-sparsity rather than by the language model's
reading/generation behavior itself. **This is a proposal only — it is not
implemented, and no higher-FPS run has been performed as part of this
report.**

## 10. Final audit

| Check | Result |
|---|---|
| Benchmark/reference checksums unchanged | ✅ all 260 files match `FREEZE_CHECKSUMS.sha256`; `FREEZE.sha256` fingerprint recomputed and matches |
| `production_2026_08_29` config unchanged | ✅ confirmed by direct diff of `run_current_model.py` |
| Raw result directory remains gitignored | ✅ `asl-translator/evaluation/results/` is git-ignored |
| No API secret in changed/untracked repo files | ✅ scanned; only a key-*detection* regex exists in the new benchmark script, no key material |
| Report numbers trace back to saved outputs | ✅ every figure re-derived from `corpus_summary.json`, `corpus_summary_matched_126.json`, `per_clip_results.csv`, and the OpenSLT/Uni-Sign result files |
| Only intended files changed | ✅ see git status/diff below — the only pending changes are pre-existing (unrelated to this report) plus the 4 new report files |

---

## What is complete / what is not complete

| Item | Status |
|---|---|
| Frozen How2Sign v2 Curify baseline (128/128) | ✅ Complete, independently re-verified |
| ALL-128 vs. MATCHED-126 metrics reconciliation | ✅ Complete |
| Apples-to-apples Curify/OpenSLT/Uni-Sign comparison | ✅ Complete |
| Deletion-dominance / short-output analysis | ✅ Complete |
| WER distribution + qualitative candidates | ✅ Complete |
| Temporal precision/recall interpretation | ✅ Complete |
| Security note on local transcript remediation | ✅ Complete |
| Higher-FPS sampling ablation | ❌ Not started — proposed as next step only |
| Any change to production code | ❌ Not applicable — none made |
| Staging / committing this report | ❌ Not done — stopped for review per instructions |

---

## Scope note

No Gemini calls were made, no `GEMINI_API_KEY` was required or inspected,
and no benchmark clips were rerun to produce this report. Nothing was
staged, committed, or pushed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01QUrty4vsXzB9EW9tjyevmz
