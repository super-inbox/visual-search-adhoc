# PR #416 Evidence Map

**Repo checked:** `super-inbox/curify-studio` (current working repo, clean, `main` @ `7b3fa5b`)
**PR:** `super-inbox/curify-studio#416` — "docs: zero-prompt creative workflow proposal + demand appendix (2026-07-31)"
**Access:** ✅ Read via authenticated `gh` CLI (`gh pr view 416`, `gh pr diff 416`) — no write operations performed.
**State:** `MERGED` · author `qqwjq1981` (Jay Wang) · base `main` ← head `jwang/zero-prompt-proposal` · 1 commit, merged 2026-07-31.

> Label legend used throughout this document: **[Observed in code]** = I read the actual source and line range cited. **[Stated in PR]** = the PR body/diff says this; I did not independently verify it against a running system. **[Inference]** = my own reasoning connecting facts; not asserted by the PR or the code. **[Recommendation]** = my suggestion, not a fact.
>
> Every claim in this document is additionally sorted into exactly one of four buckets, made explicit wherever it might otherwise be ambiguous: **(1) PR actual change** — what the PR's diff literally added/removed; **(2) PR stated goal** — what the PR's prose describes as the desired future state; **(3) similar building block found in source** — something present in `curify-frontend` or `curify-studio` that is thematically related to (2) but is not the same thing under a different name; **(4) not found in the inspected scope** — searched for and not located, which is a statement about this audit's search coverage, not a certainty that it doesn't exist anywhere in either repository.

**Re-verification note:** PR #416's read-only accessibility (`gh pr view 416 --repo super-inbox/curify-studio --json state,title`) was re-checked at the start of this revision pass and returned `state: MERGED` with the same title as originally recorded — consistent with the original read, no changes to reconcile. The quotes below were not re-fetched in full during this pass; they were verified once, directly from `gh pr diff`, in the original research pass, and re-confirming `state`/`title` here did not surface any reason to doubt that earlier reading.

---

## 0. What PR #416 actually is (important scope correction)

**[Observed in code — PR metadata]** PR #416 is a **docs-only PR**. `gh pr view 416 --json files` returns exactly two files, both `ADDED`, zero deletions, zero code files:

```
docs/zero-prompt-creative-workflow-proposal-2026-07-31.md   (+165 / -0)
docs/zero-prompt-demand-appendix-2026-07-31.md              (+54 / -0)
```

No `.tsx`, `.ts`, `.py`, route, or config file is touched. **It is a strategy/positioning proposal, not a feature branch.** Nothing about generation flow, UI, or backend behavior was shipped by this PR itself — everything it describes as "the new interaction" is a proposal for future work, not a merged feature.

**[Observed in code]** These two files do not currently exist on local `main` (`7b3fa5b`) — `ls docs/zero-prompt-creative-workflow-proposal-2026-07-31.md` fails locally even though GitHub shows the PR as merged. The local checkout does not contain these two files. A likely explanation is that the local `main` is behind the merged PR (i.e., behind `origin/main`), but this was not resolved because a `git fetch` attempted during this audit timed out in this sandboxed environment. Other repository-history or checkout explanations were not ruled out. This was not investigated further since this task is read-only and non-blocking — the PR content itself was read directly from GitHub via `gh`, which does not require the local clone to be current.

---

## 1. PR goal

**[Stated in PR]** Reposition Curify from "AI image generation tool / templates / prompts" to "zero-prompt creative workflow": idea → creative direction → production-ready asset set. Core line (translated): *"I have an idea or some material, I don't know how to prompt, I'm not a designer, but I want a professional design result directly."* The PR explicitly says Curify should not compete as "help you find/make one image" (Canva/Pinterest/Midjourney territory) but as "idea → creative direction → deliverable asset set."

## 2. Modified files

**[Observed in code]** Only the two markdown files listed above. No application code, no route, no component, no schema.

