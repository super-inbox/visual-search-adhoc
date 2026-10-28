"""Task 2 Step 2: Amendment 2 matching (INPUT_PROVENANCE_PLAN.md, A2.2-A2.4). CPU only, no model. Raw videos are
extracted one at a time from test_raw_videos.zip to a scratch folder and deleted after use.

A2.2  locate the official crop box in the raw frame: NCC of the crop clip's mean frame against the raw video's mean frame
      (half resolution, raw sampled at 2 fps), scale 1.0; box accepted if NCC >= 0.70 and the best NCC > 8 half-res px
      away is <= NCC_best - 0.05.
A2.3  temporal match of the official crop clip inside the raw video cropped to that box (A rows).
A2.4  temporal match of the B clip inside the raw video, both cropped to the B-pose signer box (B rows).
Both temporal matches: 64x64 gray region thumbnails; z-normalized MAE over 64 clip frames + 4x4-grid region motion
signature (Pearson r over frames x 16 cells); unique = agree within +-1 frame, r >= 0.90, r - r_next(>5 frames) >= 0.20.

usage: python -I locate_amendment2.py --scratch DIR --crop-dir CROPS_DIR --crops work/official_crops.json
         --out work/located_amendment2.json
         --rows R01:B,R02:B,...     (B = B_ours_5p39 via A2.4, A = A_official via A2.2 + A2.3)
"""
import argparse, csv, hashlib, json, os, re, subprocess, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
P012 = os.path.join(REPO, "docs/daily_report/10.06/asl-p0-12-unisign-pose-gap")
PREP = os.path.join(P012, "artifacts/prepared_inputs")
PROV = os.path.join(REPO, "asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/provenance/case_provenance.csv")
V2 = os.path.join(REPO, "asl-translator/data/public_benchmarks/how2sign_v2")
TEST_ZIP = os.path.expanduser("~/Desktop/curify/p018-work/downloads/test_raw_videos.zip")
T, G, EXCL = 64, 4, 5                       # region thumbnail side, motion grid, uniqueness exclusion (frames)
NCC_MIN, NCC_MARGIN, NCC_EXCL = 0.70, 0.05, 8
KP_IDX = list(range(0, 11)) + list(range(23, 133))   # body 0-10, face 23-90, hands 91-132
KP_SCORE, PAD = 0.3, 0.15

sys.path.insert(0, os.path.join(REPO, "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402
sys.path.insert(0, os.path.join(P012, "scripts"))
import safe_pickle  # noqa: E402


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def fps_of(path):
    s = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                        "-of", "csv=p=0", path], capture_output=True, check=True, text=True).stdout.strip()
    n, d = map(int, s.split("/"))
    return n / d


def frames(path, vf, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vsync", "0", "-vf", vf + ",format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)


def region_thumbs(path, box=None):
    x, y, w, h = box or (0, 0, 0, 0)
    vf = (f"crop={w}:{h}:{x}:{y}," if box else "") + f"scale={T}:{T}"
    return frames(path, vf, T, T)


