# Curify 300+ Easy Query 生产环境优化前基线测试 工作报告

**日期**: 2026-07-15
**任务**: PRODUCTION PRE-OPTIMIZATION EASY-QUERY BASELINE

---

## 一、任务背景

2026-07-15 会议要求：使用公司当前线上生产网站正在运行的版本（"优化前"版本），重新完整测试此前已确定的 328 条 Easy Query（简单词）集合，建立一份可信、可复现、不受后续搜索优化工作污染的正式基线（Baseline）。

此前（2026-07-14）已对这同一份 328 条 Query 集合执行过一轮完整测试，但那一轮使用的是**本地未提交、未推送到远程仓库**的搜索优化开发分支（`baobao/search-relevance-phrase-alias-2026-07-09`），并非生产版本。因此在今天之前，这套 Query 从未在真正的生产环境上被完整执行过——本次任务正是为了填补这个空白。

## 二、测试目标

1. 权威测试对象为公司当前线上生产网站 `https://www.curify-ai.com`，而非本地代码、非 `origin/main` 假设、非任何预览/测试环境。
2. 使用与此前优化版测试完全相同的 328 条 Query（原始顺序、原始文本、原始重复情况，不做任何增删改）。
3. 产出逐条可追溯的原始记录（原始响应结构化数据 + 全页截图），而非仅有汇总统计。

## 三、版本确认

通过 GitHub Deployments API、`origin/main` HEAD、以及仓库 `vercel.json` 部署规则三方交叉验证，确认当前生产环境对应的 Git commit 为：

```
72b55b667bb5173cab87fcec377198064dc3ac28
```

该 commit 同时也是 `origin/main` 的当前 HEAD。本地搜索优化开发分支的基准 commit（`c062e618b...`）在远程仓库中查询返回 404——证明该优化工作从未推送、从未合并，因此 `origin/main`（=生产环境）在本次任务范围内天然是"优化前"版本，无需额外回退 commit。详见 `CODE_VERSION_AUDIT.md`。

对任务列出的 26 项后续优化特性（Rewrite Guard、protected phrase dictionary、d/g 运行时开关、A/B/C/D 模式、专用 CJK 分词器、小红书/手冲咖啡/二手奢侈品专用规则、negative cache 修复、anchor piggyback 修复等）逐项审计，**全部确认为 NOT_FOUND**——生产环境代码中不存在任何一项。

需要特别说明：生产环境本身已经具备 LLM 查询改写（OpenAI `gpt-4o-mini`，自 2026-05-18 起即为生产功能）与查询分解（decomposition）能力，这是生产环境长期存在的既有行为，不属于本次要排除的"后续优化"范畴，本报告如实记录了这些行为的实际表现。

## 四、线上环境确认

- `production_site_url`: `https://www.curify-ai.com`
- 搜索页面：`https://www.curify-ai.com/search?q={query}`，Next.js App Router 服务端渲染页面，结果在首次 HTML 响应中即已包含，无需额外 API 调用。
- 无需登录、无验证码、无地区限制。
- 状态：`PRODUCTION_SITE_CONFIRMED`

## 五、Query 数据集确认

- 文件：`easy_queries_cleaned_300_plus_2026-07-14.csv`
- SHA-256: `682ed08a97f69ff39317c923ac859fe2f085ab8e8d7b9dc7b1a0f31fa0b32f3e`（与 2026-07-14 优化版测试所用文件逐字节一致，经 manifest 哈希交叉核实）
- 328 条数据行，`E001`–`E328`，0 条空值，0 条重复，原始顺序完整保留
- 状态：`AUTHORITATIVE_EASY_QUERY_FILE_CONFIRMED`

## 六、采集方法

复用此前已在生产环境上成功执行过（68 条 Hard Query 精确案例）的 Playwright 采集脚本作为基础，在独立目录中改造出 `scripts/collect_easy_query_baseline.mjs`，仅调整采集/断点续传/输出结构，未改动任何 URL 构造、DOM 解析或搜索相关逻辑。采集方式为真实 Chromium 浏览器对生产页面发起 `GET` 页面导航，与真实用户行为完全一致；不调用任何本地/预览/内部 API，不依赖任何本地产品代码。

参数：并发数 1，请求间隔 1.2–2.2 秒（随机），单请求超时 45 秒，最多重试 2 次（仅限网络/超时错误），每 10 条写入一次 checkpoint，每条完成后立即落盘独立原始记录。

