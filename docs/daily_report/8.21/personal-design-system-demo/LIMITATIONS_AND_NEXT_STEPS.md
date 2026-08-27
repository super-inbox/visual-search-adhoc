# Limitations and Next Steps

Four categories, kept separate deliberately: a demo-scope issue, a productization issue, a
rendering-capability issue, and a data-acquisition issue are different kinds of problems with
different fixes — conflating them would misdirect whoever picks this up next.

## A. Demo limitations

These are scope choices made for this demo specifically, not fundamental blockers.

- **Only 10 of the studio's 64 total uploaded works were sampled**, and only 16 of those 64 were
  even individually verified by title/URL (`PORTFOLIO_SOURCE.md`). A larger sample could surface
  more or different recurring rules.
- **Only 5 asset types were generated**, covering hero/family/social/poster/web touchpoints but not
  retail POS, e-commerce listing, or motion (`EVALUATION.md` §G).
- **One human decision checkpoint** (Phase 1.5's image-acquisition-depth question) means this
  workflow is not yet a single unattended pipeline — a real product version would need a default
  policy for that decision rather than asking each time.
- **The condensation inconsistency in the first generation round** was a real execution miss,
  caught and fixed only because this evaluation loop included an explicit cross-asset check step —
  a production pipeline would need that check built in as a gate, not a follow-up request.

## B. Productization limitations

These would need to be solved before this could be an actual internal Curify feature, independent
of any specific demo run.

- **No automated portfolio→profile matching**: this demo manually identified the studio's ZCOOL
  profile from a lead already in this repo's prior research. A real feature needs to go from "a
  user's portfolio URL" to "verified profile + sampled works" without a human pre-supplying the
  lead.
- **No automated rule-confidence tuning**: the HIGH/MEDIUM thresholds (3 works / 2 works) were
  fixed by task instruction here. A real system would need this calibrated against how many works
  are actually available and how visually consistent a given creator's output really is — 3 works
  is a low bar for some categories and an unreachable one for others.
- **No user-facing review/approval step**: nothing in this pipeline currently asks the *portfolio
  owner* (the actual designer whose work was sampled) to confirm the extracted system reads as
  true to their own style — that's a real product/trust requirement, not just a technical one.
- **No mechanism for the extracted system to *evolve*** as a designer publishes new work — this
  demo is a one-shot extraction, not a maintained profile.

## C. Rendering/image-generation limitations

**Current outputs are flat/vector proxies. Photoreal CGI has NOT been demonstrated.**

- No photoreal text-to-image or diffusion-model tool was available in this session — only the
  `design` skill's HTML/CSS/SVG canvas renderer. Every PNG in `generated_assets/` is a browser
  screenshot of that canvas, not a photoreal product render (`ASSET_GENERATION_NOTES.md`).
- The one asset meant to be *real photography* (`SOCIAL_POST`) is a flat illustration instead — a
  medium substitution, not a quality-degraded version of the same medium.
- Exact photoreal generation prompts were preserved for all 5 assets in `prompts/*.md` specifically
  so this gap can be closed later without re-deriving the spec — but closing it requires wiring in
  an actual image-generation tool (Curify's own pipeline, or an external model), which is
  infrastructure work, not a prompt-writing task.
- Screenshot resolution (browser viewport, ~500-950px per asset) is well below what a real
  marketing asset would need — even a photoreal pass would need to render at a much higher native
  resolution than this demo's capture method achieved.

## D. Portfolio acquisition/data limitations

**Only one representative image per sampled portfolio work was available. Exact source
colors/fonts/material specs were intentionally not inferred.**

- ZCOOL's anonymous-viewer experience reliably renders each work's cover/hero image but not its
  deeper case-study images (a rendering quirk, not the Aliyun WAF, per `PORTFOLIO_SAMPLE_
  SELECTION.md`) — so every downstream claim about a source work rests on a single cover shot, not
  a full case study.
- **work_10's image is only half-rendered** — the weakest single data point in the whole system,
  and the one Rule 4 (form-as-symbol) partially depends on (`PERSONAL_SYSTEM_VALIDATION.md`).
- No exact hex values, confirmed typefaces, or physical material specs were ever claimed for any
  source work, by deliberate policy (`PERSONAL_DESIGN_SYSTEM.md` §2/§3, restated throughout) —
  because single cover-image, screenshot-resolution evidence cannot responsibly support that level
  of precision. This is a correct methodological choice, not an oversight, but it does mean the
  extracted system describes *behavior* (hue-family + accent, mark-repetition, bilingual pairing)
  rather than *specification* (a literal, reusable brand-guideline PDF).
- No login was used at any point, meaning ZCOOL's "HD original quality" gated content was never
  accessed — a deliberate boundary (per the task's own instruction not to bypass access controls),
  but it caps the evidence ceiling regardless of future effort unless the actual portfolio owner
  grants access.

## Priority order for next steps

1. **(C)** Wire in a real image-generation tool for Phase 4 — highest leverage, since every
   upstream step (extraction, brief, prompts) is already automated and ready to feed it.
2. **(D)** If the demo continues, get a full (non-partial) image for work_10 or drop Rule 4 to
   MEDIUM honestly.
3. **(B)** Design the portfolio→profile matching and confidence-calibration steps before treating
   this as more than a single-run demo.
4. **(A)** Everything else in this list is lower priority until (C) is solved — a photoreal rerun
   will itself surface new demo-scope questions (asset count, resolution, format) worth deferring
   until then.
