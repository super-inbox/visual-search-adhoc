# Curify 搜索分词、召回与 Rewrite 优化阶段性工作报告

**报告日期：** 2026-07-13
**项目：** Curify Search Relevance Optimization
**当前阶段：** Stage 1–7
**报告性质：** 阶段性进展与风险报告
**当前总体状态：** 评估完成，性能目标未达成，暂不建议合并

---

## 1. Executive Summary

要求解决的问题是：Curify 搜索在中文复合短语、CJK 分词、低召回（low-result）识别、LLM Rewrite 质量等多个环节存在已知缺陷，需要系统性诊断、修复，并用固定的 68 条 hard query 做真实的 before/after 验证——而不是仅凭改动代码就宣称问题已解决。

截至本报告，我们已经完成：对现有代码、数据和历史结果的完整审计（Stage 1）；对 Fix 2 中文复合短语保护规则的专项审计与一处真实 bug 的修复（Stage 2）；CJK 分词方案的四组对照实验与技术选型（Stage 3）；low-result 触发逻辑审计，发现两处已确认的生产缺陷（Stage 4）；LLM Rewrite 链路的稳定性加固与 cache 分类修复（Stage 5）；Dictionary-first Scoped Hybrid（协议保护短语 + 真实 CJK 分词 + 别名 OR-group + 作用域收窄的 `hasStrict`）的完整实现（Stage 6）；以及基于真实代码（非 mock）的 68 条 hard query 完整 2×2 消融实验与相关性判定（Stage 7）。

Stage 7 的核心结论必须如实说明：**数据采集与归因实验已经完成，但当前 d+g（Stage 6 分词 + Stage 5 Rewrite）组合在 68 条 hard query 上的相关性验收没有通过**。重新核实后的真实数字是：Strict PASS 率 0.0%（0/68），Broad improvement 率 5.9%（4/68 PASS+PARTIAL），Weighted improvement 率 2.9%——全部远低此前设定的 60%–80% 改善目标。更重要的是，Stage 7 端到端实验发现了一个此前 Stage 5/6 只用 2 个样例标记过、但从未在全量 68 条数据上量化过的系统性问题：LLM Rewrite 产生的通用词（如"poster"、"template"）decomposition slot，与 Stage 6 更真实的分词结合后，会在 23/68（34%）条 query 上把结果灌成上千甚至全量 3209 条目录记录，这是当前最大的 production blocker。

此外必须说明一个此前未被充分强调的事实：Fix 1、Fix 2、Stage 2 remediation、Stage 5、Stage 6 的全部代码改动，目前都只存在于本地未推送分支 `baobao/search-relevance-phrase-alias-2026-07-09`，从未合并进本地 `main`，也没有对应远程分支或 PR。因此，即便 Stage 7 验收通过，也仍然需要经过 commit、push、PR、review、merge、部署验证等完整流程才能真正上线。

**当前不建议将该分支合并到 main 或部署到生产环境。**

---

## 2. 提出的核心任务与验收目标

以下要求均有历史工作报告和 Stage 7 任务说明支持：

- **中文复合短语保护与召回问题**：要求解决 `小红书`、`手冲咖啡`、`二手奢侈品`、`光与夜之恋` 等中文复合词被错误切分导致的召回/精确度问题（Stage 1 `SEARCH_CODE_AND_CALL_FLOW_INVENTORY_2026-07-11.md`、Stage 2 `fix2_audit.md`）。
- **CJK 分词方案的系统性评估**：不能只靠个别 phrase 规则打补丁，需要评估滑动窗口 bigram 与真实分词器的优劣（Stage 3 `cjk_segmentation_findings.md`）。
- **Low-result 检测与 LLM Rewrite 的可靠性**：审计触发逻辑是否只看数量、是否存在解析失败/重复调用/缓存缺失等风险（Stage 4 `low_recall_detection_audit.md`，Stage 5 `llm_rewriter_findings.md`）。
- **固定 68 条 hard query 的真实 before/after 验证，并且不能只看 result count**：Stage 7 任务明确要求"不要只用 count 判断改善，必须评估 Top Results 相关性和意图保留"，并设定 60%–80% 改善目标作为 Stage 7 阶段的验收参照（该目标出自 Stage 7 任务说明本身，未在 Stage 1–6 的历史文档中找到独立的会议记录来源，本报告如实注明这一点，不虚构额外出处）。
- **需要真实实验与可审计产出**：包括 2×2 消融（d/g 独立开关）、真实 A/B/C/D 结果文件、SHA-256 可追溯的 baseline、找出剩余失败案例（remaining failures），而不是仅凭代码 diff 或单元测试宣称修复。
- **12 条 P0 截图与 300+ easy-query 回归**：Stage 1 审计已确认这两项在当前分支状态下均不存在（详见第 9.2 节）。

---

## 3. 当前总体完成情况

| 工作方向 | 当前状态 | 主要产出 | 是否达到最终要求 |
|---|---|---|---|
| 数据与代码清点（Stage 1） | 已完成 | `CURRENT_STATUS_AND_GAP_MATRIX_2026-07-11.md` 等 4 份报告 | 是（审计类工作本身已完整） |
| Fix 2 中文复合短语审计与修复（Stage 2） | 已完成但未通过端到端验收 | `fix2_audit.md/csv`、`fix2_remediation.md/csv`，`zh_normalize.ts` +9 行 | 否（未做 68-query 或 300-query 回归） |
| CJK Tokenizer 方案评估（Stage 3） | 已完成 | `cjk_segmentation_findings.md`，5 方案 × 55 query 对照实验 | 是（评估本身完整，未涉及生产代码） |
| Low-result Detection 审计（Stage 4） | 已完成 | `low_recall_detection_audit.md`，发现 2 处确认缺陷 | 是（审计完整，缺陷留待后续修复） |
| LLM Rewrite 与 Cache 修复（Stage 5） | 已完成 | `llm_rewriter_findings.md`，49/49 测试通过 | 已完成但未通过验收（发现新精确度风险未修复） |
| Dictionary-first Scoped Hybrid 实现（Stage 6） | 已完成 | `d_g_implementation_report.md`，232/232 测试通过 | 已完成但未通过验收（68-query 未跑） |
| 68 hard-query 刷新与 A/B/C/D 消融（Stage 7） | 已完成但未通过验收 | 6 份核心文件，SHA-256 可追溯 | 否（0% strict PASS，远低于目标） |
| 12 条 P0 截图（修复前后对比） | 尚未开始 | 无 | 否 |
| 300+ easy-query 回归 | 尚未开始（数据集本身不存在） | 无 | 否 |
| Production PR / 部署 | 尚未开始 | 分支未推送、未合并 | 否 |

