"""P0-14: list the official Uni-Sign How2Sign pose archive without downloading it.

Reads only the zip64 end-of-central-directory records and the central directory (a few MB) of the split archive
HF ZechengLi19/Uni-Sign how2sign_pose_format.zip.00-.03 via HTTP range requests (concatenated-offset addressing,
same as 10.07/.../fetch_entries_retry.py). Writes one row per entry: split dir, clip id, sizes, offsets, CRC, so
the extraction step can range-fetch or stream exactly the clips it needs.

Usage: python3 -I list_pose_archive.py OUT_CSV
"""
import csv, struct, subprocess, sys

PART = 2147483648
SUF = [".zip.00", ".zip.01", ".zip.02", ".zip.03"]
SIZES = [PART] * 3 + [2023023631]
TOTAL = sum(SIZES)
BASE = "https://huggingface.co/ZechengLi19/Uni-Sign/resolve/main/how2sign_pose_format%s"

def fetch(off, n):
    buf = b""
    while n > 0:
        pi, po = off // PART, off % PART
        take = min(n, SIZES[pi] - po)
        r = subprocess.run(["curl", "-sSL", "--fail", "--retry", "5", "-r", f"{po}-{po + take - 1}", BASE % SUF[pi]],
                           capture_output=True, check=True).stdout
        assert len(r) == take, (len(r), take)
        buf += r; off += take; n -= take
    return buf

tail = fetch(TOTAL - 65536, 65536)
i = tail.rfind(b"PK\x05\x06")
assert i >= 0, "EOCD not found"
cd_n, cd_size, cd_off = struct.unpack("<HII", tail[i + 10:i + 20])
j = tail.rfind(b"PK\x06\x07", 0, i)  # zip64 locator
if j >= 0:
    z64_off = struct.unpack("<Q", tail[j + 8:j + 16])[0]
    z = fetch(z64_off, 56)
    assert z[:4] == b"PK\x06\x06"
    cd_n, cd_size, cd_off = struct.unpack("<QQQ", z[32:56])
cd = fetch(cd_off, cd_size)

rows, p = [], 0
while p < len(cd):
    assert cd[p:p + 4] == b"PK\x01\x02", p
    method, = struct.unpack("<H", cd[p + 10:p + 12])
    crc, csz, usz = struct.unpack("<III", cd[p + 16:p + 28])
    nlen, elen, clen = struct.unpack("<HHH", cd[p + 28:p + 34])
    lho, = struct.unpack("<I", cd[p + 42:p + 46])
    name = cd[p + 46:p + 46 + nlen].decode("utf-8", "replace")
    extra = cd[p + 46 + nlen:p + 46 + nlen + elen]
    q = 0
    while q + 4 <= len(extra):  # zip64 extended info overrides 0xFFFFFFFF fields, in order usz, csz, lho
        hid, hlen = struct.unpack("<HH", extra[q:q + 4])
        if hid == 1:
            vals, k = extra[q + 4:q + 4 + hlen], 0
            if usz == 0xFFFFFFFF: usz, = struct.unpack("<Q", vals[k:k + 8]); k += 8
            if csz == 0xFFFFFFFF: csz, = struct.unpack("<Q", vals[k:k + 8]); k += 8
            if lho == 0xFFFFFFFF: lho, = struct.unpack("<Q", vals[k:k + 8]); k += 8
        q += 4 + hlen
    p += 46 + nlen + elen + clen
    if name.endswith(".pkl"):
        d, f = name.rsplit("/", 1) if "/" in name else ("", name)
        rows.append({"dir": d, "clip_id": f[:-4], "csz": csz, "usz": usz, "lho": lho, "crc": crc, "method": method})

with open(sys.argv[1], "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
from collections import Counter
print("entries", cd_n, "pkl", len(rows), Counter(r["dir"] for r in rows))
print("compressed GB", round(sum(r["csz"] for r in rows) / 1e9, 2), "uncompressed GB", round(sum(r["usz"] for r in rows) / 1e9, 2))
