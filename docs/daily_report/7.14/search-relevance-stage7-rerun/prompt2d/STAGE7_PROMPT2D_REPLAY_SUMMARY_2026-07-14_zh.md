# Stage 7 Prompt 2D Replay Summary

## 1. Executive Summary

本阶段修复了 Prompt 2C 遗留的 **Anchor Piggyback** 缺口（Guard S 绑定 subject 后，rewrite 候选因与 subject **绑定前的原始文本**共享 token 而绕过绑定），使用与 Prompt 2B/2C **完全相同**的固定 Query 集（SHA-256 校验一致：`70603639...`）、相同的 7.13 已保存 raw rewrite/decomposition 输入重新运行 Deterministic Replay：

- 23 个 D 组洪泛 Case 相对 **Stage 7 原始历史基线** 仍 `>=1000` 的从 Prompt 2C 的 **3 条（Q10、Q12、Q48）降到 1 条（仅 Q12）**，远低于"最多 4 条仍 `>=1000`"的 Gate 门槛。
- Full-catalog（3209）保持 **0**（26/26），Q39/Q40/Q42 均未出现 full-catalog。
- **Regression = 0**（Prompt 2C 曾发现的 2 个小幅 regression Q27/Q28 本阶段均进一步下降，未见任何新增或恶化）。
- **Piggyback 修复直接验证**：Q10（1715→740，首次跌破 1000）、Q40 D/C（3→0）、Q48（1155→17，-98.5%）均由 `piggyback_guard_triggered=true` 的行直接确认。
- 校验确认：全部 26 行中，`native_anchored=true` 且 `synthetic_anchors` 非空的行数为 **0**——即"合成/注入锚点绝不能被误判为原生共享锚点"这一硬性条件在固定 Replay 数据上得到验证。
- **第二轮 bindTarget 修正**（避免窄化比较基准被误用为过短的实际绑定文本，导致 relaxed 匹配阈值意外降低）已包含在本次 Replay 使用的代码中——首次（未修正）Replay 曾出现 Q40 D 3→919 等不降反升的现象，修正后已消除。
- **Replay 达到数量 Gate，可以进入 Live Retest**——见第 10 节最终结论。

## 2. Harness Verification

Bundle 已在 Replay 前重新构建（`node build_bundle.cjs`），`lib/searchRewrite.ts` 的 bundle 源哈希由 Prompt 2C 的 `aeb453b4...` 变为本次 `a54aaf9e...`，确认使用当前 Prompt 2D（含 bindTarget 修正）代码，非旧缓存。`page.tsx` 本阶段未修改（哈希与 Prompt 2C 结束时完全一致：`4cb4775f...`），无需更新漂移检测器模式串。漂移检测 8 项全部通过（`missing: 0`）。Harness 逻辑（`engine.cjs`/`scoring.cjs`/`csv_utils.cjs`）未改动，仅新增 `replay_prompt2d.cjs` 作为独立入口，未复制或重写 Guard 逻辑。

## 3. Before vs After

| 指标 | Prompt 2C Replay | Prompt 2D Replay |
|---|---|---|
| 总 Run 数 | 26 | 26 |
| Full-catalog | 0 | 0 |
| D 组仍 `>=1000`（历史基线 23 条对比） | 3（Q10/Q12/Q48） | **1（仅 Q12）** |
| Regression 数 | 2（Q27/Q28，小幅非洪泛） | **0** |
| Human PASS（人工复核） | 4/15 | 5/18 |
| Human FAIL（人工复核） | 1/15 | 2/18（Q12、Q41，均为已知 deferred 结构性限制） |
| Piggyback Guard 触发次数 | N/A（本阶段新增诊断字段） | 20/26 |

**重要提醒**：以上对比是严格 A/B——Replay 使用完全相同的固定 7.13 输入，两次运行之间唯一变量是 `lib/searchRewrite.ts` 代码本身，因此可以做因果归因（不同于 Live retest）。

## 4. Q06/Q10/Q12/Q39/Q40/Q41/Q42/Q47/Q48 Deep Dive

