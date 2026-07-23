# Full-326 对比报告 — Cluster A/B Latest Fix (commit 0e794cd9)

日期：2026-07-22 · 分支：`baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19` · 评测对象：`0e794cd9`

---

## 1. 执行结论

**FINAL_STATUS: NEEDS_MORE_FIXES**

326 题全量评测已完整跑通（326/326，0 技术错误），工程验证全部通过。相对 production baseline 和上一版 candidate，
本次修复在聚合指标上都是净正向（PASS 提升、FAIL 下降、平均分提升），但 **Cluster A 和 Cluster B 各自的旗舰代表案例
（酒标类多词查询的 3/4、以及最关键的 `笔袋`）在全量真实流水线中仍未修复**，且新引入了 4 个"新增零结果"回归。评测本身已
完整、可信、可直接呈现做决策依据，但代码本身**不建议**在此刻直接晋升到生产环境——建议先处理 `笔袋` 旗舰案例和
Cluster A 剩余的 coverage-gate/isolated-hit-cap 机制，再重新跑一遍全量评测。

---

## 2. 评测版本与配置

| | production baseline | previous candidate | **latest candidate（本次）** |
|---|---|---|---|
| commit | `c550856e`（2026-07-21 时的 main，detached） | `1e56e3f0`（Cluster A/B 修复前） | **`0e794cd9`（Cluster A + B 均已落地）** |
| 结果来源 | 复用 7/21 评测的 `BASELINE_EASY326.csv`（未重新采集） | 复用 7/21 评测的 `CANDIDATE_EASY326.csv`（未重新采集） | 本次新采集 `CANDIDATE_LATEST_EASY326.csv` |

- 评测输入：`easy_query_bank_v2_2026-07-16.csv`，SHA-256 `c5b1368e33ab601884ad91aff21802c64391bee781b6daa2f3ef50e4d54a08c6`，
  326 条唯一查询，0 重复，0 缺失。
- 评测方法：与 7/19、7/21 完全相同的方法链路——`collector.mjs` 抓取真实 `next start` 服务器渲染出的 RSC flight
  payload（即真实生产检索/重写/多路合并/最终排序的结果，不是自实现的镜像逻辑），`judge.mjs` 用 `gpt-4o-mini` +
  rubric-v1.1 确定性打分（Top 5 证据），Top K = 5（该方法学从未支持 Top 10，本报告如实标注为"该字段不可用"而非
  编造）。
- **与此前运行的重要差异（必须披露）：**
  1. **catalog 内容发生了变化**：`public/data/nano_inspiration.json` 记录数在 3403 条不变，但字节内容在 commit
     `b4116648`（"strip hallucinated merch/POD aliases from 4 non-mockup templates"）发生变化，SHA-256 从
     `7ec2983a...`（`1e56e3f0`/`6efdd904` 使用）变为 `32015cab...`（`0e794cd9` 使用）。这是**数据变更**，不是
     纯代码/打分逻辑变更，可能影响与 previous candidate 的严格可比性，但影响范围限定在 4 个模板的别名字段。
  2. Scorer 版本号从 `v1.1.0-2026-07-21` 升级为 `v1.2.0-2026-07-22`；`SCORER_WEIGHTS` **未变**，仅上游的主体
     （subject）推导逻辑改变（新增 `lib/searchSubject.ts`）。
  3. Production baseline 与 previous candidate 的结果文件是**复用 2026-07-21 的历史文件**，未重新抓取当前的
     远程 `main`（按章程要求，避免"隐性替换历史基线"）。

---

## 3. 工程验证

| 检查 | 命令 | 结果 |
|---|---|---|
| 单元测试 | `npx vitest run --config vitest.unit.config.ts lib/__tests__/relevanceScorer.test.ts lib/__tests__/searchSubject.test.ts` | **53/53 通过**（含 16 个新增 `searchSubject.test.ts` 用例） |
| TypeScript | `npx tsc --noEmit` | **0 错误** |
| 生产构建 | `npm run build` | **构建成功**（"Compiled successfully"），已知无关警告 `MISSING_MESSAGE: blog.qaBotToTask`（博客 i18n 缺失，与搜索无关，非阻塞） |

**ENGINEERING_GATE: PASS**（详见 `16_ENGINEERING_VALIDATION.md`）

---

## 4. 最新 326 总体结果（0e794cd9）

