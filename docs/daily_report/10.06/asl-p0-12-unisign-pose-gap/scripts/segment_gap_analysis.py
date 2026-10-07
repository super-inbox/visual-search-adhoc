# P0-12: does our-vs-authors BLEU gap track temporal segment misalignment? Existing predictions only; no inference.
import sys, json, re, csv
import numpy as np
U, ours_jsonl, seg_json, manifest, hist_csv, out_json, out_csv = sys.argv[1:8]
sys.path.insert(0, U)
from SLRT_metrics import sableu                      # official vendored sacrebleu 1.4.2 path (validated in E0)
import sacrebleu as pip_sacrebleu                    # pip sacrebleu, only for chrF / sentence-level stats
def load(p, key):
    d = {}
    for line in open(p, encoding='utf-8'):
        m = re.match(r'sample: (.*?), ' + key + r': (.*)$', line.rstrip('\n')); d[m.group(1)[:-4]] = m.group(2)
    return d
apred = load(U + '/out/eval_how2sign_pose_only/test_tmp_pres.txt', 'prediction')
aref = load(U + '/out/eval_how2sign_pose_only/test_tmp_refs.txt', 'ground-truth')
ours = {json.loads(l)['clip_id']: json.loads(l) for l in open(ours_jsonl)}
seg = json.load(open(seg_json))
man = {r['how2sign_id']: r for r in csv.DictReader(open(manifest))}
hist = {r['how2sign_id']: r for r in csv.DictReader(open(hist_csv))}
ids = list(ours)
def corpus(idset, src):
    hyps = [(apred[i] if src == 'authors' else ours[i]['prediction']) for i in idset]
    refs = [ours[i]['reference'] for i in idset]
    b = sableu(references=refs, hypotheses=hyps, tokenizer='13a')
    chrf = pip_sacrebleu.corpus_chrf(hyps, [refs]).score
    return dict(bleu1=round(b['bleu1'], 2), bleu2=round(b['bleu2'], 2), bleu3=round(b['bleu3'], 2), bleu4=round(b['bleu4'], 2), chrf=round(chrf, 2))
def rep3(s):
    w = s.lower().split(); g = [tuple(w[k:k + 3]) for k in range(len(w) - 2)]
    return len(g) > 0 and len(set(g)) < len(g)
def term(s): return s.rstrip()[-1:] in '.?!"'
def wer(h, r):
    import numpy as np
    h = h.lower().split(); r = r.lower().split()
    d = np.arange(len(h) + 1)
    for i in range(1, len(r) + 1):
        prev = d.copy(); d[0] = i
        for j in range(1, len(h) + 1):
            d[j] = min(prev[j] + 1, d[j - 1] + 1, prev[j - 1] + (r[i - 1] != h[j - 1]))
    return d[len(h)], len(r)
def summary(idset):
    out = {'n': len(idset)}
    for src in ('authors', 'ours'):
        c = corpus(idset, src)
        preds = [(apred[i] if src == 'authors' else ours[i]['prediction']) for i in idset]
        e = [wer(p, ours[i]['reference']) for p, i in zip(preds, idset)]
        c['wer'] = round(sum(x for x, _ in e) / sum(n for _, n in e), 4)
        c['exact_match'] = sum(p.strip().lower() == ours[i]['reference'].strip().lower() for p, i in zip(preds, idset))
        c['repeated_3gram_rate'] = round(np.mean([rep3(p) for p in preds]), 3)
        c['no_terminal_punct_rate'] = round(np.mean([not term(p) for p in preds]), 3)
        c['unique_prediction_rate'] = round(len(set(preds)) / len(preds), 3)
        toks = [t for p in preds for t in p.lower().split()]
        c['distinct_1'] = round(len(set(toks)) / max(len(toks), 1), 3)
        out[src] = c
    out['ours_over_authors_bleu4'] = round(out['ours']['bleu4'] / out['authors']['bleu4'], 3) if out['authors']['bleu4'] else None
    out['ours_over_authors_chrf'] = round(out['ours']['chrf'] / out['authors']['chrf'], 3)
    return out
