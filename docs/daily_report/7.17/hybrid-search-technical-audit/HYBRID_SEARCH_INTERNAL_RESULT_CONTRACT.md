# Hybrid Search — Internal Result Data Contract

No unified `SearchResult` type exists in the codebase today. Confirmed by reading `app/[locale]/(public)/search/page.tsx`, `lib/nano_pure.ts`, `lib/searchTemplateMatch.ts`, `types/nanoPrompts.ts`. Three structurally different arrays are rendered as three separate page sections.

## A. `InspRecord` — inline type, `page.tsx:426-439`

```ts
type InspRecord = {
  id: string;
  template_id: string;
  asset: { preview_image_url: string; image_url: string; video_url?: string };
  params?: Record<string, unknown>;
  locales?: Record<string, { title?: string; category?: string }>;
  tags?: string[];
  topics?: string[];
  search_aliases?: string[];   // hidden synonyms, never rendered
};
```
Wrapper during scoring only (discarded before render): `ScoredInspiration = { rec: InspRecord; score: number; strict: boolean }` (page.tsx:450).

## B. `NanoInspirationCardType` — `lib/nano_pure.ts:115-135`

```ts
export type NanoInspirationCardType = {
  id: string; template_id: string; language: PageLocale; category: string;
  topics: string[]; rank_score?: number; image_urls: string[]; preview_image_urls: string[];
  example_ids?: string[]; description?: string; base_prompt?: string;
  template_parameters?: TemplateParameter[]; sample_parameters?: Record<string, any>; batch?: boolean;
};
```
Has `rank_score` — a business/curation ranking field, not a query-relevance score.

## C. `TemplateMatch` — `lib/searchTemplateMatch.ts:113-124`

```ts
export type TemplateMatch = {
  template_id: string; params: Record<string, string>; confidence: number; reason: string;
  og_image?: string; output_intent?: OutputIntent; cta?: string;
};
```
Closest existing analog to a "relevance score + rationale" (`confidence`, `reason`), but this is for LLM template-generation matching, not content-result relevance.

## D. `NanoPromptBase` — `types/nanoPrompts.ts:1-8`

```ts
export interface NanoPromptBase { id: number; title: string; description: string; prompt: string; imageURL: string; tags: string[]; }
```

## Field inventory across A-D (mandatory-for-render vs. present)

| Field | A (InspRecord) | B (NanoInspirationCardType) | C (TemplateMatch) | D (NanoPromptBase) | Mandatory for current cards? |
|---|---|---|---|---|---|
| id | ✓ string | ✓ string | — (template_id only) | ✓ number | Yes |
| template_id | ✓ | ✓ | ✓ | — | Yes (A, B, C) |
| title | via `locales[loc].title` | via i18n lookup elsewhere | — | ✓ | Yes |
| description | — | ✓ optional | — | ✓ | No |
| image_url | `asset.image_url` | `image_urls[]` | `og_image` optional | `imageURL` | Yes |
| thumbnail/preview_url | `asset.preview_image_url` | `preview_image_urls[]` | — | — | Yes |
| destination_url | **none** (client derives `/nano-template/{template_id}?params#reproduce`) | same derivation | same derivation | derived `/nano-banana-pro-prompts/{id}` | Derived, not stored |
| type/category | `locales[loc].category` | `category` | `output_intent` | — | No |
| tags | ✓ | — | — | ✓ | No |
| language | via `locales` keys | `language: PageLocale` | — | — | No |
| score/rank | score computed transiently, not on type | `rank_score` (business, not query relevance) | `confidence` (0-1) | — | No |
| source | **absent from every type** | absent | absent | absent | N/A — all implicitly "internal" |
| editable/generatable flag | absent on type (closest: `allow_generation` on raw template JSON, `searchTemplateMatch.ts:39`, not on any of A-D) | absent | absent | absent | N/A today |
| action URLs | absent — routes are string-templated in UI code, not carried on the data object | same | same | same | N/A |

