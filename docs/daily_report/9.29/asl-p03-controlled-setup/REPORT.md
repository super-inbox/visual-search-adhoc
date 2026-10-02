# P0.3 Controlled training intervention: implementation and smoke tests — 2026-09-29

**Status: implemented and smoke-tested; full Arm B and Arm C runs NOT launched** (awaiting approval). Nothing committed or pushed. Smoke-test numbers are not scientific results.

## 1. Arm A: baseline definition and reuse

**Arm A = the existing run `results/p02_padfix_10pct_e30`** (`scripts/train_p02.py`, padding-fix encoder):
- 501-d input, translation loss only
- seed 42, init sha256 `e651b023…`
- batch size 8, Adafactor (T5 params at 0.1 × LR), LR 1e-4, linear warmup 10% of 30 epochs
- early stopping on val loss with patience 10
- ran all 30 epochs; best epoch 20 (val loss 3.6415); all 30 checkpoints kept

**Reuse is valid, verified empirically.** The run predates the commit that now holds the code (`7da5734`), so the code it was trained with was not recorded. `scripts/train_p03.py --arm A`, run on the current code (src unchanged vs HEAD), reproduces its first **30 optimizer steps bit-for-bit**: loss and gradient norm in 30/30 steps, max diff 0.0. The initial-weights hash, split hashes and data are identical. The only config differences are metadata fields and the omitted pre-training re-score of an unrelated old 1-epoch checkpoint, which cannot affect training. The bit-exact replay confirms this (`data/config_diff_padfix_vs_armA.json`).

Note: P0.1/P0.1b/P0.2 analysed the *pre-padding-fix* run `p02_10pct_e30`. P0.3 comparisons must use padfix Arm A, evaluated with the same harness (planned below).

## 2. Arm B: input-only ablation (162 dims)

- `ColumnSelectCollate` keeps model-input columns **33–68 (pose 11–22) + 99–161 (left hand) + 162–224 (right hand)**. The selection happens inside the collate function, *after* all dataset augmentation, normalisation and stride subsampling, which are therefore identical to Arm A. The same collate is used for training, val eval, frozen generation and the gate harness.
- The only model change is the first Linear, 501→512 becomes 162→512.
- **Init:** the seed-42 Arm A model is built, and its projection weight is sliced to the kept columns. Projection = Linear + LayerNorm, so the Linear's init scale is normalised away. Every other tensor is bit-identical to Arm A's init (verified).
- No velocity, acceleration or face.

**Proof of 162 dims and landmark groups** (unit checks, all pass):
- batch shape `[8, 136, 162]`
- selected landmarks = pose 11–22 (12 points), left hand 0–20 (21), right hand 0–20 (21), nothing else; 54 landmarks × 3 = 162
- selected values are identical to the full input's columns
- attention mask and labels are unchanged

## 3. Arm C: text-grounded auxiliary objective

| Item | Choice |
|---|---|
| Video representation | Conformer **block 4 output** (encoder output, *before* the modality bridge where P0.1 located the amplification), masked mean over valid time positions |
| Projection | `aux_head = Linear(512, 512)`, trainable (262,656 params), used only by the aux loss |
| Text representation | **Frozen pretrained t5-small encoder** (local cache, same T5 family as the decoder, nothing downloaded), mean-pooled over tokens, L2-normalised, centred by the train-bank mean, re-normalised. Precomputed once as a non-persistent buffer; the T5 encoder is discarded afterwards. This is the same text space as the P0.2 probe's `t5enc` (max diff 8e-9). |
| Similarity | cosine / temperature; **τ = 0.07, fixed** (not learned) |
| Negatives | **All 2,750 other train sentences** (a fixed bank, so negatives do not depend on batch size 8). The 51 bank rows with an identical normalised text (e.g. "okay" ×7) are masked out, not treated as negatives. |
| Loss | **L = L_translation + λ · L_aux**, where L_aux = CE(cos(v, bank)/τ, own sentence) over the 2,751-sentence train bank, video→text direction only |
| Weight | **λ = 1.0**, fixed a priori; no sweep. The initial encoder gradient-norm ratio aux/translation = 0.30 is recorded as a diagnostic only. |
| When | every training forward from **step 0**; never at eval (val loss, early stopping and checkpoint selection stay translation-only, as in Arm A) |
| Gradients | encoder (projection, downsample, blocks 1–4) + aux_head receive aux gradients. The bridge and T5 receive none from the aux path; they are still trained by the translation loss as in Arm A. The text side is frozen (a buffer, not a parameter). |
| Init | base model bit-identical to Arm A (sha `e651b023…` excluding aux_head); aux_head drawn from a separate seeded generator |

