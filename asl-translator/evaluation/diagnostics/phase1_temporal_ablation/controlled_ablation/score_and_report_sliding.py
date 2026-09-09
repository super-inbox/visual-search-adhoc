#!/usr/bin/env python3
"""Score Arm A (reused baseline, independent batches) vs Arm B (new
overlapping-sliding-window predictions) for the 12 fixed diagnostic clips,
using the EXISTING, UNMODIFIED asl-eval/evaluate.py + lib.py scorer.

No model/API calls. No modification of any existing Phase-1/3A artifact.
"""
from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path("/Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c")
ASL_EVAL_DIR = REPO_ROOT / "asl-translator" / "asl-eval"
PHASE1_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "diagnostics" / "phase1_temporal_ablation"
DIAGNOSTIC_12_JSON = PHASE1_DIR / "diagnostic_12_clips.json"
MANIFEST_PATH = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2" / "manifest.csv"
BASELINE_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "curify_gemini_3_6_2026_09_04"
TEXT_SEMANTIC_JSON = PHASE1_DIR / "taxonomy_40_text_semantic_review.json"

OUT_DIR = PHASE1_DIR / "controlled_ablation" / "independent_vs_sliding"
SLIDING_PRED_DIR = OUT_DIR / "predictions"
OUT_CSV = OUT_DIR / "paired_results.csv"
OUT_JSON = OUT_DIR / "paired_results.json"

BASELINE_CONFIG = "evaluation_2026_09_04_gemini_3_6"
SLIDING_CONFIG = "phase3b_independent_vs_sliding_window24_stride12_2026_09_07"

sys.path.insert(0, str(ASL_EVAL_DIR))
import evaluate as evaluate_mod  # noqa: E402
import lib  # noqa: E402


def hint_bucket(tags: dict) -> str:
    if tags.get("fingerspelling_candidate"):
        return "fingerspelling_candidate"
    if tags.get("number_token"):
        return "number_token"
    if tags.get("fast_signing"):
        return "fast_signing"
    if tags.get("question"):
        return "question"
    return "plain_no_flag"


