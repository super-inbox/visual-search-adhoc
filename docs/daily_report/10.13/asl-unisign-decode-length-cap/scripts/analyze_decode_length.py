# Decode-length-cap analysis: R100 / R150 / R256 (A_official, max_new_tokens 100 / 150 / 256), CPU only.
# Inputs : <runs-root>/A_official_mnt{100,150,256}/ (copied back verbatim from the VM: test_tmp_pres.txt, test_tmp_refs.txt,
#          test_decode_diag.jsonl, run.log, SHA256SUMS, RUNTIME_INPUTS_A_official.sha256; R100 also R100_GATE.json),
#          references = manifest reference_text, frame counts = taxonomy inputs_128.jsonl (A_official PKL frames).
# verify() runs first and stops on any failed check (counts, clip order, refs, checksums, manifests, diagnostics, gate, flags).
# Metrics: reuse ../../asl-unisign-error-taxonomy/scripts/common.py (corpus BLEU-4 sacrebleu 13a, corpus chrF,
#          WER = score_conditions.py definition). Repetition / truncation = taxonomy.py definitions (copied below).
# Paired clip-level bootstrap, 2000 resamples, seed 0 (as P0-12 contrasts.py), on corpus WER / chrF / BLEU-4 per subset.
# Usage: python -I analyze_decode_length.py [--runs-root ../results/out] [--out ../metrics]
# Writes: decode_length_comparison.csv (one row per run, full 128), subset_comparison.csv (run x subset, with deltas vs R100
#         and paired bootstrap CIs), decode_length_summary.json, per_clip.csv, verification.json
import argparse, hashlib, json, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TAX = os.path.join(HERE, '..', '..', 'asl-unisign-error-taxonomy')
sys.dont_write_bytecode = True  # do not leave __pycache__ in the committed taxonomy folder
sys.path.insert(0, os.path.join(TAX, 'scripts'))
import common as C  # noqa: E402
from sacrebleu.metrics import BLEU, CHRF  # noqa: E402

RUNS = {'R100': 100, 'R150': 150, 'R256': 256}
BASELINE_SHA = 'd865008bc0a16ba0fb3bceb6f78f5a7153febe1d69ba756cc83f918d57300e4a'
BASELINE = os.path.join(C.P012_PRED, 'A_official.txt')
N_BOOT, SEED = 2000, 0
_BLEU, _CHRF = BLEU(max_ngram_order=4, tokenize='13a'), CHRF()


def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def has_rep3(s):  # taxonomy.py
    w = s.lower().split(); g = [tuple(w[k:k + 3]) for k in range(len(w) - 2)]
    return len(g) > 0 and len(set(g)) < len(g)


def rep3_ratio(s):  # taxonomy.py
    w = s.lower().split(); g = [tuple(w[k:k + 3]) for k in range(len(w) - 2)]
    return 0.0 if not g else 1 - len(set(g)) / len(g)


def load_run(d):
    P = []
    for line in open(os.path.join(d, 'test_tmp_pres.txt'), encoding='utf-8'):
        m = C.LINE_RE.match(line.rstrip('\n')); P.append((m.group(1).replace('.mp4', ''), m.group(2)))
    D = [json.loads(l) for l in open(os.path.join(d, 'test_decode_diag.jsonl'))]
    assert len(P) == len(D) == 128 and [c for c, _ in P] == [x['sample'].replace('.mp4', '') for x in D], d
    return P, D


REF_RE = re.compile(r'^sample: (.*?), ground-truth: (.*)$')
LOG_RE = {'log_bleu4_sableu': re.compile(r"'bleu4': ([0-9.]+)"), 'log_rouge': re.compile(r'^Rouge: ([0-9.]+)', re.M),
          'log_bleurt': re.compile(r'^BLEURT: ([0-9.]+)', re.M)}
CMD_RE = re.compile(r"process \d+ spawned with command: (\[.*\])")


def parse_log(d):
    """Official Uni-Sign scorer outputs printed in run.log (SLRT sableu BLEU-4, ROUGE, BLEURT) and the launch flags."""
    t = open(os.path.join(d, 'run.log'), encoding='utf-8', errors='replace').read()
    m = {k: (float(r.findall(t)[-1]) if r.findall(t) else None) for k, r in LOG_RE.items()}
    cmd = CMD_RE.findall(t)
    flags = [x for x in eval(cmd[-1]) if 'output_dir' not in x and '/out/A_official_mnt' not in x] if cmd else None  # noqa: S307 (own VM log)
    return m, flags


