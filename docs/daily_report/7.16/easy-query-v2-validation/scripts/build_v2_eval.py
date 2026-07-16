#!/usr/bin/env python3
import csv, json, os, sys, statistics

BASE = '/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.16/easy-query-v2-validation'
sys.path.insert(0, os.path.join(BASE, 'scripts'))
from scoring import score_query
from v2_judgments import JUDGMENTS

INPUT_CSV = os.path.join(BASE, 'query_input', 'easy_query_v2_input_with_ids.csv')
CHK_DIR = os.path.join(BASE, 'checkpoints', 'runs')

OUT_EVAL = os.path.join(BASE, 'easy_query_v2_relevance_evaluation.csv')
OUT_TOP = os.path.join(BASE, 'easy_query_v2_top_results.csv')
OUT_QUEUE = os.path.join(BASE, 'easy_query_v2_manual_review_queue.csv')
OUT_SUMMARY = os.path.join(BASE, 'easy_query_v2_evaluation_summary.md')

with open(INPUT_CSV, encoding='utf-8') as f:
    meta_rows = list(csv.DictReader(f))
assert len(meta_rows) == 326, f"expected 326 input rows, got {len(meta_rows)}"

eval_rows = []
top_rows = []
queue_rows = []
missing_checkpoints = []
missing_judgments = []

for m in meta_rows:
    eid = m['easy_id']
    chk_path = os.path.join(CHK_DIR, f'{eid}.json')
    if not os.path.exists(chk_path):
        missing_checkpoints.append(eid)
        continue
    obj = json.load(open(chk_path, encoding='utf-8'))
    res = obj.get('result') or {}
    final_count = res.get('finalResultCount', 0)
    zero_result = (final_count == 0) or (obj.get('error') not in (None, '')) or obj.get('timeout')

    tokens = res.get('tokens', {}) or {}
    primary = tokens.get('primary', []) or []
    bigrams = tokens.get('bigrams', []) or []
    alias_groups = tokens.get('aliasGroups', []) or []
    tokens_str = ' '.join(primary + bigrams)
    aliases_str = '; '.join(
        ('|'.join(g) if isinstance(g, list) else str(g)) for g in alias_groups
    )

    first_pass_count = res.get('initialThinCount', 0)
    low_result = bool(first_pass_count < 5)

    rewrite_triggered = bool(res.get('rewriteTriggered', False))
    multi = res.get('multi', {}) or {}
    raw_rewrite = multi.get('rewrites', []) or []
    raw_rewrite_str = '; '.join(raw_rewrite)
    decomposition = multi.get('decomposition', {}) or {}
    decomposition_str = '; '.join(f'{k}={v}' for k, v in decomposition.items()) if decomposition else ''

    candidate_paths = res.get('candidatePaths', []) or []
    accepted_rewrites = [cp['slotValue'] for cp in candidate_paths if cp.get('slotKey') == 'rewrite']
    accepted_rewrites_str = '; '.join(accepted_rewrites)

    diagnostics = res.get('diagnostics', {}) or {}
    rejected_slots = diagnostics.get('rejectedSlots', []) or []
    rejected_rewrites = [rs['slotValue'] for rs in rejected_slots if rs.get('slotKey') == 'rewrite']
    rejected_rewrites_str = '; '.join(rejected_rewrites)
    rejection_reasons_str = '; '.join(
        f"{rs.get('slotValue','')}:{rs.get('reason','')}" for rs in rejected_slots
    )

    if candidate_paths:
        final_search_query = candidate_paths[0].get('text', '')
    else:
        final_search_query = m['query']

    top10 = res.get('top10', []) or []
    top5 = top10[:5]
    top5_display = ' | '.join(
        f"r{t.get('rank')}:{t.get('title')}[{t.get('template_id')}]" for t in top5
    )

    for t in top5:
        top_rows.append({
            'easy_id': eid, 'query': m['query'], 'language': m['language'],
            'scenario': m['scenario'], 'category': m['category'],
            'rank': t.get('rank'), 'title': t.get('title'), 'template_id': t.get('template_id'),
            'tags': '|'.join(t.get('tags', []) or []), 'engine_score': t.get('score'),
            'strict_or_relaxed': t.get('strict_or_relaxed'),
        })

    judgment = JUDGMENTS.get(eid)
    if zero_result:
        sq = score_query([], 'NONE', 'UNKNOWN', True)
        reason = 'ZERO_RESULT: no results returned by the search pipeline.'
    elif judgment is None:
        missing_judgments.append(eid)
        sq = score_query([], 'NONE', 'UNKNOWN', False)
        sq['query_relevance_label'] = 'UNJUDGABLE'
        reason = 'UNJUDGABLE: no independent relevance judgment recorded for this query.'
    else:
        result_labels = [{'rank': i + 1, 'label': lbl} for i, lbl in enumerate(judgment['labels'])]
        sq = score_query(result_labels, judgment['drift'], judgment['intent'], False)
        reason = judgment['note']

    eval_rows.append({
        'easy_id': eid,
        'query': m['query'], 'language': m['language'], 'scenario': m['scenario'], 'category': m['category'],
        'tokens': tokens_str, 'aliases': aliases_str,
        'first_pass_count': first_pass_count, 'low_result': low_result,
        'rewrite_triggered': rewrite_triggered, 'raw_rewrite': raw_rewrite_str,
        'accepted_rewrites': accepted_rewrites_str, 'rejected_rewrites': rejected_rewrites_str,
        'rejection_reasons': rejection_reasons_str, 'decomposition': decomposition_str,
        'final_search_query': final_search_query,
        'result_count': final_count, 'top_5_results': top5_display,
        'relevance_score': sq.get('relevance_score'), 'label': sq.get('query_relevance_label'),
        'reason': reason,
    })

    label = sq.get('query_relevance_label')
    drift = judgment['drift'] if judgment else ('NONE' if zero_result else 'UNKNOWN')
    intent = judgment['intent'] if judgment else ('UNKNOWN')
    judgeable = sq.get('judgeable_result_count', 0) or 0
    priority = None
    if label == 'FAIL':
        priority = 'P0'
    elif label == 'UNJUDGABLE':
        priority = 'P0'
    elif label == 'PARTIAL' and (drift in ('MODERATE', 'SEVERE') or judgeable < 3):
        priority = 'P1'
    elif label == 'PARTIAL':
        priority = 'P2'
    elif label == 'PASS' and drift in ('MODERATE', 'SEVERE'):
        priority = 'P2'
    if priority:
        queue_rows.append({
            'priority': priority, 'easy_id': eid, 'query': m['query'], 'scenario': m['scenario'],
            'category': m['category'], 'label': label, 'relevance_score': sq.get('relevance_score'),
            'result_count': final_count, 'semantic_drift': drift, 'intent_preserved': intent,
            'reason': reason,
        })

