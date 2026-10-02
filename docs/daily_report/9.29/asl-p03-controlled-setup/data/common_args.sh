# shared data arguments for every P0.3 arm (identical to results/p02_padfix_10pct_e30 run_config argv)
COMMON="--stage-dir /Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/landmark_t5_1pct/local_run_10pct/work/stage \
 --metadata /Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/landmark_t5_1pct/local_run_10pct/work/subset_metadata.csv \
 --split-json /Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/landmark_t5_1pct/local_run_10pct/work/holdout_split.json \
 --raw-dir /Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/landmark_t5_1pct/local_run_10pct/raw_download \
 --frozen-landmarks /Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/landmark_t5_1pct/frozen_benchmark_mediapipe_eval/landmarks \
 --frozen-metadata /Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/landmark_t5_1pct/frozen_benchmark_mediapipe_eval/frozen_benchmark_metadata.csv \
 --frozen-denylist /Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/landmark_t5_1pct/frozen_denylist.json \
 --how2sign-v2-manifest /Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c/asl-translator/data/public_benchmarks/how2sign_v2/manifest.csv \
 --epochs 30 --patience 10"
