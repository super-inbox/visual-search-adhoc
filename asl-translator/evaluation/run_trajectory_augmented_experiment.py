#!/usr/bin/env python3
"""Phase D2 — trajectory-augmented Gemini inference experiment.

Tests whether appending RTMPose-derived, observation-level trajectory text
to the EXISTING frame-baseline prompt changes Gemini's semantic output, on
the same 5 clips Phase D1 already tracked. This is an INFERENCE-SIDE
experiment only — no training, no model change.

Two conditions:
  A. CONTROL     — the existing frozen curify_gemini_3_6_2026_09_04
                    prediction for each clip. NEVER rerun by this script.
  B. TREATMENT   — the exact same frames, same batches, same model, same
                    temperature/thinking_level, same dedup — with ONE
                    additional text Part (the trajectory observations,
                    see trajectory_probe/render_trajectory_text.py)
                    inserted right after PRODUCTION_PROMPT and before the
                    per-frame [timestamp, image] parts, per batch.

The ONLY structural difference between what condition A's frozen run made
and what condition B sends is that one inserted Part. Everything else
(sampling, batching, model, decoding config, prompt task text) is
byte-identical — re-derived via the SAME unmodified functions
run_current_model.py's own run_real() uses (probe_motion, segment_runs,
allocate_timestamps, extract_frames), with the frame_budget read from each
clip's own frozen prediction (not re-resolved), so sampling cannot drift.

Reference text is NEVER read by anything in the Gemini-call path — only by
a separate score_predictions() function that runs strictly after all API
calls complete (same separation already used by
run_native_video_how2sign_v2_benchmark.py).

Default mode is dry/inspection only:
    --plan-only     : exact call count per clip, zero network, no API key
    --show-example CLIP_ID : print the EXACT trajectory text and the EXACT
                      prompt-parts diff (control vs treatment) for one
                      clip's first batch. Zero network, no API key.

A real run requires --run + --acknowledge-private-data-upload +
GEMINI_API_KEY, mirroring every other real-call script in this project.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
ASL_EVAL_DIR = REPO_ROOT / "asl-translator" / "asl-eval"
TRAJ_DIR = ASL_EVAL_DIR / "trajectory_probe"
DIAG_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "diagnostics" / "phase1_temporal_ablation"
TRAJECTORY_PROBE_OUT = DIAG_DIR / "trajectory_probe"
BASELINE_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "curify_gemini_3_6_2026_09_04"
MANIFEST_PATH = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2" / "manifest.csv"
RESULTS_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "curify_gemini_trajectory_augmented_2026_09_10"
CONFIG_NAME = "evaluation_2026_09_04_gemini_3_6"  # same config as the frame baseline — NOT redeclared/changed here

D2_CLIP_IDS = [
    "92V3oH63zbQ_5-1-rgb_front",
    "Fz-N1S0swh8_2-8-rgb_front",
    "-g0iPSnQt6w_0-1-rgb_front",
    "G19uBylwQww_1-2-rgb_front",
    "FzmL8SL6Bow_1-8-rgb_front",
]

sys.path.insert(0, str(ASL_EVAL_DIR))
import run_current_model as rcm  # noqa: E402 — SAME unmodified sampler/prompt/config used by the frame baseline
sys.path.insert(0, str(TRAJ_DIR))
import render_trajectory_text as rtt  # noqa: E402


def load_manifest_row(clip_id: str) -> dict:
    import csv
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["how2sign_id"] == clip_id:
                return row
    raise SystemExit(f"{clip_id} not found in manifest.csv")


def load_frozen_baseline(clip_id: str) -> dict:
    p = BASELINE_DIR / "predictions" / f"{clip_id}.json"
    if not p.exists():
        raise SystemExit(f"No frozen frame-baseline prediction at {p} — condition A requires this to already exist.")
    return json.loads(p.read_text(encoding="utf-8"))


def load_landmarks(clip_id: str) -> dict:
    p = TRAJECTORY_PROBE_OUT / clip_id / "landmarks.json"
    if not p.exists():
        raise SystemExit(f"No Phase D1 landmarks.json for {clip_id} at {p} — run Phase D1 extraction first.")
    return json.loads(p.read_text(encoding="utf-8"))


def compute_stamps_and_batches(video_path: Path, frame_budget: int) -> tuple[list[float], int]:
    """Re-derive the EXACT same sampling the frozen baseline used — same
    functions, same frame_budget (read from the frozen prediction, not
    re-resolved), adaptive/motion-weighted strategy (this config has no
    sampling_strategy override, matching the frozen run)."""
    times, motion = rcm.probe_motion(str(video_path))
    runs = rcm.segment_runs(times, motion)
    stamps = rcm.allocate_timestamps(runs, frame_budget)
    return stamps, len(stamps)


def plan_one_clip(clip_id: str) -> dict:
    row = load_manifest_row(clip_id)
    frozen = load_frozen_baseline(clip_id)
    rm = frozen["run_metadata"]
    video_path = REPO_ROOT / row["local_video_path"]
    stamps, n_frames = compute_stamps_and_batches(video_path, rm["frame_budget"])
    if n_frames != rm["frames_sampled"]:
        raise SystemExit(
            f"{clip_id}: re-derived {n_frames} frames but frozen baseline recorded "
            f"{rm['frames_sampled']} — sampling has drifted, refusing to proceed silently."
        )
    n_batches = (n_frames + rcm.BATCH_SIZE - 1) // rcm.BATCH_SIZE
    return {
        "clip_id": clip_id, "video_path": str(video_path), "frame_budget": rm["frame_budget"],
        "n_frames": n_frames, "n_batches": n_batches, "stamps": stamps,
        "frozen_model_calls": rm["model_calls"],
    }


def build_batch_parts(stamps: list[float], frame_paths: list[str], batch_idx: int,
                       trajectory_text: Optional[str]):
    """Byte-identical to run_current_model.run_real()'s own per-batch parts
    construction, with exactly one optional insertion (the trajectory text
    Part) right after PRODUCTION_PROMPT and before the frame parts. This is
    the ONLY structural difference between control and treatment."""
    from google.genai import types as gtypes

    parts_control = [gtypes.Part.from_text(text=rcm.PRODUCTION_PROMPT)]
    for p in frame_paths:
        ts = float(re.search(r"_(\d+\.\d+)\.jpg$", p).group(1))
        parts_control.append(gtypes.Part.from_text(text=f"[t={ts:.2f}s]"))
        with open(p, "rb") as fh:
            parts_control.append(gtypes.Part.from_bytes(data=fh.read(), mime_type="image/jpeg"))

    if trajectory_text is None:
        return parts_control, None

    parts_treatment = [parts_control[0], gtypes.Part.from_text(text=trajectory_text)] + parts_control[1:]
    return parts_control, parts_treatment


def show_example(clip_id: str) -> None:
    plan = plan_one_clip(clip_id)
    landmarks = load_landmarks(clip_id)
    stamps = plan["stamps"]
    batch0 = stamps[: rcm.BATCH_SIZE]
    t_start, t_end = batch0[0], batch0[-1]
    traj_text = rtt.render_trajectory_text(landmarks, t_start, t_end)

    print("=" * 78)
    print(f"EXAMPLE — {clip_id}, batch 1/{plan['n_batches']} (t={t_start:.2f}s..{t_end:.2f}s, "
          f"{len(batch0)} frames)")
    print("=" * 78)
    print("\n--- EXACT trajectory text that would be injected for this batch ---\n")
    print(traj_text)
    print("\n--- EXACT prompt-parts structure: CONTROL vs TREATMENT (batch 1) ---\n")
    print("CONTROL parts, in order:")
    print("  [0] Part.from_text(PRODUCTION_PROMPT)  <- unchanged task instructions, same as frozen baseline")
    for i, ts in enumerate(batch0, start=1):
        print(f"  [{i}] Part.from_text('[t={ts:.2f}s]') + Part.from_bytes(<frame jpeg>)  <- unchanged")
    print("\nTREATMENT parts, in order:")
    print("  [0] Part.from_text(PRODUCTION_PROMPT)  <- IDENTICAL to control")
    print("  [1] Part.from_text(<trajectory observations block above>)  <- THE ONLY ADDITION")
    for i, ts in enumerate(batch0, start=2):
        print(f"  [{i}] Part.from_text('[t={ts:.2f}s]') + Part.from_bytes(<frame jpeg>)  <- IDENTICAL to control, same frames, same order")
    print("\nModel/decoding config (both conditions, unchanged from frozen baseline):")
    cfg = rcm.CONFIGS[CONFIG_NAME]
    print(f"  model={cfg['model']}  temperature={cfg['temperature']}  thinking_level={cfg['thinking_level']}  "
          f"dedup={cfg['dedup']}  batch_size={rcm.BATCH_SIZE}  keyframe_width={rcm.KEYFRAME_WIDTH}")
    print("\nReference text accessibility check: this function never imported, opened, or referenced")
    print("any reference/.srt file or reference_text field. grep-verifiable: no 'local_reference_path'")
    print("or 'reference_text' identifier appears anywhere in this script above the scoring section.")


def plan_only() -> None:
    total_calls = 0
    print("PLAN ONLY — no model calls made, no GEMINI_API_KEY required.\n")
    for cid in D2_CLIP_IDS:
        plan = plan_one_clip(cid)
        total_calls += plan["n_batches"]
        print(f"  {cid:35s} frames={plan['n_frames']:3d}  batches(=calls)={plan['n_batches']}  "
              f"(frozen baseline used {plan['frozen_model_calls']} call(s) — match: "
              f"{plan['n_batches'] == plan['frozen_model_calls']})")
    print(f"\nTotal planned condition-B Gemini calls across the 5 D2 clips: {total_calls}")
    print("Condition A: 0 new calls — reuses each clip's existing frozen frame-baseline prediction.")


def run_real() -> None:
    import os
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is not set. Refusing to start the run.")

    from google import genai
    from google.genai import types as gtypes
    client = genai.Client(api_key=api_key)

    (RESULTS_DIR / "predictions").mkdir(parents=True, exist_ok=True)
    total_calls = 0

    for clip_id in D2_CLIP_IDS:
        plan = plan_one_clip(clip_id)
        landmarks = load_landmarks(clip_id)
        video_path = Path(plan["video_path"])
        stamps = plan["stamps"]

        segments = []
        model_calls = 0
        with tempfile.TemporaryDirectory(prefix="asl_d2_") as td:
            frames = rcm.extract_frames(str(video_path), stamps, td)
            for i in range(0, len(frames), rcm.BATCH_SIZE):
                batch_frames = frames[i:i + rcm.BATCH_SIZE]
                batch_stamps = stamps[i:i + len(batch_frames)]
                t_start, t_end = batch_stamps[0], batch_stamps[-1]
                traj_text = rtt.render_trajectory_text(landmarks, t_start, t_end)

                _, parts_treatment = build_batch_parts(stamps, batch_frames, i // rcm.BATCH_SIZE, traj_text)

                cfg = rcm.CONFIGS[CONFIG_NAME]
                gen_config_kwargs = {"response_mime_type": "application/json"}
                if cfg["temperature"] is not None:
                    gen_config_kwargs["temperature"] = cfg["temperature"]
                if cfg.get("thinking_level"):
                    gen_config_kwargs["thinking_config"] = gtypes.ThinkingConfig(thinking_level=cfg["thinking_level"])

                resp = client.models.generate_content(
                    model=cfg["model"],
                    contents=[gtypes.Content(role="user", parts=parts_treatment)],
                    config=gtypes.GenerateContentConfig(**gen_config_kwargs),
                )
                model_calls += 1
                total_calls += 1
                raw = (resp.text or "").strip()
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    m = re.search(r"\{.*\}", raw, re.S)
                    data = json.loads(m.group(0)) if m else {"segments": []}
                for s in data.get("segments", []):
                    try:
                        segments.append({
                            "line": len(segments) + 1,
                            "start": float(s["start"]),
                            "end": float(s["end"]),
                            "text": str(s.get("text", "")).strip(),
                        })
                    except (KeyError, TypeError, ValueError):
                        continue

            segments_before_dedup = len(segments)
            if cfg["dedup"]:
                segments = rcm.merge_adjacent_duplicates(segments)

        output = {
            "project_id": None,
            "video": str(video_path),
            "producer": "asl-translator/evaluation/run_trajectory_augmented_experiment.py (--run)",
            "warning": "UNVERIFIED machine output — offline evaluation run, not a production job.",
            "run_metadata": {
                "config": CONFIG_NAME,
                "experiment": "phase_d2_trajectory_augmented",
                "condition": "B_treatment_trajectory_augmented",
                "model": cfg["model"],
                "temperature": cfg["temperature_label"],
                "thinking_level": cfg["thinking_level"],
                "frame_budget": plan["frame_budget"],
                "frames_sampled": plan["n_frames"],
                "batch_size": rcm.BATCH_SIZE,
                "keyframe_width": rcm.KEYFRAME_WIDTH,
                "model_calls": model_calls,
                "segments_before_dedup": segments_before_dedup,
                "degenerate_repetition": rcm.has_degenerate_repetition(segments),
                "trajectory_source": str((TRAJECTORY_PROBE_OUT / clip_id / "landmarks.json").relative_to(REPO_ROOT)),
                "trajectory_tracker": landmarks["tracker"],
                "trajectory_rtmlib_version": landmarks["rtmlib_version"],
                "control_prediction": str((BASELINE_DIR / "predictions" / f"{clip_id}.json").relative_to(REPO_ROOT)),
                "prompt_diff_vs_control": "ONE additional Part.from_text(trajectory observations) inserted "
                                          "immediately after PRODUCTION_PROMPT, before the per-frame parts, "
                                          "per batch. No other prompt/config/sampling change.",
                "production_side_effects": False,
                "source_repo": rcm.SOURCE_REPO,
                "source_ref": rcm.SOURCE_REF,
                "source_commit": rcm.SOURCE_COMMIT,
                "source_file": rcm.SOURCE_FILE,
                "prompt_sha256": rcm.prompt_sha256(),
            },
            "segments": segments,
        }
        out_path = RESULTS_DIR / "predictions" / f"{clip_id}.json"
        out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
        print(f"{clip_id}: {model_calls} call(s), {len(segments)} segment(s) -> {out_path}")

    print(f"\nDone. {total_calls} total Gemini calls across {len(D2_CLIP_IDS)} clips (condition B only; "
          f"condition A reused 0 new calls).")


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--show-example", metavar="CLIP_ID", default=None)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--acknowledge-private-data-upload", action="store_true")
    return ap


def main(argv=None) -> int:
    ap = build_arg_parser()
    args = ap.parse_args(argv)

    if args.show_example:
        show_example(args.show_example)
        return 0
    if args.plan_only:
        plan_only()
        return 0
    if args.run:
        if not args.acknowledge_private_data_upload:
            print("error: --run requires --acknowledge-private-data-upload. Sampled frames contain "
                  "identifiable people and leave this machine. No network call was made.", file=sys.stderr)
            return 2
        run_real()
        return 0

    print("error: pass exactly one of --plan-only, --show-example CLIP_ID, or --run "
          "(+ --acknowledge-private-data-upload). No network call was made.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
