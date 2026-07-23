# Curify 模板品类发现 — Top 10 推荐报告

日期：2026-07-23 · 基于 Task A 最新 326 全量评测（commit `0e794cd9`，直接复用，未重新跑）

---

## 0. 恢复说明

本次任务因 API 错误（"Response stalled mid-stream"）中断后恢复。经过对文件系统的逐项审计确认：结构化的
10 个候选品类数据集（`_candidates.json`）、来源清单（`01_SOURCE_INVENTORY.csv`）、31 条查询统一清单
（`02_UNIFIED_QUERY_INVENTORY.csv`）以及 26 张已拷贝证据图片在中断前均已完整生成，并逐一与原始来源文件做了
逐字节哈希校验，确认真实且可追溯，无需重新分析或重新采集。本次恢复只补齐了此前尚未生成的交付文件（详见
`RUN_LOG.md`）。Task A 的 326 题基准评测**没有被重新运行**。

---

## 1. 推荐的 10 个模板品类

| 排名 | 品类（中文） | English | 优先级 | 状态 | 置信度 | 加权分 |
|---|---|---|---|---|---|---:|
| 1 | 练习册/习题册封面合集 | Workbook & Practice-Book Cover Collection | P0 | **CONFIRMED** | HIGH | 86.0 |
| 2 | 传单/促销单页合集 | Flyer & Promotional-Flyer Templates | P0 | **CONFIRMED** | HIGH | 85.0 |
| 3 | STEM课堂教具图解合集 | STEM Classroom Teaching-Aid Illustrations | P0 | **CONFIRMED** | HIGH | 66.4 |
| 4 | 证书与荣誉奖状合集 | Certificates & Achievement Awards Collection | P1 | **CONFIRMED** | HIGH | 50.2 |
| 5 | 价格标签/商品吊牌合集 | Price Tag & Product Label Templates | P1 | **CONFIRMED** | HIGH | 62.2 |
| 6 | 香水/美妆瓶身包装样机合集 | Perfume & Cosmetic Bottle Packaging Mockups | P1 | PROVISIONAL | MEDIUM | 71.0 |
| 7 | 巧克力/节日礼盒包装合集 | Chocolate & Specialty Gift-Box Packaging | P1 | PROVISIONAL | MEDIUM | 43.5 |
| 8 | 折扣优惠券/代金券合集 | Discount Coupon & Promotional Voucher Templates | P2 | PROVISIONAL | MEDIUM | 20.1 |
| 9 | 拼图收藏品合集 | Puzzle & Jigsaw Collectible Templates | P2 | PROVISIONAL | MEDIUM | 29.5 |
| 10 | 冰箱贴/小型周边商品合集 | Fridge Magnet & Small Merch-Item Templates | P2 | PROVISIONAL | LOW-MEDIUM | 16.8 |

完整字段（受众、使用场景、视觉方向、变体建议、证据完整度等）见 `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv`。

---

## 2. P0 / P1 / P2 划分依据

- **P0**（本轮最优先，3 个）：T02、T03、T04。共同特征：内容完全缺失（不是"覆盖不足"）、在 4 轮独立基准评测
  中始终为零/低结果、且所在的 Task A 大类（`classroom_material`、`flyer` 等）整体通过率也很低，说明是系统性
  的品类空白而非个别查询的偶然现象。T02（算盘/abacus）额外获得两种独立方法学（7/20 regression-50 与 7/22
  最新评测）交叉验证，是全池中证据最扎实的候选。
- **P1**（次优先，4 个）：T01、T05、T06、T07。T01、T05 是内容完全缺失的确认型空白，但竞品证据缺失
  （NOT_FOUND），置信度略低于 P0。T06、T07 是"部分覆盖"型空白——通用巧克力/瓶身内容存在，但巧克力礼盒专用
  版式、香水瓶专用样机不存在，属于品类内的子类型缺口。
- **P2**（较低优先，3 个）：T08、T09、T10。共同特征：仅有 1-2 条支撑查询、证据完整度低于 50%、且存在部分
  现有覆盖（例如冰箱贴已有"城市地标"这一单一主题，但缺少其他通用场景）。这三个候选被明确标记为
  **PROVISIONAL（暂定）**，不建议在未补充竞品证据或额外查询验证前直接排产。

---

## 3. Confirmed vs. Provisional

- **CONFIRMED**（5 个）：T01、T02、T03、T04、T05 — 内容缺口在每一个已知历史时间点都成立（不只是最新一轮），
  且 7/17 真实截图证实缺口在近期修复周期之前就已存在，排除了"这是最近搜索改动导致的副作用"的可能性。
- **PROVISIONAL**（5 个）：T06、T07、T08、T09、T10 — 证据强度较弱，原因各不相同：T06/T07 是部分覆盖型缺口
  （通用内容存在，专用内容不存在，需要设计判断"缺口有多大"）；T08/T09/T10 支撑查询数量少（1-2 条）、部分
  查询存在跨语言的检索回归干扰、竞品证据缺失。这五个候选**不应被当作与前 5 个同等确定性的结论呈现**给
  管理层，而应标注为"值得关注但需要更多证据"的候选。

---

## 4. 最新 326 评测中被排除的"假阳性"品类：为什么排除 map 和 flashcard

在原始最新 326 结果里，`map`/`地图` 和 `flashcard` 看起来也像"内容空白"——当前结果数为零或极低。但交叉比对
历史评测和 7/17 生产基线真实截图后发现，两者在 Curify 历史上都**曾有大量相关内容**：

