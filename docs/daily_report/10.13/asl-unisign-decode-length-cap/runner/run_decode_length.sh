#!/usr/bin/env bash
# Uni-Sign decode-length-cap follow-up: A_official only, R100 / R150 / R256 (max_new_tokens 100 / 150 / 256).
# Everything else is held at the P0-12 T4/fp16 settings: pinned Uni-Sign eed438bc, same checkpoint, same 128 A_official
# pose PKLs + labels.test_p012_128, Tesla T4, --dtype fp16, batch 8, num_beams=4 (upstream literal), seed 42 (default),
# max_length 256 (default), num_workers 8 (default), deepspeed single GPU.
#
# The only code change is patch/fine_tuning_decode_length.patch, applied in a SEPARATE git worktree. The existing VM
# clone ($UNISIGN, used for P0-12) is never modified.
#
# Usage (see ../README.md):
#   RUNS=R100       bash run_decode_length.sh     # reproducibility gate: always first
#   RUNS="R150 R256" bash run_decode_length.sh    # refused unless the R100 gate verdict allows it
set -euo pipefail
: "${UNISIGN:?existing VM Uni-Sign clone at eed438bc (read-only here)}"
: "${P012:?the existing fp16-converted P0-12 runtime tree, /tmp/p012_fp16 (labels.test_p012_128 + A_official/test-pose-rtmpose-192/)}"
: "${CKPT:?path to how2sign_pose_only_slt.pth}"; : "${MT5:?path to google/mt5-base}"
: "${BASELINE_PRED:?committed docs/daily_report/10.13/asl-p0-12-full128-fp16/predictions/A_official.txt}"
RUNS="${RUNS:-R100}"
# Input lineage: committed prepared_inputs (source, runner/source_prepared_inputs_A_official.sha256)
#   -> one-off float16 conversion of the floating pose arrays into /tmp/p012_fp16 (done for P0-12, NOT redone here)
#   -> T4 runtime inputs, checked against RUNTIME_MANIFEST (sha256 snapshot of the 128 /tmp/p012_fp16 A_official PKLs).
# The converted PKLs cannot match the source checksums byte-for-byte, so the pose PKLs are only checked against
# RUNTIME_MANIFEST. labels.test_p012_128 was not converted and is still checked against the source checksum.
RUNTIME_MANIFEST="${RUNTIME_MANIFEST:-$(cd "$(dirname "$0")/.." && pwd)/A_official_fp16_runtime.sha256}"
SOURCE_PREPARED_INPUTS="${SOURCE_PREPARED_INPUTS:-}"  # optional: committed 10.06/.../prepared_inputs dir (provenance only)
OLD_RUNNER="${OLD_RUNNER:-/tmp/run_p012_full128_fp16.sh}"
DL_WORK="${DL_WORK:-$HOME/unisign_decode_length}"
MASTER_PORT="${MASTER_PORT:-29511}"
# Flags of the P0-12 run_cond (10.06/.../run_p012_gpu.sh) + --dtype fp16. Must equal the old T4 runner's flags (step 0c).
FT_ARGS="${FT_ARGS:---batch-size 8 --gradient-accumulation-steps 1 --epochs 20 --opt AdamW --lr 3e-4 --dataset How2Sign --task SLT --eval --dtype fp16}"

HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
PIN=eed438bcb49e30405cd6ccdfcccca330c134e830
CKPT_SHA=1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d
UPSTREAM_FT_SHA=3249a0aa642258779b1a70ace78c74c1fcc58b3ab7470397ea1890702c9528af
PATCHED_FT_SHA=f13e168967c974fc690a1a8393326b5aeceb1e3aaba91521953687ee7fed99bc
BASELINE_SHA=d865008bc0a16ba0fb3bceb6f78f5a7153febe1d69ba756cc83f918d57300e4a
OLD_RUNNER_SHA=7647464809806cde56a27caa882b4f90e661d22160ba798503ae9f91b0dd4426
WT="$DL_WORK/Uni-Sign-dl"; OUT="$DL_WORK/out"
mkdir -p "$DL_WORK" "$OUT"
die () { echo "STOP: $*" >&2; exit 1; }

# ---------------- 0. preconditions (all hard) ----------------
echo "$CKPT_SHA  $CKPT" | sha256sum -c - || die "checkpoint sha256"
echo "$BASELINE_SHA  $BASELINE_PRED" | sha256sum -c - || die "committed A_official.txt changed or wrong file"
GPU="$(python -c "import torch; assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0))")"
case "$GPU" in *T4*) ;; *) die "GPU is '$GPU', expected Tesla T4";; esac
# 0a. existing clone is the pinned, unpatched upstream
[ "$(git -C "$UNISIGN" rev-parse HEAD)" = "$PIN" ] || die "$UNISIGN HEAD != $PIN"
git -C "$UNISIGN" diff --quiet -- fine_tuning.py models.py utils.py datasets.py || die "$UNISIGN has local code changes"
echo "$UPSTREAM_FT_SHA  $UNISIGN/fine_tuning.py" | sha256sum -c - || die "upstream fine_tuning.py sha256"
# 0b. inputs. Source checksums = provenance only; the runtime fp16 tree is checked against RUNTIME_MANIFEST.
SRC_SUMS="$HERE/source_prepared_inputs_A_official.sha256"
RT_SUMS="$DL_WORK/runtime_inputs_A_official.normalized.sha256"   # RUNTIME_MANIFEST with paths made relative to $P012
RT_PIN="$OUT/RUNTIME_INPUTS_A_official.sha256"                    # pinned at the first preflight; R100/R150/R256 share it
if [ -n "$SOURCE_PREPARED_INPUTS" ]; then
  (cd "$SOURCE_PREPARED_INPUTS" && sha256sum -c --quiet "$SRC_SUMS") || die "source prepared_inputs differ from committed checksums"
  echo "source prepared_inputs: OK (provenance)"