| 指标 | 数值 |
|---|---:|
| PASS | 38 |
| PARTIAL | 86 |
| FAIL | 195 |
| UNJUDGABLE | 7 |
| **合计** | **326** |
| PASS 率 | 11.66% |
| 零结果数 | 20 |
| 低结果数（1-4条） | 18 |
| 平均结果数 | 46.6 |
| 中位数结果数 | 28.5 |

---

## 5. 与 Production Baseline 对比

| 指标 | production (24/83/207/12) | **latest (38/86/195/7)** | Δ |
|---|---|---|---|
| PASS | 24 | **38** | **+14** |
| PARTIAL | 83 | 86 | +3 |
| FAIL | 207 | **195** | **-12** |
| UNJUDGABLE | 12 | 7 | -5 |
| PASS 率 | 7.36% | 11.66% | +4.3pp |
| 零结果 | 23 | 20 | -3 |
| 低结果 | 19 | 18 | -1 |
| 平均分 | 14.51 | 18.95 | +4.44 |

**状态迁移（vs production）：改善 57 题，回归 38 题，不变 231 题。改善 > 回归，聚合层面是净正向。**

主要迁移矩阵：FAIL→PARTIAL 28、PARTIAL→FAIL 23、FAIL→PASS 9、PARTIAL→PASS 12、PASS→PARTIAL 8。可以看到 FAIL→PARTIAL
和 PARTIAL→FAIL 几乎相当（28 vs 23），说明"净改善"很大程度上来自 FAIL→PASS（9）和 PARTIAL→PASS（12）这类真正的
质变，而不仅仅是标签在低档位之间的漂移。

---

## 6. 与上一版 Candidate 对比（Cluster A/B 修复前 vs 修复后）

| 指标 | previous candidate (37/76/203/10) | **latest (38/86/195/7)** | Δ |
|---|---|---|---|
| PASS | 37 | 38 | +1 |
| PARTIAL | 76 | 86 | +10 |
| FAIL | 203 | 195 | -8 |
| UNJUDGABLE | 10 | 7 | -3 |
| 零结果 | 20 | 20 | 0（**集合不同，见下**） |
| 低结果 | 13 | 18 | +5 |
| 平均分 | 16.97 | 18.95 | +1.98 |

**状态迁移（vs previous candidate）：改善 30 题，回归 23 题，不变 273 题。**

这就是 Cluster A + Cluster B 这两次修复本身带来的净效果：FAIL 减少 8 题、UNJUDGABLE 减少 3 题、平均分提升近 2 分，
改善题数大于回归题数（30 > 23）。但注意零结果总数**持平**（20→20）——这不是"没有变化"，而是 3 个查询新增零结果
（`puzzle`、`优惠券`、`diploma`）同时 3 个查询走出零结果（`bobblehead`、`场景模型`、**`积分卡`**），一进一出刚好抵消。

---

## 7. Cluster A 结果

Cluster A = "头名词 + 格式词"多词查询（如 wine label、字母海报、巧克力礼盒），旧逻辑把查询主体误判为格式词
（label/海报/礼盒），导致携带格式词的错误内容反而通过 subject-presence 检测压过真正的头名词结果。修复方案：新增
`lib/searchSubject.ts` 的 `subjectUnits()`，从查询中剔除格式词，只用主题词判断 subject-presence。

| 查询 | production | previous candidate | **latest** | 结论 |
|---|---|---|---|---|
| wine label（英文） | PARTIAL | FAIL | **PASS** | **修复成功** |
| 酒标（中文同义） | PARTIAL | FAIL | FAIL（不变） | **未修复** |
| 字母海报 | PARTIAL | FAIL | FAIL（不变） | **未修复** |
| 巧克力礼盒 | PARTIAL | FAIL | FAIL（不变） | **未修复** |
| 人体图解（保留胜利被打破的案例） | PASS | FAIL | **PARTIAL** | **部分恢复**，未完全回到 PASS |
| coffee package（同类形态） | PARTIAL | FAIL | **PASS** | 修复成功 |
| cosmetic package（同类形态） | PARTIAL | FAIL | **PARTIAL** | 部分恢复 |

**代码文档（`docs/search-relevance-v2r3-r1-2026-07-21.md`）声称"四个案例均通过 scorer 实测确认修复"，但全量真实流水线
结果显示：4 个核心案例中只有 1 个（wine label 英文）完全修复，1 个（人体图解）部分恢复，2 个（字母海报、巧克力礼盒）
完全未变化。** 推测原因（基于结果形态的合理推断，非直接插桩验证）：Cluster A 的根因文档本身指出是**两个机制共同作用**
（`REQUIRED_TERM_COVERAGE_MIN_RATIO` 覆盖率门槛 + `ISOLATED_HIT_SCORE_CAP` 孤立命中封顶），而这次的 Fix A 只修复了
subject-presence 判断这一个上游输入，即便主体判断已经正确，仍可能被另一个下游机制继续压制。

