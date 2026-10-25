#!/usr/bin/env bash
# P0-19 Stage 0 on baobao-training-t4 (run from ~/p019 on the VM, after the upload in EXPERIMENT_PLAN.md section 6).
# Main run: 2,209 test_clean clips, k=4 and k=8. Repeat run: first 40 clips, separate process (gate G2).
# Both runs are resumable (Spot preemption): re-running this script continues where it stopped.
set -euo pipefail
source "$HOME/p019/env.sh"     # PY REPO MT5 CKPT Z: the P0-14 Stage 4 values (p014-work/full/env.sh), uploaded
S=$HOME/p019/repo/docs/daily_report/10.20/asl-p0-19-safe-rerank/scripts
W=$HOME/p019/stage0
mkdir -p "$W"
{
  echo "start $(date -Is)"; nvidia-smi --query-gpu=name,driver_version --format=csv,noheader; df -h "$HOME" | tail -1
  sha256sum "$CKPT"
} | tee -a "$W/preflight.log"
"$PY" -I "$S/decode_topk.py" --unisign-repo "$REPO" --mt5 "$MT5" --ckpt "$CKPT" --zip "$Z" \
      --out "$W/main" --device cuda 2>&1 | tee -a "$W/main.log"
"$PY" -I "$S/decode_topk.py" --unisign-repo "$REPO" --mt5 "$MT5" --ckpt "$CKPT" --zip "$Z" \
      --out "$W/repeat" --limit 40 --device cuda 2>&1 | tee -a "$W/repeat.log"
(cd "$W" && sha256sum main/* repeat/* > SHA256SUMS)
echo "end $(date -Is)" | tee -a "$W/preflight.log"
