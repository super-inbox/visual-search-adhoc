# 300+ Easy Query Validation 完成后的更新说明

本文档记录 Prompt 8（300+ Easy Query Validation）完成后，应如何更新本 Work Report 及关联文件。**本文档本身不包含任何 300+ 的结果数据**——撰写时该验证仍在并行运行，未被读取。

---

## 1. 完成后应读取哪些文件

```text
scripts/easy-query-validation-300plus/ 下的正式输出（脚本产出的 CSV/JSON）
docs/daily_report/7.14/search-relevance-stage7-rerun/easy-query-validation-300-plus/ 下的正式 Markdown 报告与 Manifest
```

读取前应比照本报告第 4 节（安全检查）的做法：先核对该目录的 Manifest/输出文件是否已冻结（存在 Summary 报告 + Manifest JSON 且非临时 checkpoint），避免读取到中间态数据。

## 2. 应更新哪些章节

在 `CURIFY_SEARCH_RELEVANCE_WORK_REPORT_2026-07-13_TO_2026-07-14_zh.md` 中：

```text
第 1 节 Executive Summary        — 补充300+的核心结论，更新"是否已完全满足要求"判断
第 7 节 核心量化结果              — 新增300+ Easy Query的Zero/Low/Regression Gate实测数字
第 12 节 是否满足项目负责人要求         — R13（300+ Easy Query）状态从IN_PROGRESS更新为COMPLETE或COMPLETE_WITH_LIMITATIONS
第 13 节 完成度                  — 三种口径均需重新估算（尤其"项目负责人完整任务清单"口径）
第 14 节 300+ Easy Query章节     — 从IN PROGRESS占位替换为完整实测结果
第 21 节 当前风险与限制           — 移除或收窄"无法排除普通Query系统性回归"这一条
第 22 节 下一步                  — 根据300+结果调整后续步骤顺序
末尾 报告状态                    — 从WORK_REPORT_COMPLETE_PENDING_EASY_QUERY_UPDATE
                                   更新为WORK_REPORT_COMPLETE_WITH_LIMITATIONS（或视结果调整）
```

在 `CURIFY_SEARCH_RELEVANCE_REQUIREMENT_STATUS_2026-07-14.csv` 中：

```text
R12（Easy Low-result正式清单）— 视300+是否已包含该清单，更新status
R13（300+ Easy Query）        — status从IN_PROGRESS更新，补充evidence_file
R19（完整回归）                — 视300+结果更新
```

## 3. 应替换哪些 `PENDING`

搜索本报告全文以下占位符并替换为实测数字：

```text
IN PROGRESS / PENDING FINAL RESULT
```

出现位置：第 1 节 Executive Summary、第 14 节整节、第 15 节 R13 行。

## 4. 应重新计算哪些完成度

- 第 13.3 节"项目负责人完整任务清单"完成度需重新估算（300+ 完成后至少 R13、可能 R12/R19 也随之更新，数量占比与工作量占比均会上升）。
- 第 13.1/13.2 节（搜索机制技术主线 / 两天阶段工作）**通常不受 300+ 结果影响**，除非 300+ 发现新的系统性回归需要追加 Guard 修复。

## 5. 是否改变 Final Conclusion

**视 300+ 的 Regression Gate 结果而定**：

- 若 300+ 确认无系统性回归 → Final Conclusion 可从 `WORK_REPORT_COMPLETE_PENDING_EASY_QUERY_UPDATE` 更新为 `WORK_REPORT_COMPLETE_WITH_LIMITATIONS`（Taxonomy/Content/PR 等仍未完成，limitations 不会完全清零）。
- 若 300+ 发现新的系统性回归 → 需要评估是否撤销"冻结候选版本"的决定，可能需要新增 Prompt 8.5（Easy Query Guard 修复）章节，Final Conclusion 可能需要标注为 `BLOCKED` 或新增专门的回归风险章节，**不应直接沿用当前的正面结论**。

## 6. 不应修改哪些历史结论

以下结论**不因 300+ 结果而改变**，更新时不得覆盖或删除：

```text
7.13 的第一轮结果（PASS/PARTIAL/FAIL=0/4/64）——历史事实，不因后续验证而改变
7.14 68条Hard Query的最终数字（4/42/22，Broad 67.6%，Strict 5.9%）——已独立验证锁定
D模式>=1000从23降至2、Full-catalog清零——已确认的机制性改善
12 P0截图判定（0 PASS/5 PARTIAL/7 FAIL）——已完成的截图证据，不因300+结果而改变
Remaining Hard Cases的65条根因/Owner/优先级分类——独立于Easy Query验证的既有分析
Guard迭代历史（Prompt2→2B→2C→2D的四轮修复过程与各自Gate结论）——历史记录
```

300+ 完成后的更新应体现为**新增/补充**内容，而非重写或删除以上已锁定的历史结论。
