# Stage 7 Prompt 2D Limited Live Retest

## 1. Executive Summary

Replay 通过数量 Gate 后，使用与 Prompt 3B/2C **完全相同**的 Query 集（SHA-256 校验一致：`d328df4b...`，20 唯一 Query / 23 次 Run，Q39/Q40/Q42 各两次）、相同的进程隔离 Cache 策略（`live.cjs` 复用不改动）、当前 Prompt 2D 代码（含 bindTarget 修正），重新运行真实 Live 链路：

- **Full-catalog = 0**（23/23）。
- **`>=1000` 从 Prompt 2C Live 的 3 次（Q10、Q12、Q06）降到 1 次（仅 Q12）**。
- **Human FAIL 比例从 Prompt 2C 的 30.4%（7/23）降到 13.0%（3/23）**，首次降到 20% 门槛以下。
- **Piggyback 修复在真实、非确定性 LLM 输出下直接验证有效**：Q06（1567→12，全部 Top-5 真实相关）、Q10（1642→330）、Q41（450→23，Top-1 首次真实相关）均从洪泛/FAIL 直接改善为正常范围。
- 仍 FAIL 的 3 条（Q42 两次运行、Q12）均为**已在 Replay 中明确定位、本阶段范围显式排除**的已知限制（通用词"cover"内容碰撞、relaxed 匹配阈值结构性问题），非新发现的 Guard 缺口。
- **执行过程中遭遇一次真实的 OpenAI API 持续变慢窗口**（与本阶段代码无关，详见第 2 节），通过重试（不修改任何超时配置或生产代码）最终 23/23 全部成功完成，无一次错误或超时残留在最终结果中。
- **最终结论：`READY_FOR_FULL_68`**（不自动触发运行）——详见第 9 节。

## 2. Harness Verification and Execution Notes

`live.cjs` 完全复用 Prompt 3B/2C 的入口（未修改），新增的 `run_live_prompt2d.cjs` 仅作为编排器（逐个 spawn 独立进程、汇总 CSV），不改变 Guard 判定逻辑。Bundle 已重新构建，`lib/searchRewrite.ts` 哈希为 `a54aaf9e...`（与本阶段 Replay 使用的哈希一致）。每次 Live Run 均为独立 `node` 进程调用，保证 Q39/Q40/Q42 多次运行使用全新、空的进程内 `MULTI_CACHE`。

**执行过程记录**（完整透明，供审计）：第一次批量执行中，23 次 Run 里有 14 次（L05-L18）在约 25 秒处命中失败——production 自身的 OpenAI client 超时配置为 8 秒（`lib/searchRewrite.ts` `TIMEOUT_MS=8_000`），叠加 SDK 默认重试次数，最坏情况耗时约 24-25 秒，与观测到的失败时间点吻合，确认是**真实的、外部 OpenAI API 响应变慢窗口**，不是 harness 或 production 代码缺陷。第二次批量执行（复用已成功的 9 条，不重复消耗 API 调用）中又有 2 条（L05、L06）成功，剩余 12 条仍连续 3 次尝试全部失败。第三次批量执行（复用已成功的 11 条）中，剩余全部 12 条**首次尝试即全部成功**——证实此前失败是暂时性外部窗口，随时间自然恢复，全程未修改任何超时数值或生产代码。最终 CSV 反映的是这次完全成功的执行结果：23/23 全部为真实 LLM 输出、0 error、0 timeout。

## 3. Before vs After (Live, 非严格 A/B)

| 指标 | Prompt 2C Live | Prompt 2D Live |
|---|---|---|
| Unique Query / Runs | 20 / 23 | 20 / 23 |
| Full-catalog | 0 | 0 |
| `>=1000` | 3（Q10/Q12/Q06） | **1（仅 Q12）** |
| 0 结果 | 5 | 6（L01×2、L02×2、L07、L16、L18 — 注：均确认为"安全但为空"，非 Guard 缺陷） |
| Human PASS | 3 | 4 |
| Human PARTIAL | 13 | 16 |
| Human FAIL | 7（30.4%） | **3（13.0%）** |
| Human BLOCKED | 0 | 0 |
| Piggyback Guard 触发 | N/A（本阶段新增诊断字段） | 17/23 |

