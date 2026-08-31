# OpenSLT — one-clip CPU inference result, 2026-08-31

**Status: SUCCESS.** A real English prediction was obtained from the
released OpenSLT How2Sign checkpoint (`checkpoint.best_reduced_sacrebleu_3.5401.pt`),
run entirely on CPU on this Apple Silicon Mac, on the first clip of our
frozen 19-clip How2Sign benchmark. Per instructions, this stops here — the
remaining 18 clips were **not** run.

## Clip

| Field | Value |
|---|---|
| CLIP_ID | `-g0iPSnQt6w_11-1-rgb_front` |
| Selection | First row of the frozen `manifest.csv` (row order, not cherry-picked) |
| Duration | 5.27s |
| Source | official How2Sign test split |

## Reference vs. prediction

**REFERENCE** (official How2Sign test-split translation, also our benchmark's own reference text):
> what you're going to do is you're going to take both your arms and they're going to come underneath your legs.

**PREDICTION** (OpenSLT checkpoint, detokenized, CPU, beam=5, official config):
> so, what i' be/ to do is i' be/ to from all together pressure the kick.

The prediction is fluent-shaped but semantically diverges quickly after
"what" — it does not track the reference's content (arms/legs) at all. This
is one data point from one small (11.7M-parameter) checkpoint on one short
clip; no generalization claim is made from n=1.

## Metrics

| Metric | Value |
|---|---|
| WER | 0.8333 (12 substitutions, 8 deletions, 0 insertions / 24 reference words) |
| CER | 0.6789 |
| sacreBLEU | 7.67 (30.0/10.5/5.6/2.9 n-gram precisions, BP=0.905) |
| chrF | 15.97 |
| Temporal IoU | **not computed** — OpenSLT produces sentence-level translation only, no timestamps; not meaningful here (per instructions) |

WER/CER computed with this repo's own `asl-eval/lib.py` (the same tool used
for every other WER/CER comparison in this project — SignCaption, baseline0,
temperature0). sacreBLEU is fairseq's own `--scoring sacrebleu` output
(independently recomputed via the `sacrebleu` Python package directly on the
same two strings — **7.668882940082428, matching fairseq's reported 7.67
exactly** — a cross-check, not a re-derivation). chrF computed the same way,
since fairseq's own `--scoring` flag only supports one scorer per run and
chrF wasn't requested in the official generate command.

## Runtime

**4 seconds wall-clock** for the full `fairseq-generate` process (env
activation → model load → single-clip decode → scoring → exit), on CPU, no
GPU/MPS involved. Model loading alone (a separate, earlier standalone check)
took 0.45s and ~197MB peak RSS.

## Exact command run

```bash
fairseq-generate /private/tmp/.../scratchpad/openslt_one_clip_run/i3d_data \
  --path asl-translator/data/public_benchmarks/how2sign/openslt_checkpoint/checkpoint.best_reduced_sacrebleu_3.5401.pt \
  --task sign_to_text \
  --gen-subset cvpr23.fairseq.i3d.test.how2sign \
  --seed 48151623 \
  --cpu \
  --num-workers 0 \
  --batch-size 32 \
  --scoring sacrebleu \
  --max-source-positions 1024 \
  --max-target-positions 1024 \
  --max-tokens 16000 \
  --beam 5 \
  --sacrebleu --sacrebleu-tokenizer 13a \
  --bpe sentencepiece --sentencepiece-model asl-translator/data/public_benchmarks/how2sign/openslt_checkpoint/vocab/cvpr23.train.how2sign.unigram7000_lowercased.model \
  --skip-invalid-size-inputs-valid-test > raw_generation.txt
```

Every flag here matches the official `Taskfile.yml` `generate:` target
verbatim (`--seed 48151623`, `--beam 5`, `--max-tokens 16000`,
`--sacrebleu-tokenizer 13a`, etc. — none tuned), with exactly two additions,
both zero-effect on decoding/model output:
- `--cpu` — required to run without a GPU (the milestone's whole point).
- `--num-workers 0` — disables PyTorch DataLoader subprocess workers; without
  it, macOS's `spawn`-based multiprocessing (vs. Linux's default `fork`)
  fails to pickle one of fairseq's config `Enum` classes. This is a
  data-loading plumbing flag, not a decoding parameter — it does not touch
  beam search, sampling, temperature, or scoring in any way.

Full raw output: `raw_generation.txt` in this folder.

## Data-wiring performed for this run (not touching authoritative data)

- Filtered the checksum-verified official
  `cvpr23.fairseq.i3d.test.how2sign.tab` to exactly this one row, preserving
  its official `signs_offset`/`signs_length`/`translation` unchanged.
- Renamed to the required `cvpr23.fairseq.i3d.test.how2sign.tsv` (loader
  requires this exact filename — see `OPENSLT_REPRODUCTION_PLAN.md` §6).
- Rewrote only the `signs_file` column from the original author's cluster
  path to the local, already-extracted, already-verified
  `openslt_features/-g0iPSnQt6w_11-1-rgb_front.npy`.
- This one-row scratch TSV lives entirely outside authoritative benchmark
  data, at `<session scratchpad>/openslt_one_clip_run/i3d_data/` — never
  written into `asl-translator/data/public_benchmarks/how2sign/manifest.csv`
  or any other tracked/authoritative file.
- Confirmed (by reading `sign_features_dataset.py`) that `signs_offset`/
  `signs_length` are bookkeeping-only for the `i3d` feature type and are
  **not** used to slice the loaded array — so the offset value inherited
  from the official row (2005, larger than our 100-frame extracted file) is
  harmless, not a bug.
