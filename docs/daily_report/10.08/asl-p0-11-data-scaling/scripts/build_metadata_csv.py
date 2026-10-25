"""P0-11: write SENTENCE_NAME,SENTENCE metadata for the whole official re-aligned train split (same format as
P0.2's subset_metadata.csv) and assert it is identical to P0.2's text for every P0.2 clip.
Usage: python build_metadata_csv.py REALIGNED_TRAIN_TSV P02_SUBSET_METADATA_CSV OUT_CSV"""
import csv, sys
tsv, p02, out = sys.argv[1:4]
rows = list(csv.DictReader(open(tsv), delimiter="\t"))
full = {r["SENTENCE_NAME"]: r["SENTENCE"] for r in rows}
old = {r["SENTENCE_NAME"]: r["SENTENCE"] for r in csv.DictReader(open(p02))}
bad = [k for k, v in old.items() if full.get(k) != v]
assert not bad, f"{len(bad)} P0.2 texts differ, e.g. {bad[:3]}"
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["SENTENCE_NAME", "SENTENCE"])
    for k in sorted(full):
        w.writerow([k, full[k]])
print(f"wrote {len(full)} rows; {len(old)} P0.2 texts identical")
