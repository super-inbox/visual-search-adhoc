# Stage 7 Prompt 4 — BLOCKED_INVALID_ABLATION_MODE

## 1. Executive Summary

Prompt 4 的前置 Gate（Prompt 2D 结论、production 代码状态）**已核验通过**，但在正式运行 272 次 Mode Run 之前，按 Section 8 要求"先读取旧 Stage 7 运行脚本和报告，确认 d、g 的实际定义，在运行前创建并冻结 Mode Contract"时，发现一个无法在本阶段规则下解决的结构性冲突：**当前 production 代码没有任何运行时开关可以关闭"d"（Stage 6 字典/分词器特性）**。构造 Mode A（d=OFF, g=OFF）与 Mode C（d=OFF, g=ON）唯一已知的方法，是本 Prompt 明确禁止的技术（`git show HEAD:<file>` 文本重建旧逻辑）。

已就此冲突向用户请示，用户选择：**立即停止，输出 `BLOCKED_INVALID_ABLATION_MODE`，不运行任何完整 68 Query，不调用 LLM，不创建正式 Stage 7 重跑结果**。本文档记录完整的核验证据、冲突分析和后续建议，供下一阶段修复该冲突后重新执行。

## 2. Section 0 前置 Gate 核验（已通过）

- Prompt 2D Final Summary（`/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.14/search-relevance-stage7-rerun/prompt2d/STAGE7_PROMPT2D_FINAL_SUMMARY_2026-07-14_zh.md`）第 9 行、69 行、137 行均明确包含 `READY_FOR_FULL_68`。
- Production working tree 实际核验（非仅摘要）：
  - `lib/searchRewrite.ts` 中 `grep -c "anchorBasisForDownstream"` = 13 处；`grep -c "bindTarget"` = 4 处。
  - `evaluateRewriteCandidate` 函数存在（第 805 行），签名含 `bindTarget` 第 4 参数。
  - `SubjectCandidateEvaluation.anchorBasisForDownstream: string` 字段存在（第 1007 行）。
  - `lib/__tests__/searchRewrite.test.ts` 中 `describe("Anchor Piggyback fix (Stage 7R Prompt 2D)"` 存在。
  - 分支 `baobao/search-relevance-phrase-alias-2026-07-09`，HEAD `c062e618bce4044bedf718aadf59ff69f0999344`，与预期一致。

**结论：前置 Gate 满足，Prompt 2D 修复确认存在于当前 working tree。**

## 3. Section 8 Mode Contract 冲突发现

### 3.1 已读取的旧 Stage 7 脚本与报告

- `/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.13/search-optimization-stage-7/run_manifest.json`
- `/Users/baobaoli/Desktop/visual-search-adhoc/scripts/curify-search-collect-stage7/run_mode.cjs`

`run_manifest.json` 中 `run_modes` 字段确认旧 Stage 7 的 Mode 定义：

```json
{"mode": "A", "d_enabled": false, "g_enabled": false, "meaning": "neither — reconstructed offline via harness, using pre-Stage-6 page.tsx logic (git HEAD) and no rewrite call"},
{"mode": "B", "d_enabled": true,  "g_enabled": false, "meaning": "dictionary-only — Stage 6 tokenizer/scoring, no rewrite call"},
{"mode": "C", "d_enabled": false, "g_enabled": true,  "meaning": "rewrite-only — pre-Stage-6 tokenizer/scoring, real Stage 5 getMultiQueryPaths() calls"},
{"mode": "D", "d_enabled": true,  "g_enabled": true,  "meaning": "d+g — Stage 6 tokenizer/scoring + real Stage 5 rewrite, the current production code path"}
```

`run_mode.cjs` 第 11 行注释与第 189 行代码段确认：Mode A/C 的 d=OFF 是通过 `git show HEAD:app/[locale]/(public)/search/page.tsx`（读取 Stage 6 合并前的已提交版本）在独立 harness 中重建实现的，**不是**通过当前 production 代码的某个运行时开关。

### 3.2 当前 production 代码核验

```
$ grep -n "process.env\." "app/[locale]/(public)/search/page.tsx"
（无匹配）

$ grep -n "process.env\." lib/searchRewrite.ts
337:  const key = process.env.OPENAI_API_KEY;
（仅 API Key，无 feature flag）

$ grep -rn "legacyToken|basicToken|simpleToken|d_enabled|D_ENABLED|ENABLE_DICTIONARY|DISABLE_DICTIONARY|featureFlag|FEATURE_FLAG" \
    "app/[locale]/(public)/search/page.tsx" lib/searchRewrite.ts lib/cjk_tokenizer.ts lib/query_phrase_aliases.ts
（无匹配）

$ grep -n "function buildSearchTokens|function scoreBlob|function scoreQueryTokens" "app/[locale]/(public)/search/page.tsx"
151:function buildSearchTokens(query: string): {...}
312:function scoreBlob(...)
583:  function scoreQueryTokens(...)
```

