# P0-12: score each condition's official-eval output (<out_dir>/test_tmp_pres.txt) on the frozen 128 clips with the
# same official BLEU path validated in E0 (SLRT_metrics.sableu -> vendored sacrebleu 1.4.2, 13a), plus chrF / WER /
# exact match / repetition / truncation / diversity computed identically for every condition.
# Usage: python score_conditions.py <Uni-Sign repo> <manifest.csv> <ours_5p39.jsonl> <out.json> NAME=<pres.txt> [NAME=<pres.txt> ...]
import sys, re, json, csv
import numpy as np
U, manifest, ours_jsonl, out_json = sys.argv[1:5]
sys.path.insert(0, U)
from SLRT_metrics import sableu
import sacrebleu
ids = [r['how2sign_id'] for r in csv.DictReader(open(manifest))]
ours = {json.loads(l)['clip_id']: json.loads(l) for l in open(ours_jsonl)}
refs = {i: ours[i]['reference'] for i in ids}  # E0: BLEU identical with official labels.test refs
def load(p):
    d = {}
    for line in open(p, encoding='utf-8'):
        m = re.match(r'sample: (.*?), prediction: (.*)$', line.rstrip('\n'))
        if m: d[m.group(1).replace('.mp4', '')] = m.group(2)
    return d
systems = {'authors_released': U + '/out/eval_how2sign_pose_only/test_tmp_pres.txt'}
systems.update(dict(a.split('=', 1) for a in sys.argv[5:]))
def wer(h, r):
    h = h.lower().split(); r = r.lower().split(); d = np.arange(len(h) + 1)
    for i in range(1, len(r) + 1):
        prev = d.copy(); d[0] = i
        for j in range(1, len(h) + 1):
            d[j] = min(prev[j] + 1, d[j - 1] + 1, prev[j - 1] + (r[i - 1] != h[j - 1]))
    return d[len(h)], len(r)
def rep3(s):
    w = s.lower().split(); g = [tuple(w[k:k + 3]) for k in range(len(w) - 2)]; return len(g) > 0 and len(set(g)) < len(g)
res = {}
for name, path in systems.items():
    P = load(path)
    missing = [i for i in ids if i not in P]
    if missing:
        res[name] = {'error': f'{len(missing)} of 128 clips missing', 'missing': missing[:10]}; continue
    hyps = [P[i] for i in ids]; R = [refs[i] for i in ids]
    b = sableu(references=R, hypotheses=hyps, tokenizer='13a')
    e = [wer(h, r) for h, r in zip(hyps, R)]
    toks = [t for h in hyps for t in h.lower().split()]
    res[name] = dict(n=len(ids), bleu1=round(b['bleu1'], 2), bleu2=round(b['bleu2'], 2), bleu3=round(b['bleu3'], 2), bleu4=round(b['bleu4'], 2),
                     chrf=round(sacrebleu.corpus_chrf(hyps, [R]).score, 2), wer=round(sum(x for x, _ in e) / sum(n for _, n in e), 4),
                     exact_match=sum(h.strip().lower() == r.strip().lower() for h, r in zip(hyps, R)),
                     repeated_3gram_rate=round(float(np.mean([rep3(h) for h in hyps])), 3),
                     no_terminal_punct_rate=round(float(np.mean([h.rstrip()[-1:] not in '.?!"' for h in hyps])), 3),
                     unique_prediction_rate=round(len(set(hyps)) / len(hyps), 3), distinct_1=round(len(set(toks)) / max(len(toks), 1), 3))
json.dump(res, open(out_json, 'w'), indent=1)
print(json.dumps(res, indent=1))