## 3. Key components/claims referenced by the PR (and their real status)

| PR claim | My verification | Verdict |
|---|---|---|
| "代码已证实：`ReproduceWorkbench` 就是 `source` 列 + `prompt` 第二列 + production" (code already confirms: ReproduceWorkbench is the source column + prompt column + production) | **[Observed in code]** `ReproduceWorkbench` exists at `curify-frontend:app/[locale]/_components/ReproduceWorkbench.tsx` (686 lines). It is NOT in this repo (`curify-studio`) — it lives in the sibling frontend repo `super-inbox/curify-frontend`, read via `gh api` (read-only, no clone/checkout performed). The component genuinely renders 3 columns: col 1 "Source"/"Your image" (`ReproduceWorkbench.tsx:365-413`), col 2 "Make it yours" / "Prompt & generate" with a raw prompt textarea inside a `<details>` "Prompt preview / Advanced prompt editing" block (`ReproduceWorkbench.tsx:415-554`, prompt rendered at line 494-496: `{filledPrompt || basePrompt}`), col 3 "Turn it into design work" (designer-pack tiles: resize, print-ready, PDF pack, video) (`ReproduceWorkbench.tsx:556-682`). | **CONFIRMED — this PR claim is accurate**, once the correct repo is checked. |
| "Magic Drop" (home drop-zone → auto-extraction → instant fan-out into Emotion Pack / Sticker Pack / Merch Mockups) | **(2) PR stated goal**, named in the proposal text. **(4) Not found in the inspected scope:** no component named "Magic Drop" was located anywhere in `curify-frontend`'s recursive file tree (1086 files searched by name/content). **(3) Similar building blocks found in source:** `HomeImageWorkbench.tsx` (`curify-frontend:app/[locale]/(public)/HomeImageWorkbench.tsx`), a homepage upload-and-pick-a-workflow surface (see §5 below), and `ip-merch-demo/MerchWorkflowBurst.tsx`, a component whose own code comment describes it as **client-side-only, no-backend, instant CSS-composited**, used on a pitch/demo page (`noindex`, `dynamic="force-dynamic"`) — *"Pure client-side: the doodle is composited into each product's print zone via CSS (no upload, no backend, no generation latency)... This is a DEMO surface — the 300 DPI / CMYK / 3mm-bleed labels are pre-press framing, not exported print files."* (`MerchWorkflowBurst.tsx:7-17`). | **Not found as a real, backend-connected generation flow in the inspected scope.** A visual mock of a related idea exists on a noindex pitch page, per its own code comment; this should not be read as "Magic Drop has been built under a different name" — it is a narrower, explicitly-mocked artifact, and the search covered `curify-frontend` only, not every private branch or unmerged work that may exist elsewhere. |
| "Visual Mad Libs" (prompt broken into clickable chips that assemble an agentic prompt behind the scenes) | **(2) PR stated goal**, named in the proposal text. **(4) Not found in the inspected scope:** searched `curify-frontend` for chip-based prompt-assembly UI beyond the known `TemplateParameter` form fields (`ReproduceWorkbench.tsx:420-465`, which are per-template text/select/language-pair inputs) and found no dedicated "Visual Mad Libs" component. **(3) Similar building block found in source:** per-template parameter chips with candidate-value quick-fill buttons (`ReproduceWorkbench.tsx:428-444`). | **Not found in the inspected scope, as a cross-field agentic-prompt-assembly UI.** The similar building block that does exist (per-field autofill chips) is narrower in scope than the PR's description and should not be treated as the same feature. |
| Three demo formats mapped to existing pipelines (`video_pipelines/ip_to_video`, `video_pipelines/brand_to_video`, `ecommerce-video-mini` / `curify-project-video-generation`) | Not verified — these pipeline names were not located under `dev/jayw/` in this repo in the time available (dev/jayw contains `ecommerce-video-mini`, confirming that one path only); the others were not independently confirmed. | **[Stated in PR], unverified.** Treat as an internal team claim, not confirmed fact. |
| Intent → Creative Direction → Production replacing Query → Images | **(3) Similar building block found in source:** an LLM-tagged 8-cluster "intent cluster" taxonomy (`curify-frontend:lib/intent_taxonomy.ts`, `lib/intent_clusters.ts`), applied **after** a keyword search returns results, as refinement chips — see §4 of the flow audit. **(4) Not found in the inspected scope:** a front-loaded direction-recommendation step that runs before generation. | **Partially present today, in a different sequence than the PR describes.** The taxonomy exists; the PR's target sequencing (recommend directions before generation, not after search) was not found in the inspected scope. |

