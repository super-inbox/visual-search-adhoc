# Search + Creative Exploration Demo Plan

**Prepared:** 2026-08-19. **Status:** demo preparation and validation only — no Loom recording has
been performed yet; that step is still manual and belongs to whoever records it (see
`BOSS_SUMMARY.md`).

**How this plan was validated:** every claim below about what the live product actually does
was checked today, live, against the real production site (`https://www.curify-ai.com`) via
browser automation — not assumed from older docs. Where an older doc (`docs/daily_report/8.16/...`)
turned out to be stale (it is — see §2), this plan says so explicitly and uses today's live
observation instead. See `EVIDENCE.md` for the full evidence list with timestamps.

---

## 1. Selected scenario and why

**Primary scenario: `tea-brand-exploration` — "山岚茶事" (Shanlan Tea), a modern Chinese tea
brand.**

Why this one, over the other two real Brand Direction Explorer scenarios
(`coffee-opening`, `event-poster`):

- **Live-verified today to produce clean, distinct output.** Re-running the exact 山岚茶事 brief
  live against production just now returned three clearly distinct, well-formed directions:
  **Modern Minimalism / 现代极简主义**, **Cultural Contemporary / 文化当代**, **Serene Zen /
  宁静禅意** — each with its own tagline, description, and style tags (see §4 for the full text).
  No repeated or near-duplicate titles.
- **`coffee-opening` was also live-tested today and is visibly weaker.** The same live session
  ran the `coffee-opening` case with a "Brew & Co" brief and got three titles that are real and
  distinct but noticeably repetitive/generic: *"Brew & Co Coffee Shop," "Welcome to Brew & Co,"
  "Discover Brew & Co"* — every title is just "[phrase] + Brew & Co." This is not the old,
  worse "Morrow Coffee" ×3 exact-duplicate bug documented in the 2026-08-07 archived report, but
  it is a real, current, observed quality gap next to the tea case's much more differentiated
  output. **Do not use `coffee-opening` as the primary scenario on camera.**
- **Strong, genuine search-side evidence exists for tea, live, today.** A production search for
  "modern tea brand identity" returns, in the top row, three cards literally titled *"Tea Brand
  — Contemporary Vibrant," "Tea Brand — Earthy Elegance," "Tea Brand — Heritage 国风"* — visually
  on-topic, real inspiration content that a viewer will immediately read as relevant. See §3.
- **Existing evidence trail.** A full real, archived end-to-end run of this exact scenario
  already exists from 2026-08-07 (brief, real Stage-1 API response, UI screenshot, two real
  Stage-2 generated images) — see `EVIDENCE.md`. That's a ready-made fallback if anything goes
  wrong live during recording (§5).
- **Visually easy to understand.** "I'm opening a modern tea brand, show me some directions" is
  an intuitive one-line pitch for a non-technical viewer (the boss), more so than an abstract
  merch/packaging brief.

**Backup scenario:** `event-poster` — "Afterglow Market" (see §7).

---

## 2. What is currently connected in product — read this before recording

This is the single most important thing to get right in the narration. **Do not imply Search
feeds data into Creative Exploration.** Verified live, today:

- **Search and Brand Direction Explorer ("Creative Exploration") are two separate product
  surfaces with no data handoff between them.** Clicking a Search result card
  (`https://www.curify-ai.com/search?q=...`) opens a *different* generation tool — a
  single-parameter "nano-template" generator page (confirmed live: clicking the "Tea Brand —
  Earthy Elegance" search result opened a **Food Product Packaging Design Generator** template
  page, not the Brand Direction Explorer). Nothing about the search query, the clicked card, or
  its image is passed into `https://www.curify-ai.com/tools/brand-direction-explorer` — that page
  starts from a blank brief every time, at its own URL.
- **There is no in-product navigation link from Search/home to Brand Direction Explorer either.**
  The homepage's left icon rail (Home / Video / New / Notifications / Library) and the "More"
  menu (a language switcher only) have no entry for it. It is reached only by typing/opening its
  direct URL. A real user would not stumble into it from Search today.