---

## 4. Stage 1–6 已完成工作

### 4.1 数据、代码和 Baseline 清点（Stage 1）

**问题**：在投入进一步开发前，先确认"现在到底有多少是真的完成的"——此前的 Fix 1/Fix 2 代码、测试和 68-query 结果是否真的代表一个已验证、已部署的状态。

**做了什么**：全仓库只读审计，未修改任何文件，未运行任何测试。确认了 68 条 hard query 的权威来源（`docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv`，68/68 程序化验证无重复无空值）；确认了搜索执行链路完整走查（`app/[locale]/(public)/search/page.tsx` 是唯一入口，无独立 API route）；确认了 `LOW_RESULT_THRESHOLD=5`（`page.tsx:48`）的准确定义位置；确认了 Fix 1（commit `4210e21f`，2026-07-10 02:03:29）与 Fix 2（commit `c062e618`，2026-07-10 02:50:48）**均只存在于本地未推送分支，从未合并进本地 `main`，也没有对应远程分支或 PR**（本报告已用 `git merge-base --is-ancestor` 重新验证，结论一致）。

**关键发现**：68 条 hard query 的执行结果采集于 2026-07-07，早于 Fix 1/Fix 2 的提交时间（2026-07-10）——也就是说在 Stage 1 审计时，已知没有任何一次正式回归是针对 Fix 1/Fix 2 之后代码跑的。12 张"修复后"截图完全不存在；300+ easy-query 正式回归集不存在（最接近的候选是 137 条 `search_eval_set.json`，属于不同代码路径，不能直接等价替代）。

**已知限制**：三份 tokenizer 测试镜像（`scripts/eval_search.cjs`、部分 `.test.ts`）是手工复制而非真实 import，且没有 CI 自动运行，"测试存在"不等于"曾被自动验证过"。

**验证结果**：Stage 1 全部约 62 项 checklist 子项均已确认完成或确认缺失，审计本身可正式关闭。

### 4.2 中文复合短语保护（Stage 2 / Fix 2）

**问题**：审计 Fix 2 新增的 3 条中文复合短语规则（`小红书`、`手冲咖啡`、`二手奢侈品`，均为 `atomicEntity`，防止被 bigram 拆分）是否设计合理、是否存在漏洞。

**做了什么**：运行既有测试 `-t "Fix 2"` → 11/11 通过。人工走查发现一处真实、可复现的 bug：繁体中文输入`手沖咖啡工作室視覺手冊`无法触发规则（`tsToSc` 繁简转换表缺少 `沖→冲` 等 5 个字符对），会重新触发 Fix 2 本应防止的 bigram 碰撞误命中问题。

**修复**：在 `lib/zh_normalize.ts` 新增 5 组繁简字符对（`沖/冲`、`覺/觉`、`冊/册`、`識/识`、`鑒/鉴`，+9 行），同步在 `scripts/eval_search.cjs` 镜像中修复（+66 行），并在 `search_metadata_scenarios.test.ts` 新增 10 个测试用例（+112 行）。

**验证结果**：`search_metadata_scenarios.test.ts` 65/65 通过，当时全量单测 135/135 通过（该数字为 Stage 2 阶段的历史快照，Stage 6 完成后全量单测已增至 232/232，详见 4.6 节）。修复未 commit，保留在同一未合并分支上。

**已知限制**：未对别名注入（`brand identity`/`visual identity`）加意图闸门（intent gate）——这被明确标记为"产品策略决策，本阶段不做"；未实现跨规则的 longest-match 优先级机制（该缺口在 Stage 6 中被系统性解决）；未跑 68-query 或 300-query 回归。

### 4.3 CJK 分词方案评估（Stage 3）

**问题**：评估是否应该用真实 CJK 分词器替换生产环境的滑动窗口 bigram 兜底机制，以及在换分词器之后，Fix 1/Fix 2 的 Protected Dictionary 机制是否还有必要。

**做了什么**：纯评估性质，未修改任何生产代码（已用 `git status --short` 确认）。构建独立评估 harness，对真实 3,209 条目录数据跑了 5 套方案 × 55 条 query 的对照实验：P0（当前生产）、A（纯滑动窗口）、B（纯 CJK 分词器）、C（滑动窗口 + 作用域收窄的 Protected Dictionary）、D（CJK 分词器 + 作用域收窄的 Protected Dictionary）。

**关键数字**：滑动窗口方案的误报最高达到 625 条结果（`极简主义风格海报设计`：625→6）、566 条（`首尔弘大风格海报设计`：566→2）。但同时发现一个真实、可复现两次的回归：`手冲咖啡工作室视觉手册`（Fix 2 自己的成功案例）在方案 D 下从 16 条正确结果掉到 0 条；另一条独立措辞的 query `手冲咖啡视觉识别系统手册` 从 16 掉到 1——确立了"别名分母"问题是一类可复现的风险，而非孤例。