def ncc_box(raw, crop, cw, ch):
    """A2.2: NCC of the crop clip's mean frame (half-res) over the raw video's mean frame (half-res, 2 fps)."""
    I = frames(raw, "fps=2,scale=640:360", 640, 360).mean(0).astype(np.float64)
    tw, th = cw // 2, ch // 2
    Tm = frames(crop, f"scale={tw}:{th}", tw, th).mean(0).astype(np.float64)
    T0 = Tm - Tm.mean(); n = T0.size
    H, W = I.shape
    F = (H + th, W + tw)
    num = np.fft.irfft2(np.fft.rfft2(I, F) * np.conj(np.fft.rfft2(T0, F)), F)[:H - th + 1, :W - tw + 1]
    S1 = np.pad(I, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    S2 = np.pad(I * I, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    box = lambda S: S[th:, tw:] - S[:-th, tw:] - S[th:, :-tw] + S[:-th, :-tw]
    var = np.maximum(box(S2) - box(S1) ** 2 / n, 1e-9)
    ncc = num / (np.sqrt(var) * np.linalg.norm(T0))
    py, px = np.unravel_index(int(ncc.argmax()), ncc.shape)
    yy, xx = np.mgrid[:ncc.shape[0], :ncc.shape[1]]
    far = np.maximum(np.abs(yy - py), np.abs(xx - px)) > NCC_EXCL
    best, nxt = float(ncc[py, px]), float(ncc[far].max())
    return {"box_xywh": [int(2 * px), int(2 * py), cw, ch], "ncc_best": round(best, 4),
            "ncc_next_outside_8px_half": round(nxt, 4),
            "box_accepted": bool(best >= NCC_MIN and nxt <= best - NCC_MARGIN)}


def pose_box(cid):
    """A2.4: signer box from the B_ours_5p39 pose of this clip (keypoints normalized by 1280x720)."""
    d = safe_pickle.load(os.path.join(PREP, "B_ours_5p39/test-pose-rtmpose-192", cid + ".pkl"))
    k = np.asarray(d["keypoints"])[:, 0, KP_IDX] * np.array([1280, 720])
    s = np.asarray(d["scores"])[:, 0, KP_IDX]
    p = k[s >= KP_SCORE]
    x0, y0 = p.min(0); x1, y1 = p.max(0)
    w, h = x1 - x0, y1 - y0
    x0, x1 = max(0, x0 - PAD * w), min(1280, x1 + PAD * w)
    y0, y1 = max(0, y0 - PAD * h), min(720, y1 + PAD * h)
    x0, y0 = int(x0) // 2 * 2, int(y0) // 2 * 2
    return [x0, y0, int(x1 - x0) // 2 * 2, int(y1 - y0) // 2 * 2]


def locate(R, C):
    N, M = len(R), len(C)
    if M > N:
        return None
    L = N - M + 1
    js = np.unique(np.linspace(0, M - 1, 64).round().astype(int))

    def z(X):
        return (X - X.mean(axis=(-2, -1), keepdims=True)) / (X.std(axis=(-2, -1), keepdims=True) + 1e-6)

    Rz, Cz = z(R), z(C)
    norm = np.zeros(L)
    for j in js:
        norm += np.abs(Rz[j:j + L] - Cz[j]).mean(axis=(1, 2))
    norm /= len(js)

    def cells(X):
        d = np.abs(np.diff(X, axis=0)).reshape(-1, G, T // G, G, T // G).mean(axis=(2, 4)).reshape(-1, G * G)
        return np.vstack([np.zeros((1, G * G)), d])

    mr, mc = cells(R), cells(C)
    mc_c = mc - mc.mean(0)
    numr = sum(np.correlate(mr[:, c], mc_c[:, c], "valid") for c in range(G * G))
    cs1 = np.vstack([np.zeros((1, G * G)), mr.cumsum(0)]); cs2 = np.vstack([np.zeros((1, G * G)), (mr ** 2).cumsum(0)])
    s1, s2 = cs1[M:] - cs1[:-M], cs2[M:] - cs2[:-M]
    den = np.sqrt(np.maximum((s2 - s1 ** 2 / M).sum(1), 1e-12)) * np.linalg.norm(mc_c)
    r = numr / den
    # scalar region motion energy (Amendment 1 statistic), transparency only
    sr, sc = mr.mean(1), mc.mean(1)
    win = np.lib.stride_tricks.sliding_window_view(sr, M); wc = win - win.mean(1, keepdims=True); scc = sc - sc.mean()
    r_scalar = (wc @ scc) / (np.linalg.norm(wc, axis=1) * np.linalg.norm(scc) + 1e-12)
    b_norm, b_mot = int(norm.argmin()), int(r.argmax())
    far = np.abs(np.arange(L) - b_mot) > EXCL
    r_next = float(r[far].max()) if far.any() else None
    far_n = np.abs(np.arange(L) - b_norm) > EXCL
    unique = abs(b_norm - b_mot) <= 1 and r[b_mot] >= 0.90 and r_next is not None and r[b_mot] - r_next >= 0.20
    return {"best_offset_frames": b_mot, "best_offset_norm_mae": b_norm,
            "norm_mae_best": round(float(norm[b_norm]), 4), "norm_mae_next_outside_5": round(float(norm[far_n].min()), 4),
            "norm_mae_median": round(float(np.median(norm)), 4),
            "grid_motion_r_best": round(float(r[b_mot]), 4),
            "grid_motion_r_next_outside_5": round(r_next, 4) if r_next is not None else None,
            "scalar_region_motion_r_at_best": round(float(r_scalar[b_mot]), 4),
            "scalar_region_motion_r_best_offset": int(r_scalar.argmax()),
            "unique_match": bool(unique)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True); ap.add_argument("--crops", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--rows", required=True)
    ap.add_argument("--crop-dir", required=True, help="--scratch folder given to fetch_official_crops.py")
    a = ap.parse_args()
    prov = {r["review_id"]: r for r in csv.DictReader(open(PROV))}
    crops = json.load(open(a.crops))
    a1 = json.load(open(os.path.join(OUT, "work/located_clips.json")))
    want = {}
    for t in a.rows.split(","):
        rid, d = t.split(":"); want.setdefault(rid, []).append(d)
    assert_not_holdout([prov[r]["clip_id"] for r in want])
    out = json.load(open(a.out)) if os.path.exists(a.out) else {}
    os.makedirs(a.scratch, exist_ok=True)
    for rid, doms in want.items():
        p = prov[rid]; cid = p["clip_id"]
        view = re.match(r"^.*-(\d+-rgb_front)$", cid).group(1)
        raw_name = f"raw_videos/{p['video_id']}-{view}.mp4"
        assert raw_name == a1[rid]["source_video"]
        t0 = time.time()
        subprocess.run(["unzip", "-o", "-j", "-q", TEST_ZIP, raw_name, "-d", a.scratch], check=True)
        raw = os.path.join(a.scratch, os.path.basename(raw_name))
        try:
            assert sha256(raw) == a1[rid]["source_video_sha256"]
            fps = fps_of(raw)
            for d in doms:
                key = f"{rid}:{'A_official' if d == 'A' else 'B_ours_5p39'}"
                rec = {"review_id": rid, "clip_id": cid, "domain": key.split(":")[1], "source_video": raw_name,
                       "source_fps": fps}
                if d == "A":
                    cr = crops[rid]; clip = os.path.join(a.crop_dir, cid + ".mp4")
                    assert sha256(clip) == cr["sha256"]
                    cw, ch = map(int, cr["probe"]["w_h"].split("x"))
                    rec["method"] = "A2.2 + A2.3 (official crop clip)"
                    rec["input_clip_sha256"] = cr["sha256"]
                    rec.update(ncc_box(raw, clip, cw, ch))
                    box = rec["box_xywh"]
                    C = region_thumbs(clip)
                else:
                    clip = os.path.join(V2, "videos", cid + ".mp4")
                    assert sha256(clip) == a1[rid]["clip_sha256"]
                    rec["method"] = "A2.4 (B clip, B-pose signer box)"
                    rec["input_clip_sha256"] = a1[rid]["clip_sha256"]
                    box = rec["box_xywh"] = pose_box(cid); rec["box_accepted"] = True
                    C = region_thumbs(clip, box)
                assert fps_of(clip) == fps, (fps_of(clip), fps)
                rec["clip_frames"] = len(C)
                if rec["box_accepted"]:
                    R = region_thumbs(raw, box)
                    loc = locate(R, C)
                    rec.update(loc or {"error": "clip longer than raw"})
                    if loc:
                        rec["slice_start_s"] = round(loc["best_offset_frames"] / fps, 4)
                        rec["slice_end_s"] = round((loc["best_offset_frames"] + len(C)) / fps, 4)
                    if d == "B":
                        rec["amendment1_offset_frames"] = a1[rid]["best_offset_frames"]
                        rec["amendment1_unique"] = a1[rid]["unique_match"]
                else:
                    rec["unique_match"] = False
                rec["sec"] = round(time.time() - t0, 1)
                out[key] = rec
                json.dump(out, open(a.out, "w"), indent=1)
                print(key, {k: rec.get(k) for k in ("box_xywh", "ncc_best", "ncc_next_outside_8px_half", "box_accepted",
                                                     "best_offset_frames", "best_offset_norm_mae", "norm_mae_best",
                                                     "grid_motion_r_best", "grid_motion_r_next_outside_5",
                                                     "unique_match", "slice_start_s", "slice_end_s",
                                                     "amendment1_offset_frames")}, flush=True)
        finally:
            os.remove(raw)


if __name__ == "__main__":
    main()
