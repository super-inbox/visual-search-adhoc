# Stage 7 Prompt 2B Replay Summary

## 1. Executive Summary

Prompt 2B 为 `lib/searchRewrite.ts` 的 `flattenPathsWithDiagnostics` 新增了 Guard R（`evaluateRewriteCandidate`），首次对 `rewrites[]` 自由文本改写候选做锚点校验（空 token 拒绝 + 锚点共享/别名等价/独立锚点/绑定 subject/无锚点拒绝），修复了 Prompt 3 确认的"Guard 1/2 只约束 decomposition，rewrites[] 不受约束"的缺口。

使用与 Prompt 3 完全相同的固定 Query 集（SHA-256 校验一致）、相同的 7.13 已保存 raw rewrite/decomposition 输入（未调用 LLM）重新运行 Deterministic Replay：

- 23 个 D 组洪泛 Case 相对 **Stage 7 原始历史基线** 的改善比例从 Prompt 3 的 **78.3%（18/23）提升到 82.6%（19/23）**，达到并超过 80% 门槛（即"最多允许 4 条仍 `>=1000`"，本次恰好 4 条：Q10、Q12、Q47、Q48）。
- Full-catalog（3209）保持 **0**，Q39/Q40/Q42 均未恢复 full-catalog。
- 全部 26 行 Replay **0 个 regression**（无任何 Case 结果数量相对 Prompt 3 基线上升）。
- **Replay 达到 Gate，可以进入（受限的）Prompt 3 Live Smoke**——见第 10 节最终结论。

## 2. Harness Verification

见 `STAGE7_REWRITE_ARRAY_GUARD_IMPLEMENTATION_2026-07-14_zh.md` 第 2 节完整审计，摘要：

- Guard 2 核心逻辑（`flattenPathsWithDiagnostics`，含本阶段新增的 Guard R）通过 esbuild 从当前 production 源码真实打包导入，非复制。
- Guard 1 相关 scoring 逻辑（`buildSearchTokens`/`scoreBlob`）因 `page.tsx` 是 Next.js Server Component 无法直接导入，采用逐字转录 + 漂移检测（`verifyAgainstLiveSource`，8 项字面子串断言）。
- Bundle 已在 Replay 前重新构建（`node build_bundle.cjs`），`lib/searchRewrite.ts` 的 bundle 源哈希从 Prompt 3 的 `52c5a066...` 变为本次 `bf2160d5...`，确认使用当前 Prompt 2B 代码，非旧缓存。
- `page.tsx` 本身也有 1 处小改动（诊断日志行），导致漂移检测器的 1 条预期子串需要同步更新（`errorType=UNBOUND_NON_SUBJECT_SLOT` → `errorType=${r.reason}`），已完成并重新验证通过（`missing: 0`）。

## 3. Before vs After

| 指标 | Prompt 3（Guard 1+2 后） | Prompt 2B（+Guard R 后） |
|---|---|---|
| Replay runs | 26 | 26 |
| PASS | 5 | 6 |
| PARTIAL | 17 | 18 |
| FAIL | 4 | 2 |
| 23 个 D 组 `>=1000`（vs Stage 7 原始基线） | 5（78.3% 改善） | **4（82.6% 改善）** |
| Full-catalog | 0 | 0 |
| Regression | 1（Q40 C，tokenizer 版本不可比，非 Guard 劣化） | 0 |
| `rewrite_anchor_guard_triggered` | 不适用（Guard R 尚不存在） | 12/26 行触发（拒绝或绑定至少 1 条 rewrite 候选） |

## 4. Five Remaining Cases

见实现报告第 3 节完整表格；核心结论：

