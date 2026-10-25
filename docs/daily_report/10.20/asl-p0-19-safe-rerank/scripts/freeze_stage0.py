"""Write STAGE0_FREEZE.json: sha256 of the Stage 0 plan, config, code, verdict-test output and frozen external inputs.
Runs the plan-code verdict test first; refuses to freeze if it fails. Usage: python -I freeze_stage0.py
"""
import datetime, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p019_common import EXP, P014, P016, sha256  # noqa: E402

t = subprocess.run([sys.executable, "-I", os.path.join(EXP, "scripts", "test_stage0_verdict.py")],
                   capture_output=True, text=True)
if t.returncode != 0:
    raise SystemExit("verdict test failed; freeze not allowed\n" + t.stdout + t.stderr)
open(os.path.join(EXP, "config", "stage0_verdict_test_output.txt"), "w").write(t.stdout)

own = ["EXPERIMENT_PLAN.md", "config/stage0_config.json", "config/stage0_verdict_test_output.txt",
       "scripts/p019_common.py", "scripts/decode_topk.py", "scripts/stage0_analyze.py", "scripts/stage0_verdict.py",
       "scripts/test_stage0_verdict.py", "scripts/run_stage0_vm.sh"]
ext = [os.path.join(P014, p) for p in ("splits/manifest.csv", "full_run/vm_decode/predictions.jsonl",
                                       "scripts/build_concepts.py", "scripts/extract_representations.py",
                                       "concepts/concept_list_v1.csv")] + \
      [os.path.join(P016, p) for p in ("scripts/holdout_guard.py", "scripts/verdict_policy.py", "holdout/HOLDOUT.sha256")]
files = {p: sha256(os.path.join(EXP, p)) for p in own}
files.update({os.path.relpath(p, EXP): sha256(p) for p in ext})
json.dump({"experiment": "P0-19 Stage 0", "frozen_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "verdict_test": t.stdout.strip(), "files": files}, open(os.path.join(EXP, "STAGE0_FREEZE.json"), "w"), indent=1)
print(t.stdout.strip()); print(f"STAGE0_FREEZE.json: {len(files)} files")
