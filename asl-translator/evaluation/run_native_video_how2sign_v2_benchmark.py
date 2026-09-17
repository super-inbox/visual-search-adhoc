#!/usr/bin/env python3
"""Run the Gemini NATIVE-VIDEO ASL method across the frozen How2Sign v2
benchmark (128 clips) and score every prediction with the existing,
UNMODIFIED asl-eval/evaluate.py + lib.py.

This is the native-video sibling of run_curify_how2sign_v2_benchmark.py —
same manifest, same scorer, same resumability/retry conventions, same
matched-126 comparability logic. The ONLY thing that differs is which
runner produces the prediction: this script calls
asl-eval/run_native_video.run_real() (whole .mp4 via the Files API, 1 call
per clip) instead of asl-eval/run_current_model.run_real() (sampled JPEG
frames, N calls per clip).

Neither the frozen benchmark's manifest/references/videos, nor
run_native_video.py, nor evaluate.py/lib.py is modified or
monkeypatched by this script.

────────────────────────────────────────────────────────────────────────────
Design note: independent variable isolation
────────────────────────────────────────────────────────────────────────────
The manager's task frames this experiment's primary independent variable as
"frame-based input vs native/direct video input." Model and prompt-intent
are held as close to run_curify_how2sign_v2_benchmark.py's
`evaluation_2026_09_04_gemini_3_6` control as Section 13 allows — see
run_native_video.py's module docstring for the one unavoidable prompt
confound (13.1) this inherits by construction.

────────────────────────────────────────────────────────────────────────────
Resume / retry / failure handling — identical semantics to the frame-based
driver (run_curify_how2sign_v2_benchmark.py), same code shape, reapplied
here rather than imported, because the per-clip call signature differs
(run_native_video.run_real takes no frame_budget argument).
────────────────────────────────────────────────────────────────────────────

Usage:
    # Plan only (zero network calls, exact expected upload+call count):
    python3 asl-translator/evaluation/run_native_video_how2sign_v2_benchmark.py \\
        --config native_video_2026_09_10_gemini_3_6 --plan-only

    # One-clip smoke test (real Gemini call — NOT run by this task):
    python3 asl-translator/evaluation/run_native_video_how2sign_v2_benchmark.py \\
        --config native_video_2026_09_10_gemini_3_6 --clip-ids <how2sign_id> \\
        --run --acknowledge-private-data-upload

    # The fixed diagnostic-12 (NOT run by this task):
    python3 asl-translator/evaluation/run_native_video_how2sign_v2_benchmark.py \\
        --config native_video_2026_09_10_gemini_3_6 \\
        --clip-ids-file asl-translator/evaluation/diagnostics/phase1_temporal_ablation/diagnostic_12_clips.json \\
        --run --acknowledge-private-data-upload

    # Full frozen benchmark (128 clips) — NOT run by this task:
    python3 asl-translator/evaluation/run_native_video_how2sign_v2_benchmark.py \\
        --config native_video_2026_09_10_gemini_3_6 --run --acknowledge-private-data-upload
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
ASL_EVAL_DIR = REPO_ROOT / "asl-translator" / "asl-eval"
BENCH_DIR = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2"
MANIFEST_PATH = BENCH_DIR / "manifest.csv"
FREEZE_FINGERPRINT_PATH = BENCH_DIR / "FREEZE.sha256"
OPENSLT_METADATA_PATH = (
    REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "openslt" / "run_metadata.json"
)
UNISIGN_PER_CLIP_PATH = (
    REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "unisign" / "per_clip_results.json"
)
DEFAULT_RESULTS_DIR_NAME = {
    "native_video_2026_09_10_gemini_3_6": "curify_gemini_native_video_2026_09_10",
}

sys.path.insert(0, str(ASL_EVAL_DIR))
import run_native_video  # noqa: E402
import evaluate as evaluate_mod  # noqa: E402
import lib  # noqa: E402

TRANSIENT_HTTP_CODES = {429, 500, 502, 503, 504}
_KEY_LOOKALIKE_RE = re.compile(r"AIza[0-9A-Za-z_\-]{10,}")


def redact(text: str, secret: Optional[str]) -> str:
    if secret:
        text = text.replace(secret, "[REDACTED_API_KEY]")
    text = _KEY_LOOKALIKE_RE.sub("[REDACTED_KEY_LOOKALIKE]", text)
    return text


def classify_error(exc: BaseException) -> tuple[bool, Optional[int]]:
    code = getattr(exc, "code", None)
    if not isinstance(code, int):
        code = getattr(exc, "status_code", None)
    if isinstance(code, int) and code in TRANSIENT_HTTP_CODES:
        return True, code
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return True, code if isinstance(code, int) else None
    return False, code if isinstance(code, int) else None


def load_manifest_rows() -> list[dict]:
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def select_rows(rows: list[dict], limit: Optional[int], clip_ids: Optional[list[str]]) -> list[dict]:
    if clip_ids:
        wanted = set(clip_ids)
        selected = [r for r in rows if r["how2sign_id"] in wanted]
        missing = wanted - {r["how2sign_id"] for r in selected}
        if missing:
            raise SystemExit(f"--clip-ids not found in manifest.csv: {sorted(missing)}")
        return selected
    if limit is not None:
        return rows[:limit]
    return rows


def load_clip_ids_file(path: str) -> list[str]:
    """Read the fixed diagnostic-12 clip-id list from diagnostic_12_clips.json
    (or any file with the same {"clips": [{"clip_id": ...}, ...]} shape)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "clips" in data:
        return [c["clip_id"] for c in data["clips"]]
    if isinstance(data, list):
        return list(data)
    raise SystemExit(f"Unrecognised --clip-ids-file shape in {path}")


