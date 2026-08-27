#!/usr/bin/env python3
"""Compare a reference SRT against a prediction JSON for the ASL corpus.

Local, deterministic, stdlib-only. No network calls, no model calls.
Never reads the corpus videos.

Usage:
    python3 tools/asl-eval/evaluate.py \\
        --reference data/asl_corpus/ground_truth/155_demo_asl-demo-translation_26.7s.srt \\
        --prediction /path/to/prediction.json \\
        [--json-out /tmp/eval.json] [--no-alignment]

WER/CER are English-text comparison metrics only. They do not capture ASL
semantic quality or correctness of the underlying translation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402


def run(reference: str, prediction: str, include_alignment: bool = True) -> dict:
    ref_segments = lib.parse_srt(reference)
    pred_segments = lib.parse_prediction_json(prediction)

    ref_text = lib.build_transcript(ref_segments)
    pred_text = lib.build_transcript(pred_segments)

    result = {
        "reference": str(reference),
        "prediction": str(prediction),
        "reference_segment_count": len(ref_segments),
        "prediction_segment_count": len(pred_segments),
        "text_metrics": lib.text_metrics(ref_text, pred_text),
        "timing_metrics": lib.timing_metrics(ref_segments, pred_segments),
    }
    if include_alignment:
        result["segment_alignment"] = lib.align_segments(ref_segments, pred_segments)
    return result


def print_human(result: dict) -> None:
    tm = result["text_metrics"]
    ti = result["timing_metrics"]
    print(f"Reference : {result['reference']} ({result['reference_segment_count']} segments)")
    print(f"Prediction: {result['prediction']} ({result['prediction_segment_count']} segments)")
    print()
    print("Text metrics (English-transcript comparison only — not ASL semantic quality):")
    print(f"  reference words : {tm['reference_words']}")
    print(f"  prediction words: {tm['prediction_words']}")
    print(f"  substitutions   : {tm['substitutions']}")
    print(f"  deletions       : {tm['deletions']}")
    print(f"  insertions      : {tm['insertions']}")
    print(f"  WER             : {tm['wer']}")
    print(f"  CER             : {tm['cer']}")
    print()
    print("Timing / coverage metrics (when captions exist, not what they say):")
    print(f"  reference_coverage_s : {ti['reference_coverage_s']}")
    print(f"  prediction_coverage_s: {ti['prediction_coverage_s']}")
    print(f"  overlap_s             : {ti['overlap_s']}")
    print(f"  temporal_precision    : {ti['temporal_precision']}")
    print(f"  temporal_recall       : {ti['temporal_recall']}")
    print(f"  temporal_iou          : {ti['temporal_iou']}")
    print()
    print("Normalized transcripts (debug):")
    print(f"  reference : {tm['reference_transcript_normalized']!r}")
    print(f"  prediction: {tm['prediction_transcript_normalized']!r}")
    if "segment_alignment" in result:
        print()
        print("Segment alignment (diagnostic only, not the primary score):")
        for a in result["segment_alignment"]:
            print(
                f"  ref[{a['ref_index']}] {a['ref_start']:.2f}-{a['ref_end']:.2f} "
                f"{a['ref_text']!r} -> "
                f"{a['matched_prediction_text']!r} (overlap={a['overlap_s']}s, iou={a['iou']})"
            )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reference", required=True, help="Path to reference .srt")
    ap.add_argument("--prediction", required=True, help="Path to prediction .json")
    ap.add_argument("--json-out", default=None, help="Optional path to write machine-readable JSON result")
    ap.add_argument("--no-alignment", action="store_true", help="Skip the per-segment alignment diagnostic")
    args = ap.parse_args()

    result = run(args.reference, args.prediction, include_alignment=not args.no_alignment)
    print_human(result)

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nWrote JSON result to {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
