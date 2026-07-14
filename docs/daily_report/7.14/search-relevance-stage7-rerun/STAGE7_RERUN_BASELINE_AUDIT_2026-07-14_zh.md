# Stage 7 Rerun Baseline Audit

审计时间：2026-07-14。本报告仅为只读审计，未修改任何 production 代码、未修改任何 7.13 产出文件、未重跑完整 68 条实验、未 Commit / Push。

## 1. Executive Summary

- 权威 68 Query 文件已定位：`docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv`（SHA-256 `00bd2cff...`），独立重新解析后确认为 68 行、68 个唯一 query、0 空值、0 重复 —— 与 `run_manifest.json` 和 `hard_queries_68_summary.md` 的声明一致。
- Baseline 文件（`hard_queries_68_baseline.csv`）与权威 68 Query 一一对应，无缺失、无多余、无重复，SHA-256 独立计算为 `904ea6a5...`，与 manifest 记录一致。
- 独立重新计算 Stage 7 指标：PASS=0，PARTIAL=4，FAIL=64，Broad improvement=4/68=5.88%≈5.9%，Weighted improvement=(0+0.5×4)/68=2/68=2.94%≈2.9%。**与 7.13 报告声称的数字完全一致**，且本次是从原始 CSV 独立重算，非照抄。
- 洪泛数据验证：`d_plus_g_result_count >= 1000` 的 Query 数为 **23**，与声称一致；`d_plus_g_result_count == 3209`（完整目录）的 Query 数为 **2**（Q39、Q40），与声称一致。另外发现一个未被主张突出的第三个满目录案例：Q42 在 `g_only` 阶段单独达到 3209，但 d+g 组合后降为 2291（未被"2 个完整目录"说法覆盖，因为该说法特指 d+g 组）——已在第 8 节列出。
- 目录规模确认：`public/data/nano_inspiration.json` 实际记录数为 **3209**（直接用 Python 解析 JSON 数组长度得出），与声称一致。（`nano_templates.json` 另有 308 条，未被纳入这个"3209"口径，manifest 明确说明该数字仅指 inspiration 表。）
- 人工标签覆盖：`curify_68_manual_relevance_audit_2026-07-09.csv` 的 `human_relevance_label` 列 **0/68 已填写**，`human_notes` 同样 0/68。确认 Stage 7 及此前所有阶段均未完成真正的人工验收，目前的 PASS/PARTIAL/FAIL 全部来自 LLM Judge（gpt-4o-mini）或更早的 Claude 首轮判定，从未有人类复核。
- curify-frontend 的 5 个 Stage 5/6 核心源文件（`zh_normalize.ts`、`query_phrase_aliases.ts`、`cjk_tokenizer.ts`、`searchRewrite.ts`、`topic_resolver.ts`）当前 SHA-256 逐一核对，与 manifest 记录的 Stage 7 运行时哈希 **完全一致**，且这 9 个搜索相关文件的 `git diff --stat`（996 insertions / 82 deletions）与 manifest 记录 **逐文件精确匹配**。但仓库整体 `git status` 并非"before/after 完全一致"——与 7.13 Stage 7 运行时记录相比，当前仓库多出 12 个与搜索无关的博客文件改动；根据 Prompt 0 运行前快照，这些改动在本阶段开始前已经存在，并非 Prompt 0 产生（`GenericBlogContent.tsx`、`blog/[slug]/page.tsx`、10 个 `messages/*/blog.json`），这些改动不影响搜索逻辑本身，但意味着"整个仓库 diff 字节级不变"这句话现在不再严格成立，需要在后续阶段精确区分"搜索相关文件不变"与"仓库整体不变"。
- 发现真实的 Baseline 覆盖风险：`aggregate.cjs` 只对 `hard_queries_68_baseline.csv` 做了 `existsSync` 保护，其余全部产出文件（`hard_queries_68_refreshed.csv`、`hard_queries_68_before_after.csv`、`hard_queries_68_ablation.csv`、`mode_{A,B,C,D}_results.json`、`judge_results.json`）在原路径下重跑会被无条件覆盖，且输出目录路径是硬编码的 `docs/daily_report/7.13/...`，没有日期参数化。这是本阶段最重要的、脚本级验证过的风险点。
- **结论：具备进入 Stage 7R-1 洪泛根因分析的条件，READY_WITH_LIMITATIONS。** 主要限制：(a) 人工验收始终缺失，所有既有 PASS/PARTIAL/FAIL 判断仍是 LLM Judge 的自证；(b) Mode A/C 的 d=OFF 分支是脱机 harness 重建而非真实 Next.js SSR；(c) 7.13 之后的目录内容漂移未被量化。

## 2. Repository State

### curify-frontend