fi
[ -f "$RUNTIME_MANIFEST" ] || die "runtime manifest $RUNTIME_MANIFEST not found"
# shape check: exactly the 128 A_official PKLs of the source manifest, nothing else; paths normalised to $P012-relative
python -I - "$RUNTIME_MANIFEST" "$P012" "$SRC_SUMS" "$RT_SUMS" <<'EOF' || die "runtime manifest does not describe the 128 A_official PKLs"
import sys, os, re
man, root, src, out = sys.argv[1:]; root = os.path.realpath(root)
want = {l.split(None, 1)[1].strip() for l in open(src) if l.strip() and l.split(None, 1)[1].strip().endswith('.pkl')}
src_hash = {l.split(None, 1)[1].strip(): l.split()[0] for l in open(src) if l.strip()}
rows = []
for l in open(man):
    if not l.strip(): continue
    m = re.fullmatch(r'([0-9a-f]{64}) [ *](.+)', l.rstrip('\n'))
    assert m, f'bad line: {l!r}'
    h, p = m.groups()
    if os.path.isabs(p):
        p = os.path.realpath(p); assert p.startswith(root + '/'), f'{p} is outside {root}'; p = p[len(root) + 1:]
    p = os.path.normpath(p)
    if '/' not in p: p = 'A_official/test-pose-rtmpose-192/' + p   # manifest written from inside the pose dir
    rows.append((h, p))
got = [p for _, p in rows]
assert len(got) == len(set(got)), 'duplicate paths'
assert set(got) == want and len(want) == 128, f'{len(set(got) - want)} unexpected, {len(want - set(got))} missing (want 128)'
same = sum(src_hash[p] == h for h, p in rows)
print(f'runtime manifest: 128 A_official PKLs; {same}/128 byte-identical to source (expected 0 after fp16 conversion)')
with open(out, 'w') as f:
    for h, p in sorted(rows, key=lambda r: r[1]): f.write(f'{h}  {p}\n')
EOF
if [ -f "$RT_PIN" ]; then cmp -s "$RT_SUMS" "$RT_PIN" || die "runtime manifest changed since it was pinned in $RT_PIN"
else cp "$RT_SUMS" "$RT_PIN"; echo "pinned runtime input manifest -> $RT_PIN"; fi
verify_inputs () {
  (cd "$P012" && sha256sum -c --quiet "$RT_PIN") || die "$P012 A_official PKLs differ from the runtime fp16 manifest"
  (cd "$P012" && grep '  labels\.test_p012_128$' "$SRC_SUMS" | sha256sum -c --quiet -) || die "labels.test_p012_128 differs"
  echo "runtime inputs: 128 fp16 A_official PKLs + labels OK ($P012)"
}
verify_inputs
# 0c. old T4 runner provenance: print its fine_tuning invocation next to ours; must match except --output_dir
if [ -f "$OLD_RUNNER" ]; then
  echo "$OLD_RUNNER_SHA  $OLD_RUNNER" | sha256sum -c - || die "old runner sha256"
  echo "---- old runner: fine_tuning / config lines ----"; grep -nE "fine_tuning\.py|--[a-z_-]+|config\.py|sed " "$OLD_RUNNER" || true
else
  echo "WARNING: $OLD_RUNNER not found; flag equality with P0-12 is checked only by the R100 gate"
fi
echo "---- this runner: deepspeed --include localhost:0 --master_port $MASTER_PORT fine_tuning.py $FT_ARGS --finetune \$CKPT --output_dir <run>"
[ "${CONFIRM_FLAGS_MATCH:-0}" = 1 ] || die "compare the two invocations above; re-run with CONFIRM_FLAGS_MATCH=1 (or set FT_ARGS to the old runner's flags)"

# ---------------- 1. isolated patched worktree ----------------
if [ ! -d "$WT" ]; then
  git -C "$UNISIGN" worktree add --detach "$WT" "$PIN"
  git -C "$WT" apply --check "$ROOT/patch/fine_tuning_decode_length.patch"
  git -C "$WT" apply "$ROOT/patch/fine_tuning_decode_length.patch"
  [ -e "$UNISIGN/BLEURT-20" ] && ln -s "$UNISIGN/BLEURT-20" "$WT/BLEURT-20"
