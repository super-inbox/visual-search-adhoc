# Stage 7 Limited Live Smoke Test

## 1. Executive Summary

- 运行了 **20 条唯一 Query，共 23 次 Live Run**（Q39/Q40/Q42 各 2 次，其余各 1 次），全部使用真实当前 production 代码、真实目录数据（3209 条，与 Prompt 2B 一致）、真实 OpenAI `gpt-4o-mini` LLM 调用（0 次 Mock）。
- **Full-catalog = 0**，全部 23 次 Run 均未出现 3209。
- **`>=1000` 共 4 次**：Q10（1640）、Q12（1593）、Q47（1011）、Q06（1567，见下方重要发现）。
- **Guard 真实触发**：Subject-binding 15/23 次、Rewrite-anchor Guard 11/23 次；Empty-token Guard 本轮 0 次触发（无候选恰好为空）。
- **人工结构化复核：PASS 3 / PARTIAL 9 / FAIL 11（47.8%，远超 20% 门槛）**。
- **正常对照 Query 未出现系统性回归**（Q19、手作、watercolor spring flowers 等表现稳定或良好）。
- **重要新发现**：(1) Q06 在真实 LLM 输出下暴露了 Guard R2 的一个真实设计缺口——数字锚点规则（用于保护 es6/mate60pro 等型号）过于宽松，把 "4k" 这类分辨率描述词也当作独立锚点放行，导致本应绑定的候选未被绑定，count 从 Replay 的 12 反弹到接近原始洪泛水平的 1567。(2) Decomposition subject 泛化问题（Prompt 2 范围）在真实链路中比 Replay 固定样本显示的更普遍——除已知的 Q10 外，Q40、Q41、Q44 均独立出现同一模式（subject 丢失核心实体，退化为通用词）。
- **最终结论：`NEEDS_ANOTHER_PROMPT2_FIX`**（详见第 16 节）。不建议进入 Prompt 4。

## 2. Scope and Safety

本阶段为 Limited Live Smoke（20 唯一 Query / 23 次 Run），不是完整 68 条重跑。Production repo（`curify-frontend`）全程只读，执行前后 `git status`/`git diff --stat`/关键文件 SHA-256 逐字节一致（见第 15 节）。仅在 `visual-search-adhoc` 的 `live-smoke/` 目录和 harness 目录新增文件。

## 3. Environment

| 项目 | 值 |
|---|---|
| Branch | `baobao/search-relevance-phrase-alias-2026-07-09` |
| HEAD | `c062e618bce4044bedf718aadf59ff69f0999344` |
| Node / npm | v26.3.0 / 11.16.0 |
| package-lock.json SHA-256 | `b75bd1c7113dea2eb2194a5841f05247665d1820c664f48f5929c55648f5ed59` |
| 目录数据 SHA-256 | `f7dacc56a847f6b9c1a93a714e79b4864c3babdfb06402223abbe733dfb9d906`（3209 条，与 Prompt 2B 一致，无漂移） |
| LLM Provider / Model | OpenAI / `gpt-4o-mini` |
| `OPENAI_API_KEY` | **PRESENT**（位于 `curify-frontend/.env.local`，通过 `node --env-file=.env.local` 加载进 harness 进程，未导出到交互 Shell，全程未打印明文） |
| Cache 策略 | **进程隔离**：每个 Live Run 作为独立 `node live.cjs` 进程执行，`lib/searchRewrite.ts` 的进程内 `MULTI_CACHE` 每次都是全新空 Map——与真实 Vercel Serverless 调用的隔离方式完全一致（该文件自己的注释即如此说明）。未修改 Query 文本、未清理任何全局/生产 Cache。 |

## 4. Frozen Query Set

冻结文件：`live_smoke_query_set_2026-07-14.csv`（SHA-256 `d328df4b9cc4d298314ee439c6da06a382f5b3e962194f4f9fba2c14658f025c`，运行前后哈希一致）。20 条唯一 Query：