**最终选型**：明确建议采用"Dictionary-first Scoped Hybrid"（方案 D 的分词器选型 + 分母问题的专项修复），而非直接替换。理由：纯 Protected Dictionary 无法解决更广泛的 bigram 碰撞误报问题；纯分词器或未修复的方案 D 会破坏已经工作的 `手冲咖啡` 别名逻辑；方案 C（词典 + 作用域滑窗，不用真实分词器）无法处理中英文混排 query（如 `小红书cover设计`、`蔚来ES6内饰海报`，滑窗会静默丢弃 `cover`/`es6` 等 ASCII token，真实分词器可以保留）。分词器选定 `@node-rs/jieba`（原生 Rust 绑定，支持自定义词典，相比 `Intl.Segmenter` 无自定义词典能力、`nodejieba` 构建风险更高而胜出）。同时明确回答"是否还需要 Protected Dictionary"：**需要**，因为任何分词器（包括 jieba 默认词典）都无法识别 `光与夜之恋`、`五菱宏光`、`蜜雪冰城`、`完美日记` 这类自造/小众实体名。

**已知限制**：分母修复、ASCII 保留、标点切分修复、真实接入 jieba 均被列为"留给后续阶段的设计/实现工作"，本阶段未做；未跑 68/300-query 回归；Vercel Edge Runtime 对 `Intl.Segmenter`/`jieba-wasm` 的兼容性"未经验证"。

### 4.4 Low-result Detection 审计（Stage 4）

**问题**：只读审计 low-result 判定与 LLM Rewrite 触发逻辑，不修复任何代码。

**关键发现**：`LOW_RESULT_THRESHOLD=5` 定义于 `page.tsx:48`（服务端，控制付费 LLM Rewrite 触发），`SearchResultsClient.tsx:196` 存在一个**独立声明的同值常量**（仅用于前端埋点区分 `search_lowresult`/`search_noresult`，两处需要人工保持同步，无强制约束）。判定逻辑**只看数量、不看质量**：`initialThinCount` 只统计原始 query 的严格命中数，从不参考相关性分数。由此确认两个已存在于生产的真实缺陷：(1) bigram 碰撞产生的误报会被计为"严格命中"，导致 `极简主义风格海报设计`（initialThinCount=689，全部不相关）这类 query 永远不会触发 Rewrite 安全网，68 条真实 query 中的 `故障艺术风格海报`（373，确认误报）同样受影响；(2) `手冲咖啡` 系列 query 因为别名分母问题 `initialThinCount` 永远为 0，即使已经有 16 条正确的宽松匹配结果，也会**每次都**触发付费 LLM 调用。

**已知限制**：未修复任何上述问题（均标记为 Stage 6 候选修复项）；Rewrite 合并是否可能让"本来还不错"的结果变差被标记为"风险，非已确认 bug"（当时未做真实 LLM 调用测试）；未确认多实例 Vercel 部署下 Rewrite cache 的真实命中率。

### 4.5 LLM Rewrite 与 Cache 修复（Stage 5）

**问题**：审计真实生产使用的 `getMultiQueryPaths()`（`lib/searchRewrite.ts:511`，`page.tsx:670` 唯一调用点）的稳定性，处理异常输出，并做小范围真实模型调用验证。

**修复的真实 bug**（均限定在 `lib/searchRewrite.ts` 文件内）：`JSON.parse("null")` 会成功返回 `null` 但后续读取 `.rewrites` 抛错，被错误归类为"OpenAI call failed"——加了显式的 shape guard；`getMultiQueryPaths` 此前未做 markdown 代码围栏剥离（`rewriteQuery`——一个已确认零调用点的旧函数——有这个逻辑但没同步过来）；同 query 去重此前只处理大小写/空白差异，未处理纯标点差异；新增 10 分钟负向缓存（覆盖解析失败/shape 错误/全部拒绝/全部同 query/空 decomposition 等情形），7 天正向缓存维持不变，并在同日完成"Cache Completion Patch"，把 TTL 分类规则从"JSON 是否解析成功"改为"是否存在至少一条可执行的二次检索路径"，修复了此前会把合法空输出错误归为 7 天正向缓存的问题。

**真实模型验证**：10 条真实 API 调用（非 mock），确认 `乔丹鞋 → 篮球鞋` 品牌到品类泛化的假设成立；同时也发现两处确认的语义错误：`比亚迪海豹` 被翻译成"BYD Seagull"（另一款真实存在但不同的车型）；`白箱`（动画《白箱/Shirobako》）被直译为字面意义的"white box packaging"，完全丢失了原意。这两类语义错误无法通过任何确定性校验规则捕获。

**新发现、未修复的高优先级风险**：某些 decomposition slot 是单个高频通用英文词（如 `visual`、`fashion`、`playful`），单独就能严格匹配几百到上千条目录记录；而 `page.tsx` 的最终展示过滤是"只要合并池中任意一条命中严格匹配，就只展示严格结果"这一**全局**开关，一个通用词的偶然严格命中就可能把原本正确的宽松匹配结果整体挤掉。该问题被明确记录、明确不在 Stage 5 范围内修复，标注"留给 Stage 6"。

**验证结果**：`searchRewrite.test.ts` 49/49 通过；`search_metadata_scenarios.test.ts`（Stage 2）65/65 无回归；`thin_recall_queries.test.ts` 28/28 无回归；全量单测 184/184（6 个文件）。Typecheck 0 错误；build 因沙箱网络限制（无法访问 Google Fonts）失败，与代码无关；lint 失败为已确认的 pre-existing ESLint 9 配置不兼容问题，非本阶段新增回归。

### 4.6 Dictionary-first Scoped Hybrid 实现（Stage 6）

**问题**：在 `page.tsx` 中真正落地 Stage 3 选定的方案——Protected Phrase 最长匹配优先提取 + 真实 CJK 分词器处理剩余文本 + ASCII/数字/型号保留 + 别名 OR-group 分母修复 + `hasStrict` 作用域收窄。

