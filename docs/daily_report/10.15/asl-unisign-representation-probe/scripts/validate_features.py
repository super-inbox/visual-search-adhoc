"""P0-14 gate checks for an extraction output directory (smoke, pilot, full). CPU, no model.

Checks (each reported PASS/FAIL in <features>/VALIDATION.json; exit code 1 if any FAIL):
  shapes        every pooled array has the expected per-clip shape: raw 207, fsign 1024, mt5 768 (mean/std/mad), seg4 4xD
  finite        no NaN / Inf anywhere
  one_record    exactly one record per expected clip, no duplicates, no extras
  order         concatenated shard order == manifest order of the expected clips
  provenance    every record has split / role / source_video_id matching the manifest, a pose sha256, dims
  frames        T == min(n_frames_raw, 256) for every clip
  pooled_dim    the primary probe vector [mean ; std] is 414 / 2048 / 1536 for every clip
  determinism   (--compare DIR) max |difference| over shared clips <= --tol, for every array
  labels        (--csvs) concept labels in the manifest == labels re-derived from the English reference;
                h2s split / VIDEO_ID == the CSV; role is consistent with split (no train/test mix-up)
  pose_split    (--archive-index) each clip's pose came from the archive directory of its own split
Usage: python -I validate_features.py --probe-dir . --features DIR --ids-from MANIFEST_SUBSET.csv
          [--compare DIR2] [--csvs TRAIN VAL TEST] [--archive-index audit/official_pose_archive_index.csv]
"""
import argparse, csv, glob, json, os, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--probe-dir", required=True)
ap.add_argument("--features", required=True)
ap.add_argument("--ids-from", required=True, help="manifest-format CSV listing exactly the clips expected, in order")
ap.add_argument("--compare", default=None)
ap.add_argument("--tol", type=float, default=1e-5)
ap.add_argument("--csvs", nargs=3, default=None)
ap.add_argument("--archive-index", default=None)
a = ap.parse_args()

DIMS = {"raw": 207, "fsign": 1024, "mt5": 768}
res = {}
def check(name, ok, detail=""):
    res[name] = {"pass": bool(ok), "detail": detail}

def load_dir(d):
    ids, recs, arrs = [], [], {}
    for f in sorted(glob.glob(os.path.join(d, "shard_*.npz"))):
        meta = json.load(open(f[:-4] + ".json"))
        z = np.load(f)
        n = len(meta["clip_ids"])
        for k in z.files:
            assert z[k].shape[0] == n, (f, k, z[k].shape, n)
            arrs.setdefault(k, []).append(z[k])
        ids += meta["clip_ids"]; recs += meta.get("records", [{}] * n)
    return ids, recs, {k: np.concatenate(v) for k, v in arrs.items()}

ids, recs, A = load_dir(a.features)
expected = list(csv.DictReader(open(a.ids_from)))
exp_ids = [r["clip_id"] for r in expected]
man = {r["clip_id"]: r for r in csv.DictReader(open(os.path.join(a.probe_dir, "splits", "manifest.csv")))}

# shapes / finite / pooled dim
bad = []
for rep, d in DIMS.items():
    for stat in ("mean", "std", "mad"):
        if A[f"{rep}_{stat}"].shape != (len(ids), d):
            bad.append(f"{rep}_{stat}{A[f'{rep}_{stat}'].shape}")
    if A[f"{rep}_seg4"].shape != (len(ids), 4, d):
        bad.append(f"{rep}_seg4{A[f'{rep}_seg4'].shape}")
check("shapes", not bad, bad or {k: list(v.shape) for k, v in A.items()})
nonfinite = {k: int((~np.isfinite(v)).sum()) for k, v in A.items() if np.issubdtype(v.dtype, np.floating)}
check("finite", all(v == 0 for v in nonfinite.values()), {k: v for k, v in nonfinite.items() if v})
pooled = {rep: int(np.concatenate([A[f"{rep}_mean"], A[f"{rep}_std"]], 1).shape[1]) for rep in DIMS}
check("pooled_dim", pooled == {k: 2 * v for k, v in DIMS.items()}, pooled)

# one record per clip / order
dups = len(ids) - len(set(ids))
missing, extra = sorted(set(exp_ids) - set(ids)), sorted(set(ids) - set(exp_ids))
check("one_record", dups == 0 and not missing and not extra and len(recs) == len(ids),
      {"n": len(ids), "expected": len(exp_ids), "duplicates": dups, "missing": missing[:5], "extra": extra[:5]})
