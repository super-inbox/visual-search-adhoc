# 1% vs 10% 结果对照表

日期：2026-09-22 · 所有数字直接取自下列 artifact（路径相对 `asl-translator/evaluation/experiments/landmark_t5_1pct/`）：
`local_run_1pct_REFERENCE/work/run_1pct_1epoch/{metrics,control_eval}.json`、`local_run_10pct/work/run_10pct_1epoch/{metrics,control_eval}.json`、`*/work/subset_manifest.json`、`frozen_benchmark_mediapipe_eval/eval_{1pct,10pct}_checkpoint/{metrics,predictions}.json`。

Pipeline：How2Sign → MediaPipe/Holistic landmark（501 维；样本取自官方 realigned TRAIN metadata，landmark 为第三方 Kaggle 提取）→ 4 层 Conformer → T5-small → English；无 I3D；CPU；1 epoch；batch 8，grad-accum 1。

## A. 数据与训练

| 指标 | 1% | 10% | Delta |
|---|---|---|---|
| How2Sign 官方 realigned TRAIN metadata（unique ID） | 31,165 | 31,165 | — |
| 选中样本数 | 312 | 3,117 | +2,805 |
| holdout 后训练 / 验证 | 275 / 37 | 2,751 / 366 | — |
| Leakage guard / 与 147 条 evaluation set 重叠 | PASS / 0 | PASS / 0 | — |
| 设备 / epoch | CPU / 1 | CPU / 1 | — |
| Optimizer steps（实际 / 预期） | 35 / 35 | 344 / 344 | — |
| 初始 train loss | 11.843 | 12.764 | — |
| 最终 train loss | 7.320 | 5.030 | −2.290 |
| 最低 train loss（step） | 6.179（27） | 4.829（186） | −1.350 |
| 前 k / 后 k 步均值（k） | 9.389 / 6.477（7），−31.0% | 7.231 / 5.409（69），−25.2% | — |
| 验证 loss 训练前 → 后 | 11.663 → 6.152 | 12.347 → 5.173 | 后：−0.979 |
| 非有限 grad_norm 步数 | 0 / 35 | 0 / 344 | — |
| samples/sec（train loop） | 10.28 | 12.96 | — |
| Wall-clock：整个脚本 / train loop | 47.6 s / 26.7 s | 269.0 s / 212.2 s | — |
| 参数量 | 67,176,192 | 67,176,192 | 0 |
| GPU 显存 | N/A（CPU 运行） | N/A（CPU 运行） | — |

## B. Evaluation set（147 条 = 128 条 frozen how2sign_v2 + 19 条 historical pilot_v1；greedy，max_new_tokens 30）

只有 128 条 how2sign_v2 是 checksum 冻结的 benchmark。

| 指标 | 1% | 10% | Delta |
|---|---|---|---|
| BLEU（sacrebleu，0–100） | 0.036 | 0.062 | +0.026 |
| chrF（sacrebleu，0–100） | 0.121 | 2.532 | +2.411 |
| WER | 1.000 | 1.012 | +0.012 |
| CER | 0.996 | 0.804 | −0.192 |
| eval loss | 6.226 | 5.244 | −0.982 |
| 不同输出数（distinct hypotheses） | 4 | 4 | 0 |
| 已评分 / 数据集 | 147 / 147 | 147 / 147 | — |
| 缺失的预测 | 0 | 0 | — |

输出分布（来自 `predictions.json`）：

| 1% 输出 | 次数 | 10% 输出 | 次数 |
|---|---|---|---|
| `.............................` | 75 | `So's a a a a a a a a a a a a a` | 132 |
| `" "`（空白） | 47 | `So's a little little.` | 10 |
| `.` | 24 | `So's a good.` | 4 |
| `..` | 1 | `So's a little little a little a little …` | 1 |

**注意**：chrF 上升和 CER 下降来自 10% 的输出从标点/空白变成了固定的英文重复串，**不是翻译质量的提升**。

## C. Landmark 对照（evaluation-only，同一 checkpoint，同一 held-out 验证集）

| 指标 | 1%（n=37） | 10%（n=366） |
|---|---|---|
| NORMAL eval loss | 6.1395 | 5.1690 |
| TEMPORAL_SHUFFLE eval loss | 6.1373 | 5.1690 |
| ZERO_LANDMARKS eval loss | 6.4817 | 12.1056 |
| delta_shuffle（shuffle − normal） | −0.0022 | −0.0000 |
| ↳ 逐样本均值 [bootstrap 95% CI] | −0.0026 [−0.0056, +0.0003] | −0.0001 [−0.0006, +0.0003] |
| ↳ NORMAL 更好 / shuffle 更好 / 平 | 14 / 23 / 0 | 185 / 181 / 0 |
| ↳ sign test p | 0.188 | 0.875 |
| ↳ 判定 | indistinguishable | indistinguishable |
| delta_zero（zero − normal） | +0.3422 | +6.9366 |
| ↳ 逐样本均值 [bootstrap 95% CI] | +0.3673 [+0.3006, +0.4361] | +6.7845 [+6.6730, +6.8940] |
| ↳ NORMAL 更好 / zero 更好 / 平 | 36 / 1 / 0 | 366 / 0 / 0 |
| ↳ sign test p | 0.000 | 0.000 |
| ↳ 判定 | beaten_conclusive | beaten_conclusive |
| Sanity checks | 9/9 PASS | 9/9 PASS |
| 预注册分类 | GO WITH WEAK / INCONCLUSIVE LANDMARK SIGNAL | GO WITH WEAK / INCONCLUSIVE LANDMARK SIGNAL |

解读：landmark 内容依赖明显增强（ZERO gap 从 +0.34 增加到 +6.94），但 TEMPORAL_SHUFFLE 在两个规模下都没有影响，**目前没有观察到时间顺序依赖**。每个规模只有一个 shuffle seed。1% 对照的 9/9 是修正 instrumentation 后重新评估的结果（首次运行有 2 项 check 未通过，三个条件的 eval loss 前后完全相同，详见 TECHNICAL_REPORT C 节）。
