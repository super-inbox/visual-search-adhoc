# P0 工作报告：tiny-set 过拟合、10% 多 epoch 训练与 padding 修复

- 日期：2026-09-25
- **发布说明**：本报告发布在 `super-inbox/visual-search-adhoc` 仓库的 `docs/daily_report/9.25/asl-p0-diagnostics/`。同一目录下另有 [`code/`](code/)（本次实验的代码和测试副本）、[`evidence/`](evidence/)（配置、指标、epoch 表、逐条预测、日志）和 [`README.md`](README.md)（来源、hash、复算方法、未上传清单）。**模型权重、checkpoint、landmark 和数据集都没有上传。**
- 代码仓库：`gloss-free-asl-translation` 分支 `baobao/asl-tiny-overfit-2026-09-24` 的 commit `7da5734`。该 commit 只在作者本机，**推送到 GitHub 失败（403），仍未推送**，见第 6 节。
- 报告中的所有数字都来自 `results/`、`experiments/` 下的文件。四舍五入前的精确值写在括号里。出处列在各节末尾。
- **路径对应**：文中的 `results/<X>` 对应本目录的 [`evidence/results/<X>`](evidence/results/)，`src/`、`scripts/`、`tests/` 对应 [`code/`](code/) 下的同名路径。唯一的例外是 `checkpoints/`、`final_model/` 和 `tensors/`，这些权重和张量没有上传，只在作者本机。

---

## 0. 一句话结论

**模型能记住 32 条训练样本：关掉 T5 dropout 后，训练集 BLEU 达到 100。但在验证集和测试集上仍然没有学会翻译，BLEU 约为 1。** padding/mask bug 已经修复并通过测试，但修复后重训，翻译质量没有实质改善。模型的输出会随输入视频变化，只是正确视频带来的优势很小。

> ⚠️ 下面两个数字是在不同数据上测的，不能放在一起比较：
> - **BLEU 100**：只在 **32 条训练样本**上测（模型训练时见过这些样本），是记忆能力诊断。
> - **BLEU 约 1**：在 **366 条验证样本**和 **147 条 frozen test 样本**上测（训练时从未见过），代表真实的翻译能力。

---

## 1. 老板要求及完成状态

| # | 要求 | 状态 | 说明 |
|---|---|---|---|
| P0.1 | 固定 tiny set 过拟合，验证模型能否记住训练样本 | ✅ 完成（有条件通过） | 只有 T5 dropout=0 时通过（BLEU 100、32/32）。默认 dropout=0.1 时未达到 BLEU>80 的通过线（70.74、17/32）。 |
| P0.2 | 10% 数据多 epoch 训练，观察验证集能否学到翻译 | ✅ 已完成，但结果为负 | 验证 loss 下降，但验证/测试 BLEU 始终约为 1。 |
| — | 诊断：模型是否使用视频输入（输入错配） | ✅ 完成 | 模型使用了视频，但作用很弱。见第 4 节。 |
| — | 诊断并修复 padding/mask bug | ✅ 已修复，测试通过 | 已修复；代码仓库中已在本地提交（尚未推送），副本见本目录 `code/`。修复后同一模型用 bs=1 和 bs=8 预测，结果一致。 |
| — | 修复后受控重训 | ✅ 完成 | 翻译质量无实质变化。 |

---

## 2. 关键数字对照表

### 2.1 P0.1：tiny-set 过拟合（32 条**训练**样本，评估也在这 32 条上）

共同设置：t5-small（预训练，删除 T5 encoder）+ 随机初始化的 Conformer encoder / modality bridge。训练 200 epoch、800 步，bs=8，lr=1e-4，Adafactor，warmup 0.1，CPU。生成用 greedy，max_length=30。

