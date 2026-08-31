# 1320_1000022357_137.2s — reference inventory, provenance update, and comparison

**Status of this document:** debugging / triage comparison only. It does
**not** establish ground truth, does **not** add anything to
`evaluation_set.json`, and does **not** change what counts as
`verified_gold` anywhere in the repo. No model was called to produce this
document — the SignCaption reference was already collected by hand via the
real SignCaption website, outside this repo, before this evaluation was run.

## 1. What changed today

1. Copied the raw SignCaption export for `1320_1000022357_137.2s` (produced
   via the real SignCaption website workflow: Upload Signed Video ->
   automatic English captions -> SRT Export) byte-identical from
   `~/Downloads/1320_1000022357_137.2s.mp4.srt` into
   `asl-translator/data/asl_corpus/ground_truth_candidates/signcaption/1320_1000022357_137.2s.srt`.
   Diffed against the source file before and after copy — identical.
2. Added a `.provenance.json` sidecar next to it recording tool, workflow,
   verification status, and annotation date.
3. Added lightweight `.provenance.json` sidecars retroactively for the three
   previously-existing SignCaption files (`1477_recording_6.7s`,
   `1474_1000004432_11.5s`, `1467_nohead-half1_189.5s`), confirming: SignCaption
   / Sign-Speak tool, same upload -> auto-caption -> export workflow,
   `verified_by_human: false`, `usable_for_official_metrics: false`. Exact
   run dates/session/account/credit details are not recorded anywhere in the
   repo and are **not invented** — those fields are marked `unknown` rather
   than guessed.
4. Ran the existing `asl-eval` metrics library (`lib.py`, unmodified — no
   new metric code) to compare the new SignCaption reference against the
   pre-existing burned-caption reference for the same video. Results:
   `results/1320_signcaption_vs_burned_caption_eval.json`.

## 2. Reference inventory for `1320_1000022357_137.2s` — four possible categories, only two populated

| Category | Exists? | Location |
|---|---|---|
| **A. SignCaption external-tool reference candidate** | ✅ yes (new today) | `ground_truth_candidates/signcaption/1320_1000022357_137.2s.srt` + `.provenance.json` |
| **B. Burned-caption / hand-read reference candidate** | ✅ yes (pre-existing) | `ground_truth_candidates/1320_1000022357_137.2s.srt` + `.json` |
| **C. Actual Curify model prediction** | ❌ **does not exist** | see §3 |
| **D. Human-verified gold** | ❌ does not exist | n/a — this is exactly what remains open for this video |

Neither A nor B is `usable_for_official_metrics`. Both carry
`verified_by_human: false` / `verified: false`. They are two independent,
unverified candidate references for the same video, not a candidate-vs-gold
pair.

## 3. Confirming there is no actual Curify model prediction for 1320

Per your instruction not to assume `ground_truth_candidates/1320_1000022357_137.2s.srt`
is a Curify model prediction: it isn't. Its own metadata says so
(`gt_kind: "burned_caption_reference"`, `extraction_method: "...visually
inspected... no OCR, no external/cloud service"` — i.e., a human/assistant
read the burned-in captions off video frames; it never went through the ASL
recognition model at all).

Searched for an actual Curify model output for this video:

- `asl-translator/data/asl_corpus/predictions_baseline0/` — 5 files, none
  for `1320`.
- `asl-translator/data/asl_corpus/predictions_eval/` — 6 files, none for
  `1320`.
- Repo-wide grep for `1320` in every `.json` file — only three hits, all
  already accounted for: `evaluation_set.json` (the candidate-reference
  listing), `manifest.json` (corpus metadata), and the burned-caption
  candidate's own `.json`. No prediction file anywhere.

**Root cause, per `manifest.json`:** 1320's only production job
(`video_transcript`, submitted 2026-06-28) **failed** —
`NO_SPEECH — "We can't transcribe sign language or silent footage"` — before
any ASL transcript was ever generated. 0 credits were charged. There is
nothing to retrieve; a Curify prediction for this video has never existed.

**The only way to get one is to generate it now**, via
`asl-translator/asl-eval/run_current_model.py`'s explicit real-run gate
(`--run --acknowledge-private-data-upload`, requires `GEMINI_API_KEY`). That
sends this real user's identifiable video frames to Gemini and spends real
API credits. Per the repo's own privacy/spend gate around this script, **I
have not run it.** If you want the three-way comparison this task ultimately
asks for (Curify vs. SignCaption vs. burned-caption), that command needs to
be run first — flagging this back to you rather than deciding to spend money
and upload private video on your behalf.

## 4. Comparison actually available today: SignCaption vs. burned-caption

Both are candidate references for the same video; neither is gold. Computed
with `asl-translator/asl-eval/lib.py`'s existing `text_metrics` /
`timing_metrics` / `align_segments` functions (burned-caption used in the
`reference` role, SignCaption in the `prediction` role purely because the
tool needs one label for each side — not an endorsement of either as truth).
Full machine-readable output:
`results/1320_signcaption_vs_burned_caption_eval.json`.

| Metric | Value |
|---|---|
| Reference (burned-caption) segments / words | 14 / 136 |
| SignCaption segments / words | 12 / 107 |
| WER | **0.8676** |
| CER | **0.6662** |
| Reference coverage | 90.0s |
| SignCaption coverage | 62.8s |
| Overlap | 51.8s |
| Temporal precision | 0.8245 |
| Temporal recall | 0.5751 |
| Temporal IoU | **0.5123** |

### Semantic agreement

