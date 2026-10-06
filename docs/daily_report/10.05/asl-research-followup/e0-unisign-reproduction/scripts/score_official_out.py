import sys, json, re
sys.path.insert(0, '.')
from SLRT_metrics import sableu
def load(p, key):
    d = {}
    for line in open(p, encoding='utf-8'):
        line = line.rstrip('\n')
        m = re.match(r'sample: (.*?), ' + key + r': (.*)$', line)
        assert m, line[:120]
        d[m.group(1)] = m.group(2)
    return d
pres = load('out/eval_how2sign_pose_only/test_tmp_pres.txt', 'prediction')
refs = load('out/eval_how2sign_pose_only/test_tmp_refs.txt', 'ground-truth')
names = list(refs)
assert set(names) == set(pres)
hyp = [pres[n] for n in names]; ref = [refs[n] for n in names]
s = sableu(references=ref, hypotheses=hyp, tokenizer='13a')
import sacrebleu as sb
modern = sb.corpus_bleu(hyp, [ref], tokenize='13a')
print(json.dumps({"n": len(names), "official_vendored_sacrebleu_1.4.2": s, "pip_sacrebleu_version": sb.__version__, "pip_sacrebleu_bleu": modern.score, "signature": str(modern.format(signature=True)) if hasattr(modern,'format') else None}, indent=1))