| 运行 | T5 dropout | LR schedule | BLEU | chrF | WER | 完全一致 | 最终 train loss |
|---|---|---|---|---|---|---|---|
| `tiny32_e200_lr1e-4`（默认） | 0.1 | linear | **70.74** (70.7418) | 77.34 | 0.313 | **17/32** | 1.1127 |
| `tiny32_e200_lr1e-4_constant` | 0.1 | constant_with_warmup | 56.72 | 64.67 | 0.567 | 13/32 | — |
| `tiny32_e200_lr1e-4_t5drop0` | **0** | linear | **100.00** | 100.0 | 0.0 | **32/32** | 0.0514 |

- dropout=0 运行在 epoch 180 首次达到 32/32、BLEU 100，epoch 190 和 200 保持不变。
- dropout=0 只关闭了 T5 内部的 dropout，encoder 的 dropout 仍是 0.1（`run_config.json` 中 `encoder_dropout_active: true`）。
- 与默认运行相比，dropout=0 运行的命令行只多了 `--t5-dropout 0` 和显式的 `--lr-scheduler linear`（linear 本来就是默认值）。对比文件还记录了两次运行每一步的学习率都相同（`lr_identical_all_steps: true`）。

出处：`results/tiny32_e200_lr1e-4*/summary.json`、`run_config.json`、`final_predictions.json`（我逐条比对了 exact match：17 条和 32 条）、`results/tiny32_diagnostics_t5drop0_compare.json`。

### 2.2 P0.2：10% 数据多 epoch（**验证 / 测试**集）

数据来自 `ids/` 和 `run_config.json`，旧运行与重训的 ID 列表逐字节相同：

| 集合 | 片段数 | 视频数 | 备注 |
|---|---|---|---|
| train | 2,751 | 1,208 | 含 677 条 signer 未知的片段 |
| val | 366 | 366 | 与 train 无 clip/video 重叠。规范化后的文本重叠有 2 条（"good"、"ok"） |
| frozen test | 147 | 128 | 128 条来自 how2sign_v2 official test，19 条来自 pilot_v1 test。与 train/val 零重叠，不参与模型选择 |

两次运行的设置完全相同（`run_config.json` 只有输出目录不同，初始权重 sha256 也一致）：t5-small，seed 42，bs=8，lr=1e-4，最多 30 epoch，按 val loss 做 early stopping（patience 10）。

| 指标（取最佳 epoch） | 1-epoch 旧基线 | 原始多 epoch（修复前） | 修复后受控重训 |
|---|---|---|---|
| 最佳 epoch / 实际训练 epoch | — | 18 / 28（early stop） | 20 / 30 |
| val loss | 5.1766 | **3.6339** (3.63385) | **3.6415** (3.64149) |
| val BLEU | 0.03 | **1.00** (0.9976) | **0.99** (0.9872) |
| val chrF | 2.21 | 11.51 | 11.89 |
| val 不同预测数 / 最常见预测占比 | 8/366 · 331 条相同 | 119/366 · 23.5% | 206/366 · 5.2% |
| frozen loss | 5.2651 | 3.7115 | 3.7224 |
| frozen BLEU | 0.02 | 1.24 | **1.02** (1.0227) |
| frozen chrF | 1.96 | 11.36 | 11.12 |

解读：多 epoch 训练让 loss 从约 5.2 降到约 3.63，输出也从几乎全部相同变得更多样。**但 BLEU 始终在 1 左右，预测大多是 "you're going to be a little bit of a sleeve…" 这类通用、重复的句子。** 原始运行和重训的最佳结果没有实质差别。

出处：`results/p02_10pct_e30/`、`results/p02_padfix_10pct_e30/` 下的 `summary.json`、`epoch_table.md/.csv`、`run_config.json`、`ids/`、`comparison_vs_old_p02.md`；`results/p02_padfix_10pct_e30_best_eval/bs{1,8}/metrics.json`；1-epoch 基线数字取自 `results/p02_padfix_10pct_e30.log` 开头。

### 2.3 输入错配诊断（正确视频 vs 打乱后配错的视频）

设置：用**修复前**原始运行的 epoch 18 checkpoint、修复前的代码、bs=8。每个集合随机打乱 10 次，把视频和标签错配，标签本身不变。

