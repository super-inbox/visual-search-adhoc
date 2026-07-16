# Curify Easy Query 生产 Baseline —— 自动相关性评估报告

日期：2026-07-15（Baseline 采集）/ 2026-07-16（本轮自动相关性评估）
Run ID：`curify-easy-query-automated-relevance-eval-2026-07-15-16`
评估目录：`docs/daily_report/7.15/easy-query-production-baseline-v1/automated_relevance_evaluation-v1`

## 0. 重要声明（请先读这一段）

本报告是**基于已保存的截图、Top Results 和 raw record 进行的离线自动相关性评估结果**，
并通过 Calibration（30 条二次独立评分，一致率 100%）、第二轮独立复核（54 条 tier1 深度复核 +
10 条 tier3 随机抽查）和低置信度人工复核队列，降低误判风险。**这不是人工标注的绝对真值**，
报告中的分数和标签是 Claude Code 在锁定 Rubric 下产出的可审计判断，仍有 171 条 Query 被标记
`needs_manual_review=true`，建议人工优先核查 `final/automated_relevance_manual_review_queue.csv`
中的 P0（72 条）。

## 1. 本轮任务的性质

1. **搜索采集任务已经完成**：328/328 条 Easy Query 已于 2026-07-15 对生产站点
   `https://www.curify-ai.com`（commit `72b55b667bb5173cab87fcec377198064dc3ac28`）完成采集，
   结果保存在 baseline root 的 `final/`、`raw/`、`screenshots/` 中。
2. **本轮是离线自动相关性评估**：只读取已保存的数据，不重新访问生产网站。
3. **没有重新请求生产网站**：本轮所有脚本（`scripts/01`–`09`）均只操作本地文件
   （`raw/`、`screenshots/`、`checkpoints/`、`evidence/`、`final/`），不含任何网络请求代码。
4. **没有修改生产代码**：本仓库本身不含 Curify 应用源码，是纯文档/评估工作区。
5. **没有覆盖原始 Baseline**：所有输出都写入独立目录
   `automated_relevance_evaluation-v1/`，原 `final/easy_query_production_baseline_*` 系列文件
   未被修改（详见 `WORKTREE_SAFETY_REPORT.md`）。

## 2. 使用的证据与实际视觉阅读范围

- **文字证据（328 条全覆盖）**：`original_query`、`category`、`query_type`、
  `result_count_observed`、`zero_result`、`low_result`、`broadened_query`、`rewrite_observed`、
  以及每条可见 Top Result 的 `result_title`、`result_url`（含描述性 URL slug 段）、`image_url`、
  `metadata`（`inspiration`/`template`）。
- **截图视觉阅读（有限但明确披露的范围）**：Claude Code 环境的 Read 工具可以直接读取本地 PNG
  截图的真实像素内容。本轮**实际打开并阅读**了：30 条 Calibration Set 全部（两次独立评分均含
  视觉证据）、全部 12 条 0 结果 Query（确认是否为真实空状态）、以及首轮评估阶段针对若干歧义
  Query 的抽样视觉核查。**328 条 Query 中的大多数（第二层批处理阶段）使用文字证据评估
  （`evaluation_method=TEXT_EVIDENCE_ONLY`）**，因为在本次会话可承受的规模下，逐条打开全部
  328 张详细多区块截图会消耗与产出不成比例的评估资源，而该目录（Curify 的模板/示例目录）具有
  高度描述性、可验证的 URL slug（经交叉核对 `raw/*.json` 与截图确认属实），可作为可靠的文字
  代理证据。此限制在 `MODEL_AND_METHOD.md` 中完整披露，**不构成对 328 条全量像素级视觉核实的
  宣称**。
- 本轮第二遍复核（tier1 深度复核 54 条 + tier3 随机抽查 10 条）**同样以文字证据为主**，未在
  这一步新开截图；调整/推翻的判断均来自对同一文字证据的更严格独立复读，或（如 E027 围巾）
  沿用 Calibration 阶段已有的截图证据。

## 3. 使用的自动评估环境

评估者是 **Claude Code（Claude Sonnet 5）**，以 Rubric 驱动、可审计的方式直接进行语义判断——
不是调用外部 LLM API，也不是关键词匹配脚本。Python 脚本（`scripts/`）仅用于：数据抽取/关联、
固定评分公式（Rubric §4）的算术计算、聚合、CSV/JSONL 生成与完整性校验，**从不用于产出相关性
判断本身**。

## 4. Rubric（`RELEVANCE_RUBRIC.md`，rubric-v1.1）

- 评估对象是「用户原始 Query」与「生产实际返回结果」之间的相关性，无论是否触发 rewrite/broaden。
- 结果级标签：RELEVANT / PARTIALLY_RELEVANT / IRRELEVANT / UNJUDGABLE。
- Query 级标签：PASS / PARTIAL / FAIL / UNJUDGABLE，由机械参考区间 + 强制性整体核查
  （核心意图是否保留、drift 严重程度）共同决定，评估者可依据写明的理由覆盖机械结果，但不得
  静默覆盖。
