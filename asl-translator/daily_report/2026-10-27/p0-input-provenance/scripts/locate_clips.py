"""P0-1: locate each B_ours_5p39 input clip (how2sign_v2/videos/<clip>.mp4) inside its How2Sign TEST raw source video
by pixel matching, and record the actual source interval. CPU only, no model. Raw videos are extracted one at a time
to a scratch folder and deleted after use.

Method (INPUT_PROVENANCE_PLAN.md, Amendment 1): grayscale 64x36 thumbnails of every raw and clip frame.
(1) per-frame z-normalized MAE over 64 evenly spaced clip frames; (2) motion-energy (mean |frame diff|) Pearson
correlation over all clip frames. Unique = both agree within +-1 frame, r_best >= 0.90, r_best - r_next(outside +-5)
>= 0.20. The plain-intensity MAE is kept for transparency only.

usage: python -I locate_clips.py --scratch DIR --out located_clips.json [--only R10,R14]
"""
import argparse, csv, hashlib, json, os, re, subprocess, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
SHEET = os.path.join(REPO, "docs/daily_report/10.18/asl-review-inspection-sheet")
PROV = os.path.join(REPO, "asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/provenance/case_provenance.csv")
V2 = os.path.join(REPO, "asl-translator/data/public_benchmarks/how2sign_v2")
TEST_ZIP = os.path.expanduser("~/Desktop/curify/p018-work/downloads/test_raw_videos.zip")
ORIG_CSV = os.path.expanduser("~/Desktop/curify/p018-work/downloads/how2sign_test.csv")
REAL_CSV = os.path.expanduser("~/Desktop/curify/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/"
                              "landmark_t5_1pct/local_run_10pct/raw_download/how2sign_realigned_test.csv")
W, H, EXCL = 64, 36, 5

sys.path.insert(0, os.path.join(REPO, "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_tsv(path, s_col, e_col):
    assert "val" not in os.path.basename(path)
    return {r["SENTENCE_NAME"]: (float(r[s_col]), float(r[e_col])) for r in csv.DictReader(open(path), delimiter="\t")}


def probe(path):
    out = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
         "stream=r_frame_rate,avg_frame_rate,nb_read_frames,width,height", "-of", "json", path],
        capture_output=True, check=True, text=True).stdout)["streams"][0]
    n, d = map(int, out["r_frame_rate"].split("/"))
    return {"fps": n / d, "r_frame_rate": out["r_frame_rate"], "avg_frame_rate": out["avg_frame_rate"],
            "frames": int(out["nb_read_frames"]), "w_h": f"{out['width']}x{out['height']}"}


def thumbs(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vsync", "0", "-vf", f"scale={W}:{H},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)