def verify(root, labels, refs):
    ids = [i for i, _ in labels]
    """Hard checks on the three copied-back run folders. Any failure raises; the result is written to verification.json."""
    V, chk = {}, lambda k, ok: V.__setitem__(k, bool(ok)) or (ok or sys.exit(f'VERIFY FAILED: {k}'))
    pinned = os.path.join(root, 'RUNTIME_INPUTS_A_official.sha256')
    man = {}
    for name, n in RUNS.items():
        d = os.path.join(root, f'A_official_mnt{n}')
        pres = [l.rstrip('\n') for l in open(os.path.join(d, 'test_tmp_pres.txt'), encoding='utf-8')]
        rf = [REF_RE.match(l.rstrip('\n')) for l in open(os.path.join(d, 'test_tmp_refs.txt'), encoding='utf-8')]
        D = [json.loads(l) for l in open(os.path.join(d, 'test_decode_diag.jsonl'))]
        chk(f'{name}: 128 predictions / refs / diag lines', len(pres) == len(rf) == len(D) == 128)
        chk(f'{name}: every prediction / ref line parses', all(C.LINE_RE.match(l) for l in pres) and all(rf))
        chk(f'{name}: clip order == labels.test_p012_128 (preds, refs, diag)',
            [C.LINE_RE.match(l).group(1).replace('.mp4', '') for l in pres] == ids
            == [m.group(1).replace('.mp4', '') for m in rf] == [x['sample'].replace('.mp4', '') for x in D])
        # the VM scorer reads raw labels.test text (3 lines carry mojibake apostrophes); the manifest has them fixed
        chk(f'{name}: refs == labels.test_p012_128 text', [m.group(2) for m in rf] == [t for _, t in labels])
        chk(f'{name}: refs == manifest reference_text after fix_mojibake', [C.fix_mojibake(m.group(2)) for m in rf] == refs)
        # SHA256SUMS lists absolute VM paths; check by basename
        for l in open(os.path.join(d, 'SHA256SUMS')):
            h, p = l.split(None, 1)
            chk(f'{name}: SHA256SUMS {os.path.basename(p.strip())}', sha(os.path.join(d, os.path.basename(p.strip()))) == h)
        man[name] = sha(os.path.join(d, 'RUNTIME_INPUTS_A_official.sha256'))
        lines = open(os.path.join(d, 'RUNTIME_INPUTS_A_official.sha256')).read().split('\n')
        chk(f'{name}: runtime manifest lists 128 A_official PKLs',
            sum(1 for l in lines if l.strip().endswith('.pkl') and 'A_official/' in l) == 128)
        mt = [l.rstrip('\n') for l in pres]
        chk(f'{name}: diag max_new_tokens == {n}, first id 0, n_new <= {n}',
            all(x['max_new_tokens'] == n and x['first_id'] == 0 and x['n_new_tokens'] <= n for x in D))
        chk(f'{name}: diag hit_cap <=> no EOS and {n} tokens; eos xor hit_cap',
            all(x['hit_cap'] == (not x['eos'] and x['n_gen_tokens'] == n) and (x['eos'] != x['hit_cap']) for x in D))
        chk(f'{name}: diag n_gen_tokens == len(gen_ids); pred_words == prediction words',
            all(x['n_gen_tokens'] == len(x['gen_ids']) and x['pred_words'] == len(C.LINE_RE.match(t).group(2).split())
                for x, t in zip(D, mt)))
    chk('runtime manifests identical across R100/R150/R256 and == pinned out/RUNTIME_INPUTS_A_official.sha256',
        len(set(man.values())) == 1 and sha(pinned) == man['R100'])
    chk('test_tmp_refs.txt byte-identical across runs',
        len({sha(os.path.join(root, f'A_official_mnt{n}', 'test_tmp_refs.txt')) for n in RUNS.values()}) == 1)
    g = json.load(open(os.path.join(root, 'A_official_mnt100', 'R100_GATE.json')))
    chk('R100_GATE.json verdict REPRODUCED_EXACT, 128 identical lines',
        g['verdict'] == 'REPRODUCED_EXACT' and g['identical_lines'] == 128 and not g['hard_failures'])
    chk('R100 test_tmp_pres.txt sha256 == committed A_official.txt',
        sha(os.path.join(root, 'A_official_mnt100', 'test_tmp_pres.txt')) == BASELINE_SHA)
    flags = {name: parse_log(os.path.join(root, f'A_official_mnt{n}'))[1] for name, n in RUNS.items()}
    chk('launch flags identical across runs (except --output_dir)', flags['R100'] and flags['R100'] == flags['R150'] == flags['R256'])
    return {'checks': V, 'runtime_manifest_sha256': man['R100'], 'launch_flags': flags['R100']}


