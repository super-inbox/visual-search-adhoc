# P0-12: clip-level bootstrap (2000 resamples, seed 0) of corpus BLEU-4 (official sableu) for authors vs ours,
# split by segment IoU (ours vs re-aligned) < 0.5 / >= 0.5. Existing predictions only.
import sys, csv, json, numpy as np
U, per_clip, out = sys.argv[1:4]; sys.path.insert(0, U)
from SLRT_metrics import sableu
rows = list(csv.DictReader(open(per_clip)))
def bleu(rs, key): return sableu(references=[r['reference'] for r in rs], hypotheses=[r[key] for r in rs], tokenizer='13a')['bleu4']
rng = np.random.default_rng(0); res = {}
groups = {'iou_lt_0.5': [r for r in rows if float(r['segment_iou_ours_vs_realigned']) < 0.5],
          'iou_ge_0.5': [r for r in rows if float(r['segment_iou_ours_vs_realigned']) >= 0.5]}
boot = {g: [] for g in groups}
for _ in range(2000):
    for g, rs in groups.items():
        s = [rs[i] for i in rng.integers(0, len(rs), len(rs))]
        a, o = bleu(s, 'authors_prediction'), bleu(s, 'our_previous_prediction')
        boot[g].append((a, o, o - a, o / a if a else np.nan))
for g, rs in groups.items():
    b = np.array(boot[g])
    res[g] = {'n': len(rs), 'authors_bleu4': round(bleu(rs, 'authors_prediction'), 2), 'ours_bleu4': round(bleu(rs, 'our_previous_prediction'), 2),
              'ours_minus_authors_95ci': [round(float(x), 2) for x in np.nanpercentile(b[:, 2], [2.5, 97.5])],
              'ours_over_authors_95ci': [round(float(x), 3) for x in np.nanpercentile(b[:, 3], [2.5, 97.5])]}
d = np.array(boot['iou_ge_0.5'])[:, 2] - np.array(boot['iou_lt_0.5'])[:, 2]
res['gap_difference_ge_minus_lt_95ci'] = [round(float(x), 2) for x in np.percentile(d, [2.5, 97.5])]
res['frac_boot_gap_smaller_when_aligned'] = round(float((d > 0).mean()), 4)
json.dump(res, open(out, 'w'), indent=1); print(json.dumps(res, indent=1))