## 4. Routes / entry points named or implied by the PR

**[Stated in PR]**: home page drop zone; a reworked 3-column workbench with "Prompt" column removed; `image-video-tools-adhoc/daily_reports/` (a separate **public** repo) for sanitized daily progress logs, keeping strategy/positioning in `curify-studio/docs` (this repo, private).

**[Observed in code]**: the present-in-source route analogs are `/` (home, `curify-frontend:app/[locale]/(public)/page.tsx`), `/search` (`search/page.tsx`), `/nano-template/[slug]` and `/nano-template/[slug]/example/[exampleId]` (template + example detail, both embedding `ReproduceWorkbench`), `/nano-banana-pro-prompts` and `/nano-banana-pro-prompts/[id]` (prompt gallery + remix), `/workspace` (history), `/image-project/[id]` (result/edit page), `/ip-merch-demo` (noindex pitch demo). Whether each of these routes is currently reachable and serving real traffic in production was not independently verified — this is a source/routing-file audit. Full detail in `CURRENT_PRODUCT_FLOW_AUDIT.md`.

## 5. What the user needs to input today vs. what the PR wants automated

| | Today **[Observed in code]** | PR's target **[Stated in PR]** |
|---|---|---|
| User input | Either a search keyword (`/search?q=`), OR per-template structured params (`ReproduceWorkbench` col 2 form fields), OR a free-text prompt they type/edit themselves (`nano-freeform` remix surface) | A vague idea, a dropped image, or a brief — no prompt authored by the user |
| System-inferred | Template's `base_prompt` + param substitution (`fillPrompt`, `curify-frontend:lib/nano_pure.ts`, referenced at `ReproduceWorkbench.tsx:14,221`); tag-based routing to a matching tool (`promptToolMatch.ts`) | Full creative direction (3 style options), full prompt construction, subject/character extraction from an uploaded sketch |
| User's next action | Fill in 0-3 structured params, optionally expand "Advanced prompt editing" and hand-edit the raw prompt text, click Generate | Pick one of 3 recommended directions, confirm minimal info, click Generate |

## 6. Connections to search / templates / generation / editing

- **Search → templates:** `[Observed in code]` `/search` server logic pulls from the same `nano_templates.json` / `nano_inspiration.json` corpus and links into `/nano-template/[slug]#reproduce` (`SearchResultsClient.tsx`, `GenerableTemplatesSection.tsx:413`).
- **Templates → generation:** `[Observed in code]` `/nano-templates/generate` backend endpoint (`curify_background/app/routers/nano_templates.py:105-201`), structured `params: Dict[str,str]`, async (returns `project_id`, client polls `/projects/{id}/status`).
- **Gallery/remix → generation:** `[Observed in code]` `/nano-freeform/generate` (`curify_background/app/routers/nano_freeform.py:72-97`) takes a raw user-edited `prompt` string plus optional `reference_image_url` and `source_prompt_id` (for remix-funnel tracking) — this is the actual "prompt exposed to the user" surface the PR objects to.
- **Generation → editing/export:** `[Observed in code]` A finished project reopens `ReproduceWorkbench` in `"result"` mode (`ReproduceWorkbench.tsx:56-63, 230-232`) where column 2 (parametric re-generate) is explicitly **hidden and stated as not yet built**: *"A loaded project carries no template/params to drive parametric regeneration (that's a later phase)"* (`ReproduceWorkbench.tsx:54-56`; same statement repeated in `image-project/[id]/page.tsx:21-24`, docs pointer `docs/image-workflow-page-design-2026-07-11.md`, not present in this repo). Only column-3 "designer pack" derivative transforms (resize, print-ready crop, PDF pack) operate on the finished image.

