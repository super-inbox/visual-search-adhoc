"""P0-16 holdout guard. Every P0-18 / P0-19 DEVELOPMENT script must call assert_not_holdout() on its clip ids.

    import sys; sys.path.insert(0, "<path>/asl-p0-16-experimental-credibility/scripts")
    from holdout_guard import assert_not_holdout
    assert_not_holdout(clip_ids)                 # raises if any id is a How2Sign val clip or from a val video

Denies the WHOLE How2Sign val split (all 115 videos, including the clips excluded from H18/H19), checks
holdout/HOLDOUT.sha256 first, and is the only sanctioned way to read the holdout lists before a one-shot run.
"""
import csv, hashlib, os, re

_EXP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_H = os.path.join(_EXP, "holdout")


def _verify():
    for line in open(os.path.join(_H, "HOLDOUT.sha256")):
        h, name = line.split()
        if hashlib.sha256(open(os.path.join(_H, name), "rb").read()).hexdigest() != h:
            raise RuntimeError(f"holdout file changed: {name}")


def _deny():
    _verify()
    clips, videos = set(), set()
    for n in ("H18_clips.txt", "H19_clips.txt"):
        clips |= set(open(os.path.join(_H, n)).read().split())
    for n in ("H18_units.txt", "H19_units.txt"):
        for u in open(os.path.join(_H, n)).read().split():
            videos |= set(u.split("+"))
    for r in csv.DictReader(open(os.path.join(_H, "EXCLUDED.csv"))):
        clips.add(r["clip_id"]); videos.add(r["video_id"])
    return clips, videos


def assert_not_holdout(clip_ids):
    clips, videos = _deny()
    vid = lambda c: re.sub(r"_\d+(?:_\d+)*-\d+-rgb_front(\.mp4|\.pkl)?$", "", c)    # "<VIDEO_ID>_<k>[_<k2>]-<n>-rgb_front"
    bad = [c for c in clip_ids if c in clips or vid(c) in videos]
    if bad:
        raise RuntimeError(f"{len(bad)} sealed How2Sign-val clip(s) in development input, e.g. {bad[:3]}")
