# Repository-wide video type audit — beyond the curated `asl_corpus`

**Trigger:** a follow-up manager clarification that their original "many
videos are NOT ASL" statement may refer to the **broader original data
pool**, not only the curated 13-video `asl-translator/data/asl_corpus/`
that the previous `VIDEO_TYPE_AUDIT.md` covered. This document does not
treat that broader statement as resolved, refuted, or confirmed — it
reports exactly what local, read-only search of this repository did and
did not find, and is explicit about the boundary between "not found
locally" and "does not exist."

**Scope discipline, stated up front:** this audit distinguishes two
different things that could both be called "the ASL data":

1. **The curated `asl_corpus`** (`asl-translator/data/asl_corpus/`) — the
   13-video diagnostic set already fully audited in
   `asl-translator/data/asl_corpus/VIDEO_TYPE_AUDIT.md`.
2. **The broader original data pool** the manager's clarification points
   to — per this corpus's own `manifest.json` provenance note, the
   *actual* original pool is Curify's live production storage ("Azure
   blob container `processed-videos`" and Supabase `project` /
   `projectsegment` / `video` / `transaction` tables), which is **external
   infrastructure, not synced into this repository**, and was not fetched
   here (no network or API calls are permitted for this audit). Local,
   read-only search of this repo cannot see into that pool one way or the
   other — that is a hard scope limit of this audit, not a finding about
   the pool's contents.

## Method (all local, no network, no model calls)

- `find` across the entire repository root for every common video
  extension (`.mp4 .mov .avi .webm .mkv .m4v`).
- Directory survey of the top-level `data/` directory (separate from
  `asl-translator/data/`), `docs/daily_report/`, `scripts/`,
  `claude-reports/`, and `tools/` for any ASL-related or video-bearing
  subtree outside `asl-translator/`.
- Text search (`grep`) across `docs/`, `scripts/`, `claude-reports/`,
  `tools/` for mentions of video files, Azure blob storage, Supabase, or
  `curify-studio` (the external repo the manifest cites as the source of
  truth) to check for *references* to a larger pool even where the files
  themselves are absent.
- `ffprobe` / `ffmpeg -af volumedetect` / visual contact sheets for every
  video file found that had not already been fully characterized in the
  prior `VIDEO_TYPE_AUDIT.md` pass (the two `*_burned.mp4` reference
  renders under `ground_truth/`).
- Cross-checked every finding against `manifest.json`,
  `corpus_inventory.csv`, and `README.md`.

## What was searched, and what was found

| Location | Video files found | Notes |
|---|---|---|
| `asl-translator/data/asl_corpus/videos/` | 13 | Already fully audited in `VIDEO_TYPE_AUDIT.md` |
| `asl-translator/data/asl_corpus/ground_truth/` | 2 (`*_burned.mp4`) | Caption-burned re-renders of the existing 155 and 1252 videos — **not new/independent content**, confirmed by matching resolution, duration, audio profile, and a frame check (see below) |
| `asl-translator/data/asl_corpus/ground_truth_candidates/` | 0 (only `.srt`/`.json`) | SignCaption reference files are text only, no video |
| `asl-translator/asl-ground-truth-annotator/` | 0 | HTML/JS annotator tool; operates on videos elsewhere, ships none itself |
| `asl-translator/data/` (any other subdirectory) | 0 | `asl_corpus` is the only subdirectory that exists |
| Top-level `data/` (separate from `asl-translator/data/`) | 0 | Contains only `external_signals/` (Pinterest manual-collection spreadsheet, JSON query sets) — this is unrelated tooling for the repository's other (visual-search) workstream, not user-uploaded video data, and was not inspected further per instructions to skip obviously-unrelated generated assets |
| `docs/daily_report/8.26/asl-ground-truth-eval/` | 0 | Historical write-up location for this same ASL work, predating the `asl-translator/` consolidation; its `BOSS_SUMMARY.md` / `VERIFIED_TWO_CASE_SUMMARY.md` reference only **155** and **1252** — the same two verified-gold videos already in `asl_corpus`, not additional ones |
| `docs/`, `scripts/`, `claude-reports/`, `tools/` elsewhere | 0 | Full-repo `find` for common video extensions returned only the 15 files listed above; text search for `curify-studio`, Azure/Supabase, or other ASL video references outside `asl-translator/` returned no hits pointing to local video files |

