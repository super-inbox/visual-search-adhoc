# Phase 3 candidate search — product-usable ASL→English approach

**Scope:** Research and verification only. Nothing was downloaded, no
environment was created, no API was called, no money was spent. This
document records what was checked and why each candidate was accepted or
rejected against the eight hard requirements (continuous/motion-aware,
ASL→English, arbitrary new video, commercially usable license/terms,
runnable today, no large retraining, evaluable on our clean benchmark,
realistic product latency/cost).

Per instructions: marketing claims are not trusted at face value — every
finding below is sourced from official docs, model cards, license files,
or pricing pages where available, with third-party/unverified claims
explicitly flagged as such.

---

## Result up front

**No candidate found in this search is unambiguously "ready to ship."**
Two candidates clear every hard requirement well enough to justify a
first bounded experiment:

- **Category A (native-video VLM): Google Gemini API** — the only
  general-purpose VLM checked with confirmed native video input, a
  confirmed commercial-use permission in its own terms of service, and a
  published (if imprecise) pricing model, usable today with no download
  or self-hosting.
- **Category B (ASL-specific): Sign-Speak / SignCaption** — the only
  ASL-specific system with a real, existing API/SDK offering **and**
  independent internal evidence of real accuracy (this project's own
  155/1252 comparisons against verified human gold). But its public
  Customer ToS contains a clause barring use "to create a competitive
  product" and acting "in connection with a service bureau for the
  benefit of any third party," which plausibly applies directly to
  Curify's own ASL translator — **classified `LICENSE_BLOCKED` pending
  clearance**, not `PROMISING_BUT_NEEDS_ACCESS`, since the written terms
  as they stand today block the use case. This could still be resolved
  via a negotiated enterprise agreement, but that has not been sought,
  and the legal question should be resolved before any technical
  experiment or pricing discussion, since it could close this candidate
  regardless of price or accuracy.

Everything else checked is either the wrong task direction, not yet
released, released with no API, or explicitly disqualified by license
terms. Full detail below; structured version in
`PRODUCT_FEASIBILITY.csv`.

---

## Category A — commercially usable native-video / multimodal VLMs

### Google Gemini API — `PRODUCT_EXPERIMENT_READY`

- **Native video:** confirmed. Gemini has ingested native video (not
  frame-sampling workarounds) since the 1.5 generation and this remains
  current in the 2.5/3.x lineup.
- **Commercial terms:** confirmed directly from Google's own Gemini API
  terms of service (`ai.google.dev/gemini-api/terms`): the **paid tier**
  explicitly states Google does not use submitted prompts/responses to
  improve its products, and paid usage is positioned for commercial
  product-building. The **free/unpaid tier** explicitly warns not to
  submit sensitive/confidential data, since it may be used to improve
  Google's products — a real distinction to respect (any real experiment
  must use the paid tier, not the free tier, given Curify handles user
  video).
- **Pricing:** published, but not fully precise for video specifically.
  Confirmed rates like "$0.30 per 1M tokens (text/image/video)" for
  Gemini 2.5 Flash-class models, and a documented example of "~5,792
  tokens per second of 720p video" (from the Omni Flash *output* pricing
  note, used here only as an order-of-magnitude reference for token
  volume, not as an input-price guarantee). **Exact per-second input cost
  needs confirming against the live pricing dashboard before spending
  real money** — flagged as an open item, not assumed.
- **Runnable today:** yes, via a standard API key, no download, no new
  local environment.
- **Evaluable on our benchmark:** yes — the 19-clip How2Sign set and the
  internal verified-gold clips (155, 1252) can be sent directly as video
  input.
- **Main risk:** Gemini is a general-purpose model with no ASL-specific
  training. It may simply not recognize sign language as a structured
  language at all (as opposed to, e.g., describing hand movements
  generically) — this is exactly the open question worth testing, not an
  assumption either way.

### Alibaba Qwen3-VL (open-weight, self-hostable + DashScope API) — `PRODUCT_EXPERIMENT_READY`

- **Native video:** confirmed. Qwen2.5-VL/Qwen3-VL support explicit video
  input with dynamic FPS sampling and a temporal-aware positional
  encoding (mRoPE), and DashScope's own vision API documents an `fps`
  parameter (range 0.1–10) for video frame extraction control.
- **License:** confirmed **Apache 2.0** for the mainline Qwen3-VL weights
  (verified via the model's own GitHub repo and multiple independent
  sources) — one exception noted: the largest MoE variant
  (Qwen3-235B-A22B) carries a separate Tongyi license, not relevant to
  the smaller/dense variants suitable for this use case. Apache 2.0 is
  about as clean a commercial license as exists — **self-hosting removes
  any dependency on a third party's terms of service at all**, which is
  a genuine edge over every API-only candidate in this search.
