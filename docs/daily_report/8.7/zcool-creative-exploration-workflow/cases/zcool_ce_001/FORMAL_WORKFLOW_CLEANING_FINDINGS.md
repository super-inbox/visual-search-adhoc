# Formal Workflow Cleaning Findings — Phase 6 (zcool_ce_001)

Scope: a formal, structured workflow-cleaning pass on the single Phase 5 `SELECT` candidate, `ZCE-CAND-001`, producing the first `zcool_ce_NNN`-style case record in this task's `cases/` directory. No new zcool pages were fetched, no new screenshots were taken, no images were downloaded, no `creative_explore` query was generated, and no change was made to `provenance/query_to_case_mapping.jsonl` or to the authoritative `curify-studio` `queries.jsonl`. Full per-field detail lives in `CASE_SUMMARY.md`, `QUALITY_REVIEW.md`, `workflow_extraction.json`, `evidence_manifest.csv`, and `source_metadata.json`; this document is the phase-level narrative summary, in the same style as `QUERY_DERIVATION_FINDINGS.md` (Phase 3) and `candidates/CREATIVE_EXPLORATION_CANDIDATE_FINDINGS.md` (Phase 5).

## 1. Phase goal

Following Phase 5's recommendation (`candidates/CREATIVE_EXPLORATION_CANDIDATE_FINDINGS.md` §12, §15) to clean exactly one candidate — the sole `SELECT`, `ZCE-CAND-001` — into a formal structured case, this phase re-reviewed the existing Phase 5 evidence (the full-page screenshot at `candidates/screenshots/ZCE-CAND-001_full_page.png` and the Phase 5 findings narrative/evidence index) and produced a case-level record compatible with the `baseline_pilot` design-workflow schema, without re-fetching the source page or performing new OCR/text extraction beyond what Phase 5 had already confirmed.

## 2. Why only one candidate was cleaned

Phase 5 screened 10 candidates and found exactly one `SELECT` (`ZCE-CAND-001`, 8/9) and zero `BACKUP`. Per the standing task rule (also honored in Phase 5, see `CREATIVE_EXPLORATION_CANDIDATE_FINDINGS.md` §4), the bar for what counts as a formally cleanable case is not loosened to manufacture a larger batch. The 4 `REJECT` candidates with a real brief but no workflow evidence (`ZCE-CAND-004`, `005`, `008`, `009`) remain eligible only for brief-derived queries, not for formal case cleaning — see §24 below.

## 3. Source and method

`source_url`: `https://www.zcool.com.cn/work/ZNjc0OTk2NDQ=.html`. `page_access_status=accessible` and `real_images_accessible=true`, both carried forward unchanged from Phase 5 (not re-verified by a new HTTP call this phase, since no new claim required it). The full-page screenshot (1440×14877px) was visually re-reviewed this phase at section-level granularity; fine body text was not re-transcribed from the image where it was already captured in Phase 5's evidence index, per `QUALITY_REVIEW.md` "Page access quality."

## 4. Case identity

`case_id=zcool_ce_001`, `source_candidate_id=ZCE-CAND-001`, `project_type=brand_upgrade_full_process`. This is the first and only entry in `cases/` as a formally cleaned record — distinct from the unrelated, earlier `cases/CASE_QUERY_ELIGIBILITY.csv` (a Phase 3 eligibility analysis of the 5 `baseline_pilot` cases, not a case record itself).

## 5. Brief

One confirmed paragraph under 一、项目背景 states the event has grown and the brand identity needed a visual upgrade (`ZCE-CAND-001-E001`, high confidence). No budget, timeline, or competitive-landscape text was found — this absence is recorded, not filled in.

## 6. Persona

Only the existence of a 用户画像 stage label is confirmed, sourced from the Phase 5 findings narrative rather than a dedicated Phase 5 evidence row. No descriptive persona content (demographics, behavior, etc.) was found in either phase. Recorded at `confidence=low`, `evidence_type=inferred` — a labeled-but-empty stage must not be promoted to `explicit`/`high` just because a heading exists.

## 7. Moodboard

A ~15-image collage under 情绪板, confirmed visual content category only (K-pop/fandom visual references: album covers, fan-support visuals, award-show KVs). No individual reference image is identified, and no page text ties any specific reference image to a specific downstream decision — `causal_link_evidenced=false` throughout.

## 8. Keywords

Result 活力/狂热/甜酷 is documented via the Phase 5 findings narrative (new evidence row this phase, `ZCE-CAND-001-E009`, medium confidence). The extraction method or reasoning behind arriving at these three words is not shown on the page and is recorded as unconfirmed.

## 9. Logo sketch exploration

8 black-and-white hand-drawn-style logo sketches in a 4×2 grid (`ZCE-CAND-001-E003`, high confidence). `observed_variant_count=8`. The page does not state that each sketch was a formally proposed direction — `formal_direction_count=unknown`, `selection_from_sketches=not evidenced`. This is the strongest single piece of exploration-breadth evidence in the entire case lineage to date (no `baseline_pilot` case has any sketch evidence at all).

