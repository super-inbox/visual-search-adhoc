# Task D — Claude / Codex Design Skills Research

Research/evaluation/curation only. No third-party skills were installed or executed; no repositories outside this task's target directory were modified; nothing was committed or published.

## Boss request

> "抓一些这样的 claude/codex 的 design skills，提升我们自己能力，也能作为资源发到社交媒体。可以参考，看看他们质量怎样。"

Two objectives:
- **A — Improve Curify's own capability**: study what these external skills actually do (workflow, domain knowledge, validation loops) and extract reusable principles — not install them.
- **B — Build a social-media resource pool**: identify genuinely useful, verified public design skills that could later become shareable content, plus one draft.

## Research objective and scope

Discover, statically inspect, and quality-score public Claude/Codex/coding-agent design skills, distinguishing real implementations from prompt-wrapper marketing — then translate the strongest ones into (1) Curify-relevant capability patterns and (2) a vetted external resource list. This is a documentation-only task: everything lives under this one directory, uncommitted.

## Source methodology

1. Started from the boss's 15 discovery-seed names (screenshots/Xiaohongshu link) — treated strictly as leads, not pre-verified quality signals. The Xiaohongshu link itself was not accessed; only used as context that the seeds came from a social post.
2. For each seed, used web search to locate the actual primary source (GitHub repo, SKILL.md, official docs), then fetched that primary source directly rather than relying on search-result summaries or secondary blog coverage.
3. Expanded the pool beyond the seeds via **two independent discovery passes** (GitHub topics/search, Anthropic's own `anthropics/skills` and `anthropics/claude-code` repos, adjacent repos surfaced during seed research, curated "awesome" lists used only as *pointers*, not as evidence of quality) to reach broader category coverage — including filling a category (branding) the seed list had no representative for at all.
4. Every deeply-reviewed candidate's `primary_source` URL was fetched directly at least once — and for every shortlisted candidate, a second independent fetch was done as an explicit source-verification pass before finalizing this dataset. Where a fetch failed or content couldn't be independently confirmed, the review says so explicitly (`hyperframes-creative`, `platform-design-skills`) rather than guessing.
5. One seed name (`design-process-pack`) could not be resolved to any real, findable resource and is documented as not-found. One seed (`composio`) resolved to a real, verifiable product — but that product turned out to be a general-purpose MCP/integration platform, not a design skill, and is recorded as such rather than force-fit into the design taxonomy.
6. A supplementary discovery pass (run in parallel with seed verification) surfaced 7 additional well-verified candidates not in the seed list, including Anthropic's own `canvas-design` skill and `brand-skills` — the only branding-category candidate found anywhere in this research. Two of the seven (`visual-verdict`, `brand-skills`) were deep-reviewed because they filled genuine gaps (the cleanest deterministic compare-and-fix loop found, and the only branding entry); the other five are recorded as verified candidate-pool entries for future follow-up.
7. A **focused Codex-specific correction pass** was run afterward because the pool skewed heavily Claude (20 claude vs. 1 codex at the time). Targeted search for "Codex design skill," "OpenAI Codex agent skill," "Codex Figma/visual-QA skill," etc. surfaced 4 more candidates: `Codex-Skills` (TheGoat395) — genuinely Codex-native, deep-reviewed and shortlisted; `openai/plugins` — the official repo, found to be **archived** as of 2026-08-16; `MengTo/Skills` — large (123-skill) multi-agent library with explicit, real Codex support; and a small personal port of the Claude `frontend-design` pattern for Codex. Codex compatibility was verified per-candidate from primary sources, never assumed — several other "Codex" leads found during this pass turned out to be curated lists or multi-agent tools and are recorded honestly as such, not force-classified as Codex-specific.

## Candidate pool vs. deep review

- **39 candidates** in `skills_candidates.csv` — the full discovery pool, lightly documented. This is above the task's "approximately 20–30" guidance; the overage was kept deliberately across three discovery passes (general, supplementary, Codex-focused) rather than discarding independently-verified, non-redundant material purely to hit a round number.
- **19 deep reviews** in `skill_reviews.jsonl` — candidates read closely enough (source/SKILL.md/README/workflow logic) to answer the Task D deep-review questions (purpose, real workflow vs. thin wrapper, domain knowledge, validation, Curify relevance, public-recommendation worthiness, risk).
- The other 20 candidates are recorded as discovery leads (`verification_status = discovery_only`, `verified`/`verified_with_caveat` but not yet deep-reviewed, or — for `composio` — `verified_not_design`) — found and source-checked, but not deep-reviewed. They exist in the dataset for completeness and future follow-up, not as quality claims.

## Quality rubric

`EVALUATION_RUBRIC.md` defines 10 independently-scored dimensions (A–J, 1–5 scale, plus a low/medium/high security flag) and a marketing-vs-substance classification. No single aggregate score drives tiering — S/A/B tiers are assigned from the full dimension profile plus verification status, with the explicit rule that an unverified primary source can never reach S tier.

## Shortlist logic

`skills_shortlist.csv` holds a **tightened primary shortlist of 12** deep-reviewed candidates (of 19): 5 S-tier, 7 A-tier — inside the task's suggested 8–12 range. This was deliberately cut down from an earlier 14-item draft: three A-tier candidates (`webapp-testing`, `figma-implement-design`, `video-shotcraft`) were reviewed as genuinely real and useful but are weaker fits for a *curated top-tier* list — `webapp-testing` scores lowest of any shortlisted item on design-domain depth (2/5; it's QA infrastructure, not an aesthetic design skill), `figma-implement-design`'s host repo is deprecated, and `video-shotcraft` has no automated validation loop and is more tangential to Curify's current workflows than the rest of the list. They were moved to an **Honorable Mentions / Watchlist** (see below), not discarded. `Codex-Skills` (TheGoat395) — the strongest genuinely Codex-first candidate found in either discovery pass — was added to the primary shortlist in its place. Four other deep-reviewed candidates that never made any cut (`theme-factory`, `hyperframes-creative`, `platform-design-skills`, `photo-abstract-editorial`) remain fully documented in `skill_reviews.jsonl` — being reviewed and not shortlisted is itself a finding, not an omission.

