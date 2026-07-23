# Curify 模板品类发现 — Top 10 推荐报告（V2 修订版）

日期：2026-07-23（V2 修订）· 基于 Task A 最新 326 全量评测（commit `0e794cd9`，直接复用，未重新跑）

本报告是对 `docs/daily_report/7.23/template-discovery-top10-2026-07-23/`（v1）的**针对性修正与视觉证据补充**，
不是从零重做的新分析。v1 包中的有效结论予以保留；仅纠正管理层review中指出的 5 类问题。完整的问题-修正对照见
`00_REVISION_CONTEXT.md` 和 `01_CURRENT_PACKAGE_AUDIT.csv`。

---

## 0. 本次修订的排序规则（新增，必须优先说明）

本次修订采用并明确记录以下排序规则，应用于所有文件：

**排序依据：优先级（Priority）> 状态（Status）> 证据调整分（Evidence-Adjusted Score）> 候选 ID（并列时的最终裁决）**

1. Priority：P0 > P1 > P2
2. Status：CONFIRMED（已确认） > PROVISIONAL（暂定），仅在同一 Priority 内比较
3. Evidence-Adjusted Score：同一 Priority + Status 内按降序排列
4. Candidate ID：最终并列裁决（本轮未出现并列）

v1 版本的排序在同一优先级/状态分组内仅按证据调整分排序，但缺少显式的 Status 步骤，导致两处排序错误：
- 证书（T01，评分 50.2）曾排在价格标签（T05，评分 62.2）之前——两者同为 P1 CONFIRMED，应按分数高低排列，
  V2 已更正为 T05（#4）先于 T01（#5）。
- 优惠券（T09，评分 20.1）曾排在拼图（T08，评分 29.5）之前——两者同为 P2 PROVISIONAL，V2 已更正为
  T08（#8）先于 T09（#9）。
- 香水（T07，评分 71.0，PROVISIONAL）排在两个 CONFIRMED 候选之后——经核实这是**正确**的，因为 Status 优先于
  分数，无需修改。

**所有文件不再使用含糊的"Score"列**，统一使用 `raw_opportunity_score`（原始机会分）、
`evidence_adjusted_score`（证据调整分）、`evidence_completeness_pct`（证据完整度）三个显式字段。

---

## 1. 推荐的 10 个模板品类（V2 修正排序）

| 排名 | 品类（中文） | English | 优先级 | 状态 | 置信度 | 原始分 | 证据调整分 |
|---|---|---|---|---|---|---:|---:|
| 1 | 练习册/习题册封面合集 | Workbook & Practice-Book Cover Collection | P0 | **CONFIRMED** | HIGH | 86 | 86.0 |
| 2 | 传单/促销单页合集 | Flyer & Promotional-Flyer Templates | P0 | **CONFIRMED** | HIGH | 85 | 85.0 |
| 3 | STEM课堂教具图解合集 | STEM Classroom Teaching-Aid Illustrations | P0 | **CONFIRMED** | HIGH | 80 | 66.4 |
| 4 | 价格标签/商品吊牌合集 | Price Tag & Product Label Templates | P1 | **CONFIRMED** | HIGH | 75 | 62.2 |
| 5 | 证书与荣誉奖状合集 | Certificates & Achievement Awards Collection | P1 | **CONFIRMED** | HIGH | 75 | 50.2 |
| 6 | 香水/美妆瓶身包装样机合集 | Perfume & Cosmetic Bottle Packaging Mockups | P1 | PROVISIONAL | MEDIUM | 71 | 71.0 |
| 7 | 巧克力/节日礼盒包装合集 | Chocolate & Specialty Gift-Box Packaging | P1 | PROVISIONAL | MEDIUM | 65 | 43.5 |
| 8 | 拼图收藏品合集 | Puzzle & Jigsaw Collectible Templates | P2 | PROVISIONAL | MEDIUM | 59 | 29.5 |
| 9 | 折扣优惠券/代金券合集 | Discount Coupon & Promotional Voucher Templates | P2 | PROVISIONAL | MEDIUM | 61 | 20.1 |
| 10 | 冰箱贴/小型周边商品合集 | Fridge Magnet & Small Merch-Item Templates | P2 | PROVISIONAL | LOW-MEDIUM | 51 | 16.8 |

（第 4/5 名、第 8/9 名的顺序相对 v1 已互换，其余排名不变。原始分与证据调整分数值本身未变，仅排序逻辑被修正。）

