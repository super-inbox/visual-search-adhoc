# Evaluation Rubric — Claude/Codex Design Skills

Used to score every deeply-reviewed candidate in `skill_reviews.jsonl` and `skills_shortlist.csv`. All dimensions are scored **1–5**, independently — there is no single aggregate number. A candidate can be high on domain knowledge and low on validation (or vice versa), and the rubric is built to surface that instead of averaging it away.

Stars, installs, and social shares are **not** a rubric dimension. They may appear in `notes` as unverified context, but never drive a score (see `README.md` → Safety & Source Policy).

## A. Design usefulness
Does using this materially improve the *quality* of a design task's output, not just its speed?
- **1** — No discernible design improvement; equivalent to asking the base model with no skill.
- **3** — Noticeably nudges output away from generic defaults in a narrow scenario.
- **5** — Directly targets a well-known, recurring design failure mode (e.g. "AI slop" gradients, inconsistent product-shot compliance) with a mechanism built specifically to fix it.

## B. Implementation depth
Is this a real workflow/system, or prompt text with a skill wrapper around it?
- **1** — A single generic prompt; no structure, code, or state.
- **3** — Multiple steps or sub-skills with some structure, but no code/automation.
- **5** — Multi-stage pipeline with real code (rule engines, render pipelines, validators) and/or an orchestrator chaining sub-skills with persisted state.

## C. Design-domain knowledge
Does it encode real, specific design expertise — not just "make it look nice"?
- **1** — Generic adjectives only ("modern", "clean", "professional") with no concrete rule.
- **3** — Some concrete rules (e.g. a fixed palette list) without stated reasoning.
- **5** — Named, specific expertise with reasoning: typography-weight rules, platform compliance rules, cinematography vocabulary, WCAG criteria, etc., traceable to a real design/engineering discipline.

## D. Reusability
Can the approach generalize beyond the one demo it ships with?
- **1** — Hardcoded to one project/brand/example; cannot be retargeted.
- **3** — Reusable within a fixed stack or narrow domain (e.g. one frontend framework, one output format).
- **5** — Framework-/tool-agnostic, or explicitly designed to be re-parameterized (tokens, brand files, config) for new projects.

## E. Documentation quality
Can a competent engineer understand how it actually works without executing it?
- **1** — No README/SKILL.md, or contradicts itself.
- **3** — Basic README covering setup and one example; internal mechanism unclear.
- **5** — Clear description of mechanism, inputs/outputs, dependencies, and limits; a static read is enough to predict behavior.

## F. Example / demo quality
Are the examples credible evidence of real output, not marketing renders?
- **1** — No examples, or examples are generic stock/marketing imagery unrelated to the tool's actual output.
- **3** — Examples exist but can't be independently verified as tool output (author-only claims).
- **5** — Concrete, specific examples (real code, real screenshots, a public live demo) with enough detail to judge credibility, ideally corroborated by independent third-party mentions.

## G. Validation quality
Does the workflow inspect, compare, verify, critique, or fix its own output — or does it just generate and stop?
- **1** — Pure generation; no self-check of any kind.
- **3** — Qualitative self-critique step exists (e.g. "take a screenshot and review it") but is manual/unscripted.
- **5** — Automated, scripted validation: render-compare-fix loops, deterministic rule checkers, quantified scoring, or regression diffing.

## H. Curify relevance
Could the underlying *pattern* (not the specific code) improve a Curify workflow?
- **1** — No plausible connection to Curify's creative-exploration, direction, generation, or QA workflows.
- **3** — Loosely relevant; would require significant reinterpretation to apply.
- **5** — The mechanism maps closely onto an existing or planned Curify workflow (e.g. reference decomposition ↔ inspiration-to-direction; identity-lock ↔ multi-asset generation).

## I. Social-media value
Would this make a credible, useful public resource recommendation?
- **1** — Not safe or not interesting to recommend (hype-only, broken, or misleading).
- **3** — Worth a passing mention with caveats.
- **5** — Verified, distinctive, explainable in one paragraph, and safe enough to point a general audience at directly.

## J. Security / operational risk
Recorded as **low / medium / high**, not 1–5, because it's a risk flag rather than a quality axis.
- **low** — Static content, or local-only execution with no credentials, secrets, or network calls.
- **medium** — Requires local execution of third-party code (Node/Python/Playwright/Chromium), and/or an MCP server, and/or network calls to public content sources — but no API keys/secrets observed in the reviewed content.
- **high** — Requires API keys/secrets, broad filesystem access beyond the project, or execution of code whose full behavior could not be read statically. *(No candidate in this pool was rated high — the closest is `product-shots`, rated medium for its external image-gen API key requirement.)*

---

## Marketing-vs-substance buckets

Every deeply-reviewed candidate is placed into exactly one bucket (`marketing_vs_substance` field):

| Bucket | Meaning |
|---|---|
| `strong_implementation_strong_presentation` | Real system (B/C/G ≥ 4) **and** credible, well-documented (E/F ≥ 4). The gold standard. |
| `strong_implementation_weak_presentation` | Real system, but documentation/examples are thin, unverified, or the hosting repo's status is uncertain. |
| `weak_implementation_strong_marketing` | Polished landing page / viral posts, but the actual SKILL.md or source is thin or unverifiable. *(None of the 18 deep reviews landed here — flagged as a category to watch for, not a finding.)* |
| `thin_prompt_wrapper` | A single prompt with no code, no validation loop, and largely generic advice — regardless of how well-written the prompt is. |
| `specialized_but_useful` | Narrow scope, doesn't try to be a general "design skill," but does its one job well (e.g. QA infrastructure rather than aesthetic judgment). |
| `insufficient_evidence` | Could not be verified deeply enough (broken source link, inaccessible rule files, etc.) to place in any other bucket honestly. |

## Tiering rule (S / A / B)

- **S** — Average of A–H ≥ 4.3, `verification_status = verified` (not partial/shallow/unverified), and no unresolved security concern above `medium`.
- **A** — Average of A–H ≥ 3.5, primary source verified (verified, verified_with_caveat, or verified_shallow accepted).
- **B** — Everything else that still clears a minimum bar of being a real, findable resource (excludes `discovery_only` candidates, which are not tiered at all — they simply were not deep-reviewed).

An **unverified** primary source can never receive S, regardless of how strong the pitch looks — this is enforced manually per Task D instructions, not just by the formula above.
