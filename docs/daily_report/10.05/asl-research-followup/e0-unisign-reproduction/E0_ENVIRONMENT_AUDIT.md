# E0 — Environment audit

Audit date: 2026-10-05. Machine: Apple M3 Pro, 18 GiB RAM (`hw.memsize` 19,327,352,832), macOS (Darwin 23.1.0), 455 GiB free disk.

## 1. Hardware

| Item | Official eval expects | This machine | Blocker? |
|---|---|---|---|
| GPU | CUDA GPU (`model.cuda()`, deepspeed engine, `--include localhost:0`) | None. `torch.cuda.is_available()=False`, `nvidia-smi` absent; MPS available | **Yes**: official script can't run unmodified |
| bf16 | deepspeed `dtype=bf16` default (`utils.py:501`) | CPU bf16 works (our 5.4 run used it); not numerically identical to CUDA bf16 kernels | Not a blocker for us, but a source of numeric difference |

## 2. Software (`/opt/anaconda3/envs/unisign-cpu-arm64`)

| Package | Official `requirements.txt` | Installed | Note |
|---|---|---|---|
| python | 3.9 (README) | 3.10.13 | bumped for decord arm64 wheel (documented 9.2) |
| torch | per requirements | 2.1.1 CPU | |
| transformers | per requirements | 4.40.0 | |
| deepspeed | required (import + engine) | 0.16.3, pure-Python, no CUDA ops | Engine init on CPU is untested |
| sacrebleu | vendored `external_metrics/sacrebleu.py` v1.4.2 is what the eval uses | pip 2.2.0 also present | Both give identical BLEU on the official outputs (14.4988) |
| rouge | `from rouge import Rouge` in `translation_performance` | **not installed** | ROUGE only; BLEU is computed via `sableu` directly in our scripts |
| bleurt + BLEURT-20 | imported unconditionally for How2Sign `--eval` | **not installed** | **Blocker** for the unmodified official script (crashes before writing outputs) |
| rtmlib | `demo/rtmlib-main` (bundled) | used in our 5.4 run (`mode="lightweight"`) | Not part of the official *eval* path at all (eval reads pre-extracted pkl poses) |

## 3. Assets

| Asset | Required by official eval | Local status | Verified |
|---|---|---|---|
| Checkpoint `how2sign_pose_only_slt.pth` | `--finetune` | Present: `~/.cache/uni_sign_checkpoints/how2sign_pose_only_slt.pth` (1,186,925,007 B); second copy in `curify-studio/uni_sign_server/checkpoints/` (not touched) | sha256 `1bfd5f33…683fb00d` **equals the HF LFS object id** for `ZechengLi19/Uni-Sign/how2sign_pose_only_slt.pth` (checked today via HF API). It is the released file. Nothing in the repo or model card states that this exact file produced the paper's 14.5 or the released `out/` predictions. |
| mT5-base | `config.mt5_path` | Present: `~/.cache/uni_sign_hf/hub/models--google--mt5-base` snapshot `2eb15465…` | Not hash-compared to the authors' copy (they don't publish one) |
| Test labels `data/How2Sign/labels.test` | `test_label_paths["How2Sign"]` | Present in the repo clone (gzip pickle, 2,349 entries) | sha256 `3e4c70aa…fad1`; all 128 of our clips are in it |
| Official How2Sign poses `how2sign_pose_format.zip.00–.03` | `pose_dirs["How2Sign"]/test/*.pkl` | **Not downloaded** (public on HF, 4 parts, 8,465,474,575 B; LFS oids `cfbc90d0…`, `e1f8ad67…`, `8e5d8043…`, `a091c9cd…`) | n/a |
| Official released predictions/refs `out/eval_how2sign_pose_only/test_tmp_{pres,refs}.txt` | not required, but the authors' own output | Present in the repo clone (added in upstream commits `27eb4f8`/`2c9028f`, 2026-01-03, "upload pose only evaluation result") | sha256 pres `40c0927e…8b10`, refs `bbb49bc7…4cf2`; 2,349 lines each |
| Our 128-clip predictions | n/a | `docs/daily_report/9.2/asl-baselines/results/unisign_predictions.jsonl` (tracked) | 128 rows, all `success` |
| Our original batch script (`batch_inference_cpu_patched.py`) | n/a | The scratchpad copy is gone. **Recovered verbatim** from the 2026-09-01 session transcript (`~/.claude/projects/-Users-baobaoli-Desktop-visual-search-adhoc-asl-task-c/7d8d1d28-….jsonl`, the `Write` tool call) | Settings below come from that recovered source |

## 4. Our 5.4 run: exact configuration (from the recovered script and run log)

- Driver: copy of `demo/online_inference.py` logic, batched over clips, with the 4 `.cuda()` calls removed.
- Pose: `rtmlib.Wholebody(mode="lightweight", backend="onnxruntime", device="cpu")` →
  `yolox_tiny_8xb8-300e_humanart` + `rtmw-dw-l-m_simcc-cocktail14_270e-256x192` (from `batch_run_128.log` lines 3–4). Every frame, normalized by (W, H).
- Dataset class: `S2T_Dataset_online` (one new instance per clip), `max_length=256` random subsample if longer, `random` seeded **once** with 42 at process start (so a clip's subsample depends on its position in the run).
- Model: fp32 load, `strict=True` (0 missing / 0 unexpected keys), then `model.eval(); model.to(torch.bfloat16)`; inputs cast to bf16; CPU.
- Batch size 1.
- Decoding: `generate(max_new_tokens=100, num_beams=4)`, pad to 150, `batch_decode(skip_special_tokens=True)`.
- Scoring: `sacrebleu==2.3.1` corpus BLEU, 13a (9.2 report). Re-scored today with the official vendored 1.4.2 code: **5.39**, identical.

## 5. Repo clone used for this audit

`git clone https://github.com/ZechengLi19/Uni-Sign` into the session scratchpad, checked out
`eed438bcb49e30405cd6ccdfcccca330c134e830` (2026-02-11), which is also upstream `HEAD` as of today. That is the same commit our 9.2 run pinned.
