# Stage 7: How Directions 3, 4, 5 Are Unified by the Scorer

Date: 2026-07-19. Maps each of the three directions to its concrete implementation in `lib/relevanceScorer.ts` / `app/[locale]/(public)/search/page.tsx`.

## Direction 3: Strict/Relaxed binary gate → quality/quantity gate

**V0 behavior** (confirmed via code audit, `02_PRODUCTION_SEARCH_CODE_AUDIT.md`): `hasStrict = allScored.some(x => x.strict)`, then `filter(x => hasStrict ? x.strict : true)`. If any candidate anywhere (any path) is strict, every relaxed candidate — including the original query's own relaxed matches — is dropped.

**V2 behavior**: removed entirely. Every candidate (strict or relaxed, from any path) is scored via `scoreRecord()` on the same scale and ranked by `final_score`. Strict-ness is no longer a gate; it still influences the score indirectly through `base_retrieval` (strict matches generally carry higher `primaryHits+bigramHits`) and through the `titleHit`/`tagsHit`/`exactPhraseHit` signals that a strict match is more likely to satisfy. `selectFinalCandidates` provides the safety floor: original-pass records are never excluded (existence floor); non-original records need to clear a small quality floor once original results exist. This directly implements "Strict可获得合理正向信号但不自动最终胜出" and "Strict少或质量低时从Relaxed补充高分结果" — there is no longer a hard-coded "strict wins, relaxed loses" branch; ranking does the work.

**Verified live**: `black friday banner` — before, template rail flooded to 113 total; after, inspirations dropped from a noise-dominated 49 to 2 floor-protected weak matches (the true CATALOG_GAP made visible instead of masked by Marvel-card noise). `coffee cup` — before, World Cup content ranked in the top few; after, ranks 8+, replaced by genuinely coffee-related content in positions 1-5.

## Direction 4: Phrase / whole-token / substring priority

**V0 behavior**: `tokenInBlob` already does whole-word-boundary matching for ASCII and raw substring matching for CJK (no priority tiers — a match is a match, `score = primaryHits + bigramHits` treats every hit identically regardless of whether it came from a phrase, a whole token, or a CJK substring).

**V2 behavior**: `exact_phrase` (+40) > `whole_token_title` (+18) > `whole_token_tags` (+8) > (implicit, unscored) bare AND-match > `substring_penalty` (-22, actively penalized when the ONLY evidence is a CJK bigram/substring fallback with zero real primary-token hits). This produces exactly the priority ordering the design doc specifies (`完整短语 > 多个核心整词 > 单个核心整词 > 合理Alias/词形 > 子串`) as a score gradient rather than a hard rule.

**Verified live**: `coffee cup` top-5 changed from World-Cup-poster-containing to 100% genuinely-coffee-related; `black friday banner`'s Marvel Black Widow card moved from final_score +6 to -6 (from rank #1 to correctly excluded from the tiny surviving set once the path-agreement/subject-coverage interaction was fixed).

## Direction 5: Rewrite path quality/quantity control

**V0 behavior**: no per-path cap, no total-pool cap beyond the pre-existing `.slice(0, 80)` on inspirations (and NO cap at all on the `matchedTemplates` rail — confirmed live: `coffee cup` matched 284/335 templates, ~85% of the entire catalog).

**V2 behavior, multiple layers** (per design doc 10.3's "not a single fixed cap, but a combination"):
- `PATH_CANDIDATE_CAP` (40): a single non-original path may contribute at most 40 *new* (not-already-in-pool) candidates. Existing-candidate score/field updates from that path are never capped (agreement is always allowed to strengthen an existing candidate).
- Template rail cap: templates matched ONLY by rewrite/decomposition paths (not the original query, not backing a surviving scored inspiration) are capped at `TOTAL_CANDIDATE_POOL_CAP` (80) total, prioritized by how many distinct paths independently matched them. Confirmed live: `coffee cup` template count dropped from 284 to 100-106 (roughly a 63% reduction) after this cap plus the scorer's reordering of which inspirations survive (each surviving inspiration's own template is added to the rail independently of the cap, which is correct behavior — the rail should reflect what's actually shown, not be capped below what backs real, kept results).
- `path_agreement` scorer signal (+3/hit, capped +12), gated on `subjectPresent` — replaces the old flat multiplicative `+8%/hit, capped +40%` boost that applied regardless of relevance. This is the fix for the specific bug found during implementation testing (5-path agreement inflating an off-subject Marvel card past a correctly-applied `missing_subject_penalty`).
- `family_saturation_penalty` — discourages one template family (which a single broad path can flood) from dominating the ranked pool, without ever hard-excluding it (soft penalty per design doc 11.3's "不通过hard filter制造新的零结果").
- **Original candidate pool never affected by any of the above**: `selectFinalCandidates`'s floor guarantees a failing/over-broad path can only affect non-original candidates, never remove or suppress an original-pass result (design doc 10.3's "某条路径失败不得影响原始候选结果").

## What was deliberately NOT implemented for Direction 5

A hard per-path result-count cutoff that REJECTS an entire path (vs. capping/scoring it) was not implemented — no V0 case in Stage 4 showed a path so catastrophically broad that scoring/capping alone was insufficient; per the design doc's "必要时拒绝严重漂移的具体路径" (only when necessary), rejecting whole paths was judged not currently necessary given the capping + scoring combination already produces large, evidenced improvements (see above). This can be revisited if Stage 12's full evaluation surfaces a case the current mechanism doesn't adequately handle.