**Circularity (pre-registered, `data/PREREGISTRATION.md`):** Arm C trains against the t5enc space that the P0.2 probe uses as its primary embedding. The gate therefore requires TF-IDF (lexical, train-only vocabulary) and native decoder scoring to agree.

## 4. Trainable / frozen parameters

| | Arm A | Arm B | Arm C |
|---|---:|---:|---:|
| total = trainable | 67,176,192 | 67,002,624 | 67,438,848 |
| difference vs A | — | −173,568 (projection 501→162 inputs) | +262,656 (aux_head) |
| frozen | none (as in P0.2) | none | text bank buffer (not a parameter) |

## 5. Config diffs (programmatic, `scripts/compare_p03_configs.py`, `data/config_diff_smoke.json`)

**A vs B (16 fields):** arm label, output dir/argv, `input_dim` 501→162, the input-column spec, parameter counts, init hash (plus B's record of the A-equivalent init hash), and `git.status` (new untracked files appeared between smoke runs).

**A vs C (23 fields):** arm label, output dir/argv, the documented `arm_info.aux.*` fields, parameter counts, full init hash (the base-model hash is identical), and `git.status`.

**No training hyperparameter differs:** seed, batch size, LR, schedule, optimizer groups, epochs, patience, augmentation, generation, splits, split hashes and thread count are all identical.

## 6. Smoke tests (30 optimizer steps each, full train set, unchanged 30-epoch LR schedule; final code)

| Run | Result |
|---|---|
| Arm A replay | 30/30 steps bit-identical to padfix; val loss 8.6222 |
| Arm C, λ = 0 | Steps 1–2 bit-identical. From step 3, float-level drift (grad norm differs at 1e-7 relative, max \|Δloss\| 7e-4 by step 30). The drift is deterministic across reruns. A single-process check with the same weights, batch and dropout seed gives **identical loss and all 211 gradient tensors (max diff 0.0)**, and aux_head gradients are exactly 0. So the λ = 0 path computes the same function; the drift comes from allocation-dependent CPU BLAS rounding. |
| Arm B | finite losses (step 1 11.67, step 30 9.33); val loss 8.614; checkpoint written |
| Arm C, λ = 1 | finite: step 30 translation 9.24, aux 7.96 (≈ ln 2751 = 7.92, as expected in early warmup); val loss 8.663 (translation-only) |

**Unit checks (`scripts/smoke_p03.py`, 18/18 pass, `data/unit_checks.json`):**
- Arm B: dims = 162; correct landmark groups; values identical to the source columns; init identical to A except the sliced projection; forward, loss and backward finite; checkpoint strict save/load and generation OK.
- Arm C:
  - base init = A
  - text bank = P0.2 t5enc space
  - text side frozen, with no T5 encoder module in the model
  - targets map to the right bank rows; logits `[8, 2751]`, 2,750 negatives per query
  - duplicate-text masking (e.g. "okay": 7 rows, 51 masked rows in total)
  - total loss = translation + λ·aux, and translation part = Arm A loss under the same dropout seed
  - eval loss = translation only
  - λ = 0 step = Arm A step
- **Tiny optimisation sanity** (16 train clips, aux loss only, Adam, 60 steps; memorisation, mechanical only): aux loss 8.38 → 1.95; top-1 among 2,751 sentences 0% → 50%; mean rank 1,647 → 2.25; positive cosine −0.02 → 0.55 vs mean negative 0.00.
- **Checkpoint save/load:** strict load into the aux model; strict load into the plain `ASLTranslationModel` after dropping exactly the 2 `aux_head.*` tensors; identical eval loss both ways; generation works.

## 7. Gradient sanity (aux loss alone, one batch)

Non-zero gradients reach the encoder projection, downsample, blocks 1–4 and aux_head. **Bridge: 0 of 4 tensors have a gradient; T5: 0 of 81.** The text bank is not a parameter.

## 8. Representation-gate harness (`scripts/eval_p03_representations.py`)

For each run it evaluates checkpoints at epoch 5, best-val and final:
- pooled block 2 / block 4 / bridge GELU / T5 input for all 3,264 clips, using the arm's own input columns;
- the **unchanged P0.2 probe** with the same text embeddings and the **same saved candidate sets**, saving per-query outcomes for paired tests between arms;
- P0.2 native decoder scoring;
- P0.1b collapse metrics (inter-video cosine, clip-identity / position variance shares, bridge amplification).

- **Verified:** on the old run's epoch-18 checkpoint it reproduces P0.2 **exactly** (128 probe metrics, native scores) and P0.1b's collapse metrics (max diff 0.0).
- **Plumbing:** it runs on the Arm B (162-d) and Arm C (aux-head) smoke checkpoints (64-train-clip plumbing mode; not results).
- **Pre-registered gate:** see `data/PREREGISTRATION.md`.

## 9. Launch commands (NOT run)

```bash
cd ~/Desktop/gloss-free-asl-translation && export HF_HUB_OFFLINE=1
# Arm B
bash -c 'source results/p03_controlled/common_args.sh && .venv/bin/python scripts/train_p03.py $COMMON \
  --arm B --output-dir results/p03_controlled/armB_hands_upper162' > results/p03_controlled/armB_hands_upper162.log 2>&1
# Arm C
bash -c 'source results/p03_controlled/common_args.sh && .venv/bin/python scripts/train_p03.py $COMMON \
  --arm C --aux-weight 1.0 --aux-temperature 0.07 --output-dir results/p03_controlled/armC_textalign_w1' > results/p03_controlled/armC_textalign_w1.log 2>&1
# Representation gate (after training), incl. Arm A = padfix
for r in "results/p02_padfix_10pct_e30 armA_padfix" "results/p03_controlled/armB_hands_upper162 armB" \
         "results/p03_controlled/armC_textalign_w1 armC"; do set -- $r
  .venv/bin/python scripts/eval_p03_representations.py --run-dir $1 --name $2 --epochs 5 best final; done
```

`common_args.sh` holds the padfix run's exact data arguments plus `--epochs 30 --patience 10`. Commands must run under `bash`, because zsh does not word-split `$COMMON`.

## 10. Runtime estimate

- **Training, per arm:** padfix took **2.35 h** for 30 epochs (≈ 282 s/epoch: ~220 s train, ~41 s val generation, ~13 s frozen generation). The original P0.2 run took 4.7 h under load. The aux loss adds < 1% compute (an 8 × 2,751 × 512 matmul per step).
- **Estimate:** **~2.4 h per arm on an idle machine, up to ~4.7 h under load.** Sequential B then C: ~5–9.5 h. Early stopping may shorten a run (padfix did not stop early).
- **Gate evaluation:** ~8 min per checkpoint idle (P0.2 timing). But **37 min was measured today**: the machine is heavily loaded by other apps (Finder, file-dialog services, WindowServer and Chrome at 50–80% CPU each; 15-min load average 9.4). For 9 checkpoints: ~1.2–5.5 h.
- Recommendation: run B and C **sequentially** (each uses 6 threads) with other heavy apps closed, or overnight.

## 11. Files

Model repo `~/Desktop/gloss-free-asl-translation` (untracked, nothing committed; no existing file modified):
- `scripts/train_p03.py` (new): arms A/B/C; imports `train_p02.py` unchanged
- `scripts/smoke_p03.py` (new): unit checks
- `scripts/eval_p03_representations.py` (new): representation gate
- `scripts/compare_p03_configs.py` (new): config diffs
- `results/p03_controlled/`:
  - `PREREGISTRATION.md`, `common_args.sh`
  - `smoke/`: 8 × 30-step smoke runs with logs, `unit_checks.json`, config diffs, `eval_harness_smoke.log`
  - `representation_eval/smoke_*`: harness smokes (reproduction + plumbing)

This worktree: `docs/daily_report/9.29/asl-p03-controlled-setup/` (this report + `data/`).
