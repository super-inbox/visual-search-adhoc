# Social-Media Resource Shortlist

All 12 of the tightened primary shortlist, selected for being verified, genuinely useful, explainable in a short paragraph, publicly accessible, and reasonably safe to point a general audience at. Three real, deep-reviewed A-tier resources (`webapp-testing`, `figma-implement-design`, `video-shotcraft`) were cut during shortlist tightening and moved to the Honorable Mentions / Watchlist in `README.md` instead of the primary 12 — see the note at the end of this file for why they're still worth citing in follow-up content. Distinct categories are prioritized over cramming in every strong candidate, and this list now deliberately includes one genuinely Codex-native pick alongside the Claude-heavier majority.

---

### 1. impeccable
- **Primary source:** https://github.com/pbakaus/impeccable
- **Helps with:** Stopping AI coding agents from producing generic "AI slop" UI (default gradients/fonts/nested cards) — a systematic anti-pattern checker, not a style guide.
- **Who it's for:** Anyone using Claude Code/Cursor/Codex/etc. to build UI who wants a second opinion that isn't just "ask the model again."
- **Strongest capability:** 59 deterministic rules that run without an LLM call, plus 23 design commands, across 14 different agent tools.
- **What makes it different:** It's an actual rule *engine*, not a prompt — the same input gets the same flagged issues every time.
- **Important caveat:** Requires installing an npm CLI; some anti-pattern judgments will need periodic updates as visual trends shift.
- **Social angle:** Open a "which of these are real tools vs. prompts in a folder" post with this one — it sets the bar.

### 2. styleseed
- **Primary source:** https://github.com/bitjaru/styleseed
- **Helps with:** Giving an agent design *judgment* (when/why to apply a pattern) plus a quantified quality gate for React/Tailwind UI.
- **Who it's for:** Teams already on React + Tailwind + Radix who want a scored, repeatable design-QA step.
- **Strongest capability:** Dual-gate validation — a 0–100 rule-compliance score AND rendered-pixel verification — before anything ships.
- **What makes it different:** It publishes its own self-score (58/100 on its own demo) — unusually transparent for a project pitching itself.
- **Important caveat:** Tightly coupled to one frontend stack; its own +5.3-point benchmark claim is self-reported, not independently reproduced.
- **Social angle:** Perfect "good demo vs. good implementation" example — cite the self-scorecard directly.

### 3. Anthropic's official `frontend-design` skill
- **Primary source:** https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md
- **Helps with:** Teaching Claude Code to ground UI choices in the actual subject matter instead of generic templates.
- **Who it's for:** Anyone who wants to see how Anthropic itself frames "good design" for its own coding agent.
- **Strongest capability:** The most complete single-document coverage of color, typography, motion, hierarchy, and copy of anything reviewed.
- **What makes it different:** It's the house methodology, not a third party's interpretation of what Claude Code "should" do.
- **Important caveat:** Self-critique is manual (screenshot + human/agent judgment), not automated.
- **Social angle:** Good credibility anchor — "here's the actual skill Anthropic ships."

