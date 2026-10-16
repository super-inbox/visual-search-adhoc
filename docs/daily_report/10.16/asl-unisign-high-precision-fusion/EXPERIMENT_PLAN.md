# P0-15: High-Precision Specialist Verification and Fusion — Experiment Plan

**Date:** 2026-10-16 · **Branch:** `baobao/visual-production-research-2026-10-05` · **Status: PLAN, frozen before any
dev fitting.** CPU only. No new Uni-Sign forward pass. Not committed.

Builds on: `../../10.15/asl-unisign-representation-probe/` (P0-14, formal verdict PARTIAL SUPPORT; its S1 sanity gate
was missed by 0.0002).

## 1. Question and scope

> Can a lightweight verifier filter the frozen mT5-encoder-state specialist probe so that it adds more correct
> concepts than wrong ones to Uni-Sign's translation, without materially lowering the translation's concept precision?

- The output is a **concept set** next to an **unchanged** Uni-Sign sentence. P0-15 measures **concept-set
  reliability** on the 24 Tier L concepts. It does **not** measure sentence translation quality. BLEU and chrF are
  not computed, and no translation-improvement claim can follow from this experiment.
- The fusion is **add-only**. It acts only on (clip, concept) cells where the translation does not already contain
  the concept, and it never removes a concept the translation produced.
- Decoding confidence and sequence scores are **out of scope**. They would require a new decode pass and a new
  reproducibility gate.
- A positive result answers the *necessary* fusion-readiness question. Whether verified concepts can improve the
  *sentence* (n-best re-ranking, constrained decoding) is a later P0, and it needs a fresh held-out set because this
  experiment uses up the final split (§10).

## 2. Data (all frozen P0-14 artifacts; nothing re-extracted, re-decoded or re-trained)

| Input | Source | Use |
|---|---|---|
| 2,209 `test_clean` clips, their `video_id`, `signer_proxy` and labels for the 24 Tier L concepts | P0-14 `splits/manifest.csv` (sha in `SPLITS.sha256`) | cells, labels, split units |
| Concept vocabulary and matcher | P0-14 `concepts/concept_list_v1.csv`, `scripts/build_concepts.py` (top half, run as-is) | translation concept presence. **Vocabulary unchanged** |
| Uni-Sign beam-4 translations | P0-14 `full_run/vm_decode/predictions.jsonl` (sha `0116a41a…`) | `D` (translation contains concept), `n_tokens`, `T`, `n_frames_raw` |
| mT5 probe test logits and predictions | `p014-work/results/lr/mt5_ms_{p100_d0, p10_d0..d4, p25_d0..d4, p50_d0..d2}.json` (14 files) | specialist signal and agreement |
| Fsign and raw-pose probe test logits | `p014-work/results/lr/{fsign,raw}_ms_p100_d0.json` | supporting evidence (verifier D only) |
| Train concept prevalence | manifest, `probe_train` rows only | concept prior |

Every probe file is checked against P0-14 `LR_FULL_OUTPUTS.sha256` before use.

**Excluded:** all `testcv_*` outputs. Those probes were trained on test_clean clips, so they would leak across the
dev/final split. The loader refuses any file whose name contains `testcv`.

**Per-concept probe thresholds θ.** P0-14 did not save its OOF-F1 thresholds; it saved `test_pred = (score ≥ θ)`.
θ is recovered **without labels** as the smallest score with `test_pred = 1` (or max score + 1e-3 if the probe never
fires). The builder asserts that `(score ≥ θ) == test_pred` for every cell of every probe file used.

## 3. Cells and the candidate set

- One cell = (clip i, Tier L concept k): 2,209 × 24 = 53,016 cells.
- `Y[i,k]`: the frozen reference label. `D[i,k]`: the frozen matcher applied to Uni-Sign's translation.
- **Candidate cells:** `D = 0`. Only these can be added. Builder check (label-free): Σ D = 888, as implied by P0-14's
  534 hits + 354 false mentions.
- Fused prediction: `F = D ∨ A`, where `A ⊆ candidates` is the set of additions.

## 4. Arms

