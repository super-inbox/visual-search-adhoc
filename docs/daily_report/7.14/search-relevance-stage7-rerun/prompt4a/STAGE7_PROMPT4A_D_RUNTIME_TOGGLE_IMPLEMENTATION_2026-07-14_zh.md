# Stage 7 Prompt 4A d Runtime Toggle Implementation

## 1. Executive Summary

Prompt 4 首次尝试在正式运行前发现：当前 production 代码没有任何运行时开关可以关闭"d"（Stage 6 字典/分词特性），Mode A（d=OFF,g=OFF）与 Mode C（d=OFF,g=ON）因此无法用同一份当前代码构造，且唯一已知的构造方法（`git show HEAD:page.tsx` 重建旧逻辑）被 Prompt 4 明确禁止，最终以 `BLOCKED_INVALID_ABLATION_MODE` 停止。

本阶段（Prompt 4A）新增了一个显式、类型安全、默认不改变现有行为的 `dEnabled` 运行时开关，将 `buildSearchTokens`/`normalizeForSearch` 从 `page.tsx` 的私有函数提取为 `lib/searchTokens.ts` 的可复用纯函数，Search Page 与新建的 Mode Contract Eval Harness 现在导入**同一个**真实生产实现。修复后，A/B/C/D 四个模式均已通过 32/32 的 Mode Contract Smoke Test 验证可由同一套当前代码构造，0 次真实 LLM 调用，0 次 `git show`/旧代码重建/手工 token 删除。

全量单元测试 375/375 通过，TypeScript 0 错误，Production Build 通过。

**最终结论：`READY_FOR_MODE_CONTRACT_SMOKE`**（详见第 14 节，Smoke 已实际执行并通过，详见 `STAGE7_PROMPT4A_MODE_CONTRACT_SUMMARY_2026-07-14_zh.md`）。

## 2. Prompt 4 Blocker（复述，供独立阅读）

`app/[locale]/(public)/search/page.tsx` 的 `buildSearchTokens`（原第 151-241 行）无条件调用 `segmentCJKToken`（jieba 字典分词）与 `applyPhraseAliasRulesExcluding`（排除 `CJK_ATOMIC_PHRASES` 的 Phrase Alias 规则）。代码库中不存在第二套分词实现，也没有 `process.env`/参数/其他机制可以关闭这一路径。Prompt 4 第一次尝试因此以 `BLOCKED_INVALID_ABLATION_MODE` 停止，未运行任何 Query，未调用任何 LLM。阻塞记录见 `full-68-rerun/STAGE7_PROMPT4_BLOCKED_2026-07-14_zh.md`（本阶段未修改，只读）。

## 3. Confirmed d Contract

已读取以下文件确定"d"的准确定义：

- `/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.13/search-optimization-stage-7/run_manifest.json`（`run_modes` 字段）
- `/Users/baobaoli/Desktop/visual-search-adhoc/scripts/curify-search-collect-stage7/run_mode.cjs`（第 188-257 行，`buildSearchTokensOLD`/`buildSearchTokensNEW`/`scoreBlobOLD`/`scoreBlobNEW` 的并列实现，是旧 Stage 7 对"d"最精确的代码级定义来源——**只读引用，本阶段未执行 `git show` 或读取任何 git 历史，该文件本身是 7.13 阶段已创建、当前仍在磁盘上的现存产物**）
- 当前 `lib/query_phrase_aliases.ts`（`applyPhraseAliasRules` 第 283 行 vs `applyPhraseAliasRulesExcluding` 第 297 行；`segmentCJKToken` 第 450 行）
- 当前 `lib/cjk_tokenizer.ts`（`segmentText`，真实 jieba 封装）
- 当前 `app/[locale]/(public)/search/page.tsx` 修改前的 `buildSearchTokens`/`scoreBlob`

### d=ON（启用）

