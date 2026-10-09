# P0-11: dataset splits

Built by `scripts/build_p011_splits.py` (`splits/splits_summary.json`) and checked by `scripts/check_splits.py`
(`splits/split_checks.json`). The ID lists are `splits/train_{p02_ref,p25,p50,p100}.txt`.

## 1. Sources

| Item | Value |
|---|---|
| Official How2Sign re-aligned train CSV | 31,165 clips (`how2sign_realigned_train.csv`, sha256 `67a8f4fb…`, the same file P0.2 used) |
| Landmark archive | HF `PSewmuthu/How2Sign_Holistic` → `how2sign_holistic_features/train/frontal.rar`, 21,810,397,729 B, sha256 `d5bd21a9…cbc5` (the archive P0.2's 3,117 files were extracted from). Listing: 31,047 `.npy` files |
| Reference texts | official `SENTENCE` column. The P0-11 metadata CSV is identical to P0.2's `subset_metadata.csv` on all 3,117 P0.2 clips (`build_metadata_csv.py` asserts this) |
| Val | P0.2's 366 clips (`holdout_split.json`), unchanged |
| Frozen test | P0.2's 147 clips (128 How2Sign-v2 + 19 pilot; official How2Sign **test**), unchanged, with its own metadata |

## 2. Eligible training pool

| Step | Clips |
|---|---|
| Official train clips | 31,165 |
| − no landmark file in the archive | −118 |
| − text equals a frozen-147 sentence (P0.2 denylist rule) | −2 |
| − the 366 P0.2 val clips | −366 |
| − **other clips from the 366 val videos** (keeps val video-disjoint) | −4,260 |
| − clips sharing a val `split_by_signer` group key | −0 (already covered by the video rule) |
| **Eligible pool** | **26,419** |

**Is the old "10%" label right?** P0.2's 3,117 clips (train + val) were sampled as 10% of a 31,045-clip pool. Its
2,751 training clips are **8.83 % of official How2Sign train** and **10.41 % of this P0-11 pool**. All reports
here give actual counts.

## 3. Subsets (nested; sampling seed 20261008)

Order: the 2,751 P0.2 train clips first (sorted), then the remaining 23,668 pool clips shuffled with
`random.Random(20261008)`. Each subset is a prefix of this order.

| Subset | Clips | Videos | % of pool | % of official train | sha256 of ID list |
|---|---|---|---|---|---|
| P0.2 reference | 2,751 | 1,208 | 10.41 | 8.83 | `900929628d3e…` |
| p25 | 6,605 | 1,667 | 25.00 | 21.19 | `d7566effa993…` |
| p50 | 13,210 | 1,804 | 50.00 | 42.39 | `e356f5dda92e…` |
| p100 | 26,419 | 1,826 | 100.00 | 84.77 | `7f11e938aaa7…` |

Nesting is verified: ref ⊂ p25 ⊂ p50 ⊂ p100 (`splits_summary.json → nesting`).

Video coverage saturates fast. p25 already covers 1,667 of the 1,826 pool videos, so larger subsets mostly add
**more sentences from videos already seen**, not new videos or topics. This is a property of How2Sign (about 14
sentences per video).

## 4. Integrity checks

| Check | ref | p25 | p50 | p100 |
|---|---|---|---|---|
| Unique IDs = count | ✓ | ✓ | ✓ | ✓ |
| Every ID present in archive listing | ✓ | ✓ | ✓ | ✓ |
| Empty references | 0 | 0 | 0 | 0 |
| Clip overlap with val / frozen | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Video overlap with val / frozen | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Normalized-text overlap with frozen | 0 | 0 | 0 | 0 |
| Normalized-text overlap with val clips | 6 | 22 | 48 | 90 |
| Distinct normalized texts | 2,718 | 6,462 | 12,836 | 25,513 |

- The val text overlaps are generic short sentences that recur across How2Sign videos. P0.2 already had 6 such
  clips, covering 2 distinct texts per its overlap report. They inflate val slightly and grow with subset size.
  This is one more reason the **frozen set is the primary endpoint.**
- The training script also re-checks at start: train∩val = ∅, every landmark file exists, and the val and frozen
  sizes are 366 and 147.
