# 站酷品牌设计工作流数据 Pilot（2026-08-05）

## 研究问题

1. 站酷品牌设计案例是否适合反向构建设计工作流数据？
2. 哪些类型的站酷案例最适合？
3. 能否从页面恢复设计步骤及步骤顺序？
4. 哪些字段可以自动提取？
5. 哪些字段必须人工判断？
6. 如何区分设计过程和最终效果展示？
7. 如何处理长图、组合图、重复图和无关内容？
8. 怎样避免把推测内容当成真实设计过程？
9. 后续是否适合扩大到 20–50 个案例？
10. 是否需要开发正式抓取脚本？

全部 10 个问题的具体回答见 `PILOT_FINDINGS.md`。

### 工作流数据的定义

本任务中的"设计工作流数据"不是简单保存设计成品图片，而是尽可能恢复：

```text
项目需求或品牌背景 → 调研与品牌定位 → 灵感与创意方向 → 色彩系统 → Logo探索
→ 方案选择与修改 → 字体与辅助图形 → 包装/物料/空间应用 → 最终品牌视觉系统
```

并记录每个阶段的输入、设计动作、候选方案、选择/修改、输出、依赖关系、证据来源、判断置信度。完整字段定义见 `DESIGN_WORKFLOW_SCHEMA_V0.1.md`。

---

## 1. Background

老板要求先看几个站酷品牌设计案例，判断能否反向构建设计工作流数据，并决定如何清洗；同时另有一个品牌设计视频案例由老板自行处理，不在本任务范围内。

## 2. Manager Request

> "可以抓取些站酷的案例，反向构建设计工作流的数据。你可以先看几个，决定如何清洗。"

## 3. Scope

- 收集 5-10 个候选站酷品牌设计案例，选出 3-5 个做详细分析（实际选出 5 个，含 1 个负面样本）；
- 设计结构化数据 Schema（`design_workflow_schema_v0.1.json`）；
- 制定清洗规则（`CLEANING_RULES_V0.1.md`）；
- 用真实案例完成小样本 Pilot 并给出规模化建议。

## 4. Non-goals

- 不处理老板提供的品牌设计视频；
- 不扩展 Brand Direction Explorer；
- 不做正式生产爬虫；
- 不批量抓取大量站酷案例；
- 不训练模型；
- 不把站酷素材重新发布；
- 不创建 PR、不 commit、不 push。

## 5. Method

1. 用 `WebSearch` 发现候选案例 URL；
2. 用 `WebFetch` 对每个候选 URL 做只读访问，提取标题/作者/正文/图片情况，全部记录在 `logs/access_log.md`；
3. 基于真实访问结果填写 `source_candidates.csv`，从 8 个候选中选出 5 个（含 1 个负面样本）进入详细分析；
4. 为 5 个案例分别建立 `raw_cases/<case_id>/` 五件套文件；
5. 汇总为 `pilot_cases.jsonl` 并做程序化校验；
6. 横向对比写入 `case_quality_review.csv`；
7. 汇总结论写入 `PILOT_FINDINGS.md`。

未使用任何浏览器自动化、账号登录、验证码绕过或高频请求；未下载任何图片文件（因图片资源不可得，详见第11节）。

## 6. Cases Reviewed

候选池 8 个，详细分析 5 个（含 1 个负面样本）。完整清单见 `CASES_REVIEWED.md` 和 `source_candidates.csv`。

| case_id | 案例 | workflow_completeness |
|---|---|---|
| case_001 | 冯老二散养牛品牌全案设计 | substantial |
| case_002 | NOMNOMBOX轻食包装设计 | substantial |
| case_003 | MELLOWCO好醇恰巧品牌全案设计 | partial |
| case_004 | 韬客国际直播基地品牌全案设计 | partial |
| case_005 | 视觉盛宴：探索LOGO设计之旅（负面样本） | showcase_only |

## 7. Schema

见 `design_workflow_schema_v0.1.json`（机读，已通过 JSON 语法校验）与 `DESIGN_WORKFLOW_SCHEMA_V0.1.md`（人读说明）。四层结构：案例（case）→ 步骤（step）→ 素材（asset）→ 长图切分（long_image_panel，可选）。

## 8. Cleaning Rules

见 `CLEANING_RULES_V0.1.md`，含正文清洗、图片清洗、长图处理、组合图处理、重复图处理、过程与展示区分、步骤顺序证据分级、缺失步骤处理、可训练性判断、版权与来源共 10 个子节。

## 9. Pilot Results

