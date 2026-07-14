# 搜索优化效果 — 项目负责人一页摘要（2026-07-14）

## 做了什么

本轮完成了中文复合短语保护、Low-result / LLM Rewrite Guard、68 条 Hard Query A/B/C/D 重跑、独立人工验收（Prompt 5）和 12 个 P0 Before/After 截图验证（Prompt 6）。本报告是对以上已冻结结果的只读汇总对比，未新增任何代码修改，未重新运行搜索。

## 68 条核心数字

| 指标 | 优化前 | 优化后 | 变化 |
|---|---:|---:|---:|
| PASS / PARTIAL / FAIL | 0 / 4 / 64 | 4 / 42 / 22 | FAIL -42（-65.6%） |
| Broad 改善率（PASS+PARTIAL） | 5.9% | 67.6% | +61.7pp |
| Strict 完全通过率（PASS） | 0.0% | 5.9% | +5.9pp |
| D 模式 `>=1000` 结果洪泛 | 23 条 | 2 条 | -91.3% |
| D/C 模式 Full-catalog（整表返回） | 2 / 1 条 | 0 / 0 条 | -100% |

**注意**：Broad 67.6% ≠ "67.6% 完全修复"。42 条 PARTIAL 中约 21-23 条是 0 结果的目录内容缺口案例，对用户仍不可用。真正用户可感知的相关性提升（PASS + 真实部分改善）约 18/68（26.5%）。

## 12 P0 核心数字

```text
PASS = 0   PARTIAL = 5   FAIL = 7
可作为成功证据：0 条
可作为部分改善证据：4 条（须附限制说明）
可作为剩余问题证据：8 条
```

## 最明确的改善

**结果洪泛机制性改善**：D 模式 `>=1000` 异常从 23 条降至 2 条，C/D 模式 Full-catalog（返回整个 3209 条目录）从存在案例降为 0。这是证据等级最高、可直接引用的改善。

## 最主要的剩余问题

- 22 条 Verified FAIL 中 14 条（64%）是**目录内容缺口**，需要 Content/Catalog 团队采购/生产内容，非算法可解决。
- 12 个 P0 中 0 条完全修复；1 条错误实体（NCT Dream → ILLIT）需要 Search 团队修复主体身份校验。
- 4 条已知的 Tokenizer 精度/召回回归（已上线 Stage 6，非本阶段引入）。

## 当前是否已全部完成

**未完全完成**。300+ Easy Query Validation（Prompt 8）正在并行运行中，尚无法排除已上线 Tokenizer 变更对普通查询的系统性回归风险；Taxonomy Dry-run 未启动；Content/Catalog 缺口未开始处理。

## 下一步

1. 等待 300+ Easy Query Validation 完成，确认无系统性回归。
2. 6 条范围窄、证据 HIGH 的直接代码修复候选（1 条 Wrong Entity + 5 条 Tokenizer）可优先安排 Search/Tokenizer 团队处理。
3. Content/Catalog（42-43 条缺口，含 15 条小红书/抖音社交电商运营格式簇）与 Taxonomy（8 条候选）可并行启动，不阻塞 Search 侧工作。