- 打分公式（0–100，Top-5 加权：Rank1=0.30/Rank2=0.25/Rank3=0.20/Rank4=0.15/Rank5=0.10；
  RELEVANT=1.0/PARTIALLY_RELEVANT=0.5/IRRELEVANT=0.0，UNJUDGABLE 不计入分母）在整个流程中
  **锁定不变**（Calibration Pass A/B、328 条首轮、第二轮复核均使用同一份 `scripts/scoring.py`）。
- 唯一一次 Rubric 修订（v1→v1.1）发生在**评分前**：移除了「relevant_rate<0.20 单独触发 FAIL」
  的机械规则（会误伤「全部结果均为 PARTIALLY_RELEVANT、零 IRRELEVANT」的稀薄但不错的结果集），
  详见 `CALIBRATION_REPORT.md`。

## 5. Calibration（30 条）

按 category、语言（25 zh / 5 en，与 267:61 的语料比例大致匹配）、0 结果、Low-result、
rewrite/非 rewrite、歧义单词等维度**基于客观输入特征机械抽取**（非挑选易判断案例）。两次独立
评分（Pass A / Pass B）：
- **Query 级标签一致率：30/30 = 100%**（阈值 85%，未触发进一步迭代）。
- 平均绝对分差：1.53 分。
- 2 条 Query 出现结果级分歧但未改变最终标签（E072 极简、E154 母婴），据此为「风格/格式类
  Query 仅凭单张静态缩略图判断」新增置信度上限规则（不得为 HIGH，即使 judgeable_result_count≥3）。

## 6. 第二轮独立复核

- **Tier1 深度复核（54 条）**：覆盖任务规范 §15.2 全部强制类别（全部 FAIL、全部 PARTIAL、
  全部 LOW 置信度、全部 semantic_drift MODERATE/SEVERE、全部「rewrite 且首轮 PASS」）。
  原始标签一致率 45/54 = 83.3%（该批次刻意偏向高分歧类别，低于 Calibration 的 100% 属预期）。
  12 条进入正式 adjudication（9 条标签分歧 + 3 条同标签但分差≥15 分）。
- **Tier3 随机 PASS 抽查（10 条，本轮新增）**：对首轮 PASS 且未落入 tier1/tier2 的 55 条
  「低风险」PASS Query，按确定性规则抽取 10 条（18.2%，超过 10% 最低要求）复核，发现 1 条
  额外标签翻转。
- **Tier2 机械一致性审计（219 条，覆盖全部 328 条）**：对每条 Query 已记录的结果级标签重新代入
  锁定的评分公式，核对标签/分数是否与记录一致，并检查 §15.1 列出的规则（0 结果必须 FAIL、
  UNJUDGABLE 不得有分数、SEVERE drift+intent=NO 不得 PASS 等）。**328 条全部核查通过，0 处
  规则违反**（`logs/consistency_audit.json`）。这确认了首轮批处理脚本正确执行了 Rubric 公式，
  但不能替代对「看似合理但判断有误」的语义误判的发现——这正是 tier1/tier3 真实独立复读的作用。
- **最终结果：4 条 Query 标签从 PASS 翻转为 PARTIAL**（226 宠物主人、233 旅行者、245 宝妈、
  269 冬至），核心原因是「内容面向的受众」与「结果实际展示的视觉主体」被首轮混淆（例如
  「宠物主人」类结果展示的是宠物本身而非人物），详见 `review/adjudication_report.md` 中记录的
  三条可复用裁决原则。

## 7. 总体结果（328/328 全部完成自动评估）

| 标签 | 数量 | 占比 |
|---|---|---|
| PASS | 93 | 28.35% |
| PARTIAL | 106 | 32.32% |
| FAIL | 129 | 39.33% |
| UNJUDGABLE | 0 | 0% |

- 平均 relevance_score：**34.54**，中位数：**23.0**，P25：**0.0**，P75：**64.0**
  （0 结果 Query 记 0 分，且占比不小，显著拉低均值/中位数——这是真实分布，非计算错误）。
- Top-5 加权相关性均值：**0.3962**。
- 置信度分布：HIGH 13 / MEDIUM 299 / LOW 16。
- `needs_manual_review=true`：**171 条**（含全部 68 条 SEVERE drift、全部 4 条标签翻转、
  全部经 adjudication 的 tier1 案例等）。

## 8. Rewrite / Broaden 专项（138 条触发）

| | PASS | PARTIAL | FAIL |
|---|---|---|---|
| Rewrite 触发（138 条） | 34 (24.6%) | 42 (30.4%) | 62 (44.9%) |
| 未触发 Rewrite（190 条） | 59 (31.1%) | 64 (33.7%) | 67 (35.3%) |

- Rewrite 触发的 Query 平均分略低于未触发组，但这更可能是「选择效应」——Rewrite 本身倾向于在
  更难/结果更稀疏的 Query 上触发，而非 Rewrite 本身造成损害的直接证据。
