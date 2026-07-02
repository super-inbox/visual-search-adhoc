# 2026-07-02 工作总结 — Curify Visual Search / External Signal Follow-up

> 本报告基于对两个仓库的 git log / git status / 相关文件的实际检查生成，未编造任何内容。存在不确定之处已在文中标注「不确定」。

---

## 今日完成概览

- **Blog / LinkedIn 对外版改写**：将原本偏内部风格的 58-query 视觉搜索 pilot 报告，改写为面向外部读者的 `blog_public_v2.md` 与 `linkedin_public_v2.md`，并根据反馈做了范围声明、内部内容剥离等调整。
- **多平台截图素材收集**：针对 `ESL flashcards printable` 查询，完成 Google / Bing / Pinterest / Canva / Curify 五个平台的截图收集，本地留存，CDN 上传仍未完成。
- **Content revision note 维护**：记录并两次更新了改写过程中「保留 / 移至内部 / 删除 / 新增」的内容对照表，以及图片收集状态。
- **curify-frontend C1/C2 小批量修复**：在 `baobao/c1-c2-gap-fixes-2026-07-02` 分支完成 2 项 C1（别名类）搜索 gap 修复并提交（commit `2af3ca2f`），完成验证；C2（MBTI 图片生成）任务已生成并人工审核通过图片，但因匹配器 strict-floor 回归风险和 CDN 工具缺失，主动延期不纳入本批次。

---

## 1. Blog / LinkedIn public-facing external insights 改版

**涉及文件**（现位于 `docs/daily_report/7.2/`，源自 `af237c2` 提交，后由 `93320ad` 从 `6.30/curify-blog-linkedin-wrapup-2026-06-30/` 目录搬移至 `7.2/`）：
- `blog_public_v2.md`
- `linkedin_public_v2.md`
- `content_revision_note.md`

**改动内容 / 与反馈的对齐**：
根据 `content_revision_note.md` 的记录，v2 相对旧的内部版本（`blog_draft.md`、`linkedin_post.md`，两者原文件保留未动）做了以下调整：
- 新增「What This Is (and Isn't)」开篇小节，明确声明这是 **58-query 的小规模 pilot study（定性 + 半定量），不是严谨的完整 benchmark**，并加了「Findings are directional」的措辞 —— 该说明是根据反馈专门补充的（对照 `EXTERNAL_SIGNAL_INSIGHTS_zh.md §0` 的免责声明）。
- 新增「What This Means for Visual Search Strategy」结尾小节，将内部建议改写为面向外部的行业洞察表述。
- 新增 Case Study 2（`monstera plant care guide infographic` 的 Pinterest 子意图 chip 案例）。
- LinkedIn 版本改为「精简版摘要」（58-query 概况 + 消费-创作光谱 + 3 条跨平台洞察），不再包含完整的 star rating 表格（该表格只保留在 blog 正文 §4 中）。

**移至内部专用（未出现在 v2 公开版本中）**：
- 「What Changed After PR #512」章节（引用具体内部 PR）
- 「What Still Doesn't Work (And Why That's Honest)」章节
- FDE meme 案例（"Frontend Deployed Engineer" vs "Backend Engineer" 内部工程梗）
- 4 条 query 的回归分析（root cause、修复计划）
- P0/P1/P2/P3 gap 严重度分级表
- Curify 内部别名修复细节、tokenizer 实现细节
- GSC eval 扩展 / crawling-based discovery 等内部路线图
- programmatic scoring 方法论、`eval_search.cjs` 相关引用
- LinkedIn 内部草稿中对 PR #512、FDE meme、alias tagging 的引用

**彻底删除（内部笔记中也未保留）**：
- 具体 commit hash 引用（如 `a1a60bc5`）
- 「Curify re-scored on main at commit …」这类 CI artifact 措辞
- `水果中文` bigram tokenizer gap 的实现细节
- `searchAliases: []` 修复指令（FDE meme 打标任务项）
- 对内部文件路径的引用（`eval_search.cjs`、`nano_inspiration.json`、`search_eval_set.json`）

**保留的核心内容**：58-query pilot 范围与框架、8 大主题分类分布表、消费/创作/混合意图占比（25/26/7）、消费-创作光谱图、平台 star rating 表（仅 blog）、Bing/Google 平均 label chip 数据、Pinterest One Bar 子意图 chip 案例、Canva CJK 登录墙数据、Curify 8-cluster 意图标签系统说明、"ESL flashcards printable" 跨平台路由对比案例表、pilot 局限性说明、平台信号推荐表。

**待办**：图片仍是占位符状态（见下节），博客翻译（英译中或其他语言）未开始，相关性打分（relevance scoring）体系未开始。

