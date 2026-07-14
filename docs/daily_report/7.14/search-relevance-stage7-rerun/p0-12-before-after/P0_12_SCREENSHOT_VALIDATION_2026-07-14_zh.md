# P0 12 Screenshot Validation — 2026-07-14

## 1. Executive Summary

固定 12 个 P0 Query 全部定位（来源：`docs/daily_report/7.9/manual_review/external_screenshot_queries_12_2026-07-09.csv`），全部确认属于 68 条 Hard Query 子集。12 条 Before 截图（来自 `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/`，production 实时抓取，2026-07-07）全部存在且有效。12 条 After 截图（本阶段使用当前 Stage 7 验收通过的 production 工作区，本地 dev server，2026-07-14 采集）全部成功生成，每条含完整页面与 Top Results 区域两张，共 24 张新截图。

人工逐条判定（基于实际截图内容重新判读，而非直接照搬 Stage 7 标签）：**PASS=0, PARTIAL=5, FAIL=7, NOT_COMPARABLE=0**。

可作为项目负责人汇报"部分改善证据"的有 3 条（P0_05 小红书香薰、P0_06 国风茶包装、P0_09 Genshin Furina）——均为真实、可见的相关性改善，但**均未达到"完全修复"**，改善点与剩余问题已在报告中逐条列明。其余 9 条应作为"剩余限制证据"或不建议用于展示改善，其中根因分布为目录内容缺口（多数）、错误实体（1 条）、匹配阈值限制（1 条）。

**未发现夸大改善或掩盖失败的情况。**

## 2. Authority and Scope

- 权威 12 P0 来源：`docs/daily_report/7.9/manual_review/external_screenshot_queries_12_2026-07-09.csv`——未搜索到与之冲突的第二份"12 P0"清单（68 条 Baseline 内部的 `priority` 列标注 64 条为"P0"，是不同的、更宽泛的业务优先级概念，已明确区分，未误用）。
- 12/12 Query 精确匹配到 68 条子集（Q02/Q06/Q09/Q10/Q15/Q16/Q34/Q46/Q53/Q60/Q64/Q68）。
- 未替换任何 Query，未修正拼写/空格/标点/语言，未删除表现差的 Case，未新增第 13 条。

## 3. Environment

| 项目 | Before | After |
|---|---|---|
| Branch | N/A（历史生产环境） | `baobao/search-relevance-phrase-alias-2026-07-09` |
| HEAD | N/A | `c062e618bce4044bedf718aadf59ff69f0999344` |
| 环境 | 真实生产 `https://www.curify-ai.com`（Playwright headless Chromium） | 本地 Next.js dev server（`localhost:3417`），运行当前未修改的 production 工作区，`NEXT_PUBLIC_ENV=production`，连接真实生产数据库/API |
| Locale | English（UI 切换按钮高亮 English） | `en-US`（`NEXT_LOCALE=en`，默认 locale） |
| Viewport | 1440px 宽（完整页面截图，高度按内容自适应） | 1440x900，deviceScaleFactor=1 |
| 采集日期 | 2026-07-07 | 2026-07-14 |
| Catalog | 与 7.13/7.14 Stage 7 一致（3209 条，同一份 `nano_inspiration.json`） | 同左 |

**Before/After 环境差异**：Before 是对真实线上生产站点的抓取，After 是对当前 production 工作区本地 dev server 的抓取——分支/HEAD/代码库完全一致，但物理请求路径不同（本地服务器 vs 线上 CDN/服务器），不构成像素级完全一致，已如实披露，不声称完全一致。本地 dev 环境左下角出现的红色数字徽章（如"1 Issue"）为 Next.js 开发模式专属浮层，生产环境不会出现，非产品缺陷、非敏感信息。

## 4. File Completeness

```text
P0 Query = 12/12
Before Full = 12/12
Before Top = 0/12（Before 只有单张完整页面截图，7.7 采集时未生成单独的 Top Results 裁剪图，如实记录为 NOT_AVAILABLE，未伪造）
After Full = 12/12
After Top = 12/12
Comparable Cases = 12/12
```

## 5. Case-by-case Review

