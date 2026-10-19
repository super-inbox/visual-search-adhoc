# Task e: ASL review inspection sheet for the 45 clips of the 10.13 manual-review package (CPU, existing data only).
# One row per clip: ground truth, production output, Uni-Sign output, an AUTOMATIC initial error category with evidence,
# and blank reviewer fields. Nothing is decoded, re-scored or inferred about the signing; no reviewer field is filled.
# Systems (all the same public Uni-Sign checkpoint, P0-12 T4/fp16 predictions):
#   prod_output    = B_ours_5p39  PROVISIONAL stand-in for "our production solution": the historical our-pipeline baseline
#                  (our pose extractor, original timestamps, full frame; = P0-18 A_old). Not verified as the current live
#                  production system; replace the column if the actual production output is identified.
#   unisign_output = A_official   Uni-Sign with its official poses + official re-aligned timing / signer crop
# Inputs : ../../10.13/asl-unisign-error-taxonomy/{manual_review/review_packet.csv, manual_review/weak_labels.csv,
#          error_taxonomy_annotations.jsonl}, how2sign_v2/manifest.csv (source video id)
# Outputs: ../inspection_sheet.csv, ../inspection_sheet.html
# Labelling discipline:
#   * initial_* columns are automatic weak labels (reference-text heuristics + text checks of the outputs), never ASL facts
#   * spatial_relations has no committed weak label; a strict English locative-phrase proxy is added HERE (new, weakest)
#   * reviewer_* / review fields are written blank (review_status = not_started) and asserted blank
# Usage: python3 -I build_inspection_sheet.py   (deterministic: rebuilding gives byte-identical outputs)
import csv, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(OUT, '..', '..', '..', '..'))
TAX = os.path.join(ROOT, 'docs/daily_report/10.13/asl-unisign-error-taxonomy')
sys.path.insert(0, os.path.join(TAX, 'scripts'))
import common as C  # noqa: E402
import taxonomy as T  # noqa: E402  (same number / negation / token rules as the committed taxonomy)

PACKET = os.path.join(TAX, 'manual_review/review_packet.csv')
WEAK = os.path.join(TAX, 'manual_review/weak_labels.csv')
ANN = os.path.join(TAX, 'error_taxonomy_annotations.jsonl')
PROD, UNI = 'B_ours_5p39', 'A_official'
SYS = {PROD: 'prod', UNI: 'Uni-Sign'}
PROD_SOURCE = ('B_ours_5p39 (PROVISIONAL): historical our-pipeline baseline = P0-18 A_old (our pose extractor, original '
               'timestamps, full frame); not verified as the current live production system; replace this column if '
               'the actual production output is identified')

# focus categories requested for the review, in primary-category priority order (rarest critical information first);
# a category whose item is in the reference outranks one where an output inserts it
FOCUS = ['negation', 'questions', 'numbers', 'names', 'fingerspelling', 'spatial_relations']
GENERAL, NO_ERR = 'general_semantic', 'no_clear_error'
REVIEWER_CATEGORIES = ['fingerspelling', 'names', 'numbers', 'negation', 'questions', 'spatial_relations', GENERAL,
                       'no_error', 'unclear', 'other']
REVIEW_STATUS = ['not_started', 'in_progress', 'reviewed', 'needs_second_review', 'video_unplayable']
# letter-level fingerspelling evidence (vs a capitalised word that may be a name sign): fingerspelling outranks names
LETTER_LEVEL_FS = r'\[(acronym_or_all_caps|single_capital_letter|hyphen_spelled_letters|camelcase_name)\]'
GOOD_CHRF = 39.952  # A_official S4 lower bound (manual_review/README.md): both systems >= this -> no_clear_error
# strict English locative phrases only ("here", "there", "right", "over", "through" excluded: mostly non-spatial uses)
SPATIAL_RE = re.compile(r"\b(to the (?:left|right)|on the (?:left|right)|(?:left|right)[- ]hand side|left side|right side|"
                        r"above|below|underneath|beneath|behind|in front of|next to|beside|between|on top of|"
                        r"across from|opposite|inside|outside|around|center|centre|middle|side)\b", re.I)
