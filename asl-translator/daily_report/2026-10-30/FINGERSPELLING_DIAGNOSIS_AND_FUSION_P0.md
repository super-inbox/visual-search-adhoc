# ASL Daily Report：reference-assisted 拼写诊断与局部融合

日期：2026-10-30；交接对象：baobao。  
状态：R02 单例诊断＋下一轮 P0；没有新模型推理、生产变更或已验证的 Fusion 收益。

## 今天明确的方向

**不再把“先找到 ASL 专家”作为所有 fingerspelling 工作继续推进的前提。** 已有英文 ground truth 可以帮助定位预期名字，AI 可以检查连续手部帧、找稳定手形、提出字母与时间区间，再与识别器输出比较。先完成这类诊断与融合原型，人工复核集中在分歧、模糊位置及后续质量确认。

保留两个不同的评测口径：

- **Reference-assisted diagnosis：** 可以看英文 ground truth，用于提出待核对的名字、寻找错误位置、检查帧序列。不能因为参考答案里有这个名字，就把模糊帧强行标成对应字母。
- **Reference-free inference：** 拼写识别与融合算法不接收 ground truth；运行并冻结输出后才用 reference 评分。这才回答真实推理能否改善。

10/29 的盲评 Stage A 仍未完成，它的 CER、G0–G4 和独立标签口径保持不变。今天新增的是独立记录的辅助诊断路径，**不是把 AI/reference-assisted 标签冒充盲评标签，也不是事后修改原有 gate**。原先“等待专家，暂停全部后续工作”的安排由本报告更新。

## R02：已完成的单例检查

输入为 inspection sheet 的压缩展示视频 `G3OMdQo1zjY_0-10-rgb_front.mp4`，24 fps、100 帧，时长约 4.167 秒。输入 SHA-256：`33a0432e79961dba7352c064fefaccbc2b579903e55cf612c2b2d3b81093d834`，与已保存 OpenFS 运行的输入 hash 一致。

本次展开检查了全部 100 帧，并放大复查了 0.5–1.458 秒的连续手部帧。使用既有 OpenFS 和 Uni-Sign 预测，没有重新运行识别器。分析者此前已见模型输出，之后也读取了 reference，因此本次**不是盲评**。

英文 ground truth：

> Hi, I’m Mike Camelin with SunState Aviation Flight School in Kissimmee, Florida.

| 来源 | 输出 | 可以得出的结论 |
|---|---|---|
| Sentence reference | Camelin，C-A-M-E-L-I-N | 提供待核对的目标姓氏；没有逐字母时间 |
| OpenFS，clip 0–2 s | `camilian` | 对 `camelin` 的字符编辑距离为 2；条件性名字字符串 CER = 2/7 = 28.6% |
| Uni-Sign B 旧输入 | `Hi, I'm Amelia and I'm a rescue fighter.` | 姓氏未保留；后半句也有内容错误 |
| Uni-Sign A official | `Hello, I'm Dr. Erica Millian, with Red Sox, and I'm going to teach you how to do a full moon in Spanish.` | 姓氏未保留；输入窗口与 B 不同，不作同输入性能对比 |

**CER 的限定：** 以 0–2 秒候选区间确实对应 Camelin 为前提，对完整预测字符串与 reference 姓氏做 Levenshtein 比较。不是整个视频的 CER，不是独立逐字母视频标签的准确率，也不是 Stage A 的正式结果。不能把姓名拼写与视频内容的对应关系当作已经全部验证。

当前视觉观察（clip 内秒数）：

| 稳定证据帧范围 | 暂定观察 |
|---|---|
| 0.000–0.250 | C 手形候选较清楚 |
| 0.333–0.458 | A 手形候选较清楚 |
| 0.500–0.833 | 仍有不确定手形，需要结合前后帧核对 M/E 假设 |
| 0.875–1.000 | L 手形候选较清楚 |
| 1.042–1.750 | 后续字母序列未独立确认，重点检查 I/N 假设及过渡 |

这些是**证据帧范围，不是完整字母的精确起止时间**。未知区域可能包含多个字母，不能把每一帧视为一个字母。当前不能把 `C A [未知] L [未知]` 写成已确认的完整 Camelin，也不能把 0–2 秒窗口直接当作准确的 fingerspelling 边界。

局部图像保存在本次操作机的 `docs/asl-diagnostics/2026-10-30-fingerspelling/`；本报告不依赖这些本地图片才能理解结果，也没有将视频或截图复制进仓库。可用现有 inspection sheet 的 R02 复查。

## 时间戳和置信度：当前实际有什么

- OpenFS 有输入窗口时间，例如 0–2 秒；`character_timestamps` 为空，没有逐字母对齐。
- Uni-Sign 有输入视频区间和整句输出，没有每个英文词对应的视频时间戳。不能将 token 顺序或 attention 直接宣称为已验证时间对齐。
- 已保存的 R02 provenance 中，B 起点为源视频 80/24 = 3.3333 秒，A 起点为 35/24 = 1.4583 秒；B clip 时间映射到 A clip 时间需加 45/24 = 1.875 秒。比如 B 的 0–2 秒对应源视频约 3.3333–5.3333 秒、A 内约 1.875–3.875 秒。
- 上述映射沿用已保存的验证记录及展示视频对应 B 的 100 帧时间轴；本次未重新对 raw source 做像素匹配。映射到同一时间坐标**不等于找到对应的英文词**。
- OpenFS `camilian` 的平均 token 概率约 0.838；Uni-Sign B 保存了 sequence score 约 −0.722。两者定义不同、未经正确率校准，不能直接比较，不能解释为 83.8% 与某个百分比谁更可信。

