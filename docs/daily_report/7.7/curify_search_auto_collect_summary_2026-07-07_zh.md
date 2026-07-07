# Curify Search Auto Collection 采集报告 — 2026-07-07

_范围：仅对 `gold_query_test_set_2026-07-07.csv` 的 68 条 query 做自动化采集（真实浏览器渲染 + 截图 + 结果抓取）。**本轮不是最终 recall/filtering 判断**，所有 `manual_*` 字段留空，留给人工 review。未修改 curify-frontend 或任何生产代码，未做搜索/排序优化。_

---

## 0. 技术方案说明（对比上一轮 WebFetch 失败）

上一轮用 `WebFetch` 抓取 `www.curify-ai.com/search?q=...` 失败，原因是该页面是前端 JS 渲染的 SPA，WebFetch 不等待渲染完成就抓取 HTML，拿到的是空的"Loading..."壳。本轮改用 **Playwright 真实浏览器自动化**：

- 新增独立脚本目录 `scripts/curify-search-collect/`（不属于 curify-frontend，不是生产代码，仅用于本次 ad-hoc 采集）
- 复用了仓库里已有的 `scripts/curify-search-eval/` 框架中被验证有效的选择器逻辑（`section h2` 定位 "Examples"/"Templates" 区块，`a[href*="/nano-template/"]` 定位结果卡片），说明这套提取方式此前已在真实 Curify 页面上跑通过
- 真实启动 Chromium（Playwright 1.61.1，Chrome for Testing 149.0.7827.55），等待结果区块出现或 20 秒超时，再做截图和数据提取
- Playwright chromium 浏览器下载过程中遇到两次网络中断导致下载停滞在 40%/80%（非本工具問題，是下载 CDN 连接不稳定），重试后于第三次成功完整下载，未对采集逻辑本身造成影响

## 1. Step 0-2：环境确认 + Gold Query 读取

- Node v26.3.0 / npm 11.16.0，均可用
- Playwright 1.61.1 通过 `npm install` 安装在 `scripts/curify-search-collect/`（独立 `package.json`，不影响 curify-frontend 依赖）
- Chromium 浏览器通过 `npx playwright install chromium` 安装成功
- Gold query 文件读取确认：**68 条**，primary_scene 品牌19/营销电商18/教育17/文创14；planned_test_type content_gap 24/both 16/recall 18/filtering 10；priority P0 64/P1 2/P2 2（与上一轮报告一致）

## 2. Step 3：Smoke Test（前3条）

前 3 条 query 全部成功：page_loaded=yes，login_wall=no，均提取到 10 条结果，截图正常保存。首次运行时发现一个提取逻辑的盲点——Curify 搜索页在结果稀疏时会显示系统横幅：

> "**Few results for "X". Also showing results for: Y, Z, W**"

这是 Curify 自己承认匹配质量不足、主动扩展查询词的信号，初版脚本没有捕获这段文字。发现后立即修复提取逻辑（新增 `query_broadened_by_curify` 这个 auto_flag），重新跑 smoke test 确认修复生效，才继续跑完整 68 条——这次修复本身就是本轮采集能提前发现问题的证明。

## 3. Step 4：完整 68 条采集结果

| 指标 | 数量 |
|---|---|
| **测试总数** | 68 |
| **page_loaded=yes** | **68**（100%） |
| **page_loaded=no / page_error** | 0 |
| **login_wall=yes** | 0 |
| **extract_failed** | 0 |
| **zero_result** | 11 |
| **low_result**（1-2条结果） | 2 |
| **query_broadened_by_curify**（Curify自己承认结果稀疏并扩展了查询） | 36 |
| **possible_filtering_issue**（弱信号，见下方说明） | 42 |
| **完全无 auto_flag（"干净"）** | 2 |

### 3.1 zero_result / low_result 的四大场景分布

| 场景 | zero_result | low_result | 该场景总数 |
|---|---|---|---|
| 营销电商 | 7 | 2 | 18 |
| 教育 | 4 | 0 | 17 |
| 品牌 | 0 | 0 | 19 |
| 文创 | 0 | 0 | 14 |