`buildSearchTokens`（page.tsx 第 151 行起）**无条件**调用 `segmentCJKToken`（第 204 行）、`applyPhraseAliasRulesExcluding`（第 227 行）等 Stage 6 字典/分词器函数——当前代码库中只存在这**一套**分词实现，没有第二套"无字典"分词器可供切换，也没有任何环境变量或参数可以关闭它。

### 3.3 结论

在**不重建旧逻辑（禁止 `git show`）、不手工删除 token 模拟 d OFF（Section 8.1 明确禁止）**的约束下，Mode A（d=OFF,g=OFF）与 Mode C（d=OFF,g=ON）**无法**用当前真实、未修改的 production 代码可靠构造。这直接触发 Section 8 规定的：

```text
BLOCKED_INVALID_ABLATION_MODE
```

Mode B（d=ON,g=OFF：跳过 LLM 调用，仅用当前 `buildSearchTokens`/`scoreQueryTokens` 对原始 Query 打分）与 Mode D（d=ON,g=ON：当前完整 production 路径）本身**是**可以仅用当前真实代码可靠构造的（均为"当前代码，是否调用 LLM"的二元切换，不涉及任何重建），但由于任务要求 A/B/C/D 四模式必须同批次、可比、共同构成完整消融，且规则不允许"部分模式伪造/部分模式缺失"来拼凑完整 272 行，因此在未获得用户对 Mode A/C 处理方式的明确决定前，**不单独运行 Mode B/D**。

## 4. 用户决策

已通过结构化提问向用户说明上述冲突及三个可选路径（立即停止 / 允许对 d 维度使用受限的 git-show 复用例外 / 仅运行可行的 Mode B/D 共 136 次）。**用户选择：立即停止（Stop now）**。

## 5. 本阶段实际执行的操作（全部只读，无 LLM 调用）

- 读取 Prompt 2D Final Summary、Replay/Live 报告与 Manifest（只读）。
- 核验 production 代码中 Prompt 2D 修复的存在性（`grep`，只读）。
- 记录执行前快照：`curify-frontend` 分支/HEAD/status/diff-stat/关键文件哈希；`visual-search-adhoc` 分支/HEAD/status（见 `stage7_rerun_manifest_2026-07-14.json`）。
- 核验权威 68 Query 文件（`docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv`，SHA-256 `00bd2cff...`，68 行，无重复/空值）与旧 Baseline（`docs/daily_report/7.13/.../hard_queries_68_baseline.csv`，SHA-256 `904ea6a5...`，与任务给定值一致）。逐行核对确认两文件的 68 条 Query 文本 1:1 顺序完全一致，Query ID 采用 `Q01`-`Q68`（按行序，与 Baseline 一致）。
- 读取旧 Stage 7 脚本与报告，确认 Mode Contract 定义并发现上述冲突。
- **未**创建 `hard_queries_baseline_locked_68_2026-07-14.csv` 等 7 个正式产出文件（因为它们代表已完成的真实运行结果，在 Mode A/C 无法构造的情况下创建会构成"伪造"）。
- **未**调用任何 LLM。
- **未**修改 production 代码、Baseline、权威 Query 文件、7.13 文件、Prompt 0-2D 文件。
- **未**执行任何 git 写操作。

## 6. 后续建议（供下一阶段参考，本阶段未执行）

若要解除该阻塞，需要以下之一（均需用户或后续 Prompt 明确决定，本阶段不擅自选择）：

1. **新增一个真正的运行时 `d` 开关**：在 production 代码（或一个明确标注为 evaluation-only、不影响真实用户流量的旁路参数）中添加一个可关闭 Stage 6 字典/分词特性的显式 feature flag，使 Mode A/C 可以用"当前代码 + 显式 flag"而非"历史代码重建"的方式构造——但这本身属于 production 代码改动，超出 Prompt 4"只读评估"的声明范围，需要新的、专门的 Prompt/阶段来实现并测试该开关本身不影响 Mode B/D（即默认值必须是 d=ON，不能改变现有生产行为）。
2. **明确批准对 "d" 维度复用 7.13 的 `git show` 重建技术**（因为"d"/分词器逻辑自 7.13 以来确认未被 Prompt 2D 或任何后续修复触碰，byte-for-byte 未变）——需要用户明确授权此例外，且必须在 Manifest 与报告中显式记录为"批准的例外"而非默认允许。
3. **重新定义本阶段消融范围为仅 Mode B/D**（136 次 Run），明确放弃在本次 Prompt 4 中重新验证 d=OFF 的两个模式，理由是"d" 逻辑本就不是 Prompt 2D 修复涉及的范围——需要用户明确签署对 68×4=272 强制要求的偏离。

## 7. Stage 7 Gate

```text
BLOCKED
```

理由：Mode Contract 无法在当前规则约束下用真实 production 代码可靠构造，Section 8 明确规定此情形下必须输出 `BLOCKED_INVALID_ABLATION_MODE` 并停止，不得伪造 A/B/C/D。

## 8. 是否可以进入 Prompt 5

```text
NO
```
