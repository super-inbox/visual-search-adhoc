# Hybrid Search — Safe Rollout Plan (Design Only)

No stage below has been executed beyond Stage 1 (this audit itself). No implementation, deployment, or online test has occurred.

## Stage 1 — Static architecture audit

- **Goal**: Understand current search architecture, identify insertion points, without writing any implementation code.
- **Entry criteria**: Read access to the frontend repository.
- **Work performed**: This audit — 18 deliverables covering architecture, call graph, data contracts, provider options, trigger/mode/merge design, instrumentation design, and rollout planning.
- **Output**: This document set.
- **Go criteria**: Architecture is well-understood enough to specify Stage 2-4 concretely (satisfied — see Deliverables 1-10).
- **No-go criteria**: Key architecture code absent or repository inaccessible (not encountered).
- **Rollback condition**: N/A — read-only stage.

## Stage 2 — Provider decision and compliance review

- **Goal**: Resolve the "provider unresolved" status from the Provider Options doc — get a real, compliant Google Custom Search API (or approved alternative) account provisioned, with legal/compliance sign-off on caching duration and attribution requirements.
- **Entry criteria**: Stage 1 complete; business stakeholder agreement to pursue external image fallback.
- **Work performed**: Legal/compliance review of Google Custom Search API ToS (caching limits, attribution requirements); Google Cloud project + CSE provisioning; cost/quota confirmation from an actual account (not assumed from public docs, which may be stale).
- **Output**: A provisioned, compliant provider account with confirmed pricing/quota; documented caching policy approved by compliance.
- **Go criteria**: Compliance sign-off obtained; quota sufficient for the planned Core-80 + staging call volume.
- **No-go criteria**: Compliance flags the caching/attribution model as non-compliant; cost/quota insufficient even at MVP scale.
- **Rollback condition**: N/A — pre-implementation stage; if blocked, the whole initiative pauses here without any code risk.

## Stage 3 — Mocked/sample external-response validation

- **Goal**: Validate the proposed `ExternalSearchResult` contract (Deliverable 5) against REAL provider response shapes, using a small number of manually-authorized sample calls or officially-provided sample responses — measure real latency, verify field availability (title/domain/safe-search granularity), before committing to the Core-80 offline plan's schema.
- **Entry criteria**: Stage 2 complete (provisioned account).
- **Work performed**: Small-scale sample calls (under the account's own quota, with cost tracked) to confirm field shapes match Deliverable 5's assumptions; measure real latency distribution to inform the timeout ranges left unresolved in the Failure/Cache/Cost spec.
- **Output**: Confirmed/corrected `ExternalSearchResult` field mapping; a measured (not assumed) latency distribution; a finalized timeout value.
- **Go criteria**: Response shape matches (or the contract is revised to match) with no blocking gaps (e.g., if `source_domain` turns out unreliable, the contract/UI plan must be revised before proceeding).
- **No-go criteria**: Provider response quality is too poor/inconsistent to support the attribution/safety requirements (e.g., titles are unusable, safe-search granularity is inadequate).
- **Rollback condition**: N/A — validation-only stage, no user-facing change.

## Stage 4 — Core-80 offline five-mode experiment

- **Goal**: Execute the Core-80 plan (Deliverable 11) — 80 queries × 5 modes, produce comparative relevance/safety/engineering/cost data.
- **Entry criteria**: Stage 3 complete (contract validated, real latency known).
- **Work performed**: Run all 400 mode-runs (using the now-validated provider integration in a controlled/offline harness, not live user traffic); score relevance manually and/or with an LLM judge (per the existing relevance-labeling bootstrap gap noted in Extension B — may need to lean more heavily on manual scoring at this stage given no learned relevance model exists yet); compile the CSV and metrics.
- **Output**: `hybrid_search_core_eval_80.csv` + a metrics summary comparing all 5 modes.
- **Go criteria**: Mode E shows measurable relevance/zero-result-reduction improvement over Mode B without unacceptable safety-metric regressions (unsafe/irrelevant rate, broken-link rate, internal-preservation rate).
- **No-go criteria**: Mode E's safety metrics are unacceptable, OR no meaningful improvement over Mode B is observed (in which case the added complexity/cost of the external leg isn't justified).
- **Rollback condition**: N/A — offline stage.

## Stage 5 — Select best candidate

- **Goal**: Based on Stage 4 data, choose the trigger threshold (T0/T3/T5/other) and confirm Mode E's merge policy parameters (cap sizes, etc.) as the implementation target.
- **Entry criteria**: Stage 4 complete with a go decision.
- **Work performed**: Data review, stakeholder (including the manager) sign-off on the chosen configuration.
- **Output**: A finalized MVP spec (trigger threshold + merge caps), superseding the "candidate" framing in Deliverables 7 and 9.
- **Go criteria**: Stakeholder sign-off obtained.
- **No-go criteria**: Data is ambiguous/insufficient — extend Stage 4 with more queries or a second round before proceeding.
- **Rollback condition**: N/A.

## Stage 6 — Feature-flagged local implementation