fi
echo "$PATCHED_FT_SHA  $WT/fine_tuning.py" | sha256sum -c - || die "patched fine_tuning.py sha256"
# worktree cleanliness: the only tracked change is fine_tuning.py at PATCHED_FT_SHA; the only untracked entries are the
# BLEURT-20 eval assets and __pycache__/.pyc runtime artifacts. Anything else (tracked or untracked) is a hard stop.
git -C "$WT" status --porcelain=v1 -z --untracked-files=all > "$DL_WORK/worktree_status.z"
python -I - "$WT" "$PATCHED_FT_SHA" "$DL_WORK/worktree_status.z" <<'EOF' || die "worktree is not clean (see above)"
import sys, os, hashlib
wt, patched_sha, status = sys.argv[1:]
ents = open(status, 'rb').read().decode().split('\0')
runtime = lambda p: '__pycache__' in p.split('/') or p.endswith('.pyc')
asset = lambda p: p in ('BLEURT-20', 'BLEURT-20.zip') or p.startswith('BLEURT-20/')
bad, i = [], 0
while i < len(ents):
    e = ents[i]; i += 1
    if not e: continue
    xy, p = e[:2], e[3:]
    if xy[0] in 'RC': i += 1                       # -z rename/copy: source path follows as its own field
    if runtime(p): continue
    if xy == '??':
        if not asset(p): bad.append(f'untracked: {p}')
    elif p == 'fine_tuning.py' and set(xy) <= {'M', ' '}:
        h = hashlib.sha256(open(os.path.join(wt, p), 'rb').read()).hexdigest()
        if h != patched_sha: bad.append(f'fine_tuning.py sha256 {h} != patched {patched_sha}')
    else:
        bad.append(f'tracked [{xy}]: {p}')
for b in bad: print(f'unexpected worktree change: {b}', file=sys.stderr)
sys.exit(1 if bad else 0)
EOF
[ -e "$WT/BLEURT-20" ] || die "BLEURT-20 missing (unmodified How2Sign --eval imports BLEURT before writing predictions)"
# README-sanctioned config.py edits, same as P0-12 run_cond (worktree-local)
cd "$WT"
git checkout -- config.py
sed -i "s#^mt5_path = .*#mt5_path = \"$MT5\"#" config.py
sed -i "s#\"How2Sign\": \"./data/How2Sign/labels.test\"#\"How2Sign\": \"$P012/labels.test_p012_128\"#" config.py
sed -i "s#\"How2Sign\": \"./dataset/WLASL/pose_format\"#\"How2Sign\": \"$P012/A_official/{}-pose-rtmpose-192\"#" config.py
grep -n "How2Sign\|mt5_path" config.py

# environment record
python - "$DL_WORK/environment.json" <<'EOF'
import sys, json, torch, transformers, platform
try: import deepspeed; ds = deepspeed.__version__
except Exception as e: ds = repr(e)
json.dump({'gpu': torch.cuda.get_device_name(0), 'torch': torch.__version__, 'cuda': torch.version.cuda,
           'cudnn': torch.backends.cudnn.version(), 'transformers': transformers.__version__, 'deepspeed': ds,
           'python': platform.python_version()}, open(sys.argv[1], 'w'), indent=1)
EOF
cat "$DL_WORK/environment.json"

# ---------------- 2. runs ----------------
run_one () {  # $1 = max_new_tokens
  local N="$1" D="$OUT/A_official_mnt$1"
  [ -e "$D/test_tmp_pres.txt" ] && die "$D already has predictions; move it away before re-running"
  verify_inputs
  mkdir -p "$D"
  cp "$RT_PIN" "$D/RUNTIME_INPUTS_A_official.sha256"
  UNISIGN_MAX_NEW_TOKENS="$N" UNISIGN_DECODE_DIAG=1 \
  deepspeed --include localhost:0 --master_port "$MASTER_PORT" fine_tuning.py $FT_ARGS \
     --finetune "$CKPT" --output_dir "$D" 2>&1 | tee "$D/run.log"
  [ "$(wc -l < "$D/test_tmp_pres.txt")" = 128 ] || die "$D: expected 128 prediction lines"
  [ "$(wc -l < "$D/test_decode_diag.jsonl")" = 128 ] || die "$D: expected 128 diag rows"
  sha256sum "$D"/test_tmp_pres.txt "$D"/test_tmp_refs.txt "$D"/test_decode_diag.jsonl > "$D/SHA256SUMS"
}
GATE="$OUT/A_official_mnt100/R100_GATE.json"
for R in $RUNS; do
  case "$R" in
    R100) run_one 100
          python "$ROOT/scripts/r100_gate.py" --baseline "$BASELINE_PRED" --run "$OUT/A_official_mnt100" \
                 --unisign "$WT" --out "$GATE" || die "R100 gate: NOT reproduced -- diagnose before R150/R256 (see $GATE)";;
    R150|R256)
          python -c "import json,sys; sys.exit(0 if json.load(open('$GATE'))['proceed'] else 1)" 2>/dev/null \
             || die "R100 gate missing or failed ($GATE); run RUNS=R100 first"
          run_one "${R#R}";;
    *) die "unknown run $R";;
  esac
done
git checkout -- config.py
echo "done: $RUNS -> $OUT"
