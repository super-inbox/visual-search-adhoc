# Before-Recording Checklist — Search + Creative Exploration Demo

Work through this top to bottom, in order, immediately before you hit record. Most items are a
30-second check; do them anyway — this demo goes to the boss, so a clean single take matters more
than saving five minutes of prep.

## Browser state

- [ ] Use a **clean browser profile or a fresh guest/incognito-style window** if convenient, so
      no personal bookmarks, extensions banners, or unrelated tabs are visible.
- [ ] **Zoom level at 100%** and window sized to your actual recording resolution — re-check that
      the Brand Direction Explorer's 4-tab scenario picker and the 3-card direction grid don't
      wrap awkwardly at your resolution (verified clean at ~1490px wide during prep; your setup
      may differ).
- [ ] Close any browser notification permission prompts, cookie banners, or "install app" nags
      before recording — dismiss them beforehand, not on camera.
- [ ] Turn off personal notification pop-ups (Slack, email, OS notification center) system-wide.

## Tabs / pages to pre-open

- [ ] Tab 1: `https://www.curify-ai.com/` (homepage) — this is where you start.
- [ ] Tab 2 (pre-opened in the background, not shown yet): `https://www.curify-ai.com/tools/brand-direction-explorer`
      — pre-loading it avoids a visible cold-load delay when you switch to it on camera.
- [ ] Confirm both tabs load correctly *before* recording — a blank/error page on either is a
      reason to stop and re-check, not to push through live.

## Query copied / ready

- [ ] Have the search query `modern tea brand identity` ready to type (or copied to clipboard) —
      see `DEMO_PLAN.md` §3.
- [ ] Have the 5 Brand Direction Explorer field values ready to paste or type quickly (brand
      name, product type, description, applications, tone — exact text in `DEMO_PLAN.md` §3).
      Typing them live is fine and looks natural; just don't fumble the exact wording, since the
      description length affects how good the resulting directions are.

## Scenario ready / pre-flight check

- [ ] **Do a silent dry run of the exact sequence once before the real take** — search the
      query, confirm the top-row results still look like tea-brand cards (search rankings can
      shift day to day), then run the Brand Direction Explorer brief once and confirm you get
      three distinct direction titles (not a repetitive/near-duplicate set like the
      `coffee-opening` case showed during prep — see `DEMO_PLAN.md` §1). If the dry run looks
      weak, switch to the `topics/branding` search fallback or the `event-poster` backup scenario
      (`DEMO_PLAN.md` §7) before recording for real, not mid-take.
- [ ] Decide in advance whether you're doing a **full live take** (through Stage-2 image
      generation) or **stopping at direction-selection** and narrating the fallback still image
      (`DEMO_PLAN.md` §6) — don't decide this mid-recording.

## Loading / cache considerations

- [ ] Direction generation (Stage 1) takes **~8–10 seconds** after the brief is filled in — don't
      talk through dead air; either keep narrating during the wait (per `LOOM_SCRIPT.md`) or plan
      a quick cut in editing.
- [ ] If you did a dry run immediately before recording, the *same exact brief* may return
      cached/near-identical results faster the second time — that's fine and expected, not a
      sign anything's wrong.
- [ ] Stage-2 image generation (if you're doing it live) can take longer and varies run to run —
      have the fallback image ready regardless, per `DEMO_PLAN.md` §6.

## Backup output ready

- [ ] Confirm you can locate (or have already opened/saved a copy of) the two archived Stage-2
      images for the tea scenario, in case live Stage-2 generation is skipped or fails:
      `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/02-shanlan-tea/generated-output-primary.jpg`
      and `.../generated-output-alternative.jpg` (in the separate `curify-frontend-brand-direction-explorer`
      repo — see `EVIDENCE.md` for the full path and context).
- [ ] Confirm the Stage-1 fallback screenshot is also locatable:
      `.../02-shanlan-tea/stage1-directions-full-page-corrected.png`.

## Sensitive / private information hidden

- [ ] **Log in before recording, off camera**, so no email/password entry is ever shown.
- [ ] Once logged in, avoid opening the account/profile menu, credit-balance detail, or billing
      pages on camera — the "5 credits" cost shown inline on the generate button is fine to show,
      account internals are not.
- [ ] Check the browser tab bar / bookmarks bar for anything personal or unrelated before
      starting — trim or hide it if needed.
- [ ] If any other tabs are open in the same window, close or hide them so nothing unrelated is
      visible during a tab switch.

## Recording area

- [ ] Record the browser window only (not full desktop) to avoid exposing desktop
      files/notifications.
- [ ] Set Loom (or your recording tool) to the resolution you already tested browser layout at
      (see "Browser state" above).
- [ ] Do a 5-second test recording first to confirm audio levels and screen capture are both
      working before the real take.

## Final Loom link verification

- [ ] After recording, **play back the finished Loom video start to finish** before sharing — 
      confirm the search results, the 3 direction cards, and the final image (live or fallback)
      are all actually legible on screen, not cut off or blurry.
- [ ] Confirm the Loom's sharing/visibility setting matches intent (e.g., "anyone with the link"
      vs. restricted to the team) before sending the link to the boss.
- [ ] Sanity-check the video's total length lands in the planned 60–90s range (`DEMO_PLAN.md`
      §5) — trim in Loom's editor if it ran long.
- [ ] Click the final shared link yourself, in a fresh/incognito window, to confirm it actually
      plays for someone who isn't you before sending it.
