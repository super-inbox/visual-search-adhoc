"""P0-18: write FREEZE.json (P0-16 SANITY_GATE_POLICY §3). Refuses unless the plan-code verdict test passes and the
frozen config carries every threshold the verdict code reads.

Frozen = every scripts/*.py, config/*, ref/** and EXPERIMENT_PLAN.md / DEVELOPMENT_RESULTS.md. The verdict test's
output is stored in config/verdict_test_output.txt (hashed with the rest). The H18 runner refuses to start if any
frozen file differs from its hash here.

Usage: python3 -I make_freeze.py
"""
import glob, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import p018_verdict as V  # noqa: E402

r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "test_p018_verdict.py")], capture_output=True, text=True)
if r.returncode != 0:
    sys.exit(f"REFUSED: verdict consistency test failed:\n{r.stdout}{r.stderr}")
open(os.path.join(EXP, "config", "verdict_test_output.txt"), "w").write(r.stdout)

CFG = json.load(open(os.path.join(EXP, "config", "p018_config.json")))
dummy = {"delta_B_minus_A": {"bleu4": {"delta": 0.0, "ci95": [0.0, 0.0]}, "wer": {"delta": 0.0, "ci95": [0.0, 0.0]}},
         "gap_recovery": {"gap_bleu4": 1.0, "recovery_bleu4": 0.0}, "failure_rate": 0.0,
         "runtime": {"preproc_s_per_clip": 0.0}, "primary_arm": "X", "point": {"X": {"len_ratio": 1.0}}}
V.criteria(dummy, CFG["thresholds"])                                       # KeyError if a threshold is missing
if CFG.get("primary_arm") not in ("B_auto", "B_crop_only", "B_time_only", "B_lag_only"):
    sys.exit(f"REFUSED: config primary_arm {CFG.get('primary_arm')!r} is not an automatic arm")

files = sorted(set(glob.glob(os.path.join(EXP, "scripts", "*.py")) + glob.glob(os.path.join(EXP, "config", "*"))
                   + glob.glob(os.path.join(EXP, "ref", "**", "*"), recursive=True)
                   + [os.path.join(EXP, f) for f in ("EXPERIMENT_PLAN.md", "DEVELOPMENT_RESULTS.md")]))
files = [f for f in files if os.path.isfile(f) and "__pycache__" not in f]
missing = [f for f in ("EXPERIMENT_PLAN.md", "DEVELOPMENT_RESULTS.md") if not os.path.exists(os.path.join(EXP, f))]
if missing:
    sys.exit(f"REFUSED: missing {missing}")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
P016 = os.path.join(os.path.dirname(EXP), "asl-p0-16-experimental-credibility", "holdout", "HOLDOUT.sha256")
out = {"experiment": "P0-18 automatic preprocessing", "frozen_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
       "files": {os.path.relpath(f, EXP): sha(f) for f in files},
       "verdict_test": {"passed": True, "output": r.stdout.strip()},
       "p016_HOLDOUT.sha256": sha(P016),
       "h18_opened": False}
json.dump(out, open(os.path.join(EXP, "FREEZE.json"), "w"), indent=1)
print(f"FREEZE.json: {len(out['files'])} files; {r.stdout.strip()}")
