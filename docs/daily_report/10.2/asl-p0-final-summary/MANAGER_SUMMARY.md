# ASL landmark → T5 translation: P0.1 → P0.3 investigation, final summary — 2026-10-02

**Scope:** one landmark-based model (MediaPipe landmarks → Conformer encoder → bridge → T5-small decoder) trained on a 10% How2Sign subset: 2,751 train / 366 val / 147 frozen-test clips.

The text-relevance evidence comes from **linear probes** on time-averaged clip vectors. They measure whether a representation can linearly pick a clip's English sentence out of 4 candidates (chance 25%). They do not measure linguistic understanding, and a null probe result does not rule out information a stronger probe could find.

## 1. Original problem
At the input to the T5 decoder, ~99.9% of the video representation is effectively identical across different videos (mean inter-video cosine 0.999). Translation output is accordingly weak and generic: val BLEU ≈ 1, with many repeated predictions.

## 2. Where the collapse happens (P0.1)
- The landmark input is **not** collapsed, and Conformer blocks 1–2 are the most video-specific stages in the model.
- The collapse appears in **Conformer block 4** (inter-video cosine 0.98) and is **amplified by the bridge** (Linear + GELU) to 0.999 at the T5 input.
- There, clip identity explains ~2% of token variance and the time position ~69%. The decoder sees mostly a constant vector plus a time template shared by all videos.

## 3. When it happens (P0.1b)
- **Abruptly and early**, not gradually. 74% of block 4's loss of clip identity has occurred by the end of epoch 1 (still in LR warm-up), with the minimum at **epoch 5**.
- Afterwards the Conformer blocks slowly regain some clip identity. The bridge compresses more and more over the same period, so the T5 input stays ≥ 99.6% cosine-similar at every trained checkpoint.

## 4. Is the recovered variance text-relevant? (P0.2)
No evidence that it is.
- Every learned stage is weakly above chance at matching clips to sentences, at about 33–38% 4-way.
- The **untrained network does just as well**.
- The **plain landmark input summary does at least as well as every learned stage**: 42.9% on val and frozen.
- The variance that returns after epoch 5 does not carry more linearly decodable text information.

## 5. Where the measurable raw-landmark signal sits (P0.2b)
- In **hand shape + upper-body (arm/hand location) position**. These 162 of the 501 input dimensions match the all-landmark probe: 42.1% vs 42.9% val, 46.3% vs 42.9% frozen.
- Face adds no consistent increment, and the lower body adds nothing.
- Explicit velocity/acceleration summaries did not help consistently in the probe.

## 6. Interventions tested (P0.3, preregistered, controlled against baseline Arm A)
- **Arm B:** model input restricted to hands + upper body (501 → 162 dims). Everything else identical to A, including seed, initial weights, data and schedule.
- **Arm C:** full input plus a **text-grounded auxiliary loss**. It pulls each clip's pooled encoder output toward its own sentence's frozen T5 text embedding, against all other training sentences (weight 1.0, temperature 0.07, fixed in advance).
- **Gate (fixed before training):** at the best-validation checkpoint, encoder block 4 or the T5 input must significantly beat Arm A **and** the raw-landmark baseline on val, with the same sign on frozen, under **both** text embeddings (T5 and TF-IDF).

## 7. What happened
- **Neither arm passed the gate.**
- **Arm B:** small, non-significant probe differences vs A (+1 to +5 points on val, with the sign reversing on frozen). Translation was essentially unchanged: val chrF +0.6 (significant on val, not confirmed on frozen); BLEU and WER not significant.
- **Arm C substantially reduced collapse:**
  - T5-input inter-video cosine 0.998 → 0.940
  - clip-identity share 3% → 21%
  - bridge amplification 22× → 8×
- **But Arm C did not improve semantic retrieval** (probe within ±1.5 points of A, not significant) **or translation** (no significant BLEU/chrF/WER difference at the best checkpoint).
- Its auxiliary loss fell mostly through memorising training sentences. Alignment on unseen val sentences stopped improving early.
- **More representation variance is not the same as more text-relevant information.** Arm C produced the first but not the second.
- No arm, layer or checkpoint exceeded the raw-landmark probe baseline or its own untrained starting point.

### Key results (best-validation checkpoint)

| | Arm A (baseline) | Arm B (162-d input) | Arm C (text-aux) | Raw landmarks |
|---|---:|---:|---:|---:|
| T5-input inter-video cosine | 0.998 | 0.999 | **0.940** | — |
| Probe, block 4, 4-way val % (T5 text emb / TF-IDF) | 34.4 / 28.7 | 38.3 / 31.4 | 34.7 / 30.1 | 42.9 / 43.2 |
| Val BLEU / chrF | 0.99 / 11.9 | 1.08 / 12.6 | 0.77 / 11.7 | — |
| Preregistered gate | — | not passed | not passed | — |

The raw-landmark row is the all-landmark baseline used for A and C; B's own baseline (hands + upper body) is 42.1 / 43.7. Chance is 25% for the 4-way probe.

## 8. Hypotheses not supported by this evidence
These are *not supported* in this setup (this model, data scale and these specific interventions). That is not the same as disproven in general.
- **"Removing nuisance landmark dimensions is sufficient."** Arm B did not change representation quality or translation meaningfully.
- **"Explicit velocity/acceleration features are necessary."** They added no consistent signal in the P0.2b probe. They were not tested as a training intervention.
- **"Variance collapse alone explains the translation failure."** Arm C reduced collapse substantially without improving retrieval or translation.
- **"Adding this text-alignment auxiliary objective solves the problem."** It changed encoder geometry but did not pass the gate. Only one weight and temperature were tested, by design.

## 9. Unresolved
The raw landmarks contain a measurable, linearly recoverable text-relevant signal. **Why does the trained model not turn it into generalisable text-relevant representations?** Neither cleaner input nor a direct text signal did. The trained encoders end no better than their random initialisation on this probe. P0.1–P0.3 do not distinguish between too little training data and a model or architecture limitation, such as the bridge, pooling or objective.

## 10. Recommended next experiment (NOT run)
A **no-training data-scaling probe**. Fit the same frozen P0.2 probe on raw landmarks and on Arm A features using nested subsets of the training clips (e.g. 25 / 50 / 100%), and compare the val learning curves.

The decision it informs:
- **Still rising steeply at 100%:** the next investment should be **more training data**, i.e. Arm A at a larger How2Sign fraction, before more objective or input changes.
- **Flat:** data volume at this scale is not the main constraint, and effort should go to the **encoder/bridge design** (the bridge still amplifies collapse 17–25× in A and B).

It needs no model training and reuses the frozen harness.

---
Detailed reports (this repo): `docs/daily_report/9.29/asl-p01-encoder-collapse/`, `asl-p01b-collapse-trajectory/`, `asl-p02-semantic-probe/`, `asl-p02b-landmark-localization/`, `asl-p03-controlled-setup/` and `docs/daily_report/10.2/asl-p03-controlled-results/`. Code: `gloss-free-asl-translation/scripts/`.
