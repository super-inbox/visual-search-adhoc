# Uni-Sign FastAPI 部署 — 工作报告

- 日期: 2026-09-17
- 涉及仓库:
  - ASL 研究/评测仓库: `/Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c`
  - 部署仓库: `/Users/baobaoli/Desktop/curify-studio`（分支 `baobao/asl-unisign-fastapi-service`）
  - 参照基线仓库: `/Users/baobaoli/Desktop/curify-studio-clean`（`main` 分支，无 `uni_sign_server`，仅作 diff 基线）
- Draft PR: https://github.com/super-inbox/curify-studio/pull/448
- 已核实的最新部署修复提交: `54259128e8f10b21cd640cc848b0c470064a5235`（"fix(asl): make Uni-Sign Docker build reproducible"）

本报告的所有结论均基于对两个仓库 git 历史、PR #448 元数据、`uni_sign_server/` 源码、已存在的构建日志、以及**此前实现会话的完整持久化会话记录**（`~/.claude/projects/-Users-baobaoli-Desktop-curify-studio/*.jsonl`，包含真实 `docker run`/`curl`/`docker exec` 命令与其真实输出）的直接检查，不涉及新实验、不下载 checkpoint、不调用付费 API、不修改部署代码。

> **修正说明（第二版）**：本报告初版遗漏了对上述持久化会话记录的检索，仅检查了临时 scratchpad 目录（只含构建日志），因此严重低估了实际已完成的容器验证工作。经用户指出并补充检索后，已在 PART 2 / PART 3 / PART 7 / PART 8 中做出修正，具体差异见文末 git diff。

---

## PART 1 — Manager 需求还原

在 ASL 仓库中未找到任何专门针对本次 FastAPI 部署任务的书面需求文档（`docs/daily_report/` 下与本任务同期的文档，如 9.15 的 `ASL_COMPLETE_WORK_REPORT.md`（commit `6328310`）和 `unisign-inference-parameter-audit/README.md`（commit `2388d96`），内容均属于评测/基准工作流，不涉及 FastAPI、xtts_server 模式、Docker 或 ACR）。

因此，manager 的部署需求只能从 curify-studio 分支 `baobao/asl-unisign-fastapi-service` 的实际产出（代码结构、PR 描述）反推还原，具体对应关系如下：

| # | Manager 需求（简报所列） | 是否有实现证据 |
|---|---|---|
| 1 | Uni-Sign 是替代/补充现有 Gemini 逐帧 ASL 路径的候选方案 | 间接支持：PR body 与 README 均以"候选服务"口吻描述，未见与 Gemini 路径的直接集成代码 |
| 2 | 在 curify-studio 新增 Uni-Sign FastAPI service | 已实现，见 PART 2 |
| 3 | 创建与 `xtts_server` 同级的根目录 | 已实现：`uni_sign_server/` 位于仓库根级 |
| 4 | 遵循 xtts_server 部署模式（Dockerfile / FastAPI app / local service / model loading / API request-response） | 结构性对齐已确认，见 PART 2 第 4 节 |
| 5 | 先本地验证部署/API：video upload → Uni-Sign 结果 | **部分完成** — 容器已真实启动，`/healthz`/`/readyz`/`/translate` 均已通过真实 HTTP 请求验证，真实视频的 pose extraction 已在容器内验证成功；唯独真实 checkpoint 加载与真实翻译输出未完成，见 PART 3 |
| 6 | 创建/更新 PR | 已完成：PR #448（Draft） |
| 7 | 后续将 Uni-Sign Docker 镜像推送到 ACR | 未开始（本任务明确要求不执行） |
| 8 | 回答：Uni-Sign 是否自带时间戳分段？之前 Frame Inspector/benchmark 流程是先切片后跑模型，还是整段跑完再切分？并给出样例输出 | 前两问已有明确答案（见 PART 6）；"样例输出"因未跑通真实推理，暂无法提供真实样例 |
| 9 | Follow-up：checkpoint 来源？参数量与磁盘/checkpoint 大小？ | 已核实，见 PART 4、PART 7 |

---

## PART 2 — 实际完成情况审计（curify-studio）

### 分支与提交状态

- 当前分支：`baobao/asl-unisign-fastapi-service`
- `git status`：**tracked 文件干净**；存在一个与本任务无关的未跟踪目录 `_local_research/zero-prompt-creative-workflow-exploration/`（另一项研究任务的残留，非本次部署工作产物）
- 提交历史（相对 `main` 的 3 个提交）：
  1. `7b3fa5b` — merge base into main
  2. `0fc3b4e` — feat(asl): add Uni-Sign FastAPI service
  3. `54259128e8f10b21cd640cc848b0c470064a5235`（短 SHA `5425912`）— fix(asl): make Uni-Sign Docker build reproducible，提交时间 2026-09-16 23:51:57 -0500
- **推送状态**：`git ls-remote origin` 确认 `origin/baobao/asl-unisign-fastapi-service` HEAD 与本地 HEAD 完全一致（均为 `54259128e8f10b21cd640cc848b0c470064a5235`）— 最新修复已推送。

### PR #448 状态

