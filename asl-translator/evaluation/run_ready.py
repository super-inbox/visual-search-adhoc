#!/usr/bin/env python3
"""Automatically score every evaluation_set.json item whose reference file
and a matching prediction both already exist on disk.

This is the "run once ground truth lands" entry point. The ground-truth
annotation workflow (asl-translator/asl-ground-truth-annotator/,
asl-translator/data/asl_corpus/ANNOTATION_PLAN.md) is separate and
out of scope here -- this script never creates, edits, or verifies a
reference. It only detects references that already exist and scores them.

Point it at the corpus after:
  1. An ASL-fluent reviewer exports a verified reference into
     asl-translator/data/asl_corpus/ground_truth/<video_id>.srt (+ .json), and
  2. An entry for that video_id is added to evaluation_set.json
     (see asl-translator/evaluation/README.md for the safe procedure)
and it will find and score it automatically -- no manual
--reference/--prediction bookkeeping required.

Local, deterministic, stdlib-only. Read-only against ground_truth/,
ground_truth_candidates/, and predictions_baseline0/ -- writes only under
asl-translator/evaluation/results/. Never opens a corpus video. No network
calls, no model calls.

Usage:
    python3 asl-translator/evaluation/run_ready.py
    python3 asl-translator/evaluation/run_ready.py --include-non-official
    python3 asl-translator/evaluation/run_ready.py --results-dir /tmp/eval-results
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
ASL_TRANSLATOR_ROOT = EVAL_DIR.parent
ASL_EVAL_DIR = ASL_TRANSLATOR_ROOT / "asl-eval"
CORPUS_ROOT = ASL_TRANSLATOR_ROOT / "data" / "asl_corpus"

sys.path.insert(0, str(ASL_EVAL_DIR))
import evaluate  # noqa: E402
import status  # noqa: E402

# Videos that are content-identical to an evaluation_set.json item but were
# submitted/processed as a *separate* production job, so each has its own
# baseline0 prediction under a different video_id. Once the keyed item's
# reference exists, also score these extra predictions against that same
# reference -- this is how a single annotation pass on 1466 immediately
# scores both 1466's and 1467's predictions (see the documented
# determinism_pair in asl-translator/data/asl_corpus/manifest.json).
#
# This table is intentionally hand-maintained, not auto-derived from
# filenames: "content identical" is a provenance judgment made once by a
# human inspecting both videos, not something safe to infer generically.
EXTRA_PREDICTION_PAIRINGS: dict[str, list[str]] = {
    "1466_nohead-half1_189.5s": ["1467_nohead-half1_189.5s"],
}


def find_prediction(video_id: str) -> Path | None:
    p = CORPUS_ROOT / "predictions_baseline0" / f"{video_id}.json"
    return p if p.exists() else None


def score_one(reference_path: Path, prediction_path: Path, label: str, results_dir: Path) -> dict:
    result = evaluate.run(str(reference_path), str(prediction_path))
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / f"{label}.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=str(status.MANIFEST_PATH), help="Path to evaluation_set.json")
    ap.add_argument("--results-dir", default=str(EVAL_DIR / "results"), help="Where to write per-pair JSON results")
    ap.add_argument(
        "--include-non-official",
        action="store_true",
        help="Also score items whose reference exists but is not yet "
             "usable_for_official_metrics (e.g. 1320's candidate reference). "
             "Results are still saved and labeled DEBUG-ONLY, never presented as official.",
    )
    args = ap.parse_args()

    manifest = status.load_manifest(Path(args.manifest))
    rows = status.build_status(manifest)
    results_dir = Path(args.results_dir)

    scored: list[tuple[str, bool, float, float]] = []
    skipped: list[tuple[str, str]] = []

    for row, item in zip(rows, manifest["items"]):
        video_id = row["video_id"]

        if not row["reference_exists"]:
            skipped.append((video_id, "reference_missing"))
            continue
        if not row["prediction_found"]:
            skipped.append((video_id, "waiting_prediction"))
            continue

        is_official = item.get("usable_for_official_metrics", False)
        if not is_official and not args.include_non_official:
            skipped.append((video_id, "reference_not_official (pass --include-non-official to score anyway)"))
            continue

        reference_path = CORPUS_ROOT / item["reference"]
        prediction_path = ASL_TRANSLATOR_ROOT / row["prediction_path"]
        result = score_one(reference_path, prediction_path, video_id, results_dir)
        scored.append((video_id, is_official, result["text_metrics"]["wer"], result["text_metrics"]["cer"]))

        for extra_id in EXTRA_PREDICTION_PAIRINGS.get(video_id, []):
            extra_pred = find_prediction(extra_id)
            if extra_pred is None:
                skipped.append((extra_id, f"extra pairing for {video_id}: prediction not found"))
                continue
            label = f"{video_id}__vs__{extra_id}"
            extra_result = score_one(reference_path, extra_pred, label, results_dir)
            scored.append((label, is_official, extra_result["text_metrics"]["wer"], extra_result["text_metrics"]["cer"]))

    print(f"Scored {len(scored)} pair(s):")
    for label, is_official, wer, cer in scored:
        tag = "official" if is_official else "DEBUG-ONLY (not official)"
        print(f"  {label:55s} wer={wer:.4f} cer={cer:.4f}  [{tag}]")

    print()
    print(f"Skipped {len(skipped)} item(s):")
    for video_id, reason in skipped:
        print(f"  {video_id:45s} {reason}")

    if scored:
        print(f"\nDetailed per-pair JSON written under {results_dir}")
    else:
        print("\nNo real accuracy score was computed. This is expected while every "
              "queued sample is still waiting on an ASL-fluent human reference.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