完整字段见 `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv`。

---

## 2. Confirmed vs. Partial vs. Provisional —— 替换过度概括的表述（问题3的修正）

v1 版本的管理层摘要暗示"全部 10 个候选品类在每一个历史时间点都是零/低结果"，这一表述**过于绝对**。V2 明确
区分以下四种证据形态：

- **完全缺失（complete catalog absence）**：T01（证书）、T02（STEM教具）、T03（练习册）、T04（传单）、
  T05（价格标签）—— 这 5 个候选在生产基线、历史候选、最新评测**每一个**时间点上核心查询均为零结果，标记为
  **CONFIRMED**。
- **部分覆盖（partial catalog coverage）**：T06（巧克力礼盒）、T07（香水瓶）、T08（拼图）、T10（冰箱贴）——
  这 4 个候选的通用/相邻内容在 Curify 中确实存在（例如冰箱贴已有"城市地标"主题、香水瓶查询能召回一般瓶身
  内容），但**特定子类型**版式不存在。这不是"完全空白"，而是"品类内的子类型缺口"，标记为 **PARTIAL**。
- **搜索回归（search regression）**：`map`、`flashcard` —— 历史上曾有大量真实相关内容（7/17 截图证实），
  最新结果为零是检索链路问题，不是模板缺口，已排除在 Top 10 之外（详见第 5 节）。
- **跨语言检索不一致（cross-language retrieval inconsistency）**：拼图（T08）与优惠券（T09）——中英文查询
  的证据强度不对称，需要分别说明（详见第 3、4 节）。

**T09（优惠券）的分类标签为 CONTENT_GAP_CONFIRMED (EN only)**——即"英文查询确认，但并非在每一个时间点、每一种
语言下都零结果"，这是对 v1 过度概括表述的直接修正示例。

---

## 3. 拼图（T08）：中英文证据的区别对待（问题4的修正）

v1 版本已经部分注意到这一区别，但分类文件中存在一处矛盾：`07_SEARCH_VS_CONTENT_GAP_CLASSIFICATION.csv` 中
"puzzle (EN, mostly search-regression signal)" 一行被映射到 T08 且标记为"计入 Top10 证据"，这与文件中另一行
独立存在的、正确标记为排除的通用 "puzzle" 行相互矛盾。V2 已删除这一矛盾行。

**核实后的证据情况**：
- **拼图（中文）**：在生产基线、历史候选、最新评测三个时间点上均为 3 条结果——数量稳定但**持续不相关**
  （梵高博物馆/梵高盲盒等无关内容）。这是"部分覆盖"型证据，**支持 T08 的部分内容缺口判断**。
- **puzzle（英文）**：最新结果为 0，相对**生产基线**同样是 0（`STILL_ZERO`），并非从一个真实可用的基线下降
  而来；唯一的非零数据点来自某个**非生产的中间候选构建版本**（162 条结果），且其 top5 标题为"东方明珠塔""帝国
  大厦""大雁塔"等旅游地标内容——本身就与拼图无关，属于噪声而非真实拼图内容消失的证据。

**结论（按要求明确写出）**：中文语义的证据支持一个可能的部分内容缺口；英文的零结果/回归现象被排除在内容缺口
判断之外。T08 保持 **PROVISIONAL**，不作确认级别调整。7/17 截图中 Curify 产品自身对"puzzle"查询显示"生成你
自己的模板"提示，作为独立的产品侧背景信息保留，但不作为本候选的主要量化证据。

---

## 4. 优惠券（T09）：中英文证据的区别对待（问题5的修正）

v1 版本将"discount coupon"（英文）标记为内容缺口证据，"优惠券"（中文）标记为搜索问题排除项，这一结构本身
方向正确，但**未说明依据**。V2 逐项核查了 `05_STATUS_TRANSITIONS_VS_PRODUCTION.csv`、
`06_STATUS_TRANSITIONS_VS_PREVIOUS_CANDIDATE.csv`、`12_REMAINING_FAILURE_ROOT_CAUSES.csv` 等历史结果文件，
结论如下：

- **discount coupon（英文）**：在生产基线、历史候选、最新评测**三个时间点上均为 0 结果**——是这 10 个候选中
  证据最"干净"的持续零结果案例之一。7/17 截图独立证实该缺口在 7/22 修复周期之前已存在。
