# Hybrid Search — Business Metrics and Online Experiment Design (Design Only)

Design only — no online experiment has been run or scheduled by this audit. This document is a plan for a *future* test, contingent on all prior offline/staging stages (Rollout Plan, Deliverable 14) passing first.

## Design

- **Control**: current production search (Mode B — internal + LLM rewrite, no external leg).
- **Treatment**: Controlled Hybrid MVP (Mode E, per Mode Matrix).
- **Unit of randomization**: recommend session-level (not query-level) — a user should see a consistent experience across their session rather than flipping between hybrid and non-hybrid on successive searches, which would confound any generation-funnel metric that spans multiple searches within a visit. (This is a recommendation; the exact randomization unit should be confirmed against whatever experimentation framework Curify actually uses — not verified to exist in this frontend repo.)

## Primary business metrics

- **Search-to-Generate Rate** = generation events attributable to a search session / total qualifying searches. Requires the `search_id` → generation linkage from the Instrumentation Plan to compute correctly; without it, this metric can only be approximated via the existing lossy heuristic join, which should be flagged as a stated limitation of any early read of this metric.
- **Successful Generation Rate** = successful generations / generate-button clicks. Requires the `generation_success` field (currently does not exist — Instrumentation Plan) to distinguish "clicked generate" from "generation actually completed."

## Secondary metrics

- **Search CTR** — clicks on any result / searches with ≥1 result shown.
- **Internal-result CTR** — clicks on internal results specifically / searches with ≥1 internal result shown.
- **External-result CTR** — clicks on external results / searches where the external rail rendered. Only meaningful in the treatment arm.
- **Search refinement rate** — fraction of searches followed by another search within the same session (a proxy for "the user didn't find what they wanted and tried again"). Not currently instrumented (no session-level search-sequence tracking confirmed) — would need to be newly built, likely by joining `search` events on `session_id` ordered by time, which becomes precise once `search_id` exists per event.
- **Search abandonment rate** — searches with zero clicks on anything (internal or external) before session end.

## Guardrails (must not regress beyond agreed bounds)

- **P50/P95 search latency** — must not regress beyond an agreed bound versus Mode B's current production latency. Exact current P50/P95 is UNKNOWN from this frontend-only audit (would require production APM/monitoring data not available in this repo) — must be measured as a pre-experiment baseline, not assumed.
- **External API error rate** — tracked via the observability fields in the Failure/Cache/Cost spec.
- **External bounce/exit rate** — fraction of external-result clicks where the user does not return to Curify (or does not subsequently interact with Curify) within a defined window. This is the guardrail Extension C's own kill-switch is built around ("if `external_click → curify_create` conversion < 8%, kill the rail").
- **Internal click cannibalization** — did internal-result CTR *decrease* in the treatment arm relative to control, holding query mix constant? A drop here would mean external results are displacing attention from internal results Curify actually wants clicked, not just filling genuine gaps.
- **Cost per search** — `rewrite_cost_estimate + external_cost_estimate`, averaged over all searches (not just triggered ones), must stay within an agreed budget — ties directly to the Failure/Cache/Cost spec's cost-tracking recommendation.
- **Unsafe/irrelevant external result rate** — carried over from the offline Core-80 measurement, now measured on real traffic.
- **Broken link/image rate** — same.
- **Generation rate decline** — the ultimate guardrail: if Search-to-Generate Rate *decreases* in the treatment arm even while CTR increases, that is grounds for an automatic stop, not just a data point (see below).

## The CTR-up / Search-to-Generate-down failure pattern (required analysis)

**Why this could happen**: external links may attract clicks (novelty, broader/more relevant-looking content, especially for niche/long-tail queries the internal catalog genuinely doesn't cover) but take users away from Curify — clicking an external result opens a third-party page in a new tab, and that page has zero motivation to route the user back into a generation flow unless the "Make with Curify" CTA is both present and compelling. A user who clicks an external Pinterest/blog/stock-photo page and finds what they visually wanted may simply stop there — CTR (which counts the click) goes up, but Search-to-Generate (which requires a subsequent generation event) goes down, because the click *satisfied* the user's need without ever routing them back into Curify's product.

This is not a hypothetical edge case — it is the single most likely way "the feature looks like it's working" (higher engagement, higher CTR) while actually **cannibalizing the metric that matters** (fewer generations, i.e., less actual product value delivered). It is precisely why:
- The manager's stated business question is "do users click AND generate," not just "do users click."
- Extension C already anticipated this and built the kill-switch around `external_click → curify_create` conversion specifically, not around external CTR alone.
- This audit's recommendation (below) is to define online-experiment success using Search-to-Generate Rate as the primary metric, with CTR metrics demoted to secondary/diagnostic status.

## Explicit statement (required)

**Do not define success using CTR alone.** CTR should be read as a *diagnostic* signal (did people notice and engage with the new rail) but the **decision to ship or roll back must be gated on Search-to-Generate Rate and Successful Generation Rate**, with the external-bounce and cannibalization guardrails as hard stop conditions independent of whether the primary metric looks positive. A treatment arm that improves CTR while Search-to-Generate Rate is flat-to-negative should be treated as a **failed experiment**, not a partial win.
