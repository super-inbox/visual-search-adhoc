# Step 2: automated FIRST-PASS error taxonomy over inputs_128.jsonl.
# Everything produced here is an AUTOMATIC weak label. Linguistic categories are *_candidate (reference-text heuristics);
# visual categories are pose-derived proxies. Nothing here has been manually reviewed.
# Outputs (in ..):
#   error_taxonomy_annotations.jsonl  per clip: weak labels + evidence, per-system error analysis (all 4 systems)
#   failure_matrix.csv                per (category, system): metrics, error-type rates, matched-control and paired deltas
#   manual_review_queue.csv           40 clips, stratified, review_status=PENDING (no review performed)
#   representative_failures.md        auto-selected examples per error type / category (A_official vs C)
#   taxonomy_summary.json             numbers cited in ERROR_ANALYSIS_REPORT.md
# Roles: A_official = primary system; C_ours_on_official_crop = paired diagnostic (same frames/crop/timing, our poses);
#        B_ours_5p39 / B_aspect = preprocessing controls (not a taxonomy baseline).
import os, sys, re, json, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

ANALYSIS_STATUS = 'automated first-pass / weak-label analysis; manual ASL review pending'
SEED, N_BOOT, EXPLORATORY_N = 12345, 10000, 10
N_TESTED_CATEGORIES = 16  # primary non-ALL categories -> Bonferroni alpha = 0.05 / 16 (secondary sensitivity rows excluded)
BROAD_NUMBER = 'number_candidate_broad_sensitivity'  # SECONDARY: strict numbers + ambiguous one/first/second
ALPHA_BONF = 0.05 / N_TESTED_CATEGORIES
ROLE = {'A_official': 'primary', 'C_ours_on_official_crop': 'paired_diagnostic',
        'B_ours_5p39': 'preprocessing_control', 'B_aspect': 'preprocessing_control'}

# ---------------- lexical resources (fixed before looking at scores) ----------------
STOP = set("""a an the and or but if then so because as of at by for with about against between into through during before after
above below to from up down in out on off over under again further once here there when where why how all any both each few more
most other some such only own same than too very s t can will just don should now i me my myself we our ours you your yours he him
his she her it its they them their what which who whom this that these those am is are was were be been being have has had having
do does did doing would could should might must shall may i'm you're it's that's there's we're they're i'll you'll we'll i've
you've we've i'd let's going go get got gonna wanna kind sort like really thing things way well also lot just okay ok yeah oh
want make take put see look know think say said come one ones""".split())
NEG_WORDS = {'not', 'no', 'never', 'nothing', 'nobody', 'none', 'nowhere', 'neither', 'nor', 'cannot'}
NUM_WORDS = {w: i for i, w in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen '
                                        'fifteen sixteen seventeen eighteen nineteen twenty'.split())}
NUM_WORDS.update({'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
                  'hundred': 100, 'thousand': 1000, 'million': 10 ** 6, 'billion': 10 ** 9, 'dozen': 12})
NUM_WORDS.update({w: i for i, w in enumerate('third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth thirteenth '
                                             'fourteenth fifteenth sixteenth seventeenth eighteenth nineteenth twentieth'.split(), 3)})
# 'one' (pronoun: "this one") and 'first' / 'second' (discourse / time unit) are too ambiguous to *assign* the number category
NUM_AMBIGUOUS = {'one', 'first', 'second'}
AMBIG_VALUES = {'one': '1', 'first': '1', 'second': '2'}  # broad sensitivity analysis only
CAP_STOPLIST = {'I', "I'm", 'I’m', "I'll", "I've", "I'd", 'OK', 'Okay'}
# capitalised words that usually have a lexical ASL sign (not fingerspelled): stay named_entity_candidate, not fingerspelling
LEXICAL_SIGN_LIKELY = set("""monday tuesday wednesday thursday friday saturday sunday january february march april may june july
august september october november december christmas easter thanksgiving halloween english spanish french german italian chinese
japanese european american america mexican god""".split())
DICT_LOWER, PROPERNAMES = set(), set()
if os.path.exists('/usr/share/dict/words'):
    DICT_LOWER = {w.strip() for w in open('/usr/share/dict/words') if w.strip() and w.strip().islower()}
if os.path.exists('/usr/share/dict/propernames'):
    PROPERNAMES = {w.strip().lower() for w in open('/usr/share/dict/propernames') if w.strip()}

TOK_RE = re.compile(r"(?:[A-Za-z]\.){2,}|[A-Za-z][A-Za-z'’\-&]*|\d[\d,./:]*")  # dotted initialism | word | numeral


def sentences(text):
    return [s for s in re.split(r'(?<=[.!?:;"])\s+', text) if s.strip()]


def strip_tok(t):
    return t.rstrip('.,;:!?"\'’)')


