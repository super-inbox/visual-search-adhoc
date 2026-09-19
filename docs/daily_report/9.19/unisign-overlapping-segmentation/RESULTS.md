# Manager task (b): should long ASL videos be segmented before Uni-Sign?

Date: 2026-09-19 · Scope: local R&D POC, **n = 1 long clip**. Research repo only; `curify-studio` tracked files untouched; no ACR / Azure / production changes; Uni-Sign's 256-frame preprocessing not modified. This folder contains reports, scripts and small logs only: **no checkpoint (`.pth`) and no generated video (mp4) is committed**; the checkpoint was mounted read-only and never copied.

**Classification: B — NO CLEAR BENEFIT YET.** Segmentation mechanically removes the random 618→256 frame drop, but this one clip gives no evidence that translations got *better*.

---

## 0. Audit of the pre-existing uncommitted POC (done first, nothing modified)

> **Provenance note.** The artifacts audited in this section were **pre-existing local, untracked files** on the author's working copy: `asl-translator/asl-eval/overlapping_segmentation_poc/` (3 scripts + `results/*.json`) and `docs/daily_report/9.18/asl-manager-followup-a-c/OVERLAPPING_SEGMENTATION_POC.md` (plus a +63-line "Phase B" section in the tracked `docs/daily_report/9.18/asl-manager-followup-a-c/MANAGER_SUMMARY.md`, an uncommitted local modification). They were inspected only for historical comparison. They are **not part of this branch and are not present on GitHub**, so readers should not expect to find them there. They were left untouched (not modified, staged or committed); the description below is the only record of them in this repo.

| Question | Finding |
|---|---|
| Who/what created it? | **Not in git history at all** (`git log --all -- <paths>` empty; untracked). Files were written 2026-09-19 01:28–02:13 in this same worktree; the report says "Phase A/C were run 2026-09-18" and answers the earlier Phase-B request. Authorship (which session or tool) cannot be determined from git or file metadata. I did not modify or stage any of it (SHA-256 snapshot taken during the audit and re-checked in final QA). |
| What exists? | `segment_video.py` (exact DP over the whole chain on the 0.25 s motion grid), `run_unisign_segments.py` (POST each segment once), `analyze_results.py` (raw concat + a suffix/prefix stitch, scoring), and results for 13 segments. |
| Motion detector | Reuses `run_current_model.probe_motion` + `segment_runs` unmodified. Same choice I make below. |
| Does it match the **current** requirement? | **Partly.** Video-level segmentation ✅, motion-aware boundaries ✅, overlap 0.5–1.5 s ✅, each segment sent independently ✅, merged view ✅ (raw + stitch). **Not** matching: segment length is interior **6.0–7.5 s (target 7.0)** and final 4.0–7.5 s rather than 4–8 s / target 6.0; adds a hard **≤240-frame** constraint (which pre-empts the 256-cap question); DP rather than the specified per-boundary search. |
| Ever executed? | **Yes.** 13 segments, 13/13 HTTP 200, request timestamps 06:44–07:09 UTC (= 01:44–02:09 local), `segment_results.json` contains raw service responses. Not a dry run. |
| Real checkpoint? | Responses carry the service's `model.checkpoint = how2sign_pose_only_slt.pth` label and are real, distinct, non-empty translations. The label is service metadata, so this is strong-but-not-hash-level evidence; checkpoint SHA can't be recovered from the artifacts. |
| Valid / reproducible? | Valid as an **independent prior data point, but on a different video**: `1252_1000016397_76.8s.mp4` (76.8 s, 2283 frames, variable frame rate, portrait) whose reference is flagged non-independent/circular (`usable_for_official_metrics=false`) so its metrics are "exploratory". One segment took an unexplained 810 s (others 44–87 s). Scripts are deterministic and re-runnable, but results aren't tied to the frozen How2Sign clip. Its conclusion (INCONCLUSIVE) is about that video only. |

