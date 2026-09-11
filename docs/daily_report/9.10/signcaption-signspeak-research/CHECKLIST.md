# SignCaption / Sign-Speak API — Access Research Checklist

**Date:** 2026-09-10
**Method:** Pure local research — grepped this repo and the read-only sibling
`curify-studio` checkout for existing SignCaption/Sign-Speak documentation, outreach
history, provenance files, and `.env*` files. **No network calls, no production code
changed, curify-studio not modified.** Nothing below is fabricated; every "known" item
cites its source file, and every "unknown" item is stated as unknown rather than guessed.

## Summary verdict

There is already a real paper trail: Sign-Speak (the vendor; "SignCaption" is its ASL
captioning product) was investigated once before, one pricing-inquiry email was sent and
never answered, and a hard legal blocker was identified and never resolved. This is not a
cold start — but it is also not resolved. Nothing here should be read as current
API access.

## Checklist

| Item | Status | What we know | Source(s) |
|---|---|---|---|
| **API availability** | Known | An "API & SDK Integration" offering exists per Sign-Speak's public Enterprise page. | `docs/daily_report/8.31/asl-product-direction/PRODUCT_CANDIDATES.md` |
| **Access/contact path** | Known, unresolved | Prior outreach sent to `management@sign-speak.com` via a one-shot script; **no reply was ever recorded**. No self-serve signup/API-key flow found. | `curify-studio/gtm_tools/send_signspeak_inquiry.py` (read-only ref); `curify-studio/docs/asl-translation-mvp-spec.md`, `docs/workstream-tooling-and-engineering.md` (both state the project was docked because "Sign-Speak's API went silent") |
| **Auth** | Unknown | No API key format, auth header, or session scheme documented anywhere in either repo. | — (not found) |
| **Pricing** | Unknown / not public | Every document that touches this explicitly says pricing is not public and gated behind direct Enterprise contact. | `PRODUCT_FEASIBILITY.csv`, `PHASE3_EXPERIMENT_PLAN.md` (`docs/daily_report/8.31/asl-product-direction/`) |
| **Rate limits** | Unknown | Not documented anywhere; this was one of the explicit questions in the unanswered outreach email. | `curify-studio/gtm_tools/send_signspeak_inquiry.py` |
| **Supported video input** | Partially known | Public Enterprise page documents a base64-encoded video parameter (`b64video`). No format/codec/resolution/duration limits documented beyond that. | `PRODUCT_FEASIBILITY.csv` |
| **ASL-to-English caption endpoint** | Partially known | Product exists (SignCaption). Internal accuracy was measured, but **only from manually-downloaded SRT exports already on disk** (`asl_corpus/ground_truth_candidates/signcaption/*.srt`), never via a live API call — best results: WER 0.4815/CER 0.3712 (clip 155), WER 0.5192/CER 0.3347 (clip 1252); correctly recovered fingerspelled names "Greg"/"Sara." No confirmed endpoint URL, request/response schema, or SDK sample exists in either repo. | `PRODUCT_CANDIDATES.md` (source of the clip-155/1252 WER/CER/fingerspelling numbers); `asl_corpus/ground_truth_candidates/signcaption/*.provenance.json`; `asl-translator/evaluation/SIGNCAPTION_COMPARISON_V1.md` (separate SRT-vs-Curify comparisons on different clips — 1477/1474/1466/1467 — not 155/1252; cited here only for the shared "never via a live API call" methodology) |
| **Benchmark/evaluation permission** | Blocked / unresolved | No permission from Sign-Speak has been obtained to use its outputs as a benchmark comparator. Every existing use of SignCaption SRT exports in this repo is explicitly tagged `usable_for_official_metrics: false` / "external-tool candidate reference, never verified gold." | `asl_corpus/evaluation_set.json`, `CONTAMINATION.md`, `README.md`; `asl-translator/evaluation/SIGNCAPTION_COMPARISON_V1.md` |
| **Commercial-use terms** | Known, blocking | Sign-Speak's public Customer ToS (`sign-speak.com/legal/customer`) (a) prohibits sublicensing/reselling/service-bureau use, (b) **explicitly bars using the service "to create a competitive product"** — Curify's own ASL translator is arguably exactly that, (c) licenses uploaded video back to Sign-Speak worldwide/perpetual/royalty-free for model training, (d) caps liability at trailing-6-months fees (or $100 on the free tier). **No written clearance on the competitive-product clause has been obtained.** | `PRODUCT_CANDIDATES.md`, `PRODUCT_FEASIBILITY.csv` |

## Explicitly not found / not known (stated, not guessed)

- No live or working API credentials for Sign-Speak/SignCaption in either repo — checked
  `curify_background/.env.example` and `dev/jayw/ecommerce-video-mini/.env.example` (the
  only `.env*` files present); no `SIGN_SPEAK`/`SIGNCAPTION`/`SIGNSPEAK`-named variable
  exists in either. No non-example `.env` file was found in either repo.
- No response from Sign-Speak to the prior pricing-inquiry outreach.
- No written clearance from Sign-Speak on the competitive-product ToS clause — this is a
  standing open legal risk, not a resolved question.
- No endpoint URL, request/response JSON schema, or rate-limit numbers.
- No confirmation that Sign-Speak's own marketed "BLEU score of 60" claim has been
  independently verified (noted in `PRODUCT_CANDIDATES.md` as unverified vendor marketing).

## What remains external-research work (cannot be resolved from this repo)

1. Re-send or follow up on the pricing inquiry to `management@sign-speak.com` (or find a
   more direct enterprise-sales contact) — ask specifically about pricing, rate limits,
   auth, and API/SDK docs.
2. Obtain **explicit written clearance** from Sign-Speak on the "competitive product" ToS
   clause before any further technical evaluation — flagged in
   `docs/daily_report/8.31/asl-product-direction/PHASE3_EXPERIMENT_PLAN.md` as a required
   Step 0, gating step, not yet done.
3. Ask Sign-Speak directly whether SignCaption outputs may be used as a benchmark
   comparator in a published/internal evaluation (distinct from the ToS's
   competitive-product clause, which concerns building a competing product, not citing
   comparison numbers).
4. If clearance is granted: request API docs/sandbox access to confirm auth scheme,
   supported input formats/limits, and get a live endpoint to test against (as opposed to
   the static SRT exports already on disk).

No production code was changed to produce this checklist, and no external contact was
made in this session (per the "no API calls" instruction for this task).
