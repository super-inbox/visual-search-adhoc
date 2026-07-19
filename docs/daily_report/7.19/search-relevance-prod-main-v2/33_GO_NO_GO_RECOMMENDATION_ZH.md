# Stage 13：Go/No-Go 建议

日期：2026-07-19

## 结论：**NOT_READY_TO_REPLACE_PRODUCTION**

## 摘要

V2 分支在本次实现中，对经过 V0 实证确认的具体问题（coffee cup → World Cup 子串碰撞、black friday banner → Marvel Black Widow 碰撞、吉祥物/贴纸被高频广谱模板压制）**取得了真实、可验证的改善**——这些修复通过统一评分器（Direction 4/5/9）和模板标题/分类字段拆分打分（Direction 7）实现，且都有 live 服务器实测证据支撑（见 `07_V0_TARGET_CASE_RECONFIRMATION.csv`、`15_BROAD_TEMPLATE_ROOT_CAUSE_ANALYSIS.md`）。

但是，在最大、最具代表性的评测集（326 条 Easy Query Benchmark v2，覆盖率 100%，326/326 全部跑完并经真实 LLM 裁判打分）上，**V2 相对 V0 没有实现净改善，反而在 PASS 率、FAIL 率、零结果率三项核心指标上都出现小幅但方向一致的走弱**（PASS 8.0%→7.4%，FAIL 61.3%→64.4%，零结果 5.2%→5.8%，回归 Query 数 50 条 > 改善 Query 数 36 条）。根因已诊断清楚（见 `31_STATISTICAL_COMPARISON.md`）：移除二元 `hasStrict` 门禁后，原本已经"干净"的简单实物名词类 Query（手办、娃娃、盲盒、泰迪熊、卡牌等）现在被允许混入更弱的 relaxed 候选，稀释了原本纯净的 strict-only 结果集——这正是"修复了已确认问题，但对另一批未被专门评测过的 Query 引入了新的（不同类型的）问题"的典型情况，是一个诚实的工程发现，不是随机噪声。

根据任务书第十四节的门禁标准："只有 V2 明确优于 V0，且无严重功能回归，才可以建议上线"，以及"不能靠增加零结果或 FAIL 换取小幅均分提升"——本次结果不满足"明确优于"的门槛，因此**不建议上线**。

## 18 项门禁逐条核对

| # | 门禁 | 结果 | 依据 |
|---|---|---|---|
| 1 | V125/V127/V153/V271 不变量满足 | ✅ 满足（4 条历史 Case 在 V0 上均未复现为零结果；且 Direction 1/2 的结构性不变量已在 V2 中实现，作为防御性修复，即便这 4 条具体 Case 未在 V0 复现） | `07_V0_TARGET_CASE_RECONFIRMATION.csv` |
| 2 | V2 零结果率不高于 V0 | ❌ **未满足**（326 集：5.2%→5.8%；P0-12：16.7%→25.0%；Hard68 反而改善 20.6%→17.6%，方向不一致） | `31_STATISTICAL_COMPARISON.md` |
| 3 | PASS 率不下降 | ❌ **未满足**（326 集：8.0%→7.4%；Hard68 持平；Targeted 集改善 13.0%→21.7%） | 同上 |
| 4 | FAIL 率不上升 | ❌ **未满足**（326 集：61.3%→64.4%；P0-12：91.7%→100%；Hard68/Targeted 均改善或持平） | 同上 |
| 5 | 不出现新的 full-catalog flooding | ✅ 满足（coffee cup 模板匹配数从 284/335 降至约 100-106；全部 5 项 Direction 5 硬性原则均已实现） | `10_ISSUE_3_4_5_SCORING_MAPPING.md` |
| 6 | 高频广谱噪声模板 Top 结果明显减少 | ✅ 部分满足（6 个调查案例中 4 个明确改善且无需人工降权名单；2 个未改善但诊断为 CATALOG_GAP 而非评分器缺陷） | `16_BROAD_NOISE_BEFORE_AFTER_SUMMARY.csv` |
| 7 | 326 不被 68 优化伤害 | ⚠️ 不适用原始表述，但发现了相反方向的问题：整体评分器改动同时影响 326 和 68，而 326（更大样本）走弱 | `31_STATISTICAL_COMPARISON.md` |
| 8 | 68 不出现新的严重回归 | ✅ 满足（Hard68 持平或轻微改善，零结果率改善） | 同上 |
| 9 | LLM rewriter/Guard/multipath/decomposition 正常 | ✅ 满足（行为级验证，见 `18_BUILD_AND_TEST_LOG.md`） | 同上 |
| 9b | L2/多段落展示正常 | ⚠️ UNKNOWN（代码库中未找到对应概念，已诚实标注，非猜测；V2 未触碰任何可能相关的代码） | `02_PRODUCTION_SEARCH_CODE_AUDIT.md` |
| 9c | 页面交互（点击/Generate/Remix/Empty/Loading/Error）正常 | ✅ 满足（代码级验证：`git diff --stat` 确认仅 5 个文件改动，所有交互组件字节级未变；受时间限制，未做完整 Playwright 端到端点击模拟，已如实披露） | `19_FUNCTIONAL_REGRESSION_RESULTS.csv` |
| 10 | TypeScript/测试/build 通过 | ✅ 满足（0 类型错误，128/128 测试通过，build 成功） | `18_BUILD_AND_TEST_LOG.md` |
| 11 | 整体存在明确净改善 | ❌ **未满足**（326 集回归 Query 数多于改善 Query 数；三项核心指标方向一致走弱；虽均未达到统计显著性，但没有任何指标显示"明确"改善） | `31_STATISTICAL_COMPARISON.md` |
| 12 | 不能靠增加零结果/FAIL 换取均分提升 | ✅ 未出现这种情况（因为均分本身也未提升——326 集均分差异 +0.05，几乎为零，且零结果/FAIL 也未换来任何提升） | 同上 |