| 项目 | 值 |
|---|---|
| Path | `/Users/baobaoli/Desktop/curify-frontend` |
| Branch | `baobao/search-relevance-phrase-alias-2026-07-09` |
| HEAD | `c062e618bce4044bedf718aadf59ff69f0999344` — "improve Chinese phrase protection in search" |
| Remote | `origin https://github.com/super-inbox/curify-frontend.git` (fetch/push) |
| Upstream | 未设置（`没有为该分支设置上游`）——因此无 ahead/behind 计数 |
| Dirty | 是 |
| Modified (21) | `app/[locale]/(public)/blog/[slug]/components/GenericBlogContent.tsx`, `app/[locale]/(public)/blog/[slug]/page.tsx`, `app/[locale]/(public)/search/page.tsx`, `lib/__tests__/search_metadata_scenarios.test.ts`, `lib/query_phrase_aliases.ts`, `lib/searchRewrite.ts`, `lib/zh_normalize.ts`, `messages/{de,en,es,fr,hi,ja,ko,ru,tr,zh}/blog.json`（10 个）, `next.config.ts`, `package-lock.json`, `package.json`, `scripts/eval_search.cjs` |
| Staged | 无 |
| Untracked (3) | `lib/__tests__/searchRewrite.test.ts`, `lib/__tests__/stage6_dictionary_hybrid.test.ts`, `lib/cjk_tokenizer.ts` |
| Deleted | 无 |

**注意**：以上 21 个 modified + 3 个 untracked 均为本阶段开始前已存在的改动（Stage 5/6/7 的搜索工作 + 一批与搜索无关的博客翻译/组件改动），本阶段未新增、未修改任何文件。与 7.13 run_manifest 记录的 9 modified + 3 untracked 相比，多出的 12 个文件全部是博客相关（`GenericBlogContent.tsx`、`blog/[slug]/page.tsx`、10 个 `messages/*/blog.json`），不属于 Stage 5/6/7 搜索代码范围，详见第 10 节。

### visual-search-adhoc

| 项目 | 值 |
|---|---|
| Path | `/Users/baobaoli/Desktop/visual-search-adhoc` |
| Branch | `main` |
| HEAD | `39d8d0a1c6a1c3bd9d31fedfc2d51954cff44f18` — "update 7.9 work report" |
| Remote | `origin https://github.com/super-inbox/visual-search-adhoc.git` (fetch/push) |
| Upstream | `origin/main` |
| Dirty | 是 |
| Ahead/behind | 0 ahead / 0 behind（与 origin/main 一致） |
| Modified | `.DS_Store`, `docs/.DS_Store`, `docs/daily_report/.DS_Store`, `docs/daily_report/7.2/assets/platform_spectrum/image_inventory.md`, `docs/daily_report/7.2/assets/platform_spectrum/visual_search_platform_spectrum.png`, `docs/daily_report/7.9/WORK_REPORT_2026-07-09_zh.md` |
| Staged | 无 |
| Untracked | `.cache/`, `docs/daily_report/7.11/`, `docs/daily_report/7.12/`, `docs/daily_report/7.13/`, `docs/daily_report/7.2/canva_manual_review/`, `docs/daily_report/7.5/blog_public_v2.md`, `scripts/curify-search-collect-stage7/`, `scripts/external-screenshot-p0-12/` |
| Deleted | 6 个 `.DS_Store` 文件（6.18、6.19-20、7.2 相关目录下） |

**注意**：以上全部为本阶段开始前已存在的状态（Stage 7 及此前多个阶段的既有产出，包括本次审计要读取的 7.13 目录本身，就是 untracked 状态）。本阶段新增的唯一改动是新建 `docs/daily_report/7.14/search-relevance-stage7-rerun/` 目录及其中的本报告文件（见第 3、10 节的"创建或修改文件"清单）。

## 3. Authoritative Inputs

