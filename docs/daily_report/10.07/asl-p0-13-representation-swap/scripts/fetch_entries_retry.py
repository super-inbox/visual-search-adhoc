# Range-fetch selected entries from the split official zip (concatenated-offset addressing), verify CRC32.
import json, sys, os, struct, zlib, subprocess, binascii
idx = json.load(open(sys.argv[1])); outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
KIND = sys.argv[3] if len(sys.argv) > 3 else 'pose'
if KIND == 'pose':
    PART = 2147483648; SUF = ['.zip.00', '.zip.01', '.zip.02', '.zip.03']; SIZES = [PART] * 3 + [2023023631]; STEM = 'how2sign_pose_format'; EXT = '.pkl'
else:
    PART = 4294967296; SUF = ['.zip.aa', '.zip.ab', '.zip.ac', '.zip.ad', '.zip.ae']; SIZES = [PART] * 4 + [3010900187]; STEM = 'how2sign_rgb_format'; EXT = '.mp4'
BASE = "https://huggingface.co/ZechengLi19/Uni-Sign/resolve/main/" + STEM + "%s"
def fetch(off, n):
    buf = b''
    while n > 0:
        pi = off // PART; po = off % PART; take = min(n, SIZES[pi] - po)
        r = subprocess.run(['curl', '-sSL', '--fail', '--retry', '8', '--retry-all-errors', '--retry-delay', '10', '-r', f'{po}-{po+take-1}', BASE % SUF[pi]], capture_output=True, check=True).stdout
        assert len(r) == take, (len(r), take)
        buf += r; off += take; n -= take
    return buf
ok = 0
for cid, e in idx.items():
    dst = os.path.join(outdir, cid + EXT)
    if os.path.exists(dst) and os.path.getsize(dst) == e['usz']: ok += 1; continue
    h = fetch(e['lho'], 30)
    assert h[:4] == b'PK\x03\x04'
    nlen, elen = struct.unpack('<HH', h[26:30]); crc_l = struct.unpack('<I', h[14:18])[0]
    comp = fetch(e['lho'] + 30 + nlen + elen, e['csz'])
    data = zlib.decompress(comp, -15) if e['method'] == 8 else comp
    assert len(data) == e['usz'], cid
    crc = binascii.crc32(data) & 0xffffffff
    open(dst, 'wb').write(data); ok += 1
    assert crc == e["crc"], ("CRC MISMATCH", cid)
    print(cid, len(data), "crc ok", flush=True)
print('done', ok)
