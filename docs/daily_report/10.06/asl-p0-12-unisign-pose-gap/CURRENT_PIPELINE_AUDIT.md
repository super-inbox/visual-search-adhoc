# P0-12 — Audit of the pipeline that produced BLEU-4 = 5.39

Scope: the Uni-Sign run that produced our 5.39 on the frozen 128-clip How2Sign benchmark (`how2sign_v2`).
Everything below is traced to a file on disk or to the pinned upstream code, not to memory. Where a primary
source no longer exists, that is stated.

## 1. Where the 5.39 comes from (primary artifacts)

| Artifact | Path | What it shows |
|---|---|---|
| Run directory (full outputs) | `~/Desktop/curify/visual-search-adhoc-asl-task-c/asl-translator/evaluation/results/how2sign_v2/unisign/` (`asl-task-c` worktree, read-only here) | `batch_run_128.log` (459 KB), `per_clip_results.csv/json`, `corpus_summary.json` (`corpus_sacrebleu: 5.3876`, `corpus_chrf: 22.7498`, `corpus_wer: 0.9819`), `run_metadata.json`, `predictions/` (128 json) |
| Tracked predictions | `docs/daily_report/9.2/asl-baselines/results/unisign_predictions.jsonl` | 128 rows, all `success` |
| Tracked run metadata | `docs/daily_report/9.2/asl-baselines/results/run_metadata.json` | env, patches, command, timings |
| Argparse dump of the same code path (1-clip pilot) | `docs/daily_report/8.31/asl-next-baseline/results/raw_output.txt` (per 9.15 audit) | `seed=42`, `max_length=256`, `rgb_support=False` |
| E0 re-score | `docs/daily_report/10.05/.../e0-unisign-reproduction/` | 5.39 with the official vendored BLEU code |
| Driver script `batch_inference_cpu_patched.py` | **not on disk.** The run's scratchpad is gone. E0 recovered it verbatim from session transcript `7d8d1d28-…`, which is no longer present under `~/.claude/projects/`. | Settings below come from E0's recorded audit, the run log, and the upstream code it was copied from |

Re-verified today (2026-10-06/07): `FREEZE_CHECKSUMS.sha256` hashes to `16c41282…411a` (= `FREEZE.sha256`), and all
128 videos + 128 references + manifest verify (`shasum -c`, 260/260 OK). Re-running E0's `subset_analysis.py` gives
14.50 / 9.59 / 5.39 exactly. Released-prediction files hash to E0's values (`40c0927e…`, `bbb49bc7…`).

**Behavioural reproduction of the pose input.** I re-extracted poses for all 128 clips with the same rtmlib version and
the same cached ONNX files (dated 2026-08-31, before the 2026-09-01 run). Per-clip frame counts are checked against
`n_frames` in the historical `per_clip_results.csv`; see `POSE_DIAGNOSTICS.md` §1 for the result.

## 2. Field-by-field