**做了什么**：`selectProtectedSpans()` 对 4 条 CJK atomicEntity 规则（`光与夜之恋`、`小红书`、`手冲咖啡`、`二手奢侈品`）做最长匹配优先、不重叠的 span 提取，命中的短语永不被重新分词；剩余"gap"文本用 `splitRuns()` 拆成 CJK/ASCII/其他标点三类，CJK 部分交给真实 `@node-rs/jieba`（`lib/cjk_tokenizer.ts`，内置 try/catch，分词失败时自动降级回旧的 bigram 兜底，不会导致请求失败），ASCII 部分原样保留为独立 token。**分母修复**：带 `aliasTokens` 的 atomic 短语（目前只有 `手冲咖啡`）不再把短语本身计为一个独立的强制 AND token，而是并入自己的 OR-group（`[手冲咖啡, brand identity, visual identity]`），`scoreBlob` 的宽松匹配阈值也从"一个合并分母"拆成"primary token 和 alias/concept group 分别独立判断⌈n/2⌉"，避免真实分词后 gap 词膨胀分母、稀释掉本来有效的别名信号。**`hasStrict` 修复**：从"整个合并池（原始 query + 全部 rewrite/decomposition 路径）中任意一条严格命中就生效"，收窄为"只看原始 query 自己这一趟的严格命中"，避免一个通用 decomposition slot 的偶然严格命中，把原始 query 自己真实相关的宽松结果整体挤掉。同时解决了一个 Next.js 15 的原生模块构建阻塞问题：`@node-rs/jieba` 的 `.node` 二进制被 webpack 静态解析失败，通过 `next.config.ts` 新增 `serverExternalPackages: ["@node-rs/jieba"]` 修复，构建恢复正常。

**代表性 before/after**（均来自 Stage 6 自建的评分镜像 harness，对真实 3,209 条目录数据）：`手冲咖啡工作室视觉手册` 0/16→0/17（分母回归修复）；`小红书风格海报` 0/0→9/9（整句抑制 bug 修复）；`小红书cover设计` 0/0→27/27（ASCII 丢失 bug 修复）；`极简主义风格海报设计` 625/625→0/6（bigram 碰撞误报大幅收窄）；`故障艺术风格海报` 339/339→0/2（真实 68-query 条目，误报收窄）。

**新发现、明确未修复的精确度风险**：`二手奢侈品鉴定品牌视觉` 0→57、`蔚来ES6 品牌视觉` 8→57，均是因为剩余的通用词（`品牌`/`视觉`）在真实分词后单独就能清过宽松匹配阈值——该风险在报告中被明确标记为 `manual_review_needed`/`RECALL_GAIN_PRECISION_RISK`，**未做任何阈值调整来掩盖**。`比亚迪海豹`、`白箱` 按范围要求未加任何 query-specific 特殊处理，两者依然是 0 条真实目录内容，Stage 5 发现的模型幻觉风险原样存在。

**验证结果**：新增 `stage6_dictionary_hybrid.test.ts` 48/48 通过；Stage 2/5 既有测试 65/65、49/49 均无回归；全量单测 232/232（7 个文件，184 项既有 + 48 项新增）。Typecheck 0 错误；本地 `npm run build` 通过；lint 失败与 Stage 5 报告的既有 ESLint 配置问题签名完全一致，确认非本阶段新回归。**Stage 6 本身明确声明未做 68-query 全量回归、未截图、未 commit、未 push。**

---

## 5. Stage 7：68 条 Hard Query 刷新与消融实验

### 5.1 Query Dataset

- **来源**：`docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv`
- **SHA-256**：`00bd2cff0f1dee8168c366020198ed592d0f9654786ff417aa00a19ba4c7ae68`（本报告重新计算确认）
- **行数**：68 行数据，68 个唯一 query，0 个空值（本报告重新用 Python 程序化验证）
- **选择理由**：是唯一被真实执行过（生成了对应结果文件）的 68 条 query 列表；仓库内其他"68"相关文件均为其衍生产物（打标签版本、审核模板等），无独立的第二个 68 条 query 执行集。
- **类别**：`primary_scene`/`secondary_scene`（文创、品牌、营销电商、教育等）、`priority`（多数 P0）、`confidence`、`content_gap_hypothesis`，均沿用至 Stage 7 各输出文件。

### 5.2 Baseline Provenance

- **原始文件**：`docs/daily_report/7.7/curify_search_auto_collect_2026-07-07.csv`，2026-07-07 通过 Playwright 对**线上生产环境** `https://www.curify-ai.com` 真实抓取，SHA-256 `a4b0f322839241505d7b94c0348461947e3d3ba1fa9f6efe6b78857c60a18404`（本报告重新计算确认）。
- **时间关系**：该采集**早于** Fix 1（2026-07-10 02:03:29）、Fix 2（2026-07-10 02:50:48）以及整个未提交的 Stage 2 remediation / Stage 5 / Stage 6 代码变更——是一次真正意义上"本轮全部修复之前"的快照。
- **Relevance 判定来源**：复用 `docs/daily_report/7.9/manual_review/curify_68_manual_relevance_audit_2026-07-09.csv` 中已有的 `claude_relevance_label`（PASS/WARN/FAIL），SHA-256 `e8bb59bdd35d90955b4c5039ac806dfad46e8a90a8bb515e1b6bb344d2b862ce`。**本报告重新核实：该文件的 `human_relevance_label` 列 68 行全部为空（0/68 已填写）**——也就是说，Stage 7 baseline 一侧使用的相关性判定，是已有的自动/Claude 首轮判定，**并非完整的人工视觉审核结果**，这一点在 Stage 7 的产出文件中已如实标注（`baseline_relevance_verdict` 字段来源为 `claude_relevance_label`），本报告在此重申，避免被误读为"68 条全部人工审核完成"。
- **A/B/C/D 四组的相关性判定**：由 Stage 7 新建的 LLM Judge（gpt-4o-mini，温度=0，固定 prompt 复用 7.9 人工审核指南的 PASS/WARN/FAIL/UNCLEAR 标准，同样不是人工视觉审核，而是与 baseline 判定方法一致的自动化判定）产生，共 272 次独立调用，逐条盲判（judge 不知道结果来自哪个 mode）。
- **Baseline 不可覆盖性**：`hard_queries_68_baseline.csv` 在 Stage 7 首次运行时才被创建，脚本逻辑中已内置"若文件已存在则拒绝覆盖"的检查——本报告未新建或修改该文件。

### 5.3 A/B/C/D 设计