# ─────────────────────────────────────────────────────────────────────────
# Comparability — same matched-subset logic as the frame-based driver.
# ─────────────────────────────────────────────────────────────────────────
def load_openslt_missing_ids() -> tuple[set[str], str]:
    if not OPENSLT_METADATA_PATH.exists():
        return set(), "openslt run_metadata.json not found; treated as 0 missing"
    d = json.loads(OPENSLT_METADATA_PATH.read_text(encoding="utf-8"))
    missing = set(d.get("how2sign_v2_clips_missing", []))
    return missing, str(OPENSLT_METADATA_PATH.relative_to(REPO_ROOT))


def load_unisign_missing_ids() -> tuple[set[str], str]:
    if not UNISIGN_PER_CLIP_PATH.exists():
        return set(), "unisign per_clip_results.json not found; treated as 0 missing"
    d = json.loads(UNISIGN_PER_CLIP_PATH.read_text(encoding="utf-8"))
    missing = {r["how2sign_id"] for r in d if r.get("status") != "success"}
    return missing, str(UNISIGN_PER_CLIP_PATH.relative_to(REPO_ROOT))


def compute_matched_subset(all_ids: list[str]) -> dict:
    openslt_missing, openslt_src = load_openslt_missing_ids()
    unisign_missing, unisign_src = load_unisign_missing_ids()
    excluded = openslt_missing | unisign_missing
    matched = [i for i in all_ids if i not in excluded]
    return {
        "matched_ids": matched,
        "matched_count": len(matched),
        "excluded_ids": sorted(excluded),
        "excluded_count": len(excluded),
        "excluded_from_openslt": sorted(openslt_missing),
        "excluded_from_unisign": sorted(unisign_missing),
        "openslt_source": openslt_src,
        "unisign_source": unisign_src,
    }