- 状态：**OPEN, isDraft = true**
- `head: baobao/asl-unisign-fastapi-service` → `base: main`
- PR 上的提交列表 = `0fc3b4e`, `54259128e8f10b21cd640cc848b0c470064a5235` — **与本地/远端 HEAD 完全一致**，最新修复已包含在 PR 中。
- PR body 中明确记录的关键信息：
  - 锁定的上游 Uni-Sign commit：`eed438bcb49e30405cd6ccdfcccca330c134e830`
  - checkpoint 文件与哈希：`how2sign_pose_only_slt.pth`，sha256 `1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d`（经本次审计独立核实为合法 64 位十六进制哈希）
  - 许可证阻断：CC BY-NC-4.0，非商用
  - 未推送 ACR
  - 时间戳为 wrapper 派生（`start=0.0`，`end`=ffprobe 时长），非 Uni-Sign 原生输出
  - PR 中"本地验证"一节列出：patch 可干净应用、真实 import、真实 pose extraction（28 帧 × 133 关键点）、真实 `Uni_Sign(rgb_support=False)` 构造（mT5 被 mock）、TestClient 路由检查、dummy checkpoint 的 sha256 不匹配 → `torch.load()` 失败路径测试
  - PR body 明确写"Local validation completed (**no Docker build run**)"

  **⚠️ 需要指出的偏差（比第一版报告的判断更严重）**：PR body / README 中"未跑过 Docker build""real translation output... not validated"的表述**大幅低估**了实际完成的验证工作。经检索持久化会话记录（见 PART 3），实现者当晚不仅成功构建了镜像，还**真实启动了多个容器**，通过真实 HTTP 请求完整测试了 `/healthz`、`/readyz`（三种状态）、`/translate`（真实 How2Sign 视频），并在容器内用 `docker exec` 真实运行了 `pose_extraction()`。这些工作全部发生，但从未被写回 PR body 或 README —— 换言之，问题不是"文档夸大了成果"，而是"文档遗漏了已完成的成果"。建议在关闭任务前用 PART 3 的真实验证结果更新 PR/README，这样 manager 和下一位接手的工程师才能看到实际的完成度。

### `uni_sign_server/` 目录内容

文件清单：`.gitignore`、`Dockerfile`（58 行）、`README.md`（298 行）、`app/main.py`（141 行）、`app/unisign_bridge.py`（208 行）、`patches/unisign_cpu_and_mt5path.patch`（61 行）、`requirements.txt`（32 行）。

**FastAPI 路由**：
- `GET /` — 基本信息
- `GET /healthz` — 存活探针，**不触碰模型**
- `GET /readyz` — 就绪探针，惰性加载模型；失败时返回 503 及详情
- `POST /translate` — multipart `video` 字段上传；错误路径覆盖：415（错误 content-type）、400（空/不可读视频）、503（模型不可用）、500（推理失败）

**模型加载**：`unisign_bridge.get_model()` 实现带线程锁的惰性单例加载。

**checkpoint 路径处理**：环境变量 `UNISIGN_CHECKPOINT_PATH`，默认 `/app/checkpoints/how2sign_pose_only_slt.pth`；**代码中从不自动下载**，必须由运维方挂载卷。

**许可证确认门控**：环境变量 `UNISIGN_NC_CHECKPOINT_LICENSE_ACK` 必须等于 `"1"`，否则抛出 `LicenseNotAcknowledgedError` → 503，错误信息中引用 CC BY-NC-4.0。

**SHA256 校验**：代码中会计算并与 `UNISIGN_CHECKPOINT_SHA256`（值同上）比对，**但不匹配时仅记录 warning，不阻断加载**——这是一个需要向 manager 说明的细节：checkpoint 完整性目前不是强制校验。

**响应 JSON 结构**：
```json
{
  "model": { "...": "..." },
  "translation": "<str>",
  "segments": [
    {
      "start": 0.0,
      "end": "<ffprobe 得到的整段视频时长>",
      "text": "<translation>",
      "source": "wrapper_derived",
      "note": "start/end are NOT produced by Uni-Sign..."
    }
  ]
}
```
代码中确认 Uni-Sign 自身的 `generate()` 只返回一个解码后的字符串，没有原生时间戳（详见 PART 6）。

**锁定的上游 commit**：`eed438bcb49e30405cd6ccdfcccca330c134e830`（Dockerfile 的 `UNISIGN_REPO_COMMIT` 与 bridge 默认值一致）。

**worker 数**：Dockerfile CMD 显式指定 `--workers 1`，文档说明原因：模型是进程内单例，每 worker 约占用 3.5GB 显存/内存，无跨 worker 协调机制 — 与 `xtts_server` 的约束一致。

**patch 内容**：5 行有效改动（`config.py` 的 `mt5_path` 支持通过 `UNISIGN_MT5_PATH` 环境变量覆盖；`demo/online_inference.py` 的设备放置逻辑）。

**`.gitignore`**：显式排除 `*.pth`、`*.bin`、`*.onnx`、`*.safetensors`、`checkpoints/`、`models/`、`pretrained_weight/`、`unisign_repo/` — checkpoint 与 vendored 上游仓库从不被提交。

### xtts_server 模式对齐

`xtts_server/` 结构为 `Dockerfile` + `README.md` + `app/main.py` + `requirements.txt`（无需 `patches/`）。`uni_sign_server/` 在此基础上额外拆出 `app/unisign_bridge.py`（模型逻辑独立）与 `patches/`（因上游 Uni-Sign 需要 CUDA/路径相关的补丁，xtts_server 不需要）。结构性对齐（惰性单例加载、`/healthz`+`/readyz` 分离、单 uvicorn worker、tempfile 上传后清理）已在 PR body 中被明确说明为有意模仿的模式。

---

## PART 3 — 本地部署验证状态

> **本节为第二版修正内容。** 第一版报告仅依据"临时 scratchpad 目录中只有构建日志、当前 `docker ps -a` 为空"这一不完整证据，严重低估了实际完成的容器验证工作。经检索持久化会话记录 `~/.claude/projects/-Users-baobaoli-Desktop-curify-studio/{8bded738...,7a928579...}.jsonl`（这两个 session 的完整对话记录，不同于只保留少量后台命令输出的临时 scratchpad），确认**容器实际上被完整启动、通过真实 HTTP 请求测试过，且已被验证后清理**。当前 `docker ps -a` 为空只说明"现在没有残留容器"，不能反推验证工作没有发生过——这是第一版的方法论错误，特此更正。

