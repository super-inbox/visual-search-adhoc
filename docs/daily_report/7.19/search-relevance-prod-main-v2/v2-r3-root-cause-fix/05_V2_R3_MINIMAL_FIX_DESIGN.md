# V2-R3 Stage: Minimal Fix Design

Date: 2026-07-19. **Design only — no code has been written or modified for this document.** Per charter §10/§11, this stage stops after producing the design; implementation is a future stage's task.

## 1. Confirmed root causes (recap, full detail in `01_V2_R3_ROOT_CAUSE_REVALIDATION.md` / `02_V2_R3_REGRESSION_TRACE.csv`)

| # | Root cause | Count | % of 50 | Mechanism (one line) |
|---|---|---:|---:|---|
| 1 | `ORIGINAL_TEMPLATE_OVERPROMOTION` | 22 | 44% | Template-level strict promotion (page.tsx L634-693) copies uniform, template-wide score evidence (`score:100`→capped 20, hardcoded `tagsHit:true`) onto every sibling inspiration, regardless of that inspiration's own relevance |
| 2 | `RELAXED_SCORE_TOO_HIGH_SENSE_COLLISION` | 18 | 36% | `subjectPresent` collapses to a single-token check (the query's one token, or its longest token for multi-token queries) — a wrong-sense whole-token hit satisfies it, avoiding `missing_subject_penalty` and collecting full `whole_token_title`/`whole_token_tags` |
| 3 | `CATALOG_GAP_NEVER_ZERO_FLOOR` | 5 | 10% | 100% of the available candidate pool scores below floor; kept only by the never-zero guarantee. Not a ranking defect — no candidate exists to prefer instead |
| 4 | `WEAK_RELAXED_DILUTION_PARTIAL` | 5 | 10% | Mixed floor state (some relaxed candidates genuinely above floor, others never-zero padding) — genuinely a minority, partial contributor, not reclassified as primary |

**Total explainable by a ranking/scoring fix this round: 45/50 (90%)** via mechanisms A+B below (40/50 directly = causes 1+2; the remaining 5/50 = cause 4 improves incidentally as a side effect of B, not via a dedicated gate). **Not fixable by ranking this round: 5/50 (10%)** = cause 3, a genuine catalog/content gap (see `04_CATALOG_GAP_POLICY_PROPOSAL.md`).

## 2. Root causes planned for a fix this round

- **Mechanism A — per-inspiration re-scoring for template-promoted originals** (addresses cause 1, 22 cases).
- **Mechanism B — required multi-term coverage for subject/modifier presence** (addresses cause 2 directly, 18 cases; incidentally improves the above-floor subset of cause 4, 5 cases).

## 3. Root causes NOT planned for a fix this round

- **Cause 3 (`CATALOG_GAP_NEVER_ZERO_FLOOR`, 5 cases)** — no code change; see `04_CATALOG_GAP_POLICY_PROPOSAL.md` for the full reasoning. Ranking cannot manufacture a candidate that does not exist.
- **A dedicated Strict/Relaxed admission gate** — considered and explicitly rejected, both by V2-R2's analysis (independently re-confirmed in `01_V2_R3_ROOT_CAUSE_REVALIDATION.md` §4) and by this design: it can structurally only ever touch cause 4 (10% of regressions, and only partially even there), while leaving causes 1 and 2 (80% of regressions) completely untouched. Building one would not be a "minimal, evidenced fix" — it would be a mechanism sized to a hypothesis the data does not support. See §7 for the full non-negotiable reasoning ("why not a Relaxed Gate").

## 4. Mechanism A — Original candidate preservation ↔ ranking decoupling

### 4.1 What the code audit found (see `01_V2_R3_ROOT_CAUSE_REVALIDATION.md` §2.1 for full detail)

Explicitly checked, with code citations, against charter §7.A's 6 sub-questions:

| Does this exist in the current code? | Finding |
|---|---|
| Original-source score bonus (a term in `scoreRecord` that reads `isOriginal`) | **NO** — `scoreRecord()`'s parameters (`FieldHitInfo`, `ScoreContext`, `baseRetrievalScore`) do not include `isOriginal`. Confirmed by reading the full function signature and body. |
| Original rank floor (a rule that reorders `isOriginal` records to the front) | **NO** — `selectFinalCandidates()` only filters (keeps/drops), never reorders; the array is already sorted by `applyFamilySaturation()` before it's called, and filtering preserves order. |
| Original forced insertion into Top-N | **NO** — no code path inserts a record into a fixed early slot. "Top-5" is just `array.slice(0, N)` of the score-sorted, filtered list. |
| Top-N-before forced retention | **NO** — same as above; retention (existence) is a pool-level guarantee (`selectFinalCandidates`), unconnected to any Top-N slot logic. |
| Merge-order bias | **YES, minor** — `inspirationById` (page.tsx L803-804) is populated from the ORIGINAL pass first, before rewrite/decomposition results are merged in (L891-901). JS's stable sort means **exact score ties** are broken in favor of whichever entry was inserted first, i.e. originals win ties. Confirmed by reading the Map population order. Real, but does not explain any of the 22 `ORIGINAL_TEMPLATE_OVERPROMOTION` rows (their originals dominate on score, not tie-break). |
| Stable-sort bias | Same finding as merge-order bias above — they are the same mechanism (JS `Array.prototype.sort` stability + insertion order). |
| Other indirect promotion | **YES, the actual mechanism** — template-level strict promotion (page.tsx L634-693) computes `score`/`tagsHit`/`titleHit` at the TEMPLATE level and applies the SAME values to every sibling inspiration under that template, rather than evaluating each inspiration's own relevance. This is a **retrieval/scoring-input defect**, not a ranking-priority rule. |

**Conclusion**: charter §7.A's premise ("必须确认当前代码是否真的存在...") is answered — the "candidate preservation implemented as forced high rank" pattern the charter anticipated does **not** exist as a discrete rule. What exists instead is a *scoring input* defect that produces the same visible symptom (originals dominating Top-5) through score inflation rather than an explicit priority mechanism. This changes where the fix must go: not into `selectFinalCandidates` (which is already correctly "existence-only"), but into how `score`/`fields` are computed for template-promoted siblings in `scoreQueryTokens`.

### 4.2 Proposed mechanism

Within the `promoteAllUnderStrictTpl === true` branch (page.tsx L634-693), when a template strict-matches:

1. **Keep retrieval/inclusion exactly as-is** — every sibling inspiration under a strict-matched template continues to be added to `scored` (recall preserved, zero-result risk unchanged — Direction 1 untouched).
2. **Compute `titleHit`/`tagsHit`/`exactPhraseHit`/`subjectPresent` against the INDIVIDUAL INSPIRATION's own blob** (the same `title`/`category`/`tags`/`topics`/`search_aliases` fields already used for the non-template-promoted branch, lines 694-735) **in addition to** the template-level blob, rather than hardcoding `tagsHit: true` and deriving `titleHit`/`subjectPresent` solely from the template. Two-tier evidence:
   - If the SPECIFIC inspiration's own blob also matches → keep full evidence (today's behavior) — a genuinely on-topic inspiration under a correctly-promoted template scores exactly as it does today.
   - If ONLY the template-level blob matches but the specific inspiration's own blob does not → reduced evidence (`tagsHit` reflects the inspiration's own fields, not a hardcoded `true`; `titleHit` likewise). The inspiration is still retrieved (still in the pool, still visible if nothing better exists) but no longer scores identically to a genuinely relevant sibling.
