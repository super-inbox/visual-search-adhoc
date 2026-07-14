# Stage 7 Prompt 2C Guard Implementation

## 1. Executive Summary

Prompt 3B 真实 Live Smoke（20 Query / 23 Run）暴露了 Prompt 2B 未覆盖的三类问题：(A) 弱数字属性（如 `4k`）被 Guard R2 的独立锚点规则误判为足够强的锚点，导致 Q06 的候选 `Genshin Impact fanart 4k` 未绑定回 subject `Furina`，Count 从 Replay 验证的 12 反弹到 Live 实测的 1567；(B) `decomposition.subject` 字段本身从未被校验，只要非空字符串就被无条件信任，导致 Q10/Q40/Q41/Q44 等多个真实 Query 的 subject 丢弃了原始平台/实体（如"小红书"退化为"graphic note"/"store review"），其余 slot 即使正确绑定到这个已经漂移的 subject 也无法挽回；(C) `evaluateRewriteCandidate` 中"候选与原 Query 语言不同就无条件放行"的规则被 Q12 证实过宽——跨语言不等于语义等价。

本阶段实现：

- **Guard N**：新增 `isWeakNumericAttribute`/`isStrongIdentifierToken`，将"数字锚点"拆分为弱数字属性（4k/1080p/60fps/120hz/年份/尺寸/百分比/纯数字，均不可单独作为锚点）与强标识符（字母数字混排且不属于弱属性形状，如 es6/GPT-4/a7r5/rtx4090），仅强标识符可通过 Option C 独立锚点判定，弱数字属性被排除。
- **Guard S**：新增 `evaluateSubjectCandidate`，复用与 `evaluateRewriteCandidate` 完全相同的判定结构（Options A/B/C/D/E），在 subject 被信任前先对其做锚点校验；不安全 subject 优先绑定回原 Query 提取出的可靠锚点（`extractOriginalAnchorPhrase`），无法绑定时整个 subject 被拒绝，其依赖的所有非 subject slot 随之全部拒绝，不再猜测执行。
- **跨语言规则修复**：移除 `evaluateRewriteCandidate` 中"语言不同即放行"的 Option E 旧逻辑，替换为"跨语言候选且无 subject 时，尝试绑定到原 Query 提取锚点，绑定失败才拒绝（`CROSS_LANGUAGE_WITHOUT_ANCHOR`）"；同语言无锚点候选的既有拒绝行为（Prompt 2B 已验证正确）保持不变，未被本次改动波及。
- **测试**：新增 40 条 Prompt 2C 定向测试（Guard N 12 条、Guard S 14 条、跨语言 6 条、Cache 5 条、外加对既有 6 条因行为变化而更新的测试），全量单元测试 335/335 通过，`tsc --noEmit` 0 错误，Production Build 通过。
- **Replay/Live 复验**：详见后续报告 `STAGE7_PROMPT2C_REPLAY_SUMMARY_2026-07-14_zh.md` 和 `STAGE7_PROMPT2C_LIMITED_LIVE_RETEST_2026-07-14_zh.md`。

## 2. Prompt 3B Failure Analysis

严格逐条复核 Prompt 3B 的 Live Results / Human Review / Manifest（未直接照抄旧总结）：