**Verdict: existing POC ≠ completed task (b).** It is a real executed experiment on another video with different parameters, so it neither answers the frozen-baseline comparison nor replaces it. I therefore ran the frozen-clip experiment from scratch in this new folder and left the old work alone. Its 13-segment result is directionally consistent with mine (no exact overlap duplication; per-segment outputs plausible-looking but unverified).

---

## 1. Manager question

> Determine whether long ASL videos should be segmented before Uni-Sign. Reuse the existing motion detector, but make overlapping segmentation (each clip ≈4–8 s, ≈0.5–1.5 s overlap). Compare whole-video Uni-Sign against segmented Uni-Sign.

## 2. Existing whole-video baseline (frozen; not re-run)

Source: `docs/daily_report/9.19/unisign-real-e2e/` (`RESULTS.md`, `long_response*.json`, `scores.json`, `long_container_log_filtered.txt`, `long_ffprobe.txt`). I re-scored both raw responses and they reproduce `scores.json` exactly (asserted in the script).

| Item | Value |
|---|---|
| Clip | `asl-translator/data/public_benchmarks/how2sign_v2/videos/FzmL8SL6Bow_1-8-rgb_front.mp4` (frozen How2Sign v2 test clip) |
| Duration / frames / fps | 25.75 s (manifest 25.77) · **618 frames** · 24 fps CFR · 1280×720 h264 |
| Reference (78 words) | *You want to go and clean up that hole you just made and now we are going to go and start winding our hole you just made and start spreading it out just like that and all the while I am pulling it out while my hands here are watching this wall here because this wall here is going to want to get out of control but I'm not going to let it, my hands are there.* |
| Direct prediction (run 1) | *We're going to go ahead and put this on the bottom and we're going to go ahead and put this on the bottom and we're going to go ahead and take our rubber band and* |
| Direct prediction (identical request, run 2) | *So I'm going to take this hole because it's going to be nice and clean and then I'm going to take this hole and I'm going to have the rubber band here and I'* |
| Metrics run 1 / run 2 | WER 0.8718 / 0.8590 · CER 0.7022 / 0.7022 · BLEU 2.48 / 1.86 · chrF 20.51 / 21.99 |
| Runtime | 101.04 s / 99.84 s |
| Frame handling | 618 pose frames extracted → `max_length=256` → `sorted(random.sample(range(618), 256))` (`datasets.py`): **256 kept (41.4 %), 362 dropped at random**. The RNG is seeded once at model load (`set_seed(42)`) and never per request, so **identical requests differ** (the two outputs above). I re-read the vendored code inside the running container: sampling happens only if `duration > max_length`, else `list(range(duration))`. |

## 3. Motion detector reused

`probe_motion()` + `segment_runs()` in `asl-translator/asl-eval/run_current_model.py`. I diffed their executable code against curify-studio `origin/main:curify_background/app/utils/asl_utils.py` (`_probe_motion`, `_segment_runs`): **identical; only docstrings differ**. No new detector was written.

1. **Input handling:** one ffmpeg pass, `fps=4,scale=160:h,format=gray` → raw frames in memory.
2. **Motion score:** mean |gray[i+1] − gray[i]| over the whole 160-px frame (global frame difference; not pose/hand-specific).
3. **Temporal resolution:** 4 Hz → one value per 0.25 s, `times[i]=(i+1)/4`. For this clip: 102 samples, t = 0.25…25.5 s.
4. **Smoothing / thresholds:** 5-tap boxcar (1.25 s window); idle threshold = max(35th percentile of smoothed motion, 2.0). Here 2.871.
5. **Active/idle runs:** `segment_runs` labels runs above/below threshold.
6. **Pauses/minima extractable?** Yes, from the smoothed series (`segment_runs` discards it; I re-apply the same 3-line kernel). Reliability is limited: the global frame diff also fires on head/torso movement, and a 1.25 s kernel blurs short pauses. On this clip only ~2 clear pauses exist (see §10, item 9).
7. **Reusable for boundaries?** Yes — reused *signal only*. **Not** reused: `allocate_timestamps*` / `extract_frames` (they budget still frames for a VLM prompt and never yield contiguous cut points). Old frame-sampling behaviour is not involved anywhere.

