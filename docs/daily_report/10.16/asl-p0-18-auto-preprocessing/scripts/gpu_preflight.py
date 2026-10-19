"""P0-18 GPU extractor preflight (run on the GPU host before any extraction).

1. records driver / CUDA / cuDNN / python / onnxruntime-gpu / rtmlib / opencv / numpy versions and model sha256;
2. asserts CUDAExecutionProvider is active for both rtmlib sessions;
3. asserts the run FAILS when CUDA is unavailable (subprocess with CUDA_VISIBLE_DEVICES="") instead of falling back;
4. extracts one video twice (pose_extract.extract_video, the production code) and requires identical arrays;
5. measures throughput and peak VRAM (nvidia-smi sampled every 0.5 s).

Usage: python -I gpu_preflight.py VIDEO.mp4 OUT_DIR [--workers 16]
"""
import argparse, hashlib, json, os, platform, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import pose_extract as PE  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("out")
ap.add_argument("--workers", type=int, default=16)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
rep = {"host": platform.node(), "python": sys.version.split()[0], "executable": sys.executable}
q = lambda *c: subprocess.run(list(c), capture_output=True, text=True).stdout.strip()
rep["nvidia_smi"] = q("nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader")
rep["cuda_driver_api"] = q("bash", "-c", "nvidia-smi | grep -o 'CUDA Version: [0-9.]*'")
rep["pip"] = {l.split()[0]: l.split()[1] for l in q(sys.executable, "-m", "pip", "list").splitlines()[2:]
              if l.split()[0].lower().startswith(("onnxruntime", "rtmlib", "opencv", "numpy", "nvidia-"))}
import onnxruntime as ort  # noqa: E402
rep["ort_build_info"] = getattr(ort.capi._pybind_state, "get_build_info", lambda: None)()
rep["env"] = PE.environment()

# 2. provider assertion (make_wholebody raises if CUDA EP is not first)
wb = PE.make_wholebody("cuda")
rep["sessions"] = {k: t.session.get_providers() for k, t in (("det", wb.det_model), ("pose", wb.pose_model))}
assert all(v[0] == "CUDAExecutionProvider" for v in rep["sessions"].values()), rep["sessions"]

# 3. no silent CPU fallback
r = subprocess.run([sys.executable, "-I", "-c", f"import sys; sys.path.insert(0, {HERE!r}); import pose_extract as PE; "
                    "PE.make_wholebody('cuda'); print('NO_ERROR')"],
                   env=dict(os.environ, CUDA_VISIBLE_DEVICES=""), capture_output=True, text=True)
rep["fallback_test"] = {"returncode": r.returncode, "raised": "NO_ERROR" not in r.stdout,
                        "stderr_tail": r.stderr.strip().splitlines()[-1:] if r.stderr else []}
assert rep["fallback_test"]["raised"], "onnxruntime fell back to CPU without raising"

# 4-5. determinism, throughput, VRAM
peak, stop = [0], threading.Event()


def sample():
    while not stop.is_set():
        try:
            peak[0] = max(peak[0], int(q("nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits")))
        except ValueError:
            pass
        time.sleep(0.5)


th = threading.Thread(target=sample, daemon=True); th.start()
runs = []
for i in (1, 2):
    o = os.path.join(a.out, f"run{i}.npz")
    rec = PE.extract_video(a.video, o, wb, a.workers)
    z = np.load(o); h = hashlib.sha256()
    for k in ("K", "S", "n_persons"):
        h.update(np.ascontiguousarray(z[k]).tobytes())
    rec["arrays_sha256"] = h.hexdigest(); rec["fps_throughput"] = round(rec["frames"] / rec["seconds_pose"], 1)
    runs.append(rec)
stop.set(); th.join()
rep["runs"] = runs
rep["deterministic"] = runs[0]["arrays_sha256"] == runs[1]["arrays_sha256"]
rep["peak_vram_mib"] = peak[0]
json.dump(rep, open(os.path.join(a.out, "gpu_preflight.json"), "w"), indent=1)
print(json.dumps({k: rep[k] for k in ("nvidia_smi", "cuda_driver_api", "sessions", "fallback_test", "deterministic",
                                      "peak_vram_mib")}, indent=1))
print("throughput fps:", [r_["fps_throughput"] for r_ in runs])
assert rep["deterministic"], "GPU extraction is not deterministic"
print("PREFLIGHT PASS")