| Case | Raw LLM 关键字段 | 主要错误路径 | 分类 | 本阶段是否修复 |
|---|---|---|---|---|
| Q06 | `rewrites: ["...","Genshin Impact fanart 4k","..."]`, `decomposition.subject="Furina"` | 候选丢弃 "Furina"，仅靠 "4k" 通过 Option C 独立锚点判定，未绑定 | WEAK_NUMERIC_ANCHOR | 是（Guard N） |
| Q10 | `decomposition.subject="Light and Night"` | subject 分词后退化为通用词 "light"/"night"，Top 结果被 "la land"/"night routine" 等无关内容淹没 | UNANCHORED_SUBJECT | 是（Guard S，见第 9 节局限说明） |
| Q40 Run1/2 | `decomposition.subject="graphic note"` | subject 完全丢弃"小红书"平台实体 | UNANCHORED_SUBJECT | 是（Guard S） |
| Q41 | `decomposition.subject="Xiaohongshu"`（保留但过于通用，是模板受众文案中常见的样板词） | subject 未丢实体但本身不具区分度 | UNANCHORED_SUBJECT（弱） | 部分（Guard S 无法制造出比原 Query 更强的判别力，见第 12 节 Deferred） |
| Q42 D | 无 subject，仅 style/output | 绑定的 `cover` 依赖过宽的跨语言无约束候选 | CROSS_LANGUAGE_WITHOUT_ANCHOR | 是（跨语言规则修复） |
| Q44 | `decomposition.subject="store review"` | subject 丢弃"小红书"，Top 结果为 ESL 语言卡片 | UNANCHORED_SUBJECT | 是（Guard S） |
| Q47 | `decomposition.subject="product card"`，绑定候选贡献有限 | subject 本身与"抖音"平台无关联，且已锚定候选主导洪泛 | UNANCHORED_SUBJECT + MERGE_OR_RANKING | 部分（Guard S 修复 subject，Merge 权重问题记录不修） |
| Q48 | 类似 Q47 | subject "Douyin influencer" 部分保留平台名，绑定候选贡献有限 | GENERIC_BOUND_PATH + MERGE_OR_RANKING | 部分 |
| Q12 | 无 subject，跨语言候选无条件放行 | Guard R2 旧逻辑允许缺乏证据的跨语言候选直接执行 | CROSS_LANGUAGE_WITHOUT_ANCHOR | 是（跨语言规则修复） |
| 比亚迪海豹 | 无实体漂移，"electric" 词碰撞 | 与 Guard 无关，纯目录内容碰撞 | CONTENT_COLLISION | 否（本阶段禁止修改目录/Ranking，记录见第 12 节） |
| 乔丹鞋 | "Jordan" 多义碰撞（国家/球星/品牌） | 与 Guard 无关 | AMBIGUOUS_QUERY | 否（同上） |

## 3. Weak Numeric Anchor Root Cause

`hasIndependentAnchor`（Guard R2 Option C）原判定为 `(hasCJK(t) && t.length>=2) || /\d/.test(t)`——任何含数字的 token 均被视为独立锚点。这个规则的本意是保护 "es6"/"mate60pro" 这类型号，但代价是 "4k"/"1080p"/"2024" 等纯属性描述词也会被误判为"足够独特，可以不受任何上下文约束"。Q06 的真实 Live 数据（`Genshin Impact fanart 4k`）直接证实了这个漏洞：候选丢弃了 subject "Furina"，仅凭 "4k" 就被判定为安全，未被绑定，导致其在 Union 合并中重新引入接近原始洪泛水平的结果（1567，对比 Replay 固定输入下验证有效的 12）。

## 4. Strong Identifier vs Weak Numeric Attribute

- **弱数字属性**（`isWeakNumericAttribute`）：纯数字（年份/数量/任意计数）、`\d+(k|p|fps|hz|px|cm|mm|kg|g|lb|min|sec|s)` 形状（分辨率/帧率/刷新率/尺寸单位）、`\d+x\d+`（分辨率维度）、`\d+%`（百分比）。这些模式均不能单独证明 Rewrite 保留了原 Query 的实体。
- **强标识符**（`isStrongIdentifierToken`）：token 内同时含字母和数字、且不匹配弱数字属性形状——`es6`、`gpt-4`、`a7r5`、`mate60pro`、`cs421`、`rtx4090` 均属此类，可作为 Option C 独立锚点。
- **空格分隔型号**（`iPhone 15`、`RTX 4090`、`Model 3`）：本阶段刻意不在 Option C 中做"紧邻词对"猜测（该做法要求判断紧邻的字母 token 是否为专有名词，与已被放弃的大小写启发式同样脆弱——"Genshin Impact"同样是紧邻的大写字母+专有名词形态，但需要绑定，误伤风险高）。这类型号依然被安全支持：只要原 Query 与候选**共同**出现该型号（Option A 共享锚点，本阶段未改动），就会被接受，测试用例已验证 `iPhone 15 case design`→`iPhone 15 poster`、`RTX 4090 benchmark review`→`RTX 4090 comparison chart`、`Tesla Model 3 interior`→`Model 3 dashboard poster` 均正确通过。