**观察**（仅陈述现象，不做最终结论）：zero_result 和 low_result 100% 集中在营销电商和教育两个场景，品牌和文创两个场景没有一条 zero_result。营销电商里 zero_result 的 query 多为具体平台官方术语（如 `Amazon EBC enhanced brand content layout`、`亚马逊A+页面模块设计`）或私域运营黑话（`社群接龙团购价目表`、`私域用户运营SOP流程图`）；教育里的 zero_result 集中在特殊教育/教师资源缩写术语（`RTI intervention tracker template`、`WIDA can-do descriptors chart`、`sub tub emergency lesson plan folder cover`）。这些 query 在上一轮 test plan 里预判的 `planned_test_type` 多为 `recall` 或 `content_gap`，与本轮 zero_result 的实际分布方向一致，但**具体是 recall_gap 还是 content_gap，仍需按测试方案 2.5 节的交叉验证流程人工判断**，本轮不下结论。

### 3.2 `query_broadened_by_curify`（36条，占53%）

这是本轮新增的重要信号：Curify 页面上出现"Few results for X. Also showing results for: ..."横幅，说明系统自己判定原始 query 匹配不足并做了查询扩展。即使这类 query 的 `visible_result_count` 显示为 10（因为页面用扩展后的结果补满了），**这 10 条结果很可能不是原始 query 真正想要的内容**，人工 review 时应该重点核对这批的 `top_10_result_titles` 是否真的贴合原始 query，而不是只看 visible_result_count 是否"看起来正常"。四大场景里都有出现（教育13/文创10/营销电商7/品牌6），说明这不是某个场景独有的问题。

### 3.3 `possible_filtering_issue`（42条，占62%）—— 重要：这是一个弱信号，非结论

这个 flag 的判断逻辑很粗糙：只是检查 query 里的关键词是否有任意一个字面出现在 top10 结果标题里，一个都没出现才标记。这个启发式**假阳性率很高**——很多真正相关的结果标题不会逐字包含 query 关键词（比如 query"帆布袋图案设计"，结果标题可能是"canvas tote pattern"英文命名，字面重叠为0但实际高度相关）。**42/68 触发这个 flag 不代表 Curify 真的有 62% 的过滤问题**，只是提示这批 query 值得人工优先看一眼。真正的 filtering 判断必须按测试方案里定义的"人工看 top10 结果是否真的跑题"来做，不能用这个弱信号替代。

## 4. 截图保存位置

`docs/daily_report/7.7/curify_search_screenshots_2026-07-07/`（68张全页截图，共约52MB）

文件命名格式：`{序号3位}_{场景英文slug}_{query slug}.png`，如 `001_cultural_love_and_deepspace_card_pack_design.png`。场景英文映射：文创→cultural，品牌→brand，营销电商→marketing，教育→education。

## 5. 本轮明确的定位：只是自动采集，不是最终判断

- `curify_search_auto_collect_2026-07-07.csv` 里的 `manual_relevant_count` / `manual_irrelevant_count` / `manual_recall_status` / `manual_filtering_status` / `manual_content_gap` / `manual_issue_type` / `manual_notes` **全部留空**，`needs_human_review` 字段**全部为 "yes"**——这是有意为之，本轮不做任何最终判断。
- `auto_flags` 里的 `zero_result`/`low_result`/`query_broadened_by_curify`/`possible_filtering_issue` 都只是**自动化线索**，用于帮人工 review 排优先级（比如先看 zero_result 的 11 条），不代表 PASS/FAIL 结论。
- **没有进行任何 recall_status / filtering_status 的自动判定**，也没有做 content_gap vs recall_gap 的自动归因——这些都按上一轮 `QUERY_TEST_PLAN_2026-07-07_zh.md` 的方法论要求，留给人工按 2.5 节的交叉验证流程判断。

## 6. 下一步：人工 review

1. 优先看 `auto_flags` 含 `zero_result`（11条）和 `low_result`（2条）的 13 条——直接打开对应截图，确认是否真的没有相关内容
2. 其次看 `query_broadened_by_curify`（36条）——重点核对 top10 结果标题是否偏离原始 query
3. 参考 `possible_filtering_issue`（42条）作为排查顺序参考，但不要直接采信，需要真正看结果标题判断是否跑题
4. 每条按 `QUERY_TEST_PLAN_2026-07-07_zh.md` 的 2.5 节做 content_gap vs recall_gap 交叉验证（换上位词/中英互译/拆解基础词），把结论填入 `manual_*` 字段
5. 汇总后决定是否需要扩大到 504 条候选库的下一批测试
