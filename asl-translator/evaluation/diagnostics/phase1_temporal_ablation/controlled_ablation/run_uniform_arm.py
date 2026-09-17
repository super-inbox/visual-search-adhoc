#!/usr/bin/env python3
"""Phase 3A controlled sampling-strategy ablation — uniform arm, 12 fixed
diagnostic clips ONLY.

This script makes REAL Gemini calls (config
evaluation_2026_09_07_gemini_3_6_uniform_2fps) for the UNIFORM arm only. It
NEVER calls Gemini for the adaptive/baseline arm — those predictions already
exist on disk (curify_gemini_3_6_2026_09_04/predictions/) and are read
read-only by score_and_report.py.

It is a thin wrapper around run_current_model.run_real() (imported, not
duplicated) restricted to the 12 diagnostic clip IDs in diagnostic_12_clips.json,
following the same resume/skip-if-already-done pattern as
asl-translator/evaluation/run_curify_how2sign_v2_benchmark.py.

Usage:
    # zero network calls, just prints the plan (delegates to design_check.py's numbers)
    python3 run_uniform_arm.py --plan-only

    # smoke test: exactly 1 clip (the shortest, 1 Gemini call)
    python3 run_uniform_arm.py --clip-ids 92V3oH63zbQ_5-1-rgb_front

    # all 12 (skips any clip already completed under this config)
    python3 run_uniform_arm.py
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path("/Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c")
ASL_EVAL_DIR = REPO_ROOT / "asl-translator" / "asl-eval"
PHASE1_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "diagnostics" / "phase1_temporal_ablation"
DIAGNOSTIC_12_JSON = PHASE1_DIR / "diagnostic_12_clips.json"
MANIFEST_PATH = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2" / "manifest.csv"
OUT_DIR = PHASE1_DIR / "controlled_ablation" / "adaptive_vs_uniform_2fps"
PRED_DIR = OUT_DIR / "predictions"

UNIFORM_CONFIG = "evaluation_2026_09_07_gemini_3_6_uniform_2fps"

sys.path.insert(0, str(ASL_EVAL_DIR))
import run_current_model as rcm  # noqa: E402


def load_diagnostic_rows() -> list[dict]:
    diag = json.loads(DIAGNOSTIC_12_JSON.read_text(encoding="utf-8"))
    clip_ids = [c["clip_id"] for c in diag["clips"]]
    assert len(clip_ids) == 12 and len(set(clip_ids)) == 12
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        manifest = {r["how2sign_id"]: r for r in csv.DictReader(f)}
    return [{"clip_id": cid, "video_path": REPO_ROOT / manifest[cid]["local_video_path"],
             "reference_path": REPO_ROOT / manifest[cid]["local_reference_path"]}
            for cid in clip_ids]


def existing_prediction_matches_config(pred_path: Path, config_name: str) -> bool:
    if not pred_path.exists():
        return False
    try:
        data = json.loads(pred_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return data.get("run_metadata", {}).get("config") == config_name and isinstance(data.get("segments"), list)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--clip-ids", default=None, help="Comma-separated subset of the 12 diagnostic clip IDs.")
    ap.add_argument("--overwrite", action="store_true", help="Re-run even if a matching prediction exists.")
    args = ap.parse_args()

    rows = load_diagnostic_rows()
    if args.clip_ids:
        wanted = set(args.clip_ids.split(","))
        missing = wanted - {r["clip_id"] for r in rows}
        if missing:
            raise SystemExit(f"not in the 12 diagnostic clips: {sorted(missing)}")
        rows = [r for r in rows if r["clip_id"] in wanted]

    import os
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("error: GEMINI_API_KEY not set. Refusing to start.", file=sys.stderr)
        return 2

    PRED_DIR.mkdir(parents=True, exist_ok=True)
    n_ok, n_fail, n_skip = 0, 0, 0
    for i, row in enumerate(rows, 1):
        clip_id = row["clip_id"]
        pred_path = PRED_DIR / f"{clip_id}.json"
        print(f"[{i}/{len(rows)}] {clip_id}")
        if not args.overwrite and existing_prediction_matches_config(pred_path, UNIFORM_CONFIG):
            print(f"  SKIP (already completed for {UNIFORM_CONFIG})")
            n_skip += 1
            continue
        t0 = time.monotonic()
        try:
            rcm.run_real(row["video_path"], UNIFORM_CONFIG, None, pred_path)
            n_ok += 1
            print(f"  OK ({time.monotonic() - t0:.1f}s)")
        except Exception as e:  # noqa: BLE001 — report and continue; do not lose progress on other clips
            n_fail += 1
            print(f"  FAILED: {type(e).__name__}: {str(e)[:400]}")

    print(f"\nDone. ok={n_ok} failed={n_fail} skipped={n_skip} out of {len(rows)} requested.")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
