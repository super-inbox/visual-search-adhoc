"""P0-18: full-frame RTMPose over EVERY frame of a full How2Sign video (shared by dev extraction and the H18 one-shot
runner, so both use byte-identical extraction code).

The video is read sequentially once (cv2, no seeking); every frame goes through rtmlib Wholebody(mode="lightweight",
onnxruntime) exactly as P0-12 condition B. All detected persons are kept:
<out>/<video_name>.npz with K (N, P, 133, 2) pixels float64 (rtmlib's dtype), S (N, P, 133) float32,
n_persons (N,), fps, frame_wh. P = max persons in any frame; unused slots are zero with score 0.

clip_pose() slices one window out of a video and selects the signer over that window (p018_lib.select_signer), giving
the (K, S, t0) arrays used by p018_lib. Reads only video frames; no text, no boundary of any kind.
"""
import hashlib, json, os, time
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

import p018_lib as L

CHUNK = 256


CUDA_EP = ("CUDAExecutionProvider", {"device_id": 0, "cudnn_conv_algo_search": "HEURISTIC"})
WORKERS = 4                                     # P0-18 GPU benchmark: best stable on the T4 (4 vCPU)

CKPT_DIR = os.path.expanduser("~/.cache/rtmlib/hub/checkpoints")
MODELS = {"det": ("yolox_tiny_8xb8-300e_humanart-6f3252f9.onnx",
                  "ceb11c07298f95c50d7c5abeb906d03340c85f23aa79e3e66966e7fb6c307250"),
          "pose": ("rtmw-dw-l-m_simcc-cocktail14_270e-256x192_20231122.onnx",
                   "68db326c5c6f3273456f803eae0faf5440478369f2c3ee67258d2f36512e8d76")}


def model_path(kind):
    name, sha = MODELS[kind]
    p = os.path.join(CKPT_DIR, name)
    if hashlib.sha256(open(p, "rb").read()).hexdigest() != sha:
        raise RuntimeError(f"rtmlib model checksum mismatch: {p}")
    return p


def make_wholebody(device="cpu"):
    """rtmlib Wholebody lightweight. device="cuda": both ONNX sessions are rebuilt with deterministic compute and the
    HEURISTIC cuDNN conv algorithm choice (DEFAULT has no cuDNN 9 kernel for 187 convs -> "Fallback mode", ~8x slower;
    HEURISTIC == EXHAUSTIVE byte-for-byte, see gpu_bench*.py), and the run fails unless CUDAExecutionProvider is active
    (onnxruntime otherwise silently falls back to CPU)."""
    from rtmlib import Wholebody
    if device == "cpu":
        return Wholebody(to_openpose=False, mode="lightweight", backend="onnxruntime", device=device)
    import onnxruntime as ort
    ort.preload_dlls()                          # CUDA 12 / cuDNN 9 from the nvidia-* pip wheels of onnxruntime-gpu[cuda,cudnn]
    m = Wholebody.MODE["lightweight"]
    wb = Wholebody(det=model_path("det"), det_input_size=m["det_input_size"], pose=model_path("pose"),
                   pose_input_size=m["pose_input_size"], to_openpose=False, backend="onnxruntime", device=device)
    assert device == "cuda", device
    for kind, tool in (("det", wb.det_model), ("pose", wb.pose_model)):
        so = ort.SessionOptions(); so.use_deterministic_compute = True
        tool.session = ort.InferenceSession(model_path(kind), sess_options=so, providers=[CUDA_EP])
        if tool.session.get_providers()[0] != "CUDAExecutionProvider":
            raise RuntimeError(f"onnxruntime fell back to {tool.session.get_providers()} for {kind}")
    return wb


