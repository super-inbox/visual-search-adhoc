# Stage 7 Rewrite Array Guard Implementation

## 1. Executive Summary

- **原问题**：Prompt 3 Deterministic Replay 发现 23 个 D 组洪泛 Case 中有 5 个（Q06、Q10、Q12、Q47、Q48）在 Guard 1（Empty Tokens）+ Guard 2（Subject-bound Decomposition）之后仍 `>=1000`。根因确认：`flattenPathsWithDiagnostics` 中 `paths.rewrites`（LLM 自由文本改写数组）从未受任何 Guard 约束，只要非空即无条件执行（`for (const r of paths.rewrites) pushExecuted(r, "rewrite", r, false)`），成为残留洪泛的主要来源。
- **实现内容**：在 `lib/searchRewrite.ts` 新增 Guard R（`evaluateRewriteCandidate`），对每个 `rewrites[]` 候选做锚点校验：
  - **Guard R1**：候选经归一化/分词/停用词过滤/CJK 分词/Alias 处理后若无任何 executable token 或 alias group，直接拒绝（`EMPTY_EXECUTABLE_TOKENS`）。
  - **Guard R2**：候选必须满足以下之一才可不受约束地执行：(A) 与 decomposition subject 共享字面 token；(B) 与原始 Query 共享 `PHRASE_ALIAS_RULES` 定义的 Protected Phrase / Alias 等价关系；(C) 候选自身携带独立锚点（真实字典分词后仍保持整体的 CJK 复合词，或含数字的 ASCII token）。若均不满足但存在 subject，则绑定到 subject（`<subject> <candidate>`）而非直接拒绝；若无 subject 且候选与原 Query 跨语言（合法翻译场景），仍放行；若无 subject 且同语言仍无锚点，拒绝（`UNANCHORED_REWRITE_CANDIDATE`）。
  - Guard 2（decomposition 绑定）逻辑完全未改动，仅调整了代码顺序（先算 subject 供 rewrites 循环使用）。
  - `page.tsx` 仅改动 1 行日志（`errorType=UNBOUND_NON_SUBJECT_SLOT` 硬编码 → `errorType=${r.reason}`，因为 rejected 数组现在也承载 Guard R 的新拒绝原因）。
- **测试结果**：新增 39 条 Guard R 定向测试（含 Q06/Q10/Q12/Q47 真实场景 fixture、乔丹鞋→篮球鞋等 3 个合理泛化样例、比亚迪海豹/白箱 2 个实体漂移样例、Alias/Protected Phrase/CJK/Cache 回归测试），`lib/__tests__/searchRewrite.test.ts` 99/99 通过；全量单元测试 295/295 通过（Prompt 2 基线 260）；`tsc --noEmit` 0 错误；Production Build 通过。
- **Replay 是否可重新运行**：是，已完成（见同目录 `STAGE7_PROMPT2B_REPLAY_SUMMARY_2026-07-14_zh.md`）。23 个 D 组洪泛 Case 中，相对 Stage 7 原始基线，改善比例从 Prompt 3 的 78.3%（18/23）提升到 **82.6%（19/23）**，达到 80% 门槛；Full-catalog 保持 0；Q39/Q40/Q42 均未恢复 full-catalog（Q39 D: 1→0，Q40 D: 922→3，Q42 D/C: 843→843 / 468→254）；0 个 regression。

## 2. Replay Harness Audit

在修改 production 前先审计了 `scripts/curify-search-stage7-guard-smoke/`：

- **`build_bundle.cjs`**：使用 curify-frontend 自身的 esbuild，真实打包（非复制）当前 `lib/searchRewrite.ts`（含 `flattenPathsWithDiagnostics`、`getMultiQueryPaths`）、`lib/query_phrase_aliases.ts`、`lib/cjk_tokenizer.ts`、`lib/zh_normalize.ts`、`lib/topic_resolver.ts`，产物为 `_bundle_current.cjs`，并记录各源文件 SHA-256 到 `_bundle_source_hashes.json`。
- **`engine.cjs`**：`bundle.flattenPathsWithDiagnostics(query, multi)` 直接调用真实导入的函数（第 184 行左右），Guard 2 的核心逻辑因此是真实 production 代码，不是复制。
- **`scoring.cjs`**：page.tsx 是 Next.js Server Component，无法在 harness 中 `require()`，因此 `buildSearchTokens`/`scoreBlob`/`hasExecutableConstraint` 是**逐字转录**（非重新实现），并配有 `verifyAgainstLiveSource()` 漂移检测器：每次运行前读取当前 `page.tsx`，断言 8 个关键代码片段字面存在，任一缺失即拒绝运行。这与仓库既有的 `scripts/curify-search-collect-stage7/run_mode.cjs` 采用同一套定式做法，是有据可查、有防护的折衷，不是掩盖问题。
- **结论：Harness 有效，无需因"未使用真实逻辑"而修复**（满足 Prompt 2B 第 5.1 节的可接受条件：核心 Guard/path-planning 来自当前 production 代码构建/导入；Scoring 使用当前代码的可信转录产物；production 修改后可重新 build；不使用旧缓存 bundle；Manifest 记录 source hash）。