另：`black friday banner` 按文档披露本就不在这次修复范围内（受 protected-phrase 逻辑影响，需要单独的 lever），
全量结果确认与文档一致——**没有变坏，但也确实没修**。

---

## 8. Cluster B 结果（含 笔袋）

Cluster B = 稀疏单 token 中文查询（如 笔袋、挂件、娃娃），因宽松的"永不为空"扩展 + 单 token 的
`titleHit || tagsHit` bigram 捷径，导致离题的非原始内容排在真正精确匹配之上。这是 `6efdd904`（Fix B）针对的问题，
本次 `0e794cd9` 把该分支也并入了统一的 `subjectUnits()`。

| 查询 | production | previous candidate | **latest** | 结论 |
|---|---|---|---|---|
| **笔袋（旗舰案例）** | PARTIAL | FAIL | **FAIL（不变）** | **未修复**——Top5 前两位仍是两个完全无关的科技新闻类模板（"microsoft ai dilemma 07 case google gemini"），`Stationery` 排第 3 |
| pencil case（英文对应） | PARTIAL | FAIL | FAIL（不变） | 未修复，结果数进一步降到 3（低结果） |
| 挂件 | PASS | FAIL | **PASS** | **修复成功**，恢复到 production 水平 |
| 娃娃 | PARTIAL | FAIL | FAIL（不变） | 未修复 |
| 泰迪熊 | PARTIAL | FAIL | FAIL（不变） | 未修复 |
| 单词卡 | PARTIAL | FAIL | FAIL（不变） | 未修复 |
| 积分卡（7/21 报告点名的新增零结果案例） | FAIL（368条，错位） | FAIL（0条） | **PARTIAL（87条）** | **修复成功**，走出零结果 |
| 会员卡（积分卡的姊妹案例） | FAIL（368条） | FAIL（0条） | FAIL（0条，不变） | **未修复**，仍是零结果 |

**这次修复被命名为"Fix B — single-token subject-presence bypass（笔袋 flagship）"，但旗舰案例`笔袋`本身在全量真实
流水线中仍未修复，且仍比 production baseline 差（production 是 PARTIAL，现在是 FAIL）。** 6 个 Cluster B 代表案例
中只有 1 个（挂件）真正修复。`stationery`（文具）这个垂类整体呈现净回归：4 题相对 production 回归、0 题改善——
恰恰是这次修复本应改善的垂类，聚合结果反而更差。

补充发现（非原 Cluster B 分类范畴，评测过程中的观察）：压住 `笔袋`/`pencil case` 的那两个"microsoft ai dilemma"
模板，看起来更像是**某个具体模板的标签/别名打错了**（一个科技新闻模板完全没有理由匹配"笔袋"），而不只是通用的
"宽松扩展"问题——这可能是一个比调整打分逻辑更直接、更容易修的 catalog 数据卫生问题，值得单独排查。

---

## 9. 主要改善案例

| 查询 | production → latest | 说明 |
|---|---|---|
| wine label | PARTIAL → PASS | Cluster A 修复的核心证据 |
| coffee package | PARTIAL → PASS | Cluster A 同类形态修复 |
| 挂件 | PASS(经历FAIL后)→PASS | Cluster B 唯一完全修复案例，恢复到原始水平 |
| 积分卡 | FAIL(零结果) → PARTIAL | 7/21 报告点名的新增零结果案例被修复 |
| 促销海报、sale poster 等（poster_specific 垂类） | 多题 FAIL/PARTIAL → PASS/PARTIAL | poster_specific 垂类整体 +8 改善，仅 1 题回归，是全部 326 题里聚合表现最好的垂类 |

（完整列表见 `07_IMPROVEMENTS.csv`，57 行）

---

## 10. 主要回归案例

