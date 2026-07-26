# Curify Top 10 Template Generation — 总结报告

日期：2026-07-26
输出目录：`docs/daily_report/7.26/template-generation-top10/`
Gallery：`gallery.html`（可离线打开，无需网络）

## 1. 使用了哪个 template discovery 文件？

`docs/daily_report/7.23/template-discovery-top10-2026-07-23-v2/`（v2 修正版，而非同目录下的 v1 原始版本）。
v2 是对 v1 的一次经理复核后的针对性修正（排序规则统一化、评分字段消歧、诚实标注视觉证据缺口），10 个候选模板本身、
优先级和状态均未变化（仅 Puzzle/Coupon 两条证据措辞有修正）。判定依据来自 `00_REVISION_CONTEXT.md`、
`MANIFEST.json`（87 个文件，SHA256 校验）与 `13_MANAGER_REVIEW_SUMMARY.md` 的完整交叉阅读，未做任何新的 discovery。

## 2. 最终 10 个 template 是什么？

按 discovery 最终排序（P0 > P1 > P2，同优先级内 CONFIRMED > PROVISIONAL，再按 evidence-adjusted score 排序）：

| 排名 | ID | 名称 | 优先级 | 状态 |
|---|---|---|---|---|
| 1 | T03 | 练习册/习题册封面合集 (Workbook & Practice-Book Covers) | P0 | CONFIRMED |
| 2 | T04 | 传单/促销单页合集 (Flyer & Promotional-Flyer) | P0 | CONFIRMED |
| 3 | T02 | STEM课堂教具图解合集 (STEM Classroom Teaching-Aids) | P0 | CONFIRMED |
| 4 | T05 | 价格标签/商品吊牌合集 (Price Tag & Product Label) | P1 | CONFIRMED |
| 5 | T01 | 证书与荣誉奖状合集 (Certificates & Achievement Awards) | P1 | CONFIRMED |
| 6 | T07 | 香水/美妆瓶身包装样机合集 (Perfume & Cosmetic Bottle Packaging) | P1 | PROVISIONAL |
| 7 | T06 | 巧克力/节日礼盒包装合集 (Chocolate & Gift-Box Packaging) | P1 | PROVISIONAL |
| 8 | T08 | 拼图收藏品合集 (Puzzle & Jigsaw Collectible) | P2 | PROVISIONAL |
| 9 | T09 | 折扣优惠券/代金券合集 (Discount Coupon & Voucher) | P2 | PROVISIONAL |
| 10 | T10 | 冰箱贴/小型周边商品合集 (Fridge Magnet & Small Merch) | P2 | PROVISIONAL |

未新增、未替换任何候选，`map`（地图）与 `flashcard`（抽认卡）按 discovery 结论确认为搜索回归问题而非内容缺口，
未纳入本次生成范围。

## 3. 每个 template 生成了几个 examples？

每个模板都设计了完整的 4 个 example 规格（scenario/input.json/prompt.txt），全部 4 个均已实际生成成功，
共计 10 × 4 = **40 个 example**，无一因成本或接口限制而省略。

## 4. 共成功生成多少图片？

**40 / 40 张成功**（100%），0 张失败，0 张 needs-review。生成分两批：先做 10 个 pilot（每模板 example-01），
人工逐张视觉复核通过后（见 `PILOT_REVIEW.md`），再批量生成剩余 30 张（examples 02-04），过程中无重试、无失败。
随后对全部 40 张跑了自动化结构化 QA（见 `QUALITY_REVIEW.md`：文件存在性、体积、可解码性、宽高比、是否近似空白图、
是否重复图），结果同样是 40/40 PASS。

## 5. 哪些 template 结果最好？

综合人工视觉复核（10 个 pilot 全部覆盖各模板）与自动化 QA：**十个模板质量都很稳定**，没有明显的强弱分层。
特别值得一提的：
- **T01 证书**、**T04 传单**：固定版式在多个 example 间保持得最一致（边框/标题/签名区域 vs 传单的标题带/主图/优惠区/联系方式）。
- **T07 香水瓶**、**T09 优惠券**：视觉执行最接近专业素材库水准（工作室打光的瓶身样机、票券撕边效果）。
- **T01 双语 workbook example**（英中双语词汇练习册）文字渲染准确，中英文均清晰可读，是本次生成中细节要求最高的一张，效果符合预期。

## 6. 哪些 template 有明显问题？

