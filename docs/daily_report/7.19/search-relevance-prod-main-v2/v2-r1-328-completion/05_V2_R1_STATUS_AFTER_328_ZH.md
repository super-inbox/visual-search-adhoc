# V2-R1 冻结与旧328补测后的状态说明

日期：2026-07-19

## 1. V2-R1 已经冻结

- 原始分支：`baobao/search-relevance-prod-main-v2-2026-07-19`
- 冻结分支：`baobao/search-relevance-prod-main-v2-r1-frozen-2026-07-19`（本地分支，指向与原始分支相同的 SHA，未 checkout）
- 冻结 SHA：`32f6282a240edfa87edae5a0ba5308aecf462466`（短 SHA `32f6282a`，与任务书预期一致）
- V2-R1 代码自冻结前后均为 `git status --short` 干净，未做任何修改。
- V0 worktree（`05e5f2d332778ac52c712dd2429f4a8f4e7c3673`）全程未修改。

## 2. 旧328条 Easy Query 已经补跑

- 使用与上一轮 326 条评测**完全相同**的采集方法（`scripts/collector.mjs`，真实 HTTP 请求 + RSC flight payload 提取，命中真实 `next start` 生产构建，端口 4501/V0、4502/V2-R1）、裁判方法（`scripts/judge.mjs`，rubric-v1.1，gpt-4o-mini，temperature=0，代码内确定性打分公式）、模型、prompt、rubric、LOW_RESULT_THRESHOLD（<5 条结果）、超时（30s）、重试策略、以及"评测前重启两侧服务器以保证 cache 对称"的做法。脚本文件与上一轮字节级一致，未做任何修改。详见 `00_V2_R1_FREEZE_MANIFEST.json`。
- 328 条 Query 全部跑完（328/328），0 条技术性采集失败，0 条 ERROR 行，两侧各 11 条合法 UNJUDGABLE（信号本身不足以判断，非跑失败）。

## 2.1 只读统计完整性核对（2026-07-19 追加）

针对"V0/V2-R1 的 PASS+PARTIAL+FAIL 加总为 317，与总数 328 不符"的疑问，已对三份原始 CSV（`01_V0_OLD328_RESULTS.csv`、`02_V2_R1_OLD328_RESULTS.csv`、`03_V0_V2_R1_OLD328_PAIRED.csv`）做了只读核对，结论如下：

- **总行数**：三份文件均为 328 行数据（不含表头），无缺行。
- **重复 row_index / query**：均不存在。
- **空 label**：均不存在。
- **完整标签分布**：V0 = PASS 56 + PARTIAL 79 + FAIL 182 + **UNJUDGABLE 11 = 328**；V2-R1 = PASS 60 + PARTIAL 79 + FAIL 178 + **UNJUDGABLE 11 = 328**。两侧均已 100% 覆盖 328 条。
- **差异原因**：这"消失的 11 条"就是 UNJUDGABLE 分类本身，此前已在完成状态文字中披露（"两侧各 11 条合法 UNJUDGABLE"），但未在聚合表格中单独列为一行，导致 PASS+PARTIAL+FAIL=317 这一部分和数字看起来"少了 11"。**这是报告呈现方式的遗漏，不是统计脚本计算错误**——所有百分比（PASS 率 17.07% 等）在计算时使用的分母本来就是真实的 328，未曾使用 317。
- **重要澄清**：V0 侧的 11 条 UNJUDGABLE 与 V2-R1 侧的 11 条 UNJUDGABLE **不是同一批 Query**（裁判对两侧独立判定）。两侧各自的 UNJUDGABLE 集合的并集共 17 条唯一 Query（5 条两侧都是 UNJUDGABLE，6 条仅 V0 侧是，6 条仅 V2-R1 侧是）。全部 17 条的逐条明细（query_id/query/两侧 label/两侧 result count/judge status/reason）已补充到 `04_OLD328_STATISTICAL_COMPARISON.md` 的"Label completeness audit"章节。
- **处理方式**：按核对结果，本次是"最终摘要漏写 UNJUDGABLE 明细行"，已更新 `04_OLD328_STATISTICAL_COMPARISON.md`（新增 UNJUDGABLE 行 + 17 条明细表 + 分母说明）与本文件；**未修改任何原始评测 CSV，未重新运行 LLM 评测，未修改 V0/V2-R1 代码**。

