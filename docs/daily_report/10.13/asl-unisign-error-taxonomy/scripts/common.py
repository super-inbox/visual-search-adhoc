# Shared paths, loaders and metrics for the Uni-Sign error-taxonomy analysis (P0-12 T4/fp16 predictions, frozen 128 clips).
# Metrics:
#   corpus BLEU-1..4 : sacrebleu 2.x, tokenize 13a, cumulative BLEU-n (max_ngram_order=n), same definition as the
#                      vendored sacrebleu 1.4.2 in Uni-Sign SLRT_metrics.sableu (not available on this machine).
#   ROUGE            : pltrdy `rouge==1.0.1` Rouge().get_scores(avg=True)['rouge-l']['f'] x100, case kept -- the package the
#                      Uni-Sign How2Sign eval installs (run_p012_gpu.sh). Not in the conda env: put it on PYTHONPATH
#                      (e.g. `pip install --target <dir> rouge==1.0.1; PYTHONPATH=<dir> python ...`). Corpus-level only.
#   References       : canonical = manifest.csv reference_text (encoding-fixed; identical to the refs score_conditions.py
#                      used). labels.test_p012_128 has 3 mojibake apostrophes (UTF-8 bytes of U+2019 read as latin-1); kept verbatim as
#                      reference_labels_test. Corpus BLEU is identical under both (checked in verify_predictions.py).
#   sentence BLEU    : sacrebleu.sentence_bleu (13a, exp smoothing, effective order) -- per-sample only.
#   chrF             : sacrebleu chrF (default char order 6, beta 2), corpus and sentence.
#   WER (p012)       : lowercase whitespace tokens, punctuation kept -- identical to score_conditions.py.
#   WER (norm)       : lowercase, punctuation stripped -- used for the edit-operation (omission/substitution/insertion) split.
import os, re, csv, json, gzip, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
P012_PRED = os.path.join(ROOT, 'docs/daily_report/10.13/asl-p0-12-full128-fp16/predictions')
P012_CSV = os.path.join(ROOT, 'docs/daily_report/10.13/asl-p0-12-full128-fp16/p0_12_full128_fp16_results.csv')
GAP = os.path.join(ROOT, 'docs/daily_report/10.06/asl-p0-12-unisign-pose-gap')
LABELS = os.path.join(GAP, 'artifacts/prepared_inputs/labels.test_p012_128')
POSE_DIRS = {c: os.path.join(GAP, 'artifacts/prepared_inputs', c, 'test-pose-rtmpose-192')
             for c in ('A_official', 'B_ours_5p39', 'B_aspect', 'C_ours_on_official_crop')}
POSE_DIAG = os.path.join(GAP, 'pose_diagnostics.csv')
POSE_AGG = os.path.join(GAP, 'data/pose_diagnostics_aggregate.json')
SEG_ALIGN = os.path.join(GAP, 'data/segment_alignment_128.json')
MANIFEST = os.path.join(ROOT, 'asl-translator/data/public_benchmarks/how2sign_v2/manifest.csv')

SYSTEMS = ['A_official', 'C_ours_on_official_crop', 'B_ours_5p39', 'B_aspect']  # primary, paired diagnostic, controls
PRIMARY, PAIRED = 'A_official', 'C_ours_on_official_crop'

sys.path.insert(0, os.path.join(GAP, 'scripts'))
import safe_pickle  # noqa: E402  (allow-listed unpickler: numpy arrays / builtins only)

LINE_RE = re.compile(r'^sample: (.*?), prediction: (.*)$')


def load_labels():
    """labels.test_p012_128 in file order: list of (clip_id, raw labels.test text)."""
    with gzip.open(LABELS, 'rb') as f:
        d = safe_pickle.SafeUnpickler(f).load()
    return [(k.replace('.mp4', ''), v['text']) for k, v in d.items()]


def fix_mojibake(s):
    try:
        return s.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def load_refs():
    """Canonical references keyed by clip_id: manifest reference_text (== refs used by the committed scorer)."""
    return {r['how2sign_id']: r['reference_text'] for r in load_manifest()}


def load_manifest():
    return list(csv.DictReader(open(MANIFEST, encoding='utf-8')))


def load_pred_lines(system):
    """Return the raw parse of a prediction file: list of (lineno, clip_id or None, prediction or None, raw line)."""
    out = []
    with open(os.path.join(P012_PRED, system + '.txt'), encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            raw = line.rstrip('\n')
            m = LINE_RE.match(raw)
            out.append((i, m.group(1).replace('.mp4', '') if m else None, m.group(2) if m else None, raw))
    return out


def load_preds(system):
    return {cid: p for _, cid, p, _ in load_pred_lines(system) if cid is not None}


# ---------------- metrics ----------------
import sacrebleu  # noqa: E402
from sacrebleu.metrics import BLEU, CHRF  # noqa: E402

_CHRF = CHRF()


def corpus_bleu_n(hyps, refs):
    return {f'bleu{n}': BLEU(max_ngram_order=n, tokenize='13a').corpus_score(hyps, [refs]).score for n in range(1, 5)}


def corpus_chrf(hyps, refs):
    return _CHRF.corpus_score(hyps, [refs]).score


def sentence_bleu(h, r):
    return sacrebleu.sentence_bleu(h, [r]).score


def sentence_chrf(h, r):
    return _CHRF.sentence_score(h, [r]).score


def corpus_rouge(hyps, refs):
    try:
        from rouge import Rouge
    except ImportError as e:
        raise SystemExit('corpus ROUGE needs pltrdy rouge==1.0.1 on PYTHONPATH (see header of common.py)') from e
    return 100 * Rouge().get_scores(hyps, refs, avg=True)['rouge-l']['f']


def norm_tokens(s):
    s = s.lower().replace('’', "'")
    s = re.sub(r"[^\w\s'/.-]", ' ', s)          # keep apostrophes, fractions, decimals, hyphens inside words
    s = re.sub(r"(?<!\w)[.'/-]|[.'/-](?!\w)", ' ', s)  # strip them when not word-internal
    return s.split()


def align(h, r):
    """Levenshtein alignment of token lists; returns (S, D, I, ops) where ops = list of (op, ref_tok, hyp_tok)."""
    n, m = len(r), len(h)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): d[i][0] = i
    for j in range(m + 1): d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (r[i - 1] != h[j - 1]))
    i, j, ops = n, m, []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + (r[i - 1] != h[j - 1]):
            ops.append(('C' if r[i - 1] == h[j - 1] else 'S', r[i - 1], h[j - 1])); i -= 1; j -= 1
        elif i > 0 and d[i][j] == d[i - 1][j] + 1:
            ops.append(('D', r[i - 1], None)); i -= 1
        else:
            ops.append(('I', None, h[j - 1])); j -= 1
    ops.reverse()
    S = sum(o[0] == 'S' for o in ops); D = sum(o[0] == 'D' for o in ops); I = sum(o[0] == 'I' for o in ops)
    return S, D, I, ops


def wer_p012(h, r):
    """Edit distance / ref length on lowercase whitespace tokens (score_conditions.py definition). Returns (edits, n_ref)."""
    S, D, I, _ = align(h.lower().split(), r.lower().split())
    return S + D + I, len(r.split())


def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0].keys())
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader(); w.writerows(rows)


def read_jsonl(path):
    return [json.loads(l) for l in open(path, encoding='utf-8')]


def write_jsonl(path, rows):
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