# ---------------- reference-side weak labels ----------------
def ref_labels(ref):
    fs_ev, ne_ev, num_ev, neg_ev, amb_ev = [], [], [], [], []
    for sent in sentences(ref):
        toks = [strip_tok(t) for t in TOK_RE.findall(sent)]
        for k, t in enumerate(toks):
            if not t:
                continue
            low = t.lower().replace('’', "'")
            if re.fullmatch(r'\d[\d,./:]*', t) or low in NUM_WORDS and low not in NUM_AMBIGUOUS:
                num_ev.append(t)
            elif low in NUM_AMBIGUOUS:
                amb_ev.append(t)
            if low in NEG_WORDS or low.endswith("n't"):
                neg_ev.append(t)
            if t in CAP_STOPLIST:
                continue
            if re.fullmatch(r'(?:[A-Z]\.){2,}|[A-Z]{2,}s?', t):                       # acronym / initialism / all caps
                fs_ev.append((t, 'acronym_or_all_caps')); ne_ev.append(t); continue
            if re.fullmatch(r'(?:[A-Za-z]-){2,}[A-Za-z]', t):                          # letter-hyphen spelling
                fs_ev.append((t, 'hyphen_spelled_letters')); continue
            if k > 0 and re.fullmatch(r'[A-Z]', t):                                   # isolated capital letter
                fs_ev.append((t, 'single_capital_letter')); continue
            if k > 0 and t[0].isupper():                                              # non-initial capitalised word
                ne_ev.append(t)
                parts = [p for p in re.split(r"[-']", low) if p]
                if low in LEXICAL_SIGN_LIKELY:
                    continue
                if re.search(r'[a-z][A-Z]', t):
                    fs_ev.append((t, 'camelcase_name'))
                elif low in PROPERNAMES:
                    fs_ev.append((t, 'personal_name_list'))
                elif not all(p in DICT_LOWER for p in parts):
                    fs_ev.append((t, 'capitalised_not_in_lowercase_dictionary'))
    return {
        'fingerspelling_candidate': {'value': bool(fs_ev), 'evidence': [f'{a} [{b}]' for a, b in fs_ev]},
        'named_entity_candidate': {'value': bool(ne_ev), 'evidence': ne_ev},
        'number_candidate': {'value': bool(num_ev), 'evidence': num_ev},
        BROAD_NUMBER: {'value': bool(num_ev or amb_ev), 'evidence': num_ev + [f'{t} [ambiguous]' for t in amb_ev],
                       'note': 'SECONDARY sensitivity label; primary analysis uses number_candidate (strict)'},
        'negation_candidate': {'value': bool(neg_ev), 'evidence': neg_ev},
        'question_candidate': {'value': '?' in ref, 'evidence': ['?'] if '?' in ref else []},
    }


def num_values(text):
    vals = []
    for t in C.norm_tokens(text):
        t2 = t.replace(',', '')
        if t2 in NUM_WORDS:
            vals.append(str(NUM_WORDS[t2]))
        elif re.fullmatch(r'\d+(?:[./:]\d+)?', t2):
            vals.append(t2)
    return vals


def content(tokens):
    out = []
    for t in tokens:
        t = t.replace("'s", '')
        if t in STOP or t in NEG_WORDS or len(t) < 2 or re.fullmatch(r'\W+', t):
            continue
        out.append(t[:-1] if len(t) > 3 and t.endswith('s') and not t.endswith('ss') else t)
    return out


def has_rep3(s):
    w = s.lower().split(); g = [tuple(w[k:k + 3]) for k in range(len(w) - 2)]
    return len(g) > 0 and len(set(g)) < len(g)


def rep3_ratio(s):
    w = s.lower().split(); g = [tuple(w[k:k + 3]) for k in range(len(w) - 2)]
    return 0.0 if not g else 1 - len(set(g)) / len(g)


# ---------------- per-system error analysis ----------------
ERR_FLAGS = ['omission', 'over_generation', 'hallucination_candidate', 'repetition', 'truncation_candidate', 'substitution_dominant']
PRIMARY_ORDER = ['repetition_loop', 'omission', 'hallucination', 'over_generation', 'substitution']


def analyse(pred, ref, labels, m):
    ht, rt = C.norm_tokens(pred), C.norm_tokens(ref)
    hc, rc = content(ht), content(rt)
    rcs = set(rc)
    cp = sum(t in rcs for t in hc) / len(hc) if hc else 0.0
    cr = len(rcs & set(hc)) / len(rcs) if rcs else float('nan')
    lr = len(ht) / max(len(rt), 1)
    S, D, I = m['sub'], m['del'], m['ins']
    rep = has_rep3(pred) and not has_rep3(ref)
    flags = {
        'omission': lr < 0.6,                                    # prediction < 60% of reference length
        'over_generation': lr > 1.6,
        'hallucination_candidate': cp < 0.2,                     # >80% of predicted content words unsupported by the ref
        'repetition': rep,                                       # repeated word 3-gram in pred, none in ref
        'truncation_candidate': pred.rstrip()[-1:] not in '.?!"',  # no terminal punctuation (likely max_new_tokens cut)
        'substitution_dominant': S >= max(D, I) and S > 0,
    }
    if rep and rep3_ratio(pred) >= 0.15:
        primary = 'repetition_loop'
    elif flags['omission']:
        primary = 'omission'
    elif flags['hallucination_candidate']:
        primary = 'hallucination'
    elif flags['over_generation']:
        primary = 'over_generation'
    else:
        primary = 'substitution'
    out = {'primary_error_type': primary, 'error_flags': flags,
           'length_ratio': round(lr, 3), 'content_precision': round(cp, 3),
           'content_recall': None if cr != cr else round(cr, 3), 'rep3_ratio': round(rep3_ratio(pred), 3),
           'category_checks': {}}
    pv = num_values(pred)
    if labels['number_candidate']['value']:
        rv = num_values(ref)
        rv = [v for v in rv if v != '1'] or rv
        out['category_checks']['number_recall'] = round(sum(v in pv for v in rv) / len(rv), 3) if rv else None
    else:
        out['category_checks']['number_inserted'] = any(v != '1' for v in pv)
    if labels[BROAD_NUMBER]['value']:
        def vals_broad(text):
            return num_values(text) + [AMBIG_VALUES[t] for t in C.norm_tokens(text) if t in AMBIG_VALUES]
        rb, pb = vals_broad(ref), vals_broad(pred)
        out['category_checks']['number_recall_broad'] = round(sum(v in pb for v in rb) / len(rb), 3) if rb else None
    pneg = any(t in NEG_WORDS or t.endswith("n't") for t in ht)
    if labels['negation_candidate']['value']:
        out['category_checks']['negation_dropped'] = not pneg
    else:
        out['category_checks']['negation_inserted'] = pneg
    if labels['question_candidate']['value']:
        out['category_checks']['question_mark_lost'] = '?' not in pred
    else:
        out['category_checks']['question_mark_inserted'] = '?' in pred
    hset = set(ht)
    for cat, key in (('named_entity_candidate', 'named_entity_recall'), ('fingerspelling_candidate', 'fingerspelling_recall')):
        if labels[cat]['value']:
            toks = {strip_tok(e.split(' [')[0]).lower().replace('’', "'") for e in labels[cat]['evidence']}
            out['category_checks'][key] = round(sum(t in hset for t in toks) / len(toks), 3)
    return out


