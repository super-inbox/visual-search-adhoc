#!/bin/bash
# P0.3 driver, continuation of run_p03_full.sh (replaced at 19:24 while Arm B step ~400 was training, only so
# that the gate does not evaluate the same checkpoint twice when best == final or best == epoch 5).
# Training commands are byte-identical to the setup report §9; the Arm B process started by run_p03_full.sh
# is waited on, not restarted. The gate harness is unchanged; only its --epochs list is de-duplicated.
set -u
cd ~/Desktop/gloss-free-asl-translation && export HF_HUB_OFFLINE=1
B_PID=$1
L=results/p03_controlled/driver.log
st() { echo "[$(date '+%F %T')] $*" >> $L; }
st "continuation driver: waiting for arm B pid $B_PID"
while kill -0 $B_PID 2>/dev/null; do sleep 30; done
check_run() {  # a run is OK if summary.json exists, no non-finite stop, and no traceback in its log
  [ -f "$1/summary.json" ] || return 1
  grep -q '"stop_reason": "non-finite' "$1/summary.json" && return 1
  grep -q "Traceback" "$2" && return 1
  return 0
}
check_run results/p03_controlled/armB_hands_upper162 results/p03_controlled/armB_hands_upper162.log \
  || { st "FAIL arm B (no summary / non-finite / traceback)"; exit 1; }
st "DONE arm B; START arm C"
bash -c 'source results/p03_controlled/common_args.sh && .venv/bin/python scripts/train_p03.py $COMMON \
  --arm C --aux-weight 1.0 --aux-temperature 0.07 --output-dir results/p03_controlled/armC_textalign_w1' > results/p03_controlled/armC_textalign_w1.log 2>&1 \
  || { st "FAIL arm C rc=$?"; exit 1; }
check_run results/p03_controlled/armC_textalign_w1 results/p03_controlled/armC_textalign_w1.log \
  || { st "FAIL arm C (no summary / non-finite / traceback)"; exit 1; }
st "DONE arm C; START gate"
dedup() {  # prints the de-duplicated subset of "5 best final" for a run dir (first role wins)
  .venv/bin/python - "$1" <<'PY'
import json, sys
from pathlib import Path
d = Path(sys.argv[1])
logs = [json.loads(x) for x in open(d / "epoch_log.jsonl")]
best = next(r["epoch"] for r in logs if r["checkpoint"] == json.load(open(d / "summary.json"))["best_checkpoint"])
ep = {"5": 5, "best": best, "final": max(r["epoch"] for r in logs)}
seen, keep = set(), []
for role in ("5", "best", "final"):
    if ep[role] not in seen:
        seen.add(ep[role]); keep.append(role)
print(" ".join(keep))
PY
}
for r in "results/p02_padfix_10pct_e30 armA_padfix" "results/p03_controlled/armB_hands_upper162 armB" \
         "results/p03_controlled/armC_textalign_w1 armC"; do set -- $r
  EPS=$(dedup $1)
  st "START gate $2 --epochs $EPS"
  .venv/bin/python scripts/eval_p03_representations.py --run-dir $1 --name $2 --epochs $EPS \
    > results/p03_controlled/gate_$2.log 2>&1 || { st "FAIL gate $2 rc=$?"; exit 1; }
  st "DONE gate $2"
done
st "START untrained-init references"
.venv/bin/python scripts/prepare_p03_init_states.py > results/p03_controlled/init_states.log 2>&1 \
  || { st "FAIL init prep"; exit 1; }
for a in A B; do
  .venv/bin/python scripts/eval_p03_representations.py --run-dir results/p03_controlled/init_states/arm${a}_init \
    --name arm${a}_init --epochs 0 > results/p03_controlled/gate_arm${a}_init.log 2>&1 || { st "FAIL gate arm${a}_init"; exit 1; }
  st "DONE gate arm${a}_init"
done
st "START arm C alignment trajectory"
.venv/bin/python scripts/analyse_p03_armC_alignment.py > results/p03_controlled/armC_alignment.log 2>&1 \
  || { st "FAIL armC alignment"; exit 1; }
st "ALL DONE"
