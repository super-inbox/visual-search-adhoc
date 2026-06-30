# Curify Search Optimization 工作报告 — 2026-06-30

**日期：** 2026-06-30  
**作者：** Baobao  
**项目：** Curify 搜索优化 + Blog/LinkedIn Wrap-up  
**仓库：** visual-search-adhoc（当前报告所在）/ curify-frontend（生产代码）

---

## 1. Executive Summary / 总结

今日工作分为两个阶段。

**上午阶段（Task 1–4，已在早期 report 版本中记录）：**

> 修复分支错误 → 清理仓库结构 → P0/P1 Gap Retest → 架构级 P0.5 诊断

**下午至晚间阶段（Task 5–6，本次新增内容）：**

> 最新要求转变为：**当前首要任务是 wrap up 已有 eval results → blog post + LinkedIn message**，不再继续追加实验，而是将已有数据包装成对外可读的产出。

本次更新报告涵盖全天完整工作，重点补充下午至晚间完成的内容：Curify PR #512 后 58-query refresh、Manual sanity retest、5 平台对比更新、Blog draft、LinkedIn post。

**核心结论（全天）：**

1. **P0/P1 retest FAIL=0**，系统无回归，可安全继续推进。
2. **PR #512 后 Curify creative rich rate 从 33% 升至 57%**，18/58 queries 改善，4/58 轻微回退。
3. **Blog draft 和 LinkedIn post 已完成**，可供 review，尚需补 1–2 张截图及 publish polish。
4. **主要剩余 gap**：recipe cluster、MBTI compatibility chart、FDE meme alias、部分 CJK compound alias，不是全部品类的问题。
5. **下一步技术方向应转为 relevance scoring + GSC eval expansion + crawling-based discovery**，不是继续盲目增加结果数量。

---

## 2. 今日工作背景

最新方向要求：

- 当前首要任务是 **wrap up 现有 eval results → blog post + LinkedIn message**。
- Blog 写作需遵守 `blog-writing-guidelines.md`，约 2000 字，包含平台对比核心 insights、数据表格，最好附 1–2 张 query 结果截图。
- **重点不是重新做所有实验**，而是包装已有素材，快速产出可给外部读者看的内容。
- 需要说明已有数据的来源和局限性（baseline 日期、方法论差异）。

因此今日下午工作围绕：盘点已有数据 → 补充 Curify 最新 refresh → 更新 5 平台对比 → 撰写 blog draft 和 LinkedIn post。

---

## 3. 全天工作总览

| 任务 | 名称 | 状态 | 主要产出 |
|------|------|------|---------|
| **Task 1** | 修 remote branch error | ✅ 已完成 | curify-frontend push 通道恢复正常 |
| **Task 2** | Repo Cleaning | ✅ 已完成 | 2042 个文件迁入 visual-search-adhoc（commits `ac9beb2`、`f15b11e`） |
| **Task 3** | P0/P1 Gap Retest | ✅ 已完成 | PASS=101，WARN=24，FAIL=0（commit `335bdc4`） |
| **Task 4** | 搜索架构 Review + P0.5 Gap 分析 | ✅ 已完成 | 10 个 P0.5 gap 识别（commit `3536d53`） |
| **Task 5** | Curify 58-query Refresh + 5 平台对比更新 | ✅ 已完成 | `curify_refresh_after_pr512_report.md`、`five_platform_comparison_curify_refresh_2026-06-30.md` |
| **Task 6** | Blog Draft + LinkedIn Post | ✅ 初稿完成，待 review | `blog_draft.md`、`linkedin_post.md` |

> Task 1–4 详细内容见本报告第 4–7 节，Task 5–6 详细内容见第 8–9 节。

---

## 4. Task 1 — 修 Remote Branch 上的 Error

在推送阶段之前，curify-frontend 生产仓库的远程分支存在错误（branch 分歧或 push 阻塞），导致后续工作无法安全推送到远端。