# ─────────────────────────────────────────────────────────────────────────
# Per-clip execution
# ─────────────────────────────────────────────────────────────────────────
def existing_prediction_matches_config(pred_path: Path, config_name: str) -> bool:
    if not pred_path.exists():
        return False
    try:
        data = json.loads(pred_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return (
        data.get("run_metadata", {}).get("config") == config_name
        and isinstance(data.get("segments"), list)
    )


def score_prediction(clip_id: str, row: dict, pred_path: Path, ref_path: Path) -> dict:
    pred_data = json.loads(pred_path.read_text(encoding="utf-8"))
    result = evaluate_mod.run(str(ref_path), str(pred_path), include_alignment=False)
    tm = result["text_metrics"]
    ti = result["timing_metrics"]
    meta = pred_data.get("run_metadata", {})
    return {
        "how2sign_id": clip_id,
        "status": "success",
        "failure_reason": "",
        "duration_s": float(row["duration_s"]),
        "reference_words": tm["reference_words"],
        "prediction_words": tm["prediction_words"],
        "substitutions": tm["substitutions"],
        "deletions": tm["deletions"],
        "insertions": tm["insertions"],
        "wer": tm["wer"],
        "cer": tm["cer"],
        "char_level": tm["char_level"],
        "timing_metrics": ti,
        "model_calls": meta.get("model_calls"),
        "files_uploaded": meta.get("files_uploaded"),
        "upload_wall_clock_s": meta.get("upload_wall_clock_s"),
        "file_processing_wait_s": meta.get("file_processing_wait_s"),
        "generate_content_wall_clock_s": meta.get("generate_content_wall_clock_s"),
        "token_usage": meta.get("token_usage"),
        "thinking_level": meta.get("thinking_level"),
    }


def run_one_clip(
    row: dict,
    config_name: str,
    results_dir: Path,
    api_key: str,
    max_retries: int,
    retry_backoff_s: float,
    overwrite: bool,
    keep_uploaded_file: bool,
    file_state_poll_timeout_s: float,
) -> dict:
    clip_id = row["how2sign_id"]
    video_path = REPO_ROOT / row["local_video_path"]
    ref_path = REPO_ROOT / row["local_reference_path"]
    pred_path = results_dir / "predictions" / f"{clip_id}.json"

    if not video_path.exists():
        return _base_record(clip_id, row, status="failed",
                             reason=f"missing_video: {video_path.relative_to(REPO_ROOT)}", attempts=0)
    if not ref_path.exists():
        return _base_record(clip_id, row, status="failed",
                             reason=f"missing_reference: {ref_path.relative_to(REPO_ROOT)}", attempts=0)

    if not overwrite and existing_prediction_matches_config(pred_path, config_name):
        print(f"  SKIP (already completed for {config_name}): {clip_id}")
        rec = score_prediction(clip_id, row, pred_path, ref_path)
        rec["reference_text"] = _load_ref_text(ref_path)
        rec["prediction_text"] = _load_pred_text(pred_path)
        rec["attempts"] = 0
        rec["skipped_existing"] = True
        rec["inference_wall_clock_s"] = 0.0
        return rec

    if pred_path.exists() and not existing_prediction_matches_config(pred_path, config_name) and not overwrite:
        print(f"  NOTE: existing prediction for {clip_id} was written under a different config "
              f"(or is unreadable) — regenerating under {config_name}, not reusing it.")

    attempts = 0
    last_error: Optional[dict] = None
    t0 = time.monotonic()
    for attempt in range(1, max_retries + 1):
        attempts = attempt
        try:
            run_native_video.run_real(
                video_path, config_name, pred_path,
                delete_uploaded_file=not keep_uploaded_file,
                file_state_poll_timeout_s=file_state_poll_timeout_s,
            )
            last_error = None
            break
        except SystemExit:
            raise  # missing GEMINI_API_KEY — abort the whole run, not just this clip
        except Exception as e:  # noqa: BLE001 — must classify, log, and continue the corpus
            transient, code = classify_error(e)
            sanitized = redact(str(e)[:600], api_key)
            last_error = {"error_type": type(e).__name__, "error": sanitized, "status_code": code,
                          "transient": transient}
            print(f"  attempt {attempt}/{max_retries} FAILED for {clip_id}: "
                  f"{type(e).__name__} (status={code}, transient={transient})")
            if not transient or attempt == max_retries:
                break
            time.sleep(retry_backoff_s * attempt)
    wall_s = round(time.monotonic() - t0, 3)

    if last_error is not None:
        rec = _base_record(clip_id, row, status="failed", reason=last_error["error"], attempts=attempts)
        rec["error_type"] = last_error["error_type"]
        rec["status_code"] = last_error["status_code"]
        rec["inference_wall_clock_s"] = wall_s
        return rec

    rec = score_prediction(clip_id, row, pred_path, ref_path)
    rec["reference_text"] = _load_ref_text(ref_path)
    rec["prediction_text"] = _load_pred_text(pred_path)
    rec["attempts"] = attempts
    rec["skipped_existing"] = False
    rec["inference_wall_clock_s"] = wall_s
    return rec


def _base_record(clip_id: str, row: dict, status: str, reason: str, attempts: int) -> dict:
    return {
        "how2sign_id": clip_id,
        "status": status,
        "failure_reason": reason,
        "duration_s": float(row["duration_s"]) if row.get("duration_s") else None,
        "reference_text": None,
        "prediction_text": None,
        "wer": None,
        "cer": None,
        "reference_words": None,
        "prediction_words": None,
        "substitutions": None,
        "deletions": None,
        "insertions": None,
        "char_level": None,
        "timing_metrics": None,
        "model_calls": None,
        "files_uploaded": None,
        "upload_wall_clock_s": None,
        "file_processing_wait_s": None,
        "generate_content_wall_clock_s": None,
        "token_usage": None,
        "thinking_level": None,
        "attempts": attempts,
        "skipped_existing": False,
        "inference_wall_clock_s": None,
    }


def _load_ref_text(ref_path: Path) -> str:
    return lib.build_transcript(lib.parse_srt(ref_path))


def _load_pred_text(pred_path: Path) -> str:
    return lib.build_transcript(lib.parse_prediction_json(pred_path))


# ─────────────────────────────────────────────────────────────────────────
# Corpus-level aggregation — identical shape to the frame-based driver, so
# compare_how2sign_v2_systems.py can read both result dirs the same way.
# ─────────────────────────────────────────────────────────────────────────
def _corpus_wer_cer(records: list[dict]) -> dict:
    succ = [r for r in records if r["status"] == "success"]
    if not succ:
        return {"corpus_wer": None, "corpus_cer": None, "total_reference_words": 0,
                "total_substitutions": 0, "total_deletions": 0, "total_insertions": 0}
    total_ref_words = sum(r["reference_words"] for r in succ)
    total_sub = sum(r["substitutions"] for r in succ)
    total_del = sum(r["deletions"] for r in succ)
    total_ins = sum(r["insertions"] for r in succ)
    total_ref_chars = sum(r["char_level"]["reference_chars"] for r in succ)
    total_csub = sum(r["char_level"]["substitutions"] for r in succ)
    total_cdel = sum(r["char_level"]["deletions"] for r in succ)
    total_cins = sum(r["char_level"]["insertions"] for r in succ)
    return {
        "corpus_wer": round((total_sub + total_del + total_ins) / total_ref_words, 4) if total_ref_words else None,
        "corpus_cer": round((total_csub + total_cdel + total_cins) / total_ref_chars, 4) if total_ref_chars else None,
        "total_reference_words": total_ref_words,
        "total_substitutions": total_sub,
        "total_deletions": total_del,
        "total_insertions": total_ins,
    }


def _corpus_timing(records: list[dict]) -> dict:
    succ = [r for r in records if r["status"] == "success" and r.get("timing_metrics")]
    if not succ:
        return {}
    keys = ["reference_coverage_s", "prediction_coverage_s", "overlap_s"]
    sums = {k: round(sum(r["timing_metrics"][k] for r in succ), 3) for k in keys}
    return {
        **{f"sum_{k}": v for k, v in sums.items()},
        "mean_temporal_precision": round(sum(r["timing_metrics"]["temporal_precision"] for r in succ) / len(succ), 4),
        "mean_temporal_recall": round(sum(r["timing_metrics"]["temporal_recall"] for r in succ) / len(succ), 4),
        "mean_temporal_iou": round(sum(r["timing_metrics"]["temporal_iou"] for r in succ) / len(succ), 4),
    }


def _corpus_bleu_chrf(records: list[dict]) -> dict:
    succ = [r for r in records if r["status"] == "success"]
    if not succ:
        return {"corpus_sacrebleu": None, "corpus_chrf": None, "sacrebleu_version": None,
                "bleu_signature": None, "chrf_signature": None}
    try:
        import sacrebleu
    except ImportError:
        return {"corpus_sacrebleu": None, "corpus_chrf": None, "sacrebleu_version": None,
                "bleu_signature": None, "chrf_signature": None,
                "note": "sacrebleu not installed in this environment"}
    hyps = [r["prediction_text"] for r in succ]
    refs = [r["reference_text"] for r in succ]
    bleu = sacrebleu.BLEU()
    chrf = sacrebleu.CHRF()
    bleu_score = bleu.corpus_score(hyps, [refs])
    chrf_score = chrf.corpus_score(hyps, [refs])
    return {
        "corpus_sacrebleu": round(bleu_score.score, 4),
        "corpus_chrf": round(chrf_score.score, 4),
        "sacrebleu_version": sacrebleu.__version__,
        "bleu_signature": str(bleu.get_signature()),
        "chrf_signature": str(chrf.get_signature()),
    }


def _corpus_length_ratio(records: list[dict]) -> dict:
    """§12.5's finding: report a length-insensitive signal alongside WER so a
    shorter-output artefact isn't misread as a quality gain (§13's own P0-4
    caveat: native video's test output was SHORTER than its frame control)."""
    succ = [r for r in records if r["status"] == "success" and r.get("reference_words")]
    if not succ:
        return {"mean_prediction_reference_word_ratio": None}
    ratios = [r["prediction_words"] / r["reference_words"] for r in succ if r["reference_words"]]
    return {"mean_prediction_reference_word_ratio": round(sum(ratios) / len(ratios), 4) if ratios else None}


def build_corpus_summary(records: list[dict], all_manifest_ids: list[str]) -> dict:
    n_total = len(records)
    n_success = sum(1 for r in records if r["status"] == "success")
    n_failure = n_total - n_success
    summary = {
        "n_total": n_total,
        "n_success": n_success,
        "n_failure": n_failure,
    }
    summary.update(_corpus_wer_cer(records))
    summary.update(_corpus_timing(records))
    summary.update(_corpus_bleu_chrf(records))
    summary.update(_corpus_length_ratio(records))
    return summary


def aggregate(results_dir: Path, config_name: str, all_rows: list[dict]) -> None:
    per_clip_path = results_dir / "per_clip_results.json"
    if not per_clip_path.exists():
        raise SystemExit(f"No per_clip_results.json at {per_clip_path} — nothing to aggregate. Run the harness first.")
    records = json.loads(per_clip_path.read_text(encoding="utf-8"))

    all_ids = [r["how2sign_id"] for r in all_rows]
    matched = compute_matched_subset(all_ids)
    matched_id_set = set(matched["matched_ids"])

    all_summary = build_corpus_summary(records, all_ids)
    (results_dir / "corpus_summary.json").write_text(json.dumps(all_summary, indent=2), encoding="utf-8")

    matched_records = [r for r in records if r["how2sign_id"] in matched_id_set]
    matched_summary = build_corpus_summary(matched_records, matched["matched_ids"])
    matched_summary["_comparability"] = {
        "note": "Restricted to the exact clip IDs OpenSLT and Uni-Sign both successfully produced a "
                "prediction for. Only THIS summary is valid for direct Curify-native-video-vs-OpenSLT/"
                "Uni-Sign comparison; corpus_summary.json (all attempted clips) is NOT directly "
                "comparable whenever n_total there differs from this file's n_total.",
        "matched_count": matched["matched_count"],
        "excluded_count": matched["excluded_count"],
        "excluded_ids": matched["excluded_ids"],
        "excluded_from_openslt": matched["excluded_from_openslt"],
        "excluded_from_unisign": matched["excluded_from_unisign"],
        "openslt_source": matched["openslt_source"],
        "unisign_source": matched["unisign_source"],
        "n_of_matched_set_actually_scored_here": len(matched_records),
    }
    (results_dir / "corpus_summary_matched_126.json").write_text(
        json.dumps(matched_summary, indent=2), encoding="utf-8"
    )
    print(f"Wrote corpus_summary.json (n_total={all_summary['n_total']}) and "
          f"corpus_summary_matched_126.json (matched_count={matched['matched_count']}, "
          f"scored_here={len(matched_records)}) to {results_dir}")


def build_run_metadata(config_name: str, rows: list[dict], started_at: str) -> dict:
    cfg = run_native_video.CONFIGS[config_name]
    freeze_fp = FREEZE_FINGERPRINT_PATH.read_text(encoding="utf-8").strip() if FREEZE_FINGERPRINT_PATH.exists() else None
    return {
        "config": config_name,
        "model": cfg["model"],
        "modality": cfg["modality"],
        "temperature_label": cfg["temperature_label"],
        "thinking_level": cfg.get("thinking_level"),
        "prompt_sha256": run_native_video.native_video_prompt_sha256(),
        "prompt_diff_vs_production": run_native_video.prompt_diff_vs_production(),
        "benchmark": {
            "manifest": str(MANIFEST_PATH.relative_to(REPO_ROOT)),
            "freeze_sha256_fingerprint": freeze_fp,
            "total_clips_in_manifest": len(rows),
        },
        "run_timestamp_utc": started_at,
        "source_repo": run_native_video.SOURCE_REPO,
        "source_ref": run_native_video.SOURCE_REF,
        "source_commit": run_native_video.SOURCE_COMMIT,
        "source_file": run_native_video.SOURCE_FILE,
        "source_section": run_native_video.SOURCE_SECTION,
        "pre_registered_promotion_criterion": (
            "On the 12 diagnostic clips: >= 3 of 12 move from semantic_adequacy=0 to >= 1, OR "
            "reference_topic_mismatch flips yes -> no on >= 3 of 12 (source spec §7 P0-4). This "
            "harness does not compute semantic_adequacy itself -- that requires the same manual/"
            "LLM-assisted text-semantic review used for the existing taxonomy_40 set (Phase 3 of "
            "this task). Recorded here so the criterion travels with the run, not just the plan."
        ),
        "pre_registered_rejection_criterion": (
            "0/12 clips flip category AND the WER movement sits inside the pooled decoding-noise "
            "floor (source spec §12.2: mean |delta| 0.029-0.107 on architecturally inert clips) -> "
            "native video is not the answer either; record it and stop, do not scale to 128."
        ),
    }


def plan_only(config_name: str, rows: list[dict], results_dir: Path) -> None:
    plan = []
    total_size = 0
    for row in rows:
        clip_id = row["how2sign_id"]
        video_path = REPO_ROOT / row["local_video_path"]
        if not video_path.exists():
            plan.append({"how2sign_id": clip_id, "status": "missing_video"})
            continue
        report = run_native_video.run_dry(video_path, config_name)
        total_size += report.size_bytes
        plan.append({
            "how2sign_id": clip_id,
            "status": "planned",
            "duration_s": report.duration_s,
            "size_bytes": report.size_bytes,
            "expected_files_uploaded": report.expected_files_uploaded,
            "expected_model_calls": report.expected_model_calls,
        })
    out = {
        "config": config_name,
        "n_clips_planned": len(rows),
        "n_missing_video": sum(1 for p in plan if p["status"] == "missing_video"),
        "total_expected_gemini_calls": sum(p.get("expected_model_calls", 0) for p in plan),
        "total_expected_file_uploads": sum(p.get("expected_files_uploaded", 0) for p in plan),
        "total_upload_bytes": total_size,
        "note": "Computed entirely via run_native_video.run_dry() — no network call, "
                "no google.genai import, no GEMINI_API_KEY required.",
        "per_clip": plan,
    }
    results_dir.mkdir(parents=True, exist_ok=True)
    plan_path = results_dir / "plan.json"
    plan_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"PLAN ONLY — no model calls made.\n"
          f"  clips planned          : {len(rows)}\n"
          f"  missing video          : {out['n_missing_video']}\n"
          f"  total upload bytes     : {total_size} ({total_size / 1e6:.2f} MB)\n"
          f"  total expected calls   : {out['total_expected_gemini_calls']}\n"
          f"  wrote                  : {plan_path}")


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, choices=sorted(run_native_video.CONFIGS),
                     help="Which run_native_video.py CONFIGS entry to run. No default: always explicit.")
    ap.add_argument("--results-dir", default=None,
                     help="Output directory. Default: "
                          "asl-translator/evaluation/results/how2sign_v2/<name for this config>.")
    ap.add_argument("--limit", type=int, default=None,
                     help="Only run the first N manifest rows, in frozen manifest order.")
    ap.add_argument("--clip-ids", default=None,
                     help="Comma-separated how2sign_id list to run instead of the whole manifest.")
    ap.add_argument("--clip-ids-file", default=None,
                     help="Path to a JSON file listing clip ids (e.g. diagnostic_12_clips.json) to "
                          "run instead of the whole manifest. Mutually exclusive with --clip-ids.")
    ap.add_argument("--overwrite", action="store_true",
                     help="Re-run every selected clip even if a completed prediction for this exact "
                          "config already exists.")
    ap.add_argument("--max-retries", type=int, default=3,
                     help="Max attempts per clip for TRANSIENT errors only (429/5xx). Deterministic "
                          "4xx errors are never retried.")
    ap.add_argument("--retry-backoff-s", type=float, default=5.0,
                     help="Base backoff seconds; actual sleep is retry_backoff_s * attempt_number.")
    ap.add_argument("--sleep-between-clips-s", type=float, default=0.0,
                     help="Fixed pause after each clip, regardless of success/failure — rate-limit "
                          "friendliness for a long unattended run. 0 = no pause (default).")
    ap.add_argument("--keep-uploaded-file", action="store_true",
                     help="Do not delete each clip's file from the Files API after scoring it.")
    ap.add_argument("--file-state-poll-timeout-s", type=float, default=120.0)
    ap.add_argument("--run", action="store_true",
                     help="Required to start a real run. Without it (and without --plan-only or "
                          "--aggregate-only), this script does nothing but print an error — a real "
                          "run can never start merely by omitting --plan-only. Also requires "
                          "--acknowledge-private-data-upload and GEMINI_API_KEY. Mirrors "
                          "run_native_video.py's own --run gate.")
    ap.add_argument("--acknowledge-private-data-upload", action="store_true",
                     help="Required together with --run: confirms you understand that each selected "
                          "clip's WHOLE VIDEO FILE (not just sampled frames) will be uploaded to "
                          "Gemini's Files API and will leave this machine. Mirrors run_native_video.py's "
                          "own single-clip gate of the same name.")
    ap.add_argument("--plan-only", action="store_true",
                     help="Compute exact expected upload+call count via dry-run only. No network call, "
                          "no GEMINI_API_KEY required, no predictions written.")
    ap.add_argument("--aggregate-only", action="store_true",
                     help="Recompute corpus_summary.json / corpus_summary_matched_126.json from the "
                          "per_clip_results.json already on disk. No model calls.")
    return ap


