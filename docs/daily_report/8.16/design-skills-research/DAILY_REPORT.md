# Daily Report — Task D: Design Skills Research

**Date:** 2026-08-17 · **Branch:** `baobao/inspiration-topic-pinterest-2026-08-11` (uncommitted) · **Scope:** `docs/daily_report/8.16/design-skills-research/` only

## Exact final counts (validated programmatically against the CSV/JSONL files)

| Metric | Count |
|---|---|
| Total candidates discovered | 39 (28 initial + 7 supplementary + 4 from a focused Codex correction pass) |
| Deep-reviewed candidates | 19 |
| Discovery-only (not deep-reviewed) | 20 (11 `discovery_only` + 8 `verified`/`verified_with_caveat` source-checked but not deep-reviewed + 1 `verified_not_design`) |
| Primary sources directly verified (deep-review set) | 19 (16 fully verified, 2 verified-with-caveat, 1 partially verified) |
| Boss seed name not resolvable to any source | 1 (`design-process-pack`) |
| Boss seed resolved but not design-relevant | 1 (`composio` → general MCP/integration platform) |
| **Primary shortlist** (tightened) | **12** |
| — S tier | 5 |
| — A tier | 7 |
| Honorable Mentions / Watchlist (A-tier, cut from primary 12) | 3 (`webapp-testing`, `figma-implement-design`, `video-shotcraft`) |
| B tier (reviewed, not shortlisted at all) | 4 |
| Categories covered (candidate pool) | 17 |
| Claude-specific candidates | 20 |
| Codex-specific candidates | 4 |
| Multi-agent / generic-agent / unknown-ecosystem candidates | 11 / 3 / 1 |
| Curify capability patterns identified | 7 |
| Internal experiments proposed | 5 (0 worth_adopting / 2 worth_experimenting / 3 worth_studying) |
| Social-media-ready resources | 12 (matches the tightened primary shortlist) |
| Security-concern candidates (medium risk; none rated high) | 8 of 19 deep-reviewed |
| Blocked/unreachable or archived sources | 1 raw SKILL.md URL 404 (`hyperframes-creative`); `openai/plugins` found archived as of 2026-08-16; Xiaohongshu link not accessed (treated as discovery context only, per task instructions) |

*(Counts reconciled against `skills_candidates.csv`, `skill_reviews.jsonl`, and `skills_shortlist.csv` via a validation script — see the same counts reflected in `README.md` and `FINDINGS.md`.)*

## Top resources (5 S-tier + the flagship Codex addition)

1. **impeccable** (`pbakaus/impeccable`) — deterministic 59-rule anti-"AI slop" checker + 23 commands, works across 14 agent tools.
2. **styleseed** (`bitjaru/styleseed`) — dual-gate (rule score + rendered pixel) validation, transparently self-scores its own demo 58/100.
3. **frontend-design** (Anthropic official, `anthropics/claude-code`) — the most complete single-document design-domain knowledge reviewed.
4. **product-shots** (`motiful/product-shots`) — 14-anchor identity lock + compliance-as-prompt-fields for e-commerce imagery.
5. **guizang-social-card-skill** (`op7418/guizang-social-card-skill`) — automated layout-fault validation for Xiaohongshu/WeChat cards; directly on-topic for Objective B.
6. **Codex-Skills** (`TheGoat395/Codex-Skills`) — the strongest genuinely Codex-first candidate found; ~70 real skills spanning motion/accessibility/visual-QA/design-direction with an honestly-caveated benchmark methodology.

## Top 5 quality findings