- **Access paths:** two — (a) Alibaba Cloud's DashScope API (OpenAI-
  compatible), commercial ToS not independently confirmed in this pass
  (flagged as an open item), or (b) self-hosted open weights, which sidesteps
  that question entirely at the cost of needing real inference
  infrastructure (GPU, not the CPU-only Mac setup used for Phase 1/2's
  academic checkpoints).
- **Runnable today:** yes via DashScope API; self-hosting is heavier
  (real GPU infrastructure needed for a model this size, unlike the
  small academic checkpoints evaluated in Phase 1/2).
- **Evaluable on our benchmark:** yes, same mechanism as Gemini.
- **Main risk:** same generic-VLM-vs-ASL risk as Gemini; additionally,
  DashScope's specific commercial terms were not confirmed in this pass
  (unlike Gemini's, which were directly read).

### InternVL3 / InternVL3.5 (open-weight) — `PROMISING_BUT_NEEDS_ACCESS`

- **License:** confirmed permissive — InternVL3 itself is MIT, and its
  Qwen2.5 base component is Apache 2.0 (InternVL3.5 uses Qwen3, also
  Apache 2.0). Commercial use is permitted.
- **Native video:** supported and benchmarked (Video-MME, MVBench, MLVU,
  LongVideoBench, CG-Bench are all video benchmarks in its own reported
  results), but video is less central to its documented design than
  Qwen3-VL's explicit fps/mRoPE video-native training.
- **Access path:** self-hosted open weights only — no first-party
  commercial API endpoint equivalent to DashScope or the Gemini API was
  found. This makes it heavier to stand up for a first experiment than
  either Gemini or Qwen3-VL, despite the clean license, hence
  `PROMISING_BUT_NEEDS_ACCESS` rather than `PRODUCT_EXPERIMENT_READY`.

### OpenAI GPT-4o / GPT-5 family — `NOT_SUITABLE`

- **Native video: confirmed absent.** Multiple independent sources
  (OpenAI's own developer community forum, a still-open GitHub feature
  request on `openai/openai-node`, and industry commentary) converge on
  the same fact: **the OpenAI API has never shipped native video file
  input**, despite GPT-4o's original 2024 marketing describing "any
  combination of text, audio, image, and video." As of August 2026, video
  input still is not available on any OpenAI chat/completions endpoint.
  OpenAI's own video product (Sora 2) is generation-only and was
  deprecated in March 2026. **This is a hard disqualification against
  requirement #1**, not a licensing or cost issue — there is nothing to
  test.

### Anthropic Claude — `NOT_SUITABLE`

- **Native video: not supported**, per Anthropic's own official model
  documentation (`platform.claude.com/docs/en/models/overview`, fetched
  directly): "All current models support text and image input, text
  output, multilingual capabilities, vision, and tool use" — image only,
  no video, across the entire current model lineup (Fable 5, Opus 5,
  Sonnet 5, Haiku 4.5). A third-party blog claimed Anthropic had
  "launched a real-time video API," but this claim **could not be
  corroborated by any official Anthropic source** and directly
  contradicts the official docs — treated as unverified and excluded per
  the "do not trust marketing claims alone" instruction. **Disqualified
  on the same hard requirement as OpenAI.**

---

## Category B — ASL-specific commercial APIs/services

### Sign-Speak / SignCaption — `LICENSE_BLOCKED` (pending clearance)

*Reclassified from `PROMISING_BUT_NEEDS_ACCESS` after the ToS clause
below was found and independently confirmed by a second review — the
public terms, as written today, block Curify's specific intended use.
This is not necessarily final: a negotiated enterprise agreement could
supersede the public consumer ToS, but that has not been sought or
confirmed. Treat the technical/accuracy picture below as unchanged and
strong; the classification reflects the legal gate, not a capability
judgment.*

- **What it is:** Sign-Speak is a Deaf-owned company; SignCaption is one
  of its products (automated ASL video captioning — i.e., ASL→English/
  text, the direction we need). This is the same system already used as
  this project's external reference throughout Phase 1's ground-truth
  work.
- **Existing internal evidence (already established in this project,
  restated here as-is, not re-verified in this pass):** on the two
  internal verified-human-gold clips, SignCaption scored **WER 0.4815 /
  CER 0.3712 (clip 155)** and **WER 0.5192 / CER 0.3347 (clip 1252)** —
  by a wide margin the best accuracy of any system evaluated anywhere in
  this project (both academic checkpoints scored WER ≥0.94 on the public
  benchmark) — and **correctly recovered the fingerspelled names "Greg"
  and "Sara"** on 1252, which neither Curify configuration nor either
  academic checkpoint managed. **Treat this as evidence, not ground
  truth** — SignCaption still makes real factual errors (a wrong age on
  155) and at least one fabricated clause (1252) — but it is the
  strongest accuracy signal found anywhere in this evaluation.
- **API/SDK: confirmed to exist.** Sign-Speak's own site lists "API & SDK
  Integration" as an offering ("embed AI-powered sign language
  recognition and translation directly into their applications"),
  distinct from their consumer-facing web tools.
- **Pricing: not public.** No pricing tier, per-minute rate, or
  self-serve signup was found for the API/SDK tier — it appears to sit
  under an "Enterprise"/"Organizations" category requiring direct sales
  contact. This is the main gap before any technical experiment can run.
- **Commercial integration terms: a specific, concrete blocker was
  found, not just an unknown.** Sign-Speak's public Customer Terms &
  Conditions (`sign-speak.com/legal/customer`) explicitly prohibit using
  the Service to "sublicense, resell, rent, lease, transfer, assign, time
  share, or otherwise commercially exploit or make the Service available
  to any third party," to act "in connection with a service bureau for
  the benefit of any third party," and — most directly on point — to
  "use the service to create a competitive product." **Curify's own ASL
  video translator is arguably a directly competing product to
  Sign-Speak's own ASL-translation offering**, so this clause is a real,
  specific legal risk to resolve, not boilerplate to wave past. Separately,
  the same terms license uploaded video content ("Your Content") back to
  Sign-Speak on a "worldwide, non-exclusive, perpetual, irrevocable,
  royalty-free" basis "for developing and training our AI Models" — a
  real data-handling consideration for any user video sent through the
  API — and cap Sign-Speak's liability at fees paid in the trailing 6
  months (or $100 on a free tier). **This is very likely only resolvable
  via a negotiated enterprise agreement, not the public consumer ToS as
  written** — the accuracy question (already strong, per below) is not
  the blocker here; the legal one is.
- **Accuracy claim on their own site** ("BLEU score of 60," described by
  Sign-Speak as human-interpreter-equivalent) is a marketing claim from
  their own FAQ, **not independently verified in this pass** — noted for
  completeness, not treated as fact. Our own internal WER/CER numbers
  above are the trustworthy data point here, not their self-reported
  BLEU figure.

### Google SL2T (DeepMind, shipping on Pixel 11) — `NOT_SUITABLE` (today), worth monitoring

- **Real and shipping**, unlike SignGemma below — SL2T powers ASL
  sign-to-text dictation in Gboard and Live Transcribe, shipping with
  Pixel 11 (August 20, 2026).
- **No API exists.** Confirmed via Google DeepMind's own announcement:
  "developers interested in building on the underlying architecture can
  follow Google DeepMind's announcement for updates on a potential API
  and open-weights release... under active discussion." There is
  currently no way for a third party (Curify included) to call this
  model.
- **Architecturally notable but not directly reusable today:** SL2T's
  privacy design (an on-device model converts raw video to keypoint
  coordinates locally; only keypoints, not video, go to Google's
  servers) is conceptually close to what Uni-Sign already demonstrated
  in Phase 2 (pose-based intermediate representation) — interesting
  context, not an actionable path.
- **Disqualified today purely on requirement #5 (runnable today) —**
  not a licensing or accuracy judgment. Worth re-checking if/when an API
  is announced.

### SignGemma (Google DeepMind) — `NOT_SUITABLE` (not released), worth monitoring

- **Not yet released.** Announced as an upcoming "open model" in the
  Gemma family over a year before this search (mid-2025); as of this
  search, Google has confirmed the model **still has not hit its
  internal quality metrics** and has no confirmed release date. Reported
  training scale (10,000+ hours of annotated ASL video) is a real,
  interesting signal if it does ship, but nothing is usable today.
  Distinct from SL2T (a separate, already-shipping model).

### Sorenson Communications AI Sign Language Translation (AST) — `NOT_SUITABLE` (not released)

- **Proof-of-concept stage only**, unveiled April 2026, following
  Sorenson's acquisitions of OmniBride and Hand Talk. Two POCs described
  (spoken→ASL avatar, and ASL→English text) but neither is a shipped
  product or an accessible API today.

### Signapse — `NOT_SUITABLE` (wrong direction)

- **Confirmed wrong task direction.** Signapse's own site and technology
  description confirm it does **text-to-sign generation** (English
  written text → BSL/ASL avatar video) — the opposite of what Curify
  needs (ASL video → English). Does not meet hard requirement #2
  regardless of any other property.

---

## Candidates not deep-dived (out of scope / clearly non-viable on first pass)

- General ASL "recognition SDK" hobby/research repos found via search
  (e.g. isolated GitHub projects) were not investigated further — they
  do not represent a commercial product/API path and would fail
  requirement #4 (commercially usable terms) by construction (no
  license/business behind them, same category already ruled out for
  academic checkpoints in Phase 2).
