# Current Product Flow Audit

**Scope note (read first):** This audit reads source code and repository composition. **It does not independently verify deployed production behavior, feature flags, experiments, or runtime availability.** Every finding below describes what is present in a repository's source files and, where relevant, how a page's component composition references those files — not what a real user is currently served, which feature flags may gate, or how any A/B experiment may currently route traffic. Where the word "shipped," "live," or "online" would be tempting, this document instead says "present in source" or "referenced in the [page] composition," and flags explicitly when a claim would need runtime access this audit did not have.

The task asked to audit "the current Curify product" by searching code in this repo (`super-inbox/curify-studio`). In reality, **this repo contains no frontend** (zero `.tsx`/`.jsx` files; `find . -iname "*.tsx"` returns 0). `curify-studio` is a backend/tools monorepo: `curify_background/` (FastAPI backend service), `admin_portal/` (internal ops tool), `gtm_tools/` (marketing/GTM scripts), `dev/<engineer>/` (personal sandboxes/pipelines), plus `docs/`. The actual consumer-facing web app (Homepage, Search, Templates, Editor, etc.) lives in a **separate sibling repo, `super-inbox/curify-frontend`** — confirmed by a hardcoded URL in this repo's own backend code: `curify_background/app/routers/nano_templates.py:29` fetches `https://raw.githubusercontent.com/super-inbox/curify-frontend/main/public/data/nano_templates.json`.

