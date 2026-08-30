# Curify ASL corpus

13 real ASL videos from Curify production, with ground truth where it exists and the
current production model's output where a job ran. Assembled 2026-08-25.

This is the test set `docs/daily_report/8.22/asl-transcription-ideas/EXPERIMENT_PRIORITY.md`
§3 asks for and §8 lists as blocked-on-boss. It was never blocked — it was just undocumented.

---

## 🔴 Sensitivity — read before doing anything with this folder

**This is personal data.** Real users submitted these videos to a paid product. They are
identifiable people signing, several self-recorded at home. **Not consented for public
release.**

**Do not push this folder to a public repository.** Note that ASL grammar is carried on the
face — brow raise marks a yes/no question, furrow marks a wh-question — so faces **cannot**
be blurred without destroying the exact signal this corpus exists to measure. There is no
"anonymize it" option here; the choice is private hosting or no hosting.

Three items are lower risk and separable if you need something shareable:
`155_demo_*` (Curify's own demo asset — note the *public* copy is the caption-burned output;
`videos/` holds the raw source), `1434_*` (a screen
recording of a public YouTube video), `1415_*` (a YouTube pull).

---

## Layout

```
asl_corpus/
├── manifest.json                # per-video metadata, provenance, findings — start here
├── videos/                      # 13 mp4s
├── ground_truth/                # 4 videos have some form of reference
└── predictions_baseline0/       # what the live model actually produced, 5 videos
```

Filenames are `<user_id>_<source>_<duration>.mp4`. User IDs match Curify's `project.user_id`
and the ASL index in `curify-studio/docs/asl-translation-mvp-spec.md`.

---

## 🔴 Label leakage — read before scoring anything

Two videos had **the reference answer burned into the frame the model reads**. One of them
was this corpus's primary accuracy anchor. Found 2026-08-30; full account in
[`CONTAMINATION.md`](CONTAMINATION.md).

| Video | What was wrong | State now |
|---|---|---|
| `155_demo_…` | `videos/` held the **published demo OUTPUT**, captions burned in. All its scores measured OCR, and are retracted. | Clean raw source swapped in. **No prediction exists from it**, so 155 is out of the evaluation set. |
| `1320_…` | Burned-in captions over ~69% of the clip; title cards leak topic and instructions. | `videos/1320_….mp4` is now a **conditionally masked** render, verified free of on-screen text. Unmasked source moved to `ground_truth_candidates/`. |

**No other corpus video is affected** — all 13 were re-checked frame by frame.

**The rule this establishes:** a video with its own translation on screen is a *labelled
reference render*, not a corpus input. Those live in `ground_truth/` and
`ground_truth_candidates/` beside the SRTs they came from. Anything in `videos/` must carry
`label_in_input: false` in `manifest.json`. `asl-eval/check_leakage.py` enforces this.

## Ground truth — 4 of 13

| Video | Kind | Lines | Diagnostic content? |
|---|---|---|---|
| `155_demo_asl-demo-translation_26.7s` | human-translated, verified | 6 | ✅ ages/numbers — **but see the leakage warning above: the reference is sound, the input was not, and there is no valid prediction** |
| `1252_1000016397_76.8s` | human-translated by Curify, verified | 11 | ✅ **fingerspelled names** (Greg, Sara) + numbered items |
| `1320_1000022357_137.2s` | candidate SRT derived from **burned-in English captions** | 14 | ✅ full sentences — **score only via the masked input** |
| `1434_screenrec_youtube_16.6s` | crowd-sourced YouTube comment | 11 (6 in clip) | ❌ **greetings only — see warning** |

Reference renders with captions burned in live alongside their SRTs in `ground_truth/` and
`ground_truth_candidates/`. **They are references, never inputs.**

**⚠️ The 1434 warning matters more than the rest of this file.** Its clip contains only the
greeting exchange, which is the highest-prior content in ASL. A vision model emits
"Hello / How are you? / I'm fine" for *any* two-people-signing video without decoding a
single sign, so it scores ~65% by guessing and looks like success. **Do not use 1434 as an
acceptance test.** The diagnostic half — lines 7–11, the deaf/hearing exchange — is not in
the clip and has still never been tested.

