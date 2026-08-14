# Revision Notes

This log records what was actually changed in this revision pass ("fact-accuracy calibration, content convergence, and final delivery packaging") relative to the prior version of these documents. It does not describe new research — the underlying source-code evidence and PR #416 content were re-checked for continued read access (`gh pr view 416` re-confirmed `state: MERGED`, same title, no reconciliation needed) but not re-derived from scratch.

## Formal repository delivery preparation

This seven-document research package was originally prepared and reviewed in a local working directory: `_local_research/zero-prompt-creative-workflow-exploration/` in the `super-inbox/curify-studio` repository. **Original local research location before formal delivery** — that path no longer applies once these documents live in the repository; it is recorded here purely as history, not as the current location of anything.

Once the package was reviewed and approved, it was:
- copied unchanged in substance into `docs/zero-prompt-creative-workflow-exploration-2026-08-03/` on a dedicated working branch (`baobao/zero-prompt-creative-workflow-exploration-2026-08-03`);
- updated only for local-only paths and status statements that would otherwise be stale or misleading in a formal repository context (e.g., "output location," README's "currently untracked / not committed" language, the Chinese executive summary's closing note) — these are the specific fixes logged in this section;
- left otherwise unchanged: the source-code-vs-runtime-verified distinction that runs through every document, the PR #416 factual findings (2 markdown files, 0 code, merged ≠ shipped), and every product/marketing conclusion (Goal-first as primary, Reference-first as supporting, Idea-first as fallback, P0's hand-curated directions and exclusion of field-level editing, Version A requiring implementation and runtime verification before external use, Version B as internal-only future vision) were preserved exactly as reviewed.
- Product code was not modified as part of this delivery step, and the original local research directory was left in place, untouched, as the user's local copy.

## Round 2 — small-scope wording fixes (this pass)

A follow-up pass focused on six specific, narrow wording problems identified after the first revision round. This was explicitly not a new research pass, did not change the core recommendation, and did not expand scope beyond the research directory.