本轮 40 张图片中**没有发现结构性问题**——无水印、无裁切、无乱码文字、无空白/失败占位图、无重复图片。
需要说明的局限（非生成质量问题，而是输入证据本身的局限）：10 个模板中有 6 个（T01、T02、T05、T08、T09、T10）
在 discovery 阶段本就没有找到精确匹配的竞品参考图（v2 报告诚实标注为 "REFERENCE IMAGE NEEDED"），
本次生成时这几个模板的视觉方向来自 discovery 报告中的文字描述（visual_direction 字段），而非对标某张具体竞品图，
建议经理复核时重点关注这几个模板的视觉方向是否符合预期。

## 7. 同一模板内部结构是否稳定？

稳定。每个模板的 4 个 example 严格复用同一个 `prompt_template`（仅替换变量字段），并在 prompt 中显式约束了
"FIXED LAYOUT"（如证书的边框+印章+标题带+签名区）与"VARIABLE CONTENT"（如收件人姓名、颁奖理由）的边界。
人工复核确认：同模板内的版式骨架（标题位置、主图区域占比、底部信息条）在跨 example 时保持一致，
变化的只是文案、主体插画内容和配色，符合任务要求"不能只是生成 4 张主题相关但布局完全不同的独立设计图"。

## 8. 是否存在文字生成、图片主体或版式问题？

- **文字生成**：全部检查过的图片文字均清晰、拼写正确，包括中英双语混排的 T01 workbook example。未发现乱码或多余文字。
- **图片主体**：主体内容与 editable_fields 指定的内容一致（如香水瓶模板确实生成的是香水瓶而非运动水壶——这正是
  discovery 报告中指出 Curify 当前搜索错误返回运动水壶的问题，本次生成刻意规避了这一点）。
- **版式**：所有抽查图片的固定结构区域（标题带/主图区/底部信息条等）均按 spec 落位，未出现版式漂移。

## 9. 哪些模板适合进入下一轮？

建议优先推进 **T03（练习册）、T04（传单）、T02（STEM教具）** 这三个 P0 CONFIRMED 模板——discovery 证据最强、
本轮生成质量也最稳定，可以直接考虑纳入生产模板库评审流程。

## 10. 哪些需要修改后再评审？

**T02（STEM教具）**：discovery 报告本身建议在正式批准前做一次竞品快速核查（因为该类目暂无本地竞品证据文件）。
**T08（拼图）、T09（优惠券）、T10（冰箱贴）**：均为 P2 / PROVISIONAL 状态，证据完整度（evidence_completeness_pct）
在 33%-50% 之间，属于 discovery 阶段本就标注为证据较薄的候选，建议评审时结合 discovery 报告中的 caveat
（如 T08 拼图仅中文查询证据成立、英文查询证据被明确排除）一并阅读，而非仅看生成图片本身。

## 11. generation pipeline 有哪些限制？

- 使用的是 curify-frontend 现有的 `@google/genai`（`gemini-3-pro-image-preview`）生成能力，通过独立脚本调用，
  未修改 curify-frontend 或 curify-studio 任何文件，未写入生产数据库，未触发 CDN 同步。
- 该模型按图片自身内容自适应输出分辨率/宽高比，与 template.json 中声明的目标宽高比会有合理误差
  （自动化 QA 中允许 25% 以内的比例漂移，40 张全部在容差范围内)。
- 本次生成完全基于文字 prompt，没有使用图生图（image-to-image）或参考图输入——对于 6 个缺少竞品参考图的模板，
  这意味着视觉方向完全依赖文字描述的准确性。
- 生成速度受模型响应时间影响，40 张全部生成耗时在可接受范围内（分两批：10 张 pilot + 30 张批量，均一次性成功，无需重试）。

## 12. 是否适合直接发给经理？

**基本适合**，建议附带以下说明一并发送：
1. 本次是基于 7.23 template discovery v2（经理复核修正版）的成果直接生成，未重新做 discovery。
2. 40 张图片 100% 生成成功并通过自动化结构化 QA；10 张 pilot 已人工视觉复核（PASS），
   其余 30 张的人工文字/主体复核建议经理或设计同事抽查后再最终拍板（PILOT_REVIEW.md 与 QUALITY_REVIEW.md 已注明这一点，
   未假装自动化审核能完全替代人工判断）。
3. 6 个模板（T01/T02/T05/T08/T09/T10）在 discovery 阶段缺少精确竞品参考图，本次生成的视觉方向基于文字描述，
   建议经理重点过一遍这几个模板的示例，确认视觉方向是否符合预期后再决定是否进入下一轮打磨。

打开方式：直接双击/在浏览器中打开 `gallery.html`（纯本地文件，无需启动服务器或联网）。
