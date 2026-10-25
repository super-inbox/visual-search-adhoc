# P0-14 Data Audit: How2Sign, Uni-Sign checkpoint, poses and features

**Date:** 2026-10-15 · **Status:** audit complete; no GPU work run, no Uni-Sign forward pass run.
Every number below was produced by `scripts/build_concepts.py`, `scripts/list_pose_archive.py` and
`scripts/build_splits.py`. They read only metadata CSVs and the zip central directory, never a model.
Machine-readable copies: `audit/data_audit.json`, `audit/official_pose_archive_index.csv`, `splits/manifest.csv`.

## 1. Summary

| Question | Answer |
|---|---|
| Labeled clips available | **33,435 clips with both an English reference and official Uni-Sign RTMPose poses**: 31,086 How2Sign train and 2,349 How2Sign test. The How2Sign val split (1,741) has references but **no official poses**. |
| Full How2Sign train split or a subset? | **Effectively the full split.** The re-aligned train CSV has 31,165 rows. The official pose archive covers 31,086 of them, which equals the size of Uni-Sign's own `labels.train` (31,086, P0-13 audit). The ID-level match was not re-checked, because the labels file was in the purged clone. Earlier experiments (P0.2, P0-13) used a 2,751-clip subset, but P0-14 does not need to. |
| Where raw RTMPose features are | **Not on disk yet, except 128 test clips.** Source: HF `ZechengLi19/Uni-Sign`, `how2sign_pose_format.zip.00–.03` (8.46 GB compressed, 15.93 GB of PKLs). Locally, only the 128 P0-12 `A_official` test PKLs survive in the repo (`10.06/.../prepared_inputs/A_official/`). The 3,264 PKLs that P0-13 range-fetched were in a temporary session scratchpad and **have been purged**. |
| Where Fsign can be extracted | Inside the frozen Uni-Sign forward pass. It is the **input to `pose_proj`** (`models.py`, upstream `eed438bc`): the 4 body-part streams after spatial GCN → temporal GCN → mean over keypoints, concatenated, + `part_para`, giving `[T, 1024]`. There is no upstream API for it. A forward pre-hook captures it (`scripts/extract_representations.py`). |
| Where mT5 encoder states can be extracted | Same forward pass: `mt5_model.encoder(inputs_embeds, attention_mask).last_hidden_state`, keeping the T pose rows and dropping the 8 prefix rows, giving `[T, 768]`. This is exactly P0-13's validated `enc` feature. |
| Cached features from earlier work | **None usable.** P0-13's cached `enc` features (3,264 clips) were in a temporary scratchpad and are **gone**; only their `_extract_log.jsonl` files remain. P0-13 never saved Fsign anyway. |
| Is the existing checkpoint sufficient? | **Yes, for this probe.** `how2sign_pose_only_slt.pth` (sha256 `1bfd5f33…683fb00d`) is present at `~/.cache/uni_sign_checkpoints/` and `curify-studio/uni_sign_server/checkpoints/`. It is the full model (pose branch + mT5-Base encoder + decoder) and loads strictly with 0 missing / 0 unexpected keys (P0-13 audit). mT5-Base tokenizer/config snapshot `2eb15465…` is in the HF cache. **Limitation:** it is the only Uni-Sign checkpoint we have, and it was fine-tuned on How2Sign train (see §4). |
| Environment | conda `unisign-cpu-arm64` exists (Python 3.10, torch 2.1.1, transformers 4.40). It has no scikit-learn, so the probe code uses only torch + numpy. The **Uni-Sign source clone is gone** (purged scratchpad) and must be re-cloned at `eed438bc`. |

## 2. How2Sign splits (re-aligned CSVs)

Source: `~/Desktop/curify/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/landmark_t5_1pct/local_run_10pct/raw_download/how2sign_realigned_{train,val,test}.csv`
(sha256 recorded in `audit/data_audit.json`).

| Split | Rows (clips) | Source videos (`VIDEO_ID`) | `VIDEO_NAME`s | With official poses | Median words | Median duration |
|---|---|---|---|---|---|---|
| train | 31,165 | 2,192 | 2,212 | **31,086** | 14 | 5.3 s |
| val | 1,741 | 115 | 132 | **0** | 14 | 5.7 s |
| test | 2,357 | 149 | 184 | **2,349** | 14 | 5.2 s |

The official archive (`audit/official_pose_archive_index.csv`, read from the zip central directory without
downloading) has exactly **31,086 `train-pose-rtmpose-192/` + 2,349 `test-pose-rtmpose-192/`** PKLs. Those counts
match Uni-Sign's own `labels.train` / `labels.test` counts from the P0-13 audit.

## 3. Cross-split leakage checks

| Check | train–val | train–test | val–test |
|---|---|---|---|
| Shared `VIDEO_ID` | **0** | **0** | **0** |
| Shared `SENTENCE_NAME` | 0 | 0 | 0 |
| Shared signer-proxy values (see below) | 1,2,3,5,8 | 1,2,3,5,8 | 1,2,3,5,8 |

**The official splits are video-disjoint but not signer-disjoint.** How2Sign's public CSVs have no signer column.
The number in `VIDEO_NAME` (`<ytid>-<k>-rgb_front`) takes 1–11 distinct values, consistent with How2Sign's 11
signers, so we record it as `signer_proxy`. **This mapping is unverified.** Under that proxy:
- the two most frequent signers account for 86 % of train;
- train and test share 5 signers;
- proxy value **10 occurs only in test** (257 clean test clips). That subset is a candidate *unseen-signer* check,
  reported as secondary and conditional on the proxy being right.

**Duplicate references across splits** (`audit/near_duplicates_test.csv`):

