# Step 3: validate the generated taxonomy outputs (structure, exactness, labelling discipline). Exits non-zero on failure.
import os, sys, csv, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

fails = []
def check(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)

ids = [i for i, _ in C.load_labels()]
refs = C.load_refs()
preds = {s: C.load_preds(s) for s in C.SYSTEMS}
for f in ['verification.json', 'inputs_128.jsonl', 'error_taxonomy_annotations.jsonl', 'failure_matrix.csv', 'manual_review_queue.csv',
          'representative_failures.md', 'taxonomy_summary.json', 'ERROR_ANALYSIS_REPORT.md']:
    check(os.path.exists(os.path.join(C.OUT, f)), f'exists: {f}')
check(json.load(open(os.path.join(C.OUT, 'verification.json')))['PASS'], 'verification.json PASS')

inp = C.read_jsonl(os.path.join(C.OUT, 'inputs_128.jsonl'))
ann = C.read_jsonl(os.path.join(C.OUT, 'error_taxonomy_annotations.jsonl'))
for name, rows in (('inputs_128', inp), ('annotations', ann)):
    check([r['clip_id'] for r in rows] == ids, f'{name}: 128 rows in labels.test_p012_128 order')
    check(all(r['reference'] == refs[r['clip_id']] for r in rows), f'{name}: references exact')
    check(all(r['predictions'][s] == preds[s][r['clip_id']] for r in rows for s in C.SYSTEMS), f'{name}: predictions exact (4 systems)')
check(all(all(m[k] == m[k] for k in ('wer', 'chrf', 'sentence_bleu')) for r in inp for m in r['metrics'].values()), 'per-sample WER/chrF/sentence BLEU present, no NaN')
wl = [v for a in ann for v in a['weak_labels'].values()]
check(all(v['label_source'] == 'automatic' and v['status'] == 'candidate_unverified' for v in wl), 'every weak label marked automatic / candidate_unverified')
STATUS = 'automated first-pass / weak-label analysis; manual ASL review pending'
check(all(a['annotation_meta']['manual_review'] == 'NOT PERFORMED' and a['annotation_meta']['analysis_status'] == STATUS for a in ann),
      'annotations: manual review NOT PERFORMED + first-pass status label')
for f in ('ERROR_ANALYSIS_REPORT.md', 'representative_failures.md'):
    check(STATUS in open(os.path.join(C.OUT, f), encoding='utf-8').read(), f'{f}: carries the first-pass status label')
check(json.load(open(os.path.join(C.OUT, 'taxonomy_summary.json')))['analysis_status'] == STATUS, 'taxonomy_summary: status label')
rep_txt = open(os.path.join(C.OUT, 'ERROR_ANALYSIS_REPORT.md'), encoding='utf-8').read().lower()
check('verified fingerspelling failure' not in rep_txt.replace('not a verified fingerspelling failure', '').replace('not verified fingerspelling failure', ''),
      'report: never asserts a verified fingerspelling failure')
check(all(k.endswith('_candidate') for k in ann[0]['weak_labels'] if k.startswith(('fingerspelling', 'named_entity'))),
      'fingerspelling / named-entity labels carry the _candidate suffix')

fm = list(csv.DictReader(open(os.path.join(C.OUT, 'failure_matrix.csv'))))
check(all(r['exploratory_n_lt_10'] == str(int(r['n']) < 10) for r in fm), 'failure_matrix: exploratory flag == (n < 10) on every row')
check(all(r['analysis_status'] == STATUS for r in fm), 'failure_matrix: status label on every row')
broad = [r for r in fm if r['category'] == 'number_candidate_broad_sensitivity']
check(len(broad) == 4 and all(r['category_group'] == 'sensitivity_secondary' for r in broad), 'failure_matrix: broad-number rows present and marked secondary')
check(sum(1 for r in fm if r['system'] == C.PRIMARY and r['category_group'] not in ('all', 'sensitivity_secondary')) == 16,
      'failure_matrix: 16 primary categories (Bonferroni family unchanged)')
surv = sorted((r['category'], r['system']) for r in fm if r['category_group'] != 'sensitivity_secondary'
              and (r['matched_ctrl_bonferroni_excludes_0'] == 'True' or r.get('pose_sensitivity_bonferroni_excludes_0') == 'True'))
check(not [x for x in surv if x[1] in (C.PRIMARY, C.PAIRED)],
      'no A_official / C matched-control or pose-interaction contrast survives Bonferroni (report wording depends on this)')
check(surv == [('number_candidate', 'B_aspect')],
      f'Bonferroni survivors among controls are exactly the ones disclosed in the report: {surv}')
check({r['system'] for r in fm} == set(C.SYSTEMS), 'failure_matrix: all four systems present')
allA = next(r for r in fm if r['category'] == 'ALL' and r['system'] == C.PRIMARY)
committed = {r['condition']: r for r in csv.DictReader(open(C.P012_CSV))}
check(all(abs(float(next(r for r in fm if r['category'] == 'ALL' and r['system'] == s)['corpus_bleu4']) - float(committed[s]['bleu4'])) < 0.01
          for s in C.SYSTEMS), 'failure_matrix ALL rows: corpus BLEU-4 == committed P0-12 values')

q = list(csv.DictReader(open(os.path.join(C.OUT, 'manual_review_queue.csv'))))
check(30 <= len(q) <= 50, f'manual_review_queue: {len(q)} clips (30-50)')
check(len({r['clip_id'] for r in q}) == len(q), 'manual_review_queue: no duplicate clips')
check(all(r['review_status'] == 'PENDING' and r['analysis_status'] == STATUS and not any(r[k] for k in (
    'reviewer', 'verified_fingerspelling', 'verified_named_entity', 'verified_number_signing', 'verified_negation_nmm', 'verified_question_nmm',
    'spatial_relations_notes', 'occlusion_observed', 'visual_issue_observed', 'manual_primary_error_type', 'manual_notes')) for r in q),
      'manual_review_queue: all PENDING, reviewer fields empty')
check(all(r['reference'] == refs[r['clip_id']] and r['pred_A_official'] == preds[C.PRIMARY][r['clip_id']]
          and r['pred_C_ours_on_official_crop'] == preds[C.PAIRED][r['clip_id']] for r in q), 'manual_review_queue: exact ref / A / C text')
print('ALL CHECKS PASSED' if not fails else f'{len(fails)} FAILED')
sys.exit(1 if fails else 0)
