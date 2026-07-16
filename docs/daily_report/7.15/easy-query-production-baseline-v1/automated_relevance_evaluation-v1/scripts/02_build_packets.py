#!/usr/bin/env python3
"""Phase 2 prep: build one compact judgment packet per query (328 total),
joining query_input + full_results + top_results. Also writes batch manifests
of 20 queries each for the main evaluation pass. Read-only against baseline root.
"""
import csv, json, os, re
from collections import OrderedDict

BR = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.15/easy-query-production-baseline-v1"
OUT = os.path.join(BR, "automated_relevance_evaluation-v1")

QUERY_INPUT = os.path.join(BR, "query_input/easy_queries_cleaned_300_plus_2026-07-14.csv")
FULL_CSV = os.path.join(BR, "final/easy_query_production_baseline_full_results.csv")
TOP_CSV = os.path.join(BR, "final/easy_query_production_baseline_top_results.csv")

def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

query_input = read_csv(QUERY_INPUT)
full_rows = read_csv(FULL_CSV)
top_rows = read_csv(TOP_CSV)

qi_by_easyid = {r['easy_id']: r for r in query_input}
top_by_qidx = OrderedDict()
for r in top_rows:
    top_by_qidx.setdefault(int(r['query_index']), []).append(r)

def slug_terms(url):
    """Pull human-readable words out of a curify template/carousel URL slug."""
    if not url:
        return []
    m = re.search(r'/(template|carousel)[^?]*', url)
    seg = m.group(0) if m else url
    seg = seg.split('?')[0]
    words = re.split(r'[/_\-]+', seg)
    words = [w for w in words if w and not w.isdigit() and w not in ('template', 'carousel', 'template-example', 'nano-template')]
    return words

def trim_url(url):
    """Drop the huge query string (?media=...&from=...&ids=<40-item carousel context>),
    keep scheme+host+path only. The query string is >95% of raw url bytes and carries
    no additional relevance signal beyond what url_slug_terms already extracts from the path."""
    if not url:
        return url
    return url.split('?')[0]

packets = []
for r_full in full_rows:
    qidx = int(r_full['query_index'])
    qid = r_full['query_id']
    qi = qi_by_easyid.get(qid, {})
    tops = sorted(top_by_qidx.get(qidx, []), key=lambda x: int(x['result_rank']))
    top_packet = []
    for t in tops[:5]:
        top_packet.append({
            "rank": int(t['result_rank']),
            "title": t['result_title'],
            "url": trim_url(t['result_url']),
            "image_url": t['image_url'],
            "metadata": t['metadata'],
            "url_slug_terms": slug_terms(t['result_url']),
        })
    packets.append({
        "query_index": qidx,
        "source_row_number": r_full['source_row_number'],
        "query_id": qid,
        "original_query": r_full['original_query'],
        "detected_language": qi.get('language', 'UNKNOWN'),
        "category": r_full['category'],
        "query_type_input": qi.get('query_type', ''),
        "contains_proper_noun": qi.get('contains_proper_noun', ''),
        "contains_number_or_model": qi.get('contains_number_or_model', ''),
        "contains_mixed_language": qi.get('contains_mixed_language', ''),
        "duplicate_status": qi.get('duplicate_status', ''),
        "easy_confidence": qi.get('easy_confidence', ''),
        "input_notes": qi.get('notes', ''),
        "result_count_observed": int(r_full['result_count_observed']) if r_full['result_count_observed'] not in ('', None) else 0,
        "zero_result": r_full['zero_result'] in ('True', 'true'),
        "low_result": r_full['low_result'] in ('True', 'true'),
        "query_broadened": r_full['query_broadened'] in ('True', 'true'),
        "broadened_query": r_full['broadened_query'],
        "rewrite_observed": r_full['rewrite_observed'] in ('True', 'true'),
        "raw_rewrite_visible": r_full['raw_rewrite_visible'],
        "final_status": r_full['final_status'],
        "screenshot_path": r_full['screenshot_path'],
        "raw_response_path": r_full['raw_response_path'],
        "top_results": top_packet,
        "visible_result_count": len(top_packet),
    })

packets.sort(key=lambda p: p['query_index'])
assert len(packets) == 328, len(packets)
assert [p['query_index'] for p in packets] == list(range(1, 329))

with open(os.path.join(OUT, "evidence", "query_packets.json"), "w", encoding="utf-8") as f:
    json.dump(packets, f, ensure_ascii=False, indent=2)

# Batches of 20
BATCH_SIZE = 20
os.makedirs(os.path.join(OUT, "batches", "input"), exist_ok=True)
n_batches = (len(packets) + BATCH_SIZE - 1) // BATCH_SIZE
batch_manifest = []
for i in range(n_batches):
    chunk = packets[i*BATCH_SIZE:(i+1)*BATCH_SIZE]
    batch_id = f"batch_{i+1:03d}"
    with open(os.path.join(OUT, "batches", "input", f"{batch_id}.json"), "w", encoding="utf-8") as f:
        json.dump(chunk, f, ensure_ascii=False, indent=2)
    batch_manifest.append({
        "batch_id": batch_id,
        "query_index_start": chunk[0]['query_index'],
        "query_index_end": chunk[-1]['query_index'],
        "count": len(chunk),
    })

with open(os.path.join(OUT, "batches", "batch_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(batch_manifest, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(packets)} query packets across {n_batches} batches of up to {BATCH_SIZE}.")
for b in batch_manifest:
    print(b)