# ---------------- statistics ----------------
rng = np.random.default_rng(SEED)


def _ci(b, alpha=0.05):
    return (round(float(np.percentile(b, 100 * alpha / 2)), 2), round(float(np.percentile(b, 100 * (1 - alpha / 2))), 2))


def boot_mean(x):
    x = np.asarray(x, float)
    return x[rng.integers(0, len(x), (N_BOOT, len(x)))].mean(1) if len(x) >= 2 else None


def boot_mean_ci(x, alpha=0.05):
    b = boot_mean(x)
    return (float('nan'), float('nan')) if b is None else _ci(b, alpha)


def boot_diff(x, y):
    bx, by = boot_mean(x), boot_mean(y)
    return None if bx is None or by is None else bx - by


def excludes_zero(ci):
    return bool(ci[0] > 0 or ci[1] < 0)


def matched_controls(rows, in_cat):
    """Nearest non-category clip per category clip on reference word count (tie-break duration), with replacement."""
    pool = [r for r, f in zip(rows, in_cat) if not f]
    pairs = []
    for r, f in zip(rows, in_cat):
        if f:
            best = min(pool, key=lambda p: (abs(p['reference_n_words'] - r['reference_n_words']), abs(p['duration_s'] - r['duration_s']), p['idx']))
            pairs.append((r, best))
    return pairs


def corpus_block(rows, s):
    H = [r['predictions'][s] for r in rows]; R = [r['reference'] for r in rows]
    e = sum(r['metrics'][s]['wer_edits'] for r in rows); n = sum(r['metrics'][s]['wer_ref_words'] for r in rows)
    return {'corpus_bleu4': round(C.corpus_bleu_n(H, R)['bleu4'], 2), 'corpus_chrf': round(C.corpus_chrf(H, R), 2),
            'pooled_wer': round(e / n, 4),
            'mean_chrf': round(float(np.mean([r['metrics'][s]['chrf'] for r in rows])), 2),
            'median_chrf': round(float(np.median([r['metrics'][s]['chrf'] for r in rows])), 2),
            'mean_sentence_bleu': round(float(np.mean([r['metrics'][s]['sentence_bleu'] for r in rows])), 2),
            'mean_wer': round(float(np.mean([r['metrics'][s]['wer'] for r in rows])), 4)}


