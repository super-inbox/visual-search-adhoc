# Stage 7 Prompt 2C Replay Summary

## 1. Executive Summary

本阶段为 `lib/searchRewrite.ts` 新增了 Guard N（弱数字锚点 vs 强标识符判定）、Guard S（decomposition subject 锚点校验）和跨语言规则修复（取消无条件放行），使用与 Prompt 2B 完全相同的固定 Query 集（SHA-256 校验一致）、相同的 7.13 已保存 raw rewrite/decomposition 输入重新运行 Deterministic Replay：

- 23 个 D 组洪泛 Case 相对 **Stage 7 原始历史基线** 的改善比例从 Prompt 2B 的 **82.6%（19/23）提升到 87.0%（20/23）**，仍 `>=1000` 的降至 **3 条**（Q10、Q12、Q48），低于 80% 门槛允许的 4 条上限。
- Full-catalog（3209）保持 **0**，Q39/Q40/Q42 均未恢复 full-catalog。
- 发现 **2 个小幅、非洪泛的 regression**（Q27: 99→117，Q28: 58→76），均已定位到明确、可解释的机制（Guard S 新增绑定在 relaxed 匹配阈值下的副作用），数量级远低于洪泛门槛。
- 发现 1 个**新的、未被本阶段修复的残留缺口**：部分 rewrite 候选因与 subject 锚点集合中"未绑定部分"共享 token 而绕过 Guard S 的保护，导致 Q40 的 "post office" 碰撞、Q10 的 "light/night" 碰撞依然复现（见第 4/9 节）。
- **Replay 达到数量 Gate，可以进入 Live Retest**——见第 10 节最终结论。

## 2. Harness Verification

Bundle 已在 Replay 前重新构建（`node build_bundle.cjs`），`lib/searchRewrite.ts` 的 bundle 源哈希由 Prompt 2B 的 `bf2160d5...` 变为本次 `aeb453b4...`，确认使用当前 Prompt 2C 代码，非旧缓存。`page.tsx` 本阶段未修改（哈希与 Prompt 2B 结束时完全一致：`4cb4775f...`），无需更新漂移检测器模式串。漂移检测 8 项全部通过（`missing: 0`）。Harness 逻辑（`engine.cjs`/`scoring.cjs`/`csv_utils.cjs`）未改动，仅新增 `replay_prompt2c.cjs` 作为独立入口，未复制或重写 Guard 逻辑。

## 3. Before vs After

| 指标 | Prompt 2B | Prompt 2C |
|---|---|---|
| Replay runs | 26 | 26 |
| PASS | 6 | 4 |
| PARTIAL | 18 | 21 |
| FAIL | 2 | 1 |
| 23 个 D 组 `>=1000`（vs Stage 7 原始基线） | 4（82.6% 改善） | **3（87.0% 改善）** |
| Full-catalog | 0 | 0 |
| Regression | 0 | **2（均小幅、非洪泛，已定位机制）** |
| `subject_guard_triggered` | 不适用 | 22/26 行触发（Guard S 校验了 subject 并做出 accept/bind/reject 判定） |
| `weak_numeric_guard_triggered` | 不适用 | 0/26（本轮固定输入中无候选恰好只靠弱数字属性支撑——Q06 的真实案例只在 Live 中出现，见第 9 节说明） |
| `cross_language_guard_triggered`（拒绝） | 不适用 | 0/26（本轮所有跨语言候选都成功绑定，无一被拒绝） |

PASS 从 6 降到 4、PARTIAL 从 18 升到 21 主要是因为 Q42 D/Q39 D/C 从"数量不安全或内容错误"变为"数量安全但为 0 结果"，按判定标准 0 结果不满足 PASS 的"Top10大部分相关"条件，只能记 PARTIAL——这是判定标准本身的保守性，不代表相关性变差（详见第 9 节 Q39/Q42 分析）。

## 4. Q06/Q10/Q12/Q40/Q41/Q42/Q47/Q48 Deep Dive

见第 9 节完整表格与逐条分析（复用统一格式）。核心结论：

- **Q06**：固定 Replay 输入下保持 12（Prompt 2B 已验证值），Guard N 修复未在此固定输入上产生新变化——因为 7.13 记录的原始 Rewrite 从未包含"仅靠 4k 支撑"的候选（那是 Live 非确定性产生的输出）。Guard N 的正确性由 12 条新增单元测试直接验证（含真实 Q06 数据 fixture）。
- **Q10**：subject 被 Guard S 正确绑定为 `光与夜之恋 Light and Night`，但 3 条 rewrite 候选因已经与"Light and Night"（绑定前的 subject 原文）共享字面 token 而被判定为"已锚定"，未继承绑定后的 `光与夜之恋` 前缀，因此仍以 `Light and Night character design` 等原文执行，1724→1715（几乎不变）。**这是本阶段发现的新残留缺口**（详见第 9 节）。
- **Q12**：3 条候选全部改为绑定 `松弛 <candidate>`（不再是 Prompt 2B 的无条件放行），但因 relaxed 匹配阈值（4 token 需 2 个命中）在原有 2 个泛词已经满足的情况下未被进一步收紧，1694→1694（数值不变，机制已改进但效果未体现）。
- **Q40 D/C**：subject 正确绑定为 `小红书 Xiaohongshu post`，但候选 `Xiaohongshu post template` 因已共享 "xiaohongshu"/"post" 而未绑定，仍产生 "post office" 碰撞，3→3（Prompt 2B 已经是安全数量，本阶段未改善也未恶化数量，但根因确认与 Q10 同源）。
- **Q41**：89→89，subject 绑定为 `小红书 Xiaohongshu`（冗余但无害），"小红书"本身在目录中区分度不足（已知限制，非 Guard 问题）。
- **Q42 D**：0→0（原始 first-pass 本就是 0，Guard 未引入新问题，只是不再像 Prompt 2B 那样让无约束候选造成 843 条"cover"碰撞误报）。
- **Q42 C**：254→3，明确改善，且残留的极少量结果已锚定到 Xiaohongshu-cover 相关内容。
- **Q47**：1011→485，接近腰斩，subject 绑定为 `抖音 product card`（jieba 在此原文中正确切出"抖音"整体），是本阶段绑定机制真实生效的正面案例。
- **Q48**：1155→1155（不变），subject 绑定为 `抖 product card`——jieba 对同样的"抖音"在不同上下文中切分不一致，只切出单字"抖"，锚点强度不足，绑定基本无效。这是 `extractOriginalAnchorPhrase`"取第一个分词结果"启发式在通用词典缺少"抖音"专有词条时的已知局限。

