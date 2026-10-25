# asl-unisign-decode-length-cap

The design and decision rules are in `EXPERIMENT_PLAN.md`. **Status: complete (2026-10-14), negative-result diagnostic. Results: `DECODE_LENGTH_RESULTS.md`.**
Raising `max_new_tokens` 100 → 150 → 256 leaves 126/128 outputs unchanged. Only 2 cap-hit repetition loops grow, so the
inference cap is rejected as the cause of the long-reference failure.

| Path | What it is |
|---|---|
| `patch/fine_tuning_decode_length.patch` | The only code change vs Uni-Sign `eed438bc` (`fine_tuning.py`: `max_new_tokens` from env, padding safeguard, diagnostics) |
| `patch/SHA256SUMS` | sha256 of the upstream file, the patched file and the patch |
| `runner/run_decode_length.sh` | VM runner for R100 / R150 / R256 (separate git worktree; the existing clone is untouched) |
| `runner/source_prepared_inputs_A_official.sha256` | **Source provenance.** Checksums of the original (pre-conversion) 128 A_official PKLs and `labels.test_p012_128`, from the committed P0-12 `CHECKSUMS.sha256`. The fp16 runtime PKLs are not expected to match it; only the labels line is checked at runtime |
| `A_official_fp16_runtime.sha256` (VM; its normalised, pinned copy is `results/out/RUNTIME_INPUTS_A_official.sha256`) | **Runtime manifest.** sha256 of the 128 fp16-converted A_official PKLs in `/tmp/p012_fp16` that the P0-12 T4 run read. R100/R150/R256 are verified against it before every run |
| `scripts/test_patch_cpu.py` | CPU self-test: the patch applies, padding never changes the text, diagnostics are correct |
| `scripts/r100_gate.py` | R100 vs committed A_official reproducibility gate (EXACT / CLOSE / NOT_REPRODUCED) |
| `scripts/analyze_decode_length.py` | Full R100 / R150 / R256 analysis (CPU, run locally) |
| `results/out/A_official_mnt{100,150,256}/` | The three VM output folders, copied back verbatim (R100 also has `R100_GATE.json`) |
| `results/out/RUNTIME_INPUTS_A_official.sha256` | The pinned runtime manifest (128 fp16 A_official PKLs), identical to the copy in each run folder |
| `metrics/` | `decode_length_comparison.csv`, `subset_comparison.csv`, `per_clip.csv`, `decode_length_summary.json`, `verification.json` |
| `DECODE_LENGTH_RESULTS.md` | Final results and interpretation |

## Input lineage

```
committed 10.06/.../artifacts/prepared_inputs/          (source; runner/source_prepared_inputs_A_official.sha256)
  -> one-off float16 conversion of the floating pose arrays, done for P0-12 T4/fp16 (not redone here)
  -> /tmp/p012_fp16 on the VM = the T4 runtime inputs  (A_official_fp16_runtime.sha256, 128 PKLs)
     + labels.test_p012_128, unconverted               (still matches the source checksum)
```

The P0-12 full128 T4/fp16 run read `/tmp/p012_fp16`, not the original bytes, so its PKLs cannot match the source
checksums. The runner:

1. checks that the runtime manifest lists exactly the 128 A_official PKLs of the source manifest (absolute paths under
   `$P012` or `$P012`-relative paths are both accepted), and prints how many are byte-identical to the source (expected 0);
2. pins the normalised manifest to `~/unisign_decode_length/out/RUNTIME_INPUTS_A_official.sha256` at the first
   preflight. Any later invocation whose manifest differs stops;
3. re-verifies the 128 PKLs against the pinned manifest and `labels.test_p012_128` against the source checksum, once in
   preflight and again right before each of R100/R150/R256, then copies the manifest into every run folder.

Optionally `SOURCE_PREPARED_INPUTS=<dir>` also verifies the original prepared_inputs against the source checksums.
This only proves provenance; that directory is never read by the runs.

## VM commands

Copy this folder and the committed baseline file to the VM:

```bash
# from the repo root on the laptop
scp -r docs/daily_report/10.13/asl-unisign-decode-length-cap  VM:~/decode-length-cap
scp docs/daily_report/10.13/asl-p0-12-full128-fp16/predictions/A_official.txt  VM:~/decode-length-cap/A_official.committed.txt
```

On the VM (same Python env as P0-12):

```bash
cd ~/decode-length-cap
export UNISIGN=<existing P0-12 Uni-Sign clone>   # HEAD eed438bc, unmodified
export P012=/tmp/p012_fp16                       # the existing fp16 tree used by P0-12; do NOT rebuild
export RUNTIME_MANIFEST=$PWD/A_official_fp16_runtime.sha256   # 128 fp16 A_official PKLs (default path)
export CKPT=<path>/how2sign_pose_only_slt.pth
export MT5=<path to google/mt5-base used in P0-12>
export BASELINE_PRED=$PWD/A_official.committed.txt
export OLD_RUNNER=/tmp/run_p012_full128_fp16.sh

# 0. CPU self-test of the patch (needs the pristine upstream file + mT5 tokenizer)
python -I scripts/test_patch_cpu.py "$UNISIGN/fine_tuning.py" "$MT5"

# 1. preflight only: checks everything, prints the old runner's flags next to ours, then stops
RUNS=R100 bash runner/run_decode_length.sh
#    -> compare the two invocations. If the old runner used different flags, set FT_ARGS="..." to exactly those.

# 2. R100 + gate
CONFIRM_FLAGS_MATCH=1 RUNS=R100 bash runner/run_decode_length.sh
cat ~/unisign_decode_length/out/A_official_mnt100/R100_GATE.json | head -40

# 3. only if the gate verdict is REPRODUCED_EXACT or REPRODUCED_CLOSE
CONFIRM_FLAGS_MATCH=1 RUNS="R150 R256" bash runner/run_decode_length.sh
```

If `/tmp/p012_fp16` was cleared, or the runtime manifest check fails, **stop**. Do not reconvert the pose files. A new
conversion would be a different input, and R100 could no longer be compared with P0-12 as the same run.

## Back on the laptop

```bash
D=docs/daily_report/10.13/asl-unisign-decode-length-cap
mkdir -p $D/results/out && scp -r VM:~/unisign_decode_length/out/A_official_mnt{100,150,256} VM:~/unisign_decode_length/out/RUNTIME_INPUTS_A_official.sha256 $D/results/out/
python3 -I $D/scripts/analyze_decode_length.py        # verifies the run folders, then writes $D/metrics/
```
