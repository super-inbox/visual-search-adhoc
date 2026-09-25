# ASL P0 诊断：代码与证据包

本目录配合 [`p0_work_report_2026-09-25.md`](p0_work_report_2026-09-25.md) 使用，收录了 P0.1（tiny-set 过拟合）、P0.2（10% 多 epoch 训练）、padding/mask 修复和输入错配诊断用到的代码、测试、实验配置、指标、epoch 表、逐条预测、日志和样本 ID。

**没有收录模型权重、checkpoint、landmark 或数据集。** 本目录只能复核报告中的数字，不能复现训练过程。

## 目录结构

| 路径 | 内容 |
|---|---|
| `p0_work_report_2026-09-25.md` | 工作报告 |
| `code/` | 本次实验实际使用的代码和测试，取自代码仓库的 commit `7da5734` |
| `code/patches/manual_encoder_padding_fix.patch` | padding 修复的完整 diff（`5b7eb92` → `7da5734`） |
| `evidence/results/<run>/` | 各次运行的配置、指标、epoch 表、逐条预测和逐步日志 |
| `evidence/results/*.log` | 主要运行的完整终端日志 |
| `evidence/experiments/tiny_overfit/` | tiny32 的样本 ID 列表和抽样 manifest |
| `evidence/recompute_metrics.py` | 从已发布的逐条预测复算指标的脚本，只依赖 sacrebleu |
| `MANIFEST.tsv` | 每个发布文件的来源、原件 sha256、发布件 sha256、字节数，以及发布件与原件是否逐字节一致 |

## 来源与对应关系

- **代码** `code/<path>` = 代码仓库 `gloss-free-asl-translation` 在 commit `7da5734ac4f58d76c59c1a66480426b954fcd963` 时的 `<path>`。这些文件是用 `git show 7da5734:<path>` 导出的，内容逐字节一致。
  - ⚠️ 这个 commit **只在作者本机，还没有推送**：推送到 `yyouretoast/gloss-free-asl-translation` 时返回 403，原因是没有写权限。这里的副本是目前在 GitHub 上唯一能看到的版本。
- **结果** `evidence/results/<X>` = 代码仓库本机 `results/<X>`。报告中写的 `results/...` 路径，都可以在本目录的 `evidence/results/...` 下找到，但 checkpoint 等权重文件除外，见下文"未上传"。
- **样本清单** `evidence/experiments/<X>` = 代码仓库工作区的 `experiments/<X>`。其中 ID 列表已包含在 `7da5734` 中；manifest 因为含有本机路径，没有进入代码仓库的提交。

## 发布副本与原件

- 318 个文件中，**307 个与原件逐字节一致**。
- **11 个是去除本机路径后的发布副本**，`MANIFEST.tsv` 中标为 `local-path-redacted`，同时列出了原件和发布件的 sha256。这 11 个文件包括：5 个 `run_config.json`、2 个 `baseline_1epoch/metrics.json`、3 个 `.log`，以及 tiny32 manifest。
- 对这 11 个文件唯一的改动：把本机绝对路径前缀 `/Users/<user>/Desktop/visual-search-adhoc-asl-task-c/` 逐字替换为 `<visual-search-adhoc>/`，没有改动其他任何字节，**所有指标和数值都没有改变**。
- 这些路径指向本仓库 `asl-translator/evaluation/experiments/landmark_t5_1pct/...` 下的数据目录，包括 stage、`holdout_split.json`、metadata、frozen landmark 等。这些数据目录在作者本机上是**未跟踪文件**，不在 GitHub 上。
- 复核方法：对原件做同样的前缀替换后计算 sha256，结果应等于 `published_sha256`；原件的 `source_sha256` 可由作者在本机复核。

## 运行环境（原始运行）

- macOS 14.1（arm64），**只用 CPU**
- Python 3.12.4，torch 2.10.0，transformers 4.57.6，sacrebleu 2.6.0，jiwer 3.1.0，numpy 2.5.3，safetensors 0.8.0，mediapipe 0.10.14
- T5：Hugging Face 预训练的 `t5-small`，删除了它的 encoder
- 生成设置：greedy，`max_length=30`，`num_beams=1`

## 哪些结果可以直接复算

在 `evidence/` 目录下运行下面的命令。只需要 Python 3 和 `pip install sacrebleu`：

```
python recompute_metrics.py        # 加 -v 可逐项打印
```

作者在发布前运行过一次，**385 项检查全部通过**。这个脚本会从已发布的逐条预测复算下列内容，并和原始运行写下的值比较：
- P0.1 三次运行的最终 BLEU、chrF 和 exact match（17/32、13/32、32/32）；
- P0.2 两次运行**每个 epoch** 的 val 和 frozen BLEU/chrF，与 `epoch_table.csv` 比较（表中数值保留 2 位小数）；
- 重训最佳 checkpoint 在 bs1 和 bs8 下的指标，以及修复前后 bs1 与 bs8 预测不同的条数（val 95→0，frozen 35→0；重训后 0/0）；
- 输入错配诊断中每次打乱后的 BLEU/chrF、"正确视频 loss 更低"的样本数，以及逐样本 loss 差的均值。

