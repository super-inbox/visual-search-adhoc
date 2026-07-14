# Stage 7 Prompt 2D Piggyback Guard Implementation

## 1. Executive Summary

Prompt 2C 结论为 `NEEDS_ANOTHER_GUARD_FIX`：Human FAIL 30.4%（7/23），其中 Q10、Q40、Q42 被确认属于同一个新缺口——**Anchor Piggyback**。本阶段通过直接读取 `lib/searchRewrite.ts` 当前代码（而非仅凭 Prompt 2C 报告摘要）确认了确切的代码路径：`flattenPathsWithDiagnostics` 在第 1125 行（修复前）把 `effectiveSubject`（Guard S 绑定后的**完整**文本，如 `"光与夜之恋 Light and Night"`）传给 `evaluateRewriteCandidate` 作为 Option A 的比较基准，导致任何与 subject **原始不安全部分**（如 `"Light and Night"` 本身的 `"light"`/`"night"` token）共享字面 token 的候选，被误判为"已与安全 subject 共享锚点"，从而绕过绑定、以未加固形式执行。

修复：新增 `anchorBasisForDownstream` 字段，区分"subject 本身天然安全时的完整比较基准"与"subject 需要绑定时，只能传递注入的锚点本身（不含 subject 原文）"。同时新增 decomposition modifier 的 native-constraint 检查（modifier 为空/纯 stopword/纯弱数字属性时提前拒绝，而非无条件绑定后依赖下游 Guard 1 兜底）。

**第二轮修正（同一阶段内自查发现，未新增范围）**：首次 Replay（修复后、rebindTarget 之前）显示 Q40 D 等多个 case 的 count 相对 Prompt 2C 不降反升（如 Q40 D: 3→919）。根因排查确认：把窄化后的 `anchorBasisForDownstream`（如仅 `"小红书"`）同时用作 Option A 比较基准**和**实际绑定/执行文本，会缩短最终检索短语的 token 总数，而 `ceil(n/2)` 松弛匹配阈值下，token 数越少绝对匹配门槛越低——这是 Piggyback 修复本身引入的一个非预期副作用，而非该副作用被有意设计。修正方式：将 `evaluateRewriteCandidate` 的 `subject` 参数拆分为两个——`subject`（继续保持窄化，仅用于 Option A 比较）与新增的可选参数 `bindTarget`（默认等于 `subject`，但 `flattenPathsWithDiagnostics` 显式传入完整的 `effectiveSubject` 作为 `bindTarget`）。这样比较基准仍然安全窄化（Piggyback 修复保持有效），但实际绑定文本恢复为完整的、经过 Guard S 校验的 subject 全文，避免不当收窄 token 数。该修正**完全未触碰** `ceil(n/2)` 公式本身或任何 Ranking/Matching 代码——修正范围仅限 `searchRewrite.ts` 内锚点绑定文本的构造方式。

修正后，绑定后的执行文本会出现字面重复（如 Q10 候选 `"Light and Night character design"` 绑定后变为 `"光与夜之恋 Light and Night Light and Night character design"`）——这是预期的、无害的字面冗余（token 去重发生在匹配/评分阶段，不影响功能），换取 token 总数与匹配阈值的正确性。

新增测试 21 条；因 `bindTarget` 修正导致 5 条既有断言的绑定文本/计数需要更新（Q10 ×2、Q42 Mode C、Q47、"basic e2e" 各 1 条），已用真实生产代码计算出的实际值更新断言。全量单元测试 356/356 通过，TypeScript 0 错误，Production Build 通过。

## 2. Prompt 2C Failure Review

逐条重新核对 Prompt 2C 的 Replay/Live 原始 CSV（非仅摘要）：

| Case | 原始数据确认 | Piggyback 确认 |
|---|---|---|
| Q10 | `decomposition:{"subject":"Light and Night","output":"character design"}`，`subject_executed_text:"光与夜之恋 Light and Night"`，`accepted_rewrite_candidates` 含 3 条含 "Light and Night" 字样的候选，`bound_rewrite_candidates` 为空 | **是**——3 条候选全部因共享 subject 绑定前的原文而绕过绑定 |
| Q40 | `decomposition:{"subject":"Xiaohongshu post",...}`，`subject_executed_text:"小红书 Xiaohongshu post"`，候选 `"Xiaohongshu post template"` 在 `accepted_rewrite_candidates`（非 bound） | **是**——同一机制 |
| Q42 C | `decomposition:{"subject":"Xiaohongshu cover",...}`，候选 `"Xiaohongshu cover template"` 同样列在 accepted（非 bound） | **是**——同一机制 |
| Q42 D | `decomposition:{"style":"minimalist","output":"cover template"}`（**无 subject**） | **否**——无 subject 时全部候选走 Option D2（绑定原 Query 提取锚点），不存在 piggyback；Live 中出现的"cover"碰撞来自 LLM 真实输出**恰好带 subject** 的不同样本，与固定 Replay 的 D-mode 输入不是同一实例，但代码路径相同 |

