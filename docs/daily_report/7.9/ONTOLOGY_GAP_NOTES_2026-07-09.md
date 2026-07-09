# Ontology Gap Notes — 2026-07-09

## Overview

This document uses two inputs together: the **1,118 expanded query candidates** generated during the pressure-test expansion round (`docs/daily_report/7.7/02_expanded_from_58_query_candidates_2026-07-07.csv` [188 rows], `03_net_new_scenario_seed_queries_2026-07-07.csv` [98 rows], `04_high_signal_niche_query_candidates_500_2026-07-07.csv` [504 rows], and `05_simple_head_term_seed_bank_2026-07-07.csv` [328 rows]), and the **68-query Curify pressure-test results** that were actually executed and reviewed (`curify_search_auto_collect_with_claude_relevance_2026-07-07.csv`, `CURIFY_SEARCH_RELEVANCE_SUMMARY_2026-07-07.md`, `SEARCH_ISSUE_ATTRIBUTION_AND_PR_CANDIDATES_2026-07-09.md`, `VISUAL_RELEVANCE_AND_COMPETITOR_COMPARISON_2026-07-09.md`).

**Important scope note, stated explicitly per the task instructions:** the 1,118-row candidate pool has **not** been executed against Curify search. Only the 68 gold queries have real execution results, and only 12 of those 68 received full cross-platform competitor screenshot verification (Curify + Bing + Google + Canva + Pinterest). Everything in this document about the wider 1,118-row pool is a **taxonomy/pattern extraction**, not a relevance finding — it identifies *candidates* for future taxonomy expansion and future pressure-test rounds, using the 68-query results as the only source of ground truth currently available.

The companion CSV, `taxonomy_candidates_from_expanded_queries_2026-07-09.csv`, contains one row per candidate query (1,118 rows total) with a first-pass 3-tier ontology mapping plus taxonomy/ontology-gap classification columns. 14 rows in that CSV carry evidence-backed classifications, cross-referenced directly against the 68-query eval and the 12-case competitor screenshot review; the remaining 1,104 rows carry a documented, rule-based heuristic classification (keyword-dictionary matching against the query text) and are marked `unclear_or_needs_review` for `ontology_gap_type` unless otherwise noted, consistent with not overclaiming an unverified finding.

## 3-Tier Ontology Mapping

In simple terms:

- **Tier I — subject / entity / event / domain.** *What is this fundamentally about?* A subject, a named entity, an event, or a domain area — e.g., skincare, classroom, Amazon seller, NCT Dream, Genshin Impact, tea packaging, maker space, IEP, zones of regulation. This is the "topic" axis.
- **Tier II — information type / content function.** *What kind of information or function does the result need to serve?* Fact, comparison, timeline, process, checklist, quiz, vocabulary, procedure, activity card, tracker, poster, mockup, brand visual, product teaser, packaging, worksheet, moodboard, reference image. This is the "purpose" axis.
- **Tier III — layout / visual format / synthesis style.** *What should the rendered result actually look like?* Poster, card, flashcard, checklist, chart, grid, 3x3, 4x4, carousel, packaging mockup, wallpaper, moodboard, label set, folder cover, SOP flowchart, brand kit, visual manual. This is the "shape on screen" axis.

These three tiers are not fully independent — a query can specify all three ("maker space label set printable" = Tier I: maker space; Tier II: labeling/organization; Tier III: printable label set), or only one or two, leaving the others to be inferred or defaulted. Additionally, a **style / era / mood** modifier (Y2K, chrome, clean girl, K-beauty, low saturation, Chinese style, weirdcore, dreamcore) can layer on top of any of the three tiers, and often does in the queries that failed in this audit.

## High-Priority Missing Content Types

Per the task's stated principle — **missing content type is higher priority than missing one niche subject**, because a content-type gap affects every future query that needs that format, while a subject gap affects only that one entity. The following content types appear repeatedly across the candidate pool and/or caused confirmed search failures in the 68-query eval:

| Content type | Status | Confirmed-failing example(s) |
|---|---|---|
| Activity cards (STEM/coding/classroom) | **Confirmed missing-content-type gap** | `coding unplugged activity cards` |
| Checklist visuals (administrative/education) | **Confirmed missing-content-type gap** | `IEP accommodations checklist visual` |
| Classroom posters / procedure posters (SEL, behavior) | **Confirmed missing-content-type gap** | `zones of regulation poster classroom` |
| Label sets (printable, organizational) | **Confirmed missing-content-type gap** | `maker space label set printable` |
| Brand launch visuals | Confirmed retrieval gap (see Section: Retrieval vs. Taxonomy) | `Y2K chrome skincare launch poster`, `K-beauty glass skin brand launch visual` |
| Packaging mockups (vs. packaging *imagery*) | Untested distinction — flagged | `clean girl aesthetic skincare packaging mockup`, `国货美妆联名限定包装` |
| Amazon / e-commerce operational assets (EBC/A+, Vine insert cards, SOP flowcharts) | Confirmed taxonomy/alias gap | `Amazon EBC enhanced brand content layout`, `Amazon Vine review request insert card`, `私域用户运营SOP流程图` |
| SOP flowcharts (operations/business process) | Pattern seen in pool, untested | `私域用户运营SOP流程图`, `私域裂变任务宝海报` |
| Product teaser images (Xiaohongshu-style "种草图") | Confirmed alias/segmentation gap | `小红书香薰产品种草图` |
| Photocard / card design references (fandom) | Confirmed retrieval-mapping gap, not a content gap | `NCT Dream photocard template`, `光与夜之恋 卡面设计参考图` |
| Moodboard / wallpaper / visual reference formats | Mixed — see Gallery Image Recall discussion in the PR-candidates doc | `dreamcore aesthetic moodboard`, `genshin impact Furina fanart wallpaper 4k` |

The candidate CSV additionally surfaces a wider pattern beyond the 68-query set: 299 of the 1,118 candidates (26.7%) were heuristically classified as `layout_format_candidate` and 74 (6.6%) as `information_type_candidate` — i.e., roughly a third of the whole expanded pool is anchored primarily on a content-type/format signal rather than a specific-subject signal, reinforcing that content-type coverage is a structurally large axis of this taxonomy, not a handful of edge cases.

## Missing Specific Subjects

Lower-priority by the stated principle, but still worth tracking — these are gaps tied to **one specific entity**, not a reusable format:

- **Specific fandom / IP entities:** NCT Dream, Genshin Impact, Furina (character within Genshin Impact), 光与夜之恋, Love and Deepspace, 吉伊卡哇 (Chiikawa) × McDonald's collab content.
- **Specific game characters:** Furina (Genshin Impact) specifically, as distinct from "Genshin Impact" generally — the query `genshin impact Furina fanart wallpaper 4k` names a specific character, not just the franchise.
- **Specific niche products / platform terms:** Amazon Vine (a specific Amazon program), EBC (a specific Amazon content format), specific K-beauty product-line names if they appear in future rounds.
- **Specific cultural or aesthetic terms:** 低饱和 (low-saturation, a color-style term rather than a subject, but functions like a specific qualifier in the same way a specific subject would), 应援色 (fandom support-color term, not tested in the 68-query set but flagged in the PR-candidates doc as a likely alias-gap pattern), 翼龙单词卡 (pterosaur vocabulary card — a per-task example of a single-subject vocabulary-card gap that should not be over-generalized into a content-type finding).