**本阶段对 Harness 做了 1 处必要同步（非逻辑修复）**：`page.tsx` 的诊断日志行从硬编码 `errorType=UNBOUND_NON_SUBJECT_SLOT` 改为 `errorType=${r.reason}`（因为 `rejected[]` 现在也承载 Guard R 的新拒绝原因），导致 `scoring.cjs` 漂移检测器原先检查的字面子串不再存在于 `page.tsx` 中。这是对**我自己做出的、已手工核实的 production 改动**的检测器模式同步更新，不是"绕过检测器掩盖不一致"——`UNBOUND_NON_SUBJECT_SLOT` 本身作为 Guard 2 的拒绝原因未变。更新后重新运行 `verifyAgainstLiveSource()` 通过（`missing: 0`）。除此之外未修改 Harness 任何逻辑；`build_bundle.cjs`/`engine.cjs`/`replay.cjs`/`csv_utils.cjs` 原样未动。

Replay 前重新执行了 `node build_bundle.cjs`，`_bundle_source_hashes.json` 中 `lib/searchRewrite.ts` 的哈希从 Prompt 3 时的
`52c5a066628e0295323fc7c4b026106e199512acd6b03df8247da2254936209e`
变为本次
`bf2160d5f0f0300b4be4947a19b2f34ef63063fc1b3f2e742ebff571e3d24ec5`，
确认 Bundle 已使用当前 Prompt 2B 代码，未使用旧缓存。

## 3. Five Remaining Flood Cases

逐条分析（详见 `stage7_guard_replay_results_prompt2b_2026-07-14.csv` 与人工复核 CSV）：

| Query | Rewrite candidates（真实 7.13 记录） | 洪泛候选 | 原因 | 新 Guard 行为 | 新 Count |
|---|---|---|---|---|---|
| **Q06** | "Genshin Impact Furina wallpaper" / "Furina fanart poster" / "Genshin Impact character art" | 第 3 条（丢弃了 subject="Furina"，只剩通用 franchise/category 词） | 前两条已含 "Furina"（Option A 命中，未改动）；第 3 条不含 → 无 A/B/C 锚点 → subject 存在 → **绑定**："Furina Genshin Impact character art" | 绑定 1 条 | **1569→12**（99.2% 降） |
| **Q10** | "Light and Night character design" / "光与夜之恋 character poster" / "Light and Night illustration reference" | 无（全部已锚定：前后两条含 subject "Light and Night"，中间一条含 CJK Protected Phrase "光与夜之恋"，Option B 命中） | Guard R 对全部 3 条均判定"已锚定"，不做任何改动 | 0 条改动 | **1724→1724（不变）** |
| **Q12** | "relaxed lifestyle illustration" / "cozy living design" / "serene lifestyle artwork" | 全部（无 subject，纯 CJK 原始 Query 对纯英文候选零字面重叠） | 无 subject + 跨语言（CJK→EN 合法翻译场景）→ Option E 放行不改动，保护翻译机制 | 0 条改动 | **1694→1694（不变）** |
| **Q47** | "Douyin product card design" / "TikTok merchandise template" / "ecommerce product card" | 第 2 条（不含 subject "product card"，与原文无字面/规则短语重叠） | subject 存在 → **绑定**："product card TikTok merchandise template" | 绑定 1 条 | **1031→1011**（仅降 2%，见第 8 节根因说明） |
| **Q48** | "Douyin influencer character poster" / "live commerce host profile" / "shopping influencer character design" | 第 2 条（不含 subject "Douyin influencer"、无重叠） | subject 存在 → **绑定**："Douyin influencer live commerce host profile" | 绑定 1 条 | **1155→1155（不变，见第 8 节）** |

