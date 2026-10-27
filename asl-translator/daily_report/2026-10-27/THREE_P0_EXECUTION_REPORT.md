# ASL 三个 P0 执行结果与 Baobao 接续任务

2026-10-27。代码与原始记录位于 [实验目录](../../experiments/p0-2026-10-27/README.md)。本轮没有上线，没有训练，没有获得新的翻译质量提升结论。

| P0 | 实际执行状态 | 结果 |
|---|---|---|
| 采样 | 实现三臂并跑完 45 个旧窗口展示视频，135 条采样记录 | 13 例超过 256 帧，32 例保持全帧。R10 诊断区间采样 111→69，最大间隔 0.50→0.208 秒。不是解码效果。 |
| Fingerspelling specialist | OpenFS 权重成功加载，实际执行 4 段视频及固定窗口，共 18 个识别输入 | 获得字母串与窗口时间戳；没有自动拼写存在性判断，没有专家准确率。 |
| 防重复解码 | 完成受控双臂执行脚本，执行资产预检 | 当前机器缺少 Uni-Sign checkpoint、mT5 和 45 个匹配 pose；没有 treatment 输出。 |

## P0 采样与线上关系

本地 `curify_background/app/utils/asl_utils.py` 已采用 Gemini 动作探测采样：4fps 探测、按 active run 分配帧、时长预算约 2fps、24–240 帧。本轮的“覆盖＋动作”不是发现线上尚未使用 motion，而是提出保留全局均匀覆盖的研究对照。

本地另有未提交的 `asl_backend.py`：可选 Uni-Sign 路径按 8 秒、24fps 切片，每段最多 192 帧。因此这条路径本身不触发上游 256 帧随机抽样。该代码的部署状态未验证，不能把它描述为已经在线运行。文件哈希和工作区状态见 `results/backend_audit.json`；未修改这些应用文件。

实验采用固定预算：半数帧均匀覆盖全部时间，其余按裁剪后的帧差能量分配；不使用 reference、不删除停顿区间。三臂在相同压缩 OLD 视频上比较。13 个长片的平均最大采样间隔：random 0.307 秒、uniform 0.088 秒、coverage_motion 0.148 秒。纯 uniform 的时间覆盖更密；motion arm 的目标是增加高变化区间样本，不是宣称所有指标最好。

R10 的 5–16 秒诊断区间：random 111/256、uniform 111/256、coverage_motion 69/256。手部静止不代表没有语言信息。模型质量需要同域 pose 上配对解码；不能将当前视频几何结果直接应用到 official pose，也不能据此升级线上。

## P0 Specialist 的真实输出

本轮使用 OpenFS Chicago recognizer，checkpoint 来自官方发布链接，代码固定 `0d6fa3fa9b5aeaf99171e8c77e89531a22a6fd27`。下载权重内配置是 **2D、42 维输入**，不同于当前仓库默认的 3D/63 维；执行时按权重配置加载。CPU 推理，原视频→MediaPipe Holistic→手部关键点→开放字母序列，无参考姓名或字典输入。

这是模型 specialist，但**不是 RGB 识别器，也不是 fingerspelling 时段检测器**。此实验验证视频到专用手部模型的可运行路径，尚未验证 RGB 相对 pose 的增益。

| 旧展示片 | 固定窗口（片内秒） | 原样输出举例 |
|---|---|---|
| R02 | 0–2 | `camilian` |
| R05 | 整片 | `liswithey guor` |
| R35 | 0–2 | `back` |
| R41 | 整片 | `ship` |

所有窗口，包括不理想输出，保留在 `results/specialist.json`，共 18 个输入。R02/R05 输出提供了可送专家核验的线索，不能因为接近已知名字就确认正确。R35/R41 同样生成字母串，说明不能将“有输出”当成拼写检测。R41 也没有盲评过，不能把该输出计作已确认 false positive。

时间戳标记的是**喂给识别器的窗口**，不是模型检测出的精确拼写起止；每个字符的时间戳保持 null。记录保留原帧索引、视频哈希、手部观测数和模型哈希。token probability 未校准，不设自动替换阈值；`fs_present=null`，全部需复核。

与上游预处理差异：单人全画面，未运行 YOLO person crop；Holistic complexity=1 而非 2；按上游规则保留高于肘部的手，使用训练时每只手压紧后的序号，并另外保留真实视频帧映射。Intel Mac Torch 2.2 增加两项 API 兼容垫片（padding mask shape check / disable missing MHA fastpath），未改变权重。展示版是压缩 OLD 窗口，不能拿结果与不同时间窗口的 official 输出计算增益。

