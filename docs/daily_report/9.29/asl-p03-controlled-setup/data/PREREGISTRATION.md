# P0.3 pre-registration (written 2026-09-29, before any full Arm B / Arm C run)

## Arms
- **A (baseline)**: reused run `results/p02_padfix_10pct_e30` (train_p02.py, current code; 30 epochs, best epoch 20).
  Validity: `train_p03.py --arm A` reproduces its first 30 optimizer steps bit-for-bit (loss and grad norm).
- **B (input ablation)**: `train_p03.py --arm B`: model-input columns 33–68 (pose 11–22) + 99–224 (both hands) = 162 dims;
  everything else identical to A (init: A's seed-42 weights, projection sliced to the kept columns).
- **C (text-grounded auxiliary loss)**: `train_p03.py --arm C --aux-weight 1.0 --aux-temperature 0.07`: 501-d input;
  L = L_translation + 1.0 · CE over all 2,751 train sentences (frozen pretrained t5-small encoder, mean-pooled,
  centred), video side = masked-mean block-4 output → Linear(512,512) head; active from step 0; eval loss translation-only.

No hyperparameter sweep. aux_weight = 1.0 and temperature = 0.07 were fixed a priori (the initial encoder gradient-norm
ratio aux/translation = 0.30 is recorded as a diagnostic, not used for tuning). The frozen test set is never used for
selection. Early stopping and checkpoint selection use val translation loss only (identical rule in every arm).

## Checkpoints evaluated (per arm)
epoch 5 (early; P0.1b collapse trough), best-val-loss checkpoint, final checkpoint.

## Representation gate (primary)
Harness: `scripts/eval_p03_representations.py` = the unchanged P0.2 probe (verified to reproduce P0.2's ep18 numbers
exactly), same text embeddings, same saved 4-way candidate sets. Stages: block 2, block 4, bridge GELU, T5 input.

Primary metric: **length-matched 4-way accuracy on val (n = 366)**, confirmed in direction on frozen (n = 147).
Secondary: R@10, random-negative 4-way, native decoder scoring (text prior removed), P0.1b collapse metrics.

An arm "creates MORE text-relevant representation" only if, at its best-val checkpoint, at least one of
{block 4, T5 input}:
1. beats **Arm A's same stage at its best-val checkpoint** (paired bootstrap on the same queries, 95% CI > 0) on val, and
2. beats the **raw landmark baseline for that arm's input** (A/C: all-landmark mean+std 42.9% val; B: hands+upper
   position 42.1% val; P0.2/P0.2b probes, paired bootstrap, 95% CI > 0) on val,
3. with the same sign on frozen, and
4. for **both** text embeddings (t5enc AND TF-IDF).

Circularity note (fixed now): Arm C's auxiliary loss is trained against the t5enc text space that the P0.2 probe also
uses as its primary embedding. TF-IDF (lexical, vocabulary from train only) is therefore the non-circular check for Arm C;
condition 4 makes it mandatory. Native decoder scoring (no probe) is the check that the decoder actually uses the signal.

Collapse metrics are reported separately. More variance (lower cosine, higher clip-identity share) without a gate pass
is reported as "more variance, not more text-relevant variance".

Translation metrics (val loss, BLEU, chrF, WER, unique predictions / top-1 fraction) are reported for every arm but are
not the primary gate.
