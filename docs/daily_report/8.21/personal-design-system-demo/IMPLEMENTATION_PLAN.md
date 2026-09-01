# Implementation Plan — Personal Design System Demo

Boss Task D-New, Phase 1 deliverable (2026-08-21). Covers what remains after portfolio selection:
image acquisition, rule extraction, persistence, and generation. No steps below have been executed
yet except where marked "done in Phase 1."

## Phase 2 — Image acquisition (blocked on a real browser session)

**Status:** not started. **Blocker (confirmed 2026-08-21):** ZCOOL sits behind an Aliyun WAF.
A plain `curl` against a ZCOOL work page (e.g.
`https://www.zcool.com.cn/work/ZNzQwMDE0NzI=.html`) returns an 11-line slider-captcha challenge
page, not the real HTML. `WebFetch` (Anthropic's fetch tool) does get past this for *text* content
— it correctly returned work titles, author names, and profile URLs — but image URLs it returns
are lazy-load placeholders (`bg-placeholder.jpg`), not the real CDN links, so it cannot be used to
pull actual image bytes either.

**Plan:**
1. Use the `claude-in-chrome` browser tool (a real, JS-executing browser session) to open each of
   the 8 representative work URLs listed in `PORTFOLIO_CANDIDATES.md` for the primary candidate
   (造物起异), let the page fully render/lazy-load, then read the real image URLs from the
   rendered DOM (or screenshot the work directly if URL extraction is still blocked).
2. Download/save those images to
   `docs/daily_report/8.21/personal-design-system-demo/portfolio_evidence/zaowuqiyi/` with
   filenames that preserve the source work title and URL (recorded in an accompanying
   `SOURCES.md` manifest — no image without a logged source URL).
3. Repeat for the backup candidate (独角狮设计) only if the primary set turns out insufficient for
   rule extraction (e.g. too few images actually resolve, or resolution is too low to read
   color/type detail).
4. If `claude-in-chrome` cannot bypass the WAF either (untested — the WAF may be behavior-based,
   not just header-based, in which case a slow, human-paced interactive session may be required),
   fall back to asking the user to manually save 6-8 images per candidate — do not attempt further
   automated workarounds (rotating headers, proxies, etc.), since that would cross from "scraping
   a public portfolio" into "evading a platform's explicit anti-bot control," which is out of
   scope for this demo regardless of technical feasibility.

Behance (the Sabrina Young alternative, not selected as primary/backup — see
`PORTFOLIO_CANDIDATES.md`) has no equivalent blocker: a plain `curl` returns full HTML with real
CDN image URLs. This is recorded only as a fallback fact, not a plan to switch candidates.

## Phase 3 — Design-system rule extraction

**Status:** not started, depends on Phase 2 producing real image files.

Once 6-8 real images per candidate are available locally:

1. Read the images directly (multimodal read, not just captions) alongside the existing text
   evidence already in this repo (`PACK-01-zaowuqiyi-fruit-wine.md` for primary) to extract, as an
   explicit list, each rule that recurs across **at least 3 of the 6-8** sampled works (a
   single-appearance trait is a one-off, not a system rule):
   - Color: dominant palette (hex-approximate), typical background/foreground pairing, saturation
     level.
   - Typography: Chinese/Latin bilingual pairing pattern, weight, typical hierarchy (product name
     vs. descriptor vs. brand mark).
   - Motif/device: the recurring "super-symbol" treatment — where it sits on the canvas, roughly
     what proportion of the frame it occupies, whether it's illustrative or iconographic.
   - Format conventions: gift-box vs. single-SKU packaging structure, shelf-display (PDQ)
     considerations where relevant.
2. Write the result as a single structured spec file,
   `docs/daily_report/8.21/personal-design-system-demo/DESIGN_SYSTEM_zaowuqiyi.md` (or `.json` if
   a machine-readable format is more useful for Phase 4), with each rule tagged by which sampled
   works it was observed in — so the spec stays traceable back to evidence, not just asserted.
3. Explicitly separate **"observed rule"** (repeats across works, evidenced) from **"my own
   inference beyond the evidence"** (a plausible extrapolation not directly shown) — mirroring the
   sourcing discipline already used in `PORTFOLIO_CANDIDATES.md`.

## Phase 4 — Generation against the new brief

**Status:** not started, depends on Phase 3's persisted spec.

1. Take the 荔泉气泡 (Lichuan Sparkling) brief from `DEMO_SPEC.md`.
2. Use the `design` skill (Claude Design's canvas/artboard workflow) to generate a small set of
   new assets — logo/wordmark direction, color palette board, one can + gift-box packaging
   mockup, one social key visual — constrained explicitly by the rules in
   `DESIGN_SYSTEM_zaowuqiyi.md`, not by free-form creative judgment.
3. Publish the result as an Artifact so it can be visually compared side-by-side against the
   primary portfolio's real sampled images (Phase 2 output) — the comparison itself is part of the
   deliverable, since the whole point is showing "new brief, same system" rather than just
   showing a nice-looking poster in isolation.
4. Record a short pass/fail note against the two falsifiable failure modes named in
   `DEMO_SPEC.md`: (a) generated output reads as visually unrelated to the source portfolio, or
   (b) generated output is a near-copy of one specific existing project rather than a synthesis
   of the recurring rules.

## Sequencing note

Phases 2-4 are gated in order — do not skip to Phase 4 with placeholder/assumed rules if Phase 2
image acquisition stalls. If the ZCOOL WAF cannot be gotten past within a reasonable effort, that
is a legitimate blocker to report back, not a reason to substitute stock/generic packaging imagery
as if it were the studio's real work.