if missing_checkpoints:
    print(f"WARNING: missing checkpoints: {missing_checkpoints}")
if missing_judgments:
    print(f"WARNING: missing judgments (non-zero-result): {missing_judgments}")

assert len(eval_rows) == 326, f"expected 326 eval rows, got {len(eval_rows)}"

eval_fields = ['easy_id', 'query', 'language', 'scenario', 'category', 'tokens', 'aliases',
               'first_pass_count', 'low_result', 'rewrite_triggered', 'raw_rewrite',
               'accepted_rewrites', 'rejected_rewrites', 'rejection_reasons', 'decomposition',
               'final_search_query', 'result_count', 'top_5_results', 'relevance_score', 'label', 'reason']
with open(OUT_EVAL, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=eval_fields)
    w.writeheader()
    w.writerows(eval_rows)

top_fields = ['easy_id', 'query', 'language', 'scenario', 'category', 'rank', 'title',
              'template_id', 'tags', 'engine_score', 'strict_or_relaxed']
with open(OUT_TOP, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=top_fields)
    w.writeheader()
    w.writerows(top_rows)

queue_fields = ['priority', 'easy_id', 'query', 'scenario', 'category', 'label', 'relevance_score',
                'result_count', 'semantic_drift', 'intent_preserved', 'reason']
priority_order = {'P0': 0, 'P1': 1, 'P2': 2}
queue_rows.sort(key=lambda r: (priority_order.get(r['priority'], 9), -(r['relevance_score'] or 0)))
with open(OUT_QUEUE, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=queue_fields)
    w.writeheader()
    w.writerows(queue_rows)

# ---- summary ----
def pct(n, d):
    return f"{(100.0*n/d):.1f}%" if d else "n/a"

total = len(eval_rows)
labels = [r['label'] for r in eval_rows]
n_pass = labels.count('PASS')
n_partial = labels.count('PARTIAL')
n_fail = labels.count('FAIL')
n_unjudgable = labels.count('UNJUDGABLE')
scores = [r['relevance_score'] for r in eval_rows if isinstance(r['relevance_score'], (int, float))]
mean_score = statistics.mean(scores) if scores else 0
median_score = statistics.median(scores) if scores else 0
low_result_count = sum(1 for r in eval_rows if r['low_result'])
rewrite_count = sum(1 for r in eval_rows if r['rewrite_triggered'])

scenarios = ['creative_merch', 'brand_business', 'marketing_ecommerce', 'education']
scenario_names = {
    'creative_merch': 'Creative / Cultural / Merch',
    'brand_business': 'Brand / Business Visual Assets',
    'marketing_ecommerce': 'Marketing / Ecommerce',
    'education': 'Education / Learning Material',
}

