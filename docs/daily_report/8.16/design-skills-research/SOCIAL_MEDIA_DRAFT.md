# Social Media Draft (Internal — Not Published)

Status: **DRAFT ONLY**. Nothing in this file has been posted anywhere. Adapt per-platform before any actual publishing decision, and keep every source link attached.

Primary language: Chinese (Xiaohongshu-first framing per the boss's original ask), with an English adaptation note at the end for LinkedIn/X.

---

## 小红书 / 公众号 草稿

**标题候选：**
- 我看了 39 个 Claude/Codex Design Skills，真正值得收藏的是这 12 个
- Design Skills 不只是 Prompt：这些项目真的有完整 workflow

**正文：**

最近为了搞清楚 "AI coding agent 的 design skills" 到底靠不靠谱，系统看了一圈：从 GitHub 上找了 39 个和设计相关的 Claude / Codex skill 或资源，深入看了源码、SKILL.md、workflow 逻辑的有 19 个，最后觉得真正站得住脚、进入精选清单的，是 12 个。

先说结论：**大部分"设计 skill"本质上只是一段写得比较好的 prompt**，没有代码、没有验证机制，效果完全取决于模型当天的状态。真正好的那一小撮，共同点很明确：

1. **有确定性的检查机制，不是纯靠模型"感觉"** —— 比如 `impeccable`，内置 59 条反模式规则（渐变滥用、字体默认值、卡片嵌套……），不调用 LLM 就能跑检测，跨 14 种 agent 工具都能用。
2. **有"渲染-截图-检查-修复"的闭环** —— 比如 `excalidraw-diagram-skill`，生成图表后自己截图、发现布局问题、迭代修好再交付，而不是生成完就结束。`styleseed` 更进一步，做了"规则打分 + 像素级渲染校验"的双重验证，甚至把自己的得分（58/100）公开挂在官网上，挺诚实的。这个方向里最干净的一个是 `visual-verdict`：直接输出结构化 JSON（0-100 分 + pass/revise/fail + 具体差异点），卡在 90 分阈值上，天然适合接进一个"改到过为止"的自动循环。
3. **领域知识是具体的，不是"好看"这种形容词** —— 比如 `product-shots`，把亚马逊图片合规规则直接写进生成 prompt，还用 14 个"身份锚点"保证同一个模特在 9 个角度里长得一致；`guizang-social-card-skill` 专门做小红书图文卡片，两套视觉系统（Editorial / Swiss 网格）背后是真实的排版逻辑，还有脚本自动检查溢出、碰撞、密度问题。

**几个可能出乎意料的发现：**
- Anthropic 官方在 `claude-code` 仓库里自己就带了一个 `frontend-design` skill，内容比很多第三方项目更完整——直接看官方原文比看二手安利更有信息量。
- 有的"热门"资源打开一看，验证机制很弱，或者只是一份规则清单，没法确认规则细节的深度（比如平台设计规范打包类项目），这类我们标成"证据不足"，没有放进强推荐名单。
- 一个叫 `composio` 的名字混进了讨论里，查证后发现它其实是通用的 MCP/集成平台，跟"设计"没什么关系——顺手也把这个搞清楚了。
- 专门做"品牌方向"的 skill 出奇地少——39 个候选里只找到一个（`brand-skills`），15 个子 skill 覆盖命名、定位、口吻、视觉识别简报，产出持久化的 `brand.yaml`，而不是聊完就没了的对话内容。
- 真正"Codex 原生"的 design skill 明显更少——一开始找到的几乎全是 Claude 生态的东西，专门补搜了一轮才找到 `Codex-Skills`（TheGoat395）：约 70 个真代码、有结构的 skill，覆盖视觉方向、动效、无障碍、视觉 QA，还老老实实标注"这是仓库自己的评分，不是 OpenAI 官方评测"。反倒是 OpenAI 官方那个被当作"当前范例"的 `openai/plugins` 仓库，查证时发现已经被归档（archived）了——Codex 这边的生态确实还在变动期，比 Claude 侧更不稳定。

**用之前一定要看的注意事项：**
- `guizang-social-card-skill` 是 AGPL-3.0 协议，二次开发或做成 SaaS 都需要开源，商用前务必确认。
- `product-shots` 需要外部图片生成 API key，涉及成本和第三方依赖。
- 不少 skill 需要本地跑 Node/Python/Playwright，属于"需要执行代码"的范畴，装之前建议先看源码，不要 curl | bash 式地无脑安装。

以上都是基于公开仓库的静态审阅（没有实际安装运行第三方代码），如果有出入欢迎指正，所有链接都在原文里。

---

## English adaptation note (for LinkedIn / X)

Keep the same structure and the same 12 resources, but lead with the finding rather than the count: *"Most 'AI design skills' are just a well-written prompt with no validation loop. The ones that actually hold up share three traits: deterministic checks instead of vibes, a render-inspect-fix loop, and domain knowledge specific enough to cite (not 'make it look modern')."* Then walk through 3–4 of the strongest examples (`impeccable`, `styleseed`, `product-shots`, `guizang-social-card-skill`) with the same caveats (AGPL license, API-key dependency, static-review-only methodology). Add one line for balance: most strong finds skew Claude-side, but `Codex-Skills` (TheGoat395) is a genuine, well-structured Codex-native counterpart worth naming explicitly — don't let the post imply this is Claude-only territory. Keep all GitHub links attached; do not reproduce large blocks of any project's own README text — this draft only paraphrases.