- 5 个案例全部完成结构化提取，写入 `pilot_cases.jsonl`（5 行，逐行 JSON 校验通过）；
- 最佳案例（case_001）达到 `substantial` 完整度，顺序证据等级为最高档 `explicit_text_sequence`；
- **全部 8 个访问过的页面，图片均返回占位符，无一例外**——这是本次最重要的技术发现，直接决定了"暂不扩大抓取规模"（`SCALE_UP_SCRAPING: PAUSED`）的判断，但不改变"研究本身已完成"以及"应继续验证图片访问方案"（`IMAGE_ACCESS_VALIDATION: CONTINUE`）这两个结论，三者的关系见第12节；
- 详细结论见 `PILOT_FINDINGS.md`。

## 10. Automation vs Manual Review

自动化适合：元数据提取、正文初步清洗、格式校验、初步阶段分类建议。
人工必须负责：过程 vs 服务清单的区分、顺序可信度判断、候选/选择/修改关系判断、数据不一致澄清（如 case_001 的品牌名矛盾）、版权风险判断。详见 `PILOT_FINDINGS.md` 第3节。

## 11. Risks and Limitations

- **图片不可得是结构性限制**：站酷图片走前端懒加载，`WebFetch` 只能拿到占位符 `bg-placeholder.jpg`，不是访问权限问题，也不是本次运气不好；
- 文字摘要由 WebFetch 内置模型完成转换，存在转录误差风险（如 case_001 的品牌名不一致，无法排除是转录错误还是页面本身矛盾）；
- 5 个案例样本量小，结论（尤其是"服务类别标签易被误判"的模式）需要更大样本验证才能确认是否具有代表性；
- 未做任何图片哈希去重（无图片字节可用），第5节清洗规则中的去重逻辑尚未实测。

## 12. Recommendation

结论分三个独立维度，不合并成一个词：

```text
研究阶段本身：   PILOT_COMPLETE_WITH_IMAGE_ACCESS_BLOCKER   （已完成，非半途而废）
抓取规模决策：   SCALE_UP_SCRAPING: PAUSED                   （暂不扩大到20/50案例）
技术阻塞处理：   IMAGE_ACCESS_VALIDATION: CONTINUE            （建议继续验证图片获取方案）
```

具体路径：先解决图片访问问题（如引入浏览器渲染/截图工具，或人工下载验证），再考虑重新用相同的 5 个案例验证"有图 vs 无图"对完整度的实际影响，然后再决定是否进入 10-20 案例的下一轮 Pilot。**"暂不扩大规模"只针对是否现在就投入20或50案例的抓取成本，不代表方向被否定，也不代表停止推进**。完整理由见 `PILOT_FINDINGS.md` 第4-5节。

## 13. Output Files

```text
docs/daily_report/8.5/zcool-design-workflow-pilot/
├── README.md                              本文件
├── PROGRESS_STATUS.md                     进度与状态
├── CASES_REVIEWED.md                      候选案例汇总
├── CLEANING_RULES_V0.1.md                 清洗规则
├── DESIGN_WORKFLOW_SCHEMA_V0.1.md         Schema说明（人读）
├── PILOT_FINDINGS.md                      结论与建议
├── design_workflow_schema_v0.1.json       Schema（机读）
├── pilot_cases.jsonl                      5案例结构化数据
├── source_candidates.csv                  8候选案例记录
├── case_quality_review.csv                5案例横向对比
├── raw_cases/                             5案例详细分析 + 模板
├── extracted_assets/                      图片存放位置（本轮为空，见其README）
└── logs/access_log.md                     完整访问记录
```

## 14. Validation

- JSON 语法：`design_workflow_schema_v0.1.json` 已通过 `python3 -m json.tool` 校验；
- JSONL：`pilot_cases.jsonl` 5行全部可独立解析，`case_id` 唯一，`step_id` 案例内唯一，`evidence_type`/`confidence`/`order_confidence` 全部为合法枚举值，无编造的 `local_path`（脚本校验结果见下方终端总结）；
- CSV：`source_candidates.csv`（8行）、`case_quality_review.csv`（5行）表头与数据行数核对一致；
- 范围检查：`git status --short` / `git diff --stat` / `git diff --name-only` 确认所有新增文件均在 `docs/daily_report/8.5/zcool-design-workflow-pilot/` 目录内（见终端最终输出）。

## 15. Git Status

- 分支：`baobao/search-relevance-phrase-alias-2026-07-09`（**未新建/未切换分支**——因为进入任务时工作区存在与本任务无关的未提交修改，按任务约束保留原分支，仅在新目录中新增文件，不触碰已有改动）；
- 本轮修改范围：仅 `docs/daily_report/8.5/zcool-design-workflow-pilot/` 目录下的新增文件；
- **未 commit、未 push、未创建 PR**，符合任务约束。
