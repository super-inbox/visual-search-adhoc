# Easy Query Search Solution Design · 会后修订 Changelog

日期：2026-07-18　性质：只读文档任务的变更记录，不涉及代码改动、不涉及 commit/push/PR。

- 源文件（会前最终版）：`docs/daily_report/7.17/easy-query-search-solution-design-v1/EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-17_zh.md`
- 新文件（会后最终版）：`docs/daily_report/7.17/easy-query-search-solution-design-v1/EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-18_POST_MEETING_ZH.md`
- 依据：老板书面反馈（本次任务输入原文）+ 会议最终结论（本次任务输入原文，无独立会议文字稿文件，结论以任务书面转述为准）

---

## 1. 核心变更对照表

| 会前 Design 内容 | 老板/会议反馈 | 会后处理 |
|---|---|---|
| 每项修复必须单独 Feature Flag，默认可单独关闭并回退 | 不需要逐项 Flag，基于以上改动建一个新分支，跟 main prod 做对比评测 | 改为：从 Production main 新建 V2 分支，与 V0 整体对比评测；开发用独立 commit，消融用独立 commit/临时配置/评测脚本，不构建正式运行时开关（新 Design 第 2.4、15 节） |
| 方向 3（strict/relaxed 二元门禁）独立成规则 | 是否需要引入相关性打分，或用相关性打分统一一下 | 纳入统一 scorer：strict/relaxed 改为质量/数量门禁，由评分决定去留（新 Design 第 10.1 节） |
| 方向 4（短语/整词/子串匹配）独立成规则 | 是否需要引入相关性打分，或用相关性打分统一一下 | 纳入统一 scorer：优先级通过 exact_phrase/whole_token/substring_penalty 三个评分维度体现（新 Design 第 10.2 节） |
| 方向 5（Rewrite 候选数上限）独立成规则 | 能用相关性打分统一一下吗 | 上限 + 路径质量分组合：单路径上限、总候选池上限、模板族数量控制、路径一致性/漂移评分共同作用（新 Design 第 10.3 节） |
| 方向 7：建立降权名单是可快速上线的配置级改动 | 这些为什么被广泛匹配到？是否有长期方案？ | 拆成三层：根因调查（Query→Result Trace）+ 短期降权（soft penalty，仅补充）+ 长期机制方案（评分维度、模板族饱和度控制、元数据治理）（新 Design 第 11 节） |
| Hybrid Search 方案（方案B）设计可与方案A部分并行 | 当前先做不带 Hybrid Search 的版本，基于 main prod 整体修复，结果显著优于 main prod 可上线 | 移到 V3 边界：本次新 Design 只保留 V3 定位和边界说明，不展开完整实现细节，当前阶段（V2）不做任何 Hybrid 接入（新 Design 第 17 节） |
| 上线风险：未专门列为门禁 | 之前遇到过 LLM rewriter、multi-path retrieval 在新上线时候被删除或 disable 的情况，这个要留意 | 新增正式上线门禁：LLM rewriter、Rewrite Guard、multi-path retrieval、decomposition、L2、多段落等必须行为级验证，不能只检查代码文件存在（新 Design 第 12 节） |
| 方向 1、2、6：写在最小修复方向表中，未单独强调"已认可" | 1 & 2，6 没问题，就应该这样 | 保留原方案，明确标注为已认可、无需重新设计（新 Design 第 8 节） |
| 开发基线：从 Production main 新建干净分支（表述较简略） | 就基于以上改动建一个新分支，跟 main prod 做对比评测；整体替换线上 prod 都没问题 | 澄清为：不是直接在 main 分支上写代码，而是新建 V2 分支作为 Candidate，V0（main prod）作为 Baseline，整体对比评测；整体替换 Production 是被认可的上线方式（新 Design 第 2.1、15 节） |

---

## 2. 保留了哪些历史数据

- 326 条 Benchmark v2 上 V0（Production）vs V1（旧 Candidate）的标签分布、零结果率、McNemar/Wilcoxon 统计结果；
- 旧 328 条种子库的历史交叉验证结论（零结果 3.66%→14.33%）；
- 196 次改写触发的全部指标（零结果救援率、虚假成功率、语义漂移分布）；
- 4 条 Rewrite 净负面 case（V125/V127/V153/V271）的具体定位；
- 四类根因分布（RETRIEVAL_RANKING/QUERY_UNDERSTANDING_REWRITE/CATALOG_GAP/AMBIGUOUS_INTENT，分母 244 条）；
- 代表案例清单（V009 吉祥物、V275/V276 元素周期表、V268/V032/V058/V154/V078 结果暴涨案例、V147/V242/V054/V083/V045 子串碰撞案例、V259/V221/V005/V289 CATALOG_GAP 案例）；
- 评测数据集清单（326 条 Easy Query、68 条 Hard Query、旧 328 条、12 条 P0 页面截图 Case）；
- 方法学限制（Top-5 only、无完整人工 Ground Truth、不使用 Recall@K/MRR/nDCG 作为强制指标）。