**Critical distinction confirmed by this audit:** for 3 of the 5 fandom/IP entities actually tested with competitor screenshots (NCT Dream, 光与夜之恋, and Curify's own retrieval for Genshin/Furina), the "missing specific subject" framing turned out to be **wrong** — the content exists abundantly on Bing, Google, and Pinterest, so the correct classification is a retrieval-mapping gap (NER/decomposition), not a content-supply gap. Only the Canva-specific angle on `genshin impact Furina fanart wallpaper 4k` (re-verified twice, including after a manual logged-in re-capture, and still showing zero relevant content) is a genuine, confirmed missing-specific-subject / content-supply gap. **This means "specific subject" queries should default to a retrieval-gap hypothesis and require competitor verification before being written off as a content-library gap** — the opposite of what intuition might suggest.

## Retrieval vs. Taxonomy vs. Content Supply

For each major gap category surfaced in this audit:

| Gap | Classification | Basis |
|---|---|---|
| `wrong_decomposition` (NCT Dream, maker space, dreamcore, Genshin/Furina, 光与夜之恋) | **Retrieval issue** | Visually confirmed: entity/qualifier recognized enough to generate a broadened-query banner, but not carried through to retrieval; competitors surface the content abundantly. |
| Chinese segmentation (低饱和国风茶包装设计, 光与夜之恋, 私域用户运营SOP流程图, 手冲咖啡工作室视觉手册) | **Retrieval issue** (pre-retrieval NLP step specifically) | Qualifying prefixes dropped during tokenization; same failure shape as English decomposition, language-specific mechanism. |
| Amazon EBC/Vine/GRWM/RTI/WIDA acronyms | **Taxonomy / alias-mapping issue** | Zero-result (not even a broadened attempt) suggests the term isn't in the internal vocabulary at all, not that decomposition ran and failed. |
| `missing_content_type` (maker space, zones of regulation, IEP, packaging mockups) | **Retrieval issue** (routing/multi-path specifically) | Correct format exists in the visually-reviewed competitor set; Curify appears to use one retrieval path regardless of requested output format. |
| Genshin/Furina content on Canva specifically | **Content supply issue** | Confirmed via two independent captures (automated + manual logged-in re-capture) that Canva's own template library lacks licensed anime/game character art — a platform-appropriate content gap, not a bug. |
| Amazon-seller operational assets broadly (社群接龙, 私域裂变任务宝) | **Unclear / needs more evidence** | Only 2 of 7 zero-result Amazon/e-commerce-ops queries (EBC) were competitor-verified; the rest could be alias gaps or genuine content gaps — not yet distinguishable. |
| Special-ed/homeschool content broadly (RTI, WIDA, first-then board, charlotte mason, loop schedule, newcomer kit) | **Unclear, leaning retrieval** | Only 2 of 8 (IEP, zones of regulation) were competitor-verified, and both leaned retrieval — but this is inferred, not confirmed, for the other 6. |
| The remaining ~1,104 untested candidate-pool rows | **Unclear / needs more evidence** | No execution or competitor data exists for these; the taxonomy CSV's `ontology_gap_type` column correctly reflects this as `unclear_or_needs_review` for nearly all of them. |

## Candidates for Taxonomy Expansion

Summarized from the 1,118-row candidate CSV (heuristic, rule-based extraction — see Limitations):

- **Tier I (subject/entity) candidates:** 575 of 1,118 rows (51.4%) were classified `subject_candidate` — the dominant category, expected given the head-term bank (328 rows, all pure subjects by construction) and many niche-pool queries that name a specific entity/domain without a strong format signal (e.g., `儿童理发店卡通品牌设计`, `跨境电商产品listing图`).
- **Tier II (information type/function) candidates:** 74 rows (6.6%) classified `information_type_candidate` — checklist, tracker, quiz, vocabulary, procedure, and comparison-style functional terms, concentrated in the education and e-commerce-ops scenes.
- **Tier III (layout/format) candidates:** 299 rows (26.7%) classified `layout_format_candidate` — poster, card, label, flowchart, mockup, moodboard, and similar rendered-format terms; this is the second-largest category after pure subjects, reinforcing that a meaningful fraction of real query demand is format-driven rather than subject-driven.
- **Style/era/mood candidates:** 17 rows explicitly flagged `style_candidate` (a style/aesthetic term dominates with no strong subject or format signal), plus a further ~40+ rows where a style keyword co-occurs with a subject or format term (captured in the `style_era_mood` column even when the row's primary `taxonomy_candidate_type` is something else) — Y2K, 国风, 低饱和, weirdcore, dreamcore, K-beauty/glass skin, clean girl, 复古/vintage are the most frequent.
- **Alias candidates:** 19 rows flagged `alias_candidate` — concentrated in Amazon-seller jargon (EBC, Vine, GRWM), fandom vocabulary (photocard, 卡面), and platform-specific format terms (种草图, 九宫格) — a small but high-value list given how directly they map to the confirmed `taxonomy_alias_gap` findings in the 68-query eval.
- **Mixed multi-intent candidates:** 134 rows (12.0%) carry two or more strong signals at once (e.g., a named style plus a named format, or a named entity plus a named format) — these are the queries most likely to expose a decomposition bug, since the system must correctly retain multiple qualifiers simultaneously rather than just one.

## Relationship to Search Improvements

The taxonomy/ontology candidates in this document and the accompanying CSV are meant to feed directly into the PR candidate directions already proposed in `SEARCH_ISSUE_ATTRIBUTION_AND_PR_CANDIDATES_2026-07-09.md`:

- **NER / named-entity protection** — the `alias_candidate` and `subject_candidate` rows that name a specific IP/brand/franchise (NCT Dream, Genshin Impact, Furina, 光与夜之恋, Love and Deepspace, 吉伊卡哇) form a starter gazetteer of entities that should be protected from decomposition.
- **Chinese segmentation** — every Tier-I/Tier-III combination row in Chinese where a multi-character qualifier precedes a shorter noun (低饱和+国风+茶包装, 私域+用户运营+SOP+流程图, 手冲+咖啡工作室+视觉手册) is a candidate test case for validating a segmentation fix before and after.
- **Alias expansion** — the 19 `alias_candidate` rows plus the acronym/jargon terms identified in the `missing_content_type`/`taxonomy_alias_gap` findings (EBC, A+, Vine, GRWM, RTI, WIDA, 种草图, 九宫格) form the seed list for the alias-to-taxonomy mapping table proposed in the PR-candidates doc.
- **Semantic synonym replacement** — cross-referencing near-synonymous Tier II terms across the candidate pool (e.g., "checklist" vs. "tracker" vs. "cheat sheet"; "moodboard" vs. "visual reference" vs. "inspiration board") surfaces which synonym clusters are large enough to prioritize for embedding-based expansion.
- **Multi-path retrieval** — the 299 `layout_format_candidate` and 74 `information_type_candidate` rows collectively make the case that an `expected_content_type`/`expected_output_format` classifier has enough real query volume behind it to justify the retrieval-routing investment proposed in the PR-candidates doc.
- **Content-type-aware ranking** — even where full multi-path retrieval isn't feasible immediately, the Tier II/Tier III columns in the candidate CSV could be used as a ranking-boost signal (prefer results whose own content-type tag matches the query's inferred Tier II/III) as a lighter-weight interim fix.

## Recommended Next Steps

- **Review high-priority content-type gaps with the manager** — lead with the four confirmed `missing_content_type` cases (IEP checklist, zones of regulation poster, coding-unplugged activity cards, maker-space label set), since these have both competitor evidence and a clean content-type framing that's easy to present.
- **Decide which gaps require templates/examples (content supply) vs. retrieval fixes** — use the Retrieval vs. Taxonomy vs. Content Supply table above as the starting triage; note that the *default* hypothesis for specific-subject/fandom gaps should now be "retrieval," not "content," per the corrected findings in this audit — flip that default only when a competitor check (like the Canva/Genshin case) confirms otherwise.
- **Add alias/synonym candidates to the search-improvement backlog** — the 19 `alias_candidate` rows in the CSV, plus the specific acronyms named in the PR-candidates doc, are ready to seed the alias-expansion PR without further extraction work.
- **Use the taxonomy candidates to guide future query expansion and self-diagnosis** — when selecting the next round of queries to execute from the untested ~1,050-row remainder of the candidate pool, prioritize rows tagged `layout_format_candidate` or `information_type_candidate` with `priority = P0` (carried through from the candidate pool's own pre-assigned priority where available) to keep testing content-type coverage, which the stated principle treats as higher-value than testing more single-subject niche queries.

## Limitations

- **This extraction is first-pass and partially automated.** The 3-tier mapping, style/era/mood tagging, and taxonomy-candidate-type classification for all rows outside the 14 evidence-backed cases were generated by a documented, rule-based keyword-matching script (dictionaries for format/style/info-type/alias/entity terms), not by individually reading and judging all 1,118 rows. This is a reasonable first pass for triage purposes but should not be treated as a precise, human-verified categorization.
- **Not all 1,118 candidates were executed.** This document and CSV are a taxonomy/pattern extraction over the *candidate pool*, not a relevance audit — the vast majority of rows have no execution result at all.
- **Only 68 gold queries have Curify search results**, and even those are from a single execution pass (2026-07-07), not re-verified live as of this writing.
- **Only 12 of those 68 P0 cases have full competitor screenshots** (Bing, Google, Canva, and manually-added Pinterest) — the `evidence_source` column in the taxonomy CSV marks exactly these 14 rows (12 with full competitor verification, 2 with 68-query metadata only) as anything other than `candidate_pool_not_executed`; every other row's `ontology_gap_type` is honestly left as `unclear_or_needs_review`.
- **Human spot-check is recommended before turning any of these candidates into production taxonomy.** In particular, the heuristic keyword dictionaries used for this extraction (see the script's `FORMAT_KEYWORDS`/`STYLE_KEYWORDS`/`INFO_TYPE_KEYWORDS`/`ALIAS_KEYWORDS`/`ENTITY_HINTS` lists) are a first attempt and will have both false positives (a keyword matching in an unintended sense) and false negatives (relevant terms not yet in the dictionary) — a human review pass, especially over the `mixed_multi_intent_candidate` and `alias_candidate` rows, would meaningfully improve precision before this feeds into an actual taxonomy or alias table.

No production code was touched in producing this document or the accompanying CSV. No files were staged or committed. The final consolidated work report has not been written.