| P0 ID | Query ID | Query | Before Count | After Count | Stage7 Label | 本阶段人工判定 | 改善点 | 剩余问题 |
|---|---|---|---:|---:|---|---|---|---|
| P0_01 | Q02 | NCT Dream photocard template | 10 | 945 | FAIL | **FAIL** | 无 | 错误实体（ILLIT 组合替代 NCT Dream）在实时截图中原样重现 |
| P0_02 | Q64 | maker space label set printable | 10 | 109 | FAIL | **FAIL** | 无 | Top Results（咖啡机/蝴蝶/柠檬/蘑菇/健康习惯）与查询完全无关 |
| P0_03 | Q16 | Y2K chrome skincare launch poster | 10 | 446 | FAIL | **FAIL** | 无 | Top Results（袜子/耳机/夹克/问题解决模板）与查询完全无关 |
| P0_04 | Q15 | K-beauty glass skin brand launch visual | 10 | 331 | FAIL | **FAIL** | 无 | Top Results（母婴品牌/春日美妆节/眼罩）与查询完全无关 |
| P0_05 | Q46 | 小红书香薰产品种草图 | 4 | 6（Stage7 harness）/ 本次实时截图 count 更高 | PASS | **PARTIAL** | 前 3 条真实香薰相关（扩香器/卧室/香薰角落），相比 Baseline 完全不相关的眼罩/乐器/吊坠有明确可见改善 | 本次实时截图比 Stage 7 harness 记录的干净 6 条结果多出更多洪泛尾部（受 LLM 非确定性影响，同一 production 代码路径下独立调用结果不同） |
| P0_06 | Q09 | 低饱和国风茶包装设计 | 10 | 94 | PARTIAL | **PARTIAL** | 前 4 条真实茶相关（熊猫茶师/抹茶粉/暖冬茶/奶茶店），相比 Baseline 完全不相关的燕麦/饼干/意面酱有明确可见改善 | "国风"/"低饱和"细节未确认，尾部仍洪泛（西安肉夹馍/paella/羊角包） |
| P0_07 | Q68 | zones of regulation poster classroom | 10 | 70 | PARTIAL | **PARTIAL** | 出现一条弱相关条目（"Traits of Emotional Stability"） | 核心"情绪分区"教具意图仍未命中，与 Baseline 质量基本持平 |
| P0_08 | Q60 | coding unplugged activity cards | 10 | 0 | PARTIAL | **FAIL** | 无 | 0 结果，仅展示泛类目浏览入口，对用户不可用 |
| P0_09 | Q06 | genshin impact Furina fanart wallpaper 4k | 6 | 12 | PARTIAL | **PARTIAL** | Top 8/12 为真实 Genshin Impact 内容（含 Fontaine 地区角色组，Furina 正是该地区角色），相比 Baseline 完全不相关的吉卜力电影有明确可见改善 | 未确认"Furina"角色本身或"wallpaper 4k"格式的精确匹配 |
| P0_10 | Q34 | Amazon EBC enhanced brand content layout | 0 | 6 | PARTIAL | **PARTIAL** | 从 0 到 3 条方向性相关的亚马逊消费电子类结果 | 未确认"EBC 加强品牌内容布局"模板格式本身 |
| P0_11 | Q53 | IEP accommodations checklist visual | 3 | 0 | PARTIAL | **FAIL** | 无 | 0 结果，对用户不可用 |
| P0_12 | Q10 | 光与夜之恋 卡面设计参考图 | 10 | 1324 | FAIL | **FAIL** | 无 | 已知、此前已记录的通用词（"night"/"love"）relaxed 匹配阈值碰撞，本阶段范围外 |

**说明**：`Stage7 Label` 列取自 Stage 7 Prompt 5 独立复核的 `verified_stage7_label`（基于该阶段 harness 批量运行的记录结果）；`本阶段人工判定` 列基于本次实际截图内容重新判读——两者存在 2 处差异（P0_05：PASS→PARTIAL；P0_08、P0_11：PARTIAL→FAIL），差异原因已在对应行说明，不隐藏、不掩饰。

## 6. PASS Cases

**无。** 本次 12 条实时截图复核中没有任何一条达到 PASS 标准（Top Results 大部分明显相关且无明显剩余问题）。

## 7. PARTIAL Cases

