# Current Curify Page Audit vs. VerticalPageSchema v1 — Gap Analysis

**Date:** 2026-07-29
**Task type:** Research / design prep (read-only repo analysis). No code was modified.
**Repo:** curify-frontend-prod-template-qa
**Source design doc:** `docs/vertical-page-schema-v1.md` (2026-07-28, status: "Design doc — not yet
implemented" for the parts marked ❌ below; parts marked ✅ are already shipped per that doc's own
"Implemented in v1" section).

## 1. Files reviewed

| File | Role |
|---|---|
| `docs/vertical-page-schema-v1.md` | The design doc this audit is measured against |
| `app/[locale]/(public)/nano-template/[slug]/page.tsx` | Template detail page (the "hub") |
| `app/[locale]/(public)/nano-template/[slug]/example/[exampleId]/page.tsx` | Example detail page (the "spoke") |
| `lib/vertical_schema.ts` | `VerticalPageSchema` type + registry (`VERTICAL_SCHEMAS`) |
| `app/[locale]/_components/VerticalKnowledge.tsx` | `VerticalAttributeChips` + `VerticalKnowledgeSection` render components |
| `lib/nano_seo_utils.ts` | `resolveContentSections`, `resolveVerticalSections`, `buildVerticalJsonLd`, `buildNanoTemplateMetadata`, `buildNanoH1` |
| `messages/en/nano.json` | Per-template i18n content, incl. `content.sections` / `content.attributes` / `content.vertical` |

No other files were read for this audit (component internals of `ExampleImagesGrid`,
`NanoTemplateDetailClient`, `ExampleReproduceSurface` were referenced but not deeply audited — their
externally-visible behavior (CTA labels, gallery, reproduce panel) was already confirmed via live
screenshots taken in a separate, unrelated QA task on this same page family and is consistent with
the imports/usage seen in the page files above).

## 2. What the current template page (`nano-template/[slug]`) already has

| Module | Present? | Detail |
|---|---|---|
| H1 | ✅ | `buildNanoH1()` — cleaned title (strips "Nano Banana Prompt:" / "\| Curify AI" decoration) |
| SEO `<title>` / meta description | ✅ | `buildNanoTemplateMetadata()` — from `messages/{locale}/nano.json` title/description, with fallback chain |
| Category chip | ✅ | pill badge next to H1 |
| Intro / description paragraph | ✅ | one paragraph under H1 |
| **Vertical attribute chip strip** | ⚠️ **partial** | `VerticalAttributeChips` — renders only if `resolveVerticalSections()` returns non-null, i.e. only for templates in a pilot vertical (education/mbti/merch) **AND** that already have `content.attributes` authored in nano.json. As of this audit, only 1 template (`template-hsk-bilingual-reading-text-lesson-poster`) has this data — see §5. |
| Example/template card gallery | ✅ | `ExampleImagesGrid` — up to `maxRows=2`, batch-aware, desktop click-through to example page |
| "Reproduce this template" panel | ✅ | `NanoTemplateDetailClient` (`showReproduce=true`) — parameter inputs, live prompt preview, Copy/Save/Share |
| "Other templates" rail | ✅ | second `NanoTemplateDetailClient` call (`showOtherTemplates=true`) |
| "About this template" (what/who/how/prompts) | ✅ | `resolveContentSections()` → What is this / Who should use it / How to use it / Example prompts, each conditionally rendered |
| **Vertical knowledge block** | ⚠️ **partial** | `VerticalKnowledgeSection` — same gating as the chip strip; renders "{Vertical} details" `<dl>` under "About this template" only when authored |
| **Vertical JSON-LD** | ⚠️ **partial** | `buildVerticalJsonLd()` — emits `LearningResource`/`Article`/`Product` `@type` per vertical, only when `resolveVerticalSections()` is non-null |
| Topic chip rows (top + "Explore More") | ✅ (sr-only) | present in DOM for crawl/internal-linking, visually hidden — moved to bottom `TopicStrip` for end users |
| Bottom `TopicStrip` (visible topic browsing) | ✅ | merges template topics + tier-3 sub-topics |
| FAQ section | ❌ | not present anywhere in this page |
| Breadcrumbs | ❌ | template page has no breadcrumb nav (the example page does — see §3) |
| `BreadcrumbList` JSON-LD | ❌ | not emitted anywhere in either page |
| Trust signals (reviews, ratings, usage counts) | ❌ | none observed |

## 3. What the current example page (`nano-template/[slug]/example/[exampleId]`) already has