- **Q10**（D，subject "Light and Night"）：1715 → **740**，首次跌破 1000 门槛。3 条候选中 2 条（"Light and Night character design"/"illustration reference"）此前因共享 subject 绑定前原文而绕过绑定，现已确认全部正确绑定为 `"光与夜之恋 Light and Night ..."` 前缀。残留 740 条及 Top-1 不相关结果（"la land" 电影海报）源于目录中"night"标签的广泛重叠，属于 relaxed 匹配阈值/目录标签粒度问题，本阶段范围明确排除。
- **Q40**（D/C，subject "Xiaohongshu post"）：3 → **0**（两种模式）。候选 "Xiaohongshu post template" 此前绕过绑定与 subject 原文共享 "post"，现已正确绑定为 `"小红书 Xiaohongshu post ..."`。0 结果反映该具体绑定短语在目录中的内容空白，而非 Guard 缺陷。
- **Q42 C**（subject "Xiaohongshu cover"）：3 → 3（数量不变），但已确认候选 "Xiaohongshu cover template" 现在正确绑定为 `"小红书 Xiaohongshu cover Xiaohongshu cover template"`。残留碰撞（"one hundred years of solitude cover 1"）是与目录中含通用英文词 "cover" 的无关内容碰撞，非 Guard 绕过，属内容碰撞问题，本阶段范围排除。
- **Q42 D**（无 subject）：0 → 0，`piggyback_guard_triggered=false`——确认此模式从未存在 piggyback 机制（走既有 Option D2 原始锚点绑定路径），不受本阶段修复影响，符合 Implementation 报告第 2 节的根因确认。
- **Q06**：12 → 12（无变化）。Guard N 已在 Prompt 2C 修复且未受本阶段影响；残留问题（Furina 丢弃候选靠"genshin"+"impact"满足 relaxed 阈值）是 Ranking/Matching 结构性限制，明确 deferred。
- **Q12**：1694 → 1694（**逐字节不变**）。本 Query 的 decomposition 无 subject，`piggyback_guard_triggered=false`，`native_anchored=false`——确认本阶段修复设计上不触及此 case。根因仍为 `ceil(n/2)` relaxed 匹配阈值被原有 2 个泛词独立满足，与"松弛"锚点是否加入无关，属 Ranking/Matching 范畴，本阶段禁止修改。
- **Q41**：89 → 89（无变化）。subject "Xiaohongshu" 与原 Query 中的 "Xiaohongshu" 本就同实体，绑定为冗余的 `"小红书 Xiaohongshu"`，从未具有 piggyback 漏洞特征。残留不相关结果源于"小红书"作为品牌词在目录中区分度不足，属 Taxonomy/内容限制，本阶段禁止修改。
- **Q47**：485 → 485（无变化）。已确认全部 3 条候选现在正确绑定为完整的 `"抖音 product card ..."` 前缀（而非此前 Prompt 2C 遗留的绑定到窄锚点 "抖音" 单独），但 Top 结果仍不相关（"Indian anned Space 1" 等），指向 Merge/Ranking 多路径加权问题，本阶段禁止修改。
- **Q48**：1155 → **17**（-98.5%），从洪泛区间直接降至正常范围。Piggyback 修复直接生效：候选此前通过共享 subject 未绑定的"抖音"原文自证，现已正确绑定到更完整的锚点文本。残留碰撞（城市名如"shanghai"/"tokyo"）源于 jieba 对"抖音"分词不稳定（有时切出"抖"单字），是已知 Tokenizer 限制，本阶段禁止修改。

## 5. Full-catalog Regression Check

26/26 行 `full_catalog=false`，包括全部 Q39/Q40/Q42（D+C 模式）——硬性条件满足，无 full-catalog 复发。

## 6. Valid Rewrite Controls

`piggyback_guard_triggered=false` 且计数完全不变的 6 条对照 case（Q11 889、Q12 1694、Q15 177、Q16 735、Q42 D 0、Q46 394）确认修复未误伤未涉及 piggyback 机制的既有合法路径——这些 case 在本阶段代码变更前后逐字节相同，是最直接的"未破坏既有行为"证据。

## 7. Cache and Diagnostics

`hasExecutablePath`/Cache TTL 逻辑本阶段零改动（详见 Implementation 报告第 9 节），5 条新增 Cache 单元测试覆盖 synthetic-only 拒绝、explicit-bound 存活等场景，全部通过。新增诊断字段（`native_anchors`/`inherited_anchors`/`synthetic_anchors`/`piggyback_guard_triggered`/`piggyback_rejection_reason`）已在 Replay CSV 中逐行记录，供 Live retest 阶段复用同一套判读口径。

## 8. Remaining Failures

Human 复核 FAIL 2 条（Q12、Q41），均为**已知、已定位、本阶段明确排除范围**的结构性限制（relaxed 匹配阈值、Taxonomy 区分度），不属于新发现的 Guard 逻辑缺口。未发现任何新的、未被现有分类覆盖的失败模式。

## 9. Limitations

- Replay 是固定输入的因果验证（复用 7.13 已录制的 LLM 输出），不能证明修复对 7.13 数据集之外的措辞同样有效——这正是安排 Limited Live Retest 的原因。
- Q10/Q42 C/Q45 等 case 数量下降但仍非 0，残留结果的不相关性部分来自 relaxed 匹配阈值和目录内容粒度，均已在第 4 节逐条定位根因并确认不在本阶段范围内。
- 首次（未经 bindTarget 修正）Replay 曾观察到 Q40 D 等多个 case 数量不降反升（如 3→919），根因是窄化的比较锚点被同时用作实际绑定文本，缩短了 token 总数进而降低了 `ceil(n/2)` 绝对匹配门槛；已通过拆分 `subject`（比较基准）与新增的 `bindTarget`（实际绑定文本）参数修正，本报告数字为修正后的最终 Replay 结果。

## 10. Final Gate

### **READY_FOR_LIVE_RETEST**

理由：

1. **硬性条件全部满足**：Full-catalog=0（26/26）；Q39/Q40/Q42 均未出现 full-catalog；弱数字属性未作为唯一锚点独立执行；合成/注入锚点未被误判为原生共享锚点（0 例违反）；Regression=0；原始 first-pass 保留；合理 Rewrite 路径未被全面关闭（6 条未涉及 piggyback 的对照 case 逐字节不变）；Production repo 除声明范围外无意外修改（`lib/searchRewrite.ts`、`lib/__tests__/searchRewrite.test.ts` 之外零改动，已核对 git status 与 session 开始前快照完全一致）。
2. **数量阈值大幅超额满足**：23 个 D 组 case 中仅 1 条（Q12）仍 `>=1000`，远低于"最多 4 条"的 Gate 门槛（相当于 22/23 = 95.7% 已降至 1000 以下）。
3. **核心 Piggyback case（Q10/Q40/Q42-with-subject）均已直接验证修复生效**，且未引入新的、未分类的失败模式。
4. 据此进入下一步：**Limited Live Retest**（与 Prompt 3B/2C 完全相同的 20 唯一 Query / 23 次 Run 集合，真实 LLM 调用，进程隔离 Cache 策略）。
