# Curify ASL — Manager Summary

**Date:** 2026-09-11 · **Branch:** `baobao/asl-temporal-ablation-2026-09-06` · **Main experiment commit:** `01cfd054faa67bd4980ea606e100bcfdf5f1b96e`
**Full detail:** `ASL_WORK_REPORT.md` (this folder). No Gemini call, no benchmark rerun, no external API call was made to produce either document.

## Goal

Reliable ASL video → accurate English text/captions, robust enough to ship as a Curify
captioning capability. Current work is benchmark, evaluation and diagnosis — not training a
new sign-language model.

## What I completed

### A — Uni-Sign inspector
- **Status: COMPLETE.**
- The per-clip diagnostic inspector now shows, for each of the 12 diagnostic clips:
  reference, Curify/Gemini frame baseline, Uni-Sign, and Gemini native-video predictions
  side by side with word-level diffs and WER/CER — read-only, no model is rerun.
- Matters because aggregate WER is ≈1.0 for every system and can no longer discriminate;
  this inspector is the only way we currently compare systems case by case.

### B — Gemini native-video
- Full benchmark harness built (Files API upload, one model call per clip, adapted
  production prompt, scoring, private-data safety guard, resumability).
- A real response-parsing bug (bare JSON array instead of the expected object) was found
  and fixed, then validated with a live retry.
- **5/12** diagnostic clips scored; **7/12** still blocked at the Gemini Files API before
  model inference — root cause (transient vs. clip-specific) unresolved.
- **0/5 genuine semantic recoveries** among the scored clips.
- The manager's 12-case decision gate (§7 P0-4) **remains inconclusive** — it needs all 12.

### C — SignCaption / Sign-Speak
- **Status: RESEARCH COMPLETE / ACCESS PENDING.**
- Product and prior outreach confirmed to exist; no reply was ever received.
- Vendor API credentials, endpoint/schema, auth, pricing, rate limits, benchmark-use
  permission, and written clearance on Sign-Speak's "competitive product" ToS clause are
  all still pending — none of this can be resolved from the repository.

### D — Trajectory tracking
- **D1 (tracking POC): 5/5 probe clips extracted successfully**, 1,038 total frames, 0%
  missing tracking on body/left hand/right hand, visually confirmed down to finger joints.
  **Trajectory extraction itself is technically feasible on this probe set.**
- **D2 (trajectory-as-context to Gemini): 0/5 semantic recoveries.** Appending
  trajectory-derived text to the existing frame-based prompt did not fix the semantic/topic
  failure on any of the 5 clips.
- **Do not read this as "trajectory is useless for ASL."** It rules out only one specific,
  cheap implementation (handing raw kinematics to a generic model as prompt text). A
  learned, sign-specific model trained to consume this signal directly is untested and
  remains a live direction.

## Main Finding

The experiments did not yet produce a translation-quality breakthrough. They did
meaningfully narrow the technical search space: increasing frame density, changing
sampling/batching, switching to native video (on the cases scored so far), and supplying
trajectory as textual context all failed to resolve the core semantic/topic mismatch —
fluent English describing the wrong subject.

Tracking itself worked well (0% missing tracking, 5/5 clips), so the stronger remaining
hypothesis is that the bottleneck needs a **learned, sign-specific temporal/linguistic
representation**, not more or better-formatted input patched into a generic Gemini prompt.
**This is a hypothesis supported by current experiments, not a proven conclusion** — the
true ASL-specific failure taxonomy (handshape vs. motion vs. fingerspelling vs. non-manual
markers) still requires an ASL-fluent human reviewer, which we do not yet have.

## Positive Outcomes

- A frozen, checksum-validated, reproducible 128-clip How2Sign v2 benchmark
- Uni-Sign added to the frame inspector for direct qualitative comparison
- A reusable native-video benchmark pipeline (dry-run default, resumable, provenance-tracked)
- A real parser bug discovered and fixed, validated end-to-end
- Trajectory extraction shown technically viable on 5/5 probe clips
- The simple trajectory-to-Gemini-prompt route tested and deprioritized (cheap, decisive result)
- A clearer separation between infrastructure blockers (Files API) and model-quality failures (semantic mismatch)

## Current Blockers

- 7 of 12 native-video diagnostic clips blocked by the Gemini Files API (root cause unresolved)
- SignCaption / Sign-Speak API access and permission unresolved (vendor-side)

## Recommended Next Steps

1. **Do not** spend more time on simple prompt/frame/trajectory-text tuning — five axes
   tested, none recovered meaning.
2. Finish the remaining 7 native-video cases **only if** the Files API becomes reliable.
3. Benchmark SignCaption / Sign-Speak **if** vendor access and ToS clearance are granted.
4. Investigate a learned, sign-specific temporal representation using handshape,
   hands/fingers, body, face and non-manual markers — the cheapest starting point is
   understanding why Uni-Sign, which already consumes pose data, still fails on this
   benchmark.

## Deliverables

- Full work report: `docs/daily_report/9.11/ASL_WORK_REPORT.md`
- Inspector: https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/asl-translator/evaluation/diagnostics/phase1_temporal_ablation/inspector/index.html
- Native-video status: https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/docs/daily_report/9.10/asl-native-video-evaluation/BLOCKER_STATUS.md
- Trajectory manager summary: https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/docs/daily_report/9.10/trajectory-tracking-feasibility/MANAGER_SUMMARY.md
- SignCaption checklist: https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/docs/daily_report/9.10/signcaption-signspeak-research/CHECKLIST.md

**Branch:** `baobao/asl-temporal-ablation-2026-09-06`
**Main experiment commit:** `01cfd054faa67bd4980ea606e100bcfdf5f1b96e`
No PR created.