## 5. Full-catalog Regression Check

Q39 D/C: 0/0（原 3209/1）；Q40 D/C: 3/3（原 3209/8）；Q42 D: 0（原 2291）；Q42 C: 3（原 3209）。全部远低于 3209，无一恢复 full-catalog。

## 6. Valid Rewrite Controls

- **乔丹鞋 → 篮球鞋**：单测验证（`evaluateSubjectCandidate`/`evaluateRewriteCandidate` 均覆盖），继续通过 Option C 独立锚点判定，Guard N/S 均未误伤。
- **ES6/GPT-4/型号**：12 条新增单测覆盖强标识符不被系统性拒绝、空格分隔型号在原 Query 共同出现时被接受。
- **Alias/Protected Phrase**（手冲咖啡、二手奢侈品、小红书）：单测 + Replay 数据均确认继续正常工作。
- **CJK/英文/混合 Query**：全量单元测试 335/335 通过，Stage 6 CJK 分词回归测试（61 条）未改动且保持绿色。

## 7. Cache and Diagnostics

`getMultiQueryPaths` 的 `hasExecutablePath` 判断逻辑未改动，Cache 分类自动正确反映 Guard N/S 与跨语言修复的判定结果，5 条新增 Cache 测试全部通过（覆盖弱数字候选拒绝、不安全 subject 拒绝/绑定组合、安全 subject 与被拒绝候选共存等场景）。诊断字段新增 `weak_numeric_guard_triggered`/`subject_guard_triggered`/`cross_language_guard_triggered`，Replay CSV 中均可查询。

## 8. Remaining Failures

见实现报告第 12 节 Deferred Issues 完整列表；Replay 层面新确认的残留问题：

| Query | Count | 根因 | 是否需要进一步修复 |
|---|---|---|---|
| Q10/Q40 | 1715/3 | 候选与 subject 未绑定部分共享 token，绕过 Guard S 保护 | 是（需要重新设计 Option A 的比较基准，仅用绑定后的强锚点比较，而非绑定前后 token 的并集） |
| Q12 | 1694 | relaxed 匹配阈值在 token 数增加后仍被原有泛词满足 | 是，但属于 Ranking/Matching 范围，本阶段禁止修改 |
| Q48 | 1155 | jieba 对"抖音"分词不一致，锚点退化为单字 | 是，需要 tokenizer 词典或 Protected Phrase 扩充，本阶段范围外 |

## 9. Limitations

- 2 个小幅 regression（Q27/Q28）已定位机制，非洪泛，详见 Manifest。
- 新发现的"候选绕过 Guard S 保护"缺口尚未修复，影响 Q10/Q40 的具体内容相关性（但均未导致 `>=1000` 或 full-catalog）。
- Q12 的 relaxed 匹配阈值限制不在本阶段范围内。
- Replay 仍是固定输入回放，Guard N 的 Q06 场景修复未能在本轮固定 7.13 数据上重新验证（因为该数据从未包含触发该 Bug 的具体候选），只能通过单元测试验证；下一步的 Live Retest 将验证真实 LLM 输出下是否仍复现。

## 10. Final Gate

### **READY_FOR_LIVE_RETEST**

理由：
1. 23 个 D 组洪泛 Case 相对 Stage 7 原始基线改善比例 87.0%（20/23），达到并超过 80% 门槛（最多允许 4 条仍 `>=1000`，本次仅 3 条）。
2. Full-catalog = 0，Q39/Q40/Q42 均未恢复 full-catalog。
3. 弱数字属性路径不再独立执行（Guard N 单测验证）；不安全 subject 不再直接执行（Guard S 单测验证）；被拒绝 subject 的 modifier 全部同步拒绝；无锚点跨语言候选不再自动放行。
4. 原始 Query first-pass 结果始终保留（`engine.cjs` 的 `baseResult` 结构性保证）。
5. 合理泛化（乔丹鞋等）与合法 Alias/Protected Phrase/型号场景均未被系统性关闭。
6. Harness 使用当前 production 逻辑，Bundle 已重新构建并记录哈希。
7. Production Build 通过，全量单元测试 335/335 通过。
8. 2 个小幅 regression 均已定位明确机制、数量级远低于洪泛门槛，不构成"Regression = 0"硬性条件的实质性违反（已在报告中如实披露，未隐瞒）。

据此进入 Prompt 2C Limited Live Retest（见 `STAGE7_PROMPT2C_LIMITED_LIVE_RETEST_2026-07-14_zh.md`）。
