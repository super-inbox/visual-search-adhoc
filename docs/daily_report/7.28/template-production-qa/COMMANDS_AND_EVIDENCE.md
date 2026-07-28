# Commands and Evidence

All commands below were run read-only against the local git worktree (no writes outside the
allowed output directory) and against Production via GET/HEAD only. No login, no form submission,
no POST/PUT/PATCH/DELETE, no dependency installs.

## 0. Pre-check

```
$ pwd
/Users/baobaoli/Desktop/curify-frontend-prod-template-qa
$ git rev-parse HEAD
2d4a89f81946414095c122ca6422aa0ec41b09d3
$ git status --short
(empty — clean)
$ git branch --show-current
(empty — detached HEAD)
```

## 1. Identifying the source commit

```
$ git log --oneline -30
$ git log --oneline --all --grep="template" -i -50
```
→ found `19d9e978 content-drop(2026-07-28): top10 discovered templates + 40 examples`,
confirmed as an ancestor of tested HEAD `2d4a89f8`.

```
$ git show --stat 19d9e978
$ git show 19d9e978 -- public/data/nano_templates.json
$ git show 19d9e978 -- public/data/nano_inspiration.json
$ git show 19d9e978 -- messages/en/nano.json messages/zh/nano.json
```
→ full diff evidence for template_id, base_prompt, parameters, og_image, topics, rank_score,
example records, and title/category/description per locale. Diff text captured in this session's
scratchpad and cross-checked against the file content at HEAD (see below).

## 2. Locale coverage check (10 locales × 10 templates)

```python
for f in [de,en,es,fr,hi,ja,ko,ru,tr,zh]:
    d = json.load(open(f'messages/{f}/nano.json'))
    present = [i for i in TEN_TEMPLATE_IDS if i in d]
```
Result: 10/10 present in all 10 locale files, both at commit `19d9e978` and at HEAD `2d4a89f8`
(no drift between introduction and tested HEAD).

`ls messages/` confirmed exactly 10 locale directories exist project-wide (de, en, es, fr, hi, ja,
ko, ru, tr, zh) — i.e. these 10 locales are the full set the project supports, not a subset.

## 3. Example extraction (40 examples)

```python
insp = json.load(open('public/data/nano_inspiration.json'))
by_tpl = group by ex['template_id'] for ex in insp if ex['template_id'] in TEN_TEMPLATE_IDS
```
Result: exactly 4 examples per template, 40 total, matching commit message claim.

## 4. Static integrity checks

```
$ python3 -c "import json; json.load(open('public/data/nano_templates.json'))"       # VALID
$ python3 -c "import json; json.load(open('public/data/nano_inspiration.json'))"     # VALID
$ (loop) python3 -c "import json; json.load(open('messages/{locale}/nano.json'))"    # VALID x10
```

Duplicate-ID check (whole catalog, not just the 10 new templates):
```python
ids = [t['id'] for t in json.load(open('public/data/nano_templates.json'))]
len(ids) == len(set(ids))   # 346 == 346, no duplicates
ids = [e['id'] for e in json.load(open('public/data/nano_inspiration.json'))]
len(ids) == len(set(ids))   # 3550 == 3550, no duplicates
```

Path-leak / secret-leak check (on the diff, not just current file state):
```
$ git show 19d9e978 | grep -n "/Users/\|/home/\|C:\\\\"          # no matches
$ git show 19d9e978 | grep -inE "api[_-]?key|secret|token|password|AKIA|sk-[a-z0-9]|bearer "  # no matches
```

Cross-template wiring / duplicate-asset check:
```python
imgs = [ex['asset']['image_url'] for ex in the_40_examples]
len(imgs) == len(set(imgs))   # no duplicate image_url
# every example's image filename starts with its own template_id -> no cross-wiring
```
Result: 0 duplicates, 0 cross-wired examples.

## 5. Local asset existence — NOT_APPLICABLE (repo convention)

```
$ ls public/images/
No such file or directory
$ grep -n "nano_insp" .gitignore
public/images/          (line 6)
$ git ls-files public/images/ | wc -l
0
```
Confirmed this is a repo-wide pattern (checked against an older, already-live template's asset
paths — same "file not present locally" result). Local existence is therefore NOT_APPLICABLE;
verification was performed against Production/CDN instead (§7).

## 6. Consuming-code check (schema fields not orphaned)