| 文件 | 所属 repo | 大小 | 行数/记录数 | SHA-256 | 用途 | 权威性依据 |
|---|---|---:|---:|---|---|---|
| `docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv` | adhoc | — | 69 行（1 header+68 data） | `00bd2cff0f1dee8168c366020198ed592d0f9654786ff417aa00a19ba4c7ae68` | 68 Query 权威输入 | 唯一一个"68 行 query 执行清单"文件（`find`/`grep` 全库核实），且被 `curify_search_auto_collect_2026-07-07.csv` 实际执行过，manifest 与 summary.md 明确记录了选择理由 |
| `docs/daily_report/7.7/curify_search_auto_collect_2026-07-07.csv` | adhoc | — | 68 行（原始抓取） | `a4b0f322839241505d7b94c0348461947e3d3ba1fa9f6efe6b78857c60a18404` | Baseline 原始抓取（Playwright vs 生产环境） | 是唯一真实生产环境抓取记录，早于 Fix1/Fix2 及 Stage 2/5/6 |
| `docs/daily_report/7.9/manual_review/curify_68_manual_relevance_audit_2026-07-09.csv` | adhoc | — | 68 行 | `e8bb59bdd35d90955b4c5039ac806dfad46e8a90a8bb515e1b6bb344d2b862ce` | 提供 baseline 的 relevance verdict（Claude 首轮判定），human_relevance_label 列存在但全空 | 是唯一含 68 行 Claude 首轮判定的审核表 |
| `docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_baseline.csv` | adhoc | 120898B | 69 行（68 data） | `904ea6a5a17a28dbafe3948de6f5bcb958674e518280e5eaad079b150453d233` | Stage 7 归一化 Baseline 快照 | aggregate.cjs 生成，existsSync 保护，未被覆盖 |
| `docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_refreshed.csv` | adhoc | 370209B | 69 行 | `579d1bfbdc08a8385b8abe3e5e208b9329dd8bbc17ab1db12d8710c237b75f9b` | Mode D（当前生产路径）逐条重跑结果 | Stage 7 生成输出，唯一含 D 模式细节的文件 |
| `docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_before_after.csv` | adhoc | 365712B | 69 行 | `fc4cbb9d559dba284c6d7b48d94ad927b0811b64b5f3d54b2fe74841fe6a2278` | Before/After 对比 + 最终 verdict + 归因 | 唯一含 final_verdict/attribution 字段的文件 |
| `docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_ablation.csv` | adhoc | 971062B | 273 行（68×4+1 header） | `e9a3a21d09ff9a5d62eb26c507b64e0ddd1e4133ba26acd834a1d29ee46f2061` | A/B/C/D 2×2 消融全量数据 | 唯一含 272 行逐模式细节的文件 |
| `docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_summary.md` | adhoc | 29814B | 251 行 | `5ca6bbfa5c9621e85333a3c0540757cb60ab6359c733f487b187c133a79eae32` | 人类可读汇总报告 | 与本审计独立重算数字完全吻合 |
| `docs/daily_report/7.13/search-optimization-stage-7/run_manifest.json` | adhoc | 9168B | 54 行 | `0a0431e2ce92b86e21edf31def7148e0fb7edc65d915ebdf60abba321873b7f3` | 运行环境/哈希/A-B-C-D 定义/已知限制的机器可读记录 | 本审计逐项核对（query hash、baseline hash、5 个 bundled 源码 hash、git diff stat）全部通过 |
| `scripts/curify-search-collect-stage7/build_bundle.cjs` | adhoc | 2771B | 82 行 | `f0b3738836c5260be51ffc378eae0d22879eeae11fdeb7890eddf4c33dd9dec0` | esbuild 打包 Stage 5/6 真实源码 | 运行脚本 |
| `scripts/curify-search-collect-stage7/run_mode.cjs` | adhoc | 17878B | 461 行 | `2b3dd6e7960b02e66df999fbe33bcc53707c9ecd2d837b53cc537bd8883c8f5d` | 2×2 消融 harness | 运行脚本，采集脚本 |
| `scripts/curify-search-collect-stage7/run_judge.cjs` | adhoc | 3079B | 84 行 | `bda6e5486c71cd77e2c7b943b12fe1566a4a71ae6c07ec2d61a74d41e6f5a909` | LLM relevance judge 调用脚本 | 自动判定脚本 |
| `scripts/curify-search-collect-stage7/judge_prompt.js` | adhoc | 4263B | 63 行 | `1278e4e6ff1278bbebde8d5b5fbc606abb08012041e2866df50f02335082fb24` | Judge 提示词 | 判定逻辑来源 |
| `scripts/curify-search-collect-stage7/aggregate.cjs` | adhoc | 19524B | 375 行 | `062d922d349955ac2bd47ae5b6a11267f4b987d2e341e5a6c1fe41a34d01a65b` | CSV/报告组装脚本，含 baseline 覆盖保护逻辑 | 权威计算脚本，本审计据此核实覆盖风险（第 10 节） |
| `scripts/curify-search-collect-stage7/mode_{A,B,C,D}_results.json` | adhoc | 284350/239880/608882/626234B | 10601/8851/22797/23217 行 | 见第 6 节工具输出 | 各模式原始 harness 输出 | 生成输出，无覆盖保护 |
| `scripts/curify-search-collect-stage7/judge_results.json` | adhoc | 339511B | 5880 行 | `e36dabfe91abc88a45ac20f4f723880d34402059ec733f81fc84766b0c788137` | 272 行 judge 原始输出（按模式分组） | 生成输出，无覆盖保护 |
| `public/data/nano_inspiration.json` | curify-frontend | — | 3209 条记录（Python 解析确认） | 未计算（生产数据文件，非本阶段权威输入） | 目录规模的真实来源 | 直接读取生产 JSON 得出 |

未发现同名或相似的竞争文件（例如未发现另一份 `hard_queries_68_*` 系列文件、未发现另一份 68 行 query 清单）。均为唯一权威文件，无 unresolved 项。

## 4. Query Set Validation

- 总记录数：68（1 个 header + 68 个 data 行，Python `csv.DictReader` 解析）
- 唯一 query 数：68（`len(set(queries))==68`）
- 重复：0
- 空值：0
- 字段：`query, primary_scene, secondary_scene, query_style, expected_content_type, likely_recall_challenge, likely_filtering_challenge, content_gap_hypothesis, priority, confidence, keep_or_review, selected_reason, planned_test_type`
- 顺序：固定（summary.md 明确声明"fixed order preserved throughout"，且 baseline/ablation/before_after/refreshed 四个文件的 query 顺序经比对与 gold 文件顺序一致）
- 无独立 query_id 列（query_id 是下游文件如 baseline.csv 自行生成的 Q01–Q68 编号，非源文件自带）
- `priority` 分布：P0=64, P1=2, P2=2（无独立"P0 标记"布尔字段，priority 字段本身即分类）
- 无独立语言字段（中英文混合，通过 query 文本本身区分）
- 有"预期意图"类字段：`expected_content_type`、`content_gap_hypothesis`、`likely_recall_challenge`、`likely_filtering_challenge`
- 无人工标签列（人工标签在下游 `curify_68_manual_relevance_audit_2026-07-09.csv` 中，见第 9 节）
- 与 Baseline 对应关系：68/68 一一对应，`missing_from_baseline = {}`，`extra_in_baseline = {}`