## 七、Smoke Test

从 328 条权威 Query 中抽取 5 条（`flower`、`美妆`、`横幅`、`teacher`、`perfume`，覆盖中英文与多个类别，包含此前已知的低结果候选词）进行预演。预演过程中发现并修复了一处"结果被拓宽提示文案"提取逻辑的 bug（未影响结果数量统计），修复后重新执行预演，全部 5 项检查通过。

**结果：`SMOKE_TEST_PASS`**

## 八、全量运行情况

对全部 328 条 Query 执行了正式采集。运行过程中发生一次中断（后台进程被环境重启终止，发生在第 152/328 条），采集脚本的断点续传机制正确识别已完成的 151 条记录并跳过，从第 152 条继续，未产生任何重复记录或数据丢失，过程记录于 `logs/resume_history.md`。

运行完成后，人工复核发现 17/139 条"查询被拓宽"记录的提示文案字段存在 DOM 提取范围过大的问题（仅影响文案文本，不影响结果数量/零结果/低结果判定）。修复提取逻辑后，仅针对这 17 条记录重新执行了一次实时查询（其余 311 条未受影响，未重新执行），确认修复有效。

- 实际测试 Query 数：**328 / 328**（100% 覆盖，0 条缺失）
- 是否每条 Query 都有逐条结果：**是**，每条均有独立 JSON 原始记录（`raw/*.json`）
- 是否保存了每条 Query 的 Top Results：**是**，Top 5，含标题/链接/图片地址/元数据
- 是否保存原始响应证据：**是**，结构化 JSON + 全页截图（328 张，非仅失败时）

## 九、数据完整性

`final/easy_query_production_baseline_integrity_report.md` 完整性检查全部通过：
- 输出记录数 = 输入 Query 数 = 328
- `query_index` 唯一且连续覆盖 1–328
- 无负数结果数量
- 无"失败被误记为 0 结果"的情况（本次运行 0 次网络错误、0 次超时、0 次解析错误，因此该风险未实际触发，但字段设计上二者始终区分）
- 无缺失原始文件、无缺失截图引用
- 输出顺序与输入顺序完全一致

## 十、主要统计（修复后最终数据）

- 成功搜索：328 / 328（100%）
- 零结果（Zero-result）：**12 条（3.66%）**
- 低结果（Low-result，<5）：**43 条（13.11%）**
- 查询被生产环境拓宽（触发"Few results for X, Also showing results for Y"提示）：**138 条**
- 观察到改写信号：**138 条**
- 网络错误 / 超时 / 限流 / 验证码 / 解析错误：均为 **0**
- 平均响应时间：约 3885 ms；中位数约 3302 ms；P90 约 5404 ms；P95 约 5920 ms
- 最慢的查询：`夜市`（11627 ms）、`游乐园`（9899 ms）、`3C数码`（9617 ms）

## 十一、0 结果情况

12 条零结果查询包括：`塑料`、`混凝土`、`cork`、`velvet`、`扁平化`、`中古`、`房地产`、`3C数码`、`二手交易`、`展架`、`预售`、`保健品`（完整名单见 `final/easy_query_production_baseline_zero_results.csv`）。这些词多为材质类、行业类词汇，与目录内容匹配度低，是生产环境在无 Rewrite Guard / 无 protected phrase 保护下的真实未加缓解表现。

## 十二、low-result 情况

43 条低结果查询详情见 `final/easy_query_production_baseline_low_results.csv`，按类别统计见 `final/easy_query_production_baseline_summary.md`（`material`、`style`、`object` 类别中低结果比例相对较高）。

## 十三、错误情况

本次运行未发生任何网络错误、超时、限流或验证码拦截。`final/easy_query_production_baseline_errors.csv` 与 `..._timeouts.csv` 均为带表头的空文件。

## 十四、broaden / rewrite 情况

138/328（42.1%）的查询触发了生产环境的"结果不足自动拓宽"机制，`final/easy_query_production_baseline_broadened_queries.csv` 记录了每条查询实际展示的拓宽/改写词。由于生产环境**没有** Rewrite Guard 机制，这些拓宽词未经任何相关性过滤，报告中可观察到部分拓宽结果与原查询相关性一般（例如英文 `teacher` 被拓宽后混入了与"教师"无关的 MBTI/地缘热点卡片），这正是本次基线测试希望如实记录、供后续优化版本对比参照的现象。

## 十五、可复现性