def dist(x):
    x = np.asarray(x, float)
    return {'min': float(x.min()), 'median': float(np.median(x)), 'p90': round(float(np.percentile(x, 90)), 2),
            'max': float(x.max()), 'mean': round(float(x.mean()), 2)} if len(x) else None


def stats(hyps, refs):
    """Per-clip sufficient statistics so corpus metrics can be recomputed on any resample."""
    e = [C.wer_p012(h, r) for h, r in zip(hyps, refs)]
    return {'bleu': np.array(_BLEU._extract_corpus_statistics(hyps, [refs]), float),
            'chrf': np.array(_CHRF._extract_corpus_statistics(hyps, [refs]), float),
            'wer': np.array(e, float)}


def corpus(st, idx):
    return {'bleu4': _BLEU._compute_score_from_stats(st['bleu'][idx].sum(0).tolist()).score,
            'chrf': _CHRF._compute_score_from_stats(st['chrf'][idx].sum(0).tolist()).score,
            'wer': 100 * st['wer'][idx, 0].sum() / st['wer'][idx, 1].sum()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs-root', default=os.path.join(HERE, '..', 'results', 'out'))
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'metrics'))
    a = ap.parse_args()
    assert sha(BASELINE) == BASELINE_SHA, 'committed A_official.txt changed'
    os.makedirs(a.out, exist_ok=True)

    labels = C.load_labels(); ids = [i for i, _ in labels]; refs_d = C.load_refs(); refs = [refs_d[i] for i in ids]
    inp = {r['clip_id']: r for r in C.read_jsonl(os.path.join(TAX, 'inputs_128.jsonl'))}
    frames = np.array([inp[i]['pose']['A_official']['frames'] for i in ids]); ref_w = np.array([len(r.split()) for r in refs])
    ver = verify(a.runs_root, labels, refs)
    print(f"verification: {sum(ver['checks'].values())}/{len(ver['checks'])} checks passed")
    runs = {}
    for name, n in RUNS.items():
        d = os.path.join(a.runs_root, f'A_official_mnt{n}')
        P, D = load_run(d)
        runs[name] = {'hyp': [p for _, p in P], 'diag': D, 'log': parse_log(d)[0]}
    # mT5 tokens per word, calibrated on R100 EOS-terminated outputs (no tokenizer locally): only used to flag references
    # that probably exceed the 50-token training target cap. An ESTIMATE, labelled as such everywhere.
    d0 = [x for x in runs['R100']['diag'] if x['eos']]
    tpw = sum(x['n_gen_tokens'] for x in d0) / sum(x['pred_words'] for x in d0)
    est_ref_tok = ref_w * tpw

    S = {  # subsets (indices into the 128 clips in labels order)
        'full_128': np.arange(128),
        'ref_ge35_words': np.where(ref_w >= 35)[0],
        'frames_gt256': np.where(frames > 256)[0],
        'ref_ge35__frames_gt256': np.where((ref_w >= 35) & (frames > 256))[0],
        'ref_ge35__frames_le256': np.where((ref_w >= 35) & (frames <= 256))[0],
        # supplementary length-vs-frames split (the requested within->=35 split has no <=256-frame clips)
        'frames_gt256__ref_lt35': np.where((frames > 256) & (ref_w < 35))[0],
        'frames_le256': np.where(frames <= 256)[0],
        # extra long-reference cuts
        'ref_ge45_words': np.where(ref_w >= 45)[0],
        'est_ref_tokens_gt50': np.where(est_ref_tok > 50)[0],
        'R100_cap_hit_clips': np.where([x['hit_cap'] for x in runs['R100']['diag']])[0],
    }
    ST = {k: stats(v['hyp'], refs) for k, v in runs.items()}
    out = {'baseline_sha256_unchanged': True, 'runs_present': list(runs), 'subset_n': {k: int(len(v)) for k, v in S.items()},
           'mt5_tokens_per_word_R100_estimate': round(tpw, 4), 'official_log_metrics': {k: v['log'] for k, v in runs.items()},
           'pearson_frames_vs_ref_words': round(float(np.corrcoef(frames, ref_w)[0, 1]), 3), 'metrics': {}, 'contrasts': {},
           'change_diagnostics': {}}
    rows = []
    for rn, R in runs.items():
        hyp, D = R['hyp'], R['diag']
        pw = np.array([len(h.split()) for h in hyp]); gt = np.array([d['n_gen_tokens'] for d in D])
        for sn, idx in S.items():
            if len(idx) == 0:
                out['metrics'].setdefault(rn, {})[sn] = {'n': 0, 'note': 'empty subset: not estimable'}; continue
            m = {'n': int(len(idx)), **{k: round(v, 4) for k, v in corpus(ST[rn], idx).items()},
                 'cap_hit_count': int(sum(D[i]['hit_cap'] for i in idx)), 'eos_count': int(sum(D[i]['eos'] for i in idx)),
                 'cap_hit_rate': round(float(np.mean([D[i]['hit_cap'] for i in idx])), 4),
                 # EOS-terminated outputs ending within +-2 tokens of the 50-token training target cap (models.py max_length=50)
                 'eos_at_48_52_tokens_count': int(sum(D[i]['eos'] and 48 <= D[i]['n_gen_tokens'] <= 52 for i in idx)),
                 'gen_tokens_gt52_count': int(sum(D[i]['n_gen_tokens'] > 52 for i in idx)),
                 'eos_rate': round(float(np.mean([D[i]['eos'] for i in idx])), 4),
                 'truncation_rate_no_terminal_punct': round(float(np.mean([hyp[i].rstrip()[-1:] not in '.?!"' for i in idx])), 4),
                 'repetition_rate': round(float(np.mean([has_rep3(hyp[i]) and not has_rep3(refs[i]) for i in idx])), 4),
                 'repetition_loop_rate': round(float(np.mean([has_rep3(hyp[i]) and not has_rep3(refs[i]) and rep3_ratio(hyp[i]) >= 0.15 for i in idx])), 4),
                 'pred_words': dist(pw[idx]), 'gen_tokens': dist(gt[idx]),
                 'length_ratio_corpus': round(float(pw[idx].sum() / ref_w[idx].sum()), 4),
                 'length_ratio_median_clip': round(float(np.median(pw[idx] / ref_w[idx])), 4)}
            out['metrics'].setdefault(rn, {})[sn] = m
            rows.append({'run': rn, 'subset': sn, **{k: v for k, v in m.items() if not isinstance(v, dict)},
                         **{f'pred_words_{k}': v for k, v in m['pred_words'].items()},
                         **{f'gen_tokens_{k}': v for k, v in m['gen_tokens'].items()}})

    rng = np.random.default_rng(SEED)
    for rn in [r for r in runs if r != 'R100']:
        for sn, idx in S.items():
            if len(idx) < 2: continue
            base, new = corpus(ST['R100'], idx), corpus(ST[rn], idx)
            boot = {k: [] for k in base}
            for _ in range(N_BOOT):
                b = idx[rng.integers(0, len(idx), len(idx))]
                x, y = corpus(ST['R100'], b), corpus(ST[rn], b)
                for k in boot: boot[k].append(y[k] - x[k])
            out['contrasts'].setdefault(f'{rn}_minus_R100', {})[sn] = {
                k: {'delta': round(new[k] - base[k], 4), 'ci95': [round(float(np.percentile(boot[k], 2.5)), 4),
                                                                   round(float(np.percentile(boot[k], 97.5)), 4)]}
                for k in base}
        # what changed: R100 EOS-terminated clips should be unaffected by a larger budget; cap-hit clips are the test
        h0, d0, h1, d1 = runs['R100']['hyp'], runs['R100']['diag'], runs[rn]['hyp'], runs[rn]['diag']
        eos0 = [i for i in range(128) if d0[i]['eos']]; cap0 = [i for i in range(128) if d0[i]['hit_cap']]
        out['change_diagnostics'][rn] = {
            'identical_to_R100': sum(h0[i] == h1[i] for i in range(128)),
            'R100_eos_clips': len(eos0), 'R100_eos_clips_identical': sum(h0[i] == h1[i] for i in eos0),
            'R100_cap_hit_clips': len(cap0),
            'R100_cap_hit_clips_now_eos': sum(d1[i]['eos'] for i in cap0),
            'R100_cap_hit_clips_still_cap_hit': sum(d1[i]['hit_cap'] for i in cap0),
            'R100_cap_hit_clips_prefix_preserved': sum(h1[i].startswith(h0[i].rstrip()) for i in cap0),
            'R100_cap_hit_clips_added_words': dist([len(h1[i].split()) - len(h0[i].split()) for i in cap0]) if cap0 else None,
            'R100_cap_hit_clips_repetition_loop': sum(rep3_ratio(h1[i]) >= 0.15 for i in cap0),
            'R100_cap_hit_clips_delta_sentence_chrf': dist([C.sentence_chrf(h1[i], refs[i]) - C.sentence_chrf(h0[i], refs[i]) for i in cap0]) if cap0 else None,
        }
    per_clip = []
    for k, i in enumerate(ids):
        r = {'idx': k, 'clip_id': i, 'frames': int(frames[k]), 'ref_words': int(ref_w[k])}
        for rn, R in runs.items():
            d = R['diag'][k]; h = R['hyp'][k]
            r.update({f'{rn}_eos': d['eos'], f'{rn}_hit_cap': d['hit_cap'], f'{rn}_gen_tokens': d['n_gen_tokens'],
                      f'{rn}_pred_words': len(h.split()), f'{rn}_chrf': round(C.sentence_chrf(h, refs[k]), 2),
                      f'{rn}_rep3_ratio': round(rep3_ratio(h), 3), f'{rn}_prediction': h})
        per_clip.append(r)
    # paired contrasts vs R100 joined onto the run x subset rows (R100 rows carry no delta)
    for r in rows:
        c = out['contrasts'].get(f"{r['run']}_minus_R100", {}).get(r['subset'], {})
        for k in ('bleu4', 'chrf', 'wer'):
            r[f'delta_{k}_vs_R100'] = c[k]['delta'] if c else ''
            r[f'ci95_lo_{k}'], r[f'ci95_hi_{k}'] = (c[k]['ci95'] if c else ('', ''))
    full = []
    for r in rows:
        if r['subset'] != 'full_128': continue
        ch = out['change_diagnostics'].get(r['run'], {})
        full.append({'run': r['run'], 'max_new_tokens': RUNS[r['run']], **{k: v for k, v in r.items() if k not in ('run', 'subset')},
                     **runs[r['run']]['log'],
                     'clips_identical_to_R100': ch.get('identical_to_R100', 128),
                     'R100_cap_hit_clips_now_eos': ch.get('R100_cap_hit_clips_now_eos', ''),
                     'pred_sha256': sha(os.path.join(a.runs_root, f"A_official_mnt{RUNS[r['run']]}", 'test_tmp_pres.txt'))})
    C.write_csv(os.path.join(a.out, 'decode_length_comparison.csv'), full)
    C.write_csv(os.path.join(a.out, 'subset_comparison.csv'), rows)
    C.write_csv(os.path.join(a.out, 'per_clip.csv'), per_clip)
    assert sha(BASELINE) == BASELINE_SHA, 'committed A_official.txt changed during analysis'
    json.dump(out, open(os.path.join(a.out, 'decode_length_summary.json'), 'w'), indent=1)
    json.dump(ver, open(os.path.join(a.out, 'verification.json'), 'w'), indent=1)
    for rn in runs:
        for sn in ('full_128', 'ref_ge35_words', 'frames_gt256', 'frames_le256'):
            m = out['metrics'][rn][sn]
            print(f"{rn} {sn:16s} n={m['n']:3d} WER {m['wer']:6.2f} chrF {m['chrf']:6.2f} BLEU-4 {m['bleu4']:6.2f} "
                  f"cap {m['cap_hit_rate']:.3f} EOS {m['eos_rate']:.3f} trunc {m['truncation_rate_no_terminal_punct']:.3f} "
                  f"rep {m['repetition_rate']:.3f} words med/max {m['pred_words']['median']:.0f}/{m['pred_words']['max']:.0f} "
                  f"len-ratio {m['length_ratio_corpus']:.3f}")
    print(json.dumps(out['change_diagnostics'], indent=1))


if __name__ == '__main__':
    main()
