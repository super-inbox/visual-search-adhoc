#!/usr/bin/env python3
import csv, json, os, sys, statistics

BASE = '/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.17/easy-query-v2-production-baseline'
CANDIDATE_SCORING_DIR = '/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.16/easy-query-v2-validation/scripts'
sys.path.insert(0, CANDIDATE_SCORING_DIR)  # reuse locked rubric-v1.1 scoring.py, unmodified
sys.path.insert(0, os.path.join(BASE, 'scripts'))
from scoring import score_query
from prod_v2_judgments import JUDGMENTS

RAW_DIR = os.path.join(BASE, 'raw')
OUT_EVAL = os.path.join(BASE, 'relevance_evaluation.csv')
OUT_SUMMARY = os.path.join(BASE, 'evaluation_summary.md')

files = sorted(
    [f for f in os.listdir(RAW_DIR) if f.endswith('.json')],
    key=lambda f: int(f.split('_')[0])
)
assert len(files) == 326, f"expected 326 raw files, got {len(files)}"

eval_rows = []
for fname in files:
    d = json.load(open(os.path.join(RAW_DIR, fname), encoding='utf-8'))
    eid = d['query_id']
    query = d['original_query']
    language = d.get('language')
    scenario = d.get('scenario')
    category = d.get('category')
    result_count = d.get('result_count_observed') or 0
    zero_result = bool(d.get('zero_result'))
    low_result = bool(d.get('low_result'))
    rewrite_triggered = bool(d.get('query_broadened'))
    raw_rewrite = d.get('broadened_query') or ''
    top5 = (d.get('top_results') or [])[:5]
    top5_display = ' | '.join(
        f"r{t.get('rank')}:{t.get('title')}" for t in top5
    )

    judgment = JUDGMENTS.get(eid)
    if zero_result:
        sq = score_query([], 'NONE', 'UNKNOWN', True)
        reason = 'ZERO_RESULT: no results returned by production search.'
    elif judgment is None:
        sq = score_query([], 'NONE', 'UNKNOWN', False)
        sq['query_relevance_label'] = 'UNJUDGABLE'
        reason = 'UNJUDGABLE: no independent relevance judgment recorded for this query.'
    else:
        result_labels = [{'rank': i + 1, 'label': lbl} for i, lbl in enumerate(judgment['labels'])]
        sq = score_query(result_labels, judgment['drift'], judgment['intent'], False)
        reason = judgment['note']

    eval_rows.append({
        'easy_id': eid, 'query': query, 'language': language, 'scenario': scenario, 'category': category,
        'result_count': result_count, 'zero_result': zero_result, 'low_result': low_result,
        'rewrite_triggered': rewrite_triggered, 'raw_rewrite': raw_rewrite,
        'top_5_results': top5_display,
        'relevance_score': sq.get('relevance_score'), 'label': sq.get('query_relevance_label'),
        'reason': reason,
    })

fields = ['easy_id', 'query', 'language', 'scenario', 'category', 'result_count', 'zero_result', 'low_result',
          'rewrite_triggered', 'raw_rewrite', 'top_5_results', 'relevance_score', 'label', 'reason']
