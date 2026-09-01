# Portfolio Candidates — Personal Design System Demo

Phase 1 deliverable for boss Task D-New (2026-08-21). This document records every candidate
considered, how each was verified, and why the final primary/backup pair was chosen.

## Method

1. Searched this repo (`visual-search-adhoc`) exhaustively first: `grep -ril "zcool\|behance"`,
   plus every prior inspiration/workflow research directory (`8.8/inspiration-source-pilot`,
   `8.8/workflow-research-5-domains`, `8.12/inspiration-topic-pinterest`,
   `8.14/inspiration-scale`, `8.16/creative-direction-*`, `8.19/*`).
2. Result: **no local single-designer portfolio with 6+ downloaded images exists in this repo.**
   All existing local image corpora (`8.8/inspiration-source-pilot/thumbnails/*`,
   `8.12/.../thumbnails/pinterest/*`, `8.14/inspiration-scale/thumbnails/*`) are Pinterest
   **topic/keyword search results** — each topic folder mixes pins from many different,
   unrelated Pinterest accounts. They are not attributable to one designer's own body of work.
3. The one place this repo already names real individual designers/studios with a Zcool or
   Behance byline is `8.8/workflow-research-5-domains/candidates/*.md` and its paired
   `cases/*/source_metadata.json` — but each of those is a **single case-study write-up per
   designer** (one project, no locally saved images), so none meets the "6+ works" bar on its
   own.
4. Because local material was insufficient, three of those named designers/studios were followed
   to their **live Zcool/Behance profile pages** (fresh `WebFetch`, 2026-08-21) to check whether
   their full profile — as opposed to the one case study already in this repo — has enough
   distinct, consistent work to qualify. This is "new research built on an existing local lead,"
   not an unrelated cold scrape.

No portfolio evidence below is invented. Every title, URL, and work count came back from a live
`WebFetch` of the stated URL on 2026-08-21. Where a claim about visual style is my own reading of
what was fetched, it is labeled as such rather than presented as a platform-provided fact.

---

## Candidate 1 (PRIMARY): 造物起异包装设计 (Zaowu Qiyi Packaging Design)

- **Source:** ZCOOL (站酷) — studio profile `https://www.zcool.com.cn/u/ZNTI2Mjc5ODA=`
  (Guangzhou-based packaging/brand studio; role listed as "Brand Designer")
- **Discovered via:** already a local lead — `docs/daily_report/8.8/workflow-research-5-domains/candidates/PACK-01-zaowuqiyi-fruit-wine.md`
  documents one of their case studies (星河果酒 / Xinghe Fruit Wine) in detail, with the studio's
  ZCOOL profile link surfaced directly from that article's byline.
- **Number of usable works:** **16 distinct projects** visible on the profile page (verified
  2026-08-21), all well above the 6-work minimum. A representative subset of 8 spans the
  studio's range:
  1. Printbelle cross-border e-commerce brand system (logo/VI/packaging)
  2. Sam's Club sunscreen outdoor packaging + PDQ shelf display (with Paradise Umbrella)
  3. Mid-Autumn gift-box packaging (with Greenisland Group)
  4. Facial-tissue "cat paw" flagship-SKU packaging (with Cellox/洁柔)
  5. Innovite maternal/infant-health brand + bottle design
  6. Children's nutrition "forest can" packaging (with Innluoway/英珞维)
  7. "Hawthorn Grandpa" snack packaging — super-symbol visual strategy
  8. 星河果酒 (Xinghe Fruit Wine) — the case already documented locally in PACK-01
- **Available local paths:** **none yet.** Phase 1 only verified titles/URLs/counts via
  `WebFetch`; no images have been downloaded into this repo (see Limitations and
  `IMPLEMENTATION_PLAN.md` for why, and the Phase 2 plan to get real image files).
