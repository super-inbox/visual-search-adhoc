# P0-13: representation interface

How frozen Uni-Sign features replace P0.2's landmark input, and the checks that they are aligned with
the same examples.

## 1. Where the swap happens

```
BASELINE (P0.2)   MediaPipe Holistic npy ─► ASLLandmarkDataset (normalize, AUGMENT, stride≤150) ─► [T,501]
TREATMENT         official RTMPose pkl ─► Uni-Sign (frozen) ─► cached [T,768] ─► stride≤150 ─► [T,768]
                                                                                           │
   ┌───────────────────────────────── identical from here ───────────────────────────────────┘
   ▼
ConformerEncoder.projection Linear(in→512)+LN  ◄── only shape change: in = 501 vs 768
 → stride-2 Conv1d → sinusoidal PE → 4 Conformer blocks (d 512, 4 heads, k 31)
 → modality_bridge Linear(512→512)+GELU+LN → t5-small decoder (encoder deleted) → greedy, max_length 30
```

The trainable stack is the same in both arms, freshly initialized with `set_seed(42)`. Only the input
projection's weight shape differs (501×512 vs 768×512). The Uni-Sign weights are never trained or loaded into
the trainable model; the features are precomputed.

## 2. Uni-Sign feature definition

Per clip (`scripts/extract_unisign_features.py`), using upstream code at `eed438bc` unchanged:

1. `S2T_Dataset.load_pose`: official pose pkl. If the clip is longer than 256 frames, the upstream
   `random.sample` picks 256 sorted frames. `random` is seeded per clip with
   `int(sha256(clip_id)[:8], 16)`, so it is reproducible. 542/2,751 train, 102/366 val and 52/147 frozen clips
   are subsampled.
2. `load_part_kp`: body 9, left hand 21, right hand 21, face 18 keypoints, with the official crop/scale
   normalization and confidence threshold 0.3.
3. `Uni_Sign.forward` returns `inputs_embeds = [8 prefix-token embeddings ("Translate sign language video to
   English: ") ; pose_proj(ST-GCN features)]` and the attention mask.
4. `mt5_model.encoder(inputs_embeds, attention_mask).last_hidden_state`. **Saved feature `enc` = the T
   pose-position rows** (the 8 prefix rows are dropped), so there is one 768-d vector per sampled pose frame,
   stored as float16.
5. Also saved: `pose_emb` (the pre-mT5 pose tokens, used only for diagnostics), `n_frames_raw` and `T`.

Why the mT5-encoder output rather than `pose_emb`: it is what Uni-Sign's own decoder reads, so it is "the Uni-Sign
encoder representation". `pose_emb` alone is an intermediate tensor that only makes sense through the
mT5 encoder that follows it.

Then the treatment dataset applies **the same stride rule as P0.2** (`ASLLandmarkDataset.__getitem__` step 6:
if T > 150, keep every ⌈T/150⌉-th frame, then truncate to 150).

## 3. Alignment and shape checks (`data/feature_verification.json`)

| Check | train | val | frozen |
|---|---|---|---|
| IDs in P0.2 `ids/*.txt` | 2,751 | 366 | 147 |
| Features present / bad | 2,751 / 0 | 366 / 0 | 147 / 0 |
| `enc` shape = (min(raw, 256), 768), `pose_emb` same, all finite | ✓ | ✓ | ✓ |
| Raw pose frames (min / median / max) | 2 / 130 / 2,918 | 6 / 175.5 / 1,946 | 6 / 171 / 991 |
| T fed to the Conformer after the stride rule (max) | 150 | 150 | 149 |
| Mean per-frame L2 norm | 3.23 | 3.20 | 3.12 |
| Item order = P0.2 order (dataset is built from P0.2's own `ASLLandmarkDataset.filepaths`) | ✓ | ✓ | ✓ |
| P0.2 saved predictions use the same IDs in the same order | — | ✓ | ✓ |
| Reference strings | same metadata CSVs (`subset_metadata.csv`, `frozen_benchmark_metadata.csv`) and the same lookup | | |

`compare_arms.py` also asserts that the two arms' reference strings are identical clip by clip before any
paired statistic is computed.

## 4. Faithfulness check

`scripts/validate_feature_interface.py` decodes cached frozen-set features with Uni-Sign's own decoder (beam
4, max 100 tokens). The result is close to the authors' released predictions (mean chrF 63.3 over 8
clips; `data/interface_check.json`). So the cached tensor is the real Uni-Sign encoder state, not a broken
re-implementation.

## 5. Differences between arms besides the representation (unavoidable; see `P0_13_PLAN.md`)

| | Baseline | Treatment | Why it cannot be equalized |
|---|---|---|---|
| Augmentation | flip, temporal drop/dup, hand dropout, 3D rotation/scale/shift | none | augmentations act on raw landmarks; the features are frozen and cached (online Uni-Sign at about 0.4 s/clip × 30 epochs × 2,751 would be about 9 CPU-hours) |
| Video segment | train/val: Kaggle extraction; frozen: **original** How2Sign timings, full frame | **re-aligned** timings, official signer crop (all splits) | Uni-Sign needs RTMPose keypoints; only the official archive has them for train/val. A **timing-matched secondary eval** uses Uni-Sign on our own original-timing rtmlib poses for 128/147 frozen clips (P0-12 condition `B_ours_5p39`) |
| Max frames before stride | all frames | ≤256 (upstream sampling) | part of the official Uni-Sign input contract |
| Numerics | fp32 | fp32 Uni-Sign (official uses bf16) | bf16 is 50× slower on this CPU; drift is cos 0.9994 |