---

## 2. 多平台图片素材整理

- **选定查询**：`ESL flashcards printable`
- **收集平台**：Google Images、Bing Images、Pinterest、Canva、Curify（含 Curify 搜索结果页 + 生成入口页，共 6 张图）
- **存放路径**：`docs/daily_report/7.2/assets/esl_flashcards_printable/`（原始收集于 `af237c2`，路径为 `6.30/curify-blog-linkedin-wrapup-2026-06-30/assets/esl_flashcards_printable/`，后经 `93320ad` 搬移至 `7.2/`）
- 另外今日新增了「消费-创作光谱」说明性图形素材（`assets/platform_spectrum/`，含 `.html`/`.svg`/`.png` 及 `image_inventory.md`，commit `0b1887c`），用于替换 blog §7.2 中原本「待补充」的图片占位描述。
- **CDN 状态**：**全部本地留存，尚未上传 CDN**。`image_inventory.md` 中明确写明「CDN status: Local only — not uploaded」。Curify 自身的两张截图未来可能会替换为 Curify 已托管的资源链接（如果存在）。
- **待收集**（可选）：`monstera plant care guide infographic` 查询在 Pinterest 上的 One Bar 标签截图，尚未收集。

---

## 3. Content revision note 更新

`content_revision_note.md` 记录了 v2 改写过程中「保留 / 内部化 / 删除 / 新增」四类内容的完整对照表（见第 1 节），作用是为未来审计「哪些内部信息被过滤掉了」提供可追溯依据。

今日通过 `e0d1594` 提交做了一次更新，主要变化：
- 将 LinkedIn 部分的「保留 star rating 表格」更正为「仅 blog 保留完整表格，LinkedIn 改为精简摘要」（与实际改写结果对齐）。
- 「Image Needs for Next Step」章节从「全部延后收集，仅有占位符」更新为「6 张图片已本地收集完成」的实际状态表，并把「剩余可选图片需求」拆分列出（Pinterest monstera 截图、光谱示意图、并排对比图、CDN 上传）。

当前状态：**6 张 ESL flashcards printable 截图 + 1 套光谱图形已本地就绪，CDN 上传是发布前的唯一阻塞项。**

---

## 4. C1 + C2 小批量修复

- **仓库**：curify-frontend
- **分支**：`baobao/c1-c2-gap-fixes-2026-07-02`
- **提交**：`2af3ca2f` — "add c1 alias fixes for fruit and warmup checklist queries"
- **修改文件**：`public/data/nano_inspiration.json`、`docs/search-c1-c2-small-batch-2026-07-02.md`（新增文档）

本批次是对 `project_gap_retest_2026_06_30.md`（6/30 P0/P1 gap 复测）的后续跟进，聚焦其中被归类为 **c1（别名/分词器相邻问题）** 的 gap —— 即只需给现有 `nano_inspiration.json` 记录加搜索别名即可修复、不涉及模板/匹配器/分词器代码改动的问题；与之相对的 **c2（内容生成类）** gap 需要新生成图片素材，风险和工作量更大。

**C1 修复内容**：
1. `水果中文` / `中文水果`：为 `template-vocabulary-fruits-en-zh` 记录新增这两个无空格、两种词序的别名，绕开了中文 bigram 分词器无法正确切分该组合查询的限制。
2. `warmup routine running checklist`（原 P1 gap 查询）：检查发现该 query 专指"跑步"热身，但当前没有任何 running 专属的热身模板/灵感图，因此**原始 query 本身仍未修复**。本批次改为给 6 个非 running 的热身活动模板（gym、swimming、yoga、badminton、basketball、fencing）补充 `checklist` 变体别名，修复了这些运动类型下的「checklist」措辞覆盖缺口。

**验证结果**：
- `node scripts/eval_search.cjs --quiet` → `PASS=87 WARN=38 FAIL=0`（共 125 条）。与批次前基线相比只有一处 verdict 变化：`infj vs entp dating compatibility chart` 从 WARN 变为 PASS —— 这不代表该 MBTI 查询被修复，而是「回退到批次前真实状态」：MBTI C2 记录本身未上线（未加入 `nano_inspiration.json`），随之也移除了它对该查询的宽松匹配贡献，不是回归。该 MBTI C2 条目仍是未完成的延期跟进项，详见下方说明。
- `npx vitest run --config vitest.unit.config.ts lib/__tests__/thin_recall_queries.test.ts` → 28/28 通过。
- Ad-hoc 严格匹配复核（因部分查询不在 125 条固定 eval 集合内，直接对 `nano_inspiration.json` 做分词器/匹配器重放验证）：`水果中文`、`中文水果`、`gym warmup checklist`、`swimming warmup checklist` 均命中 1 条目标记录，`yoga warmup checklist` 命中 5 条相关记录（gym/yoga/badminton/basketball/fencing）—— 5 项确认全部命中，C1 修复符合预期。