| Mode | Dictionary (d) | Rewrite (g) | 说明 |
|---|---:|---:|---|
| A | OFF | OFF | 从 `git show HEAD` 读取的真实 Stage 6 之前代码逻辑重建，不调用 Rewrite |
| B | ON | OFF | 真实 Stage 6 分词/打分逻辑（从当前工作区代码直接 import），不调用 Rewrite |
| C | OFF | ON | Stage 6 之前的分词逻辑 + 真实 Stage 5 `getMultiQueryPaths()` 调用（真实 gpt-4o-mini API） |
| D | ON | ON | 当前工作区完整生产代码路径（Stage 6 分词 + 真实 Stage 5 Rewrite），是 `hard_queries_68_refreshed.csv` 的来源 |

四组均通过 esbuild 直接打包真实、未修改的 `lib/searchRewrite.ts`、`lib/query_phrase_aliases.ts`、`lib/cjk_tokenizer.ts`、`lib/zh_normalize.ts`、`lib/topic_resolver.ts`，只有 `page.tsx` 内未导出的编排逻辑（`buildSearchTokens`/`scoreBlob`/`scoreQueryTokens`/合并/`hasStrict`，约 150 行）在评估 harness 中被逐行转录复现（NEW 版本来自当前工作区源码，OLD 版本来自 `git show HEAD` 的真实历史代码，均为只读操作，未触碰 curify-frontend 的工作区文件）。

### 5.4 输出文件

```text
docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_baseline.csv       (68 行数据)
docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_refreshed.csv      (68 行数据)
docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_before_after.csv   (68 行数据)
docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_ablation.csv       (272 行数据 = 68×4)
docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_summary.md
docs/daily_report/7.13/search-optimization-stage-7/run_manifest.json
```

配套 collector/harness 代码与原始 JSON：`visual-search-adhoc/scripts/curify-search-collect-stage7/`（`build_bundle.cjs`、`run_mode.cjs`、`run_judge.cjs`、`aggregate.cjs`、`mode_{A,B,C,D}_results.json`、`judge_results.json`）。

---

## 6. Stage 7 量化结果

以下全部数字均为本报告重新读取 CSV 并用 Python 独立统计得出，与 Stage 7 产出文件一致。

### 6.1 PASS / PARTIAL / FAIL

| 判定 | 数量 | 占比 |
|---|---:|---:|
| PASS | 0 | 0.0% |
| PARTIAL | 4 | 5.9% |
| FAIL | 64 | 94.1% |
| **合计** | **68** | **100.0%** |

### 6.2 Improvement Rates

| 口径 | 计算方式 | 结果 | 是否达到 60%–80% 目标 |
|---|---|---:|---|
| Strict PASS rate | PASS / 68 | **0.0%** | 否 |
| Broad improvement rate | (PASS+PARTIAL) / 68 | **5.9%** | 否 |
| Weighted improvement rate | (PASS + 0.5×PARTIAL) / 68 | **2.9%** | 否 |

三种口径均远低于目标区间，无一达标。

### 6.3 Zero-result / Low-result

| | Baseline（修复前） | D（d+g，修复后） |
|---|---:|---:|
| Zero-result | 11 | 12 |
| Low-result（<5） | 20 | 14 |

Zero-result 净增 1（表面上是回归），但重新核实后确认：新增的 4 条"baseline 非零→D 为零"中，有 3 条的 baseline 非零结果本身就是 Fix-2-之前 bigram 碰撞产生的完全无关噪音（`儿童安全座椅品牌视觉`、`家用医疗器械品牌设计`、`charlotte mason copywork printable`），baseline 判定本身就已经是 FAIL，D 变成诚实的零结果并不改变最终判定；只有 1 条（`知识付费博主课程品牌`，baseline 为 WARN）是真实的相关性回归，已在 `hard_queries_68_before_after.csv` 中标注。Low-result 从 20 降到 14，但这不能直接等同于质量提升——见 6.6 节的重要说明。

### 6.4 Dictionary / Tokenization

- **Protected Dictionary 命中 query 数（Mode D）**：8/68 — `NCT Dream photocard template`、`K-beauty glass skin brand launch visual`、`Y2K chrome skincare launch poster`、`手冲咖啡工作室视觉手册`、`Amazon EBC enhanced brand content layout`、`Amazon brand story module design`、`小红书香薰产品种草图`、`maker space label set printable`。
- **Tokenization changed（Mode B 相对 Mode A 的 primary token 发生变化）**：34/68 — 真实 jieba 分词在过半数据上产生了实质性差异。

### 6.5 Rewrite

| 指标 | 数值 |
|---|---:|
| Rewrite eligible（初始结果 < 5） | 68/68（这批 hard query 本身就是按"低结果"标准挑选的） |
| Rewrite triggered | 68/68 |
| Rewrite 成功（返回至少一条可执行路径） | 50/68 |
| Rewrite empty_output（合法 JSON，但无可用候选） | 18/68 |
| **Rewrite 成功率** | **73.5%**（50/68） |
| **Rewrite 空输出率** | **26.5%**（18/68，分母为全部触发数 68） |
| parse_failure / invalid_shape / model_refusal / same_query_only | 0（本轮全部空输出案例均为合法 JSON 的 `empty_output`，没有一次解析失败或格式错误） |

### 6.6 Ablation Attribution

| 归因类别 | 数量 |
|---|---:|
| d-only solved | 0 |
| g-only solved | 0 |
| both independently solved | 0 |
| **d+g joint synergy** | **3** |
| **combination regression** | **1** |
| neither solved | 64 |
| ambiguous | 0 |
| **合计** | **68** |

d-only、g-only、both-independently 三项均为 0，说明在这批极难的 68 条 query 上，单独的分词修复或单独的 Rewrite 修复都不足以让任何一条从 FAIL 变为 PARTIAL 或以上；只有 3 条同时依赖两者配合才勉强达到 PARTIAL；1 条出现"组合反而更差"的回归。**这是需要重点关注的信号：d 和 g 各自的独立改善能力在这批 hard query 上几乎为零，唯一的真实增益来自两者叠加后的少数样本，同时叠加也带来了新的、更大规模的噪音问题（见第 7 节）。**