`1320` is the best item here: studio-quality, single signer, face fully visible, and it
carries its own aligned English translation burned into the frame — which makes it both the
most valuable item and the one that most easily produces a fake result. **Score it only
through `videos/1320_….mp4`, the masked render**; the unmasked source in
`ground_truth_candidates/` exists to derive the reference from, not to feed the model.

**Production direction: RESOLVED 2026-08-30.** OCR of the title cards reads *"Certificate
Program for Sign Language Interpreters — RECEPTIVE SKILLS EVALUATION"*, *"SIGN TO VOICE"*,
*"Record yourself voicing the video"*. It is an interpreter certification exercise, so the
ASL is the source and the captions are the answer key. The remaining step before the
candidate can be promoted to gold is an annotator confirming the caption text against the
actual signing.

## Predictions — Baseline 0

`predictions_baseline0/` holds what the live tool actually returned, straight from
`projectsegment`. Config is in `manifest.json → baseline0_config`; the short version is
`gemini-2.5-flash` over ≤96 motion-adaptive stills at 512px, batched 24/call, **temperature
unset**.

This output is **unverified and non-deterministic**. Treat it as the control to beat, never
as a reference.

## The determinism pair — start your experiments here

`1466_nohead-half1` and `1467_nohead-half1` are the same video, submitted by two different
accounts 11 seconds apart, processed as two independent production jobs. Not byte-identical
(independently re-encoded on upload) but identical in content: same duration to the
millisecond, same 5684 frames, sizes differ 0.02%, frames sampled at 30s/90s/150s are
visually identical.

- **Segment boundaries: 29 of 45 shared** → the motion sampler is deterministic.
- **Text: effectively zero overlap** → the recogniser is not.
- `"Apply hand cream."` vs `"Wash your hands."` at the same timestamp.

That is a free, real-data decomposition of *where signing happens* (stable) from *what was
signed* (not stable). Both submitters were charged 32 credits.

**Before drawing conclusions from it:** decode temperature is unset, so the provider default
of 1.0 is doing some unknown share of this work. Pin `temperature=0` and re-run — that is the
cheapest experiment available and it is a one-line change.

**Also note the framing.** `"No head half 1.mp4"` is literal: the shot cuts off the signer's
head. With no face there are no non-manual markers, so this input is missing a large part of
ASL's grammar by construction. Its degenerate output (`Many / Many / All`, `Not / Not / Not
over`) is at least as attributable to framing as to sampling density. Don't treat this pair
as representative of well-framed ASL.

## Two corrections to the 8.22 research pass

1. **Curify already ships motion-adaptive sampling.** `BOSS_SUMMARY.md` proposes
   denser/motion-aware sampling (Baseline 1) as the cheapest next win. It is already live:
   the sampler puts 100% of its frame budget inside active-signing runs and was independently
   validated. The genuinely untried cheap lever is `temperature=0` plus self-consistency.
2. **Sampling density was tested and ruled out** as the cause of the instability, on
   2026-08-18, at 1 frame/0.175s — denser than uniform and near the budget ceiling. Output
   was still non-deterministic. Density *does* matter across durations (see
   `baseline0_config.note_on_budget`), but it is not what makes repeat runs disagree.

## Provenance

Videos pulled from Azure blob container `processed-videos`; metadata from Curify's Supabase
`project` / `projectsegment` / `video` / `transaction`. Full analysis, the P0 list, and the
reason this workstream was closed on 2026-08-18:
**`curify-studio/docs/asl-translation-mvp-spec.md`** (the ASL index).

Duplicate blob copies were dropped: user 1415's video existed twice (two failed jobs, byte-
identical) and user 1252's 76.8s video existed twice (`subtitle_only` + `full_translation`,
byte-identical). One copy of each is included.
