# Chunked-decoding pilot: full analysis (laptop, CPU). FROZEN before any GPU output exists; sha256 in ../FREEZE.sha256.
# Inputs : <run root>/{SMOKE,U36,S1,S2,S3}/ copied back from the VM (test_tmp_pres.txt, test_decode_diag.jsonl, SHA256SUMS,
#          run.log), <run root>/U36_GATE.json, <run root>/loader_check.json, optional <run root>/bleurt.jsonl;
#          ../chunk_plan.csv, ../pilot_clips.csv; committed R100 = asl-p0-12-full128-fp16/predictions/A_official.txt.
# Definitions (all fixed here):
#   subsets   target  = pilot_clips group long_ref_ge35 (21 clips, reference >= 35 words, all > 256 frames)
#             control = group control_gt256_ref_lt35 (15 clips, > 256 frames, reference < 35 words)
#             all36   = target + control
#   arms      U36 = unchunked baseline (36 clips taken from the 128-entry U36 run; gated byte-identical to R100)
#             S2, S3 = PRIMARY (no chunk > 256 frames, no random subsampling); S1 = EXPLORATORY (still subsamples)
#   join      pilot_join.join_chunks (temporal order, strip, drop empty, single space; nothing else)
#   refs      manifest reference_text (taxonomy common.load_refs), the canonical P0-12 references
#   BLEU-4    corpus sacrebleu BLEU, max order 4, tokenize 13a (= Uni-Sign SLRT sableu)
#   chrF      corpus sacrebleu chrF defaults (char order 6, beta 2)
#   WER       100 * sum(edits) / sum(ref words), lowercase whitespace tokens, punctuation kept (P0-12 score_conditions.py)
#   length    corpus length ratio = sum(predicted whitespace words) / sum(reference whitespace words)
#   loop      taxonomy repetition_loop: prediction repeats a word 3-gram, the reference repeats none, rep-3-gram ratio >= 0.15
#   trunc     last character of the prediction not in . ? ! "
#   BLEURT    mean sentence BLEURT-20 (bleurt_score.py on the VM); secondary, no decision weight
#   bootstrap paired clip-level, 2000 resamples, numpy default_rng(seed 0) created fresh for every (arm, subset);
#             the same resampled clip indices for arm and U36; CI = 2.5 / 97.5 percentiles of (arm - U36)
#   T1 target length ratio >= 0.85            T2 target dchrF >= +2.0 and CI low > 0      T3 target dBLEU-4 >= 0
#   T4 control dchrF >= -2.0 and control length ratio <= 1.3                               T5 all36 loops <= U36 loops + 2
#   pass      T1-T5 all true. Verdict is reported for S2/S3 as primary, for S1 as exploratory.
# Hard gates before any metric: loader_check pass, U36 gate pass (36/36 byte-identical to R100, re-checked here), every
# run folder complete (entry count == plan, SHA256SUMS match), and U36 metrics on the 36 == R100 metrics on the 36.
# Usage: python3 -I analyze_pilot.py [--runs ../results/out] [--out ../metrics]
import argparse, hashlib, json, os, sys
import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(D, '..', '..', '10.13', 'asl-unisign-error-taxonomy', 'scripts'))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
from pilot_join import arm_outputs, load_plan, read_pres  # noqa: E402
from sacrebleu.metrics import BLEU, CHRF  # noqa: E402

BASELINE = os.path.join(C.P012_PRED, 'A_official.txt')
BASELINE_SHA = 'd865008bc0a16ba0fb3bceb6f78f5a7153febe1d69ba756cc83f918d57300e4a'
ARMS = ['U36', 'S1', 'S2', 'S3']
ROLE = {'S1': 'exploratory', 'S2': 'primary', 'S3': 'primary'}
N_BOOT, SEED = 2000, 0
_BLEU, _CHRF = BLEU(max_ngram_order=4, tokenize='13a'), CHRF()


def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def has_rep3(s):
    w = s.lower().split(); g = [tuple(w[k:k + 3]) for k in range(len(w) - 2)]
    return len(g) > 0 and len(set(g)) < len(g)


def rep3_ratio(s):
    w = s.lower().split(); g = [tuple(w[k:k + 3]) for k in range(len(w) - 2)]
    return 0.0 if not g else 1 - len(set(g)) / len(g)


