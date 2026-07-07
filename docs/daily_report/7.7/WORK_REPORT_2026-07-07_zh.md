# Curify Query/Carry Expansion & Search Auto-Collection Work Report — 2026-07-07

## 1. 背景与要求

今日要求不是单纯把 query list 扩长，而是一条完整链路：

1. 围绕「文创 / 品牌 / 营销电商 / 教育」四大业务场景，把 query/carry 库从原有的 58 条系统性扩展为分层的候选库；
2. 用扩展出来的 query 去实际测试 Curify 搜索，而不是只停留在候选词表阶段；
3. 测试重点是 **recall**（应该出现的内容有没有被搜出来）和 **filtering**（明显无关内容有没有混进来）；
4. **ranking 暂时不是本轮重点**——候选池质量没过关之前谈排序没有意义；
5. 后续要在人工 review 的基础上，进一步区分 **content gap（内容库没有）/ recall gap（搜索没召回到）/ filtering issue（召回了但掺了无关内容）**，并用这个判断结果去指导具体的 content drop（该建什么内容）和搜索优化方向。

今天的工作对应这条链路的前两段：**query/carry 库分层建设** + **第一轮 Curify 搜索自动采集**。人工 review 和最终归因判断留到下一步。

## 2. 今日完成内容概览

- 完成 query/carry library 的分层整理，形成从"原始种子"到"高信号压力测试候选"再到"基础积木词"的完整层级结构
- 基于四大场景生成并扩展至 **504 条** high-signal / niche / stress-test query 候选池
- 新增 **328 个** simple head term 基础词库，作为后续继续组合生长 query 的原材料
- 从 504 条候选池中筛出第一批 **68 条 gold test set**，覆盖四大场景，兼顾高优先级与小众/长尾/黑话类型
- 设计了 recall / filtering 的判断标准和记录字段，并明确说明本阶段为什么不做 ranking
- 用 **Playwright 真实浏览器自动化**完成 68 条 query 的 Curify 搜索采集（标题、链接、标签、结果数、截图）
- 产出结构化 CSV、raw JSON、68 张全页截图作为人工 review 的证据材料
- **全程未修改 curify-frontend 或任何生产代码**
- **全程未做最终人工 PASS/FAIL 判断**——所有 `manual_*` 字段留空，等人工 review

## 3. Query/Carry Library 文件分类

| 文件 | 数量 | 作用 | 来源/生成方式 | 后续用途 |
|---|---|---|---|---|
| `01_original_58_query_scene_classification_2026-07-07.csv` | 58 条 query | 原始 58 个种子 query 按四大场景分类的基线 | 人工基于原始 tier1/intent 标注重新映射到四大场景 | 作为整条 query 扩展链路的起点，用于追溯扩展逻辑 |
| `02_expanded_from_58_query_candidates_2026-07-07.csv` | 188 条 | 对原 58 条做长尾扩写（同一 seed 的更具体变体） | 结合 Google/Bing/Pinterest/Canva 已采集的真实标签做具体化改写 | 验证"已知 query 能否问得更细"这一维度 |
| `03_net_new_scenario_seed_queries_2026-07-07.csv` | 98 条 | 不绑定原 58 条、直接从四大业务场景设计的全新种子 query | 人工基于行业/机构穷举法设计，重点补齐原 58 条完全缺失的品牌场景 | 补全 query 库的场景广度骨架，尤其是品牌场景 |
| `04_high_signal_niche_query_candidates_500_2026-07-07.csv` | 504 条 | 高信号/小众/长尾的 stress-test query 候选池（含旧版 127 条已并入并统一编号） | 基于竞品平台真实内容形态、圈层黑话、趋势热词设计，专门用于暴露 Curify 的召回/过滤短板 | **本轮 gold test set 的唯一来源**，后续所有 Curify 回测都从这里挑 |
| `05_simple_head_term_seed_bank_2026-07-07.csv` | 328 个 | 简单基础词（对象/材料/风格/场景/行业/格式/受众/节日/商品品类/动作） | 人工梳理的积木式基础词，每个词配 2-3 个组合扩展示例 | 

> 注意：文件 05（simple head term）本质上是词根库，不是可以直接拿去测 Curify 的 query，这一点在本轮及后续回测中都需要严格区分，避免误把基础词当成完整 query 送测。

## 4. Gold Test Set 筛选

**输出文件**：`gold_query_test_set_2026-07-07.csv`（**68 条**）

**为什么不是直接测全部 504 条**：504 条一次性全测的人工审核成本过高——每条 query 至少要看 10 条搜索结果做相关性判断，必要时还要跑替代 query 做 content_gap 交叉验证。先用规模适中的一批验证"用 priority/confidence/niche_signal 预判风险"这套方法论是否可靠，再决定是否值得把全部 504 条测完。

**筛选标准**：
- `priority=P0` 优先（504 条候选池中 P0 且 `keep_or_review=keep` 的有 105 条，是主要来源）
- `keep_or_review=keep` 优先，同一 `subdomain` 最多选 5 条以保证子领域覆盖广度
- 四大场景均要覆盖，按各场景在 P0&keep 池中的体量分配名额
- 人工额外补选 4 条优先级不高但信号极端的边界样本（圈层黑话、冷门服务品类等），专门用于撑开"content_gap vs recall_gap"判断方法论的边界

**68 条的四大场景分布**：品牌 19 / 营销电商 18 / 教育 17 / 文创 14

