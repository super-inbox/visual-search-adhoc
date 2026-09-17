#!/usr/bin/env python3
"""Data-pipeline smoke test for the How2Sign v2 benchmark (128 clips).

This is NOT a model evaluation. It feeds each clip's own reference text back in
as a trivial "prediction" (a perfect copy) and confirms the existing, unmodified
`asl-eval/evaluate.py` / `lib.py` scoring pipeline reads this benchmark's
manifest/reference format correctly end to end: IDs line up, SRT parsing works,
and a reference-as-prediction run produces a near-perfect score (WER/CER ~ 0,
temporal IoU ~ 1.0).

Deliberately isolated from core metric logic: this script imports `lib.py` and
`corpus_guard`-free `evaluate.run()`-equivalent logic by calling the same public
functions evaluate.py itself uses, but does not modify evaluate.py, lib.py, or
corpus_guard.py in any way. No network, no model calls, no video is opened.

Usage:
    python3 asl-translator/data/public_benchmarks/how2sign_v2/run_smoke_test.py
"""
from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
ASL_EVAL = REPO_ROOT / "asl-translator" / "asl-eval"
sys.path.insert(0, str(ASL_EVAL))
import lib  # noqa: E402


def main() -> int:
    manifest_path = HERE / "manifest.csv"
    with manifest_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} manifest rows from {manifest_path}")

    all_ok = True
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for row in rows:
            clip_id = row["how2sign_id"]
            ref_path = REPO_ROOT / row["local_reference_path"]
            ref_segments = lib.parse_srt(ref_path)

            if len(ref_segments) != 1:
                print(f"[FAIL] {clip_id}: expected exactly 1 reference segment, got {len(ref_segments)}")
                all_ok = False
                continue

            # Trivial "prediction" = perfect copy of the reference (smoke test only).
            pred_json = {
                "video": f"public_benchmarks/how2sign/videos/{clip_id}.mp4",
                "segments": [
                    {"start": s["start"], "end": s["end"], "text": s["text"]}
                    for s in ref_segments
                ],
            }
            pred_path = tmp_path / f"{clip_id}.json"
            pred_path.write_text(json.dumps(pred_json), encoding="utf-8")

            pred_segments = lib.parse_prediction_json(pred_path)
            ref_text = lib.build_transcript(ref_segments)
            pred_text = lib.build_transcript(pred_segments)
            tm = lib.text_metrics(ref_text, pred_text)
            ti = lib.timing_metrics(ref_segments, pred_segments)

            ok = (
                tm["wer"] == 0.0
                and tm["cer"] == 0.0
                and ti["temporal_iou"] == 1.0
                and abs(ref_segments[0]["end"] - float(row["duration_s"])) < 0.05
            )
            status = "OK" if ok else "FAIL"
            if not ok:
                all_ok = False
            print(
                f"[{status}] {clip_id:32s} dur={row['duration_s']:>6s}  "
                f"WER={tm['wer']:.4f} CER={tm['cer']:.4f} IoU={ti['temporal_iou']:.4f} "
                f"ref_words={tm['reference_words']}"
            )

    print()
    if all_ok:
        print(f"SMOKE TEST PASSED: all {len(rows)} clips - IDs matched, reference parsed, "
              "reference-as-prediction scored WER=0/CER=0/IoU=1.0.")
    else:
        print("SMOKE TEST FAILED: see [FAIL] rows above.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