| Field | Value in the 5.39 run | Source |
|---|---|---|
| Checkpoint | `how2sign_pose_only_slt.pth`, 1,186,925,007 B | `run_metadata.json` |
| Checkpoint sha256 | `1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d`, re-hashed today from `~/.cache/uni_sign_checkpoints/` | equals HF LFS oid (HF API listing, today) |
| Checkpoint provenance | HF `ZechengLi19/Uni-Sign` (released 2025-12-20, CC BY-NC 4.0). Not proven to be the exact weights behind the paper's 14.5 or the released `out/` predictions (E0 C3) | E0 |
| Code | Uni-Sign @ `eed438bcb49e30405cd6ccdfcccca330c134e830` | `run_metadata.json` |
| Entry point | `batch_inference_cpu_patched.py`: `demo/online_inference.py` logic, model loaded once, loop over clips, 4 `.cuda()` calls removed | `run_metadata.json` `compatibility_patches` |
| Video source | How2Sign official test "Green Screen RGB clips (frontal view)", `test_rgb_front_clips.zip`, **full 1280×720 frame**, **clip boundaries = "English Translation (original)" timestamps** (2/128 use re-aligned timing) | `how2sign_v2/README.md`, `SELECTION_METHODOLOGY.md` §5 |
| Pose extractor | rtmlib 0.0.13 `Wholebody(to_openpose=False, mode="lightweight", backend="onnxruntime", device="cpu")` | run log lines 3–4; E0 |
| Pose models | detector `yolox_tiny_8xb8-300e_humanart` (416×416 input); pose `rtmw-dw-l-m_simcc-cocktail14_270e-256x192` (192×256 input). ONNX sha256 `ceb11c07…7250` / `68db326c…8d76` | run log; `~/.cache/rtmlib/hub/checkpoints/` |
| Keypoint format | COCO-WholeBody 133 kp, (x, y) + SimCC score per kp; person index 0 of the detector output | `demo/online_inference.py`; `datasets.py:28-29` |
| Keypoints used by the model | body 9 (COCO 0, 3–10: nose, ears, shoulders, elbows, wrists); left hand 21 (91–111); right hand 21 (112–132); face 18 (9 jaw points 23–39 step 2, inner lips 83–90, nose tip 53) | `datasets.py:31-45` |
| Coordinate normalization | ① extraction: `keypoints / (W, H)` per frame, so x and y are scaled **separately** (for us W=1280, H=720). ② `load_part_kp`: body → `crop_scale`, a **clip-level** square bbox over all valid body points → [-1, 1]. Hands are made relative to the wrist (hand kp 0) and face relative to the nose tip (53), both divided by the same body scale and clipped to [-1, 1] | `online_inference.py:96`; `datasets.py:18-104` |
| Confidence handling | score kept as the 3rd channel; any kp with score ≤ 0.3 has (x, y, c) zeroed | `datasets.py:19, 71, 104` |
| Missing-keypoint handling | rtmlib always returns all 133 kp, so "missing" only means score ≤ 0.3, which gets zeroed. A frame with 0 detected persons would crash `skeleton[0]`; none occurred (128/128 success) | code; `corpus_summary.json` |
| Pose tensor shape | per part `(T, K, 3)`, K = 9/21/21/18, T ≤ 256; batch padded by `collate_fn` | `datasets.py` |
| Frame rate / sampling | native video fps (24, 30, 29.97 or 50), **every frame**, no resampling | `online_inference.py:80-96`; 9.15 audit |
| Max sequence length | `max_length=256` (argparse default) | `utils.py:523` |
| Behaviour over 256 frames | `sorted(random.sample(range(T), 256))`. Python `random` is seeded once (42) at process start, so the draw depends on run order. Affects 34/128 clips | `datasets.py:640-641`; E0 |
| Input normalization (other) | none (pose-only, `rgb_support=False`) | argparse dump |
| Batch size | 1 | `online_inference.py` DataLoader |
| dtype | model loaded fp32 (`strict=True`, 0 missing/unexpected keys), then `model.to(bfloat16)`; inputs cast to bf16 | run log; `online_inference.py:52-57,118-120` |
| Device | CPU (Apple M3 Pro), torch 2.1.1, transformers 4.40.0 | `run_metadata.json` |
| Forward | `model(src_input, tgt_input)` with empty text, then `generate` | `S2T_Dataset_online` |
| Decoder | mT5-base (`google/mt5-base` snapshot `2eb15465…`) | E0 |
| `num_beams` / `max_new_tokens` | 4 / 100 (hardcoded literals, same as official `fine_tuning.py:263-265`) | 9.15 audit |
| Repetition / length settings | none passed: HF defaults (`repetition_penalty=1.0`, `no_repeat_ngram_size=0`, `length_penalty=1.0`, `do_sample=False`) | 9.15 audit (`models.py:313-321` forwards only 2 kwargs) |
| Post-processing | pad first output to 150 with EOS, `pad_sequence`, `batch_decode(skip_special_tokens=True)` | `online_inference.py:134-140` |
| Tokenizer | mT5 SentencePiece from the mT5-base snapshot | `models.py` |
| References | `manifest.csv` `reference_text` (How2Sign original-TSV sentence); 125/128 byte-identical to official `labels.test`, 3 differ only by mojibake in the official file | E0 |
| Reference preprocessing | none | — |
| Scorer (historical) | `sacrebleu==2.3.1` `corpus_bleu`, 13a, mixed case → 5.3876 | `corpus_summary.json` |
| Scorer (official, E0 and today) | `SLRT_metrics.sableu` → vendored sacrebleu 1.4.2 `corpus_bleu`, 13a → **5.39** (identical) | E0 `subset_analysis.py`, re-run today |
| Runtime | 4,170.6 s wall for 128 clips; pose extraction sum 1,040.7 s | `run_metadata.json`, `per_clip_results.csv` |

## 3. What this audit adds to E0

E0 listed the pose extractor as the only systematic input difference. Tracing the video source for this audit
found two more input-side differences, both upstream of the extractor. They are documented in
`OFFICIAL_VS_CURRENT_PIPELINE.md`:

1. **Clip boundaries.** Our clips are cut with How2Sign *original* timestamps. The official Uni-Sign How2Sign test
   clips are cut with the *re-aligned* timestamps. So the *video segment* differs even though the clip ID and
   reference sentence are the same.
2. **Frame geometry.** We run on the full 1280×720 frame. The official poses come from a signer-centred crop,
   ~0.8 W/H (taller than wide). Since Uni-Sign divides x by W and y by H separately, the model-input geometry
   differs systematically.

With the pose extractor (V3) and the runtime differences (V4: CPU/batch 1/single-process RNG vs CUDA/batch 8/8
workers; dtype bf16 on both), these give four separate variables. After the full 128-clip diagnostics, the
extractor is **no longer the leading suspect**. See `P0_12_PLAN.md` for the revised hypotheses and the
single-variable contrasts.
