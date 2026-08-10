# Built pipelines vs. the 5 demo storyboards — what we can actually learn

Compiled 2026-08-10, from the **shipped pipeline code**, not from the videos.

The B3 baseline records `REPOSITORY_CONFIRMED: None` for all five domains — Phase 0
audited data structures, not implementation. That gap cuts both ways: several
storyboard scenes tagged `NEEDS_VALIDATION` are **already built** (so the open
question is answered), and several scenes are **genuinely missing** (so they are
real, actionable gaps). This doc closes the first set and prioritises the second.

Code inspected:
`curify-studio/dev/jayw/video_pipelines/{ip_to_video,brand_to_video,portrait_to_designset}`,
`dev/jayw/design-agent-v0/factory/sticker_exporter.py`,
`dev/jayw/curify-project-video-generation/ecommerce_workflow_variant`,
`curify-frontend/docs/learning-pack-output-template-spec.md` + the shipped
`cartoon-*` learning-card templates, `curify-frontend/lib/topic_workflows.ts`,
`/tools/packaging-mockup`.

---

## A. Storyboard open questions that are ALREADY ANSWERED by shipped code

| Storyboard | Scene | Their status | Reality |
|---|---|---|---|
| packaging | 4 — "See it fold" (3D structural verification) | `NEEDS_VALIDATION`, called **the domain's single highest-priority open question** | **BUILT.** `/tools/packaging-mockup` folds a flat dieline into a 3D render. It reads true W×H×D out of the `.ai` rather than assuming a cube — the 仁寿 case is 117 × 114 × 39 mm, a flat box. Documented in `curify-frontend` `project_packaging_mockup`. |
| packaging | 1 — dimensional/structural input as a distinct modality | `NEEDS_VALIDATION` | **CONFIRMED, and it is the hard part.** Enforcing real dimensions is the known failure mode: prompt-only generation renders a cube. Now shipped as step 4 of the `/topics/packaging` ladder. |
| merch | 3 — print-readiness (CMYK / bleed / dpi) | `MANAGER_MEETING_CONFIRMED`, implementation `UNKNOWN` | **BUILT, but in a different tool.** `sticker_exporter.py` emits a production ZIP: `01_artwork.png` (transparent), `02_cutline.svg` (mm-accurate CutContour), `03_artwork_cmyk.pdf`, `04_preview.png`, `05_spec.pdf`. ⚠️ **Spec mismatch: the exporter is 300 DPI; the storyboard says 600 dpi.** One of the two is wrong — resolve before either is demoed. |
| ecommerce | 6 — try-on | `NEEDS_VALIDATION` | Template exists (`ai-outfit-try-on-poster`, generation-enabled) and is step 3 of the shipped `product` ladder. Not wired into the ecommerce *video* pipeline. |

**Highest-value feedback to the research:** the packaging domain's #1 unknown is
already shipped. Re-rating it changes the domain's whole posture from "does Curify
even do this?" to "this is the differentiator."

---

## B. Storyboard steps we genuinely DON'T do — ranked by value/effort

### 1. Completeness contract for e-commerce ⭐ highest value
Storyboard ecommerce S4, `EXTERNAL_SOURCE_CONFIRMED`, `HIGH`: a real detail page
needs **≥7 images across 4 categories**, mandatory white-background shot, ≥60%
product-body composition, 3:4 ratio — shown as "7 of 7 — complete set".

Ours emits **4 style looks with no completeness definition at all**. This is the
single most concrete gap in the whole comparison: it converts an aesthetic output
("some nice images") into a **verifiable contract** ("your listing is complete"),
which is also a checkable acceptance test. Same shape as the print-spec validator
already scoped in POD-B1.

### 2. Raw fact → consumer-benefit translation
Storyboard ecommerce S2, `HIGH`. User types "waterproof"; the pipeline renders
"worry-free outdoor use". We do no copy structuring anywhere — our ecommerce video
carries style labels only. Cheap (one LLM step), and it is the difference between a
picture generator and something that structures the *selling message*.

### 3. Per-format recomposition, not resize ⭐ strongest cross-domain finding
Independently confirmed in **merch + brand + packaging** (merch S4, brand S5).
Recompose per target aspect ratio — vertical phone case, square magnet, horizontal
postcard — repositioning elements rather than stretching or cropping.

We do the naive thing: one artwork, same composition, applied across t-shirt/tote/mug.
I hit this exact failure on 2026-08-07 — landmark merch printed as a tiny flat graphic
because the mockup reuses a single reference. I patched it by switching the reference
to the season grid, but that is a workaround; **per-format recomposition is the real
fix and is not implemented.**

### 4. Generate N variants scored against named criteria
Packaging S2 (`HIGH`), echoed in brand S2. Generate 3–4 concepts, each visibly scored
against named criteria (shelf impact / clear communication / brand fit).

We generate variants (brand_to_video explores 3 directions) but **score nothing**.
Scoring is what makes a variant set decision-ready instead of a gallery — and it is
the natural place for a judge/eval layer we already have precedent for in the routing
eval work.

### 5. Education: three refinements, all cheap and all real
Our shipped pack is cover → vocabulary → quiz → mini-script → concept map → reading card.

- **Lead with a STORY, not a cover.** Their step 1 is an illustrated story/episode that
  *embeds the target vocabulary*; ours is a decorative cover poster. Theirs is
  pedagogically stronger — the story is where the words come from. Our cover carries no
  teaching load.
- **Cap word cards to 3–5.** Cited principle: 3±2 working-memory chunks for ages 3–7.
  **We generate 8.** A one-line prompt change.
- **Quiz each word on three dimensions — pronunciation, meaning, written form.** Ours
  tests meaning and written form (MC / true-false / fill-blank) but **never pronunciation**,
  despite our already having TTS and a pinyin toolchain.

### 6. Rights-awareness tip (merch S5)
Tagged `NEEDS_VALIDATION` / product-policy. Flagging it anyway because we have a *live*
instance, not a hypothetical: `project_word_scene_shinchan_ip` is an open TODO about a
shipped batch containing a trademarked character, and the same question came up building
the kids-show learning packs. A small non-blocking notice is cheap insurance.

---

## C. Worth stealing: the evidence discipline itself

The storyboards carry `SOURCE_OF_WORKFLOW_IDEA`, `EVIDENCE_CONFIDENCE` and a
`TAG` (`EVIDENCE_BACKED` / `PRODUCT_PROPOSAL` / `NEEDS_VALIDATION`) per scene, plus an
explicit **"scenes deliberately not included"** section explaining what was rejected and
why. The education storyboard refusing to import a live-teacher video feature from a
`PARTIAL`-rated source is exactly the right call.

Our pipeline docs assert capability flatly with no confidence marking. Adopting per-claim
confidence tags in `tool-inventory.md` would make the difference between "built and
verified", "built, unverified" and "proposed" legible — a distinction that has already
bitten us (packaging's #1 unknown was shipped months ago and nobody in the research knew).

---

## D. Suggested order

1. **Re-rate packaging S4 → BUILT** in the research (one-line fix, changes the domain read).
2. **Resolve the 300 vs 600 DPI conflict** before any merch demo.
3. **Ship the e-commerce completeness contract** — highest value, and testable.
4. **Education: story-first, 3–5 word cap, pronunciation in the quiz** — a day's work total.
5. **Per-format recomposition** — the biggest build, but the strongest cross-domain evidence.
6. **Criteria scoring on variant sets** — pairs naturally with 5.
