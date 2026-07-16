# Search → Click → Generate 转化测量方案建议

**基于文档**：本目录下的 `SEARCH_CLICK_GENERATE_DATA_AUDIT.md`、`SEARCH_ATTRIBUTION_FEASIBILITY.md`、`HYBRID_SEARCH_INSTRUMENTATION_REQUIREMENTS.md`
**要回答的核心问题**："用户搜索之后，我们能否知道他们是否点击、是否生成？"
**性质**：方案建议文档，不涉及任何代码修改、不执行 SQL、不访问生产数据。所有引用的表名/字段名/查询逻辑均来自此前的只读审计证据（`curify-studio` @ `7b3fa5b40b03da3056536257ead2200dab031247`）。

---

## 总览：为什么需要分阶段

审计已经确认：
- Search → Click 目前是 **Level 3（近似归因）**：靠 `COALESCE(user_id, session_id)` + 5 分钟时间窗做启发式关联（`curify_background/app/crud/admin.py::_section_search_queries`）。
- Click → Generate 目前是 **Level 4（无法可靠归因）**：`GENERATE` 点击埋点（`user_interactions` 表）和真正的生成任务记录（`project` 表）由两段互不调用的代码分别写入，没有任何共享键，连时间窗启发式都不存在。
- 结构性缺陷：`project` 表没有 `session_id`，匿名用户的生成行为天生无法回溯关联。

因此不存在"一步到位"的方案——短期只能在现有数据上做近似修补，真正可靠的答案必须靠新增埋点（`search_id`）才能拿到。下面按"不改代码 / 中期改造 / Hybrid Search 实验 / 路线图"四部分给出具体、可执行的方案。

---

## 一、短期方案（不做任何工程改动，基于现有数据近似回答）

### 1.1 基于 session/时间窗的归因方法

可以直接复用审计中发现的、已经在生产 SQL 里跑通的模式，把它**从"Search→Click"延伸到"Search→Click→Generate"**，作为一个只读的分析脚本（不改代码，只是新写一条 SQL，跑在只读副本/BI 工具上）：

```
关联键：who = COALESCE(user_id::text, session_id)
第一跳（已验证可行）：search 事件 → click 事件，5 分钟窗口，
                      current_page_route = '/search'
第二跳（未验证，需要新定义窗口，仅限登录用户）：click 事件 → project 表
                      status='COMPLETED' 的记录，按 user_id 关联，
                      窗口建议先用 30 分钟（可调整，需产品/工程共同拍板）
```

也就是说：
1. 先用现有的 `_section_search_queries` 逻辑（已在 admin dashboard 跑）拿到"这次搜索是否有点击"。
2. 再对**同一个 `user_id`**（注意：**做不到匿名用户**，因为 `project` 表没有 `session_id`），去查 30 分钟（或其他约定窗口）内是否有一条 `project.status = 'COMPLETED'` 的新记录。
3. 把两步结果拼在一起，得到一个"近似版 Search-to-Generate 率"。

这不需要改一行产品代码，只需要一条新的分析 SQL（可以先在 `dev/jayw/admin_analysis/` 风格的一次性脚本里跑，观察效果，再决定要不要固化进 admin dashboard）。

### 1.2 复用现有数据的具体做法

- **数据源**：只用现有两张表——`user_interactions`（搜索/点击/GENERATE点击埋点）+ `project`（真实生成任务状态）。不需要新表、不需要新埋点。
- **口径对齐**：复用审计中已经写好的 `SAFE_READ_ONLY_SQL_TEMPLATES.sql` 模板 7、8（Search-to-Generate、Click-to-Generate 的 PLACEHOLDER 版本），把窗口参数化，先用一个"实验性"窗口（如 30 分钟）跑出一个基线数字，哪怕不精确，也能作为短期内部参考、发现明显异常（比如某天生成任务暴跌）的预警信号。
- **同时保留 `surface_cohorts` 的群体相关性**作为交叉验证——如果两个近似指标（时间窗版 vs. 群体周相关版）方向一致，说明结论相对稳健；如果背离，说明需要更谨慎解读，不能只看一个数字。

