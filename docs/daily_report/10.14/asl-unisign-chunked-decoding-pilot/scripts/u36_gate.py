# U36 reproducibility gate (VM right after the U36 run, and again locally inside analyze_pilot.py). Stdlib only.
# PASS only if the U36 run (unchunked, all 128 entries, read from the pilot input copy) gives, for each of the 36 pilot
# clips, a prediction byte-identical to the committed R100 A_official prediction (asl-p0-12-full128-fp16/predictions/
# A_official.txt, sha256 d865008b...; R100 reproduced it exactly). The other 92 lines are reported, not gated.
# Exit 0 only on PASS. Fixed before any pilot output exists.
# Usage: python -I u36_gate.py <U36 run dir> <committed A_official.txt> <plan dir> <out.json>
import hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pilot_join import read_pres, load_plan  # noqa: E402

BASELINE_SHA = 'd865008bc0a16ba0fb3bceb6f78f5a7153febe1d69ba756cc83f918d57300e4a'
run, base, plan_dir, out = sys.argv[1:5]
r = {'baseline_sha256_ok': hashlib.sha256(open(base, 'rb').read()).hexdigest() == BASELINE_SHA}
B, U = read_pres(base), read_pres(os.path.join(run, 'test_tmp_pres.txt'))
_, clips = load_plan(plan_dir)
pilot = [c['clip_id'] for c in clips]
b, u = dict(B), dict(U)
r['u36_lines'] = len(U)
r['same_order_as_R100'] = [n for n, _ in U] == [n for n, _ in B]
r['pilot36_identical'] = sum(u.get(c) == b[c] for c in pilot)
r['pilot36_differing'] = [c for c in pilot if u.get(c) != b[c]]
r['all128_identical'] = sum(u.get(n) == t for n, t in B)
r['pass'] = r['baseline_sha256_ok'] and len(U) == 128 and r['same_order_as_R100'] and r['pilot36_identical'] == 36
json.dump(r, open(out, 'w'), indent=1)
print(json.dumps(r, indent=1))
sys.exit(0 if r['pass'] else 1)