def main():
    rows = C.read_jsonl(os.path.join(C.OUT, 'inputs_128.jsonl'))
    n = len(rows)
    A, Cn = C.PRIMARY, C.PAIRED

    # ---- visual flags: fixed rules, computed per pose source; clip-level categories use the A_official poses ----
    def q(vals, p): return float(np.percentile(vals, p))
    vis_thr = {}
    for s in (A, Cn):
        P = [r['pose'][s] for r in rows]
        vis_thr[s] = {
            'low_hand_conf_q25': q([min(p['left_mean_conf'], p['right_mean_conf']) for p in P], 25),
            'fast_hand_motion_q75': q([max(p['left_wrist_speed_median_sw_per_frame'], p['right_wrist_speed_median_sw_per_frame']) for p in P], 75),
            'high_hand_jitter_q75': q([max(p['left_hand_jitter_model_units'], p['right_hand_jitter_model_units']) for p in P], 75),
        }
    agree_thr = q([max(r['pose_agreement_A_vs_C']['left_err_over_shoulder_median'], r['pose_agreement_A_vs_C']['right_err_over_shoulder_median']) for r in rows], 75)

    def vis_flags(p, t):
        return {
            'long_clip_gt_256_frames': {'value': bool(p['frames_gt_256']), 'evidence': f"{int(p['frames'])} frames (Uni-Sign randomly subsamples >256)"},
            'hand_out_of_frame_candidate': {'value': max(p['left_hand_half_out_of_frame_rate'], p['right_hand_half_out_of_frame_rate']) >= 0.05,
                                            'evidence': f"half-out-of-frame rate L={p['left_hand_half_out_of_frame_rate']} R={p['right_hand_half_out_of_frame_rate']} (rule >=0.05)"},
            'low_hand_conf_candidate': {'value': min(p['left_mean_conf'], p['right_mean_conf']) <= t['low_hand_conf_q25'],
                                        'evidence': f"min hand mean conf {min(p['left_mean_conf'], p['right_mean_conf']):.3f} (rule <= q25 {t['low_hand_conf_q25']:.3f})"},
            'hand_near_face_candidate': {'value': max(p['left_wrist_near_face_rate'], p['right_wrist_near_face_rate']) >= 0.05,
                                         'evidence': f"wrist<0.5 shoulder-width from nose: L={p['left_wrist_near_face_rate']} R={p['right_wrist_near_face_rate']} (rule >=0.05)"},
            'fast_hand_motion_candidate': {'value': max(p['left_wrist_speed_median_sw_per_frame'], p['right_wrist_speed_median_sw_per_frame']) >= t['fast_hand_motion_q75'],
                                           'evidence': f"max median wrist speed {max(p['left_wrist_speed_median_sw_per_frame'], p['right_wrist_speed_median_sw_per_frame']):.4f} sw/frame (rule >= q75 {t['fast_hand_motion_q75']:.4f})"},
            'high_hand_jitter_candidate': {'value': max(p['left_hand_jitter_model_units'], p['right_hand_jitter_model_units']) >= t['high_hand_jitter_q75'],
                                           'evidence': f"max hand jitter {max(p['left_hand_jitter_model_units'], p['right_hand_jitter_model_units']):.4f} (rule >= q75 {t['high_hand_jitter_q75']:.4f})"},
        }

    ann = []
    for r in rows:
        lab = ref_labels(r['reference'])
        lab['fast_signing_text_proxy'] = {'value': r['manifest_heuristics']['heuristic_fast_signing_wps_ge_p90'].startswith('yes'),
                                          'evidence': f"reference words/sec {r['words_per_second']} (manifest heuristic, text-derived)"}
        vA = vis_flags(r['pose'][A], vis_thr[A]); vC = vis_flags(r['pose'][Cn], vis_thr[Cn])
        lab.update(vA)
        ag = r['pose_agreement_A_vs_C']
        lab['high_pose_disagreement_A_vs_C'] = {'value': max(ag['left_err_over_shoulder_median'], ag['right_err_over_shoulder_median']) >= agree_thr,
                                                'evidence': f"hand keypoint err/shoulder L={ag['left_err_over_shoulder_median']} R={ag['right_err_over_shoulder_median']} (rule >= q75 {agree_thr:.4f})"}
        for k, v in lab.items():
            v['label_source'] = 'automatic'
            v['status'] = 'candidate_unverified'
        r['_labels'] = lab
        sysan = {}
        for s in C.SYSTEMS:
            a = analyse(r['predictions'][s], r['reference'], lab, r['metrics'][s])
            a['role'] = ROLE[s]
            a['metrics'] = r['metrics'][s]
            sysan[s] = a
        r['_an'] = sysan
        ann.append({'clip_id': r['clip_id'], 'idx': r['idx'], 'reference': r['reference'],
                    'predictions': r['predictions'], 'weak_labels': lab,
                    'visual_flags_from_C_poses': {k: v['value'] for k, v in vC.items()},
                    'manifest_heuristics': r['manifest_heuristics'],
                    'system_analysis': sysan,
                    'annotation_meta': {'pass': 'automatic_first_pass', 'analysis_status': ANALYSIS_STATUS, 'manual_review': 'NOT PERFORMED',
                                        'note': 'fingerspelling/named-entity labels are reference-text candidates, not verified ASL behaviour'}})
    C.write_jsonl(os.path.join(C.OUT, 'error_taxonomy_annotations.jsonl'), ann)

    # ---- category definitions ----
    LING = ['fingerspelling_candidate', 'named_entity_candidate', 'number_candidate', 'negation_candidate', 'question_candidate']
    VIS = ['long_clip_gt_256_frames', 'hand_out_of_frame_candidate', 'low_hand_conf_candidate', 'hand_near_face_candidate',
           'fast_hand_motion_candidate', 'high_hand_jitter_candidate', 'fast_signing_text_proxy', 'high_pose_disagreement_A_vs_C']
    cats = {'ALL': [True] * n}
    for c in LING + VIS:
        cats[c] = [r['_labels'][c]['value'] for r in rows]
    nw = [r['reference_n_words'] for r in rows]
    t1, t2 = np.percentile(nw, [33.3, 66.7])
    cats['ref_length_short'] = [x <= t1 for x in nw]
    cats['ref_length_long'] = [x > t2 for x in nw]
    cats['no_linguistic_candidate'] = [not any(r['_labels'][c]['value'] for c in LING) for r in rows]
    cats[BROAD_NUMBER] = [r['_labels'][BROAD_NUMBER]['value'] for r in rows]  # last: keeps the primary rows' bootstrap draws unchanged
    group = {c: ('all' if c == 'ALL' else 'sensitivity_secondary' if c == BROAD_NUMBER else 'linguistic' if c in LING or c == 'no_linguistic_candidate' else 'length' if c.startswith('ref_length') else 'visual') for c in cats}

    # ---- failure matrix ----
    fm, summary = [], {'analysis_status': ANALYSIS_STATUS, 'n': n, 'thresholds': {'visual': vis_thr, 'pose_disagreement_q75': agree_thr, 'ref_len_terciles': [t1, t2]},
                       'categories': {}}
    dAC = np.array([r['metrics'][A]['chrf'] - r['metrics'][Cn]['chrf'] for r in rows])
    for c, mask in cats.items():
        idx = [i for i, f in enumerate(mask) if f]
        sub = [rows[i] for i in idx]
        k = len(sub)
        if k == 0:
            summary['categories'][c] = {'n': 0}
            continue
        csum = {'n': k, 'group': group[c], 'exploratory_n_lt_10': k < EXPLORATORY_N}
        pairs = matched_controls(rows, mask) if c != 'ALL' and k < n else []
        for s in C.SYSTEMS:
            row = {'category': c, 'category_group': group[c], 'system': s, 'system_role': ROLE[s], 'n': k,
                   'exploratory_n_lt_10': k < EXPLORATORY_N}
            row.update(corpus_block(sub, s))
            ch = [r['metrics'][s]['chrf'] for r in sub]
            row['mean_chrf_ci95'] = boot_mean_ci(ch)
            for f in ERR_FLAGS:
                row[f'rate_{f}'] = round(float(np.mean([r['_an'][s]['error_flags'][f] for r in sub])), 3)
            for pe in PRIMARY_ORDER:
                row[f'primary_{pe}'] = sum(r['_an'][s]['primary_error_type'] == pe for r in sub)
            row['analysis_status'] = ANALYSIS_STATUS
            for key in ('number_recall', 'number_recall_broad', 'negation_dropped', 'question_mark_lost', 'named_entity_recall', 'fingerspelling_recall'):
                v = [r['_an'][s]['category_checks'].get(key) for r in sub]
                v = [float(x) for x in v if x is not None]
                row[f'check_{key}'] = round(float(np.mean(v)), 3) if v else ''
            if pairs:
                dm = [p[0]['metrics'][s]['chrf'] - p[1]['metrics'][s]['chrf'] for p in pairs]
                gap = float(np.mean([abs(p[0]['reference_n_words'] - p[1]['reference_n_words']) for p in pairs]))
                n_uni = len({p[1]['clip_id'] for p in pairs})
                if group[c] == 'length':
                    row['matched_ctrl_quality'] = 'not_applicable: category is defined by the matching variable'
                elif gap > 2 or n_uni < 0.5 * k:
                    row['matched_ctrl_quality'] = 'poor_match: not interpretable (mean ref-word gap > 2 or < 50% unique controls)'
                else:
                    row['matched_ctrl_quality'] = 'ok'
                bm = boot_mean(dm)
                db = [p[0]['metrics'][s]['sentence_bleu'] - p[1]['metrics'][s]['sentence_bleu'] for p in pairs]
                dw = [p[0]['metrics'][s]['wer'] - p[1]['metrics'][s]['wer'] for p in pairs]
                row['matched_ctrl_n_unique_controls'] = n_uni
                row['matched_ctrl_mean_abs_refwords_gap'] = round(gap, 2)
                row['matched_ctrl_delta_chrf'] = round(float(np.mean(dm)), 2)
                row['matched_ctrl_delta_chrf_ci95'] = _ci(bm)
                row['matched_ctrl_delta_chrf_ci_bonferroni'] = _ci(bm, ALPHA_BONF)
                row['matched_ctrl_bonferroni_excludes_0'] = excludes_zero(_ci(bm, ALPHA_BONF)) and row['matched_ctrl_quality'] == 'ok' 
                row['matched_ctrl_delta_sentence_bleu'] = round(float(np.mean(db)), 2)
                row['matched_ctrl_delta_wer'] = round(float(np.mean(dw)), 4)
            if s != A:
                d = [r['metrics'][s]['chrf'] - r['metrics'][A]['chrf'] for r in sub]
                row['paired_delta_chrf_vs_A'] = round(float(np.mean(d)), 2)
                row['paired_delta_chrf_vs_A_ci95'] = boot_mean_ci(d)
                row['paired_delta_bleu4_vs_A'] = round(row['corpus_bleu4'] - corpus_block(sub, A)['corpus_bleu4'], 2)
            if s == Cn and c != 'ALL' and k < n:
                out_d = [dAC[i] for i in range(n) if not mask[i]]
                in_d = [dAC[i] for i in idx]
                row['pose_sensitivity_A_minus_C_chrf_in_cat'] = round(float(np.mean(in_d)), 2)
                row['pose_sensitivity_A_minus_C_chrf_outside'] = round(float(np.mean(out_d)), 2)
                row['pose_sensitivity_interaction'] = round(float(np.mean(in_d) - np.mean(out_d)), 2)
                bi = boot_diff(in_d, out_d)
                row['pose_sensitivity_interaction_ci95'] = _ci(bi)
                row['pose_sensitivity_interaction_ci_bonferroni'] = _ci(bi, ALPHA_BONF)
                row['pose_sensitivity_bonferroni_excludes_0'] = excludes_zero(_ci(bi, ALPHA_BONF))
            fm.append(row)
            csum[s] = {k2: v for k2, v in row.items() if k2 not in ('category', 'category_group', 'system', 'system_role', 'n', 'exploratory_n_lt_10')}
        summary['categories'][c] = csum

    fields = []
    for r in fm:
        for k2 in r:
            if k2 not in fields:
                fields.append(k2)
    for r in fm:
        for k2 in fields:
            v = r.get(k2, '')
            r[k2] = f'[{v[0]}, {v[1]}]' if isinstance(v, tuple) else v
    C.write_csv(os.path.join(C.OUT, 'failure_matrix.csv'), fm, fields)

    # ---- overall error-type distribution + A vs C disagreement ----
    for s in C.SYSTEMS:
        summary.setdefault('primary_error_type_counts', {})[s] = {pe: sum(r['_an'][s]['primary_error_type'] == pe for r in rows) for pe in PRIMARY_ORDER}
        summary.setdefault('error_flag_rates', {})[s] = {f: round(float(np.mean([r['_an'][s]['error_flags'][f] for r in rows])), 3) for f in ERR_FLAGS}
    summary['A_vs_C'] = {'mean_dchrf': round(float(dAC.mean()), 2), 'dchrf_ci95': boot_mean_ci(dAC),
                         'clips_A_better_by_gt5_chrf': int((dAC > 5).sum()), 'clips_C_better_by_gt5_chrf': int((dAC < -5).sum()),
                         'primary_type_agreement': sum(r['_an'][A]['primary_error_type'] == r['_an'][Cn]['primary_error_type'] for r in rows)}
    summary['label_counts'] = {c: int(sum(m)) for c, m in cats.items()}
    summary['manifest_vs_ours_fingerspelling'] = {
        'manifest_yes': sum(r['manifest_heuristics']['heuristic_proper_noun_or_acronym_fingerspelling_candidate'].startswith('yes') for r in rows),
        'ours_yes': sum(cats['fingerspelling_candidate']),
        'both': sum(r['manifest_heuristics']['heuristic_proper_noun_or_acronym_fingerspelling_candidate'].startswith('yes') and r['_labels']['fingerspelling_candidate']['value'] for r in rows)}
    summary['manifest_vs_ours_number'] = {
        'manifest_yes': sum(r['manifest_heuristics']['heuristic_contains_number_token'].startswith('yes') for r in rows),
        'ours_yes': sum(cats['number_candidate']),
        'both': sum(r['manifest_heuristics']['heuristic_contains_number_token'].startswith('yes') and r['_labels']['number_candidate']['value'] for r in rows)}
    summary['long_clip_vs_reference_length'] = long_clip_stratified(rows)
    summary['decoding_cap'] = decoding_cap(rows)
    summary['entity_token_recall_by_evidence_type'] = token_recall(rows)
    summary['bonferroni'] = {'n_tested_categories': N_TESTED_CATEGORIES, 'alpha_per_test': ALPHA_BONF, 'n_boot': N_BOOT, 'seed': SEED}
    json.dump(summary, open(os.path.join(C.OUT, 'taxonomy_summary.json'), 'w'), indent=1, default=lambda o: list(o) if isinstance(o, tuple) else str(o))

    write_review_queue(rows, dAC, cats)
    write_representatives(rows, cats, summary)
    print(json.dumps({'label_counts': summary['label_counts'], 'primary_error_type_counts': summary['primary_error_type_counts'],
                      'A_vs_C': summary['A_vs_C']}, indent=1))