- **Correction to prior internal docs:** `docs/daily_report/8.16/creative-direction-trajectory/README.md`
  and `docs/daily_report/8.16/creative-direction-product-iteration/README.md` describe Brand
  Direction Explorer as living only on an uncommitted, unpushed local branch
  (`baobao/brand-direction-explorer-tool-demo-2026-08-04` in the
  `curify-frontend-brand-direction-explorer` worktree). **That is no longer accurate.** As of
  today it is live on production at `https://www.curify-ai.com/tools/brand-direction-explorer`,
  including the "Visual preference (optional)" Prefer/Avoid fields that the 8.16 docs describe as
  uncommitted local work — that work has since shipped. Treat this plan's live observations as
  current; treat the 8.16 docs as historical context on how the feature was built, not as a
  description of today's product.
- **What this demo actually is, honestly stated:** a **sequential, two-part demo of two real,
  independently-live product surfaces**, connected only by the presenter's own narration and a
  manual tab/URL switch — not a single wired user flow. Say so on camera in one sentence (see
  `LOOM_SCRIPT.md`) rather than let the cut imply integration that doesn't exist.
- **One caveat on the search evidence itself:** production search for niche/compound queries can
  render a "Few results for X. Also showing results for: ..." banner (confirmed on this exact
  query — see §3). The top-row results are still genuinely relevant despite the banner. Don't
  dwell on or zoom into the banner text on camera; just move past it to the relevant cards.

---

## 3. Exact user query / brief

**Search step** — production search bar, query:

```
modern tea brand identity
```

Full URL: `https://www.curify-ai.com/search?q=modern%20tea%20brand%20identity`

Observed live (2026-08-19), top-row "Examples" results include, in order:
1. **Tea Brand — Contemporary Vibrant**
2. **Tea Brand — Earthy Elegance**
3. **Tea Brand — Heritage 国风**
4. PAW PARADISE IP Material Design Specification *(off-topic — skip over)*
5. bubble tea shop
6. Panda tea master

A yellow "Few results for 'modern tea brand identity'. Also showing results for: tea brand
design, modern tea packaging, tea branding concepts" banner renders above the results — real,
current production behavior, not an error. Narrate past it; don't linger on it.

**Backup search option** (no banner, broader but still on-topic, also live-verified today): click
the **"Brand Design"** category tab on the homepage instead of typing a query. This opens
`https://www.curify-ai.com/topics/branding`, which shows a clean grid with no results-warning,
including a full "BREW & CO" coffee-shop brand board and a "北岳茶事"-style tea-brand card. Use
this if the free-text query above looks noticeably worse on the actual recording day (search
results can change).

**Creative Exploration step** — `https://www.curify-ai.com/tools/brand-direction-explorer`,
**"Chinese tea brand style exploration"** tab, exact field values (this is the same brief used in
the 2026-08-07 archived real run, and the one re-verified live today):

| Field | Value |
|---|---|
| Brand name | `山岚茶事` |
| Tea or product type | `Modern Chinese tea` |
| Brand description | `A modern Chinese tea drink brand combining traditional Chinese tea culture with a clean contemporary lifestyle. It should appeal to customers aged 20-35 without looking overly classical or like generic bubble tea.` |
| Applications | `Storefront signage, takeaway cups, packaging, social media posts, and a launch poster` |
| Desired tone | `Modern Chinese, refined, calm, culturally grounded, and visually distinctive` |
| Visual preference (Prefer / Avoid) | Leave both blank — keep the demo to the core flow, not the newer preference feature (out of scope for this recording) |

---

## 4. Preconditions

- Access to the live production site `https://www.curify-ai.com` (no special environment, no
  local dev server, no `curify-frontend` checkout needed — everything in this plan runs on the
  real deployed product).
