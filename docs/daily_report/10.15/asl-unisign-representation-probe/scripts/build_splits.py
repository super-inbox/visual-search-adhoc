"""P0-14 step 1: freeze clip manifests, groups and low-data draws BEFORE any representation is extracted.

Inputs: the three How2Sign re-aligned CSVs, the official pose-archive index (list_pose_archive.py), the concept
list and near-duplicate table (build_concepts.py). CPU only, no model.

Design (see EXPERIMENT_PLAN.md §4):
  probe_train   = How2Sign train  ∩ official poses                       (Uni-Sign SAW these clips in fine-tuning)
  test_all      = How2Sign test   ∩ official poses                       (Uni-Sign never trained on these)
  test_clean    = test_all minus exact / near duplicates of a train reference      <- primary evaluation pool
  group         = VIDEO_ID (source video). Official splits are already video-disjoint (audit). Grouping by identical
                  sentence was tried and rejected: generic lines ("hi!", "okay.") chain hundreds of videos into one giant
                  component, which made the low-data draws unbalanced (p10 = 7 %, p50 = 62 % of clips).
  low-data      = nested draws of whole videos from probe_train, filled until the clip-count target is reached:
                  10 % / 25 % / 50 % / 100 %
  No test calibration slice: with 135 test videos a 30 % slice left some concepts with 2-7 positives. Decision
  thresholds come from probe_train out-of-fold predictions; all of test_clean is evaluation.

Outputs (OUT_DIR/splits/): manifest.csv (one row per clip, all assignments + concept labels), draws.json, SPLITS.sha256
Usage: python3 -I build_splits.py TRAIN_CSV VAL_CSV TEST_CSV ARCHIVE_INDEX_CSV PROBE_DIR
"""
import csv, hashlib, json, os, random, re, sys
from collections import Counter, defaultdict

train_csv, val_csv, test_csv, arch_csv, D = sys.argv[1:6]
SEED = 20261015
FRACTIONS = {"p10": 0.10, "p25": 0.25, "p50": 0.50, "p100": 1.0}
N_DRAWS = {"p10": 5, "p25": 5, "p50": 3, "p100": 1}
N_CV_FOLDS = 5  # group folds inside probe_train (hyper-parameter selection + out-of-fold thresholds)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
TOK = re.compile(r"[a-z]+(?:'[a-z]+)?")
norm_sentence = lambda s: " ".join(TOK.findall(s.lower().replace("’", "'")))

def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))

arch = {}
for r in csv.DictReader(open(arch_csv)):
    arch[r["clip_id"]] = "train" if r["dir"].startswith("train") else "test"

concept_rows = list(csv.DictReader(open(os.path.join(D, "concepts", "concept_list_v1.csv"))))
rules = json.load(open(os.path.join(D, "concepts", "concept_rules_v1.json")))
dups = {r["sentence_name"]: r["kind"] for r in csv.DictReader(open(os.path.join(D, "audit", "near_duplicates_test.csv")))
        if r["split"] == "test"}

