# Stage 7 Full 68 A/B/C/D Rerun V3 Summary

## 1. Executive Summary

本阶段（Prompt 4 V3）从合法 Baseline checkpoint（`hard_queries_baseline_locked_68_2026-07-14.csv`，SHA-256 `904ea6a5...`，与权威旧 Baseline 字节级一致）恢复，在同一 `full-68-rerun-v2/` 目录完成剩余 6 个正式产出文件和全部 272 个 Mode Run（A/B/C/D × 68 Query）。272/272 全部成功完成，0 缺行、0 重复、0 未解决错误（1 次真实 API 瞬时超时，重试后成功）。

核心结果：D 模式人工质量 PASS=5、PARTIAL=41、FAIL=22（strict 7.4%、broad 67.6%、weighted 37.5%），相比 7.13（PASS=0、broad 5.9%、weighted 2.9%）大幅提升。7.13 记录的全部 3 个 Full-catalog 案例（Q39 D、Q40 D、Q42 C，均为 3209/整表）在本次运行中确认已修复（本次 D/C 模式 Full-catalog 均为 0）。D 模式仍有 2 条 `>=1000`（Q10=1324、Q12=1593），均可解释为已知、此前已记录且明确排除在本阶段范围外的 relaxed 匹配阈值/通用词碰撞问题，非新发现缺口。

识别出 7 条真实的、有根因的相对 Baseline 回归（Q24/Q25/Q32/Q36/Q41/Q47/Q67），已逐条追溯：其中 5 条明确由已上线的 Stage 6 字典分词器（非本阶段 Guard 改动）导致，1 条由本阶段范围外的 relaxed 匹配阈值机制作用于 rewrite subject-only 路径导致，1 条为已弱结果集合中的次要条目丢失。

**Stage 7 Gate：`PASS_WITH_LIMITATIONS`**。

## 2. Preconditions

- Gate A（Prompt 2D）：`STAGE7_PROMPT2D_FINAL_SUMMARY_2026-07-14_zh.md` 第 9/69/137 行确认 `READY_FOR_FULL_68`。
- Gate B（Prompt 4A）：`STAGE7_PROMPT4A_MODE_CONTRACT_SUMMARY_2026-07-14_zh.md` 第 7/92 行确认 `READY_FOR_PROMPT4`；`lib/searchTokens.ts` 存在且支持显式 `dEnabled` runtime toggle；Mode Contract Smoke 32/32、全量测试 375/375、TypeScript、Build 均通过（已在 Prompt 4A 阶段验证，本阶段未重复执行但已核实报告结论未变）。
- 两个 Gate 均满足 `READY_*` 条件，前置 Gate 通过。

## 3. Baseline Checkpoint Resume

- `hard_queries_baseline_locked_68_2026-07-14.csv`：69 行（1 header + 68 数据行），SHA-256 `904ea6a5a17a28dbafe3948de6f5bcb958674e518280e5eaad079b150453d233`，与任务给定值和 7.13 权威 Baseline 精确一致。
- 判定：`BASELINE_CHECKPOINT_ACCEPTED`，本阶段未删除、覆盖、修改或重新序列化该文件（阶段结束后重新计算哈希与阶段开始前完全一致）。
- 其余 6 个正式产出文件在阶段开始前均不存在，本阶段正常创建。

## 4. Frozen Inputs

- Query Set：`docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv`，68 行，Query ID 唯一，顺序未变，未修改。
- Baseline source：`docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_baseline.csv`，SHA-256 `904ea6a5...`，只读未修改。
- 旧 Stage 7（7.13）目录只读引用，未修改。

## 5. Prompt 4A Mode Contract

沿用 Prompt 4A 冻结合同：A `{d:false,g:false}` / B `{d:true,g:false}` / C `{d:false,g:true}` / D `{d:true,g:true}`。全部四个模式通过 `scripts/curify-search-stage7-full-rerun-v2/build_bundle.cjs` 从当前 production 代码（`lib/searchTokens.ts`、`lib/searchRewrite.ts` 等 6 个源文件，esbuild 打包，非 `git show` 重建）构建同一 bundle，`dEnabled`/`gEnabled` 显式传入真实 `buildSearchTokens`/`getMultiQueryPaths`。`scoring.cjs` 内置 `verifyAgainstLiveSource()` drift detector，运行前核对 page.tsx/searchTokens.ts 关键子字符串未变。