## 5. Decomposition Subject Validation

`evaluateSubjectCandidate` 复用与 `evaluateRewriteCandidate` 相同的判定顺序：

1. **Empty-token fail closed**：subject 分词后无 executable token 或 alias group 时拒绝（`EMPTY_EXECUTABLE_TOKENS`）——修复了"the"这类停用词 subject 此前完全依赖下游 Guard 1 兜底的设计缺口，现在在 subject 校验阶段本身就能拦截。
2. **Option A/B**：subject 与原 Query 共享字面 token，或与原 Query 存在 Alias/Protected Phrase 等价，或（本阶段新增）与原 Query 存在"空格折叠后互为子串"的等价关系（修复 `bydSeal`↔`BYD Seal` 这类大小写/空格差异导致的误判）。
3. **Option C**：subject 自身携带独立强锚点（真实字典分词后仍整体保留的 CJK 复合词，或强标识符 token）——这正是 `乔丹鞋→篮球鞋` 继续通过的机制，也验证通过两个全新样例（`汉服马面裙→传统服饰`、`故障艺术风格海报→抽象设计`）。
4. **Option D**：以上均不满足时，绑定到 `extractOriginalAnchorPhrase(original)` 提取出的可靠锚点（CJK Protected Phrase 优先，其次 Alias 规则短语，最后原 Query 分词后的第一个真实 token）——绝不拼接整句原 Query。真实修复：`小红书图文笔记模板 数字标题` 的 subject `graphic note` 被绑定为 `小红书 graphic note`，后续所有 slot（含 rewrites[]）均继承这个更严格的锚点。
5. **Option E**：无法绑定（原 Query 本身也不产生任何 token，如全停用词查询）时拒绝（`UNANCHORED_DECOMPOSITION_SUBJECT`），其依赖的所有非 subject slot 同步拒绝为 `UNBOUND_NON_SUBJECT_SLOT`，不允许任何 modifier 单独执行。

## 6. Cross-language Safety Change

`evaluateRewriteCandidate` 原 Option E 末尾的 `if (hasCJK(original) !== hasCJK(candidate)) return 接受不改动` 已删除。新逻辑：跨语言候选在 Option A/B/C 均未命中、且无 decomposition subject 可绑定时，尝试绑定到 `extractOriginalAnchorPhrase(original)`；绑定成功则接受（Q12 的三条候选均被绑定为 `松弛 relaxed lifestyle illustration` 等，不再无条件放行）；绑定失败（原 Query 本身无可提取锚点）才拒绝，标记 `CROSS_LANGUAGE_WITHOUT_ANCHOR`。

**重要边界确认**：此修复只影响"无 subject 的跨语言候选"。Prompt 2B 已验证正确的"同语言无锚点候选直接拒绝"路径完全未被触碰（测试回归确认）。合法跨语言场景（Alias 等价、Protected Phrase 等价、共享型号/品牌）均通过既有 Option A/B 机制不受影响地继续工作，测试覆盖了 `手冲咖啡→brand identity`（Alias）、`二手奢侈品→pre-owned luxury`（Protected Phrase，绑定）、`蔚来es6→nio es6 interior`（共享型号）。

## 7. Diagnostics

