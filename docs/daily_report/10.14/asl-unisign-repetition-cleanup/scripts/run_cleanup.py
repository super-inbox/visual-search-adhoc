# Stage 1: post-hoc repetition cleanup of the committed P0-12 A_official predictions (CPU only, deterministic).
# Rule: cleanup_rule.py v1, spec ../CLEANUP_RULE.md (frozen before any metric was computed).
# Two modes, run in this order:
#   --dry-run : guards only, no metrics. G1 = rule changes no reference; G2 = list of changed clips vs the 18 taxonomy
#               repetition_loop clips. Writes metrics/rule_freeze.json (sha256 of the rule + spec) and metrics/changed_clips.csv.
#   (default) : refuses to run unless the rule/spec sha256 equal rule_freeze.json. Writes predictions/A_official_cleaned.txt
#               (same line format as the original) and metrics/ (comparison, per-clip, summary with paired bootstrap).
# Originals are read only and sha256-checked before and after. Metrics reuse the taxonomy common.py definitions
# (corpus BLEU-4 sacrebleu 13a, corpus chrF, WER = P0-12 score_conditions.py) and taxonomy.py repetition definitions.
# Paired clip-level bootstrap: 2000 resamples, seed 0 (as P0-12 contrasts.py and the decode-length analysis).
# BLEURT: not computed (no BLEURT-20 checkpoint on this machine); reported as not available.
# Usage: python3 -I run_cleanup.py --dry-run ; python3 -I run_cleanup.py
import argparse, hashlib, json, os, sys
import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..')
TAX = os.path.join(HERE, '..', '..', '..', '10.13', 'asl-unisign-error-taxonomy')
sys.path.insert(0, os.path.join(TAX, 'scripts'))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import cleanup_rule as R  # noqa: E402
from sacrebleu.metrics import BLEU, CHRF  # noqa: E402

BASELINE = os.path.join(C.P012_PRED, 'A_official.txt')
BASELINE_SHA = 'd865008bc0a16ba0fb3bceb6f78f5a7153febe1d69ba756cc83f918d57300e4a'
RULE_FILES = [os.path.join(HERE, 'cleanup_rule.py'), os.path.join(D, 'CLEANUP_RULE.md')]
MET = os.path.join(D, 'metrics')
N_BOOT, SEED = 2000, 0
_BLEU, _CHRF = BLEU(max_ngram_order=4, tokenize='13a'), CHRF()


def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def has_rep3(s):  # taxonomy.py
    w = s.lower().split(); g = [tuple(w[k:k + 3]) for k in range(len(w) - 2)]
    return len(g) > 0 and len(set(g)) < len(g)


def rep3_ratio(s):  # taxonomy.py
    w = s.lower().split(); g = [tuple(w[k:k + 3]) for k in range(len(w) - 2)]
    return 0.0 if not g else 1 - len(set(g)) / len(g)


def is_loop(h, r):  # taxonomy primary_error_type == repetition_loop (reads the reference: evaluation only)
    return has_rep3(h) and not has_rep3(r) and rep3_ratio(h) >= 0.15


def load():
    assert sha(BASELINE) == BASELINE_SHA, 'committed A_official.txt changed'
    lines = [l.rstrip('\n') for l in open(BASELINE, encoding='utf-8')]
    parsed = [C.LINE_RE.match(l) for l in lines]
    assert len(lines) == 128 and all(parsed)
    ids = [m.group(1).replace('.mp4', '') for m in parsed]
    assert ids == [i for i, _ in C.load_labels()], 'clip order != labels.test_p012_128'
    refs_d = C.load_refs()
    ann = {r['clip_id']: r for r in C.read_jsonl(os.path.join(TAX, 'error_taxonomy_annotations.jsonl'))}
    loop18 = [i for i in ids if ann[i]['system_analysis']['A_official']['primary_error_type'] == 'repetition_loop']
    assert len(loop18) == 18, len(loop18)
    return lines, parsed, ids, [m.group(2) for m in parsed], [refs_d[i] for i in ids], set(loop18)