## 7. Present in source vs. proposal-only, not found in scope (strict separation)

**Present in source [Observed in code] (backend and/or frontend code exists; production runtime status not independently verified):**
- Keyword search over template/inspiration corpus with relevance scoring, query normalization, synonym expansion (`search/page.tsx`).
- Post-search "intent cluster" / output-type chip refinement (`lib/intent_clusters.ts`, `lib/intent_taxonomy.ts`) — 8 creation-intent clusters, 19 output-type slugs, LLM-tagged.
- Template-driven structured-param generation (`/nano-templates/generate`).
- Free-form prompt generation from a gallery remix (`/nano-freeform/generate`).
- A homepage "source-first" omni-input router that detects URL vs. text and deep-links to the matching tool or `/search` (`HomeOmniInput.tsx`) — **explicitly labeled v1, a router only**, per its own doc comment (`HomeOmniInput.tsx:19-30`).
- A homepage image-upload workflow picker (`HomeImageWorkbench.tsx`) offering 4 fixed workflows (Product→Poster, Product→Listing, IP→Sticker pack, IP→Mockup set), each a `requires_image_upload` template with 0-1 params — i.e., a **present-in-source building block, referenced in the homepage composition, implementing the shape of "pick a goal → upload → generate."** This is a closer structural match to the PR's vision than the PR's own text credits — worth noting as an inference, though this audit did not verify how (or whether) it currently performs for real users.
- A noindex, pitch-only demo page (`/ip-merch-demo`) with a fully client-side, no-backend "drop a doodle → instant 10-product burst" animation, explicitly marked in its own code comment as a mock, not a real pipeline.
- Designer-pack derivative transforms (resize-to-social, print-ready bleed) on a finished generation.

**Proposal-only — not found in the inspected scope [Stated in PR / Inference]:**
- Killing/hiding the prompt column entirely (today it's collapsed by default in some contexts but still present and user-editable — `ReproduceWorkbench.tsx:482-498`).
- Front-loaded intent → 3 creative-direction recommendation step before any generation call.
- Real (non-demo, backend-connected) "Magic Drop" auto-extraction + multi-surface fan-out from a single dropped image.
- "Visual Mad Libs" cross-field agentic prompt assembly from clickable option chips.
- Parametric re-generation / content-only editing of an already-generated result (explicitly deferred in code comments, see §6).
- Marketing copy changes (new slogans, video series) — none of this exists in the frontend's actual copy yet; current homepage copy is workflow/solutions-oriented ("Find → Understand → Create → Adapt → Scale", `HomeWorkflow.tsx:12-18`) but does not use the PR's proposed "Zero Prompts. Studio Quality." language.

## 8. Known limitations of this evidence map

- Frontend evidence (`curify-frontend`) was read via `gh api` (read-only file fetch), not a local checkout — I did not run the app, so behavior described from code (e.g. what `useDirectGenerate` actually does end-to-end, or whether `#reproduce` anchor scroll works) is **read from source, not observed at runtime**.
- The three "existing dev/jayw video pipelines" the PR cites (`ip_to_video`, `brand_to_video`, `curify-project-video-generation`) were only partially cross-checked against `dev/jayw/` in this repo; treat as **[Stated in PR], not independently confirmed**.
- RedNote (Xiaohongshu) demand data mentioned in the PR's appendix as "next step, not done yet" — genuinely not done, per the PR's own §1.4.
