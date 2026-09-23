# 技术报告：gloss-free landmark → T5 的 1% / 10% How2Sign 可行性实验

日期：2026-09-22 · 作者：Baobao · 分支 `baobao/asl-temporal-ablation-2026-09-06`（实验目录未提交，git 中为 untracked）

本报告只汇总已有 artifact。写报告时**没有**重新训练、**没有**下载数据、**没有**修改任何实验结果或冻结 benchmark。所有数字都来自下文列出的 JSON/日志文件。

---

## A. 目标

测试一个轻量的、基于 landmark 的 ASL → English pipeline 能否学到有用的翻译信号。当前 baseline：

```
How2Sign → MediaPipe/Holistic landmark (T,543,3 → 501 维/帧) → 4 层 Conformer → T5-small → English
```

- 不使用 I3D（`i3d_params = 0`）。
- 上游 repo：`yyouretoast/gloss-free-asl-translation` @ `5b7eb92ff90c4ac5907bc6328edb79c24cec6c77`，**未修改**。本地 clone 为 `/Users/baobaoli/Desktop/gloss-free-asl-translation`，HEAD 已确认是这个 commit，working tree 干净。
- 架构已在上游代码中核对：`src/train.py` 中 `--t5_model` 默认值为 `t5-small`，`input_dim` 由第一个 batch 推出（本实验为 501）；`src/models/translation_model.py` 中 `num_layers: int = 4`。运行时的 `metrics.json` 也记录了 `conformer_blocks = 4`。
- 表示选择：我们之前的轨迹工作用 **RTMPose / COCO-WholeBody**，这个 repo 用 **MediaPipe/Holistic**。为了先复现 repo 原本的设置，本实验直接用 repo 原生的 MediaPipe 表示，**没有**强行写 RTMPose → MediaPipe 的适配器（见 H 节）。

背景（9.19 调研，`docs/daily_report/9.19/gloss-free-asl-translation-audit/`）：上游没有发布训练好的 checkpoint，分类为 “B — PIPELINE WORKS, NO TRAINED CHECKPOINT”。因此这里的 1%/10% 实验是我们自己训练的小规模可行性探针，**不是**对上游模型的复现评测。

## B. 实验配置（预注册，`config.json`，已冻结）

| 项目 | 值 |
|---|---|
| 数据 | 样本 ID / 文本来自 How2Sign 官方 realigned TRAIN metadata；landmark 来自 Kaggle “How2Sign Holistic” 的**第三方** MediaPipe/Holistic 提取（非 How2Sign 官方发布；本地 mirror：`kaggle_input_mirror/how2sign-holistic`） |
| 元数据 | `how2sign_realigned_train.csv`（TAB 分隔，sha256 `67a8f4fb…`），31,165 行 / 31,165 个 unique ID |
| 采样 | 排序后的 eligible pool（31,045）→ `random.Random(20260921).shuffle` → 取前 k 个通过文件校验的样本；k = round(fraction × 31,165) |
| Pool 排除 | 缺少 landmark 文件 118；与冻结参考句文本相同 2；视频重叠 0 |
| holdout | 上游自带的 `split_by_signer`（实际按视频 ID 前缀分组） |
| 模型 | t5-small，Conformer 4 层，d_model 512，heads 4，kernel 31，face 开启，input_dim 501 |
| 参数量 | 67,176,192（encoder 25,287,168 / bridge 263,680 / t5 41,625,344），全部可训练 |
| 训练 | 1 epoch，batch 8，grad-accum 1，lr 1e-4，Adafactor（T5 部分用 0.1× lr），linear 调度，warmup 0.1，max_len 150，max_target_len 30，gradient checkpointing |
| 设备 | CPU（macOS-14.1-arm64），torch 2.10.0，transformers 4.57.6，python 3.12.4，fp32 |
| 相对上游的偏差 | grad-accum 8→1（等效 batch 64→8）；logging 10→1；只 stage 所选子集（symlink）；强制单卡；自定义 metadata 文件名；只增加了测量代码（instrumentation） |

