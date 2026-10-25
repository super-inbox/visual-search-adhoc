# Condition B pose re-extraction: identical to Uni-Sign demo/online_inference.py pose_extraction()
# (rtmlib Wholebody mode="lightweight", onnxruntime), only device="cuda" -> "cpu" as in the 5.39 run.
import sys, os, csv, pickle, time
import cv2, numpy as np
from concurrent.futures import ThreadPoolExecutor
from rtmlib import Wholebody
manifest, videos_root, outdir = sys.argv[1:4]
os.makedirs(outdir, exist_ok=True)
wb = Wholebody(to_openpose=False, mode="lightweight", backend="onnxruntime", device="cpu")
def process_frame(frame):
    frame = np.uint8(frame); k, s = wb(frame); H, W, C = frame.shape; return k, s, [W, H]
for r in csv.DictReader(open(manifest)):
    cid = r['how2sign_id']; dst = os.path.join(outdir, cid + '.pkl')
    if os.path.exists(dst): continue
    t = time.time(); cap = cv2.VideoCapture(os.path.join(videos_root, cid + '.mp4')); frames = []
    while True:
        ok, f = cap.read()
        if not ok: break
        frames.append(f)
    cap.release()
    with ThreadPoolExecutor(max_workers=16) as ex:
        res = [f.result() for f in [ex.submit(process_frame, fr) for fr in frames]]
    data = {"keypoints": [k / np.array(wh)[None, None] for k, s, wh in res], "scores": [s for k, s, wh in res],
            "frame_wh": res[0][2] if res else None}
    pickle.dump(data, open(dst, 'wb'))
    print(f"{cid} frames={len(frames)} WH={data['frame_wh']} t={time.time()-t:.1f}s", flush=True)
print("DONE")
