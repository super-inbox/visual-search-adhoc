# Step 0: verify the restored P0-12 T4/fp16 prediction files before any analysis.
#   1. exactly 128 parseable prediction lines per file
#   2. clip order == labels.test_p012_128 order == manifest.csv order (positional, line by line)
#   3. no blank / unparseable / duplicated / unknown-ID rows, no empty predictions
#   4. recomputed corpus BLEU-1..4 / ROUGE reproduce p0_12_full128_fp16_results.csv
# Also: labels.test references == manifest reference_text (exact string), so references are unambiguous.
# Writes ../verification.json; exits non-zero if any hard check fails.
import os, sys, json, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

labels = C.load_labels()
lab_ids = [i for i, _ in labels]
lab_refs = dict(labels)
man = C.load_manifest()
man_ids = [r['how2sign_id'] for r in man]
refs = C.load_refs()  # canonical (manifest, encoding-fixed)
committed = {r['condition']: r for r in csv.DictReader(open(C.P012_CSV))}

report = {'labels_n': len(lab_ids), 'manifest_n': len(man_ids),
          'labels_order_equals_manifest_order': lab_ids == man_ids,
          'labels_refs_equal_manifest_refs': sum(lab_refs[i] == refs[i] for i in lab_ids),
          'labels_refs_differing_only_by_mojibake': [i for i in lab_ids if lab_refs[i] != refs[i] and C.fix_mojibake(lab_refs[i]) == refs[i]],
          'systems': {}}
hard_fail = []
if lab_ids != man_ids: hard_fail.append('labels order != manifest order')
if set(lab_ids) != set(refs): hard_fail.append('labels ids != manifest ids')
unexplained = [i for i in lab_ids if lab_refs[i] != refs[i] and C.fix_mojibake(lab_refs[i]) != refs[i]]
if unexplained: hard_fail.append(f'labels/manifest reference mismatch not explained by mojibake: {unexplained}')

TOL = {'bleu1': 0.05, 'bleu2': 0.05, 'bleu3': 0.05, 'bleu4': 0.05, 'rouge': 0.05}
for s in C.SYSTEMS:
    lines = C.load_pred_lines(s)
    parsed = [(ln, cid, p) for ln, cid, p, _ in lines if cid is not None]
    ids = [cid for _, cid, _ in parsed]
    r = {
        'file_lines': len(lines),
        'parsed_rows': len(parsed),
        'unparseable_or_blank_lines': [ln for ln, cid, _, raw in lines if cid is None],
        'empty_predictions': [cid for _, cid, p in parsed if not p.strip()],
        'duplicate_ids': sorted({i for i in ids if ids.count(i) > 1}),
        'unknown_ids': [i for i in ids if i not in refs],
        'missing_ids': [i for i in lab_ids if i not in set(ids)],
        'order_equals_labels': ids == lab_ids,
        'first_order_mismatch': next((k for k, (a, b) in enumerate(zip(ids, lab_ids)) if a != b), None),
        'unique_predictions': len(set(p for _, _, p in parsed)),
    }
    ok = (r['parsed_rows'] == 128 and r['file_lines'] == 128 and not r['unparseable_or_blank_lines'] and not r['empty_predictions']
          and not r['duplicate_ids'] and not r['unknown_ids'] and not r['missing_ids'] and r['order_equals_labels'])
    if not ok: hard_fail.append(f'{s}: structural check failed')
    P = dict((cid, p) for _, cid, p in parsed)
    hyps = [P[i] for i in lab_ids]; R = [refs[i] for i in lab_ids]
    m = C.corpus_bleu_n(hyps, R)
    m['rouge'] = C.corpus_rouge(hyps, R)
    m['bleu4_with_labels_test_refs'] = C.corpus_bleu_n(hyps, [lab_refs[i] for i in lab_ids])['bleu4']
    m['rouge_with_labels_test_refs'] = C.corpus_rouge(hyps, [lab_refs[i] for i in lab_ids])
    m['chrf'] = C.corpus_chrf(hyps, R)
    e = [C.wer_p012(h, rr) for h, rr in zip(hyps, R)]
    m['wer_p012'] = sum(a for a, _ in e) / sum(b for _, b in e)
    cm = committed[s]
    diffs = {k: round(m[k] - float(cm[k]), 4) for k in TOL}
    r['recomputed'] = {k: round(v, 4) for k, v in m.items()}
    r['committed'] = {k: float(cm[k]) for k in list(TOL) + ['bleurt']}
    r['diff_recomputed_minus_committed'] = diffs
    r['metrics_reproduced'] = all(abs(diffs[k]) <= TOL[k] for k in TOL)
    if not r['metrics_reproduced']: hard_fail.append(f'{s}: metrics differ beyond tolerance {diffs}')
    r['structural_ok'] = ok
    report['systems'][s] = r

# cross-file: same ID at every line position in all four files (i.e. rows are not shifted relative to each other)
per_sys_ids = {s: [cid for _, cid, _, _ in C.load_pred_lines(s)] for s in C.SYSTEMS}
report['all_files_same_line_order'] = all(per_sys_ids[s] == per_sys_ids[C.PRIMARY] for s in C.SYSTEMS)
report['bleurt_note'] = 'BLEURT not recomputed (BLEURT-20 checkpoint not available locally); committed values carried over unchanged.'
report['metric_tolerance_abs'] = TOL
report['hard_failures'] = hard_fail
report['PASS'] = not hard_fail
json.dump(report, open(os.path.join(C.OUT, 'verification.json'), 'w'), indent=1)

print(f"labels n={len(lab_ids)} manifest n={len(man_ids)} order equal={lab_ids == man_ids} "
      f"refs equal={report['labels_refs_equal_manifest_refs']}/128 (+{len(report['labels_refs_differing_only_by_mojibake'])} mojibake-only) all files same line order={report['all_files_same_line_order']}")
print(f"{'system':26s} lines parsed blank empty dup miss order | " + ' '.join(f'{k:>16s}' for k in TOL) + ' | chrF  WER')
for s, r in report['systems'].items():
    print(f"{s:26s} {r['file_lines']:5d} {r['parsed_rows']:6d} {len(r['unparseable_or_blank_lines']):5d} {len(r['empty_predictions']):5d} "
          f"{len(r['duplicate_ids']):3d} {len(r['missing_ids']):4d} {str(r['order_equals_labels']):5s} | "
          + ' '.join(f"{r['recomputed'][k]:7.2f}({r['diff_recomputed_minus_committed'][k]:+.3f})" for k in TOL)
          + f" | {r['recomputed']['chrf']:.2f} {r['recomputed']['wer_p012']:.4f}"
          + f" | labels-refs B4 {r['recomputed']['bleu4_with_labels_test_refs']:.4f} R {r['recomputed']['rouge_with_labels_test_refs']:.2f}")
print('PASS' if not hard_fail else 'FAIL: ' + '; '.join(hard_fail))
sys.exit(0 if not hard_fail else 1)