# concept labelling reuses build_concepts' tokenizer/lemmatizer by import (single source of truth)
import importlib.util
spec = importlib.util.spec_from_file_location("bc", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_concepts.py"))
bc_src = open(spec.origin).read().split("# ---------------------------------------------------------------- per-clip annotations")[0]
bc = {"__name__": "bc"}
sys_argv = sys.argv
sys.argv = ["bc", train_csv, val_csv, test_csv, D]
exec(compile(bc_src, spec.origin, "exec"), bc)
sys.argv = sys_argv

def labels(sentence):
    lem, tok = bc["lemmas"](sentence), set(bc["tokens"](sentence))
    out = {}
    for c in concept_rows:
        forms = set(c["forms"].split())
        out[c["concept"]] = int((c["concept"].lower() in lem) if c["match"] == "lemma" else bool(tok & forms))
    return out

rows = []
for split, path in (("train", train_csv), ("val", val_csv), ("test", test_csv)):
    for r in load(path):
        cid = r["SENTENCE_NAME"]
        rows.append({"clip_id": cid, "h2s_split": split, "video_id": r["VIDEO_ID"],
                     "signer_proxy": r["VIDEO_NAME"].rsplit("-rgb_front", 1)[0].rsplit("-", 1)[-1],
                     "has_official_pose": int(arch.get(cid) == split), "dup_of_train": dups.get(cid, "") if split == "test" else "",
                     "n_words": len(bc["tokens"](r["SENTENCE"])),
                     "duration_s": round(float(r["END_REALIGNED"]) - float(r["START_REALIGNED"]), 3),
                     "_norm": norm_sentence(r["SENTENCE"]), **labels(r["SENTENCE"])})

# ---- groups: source video
for r in rows:
    r["group"] = r["video_id"]

# ---- roles
for r in rows:
    if r["h2s_split"] == "train" and r["has_official_pose"]:
        r["role"] = "probe_train"
    elif r["h2s_split"] == "test" and r["has_official_pose"]:
        r["role"] = "test_dup_excluded" if r["dup_of_train"] else "test_clean"
    elif r["h2s_split"] == "val":
        r["role"] = "val_unused_no_official_pose"
    else:
        r["role"] = "no_official_pose"

rng = random.Random(SEED)
# probe_train: CV folds by group, nested low-data draws by group
pg = sorted({r["group"] for r in rows if r["role"] == "probe_train"})
rng.shuffle(pg)
fold = {g: i % N_CV_FOLDS for i, g in enumerate(pg)}
for r in rows:
    r["cv_fold"] = fold.get(r["group"], "") if r["role"] == "probe_train" else ""
n_by_group = Counter(r["group"] for r in rows if r["role"] == "probe_train")
n_total = sum(n_by_group.values())
draws = {}
for d in range(max(N_DRAWS.values())):
    order = pg[:]
    random.Random(SEED + 1000 + d).shuffle(order)
    acc, cum = [], 0
    targets = sorted(FRACTIONS.items(), key=lambda kv: kv[1])
    ti = 0
    for g in order:  # nested within a draw: p10 ⊂ p25 ⊂ p50 ⊂ p100 (prefixes of one shuffled video order)
        acc.append(g); cum += n_by_group[g]
        while ti < len(targets) and cum >= targets[ti][1] * n_total - 1e-9:
            name = targets[ti][0]
            if d < N_DRAWS[name]:
                draws[f"{name}_d{d}"] = sorted(acc)
            ti += 1

os.makedirs(os.path.join(D, "splits"), exist_ok=True)
concepts = [c["concept"] for c in concept_rows]
fields = ["clip_id", "h2s_split", "role", "cv_fold", "group", "video_id", "signer_proxy",
          "has_official_pose", "dup_of_train", "n_words", "duration_s"] + concepts
with open(os.path.join(D, "splits", "manifest.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
json.dump({"seed": SEED, "fractions": FRACTIONS, "n_draws": N_DRAWS, "group": "video_id",
           "n_cv_folds": N_CV_FOLDS, "draw_groups": draws}, open(os.path.join(D, "splits", "draws.json"), "w"))

# ---- summary
role = Counter(r["role"] for r in rows)
print("roles", dict(role))
print("probe_train videos", len(pg), "test_clean videos", len({r["group"] for r in rows if r["role"] == "test_clean"}))
for k, v in draws.items():
    if True:
        n = sum(1 for r in rows if r["role"] == "probe_train" and r["group"] in set(v))
        print(k, "groups", len(v), "clips", n)
summ = []
for c in concepts:
    s = {"test_clean": sum(r[c] for r in rows if r["role"] == "test_clean"),
         "test_clean_videos": len({r["group"] for r in rows if r["role"] == "test_clean" and r[c]})}
    s["train"] = sum(r[c] for r in rows if r["role"] == "probe_train")
    s["p10_d0"] = sum(r[c] for r in rows if r["role"] == "probe_train" and r["group"] in set(draws["p10_d0"]))
    summ.append({"concept": c, **s})
with open(os.path.join(D, "splits", "concept_counts_by_role.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(summ[0].keys())); w.writeheader(); w.writerows(summ)
for s in summ:
    print(f"{s['concept']:13s} train={s['train']:5d} p10_d0={s['p10_d0']:4d} test_clean={s['test_clean']:4d} videos={s['test_clean_videos']:3d}")
with open(os.path.join(D, "splits", "SPLITS.sha256"), "w") as f:
    for fn in ("manifest.csv", "draws.json", "concept_counts_by_role.csv"):
        f.write(hashlib.sha256(open(os.path.join(D, "splits", fn), "rb").read()).hexdigest() + "  " + fn + "\n")