1. Strong candidates share three traits: a real mechanism beyond the prompt, specifically-named domain knowledge, and some form of self-check — thin wrappers have none of the three.
2. Official framing (e.g. Anthropic's own `theme-factory`) doesn't guarantee depth — `theme-factory` is real but thin (no validation step) compared to Anthropic's own `frontend-design` skill.
3. A credible-sounding rule count can be an unverified marketing claim: `platform-design-skills`' "300+/450+ rules" and `ui-ux-pro-max-skill`'s "119 UX Guidelines" both couldn't be independently confirmed at the file level on inspection — flagged as insufficient evidence / unverified claim rather than assumed strong.
4. A search-surfaced popularity figure (~133k weekly installs for `web-design-guidelines`) could not be verified from the primary source and was excluded from scoring — a concrete instance of the "don't confuse stars with quality" rule in practice.
5. Genuine design knowledge and thin implementation aren't mutually exclusive — `photo-abstract-editorial` is a single unstructured prompt with no validation loop, yet contains real compositional reasoning; the rubric scores these on separate axes rather than one label.

## Top reusable Curify capability ideas

1. Deterministic anti-pattern checking (impeccable, web-design-guidelines) instead of relying only on LLM aesthetic judgment.
2. Render → screenshot → inspect → fix validation loop (excalidraw-diagram-skill, styleseed, figma-implement-design, guizang-social-card-skill, visual-verdict) — the single most transferable pattern across the whole pool; `visual-verdict`'s deterministic JSON-verdict contract is the cleanest machine-checkable version found.
3. Locked identity anchors for multi-asset consistency (product-shots).

Full list of 7 patterns with Curify workflow mapping in `CURIFY_CAPABILITY_FINDINGS.md`.

## Codex ecosystem finding

A focused Codex-specific discovery pass was run to correct an initial Claude-heavy skew (20 claude vs. 1 codex). Result: **4 Codex-specific candidates** now in the pool (vs. 20 Claude-specific, 11 multi-agent) — Codex-native design tooling is real but visibly smaller and newer on this sample: `openai/skills` is deprecated, its cited successor `openai/plugins` is now **archived**, and most Codex-usable resources found are multi-agent ports (e.g. `MengTo/Skills`) rather than Codex-first builds. `Codex-Skills` (TheGoat395) is the one clear exception — genuinely Codex-native, well-structured, and now shortlisted. Full detail in `FINDINGS.md` → Q16.

## Best proposed experiment

**E2 — Render → screenshot → one-iteration-fix loop.** Smallest, most self-contained experiment with the clearest success signal (A/B comparison of visible-defect rate with vs. without the loop on one existing generation path). `worth_experimenting`, priority 1 of 5.

## Best social-media angle

Lead with the finding, not the list: *"Most 'AI design skills' are a well-written prompt with no validation loop — the ones that actually hold up share three traits: deterministic checks, a render-inspect-fix loop, and domain knowledge specific enough to cite."* Draft in `SOCIAL_MEDIA_DRAFT.md`, Chinese-first with an English adaptation note, framed around 39 researched → 19 deep-reviewed → 12 genuinely strong (now including a real Codex-native pick, not just Claude).

## Main limitations

- Static review only — nothing was installed or executed; behavioral claims rest on reading source/docs, not independent reproduction (each review's `execution_tested` field states this explicitly).
- 20 of 39 candidates are discovery leads only, not deep-reviewed — their relevance/value fields are first impressions, not confirmed findings.
- The boss's Xiaohongshu link was not accessed directly (treated as discovery context per task instructions); one seed (`design-process-pack`) could not be resolved to any real source at all.
- Candidate count (39) runs above the task's suggested "approximately 20–30" — a deliberate choice across three discovery rounds (general, supplementary, Codex-focused) to keep independently-verified, non-redundant material (branding coverage; Codex-ecosystem coverage) rather than trim to a round number. The primary shortlist (12) was deliberately tightened back into the suggested 8–12 range; see `README.md` → Shortlist logic.
- The Codex-focused pass was one targeted search session, smaller in scope than the two Claude-oriented discovery rounds — the Codex-ecosystem finding (see above and `FINDINGS.md` Q16) is stated with that asymmetry in mind, not as exhaustive Codex coverage.

## Next action

Team review of `gallery.html` and the shortlist; if Objective A is prioritized next, start with experiment **E2** (smallest, clearest signal); if Objective B is prioritized next, review `SOCIAL_MEDIA_DRAFT.md` for platform-specific adaptation before any actual posting (this task did not publish anything).