# ---------------- confound checks ----------------
def long_clip_stratified(rows):
    """>256-frame clips vs <=256-frame clips within reference-length bins (frames and ref words are strongly correlated)."""
    A = C.PRIMARY
    fr = np.array([r['pose'][A]['frames'] for r in rows]); nw = np.array([r['reference_n_words'] for r in rows])
    out = {'pearson_frames_vs_ref_words': round(float(np.corrcoef(fr, nw)[0, 1]), 3),
           'max_ref_words_among_le256_clips': int(nw[fr <= 256].max()), 'min_ref_words_among_gt256_clips': int(nw[fr > 256].min()), 'bins': []}
    for lo, hi in [(0, 15), (15, 25), (25, 35), (35, 50), (50, 1000)]:
        m = (nw >= lo) & (nw < hi)
        b = {'ref_words': f'[{lo},{hi})', 'n': int(m.sum())}
        for name, mm in (('gt256', m & (fr > 256)), ('le256', m & (fr <= 256))):
            sub = [r for r, f in zip(rows, mm) if f]
            b[f'n_{name}'] = len(sub)
            for s in (A, C.PAIRED):
                b[f'mean_chrf_{s}_{name}'] = round(float(np.mean([r['metrics'][s]['chrf'] for r in sub])), 2) if sub else None
        out['bins'].append(b)
    return out


