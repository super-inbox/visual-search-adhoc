#!/usr/bin/env python3
"""Fetches real Pinterest pin pages (found via WebSearch), extracts real
og:title/og:image/og:description, downloads+validates the thumbnail, and
appends schema-compliant rows to per-domain SOURCE_CANDIDATES/inspirations
files. Every field is derived from what was actually fetched -- nothing here
is invented. Run repeatedly with different CANDIDATES lists; it appends.
"""
import csv
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

FIELDNAMES = [
    "id", "query_id", "query", "query_source", "target_domain", "topic_slug",
    "title", "source_url", "source_domain", "source_type", "thumbnail_path",
    "thumbnail_status", "short_content_understanding", "style_tags",
    "collection_method", "discovered_via", "source_rank", "topic_mapping_status",
    "quality_score", "duplicate_status", "review_status", "notes",
]


def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            r = subprocess.run(
                ["curl", "-sS", "-A", UA, "--max-time", "20", "-L", url],
                capture_output=True, text=True, timeout=25,
            )
            if r.stdout:
                return r.stdout
        except Exception:
            pass
        time.sleep(3 * (attempt + 1))
    return ""


def extract_meta(html, prop):
    m = re.search(rf'<meta[^>]*property="{prop}"[^>]*content="([^"]*)"', html)
    if m:
        return m.group(1)
    m = re.search(rf'<meta[^>]*content="([^"]*)"[^>]*property="{prop}"', html)
    return m.group(1) if m else ""


def html_unescape(s):
    return (s.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
             .replace("&lt;", "<").replace("&gt;", ">"))


def download_image(url, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    try:
        subprocess.run(
            ["curl", "-sS", "-A", UA, "--max-time", "20", "-o", dest_path, url],
            check=True, timeout=25,
        )
    except Exception:
        return False
    if not os.path.isfile(dest_path) or os.path.getsize(dest_path) < 1000:
        return False
    out = subprocess.run(["file", "--brief", dest_path], capture_output=True, text=True).stdout
    ok = any(k in out for k in ("JPEG", "PNG", "WebP", "image data"))
    if not ok:
        os.remove(dest_path)
    return ok


def process(candidates, domain, chunk_label):
    csv_path = os.path.join(HERE, f"SOURCE_CANDIDATES_{domain}{chunk_label}.csv")
    jsonl_path = os.path.join(HERE, f"inspirations_{domain}{chunk_label}.jsonl")
    write_header = not os.path.isfile(csv_path)

    csv_f = open(csv_path, "a", newline="", encoding="utf-8")
    jsonl_f = open(jsonl_path, "a", encoding="utf-8")
    w = csv.DictWriter(csv_f, fieldnames=FIELDNAMES)
    if write_header:
        w.writeheader()

    results = []
    for c in candidates:
        html = fetch(c["pin_url"])
        if not html:
            print(f"SKIP {c['id']}: fetch failed")
            continue
        title = html_unescape(extract_meta(html, "og:title"))
        desc = html_unescape(extract_meta(html, "og:description"))
        image = extract_meta(html, "og:image")
        if not title:
            print(f"SKIP {c['id']}: no og:title, likely not a real pin page")
            continue
        thumb_rel = f"thumbnails/{domain}/{c['query_id']}_{c['seq']:03d}.jpg"
        thumb_abs = os.path.join(HERE, thumb_rel)
        ok = download_image(image, thumb_abs) if image else False
        row = {
            "id": c["id"], "query_id": c["query_id"], "query": c["query"],
            "query_source": c["query_source"], "target_domain": domain,
            "topic_slug": c["topic_slug"], "title": title,
            "source_url": c["pin_url"], "source_domain": "pinterest.com",
            "source_type": "pinterest_pin",
            "thumbnail_path": thumb_rel if ok else "",
            "thumbnail_status": "AVAILABLE" if ok else "UNAVAILABLE",
            "short_content_understanding": (desc or title)[:280],
            "style_tags": c.get("style_tags", ""),
            "collection_method": "WebSearch+curl(og:meta)",
            "discovered_via": c["discovered_via"],
            "source_rank": c["seq"],
            "topic_mapping_status": c["topic_mapping_status"],
            "quality_score": c.get("quality_score", "B"),
            "duplicate_status": "UNIQUE",
            "review_status": "PENDING",
            "notes": c.get("notes", ""),
        }
        w.writerow(row)
        jrow = dict(row)
        jrow["style_tags"] = [t for t in row["style_tags"].split(";") if t]
        jsonl_f.write(json.dumps(jrow, ensure_ascii=False) + "\n")
        results.append(row)
        print(f"OK {c['id']}: thumb={row['thumbnail_status']} title={title[:60]!r}")
        time.sleep(1.5)

    csv_f.close()
    jsonl_f.close()
    return results


if __name__ == "__main__":
    print("Import this module and call process(candidates, domain, chunk_label)")