明确区分四个层次，**不要混淆**：

| 层次 | 是否验证 | 证据 |
|---|---|---|
| A. Docker/FastAPI 服务本身能否构建/运行 | **是**（构建成功 + 容器真实启动运行） | 见下 |
| B. video/pose 路径是否工作 | **是**（真实容器内、真实 HTTP/`docker exec`、真实视频） | 见下 |
| C. 模型构造（model construction）是否工作 | **是**（容器内 `Uni_Sign(args=args)` 真实构造成功，使用真实 mT5，非 mock） | 见下 |
| D. 真实 checkpoint 推理是否工作 | **否** | 仅挂载了 22 字节的 dummy checkpoint；`torch.load()` 在读取该文件时失败；从未加载真实 `how2sign_pose_only_slt.pth` |

### 完整的容器验证时间线（均为真实命令 + 真实输出，非模拟）

**1. 构建**：`docker build --platform linux/amd64 -t uni-sign-local:test .`，108 秒，`BUILD_EXIT_CODE=0`，镜像 646MB（内容层）。（此前一次不指定平台的构建因 `torch==2.1.1+cpu` 在 arm64 主机上无匹配 wheel 而失败，之后改用显式 `--platform linux/amd64` 成功。）

**2. 第一次容器测试**（`docker run -d --name uni-sign-test --platform linux/amd64 -p 8000:8000 uni-sign-local:test`）：
- 容器日志：`INFO: Application startup complete.` `Uvicorn running on http://0.0.0.0:8000`
- `GET /` → `200` `{"service":"uni-sign","status":"running","version":"1.0.0"}`
- `GET /healthz` → `200` `{"status":"ok"}`
- `GET /readyz`（未设置 license ack）→ `503` `{"detail":"...CC BY-NC-4.0...Set UNISIGN_NC_CHECKPOINT_LICENSE_ACK=1..."}`
- 清理：`docker stop uni-sign-test && docker rm uni-sign-test`

**3. 第二次容器测试**（新容器 `uni-sign-test-ack`，设置 `UNISIGN_NC_CHECKPOINT_LICENSE_ACK=1`，未挂载 checkpoint）：
- `GET /readyz` → `503` `{"detail":"Checkpoint not found at /app/checkpoints/how2sign_pose_only_slt.pth..."}`
- `POST /translate`，真实上传 How2Sign 视频 `g3sLd8JupoQ_14-3-rgb_front.mp4`（821,878 字节）→ `503` `{"detail":"Model not ready: Checkpoint not found..."}` —— **确认真实 multipart 上传 + 就绪状态门控在真实 HTTP 路径上完整工作**，只是因缺少真实 checkpoint 而在就绪检查这一步被正确拦截。
- 清理：`docker stop/rm uni-sign-test-ack`

**4. 第三次容器测试**（新容器 `uni-sign-test-full`，license ack + 挂载 22 字节假 checkpoint + 挂载真实 mT5 HF 缓存）：
- `GET /readyz` → `503` `{"detail":"invalid load key, 'n'."}`
- 容器日志显示完整顺序：先记录 `WARNING: Checkpoint sha256 mismatch: expected 1bfd5f33...fb00d, got 11e66f1e...f347. Proceeding anyway`（非致命，符合 PART 2 中"sha256 不匹配仅警告不阻断"的代码逻辑），随后在 `torch.load(UNISIGN_CHECKPOINT_PATH...)` 读取假文件时因文件不是合法 pickle/zip 而失败。
- **关键点**：核对 `unisign_bridge.py` 源码，`Uni_Sign(args=args)` 的真实模型构造发生在 `torch.load()` **之前**（先构造模型架构，再加载权重）。因此能走到"`torch.load()` 读取假文件失败"这一步，就已经反向证明了**容器内真实 `Uni_Sign(args=args)` 架构构造（含真实 mT5，非 mock）已经成功完成**——这是唯一未跨过的门槛就是"真实权重文件"本身。

**5. 第四次容器测试**（新容器 `uni-sign-pose-test`，license ack + 挂载真实 How2Sign 视频目录 + 挂载真实 rtmlib 姿态模型缓存）：
- `docker exec` 直接调用 `online_inference.pose_extraction('/data/videos/g3sLd8JupoQ_14-3-rgb_front.mp4')`
- 输出：`POSE_EXTRACTION_OK frames= 137 kp_shape= (1, 133, 2) seconds= 6.71` —— **容器内真实姿态提取，对真实视频，产出真实关键点数据**。

**6. 清理与重建**：所有测试容器 `docker stop`/`docker rm`；旧镜像 `docker rmi`；随后应用 Dockerfile 修复（`python:3.9-slim` → `python:3.10-slim` + `requirements.txt` 版本锁修正）并重新构建（`docker_rebuild.log`，缓存命中，成功）——对应 fix commit `5425912`。

**7. Fix commit 之后的最终冒烟测试**（另一会话，23:51 commit 之后）：新容器 `unisign-verify`，`GET /healthz` → `200` `{"status":"ok"}`，`GET /readyz`（无 ack）→ `503`（CC BY-NC-4.0 消息）。**确认修复后、当前分支实际使用的镜像同样能真实启动并正确响应。**

### 结论

