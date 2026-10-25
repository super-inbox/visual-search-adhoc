#!/usr/bin/env bash
# Chunked-decoding pilot (spec: ../PILOT_PLAN.md). PREPARED, NOT RUN.
# Reuses, unchanged, the decode-length setup on the same T4 VM: pinned Uni-Sign eed438bc in the separate patched worktree
# ($DL_WORK/Uni-Sign-dl, fine_tuning.py = decode-length patch; max_new_tokens left at the upstream 100), the same checkpoint,
# the same fp16 runtime PKLs ($P012, checked against the pinned runtime manifest), the same launch flags (T4, fp16,
# batch 8, num_beams 4, seed 42, max_length 256, 8 workers). No training.
# What differs per arm is only the input: config.py points labels + pose dir at $PILOT/<ARM>/ (chunk PKLs built from
# the runtime PKLs by scripts/make_chunks.py build, using the frozen chunk_plan.csv).
# Usage:
#   bash run_chunk_pilot.sh        # build inputs -> loader/frame-slice validation -> SMOKE -> U36 -> U36 gate
#                                  # -> (only if the gate passes) S1 S2 S3 -> BLEURT-20 on the joined outputs
#   ARMS="..." restricts the arms; S1/S2/S3 are always refused unless $OUT/U36_GATE.json says pass.
# U36 decodes all 128 clips unchunked from the pilot input copy (same RNG stream as R100); the gate needs the 36 pilot
# clips byte-identical to the committed R100 predictions ($BASELINE_PRED).
set -euo pipefail
: "${P012:?/tmp/p012_fp16 (the P0-12 T4 runtime tree)}"; : "${CKPT:?how2sign_pose_only_slt.pth}"; : "${MT5:?google/mt5-base}"
DL_WORK="${DL_WORK:-$HOME/unisign_decode_length}"          # decode-length work dir (worktree + pinned manifest)
PW="${PW:-$HOME/unisign_chunk_pilot}"; PILOT="$PW/inputs"; OUT="$PW/out"
ARMS="${ARMS:-SMOKE U36 S1 S2 S3}"; : "${BASELINE_PRED:?committed A_official.txt (= R100), e.g. ~/decode-length-cap/A_official.committed.txt}"; MASTER_PORT="${MASTER_PORT:-29511}"
FT_ARGS="--batch-size 8 --gradient-accumulation-steps 1 --epochs 20 --opt AdamW --lr 3e-4 --dataset How2Sign --task SLT --eval --dtype fp16"
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
WT="$DL_WORK/Uni-Sign-dl"; RT_PIN="$DL_WORK/out/RUNTIME_INPUTS_A_official.sha256"
CKPT_SHA=1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d
PATCHED_FT_SHA=f13e168967c974fc690a1a8393326b5aeceb1e3aaba91521953687ee7fed99bc
die () { echo "STOP: $*" >&2; exit 1; }
mkdir -p "$PW" "$OUT"

# ---- 0. preconditions (same pins as the decode-length runs) ----
echo "$CKPT_SHA  $CKPT" | sha256sum -c - || die "checkpoint sha256"
GPU="$(python -c "import torch; assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0))")"
case "$GPU" in *T4*) ;; *) die "GPU is '$GPU', expected Tesla T4";; esac
echo "d865008bc0a16ba0fb3bceb6f78f5a7153febe1d69ba756cc83f918d57300e4a  $BASELINE_PRED" | sha256sum -c - || die "BASELINE_PRED is not the committed R100 A_official.txt"
(cd "$ROOT" && sha256sum -c --quiet FREEZE.sha256) || die "frozen analysis / plan files changed since FREEZE.sha256 was recorded"
[ -d "$WT" ] || die "decode-length worktree $WT missing"
echo "$PATCHED_FT_SHA  $WT/fine_tuning.py" | sha256sum -c - || die "worktree fine_tuning.py is not the decode-length patch"
git -C "$WT" diff --quiet -- models.py utils.py datasets.py || die "worktree has changes outside fine_tuning.py"
[ -e "$WT/BLEURT-20" ] || die "BLEURT-20 missing in $WT"
[ -f "$RT_PIN" ] || die "pinned runtime manifest $RT_PIN missing"
(cd "$P012" && sha256sum -c --quiet "$RT_PIN") || die "$P012 A_official PKLs differ from the pinned runtime manifest"
[ -z "${UNISIGN_MAX_NEW_TOKENS:-}" ] || die "unset UNISIGN_MAX_NEW_TOKENS (the pilot uses the upstream 100)"

# ---- 1. build pilot inputs once, from the runtime PKLs + frozen plan; pin their checksums ----
if [ ! -d "$PILOT" ]; then
  python -I "$ROOT/scripts/make_chunks.py" build --runtime-pose-dir "$P012/A_official/test-pose-rtmpose-192" \
         --labels "$P012/labels.test_p012_128" --out "$PILOT"
  sha256sum "$ROOT/chunk_plan.csv" "$ROOT/pilot_clips.csv" > "$PW/PLAN.sha256"
