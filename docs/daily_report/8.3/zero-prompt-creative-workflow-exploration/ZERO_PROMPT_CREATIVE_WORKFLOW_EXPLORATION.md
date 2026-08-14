# Curify 零提示词创意工作流探索

**Type:** Research + product/marketing exploration. **No product code was modified to produce this document.**
**Output location:** `docs/zero-prompt-creative-workflow-exploration-2026-08-03/`. This research was originally prepared and reviewed in a local working directory before formal repository delivery; see `REVISION_NOTES.md` for that history.
**Companion documents:** `ZERO_PROMPT_CREATIVE_WORKFLOW_EXECUTIVE_SUMMARY_ZH.md` (中文摘要), `PR416_EVIDENCE_MAP.md`, `CURRENT_PRODUCT_FLOW_AUDIT.md`, `DEMO_STORYBOARD.md` (same directory).

Label legend: **[Observed in code]** / **[Stated in PR]** / **[Inference]** / **[Recommendation]** — used throughout, consistent with the two evidence documents. A fifth qualifier is used where relevant: **source-code-level** (present in the repository's source and/or referenced in a page's component composition) vs. **runtime-verified** (independently confirmed to behave this way in a running deployment). This audit is **source-code-level only** — no running instance of `curify-frontend` was started, clicked through, or observed during this work. Nothing in this document should be read as confirming or denying what is currently live for real users, what feature flags gate, or what any A/B experiment currently serves.

---

## 1. Executive Summary

The boss's suspicion — that Curify's product and marketing may not match what users actually need — has real, source-level evidence behind it, though this audit cannot confirm or deny it at the level of "what real users experience in production today." Two homepage components exist side by side in the current frontend source and are both referenced in the homepage's component composition: `HomeOmniInput`, a free-text router, and `HomeImageWorkbench`, an upload-and-pick-a-workflow surface whose own code comment says it "replaces" the router. Whether both, one, or neither is actually rendered to real users right now was not independently verified — that would require runtime access this audit did not have. What the source code does show is that the product's own internal comments have not agreed on which surface is the front door, which is itself a useful signal about unresolved product direction, distinct from — and more modest than — a claim about what's "live."

PR #416 (merged, docs-only, contains no code) correctly diagnoses a directional problem but its two named interaction concepts — "Magic Drop" and "Visual Mad Libs" — were not found anywhere in the inspected frontend source. Several partial building blocks exist that are thematically related (a homepage upload/workflow picker, a client-side demo-only "doodle to merch burst" page, per-template structured parameter forms), but none of these should be read as the PR's proposal already having been built.