- **Q06**：绑定 1 条候选（丢弃 subject "Furina" 的 "Genshin Impact character art" → "Furina Genshin Impact character art"），**1569 → 12**，人工复核确认 Top 5 全部为真正的 Genshin Impact 角色相关内容，**PASS**。
- **Q10**：Guard R 判定全部 3 条候选已锚定（2 条含字面 subject，1 条含 CJK Protected Phrase "光与夜之恋"），未做任何改动，**1724 → 1724 不变**。人工复核确认洪泛源不是 rewrites[]，而是 decomposition subject "Light and Night" 本身分词退化为通用词 "light"/"night"，超出 Prompt 2B 范围。
- **Q12**：无 subject，纯 CJK 原始 Query 对纯英文候选零字面重叠，Guard R 的跨语言合法翻译保护机制放行不改动，**1694 → 1694 不变**。人工复核确认这是有意识的取舍（保护 CJK→EN 翻译能力优先于堵死这一残留洪泛）。
- **Q47**：绑定 1 条候选，**1031 → 1011**，仅降 2%。人工复核确认洪泛主力是 subject "product card" 本身和另外两条已锚定候选，被绑定的那一条本就不是主要贡献者。
- **Q48**：绑定 1 条候选，**1155 → 1155 完全不变**。同 Q47 模式：被绑定候选的贡献被其余路径完全掩盖。

## 5. Full-catalog Regression Check

| Query | Mode | 新 Count | 是否 Full-catalog |
|---|---|---|---|
| Q39 | D | 0 | 否 |
| Q39 | C | 0 | 否 |
| Q40 | D | 3 | 否 |
| Q40 | C | 3 | 否 |
| Q42 | D | 843 | 否 |
| Q42 | C | 254 | 否 |

全部 6 行均未恢复 3209（full-catalog）。Q39 D 从 Prompt 3 的 1 进一步降到 0（人工复核：安全但空结果，无洪泛，无危害）；Q40 D/C 从 922 大幅降到 3（人工复核：**数量安全但内容错误**——"post"/"post office" 同形异义碰撞，详见第 6 节澄清，这是 7.13 记录的 decomposition subject 文本本身携带的既有问题，非 Guard R 引入）；Q42 D/C 保持/小幅改善但内容仍偏泛。

## 6. Valid Rewrite Controls

- **乔丹鞋 → 篮球鞋**：单测直接验证（`evaluateRewriteCandidate`），jieba 真实分词确认 "篮球鞋" 整体保留为 1 个 token（不拆分为"篮球"+"鞋"），与原文零字面重叠，通过 Guard R2 Option C（独立 CJK 类别锚点）保留，不被绑定或拒绝。另增 2 个泛化样例（婚纱照→婚礼摄影、手机壳→数码配件）同样通过。
- **Alias**：`手冲咖啡` → `brand identity` 候选通过 Option B（Alias-group 等价）保留；单测覆盖。
- **Protected Phrase**：`小红书`、`二手奢侈品` 候选保留（atomicEntity，Option B/C）；单测覆盖。
- **English/CJK/Mixed**：`kawaii museum sticker` → `kawaii museum sticker pack`（同语言共享 token）、`小红书cover设计` → `小红书 cover template design`（中英混合共享 CJK 锚点）均保留；单测覆盖。
- **English original + Chinese rewrite（对称跨语言场景）**：`passport photo headshot` → `证件照 风格头像` 同样受跨语言保护放行；单测覆盖。

未发现英文/CJK/中英混合 Query 的系统性回归——全量单元测试 295/295 通过，含 Stage 6 CJK 分词回归测试（61 条）、search metadata 场景测试（65 条）均未改动且保持绿色。

## 7. Cache and Diagnostics

- `getMultiQueryPaths` 的 `hasExecutablePath` 判断逻辑未改动一行代码，但因内部调用链路自动传导 Guard R 的判定结果，5 条新增 Cache 测试验证：全部 rewrites 被拒绝且无 decomposition → Negative（10 分钟）；至少 1 条被接受（含绑定）→ Success（7 天）；全部拒绝（decomposition+rewrites）→ Negative；1 个 decomposition subject 存活即使 rewrite 被拒绝 → Success；合法/非法候选混合 → Success。全部通过。
- 诊断字段 `RejectedSlot.reason` 新增 `EMPTY_EXECUTABLE_TOKENS`（rewrites 专属空 token 拒绝）与 `UNANCHORED_REWRITE_CANDIDATE`（无锚点拒绝），`slotKey` 新增 `"rewrite"`。Replay CSV 中 `rewrite_anchor_guard_triggered=true` 的行数为 **12/26**（含拒绝或绑定至少 1 条候选的所有行）。