**不得强行套用同一修复的确认**：Q10/Q12 的根因经证实**并非** rewrites[] 缺锚点问题——Q10 的 3 条候选本身就已充分锚定（Guard R 未改动任何东西），真正洪泛源是 decomposition subject "Light and Night" 本身在被拆词后退化为通用词 "light"/"night"（Top 结果出现 "la land"/"night routine"/"quiet night thoughts" 等无关内容），这是 Prompt 2 decomposition Guard 的范围，本阶段明确不改动。Q12 是本阶段刻意保留的权衡（保护 CJK→EN 合法翻译机制优先于堵死这一条边界 Case）。Q47/Q48 虽触发了 Guard R（绑定），但改善幅度很小——人工复核确认这两条的洪泛主力其实是 subject 本身（"product card"、"Douyin influencer"）和另外两条**已经锚定**的候选，不是被绑定的那一条，Guard R 的设计范围本就不覆盖这种情况。

## 4. Rewrite Candidate Guard

`evaluateRewriteCandidate(original, candidate, subject)` 的判定顺序：

1. **executable token 判断**（Guard R1）：复用 `segmentCJKToken`/`applyPhraseAliasRulesExcluding`/`CJK_ATOMIC_PHRASES` 对候选分词，若 `primary.length===0 && aliasGroups.length===0` → 拒绝 `EMPTY_EXECUTABLE_TOKENS`。
2. **anchor 判断**（Guard R2）：
   - **shared anchor**：候选 token 与"比较基准"（有 subject 时为 subject 分词结果；无 subject 时回退为原始 Query 自身分词结果）有交集 → 接受不改动。
   - **alias/protected phrase 等价**：原始 Query 与候选各自命中 `PHRASE_ALIAS_RULES` 同一条规则的任一成员（phrase 本身或其 aliasTokens）→ 接受不改动（覆盖跨语言实体等价，如 "光与夜之恋" ↔ "Light and Night"；也覆盖 Alias-group 等价，如 "手冲咖啡" ↔ "brand identity"）。
   - **独立锚点**：候选自身含"真实字典分词后仍保持整体的 CJK 复合词"（如 "篮球鞋" 经 jieba 分词后仍是 1 个 token，不会被拆成"篮球"+"鞋"）或含数字的 ASCII token（型号/版本号）→ 接受不改动。
   - **绑定**：以上均不满足，但存在 subject → `${subject} ${candidate}`，标记 `subjectBound: true`。
   - **拒绝**：无 subject 且候选与原始 Query 同语言（非跨语言合法翻译场景）→ 拒绝 `UNANCHORED_REWRITE_CANDIDATE`。

## 5. Reasonable Broadening

- **乔丹鞋 → 篮球鞋**：实测 jieba 对 "篮球鞋" 分词结果为 `["篮球鞋"]`（整体保留，不拆分），而非我最初设想的 `["篮球","鞋"]`；因此与原文 "乔丹鞋"（分词为 `["乔丹","鞋"]`）**零字面重叠**。若仅靠"共享 token"判断会被误伤为 `UNANCHORED_REWRITE_CANDIDATE`——这正是 Guard R2 独立锚点（Option C）存在的原因："篮球鞋" 作为真实字典词本身就是一个具体类别名词，不需要与原文重叠即可被接受。已用单测直接验证（`乔丹鞋 -> 篮球鞋` 用例）。
- **另外两个泛化样例**（避免只覆盖单一 Query）：`婚纱照 → 婚礼摄影`（wedding photo → wedding photography）、`手机壳 → 数码配件`（phone case → digital accessories），均无 subject、零字面重叠，均通过 Guard R2 Option C 保留。
- **如何避免误伤**：Option C 的判定条件是"jieba 真实分词后仍是完整 token 的 CJK 复合词"或"含数字的 ASCII token"，不依赖任何静态英文黑名单，也不对 English 单词做"是否是专有名词"之类的脆弱启发式判断（曾考虑用大小写做代理信号，但会让 "Genshin Impact character art" 这种应该被绑定的候选因为 "Genshin"/"Impact" 首字母大写而被误判为已有独立锚点，故放弃）。

## 6. Diagnostics

`RejectedSlot.reason` 类型扩展为：`"UNBOUND_NON_SUBJECT_SLOT" | "EMPTY_EXECUTABLE_TOKENS" | "UNANCHORED_REWRITE_CANDIDATE"`；`RejectedSlot.slotKey` 扩展为 `keyof QueryDecomposition | "rewrite"`。`evaluateRewriteCandidate` 返回 `RewriteCandidateEvaluation`（`candidate`/`normalizedCandidate`/`executableTokens`/`originalAnchors`/`candidateAnchors`/`sharedAnchors`/`accepted`/`bindingApplied`/`executedQuery`/`reason?`），JSON-serializable，纯函数无副作用，可独立单测。`FlattenedPath.subjectBound` 语义扩展为"subject 自身、绑定到 subject 的 decomposition slot、或本阶段新增的绑定到 subject 的 rewrite 候选"，均为 `true`。`page.tsx` 的诊断日志行统一使用 `r.reason`，不再对 `rewrites` 的拒绝原因误标为 `UNBOUND_NON_SUBJECT_SLOT`。

