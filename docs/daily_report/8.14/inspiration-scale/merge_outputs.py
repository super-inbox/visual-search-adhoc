#!/usr/bin/env python3
"""Merges per-domain SOURCE_CANDIDATES_*.csv into SOURCE_CANDIDATES.csv and
inspirations.jsonl, validating no duplicate ids/URLs across domains."""
import csv
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

FIELDNAMES = [
    "id", "query_id", "query", "query_source", "target_domain", "topic_slug",
    "title", "source_url", "source_domain", "source_type", "thumbnail_path",
    "thumbnail_status", "short_content_understanding", "style_tags",
    "collection_method", "discovered_via", "source_rank", "topic_mapping_status",
    "quality_score", "duplicate_status", "review_status", "notes",
]

all_rows = []
seen_ids = {}
seen_urls = {}
for f in sorted(glob.glob("SOURCE_CANDIDATES_*.csv")):
    with open(f, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rid = row["id"]
            url = row["source_url"]
            if rid in seen_ids:
                print(f"DUPLICATE ID: {rid} in {f} and {seen_ids[rid]}")
            seen_ids[rid] = f
            if url in seen_urls:
                row["duplicate_status"] = f"DUPLICATE_OF:{seen_urls[url]}"
            else:
                seen_urls[url] = rid
            all_rows.append(row)

with open("SOURCE_CANDIDATES.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDNAMES)
    w.writeheader()
    for r in all_rows:
        w.writerow({k: r.get(k, "") for k in FIELDNAMES})

with open("inspirations.jsonl", "w", encoding="utf-8") as f:
    for r in all_rows:
        jr = dict(r)
        jr["style_tags"] = [t for t in r.get("style_tags", "").split(";") if t]
        f.write(json.dumps(jr, ensure_ascii=False) + "\n")

print(f"Merged {len(all_rows)} records into SOURCE_CANDIDATES.csv / inspirations.jsonl")
dup_urls = [r["id"] for r in all_rows if r["duplicate_status"] != "UNIQUE"]
print(f"Cross-domain duplicate URLs: {len(dup_urls)} -> {dup_urls}")

# thumbnail validation
missing = []
for r in all_rows:
    tp = r.get("thumbnail_path", "")
    if r["thumbnail_status"] == "AVAILABLE":
        if not tp or not os.path.isfile(os.path.join(HERE, tp)):
            missing.append(r["id"])
print(f"Thumbnails marked AVAILABLE but missing on disk: {len(missing)} -> {missing}")

from collections import Counter
print("Per-domain counts:", Counter(r["target_domain"] for r in all_rows))
print("Per-source-type counts:", Counter(r["source_type"] for r in all_rows))
print("Per-quality counts:", Counter(r["quality_score"] for r in all_rows))