## 4. Segmentation algorithm (deterministic; video/motion only)

`scripts/segment_video.py`. Inputs to boundary choice: motion series and video duration. No reference text, no Uni-Sign output. **Parameters were fixed before any inference and not tuned afterwards.**

| Parameter | Value |
|---|---|
| target / min / max segment | 6.0 / 4.0 / 8.0 s |
| overlap target / range | 1.0 s / 0.5–1.5 s |
| grid | 0.25 s (the detector's resolution) |
| distance weight λ | 0.30 |

Greedy forward pass, per segment starting at `s`:
1. If `video_end − s ≤ 8`: final segment, ends at video end.
2. Else **end** `e` = argmin over the 0.25 s grid in `[s+4, s+8]` of `motion_percentile_rank(e) + 0.30·|e−(s+6)|/2`, restricted so a following segment ≥ 4 s still fits.
3. **Next start** `s'` = argmin over `[e−1.5, e−0.5]` of `rank(s') + 0.30·|(e−s')−1|/0.5`.
4. Repeat. Ties → closer to target, then earlier.

`rank` = percentile of smoothed motion within this video (0 = calmest). Chronology is preserved by construction; the overlap is ≥ 0.5 s so there are no gaps; the last segment is ≥ 4 s unless the whole video is shorter than 4 s (that is the only unavoidable short case). `validate()` re-checks all constraints; problems = none.

## 5. Segment table (manifest: `segmentation_manifest.json`)

Clips were cut with ffmpeg (video-only libx264 crf 18, `-fps_mode passthrough`; **kept outside git**, in the session scratchpad). Every clip was verified readable, correct duration, frame count = expected pts count, chronological.

| # | start | end | dur | overlap w/ prev | frames | start-boundary motion (rank / idle-run / local-min) | end-boundary motion (rank / idle-run / local-min) |
|---|---|---|---|---|---|---|---|
| 0 | 0.00 | 6.75 | 6.75 | – | 162 | video start | 0.257 / idle / yes |
| 1 | 5.75 | 10.75 | 5.00 | 1.00 | 120 | 0.584 / active / no | **0.030 / idle / yes** |
| 2 | 10.00 | 14.25 | 4.25 | 0.75 | 102 | 0.149 / idle / no | 0.168 / idle / yes |
| 3 | 13.25 | 19.50 | 6.25 | 1.00 | 150 | 0.386 / active / no | 0.624 / active / yes |
| 4 | 18.50 | 25.75 | 7.25 | 1.00 | 174 | **0.792 / active / no** | video end |

5 segments, 4–8 s each, overlaps 0.75–1.0 s (all within 0.5–1.5). All timestamps are **wrapper/source-derived** (`source: "wrapper_segmentation"`); Uni-Sign has no native temporal alignment.

## 6. Frame-count / 256-cap analysis

Uni-Sign's `max_length` = 256 frames. Numbers are the native frame counts of the physical clips, cross-checked against the service's own `Processing frames: N/N` counter.

| | frames | > 256? | SUBSAMPLING REQUIRED |
|---|---|---|---|
| **Whole video** | **618 → 256** (362 dropped at random) | yes | **YES** |
| Segment 0 | 162 (service saw 162) | no | **NO** |
| Segment 1 | 120 (120) | no | **NO** |
| Segment 2 | 102 (102) | no | **NO** |
| Segment 3 | 150 (150) | no | **NO** |
| Segment 4 | 174 (174) | no | **NO** |

**Segmentation removed the random subsampling entirely.** 0 of 5 segments hit the cap; max segment = 174 frames. Total frames processed = 708 = 618 + 90 extra from overlap (14.6 % overhead). Preprocessing was not modified.

Engineering caveat: the cap is in **frames**, not seconds. At 24 fps an 8 s segment is 192 frames, but at 30 fps it is 240 and at 60 fps 480 (> 256). A duration-only 4–8 s rule is not fps-safe; a production version should use `max_seg_sec = min(8, 256/fps)`.

## 7. Real Uni-Sign inference

Same real checkpoint as task (a): `how2sign_pose_only_slt.pth`, SHA-256 `1bfd5f33…fb00d` **verified on the host and again inside the container**; mounted read-only, not copied or committed. Image `uni-sign-local:test` (linux/amd64, emulated on Apple Silicon), container `uni-sign-taskb` on port 8010, service code unchanged (`curify-studio` `git status` clean for tracked files). **`/healthz` = 200, `/readyz` = 200** (model loaded strictly). `/translate` called **once per segment**, sequentially.

| # | HTTP | wall-clock | frames seen | random 256 sampling | warnings/errors | Uni-Sign output (raw) |
|---|---|---|---|---|---|---|
| 0 | 200 | 78.0 s* | 162 | no | none | *So I'm just going to go ahead and put that into the bottom of the glass, and I'm just going to go ahead and just rub it on to the bottom of the glass.* |
| 1 | 200 | 37.1 s | 120 | no | none | *And then we're going to go ahead and drill the hole in the wheel.* |
| 2 | 200 | 31.3 s | 102 | no | none | *We're going to have a pair of rubber stamps here.* |
| 3 | 200 | 46.4 s | 150 | no | none | *You don't want to use it when you're watching and you don't want to move around too much.* |
| 4 | 200 | 55.7 s | 174 | no | none | *And then we're going to go ahead and put the bottom of the pot and we're going to talk about the bottom of the pot.* |

\* Segment 0 was the first request to a fresh container, so it includes the one-time ~132 MB rtmlib ONNX weight download (visible in `segment_container_log_filtered.txt`). Only upstream noise otherwise; container `OOMKilled=false`, 0 restarts.

**Determinism probe (extra, not scored):** segment 2 re-sent once → **bit-identical** output (`determinism_probe_seg2.json`). Consistent with the code path (≤256 frames → no RNG) and with task (a)'s short clip. I did not rerun the other segments.

## 8. Merged outputs and metrics

Merge views (`scripts/merge_and_score.py`; deterministic, no LLM, no reference, text only ever deleted):
- **B — naive concatenation:** chronological join.
- **C — overlap dedup:** for each adjacent pair, drop the longest exact (case/punctuation-insensitive) run of ≥ 2 words that repeats the previous text's tail at the next text's head.

**Result: the dedup removed nothing.** At all 4 junctions the exact suffix/prefix match was 0 words, so **B and C are the same string**. Both are preserved in `comparison_metrics.json`.

**B = C (naive = dedup):**
> So I'm just going to go ahead and put that into the bottom of the glass, and I'm just going to go ahead and just rub it on to the bottom of the glass. And then we're going to go ahead and drill the hole in the wheel. We're going to have a pair of rubber stamps here. You don't want to use it when you're watching and you don't want to move around too much. And then we're going to go ahead and put the bottom of the pot and we're going to talk about the bottom of the pot.

Same scoring conventions as `score_e2e.py` (WER/CER = repo `lib.text_metrics`; BLEU/chrF = sacrebleu sentence-level on the normalized strings). Reference = same 78-word reference.

| | WER | CER | BLEU | chrF | pred words | ref words | unigram recall / precision | repeated 3-grams |
|---|---|---|---|---|---|---|---|---|
| **A. Direct, run 1** | 0.8718 | 0.7022 | 2.48 | 20.51 | 38 | 78 | 0.231 / 0.474 | 18 |
| A. Direct, run 2 (same request) | 0.8590 | 0.7022 | 1.86 | 21.99 | 38 | 78 | 0.295 / 0.605 | 7 |
| **B. Segmented + naive** | **1.1795** | **0.8146** | 3.17 | **35.33** | 110 | 78 | 0.449 / 0.318 | 33 |
| **C. Segmented + dedup** | 1.1795 | 0.8146 | 3.17 | 35.33 | 110 | 78 | 0.449 / 0.318 | 33 |

WER above 1 is possible (insertions): the segmented output is 1.41× the reference length. Unigram recall/precision and repeated-3-gram counts are exploratory diagnostics I added, not manager metrics.

## 9. Runtime / cost comparison

| | direct | segmented |
|---|---|---|
| model calls | 1 | 5 |
| runtime | 101.0 s (run 2: 99.8 s) | **248.5 s** sum of calls (2.46×); **≈ 221 s (2.19×) after removing an estimated ~27 s cold-start download** in segment 0 (estimate from the ~0.31 s/frame rate of segments 1–4) |
| frames extracted / reaching the model | 618 extracted, **256** to the model | 708 extracted, **708** to the model |
| segments needing random sampling | 1 | **0** |
| frames dropped at random | 362 | **0** |

Runtime is close to linear in frames (0.31 s/frame). Segments are independent so could be parallelised, but I did not test that (container has 7.65 GiB; the single long clip already peaked at 6.6 GiB in task (a)). Both runs are under amd64 emulation; absolute times aren't representative of a native server.

## 10. Qualitative analysis (n = 1; not generalisable)

1. **Did segmentation prevent the 618→256 random loss?** **Yes, unambiguously and mechanically.** 0/5 segments subsampled; service logs show every frame consumed.
2. **Deterministic repeated inference?** For segment 2, **yes** (identical repeat), as the code path predicts. The whole-video direct request was *not* deterministic (two different outputs). Only one segment was re-run.
3. **More reference content covered?** The output now spans the whole timeline and is 110 words instead of a 38-word output that stopped early. But **topical accuracy is not shown**: the reference talks about cleaning/winding/spreading a hole and the signer's hands; the segmented text talks about a glass, a wheel, rubber stamps, a pot. Overlap with the reference is mostly filler ("going to go ahead", "want"), plus "hole" and "watching". Direct run 2 also got "hole" and "clean". My "non-stopword" diagnostic is dominated by filler words (`go`, `going`, `want`) so I do not rely on it.
4. **Duplicate text introduced?** No exact duplicated text across the 4 overlaps (0-word suffix/prefix matches; the longest shared runs were generic: "going to go ahead and", "we're going to", "to", "to"). But repeated 3-grams rose from 7–18 (direct) to 33, driven by filler like "we're going to go ahead and", including a repeated clause inside segment 0 and segment 4. Repetition did not go away.
5. **Did overlap help or hurt merge quality?** **Cannot tell.** Adjacent segments produced unrelated sentences for the same ≈1 s of video, so there is nothing to dedupe and no evidence the overlap preserved a boundary-crossing sign. It cost 90 extra frames (14.6 %).
6. **Did metrics materially change?** Mixed. WER 0.87→1.18 and CER 0.70→0.81 got worse (mostly insertions from longer output). chrF 20.5/22.0→35.3 and BLEU 2.5/1.9→3.2 rose (chrF is recall-weighted and rewards longer output). The two identical direct requests already differ by ~0.6 BLEU / ~1.5 chrF, so the chrF gain (+13 to +15) is well outside that spread while the BLEU gain (+0.7 to +1.3) is the same order as it. No metric change is interpreted as "better" or "worse" quality.
7. **Runtime cost:** ≈2.2× (≈2.5× raw) and 5× calls.
8. **Is 4–8 s / ~1 s overlap technically reasonable?** Yes for this clip: all segments 102–174 frames, well under 256; and in the frozen 128-clip benchmark the median clip is 5.15 s with 52 % in 4–8 s (so this matches the sentence-level clips Uni-Sign is used on), while 23 % of that benchmark exceeds 10.67 s (= 256 frames at 24 fps, assuming 24 fps). Needs the fps-aware cap in §6.
9. **Is motion-aware boundary selection visibly sensible?** **Partly.** Chosen interior boundaries have mean motion rank **0.374** vs 0.515 for a naive fixed 6 s/1 s grid and 0.552 for a uniformly random cut in the legal windows, so the search does pick calmer points. Reading frames at each boundary (`boundary_frames.jpg`; order E0 6.75, S1 5.75, E1 10.75 / S2 10.0, E2 14.25, S3 13.25 / E3 19.5, S4 18.5, and 23.5 for reference): 10.0 and 10.75 are true rest poses (the only real pause in the clip), most others show hands low or between signs, but **S4 at 18.5 s is mid-sign** (rank 0.79) and E3 19.5 is only mid-ranked (the whole legal 17.25–21.25 s search window contains no calm point; its best rank is 0.515). This signer signs near-continuously, and the overlap prior forces start boundaries away from the calmest point. The tail (22–25.75 s) is ≈3.5 s of idle inside segment 4, which the model still turned into a sentence. Both are visible in `motion_strip.txt`.

## 11. Optional second long clip (Phase 10) — not run

The gate requires that one more example would *materially clarify the engineering decision*. It would not: the manager's rule is to not overclaim from n=1 or n=2, so the classification could not move beyond "B" (or become "A"/"C") on a second clip, and there is still no segment-level gold to score against. The mechanical finding (§6) does not depend on the clip. Stopped at one clip, as instructed for this case.

## 12. Limitations

- **n = 1** long clip; the direct baseline has only 2 samples and they disagree.
- **Single 78-word reference for a 25.75 s clip, no temporal alignment.** Segment-level correctness can't be scored; WER/BLEU/chrF against one long reference mostly measure length and generic overlap.
- Sentence-level BLEU on one item is very noisy; chrF favours longer output; WER can exceed 1.
- **No segment-level references exist** for this source clip, so per-segment translation quality cannot be scored.
- **Overlap benefit could not be established:** adjacent segments gave unrelated text for the shared ≈1 s, so there is no evidence the overlap preserved a boundary-crossing sign.
- Segments were **re-encoded** (crf 18) before pose extraction, so the pose model saw slightly recompressed frames (small possible confound; not measured).
- Global frame-difference motion is a coarse pause detector; only ~2 real pauses in this clip; λ and the overlap prior were chosen a priori, not tuned or ablated.
- Runtime measured under amd64 emulation; the cold-start correction (~27 s, 221 s "warm") is only an **approximate** estimate.
- The old 13-segment POC (local, untracked, not on this branch; see §0) was on a different video/parameter set and is not combined with these results.

## 13. Recommendation

- **Segmentation stays an *experimental candidate* preprocessing step for clips beyond the 256-frame cap — not a production recommendation.** It removes the random frame drop and per-request nondeterminism, at ≈2× cost. But **do not claim a translation-quality gain**, and do not ship the merge step: the dedup did nothing here, and simple concatenation yields long, generic, partly hallucinated text. This is an n = 1 result and must not be generalised.
- If pursued, cap segments by frames (`min(8 s, 256/fps)`), and consider dropping/merging idle-only segments instead of translating them.
- **The next experiment needs segment-level gold.** How2Sign IDs are sentence-level clips of longer videos (`FzmL8SL6Bow_1-8`); concatenating consecutive sentence clips of one video would give long videos with known per-sentence references and boundaries, allowing real segment-vs-whole and boundary-quality evaluation. (Needs clips outside the frozen 128, so it was not done here.)
- Do not run a full benchmark or productionize until that comparison exists.

## Files (this folder)

`RESULTS.md`, `MANAGER_SUMMARY.md`, `segmentation_manifest.json`, `segment_predictions.json`, `comparison_metrics.json`, `motion_strip.txt`, `boundary_frames.jpg`, `segment_container_log_filtered.txt`, `determinism_probe_seg2.json` (+ `_container_log.txt`), `scripts/{segment_video,run_segments,merge_and_score}.py`. Generated mp4 clips are **not** here (scratchpad only).