# what only an ASL-fluent reviewer can settle, per focus category
ASL_QUESTION = {
    'fingerspelling': 'is it actually fingerspelled, and what is spelled?',
    'names': 'is the name signed (name sign / fingerspelling) or absent from the signing?',
    'numbers': 'is a number actually signed, and which value?',
    'negation': 'is negation signed / marked non-manually (headshake)?',
    'questions': 'is a question marked (brows / wh-sign), or is it rhetorical?',
    'spatial_relations': 'does the signer use signing space / classifiers for this relation?',
    GENERAL: 'does the signing support the reference, prod or Uni-Sign content?',
    NO_ERR: 'confirm the outputs match what is signed (sanity row).',
}

FIELDS = ['review_id', 'clip_id', 'video_id', 'video_path', 'video_status', 'duration_s', 'queue_reasons',
          'ground_truth', 'prod_output', 'prod_output_source', 'unisign_output', 'prod_vs_unisign', 'chrf_prod', 'chrf_unisign',
          'auto_error_type_prod', 'auto_error_type_unisign',
          'initial_error_category', 'initial_error_categories_all', 'weak_focus_candidates',
          'initial_label_source', 'initial_label_status', 'evidence_notes', 'visual_flags', 'showcase_example',
          'asl_fluent_question',
          'reviewer', 'reviewer_asl_background', 'reviewer_verified_category', 'verified_label_source',
          'reviewer_comment', 'review_status', 'reviewed_at']
REVIEWER_FIELDS = ['reviewer', 'reviewer_asl_background', 'reviewer_verified_category', 'verified_label_source',
                   'reviewer_comment', 'reviewed_at']


def toks(text):
    return set(C.norm_tokens(text))


def present(items, text):
    """items present in text by the taxonomy's token rule (lowercased whole-token match)."""
    ts = toks(text)
    return [i for i in items if T.strip_tok(i).lower().replace('’', "'") in ts]


def neg_tokens(text):
    return [t for t in C.norm_tokens(text) if t in T.NEG_WORDS or t.endswith("n't")]


def new_caps(pred, ref):
    """capitalised non-initial words in pred that are not in ref (likely substituted names)."""
    rt = toks(ref)
    out = []
    for sent in T.sentences(pred):
        for k, t in enumerate(T.TOK_RE.findall(sent)):
            t = T.strip_tok(t)
            if k > 0 and t and t[0].isupper() and t not in T.CAP_STOPLIST and t.lower() not in rt and t not in out:
                out.append(t)
    return out


def fmt(xs):
    return ', '.join(xs) if xs else '—'


