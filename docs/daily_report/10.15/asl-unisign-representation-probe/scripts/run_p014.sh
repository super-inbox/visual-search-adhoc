#!/usr/bin/env bash
# P0-14 runner (PROPOSED - NOT YET RUN). Each stage is gated; nothing here trains Uni-Sign.
#
#   stage 0  smoke     : 128 committed A_official test PKLs (already in the repo), CPU, ~2 min.
#                        Checks shapes, finiteness, and decodes 8 clips with Uni-Sign's own decoder; the decodes must
#                        track the committed P0-12 A_official predictions (faithfulness gate, same idea as P0-13).
#   stage 1  fetch     : download the official pose archive (4 parts, 8.46 GB) and concatenate it.
#   stage 2  extract   : one frozen forward pass over probe_train (31,086) + test_clean (2,209) -> pooled R1/R2/R3.
#   stage 3  probe     : LR probes (all draws, Design A + B), then MLP probes (p10/p25/p100 only).
#   stage 4  analyze   : paired cluster bootstrap + pre-registered decision rules -> results/DECISION.json
#
# Usage: STAGE=0 bash run_p014.sh     (then STAGE=1, 2, 3, 4)
# Env:   UNISIGN_REPO (clone of github.com/ZechengLi19/Uni-Sign at eed438bc), MT5 (google/mt5-base snapshot dir),
#        CKPT (how2sign_pose_only_slt.pth, sha256 1bfd5f33...683fb00d), WORK (big scratch dir, >= 15 GB free),
#        PY_UNISIGN (python of the Uni-Sign env), PY_PROBE (python with torch + numpy), DEVICE (cpu|cuda)
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
: "${UNISIGN_REPO:?}" "${MT5:?}" "${CKPT:?}" "${WORK:?}" "${PY_UNISIGN:?}" "${PY_PROBE:?}"
DEVICE="${DEVICE:-cpu}"
REPO_ROOT="$(cd "$HERE/../../../.." && pwd)"
A_OFFICIAL="$REPO_ROOT/docs/daily_report/10.06/asl-p0-12-unisign-pose-gap/artifacts/prepared_inputs/A_official/test-pose-rtmpose-192"

case "${STAGE:?set STAGE=0..4}" in
0)
  ( cd "$HERE/splits" && shasum -a 256 -c SPLITS.sha256 )
  echo "$(shasum -a 256 "$CKPT" | cut -c1-16)  (expect 1bfd5f3312f04e47)"
  python3 - "$HERE/splits/manifest.csv" "$A_OFFICIAL" "$WORK/smoke_manifest.csv" <<'EOF'
import csv, os, sys
man, pdir, out = sys.argv[1:4]
have = {f[:-4] for f in os.listdir(pdir)}
rows = [r for r in csv.DictReader(open(man)) if r["clip_id"] in have]
w = csv.DictWriter(open(out, "w", newline=""), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("smoke clips", len(rows), "roles", {r["role"] for r in rows})
EOF
  "$PY_UNISIGN" -I "$HERE/scripts/extract_representations.py" --unisign-repo "$UNISIGN_REPO" --mt5 "$MT5" --ckpt "$CKPT" \
     --manifest "$WORK/smoke_manifest.csv" --roles test_clean,test_dup_excluded --pose-dir "$A_OFFICIAL" \
     --out "$WORK/features_smoke" --device "$DEVICE" --decode-check 8 --save-seq-roles ""
  echo "Compare $WORK/features_smoke/decode_check.json with 10.13/asl-p0-12-full128-fp16/predictions/A_official.txt"
  ;;
1)
  mkdir -p "$WORK/archive"
  for s in 00 01 02 03; do
    curl -L --fail --retry 8 -C - -o "$WORK/archive/how2sign_pose_format.zip.$s" \
      "https://huggingface.co/ZechengLi19/Uni-Sign/resolve/main/how2sign_pose_format.zip.$s"
  done
  cat "$WORK"/archive/how2sign_pose_format.zip.0{0,1,2,3} > "$WORK/archive/how2sign_pose_format.zip"
  ls -l "$WORK/archive/how2sign_pose_format.zip"   # expect 8,465,474,575 bytes (3 x 2 GiB + 2,023,023,631)
  ;;
2)
  "$PY_UNISIGN" -I "$HERE/scripts/extract_representations.py" --unisign-repo "$UNISIGN_REPO" --mt5 "$MT5" --ckpt "$CKPT" \
     --manifest "$HERE/splits/manifest.csv" --roles probe_train,test_clean --zip "$WORK/archive/how2sign_pose_format.zip" \
     --out "$WORK/features" --device "$DEVICE" --save-seq-roles test_clean
  ;;
3)
  "$PY_PROBE" -I "$HERE/scripts/run_probe.py" --probe-dir "$HERE" --features "$WORK/features" \
     --reps raw,fsign,mt5,length,shuffle --pools ms,msd,seg4 --draws all --probe lr --out "$WORK/results/lr"
  "$PY_PROBE" -I "$HERE/scripts/run_probe.py" --probe-dir "$HERE" --features "$WORK/features" \
     --reps raw,fsign,mt5 --pools ms --draws p10_d0,p10_d1,p10_d2,p25_d0,p25_d1,p25_d2,p100_d0 --probe mlp --out "$WORK/results/mlp"
  ;;
4)
  "$PY_PROBE" -I "$HERE/scripts/analyze_probe.py" --probe-dir "$HERE" --results "$WORK/results/lr" --primary-draw p100_d0
  ;;
esac
