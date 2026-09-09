#!/usr/bin/env python3
"""Phase 3A design check — LOCAL ONLY, NO MODEL CALLS.

For the fixed 12 diagnostic clips, computes and compares (a) the existing
adaptive/motion-weighted sampler's timestamps (reproduced locally via
run_current_model.probe_motion/segment_runs/allocate_timestamps, the same
unmodified functions used to produce the saved baseline predictions) against
(b) the new uniform sampler's timestamps
(run_current_model.allocate_timestamps_uniform), under the SAME duration-
scaled 2fps frame-budget policy (config evaluation_2026_09_07_gemini_3_6_uniform_2fps
resolves target_frames_per_sec identically to baseline A's 2.0).

Writes design_check.json with, per clip:
  - adaptive_timestamps, uniform_timestamps
  - frame_budget (from resolve_frame_budget, identical for both arms per clip)
  - adaptive_frame_count, uniform_frame_count (actual len(stamps) — these can
    differ from frame_budget for the adaptive arm; never for uniform, which by
    construction always returns exactly `budget` timestamps)
  - chronological-order checks for both
  - whether MIN_FRAME_BUDGET=24 is the binding constraint for this clip
    (i.e., duration*2.0 < 24, so both arms are sampling denser than "2fps"
    literally implies)
  - estimated Gemini calls for the uniform arm (batch_size=24)

This script imports ONLY run_current_model's dry-run path (probe_motion,
segment_runs, allocate_timestamps, allocate_timestamps_uniform,
resolve_frame_budget) — it never imports google.genai and makes no network
call.
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
OUT_DIR = PHASE1_DIR / "controlled_ablation" / "adaptive_vs_uniform_2fps"
OUT_JSON = OUT_DIR / "design_check.json"

BASELINE_CONFIG = "evaluation_2026_09_04_gemini_3_6"
UNIFORM_CONFIG = "evaluation_2026_09_07_gemini_3_6_uniform_2fps"

sys.path.insert(0, str(ASL_EVAL_DIR))
import run_current_model as rcm  # noqa: E402


def is_sorted_nondecreasing(xs: list[float]) -> bool:
    return all(xs[i] <= xs[i + 1] for i in range(len(xs) - 1))


def main() -> None:
    diag = json.loads(DIAGNOSTIC_12_JSON.read_text(encoding="utf-8"))
    clip_ids = [c["clip_id"] for c in diag["clips"]]
    assert len(clip_ids) == 12, f"expected 12 diagnostic clips, found {len(clip_ids)}"
    assert len(set(clip_ids)) == 12, "duplicate diagnostic clip ids"

    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        manifest = {r["how2sign_id"]: r for r in csv.DictReader(f)}

    per_clip = []
    total_uniform_calls = 0
    total_uniform_frames = 0
    min_budget_binding_clips = []
    frame_count_mismatches = []

    assert rcm.resolve_target_fps(BASELINE_CONFIG) == rcm.resolve_target_fps(UNIFORM_CONFIG), \
        "CONFOUND: baseline and uniform configs resolve to different target_frames_per_sec"
    assert rcm.CONFIGS[BASELINE_CONFIG]["model"] == rcm.CONFIGS[UNIFORM_CONFIG]["model"]
    assert rcm.CONFIGS[BASELINE_CONFIG]["thinking_level"] == rcm.CONFIGS[UNIFORM_CONFIG]["thinking_level"]
    assert rcm.CONFIGS[BASELINE_CONFIG]["dedup"] == rcm.CONFIGS[UNIFORM_CONFIG]["dedup"]
    assert rcm.CONFIGS[BASELINE_CONFIG]["budget_mode"] == rcm.CONFIGS[UNIFORM_CONFIG]["budget_mode"]
    assert rcm.BATCH_SIZE == 24  # unchanged module constant, both arms use it

    for clip_id in clip_ids:
        row = manifest[clip_id]
        video_path = REPO_ROOT / row["local_video_path"]
        assert video_path.exists(), f"video missing for {clip_id}: {video_path}"

        times, motion = rcm.probe_motion(str(video_path))
        assert times, f"motion probe returned no frames for {clip_id}"
        duration = times[-1]
        runs = rcm.segment_runs(times, motion)

        # Both configs share budget_mode="duration_scaled" and the same
        # (unset -> default 2.0) target_frames_per_sec, so this resolves
        # IDENTICALLY for both arms -- computed once, asserted equal below.
        budget_a = rcm.resolve_frame_budget(BASELINE_CONFIG, duration)
        budget_u = rcm.resolve_frame_budget(UNIFORM_CONFIG, duration)
        assert budget_a == budget_u, f"CONFOUND: frame_budget differs for {clip_id}: {budget_a} vs {budget_u}"
        frame_budget = budget_a

        adaptive_stamps = rcm.allocate_timestamps(runs, frame_budget)
        uniform_stamps = rcm.allocate_timestamps_uniform(times, frame_budget)

        naive_2fps_frame_count = round(duration * rcm.TARGET_FRAMES_PER_SEC)
        min_budget_binding = naive_2fps_frame_count < rcm.MIN_FRAME_BUDGET
        if min_budget_binding:
            min_budget_binding_clips.append(clip_id)

        if len(adaptive_stamps) != len(uniform_stamps):
            frame_count_mismatches.append({
                "clip_id": clip_id,
                "adaptive_frame_count": len(adaptive_stamps),
                "uniform_frame_count": len(uniform_stamps),
                "frame_budget": frame_budget,
            })

        adaptive_sorted = is_sorted_nondecreasing(adaptive_stamps)
        uniform_sorted = is_sorted_nondecreasing(uniform_stamps)
        assert uniform_sorted, f"uniform timestamps not chronological for {clip_id}"
        assert adaptive_sorted, f"adaptive timestamps not chronological for {clip_id} (pre-existing sampler!)"

        expected_calls = rcm.expected_batch_count(len(uniform_stamps))
        total_uniform_calls += expected_calls
        total_uniform_frames += len(uniform_stamps)

        per_clip.append({
            "clip_id": clip_id,
            "duration_s": round(duration, 3),
            "frame_budget": frame_budget,
            "naive_literal_2fps_frame_count": naive_2fps_frame_count,
            "min_frame_budget_binding": min_budget_binding,
            "active_run_count": sum(1 for r in runs if r.active),
            "idle_run_count": sum(1 for r in runs if not r.active),
            "adaptive_frame_count": len(adaptive_stamps),
            "uniform_frame_count": len(uniform_stamps),
            "frame_count_matched": len(adaptive_stamps) == len(uniform_stamps),
            "adaptive_chronological": adaptive_sorted,
            "uniform_chronological": uniform_sorted,
            "adaptive_expected_model_calls": rcm.expected_batch_count(len(adaptive_stamps)),
            "uniform_expected_model_calls": expected_calls,
            "adaptive_timestamps_s": [round(t, 3) for t in adaptive_stamps],
            "uniform_timestamps_s": [round(t, 3) for t in uniform_stamps],
        })

    out = {
        "purpose": "Phase 3A design check (LOCAL ONLY, NO MODEL CALLS) comparing adaptive vs. "
                   "uniform sampler timestamps for the 12 fixed diagnostic clips before any "
                   "Gemini inference is run.",
        "baseline_config": BASELINE_CONFIG,
        "uniform_config": UNIFORM_CONFIG,
        "target_frames_per_sec_both_arms": rcm.resolve_target_fps(BASELINE_CONFIG),
        "batch_size_both_arms": rcm.BATCH_SIZE,
        "min_frame_budget": rcm.MIN_FRAME_BUDGET,
        "n_clips": len(clip_ids),
        "n_clips_with_frame_count_mismatch": len(frame_count_mismatches),
        "frame_count_mismatches": frame_count_mismatches,
        "n_clips_where_min_frame_budget_is_binding": len(min_budget_binding_clips),
        "clips_where_min_frame_budget_is_binding": min_budget_binding_clips,
        "estimate_new_gemini_calls_uniform_arm_only": total_uniform_calls,
        "estimate_total_frames_uniform_arm_only": total_uniform_frames,
        "note_on_estimate": "Baseline A predictions are REUSED, not rerun -- these are the ONLY new "
                            "Gemini calls this experiment will make.",
        "per_clip": per_clip,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"n_clips = {out['n_clips']}")
    print(f"frame_count mismatches (adaptive actual frames != uniform actual frames): "
          f"{out['n_clips_with_frame_count_mismatch']}")
    for m in frame_count_mismatches:
        print(f"  {m}")
    print(f"MIN_FRAME_BUDGET=24 binding (literal 2fps would be < 24 frames) on "
          f"{out['n_clips_where_min_frame_budget_is_binding']} clip(s): "
          f"{out['clips_where_min_frame_budget_is_binding']}")
    print(f"estimated NEW Gemini calls (uniform arm only): {total_uniform_calls}")
    print(f"estimated total frames (uniform arm only): {total_uniform_frames}")


if __name__ == "__main__":
    main()
