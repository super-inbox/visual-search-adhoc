# P0-14: Uni-Sign Representation Probe for Specialist Fusion

**Status (2026-10-15): full extraction, decoder baseline and frozen LR probe complete. Results in
`FULL_RUN_REPORT.md`, evidence in `full_run/`. Formal verdict: PARTIAL SUPPORT (S1 sanity gate missed).**

- `EXPERIMENT_PLAN.md`: question, the three representations, probe, pooling, metrics, low-data draws,
  **pre-registered success criteria (§9)**, compute estimates, limits.
- `DATA_AUDIT.md`: what data, poses, checkpoints and features exist, and the leakage findings.
- `concepts/concept_list_v1.csv`: proposed concepts (24 lexical + 6 semantic groups), selected from train only.
- `splits/`: frozen manifest, video-level low-data draws and hashes.
- `scripts/`: see the layout in `EXPERIMENT_PLAN.md` §15.

## Re-running what was already run (CPU, seconds, no model)

```bash
R=~/Desktop/curify/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/landmark_t5_1pct/local_run_10pct/raw_download
D=docs/daily_report/10.15/asl-unisign-representation-probe
python3 -I $D/scripts/build_concepts.py $R/how2sign_realigned_{train,val,test}.csv $D
python3 -I $D/scripts/list_pose_archive.py $D/audit/official_pose_archive_index.csv       # ~3 s, range requests only
python3 -I $D/scripts/build_splits.py $R/how2sign_realigned_{train,val,test}.csv $D/audit/official_pose_archive_index.csv $D
( cd $D/splits && shasum -a 256 -c SPLITS.sha256 )
```

Synthetic self-test of the probe and decision code (no real features):

```bash
PY=~/Desktop/curify/gloss-free-asl-translation/.venv/bin/python   # torch + numpy
$PY -I $D/scripts/run_probe.py --probe-dir $D --synthetic [--synthetic-null] --draws p10_d0,p25_d0,testcv_r0 --out /tmp/x/lr
$PY -I $D/scripts/analyze_probe.py --probe-dir $D --results /tmp/x/lr --primary-draw p25_d0 --B 400
```

## Full-run commands (already run; results in `FULL_RUN_REPORT.md`)

```bash
git clone https://github.com/ZechengLi19/Uni-Sign $WORK/Uni-Sign && git -C $WORK/Uni-Sign checkout eed438bc
export UNISIGN_REPO=$WORK/Uni-Sign MT5=~/.cache/huggingface/hub/models--google--mt5-base/snapshots/2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f \
       CKPT=~/.cache/uni_sign_checkpoints/how2sign_pose_only_slt.pth WORK=... DEVICE=cpu \
       PY_UNISIGN=/opt/anaconda3/envs/unisign-cpu-arm64/bin/python PY_PROBE=~/Desktop/curify/gloss-free-asl-translation/.venv/bin/python
STAGE=0 bash $D/scripts/run_p014.sh   # smoke on the 128 committed test PKLs + faithfulness decode  (gate)
STAGE=1 bash $D/scripts/run_p014.sh   # download official poses (8.46 GB)
STAGE=2 bash $D/scripts/run_p014.sh   # extract R1/R2/R3 (≈ 3.7 h Mac CPU, or < 1.5 h on the T4)
STAGE=3 bash $D/scripts/run_p014.sh   # probes (≈ 1–2 h CPU)
STAGE=4 bash $D/scripts/run_p014.sh   # bootstrap + verdicts -> results/DECISION.json
```

The Uni-Sign env path may need patching as in P0-13: `config.mt5_path` is set by the script, and on CPU the
upstream patch `curify-studio/uni_sign_server/patches/unisign_cpu_and_mt5path.patch` may apply.
