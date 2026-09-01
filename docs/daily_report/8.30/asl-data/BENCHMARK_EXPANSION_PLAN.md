# ASL evaluation benchmark expansion plan — 2026-08-30

**Status:** planning only. No downloads, no training, no model/API calls have been made.
This defines the smallest useful next step for each of the internal and public tracks;
execution is a separate, later step requiring its own go-ahead.

**2026-08-30 pilot addendum — material correction found during execution.** The How2Sign
mini-benchmark pilot (`HOW2SIGN_MINI_BENCHMARK.md`) surfaced two corrections to this plan:

1. **Use How2Sign's "English Translation (original)" file, not the "manually re-aligned"
   one, when pairing text with the pre-segmented clips archive.** The physical clips inside
   the official `test_rgb_front_clips.zip` are cut according to the *original* alignment —
   `ffprobe`-measured clip durations matched the original file's timestamps to ~0.03s and
   did not match the re-aligned file's timestamps at all (some off by close to 2x). Sentence
   text is identical between both files; only timing differs. Using the re-aligned file would
   silently pair correct English text with wrong start/end times for every clip.
2. **There is no official per-clip download endpoint** — the smallest official path to
   segmented test-split video is still the full 2.2GB clips archive; "prefer the smallest
   download path" in practice means "download that one archive, extract only the needed
   clips via selective zip extraction, then delete it," not "find a smaller official
   artifact." None exists for clips (only the 23GB full-video archives are larger
   alternatives, both worse).

Both are now reflected in the executed pilot's manifest/method; no other part of this plan
changed.

---

## Internal track

**Current official state:** n=1. `1252_1000016397_76.8s` is the only video with both a clean
input and a verified human reference (WER 0.9231, per `evaluation_set.json` /
`CONTAMINATION.md`, 2026-08-30).

### Path to n=2 (cheapest, already unblocked)

Two independent routes, in order of effort:

1. **Re-score `155` from its now-clean input.** The clean raw source was already swapped in
   during decontamination; its human-verified reference (`ground_truth/155_demo_..._26.7s.srt`)
   was never in question — only the old *input* was contaminated. All that's missing is a
   fresh `baseline0`/`temperature0` prediction generated from the clean file. This requires a
   real model call (`run_current_model.py --run --acknowledge-private-data-upload`), which is
   explicitly **out of scope for this data-only workstream** — flag as the next step once
   model calls are authorized. No new annotation needed.
2. **Promote `1320` from candidate to verified gold.** Its production-direction blocker is
   resolved (2026-08-30: it's an interpreter certification exercise, captions are the answer
   key) and the model-facing input is already a verified-clean masked render. What remains is
   **exactly one qualified-human-annotator pass**: watch the actual signing in
   `asl-ground-truth-annotator/` against the existing candidate text
   (`ground_truth_candidates/1320_1000022357_137.2s.srt`), confirm or correct it, mark
   `gt_kind: human`, and export to `ground_truth/1320_1000022357_137.2s.srt`. No model call is
   required for this step — it only needs a human watching video that's already local. This is
   the single cheapest path to n=2 with a verified reference already 90% built.

### Internal candidates that require qualified human ASL verification before they can count

