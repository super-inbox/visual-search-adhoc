# VM, CPU only, no model. Preflight validation of the pilot inputs against the UNMODIFIED Uni-Sign S2T_Dataset.
# Checks (all must pass; written to <out.json>):
#   A  raw slice    every chunk PKL's keypoints / scores are exactly the runtime PKL's frames [start, end), w_h unchanged
#   B  lengths      S2 and S3 have no chunk > 256 frames; S1 has exactly the planned chunks > 256 frames
#   C  sampling     loading every S2 / S3 chunk with the default max_length 256 never calls random.sample (no subsampling);
#                   in S1, random.sample is called exactly for the chunks > 256 frames
#   D  no extra op  for S2 / S3 the loader output equals datasets.load_part_kp(raw frames [start, end)) exactly, i.e. the
#                   loader adds nothing beyond its own per-sequence normalisation
#   E  U36          U36 PKLs + labels are byte copies of the runtime inputs (sha256)
# Reported, not gated: datasets.crop_scale computes ONE body bounding box per loaded sequence, so a chunk is normalised
# with its own box, not the full clip's. scale_ratio = chunk body scale / full-clip body scale (all frames), per chunk.
# Usage: python -I check_loader_chunks.py <Uni-Sign worktree> <PILOT root> <runtime pose dir> <runtime labels> <plan dir> <out.json>
import csv, hashlib, json, os, pickle, sys, types
U, PILOT, RT_POSE, RT_LABELS, PLAN_DIR, OUT = sys.argv[1:7]
sys.path.insert(0, U)
cfg = types.ModuleType('config'); exec(open(os.path.join(U, 'config.py')).read(), cfg.__dict__); sys.modules['config'] = cfg
import numpy as np, torch, utils, datasets  # noqa: E402

sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
plan = list(csv.DictReader(open(os.path.join(PLAN_DIR, 'chunk_plan.csv'))))
fails, rep = [], {'arms': {}}
def need(ok, msg):
    if not ok: fails.append(msg)

calls = []
_orig_sample = datasets.random.sample
def spy_sample(pop, k):
    calls.append(len(pop)); return _orig_sample(pop, k)
datasets.random.sample = spy_sample

def dataset(arm):
    datasets.pose_dirs['How2Sign'] = os.path.join(PILOT, arm, '{}-pose-rtmpose-192')
    args = utils.get_args_parser().parse_args(['--dataset', 'How2Sign', '--task', 'SLT', '--batch-size', '1'])
    assert args.max_length == 256
    return datasets.S2T_Dataset(path=os.path.join(PILOT, arm, 'labels.test_pilot'), args=args, phase='test')

def body_scale(kp, sc):
    _, s, _ = datasets.crop_scale(np.concatenate([np.stack([k[0][[0] + list(range(3, 11))] for k in kp]),
                                                  np.stack([c[0][[0] + list(range(3, 11))] for c in sc])[..., None]], -1), 0.3)
    return float(s)

full_cache = {}
def full(clip):
    if clip not in full_cache:
        full_cache[clip] = pickle.load(open(os.path.join(RT_POSE, clip + '.pkl'), 'rb'))
    return full_cache[clip]

for arm in ('S1', 'S2', 'S3'):
    rows = [r for r in plan if r['arm'] == arm]
    ds = dataset(arm)
    need(len(ds) == len(rows), f'{arm}: dataset has {len(ds)} entries, plan {len(rows)}')
    n_long, n_called, ratios = 0, 0, []
    for j, r in enumerate(rows):
        s, e, name, clip = int(r['start']), int(r['end']), r['chunk_name'], r['clip_id']
        F = full(clip); Cpk = pickle.load(open(os.path.join(PILOT, arm, 'test-pose-rtmpose-192', name + '.pkl'), 'rb'))
        # A
        need(len(Cpk['keypoints']) == len(Cpk['scores']) == e - s, f'{arm} {name}: length != end-start')
        need(all(np.array_equal(a, b) for a, b in zip(Cpk['keypoints'], F['keypoints'][s:e]))
             and all(np.array_equal(a, b) for a, b in zip(Cpk['scores'], F['scores'][s:e])) and list(Cpk['w_h']) == list(F['w_h']),
             f'{arm} {name}: chunk PKL != runtime frames [{s},{e})')
        # B / C
        long = e - s > 256; n_long += long
        calls.clear(); name_s, pose, *_ = ds[j]
        need(name_s == name + '.mp4', f'{arm}: entry {j} is {name_s}, plan says {name}')
        n_called += bool(calls)
        need(bool(calls) == long, f'{arm} {name}: random.sample called={bool(calls)} but chunk>256={long}')
        # D (deterministic arms only)
        if not long:
            ref = datasets.load_part_kp(F['keypoints'][s:e], F['scores'][s:e], force_ok=True)
            need(all(torch.equal(pose[k], ref[k]) for k in ref), f'{arm} {name}: loader output != load_part_kp(frames [{s},{e}))')
        ratios.append(body_scale(Cpk['keypoints'], Cpk['scores']) / body_scale(F['keypoints'], F['scores']))
    if arm in ('S2', 'S3'):
        need(n_long == 0 and n_called == 0, f'{arm}: {n_long} chunks > 256, random.sample called for {n_called}')
    else:
        planned = sum(r['subsampled_by_loader'] == 'True' for r in rows)
        need(n_long == planned == n_called, f'S1: {n_long} chunks > 256, planned {planned}, sampled {n_called}')
    q = np.percentile(ratios, [0, 10, 50, 90, 100]).round(3).tolist()
    rep['arms'][arm] = {'chunks': len(rows), 'chunks_gt256': n_long, 'random_sample_called': n_called,
                        'body_scale_ratio_chunk_over_full_min_p10_median_p90_max': q,
                        'chunks_scale_ratio_lt_0.8': int(sum(x < 0.8 for x in ratios))}

# E
u = os.path.join(PILOT, 'U36', 'test-pose-rtmpose-192')
need(sorted(os.listdir(u)) == sorted(os.listdir(RT_POSE)) and all(sha(os.path.join(u, f)) == sha(os.path.join(RT_POSE, f)) for f in os.listdir(u)),
     'U36 PKLs are not byte copies of the runtime PKLs')
need(sha(os.path.join(PILOT, 'U36', 'labels.test_pilot')) == sha(RT_LABELS), 'U36 labels != runtime labels')
rep['U36_pkls'] = len(os.listdir(u))
rep['fails'] = fails; rep['pass'] = not fails
json.dump(rep, open(OUT, 'w'), indent=1)
print(json.dumps(rep, indent=1))
sys.exit(1 if fails else 0)
