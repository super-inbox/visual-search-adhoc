# Internal Experiments (Proposed, Not Implemented)

Five small experiments derived from `CURIFY_CAPABILITY_FINDINGS.md`. None of these have been implemented as part of Task D — this is a recommendation list for the team to pick up separately. Each is explicitly classified as **worth_studying**, **worth_experimenting**, or **worth_adopting**; the three tiers are not equivalent, and nothing here has graduated to `worth_adopting` yet.

---

### E1 — Static "known failure mode" checklist for generated output

| Field | Value |
|---|---|
| experiment_id | E1 |
| name | Curify generic-output checklist |
| external_inspiration | `impeccable` (C01) deterministic 59-rule anti-pattern engine; `web-design-guidelines` (C06) 100+ rule audit |
| current_problem | Generated design/frontend output sometimes reproduces generic, repeatable defaults without a fast, cheap way to catch it before human review |
| hypothesis | A short static checklist of Curify's own recurring generic-output patterns, run before delivery, catches a meaningful share of "obviously needs a redo" cases without an extra LLM call |
| minimum_implementation | Write down 10–15 concrete, Curify-specific anti-patterns (not a copy of impeccable's list — ours will differ) as a plain checklist; manually apply it to a sample of recent generated outputs to see how many it would have flagged |
| Curify_workflow | Design generation, frontend visual generation |
| expected_benefit | Cheaper first-pass filtering than always relying on LLM aesthetic judgment; a versioned, auditable list the team can argue about and improve over time |
| risk | List goes stale as visual trends shift; risk of flagging legitimately good choices if rules are too rigid |
| validation_method | Manually score the checklist's flags against human judgment on a sample of past outputs (precision/recall on "would a reviewer have rejected this?") |
| success_signal | Checklist agrees with human reviewer judgment on a clear majority of a sampled batch, with few false positives on outputs that were actually fine |
| priority | worth_studying (write the checklist and backtest it manually first; do not build tooling yet) |

---

### E2 — Render → screenshot → one-iteration-fix loop

| Field | Value |
|---|---|
| experiment_id | E2 |
| name | Single-iteration visual self-correction |
| external_inspiration | `excalidraw-diagram-skill` (C08) render-screenshot-fix loop; `styleseed` (C14) dual-gate rule+pixel verification; `guizang-social-card-skill` (C13) `validate-social-deck.mjs`; `visual-verdict` (C30) deterministic JSON-verdict + numeric threshold gate |
| current_problem | Some generated visual artifacts have layout issues (overflow, misalignment, collision) that are invisible in source but obvious once rendered |
| hypothesis | Adding exactly one render→inspect→fix pass before delivery measurably reduces the rate of visually-broken output, for a bounded added cost |
| minimum_implementation | Pick one existing Curify generation path that already produces a renderable artifact; add a single screenshot-and-critique step (LLM vision call or a small scripted checker for a few concrete faults) with at most one automatic fix attempt, then stop regardless of outcome |
| Curify_workflow | Frontend visual generation, visual QA |
| expected_benefit | Fewer visually broken deliverables reaching human review; a template pattern reusable in other generation paths if it works |
| risk | Added latency and (if using an LLM vision call) added cost per generation; a badly-scoped "fix" step could make output worse, not better |
| validation_method | A/B comparison: same generation requests run with and without the loop, human-rated for visible defects |
| success_signal | Statistically noticeable drop in "visibly broken" rate in the with-loop group, without a comparable rise in generation time that breaks the workflow's usability |
| priority | worth_experimenting (highest priority — smallest, most self-contained experiment with the clearest success signal) |

---

### E3 — Locked identity anchors for multi-asset batches

| Field | Value |
|---|---|
| experiment_id | E3 |
| name | Identity-anchor propagation for generation sets |
| external_inspiration | `product-shots` (C10) 14-anchor identity lock across a 9-angle shoot |
| current_problem | When Curify generates multiple related assets in one batch (e.g. variants, multiple angles/views of a direction), visual consistency across the batch is not guaranteed by independent generation calls |
| hypothesis | Extracting a small, explicit set of "locked" attributes from the first accepted generation and re-injecting them into subsequent calls in the same batch improves cross-asset consistency |
| minimum_implementation | On one existing multi-asset generation flow, extract 5–8 concrete attributes from the first output (not a full re-description) and pass them explicitly into the next 2–3 generations in the batch; compare consistency against the current no-anchor baseline |
| Curify_workflow | Design generation, manufacturing output QA |
| expected_benefit | More usable multi-asset sets without needing a larger model or more generation attempts |
| risk | If the first generation has a flaw, the anchors propagate that flaw through the whole batch; anchor extraction itself needs to be reliable |
| validation_method | Human side-by-side comparison of batch consistency with vs. without anchor propagation, on a fixed set of test requests |
| success_signal | Clear, human-visible improvement in cross-asset consistency in the anchor condition, without a new failure mode (e.g. anchors "locking in" an early mistake) dominating the result |
| priority | worth_experimenting |

---

### E4 — Reference-to-token extraction step before generation

| Field | Value |
|---|---|
| experiment_id | E4 |
| name | Explicit reference decomposition step |
| external_inspiration | `styleseed` (C14) `/ss-reference`; `designer-skills` (C12) named aesthetic philosophies with concrete parameters |
| current_problem | Curify's inspiration-to-direction workflow already interprets references, but it's worth checking whether making the extraction step *explicit and inspectable* (a named, listed set of tokens) outperforms an implicit one |
| hypothesis | Converting a user's inspiration reference into 5–8 explicit, named tokens (palette, type mood, spacing rhythm, a named style-family label) before generation produces output that's easier to audit and at least as good as, if not better than, direct reference-to-generation |
| minimum_implementation | Prototype the extraction step in isolation (produce the token list only, don't wire it into generation yet) on a handful of real inspiration references already in Curify's pipeline, and have a human check whether the tokens accurately capture what mattered in each reference |
| Curify_workflow | Reference understanding, inspiration-to-direction workflow, Creative Direction / Brand Direction |
| expected_benefit | A more auditable, debuggable middle layer between "user's inspiration" and "what got generated" — useful even before/independent of any generation-quality change |
| risk | Extraction could be lossy or systematically miss the attribute that actually mattered for a given reference; adds a step to a pipeline that already works reasonably well |
| validation_method | Human review: for each sampled reference, does the extracted token list match what a designer would say mattered about that reference? |
| success_signal | Human reviewers agree the token list captures the reference's key properties for most sampled cases |
| priority | worth_studying (prototype the extraction step alone first — do not wire into the live generation path until the extraction itself is judged reliable) |

---

### E5 — Lightweight automated layout-fault script for generated marketing/social assets

| Field | Value |
|---|---|
| experiment_id | E5 |
| name | Layout-fault linter for generated social/marketing assets |
| external_inspiration | `guizang-social-card-skill` (C13) `validate-social-deck.mjs` (catches overflow, footer collision, density, line-break, and margin-drift faults) |
| current_problem | If/when Curify or its team produces generated social/marketing assets (including for its own content, per Objective B of this task), there's no automated check for common layout faults before publishing |
| hypothesis | A small script checking a handful of concrete, cheap-to-detect layout faults (text overflow, element collision, insufficient contrast) catches a useful share of embarrassing publish-time mistakes |
| minimum_implementation | Write a small standalone script (not tied to any specific generator) that takes a rendered HTML/image asset and checks for 3–5 concrete fault classes, run manually against a handful of past or draft assets |
| Curify_workflow | Manufacturing output QA, any future Curify-produced marketing/social content |
| expected_benefit | Cheap, fast, reusable check independent of any specific generation pipeline |
| risk | Narrow scope — only catches the fault classes it's explicitly written to check for; false sense of security if treated as a complete QA pass |
| validation_method | Run against a batch of already-known-good and already-known-bad assets; check it correctly flags the bad ones and doesn't flag the good ones |
| success_signal | Correctly distinguishes known-bad from known-good assets in the test batch |
| priority | worth_studying (useful but lowest urgency of the five — build only if E2 proves the render-then-check pattern is worth investing in further) |

---

## Summary

| ID | Name | Classification | Priority order |
|---|---|---|---|
| E2 | Render→screenshot→one-iteration-fix loop | worth_experimenting | 1 (start here) |
| E3 | Locked identity anchors for multi-asset batches | worth_experimenting | 2 |
| E1 | Static generic-output checklist | worth_studying | 3 |
| E4 | Reference-to-token extraction step | worth_studying | 4 |
| E5 | Layout-fault linter for social/marketing assets | worth_studying | 5 |

No experiment here is recommended as `worth_adopting` yet — all five are proposals to prototype and validate internally, not conclusions to act on directly.