def locate(R, C):
    N, M = len(R), len(C)
    if M > N:
        return None
    L = N - M + 1
    js = np.unique(np.linspace(0, M - 1, 64).round().astype(int))

    def z(X):
        return (X - X.mean(axis=(-2, -1), keepdims=True)) / (X.std(axis=(-2, -1), keepdims=True) + 1e-6)

    Rz, Cz = z(R), z(C)
    plain, norm = np.zeros(L), np.zeros(L)
    for j in js:
        plain += np.abs(R[j:j + L] - C[j]).mean(axis=(1, 2))
        norm += np.abs(Rz[j:j + L] - Cz[j]).mean(axis=(1, 2))
    plain /= len(js); norm /= len(js)
    mr = np.r_[0, np.abs(np.diff(R, axis=0)).mean(axis=(1, 2))]
    mc = np.r_[0, np.abs(np.diff(C, axis=0)).mean(axis=(1, 2))]
    mc_c = mc - mc.mean()
    win = np.lib.stride_tricks.sliding_window_view(mr, M)
    wc = win - win.mean(axis=1, keepdims=True)
    r = (wc @ mc_c) / (np.linalg.norm(wc, axis=1) * np.linalg.norm(mc_c) + 1e-12)
    b_norm, b_mot = int(norm.argmin()), int(r.argmax())
    far = np.abs(np.arange(L) - b_mot) > EXCL
    r_next = float(r[far].max()) if far.any() else None
    unique = (abs(b_norm - b_mot) <= 1 and r[b_mot] >= 0.90 and r_next is not None and r[b_mot] - r_next >= 0.20)
    return {"best_offset_frames": b_mot, "best_offset_norm_mae": b_norm, "norm_mae_best": round(float(norm[b_norm]), 4),
            "norm_mae_median": round(float(np.median(norm)), 4), "motion_r_best": round(float(r[b_mot]), 4),
            "motion_r_next_outside_5": round(r_next, 4) if r_next is not None else None,
            "plain_mae_at_best": round(float(plain[b_mot]), 4), "unique_match": bool(unique),
            "_norm": norm, "_r": r}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--scratch", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    prov = list(csv.DictReader(open(PROV)))
    vman = {r["clip_id"]: r for r in csv.DictReader(open(os.path.join(SHEET, "videos_manifest.csv")))}
    if a.only:
        keep = set(a.only.split(",")); prov = [r for r in prov if r["review_id"] in keep]
    assert_not_holdout([r["clip_id"] for r in prov])
    out = json.load(open(a.out)) if os.path.exists(a.out) else {}
    os.makedirs(a.scratch, exist_ok=True)
    orig = load_tsv(ORIG_CSV, "START", "END"); real = load_tsv(REAL_CSV, "START_REALIGNED", "END_REALIGNED")
    for r in prov:
        cid, rid = r["clip_id"], r["review_id"]
        r["_orig_start"] = orig.get(cid, (None,))[0]; r["_real_start"] = real.get(cid, (None,))[0]
        if rid in out:
            continue
        view = re.match(r"^.*-(\d+-rgb_front)$", cid).group(1)
        raw_name = f"raw_videos/{r['video_id']}-{view}.mp4"
        clip = os.path.join(V2, "videos", cid + ".mp4")
        assert sha256(clip) == vman[cid]["sha256"], cid
        t0 = time.time()
        subprocess.run(["unzip", "-o", "-j", "-q", TEST_ZIP, raw_name, "-d", a.scratch], check=True)
        raw = os.path.join(a.scratch, os.path.basename(raw_name))
        try:
            rp, cp = probe(raw), probe(clip)
            R, C = thumbs(raw), thumbs(clip)
            loc = locate(R, C)
            if loc:
                norm, rr = loc.pop("_norm"), loc.pop("_r")
                fps0 = rp["fps"]
                loc["at_annotations"] = {}
                for lab, t in (("original_start", r["_orig_start"]), ("realigned_start", r["_real_start"])):
                    if t is not None:
                        o = int(round(t * fps0))
                        if 0 <= o < len(norm):
                            loc["at_annotations"][lab] = {"offset_frames": o, "norm_mae": round(float(norm[o]), 4),
                                                          "motion_r": round(float(rr[o]), 4)}
            rec = {"review_id": rid, "clip_id": cid, "source_video": raw_name, "source_video_sha256": sha256(raw),
                   "raw_probe": rp, "clip_probe": cp, "clip_sha256": vman[cid]["sha256"],
                   "raw_thumb_frames": len(R), "clip_thumb_frames": len(C), **(loc or {"error": "clip longer than raw"})}
            if loc:
                fps = rp["fps"]
                rec["slice_start_s"] = round(loc["best_offset_frames"] / fps, 4)
                rec["slice_end_s"] = round((loc["best_offset_frames"] + len(C)) / fps, 4)
            rec["sec"] = round(time.time() - t0, 1)
        finally:
            os.remove(raw)
        out[rid] = rec
        json.dump(out, open(a.out, "w"), indent=1)
        print(rid, cid, rec.get("best_offset_frames"), rec.get("norm_mae_best"), rec.get("motion_r_best"),
              rec.get("motion_r_next_outside_5"), rec.get("unique_match"),
              rec.get("slice_start_s"), rec.get("slice_end_s"), rec["sec"], flush=True)


if __name__ == "__main__":
    main()
