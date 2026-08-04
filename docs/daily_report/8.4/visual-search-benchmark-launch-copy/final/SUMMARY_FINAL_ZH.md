# 审核材料 — 三平台发布文案 FINAL 版（2026-08-04）

**状态：文案已完成，尚未发布，需要你审核后才能对外发出。本文件是这次修订的最终版本，替代同目录上层
的 `BOSS_REVIEW_SUMMARY_ZH.md`（那份是修订前的版本，仓库文档口径当时还有问题，仅供留档对比）。**

## 1. 这一轮做了什么

在上一版文案完成之后，仓库工作分支上又发生了两次只改文档、不改数据的修正提交
（`0cb6f07`、`cd2f5e4`），把上一版文案里明确指出的"319 vs 318"文档口径冲突，以及另外几处措辞问题
（人工审核表述、文件大小声明、截图证据表述）都修好了。这一轮工作内容：

- 重新从仓库只读核对了一遍所有关键数字，确认修正已生效（318/1/7、319 automated + 7
  automated_retry、326/326 覆盖率等）。
- 重新核对了 Git 状态，发现一个新情况：**`main` 分支目前落后工作分支两个提交**，上面说的文档修正还
  没有同步到 `main`（详见第 6 点）——这和上一版文案写的"main 已经和工作分支完全一致"不一样了，是本轮
  新发现。
- 修正了 LinkedIn 个人版草稿里一句没有证据支持的表述（"采集过程中遇到 CAPTCHA、cookie 同意墙"）——重
  新核对 manifest 数据后发现，326 条 Google Images 记录里 `consent_detected`/`captcha_detected` 全部
  是 `false`，即发布出来的证据里从未出现过 CAPTCHA 或同意墙，只有超时和页面加载竞态问题，已按事实改
  写。
- 修正了 HN 草稿里"两个 benchmark 都有内部人工复核流程"这个不准确的笼统说法，改成分别说明
  68-query（0/68 完成，rubric 准备过但没人做）和 326-query（内部有，但未公开）两种不同情况。
- 三平台文案全部重新组织进 `final/` 目录，标出 `COPY-READY` 区域方便你直接复制，内部提示单独放进
  `INTERNAL REVIEW NOTE — REMOVE BEFORE POSTING` 区块，不会混进可复制正文。

## 2. 两个 benchmark 的范围（未变）

- **68-query：** Curify 自己搜索相关性的"金标准"查询集，68 条精选查询，其中 12 条有跨平台真实截图
  证据（Curify/Bing/Google Images/Canva/Pinterest，共 62 张图）。
- **326-query：** 用来回归测试 Curify 搜索相关性 pipeline 两个代码版本（生产基线 vs. 候选分支）的
  326 条查询（中文 163 / 英文 163），`evaluations.csv` 652 行打分结果。

两者是分开发布、不合并成一个 benchmark 的两套独立数据。

## 3. 最新截图覆盖情况（本轮重新核对）

- Google Images：326/326，全部 `status=success`，`consent_detected`/`captcha_detected` 全部为
  `false`（即发布证据里没有 CAPTCHA、没有同意墙）。
- Curify：326/326，全部 `status=success`。

## 4. 318/1/7 口径已经修正（本轮最重要的确认）

上一版文案发现的问题——`README.md`、`METHODOLOGY.md`、`data/326-query/README.md` 把"319 = 自动化采集
方式计数"误标成"319 = 标准搜索结果页计数"，其中 `README.md` 那句话加总还多出 1（等于 327，超过总数
326）——**已经在工作分支上修好了**，分两次提交：

- `0cb6f07`：修正 `README.md`、`METHODOLOGY.md`、`SOURCE_AUDIT.md`、`data/326-query/README.md` 四个文
  件，统一为 318 个标准搜索结果页 + 1 个真实零结果页（V078 "bobblehead"）+ 7 个 topic-redirect 页
  =326，并把"采集方式"（319 automated + 7 automated_retry）和"页面类型"（318/1/7）两个统计口径分开
  写清楚。
- `cd2f5e4`：修正了另外几处相关联的模糊表述（`provenance.json` 里"319 standard + 1 zero-result"这句
  容易被误读成 320 的写法、`curify/gallery.html` 首页摘要里同样的口径混淆、`VALIDATION_REPORT.md` 里
  一句和 `SIZE_REPORT.md` 矛盾的文件大小声明、README 里暗示"两个 benchmark 都完成过人工复核"的措
  辞）。

本轮三平台文案全部使用修正后的 318/1/7，不再使用有问题的"319 标准页"表述。

## 5. 三个平台文案分别采取什么角度

