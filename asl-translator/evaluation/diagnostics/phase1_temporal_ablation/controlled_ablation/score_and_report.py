#!/usr/bin/env python3
"""Score Arm A (reused baseline) vs Arm B (new uniform-arm predictions) for the
12 fixed diagnostic clips, using the EXISTING, UNMODIFIED asl-eval/evaluate.py
+ lib.py scorer (the same scorer used for every other result in this repo).

Reads:
  - baseline predictions (Arm A): curify_gemini_3_6_2026_09_04/predictions/*.json
    (read-only; never modified, never rerun by this script)
  - uniform predictions (Arm B): controlled_ablation/adaptive_vs_uniform_2fps/predictions/*.json
  - existing frozen references (manifest.csv -> local_reference_path)
  - the LLM-assisted text-semantic review of baseline predictions (descriptive
    context only, for Arm A; NOT computed or claimed for Arm B's predictions)

Writes:
  - paired_results.csv / .json (per-clip WER for both arms + deltas)
  - prints corpus WER / mean WER / median delta / improved-worsened-unchanged

No model/API calls. No modification of any existing Phase-1 artifact.
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

OUT_DIR = PHASE1_DIR / "controlled_ablation" / "adaptive_vs_uniform_2fps"
UNIFORM_PRED_DIR = OUT_DIR / "predictions"
OUT_CSV = OUT_DIR / "paired_results.csv"
OUT_JSON = OUT_DIR / "paired_results.json"

BASELINE_CONFIG = "evaluation_2026_09_04_gemini_3_6"
UNIFORM_CONFIG = "evaluation_2026_09_07_gemini_3_6_uniform_2fps"

sys.path.insert(0, str(ASL_EVAL_DIR))
import evaluate as evaluate_mod  # noqa: E402
import lib  # noqa: E402


def hint_bucket(tags: dict) -> str:
    """tags is diagnostic_12_clips.json's own per-clip manifest_heuristic_tags
    dict (already boolean-normalized there) -- NOT re-derived from the raw
    manifest.csv heuristic_* columns, to avoid a column-name mismatch."""
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
    missing_uniform = []
    for clip_id in clip_ids:
        m = manifest[clip_id]
        ref_path = REPO_ROOT / m["local_reference_path"]
        base_pred_path = BASELINE_DIR / "predictions" / f"{clip_id}.json"
        uni_pred_path = UNIFORM_PRED_DIR / f"{clip_id}.json"

        assert ref_path.exists(), f"reference missing: {ref_path}"
        assert base_pred_path.exists(), f"BASELINE prediction missing (must be reused, not rerun): {base_pred_path}"
        base_meta = json.loads(base_pred_path.read_text(encoding="utf-8")).get("run_metadata", {})
        assert base_meta.get("config") == BASELINE_CONFIG, \
            f"{clip_id}: baseline prediction config mismatch: {base_meta.get('config')!r}"

        if not uni_pred_path.exists():
            missing_uniform.append(clip_id)
            continue
        uni_meta = json.loads(uni_pred_path.read_text(encoding="utf-8")).get("run_metadata", {})
        assert uni_meta.get("config") == UNIFORM_CONFIG, \
            f"{clip_id}: uniform prediction config mismatch: {uni_meta.get('config')!r}"
        assert uni_meta.get("sampling_strategy") == "uniform", \
            f"{clip_id}: uniform prediction missing sampling_strategy=uniform tag"

        base_result = evaluate_mod.run(str(ref_path), str(base_pred_path), include_alignment=False)
        uni_result = evaluate_mod.run(str(ref_path), str(uni_pred_path), include_alignment=False)
        base_wer = base_result["text_metrics"]["wer"]
        uni_wer = uni_result["text_metrics"]["wer"]

        tsr = text_review.get(clip_id, {})
        rows.append({
            "clip_id": clip_id,
            "reference": lib.build_transcript(lib.parse_srt(ref_path)),
            "adaptive_prediction": lib.build_transcript(lib.parse_prediction_json(base_pred_path)),
            "uniform_prediction": lib.build_transcript(lib.parse_prediction_json(uni_pred_path)),
            "adaptive_wer": base_wer,
            "uniform_wer": uni_wer,
            "wer_delta": round(uni_wer - base_wer, 4),
            "adaptive_frames_sampled": base_meta.get("frames_sampled"),
            "uniform_frames_sampled": uni_meta.get("frames_sampled"),
            "adaptive_model_calls": base_meta.get("model_calls"),
            "uniform_model_calls": uni_meta.get("model_calls"),
            "manifest_hint_bucket": hint_bucket(heuristic_tags.get(clip_id, {})),
            "diagnostic_reason_selected": ";".join(reason_selected.get(clip_id) or []),
            "baseline_semantic_adequacy_llm_text_review": tsr.get("semantic_adequacy", ""),
            "baseline_reference_topic_mismatch_llm_text_review": tsr.get("reference_topic_mismatch", ""),
            "baseline_requires_asl_expert_review_llm_text_review": tsr.get("requires_asl_expert_review", ""),
        })

    if missing_uniform:
        print(f"NOT SCORING — {len(missing_uniform)} uniform-arm prediction(s) still missing: {missing_uniform}")
        print("Run run_uniform_arm.py for the remaining clips before scoring.")
        sys.exit(1)

    assert len(rows) == 12, f"expected 12 paired clips, got {len(rows)}"

    deltas = [r["wer_delta"] for r in rows]
    n_improved = sum(1 for d in deltas if d < -1e-9)
    n_worsened = sum(1 for d in deltas if d > 1e-9)
    n_unchanged = len(deltas) - n_improved - n_worsened

    total_ref_words_a = 0
    total_err_a = 0
    total_ref_words_b = 0
    total_err_b = 0
    for clip_id in clip_ids:
        ref_path = REPO_ROOT / manifest[clip_id]["local_reference_path"]
        base_pred_path = BASELINE_DIR / "predictions" / f"{clip_id}.json"
        uni_pred_path = UNIFORM_PRED_DIR / f"{clip_id}.json"
        ba = evaluate_mod.run(str(ref_path), str(base_pred_path), include_alignment=False)["text_metrics"]
        ub = evaluate_mod.run(str(ref_path), str(uni_pred_path), include_alignment=False)["text_metrics"]
        total_ref_words_a += ba["reference_words"]
        total_err_a += ba["substitutions"] + ba["deletions"] + ba["insertions"]
        total_ref_words_b += ub["reference_words"]
        total_err_b += ub["substitutions"] + ub["deletions"] + ub["insertions"]

    corpus_wer_a = round(total_err_a / total_ref_words_a, 4) if total_ref_words_a else None
    corpus_wer_b = round(total_err_b / total_ref_words_b, 4) if total_ref_words_b else None
    mean_wer_a = round(statistics.mean(r["adaptive_wer"] for r in rows), 4)
    mean_wer_b = round(statistics.mean(r["uniform_wer"] for r in rows), 4)
    median_delta = round(statistics.median(deltas), 4)

    summary = {
        "n_clips": 12,
        "baseline_config": BASELINE_CONFIG,
        "uniform_config": UNIFORM_CONFIG,
        "corpus_wer_adaptive": corpus_wer_a,
        "corpus_wer_uniform": corpus_wer_b,
        "corpus_wer_delta": round(corpus_wer_b - corpus_wer_a, 4) if corpus_wer_a is not None else None,
        "mean_wer_adaptive": mean_wer_a,
        "mean_wer_uniform": mean_wer_b,
        "mean_wer_delta": round(mean_wer_b - mean_wer_a, 4),
        "median_per_clip_wer_delta": median_delta,
        "n_improved": n_improved,
        "n_worsened": n_worsened,
        "n_unchanged": n_unchanged,
        "per_clip": rows,
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    fieldnames = ["clip_id", "reference", "adaptive_prediction", "uniform_prediction",
                  "adaptive_wer", "uniform_wer", "wer_delta",
                  "adaptive_frames_sampled", "uniform_frames_sampled",
                  "adaptive_model_calls", "uniform_model_calls",
                  "manifest_hint_bucket", "diagnostic_reason_selected",
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
    print(f"corpus_wer_adaptive = {corpus_wer_a}   corpus_wer_uniform = {corpus_wer_b}   delta = {summary['corpus_wer_delta']}")
    print(f"mean_wer_adaptive   = {mean_wer_a}   mean_wer_uniform   = {mean_wer_b}   delta = {summary['mean_wer_delta']}")
    print(f"median per-clip delta = {median_delta}")
    print(f"improved={n_improved} worsened={n_worsened} unchanged={n_unchanged}")
    for r in sorted(rows, key=lambda r: abs(r["wer_delta"]), reverse=True)[:5]:
        print(f"  {r['clip_id']:40s} adaptive={r['adaptive_wer']:.4f} uniform={r['uniform_wer']:.4f} "
              f"delta={r['wer_delta']:+.4f}")


if __name__ == "__main__":
    main()
