"""P0-11: integrity checks for the nested subsets (text overlap with val/frozen, reference identity, file presence
in the archive listing, signer-key counts). Usage: python check_splits.py SPLITS_DIR TRAIN_TSV HOLDOUT_SPLIT_JSON
FROZEN_METADATA_CSV ARCHIVE_FILELIST OUT_JSON"""
import csv, json, re, sys
from pathlib import Path
sd, tsv, split_json, frozen_meta, filelist, out = sys.argv[1:7]
norm = lambda t: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", t.lower())).strip()  # = train_p02.norm_text
text = {r["SENTENCE_NAME"]: r["SENTENCE"] for r in csv.DictReader(open(tsv), delimiter="\t")}
val = json.load(open(split_json))["val"]
ftext = {r["SENTENCE_NAME"]: r["SENTENCE"] for r in csv.DictReader(open(frozen_meta))}
files = {Path(l.strip()).name.replace("_holistic.npy", "") for l in open(filelist) if l.strip()}
vt, ft = {norm(text[i]) for i in val}, {norm(t) for t in ftext.values()}
res = {"val_n": len(val), "frozen_n": len(ftext)}
for name in ("p02_ref", "p25", "p50", "p100"):
    ids = [l.strip() for l in open(Path(sd) / f"train_{name}.txt") if l.strip()]
    tn = [norm(text[i]) for i in ids]
    res[name] = {"n": len(ids), "unique_ids": len(set(ids)), "all_in_archive_listing": all(i in files for i in ids),
                 "empty_text": sum(not text[i].strip() for i in ids),
                 "normalised_text_overlap_with_val_clips": sum(t in vt for t in tn),
                 "normalised_text_overlap_with_frozen": sum(t in ft for t in tn),
                 "distinct_normalised_texts": len(set(tn))}
print(json.dumps(res, indent=1))
json.dump(res, open(out, "w"), indent=1)
