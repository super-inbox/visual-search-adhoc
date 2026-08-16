# Curify Capability Findings

This document extracts **reusable capability patterns** from the reviewed external skills — not recommendations to install or copy any of them. Every pattern below is backed by a specific, verified reviewed candidate (see `skill_reviews.jsonl` for the full evidence).

Curify areas referenced: Creative Exploration, Creative Direction / Brand Direction, design generation, design-agent workflow planning, frontend visual generation, visual QA, manufacturing output QA, reference understanding, inspiration-to-direction workflow.

---

## Pattern 1 — Deterministic anti-pattern checking, not just LLM aesthetic judgment

**External source:** `impeccable` (C01) — 59-rule deterministic detector for "AI slop" (default fonts, gray-on-color text, nested cards, dated easing); `web-design-guidelines` (C06) — 100+ static rule audit.

**What it does / why it works:** Instead of asking the model "does this look good?" — a judgment that drifts and is expensive — both tools encode a fixed, checkable rule list that runs without an LLM call for the detection step itself.

**Underlying principle:** Known, recurring failure modes should be caught by cheap deterministic checks; LLM judgment should be reserved for things that genuinely require taste, not for catching "used Inter font again."

**Design failure prevented:** Generic, repeatable "AI-generated look" defaults that a model reproduces because they're statistically common in training data, not because they're the best choice for the brief.

**Possible Curify application:** A short, versioned checklist of Curify's own known generic-output failure modes (specific palette clichés, layout defaults, spacing patterns seen repeatedly in generated output) that runs as a cheap pre-delivery lint pass, separate from and prior to any LLM-based critique.

**Curify workflow that benefits:** Design generation, frontend visual generation.

**Minimum version to experiment with:** A 10–15 item static checklist (see `INTERNAL_EXPERIMENTS.md` → E1), not a full rule engine.

**Risks/limitations:** Rule lists go stale as visual trends shift and need periodic review; over-tuning to today's defaults risks flagging tomorrow's legitimately good choices.

---

## Pattern 2 — Render → screenshot → inspect → fix loop

**External source:** `excalidraw-diagram-skill` (C08) — Playwright renders its own diagram, screenshots it, detects overlap/misalignment/unbalanced spacing, and fixes before delivery; `figma-implement-design` (C05) — explicit 7-dimension screenshot-vs-Figma validation checklist; `styleseed` (C14) — dual-gate rule-score + rendered-pixel verification before delivery; `guizang-social-card-skill` (C13) — `validate-social-deck.mjs` catches 9 classes of layout fault post-render; `visual-verdict` (C30) — the cleanest version found: a deterministic JSON contract (0–100 score, pass/revise/fail, differences[], suggestions[]) gated at a 90+ threshold, designed specifically to drive a programmatic iterate-until-pass loop rather than a one-off critique.

**What it does / why it works:** The agent doesn't trust its own first-pass output; it renders what it produced, looks at the rendered artifact (not just the source code/markup), and only ships after a check against that rendering. This catches classes of bugs that are invisible in source (overlapping text, off-canvas elements, broken responsive states) but obvious in a screenshot.

**Underlying principle:** Generation and verification are different competencies and should be separate steps, not conflated into "generate well the first time."

**Design failure prevented:** Layout breakage, overflow, visual collisions, and fidelity drift between a reference/spec and the actual rendered output — the single most common class of "looks fine in the code, broken on screen" bug.