## 10. Logo concept rationale

A paragraph under LOGO概念 explains the final mark's V + ring + heart + speech-bubble symbolism (`ZCE-CAND-001-E006`, high confidence, `rationale_scope=final_logo_concept`). This explains the finished logo's construction; it is not an individual rationale for any of the 8 sketches.

## 11. Two-version comparison

Two finished logo lockups, 版本一 and 版本二, shown side by side (`ZCE-CAND-001-E004`, `ZCE-CAND-001-E005`). Per new evidence row `ZCE-CAND-001-E011`, page text differentiates them by usage context (版本一 = default; 版本二 = for a dated campaign placement) — this is a usage note, not a selection rationale, and is not treated as one anywhere in this case's files.

## 12. Refinement

A visual progression from the 8-sketch grid → an exploded concept breakdown (heart/ring/bubble/V icons) → the final vector lockup is inferable from page presentation order (`ZCE-CAND-001-E007`). Recorded at `confidence=medium`, `order_confidence=low` — this is page order, not a stated iteration history, and must not be read as confirmed design history.

## 13. Applications

Section 3.4 落地效果 shows on-site event photography (booth, signage, crowd) and an embedded recap video (`ZCE-CAND-001-E008`, high confidence). 4 application entries recorded (`ZCE-APP-001`–`ZCE-APP-004`). These establish real-world deployment only; they establish nothing about which intermediate decisions led to them.

## 14. Selection — the central gap

`has_selection_reason=false`, unchanged from Phase 5. No statement anywhere on the page of why any one of the 8 sketches, or either of the two final logo versions, was chosen. `selection.selected_output=null`, `selection.selection_evidenced=false` at both the sketch stage and the two-version stage. This is the single most consequential missing piece in an otherwise unusually rich case — see §20 for why it caps how the case can be used.

## 15. KV and IP exploration — deliberately excluded

The Phase 5 findings narrative mentions "KV concept and execution" and "IP exploration reasoning" as part of why `ZCE-CAND-001` scored highly (`candidates/CREATIVE_EXPLORATION_CANDIDATE_FINDINGS.md` §5). Phase 6 could not independently confirm specific KV or IP content at the resolution available in the existing full-page screenshot, and no dedicated Phase 5 `evidence_id` exists for either. Rather than fabricate a `workflow_steps` entry from prose alone, both were excluded from `workflow_extraction.json.workflow_steps` and recorded only as open items in `missing_information` and in `quality_flags` (`kv_ip_exploration_excluded_due_to_insufficient_dedicated_evidence`). This is the most conservative available choice and is called out explicitly rather than silently — see §25.

## 16. Schema reuse

`workflow_extraction.json` reuses the exact `baseline_pilot/schema/design_workflow_schema_v0.1.json` enums for `stage_type`, `evidence_type`, `confidence`, `order_confidence`, `order_basis`, and `workflow_completeness` — no new enum values were invented anywhere in this case's files.

## 17. Schema deviations — documented, not silent

Two case-level constant deviations from the baseline schema: `language="zh-CN"` (baseline fixes `"zh"`) and `source_platform="ZCOOL"` (baseline fixes `"zcool"`), both required by this phase's explicit task instruction and recorded as known deviations in `QUALITY_REVIEW.md` §"Schema compatibility notes," not silently substituted. One enum-mapping decision: the keyword-extraction stage has no baseline `stage_type` value, so it was mapped to the closest existing value, `creative_direction`, with a note on the step itself (`ZCE-WF-004.notes` in `workflow_extraction.json`; mirrored in `outputs/creative_exploration_workflows.jsonl`).

## 18. Additive case-level fields

`workflow_extraction.json` adds case-level `brief` / `exploration_inputs` / `candidate_outputs` / `comparison` / `selection` / `refinement` / `applications` objects, since the baseline schema only carries per-step `selected_output`/`selection_reason` plus a flat `case_summary` string. These are additive, non-colliding top-level keys — no existing baseline field was renamed, overloaded, or removed, and `design_workflow_schema_v0.1.json` itself was not modified.

## 19. `outputs/creative_exploration_workflows.jsonl`

This phase populated the previously-empty `outputs/creative_exploration_workflows.jsonl` with exactly one line, structured to match `baseline_pilot/structured_cases/pilot_cases.jsonl`'s `{case, steps[], missing_stages[], assets[]}` shape (not `workflow_extraction.json`'s additive shape) so the two output styles stay distinguishable: `workflow_extraction.json` is the case's own detailed record with the additive sections from §18; `outputs/creative_exploration_workflows.jsonl` is the schema-conformant provenance record intended to sit alongside the `baseline_pilot` pilot cases. The 9 steps carry the same `step_id`s (`ZCE-WF-001`..`009`) as `workflow_extraction.json` for direct cross-reference — no second ID space was introduced. Its single `assets[]` entry represents the one shared full-page screenshot rather than 11 fabricated per-evidence asset rows, since only one screenshot file exists; per-section detail stays in `evidence_manifest.csv`.

