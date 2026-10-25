"""Contact sheet: frames at a fixed fps from a source-video span, labeled with source seconds.
usage: sheet.py VIDEO START END FPS COLS OUT [--crop x,y,w,h] [--width 320] [--mark a-b,c-d]"""
import argparse, subprocess, io
from PIL import Image, ImageDraw
ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("start", type=float); ap.add_argument("end", type=float)
ap.add_argument("fps", type=float); ap.add_argument("cols", type=int); ap.add_argument("out")
ap.add_argument("--crop"); ap.add_argument("--width", type=int, default=320); ap.add_argument("--mark", default="")
a = ap.parse_args()
marks = [tuple(map(float, m.split("-"))) for m in a.mark.split(",") if m]
ts, t = [], a.start
while t < a.end - 1e-6:
    ts.append(round(t, 3)); t += 1 / a.fps
tiles = []
for t in ts:
    x, y, w, h = a.crop.split(",") if a.crop else (0,)*4
    vf = (f"crop={w}:{h}:{x}:{y}," if a.crop else "") + f"scale={a.width}:-2"
    png = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", a.video, "-frames:v", "1", "-vf", vf,
                          "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(png)).convert("RGB"); d = ImageDraw.Draw(im)
    inside = any(lo <= t <= hi for lo, hi in marks)
    d.rectangle([0, 0, 70, 16], fill="red" if inside else "black"); d.text((3, 2), f"{t:.2f}s", fill="yellow")
    if inside:
        d.rectangle([0, 0, im.width - 1, im.height - 1], outline="red", width=3)
    tiles.append(im)
w, h = tiles[0].size; rows = -(-len(tiles) // a.cols)
sheet = Image.new("RGB", (w * a.cols, h * rows), "white")
for i, im in enumerate(tiles):
    sheet.paste(im, ((i % a.cols) * w, (i // a.cols) * h))
sheet.save(a.out); print(a.out, len(tiles), sheet.size)
