# MANAGER_SUMMARY.md — Visual Direction / Creative Exploration Trajectory SFT (research only)

Research task, per manager direction: "可以看看 visual direction / creative exploration 怎么用
trajectory SFT 的方法." No frontend, backend, SFT pipeline, or model training was built or changed.

## What we learned from gc-minimal-zine-poster

It's a Codex Skill (markdown instructions for an LLM), not code or a trained agent, and it contains
**no executed trajectory logs** — it's useful only as a source of *stage vocabulary*, not as a
source of trajectory examples. What's genuinely reusable: a **fixed / variable / sample-residue**
three-way split for reference analysis; **numeric, checkable fixed-system fields** over vague
adjectives; a named **variation-axis set with an explicit anti-repetition rule**; and a **capped
single-retry regeneration loop** that reports a remaining limitation instead of overclaiming success.
Full detail and explicit "don't copy this" list in `REPO_ANALYSIS.md`.

## What trajectory SFT means for Curify

Curify's existing workflow research (8.8, five domains) captured **workflow data**: a finished
project's stages (`brief → concepts → design → final result`). Trajectory SFT needs a different
object — **trajectory data**: a record of an agent's actual decision process
(`state → decision → action/tool → observation → evaluation → next decision → revision → final output`),
including paths that were tried and rejected. Workflow-data case studies structurally cannot contain
rejected/failed paths, since published case studies only show what shipped; trajectory data is
defined by including exactly that.

## What a Curify trajectory should contain

A 10-stage structure derived from the workflow research + the external repo's stage list + the
requirement to show weak-direction handling: brief understanding → reference retrieval → reference
analysis → direction generation → direction evaluation → selection → critique (conditional) →
revision (conditional) → generation → final output. Full schema (trajectory-level and step-level
fields) in `TRAJECTORY_SCHEMA.md`. Every field is an observable, short, structured statement —
no hidden chain-of-thought is required or proposed.

## 4 proposed trajectory examples

`CURIFY_TRAJECTORY_EXAMPLES.jsonl` — coffee shop, brand/logo, poster, packaging. All 4 lines parse
independently as JSON. The coffee-shop example demonstrates the required weak-direction path: a
high-saturation candidate is generated, evaluated as mismatching the brief's "calm" requirement,
rejected with a stated reason, and a separate thumbnail-legibility defect on the winning candidate
is caught and fixed in one capped revision pass. The packaging example demonstrates a disclosed
partial-success case (thin reference retrieval), not hidden as a clean success. **These are labeled
PROPOSED examples for schema illustration — not historical production logs.**

## How the benchmark should work

Three separate layers, never collapsed into one score: **step-level** (is each decision/evaluation
good on its own), **trajectory-level** (does the sequence hang together — did evaluation actually
drive selection, did critique actually get addressed), and **final-output** (does the deliverable
match the brief). Eleven evaluation dimensions are defined in `BENCHMARK_PROPOSAL.md`, each split
into rule-based checks (dimensions, required text, revision-loop length), LLM-judge checks (brief
understanding, reference understanding, alignment, critique correctness), and human-only review
(direction-diversity meaningfulness, final craft quality). No single scalar "visual quality" score
is proposed — subjective craft judgment stays human-reviewed.

## Smallest next pilot

**Benchmark first, training later.** 10–20 Creative Exploration tasks across 2–3 domains, manually
authored or manually logged as full trajectories (not just final images), deliberately including
both clean successes and failed/revised cases, graded by hand against the proposed dimensions to
test whether they're actually gradable — and only then check whether an LLM-judge roughly tracks
human judgment on the subset proposed for automation. No trajectory-SFT training should start before
this pilot shows the dimensions are gradable at all.

## ChatGPT shared-discussion access

The link (`https://chatgpt.com/share/6a7bbf58-43b8-83e8-8968-e0c4662840bf`) was **not accessible**.
WebFetch returned only the page title ("ChatGPT - Agentic AI Architecture State") with no body
content — the share page is a JavaScript-rendered SPA that doesn't serve its content to a
non-interactive fetch. Interactive browser access was also attempted but the Chrome extension used
for that was not connected in this environment. No content from that discussion was used or invented
anywhere in this task; everything above is derived from the gc-minimal-zine-poster repo and the
existing Curify workflow research only. If the discussion content matters, please re-share it
directly (paste text, or a reachable export) in a future session.