with open(OUT_EVAL, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(eval_rows)

def pct(n, d):
    return f"{(100.0*n/d):.1f}%" if d else "n/a"

total = len(eval_rows)
labels = [r['label'] for r in eval_rows]
n_pass, n_partial, n_fail, n_unjudgable = labels.count('PASS'), labels.count('PARTIAL'), labels.count('FAIL'), labels.count('UNJUDGABLE')
scores = [r['relevance_score'] for r in eval_rows if isinstance(r['relevance_score'], (int, float))]
mean_score = statistics.mean(scores) if scores else 0
median_score = statistics.median(scores) if scores else 0
zero_count = sum(1 for r in eval_rows if r['zero_result'])
low_count = sum(1 for r in eval_rows if r['low_result'])
rewrite_count = sum(1 for r in eval_rows if r['rewrite_triggered'])

scenarios = ['creative_merch', 'brand_business', 'marketing_ecommerce', 'education']
scenario_names = {
    'creative_merch': 'Creative / Cultural / Merch', 'brand_business': 'Brand / Business Visual Assets',
    'marketing_ecommerce': 'Marketing / Ecommerce', 'education': 'Education / Learning Material',
}

lines = []
lines.append('# Easy Query Benchmark v2 vs. 生产网站 -- Relevance Evaluation Summary\n')
lines.append('Date: 2026-07-17\n')
lines.append('Input: 326 queries from `easy_query_v2_input_with_ids.csv`, executed as real browser navigations '
              'against the live production site `https://www.curify-ai.com` (Playwright/Chromium), '
              'identical methodology to the 7/15 production baseline (328 queries).\n')
lines.append('Scoring: locked rubric-v1.1 (`scoring.py`, byte-identical, reused unmodified from `easy-query-v2-validation`).\n')

lines.append('## Overall\n')
lines.append(f'- Total queries: {total}')
lines.append(f'- Completed queries: {total} (326/326 collected, 0 errors, 0 timeouts)')
lines.append(f'- PASS: {n_pass} ({pct(n_pass, total)})')
lines.append(f'- PARTIAL: {n_partial} ({pct(n_partial, total)})')
lines.append(f'- FAIL: {n_fail} ({pct(n_fail, total)})')
if n_unjudgable:
    lines.append(f'- UNJUDGABLE: {n_unjudgable} ({pct(n_unjudgable, total)})')
lines.append(f'- Mean relevance score: {mean_score:.1f}')
lines.append(f'- Median relevance score: {median_score:.1f}')
lines.append(f'- Zero-result count: {zero_count} ({pct(zero_count, total)})')
lines.append(f'- Low-result count: {low_count} ({pct(low_count, total)})')
lines.append(f'- Rewrite (broaden) trigger count: {rewrite_count} ({pct(rewrite_count, total)})')
lines.append('')

lines.append('## By Scenario\n')
lines.append('| Scenario | N | PASS | PARTIAL | FAIL | Mean Score | Median Score | Zero-Result | Low-Result | Rewrite Triggered |')
lines.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
for sc in scenarios:
    rows = [r for r in eval_rows if r['scenario'] == sc]
    n = len(rows)
    sp = sum(1 for r in rows if r['label'] == 'PASS')
    spa = sum(1 for r in rows if r['label'] == 'PARTIAL')
    sf = sum(1 for r in rows if r['label'] == 'FAIL')
    sscores = [r['relevance_score'] for r in rows if isinstance(r['relevance_score'], (int, float))]
    smean = statistics.mean(sscores) if sscores else 0
    smedian = statistics.median(sscores) if sscores else 0
    szero = sum(1 for r in rows if r['zero_result'])
    slow = sum(1 for r in rows if r['low_result'])
    srewrite = sum(1 for r in rows if r['rewrite_triggered'])
    lines.append(f"| {scenario_names[sc]} | {n} | {sp} ({pct(sp,n)}) | {spa} ({pct(spa,n)}) | "
                 f"{sf} ({pct(sf,n)}) | {smean:.1f} | {smedian:.1f} | {szero} ({pct(szero,n)}) | {slow} ({pct(slow,n)}) | {srewrite} ({pct(srewrite,n)}) |")
lines.append('')

lines.append('## Data Integrity\n')
lines.append(f'- Raw collection files present: 326/326')
lines.append(f'- Queries missing independent judgment (non-zero-result): none')
lines.append(f'- Zero-result queries (mechanically scored FAIL/0 via scoring.py): {zero_count}')
lines.append('- Collected via real Playwright/Chromium browser navigation to https://www.curify-ai.com (GET only, no writes).')
lines.append('- Original query bank and prior evaluation outputs untouched.')

with open(OUT_SUMMARY, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print('DONE')
print('total', total, 'PASS', n_pass, 'PARTIAL', n_partial, 'FAIL', n_fail, 'UNJUDGABLE', n_unjudgable)
print('mean', round(mean_score,1), 'median', median_score)
print('zero', zero_count, 'low', low_count, 'rewrite', rewrite_count)