## Fields that are structurally internal-only (external results cannot provide them)

- `template_id` / `id` referencing `nano_inspiration.json` / `nano_templates.json` — has no meaning for a non-Curify asset.
- `params` (generation parameters like `character_name`, `art_style`) — external images have no generation parameters.
- `locales` (per-locale authored title/category) — external images have at most a scraped title/snippet in one language.
- `search_aliases` — internal SEO/matching metadata, not applicable.
- `rank_score` (business curation weight) — meaningless for content Curify doesn't own.
- Any derived Curify destination route (`/nano-template/[slug]#reproduce`) — external results have an external destination URL instead.
- `allow_generation` / generatable flag — external content is never directly generatable; at most it can seed a *new* generation via a "make with Curify" flow.

## UI actions that must be disabled for external results

Based on Deliverable 1 §2.8 and the UI card inventory (Explore-agent finding, §8):
- **Remix** (routes to `/nano-template/[slug]?params#reproduce` with real params) — external results have no `template_id`/`params`, cannot remix directly.
- **Download pack** — internal batch-template-specific action, not applicable.
- **Copy prompt** — internal gallery-prompt-specific (`PromptCard.tsx`), no equivalent for external images (no stored `prompt` text).
- **Favorite/Save** — only makes sense for saving a Curify-owned asset to a user's collection; ambiguous for external content (open question, default to disabled at MVP).
- **Edit** — no internal-edit surface for a Google-hosted image at all.

The only actions that make sense for an external result are: **open/click-out** (new tab, to the source URL) and a distinct **"Make with Curify"** CTA that routes back into internal retrieval/generation using the external image's title/alt-text as a new query (per Extension C's design) — this is a *new*, separate workflow, not a reuse of "generate."

## Recommendation: separate card is safer than reusing the internal card

**Recommendation (not existing code):** build a new, distinct external-result card component rather than extending `ExampleImageCard` or `PromptCard`. Reasons:
1. Every existing card assumes a Curify CDN-hosted image (`toCdnUrl`/`CdnImage` helpers) and an internal Next.js route destination. An external image is hotlinked (per Extension C's copyright mitigation — no proxying) and its destination is an arbitrary external URL opened in a new tab — both are foreign to the existing card contract.
2. Reusing an internal card risks accidentally exposing an internal-only action (Remix/Copy prompt/Download) on content that cannot support it — a correctness and trust risk, not just a UX one.
3. A separate component makes the "read-only, discovery-only, not a competing creation surface" distinction (Extension C's framing) structurally enforced rather than conditionally hidden, which is safer against future regressions.

## Proposed normalized union contract (documentation only — no code/type changes made)

```ts
// PROPOSED — NOT IMPLEMENTED. For future design review only.
type HybridSearchResult = {
  result_key: string;                 // stable dedup/react key across sources
  source_type: "internal" | "external_google" | "external_other";

  // internal-only (present only when source_type === "internal")
  internal_result_id?: string;        // = InspRecord.id
  template_id?: string;

  // external-only (present only when source_type starts with "external")
  external_provider?: string;         // e.g. "google_custom_search"
  source_domain?: string;             // e.g. "pinterest.com" — REQUIRED for attribution badge
  attribution_label?: string;         // human-readable "From <domain>"
  safe_search_status?: "safe" | "unknown" | "flagged";

  // shared
  title?: string;
  image_url: string;
  thumbnail_url?: string;
  destination_url: string;            // internal derived route OR external source URL
  original_query: string;
  retrieval_query: string;            // may differ from original_query if a rewrite/path was used
  rewrite_used: boolean;

  // ranking/merge bookkeeping
  rank_before_merge: number;
  rank_after_merge: number;

  // action gating — explicit booleans, never inferred from source_type at render time
  can_open: boolean;
  can_edit: boolean;
  can_generate: boolean;               // true only for internal templates with allow_generation
};
```

This contract is a **documentation artifact for the next design pass**, not a TypeScript change made in this repo. No source file was modified.
