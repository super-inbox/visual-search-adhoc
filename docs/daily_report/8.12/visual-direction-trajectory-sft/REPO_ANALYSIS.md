# REPO_ANALYSIS.md — gc-minimal-zine-poster

**Source:** [github.com/LiamGvchi/gc-minimal-zine-poster](https://github.com/LiamGvchi/gc-minimal-zine-poster)
(public, MIT license, v0.3, confirmed real — not the typo'd "gc-minimal-zine-posterr").
Fetched 2026-08-13 via `gh api` tree listing + `raw.githubusercontent.com` (README.md, README.zh-CN.md,
README.ja.md, SKILL.md, `agents/openai.yaml`, `evals/evals.json`, all five `references/*.md`,
`examples/*.jpeg`, `LICENSE`). No local clone was kept in this repo — files were read from the
scratchpad only, and nothing from the external repo is copied into our output verbatim beyond
short attributed excerpts below.

This is a **Codex Skill package**, not a running application or agent framework. It is a set of
markdown instructions (`SKILL.md` + `references/*.md`) that a host LLM (Codex) reads and follows
when a user invokes `$gc-minimal-zine-poster-v0-3`. There is no code, no orchestration engine, no
training data, and no trajectory logs in the repo — "workflow" here means "documented procedure an
LLM is instructed to execute," not an executed/logged agent run.

---

## A. What the external repo explicitly does

### A.1 Request routing (`SKILL.md`, "Route The Request")
The skill defines five named modes and tells the host model to pick the smallest one that fits the
request, using explicit Chinese-language trigger phrases:
- **Generate** (default): theme/sentence/article/object/mood/photo/brief → visual metaphor → prompt → generated image → inspection.
- **Photo Input** (a Generate subflow): triggers when a photo is supplied; classifies it as *edit target*, *reference image*, or *supporting insert*, and assigns a *preservation level* (High/Medium/Low) before generation.
- **Reference Analysis**: reference images/folder + a request to analyze/extract/systematize → evidence-based style rules, no image generated unless also requested.
- **Prompt-only**: explicit request for a prompt with no generation.
- **Analyze + Generate**: Reference Analysis first, then Generate Mode using the extracted system.

Routing is rule-based pattern matching on the user's literal wording (e.g. "把这张照片做成海报" →
edit target), not a learned classifier or confidence score. The skill instructs: "Do not stop to
ask about choices the skill can make safely" — ambiguity is resolved by a stated default (edit
target, generate mode), not by an escalation step, except when "two materially different roles
remain equally plausible."

### A.2 Reference analysis (`references/reference-analysis.md`)
A three-way evidence classification, applied per supplied reference image:
- **Fixed system**: traits repeated across most usable references → become non-negotiable rules.
- **Variable system**: traits that change while family resemblance survives → safe axes of variation.
- **Sample residue**: traits appearing in only one or two examples (words, brands, exact dates,
  layouts) → explicitly excluded from reuse, never generalized.

The repo is explicit that this classification is evidence-based: "Separate `observed` from
`inferred`" (e.g., "paper fibers are visible" is observed; "intended to feel nostalgic" is
inferred), and confidence must scale down with sample size — "With one reference, describe
observed traits and confidence limits; do not claim collection-wide frequency."

### A.3 Fixed vs. variable visual system (`references/style-system.md`)
A concrete, numeric fixed/variable split for this one visual family:
- **Fixed** (non-negotiable): 3:5 canvas, 70–90% negative space, one visual cluster at 8–25% of
  canvas, one high-chroma color anchor, paper/scan reproduction texture, restrained typography, an
  "anti-identity" exclusion list (no commercial ad layouts, no glossy mockups, no 3D/neon/cartoon).
- **Variable**: paper tone, cluster position, anchor form, structure, typography distribution,
  decorative marks, mood — each given as an enumerated option list, not free text.
- **Color system** is a further fixed/variable split of its own: one main high-chroma hue at a
  numeric area range (0.8–2.5% of canvas), optional subordinate second hue capped at ~10% of
  chromatic area.

### A.4 Prompt compilation (`references/prompt-compiler.md`)
A fixed **field order** (canvas → attention geometry → photo contract → visual metaphor → anchor
form → material treatment → typography → color → reproduction/mood → hard avoids) compiled into a
**four-paragraph template** with named slots (`[ratio]`, `[cluster_scale]`, `[exact_hue]`, etc.).
Different second-paragraph templates are swapped in for edit-target vs. reference-image cases. This
is the closest the repo comes to a literal "prompt compilation" module — it's a deterministic
template-fill, not a learned compiler.

### A.5 Variation engine (`references/variation-engine.md`)
Six independent enumerated axes (layout family, anchor form, typography mode, texture mode,
decorative system, plus the color/mood axes from style-system.md). Selection rules explicitly
require the model to avoid mode-collapse: "Do not repeat `center-fragment` simply because it is
safe... prefer an off-axis, dual-panel, type-led, or edge-counterweight family" if the prior visible
output was centered, and for batches of ≥4, "use at least three layout families." The chosen
combination is recorded as a compact **recipe string** — this is the repo's de facto "variation
recipe" concept named in the task brief.