## 20. `usable_for_workflow_training` — first `true` in this task's lineage

Every `baseline_pilot` case (`case_001`–`case_005`) is `usable_for_workflow_training=false`, because none has any multi-direction or comparison evidence at all. `zcool_ce_001` is the first case in this task's full lineage (5 baseline-pilot cases + 10 Phase 5 candidates) to earn `true`, because it has real sketch-exploration evidence (§9) and real side-by-side final-comparison evidence (§11) — genuine signal for exploration-breadth and comparison-visibility patterns. This must not be over-read: it does **not** mean the case is usable for selection-decision training, since §14 establishes that no selection evidence exists anywhere in it. `QUALITY_REVIEW.md`'s "Final recommendation" states this distinction explicitly, and `outputs/README.md`/`outputs/creative_exploration_workflows.jsonl`'s `case.schema_note` both repeat it, so a reader of any one file encounters the caveat.

## 21. Workflow completeness

`workflow_completeness=substantial`. Brief through final application are present with a mix of high/medium/low-confidence evidence, but the page's own "全流程" (full-process) framing in the title is not, by itself, grounds for `complete` — selection evidence, KV/IP detail, and full persona content are all missing. `complete` is reserved for cases with no such gaps; this case does not qualify.

## 22. Evidence traceability

All 9 `workflow_steps` in `workflow_extraction.json` reference at least one `evidence_id`; every `evidence_id` referenced there exists in `evidence_manifest.csv`, and every row in `evidence_manifest.csv` is referenced by at least one step — verified by direct set comparison, no orphaned or dangling references in either direction. `evidence_manifest.csv` carries 11 rows total: 9 carried forward unchanged from Phase 5's `CANDIDATE_EVIDENCE_INDEX.csv`, plus 2 new rows this phase (`ZCE-CAND-001-E009` keywords, `ZCE-CAND-001-E010` persona label — both sourced from the Phase 5 findings narrative, not from a new page visit) and 1 new row for the version-usage note (`ZCE-CAND-001-E011`).

## 23. Unsupported conclusions — explicit guardrails

Per `CASE_SUMMARY.md` §19, this case must not be described as: 8 formally proposed and compared creative directions; a documented client selection process; a complete closed-loop design-decision record; or a validated causal chain from moodboard to final logo. These guardrails exist because the case's visual richness (8 sketches, 2 compared finals, real applications) could otherwise tempt an over-read in exactly the way Phase 5 flagged for the negative sample `ZCE-CAND-010` (`candidates/CREATIVE_EXPLORATION_CANDIDATE_FINDINGS.md` §8) — richness of presentation is not evidence of a documented decision process, and this case, despite being the best in the lineage, still falls short of one at the selection step.

## 24. What this enables for the next phase

`zcool_ce_001` can now support a `workflow_derived` `creative_explore` candidate query (in addition to a `brief_derived` one) — the first case in this task's lineage where that distinction is real rather than moot, since Phase 3's 6 `AR-ZCE-xxx` queries were all `brief_derived` by necessity (see `CREATIVE_EXPLORATION_FINDINGS.md` §"Key finding carried forward"). No such query was generated this phase; doing so, and updating `provenance/query_to_case_mapping.jsonl` accordingly, would be new-phase work requiring the same schema-owner review path already established in Phase 3 (`README.md` "Open items still requiring schema owner (Jay) decision"). Separately, the 4 Phase 5 `REJECT` candidates with a real brief but no workflow evidence (`ZCE-CAND-004`, `005`, `008`, `009`) remain available for brief-derived-only queries, unchanged from Phase 5's own recommendation.

## 25. Open items requiring a human decision

1. **KV/IP exploration** (§15): whether to authorize revisiting `ZCE-CAND-001`'s page directly (a fresh page visit / higher-resolution crop, not a re-use of the existing screenshot) specifically to attempt confirming KV and IP content, versus leaving it permanently excluded from `workflow_steps` as currently recorded.
2. **Selection gap** (§14): whether the version-usage distinction (`ZCE-CAND-001-E011`) should ever be documented as a *soft proxy* for selection reasoning in any downstream query or training use, or whether it must remain strictly excluded from anything claiming to be selection evidence, as recorded now.
3. **Workflow-derived query authorship** (§24): whether to authorize drafting a `workflow_derived` `creative_explore` candidate query against `zcool_ce_001` next phase, and whether the 4 brief-derived-only `REJECT` candidates should be queried in the same pass.
4. **Schema deviations** (§17): whether the two documented constant deviations (`language`, `source_platform`) should eventually be reconciled by relaxing the baseline schema's `const` constraints (a `baseline_pilot` schema change, out of scope for this adhoc-repo case-cleaning task) rather than being carried forward as per-case documented exceptions indefinitely.