**C2（MBTI INFJ×ENTP）延期说明**：
- 目标记录：`template-mbti-relationship-infographic-infj-entp`（目标查询：`infj vs entp dating compatibility chart`）。
- 生成的图片**已通过人工逐项目测审核**（物理缺陷、逻辑缺陷、文字乱码、语言不匹配、语义漂移、模板误用、占位符未替换、内容诡异等项均 PASS；仅备注底部摘要文字偏小偏密但可接受）。
- **CDN 上传受阻**：当前机器上未安装 `gcloud` 和 `gsutil`（已检查 PATH、Homebrew、onboarding runbook 中提到的 `~/curify-studio` venv，以及全盘搜索，均未找到），无法将素材推送至 `gs://curify-static`。
- **仅靠加别名会引发回归**：目标查询要求 6 个 token（`infj`/`vs`/`entp`/`dating`/`compatibility`/`chart`）全部严格命中记录的搜索文本（strict "allPrimary" 规则，不接受部分匹配）。但 `template_id`（`template-mbti-relationship-infographic`）本身已经免费带入了 "mbti"、"relationship" 两个词。由于匹配器的 strict-floor 行为（一旦某查询产生新的严格匹配，会整体丢弃该查询的所有宽松匹配结果，即使宽松匹配池本来很大），任何能同时补上 `compatibility` 和 `chart`（命中目标查询所需）的别名，也会让这条记录意外严格命中另一个无关查询 `mbti relationship compatibility chart`，把该查询原本 10+ 条宽松匹配结果（`rich` 桶，PASS）压缩成 1 条严格匹配（`thin` 桶，WARN）。测试了 4 个候选别名方案，能推动目标查询命中的两个都会引发该回归，不引发回归的两个也推不动目标查询。
- **真正的修复超出本批次范围**：需要匹配器/检索层面的改动（例如"新增一个严格匹配不应整体清空宽松匹配池"），或改用模板级而非 token-blob 级的检索信号 —— 两者都涉及匹配器/分词器代码，而本批次明确限定不碰这部分代码。
- **最终未上线**：该记录已从 `public/data/nano_inspiration.json` 中移除；`scripts/configs/mbti_infj_entp_2026-07-02.json`（未追踪文件，从未提交）已删除。已生成的本地图片文件（`public/images/nano_insp/template-mbti-relationship-infographic-infj-entp.jpg` 及 `nano_insp_preview/` 下的预览图）作为 gitignored 的本地草稿资产予以保留，后续重新拾起该任务时可直接复用。

---

## 已提交 / 已 push 的内容

| 仓库 | 分支 | Commit | 提交信息 | Push 状态 |
|---|---|---|---|---|
| visual-search-adhoc | main | `af237c2` | add public external insights blog linkedin drafts and image assets | 已 push |
| visual-search-adhoc | main | `e0d1594` | update revision note image status | 已 push |
| visual-search-adhoc | main | `93320ad` | move blog linkedin wrapup files to 7.2 daily report | 已 push |
| visual-search-adhoc | main | `0b1887c` | add visual search platform spectrum graphic | 已 push |
| curify-frontend | `baobao/c1-c2-gap-fixes-2026-07-02` | `2af3ca2f` | add c1 alias fixes for fruit and warmup checklist queries | 已 push |

> 已用 `git fetch origin main` + `git log origin/main..HEAD` 核实：visual-search-adhoc 的 main 分支与 origin/main 完全一致，今日 4 个提交均已推送。curify-frontend 分支在报告生成后已成功 push 至 origin。

---

## 仍未完成 / Follow-ups

- **Blog 配图 CDN 上传**：6 张 ESL flashcards printable 截图 + 光谱图形素材，均为本地文件，未上传 CDN，是发布前的阻塞项。
- **可选 Pinterest monstera 截图**：`monstera plant care guide infographic` 查询在 Pinterest 上的 One Bar 标签截图尚未收集（可选项）。
- **Blog 翻译未开始**。
- **Relevance scoring 体系未开始**。
- **C2 MBTI 检索策略已延期**：需要匹配器/检索层面的方案决策后才能安全上线；已生成图片和人工审核结果予以保留待复用。
- **gcloud/gsutil 工具缺失**：当前机器无法执行 CDN 同步，需要在装有该工具的机器上操作，或先完成本机安装（参考 `docs/onboarding-runbook.md` §1）。
- **curify-frontend 分支已 push，PR 仍需打开**。

---