def decoding_cap(rows):
    """Truncation proxy vs reference length. Uni-Sign eval decodes with max_new_tokens=100 (run_p012_gpu.sh)."""
    out = {}
    for s in (C.PRIMARY, C.PAIRED):
        hl = np.array([len(r['predictions'][s].split()) for r in rows]); nw = np.array([r['reference_n_words'] for r in rows])
        tr = np.array([r['_an'][s]['error_flags']['truncation_candidate'] for r in rows])
        out[s] = {'max_pred_words': int(hl.max()), 'median_pred_words_truncated': float(np.median(hl[tr])), 'n_truncated': int(tr.sum()),
                  'truncation_rate_ref_ge_35_words': round(float(tr[nw >= 35].mean()), 3), 'n_ref_ge_35_words': int((nw >= 35).sum()),
                  'truncation_rate_ref_lt_35_words': round(float(tr[nw < 35].mean()), 3),
                  'mean_length_ratio_ref_ge_35_words': round(float(np.mean([r['_an'][s]['length_ratio'] for r, x in zip(rows, nw) if x >= 35])), 3)}
    return out


def token_recall(rows):
    """Exact-token recall of fingerspelling-candidate tokens in each prediction, split by the heuristic that fired."""
    out = {}
    for s in (C.PRIMARY, C.PAIRED, 'B_ours_5p39', 'B_aspect'):
        d = {}
        for r in rows:
            hset = set(C.norm_tokens(r['predictions'][s]))
            for e in r['_labels']['fingerspelling_candidate']['evidence']:
                tok, why = e.split(' [')
                d.setdefault(why.rstrip(']'), []).append((strip_tok(tok).lower(), strip_tok(tok).lower() in hset, r['clip_id']))
        out[s] = {why: {'n_tokens': len(v), 'n_recalled': int(sum(x[1] for x in v)), 'recalled': sorted({x[0] for x in v if x[1]})} for why, v in d.items()}
    return out


