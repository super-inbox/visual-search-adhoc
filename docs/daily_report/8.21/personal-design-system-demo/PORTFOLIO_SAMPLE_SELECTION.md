# Portfolio Sample Selection — Phase 1.5

Records which of the primary portfolio's 16 verified works were sampled for real image
acquisition, why, and exactly what acquisition limitations shaped the final set. All images live
in `portfolio/source_images/`, indexed by `portfolio/manifest.csv`.

## Primary portfolio

造物起异包装设计 (Zaowu Qiyi Packaging Design) — ZCOOL
`https://www.zcool.com.cn/u/ZNTI2Mjc5ODA=.html`

## Acquisition method actually used

Per instruction, only a normal (anonymous, logged-out) `claude-in-chrome` browser session was
used — no WAF/anti-bot evasion, no credential entry. Method: navigate to each work's real URL,
let the page load, scroll to the work's cover/hero image, and take a full-viewport screenshot.
Full findings on what did and didn't work are in `IMPLEMENTATION_PLAN.md`; summarized here:

- The ZCOOL Aliyun WAF that blocks plain `curl` (documented in Phase 1) **does not block a real
  browser session** — every work page loaded normally without any captcha challenge.
- Each work's **cover/hero image reliably renders** in this session.
- Scrolling *deeper* into the same work's long-scroll case study (to reach the 2nd/3rd/4th
  images) produced blank white content in the vast majority of attempts, across multiple
  techniques (mouse wheel, instant `scrollTo`, fine-grained stepped scroll with waits, precise
  per-image targeting using measured DOM coordinates) — even though the browser's own DOM
  reported those images as fully loaded (`img.complete === true`, correct non-placeholder
  `naturalWidth`/`naturalHeight`). This looks like a lazy-render/paint quirk specific to this
  automated session, not a deliberate access control (contrast with the one clear login gate
  below). It was not solved despite substantial troubleshooting, so — per your explicit
  instruction to stop rather than keep working around access limits — the scope was narrowed to
  **1 real image per work (the cover/hero shot)** rather than the 2-4 originally requested.