## 7. Cache Semantics

`getMultiQueryPaths` 中 `hasExecutablePath = flattenPathsWithDiagnostics(trimmed, out).executed.length > 0` **未改动一行代码**，但由于该函数现在内部会调用 `evaluateRewriteCandidate`，Cache 分类自动、正确地反映了 Guard R 的判定结果：

- 全部 rewrites 被 Guard R 拒绝 + 无 decomposition → Negative Cache（10 分钟）。
- 至少 1 条 rewrite 被 Guard R 接受（含绑定）→ Success Cache（7 天）。
- 全部 decomposition 被拒绝 + 全部 rewrites 被拒绝 → Negative Cache。
- 至少 1 个 decomposition subject 存活，即使某条 rewrite 被拒绝 → Success Cache。
- 部分合法/部分非法候选混合 → 只要有 1 条存活即 Success Cache。

5 个新增 Cache 测试直接验证了以上全部分支（见第 9 节）。

## 8. Modified Files

### Prompt 2B 修改
- `lib/searchRewrite.ts`：新增 imports（`tsToSc`、`applyPhraseAliasRulesExcluding`、`segmentCJKToken`、`CJK_ATOMIC_PHRASES`、`PHRASE_ALIAS_RULES`）；新增 Guard R 相关函数与类型（`REWRITE_STOPWORDS`、`normalizeRewriteText`、`anchorTokens`、`anchorTokenSet`、`hasCJK`、`hasIndependentAnchor`、`sharesRulePhrase`、`RewriteCandidateEvaluation`、`evaluateRewriteCandidate`）；`RejectedSlot`/`FlattenedPath` 类型扩展；`flattenPathsWithDiagnostics` 内部重排（subject 提前计算）并改写 rewrites 循环调用 `evaluateRewriteCandidate`。**未改动** `flattenPaths`、Guard 2 的 decomposition 绑定逻辑、`getMultiQueryPaths` 的候选净化/Cache 写入逻辑本身。
- `app/[locale]/(public)/search/page.tsx`：1 行日志改动（见第 2 节）。
- `lib/__tests__/searchRewrite.test.ts`：更新 1 条既有测试（`"plain rewrites array is untouched by Guard 2"` 更名并补充说明其通过原因已变为 Guard R 的跨语言保护，而非"完全未被触碰"）；新增 39 条 Guard R 定向测试。

### Prompt 2B 新增
- `scripts/curify-search-stage7-guard-smoke/replay_prompt2b.cjs`（新脚本，见第 16 节 Replay 方法）。
- `docs/daily_report/7.14/search-relevance-stage7-rerun/prompt2b/` 全部输出文件。

### Prompt 2B 开始前已有改动（未触碰，快照记录见 manifest）
- `app/[locale]/(public)/blog/[slug]/components/GenericBlogContent.tsx`、`app/[locale]/(public)/blog/[slug]/page.tsx`、`lib/query_phrase_aliases.ts`（Prompt 2 已有改动）、`lib/zh_normalize.ts`（Prompt 2 已有改动）、`messages/*/blog.json`、`next.config.ts`、`package.json`/`package-lock.json`、`scripts/eval_search.cjs`、`lib/__tests__/search_metadata_scenarios.test.ts`、`lib/cjk_tokenizer.ts`（Prompt 2 新增未跟踪文件）、`lib/__tests__/stage6_dictionary_hybrid.test.ts`（Prompt 2 新增未跟踪文件）。

## 9. Tests

| 命令 | 结果 |
|---|---|
| `npx vitest run --config vitest.unit.config.ts lib/__tests__/searchRewrite.test.ts` | 99/99 通过（60 既有 + 39 新增） |
| `npx vitest run --config vitest.unit.config.ts lib/__tests__/stage6_dictionary_hybrid.test.ts lib/__tests__/search_metadata_scenarios.test.ts` | 126/126 通过（未改动，回归确认） |
| `npx vitest run --config vitest.unit.config.ts`（全量） | 295/295 通过（Prompt 2 基线 260） |
| `npx tsc --noEmit` | 0 错误 |
| `npm run build` | 退出码 0，成功 |