### 1.3 局限性（必须向管理层明确说明，避免误用）

1. **完全无法覆盖匿名用户**——`project` 没有 `session_id`，这条路径下的"生成"只能匹配到登录用户，Curify 相当一部分流量可能是未登录搜索用户，这部分转化会被完全漏掉，导致低估。
2. **时间窗是拍脑袋定的，没有验证过**——不像 Search→Click 那个 5 分钟窗口好歹是生产代码里跑了一段时间、有历史数据支撑的经验值，Click→Generate 的窗口目前完全没有先例，选 10 分钟还是 1 小时都会显著改变结果，需要谨慎标注"这是估算，不是精确指标"。
3. **多次搜索/多次点击导致的归因混淆问题会被放大**——审计已经指出 Search→Click 这一跳存在"同一窗口内多次搜索"的归因错误风险，现在再叠加一跳 Click→Generate，误差会累积而不是抵消。
4. **搜索埋点本身存在低估**——健康的、未被话题标签收窄的搜索根本不产生任何事件（详见审计 `SEARCH_TRACKING_GAPS.md` 第6条），所以短期方案算出来的"搜索转化率"分母依然是偏小、偏向失败案例的，绝对值不可信，只能看**相对趋势**（比如周环比是否明显异常）。
5. **`GENERATE` 点击埋点和真实生成结果依然是两回事**——如果只用 `user_interactions` 里的 `GENERATE` 点击事件而不去 `project` 表核实 `status='COMPLETED'`，得到的只是"点了生成按钮"的意愿指标，不是"真的生成成功"的结果指标，两者必须分开报告，不能混为一谈。

**结论：短期方案能给出一个"方向性、有明显偏差警告"的近似数字，可以用于内部粗略监控和异常告警，但不建议作为任何决策（尤其是 Hybrid Search 上线与否）的依据。**

---

## 二、中期方案：引入 `search_id`，打通 Search → 曝光 → Click → Generate

### 2.1 核心改造：新增 `search_id`

这是审计报告反复强调的关键结论——**没有 `search_id`，后面所有精细化指标都无从谈起**。中期方案的核心就是一件事：

> 在用户发起一次搜索的那一刻，生成一个稳定的 `search_id`（建议 UUID），并让它贯穿这次搜索所引发的**曝光、点击、生成**全部事件。

具体建议（不涉及本次审计要求的代码修改，仅作为工程侧后续实施的设计建议）：

1. **搜索事件（`user_interactions` 表扩展）**：新增 `search_id` 列，每次真正发起搜索时生成并写入，同时也要修正现有的"只有失败/收窄搜索才埋点"的问题，改为**每次搜索都埋点**（不再只在零结果/低结果/chip收窄时才发事件）。
2. **结果曝光事件（新事件类型）**：目前完全不存在的一类事件，需要新增——搜索结果卡片被渲染/可见时，带上 `search_id` + `result_id` + `result_rank` + `result_source`（当前全部是 internal，为 Hybrid Search 预留字段）。
3. **点击事件**：在现有 `CLICK`/`VIDEO_CLICK` 埋点基础上，把 `search_id`（从曝光事件里带出来）一并写入点击事件，而不是像现在这样只能靠"5分钟时间窗+相同用户"去猜。
4. **生成事件/记录（`project` 表扩展）**：这是目前最大的断层——`project` 表需要新增 `search_id`（以及 `source_result_id`），在调用 `/nano-templates/generate` 或 `/nano-freeform/generate` 时，如果这次生成是从某次搜索结果点击发起的，就把对应的 `search_id` 传进来并落库。同时补上 `session_id`，让匿名用户的生成也能回溯关联。

### 2.2 打通后的效果

一旦 `search_id` 贯穿全链路，原来需要靠"用户身份 + 猜时间窗"才能近似回答的问题，变成一次简单的**主键 JOIN**：