- **Hacker News（Show HN）：** 技术向、克制，重点讲"为什么建这个 benchmark + 能下载什么 + 326-query
  截图证据 + 截图不是打分 + 主动列限制"。标题推荐：`Show HN: Visual search benchmark with screenshot
  evidence for all 326 queries`。FAQ 里"是否人工复核"这一条这次改成分开说明两个数据集各自的真实情
  况，不再用容易误导的笼统说法。
- **Reddit：** 只锁定 r/datasets、r/computervision 两个独立发帖 + r/MachineLearning 的
  self-promotion 帖内评论（不单独发帖）。三篇正文完全不同，各自附带身份披露（"Disclosure: I worked
  on assembling and validating this benchmark."）和针对性讨论问题。**本环境无法直接访问 Reddit 核实
  当前规则（`reddit.com`/`old.reddit.com` 均被网络策略阻断），因此每个目标前面都加了"发布当天必须人
  工重新核实规则"的强制提示，不能跳过。**
- **LinkedIn：** 个人版突出"我参与的数据采集/验证工作 + 真实遇到的坑（网络超时、页面加载竞态、7 个
  redirect 误判被及时纠正、零结果页面如实发布）+ 感谢原始评测团队"——**这次把没有证据支持的"CAPTCHA、
  cookie 同意墙"说法删掉了，换成 manifest 数据和 `METHODOLOGY.md` 里实际记录的问题**；公司版突出
  "benchmark 范围 + 可复现性 + 对搜索工程师/研究者的价值 + 准确限制"；短版本用于同周技术向转发或作为
  carousel 文案。推荐优先发个人版。个人字符数 2,478（目标区间 2,300–2,600），公司版 1,703（低于
  3,000），短版 605（低于 1,000）——均已在本轮重新实际计算。

## 6. 当前工作分支和 main 的状态（本轮新发现，请重点看）

- **工作分支：** `baobao/publish-visual-search-benchmarks-2026-07-30`，当前 HEAD
  `cd2f5e4ad5db49fc1a0f47a125e5a760073d19be`，已推送到远程，工作区干净。
- **`origin/main`：** `22414abf6e6f7a4d4453a647c46bc4765119d6c8`。
- **关键变化：main 现在落后工作分支两个提交（`0cb6f07`、`cd2f5e4`）。** 也就是说，第 4 点说的所有文
  档修正，目前**只存在于工作分支，还没有进入 `main`**。如果现在直接把仓库默认地址
  （`https://github.com/super-inbox/visual-search-benchmark`）贴到三个外部平台，读者点进去看到的
  `main` 分支上 `README.md`/`METHODOLOGY.md`/`SOURCE_AUDIT.md`/`data/326-query/README.md` 里仍然会写
  着"319 个标准搜索结果页"这个有问题的旧表述，和你即将发布的文案里的"318"对不上。
- 这和上一版文案的结论（"main 已经和工作分支字节级一致，可以直接用默认分支链接"）**不再成立**——那是
  更早一次会话核实的结果，在这两次文档修正提交之前是对的，现在不是了。
- 本轮全程只执行了只读 `git`/`gh` 命令（`git status`、`git diff --stat`、`git rev-parse`、
  `gh pr list` 等），**没有执行任何 `git add`/`commit`/`push`，没有创建或合并任何 PR**，严格遵守本次
  任务的限制。

## 7. 还需要你确认的事项

1. **是否批准三平台最终文案**（`HACKER_NEWS_FINAL.md`、`REDDIT_FINAL.md`、`LINKEDIN_FINAL.md`）。
2. **是否先把 `0cb6f07`、`cd2f5e4` 同步到 `main`，再对外发布**——建议先同步，避免读者点进仓库看到和
   文案数字对不上的"319"旧表述；具体走 PR 还是直接合并由你/仓库维护者决定，本轮没有替你做这个决定，
   也没有创建 PR。
3. **LinkedIn 用个人账号还是公司账号发布**，@ 提及队友时用谁的 handle（本轮没有猜测任何人的
   LinkedIn handle，全部留空待你/本人确认）。
4. **Reddit 三个目标社区是否认可**（r/datasets、r/computervision 独立发帖 + r/MachineLearning 自我推
   广贴内评论）——发布当天必须人工重新核实各社区当前规则，这不是本轮能替你确认的事项。
5. **是否批准正式发布**——本轮没有发布任何内容到 HN/Reddit/LinkedIn，没有登录任何外部平台。
6. **第三方截图版权表述是否需要法务再看一遍**——尤其是 `CITATION.cff` 新加的 `abstract` 字段和三平
   台文案里"third-party screenshots are evidence only, not CC BY 4.0"这句话，是否符合公司当前的法务
   要求。

## 8. 当前没有正式发布到外部平台

**本轮没有发布任何内容到 Hacker News、Reddit 或 LinkedIn，没有登录任何外部平台，没有执行任何
`git add`/`commit`/`push`，没有创建任何 PR。** 所有产出文件都在本地未跟踪目录
`/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/8.4/visual-search-benchmark-launch-copy/final/`
下，等待你审核。

## 9. 没有创建 PR

同上——本轮只对 benchmark 仓库执行了只读 `git`/`gh` 检查命令，没有修改仓库本身、没有创建或合并任何
Pull Request。

## 10. 推荐发布顺序

1. **先决定并执行 `main` 同步**（第 7 点第 2 项），避免文案发布后被读者发现仓库页面和文案数字不一
   致。
2. **Hacker News 优先**（一次性事件，适合先发，观察反馈后再决定其他平台的措辞是否需要微调）。
3. **LinkedIn 个人版**（可以引用 HN 上的早期反馈，如果有的话）。
4. **Reddit 三个目标**（分散在不同时间发，不要在同一天集中发布同一份数据到三个 subreddit；
   r/MachineLearning 的评论要等到该 subreddit 当前的 self-promotion 帖子存在时才能发；发布当天必须人
   工重新核实规则）。

每一步之间建议间隔至少一天，方便根据前一步的反馈调整后续文案。
