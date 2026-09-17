#!/usr/bin/env python3
"""Phase 3B design check — LOCAL ONLY, NO MODEL CALLS.

For the fixed 12 diagnostic clips, re-derives the exact baseline (Arm A)
adaptive/motion-weighted sampling (unmodified run_current_model functions,
config evaluation_2026_09_04_gemini_3_6 -- the same config baseline A's saved
predictions were produced with) and cross-checks it against what is recorded
in those saved predictions' own run_metadata (frame_budget, frames_sampled) --
this is how "baseline timestamps/frames are reused exactly" is verified,
since run_real() does not persist the timestamp array itself (only the
dry-run path does; this is documented, pre-existing behavior, not something
this task changes).

Then computes the Arm B (overlapping/sliding window) plan for those SAME
frames: window boundaries, per-window frame counts, the deterministic
frame-index "ownership" partition each window is responsible for (see
merge design in the module docstring below), and totals (window count,
expected model calls, repeated frame exposures) -- all before any Gemini call.

No import of google.genai. No network call.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c")
ASL_EVAL_DIR = REPO_ROOT / "asl-translator" / "asl-eval"
PHASE1_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "diagnostics" / "phase1_temporal_ablation"
DIAGNOSTIC_12_JSON = PHASE1_DIR / "diagnostic_12_clips.json"
MANIFEST_PATH = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2" / "manifest.csv"
BASELINE_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "curify_gemini_3_6_2026_09_04"
OUT_DIR = PHASE1_DIR / "controlled_ablation" / "independent_vs_sliding"
OUT_JSON = OUT_DIR / "design_check.json"

BASELINE_CONFIG = "evaluation_2026_09_04_gemini_3_6"
WINDOW_SIZE = 24
STRIDE = 12

sys.path.insert(0, str(ASL_EVAL_DIR))
import run_current_model as rcm  # noqa: E402


def build_windows(n_frames: int, window_size: int = WINDOW_SIZE, stride: int = STRIDE) -> list[tuple[int, int]]:
    """[(start_idx, end_idx), ...] half-open frame-index ranges, chronological,
    covering [0, n_frames) with window_size-length windows advancing by stride,
    the last window truncated/extended to end exactly at n_frames so the whole
    clip is covered with no gap. Reduces to a single [0, n_frames) window when
    n_frames <= window_size (identical to the one independent batch baseline
    would use for that clip)."""
    windows = []
    start = 0
    while True:
        end = min(start + window_size, n_frames)
        windows.append((start, end))
        if end >= n_frames:
            break
        start += stride
    return windows


def ownership_frame_ranges(windows: list[tuple[int, int]], n_frames: int) -> list[tuple[int, int]]:
    """Deterministic, reference-free, content-free partition of [0, n_frames)
    into one contiguous non-overlapping "owned" range per window, based ONLY
    on window position in the sequence (known before any inference runs):
      - window 0 owns starting at frame index 0
      - window i>0 owns starting at its own start index (= i*stride)
      - every window except the last owns up to (not including) the NEXT
        window's start index
      - the last window owns up to n_frames (absorbs any remainder)
    This exactly tiles [0, n_frames) with zero gaps and zero overlaps."""
    owned = []
    for i, (start, _end) in enumerate(windows):
        owned_start = 0 if i == 0 else start
        owned_end = n_frames if i == len(windows) - 1 else windows[i + 1][0]
        owned.append((owned_start, owned_end))
    return owned


def main() -> None:
    diag = json.loads(DIAGNOSTIC_12_JSON.read_text(encoding="utf-8"))
    clip_ids = [c["clip_id"] for c in diag["clips"]]
    assert len(clip_ids) == 12 and len(set(clip_ids)) == 12

    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        manifest = {r["how2sign_id"]: r for r in csv.DictReader(f)}

    per_clip = []
    total_windows = 0
    total_frame_exposures = 0
    total_unique_frames = 0
    multi_batch_clips = []

    for clip_id in clip_ids:
        row = manifest[clip_id]
        video_path = REPO_ROOT / row["local_video_path"]
        assert video_path.exists(), f"video missing for {clip_id}"

        base_pred_path = BASELINE_DIR / "predictions" / f"{clip_id}.json"
        assert base_pred_path.exists(), f"baseline prediction missing: {base_pred_path}"
        base_meta = json.loads(base_pred_path.read_text(encoding="utf-8"))["run_metadata"]
        assert base_meta["config"] == BASELINE_CONFIG

        # Re-derive the SAME sampler baseline A used, on the SAME video, with
        # the SAME config -- this is how "baseline timestamps are reused
        # exactly" is verified without a stored timestamp array (run_real()
        # does not persist one; pre-existing, documented behavior).
        times, motion = rcm.probe_motion(str(video_path))
        assert times, f"motion probe returned no frames for {clip_id}"
        duration = times[-1]
        runs = rcm.segment_runs(times, motion)
        frame_budget = rcm.resolve_frame_budget(BASELINE_CONFIG, duration)
        stamps = rcm.allocate_timestamps(runs, frame_budget)
        n_frames = len(stamps)

        assert frame_budget == base_meta["frame_budget"], (
            f"CONFOUND: recomputed frame_budget {frame_budget} != baseline's saved "
            f"{base_meta['frame_budget']} for {clip_id}")
        assert n_frames == base_meta["frames_sampled"], (
            f"CONFOUND: recomputed frame count {n_frames} != baseline's saved "
            f"{base_meta['frames_sampled']} for {clip_id}")

        windows = build_windows(n_frames, WINDOW_SIZE, STRIDE)
        owned = ownership_frame_ranges(windows, n_frames)
        n_baseline_batches = rcm.expected_batch_count(n_frames)
        is_multi_batch = n_baseline_batches > 1
        if is_multi_batch:
            multi_batch_clips.append(clip_id)

        exposures = sum(end - start for start, end in windows)
        total_windows += len(windows)
        total_frame_exposures += exposures
        total_unique_frames += n_frames

        per_clip.append({
            "clip_id": clip_id,
            "duration_s": round(duration, 3),
            "frame_budget": frame_budget,
            "n_frames_sampled": n_frames,
            "n_baseline_independent_batches": n_baseline_batches,
            "is_multi_batch": is_multi_batch,
            "n_sliding_windows": len(windows),
            "windows_frame_index_ranges": windows,
            "windows_owned_frame_index_ranges": owned,
            "windows_owned_time_ranges_s": [
                [
                    "-inf" if i == 0 else round(stamps[owned[i][0]], 3),
                    "+inf" if i == len(windows) - 1 else round(stamps[owned[i][1]], 3),
                ]
                for i in range(len(windows))
            ],
            "frame_exposures_with_overlap": exposures,
            "repeated_frame_exposures": exposures - n_frames,
            "same_as_baseline_batching_when_single_window": len(windows) == 1,
        })

    out = {
        "purpose": "Phase 3B design check (LOCAL ONLY, NO MODEL CALLS): re-verifies baseline "
                   "sampling is reproduced exactly, then computes the sliding-window plan "
                   "(window boundaries, ownership partition, call/frame estimates) before any "
                   "Gemini inference.",
        "baseline_config": BASELINE_CONFIG,
        "window_size": WINDOW_SIZE,
        "stride": STRIDE,
        "overlap_fraction": round(1 - STRIDE / WINDOW_SIZE, 3),
        "n_clips": 12,
        "n_multi_batch_clips": len(multi_batch_clips),
        "multi_batch_clips": multi_batch_clips,
        "n_single_batch_clips": 12 - len(multi_batch_clips),
        "total_expected_sliding_window_model_calls": total_windows,
        "total_baseline_independent_batch_calls_for_these_12": sum(c["n_baseline_independent_batches"] for c in per_clip),
        "total_unique_frames": total_unique_frames,
        "total_frame_exposures_with_overlap": total_frame_exposures,
        "total_repeated_frame_exposures": total_frame_exposures - total_unique_frames,
        "merge_strategy": {
            "name": "deterministic frame-index ownership partition, applied before any dedup",
            "what_each_window_sees": (
                "Window i sees frames[start_i:end_i) of the SAME global chronologically-ordered "
                "sampled-frame sequence baseline A used for this clip (identical frame images, "
                "identical [t=...s] timestamp labels, identical prompt/model/decoding settings). "
                "start_i = i*stride, end_i = min(start_i+window_size, n_frames)."
            ),
            "what_each_window_owns": (
                "A disjoint, gap-free slice of the clip's TIME axis, decided purely from window "
                "POSITION in the sequence (known before inference): window 0 owns from the "
                "start of the clip; window i>0 owns starting at its own first frame's timestamp; "
                "every window except the last owns up to (not including) the next window's first "
                "frame's timestamp; the last window owns to the end of the clip. This is computed "
                "entirely from the pre-planned window boundaries -- it never looks at what any "
                "window actually returned."
            ),
            "how_overlap_outputs_are_merged": (
                "For each window's returned segments, KEEP a segment iff its own reported `start` "
                "time falls inside that window's owned time range; DISCARD it otherwise (it will "
                "be covered by whichever window owns that time, if any window's kept segments "
                "cover it). Kept segments from all windows are then sorted by start time and, as a "
                "final pass IDENTICAL to what Arm A already does (dedup=True in the shared "
                "baseline config), run through the existing, unmodified "
                "run_current_model.merge_adjacent_duplicates() to collapse any remaining exact-text "
                "adjacent repeats (e.g. a window internally repeating a caption) -- this dedup pass "
                "runs on the ALREADY-DISJOINT-BY-CONSTRUCTION segment list, not on raw overlapping "
                "output, which is the blind-reuse failure mode the task flagged: dedup alone "
                "(exact-text match only) cannot safely resolve genuine content overlap between two "
                "windows describing the same moment in different words, so ownership partitioning "
                "-- not text matching -- is what removes the overlap."
            ),
            "why_it_cannot_look_at_ground_truth": (
                "The ownership partition is fixed entirely by window start/end frame indices, which "
                "are computed from window_size/stride/n_frames alone -- BEFORE any Gemini call is "
                "made and therefore before any model output (let alone the reference) exists to "
                "consult. The only per-segment decision (keep vs. discard) uses that segment's own "
                "`start` time, a field the model always reports as part of its normal output schema "
                "regardless of correctness -- never the reference SRT, and never a comparison "
                "between what two different windows said."
            ),
            "why_the_comparison_remains_fair": (
                "Arm A's predictions are untouched and unscored by anything in this design. Arm B's "
                "merge rule cannot see the reference, cannot see which window's wording is closer to "
                "the reference, and cannot selectively keep a 'better' overlapping segment over a "
                "'worse' one -- ownership is a fixed geometric partition decided in advance, so the "
                "final transcript reflects exactly one window's read of each moment, chosen only by "
                "position, not by correctness. This mirrors how a real deployed sliding-window "
                "pipeline would have to work (no reference available at inference time), so the WER "
                "measured here is not inflated relative to a real-world use of this architecture."
            ),
        },
        "confound_check_result": "No blocker identified: baseline frame_budget/frame_count "
                                  "reproduced exactly for all 12 clips (0 mismatches), merge rule is "
                                  "fully deterministic and reference-free, and the only architecture "
                                  "difference from Arm A is independent-vs-overlapping batch "
                                  "construction over the SAME frames.",
        "per_clip": per_clip,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"n_clips = 12, multi_batch = {len(multi_batch_clips)} {multi_batch_clips}")
    print(f"total sliding-window model calls (all 12 clips): {total_windows}")
    print(f"total baseline independent-batch calls (same 12): {out['total_baseline_independent_batch_calls_for_these_12']}")
    print(f"total unique frames: {total_unique_frames}   total frame exposures (with overlap): {total_frame_exposures}"
          f"   repeated exposures: {out['total_repeated_frame_exposures']}")
    for c in per_clip:
        print(f"  {c['clip_id']:38s} n_frames={c['n_frames_sampled']:3d} "
              f"baseline_batches={c['n_baseline_independent_batches']} sliding_windows={c['n_sliding_windows']} "
              f"multi_batch={c['is_multi_batch']}")


if __name__ == "__main__":
    main()