### A.6 Quality gate (`references/quality-gate.md`)
A checklist applied to the actual generated raster (not just the prompt) before returning it:
canvas ratio, negative-space %, cluster size %, color-anchor visibility and area %, absence of the
anti-identity list, and — for Photo Input — a specific preservation check (identity/proportions/
markings/silhouette must not drift at High preservation). On failure: **regenerate once** with a
tightened prompt; if the second attempt still fails, "return the better result and state the
remaining limitation briefly; do not describe failed preservation as successful." This is the
repo's only closed-loop revision mechanism, and it is capped at exactly one retry.

### A.7 Evaluation (`evals/evals.json`)
Seven eval cases, each an input prompt (some with attached reference images) plus a natural-language
`expected_output` description of what a correct run should do — e.g. eval #3 supplies six of the
repo's own example images and expects the model to "separate observed evidence, fixed system,
variable system, and sample residue... without claiming to generate an image." These are **rubric
prompts for a human or LLM judge to read against a transcript**, not automated pass/fail assertions,
scorers, or ground-truth images. There is no scoring script, no numeric threshold, and no benchmark
harness in the repo.

### A.8 What is *not* in the repo
No code (Python/JS/etc.), no logged trajectories, no training data, no state/action/observation
schema, no tool-call interface (image generation is invoked through the host Codex runtime's
built-in capability, referenced only as "the built-in image-generation tool"), no multi-model
comparison, and no persisted history across runs beyond "the current conversation."

---

## B. What we infer Curify could adopt

These are inferences, not repo claims — each is labeled with the specific mechanism it's drawn from.

1. **Fixed/variable/residue as a reusable reference-analysis vocabulary** (from A.2/A.3). Curify's
   Creative Exploration already ingests reference images; this repo's three-way split (what must
   carry over / what may vary / what belongs only to this one sample and must not leak) is a
   cleaner intermediate representation than an unstructured "style description," and maps directly
   onto a trajectory step (`visual-system-extraction`, see `TRAJECTORY_SCHEMA.md`).
2. **Numeric, checkable fixed-system fields over adjectives** (from A.3, A.6). "70–90% negative
   space" and "0.8–2.5% chroma area" are things a judge (human or automated) can actually check
   against a generated image; "elegant" or "on-brand" are not. Curify visual-direction output could
   define a small set of numeric/enumerable fields per domain (not this repo's specific numbers,
   which are poster-specific) as the observable target of a quality-gate step.
3. **A named, enumerated variation axis set with an anti-repetition rule** (from A.5). The
   "don't repeat the same layout+anchor pair; change grammar not just position" rule is a concrete,
   reusable pattern for a `direction-generation` trajectory step that must produce genuinely
   diverse candidates rather than N cosmetic variants of one idea.
4. **A capped, single-retry regeneration loop with an honesty rule on residual failure** (from
   A.6). "Regenerate once; if still failing, state the limitation, don't claim success" is a
   concrete, observable revision policy — directly useful as the shape of a `revision` trajectory
   step and as a benchmark dimension ("did the trajectory correctly report a limitation instead of
   overclaiming?").
5. **Eval cases as rubric prompts, not scorers** (from A.7). This repo shows what a *lightweight*
   eval set looks like for a subjective visual task: natural-language expected behavior, judged by
   reading the transcript. Useful precedent for Curify's own benchmark (`BENCHMARK_PROPOSAL.md`)
   showing that "no single scalar score" is an accepted, working pattern elsewhere, not a cop-out.
6. **Explicit preservation-level classification for photo inputs** (from A.1/A.6) is a transferable
   idea for any Curify flow that takes a user's own photo/logo/product image as input alongside a
   creative brief — classifying it once (edit target / reference / insert) before generation avoids
   silently discarding or over-preserving user content.

---

## C. Things Curify should NOT copy blindly

- **The poster-specific numbers are not transferable.** 3:5 canvas, 70–90% negative space, one
  high-chroma hue at 0.8–2.5% area are tuned to one visual family (quiet paper-texture zine
  posters). A coffee-shop brand direction or packaging direction needs its *own* domain-specific
  fixed-system numbers, not these ones.
- **The routing logic is regex-like pattern matching on Chinese trigger phrases**, not a learned or
  robust intent classifier — it is not a model for how Curify should do request routing at
  production scale or across languages/domains.
- **The "one retry, then admit failure" loop is a minimal, single-agent pattern**, not a full
  agentic revision loop with intermediate critique, multiple candidates, or selection among
  alternatives — Curify's Creative Exploration (which the brief frames as producing *multiple*
  directions for comparison/selection) needs more structure than this.
- **The repo has no persisted trajectory data at all** — it cannot be treated as a source of
  example trajectories, only as a source of *stage vocabulary* (what steps exist, what each step's
  input/output looks like conceptually).
- **The eval set is not a benchmark** in the sense Part 6 of the brief asks for (no automated
  metrics, no step-level breakdown, no pairwise preference data) — do not present `evals.json` as
  evidence that a Curify benchmark can be this lightweight; it is evidence only that *some* rubric-
  style eval is workable as one layer, not evidence about coverage or rigor.
- **No agentic architecture, tool-use trace, or SFT-relevant data exists in this repo at all.** It
  answers "what stages/fixed-variable vocabulary might a visual-direction workflow have," not "what
  does a trajectory-SFT-ready log look like" — that question is addressed separately in
  `TRAJECTORY_SCHEMA.md` using general trajectory-SFT concepts, not anything from this repo.
