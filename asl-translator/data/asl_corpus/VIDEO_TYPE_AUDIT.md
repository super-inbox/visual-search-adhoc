# Video type audit — is every file in `asl_corpus/videos/` actually ASL?

**Trigger:** a manager clarification that "many videos in the current data
directory are NOT ASL videos" — some may be ordinary captioned/spoken
video rather than sign language. This audit independently re-examines all
13 videos with local-only evidence (no external API calls, nothing
deleted/moved/modified) and does not assume corpus placement implies ASL
content.

**Method (all local, no network, no model calls):**

- `ffprobe` on every file for stream layout (video/audio codecs,
  resolution, frame rate, per-stream duration).
- `ffmpeg -af volumedetect` on every file's audio track to characterize
  loudness (near-total digital silence vs. an active audio signal) as a
  cheap, local proxy for "is there likely spoken narration," without
  transcribing anything.
- Visual contact sheets: 6 frames per video at 5/20/40/60/80/95% of
  duration for an initial pass; for the three longest/most ambiguous
  videos (`1442`, `1415`, `1252_1000016402`) a second pass with 12 frames
  at ~8% spacing across the full duration, to rule out "a few seconds of
  gesture inside an otherwise ordinary talking video." One further
  brightened/contrast-boosted pass for `1457`, which was under-lit.
- Cross-checked every finding against the corpus's own
  `manifest.json`, `corpus_inventory.csv`, and `README.md` — used as
  additional evidence, not as ground truth to be assumed correct.

**Result up front:** this audit does **not** find broad evidence for
"many videos are not ASL." Twelve of thirteen files show clear, sustained,
varied handshapes consistent with continuous ASL discourse across densely
sampled frames. The genuine finding is narrower and different in kind:
**one video (`1457`) is legitimately uncertain** (a screen-recorded,
under-lit social-media clip with sparse gesture evidence), and **two
already-known caveats are reconfirmed and worth restating plainly**:
`1434` is real ASL content but is a screen recording of someone else's
public YouTube video (not a first-person Curify submission, already
excluded from evaluation), and `1466`/`1467` are real signing but with the
signer's head cropped out of frame, which removes ASL's facial-grammar
channel by construction. Neither of those two is "not ASL" — both are
signing — but neither is clean, representative ASL input either, and that
distinction matters for how their results should be read.

Full per-video data: `VIDEO_TYPE_AUDIT.csv` (same 13 rows, machine-readable).

---

## Full per-video findings