有效的 `TrainingArguments` 已确认（`deviation_verified.ok = True`）：accum=1，logging=1，batch=8。这是 manager 批准的 CPU 可行性运行，所以 **GPU 显存为 N/A**。

预注册规则的修正 A1–A3 都是在**看到任何真实数据之前**做的。A1 的起因：在纯随机噪声 landmark 上做 dry-run 时，原来的 GO 规则也会判 GO（loss 下降了 33%）。所以只看 loss 下降不能证明模型用了 landmark，必须另加 landmark 对照实验。

## C. 1% 可行性实验

来源：`local_run_1pct_REFERENCE/work/`（`DO_NOT_MODIFY.txt` 标明这些是不可变的参考 artifact）。

| 指标 | 值 |
|---|---|
| 全量 realigned train | 31,165 |
| 1% 选中 | 312 |
| holdout 后训练 / 验证 | 275 / 37 |
| Leakage guard | PASS，与 147 条 evaluation set 重叠 0（clip / video / text 都是 0） |
| Subset IDs sha256 | `515d75f4e860b30e698dcafae04a19313cf0e6658a020a8151699a9462613418` |
| Optimizer steps | 35（预期 35；`trainer_state.global_step = 35`） |
| Train loss 首步 / 末步 / 最低 | 11.843 / 7.320 / 6.179（第 27 步） |
| 前 7 步 / 后 7 步均值 | 9.389 / 6.477（−31.0%）；OLS 斜率 −0.0925/步 |
| 验证 loss 训练前 → 后 | 11.663 → 6.152（n=37） |
| grad_norm 非有限值 | 0/35（中位数 8.42） |
| 参数更新 L2 | encoder 9.533 / bridge 0.249 / t5 2.003 |
| samples/sec | 10.28（去掉前 2 步后为 13.48） |
| Wall-clock | 整个脚本 47.6 s（初始化 10.0 s，train loop 26.7 s，eval 10.0 s） |
| GPU 显存 | N/A（CPU 运行） |
| Checkpoint | `run_1pct_1epoch/checkpoints/checkpoint-35`（sha256 前缀 `379af2236fa03972`） |
| 预注册分类 | **GO WITH WEAK / INCONCLUSIVE LANDMARK SIGNAL** |

简单说：训练流程正确，loss 在下降，没有数值不稳定。ZERO_LANDMARKS 比 NORMAL 差（+0.342）；TEMPORAL_SHUFFLE 和 NORMAL 基本分不开（−0.002，p=0.188）。所以这里有早期的 landmark 内容依赖，但**没有**证明模型依赖时间顺序。**这不是一次成功的 ASL 翻译。**

过程说明：1% 的对照实验第一次运行时有两项 sanity check 没通过（`same_heldout_examples_as_manifest`、`NORMAL_reproduces_trainer_eval_loss`），当时分类为 DEBUG FIRST。修正 instrumentation 后重新评估，9/9 都通过。重跑前后三个条件的 eval loss 完全相同，只有 status、计时和新增的复现字段有变化。原文件保留为 `*.pre_fix_bak`。

## D. 10% 扩展实验

来源：`local_run_10pct/work/`

| 指标 | 值 |
|---|---|
| 10% 选中 | 3,117（1% 的 312 条全部包含在里面：同一个种子和打乱顺序，取前 k 条） |
| holdout 后训练 / 验证 | 2,751 / 366 |
| Leakage guard | PASS；8 项 final check 全为 True（没有冻结 clip ID、没有冻结源视频、没有 val/test 的视频或 ID、没有冻结文本、landmark 全在 train 目录下）；重叠 0 |
| Subset IDs sha256 | `149426a50ee31cc9a8291e668c65b35ce43426d14b3160a6ce62d7a04688a0ac` |
| 设备 / epoch | CPU / 1 |
| Optimizer steps | 344（预期 344；`trainer_state.global_step = 344`） |
| Train loss 首步 / 末步 / 最低 | 12.764 / 5.030 / 4.829（第 186 步） |
| 前 69 步 / 后 69 步均值 | 7.231 / 5.409（−25.2%）；OLS 斜率 −0.0063/步 |
| 验证 loss 训练前 → 后 | 12.347 → 5.173（n=366） |
| grad_norm 非有限值 | 0/344（中位数 6.80） |
| 参数更新 L2 | encoder 31.644 / bridge 0.935 / t5 12.733 |
| samples/sec | 12.96（去掉前 2 步后为 13.37） |
| Wall-clock | 整个脚本 269.0 s（初始化 17.5 s，train loop 212.2 s，eval 38.5 s） |
| Checkpoint | `run_10pct_1epoch/checkpoints/checkpoint-344`（sha256 前缀 `c04425b6adc7ebbf`） |
| 预注册分类 | **GO WITH WEAK / INCONCLUSIVE LANDMARK SIGNAL** |