| Arm | Additions A | Fitted on dev |
|---|---|---|
| **A** | none (Uni-Sign translation baseline) | nothing |
| **B** | candidates where the mT5 p100 probe fires at P0-14's frozen threshold (naive union) | nothing |
| **C** | candidates with `mt5_margin ≥ τ_C` | one scalar τ_C (§6) |
| **D** | candidates with verifier logit `≥ τ_D` | L2 strength, 12 weights (11 features + intercept), τ_D (§5–6) |

`mt5_margin = s_mt5,p100 − θ_mt5,p100,k`. It is concept-specific through θ_k, which P0-14 derived on probe_train,
so C has per-concept calibration without fitting any per-concept parameter on dev.

## 5. Verifier D (frozen feature list; no feature may be added after the final split is opened)

Fit on dev candidate cells only:

| # | Feature | Definition |
|---|---|---|
| f1 | `mt5_logit` | mT5 p100_d0 test logit for (i, k) |
| f2 | `mt5_margin` | f1 − θ (mT5 p100_d0, k) |
| f3 | `mt5_agree` | mean of `test_pred` over the 14 mT5 probes (p10 d0–4, p25 d0–4, p50 d0–2, p100 d0) |
| f4 | `mt5_margin_sd` | SD (ddof 0) over the same 14 probes of (logit − θ for that probe and concept) |
| f5 | `fsign_margin` | Fsign p100_d0 logit − its θ_k |
| f6 | `raw_margin` | raw-pose p100_d0 logit − its θ_k |
| f7 | `log_frames` | log(`n_frames_raw`) |
| f8 | `n_tokens` | translation token count from `predictions.jsonl` |
| f9 | `log_tok_per_frame` | log((`n_tokens` + 1) / `n_frames_raw`) |
| f10 | `log_prior` | log of concept k's prevalence among the 31,086 probe_train clips |
| f11 | `n_other_trans` | number of the other 23 Tier L concepts present in the translation |

- Model: logistic regression. Objective = mean log-loss + (λ/2)‖w‖², intercept unpenalized, no class weights.
  Features are z-scored with the fitting rows' mean and SD. Solver: Newton/IRLS, tolerance 1e-10, at most 100
  iterations, deterministic.
- λ ∈ {1e-4, 1e-3, 1e-2, 1e-1}, chosen by grouped CV over dev units, maximizing pooled out-of-fold average
  precision (AP) on candidate cells. Ties go to the larger λ.
- There are no per-concept models, no per-concept intercepts and no interactions. Dev has only about 2–28
  translation-missed positives per concept.

## 6. Operating-point rule (same rule for C, D and the controls)

Given scores on a set of candidate cells with labels:
- **τ\*** is the **smallest** score value τ among those cells such that the additions `{score ≥ τ}` number **≥ 10**
  and their precision has a **Wilson 90 % lower bound ≥ 0.50** (z = 1.6449).
- If no τ qualifies, the arm **abstains**: it adds nothing, and τ = +∞.
- Rationale: net correct additions > 0 is the same as add-precision > 0.5. The Wilson bound guards against picking a
  lucky threshold on few cells.

**τ_C:** the rule applied to `mt5_margin` on all dev candidates.

**D frozen model:**
1. λ by 5-fold grouped CV on dev (the dev folds of §7).
2. τ_D by the rule applied to the 5-fold OOF verifier logits at that λ.
3. Refit at that λ on all dev candidates. These weights and τ_D are frozen.

## 7. Source-video-level dev/final split (`scripts/build_split.py`)

1. **Units:** the 149 test_clean videos. The two videos that share an identical normalized reference sentence
   (`f_zna_wG3zo`, `G3di9jJTqDs`) are merged into one unit, giving **148 units**.
2. **Stratum of a unit:** its majority `signer_proxy` over its clips. Ties go to the lower id. Signer proxy varies
   within 31 videos, so this is per unit.
3. **Unit weight:** its number of Tier L reference positives.
4. **Assignment for seed s:**
   - `rng = numpy.random.default_rng(s)`.
   - Strata are processed in ascending id. Within each stratum: random permutation by `rng`, then a stable sort by
     unit weight descending.
   - Units are then assigned serpentine. Even-index strata use the pattern dev, final, final, dev, repeating; odd-index
     strata use final, dev, dev, final.