### Honorable Mentions / Watchlist

Real, deep-reviewed, A-tier resources that didn't make the tightened top-12 but are still worth citing when relevant:

- **`webapp-testing`** (Anthropic official, `anthropics/skills`) — official, well-specified browser-automation QA; excellent as a *pairing* with an aesthetic-design skill, but carries little design-domain knowledge of its own (design_domain_depth 2/5).
- **`figma-implement-design`** (`openai/skills`, now deprecated by OpenAI) — a genuinely useful 7-dimension screenshot-vs-Figma validation checklist; cite the *pattern*, not the repo, since its host is no longer maintained.
- **`video-shotcraft`** — the largest structured domain-knowledge library reviewed (152 shot-recipe cards) and highest social-media-value score (5/5) of any candidate, but no automated visual-QA loop and video/motion is more tangential to Curify's current core workflows than the rest of the primary list.

These remain candidates worth referencing in follow-up content or deeper Curify exploration — the demotion is about curation, not quality.

## Safety / static-review policy

All 19 deep reviews were done by **reading** SKILL.md/README/source content — no third-party skill was installed, no script was executed, no MCP server was added, no package was globally installed, and no credentials/API keys were used or requested. Where a candidate would require execution to fully evaluate (e.g. running `product-shots`'s image-gen pipeline, or `accesslint`'s Chrome-CDP automation), that is recorded explicitly as `execution_tested: execution_not_tested` in `skill_reviews.jsonl`, with the reason given.

## Curify capability analysis

