"""P0-18: content hash of Uni-Sign pose pkls (array bytes + dtype + shape of every keypoints / scores entry, and w_h),
loaded the way decode_dir.py loads them (numpy>=2 pickles remapped under numpy 1.x). Used to show that a pkl built on
the Mac (numpy 2) reaches the T4 decoder (numpy 1) with bit-identical arrays.

Usage: python -I pkl_content_hash.py --pose-dir DIR --ids IDS.txt --out OUT.json
"""
import argparse, hashlib, io, json, os, pickle, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


class _Np2Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module.startswith("numpy._core") and int(np.__version__.split(".")[0]) < 2:
            module = "numpy.core" + module[len("numpy._core"):]
        return super().find_class(module, name)


def content_hash(path):
    d = _Np2Unpickler(io.BytesIO(open(path, "rb").read())).load(); h = hashlib.sha256()
    for k in ("keypoints", "scores"):
        for x in d[k]:
            x = np.ascontiguousarray(x); h.update(f"{x.dtype.str}{x.shape}".encode()); h.update(x.tobytes())
    h.update(json.dumps([int(v) for v in d.get("w_h", d.get("frame_wh", []))]).encode())
    return h.hexdigest()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pose-dir", required=True); ap.add_argument("--ids", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = {c: content_hash(os.path.join(a.pose_dir, c + ".pkl")) for c in open(a.ids).read().split()}
    json.dump({"numpy": np.__version__, "hashes": out}, open(a.out, "w"), indent=1)
    print(len(out), "pkls, numpy", np.__version__)