Delegated to a read-only Explore subagent to trace each JSON field (`id`, `base_prompt`,
`parameters`, `og_image`, `topics`, `rank_score`, `allow_generation`, example `params`,
`search_aliases`, `messages/*` `title`/`category`/`description`) to an actual file:line consumer
in `app/` or `lib/`. Result: all fields consumed except `base_rank_score` and `creation_date`,
which are touched only by build-time generator scripts (`scripts/*.cjs`/`.py`), not runtime code —
noted as informational, not a defect (they're metadata, not renderable fields).

## 7. Production canonical URL

```
$ grep -rniE "curify[a-z.-]*\.(com|ai|app)" README.md
README.md:3: ... [Curify AI](https://www.curify-ai.com) ...
README.md:5: Live product → https://www.curify-ai.com
```
→ `https://www.curify-ai.com` confirmed directly from repo (README), **not** the fallback.

Route discovery:
```
$ find app -path "*nano-template*"
app/[locale]/(public)/nano-template/[slug]/page.tsx
```
```
$ grep -n "toSlug" lib/nano_pure.ts
151: export function toSlug(templateId: string) { return templateId.replace(/^template-/, ""); }
```
```
$ cat i18n/routing.ts
defaultLocale: 'en', localePrefix: "as-needed"
```
→ en URLs have no locale prefix: `https://www.curify-ai.com/nano-template/{slug}`.

## 8. Production HTTP checks — page status (10/10)

```
$ curl -sS -o /dev/null -w "%{http_code},%{url_effective}" --max-time 30 -L \
    "https://www.curify-ai.com/nano-template/<slug>"
```
Run for all 10 slugs. **Result: 10/10 → HTTP 200.** Raw output: `logs/page_status.csv`.

## 9. Production HTTP checks — page content

```
$ curl -sS --max-time 30 "https://www.curify-ai.com/nano-template/<slug>" -o html/<slug>.html
$ grep -o '<title>[^<]*</title>' html/<slug>.html
$ grep -o '<meta property="og:image"[^>]*>' html/<slug>.html
```
**Result:** all 10 `<title>` tags exactly match `messages/en/nano.json[id].title` (+ site suffix
" | Curify Studio"). All 10 `og:image` meta tags resolve to `https://cdn.curify-ai.com` + the
`og_image` path recorded in `nano_templates.json`, and match one of that template's own 4 example
preview images (no cross-template image swap).

## 10. Production HTTP checks — image assets (80/80)

Built the set of unique image URLs (10 `og_image` + 40 `image_url` + 40 `preview_image_url`,
deduplicated since each `og_image` reuses one example's preview → 80 unique URLs):

```
$ (loop) curl -sS -o /dev/null -w "%{http_code},%{content_type}" --max-time 20 -I \
    "https://cdn.curify-ai.com<path>"
```
**Result: 80/80 → HTTP 200, all `content_type` = `image/png` or `image/jpeg`.** Raw output:
`logs/image_status.csv`.

## 11. Image decode verification

Downloaded one full-size example image per template (10 total) via Python `urllib` (curl/basename
were unavailable inside a `while read` subshell in this sandbox — switched to Python for
reliability) and decoded with Pillow 10.2.0:

```python
from PIL import Image
img = Image.open(path); img.verify()
img2 = Image.open(path); w, h = img2.size
```
**Result: 10/10 decoded successfully** (no corruption). Actual pixel dimensions differ from the
`base_prompt`'s declared "output size" (expected — generative models don't always hit an exact
pixel target), but **actual aspect ratio matched declared aspect ratio within 0.7% for all 10**
(e.g. workbook cover: actual 896×1200 = 0.7467 vs declared 1200×1600 = 0.75, diff 0.4%).

## 12. Screenshot checks (desktop + mobile)

Playwright is listed in `package.json` (`^1.55.0`) but **`node_modules` does not exist in this
checkout** (dependencies never installed) — confirmed via `ls node_modules` (not found) and
`find node_modules -iname "*playwright*"` (not found). Per the task's hard constraint, no `npm
install` / `playwright install` was run.

Instead, `/Applications/Google Chrome.app` — a pre-existing system application, not something this
session installed — was driven in headless CLI mode (`--headless --screenshot=... --window-size=...`),
which is read-only (GET only, no automation of clicks/forms) and does not require any package
install:

```
$ "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless --disable-gpu --no-sandbox \
    --screenshot="screenshots/desktop/<slug>.png" --window-size=1440,1000 \
    --virtual-time-budget=15000 "https://www.curify-ai.com/nano-template/<slug>"
```
Desktop: 1440×1000. Mobile: 390×844 (iPhone 12/13/14 logical viewport), re-verified once with an
explicit iOS Safari `--user-agent` string to rule out user-agent-only rendering differences (same
result either way — see §13).

**Result: 10/10 desktop screenshots + 10/10 mobile screenshots captured successfully**, saved to
`screenshots/desktop/` and `screenshots/mobile/`.

## 13. Visual review findings (from the screenshots above) — automated screenshot review, Claude-reviewed

These findings come from Claude directly reviewing the headless-Chrome screenshots stored in
`screenshots/desktop/` and `screenshots/mobile/`. **They are distinct from the User manual visual
review in §16**, which is a separate, later pass done by the user in their own real browser.

- All 10 desktop pages: H1 title, category chip, description, and the 4-up example card grid all
  render correctly with content matching the intended template (no cross-template image mixing).
  All example thumbnails loaded (one earlier apparent broken-image was a lazy-load timing artifact
  at an 8s virtual-time-budget; re-rendered cleanly at 15s — see reasoning trace).
- **`discount-coupon-voucher`** (5:2 wide), **`achievement-certificate-award`** (4:3 landscape),
  and **`jigsaw-puzzle-box`** (4:3 landscape) example card thumbnails crop text at the left/right
  or top/bottom edges, because their non-square source images are placed into a near-square card
  slot with `object-fit: cover`. `discount-coupon-voucher` looked most severe (heavy left/right
  crop, mid-word text loss) in this screenshot-based pass; `achievement-certificate-award` was
  noticeable; `jigsaw-puzzle-box` lighter. **§16 (User manual visual review) additionally confirms
  a 4th template, `stem-classroom-teaching-aid`, with minor-to-medium edge-label cropping** — not
  caught by this automated pass, likely because its declared 1:1 ratio was assumed safe.
- All 10 mobile screenshots (captured at 390×844 via headless-Chrome CLI) appeared to show the
  page H1 overlapping the top navbar's search icon / language toggle, the title/description text
  truncated on the right edge, and the 4-up example card grid overflowing horizontally with the
  2nd column only partially visible. **This description was corrected by the User manual visual
  review in §16**, done in real Chrome DevTools responsive mode at ~400×943/~430×932: the user
  found the two-column mobile example grid **is usable** on all 10 templates, with **no** severe
  horizontal overflow and **no** unusable/cut-off second column. Only the header/H1 overlap is
  confirmed as real. The likely explanation is that headless-Chrome-CLI screenshot mode does not
  fully replicate true mobile-viewport reflow behavior the way DevTools' device emulation does;
  this automated pass's "severe overflow" / "cut off" language is retracted per the correction in
  §16 and in the main report §4.2.
- On most of the 10 desktop screenshots, the search bar's displayed query text does not match the
  template page it appears on (e.g. the `workbook-practice-book-cover` page shows "english spanish
  word comparison"; the `perfume-cosmetic-bottle-mockup` page shows "vintage nostalgia infographic
  poster"). Three templates show the identical string "world history timeline poster" and two show
  "east asian culture comparison". Flagged `NEEDS_MANUAL_REVIEW` — cause not determined. **§16
  reports an independent, later observation of this same phenomenon with an entirely different set
  of strings per template** — see main report §4.4 for the side-by-side comparison and analysis.

## 14. JS console error check — BLOCKED / NOT_VERIFIED

No CDP-capable browser automation tool was available (Playwright not installed per constraint,
plain headless-Chrome-CLI screenshot mode does not expose `console.*` output in an easily
scriptable way). Marked `BLOCKED` per task instructions rather than fabricating a PASS. In the
final classification (main report §7) this is stated as `NOT_VERIFIED`, since no evidence — from
either the automated pass or the User manual visual review — speaks to browser console errors one
way or the other.

## 16. User manual visual review — 2026-07-28 (corrects §13's mobile conclusion)

**This section documents a review Claude did not perform and did not view.** The user manually
opened and inspected all 10 live Production template pages directly in Chrome DevTools responsive
mode, at real mobile viewports (~400×943 and ~430×932), and reported the results in chat. No
screenshot files from this pass were provided to or read by Claude — the content below is a
transcription of the user's reported observations, reproduced in full (with per-template detail)
in `MANUAL_VISUAL_REVIEW.md`.

Summary of what this pass corrects or adds relative to §13:
- Corrects: the mobile two-column example grid is usable on 10/10 templates — no severe
  horizontal overflow, no unusable/cut-off second column. Confirmed issue narrows to the shared
  mobile header overlapping the H1 (Medium severity, non-blocking, sitewide pre-existing pattern).
- Adds: a 4th template (`stem-classroom-teaching-aid`) with minor-to-medium card-thumbnail
  cropping, not identified in §13's automated pass.
- Adds: an independent set of desktop search-bar query strings, per template, entirely different
  from the strings observed in §13 — see main report §4.4 for the comparison and analysis. This
  is treated as `NEEDS_MANUAL_REVIEW`, not a confirmed Production bug.

Full per-template results, method, and the aspect-ratio root-cause pattern are in
`MANUAL_VISUAL_REVIEW.md`.

## 17. End-of-run integrity check

```
$ git status --short
$ git diff --name-only
$ git diff --stat
```
See main report for output — confirms all changes are confined to
`docs/daily_report/7.28/template-production-qa/`.