| 集合 | 错配后 loss 上升（10 次打乱的范围） | 正确视频 loss 更低的样本数 | chrF 变化 | BLEU 变化 | 预测随视频移动的条数 |
|---|---|---|---|---|---|
| val366 | +0.091 ~ +0.115 | 234–256 / 366 | −0.35 ~ −0.61 | −0.36 ~ +0.23 | 354–359 / 366 |
| frozen147 | +0.047 ~ +0.073 | 88–105 / 147 | −0.06 ~ −0.76 | −0.54 ~ −0.08 | 142–145 / 147 |
| train 抽样 366 | +0.20 ~ +0.23 | 327–339 / 366 | −0.79 ~ −1.40 | −0.60 ~ +0.08 | 347–359 / 366 |

- 10 次打乱中，没有一次的 loss 低于或等于正确配对，也没有一次的 chrF 高于或等于正确配对。在 val 上有 1 次打乱的 BLEU 高于或等于原始值，train 抽样上有 2 次。BLEU 在这个量级上噪声很大。
- 不同视频的 encoder 输出平均余弦相似度约 0.998–0.999，其中约 99.9% 的能量来自所有视频共有的成分。去掉共有成分后，不同视频之间的余弦相似度只有约 0.02–0.05。**也就是说，encoder 输出主要由与视频无关的共有成分组成，视频特有的信号很弱。**

出处：`results/p02_input_dependence/summary.json`、`results/p02_input_dependence.log`。

### 2.4 padding/mask 修复

修改文件：`src/models/manual_encoder.py`（+15/−7）。共三处：
1. padded 帧经过 projection 后会带上 bias/LayerNorm 产生的非零值，修复后在下采样卷积之前把它们清零；
2. ConformerConvModule 中，GLU 之后把 padded 位置重新清零，再进入 depthwise conv；
3. 下采样后的 key_padding_mask 原来用 `max_pool1d(k=3,s=2,p=1)` 计算，偶数长度的序列会多标一个有效位置。改为 `attention_mask[:, ::2]`。

| 检查项 | 修复前 | 修复后 |
|---|---|---|
| 同一旧 checkpoint，bs=1 与 bs=8 的预测不同的条数：val366 | 95 | **0** |
| 同上：frozen147 | 35 | **0** |
| 10 个视频 × 5 种 batch 组合，预测与单独推理一致的次数 | 31/50 | **50/50** |
| 重训后最佳 checkpoint，bs=1 与 bs=8 的预测不同的条数：val366 + frozen147 | — | **0 / 0** |
| `tests/test_padding_invariance.py` | — | **45 passed** |
| 全部测试 `tests/` | — | **56 passed**（1 warning） |

- 在旧 checkpoint 上，修复只改变了 val 中 bs=8 的 95 条预测，这 95 条的 exact match 修复前后都是 0。按句子 chrF 算，47 条变好、47 条变差、1 条持平。val BLEU 从 0.9976 变为 0.9565。
- 测试是我今天（2026-09-25）用 `.venv/bin/python -m pytest` 重新跑的，结果与上表一致。

出处：`results/p02_padfix_eval/before_after_comparison.json` 及 `{before,after}_bs{1,8}/metrics.json`、`results/p02_batch_context{,_after_fix}/report.json`、`results/p02_batch_context/fix_candidates.json`、`git diff src/models/manual_encoder.py`。

---

## 3. 结论：能支持的与不能支持的

### 能够支持
1. 在 32 条短句样本上，不开 T5 dropout 时，这套架构和训练流程能把训练样本完整背下来（BLEU 100、32/32）。这说明前向传播、label 对齐和生成流程没有阻止记忆的硬 bug。
2. 在 tiny-set 上，T5 dropout=0.1 明显拖慢记忆：200 epoch 后只有 70.74 / 17/32。
3. 在 10% 数据上多 epoch 训练，val loss 从约 5.18 降到约 3.63，输出多样性明显上升，**但验证和测试 BLEU 始终约为 1。**
4. 模型**确实使用了视频输入**：错配视频时 loss 稳定上升，p 值很小；预测跟着视频走（例如 val 上 354–359/366 条）。**但正确视频的优势很小**（val 上 loss 只差约 0.1，chrF 只差约 0.5）。
5. padding bug 真实存在，会导致同一模型的预测随 batch 组成变化。修复后这种变化消失，并有回归测试覆盖。
6. padding bug **不是**验证 BLEU 约为 1 的主要原因：修复后重训，val BLEU 0.99，frozen BLEU 1.02，与修复前（1.00 / 1.24）没有实质差别。

