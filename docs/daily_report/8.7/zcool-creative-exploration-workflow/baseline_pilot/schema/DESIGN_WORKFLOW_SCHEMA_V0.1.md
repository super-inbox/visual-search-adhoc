# Design Workflow Schema v0.1 (Pilot)

机读版本见 [`design_workflow_schema_v0.1.json`](./design_workflow_schema_v0.1.json)（JSON Schema draft-07，已通过 `python3 -m json.tool` 语法校验）。本文档是给人看的字段说明和判定标准。

Schema 分四层：**案例（case）→ 步骤（step）→ 素材（asset）→ 长图切分（long_image_panel，可选）**。一个案例包含 0..N 个 step，一个 case 或 step 可以引用 0..N 个 asset。

---

## A. 案例层字段（case）

| 字段 | 说明 |
|---|---|
| `case_id` | 案例内唯一 ID，如 `case_001` |
| `source_platform` | 固定为 `zcool` |
| `source_url` | 真实访问过的页面 URL |
| `source_title` / `source_author` | 必须取自页面本身，不可编造 |
| `source_publish_date` | 页面原文的相对时间字符串（如"1年前"），不换算成绝对日期，因为页面本身就没给出精确日期 |
| `source_access_date` | 本次访问的日期 |
| `design_category` | 如 `brand_full_case`、`logo_showcase`、`logo_collection`、`educational_article` |
| `industry` | 行业/品类 |
| `case_summary` | 1-3 句事实性摘要，不得包含页面未提及的推测细节 |
| `workflow_completeness` | 见下方"完整度等级"定义 |
| `workflow_order_recoverability` | 顺序是否可信复原，取值同 `confidence` |
| `source_quality` | 文本/图片实际可获取程度（见下） |
| `usable_for_workflow_training` | 布尔值 |
| `usage_recommendation` | 四选一：`usable_for_workflow_training` / `usable_as_visual_reference_only` / `usable_for_analysis_only` / `not_recommended` |
| `copyright_or_reuse_notes` | 必须写明平台、作者，明确该内容是站酷设计师的知识产权，不是 Curify 自有资产 |
| `review_status` | 见下 |

`source_quality` 取值：`text_and_images_ok` / `text_ok_images_blocked` / `text_partial_images_blocked` / `degraded` / `inaccessible`。**本轮 Pilot 中全部 8 个候选页面的图片均为占位符**，因此本 Pilot 案例的 `source_quality` 全部为 `text_ok_images_blocked`，这是本次最重要的数据质量限制,详见 `logs/access_log.md`。

`review_status` 取值：`not_reviewed` / `in_review` / `reviewed_by_ai_only` / `reviewed_by_human` / `needs_human_review`。本 Pilot 所有案例的初次抽取均由 AI 完成，尚未经过人工设计师复核，因此统一标记为 `reviewed_by_ai_only`，且在案例内容有争议判断处额外标 `needs_human_review`。

---

## B. 工作流步骤字段（step）

对应第七节"研究问题"中"能否恢复设计步骤及顺序"的核心数据结构。关键字段：

- `stage_type`：见下方枚举（36 个值，含 `unknown`）。
- `evidence_type` / `confidence` / `order_confidence` / `order_basis`：证据链的四个维度，缺一不可——一个步骤"存在"、"可信"、"顺序可信"、"顺序依据"是四件不同的事，必须分开记录，不能用一个"置信度"字段笼统概括。
- `candidate_outputs` / `selected_output` / `selection_reason` / `revision_instruction`：只有页面明确展示了多个方案及取舍时才填，否则留空，不得推测"设计师大概率还做过其他方案"。
- `next_step_dependencies`：记录该步骤的输出被哪个后续 `step_id` 使用，用于还原依赖图，而不仅仅是线性顺序。

---

## C. 素材字段（asset）

核心原则：**素材记录的是"页面上出现过什么、我们实际拿到了什么"，不是"我们猜测它是什么"**。

