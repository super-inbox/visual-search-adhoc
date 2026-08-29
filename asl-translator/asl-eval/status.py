#!/usr/bin/env python3
"""Report which items in the evaluation-set manifest are actually ready to
evaluate: reference status, whether a matching baseline0 prediction exists,
and whether the pair is eligible for official metrics.

Local, deterministic, stdlib-only. Does not open any video or prediction
content — only checks file existence and the manifest's own fields.

Usage:
    python3 asl-translator/asl-eval/status.py [--json-out /tmp/status.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# This file lives at asl-translator/asl-eval/status.py — one level up is
# asl-translator/, which is the root all corpus paths are anchored to.
# Explicit, not derived from a fixed depth-from-repo-root assumption.
ASL_TRANSLATOR_ROOT = Path(__file__).resolve().parents[1]
CORPUS_ROOT = ASL_TRANSLATOR_ROOT / "data" / "asl_corpus"
MANIFEST_PATH = CORPUS_ROOT / "evaluation_set.json"


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_prediction(video_id: str) -> Path | None:
    """Look for a baseline0 prediction matching this video_id by basename."""
    candidate = CORPUS_ROOT / "predictions_baseline0" / f"{video_id}.json"
    return candidate if candidate.exists() else None


def build_status(manifest: dict) -> list[dict]:
    rows = []
    for item in manifest["items"]:
        ref_path = CORPUS_ROOT / item["reference"]
        reference_exists = ref_path.exists()
        prediction_path = find_prediction(item["video_id"])
        prediction_found = prediction_path is not None

        if not reference_exists:
            eligibility = "reference_missing"
        elif not prediction_found:
            eligibility = "waiting_prediction"
        elif not item.get("usable_for_official_metrics", False):
            eligibility = "reference_not_official"
        else:
            eligibility = "ready_for_official_metrics"

        rows.append(
            {
                "video_id": item["video_id"],
                "reference_status": item["reference_status"],
                "reference_exists": reference_exists,
                "prediction_found": prediction_found,
                "prediction_path": str(prediction_path.relative_to(ASL_TRANSLATOR_ROOT)) if prediction_path else None,
                "eligibility": eligibility,
            }
        )
    return rows


def print_human(rows: list[dict]) -> None:
    headers = ["Video", "Reference status", "Prediction found", "Eligibility"]
    widths = [max(len(h), 34) for h in headers]
    widths[0] = max(widths[0], max((len(r["video_id"]) for r in rows), default=0))
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for r in rows:
        print(
            fmt.format(
                r["video_id"],
                r["reference_status"],
                "yes" if r["prediction_found"] else "no",
                r["eligibility"],
            )
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=str(MANIFEST_PATH), help="Path to evaluation_set.json")
    ap.add_argument("--json-out", default=None, help="Optional path to write machine-readable JSON result")
    args = ap.parse_args()

    manifest = load_manifest(Path(args.manifest))
    rows = build_status(manifest)
    print_human(rows)

    ready = [r for r in rows if r["eligibility"] == "ready_for_official_metrics"]
    print()
    print(f"{len(ready)} of {len(rows)} evaluation-set item(s) are ready for official metrics.")
    if not ready:
        print("No real accuracy score can currently be computed — every item is waiting on a matching prediction.")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(f"\nWrote JSON result to {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
