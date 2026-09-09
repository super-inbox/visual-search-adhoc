#!/usr/bin/env python3
"""Automated validation for the Phase 1 paired-76 analysis + review app
deliverables. Read-only: makes no network/model call, writes nothing.

Run:
    python3 asl-translator/evaluation/diagnostics/phase1_temporal_ablation/validate_phase1.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
BASELINE_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "curify_gemini_3_6_2026_09_04"
EIGHTFPS_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "curify_gemini_3_6_2026_09_06_8fps"
MANIFEST_PATH = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2" / "manifest.csv"

results = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def main() -> int:
    # 40 review clips, no duplicates
    with (HERE / "taxonomy_40_clips.csv").open(newline="", encoding="utf-8") as f:
        taxonomy_rows = list(csv.DictReader(f))
    ids40 = [r["clip_id"] for r in taxonomy_rows]
    check("exactly 40 review clips", len(ids40) == 40, f"found {len(ids40)}")
    check("no duplicate clip IDs in taxonomy_40_clips.csv", len(set(ids40)) == len(ids40),
          f"{len(ids40) - len(set(ids40))} duplicates")

    # 12 priority diagnostic clips
    diag12 = json.loads((HERE / "diagnostic_12_clips.json").read_text(encoding="utf-8"))["clips"]
    ids12 = [c["clip_id"] for c in diag12]
    check("exactly 12 priority diagnostic clips", len(ids12) == 12, f"found {len(ids12)}")
    check("no duplicate clip IDs in diagnostic_12_clips.json", len(set(ids12)) == len(ids12))
    check("all 12 priority clips are among the 40", set(ids12) <= set(ids40),
          f"missing: {set(ids12) - set(ids40)}")

    # baseline predictions exist for all 40
    missing_preds = [cid for cid in ids40 if not (BASELINE_DIR / "predictions" / f"{cid}.json").exists()]
    check("all referenced baseline predictions exist (40/40)", not missing_preds, f"missing: {missing_preds}")

    # local video paths resolve for all 40
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        manifest = {r["how2sign_id"]: r for r in csv.DictReader(f)}
    missing_videos = [cid for cid in ids40
                       if cid not in manifest or not (REPO_ROOT / manifest[cid]["local_video_path"]).exists()]
    check("local video paths resolve for all 40 clips", not missing_videos, f"missing: {missing_videos}")

    # original taxonomy_40_clips.csv not overwritten by the app: still exactly the 38 columns
    # select_40_taxonomy_clips.py wrote, and no review-only field ("last_saved_utc") leaked in.
    header = list(taxonomy_rows[0].keys())
    check("taxonomy_40_clips.csv column count unchanged (38, as written by select_40_taxonomy_clips.py)",
          len(header) == 38, f"found {len(header)}")
    check("taxonomy_40_clips.csv has no review-app-only field (last_saved_utc)",
          "last_saved_utc" not in header)
    check("taxonomy_40_human_review.{json,csv} exist as SEPARATE files from taxonomy_40_clips.csv",
          (HERE / "taxonomy_40_human_review.json").exists() and (HERE / "taxonomy_40_human_review.csv").exists())

    # paired-76 exact match
    eightfps_per_clip = json.loads((EIGHTFPS_DIR / "per_clip_results.json").read_text(encoding="utf-8"))
    actual_success_ids = set(r["how2sign_id"] for r in eightfps_per_clip if r["status"] == "success")
    check("8fps run has exactly 76 successful clips", len(actual_success_ids) == 76, f"found {len(actual_success_ids)}")

    with (HERE / "paired_76_2fps_vs_8fps.csv").open(newline="", encoding="utf-8") as f:
        paired_rows = list(csv.DictReader(f))
    paired_ids = set(r["clip_id"] for r in paired_rows)
    check("paired_76_2fps_vs_8fps.csv has exactly 76 rows", len(paired_rows) == 76, f"found {len(paired_rows)}")
    check("paired_76 clip IDs are EXACTLY the 76 successful 8fps IDs (set-equal)",
          paired_ids == actual_success_ids,
          f"symmetric diff: {paired_ids.symmetric_difference(actual_success_ids)}")

    baseline_per_clip = json.loads((BASELINE_DIR / "per_clip_results.json").read_text(encoding="utf-8"))
    baseline_success_ids = set(r["how2sign_id"] for r in baseline_per_clip if r["status"] == "success")
    check("all 76 paired IDs also succeeded in baseline A", actual_success_ids <= baseline_success_ids,
          f"missing from baseline: {actual_success_ids - baseline_success_ids}")

    # no Gemini / external inference call anywhere in the new Phase 1 code.
    # AST-based, not text search: several files intentionally MENTION
    # "google.genai" / "run_real(" inside docstrings and markdown-report
    # f-strings to document that they do NOT call them. Parsing the AST and
    # only inspecting actual Import/ImportFrom/Call nodes (string literals
    # and comments are never nodes of those kinds) avoids that false-positive
    # entirely, rather than trying to text-match around prose.
    import ast as _ast

    def scan(path: Path) -> tuple[bool, bool]:
        tree = _ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        found_import = found_call = False
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Import):
                if any("genai" in a.name or a.name == "google" for a in node.names):
                    found_import = True
            elif isinstance(node, _ast.ImportFrom):
                mod = node.module or ""
                if "genai" in mod or mod == "google" or any("genai" in a.name for a in node.names):
                    found_import = True
            elif isinstance(node, _ast.Call):
                fname = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
                if fname in ("run_real", "generate_content"):
                    found_call = True
        return found_import, found_call

    py_files = [f for f in HERE.rglob("*.py") if f.resolve() != Path(__file__).resolve()]
    offenders_import, offenders_call = [], []
    for f in py_files:
        imp, call = scan(f)
        if imp:
            offenders_import.append(str(f.relative_to(REPO_ROOT)))
        if call:
            offenders_call.append(str(f.relative_to(REPO_ROOT)))
    check("no google.genai import in any Phase 1 script's AST",
          not offenders_import, f"found in: {offenders_import}")
    check("no Phase 1 script's AST calls run_current_model.run_real() or generate_content()",
          not offenders_call, f"found in: {offenders_call}")

    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f"\n{len(results) - n_fail}/{len(results)} checks passed.")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