**Zero-prompt should not mean "zero input."** The recommended definition: the user always gives *something* — a goal, a rough idea, a reference image, or a few structured facts — but is never asked to translate that into AI-prompt vocabulary. The system does that translation. Based on the limited evidence available (source-code building blocks plus a first-pass, non-exhaustive demand sample cited in PR #416), the working recommendation is a **Goal-first primary path**, with a **reference/upload-first supporting path**, and an **open-ended idea path as a fallback** for goals outside a curated catalog. This is presented as a working hypothesis given current evidence and reuse potential — not a conclusion backed by measured user data, since no such measurement exists yet.

Several core building blocks relevant to this direction already exist in the inspected source: a structured per-template parameter form, a reference-image upload component, a shared 3-column generation workbench, an LLM-tagged intent taxonomy (used today for post-search refinement), and two generation backend implementations present in the inspected source (template-based and freeform-prompt-based) — their route handlers and request/response shapes were read directly, but no request was actually issued against them in this audit, so their runtime behavior was not verified. What is clearly absent from the inspected source is a pre-generation "recommend 2-3 creative directions" step, and a way to edit the content of an already-generated result without re-running generation. The next recommended step is to validate the goal-first entry and direction-selection idea with a small, honestly-scoped demo — built and runtime-verified before any external use — before committing to a broader build — see §14.

## 2. Background and Problem

**[Stated by user/boss, background section]** Prior external positioning: "Images for every query." Suspected misalignment: users don't want to learn prompting; they have vague ideas, not visual vocabulary; they want designer-level output from simple input; they want to start from a reference image, not a blank box; they want the product to help them understand their own need, not just return search results.

**[Observed in code]** This concern has source-level corroboration, though not runtime confirmation: (1) two homepage components with conflicting code comments about which is the intended front door (§4 and `CURRENT_PRODUCT_FLOW_AUDIT.md` §2), (2) `search/page.tsx`, a roughly 1,300-line keyword relevance-scoring engine, which is a literal source-level embodiment of "images for every query," and (3) a pre-existing internal doc in this repo, `docs/reproduction-surface-review-2026-06-21.md`, independently flagging inconsistent CTA verbs across the funnel ("Make your own" vs. "copy the text") — written months before this task or PR #416, so it is not a finding manufactured for this exercise.

## 3. Evidence from PR #416

Full detail in `PR416_EVIDENCE_MAP.md`. Summary: PR #416 is a **merged, docs-only** proposal (2 new markdown files, 0 code files) authored by Jay Wang, grounded in a first-pass, limited Reddit demand-mining exercise that the PR itself describes as incomplete (Chinese-market/RedNote data explicitly deferred). Its central, source-verifiable claim — that the shared `ReproduceWorkbench` component is a `Source → Prompt → Production` 3-column layout — matches what is present in the actual frontend repository source (`curify-frontend:app/[locale]/_components/ReproduceWorkbench.tsx`). Its two named interaction concepts, "Magic Drop" and "Visual Mad Libs," were **not found** in the inspected frontend source scope; the closest thematically-related artifacts present in source are `HomeImageWorkbench.tsx` (a goal-first upload+workflow picker referenced in the homepage composition) and `/ip-merch-demo`'s `MerchWorkflowBurst.tsx` (an explicitly client-side, no-backend, pitch/demo-only mock of a doodle→merch-burst moment, per its own code comment). Neither of these should be treated as equivalent to the PR's full proposal — they are partial, related building blocks, not the same thing under a different name.

## 4. Current Product Flow

Full detail in `CURRENT_PRODUCT_FLOW_AUDIT.md`, which is a **source-code and repository-composition audit**, not a runtime/production verification. Key structural facts:
- Frontend lives in a separate repository (`super-inbox/curify-frontend`), not in this one — confirmed via a hardcoded cross-repo URL in this repo's backend (`curify_background/app/routers/nano_templates.py:29`).
- Search, templates, gallery-remix, and generation share one data corpus and are connected through source-level routing (`/search` → `/nano-template/[slug]#reproduce` → `ReproduceWorkbench` → `/nano-templates/generate` or `/nano-freeform/generate`).
- An LLM-tagged 8-cluster intent taxonomy is present in source (`lib/intent_clusters.ts`, `lib/intent_taxonomy.ts`) but, per its own code comments, is applied as **post-search refinement chips**, not as a pre-generation direction recommendation.
- The clearest current "the user is asked to read/edit a raw prompt" surface is the gallery remix flow (`/nano-banana-pro-prompts/[id]` → `/nano-freeform/generate`, a free-text editable `prompt` field).
- A code-comment-confirmed gap: parametric/content-level re-edit of a finished result is explicitly described in a code comment as deferred to "a later phase" (`ReproduceWorkbench.tsx:54-56`) — this is a real finding, but see §6 below on why it is not treated as the central blocker for a zero-prompt MVP.

## 5. User Jobs and Pain Points

Per the task's requirement not to collapse everything into "users can't write prompts," these are separated into distinct jobs, each with functional job / emotional job / current friction / desired outcome. All entries below are **[Inference]** grounded in the boss's brief, the limited Reddit citations in PR #416's appendix, and the source-code audit — not newly invented personas, and not claims backed by first-party Curify user research.

| Job | Functional job | Emotional job | Current friction (source-grounded where applicable) | Desired outcome |
|---|---|---|---|---|
| **Vague idea, no visual direction** ("I want to open a tea brand, don't know what it should look like") | Turn a one-line idea into a concrete visual direction | Feel like someone competent is helping, not judged for not knowing design terms | `HomeOmniInput` free text routes only to `/search?q=`; no direction-recommendation step was found in source, before or after search | 2-3 distinct, named creative directions to choose from before any generation |
| **Knows the goal, lacks visual vocabulary** ("I want a poster, but I don't know how to say 'minimalist warm palette'") | Convert a plain-language goal into the right template + params | Avoid feeling stupid for not knowing prompt jargon | Prompt is demoted to a collapsible "Advanced" panel (`ReproduceWorkbench.tsx:482-498`) but is present in the DOM and opened by default in upload mode | Never see the word "prompt"; fill in facts, not vocabulary |
| **Has a reference image, wants to reproduce structure/style** | Extract structure/style/use-case from an uploaded image automatically | Feel like the system "gets" their taste without them explaining it | `ReferenceImageUpload` is present and wired into `ReproduceWorkbench`, but no automatic style/structure extraction from an arbitrary (non-catalog) image was found in source — the user still manually picks template + params | Drop an image, get options inferred from it, not a blank param form |
| **Wants several professional directions to choose from, not one output** | See distinct options before committing generation credits | Feel in control of taste, not stuck with the first (possibly wrong) result | Today's generation path is 1 template/params → 1 result; no "present 3 directions" step was found anywhere in the inspected source | 3 named directions generated cheaply/fast, pick one, then commit to full generation |
| **Wants to change content (name, date, price) on a result later, not re-prompt** | Edit specific fields on an already-generated asset | Avoid the frustration of "starting over" for a minor correction | A code comment explicitly defers parametric regeneration on a loaded result to "a later phase" (`ReproduceWorkbench.tsx:54-56`) — a real, source-confirmed gap, but treated in this document as a valuable downstream extension rather than a blocker for the initial zero-prompt hypothesis (see §6, §14) | Eventually, correct a field on a finished asset without touching a prompt or a template |
| **Wants a fast, professional deliverable for a specific format** (poster, e-commerce image, brand kit, education content, social post) | Get a finished, on-brand asset (often a *set*, e.g. logo+packaging+social) for a known deliverable type | Feel like they got agency/designer-quality output on a shoestring budget/timeline | `template_packs.py`, `etsy_packs.py` back packaged downloads exist in source, but no single "tell us your deliverable type, get a matched pack" front-end flow was found | Pick "I need a brand kit" / "I need a product listing," answer a few fields, get the full set |

## 6. Design Principles

**[Recommendation]**, derived from the evidence above:
1. **Zero-prompt ≠ zero-input.** The user always gives *something* — an idea, an image, a goal, or a few facts. The system never asks them to phrase that as an AI instruction.
2. **Show directions, not a wall of images, at the primary entry.** The primary Goal-first entry should surface 2-4 named creative directions instead of defaulting immediately to a large result grid — this is the single biggest thing to validate first (§14). Search and browsing should remain available as reference-discovery paths, rather than being replaced across every surface: this principle scopes the direction-recommendation experience to the Goal-first entry point, not to every existing search or browse page.
3. **Reuse what already exists in source before building new services.** The intent taxonomy, template registry, and `ReproduceWorkbench` engine are real, present building blocks — the priority is sequencing and front-loading them, not rebuilding them.
4. **Editing without re-prompting is valuable, but it is a downstream extension, not the entry hypothesis.** Content-level edits (change a name, a date, a price) matter for retention and satisfaction once a user has a result — but validating whether goal-first entry + direction selection removes the "prompt fear" does not depend on this capability existing yet. It belongs in P1 Extension, not the P0 story (§14).
5. **Never present a demo capability as a shipped product capability.** The `/ip-merch-demo` page's own code comment — "this is a DEMO surface... not exported print files" — is the right internal discipline and should be the standing bar for any external claim, marketing or otherwise.

## 7. Three Workflow Concepts

These three concepts are **not equal-weight alternatives** — §8 sets a clear primary/supporting/fallback ordering. They are described symmetrically below only to make the comparison auditable.

### Concept A — Idea-first (Fallback path)
`Open-ended brief → intent identification → route into the same structured workflow used by Goal-first`

- **Entry:** a single free-text input, similar in spirit to today's `HomeOmniInput`, but with a different destination.
- **Input:** free text describing a goal ("opening poster for my coffee shop").
- **System infers:** deliverable type and likely template family — repurposing the existing intent taxonomy (`intent_clusters.ts`), which today only runs after a search, not before generation.
- **Reuse:** intent taxonomy (present in source), template registry (present in source), generation backends (present in source). Not present in source: a service that maps an open brief directly to a small set of template/style candidates before any search or browse step.
- **Role in this recommendation:** the entry path for goals that don't fit a curated deliverable catalog — a fallback, not the headline experience.
- **Risk:** producing confident, good-quality direction candidates from an unconstrained brief with no reference material is the hardest open-ended problem of the three concepts, and is unproven at any evidence level available to this audit.
- **Long-term role:** the most general, most extensible entry pattern if it can be made reliable — but not the right first bet given its risk profile.

### Concept B — Reference-first (Supporting path)
`Search or select a reference image → "Make your own" → enter the same structured workflow used by Goal-first`

- **Entry:** search results, gallery, or template/example detail — today's most-used browsing surfaces.
- **Input:** a chosen reference image (existing "Make your own" CTA, `remixThis` per `docs/reproduction-surface-review-2026-06-21.md`).
- **System infers:** a template match for **catalog** images (present in source — search already links to the matching `/nano-template/[slug]`); auto-extraction of style/structure from an **arbitrary, non-catalog** upload was not found in source.
- **Reuse:** high for catalog-anchored images — `ReproduceWorkbench`, `ReferenceImageUpload`, template matching, and `/nano-templates/generate` already cover most of this case in source. The gap is generalizing to arbitrary uploads.
- **Role in this recommendation:** the natural on-ramp for users who already have an image in hand — feeds into the same confirm-info-then-generate workflow as Goal-first, rather than being a separate product.
- **Risk:** lowest of the three, since it builds most directly on present infrastructure.

### Concept C — Goal-first (Primary/recommended path)
`Choose what to create → provide a few required facts → receive 2-3 creative directions → select one → generate`

- **Entry:** "What do you need?" — a deliverable-type picker (poster / listing image / sticker pack / brand kit / social post / education content).
- **Input:** deliverable type + a handful of structured fields (name, date, selling point, etc.) — the same shape `HomeImageWorkbench`'s `WORKFLOWS` array and the `TemplateParameter` form already use in source.
- **System infers:** the template and its base prompt; a direction-recommendation step (2-3 style variants) is the one genuinely new piece needed to complete this path.
- **Reuse:** highest of the three in source terms — `HomeImageWorkbench.tsx` (workflow picker → `requires_image_upload` template → `ReproduceWorkbench`) is a close, present-in-source analog of this pattern, referenced in the homepage composition. Several core building blocks already exist, while the unified workflow and the creative-direction-recommendation step remain unimplemented.
- **Role in this recommendation:** the primary entry — see §8 for why.
- **Risk:** a fixed deliverable catalog doesn't scale gracefully to open-ended goals on its own — this is exactly why Concept A exists as a fallback, not a competitor.

### Comparison Matrix

| | A: Idea-first (Fallback) | B: Reference-first (Supporting) | C: Goal-first (Primary) |
|---|---|---|---|
| Entry point | Free-text brief | Search/gallery reference image | Deliverable-type picker |
| System infers | Direction + template | Style/structure from image | Template + prompt |
| Reuse of present source building blocks | Medium (taxonomy present, pre-generation sequencing absent) | High (upload + workbench + catalog template matching present) | Highest (`HomeImageWorkbench` is a close present-in-source analog) |
| Direction-recommendation step | Not present in source, hardest to build reliably | Not applicable directly (relies on Goal-first's flow once a match is found) | Not present in source, but narrowest scope to build first |
| Role | Fallback for goals outside the catalog | Supporting on-ramp into the same workflow | Primary hypothesis to validate first |

## 8. Recommended Concept

**Recommendation: Concept C (Goal-first) as the primary path, Concept B (Reference-first) as a supporting on-ramp into the same structured workflow, and Concept A (Idea-first / open brief) as the fallback for goals outside the curated deliverable catalog.**

**Why, stated as a working hypothesis based on limited evidence — not a settled conclusion:**
- `HomeImageWorkbench.tsx` is a building block present in source, referenced in the homepage composition, that already follows this same shape (pick a workflow → upload/confirm → generate). This means a Goal-first P0 demo is mostly a packaging and scoping exercise on top of present infrastructure, rather than a new capability.
- In the **limited demand sample cited by PR #416** — a first-pass, English-language, Reddit-only search, explicitly not covering Chinese-market/RedNote data — seller and SMB workflows showed a comparatively direct pain signal ("done-for-me," "can't afford a designer," "want a matched set"). This is a useful directional signal, not a market-sizing conclusion, and it happens to map naturally onto "pick a deliverable, get a set" (Concept C) rather than open-ended idea exploration.
- Concept A is closest to the PR's proposal in spirit, but has the least proven reliability path and the highest technical risk of the three — appropriate as a longer-term fallback, not the first validation step.
- Concept B is already substantially supported in source for catalog-anchored images; its main gap (arbitrary-upload auto-extraction) is a reasonable **P1** extension of Concept C's flow rather than a separate product line.

Goal-first is treated here as **the working hypothesis to validate first**, given current evidence and reuse potential — not as a proven-correct strategy. §14 lays out a deliberately small first step to test this hypothesis before committing further investment.

## 9. Detailed User Flow (Recommended Concept)

```
Primary:
  Choose what to create (deliverable-type picker)
   → provide a few required facts (name, date, selling point, etc.)
   → receive 2-3 creative directions
       (P0: hand-curated per scenario; P1: a real recommendation step — see §14)
   → select one
   → generate (present in source: /nano-templates/generate)
   → result (present in source: result-mode ReproduceWorkbench — download +
     designer-pack transforms)
   → export

Supporting:
  Upload or select a reference image
   → enter the same structured workflow above (facts → directions → generate)

Fallback:
  Describe an open-ended idea
   → system identifies the likely deliverable type/direction
   → route into the same structured workflow above
```

## 10. Screen-Level Interaction

| Screen | Purpose | User sees | User inputs | System infers | Primary CTA | Secondary CTA | Loading state | Insufficient-info state | Zero-result state | Generation-failure state | Return-to-edit path |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Entry | Establish the goal without a blank prompt box | Deliverable-type tiles + "or drop an image" + "or just tell us" text field | Tap a tile, drop an image, or type a brief | Nothing yet | "Continue" | "I'm not sure" → open-ended brief path | n/a | n/a (tiles always available) | n/a | n/a | n/a |
| Direction | Show the system understood the goal | 2-3 named style directions with a preview thumbnail each | Pick one direction | Template family, style variant | "Use this direction" | "Show me something different" (reroll, where supported) | Skeleton cards while directions load | If the brief is too vague, ask 1-2 clarifying questions rather than failing silently | If nothing matches, show example briefs instead of a dead end | n/a | Back arrow to Entry, brief preserved |
| Confirm info | Collect the minimum facts needed, nothing more | A short form: 1-4 fields depending on deliverable type (reuse: `TemplateParameter`) | Name, date, selling point, etc. | Field defaults from placeholders (reuse: existing fallback logic referenced in `nano_templates.py:138-164`) | "Generate" | "Edit direction" (back to previous screen) | n/a | Disable Generate + inline field-level error until required fields filled (reuse: existing missing-param validation) | n/a | n/a | Back to Direction screen without losing typed field values |
| Generating | Manage wait time honestly | Progress animation | none | none | n/a | "Cancel" | Reuse existing async poll pattern (`project_id` + status poll) | n/a | n/a | Clear retry CTA on backend failure, not a silent hang | n/a |
| Result | Deliver the payoff | Finished asset, plus a designer-pack row (resize/print-ready — reuse existing) | Tap a designer-pack tile (reuse); field-level edit is a later extension, not assumed here | none | "Export" | "Try another direction" (back to Direction screen, same brief) | n/a | n/a | n/a | Explicit failure state with "Try again," never a dead end | N/A in this scope — see P1 Extension in §14 |
| Export | Close the loop | The finished set (primary asset + any designer-pack derivatives already made) | Tap "Download all" or pick individual files | none | "Download all" | Individual per-file download (reuse existing pattern) | n/a | n/a | n/a | n/a | Back to Result |

**What's hidden vs. confirmed:** the base prompt, template ID, and AI-specific vocabulary are intended to stay server-side and not shown by default anywhere in this flow — a stricter posture than today's `ReproduceWorkbench`, which still surfaces a "Prompt preview" disclosure. Only business facts (name, date, price, selling point) are asked of the user directly.

## 11. Capability Gap Analysis

| Capability | Current product (source-level) | PR #416 | Reusable now | Needs adaptation | Needs new development | Evidence |
|---|---|---|---|---|---|---|
| Simple brief input | Partial — `HomeOmniInput` (text only, routes to search) | Proposed as primary entry | Yes, as the fallback path | Route to Direction screen instead of `/search` | — | `HomeOmniInput.tsx:70-77` |
| Intent classification | Partial — tag-based tool routing (`promptToolMatch.ts`), not semantic | Implied by "Intent → Creative Direction" | Tag map as a coarse fallback | — | Real semantic classification for open-ended briefs | `promptToolMatch.ts:29-45` |
| Use-case recognition | Present — 8-cluster/19-slug intent taxonomy, LLM-tagged | Not named specifically, but same concept | Yes, taxonomy + tagging pipeline | Move from post-search refinement to pre-generation step | — | `intent_clusters.ts:1-42` |
| Search inspiration | Present — full relevance-scoring engine | Deprioritized as headline UX (not proposed for removal) | Yes, as one of several entry paths | Reframe as "browse," not the default front door | — | `search/page.tsx` |
| Recommend creative direction | Not found in the inspected source scope | Named as core to the proposal | — | Template registry + preview assets are the raw material | A direction-generation step (brief/goal → 2-3 templates/styles) + UI | Not found anywhere in the inspected `curify-frontend` file tree |
| Reference image selection | Present within the catalog (search/gallery → "Make your own") | Implied by "Magic Drop" | Yes for catalog images | — | Auto-extraction for arbitrary/non-catalog uploads | `ReferenceImageUpload.tsx`, `ReproduceWorkbench.tsx:365-413` |
| Template selection | Present — manual, via search/browse | Should become automatic | Yes as the underlying matcher | Trigger automatically from brief/image instead of manual browse | — | `nano_templates.py`, template registry |
| Auto-fill prompt | Present — `fillPrompt` param substitution | Core requirement ("no prompt shown") | Yes, mechanism reusable | Keep prompt server-side always, never open the disclosure by default | — | `ReproduceWorkbench.tsx:221,480-498` |
| Structured info form | Present — `TemplateParameter` | Implied ("Visual Mad Libs" is a related, more elaborate idea) | Yes | — | Optional: richer chip-based multi-field UI | `ReproduceWorkbench.tsx:420-464` |
| "Make your own" (reference→generate) | Present | Central to the proposal | Yes | Rename/reposition CTA consistently (an internal doc already flags this inconsistency) | — | `docs/reproduction-surface-review-2026-06-21.md:61-77` |
| Generation | Present — 2 backends (template + freeform) | Assumed as-is | Yes | — | — | `nano_templates.py:105`, `nano_freeform.py:72` |
| Editing (content-level) | Not found in the inspected source scope; a code comment explicitly defers this ("a later phase") | Not explicitly addressed by the PR either | Designer-pack tiles reusable for whole-image transforms | — | Field-level re-edit of a finished result — a valuable P1 Extension, not a P0 requirement | `ReproduceWorkbench.tsx:54-56` |
| Export | Present — plain download links + resize/print-ready bundle | Implied ("成套产出") | Yes | Bundle into one "download all" action | — | `ReproduceWorkbench.tsx:642-682`, `resize_bundle` lib |
| History | Present — `/workspace` generated/saved tabs | Not addressed | Yes | — | — | `WorkspaceClientPage.tsx:20` |
| Failure recovery | Partial — duplicate-image warning, insufficient-credits modal present; no generic "generation failed, retry" pattern confirmed across all paths | Not addressed | Partial | Add a consistent failure state across all generate calls | — | `ReproduceWorkbench.tsx:500-511` (duplicate warning), credits modal (`setModal("topup")`) |

## 12. Marketing Positioning

### One-line positioning (3 directions)

**PR-proposed line (kept for the record, not carried forward as a recommendation):**
> "Zero Prompts. Studio Quality." — *(PR #416's own proposed line, `docs/zero-prompt-creative-workflow-proposal-2026-07-31.md` §4.1)*. This document does not recommend using it as-is: "Studio Quality" is exactly the kind of unverifiable absolute quality claim §12's own marketing guidance warns against (see the "polished first draft, ready to refine" framing used elsewhere in this section and in `DEMO_STORYBOARD.md`). It is preserved here only as a factual record of what the PR proposed, not as a supporting line for current use.

**Recommended directions instead:**

1. **"No Prompt Engineering. A Clear Creative Direction."** — **[Recommendation]** keeps the PR's "no prompt" contrast without the unverifiable quality claim; best for creator/DIY audiences already frustrated with prompt-heavy tools.
2. **"Tell us what you need. We'll figure out how it should look."** — leans into the "system understands your idea" emotional job (§5); best for SMB/seller audiences who want to feel understood, not just served a tool.
3. **"From a Simple Goal to a Clear Creative Direction."** — leans into the "asset set, not one image" differentiator; pairs with Concept C messaging without asserting a quality level that hasn't been validated.

**[Recommendation]:** lead external marketing with #2 or #3 for the SMB/seller audience — noting again that the underlying demand signal is a **limited, first-pass sample**, not a validated market conclusion — and use #1 as a supporting line inside the product/UI itself. Do not use the PR's original "Studio Quality" phrasing as a current recommendation.

### Homepage

- **Headlines (3):**
  1. "Turn your idea into a finished design — no prompt required."
  2. "Tell us what you need. We'll show you the directions."
  3. "From a rough idea to a full, professional set."
- **Subheadlines (3):**
  1. "Pick a direction, fill in the details, done. No prompt engineering, no design degree."
  2. "Curify understands your goal and does the design thinking — you just choose."
  3. "One idea in. Poster, social post, and print-ready files out."
- **Primary CTA:** "Show me my directions" (replaces a generic "Generate" or "Search")
- **Secondary CTA:** "Start from a photo" (routes into the reference/upload path)
- **Input placeholder:** "What do you need? e.g. 'opening poster for my coffee shop'"
- **Example prompts/needs (3):** "Opening poster for my coffee shop" · "Clean, professional product photos for my online store" · "Logo + packaging for my new tea brand"

Marketing copy is written to describe **user outcomes**, not technical capability, and avoids: comparisons that disparage other platforms or products, quality guarantees that cannot be verified, and "one click does everything" framing that overstates automation. "Studio-quality, from the very first draft" is avoided as an unverifiable absolute claim; a more accurate framing is **"a polished first draft, ready to refine."**

## 13. Demo Storyboard Summary

Full storyboard in `DEMO_STORYBOARD.md`, now presented in two explicit versions: **Version A — Honest P0 Demo Plan**, which describes a demo built only from present building blocks plus a small number of hand-curated directions, with no field-level editing claimed; and **Version B — P1 Target Vision**, which includes the not-yet-built direction-recommendation step and field-level editing, clearly labeled as a future-state concept reel rather than a demo of current capability. Version A is a production plan, not a ready-to-publish asset — it becomes suitable for external use only once its adaptations are actually built, runtime-verified, and checked scene-by-scene against the final script. Version B should be reserved for internal alignment/pitch use only, always clearly labeled as a future concept, and never published as a demo of current capability.

## 14. P0 / P1 / P2 Plan

### P0 — Fast Demo
**Scope:** A single, unified demo user story (coffee-shop poster, or the PR's IP-merch scenario) built around: a Goal-first entry screen, 2-3 hand-curated or pre-computed creative directions (not a general recommendation service), a short structured-info form, and generation via the present `ReproduceWorkbench`/`/nano-templates/generate` path. Field-level editing is explicitly **out of scope** for P0.
**Dependencies:** none beyond present surfaces + one new screen for direction selection.
**Modules likely touched:** a new "Directions" screen (frontend only); no backend changes required if directions are pre-computed for the specific demo scenario.
**Risks:** the demo may look scripted/narrow if directions aren't at least somewhat scenario-flexible; internal framing must be explicit that this is a demo build, not a general-purpose recommendation engine, to avoid the demo being mistaken for a shipped capability.
**Validation:** can a non-technical viewer watch the demo and correctly explain what Curify does, without either party using the word "prompt"?

### P1 Core — Product MVP
**Scope:** A real, general direction-recommendation step (mapping a brief or catalog match to 2-4 template/style variants) wired into an actual entry surface; an expanded deliverable catalog beyond `HomeImageWorkbench`'s current 4 workflows; a decision and follow-through on how the two present homepage surfaces should relate to each other (merge, replace, or A/B — a product decision, not an engineering default); and a consistent generation-failure/retry experience across all generate calls.
**Dependencies:** P0 learnings on which directions/scenarios resonate.
**Modules likely touched:** `curify-frontend` (new Directions screen, expanded workflow catalog, consistent failure states); possibly a new lightweight service for direction generation.
**Risks:** direction-recommendation quality across a wide range of real user briefs (not just the demo scenario) is unproven; the homepage entry-surface decision requires explicit product ownership, not just a merge.
**Validation:** real (not scripted) users complete brief → generated result without needing to view or edit a raw prompt, at a completion rate meaningfully better than today's search-and-browse baseline.

### P1 Extension — Post-generation editing
**Scope:** Field-level content editing of an already-generated result (change a name, date, or price without re-prompting or fully regenerating). This is a valuable downstream workflow extension addressing post-generation correction and reuse — but it is **not required** to validate the initial Goal-first entry and direction-selection hypothesis, and should not block or be conflated with the P0/P1 Core timeline.
**Dependencies:** requires the saved-project data model to retain template/params against a finished result, which a code comment indicates is not currently the case (`ReproduceWorkbench.tsx:54-56`) — this is backend schema work, not just a UI addition.
**Modules likely touched:** `curify_background` (project schema + a param-only re-generation endpoint), `curify-frontend` (edit UI on result screens).
**Risks:** scope and cost of this work were not estimated here; treat as a distinct, laterworkstream from the P0/P1 Core validation.
**Validation:** users who reach a result can correct at least one common field type (e.g., a date) without re-authoring anything prompt-like.

### P2 — Long-term Architecture
**Scope:** generalize direction recommendation across arbitrary use cases beyond a curated catalog (this is Concept A's long-term role); real image-understanding for arbitrary (non-catalog) reference uploads (fully realizing Concept B); personalization/learning from `/workspace` history to bias future recommendations; resolve the two-homepage-surface question at an architectural level if P1's tactical decision needs revisiting at scale.
**Dependencies:** P1 Core's direction-recommendation step must be live and instrumented; sufficient usage volume to justify personalization work.
**Modules likely touched:** broad — taxonomy/tagging pipeline, a recommendation service, `/workspace` data model, possibly a redesigned home-page information architecture.
**Risks:** scope creep; personalization needs meaningful usage volume to avoid cold-start problems.
**Validation:** returning users get progressively more relevant direction recommendations; new use cases can be added without a fully manual catalog entry for each one.

**No engineering time estimates (hours/days/sprints) are given anywhere above, since none can currently be supported with evidence.**

## 15. Metrics

| Metric | Validates |
|---|---|
| Time to first meaningful result (brief → first generated asset) | Whether the flow is actually faster than today's search-and-browse path |
| Continuation rate after homepage input | Whether a Goal-first entry reduces drop-off relative to a blank/ambiguous entry |
| Search-results → "Make your own" click-through | Baseline for how well today's funnel already converts, to compare against a new entry |
| Direction-selection rate (of users shown directions, share who pick one vs. abandon) | Whether "recommend directions" genuinely beats a blank prompt box |
| Generation-start rate | Whether the confirm-info step is short enough not to lose users |
| Generation-completion rate | Backend/pipeline reliability, independent of UX |
| Blank-input-box abandonment rate | Whether removing/demoting a blank prompt box reduces the "blank page fear" the boss described |
| Manual prompt-edit rate (users who open "Advanced prompt editing," where still present) | Whether hiding the prompt by default is sufficient, or power users still need/want it |
| Post-generation edit request rate (qualitative or proxy signal, since the capability doesn't yet exist) | Whether investing in the P1 Extension (field-level editing) is worth prioritizing sooner |
| Export rate | Whether the flow reliably reaches a usable deliverable, not just a preview |
| D1/D7 return rate | Whether the "asset set" framing drives repeat use for ongoing brand/content needs |

## 16. Risks and Open Questions

- **Two homepage entry surfaces are both present in source with conflicting code comments about intent** — this needs an explicit product decision (merge, replace, or A/B) before any new Goal-first entry point is added, or it becomes a third uncoordinated surface. Whether this reflects the single root cause of the boss's broader misalignment concern was not established by this audit — it is one concrete, code-observable manifestation of it.
- **Direction-recommendation quality is unproven** at any evidence level available to this audit — the central open technical risk across all three concepts.
- **"Don't look AI/fake" counter-signal** (noted in PR #416's limited demand sample) — marketing or demo framing emphasizing speed/quantity risks the distrust signal that sample surfaced; framing should stay on quality/authenticity, not volume — while remembering the sample itself is limited and not a full market read.
- **Field-level content editing is a real, source-confirmed gap**, but this document deliberately treats it as a P1 Extension, not a P0 blocker — see §6 and §14 for the reasoning.
- **Open question:** should the two existing homepage surfaces be merged, replaced, or run as an A/B — this task did not have product/analytics ownership or runtime access to decide, and it is flagged as a decision for the team.
- **Open question:** the PR's references to "existing dev/jayw video pipelines" were only partially cross-checked in the available time — worth a follow-up check before committing marketing video production plans to them.
- **Open question:** none of the demand evidence cited here (PR #416's Reddit sample) has been validated against Curify's own user base — first-party validation (e.g., a small user test of the P0 demo) is a natural next step before P1 investment.

## 17. Recommendation to the Team

1. **One concrete manifestation of the broader positioning and workflow misalignment is the coexistence of two differently framed homepage entry surfaces in the current source composition.** This is evidence of an unresolved decision, not proof of the single root cause — the team should treat it as one important signal among several, and decide explicitly whether to merge, replace, or A/B test the two surfaces.
2. **Zero-prompt should be defined as: the user always gives something (idea / image / goal / facts), but never writes or sees AI vocabulary.** That is a testable, buildable definition — not "no input at all."
3. **The recommended path is Concept C (Goal-first) as primary, Concept B (Reference-first) as a supporting on-ramp, and Concept A (open brief) as a fallback** — a working hypothesis based on current source-level reuse potential and a limited demand sample, not a data-validated conclusion.
4. **This direction fits Curify's current capability because several core building blocks — a template registry, structured params, a generation backend, an intent taxonomy — are already present in source.** The main gap is sequencing (recommend before generate, not just search-then-refine); field-level editing is a valuable but separate, later extension.
5. **The fastest thing to validate is a small, honestly-scoped P0 demo** (coffee-shop poster or IP-merch scenario) using hand-curated directions on top of the present generation backend — not a general recommendation engine, and not a claim of field-level editing.
6. **Product and marketing should use the same user story, and the same honesty boundary** — the P0 demo script should be the same script used to brief engineering, and should never show a capability (like real-time field editing or a general direction-recommendation model) that doesn't exist yet at the time it is published.