- **Full-catalog 核心**（各 2 次）：Q39、Q40、Q42
- **Prompt 2B 后仍 `>=1000`**（各 1 次）：Q10、Q12、Q47、Q48
- **Prompt 2B 显著改善**（1 次）：Q06
- **原 PARTIAL Case**（各 1 次）：Q18、Q19
- **语义/Guard 对照**（各 1 次）：乔丹鞋、比亚迪海豹、白箱
- **Protected Phrase / Alias / 正常对照**（各 1 次）：Q30（手冲咖啡）、Q21（二手奢侈品）、Q44（小红书）、Q41（中英混合）、Q50（SOP 缩写）、手作（CJK 正常）、watercolor spring flowers（英文正常，不应触发 Rewrite）

合计 20 唯一 / 23 次 Run，均在 18–24 / ≤27 范围内。

## 5. Live Harness

- `live.cjs`（新建，Prompt 3B 专用入口）复用 `engine.cjs`/`scoring.cjs`/`csv_utils.cjs`，未复制或重写任何 Guard 逻辑。
- `runOne(query, {})` 不传 `multiPathsOverride`，因此在 `lowResultGatePassed` 为真时会真实调用 `bundle.getMultiQueryPaths(query)`（真实 OpenAI 请求）。
- Bundle 已在运行前重新构建（`node build_bundle.cjs`，2026-07-14T06:44:32.210Z），`lib/searchRewrite.ts` 源哈希 `bf2160d5...` 与 Prompt 2B 结束时完全一致（生产代码在两阶段之间未变化）。
- `page.tsx` 漂移检测（`verifyAgainstLiveSource`）8 项全部通过（`missing: 0`）。
- 已知限制：Guard 1 的 `scoreBlob`/`buildSearchTokens` 仍是逐字转录（因 `page.tsx` 是 Next.js Server Component 无法直接 `require`），非直接导入，与 Prompt 3/2B 的既有折衷一致。

## 6. Core Guard Results

| 指标 | 触发次数 / 总 Run 数 |
|---|---|
| Empty-token Guard | 0/23（本轮无候选恰好为空） |
| Subject-binding Guard | 15/23 |
| Rewrite-anchor Guard（拒绝或绑定 rewrite 候选） | 11/23 |
| No-valid-rewrite-path | 3/23 |
| 原始 first-pass 结果保留 | 23/23（`engine.cjs` 的 `runOne` 始终先用 `baseResult.scored` 填充 `inspirationById`，结构性保证） |

## 7. Q39/Q40/Q42 Deep Dive

### Q39（亚马逊评论截图水印素材）
- **Run 1**：LLM 输出 `{"rewrites":["Amazon review screenshot template","watermark for reviews","screenshot design resources"],"decomposition":{"subject":"Amazon reviews","style":"watermark","output":"screenshot"}}`——与 7.13 记录的输出不同（subject/output 措辞均变化），证实 LLM 非确定性。Guard 正确绑定了脱离 subject 的候选（"screenshot design resources"→"Amazon reviews screenshot design resources"）。Count=7，无 full-catalog。**但人工复核 Top 7 全部无关**（智能手表/耳机/咖啡机等通用电商模板）——数量安全但内容不相关，是目录内容缺口，非 Guard 缺陷。
- **Run 2**：LLM 输出 `{"rewrites":[],"decomposition":{}}`（Path B，判定该 Query 无法映射到目录），first-pass 本身也是 0，最终 **count=0**。Diagnostics 显示 0 个 rejected/empty-token path——Guard 从未获得任何候选可供判断，是 **LLM 自身的 Path A/B 判定摇摆**，不是 Guard 过度过滤。
- **两次判断**：不能因 3209→0/7 就判 PASS；两次均标记 **PARTIAL/FAIL**（内容层面均不合格），但均确认无 Full-catalog、无 Guard 过滤异常。

### Q40（小红书图文笔记模板 数字标题）
- **两次运行 LLM 输出完全相同**（同一进程隔离验证不是 Cache 命中，可能是该 Query 在当前温度设置下的真实收敛）：`{"rewrites":["Xiaohongshu graphic note template","digital title design","social media post template"],"decomposition":{"subject":"graphic note","output":"template"}}`。
- **未出现 `post`/`post office`**（7.13 记录的那个同形异义碰撞本轮未复现），但出现了**另一个**同样错误的碰撞——Top 8 全部是"Cat-themed Red Envelopes"/"Dragon Year Red Envelopes"等春节红包模板，与小红书笔记模板完全无关。根因相同：decomposition subject "graphic note" 丢弃了"小红书"实体，退化为通用词。
- **数量小但语义错误，两次均判 FAIL**（不能因为 count=8 就判 PASS）。