---

## 7. 关键发现：Generic Decomposition Catalog Flood

Stage 7 端到端实验发现的最重要、此前未被充分量化的问题：

**问题机制**：复杂原始 query（尤其是中文长尾/垂类 query）触发 Rewrite 后，`getMultiQueryPaths()` 返回的 decomposition 中，某个字段（如 `output`）的取值本身就是一个极其通用的单词（`poster`、`design`、`template`、`moodboard` 等）。这个通用词被当作一条独立的二次检索路径重新执行 `buildSearchTokens`/`scoreQueryTokens`。在 Stage 6 的真实分词逻辑下，这类词要么本身命中目录中海量记录的标签文案（如 `poster`），要么——最严重的情形——如果该词恰好落在 `STOPWORDS` 集合内（如 `template`，`page.tsx` 中因为"每条 inspiration 的 `template_id` 都含有该词"而被专门列为停用词），会导致该检索路径的 `primary` token 数组变为空、`requiredSlots` 变为 0，而打分公式 `allPrimary: primaryHits + groupHits === requiredSlots` 在双方都为 0 时**对目录中任意一条记录都恒为真**——相当于把整个 3,209 条目录当作"严格命中"合并进最终结果池。

**重新核实后的数字**：

- Mode D 中 **23/68（33.8%）** 条 query 的最终结果数超过 1000 条。
- 其中 **2 条**（`亚马逊评论截图水印素材`、`小红书图文笔记模板 数字标题`）结果数恰好等于 **3209**，即目录全部记录，均确认是 decomposition 的 `output` 槽位取值为字面单词 `"template"` 触发了上述"零必需 token 恒真"的边界情况。
- **22/68** 条 query 满足"结果数增加但相关性判定变差"（`count_increased_but_relevance_decreased`），几乎与上述洪泛问题完全重合。
- Mode D 最大单条结果数即为 3209（全量目录）。

**代表性 query（重新核实自 `hard_queries_68_before_after.csv` 与 `hard_queries_68_ablation.csv`，非虚构举例）**：

| Query | Baseline Count | d+g Count | Relevance 变化 | 主要问题 |
|---|---:|---:|---|---|
| 亚马逊评论截图水印素材 | 少量/噪音 | 3209 | FAIL（noise_level=high） | decomposition `output`="template"，命中 STOPWORDS，requiredSlots=0，恒真匹配全量目录 |
| 小红书图文笔记模板 数字标题 | 少量/噪音 | 3209 | FAIL | 同上机制 |
| 故障艺术风格海报 | 少量/噪音 | 2814 | FAIL（noise_level=high） | decomposition `output`="poster"，单一通用词命中目录中大量标签文案；Stage 6 自建 harness 曾单独测得该 query 分词层面 339→2 是精确度改善，但端到端跑通后被 Rewrite 层引入的 "poster" 通用词重新淹没 |
| 二手奢侈品鉴定品牌视觉 | 4（本身已判 FAIL） | 57 | FAIL（Stage 7 判定与 Stage 6 报告预判一致） | 分词后剩余通用词"品牌"/"视觉"单独清过宽松匹配阈值，Stage 6 报告已提前标注为 `manual_review_needed`，Stage 7 予以确认 |

**为什么这不是"可能有噪音"，而是当前最重要的 production blocker**：这类洪泛不是边缘情形，而是覆盖了 Mode D 三分之一以上的 query；它会让页面在没有任何真实相关内容的情况下返回"看起来很丰富"的上千条结果，对用户体验的破坏性远大于诚实地返回零结果或触发 Rewrite 失败；且该问题**同时存在于新旧两版分词逻辑**（`allPrimary` 的零分母恒真问题本身是 Stage 6 之前就存在的打分公式缺陷，只是过去很少真正走到"完全空 token"这种极端分支，Stage 6 真实分词把更多路径推到了这个边界）。

**为什么单元测试通过不足以证明真实搜索质量**：Stage 6 的 232/232 单元测试全部通过，覆盖的是分词/短语保护/`hasStrict` 逻辑的行为正确性，**没有一条测试模拟"Rewrite decomposition 槽位恰好是停用词或高频通用词"这一具体场景**——这正是端到端真实数据 A/B/C/D 实验（而非孤立单元测试）存在的价值。

---

## 8. 已改善、部分改善和回归案例

### 8.1 PARTIAL Cases

Mode D 全部 4 条 PARTIAL（判定标签均为 WARN）：

| Query | Before | After | 为什么有改善 | 为什么仍不能 PASS |
|---|---|---|---|---|
| genshin impact Furina fanart wallpaper 4k | FAIL | WARN | 结果整体转向 Genshin Impact 相关内容 | 未命中 Furina 这一具体角色，也非 wallpaper 格式 |
| 松弛感生活方式插画 | FAIL | WARN | 结果转向生活方式/健康相关内容 | 未体现"松弛感"这一具体美学特征 |
| clean girl aesthetic skincare packaging mockup | FAIL | WARN | 出现部分护肤相关内容 | 与不相关内容混杂，未命中包装 mockup 这一具体格式 |
| heritage brand rebrand moodboard | FAIL | WARN | 出现品牌/moodboard 相关内容 | 未命中"heritage brand"这一具体定位 |

### 8.2 Precision Fixes（表面回归、实为精确度修正）

3 条 "baseline 非零 → D 为零"，但经核实 baseline 的非零结果本身就是无关噪音，判定并未变化（均为 FAIL→FAIL）：

- `儿童安全座椅品牌视觉`：baseline 10 条结果（eyemask、宠物用品、饮食标签等，与"儿童安全座椅"完全无关），baseline 判定已是 FAIL；D 为 0 条，诚实反映目录中确无相关内容。
- `家用医疗器械品牌设计`：baseline 10 条结果（婴儿护理品牌、燕麦、意面酱等），同样与主题无关，baseline 已判 FAIL；D 为 0。
- `charlotte mason copywork printable`：baseline 结果为语言闪卡/舞蹈教程类无关内容，baseline 已判 FAIL；D 为 0。