自动区间检测方面，重新核查 [FS-Detection 官方代码](https://github.com/chevalierNoir/FS-Detection) 发现确实提供 ChicagoFSWild+ 预训练 detector 链接，修正之前“未找到权重”的信息。其代码固定 `b386f04d90b88daf9f7bf598e5ca7075d8376421`，依赖旧 PyTorch 1.1、Warp-CTC、CUDA 路径；本轮未移植或执行 detector。OpenFS 的 frame classifier 也不能默认当成整句拼写检测器。

OpenFS 代码及 checkpoint 的官方许可限非商业研究。本次仅研究验证，未将权重、视频或第三方代码推入仓库，未集成到产品。产品采用需另行核实许可。

## P0 防重复

新实验与冻结的 P0-A 分开：control 保持 beam=4、max_new_tokens=100；treatment 仅增加 `no_repeat_ngram_size=3`，针对 tokenizer token 三元组，不等于三个英文单词。读取固定 45 例白名单，校验上游 commit、checkpoint、pose 和模型输入张量哈希，且 control 须与原 CPU 输出一致；不符合则停止解释 treatment。

`results/repetition_preflight.json` 是实际失败的资产预检，不是模型结果。旧报告中的 Apple M3/Anaconda 路径不在当前 Intel Mac 上；检查了本地常见缓存、工作区及报告路径，没有找到对应资产。已询问实验机或共享目录。接通后才可生成配对文本并测量内容恢复、误伤、重复和截断。

## 当前决策

1. 采样：保留实验实现，先补齐同域输入做质量对照，不直接改线上。
2. Specialist：R02/R05 的结果值得优先盲评；下一步必须验证匹配 official 窗口，并接入真正的 temporal detector。当前不替换姓名、不把滑窗输出算成自动识别成功。
3. 防重复：等待原始实验资产，执行已写好的配对 runner；不要用文本后处理冒充解码改善。

## 验证

6 项采样测试通过（空/短片、非法输入、静止、预算与顺序、全局覆盖、单帧尖峰）；45 例/135 臂的预算、去重、顺序和 PTS 映射检查通过。specialist 完成真实 CPU 前向与生成。防重复仅完成脚本语法与缺失资产预检，未完成模型级验证。


## 给 Baobao 的接续任务

本日报对应分支 `codex/asl-three-p0-20261027`，实验代码及首批结果提交为 `2a84dd0`。先阅读本报告，再按 [实验 README](../../experiments/p0-2026-10-27/README.md) 复现。当前交付是研究分支，尚未合并 main，也未改线上。

### 先恢复匹配的实验资产

请在原实验机定位并记录以下资产的绝对路径、版本和哈希；二进制留在本地或现有共享存储，不提交到 Git：

- Uni-Sign checkout：`eed438bcb49e30405cd6ccdfcccca330c134e830`。
- `how2sign_pose_only_slt.pth`：SHA256 `1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d`。
- mT5 snapshot：`2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f`。
- P0-12 A_official 的 45 个 pose 文件，以及对应原视频窗口。输入哈希可对照 [canonical candidates](../2026-10-23/p0a-candidate-rerank/runs/full45/A_official/run1/candidates.jsonl)。

先执行 `decode_repetition.py --preflight-only`，具体参数见实验 README。若本机路径不同，传入真实路径，不要创建空文件绕过检查。缺失项目见 [预检记录](../../experiments/p0-2026-10-27/results/repetition_preflight.json)。

### 任务一 防重复配对解码

资产齐备后优先执行，这是已有 runner、最容易闭环的模型实验。去掉 `--preflight-only`，运行 control 与固定的 token-trigram 约束两臂。保持模型、输入、seed、beam 和长度限制一致；control 与已保存 CPU 输出不匹配时先排查，不能继续宣布 treatment 有效。

交付：45 例配对输出、chrF/WER、重复率、截断情况、R01 和 R41 的逐句比较。所有案例均保留，包括变差案例。人工语义标签尚缺时写 pending，不以自动分数代替 wrong→right / right→wrong 判断。

### 任务二 同域采样质量实验

现有 `sampling.py` 已可运行，但 `run_sampling.py` 的结果来自压缩 OLD 视频；它还不是 Uni-Sign pose loader 的完整适配。先建立同域视频 PTS→pose 帧映射，再将 sampler 接入研究 loader，保留所选索引及输入哈希。不要把 OLD 视频索引直接套到 official pose。

首先解决 R10 的 23.38–42.38 与 31.03–56.34 时间来源冲突；追溯实际文件与切片命令，不凭时长猜测。之后在固定的匹配输入上比较 random、uniform、coverage_motion 三臂，使用相同解码设置。每个实验前写清输入域和对照；不覆盖 10 月 23 日冻结结果。

交付：映射验证、三臂配对译文与指标、长片子集及正常对照的退化情况。线上 Gemini 与可选 Uni-Sign wrapper 是不同路径；在研究收益确认前，不改默认采样或切片策略。

### 任务三 拼写检测与识别

先复现 [OpenFS 原始结果](../../experiments/p0-2026-10-27/results/specialist.json)，再取得 R02/R05 的匹配 official 原分辨率视频，按原样保存识别输出，不提供 reference 姓名或词典。R35 旧窗口与 official 完全不重叠，必须分别标记。

并行评估 FS-Detection 的预训练 temporal detector 能否在现有环境运行：记录 checkpoint 来源、代码版本、依赖适配及许可。它若不能运行，交付具体报错和所需移植范围；不要把固定滑窗、手部运动或识别器 token probability 改名为检测置信度。

交付：每个视频的候选 start/end、时间基准、区间来源（detector / fixed_window / human）、字母串和模型版本。没有可靠字符对齐时，字符时间戳保持 null。未经盲评，`fs_present` 保持 unknown；不自动替换 Uni-Sign 句子。获得人工标签后，分别评估区间定位、字母识别和整句融合损伤。

### 下一次日报的统一格式

每个 P0 分别列出：本次改动、实际执行命令、输入和模型版本、结果文件、相对 control 的改善与退化、未完成项、下一步。明确区分“可运行”“诊断信号”“翻译质量提升”。当前的 45 例为开发诊断集，不能反复调参后当成独立验证集。