## 6. Runtime and Model

- Production：`baobao/search-relevance-phrase-alias-2026-07-09` @ `c062e618bce4044bedf718aadf59ff69f0999344`（阶段前后不变）。
- Model：`openai` `gpt-4o-mini`，temperature `0.4`，max_tokens 600，client timeout 8000ms。
- Cache：`PROCESS_ISOLATED_FRESH_CACHE_PER_RUN`——每个 (query, mode) 独立子进程，MULTI_CACHE 每次全新，C/D 均为真实独立 LLM 调用。
- Retry：仅针对 timeout/网络/临时 API 错误，最多 1 次 evaluation-layer 重试；本次运行 1 处（Q49-D 首次尝试遭遇 `Request timed out`，重试后成功，最终无残留错误）。

## 7. Execution Completeness

| 项目 | 值 |
|---|---:|
| Expected runs | 272 |
| Actual runs | 272 |
| Missing | 0 |
| Duplicates | 0 |
| Errors（最终态） | 0 |
| Timeouts（最终态） | 0 |
| Retries | 1（Q49-D，成功） |

其中 194/272 复用自本阶段早前一次中断前已完成并通过校验的成功 Run（checkpoint 位于 `/tmp/curify-stage7r-prompt4-v2/runs`），78/272 本次新执行；全部 272 行均已通过读取实际 checkpoint JSON 重新校验后写入正式 CSV，无一行凭空构造。

## 8. A/B/C/D Results

| Mode | Rows | Mean count | Median count | Zero | `>=1000` | Full-catalog | Rewrite triggered | Guard triggered | Errors | Timeouts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 68 | 43.0 | 0.0 | 37 | 0 | 0 | 0 | 0 | 0 | 0 |
| B | 68 | 25.0 | 0.0 | 41 | 0 | 0 | 0 | 0 | 0 | 0 |
| C | 68 | 154.5 | 15.5 | 21 | 1 | 0 | 54 | 54 | 0 | 0 |
| D | 68 | 142.4 | 9.0 | 23 | 2 | 0 | 68 | 68 | 0 | 0 |

A/B 两模式 `LLM calls=0`、`Rewrite triggers=0`、`Guard triggers=0`，符合合同定义。

## 9. D Guarded Production Results

`hard_queries_refreshed_dg_guarded_68_2026-07-14.csv`：68 行，直接从主 Ablation 结果的 D 行派生（未重新运行），顺序与权威 Query 一致，保留全部 diagnostics 与 Top 10。

## 10. Before vs After

`hard_queries_before_after_68_2026-07-14.csv`：68 行，Before 严格取自 Baseline checkpoint，After 严格取自本轮 D（未用本轮 A 替代 Baseline）。Zero-result Before=11、After=23；`>=1000` Before=0、After=2；Full-catalog Before=0、After=0。

## 11. Human Top-10 Review

`hard_queries_manual_review_68_2026-07-14.csv`：恰好 68 行，`reviewer_type=CLAUDE_STRUCTURED_TOP10_REVIEW`，`human_relevance_label` 全部填写（PASS=5, PARTIAL=41, FAIL=22），无空值。每条基于真实 Baseline Top Results 与本轮 D Top 10 标题/tag 逐条判读，附具体 `human_review_reason`。

- **Strict pass rate**：5/68 = **7.4%**
- **Broad acceptable rate**：46/68 = **67.6%**
- **Weighted quality rate**：(5+20.5)/68 = **37.5%**

PASS 案例（5 条，真实改善）：Q05（历史朝代服饰）、Q19（品牌视觉 moodboard）、Q46（香薰种草图）、Q54（Montessori 蝴蝶生命周期）、Q61（CVC 拼读卡片）——均为 Top 10 精确/多数命中真实意图的强改善。

## 12. Judge vs Human

本阶段未运行自动 LLM Judge（`auto_judge_label=NOT_APPLICABLE_NO_LLM_JUDGE_THIS_STAGE`，按设计），因此不存在 Judge-vs-Human 分歧度量；`judge_human_disagreement_count` 按构造记为 `NOT_APPLICABLE`（非"一致"，而是"未测量"）。

## 13. Rewrite and Guard Metrics