- One separate, different phenomenon: the **Printbelle** work
  (`https://www.zcool.com.cn/work/ZNzQwMDE0NzI=.html`) had its cover image itself gated — clicking
  it redirected straight to ZCOOL's login page (`passport.zcool.com.cn`). This is a genuine
  per-work login wall (consistent with ZCOOL's own "登录站酷，高清原画质看" messaging), not the
  rendering quirk above. Printbelle was **dropped from the sample** and replaced with 英珞维
  儿童营养森林罐 to keep the set at 10 works.

## The 10 works sampled (of 16 verified)

Selected for category/format diversity across the studio's "超级符号" (super-symbol) methodology,
while staying inside works that actually rendered anonymously:

| # | Work | Category | Why included |
|---|------|----------|---------------|
| 1 | 摘要·酌古 (wine bottle) | Spirits/bottle packaging | Traditional-motif "super-symbol" (dragon/cloud illustration) at its most elaborate — anchors the high end of the studio's illustrative-symbol range. Also the work already documented in this repo's prior research (`8.8/workflow-research-5-domains` lineage led to this studio). |
| 2 | 天堂伞 sunscreen (PDQ) | Outdoor/personal-care packaging | Different format entirely (soft-goods + shelf-display PDQ unit), softer photographic (non-illustrated) treatment — tests whether "super-symbol" language holds outside bottles/boxes. |
| 3 | Artevive (brand symbol upgrade) | Generic brand/stationery-adjacent | The most abstract, non-CPG-specific example — a pure logo/symbol-system case, useful for isolating the studio's *symbol design logic* apart from any specific packaging substrate. |
| 4 | 元气女孩 yoga apparel | Apparel/soft-goods brand | Only non-edible, non-personal-care category in the sample — tests whether the studio's palette/box conventions generalize to textile retail packaging. |
| 5 | CreativeArt hairbrush | Beauty-tool packaging | Bold flat-color + circular logomark treatment, different from the illustrative/photographic works — broadens the symbol-style range sampled. |
| 6 | 绿岛集团 Mid-Autumn gift box | Festival/seasonal gift packaging | Represents the studio's gift-box format convention explicitly, with dedicated seasonal color logic (burgundy/orange). |
| 7 | 洁柔 cat-paw tissue | FMCG/tissue packaging | Character-illustration-led (cat paw), lighter/playful palette (periwinkle) — contrasts with the more premium/traditional works, testing range of tone. |
| 8 | Innovite maternal/infant | Health/wellness packaging, bottle format | Captured in real retail/shelf context (not a studio render) — different presentation mode from the others, useful cross-check that the visual language holds in situ. |
| 9 | 山楂爷爷 snack | Snack/FMCG packaging | Explicitly named by the studio as a "超级符号视觉策略" (super-symbol visual strategy) case — the most direct, named evidence for the core methodology claim. |
| 10 | 英珞维 children's nutrition | Children's health/FMCG, novelty bottle shape | Playful sculptural bottle-cap form (tree shape) — another format variant; image only partially rendered (see Limitations), included anyway since the visible left half is real, diagnostic content, not filler. |

**Not sampled from the 16:** Printbelle (login-gated, see above); 造物起异2025年终总结 and
品牌走对第一步有多重要 (both self-published reflective articles about the studio itself, not
client project case studies — excluded as they wouldn't contribute product/packaging visual
evidence); 中国品牌走向世界 (same reason); 轻食餐饮 and 漫步者 gift box (not sampled purely for
time — the 10 above already cover the intended category/format spread without them; they remain
good candidates if Phase 2 needs more evidence).

## What visual evidence the sample contributes (for Phase 2 extraction)

Across the 10 images: bilingual Chinese/Latin typography pairing (works 1, 3, 5, 10), a
recurring dominant-graphic/"super-symbol" placement strategy (works 1, 5, 9, 10 most clearly),
saturated color-blocked backgrounds spanning distinct seasonal/brand palettes (burgundy/gold for
1 and 6, sage green for 2, lime/purple for 5, periwinkle for 7, green for 8 and 10, lavender for
4), and both studio-rendered mockups (1, 3, 4, 5, 6, 7, 9, 10) and real in-context photography (2,
8) — giving Phase 2 evidence for both the "designed" and "as-manufactured" look of the studio's
output.

## Acquisition limitations (honest accounting)

- **9 of 10 images are single full-viewport screenshots of each work's cover/hero shot only** —
  not the 2-4 images per work originally requested. Deeper case-study images (construction detail,
  color-proof shots, multi-SKU lineups, etc.) were not acquired; see the rendering-quirk
  explanation above.
- **Work 10's image is partial** — the right half of the captured frame did not paint (blank),
  so only the left portion (the tree-shaped bottle cap and wordmark) carries real visual content.
- **Work 9's "hero" position differs structurally** — its case study opens with a text section
  ("项目背景") before the first image, so the captured frame is not literally the top-of-page
  cover the way works 1-8 and 10 are; it's still the same work's first real product image.
- **Resolution is full-viewport screenshot resolution (1194×650), not the source image's native
  resolution** — sufficient to read color and layout/type composition, but not for pixel-level
  color sampling. If Phase 2 needs exact hex values, that would require either a logged-in session
  (to reach ZCOOL's stated "高清原画质" / HD original quality) or the user manually saving
  higher-resolution originals.
- All 10 source URLs, work titles, and the studio attribution are recorded in `manifest.csv` and
  were each independently re-verified as real, live ZCOOL pages during this session
  (2026-08-21) — none of the above limitations involve fabricated or substituted imagery.

## Validation performed

- Every `local_image_path` in `manifest.csv` resolves to a real file under
  `portfolio/source_images/` (checked via direct file existence test).
- All 10 image files have distinct MD5 checksums — no duplicate screenshot is standing in for two
  different works.
- No files outside `docs/daily_report/8.21/personal-design-system-demo/` were created or modified
  this phase.