### Q42（小红书封面模板 白底大字）
- **两次运行 LLM 输出完全相同**：`{"rewrites":["Xiaohongshu cover template","white background text design","social media cover layout"],"decomposition":{"subject":"Xiaohongshu cover","style":"minimalist","output":"template"}}`。
- 与 Prompt 2B Replay 几乎完全一致地复现了"cover"碰撞：Top 3 均为"microsoft ai dilemma cover"/"one hundred years of solitude cover"，与小红书封面无关。
- Subject Binding 有触发（"minimalist"/"template" 绑定到 "Xiaohongshu cover"），Empty-token 未触发，Count（464）未超 1000。**两次均判 FAIL**（内容不相关）。

## 8. Remaining Flood Cases

- **Q10**：1640，Top 结果（"leo"/"la land"/"quiet night thoughts"）与 Prompt 2B Replay 的"light"/"night"通用词碰撞完全一致复现。3 条 rewrite 候选均被 Guard R 正确判定为已锚定（2 条含"Light and Night"，1 条含 CJK Protected Phrase "光与夜之恋"）——Guard R 本身工作正常，根因是 decomposition subject 本身。
- **Q12**：1593，全部 3 条候选通过跨语言保护（Option E）放行，与 Replay 一致复现。
- **Q47**：1011，与 Prompt 2B Replay 几乎完全相同（LLM 输出与 7.13 记录高度相似），Guard 绑定效果依然边际。
- **Q48**：本次真实 LLM 输出与 7.13 记录不同，绑定后 **count=565（首次低于 1000）**——LLM 非确定性这次对该 Query 有利，不代表 Guard 逻辑改变。
- **Q06**：**重要新发现**——真实 LLM 输出中出现候选 "Genshin Impact fanart 4k"（丢弃了 "Furina"），因含数字 token "4k" 被 Guard R2 Option C 误判为独立锚点而未绑定，Count 从 Replay 的 12 反弹到 **1567**（接近原始洪泛水平 1569）。Top 10 中 7/10 仍是 Genshin Impact 相关内容（franchise 层面保留），但具体角色 Furina 的narrowing 丢失，判定 PARTIAL。这是本阶段发现的、Replay 固定输入未能暴露的**真实 Guard R 设计缺口**。

## 9. Semantic Controls

- **乔丹鞋**：LLM 输出 `subject="Jordan shoes", output="poster"`，Guard 正确执行泛化绑定，未误拒绝。**但 Top 10 中出现"Jordan 2026 World Cup squad"（约旦国家队）、"Basketball ft Michael Jordan..."（NBA 球星）等"Jordan"一词的其他义项误配**——这是"Jordan"多义性导致的目录内容碰撞，不是 Guard 的锚点判断问题（Guard 该做的事都做对了）。
- **比亚迪海豹**：**未出现错误 Rewrite 为"BYD Seagull"**，本次真实 LLM 输出正确识别为"BYD seal"，原车型实体全程保留，Guard 未被要求纠正任何漂移（无漂移发生）。但 Top 3（"guitar"/"physics electric charges"/"fender stratocaster guitar"）与"electric"一词碰撞完全无关——这是另一个与实体漂移无关的目录内容问题。
- **白箱**：LLM 选择了字面"white box"（包装设计）释义，未触及动画行业术语释义——这是查询本身固有的歧义，无 Guard 能解决，Top 10 大部分无关，但也未产生错误的强行匹配。

## 10. Phrase/Alias/CJK Controls