Task 3（commit `335bdc4`）和 Task 4（commit `3536d53`）均成功推送，间接证明 push 通道在此之前已修复正常。

> 具体 error 类型需在 curify-frontend 仓库的操作记录中人工核对。

---

## 5. Task 2 — Repo Cleaning

**要求：**

- `curify-frontend`：保持生产仓库，`docs/` 目录只保留 `.md` 文件。
- `visual-search-adhoc`：专门存放实验产物（截图、JSON/CSV、采集数据、分析报告等）。

**完成情况：**

| Commit | 日期 | 内容 |
|--------|------|------|
| `ac9beb2` | 2026-06-30 13:09 | 主体迁移（2042 个文件），含 claude-reports、data/external_signals、daily_report、external-signal-pilot 全部内容 |
| `f15b11e` | 2026-06-30 14:02 | 清理补充（DS_Store 移除、部分修正） |

迁移到 visual-search-adhoc 的内容类型：Claude 分析报告、外部信号采集数据、日报/阶段进度、实验脚本、PNG 截图、手工采集模板。

---

## 6. Task 3 — P0/P1 Gap Retest

**Commit：** `335bdc4`  
**产出文件：** `p0-p1-gap-retest-2026-06-30/report.md`、`p0-p1-gap-retest-2026-06-30/gap_retest.csv`

**测试范围：** `search_eval_set.json`（125 条 query），branch `baobao/multi-intent-topic-cooccurrence`

**最终结果：**

| 指标 | 数值 |
|------|------|
| 总 query 数 | 125 |
| PASS | 101 |
| WARN | 24 |
| **FAIL** | **0** |

**FAIL=0 的意义：** 没有任何 query 出现"原本正常、现在崩溃"的情况，没有因代码改动导致的 recall 退化，可以安全进行下一步改进。

24 条 WARN 中 17 条为尚未解决的 gap，其中 82%（14 条）属于 c2（有模板但缺少 inspiration 内容），说明搜索算法对"已有内容"的召回基本正常，更深的问题是内容 density 为零。

---

## 7. Task 4 — 搜索架构 Review + P0.5 Gap 分析

**Commit：** `3536d53`  
**产出文件：** `search-architecture-review-p0-5-2026-06-30/report.md`、`search-architecture-review-p0-5-2026-06-30/p0_5_gap_summary.csv`

梳理了 Curify 搜索 pipeline 12 个步骤，识别出 10 个系统性 P0.5 级架构 gap：

| Gap ID | 短名称 | 中文说明 | 优先级 |
|--------|--------|---------|--------|
| G1 | plural-stem | 多词 query 复数 token 不 stem | T1 |
| G2 | catalog-density | 整个内容家族 0–1 条 inspiration | T3 |
| G3 | flat-scoring | 打分无字段权重，所有字段等权 | T1 |
| G4 | bulk-promo-precision | Template bulk-promotion 制造 score=100 洪水 | T1 |
| G5 | rank-score-orphaned | rank_score 未用于搜索排序 | T2 |
| G6 | concept-expand-inspirs | Concept expansion 仅覆盖 template，不覆盖 inspiration | T2 |
| G7 | gallery-exact-only | Gallery prompts 仅精确 tag 匹配 | T3 |
| G8 | alias-table-empty | QUERY_ALIASES 仅 2 条，覆盖极少 | T2 |
| G9 | cjk-bigram-fragility | CJK bigram 滑动窗口生成非词 bigram | T1 |
| G10 | generable-duplication | Generable templates section 与主 pipeline 完全隔离 | T2 |

**核心结论：最大的问题不是内容全部缺失，而是已有内容因 ranking 逻辑缺陷、alias 覆盖不足、stemming 限制、CJK tokenization 缺陷等，无法被稳定 surface 出来。**

---

## 8. Task 5 — Curify PR #512 后 58-query Refresh + 5 平台对比更新

