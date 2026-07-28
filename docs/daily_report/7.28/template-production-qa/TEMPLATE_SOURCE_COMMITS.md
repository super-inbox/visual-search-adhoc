# Template Source Commits

**Tested repository:** curify-frontend-prod-template-qa
**Tested commit (HEAD at start of audit):** `2d4a89f81946414095c122ca6422aa0ec41b09d3` (`2d4a89f8`)

## How the 10 templates were identified

The task brief supplied only informal search hints ("mascot, periodic table, movie poster, product
photography, sticker pack, calendar, logo, puzzle, coupon, character card"). None of these were
taken as ground truth. Instead, the actual introducing commit was located by searching commit
history for content-drop / template-registration commits touching `public/data/nano_templates.json`:

```
git log --oneline --all --grep="template" -i -50
```

This surfaced:

```
19d9e978 content-drop(2026-07-28): top10 discovered templates + 40 examples
```

`19d9e978` is an ancestor of tested HEAD `2d4a89f8` (merged via PR #541 / `jwang/vercel` branch,
confirmed by `git log --oneline -30` showing it in the direct ancestry chain). This is the actual
commit that registered the 10 templates — **not** the HEAD merge commit itself, and **not** the
guessed theme list from the task brief. Only 2 of the 10 hinted themes ("puzzle", "coupon") turned
out to be correct; the other 8 hints did not match any template in this commit.

## Commit details

```
commit 19d9e978e215b0a008f5178e015d11eeaed64227
Author: jay wang <qqwjq9916@gmail.com>
Date:   Tue Jul 28 16:47:55 2026 +0800

    content-drop(2026-07-28): top10 discovered templates + 40 examples

    Integrates the visual-search-adhoc template-discovery top10 (docs/daily_report/
    7.26/template-generation-top10) — content-gap-driven templates the catalog had
    zero/near-zero coverage for:
    - 10 templates → nano_templates.json (workbook cover, promotional flyer, STEM
      teaching-aid, price tag/label, achievement certificate, perfume/cosmetic bottle
      mockup, chocolate giftbox, jigsaw puzzle box, discount coupon, fridge magnet).
      base_prompt from the discovery prompt_template; parameters from editable_fields;
      allow_generation, rank_score 90.
    - 40 examples (4/template) → nano_inspiration.json: watermarked + previews +
      CDN-synced (gs://curify-static) + auto-tagged (topics + bilingual aliases) +
      enriched with real params + titles.
    - 10-locale i18n (messages/*/nano.json) via i18n_autotranslate.

    Source: 40/40 Gemini-generated, QA-passed, IP-clean.

    Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

 messages/de/nano.json             |   50 ++
 messages/en/nano.json             |   50 ++
 messages/es/nano.json             |   50 ++
 messages/fr/nano.json             |   50 ++
 messages/hi/nano.json             |   50 ++
 messages/ja/nano.json             |   50 ++
 messages/ko/nano.json             |   50 ++
 messages/ru/nano.json             |   50 ++
 messages/tr/nano.json             |   50 ++
 messages/zh/nano.json             |   50 ++
 public/data/nano_inspiration.json | 1133 +++++++++++++++++++++++++++++++++++++
 public/data/nano_templates.json   |  836 +++++++++++++++++++++++++++
 12 files changed, 2469 insertions(+)
```

Retrieved with: `git show --stat 19d9e978` and `git show 19d9e978 -- public/data/nano_templates.json`
and `git show 19d9e978 -- public/data/nano_inspiration.json` and
`git show 19d9e978 -- messages/en/nano.json messages/zh/nano.json`.

## The 10 confirmed templates (by `id` field in `public/data/nano_templates.json`)

| # | template_id | slug (URL) | category (messages/en/nano.json) |
|---|---|---|---|
| 1 | `template-workbook-practice-book-cover` | `workbook-practice-book-cover` | Workbook & Practice-Book Cover |
| 2 | `template-promotional-flyer` | `promotional-flyer` | Flyer & Promotional-Flyer |
| 3 | `template-stem-classroom-teaching-aid` | `stem-classroom-teaching-aid` | STEM Classroom Teaching-Aid Illustrations |
| 4 | `template-price-tag-product-label` | `price-tag-product-label` | Price Tag & Product Label |
| 5 | `template-achievement-certificate-award` | `achievement-certificate-award` | Certificates & Achievement Awards |
| 6 | `template-perfume-cosmetic-bottle-mockup` | `perfume-cosmetic-bottle-mockup` | Perfume & Cosmetic Bottle Packaging |
| 7 | `template-chocolate-giftbox-packaging` | `chocolate-giftbox-packaging` | Chocolate & Specialty Gift-Box Packaging |
| 8 | `template-jigsaw-puzzle-box` | `jigsaw-puzzle-box` | Puzzle & Jigsaw Collectible |
| 9 | `template-discount-coupon-voucher` | `discount-coupon-voucher` | Discount Coupon & Promotional Voucher |
| 10 | `template-fridge-magnet-merch` | `fridge-magnet-merch` | Fridge Magnet & Small Merch-Item |

Full per-template detail (title, description, og_image, topics, rank_score, parameters,
example IDs, declared aspect ratio) is in `TEMPLATE_PRODUCTION_MANIFEST.json` in this directory.

## Source files touched

- `public/data/nano_templates.json` — 10 template records appended (English `base_prompt` +
  `parameters` only; see "Locale note" below).
- `public/data/nano_inspiration.json` — 40 example records appended (4 per template), each with
  `id`, `template_id`, `asset.image_url` (PNG), `asset.preview_image_url` (JPG), `params`,
  `locales.en.title`, `search_aliases`.
- `messages/{de,en,es,fr,hi,ja,ko,ru,tr,zh}/nano.json` — one `{template_id}` key added per locale
  (10 locales × 10 templates = 100 keys total), each with `title`, `category`, `description`.

## Locale note (not a defect)

`nano_templates.json` entries for these 10 templates only populate the `locales.en` key (English
`base_prompt`/`parameters`); no `zh`/`es`/etc. prompt-generation content was added. This was
checked against the rest of the catalog: of 346 total templates in `nano_templates.json`, 282
(81.5%) have **only** an `en` locale key — multi-locale generation prompts are the exception, not
the rule. The 10-locale requirement that **is** consistently enforced project-wide is the
UI-string layer in `messages/{locale}/nano.json` (title/category/description), and that is
100% complete (10/10 locales × 10/10 templates — verified by parsing each `messages/{locale}/nano.json`
at HEAD `2d4a89f8`).

## CDN image hosting note (not a defect)

`public/images/` is excluded from git via `.gitignore:6`. This is a repository-wide convention —
verified by checking an older, already-live template's `nano_inspiration.json` entry (index 0),
which shows the identical `/images/nano_insp/...` path pattern with zero locally-committed files
either. Per the commit message, images are "CDN-synced (gs://curify-static)" and, per the
downloaded Production HTML (`og:image` meta tags), actually served from `https://cdn.curify-ai.com`
at request time. Local file-existence checks were therefore marked NOT_APPLICABLE and asset
verification was instead performed via read-only HTTP against the CDN (see
`COMMANDS_AND_EVIDENCE.md` and `logs/image_status.csv`).
