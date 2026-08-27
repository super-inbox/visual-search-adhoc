# Personal Design System Demo — 造物起异包装设计 → 荔泉气泡

Boss Task D-New. This folder demonstrates the full Claude Design "personal design system" workflow:
an existing designer's portfolio → extracted, evidence-backed design rules → a persisted system →
a brand-new brief the portfolio never covered → a generated visual system and demo assets.

**This is a workflow proof, not a production-ready creative deliverable.** The 5 generated assets
are flat/vector renderings (no photoreal image-generation tool was available in this environment) —
see `gallery.html` §8 and `LIMITATIONS_AND_NEXT_STEPS.md` for the full, undisguised accounting.

## Recommended viewing order

1. **`gallery.html`** — open this first. The visual walkthrough of the entire demo: source
   portfolio, extracted rules, new brand brief, new visual system, generated assets, traceability,
   evaluation, and limitations, in one scannable page.
2. **`BOSS_SUMMARY.md`** — a one-page written summary, if you want the story in text instead of
   (or alongside) the gallery.
3. **`FINAL_DEMO_VERDICT.md`** — the candid answer to "did this actually prove the hypothesis, and
   is it ready to show further." Read this before deciding what to do next.
4. **Everything else below** — only if you want to audit a specific claim or dig into how a
   specific decision was made.

## Folder structure

```
personal-design-system-demo/
├── gallery.html                        ← start here
├── BOSS_SUMMARY.md                     ← one-page summary
├── FINAL_DEMO_VERDICT.md               ← candid verdict
├── README.md                           ← this file
│
├── Phase 1 — Portfolio discovery
│   ├── DEMO_SPEC.md
│   ├── PORTFOLIO_CANDIDATES.md
│   └── IMPLEMENTATION_PLAN.md
│
├── Phase 1.5 — Portfolio image acquisition
│   ├── PORTFOLIO_SAMPLE_SELECTION.md
│   └── portfolio/
│       ├── manifest.csv                ← source_images path ↔ work title ↔ URL ↔ attribution
│       └── source_images/work_01_01.jpg … work_10_01.jpg   (10 sampled cover images)
│
├── Phase 2 — Personal Design System extraction
│   ├── PORTFOLIO_SOURCE.md             ← studio/profile attribution, sampling rationale
│   ├── PORTFOLIO_EVIDENCE.jsonl        ← 1 evidence record per sampled work, [A]/[B]/[C]-tagged
│   ├── PERSONAL_DESIGN_SYSTEM.md       ← the 7-rule system, fully evidenced
│   ├── PERSONAL_SYSTEM_VALIDATION.md   ← checks the ruleset against its own evidence
│   └── PERSONAL_SYSTEM_SUMMARY.md
│
├── Phase 3 — New brand + visual system
│   ├── BRAND_BRIEF.md                  ← 荔泉气泡 / Lichuan Sparkling
│   ├── BRAND_VISUAL_SYSTEM.md          ← super-symbol, color, type, SKU system, staging rules
│   ├── BRAND_SYSTEM_TRACEABILITY.md    ← every decision → rule → work ID → transfer type
│   ├── BRAND_SYSTEM_CONSISTENCY_CHECK.md
│   └── ASSET_PLAN.md                   ← spec for the 5 assets before generation
│
├── Phase 4 — Generated assets
│   └── generated_assets/
│       ├── HERO_KEY_VISUAL.png
│       ├── SKU_FAMILY_SHOT.png
│       ├── SOCIAL_POST.png
│       ├── CAMPAIGN_POSTER.png
│       ├── WEBSITE_HERO.png
│       ├── ASSET_MANIFEST.csv          ← per-asset rule/work-ID mapping and status
│       ├── ASSET_GENERATION_NOTES.md   ← intent, deviations, the condensation fix
│       ├── CROSS_ASSET_CHECK.md        ← symbol/type/color/composition consistency, verified
│       ├── canvas_src/                 ← the actual .dc.html source (shared Can + symbol components)
│       ├── prompts/                    ← exact per-asset generation prompts, ready for a photoreal tool
│       └── lichuan-sparkling-brand-system.html   ← the seeded Claude Design canvas file
│
└── Phase 5 — Final evaluation
    ├── EVALUATION.md / EVALUATION.csv  ← 10-dimension scored evaluation
    ├── END_TO_END_TRACE.md             ← 8 concrete portfolio→rule→decision→asset chains
    └── LIMITATIONS_AND_NEXT_STEPS.md   ← demo / productization / rendering / data limitations
```

## What to trust, what to double-check

Every claim in `gallery.html` and `BOSS_SUMMARY.md` is backed by a document in this folder — if a
number, rule, or attribution looks off, the source document named next to it in `gallery.html` is
the place to verify it, not this summary layer.