def environment():
    """Extractor environment record (frozen into the P0-18 config; checked by the H18 runner)."""
    import cv2 as _cv2, onnxruntime as ort, rtmlib, subprocess
    env = {"onnxruntime": ort.__version__, "ort_device": ort.get_device(), "providers": ort.get_available_providers(),
           "rtmlib": getattr(rtmlib, "__version__", "0.0.13"), "opencv": _cv2.__version__, "numpy": np.__version__,
           "models_sha256": {k: v[1] for k, v in MODELS.items()}, "cuda_ep": list(CUDA_EP),
           "deterministic_compute": True, "workers": WORKERS, "chunk": CHUNK,
           "ffmpeg": _cv2.getBuildInformation().split("FFMPEG:")[1].split("swscale")[0].split()}
    try:
        env["gpu"] = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
                                    capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        env["gpu"] = None
    return env


def extract_video(video_path, out_npz, wb, workers=WORKERS):
    t_start = time.time()
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ks, ss, batch = [], [], []

    def flush():
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for k, s in ex.map(lambda f: wb(np.uint8(f)), batch):
                ks.append(np.asarray(k, np.float64).reshape(-1, 133, 2))
                ss.append(np.asarray(s, np.float32).reshape(-1, 133))
        batch.clear()

    while True:
        ok, fr = cap.read()
        if not ok:
            break
        batch.append(fr)
        if len(batch) == CHUNK:
            flush()
    if batch:
        flush()
    cap.release()
    N = len(ks); P = max([len(k) for k in ks] + [1])
    K = np.zeros((N, P, 133, 2), np.float64); S = np.zeros((N, P, 133), np.float32)
    npers = np.array([len(k) for k in ks], np.int16)
    for t in range(N):
        K[t, :npers[t]], S[t, :npers[t]] = ks[t], ss[t]
    np.savez_compressed(out_npz, K=K, S=S, n_persons=npers, fps=fps, frame_wh=np.array([W, H]))
    return {"video": os.path.basename(video_path), "fps": fps, "frames": N, "max_persons": int(P),
            "frames_multi": int((npers > 1).sum()), "frames_none": int((npers == 0).sum()),
            "seconds_pose": round(time.time() - t_start, 2)}


def extract_from_zip(zf, zip_names, videos, out_dir, wb, tmpdir, log_path, workers=WORKERS):
    """Resumable per video. Appends one JSON line per video to log_path."""
    log = open(log_path, "a")
    for vn in sorted(videos, key=lambda v: hashlib.sha1(v.encode()).hexdigest()):   # spread progress over videos
        out = os.path.join(out_dir, vn + ".npz")
        if os.path.exists(out):
            continue
        if vn not in zip_names:
            log.write(json.dumps({"video": vn, "error": "video_not_in_zip"}) + "\n"); log.flush(); continue
        t = time.time()
        vp = os.path.join(tmpdir, vn + ".mp4")
        with zf.open(zip_names[vn]) as src, open(vp, "wb") as dst:
            while True:
                b = src.read(1 << 22)
                if not b:
                    break
                dst.write(b)
        t_unzip = time.time() - t
        rec = extract_video(vp, out + ".tmp.npz", wb, workers)
        os.replace(out + ".tmp.npz", out)
        rec["seconds_unzip"] = round(t_unzip, 2)
        os.remove(vp)
        log.write(json.dumps(rec) + "\n"); log.flush()
        print(f"{vn} frames={rec['frames']} pose={rec['seconds_pose']:.0f}s", flush=True)
    log.close()


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def arrays_sha256(npz):
    z = np.load(npz); h = hashlib.sha256()
    for k in ("K", "S", "n_persons"):
        h.update(np.ascontiguousarray(z[k]).tobytes())
    return h.hexdigest()