| 查询 | production → latest | 严重程度 | 说明 |
|---|---|---|---|
| diploma | FAIL(101条) → FAIL(0条) | **高** | 新增零结果，结果数在三版之间持续单调下滑（101→6→0），推测是候选项被逐步过滤丢失，而非查询本身无内容（production 曾有 101 条结果） |
| 会员卡 | FAIL(368条) → FAIL(0条) | **高** | 新增零结果（相对 production；相对 previous candidate 是持续零结果） |
| 笔袋 | PARTIAL → FAIL | 高（Cluster B 旗舰目标未达成） | 见第 8 节 |
| pencil case | PARTIAL → FAIL | 高 | 见第 8 节 |
| 信封（envelope） | PASS → PARTIAL | 中 | stationery 垂类回归之一 |
| 书签（bookmark） | UNJUDGABLE → FAIL | 中 | stationery 垂类回归之一 |
| banner 垂类多题 | 多为 PARTIAL/UNJUDGABLE → FAIL | 中高 | 该垂类净回归 +4，是回归最多的垂类 |

（完整列表见 `08_REGRESSIONS.csv`，38 行；4 个新增零结果回归见 `12_REMAINING_FAILURE_ROOT_CAUSES.csv` 中
`candidate_loss_regression` 分类）

---

## 11. Zero / Low-result 变化

| | production | previous candidate | latest |
|---|---:|---:|---:|
| 零结果 | 23 | 20 | 20 |
| 低结果 | 19 | 13 | 18 |

- **相对 production**：净减少 3 个零结果（2 个新增：`会员卡`、`diploma`；5 个恢复：`扭蛋`、`diorama`、
  `advertisement`、`折扣传单`、`数学练习册`）。
- **相对 previous candidate**：总数持平（20→20），但集合不同：3 个新增零结果（`puzzle`、`优惠券`、`diploma`），
  3 个恢复（`bobblehead`、`场景模型`、`积分卡`——后两者正是 7/21 报告点名的目标修复案例）。
- **低结果相对 production 从 19 升到 18（微降），但相对 previous candidate 从 13 升到 18（+5）**——包含
  `pencil case` 这个 Cluster B 案例（结果数从 21 一路缩到 3）。
- 4 个新增零结果案例（`diploma`、`会员卡`、`puzzle`、`优惠券`）全部 `ok=true`、无采集错误、`rewrite_triggered=false`，
  排除了执行错误和重写抑制两种可能，形态更符合"候选项在过滤链路中被逐步丢失"（candidate loss），而不是数据库中
  本来就没有相关内容。

（详见 `09_ZERO_LOW_RESULT_ANALYSIS.csv` / `09_ZERO_LOW_RESULT_REPORT.md`）

---

## 12. 垂类表现

- **最强**：`sticker`（4/4 PASS，100%）、`mascot`（2/2 PASS）、`poster_specific`（16 题里 PASS 率 31.2%，+8 改善
  仅 1 回归，全场最佳）、`package`（相对 previous candidate +6 改善 0 回归，Cluster A 修复受益最明显的垂类）。
- **最弱**：`banner`（0% PASS，+4 回归，全场回归最多）、`stationery`（0% PASS，4 回归 0 改善，含笔袋旗舰未修复
  案例）、`certificate`（0% PASS，3 零结果）、`classroom_material`/`worksheet`/`flyer`（0-10% PASS，持续偏弱）。
- **教育/课堂类**（classroom_material, worksheet, chart, textbook 等）：整体偏弱，主要是 catalog 内容缺口和证据
  不足，不是单一打分机制问题。
- **商业设计/海报类**：poster_specific 与 banner 两极分化，正好印证 Cluster A 文档自己披露的"同一机制帮了一部分
  多词促销查询，也伤了另一部分"。
- **贴纸/标签类**：sticker 满分；label 垂类中等（12.5% PASS，含未修复的 酒标）。
- **周边/玩具/公仔/收藏品类**：doll、globe、keychain、textbook 等小样本垂类全 FAIL 且三版本均无变化，更像
  catalog 内容缺口而非搜索逻辑问题。

（详见 `10_VERTICAL_SUMMARY.csv` / `10_VERTICAL_REPORT.md`）

---

## 13. 剩余失败根因

对全部 195 个 FAIL + 8 个相对 production 回归的 PARTIAL（共 203 行）做了基于行级字段的自动化根因分类
（`12_REMAINING_FAILURE_ROOT_CAUSES.csv`，方法披露见 `12_ROOT_CAUSE_SUMMARY.md`）：

| 根因分类 | 数量 | 占比 | 可否靠搜索逻辑修复 |
|---|---:|---:|---|
| 证据不足（insufficient_evidence） | 65 | 32.0% | 未知，需人工复核 Top5 |
| 主体判定/覆盖率缺口（同 Cluster A 机制） | 47 | 23.2% | **可以** |
| 重写/分解路径问题 | 28 | 13.8% | **可以** |
| 检索/打分相关性问题 | 24 | 11.8% | **可以** |
| **Catalog 内容缺口** | 16 | 7.9% | **不可以，需模板补充** |
| 候选项丢失（低结果但 FAIL） | 11 | 5.4% | 大概率可以 |
| PARTIAL 相对 production 回归 | 8 | 3.9% | 视具体情况 |
| **新增零结果回归** | 4 | 2.0% | **可以，且优先级高** |

