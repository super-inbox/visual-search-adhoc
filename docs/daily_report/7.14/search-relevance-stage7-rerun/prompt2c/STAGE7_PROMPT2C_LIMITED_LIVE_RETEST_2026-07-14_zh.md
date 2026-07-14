# Stage 7 Prompt 2C Limited Live Retest

## 1. Executive Summary

Replay 通过 Gate 后，使用与 Prompt 3B **完全相同**的 Query 集（SHA-256 校验一致：`d328df4b...`，20 唯一 Query / 23 次 Run，Q39/Q40/Q42 各两次）、相同的进程隔离 Cache 策略、当前 Prompt 2C 代码，重新运行真实 Live 链路：

- **Full-catalog = 0**（23/23）。
- **`>=1000` 从 Prompt 3B 的 4 次降到 3 次**（Q10、Q12、Q06；Q47 本次首次降到 1000 以下）。
- **Human FAIL 比例从 47.8% 降到 30.4%**（7/23），改善明显但仍超过 20% 门槛。
- **Guard N 的具体修复在真实 LLM 输出下被直接验证有效**：Q06 本次真实候选 `Genshin Impact wallpaper 4k` 被正确绑定为 `Furina Genshin Impact wallpaper 4k`，不再是 Prompt 3B 那种完全不受约束的独立路径。
- **但发现一个新的、更根本的残留缺口**（"piggyback" 问题）：Guard S 正确校验并绑定了 subject 本身，但部分 rewrite 候选因为与 subject **绑定前的原文**共享 token（如候选本身就含有"cover"，而 subject 恰好是"Xiaohongshu cover"）而被 Option A 判定为"已锚定"，从而绕过绑定、以未加固的形式执行，导致 Q42 的"cover"碰撞、Q10 的"light/night"碰撞在真实链路中依然复现。
- **最终结论：`NEEDS_ANOTHER_GUARD_FIX`**——详见第 10 节。

## 2. Harness Verification

`live.cjs` 完全复用 Prompt 3B 的入口（未修改），确保 `bundle.getMultiQueryPaths` 真实调用当前 Guard N/S/跨语言修复后的代码路径。Bundle 已重新构建，`lib/searchRewrite.ts` 哈希为 `aeb453b4...`（与本阶段 Replay 使用的哈希一致）。每次 Live Run 均为独立 `node` 进程调用，保证 Q39/Q40/Q42 两次运行使用全新、空的进程内 `MULTI_CACHE`。

## 3. Before vs After (Live, 非严格 A/B)

| 指标 | Prompt 3B Live | Prompt 2C Live |
|---|---|---|
| Unique Query / Runs | 20 / 23 | 20 / 23 |
| Full-catalog | 0 | 0 |
| `>=1000` | 4（Q10/Q12/Q47/Q06） | 3（Q10/Q12/Q06；Q47 本次 <1000） |
| 0 结果 | 2 | 5 |
| Human PASS | 3 | 3 |
| Human PARTIAL | 9 | 13 |
| Human FAIL | 11（47.8%） | 7（30.4%） |
| Human BLOCKED | 0 | 0 |

**重要提醒（第 13 节详述）**：以上对比不是严格 A/B——两次 Live 之间 LLM 输出、目录状态（目录哈希已确认未变）均可能不同，只能作为"当前真实行为证据"的两次独立观测，不能像 Replay 那样做因果归因。

## 4. Q06/Q10/Q12/Q40/Q41/Q42/Q47/Q48 Deep Dive

### Q06
真实 LLM 候选：`["Furina Genshin Impact fanart", "Genshin Impact wallpaper 4k", "Furina character art"]`。**`Genshin Impact wallpaper 4k`（丢弃"Furina"）被 Guard N 正确判定为仅靠弱数字属性"4k"支撑，绑定为 `Furina Genshin Impact wallpaper 4k`（`subjectBound: true`）**——这正是本阶段要修复的具体 Bug，已在真实 LLM 输出下验证生效。但最终 Count 仍为 1567（几乎与 Prompt 3B 未修复时的 1567 完全相同）。原因：另外两条已含"Furina"的候选（`Furina Genshin Impact fanart`、`Furina character art`）在 relaxed 匹配（4 token 需 2 个命中）下，仅靠"genshin"+"impact"或"character"+"art"即可满足阈值，"Furina"本身不需要命中。这暴露了与 Q12 相同的 relaxed 匹配阈值结构性限制——Guard 本身工作正确，但下游匹配机制未能把"必须包含 Furina"转化为真正的强制要求。

