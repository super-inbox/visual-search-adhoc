# ASL 轻量 landmark 翻译：1% → 10% 可行性实验总结

日期：2026-09-22 · 负责人：Baobao · 详细数据见 `TECHNICAL_REPORT.md`、`RESULTS_TABLE.md`

## 结论先行

**训练流程是健康的，但翻译输出仍然是塌缩的。** 从 1% 扩到 10% 后，loss 明显下降，但翻译质量没有实质提升。模型已经开始依赖 landmark 内容，**但还没有观察到它利用帧的时间顺序**。**目前不建议直接上全量（100%）训练**，需要先做诊断。

## 1. 做了什么

- 测试一个轻量的 landmark 方案能否学到 ASL → English 的翻译信号：How2Sign → MediaPipe/Holistic landmark → 4 层 Conformer → T5-small → 英文（不用 I3D）。
- 用 repo 原生的 MediaPipe 表示，没有强行把我们的 RTMPose 转过去。
- 从 How2Sign realigned TRAIN metadata（31,165 条）中固定采样 1%（312 条）和 10%（3,117 条），使用对应的 MediaPipe/Holistic landmarks 训练。按批准的计划在 CPU 上各训练 1 epoch。
- 在 147 条 evaluation set（128 条 frozen how2sign_v2 + 19 条 historical pilot_v1）上对两个 checkpoint 做了评测，并做了 landmark 对照实验。

## 2. 跑通了什么

- 数据流程、MediaPipe 数据加载、Conformer/T5 训练、1%→10% 扩展全部跑通。两个规模训练都稳定，loss 没有出现 NaN/Inf。
- 防泄漏检查通过：训练集与 147 条 evaluation set 重叠 **0**。147/147 全部完成评分，没有缺失的预测。

| | 1% | 10% |
|---|---|---|
| 选中样本 | 312 | 3,117 |
| 实际训练 / 验证 | 275 / 37 | 2,751 / 366 |
| 训练 loss 首步 / 末步 / 最低 | 11.8434 / 7.3202 / 6.1791 | 12.76 / 5.03 / 4.83 |
| 验证 loss 训练前 → 后 | 11.6633 → 6.1517 | 12.35 → 5.17 |
| CPU 总耗时 | 47.6 s | 269.0 s |

## 3. 还没跑通什么

- **没有得到有意义的翻译。** 1% 的输出基本是空白或一串句点；10% 的 147 条里有 132 条是同一句 "So's a a a a …"。两次的不同输出都只有 **4/147 种**。

| evaluation set（147 条） | 1% | 10% |
|---|---|---|
| BLEU | 0.04 | 0.06 |
| chrF | 0.12 | 2.53 |
| WER | 1.0000 | 1.0115 |
| CER | 0.9960 | 0.8045 |
| eval loss | 6.2259 | 5.2442 |
| 不同输出数 | 4/147 | 4/147 |

- chrF/CER 的小幅变化来自固定的重复输出，**不代表翻译变好了**。

## 4. 学到了什么

- **模型确实依赖 landmark 内容**：NORMAL 明显优于 ZERO_LANDMARKS（输入全部置零），loss 增加量从 1% 的 +0.34 扩大到 10% 的 +6.94。
- **但打乱帧顺序（TEMPORAL_SHUFFLE）在两个规模下都和 NORMAL 基本分不开**（10% 时差值约为 0，366 条里 185 条变好、181 条变差）。
- 也就是说：**模型开始依赖 landmark 内容，但目前没有观察到它依赖时间顺序。** 它可能只是识别出“有结构的输入”，还没有学到手语在时间上的语义。这是一个早期诊断结果，和我们的研究问题直接相关：轻量的姿态轨迹能恢复多少 ASL 语义？需要什么样的时间表示？

## 5. 要不要上全量训练？

**现在不建议。** 1% → 10% 的可行性检查已经完成。数据量扩大 10 倍，loss 变好了，但输出没有变好。在没搞清楚原因之前直接上 100%，风险很高。

## 6. 联系原作者

- 已在 GitHub 向 `yyouretoast/gloss-free-asl-translation` 提交 Issue #1（https://github.com/yyouretoast/gloss-free-asl-translation/issues/1），询问是否有 checkpoint、部分训练的 checkpoint 或 Kaggle 训练输出。
- **目前在等待回复**（Issue 仍为 OPEN，暂无评论）。
- **没有进行邮件联系。**

## 7. 需要您决定的下一步（选一个或几个）

1. 用现有的 10% 设置多跑几个 epoch，判断是不是训练不足；
2. 换一种解码方式（如 beam search 或 repetition penalty），判断输出塌缩是否来自解码；
3. 查明为什么打乱帧顺序没有影响；
4. 研究 RTMPose 和 MediaPipe 的表示差异。我们的轨迹工作用 RTMPose/COCO-WholeBody，这个 repo 用 MediaPipe/Holistic，两者不能直接互换，本次没有做转换；
5. 等诊断完成后，再决定是做全量训练，还是转向新的时间表示方案。