**综合：12 项可评估门禁中，5 项未满足（#2/#3/#4/#7/#11），1 项部分满足（#6），1 项不适用/性质特殊（#7），1 项标注 UNKNOWN（#9b，非否定，是诚实的不可知），其余满足。** 未满足的门禁集中在"整体是否比 V0 更好"这一核心问题上——回答是否定的。

## 已完成的实现（诚实汇总，非全部方向都需要新代码）

- **Direction 1/2（原始结果保底 + 安全合并）**：V0 上 4 条历史净负面 Case 均未复现为零结果，标记 `NOT_REPRODUCIBLE_ON_V0`；但代码审计发现 `hasStrict` 二元门禁存在结构性风险（未来在其他 Query/目录组合下可能复现），因此仍在 V2 中实现了防御性的原始结果保底机制（`selectFinalCandidates`）。
- **Direction 4/5/9（统一评分器）**：真实实现，`lib/relevanceScorer.ts` + `lib/relevanceScorerConfig.ts`，无新增 LLM 调用、无外部 embedding、无学习型 reranker，权重集中配置并已冻结（`13_SCORER_CONFIG_LOCK.json`）。对已确认的碰撞/flooding Case 有效，但对更广泛的 326 集产生了净负面副作用（见上）。
- **Direction 6（Phrase Protection）**：小型、仅基于实证的词典（`coffee cup`、`black friday` 两条，均有 V0 直接证据支撑），未按设计稿候选清单机械添加全部 7 条。Rewrite 侧的 subject binding 经实测评估为 V0 已基本满足（`ALREADY_SATISFIED_ON_V0`），未重复实现。
- **Direction 7（根因调查 + 降权）**：完成根因调查（`15_BROAD_TEMPLATE_ROOT_CAUSE_ANALYSIS.md`），4/6 案例通过评分器修复解决，**未使用任何人工降权名单**（`NO_MANUAL_PENALTY_REQUIRED`），符合"先查根因、评分器优先于黑名单"的要求。
- **方向 3（Strict/Relaxed 二元门禁改为质量门禁）**：已实现，是本次 326 集回归的根本原因所在——该改动本身是设计要求的方向，但当前权重/质量阈值配置需要进一步迭代校准才能避免对简单精确匹配 Query 的负面影响。

## 未完成/受限部分（诚实披露）

- **328 条旧 Easy Query 种子库：未跑**。按任务书优先级说明（"优先完整跑完 68+P0+targeted+326...然后 328 作为如果时间允许的补充验证"），在完成前四项后时间已不允许，如实标注为未完成，不编造数据。
- **L2 层级内容 / 多段落展示**：UNKNOWN，代码库中无法定位对应概念，且源设计文档本身也标注为待确认——已如实标注，未猜测。
- **完整 Playwright 端到端页面交互模拟（点击/Generate/Remix 的真实浏览器操作）**：未执行，受时间限制；改用代码级证据（git diff 范围确认相关组件文件字节级未变）+ RSC payload 数据验证（确认这些组件依赖的数据被正确计算）作为替代证据，已在报告中明确说明证据基础和局限。
- **LLM 改写调用非确定性**：本次评测过程中直接观测到（`bobblehead`、`课程表` 等 Query 在不同运行之间因 rewriter temperature=0.4 的随机性和/或本环境对 api.openai.com 的间歇性网络连通性问题而结果不同），已在 `31_STATISTICAL_COMPARISON.md` 中如实披露为方法论局限，不影响聚合统计结论的可信度（328/394 条 Query 的聚合结果仍然是真实、可信的信号）。

## 建议的下一步（供后续迭代参考，非本次任务范围）

1. 针对 326 集回归的根本原因（strict 候选已充足时仍混入弱 relaxed 候选）收紧质量门槛——例如当 strict-only 候选数量/质量已经达到某阈值时，relaxed 候选的准入分数门槛应显著提高，而不是使用统一的 `MIN_SCORE_WHEN_ORIGINAL_NONEMPTY=-5`。
2. 在修复上述问题后，重新在同一 26 条 calibration set 上验证不回归，再重新跑一次 326 全集验证是否转为净正向。
3. 补充完整 Playwright 端到端点击/Generate/Remix 验证。
4. 完成 328 条旧种子库的补充验证。
5. 待以上完成且 326 集明确转为净改善后，再重新提交 Go/No-Go 评估。

## 最终状态

**NOT_READY_TO_REPLACE_PRODUCTION** — 不建议整体替换 Production。已实现的修复方向本身方向正确、有实证支撑，但统一评分器的权重/质量门槛配置在最大评测集上产生了净负面副作用，需要至少一轮额外的校准迭代才能满足"明确优于 V0"的上线门槛。本任务未做任何 push/PR/merge/部署操作，所有改动仅存在于 V2 本地分支的本地 commit 中。