- **A logged-in Curify account with enough credits for at least one image generation** (Stage 2 —
  "Generate visual" — costs 5 credits per the live UI; Stage 1 direction generation itself is
  free/pre-login). Confirm login state before recording — see `DEMO_CHECKLIST.md`.
- A modern desktop browser at a normal recording resolution (results above were captured at
  ~1490px wide; verify layout doesn't break at your actual recording resolution beforehand).
- Nothing to install, no branches to check out, no `.env` setup — this is 100% a live-production
  click-through.

---

## 5. Exact click / interaction sequence and expected result at each stage

| # | Action | Expected result |
|---|---|---|
| 1 | Open `https://www.curify-ai.com/` | Homepage loads: "Don't just make an image. Finish the job." headline, tagline mentioning "search inspiration, generate visuals," and a row of topic tabs (Merch & Stickers, Product & E-commerce, Education, Brand Design, Packaging, ...). |
| 2 | Click the search bar, type `modern tea brand identity`, press Enter | Navigates to `/search?q=modern%20tea%20brand%20identity`. A "Few results..." banner appears, followed by an "Examples" grid whose top row includes "Tea Brand — Contemporary Vibrant," "Tea Brand — Earthy Elegance," "Tea Brand — Heritage 国风." |
| 3 | Point out 1–2 of the top-row tea-brand cards (do not click into one) | Viewer sees real, on-topic inspiration content. **Do not click a card** — it opens an unrelated single-parameter template generator (a different product surface), which would confuse the narrative (see §2). |
| 4 | Manually navigate (new tab or same tab) to `https://www.curify-ai.com/tools/brand-direction-explorer` | Brand Direction Explorer loads: "Explore three creative directions from one brief," a 4-tab scenario picker, currently on "Coffee shop opening poster" by default. |
| 5 | Click the **"Chinese tea brand style exploration"** tab | Form switches to 5 fields: Brand name, Tea or product type, Brand description, Applications, Desired tone. |
| 6 | Fill in the 5 fields exactly as in §3 | As the last field is typed, a debounced auto-fetch fires (~600ms after typing stops) — a "Generating directions…" spinner appears under "PICK A DIRECTION." |
| 7 | Wait ~8–10 seconds | Three direction cards render: **Modern Minimalism / 现代极简主义** ("A sleek interpretation of modern tea culture, blending traditional elements with a minimalist approach" — tags: modern, minimalist, clean, refined), **Cultural Contemporary / 文化当代** ("Emphasizing the harmony between cultural heritage and a contemporary lifestyle" — tags: cultural, contemporary, elegant, vibrant), **Serene Zen / 宁静禅意** ("Capturing the essence of tranquility and mindfulness through tea culture" — tags: zen, serene, natural, earthy). |
| 8 | Click one direction card (recommended: **Cultural Contemporary**, the clearest bridge back to the "Tea Brand — Contemporary Vibrant" search result from step 2) | Card shows a "SELECTED" badge; the "Generate visual" button (previously disabled/grey) becomes active, showing "1 image per generation · 5 credits." |
| 9 | Click "Generate visual" | Image generation begins (this step was **not** executed by this prep pass — it requires login/credits, a real user action; see §6 for what to do if it fails). Expected: after a wait, a finished poster/moodboard-style image renders in the "RESULT" panel. |
| 10 | Hold on the final generated image for a beat, then cut | Closes the demo on a finished, tea-branded visual — the concrete "resulting creative direction" payoff. |

**Suggested total recording length: 60–90 seconds.** This is a short, two-scene demo (search →
creative exploration), not a full product tour. Cut ruthlessly — the value is "brief in, three
distinct directions out, one finished visual," not an exhaustive feature walkthrough.

---

## 6. Fallback if a live generation step fails

- **If the Stage-1 direction generation (step 7) is slow, errors, or times out:** re-trigger it
  by re-focusing any field and adding/removing a single character (the debounced fetch re-fires
  on any field change) — this is a real, live retry, not a script trick. If it still fails,
  fall back to the archived real screenshot of this exact scenario:
  `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/02-shanlan-tea/stage1-directions-full-page-corrected.png`
  (in the `curify-frontend-brand-direction-explorer` repo — read-only reference, see
  `EVIDENCE.md` for the full path) — narrate over the still image rather than claim it's live.
- **If Stage-2 "Generate visual" (step 9) fails, times out, or you'd rather not spend credits
  live on camera:** use the two already-real, already-generated Stage-2 outputs from the same
  scenario's 2026-08-07 archived run as the "expected result" visual instead:
  `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/02-shanlan-tea/generated-output-primary.jpg`
  (sage-green ceramic tea jar on a linen moodboard) and
  `.../generated-output-alternative.jpg` (ornate red-and-gold lacquered tea tin with the 5
  application icons illustrated on the poster). **Say explicitly on camera that this is an
  example from a prior real generation of the same scenario**, not the literal output of the
  exact direction you just clicked — don't let the cut imply otherwise.
- **If the live search results (step 2) look weak or empty on the actual recording day**
  (rankings can shift): switch to the "Brand Design" topic-tab fallback described in §3
  (`https://www.curify-ai.com/topics/branding`) — verified today to render cleanly with no
  results-warning banner.
- **If you are not logged in / don't want to spend credits at all:** end the demo at step 8
  (direction selected, "Generate visual" button visibly active/ready) and narrate the payoff as
  "from here, one click turns this into a finished visual" — showing the archived output image
  as a still to illustrate what that click produces, per the Stage-2 fallback above.

---

## 7. Backup demo scenario

**`event-poster` — "Afterglow Market."** Real archived brief (2026-08-07, not re-verified live
today — do a quick live check before using it as an actual fallback on recording day):

| Field | Value |
|---|---|
| Event name | `Afterglow Market` |
| Date & time | `August 30, 5 PM–11 PM` |
| Location | `Harbor District` |
| Event highlights | `Food, independent designers, vinyl records, and live music` |
| Visual tone | `Energetic, youthful, slightly experimental, and highly recognizable from a distance` |

The archived 2026-08-07 run for this scenario returned three genuinely distinct directions
(`vibrant-abstract`, `retro-vinyl`, `minimalist-geometric`) with no title-repetition issue — a
clean result on par with the tea scenario. It's a good backup specifically because "market /
community event poster" pairs naturally with a wide range of Search queries (festival posters,
event flyers, market branding), giving more flexibility if the tea-specific search results are
weak on the day. Use this only if the primary tea scenario is somehow unavailable or degraded —
it has not been re-verified live today the way the primary scenario has.

