# Manual Query Review — Top5 vs Top10 (supplement to scorer v1.1 evaluation)

**Date:** 2026-07-22 · **Basis:** existing artifacts only, no re-run

This note supplements the 2026-07-21 scorer v1.1 evaluation
(`SCORER_V1_1_EVALUATION_SUMMARY.md`, `REGRESSION_ANALYSIS.md`, `TARGETED_CASE_ANALYSIS.md`,
`FULL326_COMPARISON.csv`) in response to Jay's feedback:

1. Comparisons should look at top10, not only top5 — a label can flip on tail composition alone.
2. Some queries carry similar underlying quality but were judged/labeled differently.
3. Concrete query examples should be reviewed manually rather than read off aggregate counts.

All titles/labels below are taken verbatim from the full inspiration lists already recorded in
`eval_raw/targeted/*.json` (real server-computed RSC results, collected live 2026-07-21) and the
top-5 lists in `FULL326_COMPARISON.csv`. No benchmark was re-run and no existing numbers were
changed to produce this file.

---

## Regression cases

### 笔袋 (pencil case) — zh, stationery

| | baseline (main) | candidate (v1.1) |
|---|---|---|
| label / score | PARTIAL / 0 | **FAIL / 0** |
| total results | 17 | 8 |

**Top5 comparison**
- Baseline: `microsoft ai dilemma…gemini` ×2 (off-subject AI infographic), **`Stationery`** (correct, #3), `label printer`, `en-zh` (stationery flashcards, correct-ish)
- Candidate: **`western1`**, **`western2`** (western-food sticker templates, off-subject) at #1–#2, then the same `microsoft ai dilemma` pair, `Stationery` pushed to #5
- Main difference: the two food-sticker templates jump to the top, displacing the one genuinely on-subject item from #3 to #5.

**Top10 comparison**
- Baseline top10 adds: `moyu zhong`, `panda tea master`, `rabbit ding feng`, `busan boogi duck`, `curi ai robot keyring mug notebook pen set` — all IP/merch mockups, still mostly off-subject but at least tonally neutral.
- Candidate has only **5 total inspirations** (`totalResults=8`, `inspirationCount=5`), so its "top10" is identical to its top5 — there is no tail to recover the ranking in.
- The regression **does not soften** when the window is widened; if anything it is starker, because the candidate has nothing left to show past rank 5.

**Manual judgement:** **FAIL** — confirmed regression, not a top5 framing artifact. This is the flagship 笔袋-class case: a non-original, off-subject candidate (western-food stickers) outranks the one authentic stationery result, and widening to top10 offers no recovery because the candidate result set itself shrank.

---

### 人体图解 (human-body diagram) — zh, chart

| | baseline (main) | candidate (v1.1) |
|---|---|---|
| label / score | **PASS / 67** | **FAIL / 0** |
| total results | 303 (flooded) | 164 |

**Top5 comparison**
- Baseline: `human brain usage`, `human body bilingual science mindmap`, `human body`, `body parts`, `sleep disorder guide` — 5/5 genuine anatomy/body content.
- Candidate: `human body` (correct, #1), then **`empire state building`**, **`giant wild goose pagoda`**, **`national stadium (bird nest)`**, **`oriental pearl tower`** — 4/5 architecture, promoted via a shared `anatomy` tag.

**Top10 comparison**
- Baseline top10 adds: `fitness science guide`, `muscle fiber types`, `muscle growth mechanisms`, `supercompensation`, `hack squat tbar row incline bench press hip abductor` — all still body/anatomy-adjacent, so baseline stays coherent through rank 10.
- Candidate top10 adds: `beijing opera colorful female armor`, `ming dynasty dragon robe`, `qing dynasty buzi`, `song beizi`, `tang qixiong` — **historical costume templates**, again off-subject and again riding the same loose `anatomy` tag.
- The regression **persists and does not self-correct** in the tail; ranks 6–10 for the candidate are architecture/costume content, not a return to human-body results.

**Manual judgement:** **FAIL** — regression confirmed at top10, not just top5. The pattern (architecture at 2–5, costumes at 6–10) points to `anatomy` being an over-broad tag shared by unrelated template families, which is a distinct, reviewable finding beyond what the original targeted-case note captured.

---

### 促销海报 (promotional poster) — zh, poster_specific — *listed as regression, but data shows a same-quality reorder*

| | baseline (main) | candidate (v1.1) |
|---|---|---|
| label / score | PARTIAL / 42 | **PASS / 65** |
| total / paths | 10 / 1 | 10 / 1 |

**Top5 comparison**
- Baseline: `baby care brand`, `spring beauty festival`, `summer beach sale`, `summer snack festival`, `tech gadget sale`.
- Candidate: `tech gadget sale`, `Chinese`, `Chinese`, `baby care brand`, `spring beauty festival`.
- Main difference: pure re-ordering of the same promotional-poster template family — no new template, no rewrite path, no non-original candidate involved (`paths=1` both sides).

**Top10 comparison**
- Both sides return exactly the **same 8 items** (`baby care brand`, `spring beauty festival`, `summer beach sale`, `summer snack festival`, `tech gadget sale`, `Chinese` ×2, `The AI Content Factory`) — only the order differs. Nothing is added or dropped between top5 and top10 on either side.

**Manual judgement:** **SAME** (quality identical; label changed on order alone) — this is exactly Jay's point #2. The judge scored the reordered set 23 points higher (42→65) even though the item set is byte-identical. Treating this as a "regression" at the aggregate-label level overstates what actually changed; it should be read as judge/order sensitivity, not a ranking-quality defect.

---

## Improvement cases

### 电影海报 (movie poster) — zh, poster_specific

| | baseline (main) | candidate (v1.1) |
|---|---|---|
| label / score | FAIL / 0 | **PASS / 100** |

**Top5 comparison**
- Baseline: `buddha jumps over the wall`, `four joy meatballs`, `kung pao chicken`, `sweet and sour ribs` (4 Chinese-food recipe cards, wrong sense) then `forrest gump` (1 correct) at #5.
- Candidate: `forrest gump`, `la la land`, `titanic`, `casablanca`, `gone with the wind` — 5/5 genuine movie posters.

**Top10 comparison**
- Baseline top10 adds `la la land`, `the shawshank redemption`, `titanic`, `inception`, `the godfather` — **all correct movie posters**. Baseline's top10 is far better than its top5: the real content exists, it's just buried below 4 food-recipe cards at the head of the list.
- Candidate top10 adds `roman holiday`, `farewell my concubine`, `green book` (all correct posters), then `legendary heroes`, `brad pitt` (generic character-grid / celebrity-filmography infographics — off-subject drift starting at rank 9).

**Manual judgement:** **PASS** — improvement holds at top10, though the candidate's own tail (ranks 9–10) starts drifting off-subject. Notable: baseline's FAIL/0 is a **top-of-list precision problem**, not an absence of relevant content — its top10 is already 6/10 correct. This is a clean illustration of Jay's point #1: judging on top5 alone can make a baseline look worse than its underlying result set actually is.

---

### sticker pack — en, merch_item

| | baseline (main) | candidate (v1.1) |
|---|---|---|
| label / score | PARTIAL / 24 | **PASS / 95** |

**Top5 comparison**
- Baseline: `graduation alpaca`, `basketball tennis badminton`, `tennis volleyball soccer baseball`, `curi ai robot poses views icons`, `Bronze worker mythical beast` — mostly sports-flashcards/robot-icon sets, only loosely "sticker pack".
- Candidate: `Andrew Tate…sticker pack & merch collection`, `Cristiano Ronaldo…`, `Elon Musk…`, `Erling Haaland…`, `Harry Kane England Chibi Sticker Pack` — 5/5 literal celebrity/meme sticker packs.

**Top10 comparison**
- Baseline top10 adds `Tang horse figurine ride-share driver`, `Office plant succulent buddy`, `Anthropomorphized rubber duck product manager`, `ancient bronze beast full character sheet`, `Andrew Tate…sticker pack & merch collection` — genuine sticker-pack items start appearing by rank 9–10.
- Candidate top10 adds `Bronze worker mythical beast`, `Tang horse figurine ride-share driver`, `Office plant succulent buddy`, `Anthropomorphized rubber duck product manager`, `graduation alpaca` — stays on template families tagged `original-character-sticker-pack` / `sticker-pack` throughout.

**Manual judgement:** **PASS** — improvement holds and is more consistent top-to-bottom; the candidate keeps returning literal sticker-pack content through rank 10, while the baseline only starts recovering relevant items in the last two slots of its top10.

---

### product photo — en, product_photo

| | baseline (main) | candidate (v1.1) |
|---|---|---|
| label / score | FAIL / 0 | **PASS / 100** |

**Top5 comparison**
- Baseline: `bell peppers`, `carrots`, `lettuce`, `pineapple`, `strawberries` — gardening how-to infographics, wrong sense entirely.
- Candidate: `Organic Rolled Oats`, `Double Chocolate Cookies`, `Italian Pasta Sauce`, `choco chip cookies`, `espresso coffee beans` — 5/5 genuine product-packaging photos.

**Top10 comparison**
- Baseline top10 adds `tomatoes`, `cat`, `dog`, `hamster`, `horse` — still wrong sense (gardening/pet-care infographics), no recovery at all through rank 10.
- Candidate top10 adds `marinara sauce`, `matcha powder`, `pasta sauce`, `rolled oats`, `eyemask` — stays on genuine product/ecommerce packaging content.

**Manual judgement:** **PASS** — the cleanest win in this set: baseline stays off-subject through all 10 ranks, candidate stays on-subject through all 10 ranks. Unlike 电影海报 or sticker pack, there's no "buried in the tail" nuance here — the baseline result set itself never contains the right content.

---

### 日历 (calendar) — zh, calendar

| | baseline (main) | candidate (v1.1) |
|---|---|---|
| label / score | FAIL / 0 | **PASS / 32** |

**Top5 comparison**
- Baseline: `2026 FIFA World Cup — North American Soccer Showcase`, `Milano Cortina 2026 — Winter Olympic Games`, `Nagoya 2026 Asian Games`, `Coachella Valley Music and Arts Festival 2026`, `resort` — sports/festival event posters, only the last item calendar-adjacent.
- Candidate: `resort`, `Local Festival Schedule`, `Community Center Annual Events`, `2025 RV Resort Events`, `chiikawa 2026` — generic "annual event calendar infographic" templates, with the first genuine 12-month wall-calendar poster (`chiikawa 2026`) appearing at #5.

**Top10 comparison**
- Baseline top10 adds `beijing 798 art season 2026`, `coachella 2026 festival`, `dakar 2026 youth olympics`, `fifa world cup 2026 spanish`, `Local Festival Schedule` — still event/sports posters; no genuine wall-calendar template appears anywhere in baseline's top10.
- Candidate top10 adds `crayon shinchan 2026`, `jiji black cat 2026`, `snoopy peanuts 2026`, `studio ghibli 2026` (four more genuine 12-month calendar posters), then `2026 FIFA World Cup` (event poster, off-subject) at #10.

**Manual judgement:** **PASS** — improvement holds at top10; the candidate surfaces 5 genuine calendar templates inside its top9, while the baseline never surfaces one in its top10. The moderate score (32, not higher) reflects that candidate ranks 1–4 are still generic event-calendar infographics rather than literal wall calendars — the win is real but not yet a clean top-of-list result.

---

### logo — en, logo

| | baseline (main) | candidate (v1.1) |
|---|---|---|
| label / score | FAIL / 0 | **PASS / 57** |

**Top5 comparison**
- Baseline: `ghibli vs mappa`, `kyotoani vs ufotable 1`, `kyotoani vs ufotable 2`, `pixar vs dreamworks`, `wit vs ufotable` — anime-studio comparison infographics, entirely off-subject.
- Candidate: `Meta lays off 8,000 workers…` (editorial hero card whose prompt text mentions a "logo", borderline), `PAW PARADISE Pet Shop brand identity moodboard`, `BREW & CO Coffee Shop brand identity moodboard`, `Golden Crust Bakery…`, `GreenBasket Grocery…` — 4/5 genuine brand-identity/logo-design templates.

**Top10 comparison**
- Baseline top10 adds `Organic Rolled Oats`, `Double Chocolate Cookies`, `Italian Pasta Sauce`, `choco chip cookies`, `espresso coffee beans` — food packaging, still off-subject.
- Candidate top10 adds `Page Turner Bookstore…`, `Power Fit Gym & Fitness…`, `PAW PARADISE Cultural Creative Products…`, `PAW PARADISE IP Material Design Specification` (all more brand-identity/logo-design templates), then `ghibli vs mappa` at #10 (off-subject drift at the very end).

**Manual judgement:** **PASS** — improvement holds strongly through top10; the candidate keeps returning `logo-design`/`brand-identity`-tagged templates through rank 9, while the baseline never leaves anime-studio and food-packaging content.

---

## Summary

- **Top5-only judging can mislabel queries that are actually fine lower in the list.** 电影海报's baseline is FAIL/0 on top5 but already has 6/10 correct movie posters by rank 10 — the defect is head-of-list ordering, not absence of relevant content. sticker pack shows the same shape, milder.
- **Some "regressions" are really judge/order sensitivity on an unchanged result set, not ranking-quality defects.** 促销海报's baseline and candidate return the *identical* 8 items in both top5 and top10 — only the order changed, yet the label moved PARTIAL→PASS. This is the clearest case of Jay's point #2: same quality, different classification.
- **Other changes are genuinely tail-only and don't affect the verdict either way.** logo and 日历 both drift slightly off-subject in their last 1–2 slots (rank 9–10) without changing the overall PASS read; product photo shows no tail drift at all in either direction.
- **The most important remaining regression is the 笔袋-class single-token CJK subject-matching failure.** Unlike the other regression candidates, 笔袋 and 人体图解 do not recover or stay flat at top10 — 笔袋's candidate result set is too small to even have a tail (5 total items), and 人体图解's candidate tail fills with a *different* off-subject template family (costumes) rather than reverting to on-subject content. This confirms the original evaluation's conclusion: widening the judging window does not fix the flagship regression, so it remains the highest-priority open issue ahead of any re-run.