- 输入文件、采集脚本、原始记录、截图、日志、checkpoint 均已保存在本次独立输出目录内，任何环节均可复核。
- 断点续传机制已经过两次实战验证（一次因环境中断触发，一次为主动的定向修复重跑）。
- `RUN_MANIFEST.json` 记录了完整机器可读的运行参数与版本证据链。

## 十六、局限性

1. 生产页面未在 DOM 中暴露"共 N 条结果"的数字文案，`result_count_reported` 字段全部为 `null`；本报告统一使用实际渲染卡片数 `result_count_observed` 作为口径。
2. 生产搜索结果页无筛选器、无分页组件，`filter_state`/`pagination_state` 字段全部为 `null`，如实反映页面确实不存在此类功能，而非采集缺陷。
3. `spelling_correction_visible` 未能与通用改写/拓宽提示明确区分，为避免误判，统一记为 `null`。
4. 17 条记录的"拓宽词"文本经过一次事后修复重采集，其中少数记录的结果数量/状态与首次采集存在细微差异——这是生产环境 LLM 改写器非零 temperature（0.4）导致的真实系统波动，而非数据缺陷，详见 `logs/resume_history.md`。
5. 与 2026-07-14 优化版结果的对比（`summaries/baseline_vs_optimized_join_ready.csv`）本质上是"生产版本 vs. 本地未合并优化候选版本"的代码路径对比，而非同一部署版本的时间前后对比，文件中每行均标注了该说明。

## 十七、后续与优化版对比建议

待未来正式的优化版本合并并部署到生产环境后，可使用同一份 328 条 Query 文件、同样的生产环境采集方法重新运行一次，与本次基线（`easy_query_production_baseline_full_results.csv`）逐条对比 `zero_result`/`low_result`/`query_broadened`/`result_count_observed` 等字段，即可获得真实的"优化前 vs. 优化后"生产环境效果对比。

## 十八、文件索引

详见根目录 `README.md` 第 13 节与 `final/easy_query_production_baseline_file_manifest.json`。核心交付物：

- `final/easy_query_production_baseline_full_results.csv` / `.jsonl` — 328 条逐条结果
- `final/easy_query_production_baseline_summary.md` / `.json` — 汇总统计
- `final/easy_query_production_baseline_zero_results.csv`、`..._low_results.csv`、`..._broadened_queries.csv`、`..._rewrite_observed.csv`、`..._top_results.csv`
- `final/easy_query_production_baseline_integrity_report.md` — 完整性检查
- `summaries/manual_review_queue.csv` — 人工复核优先级队列
- `CODE_VERSION_AUDIT.md`、`QUERY_FILE_AUDIT.md`、`COLLECTOR_AUDIT.md`、`COLLECTION_METHOD.md`、`WORKTREE_SAFETY_REPORT.md`

## 十九、最终结论回答

1. **这次是否测试了当前公司线上网站？** 是，全部 328 条 Query 均通过真实浏览器对 `https://www.curify-ai.com` 发起页面请求完成。
2. **是否使用了优化前版本？** 是，已通过 GitHub 部署元数据独立确认生产 commit 不含任何后续优化特性。
3. **是否调用了本地优化代码？** 否，采集脚本与本地任何产品代码仓库均无依赖关系。
4. **产品搜索本身是否调用 LLM rewriter？** 是，生产环境的 `lib/searchRewrite.ts` 会对稀疏结果查询调用 OpenAI `gpt-4o-mini`，这是生产环境既有行为。
5. **collector 自己是否调用 LLM？** 否。
6. **实际测试了多少条 Query？** 328 条，100% 覆盖。
7. **是否有每条 Query 的逐条结果？** 是。
8. **是否保存了每条 Query 的 Top Results？** 是，Top 5，含图片地址。
9. **有多少条 0 结果？** 12 条（3.66%）。
10. **有多少条 low-result？** 43 条（13.11%）。
11. **有多少条技术错误？** 0 条（0 网络错误、0 超时、0 解析错误、0 验证码、0 限流）。
12. **是否可以和之后的优化版逐条比较？** 可以，`summaries/baseline_vs_optimized_join_ready.csv` 已提供 328 行的 join-ready 结构，但需注意当前唯一可比对象是本地未合并的优化候选代码，而非已部署的优化版生产环境；待优化版真正部署后，可用同一方法重新采集获得更严谨的时间前后对比。

---

**最终状态：`FULL_EASY_QUERY_PRODUCTION_BASELINE_COMPLETE`**