A、B、C 三个层次**均已通过真实容器 + 真实 HTTP/`docker exec` 验证**，不是仅靠 TestClient 或函数级 mock。**唯一真正未跨过的门槛是 D**：由于从未获取/挂载过真实的 `how2sign_pose_only_slt.pth`，因此**真实 checkpoint 支撑下的 `/readyz` 成功响应（200）与真实 Uni-Sign `/translate` 翻译输出，二者均尚未得到验证**。这与第一版报告严重低估容器验证完整度的结论有实质性差异，务必以本节为准。

---

## PART 4 — Checkpoint 溯源

目标文件：`how2sign_pose_only_slt.pth`

- **当前是否存在于本地磁盘**：ASL 仓库中 `find` 未找到该文件，当前不存在于本地工作区。
- **是否曾提交到 Git 树中**：否。全仓库 git 历史检索无命中，未使用 Git LFS，从未作为二进制文件提交。
- **历史来源**：`docs/daily_report/8.31/asl-next-baseline/SECOND_BASELINE_CANDIDATES.md`（第 110–114 行）记录了通过 `curl` HEAD 请求验证的官方 Hugging Face 来源：
  `https://huggingface.co/ZechengLi19/Uni-Sign/resolve/main/how2sign_pose_only_slt.pth`
  即该文件是**此前的评测工作自行从 Hugging Face 官方仓库下载**的，**没有证据表明 checkpoint 是 manager 本人提供的**。
- **预期文件大小**：1,186,925,007 字节（约 1.19GB），通过 `curl -sIL` HEAD 请求确认。
- **预期 SHA256**：`1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d`（记录于 `docs/daily_report/9.2/asl-baselines/results/run_metadata.json` 第 59 行；本次审计独立验证为合法 64 位十六进制字符串，且与 curify-studio 的 PR body/README/`unisign_bridge.py` 中记录的哈希**完全一致**，跨仓库交叉印证）。
- **许可证**：CC BY-NC-4.0（研究/评测用途，非商用）。
- **为什么此前的 benchmark 能跑通，而今天文件却不存在**：checkpoint 被下载到此前某次会话的 scratchpad 路径（`<scratchpad>/unisign_run/checkpoints/how2sign_pose_only_slt.pth`）以及一个现已不存在的 conda 环境（`unisign-cpu-arm64`），当时所在的机器/会话环境目前已不可用。二进制文件按设计从未被提交进 git（`.gitignore` 中相应排除项与 curify-studio 侧的排除逻辑一致），因此文件"消失"是预期行为，不是丢失事故。

**重要澄清**：不应描述为"checkpoint 从 GitHub 丢失"（它从未被提交到 GitHub），也不应描述为"manager 亲自发送过这个文件"（没有证据支持后者）。

---

## PART 5 — 真实用户视频状态

- 位置：`asl-translator/data/asl_corpus/videos/`
- 总数：13 个视频文件（`corpus_inventory.csv` 含表头共 14 行）
- 已核实存在的两个候选冒烟测试视频：
  - `1474_1000004432_11.5s.mp4` ✅ 存在
  - `1477_recording_6.7s.mp4` ✅ 存在
- 根据仓库内已有的 `VIDEO_TYPE_AUDIT.md`：13 个中 12 个确认为真实 ASL 内容（`1457` 存疑/不确定），另有两个已知瑕疵需注意：`1434` 是屏幕录制的 YouTube 视频而非第一人称用户提交内容；`1466`/`1467` 打手语者的头部被裁切出画面。
- 这些视频与 How2Sign 公开基准片段**明确不同**：存放目录不同（`asl_corpus/` vs `public_benchmarks/how2sign/`），命名规则也不同（Curify 用户提交 ID vs How2Sign 标准片段 ID）。
- 本报告未复制、未展示、未发布任何私有用户视频内容，仅确认路径存在性。

推荐冒烟测试用视频（若获得 checkpoint 后要做真实 E2E 验证）：优先用 `1477_recording_6.7s.mp4`（时长最短，约 6.7 秒，适合最快验证链路是否打通），随后用 `1474_1000004432_11.5s.mp4` 做第二轮验证。

---

## PART 6 — 时间戳 / 分段问题的精确回答

### Uni-Sign 本身是否返回带时间戳的句子分段？

**不返回。** 根据已有的 `unisign-inference-parameter-audit`（锁定的上游 commit `eed438bcb49e30405cd6ccdfcccca330c134e830`）对源码的直接检查：`generate()`（`models.py:313-321`）只接受并转发 `max_new_tokens` 和 `num_beams` 两个参数，返回值是单个解码后的字符串。调用链中任何位置都**没有**时间戳、句子边界、帧-token 对齐或置信度输出。调用方（`demo/online_inference.py:125-127`、`fine_tuning.py:263-265`）使用硬编码的 `num_beams=4, max_new_tokens=100`。

### 之前的 Frame Inspector / benchmark 流程：先切片还是整段跑完再切分？

**先切片。** How2Sign v2 使用的片段（如 `how2sign_v2_batch2_10clip/clips/` 下的目录名 `FZCEymcpq7I_14-1-rgb_front` 等）遵循 How2Sign 标准的**预切分句子级片段**命名规则（视频ID_句子序号-摄像机位）。Uni-Sign 通过 `batch_inference_cpu_patched.py` 遍历 manifest，**对每个预切分片段单独调用一次推理**（命令行证据见 `run_metadata.json` 第 84 行：`--manifest_csv how2sign_v2/manifest.csv --videos_root how2sign_v2/videos`）。仓库中**没有任何证据**支持"整段长视频跑一次推理，再对输出做后处理切分"这种流程。

### 当前 API 的 `segments` 字段语义