To honor the spirit of "audit the current product flow with code evidence" rather than produce a report based only on internal docs, I read `curify-frontend` **read-only**, via authenticated `gh api` calls (file-content fetches over the GitHub API — no `git clone`, no checkout, no local copy retained outside this session's scratch dir, no build or run of the application). This is flagged explicitly per the instructions ("如仍无法获取...不要猜测"): I did not guess at frontend behavior — I read the actual source. What follows is therefore a **source-code-level** audit; it is not a runtime-verified audit.

All file paths below prefixed `curify-frontend:` are in that sibling repo (read via `gh api`, not present locally). Paths prefixed `curify_background:` are in this repo.

---

## 1. Current user entry points

**[Observed in code]** `curify-frontend:app/[locale]/(public)/page.tsx` (home) renders, top to bottom (per `HomeClient` composition and sibling files):
- `HomeHero` — headline + montage of real generated images (`HomeHero.tsx:14-73`)
- `HomeOmniInput` — single text box (`HomeOmniInput.tsx`)
- `HomeImageWorkbench` — upload + pick-a-workflow 3-column workbench (`HomeImageWorkbench.tsx`)
- `HomeWorkflow` — 5-step "Find → Understand → Create → Adapt → Scale" explainer strip (`HomeWorkflow.tsx:12-18`)
- `HomeSolutionsGrid` — 6 audience entry cards linking to `/use-cases/for-*`, `/tools`, etc. (`HomeSolutionsGrid.tsx:16-23`)
- `HomeFusedRow` / `HomeDiscoveryStrip` / `HomeToolsStrip` — content rails (inspiration cards, gallery prompts, search-query nudges)

Other entry points: `/search`, `/nano-template/[slug]`, `/nano-banana-pro-prompts` (gallery), `/tools`, `/ip-merch-demo` (noindex pitch page), `/use-cases/for-*` (not read in full — out of time budget), blog (`/blog/*`, large SEO surface, not creative-workflow-relevant).

## 2. Home page current expression

**[Observed in code]** Two components are both present in the inspected source and both appear to be referenced in the homepage's component composition (per `page.tsx`/`HomeClient`):

1. **`HomeOmniInput`** — a single text box. Its own code comment calls it *"the 'Source-First Routing' front-door (agentic doc P0-6)... v1 is deliberately a smart router (deep-links to shipped tool routes); it does not yet carry the source into the destination's internal state... is the next increment"* (`HomeOmniInput.tsx:19-30`). Behavior described in source: paste a URL → 3 chips for video tools; type free text → routes to `/search?q=<text>` (`HomeOmniInput.tsx:70-77`). **This matches the "blank prompt box" pattern the task's background worries about** — no intent understanding, just URL vs. text sniffing — based on reading the source, not on observing it run.
2. **`HomeImageWorkbench`** — appears directly below it in the composition, and its own comment says it *"replaces the router-style Omni-Input v1"* (`HomeImageWorkbench.tsx:10-19`). Whether this "replaces" claim reflects a completed product decision, an in-progress migration, or a stale comment left after a decision was reversed **cannot be determined from source alone** — code comments describe intent at the time they were written and may be out of date. What can be said from source: both components exist in the file tree and both are referenced in the composition; whether both, one, or neither is actually served to real users today was not independently verified (this would require runtime/deployment access this audit did not have). This is nonetheless a useful signal that the home-page entry strategy had not been fully reconciled as of the state of the source read, which is relevant to — but not proof of the sole cause of — the boss's broader "misalignment" concern.

`HomeImageWorkbench` offers 4 fixed workflow buttons (Product→Poster, Product→Listing, IP→Sticker pack, IP→Mockup set; `HomeImageWorkbench.tsx:29-65`), each pre-wired to a `requires_image_upload` template with 0-1 extra params, driving the shared `ReproduceWorkbench` in upload mode. **This is the closest present-in-source analog to Concept C (goal-first, pick-a-deliverable-then-fill-minimal-info)** — described here as a source-level building block, not a claim about its current production usage or performance.

## 3. Search and inspiration discovery path

**[Observed in code]** `/search` (`curify-frontend:app/[locale]/(public)/search/page.tsx`, 1298 lines server-side) is a heavyweight keyword relevance engine: query normalization (`normalizeForSearch`), garbage-query detection (`looksLikeGarbageQuery`), synonym/concept expansion (`CONCEPT_SYNONYMS`), phrase protection, business overrides, multi-query LLM rewrite fallback when results are thin, topic co-occurrence scoring, and a capped candidate pool (`TOTAL_CANDIDATE_POOL_CAP`, `PATH_CANDIDATE_CAP`). This is a genuinely sophisticated **"images for every query"** implementation — literally the old positioning, at the code level.

Post-search, `SearchResultsClient.tsx` renders: matched templates, gallery prompts, related-topics strip, and — importantly — **`intentChips`**: a Pinterest-style "Explore further" chip row (`SearchResultsClient.tsx:16,58-62`). These chips are computed by `lib/intent_clusters.ts` + `lib/intent_taxonomy.ts`: **a real, LLM-tagged, 8-cluster intent taxonomy over 19 output-type slugs** (flashcards, recipes, mind-maps, stickers, character-ip, etc. — `intent_clusters.ts:26-42`). This is a genuinely reusable asset for a future "recommend a creative direction" step — **but today it only refines/filters results that already came back from a keyword search; it never runs before or independent of a query.**

## 4. Template / example detail path ("Make your own")

**[Observed in code]** `/nano-template/[slug]` and `/nano-template/[slug]/example/[exampleId]` both embed the shared `ReproduceWorkbench` component (`curify-frontend:app/[locale]/_components/ReproduceWorkbench.tsx`, 686 lines) — confirmed to be the exact 3-column `source → prompt → production` structure PR #416 describes (full detail in `PR416_EVIDENCE_MAP.md` §3). Prior internal doc `docs/reproduction-surface-review-2026-06-21.md` (in this repo) independently corroborates: *"`NanoInspirationCard` (template) | home, topic, search | **'Make your own'** (`remixThis`) → `#reproduce`"* — the CTA verb is literally "Make your own," landing on an anchor into this same workbench.

Column 2 always keeps a **raw prompt text block** in the DOM — collapsed by default in "source" mode, **open by default in "upload" mode** (`ReproduceWorkbench.tsx:480-498`) — labeled "Prompt preview" or "Advanced prompt editing." The prompt is never fully hidden; it's demoted to a disclosure widget. This is a partial, not complete, version of "hide the prompt from the user."

## 5. Gallery / remix path (prompt exposed to the user today)

**[Observed in code]** `/nano-banana-pro-prompts` (gallery of ~4,117 prompts per `promptToolMatch.ts:4-6` comment) and `/nano-banana-pro-prompts/[id]` detail pages let a user browse existing prompts (backed by `curify_background/app/routers/nano_prompts.py:17-140`: `/feeds`, `/most-popular`, `/tag/{tag}`, `/{id}`). The detail page's `GalleryReproduceSurface.tsx` and `PromptTryInTool.tsx` feed into `/nano-freeform/generate` (`curify_background/app/routers/nano_freeform.py:72-97`), whose request body is a **user-edited free-text `prompt` string** (`FreeformGenerateRequest.prompt`, min/max length validated, no template). Code comment: *"Used by the gallery remix surface (frontend: /nano-banana-pro-prompts/[id])"* (`nano_freeform.py:7`). **This is the clearest prompt-editing surface identified in the inspected scope** — the most literal embodiment of the pain point the boss described, among the surfaces this audit reviewed.

Separately, `promptToolMatch.ts` (`curify-frontend:app/[locale]/(public)/nano-banana-pro-prompts/[id]/promptToolMatch.ts`) routes a gallery prompt to "the right tool" via a small tag→tool lookup table, falling back to a **deterministic round-robin hash** across live tools when no tag matches (`promptToolMatch.ts:49-59, 68-86`). **The inspected routing implementation in this path uses a tag lookup and deterministic hash fallback, rather than semantic intent classification.** This describes what was found in this specific file, not a claim that no semantic classification exists anywhere else in either repository.

## 6. Generate entry points (backend, this repo)

**[Observed in code]** `curify_background/app/routers/`:
- `nano_templates.py:105` `POST /nano-templates/generate` — structured params (`Dict[str,str]`), template registry fetched from the frontend repo's public JSON (see scope note above), async (returns `project_id`, client polls `.../status`). Validates required params with placeholder/default fallback (`nano_templates.py:138-164`) and, for image-to-image templates, requires `reference_image_url` (`nano_templates.py:166-172`).
- `nano_freeform.py:72` `POST /nano-freeform/generate` — raw prompt + optional reference image + `source_prompt_id` (remix funnel tracking).
- `inspiration.py` — `/generate` (bulk), `/cards`, `/curate`, `/cards/{id}/approve|reject` — this looks like an **internal/admin content-curation pipeline** (approve/reject cards) rather than an end-user generation surface; not further audited given time budget.
- `template_packs.py:85`, `etsy_packs.py:116` — packaged PDF/asset-pack downloads, paid via credits.
- `product_video.py:55` `POST /product_video/generate` — separate product-video pipeline.

## 7. Editor and export entry points

**[Observed in code]** There is no dedicated "editor" page distinct from the workbench. A finished generation:
- Lives in `/workspace` (`curify-frontend:app/[locale]/(app)/workspace/WorkspaceClientPage.tsx`) under "generated" / "saved" tabs (`WorkspaceClientPage.tsx:20`), each card linking to `/nano-template/[slug]/example/[id]`.
- Or reopens at `/image-project/[id]` (`curify-frontend:app/[locale]/(app)/image-project/[id]/page.tsx`), which mounts `ReproduceWorkbench` in **`"result"` mode**: column 1 = the result image + Download button, column 3 = designer-pack derivative transforms (resize-to-social bundle, print-ready bleed), **column 2 (parametric re-generation) is explicitly hidden**, with the code comment: *"A loaded project carries no template/params to drive parametric regeneration (that's a later phase)"* (`ReproduceWorkbench.tsx:54-56`, same statement in `image-project/[id]/page.tsx:21-24`, referencing an internal doc `docs/image-workflow-page-design-2026-07-11.md` not present in this repo).

**This is explicitly deferred according to the cited code comment:** today, "I just want to change the store name and date" (task's own JTBD example) requires re-running generation from scratch — the code comment describes structured re-edit of an existing result's content as a "later phase," not yet built. "Editing" today = derivative transforms (resize, crop-to-print) on the whole image, not field-level content edits.

Export = plain browser download links (`<a href download>`) on the result image and on designer-pack tiles; no dedicated multi-format export flow was found in the inspected files and repository scope.

## 8. Where the flow breaks / is inconsistent

- **[Observed in code]** Two home front-door components (`HomeOmniInput` vs `HomeImageWorkbench`) are both present in source and both referenced in the homepage composition, with one's own comment claiming to replace the other — production runtime behavior (which is actually served to users) was not independently verified in this audit (§2).
- **[Observed in code]** Internal doc `docs/reproduction-surface-review-2026-06-21.md` (this repo) independently flags: *"Verb is inconsistent across the funnel: 'Make your own' (template/example), ... the home-rail [CTA] that feeds it advertises copy the text, not make your own"* (line 70) — i.e., even the CTA copy across surfaces disagrees with itself about whether the destination is "copy the prompt" or "make your own version." This is a pre-existing, internally-documented UX inconsistency, not something newly discovered for this task.
- **[Observed in code]** Post-generation editing gap (§7): no content-level re-edit path exists.
- **[Observed in code]** Intent taxonomy (§3) exists but only fires after a keyword search returns results — a user who has no keyword to type (the "blank prompt box fear" case) gets no benefit from it.

## 9. Where the user must write a prompt today

1. `/nano-banana-pro-prompts/[id]` gallery remix → `/nano-freeform/generate` — **full free-text prompt**, the clearest current instance of prompt exposure (`nano_freeform.py:30-38`).
2. `ReproduceWorkbench` "Advanced prompt editing" disclosure, open by default in upload mode (`ReproduceWorkbench.tsx:482-498`) — optional but visible/editable raw prompt text for power users; most users can ignore it and just fill the 0-2 structured params instead.
3. `HomeOmniInput` free-text box — not a prompt in the generation sense, but still an unstructured text field with no guidance on what "good" input looks like.

## 10. Existing structured-input / auto-inference capability

**[Observed in code]** Real, reusable pieces already exist:
- Per-template structured parameter schema (`TemplateParameter`, `curify-frontend:lib/nano_prompt_utils.ts`) with placeholder-derived candidate quick-fill chips (`ReproduceWorkbench.tsx:420-464`).
- Base-prompt templating with param substitution (`fillPrompt`, `lib/nano_pure.ts`).
- Output-intent tagging per template (`getOutputIntent`, used to customize workflow-tile copy, `ReproduceWorkbench.tsx:204,208`).
- 8-cluster / 19-slug intent taxonomy for search refinement (§3).
- Tag-based (not semantic) tool routing for gallery prompts (§5).
- A reference-image-upload component reused across surfaces (`ReferenceImageUpload.tsx`).

None of these are wired together into a single "tell us your goal → we infer the rest → confirm → generate" flow. They are the raw materials for one.

## 11. Are search, templates, and generation siloed?

**[Observed in code]** No — they share a data corpus (`nano_templates.json`, `nano_inspiration.json`) and cross-link (`/search` → `/nano-template/[slug]#reproduce` → `ReproduceWorkbench` → `/nano-templates/generate`). The generation backend itself is unified (`ReproduceWorkbench` calls either `useDirectGenerate` → `/nano-templates/generate`, or `useFreeformGenerate` → `/nano-freeform/generate`, depending on context). **The connective tissue exists; what's missing is a pre-generation step that turns a vague goal into a specific template + params choice without the user browsing/searching for it themselves.**

## 12. Summary table (entry → next step, with evidence)

| Stage | Current entry | Evidence |
|---|---|---|
| Homepage | `HomeOmniInput` (text router) + `HomeImageWorkbench` (upload+workflow-pick), uncoordinated | `HomeOmniInput.tsx:19-30`, `HomeImageWorkbench.tsx:10-19` |
| Search | Keyword relevance search + post-hoc intent chips | `search/page.tsx`, `intent_clusters.ts` |
| Template/example detail | `ReproduceWorkbench` 3-col (source/upload → params+prompt → designer pack) | `ReproduceWorkbench.tsx:360-686` |
| Gallery remix | Free-text prompt edit → `/nano-freeform/generate` | `nano_freeform.py:30-97` |
| Generate | Structured (`/nano-templates/generate`) or freeform (`/nano-freeform/generate`) | `nano_templates.py:105-201`, `nano_freeform.py:72-97` |
| Result / edit | `/image-project/[id]`, result-mode workbench, no parametric re-edit | `image-project/[id]/page.tsx:21-24` |
| Export | Plain download links | `ReproduceWorkbench.tsx:642-653` |