- **优惠券（中文）**：相对**生产基线**同样是 0 结果（`STILL_ZERO`）；唯一的非零数据点同样来自某个**非生产的
  中间候选构建版本**（8 条结果），其 top5 标题为"孙悟空""猪八戒""蜡笔小新""老龄化社会影响""生育率下降"等——
  神话人物与人口学信息图，与优惠券/代金券完全无关，属于噪声而非真实优惠券内容消失的证据。

**三种可能性的判断（按要求逐一排除）**：
- **A. Curify 有优惠券内容，但某一语言检索失败** —— 排除：中英文在生产基线上均为零，不存在"一种语言能检索到
  内容、另一种语言检索不到"的情况。
- **B. 现有结果只是表面相关** —— 最接近实际情况：优惠券中文的"8 条结果"本身就是无关填充内容，不是真实优惠券
  相关素材的检索失败，而是候选构建版本噪声。
- **C. 存在真实的子类目缺口** —— 证据不足以单独确认（仅英文一条支撑查询，证据完整度全池最低 33%）。

**结论**：T09 的内容缺口判断**仅以英文"discount coupon"为依据**；优惠券（中文）被明确排除在判断依据之外，
但排除理由是"该数据点是噪声"，而非"表明存在语言特定的检索失败"。T09 保持 **PROVISIONAL / P2**，未作确认级别
调整。

---

## 5. 最新 326 评测中被排除的"假阳性"品类：为什么排除 map 和 flashcard

（本节结论与 v1 一致，未发现新证据推翻此判断，`map` 与 `flashcard` 仍然被排除。）

7/17 生产基线截图证实 `map`（60+ 条真实相关结果）与 `flashcard`（680+ 条真实相关结果）在 Curify 历史上均曾
有大量相关内容，最新一轮的零/低结果是检索链路的**回归问题**，不是模板品类缺失。将其误判为"内容空白"只会
浪费设计资源——应转交搜索工程团队排查，而非纳入 Top 10。完整分类依据见
`07_SEARCH_VS_CONTENT_GAP_CLASSIFICATION.csv`，图片证据见 `images/00_excluded-search-issues/`。

---

## 6. 视觉证据情况（问题1的修正 + 本次仓库搜索的新发现）

v1 版本的卡片主要展示 Curify 的搜索结果截图（证明缺口存在），但**没有清晰展示"推荐新模板应该长什么样"**。
V2 重新设计了全部 10 张卡片，明确区分三个视觉区域：

1. **CURIFY CURRENT GAP**（Curify 当前缺口）—— Curify 的真实搜索结果截图
2. **REFERENCE EXAMPLE**（参考样例）—— 精确匹配 / 相邻类别（明确标注"ADJACENT REFERENCE — NOT EXACT
   CATEGORY"）/ 或如实标注"REFERENCE IMAGE NEEDED"（暂无参考图片）
3. **RECOMMENDED VISUAL DIRECTION**（推荐视觉方向）—— 文字化的设计规格说明，明确标注"SPEC SKETCH — NOT A
   PHOTOGRAPH"（设计草案，非照片），不编造任何虚假的产品照片

本次针对全仓库 `docs/daily_report/` 目录（约 1600 张图片）按候选关键词（中英文）进行了扩展搜索
（`02_REPOSITORY_IMAGE_SEARCH_INDEX.csv`、`02_IMAGE_SEARCH_SUMMARY.md`）。一个后台搜索子任务因连接中断失败
未产出文件，本次搜索改为直接执行。

**新发现**：
- **T03（练习册）**：找到真实的 Canva 竞品截图（"Phonics Worksheets Kindergarten templates" 分类页），与同一
  基准测试中 Curify 对相同查询的零结果截图配对——这是 v1 中仅有文字记录、本次升级为真实图片的证据。标注为
  相邻类别（自然拼读练习页，非练习册封面本身）。
  - **重要说明**：`worksheet`（练习页）与 `phonics card`（自然拼读卡片）这两个裸查询在 Curify 中**确实返回
    相关真实内容**——这不是缺口。T03 的缺口被精确限定为"练习册封面/册子"这一版式，而非泛指所有练习类内容。
