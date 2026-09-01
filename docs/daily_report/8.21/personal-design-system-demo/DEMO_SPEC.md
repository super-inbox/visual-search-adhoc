# Demo Spec — Personal Design System

Boss Task D-New, Phase 1 (2026-08-21). Defines what this demo is, the workflow it must
reproduce, the chosen portfolio, and the new brief used to test generalization.

## What we're reproducing

Not the Claude Design 2.0 UI — the underlying workflow:

```
existing visual/design work
  → extract reusable design-system rules
  → persist those rules
  → use the system to generate new, stylistically consistent outputs
```

Concretely, four stages:

1. **Source portfolio** — a real designer's existing body of work (Zcool or Behance), used only
   as *evidence*, never modified or misrepresented.
2. **Extraction** — read across that portfolio and write down the recurring, reusable rules: color
   palette, typography, layout/composition patterns, recurring motifs/devices, format
   conventions. This is a claim about *what repeats*, not a description of any single piece.
3. **Persistence** — the extracted rules get written to a standalone spec file (not just held in
   a chat transcript) so they can be reused independently of the extraction session.
4. **Generation** — a brand-new brief (never one of the designer's own projects) gets run through
   the persisted spec to produce new assets. Success is judged by whether the output reads as
   "from the same design system" despite being a genuinely new product/category.

## Portfolio selection (see `PORTFOLIO_CANDIDATES.md` for full evidence and rationale)

- **Primary:** 造物起异包装设计 (Zaowu Qiyi Packaging Design) — ZCOOL, Guangzhou packaging/brand
  studio, 16 verified works, a stated repeatable "超级符号" (super-symbol) methodology.
- **Backup:** 独角狮设计 (Unicorn Lion Design) — ZCOOL, Yinchuan, 11 verified works, regional
  food/agri packaging.
- Both were reached via leads already present in this repo's prior workflow research
  (`8.8/workflow-research-5-domains`), then independently re-verified live on 2026-08-21.

## New brand brief (generalization test)

**Brief:** *"荔泉气泡 (Lichuan Sparkling)" — a plant-protein sparkling water brand launching in
first-tier Chinese cities, targeting young urban professionals who want a "healthy indulgence"
alternative to soda. Deliverable: a brand name/logo direction, a recurring super-symbol-style
graphic device, a 330ml can + gift-box packaging direction, and one social-media launch key
visual.*

This brief was deliberately chosen because it sits **outside every one of the 16 works** on the
primary studio's verified profile: none of their listed projects are a beverage can, a carbonated
drink, or a plant-protein product (their portfolio covers wine bottles, gift boxes, tissue,
maternal/infant products, snacks, apparel, and sunscreen — no canned beverages at all). It stays
inside the studio's core competency (CPG packaging + brand identity for a Chinese consumer
market), so the test isolates one variable: *does the extracted visual system transfer to an
unseen product category*, rather than testing an unrelated domain jump the studio has no
demonstrated competency in.

## Why this is a good generalization test

- **Same competency, new category.** Packaging + super-symbol branding is exactly what the
  studio does; sparkling water is a category they have zero documented prior work in — so a
  convincing result demonstrates rule transfer, not memorized-project recall.
- **Falsifiable.** If the generated output either (a) fails to read as visually related to the
  studio's known work, or (b) is clearly a near-copy of one specific existing project (e.g. just
  re-skinning the Xinghe Fruit Wine bottle), that is a legible failure mode, not a fuzzy judgment
  call.
- **Bilingual/format constraints carry over.** The new brief keeps the bilingual Chinese/Latin
  typography and gift-box packaging convention seen across the primary portfolio, so the
  extracted rules have concrete surfaces to apply to (not just "similar color mood").

## Explicit scope boundaries for this phase

- Phase 1 (this document + `PORTFOLIO_CANDIDATES.md` + `IMPLEMENTATION_PLAN.md`) is
  **discovery and definition only** — no design-system extraction, no persisted spec file, and no
  generated assets yet.
- Work stays inside `visual-search-adhoc`, specifically under
  `docs/daily_report/8.21/personal-design-system-demo/`. `curify-frontend` is not touched.
- No portfolio evidence is fabricated. Every designer, URL, and work count in
  `PORTFOLIO_CANDIDATES.md` was independently verified via live `WebFetch` on 2026-08-21, not
  assumed from memory or invented for narrative convenience.
- Nothing in this phase is committed to git.

## Open blocker carried into Phase 2

ZCOOL (both primary and backup candidates' host platform) sits behind an Aliyun WAF that blocks
scripted `curl` image downloads with a slider-captcha challenge, and its images are lazy-loaded
(not present as real URLs in a plain HTML fetch). Acquiring real local image files for the
primary/backup portfolios will require a real browser session (e.g. Claude-in-Chrome) rather than
a plain HTTP client. See `IMPLEMENTATION_PLAN.md` for the concrete Phase 2 plan.
