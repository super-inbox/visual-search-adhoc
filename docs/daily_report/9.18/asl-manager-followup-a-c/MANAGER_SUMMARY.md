# ASL Manager Follow-up — Manager 摘要（Phase A + Phase C）

日期：2026-09-18 ｜ 执行顺序：A → C → B ｜ Phase A 详细版见 `UNI_SIGN_REAL_E2E.md`，
Phase C 详细版见 `GLOSS_FREE_REPO_BRINGUP_AND_EVAL.md`

# Phase A — Uni-Sign 真实本地端到端验证

## 一句话结论

**真实 checkpoint 已下载、校验通过、挂载进容器，`/healthz`、`/readyz`（200，模型真实加载成功）、`/translate` 全部用真实 HTTP 请求验证通过，短视频和长视频各跑出了一条真实的、checkpoint 支撑的英文翻译文本。9.17 报告中 PARTIAL 的 b1（本地部署验证），从"本地 E2E 是否跑通"这个角度，现在可以判定为 **COMPLETE**。** b2（ACR 推送）仍未开始，按计划不受影响，许可证问题（CC BY-NC-4.0 非商用）依然存在，未解决，不受本次验证影响。

## 做了什么（均为真实操作，非模拟）

- Checkpoint `how2sign_pose_only_slt.pth` 从 Hugging Face 官方仓库重新下载，大小 1,186,925,007 字节、SHA256 与此前记录完全一致，两项都精确匹配。存放路径 `~/.cache/uni_sign_checkpoints/`，完全在所有 git 仓库之外（不是靠 .gitignore，是物理上不在任何仓库目录里），不可能被误提交；也确认了服务默认挂载路径本身也在 `.gitignore` 里。没有打进镜像。
- 用现有 Dockerfile 重新构建了 `linux/amd64` 镜像——**全部层命中缓存**，说明代码本来就没有漂移，没有改任何 curify-studio 代码。
- 启动容器，挂载真实 checkpoint（只读）+ HF 缓存，设置许可证确认环境变量：
  - `/healthz` → 200
  - `/readyz` → 200，`model_loaded: true`，模型加载耗时约 55 秒（含 mT5-base 下载 + 真实 checkpoint `torch.load` + **strict** state_dict 加载，零缺失/多余权重键，即架构完全匹配）
- 短视频（`1477_recording_6.7s.mp4`，6.68s，真实用户录制，无参考文本）→ `/translate` 返回 HTTP 200，真实生成文本：`"One, two, three; one, two, three; ..."`（重复约16次，在 `max_new_tokens=100` 处被截断）。耗时约 5 分钟（本机是 Apple Silicon，容器跑的是 amd64 模拟层，比原生慢很多，属预期）。
- 长视频（`1252_1000016397_76.8s.mp4`，77.5s，真实用户录制，**这条视频之前在 Curify 自己的生产翻译流程里就失败过**）→ `/translate` 返回 HTTP 200，真实生成文本：`"One, two, three, four. One, two, three, four. ..."`（重复约12.5次，同样被截断），耗时约 25.5 分钟。该视频有参考字幕（11行、6句话），但这份参考本身在项目自己的审计里被标注为"非独立、循环引用"（Curify 自己翻译后又拿来对比自己），仅供定性参考，不作为准确率基准。定性对比：模型输出完全没有覆盖参考里的任何一句话或两个指式拼写的人名。

## 两个关键技术事实（代码直接确认，非猜测）

1. Uni-Sign 自己不产出时间戳。API 返回里的 `segments[0].start/end` 是服务包装层自己拼的（start 永远 0，end 永远整段视频时长），不是模型输出——这点短视频和长视频的返回结果里都体现了。
2. 长视频预处理路径（代码里直接确认）：姿态提取阶段处理了全部 2283 帧，不跳帧；但下游 `max_length=256` 这一步，因为 2283 > 256，会**随机**抽取 256 帧（约11.2%），不是均匀间隔抽样，而且这个随机种子只在模型加载时设置一次，不是每次请求重新设置。再加上 `max_new_tokens=100` 这个输出长度上限对短视频和长视频完全一样——这两点合起来，直接导致了长视频"只输出一段循环短语、丢失几乎所有句子内容"的结果。

## Phase A 下一步