- **小红书**（Q44，小红书探店笔记封面）：Protected Phrase 未被拆分，但 decomposition subject 被 LLM 写成"store review"（丢弃了"小红书"），Top 5 是 ESL 语言学习卡片，完全无关——与 Q10/Q40 同一模式的第三次独立复现。
- **手冲咖啡**（Q30）：Protected Phrase + Alias-group（brand identity/visual identity）工作正常，Top 5 中 2 条真正相关（"riseup coffee"、"BREW & CO 品牌视觉规范"），是本轮少数 PASS 之一。
- **二手奢侈品**（Q21）：本次 LLM 返回空 Rewrite（Path B），回退到原始 Query 首轮结果（57 条），Protected Phrase 未被误伤，但目录本身确无相关内容（已知缺口，非本阶段引入）。
- **Alias（Q41，中英混合"小红书对比图 use前后"）**：Subject 保留为"Xiaohongshu"但该词在目录中过于通用（大量模板的受众描述都提到小红书），Top 5 是婚纱/牛仔裤等时尚内容，无关——同一模式的第四次复现。
- **English/CJK/Mixed 正常对照**：手作（CJK，未触发 Rewrite，Top 5 与"手作"存在松散关联）、watercolor spring flowers（英文，未触发 Rewrite，Top 5 完全相关）均**无回归、无系统性 0 结果、无 Full-catalog**。

## 11. Human Top-10 Review

23/23 Live Run 全部完成结构化复核（`reviewer_type=CLAUDE_STRUCTURED_REVIEW`，非用户本人视觉审核）：

- **PASS（3）**：Q19（heritage brand rebrand moodboard，全部 Top 5 严格相关）、Q30（手冲咖啡工作室视觉手册）、watercolor spring flowers（正常英文对照）。
- **PARTIAL（9）**：Q39 Run2（0 结果但为 LLM 判定而非 Guard 过滤）、Q06（franchise 保留但角色丢失）、Q47*（Q47 判 FAIL 见下，此处为 Q48/Q18/乔丹鞋/白箱/Q21/手作等混合相关性案例）。
- **FAIL（11，47.8%）**：Q39 Run1、Q40 Run1/Run2、Q42 Run1/Run2、Q10、Q12、Q47、Q44、Q41、比亚迪海豹——绝大多数是"数量安全但内容基本无关"，而非 Full-catalog 或错误实体替换。

## 12. Metrics

### 运行指标
Unique Query 20 / Live Run 23 / 成功 23 / Error 0 / Timeout 0 / Cache Hit 0（进程隔离保证）/ LLM Called 21 / Rewrite Triggered 21 / Empty-token Guard 0 / Subject-binding Guard 15 / Rewrite-anchor Guard 11 / No-valid-rewrite-path 3

### 结果指标
Full-catalog 0 / `>=1000` 4 / 0-result 2 / 原始 first-pass 保留率 100%（结构性保证）/ Human PASS 3 / PARTIAL 9 / FAIL 11（47.8%）/ BLOCKED 0 / 正常对照 Regression 0

## 13. Replay vs Live Interpretation

Replay（Prompt 3/2B）是固定输入下的因果证据：相同输入，仅 Guard 代码不同，count 变化可直接归因于 Guard。本次 Live 是**当前真实行为证据**，不是严格 A/B——LLM 输出、目录内容、Cache 状态均可能与 Replay 时不同。Q06、Q40、Q42 的具体案例证明了这一点：Q40/Q42 的具体错误内容（红包 vs post office）在两次评估间发生了变化，但**根本模式**（decomposition subject 丢弃实体 → 泛词碰撞）保持一致，说明这是一个稳定、可复现的结构性问题，而不是某次特定 LLM 输出的偶然产物。

## 14. Remaining Failures