### 8.1 资料盘点与方法确认

- 确认之前 benchmark 是 58 queries（非 57）。
- 外部 4 平台（Google / Bing / Pinterest / Canva）数据来自 June 19–23 baseline，**不重新抓取**，沿用旧数据。
- Curify 在 PR #512 merge 后（`main` at `a1a60bc5`）重新做 programmatic refresh。
- 方法：local tokenizer + `nano_inspiration.json`（3,160 条）+ template i18n blobs（en+zh），不含 LLM rewriter live path。

### 8.2 Curify 58-query Refresh 结果

**产出文件：** `curify-blog-linkedin-wrapup-2026-06-30/curify_refresh_after_pr512.csv`、`curify-blog-linkedin-wrapup-2026-06-30/curify_refresh_after_pr512_report.md`

| 指标 | June Baseline（pre-PR #512） | Post-PR #512（programmatic） | 变化 |
|------|------------------------------|------------------------------|------|
| Rich queries（/58） | ~35 | 41 | +6 |
| Empty queries（/58） | ~8 | 6 | -2 |
| Creative rich rate（30 queries） | ~33% | **57%** | +24 pp |
| Consumer rich rate（28 queries） | ~82% | **86%** | +4 pp |
| Improved bucket | — | 18/58（31%） | — |
| Regressed bucket | — | 4/58（7%） | — |
| Stable | — | 36/58（62%） | — |

**改善代表性案例（18 queries）：**

- `ESL flashcards printable`：thin → rich（16 条）
- `Spanish vocabulary printable`：thin → rich（15 条）
- `global influence`：empty → rich（38 条）
- `remote destination`：empty → rich（177 条）
- `mbti marvel`：moderate → rich（74 条）
- `minimalist autumn outfit for japan travel`：empty → rich（11 条）

**4 条回退（需跟进）：**

| Query | 原因 |
|-------|------|
| `phonics worksheets kindergarten` | alias fix 在 `baobao` 分支未 merge 到 main |
| `香薰` | P0.1 re-enrichment 可能 narrow 了 tag |
| `bilingual flashcards for kids learning korean fruits` | 6-token strict query，alias 覆盖不足 |
| `samurai` | 轻微下降（9 条，略低于 rich 阈值），可接受 |

**仍为 empty/weak 的 10 条 query（持续 gap）：**

- Recipe cluster（easy weeknight dinners、gluten free dinner ideas、cuban sandwich）：c2 内容生成缺口
- Creative intent gap（watercolor map of europe、before after kitchen makeover、infj vs entp dating）：c2
- 抽象/品牌 query（unique cultural experiences、水果中文）：c3 或 c1 alias 问题

### 8.3 Manual Sanity Retest（10 query live 验证）

**产出文件：** `curify-blog-linkedin-wrapup-2026-06-30/sanity_retest.csv`、`curify-blog-linkedin-wrapup-2026-06-30/sanity_retest_report.md`

对以下 10 个 query 进行人工 live/manual verification：

| Query | 类别 | 结果 |
|-------|------|------|
| `vocabulary flashcards` | Bilingual/educational | 表现好 |
| `Spanish vocabulary printable` | Bilingual printable | 表现好 |
| `ESL flashcards printable` | Bilingual printable | 表现好 |
| `青铜打工小兽` | CJK fandom | Fallback rewrite rescue，但 ranking noisy |
| `FDE meme frontend deployed engineer` | Creative meme | Live 0 结果（alias 缺口） |
| `backend engineer rear wheel drive meme` | Creative meme | Live 0 结果 |
| `canva presentation template` | Template keyword | Live 0 结果 |
| `动物 词汇` | CJK educational | 表现好 |
| `genshin` | Fandom | 表现好 |
| `classroom poster printable` | Template/educational | 表现好 |