## 5. Baseline Validation

- `hard_queries_68_baseline.csv`：68 条记录，68 个唯一 query
- 缺失 Query：无（`missing_from_baseline = set()`）
- 多余 Query：无（`extra_in_baseline = set()`）
- 重复：无
- 可用字段：`query_id, query, query_category, priority, baseline_source_file, baseline_source_type, baseline_commit, baseline_timestamp, baseline_environment, baseline_result_count, baseline_zero_result, baseline_low_result, baseline_top_results_json, baseline_relevance_score, baseline_relevance_verdict, baseline_relevance_notes, baseline_tokens_json, baseline_protected_phrases_json, baseline_rewrite_triggered, baseline_rewrite_raw_output, baseline_rewrite_parsed_output_json, baseline_final_search_queries_json, baseline_error, baseline_timeout, baseline_empty_page, baseline_data_quality`
- 包含 Top Results：是（`baseline_top_results_json`）
- 包含 result count：是
- 包含 relevance：是（`baseline_relevance_verdict` 分布 FAIL=43, PARTIAL=25，与人工审核指南中记录的 Claude 首轮 FAIL=43/WARN=25 一致，PARTIAL 即 WARN 的重命名）
- 包含 tokens：字段存在但值全部为 `not_available`（因为 baseline 来自纯浏览器渲染抓取，无法访问服务端 tokenizer 内部状态——这是采集范围限制，文件内 `baseline_data_quality` 字段已逐行注明，不是隐藏缺陷）
- 包含 protected phrase：同上，字段存在值为 `not_available`
- 错误/timeout：0 条（`baseline_error` 全空，`baseline_timeout` 全为 false）
- 代码版本：`baseline_commit` = "pre-Fix1/Fix2 production...before commits 4210e21f/c062e618"（描述性文本，非 commit hash 本身；这是一个数据缺口，见第 12 节）
- 数据版本：无独立字段，隐含于 `baseline_source_file`/`baseline_timestamp`
- 采集时间：`baseline_timestamp` = 2026-07-07（统一值）
- 运行环境：`baseline_environment` = "Playwright headless Chromium vs live https://www.curify-ai.com (production)"（统一值）
- 模型配置：无（baseline 未涉及 LLM 调用记录，因为是纯前端渲染快照）

**适合作为锁定 Baseline**：是，具备完整的 68/68 覆盖、可追溯来源、SHA-256 已记录、脚本级 existsSync 覆盖保护已验证生效。唯一缺口是 `baseline_commit` 字段是描述性文本而非可 grep 的精确 commit hash，若未来需要精确复现"before"状态需回退到该描述文本手工定位。

## 6. A/B/C/D Definition

从 `run_manifest.json` 与 `hard_queries_68_summary.md` §6 交叉验证，并用 `hard_queries_68_ablation.csv` 逐模式统计核实：

| Mode | d (dictionary/tokenizer) | g (LLM rewrite) | 实际构造方式 |
|---|---|---|---|
| A | OFF | OFF | harness 离线重建：`buildSearchTokens`/`scoreBlob` 逐字抄自 `git show HEAD:app/[locale]/(public)/search/page.tsx`（真实的、最后一次提交的 pre-Stage-6 代码）；不调用 rewrite |
| B | ON | OFF | 真实导入 Stage 6 的 `lib/query_phrase_aliases.ts`（`segmentCJKToken`/`applyPhraseAliasRulesExcluding`），配合 working-tree `page.tsx` 的 `scoreBlob`；不调用 rewrite |
| C | OFF | ON | pre-Stage-6 tokenizer（同 A）+ 真实调用 `lib/searchRewrite.ts` 的 `getMultiQueryPaths()`/`flattenPaths()`（真实 gpt-4o-mini API 调用） |
| D | ON | ON | working-tree `page.tsx` 端到端逻辑（Stage 6 tokenizer + 真实 Stage 5 rewrite）——即当前生产代码路径，是 `hard_queries_68_refreshed.csv` 的来源 |

- d 具体代表：Stage 6 的字典/分词/短语保护逻辑（`segmentCJKToken`, `applyPhraseAliasRulesExcluding`，来自 `lib/query_phrase_aliases.ts`/`lib/cjk_tokenizer.ts`）
- g 具体代表：Stage 5 的 LLM query rewrite/decomposition 逻辑（`getMultiQueryPaths`/`flattenPaths`，来自 `lib/searchRewrite.ts`，模型为 gpt-4o-mini）
- 数据版本：四组均在同一次会话内、同一 catalog 快照（`public/data/nano_inspiration.json`，运行时读取，3209 条）下执行，无跨组数据版本差异
- 是否调用真实 production 搜索代码：B/C/D 三组均通过 esbuild bundle 真实导入未修改的生产源码（非手抄、非 mock）；A 组的"OFF"分支是通过 `git show HEAD` 读取旧版 page.tsx 文本重建的，**不是**通过导入真实旧版模块——manifest 与 summary.md 均明确标注这是本次运行"最大的一处已知局限"，不是隐藏问题
- Mock：C/D 组的 rewrite 调用是真实 OpenAI API 调用，非 mock；A/B 组不涉及 rewrite 调用故无 mock 问题
- Fallback：未在脚本中发现针对 A/B/C/D 特定分支的静默 fallback（`run_mode.cjs`/`aggregate.cjs` 未发现按 query 字符串分支的硬编码逻辑，仅有用于 `manual_review_required` 标记的风险家族关键词列表，不影响 verdict 计算——已用 grep 核实）
- 未运行/超时/失败行：0（Ablation CSV 272 行全部有 `relevance_verdict`，`error` 列全空；`mode_D.log` 中出现的 18 处"error"字样经核实均为 `errorType=empty_output` 这一命名字段，非真实运行时异常）
- 四组是否使用相同 query 顺序：是（68 个 query_id Q01–Q68 在四个模式子集中顺序一致，已用 Python 校验）
- 结果覆盖风险：见第 10 节

