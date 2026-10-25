# R100 reproducibility gate: compare the new max_new_tokens=100 run against the committed P0-12 A_official predictions.
# Runs on the VM right after R100 (called by runner/run_decode_length.sh) or locally. Stdlib only, plus the official
# Uni-Sign SLRT_metrics.sableu (--unisign) or sacrebleu 2.x for corpus BLEU-4 / chrF.
#
# Verdicts (fixed before any R100 output exists):
#   REPRODUCED_EXACT : 128/128 prediction lines byte-identical to the committed file              -> proceed
#   REPRODUCED_CLOSE : same 128 clips in the same order, <= 4 lines differ, |dBLEU-4| <= 0.10,
#                      |dchrF| <= 0.20 (corpus, vs committed)                                       -> proceed; R100 (not the
#                      committed file) is the paired baseline for R150 / R256, and the differing clips are reported
#   NOT_REPRODUCED   : anything else, or any structural / diagnostic check failing                  -> stop and diagnose
# Exit code 0 only when proceed is true.
import argparse, hashlib, json, re, sys

BASELINE_SHA = 'd865008bc0a16ba0fb3bceb6f78f5a7153febe1d69ba756cc83f918d57300e4a'
COMMITTED_BLEU4 = 9.131944073379477  # p0_12_full128_fp16_results.csv, A_official
MAX_DIFF_LINES, TOL_BLEU4, TOL_CHRF = 4, 0.10, 0.20
LINE_RE = re.compile(r'^sample: (.*?), (prediction|ground-truth): (.*)$')

ap = argparse.ArgumentParser()
ap.add_argument('--baseline', required=True, help='committed asl-p0-12-full128-fp16/predictions/A_official.txt')
ap.add_argument('--run', required=True, help='R100 output dir (test_tmp_pres.txt, test_tmp_refs.txt, test_decode_diag.jsonl)')
ap.add_argument('--unisign', help='Uni-Sign worktree, for the official SLRT_metrics.sableu')
ap.add_argument('--out', required=True)
a = ap.parse_args()


def parse(path):
    rows = []
    for line in open(path, encoding='utf-8'):
        m = LINE_RE.match(line.rstrip('\n'))
        rows.append((m.group(1), m.group(3)) if m else (None, line))
    return rows


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


fail, R = [], {}
R['baseline_sha256'] = sha(a.baseline)
if R['baseline_sha256'] != BASELINE_SHA: fail.append('committed baseline file changed / wrong file')
base, new = parse(a.baseline), parse(f'{a.run}/test_tmp_pres.txt')
refs = parse(f'{a.run}/test_tmp_refs.txt')
diag = [json.loads(l) for l in open(f'{a.run}/test_decode_diag.jsonl')]
R['candidate_sha256'] = sha(f'{a.run}/test_tmp_pres.txt')

# structure
R['n_lines'] = {'baseline': len(base), 'candidate': len(new), 'refs': len(refs), 'diag': len(diag)}
if any(n != 128 for n in R['n_lines'].values()): fail.append(f"line counts {R['n_lines']}")
if any(c is None for c, _ in new): fail.append('unparseable candidate lines')
R['same_clip_order'] = [c for c, _ in base] == [c for c, _ in new] == [c for c, _ in refs] == [d['sample'] for d in diag]
if not R['same_clip_order']: fail.append('clip order differs between baseline / candidate / refs / diag')

# diagnostics sanity: R100 settings, decoder start token, internal consistency
R['diag_checks'] = {
    'all_max_new_tokens_100': all(d['max_new_tokens'] == 100 for d in diag),
    'all_first_id_decoder_start_0': all(d['first_id'] == 0 for d in diag),
    'n_new_tokens_le_100': all(d['n_new_tokens'] <= 100 for d in diag),
    'hit_cap_iff_no_eos_and_100_tokens': all(d['hit_cap'] == ((not d['eos']) and d['n_gen_tokens'] == 100) for d in diag),
    'pred_words_match_text': all(d['pred_words'] == len(p.split()) for d, (_, p) in zip(diag, new)),
    'max_seq_len_le_150 (padding safeguard is a no-op)': max(d['seq_len'] for d in diag) <= 150,
}
for k, v in R['diag_checks'].items():
    if not v: fail.append(f'diag check failed: {k}')
R['cap_hits'] = sum(d['hit_cap'] for d in diag); R['eos_rate'] = sum(d['eos'] for d in diag) / max(len(diag), 1)

# identity
diff = [i for i, (b, n) in enumerate(zip(base, new)) if b != n]
R['identical_lines'] = 128 - len(diff) if len(base) == len(new) == 128 else None
R['differing'] = [{'idx': i, 'clip': base[i][0], 'committed': base[i][1], 'r100': new[i][1]} for i in diff]

# corpus metrics vs committed (references from the run's own refs file == labels.test_p012_128)
H0, H1, RR = [p for _, p in base], [p for _, p in new], [r for _, r in refs]
try:
    if a.unisign:
        sys.path.insert(0, a.unisign)
        from SLRT_metrics import sableu
        b4 = lambda H: sableu(references=RR, hypotheses=H, tokenizer='13a')['bleu4']; R['bleu_impl'] = 'SLRT_metrics.sableu'
    else:
        raise ImportError
except Exception:
    from sacrebleu.metrics import BLEU
    b4 = lambda H: BLEU(max_ngram_order=4, tokenize='13a').corpus_score(H, [RR]).score; R['bleu_impl'] = 'sacrebleu 2.x 13a'
R['bleu4'] = {'committed_csv': COMMITTED_BLEU4, 'committed_file_rescored': b4(H0), 'r100': b4(H1)}
R['bleu4']['delta_r100_minus_committed'] = R['bleu4']['r100'] - R['bleu4']['committed_file_rescored']
try:
    from sacrebleu.metrics import CHRF
    c = CHRF(); R['chrf'] = {'committed': c.corpus_score(H0, [RR]).score, 'r100': c.corpus_score(H1, [RR]).score}
    R['chrf']['delta'] = R['chrf']['r100'] - R['chrf']['committed']
except ImportError:
    R['chrf'] = None  # CLOSE cannot be granted without chrF; EXACT still can

# verdict
if fail:
    verdict = 'NOT_REPRODUCED'
elif not diff:
    verdict = 'REPRODUCED_EXACT'
elif (len(diff) <= MAX_DIFF_LINES and abs(R['bleu4']['delta_r100_minus_committed']) <= TOL_BLEU4
      and R['chrf'] is not None and abs(R['chrf']['delta']) <= TOL_CHRF):
    verdict = 'REPRODUCED_CLOSE'
else:
    verdict = 'NOT_REPRODUCED'
R.update(verdict=verdict, proceed=verdict != 'NOT_REPRODUCED', hard_failures=fail,
         thresholds={'max_differing_lines': MAX_DIFF_LINES, 'abs_delta_bleu4': TOL_BLEU4, 'abs_delta_chrf': TOL_CHRF})
json.dump(R, open(a.out, 'w'), indent=1, ensure_ascii=False)
print(f"identical {R['identical_lines']}/128 | BLEU-4 committed {R['bleu4']['committed_file_rescored']:.4f} "
      f"r100 {R['bleu4']['r100']:.4f} ({R['bleu4']['delta_r100_minus_committed']:+.4f}) [{R['bleu_impl']}] | "
      f"cap hits {R['cap_hits']} | EOS {R['eos_rate']:.3f} | {verdict}" + (f" | failures: {fail}" if fail else ''))
sys.exit(0 if R['proceed'] else 1)
