import sys, json, re, gzip, pickle, csv
U = sys.argv[1]; sys.path.insert(0, U)
from SLRT_metrics import sableu
def load(p, key):
    d = {}
    for line in open(p, encoding='utf-8'):
        m = re.match(r'sample: (.*?), ' + key + r': (.*)$', line.rstrip('\n')); d[m.group(1)[:-4]] = m.group(2)
    return d
opres = load(U+'/out/eval_how2sign_pose_only/test_tmp_pres.txt', 'prediction')
orefs = load(U+'/out/eval_how2sign_pose_only/test_tmp_refs.txt', 'ground-truth')
ours = {}
for l in open('docs/daily_report/9.2/asl-baselines/results/unisign_predictions.jsonl'):
    r = json.loads(l); ours[r['clip_id']] = r
ids = list(ours)
inset = [i for i in ids if i in opres]
missing = [i for i in ids if i not in opres]
def b(h, r): return round(sableu(references=r, hypotheses=h, tokenizer='13a')['bleu4'], 2)
ref_mismatch = [i for i in inset if orefs[i].strip() != ours[i]['reference'].strip()]
out = {
 "n_ours": len(ids), "n_in_official_test_labels": len(inset), "missing_from_official": missing,
 "n_reference_text_mismatch": len(ref_mismatch),
 "ref_mismatch_examples": [{"id": i, "official": orefs[i], "ours": ours[i]['reference']} for i in ref_mismatch[:5]],
 "A_official_preds_full_test_official_refs": b([opres[k] for k in orefs], list(orefs.values())),
 "B_official_preds_on_our_subset_official_refs": b([opres[i] for i in inset], [orefs[i] for i in inset]),
 "C_our_preds_on_same_subset_official_refs": b([ours[i]['prediction'] for i in inset], [orefs[i] for i in inset]),
 "D_our_preds_on_same_subset_our_refs": b([ours[i]['prediction'] for i in inset], [ours[i]['reference'] for i in inset]),
 "E_our_preds_all128_our_refs": b([ours[i]['prediction'] for i in ids], [ours[i]['reference'] for i in ids]),
 "F_official_preds_on_subset_our_refs": b([opres[i] for i in inset], [ours[i]['reference'] for i in inset]),
}
# official preds that look truncated (no terminal punct) on subset vs ours
tp = lambda s: s.rstrip()[-1:] in '.?!"'
out["subset_frac_no_terminal_punct_official"] = round(sum(not tp(opres[i]) for i in inset)/len(inset),3)
out["subset_frac_no_terminal_punct_ours"] = round(sum(not tp(ours[i]['prediction']) for i in inset)/len(inset),3)
out["subset_exact_same_prediction_count"] = sum(opres[i].strip()==ours[i]['prediction'].strip() for i in inset)
json.dump({"per_clip": [{"id": i, "official_pred": opres[i], "our_pred": ours[i]['prediction'], "official_ref": orefs[i]} for i in inset]}, open(sys.argv[2],'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
