#!/usr/bin/env python3
"""Phase: deterministic, criteria-based selection of the 30-query Calibration Set.
Selection is driven by objective input features only (category, language, zero/low
result, rewrite flag, token length as an "ambiguous simple word" proxy, result_count
as a rough performance-tier proxy). No outcome is pre-judged; the proxy tiers are
only used to make sure the calibration set spans easy/hard cases, not to predict labels.
"""
import json, os
from collections import defaultdict

OUT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.15/easy-query-production-baseline-v1/automated_relevance_evaluation-v1"

with open(os.path.join(OUT, "evidence", "query_packets.json"), encoding="utf-8") as f:
    packets = json.load(f)

def tier(p):
    # Weak, objective, pre-judgment-free proxy for "likely performance tier" using
    # only structural signals (never used as the actual relevance verdict).
    if p['zero_result']:
        return 'low'
    if p['low_result']:
        return 'mid'
    if p['result_count_observed'] >= 15 and not p['query_broadened']:
        return 'high'
    if p['query_broadened']:
        return 'mid'
    return 'high'

for p in packets:
    p['_tier'] = tier(p)
    p['_is_short_token'] = len(p['original_query'].strip().split()) == 1 and len(p['original_query'].strip()) <= 6

selected = []
selected_idx = set()

def add(p, reason):
    if p['query_index'] in selected_idx:
        return False
    selected.append((p, reason))
    selected_idx.add(p['query_index'])
    return True

# 1. Guarantee category coverage: 1 per category (10 categories) picking a query_broadened=true example where possible for variety
by_cat = defaultdict(list)
for p in packets:
    by_cat[p['category']].append(p)
categories = sorted(by_cat.keys())
for i, cat in enumerate(categories):
    cands = by_cat[cat]
    # alternate rewrite/no-rewrite across categories for variety
    want_rewrite = (i % 2 == 0)
    pick = next((p for p in cands if p['query_broadened'] == want_rewrite and not p['zero_result']), cands[0])
    add(pick, f"category coverage: {cat} (rewrite={pick['query_broadened']})")

# 2. Zero-result coverage: 3
zero_qs = [p for p in packets if p['zero_result']]
for p in zero_qs[:3]:
    add(p, "zero-result coverage")

# 3. Low-result coverage: 4
low_qs = [p for p in packets if p['low_result'] and not p['zero_result']]
for p in low_qs[:4]:
    add(p, "low-result coverage")

# 4. Rewrite/broaden coverage: 5 more rewrite=true (beyond category picks)
rewrite_qs = [p for p in packets if p['query_broadened'] and not p['zero_result'] and not p['low_result']]
c = 0
for p in rewrite_qs:
    if c >= 5:
        break
    if add(p, "rewrite/broaden coverage"):
        c += 1

# 5. No-rewrite coverage: 5 more
norewrite_qs = [p for p in packets if not p['query_broadened'] and not p['zero_result'] and not p['low_result']]
c = 0
for p in norewrite_qs:
    if c >= 5:
        break
    if add(p, "no-rewrite coverage"):
        c += 1

# 6. Ambiguous / simple single-token word coverage: 4
short_qs = [p for p in packets if p['_is_short_token']]
c = 0
for p in short_qs:
    if c >= 4:
        break
    if add(p, "ambiguous/simple single-token word coverage"):
        c += 1

# 7. Language coverage check + top-up: ensure at least 5 'en'
en_selected = [p for p, r in selected if p['detected_language'] == 'en']
if len(en_selected) < 6:
    need = 6 - len(en_selected)
    en_qs = [p for p in packets if p['detected_language'] == 'en']
    c = 0
    for p in en_qs:
        if c >= need:
            break
        if add(p, "language coverage top-up (en)"):
            c += 1

# 8. Fill remainder to 30 balancing tiers (aim ~10 high / ~10 mid / ~10 low overall)
target = 30
tier_counts = defaultdict(int)
for p, r in selected:
    tier_counts[p['_tier']] += 1

remaining_pool = [p for p in packets if p['query_index'] not in selected_idx]
remaining_pool.sort(key=lambda p: p['query_index'])
while len(selected) < target and remaining_pool:
    # pick whichever tier is most under target of 10
    tier_deficit = {t: 10 - tier_counts.get(t, 0) for t in ('high', 'mid', 'low')}
    want_tier = max(tier_deficit, key=tier_deficit.get)
    cand = next((p for p in remaining_pool if p['_tier'] == want_tier), remaining_pool[0])
    remaining_pool.remove(cand)
    if add(cand, f"tier balance fill ({want_tier})"):
        tier_counts[cand['_tier']] += 1

selected = selected[:30]

calib = []
for p, reason in selected:
    calib.append({
        "query_index": p['query_index'],
        "query_id": p['query_id'],
        "original_query": p['original_query'],
        "category": p['category'],
        "detected_language": p['detected_language'],
        "zero_result": p['zero_result'],
        "low_result": p['low_result'],
        "query_broadened": p['query_broadened'],
        "proxy_tier": p['_tier'],
        "selection_reason": reason,
    })

os.makedirs(os.path.join(OUT, "checkpoints"), exist_ok=True)
with open(os.path.join(OUT, "checkpoints", "calibration_set_selection.json"), "w", encoding="utf-8") as f:
    json.dump(calib, f, ensure_ascii=False, indent=2)

print(f"Selected {len(calib)} calibration queries")
lang_counts = defaultdict(int); cat_counts = defaultdict(int); tier_counts2 = defaultdict(int)
zero_c = low_c = rw_c = norw_c = 0
for c in calib:
    lang_counts[c['detected_language']] += 1
    cat_counts[c['category']] += 1
    tier_counts2[c['proxy_tier']] += 1
    zero_c += c['zero_result']; low_c += c['low_result']
    rw_c += c['query_broadened']; norw_c += (not c['query_broadened'])
print("lang", dict(lang_counts))
print("category", dict(cat_counts))
print("tier", dict(tier_counts2))
print("zero", zero_c, "low", low_c, "rewrite", rw_c, "no-rewrite", norw_c)
for c in calib:
    print(c['query_index'], c['query_id'], repr(c['original_query']), c['category'], c['detected_language'], c['proxy_tier'], '|', c['selection_reason'])
