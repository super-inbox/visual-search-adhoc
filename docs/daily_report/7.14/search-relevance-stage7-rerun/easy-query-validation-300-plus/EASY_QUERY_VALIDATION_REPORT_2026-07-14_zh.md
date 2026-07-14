# 300+ Easy Query Validation Report（Prompt 8）

**运行日期**: 2026-07-14 | **候选版本**: `baobao/search-relevance-phrase-alias-2026-07-09` @ `c062e618bce4044bedf718aadf59ff69f0999344`（冻结）

**Regression Gate**: `SYSTEMATIC_REGRESSION` | **Execution Gate**: `EASY_QUERY_RUN_COMPLETE` | **下一步**: `BLOCK_RELEASE_CANDIDATE`

---

## 1. Executive Summary

对冻结候选版本运行了完整的 328 条 Easy Query（D 模式，生产默认配置：`dEnabled=true, gEnabled=true, guard=enabled`），328/328 全部成功执行，**0 错误、0 超时**。

核心发现：

- **Zero-result 率 14.3%（47/328），Low-result 率 18.9%（62/328）**，合计约 **33.2%** 的常见/简单词汇查询返回不可用结果。
- 对 202 条（61.6%，覆盖全部异常类别 + 随机对照样本）进行了逐条人工等效相关性复核：**PASS 13 / PARTIAL 106 / FAIL 74 / NOT_PROVABLE 9**。FAIL 率 36.6%（74/202）。
- **11 个 `>=1000` flooding case，人工复核 11/11 全部为 FAIL**——都是与查询词完全无关的通用词 relaxed-match 碰撞结果，且该机制与 Stage 7 Hard Query 阶段（Prompt 7）已确认的 `MATCHING_THRESHOLD` 根因**完全相同**。这证明该问题不是 Hard Query 特有的边缘情况，而是**影响普通常见词汇的系统性检索机制风险**。
- Rewrite 触发后，**66%（103/155）仍然是 zero/low 结果**；Rewrite 触发的 case 中人工判定 FAIL 率（53/155 ≈ 34.2%）明显高于未触发 Rewrite 的 case（21/47 ≈ 44.7%，注：未触发 Rewrite 组的复核样本本身即偏向随机对照，非全量筛选异常）。
- 发现至少 20+ 例"Rewrite 触发后从有结果（1-19 条 relaxed 匹配）变为 0 结果"的具体案例（如 沙发家具 19→0、耳机 2→0、香氛 1→0、万圣节英文版 1→0 等），根因是 Rewrite 空输出 + `hasStrict` 严格过滤器叠加导致的结果劣化。
- 未发现候选版本本身崩溃或不可用；执行链路完全健康，问题集中在**检索相关性**而非**系统稳定性**。

---

## 2. Frozen Candidate Version

```
Production repository: /Users/baobaoli/Desktop/curify-frontend
Branch: baobao/search-relevance-phrase-alias-2026-07-09
HEAD:   c062e618bce4044bedf718aadf59ff69f0999344
```

关键文件 SHA-256（运行前后一致，全程未变更）：

```
lib/searchTokens.ts          38a1fa18...0847ba4
lib/searchRewrite.ts         a54aaf9e...833d45
lib/cjk_tokenizer.ts         6a637647...4dc1dc6b6
lib/query_phrase_aliases.ts  eb99cac6...4fc6fc1e971
lib/zh_normalize.ts          a8c42f05...071df34
lib/topic_resolver.ts        180bb8cc...25865981b0f
search/page.tsx              a1937285...44cff4c
package.json / package-lock.json  1233845e... / b75bd1c7...
```

Catalog 版本：`nano_inspiration.json` 3209 条资产（sha256 f7dacc56...），与 `nano_templates.json`（sha256 8a11ad73...）共同构成检索语料，均为只读引用，未修改。

模型配置：`gpt-4o-mini`，`temperature=0.4`（来自 `lib/searchRewrite.ts` 源码常量，非本 Prompt 假设）。

Low-result 阈值：`LOW_RESULT_THRESHOLD = 5`（来自 `app/[locale]/(public)/search/page.tsx:47`，静态常量，非动态规则；已与执行引擎 `engine.cjs` 交叉核实一致）。