def check(cat, ref, w, preds, sa):
    """-> (is candidate in ref, {system: missed?}, evidence line) for one focus category. None if not applicable."""
    if cat in ('names', 'fingerspelling'):
        key = 'named_entity_candidate' if cat == 'names' else 'fingerspelling_candidate'
        if w[key] != 'yes':
            return None
        items = [e.split(' [')[0] for e in w[key + '__evidence'].split('; ')]
        recall_key = 'named_entity_recall' if cat == 'names' else 'fingerspelling_recall'
        miss, parts = {}, []
        for s in (PROD, UNI):
            got = present(items, preds[s])
            assert round(len(got) / len(items), 3) == sa[s]['category_checks'][recall_key], (cat, s)  # same rule as taxonomy
            miss[s] = len(got) < len(items)
            extra = f'; new names in output: {fmt(new_caps(preds[s], ref))}' if cat == 'names' else ''
            parts.append(f'{SYS[s]} kept {len(got)}/{len(items)} ({fmt(got)}){extra}')
        label = w[key + '__evidence'] if cat == 'fingerspelling' else fmt(items)
        return True, miss, f'{cat}: ref {label} | ' + ' | '.join(parts)
    if cat == 'numbers':
        rv = T.num_values(ref)
        if w['number_candidate'] == 'yes':
            rv2 = [v for v in rv if v != '1'] or rv  # taxonomy's number_recall rule
            miss = {s: not all(v in T.num_values(preds[s]) for v in rv2) for s in (PROD, UNI)}
            return True, miss, (f'numbers: ref values {fmt(rv)} | ' +
                                ' | '.join(f'{SYS[s]} values {fmt(T.num_values(preds[s]))}' for s in (PROD, UNI)))
        ins = {s: sa[s]['category_checks'].get('number_inserted', False) for s in (PROD, UNI)}
        if any(ins.values()):
            return False, ins, ('numbers (inserted, ref has none): ' +
                                ' | '.join(f'{SYS[s]} values {fmt(T.num_values(preds[s]))}' for s in (PROD, UNI)))
        return None
    if cat == 'negation':
        if w['negation_candidate'] == 'yes':
            miss = {s: sa[s]['category_checks']['negation_dropped'] for s in (PROD, UNI)}
            return True, miss, (f'negation: ref {w["negation_candidate__evidence"]} | ' +
                                ' | '.join(f'{SYS[s]} {fmt(neg_tokens(preds[s]))}' for s in (PROD, UNI)))
        ins = {s: sa[s]['category_checks']['negation_inserted'] for s in (PROD, UNI)}
        if any(ins.values()):
            return False, ins, ('negation (inserted, ref has none): ' +
                                ' | '.join(f'{SYS[s]} {fmt(neg_tokens(preds[s]))}' for s in (PROD, UNI)))
        return None
    if cat == 'questions':
        if w['question_candidate'] == 'yes':
            if not re.search(r'\?(?!\w)', ref):  # every '?' is word-internal: mojibake apostrophe ("you?re")
                return True, {PROD: False, UNI: False}, ('questions: ref "?" is only word-internal (mojibake apostrophe, '
                                                         'e.g. "you?re"): committed weak label, likely false positive')
            miss = {s: sa[s]['category_checks']['question_mark_lost'] for s in (PROD, UNI)}
            return True, miss, ('questions: ref ends/contains "?" | ' +
                                ' | '.join(f'{SYS[s]} {"has" if not miss[s] else "no"} "?"' for s in (PROD, UNI)))
        ins = {s: sa[s]['category_checks']['question_mark_inserted'] for s in (PROD, UNI)}
        if any(ins.values()):
            return False, ins, ('questions (inserted "?", ref has none): ' +
                                ' | '.join(f'{SYS[s]} {"has" if ins[s] else "no"} "?"' for s in (PROD, UNI)))
        return None
    if cat == 'spatial_relations':
        items = sorted({m.lower() for m in SPATIAL_RE.findall(ref)})
        if not items:
            return None
        miss = {s: not all(re.search(r'\b' + re.escape(i) + r'\b', preds[s], re.I) for i in items) for s in (PROD, UNI)}
        return True, miss, (f'spatial_relations [NEW text proxy, weakest]: ref phrase {fmt(items)} | ' +
                            ' | '.join(f'{SYS[s]} {"kept" if not miss[s] else "missing"}' for s in (PROD, UNI)))
    raise ValueError(cat)


