"""P0-18 oracle REFERENCE arm (pre-registered by P0-16 HOLDOUT_PLAN §6): official signer-crop, re-aligned clip videos
from Uni-Sign's HF archive, posed with our extractor exactly as P0-12 condition C. Never an input of the automatic
pipeline.

fetch(): range-fetch one archive member (P0-12 fetch_entries.py addressing over the split zip), verify CRC-32.
pose_p012(): rtmlib Wholebody lightweight on every frame, stored as P0-12 extract_rtmlib_lightweight.py did
(keypoints / (W, H), all persons, scores). A frame with no detected person gets one all-zero person with score 0
(Uni-Sign reads person 0 of every frame).
"""
import binascii, csv, struct, subprocess, time, zlib
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

PART = 4294967296
SUF = [".zip.aa", ".zip.ab", ".zip.ac", ".zip.ad", ".zip.ae"]
SIZES = [PART] * 4 + [3010900187]
REVISION = "eab251b7fe7e8521afc0e67be98add670ea40a0d"          # HF model repo commit (lastModified 2026-05-22)
BASE = "https://huggingface.co/ZechengLi19/Uni-Sign/resolve/" + REVISION + "/how2sign_rgb_format%s"


def load_index(tsv):
    return {r["name"].split("/", 1)[1][:-4]: (int(r["compressed_size"]), int(r["local_header_offset"]),
                                              int(r["crc32"], 16)) for r in csv.DictReader(open(tsv), delimiter="\t")}


def _range(off, n, tries=4):
    buf = b""
    while n > 0:
        pi, po = off // PART, off % PART
        take = min(n, SIZES[pi] - po)
        for k in range(tries):
            r = subprocess.run(["curl", "-sSL", "--fail", "-r", f"{po}-{po + take - 1}", BASE % SUF[pi]],
                               capture_output=True)
            if r.returncode == 0 and len(r.stdout) == take:
                break
            time.sleep(2 ** k)
        else:
            raise IOError(f"range fetch failed at {off}")
        buf += r.stdout; off += take; n -= take
    return buf


def fetch(entry, dst):
    csz, lho, crc = entry
    h = _range(lho, 30)
    assert h[:4] == b"PK\x03\x04", "bad local header"
    method = struct.unpack("<H", h[8:10])[0]
    nlen, elen = struct.unpack("<HH", h[26:30])
    comp = _range(lho + 30 + nlen + elen, csz)
    data = zlib.decompress(comp, -15) if method == 8 else comp
    if binascii.crc32(data) & 0xFFFFFFFF != crc:
        raise IOError("CRC mismatch")
    open(dst, "wb").write(data)
    return len(data)


def pose_p012(video_path, wb, workers=4):
    cap = cv2.VideoCapture(video_path); frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    cap.release()

    def one(fr):
        k, s = wb(np.uint8(fr)); H, W = fr.shape[:2]
        k = np.asarray(k, np.float64).reshape(-1, 133, 2); s = np.asarray(s, np.float32).reshape(-1, 133)
        if len(k) == 0:
            k, s = np.zeros((1, 133, 2)), np.zeros((1, 133), np.float32)
        return k / np.array([W, H])[None, None], s, [W, H]

    with ThreadPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(one, frames))
    return {"keypoints": [k for k, _, _ in res], "scores": [s for _, s, _ in res],
            "frame_wh": res[0][2] if res else None}