### 不能支持
1. **不能**因为 BLEU 100 就说"模型能翻译"。BLEU 100 只在见过的 32 条训练样本上测得，而且这 32 条只从 ≤30 token 的短句中抽取。
2. **不能**说"模型完全忽略视频"。第 4 点的证据与此矛盾。
3. **不能**说修复后的模型对视频的依赖有没有变化：输入错配诊断只在修复前的 checkpoint 上跑过。
4. **不能**说扩大数据或训练更久就会好。现有数据只能说明，在这个 10% 设置下 30 epoch 不够，也无法推断更大规模的结果。
5. **不能**把 frozen BLEU 1.24 和 1.02 的差异当成修复带来的退步。BLEU 在约 1 的量级上噪声很大，错配诊断中 10 次打乱之间的 BLEU 波动就有约 ±0.3–0.6。

---

## 4. 局限性

- **模型规模**：所有 P0 实验都用 t5-small（`scripts/train_p02.py`、`scripts/overfit_tiny.py` 中 `T5_MODEL = "t5-small"`），与仓库 notebook 中的 flan-t5-base 不同。
- **tiny-set 有选择偏差**：这 32 条样本是从 2,060 条合格训练样本中抽的。抽样前排除了 683 条 token 数超过 30 的句子和 8 条 tokenizer 往返不一致的句子。其中 `03jABW2MKkk_10-8-rgb_front` 有 29 个内容 token，在 max_length=30 下放不下 EOS：文本完全一致，但没有生成 EOS。
- **只有一个 seed**：P0.1 和 P0.2 的每个配置都只跑了一次，没有 seed 方差。
- **生成长度上限**：val/frozen 评估用 greedy 生成，max_length=30，长参考句会被截断，BLEU 会因此偏低。不过这不足以解释 BLEU 约为 1 的结果。
- **val loss 的口径不同**：重训最佳 val loss 3.6415 是 HF Trainer 在 bs=8 下的 batch 平均。在同一 checkpoint 上，bs=1 算出 3.6224，按 token 加权算出 3.6349。比较时必须用同一口径。
- **frozen 特征的来源不同**：train/val 用的是第三方 Kaggle "How2Sign Holistic" MediaPipe 提取结果，frozen 是本地用 upstream `src/data_pipeline.py` 提取的（见 `ids/overlap_report.json`）。两者可能存在分布差异。
- **"10%"的比例未核对**："10%"只来自数据目录名 `local_run_10pct`，我没有核对它相对全集的真实比例。
- **重训所用代码版本是推断的**：重训的 `run_config.json` 没有记录代码 hash。我是根据时间推断的：`manual_encoder.py` 最后修改于 2026-09-24 21:32:54，重训开始于约 21:34（结束 23:56:39，总耗时 8,508 s）。之后对最佳 checkpoint 的评估记录的 `manual_encoder_sha256` 为 `b7efabef…`，与当前文件一致。
- **默认 dropout 运行的配置记录不全**：`tiny32_e200_lr1e-4` 的 `run_config.json` 由较早版本的脚本生成，没有 `t5_dropout` 和 `initial_state_dict_sha256` 字段。dropout=0.1 是根据脚本默认值和 dropout=0 运行中记录的 `t5_before` 推断的。
- **运行环境**：全部在 CPU 上运行，gradient_accumulation_steps=1，与 upstream 的 8 不同（`run_config.json` 中已列为 deviation）。

---

## 5. 建议的下一步实验

按优先级和成本排序：

