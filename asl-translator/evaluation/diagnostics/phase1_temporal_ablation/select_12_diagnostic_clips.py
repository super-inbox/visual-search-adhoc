#!/usr/bin/env python3
"""Deterministically select 12 diagnostic clips from the frozen How2Sign v2
benchmark, using only files already on disk: the manifest and baseline A's
(evaluation_2026_09_04_gemini_3_6, 128/128) per_clip_results.

No inference is run. No files outside this diagnostics directory are written.

Selection is done by six fixed categories, applied in priority order below.
Each category ranks the full 128-clip pool deterministically (numeric key,
ties broken by how2sign_id ascending) and contributes up to 2 NEW clips
(skipping any already selected by an earlier, higher-priority category) so
overlap between categories is allowed but the final set has exactly 12
distinct clips. This intentionally avoids a worst-WER-only sample.

Categories (2 slots each, 12 total):
  1. long/multi-batch (batch-boundary risk): most model_calls, then longest
     duration_s. A clip crossing more batch boundaries is the strongest
     candidate for the "seams lose signs" failure mode from the frame
     inspector.
  2. fingerspelling candidate (manifest heuristic), ranked by WER desc.
  3. number-token clip (manifest heuristic), ranked by WER desc.
  4. fast-signing OR question clip (manifest heuristics), ranked by WER desc.
  5. very-high-WER clip, regardless of tag, ranked by WER desc (global).
  6. low-WER contrast clip, ranked by WER asc (global) — NOT cherry-picking
     only failures.

Run:
    python3 asl-translator/evaluation/diagnostics/phase1_temporal_ablation/select_12_diagnostic_clips.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
MANIFEST_PATH = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2" / "manifest.csv"
BASELINE_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "curify_gemini_3_6_2026_09_04"
PER_CLIP_CSV = BASELINE_DIR / "per_clip_results.csv"
OUT_DIR = Path(__file__).resolve().parent
OUT_JSON = OUT_DIR / "diagnostic_12_clips.json"
OUT_CSV = OUT_DIR / "diagnostic_12_clips.csv"

BASELINE_CONFIG = "evaluation_2026_09_04_gemini_3_6"
BASELINE_RESULTS_DIR = "curify_gemini_3_6_2026_09_04"

HEURISTIC_COLS = [
    "heuristic_contains_number_token",
    "heuristic_proper_noun_or_acronym_fingerspelling_candidate",
    "heuristic_fast_signing_wps_ge_p90",
    "official_ends_with_question_mark",
]


def is_yes(v: str) -> bool:
    return (v or "").strip().lower().startswith("yes")


def load_joined_rows() -> dict:
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        manifest = {r["how2sign_id"]: r for r in csv.DictReader(f)}
    with PER_CLIP_CSV.open(newline="", encoding="utf-8") as f:
        results = {r["how2sign_id"]: r for r in csv.DictReader(f)}
    missing = set(manifest) - set(results)
    if missing:
        raise SystemExit(f"per_clip_results.csv missing rows for: {sorted(missing)}")
    joined = {}
    for cid, m in manifest.items():
        r = results[cid]
        joined[cid] = {
            "how2sign_id": cid,
            "duration_s": float(m["duration_s"]),
            "reference_text": m["reference_text"],
            "wer": float(r["wer"]) if r["wer"] not in ("", None) else None,
            "frames_sampled": int(r["frames_sampled"]) if r["frames_sampled"] else None,
            "model_calls": int(r["model_calls"]) if r["model_calls"] else None,
            "sampling_density_fps": float(r["sampling_density_fps"]) if r["sampling_density_fps"] else None,
            "baseline_prediction_text": r["prediction_text"],
            "heuristics": {c: m[c] for c in HEURISTIC_COLS},
            "manifest_row": m,
            "per_clip_row": r,
        }
    return joined


def category_ranked_ids(joined: dict) -> dict:
    all_ids = list(joined)

    def sortable_wer(cid, default):
        w = joined[cid]["wer"]
        return w if w is not None else default

    cat1 = sorted(
        all_ids,
        key=lambda cid: (
            -(joined[cid]["model_calls"] or 0),
            -joined[cid]["duration_s"],
            cid,
        ),
    )
    cat2 = sorted(
        [cid for cid in all_ids if is_yes(joined[cid]["heuristics"]["heuristic_proper_noun_or_acronym_fingerspelling_candidate"])],
        key=lambda cid: (-sortable_wer(cid, -1.0), cid),
    )
    cat3 = sorted(
        [cid for cid in all_ids if is_yes(joined[cid]["heuristics"]["heuristic_contains_number_token"])],
        key=lambda cid: (-sortable_wer(cid, -1.0), cid),
    )
    cat4 = sorted(
        [cid for cid in all_ids if is_yes(joined[cid]["heuristics"]["heuristic_fast_signing_wps_ge_p90"])
         or is_yes(joined[cid]["heuristics"]["official_ends_with_question_mark"])],
        key=lambda cid: (-sortable_wer(cid, -1.0), cid),
    )
    cat5 = sorted(all_ids, key=lambda cid: (-sortable_wer(cid, -1.0), cid))
    cat6 = sorted(
        [cid for cid in all_ids if joined[cid]["wer"] is not None],
        key=lambda cid: (joined[cid]["wer"], cid),
    )
    return {
        "long_multi_batch_boundary_risk": cat1,
        "fingerspelling_candidate": cat2,
        "number_token": cat3,
        "fast_signing_or_question": cat4,
        "very_high_wer": cat5,
        "low_wer_contrast": cat6,
    }


def select(joined: dict) -> list[dict]:
    ranked = category_ranked_ids(joined)
    selected: list[str] = []
    contributed_by: dict[str, list[str]] = {}
    for cat_name, ranked_ids in ranked.items():
        added = 0
        for cid in ranked_ids:
            if added >= 2:
                break
            if cid not in selected:
                selected.append(cid)
                contributed_by[cid] = [cat_name]
                added += 1
            # already-selected clip counted toward this category's quota only
            # if it happens to be a NEW pick; if it was already picked by an
            # earlier category we still note the tag match for transparency,
            # but it doesn't consume this category's "2 new" budget.
        # note tag matches for clips selected by earlier categories too
        for cid in ranked_ids[:2]:
            if cid in selected and cat_name not in contributed_by.setdefault(cid, []):
                contributed_by[cid].append(cat_name)

    assert len(selected) == 12, f"expected 12 unique clips, got {len(selected)}: {selected}"

    records = []
    for cid in selected:
        row = joined[cid]
        reasons = contributed_by[cid]
        records.append({
            "clip_id": cid,
            "duration_s": row["duration_s"],
            "reference": row["reference_text"],
            "baseline_prediction": row["baseline_prediction_text"],
            "baseline_wer": row["wer"],
            "frames_sampled": row["frames_sampled"],
            "model_calls": row["model_calls"],
            "sampling_density_fps": row["sampling_density_fps"],
            "manifest_heuristic_tags": {
                "number_token": is_yes(row["heuristics"]["heuristic_contains_number_token"]),
                "fingerspelling_candidate": is_yes(row["heuristics"]["heuristic_proper_noun_or_acronym_fingerspelling_candidate"]),
                "fast_signing": is_yes(row["heuristics"]["heuristic_fast_signing_wps_ge_p90"]),
                "question": is_yes(row["heuristics"]["official_ends_with_question_mark"]),
            },
            "reason_selected": reasons,
            "baseline_config": BASELINE_CONFIG,
            "baseline_results_dir": BASELINE_RESULTS_DIR,
        })
    return records


def main() -> None:
    joined = load_joined_rows()
    records = select(joined)

    OUT_JSON.write_text(json.dumps({
        "source_manifest": str(MANIFEST_PATH.relative_to(REPO_ROOT)),
        "source_baseline_per_clip_results": str(PER_CLIP_CSV.relative_to(REPO_ROOT)),
        "baseline_config": BASELINE_CONFIG,
        "n_selected": len(records),
        "selection_method": "select_12_diagnostic_clips.py, six fixed categories, deterministic ranking, no model calls",
        "clips": records,
    }, indent=2), encoding="utf-8")

    fieldnames = ["clip_id", "duration_s", "reference", "baseline_prediction", "baseline_wer",
                  "frames_sampled", "model_calls", "sampling_density_fps",
                  "manifest_heuristic_tags", "reason_selected", "baseline_config", "baseline_results_dir"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in records:
            row = dict(r)
            row["manifest_heuristic_tags"] = json.dumps(row["manifest_heuristic_tags"])
            row["reason_selected"] = ";".join(row["reason_selected"])
            w.writerow(row)

    print(f"Wrote {OUT_JSON} and {OUT_CSV} ({len(records)} clips)")
    for r in records:
        print(f"  {r['clip_id']:45s} wer={r['baseline_wer']!s:8s} dur={r['duration_s']:6.2f}s "
              f"calls={r['model_calls']} reasons={','.join(r['reason_selected'])}")


if __name__ == "__main__":
    main()