**68 条的 planned_test_type 预判分布**：content_gap 24 / recall 18 / both 16 / filtering 10

## 5. 测试方法设计

**测试重点**（明确要求）：
- **recall**：前10个搜索结果里，应该出现的相关内容有没有被搜出来
- **filtering**：前10个搜索结果里，明显无关的内容有没有混进来
- **ranking**：本阶段暂缓——候选池召回/过滤质量未验证清楚之前，排序优化没有意义，且分级相关性标注成本远高于二元判断

**自动采集字段**（本轮已完成，机器可判定的部分）：
`visible_result_count`、`top_10_result_titles`、`top_10_result_links`、`top_10_result_tags_or_labels`、`top_10_result_types`、`no_result_text`、`screenshot_path`、`auto_flags`

**留给人工 review 的字段**（本轮全部留空）：
`manual_relevant_count`、`manual_irrelevant_count`、`manual_recall_status`、`manual_filtering_status`、`manual_content_gap`、`manual_issue_type`、`manual_notes`

## 6. Curify Search Auto Collection 结果

**技术路线变更**：最初尝试用 WebFetch 抓取 Curify 搜索页失败——Curify 搜索页是前端 JS 渲染的 SPA，WebFetch 不等待渲染完成就抓取 HTML，拿到的是空的"Loading..."壳，数据不可信。随后改用 **Playwright 真实浏览器自动化**（新增 `scripts/curify-search-collect/`，独立于 curify-frontend 的 ad-hoc 脚本），先做 3 条 smoke test 验证可靠后，再跑完整 68 条。

**采集结果**：

| 指标 | 数量 |
|---|---|
| 测试总数 | 68 |
| page_loaded=yes | **68/68（100%）** |
| login_wall=yes | **0** |
| extract_failed | **0** |
| page_error | **0** |
| zero_result | **11**（营销电商7 / 教育4） |
| low_result（1-2条结果） | **2**（均在营销电商） |
| query_broadened_by_curify（Curify自己判定结果稀疏并扩展了查询） | **36**（文创10 / 品牌6 / 营销电商7 / 教育13） |
| possible_filtering_issue（**弱信号，非结论**，见下节说明） | **42**（文创8 / 品牌14 / 营销电商10 / 教育10） |

**输出文件**：
- `curify_search_auto_collect_2026-07-07.csv`（68条，`manual_*` 字段全部留空）
- `curify_search_auto_collect_raw_2026-07-07.json`（68条原始采集数据）
- `curify_search_screenshots_2026-07-07/`（**68张**全页截图，共约 **52MB**）

## 7. 初步观察，但不下最终结论

自动采集暴露了几个**需要人工 review 优先关注**的方向：

- **zero_result 的 11 条样本**：集中在营销电商（Amazon平台官方术语类、私域运营黑话类）和教育（特殊教育/教师资源缩写术语类），品牌和文创两个场景零 zero_result
- **low_result 的 2 条样本**：均在营销电商
- **query_broadened_by_curify 的 36 条样本**：Curify 页面自己显示"Few results for X, also showing results for..."横幅，说明系统判定原始 query 匹配不足并做了扩展，即使 `visible_result_count` 显示为10，也可能是扩展后的填充结果而非真正匹配
- **possible_filtering_issue 的 42 条样本**：仅供人工排查优先级参考，**这个 flag 的判断逻辑只是粗糙的关键词字面重叠检测，假阳性率很高**（比如中文query配英文命名的结果标题，字面重叠为0但可能实际相关）

**明确不下的结论**：本轮**没有**、也**不应该**得出"Curify 有多少条 recall fail"或"Curify 有多少条 filtering fail"这类结论——这些判断必须建立在人工看过 68 张截图和 top10 结果标题、并按 content_gap vs recall_gap 交叉验证流程逐条核实之后，本轮只是把证据材料准备齐全。

## 8. 后续还需要做什么

1. 人工 review 68 条截图和 top 10 results，逐条核实自动采集的 flag 是否成立
2. 优先 review zero_result（11条）/ low_result（2条）/ query_broadened_by_curify（36条）三类样本
3. 填写 `manual_*` 字段（相关/不相关结果数、recall_status、filtering_status、content_gap、issue_type、notes）
4. 对每条结果不理想的 query，按上位词泛化 / 中英互译 / 拆解基础词三种方式做交叉验证，区分是 content_gap（内容库没有）、recall_gap（内容有但没搜到）还是 filtering_issue（搜到了但掺了无关内容）
5. 汇总 68 条的人工判断结果，生成 issue summary
6. 基于 content_gap 的归因结果，制定具体的 content drop 计划（明确要新建哪些内容类型/主题）
7. 针对 recall_gap 和 filtering_issue，推动对应的搜索/同义词映射优化，优化后再回测验证

## 9. 本轮没有做什么

- ❌ 没有修改 `curify-frontend` 任何生产代码或搜索逻辑
- ❌ 没有修改任何生产代码
- ❌ 没有测试全部 504 条候选，仅完成 68 条 gold test set 的采集
- ❌ 没有做 ranking 优化，也没有设计 ranking 评估方案
- ❌ 没有自动给出最终 recall_status / filtering_status 的 PASS/FAIL 判断，`manual_*` 字段全部留空
- ❌ 没有把 `possible_filtering_issue` 这个弱启发式信号当成最终判断，它只是排查优先级参考
