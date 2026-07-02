# C2 small batch — recipe family (2026-07-02)

_Follow-up to `docs/daily_report/6.30/p0-p1-gap-retest-2026-06-30/report.md`. Scope: **recipe family only** — 3 of the 14 c2 (content-generation) gaps from that retest. All other c2 families left untouched per instruction._

**Implementation repo:** `~/Desktop/curify-frontend` (branch `baobao/c1-c2-gap-fixes-2026-07-02`, uncommitted, not pushed). This repo (`visual-search-adhoc`) has no `public/data/nano_inspiration.json`, `scripts/eval_search.cjs`, or templates — it is docs/reporting-only, so all data/config/image changes live in `curify-frontend`. The branch already had 2026-07-02's c1 alias fixes committed (`2af3ca2f`, see `curify-frontend/docs/search-c1-c2-small-batch-2026-07-02.md`); this batch continues on top of that, still uncommitted.

## Scope

- Only the **recipe family** c2 gaps from the 6/30 retest queue item 1 ("Recipe family: weeknight healthy dinners, gluten-free, meal prep").
- Exactly 3 new records / 3 new images generated. No more.
- No other c2 family touched (architecture landmarks, food sandwich series, en-ko vocab, then-vs-now, vintage stamps, warmup variants, Paris itinerary, watercolor maps, before-after rooms — all still open, see Deferred section).
- No matcher/tokenizer/ranking code touched — content + config + data only.

## Target queries

- `easy weeknight dinners healthy`
- `gluten free dinner ideas`
- `meal prep weekly recipes`

## Template decision

The retest report suggested `template-recipe` for this family. On inspection, `template-recipe`'s base prompt is hardcoded to a **Chinese New Year's Eve dinner** aesthetic (gold foil / paper-cutting / calligraphy, 年夜饭 framing) regardless of the `dish_name` param — a poor semantic fit for "weeknight," "gluten-free," and "meal prep" queries. Used **`template-premium-recipe-card-infographic`** instead (also listed as a valid template for all 3 gaps in the retest report): a neutral rustic recipe-card infographic (hero photo + prep/serving info bar + ingredients grid + 6-step instructions grid), higher rank_score (90.3 vs 80.3), and already has 7 similar shipped examples to pattern-match against.

## Files changed

| File | Change |
|---|---|
| `curify-frontend/scripts/configs/recipe_c2_batch_2026-07-02.json` | New — 3-entry batch-gen config |
| `curify-frontend/public/data/nano_inspiration.json` | +3 new records (156 lines added, 0 unrelated lines touched) |
| `curify-frontend/public/images/nano_insp/*.jpg` (×3) | New — full-size generated images. **Gitignored** (`public/images/` is in `.gitignore`), so they won't show in `git status` — they ship via the Vercel build picking up `public/` directly, not via git. |
| `curify-frontend/public/images/nano_insp_preview/*-prev.jpg` (×3) | New — preview images, same gitignore note |
| `visual-search-adhoc/docs/daily_report/7.2/c2-recipe-batch-2026-07-02.md` | This report |

No CDN sync attempted — `gcloud`/`gsutil` are not installed on this machine (same limitation already logged in the prior C1/C2 report for the MBTI item). Images are local-only; safe to reuse for a future `--sync` run once tooling is available.

## Generated records/images

Ran via the documented pipeline (`docs/batch-generation.md`): `node scripts/generate_template_examples.cjs --config=scripts/configs/recipe_c2_batch_2026-07-02.json --dry-run` (validated, 0 collisions) then the same command without `--dry-run`. Auto-tag (gpt-4o-mini) ran and seeded baseline bilingual aliases; I then manually merged in the exact alias lists you specified on top (no duplicates — dedup was case-insensitive).

## Eyeball QA table

All 3 records manually eyeballed and **PASS** (2026-07-02, by Baobao). Safe to proceed to commit.

| Record ID | Target query | Image path (local, no CDN yet) | Modified file | Aliases added (your list, on top of auto-tag) | Eyeball status | Notes |
|---|---|---|---|---|---|---|
| `template-premium-recipe-card-infographic-easy-weeknight-healthy-chicken-skillet` | `easy weeknight dinners healthy` | `public/images/nano_insp/template-premium-recipe-card-infographic-easy-weeknight-healthy-chicken-skillet.jpg` (+ `_preview/...-prev.jpg`) | `public/data/nano_inspiration.json` | `easy weeknight dinners healthy`, `healthy weeknight dinners`, `easy healthy dinner`, `healthy dinner ideas`, `quick weeknight dinner`, `weeknight dinner recipes` | **PASS** | Manually eyeballed by Baobao (2026-07-02). Clean layout, readable text, visuals match the target query. No garbled text, broken layout, or semantic mismatch. Minor Curify preview watermark artifacts present — expected, not blocking. |
| `template-premium-recipe-card-infographic-gluten-free-lemon-herb-baked-salmon` | `gluten free dinner ideas` | `public/images/nano_insp/template-premium-recipe-card-infographic-gluten-free-lemon-herb-baked-salmon.jpg` (+ `_preview/...-prev.jpg`) | `public/data/nano_inspiration.json` | `gluten free dinner ideas`, `gluten-free dinner ideas`, `gluten free dinner recipes`, `gluten-free recipes`, `gluten free meal`, `healthy gluten free dinner` | **PASS** | Manually eyeballed by Baobao (2026-07-02). Clean layout, readable text, visuals match the target query. No garbled text, broken layout, or semantic mismatch. Minor Curify preview watermark artifacts present — expected, not blocking. |
| `template-premium-recipe-card-infographic-meal-prep-chicken-veggie-bowls` | `meal prep weekly recipes` | `public/images/nano_insp/template-premium-recipe-card-infographic-meal-prep-chicken-veggie-bowls.jpg` (+ `_preview/...-prev.jpg`) | `public/data/nano_inspiration.json` | `meal prep weekly recipes`, `weekly meal prep`, `meal prep recipes`, `batch cooking recipes`, `weekly meal plan`, `healthy meal prep` | **PASS** | Manually eyeballed by Baobao (2026-07-02). Clean layout, readable text, visuals match the target query. No garbled text, broken layout, or semantic mismatch. Minor Curify preview watermark artifacts present — expected, not blocking. **See matcher-quirk note below — this record's eval bucket shows a *count* drop even though relevance improved.** |

