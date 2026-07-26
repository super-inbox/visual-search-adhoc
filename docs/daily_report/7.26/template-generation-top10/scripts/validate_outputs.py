#!/usr/bin/env python3
"""
validate_outputs.py

Automated structural QA over every generated example in templates/**.
Checks: file exists, non-trivial size, valid decodable image, aspect ratio
roughly matches the template's requested aspect_ratio, image is not blank
(all-white/all-black/near-uniform), and metadata.json / manifests agree.

Read-only against the generated images; writes only:
  - QUALITY_REVIEW.md
  - example_manifest.json (status field updated per example)
"""
import json, os, sys, hashlib
from PIL import Image
import numpy as np

OUT_ROOT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.26/template-generation-top10"

def parse_ratio(s):
    w, h = s.split(":")
    return float(w) / float(h)

def is_near_uniform(img, threshold=3.0):
    arr = np.asarray(img.convert("L"), dtype=np.float32)
    return float(arr.std()) < threshold, float(arr.std())

def main():
    tm = json.load(open(os.path.join(OUT_ROOT, "template_manifest.json")))
    em = json.load(open(os.path.join(OUT_ROOT, "example_manifest.json")))
    templates_by_id = {t["template_id"]: t for t in tm["templates"]}

    rows = []
    seen_hashes = {}
    counts = {"PASS": 0, "NEEDS_REVIEW": 0, "FAIL": 0}

    for ex in em["examples"]:
        edir = os.path.join(OUT_ROOT, ex["example_dir"])
        meta_path = os.path.join(edir, "metadata.json")
        meta = json.load(open(meta_path))
        tpl = templates_by_id[ex["template_id"]]

        notes = []
        result = "PASS"

        if meta["status"] != "success":
            result = "FAIL"
            notes.append(f"generation status={meta['status']}, error={meta.get('error')}")
            ex["status"] = "failed"
            rows.append((ex, tpl, result, notes, None, None, None))
            counts[result] += 1
            continue

        out_path = os.path.join(edir, "output.png")
        if not os.path.exists(out_path):
            result = "FAIL"
            notes.append("output.png missing despite success status")
            ex["status"] = "failed"
            rows.append((ex, tpl, result, notes, None, None, None))
            counts[result] += 1
            continue

        size_bytes = os.path.getsize(out_path)
        if size_bytes < 20_000:
            result = "FAIL"
            notes.append(f"suspiciously small file ({size_bytes} bytes)")

        try:
            img = Image.open(out_path)
            img.load()
            w, h = img.size
        except Exception as e:
            result = "FAIL"
            notes.append(f"undecodable image: {e}")
            ex["status"] = "failed"
            rows.append((ex, tpl, result, notes, None, None, None))
            counts[result] += 1
            continue

        expected_ratio = parse_ratio(tpl["aspect_ratio"])
        actual_ratio = w / h
        ratio_diff = abs(actual_ratio - expected_ratio) / expected_ratio
        if ratio_diff > 0.25:
            result = "NEEDS_REVIEW" if result == "PASS" else result
            notes.append(f"aspect ratio drift: expected {tpl['aspect_ratio']} ({expected_ratio:.2f}), got {w}x{h} ({actual_ratio:.2f}), diff={ratio_diff:.0%}")

        uniform, std = is_near_uniform(img)
        if uniform:
            result = "FAIL"
            notes.append(f"near-uniform image (likely blank), stddev={std:.2f}")

        sha256 = hashlib.sha256(open(out_path, "rb").read()).hexdigest()
        if sha256 in seen_hashes:
            result = "NEEDS_REVIEW" if result == "PASS" else result
            notes.append(f"duplicate image bytes -- identical to {seen_hashes[sha256]}")
        else:
            seen_hashes[sha256] = ex["example_id"]

        if not notes:
            notes.append("all automated checks passed; text readability / subject accuracy require human visual review (see PILOT_REVIEW.md for the 10 manually-reviewed pilots)")

        ex["status"] = "success" if result == "PASS" else result.lower()
        counts[result] += 1
        rows.append((ex, tpl, result, notes, w, h, size_bytes))

    with open(os.path.join(OUT_ROOT, "example_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(em, f, indent=2, ensure_ascii=False)
        f.write("\n")

    lines = []
    lines.append("# Quality Review — Automated Structural QA (all 40 examples)\n")
    lines.append(f"PASS: {counts['PASS']}  |  NEEDS_REVIEW: {counts['NEEDS_REVIEW']}  |  FAIL: {counts['FAIL']}\n")
    lines.append("Automated checks: file exists, size > 20KB, image decodes, aspect ratio within 25% of the "
                  "template's target, not near-uniform (blank/placeholder-failure), not a byte-for-byte duplicate "
                  "of another example. Text readability and subject accuracy were manually verified for the 10 "
                  "pilot examples (see `PILOT_REVIEW.md`); the automated checks here extend structural coverage "
                  "to the full batch of 40 without claiming to replace human visual review of text/content "
                  "correctness on every single image.\n")
    lines.append("| Template | Example | Dimensions | Size | Result | Notes |")
    lines.append("|---|---|---|---|---|---|")
    for ex, tpl, result, notes, w, h, size_bytes in rows:
        dims = f"{w}x{h}" if w else "-"
        size_s = f"{size_bytes/1024:.0f} KB" if size_bytes else "-"
        lines.append(f"| {tpl['template_name']} ({ex['template_id']}) | {ex['example_id'].split('-example-')[-1]} | {dims} | {size_s} | {result} | {'; '.join(notes)} |")

    with open(os.path.join(OUT_ROOT, "QUALITY_REVIEW.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"PASS={counts['PASS']} NEEDS_REVIEW={counts['NEEDS_REVIEW']} FAIL={counts['FAIL']}")

if __name__ == "__main__":
    main()
