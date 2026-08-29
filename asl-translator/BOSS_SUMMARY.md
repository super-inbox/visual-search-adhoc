# ASL Translator — evaluation iteration summary

**Audience:** decision-maker skim. **Scope:** evaluation/diagnostics only —
no model, prompt, or production code was changed in this iteration.

## 1. What was done

- Consolidated ASL translator evaluation assets under `asl-translator/`
  (corpus, ground truth, external-tool candidates, predictions, and the
  local `asl-eval/` scoring toolkit).
- Built and documented a 13-video corpus inventory
  (`data/asl_corpus/corpus_inventory.csv`) with an annotation plan
  (`data/asl_corpus/ANNOTATION_PLAN.md`) prioritizing which videos are
  worth human-verifying next and why.
- Ran local, no-network evaluation (`asl-eval/evaluate.py`,
  `asl-eval/lib.py`) comparing model output against every reference type
  currently available: human-verified gold, an external commercial tool's
  output, and the model's own repeat runs.
- Ran a targeted determinism experiment: two real `temperature=0` calls on
  the same video (`1466_nohead-half1_189.5s`), spending real API credits,
  under the repo's existing private-data-upload gate.
- **Following a manager clarification, audited every locally available
  video for genuine ASL/sign-language content** (frame inspection, audio
  characterization, provenance cross-checks — see §2), then separately
  investigated what it would take to extend that same audit to Curify's
  broader production video pool (§2).
- Diagnostic and comparison logic reused existing tooling only; no new
  metric code was added to the repo (`SIGNCAPTION_COMPARISON_V1.md`,
  `DETERMINISM_EXPERIMENT_V1.md`, `VIDEO_TYPE_AUDIT.md`,
  `ALL_VIDEO_TYPE_AUDIT.md`).

## 2. Manager clarification: is the corpus really all ASL?

A manager flagged that many videos in the data may be **ordinary
captioned/spoken video rather than sign language**. This section states
plainly what was and was not checked, and does **not** conclude that
concern was mistaken — it narrows exactly what has been verified so far
and what remains open.

**Two different things are in play here, and they must not be
conflated:**

1. **The curated local corpus** — the 13 videos physically present in
   `asl-translator/data/asl_corpus/videos/` in this repository.
2. **The broader production user-video pool** — the full set of videos
   ever submitted to Curify, which `manifest.json` documents as living in
   an external Azure Blob container and a production Postgres database,
   **not synced into this repository**.

### What was verified about the curated local corpus