- **Strongest agreement, segment 13 (t≈118–124s):** burned-caption "I'm sure
  this is about **a relationship with Christ**" vs. SignCaption "I'm sure
  this is about **Christ's family**" (t=118.24–121.28s) — near-identical
  opening clause, same timestamp, closely related paraphrase. This is the
  one place the two tools substantively agree on both timing and meaning.
- **Weak but topically-related agreement:** both transcripts independently
  land on a cluster of Christian/faith-themed content across the ~50–105s
  window (dedication, faith, decision, happiness) — the two tools are
  clearly looking at the same *topic*, even where exact wording diverges
  sharply.
- **No agreement at all at the very start (t≈15–20s):** burned-caption reads
  a literal self-introduction, "**Hello, I'm Crystal Cousineau**"; SignCaption
  reads the same time window as "**I'm going to praise my brother. He's a
  good person.**" These share no content. Timing overlap is high (IoU 0.75)
  but the propositions are unrelated — one of the two is describing
  something that isn't there, or the video's ASL and its burned English
  caption diverge more than a same-language rendition would (relevant to the
  still-open "captioned-ASL vs. interpreted-English" production-direction
  question this candidate has always carried).

### Omissions

- SignCaption **entirely omits the scripture citation and quoted verse**
  that dominates the burned-caption's mid-section: "Can we read **Romans
  10:6-8**?" / "Do not say in your heart, 'Who will go up to heaven?'" / "And
  do not say, 'Who will go down into the abyss?'" / "The word is near you, in
  your mouth and in your heart." (burned-caption segments 7–10, t=62–92s,
  four full segments / ~36% of the reference's segment count). SignCaption's
  corresponding window (t≈57–79s) instead reads "No. Christian life relies on
  faith." / "You can decide what you want, and you'll get what you promised."
  — generic paraphrase with no trace of the specific chapter/verse reference
  or the quoted rhetorical questions. One full burned-caption segment
  (segment 9, "The word is near you...", t=86–92s) has **no matching
  SignCaption segment at all** (`matched_prediction_text: null` in the
  alignment output) — a straight omission, not just a paraphrase.
- Burned-caption segment 12 ("I'm not happy; I'm just trying to find a few
  things," t=108–116s) also has **no SignCaption match** — another clean
  omission in the alignment.

### Unsupported / possibly fabricated content

- SignCaption's opening line ("I'm going to praise my brother. He's a good
  person.") introduces a **third person ("my brother")** that appears
  nowhere in the burned-caption reference at any point in the video. Either
  this is content the burned caption simply didn't transcribe, or
  SignCaption introduced it — the two candidate references disagree enough
  here to call this unsupported on the burned-caption side, and it can't be
  resolved without a human watching the actual signing.
- The specific scripture citation ("Romans 10:6-8") in the burned-caption
  reference has no counterpart anywhere in SignCaption's output — if the
  burned caption is accurate, this is a meaningful omission-as-fabrication
  risk on SignCaption's side (dropping a named, checkable reference in favor
  of generic paraphrase); if the burned caption itself doesn't reflect the
  actual signing (open production-direction question), this cannot be
  attributed to either tool with confidence.

### Incorrect translation (candidate-vs-candidate, not vs. gold)

Cannot be established without a human-verified reference — this section only
supports "the two candidates disagree," not "X is wrong." The wording
disagreements catalogued above (omissions, the opening-line divergence, the
scripture-citation gap) are the concrete instances.

### Repetition

Neither transcript shows internal repetition (no video repeats a clause
within itself). Not applicable here.

### Low-density behavior

SignCaption's output is measurably **lower-density** than the burned-caption
reference: 12 segments / 107 words / 62.8s of coverage vs. 14 segments / 136
words / 90.0s of coverage over the same 137.2s video — SignCaption covers
~30% less total runtime and omits two full reference segments outright
(§ Omissions). This is the same "sparser output on longer/lower-signal
content" pattern flagged elsewhere in the corpus for Curify's own baseline0
runs (e.g. `1442_clip01_300.0s`), though here it's SignCaption showing the
pattern, not Curify.

### Timing / segmentation differences

- SignCaption's 12 segments vs. the burned-caption's 14 — SignCaption merges
  some of what the burned caption treats as separate cues (e.g. burned-caption
  segments 5–6, "Happiness comes from our hearts..." / "It is your decision,
  and it takes dedication," both land inside a single wider SignCaption
  window).
- Start times align closely: SignCaption's first cue starts at 15.21s vs. the
  burned-caption's first cue at 16.0s — both correctly skip the ~0–16s
  production title-card slides that were deliberately excluded from the
  burned-caption candidate (see its `meta.review_notes`).
- End times also align closely (SignCaption's last cue ends at 126.48s,
  burned-caption's last at 130.0s), both correctly stopping before the
  closing title card.
- Overall temporal IoU of 0.51 reflects boundary-level disagreement (SignCaption's
  narrower/merged segments vs. the burned-caption's denser splitting) more
  than a fundamentally different read of *when* signing/captioning is
  happening — the two tools broadly agree on the active window, less on how
  to chop it into cues.

## 5. Bottom line

- Provenance for all 4 SignCaption files is now recorded in-repo
  (`*.provenance.json` sidecars); no dates/sessions/credits were invented for
  the 3 retroactive ones.
- `1320` now has **two independent unverified candidate references**
  (SignCaption + burned-caption), which disagree substantially (WER 0.87,
  IoU 0.51) — useful evidence that a human annotator resolving `1320` in
  `asl-ground-truth-annotator/` has real, non-trivial content to adjudicate
  between, not a rubber-stamp confirmation.
- **No Curify model prediction exists for 1320** — the requested Curify-vs-both
  comparison cannot be produced without first running a real, gated,
  credit-spending, privacy-sensitive model call that this task has not
  authorized. Flagging back to you before taking that step.