1. **（无需训练）在重训后的最佳 checkpoint 上重跑输入错配诊断**（`scripts/diagnose_input_dependence.py`），补上结论第 3 条的空缺，并确认 encoder 输出里共有成分是否仍占约 99.9%。
2. **（无需训练或训练很少）排查 encoder 表示坍缩**：检查 501 维 landmark 输入的归一化（各维度的尺度、缺失帧怎样填充），以及 Conformer 和 bridge 输出在不同视频之间的方差。如果输入尺度被少数维度主导，或者 bridge 输出被 LayerNorm/bias 主导，就能解释为什么视频特有的信号这么弱。
3. **做中等规模的记忆到泛化曲线**：例如 32 → 256 → 1,024 条训练样本，每档同时报告训练子集和固定 val 的 BLEU/chrF 以及错配 loss 差，定位泛化在哪一档开始失效。建议至少用 2 个 seed。
4. **做针对 encoder 的消融**：给 encoder/bridge 和 T5 设置不同的学习率，或者先冻结 T5 decoder 预热 encoder，然后观察错配 loss 差能否明显高于约 0.1。以这个差值作为主要指标，BLEU 作为次要指标。
5. **调整评估设置**：把生成的 max_length 放宽到能覆盖 val/frozen 参考句长度，或者按长度分桶报告，排除截断带来的偏差。
6. **在第 1–4 步确认 encoder 能提供有效的视频信号之前，暂不建议**扩大到 100% 数据、换 flan-t5-base 或做长时间训练。

---

## 6. 代码与结果的提交状态（2026-09-25）

**本目录在 GitHub 上已发布的内容**（`super-inbox/visual-search-adhoc`，分支 `baobao/asl-p0-report-2026-09-25`，路径 `docs/daily_report/9.25/asl-p0-diagnostics/`）：
- 本报告和 `README.md`；
- `code/`：代码仓库 commit `7da5734` 中本次新增或修改的 8 个文件，内容逐字节一致，另有 padding 修复的 patch：
  - `src/models/manual_encoder.py`
  - `scripts/overfit_tiny.py`、`train_p02.py`、`eval_checkpoint.py`、`diagnose_tiny.py`、`diagnose_input_dependence.py`、`diagnose_batch_context.py`
  - `tests/test_padding_invariance.py`

  这些代码**不能单独运行**，还依赖代码仓库中的其他文件和数据，见 README。
- `evidence/`：P0.1、P0.2、padding 修复和输入错配诊断用到的 run_config、summary、epoch 表、逐 epoch 的 val/frozen 预测、逐条预测、指标、逐步日志、终端日志、样本 ID 和 tiny32 manifest。共 318 个文件，约 31.6 MB。
  - 其中 11 个文件去除了本机路径前缀，数值没有改动，原件的 sha256 记录在 `MANIFEST.tsv`。
  - `evidence/recompute_metrics.py` 可以从逐条预测复算 BLEU、chrF 和 exact match，发布前 385 项检查全部通过。

**代码仓库 `gloss-free-asl-translation`**：commit `7da5734`（分支 `baobao/asl-tiny-overfit-2026-09-24`）**仍然只在作者本机，没有推送**。推送到 `yyouretoast/gloss-free-asl-translation` 时返回 403，因为 GitHub 账号 `baobaoli03` 对该仓库没有写权限。没有创建 PR，也没有创建 fork。本目录的 `code/` 是目前在 GitHub 上唯一能看到的副本。

**仍未上传、只在作者本机的内容**（明细见 README）：
- 全部模型权重：P0.2 两次运行的 58 个 epoch checkpoint（25.5 GB），P0.1 的 3 个最终模型（1.26 GB），每个 `model.safetensors` 420.8 MB；
- batch-context 诊断的中间张量（0.49 GB）；
- 与本报告无关的 smoke 运行；
- 训练、验证和 frozen landmark、原始视频、metadata、split 文件；`.venv`；代码仓库中本次没有改动的文件。

如需共享权重，README 中给出了建议方案，**尚未执行**。