- Semantic drift 分布（全语料）：NONE 210 / MINOR 25 / MODERATE 25 / SEVERE 68。
- 典型「Rewrite Guard 必要性」案例：E019 镜子（SEVERE drift，尽管有镜子专门的 rewrite，
  返回结果与镜子完全无关，0 相关结果）、E245 宝妈与 E269 冬至（MODERATE drift，标签翻转
  PASS→PARTIAL）、以及跨多个无关 Query 反复出现的「dual-character-comparison-infographic」
  噪声模板（Calibration 阶段发现，说明部分噪声源于检索排序本身而非仅 Rewrite）。
- 也存在 Rewrite **改善**结果的案例（如 E020 花瓶、E297 香薰机、E304 婴儿用品——均为
  low_result 但 Rewrite 后命中直接相关结果，最终 PASS），故**不能预设 Rewrite Guard 一定有效
  或一定有害**，需结合具体证据判断。详见 `summaries/rewrite_relevance_summary.md`。

## 9. 0 结果与 Low-result 表现

- **0 结果（12 条）**：按规则全部判 FAIL、score=0、`primary_failure_reason=ZERO_RESULT`，
  已与其余数据核对无矛盾。详见 `summaries/zero_result_relevance_analysis.csv`。
- **Low-result（43 条）**：**未被自动 FAIL**，按实际结果单独判断：PASS 13 / PARTIAL 15 /
  FAIL 15，证明「结果少 ≠ 一定不相关」的规则被正确执行。详见
  `summaries/low_result_relevance_analysis.csv`。

## 10. 主要失败模式

`primary_failure_reason` 分布（FAIL + PARTIAL）：`MOST_RESULTS_IRRELEVANT` 104、
`PARTIAL_INTENT_ONLY` 102、`ZERO_RESULT` 12、`REWRITE_SEMANTIC_DRIFT` 15、
`CORE_INTENT_LOST` 1、`WRONG_ENTITY` 1。核心问题集中在「结果主体与 Query 核心意图不匹配」，
其次是「仅覆盖部分意图」，两者合计占绝大多数非 PASS Query。

## 11. 自动评估的局限性

1. 328 条中的多数条目仅使用文字证据（URL slug / 标题 / metadata），未逐条打开截图核实真实
   像素内容——这是本轮披露的真实规模限制，不是隐藏的缺口。
2. 第二轮复核（tier2 的 219 条）为机械一致性审计，并非对每条重新进行独立语义判断；仅 tier1
   的 54 条 + tier3 的 10 条获得了真正意义上的第二次独立评分。
3. 评分/标签是 Claude Code 基于锁定 Rubric 的可审计判断，不是人工标注的绝对真值。
4. `by_result_count_bucket` 统计基于本次保存的 `visible_result_count`（Top Results 长表实际
   保存条数），并非网站真实总结果数——未获取、也未编造网站侧总数。

## 12. 仍需人工复核的部分

详见 `final/automated_relevance_manual_review_queue.csv`：
- **P0（72 条）**：全部 68 条 SEVERE drift Query + 4 条标签翻转 Query。
- **P1（78 条）**：FAIL Query、PARTIAL 且 LOW 置信度、可判断结果数<3。
- **P2（51 条）**：PASS 但触发 Rewrite/Broaden、其他中等置信度案例。

## 13. 后续如何与优化版本对比

本轮建立的 `final/automated_relevance_query_level_results.csv`（含 `query_index`、
`query_relevance_label`、`relevance_score`、`primary_failure_reason` 等字段）可作为**可复用的
基线对比表**：未来若 Curify 上线新版本（新的 Rewrite Guard、检索排序调整等），可用同一
Rubric（`RELEVANCE_RUBRIC.md`，锁定 rubric-v1.1）和同一评分公式（`scripts/scoring.py`）对新
一轮采集结果重新评估，逐 `query_index` 对比 `relevance_score` 与 `query_relevance_label` 的
变化，尤其关注本轮 FAIL（129 条）和 PARTIAL（106 条）Query 是否在新版本中改善，以及本轮识别的
「dual-character-comparison-infographic 噪声模板」「audience-vs-subject 混淆」等系统性模式
是否被修复。

## 14. 核心文件索引

- Query 级完整结果：`final/automated_relevance_query_level_results.csv` / `.jsonl`
- 结果级完整结果：`final/automated_relevance_result_level_results.csv` / `.jsonl`
- 汇总统计：`final/automated_relevance_summary.json` / `.md`
- 人工复核队列：`final/automated_relevance_manual_review_queue.csv`
- Rewrite 专项：`summaries/rewrite_relevance_analysis.csv` / `rewrite_relevance_summary.md`
- 0 结果 / Low-result 专项：`summaries/zero_result_relevance_analysis.csv` /
  `summaries/low_result_relevance_analysis.csv`
- 第二轮复核明细：`review/second_pass_review.csv`、`review/disagreement_cases.csv`、
  `review/adjudication_report.md`、`review/random_pass_audit.csv`
- 完整性报告：`final/automated_relevance_integrity_report.md`
- 文件清单：`final/automated_relevance_file_manifest.json`
- 工作区安全检查：`WORKTREE_SAFETY_REPORT.md`