- **P0_05（小红书香薰产品种草图）**：真实改善但非完全修复，Top 3 相关，尾部仍洪泛。
- **P0_06（低饱和国风茶包装设计）**：真实改善但非完全修复，Top 4 相关，尾部仍洪泛。
- **P0_07（zones of regulation poster classroom）**：仅边际变化，核心意图仍未命中，不构成有意义改善。
- **P0_09（genshin impact Furina fanart wallpaper 4k）**：真实改善但非完全修复，正确圈定 fandom/地区，但精确角色/格式未确认。
- **P0_10（Amazon EBC enhanced brand content layout）**：从 0 到方向性相关的少量结果，格式本身未确认。

以上 5 条均**不得**描述为"已解决"或"完全修复"。

## 8. FAIL Cases

- **P0_01（NCT Dream photocard template）**：错误实体（ILLIT），未改善。
- **P0_02（maker space label set printable）**：目录缺口，Top Results 完全无关。
- **P0_03（Y2K chrome skincare launch poster）**：目录缺口，Top Results 完全无关。
- **P0_04（K-beauty glass skin brand launch visual）**：目录缺口，Top Results 完全无关。
- **P0_08（coding unplugged activity cards）**：0 结果，对用户不可用。
- **P0_11（IEP accommodations checklist visual）**：0 结果，对用户不可用。
- **P0_12（光与夜之恋 卡面设计参考图）**：已知 Matching Threshold 限制导致的结果洪泛。

以上 7 条不得在项目负责人汇报中描述为已改善，也不得隐藏。

## 9. NOT_COMPARABLE Cases

无。全部 12 条 Before/After 均可比较（Before 有效存在，Query 完全一致，环境差异已在 §3 披露但不构成"不可比较"）。

## 10. Evidence for Project Report

```text
可以作为成功证据（SUCCESS_EVIDENCE）：无
可以作为部分改善证据（PARTIAL_EVIDENCE）：P0_05, P0_06, P0_09（须附带明确限制说明，不得单独展示为"已解决"）
可以作为剩余问题证据（LIMITATION_EVIDENCE）：P0_01, P0_02, P0_03, P0_04, P0_07, P0_08, P0_10, P0_11, P0_12
不建议使用（DO_NOT_USE）：无（以上 9 条均可作为限制证据使用，只是不适合作为改善证据）
```

## 11. Remaining Limitations

- **Catalog / Content**：P0_02/P0_03/P0_04/P0_08/P0_11（及 P0_06/P0_09/P0_10 的垂直细节部分）——目录本身未收录对应内容或格式，检索机制无法制造未被创作的内容。
- **Taxonomy**：P0_07——情绪分区教具类目覆盖不足。
- **Tokenizer**：本 12 条中无直接证据（Tokenizer 精度问题主要出现在 68 条集合的其他 Query，如 Q24/Q41/Q47，不在本 12 条 P0 内）。
- **Matching Threshold**：P0_12——已知的通用词 relaxed 阈值碰撞，此前已记录，本阶段范围外。
- **Wrong Entity**：P0_01——NCT Dream 被泛化匹配到错误的 k-pop 组合 ILLIT。
- **Screenshot comparability**：Before 为线上生产环境抓取，After 为本地 dev server 抓取（同一 branch/HEAD/代码），非像素级同一请求路径；本地 dev 模式徽章为环境专属浮层。
- **数据版本限制**：C/D 模式改写为真实独立 LLM 调用，本次实时截图结果与 Stage 7 harness 批量记录的结果在数量/排序上可能有非确定性差异（P0_05 即为典型案例），两者共享同一 production 代码路径，差异不代表代码回归。

## 12. Final Conclusion

```text
12 个 P0 Before / After 是否完成: 是（12/12 完成，含完整页面+Top Results 双截图）
项目负责人要求的截图交付是否完整: 是
可以声称修复多少条: 0 条（无 PASS，不得声称"已修复"）
只能声称部分改善多少条: 3 条（P0_05, P0_06, P0_09，均需附带限制说明）
仍未改善多少条: 7 条（P0_01, P0_02, P0_03, P0_04, P0_08, P0_11, P0_12）
不可比较多少条: 0 条
```