Artifact 标签说明：10% 的运行复用了 1% 的代码包，所以 `RESULTS.md` 里原本有沿用 1% 模板的文字（标题、“1% selected”、“The 10% run has not been started” 等）。这些描述性文字已在 `RESULTS.md` 中更正为 10% 的表述，数字未改动。`metrics.json` / `run_config.json` 里的 `mode = full_1pct_1epoch` 是原始运行记录，**保持原样未修改**（只是沿用的模式名，不代表 1% 运行）。实际数字（3,117 / 344 步 / n=366）以 `subset_manifest.json`、`metrics.json`、`trainer_state.json` 为准，三者一致。

## E. Evaluation set 评测

- Evaluation set：147 条（128 条 frozen how2sign_v2 + 19 条 historical pilot_v1），与 `frozen_denylist.json` 完全对应。其中只有 128 条 how2sign_v2 是 checksum 冻结的 benchmark；19 条 pilot_v1 是历史 pilot 片段，不在 checksum 冻结范围内。
- Landmark：用上游自己的 extractor（`src/data_pipeline.py`，MediaPipe Holistic）直接从 147 条 evaluation set 的本地视频提取，147/147 成功、0 失败（`extraction_manifest.json`）。然后按上游 raw `.npy` 的约定写成 (T,543,3)，读取时用训练时的同一个 loader（`build_frozen_benchmark_landmarks.py`）。
- 解码：greedy，num_beams 1，max_new_tokens 30，batch 8。指标用 sacrebleu（BLEU/chrF，0–100 分）和 jiwer（WER/CER）。

| 指标 | 1% | 10% | Delta |
|---|---|---|---|
| BLEU | 0.036 | 0.062 | +0.026 |
| chrF | 0.121 | 2.532 | +2.411 |
| WER | 1.000 | 1.012 | +0.012 |
| CER | 0.996 | 0.804 | −0.192 |
| eval loss | 6.226 | 5.244 | −0.982 |
| distinct outputs | 4 | 4 | 0 |
| n_predictions / n_scored / n_dataset | 147 / 147 / 147 | 147 / 147 / 147 | — |

147 条全部完成评分，**没有缺失的预测**。

冻结 benchmark（128 条 how2sign_v2）没有被修改：`how2sign_v2/FREEZE_CHECKSUMS.sha256` 的 260 个文件 `shasum -c` 全部 OK；这个清单文件本身的 sha256 = `16c41282b21928e36e4c5481d8c3de48d56794accbb091fde67698dd2963411a`，与 `FREEZE.sha256` 以及两个 subset_manifest 中记录的 freeze 指纹一致。`asl-translator/data/` 在 git 中没有改动。提取结果写在单独的目录 `frozen_benchmark_mediapipe_eval/`。

## F. 定性结果（重要）

**从 1% 到 10%，优化指标变好了，但翻译质量没有实质提升。**

- **1%**：输出基本是空的或退化的。147 条中有 75 条是一串句点，47 条只有空白，24 条是 `.`，1 条是 `..`。
- **10%**：输出塌缩成一个重复模式。147 条中有 132 条是 `So's a a a a a a a a a a a a a`，其余是 `So's a little little.`（10）、`So's a good.`（4）以及一条更长的重复串（1）。
- 两个 checkpoint 的 distinct outputs 都**只有 4 种**。输出基本不随输入变化。
- chrF 上升和 CER 下降，是因为输出从标点变成了固定的英文字母串，和参考句在字符层面碰巧重合得多一点。**不能把它当成翻译改进。** WER 仍然 ≥ 1。