def is_loop(h, r): return has_rep3(h) and not has_rep3(r) and rep3_ratio(h) >= 0.15
def is_trunc(h): return h.rstrip()[-1:] not in '.?!"'


def stats(hyps, refs):
    return {'bleu': np.array(_BLEU._extract_corpus_statistics(hyps, [refs]), float),
            'chrf': np.array(_CHRF._extract_corpus_statistics(hyps, [refs]), float),
            'wer': np.array([C.wer_p012(h, r) for h, r in zip(hyps, refs)], float),
            'len': np.array([[len(h.split()), len(r.split())] for h, r in zip(hyps, refs)], float)}


def corpus(st, idx):
    return {'bleu4': _BLEU._compute_score_from_stats(st['bleu'][idx].sum(0).tolist()).score,
            'chrf': _CHRF._compute_score_from_stats(st['chrf'][idx].sum(0).tolist()).score,
            'wer': 100 * st['wer'][idx, 0].sum() / st['wer'][idx, 1].sum(),
            'length_ratio': st['len'][idx, 0].sum() / st['len'][idx, 1].sum()}


def verify(runs, plan, clips):
    V = {}
    def chk(k, ok):
        V[k] = bool(ok)
        if not ok: sys.exit(f'GATE FAILED: {k}')
    lc = json.load(open(os.path.join(runs, 'loader_check.json')))
    chk('loader/frame-slice validation passed on the VM', lc['pass'])
    chk('S2/S3: no chunk > 256 frames and no random subsampling',
        all(lc['arms'][a]['chunks_gt256'] == 0 and lc['arms'][a]['random_sample_called'] == 0 for a in ('S2', 'S3')))
    g = json.load(open(os.path.join(runs, 'U36_GATE.json')))
    chk('U36 gate (VM): 36/36 pilot predictions byte-identical to R100', g['pass'] and g['pilot36_identical'] == 36)
    B = dict(read_pres(BASELINE)); U = arm_outputs(runs, D, 'U36')
    chk('U36 gate re-checked locally: 36/36 byte-identical', all(U[c['clip_id']] == B[c['clip_id']] for c in clips))
    n_plan = {a: sum(r['arm'] == a for r in plan) for a in ('S1', 'S2', 'S3')}
    n_plan['U36'] = 128
    for a in ARMS:
        d = os.path.join(runs, a)
        chk(f'{a}: {n_plan[a]} prediction lines and diag rows',
            len(read_pres(os.path.join(d, 'test_tmp_pres.txt'))) == n_plan[a]
            == sum(1 for _ in open(os.path.join(d, 'test_decode_diag.jsonl'))))
        for l in open(os.path.join(d, 'SHA256SUMS')):
            h, p = l.split(None, 1)
            chk(f'{a}: SHA256SUMS {os.path.basename(p.strip())}', sha(os.path.join(d, os.path.basename(p.strip()))) == h)
    return V, g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', default=os.path.join(D, 'results', 'out'))
    ap.add_argument('--out', default=os.path.join(D, 'metrics'))
    a = ap.parse_args()
    assert sha(BASELINE) == BASELINE_SHA
    plan, clips = load_plan(D)
    V, gate = verify(a.runs, plan, clips)
    os.makedirs(a.out, exist_ok=True)
    ids = [c['clip_id'] for c in clips]; grp = {c['clip_id']: c['group'] for c in clips}
    refs_d = C.load_refs(); refs = [refs_d[i] for i in ids]
    S = {'target_long_ref_21': np.array([k for k, i in enumerate(ids) if grp[i] == 'long_ref_ge35']),
         'control_short_ref_15': np.array([k for k, i in enumerate(ids) if grp[i] == 'control_gt256_ref_lt35']),
         'all_36': np.arange(len(ids))}
    assert [len(v) for v in S.values()] == [21, 15, 36]
    H = {arm: [arm_outputs(a.runs, D, arm)[i] for i in ids] for arm in ARMS}
    R100 = dict(read_pres(BASELINE)); H['R100'] = [R100[i] for i in ids]
    ST = {k: stats(v, refs) for k, v in H.items()}
    for sn, idx in S.items():  # U36 metrics must equal R100 metrics on the same clips
        V[f'U36 metrics == R100 metrics ({sn})'] = corpus(ST['U36'], idx) == corpus(ST['R100'], idx)
        if not V[f'U36 metrics == R100 metrics ({sn})']: sys.exit(f'GATE FAILED: U36 metrics != R100 metrics on {sn}')
    bl = {}
    bp = os.path.join(a.runs, 'bleurt.jsonl')
    if os.path.exists(bp):
        for l in open(bp):
            x = json.loads(l); bl[(x['arm'], x['clip_id'])] = x['bleurt']
            assert x['hyp'] == H[x['arm']][ids.index(x['clip_id'])], 'bleurt.jsonl hypothesis != joined output'
    BL = {arm: (np.array([bl[(arm, i)] for i in ids]) if all((arm, i) in bl for i in ids) else None) for arm in ARMS}

    res = {'roles': ROLE, 'verification': V, 'u36_gate': gate, 'subset_n': {k: int(len(v)) for k, v in S.items()},
           'metrics': {}, 'contrasts': {}, 'decision': {}}
    rows = []
    for arm in ARMS:
        h = H[arm]
        for sn, idx in S.items():
            m = {k: round(v, 4) for k, v in corpus(ST[arm], idx).items()}
            m.update({'n': int(len(idx)), 'loops': int(sum(is_loop(h[i], refs[i]) for i in idx)),
                      'truncation_rate': round(float(np.mean([is_trunc(h[i]) for i in idx])), 4),
                      'mean_rep3_ratio': round(float(np.mean([rep3_ratio(h[i]) for i in idx])), 4),
                      'pred_words_median': float(np.median([len(h[i].split()) for i in idx])),
                      'pred_words_max': int(max(len(h[i].split()) for i in idx)),
                      'bleurt_mean': None if BL[arm] is None else round(float(BL[arm][idx].mean()), 4)})
            res['metrics'].setdefault(arm, {})[sn] = m
            rows.append({'arm': arm, 'role': ROLE.get(arm, 'baseline'), 'subset': sn, **m})
    for arm in ('S1', 'S2', 'S3'):
        for sn, idx in S.items():
            rng = np.random.default_rng(SEED)
            base, new = corpus(ST['U36'], idx), corpus(ST[arm], idx)
            keys = list(base) + (['bleurt'] if BL[arm] is not None and BL['U36'] is not None else [])
            if 'bleurt' in keys:
                base['bleurt'], new['bleurt'] = BL['U36'][idx].mean(), BL[arm][idx].mean()
            boot = {k: [] for k in keys}
            for _ in range(N_BOOT):
                b = idx[rng.integers(0, len(idx), len(idx))]
                x, y = corpus(ST['U36'], b), corpus(ST[arm], b)
                if 'bleurt' in keys:
                    x['bleurt'], y['bleurt'] = BL['U36'][b].mean(), BL[arm][b].mean()
                for k in keys: boot[k].append(y[k] - x[k])
            res['contrasts'].setdefault(arm, {})[sn] = {
                k: {'delta': round(new[k] - base[k], 4),
                    'ci95': [round(float(np.percentile(boot[k], 2.5)), 4), round(float(np.percentile(boot[k], 97.5)), 4)]}
                for k in keys}
        M, Cn = res['metrics'][arm], res['contrasts'][arm]
        t = {'T1_target_length_ratio_ge_0.85': M['target_long_ref_21']['length_ratio'] >= 0.85,
             'T2_target_dchrF_ge_2_and_ci_low_gt_0': Cn['target_long_ref_21']['chrf']['delta'] >= 2.0
                                                     and Cn['target_long_ref_21']['chrf']['ci95'][0] > 0,
             'T3_target_dBLEU4_ge_0': Cn['target_long_ref_21']['bleu4']['delta'] >= 0,
             'T4_control_dchrF_ge_-2_and_length_ratio_le_1.3': Cn['control_short_ref_15']['chrf']['delta'] >= -2.0
                                                               and M['control_short_ref_15']['length_ratio'] <= 1.3,
             'T5_all36_loops_le_U36_plus_2': M['all_36']['loops'] <= res['metrics']['U36']['all_36']['loops'] + 2}
        t = {k: bool(v) for k, v in t.items()}
        res['decision'][arm] = {'role': ROLE[arm], 'criteria': t, 'pass': all(t.values())}
    for r in rows:
        c = res['contrasts'].get(r['arm'], {}).get(r['subset'], {})
        for k in ('bleu4', 'chrf', 'wer', 'length_ratio', 'bleurt'):
            r[f'delta_{k}'] = c[k]['delta'] if k in c else ''
            r[f'ci95_lo_{k}'], r[f'ci95_hi_{k}'] = c[k]['ci95'] if k in c else ('', '')
    # per chunk: decode diagnostics (EOS, cap, tokens) joined to the plan
    chunk_rows = []
    for arm in ('S1', 'S2', 'S3'):
        dg = [json.loads(l) for l in open(os.path.join(a.runs, arm, 'test_decode_diag.jsonl'))]
        pr = dict(read_pres(os.path.join(a.runs, arm, 'test_tmp_pres.txt')))
        dd = {x['sample'][:-4]: x for x in dg}
        for r in plan:
            if r['arm'] != arm: continue
            x = dd[r['chunk_name']]
            chunk_rows.append({**r, 'eos': x['eos'], 'hit_cap': x['hit_cap'], 'n_gen_tokens': x['n_gen_tokens'],
                               'pred_words': x['pred_words'], 'prediction': pr[r['chunk_name']]})
        cr = [x for x in chunk_rows if x['arm'] == arm]
        res.setdefault('chunk_diagnostics', {})[arm] = {
            'chunks': len(cr), 'eos': sum(x['eos'] for x in cr), 'cap_hits': sum(x['hit_cap'] for x in cr),
            'gen_tokens_median': float(np.median([x['n_gen_tokens'] for x in cr])),
            'eos_at_48_52_tokens': sum(x['eos'] and 48 <= x['n_gen_tokens'] <= 52 for x in cr),
            'empty_predictions': sum(not x['prediction'].strip() for x in cr)}
    per_clip = []
    for k, i in enumerate(ids):
        r = {'clip_id': i, 'group': grp[i], 'ref_words': len(refs[k].split()), 'reference': refs[k]}
        for arm in ARMS:
            h = H[arm][k]
            r.update({f'{arm}_words': len(h.split()), f'{arm}_chrf': round(C.sentence_chrf(h, refs[k]), 2),
                      f'{arm}_loop': is_loop(h, refs[k]), f'{arm}_bleurt': None if BL[arm] is None else round(float(BL[arm][k]), 4),
                      f'{arm}_prediction': h})
        per_clip.append(r)
    # secondary: full 128 with the 92 <= 256-frame clips at their committed R100 outputs (unchanged by design)
    all_ids = [i for i, _ in C.load_labels()]; all_refs = [refs_d[i] for i in all_ids]
    res['full128_spliced_secondary'] = {}
    for arm in ARMS:
        A_ = arm_outputs(a.runs, D, arm)
        hy = [A_.get(i, R100[i]) for i in all_ids]
        res['full128_spliced_secondary'][arm] = {k: round(v, 4) for k, v in corpus(stats(hy, all_refs), np.arange(128)).items()}
    res['analysis_script_sha256'] = sha(os.path.abspath(__file__))
    C.write_csv(os.path.join(a.out, 'pilot_comparison.csv'), rows)
    C.write_csv(os.path.join(a.out, 'per_clip.csv'), per_clip)
    C.write_csv(os.path.join(a.out, 'per_chunk.csv'), chunk_rows)
    json.dump(res, open(os.path.join(a.out, 'pilot_summary.json'), 'w'), indent=1)
    for r in rows:
        print(f"{r['arm']:4s} {r['role']:11s} {r['subset']:21s} n={r['n']:2d} chrF {r['chrf']:6.2f} BLEU-4 {r['bleu4']:6.2f} "
              f"WER {r['wer']:6.2f} len {r['length_ratio']:.3f} loops {r['loops']} trunc {r['truncation_rate']:.2f} "
              f"BLEURT {r['bleurt_mean']}  d_chrF {r['delta_chrf']} [{r['ci95_lo_chrf']}, {r['ci95_hi_chrf']}]")
    print(json.dumps(res['decision'], indent=1)); print(json.dumps(res['chunk_diagnostics'], indent=1))
    assert sha(BASELINE) == BASELINE_SHA


if __name__ == '__main__':
    main()
