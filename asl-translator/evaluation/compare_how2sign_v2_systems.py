#!/usr/bin/env python3
"""Build the 4-system How2Sign v2 scorecard (WER/CER/BLEU/chrF/n) and the
three pairwise comparisons the manager's native-video task asks for:

  1. Gemini native video  vs  Curify frame baseline (evaluation_2026_09_04_gemini_3_6)
  2. Gemini native video  vs  Uni-Sign
  3. Gemini native video  vs  OpenSLT
  4. 4-system scorecard: Curify frame / Gemini native video / Uni-Sign / OpenSLT

Reads ONLY already-written corpus_summary*.json files under
asl-translator/evaluation/results/how2sign_v2/<system>/ — makes no model
calls, modifies no existing result, and does not require GEMINI_API_KEY.

For each comparison this reports BOTH the ALL-scope number (whatever each
system's own corpus_summary.json covers) and the MATCHED-126 number (the
only scope valid for cross-system comparison, per the source spec's §11.3
and this repo's own run_curify_how2sign_v2_benchmark.py convention) side by
side, and never collapses them into one figure.

Usage (once native-video predictions exist):
    python3 asl-translator/evaluation/compare_how2sign_v2_systems.py \\
        --native-video-dir asl-translator/evaluation/results/how2sign_v2/curify_gemini_native_video_2026_09_10 \\
        --json-out /path/to/scorecard.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_ROOT = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2"

DEFAULT_DIRS = {
    "curify_frame_baseline": RESULTS_ROOT / "curify_gemini_3_6_2026_09_04",
    "unisign": RESULTS_ROOT / "unisign",
    "openslt": RESULTS_ROOT / "openslt",
}

METRICS = ["corpus_wer", "corpus_cer", "corpus_sacrebleu", "corpus_chrf"]
METRIC_LABELS = {
    "corpus_wer": "WER ↓",
    "corpus_cer": "CER ↓",
    "corpus_sacrebleu": "BLEU ↑",
    "corpus_chrf": "chrF ↑",
}
# OpenSLT's own harness names its independently-recomputed BLEU field
# differently (it also records fairseq's own self-reported number alongside
# it, which this script deliberately does NOT surface here — see its
# corpus_summary.json note — only the independently-recomputed figure is
# comparable to how sacrebleu is computed for every other system here).
METRIC_ALIASES = {"corpus_sacrebleu": ["corpus_sacrebleu", "corpus_sacrebleu_independent"]}


def _metric_value(summary: dict, metric: str):
    for key in METRIC_ALIASES.get(metric, [metric]):
        if summary.get(key) is not None:
            return summary.get(key)
    return None


# Not every existing result dir uses the same filenames/field names as this
# task's own new driver (run_native_video_how2sign_v2_benchmark.py /
# run_curify_how2sign_v2_benchmark.py write corpus_summary.json +
# corpus_summary_matched_126.json with n_success/n_total). Uni-Sign's own
# harness instead writes matched126_summary.json with a bare "n" field, and
# OpenSLT only ever produced 126 predictions in the first place, so its own
# corpus_summary.json (the "all" file) already IS the matched-126 scope —
# there is no separate matched file to look for. Handled explicitly here
# rather than silently mis-scoping any system.
ALL_FILENAME_CANDIDATES = ["corpus_summary.json"]
MATCHED_FILENAME_CANDIDATES = ["corpus_summary_matched_126.json", "matched126_summary.json"]
# Systems whose own "all" file already covers only the matched-126 clips
# (openslt never attempted the other 2) — reuse it for BOTH scopes instead
# of reporting matched_126 as unavailable.
ALL_IS_ALREADY_MATCHED = {"openslt"}


def _first_existing(results_dir: Path, candidates: list[str]) -> Optional[Path]:
    for name in candidates:
        p = results_dir / name
        if p.exists():
            return p
    return None


def load_summary(results_dir: Path, candidates: list[str]) -> Optional[dict]:
    path = _first_existing(results_dir, candidates)
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize(summary: dict) -> dict:
    n_success = summary.get("n_success", summary.get("n"))
    n_total = summary.get("n_total", summary.get("n"))
    return {
        "available": True,
        "n_success": n_success,
        "n_total": n_total,
        **{m: _metric_value(summary, m) for m in METRICS},
        "mean_prediction_reference_word_ratio": summary.get("mean_prediction_reference_word_ratio"),
    }


def row_for(system: str, results_dir: Path) -> dict:
    all_summary = load_summary(results_dir, ALL_FILENAME_CANDIDATES)
    matched_summary = load_summary(results_dir, MATCHED_FILENAME_CANDIDATES)
    if matched_summary is None and system in ALL_IS_ALREADY_MATCHED and all_summary is not None:
        matched_summary = all_summary
    row = {"system": system, "results_dir": str(results_dir.relative_to(REPO_ROOT)) if results_dir.exists() else str(results_dir)}
    for scope_name, summary in (("all", all_summary), ("matched_126", matched_summary)):
        row[scope_name] = _normalize(summary) if summary is not None else {"available": False}
    return row


def pairwise(a: dict, b: dict, scope: str) -> dict:
    """a vs b delta for one scope ('all' or 'matched_126'). Positive delta on
    WER/CER = a is worse; positive delta on BLEU/chrF = a is better. Never
    computed if either side is unavailable in that scope."""
    if not a.get(scope, {}).get("available") or not b.get(scope, {}).get("available"):
        return {"available": False}
    out = {"available": True}
    for m in METRICS:
        av, bv = a[scope].get(m), b[scope].get(m)
        out[m] = {"a": av, "b": bv, "delta_a_minus_b": round(av - bv, 4) if (av is not None and bv is not None) else None}
    return out


def print_scorecard(rows: dict, scope: str) -> None:
    print(f"\n=== 4-system scorecard — scope: {scope} ===")
    header = f"{'system':<22} {'n':>5} " + " ".join(f"{METRIC_LABELS[m]:>10}" for m in METRICS)
    print(header)
    print("-" * len(header))
    for name, row in rows.items():
        s = row.get(scope, {})
        if not s.get("available"):
            print(f"{name:<22} {'--':>5} (no {scope} corpus_summary found at {row['results_dir']})")
            continue
        n = s.get("n_success")
        vals = " ".join(f"{s.get(m):>10}" if s.get(m) is not None else f"{'--':>10}" for m in METRICS)
        print(f"{name:<22} {n:>5} {vals}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--native-video-dir", default=str(RESULTS_ROOT / "curify_gemini_native_video_2026_09_10"),
                     help="Results dir written by run_native_video_how2sign_v2_benchmark.py")
    ap.add_argument("--curify-frame-dir", default=str(DEFAULT_DIRS["curify_frame_baseline"]))
    ap.add_argument("--unisign-dir", default=str(DEFAULT_DIRS["unisign"]))
    ap.add_argument("--openslt-dir", default=str(DEFAULT_DIRS["openslt"]))
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args(argv)

    dirs = {
        "curify_frame_baseline": Path(args.curify_frame_dir),
        "gemini_native_video": Path(args.native_video_dir),
        "unisign": Path(args.unisign_dir),
        "openslt": Path(args.openslt_dir),
    }
    rows = {name: row_for(name, d) for name, d in dirs.items()}

    print_scorecard(rows, "all")
    print_scorecard(rows, "matched_126")

    comparisons = {}
    if rows["gemini_native_video"]["all"].get("available") or rows["gemini_native_video"]["matched_126"].get("available"):
        for scope in ("all", "matched_126"):
            comparisons.setdefault("native_video_vs_curify_frame", {})[scope] = pairwise(
                rows["gemini_native_video"], rows["curify_frame_baseline"], scope)
            comparisons.setdefault("native_video_vs_unisign", {})[scope] = pairwise(
                rows["gemini_native_video"], rows["unisign"], scope)
            comparisons.setdefault("native_video_vs_openslt", {})[scope] = pairwise(
                rows["gemini_native_video"], rows["openslt"], scope)
    else:
        print("\nNo native-video corpus_summary found yet — run "
              "run_native_video_how2sign_v2_benchmark.py first (see --native-video-dir). "
              "Scorecard above shows the 3 existing systems only.")

    out = {"scorecard": rows, "pairwise_comparisons": comparisons,
           "note": "WER movement alone is not evidence of semantic improvement — see "
                   "mean_prediction_reference_word_ratio in each row and the source spec's §12.5 "
                   "finding that shorter output can lower WER on this corpus without improving meaning."}
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"\nWrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