新增测试覆盖：Guard R1 空候选（空字符串/空白/纯分隔符标点/停用词专用/裸词"template"）5 条；Guard R2 无锚点候选（同语言无 subject 拒绝、混合锚定/未锚定、多条同时拒绝）3 条；Guard R2 绑定（Q06/Q47 真实场景各 1 条）2 条；Guard R2 跨语言保护（Q12 真实场景 + 对称的英转中场景）2 条；Guard R2 Options A/B/C 各 1 条共 3 条；合理泛化 3 条；实体漂移绑定 2 条；Guard 2 decomposition 回归确认 4 条；Alias/CJK/Protected Phrase/普通英文/中英混合 5 条；Cache TTL 5 条。合计 39（含 2 条为修正既有测试假设后新增的补充断言）。

## 10. Validation

- **TypeScript**：`npx tsc --noEmit` 通过，0 错误。
- **Build**：`npm run build` 成功（exit 0）。构建日志中出现的 `MISSING_MESSAGE: blog.*` 错误针对 `hi`（印地语）Locale 的博客翻译键，与本次搜索改动无关，是既有问题。
- **Lint**：运行 `npx eslint` 后报 `typescript-eslint`/`eslint.config.js` 的 `extends` 数组不兼容错误（ESLint 9 flat config 与仓库配置的既有不兼容问题），与本次代码内容无关，未修复（遵循"不修复已有配置问题"的指示）。
- **已有问题**：上述 Lint 配置问题、`hi` Locale 缺失翻译均为 Prompt 2B 开始前已存在，未被本阶段引入或加剧。

## 11. Deferred

以下明确推迟到未来阶段，本轮未实现：

- **目录级 IDF / 词频稀有度打分**：本轮明确禁止引入，Guard R 完全基于锚点共享/别名等价/独立类别锚点/绑定这 4 种机制，不对"某个词有多常见"做统计判断。
- **静态英文黑名单（denylist）**：未使用，也未针对 poster/template/design 等词做特判。
- **第二个 LLM Judge**：未引入，所有判定均为确定性规则。
- **候选数量预算（Top N 截断）**：未实现，`MAX_REWRITES=3` 沿用现有上限，未新增基于结果数的截断逻辑。
- **分层 Merge / Ranking 重排**：Q47/Q48 揭示的"绑定 1 条候选但其贡献被其余路径完全掩盖"问题，本质上是 Merge/Union 阶段对多路径贡献度未做区分（所有命中路径平权 Union，只有 命中数量 做 +8%/次 的轻微加权），这类问题超出 Guard R 的设计范围，留给未来 Ranking 阶段处理。
- **Q10 类型的 decomposition subject 质量问题**（subject 本身分词后退化为通用词）：明确不属于本阶段范围（会触碰"已经有效的 decomposition Guard"），记录为未来 Prompt 2 系列潜在方向。

## 12. Limitations

- Live Smoke（真实 LLM 调用）本阶段未运行，Prompt 2B 明确禁止。
- Replay 仍是固定的、7.13 记录的 raw rewrite/decomposition 输入回放，非新的 LLM 输出，无法评估 LLM 输出非确定性对 Guard R 判定结果的影响。
- 人工/结构化审核覆盖 26 行 Replay 结果中的 13 行（全部 11 个强制要求 Case + 2 个补充 PASS 对照），其余 13 行仅有自动启发式判定。
- 自动启发式判定与人工复核在 2 个案例（Q40 D/C）上不一致——自动判定因结果数低（=3）误标为 PASS，人工复核发现实际内容是"post"（发帖）与"post office"（邮局）的同形异义碰撞，与小红书内容无关；已在人工复核 CSV 中如实记录并覆盖。
- `OPENAI_API_KEY` 在当前 Shell 会话缺失，但本阶段 Replay 不需要真实 LLM 调用，不构成阻塞；仅意味着无法在本环境验证 Live 就绪状态。
- Lint 因仓库既有的 ESLint 9 flat-config 兼容性问题无法运行，未修复（不在本阶段范围）。

## 13. Readiness for Replay

**READY_FOR_REPLAY** — Harness 审计通过（真实 production 逻辑，已重新 build bundle 并记录新 hash）；全量测试/TypeScript/Build 全部通过；Guard R 实现完成，未破坏已有的 Guard 1/2/3/4/5 行为（全部既有测试保持绿色）。已据此完成 Replay，见 `STAGE7_PROMPT2B_REPLAY_SUMMARY_2026-07-14_zh.md`。