- **Replaced the PR-proposed "Studio Quality" line with a safer recommendation.** In `ZERO_PROMPT_CREATIVE_WORKFLOW_EXPLORATION.md` §12, "Zero Prompts. Studio Quality." is now presented explicitly as a PR-proposed line kept only for the factual record, with a note that this document does not recommend it (it conflicts with the document's own guidance against unverifiable quality claims). Added two safer recommended alternatives — "No Prompt Engineering. A Clear Creative Direction." and "From a Simple Goal to a Clear Creative Direction." — and updated the lead-with-marketing recommendation to point at the safer options instead of the PR's original line. Confirmed no other file (`DEMO_STORYBOARD.md`, `README.md`, the Chinese executive summary) treats "Studio Quality" as a current recommendation — only `PR416_EVIDENCE_MAP.md`'s factual note that the PR proposed this phrase remains, unchanged and correctly labeled.
- **Changed "working generation backends" to source-level endpoint/implementation wording.** In the main document's Executive Summary, "two working generation backends" was rewritten to "two generation backend implementations present in the inspected source... their route handlers and request/response shapes were read directly, but no request was actually issued against them in this audit, so their runtime behavior was not verified." The Chinese executive summary's P0 flow step "使用现有生成能力生成" was changed to "接入当前源码中的生成路径，并在拍摄前完成运行验证" (connect to the generation path present in current source, and complete runtime verification before filming).
- **Changed Version A from "safe for external use" to an implementation-and-runtime-verified demo plan.** Renamed the storyboard section to "Version A — Honest P0 Demo Plan" in `DEMO_STORYBOARD.md`, the main document (§13), and `README.md`. Removed all "safe for near-term external use" / "safe to publish" framing and replaced it with an explicit statement that Version A is a production/demo plan, not a ready-to-publish asset, and becomes suitable for external use only after its adaptations are built, runtime-verified, and checked scene-by-scene against the final script. Added a new "Before Version A can be published externally" checklist to `DEMO_STORYBOARD.md`. Version B remains unchanged: internal-only, future-vision, never to be published as current capability.
- **Downgraded the local-main-behind conclusion to an unresolved likely explanation.** In `PR416_EVIDENCE_MAP.md` §0, "This means the local clone's `main` is behind `origin/main`" was rewritten to state only that the local checkout does not contain the two files, that a likely explanation is the local `main` being behind the merged PR, that this was not resolved because a fetch attempt timed out, and that other repository-history or checkout explanations were not ruled out. Also removed the sentence "The PR's merged state is immutable on GitHub" from the re-verification note, replacing it with a statement that re-confirming `state`/`title` this pass did not surface any reason to doubt the earlier reading. The PR's `MERGED` state, the 2-markdown/0-code file count, and the "merged ≠ shipped feature" distinction were all preserved unchanged.
- **Softened two absolute claims in `CURRENT_PRODUCT_FLOW_AUDIT.md`.** "This is the one surface where the user is asked to read and edit an actual prompt string" was changed to "This is the clearest prompt-editing surface identified in the inspected scope... among the surfaces this audit reviewed." "This confirms there is no real intent-classification model in this path" was changed to "The inspected routing implementation in this path uses a tag lookup and deterministic hash fallback, rather than semantic intent classification. This describes what was found in this specific file, not a claim that no semantic classification exists anywhere else in either repository."
- **Narrowed the creative-direction-recommendation principle to the primary Goal-first entry.** In the main document's Design Principles (§6), "Every entry point that currently returns a grid of results should be able to instead surface 2-4 named creative directions" was rewritten to scope this to the primary Goal-first entry specifically, with an added sentence that search and browsing should remain available as reference-discovery paths rather than being replaced across every surface.

### What was deliberately NOT changed in this round
- The core recommendation (Goal-first primary / Reference-first supporting / Idea-first fallback) is unchanged.
- The P0 scope (hand-curated directions, no field-level editing) is unchanged — Version A's demotion from "safe for external use" to "a plan requiring implementation and runtime verification" is a publication-readiness correction, not a scope change to what P0 contains.
- No new market research, code search, or PR re-analysis was performed; all six fixes are wording/framing corrections applied to conclusions already established in the prior round.

## Softened runtime claims

- Replaced "shipped," "working today," "live," "currently runs," "both still live," "already online," "in production," and similar phrasing throughout `ZERO_PROMPT_CREATIVE_WORKFLOW_EXPLORATION.md`, `CURRENT_PRODUCT_FLOW_AUDIT.md`, and `PR416_EVIDENCE_MAP.md` with source-code-level phrasing: "present in the current frontend source," "referenced in the homepage component composition," "present-in-source building block." Added an explicit statement at the top of each of the three documents that this audit did not independently verify deployed production behavior, feature flags, experiments, or runtime availability.
- The claim that `HomeImageWorkbench.tsx` is "a real, shipped, goal-first upload+workflow picker" was rewritten to describe it as present in source and referenced in the homepage composition, without asserting its current production status.

## Removed unsupported percentages

- Removed "70-80% of the way there" from the Executive Summary of the main document. Replaced with: "Several core building blocks already exist, while the unified workflow and creative-direction recommendation step remain unimplemented" (per the instruction's suggested phrasing), used at the Concept C description and the capability-gap framing.
- Searched for any other bare completion percentages; none other were found (the "8-cluster / 19-slug" and "1086 files" figures were kept, since these are direct counts of concrete, named things — cluster labels and files found in a recursive tree listing — not subjective completion estimates).

## Reframed the dual-entry issue

- Changed "The real misalignment isn't the tagline — it's an unresolved homepage architecture decision" to "One concrete manifestation of the broader positioning and workflow misalignment is the coexistence of two differently framed homepage entry surfaces in the current source composition," in both the Executive Summary and the final Recommendation section (§17) of the main document, and in `CURRENT_PRODUCT_FLOW_AUDIT.md` §2 and §8.
- Added explicit language that whether the two surfaces are actually both serving traffic today was not independently verified, that a code comment's "replaces" claim may be stale, and that merging/replacing/A-B-testing the two surfaces remains a product-owner decision, not something this audit resolves.

## Downgraded market-evidence strength

- Replaced "single largest and most commercially proven segment," "strongest demand," and similar phrasing with: "In the limited demand sample cited by PR #416, seller and SMB workflows showed a comparatively direct pain signal" — used in the Concept C description, §8 (Recommended Concept), and the Marketing Positioning section.
- Added explicit statements in the main document and the Chinese executive summary that the PR's Reddit research is a first-pass, non-exhaustive, English-language sample; that RedNote/Chinese-market research is not done; and that Goal-first is a working hypothesis based on limited evidence and reuse potential, not a data-validated market conclusion.

## Clarified Goal-first priority (no longer equal-weight concepts)

- Rewrote §7 ("Three Workflow Concepts") to label Concept C explicitly as "Primary/recommended path," Concept B as "Supporting path," and Concept A as "Fallback path" in their section headers, rather than presenting three parallel, symmetric options.
- Rewrote §9 (Detailed User Flow) as a single Primary/Supporting/Fallback flow diagram (matching the exact structure requested) rather than one combined "Concept C+B+A-fallback" flow presented as if it were one more option among equals.
- Updated the Comparison Matrix column headers to carry the Primary/Supporting/Fallback labels.

## Moved field-level editing out of the P0/MVP core

- Changed every instance describing field-level content editing as "the single biggest gap," "the most important missing capability," or "required for the zero-prompt MVP" to: "a valuable downstream workflow extension that addresses post-generation correction and reuse, but is not required to validate the initial zero-prompt entry and direction-selection hypothesis" (main document Design Principles §6, User Jobs table §5, Capability Gap Analysis §11, Risks §16, Recommendation §17).
- Restructured §14 (P0/P1/P2 Plan) into the four-tier structure requested: **P0** (unified demo story, Goal-first entry, hand-curated directions, existing generation, no field-level editing), **P1 Core** (real direction-recommendation service, catalog expansion, homepage-entry decision, failure/recovery), **P1 Extension** (field-level content editing — explicitly separated from P1 Core and P0), **P2** (long-term architecture). The prior version had bundled field-level editing into "P1" alongside the direction-recommendation service as if they were equally urgent; they are now explicitly separated.

## Revised marketing claims

- Replaced "Product photos that don't look like AliExpress" with "Clean, professional product photos for my online store" (removes a comparison that disparages a specific competitor platform).
- Replaced "Studio-quality, from the very first draft" with "A polished first draft, ready to refine" in the main document's Marketing Positioning section and throughout `DEMO_STORYBOARD.md`.
- Added an explicit checklist item in the main document (§12) against disparaging comparisons, unverifiable quality guarantees, and "one click does everything" overpromising — and applied the same standard when writing the Version A demo script.

## Demo capability status added

- Rewrote `DEMO_STORYBOARD.md` to tag every scene with a **Capability status** column: "Existing building block," "Existing building block, adapted," "P0 demo adaptation," "P0 demo adaptation, hand-curated," or "P1 Extension target" / "P1 Core target."
- Split the storyboard into **Version A — Honest P0 demo** (no dynamic direction-recommendation service, no field-level editing, safe for near-term external use) and **Version B — P1 target vision** (includes both not-yet-built capabilities, explicitly labeled as internal-only and not to be published as a demo of current capability). **Superseded note (see "Round 2" above):** the "safe for near-term external use" framing in this original Round-1 description was itself later found to be overstated and was corrected in Round 2 to "Version A — Honest P0 Demo Plan," suitable for external use only after implementation and runtime verification. This line is kept as a historical record of what Round 1 said, not as current guidance.

## Added Chinese executive summary

- New file `ZERO_PROMPT_CREATIVE_WORKFLOW_EXECUTIVE_SUMMARY_ZH.md`, structured per the requested 10-section outline, roughly 1-2 pages, written for a fast read by the boss and product team, using the same source-code-vs-runtime distinction and Primary/Supporting/Fallback framing as the English main document.

## Added README

- New file `README.md` describing the directory's purpose, a table of what each file is for, a recommended reading order, an explicit "what this is not" section, and a git-safety confirmation.

## What was deliberately NOT changed

- The core recommendation (Goal-first primary / Reference-first supporting / Idea-first fallback) is unchanged in substance — only its framing (equal-weight → clearly prioritized) and evidentiary caveats were revised.
- All `[Observed in code]` file-path and line-number citations were preserved; none were removed. Where a claim's confidence was downgraded, the underlying evidence citation was kept so the reader can still verify it.
- The finding that PR #416 is docs-only (2 markdown files, 0 code, merged) was preserved as-is — this was already accurately scoped in the prior version and did not need softening.
- The finding that `/ip-merch-demo`'s `MerchWorkflowBurst.tsx` is an explicitly client-side, no-backend, demo-only mock (per its own code comment) was preserved as-is — this is a direct quote of a code comment, not an inference that needed softening.
