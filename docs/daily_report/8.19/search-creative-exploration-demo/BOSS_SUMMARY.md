# Search + Creative Exploration Demo — Summary

## Proposed scenario

**Launching a modern Chinese tea brand ("山岚茶事" / Shanlan Tea).** Search for tea-brand
inspiration on Curify, then use the live Brand Direction Explorer ("Creative Exploration") tool
to turn a one-line brief into three distinct creative directions and a finished visual. Both
halves were live-tested against production today (2026-08-19) and produce clean, distinct,
demo-ready output — this is the strongest of the three real available scenarios (the
`coffee-opening` case was also tested and its direction titles are noticeably more repetitive;
see `DEMO_PLAN.md`).

## What the demo shows

1. A live search on `curify-ai.com` for "modern tea brand identity," surfacing real, on-topic
   inspiration cards ("Tea Brand — Contemporary Vibrant," "Tea Brand — Earthy Elegance," etc.).
2. A manual switch to the Brand Direction Explorer tool, where a short brief produces three
   genuinely different creative directions in ~8–10 seconds.
3. Selecting one direction and generating a finished visual from it.

Full click-by-click sequence, exact copy, timing, and fallbacks: `DEMO_PLAN.md` +
`LOOM_SCRIPT.md`.

## Is Search → Creative Exploration a true integrated flow?

**No — it's a sequential demo of two separate, independently-real product surfaces, not a wired
handoff.** Confirmed live today: clicking a Search result opens an unrelated single-parameter
template generator, not Brand Direction Explorer; there's also no in-product navigation link
between the two. The demo connects them only through the presenter's narration and a manual
tab/URL switch — the script says so plainly rather than implying integration that doesn't exist.

One genuinely good finding from today's check: **Brand Direction Explorer is now live in
production** (`curify-ai.com/tools/brand-direction-explorer`), including the preference feature
that our own 8.16 internal docs still describe as unshipped local work — that's now stale and
corrected in `DEMO_PLAN.md`.

## Status

All materials for this demo are prepared and validated (`DEMO_PLAN.md`, `LOOM_SCRIPT.md`,
`DEMO_CHECKLIST.md`, `EVIDENCE.md`), including a backup scenario (`event-poster` / "Afterglow
Market") if the tea scenario underperforms on the actual recording day. **The Loom recording
itself still needs to be performed manually** — nothing here records or publishes a video; this
is the prep package for whoever does that.