## 8. Remaining Failures

| Query | Count | 根因 | 是否需要进一步 Prompt 2 修复 |
|---|---|---|---|
| Q10 | 1724 | decomposition subject "Light and Night" 分词退化为通用词 | 是（但属于 decomposition Guard 范围，非 rewrites[] Guard 范围，本阶段明确不触碰） |
| Q12 | 1694 | 无 subject + 纯 CJK↔纯英文候选零字面重叠，Guard R 有意保护跨语言翻译机制 | 待定（需要权衡：进一步收紧会伤及合法 CJK→EN 翻译能力，建议下一阶段引入更细粒度的信号而非简单拒绝） |
| Q47 | 1011 | 洪泛主力是 subject 本身 + 已锚定候选，Guard R 绑定的候选不是主因 | 是（需要 Merge 阶段的路径贡献度区分，或对"已锚定"候选也施加更强约束） |
| Q48 | 1155 | 同 Q47 模式 | 是（同上） |
| Q40 D/C | 3（数量已安全） | "post"（发帖）/"post office"（邮局）同形异义碰撞，源自 7.13 记录的 decomposition subject 文本本身 | 否（数量层面已解决，属于内容相关性问题，非洪泛问题，超出本阶段"洪泛修复"范围） |

以上均非 Guard R 逻辑缺陷（Guard R 按设计正确执行），而是揭示了 Guard R 设计边界之外的残留问题：decomposition subject 质量、Merge 阶段路径加权、以及无法自动区分的语义歧义。

## 9. Limitations

- Live Smoke 本阶段未运行（Prompt 2B 明确禁止）。
- Replay 仍是固定输入回放，未评估真实 LLM 输出下 Guard R 的行为。
- 人工复核覆盖 26 行中的 13 行（全部强制 Case + 2 条补充 PASS 对照）。
- 自动启发式判定与人工复核在 Q40 D/C 上不一致（自动因低计数误判 PASS，人工发现内容错误），已在人工复核 CSV 中覆盖并如实记录。
- `OPENAI_API_KEY` 本次 Shell 会话缺失，但 Replay 不需要 LLM 调用，不构成阻塞。
- 目录内容自 7.7/7.13 起可能已漂移，未量化（继承自 Prompt 0/1 的已知限制）。

## 10. Final Gate

### **READY_FOR_LIVE_SMOKE**

理由：
1. 23 个 D 组洪泛 Case 相对 Stage 7 原始基线改善比例 82.6%（19/23），达到并超过 Prompt 3/2B 共同规定的 80% 门槛（最多允许 4 条仍 `>=1000`，本次恰好 4 条）。
2. Full-catalog = 0，Q39/Q40/Q42 均未恢复 full-catalog。
3. 0 个 regression。
4. 独立非 subject decomposition path 与被拒绝的 rewrites 均未进入 Merge（单测 + Replay 诊断字段双重验证）。
5. 原始 Query first-pass 结果始终保留（`engine.cjs` 的 `baseResult` 在任何 rewrite 路径考虑之前就已写入 `inspirationById`）。
6. 合理泛化（乔丹鞋→篮球鞋等 3 例）与跨语言翻译（Q12 等）均未被系统性关闭。
7. Harness 使用当前 production 逻辑，Bundle 已重新构建并记录哈希。
8. Production Build 通过，全量单元测试 295/295 通过。
9. Production repo 未出现 Prompt 2B 声明范围之外的新修改（见对应 Prompt 2B 终端回复的 Git 状态章节）。

限制：Q10/Q12/Q47/Q48 仍 `>=1000`（4 条，恰好在允许上限），其残留原因已逐条诊断清楚且明确超出本阶段范围（decomposition subject 质量、跨语言翻译保护取舍、Merge 阶段路径加权）；Q40 D/C 揭示了一个数量安全但内容错误的既有问题（非本阶段引入）。这些限制不构成 Replay Gate 失败条件，但建议在正式进入 Prompt 4（完整 68 条重跑）之前，先完成 Prompt 3 的（受限）Live Smoke 以验证真实 LLM 输出下的行为，并将 Q10/Q47/Q48/Q40 的根因记录为后续阶段的候选修复项。