### 8.3 Genuine Regression（真实回归）

- `知识付费博主课程品牌`：baseline 判定为 **WARN**（"Time Management Mastery"、"Book Interpretation Series" 等结果与查询意图存在合理关联），D 变为 **0 条结果**（FAIL）。这是本轮唯一一条确认的真实相关性回归，与 g（Rewrite 在该 query 上返回空输出）和分词变化共同相关，尚未做进一步根因拆分。

### 8.4 Count Increased but Relevance Decreased

**22/68** 条 query 满足该条件，详见第 7 节的机制说明与代表案例表。

---

## 9. 当前工作是否符合要求

### 9.1 已按要求完成

- 对现有搜索代码、数据、历史结果的完整审计（Stage 1），未凭主观印象汇报。
- 中文复合短语保护的专项审计，发现并修复一处真实繁简转换 bug（Stage 2）。
- CJK 分词方案的系统性技术选型，基于真实目录数据的四组对照实验，而非直接采纳某个方案（Stage 3）。
- Low-result 判定逻辑审计，发现两处已确认的生产缺陷（bigram 误报绕过 Rewrite 安全网、别名分母问题导致重复付费调用）（Stage 4）。
- LLM Rewrite 链路的稳定性加固：修复解析/缓存/去重相关的真实 bug，并做真实 API 调用验证品牌泛化能力，同时诚实记录两处模型幻觉案例（Stage 5）。
- Dictionary-first Scoped Hybrid 的完整实现与本地验证（232/232 测试、typecheck 0 错误、build 通过）（Stage 6）。
- 基于真实生产代码（非 mock）的 68 条 hard query 完整 2×2 消融实验，SHA-256 可追溯的 baseline，暴露出新的系统性风险，而非只挑选好看的样例汇报（Stage 7）。
- 严格遵守"不能只看 result count"的要求：Stage 7 全程使用独立 LLM Judge 对相关性做判定，并对"结果数增加但相关性下降"的 22 条案例做专项识别和人工复核。

### 9.2 尚未满足的最终验收项

- **60%–80% 改善目标**：实际 Strict PASS 0.0%、Broad improvement 5.9%、Weighted improvement 2.9%，全部未达标。
- **Search relevance acceptance**：0/68 严格通过，64/68 仍为 FAIL。
- **12 条 P0 最终截图（修复前后对比）**：Stage 1 审计已确认"修复后"截图完全不存在，本报告确认截至目前仍未生成。
- **300+ easy-query 回归**：Stage 1 审计已确认该数据集本身不存在，本报告确认截至目前仍未建立。
- **Vercel 端到端部署验证**：Stage 6 报告明确标注"本地 build 通过，未在真实 Vercel 环境验证原生模块冷启动行为"，本报告未新增验证。
- **Production PR / merge**：Fix 1、Fix 2、Stage 2 remediation、Stage 5、Stage 6 全部代码改动仍只存在于本地未推送分支，无对应 PR。

**结论：工作方向和评估方法符合要求，但最终搜索效果尚未满足要求。**

---

## 10. 当前是否可以提交、PR 或 Merge

| 动作 | 当前是否适合 | 原因 |
|---|---|---|
| 提交阶段性 Work Report | 是 | 已有完整审计、真实实现与真实实验结果，可如实汇报进展与差距 |
| Commit 实验报告（visual-search-adhoc） | 可在确认后进行 | 当前尚未 commit，报告文件为新增内容，不影响生产代码 |
| 提交 production PR（curify-frontend） | 暂不建议 | d+g 端到端相关性验收未通过（0% strict PASS），且存在未修复的系统性 catalog flood 风险 |
| Merge 到 main | 不可以 | 存在 34% query 触发的系统性洪泛缺陷，且尚无 12 P0 截图、300+ easy-query 回归佐证不会引入新的回归 |
| 进入最终 P0 Screenshot 阶段 | 暂缓 | "修复后"状态本身还需要先解决 catalog flood 问题，否则截图会记录一个已知有缺陷的状态 |
| 进入 300+ Easy Query 回归 | 暂缓，或仅用于诊断 generic-flood 问题在简单 query 上的暴露面 | hard-query 状态尚不稳定，优先级应先于扩大回归范围 |

---

## 11. 下一步建议

1. 新增 Stage 7.5：专项修复 Generic Decomposition Catalog Flood（第 7 节问题），这是当前唯一被确认的系统性 production blocker。
2. 禁止 decomposition/rewrite 产生的单一通用词独立作为一条检索路径执行（尤其是本身就在 `STOPWORDS` 集合内、或分词后 `primary`/`aliasGroups` 均为空的退化情形）。
3. 要求每条 rewrite/decomposition 检索路径保留原始 query 的核心区分性意图，而非退化为纯格式词（poster/template/design）。
4. 明确规定：单一通用 token 命中不应进入宽松匹配兜底池，或至少需要与其他更具区分度的 token 联合满足条件。
5. 增加结果集"选择性"或"洪泛防护"机制（例如单条检索路径的结果数上限、或对占目录总量异常高比例的命中做降级处理）。
6. 记录每条 rewrite/decomposition 路径各自贡献的结果数和相关性，便于后续快速定位类似问题，而不是只看合并后的总数。
7. 先在一个聚焦的回归集合（针对本次发现的 23 条洪泛 query 及其变体）上验证修复效果，不要直接重跑全部 68 条。
8. 聚焦集合通过后，再重新跑一次完整 68 条 hard query 验证是否达到改善目标。
9. 达到目标后再进入 12 条 P0 截图（修复前后对比）阶段。
10. 最后再执行 300+ easy-query 回归和 Vercel 部署验证，完成 commit / push / PR / merge 流程。

本报告不在此对上述修改做任何实际实施。

---

## 12. 风险与限制

