#!/usr/bin/env python3
"""Offline validation for the 8.14 inspiration-scale gallery.html, adapted
from docs/daily_report/8.8/inspiration-source-pilot/validate_gallery.py."""
import csv
import json
import os
import re
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
GALLERY = os.path.join(HERE, "gallery.html")
CANDIDATES_CSV = os.path.join(HERE, "SOURCE_CANDIDATES.csv")
JSONL = os.path.join(HERE, "inspirations.jsonl")

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" — {detail}" if detail else ""))
    if not condition:
        failures.append(label)


check("gallery.html exists", os.path.isfile(GALLERY))
with open(GALLERY, encoding="utf-8") as f:
    html = f.read()

check("has <!DOCTYPE html>", html.strip().lower().startswith("<!doctype html>"))
check("has <html> and </html>", "<html" in html and "</html>" in html)
check("has <head> and </head>", "<head>" in html and "</head>" in html)
check("has <body> and </body>", "<body>" in html and "</body>" in html)
check("has non-empty <title>", bool(re.search(r"<title>[^<]+</title>", html)))

m = re.search(r'<script id="gallery-data" type="application/json">(.*?)</script>', html, re.S)
check("gallery-data script tag found", m is not None)
data = json.loads(m.group(1)) if m else []
check("embedded JSON parses", m is not None)

with open(CANDIDATES_CSV, newline="", encoding="utf-8") as f:
    candidate_rows = list(csv.DictReader(f))
check("record count matches SOURCE_CANDIDATES.csv", len(data) == len(candidate_rows),
      f"gallery={len(data)} candidates={len(candidate_rows)}")

# JSONL parses, same count
with open(JSONL, encoding="utf-8") as f:
    jsonl_lines = [l for l in f if l.strip()]
jsonl_records = []
jsonl_bad = 0
for l in jsonl_lines:
    try:
        jsonl_records.append(json.loads(l))
    except json.JSONDecodeError:
        jsonl_bad += 1
check("every inspirations.jsonl line parses", jsonl_bad == 0, f"{jsonl_bad} bad lines")
check("inspirations.jsonl record count matches CSV", len(jsonl_records) == len(candidate_rows),
      f"jsonl={len(jsonl_records)} csv={len(candidate_rows)}")

# required IDs exist
missing_id = [r for r in jsonl_records if not r.get("id")]
check("every jsonl record has a non-empty id", len(missing_id) == 0, str(len(missing_id)))

# CSV column consistency
expected_cols = set(candidate_rows[0].keys()) if candidate_rows else set()
bad_rows = [i for i, r in enumerate(candidate_rows) if set(r.keys()) != expected_cols]
check("all CSV rows share the same column set", len(bad_rows) == 0, str(bad_rows))

# duplicate ids
ids = [r.get("id") for r in candidate_rows]
dup_ids = len(ids) - len(set(ids))
check("no duplicate id in SOURCE_CANDIDATES.csv", dup_ids == 0, f"{dup_ids} dupes")

ids_j = [r.get("id") for r in data]
check("no duplicate source_id in embedded gallery data", len(ids_j) == len(set(ids_j)))

# duplicate URLs (report, not necessarily fail -- cross-domain collisions are flagged via duplicate_status)
urls = [r.get("source_url") for r in candidate_rows]
url_counts = {}
for u in urls:
    url_counts[u] = url_counts.get(u, 0) + 1
dup_urls = {u: c for u, c in url_counts.items() if c > 1}
print(f"[INFO] duplicate source_url count: {len(dup_urls)} -> {list(dup_urls.keys())}")

# thumbnail resolution
missing_thumbs = []
external_thumbs = []
bad_type_thumbs = []
for r in data:
    thumb = r.get("thumbnail_path", "")
    if r.get("thumbnail_status") != "AVAILABLE":
        continue
    parsed = urlparse(thumb)
    if parsed.scheme in ("http", "https"):
        external_thumbs.append(r.get("id"))
        continue
    p = os.path.join(HERE, thumb)
    if not os.path.isfile(p):
        missing_thumbs.append(r.get("id"))
check("all thumbnail paths are local (no http/https)", len(external_thumbs) == 0, str(external_thumbs))
check("all AVAILABLE thumbnail files resolve on disk", len(missing_thumbs) == 0, str(missing_thumbs))

# validate actual image type via `file`
import subprocess
bad_files = []
for r in data:
    if r.get("thumbnail_status") != "AVAILABLE":
        continue
    p = os.path.join(HERE, r.get("thumbnail_path", ""))
    if not os.path.isfile(p):
        continue
    out = subprocess.run(["file", "--brief", p], capture_output=True, text=True).stdout
    if not any(k in out for k in ("JPEG", "PNG", "WebP", "image data")):
        bad_files.append((r.get("id"), out.strip()))
check("all thumbnail files decode as real images (not HTML/text)", len(bad_files) == 0, str(bad_files))

# no external <img src> in raw markup outside gallery-data script
markup_wo_data = html[:m.start()] + html[m.end():] if m else html
img_srcs = re.findall(r'<img[^>]+src="([^"]+)"', markup_wo_data)
external_imgs = [s for s in img_srcs if s.startswith("http://") or s.startswith("https://")]
check("no hardcoded external <img src> in static markup", len(external_imgs) == 0, str(external_imgs))
check("no <iframe> anywhere in gallery.html", "<iframe" not in html.lower())

for filter_id in ["f-domain", "f-query", "f-source", "f-type", "f-mapping", "f-review", "f-search"]:
    check(f'filter control "{filter_id}" present', f'id="{filter_id}"' in html)

bad_urls = []
mismatched = []
cand_by_id = {r["id"]: r for r in candidate_rows}
for r in data:
    su = r.get("source_url", "")
    parsed = urlparse(su)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        bad_urls.append((r.get("id"), su))
    cand = cand_by_id.get(r.get("id"))
    if cand and cand["source_url"] != su:
        mismatched.append(r.get("id"))
check("all source_url values are syntactically valid http(s) URLs", len(bad_urls) == 0, str(bad_urls))
check("all source_url values match SOURCE_CANDIDATES.csv", len(mismatched) == 0, str(mismatched))

check(
    'gallery uses target="_blank" + rel=noopener for outbound links',
    'link.target = "_blank"' in html and 'rel = "noopener"' in html,
)

# query linkage: every query_id in the data exists in selected_queries.csv
sel_path = os.path.join(HERE, "selected_queries.csv")
with open(sel_path, newline="", encoding="utf-8") as f:
    sel_ids = {r["id"] for r in csv.DictReader(f)}
bad_query_links = [r.get("id") for r in data if r.get("query_id") not in sel_ids]
check("every record's query_id exists in selected_queries.csv", len(bad_query_links) == 0, str(bad_query_links))

# topic_slug sanity: non-empty
bad_topic = [r.get("id") for r in data if not r.get("topic_slug")]
check("every record has a non-empty topic_slug", len(bad_topic) == 0, str(bad_topic))

print()
print(f"TOTAL CHECKS FAILED: {len(failures)}")
if failures:
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("ALL CHECKS PASSED")