执行引擎复用了 Stage 7R Prompt 4 V2 已验证、哈希锁定的真实生产代码 bundle（`scripts/curify-search-stage7-full-rerun-v2/_bundle_current.cjs`），每次运行都通过 `drift_check` 字段实时核验候选文件哈希未漂移；328 次运行的 `drift_check.missing` 全部为 0，`pageTsxSha256`/`searchTokensSha256` 全部与冻结值一致。

---

## 3. Input Authority

权威 300+ Easy Query 文件：**`docs/daily_report/7.7/05_simple_head_term_seed_bank_2026-07-07.csv`（328 行）**。

选择依据：项目自身 Stage 1 测试数据盘点报告（`docs/daily_report/7.11/search-optimization-stage-1/TEST_DATA_INVENTORY_2026-07-11.md` 第 5、15 节）已明确排查过全部候选，结论是"不存在满足 300+ 且已执行测试定义的 easy-query 数据集"，并**明确推荐**本文件（328 条中英双语头部词）作为组建该数据集的最合适起点——因为它是唯一同时满足"≥300 行、真正 easy 风格（非 niche/hard）、从未被执行过（无陈旧结果风险）、与 68 条 Hard Query / 12 个 P0 零重叠"四个条件的候选。其余候选（04 号 niche 池 504 条、02/03 号扩展池 188+98 条、`search_eval_set.json` 137 条不同代码路径回归集、1,118 条 taxonomy candidate 混合表）均被排除，理由详见 `easy_query_input_inventory_2026-07-14.csv`。

---

## 4. Data Cleaning

328 行 → 清洗后 **328 条唯一 Query**（无重复、无空值、内部空格/大小写核查通过）。语言分布：中文 267 / 英文 61。与 68 条 Hard Query、12 个 P0 交集均为 **0**（程序化 normalize 比对确认）。

字段完整性：`easy_id, query, source_file, source_row, language, query_type, contains_proper_noun, contains_number_or_model, contains_mixed_language, duplicate_status, overlaps_hard_68, overlaps_p0_12, easy_confidence, notes` 全部字段 328/328 已填写，无缺失。

`easy_confidence` 分布：HIGH 324 / MEDIUM 4（因含专有名词或中英混合字符触发降级，如 "Y2K"）/ LOW 0。

---

## 5. Query Composition

数据集本身是**裸露单字/双字头部词**（如"鲜花""flower""极简""minimalist"），而非"名词+设计意图"式的自然语言查询（如 68 条 Hard Query 里的"dreamcore aesthetic moodboard"）。这是"easy/常见词汇"定义下的合理构成，但对一个以设计模板/灵感为主体的 Catalog 而言，天然比多词自然语言查询更难被字面匹配命中——这一构成特征本身也是本报告需要如实指出的一个方法论限制（见第 20 节）。

`query_type` 分布（10 类，各 24-41 条）：object / style / scene / industry / format / product_category / material / audience / festival / action，覆盖较为均衡。

---

## 6. Execution Completeness

```
Expected: 328    Actual: 328    Successful: 328    Errors: 0    Timeouts: 0    Missing: 0    Duplicates: 0    Retries: 0
```

全部 328 次运行均在第一次尝试即成功完成，未触发 checkpoint/resume 的重跑逻辑，运行过程中候选版本文件哈希持续核验一致，未出现 `BLOCKED_CANDIDATE_VERSION_CHANGED`。

---

## 7. Zero / Low Results

```
Zero-result: 47/328 = 14.33%
Low-result (0<n<5): 62/328 = 18.90%
合计不可用/极弱: 109/328 = 33.23%
```

Zero-result 集中在两类：(a) 常见具体物品/材质裸词（背包、雨伞、台灯、镜子、耳机、相框、风筝、皮革、塑料、羊毛、藤编、混凝土、棉麻、velvet、香水/perfume、书签、窗帘、沙发家具等）——判定为 **FAIL**（常见词汇理应有可用设计内容）；(b) 更偏商业/运营向的垂类词（房地产、3C数码、二手交易、招募、招聘、预售、直播）——判定为 **NOT_PROVABLE**（无法确定 Catalog 是否本就不覆盖该垂类，还是检索机制问题）。

---

## 8. Rewrite Performance

```
Rewrite Trigger: 155/328 = 47.26%
Model Output Rate: 91.61%（155 次触发中，141 次模型产出可用 rewrite/decomposition）
Executable Rewrite Rate: 90.97%
Second-pass Execution Rate: 90.97%
Rewrite Improved (人工判定): 75/155
Rewrite Neutral: 63/155
Rewrite Worsened: 17/155（含多例"从个位数结果变为 0"的严重劣化，如 沙发家具 19→0、耳机 2→0、万圣节英文版 1→0）
```

