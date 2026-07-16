#!/usr/bin/env python3
import json, os, sys, importlib.util

HERE = os.path.dirname(__file__)
OUT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.15/easy-query-production-baseline-v1/automated_relevance_evaluation-v1"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pb = load(os.path.join(HERE, "05_process_batch.py"), "pb")

with open(os.path.join(OUT, "evidence", "query_packets.json"), encoding="utf-8") as f:
    packets = json.load(f)
packets_by_id = {p["query_id"]: p for p in packets}

batch_id = sys.argv[1]
judgments_path = os.path.join(OUT, "batches", "judgments", f"{batch_id}.py")
q_rows, r_rows = pb.process(batch_id, judgments_path, packets_by_id)
print(f"{batch_id}: {len(q_rows)} query rows, {len(r_rows)} result rows")
labels = {}
for r in q_rows:
    labels[r["query_relevance_label"]] = labels.get(r["query_relevance_label"], 0) + 1
print(labels)
missing = set(packets_by_id.keys()) if False else None
