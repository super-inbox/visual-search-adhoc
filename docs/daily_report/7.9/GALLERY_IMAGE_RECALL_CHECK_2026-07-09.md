# Gallery Image Recall Check — 2026-07-09

## Overview

Gallery/inspiration-style image recall was called out as a separate open item throughout this audit rather than folded into the general relevance analysis, for a specific reason: the originally-specified labeling rule (`gallery_under_recall` — flag when a moodboard/aesthetic/wallpaper/visual-reference query returns no gallery-type result) **could not be applied as written**, because the underlying metadata does not distinguish a "gallery" result type from any other visual-reference type (`CURIFY_SEARCH_RELEVANCE_SUMMARY_2026-07-07.md`, "Gallery Image Recall Observations" section). Under a literal reading of the data, the `gallery_under_recall` tag fired on **0 of 68 rows** — not because gallery recall is actually fine, but because the column needed to measure it doesn't carry the value it would need to. This document exists to resolve that ambiguity: is gallery recall actually healthy, or is it an unmeasured gap hiding inside the `bad_relevance`/`wrong_decomposition` numbers? The short answer, developed below, is **the latter for several cases, but the metadata genuinely cannot separate "gallery recall" from "general relevance" as an independent axis** — so this document treats that limitation as the headline finding, not a caveat.

## What Can and Cannot Be Measured

**Cannot be measured:** a distinct "gallery" result type. Across all 68 rows in `curify_search_auto_collect_with_claude_relevance_2026-07-07.csv`, the `top_10_result_types` column contains **only two distinct tokens: `inspiration` and `template`** — confirmed by re-checking every row's type string directly for this document. There is no `gallery` value, no subtype, and no way to distinguish "gallery-style reference image" from any other `inspiration`-typed result. This means:
- A query cannot be flagged as "gallery recall failed" in any way that's distinguishable from "inspiration recall failed" or "relevance failed" generally.
- The 0/68 `gallery_under_recall` count from the prior pass is a **measurement artifact**, not a clean bill of health, exactly as flagged in the prior summary doc.

**Can be measured, with caveats:** whether `inspiration`-typed results are topically on-target for queries that clearly *want* a gallery/moodboard/reference-image experience. This is a proxy, not a direct measurement of "gallery recall" — it tells us whether the *format* (inspiration-style image, as opposed to a structured template) was returned, and separately whether the *subject matter* of that format matched the query. Both are checkable from `top_10_result_titles`/`top_10_result_tags_or_labels` plus direct screenshot inspection where available.

**Notable finding while checking this:** it is not only the classically "gallery-oriented" queries (moodboard, wallpaper, aesthetic) that get typed `inspiration` — several queries explicitly asking for a structured asset (`NCT Dream photocard **template**`, `Y2K chrome skincare launch **poster**`, `K-beauty glass skin brand launch **visual**`, `低饱和国风茶包装**设计**`) also came back **100% `inspiration`-typed** (10/10), not `template`-typed at all. This suggests the `inspiration`/`template` type split in the underlying data may not reliably reflect the requested asset format even in the cases we already know are unrelated to gallery-style browsing — reinforcing that this type field is a weak signal for content-format questions generally, not just for gallery recall specifically.

## Gallery-Oriented Query Candidates

From the 68 gold-set queries, searching `query` text for gallery/inspiration-style signal terms (moodboard, inspiration/inspo, wallpaper, aesthetic, sticker, fanart, reference/参考图, 壁纸, 美学, 情绪板, 灵感) surfaces **10 candidates**:

| Query | Label | Issue type(s) | Result count | `top_10_result_types` |
|---|---|---|---|---|
| dreamcore aesthetic moodboard | FAIL | wrong_decomposition;bad_relevance | 4 | inspiration ×3, template ×1 |
| weirdcore aesthetic sticker design | FAIL | wrong_decomposition;bad_relevance | 10 | inspiration ×10 |
| genshin impact Furina fanart wallpaper 4k | FAIL | wrong_decomposition;bad_relevance;competitor_gap | 6 | inspiration ×3, template ×3 |
| 光与夜之恋 卡面设计参考图 | FAIL | wrong_decomposition;bad_relevance;competitor_gap | 10 | inspiration ×9, template ×1 |
| clean girl aesthetic skincare packaging mockup | FAIL | bad_relevance;missing_content_type;wrong_decomposition | 10 | inspiration ×10 |
| dress to impress historical royalty outfit inspo | WARN | bad_relevance | 10 | inspiration ×10 |
| 汉服马面裙叠穿灵感图 | WARN | bad_relevance | 10 | inspiration ×10 |
| heritage brand rebrand moodboard | WARN | bad_relevance;content_gap | 10 | inspiration ×10 |
| blind box toy character sticker sheet | WARN | bad_relevance | 10 | inspiration ×10 |
| 松弛感生活方式插画 | WARN | bad_relevance;missing_content_type | 10 | inspiration ×10 |

