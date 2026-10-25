# P0-13: Uni-Sign encoder availability audit

**Verdict: AVAILABLE.** The weights, code, environment and input poses needed to extract frozen Uni-Sign
encoder features are all present or fetchable for all 3,264 P0.2 clips. Nothing had to be substituted.
One finding changes how the results must be read: **leakage on val** (§4).

## 1. Weights

| Item | Status | Evidence |
|---|---|---|
| Checkpoint `how2sign_pose_only_slt.pth` | **present** (two identical copies) | `~/.cache/uni_sign_checkpoints/` and `curify-studio/uni_sign_server/checkpoints/`; sha256 `1bfd5f33…683fb00d` for both, equal to the HF LFS oid (P0-12) |
| Content | **full model: pose encoder + mT5-Base encoder + decoder** | 627 tensors, stored bf16. Pose branch (`proj_linear`, `gcn_modules`, `fusion_gcn_modules`, `part_para`, `pose_proj`) has 6.89M params; `mt5_model.encoder` has 277.0M (192M of that is the shared 250k-token embedding); `mt5_model.decoder` has 305.4M |
| Strict load | **0 missing / 0 unexpected keys** | `extract_unisign_features.py` asserts this |
| mT5-Base tokenizer/config | **present** | HF cache `google/mt5-base` snapshot `2eb15465…` |
| License | CC BY-NC-4.0 | research use only; unchanged from earlier reports |

**Can the released How2Sign checkpoint be used as a frozen encoder? Yes.** It is the full end-to-end model, not
a decoder-only release. Its encoder half (pose ST-GCN branch → `pose_proj` → mT5-Base encoder) can be run alone
and its output kept. What is **not** released (unchanged from the 10.05 analysis) are YouTube-ASL stage-1/2
pretrained weights. So the only available ASL encoder is one that was already **fine-tuned on How2Sign train**.

## 2. Code and feature-extraction interface

| Item | Status |
|---|---|
| Upstream repo | local clone at commit `eed438bc…` (pinned in every earlier report), clean apart from `__pycache__`, used read-only from the E0 session scratchpad |
| Pose loader | upstream `S2T_Dataset.load_pose` + `load_part_kp` + `Base_Dataset.collate_fn`, used unchanged |
| Encoder forward | upstream `Uni_Sign.forward` returns `inputs_embeds` (prefix + pose tokens) and `attention_mask`; the extractor then calls `mt5_model.encoder` on them. Nothing is reimplemented |
| Built-in "extract features" API | **none upstream.** The interface is the 40-line wrapper `scripts/extract_unisign_features.py` around the two calls above |
| Environment | conda `unisign-cpu-arm64` (Python 3.10.13, torch 2.1.1 CPU, transformers 4.40.0). `Tensor.numpy()` is broken against numpy 2.2.6 in this env, so the script converts via lists |
| Hardware | Apple M3 Pro, CPU only (no CUDA). bf16 forward takes about 20 s per clip on CPU vs **0.4 s in fp32**, so fp32 is used (see §5) |

## 3. Input poses for the exact P0.2 clips

Uni-Sign needs 133-point COCO-WholeBody RTMPose keypoints. P0.2's inputs are MediaPipe Holistic (543 points),
which **cannot be mapped faithfully** (different face topology, no per-keypoint hand scores). That mapping
would have been an invented substitute and was not attempted.

The official Uni-Sign pose archive (HF `ZechengLi19/Uni-Sign`, `how2sign_pose_format.zip.00–.03`, 33,437
entries: `train-pose-rtmpose-192/` 31,087 + `test-pose-rtmpose-192/` 2,350; no dev directory) covers every clip:

| P0.2 split | n | in official `train-` dir | in official `test-` dir | missing |
|---|---|---|---|---|
| train | 2,751 | 2,751 | 0 | **0** |
| val | 366 | 366 | 0 | **0** |
| frozen | 147 | 0 | 147 | **0** |

All 3,264 entries were range-fetched (876 MB compressed), CRC-32 verified per entry, and kept in the
session scratchpad only, not in the repo. A few HF range requests returned HTTP errors under 9-way
parallelism; they were retried with `curl --retry` and every entry finally passed CRC.

## 4. Leakage audit (critical)

Uni-Sign's own `data/How2Sign/labels.train` (31,086 clips) and `labels.test` (2,349) were checked against the
P0.2 ID lists:

| P0.2 split | in Uni-Sign `labels.train` | in Uni-Sign `labels.test` |
|---|---|---|
| train 2,751 | **2,751** | 0 |
| val 366 | **366** | 0 |
| frozen 147 | 0 | **147** |

P0.2's val split is a signer-held-out slice of How2Sign *train*, not How2Sign val. So:

- **The frozen Uni-Sign encoder was fine-tuned, end to end with its own decoder, on all 366 val clip–sentence
  pairs.** Treatment val metrics are contaminated and cannot test the hypothesis.
- The frozen 147 (How2Sign test) were never trained on by Uni-Sign. **Frozen-147 is the only clean
  endpoint.**
- Downstream training data is identical (2,751 clips), but the *representation* embeds far more supervision:
  about 31k How2Sign train pairs plus 984 h of YouTube-ASL pretraining. P0-13 compares "our representation" vs
  "this pretrained representation" at fixed downstream data. It does **not** compare architectures at equal
  total data.

## 5. Interface validation

- **Shape and coverage.** See `REPRESENTATION_INTERFACE.md` §3 (all 3,264 present, T = min(frames, 256), 768-d,
  finite).
- **Faithfulness.** Cached `enc` features for 8 frozen clips were decoded with Uni-Sign's **own** frozen mT5
  decoder (beam 4, max 100 tokens, as in the official eval). The decodes track the authors' released
  predictions for the same clips: mean sentence chrF 63.3 against them, 100.0 on one clip, and on-topic
  (salt/pepper, breathing, pasta). The remaining differences fit the upstream random sampling of clips over 256
  frames and fp32 vs bf16 (`data/interface_check.json`). **The cached features are the real Uni-Sign encoder
  output.**
- **fp32 vs bf16.** On one 264-token clip, the fp32 encoder output vs the official bf16 path gives per-frame
  cosine mean 0.99939 (min 0.967) and relative L2 0.028. The pose-embedding input to mT5 gives cosine 0.99982.
  CPU and MPS fp32 are identical.

## 6. Blockers

None that stop P0-13. Constraints carried into the results: val leakage (§4), no augmentation in the treatment,
and different frame timing/crop on the frozen set (see `P0_13_PLAN.md`, forced deviations).