- `segmentCJKToken`：对每个含 CJK 字符的 raw token，先提取最长匹配、非重叠的 Protected Phrase spans，再对剩余部分调用真实 jieba 分词器（`lib/cjk_tokenizer.ts:segmentText`）。
- `applyPhraseAliasRulesExcluding`：在已被 `segmentCJKToken` 处理过的 `CJK_ATOMIC_PHRASES` 基础上，对剩余 token 施加 Phrase Alias 规则（ASCII 多词短语 + 未被吸收的 CJK 别名规则）。
- Concept groups（segmentCJKToken 产出）与 phraseResult.aliasGroups 合并为最终 `aliasGroups`。

### d=OFF（关闭，保留的基础功能）

- 保留：whitespace/结构标点切分、Stopword 过滤、英文复数词干化（这部分从未被"d"控制，新旧两版共享同一切分逻辑，见 `run_mode.cjs` 的 `splitAndStem` 在 OLD/NEW 间共用）。
- 保留：`applyPhraseAliasRules`（不排除 `CJK_ATOMIC_PHRASES` 的基础版本，当前代码中仍存在、仍被导出、仍有独立测试覆盖的真实生产函数，非新增）——Protected Phrase 规则仍会命中，只是不经过 `segmentCJKToken` 预处理。
- 关闭：`segmentCJKToken`（jieba 字典 CJK 分词）——不对 CJK token 做子词切分。
- 新增（本阶段，仅供 d=OFF 分支使用）：一个极简的 CJK bigram 兜底（`cjkBigramFallback`，10 行，仅在整条 Query 是单个未切分的 CJK 字符串且未被 atomicEntity 规则命中时触发），确保 d=OFF 仍有合法、非空的基础 tokenization，而不是简单复制旧 tokenizer 的复杂实现。

### 依据

见上方文件列表；`run_mode.cjs` 第 188-204 行的 `buildSearchTokensOLD` 与本阶段新增的 `buildSearchTokensDictionaryOff`（`lib/searchTokens.ts`）在**逻辑意图**上一致（都是"无字典增强的基础分词 + CJK bigram 兜底"），但**代码本身是本阶段独立重写**，不是复制——详见第 4 节的范围说明。

### 明确排除的范围（"哪些功能不属于 d"）

`scoreBlob`/`scoreQueryTokens` 的 Merge/Ranking/relaxed 匹配阈值（`ceil(n/2)`）**不属于**本阶段"d"开关的范围——历史上 7.13 的 Ablation 确实同时切换了 `scoreBlobOLD`/`scoreBlobNEW`（新增了 `relaxedOk` 概念），但 Prompt 4A 明确禁止修改 Ranking/Merge，因此本阶段的 `dEnabled` 开关**只**控制 tokenization 层（`buildSearchTokens`），评分逻辑（`scoreBlob`）在 A/B/C/D 四个模式下保持**完全相同**（当前唯一、未改动的实现）。这是本阶段对"d"合同的一处**明确、有意的范围收窄**，原因见第 13 节"Safety"。

## 4. Previous Architecture

修改前，`buildSearchTokens` 是 `page.tsx` 内的模块私有函数（未 `export`），Next.js Server Component 文件本身无法被 Node.js 脚本 `require()`（依赖 `next/navigation`/`next/headers`）。因此此前所有 Harness（`curify-search-collect-stage7`、`curify-search-stage7-guard-smoke`）都只能靠"逐字转录"复现这个函数，无法真正 import 它，也就没有天然的地方插入一个 options 参数——旧 Stage 7 的解决方案是转录两份（OLD/NEW），靠读取 git 历史获得 OLD 版本的源码；这正是 Prompt 4 被禁止复用的方法。

## 5. New Runtime Toggle

新文件 `lib/searchTokens.ts` 导出：

```ts
export type SearchTokenizationOptions = { dEnabled?: boolean };
export const DEFAULT_SEARCH_TOKENIZATION_OPTIONS: Required<SearchTokenizationOptions> = { dEnabled: true };
export function buildSearchTokens(query: string, options: SearchTokenizationOptions = DEFAULT_SEARCH_TOKENIZATION_OPTIONS): SearchTokens
export function normalizeForSearch(s: string): string
export const STOPWORDS: Set<string>
```