**可通过搜索逻辑修复的比例约 56.2%（114/203），真正的 catalog 内容缺口约 7.9%（16/203）**，其余约 32% 因证据
不足暂无法下结论。这个切分可以直接支撑"哪些该继续调打分逻辑、哪些该走模板补充"的决策。

---

## 14. 风险和可比性限制

1. **Catalog 数据在对比区间内发生了变化**（`b4116648`，同记录数不同内容），这是评测期间无法避免的既成事实，已在
   配置锁与本报告多处披露，但意味着 latest vs previous-candidate 的对比不是 100% 严格受控实验，存在极小的
   数据侧干扰因素（影响范围仅 4 个模板的别名字段）。
2. **Production baseline 和 previous candidate 的结果文件是复用 2026-07-21 的历史文件，未在今天重新采集** ——
   按章程要求这是正确做法（避免用变化中的当前 main 做基线），但也意味着如果 production main 在这几天内有其他
   改动，本报告的 production 对比行不会反映那些改动。
3. **评测方法本身的既有限制**（继承自 7/19/7/21）：Top K 固定为 5，无法支持 Top 10；判分仅基于文本证据
  （title/tags/topics），未做截图级别的视觉判断；LLM judge（`gpt-4o-mini`）存在噪声，历史经验显示约 1-2 题/侧
  的标签抖动属于噪声范围而非真实变化。
4. **根因分类是自动化启发式推断，不是逐题人工核实**——`insufficient_evidence` 占比高达 32%，是本报告最大的
   已知盲区，如果要对具体案例做工程决策，建议先对这部分做抽样人工复核。

---

## 15. 结论

- **Cluster A fix 是否有效？** 部分有效。4 个核心代表案例中，1 个完全修复（wine label 英文），1 个部分恢复
  （人体图解），2 个完全未变化（字母海报、巧克力礼盒）。同类形态的英文"X package"查询修复效果更好（coffee
  package 完全修复）。垂类层面（package、poster_specific）确有实质性改善。**但文档中"四个案例均已确认修复"的
  表述与全量真实流水线结果不完全一致，需要如实说明。**
- **Cluster B fix 是否有效？** 基本无效。6 个核心代表案例中只有 1 个（挂件）真正修复；**旗舰案例`笔袋`本身仍未
  修复，且比 production baseline 更差**。这是本次评测最重要的负面发现——这次修复是专门为`笔袋`命名和设计的，
  而它在真实流水线里仍然失败。
- **326 整体是否比上一版好？** 是，聚合指标净正向：PASS 37→38、FAIL 203→195、UNJUDGABLE 10→7、平均分
  16.97→18.95、改善题数大于回归题数（30 > 23）。相对 production baseline 的净改善更明显（PASS +14，FAIL -12）。
- **是否引入明显新回归？** 是，有 4 个新增零结果回归（`diploma`、`会员卡`、`puzzle`、`优惠券`），其中 `diploma`
  的结果数呈现"101→6→0"的持续单调下滑趋势，值得在下一轮修复前优先排查。
- **是否建议继续修复？** 建议继续。优先级：① `笔袋`/`pencil case`旗舰案例（含疑似具体模板打错标签的独立线索）；
  ② Cluster A 剩余的 coverage-gate / isolated-hit-cap 机制（占剩余失败根因的 23.2%，是最大的已诊断可修复类别）；
  ③ 4 个新增零结果回归。
- **是否可以进入 manager review？** **评测数据和本报告本身已经完整、可信，可以直接呈交参考决策**——但
  工程建议是：**在旗舰案例 `笔袋` 修复并重新跑一遍全量评测之前，不建议将这版代码晋升替换生产环境**。
- **哪些内容 gap 可以进入 template discovery？** `12_ROOT_CAUSE_SUMMARY.md` 中的 16 个 `catalog_content_gap`
  案例（约占剩余失败的 7.9%），以及垂类报告中标记为"三版本均无变化的全 FAIL 小样本垂类"（doll、globe、keychain、
  textbook、coupon 等）——这些在三个不同版本的打分逻辑下都拿不到 PASS，更像是目录内容本身的缺口，而非排序/过滤
  逻辑问题。