确认 Q10、Q40、Q42（带 subject 时）**属于同一代码路径**（`flattenPathsWithDiagnostics` 第 1125 行调用），Q42 D（无 subject）不受影响，因为其绑定逻辑走的是 `evaluateRewriteCandidate` 自身的 Option D2（绑定原 Query 提取锚点），不涉及 subject 传递。

## 3. Confirmed Piggyback Mechanism

```text
1. LLM 提出 decomposition.subject（如 "Light and Night"）
2. Guard S 判定该 subject 本身不安全（与原 Query 无共享锚点/Alias/Protected Phrase/独立锚点）
3. Guard S 绑定：executedSubject = "光与夜之恋 Light and Night"（注入原 Query 提取的锚点 "光与夜之恋"）
4. 【修复前】flattenPathsWithDiagnostics 把 executedSubject（含义 3 的完整绑定文本）传给
   evaluateRewriteCandidate 作为 subject 参数
5. evaluateRewriteCandidate 内部计算 subjectAnchors = anchorTokenSet(subject参数)
   = {"光与夜之恋", "light", "night"}（同时含安全锚点和不安全原文）
6. 候选 "Light and Night character design" 的 token 与 subjectAnchors 有交集
   （"light"、"night"）→ Option A 判定为"已共享锚点" → accepted，不绑定
7. 该候选以 "Light and Night character design"（无 "光与夜之恋" 前缀）执行，
   复现与绑定前完全相同的洪泛
```

## 4. Option A Comparison Before Fix

修复前：`evaluateRewriteCandidate` 第 850 行 `const subjectAnchors = subject ? anchorTokenSet(subject) : anchorTokenSet(original);`——其中 `subject` 参数来自调用方 `flattenPathsWithDiagnostics` 传入的 `effectiveSubject`（Guard S 绑定后的完整输出）。比较发生在 **binding 之后**：candidate 与"系统刚刚生成的绑定结果"比较，而不是与"subject 原始 LLM 输出"或"绑定前的安全性证据"比较——这正是任务描述的自证循环。

## 5. Anchor Provenance Design

新增 `SubjectCandidateEvaluation.anchorBasisForDownstream: string`：

- Subject 经 Option A/B/C 判定为**原生安全**（`bindingApplied=false`）：`anchorBasisForDownstream = subject`（完整原文可信）。
- Subject 经 Option D **绑定**（`bindingApplied=true`）：`anchorBasisForDownstream = fallbackAnchor`（仅注入的锚点本身，如 `"光与夜之恋"`/`"小红书"`/`"抖音"`，绝不包含 subject 的原始不安全文本）。

`flattenPathsWithDiagnostics` 改为把 `anchorBasisForDownstream`（而非 `effectiveSubject`）作为 `subject` 参数传给每个 rewrite 候选的 `evaluateRewriteCandidate` 调用，**并额外传入 `effectiveSubject` 作为新增的第 4 参数 `bindTarget`**——`evaluateRewriteCandidate` 内部 Option A 比较仍只用窄化的 `subject`，但 Option D 实际绑定时使用 `bindTarget`（缺省回退到 `subject`，保持向后兼容）构造 `executedQuery` 前缀。`effectiveSubject`（完整绑定文本）用于：(a) subject 自身的执行路径文本，(b) 其他 decomposition modifier 的绑定前缀（modifier 不经过 Option A 自证检查，不存在同类风险，详见第 7 节），(c) 现在也作为 rewrite 候选绑定时的 `bindTarget`。

未创建第二套 Anchor 系统——完全复用既有 `evaluateRewriteCandidate`/`evaluateSubjectCandidate`/`anchorTokens`/`isWeakNumericAttribute` 结构，只新增了一个字段和调用方传参方式的修正。

## 6. Subject Provenance

`evaluateSubjectCandidate` 本身逻辑未变（比较 raw subject vs raw original，从未涉及注入锚点，不存在自证风险）——问题完全在于其**输出如何被下游复用**。新增字段使调用方能区分"这个 subject 的判定结果是原生可信的，还是需要绑定才可信的"，并只把可信部分传递下去。

## 7. Modifier Provenance

新增 modifier native-constraint 检查（`flattenPathsWithDiagnostics` 的 decomposition 循环内）：绑定前先用 `anchorTokens(value)` 检查 modifier 是否有 executable token；若全空（stopword-only，如 `"template"`/`"the"`）→ 拒绝 `EMPTY_EXECUTABLE_TOKENS`；若全部是弱数字属性且无强标识符 → 拒绝 `WEAK_NUMERIC_ONLY_ANCHOR`。Modifier 本身不经过 Option A 自证检查（它从不"声称自己已锚定"，只是无条件绑定或拒绝），因此不存在与 rewrite 候选相同的 piggyback 循环；此项检查属于任务 Section 12 的显式要求，作为独立、范围明确的补充，而非 piggyback 主线修复的一部分。

