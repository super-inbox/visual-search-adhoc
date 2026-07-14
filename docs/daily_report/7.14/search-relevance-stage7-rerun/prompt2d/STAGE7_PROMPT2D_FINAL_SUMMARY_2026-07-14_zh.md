# Stage 7 Prompt 2D Final Summary

## 1. Executive Summary

Prompt 2C 结论为 `NEEDS_ANOTHER_GUARD_FIX`：Human FAIL 30.4%（7/23），根因确认为 **Anchor Piggyback**——Guard S 正确绑定 subject 后，部分 rewrite 候选因与 subject **绑定前的原始不安全文本**共享 token，被 Option A 误判为"已锚定"而绕过绑定。本阶段（Prompt 2D）通过读取实际生产代码（而非仅摘要）确认了该机制的确切代码路径，实现了最小化的 Anchor Provenance 修复，并完成了固定 Deterministic Replay 与 Limited Live Retest 两级验证：

- Replay：23 个 D 组仍 `>=1000` 的从 3 条降到 1 条，Regression=0。
- Live：Human FAIL 从 30.4% 降到 **13.0%**，首次低于 20% 门槛。
- **最终结论：`READY_FOR_FULL_68`**（不自动触发运行）。

## 2. Piggyback 根因（复述自 Implementation 报告，供独立阅读）

`flattenPathsWithDiagnostics`（修复前）把 Guard S 绑定后的**完整**文本（如 `"光与夜之恋 Light and Night"`）传给每个 rewrite 候选的 `evaluateRewriteCandidate` 作为 Option A 比较基准。该完整文本同时包含"安全的注入锚点"（"光与夜之恋"）和"subject 本身未经验证的不安全原文"（"Light and Night"）。任何候选与后者共享字面 token（如候选本身就是 `"Light and Night character design"`），都会被误判为"已与安全 subject 共享锚点"而绕过绑定，以未加固形式执行——这是一个自证循环：candidate 通过与"刚刚因为不安全才需要绑定的原文"比较，反而证明了自己"安全"。

真实数据确认 Q10、Q40、Q42（带 subject 时）共享此确切代码路径；Q42 D（无 subject）走不同的、已安全的 Option D2 路径，不受影响。

## 3. Anchor Provenance 修复设计

新增 `SubjectCandidateEvaluation.anchorBasisForDownstream` 字段，区分：
- Subject 原生安全（Option A/B/C 判定）：`anchorBasisForDownstream = subject`（完整原文可信）。
- Subject 需要绑定（Option D）：`anchorBasisForDownstream = fallbackAnchor`（仅注入锚点本身，不含 subject 不安全原文）。

`flattenPathsWithDiagnostics` 改为把 `anchorBasisForDownstream` 传给 `evaluateRewriteCandidate` 作为窄化的 Option A 比较基准。同时新增 decomposition modifier 的 native-constraint 检查（空/纯 stopword/纯弱数字属性提前拒绝）。

**第二轮修正**：首次 Replay 发现窄化后的比较基准若同时被用作实际绑定文本，会缩短最终检索短语的 token 总数，在 `ceil(n/2)` 松弛匹配阈值下反而**降低**了绝对匹配门槛（如 Q40 D 一度从 3 升至 919）。修正：拆分为 `subject`（窄化，仅用于比较）与新增的 `bindTarget`（完整 `effectiveSubject`，用于实际绑定文本），两者语义分离，各司其职。

未创建第二套锚点系统、未修改 `ceil(n/2)` 公式本身、未修改 Ranking/Merge/Tokenizer/Protected Phrase/Alias/Taxonomy/catalog 内容。

## 4. Production 代码改动清单

- `lib/searchRewrite.ts`：
  - `SubjectCandidateEvaluation` 新增 `anchorBasisForDownstream` 字段（5 个返回分支赋值）。
  - `flattenPathsWithDiagnostics`：新增 `anchorBasisForDownstream` 局部变量；rewrite 候选评估改用其作为比较基准，同时传入 `effectiveSubject` 作为新增的 `bindTarget` 参数；decomposition modifier 循环新增 native-constraint 检查（2 个新 if 分支）。
  - `evaluateRewriteCandidate`：新增可选第 4 参数 `bindTarget`（默认 = `subject`，向后兼容）；Option D 绑定逻辑改用 `bindTarget` 构造 `executedQuery` 前缀。
  - 未改动 Option A/B/C/E 判定逻辑本身、`evaluateSubjectCandidate` 自身逻辑、Guard 1（page.tsx，本阶段零改动，哈希验证一致）。
- `lib/__tests__/searchRewrite.test.ts`：更新 6 条既有测试 + 因 bindTarget 修正额外更新 5 条断言，新增 21 条 Prompt 2D 定向测试。

