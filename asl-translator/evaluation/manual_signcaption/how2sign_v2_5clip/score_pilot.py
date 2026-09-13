#!/usr/bin/env python3
"""Score the manually-run SignCaption pilot (5 How2Sign v2 clips) against the frozen
reference, and build a 5/6-system comparison table alongside it.

PREPARED BUT NOT EXECUTED. This script makes no network calls, no Gemini/SignCaption API
calls, and does not run any experiment — it only reads local files: the frozen benchmark
manifest/references, the already-scored Curify/Uni-Sign/native-video/trajectory result
files, and whatever the human operator has manually placed under
clips/<clip_id>/signcaption_result.{srt,txt}.

It reuses the repo's own scoring primitives (asl-eval/lib.py: parse_srt, build_transcript,
text_metrics) and the same corpus-level BLEU/chrF convention already used by
run_curify_how2sign_v2_benchmark.py / run_native_video_how2sign_v2_benchmark.py
(sacrebleu.BLEU()/CHRF().corpus_score, called per-clip with a single-sentence list — the
same call shape already used corpus-wide elsewhere in this repo, applied here at n=1 per
clip since this pilot is intentionally small).

SignCaption's output is scored strictly as a PREDICTION being benchmarked against the
frozen reference — it is never treated as ground truth, and it never overwrites or
corrects any other system's existing recorded result.

Usage (do not run until all 5 clips.README.md-implied result files are place):
    python3 asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/score_pilot.py \\
        --write-results

    # Inspect without writing anything:
    python3 asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/score_pilot.py \\
        --dry-run
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
ASL_EVAL_DIR = REPO_ROOT / "asl-translator" / "asl-eval"
sys.path.insert(0, str(ASL_EVAL_DIR))
import lib  # noqa: E402  (repo's own parse_srt / build_transcript / text_metrics)

BENCH_DIR = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2"
REFERENCES_DIR = BENCH_DIR / "references"
RESULTS_ROOT = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2"
CLIPS_DIR = HERE / "clips"
OUT_DIR = HERE / "results"

BASELINE_PER_CLIP = RESULTS_ROOT / "curify_gemini_3_6_2026_09_04" / "per_clip_results.json"
UNISIGN_PER_CLIP = RESULTS_ROOT / "unisign" / "per_clip_results.json"
NATIVE_VIDEO_PER_CLIP = RESULTS_ROOT / "curify_gemini_native_video_2026_09_10" / "per_clip_results.json"
TRAJECTORY_PREDICTIONS_DIR = RESULTS_ROOT / "curify_gemini_trajectory_augmented_2026_09_10" / "predictions"

CLIP_IDS = [
    "FzmL8SL6Bow_1-8-rgb_front",
    "92V3oH63zbQ_5-1-rgb_front",
    "G05uFub3YFc_9-2-rgb_front",
    "fzNnTgHa1lM_2-5-rgb_front",
    "-g0sqksgyc4_3-2-rgb_front",
]


def _load_per_clip(path: Path) -> dict:
    if not path.exists():
        return {}
    return {r["how2sign_id"]: r for r in json.loads(path.read_text(encoding="utf-8"))}


def _corpus_bleu_chrf_single(ref_text: str, pred_text: str) -> dict:
    """Same call shape as run_curify_how2sign_v2_benchmark.py's _corpus_bleu_chrf /
    run_native_video_how2sign_v2_benchmark.py's _corpus_bleu_chrf, applied to one
    ref/hyp pair (n=1) rather than the full corpus — this pilot is 5 clips, not 128."""
    try:
        import sacrebleu
    except ImportError:
        return {"bleu": None, "chrf": None, "note": "sacrebleu not installed in this environment"}
    bleu = sacrebleu.BLEU()
    chrf = sacrebleu.CHRF()
    bleu_score = bleu.corpus_score([pred_text], [[ref_text]])
    chrf_score = chrf.corpus_score([pred_text], [[ref_text]])
    return {"bleu": round(bleu_score.score, 4), "chrf": round(chrf_score.score, 4)}


def load_signcaption_result(clip_id: str) -> dict:
    """Read the manually-placed SignCaption export for one clip.

    Returns one of three explicit, non-overlapping states — never silently merged:
      - status="missing"          : no result file exists at all (not attempted yet)
      - status="empty_prediction" : a result file exists and is genuinely empty
                                     (SignCaption returned nothing — a real result)
      - status="parse_failure"    : a result file exists, is non-empty, but could not
                                     be parsed into transcript text
      - status="success"          : parsed to a (possibly single-segment) transcript
    """
    clip_dir = CLIPS_DIR / clip_id
    srt_path = clip_dir / "signcaption_result.srt"
    txt_path = clip_dir / "signcaption_result.txt"

    if srt_path.exists():
        raw = srt_path.read_text(encoding="utf-8-sig", errors="replace")
        if raw.strip() == "":
            return {"status": "empty_prediction", "prediction_text": "", "source_file": str(srt_path.relative_to(REPO_ROOT))}
        try:
            segments = lib.parse_srt(srt_path)
        except Exception as e:  # malformed SRT
            return {"status": "parse_failure", "prediction_text": None,
                     "source_file": str(srt_path.relative_to(REPO_ROOT)), "error": str(e)}
        if not segments:
            # Non-empty file, but nothing matched the SRT cue-block pattern —
            # this is a parse failure, not a genuine empty prediction: SignCaption
            # returned *something* (the file has bytes) but it wasn't valid SRT.
            return {"status": "parse_failure", "prediction_text": None,
                     "source_file": str(srt_path.relative_to(REPO_ROOT)),
                     "error": "file is non-empty but no valid SRT cue block was found"}
        text = lib.build_transcript(segments)
        return {"status": "success", "prediction_text": text,
                "source_file": str(srt_path.relative_to(REPO_ROOT)), "segments": segments}

    if txt_path.exists():
        raw = txt_path.read_text(encoding="utf-8", errors="replace").strip()
        if raw == "":
            return {"status": "empty_prediction", "prediction_text": "", "source_file": str(txt_path.relative_to(REPO_ROOT))}
        return {"status": "success", "prediction_text": raw,
                "source_file": str(txt_path.relative_to(REPO_ROOT))}

    return {"status": "missing", "prediction_text": None, "source_file": None}


def score_clip(clip_id: str, baseline_by_id: dict, unisign_by_id: dict,
                native_by_id: dict) -> dict:
    ref_path = REFERENCES_DIR / f"{clip_id}.srt"
    ref_segments = lib.parse_srt(ref_path)
    ref_text = lib.build_transcript(ref_segments)

    sc = load_signcaption_result(clip_id)
    row = {
        "clip_id": clip_id,
        "reference_text": ref_text,
        "signcaption_status": sc["status"],
        "signcaption_source_file": sc.get("source_file"),
    }

    if sc["status"] == "success":
        tm = lib.text_metrics(ref_text, sc["prediction_text"])
        bc = _corpus_bleu_chrf_single(ref_text, sc["prediction_text"])
        row.update({
            "signcaption_prediction_text": sc["prediction_text"],
            "signcaption_wer": tm["wer"],
            "signcaption_cer": tm["cer"],
            "signcaption_bleu": bc["bleu"],
            "signcaption_chrf": bc["chrf"],
        })
    elif sc["status"] == "empty_prediction":
        tm = lib.text_metrics(ref_text, "")
        row.update({
            "signcaption_prediction_text": "",
            "signcaption_wer": tm["wer"],
            "signcaption_cer": tm["cer"],
            "signcaption_bleu": 0.0,
            "signcaption_chrf": 0.0,
        })
    else:
        # "missing" or "parse_failure" — no score is computed or fabricated.
        row.update({
            "signcaption_prediction_text": None,
            "signcaption_wer": None,
            "signcaption_cer": None,
            "signcaption_bleu": None,
            "signcaption_chrf": None,
        })
        if sc["status"] == "parse_failure":
            row["signcaption_parse_error"] = sc.get("error")

    # Existing, already-scored systems — read-only, never recomputed.
    b = baseline_by_id.get(clip_id)
    u = unisign_by_id.get(clip_id)
    n = native_by_id.get(clip_id)
    row["curify_frame_baseline_prediction_text"] = (b or {}).get("prediction_text")
    row["curify_frame_baseline_wer"] = (b or {}).get("wer") if b and b.get("status") == "success" else None
    row["unisign_prediction_text"] = (u or {}).get("prediction_text")
    row["unisign_wer"] = (u or {}).get("wer") if u and u.get("status") == "success" else None
    row["native_video_prediction_text"] = (n or {}).get("prediction_text")
    row["native_video_wer"] = (n or {}).get("wer") if n and n.get("status") == "success" else None

    traj_path = TRAJECTORY_PREDICTIONS_DIR / f"{clip_id}.json"
    if traj_path.exists():
        # This prediction file is baseline0-shaped ({"segments": [...]})  , the same
        # shape run_trajectory_augmented_experiment.py's condition B (treatment) wrote —
        # no precomputed WER is stored alongside it, so it is scored here the same way
        # every other system in this repo is scored: lib.parse_prediction_json +
        # build_transcript + text_metrics against the frozen reference. Read-only;
        # this does not rerun the experiment or call Gemini.
        traj_segments = lib.parse_prediction_json(traj_path)
        traj_text = lib.build_transcript(traj_segments)
        traj_tm = lib.text_metrics(ref_text, traj_text)
        row["trajectory_augmented_available"] = True
        row["trajectory_augmented_prediction_text"] = traj_text
        row["trajectory_augmented_wer"] = traj_tm["wer"]
    else:
        row["trajectory_augmented_available"] = False
        row["trajectory_augmented_prediction_text"] = None
        row["trajectory_augmented_wer"] = None

    return row


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write-results", action="store_true",
                     help="Write per_clip_results.json/.csv under results/. Without this flag, prints a summary only.")
    ap.add_argument("--dry-run", action="store_true",
                     help="Explicit no-op alias: never writes files, only prints status per clip.")
    args = ap.parse_args(argv)

    baseline_by_id = _load_per_clip(BASELINE_PER_CLIP)
    unisign_by_id = _load_per_clip(UNISIGN_PER_CLIP)
    native_by_id = _load_per_clip(NATIVE_VIDEO_PER_CLIP)

    rows = [score_clip(c, baseline_by_id, unisign_by_id, native_by_id) for c in CLIP_IDS]

    n_missing = sum(1 for r in rows if r["signcaption_status"] == "missing")
    n_empty = sum(1 for r in rows if r["signcaption_status"] == "empty_prediction")
    n_parse_fail = sum(1 for r in rows if r["signcaption_status"] == "parse_failure")
    n_success = sum(1 for r in rows if r["signcaption_status"] == "success")

    print(f"SignCaption manual pilot — {len(rows)} clips")
    print(f"  success: {n_success}  empty_prediction: {n_empty}  parse_failure: {n_parse_fail}  missing: {n_missing}")
    for r in rows:
        print(f"  {r['clip_id']:32s} signcaption_status={r['signcaption_status']:16s} "
              f"wer={r['signcaption_wer']}")

    if n_missing == len(rows):
        print("\nNo SignCaption results have been placed yet — nothing to score. "
              "See MANUAL_UPLOAD_CHECKLIST.md.")

    if args.dry_run or not args.write_results:
        print("\n(dry run / no --write-results — nothing written)")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "per_clip_comparison.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")

    fieldnames = [
        "clip_id", "reference_text",
        "curify_frame_baseline_prediction_text", "curify_frame_baseline_wer",
        "unisign_prediction_text", "unisign_wer",
        "native_video_prediction_text", "native_video_wer",
        "signcaption_status", "signcaption_source_file", "signcaption_prediction_text",
        "signcaption_wer", "signcaption_cer", "signcaption_bleu", "signcaption_chrf",
        "trajectory_augmented_available", "trajectory_augmented_prediction_text", "trajectory_augmented_wer",
    ]
    with open(OUT_DIR / "per_clip_comparison.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"\nWrote {OUT_DIR / 'per_clip_comparison.json'} and {OUT_DIR / 'per_clip_comparison.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