# ---------------- manual review queue ----------------
def write_review_queue(rows, dAC, cats):
    A, Cn = C.PRIMARY, C.PAIRED
    man = {r['how2sign_id']: r for r in C.load_manifest()}
    picked, reasons = [], {}

    def add(i, why, cap_list, cap):
        if len(cap_list) >= cap:
            return
        cap_list.append(i)
        reasons.setdefault(i, []).append(why)
        if i not in picked:
            picked.append(i)

    order_worst = sorted(range(len(rows)), key=lambda i: rows[i]['metrics'][A]['chrf'])
    strata = [  # (name, candidate indices in priority order, cap)
        ('fingerspelling_candidate: verify fingerspelling actually occurs', [i for i in order_worst if cats['fingerspelling_candidate'][i]], 10),
        ('named_entity_candidate: verify entity + how it is signed', [i for i in order_worst if cats['named_entity_candidate'][i] and not cats['fingerspelling_candidate'][i]], 5),
        ('number_candidate: verify number signing / number error', [i for i in order_worst if cats['number_candidate'][i]], 6),
        ('negation: polarity flip in A_official', [i for i in order_worst if rows[i]['_an'][A]['category_checks'].get('negation_dropped') or rows[i]['_an'][A]['category_checks'].get('negation_inserted')], 4),
        ('question_candidate: verify question form (NMM) / lost question', [i for i in order_worst if cats['question_candidate'][i]], 4),
        ('large A vs C disagreement (pose-source sensitive)', sorted(range(len(rows)), key=lambda i: -abs(dAC[i])), 6),
        ('visual proxy flagged (out-of-frame / near-face / low conf): check video', [i for i in order_worst if cats['hand_out_of_frame_candidate'][i] or cats['hand_near_face_candidate'][i] or cats['low_hand_conf_candidate'][i]], 4),
        ('A_official best clips (sanity: what success looks like)', order_worst[::-1], 2),
    ]
    ranked = {'large A vs C disagreement (pose-source sensitive)', 'A_official best clips (sanity: what success looks like)'}
    for name, cand, cap in strata:
        got = []
        for i in cand:
            if i in picked:
                # categorical strata: annotate genuine membership; ranked strata: only within their own top-cap window
                if (name not in ranked or i in cand[:cap]) and name not in reasons[i]:
                    reasons[i].append(name)
                continue
            add(i, name, got, cap)
    rnd = random.Random(SEED)
    plain = [i for i in range(len(rows)) if cats['no_linguistic_candidate'][i] and i not in picked]
    for i in rnd.sample(plain, min(4, len(plain))):
        reasons.setdefault(i, []).append('random control: no linguistic candidate')
        picked.append(i)
    out = []
    for k, i in enumerate(picked, 1):
        r = rows[i]
        lab = r['_labels']
        out.append({'review_id': f'R{k:02d}', 'clip_id': r['clip_id'], 'queue_reasons': ' | '.join(reasons[i]),
                    'auto_labels_true': ';'.join(c for c, v in lab.items() if v['value']),
                    'fingerspelling_candidate_evidence': '; '.join(lab['fingerspelling_candidate']['evidence']),
                    'named_entity_candidate_evidence': '; '.join(lab['named_entity_candidate']['evidence']),
                    'number_candidate_evidence': '; '.join(lab['number_candidate']['evidence']),
                    'reference': r['reference'], 'pred_A_official': r['predictions'][A], 'pred_C_ours_on_official_crop': r['predictions'][Cn],
                    'chrf_A': r['metrics'][A]['chrf'], 'chrf_C': r['metrics'][Cn]['chrf'],
                    'sentence_bleu_A': r['metrics'][A]['sentence_bleu'], 'sentence_bleu_C': r['metrics'][Cn]['sentence_bleu'],
                    'auto_primary_error_A': r['_an'][A]['primary_error_type'], 'auto_primary_error_C': r['_an'][Cn]['primary_error_type'],
                    'local_video_path': man[r['clip_id']]['local_video_path'],
                    'analysis_status': ANALYSIS_STATUS, 'review_status': 'PENDING', 'reviewer': '', 'verified_fingerspelling': '', 'verified_named_entity': '',
                    'verified_number_signing': '', 'verified_negation_nmm': '', 'verified_question_nmm': '',
                    'spatial_relations_notes': '', 'occlusion_observed': '', 'visual_issue_observed': '',
                    'manual_primary_error_type': '', 'manual_notes': ''})
    assert 30 <= len(out) <= 50, len(out)
    C.write_csv(os.path.join(C.OUT, 'manual_review_queue.csv'), out)