## 8. Diagnostics

新增/复用字段：`RewriteCandidateEvaluation`/`SubjectCandidateEvaluation` 已含 `weakNumericAttributes`/`strongIdentifiers`/`sharedAnchors`/`bindingApplied`（Prompt 2C 引入），本阶段新增 `anchorBasisForDownstream`。`RejectedSlot.reason` 复用既有枚举（`EMPTY_EXECUTABLE_TOKENS`/`WEAK_NUMERIC_ONLY_ANCHOR`），未新增字符串常量——因为 modifier 拒绝的语义与既有原因完全吻合，无需另造 `PIGGYBACKED_ANCHOR_ONLY` 等新枚举（评估后认为会造成语义重复，复用更清晰，测试用例已在报告和代码注释中明确解释每次触发的真实含义，满足"必须解释实际使用方式"的要求）。

## 9. Cache Semantics

`hasExecutablePath` 逻辑零改动，自动正确反映修复后的判定（5 条新 Cache 测试验证：synthetic-only 拒绝→Negative；explicit bound path 存活→Success；safe subject+invalid modifier→Success；rejected subject 无其他路径→Negative；rejected subject+安全 rewrite→Success）。

## 10. Modified Files

- `lib/searchRewrite.ts`：`SubjectCandidateEvaluation` 新增 `anchorBasisForDownstream` 字段及其在 5 个返回分支中的赋值；`flattenPathsWithDiagnostics` 新增 `anchorBasisForDownstream` 局部变量并改用其调用 `evaluateRewriteCandidate`（原传 `effectiveSubject`）；decomposition 循环新增 modifier native-constraint 检查（2 个新 if 分支）；`evaluateRewriteCandidate` 新增第 4 个可选参数 `bindTarget`（缺省 = `subject`），Option D 绑定逻辑改用 `bindTarget` 构造 `executedQuery` 前缀（第二轮修正，见 Executive Summary）。**未改动** `evaluateRewriteCandidate`/`evaluateSubjectCandidate` 的 Option A/B/C/E 判定逻辑本身、Guard 1（page.tsx）、Merge/Ranking、relaxed 匹配阈值公式、Tokenizer、Protected Phrase、Taxonomy。
- `lib/__tests__/searchRewrite.test.ts`：更新 6 条因该修复而合法改变行为的既有测试（modifier 拒绝、Q47/Option A/Option B 场景的绑定文本变化），新增 21 条 Prompt 2D 定向测试。
- `app/[locale]/(public)/search/page.tsx`：**本阶段未修改**——`errorType=${r.reason}` 日志行（Prompt 2B 引入）已自动兼容，无需改动。

## 11. Unit Tests

| 命令 | 结果 |
|---|---|
| `npx vitest run --config vitest.unit.config.ts lib/__tests__/searchRewrite.test.ts` | 160/160 通过（139 既有 + 21 新增） |
| 全量单元测试 | **356/356 通过**（Prompt 2C 基线 335） |

新增覆盖：基础 piggyback 机制 2 条（含直接调用 `evaluateRewriteCandidate` 演示漏洞本身）；synthetic-anchor-only 拒绝 2 条；Q10/Q40/Q42（Mode C+D）机制 fixture 4 条（全部使用真实 7.13/Prompt 2C 数据，无 Query ID 硬编码）；native-safe candidate 2 条；explicit-bound 诊断 1 条；subject+modifier 组合 4 条；Prompt 2/2B/2C 回归抽样 1 条；Cache TTL 5 条。

## 12. TypeScript and Build

- `npx tsc --noEmit`：0 错误。
- `npm run build`：exit 0，成功，无新增/非既有错误。
- Lint：与 Prompt 2B/2C 相同的 ESLint 9 flat-config 预存问题，未修复。

## 13. Deferred Problems

明确记录，本阶段未修改：

- **Q06/Q12 relaxed 匹配阈值**：`ceil(n/2)` 规则在候选 token 增多后仍可能被原有泛词满足，未触碰 Ranking/Matching 代码。
- **Q41 Taxonomy/内容**："小红书"作为模板受众文案样板词导致的区分度不足，未修改 Taxonomy 或内容目录。
- **Q47 Merge/Ranking**：多路径 Union 加权（+8%/命中）未调整。
- **Q48 Tokenizer**：jieba 对"抖音"分词不一致（依上下文有时切出"抖"单字），未修改 Tokenizer 词典或新增 Protected Phrase。
- **内容碰撞**（比亚迪海豹的"electric"碰撞等）：未修改目录内容。

## 14. Readiness for Replay

**READY_FOR_REPLAY** — 定向测试、全量单元测试、TypeScript、Production Build 全部通过；Piggyback 修复有直接、真实数据支撑的单元测试覆盖（Q10/Q40/Q42 机制 fixture）；未破坏 Prompt 2/2B/2C 已验证的合法行为。据此进入固定 Deterministic Replay。