- **T04（传单）**：复合查询 `event flyer`（活动传单，不在原始双查询基准集内）在 Curify 中召回一个真实保存的
  "Event Flyer" 模板。这**不推翻**裸查询 `flyer`/`传单` 在每个时间点均为零结果的核心发现，但提示该缺口可能
  部分是通用词的检索/别名问题，而非纯粹的内容真空——已如实披露为排产前需要核实的注意事项，未据此改变
  T04 的排名或状态。
- **T05（价格标签）**：相邻查询 `product label`（商品标签）在 Curify 中召回真实相关内容（奶酪/橄榄油/咖啡豆
  产品标签）。缺口被精确限定为"价格/吊牌"这一小型标签子格式，而非泛指所有标签类内容。
- **T06（巧克力礼盒）**：v1 已记录但未拷贝的相邻茶叶礼盒 Pinterest 截图，本次经过重新视觉核实（确认确实是
  真实的茶叶礼盒/罐装包装照片，而非无关内容）后正式纳入本次图片目录。
- 其余 6 个候选（T01、T02、T05、T08、T09、T10 中除价格标签的语境说明外）**仍未找到**任何精确或相邻的本地
  竞品参考图片，如实标注为 REFERENCE IMAGE NEEDED，未使用无关图片填充或编造。

---

## 7. 仍然缺失的视觉证据

六个候选（T01 证书、T02 STEM教具、T05 价格标签、T08 拼图、T09 优惠券、T10 冰箱贴）在扩展搜索后仍然**没有**
任何精确或相邻的竞品参考图片；T04（传单）仅有文字记录的竞品分类证据，没有对应截图。这些位置在卡片和联系表中
均如实标注为 "REFERENCE IMAGE NEEDED"，而非编造或使用无关的填充图片。完整清单见 `11_MISSING_IMAGE_EVIDENCE.md`。

---

## 8. 管理层应优先审阅的内容

1. **T03（练习册）**：排名第 1，P0，CONFIRMED，证据完整度 100%——本轮证据最扎实的候选，**可优先批准**。
2. **T04（传单）**：排名第 2，P0，CONFIRMED，**仍是有力的 P0 候选**，但因复合查询 "event flyer" 能在 Curify 中
   检索到一个真实存在的模板，**建议在排产审批前先做一次别名/检索层面的快速核实**，以确认该缺口是内容问题、
   检索问题还是两者兼有——这不推翻裸查询 `flyer`/`传单` 在每个时间点均为零结果（`STILL_ZERO`）的核心发现，
   只是提示需要一次核实，而非无限期推迟批准。
3. **T05（价格标签）优先于 T01（证书）**：排序修正后，价格标签现排第 4，证书排第 5（v1 中顺序相反，已修正）。
4. **T02（STEM 教具）**：原始加权分全池最高（80/100），但因竞品证据缺失，调整后降至第 3 名——建议在排产前
   补充一次竞品截图核实。
5. **map 和 flashcard 的排除决定**：这两个不是模板缺口，而是搜索回归，应转交搜索工程团队而非设计团队。
6. **拼图（T08）与优惠券（T09）的中英文证据说明**：这两个候选的排产决策应基于本报告第 3、4 节的证据说明，
   而非笼统的"零结果"表述。
7. **仍需外部视觉调研才能进入生产审批的候选**：T01、T02、T05、T08、T09、T10（缺乏任何竞品参考图片）。

完整背景与逐候选详情见 `13_MANAGER_REVIEW_SUMMARY.md` 与 `13_MANAGER_REVIEW_TOP10.csv`。

---

## 9. 方法论与免责声明

- 本报告的 Task A 数据来源于 `docs/daily_report/7.22/cluster-ab-latest-fix-full326-2026-07-22/`，commit
  `0e794cd91396a96cd56fd1d8f7f1495909f3adc5`，326 题总量——**本次分析直接复用该结果，未重新运行评测**。
  Task A 基准数据本身在本次修订中**未被重新采集或修改**。
- 打分方法（100 分制原始分 + 证据完整度调整）见 `09_SCORING_METHOD.md`（V2 已补充明确的排序规则说明）。
- 本次分析、图片搜索与拷贝、卡片与联系表重新生成均**未修改任何前端源代码**，**未创建 git commit**，**未
  push**，**未创建 PR**。
- 本次修订未覆盖或删除 v1 包中的任何文件；v1 包完整保留在
  `docs/daily_report/7.23/template-discovery-top10-2026-07-23/`，本次工作全部输出至独立的 `-v2` 目录。