## 给 baobao 的 P0 Items

### P0-A：R02 完整逐字母诊断，然后扩展小批开发样例

1. 使用原始可获得的最高质量视频，保留完整帧率；逐帧检查候选区间并向两侧扩展，不停留在稀疏采样截图上。
2. 结合 reference 的 Camelin，逐个检查 C/A/M/E/L/I/N 是否被视频支持；不以英文 reference 代替视觉证据。不清楚的字母、可能的漏字和重复字母保留候选或 `?`。
3. 输出 `case_id / video_hash / time_base / span_start / span_end / letter_candidates / evidence_frames / uncertainty_reason / label_origin`。区分稳定手形证据帧、过渡帧和估计的字母边界，不编造数值置信度。
4. 将既有 OpenFS 预测与 reference、AI 视觉观察分别比较：明确哪些是识别错误、哪些可能是区间截断、低分辨率或对齐不确定。名字 CER 标明分母和匹配前提；不确定标签不做正式准确率结论。
5. R02 走通后，按预先记录规则选择少量其他开发样例，包含负例和原本 Uni-Sign 正确的例子。不要只选可修复的名字；不要把此工作流混入原冻结盲评集而仍称其为 blind。

**交付：** 逐字母证据表、时间范围、误差归因和可复查的输入清单。成功标准是能解释具体字符错误，不是必须拼出一个完整名字。人工/独立复核不是启动条件，后续优先复核 AI 分歧位置。

### P0-B：实现 reference-free 的有限融合原型

目标：只修对应的名字/拼写内容，避免让大模型按语言常识重写整句。

1. **统一坐标：** specialist 和 Uni-Sign 使用同一源视频 ID 与可核验时间映射；记录各自 crop、窗口和预处理版本。
2. **提出文本位置：** 根据整句中的人名/专有名词位置与视频上下文提出匹配。R02 B 的 `Amelia` 只是待验证位置，不能因为它是名字就认定与候选区间精确对应。多位置或无法匹配时弃权。
3. **建立可检查的替换条件：** 拼写证据是否完整、边界是否稳定、独立解码或轻微窗口扰动是否一致、候选是否明显优于备选、对应文本位置是否唯一。稳定不等于正确，这些只是门控特征；阈值在评测前登记。
4. **保守输出：** 满足条件则仅修改匹配的文本片段；否则保留原句并附未确认候选。禁止读取 reference 来修拼写，禁止用词典把不确定名字强行补成常见名字，禁止融合时自行补入 reference 的 Mike 或其他信息。
5. **保存审计记录：** 原句、候选拼写、源时间、拟替换字符位置、匹配依据、动作（replace / keep / attach_candidate）、原因与最终输出。未替换部分应保持不变。

**R02 本次实际动作：** 保留 B 原句，附 `camilian` 未确认候选；没有执行自动替换。若未来 reference-free 视觉识别得到 Camelin 且位置匹配通过，可测试只将 Amelia 替换为 Camelin。即使成功，`rescue fighter` 等其他内容错误仍未修复，不能称整句已经正确。把 ground truth 中的 Camelin 直接填进去只能算 oracle/reference-assisted 上界示范，必须与实际融合分开。

**交付：** 可复现融合 runner、逐例 action 日志及失败案例；第一版不要求训练新融合模型，也不要求先解决全句词级时间对齐。

### P0-C：评测增量与误伤，不重复旧基线

- 比较固定的 Uni-Sign baseline、specialist 候选、实际 reference-free fusion；如有 oracle 修复，单列。
- 同时报告名字字符串 CER/准确率、正确修复数、错误替换数、原本正确内容的损伤、替换覆盖率/弃权率、整句指标与额外成本。
- reference 只在输出冻结后用于融合评分。开发诊断可以看答案，但必须与确认集区分；AI 辅助标签首先支持诊断和一致性分析，不能自动成为独立真实标签。
- 先在小批开发案例证明明确收益，再冻结方法，用未参与调参的数据确认。复用已有大规模 Gemini/Uni-Sign 基线；不恢复已暂停的 OpenAI 配置或当前 no-repeat 再生成。

R03 PARTIAL 状态与仅失败 batch 重试仍是可并行的工程 P0，与本轮拼写研究独立。

## 来源与范围

- [NEXT_P0 总报告（10/29，固定提交）](https://github.com/super-inbox/visual-search-adhoc/blob/b084709236bc78ae12939138c1fcfa72f549d1f0/asl-translator/daily_report/2026-10-29/ASL_NEXT_P0_WORK_REPORT.md)
- [OpenFS 已保存结果](../../experiments/p0-2026-10-27/results/specialist.json)
- [输入 provenance 文档](../2026-10-27/p0-input-provenance/README.md)
- [当前 ASL index](../../asl-translation-mvp-spec.md)

本次完成：100 帧视觉复查、输入 hash 与既有识别结果一致性核对、reference 姓氏编辑距离计算、现有时间/分数字段核对、保守融合决策记录。未完成：完整独立逐字母标签、新识别器推理、实际自动替换、批量收益评测或上线。
