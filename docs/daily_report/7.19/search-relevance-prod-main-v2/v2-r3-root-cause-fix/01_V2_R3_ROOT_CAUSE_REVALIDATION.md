# V2-R3 Stage: Root-Cause Revalidation of the 50 Regressed 326-Set Queries

Date: 2026-07-19. V2-R3 worktree: `/Users/baobaoli/Desktop/curify-frontend-search-v2-r3-2026-07-19`, branch `baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19`, HEAD `32f6282a240edfa87edae5a0ba5308aecf462466` (identical to V2-R1 frozen / V2-R2 initial SHA). **No code was modified to produce this document** — this is a re-verification pass over V2-R2's evidence plus direct reading of the live code, not a new evaluation run.

## 0. What changed since V2-R2, and what didn't

V2-R2 (`v2-r2-relaxed-gate/01_RELAXED_REGRESSION_ROOT_CAUSE.md`) instrumented a temporary debug trace and re-ran all 50 regressed queries live against V2-R2 (identical code to V2-R1) to get per-candidate evidence, concluding the "弱 Relaxed 稀释" hypothesis from `31_STATISTICAL_COMPARISON.md` explained only 10% of the regressions. This stage independently re-derived the same 50-row classification from the **existing** V2-R2 trace CSV (`v2-r2-relaxed-gate/02_REGRESSED_QUERY_RELAXED_TRACE.csv`) by exact tally (`grep -c` per classification, see §1) and cross-checked every classification against a **fresh, line-level reading of `lib/relevanceScorer.ts`, `lib/relevanceScorerConfig.ts`, and `app/[locale]/(public)/search/page.tsx`** in the V2-R1/V2-R3 worktree (byte-identical code, since V2-R3's HEAD equals V2-R1 frozen). No new server run, no new LLM judge call, no new debug instrumentation was performed this stage — this was explicitly out of scope ("禁止运行完整326/旧328/Hard68/12条P0") and unnecessary: V2-R2's per-candidate trace already contains real, live-collected evidence (`isOriginal`, path source, `score`, `ScoreBreakdown.reasons`) for every regressed query, sufficient to verify the classification against the code.

**Verdict: V2-R2's classification is confirmed exactly, with additional code-level mechanism detail added below that sharpens the fix design.** Tally re-verified independently:

```
ORIGINAL_TEMPLATE_OVERPROMOTION:          22  (44%)
RELAXED_SCORE_TOO_HIGH_SENSE_COLLISION:   18  (36%)
CATALOG_GAP_NEVER_ZERO_FLOOR:              5  (10%)
WEAK_RELAXED_DILUTION_PARTIAL:             5  (10%)
Total:                                    50 (100%)
```

No row was reclassified. No row is `UNKNOWN`. Full per-query detail (all columns required by the task charter — matched/missed query terms, subject/modifier coverage, score breakdown, displaced/replacement candidate, confidence, evidence, proposed mechanism) is in `02_V2_R3_REGRESSION_TRACE.csv`, mechanically derived from the real V2-R2 trace data plus the code mechanisms confirmed in §2-§5 below (methodology note in that CSV's header comment and in §6).

## 1. Method for this revalidation

1. Read `v2-r2-relaxed-gate/01_RELAXED_REGRESSION_ROOT_CAUSE.md` end to end and `v2-r2-relaxed-gate/02_REGRESSED_QUERY_RELAXED_TRACE.csv` in full (all 50 rows, every column).
2. Independently tallied the `classification` column by exact string match (`grep -c`) — confirms 22/18/5/5 = 50 with no arithmetic slip in the prose summary.
3. Read `lib/relevanceScorer.ts` in full (`scoreRecord`, `applyFamilySaturation`, `selectFinalCandidates`) and `lib/relevanceScorerConfig.ts` in full (all weight constants).
4. Read `app/[locale]/(public)/search/page.tsx` lines 570-1024 (the two-pass scorer, template-level strict promotion branch, rewrite/decomposition merge loop, and the `scoredCandidates` → `applyFamilySaturation` → `selectFinalCandidates` → `inspirations` pipeline that produces the rendered result list).
5. Cross-referenced `31_STATISTICAL_COMPARISON.md`, `33_GO_NO_GO_RECOMMENDATION_ZH.md`, `32_REGRESSION_AND_IMPROVEMENT_CASEBOOK.csv`, `v2-r1-328-completion/04_OLD328_STATISTICAL_COMPARISON.md` / `05_V2_R1_STATUS_AFTER_328_ZH.md` for consistency (the old-328 report independently reproduces the same "simple literal-noun query loses precision" pattern with concrete examples — 马克杯/mug, 咖啡/coffee, 香水/perfume, 口红/lipstick — corroborating the mechanism found here on a completely disjoint query set).
6. Verified git state of all five worktrees (V0, V2-R1, V2-R2, V2-R3, artifact backup) before starting — all clean, all at their expected SHAs (see §8 for the full audit).

## 2. Code-confirmed mechanism per root cause

### 2.1 `ORIGINAL_TEMPLATE_OVERPROMOTION` (22/50, 44%) — confirmed, mechanism sharpened

**Location**: `app/[locale]/(public)/search/page.tsx` lines 634-693, inside `scoreQueryTokens(tokens, promoteAllUnderStrictTpl=true)` — the ORIGINAL (non-rewrite) query pass.

**Mechanism**: once a template's title/category/tags/topics/description blob strict-matches the query ANYWHERE (`strictTpl.has(r.template_id)`), **every inspiration under that template** is pushed into `scored` with:
```
score: 100,                 // capped to 20 by scoreRecord's Math.min(baseRetrievalScore, 20)
fields.tagsHit: true,       // HARDCODED — "the full blob did strict-match by definition" (line 685 comment)
fields.substringOnly: false,
fields.titleHit: <computed against templateTitleCategoryBlob>,
fields.subjectPresent: <computed against templateTitleCategoryBlob>,
```
`tagsHit` is unconditionally `true` for **every sibling inspiration**, regardless of whether that specific inspiration has anything to do with the query — only the template as a whole matched. This directly feeds `relevanceScorer.ts scoreRecord()`: `base_retrieval = min(100,20)*1.0 = 20` (relevanceScorerConfig.ts `base_retrieval: 1.0`) plus `whole_token_tags = +8` (hardcoded `tagsHit`) plus, if the template's title/category blob also matches, `whole_token_title = +18`. This arithmetic exactly reproduces the observed flat scores in the trace (e.g. `figure`: all 15 top candidates score **46** = 20 + 8 + 18; `doll`: all 5 score **13** = 20 - 8 + ... — see per-row `score_breakdown` in `02_V2_R3_REGRESSION_TRACE.csv` for the exact reconciliation against each row's real `strict_scores`).

V2-R1's second commit (`fix(search): reduce broad template ranking noise via title/category field-split scoring (direction 7)`) already narrowed `titleHit`/`subjectPresent` evidence from the full free-text blob to `templateTitleCategoryBlob` (title+category only) — this measurably helped (`16_BROAD_NOISE_BEFORE_AFTER_SUMMARY.csv`: `periodic table`, `吉祥物`, `贴纸`, `横幅` all improved or held). **What Direction 7 did NOT touch: `tagsHit: true` is still hardcoded for every sibling, and the retrieval/promotion itself (which inspirations get pulled in) is untouched by design** ("retrieval/promotion itself is UNCHANGED... preserving recall / not risking a new zero-result case" — page.tsx comment, line 637-640). The residual defect is that **scoring evidence is still computed at the TEMPLATE level and copied uniformly onto every sibling inspiration**, instead of being computed per-inspiration.

**Explicit check against the 6 mandatory sub-questions (charter §5.A)**:
1. *Original results only kept in the pool, or ranked?* — **Ranked, via inflated score, not via a separate rank bonus.** No code path adds points to a candidate merely because `isOriginal===true`; `scoreRecord()` never reads `isOriginal`. The inflation happens one step earlier, in how the ORIGINAL pass computes `score`/`fields` for each candidate (see above).
2. *Direct or indirect ranking bonus?* — Indirect: `isOriginal` correlates with going through the `promoteAllUnderStrictTpl=true` branch, which is the branch that hardcodes `tagsHit`. A hypothetical non-original candidate that reached the scorer through this same branch would receive the identical inflated score — it is not an `isOriginal` check, it is a **template-promotion-branch** effect that happens to apply only to the original pass today (rewrite/decomposition passes use `promoteAllUnderStrictTpl=false`, page.tsx line 587-593, and score inspirations against their OWN blob).
3. *Does `isOriginal` affect score directly?* — **No.** Confirmed by reading `scoreRecord()`'s full parameter list (`FieldHitInfo`, `ScoreContext`, `baseRetrievalScore`) — `isOriginal` is not one of them. `ScoredCandidate.isOriginal` is computed and stored (page.tsx line 983) but used ONLY by `selectFinalCandidates()` for the existence-floor filter, never by `scoreRecord()`.
4. *Does the original floor affect Top-5 truncation?* — **No separate truncation step exists.** `finalSelected` (line 991) is the *already score-sorted* output of `applyFamilySaturation()` (line 990, which explicitly re-sorts by `final_score` descending); `selectFinalCandidates()` only **filters** that sorted array (dropping some elements), it does not re-sort or re-order. `Array.prototype.filter` preserves relative order, so the "Top-5" rendered to the user is simply the first 5 elements of this score-sorted-then-filtered list, computed via `inspirations = finalSelected.slice(0, TOTAL_CANDIDATE_POOL_CAP)` (line 993-994) and consumed downstream. There is no dedicated "keep originals in the first N slots" step anywhere in the file.
5. *Is "must be kept" implemented as "must be ranked high"?* — **No, not as a rule.** But in *practice*, because the SCORE itself is inflated for template-promoted originals (see mechanism above), they frequently do end up ranking high — this is a scoring-evidence defect producing the same symptom, not a code path that conflates the two concepts by name.
6. *Can a low-relevance original be kept but ranked outside Top-5?* — **Yes, structurally possible today** — nothing prevents a low-scoring `isOriginal` record from sorting below rank 5 (the invariant is existence-in-pool, not existence-in-top-5). The 22 offending queries end up in Top-5 anyway only because their *score* (not their `isOriginal` flag) is inflated to 46/13/etc. by the mechanism above. **This is the key, actionable finding for Section A of the fix design**: the code does NOT need a new "decouple existence from rank" mechanism (that decoupling already exists structurally) — it needs the SCORE that determines rank to stop being a template-level constant copied onto every sibling.

One secondary, minor effect also confirmed by reading the code: `inspirationById` (page.tsx line 803-804) is populated from `baseResult.scored` (the ORIGINAL pass) **before** the rewrite/decomposition merge loop runs (line 891-901 inserts new keys but does not reorder existing ones). Because `Array.prototype.sort` in V8/Node is a stable sort, **exact score ties are broken in favor of whichever candidate's Map entry was inserted first — i.e., originals win ties over rewrite/decomposition-only candidates with an identical `final_score`.** This is real but minor (it only matters for exact-score ties, and none of the 22 `ORIGINAL_TEMPLATE_OVERPROMOTION` rows depend on it — their originals dominate on score alone, not on tie-break order). Flagged in the fix design (§7A) as a secondary cleanup, not a primary mechanism.

### 2.2 `RELAXED_SCORE_TOO_HIGH_SENSE_COLLISION` (18/50, 36%) — confirmed, mechanism sharpened

**Location**: `app/[locale]/(public)/search/page.tsx` `subjectPresent` derivation, two call sites:
- Non-template-promoted candidates (relaxed/rewrite path): lines 548-573 (`deriveFieldHits`).
- Template-promoted candidates (original path): lines 665-678.

**Mechanism**: `subjectPresent` — the ONE signal that gates `missing_subject_penalty` (`-15`) and gates whether `path_agreement` (`+3` per extra path, capped `+12`) is credited — collapses to a single-token check in two distinct ways:
- **Single-token query** (`originalPrimaryTokensForSubject.length <= 1`): `subjectPresent = titleHit` (line 561 / line 672 for the two call sites). There is **no sense-disambiguation** — any whole-token hit on the query's one token, in ANY sense, satisfies "subject present."
- **Multi-token query, no protected phrase**: `subjectPresent` checks **only the single longest primary token** (`[...originalPrimaryTokensForSubject].sort((a,b)=>b.length-a.length)[0]`, lines 564 / 674-677) — the REST of the query's tokens (the modifiers) are never required to be present anywhere for `subjectPresent` to be true.

Once `subjectPresent` is satisfied this cheaply, a candidate that matched only ONE ambiguous token in the wrong sense gets: full `whole_token_title` (`+18`) and/or `whole_token_tags` (`+8`) if that token literally appears in title/tags (which it does — that's the collision), **no** `missing_subject_penalty` (`-15` avoided), and is eligible for `path_agreement` credit if multiple rewrite paths converge on it. This is exactly enough to clear `MIN_SCORE_WHEN_ORIGINAL_NONEMPTY = -5` comfortably — the trace shows these candidates scoring `+12` to `+50`, far above the floor (`02_V2_R3_REGRESSION_TRACE.csv`, `relaxed_scores` column). Concrete recurring pattern across the 18 rows: `banner` → Marvel `Bruce Banner` MBTI cards (`sale banner`, `black friday banner`, `新品横幅`, `清仓促销横幅`, `黑五促销横幅`); `tag` → generic metadata tag, not clothing tag (`clothing tag`, `产品标签`); `figure`/`teddy` → wrong-sense whole-token hits inside otherwise-legitimate templates.

**Explicit check against the 8 mandatory sub-questions (charter §5.B)**:
1. *Does one-word match on a multi-word query get a high score?* — **Yes, confirmed** — see mechanism above; the multi-token subject check degenerates to a single (longest) token check.
2. *Does full word hit outscore full-subject match?* — Not quite the right framing given the code: there is no separate "full-subject match" tier to compare against — the code's ONLY subject-coverage signal already IS a single-token check, so a full word hit on that one token *is* currently treated as equivalent to full subject coverage.
3. *Are both subject and modifier covered?* — **No** — modifiers are never checked for presence at all; `relevanceScorer.ts`'s own header comment confirms this was a deliberate scope decision ("a standalone 'Modifier Coverage' term... deliberately NOT implemented").
4. *Is category/topic mismatch unpenalized?* — **Yes, confirmed** — same header comment: "a separate Category/Topic Consistency term... deliberately NOT implemented."
5. *Is title single-word-hit weight too high relative to what it should be for ambiguous words?* — The weight itself (`whole_token_title: 18`) is not inherently wrong for genuine matches; the defect is that it fires identically for both a genuine subject match and a wrong-sense collision, because nothing downstream distinguishes them.
6. *Are there banner→Bruce-Banner-style wrong-sense hits?* — **Yes, directly observed** in 5+ of the 18 rows (see above), matching the `lib/searchPhraseProtection.ts` header's own prior documented case of the same class of bug for `coffee cup`/`black friday`.
7. *Do single-word and multi-word queries need different strategies?* — Partially — single-token queries have literally nothing else to check (there is no modifier to require), so the achievable fix there is bounded to "penalize weak single-signal matches more, or require a stronger signal tier (phrase/category) before granting a high score", not "require coverage" (there's only one token). Multi-token queries have a real, currently-unused opportunity: require some minimum fraction of the query's OTHER tokens to also appear.
8. *Can this be solved with a general rule instead of a manual blacklist?* — **Yes** — the existing `subjectTokens`/`anchorToken` infrastructure (`lib/searchPhraseProtection.ts`) already generalizes this exact idea for 2 evidenced phrases; the fix design in §7B extends the SAME mechanism (required-coverage-of-non-subject-tokens, downweighting isolated single-token-only matches) generically, not via a growing hand-built list of wrong senses.

### 2.3 `CATALOG_GAP_NEVER_ZERO_FLOOR` (5/50, 10%) — confirmed, no code defect

**Location**: `lib/relevanceScorer.ts` `selectFinalCandidates()`, lines 235-247, the `originalIds.size === 0` branch.

**Mechanism**: when fewer than `MIN_KEPT_WHEN_ORIGINAL_EMPTY = 5` candidates clear `MIN_SCORE_WHEN_ORIGINAL_EMPTY = -5`, the function does not return an empty or near-empty list — it takes the top-N by score **regardless of the floor**. For these 5 queries, **100% of the entire available candidate pool** scores below the floor (verified directly in the trace: `relaxed_above_floor=0` for all 5 rows — `盲盒`, `泰迪熊`, `练习册`, `笔袋`, `算盘`). `泰迪熊` is the clearest case: V0's top-5 and V2's top-5 are **the literal same 4 records**, merely reordered — there is no candidate anywhere in the catalog to prefer instead. This is a content/catalog supply gap, not a ranking or admission-threshold defect; no threshold change can manufacture a better candidate that does not exist. See `04_CATALOG_GAP_POLICY_PROPOSAL.md` for the (non-code, non-ranking) options considered for this bucket.

### 2.4 `WEAK_RELAXED_DILUTION_PARTIAL` (5/50, 10%) — confirmed as genuinely partial, not reclassified

Mechanically, all 5 rows (`手办`, `娃娃`, `挂件`, `酒标`, `online store banner`) show a **mixed** floor state: some relaxed candidates score above `-5` (real signal), others score at the catalog-gap-like `-13`/`-14` floor and are present purely via the `MIN_KEPT_WHEN_ORIGINAL_EMPTY` never-zero override. This is a genuinely distinct pattern from both 2.1 (no template-promotion involved — `originalIds` is empty for all 5) and 2.3 (not 100% below floor). It is correctly NOT reclassified as the primary root cause (charter §5.D explicitly forbids re-promoting Weak Relaxed to primary status) — it remains a **minority, partially-addressable** bucket, and per V2-R2's finding (independently re-confirmed here), **even a full fix to this bucket cannot flip the 326-set's net-negative outcome**, because it is only 10% of the regressions and the other 90% (2.1 + 2.2 + 2.3) are untouched by any Relaxed-specific gate. §7D of the design explains why this stage still does not build a dedicated Relaxed gate, in favor of letting the coverage/scoring fix (§7B) incidentally clean up the above-floor subset of this bucket.

## 3. Cross-validation against the old-328 seed library (independent dataset)

`v2-r1-328-completion/04_OLD328_STATISTICAL_COMPARISON.md` (a completely separate 328-query set, run after the 326-set) independently reproduces the same qualitative failure signature: `zero-result rate +0.61pp` and `low-result rate +1.52pp` (both worse), driven by exactly the same query shape — "simple literal-noun/demographic queries losing their previously-clean strict-only result set to weaker relaxed candidates" (报告原文), with concrete named regressions (马克杯/mug, 咖啡/coffee, 香水/perfume, 口红/lipstick, 家纺/home textiles, 保健品/health supplements) that are structurally identical in shape to the 326-set's `ORIGINAL_TEMPLATE_OVERPROMOTION`/`RELAXED_SCORE_TOO_HIGH_SENSE_COLLISION` patterns (single/double literal-noun queries hitting an unrelated template or wrong word sense). This is independent corroboration from a disjoint query set that the two dominant mechanisms identified above are systemic, not an artifact of the specific 326-query sample.

## 4. What this confirms for the fix design

- **90% of the regressions (45/50) are NOT a Relaxed-admission problem** — a Strict/Relaxed gate (of any threshold) structurally cannot reach `ORIGINAL_TEMPLATE_OVERPROMOTION` (protected by the Direction-1 existence floor and, more precisely, driven by score inflation on the ORIGINAL pass, which a Relaxed gate never touches) or `RELAXED_SCORE_TOO_HIGH_SENSE_COLLISION` (candidates already score comfortably above any floor a Relaxed gate could reasonably set) or `CATALOG_GAP_NEVER_ZERO_FLOOR` (100% below floor already, nothing to admit/exclude between).
- **Both dominant mechanisms are fixable by the SAME general technique**: making the scorer's evidence more precise about WHERE and HOW WELL a query's terms are actually covered by a SPECIFIC candidate, instead of (a) copying template-level evidence onto every sibling inspiration, or (b) treating a single-token hit as sufficient subject coverage regardless of the rest of the query. This is why §7 proposes two mechanisms (A: per-inspiration re-scoring for template-promoted originals; B: multi-term coverage for the sense-collision bucket) rather than a Relaxed-admission gate.
- **No mechanism proposed below requires touching `selectFinalCandidates`'s existence-floor logic, the never-zero override, or the phrase-protection dictionary's existing 2 entries** — all three are confirmed correct and load-bearing for other cases (protection set, §6 of `03_V2_R3_CASE_SPLIT.csv`).

## 5. Confidence and evidence summary

| Root cause | Count | Confidence | Primary evidence |
|---|---:|---|---|
| `ORIGINAL_TEMPLATE_OVERPROMOTION` | 22 | HIGH | Live V2-R2 trace (`isOriginal` array all-true, flat scores) + direct code read of page.tsx L634-693 reproduces the exact observed scores arithmetically |
| `RELAXED_SCORE_TOO_HIGH_SENSE_COLLISION` | 18 | HIGH | Live V2-R2 trace (above-floor relaxed scores, wrong-sense titles visible in top5) + direct code read of `subjectPresent` derivation (single-token-only check) |
| `CATALOG_GAP_NEVER_ZERO_FLOOR` | 5 | HIGH | Live V2-R2 trace (`relaxed_above_floor=0` for all 5) + `selectFinalCandidates` never-zero branch read; `泰迪熊` V0/V2 identical-candidate-set direct comparison |
| `WEAK_RELAXED_DILUTION_PARTIAL` | 5 | MEDIUM (by the source report's own qualification — "partially") | Live V2-R2 trace mixed floor states; V2-R2 report's own explicit "partially fixable" framing preserved, not overstated |

## 6. Worktree/branch safety audit performed before this document was written

| Worktree | Expected branch | Expected SHA | Actual branch | Actual SHA | Clean? |
|---|---|---|---|---|---|
| V2-R3 | `baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19` | `32f6282a...462466` | matches | matches | yes |
| V2-R1 | `baobao/search-relevance-prod-main-v2-2026-07-19` (frozen branch `...v2-r1-frozen-2026-07-19` co-points to same SHA) | `32f6282a...462466` | matches | matches | yes |
| V2-R2 | `baobao/search-relevance-prod-main-v2-r2-2026-07-19` | `32f6282a...462466` | matches | matches | yes |
| V0 | detached HEAD | `05e5f2d3...c3673` | matches | matches | yes |
| Artifact backup | `baobao/search-relevance-v2-r1-r2-artifacts-2026-07-19` | `e42b8024...befa51` | matches | matches | not touched |

**FINAL_STATUS (this document): V2_R3_ROOT_CAUSE_REVALIDATION_CONFIRMED** — V2-R2's classification stands unchanged (22/18/5/5, no reclassification, no unknowns); code-level mechanism detail added sharpens the fix design in `05_V2_R3_MINIMAL_FIX_DESIGN.md`. No code was modified to produce this document.