- 默认值为 `dEnabled: true`——不传 `options` 完全等价于修改前的唯一行为。
- 未使用环境变量、全局可变状态或 process-level 隐式开关；开关只是一个普通函数参数。
- 未暴露为 URL query 参数或任何真实用户可触达的入口——`page.tsx` 的两个调用点（原第 401、767 行，现第 267、633 行附近）均不传 `options`。

## 6. Shared Production Helper

- **Search Page**（`app/[locale]/(public)/search/page.tsx`）：`import { buildSearchTokens, normalizeForSearch } from "@/lib/searchTokens";`，两个调用点均不传 `options`（默认 d=ON）。
- **单元测试**（`lib/__tests__/searchTokens.test.ts`）：`import { buildSearchTokens, ... } from "../searchTokens";`，直接测试真实实现，覆盖 d=ON/d=OFF/默认值/差异 case。
- **Mode Contract Eval Harness**（`scripts/curify-search-stage7-mode-contract/`）：通过 esbuild 把 `lib/searchTokens.ts` 真实打包进 `_bundle_current.cjs`，`engine.cjs` 调用 `bundle.buildSearchTokens(query, { dEnabled })`——与 Search Page 使用**同一个**编译产物中的**同一个**函数，不是转录。
- 三者共享同一实现，未复制。`scoreBlob`/`scoreQueryTokens`（Merge/Ranking，第 3 节已说明范围外）仍是 Harness 内的转录（`scoring.cjs`），与本阶段之前的 `curify-search-stage7-guard-smoke` Harness 使用相同的、已验证的转录+漂移检测模式，未新增风险。

## 7. Default Behavior Preservation

用一个独立的、临时的 scratch 测试文件（运行后已删除，不留存于代码库）验证：把**本阶段编辑前**的 `buildSearchTokens`/`normalizeForSearch`/`STOPWORDS`（我在编辑 `page.tsx` 时读到的、被 `Edit` 工具原样替换掉的原始文本——非 `git show`，是本次会话自己刚执行的编辑操作留下的确切文本）作为参照实现，与新的 `lib/searchTokens.ts` 的默认路径（不传 options 与显式 `{dEnabled:true}` 两种调用方式）逐字段深度比较：

- Fixture 数量：14 条（小红书、小红书香薰产品、手冲咖啡、手冲咖啡品牌视觉、二手奢侈品、比亚迪海豹、抖音 product card、乔丹鞋、白箱、Genshin Impact fanart 4k、ES6、GPT-4 poster、English brand identity poster、光与夜之恋 卡面设计）。
- 修改前 vs 修改后默认行为：**0 处差异**（14/14 `toEqual` 断言全部通过）。
- 默认 vs 显式 `dEnabled:true`：**0 处差异**（14/14 全部通过）。
- Regression：**0**。

（该临时对比测试的完整运行记录见 `stage7_prompt4a_test_results_2026-07-14.json` 的 `default_behavior_verification` 字段。）

## 8. d=OFF Validation

同样通过临时 scratch 测试导出的真实运行结果（已归档进 `stage7_prompt4a_test_results_2026-07-14.json` 的 `d_off_evidence` 字段）：

- 受影响 Query（7 条测试）：小红书、手冲咖啡、二手奢侈品、比亚迪海豹、抖音 product card、乔丹鞋、白箱。
- **观察到预期差异的 Query（4 条，超过"至少 3 条"的要求）**：
  - `手冲咖啡`：d=ON 得到 `primary=[]` + `aliasGroups=[["手冲咖啡","brand identity","visual identity"]]`（Protected Phrase 消费了 primary token）；d=OFF 得到 `primary=["手冲咖啡"]` + `aliasGroups=[["brand identity","visual identity"]]`（基础规则未消费 primary token）——结构性差异。
  - `比亚迪海豹`：d=ON 得到 `primary=["比亚迪","海豹"]`（jieba 字典切分）；d=OFF 得到 `primary=["比亚迪海豹"]` + `bigrams=["比亚","亚迪","迪海","海豹"]`（未切分 + bigram 兜底）。
  - `乔丹鞋`：同上模式，d=ON 切分为 `["乔丹","鞋"]`，d=OFF 保留 `["乔丹鞋"]` + bigrams。
  - `白箱`：primary 相同（`["白箱"]`，2 字词 jieba 也不会再切分），但 `bigrams` 字段不同（d=ON 恒为 `[]`；d=OFF 为 `["白箱"]`）——仍是真实、非伪造的结构差异。
