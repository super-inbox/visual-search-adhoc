# Hybrid Search — External Result Data Contract (Proposed, Documentation Only)

No external-result type exists in the codebase today (confirmed — see Internal Result Contract doc §"structurally internal-only" and the Current Architecture doc §2.5-2.6). Everything in this document is a **design proposal for future review**, not a code change.

## Design goals

1. Never let an external result silently pass through code paths written for `InspRecord`/`NanoInspirationCardType` — type-level separation prevents accidental exposure of internal-only actions.
2. Preserve the external destination URL exactly as returned by the provider (no rewriting/redirect through Curify) — required both for the "read-only, click-out" product framing (Extension C) and to avoid any appearance of endorsing/hosting third-party content as Curify's own.
3. Carry enough fields for attribution (source domain badge), safety (safe-search status), and instrumentation (provider, retrieval query, rank) without inventing fields the provider can't actually supply — see Provider Options doc for what Google Custom Search JSON API can and cannot return.

## Proposed shape

```ts
// PROPOSED — NOT IMPLEMENTED.
type ExternalSearchResult = {
  result_key: string;               // hash of destination_url, for dedup/react key
  source_type: "external_google" | "external_other";
  external_provider: string;        // "google_custom_search" | future providers
  source_domain: string;            // parsed from destination_url host — REQUIRED, always rendered as a badge
  title?: string;                   // provider-supplied title/snippet, may be absent or low-quality
  image_url: string;                // hotlinked, never proxied/re-hosted
  thumbnail_url?: string;           // if provider supplies a separate thumbnail
  destination_url: string;          // the original external page URL, UNMODIFIED
  attribution_label: string;        // derived, e.g. "From pinterest.com" — always shown
  safe_search_status: "safe" | "unknown" | "flagged"; // from provider's safe-search field if available, else "unknown"

  original_query: string;
  retrieval_query: string;          // query actually sent to the provider (may be the LLM-rewritten query per Extension C)
  rewrite_used: boolean;

  rank_before_merge: number;        // position in the provider's own result order
  rank_after_merge: number;         // position after the merge policy is applied (Deliverable 9)

  can_open: true;                   // always true — click-out is the one guaranteed action
  can_edit: false;                  // ALWAYS false — hard invariant, not a runtime decision
  can_generate: false;              // ALWAYS false for the raw card — "Make with Curify" is a SEPARATE CTA/workflow, not this flag
};
```

## Why `can_edit`/`can_generate` should be hard-coded constants, not computed booleans

Unlike the internal contract (where `can_generate` genuinely varies per template), an external result should never be directly editable or directly generatable — there is no generation-parameter payload behind a scraped image. Making these **literal `false`/`true` constants in the type**, rather than values a merge/ranking bug could accidentally flip, is a deliberate safety choice: it makes "external results can't trigger internal-only actions" a type-level invariant instead of a behavior that depends on correct downstream logic every time. This directly reduces the "misleading UI" risk flagged in the Risk Register.

## Which internal-only fields external results structurally cannot provide

(Same list as the Internal Result Contract's "internal-only fields" section — restated here for completeness of this deliverable per the task brief):
- `template_id`, `internal_result_id`, `params` (generation parameters)
- `locales` (multi-locale authored title/category)
- `search_aliases` (internal SEO metadata)
- `rank_score` (business curation weight)
- `allow_generation` / any generatable flag with a `true` value
- A Curify-internal destination route

## UI actions that must be disabled for external results (restated for this deliverable)

open/click-out: **allowed**. Everything else — Remix, Edit, Download pack, Copy prompt, direct Generate, Favorite (open question, default disabled at MVP) — **disabled**. The only additional allowed action is the distinct **"Make with Curify"** CTA, which is not a flag on this contract but a separate UI element that triggers a *new* internal search/generation flow using `title`/`image_url` alt-text as a fresh `retrieval_query` — never a mutation of the external card's own state.

## Separate card component — restated recommendation

Confirmed in the Internal Result Contract doc: build a **new, distinct external-result card**, not a variant of `ExampleImageCard`/`PromptCard`. This document's hard-coded `can_edit: false; can_generate: false` constants reinforce that recommendation — a shared card component would need runtime conditionals to hide internal-only buttons, which is strictly more failure-prone than a component that structurally never renders those buttons at all.

## Fields explicitly marked unresolved pending provider selection

Per the read-only constraint (no external API calls made in this audit), the following are **provider-dependent and unverified**:
- Whether `safe_search_status` can be populated with real granularity, or only a boolean "safe search was applied to this query" — see Provider Options doc.
- Whether `source_domain` is reliably present for every result type Google Custom Search Image returns (some results may be redirect/CDN URLs where the "true" source domain requires an extra parse step).
- Whether `title` is consistently non-empty (image search snippets are often thin or auto-generated).

These are marked **provider unresolved** and must be validated against real (mocked/sample, per Phase 3 of the rollout plan) API responses before finalizing the type — not assumed from this document alone.
