# Publish Checklist — FINAL (Visual Search Benchmark Launch Copy)

Nothing below has been executed as "done" by this session — this checklist is for the boss/poster to
work through before anything goes external. Status as of 2026-08-04, re-verified against the
repository this session (working branch `baobao/publish-visual-search-benchmarks-2026-07-30` @
`cd2f5e4ad5db49fc1a0f47a125e5a760073d19be`).

- [ ] **Boss approval** — explicit sign-off on all three platforms' final copy (`HACKER_NEWS_FINAL.md`,
      `REDDIT_FINAL.md`, `LINKEDIN_FINAL.md`) and on the `main`-sync finding in
      `PUBLIC_RELEASE_FACT_SHEET_FINAL.md` §10–11 / `SUMMARY_FINAL_ZH.md` §6.
- [ ] **Canonical URL confirmed** — boss confirms `https://github.com/super-inbox/visual-search-benchmark`
      (default branch `main`) is the correct public URL to use in all copy. The URL itself is not in
      question; what needs a decision is whether `main`'s *content* is synced first (next item).
- [ ] **`main`/branch status rechecked** — **re-verified this session, status changed from the earlier
      draft:** `main` (`22414abf6e6f7a4d4453a647c46bc4765119d6c8`) is **2 commits behind** the working
      branch (`0cb6f07`, `cd2f5e4`) — it does **not** yet contain the 318/1/7 documentation fix or the
      other wording corrections. Re-run before posting:
      ```
      git fetch origin
      git rev-parse origin/main
      git rev-parse origin/baobao/publish-visual-search-benchmarks-2026-07-30
      git diff --stat origin/main...origin/baobao/publish-visual-search-benchmarks-2026-07-30
      ```
      Decide and execute a sync (merge/PR, boss-approved) before publishing, or accept the "319 on
      `main`, 318 in the announcement" inconsistency and be ready to address it if raised.
- [ ] **Repo publicly accessible** — re-run `gh repo view super-inbox/visual-search-benchmark --json
      visibility` immediately before posting to confirm it is still `PUBLIC` (confirmed `PUBLIC` this
      session; re-check on posting day, not just this session's finding).
- [ ] **HN title selected** — pick one of the 5 options in `HACKER_NEWS_FINAL.md` (recommended: option
      1) and confirm the "Show HN" categorization is still correct at posting time.
- [ ] **Reddit rules checked on posting day** — mandatory, not optional: this environment could not
      fetch any subreddit's current rules (`reddit.com`/`old.reddit.com` blocked). Manually open each
      target subreddit's current sidebar/wiki rules in a browser before posting to r/datasets,
      r/computervision, or r/MachineLearning's self-promotion thread — see the
      "POSTING-DAY ACTION REQUIRED" banner before each destination in `REDDIT_FINAL.md`.
- [ ] **LinkedIn account selected** — personal or company page (boss decision; see
      `LINKEDIN_FINAL.md` §4 and `SUMMARY_FINAL_ZH.md` §7 item 3).
- [ ] **Character counts checked** — re-verified this session on the exact final text: personal
      2,478 characters (target ~2,300–2,600), company 1,703 (< 3,000), short 605 (< 1,000). Re-verify
      if any further edits are made after boss review.
- [ ] **License language confirmed** — CC BY 4.0 applies to Curify-authored data/schema/code/Curify's
      own screenshots; third-party screenshots (68-query: 50 files; 326-query: 326 Google Images
      files) are evidence-only, not CC BY 4.0. `CITATION.cff` now carries an `abstract:` field stating
      this explicitly. Confirm this framing is legally acceptable before any public post repeats it
      (see `SUMMARY_FINAL_ZH.md` §7 item 6).
- [ ] **No unsupported claims** — cross-checked against `CLAIM_AUDIT_FINAL.md`: no "first," "largest,"
      "best," "state of the art"/SOTA, no unscored comparison presented as a cross-platform ranking, no
      screenshot presented as a relevance judgment, no human-review claim for either benchmark, no
      unsupported CAPTCHA/consent-wall claim (corrected this pass, see `LINKEDIN_FINAL.md` header).
- [ ] **No internal paths** — checked: no local absolute filesystem paths (e.g. `/Users/baobaoli/...`)
      appear in any `COPY-READY` section of `HACKER_NEWS_FINAL.md`, `REDDIT_FINAL.md`, or
      `LINKEDIN_FINAL.md`. They appear only in this checklist and the internal-facing fact
      sheet/audit/summary files, which are not meant for external posting.
- [ ] **No secrets** — no credentials, tokens, cookies, or API keys appear anywhere in this output
      directory; none were found in the source repo either (`VALIDATION_REPORT.md` sensitive-data
      scan: clean, re-confirmed this session via `validate_data.py`/`validate_benchmark.py` PASS).
- [ ] **No external post published yet** — confirmed: this session made zero calls to any
      HN/Reddit/LinkedIn API or login flow, and no browser-based posting occurred.

## Final git-safety re-check (run immediately before and after any future publish step)

```bash
cd /Users/baobaoli/Desktop/visual-search-benchmark
git status --short
git diff --cached --stat
git rev-parse HEAD
git rev-parse origin/main
```

Expected result before any publish action: `git status --short` and `git diff --cached --stat` both
return empty (clean tree, nothing staged) — confirmed at the end of this session. `HEAD` should still
be `cd2f5e4ad5db49fc1a0f47a125e5a760073d19be` unless a `main`-sync action has since been taken
elsewhere (not by this drafting session).