| | test vs train | val vs train |
|---|---|---|
| Exact duplicate (normalised text) | 78 | 53 |
| Near duplicate (≥ 50 % of the sentence's word 4-grams in a single train sentence, ≥ 6 words) | 62 | 39 |

- **Exact duplicates** are almost all generic short lines: "hi!" (8), "cheers!" (6), "okay?", "right.", "one, two,
  three.".
- **Near duplicates** include presenter intros and outros. The same presenter's multi-part series appears in both
  train and test under different `VIDEO_ID`s, e.g. "Hi, I'm Johanna Krynytzky with Hip Expressions…", "My name is
  Robert Segundo…", "We're going to do two ounces of gin."
- **Decision:** all **140** are excluded from evaluation (`role = test_dup_excluded`). That leaves
  **test_clean = 2,209 clips from 149 videos**.
- Within train there are 1,122 exact-duplicate rows (generic lines). They stay in, because they cannot leak into
  evaluation.

## 4. The leakage that matters most: Uni-Sign has already seen every train clip

Carried over from the P0-13 audit and confirmed by the counts above:

- Uni-Sign's How2Sign checkpoint was **fine-tuned end-to-end on all 31,086 train clips with their English
  sentences**. It also had about 984 h of YouTube-ASL pretraining.
- Uni-Sign's How2Sign dev label path is empty upstream (`config.py`: `"How2Sign": ""`), so **How2Sign val was never
  used**. But val has no official poses.
- **How2Sign test (2,349) was never trained on. It is the only clean evaluation pool that has official poses.**

Consequences for the design (`EXPERIMENT_PLAN.md` §4):
1. Probe *evaluation* must be on test only.
2. Fsign and mT5 features of train clips come from a network that was trained to emit those clips' sentences.
   Probe-train features are therefore "memorized" for the Uni-Sign arms but not for raw pose. This makes the
   train-to-test shift larger for the Uni-Sign arms. It tends to *hurt* them, so it is conservative, but it can
   distort threshold choice. Hence:
   - AUROC (threshold-free) is a required co-criterion;
   - **Design B** (probe trained *and* tested inside test_clean) is a required leakage control.
3. No earlier Uni-Sign checkpoint exists (pretrain-only or random-init), so P0-14 **cannot separate "broad
   pretraining" from "How2Sign fine-tuning"**. This limitation is the same as in P0-13.

## 5. Concept labels: availability and balance

Selection uses train references only (`concepts/concept_rules_v1.json`). Full table:
`concepts/concept_list_v1.csv`; per-role counts: `splits/concept_counts_by_role.csv`.

| | Tier L (24 lexical concepts) | Tier S (6 semantic groups) |
|---|---|---|
| Train positives per concept | 404 – 847 (prevalence 1.3 – 2.7 %) | 418 – 3,140 (1.3 – 10.1 %) |
| Smallest low-data draw (p10, ~3.1k clips) | 27 – 91 positives | 35 – 333 |
| test_clean positives | **22 – 105** | 32 – 280 |
| test_clean videos containing a positive | **11 – 37** | 10 – 62 |

Two properties of the labels that shape the analysis:
- **Length confound.** Sentences that contain a concept are 1.1–1.6× longer than those that do not, for every
  concept (`train_len_ratio_pos_neg`). A probe could score above chance just by reading clip length. A
  `length`-only baseline (log T, log frames) goes through the identical probe, and a representation must beat it
  by a fixed margin (plan §9, C5).
- **Small, clustered test positives.** Per-concept test estimates rest on 22–105 positives from 11–37 videos.
  Per-concept CIs will be wide. The decision therefore uses macro averages with a **video-cluster bootstrap**,
  plus a sign count across concepts, not single-concept significance.

## 6. What exists locally vs what must be produced

| Item | Status | Location / action |
|---|---|---|
| How2Sign re-aligned CSVs (train/val/test) | ✅ present | `visual-search-adhoc-asl-task-c/.../raw_download/` |
| Uni-Sign checkpoint | ✅ present | `~/.cache/uni_sign_checkpoints/how2sign_pose_only_slt.pth` |
| mT5-Base tokenizer/config | ✅ present | `~/.cache/huggingface/hub/models--google--mt5-base` |
| Uni-Sign env (CPU) | ✅ present | conda `unisign-cpu-arm64` |
| Uni-Sign source at `eed438bc` | ❌ purged | re-clone (≈ 1 min) |
| Official poses, 128 test clips | ✅ present | `10.06/.../prepared_inputs/A_official/` (smoke test) |
| Official poses, all 33,435 clips | ❌ not downloaded | 8.46 GB from HF (`run_p014.sh` stage 1) |
| Raw / Fsign / mT5 features | ❌ none | one frozen forward pass (`run_p014.sh` stage 2) |
| Concept list, split manifest, low-data draws | ✅ **built and frozen** | `concepts/`, `splits/` (+ `SPLITS.sha256`) |
| Probe + analysis code | ✅ written, **self-tested on synthetic data only** | `scripts/run_probe.py`, `scripts/analyze_probe.py` |
| Free disk (Mac) | ✅ 431 GB free | needs ≈ 13 GB peak |

## 7. Caveats on this audit

- The signer proxy is inferred from file names, not documented by How2Sign.
- The near-duplicate rule (4-gram overlap ≥ 50 %) is a heuristic. A stricter rule would remove more presenter
  boilerplate. The excluded list is saved, so the choice can be revisited.
- Archive counts come from the zip central directory. Per-entry CRCs will be verified when the archive is
  downloaded.
- English-reference concepts are a **weak proxy** for what was signed. "time" in "at the same time" may not be
  signed as TIME. The noise affects all three representations equally, but it caps absolute scores.