iou = {i: seg[i]['iou'] for i in ids}
buckets = {'iou_eq_0': [i for i in ids if iou[i] == 0], 'iou_0_to_0.5': [i for i in ids if 0 < iou[i] < 0.5],
           'iou_0.5_to_0.9': [i for i in ids if 0.5 <= iou[i] < 0.9], 'iou_ge_0.9': [i for i in ids if iou[i] >= 0.9],
           'iou_lt_0.5': [i for i in ids if iou[i] < 0.5], 'iou_ge_0.5': [i for i in ids if iou[i] >= 0.5], 'all': ids}
res = {k: summary(v) for k, v in buckets.items()}
# per-clip sentence chrF, and rank correlation of (ours - authors) with IoU
def schrf(h, r): return pip_sacrebleu.sentence_chrf(h, [r]).score
def sbleu(h, r): return pip_sacrebleu.sentence_bleu(h, [r]).score
rows = []
for i in ids:
    r = ours[i]['reference']
    rows.append(dict(clip_id=i, reference=r, authors_prediction=apred[i], our_previous_prediction=ours[i]['prediction'],
        authors_sentence_bleu=round(sbleu(apred[i], r), 2), our_previous_sentence_bleu=round(sbleu(ours[i]['prediction'], r), 2),
        authors_sentence_chrf=round(schrf(apred[i], r), 2), our_previous_sentence_chrf=round(schrf(ours[i]['prediction'], r), 2),
        our_clip_start_s=seg[i]['ours_start'], our_clip_end_s=seg[i]['ours_end'],
        realigned_start_s=seg[i]['realigned_start'], realigned_end_s=seg[i]['realigned_end'],
        segment_iou_ours_vs_realigned=iou[i], realigned_window_covered_by_our_clip=seg[i]['frac_of_realigned_covered_by_ours'],
        our_frames=int(hist[i]['n_frames']), duration_s=float(man[i]['duration_s']),
        authors_repeated_3gram=rep3(apred[i]), ours_repeated_3gram=rep3(ours[i]['prediction']),
        authors_no_terminal_punct=not term(apred[i]), ours_no_terminal_punct=not term(ours[i]['prediction'])))
def _rank(a):
    a = np.asarray(a, float); o = a.argsort(kind='mergesort'); r = np.empty(len(a)); r[o] = np.arange(len(a))
    for v in np.unique(a):  # average ties
        m = a == v; r[m] = r[m].mean()
    return r
def spearmanr(x, y, n_perm=20000, seed=0):
    rx, ry = _rank(x), _rank(y); rho = np.corrcoef(rx, ry)[0, 1]
    rng = np.random.default_rng(seed); null = np.array([np.corrcoef(rx, rng.permutation(ry))[0, 1] for _ in range(n_perm)])
    return rho, float((np.abs(null) >= abs(rho)).mean() + 1 / n_perm)
d = [x['our_previous_sentence_chrf'] - x['authors_sentence_chrf'] for x in rows]
rho, p = spearmanr([x['segment_iou_ours_vs_realigned'] for x in rows], d)
res['spearman_iou_vs_chrf_delta'] = {'rho': round(float(rho), 3), 'p': float(p), 'delta': 'ours_sentence_chrf - authors_sentence_chrf'}
rho2, p2 = spearmanr([x['segment_iou_ours_vs_realigned'] for x in rows], [x['authors_sentence_chrf'] for x in rows])
res['spearman_iou_vs_authors_chrf_control'] = {'rho': round(float(rho2), 3), 'p': float(p2)}
rho3, p3 = spearmanr([x['segment_iou_ours_vs_realigned'] for x in rows], [x['our_previous_sentence_chrf'] for x in rows])
res['spearman_iou_vs_ours_chrf'] = {'rho': round(float(rho3), 3), 'p': float(p3)}
json.dump(res, open(out_json, 'w'), indent=1)
with open(out_csv, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(json.dumps(res, indent=1))