## 7. Metric Recalculation

以下全部为本次独立重算结果（Python 解析 CSV 原始字段，非照抄旧报告），并附计算定义：

| 指标 | 计算定义 | 独立重算结果 | 与 7.13 声称是否一致 |
|---|---|---:|---|
| 总 Query 数 | `hard_queries_68_before_after.csv` 行数 | 68 | 一致 |
| PASS | `final_verdict == 'PASS'` 计数 | 0 | 一致 |
| PARTIAL | `final_verdict == 'PARTIAL'` 计数 | 4 | 一致 |
| FAIL | `final_verdict == 'FAIL'` 计数 | 64 | 一致 |
| 未判定数 | `final_verdict` 不在 {PASS,PARTIAL,FAIL} 的计数 | 0 | 一致 |
| Strict pass rate | PASS/68 | 0/68 = 0.0% | 一致 |
| Broad improvement rate | (PASS+PARTIAL)/68 | 4/68 = 5.88%≈5.9% | 一致 |
| Weighted improvement rate | (PASS+0.5×PARTIAL)/68 | (0+2)/68 = 2.94%≈2.9% | 一致 |
| zero-result 数量（baseline→D） | `baseline_zero_result`/`d_plus_g_zero_result` 为 true 的计数 | baseline=11, D=12 | 一致 |
| low-result 数量（baseline→D） | `baseline_low_result`/`d_plus_g_low_result` 为 true 的计数 | baseline=20, D=14 | 一致 |
| regression 数量 | `count_increased_but_relevance_decreased == true` 的计数 | 22 | 一致 |
| 1000+ result Case 数量 | `d_plus_g_result_count` 数值 ≥ 1000 的行数 | 23 | 一致 |
| full-catalog Case 数量 | `d_plus_g_result_count == 3209` 的行数 | 2（Q39, Q40） | 一致 |
| error 数量 | ablation.csv 272 行中 `error` 非空的计数 | 0 | 一致 |
| timeout 数量 | 未见独立 timeout 字段；manifest/summary 明确声明 0/272 harness 行超时 | 0（未见反证） | 一致 |
| missing result 数量 | 272 行中缺少 `top_results_json`/`relevance_verdict` 的行数 | 0 | 一致 |
| Mode A/B/C/D 各自 PASS/PARTIAL/FAIL/zero/low | 按 mode 分组统计 ablation.csv | A: 0/2/66, zero42,low46；B: 0/2/66, zero41,low50；C: 1/1/66, zero11,low15；D: 0/4/64, zero12,low14 | 与 summary.md §12 表格逐格一致 |

所有指标均可从现有文件完整复现，无需推测或补造数字。

## 8. Flooding Cases

以下为 `d_plus_g_result_count >= 1000` 的全部 23 条 Query（来源：`hard_queries_68_before_after.csv`，独立解析，非抽样）：