### 为什么排除 `map`
7/17 生产基线截图（`254_V254_map.png`，已保存于
`images/00_excluded-search-issues/map/curify_7.17_map_60plus_results.png`）显示 `map` 查询当时返回了 **60 条以上
真实相关的地图类结果**。这说明地图类模板内容在 Curify 内部是充足的，最新一轮的零/低结果是**检索链路的回归
问题**（很可能与近期的搜索改动有关），而不是模板品类缺失。将其误判为"内容空白"并推荐设计团队生产新地图
模板，只会浪费设计资源——真正需要做的是把这个发现转交给搜索工程团队排查。

### 为什么排除/降级 flashcard
7/17 生产基线截图（`248_V248_flashcard.png`，已保存于
`images/00_excluded-search-issues/flashcard/curify_7.17_flashcard_680_results.png`）显示 `flashcard` 查询当时返回
了 **680 条以上真实相关结果**。同样的逻辑：这是搜索回归，不是内容缺口，因此 `flashcard` 及其近义查询
（`vocabulary card`、`单词卡`）均被排除在 Top 10 之外，不作为"确认的内容空白"呈现。

两者的完整分类依据见 `07_SEARCH_VS_CONTENT_GAP_CLASSIFICATION.csv`，图片证据见
`images/00_excluded-search-issues/`。

---

## 5. 核心缺口最强的品类

- **教育与课堂材料类**（Education & Classroom Materials）：T02（STEM 教具）、T03（练习册）都属于此大类，
  且都是 P0 CONFIRMED，是本轮证据最扎实、覆盖面最系统的核心缺口区域。
- **证书/文档类**（Certificates & Academic Documents）：T01，7/17 截图显示 Curify 产品自身在页面上给出了
  "Generate 'achievement certificate' yourself"的提示语，即产品侧已自我承认该品类无匹配模板——这是比检索
  日志更直接的产品侧证据。
- **信息设计类**（Posters & Information Design）：T04（传单），该大类在 Task A 评测中相邻的 `poster_specific`
  子类反而是全评测集中表现最好的子类之一（31.2% 通过率），恰好反衬出"传单"这一独立版式（区别于海报的
  信息密集型单页）是被明确遗漏的子类型。

---

## 6. 竞品证据情况

仅 **T07（香水/美妆瓶身包装）** 拥有直接的竞品图片证据（小红书香薰种草图案例，Pinterest/Canva/Curify 三方
真实截图，已拷贝至 `images/07_perfume-cosmetic-bottle-packaging/competitor/`）。T03（练习册）、T04（传单）拥有
文字记录形式的竞品证据（Canva 筛选分类标签明确包含"Worksheet / Educational / Printable"及"Flyer / Travel
Flyer"，证明这是可比竞品已独立成类目的模板类型）。T06（巧克力礼盒）拥有相邻品类（茶叶礼盒，非巧克力）的
竞品截图佐证。其余 6 个候选（T01、T02、T05、T08、T09、T10）**未找到**任何本地竞品截图或文档，如实记录为
`NOT_FOUND`，未进行任何编造。详见 `06_COMPETITOR_ANALYSIS_SUMMARY.md`。

---

## 7. 仍然缺失的视觉证据

六个候选（T01、T02、T05、T08、T09、T10）没有竞品截图；T04 的竞品证据仅为文字记录，没有针对该查询的截图；
T06 的竞品证据是相邻品类（茶叶而非巧克力）的截图，未拷贝入本次目录（因主体不匹配）。在对应的推荐卡片
（`cards/`）和联系表（`TOP10_TEMPLATE_CONTACT_SHEET.png`）中，这些缺失位置使用了明确标注"No competitor
evidence on file"的占位符，而非编造或使用无关的填充图片。完整清单见 `11_MISSING_IMAGE_EVIDENCE.md`。

---

## 8. 管理层应优先审阅的内容

1. **T03（练习册）与 T04（传单）**：排名第 1、2，P0，CONFIRMED，证据完整度 100%，建议优先批准。
2. **T02（STEM 教具）**：原始加权分全池最高（80/100），但因竞品证据缺失，调整后降至第 3 名——建议在排产前
   补充一次竞品截图核实。
3. **map 和 flashcard 的排除决定**：这两个不是模板缺口，而是搜索回归，应转交搜索工程团队而非设计团队。
4. **T06-T10 的证据强度**：这 5 个候选标记为 PROVISIONAL，管理层审阅时应明确区分"已确认"和"待验证"的
   结论，避免以确认级别的语气对外汇报暂定结论。

完整背景与逐候选详情见 `13_MANAGER_REVIEW_SUMMARY.md` 与 `13_MANAGER_REVIEW_TOP10.csv`。

---

## 9. 方法论与免责声明

- 本报告的 Task A 数据来源于 `docs/daily_report/7.22/cluster-ab-latest-fix-full326-2026-07-22/`，commit
  `0e794cd91396a96cd56fd1d8f7f1495909f3adc5`，326 题总量，38 PASS / 86 PARTIAL / 195 FAIL / 7 UNJ，20 个零结果查询，
  18 个低结果查询——**本次分析直接复用该结果，未重新运行评测**。
- 打分方法（100 分制原始分 + 证据完整度调整）见 `09_SCORING_METHOD.md`。
- 本次分析、图片拷贝、卡片生成均未修改任何前端源代码，未创建 git commit，未 push，未创建 PR。
