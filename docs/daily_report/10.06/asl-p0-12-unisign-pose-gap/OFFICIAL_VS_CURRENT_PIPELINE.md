# P0-12 — Official Uni-Sign How2Sign path vs our 5.39 path

Official sources: Uni-Sign @ `eed438bc` (`fine_tuning.py`, `datasets.py`, `utils.py`, `config.py`, `demo/`,
`docs/DATASET.md`, `README.md`). HF `ZechengLi19/Uni-Sign` file listing (API, today). **Zip central directories**
of `how2sign_pose_format.zip.00-.03` and `how2sign_rgb_format.zip.aa-.ae`, read by HTTP range request (~8.5 MB in
total, no full download). The 128 matching official pose pkls (42 MB) and official crop videos (95 MB) were
range-fetched; every entry passes its zip CRC-32. Paper arXiv 2501.15187 App. A.1 is cited via E0.

Classification: **confirmed mismatch**, **likely mismatch**, **uncertain**, **same**.

## 1. Field-by-field

| Field | Official How2Sign eval | Our 5.39 run | Class |
|---|---|---|---|
| Checkpoint | `how2sign_pose_only_slt.pth` (HF) | same file, sha256 `1bfd5f33…683fb00d` = HF LFS oid | **same** (file). Link to the paper's 14.5 not provable (E0 C3) → uncertain |
| Base LM / tokenizer | `./pretrained_weight/mt5-base` | HF `google/mt5-base` snapshot `2eb15465…` | likely same (not hash-comparable) |
| Test split / IDs | `labels.test`, 2,349 clips | 128-ID subset, all present in `labels.test` | **same IDs** (subset) |
| References | `labels.test` text | manifest text; 125/128 byte-identical, 3 differ by official-file mojibake; BLEU unchanged | **same** for scoring |
| **Clip boundaries (temporal segment)** | Official crop clips (`crop_test/*.mp4`) and pose pkls match How2Sign **re-aligned** timestamps: 128/128 within 0.25 s, 126/128 within 0.1 s, max \|Δ\| 0.11 s | How2Sign official clip archive cut at **original** timestamps (manifest; 2/128 re-aligned) | **confirmed mismatch.** IoU(ours, re-aligned) median 0.555; **28/128 have zero overlap**; 61/128 < 0.5; 16/128 ≥ 0.9 (`data/segment_alignment_128.json`) |
| Frame count fed to the loader | official pkl frames = official crop video frames (128/128) | our video frames (474 for clip 1, …) | **confirmed mismatch** (consequence of the row above): official/ours ratio 0.17–2.46, median 1.09; only 5/128 equal |
| **Frame geometry / crop** | signer-centred crop; W 324–758, H 510–640, median H/W 1.23 (`w_h` stored in each pkl) | full frame 1280×720, H/W 0.5625 | **confirmed mismatch** |
| Coordinate normalization | `kp / (W, H)` of the crop, then `crop_scale` | `kp / (1280, 720)`, then `crop_scale` | same code, **different input aspect.** Because x and y are divided separately, the model-input body/hand geometry is horizontally squashed ~2× relative to training (measured in `POSE_DIAGNOSTICS.md` §3) → **confirmed mismatch** |
| Pose source | pre-extracted pkl, dir `test-pose-rtmpose-192` (train: `train-pose-rtmpose-192`); DATASET.md: "extracted using RTMPose from MMPose"; paper: RTMPose-x | live rtmlib `lightweight`: YOLOX-tiny + RTMW-dw-l-m 256×192 (ONNX) | **uncertain as to model identity.** The "192" suffix matches a 256×192 input like ours, not RTMPose-x 384×288. On identical frames the keypoints agree closely (`POSE_DIAGNOSTICS.md` §2) |
| Upstream "lighter" demo | README 2025-06-05: "Release lighter pose extraction"; `demo/pose_extraction.py` default `mode="lightweight"` | we used exactly the demo's lightweight mode | **same as the official demo**, which is distinct from how the training/eval pkls were made |
| pkl structure | `{'keypoints': [T×(1,133,2) float64], 'scores': [T×(1,133) float32], 'w_h': [W,H]}`; always exactly 1 person | in-memory dict, `(N,133,2)` per frame; person 0 used | same format; person count: see diagnostics |
| Keypoint ordering | COCO-WholeBody 133 | COCO-WholeBody 133 | **same** |
| Confidence scale / threshold | SimCC scores ~1.0 median; threshold 0.3 in loader | same loader; scale in `POSE_DIAGNOSTICS.md` | same threshold; scales measured |
| Loader class | `S2T_Dataset` (pkl from disk) | `S2T_Dataset_online` (in-memory) | same logic for pose-only (E0) |
| Max length / >256 | 256, `sorted(random.sample)` | same rule | same rule. RNG stream differs (8 workers vs single process) → **confirmed mismatch**, affects 36 official / 34 our clips >256 frames |
| Seed | 42 | 42 | same value |
| Batch size | 8 (`eval_stage3.sh`) | 1 | **confirmed mismatch**; padding masked via `attention_mask`; effect unmeasured |
| dtype | deepspeed bf16 | bf16 | same nominal dtype |
| Device / kernels | CUDA via deepspeed engine (`.cuda()` hardcoded L69/254/276) | CPU | **confirmed mismatch**; effect unmeasured (likely small) |
| Forward | `model(src, tgt)` with refs | with empty text | generation ignores refs (`models.py:313-321`) → same for outputs |
| Decoding | `generate(max_new_tokens=100, num_beams=4)` | same literals; HF defaults otherwise | **same** |
| Post-processing | pad to 150, `batch_decode(skip_special_tokens=True)` | same | **same** |
| BLEU | `SLRT_metrics.sableu` → vendored sacrebleu 1.4.2, 13a | sacrebleu 2.3.1 13a; official code gives identical 5.39 | **same numerically** |
| Other metrics | ROUGE-L (`rouge`), BLEURT-20 (`--eval` only, imported **before** prediction files are written, `fine_tuning.py:292-322`) | WER/CER/chrF | n/a to BLEU; BLEURT is a run prerequisite |
| CUDA / deepspeed | required | absent on this machine (Step 4) | blocker for inference, not a pipeline difference |
| `config.py` How2Sign pose path | upstream points at WLASL; must be set to `<root>/{}-pose-rtmpose-192` (`datasets.py:426` uses `.format(phase)`) | n/a | setup item |

