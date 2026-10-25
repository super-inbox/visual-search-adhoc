"""P0-18 DEV: full-frame RTMPose over every frame of every DEVELOPMENT video that has a listed clip (pose_extract.py).

Every clip id passes the P0-16 holdout guard first (How2Sign val is denied). The H18 one-shot runner calls
pose_extract directly, after RUN_LOCK.

Usage: python -I extract_context.py --clips CLIPS.csv --videos-zip ZIP --out DIR [--device cpu|cuda]
       (the canonical GPU extraction on the VM uses vm_upload.py + vm_worker.py instead)
       CLIPS.csv columns: clip_id, video_name, start, end   (ORIGINAL timing)
"""
import argparse, csv, json, os, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "asl-p0-16-experimental-credibility", "scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402
import pose_extract as PE  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--clips", required=True)
ap.add_argument("--videos-zip", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--device", default="cpu")
ap.add_argument("--workers", type=int, default=PE.WORKERS)
a = ap.parse_args()
rows = list(csv.DictReader(open(a.clips)))
assert_not_holdout([r["clip_id"] for r in rows])
os.makedirs(a.out, exist_ok=True)
wb = PE.make_wholebody(a.device)
env = dict(PE.environment(), device=a.device)
open(os.path.join(a.out, "extractor_env.jsonl"), "a").write(json.dumps(env) + "\n")
videos = {r["video_name"] for r in rows}
zf = zipfile.ZipFile(a.videos_zip)
PE.extract_from_zip(zf, PE.zip_video_index(zf), videos, a.out, wb, tempfile.mkdtemp(prefix="p018_vid_"),
                    os.path.join(a.out, "extract_log.jsonl"), a.workers)
print("DONE")