- `local_path` 必须为 `null`，除非本次会话中真的下载了文件。本 Pilot 未下载任何图片（因为拿到的都是占位符，下载没有意义），因此本 Pilot 所有 asset 的 `local_path` 均为 `null`，只记录 `source_url`。
- `detected_content` 在图片字节不可得时必须为 `null` 或字符串 `"unknown - image not retrieved"`，**不允许仅凭图片文件名、alt 文本或上下文猜测图片内容再当作已确认信息写入**。
- `is_process_asset` / `is_final_showcase` 可同时为 true，但需在 `caption` 或 `review_notes`（step 层）中说明原因。
- `is_composite`：一张图同时覆盖多个阶段时为 true，此时 `workflow_stage_candidates` 可以有多个值，不强行归一。
- `is_duplicate` / `duplicate_group`：本 Pilot 未做哈希去重（因为图片字节不可得），该字段目前全部为 `false` / `null`，留待后续阶段用 SHA-256 / perceptual hash 实现。

---

## D. `stage_type` 枚举（36 值）

```text
project_brief, business_context, brand_research, competitor_research, audience_definition,
brand_strategy, brand_positioning, naming, moodboard, reference_collection,
creative_direction, concept_development, color_system, logo_sketch, logo_exploration,
logo_refinement, logo_selection, logo_system, typography, custom_lettering,
graphic_elements, illustration_system, icon_system, photography_direction, packaging,
print_materials, marketing_materials, social_media, digital_application, merchandise,
signage, spatial_design, store_design, brand_guidelines, final_presentation, unknown
```

Pilot 中实际观察到有文字证据支持的 `stage_type` 子集：`business_context`、`brand_strategy`、`naming`、`color_system`、`packaging`、`marketing_materials`。其余枚举值在本 5 个案例中均未出现明确证据，保留在 schema 中是为了未来扩大样本时复用，而不是本 Pilot 的实际发现。

---

## E. 证据字段 `evidence_type`

| 值 | 定义 | 判定要求 |
|---|---|---|
| `explicit` | 页面正文明确描述了该步骤或决策 | 必须在 `evidence_text` 中给出可追溯的引用/近似引用 |
| `visual_explicit` | 图片本身明确展示该阶段（如色卡、Logo 草图网格、字体规范页） | 前提是图片字节实际可见；本 Pilot 图片不可得，因此**本轮没有任何一条记录使用 `visual_explicit`** |
| `inferred` | 只能根据前后文/展示顺序推断 | 必须同时给出较低或中等 `confidence`，不得当作已确认事实向下游传递 |
| `unknown` | 无法判断 | 默认兜底值 |

---

## F. 置信度 `confidence` / `order_confidence`

统一四值：`high` / `medium` / `low` / `unknown`。

- `confidence` 回答"这个步骤真的发生过吗、我们对它的描述准吗"；
- `order_confidence` 回答"这个步骤在这个位置（第几步）这件事本身有多可信"——两者经常不同，例如"冯老二散养牛"案例中"命名"这一步内容本身证据是 `explicit`/`high`，但它是否严格排在"调研"之后而非同步进行，只能算 `medium`。

---

## G. 完整度等级 `workflow_completeness`

| 等级 | 判定条件 |
|---|---|
| `complete` | 从 Brief 到最终应用全部阶段都有 `explicit` 或 `visual_explicit` 证据，且顺序可信（`order_confidence` ≥ medium） |
| `substantial` | 多数中段阶段存在（至少包含策略/定位类 1 项 + 探索或选择类 1 项 + 输出类 1 项），但 Brief 或规范页可能缺失 |
| `partial` | 只能恢复少数阶段，多为单点证据，顺序基本不可复原 |
| `showcase_only` | 只有最终成品/Mockup，没有任何过程证据 |
| `unusable` | 页面根本不是可还原的单一项目案例（如多项目合集、科普文章），或内容严重降级无法分析 |

本 Pilot 5 个详细案例的判定结果：`case_006`（冯老二散养牛）= `substantial`（全 Pilot 最高）；`case_002`（NOMNOMBOX）= `substantial`；`case_007`（MELLOWCO）= `partial`；`case_008`（韬客直播基地）= `partial`；`case_003`（视觉盛宴）= `showcase_only`（负面样本，符合预期）。无一案例达到 `complete`——这是 Pilot 的核心发现之一，详见 `PILOT_FINDINGS.md`。
