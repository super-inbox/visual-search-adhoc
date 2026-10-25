"""Frame-difference motion energy in a box (signer torso/hands), source seconds. usage: motion.py VIDEO START END x,y,w,h STEP"""
import sys, subprocess, numpy as np
v, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); x, y, w, h = map(int, sys.argv[4].split(",")); step = float(sys.argv[5])
W, H = w // 4, h // 4
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", v, "-vf",
                      f"crop={w}:{h}:{x}:{y},scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(float)
fps = 30.0; e = np.r_[0, np.abs(np.diff(f, axis=0)).mean((1, 2))]
n = int(round(step * fps))
for i in range(0, len(e), n):
    s = e[i:i + n].mean(); print(f"{a + i / fps:6.2f}-{a + (i + n) / fps:6.2f}s  {s:5.2f} " + "#" * int(s * 4))