Rewrite 触发后，**66%（103/155）依然是 zero/low 结果**（人工复核确认，非仅计数判定）。这不能简单归因于"Rewrite 没帮上忙"——多例显示 Rewrite 的**空输出**（`rawCandidateCount=0`，`errorType=empty_output`）叠加检索引擎的 `hasStrict` 严格过滤逻辑（一旦存在任意 strict 匹配，只保留 strict 结果，丢弃全部 relaxed 匹配），导致触发前已有的少量 relaxed 匹配结果被清零。这是本次验证发现的一个具体、可复现的机制级风险点。

---

## 9. Guard Performance

Guard（`gEnabled=true`）在全部 155 次 Rewrite 触发中均正常介入（`guard_triggered` 诊断字段完整记录 `rejectedSlots` / `emptyTokenPaths` / `noValidRewritePath`）。未发现 Guard False Accept（明显应拦截但放行的危险泛化）或大规模 False Reject（应放行但被拦截）的独立证据；Guard 层面本身未观测到异常，风险主要来自其下游的匹配/过滤逻辑而非 Guard 判定本身。

---

## 10. Flooding / Full-catalog

```
>=1000: 11/328 = 3.35%
Full-catalog (=3209): 0/328
```

11 个 `>=1000` case 人工逐条核查（**11/11 = 100% FAIL**）：

| Query | 语言 | 结果数 | 判定 |
|---|---|---:|---|
| cork | en | 1611 | FAIL — 通用词碰撞，Top10 均无关 |
| terrazzo | en | 1601 | FAIL — 同上 |
| minimalist | en | 1889 | FAIL — Top10 均无关（西游记人物/DNA双螺旋等） |
| vintage | en | 1008 | FAIL — Top10 均无关（中式菜品/剪纸等） |
| 扁平化 | zh | 1040 | FAIL — Top10 均为"microsoft ai dilemma"系列模板，无关 |
| wabi-sabi | en | 2056 | FAIL — 仅第1条相关，1/10 |
| 童趣 | zh | 3008 | FAIL — Top10 均无关 |
| 海报 | zh | 1913 | FAIL — 核心产品品类词，Top10 仍是无关角色/菜品 |
| poster | en | 1896 | FAIL — 与中文版同样的碰撞模式 |
| card | en | 1296 | FAIL — Top10 均无关 |
| 家庭主妇 | zh | 1115 | FAIL — Top10 均无关 |

这与 Prompt 7 中 Stage 7 Hard Query 的 `MATCHING_THRESHOLD` 根因（relaxed-match 阈值 `ceil(n/2)` + 无停用词表的通用词碰撞）**完全一致**，且这里出现的词（poster、card、minimalist、vintage）都是**极其基础、高频、非 Hard 的常见设计词汇**，证明该机制风险不局限于此前识别的 5 条 Hard Query，而是更广泛的系统性风险。

---

## 11. Language Breakdown

```
Chinese (267):  Zero 16.10%  Low 20.60%  Human FAIL 59/170 reviewed（34.7%）
English (61):   Zero  6.56%  Low 11.48%  Human FAIL 15/32 reviewed（46.9%，样本量小，需谨慎解读）
Mixed (2):      样本量过小（2条，均为"Z世代"类单字符误判），不具统计意义
```

中文查询的 Zero/Low 率明显高于英文（16.1%+20.6%=36.7% vs 6.56%+11.48%=18.0%），但英文复核样本中 FAIL 占比反而更高——这提示"结果数量"和"结果相关性"是两个独立维度：英文查询更少出现 0 结果，但一旦有结果，相关性未必更好（例如 poster/card/minimalist/vintage 均为英文，且全部人工判定 FAIL）。

同概念中英对照发现明显不对称的案例（见第 16 节 Tokenizer Risk）：万圣节（zh）257 结果 vs halloween（en）0 结果；圣诞节（zh）1 条通用"en-zh"标签 vs christmas（en）7 条真实圣诞相关结果。

---

## 12. Proper Noun Breakdown

数据集中仅 2 条含专有名词特征（Y2K、3C数码），样本量过小，不具统计意义，如实标注 `NOT_PROVABLE` 级别的样本不足，不强行给出结论。

