"""P0-18 DEV: turn full-video poses (extract_context.py) into Uni-Sign pose pkls per condition (pipeline.py).

Usage: python -I build_conditions.py --vid-dir DIR --clips CLIPS.csv --params PARAMS.json --out ROOT
       --conditions A_old,B_auto,... [--oracle ORACLE.json] [--only IDS.txt]
       CLIPS.csv: clip_id, video_name, start, end (ORIGINAL timing; ALL clips of each video give its sentence timeline)
       ORACLE.json: {clip_id: [start, end]} realigned windows, dev only (O_* conditions)
Writes ROOT/<condition>/<clip_id>.pkl and ROOT/build_meta.json (lag, interval, box, failure flags per clip).
"""
import argparse, csv, json, os, pickle, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "asl-p0-16-experimental-credibility", "scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402
import pipeline as PL  # noqa: E402
import pose_extract as PE  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--vid-dir", required=True)
ap.add_argument("--clips", required=True)
ap.add_argument("--params", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--conditions", default=",".join(PL.PROD))
ap.add_argument("--oracle", default="")
ap.add_argument("--only", default="")
a = ap.parse_args()
conds = a.conditions.split(",")
assert set(conds) <= set(PL.PROD + PL.ORACLE), conds
P = json.load(open(a.params)); PI, PC = P["interval"], P["crop"]
orc = json.load(open(a.oracle)) if a.oracle else {}
if set(conds) & set(PL.ORACLE):
    assert orc, "oracle conditions need --oracle (dev only)"
rows = list(csv.DictReader(open(a.clips)))
assert_not_holdout([r["clip_id"] for r in rows])
only = set(open(a.only).read().split()) if a.only else None
for c in conds:
    os.makedirs(os.path.join(a.out, c), exist_ok=True)
by_v = {}
for r in rows:
    by_v.setdefault(r["video_name"], []).append((r["clip_id"], float(r["start"]), float(r["end"])))
meta, videos = {}, {}
for vn, cl in sorted(by_v.items()):
    todo = [c for c in cl if only is None or c[0] in only]
    if not todo:
        continue
    npz = os.path.join(a.vid_dir, vn + ".npz")
    if not os.path.exists(npz):
        for c in todo:
            meta[c[0]] = {"fail": "missing_pose"}
        continue
    t = time.time()
    V = PE.VideoPose(npz)
    vrec, recs = PL.video_intervals(V, todo, [(s, e) for _, s, e in cl], PI)
    for cid, rec in recs.items():
        pk, m = PL.build_clip(V, cid, rec, conds, PC, orc.get(cid))
        for c, d in pk.items():
            pickle.dump(d, open(os.path.join(a.out, c, cid + ".pkl"), "wb"))
        meta[cid] = dict(rec, **m, video=vn, failed=PL.clip_failed(rec, m))
    vrec["seconds_build"] = round(time.time() - t, 2)
    videos[vn] = vrec
json.dump({"params": P, "conditions": conds, "videos": videos, "clips": meta},
          open(os.path.join(a.out, "build_meta.json"), "w"), indent=1)
print({"clips": len(meta), "missing_pose": sum(v.get("fail") == "missing_pose" for v in meta.values()),
       "failed": sum(1 for v in meta.values() if v.get("failed")),
       "lag_low_conf_videos": sum(v["warp_fail"] == "lag_low_conf" for v in videos.values())})
