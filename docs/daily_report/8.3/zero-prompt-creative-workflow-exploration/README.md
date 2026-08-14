# Zero-Prompt Creative Workflow Exploration

**Status:** Documentation deliverable. These documents contain product and marketing research only — no product code was modified as part of this work. The code findings throughout this directory are source-code-level and were not independently runtime-verified (see the framing note below). The research was originally prepared locally and reviewed before formal repository delivery; see `REVISION_NOTES.md` for that history.

## Purpose

This directory investigates whether Curify's current product experience and external marketing ("Images for every query") match what users actually need, using PR #416 ("zero-prompt creative workflow" proposal) and a source-code-level audit of the `curify-studio` and `curify-frontend` repositories as evidence. It proposes a definition of "zero-prompt," a recommended product direction, and a phased plan — all clearly separated into what is present in source today versus what would need to be built.

**Important framing that applies to every file in this directory:** all code-based findings are **source-code-level**, not runtime-verified. Something being present in a repository's source, or referenced in a page's component composition, is not the same as it being live in production, enabled for real users, or validated by usage data. Each document says so explicitly wherever this distinction matters.

## Files in this directory

| File | Purpose |
|---|---|
| `ZERO_PROMPT_CREATIVE_WORKFLOW_EXECUTIVE_SUMMARY_ZH.md` | 中文执行摘要，面向老板和产品团队，1-2 页快速阅读 |
| `ZERO_PROMPT_CREATIVE_WORKFLOW_EXPLORATION.md` | Main English document: background, PR evidence, JTBD, three workflow concepts, recommended concept, detailed flow, capability gaps, marketing positioning, P0/P1/P2 plan, metrics, risks, and final recommendation |
| `DEMO_STORYBOARD.md` | 30-second demo storyboard for a coffee-shop-poster scenario, split into **Version A (Honest P0 Demo Plan — a production brief, suitable for external use only after it is built and runtime-verified)** and **Version B (P1 target vision, internal-only, must be labeled as a future concept)** |
| `CURRENT_PRODUCT_FLOW_AUDIT.md` | Detailed source-code and repository-composition audit of the current Curify frontend/backend flow (home, search, templates, gallery remix, generation, result/edit, export) — the evidentiary backbone for the main document |
| `PR416_EVIDENCE_MAP.md` | Item-by-item evidence map for PR #416: what the PR actually changed (2 markdown files, 0 code) vs. what it proposes vs. what similar building blocks were found in source vs. what was not found in the inspected scope |
| `REVISION_NOTES.md` | Log of what was changed in this revision pass and why |

## Recommended reading order

1. `ZERO_PROMPT_CREATIVE_WORKFLOW_EXECUTIVE_SUMMARY_ZH.md` — start here for a fast, Chinese-language overview
2. `ZERO_PROMPT_CREATIVE_WORKFLOW_EXPLORATION.md` — the full argument and recommendation
3. `DEMO_STORYBOARD.md` — what a first demo could look like, and what it must not claim
4. `CURRENT_PRODUCT_FLOW_AUDIT.md` — the underlying source-code evidence, for anyone who wants to verify a claim
5. `PR416_EVIDENCE_MAP.md` — the PR-specific fact-check, for anyone evaluating PR #416 directly

## What this is not

- Not a feature build — no product code (in `curify-studio` or the separately-hosted `curify-frontend`) was modified to produce or validate these documents.
- Not a production-runtime audit — no application was run, deployed, or clicked through; all code-based claims are source-level.
- Not a market-research report — the demand signal cited (via PR #416's Reddit sample) is explicitly a small, first-pass, non-exhaustive sample, not a validated market conclusion.

## Delivery note

This package was reviewed as local research before being copied, with only local-stage paths and status statements updated, into `docs/zero-prompt-creative-workflow-exploration-2026-08-03/` for formal repository delivery on a dedicated working branch. No research conclusion was changed as part of that delivery step — see `REVISION_NOTES.md`'s "Formal repository delivery preparation" section for exactly what was and wasn't touched.