For context, from the wider 1,118-query expanded candidate pool (not executed), the same signal terms surface many more gallery-oriented candidates for future rounds — see `ONTOLOGY_GAP_NOTES_2026-07-09.md`'s discussion of moodboard/wallpaper/visual-reference formats — but this document restricts itself to the 10 queries above plus the 7 already-executed cases named in the task, since those are the only ones with real execution data.

Of the 7 cases explicitly named for this check (`NCT Dream photocard template`, `genshin impact Furina fanart wallpaper 4k`, `光与夜之恋 卡面设计参考图`, `Y2K chrome skincare launch poster`, `K-beauty glass skin brand launch visual`, `低饱和国风茶包装设计`, `小红书香薰产品种草图`), 2 (`genshin impact Furina fanart wallpaper 4k`, `光与夜之恋 卡面设计参考图`) also appear in the gallery-signal-term table above; the other 5 don't contain a literal gallery/moodboard/aesthetic keyword but are included here because they were part of the 12-case full screenshot review and because "photocard template," "card design reference," and "product teaser image" are visual-reference-adjacent formats worth checking against the same gallery-recall question.

## Observed Patterns

Reading `top_10_result_titles` alongside `claude_issue_type` across the 17 total cases considered here (10 gallery-signal-term matches + 7 named cases, with 2 overlapping), three distinct patterns emerge:

1. **Format matched, subject didn't, and it's a clean split.** `heritage brand rebrand moodboard` is the cleanest example: the first 3 of 10 results are genuine, well-formed brand-identity moodboards (structurally exactly what was asked for) — but for a coffee shop, a bakery, and a grocery store, not a heritage-brand rebrand. The gallery/moodboard *format* recall worked; the *subject* recall (heritage, rebrand) did not. `dreamcore aesthetic moodboard` shows the identical pattern in miniature (3 of 4 results are real brand moodboards, just F&B-generic instead of dreamcore-styled).
2. **Format matched, subject was dropped down to a bare generic word.** `NCT Dream photocard template`, `genshin impact Furina fanart wallpaper 4k`, `光与夜之恋 卡面设计参考图`, and `weirdcore aesthetic sticker design` all return `inspiration`-typed results, but the qualifying entity or style term (NCT Dream, Furina, 光与夜之恋, weirdcore) was decomposed away entirely, leaving a match on a leftover generic word ("dream," "friends"/Ghibli refs, "night," or unrelated meme-sticker/mythical-beast content). This is the same `wrong_decomposition` pattern documented throughout this audit — it happens to manifest in `inspiration`-typed results here because these particular queries are gallery-adjacent, not because gallery recall has a distinct failure mode.
3. **Partially topical, mixed with unrelated clutter.** `dress to impress historical royalty outfit inspo`, `汉服马面裙叠穿灵感图`, and `blind box toy character sticker sheet` all return a mix of genuinely topical results (dynasty costumes; character-IP stickers) alongside clearly unrelated items (an anime-director bio; a club sandwich; national football team flags) in the same 10-result set — a ranking/fusion weakness rather than a clean subject or format miss.

None of the 17 cases show a pattern where the *format itself* (gallery/inspiration-style browsing) was unavailable or suppressed — `inspiration`-typed results were returned in every single case with a nonzero result count. The failures are entirely in **what** the inspiration-typed results depict, not **whether** inspiration-typed results were returned at all. This is an important distinction: it means the observable evidence points toward the same retrieval/decomposition/ranking causes already documented elsewhere in this audit, not toward a gallery-specific recall mechanism failing on its own.

## Screenshot Evidence

Of the 7 named cases, all 7 were part of the 12-case full screenshot review (`VISUAL_RELEVANCE_AND_COMPETITOR_COMPARISON_2026-07-09.md`, `COMPETITOR_SCREENSHOT_INDEX_2026-07-09.md`), so direct visual confirmation exists (not just metadata) for all of them:

