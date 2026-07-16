# Search → Click → Generate 数据审计 · 执行摘要

审计仓库：`curify-studio` @ `7b3fa5b40b03da3056536257ead2200dab031247`（`main` 分支）
审计方式：严格只读静态代码审查，未执行任何 SQL，未连接生产数据库，未修改任何文件。

---

## 1. 当前搜索数据在哪里？

`curify-studio` 本身是后端/运维 monorepo（FastAPI 后端 `curify_background/` + 静态管理后台 `admin_portal/`），并不是渲染 `/search` 页面的前端应用（前端在独立的 `curify-frontend` 仓库中，不在本次审计范围内，仅作为辅助佐证引用并明确标注）。

在 `curify-studio` 内部，**没有独立的 `search_logs`/`search_history` 表**。所有搜索行为都写入一张通用事件表 **`user_interactions`**（定义于 `curify_background/app/models/interactions.py`），通过 `action_type` 字段区分是否为搜索事件（`SEARCH` / `SEARCH_NORESULT` / `SEARCH_LOWRESULT`），查询原文本身被塞进通用的 `content_id` 字符串列，而不是独立的 `query`/`search_id` 列。写入通过唯一入口 `POST /interactions/track` 完成。

## 2. Admin dashboard 目前能看到什么？

`admin_portal/` 的 "Business Metrics" 标签页中嵌入了三个与本次审计直接相关的表格（数据来自 `GET /admin/interaction-analytics`，后端逻辑在 `curify_background/app/crud/admin.py`）：

- **Search Queries**（近 7 天）：按查询词展示搜索次数、无结果占比、以及点击归因（`result_clicks`/`chip_clicks`/`escape_clicks`/`result_ctr_pct`）——这是唯一能回答"搜索是否带来点击"的具体表格。
- **Engagement Funnel**（近 7 天）：DAU→iDAU→浏览→点击→搜索→...→Generate/Remix→保存/下载/分享，但每一环只是"该用户在窗口内是否发生过该行为"的布尔标记，**不是**严格按时间顺序验证的单用户路径。
- **Surface Cohorts**：将"搜索过的用户"群体与"是否有过 Generate/Copy/Remix 行为"的群体做交叉统计——这是全仓库中**唯一**把 Search 和 Generate 联系起来的地方，但只是"同一周内是否都发生过"的群体相关性，不是具体某一次搜索到某一次生成的因果链路。

## 3. Search → Click → Generate 能否准确串起来？

**不能，目前只能部分、近似地串起 Search → Click，Click → Generate 这一段完全没有打通。**

- Search → Click：通过 `COALESCE(user_id, session_id)` + **5 分钟时间窗**的启发式规则做关联（代码见 `crud/admin.py::_section_search_queries`），存在已知漏洞：同一窗口内多次搜索会造成归因错误；`/search → /topics` 服务端跳转会导致点击事件完全丢失（工程师为此专门发明了一个 `content_id='search-redirect'` 的补丁标记）；健康的、未被话题标签收窄的正常搜索（结果数 ≥5）根本不会产生任何埋点事件——这意味着"搜索总量"这个分母本身就是被严重低估的。
- Click → Generate：`user_interactions` 表里的 `GENERATE` 事件（点击"生成"按钮的埋点）和真正的生成任务记录表 `project`（由 `/nano-templates/generate`、`/nano-freeform/generate` 两个接口创建）是由**完全不相干的两段代码分别写入的**，彼此之间没有任何共享主键，甚至连 Search→Click 那种"5 分钟时间窗"式的近似关联都没有实现。
- 更关键的结构性缺陷：`project` 表**没有 `session_id` 字段**，只有 `user_id`。这意味着即使未来补上了关联字段，**匿名（未登录）用户的生成行为也天生无法与其匿名搜索/点击历史关联**。

## 4. 当前归因等级是什么？

按 Level 1（精确 search_id 串联全链路）到 Level 4（无法可靠归因）分级：

- **Search → Click**：Level 3——近似归因（session/user 键 + 有界时间窗），但有明确记录在案的失效场景。
- **Click → Generate** 及 **Search → Generate（单次实例级别）**：Level 4——无法可靠归因。唯一存在的信号是 Surface Cohorts 那种**群体层面、同周共现**的相关性统计，不满足"某次搜索导致某次生成"这种因果/时序要求。