check("order", ids == exp_ids, "" if ids == exp_ids else "first mismatch at %d" % next(
    (i for i, (x, y) in enumerate(zip(ids, exp_ids)) if x != y), min(len(ids), len(exp_ids))))

# provenance / frames
prov_bad, frame_bad = [], []
for cid, r in zip(ids, recs):
    m = man[cid]
    if not (r.get("split") == m["h2s_split"] and r.get("role") == m["role"] and r.get("source_video_id") == m["video_id"]
            and len(r.get("pose_sha256", "")) == 64 and r.get("dims") == DIMS):
        prov_bad.append(cid)
for cid, r, T, n in zip(ids, recs, A["T"], A["n_frames_raw"]):
    if int(T) != min(int(n), 256) or r.get("T") != int(T):
        frame_bad.append((cid, int(T), int(n)))
check("provenance", not prov_bad, prov_bad[:5])
check("frames", not frame_bad, {"bad": frame_bad[:5], "T_min": int(A["T"].min()), "T_max": int(A["T"].max()),
                                "n_sampled_gt256": int((A["n_frames_raw"] > 256).sum())})

# determinism
if a.compare:
    ids2, _, B = load_dir(a.compare)
    shared = [c for c in ids if c in set(ids2)]
    i1 = [ids.index(c) for c in shared]; i2 = [ids2.index(c) for c in shared]
    diffs = {k: float(np.abs(A[k][i1].astype(np.float64) - B[k][i2]).max()) for k in A if k in B}
    check("determinism", shared and all(v <= a.tol for v in diffs.values()), {"n_shared": len(shared), "max_abs_diff": diffs})

# labels re-derived from the English references
if a.csvs:
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_concepts.py")).read()
    src = src.split("# ---------------------------------------------------------------- per-clip annotations")[0]
    g = {"__name__": "bc"}; argv = sys.argv; sys.argv = ["bc", *a.csvs, a.probe_dir]
    exec(compile(src, "build_concepts.py", "exec"), g); sys.argv = argv
    concepts = list(csv.DictReader(open(os.path.join(a.probe_dir, "concepts", "concept_list_v1.csv"))))
    ref = {}
    for split, rows in g["splits"].items():
        for r in rows:
            ref[r["SENTENCE_NAME"]] = (split, r["VIDEO_ID"], r["SENTENCE"])
    lab_bad, split_bad, n_pos = [], [], 0
    for cid in ids:
        split, vid_, sent = ref[cid]
        lem, tok = g["lemmas"](sent), set(g["tokens"](sent))
        for c in concepts:
            y = int((c["concept"].lower() in lem) if c["match"] == "lemma" else bool(tok & set(c["forms"].split())))
            n_pos += y
            if y != int(man[cid][c["concept"]]):
                lab_bad.append((cid, c["concept"]))
        m = man[cid]
        role_ok = (m["role"] == "probe_train") == (split == "train") and (m["role"].startswith("test")) == (split == "test")
        if split != m["h2s_split"] or vid_ != m["video_id"] or not role_ok:
            split_bad.append(cid)
    check("labels", not lab_bad, {"mismatches": lab_bad[:5], "n_positive_labels_checked": n_pos})
    check("split_video_role", not split_bad, split_bad[:5])

if a.archive_index:
    arch = {r["clip_id"]: r["dir"] for r in csv.DictReader(open(a.archive_index))}
    bad = [c for c, r in zip(ids, recs) if not arch.get(c, "").startswith(r["split"])
           or (r["pose_source"].startswith("zip:") and not r["pose_source"][4:].startswith(arch[c]))]
    check("pose_split", not bad, bad[:5])

ok = all(v["pass"] for v in res.values())
json.dump({"features": a.features, "n_clips": len(ids), "all_pass": ok, "checks": res},
          open(os.path.join(a.features, "VALIDATION.json"), "w"), indent=1, default=str)
for k, v in res.items():
    print(f"{'PASS' if v['pass'] else 'FAIL'}  {k}  {json.dumps(v['detail'], default=str)[:200]}")
print("ALL PASS" if ok else "GATE FAILED")
sys.exit(0 if ok else 1)