- **Goal**: Implement Mode E behind all five feature flags (Failure/Cache/Cost spec), defaulted OFF, in a local/dev environment.
- **Entry criteria**: Stage 5 complete.
- **Work performed**: Build the external-provider client, the merge/rank logic, the new card component, the `search_id` instrumentation plumbing, the cache layer, the circuit breaker. Unit/integration tests. This is the first stage that touches source code — explicitly out of scope for THIS audit.
- **Output**: A feature-flagged implementation, mergeable to main but inert (all flags off) in production.
- **Go criteria**: Code review passed; flags confirmed independently toggleable; the "internal results never removed on external/LLM failure" guarantee verified by test.
- **No-go criteria**: Any test shows the hard failure guarantee violated.
- **Rollback condition**: Flags default OFF — no rollback needed, feature is inert by default even after merge.

## Stage 7 — Staging QA

- **Goal**: Flip flags ON in staging, verify end-to-end behavior, tune circuit-breaker thresholds and cache TTLs with real staging traffic patterns.
- **Entry criteria**: Stage 6 complete, merged to main.
- **Work performed**: Manual + automated QA in staging; load/latency testing; verify observability fields are actually emitted and queryable.
- **Output**: A staging sign-off report; tuned operational parameters.
- **Go criteria**: No P0/P1 bugs; latency within budget; observability confirmed working.
- **No-go criteria**: Any hard-guarantee violation observed; unacceptable latency.
- **Rollback condition**: Flags off in staging; no production impact regardless.

## Stage 8 — Instrumentation validation

- **Goal**: Confirm the new `search_id`/`result_source`/`rank`/generation-linkage fields are actually flowing end-to-end and are queryable by whatever analytics/admin SQL tooling the backend team uses (explicitly unverified by this frontend-only audit — see Instrumentation Plan's caveat).
- **Entry criteria**: Stage 7 complete.
- **Work performed**: Coordinate with backend/data team to confirm `/interactions/track` accepts and stores the new fields; run a synthetic search→click→generate flow in staging and verify the full funnel is joinable via `search_id` in whatever query tool is used downstream.
- **Output**: A confirmed, joinable funnel in staging data.
- **Go criteria**: A test search→click→generate sequence is verifiably joinable end-to-end.
- **No-go criteria**: Backend cannot support the new fields without its own changes — this stage may reveal Stage 6 needs backend coordination that wasn't visible from the frontend-only audit.
- **Rollback condition**: N/A — data-validation stage.

## Stage 9 — Small-traffic A/B test

- **Goal**: Run the online experiment (Deliverable 13) at small scale (e.g., single-digit percentage of traffic) to get a first real read on Search-to-Generate Rate, CTR, and guardrails.
- **Entry criteria**: Stage 8 complete.
- **Work performed**: Launch the A/B test per Deliverable 13's design; monitor guardrails daily/continuously, not just at the end.
- **Output**: A first-read experiment report.
- **Go criteria**: No guardrail breached; Search-to-Generate Rate flat-to-positive in the treatment arm (not just CTR).
- **No-go criteria**: Any guardrail breached (especially external bounce rate or generation-rate decline — the CTR-up/Generate-down pattern from Deliverable 13), OR `EXTERNAL_SEARCH_KILL_SWITCH` conditions met (external_click→curify_create conversion < 8%, per Extension C's proposed threshold, pending confirmation in Stage 5).
- **Rollback condition**: `EXTERNAL_SEARCH_KILL_SWITCH=true` — instant, independent of the other flags.

## Stage 10 — Gradual rollout

- **Goal**: Ramp traffic percentage up incrementally (e.g., 5% → 25% → 50% → 100%) only if each step's guardrails hold.
- **Entry criteria**: Stage 9 complete with a go decision.
- **Work performed**: Staged ramp with monitoring at each step; hold at each percentage long enough to get statistically meaningful guardrail reads before advancing.
- **Output**: 100% rollout, or a documented stopping point with rationale.
- **Go criteria**: Guardrails hold at each step.
- **No-go criteria**: Any guardrail breach at any step halts the ramp.
- **Rollback condition**: Step back to the previous traffic percentage, or full kill switch if the breach is severe.

## Stage 11 — Full rollback capability

- **Goal**: At every stage from 6 onward, confirm the system can be returned to Mode-B-equivalent (current production) behavior within minutes, without a deploy.
- **Entry criteria**: N/A — this is a standing capability required throughout Stages 6-10, not a terminal stage.
- **Work performed**: `EXTERNAL_SEARCH_KILL_SWITCH` (env var/remote config, no deploy needed) confirmed functional at every stage; documented incident-response runbook.
- **Output**: A verified, documented, always-available rollback path.
- **Go criteria**: Kill switch tested and confirmed to disable the external leg within the target response time (minutes, not a release cycle) at every stage from 6 onward.
- **No-go criteria**: Kill switch requires a deploy or is untested — this would itself be a blocking finding requiring remediation before Stage 9 (online traffic) proceeds.
- **Rollback condition**: N/A — this stage IS the rollback mechanism.

## Explicit statement (required)

**Direct production deployment before offline (Stage 4) and staging (Stage 7) validation is not recommended.** No stage in this plan skips ahead to production traffic before both the offline relevance/safety data and the staging functional/instrumentation validation are complete.