`RejectedSlot.reason` 扩展为：`"UNBOUND_NON_SUBJECT_SLOT" | "EMPTY_EXECUTABLE_TOKENS" | "UNANCHORED_REWRITE_CANDIDATE" | "WEAK_NUMERIC_ONLY_ANCHOR" | "UNANCHORED_DECOMPOSITION_SUBJECT" | "CROSS_LANGUAGE_WITHOUT_ANCHOR"`。`RewriteCandidateEvaluation`/新增的 `SubjectCandidateEvaluation` 均包含 `weakNumericAttributes`/`strongIdentifiers` 字段，暴露每个候选/subject 被判定时具体命中了哪些弱数字属性、哪些强标识符，Harness 可直接读取，全部 JSON-serializable，不含 Secret。`FlattenedPath.subjectBound` 语义再次扩展：现在也覆盖"被 Guard S 绑定的 subject 自身路径"和"绑定到 Guard S 校验后 effectiveSubject 的下游候选"。

## 8. Cache Semantics

`getMultiQueryPaths` 的 `hasExecutablePath = flattenPathsWithDiagnostics(trimmed, out).executed.length > 0` 未改动一行代码。由于该函数内部现在会依次调用 Guard S（subject 校验）与更新后的 Guard R2（含 Guard N 数字判定与新跨语言规则），Cache 分类自动、正确地反映全部新增判定：弱数字候选被拒绝、不安全 subject 被拒绝或绑定、跨语言无锚点候选被拒绝或绑定，均通过 5 条新增 Cache 测试验证（10 分钟 Negative / 7 天 Success 两档，覆盖"全部拒绝"、"不安全 subject 但独立锚定的 rewrite 存活"、"安全 subject 但空 token rewrite 被拒绝"等组合）。

## 9. Modified Files

- `lib/searchRewrite.ts`：新增 `isWeakNumericAttribute`、`isStrongIdentifierToken`、`extractOriginalAnchorPhrase`、`sharesCollapsedForm`、`evaluateSubjectCandidate`/`SubjectCandidateEvaluation`；修改 `hasIndependentAnchor`（排除弱数字属性）、`evaluateRewriteCandidate`（新增 weakNumericAttributes/strongIdentifiers 字段、移除跨语言无条件放行、新增 Option D2 原锚点绑定回退）、`flattenPathsWithDiagnostics`（先校验 subject 再用于后续绑定）、`RejectedSlot`/`RewriteCandidateEvaluation` 类型扩展。**未改动** `flattenPaths`、`getMultiQueryPaths` 的候选净化与 Cache 写入本身、Guard 1（page.tsx scoreBlob）、Merge/Ranking 逻辑。
- `lib/__tests__/searchRewrite.test.ts`：更新 6 条因跨语言规则修复而行为改变的既有测试（"stopword-only subject"、"never includes the original query"内的标点测试、Guard 2 rewrites 段落测试、Q47/Q12 场景测试），新增 40 条 Prompt 2C 定向测试。
- `app/[locale]/(public)/search/page.tsx`：**本阶段无需修改**——page.tsx 的诊断日志行已在 Prompt 2B 改为 `errorType=${r.reason}`，自动兼容本阶段新增的 3 个 reason 枚举值；候选执行循环对所有 `slotKey`（含 `subject`）一视同仁地跑 `buildSearchTokens`/`hasExecutableConstraint`，无需为 Guard S 的 bound subject 文本做任何特殊处理。

## 10. Tests

| 命令 | 结果 |
|---|---|
| `npx vitest run --config vitest.unit.config.ts lib/__tests__/searchRewrite.test.ts` | 139/139 通过（99 既有 + 40 新增） |
| `npx vitest run --config vitest.unit.config.ts`（全量） | 335/335 通过（Prompt 2B 基线 295） |

新增覆盖：Guard N 弱数字属性 6 组（4k/8k、1080p/720p、60fps/120hz、年份、尺寸百分比、分辨率维度+纯数字）+ Q06 机制 fixture 2 条 + 弱数字与真实实体共存 1 条；强标识符 4 组（ES6/GPT-4/CS421、混合型号、共享完整型号、空格分隔型号）；Guard S 安全 subject 6 条（含 2 个全新零重叠泛化）、不安全 subject 绑定 6 条（含真实 Q40/Q47/Q42 场景）、无法绑定拒绝 3 条；跨语言安全 6 条（Alias/Protected Phrase/共享型号/真实 Q12 场景/subject 兜底/真正无锚点拒绝）；Cache 5 条。

