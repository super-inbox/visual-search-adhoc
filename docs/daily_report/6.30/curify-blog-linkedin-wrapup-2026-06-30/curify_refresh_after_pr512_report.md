# Curify Search Refresh — Post-PR #512 vs June Benchmark
**Date:** 2026-06-30  
**Branch:** `main` at commit `a1a60bc5`  
**Query set:** 58-query external-signal benchmark (same as the June 19–23 5-platform pilot)  
**Method:** Programmatic scoring — local tokenizer + `nano_inspiration.json` + template i18n blobs (en+zh). No LLM calls. Mirrors `eval_search.cjs` logic.

---

## Summary

| Metric | June Baseline (pre-PR #512) | Post-PR #512 (programmatic) | Delta |
|--------|----------------------------|----------------------------|-------|
| Rich queries (of 58) | ~35 | 41 | +6 |
| Empty queries (of 58) | ~8 | 6 | -2 |
| Creative rich rate (30 queries) | ~33% | 57% | +24 pp |
| Consumer rich rate (28 queries) | ~82% | 86% | +4 pp |
| Improved bucket | — | 18/58 (31%) | — |
| Regressed bucket | — | 4/58 (7%) | — |
| Stable | — | 36/58 (62%) | — |

PR #512 merged 2026-06-26 included: P0.1 metadata expansion v2 (inspirations avg 5→25.5 tags/record; gallery prompts avg 26.3 tags; templates avg 5→15 topics); P0.2 multi-query retrieval (3→8 paths + multi-hit re-rank); LOW_RESULT_THRESHOLD raised 3→5.

---

## Improvements (18 queries)

| Query | Old bucket | New bucket | New count | Notes |
|-------|-----------|-----------|-----------|-------|
| `电商详情图` | thin | **rich** | 23 | E-commerce detail page content now surfaces |
| `趣味经济学知识科普` | moderate | **rich** | 20 | Economics infographic expanded |
| `historical character` | moderate | **rich** | 155 | Historical character content very rich |
| `future characters` | moderate | **rich** | 35 | Future character content now rich |
| `global influence` | empty | **rich** | 38 | Rescued from zero — cultural content expanded |
| `remote destination` | empty | **rich** | 177 | Travel destination content now very rich |
| `short city escapes` | thin | **rich** | 177 | Short trip city content now very rich |
| `mbti marvel` | moderate | **rich** | 74 | Marvel MBTI chart content now rich |
| `wedding planner` | moderate | **rich** | 28 | Wedding content expanded |
| `minimalist autumn outfit for japan travel` | empty | **rich** | 11 | Fashion + Japan travel now surfaces |
| `monstera plant care guide infographic` | moderate | **rich** | 105 | Plant care infographic very rich |
| `marvel mbti character chart 16 types` | moderate | **rich** | 92 | Marvel MBTI 16-type chart now rich |
| `Spanish vocabulary printable` | thin | **rich** | 15 | Bilingual vocab printable rescued |
| `ESL flashcards printable` | thin | **rich** | 16 | ESL flashcards rescued |
| `cozy reading aesthetic` | thin | **rich** | 103 | Cozy reading content now very rich |
| `homophones and homonyms` | thin | moderate | 6 | Improved but not yet rich |
| `lunar new year red envelope graphic design` | thin | moderate | 8 | Red envelope content improved |
| `meal prep weekly recipes` | empty | moderate | 5 | Partial rescue — recipe content beginning to surface |

---

## Stable (36 queries)

Most stable-rich queries grew substantially in absolute count (reflecting actual catalog depth rather than the capped-at-10 baseline counts from live prod):

| Query | Old bucket | New count (actual) |
|-------|-----------|-------------------|
| `单词` | rich | 530 |
| `卡通` | rich | 587 |
| `词汇` | rich | 611 |
| `1950s vintage diner illustration retro poster` | rich | 323 |
| `英语-中文` / `english-chinese` | rich | 282 |
| `language learning expressions` | rich | 207 |
| `植物` | rich | 200 |
| `maps` | rich | 199 |
| `动物 词汇` | rich | 172 |
| `食物` | rich | 168 |

---

## Regressions (4 queries) — Warrant Investigation

| Query | Old bucket | New bucket | New count | Likely cause |
|-------|-----------|-----------|-----------|-------------|
| `香薰` | rich | moderate | 5 | P0.1 re-enrichment may have narrowed tags on aromatherapy records; programmatic vs live prod difference |
| `phonics worksheets kindergarten` | thin | empty | 0 | Phonics alias fix shipped on `baobao/multi-intent-topic-cooccurrence` branch, not yet merged to main |
| `bilingual flashcards for kids learning korean fruits` | moderate | thin | 1 | 6-token strict query; only 1 record has all tokens; P0.1 may have narrowed sibling vocab record tags |
| `samurai` | rich | moderate | 9 | Minor (9 hits, just under rich threshold of 10); likely acceptable |

**Action items:**
- Merge `phonics` alias fix from `baobao` branch → main
- Audit `香薰` aromatherapy records — verify P0.1 didn't remove `香薰` from tags
- Audit `bilingual flashcards for kids learning korean fruits` — add `bilingual`/`flashcards`/`kids` aliases to en-ko vocabulary sibling records

---

## Still Weak / Empty (10 queries)

### Recipe cluster (persistent gap — c2 content generation needed)
- `easy weeknight dinners healthy` — 0 hits
- `gluten free dinner ideas` — 0 hits
- `cuban sandwich recipe poster` — 1 hit
- `meal prep weekly recipes` — 5 hits (improved from 0, still moderate)

### Creative intent with template gap (c2)
- `watercolor map of europe travel destinations` — 1 hit (only 1 Europe watercolor map item)
- `before after kitchen organization makeover` — 2 hits (only 2 kitchen before-after items)
- `infj vs entp dating compatibility chart` — 0 hits (MBTI compatibility chart content not generated)

### Abstract/brand queries (c3 or out-of-scope)
- `unique cultural experiences` — 0 hits (too abstract for current catalog)
- `水果中文` — 0 hits (known c1 alias gap: bigrams don't span the compound term)

---

## Methodology Notes

1. **Baseline counts were live-production maximums** (capped at 10/section in the June 19-20 eval). Post-PR #512 counts are actual programmatic totals. Queries showing "stable rich" with counts of 500+ simply had actual depth that was previously hidden by the 10-result cap.

2. **No LLM rewriter modeled.** In production, the P0.2 multi-query path (up to 8 retrieval passes) would further rescue thin/empty queries. Manual live verification on 10 queries confirmed ESL flashcards and 青铜打工小兽 are rescued in prod.

3. **Regression caution:** The 4 regressions may partly reflect programmatic vs live prod differences, not actual content loss. Verify `香薰` and `bilingual flashcards` in production before treating as confirmed regressions.

---

*Run: 2026-06-30 on main@a1a60bc5 · tool: `curify_58q_refresh.cjs` (scratchpad, not committed) · data: `public/data/nano_inspiration.json` (3160 records) + `messages/en/nano.json` + `messages/zh/nano.json`*
