# Image Inventory — Visual Search Platform Spectrum

Purpose: A clean, editorial (not AI-generated) explanatory graphic for the public-facing
external insights blog / LinkedIn materials. Illustrates how visual search platforms
range from consumption-oriented discovery to creation-oriented templates, matching the
"Consumption-to-Creation Spectrum" framing in `../../blog_public_v2.md` (§4, §7.2).

Created: 2026-07-02
CDN status: **Local draft asset only — not uploaded to CDN.**

---

## Exact Text Used

**Main title:** Visual Search Platform Spectrum

**Subtitle:** From open-web discovery signals to template-led creation systems

**Axis text:** Consumption-oriented discovery ◄ ── (gradient spectrum line) ── ► Creation-oriented templates

**Platforms, left to right:**

| # | Platform | Label | Rating |
|---|---|---|---|
| 1 | Google Images | Open-web recall | ★★★★★ |
| 2 | Bing Images | Rich taxonomy + labels | ★★★★★ |
| 3 | Pinterest | Inspiration + label chips | ★★★★☆ |
| 4 | Curify | Template-led creation | ★★★★☆ |
| 5 | Canva | Template marketplace | ★★★★★ |

**Footer:** Source: 58-query visual search pilot study across 5 platforms (June 2026)

---

## Local File Paths

| File | Format | Purpose |
|---|---|---|
| `visual_search_platform_spectrum.svg` | SVG | Primary, self-contained source-of-truth graphic. No external fonts, images, or remote assets — system sans-serif font stack only. Editable text. |
| `visual_search_platform_spectrum.html` | HTML | Renders the SVG centered on a page for browser preview / screenshot export. Open with `open docs/daily_report/7.2/assets/platform_spectrum/visual_search_platform_spectrum.html`. |
| `visual_search_platform_spectrum.png` | PNG | Rasterized export (2400×880, 2x) generated locally via `rsvg-convert` (already installed; no new packages installed). Convenience only — SVG is the source of truth. |

---

## Status

**Local draft asset — not uploaded to CDN.** Before publication, upload the PNG (or an
exported screenshot of the HTML) to the CDN/image host used for the blog and LinkedIn
post, then update this file's CDN status.

---

## Notes

- "Label chips" / "labels" refers to UI label filters / related-search label pills shown
  on search platforms (e.g., Bing's related-search labels, Pinterest's One Bar label
  chips, Canva's Format/Style filter chips) — **not hardware chips**. If a Chinese note
  is ever needed for this term, use **标签**, not 芯片.
- Star ratings mirror the "Creative / Template Orientation" dimension in the Platform
  Star Rating Table (`../../blog_public_v2.md` §5), simplified to a single spectrum
  rating for this graphic.
- Colors were chosen and validated (categorical CVD/contrast checks) via the repo's
  `dataviz` design skill: deep blue → blue (consumption) → violet (Pinterest, bridge) →
  orange → deep orange/red (creation). Identity is carried by direct text labels on each
  card, not by color alone.
- Graphic is sized for 1200px-wide insertion and reads cleanly as a LinkedIn preview
  image at 2x (2400×880) export.
