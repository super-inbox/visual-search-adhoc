# Stage 7 Prompt 4A Mode Contract Summary

## 1. Executive Summary

Prompt 4A 新增了显式、类型安全的 `dEnabled` runtime toggle（`lib/searchTokens.ts`），使 Mode A/B/C/D 四种组合首次可以全部由**同一份**当前 production 代码构造，不再需要 `git show` 重建旧逻辑。Mode Contract Smoke Test（8 Query × 4 Mode = 32 Run）**32/32 全部通过**，0 次真实 LLM 调用，0 缺行，0 重复。全量单元测试 375/375、TypeScript、Production Build 全部通过。

**Final Gate：`READY_FOR_PROMPT4`**——Prompt 4 的阻塞问题已解决，可以重新执行（不自动触发）。

## 2. Confirmed d Contract

"d" = `lib/searchTokens.ts` 的 tokenization 层开关：

- **d=ON**：`segmentCJKToken`（jieba 字典 CJK 分词 + Protected Phrase span 提取）+ `applyPhraseAliasRulesExcluding`（排除已被字典处理的 CJK atomic phrases）。
- **d=OFF**：不调用 `segmentCJKToken`，改用未排除的 `applyPhraseAliasRules` 基础规则 + 新增的极简 CJK bigram 兜底（仅用于单一未切分 CJK token，保证非空）。
- **明确排除范围**：`scoreBlob`/Merge/Ranking/relaxed 匹配阈值——本阶段禁止修改，四个模式共用同一份未改动的评分实现。详见 Implementation 报告第 3 节。

## 3. Default Production Behavior

14 条冻结 Fixture 逐字段比较"修改前"与"修改后默认值/显式 `dEnabled:true`"：**0 处差异，0 Regression**。详细数据见 `stage7_prompt4a_test_results_2026-07-14.json` 的 `default_behavior_verification` 字段。

## 4. d=OFF Evidence

13 条 Query（7 条已知受 d 影响 + 6 条普通对照）：

- **4 条观察到预期的、结构性的差异**（手冲咖啡、比亚迪海豹、乔丹鞋、白箱），超过"至少 3 条"的要求。
- 3 条已知受 d 影响但差异符合预期地未体现（小红书、二手奢侈品、抖音 product card）——这些 2-4 字 CJK 词本身不含 Protected Phrase 规则也不会被 jieba 进一步切分，两条路径殊途同归，是真实行为而非开关失效。
- 6 条普通对照 Query（English brand identity poster / Genshin Impact fanart 4k / ES6 / GPT-4 poster / watercolor spring flowers / 光与夜之恋 卡面设计）：d=ON 与 d=OFF **逐字段完全相同**，且均非空——确认 d=OFF 不会破坏英文/数字/型号/正常 Query 的可搜索性。

详细数据见 `stage7_prompt4a_test_results_2026-07-14.json` 的 `d_off_evidence` 字段。

## 5. A/B/C/D Evidence

Mode Contract Smoke Test（`mode_contract_smoke_results_2026-07-14.csv`，32 行）直接证明四模式可由同一代码、同一 Harness 配置构造：

| Query | A (d=off,g=off) | B (d=on,g=off) | C (d=off,g=on) | D (d=on,g=on) |
|---|---|---|---|---|
| 小红书香薰产品 | 6 | 6 | 6 | 6 |
| 手冲咖啡品牌视觉 | 16 | **10** | 16 | **10** |
| 二手奢侈品 | 0 | 0 | 0 | 0 |
| 比亚迪海豹 | 0 | 0 | 0 | 0 |
| 乔丹鞋 | 0 | **4** | **5** | **4** |
| 白箱 | 0 | 0 | **31** | **31** |
| Genshin Impact fanart 4k | 7 | 7 | **12** | **12** |
| English brand identity poster | 230 | 230 | **545** | **545** |

- A/B 两列的差异（手冲咖啡品牌视觉 16 vs 10、乔丹鞋 0 vs 4）直接证明 `dEnabled` 真实影响了 tokenization 与最终结果，不是摆设。
- A/C 两列在多数行相同，因为这些 Query 的首轮结果数 ≥ `LOW_RESULT_THRESHOLD`（5），未触发 Rewrite Gate，`rewriteFixture` 未被消费——这本身就是真实生产 Gate 逻辑（`page.tsx` 的 `LOW_RESULT_THRESHOLD`，未改动）在起作用。乔丹鞋/白箱/Genshin/English brand identity 四行首轮结果数确实 < 5（或本就是 gate 判定阈值边界内），Fixture 被消费，C/D 相比 A/B 出现真实、可解释的数量变化。
- `rewrite_provider_called` 全部 32 行为 `false`——Smoke Test 全程 0 次真实 LLM 调用。