---

## 13. Human Spot-check

```
Reviewed: 202/328 (61.6%)
PASS: 13   PARTIAL: 106   FAIL: 74   NOT_PROVABLE: 9
```

复核范围覆盖：全部 Zero Result（47）、全部 Low Result（62）、全部 Rewrite Trigger（155）、全部 `>=1000`（11）、全部 Full-catalog（0，不适用）、全部 Timeout（0，不适用）、30 条随机正常 Query、10 条不触发 Rewrite 的正常对照 Query。由于异常类别并集（zero∪low∪rewrite∪gte1000∪timeout = 166/328 = 50.6%）已超过 50% 门槛，按规则未做抽样缩减，异常类别全部逐条复核；在此基础上再补充 30+10 条对照样本，总复核覆盖率 61.6%。剩余 126 条为"未触发 Rewrite 且结果数健康（≥5、非 flooding）"的 Query，未逐条复核。

---

## 14. Anomaly Analysis

`easy_query_anomalies_2026-07-14.csv` 汇总 144 条异常 Case（Zero/Low/Rewrite-Worsened/`>=1000`/Wrong-Entity-候选/Tokenizer-风险/Human-FAIL 任一命中）。核心模式：

1. **通用词 relaxed-match flooding**（第 10 节 11 条 `>=1000` + 多条 100-900 区间的同类模式，如 Scandinavian 891、光明节 218、复活节 248、万圣节 257）——与 Hard Query 阶段根因相同的系统性机制。
2. **Rewrite 空输出 + strict-only 过滤 → 结果归零**（沙发家具 19→0、耳机 2→0、香氛 1→0、万圣节英文版 1→0 等 20+ 例）。
3. **裸物品/材质词大面积零结果**（约 35+ 例，见第 7 节）。

---

## 15. Tokenizer Risk

未发现大规模、系统性的中文分词误拆（`tokens.primary` 字段抽查显示分词结果基本合理，如"3C数码"→`["3c","数码"]`正确切分）。但发现一类**跨语言结果不对称**风险，怀疑与分词/相同概念在双语路径下走了不同的 relaxed-match 分支有关：

| 概念 | 中文结果 | 英文结果 | 现象 |
|---|---:|---:|---|
| 万圣节 / halloween | 257（flood，判定FAIL） | 0 | 同一概念两种语言表现天差地别 |
| 圣诞节 / christmas | 1（通用"en-zh"标签，判定FAIL） | 7（真实圣诞相关内容） | 中文版拿到的是无意义通用标签，英文版有真实内容 |
| wood / 木头 | final=1（"Chris Wood"姓氏巧合） | final=1（同样的"Chris Wood"姓氏巧合） | 两种语言都被同一个新西兰球员姓氏误命中，非真实木材相关内容 |

此风险标记为 `NEEDS_EVIDENCE`（需要 Search/Tokenizer Owner 进一步复核具体路径分歧原因），不在本 Prompt 范围内下定论或修复。

---

## 16. Wrong Entity Risk

未发现 Stage 7/P0 阶段那类"具名 IP 被替换为另一同类具名 IP"式的严重 Wrong Entity（Easy Query 数据集本身多为通用词汇，缺少具名实体供替换）。唯一相关观察是 **E046（木头/wood）与 E047（wood, en）均被"Chris Wood"（新西兰国脚姓氏）误命中**——这是一种"姓氏/常见词碰撞"式的弱 Wrong Entity 信号，不涉及 Rewrite 主动替换实体，风险等级低于 P0 中确认的 Q02（NCT Dream → ILLIT）案例，标记为 `WRONG_ENTITY_CANDIDATE`，供 Search Owner 参考。

---

## 17. Matching Threshold Risk

**核心风险确认**：第 10 节 11/11 flooding case 全部证实为 relaxed-match 阈值/通用词碰撞问题，且该问题在本次 Easy Query 验证中被证明**广泛存在于普通、高频、非 Hard 的常见设计词汇**（poster、card、minimalist、vintage 等），而不只是 Prompt 7 此前识别的 5 条 Hard Query。这是本次验证最重要的升级性发现：**Matching Threshold 问题的实际影响范围比 Stage 7 阶段评估的更广**。

---

## 18. Regression Assessment

```
Regression Gate: SYSTEMATIC_REGRESSION
```

判定依据（对照 Section 20 标准，逐条核对）：

