#!/usr/bin/env python3
"""Deterministically build the 40-clip stratified set for the Phase-1
qualitative error taxonomy, and emit a CSV/JSON annotation template with all
machine-available fields prefilled and every human-judgment column left
blank.

No inference is run. Reuses select_12_diagnostic_clips.py's loader (same
manifest + baseline A per_clip_results join) instead of re-implementing it.

Construction (deterministic, documented, no WER-only cherry-picking):
  1. The 12 clips from diagnostic_12_clips.json are included unconditionally
     (reason: "phase1_diagnostic_12").
  2. The remaining 28 slots are filled from manifest heuristic categories,
     modeled on the bucket names already used in
     evaluation/results/how2sign_v2/openslt/category_breakdown.json so this
     taxonomy sample can be cross-referenced against that precedent:
       number_token_HEURISTIC            6
       proper_noun_fingerspelling_HEURISTIC 6
       fast_signing_HEURISTIC            4
       question_official                 4
       duration_15-31s (long, extra multi-batch coverage beyond the 12) 3
       duration_lt_2s (near the MIN_FRAME_BUDGET floor)  2
       plain_no_flag (control group: no heuristic tag at all)  3
     Within each category, candidates NOT already selected are ranked by
     how2sign_id ascending (ties are impossible) — i.e. plain alphabetical,
     NOT by WER — precisely so this expansion doesn't just re-derive another
     worst-WER list on top of the 12 that already covered the WER extremes.

Human annotation columns (content tags, failure tags, semantic_adequacy,
hallucination, fps_might_help, batch_boundary_might_help, notes) are emitted
EMPTY. Manifest heuristics are surfaced as separate `hint_*` columns — they
describe the ENGLISH REFERENCE TEXT (a number word, a proper noun, a fast
words-per-second rate), not confirmed visual content of the sign video, so
they are hints for the human reviewer, not prefilled answers.

Run:
    python3 asl-translator/evaluation/diagnostics/phase1_temporal_ablation/select_40_taxonomy_clips.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import select_12_diagnostic_clips as diag12  # noqa: E402 reuse the loader, not reimplement it

REPO_ROOT = diag12.REPO_ROOT
DIAGNOSTIC_JSON = HERE / "diagnostic_12_clips.json"
OUT_JSON = HERE / "taxonomy_40_clips.json"
OUT_CSV = HERE / "taxonomy_40_clips.csv"

CONTENT_TAG_COLUMNS = [
    "handshape_sensitive", "motion", "fingerspelling", "numbers",
    "facial_non_manual", "fast_signing", "other",
]
FAILURE_TAG_COLUMNS = [
    "handshape", "motion", "fingerspelling", "numbers", "facial_non_manual",
    "segmentation", "hallucinated_topic", "repetition",
    "correct_meaning_different_english", "other",
]
SEMANTIC_COLUMNS = [
    "semantic_adequacy",  # 0/1/2, human
    "hallucination",  # yes/no, human
    "fps_might_help",  # yes/no/uncertain, human
    "batch_boundary_might_help",  # yes/no/uncertain, human
    "notes",  # free text, human
]


def duration_bucket(d: float) -> str:
    if d < 2:
        return "duration_lt_2s"
    if d < 5:
        return "duration_2-5s"
    if d < 15:
        return "duration_5-15s"
    return "duration_15-31s"


def build_categories(joined: dict, exclude: set) -> dict:
    def avail(pred):
        return sorted(
            [cid for cid in joined if cid not in exclude and pred(joined[cid])],
            key=lambda cid: cid,
        )

    return {
        "number_token_HEURISTIC": (
            avail(lambda r: diag12.is_yes(r["heuristics"]["heuristic_contains_number_token"])), 6),
        "proper_noun_fingerspelling_HEURISTIC": (
            avail(lambda r: diag12.is_yes(r["heuristics"]["heuristic_proper_noun_or_acronym_fingerspelling_candidate"])), 6),
        "fast_signing_HEURISTIC": (
            avail(lambda r: diag12.is_yes(r["heuristics"]["heuristic_fast_signing_wps_ge_p90"])), 4),
        "question_official": (
            avail(lambda r: diag12.is_yes(r["heuristics"]["official_ends_with_question_mark"])), 4),
        "duration_15-31s": (
            avail(lambda r: duration_bucket(r["duration_s"]) == "duration_15-31s"), 3),
        "duration_lt_2s": (
            avail(lambda r: duration_bucket(r["duration_s"]) == "duration_lt_2s"), 2),
        "plain_no_flag": (
            avail(lambda r: not any([
                diag12.is_yes(r["heuristics"]["heuristic_contains_number_token"]),
                diag12.is_yes(r["heuristics"]["heuristic_proper_noun_or_acronym_fingerspelling_candidate"]),
                diag12.is_yes(r["heuristics"]["heuristic_fast_signing_wps_ge_p90"]),
                diag12.is_yes(r["heuristics"]["official_ends_with_question_mark"]),
            ])), 3),
    }


def select_40(joined: dict, twelve: list[dict]) -> list[dict]:
    selected = [c["clip_id"] for c in twelve]
    reasons = {c["clip_id"]: ["phase1_diagnostic_12"] for c in twelve}

    categories = build_categories(joined, exclude=set(selected))
    for cat_name, (candidates, quota) in categories.items():
        taken = 0
        for cid in candidates:
            if taken >= quota:
                break
            if cid in selected:
                continue
            selected.append(cid)
            reasons[cid] = [cat_name]
            taken += 1
        if taken < quota:
            print(f"WARNING: category {cat_name!r} only had {taken}/{quota} available after exclusions")

    assert len(selected) == 40, f"expected 40 clips, got {len(selected)}"
    return [{"clip_id": cid, "reason_selected": reasons[cid]} for cid in selected]


def main() -> None:
    joined = diag12.load_joined_rows()
    twelve = json.loads(DIAGNOSTIC_JSON.read_text(encoding="utf-8"))["clips"]
    picks = select_40(joined, twelve)

    records = []
    for p in picks:
        cid = p["clip_id"]
        row = joined[cid]
        h = row["heuristics"]
        rec = {
            "clip_id": cid,
            "duration_s": row["duration_s"],
            "duration_bucket": duration_bucket(row["duration_s"]),
            "reference": row["reference_text"],
            "baseline_prediction": row["baseline_prediction_text"],
            "baseline_wer": row["wer"],
            "frames_sampled": row["frames_sampled"],
            "model_calls_baseline": row["model_calls"],
            "n_batches_baseline": row["model_calls"],  # 1 model call == 1 batch in run_real()
            "sampling_density_fps_baseline": row["sampling_density_fps"],
            "hint_number_token": diag12.is_yes(h["heuristic_contains_number_token"]),
            "hint_fingerspelling_candidate": diag12.is_yes(h["heuristic_proper_noun_or_acronym_fingerspelling_candidate"]),
            "hint_fast_signing": diag12.is_yes(h["heuristic_fast_signing_wps_ge_p90"]),
            "hint_question": diag12.is_yes(h["official_ends_with_question_mark"]),
            "reason_selected": p["reason_selected"],
            "in_phase1_12clip_inspector": "phase1_diagnostic_12" in p["reason_selected"],
        }
        for c in CONTENT_TAG_COLUMNS:
            rec[f"content__{c}"] = ""
        for c in FAILURE_TAG_COLUMNS:
            rec[f"failure__{c}"] = ""
        for c in SEMANTIC_COLUMNS:
            rec[c] = ""
        records.append(rec)

    OUT_JSON.write_text(json.dumps({
        "n_selected": len(records),
        "selection_method": "select_40_taxonomy_clips.py — 12 fixed diagnostic clips + 28 "
                             "category-stratified (alphabetical within category, not WER-ranked)",
        "content_tag_columns": CONTENT_TAG_COLUMNS,
        "failure_tag_columns": FAILURE_TAG_COLUMNS,
        "semantic_columns": SEMANTIC_COLUMNS,
        "human_annotation_note": "content__*, failure__*, and the semantic columns are intentionally "
                                  "blank — human visual/semantic judgment only. hint_* columns are "
                                  "machine-derived from manifest.csv text/WPS heuristics on the "
                                  "REFERENCE TEXT, not confirmed visual content; they are hints, not "
                                  "prefilled answers.",
        "clips": records,
    }, indent=2), encoding="utf-8")

    fieldnames = (
        ["clip_id", "duration_s", "duration_bucket", "reference", "baseline_prediction",
         "baseline_wer", "frames_sampled", "model_calls_baseline", "n_batches_baseline",
         "sampling_density_fps_baseline", "hint_number_token", "hint_fingerspelling_candidate",
         "hint_fast_signing", "hint_question", "in_phase1_12clip_inspector", "reason_selected"]
        + [f"content__{c}" for c in CONTENT_TAG_COLUMNS]
        + [f"failure__{c}" for c in FAILURE_TAG_COLUMNS]
        + SEMANTIC_COLUMNS
    )
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in records:
            row = dict(r)
            row["reason_selected"] = ";".join(row["reason_selected"])
            w.writerow(row)

    print(f"Wrote {OUT_JSON} and {OUT_CSV} ({len(records)} clips)")
    by_reason: dict[str, int] = {}
    for r in records:
        for reason in r["reason_selected"]:
            by_reason[reason] = by_reason.get(reason, 0) + 1
    for k, v in by_reason.items():
        print(f"  {k:45s} {v}")


if __name__ == "__main__":
    main()