| Query ID | Query | Baseline count | d_only | g_only | d+g count | Growth (vs baseline) | final_verdict | attribution |
|---|---|---:|---:|---:|---:|---:|---|---|
| Q06 | genshin impact Furina fanart wallpaper 4k | 6 | 2 | 5 | 1569 | ×261.5 | PARTIAL | d_plus_g_joint_synergy |
| Q09 | 低饱和国风茶包装设计 | 10 | 2 | 84 | 1023 | ×102.3 | FAIL | neither_solved |
| Q10 | 光与夜之恋 卡面设计参考图 | 10 | 0 | 20 | 2687 | ×268.7 | FAIL | neither_solved |
| Q11 | 故障艺术风格海报 | 10 | 2 | 339 | 2814 | ×281.4 | FAIL | neither_solved |
| Q12 | 松弛感生活方式插画 | 10 | 7 | 156 | 3154 | ×315.4 | PARTIAL | d_plus_g_joint_synergy |
| Q15 | K-beauty glass skin brand launch visual | 10 | 6 | 84 | 1026 | ×102.6 | FAIL | neither_solved |
| Q16 | Y2K chrome skincare launch poster | 10 | 346 | 1192 | 1197 | ×119.7 | FAIL | neither_solved |
| Q19 | heritage brand rebrand moodboard | 10 | 8 | 25 | 1855 | ×185.5 | PARTIAL | neither_solved |
| Q25 | 博物馆文创联名产品设计 | 10 | 0 | 198 | 1712 | ×171.2 | FAIL | neither_solved |
| Q26 | 国货美妆联名限定包装 | 5 | 0 | 276 | 1766 | ×353.2 | FAIL | neither_solved |
| Q27 | 宠物摄影工作室品牌设计 | 10 | 0 | 131 | 1600 | ×160.0 | FAIL | neither_solved |
| Q28 | 宠物殡葬服务品牌视觉设计 | 10 | 51 | 161 | 1602 | ×160.2 | FAIL | neither_solved |
| Q33 | 美妆博主个人IP视觉设计 | 10 | 3 | 117 | 1670 | ×167.0 | FAIL | neither_solved |
| Q39 | 亚马逊评论截图水印素材 | 2 | 0 | 1 | **3209 (full)** | ×1604.5 | FAIL | neither_solved |
| Q40 | 小红书图文笔记模板 数字标题 | 10 | 0 | 8 | **3209 (full)** | ×320.9 | FAIL | neither_solved |
| Q41 | 小红书对比图 use前后 | 10 | 1 | 7 | 1195 | ×119.5 | FAIL | neither_solved |
| Q42 | 小红书封面模板 白底大字 | 10 | 0 | 3209 (g_only full) | 2291 | ×229.1 | FAIL | neither_solved |
| Q43 | 小红书探店打卡九宫格 | 10 | 0 | 29 | 1726 | ×172.6 | FAIL | neither_solved |
| Q45 | 小红书爆款封面 emoji风 | 10 | 0 | 26 | 1866 | ×186.6 | FAIL | neither_solved |
| Q46 | 小红书香薰产品种草图 | 4 | 6 | 943 | 2904 | ×726.0 | FAIL | neither_solved |
| Q47 | 抖音小黄车商品卡片设计 | 6 | 2 | 9 | 2129 | ×354.8 | FAIL | neither_solved |
| Q48 | 抖音带货主播人设海报 | 10 | 0 | 544 | 2184 | ×218.4 | FAIL | neither_solved |
| Q52 | Gen Alpha slang classroom poster | 10 | 0 | 995 | 1056 | ×105.6 | FAIL | neither_solved |

**验证结论**：
- "23 个 1000+ Case"：**准确**（独立重算得 23，与声称一致）。
- "2 个完整目录 Case"：**准确**，指 d+g 组恰好等于 3209 的行数为 2（Q39, Q40）。
- 目录规模确认为 **3209**：Python 直接解析 `public/data/nano_inspiration.json` 得到列表长度 3209，与声称一致。
- **补充发现（未被"2 个"这句话覆盖，但属于同一现象）**：Q42 在 `g_only` 单独模式下也达到 3209（完整目录），但在 d+g 组合后被稀释为 2291——说明"g_only 单独触发满目录洪泛"至少还有 1 个额外案例（Q42），只是被 d+g 组合部分抵消了，之前的表述"2 条接近或达到完整目录"若严格限定为 d+g 组是准确的，但如果读者理解为"全部消融数据里只有 2 处触碰过 3209"则不准确——应明确区分口径。

Rewrite/decomposition 层面的根因（来自 `hard_queries_68_refreshed.csv` 的 `rewrite_output_json` 字段，逐条读取确认）：Q39/Q40 的 decomposition `output` slot 被解析为停用词 "template"，剥离后产生零个 primary token，使 `allPrimary` 判断平凡为真，导致对全部 3209 条记录都判定为匹配——这是 manifest 与 summary.md §1/§14 描述的机制，本审计已在 CSV 原始字段层面核实该描述与数据一致（非凭空转述）。

Top Results 存在性：23 条洪泛 Case 的 `d_plus_g_top_results_json` 字段均非空（已核实非空数组）。
人工标签：0/23（因为整个 68 条 query 集的人工标签均为空，见第 9 节）。

## 9. Human Review Coverage

- 文件：`docs/daily_report/7.9/manual_review/curify_68_manual_relevance_audit_2026-07-09.csv`
- 已填写数量（`human_relevance_label` 非空）：**0/68**
- 空白数量：**68/68**
- PASS/PARTIAL/FAIL/其他值（human 列）：全部为空字符串，无法分类
- 非法值：无（因为全空，不存在非法枚举值问题）
- `human_notes` 同样 0/68 已填写
- `human_needs_followup` 同样 0/68 已填写
- 是否所有 68 条都有人工作出判断：**否，0/68**
- 自动 Judge 与人工标签是否分别保存：是，字段结构上分离（`claude_relevance_label` 列与 `human_relevance_label` 列并存于同一 CSV，但后者从未填写）；Stage 7 的 LLM Judge（gpt-4o-mini）结果保存在独立的 `judge_results.json`/`hard_queries_68_ablation.csv`/`hard_queries_68_refreshed.csv` 中，同样不含任何人工字段

**明确声明**：当前 Stage 7 的全部 PASS=0/PARTIAL=4/FAIL=64 判定，以及更早 baseline 的 FAIL=43/PARTIAL(WARN)=25 判定，均完全来自自动化 LLM Judge（分别为 gpt-4o-mini 温度 0 的 Stage 7 判定，以及更早的 Claude 首轮判定），**不能被视为已经完成了最终人工验收**。这是本轮结果最大的方法论缺口之一，Stage 7R-1 及后续阶段应将其列为已知限制，而非默认接受判定结果为"人工确认过的事实"。

## 10. Baseline Overwrite Risk