- 多个常见 Query 因同一机制失败：**成立**——11/11 flooding case + 数十例通用词碰撞均指向同一 relaxed-match 阈值机制。
- Rewrite 对普通 Query 频繁有害：**部分成立**——17/155（11%）明确劣化，另有约 20+ 例"触发前已有少量结果、触发后清零"的具体劣化实例。
- Full-catalog 或 flooding 重现：**成立**——11 例 `>=1000`，与 Stage 7 已确认机制一致地重现。
- 普通 Query Zero/Low 显著异常：**成立**——合计 33.2% 的 Easy Query 处于不可用或极弱可用状态。
- 人工 FAIL 比例明显不可接受：**成立**——202 条复核样本中 74 条（36.6%）判定 FAIL。

**重要方法论说明（按 Section 19-B 要求明确写出）**：`Regression is behavior-based, not strict historical before/after.` 这 328 条 Query 此前从未被执行过测试（Stage 1 盘点已确认），因此本报告**无法证明**这是 2026-07-10 phrase-alias 分支引入的新退化，也**无法排除** LOW_RESULT_THRESHOLD 网关、relaxed-match 阈值、Rewrite 空输出处理等机制在此之前就已存在同样表现——这些机制的代码注释显示其中多数早于本分支提交。本报告的 `SYSTEMATIC_REGRESSION` 判定是基于**当前候选版本的现状行为**是否满足 Section 20 列出的客观标准，而非对因果关系或"何时引入"的断言。

---

## 19. Comparison with Stage 7

Stage 7（68 条 Hard Query，Prompt 5/6/7）已确认 `MATCHING_THRESHOLD` 是 22 条 Verified FAIL 中 4 条的根因，并被列为 P1 系统性问题（`MATCHING_EXPERIMENT` 处理路线）。本次 Easy Query 验证提供了**独立的额外证据**，证明该同一机制同样广泛影响普通词汇查询，而非仅限于已识别的 Hard Query 子集——这应当**提升**该问题在 Prompt 7 优先级排序中的紧迫性，即使本 Prompt 按用户指示不执行任何修复。

---

## 20. Limitations

1. 输入数据集本身是裸头部词（非自然语言查询），对模板类 Catalog 天然更难匹配，这一构成特征会放大 Zero/Low 结果率，需要在解读"33.2% zero/low"时一并考虑（见第 5 节）。
2. 无历史 Baseline，回归判定为行为判定而非严格前后对比（见第 18 节）。
3. 202/328（61.6%）复核，126 条健康、非异常、未触发 Rewrite 的 Query 未逐条复核（合理，因为它们不属于任何强制复核类别）。
4. 中英混合语言子集样本量过小（2 条），未能得出可靠结论。
5. Wrong Entity / Tokenizer 风险为本次观察到的模式信号，未像 Prompt 7 那样做逐条独立 Catalog 检索验证。

---

## 21. Final Gate

```
Execution Gate:  EASY_QUERY_RUN_COMPLETE
Regression Gate: SYSTEMATIC_REGRESSION
```

## 22. Recommendation for Taxonomy / Final Report / PR

- **不建议**直接 `PROCEED_TO_TAXONOMY_DRY_RUN` 或 `PROCEED_TO_FINAL_REPORT_WITH_LIMITATIONS`——因为"Easy Query 无系统性回归"和"Easy Query 基本安全"两个前提均不成立（见第 18 节）。
- 数据显示的问题**范围广、机制单一集中**（同一 relaxed-match 阈值机制），并非"少量、可有限修复"的规模，因此严格来说也不完全匹配 `RETURN_TO_LIMITED_SEARCH_REPAIR` 的"少量明确回归"表述。
- 按 Section 26 标准客观评估，本报告给出的下一步判定是 **`BLOCK_RELEASE_CANDIDATE`**：`系统性回归`、`flooding 重现`、`大量普通 Query 失败` 三项客观标准均成立。
- **需要向用户明确指出的张力**：Prompt 8 开始时用户已做出 `FREEZE_CURRENT_SEARCH_CODE` 的项目决策，本阶段不执行修复。本报告的数据结论客观上与"直接冻结并继续下一阶段"的预期路径存在冲突——这不是本 Prompt 可以自行调和的产品/资源取舍问题，如实呈现证据后，是否接受该风险继续推进（`NEEDS_OWNER_DECISION`）应由用户/产品决策，而不是本报告代为决定。