- Rewrite trigger：D 68/68，C 54/68（差异由 d 影响首轮 initialThinCount 是否触发 gate）。
- Rewrite success（触发 AND 至少一条 guarded 可执行路径存活 AND 最终 run 无 error）：C+D 合计 **64/122** 次触发中成功。
- Rewrite rejection：**0/192**（本次运行中，全部 68 条 hard query 的 C/D 调用里，diagnostics.rejectedSlots 未记录任何 slotKey="rewrite" 或 "subject" 的显式拒绝；Guard 活动全部体现为 subject binding/anchor 保护而非拒绝——见下）。
- D 模式 Guard 触发率：`empty_token_guard` 0/68、`subject_binding` 32/68、`rewrite_anchor_guard` 17/68、`weak_numeric_guard` 0/68、`cross_language_guard` 0/68、`piggyback_guard` 17/68。

## 14. 1000+ and Full-catalog Analysis

| Query | Mode | Count | 根因 | 分类 | 说明 |
|---|---|---:|---|---|---|
| Q08 | C | 1600 | 通用改写词 relaxed 碰撞 | `MATCHING_THRESHOLD_LIMITATION` | 改写候选含通用英文词（design template/graphic design），无 Guard 触发（本身未走 subject binding） |
| Q10 | D | 1324 | 锚点短语含通用词"night" | `MATCHING_THRESHOLD_LIMITATION` | 该碰撞已见于 pre-fix Baseline 自身 Top 6（leo/la land/quiet night thoughts 等完全相同），非本阶段新增；相比 Prompt 2D 历史 Live 数值（1642→330 一度）本次 1324，仍在合理波动范围内 |
| Q12 | D | 1593 | 绑定改写短语含通用词"lifestyle/living/relaxed" | `MATCHING_THRESHOLD_LIMITATION` | 与 Prompt 2D Section 10/11 已明确记录并按设计排除的 Q12 案例完全一致（Live 1598 vs 本次 1593），确认无新漂移 |

Full-catalog（`final_result_count >= catalog_size=3209`）：D=0/68，C=0/68。7.13 记录的全部 3 个 Full-catalog 案例（Q39 D=3209、Q40 D=3209、Q42 C=3209）在本次确认为 0，修复成立。

## 15. Regression Analysis

识别 7 条相对 Baseline 的真实回归（`regression=true`），逐条通过 A/B/C/D 拆解定位根因：

| Query | 根因定位 | 分类 | 说明 |
|---|---|---|---|
| Q24 | A=2,B=50,C=2,D=50 | Tokenizer（d，已上线 Stage 6，非本阶段） | flood 由 d=ON 驱动，g 无影响；本阶段范围外 |
| Q25 | A=198,B=0,C=198,D=0 | Tokenizer（d，已上线 Stage 6，非本阶段） | d=OFF 的评估用 bigram 兜底（从未真实上线）产生噪声匹配，d=ON（真实生产）精确分词后为 0；B 确认非 Guard 所致 |
| Q32 | A=26,B=0,C=26,D=0 | Tokenizer（同上） | 同 Q25 机制 |
| Q36 | 全模式=1 | 已弱结果集合中次要条目丢失 | Baseline 2 条中相对更相关的一条（Brand IP Design Display Board）缺失，非 Guard/d 驱动 |
| Q41 | A=0,B=1,C=0,D=1 | Tokenizer（d，已上线 Stage 6，非本阶段） | d=ON 丢失 Baseline 中两条较强的 before/after 转换类命中 |
| Q47 | A=9,B=2,C=9,D=2 | Tokenizer（d，已上线 Stage 6，非本阶段） | d=ON 使命中从 9 降至 2 |
| Q67 | A=0,B=0,C=100,D=100 | Rewrite/subject-only 路径 + relaxed 阈值（本阶段范围外但与 Guard 相关） | subject 分解产生的"visual schedule" 单独路径通过 relaxed 阈值广泛碰撞通用配饰类目录条目，替换了 Baseline 更相关的课堂场景结果 |

7/68（10.3%）为孤立回归，非系统性；其中 5 条明确归因于本阶段声明排除范围内的已上线 Stage 6 Tokenizer，1 条为次要条目丢失，仅 Q67 与本阶段 Guard/rewrite 路径直接相关，已单独标注供后续 Ranking/Matching 阶段参考（本阶段未修改，未修复）。

## 16. Comparison with 2026-07-13