Using only local evidence (ffprobe, frame contact sheets at multiple
timestamps, audio-loudness characterization, and cross-checks against the
corpus's own manifest/inventory — no external calls):

- **13 distinct videos were audited.**
- **12 show sustained, varied, ASL-consistent signing** across densely
  sampled frames.
- **1 video (`1457_10426_28.3s`) remains uncertain** — a poorly-lit,
  screen-recorded social-media clip with sparse, ambiguous gestures that
  local evidence can neither confirm nor rule out as sustained signing.
- **No confirmed ordinary/non-ASL captioned video was found** among the 13
  local files.

Full detail: `data/asl_corpus/VIDEO_TYPE_AUDIT.md` /
`VIDEO_TYPE_AUDIT.csv` (the 13-video pass), and
`data/ALL_VIDEO_TYPE_AUDIT.md` / `ALL_VIDEO_TYPE_AUDIT.csv` (a
repository-wide search confirming no video files exist anywhere else in
this repo outside `asl_corpus`).

**This finding describes the local repository only. It is not evidence
about, and does not characterize, the broader production pool.** The 13
curated videos were themselves selected by an engineer from that larger
pool, and the local audit has no way to see what was screened out, never
synced, or never even inspected during that selection.

### Scope limitation: the broader production pool has not been audited

A separate investigation (read-only, no external calls) established:

- The broader pool's actual storage is an Azure Blob container
  (`processed-videos`) plus a production Postgres database (`video`,
  `project`, `projectsegment` tables) belonging to a **separate codebase**
  (`curify-studio`), not this repository.
- **No credentials for either system are available in this environment**
  (`AZURE_STORAGE_CONNECTION_STRING`, `DATABASE_URL`, and related
  Supabase variables are all unset here; no populated `.env` exists in the
  local `curify-studio` checkout either — only a blank template).
- Metadata that would let us classify ASL vs. ordinary captioning content
  at scale (filename, duration, source, job type, user-provided
  description) **is queryable without downloading any video**, in
  principle — but doing so requires production DB/Azure access this
  environment does not have, and would need explicit authorization before
  running even a read-only query, since it touches real users' data.
- Independent context supports why the manager's concern about the
  *broader* pool is plausible: Curify's product is fundamentally a
  general-purpose video dubbing/translation/subtitling tool, and ASL
  support is documented internally as a small, recent, exploratory
  addition motivated by very few organic user requests. That makes it
  likely the broader submitted-video pool is dominated by ordinary
  spoken/captioned content, with ASL videos as a small minority — but this
  is inference from documentation, **not a direct measurement**, and does
  not substitute for actually inventorying the pool.

**Bottom line: the manager's statement about the broader production pool
has not been independently audited yet.** What has been established is
narrower — the 13 videos already inside this repo's curated corpus are, to
local evidence, essentially all genuine signing (with one unresolved
case), which is a different claim than "the broader pool is mostly ASL."

## 3. Data / reference types used (do not conflate these)

| Type | Examples | What it can support |
|---|---|---|
| **Verified-human gold** | `155_demo_asl-demo-translation_26.7s`, `1252_1000016397_76.8s` — hand-transcribed/verified against actual signing, marked `verified_gold`, `usable_for_official_metrics: true` | The only evidence in this repo that can support an **accuracy** claim |
| **External-tool candidate reference** | Sign-Speak / SignCaption outputs for `1477_recording_6.7s`, `1474_1000004432_11.5s`, and (diagnostically) `1467_nohead-half1_189.5s.mp4.srt` | Cross-tool disagreement signal only — **not** gold, `usable_for_official_metrics: false` throughout |
| **Diagnostic / self-comparison** | baseline0 1466-vs-1467 self-disagreement; temperature0 repeat1-vs-repeat2 self-disagreement | Repeatability/noise measurement — says nothing about correctness |

## 4. Main evaluation findings

- Across all reference types tested, model output disagrees heavily with
  whatever it's compared against — including with **itself**, run to run.
- The model's own two independent `baseline0` runs on identical content
  disagree with each other **at least as much as** they each disagree with
  an unrelated external tool (SignCaption). That pointed at non-determinism,
  not a stable content-understanding gap, as a major driver — but it was a
  hypothesis until directly tested (see §5–6).
- Pinning `temperature=0` and re-running twice on the exact same video
  directly tested that hypothesis and confirmed it: self-disagreement drops
  sharply (see §6), while disagreement with SignCaption does **not**
  improve at all.
- **The samples underlying these findings — 1477, 1474, 1466, 1467 — were
  independently re-confirmed by the video-type audit (§2) to contain
  genuine, sustained signing.** Their findings stand; see §7 for the one
  caveat that applies to 1466/1467 specifically.

## 5. Baseline0 non-determinism finding (the control)

Two independent `baseline0` production runs (`1466`, `1467`) on
**documented content-identical video**, temperature unset (provider default
≈1.0), no fixed seed:

| Metric | Value |
|---|---|
| WER | **0.9706** |
| CER | **0.7088** |
| Temporal IoU | **0.4631** |
| Segments | 24 vs. 29 |

Interpretation: two runs on the *same* signing content produce transcripts
that share almost no words. This is the baseline this iteration set out to
explain and, if possible, fix.

## 6. Temperature=0 repeatability result

Two new real-model repeat runs on the **exact same** `1466` video, this
time with `temperature=0.0` pinned (everything else — model, frame budget,
batch size — held identical to the control):

| Metric | Value | vs. control |
|---|---|---|
| WER | **0.1786** | ↓ from 0.9706 (**~82% relative reduction in repeat-run WER disagreement**) |
| CER | **0.1335** | ↓ from 0.7088 (~81% relative reduction) |
| Temporal IoU | **0.9085** | ↑ from 0.4631 |
| Segments | 18 vs. 15 | (24 vs. 29 at baseline0) |

12 of 18 segments (~76% of the clip's duration) came back **byte-for-byte
identical** — same text, same timestamps — across the two temperature=0
runs. All residual disagreement is confined to one ~42-second window near
the start of the clip; nothing outside that window differs at all.

**This is a repeatability finding only, not an accuracy claim** — see §7.

## 7. Important interpretation — read this before repeating any of the above numbers

- **Temperature=0 materially improves repeatability/stability.** This is a
  large, observed, one-video effect (WER 0.97 → 0.18), not a marginal one.
- **This does NOT establish improved translation accuracy.** Repeatability
  and correctness are different axes. Two runs agreeing with each other
  tells us nothing about whether either run is a correct translation of
  the signing.
- **Disagreement with SignCaption remains ~0.95 WER, unchanged from
  baseline0**, even after fixing self-repeatability. If temperature-driven
  noise were the whole story behind the baseline0-vs-SignCaption gap, fixing
  it should have narrowed that gap. It did not. So either SignCaption and
  Curify genuinely describe this content differently, or SignCaption
  itself is unreliable, or both — this experiment cannot and does not
  decide between those.
- No accuracy claim should be extracted from this iteration's evidence.
  The only accuracy-capable evidence in the repo is the two verified-gold
  cases (155, 1252), and neither was re-scored under temperature=0 in this
  round.
- **1466/1467 video-authenticity caveat (restated from §2):** both videos
  show **genuine signing** — this was independently re-confirmed by the
  video-type audit — but the camera framing **crops the signer's head out
  of the shot**, which removes ASL's facial-grammar channel (brow raise
  for yes/no questions, furrow for wh-questions) by construction. That
  makes this pair **useful for exactly what it was used for here**
  (run-to-run repeatability and segmentation-timing diagnostics, which
  don't depend on facial grammar being present) but **not representative
  of well-framed ASL for accuracy evaluation**. Don't generalize the
  temperature=0 repeatability magnitude to "ASL video in general" without
  re-testing on a properly framed clip.

## 8. Top optimization paths (in priority order)

1. **Deterministic decoding (`temperature=0`)** — validated as a
   high-leverage, low-cost lever for repeatability on this video. Cheap to
   apply broadly (no new infra); next step is confirming it generalizes
   (see §9).
2. **Investigate the localized opening-window instability.** Temperature=0
   did not eliminate disagreement — it concentrated the remainder into one
   ~42-second window. Worth understanding whether that's a
   content-specific hard passage (e.g., faster/ambiguous signing) or a
   generic segmentation-boundary artifact, since that determines whether
   the fix is "run one more repeat" or "improve motion-adaptive
   segmentation."
3. **Obtain more human-verified ground truth before making any accuracy
   claim.** Every accuracy-relevant question this iteration raised — is
   Curify or SignCaption closer to the truth on 1466/1467, does
   temperature=0 change *correctness* and not just repeatability — is
   blocked on a verified-gold reference that doesn't exist yet for that
   content.

## 9. Recommended next steps

**a. Production consideration: deterministic decoding (`temperature=0`) as
a stability-improvement candidate.** The repeatability gain measured here
(WER 0.97 → 0.18, IoU 0.46 → 0.91) is large enough to warrant serious
consideration for production, but should be adopted as a **stability**
improvement, not sold internally as an **accuracy** improvement — those
are separate claims and only the first is supported yet. Confirming it
generalizes beyond this one video (e.g., one more repeat run, ideally on a
well-framed clip) is cheap and worth doing before committing broadly.

**b. Obtain more human-verified ground truth for accuracy evaluation.**
This remains the only way to answer the accuracy-relevant questions this
iteration surfaced but couldn't resolve: whether temperature=0 changes
correctness (not just repeatability), and whether Curify or SignCaption is
closer to the truth on contested content. 1466/1467 is a reasonable
candidate for this (unlocks two predictions per one annotation) but a
well-framed clip should be prioritized alongside it, given the facial-grammar
caveat in §7.

**c. If requested, obtain authorized metadata-only access to the broader
production pool and classify ASL vs. ordinary-captioning inputs before
expanding the benchmark.** Per §2, this is a read-only, no-video-download
query (filename, duration, source, job type, user description) against
Curify's production DB — technically feasible and scoped narrowly enough
to avoid touching video bytes, but it still requires credentials this
environment doesn't have and explicit authorization before running,
since it touches real users' production data. This should happen **before**
any further expansion of the evaluation corpus with additional
"ASL-labeled" production videos, precisely because the manager's concern
about the broader pool remains open.

## 10. Important caveats

- **SignCaption outputs are external-tool-constructed candidate
  references, not human-verified gold.** They carry
  `usable_for_official_metrics: false` throughout and should never be
  quoted as an accuracy benchmark.
- **File-naming discrepancy, preserved as fact:** the SignCaption reference
  used for both the 1466 and 1467 diagnostic comparisons is
  `ground_truth_candidates/signcaption/1467_nohead-half1_189.5s.mp4.srt` —
  named after **1467**, not 1466, and with a nonstandard double extension.
  It was reused for 1466's comparisons only because the corpus documents
  1466 and 1467 as the same underlying video content submitted as two
  separate production jobs 11 seconds apart. Which production job
  SignCaption was actually run against is not independently confirmed.
- **One-video repeatability evidence should not be generalized.** The
  WER 0.97→0.18 improvement was measured on a single video
  (`1466_nohead-half1_189.5s`). An earlier, unrelated spot-check
  (baseline0-vs-temperature0 on `155` and `1252`) already shows
  temperature's effect size is content-dependent (WER 0.09 on one video,
  0.82 on another) — so this iteration's result is evidence that
  temperature=0 **can** produce a large repeatability gain, not proof that
  it **will**, on unseen content.
- **1466/1467 are genuine signing with a framing defect, not a corpus
  error.** See §7 — don't read this caveat as "these videos shouldn't have
  been used"; they were used correctly, for repeatability diagnostics
  only.
- **The curated corpus's ASL-authenticity finding (§2) does not extend to
  the broader production pool.** No claim in this document about "the
  corpus is genuine ASL" should be read as a statement about Curify's
  full user-video population.

---

### Evidence-type recap (for anyone skimming just this box)

- **Verified-human evidence:** 155, 1252 (`verified_gold`) — exists, but
  **not used** to score temperature=0 in this iteration.
- **External-reference evidence:** SignCaption vs. 1477 / 1474 / 1466 /
  1467 — cross-tool disagreement only, not gold.
- **Diagnostic evidence:** baseline0 1466-vs-1467 self-disagreement;
  temperature0 repeat1-vs-repeat2 self-disagreement — the core finding of
  this iteration, repeatability only.
- **Video-authenticity evidence:** local frame/audio audit of all 13
  curated videos — 12 confirmed genuine signing, 1 uncertain
  (`1457`), 0 confirmed non-ASL. **Local-corpus finding only — does not
  characterize the broader production pool**, which remains un-audited
  pending authorized production DB/Azure access.
- **Hypotheses (not established):** whether the opening-window instability
  is content-specific; whether this magnitude of improvement generalizes
  beyond 1466's content; which of Curify or SignCaption is closer to the
  true signing; whether the broader production pool's ASL-vs-ordinary
  composition matches or differs from the curated corpus's.
