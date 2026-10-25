# P0-12: confirm each prepared condition directory is consumed by the UNMODIFIED official Uni-Sign S2T_Dataset
# (the class fine_tuning.py --eval uses) exactly as on the GPU box. CPU, data pipeline only: no model is built,
# no inference. config.py is not edited: a stand-in `config` module with the same names is injected.
import sys, os, types, json, random
U, P012, out_json = sys.argv[1:4]
conds = sys.argv[4:] or ['A_official', 'B_ours_5p39', 'B_aspect', 'C_ours_on_official_crop']
sys.path.insert(0, U)
cfg = types.ModuleType('config')
exec(open(os.path.join(U, 'config.py')).read(), cfg.__dict__)
sys.modules['config'] = cfg
import torch, numpy as np
import utils, datasets
from torch.utils.data import DataLoader, SequentialSampler
report = {}
for cond in conds:
    datasets.pose_dirs['How2Sign'] = os.path.join(P012, cond, '{}-pose-rtmpose-192')
    args = utils.get_args_parser().parse_args(['--dataset', 'How2Sign', '--task', 'SLT', '--batch-size', '8'])
    utils.set_seed(args.seed)
    ds = datasets.S2T_Dataset(path=os.path.join(P012, 'labels.test_p012_128'), args=args, phase='test')
    dl = DataLoader(ds, batch_size=8, num_workers=0, collate_fn=ds.collate_fn, sampler=SequentialSampler(ds))
    n, T, shapes, zero_frac = 0, [], set(), []
    for src, tgt in dl:
        n += len(src['name_batch'])
        T += [int(x) for x in src['attention_mask'].sum(1)] if 'attention_mask' in src else []
        for k in ('body', 'left', 'right', 'face_all'):
            shapes.add((k, tuple(src[k].shape[2:])))
            zero_frac.append(float((src[k][..., 2] == 0).float().mean()))
    report[cond] = {'clips_loaded': n, 'pose_dir': ds.pose_dir, 'part_shapes_excl_BT': sorted(shapes),
                    'seq_len_after_cap_min_max': [min(T), max(T)] if T else None, 'mean_zeroed_frac_incl_padding': round(float(np.mean(zero_frac)), 4)}
    print(cond, report[cond], flush=True)
json.dump(report, open(out_json, 'w'), indent=1)