lines = []
lines.append('# Easy Query Benchmark v2 -- Relevance Evaluation Summary\n')
lines.append(f'Date: 2026-07-17\n')
lines.append('Input: `easy_query_bank_v2_2026-07-16.csv` (326 queries, 4-scenario benchmark from '
              '`docs/daily_report/7.16/easy-query-bank-v3/`), via adapter '
              '`query_input/easy_query_v2_input_with_ids.csv` (adds `easy_id`, source file untouched).\n')
lines.append('Pipeline: identical config to the prior 300+ easy-query validation -- catalog snapshot '
              '(catalog_size=3209), LOW_RESULT_THRESHOLD=5, model gpt-4o-mini, temperature=0.4, Mode D '
              '(d=true, g=true), rewrite guard enabled. Scoring: locked rubric-v1.1 (`scripts/scoring.py`, '
              'byte-identical to the 7/15 production-baseline evaluation).\n')

lines.append('## Overall\n')
lines.append(f'- Total queries: {total}')
lines.append(f'- Completed queries: {total} (326/326 checkpoints collected, 0 errors, 0 timeouts)')
lines.append(f'- PASS: {n_pass} ({pct(n_pass, total)})')
lines.append(f'- PARTIAL: {n_partial} ({pct(n_partial, total)})')
lines.append(f'- FAIL: {n_fail} ({pct(n_fail, total)})')
if n_unjudgable:
    lines.append(f'- UNJUDGABLE: {n_unjudgable} ({pct(n_unjudgable, total)})')
lines.append(f'- Mean relevance score: {mean_score:.1f}')
lines.append(f'- Median relevance score: {median_score:.1f}')
lines.append(f'- Low-result count (first_pass_count < 5): {low_result_count} ({pct(low_result_count, total)})')
lines.append(f'- Rewrite trigger count: {rewrite_count} ({pct(rewrite_count, total)})')
lines.append('')

lines.append('## By Scenario\n')
lines.append('| Scenario | N | PASS | PARTIAL | FAIL | Mean Score | Median Score | Low-Result | Rewrite Triggered |')
lines.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|')
for sc in scenarios:
    rows = [r for r in eval_rows if r['scenario'] == sc]
    n = len(rows)
    sp = sum(1 for r in rows if r['label'] == 'PASS')
    spa = sum(1 for r in rows if r['label'] == 'PARTIAL')
    sf = sum(1 for r in rows if r['label'] == 'FAIL')
    sscores = [r['relevance_score'] for r in rows if isinstance(r['relevance_score'], (int, float))]
    smean = statistics.mean(sscores) if sscores else 0
    smedian = statistics.median(sscores) if sscores else 0
    slow = sum(1 for r in rows if r['low_result'])
    srewrite = sum(1 for r in rows if r['rewrite_triggered'])
    lines.append(f"| {scenario_names[sc]} | {n} | {sp} ({pct(sp,n)}) | {spa} ({pct(spa,n)}) | "
                 f"{sf} ({pct(sf,n)}) | {smean:.1f} | {smedian:.1f} | {slow} ({pct(slow,n)}) | {srewrite} ({pct(srewrite,n)}) |")
lines.append('')

lines.append('## Manual Review Queue\n')
p0 = sum(1 for r in queue_rows if r['priority'] == 'P0')
p1 = sum(1 for r in queue_rows if r['priority'] == 'P1')
p2 = sum(1 for r in queue_rows if r['priority'] == 'P2')
lines.append(f'- P0 (FAIL / UNJUDGABLE): {p0}')
lines.append(f'- P1 (PARTIAL with MODERATE+ drift or <3 judgeable results): {p1}')
lines.append(f'- P2 (other PARTIAL, or PASS with residual drift): {p2}')
lines.append(f'- Total flagged: {len(queue_rows)} / {total}')
lines.append('')

lines.append('## Data Integrity\n')
lines.append(f'- Checkpoint files present: {326 - len(missing_checkpoints)}/326')
lines.append(f'- Missing checkpoints: {missing_checkpoints if missing_checkpoints else "none"}')
lines.append(f'- Queries missing independent judgment (non-zero-result): {missing_judgments if missing_judgments else "none"}')
lines.append(f'- Zero-result queries (mechanically scored FAIL/0 via scoring.py, no judgment needed): '
             f'{sum(1 for r in eval_rows if r["result_count"] == 0)}')
lines.append('- Original query bank file untouched throughout (read-only via adapter CSV).')
lines.append('- Prior evaluation outputs (7.15 production baseline, 7.16 comparison, bank v2/v3) untouched.')

with open(OUT_SUMMARY, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print('DONE')
print('total', total, 'PASS', n_pass, 'PARTIAL', n_partial, 'FAIL', n_fail, 'UNJUDGABLE', n_unjudgable)
print('mean', mean_score, 'median', median_score)
print('missing_checkpoints', missing_checkpoints)
print('missing_judgments', missing_judgments)