**只能核对记录值、不能直接复算的内容**：
- **loss**：包括 val/frozen loss 和 teacher-forced loss。复算要用到 checkpoint 和 landmark。输入错配诊断中，逐样本 loss 可以从 `perm_seed*.json` 核对；但 HF 口径的 batch loss（报告 2.3 表中的 +0.091~+0.115）以及 encoder 余弦相似度，都需要模型才能复算。
- **batch-context 诊断**：`p02_batch_context*/report.json` 是逐视频的结果，其中的中间张量（`tensors/`，约 480 MB）没有上传。
- **训练过程本身**：需要权重、数据和代码仓库的其余部分。

## 代码不能独立运行

`code/` 下只有本次新增或修改的文件，**不能单独运行**，原因如下：
- 这些文件还依赖代码仓库 `main`（`5b7eb92`）中的 `src/dataset.py`、`src/models/translation_model.py`、`src/utils/{metadata,splits}.py` 等文件，这些文件没有复制过来；
- 运行还需要 How2Sign landmark 数据、`holdout_split.json` 和 frozen landmark，它们都不在 GitHub 上；
- 还需要从 Hugging Face 下载 `t5-small`。

`tests/test_padding_invariance.py`（45 项）在代码仓库中与原有测试一起运行，共 56 项全部通过（2026-09-25）。测试需要放在完整的代码仓库里才能运行。

## 未上传的内容

| 项目 | 数量 | 大小 | 说明 |
|---|---|---|---|
| P0.2 原始运行的逐 epoch checkpoint（`p02_10pct_e30/checkpoints/`） | 28 个 checkpoint，280 个文件 | 12.32 GB | 每个 `model.safetensors` 420.8 MB，另有 optimizer 等文件 |
| P0.2 修复后重训的 checkpoint（`p02_padfix_10pct_e30/checkpoints/`） | 30 个 checkpoint，300 个文件 | 13.20 GB | 同上 |
| P0.1 最终模型（3 × `final_model/`） | 18 个文件 | 1.26 GB | 每个 `model.safetensors` 420.8 MB |
| batch-context 中间张量（2 × `tensors/`） | 100 个文件 | 0.49 GB | 仅用于诊断 |
| 以上合计 | 698 个文件 | 27.28 GB | |
| 与本报告无关的 smoke/recheck 运行（`tiny32_smoke_*`、`p02_smoke*`、`p02_padfix_smoke`） | 8 个目录 | 约 2.5 GB | 冒烟测试，报告没有引用 |
| 训练/验证 landmark、frozen landmark、原始视频、metadata 和 split 文件 | — | — | 位于本仓库 `asl-translator/...` 下，作者本机未跟踪 |
| `.venv` 以及代码仓库中本次没有改动的文件 | — | — | — |

关键权重的 sha256，供以后共享时校验：

| 权重 | sha256 |
|---|---|
| P0.2 重训最佳 `p02_padfix_10pct_e30/checkpoint-6880/model.safetensors` | `0d087522e12d8225434dbf4a591da8cd1eaada92747c51e46ef023d8264ca5ec` |
| P0.2 原始最佳 `p02_10pct_e30/checkpoint-6192/model.safetensors` | `49397a7b80a39366acca10b96f1a7ae1d38c2cfd8e43ebce8e2ab022426ada0f` |
| P0.1 dropout=0 `tiny32_e200_lr1e-4_t5drop0/final_model/model.safetensors` | `ab5cfd58cad9daf7da6a98bc3045c35cbae281df6d15b44c939fc073bd0a3c4d` |
| P0.1 默认 `tiny32_e200_lr1e-4/final_model/model.safetensors` | `b52c5c94f45eb9841723c0e4107fd5d6a0edf5e03bd4eb6b7574f56bd941bc42` |
| P0.1 constant LR `tiny32_e200_lr1e-4_constant/final_model/model.safetensors` | `d9d7918a3dc5350ea28981a233bc8eadf91406d71eb28954c357652b9a97e73a` |

### 共享权重的建议方案（尚未执行，需要批准）

不建议把权重直接放进这个 Git 仓库：每个文件 420.8 MB，会永久增大仓库历史。如果确实需要共享，建议只共享上表中 2–5 个关键 `model.safetensors`（约 0.84–2.1 GB），不共享 optimizer 状态和全部 58 个 epoch checkpoint。可选方案：
1. **团队已有的云存储**（Google Drive、S3、GCS 等），按上表 sha256 校验，把下载链接写进本 README；
2. **本仓库的 GitHub Release 附件**：单个文件上限 2 GB，不进入 Git 历史，访问权限跟随这个私有仓库；
3. **Git LFS**：会占用组织的 LFS 存储和流量额度，需要仓库管理员同意。