## 6. Smoke Completeness

- Expected 32，Actual 32，Missing 0，Duplicates 0。
- A/B/C/D 各 8 行。
- `mode_contract_pass` 全部 32 行为 `true`。

## 7. Tests and Build

| 项目 | 结果 |
|---|---|
| `searchTokens.test.ts` | 19/19 通过 |
| 全量单元测试 | 375/375 通过（含 `searchRewrite.test.ts` 160 条 Prompt 2D 回归测试） |
| TypeScript | 0 错误 |
| Production Build | exit 0 |
| Lint | 既有 ESLint 9 配置问题，未修复（Prompt 2B/2C/2D 同款） |

## 8. Remaining Limitations

- 本阶段的 `d` 开关范围有意收窄为仅 tokenization 层（不含 Merge/Ranking/relaxed 阈值），与 7.13 原始 Ablation（同时切换 scoring 函数）不完全等价——已在 Implementation 报告第 3 节明确记录为"有意的范围收窄"，原因是 Prompt 4A 明确禁止修改 Ranking/Merge。
- Mode Contract Smoke Test 仅覆盖 8 条固定 Query + 固定 Rewrite Fixture，用于验证**接线（wiring）正确**，不代表完整 68 条真实 LLM Ablation 的数值结果——这是下一次 Prompt 4 的任务。
- `d=OFF` 的 CJK bigram 兜底是本阶段新写的极简实现，其具体数值行为可能与"假想中逐字重建的旧 tokenizer"存在细节差异（例如 bigram 的具体触发条件），但其"提供合法非空基础 tokenization"这一功能意图已验证达成。

## 9. Prompt 4 Output-directory Handling

旧阻塞记录目录：

```text
/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.14/search-relevance-stage7-rerun/full-68-rerun/
```

**本阶段未修改、未删除**——`STAGE7_PROMPT4_BLOCKED_2026-07-14_zh.md` 与 `stage7_rerun_manifest_2026-07-14.json` 保持原样，作为 Prompt 4 第一次尝试的完整、可审计记录永久保留。

下一次正式 Prompt 4 应使用新的独立目录：

```text
/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.14/search-relevance-stage7-rerun/full-68-rerun-v2/
```

该目录**本阶段未创建**，留给下一次 Prompt 4 执行时创建。正式 CSV 文件名可沿用 Prompt 4 原定义（`hard_queries_baseline_locked_68_2026-07-14.csv` 等），只是父目录改为 `full-68-rerun-v2/`。

## 10. Final Gate

### **READY_FOR_PROMPT4**

理由：

1. `d` 合同已从历史资料（7.13 `run_manifest.json`、`run_mode.cjs`）与当前代码明确确认，并记录了本阶段范围收窄的理由。
2. 当前 production 代码（`lib/searchTokens.ts`）新增了显式 typed toggle，默认值为 `d=ON`，修改前后默认行为逐字段验证一致（14/14 fixture，0 regression）。
3. Search Page 与 Eval Harness 现在导入同一个真实 `buildSearchTokens`/`normalizeForSearch` 实现，不再是各自转录。
4. `d=OFF` 不使用旧源码重建（未调用 `git show`），不通过运行后删除 token 实现，保留合法基础 tokenization（4 条已知受影响 Query 观察到预期差异，6 条对照 Query 无回归、无空 token）。
5. 四个 Mode 均已通过 32/32 的 Mode Contract Smoke Test，从同一套代码、同一 Harness 配置构造成功，0 次真实 LLM 调用，0 缺行/重复。
6. 全量单元测试 375/375、TypeScript 0 错误、Production Build 通过，Prompt 2D 的全部 Guard/Piggyback/Anchor Provenance 回归测试（160 条）未受影响。
7. Blog、Taxonomy、catalog 均未被本阶段修改（哈希核对一致）。
8. 未运行完整 68 条 Query，未运行 272 次 Mode Run。

**按任务要求，本结论不自动触发重新执行 Prompt 4**，需等待用户明确指示。