## 2. What changed relative to E0

E0 framed the 9.59 → 5.39 gap as "same clips, same refs, same scorer, different inference path", with the pose
extractor as the only systematic input difference. That remains true for **IDs, references and scorer**. It is
**not** true for the **video content**: the authors' predictions come from re-aligned segments, and ours from
original-timestamp segments that in 28/128 cases do not overlap the re-aligned signing window at all. E0's
numbers are unchanged. This adds a variable E0 could not see without the official pkls.

## 3. The mismatches, grouped into four separate variables (ranked by measured input-level size)

| Rank | Variable | Rows above | Input-level size | Translation-level status |
|---|---|---|---|---|
| 1 | **V1 Timestamp alignment** | clip boundaries, frame count | large: 28/128 zero overlap; IoU median 0.555 | observational support (`P0_12_RESULTS.md` §3) |
| 2 | **V2 Crop / coordinate normalization** | frame geometry, coordinate normalization | large: model-input width ~0.44× | untested |
| 3 | **V4 dtype / device / batch / inference** | device, batch, RNG, loader class (dtype equal: bf16) | not observable without GPU | untested; expected small |
| 4 | **V3 Pose extractor model** | pose source | small: 0.85 % / ~1.6 % of shoulder width on identical frames | untested; **no longer the leading suspect** |

The original framing ("the extractor is the only systematic input difference") is replaced by this table. V3 is
ranked last because of its measured input-level size, not because of translation evidence. V4 is ranked above V3
only because it is unmeasured.