5. **Balance check (pre-registered):**
   - dev share of clips ∈ [0.45, 0.55];
   - for each of the 24 Tier L concepts, dev share of reference positives ∈ [0.25, 0.75].
6. **Seed procedure:** try s = 15, 16, …, 114 in order and accept the **first** seed that passes. Every seed tried is
   logged with its check values in `split/SPLIT_LOG.json`. The balance check uses **only reference labels and clip
   counts**. Translation output and probe scores are never used to build or select the split.
7. **Outputs:** `split/dev_units.txt`, `split/final_units.txt`, `split/dev_clips.txt`, `split/final_clips.txt`, and
   their sha256 in `split/SPLIT.sha256`.
8. **Dev folds** (for C/D CV): the dev units sorted by clip count descending (ties by id), each assigned in turn to
   the fold with the fewest clips so far (ties to the lowest fold index). 5 folds, label-free.

**Keeping the final split hidden:**
- `build_cells.py` writes `cells_dev.csv.gz` (features, D and Y) and `cells_final_nolabel.csv.gz` (features and D,
  **no Y**).
- All dev scripts read only `cells_dev.csv.gz`.
- Final labels are joined only inside `evaluate_final.py --target final`.

## 8. Dev-only decision: is a simple threshold enough? (D-vs-C primary-arm rule)

Nested out-of-fold estimates on dev:
- **C:** for each dev fold f, τ is chosen by the §6 rule on the other 4 folds and applied to fold f.
- **D:** for each fold f, on the other 4 folds:
  - λ is chosen by 4-fold grouped CV AP;
  - τ by the §6 rule on those 4-fold OOF logits;
  - the model is refit on the 4 folds and applied to fold f.
- `net_X` = Σ over folds of (correct additions − incorrect additions) for arm X. `Δ = net_D − net_C`.
- **Bootstrap:** resample dev units with replacement, B = 2,000, seed 20261016, with the OOF predictions held fixed.
- **D is the primary arm iff Δ ≥ 0.25 · max(net_C, 0) and the 95 % percentile-CI lower bound of Δ > 0.**
  Otherwise **C is primary** and D is reported as secondary. If C abstains and D does not satisfy the rule, the
  primary arm is C, which abstains.

## 9. Final evaluation (one shot, after `FREEZE.json`)

### 9.1 One-shot rule
- `FREEZE.json` records:
  - τ_C;
  - D's λ, weights, scaler and τ_D;
  - the primary arm;
  - the N1 and N2 configurations;
  - the split hashes;
  - the sha256 of every input file and of every script, including `evaluate_final.py`.
- `evaluate_final.py --target final` refuses to run if any hash differs or if `final/RUN_LOCK` exists. It writes
  `RUN_LOCK` (timestamp and FREEZE sha) **before** loading final labels, then runs once.
- If the run crashes before writing any metric, the crash and the fix are documented and the run is repeated. Once
  any final number exists, no code, threshold, feature or criterion may change.
- `--target dev` is a dry run of the same code on dev (output under `dev/dryrun/`). It is used to test the code path
  before the freeze.
- No final metric, curve or per-concept count is looked at before `FREEZE.json` is written. The intent is to commit
  `FREEZE.json` before the final run, so the git history shows the order.

### 9.2 Metrics (final split; cells pooled = micro, unless marked macro)
- additions n_add; correct TP_add; incorrect FP_add;
- **add precision** = TP_add / n_add;
- **missed recall** = TP_add / (positives among candidates);
- **add F1**;
- **net correct additions** = TP_add − FP_add, also per 100 clips;
- false additions per clip;
- fused micro P/R/F1 and Δ vs A;
- macro P/R/F1 over the 24 concepts (P0-14 convention: P = 0 when a concept has no predictions) and Δ vs A.

### 9.3 Bootstrap
Paired video-cluster bootstrap over **final units**, B = 2,000, seed 20261017. All arms share the same resamples.
Percentile 95 % CIs.

### 9.4 Success criteria (primary arm only)

