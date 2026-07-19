# V2-R3 Stage: Implementation Summary

Date: 2026-07-19. Branch `baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19`, initial SHA `32f6282a240edfa87edae5a0ba5308aecf462466`.

## 1. Files actually modified

| File | Change |
|---|---|
| `app/[locale]/(public)/search/page.tsx` | Mechanism A (per-inspiration re-scoring for template-promoted siblings) + mechanism B wiring (query-level `isMultiTermQuery`/`hasProtectedPhraseQuery` flags, `coverageRatio` computation, `computeCoverageRatio` helper) |
| `lib/relevanceScorer.ts` | Mechanism B core logic in `scoreRecord` (coverage-gated `subjectPresent`, isolated-hit score cap); `FieldHitInfo`/`ScoreContext` type extensions |
| `lib/relevanceScorerConfig.ts` | 3 new named constants: `REQUIRED_TERM_COVERAGE_MIN_RATIO`, `ISOLATED_HIT_MAX_COVERAGE_RATIO`, `ISOLATED_HIT_SCORE_CAP` |
| `lib/__tests__/relevanceScorer.test.ts` | Updated existing fixtures for the new type fields (`ctx()`/`fields()` helpers); +18 new tests (4 mechanism A, 14 mechanism B) |

No other production or fixture file was modified. All 4 files were anticipated by the design doc (`05_V2_R3_MINIMAL_FIX_DESIGN.md` §13) — **no out-of-scope files were touched.**

## 2. Mechanism A implementation

**Location**: `page.tsx`'s `scoreQueryTokens`, the `promoteAllUnderStrictTpl === true` branch (per-inspiration loop over `nanoInspiration`).

**What changed**: the per-inspiration own-content blobs (`titleBlob`, `topicalBlob`, full `blob`) — previously computed only inside the non-template-promoted branch — are now hoisted to run unconditionally for every inspiration, before the branch check. Inside the template-promoted branch:

