# P0-12: paired clip-level bootstrap (2000 resamples, seed 0) of corpus BLEU-4 (official sableu) for each planned
# single-variable contrast. Same 128 clips/references for both arms of every contrast.
# Usage: python contrasts.py <Uni-Sign repo> <manifest.csv> <ours_5p39.jsonl> <out.json> NAME=<pres.txt> ...
#   Optional SEG=<data/segment_alignment_128.json> adds the IoU-stratified V2 interaction check.
#   NAME 'ours_5p39_historical_cpu' is built automatically from ours_5p39.jsonl; 'authors_released' from the repo.
import sys, re, json, csv
import numpy as np
U, manifest, ours_jsonl, out_json = sys.argv[1:5]
sys.path.insert(0, U)
from SLRT_metrics import sableu
ids = [r['how2sign_id'] for r in csv.DictReader(open(manifest))]
ours = {json.loads(l)['clip_id']: json.loads(l) for l in open(ours_jsonl)}
refs = [ours[i]['reference'] for i in ids]
def load(p):
    d = {}
    for line in open(p, encoding='utf-8'):
        m = re.match(r'sample: (.*?), prediction: (.*)$', line.rstrip('\n'))
        if m: d[m.group(1).replace('.mp4', '')] = m.group(2)
    return d
S = {'authors_released': load(U + '/out/eval_how2sign_pose_only/test_tmp_pres.txt'),
     'ours_5p39_historical_cpu': {i: ours[i]['prediction'] for i in ids}}
SEG = None
for a in sys.argv[5:]:
    k, p = a.split('=', 1)
    if k == 'SEG': SEG = json.load(open(p))
    else: S[k] = load(p)
# (label, variable isolated, arm_new, arm_base): delta = arm_new - arm_base
PLAN = [
    ('official path reproduces authors on subset', 'path check', 'A_official', 'authors_released'),
    ('V3 pose extractor model', 'V3', 'A_official', 'C_ours_on_official_crop'),
    ('V1 timestamp alignment', 'V1', 'C_ours_on_official_crop', 'B_aspect'),
    ('V2 crop / coordinate normalization', 'V2', 'B_aspect', 'B_ours_5p39'),
    ('V4a batch 8 + worker RNG (our input)', 'V4', 'B_ours_5p39', 'B_ours_5p39_bs1_nw0'),
    ('V4b CUDA vs CPU (+ loader class), batch 1', 'V4', 'B_ours_5p39_bs1_nw0', 'ours_5p39_historical_cpu'),
    ('V4a batch 8 + worker RNG (official input)', 'V4', 'A_official', 'A_official_bs1_nw0'),
    ('seed noise 43 vs 42 (official input)', 'noise', 'A_official_seed43', 'A_official'),
    ('seed noise 44 vs 42 (official input)', 'noise', 'A_official_seed44', 'A_official'),
    ('total pipeline gap (GPU, all variables)', 'total', 'A_official', 'B_ours_5p39'),
    ('reference: authors vs our historical', 'reference', 'authors_released', 'ours_5p39_historical_cpu'),
]
def b4(sys_, idx): return sableu(references=[refs[i] for i in idx], hypotheses=[S[sys_][ids[i]] for i in idx], tokenizer='13a')['bleu4']
rng = np.random.default_rng(0); B = [rng.integers(0, len(ids), len(ids)) for _ in range(2000)]
full = np.arange(len(ids)); res = []
for label, var, new, base in PLAN:
    if new not in S or base not in S or any(i not in S[new] or i not in S[base] for i in ids):
        res.append({'contrast': label, 'variable': var, 'new': new, 'base': base, 'status': 'not available'}); continue
    d = b4(new, full) - b4(base, full)
    boot = np.array([b4(new, ix) - b4(base, ix) for ix in B])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    res.append({'contrast': label, 'variable': var, 'new': new, 'base': base, 'bleu4_new': round(b4(new, full), 2),
                'bleu4_base': round(b4(base, full), 2), 'delta': round(d, 2), 'ci95': [round(lo, 2), round(hi, 2)],
                'ci_excludes_0': bool(lo > 0 or hi < 0)})
# interaction check: V2 (geometry) effect separately on poorly / well aligned clips
if SEG is not None and all(k in S for k in ('B_aspect', 'B_ours_5p39')):
    for lab, sel in (('IoU<0.5', lambda v: v < 0.5), ('IoU>=0.5', lambda v: v >= 0.5)):
        idx = np.array([n for n, i in enumerate(ids) if sel(SEG[i]['iou'])])
        d = b4('B_aspect', idx) - b4('B_ours_5p39', idx)
        boot = np.array([b4('B_aspect', idx[ix]) - b4('B_ours_5p39', idx[ix]) for ix in (rng.integers(0, len(idx), len(idx)) for _ in range(2000))])
        lo, hi = np.percentile(boot, [2.5, 97.5])
        res.append({'contrast': f'V2 interaction check, {lab}', 'variable': 'V2xV1', 'n': len(idx), 'delta': round(d, 2),
                    'ci95': [round(lo, 2), round(hi, 2)], 'ci_excludes_0': bool(lo > 0 or hi < 0)})
json.dump(res, open(out_json, 'w'), indent=1)
for r in res: print(r)