在 `uni_sign_server/app/unisign_bridge.py` 中：
- `start` 固定为 `0.0`
- `end` 是通过 `ffprobe` 读取的**整个输入视频的总时长**
- `text` 是模型对整段视频的翻译结果
- `source` 字段显式标注为 `"wrapper_derived"`
- 代码中附带一条 `note` 字段，明确写明"start/end are NOT produced by Uni-Sign"

**必须非常明确地说明**：这个 `segments` 字段是服务包装层（wrapper）为了满足下游 API 契约人为构造的"伪分段"（整段视频作为唯一一个 segment），**不是** Uni-Sign 模型原生的时间对齐能力，不能被下游误读为"Uni-Sign 支持句子级时间戳定位"。

---

## PART 7 — 模型 / Checkpoint 大小汇总

| 系统 | 模型类型 | 参数量 | 本地 checkpoint/模型大小 | 是否专有/API |
|---|---|---|---|---|
| Curify / Gemini 3.6 | 专有多模态 LLM API | 未知（专有，无法本地审计） | 不适用（无本地 checkpoint） | 是，API |
| Uni-Sign How2Sign pose-only | Pose-only SLT 模型 | **⚠️ 约 5.869 亿（586.9M）— 本次审计在 curify-studio 与 ASL 两个仓库中均未检索到独立审计证据支持这一数字，建议在正式引用前进一步核实来源** | `how2sign_pose_only_slt.pth`，1,186,925,007 字节 ≈ **1.187GB / 1.105GiB**，sha256 `1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d`，CC BY-NC-4.0，pose-only checkpoint | 否（开源权重，非商用许可证） |
| OpenSLT | Fairseq-based SLT baseline | 见下方专门说明 —— **raw: 11,746,819**（187 个 state_dict 条目原始求和）／**unique: 9,954,819**（去除 decoder 输入/输出权重绑定重复计数后） | `checkpoint.best_reduced_sacrebleu_3.5401.pt`，126,827,063 字节 = **0.127GB / 0.118GiB**，MD5 `52f2f55dca970d82c7ffe534fbfdec43` | 否 |
| SignCaption | 第三方 API（Sign-Speak） | 不适用（专有 API） | 不适用 | 是，API |

### OpenSLT 参数量口径澄清（两个数字都对，衡量的是不同口径）

任务简报假设的 9,954,819（"唯一参数"）与仓库既有审计文档 `OPENSLT_REPRODUCTION_PLAN.md:496` 记录的 11,746,819（"187 tensors total"）此前被误判为矛盾。本次用仓库中已有的本地 checkpoint 文件（`asl-translator/data/public_benchmarks/how2sign/openslt_checkpoint/checkpoint.best_reduced_sacrebleu_3.5401.pt`，只读加载，未下载任何新文件）重新验证，结论是：**两个数字都正确，只是统计口径不同**。

| 口径 | 数值 | 说明 |
|---|---|---|
| A. Checkpoint 原始 tensor 元素总数 | **11,746,819** | `state_dict` 里全部 187 个条目的 `numel()` 朴素求和（本次独立重跑验证，与既有审计文档完全一致） |
| B. state_dict tensor 条目数 | **187** | 同上 |
| C. 实例化模型的参数量（真实构建 fairseq 模型对象后统计） | 未在本次复核 | 需要完整搭建 fairseq task/model 才能拿到，超出"轻量级只读校验"范围，未执行 |
| D. 去重后的"唯一参数"量 | **9,954,819** | 见下方证据 |
| E. 差异的确切原因 | **decoder 输入/输出权重绑定（tied embedding）被重复计数** | 见下方证据 |

**证据（本次独立复核，读取仓库中已存在的本地 checkpoint 文件，torch.load 只读）**：
- `decoder.embed_tokens.weight` 与 `decoder.output_projection.weight` 两个 tensor，形状均为 `(7000, 256)`，各含 1,792,000 个元素。
- 两者在 state_dict 中是**两个独立的存储对象**（`data_ptr()` 不同），但**数值逐字节完全相同**（`torch.equal()` 返回 `True`）。
- 这正是 fairseq 经典的 `--share-decoder-input-output-embed` 权重绑定模式：概念上只有**一个**学到的参数矩阵，同时被用作输入词嵌入和输出投影层，但在这份 checkpoint 序列化时被展开成了两个数值相同的独立条目。
- 算术验证：`11,746,819 − 1,792,000 = 9,954,819`，与任务简报中的数字**精确吻合**。

**结论**：11,746,819 是对 187 个 state_dict 条目的朴素求和（未识别权重绑定，把同一个逻辑参数矩阵算了两遍）；9,954,819 是识别出 decoder 输入/输出权重绑定、只计一次之后的"唯一参数"数（这也应当就是真实例化 fairseq 模型对象、调用 `model.parameters()` 会得到的数字，因为 PyTorch 按对象身份去重——但本次未实际执行 C 项完整验证，措辞上仍标注为"未在本次复核中直接确认"）。**两个数字都可以放心引用，前提是标注清楚口径**：面向 manager 汇报时建议统一使用 **9,954,819（唯一参数，去重后）** 作为"模型有效参数量"，11,746,819 仅作为 checkpoint 文件层面的技术细节脚注。

---

## PART 8 — 当前完成矩阵

状态类型：`COMPLETE` / `PARTIAL` / `NOT STARTED` / `BLOCKED`