| Module | Present? | Detail |
|---|---|---|
| Breadcrumbs | ✅ | Home / Template category / Example title |
| H1 | ✅ | example title, with MBTI-specific title-format injection logic (appends "MBTI" head-term when missing, per a documented 2026-06-10 CTR fix) |
| Topic chips + category link | ✅ (sr-only for topic chips) | |
| **Vertical attribute chips** | ❌ **not rendered at all** | Confirmed by direct read of the page file — no import of `VerticalAttributeChips`/`VerticalKnowledgeSection`/`buildVerticalJsonLd` on this page. This matches the design doc's own Roadmap item #2, which explicitly calls out the example page as "today shows no domain prose" and names this the **highest-lift unbuilt work**. |
| "Reproduce" workbench | ✅ | `ExampleReproduceSurface` — source/make-it-yours/production tiles, unified with the gallery reproduce UX |
| Video player (when example has a video asset) | ✅ | `ExampleVideoPlayer` |
| Prev/Next example nav | ✅ | circular nav within the template's example set |
| "More like this" / "More from this template" gallery | ✅ | `ExampleImagesGrid`, similarity-ranked with per-template cap |
| Related-topics footer | ✅ (sr-only) | `ExampleRelatedTopics`, expands topic union with ancestors |
| Bottom `TopicStrip` | ✅ | same pattern as template page |
| World-Cup → travel cross-sell rail | ✅ | conditional, only on WC-tagged content |
| JSON-LD | ⚠️ **`HowTo` only** | 3 generic steps ("Open Nano Banana… / Enter the prompt… / Generate and download…"); not vertical-aware, not per-instance ontology |
| FAQ section | ❌ | none |
| `BreadcrumbList` JSON-LD | ❌ | breadcrumb nav is visual only, not machine-readable |

## 4. What `VerticalPageSchema v1` (design doc) plans to support

The doc's four-pillar model (Know → Structure → Show → Make):

| Pillar | What it adds | Doc-stated status |
|---|---|---|
| 1. Knowledge | Authored domain prose beyond what/who/how (per-vertical "knowledge slots") | Partially exists (what/who/how on most templates); vertical-specific slots are net-new, gated behind pilot enrichment |
| 2. Attributes | 10–20-field machine-readable ontology per vertical → chip strip + facets + JSON-LD `additionalProperty` | ❌ core gap — schema exists in code (`vertical_schema.ts`) but **values are authored per-template in nano.json and only 1 template has them filled in** |
| 3. Assets | Example gallery | ✅ already exists, unchanged by this work |
| 4. Create | Generate/Remix CTA | ✅ already exists (`ReproduceTemplateSection`/`NanoTemplateDetailClient`), unchanged |

Five verticals are designed in the doc; **only 3 are implemented in code** (`VERTICAL_SCHEMAS` in
`lib/vertical_schema.ts`):

