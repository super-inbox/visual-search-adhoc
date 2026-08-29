# ASL Ground Truth / Evaluation — Boss Summary

## 1. 这次做了什么

1. 搭建了一个本地 ASL 字幕 / ground truth 标注工具。
2. 整理了现有的 13 个 ASL 视频语料库和已有的参考字幕。
3. 为视频 1320 新增了一份基于烧录字幕（burned-in caption）转写得到的 reference candidate。
4. 搭建了一套本地评测 + 生产配置等效的离线 runner，用它在两个已验证案例上评测了当前识别算法。

说明：
- **155** 和 **1252** 是已验证（verified）的 reference。
- **1320** 目前仍是 `candidate_reference`，尚未纳入官方指标，等待生产方向确认后再决定是否转正。1320 的参考文本是"烧录字幕转写候选"（burned-caption-derived reference candidate），**没有使用 OCR**，是人工转写视频画面中已烧录的英文字幕得到的。

## 2. Ground Truth 工具

工具路径：`tools/asl-ground-truth-annotator/`

功能：
- 本地 MP4 播放
- 带时间戳的字幕编辑
- 导入 SRT
- 导入 baseline 预测 JSON
- 编辑 / 新增 / 删除 / 拆分字幕片段
- 导出 SRT + 标准化 JSON
- 校验（validation）
- 纯本地运行，不上传任何数据

启动命令：

```
python3 -m http.server 8934 --bind 127.0.0.1 -d tools/asl-ground-truth-annotator
```

有了这个工具，我们以后可以持续、可重复地构造更多人工验证的 GT，而不需要手工直接改原始文件。

## 3. 当前可用的 reference 数据

**155**
- 已验证的人工翻译 reference
- 6 个片段
- Curify 公开 demo 视频
- 对家庭关系 / 年龄 / 数字识别的诊断很有用

**1252**
- 已验证的 Curify 人工翻译 reference
- 11 个片段
- 真实用户视频
- 对拼写手语（fingerspelling）和数字类内容的诊断很有用

**1320**
- 14 个基于字幕转写的片段
- 参考文本来自视频中烧录的英文字幕，人工转写得到
- 仅为 `candidate_reference`，尚未纳入官方评测指标，需等生产方向确认

整体语料库共 13 个视频。

## 4. 现有算法 A/B 评测

对比条件（相同）：
- `gemini-2.5-flash`
- 相同的 motion-adaptive 采样器
- `FRAME_BUDGET=96`
- `KEYFRAME_WIDTH=512`
- `BATCH_SIZE=24`
- 相同 prompt
- 相同解析逻辑

唯一变量：
- **baseline0**：不设置 temperature（provider 默认值）
- **temperature0**：显式设置 temperature=0

这是"生产配置等效"（production-configuration-equivalent），不代表两次调用是字面上完全确定性复现（Gemini 在 temperature=0 时实际仍存在一定非确定性）。

| Case | Config | WER | CER | Temporal IoU |
| --- | --- | ---: | ---: | ---: |
| 155 | baseline0 | 37.04% | 34.85% | 70.95% |
| 155 | temperature=0 | 33.33% | 34.09% | 70.49% |
| 1252 | baseline0 | 92.31% | 72.11% | 47.43% |
| 1252 | temperature=0 | 92.31% | 66.93% | 60.72% |

两个已验证案例的汇总：

| Metric | baseline0 | temperature=0 |
| --- | ---: | ---: |
| Macro WER | 64.68% | 62.82% |
| Macro CER | 53.48% | 50.51% |
| Macro Temporal IoU | 59.19% | 65.61% |
| Pooled WER | 73.42% | 72.15% |

注意：以上汇总只包含 **2 个已验证视频**（155、1252），**1320 未被计入**这个汇总。

## 5. 主要发现

1. temperature=0 有一定局部改善，但效果小且不一致。
   - 155 的 WER 从 37.04% 降到 33.33%。
   - 1252 的 WER 两个配置完全一样，都是 92.31%。
   - CER 在两个案例上都有改善。
   - 时序（timing）对齐在 1252 上明显变好，但在 155 上基本没变化。

2. Temperature 不是主要问题。仅凭这两个案例的证据，不足以支持调整生产环境的 temperature 设置。

3. 更大的问题在识别质量本身：
   - 1252 中的拼写手语人名（Greg、Sara），两个配置都没有识别对。
   - 数字类内容（Number two/three/four 等）识别仍然偏弱。
   - 模型输出的英文很流畅，但内容不一定对应实际打出的手语内容。

4. 时序识别（判断什么时候在打手语）看起来比内容识别（打的是什么）更可靠。也就是说，模型更擅长判断"何时"在打手语，而不是"打了什么"。

5. 现有的重复 / 碎片化片段问题（比如 155 里同一句话被拆成两段）在两种 temperature 配置下都存在，说明这不是 temperature 引起的。

以上结论只基于当前已验证的两个案例，不做超出范围的推广。

## 6. 结论 / 推荐下一步

**暂不建议改动生产环境的 temperature 设置。**

推荐的下一步优先级：

1. 扩大已验证的 ground truth 数量，用标注工具构造 / 验证更多真实案例。
2. 优先覆盖以下诊断类别：
   - 拼写手语 / 人名
   - 数字
   - 更长的语义内容
   - 画面清晰、能看到面部和非手动标记（non-manual markers）的案例
3. 之后用现有的评测工具持续、统一地对比算法迭代效果。
4. 把 temperature=0 当作一个可能的小幅配置调整项，而不是核心修复方案。

后续如果需要，可以在有更多已验证 GT 之后再做重复调用 / 确定性测试。

## 7. 主要产物

标注工具：`tools/asl-ground-truth-annotator/`

评测工具：`tools/asl-eval/`

评测集定义：`data/asl_corpus/evaluation_set.json`

1320 candidate 数据：`data/asl_corpus/ground_truth_candidates/`

模型评测预测结果：`data/asl_corpus/predictions_eval/`

详细 A/B 报告：
- `docs/daily_report/8.26/asl-ground-truth-eval/155_BASELINE0_VS_TEMPERATURE0.md`
- `docs/daily_report/8.26/asl-ground-truth-eval/1252_BASELINE0_VS_TEMPERATURE0.md`
- `docs/daily_report/8.26/asl-ground-truth-eval/VERIFIED_TWO_CASE_SUMMARY.md`

## 8. Privacy / Safety

- 标注工具和评测 runner 均为本地运行
- 评测 runner 绕过 Curify 生产数据库和 credit 计费链路，不产生任何 Supabase / Azure / credit 副作用
- 只有本次评测中被选中的采样帧被发送给 Gemini
- 原始视频和用户语料不应公开发布