def dry_run():
    lines, parsed, ids, hyp, refs, loop18 = load()
    g1 = [(i, r) for i, r in zip(ids, refs) if R.cleanup(r)[0] != r]
    rows = []
    for i, h, r in zip(ids, hyp, refs):
        new, col = R.cleanup(h)
        if new != h:
            rows.append({'clip_id': i, 'in_taxonomy_loop18': i in loop18, 'ref_has_rep3': has_rep3(r),
                         'collapses': json.dumps(col), 'words_before': len(h.split()), 'words_after': len(new.split()),
                         'original': h, 'cleaned': new})
    changed = {x['clip_id'] for x in rows}
    g2_viol = sorted(changed - loop18)
    os.makedirs(MET, exist_ok=True)
    C.write_csv(os.path.join(MET, 'changed_clips.csv'), rows or [{'clip_id': ''}])
    freeze = {'rule_version': R.RULE_VERSION, 'frozen_files_sha256': {os.path.basename(p): sha(p) for p in RULE_FILES},
              'G1_references_changed': len(g1), 'G1_pass': not g1,
              'G2_changed_clips': len(changed), 'G2_changed_in_loop18': len(changed & loop18),
              'G2_loop18_not_changed': sorted(loop18 - changed),
              'G2_changed_outside_loop18': g2_viol, 'G2_pass': not g2_viol,
              'note': 'dry run: guards only, no metric computed'}
    json.dump(freeze, open(os.path.join(MET, 'rule_freeze.json'), 'w'), indent=1)
    print(json.dumps(freeze, indent=1))
    for x in rows:
        print(f"\n{x['clip_id']} loop18={x['in_taxonomy_loop18']} ref_rep3={x['ref_has_rep3']} {x['words_before']}->{x['words_after']} words\n"
              f"  before: {x['original']}\n  after : {x['cleaned']}")
    assert sha(BASELINE) == BASELINE_SHA


def stats(hyps, refs):
    e = [C.wer_p012(h, r) for h, r in zip(hyps, refs)]
    return {'bleu': np.array(_BLEU._extract_corpus_statistics(hyps, [refs]), float),
            'chrf': np.array(_CHRF._extract_corpus_statistics(hyps, [refs]), float),
            'wer': np.array(e, float)}


def corpus(st, idx):
    return {'bleu4': _BLEU._compute_score_from_stats(st['bleu'][idx].sum(0).tolist()).score,
            'chrf': _CHRF._compute_score_from_stats(st['chrf'][idx].sum(0).tolist()).score,
            'wer': 100 * st['wer'][idx, 0].sum() / st['wer'][idx, 1].sum()}


