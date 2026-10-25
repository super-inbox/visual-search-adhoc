#!/bin/bash
# P0-11 orchestrator: verify archive -> extract -> check files -> launch p25/p50/p100 concurrently (CPU).
# Usage: run_p011.sh WORK_DIR REPORT_DIR
set -euo pipefail
S="$1"; D="$2"
G=~/Desktop/curify/gloss-free-asl-translation
N=~/Desktop/curify/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/landmark_t5_1pct
EXPECTED=d5bd21a9b1b8944c6ea27ab3e518aafff808d286d1054c4fcaefd8b97224cbc5
ACTUAL=$(shasum -a 256 "$S/raw/train_frontal.rar" | awk '{print $1}')
echo "sha256 $ACTUAL"; [ "$ACTUAL" = "$EXPECTED" ] || { echo "STOP: archive hash mismatch"; exit 2; }
mkdir -p "$S/landmarks"
[ -d "$S/landmarks/frontal" ] || /opt/homebrew/bin/unar -q -f -o "$S/landmarks" "$S/raw/train_frontal.rar"
echo "extracted $(ls "$S/landmarks/frontal" | wc -l) files"
python3 - "$S/landmarks/frontal" "$D/splits" "$N/local_run_10pct/work/holdout_split.json" <<'PY'
import sys, json
from pathlib import Path
d, sd, sp = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
need = {l.strip() for l in open(sd / "train_p100.txt") if l.strip()} | set(json.load(open(sp))["val"])
miss = [i for i in need if not (d / f"{i}_holistic.npy").exists()]
print("needed", len(need), "missing", len(miss)); assert not miss, miss[:5]
PY
cd "$G"
for c in p25 p50 p100; do
  OMP_NUM_THREADS=4 PYTHONPATH="$G" .venv/bin/python "$D/scripts/train_p011.py" \
    --stage-dir "$S/landmarks/frontal" --metadata "$S/full_train_metadata.csv" \
    --split-json "$N/local_run_10pct/work/holdout_split.json" --raw-dir "$N/local_run_10pct/raw_download" \
    --frozen-landmarks "$N/frozen_benchmark_mediapipe_eval/landmarks" \
    --frozen-metadata "$N/frozen_benchmark_mediapipe_eval/frozen_benchmark_metadata.csv" \
    --frozen-denylist "$N/frozen_denylist.json" \
    --how2sign-v2-manifest ~/Desktop/curify/visual-search-adhoc-asl-task-c/asl-translator/data/public_benchmarks/how2sign_v2/manifest.csv \
    --train-ids "$D/splits/train_$c.txt" --max-steps 10320 --patience 10 \
    --output-dir "$S/runs/$c" > "$S/logs/train_$c.log" 2>&1 &
done
wait
grep -h "^\[done\]" "$S"/logs/train_p*.log