**Possible Curify application:** Any Curify workflow that produces a visual artifact (generated frontend, a manufacturing/packaging mockup, a social/marketing asset) could add a render-then-inspect step before the artifact is presented as final, using either a scripted checker (cheapest, like `validate-social-deck.mjs`) or a screenshot-based LLM critique (more flexible, like `figma-implement-design`'s checklist).

**Curify workflow that benefits:** Frontend visual generation, visual QA, manufacturing output QA.

**Minimum version to experiment with:** See `INTERNAL_EXPERIMENTS.md` → E2 — a single render→screenshot→one-iteration-fix step added to one existing generation path, measured against a no-loop baseline.

**Risks/limitations:** Adds latency and (if screenshot critique uses an LLM call) cost per generation; needs a stopping condition so the loop doesn't run indefinitely.

---

## Pattern 3 — Locked identity anchors for multi-asset consistency

**External source:** `product-shots` (C10) — 14 locked "identity anchors" (face, hair, outfit, lighting, camera) keep a fashion-on-model shoot visually consistent across 9 generated angles.

**What it does / why it works:** Rather than re-describing the full subject in every generation call and hoping for consistency, a small, explicit set of attributes is extracted once and re-injected into every subsequent generation in the batch.

**Underlying principle:** Consistency across a generated set is a *constraint-propagation* problem, not a prompting-luck problem.

**Design failure prevented:** Visually inconsistent multi-image sets (different lighting, subtly different subject appearance) that look obviously AI-generated and unusable together.

**Possible Curify application:** Any Curify generation flow that produces multiple related assets (multiple angles, a set for one creative direction, a batch of variants) could extract a small anchor set from the first accepted generation and re-inject it into subsequent ones.

**Curify workflow that benefits:** Design generation, manufacturing output QA (multi-angle product previews).

**Minimum version to experiment with:** See `INTERNAL_EXPERIMENTS.md` → E3.

**Risks/limitations:** Anchor extraction itself needs to be reliable — a bad first generation propagates its flaws to the whole batch.

---

## Pattern 4 — Hard constraints as prompt fields, not post-hoc filters

**External source:** `product-shots` (C10) — Amazon's compliance "MUST" rules (white background, ≥85% frame fill, no overlays) are written directly into the generation prompt per platform, rather than checked and rejected after the image is made.

**What it does / why it works:** Bakes non-negotiable constraints into the generation request itself, so the model is far less likely to produce output that then needs to be discarded and regenerated.

**Underlying principle:** It's cheaper and more reliable to constrain generation than to filter its output after the fact, when the constraint is well understood in advance (e.g. platform/manufacturing specs).

**Design failure prevented:** Wasted generations that violate a known, fixed requirement (platform compliance, print/manufacturing spec, aspect ratio) that could have been stated up front.

**Possible Curify application:** Where Curify already knows a hard constraint ahead of generation (manufacturing dimensions, safe zones, platform aspect ratios), state it explicitly as a structured prompt field rather than relying on a downstream check to catch violations.

**Curify workflow that benefits:** Manufacturing output QA, design generation.

**Risks/limitations:** Only works for constraints that are known and stable in advance; doesn't replace verification for constraints discovered dynamically (still needs Pattern 2 for those).

---

## Pattern 5 — Staged pipeline with an orchestrator and persisted intermediate artifacts

**External source:** `designer-skills` (C12) — 8 skills (brief → information architecture → design tokens → tasks → build → review) chained by a `/design-flow` orchestrator that persists work to `.design/` folders per feature and allows skip/confirm at each gate; `brand-skills` (C32) — 15 skills (naming → positioning → architecture → verbal identity → visual identity brief → guidelines) persisted as a git-tracked `brand.yaml` package rather than ephemeral chat output — the same pattern applied to brand direction specifically, not just UI.

**What it does / why it works:** Breaks "design this" into named, inspectable stages with real artifacts at each boundary, instead of one large opaque generation step. A human (or another agent) can intervene at any gate.

**Underlying principle:** Long creative workflows benefit from explicit checkpoints with durable state, the same way a multi-step build pipeline benefits from named stages over one monolithic script.

**Design failure prevented:** Losing traceability between "what the user asked for," "what direction was chosen," and "what got generated" — and being unable to back up one stage without redoing everything.

**Possible Curify application:** Curify's inspiration-to-direction-to-generation pipeline could formalize its own stage boundaries (inspiration intake → extracted direction/tokens → generation → review) with persisted intermediate state at each boundary, similar in spirit to this orchestrator pattern.

**Curify workflow that benefits:** Creative Exploration, Creative Direction / Brand Direction, design-agent workflow planning.

**Risks/limitations:** More stages means more places for a workflow to stall waiting on confirmation; needs sensible defaults so it doesn't become a chore for simple requests.

---

## Pattern 6 — Quantified, self-reported quality score published alongside the tool

**External source:** `styleseed` (C14) — publishes a 0–100 rule-compliance score for its own demo (58/100), and reports a benchmark delta (+5.3 points across 120 test cells on Codex and Claude Code); `Codex-Skills` (C36) — reports two named before/after rubric-scored benchmark runs (Atlas 19→23/30, Signal/Matter 23→28/30), explicitly labeled "repository rubric scores, not an OpenAI evaluation" rather than overclaimed. The pattern shows up independently on both the Claude and Codex sides of this research.

**What it does / why it works:** Turns "is this better?" into a trackable number instead of a vibe, and — notably — the project scores its *own* output honestly rather than only showing best-case examples.

**Underlying principle:** A quality-gate is more useful internally if it produces a comparable number over time, not just a pass/fail per artifact.

**Design failure prevented:** Regression that goes unnoticed because there's no baseline number to compare against; also prevents overclaiming quality without any way to check the claim.

**Possible Curify application:** Curify could define its own small internal scoring rubric (reusing dimensions from `EVALUATION_RUBRIC.md`-style axes: hierarchy, consistency, constraint compliance) and score generated creative-direction output against it over time, rather than relying purely on qualitative review.

**Curify workflow that benefits:** Design generation, Creative Direction / Brand Direction (tracking whether prompting/workflow changes actually help).

**Risks/limitations:** A self-reported benchmark (as `styleseed`'s own +5.3pt claim is) is not independently verified — this pattern is worth adopting methodologically, but any resulting Curify number needs its own independent validation before being trusted.

---

## Pattern 7 — Reference decomposition into explicit semantic tokens

**External source:** `styleseed` (C14)'s `/ss-reference` — converts screenshots/URLs/Figma files into "evidence-backed project grammars" with semantic tokens and named anti-patterns; `designer-skills` (C12)'s 8 named aesthetic philosophies (Dieter Rams, Swiss, Japanese minimalism, etc.) with concrete parameters per philosophy.

**What it does / why it works:** Instead of "make it look like this reference" (vague, hard to apply consistently), the reference is first decomposed into a small set of explicit, named attributes (palette, type scale, spacing rhythm, a named aesthetic family) that can then be applied deliberately and audited.

**Underlying principle:** Structured, named tokens generalize and are checkable; freeform "vibe matching" against a reference image does not.

**Design failure prevented:** Superficial mimicry of a reference (copying an obvious surface trait) while missing the structural properties that actually made the reference work.

**Possible Curify application:** This is the pattern most directly aligned with Curify's own "reference understanding" and "inspiration-to-direction" workflow — an explicit token/grammar-extraction step between "user supplied inspiration" and "generation begins" is worth prototyping as a distinct, inspectable stage.

**Curify workflow that benefits:** Reference understanding, inspiration-to-direction workflow, Creative Direction / Brand Direction.

**Minimum version to experiment with:** See `INTERNAL_EXPERIMENTS.md` → E4.

**Risks/limitations:** Token extraction can itself be lossy or biased toward whatever attributes the extraction step was told to look for; needs periodic human spot-checking against the original reference.

---

## What NOT to blindly copy or install

- **None of these external skills should be installed into Curify's own repositories or CI.** Every pattern above is described as a principle to reimplement in Curify's own words/stack, not a dependency to pull in.
- Several candidates require external API keys or broad local execution (`product-shots` needs an image-gen API key; `accesslint`/`excalidraw-diagram-skill`/`video-shotcraft`/`guizang-social-card-skill` all require local Node/Python/Playwright/Chromium execution) — none of this was run for Task D, and none should be run without a separate, explicit security review.
- `guizang-social-card-skill` is **AGPL-3.0** — reusing its actual code (not just the pattern) in any Curify-adjacent product would carry copyleft obligations. The *idea* (automated layout-fault validation) is free to reimplement independently; the code is not free to embed.
- `figma-implement-design`'s host repo (`openai/skills`) is marked deprecated by OpenAI — treat its pattern as historical evidence, not as a live dependency to track.