```
search 事件 (search_id)
  → 曝光事件 (search_id, result_id, result_rank)
    → 点击事件 (search_id, result_id)
      → 生成记录 project (search_id, status)
```

不再需要猜"这个点击是不是刚才那次搜索引起的"——因为点击事件本身就带着它所属的 `search_id`，是精确匹配，不是概率匹配。这解决了短期方案里列出的全部核心局限性：覆盖匿名用户、消除时间窗猜测误差、消除多次搜索/多次点击的归因混淆。

### 2.3 迁移与兼容性建议

- 新字段应为**可空（nullable）**，新数据逐步带上 `search_id`，历史数据继续用短期方案的近似方法兜底，两套方法并行报告一段时间，观察两者差异是否收敛，作为新埋点质量的验证手段。
- 建议同时清理 `content_id` 里那些编码后缀（`|within=`、`|n=`、`|rw=`、`|paths=`），改成独立的结构化字段（`within_slug`、`result_count`、`rewrite_triggered` 等），避免继续用字符串拼接的方式传递结构化信息，减少后续查询出错的概率。
- 建议同步修正测试用户排除名单不一致的问题（审计中发现 `(155,1117,1267)` 和 `(155,1117)` 两个版本并存），在新埋点上线时统一维护成一个共享配置，而不是散落在多个脚本里。

---

## 三、Hybrid Search 实验测量方案

在 `search_id` 打通（即中期方案落地）之后，才具备做一个"可信"的 Hybrid Search A/B 实验的前提条件。以下是实验设计建议：

### 3.1 必需指标（按优先级）

**主指标（决定实验成败，必须两个一起看，不能只看一个）**：
- **Search-to-Generate Rate**：某次搜索最终是否产生了 `project.status='COMPLETED'` 的生成，通过 `search_id` 精确关联。
- **Generation Success Rate**：生成任务的成功率（独立于搜索，直接来自 `project.status`，作为质量兜底指标——如果 Hybrid Search 带来的生成请求本身质量下降导致失败率上升，这个指标能单独捕捉到）。

**次要指标（用于诊断，不用于判断实验成败）**：
- Search CTR（整体点击率）
- Internal CTR（内部结果点击率，需要 `result_source='internal'` 过滤）
- External CTR（外部结果点击率，需要 `result_source='external'` 过滤，Hybrid Search 上线后才有意义）
- Rank CTR（分位置点击率，评估外部结果插入位置是否合理）

### 3.2 A/B 对比设计

- **分组维度**：`search_mode`（如 `internal_only` vs. `hybrid`），随机分配到用户/会话级别（避免同一用户在实验期内看到不一致的体验）。
- **对比方式**：同一时间窗口内，两组分别计算主指标 + 次要指标 + 护栏指标，做统计显著性检验（样本量、显著性水平由数据团队按现有流量估算，本文档不做具体假设）。
- **必须同时对比**：不能只看"Hybrid 组的 CTR 比对照组高多少"，必须同时看"Hybrid 组的 Search-to-Generate Rate 比对照组低/高多少"——这正是审计报告反复强调的风险点：**CTR 上升、生成下降**这种组合，只有两个指标放在一起看才能被发现。

### 3.3 成功标准（建议，需产品/业务最终拍板具体数值阈值）

实验判定为"可以放量"，建议同时满足：
1. Hybrid 组的 **Search-to-Generate Rate 不显著低于**对照组（这是硬性门槛，一票否决）；
2. Hybrid 组的 **Generation Success Rate 不显著低于**对照组；
3. 在满足以上两条的前提下，Hybrid 组的 Search CTR / Internal CTR 等次要指标可以作为"体验是否改善"的辅助参考，但不能单独作为放量依据。

换句话说：**CTR 提升只是加分项，Search-to-Generate 和 Generation Success 不能掉，才是及格线。**

### 3.4 护栏指标（Guardrail Metrics）

以下指标即使不是本次实验的主要目标，也必须监控，一旦触发阈值应考虑暂停实验（具体阈值需要工程/业务共同确定）：