| # | 需求项 | 状态 | 证据 | 剩余动作 |
|---|---|---|---|---|
| 1 | `uni_sign_server` 目录 | COMPLETE | 目录已存在于根级，已提交并推送 | 无 |
| 2 | FastAPI 服务实现 | COMPLETE | `app/main.py` 四个路由完整实现 | 无 |
| 3 | xtts_server 模式对齐 | COMPLETE | 惰性加载/健康检查分离/单 worker/临时文件清理均已对齐 | 无 |
| 4 | Docker 构建 | COMPLETE | `docker_build_amd64.log` 显示构建成功，镜像 `uni-sign-local:test` 存在，fix commit 后已重建 | 更新 PR/README，去除"未跑过 Docker build"的过时表述 |
| 5 | 本地容器启动 | COMPLETE | 会话记录确认多次真实 `docker run`，容器日志显示 `Application startup complete`；fix commit 后另有一次独立冒烟测试确认可用 | 更新 PR/README 补充记录 |
| 6 | `/healthz` | COMPLETE | 真实容器 + 真实 HTTP：`GET /healthz` → `200 {"status":"ok"}`（fix commit 前后均验证过） | 无 |
| 7 | `/readyz` | PARTIAL | 真实容器 + 真实 HTTP 验证了三种失败路径（无 ack / ack+无 checkpoint / ack+假 checkpoint→`torch.load()`失败）；成功路径（真实 checkpoint）未验证 | 挂载真实 checkpoint，验证 200 成功路径 |
| 8 | 视频上传路径 | COMPLETE | 真实容器：`POST /translate` 携带真实 How2Sign 视频（821,878 字节）→ 正确走到 503 model-not-ready，证明 multipart 上传+就绪门控在真实 HTTP 路径上完整工作 | 无（获得真实 checkpoint 后即可看到端到端成功响应） |
| 9 | pose extraction | COMPLETE | 真实容器内 `docker exec` 运行 `pose_extraction()`：真实视频 → `POSE_EXTRACTION_OK frames=137 kp_shape=(1,133,2) seconds=6.71` | 无 |
| 10 | 真实 Uni-Sign checkpoint 加载 | BLOCKED | 真实容器内已验证到"`Uni_Sign(args=args)` 真实构造成功（含真实 mT5）→ `torch.load()` 读取 checkpoint"这一步，仅因挂载的是 22 字节假文件而在 `torch.load()` 失败；真实权重文件从未被加载过 | 获取真实 `how2sign_pose_only_slt.pth` 并挂载 |
| 11 | 真实 `/translate` 推理 | BLOCKED | 未发生 | 依赖 #10 完成后执行 |
| 12 | 真实用户视频冒烟测试 | NOT STARTED | 候选视频已确认存在（`1477_recording_6.7s.mp4`、`1474_1000004432_11.5s.mp4`） | 依赖 #10、#11 完成后执行 |
| 13 | 时间戳调研 | COMPLETE | 见 PART 6，源码级确认 | 无 |
| 14 | 既往 Frame Inspector 行为调研 | COMPLETE | 见 PART 6，命名规则+运行命令双重证据 | 无 |
| 15 | Checkpoint 溯源调研 | COMPLETE | 见 PART 4 | 无 |
| 16 | 样例输出 | BLOCKED | 无真实推理，无法提供真实样例；仅能提供 JSON *结构* 示例 | 依赖 #11 完成后提供真实样例 |
| 17 | Draft PR | COMPLETE | PR #448，OPEN，isDraft=true | 无 |
| 18 | 最新部署修复已推送 | COMPLETE | `git ls-remote` 确认远端/本地/PR 最新 commit 三方一致 | 无 |
| 19 | ACR 镜像推送 | NOT STARTED | 明确排除在本任务范围外，需 manager/许可证确认后才能做 | 等待许可确认 |
| 20 | Azure 部署（如需要） | NOT STARTED | 未见相关请求证据 | 视 manager 是否提出再定 |

---

## PART 9 — 总体结论

### b1（本地部署/API 验证：video upload → Uni-Sign 结果）

**B — PARTIAL**

理由：
- FastAPI 服务代码、路由、错误处理、xtts_server 模式对齐、Docker 镜像构建、**容器真实启动运行**、`/healthz`、`/readyz`（三种失败路径）、真实视频的 multipart 上传 + 就绪门控、真实容器内 pose extraction、真实（非 mock）`Uni_Sign(args=args)` 模型构造——**均已完成且有真实 HTTP/`docker exec` 证据**（详见 PART 3 修正后的完整时间线）。
- **b1 的剩余缺口，精确表述如下**：由于从未挂载过真实的 `how2sign_pose_only_slt.pth`，因此**真实 checkpoint 支撑下的 `/readyz` 成功响应（200）**与**真实 Uni-Sign `/translate` 翻译输出**，这两项均尚未得到验证。
- 按任务要求："Do not call b1 complete if no real checkpoint was loaded / no real Uni-Sign translation was produced through /translate" — 这两个条件仍然触发，因此不能判定为 COMPLETE。
- 与本报告第一版不同的是：现在 b1 唯一未完成的技术缺口被精确定位到"真实 checkpoint"这一个环节，而不是"容器/部署链路本身"——工程实现和验证的完整度实际上非常扎实，只差最后一步（获取并挂载受 CC BY-NC-4.0 限制的真实权重文件）。因此判定为 PARTIAL，且非常接近 COMPLETE。
- **范围说明**：以上"唯一缺口"的表述仅限定在 b1（本地部署/API 验证）自身的技术范围内，**不包含 b2（ACR 镜像推送）**。b2 是否完成取决于另一组独立条件（manager/许可证确认），与 b1 的技术缺口无关，详见下方 b2 小节——不应把"b1 只差最后一步"误读为"整个部署任务只差最后一步"。

### b2（ACR 镜像推送）

**NOT STARTED / BLOCKED**（与 b1 分开陈述，不与 b1 混合评级）

理由：镜像推送依赖 b1 的真实 checkpoint 推理验证先行完成，且需要 manager/许可证层面的明确许可（CC BY-NC-4.0 checkpoint 的使用范围需要确认）。本任务的安全范围也明确禁止在本次会话中执行 ACR 推送，因此 b2 目前处于阻塞状态，并非工程能力不足。

