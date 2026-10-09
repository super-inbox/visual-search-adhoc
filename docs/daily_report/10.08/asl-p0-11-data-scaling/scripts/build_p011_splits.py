"""P0-11: build nested supervised-data subsets from the same How2Sign train pool as P0.2.

Pool (same eligibility rules as P0.2's prepare_subset.py, plus val-leakage exclusion):
  official How2Sign re-aligned TRAIN clips
  ∩ clips with a landmark file in the Kaggle 'How2Sign Holistic' train/frontal archive
  − clips whose normalised text equals a frozen-147 text (P0.2 denylist rule; 2 clips)
  − frozen clip / video IDs (none expected: frozen set is official TEST)
  − the 366 P0.2 val clips, every clip from a val video, and every clip sharing a val
    split_by_signer group key (P0.2's "signer" = filename prefix), so no val leakage at any size
Order: the existing 2,751 P0.2 train clips first (sorted), then the rest of the pool shuffled with
random.Random(SEED). Subsets are prefixes of this order, so 2,751 ⊂ 25% ⊂ 50% ⊂ 100%.
Usage: python build_p011_splits.py TRAIN_CSV ARCHIVE_FILELIST DENYLIST_JSON HOLDOUT_SPLIT_JSON
                                   FROZEN_IDS_TXT OUT_DIR
"""
import csv, hashlib, json, random, re, sys
from collections import Counter
from pathlib import Path

SEED = 20261008
FRACTIONS = {"p25": 0.25, "p50": 0.50, "p100": 1.00}

train_csv, filelist, deny_json, split_json, frozen_txt, out = sys.argv[1:7]
out = Path(out)
out.mkdir(parents=True, exist_ok=True)


def norm_text(t):  # identical to landmark_t5_1pct/common.py norm_text
    t = re.sub(r"[^a-z0-9\s]", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def key(i):  # identical to src/utils/splits.py split_by_signer filename-prefix rule
    p = i.split("_")
    bad = ["video", "sentence", "segment", "clip", "train", "val", "test", "validation", "dev", "run"]
    return p[0] if len(p) > 1 and p[0].isalnum() and p[0].lower() not in bad else None


rows = list(csv.DictReader(open(train_csv), delimiter="\t"))
vid = {r["SENTENCE_NAME"]: r["VIDEO_ID"] for r in rows}
text = {r["SENTENCE_NAME"]: r["SENTENCE"] for r in rows}
files = {Path(l.strip()).name.replace("_holistic.npy", "") for l in open(filelist) if l.strip().endswith(".npy")}
deny = json.load(open(deny_json))
split = json.load(open(split_json))
p02_train, p02_val = list(split["train"]), list(split["val"])
frozen = [l.strip() for l in open(frozen_txt) if l.strip()]
assert len(p02_train) == 2751 and len(p02_val) == 366 and len(frozen) == 147

deny_text = set(deny["normalised_texts"])
val_videos = {vid[i] for i in p02_val}
val_keys = {key(i) for i in p02_val} - {None}
excl = Counter()
pool = []
for i in sorted(vid):
    if i not in files:
        excl["no_landmark_file"] += 1
    elif not text[i].strip():
        excl["empty_text"] += 1
    elif norm_text(text[i]) in deny_text:
        excl["frozen_text_collision"] += 1
    elif i in set(deny["clip_ids"]) or vid[i] in set(deny["video_ids"]):
        excl["frozen_clip_or_video"] += 1
    elif i in set(p02_val):
        excl["p02_val_clip"] += 1
    elif vid[i] in val_videos:
        excl["same_video_as_val"] += 1
    elif key(i) in val_keys:
        excl["same_split_key_as_val"] += 1
    else:
        pool.append(i)
pool_set = set(pool)
assert set(p02_train) <= pool_set, "P0.2 train not inside pool"
rest = sorted(pool_set - set(p02_train))
random.Random(SEED).shuffle(rest)
order = sorted(p02_train) + rest
N = len(order)

subsets = {"p02_ref": sorted(p02_train)}
for name, f in FRACTIONS.items():
    k = round(f * N)
    assert k >= 2751
    subsets[name] = order[:k]

summ = {"seed": SEED, "n_official_train": len(vid), "n_with_landmarks": len(set(vid) & files),
        "exclusions": dict(excl), "pool_size": N, "val_videos": len(val_videos), "val_split_keys": len(val_keys),
        "subsets": {}}
names = list(subsets)
for name in names:
    ids = subsets[name]
    vids = {vid[i] for i in ids}
    (out / f"train_{name}.txt").write_text("\n".join(ids) + "\n")
    summ["subsets"][name] = {
        "n_clips": len(ids), "n_videos": len(vids),
        "pct_of_pool": round(100 * len(ids) / N, 2),
        "pct_of_official_train": round(100 * len(ids) / len(vid), 2),
        "sha256_ids": hashlib.sha256(("\n".join(ids) + "\n").encode()).hexdigest(),
        "val_clip_overlap": len(set(ids) & set(p02_val)),
        "val_video_overlap": len(vids & val_videos),
        "frozen_clip_overlap": len(set(ids) & set(frozen)),
        "frozen_video_overlap": len(vids & set(deny["video_ids"])),
        "frozen_text_overlap": sum(norm_text(text[i]) in deny_text for i in ids),
    }
for a, b in zip(names, names[1:]):
    summ.setdefault("nesting", {})[f"{a}⊂{b}"] = set(subsets[a]) <= set(subsets[b])
print(json.dumps(summ, indent=1))
json.dump(summ, open(out / "splits_summary.json", "w"), indent=1)