以上数据在新 Design 中均标注为历史事实，未重新计算，不作为 V2 的评测结果。

## 3. 删除了哪些旧要求

- "每项均挂独立 Feature Flag，默认可单独关闭并回退到该项改动之前的行为"——已被会议否定，新 Design 不再作为最终要求，仅在第 15 节以"会前要求，已被会议修改"方式历史引用；
- 方向 3、4、5 作为三套互相独立规则的写法——已被会议要求改为统一评分机制统一处理，不再单独成章；
- "降权名单是可以快速上线的配置级改动"作为方向 7 的完整方案——已被要求拆分为根因调查/短期/长期三层，降权名单降级为短期补充手段。

## 4. 新增了哪些章节

- 第 2 节：会后最终决策（完整转述会议结论，标注 `[会议决定]`）；
- 第 9 节：统一轻量文本相关性评分设计（评分维度结构、Score Breakdown、边界说明）；
- 第 10 节：方向 3、4、5 如何被评分统一（三个子节分别对应原方向 3、4、5）；
- 第 11 节：方向 7 根因调查、短期与长期方案（Query→Result Trace 设计、统一评分验证、短期降权、长期方案四个子节）；
- 第 12 节：现有功能回归保护（LLM rewriter/multi-path/L2/多段落门禁清单及验证方式）；
- 第 15 节：开发与提交建议（独立 commit + 整体对比评测，替代逐项 Feature Flag）。

## 5. 哪些内容仍为 proposed（未实现、未校准、待工程/会议进一步确认）

- 统一评分机制的具体维度权重（第 9.2 节）；
- Score Breakdown 的具体字段结构（第 9.3 节，设计建议非已实现类型）；
- Query→Result Trace 的具体字段结构（第 11.1 节）；
- 方向 5 的单路径/总池/模板族候选数具体上限数值；
- 短期降权名单的具体覆盖范围和规则数量（待根因调查产出后确定）；
- "显著优于 main prod"的具体数值门槛（会议未确认固定百分点，待首轮 V2 实验后与管理层确认）；
- V0 vs V2 统一采集方式具体选用浏览器导航还是 in-process harness。

## 6. 哪些问题仍为 UNKNOWN

- Production main 具体分叉 commit SHA；
- "L2 层级内容"在当前代码结构中的具体指代；
- 现有打分逻辑是否已融合 title+tags+category 多字段支持；
- 中英文分词/别名扩展路径统一的工作量评估（沿用会前 Design 的 P2 标注，本次会议未讨论）。

---

## 7. 质量核对结果（对应任务要求第十二节）

已对新 Design 文件（`EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-18_POST_MEETING_ZH.md`）做以下检查：

- 明确写明从 Production main 新建分支（第 2.1、5、15 节）：确认存在；
- 明确写明旧 Candidate（V1）冻结（第 2.1、5、6 节）：确认存在；
- 明确写明方向 1、2、6 已获认可（第 1、8 节）：确认存在；
- 明确写明方向 3、4、5 由 scorer 统一（第 1、9、10 节）：确认存在；
- 明确写明方向 7 先查根因（第 2.3、11.1 节）：确认存在；
- 明确写明降权名单只是短期（第 11.3 节）：确认存在；
- 明确删除逐项 Feature Flag 要求，并标注为"会前要求，已被会议修改"（第 2.4、15 节）：确认存在；
- 明确包含 LLM rewriter 回归门禁（第 2.5、12 节）：确认存在；
- 明确包含 multi-path retrieval 回归门禁（第 2.5、12 节）：确认存在；
- 明确包含 L2、多段落回归门禁（第 2.5、12 节）：确认存在；
- 明确当前不做 Hybrid（第 1、4、17 节）：确认存在；
- 明确显著改善未擅自写死百分点（第 1、14 节）：确认存在；
- 明确不能使用不同采集机制比较 V0 和 V2（第 13.2 节）：确认存在；
- 明确不把 MRR/nDCG/Recall@K 写成已有强制指标（第 3.6 节）：确认存在。

禁止残留表述检查（grep 全文，逐一确认未以"最终要求"形式出现，仅历史引用处标注"会前要求，已被会议修改"）：

- "每项必须单独 Feature Flag" / "每项默认单独关闭" / "必须通过 runtime flag 回滚每项"：未作为最终要求出现，仅在第 15 节以历史对照方式提及并明确标注已被修改；
- "V2 已实现" / "V3 已实现" / "Hybrid 已接入"：未出现；
- "已重新运行 326 条" / "已重新运行 68 条"：未出现（第 18.2 节明确声明"不声称已重新运行"）；
- "已提交 commit" / "已 push" / "已创建 PR"：未出现（第 18.2 节明确声明未做）；
- "PASS 必须提升 8%" / "PASS 必须提升 10%"：未出现，第 14 节明确声明会议未确认固定百分点。