**重要提醒**：以上对比不是严格 A/B——两次 Live 之间 LLM 输出、目录状态（目录哈希已确认未变：`f7dacc56...`）均可能不同，只能作为"当前真实行为证据"的两次独立观测，不能像 Replay 那样做因果归因。但 Piggyback 直接相关的 3 个 case（Q06/Q10/Q41）改善方向和幅度与 Replay 的因果结论高度一致，构成有力的交叉验证。

## 4. Q06/Q10/Q12/Q39/Q40/Q41/Q42/Q47/Q48 Deep Dive

### Q06
真实 LLM 候选生成 `Furina Genshin Impact character wallpaper`（subject "Furina" 正确绑定）。Count **1567 → 12**，Top-5 全部为真实相关的 Genshin Impact 角色内容。这是本次 Live 最强的直接证据：Prompt 2C 时 Guard N 已修复但仍受 piggyback 影响（1567 未降），本阶段 piggyback 修复后在真实、非确定性 LLM 输出下首次验证为 **PASS**。

### Q10
Subject "Light and Night Love" 正确绑定为 `光与夜之恋 Light and Night Love`，2 条候选全部绑定。Count **1642 → 330**，首次跌出 `>=1000`。残留 Top-5 不相关（"love"/"night"泛标签碰撞）反映 relaxed 匹配阈值/目录标签粒度问题，本阶段范围明确排除。

### Q12
无 subject，`piggyback_guard_triggered=true` 反映的是候选绑定到原 Query 自身提取锚点"松弛"（Option D2 路径），非 subject-piggyback 场景，确认按设计不受本阶段修复影响。Count **2382 → 1598**，仍 `>=1000`，与 Replay 结论一致：relaxed 匹配阈值结构性限制，本阶段禁止修改。

### Q39（两次）
两次运行均 0 结果，候选正确绑定到"亚马逊"。与 Prompt 2C（0、1）基本一致，已知内容空白，非新问题。

### Q40（两次）
两次运行 LLM 候选措辞不同（"Xiaohongshu note"/"Xiaohongshu template"），但均全部正确绑定，无一 piggyback 绕过。Count 均为 0，与 Prompt 2C 一致（该阶段也是 0/0）。

### Q41
Subject "Xiaohongshu" 绑定为 `小红书 Xiaohongshu`。Count **450 → 23**，Top-1 首次变为真实相关（"learn before and after"）。较大提升是 LLM 样本差异与 Guard 修复共同作用，不能单独归因于本阶段修复，但方向与 Replay 一致。

### Q42（两次）
Subject "cover template" 正确绑定为 `小红书 cover template`，全部候选绑定确认。Count 464/464（与 Prompt 2C 的 468/476 接近），Top-5 仍与通用英文词"cover"碰撞（AI 系列封面、书籍封面等无关内容）。两次结果 Top-5 完全一致，确认这是稳定、可复现的**内容碰撞问题**（已在 Replay 中定位），不是 Guard 逻辑缺口，本阶段范围明确排除。

### Q47
候选全部确认绑定到完整的 `抖音 product card`（而非窄锚点"抖音"）。Count 501 → 485，基本持平，残留不相关结果指向 Merge/Ranking 多路径加权问题，本阶段范围排除。

### Q48
候选绑定到 `抖 Douyin influencer`（jieba 对"抖音"分词不稳定的已知限制，本阶段范围排除）。Count 544 → 0（安全但为空，本次 LLM 样本产生的具体绑定短语恰好目录内无覆盖），非新增问题。

## 5. Semantic Controls

- **乔丹鞋**：Count 7 → 4，Top 结果确认全部相关（Air Jordan/sneaker 内容），机制继续有效。
- **比亚迪海豹**：Count 3 → 0（安全但为空），继续确认无实体漂移（"BYD Seagull"正确绑定为"比亚迪 BYD Seagull"）。
- **白箱**：Count 42 → 31，与 Prompt 2C 接近，已知语义歧义问题未变。