## 11. TypeScript and Build

- `npx tsc --noEmit`：0 错误。
- `npm run build`：exit 0，成功。构建日志中的 `INVALID_MESSAGE` 错误均来自 `blog/[slug]/page.js`（Blog i18n 既有问题），与本次搜索改动无关，未新增、未加剧。
- Lint：与 Prompt 2B 相同的 ESLint 9 flat-config 预存问题（`next/core-web-vitals` 与 `typescript-eslint` 的 `config()` 助手不兼容），未修复（不在本阶段范围）。

## 12. Deferred Issues

以下问题明确记录，本阶段不修改：

- **Q47/Q48 Merge/Ranking 问题**：Guard S 已正确校验 subject（"product card"/"Douyin influencer" 本身是否与原 Query 关联），但即使 subject 被正确处理，其余已锚定候选与 subject 路径贡献的通用结果依然主导洪泛——这是 Union Merge 阶段对多路径贡献度不做区分（仅 +8%/命中的轻微加权）的固有限制，需要 Ranking/Merge 重新设计才能根本解决，超出本阶段范围。
- **Q42 D 的独立 generic bound path**：无 subject 时，Guard S 无法作用（没有 subject 可校验），跨语言修复后候选会绑定到原 Query 提取的锚点，但如果提取到的锚点本身信息量不足（如仅提取到一个宽泛的分词结果），仍可能残留较宽结果集，记录为后续候选改进方向。
- **比亚迪海豹"electric"词碰撞、乔丹鞋"Jordan"多义碰撞**：均为目录内容/Taxonomy 层面的碰撞，与 Guard 逻辑无关，本阶段禁止修改目录数据和 Ranking，仅记录。
- **目录级 IDF、动态词频基础设施、Candidate Top N 截断、Ranking 重写、Merge 权重调整**：本阶段明确禁止实施，未触碰。

## 13. Limitations

- Guard S 的"绑定回原 Query 锚点"是**保守但非完美**的修复：对 Q41（`小红书对比图 use前后`）这类原 subject 已经保留实体但实体本身在目录中过于通用（"小红书"在大量模板审美描述中都会出现）的情况，Guard S 无能为力——它只能确保 subject 与原 Query 有真实关联，不能进一步判断这个关联词在目录中是否具有区分度（这需要类似 IDF 的机制，本阶段明确禁止）。
- `extractOriginalAnchorPhrase` 取原 Query 分词后的"第一个"非停用词 token 作为兜底锚点，是一个确定性但简化的启发式，不保证总是语义上"最核心"的词。
- Guard N 的强标识符判定不处理空格分隔的型号（`iPhone 15`）作为**独立**锚点（无原 Query 佐证时）——这是刻意的保守选择（避免复活已被否定的大小写启发式），意味着如果 LLM 提出一个原 Query 完全未提及的空格分隔型号，该候选仍需绑定或拒绝，不会被无条件信任。
- 尚未运行完整 68 条权威 Query 集。
- Live Retest（若 Replay 通过 Gate）仍存在 LLM 非确定性、目录漂移、Human review 为 Claude 结构化审核（非用户本人）等既有限制。

## 14. Readiness for Replay

**READY_FOR_REPLAY** — 全部单元测试、TypeScript、Production Build 通过；Guard N/S/跨语言修复均有直接单元测试覆盖，包括真实 Q06/Q10/Q12/Q40/Q42/Q47 场景 fixture；未破坏 Prompt 2/2B 已验证的合法行为（乔丹鞋泛化、Alias OR-group、Protected Phrase、CJK/英文/混合 Query 全部回归通过）。据此进入固定 Deterministic Replay（见 `STAGE7_PROMPT2C_REPLAY_SUMMARY_2026-07-14_zh.md`）。
