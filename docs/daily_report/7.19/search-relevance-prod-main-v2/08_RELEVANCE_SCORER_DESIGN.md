# Stage 7: Unified Relevance Scorer Design

Date: 2026-07-19. Implementation: `lib/relevanceScorer.ts` + `lib/relevanceScorerConfig.ts` + `lib/searchPhraseProtection.ts` in the V2 worktree, integrated into `app/[locale]/(public)/search/page.tsx`. Commit: `c5d77149 feat(search): unified explainable relevance scorer (directions 1, 2, 4, 5, 6, 9)`.

## Goal and constraints (re-stated, all honored)

Lightweight, text-based, deterministic, explainable. No new LLM requests. No external embeddings. No learned reranker. No dependency on human ground truth. No feature implemented without direct V0 evidence (see `07_V0_TARGET_CASE_RECONFIRMATION.csv`).

## What informed the design

Per Stage 2's audit finding (`02_PRODUCTION_SEARCH_CODE_AUDIT.md`), V0's existing scoring is a two-tier bucket system (`strict: boolean`, `score = primaryHits + bigramHits`) with **zero per-field weighting** and a **binary `hasStrict` merge gate** that can drop all-relaxed original results the instant any path anywhere produces a strict hit. Stage 4's reconfirmation (`07_V0_TARGET_CASE_RECONFIRMATION.csv`) produced two DIRECTLY CONFIRMED, live-reproduced collision cases on V0:

1. `coffee cup` → multiple "World Cup" team-sticker-poster inspirations matched (284/335 templates, ~85% of the whole catalog).
2. `black friday banner` → a Marvel "Black Widow" MBTI character card ranked #1.

These two cases are the primary evidence backing every signal below. Signals from the design doc's candidate list WITHOUT direct V0 evidence (a standalone Category/Topic Consistency term separate from field_support; a standalone Modifier Coverage term) were **not implemented** — seeing them in the design doc is not sufficient justification per the task's explicit anti-checklist-completionism instruction.

## Implemented signals (see `09_SCORE_FEATURE_AUDIT.csv` for the full per-feature evidence table)

| Signal | Direction | What it measures | Weight (v1.0.0) |
|---|---:|---|---:|
| `base_retrieval` | carry-over | existing primaryHits+bigramHits, capped at 20 | ×1.0 |
| `exact_phrase` | 4 | protected phrase or full multi-token query found verbatim in title/tags blob | +40 |
| `whole_token` (title) | 4 | whole-token/phrase hit in the record's title/category blob | +18 |
| `whole_token` (tags) | 4 | whole-token/phrase hit in tags/topics/aliases blob | +8 |
| `path_agreement` | 5 | 2+ distinct retrieval paths independently matched this record, **only when the record's core subject is present** | +3/hit, capped +12 |
| `substring_penalty` | 4 | match relied only on a CJK bigram/substring fallback, no whole-token hit anywhere | -22 |
| `missing_subject_penalty` | 4, 6 | the query's recognized core subject (protected phrase or longest primary token) is absent from title/tags | -15 |
| `family_saturation_penalty` | 5, 10 | applied once a template_id family has already placed 6+ records ahead of this one in the ranked pool | -6/excess, capped -30 |

Every field is documented with its exact evidence case in the `reasons: string[]` output for that candidate (design doc 9.3's `reasons` requirement).

## Why `path_agreement` requires `subjectPresent` (the most important calibration finding)

The first implementation allowed cross-path agreement to accumulate regardless of subject relevance. Live testing against the running V2 server exposed exactly the failure mode Direction 5 warns against ("不简单按路径数量累加出不合理高分"): the Black Widow MBTI card was matched by 5 separate rewrite/decomposition paths (mostly via a generic `hero-banner` tag), earning `path_agreement=+12`, which fully offset `missing_subject_penalty=-15` and kept it ranked #1. The fix: `path_agreement` is now zero whenever `subjectPresent` is false, regardless of how many paths hit the record. This is documented in `lib/relevanceScorer.ts` with the specific case that exposed it.

## Why `exactPhraseHit`/`subjectPresent` are computed against the ORIGINAL query, not each path's own text

Initially these were recomputed per retrieval pass (original query, each rewrite, each decomposition slot) from that pass's own tokens. This let a narrow decomposition slot (e.g. an `output` slot resolving to just `"banner"`) trivially "satisfy" subject presence for itself, and because field-hit info is OR-merged across paths when a record is found by multiple passes, one weak pass could poison the merged record's fields even though the ORIGINAL query's actual subject was never present. Fixed by computing `originalProtectedPhrases` / `originalQueryPhraseText` / `originalPrimaryTokensForSubject` once from the user's actual typed query and using them consistently across every path's per-record field derivation (see the comment block at their definition in `page.tsx`).

## Why protected phrases use an "anchor token," not the literal phrase, for Subject Coverage

Requiring the literal 2-word phrase (`"coffee cup"`) verbatim in a candidate's blob incorrectly penalized genuinely relevant near-matches like a `coffee drinks` vocabulary card (contains "coffee" but not the literal phrase). Each `ProtectedPhrase` entry in `lib/searchPhraseProtection.ts` now specifies an `anchorToken` — the semantically load-bearing, low-collision word (`"coffee"` for `coffee cup`, `"friday"` for `black friday`) — and `subjectPresent` is true if either the full phrase OR the anchor token is present. This correctly keeps "coffee drinks"/"coffee machine" as on-subject while still excluding "World Cup" content (which contains neither "coffee" nor the phrase).

## Known limitation (honestly documented, not hidden)

The generic (non-protected-phrase) Subject Coverage heuristic — "the longest primary token of the original query" — is a simple, explainable proxy, not a real linguistic subject detector. For queries where the catalog has genuinely no relevant content at all (confirmed CATALOG_GAP case: `plush pillow` — every single candidate the pipeline can find, across all rewrite/decomposition paths, scores below the quality floor), the scorer correctly identifies all candidates as low-quality (`missing_subject_penalty` fires, `final_score` deeply negative), but the never-zero safety net in `selectFinalCandidates` still surfaces the least-bad ones rather than an empty page — because the task's explicit gate is "V2's zero-result rate must not exceed V0's," and V0 was already showing weak results for this query. This is a deliberate, evidence-based tradeoff, not an oversight: showing weak results (correctly flagged internally as low-scoring) is preferred over a new zero-result regression, but it is also not a full fix for the underlying content gap — that gap is a `CATALOG_GAP`, not something a text scorer can solve. Reported honestly here rather than claimed as resolved.

## Weight source of truth

All weights live in `lib/relevanceScorerConfig.ts` (design doc 9.2's "single configuration source" requirement) — no weight is hardcoded anywhere else. See `13_SCORER_CONFIG_LOCK.json` for the frozen snapshot.