## 5. 哪些指标现在能算？

- 无结果率、低结果率（作为已跟踪事件类型的比例，可计算，但分母因"健康搜索不埋点"而被低估，导致比率**偏高**）
- Search CTR / Internal CTR（当前所有结果都是内部结果，两者数值相同；同样受益于/受限于上述 5 分钟启发式归因）
- 生成启动率、生成成功率（可直接从 `project.status` 计算，但**与搜索完全无关联**，是独立指标）

## 6. 哪些只能近似算？

- 总搜索量、搜索会话数、独立搜索用户数、独立查询词数（均受"健康搜索不埋点"影响而低估；查询词文本还带有未清洗的编码后缀，导致去重计数偏差）
- 搜索放弃率、搜索改写/重搜率（字段存在但目前代码库中未实现，需要新写查询）
- Search-to-Generate 率（唯一近似替代是 Surface Cohorts 的群体周相关性，**不满足**管理层要求的"会话级、有时序"的定义）

## 7. 哪些完全不能算？

- Click-to-Generate 率（无任何关联机制，哪怕是近似的时间窗都没有）
- 搜索结果曝光率（曝光事件完全不存在）
- 排名点击率 Rank CTR（`result_rank` 字段完全不存在）
- 内部/外部结果 CTR、外部流失率（Hybrid Search 尚未上线，`result_source` 字段不存在）
- 查询级别转化率（同 Search-to-Generate/Click-to-Generate 的缺陷，细化到单个查询词）

## 8. 上 Hybrid Search 前必须补哪些 P0 埋点？

- **search_id**（贯穿曝光→点击→生成全链路的唯一稳定主键，这是最关键、最优先的一项——没有它，其他所有 P0 字段都无法真正发挥作用）
- search_mode（区分内部 vs. 混合搜索实验分组）
- result_source（区分内部/外部结果来源）
- result_rank（结果排名位置）
- result_click（通过 search_id 关联，而非猜测式时间窗）
- generate_click（通过 search_id 关联）
- generation_success（通过 search_id 关联，数据源仍是 `project.status`）

此外，`project` 表需要补充能覆盖匿名用户的关联字段（不能仅依赖 `session_id` 的持久性），否则匿名转化链路依然无法闭环。

## 9. 为什么不能只看 CTR？

本次审计发现的两个真实存在（非假设）的机制，**已经足以**在不改变生成效果的情况下人为推高 CTR 报表数值：

1. **分母被低估**：由于健康的、未收窄的正常搜索根本不产生埋点事件，一旦 Hybrid Search 带来更多"外观吸引人但导向站外"的结果点击，`result_clicks`（分子）会上升，而"searches"（分母）依然是被低估、偏向失败案例的样本——CTR 数字因此被结构性推高，与真实搜索体验无关。
2. **Search 和 Generate 之间根本没有可靠链路**（见第 3、4 点）。如果 Hybrid Search 增加的点击流向了不支持"生成"能力的外部结果，Admin Dashboard 的 CTR 表格会显示"提升"，而 Surface Cohorts 这类唯一与生成相关的信号最多只能显示"同周整体 replicate 比例略有下降"——既无法证明也无法排除这是不是该次实验造成的，看 CTR 的人对此完全没有可见性。

## 10. 为什么最终必须看 Search-to-Generate 和 Generation Success？

因为 Curify 的商业目标不是"让用户点一下"，而是"让用户完成生成"。CTR 只衡量了漏斗最前端的一小段，而且如上所述这一小段本身的测量已经存在结构性偏差；Generation Success（可直接、可靠地从 `project.status` 计算，且不依赖任何搜索归因）和 Search-to-Generate（一旦补齐 `search_id` 之后才能真正可靠计算）才是能够反映"搜索是否真正为业务创造价值"的指标。在 P0 埋点补齐之前，任何仅依据 CTR 做出的 Hybrid Search 上线/放量决策，都存在"点击上升、生成下降"却被误判为成功的真实风险。

---

**结论：当前系统可以近似回答"搜索是否带来点击"，但完全无法可靠回答"搜索是否带来生成"。在为 Hybrid Search 设计 A/B 实验之前，必须先补齐以 `search_id` 为核心的 P0 埋点，否则任何基于现有数据的实验结论都可能是误导性的。**
