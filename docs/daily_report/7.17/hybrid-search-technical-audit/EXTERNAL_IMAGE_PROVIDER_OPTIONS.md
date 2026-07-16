# External Image Search Provider Options

**No external service was called. No HTML was scraped. This is a desk evaluation only**, cross-checked against what the repository already has evidence for (Extension C's stated intent, package.json dependencies, absence of `.env.example`).

## Repository evidence check (per task requirement — do not claim availability without evidence)

- Full-repo grep for `customsearch`, `serpapi`, `SERP_API`, `GOOGLE_CSE`, `cse.google` → **zero code hits**.
- `.env.example` → **does not exist** in the repo. No documented env-var naming convention for any search-provider key.
- `docs/eval-framework-visual-search-benchmark-2026-06-14.md:250` names "**Google Custom Search API (Image search)**" as the intended source for Extension C — this is a **stated intent in a strategic doc**, not evidence of a provisioned account, key, or quota.
- `@google/genai` (package.json, v1.48.0) is present but used exclusively for image *generation* (`GoogleGenAI, Modality` in `app/api/illustrator-demo/generate/route.ts`, `app/api/progseo-demo/generate/route.ts`) — **not** the Custom Search JSON API, and not evidence a Google Cloud/Search Console project exists for search grounding.

**Conclusion: provider unresolved. Credentials unresolved. Cost unresolved. Quota unresolved.** Nothing in this repository confirms an active, billable Google Custom Search API integration exists or has been provisioned. Any implementation must start with a compliance/credentials provisioning step (Rollout Plan, Stage 2), not assume access.

---

## Option 1 — Google Programmable Search Engine / Custom Search JSON API (Image search)

| Dimension | Assessment |
|---|---|
| Official/compliant access | Yes — this is Google's documented, ToS-compliant API for programmatic search. Requires a Google Cloud project + Custom Search Engine (CSE) configuration + API key. |
| Image URL availability | Yes — `image.link` field returns a direct image URL per result. |
| Original page URL availability | Yes — `link`/`displayLink` return the hosting page URL and domain. |
| Source-domain availability | Yes — `displayLink` gives the domain directly; no extra parsing needed for the common case. |
| Title/snippet availability | Yes, but often thin/auto-generated for image results — quality UNKNOWN without a live sample (no live calls made in this audit). |
| Safe Search support | Yes — `safe=active\|off` query param; granularity is binary (filtered or not), not a graded score. |
| Pricing model | Publicly documented as a paid-per-query API beyond a small free daily quota (exact current figures UNRESOLVED — pricing pages change; must be re-verified at provisioning time, not assumed from training data). |
| Quota | Configurable via Google Cloud Console; default free tier is small (order of ~100 queries/day per public docs, UNVERIFIED for current terms). Should be treated as a hard cost/throughput constraint requiring the thin-results gate (already exists at `LOW_RESULT_THRESHOLD=5`) to bound call volume. |
| Expected latency | UNRESOLVED without a live call — desk estimate only, typical SERP-API-class latency is in the few-hundred-ms range; must be measured in Phase 3 (mocked/sample validation) before any timeout budget is finalized. |
| Caching constraints | Google's ToS historically restricts caching/storing search results beyond short-term display — **must be reviewed by legal/compliance before implementing any cache duration**; Extension C's proposed 7-day cache is a design intent, not a confirmed-compliant policy. |
| Attribution requirements | Google's terms typically require displaying results as provided, with the source clearly attributable — consistent with the "hotlink + show source domain badge" design already proposed. |
| Hotlink/broken-image risk | Real — hotlinked third-party images can 404/change/be taken down at any time; no Curify control over uptime. Requires client-side broken-image fallback handling (new UI work, not yet designed in detail here). |
| Implementation complexity | Low-to-medium — a well-documented REST API, single API key, JSON response. The main complexity is compliance review + the new merge/rank/UI layer, not the API call itself. |
| Vendor dependency | High — single point of failure on Google's API availability/pricing/ToS changes; mitigated by the "failure must never remove internal results" guarantee (Deliverable 10). |
| Suitability for MVP | **Preferred**, contingent on legal/compliance sign-off and real quota/cost confirmation — matches the existing Extension C intent and requires no scraping. |

## Option 2 — Approved commercial SERP/Image-Search API provider (e.g., a licensed aggregator)

| Dimension | Assessment |
|---|---|
| Official/compliant access | Depends entirely on the specific vendor's ToS and Curify's contract with them — **no such vendor is referenced anywhere in this repository**, so this is a hypothetical category, not a concrete option. |
| Image/page/domain/title availability | Typically yes, often richer metadata than raw Google CSE (multi-source aggregation) — UNVERIFIED, no vendor named in repo. |
| Safe Search | Varies by vendor — UNVERIFIED. |
| Pricing/quota | Typically usage-based, often more expensive per-query than direct Google CSE since it's a reseller/aggregator margin — UNVERIFIED, provider unresolved. |
| Latency | Often higher than a direct API (proxy hop) — UNVERIFIED. |
| Caching/attribution | Vendor-specific ToS — would need its own compliance review. |
| Implementation complexity | Similar to Option 1 once a vendor is chosen. |
| Vendor dependency | Adds a second vendor relationship on top of (or instead of) Google directly. |
| Suitability for MVP | **Acceptable fallback** only if Option 1 is blocked by quota/compliance/cost — not recommended as a first choice given zero existing evidence of vendor selection or contract. |

## Option 3 — Existing internal company service

Full-repo search for any internal proxy/service that already wraps external image search → **none found**. `services/api.ts` (`apiClient`) talks to a real Curify backend, but only for tracking and gallery-prompt tag lookups (`nanoPromptsService.getNanoPromptsByTag`) — no search-provider passthrough endpoint exists. **Option ruled out for MVP — no such service exists today.**

## Option 4 — Other compliant image-search APIs already used/documented in the codebase

None found beyond `@google/genai` (generation-only, not search). **No other candidate exists in-repo.**

## HTML Scraping of Google Images or any other search engine

**Not recommended. Explicitly ruled out**, consistent with the hard safety constraints of this audit and with the existing `docs/eval-framework-visual-search-benchmark-2026-06-14.md` framing of Pinterest scraping ("Playwright against pinterest.com... aggressive bot-detection... doesn't scale, gets fragile fast," lines 37-41) — the same reasoning applies transitively to scraping Google Images: ToS violation risk, fragility, ban risk, and no legal/compliant path to production use. Any future implementation must use an official API, never scraping.

---

## Recommendation hierarchy

1. **Preferred:** Google Custom Search JSON API (Image search), Option 1 — matches existing Extension C intent, official/compliant, well-documented. **Contingent on:** legal/compliance sign-off on caching + attribution terms, and real pricing/quota confirmation via account provisioning (Rollout Plan Stage 2) — none of which exist yet in this repo.
2. **Acceptable fallback:** a licensed SERP/image-search aggregator (Option 2), only if Option 1's quota or pricing proves unworkable at Curify's expected query volume — no specific vendor evaluated, purely a category placeholder.
3. **Not recommended:** any form of HTML scraping of Google Images, Pinterest, Bing, or other search engines (explicitly out of scope, ToS-violating, fragile, previously documented as rejected for Pinterest in this same codebase's docs).

## Explicit unresolved items (per task requirement — do not assume)

- Provider account/project: **unresolved** — no evidence of provisioning.
- Credentials: **unresolved** — no `.env.example`, no key naming convention.
- Cost: **unresolved** — current published pricing must be re-verified at provisioning time; not assumed here.
- Quota: **unresolved** — same.
- Real latency: **unresolved** — requires a mocked/sample validation pass (Rollout Plan Stage 3) before any timeout value is finalized in the Failure/Cache/Cost spec (Deliverable 10), where only *ranges* are proposed for exactly this reason.