## G. Landmark 对照实验

条件：NORMAL（原始输入）、TEMPORAL_SHUFFLE（每条样本内部打乱帧顺序，长度、mask、label 都不变，seed 20260921）、ZERO_LANDMARKS（所有值置零）。都是 evaluation-only：同一个 checkpoint、同一批 held-out 验证样本、不更新权重。bootstrap 10,000 次，seed 20260921。两次运行 9/9 sanity check 全部 PASS（包括权重在评估前后不变、shuffle 确实是一个置换、NORMAL 能复现 Trainer 算出的 eval loss）。

| | 1%（n=37） | 10%（n=366） |
|---|---|---|
| NORMAL | 6.1395 | 5.1690 |
| TEMPORAL_SHUFFLE | 6.1373（Δ −0.0022；逐样本 −0.0026 [−0.0056, +0.0003]；14/23；p=0.188） | 5.1690（Δ −0.0000；逐样本 −0.0001 [−0.0006, +0.0003]；185/181；p=0.875） |
| ZERO_LANDMARKS | 6.4817（Δ +0.3422；逐样本 +0.3673 [+0.3006, +0.4361]；36/1；p<0.001） | 12.1056（Δ +6.9366；逐样本 +6.7845 [+6.6730, +6.8940]；366/0；p<0.001） |

解读：
- **ZERO gap 在 10% 时大幅增加**（+0.34 → +6.94，366 条全部是 NORMAL 更好）。10% 模型越来越依赖非零的、有结构的 landmark 输入。ZERO 条件下的 loss（12.11）和训练前的验证 loss（12.35）接近。
- **TEMPORAL_SHUFFLE 仍然基本没有影响**：10% 时差值在 1e-4 量级，好坏各占一半。因此**没有证据**表明模型利用了帧顺序或 ASL 的时间结构。
- 局限：每个规模只用了**一个** shuffle seed（20260921）做一次打乱，没有多 seed 重复。
- 措辞要谨慎：这可能说明模型在识别或依赖“有结构的输入”（比如输入的整体分布或统计特征），**还没有学到时间上的手语语义**。ZERO_LANDMARKS 是分布外输入，打败它的证据强度本来就比打败 TEMPORAL_SHUFFLE 弱。**ZERO gap 不能证明模型理解了手语。**

## H. 表示对齐（Representation alignment）

- 我们已有的轨迹工作：**RTMPose / COCO-WholeBody**（133 点，2D 像素坐标，脸 68 点，带置信度）。
- gloss-free repo：**MediaPipe/Holistic**（pose 33 + 左右手各 21 + 脸从 468 点中选 92 点；3D 归一化坐标；每帧 501 维；检测不到的点补 0）。
- 两者**不能直接互换**（9.19 调研：`mediapipe_vs_rtmpose_comparison.json`）。本 baseline 实验**没有**引入 RTMPose → MediaPipe 适配器。表示对齐是一个单独的后续问题。
- 还要注意：训练用的 landmark 是第三方 Kaggle 提取的（MediaPipe 版本和配置没有文档，属于 `known_unverifiable`），evaluation set 的 landmark 是我们用上游 extractor 自己提取的。两者来自不同的 MediaPipe 提取/配置，**无法完全核实是否一致**，可能存在提取差异。不过 evaluation set eval loss（6.23 / 5.24）和同分布验证 loss（6.14 / 5.17）接近，目前没有看到明显的分布偏移。

## I. 联系作者

- Manager 要求联系 gloss-free-asl-translation 的作者，询问是否有 checkpoint、部分训练的 checkpoint 或 Kaggle 训练输出。
- **已通过 GitHub 查询核实提交**：`yyouretoast/gloss-free-asl-translation` Issue **#1**，标题 “Request for preliminary How2Sign checkpoint / training output for research evaluation”。作者账号 `baobaoli03`（与本机 `gh` 登录账号一致），创建于 2026-09-23T02:06:50Z（即 2026-09-22 21:06 CDT）。状态 OPEN，**0 条评论 / 作者尚未回复**。
- Issue 的内容就是上面三项请求，并表示愿意在我们的冻结 benchmark 上评测、分享结果。
- **没有做邮件联系**（没有使用任何经过核实的公开邮箱）。