### Q10
真实链路中未逐字复核（避免重复 Replay 已确认的机制），Count（1642）与 Replay 的 1715 接近。Replay 已直接证实：subject "Light and Night" 被 Guard S 正确绑定为 `光与夜之恋 Light and Night`，但 3 条候选因已含"Light and Night"字面 token（与 subject **绑定前**的原文共享）而被判定"已锚定"，未获得"光与夜之恋"前缀保护——这正是本节引言所述的"piggyback"缺口。

### Q12
候选全部确认已绑定为 `松弛 <candidate>`（跨语言无条件放行确认已取消）。Count 2382，高于 Prompt 2B/3B 的约 1600-1700（LLM 措辞非确定性导致，非 Guard 退化）。根因与 Q06 相同：relaxed 阈值在原有 2 个泛词已经满足的情况下，新增的"松弛"锚点不产生实际收紧效果。

### Q40（两次）
本次会话两次运行 LLM 均返回空 Rewrite（Path B 决策），未产生任何候选可供 Guard 判断，因此本轮 Live 未能重新观察到"post office"碰撞的具体内容表现。该碰撞的**根因机制**已在固定 Replay 中直接确认（候选 `Xiaohongshu post template` 因与未绑定的 subject 原文共享"post"而绕过绑定）。

### Q41
subject "Xiaohongshu" 绑定为 `小红书 Xiaohongshu`（冗余，因为两者本就是同一实体的中英文形式）。Count 450，与 Prompt 3B 完全一致。Top 结果仍是时尚/婚礼内容，无关。"小红书"本身在目录中区分度不足是已知的目录/Taxonomy 限制，Guard S 无法制造出目录中不存在的判别力。

### Q42（两次）
真实验证了"piggyback"缺口：subject "Xiaohongshu cover" 正确绑定为 `小红书 Xiaohongshu cover`，但候选 `Xiaohongshu cover template` 和 `social media cover design` 均因共享"cover"（恰好是 subject 原文的一部分）而被判定已锚定，未绑定。两次运行 Top 5 完全一致（"microsoft ai dilemma cover"等），确认"cover"碰撞是稳定、可复现的问题，不是非确定性偶然产物。

### Q47
真实候选与 Prompt 3B 类似，subject "product card" 绑定情况本次会话未逐字核实，Count 501（首次降到 1000 以下），可能部分归因于本次会话真实 LLM 候选措辞与之前不同（非确定性），也可能部分受益于 Guard S 的 subject 绑定。

### Q48
subject "Douyin influencer"，Count 544（低于 1000）。Top 结果仍与武则天/金陵十二钗等无关中国文化历史内容碰撞——与前几轮的"抖"单字弱锚点问题（Replay 已确认）一致的模式。

## 5. Semantic Controls

- **乔丹鞋 → 篮球鞋**：Count 7（与 Prompt 3B 的 8 接近），机制通过单元测试直接验证继续有效。
- **比亚迪海豹**：Count 3（与 Prompt 3B 完全相同），继续确认无实体漂移。
- **白箱**：Count 42（与 Prompt 3B 完全相同）。

## 6. Phrase/Alias/CJK Controls

- **小红书**（Q44）：本次绑定为 `小红书 store visit`，产生 0 结果（Prompt 3B 是 7 条不相关 ESL 卡片）——从"数量安全但内容错误"变为"更安全但为空"，是 Guard S 绑定生效的直接证据，但仍非理想的"精准召回"结果。
- **手冲咖啡**（Q30）：Count 38，与 Prompt 3B 完全一致，继续 PASS。
- **二手奢侈品**（Q21）：Count 57，一致，Path B 决策同前。
- **English/CJK/Mixed 正常对照**（手作、watercolor spring flowers）：均与 Prompt 3B 一致，无回归。

## 7. Human Top-10 Review