Phase A 到此结束，未实现任何分段（segmentation）方案，未开始新的 gloss-free 仓库（Phase C），未 commit、未 push、未推 ACR。长视频这次暴露的"随机抽帧丢内容 + 固定输出长度上限"问题，将作为 Phase B 的证据基础，本次不处理。

---

# Phase C — `gloss-free-asl-translation` 调通与评估

详细版见同目录 `GLOSS_FREE_REPO_BRINGUP_AND_EVAL.md`。分类结论：**B —
调通完成，评估被阻塞**（代码/环境/MediaPipe提取/数据管线/模型构造全部真实跑通，
但没有可用的、训练好的 ASL 翻译 checkpoint，所以没有跑真正的翻译评估，也没有编造）。

## 问题回答

- **我们是不是 MediaPipe？** 不是。我们现在用 `rtmlib.Wholebody()`（RTMDet-tiny +
  RTMW-l，COCO-WholeBody 133 点），代码里从未 import 过 `mediapipe`。
- **新 repo 用什么？** MediaPipe Holistic（`mp.solutions.holistic`），pose 33 + 左右手
  各 21 + 脸部 468 点里精选的 92 点，直接喂给一个可训练的 Conformer 时序编码器（不经过
  任何文字化中间步骤），再通过 T5 解码器的 cross-attention 生成英文，架构上和我们的 D2
  （轨迹转文字给通用 Gemini）是完全不同的路线。
- **本地是否调通？** 调通到"依赖安装、单测通过（6/6 快速单测 + 4/5 慢速单测，唯一失败
  的1个和模型/MediaPipe无关，是合成测试视频的编解码器问题）、模型能真实构造并跑通
  `generate()` 调用"这一步。全程零改动上游被跟踪的代码。
- **MediaPipe landmarks 是否成功提取？** 成功，在 Phase A 同一条真实本地视频
  （`1477_recording_6.7s.mp4`）上跑通，167帧全部处理，pose/face 100%检测率，
  耗时7.64秒（接近实时），即使本机是通过 Rosetta 模拟跑的 x86_64 版本依赖也是如此。
- **模型是否能构建？** 能。Conformer + 真实预训练 T5-small 解码器 + Gated Multimodal
  Fusion，共6717万参数（其中4163万是真实预训练T5权重），构造和推理调用全部真实跑通。
- **有没有训练好的 ASL translation checkpoint？没有。** 仓库内、GitHub Releases
  （查证为0个）、tags（0个）、代码里所有可能的 HF/Drive/Kaggle 链接全部查过，唯一真实
  存在的权重是从未在任何手语数据上训练过的通用预训练T5。README 的 Results/Demo 两节
  原文就是占位符（"训练完成后补充"），仓库最后一次 push 是2026-07-01，两个半月没更新。
- **是否真正跑了 evaluation？没有，也没有编造。** 因为没有真实 checkpoint，官方
  `scripts/evaluate.py` 强制要求本地 checkpoint 目录（`model.safetensors` 或
  `pytorch_model.bin`），该目录不存在。本session额外做了一次工程性质的管线验证
  （非评估）：真实提取的 landmarks 喂给"未训练编码器+真实预训练T5解码器"跑通了
  `generate()`，输出是预期中的无意义重复token，只用来证明管线机械上通了，不是翻译结果。
- **具体 blocker 是什么？** 没有任何地方发布过这个架构在 MediaPipe landmarks 上训练好
  的真实 checkpoint。训练代码本身是真实可运行的（Kaggle notebook + `src/train.py`），
  但需要真正跑一次完整的 Kaggle GPU 训练（本session明确不允许启动），且作者自己也从未
  把训练产出的 checkpoint 发布回这个仓库。
- **和我们之前 trajectory 实验的关系？** 不矛盾，不能互相验证，也不能说新 repo 已经被
  验证有效。我们自己的 D2 报告原文写得很清楚："没有测试、也没有排除"一个专门训练的时序
  编码器直接消费轨迹特征这条路径——而这正是新 repo 的架构。D2 的 0/5 负结果范围严格限定在
  "轨迹转文字给通用冻结 Gemini"这一条路径上，不能拿来推翻或证明新 repo 这条完全不同的
  技术路线。

## Phase C 下一步

未开始 Phase B（重叠分段），未开始真正的 Kaggle 训练，未 commit、未 push，未修改
`curify-studio` 任何代码。