- 未观察到差异（3 条，符合预期，不构成 Gate 失败）：`小红书`、`二手奢侈品`、`抖音 product card`——这些 2-4 字 CJK 词本身既不含 Protected Phrase 规则，也不会被 jieba 进一步切分，d=ON/d=OFF 路径殊途同归，是**真实**的"该 Query 对 d 不敏感"，不是开关失效。
- 普通控制 Query（6 条：English brand identity poster / Genshin Impact fanart 4k / ES6 / GPT-4 poster / watercolor spring flowers / 光与夜之恋 卡面设计）：**全部 d=ON 与 d=OFF 逐字段相同**，且均为非空 token（`primary.length > 0`）——确认 d=OFF 不会让英文、数字、型号或正常 Query 变得不可搜索，也不会产生系统性空 token。

## 9. Four-mode Contract

Mode Contract Smoke Test（32/32，详见独立的 `STAGE7_PROMPT4A_MODE_CONTRACT_SUMMARY_2026-07-14_zh.md`）已直接验证：

| Mode | dEnabled | gEnabled | 真实 LLM 调用 | 验证结果 |
|---|---|---|---|---|
| A | false | false | 0 | 8/8 通过，仅基础 tokenization，Rewrite Provider 从未调用 |
| B | true | false | 0 | 8/8 通过，当前 d=ON tokenization，Rewrite Provider 从未调用 |
| C | false | true | 0 | 8/8 通过，基础 tokenization + 真实 Guard（`flattenPathsWithDiagnostics`）+ 固定 fixture |
| D | true | true | 0 | 8/8 通过，当前完整 production 组合（d=ON tokenization + 真实 Guard + 固定 fixture） |

## 10. Modified Files

**Prompt 4A 新建**：
- `lib/searchTokens.ts`（curify-frontend，新文件）
- `lib/__tests__/searchTokens.test.ts`（curify-frontend，新文件，19 条测试）
- `scripts/curify-search-stage7-mode-contract/`（visual-search-adhoc，新目录：`build_bundle.cjs`、`scoring.cjs`、`engine.cjs`、`run_smoke.cjs`、`rewrite_fixtures.json`、`csv_utils.cjs`〔复制自既有 guard-smoke Harness的通用 RFC4180 解析器，非 tokenizer/scoring/guard 逻辑〕、`node_modules`〔到 curify-frontend 的符号链接〕、`_bundle_current.cjs`/`_bundle_source_hashes.json`〔构建产物〕）

**Prompt 4A 修改**：
- `app/[locale]/(public)/search/page.tsx`：删除私有的 `STOPWORDS`/`normalizeForSearch`/`buildSearchTokens`（原第 107-241 行，134 行），改为从 `lib/searchTokens.ts` 导入；同步移除现已无用的 `tsToSc`/`applyPhraseAliasRulesExcluding`/`segmentCJKToken`/`CJK_ATOMIC_PHRASES` 直接导入（这些函数现在只被 `lib/searchTokens.ts` 使用）。**两个调用点的调用方式未变（不传 options），默认行为逐字段验证不变（见第 7 节）**。

**Prompt 4A 开始前已有修改**（本阶段未触碰，快照核对确认）：`lib/searchRewrite.ts`、`lib/query_phrase_aliases.ts`、`lib/zh_normalize.ts`、Blog 相关文件、`next.config.ts`、`package.json`/`package-lock.json`、`scripts/eval_search.cjs` 等——与执行前 `git status --short` 快照逐行一致（除 `lib/searchTokens.ts`/`lib/__tests__/searchTokens.test.ts` 两个新增文件外）。

## 11. Unit Tests