- **Dominant apparent visual characteristics** (my reading of the fetched titles/descriptions,
  cross-checked against the studio's own stated methodology in PACK-01): a repeatable
  "超级符号" (super-symbol) approach — one dominant graphic/illustrative icon per product,
  scaled large on the pack face; bold, saturated color-blocked backgrounds; bilingual
  Chinese/Latin type pairing; consistent use of gift-box format conventions for
  festival/seasonal SKUs.
- **Strength of consistency:** **High.** All 16 works sit inside one domain (CPG packaging +
  brand identity) and the studio explicitly names its own repeatable method
  ("超级符号，卖点设计，元素构成，原创插画，字体设计，配色设计，板式设计" — per PACK-01), so the
  consistency is not just visual coincidence but a stated house methodology applied across many
  different clients.
- **Limitations:**
  - ZCOOL sits behind an Aliyun WAF that returns a slider-captcha challenge page to scripted
    `curl` requests (confirmed directly, 2026-08-21) — image files cannot be bulk-downloaded by a
    plain HTTP client. `WebFetch`'s markdown conversion reaches the text/title content but returns
    lazy-load placeholder URLs for images, not real CDN links.
  - Only one of the 16 works (Xinghe Fruit Wine) has an existing detailed process write-up in
    this repo; the process depth of the other 15 is inferred from titles/thumbnnail descriptions
    only, not independently read in full.

---

## Candidate 2 (BACKUP): 独角狮设计 (Unicorn Lion Design)

- **Source:** ZCOOL (站酷) — profile `https://www.zcool.com.cn/u/ZNzEyMzA4MDA=`
  (independent designer, Yinchuan; "设计爱好者" / design enthusiast, ~5 years' posted history)
- **Discovered via:** already a local lead — `docs/daily_report/8.8/workflow-research-5-domains/candidates/PACK-04-danjiaoshi-process-overview.md`
  references this designer's ZCOOL packaging-process article; the profile link was surfaced
  directly from that article's byline.
- **Number of usable works:** **11 distinct projects** (verified 2026-08-21), above the 6-work
  minimum. Representative subset of 8 (excluding the one process article and one pure-logo grid
  post):
  1. 元气鸡汤 (energy chicken-soup) brand packaging
  2. 鑫蜀岸足浴 (foot-spa) tri-fold brochure
  3. 饭菜集火锅烧烤食材超市 (hotpot/BBQ ingredient supermarket) tri-fold brochure
  4. 香村农客 logo
  5. 晓鸣农牧 (agriculture/livestock) VI system
  6. 兰熙贡米 (tribute rice) packaging
  7. 30°宁夏大米 (Ningxia rice) packaging
  8. 广夏葡萄酒 (wine) packaging + 马兰花胡麻油 (sesame oil) packaging
- **Available local paths:** **none yet** — same status as Candidate 1; see Limitations.
- **Dominant apparent visual characteristics:** a narrower, more regional niche than Candidate 1
  — Ningxia-region agricultural/food branding (rice, sesame oil, wine, herbal soup), consistently
  packaging + logo + VI for small-to-mid regional food producers, with a plainer, ingredient/
  provenance-forward visual language (product photography or crop/grain illustration rather than
  an abstract super-symbol icon).
- **Strength of consistency:** **Moderate-high.** Consistent domain (regional food/agri
  packaging) and consistent client profile (small regional producers), but less of an explicit,
  named personal methodology than Candidate 1 — the consistency here looks more like "same
  designer serving the same regional market" than "one deliberate signature device."
- **Limitations:** same ZCOOL WAF/lazy-load image-acquisition blocker as Candidate 1. Smaller
  total work count (11 vs. 16) and narrower brief diversity (nearly all food/agri), which slightly
  narrows how far a "new brief" test can push generalization.

---

## Candidate 3 (reported, not selected): Sabrina Young, RGD

- **Source:** Behance — profile `https://www.behance.net/SabrinaYoungRGD` (London, Ontario,
  Canada; Creative Director / Accessible Document Specialist, 20+ years)
- **Discovered via:** already a local lead — `docs/daily_report/8.8/workflow-research-5-domains/candidates/BRAND-03-constellation-rebrand.md`
  and paired `cases/brand_logo_001/` document her Canada Life "Constellation" rebrand case in
  detail; her Behance profile link was surfaced directly from that project page's byline.
- **Number of usable works:** **12 distinct projects visible** (verified 2026-08-21; profile
  pagination suggests more exist beyond the first page). Well above the 6-work minimum.
- **Available local paths:** **one real, downloaded proof image** —
  `/private/tmp/.../scratchpad/sabrina_young_check/constellation_1.jpg` (a client-kit spread from
  the already-documented Constellation project). This file lives in the session scratchpad, not
  in this repo, and was pulled only to confirm Behance is technically scrapable (see below) — it
  is evidence about *feasibility*, not a portfolio asset for this demo, and was not copied into
  `docs/daily_report/8.21/`.
- **Dominant apparent visual characteristics:** professional, systems-oriented corporate brand
  identity work — persona-driven collateral, a recurring structural device ("keyline square over
  photography," per BRAND-03), clean sans-serif type, print + digital application breadth.
- **Strength of consistency:** **Low-moderate for a *personal* design system, specifically.**
  This is the key finding that disqualifies her as primary: each of her 12 projects is built for
  a *different named client* (Canada Life red, CICan's own palette, Limestone District School
  Board's own palette, Rockwell's own palette, etc.), and the actual colors/logos/type in every
  project are constrained by that client's pre-existing brand guidelines, not by Sabrina Young's
  own recurring aesthetic. What repeats across her work is a *methodology* (personas → structural
  device → multi-format rollout), not a transferable visual signature (palette, type, motif) the
  way Candidates 1 and 2 show. Since the demo's premise is extracting a *visual* system that can
  be reapplied to a new brief, an in-house/agency generalist whose look is dictated per-client is
  a weaker fit than an independent studio whose look is closer to a personal signature.
- **Why still worth reporting:** Behance has **no comparable scraping blocker** — a plain `curl`
  against a Behance project page returns full HTML with direct, real CDN image URLs
  (`mir-s3-cdn-cf.behance.net/project_modules/...`) with no captcha/WAF challenge (confirmed
  2026-08-21). If a future iteration of this demo needs frictionless bulk image acquisition, a
  Behance-hosted candidate would be by far the easier path technically — the tradeoff is against
  visual-system purity, not access.

---

## Selection

- **Primary: 造物起异包装设计 (Zaowu Qiyi Packaging Design)** — largest verified work count (16),
  strongest documented single methodology ("super-symbol"), and the one candidate with an
  existing, already-vetted detailed process write-up in this repo (PACK-01) to cross-check
  extracted rules against.
- **Backup: 独角狮设计 (Unicorn Lion Design)** — same platform and same acquisition approach as
  primary (so the Phase 2 pipeline built for one works for the other unchanged), sufficient work
  count (11), coherent though narrower visual niche.
- **Sabrina Young kept as a documented alternative, not backup**, specifically because her
  portfolio's consistency is methodological rather than visual — the wrong shape of evidence for
  a demo about extracting a reusable *visual* system.
