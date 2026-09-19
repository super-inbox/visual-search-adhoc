# gloss-free-asl-translation 调研结论（任务 c）

日期：2026-09-19 · 仓库：`yyouretoast/gloss-free-asl-translation` · upstream commit `5b7eb92ff90c4ac5907bc6328edb79c24cec6c77`（MIT 许可证）

**分类：B — PIPELINE WORKS, NO TRAINED CHECKPOINT（流程能跑，但没有训练好的 checkpoint）**

**性质：这是上游缺少训练好权重（upstream-artifact blocker），不是我们本地流程失败。**

> 一句话：**代码和 MediaPipe 部分能跑；训练好的 ASL→English 模型不存在，所以没法做翻译。** 这是两件不同的事。

## 这个 repo 能不能跑？

**能跑。** 用 Python 3.12 在 repo 内建了独立环境，依赖装好；官方测试全部通过（不含 slow：6 个通过；slow：5 个通过；共 11/11）。没有改动 repo 里任何已跟踪的文件。
小问题：README 的安装步骤漏了 `pip install -e .`（repo 自己的 CI 里有），不加的话跑测试会报 `No module named 'src'`。

## MediaPipe 部分能不能跑？

**能跑，而且是真实数据。** 已确认这个 repo 用的是 MediaPipe Holistic（老 API，固定 `mediapipe==0.10.14`）。我们在和 Uni-Sign 测试**同样的两个 How2Sign 公开视频**上跑了：

| | SHORT `g0uGWjwdOIw_1-8-rgb_front` | LONG `FzmL8SL6Bow_1-8-rgb_front` |
|---|---|---|
| 时长 / 帧数 | 5.9 秒 / 141 帧 | 25.8 秒 / 618 帧 |
| 成功提取 | 141/141 帧 | 618/618 帧 |
| 耗时（CPU） | 3.7 秒 | 15.2 秒 |
| 送入模型的形状 | (141, 501) | (124, 501)（每 5 帧取 1 帧） |
| 左手丢失帧 | 0.7% | **34.0%** |
| 右手丢失帧 | 5.7% | **40.6%** |
| NaN | 0 | 0 |

关键点：pose 33 点、左手 21、右手 21、脸 92（从 468 个里选）；每个点是 x/y/z；每帧 501 维。丢失的点直接补 0。

## 有没有训练好的 checkpoint？

**没有。** 查了：代码树、94 个 git 历史提交、Git LFS、README、GitHub Releases/Tags/Actions、作者的 Hugging Face、各种下载链接、Kaggle notebook。结果：
- 没有任何权重文件，也没有下载链接；`.gitignore` 还特意忽略了 `results/` 和 `*.safetensors`。
- README 的 Demo 和 Results 都是"训练完成后再补"的占位符。
- Kaggle notebook 没有保存任何运行输出。历史文档里只有在**模拟数据**上的试跑（BLEU 0.0）。
- 作者的 Hugging Face 上只有不相关的项目（deepfake 检测等），没有 ASL 模型。
- 网上有别人的 "asl-translation" 模型，但和这个 repo 无关、架构不同，**没有使用**。
- 普通的 T5 权重不算（它没有学过手语）。

（唯一不确定的地方：作者可能在自己的 Kaggle 里有没公开的训练结果，我们从公开渠道查不到。）

## 能不能直接做 ASL → English？

**不能。** 没有训练好的模型，所以：没有做推理，没有做小规模评测，也没有 WER/BLEU 等数字。如果拿随机初始化的模型硬跑，只会得到乱码，我们没有这么做，也没有把它当成翻译结果。**没有编造任何评测结果**，也**没有开始任何训练**。

补充：即使有 checkpoint，这个模型的设计也有限制——输出最多 30 个 token，输入最多取 150 帧；我们的 LONG 视频（78 个词）会被明显截断。

## 和我们现在的 RTMPose 有什么区别？

| | 我们的 RTMPose | 这个 repo 的 MediaPipe |
|---|---|---|
| 关键点 | COCO-WholeBody 133 点 | 33 + 21 + 21 + 92（从 468 选） |
| 坐标 | **2D 像素** | **3D**，归一化 0–1 + 深度 z |
| 脸 | 68 点 | 468 点里选 92 点 |
| 置信度 | 有（分数，不是概率） | 基本不用 |
| 手丢失 | LONG 上 618 帧**都检测到手** | LONG 上丢了 34% / 41% |
| 速度 | 37 秒（LONG） | 15 秒（LONG）（不是严格对比） |

- **两者格式不兼容**，我们的 RTMPose JSON **不能直接**喂给这个 repo。
- 在同一个 LONG 视频上，两者对肩膀、手腕等共同关节的位置差只有画面大小的 1–2%，左右手方向也一致——所以**原则上可以做适配器**（手 21↔21、身体主要关节可直接对应）。
- 但适配会**丢信息**：RTMPose 没有 z 深度；脸的 68 点对不上 92 个 MediaPipe 脸点。
- **没有做适配器**。而且没有权重，适配器现在也没有用处。
- 注意：RTMPose"每帧都有手"部分是因为它总会输出 133 个点，不一定代表比 MediaPipe 更准（没有标准答案）。

## 下一步该怎么办？

1. **汇报为 B**：流程可跑，但没有可评测的 ASL→English 模型，不能当成可评测系统。
2. **（可选，成本很低）** 在作者的 GitHub 提个 issue，问是否有训练好的 checkpoint，并请他说明 `input_dim`、T5 版本（`t5-small` 还是 `flan-t5-base`）、是否用 I3D。最近一次更新是 2026-07-01，仓库有在维护。
3. **我们自己不要训练**，除非另行决定：需要 ~44 GB 的 How2Sign MediaPipe 数据 + GPU 时间，作者自己也预期分数很低。repo 里没有记录需要多少 GPU 时间，我们也没有估算。
4. **暂时不要做 RTMPose→MediaPipe 适配器。**
5. 按 a → c → b 的顺序，**可以开始任务 b**。本次没有动 b。

详细数据见同目录 `RESULTS.md`、`checkpoint_search.json`、`mediapipe_*_summary.json`、`mediapipe_vs_rtmpose_comparison.json`。