## 3. 328的结论与326是否一致

**不完全一致，但核心失败模式一致，且不推翻326的结论。**

- 在 328 条集合上单独看，V2-R1 的 PASS 率（17.07%→18.29%）、FAIL 率（55.49%→54.27%）、均分（22.64→24.17，paired bootstrap 95% CI [+0.36, +2.56] 不含零，Wilcoxon p=0.007）都表现出小幅、统计上可检测的正向移动，改善 Query 数（24）多于回归 Query 数（16）。
- 但**零结果率（8.23%→8.84%）和低结果率（5.49%→7.01%）同时走弱**——这正是 326 集合分析中诊断出的核心回归模式（简单实物名词/人群类 Query，如 马克杯、咖啡、香水、口红、家纺、保健品、大学生、素食者，从原本干净的 strict-only 结果被稀释为更弱的 relaxed 候选混入）。回归 Query 清单里可以直接看到这个模式在 328 集合上同样复现。
- 因此：328 的"表面净改善"和 326 的"净回归"并不矛盾——它们是**同一个根因、在不同 Query 分布下呈现出不同净方向**的两次观测，而不是"V2-R1 其实是好的，326 只是噪声"。任务书第 14 节的门禁（零结果率不得上升）在 328 上依然未通过。

**综合 326 + 328（共 654 条 Query）的结论：混合偏负面（mixed-to-negative）**。326 在 PASS/FAIL/零结果三项核心指标上全部走弱；328 在均分/PASS/FAIL 上小幅走强但零结果/低结果走弱。没有任何组合角度能得出"V2-R1 明确优于 V0"的结论。

## 4. V2-R1 是否仍然 NOT_READY_TO_REPLACE_PRODUCTION

**是，维持不变。** 328 的补充结果不构成推翻上一轮 Go/No-Go 结论的证据——上一轮 `33_GO_NO_GO_RECOMMENDATION_ZH.md` 的核心论据（326 集合零结果率/PASS率/FAIL率三项一致走弱、回归Query数多于改善Query数、根因已诊断为移除二元 strict 门禁后简单Query被稀释）在加入 328 数据后依然成立，且 328 本身的零结果/低结果走弱是对同一根因的独立佐证，而非反证。

## 5. V2-R1 可以作为第一轮实验成果保留

V2-R1 分支与冻结分支均予以保留（不删除、不 rebase、不 squash）。其中已验证、有实证支撑的修复方向（coffee cup 子串碰撞、black friday banner 碰撞、吉祥物/贴纸广谱噪声压制、统一可解释评分器架构本身）可作为后续迭代（如需要开启新一轮实验）的起点，但本阶段任务范围**不包含**开始该项工作。

## 6. V2-R1 不得作为当前上线版本

明确：V2-R1 在 326 与新补跑的 328 两个数据集上均未达到"明确优于 V0 且无严重回归"的上线门槛（326 三项核心指标走弱；328 零结果/低结果走弱），**不得**合并、部署或以任何形式替换生产环境当前版本。

## 7. Production fallback 仍是 V0

生产环境当前版本（`05e5f2d332778ac52c712dd2429f4a8f4e7c3673`）保持不变，继续作为唯一的生产 fallback。本阶段未对 V0 做任何修改，未执行 push/PR/merge/deploy。

## 附：数据来源

- `01_V0_OLD328_RESULTS.csv` / `02_V2_R1_OLD328_RESULTS.csv` / `03_V0_V2_R1_OLD328_PAIRED.csv` — 328 条逐条原始结果
- `04_OLD328_STATISTICAL_COMPARISON.md` — 完整统计检验（McNemar / paired bootstrap / Wilcoxon）与改善/回归 Query 清单
- `00_V2_R1_FREEZE_MANIFEST.json` — 冻结与配置复用的完整记录