- **`genshin impact Furina fanart wallpaper 4k`** — the screenshot shows exactly 3 `inspiration`-typed cards render, captioned "friends," "howls moving castle," "neighbor totoro" (Studio Ghibli references), plus 3 `template`-typed "Media-Themed Wallpaper Poster" cards. Bing, Google, and Pinterest all return gorgeous, abundant, exact Furina 4K fanart wallpapers — confirming this is a retrieval-mapping gap, not a gallery-format problem (the wallpaper-gallery format itself works; the subject match failed). Canva alone is a confirmed, re-verified genuine content gap for this specific IP.
- **`光与夜之恋 卡面设计参考图`** — screenshot shows a Leo zodiac card, La La Land fan art, a night-routine poster, and several unrelated AI-infrastructure diagrams. Bing, Google, and Pinterest all return exact official game character-card art; Canva shows a nuanced partial-recognition result (correct character-name filter chips, no matching cards) after a manual re-capture. Same conclusion: retrieval-mapping gap, gallery format itself unaffected.
- **`NCT Dream photocard template`** — screenshot shows Curify's own broadened-query banner naming the correct entity, yet the rendered grid still shows Dream-of-the-Red-Chamber scrolls. Pinterest returns precisely NCT Dream-branded photocard templates by name (the strongest single-platform match in the whole 12-case sample). Confirmed retrieval-mapping/NER gap.
- **`Y2K chrome skincare launch poster`** and **`K-beauty glass skin brand launch visual`** — both screenshots show a fully unrelated consumer-product grab-bag (socks, headphones, eyemasks, coffee makers). All four competitor platforms (including Pinterest, which has a pin literally titled "Y2K Chrome Aesthetics for Beauty") return genuinely on-topic results. Confirmed retrieval gaps, not gallery-recall-specific issues — these are brand-visual/poster queries with a gallery-adjacent presentation, not moodboard queries per se.
- **`低饱和国风茶包装设计`** and **`小红书香薰产品种草图`** — both screenshots show generic Western grocery-product photography / unrelated lifestyle items, with the Chinese qualifying prefixes (低饱和, 国风, 香薰) dropped. Bing, Google, and Pinterest all return abundant, precisely matching content. Confirmed Chinese-segmentation/alias gaps (see `SEARCH_ISSUE_ATTRIBUTION_AND_PR_CANDIDATES_2026-07-09.md`), not gallery-specific failures.

**None of the 7 named cases turned out to be a gallery-recall-specific issue on closer inspection** — every one resolves to a cause already documented elsewhere in this audit (NER/decomposition, Chinese segmentation, or a Canva-specific content gap). This is itself useful evidence: it suggests gallery-style queries fail for the *same* reasons other query types fail, rather than exposing a unique gallery-recall weakness — though this conclusion is limited to these 7 cases and cannot be generalized to the full gallery-oriented query space without further testing (see Limitations).

## Issue Classification

| Query | Classification | Basis |
|---|---|---|
| heritage brand rebrand moodboard | `inspiration_result_but_topic_mismatch` | Cleanest case: 3/10 results are structurally correct moodboards, just wrong subject (F&B instead of heritage/rebrand). |
| dreamcore aesthetic moodboard | `inspiration_result_but_topic_mismatch` (+ `retrieval_mapping_gap`) | Same structural-moodboard-wrong-subject pattern as above, compounded by the "dreamcore" style qualifier being dropped. |
| dress to impress historical royalty outfit inspo | `inspiration_result_but_topic_mismatch` | Topically adjacent (dynasty costume) results mixed with an unrelated item; format recall intact. |
| 汉服马面裙叠穿灵感图 | `inspiration_result_but_topic_mismatch` | Same pattern, Chinese-language case. |
| blind box toy character sticker sheet | `inspiration_result_but_topic_mismatch` | Some genuine character-IP sticker results mixed with unrelated food/sports items. |
| genshin impact Furina fanart wallpaper 4k | `retrieval_mapping_gap` (Curify overall); `content_type_gap`-adjacent finding specific to Canva only | Visually confirmed via competitor screenshots — see Screenshot Evidence above. |
| 光与夜之恋 卡面设计参考图 | `retrieval_mapping_gap` | Visually confirmed via competitor screenshots. |
| NCT Dream photocard template | `retrieval_mapping_gap` | Visually confirmed via competitor screenshots. |
| weirdcore aesthetic sticker design | `retrieval_mapping_gap` | Style qualifier dropped; matched on unrelated meme-sticker/mythical-beast content instead. |
| Y2K chrome skincare launch poster | `retrieval_mapping_gap` | Visually confirmed via competitor screenshots. |
| K-beauty glass skin brand launch visual | `retrieval_mapping_gap` | Visually confirmed via competitor screenshots. |
| 低饱和国风茶包装设计 | `retrieval_mapping_gap` | Visually confirmed via competitor screenshots (Chinese segmentation). |
| 小红书香薰产品种草图 | `retrieval_mapping_gap` | Visually confirmed via competitor screenshots (Chinese segmentation/alias). |
| clean girl aesthetic skincare packaging mockup | `content_type_gap` (+ `retrieval_mapping_gap`) | No packaging-mockup template type surfaced at all; style qualifier also dropped. Not competitor-verified. |
| 松弛感生活方式插画 | `needs_manual_review` | Ambiguous: some room/lifestyle results fit the mood, but it's unclear whether an "illustration" content type was ever attempted; not competitor-verified. |
| **(structural, applies to all 68 rows)** | `no_distinct_gallery_type_to_measure` | `top_10_result_types` contains only `inspiration`/`template` — there is no way to isolate a gallery-specific recall metric from this data at all, for any query. |