### 155_demo_asl-demo-translation_26.7s
- Visible signer: yes (single woman, blue backdrop). Signing visibly
  present: yes — numbers, classifiers, clearly ASL-consistent across all 6
  sampled frames, matching burned captions ("My family has five..." / "My
  mother is twenty-nine.").
- Sign language is the primary channel: yes. Burned-in captions: yes.
  Audio: present as a stream, but digitally silent (-91 dB).
- **Likely ASL: yes. Confidence: high. Suitable for evaluation: yes.**
  Already `verified_gold`.

### 1252_1000016397_76.8s
- Visible signer: yes (portrait phone video, letterboxed, whiteboard
  background). Signing visibly present: yes — active fingerspelling/number
  handshapes in all 6 frames.
- Primary channel: yes. Burned captions: no. Audio: quiet ambient (-62.1
  dB mean, -15.0 dB max) — no clear speech.
- **Likely ASL: yes. Confidence: high. Suitable for evaluation: yes.**
  Already `verified_gold`, includes the corpus's only fingerspelling case.

### 1252_1000016402_250.8s
- Visible signer: yes — same submitter/setup as the verified-gold
  `1252_1000016397` (cap, laptop webcam). 12 densely-sampled frames across
  the full 250.8s all show continuous, varied handshapes, including one
  frame with an emotive face-covering gesture — consistent with sustained
  narrative signing, not a brief aside.
- Primary channel: yes. Burned captions: no.
- Audio: present, and louder than the corpus norm for silent signing
  (-44.7 dB mean, **-0.8 dB max** — close to clipping). This is flagged,
  not resolved: the video's own production job failed with `NO_SPEECH —
  "We can't transcribe sign language or silent footage"`, which is some
  evidence against a coherent spoken track, but the raw loudness is still
  an outlier worth a human second look. No transcription was performed to
  adjudicate this (would require a model call, out of scope here).
- **Likely ASL: yes. Confidence: high (visual), with an unresolved audio
  flag. Suitable for evaluation: uncertain** — no ground truth or
  prediction exists yet, and the audio anomaly should be checked (by ear,
  locally) before treating this as a clean sample.

### 1320_1000022357_137.2s
- Visible signer: yes, studio production. A title card reads "RECEPTIVE
  SKILLS / SIGN TO VOICE / CATEGORY: RELIGIOUS." Signing visibly present:
  yes, face fully visible, captions burned in and synced to the signing
  across all 6 sampled frames.
- Primary channel: yes. Burned captions: yes (throughout). Audio: digital
  silence (-91 dB).
- **Likely ASL: yes. Confidence: high. Suitable for evaluation: yes** —
  reconfirms the manifest's own "confirmed ASL by frame inspection" note.

### 1415_unit7_200.6s
- Visible signer: yes (single man, blue backdrop, "Professor Weingart"
  watermark). 12 densely-sampled frames across the full 200.6s show
  continuous, varied ASL-consistent handshapes and facial grammar (mouth
  morphemes, brow movement) — not a token gesture inside an otherwise
  ordinary talking-head video.
- Primary channel: yes. Burned captions: no (only the watermark). Audio:
  digital silence (-91 dB).
- **Likely ASL: yes. Confidence: high. Suitable for evaluation: uncertain**
  — no ground truth or prediction exists yet, so it isn't scoreable today,
  but nothing here argues against using it as a future GT candidate. Its
  job was misfiled twice under a speech-transcription job type
  (`full_translation`, which then failed on an unrelated WhisperX outage)
  — that is a product/workflow routing anomaly, not evidence the content
  itself isn't ASL.

### 1434_screenrec_youtube_16.6s
- Visible signer: yes — **two** people, one wearing a T-shirt with an ASL
  "I love you" handshape graphic. Signing visibly present: yes.
- **Appears instead as: a screen recording.** Browser/video-player chrome
  and the on-screen title "Basic ASL Conversation" are visible in-frame —
  this is a screen capture of a public YouTube video, not a first-person
  Curify submission. Burned captions: no (the visible text is player UI,
  not captions on the signing itself). Audio: digital silence (-91 dB).
- **Likely ASL: yes** (the underlying content is real signing) **—
  Confidence: high. Suitable for evaluation: no.** This reconfirms, rather
  than changes, what the manifest and corpus inventory already say:
  greeting-only content (the highest-prior, most-guessable exchange in
  ASL), crowd-sourced non-authoritative ground truth, and already excluded
  from `evaluation_set.json`. This audit's contribution is confirming *why*
  it's excluded (screen-recording provenance, not a first-party sample) is
  visually correct, not merely asserted.

### 1442_clip01_300.0s
- Visible signer: yes (single woman, bookshelf background). 12
  densely-sampled frames across the full 300s all show continuous, varied
  active handshapes.
- Primary channel: yes. Burned captions: no. Audio: digital silence (-91
  dB).
- **Likely ASL: yes. Confidence: high. Suitable for evaluation: yes** —
  has an existing baseline0 prediction. The manifest's separate concern
  about this clip (fluent-sounding output that may be fabricated given
  sparse frame sampling) is an **accuracy** question about the model's
  output, not an authenticity question about the input video.

### 1457_10426_28.3s — the one genuinely uncertain case
- Visible person: yes, but poorly lit (backlit against window blinds);
  brightening the frames was necessary to see anything.
- **Appears instead as: a screen recording** of a social-media (Instagram-
  style) direct-message thread. One sampled frame shows a preceding text
  bubble reading "...I KNOW SO MANY OTHER LANGUAGES..." followed by what
  looks like a video reply.
- Signing visibly present: **uncertain**. Across 10–16 sampled frames the
  person makes isolated hand-near-face/chin gestures — consistent with,
  but not conclusively establishing, continuous ASL discourse. It could
  equally be a single sign, a brief gesture while talking, or genuine
  short-form signing; frame sampling alone cannot distinguish these, and
  no transcription was attempted (would require a model call).
- Primary channel: uncertain. Burned captions: no (chat-app UI text, not
  video captions). Audio stream is present per `ffprobe` but is digitally
  silent (-91 dB) — mildly consistent with no spoken narration, but not
  strong evidence either way.
- **Likely ASL: uncertain. Confidence: low. Suitable for evaluation:
  uncertain.** This video was never processed by any model (the job
  failed on a spend cap) and has no existing prediction or ground truth,
  so no past conclusion in this repo depends on it. Recommend a full
  manual watch-through before using it as the "clean unseen test input"
  the manifest currently calls it.

### 1466_nohead-half1_189.5s
- Visible signer: **partial** — hands and torso only. The signer's head is
  cropped out of frame by construction (the filename is literal).
- Signing visibly present: yes — all 6 sampled frames show continuous,
  clearly ASL-consistent handshapes (fingerspelling-like configurations,
  classifier shapes).
- Primary channel: **yes, but incomplete** — ASL grammar carried on the
  face (brow raise for yes/no questions, furrow for wh-questions) is
  structurally unavailable in this framing.
- Burned captions: no. Audio: moderate ambient/room noise (-38.4 dB mean,
  -12.6 dB max; visible electronics in the background), not clear speech.
- **Likely ASL: yes (real signing). Confidence: high. Suitable for
  evaluation: yes for repeatability/timing experiments** (which is exactly
  how it was used — see below) **but not representative of well-framed
  ASL input** — this reconfirms, in the audit's own words, the caveat the
  corpus's `README.md` already states explicitly.

### 1466_nohead-half2_190.0s
- Same signer, same room, same shirt as half1 — second half of the same
  recording session. Same headless-framing caveat applies. Signing
  visibly present: yes, across all 6 sampled frames.
- Audio: moderate ambient noise (-38.9 dB mean, -13.7 dB max).
- **Likely ASL: yes. Confidence: high. Suitable for evaluation:
  uncertain** — never processed by any model; no prediction exists to
  evaluate against anything yet.

### 1467_nohead-half1_189.5s
- Visually indistinguishable from `1466_nohead-half1` across all 6 sampled
  frames — same shirt, same room, same handshapes appearing at matching
  relative timestamps — consistent with the corpus's documented
  content-identical determinism pair.
- Same partial-framing caveat as 1466 (head cropped, facial grammar
  unavailable). Audio: moderate ambient noise (-38.4 dB mean, -12.6 dB
  max).
- **Likely ASL: yes. Confidence: high. Suitable for evaluation: yes for
  repeatability/timing experiments, not representative of well-framed
  ASL** — same caveat as 1466.

### 1474_1000004432_11.5s
- Visible signer: yes (self-recorded phone clip, seated on a couch). All 6
  sampled frames show distinct ASL-consistent handshapes (fingerspelling/
  classifier-like configurations, hands crossed near the chin).
- Primary channel: yes. Burned captions: no. Audio: quiet (-73.9 dB mean,
  -41.3 dB max).
- **Likely ASL: yes. Confidence: high. Suitable for evaluation: yes** —
  has an existing baseline0 prediction, was used in the SignCaption
  comparison.

### 1477_recording_6.7s
- Visible signer: yes (webcam recording). Frames show clear ASL number
  handshapes (one finger, then two/three fingers) consistent with
  fingerspelling/counting content.
- Primary channel: yes. Burned captions: no.
- Audio: the **loudest non-silent track in the entire corpus** (-21.3 dB
  mean, -3.4 dB max). Flagged as worth a closer (human, local) listen for
  possible simultaneous vocalization — not resolved here, since confirming
  or refuting that would require transcription, which is out of scope for
  this audit.
- **Likely ASL: yes. Confidence: medium-high (the audio anomaly is the
  only reason this isn't "high"). Suitable for evaluation: yes** — has an
  existing baseline0 prediction, was used in the SignCaption comparison.

---

## The ten samples from recent experiments — specific answers

For each: (1) is it actually ASL, (2) should it be used for evaluation,
(3) which existing conclusions remain valid, (4) what would need
downgrading if it were not ASL.

### 1477
1. **Yes**, confirmed ASL (medium-high confidence; audio-loudness anomaly
   noted but unresolved).
2. **Yes**, suitable for evaluation.
3. `SIGNCAPTION_COMPARISON_V1.md`'s Sample 1 (SignCaption vs. Curify
   baseline0 on 1477) **remains valid** as a comparison between two
   candidate machine outputs on genuine ASL video content.
4. N/A — it is ASL; nothing to downgrade.

### 1474
1. **Yes**, confirmed ASL (high confidence).
2. **Yes**, suitable for evaluation.
3. `SIGNCAPTION_COMPARISON_V1.md`'s Sample 2 (SignCaption vs. Curify
   baseline0 on 1474) **remains valid**.
4. N/A.

### 1466 / 1467
1. **Yes, real signing is present** (high confidence) — but the framing
   crops out the signer's head, so this is *incomplete* ASL input by
   construction, not full-grammar ASL. This was already flagged in the
   corpus's own README before this audit; the audit independently
   confirms the underlying hand content is genuine signing, not some
   other video type.
2. **Yes for the specific purpose already used** (self-repeatability /
   segmentation-timing experiments), because those experiments measure
   the model's own run-to-run consistency on real signing input, which
   doesn't depend on facial grammar being present. **Not** suitable as a
   stand-in for "well-framed ASL" more generally.
3. `SIGNCAPTION_COMPARISON_V1.md`'s 1466/1467 comparisons and
   `DETERMINISM_EXPERIMENT_V1.md`'s full repeatability finding (baseline0
   self-disagreement WER 0.9706 → temperature0 self-disagreement WER
   0.1786) **remain valid as repeatability evidence on genuine ASL video
   content.** The large temperature=0 repeatability improvement is not
   called into question by this audit.
4. What should be **restated more explicitly** (not newly discovered —
   already in the README, but worth repeating wherever 1466/1467 results
   are quoted going forward): neither video is representative of
   well-framed ASL, so this pair's results should not be generalized to
   "ASL video in general" without re-testing on a properly framed clip.

### 155
1. **Yes**, confirmed ASL, `verified_gold`.
2. **Yes**, suitable for evaluation (the strongest reference in the
   corpus).
3. All existing accuracy-relevant conclusions built on 155 remain fully
   valid.
4. N/A.

### 1252 (the sample used in experiments: `1252_1000016397`)
1. **Yes**, confirmed ASL, `verified_gold`, includes the corpus's only
   fingerspelling case.
2. **Yes**, suitable for evaluation.
3. All existing accuracy-relevant conclusions built on this file remain
   fully valid.
4. N/A. (Its sibling file, `1252_1000016402`, was also visually confirmed
   as likely ASL in this audit but was never used in any prior experiment
   or comparison — nothing to downgrade there either, though its audio
   anomaly is worth a look before it's used in the future.)

### 1320
1. **Yes**, confirmed ASL (title card, burned captions, single signer,
   face fully visible).
2. **Yes**, suitable for evaluation — remains the corpus's highest-value
   item for a future verified-gold conversion.
3. Not used in the recent temperature=0 or SignCaption comparisons, so
   there is nothing from those documents to revalidate; the corpus
   inventory's existing recommendation to prioritize it for annotation
   remains valid.
4. N/A.

### 1434
1. **Yes**, the underlying content is real ASL — but it reaches this
   corpus as **a screen recording of a public YouTube video**, not a
   first-person Curify submission.
2. **No** — already excluded from `evaluation_set.json`
   (`in_evaluation_set: no`) and already documented as non-diagnostic
   (greeting-only) with non-authoritative, crowd-sourced ground truth.
   This audit reconfirms that exclusion is correct rather than changing
   it.
3. Not used in the recent SignCaption or determinism comparisons — no
   existing conclusion in those documents depends on 1434.
4. N/A for an "is it ASL" downgrade (it is). If it were being considered
   for inclusion anywhere, the correct label is "genuine ASL content,
   external/non-authoritative provenance, screen-recording delivery" —
   not "not ASL."

### 1442
1. **Yes**, confirmed ASL (high confidence, reconfirmed via 12-frame dense
   sampling across the full 300s).
2. **Yes**, suitable for evaluation — has an existing baseline0
   prediction.
3. Not used in the recent SignCaption or determinism comparisons; the
   corpus inventory's existing note about it (longest job, sparsest
   sampling, fluency/fabrication-risk concern) remains valid and is
   orthogonal to this audit (that's an accuracy concern about the model's
   output, not a content-authenticity concern about the input).
4. N/A.

### 1457
1. **Uncertain.** Screen-recorded, under-lit, sparse/ambiguous gesture
   evidence; could be genuine short-form signing or could be incidental
   gesture. Not established either way by local frame/audio inspection.
2. **Uncertain** — recommend excluding from any "confirmed ASL" evaluation
   subset until a full manual watch-through resolves the ambiguity.
3. **N/A — no existing conclusion depends on this file.** It has no
   ground truth, no baseline0 prediction, and no `predictions_eval` entry;
   it was never used in `SIGNCAPTION_COMPARISON_V1.md`,
   `DETERMINISM_EXPERIMENT_V1.md`, or `BOSS_SUMMARY.md`. Nothing needs
   downgrading.
4. If it turns out not to be ASL, the only thing to change is the
   manifest's characterization of it as a "clean unseen test input" for
   future ASL-model testing — that label should not be trusted without
   the manual review recommended above.

---

## Counts

| Category | Count | Videos |
|---|---|---|
| **Confirmed ASL (yes)** | **12** | 155, 1252_1000016397, 1252_1000016402, 1320, 1415, 1434, 1442, 1466_half1, 1466_half2, 1467, 1474, 1477 |
| **Confirmed non-ASL (no)** | **0** | — none found |
| **Uncertain** | **1** | 1457 |

Within the 12 "confirmed ASL," two carry provenance/completeness caveats
worth tracking separately even though they are genuinely signing:
- **1434** — real ASL, but screen-recorded from an external YouTube video,
  not a first-person submission; already excluded from evaluation.
- **1466 / 1467** — real ASL, but head cropped out of frame, so ASL's
  facial-grammar channel is structurally missing; usable for
  repeatability/timing work, not representative of well-framed ASL.

## Recommended ASL-only evaluation subset

Videos that are both **confirmed ASL** and **free of the provenance/
framing caveats above** (i.e., a first-person, well-framed signing
submission):

`155, 1252_1000016397, 1320, 1442, 1474, 1477`

(1252_1000016402 and 1415 belong in this tier by content/framing quality
but currently have no ground truth or prediction to evaluate against —
they're future-candidate quality, not blocked by an authenticity concern.)

## Recommended exclusions (from ASL-accuracy claims specifically)

- **1434** — keep excluded; real ASL but non-authoritative/non-diagnostic/
  external-source, as already documented.
- **1466 / 1467** — keep usable for repeatability/segmentation-timing
  experiments only (as already done); do not use as evidence about
  translation accuracy on "typical" or well-framed ASL, and say so
  explicitly wherever their numbers are quoted.
- **1457** — exclude until a full manual review resolves whether it shows
  genuine, sustained ASL discourse.

## Scope / non-modification note

- No video file was moved, deleted, or re-encoded in place; all frame
  extraction and audio analysis was read-only against the existing files.
- No ground truth, prediction, or `evaluation_set.json` file was modified.
- No external API or model call was made; all analysis used local
  `ffprobe`/`ffmpeg` (metadata, frame extraction, volume analysis) and
  visual inspection of the resulting local images.
- This document and `VIDEO_TYPE_AUDIT.csv` are new files; nothing existing
  was overwritten.
- `BOSS_SUMMARY.md` was **not** modified by this audit, per instructions.