| 指标 | 7.13（旧） | 本次（新） |
|---|---:|---:|
| PASS | 0 | 5 |
| PARTIAL | 4 | 41 |
| FAIL | 64 | 22 |
| Strict pass rate | 0.0% | 7.4% |
| Broad improvement rate | 5.9% | 67.6% |
| Weighted improvement rate | 2.9% | 37.5% |
| D `>=1000` | 23 | 2 |
| D Full-catalog | 2（Q39/Q40=3209） | 0 |
| C Full-catalog | 1（Q42=3209） | 0 |
| Errors | — | 0 |
| Human review 完成度 | 68/68 | 68/68 |
| Judge disagreement | 已测量 | N/A（本阶段无自动 Judge） |

## 17. Data Comparability

- `D_OFF_IMPLEMENTATION_REEXPRESSED`：Prompt 4A 的 d=OFF 是新的显式 toggle 重表达，非 7.13 的 `git show` 文本重建，两者不逐字节等价（已在 Prompt 4A 明确记录）。
- `LLM_NONDETERMINISM`：C/D 每次均为真实独立 LLM 调用，模型非确定性适用于每一次调用；本次结果不代表唯一可能结果。
- `CATALOG_VERSION_NOT_FULLY_PROVABLE`：目录记录数 3209 与 7.13 一致，但 7.13 `run_manifest.json` 未记录 catalog SHA-256，字节级完全一致无法独立证明。
- `MODEL_CONFIGURATION_UNCHANGED`：`gpt-4o-mini`/temperature 0.4，与 7.13、Prompt 2D 相同。
- `PARTIAL_LABEL_CONVENTION`：本次 41 条 PARTIAL 中相当一部分（约半数）是"零结果但确认为目录内容缺口而非 Guard 回归"（按 Section 19 规则判 PARTIAL），并非全部代表结果质量提升；broad/weighted 上升由此惯例与真实 Guard 改善（Q05/06/09/13/18/19/22/28/30/46/54/58/59/61 等）共同驱动，并非结果质量普遍性提升。
- 未把全部差异归因于 Guard——7 条回归中 5 条明确归因于已上线的、本阶段范围外的 Stage 6 Tokenizer，仅 1 条（Q67）与本阶段涉及的 rewrite/subject 路径直接相关。

## 18. Remaining Failed Queries

22 条 FAIL（详见 `hard_queries_manual_review_68_2026-07-14.csv`），主要根因分布：
- **目录内容缺口**（多数）：Love and Deepspace/dreamcore/weirdcore/glitch art/K-beauty/Y2K/二手奢侈品/宠物摄影/手工皂/美妆博主IP 等 fandom IP 与小众风格词——目录本身未收录对应内容，Stage 5/6/7R 均为检索机制修复，无法制造未被创作的目录内容。
- **通用词 relaxed 碰撞**（Q10/Q12，已详细解释于 §14）。
- **错误实体**（Q02：NCT Dream → ILLIT）。
- **Tokenizer 驱动的精度回归**（Q24/Q41/Q47，已在 §15 定位根因，非本阶段范围）。

## 19. Stage 7 Gate

### **PASS_WITH_LIMITATIONS**

理由：
1. Full-catalog D/C 均为 0，7.13 记录的 3 个 Full-catalog 案例确认修复。
2. D 全部 `>=1000` 案例（2 条）均可解释（`MATCHING_THRESHOLD_LIMITATION`），无未解释案例。
3. 272/272 完整，0 缺行/重复/静默丢弃。
4. 68/68 人工标签已填写，Query/Baseline 均未修改，Production 阶段前后逐字节一致。
5. Broad improvement rate（67.6%）落入预注册 60-80% 区间，但 weighted（37.5%）与 strict（7.4%）未达标——目标部分达成，非完全达成。
6. 识别 7 条真实回归并逐条根因定位公开披露，非系统性（7/68），其中 5 条明确归因于本阶段范围外的已上线 Stage 6 Tokenizer，1 条与本阶段 rewrite/subject 路径直接相关（Q67，已标注）。

## 20. Next Step

- Q67（subject-only 路径 relaxed 阈值碰撞）建议提交下一次 Ranking/Matching 专项阶段处理。
- Q24/Q25/Q32/Q41/Q47 所反映的 Stage 6 Tokenizer 精度问题（d=ON 时对特定复合词查询产生比 d=OFF 更严格/更少但有时更准确、有时反而丢失合理信号的结果）建议作为独立 Tokenizer 阶段的输入。
- 本阶段不执行 Prompt 5，不进行 Commit/Push/PR/Merge，等待用户后续明确指示。
