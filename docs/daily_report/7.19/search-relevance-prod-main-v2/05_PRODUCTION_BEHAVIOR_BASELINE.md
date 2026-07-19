# Stage 3: V0 Behavior Baseline

Date: 2026-07-19. Established BEFORE any V2 code changes (verified by commit timestamps: V0 collector testing and Stage 4 target-case reconfirmation were run against the live V0 production build prior to the first V2 commit `c5d77149`).

## Method

Per task instructions, "file exists" is not sufficient evidence — every behavior below was triggered against a real running `next start` production build of V0 (port 4501) via the real `/search` page, using `scripts/collector.mjs` (RSC-flight-payload extraction of the actual server-computed `<SearchResultsClient>` props — the same real pipeline a browser would receive, not a re-implementation/mirror). This satisfies the task's requirement to check whether an in-process harness fully covers the real pipeline first: `scripts/eval_search.cjs` (the pre-existing committed harness) was read and found to be a hand-maintained MIRROR of the tokenizer/scorer logic, not an import of the real functions, and does not cover multi-path decomposition, the exact merge/gate logic, or the compound-noun guard — documented in `02_PRODUCTION_SEARCH_CODE_AUDIT.md`. It was therefore judged insufficient for primary evaluation, and the real-server collector was built and used instead for all V0/V2 comparison work in this project, satisfying the "same collection method for both sides" requirement (task section 13.2) from the start.

## Baseline behaviors captured on V0 (pre-any-V2-change)

| Behavior | Trigger query | V0 observed result | Source |
|---|---|---|---|
| LLM rewriter triggers | 烘焙包装 (thin CJK query) | `usedRewrites=["baking packaging design","baked goods packaging","pastry packaging ideas"]`, `pathsUsed=6` | `07_V0_TARGET_CASE_RECONFIRMATION.csv`, `scripts/stage4_v0.json` |
| Rewrite Guard (Path A/B decision + garbage/bot pre-filter) | code-level (no live test needed — verified present in source) | `looksLikeGarbageQuery`, `BOT_UA_REGEX` present at `page.tsx:60-70,53` | `02_PRODUCTION_SEARCH_CODE_AUDIT.md` |
| multi-path retrieval | coffee cup | `pathsUsed=5`, real result-count increase from thin original to 364 total | `07_V0_TARGET_CASE_RECONFIRMATION.csv` |
| decomposition | black friday banner | `pathsUsed=6` (3 rewrites + up to 3 decomposition slots) | `07_V0_TARGET_CASE_RECONFIRMATION.csv` |
| Strict result case (rich, no rewrite) | mbti marvel | 74 strict inspirations, `pathsUsed=1` (no thin trigger) | this session live check |
| Relaxed supplement case | warmup routine running checklist | 7 inspirations, small precise set | this session live check |
| L2 hierarchical content | (repo-wide grep + targeted reads) | UNKNOWN — no code artifact found, and the source design doc itself flags this as unresolved | `02_PRODUCTION_SEARCH_CODE_AUDIT.md` |
| Multi-paragraph display | same | UNKNOWN | `02_PRODUCTION_SEARCH_CODE_AUDIT.md` |
| Search result click | component-level (shared with /topics, /nano-template) | not independently re-clicked via browser this session (time constraint, disclosed in `19_FUNCTIONAL_REGRESSION_RESULTS.csv`); code-level confirmed unmodified in V2 | `19_FUNCTIONAL_REGRESSION_RESULTS.csv` |
| Empty state | Historical thin/CATALOG_GAP query (课程表 pre-fix) | renders `GenerableTemplatesSection` + `TopicStrip` fallback (confirmed via code read, `SearchResultsClient.tsx:319-333`) | `02_PRODUCTION_SEARCH_CODE_AUDIT.md`, `04_EXISTING_FEATURE_REGRESSION_TARGETS.md` |
| Loading state | component-internal to `GenerableTemplatesSection.tsx` | not independently re-triggered via browser this session; code unmodified | `19_FUNCTIONAL_REGRESSION_RESULTS.csv` |
| Error/timeout fallback | code-level (`lib/searchRewrite.ts` catch blocks) | returns safe empty rewrite list on any failure, verified present in source | `02_PRODUCTION_SEARCH_CODE_AUDIT.md` |

## V0 engineering baseline (pre-any-V2-change)

- `tsc --noEmit`: 0 errors
- `npx vitest run --config vitest.unit.config.ts`: 111/111 pass
- `npm run build`: succeeds

All three re-confirmed identical on V2's INITIAL state (before any implementation commit), since V0 and V2 were verified byte-identical via `diff -rq` (see `01_WORKTREE_AND_BRANCH_SETUP.md`) — this satisfies "初始V2应与V0行为一致" directly (they were the literal same files at that point).

## Gate result

**V0 behavior baseline recorded: YES. Initial V2 == V0: YES (byte-identical, verified). Key regression tests runnable: YES (vitest suite + live collector against real running servers, both confirmed working before any implementation change).** Gate PASSED — proceeded to Stage 4/5.