def validate_npz(npz, video_path):
    """Pose output check before the source video copy may be deleted: one row per frame (vs the container frame count,
    tolerance 2), layout and dtypes as documented, values finite. Returns a list of problems (empty = valid)."""
    z = np.load(npz); bad = []
    K, S, n = z["K"], z["S"], z["n_persons"]
    cap = cv2.VideoCapture(video_path); n_meta = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); cap.release()
    if len(K) == 0 or abs(len(K) - n_meta) > 2:
        bad.append(f"frames {len(K)} vs container {n_meta}")
    if K.dtype != np.float64 or S.dtype != np.float32 or K.shape[2:] != (133, 2) or S.shape != K.shape[:3]:
        bad.append(f"layout K{K.shape}{K.dtype} S{S.shape}{S.dtype}")
    if len(n) != len(K) or (len(K) and n.max() > K.shape[1]):
        bad.append("n_persons")
    if not (np.isfinite(K).all() and np.isfinite(S).all()):
        bad.append("non-finite")
    if float(z["fps"]) <= 0:
        bad.append("fps")
    return bad


def extract_from_dir(video_dir, manifest, out_dir, wb, log_path, workers=WORKERS, delete_after=False):
    """As extract_from_zip, reading uploaded copies <video_dir>/<video_name>.mp4 listed in manifest
    {video_name: sha256 of the zip member}. Each copy is sha256-checked before extraction; its npz is validated
    (validate_npz) and checksummed before the copy is deleted (delete_after, GPU VM's small disk). Resumable."""
    log = open(log_path, "a"); n_fail = 0
    for vn in sorted(manifest, key=lambda v: hashlib.sha1(v.encode()).hexdigest()):
        out = os.path.join(out_dir, vn + ".npz"); vp = os.path.join(video_dir, vn + ".mp4")
        if os.path.exists(out) or not os.path.exists(vp):
            continue
        sha = file_sha256(vp)
        if sha != manifest[vn]:
            log.write(json.dumps({"video": vn, "error": "video_sha256_mismatch", "sha256": sha}) + "\n"); log.flush()
            n_fail += 1; continue
        rec = extract_video(vp, out + ".tmp.npz", wb, workers)
        bad = validate_npz(out + ".tmp.npz", vp)
        if bad:
            rec.update(error="invalid_output", problems=bad)
            log.write(json.dumps(rec) + "\n"); log.flush(); n_fail += 1; continue
        rec.update(video_sha256=sha, arrays_sha256=arrays_sha256(out + ".tmp.npz"))
        os.replace(out + ".tmp.npz", out)
        rec.update(npz_sha256=file_sha256(out), seconds_unzip=0.0)
        if delete_after:
            os.remove(vp); rec["video_copy_deleted"] = True
        log.write(json.dumps(rec) + "\n"); log.flush()
        print(f"{vn} frames={rec['frames']} pose={rec['seconds_pose']:.0f}s", flush=True)
    log.close()
    return n_fail


def zip_video_index(zf):
    return {os.path.splitext(os.path.basename(n))[0]: n for n in zf.namelist() if n.lower().endswith(".mp4")}


class VideoPose:
    def __init__(self, npz):
        z = np.load(npz)
        self.K, self.S, self.n_persons = z["K"], z["S"], z["n_persons"]
        self.fps, self.frame_wh = float(z["fps"]), tuple(int(x) for x in z["frame_wh"])
        self.n = len(self.K)
        self._signer = None

    def frame_range(self, s, e):
        """Frames of the window [s, e) seconds: f0 = round(s * fps), f1 = round(e * fps), clamped."""
        return max(0, int(round(s * self.fps))), min(self.n, int(round(e * self.fps)))

    def clip_pose(self, s, e):
        """Signer-selected (K (T,133,2), S (T,133), t0, n_multi) over the window, or None if it holds no frame."""
        f0, f1 = self.frame_range(s, e)
        if f1 <= f0:
            return None
        kl = [self.K[t, :self.n_persons[t]] for t in range(f0, f1)]
        sl = [self.S[t, :self.n_persons[t]] for t in range(f0, f1)]
        K, S, n_multi = L.select_signer(kl, sl)
        return K, S, f0 / self.fps, n_multi

    def signer_track(self):
        """Signer-selected pose over the WHOLE video (for video-level activity), cached."""
        if self._signer is None:
            self._signer = self.clip_pose(0.0, self.n / self.fps)
        return self._signer