| Vertical | In `VERTICAL_SCHEMAS`? | Attribute count (doc) | Knowledge slots (doc) | schema.org type |
|---|---|---|---|---|
| Education | ✅ | 11 fields in doc §2.1 (8 shipped in code — `duration_min`/`age_range` etc. trimmed to code's 8) | 3 (learning_objective, includes, background) | `LearningResource` |
| MBTI / Character | ✅ | 10 fields in doc §2.2 (4 shipped in code) | 7 (traits, strengths, weaknesses, communication, relationships, career, compatibility) | `Article` |
| Culture / 服饰 | ❌ not in code | 8 fields designed (doc §2.3) | not coded | `Article` (planned) |
| 文创 / Merch | ✅ | 9 fields in doc §2.4 (7 shipped in code) | 3 (cultural_background, design_requirements, manufacturing_notes) | `Product` |
| **E-commerce content** | ❌ **not in code** | 6 fields designed (doc §2.5: product_category, shot_type, background, platform, resolution_note, conversion_role) | **none designed yet** — the doc lists only attribute fields for this vertical, no knowledge slots | `Product`/`ImageObject` (planned) |

**This directly affects the 4 research categories in this task:** MBTI, Education, and Merch have a
code-level schema to design against (even though rendering is still mostly unauthored — see §5).
**Ecommerce Content has no schema in code at all** — it is explicitly deferred in the doc's Roadmap
item #3 ("Vertical v2 — culture + ecommerce... once the first read-out validates the approach") and
has no knowledge-slot design yet, only a 6-field attribute sketch. Research for the Ecommerce
category should treat this as a from-scratch design input, not a gap-fill exercise.

## 5. Enrichment status — how much of the *design* is actually *live*

The rendering code (chip strip, knowledge block, JSON-LD) is shipped and wired into the template
page for all 3 coded verticals. But it is **gated on authored data that mostly doesn't exist yet**:
`resolveVerticalSections()` returns `null` — and the page renders with zero vertical layer, exactly
as it did before this project — unless a template's `messages/en/nano.json` entry has a non-empty
`content.attributes` or `content.vertical` object.

Checked directly against `messages/en/nano.json` for the 12 pilot templates the doc names in its
"Pilot cohort — GSC-mined" table:

| Vertical | Pilot templates named in doc | Templates with `content.attributes`/`content.vertical` actually filled in |
|---|---|---|
| Education | `template-hsk-bilingual-reading-text-lesson-poster`, `template-chinese-idiom-learning-card`, `template-education-card`, `template-kids-vocabulary-poster` | **1 of 4** (HSK only — doc itself calls this "shipped"; the other 3 are still plain what/who/how, no ontology) |
| MBTI | `template-mbti-generic`, `template-mbti-yellowstone`, `template-friends-character-mbti`, `template-chinese-classic-character-mbti` | **0 of 4** |
| Merch | `template-city-landmark-fridge-magnet-collection`, `template-food-product-packaging-design`, `template-ip-creative-cultural-goods-mockup-set`, `template-fridge-magnet-merch` | **0 of 4** |

So today, in Production, **exactly one page in the entire catalog renders the vertical layer** — the
HSK template. Every other MBTI and Merch template (pilot or otherwise) currently renders identically
to a page with no vertical schema at all. This is a live-repo fact, not a criticism of the doc's plan
(the doc itself says Phase 1 is "hand-enrich a small cohort... do NOT batch-generate" and is still
mid-rollout).

## 6. Gap analysis summary (current page vs. design doc)

| Gap | Severity for this research task | Notes |
|---|---|---|
| Example page has zero vertical-layer rendering (chips/knowledge/JSON-LD) | **High** | Doc's own roadmap ranks this the highest-lift unbuilt item (85% of impressions land on example pages, not template pages) |
| Only 1/12 named pilot templates have authored ontology data | **High** | The Pillar-2 "structured attributes" pillar — the thing the 4 research categories are meant to inform — is present in schema/code but nearly unauthored in content |
| No Ecommerce Content schema in code | **High** (for category 4 specifically) | Research for this category is greenfield, not gap-fill; there's no existing attribute/knowledge-slot list to react to beyond the 6-field doc sketch |
| No FAQ module anywhere | **Medium** | Common competitor pattern (TpT, 16Personalities, Printify all have FAQ or Q&A blocks); not in the current page or the design doc's pillar list |
| No `BreadcrumbList` JSON-LD | **Medium** | Visual breadcrumbs exist on the example page only; neither page emits the structured-data equivalent |
| Example-page JSON-LD is generic `HowTo`, not vertical-aware | **Medium** | A `LearningResource`/`Article`/`Product` per-example JSON-LD is exactly Roadmap item #2, unbuilt |
| No trust signals (ratings, usage stats, testimonials) | **Low–Medium** | Not in current page; not in design doc either — a candidate finding for the competitor research if reference sites lean on it |
| Merch/MBTI code schemas are trimmed vs. the doc's fuller field lists | **Low** | e.g. doc's MBTI table lists `strengths`/`weaknesses`/`career_fit`/`compatibility` as *attributes*; shipped code moved most of those into *knowledge slots* instead (only `type_code`/`type_nickname`/`dimensions`/`subject_kind` are attributes) — a modeling choice already made, worth noting but not a "missing" gap |

## 7. Implication for the 4 research categories

- **MBTI**: schema exists (4 attributes + 7 knowledge slots), reference sites named (16Personalities,
  Truity), but zero live pages render it. Research should validate/stress-test the existing 11-field
  design against what competitors actually show, not just confirm it.
- **Education**: schema exists (8 attributes + 3 knowledge slots), 1 live reference implementation
  (HSK) to compare research findings against directly. Best-covered vertical.
- **Creative Merch (文创)**: schema exists (7 attributes + 3 knowledge slots), reference sites named
  (Printify, Prodigi), zero live pages. Doc explicitly flags this as "the sharpest differentiator vs
  a plain AI-image site" — research should focus on the spec-sheet / manufacturing-notes pattern.
- **Ecommerce Content**: **no schema in code**, only a 6-field attribute sketch in the doc with no
  knowledge slots defined and no pilot templates chosen. This category's research output should
  propose a fuller schema (attributes + knowledge slots), not just validate an existing one.