| 命令 | 结果 |
|---|---|
| `npx vitest run --config vitest.unit.config.ts lib/__tests__/searchTokens.test.ts` | 19/19 通过 |
| 全量单元测试 | **375/375 通过**（Prompt 2D 基线 356 + 本阶段新增 19） |

新增覆盖：默认值等价性（11.1）、d=ON 覆盖（Protected Phrase/CJK 字典切分/中英混合/型号 token/弱数字属性，11.2）、d=OFF 覆盖（字典增强确实关闭/基础 tokenizer 工作/非空/不调用 jieba 字典切分/英文与数字型号 Query 不受影响，11.3）、ON/OFF 差异（11.4，5 条）、`normalizeForSearch` 复用验证。`searchRewrite.test.ts`（160 条，含全部 Prompt 2D Piggyback/Anchor Provenance/`anchorBasisForDownstream`/`bindTarget` 回归测试）、`stage6_dictionary_hybrid.test.ts`（61 条）、`search_metadata_scenarios.test.ts`（65 条）、`thin_recall_queries.test.ts`（28 条）**全部继续通过，零回归**。

## 12. TypeScript and Build

- `npx tsc --noEmit`：0 错误。
- `npm run build`：exit 0，成功，无新增/非既有错误。
- Lint：与 Prompt 2B/2C/2D 相同的 ESLint 9 flat-config 预存问题（`next/core-web-vitals` extends 语法不兼容），未修复，未扩大修复范围。

## 13. Safety

- 未使用 `git show`、未读取任何 git 历史提交、未复制旧 `page.tsx`。
- `d=OFF` 的实现是本阶段独立编写的新代码（复用当前代码库中已存在、已导出的 `applyPhraseAliasRules` + 一个 10 行的通用 CJK bigram 兜底），不是对旧 tokenizer 的复制——旧 `buildSearchTokensOLD`（`run_mode.cjs`）与新 `buildSearchTokensDictionaryOff`（`lib/searchTokens.ts`）在触发条件、使用的具体函数调用上有意保持了必要的相似性（both 使用 `applyPhraseAliasRules` 基础版本、both 有单 token 时的 bigram 兜底），因为这是"关闭字典增强"这一概念在两次独立实现中都会自然收敛到的形态，但代码本身是本阶段重新书写，未整段挪用。
- 未手工删除 token 模拟 d OFF——`d=OFF` 路径是通过实际不同的代码分支（不调用 `segmentCJKToken`、调用未排除的 `applyPhraseAliasRules`）产生结果，不是先跑 d=ON 再删减。
- 未在运行后过滤 alias 模拟 g OFF——`gEnabled=false` 时代码根本不进入 rewrite/guard 分支（`if (gEnabled && lowResultGatePassed)`），不是"先跑再丢弃"。
- Mode Contract Smoke Test 全程 0 次真实 LLM 调用（`rewrite_provider_called` 全部为 `false`，C/D 模式使用 `rewrite_fixtures.json` 中逐条注明来源的、复制自真实已保存 Prompt 2B/2C/2D 生产结果的固定 fixture）。
- 未修改 Ranking/Merge/relaxed 匹配阈值/Tokenizer 词典/Protected Phrase 规则内容/Alias 数据/Taxonomy/catalog 内容/Rewrite Guard 判断逻辑/Cache TTL——已用 `git diff --stat`/哈希核对确认 `lib/searchRewrite.ts`、`lib/query_phrase_aliases.ts` 等文件未被本阶段触碰。
- Blog、Taxonomy、catalog 文件哈希在执行前后逐一核对一致（见执行后安全校验）。

## 14. Readiness

**READY_FOR_MODE_CONTRACT_SMOKE** — d 合同已从历史资料与当前代码明确确认；新 runtime toggle 已实现，默认值为 `d=ON` 且逐字段验证与修改前行为完全一致；`d=OFF` 使用同一份当前代码的显式分支，产生合法非空的基础 tokenization，并在 4 个已知受影响 Query 上观察到预期差异；全量单元测试、TypeScript、Production Build 全部通过。据此进入 Mode Contract Smoke Test（已实际执行，见独立 Summary 报告，结果 32/32 通过）。