`CURIFY_CAPABILITY_FINDINGS.md` extracts 7 evidence-backed reusable patterns (not install recommendations) mapped to specific Curify workflow areas, each with a stated minimum experimental version and known risks. `INTERNAL_EXPERIMENTS.md` turns the strongest of these into 5 concrete, unimplemented internal experiment proposals, explicitly tiered `worth_studying` vs. `worth_experimenting` (none are marked `worth_adopting` yet).

## Social-media curation

`SOCIAL_MEDIA_SHORTLIST.md` selects all 12 of the tightened primary-shortlist resources as safe, distinct, and explainable enough for public recommendation, each with a stated caveat. `SOCIAL_MEDIA_DRAFT.md` is one unpublished draft post (Chinese-first, with an English adaptation note), explicitly marked DRAFT ONLY.

## Directory structure

```
design-skills-research/
├── README.md                        (this file)
├── skills_candidates.csv            (39 candidates, discovery pool)
├── skill_reviews.jsonl              (19 deep reviews, one JSON object per line)
├── skills_shortlist.csv             (12 primary-shortlisted candidates, ranked)
├── EVALUATION_RUBRIC.md             (scoring dimensions + tiering rule)
├── CURIFY_CAPABILITY_FINDINGS.md    (7 reusable patterns, not install recs)
├── INTERNAL_EXPERIMENTS.md          (5 proposed experiments, unimplemented)
├── SOCIAL_MEDIA_SHORTLIST.md        (12 externally-shareable resources)
├── SOCIAL_MEDIA_DRAFT.md            (1 unpublished draft post)
├── FINDINGS.md                      (direct answers to the boss's 15 questions)
├── gallery.html                     (internal visual review artifact)
└── DAILY_REPORT.md                  (manager-readable summary with exact counts)
```

## Gallery usage

`gallery.html` is a static, self-contained internal artifact — open it directly in a browser. It renders one card per deeply-reviewed candidate with category/ecosystem/verification/scores/strengths/weaknesses/security-risk/shortlist status, and has client-side filters for category, ecosystem, tier, shortlist status, Curify relevance, social-media value, and security risk. It is a human-review aid only — no data lives outside `skills_candidates.csv` / `skill_reviews.jsonl` / `skills_shortlist.csv`, which remain the source of truth.

## Limitations

- Static review only — no candidate was actually installed or run, so behavioral claims (does the validation loop *actually* catch what it claims to?) rest on reading the source/docs, not on independent reproduction. Every review's `execution_tested` field is honest about this.
- The Xiaohongshu link supplied by the boss was not accessed directly; it was treated purely as context that the seed list originated from a social post, per the task's own guidance on that link's likely inaccessibility.
- Several popularity/adoption figures surfaced during search (install counts, star counts) were deliberately **not** used to drive scoring or tiering, and are flagged as unverified wherever they appear — per Task D's explicit instruction not to confuse stars with quality.
- The 11 `discovery_only` candidates and 1 `verified_not_design` candidate in the pool have not been deep-reviewed; their `initial_curify_relevance` / `initial_social_media_value` fields in `skills_candidates.csv` are first-pass impressions from search results, not confirmed findings, and should not be cited as equivalent to the deep-review data. A further 8 `verified`/`verified_with_caveat` candidates from the supplementary and Codex-focused discovery passes (`canvas-design`, `claude-wcag-accessibility-skill`, `design-system-skill`, `motion-dev-animations-skill`, `ui-ux-pro-max-skill`, `openai/plugins`, `MengTo/Skills`, the `fcakyon` Codex port) had their primary source directly fetched and confirmed real, but were not taken through the full 12-question deep-review process — treat their candidate-pool notes as verified-but-shallow, not as deep-review-equivalent findings.
- The Codex-focused pass was necessarily smaller and more targeted than the two Claude-oriented passes; 4 new candidates in one focused search session is not the same evidentiary depth as the ~35 candidates and two independent discovery rounds behind the Claude-side pool. The Codex ecosystem finding in `FINDINGS.md` is stated with that asymmetry in mind, not as a claim of exhaustive Codex coverage.