def main() -> None:
    diag = json.loads(DIAGNOSTIC_12_JSON.read_text(encoding="utf-8"))
    clip_ids = [c["clip_id"] for c in diag["clips"]]
    reason_selected = {c["clip_id"]: c.get("reason_selected") for c in diag["clips"]}
    heuristic_tags = {c["clip_id"]: c.get("manifest_heuristic_tags", {}) for c in diag["clips"]}
    assert len(clip_ids) == 12 and len(set(clip_ids)) == 12

    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        manifest = {r["how2sign_id"]: r for r in csv.DictReader(f)}

    text_review = {}
    if TEXT_SEMANTIC_JSON.exists():
        text_review = json.loads(TEXT_SEMANTIC_JSON.read_text(encoding="utf-8"))

    rows = []
    missing = []
    for clip_id in clip_ids:
        m = manifest[clip_id]
        ref_path = REPO_ROOT / m["local_reference_path"]
        base_pred_path = BASELINE_DIR / "predictions" / f"{clip_id}.json"
        slide_pred_path = SLIDING_PRED_DIR / f"{clip_id}.json"

        assert ref_path.exists()
        assert base_pred_path.exists(), f"baseline missing: {base_pred_path}"
        base_meta = json.loads(base_pred_path.read_text(encoding="utf-8"))["run_metadata"]
        assert base_meta.get("config") == BASELINE_CONFIG

        if not slide_pred_path.exists():
            missing.append(clip_id)
            continue
        slide_data = json.loads(slide_pred_path.read_text(encoding="utf-8"))
        slide_meta = slide_data["run_metadata"]
        assert slide_meta.get("config") == SLIDING_CONFIG, f"{clip_id}: unexpected config {slide_meta.get('config')!r}"
        assert slide_meta.get("frame_budget") == base_meta.get("frame_budget"), \
            f"{clip_id}: frame_budget mismatch between arms"
        assert slide_meta.get("frames_sampled") == base_meta.get("frames_sampled"), \
            f"{clip_id}: frames_sampled mismatch between arms"

        base_result = evaluate_mod.run(str(ref_path), str(base_pred_path), include_alignment=False)
        slide_result = evaluate_mod.run(str(ref_path), str(slide_pred_path), include_alignment=False)
        base_wer = base_result["text_metrics"]["wer"]
        slide_wer = slide_result["text_metrics"]["wer"]

        tsr = text_review.get(clip_id, {})
        n_baseline_batches = base_meta.get("model_calls")
        rows.append({
            "clip_id": clip_id,
            "reference": lib.build_transcript(lib.parse_srt(ref_path)),
            "baseline_prediction": lib.build_transcript(lib.parse_prediction_json(base_pred_path)),
            "sliding_prediction": lib.build_transcript(lib.parse_prediction_json(slide_pred_path)),
            "baseline_wer": base_wer,
            "sliding_wer": slide_wer,
            "wer_delta": round(slide_wer - base_wer, 4),
            "n_baseline_calls": n_baseline_batches,
            "n_sliding_calls": slide_meta.get("model_calls"),
            "n_sliding_windows": slide_meta.get("n_windows"),
            "is_multi_batch": (n_baseline_batches or 0) > 1,
            "duration_s": m.get("duration_s"),
            "manifest_hint_bucket": hint_bucket(heuristic_tags.get(clip_id, {})),
            "diagnostic_reason_selected": ";".join(reason_selected.get(clip_id) or []),
            "baseline_semantic_adequacy_llm_text_review": tsr.get("semantic_adequacy", ""),
            "baseline_reference_topic_mismatch_llm_text_review": tsr.get("reference_topic_mismatch", ""),
            "baseline_requires_asl_expert_review_llm_text_review": tsr.get("requires_asl_expert_review", ""),
        })

    if missing:
        print(f"NOT SCORING — {len(missing)} sliding-arm prediction(s) missing: {missing}")
        sys.exit(1)
    assert len(rows) == 12

    deltas = [r["wer_delta"] for r in rows]
    n_improved = sum(1 for d in deltas if d < -1e-9)
    n_worsened = sum(1 for d in deltas if d > 1e-9)
    n_unchanged = len(deltas) - n_improved - n_worsened

    total_ref_words_a = total_err_a = total_ref_words_b = total_err_b = 0
    for clip_id in clip_ids:
        ref_path = REPO_ROOT / manifest[clip_id]["local_reference_path"]
        ba = evaluate_mod.run(str(ref_path), str(BASELINE_DIR / "predictions" / f"{clip_id}.json"),
                               include_alignment=False)["text_metrics"]
        sb = evaluate_mod.run(str(ref_path), str(SLIDING_PRED_DIR / f"{clip_id}.json"),
                               include_alignment=False)["text_metrics"]
        total_ref_words_a += ba["reference_words"]
        total_err_a += ba["substitutions"] + ba["deletions"] + ba["insertions"]
        total_ref_words_b += sb["reference_words"]
        total_err_b += sb["substitutions"] + sb["deletions"] + sb["insertions"]

    corpus_wer_a = round(total_err_a / total_ref_words_a, 4) if total_ref_words_a else None
    corpus_wer_b = round(total_err_b / total_ref_words_b, 4) if total_ref_words_b else None
    mean_wer_a = round(statistics.mean(r["baseline_wer"] for r in rows), 4)
    mean_wer_b = round(statistics.mean(r["sliding_wer"] for r in rows), 4)
    median_delta = round(statistics.median(deltas), 4)

    multi_batch_rows = [r for r in rows if r["is_multi_batch"]]
    single_batch_rows = [r for r in rows if not r["is_multi_batch"]]

    def subset_stats(subset):
        if not subset:
            return {}
        return {
            "n": len(subset),
            "mean_baseline_wer": round(statistics.mean(r["baseline_wer"] for r in subset), 4),
            "mean_sliding_wer": round(statistics.mean(r["sliding_wer"] for r in subset), 4),
            "mean_delta": round(statistics.mean(r["wer_delta"] for r in subset), 4),
            "median_delta": round(statistics.median(r["wer_delta"] for r in subset), 4),
            "n_improved": sum(1 for r in subset if r["wer_delta"] < -1e-9),
            "n_worsened": sum(1 for r in subset if r["wer_delta"] > 1e-9),
            "n_unchanged": sum(1 for r in subset if abs(r["wer_delta"]) <= 1e-9),
        }

    hint_buckets = {}
    for r in rows:
        hint_buckets.setdefault(r["manifest_hint_bucket"], []).append(r)
    hint_bucket_stats = {b: subset_stats(rs) for b, rs in hint_buckets.items()}

    summary = {
        "n_clips": 12,
        "baseline_config": BASELINE_CONFIG,
        "sliding_config": SLIDING_CONFIG,
        "corpus_wer_baseline": corpus_wer_a,
        "corpus_wer_sliding": corpus_wer_b,
        "corpus_wer_delta": round(corpus_wer_b - corpus_wer_a, 4) if corpus_wer_a is not None else None,
        "mean_wer_baseline": mean_wer_a,
        "mean_wer_sliding": mean_wer_b,
        "mean_wer_delta": round(mean_wer_b - mean_wer_a, 4),
        "median_per_clip_wer_delta": median_delta,
        "n_improved": n_improved,
        "n_worsened": n_worsened,
        "n_unchanged": n_unchanged,
        "multi_batch_subset": subset_stats(multi_batch_rows),
        "single_batch_subset": subset_stats(single_batch_rows),
        "hint_bucket_subsets": hint_bucket_stats,
        "per_clip": rows,
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    fieldnames = ["clip_id", "reference", "baseline_prediction", "sliding_prediction",
                  "baseline_wer", "sliding_wer", "wer_delta",
                  "n_baseline_calls", "n_sliding_calls", "n_sliding_windows", "is_multi_batch",
                  "duration_s", "manifest_hint_bucket", "diagnostic_reason_selected",
                  "baseline_semantic_adequacy_llm_text_review",
                  "baseline_reference_topic_mismatch_llm_text_review",
                  "baseline_requires_asl_expert_review_llm_text_review"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_JSON}")
    print(f"corpus_wer_baseline={corpus_wer_a} corpus_wer_sliding={corpus_wer_b} delta={summary['corpus_wer_delta']}")
    print(f"mean_wer_baseline={mean_wer_a} mean_wer_sliding={mean_wer_b} delta={summary['mean_wer_delta']}")
    print(f"median per-clip delta = {median_delta}")
    print(f"improved={n_improved} worsened={n_worsened} unchanged={n_unchanged}")
    print(f"multi_batch subset (n={len(multi_batch_rows)}): {hint_bucket_stats if False else subset_stats(multi_batch_rows)}")
    print(f"single_batch subset (n={len(single_batch_rows)}): {subset_stats(single_batch_rows)}")
    for r in sorted(rows, key=lambda r: abs(r["wer_delta"]), reverse=True)[:6]:
        print(f"  {r['clip_id']:40s} baseline={r['baseline_wer']:.4f} sliding={r['sliding_wer']:.4f} "
              f"delta={r['wer_delta']:+.4f} multi_batch={r['is_multi_batch']}")


if __name__ == "__main__":
    main()