---

## 8. What NOT to show — unstable, irrelevant, or off-message

- **Do not click into a Search result card and let it land on a nano-template generator page.**
  It's real and it works, but showing it here directly contradicts the "Search → Creative
  Exploration" narrative and will confuse the viewer about what's connected to what.
- **Do not use `coffee-opening` as the on-camera generation scenario** — live-tested today and
  its direction titles are markedly more repetitive/generic than the tea scenario's (see §1).
- **Do not show the "few results" banner as if it's a bug** — it's real current behavior, not
  something this task can or should fix; just don't dwell on it.
- **Do not demonstrate the "Visual preference (optional)" Prefer/Avoid fields** — real and live,
  but out of scope for this specific demo's narrative (it's a personalization feature, not part
  of the core Search→Explore→Generate story) and adds length/complexity without payoff.
- **Do not open or reference the untested 4th scenario tab, "From your brief"** — it exists live
  in production today but was not exercised in this prep pass; don't claim anything about its
  behavior.
- **Do not show login, account, credit-balance, or billing UI** any longer than the single click
  needed to generate — no reason to expose account details on a recording meant for the boss.
- **Do not narrate or suggest that the search query was "fed into" or "used by" Creative
  Exploration.** It wasn't. Keep the transition line honest (see `LOOM_SCRIPT.md`).