# ---------------- representative failures ----------------
def write_representatives(rows, cats, summary):
    A, Cn = C.PRIMARY, C.PAIRED

    def block(r, why):
        a, c = r['_an'][A], r['_an'][Cn]
        lab = [k for k, v in r['_labels'].items() if v['value']]
        return (f"#### `{r['clip_id']}` — {why}\n\n"
                f"- auto labels: {', '.join(lab) if lab else '(none)'}\n"
                f"- A_official: primary=`{a['primary_error_type']}` chrF={r['metrics'][A]['chrf']:.1f} sBLEU={r['metrics'][A]['sentence_bleu']:.1f} "
                f"WER={r['metrics'][A]['wer']:.2f} len_ratio={a['length_ratio']} content_P={a['content_precision']} content_R={a['content_recall']}\n"
                f"- C_ours_on_official_crop: primary=`{c['primary_error_type']}` chrF={r['metrics'][Cn]['chrf']:.1f} sBLEU={r['metrics'][Cn]['sentence_bleu']:.1f}\n\n"
                f"| | text |\n|---|---|\n| REF | {r['reference'].replace('|', '/')} |\n"
                f"| A_official | {r['predictions'][A].replace('|', '/')} |\n| C_ours_on_official_crop | {r['predictions'][Cn].replace('|', '/')} |\n\n")

    md = ['# Representative failures (automatic selection, NOT manually reviewed)\n',
          f'> **Status: {ANALYSIS_STATUS}.** Category labels are weak labels; `fingerspelling_candidate` examples show '
          'rare-name / entity recovery failures, not verified fingerspelling failures.\n',
          'Auto-selected from `error_taxonomy_annotations.jsonl`. Primary system: **A_official**; paired diagnostic: '
          '**C_ours_on_official_crop** (same frames / crop / timing, our pose extractor). All labels are automatic weak labels '
          '(`*_candidate` = reference-text heuristic, visual = pose-derived proxy). Selection rule: for each A_official primary '
          'error type, the clip whose chrF is closest to that type\'s median chrF (typical case) plus the lowest-chrF clip; for each '
          'linguistic category, the lowest-chrF and median-chrF clip. Exact references and predictions are reproduced verbatim '
          '(only `|` is escaped for the table).\n']
    md.append('## 1. By A_official primary error type\n')
    for pe in PRIMARY_ORDER:
        grp = [r for r in rows if r['_an'][A]['primary_error_type'] == pe]
        if not grp:
            continue
        med = float(np.median([r['metrics'][A]['chrf'] for r in grp]))
        typical = min(grp, key=lambda r: (abs(r['metrics'][A]['chrf'] - med), r['idx']))
        worst = min(grp, key=lambda r: (r['metrics'][A]['chrf'], r['idx']))
        md.append(f'### {pe} (n={len(grp)} of 128 for A_official)\n')
        md.append(block(typical, f'typical {pe} (chrF closest to type median {med:.1f})'))
        if worst is not typical:
            md.append(block(worst, f'worst {pe}'))
    md.append('## 2. By linguistic candidate category\n')
    for c in ['fingerspelling_candidate', 'named_entity_candidate', 'number_candidate', 'negation_candidate', 'question_candidate']:
        grp = [r for r, f in zip(rows, cats[c]) if f]
        if not grp:
            continue
        tag = ' — EXPLORATORY (n < 10)' if len(grp) < EXPLORATORY_N else ''
        md.append(f'### {c} (n={len(grp)}){tag}\n')
        med = float(np.median([r['metrics'][A]['chrf'] for r in grp]))
        worst = min(grp, key=lambda r: (r['metrics'][A]['chrf'], r['idx']))
        typical = min(grp, key=lambda r: (abs(r['metrics'][A]['chrf'] - med), r['idx']))
        md.append(block(worst, f'lowest A_official chrF in {c}; evidence: {r_ev(worst, c)}'))
        if typical is not worst:
            md.append(block(typical, f'median-chrF clip in {c}; evidence: {r_ev(typical, c)}'))
    md.append('## 3. Largest A_official vs C_ours_on_official_crop disagreements\n')
    md.append('Same frames, crop and timing; only the pose extractor differs. Large per-clip swings occur in both directions.\n')
    d = sorted(rows, key=lambda r: r['metrics'][A]['chrf'] - r['metrics'][Cn]['chrf'])
    md.append(block(d[-1], f"A better than C by {d[-1]['metrics'][A]['chrf'] - d[-1]['metrics'][Cn]['chrf']:.1f} chrF"))
    md.append(block(d[0], f"C better than A by {d[0]['metrics'][Cn]['chrf'] - d[0]['metrics'][A]['chrf']:.1f} chrF"))
    open(os.path.join(C.OUT, 'representative_failures.md'), 'w', encoding='utf-8').write('\n'.join(md))


def r_ev(r, c):
    return ', '.join(r['_labels'][c]['evidence']) or '-'


if __name__ == '__main__':
    main()