- Stage 7 的相关性判定（无论是 baseline 复用的 `claude_relevance_label`，还是 A/B/C/D 新建的 gpt-4o-mini Judge）均为自动化判定，**不是完整的人工视觉审核**——`human_relevance_label` 列截至本报告仍为 0/68 填写。
- Baseline（2026-07-07）与本次 Stage 7 运行（2026-07-13）之间目录数据（`nano_inspiration.json`，3209 条）是否发生变化未独立核实，两者的结果数对比可能部分反映目录漂移，而非只反映代码变化。
- LLM Rewrite（温度 0.4）与 Judge（温度 0，但 API 不保证严格确定性）均存在非确定性，重新运行不保证逐条结果完全一致，但本报告的量级结论（0% strict PASS、34% 洪泛率）预期对此有较强鲁棒性。
- Stage 7 评估 harness 与生产端到端路径的一致性：harness 直接 import 真实 Stage 5/6 模块，但 `page.tsx` 内的编排逻辑是转录复现而非直接运行 Next.js SSR，不覆盖 topic 重定向、模板栏的 concept-expansion 二次通道、客户端模板匹配器等模块——这些模块不影响本报告统计的 inspiration Top-10 结果，但完整性上仍需在未来阶段用真实页面渲染做交叉验证。
- Rewrite 在本轮 68/68 全部触发——这本身符合预期（hard query 集合本就是按"低结果"标准挑选的），但也意味着本次实验没有覆盖"正常召回量级 query 下 Rewrite 网关行为"这一层面。
- `@node-rs/jieba` 原生模块在真实 Vercel Serverless 冷启动下的行为，Stage 6 已声明"未独立验证"，本报告未新增验证，仍为已知缺口。
- Stage 7 未重新运行 Stage 6 的完整测试套件（单测/typecheck/build/lint），因为 Stage 7 未对生产代码做任何改动——`git diff --stat` 在本报告开始前后重新核对结果一致（详见第 13 节），因此判断无需重新验证。
- Production 工作区（`curify-frontend`）当前仍存在 9 个已修改文件和 3 个新增未提交文件（Stage 2 remediation + Stage 5 + Stage 6 的全部改动），均未 commit。

---

## 13. 文件与 Git 状态

### Production repository（curify-frontend）

```text
Branch:  baobao/search-relevance-phrase-alias-2026-07-09
HEAD:    c062e618bce4044bedf718aadf59ff69f0999344 ("improve Chinese phrase protection in search")

git status --short（本报告重新执行确认）：
 M app/[locale]/(public)/search/page.tsx
 M lib/__tests__/search_metadata_scenarios.test.ts
 M lib/query_phrase_aliases.ts
 M lib/searchRewrite.ts
 M lib/zh_normalize.ts
 M next.config.ts
 M package-lock.json
 M package.json
 M scripts/eval_search.cjs
?? lib/__tests__/searchRewrite.test.ts
?? lib/__tests__/stage6_dictionary_hybrid.test.ts
?? lib/cjk_tokenizer.ts

git diff --stat：9 files changed, 996 insertions(+), 82 deletions(-)
```

说明：本报告开始前后重新执行 `git status --short` 与 `git diff --stat`，两次结果完全一致，可以确认本次 Work Report 撰写过程**未对生产代码做任何修改**；但严格来说这是"两次快照的文本/行数比对一致"，并非基于逐文件 hash/checksum 的比对，不应表述为"byte-identical"。

**Merge/Push 状态（本报告重新用 `git merge-base --is-ancestor` 与 `git branch -a` 独立核实）**：`4210e21f`（Fix 1）与 `c062e618`（Fix 2）均**不是**本地 `main` 分支的祖先提交，即未合并；`git branch -a` 中不存在 `remotes/origin/baobao/search-relevance-phrase-alias-2026-07-09`，即该分支**从未推送到远程**，也没有对应的 PR。这意味着 Stage 2 remediation、Stage 5、Stage 6 的全部工作目前仍完全停留在本地未提交状态。

### Report repository（visual-search-adhoc）

```text
Branch: main
HEAD:   39d8d0a1c6a1c3bd9d31fedfc2d51954cff44f18 ("update 7.9 work report")

本次新增（未提交）：
?? docs/daily_report/7.13/  （含 search-optimization-stage-7/ 与本 Work Report）
?? scripts/curify-search-collect-stage7/
```

本次 Work Report 生成过程中，除创建/写入 `docs/daily_report/7.13/WORK_REPORT_2026-07-13_zh.md` 本身外，未修改任何其他文件；未覆盖 Stage 7 的任何 CSV/JSON/Markdown 产出。**未执行 commit，未执行 push。**

---

## 14. Final Verdict

### 工作完成度

```text
Stage 1–6 implementation: completed
Stage 7 data collection and attribution: completed
Stage 7 performance acceptance: failed
Overall search optimization: not complete
Production merge readiness: blocked
```

截至 2026-07-13，Curify 搜索优化项目已经完成了要求的全部诊断、方案比较和真实端到端验证工作，方法论和工作方向本身是扎实、可审计的：从 Stage 1 的全面代码/数据盘点，到 Stage 2–6 逐层解决中文复合短语保护、CJK 分词方案选型、low-result 判定缺陷、LLM Rewrite 稳定性，最终在 Stage 7 用真实生产代码（而非 mock）对固定的 68 条 hard query 做了完整的 2×2 消融实验和相关性判定。但真实结果必须如实汇报：当前 d+g 组合方案在这批 hard query 上的相关性验收未通过（Strict PASS 仅 0.0%，Broad improvement 仅 5.9%，Weighted improvement 仅 2.9%，全部远低于 60%–80% 的目标区间），且 Stage 7 端到端实验暴露了一个此前未被充分量化的系统性问题——LLM Rewrite 产生的通用词与新分词逻辑组合后，会在超过三分之一的 hard query 上把结果灌成成百上千条乃至全量目录，这是当前最需要优先解决的 production blocker。同时需要明确的是，全部相关代码改动目前仍停留在本地未推送、未合并的分支上，距离真正可以 commit / PR / merge / 上线部署，还有一段确定的、有明确下一步路径的工作要做。本报告如实反映以上全部结论，不宣称问题已经解决，也不建议在当前状态下合并或部署。