1. The **template-level** evidence (today's pre-existing behavior: `titleHit`/`exactPhraseHit`/`subjectPresent` computed against `templateTitleCategoryBlob`, `tagsHit` hardcoded `true`) is still computed first, as `templateFallbackFields` — this is tier 2.
2. `hasOwnContent` is computed: does this specific inspiration have ANY own descriptive content (own locale title/category text, own tags, own topics, or own `search_aliases`)?
3. If `hasOwnContent` is true, the **same `deriveFieldHits` helper the non-template branch already uses** is called against this inspiration's own `titleBlob`/`topicalBlob` — tier 1, genuinely per-sibling evidence.
4. If `hasOwnContent` is false (the sibling has zero own descriptive content at all), `templateFallbackFields` (tier 2) is used instead — the safe fallback, only triggered when there is truly nothing else to score against.
5. Retrieval/inclusion is untouched: every sibling under a strict-matched template is still pushed to `scored` with `score: 100` (which `scoreRecord` still caps to `base_retrieval = 20` either way) — recall and the Direction-1 existence floor are unaffected, only the FIELD evidence that determines rank changes.

`mergeFields` (used when a record is hit by multiple rewrite/decomposition paths) was extended to propagate `coverageRatio` via `Math.max` (a record hit by an independently-corroborating path is at least as well-covered as either path alone found it).

**Consistency with design**: matches `05_V2_R3_MINIMAL_FIX_DESIGN.md` §4.2 exactly — two-tier evidence, own-blob-when-present / template-fallback-only-when-genuinely-absent, no change to retrieval/inclusion, no change to `selectFinalCandidates`/`applyFamilySaturation`.

## 3. Mechanism B implementation

**Location**: `lib/relevanceScorerConfig.ts` (3 new constants) + `lib/relevanceScorer.ts` (`scoreRecord` logic) + `page.tsx` (raw measurement: `computeCoverageRatio`, `isMultiTermQuery`, `hasProtectedPhraseQuery`).

**Design decision beyond the doc's prose**: the design doc left the EN/CJK consistency question open (charter requirement: "中文和英文必须有一致的覆盖原则"). Investigation of `buildSearchTokens` showed that CJK queries **without whitespace** (the normal case — Chinese does not use spaces between words) always tokenize to a SINGLE primary token regardless of how many real words they contain, so the "2+ primary tokens" definition of multi-term is EN/space-separated-only. The fix generalizes "required term" to mean: **primary tokens for space-separated queries, or bigrams (the tokenizer's own existing CJK fallback unit) for an unsegmented CJK compound** — i.e. `isMultiTermQuery = primary.length > 1 || bigrams.length > 1`, and `coverageRatio` is computed against whichever unit applies. This reuses data the tokenizer already produces (no new tokenizer, no new dictionary) and gives EN and CJK the same qualitative principle (a majority of the query's decomposed units must be found) via the same code path in `scoreRecord`.

**scoreRecord changes**:
- A `coverageGateApplies = ctx.isMultiTermQuery && !ctx.hasProtectedPhraseQuery` gate. Protected-phrase queries are fully exempted (compose with, don't replace, `lib/searchPhraseProtection.ts`'s existing anchor-token semantics).
- Effective `subjectPresent = fields.subjectPresent && fields.coverageRatio >= REQUIRED_TERM_COVERAGE_MIN_RATIO` when the gate applies (else unchanged) — feeds `missing_subject_penalty` and `path_agreement` exactly as before, just with a corrected input.
- An isolated-hit cap: when the gate applies, `!exactPhraseHit`, `coverageRatio <= ISOLATED_HIT_MAX_COVERAGE_RATIO`, and the combined `whole_token` contribution exceeds `ISOLATED_HIT_SCORE_CAP`, `whole_token` is capped and a `reasons` entry (`isolated_single_term_hit_capped`) records why.
- Single-term queries (`isMultiTermQuery: false`) are byte-for-byte unaffected — confirmed by a dedicated unit test.

**Consistency with design**: matches `05_V2_R3_MINIMAL_FIX_DESIGN.md` §5.2 exactly (both changes: required coverage gating subject presence, isolated-hit score cap), using the qualitative "majority, not 100%" / "cap, not subtract" principles from §5.3, generalized to CJK via the bigram-coverage equivalence documented above (an extension NOT explicit in the design doc's prose, but consistent with its stated goal and its own stated boundary — "no new tokenizer/data source").

## 4. What was NOT implemented (and why)

- **A standalone Category/Topic Consistency term** — design doc explicitly excludes this; no case in the 50 regressions required it beyond what coverage/isolation already explain.
- **A dedicated Strict/Relaxed admission gate** — explicitly prohibited by the charter and the design's own §7 reasoning (would only reach 10% of regressions).
- **Per-candidate debug instrumentation** (a live trace of `coverageRatio`/`isolated_hit_cap_triggered`/template-sibling-count per rendered result) — not added this stage. `07_V0_R1_R3_TARGETED_COMPARISON.csv`'s `template_sibling_count` / `isolated_hit_cap_triggered` columns are marked `NOT_INSTRUMENTED` rather than fabricated; the targeted evaluation instead confirms the mechanisms' effect by directly comparing rendered top-5 content and rubric scores, which is sufficient to demonstrate the intended behavior (see `08_V2_R3_TARGETED_GATE_RESULT.md` §2-3 for concrete before/after examples) without adding new production code paths purely for observability.
- Any change to `selectFinalCandidates`, `applyFamilySaturation`, `searchPhraseProtection.ts`, or the never-zero/floor constants — none needed, none made.

## 5. Parameters (see `09_V2_R3_CONFIG_LOCK.json` for the full frozen snapshot)

| Constant | Value | File |
|---|---:|---|
| `REQUIRED_TERM_COVERAGE_MIN_RATIO` | 0.5 | `lib/relevanceScorerConfig.ts` |
| `ISOLATED_HIT_MAX_COVERAGE_RATIO` | 0.5 | `lib/relevanceScorerConfig.ts` |
| `ISOLATED_HIT_SCORE_CAP` | 8 | `lib/relevanceScorerConfig.ts` |

Zero adjustment rounds beyond the initial design-derived defaults — calibration showed a clear net improvement (4 label upgrades, 0 downgrades) on the first attempt, so no iteration was performed (satisfying the charter's "no per-query hand-tuning" and "calibration-only" constraints trivially, by not needing to tune at all).

## 6. Tests

18 new tests added to `lib/__tests__/relevanceScorer.test.ts` (4 mechanism A, 14 mechanism B — see `11_V2_R3_ENGINEERING_CHECKS.md` §2 for the full breakdown); all pre-existing tests (28, now updated only for the additive type-fixture fields, no assertion weakened) still pass. 143/143 total across the repo's full `lib/__tests__` suite.

## 7. Risks

See `08_V2_R3_TARGETED_GATE_RESULT.md` §6 for the full, evaluated risk list (贴纸/coffee cup score softening, 5 holdout label downgrades in a packaging/label query cluster, several pre-existing unresolved FAIL cases). None of these constitute a gate failure; all are flagged for the next stage's attention.

## 8. Rollback

Both mechanisms are additive and local, exactly as the design doc anticipated (§9): mechanism A modifies field-derivation inside one branch of one function; mechanism B adds one derived field, two context flags, and one score-cap rule. Rollback is `git revert` of the implementing commit — no data migration, no schema change, no external service touched, no config file outside `relevanceScorerConfig.ts` involved.

## 9. Commit

Created only after the engineering checks and targeted gate both passed. SHA `a811f06f8838e330e08caa4d3c4952d6ab10554d` on branch `baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19` (parent `32f6282a240edfa87edae5a0ba5308aecf462466`), containing exactly the 4 files listed in §1 (533 insertions, 72 deletions). Not pushed. Working tree clean after commit.

## 10. Next-stage gate conclusion

**FINAL_STATUS: V2_R3_TARGETED_FIX_COMPLETE.** Full-326 is authorized as the next stage's task.