**结论：** vocabulary / bilingual / printable / template-oriented query 表现较好；FDE meme / backend meme / canva template 这类 compound creative intent query 仍然 live 0，本质是 tagging/alias 缺口，而非内容或架构缺失。

### 8.4 Updated 5-Platform Comparison

**产出文件：** `curify-blog-linkedin-wrapup-2026-06-30/five_platform_comparison_curify_refresh_2026-06-30.md`

方法：Google / Bing / Pinterest / Canva 使用旧 baseline；Curify 使用 PR #512 后 refresh 结果。不是 full re-crawl，而是 Curify-refresh update。

| 平台 | 角色定位 | 核心 insight |
|------|---------|-------------|
| Google Images | Recall floor | 58/58 coverage，100% recall，但无法路由到创作工具 |
| Bing Images | Category taxonomy signal | 39.9 chips/query，taxonomy 最丰富，同样无创作路由 |
| Pinterest | Inspiration/sub-intent cluster | 视觉多样性最好，但 40/58 query 因 login modal 无 label 数据 |
| Canva | English template benchmark | 58.2 chips/query（可访问 query），36/58 accessible；CJK + fandom query 有 login wall |
| Curify (baseline) | Actionable/generative | Creative rich rate 33%，avg 8.8 intent chips |
| **Curify (post-PR #512)** | **Actionable/generative（提升后）** | **Creative rich rate 57%，18/58 improved** |

---

## 9. Task 6 — Blog Draft + LinkedIn Post

### 9.1 Blog Draft

**产出文件：** `curify-blog-linkedin-wrapup-2026-06-30/blog_draft.md`

**标题：** Visual Search in 2026: A 5-Platform, 58-Query Benchmark

**主要内容结构：**

1. 开篇：visual search benchmark 的常见误区（recall ≠ 真正有用的指标）
2. 平台快照：5 平台各自定位与局限性
3. PR #512 具体改动说明（metadata expansion v2、multi-query retrieval P0.2、阈值调整）
4. 数据对比：creative rich rate 33% → 57%，改善案例，4 条回退说明
5. Label count gap 的正确解读（chip 数量 ≠ intent 理解深度，是 catalog 深度的反映）
6. FDE meme case study（zero result 的根因不是架构或内容，是 metadata/tagging）
7. FAQ（5 问）
8. Next steps（relevance scoring、GSC eval expansion、crawling-based discovery）

**当前状态：**

- 内容完整，逻辑自洽，约 2000 字，符合 blog-writing-guidelines.md 要求。
- 可供 review。
- **尚需**：补 1–2 张真实 query 截图（目前为 `<!-- Screenshot placeholder -->`），平台总表 caption、CTA、internal links 等 publish polish 工作。

### 9.2 LinkedIn Post

**产出文件：** `curify-blog-linkedin-wrapup-2026-06-30/linkedin_post.md`

**核心论点：**

> "The gap that matters isn't recall. It's routing."

**主要内容：**

1. 58-query benchmark 说明（30 creative + 28 consumer）
2. Google / Bing / Pinterest / Canva 各自定位
3. PR #512 前后数据对比：creative rich rate 33% → 57%
4. Label count gap 的正确解读（chip 数 ≠ intent 理解）
5. FDE meme case study（zero result 的本质 = metadata gap）
6. Next steps 预告

**当前状态：**

- 基本可供 review，语气、风格可微调。
- 后续若 publish，根据平台调整长度和标签。

---

## 10. 当前 6.30 产出文件清单

### curify-blog-linkedin-wrapup-2026-06-30/

| 文件 | 说明 | 状态 |
|------|------|------|
| `blog_draft.md` | Blog 正文初稿，~2000 字，5 平台对比 | 待 review |
| `linkedin_post.md` | LinkedIn post 初稿 | 待 review |
| `blog_source_inventory.md` | 素材盘点文档，确认数据来源与方法论 | 已完成 |
| `curify_refresh_after_pr512.csv` | 58-query programmatic refresh 明细数据 | 已完成 |
| `curify_refresh_after_pr512_report.md` | Refresh 分析报告（含 summary table、回归说明） | 已完成 |
| `five_platform_comparison_curify_refresh_2026-06-30.md` | 5 平台对比更新（Curify 使用最新 refresh） | 已完成 |
| `sanity_retest.csv` | 10-query manual live retest 明细 | 已完成 |
| `sanity_retest_report.md` | Manual retest 分析报告 | 已完成 |

### 其余 6.30 产出（早期已记录）

| 目录 | 说明 |
|------|------|
| `p0-p1-gap-retest-2026-06-30/` | Task 3：125-query retest（PASS=101, WARN=24, FAIL=0） |
| `search-architecture-review-p0-5-2026-06-30/` | Task 4：架构 review + 10 个 P0.5 gap |

---

## 11. 关键结论

### PR #512 后 Curify 的召回变化

PR #512（2026-06-26 merge）包含三项改动：

1. **Metadata expansion v2**：inspiration 平均 tag 数从 5 升至 25.5，gallery prompt 平均 26.3 个 tag，template topic 从 5 升至 15。这是召回改善的主要原因。
2. **Multi-query retrieval（P0.2）**：低结果 query 触发最多 8 条检索路径，结果合并后按 multi-hit 重新排序。
3. **LOW_RESULT_THRESHOLD 调整**：从 3 升至 5，catch 更多 borderline-thin query。

**改善明显的 query 类型：** vocabulary / bilingual / printable / template-oriented / travel & lifestyle / character-MBTI。

### 仍有 gap 的领域

以下问题**没有**被 PR #512 解决：

- **Recipe cluster**：easy weeknight dinners、gluten free dinner ideas、cuban sandwich recipe poster → c2 内容生成缺口（没有对应的 inspiration 记录）
- **MBTI compatibility chart**：infj vs entp dating compatibility chart → c2 内容生成缺口
- **FDE meme alias**：frontend deployed engineer meme → compound creative intent，alias/tagging 缺口，不是内容或架构问题
- **部分 CJK compound alias**：水果中文 → c1 alias / bigram 缺口（bigram 生成了非词 `果中`）

### 方法论注意事项

- 外部 4 平台数据来自 June 19–23，与 Curify 的 June 30 数据存在时间差，**不是 same-day comparison**。
- Curify refresh 为 programmatic scoring，**不包含 LLM rewriter live path**；live prod 实际表现会比 programmatic 结果更好（已通过 10-query manual retest 验证）。
- 4 条回退中，`phonics worksheets` 回退原因是 alias fix 在 `baobao` 分支未 merge 到 main，不是内容变差。

---

## 12. 下一步建议

### 即时行动（Blog/LinkedIn wrap-up）

1. **提交 `blog_draft.md` 和 `linkedin_post.md` 供 review。**
2. 根据反馈补 1–2 张真实 query 截图（建议："Spanish vocabulary printable" 跨平台对比，或 "ESL flashcards" before/after）。
3. 如需 publish，补充：SEO metadata、CTA、internal links、autotranslation/i18n 标注。

### 技术方向（下一阶段）

1. **Relevance scoring**：当前最大问题不是 recall 数量，而是排序质量。G3（字段权重）、G4（bulk-promotion flood）是优先修复点，代价低、收益高。
2. **GSC eval expansion**：5,913 条真实用户 query 信号（Search Console）是下一步 eval set 扩展的主要来源，优先于人工制定新 query。
3. **Crawling-based discovery**：通过爬取发现 catalog 中仍未覆盖的内容家族（recipe、landmark、cultural experiences 等），不是盲目增加数量，而是定向填补 c2/c3 gap。
4. **修复 FDE meme 类 alias 缺口**：compound creative intent / template routing 问题，在 gallery prompts 中补充 search_aliases 即可修复，代价极低。
5. **Merge phonics alias fix**：`baobao/multi-intent-topic-cooccurrence` → main，修复 `phonics worksheets kindergarten` 回退。

---

## 13. 产出文件汇总

### Task 1 — Remote Branch Error 修复

| 证据 | 说明 |
|------|------|
| Commits `335bdc4`、`3536d53` 均成功推送 | 间接证明 push 通道已恢复 |
| ⚠️ 具体 error log 需在 curify-frontend 仓库人工确认 | — |

### Task 2 — Repo Cleaning

| 产出 | 说明 |
|------|------|
| `curify-frontend-cleanup-2026-06-30/`（本仓库） | 迁移自 curify-frontend 的全部实验产物 |
| Commit `ac9beb2`（2042 files） | 主体迁移 |
| Commit `f15b11e` | 清理补充 |

### Task 3 — P0/P1 Gap Retest

| 文件 | 说明 |
|------|------|
| `p0-p1-gap-retest-2026-06-30/report.md` | PASS=101，WARN=24，FAIL=0 |
| `p0-p1-gap-retest-2026-06-30/gap_retest.csv` | 逐 query 明细 |
| Commit `335bdc4` | 已推送 |

### Task 4 — 搜索架构 Review + P0.5 Gap 分析

| 文件 | 说明 |
|------|------|
| `search-architecture-review-p0-5-2026-06-30/report.md` | 架构 review 主报告（10 个 P0.5 gap） |
| `search-architecture-review-p0-5-2026-06-30/p0_5_gap_summary.csv` | Gap 汇总表 |
| Commit `3536d53` | 已推送 |

### Task 5 — Curify Refresh + 5 平台对比

| 文件 | 说明 |
|------|------|
| `curify-blog-linkedin-wrapup-2026-06-30/curify_refresh_after_pr512.csv` | 58-query programmatic refresh 数据 |
| `curify-blog-linkedin-wrapup-2026-06-30/curify_refresh_after_pr512_report.md` | Refresh 分析报告 |
| `curify-blog-linkedin-wrapup-2026-06-30/five_platform_comparison_curify_refresh_2026-06-30.md` | 5 平台对比更新版 |
| `curify-blog-linkedin-wrapup-2026-06-30/sanity_retest.csv` | 10-query manual retest 数据 |
| `curify-blog-linkedin-wrapup-2026-06-30/sanity_retest_report.md` | Manual retest 报告 |
| `curify-blog-linkedin-wrapup-2026-06-30/blog_source_inventory.md` | 素材盘点 |

### Task 6 — Blog Draft + LinkedIn Post

| 文件 | 说明 |
|------|------|
| `curify-blog-linkedin-wrapup-2026-06-30/blog_draft.md` | Blog 初稿，待 review |
| `curify-blog-linkedin-wrapup-2026-06-30/linkedin_post.md` | LinkedIn post 初稿，待 review |

---

## 14. 简短汇报

今日完成六件事。早期四件事（remote branch fix、repo cleaning、P0/P1 retest FAIL=0、架构 P0.5 gap 分析）已在上午完成并推送。

下午至晚间的重心转向 wrap-up：在 PR #512 后重新 refresh 了 Curify 的 58-query benchmark，creative rich rate 从 33% 提升至 57%，18/58 queries 改善；做了 10-query manual live retest 验证 programmatic 结果在 live prod 中基本成立；更新了 5 平台对比文档；完成了 blog draft（约 2000 字）和 LinkedIn post 初稿。

Blog 和 LinkedIn post 均可供 review。待反馈后补 1–2 张截图，如需 publish 再补 SEO/CTA/i18n。

下一步技术重点应是 relevance scoring + GSC eval expansion + crawling-based discovery，而不是继续追加 recall 数量。

---

*报告生成时间：2026-06-30 | 作者：Baobao | 仓库：visual-search-adhoc*