- **External Exit Rate**（外部结果点击后未返回产品完成任何操作的比例）——直接对应审计中"外部结果可能带用户离开产品"的风险。
- **Internal Click Cannibalization**（内部结果点击量是否被外部结果显著挤压）——对应"Internal-result preservation rate"。
- **搜索延迟（latency_ms）**——外部供应商调用增加的延迟不能显著拖慢搜索响应。
- **API 错误率（error_type / 外部供应商调用失败率）**——外部依赖的稳定性风险。
- **单次搜索成本（cost per search）**——外部供应商调用通常有成本，需要监控 ROI。
- **不安全/不相关外部结果比例**——外部结果的内容质量风险，需要人工抽查或规则过滤。

---

## 四、推荐实施路线图

### P0（尽快启动，建议本季度内完成，进入下一轮 Hybrid Search 讨论前必须就绪）

- 落地"短期方案"中的近似 Search→Click→Generate 分析脚本（不改代码），作为过渡期监控手段，并向管理层明确标注其局限性（尤其是匿名用户覆盖缺失、时间窗未经验证两点）。
- 启动中期方案的工程设计评审：确定 `search_id` 生成时机、传递方式、`project` 表新增字段的具体设计（这是后续所有工作的前提，建议尽快拉工程团队评审，本文档只给方向不给实现细节）。
- 修正测试用户排除名单不一致的问题（低成本、高性价比的数据质量修复）。

### P1（`search_id` 工程改造窗口，建议下一到两个迭代周期）

- 完成 `search_id` 在搜索事件上的埋点，并把"只有失败/收窄搜索才埋点"的逻辑改为全量埋点（这一步本身就能修复短期方案里提到的"搜索总量被低估"问题，即使还没打通 Click→Generate 也有独立价值）。
- 新增结果曝光事件（`search_id` + `result_id` + `result_rank` + `result_source`），补上目前完全空白的"曝光"这一环。
- 点击事件补充 `search_id` 透传。
- `project` 表补充 `search_id`、`source_result_id`、`session_id` 三个字段，并在生成流程中把这三个字段实际写入。
- 双轨验证期：新旧两套方法（精确 `search_id` join vs. 短期近似方法）并行运行，比较差异，确认新埋点数据质量后再切换为主口径。

### P2（Hybrid Search 实验就绪后）

- 落地 `search_mode`、外部结果的 `result_source`/`provider`/`destination_domain` 字段（Hybrid Search 专属字段）。
- 搭建 A/B 实验的指标看板：主指标（Search-to-Generate、Generation Success）+ 次要指标（各类 CTR）+ 护栏指标（外部流失率、延迟、成本、错误率），并设置自动预警阈值。
- 补充查询敏感信息过滤/脱敏机制（对应审计中 `SEARCH_QUERY_PRIVACY_RISK_NOTES.md` 提到的"外部供应商调用前需要做敏感查询过滤"的建议），在真正把原始查询发送给外部供应商之前完成。
- 建立定期刷新的汇总报表层（替代目前"每次打开 dashboard 都实时查询、且相关物化视图早已失效"的现状），支撑长期趋势分析而不只是近 7/14 天的滚动窗口。

---

## 结语：直接回答管理层的问题

**"用户搜索之后，我们能否知道他们是否点击、是否生成？"**

- **点击：能，但只是近似的。** 现有数据 + 短期方案可以给出一个方向性、有明确误差范围的答案，足够做粗略监控，不够做精确决策。
- **生成：现在基本不能，短期方案只能给出一个覆盖不全（漏掉匿名用户）、窗口未经验证的粗略估算。** 要想真正、可靠地回答这个问题，必须先完成中期方案里 `search_id` 的埋点改造——这不是"锦上添花"的优化，而是回答管理层这个问题的**必要条件**。
- 在此之前，任何关于 Hybrid Search 的放量决策，都应该同时参考 Search-to-Generate 和 Generation Success 两个指标，而不能只看 CTR——这正是本次审计和本方案反复强调的核心风险点。
