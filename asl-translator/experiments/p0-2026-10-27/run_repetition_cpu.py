"""CPU launcher for decode_repetition.py (unmodified). Adds guards only; no decoding argument is touched.

- hides CUDA and MPS before torch is used, so nothing can be placed on an accelerator;
- refuses to start unless the canonical list is exactly R01-R45 and passes the P0-16 holdout guard;
- wraps transformers generate() as a pass-through that asserts every model parameter and input tensor is on CPU,
  and records the device, generation kwargs and wall time of every call to <out>.calls.json.

Usage (repo root):
  /opt/anaconda3/envs/unisign-cpu-arm64/bin/python -I asl-translator/experiments/p0-2026-10-27/run_repetition_cpu.py \
      --unisign ... --checkpoint ... --mt5 ... --pose-dir ... --out ...
"""
import json, os, runpy, sys, time
from pathlib import Path

os.environ['CUDA_VISIBLE_DEVICES'] = ''
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
out = Path(sys.argv[sys.argv.index('--out') + 1])

records = [json.loads(l) for l in (REPO / 'asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/runs/full45/A_official/run1/candidates.jsonl').read_text().splitlines()]
assert sorted(r['review_id'] for r in records) == [f'R{i:02d}' for i in range(1, 46)], 'unexpected case list'
assert {r['domain'] for r in records} == {'A_official'} and len({r['clip_id'] for r in records}) == 45
sys.path.insert(0, str(REPO / 'docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts'))
from holdout_guard import assert_not_holdout
assert_not_holdout([r['clip_id'] for r in records])

import torch
torch.backends.mps.is_available = lambda: False
torch.backends.mps.is_built = lambda: False
assert not torch.cuda.is_available()

from transformers.generation.utils import GenerationMixin
_generate = GenerationMixin.generate
calls = []


def checked_generate(self, *args, **kw):
    devs = {p.device.type for p in self.parameters()}
    devs |= {v.device.type for v in kw.values() if torch.is_tensor(v)}
    assert devs == {'cpu'}, f'non-CPU device in generate: {devs}'
    t0 = time.perf_counter()
    seq = _generate(self, *args, **kw)
    calls.append({'devices': sorted(devs), 'seconds': round(time.perf_counter() - t0, 4),
                  'kwargs': {k: v for k, v in kw.items() if not torch.is_tensor(v)}})
    Path(str(out) + '.calls.json').write_text(json.dumps({'torch': torch.__version__, 'threads': torch.get_num_threads(),
                                                           'calls': calls}, indent=1))
    return seq


GenerationMixin.generate = checked_generate
t0 = time.perf_counter()
sys.argv = [str(HERE / 'decode_repetition.py')] + sys.argv[1:]
try:
    runpy.run_path(str(HERE / 'decode_repetition.py'), run_name='__main__')
finally:
    print(f'wall_seconds={time.perf_counter() - t0:.1f} generate_calls={len(calls)}', flush=True)