def resolve_results_dir(config_name: str, override: Optional[str]) -> Path:
    if override:
        return Path(override).resolve()
    name = DEFAULT_RESULTS_DIR_NAME.get(config_name, f"curify_{config_name}")
    return REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / name


def main(argv: Optional[list[str]] = None) -> int:
    ap = build_arg_parser()
    args = ap.parse_args(argv)

    if args.clip_ids and args.clip_ids_file:
        ap.error("--clip-ids and --clip-ids-file are mutually exclusive")

    all_rows = load_manifest_rows()
    results_dir = resolve_results_dir(args.config, args.results_dir)

    clip_ids = None
    if args.clip_ids:
        clip_ids = args.clip_ids.split(",")
    elif args.clip_ids_file:
        clip_ids = load_clip_ids_file(args.clip_ids_file)

    if args.plan_only:
        rows = select_rows(all_rows, args.limit, clip_ids)
        plan_only(args.config, rows, results_dir)
        return 0

    if args.aggregate_only:
        aggregate(results_dir, args.config, all_rows)
        return 0

    if not args.run:
        print(
            "error: no action requested. Pass exactly one of --plan-only (zero network calls, see "
            "exactly what would be uploaded), --aggregate-only (rescore existing predictions), or "
            "--run (start a real run — also requires --acknowledge-private-data-upload and "
            "GEMINI_API_KEY). No network call was made.",
            file=sys.stderr,
        )
        return 2

    if not args.acknowledge_private_data_upload:
        print(
            "error: --run requires --acknowledge-private-data-upload. Each selected clip's WHOLE "
            "VIDEO FILE (not just sampled frames) will be uploaded to Gemini's Files API, off this "
            "machine. No network call was made. Use --plan-only first to see exactly what would be "
            "uploaded, with zero network calls and no GEMINI_API_KEY required.",
            file=sys.stderr,
        )
        return 2

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("error: GEMINI_API_KEY is not set. Refusing to start the run.", file=sys.stderr)
        return 2

    rows = select_rows(all_rows, args.limit, clip_ids)
    (results_dir / "predictions").mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc).isoformat()
    run_meta = build_run_metadata(args.config, all_rows, started_at)
    (results_dir / "run_metadata.json").write_text(json.dumps(run_meta, indent=2), encoding="utf-8")

    per_clip_path = results_dir / "per_clip_results.json"
    csv_path = results_dir / "per_clip_results.csv"
    if per_clip_path.exists() and not args.overwrite:
        try:
            existing = {r["how2sign_id"]: r for r in json.loads(per_clip_path.read_text(encoding="utf-8"))}
        except (json.JSONDecodeError, OSError):
            existing = {}
    else:
        existing = {}

    print(f"Running {len(rows)} clip(s) under config={args.config!r} -> {results_dir}")
    for i, row in enumerate(rows, 1):
        clip_id = row["how2sign_id"]
        print(f"[{i}/{len(rows)}] {clip_id}")
        rec = run_one_clip(row, args.config, results_dir, api_key, args.max_retries,
                            args.retry_backoff_s, args.overwrite, args.keep_uploaded_file,
                            args.file_state_poll_timeout_s)
        existing[clip_id] = rec
        records = [existing[r["how2sign_id"]] for r in all_rows if r["how2sign_id"] in existing]
        per_clip_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        _write_csv(csv_path, records)
        status = rec["status"]
        if status == "success":
            print(f"  OK   wer={rec['wer']} cer={rec['cer']} attempts={rec['attempts']}")
        else:
            print(f"  FAIL {rec['failure_reason']} (attempts={rec['attempts']})")
        if args.sleep_between_clips_s > 0 and i < len(rows):
            time.sleep(args.sleep_between_clips_s)

    n_success = sum(1 for r in records if r["status"] == "success")
    n_failure = len(records) - n_success
    run_meta["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    run_meta["total_clips_attempted_this_invocation"] = len(rows)
    run_meta["total_clips_in_results_file"] = len(records)
    run_meta["successful_clips"] = n_success
    run_meta["failed_clips"] = n_failure
    (results_dir / "run_metadata.json").write_text(json.dumps(run_meta, indent=2), encoding="utf-8")

    aggregate(results_dir, args.config, all_rows)
    print(f"\nDone. {n_success} succeeded, {n_failure} failed, out of {len(records)} total in results file.")
    return 0


def _write_csv(csv_path: Path, records: list[dict]) -> None:
    if not records:
        return
    flat_fields = [
        "how2sign_id", "status", "failure_reason", "attempts", "duration_s",
        "reference_text", "prediction_text", "wer", "cer",
        "reference_words", "prediction_words", "substitutions", "deletions", "insertions",
        "model_calls", "files_uploaded", "upload_wall_clock_s", "file_processing_wait_s",
        "generate_content_wall_clock_s", "thinking_level", "skipped_existing", "inference_wall_clock_s",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=flat_fields, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow(r)


if __name__ == "__main__":
    raise SystemExit(main())
