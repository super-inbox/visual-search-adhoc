# Gemini Native-Video Evaluation — Blocker Status

**Date:** 2026-09-10 (updated same day: `G05uFub3YFc_9-2-rgb_front` retry)
**Branch:** `baobao/asl-temporal-ablation-2026-09-06`
**Status:** 5/12 diagnostic clips valid and scored. BLOCKED on the remaining 7 — a
root-cause-unresolved Files API issue, not a code/logic failure — no parameter tuning was
applied in response to it. `G05uFub3YFc_9-2-rgb_front` previously had a separate, local
response-parsing bug (bare-JSON-array response), found and fixed during the 2026-09-10
delivery QA pass; a subsequent retry with the fix in place made a real `generate_content`
call and produced a valid (non-semantic-recovery) prediction. **G05 is no longer
parser-blocked and is not counted among the unresolved 7** — see §"5 valid native-video
predictions" and §"7 clips without a valid native-video prediction" below.

## Manager method (Section 13, verified config)

`run_native_video.py`'s independent variable is **frame-based input vs. native/direct
video input** — the model receives the whole `.mp4` via the Gemini Files API in one call,
instead of sampled JPEG frames. Model, prompt-intent, and decoding knobs are held as close
to the frame-baseline control (`evaluation_2026_09_04_gemini_3_6`) as the manager's
Section 13 guidance allows (one unavoidable prompt confound, §13.1, is documented in
`run_native_video.py`'s own module docstring).

Verified config used throughout: `native_video_2026_09_10_gemini_3_6`
(`model=gemini-3.6-flash`, `thinking_level=medium`, no explicit temperature). Recorded
provenance on every prediction: `source_repo=curify-studio`, `source_ref=origin/main`,
`source_commit=db86417ec1889858f5b163503a60253302843644`,
`source_file=docs/asl-translation-mvp-spec.md`, `source_section="13. Change record —
2026-09-10 (native video input — the first intervention that moved anything)"`.

Pre-registered decision gate (manager's §7 P0-4), recorded verbatim in every run's
`run_metadata.json`:
- **Promotion:** ≥3 of 12 diagnostic clips move `semantic_adequacy` 0→≥1, OR
  `reference_topic_mismatch` flips yes→no on ≥3 of 12.
- **Rejection:** 0/12 clips flip category AND WER movement sits inside the pooled
  decoding-noise floor (§12.2: mean \|delta\| 0.029–0.107) → native video is not the
  answer either; record and stop, do not scale to 128.

## Stage 1 — single-clip smoke test: succeeded

`FzmL8SL6Bow_1-8-rgb_front` run end-to-end (upload → inference → parse → score →
cleanup), all steps succeeded. Result was **not semantic recovery**: WER 1.0000,
CER 0.9298, BLEU 0.0008, chrF 1.7407. Reference topic (wall/drywall repair) was not
recovered; prediction ("An ugly frog a big, fat frog") is a different hallucination than
the frame-baseline's ("I looked and saw a dog... bear...") but the same failure class —
severe under-generation (7 predicted words vs. 78 reference words) plus topic mismatch.

## Stage 2 — diagnostic-12: 4/12 scored, 8/12 blocked (superseded by Stage 3 below)

Two identical invocations of the approved command were run — the second was a pure retry,
no parameters changed:

```
python3 asl-translator/evaluation/run_native_video_how2sign_v2_benchmark.py \
    --config native_video_2026_09_10_gemini_3_6 \
    --clip-ids-file asl-translator/evaluation/diagnostics/phase1_temporal_ablation/diagnostic_12_clips.json \
    --run --acknowledge-private-data-upload
```

Both invocations produced the **same split**: the resumability logic correctly skipped
the 4 already-completed clips (including the preserved Stage-1 result) and re-attempted
only the missing 8 both times.

### 4 valid native-video predictions (as of Stage 2)

| clip_id | native WER | native CER |
|---|---|---|
| `FzmL8SL6Bow_1-8-rgb_front` | 1.0000 | 0.9298 |
| `-g0sqksgyc4_3-2-rgb_front` | 1.0000 | 0.8022 |
| `92V3oH63zbQ_5-1-rgb_front` | 1.0000 | 1.0000 |
| `fzNnTgHa1lM_2-5-rgb_front` | 0.9118 | 0.7962 |

0/4 show semantic recovery (semantic adequacy remains "completely wrong" and reference
topic mismatch remains "yes" on every one of these 4, matching the frame-baseline's
failure class).

### 8 clips without a valid native-video prediction as of Stage 2 (7 blocked before model inference; 1 — `G05uFub3YFc` — failed after a real model call, and was resolved in Stage 3)

| clip_id |
|---|
| `G05uFub3YFc_9-2-rgb_front` (**resolved in Stage 3 below — no longer blocked**) |
| `fZM3IcM2Xs4_14_15_16-10-rgb_front` |
| `-g0iPSnQt6w_0-1-rgb_front` |
| `g2NA_eBUcH8_0-3-rgb_front` |
| `G19uBylwQww_1-2-rgb_front` |
| `Fz-N1S0swh8_2-8-rgb_front` |
| `g0TkUiO7t4I_6-8-rgb_front` |
| `g2ELiaFjKfs_3-10-rgb_front` |

7 of the 8 failed during the **Gemini Files API upload/poll step, before the
`generate_content` model call was ever made** — i.e. before model inference, not a
model-output or scoring problem. First attempt: `RuntimeError: Gemini Files API reported
FAILED for '<file>'` on all 8 (including `G05uFub3YFc`). Second attempt (pure retry, no
config change): the same 7 clip IDs failed again with the identical `FAILED`-state error.

**`G05uFub3YFc_9-2-rgb_front`'s second attempt was a different case — corrected during
later QA, then validated by a successful third attempt (Stage 3).** Its Stage-2
`per_clip_results.json` entry showed `inference_wall_clock_s: 16.622` — consistent with a
real `generate_content` call (comparable to the 4 valid clips' 8.5–18.5s call times), not
the ~3s immediate `FAILED`-state response the other 7 get. The actual error,
`AttributeError: 'list' object has no attribute 'get'`, traced to `run_native_video.py`'s
response-parsing step (`data.get("segments", [])`, reached only *after* a successful
`generate_content` call) firing when the model returned a bare JSON array instead of the
requested `{"segments": [...]}` object — a **local parsing bug, not a Files API or
backend problem**, and not evidence about Files-API stability either way. Fixed in
`run_native_video.py` (now accepts either shape) as part of the 2026-09-10 delivery QA
pass. At the time that fix landed, no Gemini call had been made to verify it end-to-end —
Stage 3 below is that verification.

## Stage 3 — `G05uFub3YFc_9-2-rgb_front` retry: succeeded, parser fix validated

A single-clip retry of `G05uFub3YFc_9-2-rgb_front` (same command as Stage 2, unchanged
config `native_video_2026_09_10_gemini_3_6`; resumability skipped the other 11 clips) was
run after the bare-array parsing fix landed. **This is the retry that validates the fix**:
`generate_content` returned a bare JSON array (the same response shape that triggered the
Stage-2 `AttributeError`) and `run_native_video.py` parsed it correctly this time, with no
error.

Result: `model_calls=1`, `inference_wall_clock_s=17.459`, `status=success`.

| clip_id | native WER | native CER | native BLEU (sentence) | native chrF (sentence) |
|---|---|---|---|---|
| `G05uFub3YFc_9-2-rgb_front` | 0.9412 | 0.7251 | 0.9745 | 13.4619 |

Reference (breathing-exercise instructions) vs. prediction ("I was terrified and my heart
was pounding. Then I looked closely and saw what was actually there.") — **not semantic
recovery**: topic mismatch persists (fear/startle narrative vs. breathing instructions),
same failure class as the other 4 valid native-video clips and as this clip's own
frame-baseline prediction (which hallucinated a different, also-unrelated cloth/gear/fire
narrative). `semantic_adequacy` remains 0 ("completely wrong"); `reference_topic_mismatch`
remains "yes".

**G05 is now counted among the 5 valid native-video predictions, not among the unresolved
7.** It should not be pooled with the 7 Files-API-`FAILED` clips when reasoning about that
root cause — its failure-then-success arc was a local parsing bug, fully independent of
whatever is wrong with the other 7.

## Root cause of the remaining 7: unresolved

**Do not treat this as confirmed to be a Gemini backend-only issue.** One piece of
evidence is consistent with transient/account-side Gemini Files API degradation:
- `client.files.list()`, called independently (outside the harness, to check for
  orphaned uploads) failed identically on two separate occasions with
  `ServerError 500 INTERNAL: Failed to convert server response to JSON`.

(The second attempt's differing error shape on `G05uFub3YFc` is no longer read as evidence
of backend instability — see above: that clip's failure has a separate, known, now-fixed
local-code cause and should not be pooled with the remaining 7 when reasoning about
Files-API root cause.)

But the same **7** clip IDs failing identically on **both** independent attempts is also
consistent with a **clip-specific Files-API processing incompatibility** that a backend
glitch alone would not explain (pure transient noise would be expected to hit a
different/random subset each time). A local, non-API inspection of the 12 source videos
(codec, resolution, pixel format, frame rate, file size via `ffprobe`) found **no
distinguishing pattern** between the 8 failing and 4 succeeding clips — all 12 are
h264/1280×720/yuv420p, and both sets span overlapping duration/framerate/size ranges. This
rules out the obvious local explanations but does not resolve the question.

**Conclusion: root cause is genuinely unresolved for the remaining 7 — either (a)
transient/account-side Gemini Files API degradation, or (b) a clip-specific Files-API
processing incompatibility in these 7 videos. Do not report either as confirmed.**

## What is preserved / verified

- The 5 successful native-video predictions (the original 4 plus `G05uFub3YFc` as of
  Stage 3) are preserved on disk under their own config metadata
  (`asl-translator/evaluation/results/how2sign_v2/curify_gemini_native_video_2026_09_10/`).
- Resume behavior is verified end-to-end across three invocations (two full Stage-2 runs
  plus the Stage-3 single-clip retry): re-running the harness against the same results dir
  skips all already-completed clips and attempts only the still-missing ones — no re-work,
  no risk to the valid predictions.
- Every uploaded Gemini file across the Stage-2 attempts (8 + 7 = 15 stray `FAILED`-state
  uploads whose file IDs were recoverable from the logs) was individually verified
  (`state=FAILED`) and deleted. One file ID (`G05uFub3YFc_9-2-rgb_front`'s Stage-2
  second-attempt upload) could not be recovered from the log because the `AttributeError`
  fired before the file name reached the error message; it was not manually deleted, but
  Gemini's Files API auto-expires uploads after 48 hours regardless of manual cleanup. The
  Stage-3 retry's upload completed and was processed normally (no `FAILED` state).
- No commits, no pushes, no changes to `curify-studio`, no parameter tuning applied at any
  point in response to any failure (Stage 1's semantic failure, Stage 2's API failures, or
  the Stage-2 parsing bug — Stage 3 changed only the response-parsing code path already
  fixed pre-retry, not the model/prompt/decoding config).

## What is blocked

- **7 of 12 diagnostic clips are still unscored** — the Files-API-`FAILED` group; root
  cause unresolved (see above).
- **Do not extrapolate the 5/12 result to the full diagnostic-12.** With 0/5 semantic
  flips so far, reaching the promotion threshold (≥3/12) is still mathematically possible
  depending on the outcome of the 7 missing clips; the rejection criterion (0/12 flip)
  cannot be asserted from 5/12 either. The **§7 P0-4 decision gate has no valid answer
  yet** — it requires all 12 clips.

## Next action (not code/parameter changes)

Per current instructions, do not retry the remaining 7 clips in this pass. When that retry
does happen, it is the same command as above; resumability will skip the 5 valid clips
(including `G05uFub3YFc`) automatically:

```
python3 asl-translator/evaluation/run_native_video_how2sign_v2_benchmark.py \
    --config native_video_2026_09_10_gemini_3_6 \
    --clip-ids-file asl-translator/evaluation/diagnostics/phase1_temporal_ablation/diagnostic_12_clips.json \
    --run --acknowledge-private-data-upload
```

If a third identical attempt still fails on the same 8 clip IDs, that would be stronger
evidence against pure backend transience and toward a clip-specific incompatibility
worth investigating directly (e.g. via Gemini API support/status channels) rather than
retried indefinitely.
