# Demo Storyboard — 30-Second Zero-Prompt Creative Workflow

**Status: all content below is [Recommendation] / creative direction for a future demo. Nothing in this document describes a shipped, runtime-verified feature.** Where a shot leans on a present-in-source surface, that surface is named explicitly with a `[Observed in code]` tag and a capability-status marker (below). Every other shot assumes new UI that was not found in the inspected source (P0/P1 scope, see main document §14).

**Primary scenario (per task brief):** a coffee shop owner needs an opening-day poster.

This document is split into two explicit versions, because the two carry very different publication readiness:

- **Version A — Honest P0 Demo Plan:** describes a demo built only from present-in-source building blocks plus a small number of hand-curated (not dynamically generated) directions, with no field-level editing shown or implied. This is a **plan for what to build and film**, not a finished, ready-to-publish asset — several of its scenes (the Goal-first entry screen, the direction cards, the "download all" packaging) describe new screens or adaptations that do not yet exist and have not been runtime-verified. **Suitable for external use only after the P0 adaptations described below have been implemented, runtime-verified, and checked scene-by-scene against the final published script** (see the checklist at the end of this document and in the main document's §13/§14). Until that verification happens, treat Version A as an internal production brief, not a publishable video.
- **Version B — P1 Target Vision:** includes the not-yet-built direction-recommendation step and field-level editing, clearly labeled as a future-state concept reel. **Must not be published as a demo of current product capability** — appropriate for internal alignment, pitch decks, or roadmap conversations only, always labeled as a target vision.

---

## Version A — Honest P0 Demo Plan

**Suitable for external use only after the P0 adaptations below have been implemented, runtime-verified, and checked against the final published script — not immediately, as-is.** The table below is the production/demo plan; it is not a description of a finished, filmable-today asset.

| Time | Screen / visual | User action | Product response | On-screen text | Voice-over | Capability status |
|---|---|---|---|---|---|---|
| 0:00–0:03 | Homepage, a single Goal-first entry surface ("What do you need?" with deliverable tiles) | User taps "Poster" | Tile selection confirms | "Poster" | *"Tell us what you need."* | **P0 demo adaptation** — a simplified, single-purpose entry screen built for this demo; the present-in-source homepage has two entry components today (`HomeOmniInput`, `HomeImageWorkbench`), and this screen does not claim either of them has been replaced |
| 0:03–0:07 | 3 direction cards appear (e.g. "Warm Minimal," "Bold Retro Diner," "Modern Botanical") | User looks, no typing | Cards render with a preview image each | "Pick a direction" | *"Here are three directions to choose from."* | **P0 demo adaptation, hand-curated** — these 3 directions are pre-selected for this specific demo scenario, not produced by a general recommendation service (that service was not found in the inspected source and is P1 Core scope) |
| 0:07–0:11 | One card highlighted on tap | User taps "Bold Retro Diner" | Card confirms selection | "Bold Retro Diner ✓" | *"Pick the one that feels right."* | **P0 demo adaptation** — selection UI is new, but the underlying template it maps to is a present-in-source template |
| 0:11–0:15 | Minimal confirm panel — shop name, opening date | User types "Rise & Grind" and "Aug 15" | Fields populate a layout preview | "Rise & Grind · Aug 15" | *"Just the facts — no design vocabulary needed."* | **Existing building block, adapted** — the structured parameter form pattern is present in source (`TemplateParameter`, `ReproduceWorkbench.tsx:420-464`); this screen restyles it for the demo |
| 0:15–0:19 | Generation | User taps "Generate" | Loading animation | "Generating your poster…" | *(soft music, let visual do the work)* | **Existing generation building block** — the async generate → poll pattern is present in source (`/nano-templates/generate`, `ReproduceWorkbench.tsx`) |
| 0:19–0:24 | Result — poster fills the frame | User taps around the poster | Poster renders with shop name + date placed | "Your poster is ready" | *"A polished first draft, ready to refine."* | **Existing generation building block** — result rendering is present in source; the voice-over avoids an unverifiable "studio-quality" guarantee |
| 0:24–0:27 | Designer-pack row — resize/print-ready tiles (no inline text editing shown) | User taps "Make print-ready" | A print-ready variant is added | "Print-ready ✓" | *"Turn it into more formats, instantly."* | **Existing building block** — designer-pack derivative transforms are present in source (`ReproduceWorkbench.tsx:556-682`); this version does **not** show editing the poster's text content, since that capability was not found in the inspected source |
| 0:27–0:30 | Export tray — poster + resized variant, one tap to download | User taps "Download all" | Files save | "Poster · Print-ready — done" | *"One idea. Ready-to-use files."* | **Existing building block, needs packaging adaptation** — individual downloads are present in source; a single "download all" bundling action was not found and would need light new work |

### What Version A deliberately does NOT show
- No field-level editing of the generated result (change the date, fix a typo) — this capability was not found in the inspected source and is scoped as a P1 Extension, not P0.
- No claim that the 3 directions come from a general, reusable recommendation model — the voice-over ("here are three directions") is compatible with either a hand-curated demo or a future real service, and does not overstate which one is running.
- No unverifiable quality claims ("studio-quality," "professional-grade") — replaced with "a polished first draft, ready to refine."

### Before Version A can be published externally
This plan is only "honest" once it is also true — publishing before the following are done would create the exact overpromising problem this document is trying to avoid:
1. The Goal-first entry screen, direction cards, and packaging adaptation (rows flagged "P0 demo adaptation" or "needs packaging adaptation" above) are actually built.
2. The built demo is run end-to-end against a real (not mocked) generation call, and the output is checked against what the storyboard claims it shows.
3. The final video script is checked scene-by-scene against this table and against the phrase checklist in the main document (§12/§13), so no line implies a capability (a general recommendation model, real-time editing) that isn't actually running.

---

## Version B — P1 Target Vision (internal use only, must be labeled as a future concept)

**This version must carry an on-screen or verbal disclaimer such as "concept vision — not current product" whenever shown to anyone outside the immediate product/eng team, and must not be published as a marketing asset.**

| Time | Screen / visual | User action | Product response | On-screen text | Voice-over | Capability status |
|---|---|---|---|---|---|---|
| 0:00–0:03 | Unified homepage entry (hypothetical, post-decision on the two current entry surfaces) | User types: *"opening poster for my coffee shop"* | Input pulses | "opening poster for my coffee shop" | *"You don't need a prompt. Just tell us what you need."* | **P1 target** — assumes the two-entry-surface product decision (main doc §16) has been resolved |
| 0:03–0:07 | Direction cards generated dynamically from the brief | User looks, no typing | Cards render live from a recommendation step | "Pick a direction" | *"Curify reads your idea and gives you real creative directions."* | **P1 Core target** — a general direction-recommendation service; not found in the inspected source today |
| 0:07–0:15 | Direction selection + confirm info | User picks a direction, types name/date | Fields populate | "Rise & Grind · Aug 15" | *"Just the facts — no design vocabulary needed."* | Existing building block (same as Version A) |
| 0:15–0:24 | Generation + result | — | Poster renders | "Your poster is ready" | *"A polished first draft, ready to refine."* | Existing building block (same as Version A) |
| 0:24–0:27 | Inline field edit — user taps the date directly on the poster, types a new date | User edits inline | Poster updates just that field | "Aug 22" | *"Change the details anytime — without writing a new prompt."* | **P1 Extension target** — field-level content editing without re-generation; explicitly deferred per a code comment in the present source (`ReproduceWorkbench.tsx:54-56`) and requires backend schema work, not just UI |
| 0:27–0:30 | Full-set export | User taps "Download all" | Full asset set saves | "Poster · Social post · Print-ready — done" | *"One idea. A full set, ready to use."* | Mostly existing building blocks + packaging adaptation (same as Version A's last row) |

---

## Alternative demo hook (if a faster P0 is needed before the Directions screen is built)

If the team needs something filmable **before** even the hand-curated Directions screen exists, the `/ip-merch-demo` page (`curify-frontend:app/[locale]/(public)/ip-merch-demo/MerchWorkflowBurst.tsx`) already provides a filmable "drop a doodle → instant burst of production sheets" moment — **[Observed in code]; capability status: existing building block, demo-only per its own code comment** (client-side, no backend, no real generation call, explicitly marked in the component's own comment as a mock, not exported print files). It is honest to film this today only if the voice-over and on-screen text make clear it's illustrating the *workflow concept*, not claiming every frame is a live AI generation.

## Format notes

- Total runtime target: 30s, matching the brief.
- Aspect ratio: vertical (9:16) primary cut for TikTok/Reels/小红书; a 1:1 crop for Instagram feed as a secondary export.
- Music/pacing: fast cuts 0:00–0:15 (decision-making feels quick), one held beat at 0:19–0:24 (let the payoff breathe), fast close 0:24–0:30 (export = done, no friction).
- Before any external publication of either version, re-run the phrase check in the main document's quality checklist (§ cross-consistency) against the final video script to confirm no disparaging comparisons, no unverifiable quality guarantees, and no capability shown that doesn't exist at publish time.