## Search validation

**Command:** `node scripts/eval_search.cjs --quiet` (existing eval, 125-query set, unchanged).

**Overall:** before `PASS=87 WARN=38 FAIL=0`, after `PASS=85 WARN=40 FAIL=0` (of 125). The 2-point net drop is fully explained below — no unrelated query regressed. I diffed the full before/after verdict listing line-by-line (temporarily checking out the pre-batch `nano_inspiration.json` and re-running eval) to confirm this.

**Direct per-query check** (before → after):

| Query | Before | After | Change |
|---|---|---|---|
| `easy weeknight dinners healthy` | 0 hits, bucket `empty`, verdict PASS (matches stale `expected: empty`) | 1 hit, bucket `thin`, verdict **WARN** | Gap closed — content now exists and strict-matches. WARN only because `search_eval_set.json`'s `expected` field is stale (still says `empty`); same "resolved, baseline needs updating" pattern as the 15 queries the 6/30 retest already flagged. Did not touch the eval set — leaving that calibration update as a separate, explicit follow-up rather than silently editing it. |
| `gluten free dinner ideas` | 0 hits, bucket `empty`, verdict PASS | 1 hit, bucket `thin`, verdict **WARN** | Same as above — gap closed, baseline stale. |
| `meal prep weekly recipes` | 5 hits, bucket `moderate`, verdict WARN (`expected: empty`) | 1 hit, bucket `thin`, verdict **WARN** | **Hit count went down, not up — investigated, not a regression.** The prior 5 "hits" were only loosely relaxed-matched (2-of-3 token overlap: a salad poster, a healthy-eating guide, and 3 sandwich recipes — none actually about meal prep). The new record strict-matches all 3 tokens via its aliases. Per the matcher's documented strict-floor rule (any strict match discards the entire relaxed pool for that query — same behavior already logged against the deferred MBTI item in the prior report), the 1 genuinely-relevant strict hit replaces the 5 loosely-related relaxed hits. Net content quality is better; the raw eval bucket looks worse because the eval only counts total hits, not relevance. Flagging this explicitly rather than letting the number speak for itself. |

Two incidental relaxed-match gains from the new records also touched unrelated CJK queries: `蔬菜` (vegetables) 31→32 hits and `食物` (food) 168→171 hits — both already `PASS`/`rich`, no bucket change.

No other query in the 125-query set changed verdict. Full before/after diff available on request (saved at `/tmp/eval_before.txt` / `/tmp/eval_after.txt` on this machine, not committed).

## Deferred — other C2 families not touched

Per the 6/30 retest's batch-gen queue, still open (in priority order):

1. Architecture landmarks (Eiffel Tower, Colosseum, Big Ben, Sagrada Familia)
2. Food poster sandwich series (philly cheesesteak, reuben, banh mi) — to lift `cuban sandwich recipe poster`
3. Vocabulary en-ko series (vegetables, animals, colors, body parts)
4. Then-vs-now comparison topics (tech gadgets, fashion, music, school life)
5. Vintage stamp topics (ocean life, butterflies, wildflowers)
6. Warmup routine variants (5K, trail, sprint) — note `warmup routine running checklist` is still genuinely unfixed per the 7/2 c1 report; no running-specific template/inspiration exists yet
7. Paris travel itinerary neighborhood/route variations
8. Watercolor world maps (Asia, North America, Latin America)
9. Before-after room organization (living room, bathroom, closet)
10. MBTI INFJ×ENTP — already generated + eyeball-approved, but **deferred** (not shipped) due to a matcher regression on an unrelated query; needs a matcher-level decision, out of scope for content-only batches. See `curify-frontend/docs/search-c1-c2-small-batch-2026-07-02.md`.

Also open: the `search_eval_set.json` `expected` baseline for the 3 queries in this batch (and the 15 from the 6/30 retest) should be recalibrated from `empty`/stale values to reflect current state — flagged, not actioned, since it's an eval-config decision rather than a content-gen task.

---

*Generated 2026-07-02 · pipeline: `scripts/generate_template_examples.cjs` · eval: `scripts/eval_search.cjs` · data: `curify-frontend/public/data/nano_inspiration.json`*