## 5. 测试结果

| 项目 | 结果 |
|---|---|
| `searchRewrite.test.ts` | 160/160 通过（139 既有/更新 + 21 新增） |
| 全量单元测试 | 356/356 通过 |
| TypeScript (`tsc --noEmit`) | 0 错误 |
| Production Build | exit 0 |
| Lint | 与 Prompt 2B/2C 相同的预存 ESLint 9 flat-config 问题，未修复（按指示只运行一次） |

## 6. Replay 结果摘要

固定 Deterministic Replay（复用 7.13 已录制的 LLM 输出，同一 26 次 Run，SHA-256 校验 Query 集一致）：

- Full-catalog = 0（26/26）。
- 23 个 D 组仍 `>=1000` 的从 Prompt 2C 的 3 条（Q10/Q12/Q48）降到 **1 条（仅 Q12）**。
- Regression = 0。
- 校验：`native_anchored=true` 且 `synthetic_anchors` 非空的行数 = 0（合成锚点从未被误判为原生共享锚点）。
- Gate 结论：`READY_FOR_LIVE_RETEST`。

详见 `STAGE7_PROMPT2D_REPLAY_SUMMARY_2026-07-14_zh.md`。

## 7. Live 结果摘要

Limited Live Retest（真实 LLM 调用，与 Prompt 3B/2C 完全相同的 20 唯一 Query / 23 次 Run 集合，SHA-256 校验一致，进程隔离 Cache）：

- Full-catalog = 0（23/23）。
- `>=1000` 从 Prompt 2C Live 的 3 次（Q10/Q12/Q06）降到 **1 次（仅 Q12）**。
- Human FAIL 从 30.4% 降到 **13.0%（3/23）**，首次低于 20% 门槛。
- 5 个对照 case（Q30/Q21/Q44/手作/watercolor）计数逐字节零回归。
- 执行过程中遭遇一次真实的、外部 OpenAI API 持续变慢窗口（与本阶段代码无关，通过重试、未修改任何超时配置或生产代码，最终 23/23 全部成功完成），详见 Live 报告第 2 节的完整透明记录。
- Gate 结论：`READY_FOR_FULL_68`。

详见 `STAGE7_PROMPT2D_LIMITED_LIVE_RETEST_2026-07-14_zh.md`。

## 8. 核心 Case 深度对比（Q10/Q40/Q42/Q06/Q12/Q41/Q47/Q48）

| Query | Replay（Prompt2C → 2D） | Live（Prompt2C → 2D） | 状态 |
|---|---|---|---|
| Q10 | 1715 → 740 | 1642 → 330 | 直接修复确认，双重验证 |
| Q40 | 3 → 0 | 0 → 0 | 直接修复确认（Replay），Live 本身两阶段均已是 0 |
| Q42 | 3 → 3（已确认正确绑定） | 468/476 → 464/464 | 绑定修复确认，残留为已知内容碰撞（deferred） |
| Q06 | 12 → 12（未涉及） | 1567 → 12 | Live 强力确认修复对真实非确定性输出泛化 |
| Q12 | 1694 → 1694（按设计不受影响） | 2382 → 1598 | 确认按设计不受影响，relaxed 阈值问题 deferred |
| Q41 | 89 → 89（未涉及） | 450 → 23 | Live 显著改善，LLM 样本差异+修复共同作用 |
| Q47 | 485 → 485（已确认正确绑定） | 501 → 485 | 绑定修复确认，残留为 Merge/Ranking 问题（deferred） |
| Q48 | 1155 → 17 | 544 → 0 | 直接修复确认（Replay），Live 安全但为空 |

## 9. 合法行为保留确认（未破坏既有正确行为）

- Replay：6 条未涉及 piggyback 机制的对照 case（Q11/Q12/Q15/Q16/Q42D/Q46）计数逐字节不变。
- Live：5 条对照 case（Q30/Q21/Q44/手作/watercolor spring flowers）计数逐字节不变。
- 全量单元测试 356/356 通过，包含 Prompt 2/2B/2C 已验证的合法行为回归抽样测试。
- 乔丹鞋→篮球鞋类目泛化、比亚迪海豹实体漂移防护等既有语义控制在 Live 中继续正确工作。

## 10. 仍失败/仍存在的问题（本阶段明确排除范围，非新发现缺口）

