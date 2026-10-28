# 任务一 防重复配对解码结果（Baobao，2026-10-27）

接续 [THREE_P0_EXECUTION_REPORT.md](THREE_P0_EXECUTION_REPORT.md) 任务一，协议见 [PROTOCOL.md](../../experiments/p0-2026-10-27/PROTOCOL.md) §C。状态：**可运行，已得诊断信号；没有翻译质量提升结论。** 人工语义标签全部 pending。45 例是开发诊断集，本轮未调参。

## 本次改动

- 未修改 `decode_repetition.py`、`PROTOCOL.md`，也未覆盖原 `results/repetition_preflight.json`（老板机器的 BLOCKED 记录保留）。
- 新增 `run_repetition_cpu.py`：只加防护的启动器。隐藏 CUDA/MPS；启动前核对 45 例恰为 R01–R45、全部 A_official，并运行 P0-16 holdout guard（H18/H19 排除）；把 transformers `generate` 包成透传函数，每次调用断言所有参数和输入张量在 CPU，并记录调用参数和耗时。不改任何解码参数。
- 新增 `score_repetition.py`：指标逐字复制 P0-A 冻结定义（`headroom_oracle.py`，§1.4/§1.6）。三个分箱阈值在读取 treatment 输出前固定：Δ句 chrF ±5、变短 ≤0.75×、触顶 100 token 且无 EOS。仅供人工复核分流。

## 实际执行命令

```bash
# 预检（PASS）及另行的只读补充检查（模型输入哈希 45/45、holdout guard、P0-12 CHECKSUMS 45/45）
/opt/anaconda3/envs/unisign-cpu-arm64/bin/python -I asl-translator/experiments/p0-2026-10-27/decode_repetition.py ... --preflight-only

# 配对解码（CPU，4 线程）
/opt/anaconda3/envs/unisign-cpu-arm64/bin/python -I asl-translator/experiments/p0-2026-10-27/run_repetition_cpu.py \
  --unisign /Users/baobaoli/Desktop/curify/p014-work/Uni-Sign \
  --checkpoint /Users/baobaoli/.cache/uni_sign_checkpoints/how2sign_pose_only_slt.pth \
  --mt5 /Users/baobaoli/.cache/huggingface/hub/models--google--mt5-base/snapshots/2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f \
  --pose-dir docs/daily_report/10.06/asl-p0-12-unisign-pose-gap/artifacts/prepared_inputs/A_official/test-pose-rtmpose-192 \
  --out asl-translator/experiments/p0-2026-10-27/results/repetition_paired_decode_local_arm64.json

/opt/anaconda3/bin/python3 -I asl-translator/experiments/p0-2026-10-27/score_repetition.py
```

第一次启动在加载模型前就被启动器自身的检查拦下：canonical 文件按 focus 案例优先排序，不是 R01→R45 顺序。改为按排序后比较，与预检一致。该次未生成任何输出。

## 输入和模型版本

Apple arm64，conda `unisign-cpu-arm64`（Python 3.10.13，torch 2.1.1，transformers 4.40.0）。Uni-Sign `eed438bc`（工作区仅有 `__pycache__`）。checkpoint SHA256 `1bfd5f33…fb00d`。mT5 snapshot `2eb15465…`。45 个 A_official pose，文件哈希及模型输入张量哈希与 P0-A canonical 全部一致（`candidates.jsonl` sha256 `aeb81764…`）。参考译文 10.13 `inputs_128.jsonl`（sha256 `1c7336c4…`），只用于打分。

## 结果文件

`asl-translator/experiments/p0-2026-10-27/results/`
- `repetition_paired_decode_local_arm64.json`：runner 原始输出，status COMPLETE。
- `….json.calls.json`：90 次 generate 调用的设备、参数及耗时。
- `….log`：运行日志。
- `repetition_paired_scores.json`：汇总及逐例数据。
- `repetition_paired_cases.csv`：45 例逐例表。

## Control 复现

**45/45 文本一致，45/45 token id 一致**，与 P0-A 保存的 CPU T 相同。corpus 指标与 P0-A 记录逐位相同。90 次 generate 全部在 CPU 上运行，只出现两组参数：`num_beams=4, max_new_tokens=100, do_sample=False`，`no_repeat_ngram_size` 分别为 0 和 3。因此 treatment 可以解释。

## 相对 control 的改善与退化（自动指标）

| 45 例 | Control | Treatment | Δ |
|---|---|---|---|
| corpus chrF | 23.7634 | 25.4893 | **+1.73** |
| BLEU-4 | 5.7246 | 5.9436 | +0.22 |
| WER | 95.44 | 92.91 | −2.52 |
| 平均输出/参考词长比 | 0.9997 | 0.9714 | −0.03 |
| 平均词数（参考 22.89） | 19.18 | 18.96 | — |
| loop_out（§1.4） | 9 | **0** | −9 |
| 旧 10.13 repetition_loop 标记 | 7 | 0 | −7 |
| 触顶 100 token | 1（R36） | 0 | — |
| 明显变短（≤0.75×） | — | 4（R01、R35、R39、R42） | — |
| 空输出 / 报错 | 0 | 0 | — |
| generate 耗时 | 130.5 秒 | 123.0 秒 | 全程 279 秒 |