### 4. product-shots
- **Primary source:** https://github.com/motiful/product-shots
- **Helps with:** Turning one product photo into a full e-commerce visual set (main image, detail pages, multi-angle shoot, ads, social posts).
- **Who it's for:** Cross-border sellers on Amazon/Shopify/TikTok Shop, or anyone doing product photography at volume.
- **Strongest capability:** Platform compliance rules baked directly into the generation prompt, plus a 14-point "identity lock" that keeps a model/product consistent across 9 angles.
- **What makes it different:** Real e-commerce-specific expertise (Amazon's "MUST" rules, per-platform style profiles), not generic "make it look professional."
- **Important caveat:** Needs a paid external image-generation API key to actually run.
- **Social angle:** Strong visual before/after story — disclose the API-key requirement up front.

### 5. guizang-social-card-skill
- **Primary source:** https://github.com/op7418/guizang-social-card-skill
- **Helps with:** Generating Xiaohongshu carousels and WeChat cover pairs from content/images, in a coherent visual system rather than ad hoc slides.
- **Who it's for:** Anyone producing Chinese social content at volume — directly the kind of tool this research task's Objective B is about.
- **Strongest capability:** An automated post-render validation script that catches 9 classes of layout fault (overflow, collisions, density) before the image ships.
- **What makes it different:** Two named, well-reasoned visual systems (Editorial vs. Swiss/grid) mapped to content type, not one generic template.
- **Important caveat:** **AGPL-3.0** — any derivative or SaaS-style use must open-source modifications. Flag this every time it's recommended.
- **Social angle:** The single most literal fit for a Chinese-language "resources you can actually use" post — but always pair the recommendation with the license caveat.

### 6. designer-skills (julianoczkowski)
- **Primary source:** https://github.com/julianoczkowski/designer-skills
- **Helps with:** Forcing a staged design process (brief → information architecture → tokens → build → review) instead of one-shot generation.
- **Who it's for:** Anyone who's been burned by an agent jumping straight to code from a vague prompt.
- **Strongest capability:** A `/design-flow` orchestrator that chains 8 skills with skip/confirm gates and persists work per feature.
- **What makes it different:** It's a *process*, not a style — the philosophies (Swiss, Brutalism, Japanese minimalism, etc.) are the payload, not the structure.
- **Important caveat:** An unrelated repo (`Owl-Listener/designer-skills`) shares the exact same name — always link the specific julianoczkowski URL.
- **Social angle:** Good "process beats prompt" example for a more workflow-literate audience.

### 7. excalidraw-diagram-skill
- **Primary source:** https://github.com/coleam00/excalidraw-diagram-skill
- **Helps with:** Generating diagrams that visually argue a concept (fan-out, timeline, convergence) instead of generic boxes-and-arrows.
- **Who it's for:** Anyone who needs technical/explanatory diagrams from any coding agent.
- **Strongest capability:** A genuine render-screenshot-inspect-fix self-correction loop — the cleanest example of that pattern in the whole review set.
- **What makes it different:** Small, focused scope done well, rather than trying to be a general design skill.
- **Important caveat:** License not stated in the reviewed content — confirm before any commercial reuse.
- **Social angle:** Best pick for explaining "what a validation loop actually looks like" in plain terms.

### 8. accesslint / skills
- **Primary source:** https://github.com/accesslint/skills
- **Helps with:** A full WCAG 2.2 workflow — scan, manual-check, site-wide audit, mechanical fix, regression-diff.
- **Who it's for:** Teams that treat accessibility as an ongoing discipline, not a one-time audit.
- **Strongest capability:** Honest severity + confidence grading that acknowledges what automated checking can't catch.
- **What makes it different:** Most "a11y skills" are a single scan; this is a 5-stage lifecycle.
- **Important caveat:** Full functionality needs an MCP server and Chrome CDP automation — review the execution surface first.
- **Social angle:** Good "accessibility is a real design discipline" entry for a more skeptical audience.

### 9. web-design-guidelines
- **Primary source:** https://github.com/vercel-labs/agent-skills
- **Helps with:** A baseline UI-code audit against externally maintained best practices (a11y, forms, animation, performance, dark mode, i18n).
- **Who it's for:** Almost anyone — lowest setup cost of any resource on this list.
- **Strongest capability:** Grounded in Vercel's own maintained guideline set rather than one author's opinions.
- **What makes it different:** Zero dependency, agent-agnostic, safe default recommendation.
- **Important caveat:** Audits/flags only — doesn't fix or visually verify. A "133k weekly installs" figure seen in search results could not be independently verified — don't repeat it as fact.
- **Social angle:** The safe "start here" pick for a general audience.

### 10. Codex-Skills (TheGoat395)
- **Primary source:** https://github.com/TheGoat395/Codex-Skills
- **Helps with:** Giving OpenAI Codex a native, structured library (~70 skills) for visual direction, motion, accessibility, and visual-QA — not a Claude-first tool used cross-ecosystem.
- **Who it's for:** Codex users specifically who want the same kind of structured design tooling Claude Code users already have several strong options for.
- **Strongest capability:** Real code-bearing skill folders plus two honestly-caveated before/after benchmark runs (Atlas 19→23/30, Signal/Matter 23→28/30), explicitly labeled "not an OpenAI evaluation."
- **What makes it different:** Genuinely Codex-first by architecture (adapters for Claude Code/Cursor/Gemini CLI were added afterward, not the other way around) — the clearest Codex-native find in this entire research pass.
- **Important caveat:** Benchmarks are self-reported on only 2 runs, not independently reproduced; individual skill folders weren't opened one-by-one in this review.
- **Social angle:** The anchor for a "this isn't just a Claude thing" section — good evidence the Codex side isn't empty, just smaller.

### 11. visual-verdict
- **Primary source:** https://github.com/Yeachan-Heo/oh-my-claudecode/blob/main/skills/visual-verdict/SKILL.md
- **Helps with:** Turning "does this look right?" into a deterministic, machine-checkable verdict — score, pass/fail, and a structured list of what's wrong — instead of a free-text opinion.
- **Who it's for:** Builders who want to wire a visual-QA gate into an automated loop, not just ask an agent to "take a look."
- **Strongest capability:** A JSON contract (score, verdict, differences[], suggestions[]) gated at a 90+ threshold, built specifically to drive an iterate-until-pass loop.
- **What makes it different:** Cleanest example in the whole review set of a *programmable* compare-and-fix mechanism rather than a described one; a companion GitHub issue in the same repo claims a parallel Codex-ecosystem port.
- **Important caveat:** No license stated; lives inside a larger personal skill collection rather than a standalone maintained project.
- **Social angle:** Good closer for the "what does a real validation loop actually look like" section — show the JSON, not just describe it.

### 12. brand-skills (cofoundy)
- **Primary source:** https://github.com/cofoundy/brand-skills
- **Helps with:** Running a full brand-creation process (naming, positioning, verbal identity, visual identity brief, guidelines) inside a coding agent.
- **Who it's for:** Founders/small teams who need an actual brand-direction process, not just a UI style guide.
- **Strongest capability:** 15 composable skills persisted as a git-tracked `brand.yaml` package, not ephemeral chat output — and the only branding-specific candidate found in this entire research pass.
- **What makes it different:** Most "design skills" in this pool are UI/visual; this is one of the very few addressing brand strategy and naming specifically.
- **Important caveat:** No strong visual validation loop — it specifies and documents rather than critiques generated visuals; its "70+ agents" compatibility claim is an unverified vendor number.
- **Social angle:** Good "design process isn't just UI" post-widener — pairs well with `designer-skills` for a "process, not just prompts" theme.

---

**Not included here despite being strong (Honorable Mentions / Watchlist — see `README.md`):**
- `webapp-testing` — excellent but QA infrastructure, not an aesthetic "design skill" — better suited to a technical audience than a general design-resource post.
- `figma-implement-design` — genuinely useful validation-checklist pattern, but its host repo is marked deprecated by OpenAI — worth citing as a pattern reference in a more technical post, not as a top public recommendation.
- `video-shotcraft` — 152 shot-recipe cards is genuinely the largest domain-knowledge library reviewed and it has the highest social-media-value score of any candidate, but it was cut from the tightened primary shortlist for weaker Curify relevance and no automated validation loop; still a strong pick for a *future*, video-focused post.