逐脚本代码级核实（`grep -n "existsSync\|writeFileSync"`）：

| 文件路径 | 风险位置 | 当前行为 | 风险等级 | 后续建议 |
|---|---|---|---|---|
| `scripts/curify-search-collect-stage7/aggregate.cjs:364-368` | baseline 写入前有 `fs.existsSync(baselinePath)` 检查 | **有保护**：若已存在则打印提示并跳过写入，不覆盖 | 低 | 保持现状 |
| `scripts/curify-search-collect-stage7/aggregate.cjs:356-358` | `hard_queries_68_refreshed.csv`/`hard_queries_68_before_after.csv`/`hard_queries_68_ablation.csv` 三个 `fs.writeFileSync` 调用前**无** `existsSync` 检查 | 无条件覆盖写入；`OUT_DIR` 硬编码为 `docs/daily_report/7.13/search-optimization-stage-7`（第 8 行），未按运行日期参数化 | **高** | 若重跑，必须先将 OUT_DIR 改为新日期目录（如 7.14），或在写入前加 existsSync 保护 |
| `scripts/curify-search-collect-stage7/run_mode.cjs:454` | `mode_{A,B,C,D}_results.json` 的 `fs.writeFileSync`，`OUT_DIR = __dirname`（第 29 行），无 existsSync 检查 | 无条件覆盖写入到脚本自身目录 | 高 | 同上，重跑前需先备份或改路径 |
| `scripts/curify-search-collect-stage7/run_judge.cjs:74` | `judge_results.json` 的 `fs.writeFileSync`，`OUT_DIR = __dirname`，无 existsSync 检查 | 无条件覆盖写入 | 高 | 同上 |
| `scripts/curify-search-collect-stage7/build_bundle.cjs:47,78` | 打包中间产物（`_bundle_stage56.cjs`、`_bundle_source_hashes.json`）无 existsSync 检查 | 无条件覆盖写入，但这些是可重新生成的中间产物而非评测结果，风险较低 | 低 | 保持现状 |
| `hard_queries_68_summary.md` | 未在任何 `.cjs` 脚本中找到其写入逻辑 | 判断为人工撰写而非脚本生成，因此没有脚本层面的覆盖风险，但也没有脚本层面的保护——纯粹依赖人工不手滑覆盖 | 中 | 重跑时人工确认不直接覆盖旧 summary.md |

**结论**：Baseline 本身（`hard_queries_68_baseline.csv`）有代码级不可覆盖保护，这是本次审计验证过、真实存在的保护机制，不是声称。但 Stage 7 的其余全部产出文件（含最关键的 ablation/before_after/refreshed 三个 CSV 和四个原始 JSON）在原始路径下重跑会被**无条件静默覆盖**，且没有任何脚本层面的告警。这是进入 Stage 7R-1 前必须解决的操作规程问题（而非代码问题——本阶段禁止修改脚本）。

## 11. Locked Baseline Strategy

后续只读保护方案（仅提出方案，未执行任何权限修改）：

1. 所有后续分析（Stage 7R-1 及以后）读取 Stage 7 数据时，一律使用本报告第 3 节列出的原始路径（`docs/daily_report/7.13/search-optimization-stage-7/*`、`scripts/curify-search-collect-stage7/*`）作为只读输入，不在这些路径下二次运行任何采集/聚合脚本。
2. 本报告第 3 节记录的全部 SHA-256 作为"锁定指纹"，任何后续引用这些文件的分析都应在使用前重新计算并比对哈希，一旦不一致立即停止分析并升级。
3. 后续任何新的采集/复现工作必须输出到新的、按日期区分的目录（如本次的 `docs/daily_report/7.14/search-relevance-stage7-rerun/`），不得写入 `7.13/search-optimization-stage-7/` 或 `scripts/curify-search-collect-stage7/`。
4. 后续任何新的 run manifest 必须显式记录本报告第 3 节的旧 Baseline SHA-256（尤其是 `hard_queries_68_baseline.csv` 的 `904ea6a5...` 和 `gold_query_test_set_2026-07-07.csv` 的 `00bd2cff...`），作为"我读取的是同一份 baseline"的证明。
5. 若未来任何原因导致权威 68 Query 集合发生变化（增删改任何一条 query，或改变顺序），必须在新 manifest 中显式声明"本次实验与 Stage 7 不可直接比较"，不得默认延续 Stage 7 的对比结论。
6. 不对旧文件执行 `chmod`，不修改脚本代码——第 10 节列出的覆盖风险应作为操作规程（人工检查清单）解决，而非本阶段的代码改动。

## 12. Data Gaps and Limitations