**No query in this check was classified as `likely_gallery_recall_gap`.** That category would require evidence that the gallery/inspiration *format itself* is being suppressed or under-returned for gallery-appropriate queries — and in every case examined, `inspiration`-typed results were returned; the failure is in subject-matter relevance or ranking, not format availability. This is a meaningful finding on its own: **the observable data gives no support for a distinct "gallery recall" problem separate from the general relevance/decomposition/segmentation problems already documented.** It cannot rule one out either, given the instrumentation gap — but it does not provide positive evidence for one.

## Recommended Fix Directions

- **Add or expose a distinct gallery image result type, if one exists internally but isn't surfaced in this metadata.** If Curify's backend already distinguishes gallery-style reference images from other `inspiration`-typed content, exposing that distinction in the logged/exported metadata would let future audits measure this directly instead of relying on the proxy analysis in this document.
- **Improve gallery tags/aliases** for terms that signal a gallery/moodboard/reference-image intent specifically (moodboard, inspo, visual reference, 灵感图, 情绪板, 参考图) so these queries can be tracked and evaluated as their own cohort, distinct from template/poster/checklist-style structured-asset queries.
- **Boost gallery results for inspiration-oriented queries** — but only once subject-matter relevance is fixed; boosting the *volume* of inspiration-typed results without fixing the entity/style-dropping problem documented in `SEARCH_ISSUE_ATTRIBUTION_AND_PR_CANDIDATES_2026-07-09.md` would likely just return more of the same wrong-subject moodboards.
- **Connect moodboard / visual reference / aesthetic queries to gallery recall** by explicitly mapping this query cohort's expected output type as "gallery/inspiration image" in the same `expected_content_type`/multi-path-retrieval mechanism proposed for other content-type gaps — this cohort would benefit from the same fix direction as the `missing_content_type` PR candidate, applied to a gallery-specific expected type rather than a template-specific one.
- **Evaluate gallery recall separately from template recall** going forward — this document's central finding is that the current data cannot do this cleanly. A future eval round should deliberately tag a `gallery` vs. `template` vs. `other-inspiration` distinction at capture time, not just `inspiration`/`template`.

## Limitations

- **Only 68 gold queries were executed.** Everything in this document beyond the "Gallery-Oriented Query Candidates" list is grounded in that 68-query set; the wider candidate pool's gallery-oriented queries (see `ONTOLOGY_GAP_NOTES_2026-07-09.md`) have not been executed or measured at all.
- **Only 12 P0 cases have full competitor screenshot comparison.** Of the 17 cases discussed here, only the 7 named cases (which overlap with the 12-case sample) have direct visual/competitor confirmation; the other 10 gallery-signal-term matches are metadata-only (titles/types/tags), not independently visually verified.
- **`top_10_result_types` may not expose a distinct gallery type**, as established above — this is the central, structural limitation of this entire document, not a minor caveat. Every classification in the Issue Classification table that isn't `no_distinct_gallery_type_to_measure` is a best-effort proxy analysis built on top of that gap, not a direct measurement.
- **Gallery recall cannot be fully concluded from metadata alone.** The "format matched, subject didn't" pattern identified in Observed Patterns is a reasonable read of the available titles/types, but a full conclusion would require either exposing a true gallery-type field internally, or a dedicated manual pass opening live result grids specifically to judge gallery-style visual quality/relevance independent of the title text.

## Next Steps

- **Define a small gallery-specific eval set** — a deliberately curated set of 15-20 queries that are unambiguously gallery/moodboard/visual-reference in intent (distinct from template/poster/checklist-style structured-asset queries), to isolate this cohort for its own measurement round.
- **Run Curify search on inspiration / moodboard / visual reference queries** from that eval set, capturing not just `top_10_result_types` but the actual rendered screenshot for each, since the type field alone has been shown here to be an unreliable proxy.
- **Compare gallery vs. template vs. inspiration result mix** across that eval set to see whether the current `inspiration`/`template` split correlates with anything meaningful, or whether it needs to be replaced/supplemented with a genuine gallery-specific type.
- **Manually inspect screenshots** for that eval set the same way the 12-case P0 sample was inspected in this audit — direct pixel inspection, not metadata inference — before drawing any firm conclusion about whether gallery recall is a distinct problem or, as this document's provisional finding suggests, simply an instance of the same retrieval/decomposition/segmentation problems already being tracked.

No production code was touched in producing this document. No files were staged or committed. The final consolidated work report has not been written.