## J. 当前结论

**跑通了的：** 数据 pipeline；MediaPipe 表示的加载；Conformer/T5 训练；从 1% 扩到 10%；稳定的优化（所有 loss 有限，grad_norm 没有非有限值）；147 条 evaluation set 评测（147/147）；landmark 依赖对照；泄漏防护（重叠 0）。

**还没跑通的：** 有意义的 ASL → English 翻译；时间顺序依赖；多样化的输出。

**决定：** 原定的 1% → 10% 可行性检查**已经完成**。**目前不建议直接扩到 100% 或全量训练**：数据增加 10 倍，loss 变好了，但输出仍然塌缩，而且没有时间顺序依赖。在没有进一步诊断之前，全量训练的理由不充分。

## K. 与研究方向的关系

这里有用的发现不只是“BLEU 很低”。当前受控实验的结果是：

> **Landmark 依赖出现了，但没有测出时间顺序依赖。**

这和更大的研究问题直接相关：从轻量的姿态轨迹中能恢复多少 ASL 语义？需要什么样的时间表示？目前这只是一个**早期的研究发现 / 诊断结果**，还不是论文贡献。它只基于一个架构、各 1 epoch、一次 shuffle 抽样。

## L. 建议的下一步（等 manager 决定）

扩展实验已经完成。以下是可选的后续方向，**不会自动开始任何一项**：

1. **诊断训练不足**：用现有的 10% 设置跑几个 epoch，看输出塌缩和 shuffle 无影响是否会改变。
2. **诊断解码塌缩**：换其他解码方式，如 beam search、`no_repeat_ngram_size`、repetition penalty、sampling。只做评估，不重新训练。
3. **查明 temporal shuffle 为什么没有影响**：例如检查 150 帧的 stride 下采样（约 40% 的样本超过 max_len）、Conformer 的输出在 bridge 或 T5 cross-attention 中是否被当成“无序集合”使用，以及多次 shuffle 抽样的结果。
4. **表示研究**：RTMPose 和 MediaPipe 的对齐问题。
5. **诊断之后**再决定是否值得做全量训练，或者转向新的时间表示方案。

## M. Artifact 位置

根目录：`asl-translator/evaluation/experiments/landmark_t5_1pct/`

| 内容 | 路径 |
|---|---|
| 预注册配置 / README / 冻结 | `config.json`、`README.md`、`PACKAGE_FREEZE*.sha256` |
| Deny-list | `frozen_denylist.json`（sha256 `428d6e8b…`） |
| 1% subset / guard | `local_run_1pct_REFERENCE/work/subset_manifest.json`、`holdout_split.json` |
| 1% 训练 / 对照 | `local_run_1pct_REFERENCE/work/run_1pct_1epoch/{metrics,control_eval,control_predictions,trainer_state,run_config}.json`、`step_metrics.jsonl`、`RESULTS.md`、`loss_curve.png` |
| 10% subset / guard | `local_run_10pct/work/subset_manifest.json`、`holdout_split.json` |
| 10% 训练 / 对照 | `local_run_10pct/work/run_10pct_1epoch/{metrics,control_eval,control_predictions,trainer_state,run_config}.json`、`step_metrics.jsonl`、`RESULTS.md`、`loss_curve.png` |
| Evaluation set 评测 | `frozen_benchmark_mediapipe_eval/eval_{1pct,10pct}_checkpoint/{metrics,predictions}.json`、`extraction_manifest.json`、`eval_on_frozen_benchmark.py`、`build_frozen_benchmark_landmarks.py` |
| Evaluation set 源 | `asl-translator/data/public_benchmarks/how2sign_v2/`（128 条冻结，`FREEZE.sha256`）、`asl-translator/data/public_benchmarks/how2sign/` |
| Repo 调研 | `docs/daily_report/9.19/gloss-free-asl-translation-audit/` |
| 作者 Issue | https://github.com/yyouretoast/gloss-free-asl-translation/issues/1 |