def main():
    packet = list(csv.DictReader(open(PACKET, encoding='utf-8')))
    weak = {r['clip_id']: r for r in csv.DictReader(open(WEAK, encoding='utf-8'))}
    ann = {r['clip_id']: r for r in C.read_jsonl(ANN)}
    man = {r['how2sign_id']: r for r in csv.DictReader(open(C.MANIFEST, encoding='utf-8'))}
    assert len(packet) == 45 and set(weak) == {p['clip_id'] for p in packet}
    rows = []
    for p in packet:
        cid = p['clip_id']; a = ann[cid]; w = weak[cid]; sa = a['system_analysis']
        ref, preds = a['reference'], a['predictions']
        assert ref == p['reference'] and preds[UNI] == p['pred_A_official'] and w['label_source'] == 'automatic_weak'
        cands, failed, inserted, ev = [], [], [], []
        order = list(FOCUS)
        if re.search(LETTER_LEVEL_FS, w['fingerspelling_candidate__evidence']):
            order.remove('fingerspelling'); order.insert(order.index('names'), 'fingerspelling')
        for cat in order:
            r = check(cat, ref, w, preds, sa)
            if r is None:
                continue
            in_ref, miss, line = r
            if in_ref:
                cands.append(cat)
            who = [SYS[s] for s in (PROD, UNI) if miss[s]]
            if who:
                (failed if in_ref else inserted).append(cat)
            ev.append((cat, f'{line} → {"MISSED by " + " + ".join(who) if in_ref and who else "INSERTED by " + " + ".join(who) if who else "kept by both"}'))
        ch = {s: sa[s]['metrics']['chrf'] for s in (PROD, UNI)}
        ev.append((GENERAL, 'general: ' + ' | '.join(
            f'{SYS[s]} {sa[s]["primary_error_type"]}, chrF {ch[s]:.1f}, content recall {sa[s]["content_recall"]}'
            for s in (PROD, UNI))))
        failed += inserted  # item in the reference lost > item inserted by an output (ref has none)
        if failed:
            primary = failed[0]
        elif min(ch.values()) >= GOOD_CHRF:
            primary = NO_ERR
        else:
            primary = GENERAL
        allcats = failed + ([GENERAL] if primary != NO_ERR and GENERAL not in failed else [])
        rows.append({
            'review_id': p['review_id'], 'clip_id': cid, 'video_id': man[cid]['source_video_id'],
            'video_path': p['expected_video_path'], 'video_status': p['video_status'], 'duration_s': p['duration_s'],
            'queue_reasons': p['queue_reasons'], 'ground_truth': ref,
            'prod_output': preds[PROD], 'prod_output_source': PROD_SOURCE, 'unisign_output': preds[UNI],
            'prod_vs_unisign': 'identical' if C.norm_tokens(preds[PROD]) == C.norm_tokens(preds[UNI]) else 'differ',
            'chrf_prod': f'{ch[PROD]:.3f}', 'chrf_unisign': f'{ch[UNI]:.3f}',
            'auto_error_type_prod': sa[PROD]['primary_error_type'], 'auto_error_type_unisign': sa[UNI]['primary_error_type'],
            'initial_error_category': primary, 'initial_error_categories_all': ';'.join(allcats) or NO_ERR,
            'weak_focus_candidates': ';'.join(cands),
            'initial_label_source': 'automatic_weak', 'initial_label_status': 'candidate_unverified',
            'evidence_notes': ' || '.join(e for _, e in sorted(ev, key=lambda x: x[0] != primary)),  # primary first
            'visual_flags': p['visual_flags_true'], 'showcase_example': '',
            'asl_fluent_question': ASL_QUESTION[primary],
            **{f: '' for f in REVIEWER_FIELDS}, 'review_status': 'not_started',
        })
    # showcase: per focus category up to 3 clips where GT / prod / Uni-Sign all differ; prefer clips where exactly one
    # system missed the item (prod vs Uni-Sign disagreement), then (names) an output that substitutes another name,
    # then the lower Uni-Sign chrF
    for cat in FOCUS + [GENERAL]:
        pool = [r for r in rows if r['initial_error_category'] == cat and r['prod_vs_unisign'] == 'differ'
                and not r['showcase_example']]
        one = lambda r: 0 if re.search(rf'{cat}[^|]*?→ MISSED by (prod|Uni-Sign)(?! \+)', r['evidence_notes']) else 1
        subst = lambda r: 0 if cat != 'names' or re.search(r'new names in output: [^—|]', r['evidence_notes']) else 1
        for r in sorted(pool, key=lambda r: (one(r), subst(r), float(r['chrf_unisign'])))[:3]:
            r['showcase_example'] = cat
    for r in rows:
        assert all(r[f] == '' for f in REVIEWER_FIELDS) and r['review_status'] == 'not_started'
        assert set(r) == set(FIELDS)
    C.write_csv(os.path.join(OUT, 'inspection_sheet.csv'), rows, FIELDS)
    tpl = open(os.path.join(HERE, 'inspection_sheet_template.html'), encoding='utf-8').read()
    video_rel = os.path.relpath(ROOT, OUT)
    data = {'rows': rows, 'fields': FIELDS, 'reviewer_fields': REVIEWER_FIELDS + ['review_status'],
            'categories': REVIEWER_CATEGORIES, 'statuses': REVIEW_STATUS, 'video_root': video_rel}
    html = tpl.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
    open(os.path.join(OUT, 'inspection_sheet.html'), 'w', encoding='utf-8').write(html)
    from collections import Counter
    print('rows', len(rows), '| differ', sum(r['prod_vs_unisign'] == 'differ' for r in rows))
    print('initial_error_category', dict(Counter(r['initial_error_category'] for r in rows)))
    print('showcase', dict(Counter(r['showcase_example'] for r in rows if r['showcase_example'])))
    print('weak_focus_candidates', dict(Counter(c for r in rows for c in r['weak_focus_candidates'].split(';') if c)))


if __name__ == '__main__':
    main()