| Video | What exists today | What's still needed |
|---|---|---|
| `1320_1000022357_137.2s` | Candidate reference (burned-caption-derived) + a SignCaption external candidate (2026-08-29) | Human annotator confirms candidate text against actual signing |
| `1477_recording_6.7s` | SignCaption external candidate + baseline0 prediction | From-scratch human annotation (ANNOTATION_PLAN #1) |
| `1474_1000004432_11.5s` | SignCaption external candidate + baseline0 prediction | From-scratch human annotation (ANNOTATION_PLAN #2) |
| `1466_nohead-half1_189.5s` | baseline0 + temperature0×2 predictions | From-scratch human annotation (ANNOTATION_PLAN #4) — but flag the head-crop/no-facial-grammar limitation on any resulting claim |
| `1442_clip01_300.0s` | baseline0 prediction, suspected fluent fabrication | From-scratch human annotation, specifically to test the fabrication hypothesis (ANNOTATION_PLAN #5) |

None of these need a model/API call to annotate — only a human watching already-local video.
**SignCaption outputs (1320/1477/1474/1467) must never be silently upgraded to gold** — they
stay `external_tool_reference_candidate` until a qualified human independently verifies them
against the actual signing, per the existing repo convention.

---

## Public track

### Smallest subset to try first

**How2Sign's official test split.** Rationale, directly from the research:

- Directly hosted (Google Drive, no scraping, no link-rot risk) — zero download uncertainty.
- Test split is exactly the right size: **2,322 clips / 5.59h** — pull ~15-20 from it, not
  the whole thing.
- Clear, unambiguous license for internal research use (CC BY-NC 4.0).
- It's the field's standard benchmark, with a citable SOTA (12.39 BLEU, YouTube-ASL→How2Sign)
  to compare any OSS baseline or Curify's own model against on neutral ground.
- **No training required** — this is inference-only comparison, exactly what's needed to
  compare multiple baselines on identical clips.

**Concrete selection criteria for the 10–20 clips:**
1. Filter the official test-split manifest for clip duration in roughly the 5–60s range
   (comparable to Curify's own corpus durations, and cheap to score/inspect by hand).
2. Prefer single-signer clips with the face clearly visible (avoid How2Sign's rare
   multi-signer or occluded cases), to keep the comparison apples-to-apples with what Curify's
   product actually receives.
3. **Apply the leakage lesson from `CONTAMINATION.md` even though the risk is low here**:
   How2Sign is raw green-screen studio footage, not a captioned output video, so burned-in-text
   contamination is not expected — but spot-check a handful of frames per selected clip before
   trusting it, the same discipline that would have caught our own 155/1320 issue earlier.
4. Stop at the first 15–20 clips that pass both filters and download cleanly.

**Second-choice subset, if more naturalistic content is wanted:** OpenASL's **975-item
human-verified test set** — closer in spirit to Curify's real, spontaneous user uploads, but
requires a fresh per-video YouTube-availability check first (known link rot), and its CC
BY-NC-ND license restricts derivative redistribution more than How2Sign's — confirm both
before committing effort here.

### Explicitly out of scope for "evaluation subset"

`WLASL` and `ASL Citizen` — isolated single-sign datasets, no sentence-level English ground
truth, wrong task shape entirely. Not a smaller/cheaper version of a translation benchmark;
they cannot substitute for one at any size.

### What this subset lets us do, with no training and no new annotation

- Score Curify's current production model against the same clips an OSS baseline (e.g., a
  YouTube-ASL-finetuned checkpoint, if one is obtained) is scored against.
- Establish whether Curify's ~0.92 WER on its one internal case (1252) is in the same range
  as, better than, or worse than published/reproducible numbers on a public benchmark —
  something our n=1 internal set can never tell us on its own.
- Do this **without** touching any new real Curify user's private video, and without
  spending API credits on anything beyond whatever inference run is separately authorized
  later.

---

## Exact next executable DATA step (no model calls, no training)

1. Fetch How2Sign's official test-split video links + the accompanying English-transcript
   file from https://how2sign.github.io/ (Green Screen RGB, test split, ~5.59h).
2. From the transcript manifest, select 15–20 clips per the duration/single-signer criteria
   above.
3. Download just those clips (not the full 2,322-clip split).
4. Spot-check each for on-screen burned text (per the contamination lesson) before trusting it.
5. Stage them locally in a clearly-labeled, clearly-licensed location (not inside
   `asl-translator/data/asl_corpus/`, since that directory's own README is scoped to Curify's
   real-user corpus — a new sibling directory, e.g. `asl-translator/data/public_benchmarks/how2sign/`,
   keeps public CC-BY-NC data from ever being confused with Curify's private user videos).
6. Confirm each staged clip scores correctly with the existing `asl-eval/evaluate.py` (same
   tool, no new metric code) before treating the subset as ready for comparison.

Step 1–6 above requires no model/API call and no training. Actually running any model
(Curify's own or an OSS baseline) against the staged clips is a separate, later step that
needs its own explicit authorization, same as any other model-call request in this project.
