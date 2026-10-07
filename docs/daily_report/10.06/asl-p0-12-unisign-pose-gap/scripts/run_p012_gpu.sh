#!/usr/bin/env bash
# P0-12 GPU runbook — controlled pose-condition inference through the UNMODIFIED official Uni-Sign eval path.
# STATUS: PREPARED, NOT RUN. The audit machine (Apple M3 Pro) has no CUDA GPU; official fine_tuning.py hardcodes .cuda()
# and a deepspeed engine. Run this on a single-CUDA-GPU Linux box.
#
# Every condition uses: same checkpoint (sha256 below), same 128 clip IDs + references (labels.test_p012_128, a subset
# of the official labels.test), same official fine_tuning.py --eval, batch 8, bf16, num_beams=4, max_new_tokens=100,
# seed 42, same scorer (score_conditions.py -> official SLRT_metrics.sableu). Main arms change only the pose
# directory; V4 arms (step 3b) change only batch size / workers / seed with the pose directory fixed.
# dtype is bf16 everywhere (official --dtype allows only fp16/bf16; our historical run was also bf16).
# Estimated 1-2 GPU-hours for all 8 x 128-clip runs (estimate, not measured).
#
# Inputs (produced on the audit machine by make_condition_dirs.py; copy the whole $P012 tree to the GPU box):
#   $P012/labels.test_p012_128, $P012/labels.test_p012_smoke3
#   $P012/<COND>/test-pose-rtmpose-192/<clip>.pkl  for COND in A_official B_ours_5p39 B_aspect C_ours_on_official_crop
set -euo pipefail
: "${P012:?prepared condition root}"; : "${CKPT:?path to how2sign_pose_only_slt.pth}"; : "${MT5:?path to google/mt5-base}"
: "${MANIFEST:?how2sign_v2/manifest.csv}"; : "${OURS_JSONL:?docs/daily_report/9.2/asl-baselines/results/unisign_predictions.jsonl}"
TOOLS="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-$PWD/p012_work}"; mkdir -p "$WORK"
CONDS="${CONDS:-A_official B_ours_5p39 B_aspect C_ours_on_official_crop}"

# 0. preconditions
echo "1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d  $CKPT" | sha256sum -c -
python -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('GPU:', torch.cuda.get_device_name(0), 'torch', torch.__version__, 'cuda', torch.version.cuda)"

# 1. official code at the pinned commit
[ -d "$WORK/Uni-Sign" ] || git clone https://github.com/ZechengLi19/Uni-Sign "$WORK/Uni-Sign"
cd "$WORK/Uni-Sign" && git checkout eed438bcb49e30405cd6ccdfcccca330c134e830
# README-sanctioned local config edits only (config.py is restored before every run)
pip install rouge
# The unmodified How2Sign --eval imports BLEURT *before* it writes test_tmp_pres.txt (fine_tuning.py:292-322).
pip install git+https://github.com/google-research/bleurt.git
[ -d BLEURT-20 ] || { wget -q https://storage.googleapis.com/bleurt-oss-21/BLEURT-20.zip && unzip -q BLEURT-20.zip; }

run_cond () {  # $1 = condition, $2 = labels file name, $3 = tag, $4... = extra fine_tuning.py args (V4 arms)
  local COND="$1" LABELS="$2" TAG="$3"; shift 3
  git checkout -- config.py
  sed -i "s#^mt5_path = .*#mt5_path = \"$MT5\"#" config.py
  sed -i "s#\"How2Sign\": \"./data/How2Sign/labels.test\"#\"How2Sign\": \"$P012/$LABELS\"#" config.py
  sed -i "s#\"How2Sign\": \"./dataset/WLASL/pose_format\"#\"How2Sign\": \"$P012/$COND/{}-pose-rtmpose-192\"#" config.py
  grep -n "How2Sign\|mt5_path" config.py
  deepspeed --include localhost:0 --master_port 29511 fine_tuning.py \
     --batch-size 8 --gradient-accumulation-steps 1 --epochs 20 --opt AdamW --lr 3e-4 \
     --output_dir "out/p012_${COND}_${TAG}" --finetune "$CKPT" --dataset How2Sign --task SLT --eval "$@" 2>&1 | tee "out/p012_${COND}_${TAG}.log"
  git checkout -- config.py
}

# 2. smoke test: 3 clips per condition; confirm test_tmp_pres.txt is written and the scorer runs
mkdir -p out
for C in $CONDS; do run_cond "$C" labels.test_p012_smoke3 smoke3; test -s "out/p012_${C}_smoke3/test_tmp_pres.txt"; done

# 3. full 128 clips per condition
for C in $CONDS; do run_cond "$C" labels.test_p012_128 n128; done

# 3b. V4 runtime arms (pose input fixed; later flags override the defaults above, argparse last-wins)
#   B_bs1_nw0 : our 5.39 input, batch 1, no workers -> closest official-path analogue of the historical CPU run;
#               B_bs1_nw0(GPU) - 5.39(CPU) = device/kernel (+ Dataset vs Dataset_online, logically identical; E0)
#   B n128 - B_bs1_nw0 : batch 8 + 8-worker RNG effect on our input
#   A_bs1_nw0 : same for the official input
#   A seed43/seed44 : run-to-run noise band from the >256-frame random subsample (36 clips)
run_cond B_ours_5p39 labels.test_p012_128 bs1_nw0 --batch-size 1 --num_workers 0
run_cond A_official  labels.test_p012_128 bs1_nw0 --batch-size 1 --num_workers 0
run_cond A_official  labels.test_p012_128 seed43  --seed 43
run_cond A_official  labels.test_p012_128 seed44  --seed 44

# 4. score everything with the identical scorer
ARGS=(); for C in $CONDS; do ARGS+=("${C}=out/p012_${C}_n128/test_tmp_pres.txt"); done
for X in B_ours_5p39_bs1_nw0 A_official_bs1_nw0 A_official_seed43 A_official_seed44; do ARGS+=("${X}=out/p012_${X}/test_tmp_pres.txt"); done
python "$TOOLS/score_conditions.py" "$WORK/Uni-Sign" "$MANIFEST" "$OURS_JSONL" "$WORK/p012_scores.json" "${ARGS[@]}"
# 4b. planned single-variable contrasts with paired bootstrap CIs (V1, V2, V3, V4, noise, total)
python "$TOOLS/contrasts.py" "$WORK/Uni-Sign" "$MANIFEST" "$OURS_JSONL" "$WORK/p012_contrasts.json" "${ARGS[@]}" "SEG=$TOOLS/../data/segment_alignment_128.json"

# 5. OPTIONAL (E0-b, needs the full 8.47 GB how2sign_pose_format.zip.00-.03): full 2,349-clip official test
#    -> expect ≈14.5 if the released checkpoint is the one behind the paper/released predictions.
#    cat how2sign_pose_format.zip.* > how2sign_pose_format.zip && unzip how2sign_pose_format.zip -d $FULL
#    then run_cond with pose_dirs -> $FULL/{}-pose-rtmpose-192 and the original ./data/How2Sign/labels.test