## 6. Phrase/Alias/CJK Controls

- **手冲咖啡**（Q30）：Count **38 → 38**（逐字节相同），继续 PASS，零回归。
- **二手奢侈品**（Q21）：Count **57 → 57**（逐字节相同），继续 PARTIAL，零回归。
- **小红书探店笔记封面**（Q44）：Count **0 → 0**（逐字节相同），零回归。
- **手作**（NA-CJK-BILINGUAL）：Count **55 → 55**（逐字节相同，本查询从未触发 LLM 改写，天然不受本阶段影响）。
- **watercolor spring flowers**（NA-EN-NORMAL）：Count **65 → 65**（逐字节相同），继续 PASS。

以上 5 个对照 case 与 Prompt 2C 完全相同的计数，是"未破坏既有合法行为"最直接的真实 Live 证据。

## 7. Human Top-10 Review

23/23 Live Run 全部完成结构化复核（`CLAUDE_STRUCTURED_REVIEW`）：**PASS 4 / PARTIAL 16 / FAIL 3 / BLOCKED 0**。FAIL 3 条（Q42×2、Q12）均已在第 4 节定位为本阶段范围显式排除的已知限制（内容碰撞、relaxed 匹配阈值），无一属于新发现的 Guard 逻辑缺口。

## 8. Metrics

Unique Query 20 / Runs 23 / 成功 23 / Error 0 / Timeout 0 / Full-catalog 0 / `>=1000` 1（Q12）/ 0 结果 6（均确认安全但为空）/ Human PASS 4 / PARTIAL 16 / FAIL 3（**13.0%**）/ BLOCKED 0 / Piggyback Guard 触发 17/23 / Subject Guard 触发 17/23。

## 9. Final Gate

### **READY_FOR_FULL_68**（结论达成，但不自动触发运行全部 68 条）

理由：

1. **硬性条件全部满足**：Full-catalog=0（23/23）；Q39/Q40/Q42 均未出现 full-catalog；弱数字属性未作为唯一锚点独立执行；无锚点 subject 未直接执行；非 subject slot 未独立执行；原始 first-pass 保留；合理 Rewrite 未被全面关闭（Q30/Q21/Q44/手作/watercolor 5 个对照 case 逐字节零回归）；Production repo 除声明范围外无意外修改（已核对 git status 与快照完全一致）。
2. **数量阈值大幅超额满足**：`>=1000` 仅 1 次成功 Run（Q12），远低于 4 的上限。
3. **Human FAIL 比例 13.0%（3/23），首次低于 20% 门槛**（Prompt 2C 为 30.4%，Prompt 3B 为 47.8%）。
4. **核心 Piggyback case（Q06/Q10/Q41）在真实、非确定性 LLM 输出下均直接验证修复生效**，且与固定 Replay 的因果结论方向一致，构成有效交叉验证。
5. 仍 FAIL 的 3 条（Q42×2、Q12）根因均已明确归类为本阶段范围排除的已知限制（内容碰撞、Ranking/Matching 结构性问题），不属于 Guard 逻辑缺口，故不适用 `NEEDS_ANOTHER_GUARD_FIX`。

**不建议进入 Prompt 4，也不自动运行全部 68 条 Query**——按任务要求，即使结论为 `READY_FOR_FULL_68`，仍需等待用户明确指示后才能触发該运行。下一步建议范围（供未来阶段参考，本阶段未执行）：

- Q42 的"cover"内容碰撞、Q47 的 Merge/Ranking 加权问题、Q48 的 Tokenizer 分词问题，可考虑作为独立的 Ranking/Matching 或 Taxonomy/内容阶段处理。
- Q12/Q06（部分）的 relaxed 匹配阈值结构性限制，建议交由未来的 Ranking/Matching 阶段统一评估，而非逐个 Query 打补丁。
