#!/usr/bin/env python3
"""Run the Curify/Gemini ASL pipeline across the frozen How2Sign v2 benchmark
(128 clips) and score every prediction with the existing, UNMODIFIED
asl-eval/evaluate.py + lib.py.

This file adds NO new sampling/prompt/model/metric logic of its own. It is a
thin sequential loop around two already-existing, already-verified pieces:

  - asl-translator/asl-eval/run_current_model.py  (production-equivalent
    inference — same PRODUCTION_PROMPT, motion probe, TARGET_FRAMES_PER_SEC,
    BATCH_SIZE, dedup, response schema for every --config)
  - asl-translator/asl-eval/evaluate.py / lib.py   (WER/CER/timing scoring,
    same normalization as every other model scored against this benchmark)

Neither of those files, nor the frozen benchmark's manifest/references/videos,
is modified or imported-and-monkeypatched by this script.

────────────────────────────────────────────────────────────────────────────
Config selection
────────────────────────────────────────────────────────────────────────────
--config is REQUIRED (no default) — you always say explicitly which
CONFIGS entry from run_current_model.py you mean. `production_2026_08_29`
(gemini-2.5-flash) is BLOCKED for the currently provisioned credential — see
CONFIG_STATUS in run_current_model.py and
docs/daily_report/9.2/asl-baselines/GEMINI_PHASE3A_CREDENTIAL_BLOCKER.md.
The runnable baseline today is `evaluation_2026_09_04_gemini_3_6`
(gemini-3.6-flash), and MUST NEVER be reported as production_2026_08_29 —
every output file this script writes carries its own `config` field so the
two are never conflated.

────────────────────────────────────────────────────────────────────────────
Resume / retry / failure handling
────────────────────────────────────────────────────────────────────────────
- Each clip's prediction is written to `<results_dir>/predictions/<id>.json`
  IMMEDIATELY after that clip completes (this is exactly what
  run_current_model.run_real() already does — this script just points it at
  a per-clip path). per_clip_results.json/.csv are rewritten in full after
  EVERY clip, so an interrupted run leaves a valid, inspectable "results so
  far" file, not a half-written one.
- On the next invocation with the same --results-dir and --config, a clip
  whose prediction file already exists AND whose own
  `run_metadata.config == this run's --config` is SKIPPED by default (logged
  as "SKIP (already completed)"). A prediction saved under a DIFFERENT
  config is never silently reused or rescored as if it were this run's
  config — it is treated as "not completed for this config" and regenerated
  (overwriting only that clip's file). Pass --overwrite to force every
  requested clip to re-run regardless of what is on disk.
- Retries are ONLY attempted for transient failures: HTTP 429 (rate limit)
  and 5xx (server-side), plus local connection/timeout errors. A
  deterministic 4xx (400 bad request, 401/403 auth, 404 model-not-available
  — exactly what production_2026_08_29 hits today) is recorded as a failure
  on the FIRST attempt and is never retried, since retrying cannot change a
  deterministic rejection. --max-retries / --retry-backoff-s control this.
- A failure never aborts the corpus run. It is recorded in
  per_clip_results.json with status="failed", a sanitized failure_reason
  (API key value is never included — see redact()), and the attempt count.
  The one exception: a missing GEMINI_API_KEY aborts immediately, once,
  before touching any clip — there is no point recording 128 identical
  "no key" failures.

────────────────────────────────────────────────────────────────────────────
Execution model
────────────────────────────────────────────────────────────────────────────
Strictly sequential, one clip at a time, one batch at a time within a clip
(exactly run_current_model.run_real()'s own loop) — no concurrency was added.
Nothing in this script changes FPS, frame sampling, batching, dedup, the
prompt, the model, thinking_level, or evaluate.py's normalization; it only
orchestrates calls to the existing, unmodified functions across all clips.

────────────────────────────────────────────────────────────────────────────
Known, pre-existing, NOT fixed here
────────────────────────────────────────────────────────────────────────────
run_current_model.py's dry-run duration (ffprobe, `probe_duration()`) and
its real-run duration (the motion probe's own last timestamp, `times[-1]`)
can differ by roughly one probe frame (~0.25s at PROBE_FPS=4.0), which can
shift the duration-scaled frame budget by ±1 frame between a --plan-only
estimate and the real run for the same clip. This is existing behavior of
the unmodified run_current_model.py used identically by every config
(baseline0/temperature0/production_2026_08_29/evaluation_2026_09_04_gemini_3_6)
and is documented, not patched, so the baseline stays unchanged.

────────────────────────────────────────────────────────────────────────────
Usage
────────────────────────────────────────────────────────────────────────────
Plan only (zero network calls, exact expected Gemini call count for the
whole frozen benchmark under this config):

    python3 asl-translator/evaluation/run_curify_how2sign_v2_benchmark.py \\
        --config evaluation_2026_09_04_gemini_3_6 --plan-only

Run 2 clips (validation), real Gemini calls:

    python3 asl-translator/evaluation/run_curify_how2sign_v2_benchmark.py \\
        --config evaluation_2026_09_04_gemini_3_6 --limit 2

Resume (already-completed clips are skipped):

    python3 asl-translator/evaluation/run_curify_how2sign_v2_benchmark.py \\
        --config evaluation_2026_09_04_gemini_3_6 --limit 2

Recompute corpus_summary.json etc. from what's already on disk, no model
calls at all:

    python3 asl-translator/evaluation/run_curify_how2sign_v2_benchmark.py \\
        --config evaluation_2026_09_04_gemini_3_6 --aggregate-only

Full frozen benchmark (128 clips) — NOT run by this task, listed for the
future step this harness is being built for:

    python3 asl-translator/evaluation/run_curify_how2sign_v2_benchmark.py \\
        --config evaluation_2026_09_04_gemini_3_6
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
    "evaluation_2026_09_04_gemini_3_6": "curify_gemini_3_6_2026_09_04",
    # Experiment B (temporal-sampling ablation, 8 fps target) — its own
    # directory so it can never reuse or overwrite frozen baseline-A
    # predictions/results, which live under curify_gemini_3_6_2026_09_04/.
    "evaluation_2026_09_06_gemini_3_6_8fps": "curify_gemini_3_6_2026_09_06_8fps",
}

sys.path.insert(0, str(ASL_EVAL_DIR))
import run_current_model  # noqa: E402
import evaluate as evaluate_mod  # noqa: E402
import lib  # noqa: E402

TRANSIENT_HTTP_CODES = {429, 500, 502, 503, 504}


# ─────────────────────────────────────────────────────────────────────────
# Credential hygiene — never let a key value reach any file this script
# writes, even inside a sanitized exception message.
# ─────────────────────────────────────────────────────────────────────────
_KEY_LOOKALIKE_RE = re.compile(r"AIza[0-9A-Za-z_\-]{10,}")


def redact(text: str, secret: Optional[str]) -> str:
    if secret:
        text = text.replace(secret, "[REDACTED_API_KEY]")
    text = _KEY_LOOKALIKE_RE.sub("[REDACTED_KEY_LOOKALIKE]", text)
    return text


def classify_error(exc: BaseException) -> tuple[bool, Optional[int]]:
    """(is_transient, http_status_code_if_known)."""
    code = getattr(exc, "code", None)
    if not isinstance(code, int):
        code = getattr(exc, "status_code", None)
    if isinstance(code, int) and code in TRANSIENT_HTTP_CODES:
        return True, code
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return True, code if isinstance(code, int) else None
    return False, code if isinstance(code, int) else None


# ─────────────────────────────────────────────────────────────────────────
# Frozen manifest — iterate in file order, never by filesystem listing.
# ─────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────
# Comparability: the exact matched subset OpenSLT/Uni-Sign results support.
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
        # reference_text / prediction_text are filled in by the caller
        # (run_one_clip) via lib.build_transcript, not here.
        "reference_words": tm["reference_words"],
        "prediction_words": tm["prediction_words"],
        "substitutions": tm["substitutions"],
        "deletions": tm["deletions"],
        "insertions": tm["insertions"],
        "wer": tm["wer"],
        "cer": tm["cer"],
        "char_level": tm["char_level"],
        "timing_metrics": ti,
        "frames_sampled": meta.get("frames_sampled"),
        "model_calls": meta.get("model_calls"),
        "sampling_density_fps": meta.get("sampling_density_fps"),
        "low_density": meta.get("low_density"),
        "degenerate_repetition": meta.get("degenerate_repetition"),
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
            run_current_model.run_real(video_path, config_name, None, pred_path)
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
        "frames_sampled": None,
        "model_calls": None,
        "sampling_density_fps": None,
        "low_density": None,
        "degenerate_repetition": None,
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
# Corpus-level aggregation (also runnable standalone, no model calls)
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
                "prediction for. Only THIS summary is valid for direct Curify-vs-OpenSLT/Uni-Sign "
                "comparison; corpus_summary.json (all attempted clips) is NOT directly comparable "
                "whenever n_total there differs from this file's n_total.",
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


# ─────────────────────────────────────────────────────────────────────────
# Run metadata (written at start, refreshed at end)
# ─────────────────────────────────────────────────────────────────────────
def build_run_metadata(config_name: str, rows: list[dict], started_at: str) -> dict:
    cfg = run_current_model.CONFIGS[config_name]
    status = run_current_model.CONFIG_STATUS.get(config_name, {})
    freeze_fp = FREEZE_FINGERPRINT_PATH.read_text(encoding="utf-8").strip() if FREEZE_FINGERPRINT_PATH.exists() else None
    return {
        "config": config_name,
        "config_status": status,
        "model": cfg["model"],
        "temperature_label": cfg["temperature_label"],
        "thinking_level": cfg.get("thinking_level"),
        "budget_mode": cfg["budget_mode"],
        "dedup": cfg["dedup"],
        "prompt_sha256": run_current_model.prompt_sha256(),
        "frame_policy": {
            "probe_fps": run_current_model.PROBE_FPS,
            "idle_quantile": run_current_model.IDLE_QUANTILE,
            "abs_motion_floor": run_current_model.ABS_MOTION_FLOOR,
            # Per-config resolved density, not the bare module constant — that
            # constant stays 2.0 for every config; a config (e.g. this
            # ablation's 8fps arm) overrides it via CONFIGS[name]["target_frames_per_sec"].
            "target_frames_per_sec": run_current_model.resolve_target_fps(config_name),
            "min_frame_budget": run_current_model.MIN_FRAME_BUDGET,
            "max_frame_budget": run_current_model.MAX_FRAME_BUDGET,
            "keyframe_width": run_current_model.KEYFRAME_WIDTH,
            "batch_size": run_current_model.BATCH_SIZE,
            "density_floor_fps": run_current_model.DENSITY_FLOOR_FPS,
            "dedup_max_gap_s": run_current_model.DEDUP_MAX_GAP_S,
        },
        "benchmark": {
            "manifest": str(MANIFEST_PATH.relative_to(REPO_ROOT)),
            "freeze_sha256_fingerprint": freeze_fp,
            "total_clips_in_manifest": len(rows),
        },
        "run_timestamp_utc": started_at,
        "source_repo": run_current_model.SOURCE_REPO,
        "source_ref": run_current_model.SOURCE_REF,
        "source_commit": run_current_model.SOURCE_COMMIT,
        "source_file": run_current_model.SOURCE_FILE,
        "known_pre_existing_behavior": (
            "run_current_model.py's dry-run duration (ffprobe) and real-run duration "
            "(motion-probe last timestamp) can differ by ~0.25s / 1 probe frame at "
            "PROBE_FPS=4.0, shifting the duration-scaled frame budget by up to 1 frame "
            "between a --plan-only estimate and the real run for the same clip. "
            "Pre-existing in the unmodified pipeline; not fixed here so the baseline "
            "stays unchanged."
        ),
        "repetition_loop_rate_and_number_recovery": (
            "NOT implemented in this harness. OpenSLT's failure_analysis.json reports "
            "repetition_loop_rate / number_recovery_rate, but no reusable function "
            "computing them exists anywhere in this repo (they were computed ad hoc for "
            "that report) — there is nothing to formally reuse. Implementing them here "
            "would require newly defining: (1) a repeated-n-gram detection rule "
            "(n-gram length, minimum repeat count, whether counted pre- or post-dedup) "
            "and (2) a number-token extraction + match rule (digits vs. number-words, "
            "how a 'recovered' match is defined against the reference). Silently "
            "inventing either definition now would produce a number that looks "
            "comparable to OpenSLT's but isn't measuring the same thing."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────
# --plan-only: exact expected Gemini call count, zero network calls.
# ─────────────────────────────────────────────────────────────────────────
def plan_only(config_name: str, rows: list[dict], results_dir: Path) -> None:
    plan = []
    total_calls = 0
    total_frames = 0
    for row in rows:
        clip_id = row["how2sign_id"]
        video_path = REPO_ROOT / row["local_video_path"]
        if not video_path.exists():
            plan.append({"how2sign_id": clip_id, "status": "missing_video"})
            continue
        report = run_current_model.run_dry(video_path, config_name, None, extract=False, keep_frames_dir=None)
        total_calls += report.expected_model_calls
        total_frames += report.sampled_frame_count
        plan.append({
            "how2sign_id": clip_id,
            "status": "planned",
            "duration_s": report.duration_s,
            "frame_budget": report.frame_budget,
            "sampled_frame_count": report.sampled_frame_count,
            "expected_model_calls": report.expected_model_calls,
            "sampling_density_fps": report.sampling_density_fps,
            "low_density": report.low_density,
        })
    out = {
        "config": config_name,
        "n_clips_planned": len(rows),
        "n_missing_video": sum(1 for p in plan if p["status"] == "missing_video"),
        "total_expected_gemini_calls": total_calls,
        "total_sampled_frames": total_frames,
        "note": "Computed entirely via run_current_model.run_dry() — no network call, "
                "no google.genai import, no GEMINI_API_KEY required.",
        "per_clip": plan,
    }
    results_dir.mkdir(parents=True, exist_ok=True)
    plan_path = results_dir / "plan.json"
    plan_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"PLAN ONLY — no model calls made.\n"
          f"  clips planned          : {len(rows)}\n"
          f"  missing video          : {out['n_missing_video']}\n"
          f"  total sampled frames   : {total_frames}\n"
          f"  total expected calls   : {total_calls}\n"
          f"  wrote                  : {plan_path}")


# ─────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────
def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, choices=sorted(run_current_model.CONFIGS),
                     help="Which run_current_model.py CONFIGS entry to run. No default: always explicit.")
    ap.add_argument("--results-dir", default=None,
                     help="Output directory. Default: "
                          "asl-translator/evaluation/results/how2sign_v2/<name for this config>.")
    ap.add_argument("--limit", type=int, default=None,
                     help="Only run the first N manifest rows, in frozen manifest order.")
    ap.add_argument("--clip-ids", default=None,
                     help="Comma-separated how2sign_id list to run instead of the whole manifest.")
    ap.add_argument("--overwrite", action="store_true",
                     help="Re-run every selected clip even if a completed prediction for this exact "
                          "config already exists.")
    ap.add_argument("--max-retries", type=int, default=3,
                     help="Max attempts per clip for TRANSIENT errors only (429/5xx). Deterministic "
                          "4xx errors are never retried.")
    ap.add_argument("--retry-backoff-s", type=float, default=5.0,
                     help="Base backoff seconds; actual sleep is retry_backoff_s * attempt_number.")
    ap.add_argument("--plan-only", action="store_true",
                     help="Compute exact expected Gemini call count via dry-run only. No network call, "
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

    all_rows = load_manifest_rows()
    results_dir = resolve_results_dir(args.config, args.results_dir)

    if args.plan_only:
        rows = select_rows(all_rows, args.limit, args.clip_ids.split(",") if args.clip_ids else None)
        plan_only(args.config, rows, results_dir)
        return 0

    if args.aggregate_only:
        aggregate(results_dir, args.config, all_rows)
        return 0

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("error: GEMINI_API_KEY is not set. Refusing to start the run.", file=sys.stderr)
        return 2

    rows = select_rows(all_rows, args.limit, args.clip_ids.split(",") if args.clip_ids else None)
    (results_dir / "predictions").mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc).isoformat()
    run_meta = build_run_metadata(args.config, all_rows, started_at)
    (results_dir / "run_metadata.json").write_text(json.dumps(run_meta, indent=2), encoding="utf-8")

    per_clip_path = results_dir / "per_clip_results.json"
    csv_path = results_dir / "per_clip_results.csv"
    records: list[dict] = []
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
                            args.retry_backoff_s, args.overwrite)
        existing[clip_id] = rec
        # Preserve frozen manifest order in the written files regardless of --clip-ids order.
        records = [existing[r["how2sign_id"]] for r in all_rows if r["how2sign_id"] in existing]
        per_clip_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        _write_csv(csv_path, records)
        status = rec["status"]
        if status == "success":
            print(f"  OK   wer={rec['wer']} cer={rec['cer']} attempts={rec['attempts']}")
        else:
            print(f"  FAIL {rec['failure_reason']} (attempts={rec['attempts']})")

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
        "frames_sampled", "model_calls", "sampling_density_fps", "low_density",
        "degenerate_repetition", "thinking_level", "skipped_existing", "inference_wall_clock_s",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=flat_fields, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow(r)


if __name__ == "__main__":
    raise SystemExit(main())