**Total video files physically present anywhere in this repository: 15**
(13 in `videos/` + 2 caption-burned re-renders in `ground_truth/`, the
latter representing only 2 distinct underlying videos already counted in
the 13).

**No video files were found outside `asl-translator/data/asl_corpus/`.**
The top-level `data/` directory belongs to a different, unrelated
workstream (Pinterest/external-signal research for the repository's search
product) and contains no video assets at all.

## The two `*_burned.mp4` files, checked individually

Both were suspected to possibly be independent samples rather than
duplicates, so each was individually verified rather than assumed:

- **`155_demo_asl-demo-translation_26.7s_burned.mp4`** — identical
  resolution (640×360), identical duration (26.7s), identical audio
  profile (digital silence, -91 dB) to `videos/155_demo_...mp4`. A sampled
  frame shows the same signer with a human-verified caption burned in
  ("My mother is twenty-nine.") matching the existing SRT. **Confirmed: a
  caption-burned re-render of the existing 155 video, not new content.**
- **`1252_1000016397_76.8s_burned.mp4`** — identical resolution
  (480×856), identical duration (76.7s), matching audio profile (-62.3 dB
  mean vs. the source's -62.1 dB) to `videos/1252_1000016397_...mp4`. A
  sampled frame shows the same signer with a human-verified caption burned
  in ("The boy's name is Greg.") — matching the manifest's own note about
  this video's fingerspelled name "Greg." **Confirmed: a caption-burned
  re-render of the existing 1252 video, not new content.**

Both classify as **confirmed ASL (reference render, not an independent
sample)** — real signing, but they don't add to the video count; they
exist to let a human visually verify the SRT against the signing without
needing timecodes.

## Full findings table

See `ALL_VIDEO_TYPE_AUDIT.csv` for the machine-readable version (15 rows,
one per physical video file found anywhere in the repository). The 13
`videos/` entries carry forward the classifications already established in
`asl-translator/data/asl_corpus/VIDEO_TYPE_AUDIT.md` (re-verified, not
re-derived from scratch, since that audit's frame/audio evidence for those
13 files is still the same evidence — the files haven't changed). The 2
`ground_truth/*_burned.mp4` entries are new to this pass.

---

## Answers

### 1. How many relevant videos exist in the broader data pool?

**Within this repository: 15 video files, representing 13 distinct video
contents** (the 2 `*_burned.mp4` files are re-renders of 2 of the 13, not
additional content). No video files exist anywhere in this repository
outside `asl-translator/data/asl_corpus/`.

This audit **cannot answer** how many videos exist in Curify's actual
original production pool (the Azure blob container / Supabase database
`manifest.json` names as the corpus's source) — that pool is external,
was never synced into this repository, and fetching it would require
network/API access this task explicitly disallows. The manifest itself
already documents that the 13 curated videos are a *subset*: it notes
duplicate blob copies were deliberately dropped during curation (one of
user 1415's videos existed twice, one of user 1252's existed twice), which
confirms a larger original set existed upstream even before considering
whether the manager's "many are not ASL" statement refers to videos never
brought into this repo at all. This audit's honest boundary is: **it can
account for every video byte physically present in this repository, and
found nothing beyond the known 13; it has no visibility into what was
never synced here.**

### 2. How many are ASL?

Of the 13 distinct video contents present: **12 confirmed ASL** (including
2 with caveats — 1434's external/screen-recording provenance, and
1466/1467's headless framing) **+ 1 uncertain** (1457). Both burned
reference renders are confirmed-ASL re-renders of already-counted videos.
**Zero confirmed non-ASL videos** were found anywhere in the repository.

### 3. How many are ordinary/non-ASL captioned videos?

**Zero**, among the video files physically present in this repository.
No video file found here shows a talking-head/spoken-audio-driven video
with captions and no signing. This is consistent with the prior
`VIDEO_TYPE_AUDIT.md` finding on the curated 13 and is not contradicted by
this broader repository search — there was simply nothing further to
search once the curated corpus, its reference renders, and the rest of the
repository were all checked and came up empty.

### 4. Which videos should actually remain in the ASL evaluation corpus?

Unchanged from the prior audit's recommendation, since no new evidence
emerged: **`155, 1252_1000016397, 1320, 1442, 1474, 1477`** as the clean,
first-person, well-framed ASL-only evaluation subset (155 and 1252 already
`verified_gold`). `1252_1000016402` and `1415` remain good future-GT
candidates (confirmed ASL, but no ground truth/prediction exists yet).
`1434` (external/screen-recording, non-diagnostic) and `1457` (unresolved
authenticity) should stay excluded. `1466`/`1467` should remain limited to
repeatability/timing use, not accuracy claims, per their framing caveat.
The two `*_burned.mp4` files aren't separate evaluation items — they
support the existing 155/1252 ground truth and should stay exactly as they
are.

### 5. Did any non-ASL videos accidentally enter the current 13-video `asl_corpus`?

**No confirmed non-ASL video was found** in the corpus by this or the
prior audit's local evidence. What *did* surface, and is worth restating
plainly rather than treating as resolved: two items in the corpus are real
signing but carry provenance/completeness caveats that a less careful
audit could mistake for "not really ASL" — **1434** (genuine ASL content,
but sourced via screen recording of an external YouTube video, not a
first-person submission) and **1466/1467** (genuine signing, but the
signer's head is cropped from frame, removing ASL's facial-grammar
channel). Neither is an accidental non-ASL video; both are already
flagged and already handled correctly (1434 excluded from
`evaluation_set.json`, 1466/1467 restricted to repeatability use). One
item, **1457**, remains genuinely unresolved and is the one case where
this audit cannot rule out that it isn't sustained ASL discourse — but
"unresolved" is a different finding than "confirmed non-ASL entered the
corpus."

### 6. Do any of the 1477 / 1474 / 1466 / 1467 experiments need to be invalidated?

**No.** This broader, repository-wide search surfaced no new video files
and no new evidence bearing on those four videos beyond what the prior
`VIDEO_TYPE_AUDIT.md` already established: all four show genuine,
sustained ASL signing on local frame/audio inspection. The existing
caveat on 1466/1467 (headless framing removes facial grammar, so their
results shouldn't be generalized to well-framed ASL) still stands and
should keep being stated wherever those results are quoted — but it was
already known before this audit and does not invalidate the
`SIGNCAPTION_COMPARISON_V1.md` or `DETERMINISM_EXPERIMENT_V1.md`
conclusions built on genuine (if imperfectly framed) ASL video content.

---

## Scope / non-modification note

- No video, image, or data file was moved, deleted, or re-encoded; all
  analysis was read-only against existing files.
- No ground truth, prediction, `evaluation_set.json`, or `BOSS_SUMMARY.md`
  file was modified.
- No external API, network, or model call was made. All analysis used
  local `find`, `grep`, `ffprobe`, `ffmpeg` (frame extraction, volume
  analysis), and visual inspection of the resulting local images.
- This document and `ALL_VIDEO_TYPE_AUDIT.csv` are new files; nothing
  existing was overwritten.
- This audit does not assert that the manager's original statement about
  a broader non-ASL video population is incorrect — it reports that no
  such videos were found to be physically present in this repository, and
  is explicit that Curify's actual original production video pool lives in
  external storage this audit had no access to.