---

## PART 10 — 精确的下一步动作序列

容器启动、`/healthz`/`/readyz`失败路径、视频上传、pose extraction 均已验证完成（见 PART 3），无需重复。剩余路径只围绕"真实 checkpoint"这一个缺口：

1. 确认/获取官方 `how2sign_pose_only_slt.pth`（Hugging Face `ZechengLi19/Uni-Sign` 仓库）的使用许可，确认 CC BY-NC-4.0 许可证下这次本地部署冒烟测试是被允许的用途。
2. 下载后校验 SHA256 是否等于 `1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d`。
3. 用已构建好的镜像启动容器，将真实 checkpoint 挂载进去（`UNISIGN_CHECKPOINT_PATH`），设置 `UNISIGN_NC_CHECKPOINT_LICENSE_ACK=1`。
4. 确认 `/readyz` 返回 200（此前三种失败路径已验证，只差这一条成功路径）。
5. 向 `/translate` 提交一个已知的 How2Sign 片段（例如已在容器测试中用过的 `g3sLd8JupoQ_14-3-rgb_front.mp4`），确认返回结果与既往基准评测的翻译趋势一致。
6. 向 `/translate` 提交一个真实 Curify 用户短视频（建议先用 `1477_recording_6.7s.mp4`，时长最短）。
7. 记录真实的 JSON 响应（含真实 `translation` 文本），作为提供给 manager 的"样例输出"。
8. 更新 `uni_sign_server/README.md` 与 PR #448 描述，补全 PART 3 中已完成但未被文档记录的真实容器验证结果，并加上这一步的真实翻译输出。
9. **只有在** manager/许可证/权限三方面都确认之后，才进行镜像 tag 与 ACR 推送。

不在本次任务范围内追加新的 ASL 研究实验。

---

## PART 11 — Manager 消息草稿

### A. 现状同步（Slack 风格，中文）

> Uni-Sign 的 FastAPI 服务这边进展比较扎实：`uni_sign_server/` 目录按 xtts_server 模式搭好了，PR #448（Draft）是最新的。Docker 镜像已经真实构建并启动跑过，`/healthz`、`/readyz`、`/translate` 三个接口都用真实 HTTP 请求测过了，真实视频的姿态提取（pose extraction）在容器里也验证成功了，模型结构本身也真实构造成功过。目前唯一还没跑通的是最后一步：还没有拿到真实的 `how2sign_pose_only_slt.pth` checkpoint（CC BY-NC-4.0 许可，之前是从 Hugging Face 官方仓库下载的，不是您发的），所以还没有产出真实的翻译文本。等这一步打通，整个链路就算完全跑通了。ACR 推送按计划先不动，等这步和许可证都确认了再推进。

### B. Checkpoint 许可确认询问（中文）

> 想跟您确认一下：这次本地部署冒烟测试，能否使用官方 Hugging Face 上的 `how2sign_pose_only_slt.pth`（`ZechengLi19/Uni-Sign` 仓库，CC BY-NC-4.0 许可）重新下载来用？确认可以的话我就去下载校验、挂载进容器，跑一遍真实的视频翻译验证。

---

## PART 12 — Manager follow-up C：轨迹追踪方法追了多少个点？是否包含面部？

> 本节回答的是与本次 Uni-Sign 部署无关的独立追问（针对此前 `docs/daily_report/9.10/trajectory-tracking-feasibility/` 下 Phase D1 轨迹追踪 POC 的技术细节）。回答基于对 `asl-translator/asl-eval/trajectory_probe/` 下全部代码文件、一份真实 `landmarks.json`/`trajectory_summary.json` 产出、以及 D0/D1 阶段既有报告的直接检查，未运行新推理，未修改任何文件。**本节内容不影响本报告 PART 9 的 b1/b2 结论**，纯属信息性追问。

### 1. 追踪器与 schema

底层追踪器是 `rtmlib.Wholebody()`（RTMDet-tiny 检测 + RTMW-l 姿态模型，`lightweight` 模式），schema 是标准 **COCO-WholeBody 133 点**（`extract_trajectory.py` 中显式标注 `keypoint_schema: "coco_wholebody_133"`，与之前 Uni-Sign pose extraction 用的同一套 rtmlib/RTMPose 提取路径一致）。

### 2. 精确点数分解（源自 `keypoint_schema.py` 索引定义，逐条核对代码确认）

| 区域 | 点数 | 索引范围 | 原始提取/落盘？ | trajectory summary 是否使用？ |
|---|---|---|---|---|
| body 身体 | 17 | 0:17 | 是 | 是（部分：详见下） |
| feet 脚 | 6 | 17:23 | 是 | 否 |
| face 脸 | 68 | 23:91 | 是 | 否 |
| left hand 左手 | 21 | 91:112 | 是 | 是 |
| right hand 右手 | 21 | 112:133 | 是 | 是 |
| **总计** | **133** | 0:133 | — | — |

### 3. 关键结论（明确回答 manager 问题）

底层追踪器**每帧确实提取 133 个全身关键点，且确实包含脸部（68 点）和双手**——这一步是真实发生的，`landmarks.json` 里逐帧都存了全部 133 个点的坐标+置信度。

