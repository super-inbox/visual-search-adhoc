# Curify 68-Query Manual Relevance Audit Guide — 2026-07-09

## Purpose

This guide accompanies `curify_68_manual_relevance_audit_2026-07-09.csv`, a per-row audit sheet built from `docs/daily_report/7.9/curify_search_auto_collect_with_claude_relevance_2026-07-07.csv`. It exists to support a **human, ground-truth relevance pass** over the 68 executed Curify gold queries — Claude's first-pass labels (`claude_relevance_label`, `claude_issue_type`, `claude_relevance_reason`, `claude_confidence`) are carried into the sheet for reference, but the `human_*` columns are intentionally left blank for manual judgment.

**Why this matters:** Claude's first pass returned **PASS = 0 out of 68 (0%)**, with FAIL = 43 (63.2%) and WARN = 25 (36.8%). A 0% PASS rate across every single query in a gold set is an unusual result and is worth independently verifying rather than taking at face value — either Curify's search really is failing on every one of these 68 queries to some degree (plausible, given how much of this audit's competitor-screenshot evidence supports real retrieval gaps), or Claude's first-pass grading criteria were stricter than a reasonable human bar for "good enough to use," or some mix of both. This audit sheet is the tool for resolving that question with actual human judgment, row by row.

The original source CSV (`curify_search_auto_collect_with_claude_relevance_2026-07-07.csv`) has **not** been modified — this audit lives in a separate file under `docs/daily_report/7.9/manual_review/`.

## Manual Audit Criteria

Use these four labels for `human_relevance_label`. They mirror Claude's original label set (PASS/WARN/FAIL) plus one new option (UNCLEAR) for cases the metadata-only first pass couldn't have used but a human reviewer legitimately needs:

### PASS
- Top results clearly satisfy the query intent.
- Subject/entity and expected content type are both mostly correct.
- The user could reasonably use the results directly, without needing to reformulate the query.

### WARN
- Some relevant signal exists, but results are too broad, incomplete, or mixed with off-topic items.
- Subject is right but format is wrong, or format is right but subject is weak/generic.
- A user would need to refine the query, scroll past irrelevant items, or settle for an approximate match.

### FAIL
- Zero result.
- Results are off-topic (the subject, not just the format, is wrong).
- A named entity or Chinese compound phrase was decomposed/segmented incorrectly, losing the query's actual intent.
- The expected content type is entirely missing from the result set.
- Results do not satisfy the query intent in any usable way.

### UNCLEAR
- The screenshot is missing, didn't load, or is unreadable.
- The query intent itself is ambiguous enough that even a confident human can't judge relevance either way.
- The reviewer genuinely cannot decide with the available evidence — use this rather than forcing a PASS/WARN/FAIL guess.

**Using `human_issue_type_override`:** if your judgment agrees with Claude's `claude_issue_type` tags, leave this blank (or copy them over) — no need to restate agreement. Use this column specifically to correct, add, or remove tags when your read differs (e.g., you find the real problem is `low_result` and not `wrong_decomposition`, or vice versa).

**Using `human_needs_followup`:** mark `yes` for anything that should get a live re-check against Curify (e.g., a zero-result row where you want to confirm it's still zero today, or a case where the screenshot alone isn't conclusive), otherwise leave blank or mark `no`.

## Recommended Review Order

Given 68 rows, review in this order to get the highest-value corrections first and de-risk the most surprising finding (PASS = 0) as early as possible:

1. **First, check all 25 rows Claude labeled WARN.** These are the rows most likely to flip to PASS on human review, since WARN by definition already carries "some relevant signal" — if the PASS=0 finding is going to be corrected anywhere, it's most likely to happen here. See the pre-sorted candidate list below for where to start.
2. **Then check the P0 FAIL rows** (the 42 `recommended_manual_review_priority = P0` rows) — these are Claude's highest-confidence, highest-priority failures, and the ones most likely to be cited in a report or PR, so they deserve direct human confirmation before being relied on.
3. **Then check zero-result rows specifically, to confirm they are truly zero.** 11 rows carry `zero_result` in `claude_issue_type` — for these, the human check is narrower than a full relevance judgment: just confirm the screenshot genuinely shows "no results" (not a broken capture or a mis-recorded count), since a real zero-result is the least ambiguous kind of failure and the fastest to confirm.
4. **Finally, review any remaining rows with low Claude confidence** (`claude_confidence = medium` or `low`) that weren't already covered by steps 1-3 — these are the rows where Claude itself flagged the most uncertainty, so they benefit most from a second opinion even if they weren't WARN or P0.

This order front-loads the rows most likely to change the headline PASS=0 finding (step 1), then works through the rows most likely to be used externally (step 2), then closes out the mechanically-easiest checks (step 3) and the residual uncertainty (step 4).

## How to Use the `suggested_human_check_focus` Column

Each row's `suggested_human_check_focus` was generated from that row's `claude_issue_type` tags, so the instruction is tailored to what Claude's first pass suspected was wrong — but you are not limited to only checking that. Typical instructions you'll see:

- *"Check whether zero-result is real..."* — for `zero_result` rows.
- *"Check whether the Chinese compound phrase was segmented correctly..."* — for `wrong_decomposition` rows with Chinese-language queries.
- *"Check whether the named entity or compound term was preserved..."* — for `wrong_decomposition` rows in English.
- *"Check whether the result matches the expected content type/format..."* — for `missing_content_type` rows.
- *"Check whether the result is broad but still usable..."* — for `competitor_gap` rows, and appended to every WARN row as a prompt to reconsider PASS.
- A confidence-specific reminder (*"First-pass confidence was only 'medium'..."*) is appended wherever `claude_confidence` was medium or low.

Multiple instructions are joined with ` | ` when a row carries multiple issue tags — work through each clause in order.

## Limitations

- This guide and the accompanying CSV are a **structuring tool**, not a substitute for actually opening each screenshot. The `suggested_human_check_focus` text is generated from Claude's own first-pass tags, so it inherits any blind spot in that first pass — if Claude mistagged a row's issue type, the suggested focus for that row may point you in a slightly wrong direction. Use it as a starting hint, not a constraint on what you're allowed to notice.
- The screenshots referenced (`docs/daily_report/7.7/curify_search_screenshots_2026-07-07/`) are from the original 2026-07-07 execution run — if Curify's index has changed since then, a screenshot-only review could miss a since-fixed or since-broken case. The `search_url` is available in the original source CSV for anyone who wants to re-run a specific query live.
- This is the full 68-row set, not just the 12-case sample that received full competitor-screenshot comparison elsewhere in this audit (`VISUAL_RELEVANCE_AND_COMPETITOR_COMPARISON_2026-07-09.md`). For those 12 overlapping rows, you already have a second, independent data point (competitor screenshots) to cross-check against your manual judgment here.