3. **`base_retrieval` stays capped at 20 either way** (this term is not the primary driver of the inflation — `tagsHit`'s hardcoded `true` is) — no change needed to `scoreRecord()` or `relevanceScorerConfig.ts`'s `base_retrieval` weight.

### 4.3 Why this is minimal

- Touches exactly one branch of one function (`scoreQueryTokens`'s `promoteAllUnderStrictTpl===true` path, ~15 lines around L679-691) plus reuses field-derivation logic that already exists for the sibling branch (lines 694-777) — no new files, no new scorer terms, no new config constants.
- Does not change `relevanceScorer.ts`, `relevanceScorerConfig.ts`, `selectFinalCandidates`, `applyFamilySaturation`, or the never-zero floor at all.
- Does not change which records are retrieved — only how they are scored once retrieved.

### 4.4 Why this does not violate Direction 1

Direction 1 (existence floor: "original结果不能被rewrite清空") is about **inclusion**, not **score**. `selectFinalCandidates`'s unconditional-inclusion-of-`originalIds` rule is untouched by this mechanism — every template-promoted sibling is still in `originalIds`, still unconditionally included when `originalIds.size>0`. What changes is only whether that inclusion also comes with an inflated score; a low-relevance included original can now legitimately rank outside Top-5 while a more relevant one (original or not) ranks inside it — which is precisely the "existence floor, not rank floor" distinction the charter asks this stage to make explicit and enforce (§7.A point 7).

## 5. Mechanism B — Sense-collision / multi-term coverage

### 5.1 What the code audit found (charter §7.B's 11 sub-questions, condensed — full detail in `01_V2_R3_ROOT_CAUSE_REVALIDATION.md` §2.2)

- Multi-token queries: `subjectPresent` checks only the single longest token — the rest of the query's tokens are never checked for presence anywhere. **Confirmed defect.**
- Single-token queries: `subjectPresent = titleHit`, i.e. any whole-token hit (any sense) satisfies it. **Confirmed defect**, but structurally bounded — there is no "modifier" to require for a genuinely single-token query; the achievable fix there is a stronger single-signal bar (phrase/category-adjacent context), not "coverage" in the multi-term sense.
- No category/topic-consistency term exists (deliberately, per `relevanceScorer.ts`'s own header comment) — left unimplemented per charter instruction not to add signals without direct evidence; this design does not add one now either (no case in the 50 regressions was diagnosed as needing it specifically — the required-coverage change in §5.2 already explains all 18 sense-collision rows).
- No modifier-coverage term exists — same reasoning; §5.2's required-coverage mechanism against the FULL token set (not a separately-named "modifier" concept) covers what's needed without adding a distinct signal class.

### 5.2 Proposed mechanism (selected from the charter's candidate list — only the minimal, generalizable subset)

Two changes, both to `relevanceScorer.ts`/`relevanceScorerConfig.ts` (scorer-internal, no page.tsx retrieval change):

1. **Required multi-term coverage** (replaces the "longest-token-only" `subjectPresent` check for multi-token queries): a new `coverageRatio` field on `FieldHitInfo` — the fraction of the query's primary tokens (not just the longest one) found as whole-token hits anywhere in the candidate's title+tags blob. `subjectPresent` for multi-token queries becomes "the previously-designated subject token is present AND `coverageRatio` clears a minimum (e.g. ≥0.5 — the majority of query tokens, not all — see §5.3 for why not 100%)." Single-token queries are **unaffected by this specific change** (coverage of 1 token out of 1 is trivially 100%/0%, unchanged from today).
2. **Isolated-single-token score cap**: when a candidate's ONLY positive evidence is a single whole-token hit (title or tags) with `coverageRatio` at its minimum and no exact-phrase/category-topic corroboration, cap the combined `whole_token_title + whole_token_tags` contribution (e.g. at the `whole_token_tags` weight, `8`, instead of allowing both `title`+`tags` weights, `18+8=26`, to stack) — a single isolated hit should not score as strongly as genuine multi-signal agreement, even before path_agreement/subject penalties are applied. This directly targets the `banner`→`Bruce Banner`, `tag`→metadata-tag class of collision: these candidates typically have exactly one isolated whole-token hit and nothing else.

Both changes are **general, coverage/isolation-based rules**, not a per-word blacklist — they apply uniformly to every query and every candidate based on token-overlap arithmetic already computed by the existing tokenizer, satisfying charter §7.B point 9-10 (no LLM calls, no large blacklist).

### 5.3 Parameter/threshold design principles (not final numbers — final calibration happens in implementation, against the calibration set only)

- **Coverage minimum is a majority, not 100%**: requiring every query token to appear would break genuinely relevant results where one modifier is absent from a title (e.g. a candidate literally titled "wine" for query "wine label" if "label" isn't literally in its blob but the record IS a label). A majority threshold (≥50%) demotes the worst single-token collisions (which have exactly 1 of 2+ tokens = <50%) without demanding perfect coverage.
- **Isolated-hit cap, not a fixed penalty subtraction**: capping (not subtracting) prevents the value from going negative and colliding with `missing_subject_penalty`'s already-defined -15 semantics — keeps the two signals conceptually separate (one says "you have some evidence but it's thin," the other says "you have no subject evidence at all").
- **Both parameters are tuned ONLY against the 13-query calibration set (§6)**, never against the 37-query holdout or any full-suite run — satisfying charter §10 point 2 (no full-326 query-by-query tuning).

### 5.4 Why this is minimal

- Adds one new derived field (`coverageRatio`) computed from data the tokenizer already produces (primary token list, blob text) — no new retrieval, no new data source.
- Reuses the existing `subjectPresent`/`missing_subject_penalty` machinery rather than inventing a parallel scoring track.
- Composes with, does not replace, the existing 2-entry `searchPhraseProtection.ts` dictionary — a protected phrase's anchor-token check still runs first; the coverage/isolation rule is the general-case fallback for the other ~7,998 possible query token combinations that don't have (and per charter, should not need) a hand-curated entry.

## 6. Calibration / holdout split (full detail in `03_V2_R3_CASE_SPLIT.csv`)

| Set | Count | tuning_allowed | Purpose |
|---|---:|---|---|
| `calibration` | 14 | true | 13 real regression cases (4 overpromotion, 4 sense-collision, 2 catalog-gap, 3 weak-relaxed-dilution) covering zh/en, single/multi-word, few/many-candidate scenarios, + 1 non-regression high-quality-strict anchor (`statue`, a confirmed V2-R1 win) used to design mechanisms A/B's parameters |
| `holdout` | 37 | false | The remaining 37 of the 50 regressions (18 overpromotion, 14 sense-collision, 3 catalog-gap, 2 weak-relaxed-dilution — proportion approximates calibration's shape); never used to pick a threshold, only to check the fix generalizes |
| `previous_improvement_protection` | 8 | false | V2-R1 confirmed wins that must not regress: coffee cup, statue, 吉祥物, 贴纸, 咖啡馆菜单, periodic table, globe, 横幅 (broad-noise + flooding coverage) |
| `rewrite_invariant` | 4 | false | The 4 historical net-negative rewrite cases (V125/V127/V153/V271) — must stay non-zero; V271 (课程表) doubles as a calibration/holdout cross-check since it is also a live sense-collision regression |
| `functional_protection` | 6 | false | Structural invariants (original-non-empty floor, rewrite guard/subject binding, multi-path scoring, decomposition precision, phrase-protection dictionary, never-zero guarantee) — mechanism-level, verified via the existing `lib/__tests__/relevanceScorer.test.ts` suite plus new tests for A/B (§9) |

Calibration and holdout were split by fixed `query_id` before any parameter was chosen (this document does not propose specific numeric threshold VALUES beyond the qualitative "majority, not 100%" / "cap, not subtract" principles in §5.3 — exact numbers are an implementation-stage calibration exercise run only against the 14 calibration cases, never touching the 37 holdout cases until after numbers are frozen).

## 7. Why this is not a Relaxed Gate

- A Relaxed admission gate (raising/lowering `MIN_SCORE_WHEN_ORIGINAL_NONEMPTY`/`MIN_SCORE_WHEN_ORIGINAL_EMPTY`, or reintroducing a binary `hasStrict` check) can only ever affect **non-original candidates near the floor** — by construction it cannot touch `ORIGINAL_TEMPLATE_OVERPROMOTION` (all `isOriginal:true`, unconditionally included regardless of any floor) and cannot touch the 18 `RELAXED_SCORE_TOO_HIGH_SENSE_COLLISION` rows (already scoring 12-50, far above any floor a gate could reasonably set without also stripping genuine content elsewhere — confirmed by V2-R2's evidence and independently re-verified here).
- Reinstating the old binary `hasStrict` gate (charter §7.D's first prohibition) would re-break the very cases Direction 3 was built to fix (charter's own targeted/calibration wins: `coffee cup`, `statue`, `吉祥物`, `贴纸`) — those improvements specifically came from unifying strict/relaxed into one scored pool.
- A complex multi-layer gate (charter's second prohibition) would add a second admission mechanism on top of the scorer, duplicating logic already expressed as scores/floors, increasing surface area without addressing 90% of the actual regressions.
- Mechanisms A and B, by contrast, directly target the two mechanisms responsible for 40/50 (80%) of the regressions, and incidentally clean up the above-floor subset of the remaining 5 `WEAK_RELAXED_DILUTION_PARTIAL` cases as a side effect of more accurate scoring — without ever touching the floor/gate constants themselves.

## 8. Risks

| Risk | Mitigation |
|---|---|
| Mechanism A under-scores a genuinely relevant template-promoted sibling that happens to lack the exact literal token in its own blob (e.g. relies on a synonym/alias) | The two-tier fallback (§4.2) keeps the template-level match as a FLOOR, not a removal — a sibling with no own-blob evidence still gets SOME credit (today's hardcoded values become a ceiling, not eliminated); calibration cases 3/7/70/65 specifically test this |
| Mechanism B's coverage threshold demotes a genuinely relevant candidate whose title is terse (1-2 words) even for a multi-word query | Threshold is a MAJORITY not ALL (§5.3); calibration includes both few-candidate (teddy bear, black friday banner) and many-candidate (咖啡包装, 课程表) scenarios to catch this |
| Interaction between A and B on the same candidate (a template-promoted original that is ALSO a sense-collision) | No confirmed case in the 50 regressions requires both simultaneously (each row's proposed_mechanism in `02_V2_R3_REGRESSION_TRACE.csv` names exactly one); still, both mechanisms operate on independent `FieldHitInfo` fields (`tagsHit`/`titleHit` for A, `coverageRatio` for B) so they compose without a conflict by construction |
| Never-zero floor accidentally affected by coverage change | Coverage/isolation changes only affect `ScoreBreakdown.final_score` inputs upstream of `selectFinalCandidates` — the never-zero branch's logic (`MIN_KEPT_WHEN_ORIGINAL_EMPTY=5`) is untouched; catalog-gap calibration/holdout cases (盲盒/泰迪熊/练习册/笔袋/算盘) explicitly re-checked post-implementation |
| Regression on the 4 rewrite-invariant cases (esp. V271/课程表, which is both an invariant AND a calibration sense-collision case) | Explicit dual-purpose inclusion in the calibration set (§6) — the fix must satisfy both properties on the SAME query before being considered calibration-passing |

## 9. Rollback

Both mechanisms are additive/local: mechanism A modifies field-derivation inside one branch of one function; mechanism B adds one derived field and one score-cap rule inside `scoreRecord`. Rollback is a straightforward revert of the implementing commit(s) — no data migration, no config/schema change, no external service touched. `relevanceScorerConfig.ts`'s existing frozen-snapshot discipline (`13_SCORER_CONFIG_LOCK.json` pattern from V2-R1) should be repeated for any new constants introduced (coverage threshold, isolated-hit cap) so the exact frozen values are auditable and revertible independent of code.

## 10. Unit test plan (design only — not written or run this stage)

Extends `lib/__tests__/relevanceScorer.test.ts`'s existing `describe` blocks:
- `relevanceScorer.scoreRecord` (existing): add cases for the two-tier template-promotion evidence (mechanism A) — a sibling with own-blob evidence vs. one without, asserting the latter scores lower but is still non-negative/still-included-eligible.
- New `describe("relevanceScorer coverage / isolated-hit cap")` (mechanism B): majority-coverage-met vs. not-met on a synthetic multi-token query; isolated single-token hit capped vs. two-signal agreement uncapped; single-token queries confirmed UNCHANGED by the coverage addition (coverage of 1/1 trivial case).
- `relevanceScorer.selectFinalCandidates` (existing, Direction 1 floor invariant): re-run unchanged — this stage's design does not touch this function; existing tests should keep passing by construction of the design, and re-passing them post-implementation is part of the gate (§11).
- `searchPhraseProtection` (existing): re-run unchanged — confirms mechanism B composes with, not replaces, the 2-entry dictionary.
- New: golden-output tests for the 14 calibration-set queries (§6), snapshotting the qualitative expected_behavior column from `03_V2_R3_CASE_SPLIT.csv` (e.g. `statue` stays PASS; `figure`'s top-5 promotes `chinese figure fengshenbang` over `body movement verbs`) as executable assertions once mechanisms A/B are implemented.

## 11. Targeted evaluation plan (design only — not run this stage)

1. Re-run ONLY the 14-query calibration set + 8-query previous-improvement-protection set + 4-query rewrite-invariant set + 6 functional-protection checks (32 live queries total, well short of any full-suite run) against the implemented V2-R3 code, live server, same collector/judge methodology as V2-R1/V2-R2 (`scripts/collector.mjs` + `scripts/judge.mjs`, rubric-v1.1).
2. Confirm: calibration cases show the `expected_behavior` improvement direction; protection/invariant/functional cases show no regression from their recorded V2-R1 baseline.
3. THEN, and only then, re-run the 37-query holdout set (still far short of the full 326) to confirm the fix generalizes without holdout-specific tuning having occurred.
4. Only after both pass does a full-326 (and optionally old-328) re-run become the appropriate NEXT stage's task — explicitly out of scope for V2-R3 itself per charter prohibitions.

## 12. Full-326 gate (for the future stage that runs it — not this stage)

Per charter §8, a future full-326 run must clear, relative to V0:
1. PASS rate not lower than V0.
2. FAIL rate not higher than V0.
3. Zero-result rate not higher than V0.
4. Improved-query count ≥ regressed-query count.
5. Clearly better than V2-R1 (net-negative outcome, 50 regressed > 36 improved, must flip).
6. No new full-catalog flooding (family-saturation protection cases, e.g. `globe`/`横幅`, must hold).
7. A genuine net improvement, not a small-sample artifact confined to the 14 calibration cases.

## 13. Implementation file scope (for the future implementation stage)

Confirmed, based on this design, to be fully containable within the files V2-R1 already touched — no new files needed beyond possibly a config-lock snapshot file mirroring `13_SCORER_CONFIG_LOCK.json`:

- `app/[locale]/(public)/search/page.tsx` — mechanism A, inside `scoreQueryTokens`'s `promoteAllUnderStrictTpl===true` branch (~L634-693).
- `lib/relevanceScorer.ts` — mechanism B, inside `scoreRecord()` (new `coverageRatio` handling, isolated-hit cap logic).
- `lib/relevanceScorerConfig.ts` — mechanism B, new named constants (coverage minimum, isolated-hit cap value) alongside the existing `SCORER_WEIGHTS`.
- `lib/__tests__/relevanceScorer.test.ts` — new test cases per §10.
- No changes anticipated to `lib/searchPhraseProtection.ts`, `selectFinalCandidates`, `applyFamilySaturation`, or any never-zero/floor constant.

## 14. Design gate self-check

| Charter §10 condition | Met? | Basis |
|---|---|---|
| Root cause has code + candidate-level data support | Yes | §1, `01_V2_R3_ROOT_CAUSE_REVALIDATION.md` |
| Plan does not depend on full-326 query-by-query tuning | Yes | §5.3, §11 — calibration only against 14 fixed cases |
| Calibration/holdout separated | Yes | §6, `03_V2_R3_CASE_SPLIT.csv` |
| Minimal-change implementable | Yes | §4.3, §5.4, §13 — 3 existing files, no new mechanism classes |
| Direction 1/2/6 preserved | Yes | §4.4 (Direction 1); mechanism A/B never touch `selectFinalCandidates`'s merge-safety logic (Direction 2) or `searchPhraseProtection.ts` (Direction 6) — composes with it |
| V2-R1 broad-noise/flooding improvements preserved | Yes | §6 previous_improvement_protection set includes 吉祥物/贴纸/periodic table/globe/横幅; `applyFamilySaturation` untouched |
| No new LLM requests | Yes | Both mechanisms are pure text/arithmetic over already-tokenized data |
| No large manual blacklist | Yes | Coverage/isolation rules are general (token-overlap arithmetic); the existing 2-entry phrase dictionary is composed with, not expanded |
| Catalog gap vs ranking separated | Yes | `04_CATALOG_GAP_POLICY_PROPOSAL.md`; §1 cause 3 explicitly excluded from A/B |
| Clear test/stop gates defined | Yes | §10 (unit), §11 (targeted eval), §12 (future full-326 gate) |

**All 10 conditions met → design gate: PASS.**