fi
(cd "$PILOT" && sha256sum -c --quiet PILOT_INPUTS.sha256) || die "pilot inputs changed since they were built"
sha256sum -c --quiet "$PW/PLAN.sha256" || die "chunk_plan.csv / pilot_clips.csv changed since the inputs were built"

# ---- 2. loader check (CPU, no model): chunk tensors == full-clip tensors [start:end) ----
cd "$WT"; git checkout -- config.py
sed -i "s#^mt5_path = .*#mt5_path = \"$MT5\"#" config.py
[ -f "$OUT/loader_check.json" ] || python -I "$ROOT/scripts/check_loader_chunks.py" "$WT" "$PILOT" "$P012/A_official/test-pose-rtmpose-192" \
     "$P012/labels.test_p012_128" "$ROOT" "$OUT/loader_check.json" || die "loader/frame-slice validation failed (see $OUT/loader_check.json)"
python -c "import json,sys; sys.exit(0 if json.load(open('$OUT/loader_check.json'))['pass'] else 1)" || die "loader check did not pass"

# ---- 3. runs ----
run_arm () {
  local ARM="$1" D="$OUT/$1" N
  [ -e "$D/test_tmp_pres.txt" ] && die "$D already has predictions; move it away first"
  N="$(python -c "import gzip,pickle; print(len(pickle.load(gzip.open('$PILOT/$ARM/labels.test_pilot','rb'))))")"
  git checkout -- config.py
  sed -i "s#^mt5_path = .*#mt5_path = \"$MT5\"#" config.py
  sed -i "s#\"How2Sign\": \"./data/How2Sign/labels.test\"#\"How2Sign\": \"$PILOT/$ARM/labels.test_pilot\"#" config.py
  sed -i "s#\"How2Sign\": \"./dataset/WLASL/pose_format\"#\"How2Sign\": \"$PILOT/$ARM/{}-pose-rtmpose-192\"#" config.py
  grep -n "How2Sign\|mt5_path" config.py
  (cd "$P012" && sha256sum -c --quiet "$RT_PIN") || die "runtime PKLs changed"
  (cd "$PILOT" && sha256sum -c --quiet PILOT_INPUTS.sha256) || die "pilot inputs changed"
  mkdir -p "$D"
  UNISIGN_DECODE_DIAG=1 deepspeed --include localhost:0 --master_port "$MASTER_PORT" fine_tuning.py $FT_ARGS \
     --finetune "$CKPT" --output_dir "$D" 2>&1 | tee "$D/run.log"
  [ "$(wc -l < "$D/test_tmp_pres.txt")" = "$N" ] || die "$D: expected $N prediction lines"
  [ "$(wc -l < "$D/test_decode_diag.jsonl")" = "$N" ] || die "$D: expected $N diag rows"
  sha256sum "$D"/test_tmp_pres.txt "$D"/test_tmp_refs.txt "$D"/test_decode_diag.jsonl > "$D/SHA256SUMS"
  git checkout -- config.py
}
for A in $ARMS; do
  case "$A" in
    SMOKE) run_arm SMOKE ;;
    U36) [ -s "$OUT/SMOKE/test_tmp_pres.txt" ] || die "run SMOKE first"; run_arm U36
         python -I "$ROOT/scripts/u36_gate.py" "$OUT/U36" "$BASELINE_PRED" "$ROOT" "$OUT/U36_GATE.json" \
           || die "U36 gate FAILED: unchunked predictions are not byte-identical to R100 -- STOP, diagnose before S1/S2/S3" ;;
    S1|S2|S3) python -c "import json,sys; sys.exit(0 if json.load(open('$OUT/U36_GATE.json'))['pass'] else 1)" 2>/dev/null \
                || die "U36 gate missing or failed; S1/S2/S3 refused"
              run_arm "$A" ;;
    *) die "unknown arm $A" ;;
  esac
done
cp "$PILOT/PILOT_INPUTS.sha256" "$PW/PLAN.sha256" "$OUT/"
if [ -s "$OUT/S1/test_tmp_pres.txt" ] && [ -s "$OUT/S2/test_tmp_pres.txt" ] && [ -s "$OUT/S3/test_tmp_pres.txt" ] && [ ! -f "$OUT/bleurt.jsonl" ]; then
  python -I "$ROOT/scripts/bleurt_score.py" "$WT/BLEURT-20" "$OUT" "$ROOT" "$P012/labels.test_p012_128" "$OUT/bleurt.jsonl"
fi
python - "$OUT/environment.json" <<'EOF'
import sys, json, torch, transformers, platform
json.dump({'gpu': torch.cuda.get_device_name(0), 'torch': torch.__version__, 'cuda': torch.version.cuda,
           'transformers': transformers.__version__, 'python': platform.python_version()}, open(sys.argv[1], 'w'), indent=1)
EOF
echo "done: $ARMS -> $OUT   (run.log metrics are chunk-level against full references: ignore them; analyse locally)"