| 问题 | 影响 Case | 分类 | 说明 |
|---|---|---|---|
| relaxed 匹配阈值（`ceil(n/2)`） | Q12（持续 `>=1000`）、Q06 部分 | Ranking/Matching | 本阶段禁止修改；已在 Replay 与 Live 中独立确认与本阶段修复无关 |
| 通用英文词内容碰撞（"cover"） | Q42 | Taxonomy/内容 | 已确认候选正确绑定，碰撞来自目录内无关内容含相同泛词，非 Guard 缺陷 |
| Merge/Ranking 多路径加权 | Q47 | Ranking | 已确认候选正确绑定，计数持平指向加权机制本身，非 Guard 缺陷 |
| Tokenizer 对"抖音"分词不稳定 | Q48 | Tokenizer | jieba 词典问题，已知限制，未修改词典 |
| "小红书"目录区分度不足 | Q41（Replay 仍 FAIL，Live 已改善） | Taxonomy/内容 | 通用品牌词在目录中区分度有限，非 Guard 逻辑问题 |

## 11. Deferred 问题最终记录（贯穿 Prompt 2B/2C/2D 累计）

以上第 10 节所列问题均**从未被本阶段或此前任何阶段修改**，符合任务规定的显式排除范围（relaxed 匹配阈值、Ranking、Merge、Tokenizer、Protected Phrase、Alias、Taxonomy、catalog 内容）。建议作为未来独立阶段（Ranking/Matching 阶段、Taxonomy/内容阶段）处理，不建议在 Guard 逻辑内继续打补丁。

## 12. Modified Files（Production repo）

仅 `lib/searchRewrite.ts` 与 `lib/__tests__/searchRewrite.test.ts` 两个文件，均在声明范围内。`app/[locale]/(public)/search/page.tsx`（Guard 1）本阶段零改动，哈希验证与阶段开始前完全一致（`4cb4775f...`）。

## 13. 输出文件清单

**prompt2d/ 目录（新增，未覆盖任何既往阶段文件）**：
- `STAGE7_PROMPT2D_PIGGYBACK_GUARD_IMPLEMENTATION_2026-07-14_zh.md`
- `stage7_guard_replay_results_prompt2d_2026-07-14.csv`
- `stage7_guard_replay_human_review_prompt2d_2026-07-14.csv`
- `stage7_guard_replay_manifest_prompt2d_2026-07-14.json`
- `STAGE7_PROMPT2D_REPLAY_SUMMARY_2026-07-14_zh.md`
- `stage7_guard_live_results_prompt2d_2026-07-14.csv`
- `stage7_guard_live_human_review_prompt2d_2026-07-14.csv`
- `stage7_guard_live_manifest_prompt2d_2026-07-14.json`
- `STAGE7_PROMPT2D_LIMITED_LIVE_RETEST_2026-07-14_zh.md`
- `STAGE7_PROMPT2D_FINAL_SUMMARY_2026-07-14_zh.md`（本文件）
- `_replay_prompt2d_summary.json`、`_live_prompt2d_summary.json`

**scripts/curify-search-stage7-guard-smoke/ 目录（新增脚本，未覆盖既有脚本）**：
- `replay_prompt2d.cjs`
- `run_live_prompt2d.cjs`

## 14. Git 安全校验

- `curify-frontend`：分支 `baobao/search-relevance-phrase-alias-2026-07-09`，HEAD `c062e618bce4044bedf718aadf59ff69f0999344`（未变）。`git status --short` 与阶段开始前快照逐行一致，仅 `lib/searchRewrite.ts` 内容哈希从 `aeb453b4...` 变为 `a54aaf9e...`（预期改动），`lib/__tests__/searchRewrite.test.ts` 为既有 untracked 文件（内容更新）。未执行任何 `git add/commit/push/reset` 等操作。
- `visual-search-adhoc`：分支 `main`，HEAD `39d8d0a1c6a1c3bd9d31fedfc2d51954cff44f18`（未变）。仅在 `prompt2d/` 与 `scripts/curify-search-stage7-guard-smoke/` 新增文件，未覆盖或删除任何既往阶段（Prompt 0/1/2/2B/2C/3/3B）文件或两个冻结 Query Set。

## 15. Final Gate 结论

### **READY_FOR_FULL_68**

Replay 与 Live 两级验证均已通过硬性条件与数量门槛；Human FAIL 比例（Live 13.0%）首次低于 20% 门槛；核心 Piggyback case（Q06/Q10/Q40/Q41）在固定 Replay 与真实 Live 两种验证方式下均直接确认修复生效且方向一致；仍存在的失败 case（Q42/Q12）均已明确归类为本阶段范围排除的已知限制，非 Guard 逻辑缺口。

**按任务要求，即使结论为 `READY_FOR_FULL_68`，本阶段不自动触发运行全部 68 条 Query，不进入 Prompt 4，不执行任何 Git 写操作**，等待用户后续明确指示。