def evaluate():
    fz = json.load(open(os.path.join(MET, 'rule_freeze.json')))
    for p in RULE_FILES:
        assert sha(p) == fz['frozen_files_sha256'][os.path.basename(p)], f'{p} changed after the freeze: rerun --dry-run first'
    assert fz['G1_pass'], 'G1 failed: the rule changes a reference'
    lines, parsed, ids, hyp, refs, loop18 = load()
    new = [R.cleanup(h)[0] for h in hyp]
    os.makedirs(os.path.join(D, 'predictions'), exist_ok=True)
    out_p = os.path.join(D, 'predictions', 'A_official_cleaned.txt')
    with open(out_p, 'w', encoding='utf-8') as f:  # same 'sample: <id>.mp4, prediction: <text>' format
        for m, h0, h1 in zip(parsed, hyp, new):
            f.write(f'sample: {m.group(1)}, prediction: {h1}\n')
    # line-level check: unchanged predictions give byte-identical lines
    new_lines = [l.rstrip('\n') for l in open(out_p, encoding='utf-8')]
    assert all((a == b) == (h0 == h1) for a, b, h0, h1 in zip(lines, new_lines, hyp, new))

    rw = np.array([len(r.split()) for r in refs])
    S = {'full_128': np.arange(128),
         'loop18': np.array([k for k, i in enumerate(ids) if i in loop18]),
         'non_loop110': np.array([k for k, i in enumerate(ids) if i not in loop18]),
         'changed_by_rule': np.array([k for k in range(128) if new[k] != hyp[k]]),
         'ref_ge35_words': np.where(rw >= 35)[0]}
    ST = {'original': stats(hyp, refs), 'cleaned': stats(new, refs)}
    H = {'original': hyp, 'cleaned': new}
    res = {'rule_version': R.RULE_VERSION, 'bleurt': 'not available locally (no BLEURT-20 checkpoint); not computed',
           'subset_n': {k: int(len(v)) for k, v in S.items()}, 'metrics': {}, 'contrasts': {}}
    rows = []
    for sn, idx in S.items():
        for sysn in ('original', 'cleaned'):
            h = H[sysn]
            m = {'n': int(len(idx)), **{k: round(v, 4) for k, v in corpus(ST[sysn], idx).items()},
                 'loop_rate_taxonomy': round(float(np.mean([is_loop(h[i], refs[i]) for i in idx])), 4),
                 'loop_rate_ref_free_rep3_ge_0.15': round(float(np.mean([rep3_ratio(h[i]) >= 0.15 for i in idx])), 4),
                 'repetition_rate_taxonomy': round(float(np.mean([has_rep3(h[i]) and not has_rep3(refs[i]) for i in idx])), 4),
                 'mean_rep3_ratio': round(float(np.mean([rep3_ratio(h[i]) for i in idx])), 4),
                 'mean_sentence_chrf': round(float(np.mean([C.sentence_chrf(h[i], refs[i]) for i in idx])), 3),
                 'pred_words_total': int(sum(len(h[i].split()) for i in idx)), 'ref_words_total': int(rw[idx].sum()),
                 'byte_identical_to_original': int(sum(hyp[i] == new[i] for i in idx))}
            res['metrics'].setdefault(sn, {})[sysn] = m
            rows.append({'subset': sn, 'system': sysn, **m})
    rng = np.random.default_rng(SEED)
    for sn, idx in S.items():
        base, cl = corpus(ST['original'], idx), corpus(ST['cleaned'], idx)
        boot = {k: [] for k in base}
        for _ in range(N_BOOT):
            b = idx[rng.integers(0, len(idx), len(idx))]
            x, y = corpus(ST['original'], b), corpus(ST['cleaned'], b)
            for k in boot: boot[k].append(y[k] - x[k])
        res['contrasts'][sn] = {k: {'delta': round(cl[k] - base[k], 4),
                                    'ci95': [round(float(np.percentile(boot[k], 2.5)), 4), round(float(np.percentile(boot[k], 97.5)), 4)]}
                                for k in base}
    for r in rows:
        if r['system'] == 'cleaned':
            for k in ('bleu4', 'chrf', 'wer'):
                c = res['contrasts'][r['subset']][k]
                r[f'delta_{k}'], r[f'ci95_lo_{k}'], r[f'ci95_hi_{k}'] = c['delta'], c['ci95'][0], c['ci95'][1]
    per_clip = []
    for k, i in enumerate(ids):
        h0, h1 = hyp[k], new[k]
        per_clip.append({'idx': k, 'clip_id': i, 'in_taxonomy_loop18': i in loop18, 'changed': h0 != h1, 'ref_words': int(rw[k]),
                         'words_before': len(h0.split()), 'words_after': len(h1.split()),
                         'rep3_before': round(rep3_ratio(h0), 3), 'rep3_after': round(rep3_ratio(h1), 3),
                         'loop_before': is_loop(h0, refs[k]), 'loop_after': is_loop(h1, refs[k]),
                         'chrf_before': round(C.sentence_chrf(h0, refs[k]), 2), 'chrf_after': round(C.sentence_chrf(h1, refs[k]), 2),
                         'wer_edits_before': C.wer_p012(h0, refs[k])[0], 'wer_edits_after': C.wer_p012(h1, refs[k])[0],
                         'original': h0, 'cleaned': h1})
    # decision rule, fixed in CLEANUP_RULE.md
    L, Cn = res['metrics']['loop18'], res['contrasts']['loop18']
    crit = {'loop_rate_halved': L['cleaned']['loop_rate_taxonomy'] <= 0.5 * L['original']['loop_rate_taxonomy'],
            'wer_ci_below_0': Cn['wer']['ci95'][1] < 0,
            'chrf_delta_ge_-0.5': Cn['chrf']['delta'] >= -0.5,
            'non_loop_byte_identical': res['metrics']['non_loop110']['cleaned']['byte_identical_to_original'] == 110}
    res['decision'] = {'criteria': crit, 'useful': all(crit.values())}
    res['files'] = {'original_sha256': BASELINE_SHA, 'cleaned_sha256': sha(out_p)}
    C.write_csv(os.path.join(MET, 'cleanup_comparison.csv'), rows)
    C.write_csv(os.path.join(MET, 'per_clip.csv'), per_clip)
    json.dump(res, open(os.path.join(MET, 'cleanup_summary.json'), 'w'), indent=1)
    assert sha(BASELINE) == BASELINE_SHA, 'original changed during the run'
    for r in rows:
        print(f"{r['subset']:16s} {r['system']:8s} n={r['n']:3d} WER {r['wer']:7.2f} chrF {r['chrf']:6.2f} BLEU-4 {r['bleu4']:6.2f} "
              f"loop {r['loop_rate_taxonomy']:.3f} rep3 {r['mean_rep3_ratio']:.3f} sChrF {r['mean_sentence_chrf']:.2f}")
    print(json.dumps(res['contrasts'], indent=1)); print(json.dumps(res['decision'], indent=1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--dry-run', action='store_true')
    dry_run() if ap.parse_args().dry_run else evaluate()