**但当前的轨迹分析层（`summarize_trajectory.py`）并没有使用全部 133 个点。** 逐行核对该文件，`ks.FACE_START`/`ks.FACE_END`/`ks.FEET_START`/`ks.FEET_END` 从未被引用；实际被读取切片的只有 `ks.BODY_START:ks.BODY_END`（body 区域）、`ks.LEFT_HAND_START:ks.LEFT_HAND_END`、`ks.RIGHT_HAND_START:ks.RIGHT_HAND_END`。也就是说，当前的量化 derived-feature 计算只覆盖 **body + 双手对应的区域（17+21+21=59 个点位）**，脸和脚被提取、落盘，但没有被消费。

### 4. 这 59 个点位的区域目前实际产出了什么（逐项对应代码，未列未验证项）

- **body 区域（17点）**：不是逐点等权使用——`_body_detected()` 只用"≥12/17 点置信度过阈值"判断 body 是否被检测到；其中 **nose + 左右肩** 这 3 个点被单独取出，作为"手相对身体高度分区"的参照线（见下）。
- **双手（各21点）**：是主要的信号来源——
  - 检测率：`_hand_detected()`，多数点过阈值即算检测到
  - 手部置信度分布：mean/median
  - 手腕轨迹（`left_wrist_trajectory`/`right_wrist_trajectory`，只取 body 区域里的 `LEFT_WRIST_IDX`/`RIGHT_WRIST_IDX` 两个点）
  - 手心质心轨迹（`_hand_center()`，21点加权质心）
  - 手腕速度、手心质心速度（`_velocity_stats()`）
  - 双手间距离（`two_hand_distance`）
  - 手相对身体高度分区（`hand_relative_to_body_band`，用手心质心 y 坐标与 nose_y/chest_y 比较）
  - 帧间跳变候选（`discontinuity_candidates`，自校准阈值，标记疑似检测跳跃，不是确认的身份切换）

### 5. 面部点的重要澄清：脸部 landmark 被追踪 ≠ 理解了 ASL 面部/非手动语法特征

必须区分这两句话：
- "脸部关键点被追踪"——**成立**，rtmlib 确实输出了 68 个脸部几何坐标点，且逐帧存进了 `landmarks.json`。
- "ASL 的面部/非手动语言特征被理解了"——**不成立**。`keypoint_schema.py` 文件头原文写明："No ASL-specific meaning is attached to any of this — these are the tracker's own generic anatomical landmark names, not gloss/handshape labels."

当前代码**没有**把这 68 个脸部坐标翻译成任何 ASL 非手动语法信号，例如：
- 眉毛动作对应的语法意义（如疑问句眉毛上扬）
- 嘴型/mouthing 模式
- 头部动作的语法标记
- 面部表情作为 ASL 句法/语义成分

另外要指出一个容易误读的命名：`trajectory_summary.json` 里有个字段叫 `face_or_above`，名字里带"face"，但它**不是**基于脸部 68 点计算的——代码里它是拿 body 区域里的单个点 `nose_y`（以及左右肩连线推算的 `chest_y`）当参照线，判断"手心质心的 y 坐标是否高于鼻子高度"，和脸部 mesh 完全无关。这个字段不能被当作"脸部数据被分析"的证据。

### 6. 此前 5-clip POC 的证据范围（引用 `PHASE_D1_RESULTS.md`，不做定性转定量的夸大）

- 5/5 clip 提取成功，累计 1,038 帧（`92V3oH63zbQ_5-1-rgb_front` 55 帧、`Fz-N1S0swh8_2-8-rgb_front` 54 帧、`-g0iPSnQt6w_0-1-rgb_front` 175 帧、`G19uBylwQww_1-2-rgb_front` 136 帧、`FzmL8SL6Bow_1-8-rgb_front` 618 帧）。
- **量化的追踪质量指标（missing-tracking %、mean/median confidence）只报告了 body / left-hand / right-hand 三项**（见该报告第4节表格），脸和脚**没有**对应的量化指标。
- 脸部关键点仅在**唯一一段**全骨架 overlay 视频（`render_overlay.py` 把全部133点交给 rtmlib 的 `draw_skeleton` 绘制）及 4 个静态截图里做过**人工目检**（"skeleton lines on the actual shoulders/arms, face landmarks on the actual face"）——这是一次性的可视化 QA 观察，**不是**可复现的量化验证结果，不应被当作"脸部追踪质量已验证"的依据。

### 7. 对现有研究结论的影响（范围严格限定，不重新评价 D2）

已有的 Phase D2 负结果——"把轨迹信息转成结构化文字附加给通用 Gemini prompt，在这 5 个 clip 上没有恢复出语义（0/5）"——这个结论本身不变。

但**这个负结果不能被解读为"面部/非手动信息没用"**，因为当前的轨迹分析代码从未真正总结或提取过脸部关键点轨迹，D2 测试的输入里根本不包含任何脸部/非手动派生特征。也就是说，D2 检验的是"手部轨迹文字化对 Gemini 有没有帮助"，不是"面部非手动特征对 Gemini 有没有帮助"——后者目前完全没有被测试过。这是当前轨迹研究工作的一个明确局限，需要向 manager 说明，不能默认已经排除。

**未来可能的方向（仅作为方向提示，非已完成工作，本报告不提议或执行新实验）**：如果轨迹追踪这条线继续推进，一个可能的扩展是显式地从已经提取出来的 68 个脸部关键点（以及已存在但未使用的脚部 6 点）中派生出面部/头部/非手动特征（例如眉毛垂直位移、头部姿态角度变化等几何量），再评估这些特征是否对下游任务有帮助——这属于**未来工作（future work）**，本次未设计、未实现、未验证。

---

*本报告基于对 curify-studio（分支 `baobao/asl-unisign-fastapi-service`）、curify-studio-clean、以及本 ASL 仓库既有文档的直接检查生成，未运行新实验、未下载 checkpoint、未调用付费 API、未修改任何部署代码、未提交/推送任何改动。*
