#!/usr/bin/env python3
"""Phase 3B — overlapping/sliding-window arm, 12 fixed diagnostic clips ONLY.

Makes REAL Gemini calls. Uses the EXACT SAME sampled frames/timestamps as
baseline A for each clip (re-derived via the unmodified run_current_model
probe_motion/segment_runs/allocate_timestamps, config
evaluation_2026_09_04_gemini_3_6 -- verified against baseline A's own saved
frame_budget/frames_sampled in design_check_sliding.py before this script is
ever run). No resampling. Same model/prompt/decoding/image-encoding as
baseline A (read from run_current_model.CONFIGS[BASELINE_CONFIG] directly, not
duplicated by value).

The ONLY architectural change from baseline A: frames are grouped into
overlapping windows (window_size=24, stride=12) instead of independent
non-overlapping batches, and overlapping window outputs are merged via a
deterministic, reference-free frame-index ownership partition (see
design_check_sliding.py's "merge_strategy" block for the full rationale) --
never via merge_adjacent_duplicates() applied naively to raw overlapping
output, and never by comparing against the ground-truth reference.

run_current_model.py itself is NOT imported for its run_real()/CONFIGS
mutation -- it is used strictly read-only (probe_motion, segment_runs,
allocate_timestamps, extract_frames, PRODUCTION_PROMPT, prompt_sha256,
input_md5, merge_adjacent_duplicates, has_degenerate_repetition,
CONFIGS[BASELINE_CONFIG]). Nothing in that module is modified, monkeypatched,
or extended by this script.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path("/Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c")
ASL_EVAL_DIR = REPO_ROOT / "asl-translator" / "asl-eval"
PHASE1_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "diagnostics" / "phase1_temporal_ablation"
DIAGNOSTIC_12_JSON = PHASE1_DIR / "diagnostic_12_clips.json"
MANIFEST_PATH = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2" / "manifest.csv"
BASELINE_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "curify_gemini_3_6_2026_09_04"
OUT_DIR = PHASE1_DIR / "controlled_ablation" / "independent_vs_sliding"
PRED_DIR = OUT_DIR / "predictions"

BASELINE_CONFIG = "evaluation_2026_09_04_gemini_3_6"
WINDOW_SIZE = 24
STRIDE = 12
ARM_LABEL = "phase3b_independent_vs_sliding_window24_stride12_2026_09_07"

sys.path.insert(0, str(ASL_EVAL_DIR))
import run_current_model as rcm  # noqa: E402  READ-ONLY reuse; not modified


def build_windows(n_frames: int) -> list[tuple[int, int]]:
    windows = []
    start = 0
    while True:
        end = min(start + WINDOW_SIZE, n_frames)
        windows.append((start, end))
        if end >= n_frames:
            break
        start += STRIDE
    return windows


def ownership_frame_ranges(windows: list[tuple[int, int]], n_frames: int) -> list[tuple[int, int]]:
    owned = []
    for i, (start, _end) in enumerate(windows):
        owned_start = 0 if i == 0 else start
        owned_end = n_frames if i == len(windows) - 1 else windows[i + 1][0]
        owned.append((owned_start, owned_end))
    return owned


def call_gemini_on_frames(client, gtypes, frame_paths: list[str], cfg: dict):
    parts = [gtypes.Part.from_text(text=rcm.PRODUCTION_PROMPT)]
    for p in frame_paths:
        ts = float(re.search(r"_(\d+\.\d+)\.jpg$", p).group(1))
        parts.append(gtypes.Part.from_text(text=f"[t={ts:.2f}s]"))
        with open(p, "rb") as fh:
            parts.append(gtypes.Part.from_bytes(data=fh.read(), mime_type="image/jpeg"))

    gen_config_kwargs = {"response_mime_type": "application/json"}
    if cfg["temperature"] is not None:
        gen_config_kwargs["temperature"] = cfg["temperature"]
    if cfg.get("thinking_level"):
        gen_config_kwargs["thinking_config"] = gtypes.ThinkingConfig(thinking_level=cfg["thinking_level"])

    resp = client.models.generate_content(
        model=cfg["model"],
        contents=[gtypes.Content(role="user", parts=parts)],
        config=gtypes.GenerateContentConfig(**gen_config_kwargs),
    )
    raw = (resp.text or "").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.S)
        data = json.loads(m.group(0)) if m else {"segments": []}
    segs = []
    for s in data.get("segments", []):
        try:
            segs.append({"start": float(s["start"]), "end": float(s["end"]), "text": str(s.get("text", "")).strip()})
        except (KeyError, TypeError, ValueError):
            continue
    return segs


def run_one_clip(clip_id: str, video_path: Path, api_key: str) -> dict:
    from google import genai
    from google.genai import types as gtypes

    cfg = rcm.CONFIGS[BASELINE_CONFIG]
    client = genai.Client(api_key=api_key)

    times, motion = rcm.probe_motion(str(video_path))
    duration = times[-1]
    runs = rcm.segment_runs(times, motion)
    frame_budget = rcm.resolve_frame_budget(BASELINE_CONFIG, duration)
    stamps = rcm.allocate_timestamps(runs, frame_budget)
    n_frames = len(stamps)

    windows = build_windows(n_frames)
    owned = ownership_frame_ranges(windows, n_frames)
    owned_time = [
        (float("-inf") if i == 0 else stamps[owned[i][0]],
         float("inf") if i == len(windows) - 1 else stamps[owned[i][1]])
        for i in range(len(windows))
    ]

    all_kept_segments = []
    window_reports = []
    model_calls = 0
    with tempfile.TemporaryDirectory(prefix="asl_phase3b_sliding_") as td:
        frame_paths = rcm.extract_frames(str(video_path), stamps, td)
        assert len(frame_paths) == n_frames, f"{clip_id}: extracted {len(frame_paths)} frames, expected {n_frames}"

        for i, (w_start, w_end) in enumerate(windows):
            batch = frame_paths[w_start:w_end]
            raw_segs = call_gemini_on_frames(client, gtypes, batch, cfg)
            model_calls += 1
            lo, hi = owned_time[i]
            kept = [s for s in raw_segs if lo <= s["start"] < hi]
            discarded = [s for s in raw_segs if not (lo <= s["start"] < hi)]
            all_kept_segments.extend(kept)
            window_reports.append({
                "window_index": i,
                "frame_index_range": [w_start, w_end],
                "owned_frame_index_range": list(owned[i]),
                "owned_time_range_s": [str(lo) if lo == float("-inf") else round(lo, 3),
                                        str(hi) if hi == float("inf") else round(hi, 3)],
                "raw_segments_returned": len(raw_segs),
                "segments_kept_by_ownership": len(kept),
                "segments_discarded_by_ownership": len(discarded),
            })

    all_kept_segments.sort(key=lambda s: s["start"])
    for i, s in enumerate(all_kept_segments):
        s["line"] = i + 1
    segments_before_dedup = len(all_kept_segments)
    if cfg["dedup"]:
        final_segments = rcm.merge_adjacent_duplicates(all_kept_segments)
    else:
        final_segments = all_kept_segments

    density = round(n_frames / duration, 3) if duration > 0 else 0.0
    output = {
        "project_id": None,
        "video": str(video_path),
        "producer": "asl-translator/evaluation/diagnostics/phase1_temporal_ablation/controlled_ablation/run_sliding_arm.py",
        "warning": "UNVERIFIED machine output — offline Phase 3B ablation run, not a production job. "
                   "NOT the evaluation_2026_09_04_gemini_3_6 baseline (Arm A) — same sampled frames, "
                   "different (overlapping) batch/window construction.",
        "run_metadata": {
            "config": ARM_LABEL,
            "not_baseline_config": BASELINE_CONFIG,
            "model": cfg["model"],
            "temperature": cfg["temperature_label"],
            "thinking_level": cfg.get("thinking_level"),
            "frame_budget": frame_budget,
            "budget_mode": cfg["budget_mode"],
            "sampling_density_fps": density,
            "sampling_strategy": "adaptive (identical to baseline A -- reused frames, not resampled)",
            "dedup": cfg["dedup"],
            "segments_before_dedup": segments_before_dedup,
            "degenerate_repetition": rcm.has_degenerate_repetition(final_segments),
            "keyframe_width": rcm.KEYFRAME_WIDTH,
            "duration_s": round(duration, 3),
            "frames_sampled": n_frames,
            "model_calls": model_calls,
            "batching_strategy": "overlapping_sliding_window",
            "window_size": WINDOW_SIZE,
            "stride": STRIDE,
            "n_windows": len(windows),
            "merge_strategy": "deterministic_frame_index_ownership_partition_then_exact_text_dedup",
            "window_reports": window_reports,
            "production_side_effects": False,
            "source_repo": rcm.SOURCE_REPO,
            "source_ref": rcm.SOURCE_REF,
            "source_commit": rcm.SOURCE_COMMIT,
            "source_file": rcm.SOURCE_FILE,
            "prompt_sha256": rcm.prompt_sha256(),
            "input_md5": rcm.input_md5(video_path),
            "not_production_2026_08_29": True,
        },
        "segments": final_segments,
    }
    pred_path = PRED_DIR / f"{clip_id}.json"
    pred_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return {"clip_id": clip_id, "model_calls": model_calls, "n_windows": len(windows),
            "segments_before_dedup": segments_before_dedup, "segments_after_dedup": len(final_segments),
            "pred_path": str(pred_path)}


def existing_matches(pred_path: Path) -> bool:
    if not pred_path.exists():
        return False
    try:
        data = json.loads(pred_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return data.get("run_metadata", {}).get("config") == ARM_LABEL and isinstance(data.get("segments"), list)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--clip-ids", default=None, help="Comma-separated subset of the 12 diagnostic clip IDs.")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    diag = json.loads(DIAGNOSTIC_12_JSON.read_text(encoding="utf-8"))
    clip_ids = [c["clip_id"] for c in diag["clips"]]
    assert len(clip_ids) == 12 and len(set(clip_ids)) == 12
    if args.clip_ids:
        wanted = set(args.clip_ids.split(","))
        missing = wanted - set(clip_ids)
        if missing:
            raise SystemExit(f"not in the 12 diagnostic clips: {sorted(missing)}")
        clip_ids = [c for c in clip_ids if c in wanted]

    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        manifest = {r["how2sign_id"]: r for r in csv.DictReader(f)}

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("error: GEMINI_API_KEY not set.", file=sys.stderr)
        return 2

    PRED_DIR.mkdir(parents=True, exist_ok=True)
    n_ok, n_fail, n_skip = 0, 0, 0
    for i, clip_id in enumerate(clip_ids, 1):
        pred_path = PRED_DIR / f"{clip_id}.json"
        print(f"[{i}/{len(clip_ids)}] {clip_id}")
        if not args.overwrite and existing_matches(pred_path):
            print(f"  SKIP (already completed for {ARM_LABEL})")
            n_skip += 1
            continue
        video_path = REPO_ROOT / manifest[clip_id]["local_video_path"]
        t0 = time.monotonic()
        try:
            rec = run_one_clip(clip_id, video_path, api_key)
            n_ok += 1
            print(f"  OK windows={rec['n_windows']} calls={rec['model_calls']} "
                  f"segs_before_dedup={rec['segments_before_dedup']} segs_after={rec['segments_after_dedup']} "
                  f"({time.monotonic()-t0:.1f}s)")
        except Exception as e:  # noqa: BLE001
            n_fail += 1
            print(f"  FAILED: {type(e).__name__}: {str(e)[:400]}")

    print(f"\nDone. ok={n_ok} failed={n_fail} skipped={n_skip} out of {len(clip_ids)} requested.")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