| Query | Count | Top 10 问题 | 根因 | 需要代码修复？ | 归属 |
|---|---|---|---|---|---|
| Q39（两次） | 7 / 0 | 无关电商模板 / 空结果 | 目录内容缺口 + LLM Path A/B 判定摇摆 | 否 | 内容/LLM |
| Q40（两次） | 8 / 8 | 春节红包模板，与小红书笔记无关 | decomposition subject "graphic note" 丢弃"小红书"实体 | 是（Guard 2/decomposition，非本阶段范围） | Guard 2 |
| Q42（两次） | 464 / 464 | "cover"泛词碰撞 | 无 subject，跨语言候选无约束放行 | 待定（收紧会伤及合法翻译） | Guard R 权衡 |
| Q10 | 1640 | "light"/"night"通用词碰撞 | decomposition subject 分词退化为通用词 | 是（Guard 2/decomposition） | Guard 2 |
| Q12 | 1593 | 泛化 wellness 内容 | 无 subject + 跨语言保护，有意权衡 | 待定 | Guard R 权衡 |
| Q47 | 1011 | 无关电商/知识卡内容 | subject "product card" 本身宽泛 + 已锚定候选主导 | 是（Merge 路径加权，超出 Guard R 范围） | Merge |
| Q06 | 1567 | 角色特异性丢失 | Guard R2 数字锚点规则（"4k"）过于宽松 | **是（Guard R 本身，Prompt 2B 范围内的缺陷）** | **Guard R** |
| Q44 | 7 | ESL 语言卡片，与小红书探店无关 | 同 Q10/Q40 模式 | 是（Guard 2/decomposition） | Guard 2 |
| Q41 | 450 | 时尚内容，与对比图无关 | subject "Xiaohongshu"过于通用（已知的目录级碰撞） | 是（Guard 2/decomposition 或 Taxonomy 层） | Guard 2 / Taxonomy |
| 比亚迪海豹 | 3 | "electric"泛词碰撞，与车型无关 | 无关目录内容碰撞，非实体漂移 | 否 | 内容 |
| 乔丹鞋 | 8 | "Jordan"多义碰撞（国家/球星/品牌） | 目录内容/Taxonomy 层歧义 | 否（Guard 层面无法区分词义） | 内容/Taxonomy |

## 15. Limitations

- LLM 非确定性：Q39 两次输出/结果差异显著；Q40/Q42 两次输出完全相同（已核实为进程隔离下的真实收敛，非 Cache 伪影，但也不构成"两次独立证据"意义上的变化性）。
- Cache：进程隔离设计保证了 Cache 不干扰，但也意味着无法观测"真实同进程内 Cache 命中"下的行为（该情形已由 Prompt 2/2B 的 Cache 单元测试覆盖）。
- 目录漂移未量化（与 Prompt 2B 一致，3209 条哈希未变）。
- Human review 为 `CLAUDE_STRUCTURED_REVIEW`（基于 title/category/tags 的结构化审核），非用户本人视觉审核。
- Guard 1 的 scoring 转录仍是既有限制（page.tsx 无法直接导入）。
- 仅覆盖 20/68 条权威 Query，尚未完整 68 条重跑。
- 未截图（本阶段明确禁止）。

## 16. Final Gate

### **NEEDS_ANOTHER_PROMPT2_FIX**

理由：

1. Human FAIL 比例 **47.8%（11/23）**，远超 READY_FOR_FULL_68 所需的 20% 上限。
2. FAIL 主要可归因于 Guard 管线覆盖不到的两类系统性问题：
   - **Decomposition subject 泛化问题**（Prompt 2 范围）：本轮独立复现于 Q10（已知）+ Q40、Q41、Q44（新发现，均不在原 23 个 D 组洪泛样本内）——说明该问题比 Prompt 2B Replay 揭示的范围更广。
   - **Guard R2 数字锚点规则过于宽松**（Prompt 2B/Guard R 范围内的真实缺陷）：Q06 案例证实"4k"这类分辨率描述词被错误当作独立锚点，导致本应绑定的候选未被绑定，Replay 中验证有效的修复在真实 LLM 输出多样性下失效。
3. 硬性条件中 Full-catalog=0、Empty-token 不进入 Merge、原始结果保留、Production 未修改等均满足，但"Human FAIL 明显超过阈值并可归因于 Guard"这一条触发 `NEEDS_ANOTHER_PROMPT2_FIX` 的判定条件。
4. 不建议进入 Prompt 4。建议下一阶段（Prompt 2C 或等价）范围：
   - 收紧 Guard R2 Option C 的数字锚点规则，排除纯分辨率/格式类描述词（4k/8k/hd/1080p 等），或要求数字 token 同时满足字母+数字混排（型号特征）而非纯描述词。
   - 评估 decomposition subject 质量问题的独立修复方案（例如要求 subject 优先保留原始 Query 中的具名实体/平台名，而非允许 LLM 替换为通用类别词）——这是本阶段发现的、比 rewrites[] Guard 更根本的剩余问题来源。