- **人工验收完全缺失**：0/68 human_relevance_label 已填写，所有既有判定均为 LLM Judge 自证（第 9 节）。
- **`baseline_commit` 不是精确 hash**：baseline.csv 的 `baseline_commit` 字段是描述性文本（"pre-Fix1/Fix2 production..."），不是可直接 `git show` 的 commit hash，若要精确复现该时间点代码状态需要额外考证。
- **Mode A/C 的 d=OFF 分支是文本重建，非真实旧版模块导入**：manifest 与 summary.md 已自行声明这一局限，本审计未发现与此矛盾的证据，但也无法独立验证"文本重建"与"真实运行旧代码"在边界情况下是否存在细微差异。
- **目录内容漂移未量化**：baseline 采集于 2026-07-07，Stage 7 harness 于 2026-07-13 读取当时的 `nano_inspiration.json`（3209 条），若两个时间点之间目录内容发生变化，baseline vs D 的结果数对比会部分反映内容漂移而非纯代码变化——manifest 已声明此限制，但没有历史目录快照可供反向核实，本审计同样无法弥补这一缺口。
- **LLM 非确定性**：rewrite 调用温度 0.4、judge 调用温度 0 但 API 不保证严格确定性，重跑不会得到字节级相同结果，这是模型层面固有限制，非本次审计可解决。
- **仓库整体 git diff 已非"before/after 完全一致"**：与 7.13 Stage 7 运行时记录相比，当前仓库多出 12 个博客相关文件改动；根据 Prompt 0 运行前快照，这些改动在本阶段开始前已经存在，并非 Prompt 0 产生（第 2 节），虽已核实这些改动与 9 个搜索相关文件无关（hash 与 diff stat 逐项比对一致），但"整个仓库字节级不变"这一表述在当前时间点已不再严格成立，后续报告若要复用这句话需要改为"搜索相关文件不变，仓库整体因无关工作而有新改动"。
- **P0_visual_review_with_claude_2026-07-09.csv 的 `needs_human_spot_check` 字段虽 12/12 已填写，但这是一个独立的 12 条 P0 子集竞品截图审查表，不等同于 68 条主集的人工验收**，二者不应混淆。

## 13. Readiness for Stage 7R-1

**READY_WITH_LIMITATIONS**

理由：
- 权威输入文件、Baseline、A/B/C/D 定义、Stage 7 全部关键指标均已从原始文件独立复现，未发现任何与 7.13 报告矛盾的数字。
- 洪泛数据（23 个 1000+、2 个满目录、3209 目录规模）已逐条核实为真实存在于数据文件中，可直接作为 Stage 7R-1 根因分析的输入,不需要重新采集。
- Baseline 文件本身有代码级不可覆盖保护，且本次确认未被本阶段任何操作触碰。
- 之所以不是纯粹的 READY，是因为：(a) 人工验收始终缺失，Stage 7R-1 的任何"改进/未改进"结论仍建立在纯 LLM Judge 判定之上；(b) Mode A/C 的"neither"基线是离线重建而非真实旧代码路径的直接执行；(c) 目录内容漂移未量化。这些限制不阻塞洪泛根因分析（根因分析主要依赖 D 模式的 tokens/rewrite/decomposition 字段，与人工标签缺失无直接冲突），但应在 Stage 7R-1 的报告中明确重申，不应被默默继承为"已确认事实"。

## 14. Next Analysis Priorities

1. 针对 23 个 1000+ Case，逐条比对 `rewrite_output_json` 的 `decomposition` slot 值，统计究竟有多少条是被单一通用词（poster/template/design/moodboard/visual/playful 等）触发的，量化"通用 slot 导致洪泛"这一假设的覆盖率而非只看 2 个满目录样本。
2. 确认 `allPrimary`/token 剥离逻辑的具体代码位置（`page.tsx` 或 `lib/query_phrase_aliases.ts`/`lib/cjk_tokenizer.ts` 中哪一段），定位这个"停用词导致零 primary token→平凡为真"判断的确切函数与行号。
3. 对比 22 条 `count_increased_but_relevance_decreased=true` 的 Case 与 23 条 1000+ Case 的重叠（已知 22/23 重叠，唯一例外是 Q06），确认这一数字关系背后的机制是否可推广。
4. 检查 Mode B（d-only）在同一批洪泛 query 上的表现（`d_only_result_count` 均为个位数至百位数，未洪泛），确认洪泛现象是否严格依赖 g（rewrite）触发，而不是 d 单独导致。
5. 针对 3 个 `d_plus_g_joint_synergy` Case（Q06/Q12/Q33 对应的三个 query），分析它们为何没有像其余 20 个洪泛 Case 一样被通用 slot 拖累，寻找"good rewrite" vs "bad rewrite" 的可区分特征。
6. 评估是否可以在 rewrite 阶段对 decomposition slot 做停用词过滤或最小 token 长度校验，作为根治洪泛的候选方案（本阶段只做定位，不做修复）。
7. 核实 Q42（g_only 单独达到 3209 但 d+g 未达到）与 Q39/Q40（d+g 直接达到 3209）之间 d 分词逻辑的介入差异，理解为什么 d 组件在 Q42 上"缓解"了洪泛而在 Q39/Q40 上没有。
8. 为 68 条 query 补齐真正的人工 relevance 标签（哪怕只先做 23 条洪泛 Case + 4 条 PARTIAL Case 的小规模人工抽检），避免根因分析结论完全建立在自动 Judge 之上。
9. 量化 7/7 baseline 采集与 7/13 harness 运行之间目录内容是否发生变化（例如对比两个时间点的记录数或某些已知模板 ID 是否新增），排除"洪泛是因为目录本身变大"这一替代假设。
10. 检查除 68 条 hard query 之外，Stage 6 §17 与 Stage 5 §12 提到的"2 个手工样例"具体是哪两条 query，确认它们是否也在本 68 条集合内，避免根因分析重复劳动或遗漏已有证据。