| # | Criterion | Rule |
|---|---|---|
| **P1** | More right additions than wrong | net correct additions CI lower bound > 0 |
| **P2** | **Do no harm** | Δ fused micro-precision vs A: CI lower bound ≥ −0.020; **and** Δ macro-precision point estimate ≥ −0.020 |
| **P3** | Large enough to matter | TP_add ≥ 5 % of the final split's translation-missed positives (point estimate) **and** Δ fused micro-F1 vs A CI lower bound > 0 |
| **N1** | Permutation control | 20 dev label permutations (each concept's Y permuted across dev clips, seeds 1–20). The primary arm's full fitting procedure (§6, and §5 if D) is re-run on each and frozen. Applied to final with true labels, the **median net correct additions must be ≤ 0** |
| **N2** | Length-only control | the D procedure with features {log `n_frames_raw`, log `T`} only, frozen. It must **not** pass P1 on final |

**Verdict:**
- **SUPPORTED:** P1, P2 and P3 pass.
- **PARTIAL:** P1 and P2 pass, P3 fails ("safe but too small to matter").
- **NOT SUPPORTED:** P1 or P2 fails, including when the primary arm abstains.
- **VOID:** N1 or N2 fails (the pipeline is not trusted). Nothing is interpreted beyond the descriptive tables.

### 9.5 Descriptive only (not part of the verdict)
- arm B on the final split;
- the secondary arm;
- per-concept adds and TP;
- AUROC and AUPRC among final candidate cells for the mT5 margin and the D logit;
- risk–coverage and precision–recall curves over τ on final (computed **after** the primary metrics are written);
- results by signer proxy;
- dev-OOF vs final gap;
- a D ablation without f5/f6 (fitted on dev and frozen in FREEZE.json, like every other arm).

## 10. Leakage and contamination disclosures

1. **P0-14 aggregates already influenced the design.** P0-14 reported results on all 2,209 test_clean clips,
   including every future final clip:
   - AUROC 0.78 on translation misses;
   - OR-fusion −6.2 F1;
   - add-precision 13 %;
   - per-concept tables.

   These shaped the high-level design: mT5 as the specialist, add-only, high precision, a verifier. No threshold,
   weight or feature value has been fit on final clips, but the final split is not "never seen" at the design level.
2. **Balance check reads final labels as counts.** The split balance check uses per-concept reference-positive
   counts on both sides. It never uses translation output or probe scores.
3. **θ comes from unlabeled final scores.** θ is reconstructed from the unlabeled probe scores and predictions of all
   test clips. It recovers a value that P0-14 already fixed on probe_train; no labels are involved.
4. **Matcher integrity check reads all reference labels.** The check (frozen matcher on references = manifest labels)
   runs over all test clips. It is an assertion only; no metric is computed.
5. **Same signers on both sides.** All signer proxies appear on both sides, so the experiment does not test
   unseen-signer generalization.
6. **Proxy labels.** The labels are proxies from English references (the frozen P0-14 matcher), not ASL manual
   annotations.
7. **Training data and checkpoint.** The probes were trained on How2Sign train (probe_train) only. The Uni-Sign
   checkpoint was fine-tuned on How2Sign train. How2Sign val has no official poses, so test_clean is the only
   in-distribution set where both translations and labels exist. That is why calibration must happen on a test
   subset.
8. **testcv excluded.** The `testcv_*` probe outputs are excluded (§2).
9. **P0-14's S1 caveat carries over.** The same mT5 probes are used, and P0-14's sanity gate S1 was missed by 0.0002.

## 11. Compute

Mac CPU only:
- cell building: seconds;
- dev fitting with nested CV, the decision bootstrap, N1 and N2: minutes;
- final run: minutes.

Bulk files live in `~/Desktop/curify/p015-work/` (≈ 15 MB). The repo gets the scripts, the split lists and hashes,
the dev results and `FREEZE.json` (< 2 MB).

## 12. Layout

```
docs/daily_report/10.16/asl-unisign-high-precision-fusion/
├── EXPERIMENT_PLAN.md
├── scripts/  common.py  build_split.py  build_cells.py  fit_dev.py  evaluate_final.py
├── split/    SPLIT_LOG.json  {dev,final}_{units,clips}.txt  dev_folds.json  SPLIT.sha256
├── dev/      DEV_RESULTS.json  dryrun/
├── FREEZE.json
└── final/    (empty until the one-shot run)
```
