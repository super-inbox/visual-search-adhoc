# ASL progress review — 2026-10-25

Reviewed research head: `7a4400b4a790a4b467639ed070f6865a3af74c35`.
Sources: [work report](ASL_P0_WORK_REPORT.md), [frozen protocol](../2026-10-23/P0_PROTOCOL_FREEZE.md), and the linked candidate, source-check and reviewer artifacts.

## 当前结论

这轮工作减少了不确定性，但尚未交付可上线的翻译质量提升。45 个样例均为探索集，不能把样例比例推广为真实用户错误率。当前优先级应从“直接加 Fusion”改为“先确认缺失信息在哪里、是否能从视频恢复”。

| 工作 | 已有证据 | 决策 |
|---|---|---|
| P0-A 候选重排 | official 输入 top-1 chrF 23.7634；逐句 oracle 后 corpus chrF 26.0015，差值 +2.2381，低于预设 +3。旧输入 +2.2638 也未过线。official 的 9 个重复输出中仅 1 个有非重复候选。 | 保持冻结门槛的 STOP；不为这个候选池投入训练/GPU。不是所有 Fusion 无效的结论。 |
| P0-B 手指拼写 | 完成现成识别器可行性调查；尚未确认 R02/R05/R35 中拼写的存在、时间和可读性，也没有识别器效果。 | 先做熟练 ASL 使用者盲评，再决定是否值得跑 CPU specialist。 |
| P0-C 输入修正 | R26 旧窗口在相机边缘丢手指，放大 crop 无法恢复；official 窗口手部可见。R29 当前窗口约 46% 是静止。 | R26 不再以扩大 crop 为 P0；R29 优先验证时间边界。尚无 corrected decode 或语义改善证据。 |

## 评审中需要明确的限制

1. **Oracle 的适用范围。** `headroom_oracle.py` 先逐句最大化 sentence chrF，再计算 corpus chrF。后者不是前者的算术平均，因此这不是所有候选组合的 corpus chrF 严格上界。冻结规则下的 STOP 有效，但“任何 reranker 都不可能更好”的解释过强。工作报告已修正；原始协议、脚本及结果哈希保持不变。
2. **P0-A 尚有协议报告缺口。** 冻结 §1.7 要求停止时仍描述性报告 R1/R2；实际结果明确没有运行这两臂。应将状态理解为“gate 已结束，描述性两臂未完成”，记录这个偏离。若补齐，只使用已有候选和已冻结 probe 输出，不调阈值、不训练、不新增解码；没有完整输入则继续显式标记未完成。不能声称 R1/R2 已被实测否定。
3. **P0-C 盲评与参考条件定位要分开。** reviewer instructions 的 Step 2 会在展示参考文本后询问 target_start/end。这类区间不是 reference-free 的修正证据。保留 Step 1 原始边界和内容记录；若修正依赖 Step 2 才能定位，只能标为人工参考条件下的诊断，不能支撑自动化效果。执行修正前必须明确其与冻结 §3 的关系；不要事后重写协议。
4. **时间相等不等于从未校准。** R29 original == realigned 和邻句错序提示可能存在标注问题，但不足以证明该行未经校准。最终内容归属需要 ASL 评审。R10 的两个时间来源冲突也尚未解决。
5. **“old”不是 Gemini 基线。** 本轮 D-B 是 Uni-Sign 在旧预处理输入上的输出；D-A 是同一 Uni-Sign 的 official 输入域。不能将两列差异当成 Gemini vs Uni-Sign，或训练新模型的收益。

## 下一步 P0（按优先级）

1. **完成 8-clip 两阶段人工评审。** 包已构建但尚未发送、标签为空。由团队安排熟练 ASL reviewer；先保存盲评版本再开放参考。验收：R02/R05/R35 拼写存在性、时间、盲读字母及可见性；R26/R29 自然边界和独立内容记录。此合并不代表已经联系 reviewer。
2. **解决输入溯源并冻结一次修正。** 工程侧先解决 R10 时间来源冲突、确认实际送入模型的帧；R29 优先评估边界错误。每个可修正案例预先记录一种修正、来源和时间，再做同模型配对比较。没有 reference-free 修正依据的案例保留为诊断或停止。R35 的两个窗口不重叠，必须分别定位内容。
3. **有清晰可见拼写才跑局部 specialist。** 验证可用权重、许可、CPU 路径和 MediaPipe 输入适配。输出字符错误率、名字 exact match、覆盖率、替换精确率及整句损伤；低置信度保留原句。先证明局部新增视觉信息能纠错，再讨论融合。
4. **补齐 P0-A 描述性报告或明确偏离。** 维持停止投资的决定；后续 Fusion 若改变输入信息或候选生成，应另立实验，不用当前 45 例反复调参冒充新验证集。

每个修正/融合实验均需报告 wrong→right、right→wrong、unchanged、changed-same-status、can't-tell；减少重复或提高单个文本分数不等于成功。

## Merge scope and validation

The research branch contains 29 commits beyond main, adding 617 files with no removed lines. This includes the October 5–20 supporting research archive, six visual-production research documents, the October 23 P0 artifacts and the October 25 report; it is not just the latest report. Changes are research documentation, data, scripts and ignore rules, not application runtime code. This review does not claim a line-by-line audit of the historical archive.

Merge-time checks passed: AST parsing of all 9 new October 23 Python scripts; parsing of 5 JSON files, 2 JSONL files and 8 structurally consistent CSV files; both canonical candidate SHA256 values against summary/determinism records; 90 candidate records with case ordering, pool size, recorded sentence-oracle selection and loop totals; 26 human-review rows. These checks verify artifact consistency, not an independent recomputation of chrF/BLEU or a model rerun. The second decode run, raw source videos and reviewer package binaries are not independently reproduced here. No model training, GPU run, holdout access or reviewer outreach was performed.