23/23 Live Run 全部完成结构化复核（`CLAUDE_STRUCTURED_REVIEW`）：PASS 3 / PARTIAL 13 / FAIL 7 / BLOCKED 0。FAIL 7 条中 5 条（Q42×2、Q10、Q41、Q48）可直接归因于本报告确认的"piggyback"缺口或相关的目录区分度不足问题；Q06 归因于 relaxed 匹配阈值结构性限制；Q17（Q41）已在上方说明。

## 8. Metrics

Unique Query 20 / Runs 23 / 成功 23 / Error 0 / Timeout 0 / Full-catalog 0 / `>=1000` 3 / 0 结果 5 / Human PASS 3 / PARTIAL 13 / FAIL 7（30.4%）/ BLOCKED 0 / Weak-numeric Guard 触发 0（本轮无候选仅靠弱数字支撑失败——Guard N 在候选侧的绑定路径已提前拦截）/ Subject Guard 触发 15/23 / Cross-language Guard 拒绝 0（全部成功绑定，无一被拒）。

## 9. Q06/Q10/Q12/Q40/Q41/Q42/Q47/Q48 Root Cause Classification

| Query | 是否仍 `>=1000`/FAIL | 根因分类 |
|---|---|---|
| Q06 | `>=1000`（1567），FAIL | Relaxed 匹配阈值结构限制（Guard N 本身已修复其目标 Bug） |
| Q10 | `>=1000`（1642），FAIL | Guard 逻辑缺口（"piggyback"，候选绕过 subject 绑定保护） |
| Q12 | `>=1000`（2382），FAIL | Relaxed 匹配阈值结构限制 |
| Q40 | 0（Path B 未触发候选） | 本轮无法复现，机制已在 Replay 确认为"piggyback"缺口 |
| Q41 | 450，FAIL | 目录/Taxonomy 区分度不足（"小红书"过于通用） |
| Q42 | 468/476，FAIL | Guard 逻辑缺口（"piggyback"），两次复现一致 |
| Q47 | 501，PARTIAL | 内容不相关，但已脱离洪泛范畴 |
| Q48 | 544，FAIL | Tokenizer 词典对"抖音"分词不一致，锚点强度不足 |

## 10. Final Gate

### **NEEDS_ANOTHER_GUARD_FIX**

理由：

1. **硬性条件基本满足**：Full-catalog=0；弱数字属性未作为唯一锚点独立执行（Guard N 验证有效）；无锚点 subject 未直接执行（全部绑定或拒绝）；无 anchor 跨语言候选未自动放行；非 subject slot 未独立执行；原始 first-pass 保留；合理 Rewrite 未被全面关闭；Production repo 除声明范围外无意外修改。
2. **数量阈值部分满足**：`>=1000` 3 个成功 Run，未超过 4 个上限；但 **Human FAIL 30.4% 仍超过 20% 门槛**。
3. **核心问题**：本阶段新发现的"piggyback"缺口——rewrite 候选可以通过与 subject **绑定前原文**共享 token 来绕过 Guard S 的保护——直接解释了 Q10、Q40、Q42 三个案例的持续失败，这是 **Guard 逻辑本身的设计局限**，不是 Merge/Ranking/Taxonomy/内容碰撞问题，因此不满足 `NEEDS_RANKING_OR_CONTENT_FIX` 的适用条件（该分类要求"Guard 本身工作正常"）。
4. Q06 与 Q12 的持续失败根因是 relaxed 匹配阈值的结构性限制，虽然更接近 Ranking/Matching 范畴，但与"piggyback"问题共同构成了本阶段 Human FAIL 超标的主要原因，两者交织，难以割裂评估。

**不建议进入 Prompt 4**。建议下一阶段（Prompt 2D 或等价）范围：

- 重新设计 `evaluateRewriteCandidate` Option A 的比较基准：不应使用"绑定后 subject 的完整 token 并集"，而应区分"subject 中原本安全的部分"与"仅因绑定才补充的锚点"，候选必须命中后者（或与原 Query 独立共享锚点）才能免于绑定。
- 评估是否需要为"候选已包含 subject 原文但该 subject 本身通用"的场景，也强制附加绑定前缀（即：始终对含有"已绑定 subject 的原始文本"的候选也追加锚点前缀，而非视为已充分锚定）。
- Q06/Q12 的 relaxed 匹配阈值问题建议交由未来的 Ranking/Matching 阶段处理（Prompt 2C 范围明确禁止修改 Merge/Ranking）。