重复统计：去除 loop 9 例（R01、R03、R11、R18、R20、R23、R36、R39、R42），新增 loop 0 例，仍保留 0 例；36 例两臂均无 loop。文本变化 24 例，不变 21 例。

**关键副作用：** 变化的 24 例中有 15 例在 control 中本没有 loop。约束作用于 mT5 token 三元组。经 tokenizer 核实，`I'm` 被切为 `▁I ' m` 三个 token（`you're` 同理），所以同一句中第二次出现 `I'm` 会被禁止。control 中含 ≥2 个 `I'm` 的 7 例全部被改写（R02、R03、R04、R05、R13、R23、R35）。这不是"去除重复"，而是对正常语言的约束。

### R01 与 R41

| | R01（focus，loop） | R41（named control） |
|---|---|---|
| 参考 | Instead of saying ball, we're going to replace it with a D, and we're going to say dall. | So always save those drawings, that's where some of these come from. |
| Control | I'm going to change the ball ring to a D and a D instead of a D and a D instead of a D and a D instead of a D instead of a | We always save these drawings and that's where they come from. |
| Treatment | I'm going to change my ball joints to a D, which is a red ball which means I've got a very red ball. | （与 control 相同） |
| 句 chrF C→T | 28.19 → 26.55（−1.64） | 63.74 → 63.74（0） |
| WER C→T | 172.2 → 116.7 | 58.3 → 58.3 |
| loop | 去除 | 无 |
| 词数 / token | 34→23 / 51→40 | 11 / 21 |

R01：loop 被去除，但 control 的重复部分里含有 "D instead of"，与参考的 "replace it with a D" 相关；treatment 换成了 "red ball" 等参考中没有的内容。WER 下降主要因为输出变短。语义是否改善需要人工判断。R41 不受影响。

### 逐例分流（自动，非语义标签；人工状态全部 pending）

| 类别 | 案例 | 说明 |
|---|---|---|
| wrong→right 候选（Δ句 chrF ≥ +5） | R03、R05、R11、R18、R36 | 阅读后看，R03、R11、R36 仍与参考内容基本无关，只是去掉了循环。R18 出现 "head" 相关词。R05 无 loop，变化来自 `I'm` 限制，姓名仍错。**未发现可确认的 wrong→right。** |
| right→wrong 候选 | R35（−5.14）、R42（−5.97）、R04（−4.82） | R35 是 control 中最接近参考的案例之一（chrF 45），treatment 删除了自我介绍 "Hi, I'm Colin"。这正是 fingerspelling 的姓名位置，原因是第二个 `I'm` 被禁。R04 的姓名从 Silver 变为 Segundo（两者均错）。R42 去掉了 loop，但内容缩减为一句。 |
| loop 去除但句 chrF 下降 | R01、R20、R42 | — |
| 重复状态不变 | 36 例（其中 21 例文本完全相同，15 例无 loop 但文本改变） | — |
| can't-tell / 需人工 | 其余全部变化案例 | 小幅变化多为措辞替换，自动分数不能判断语义。 |

## 结论

- **可运行：** 是。资产在本机齐全，control 与 P0-A 逐 token 复现。
- **诊断信号：** `no_repeat_ngram_size=3` 消除了全部 9 个 §1.4 loop 和唯一的触顶截断，没有新增 loop，corpus chrF +1.73、WER −2.5。但它同时改写了 15 个原本没有 loop 的输出，并在姓名介绍句上造成可见损伤（R35、R04）。
- **翻译质量提升：** 未证明。没有一例可以自动确认为 wrong→right；去掉 loop 后的内容多数仍与参考无关。增益幅度也低于 P0-A 冻结的 +3 chrF 门槛（该门槛属于另一个实验，这里只作为量级参照，不作为本实验的判定）。

## 未完成项

- 人工语义标签：wrong→right / right→wrong / unchanged / changed-same-status / can't-tell，45 例全部 pending。优先复核 R01、R03、R11、R18、R35、R36、R42。
- 只跑了 A_official 域；B_ours_5p39 未跑。
- 只测了协议固定的 token trigram 一个 treatment 设置；未测其他 n 或词级约束（协议不允许本轮追加）。

## 下一步

1. 把上表 7 例连同两臂文本交 ASL reviewer 盲评（隐去臂标签）。
2. 若要继续这条路线，需另立预注册实验：例如只禁止与 loop 相关的长 n-gram，或在词级而非 token 级约束，以避免 `I'm` 类误伤。不得用当前 45 例调参后再当成验证结果。
3. 不改线上：线上是 Gemini 路径，不使用此 Uni-Sign 解码设置。
