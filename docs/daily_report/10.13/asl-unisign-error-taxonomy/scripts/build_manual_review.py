# Build the manual-review packet for the 45 clips in manual_review_queue.csv (CPU, stdlib only).
# Two reviewer roles, labelled separately and exported to separate files:
#   Role A  translation-error review  (no ASL knowledge needed: reference vs A_official text, obvious output failures)
#   Role B  ASL-linguistic review     (ASL-fluent annotator only: fingerspelling, numbers, names, non-manuals, space)
# Inputs : manual_review_queue.csv, error_taxonomy_annotations.jsonl, representative_failures.md (this folder),
#          how2sign_v2/manifest.csv (expected video path + frozen video sha256).
# Outputs: manual_review/review_packet.csv               everything the reviewers see, one row per clip (read-only context)
#          manual_review/weak_labels.csv                 every automatic weak label (value + evidence), kept apart from manual labels
#          manual_review/translation_error_review.csv    Role A form: blank manual fields (same columns the page exports)
#          manual_review/asl_linguistic_review.csv       Role B form: blank manual fields (same columns the page exports)
#          manual_review/video_availability.csv          expected path, whether it exists, sha256 vs the frozen manifest
#          manual_review/required_videos.sha256          the 45 required videos (restore / verify list)
#          manual_review/review.html                     self-contained review page (role switch; video + text + form; CSV export)
# No manual label is inferred or filled: every reviewer field is written blank and checked blank. No ASL-specific label
# is ever derived from a weak label.
# Usage: python -I build_manual_review.py [--restore-from <dir with How2Sign v2 .mp4 files>]
#   --restore-from copies only queued clips whose sha256 matches the manifest into the canonical (gitignored)
#   asl-translator/data/public_benchmarks/how2sign_v2/videos/ path; files already there are never overwritten.
import argparse, csv, hashlib, json, os, re, shutil, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402

TAX = C.OUT
OUT = os.path.join(TAX, 'manual_review')
QUEUE = os.path.join(TAX, 'manual_review_queue.csv')
ANN = os.path.join(TAX, 'error_taxonomy_annotations.jsonl')
REPR = os.path.join(TAX, 'representative_failures.md')
A, CN = 'A_official', 'C_ours_on_official_crop'

YNU = ['yes', 'no', 'unclear']
ERR = ['correct', 'omission', 'substitution', 'hallucination', 'repetition', 'truncation', 'other']
# reviewer fields per role, in form order: (name, allowed values or None for optional free text, question shown)
ROLES = {
    'translation_error': {
        'title': 'Role A · Translation-error review', 'file': 'translation_error_review.csv', 'asl_fluent_required': False,
        'fields': [
            ('translation_error_type', ERR, 'Main error of the A_official prediction compared with the English reference'),
            ('critical_information_error', YNU, 'Does A_official get critical information wrong vs the reference (who / what / number / negation / question)?'),
            ('obvious_repetition', YNU, 'Does A_official repeat a word or phrase in a loop?'),
            ('obvious_truncation', YNU, 'Does A_official stop mid-sentence or drop the end of the reference?'),
            ('obvious_hallucination', YNU, 'Does A_official add content that is not in the reference?'),
            ('obvious_omission', YNU, 'Does A_official leave out content that is in the reference?'),
            ('obvious_substitution', YNU, 'Does A_official replace reference content with different content?'),
            ('visual_occlusion', YNU, 'Visual only, no ASL judgement: are the hands occluded, out of frame or blurred at any point?'),
            ('translation_notes', None, 'Notes comparing the reference and A_official (and C_ours if relevant)'),
        ]},
    'asl_linguistic': {
        'title': 'Role B · ASL-linguistic review', 'file': 'asl_linguistic_review.csv', 'asl_fluent_required': True,
        'fields': [
            ('actual_fingerspelling', YNU, 'Is fingerspelling actually produced in the video?'),
            ('fingerspelled_content', None, 'Optional: what is fingerspelled, if legible (e.g. "D", "K-I-S-S-I-M-M-E-E")'),
            ('actual_number_sign', YNU, 'Is a number actually signed?'),
            ('named_entity_signed', YNU, 'Is a named entity (person / place / organisation / brand) signed, by name sign or fingerspelling?'),
            ('negation_nonmanual', YNU, 'Is negation marked non-manually (headshake, negative facial expression)?'),
            ('question_nonmanual', YNU, 'Is a question marked non-manually (brow raise for yes/no, brow furrow for wh-)?'),
            ('spatial_relation', YNU, 'Does the signing set up and use locations in signing space (loci, indexing, directional verbs)?'),
            ('classifier_use', YNU, 'Are classifier constructions (depicting signs) used?'),
            ('other_asl_phenomena', None, 'Optional: other ASL phenomena relevant to translation (role shift, constructed action, lexical variation, ...)'),
            ('asl_notes', None, 'Notes: timestamps, reasons for "unclear", anything the English reference misses'),
        ]},
}
ROLE_META = {'translation_error': ['reviewer'], 'asl_linguistic': ['reviewer', 'reviewer_asl_background']}
ASL_SPECIFIC = [f for f, _, _ in ROLES['asl_linguistic']['fields']]


def role_columns(role):
    """Exact column order of a role's CSV (blank form written here == file the page exports)."""
    return ['review_id', 'clip_id', 'review_role', *ROLE_META[role], *(f for f, _, _ in ROLES[role]['fields']),
            'review_complete', 'exported_at']


LING = ['fingerspelling_candidate', 'named_entity_candidate', 'number_candidate', 'number_candidate_broad_sensitivity',
        'negation_candidate', 'question_candidate', 'fast_signing_text_proxy']
VIS = ['long_clip_gt_256_frames', 'hand_out_of_frame_candidate', 'low_hand_conf_candidate', 'hand_near_face_candidate',
       'fast_hand_motion_candidate', 'high_hand_jitter_candidate', 'high_pose_disagreement_A_vs_C']
SEVERITY = ['S1 severe (worst chrF quartile)', 'S2 high', 'S3 moderate', 'S4 mild (best chrF quartile)']


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def representative(path):
    """clip_id -> ['<section>: <selection reason>', ...] from representative_failures.md headings."""
    out, sec = {}, ''
    for line in open(path, encoding='utf-8'):
        if line.startswith('### '):
            sec = line[4:].strip()
        elif line.startswith('## '):
            sec = line[3:].strip()
        m = re.match(r'^#### `(.+?)` — (.*)$', line.rstrip('\n'))
        if m:
            out.setdefault(m.group(1), []).append(f'{sec}: {m.group(2)}')
    return out


def fmt_ev(ev):
    return '; '.join(ev) if isinstance(ev, list) else (ev or '')


def fmt_label(w, k):
    ev = fmt_ev(w[k]['evidence'])
    return f"{k}={'yes' if w[k]['value'] else 'no'}" + (f' [{ev}]' if ev else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--restore-from', help='directory holding How2Sign v2 <clip_id>.mp4 files to copy into the canonical path')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    queue = list(csv.DictReader(open(QUEUE, encoding='utf-8')))
    ann = {r['clip_id']: r for r in C.read_jsonl(ANN)}
    man = {r['how2sign_id']: r for r in C.load_manifest()}
    rep = representative(REPR)
    assert len(queue) == 45 and len({q['clip_id'] for q in queue}) == 45, 'expected 45 unique queued clips'

    # automatic severity = A_official sentence-chrF quartile over all 128 clips (derived here, for ordering only)
    chrf_all = sorted(r['system_analysis'][A]['metrics']['chrf'] for r in ann.values())
    qcut = [chrf_all[int(len(chrf_all) * p)] for p in (0.25, 0.5, 0.75)]

    def severity(x):
        return SEVERITY[sum(x >= c for c in qcut)]

    packet, weak, avail = [], [], []
    blank = {role: [] for role in ROLES}
    for q in queue:
        c = q['clip_id']; r = ann[c]; m = man[c]; w = r['weak_labels']; sa, sc = r['system_analysis'][A], r['system_analysis'][CN]
        assert q['reference'] == r['reference'] and q['pred_A_official'] == r['predictions'][A] \
            and q['pred_C_ours_on_official_crop'] == r['predictions'][CN], f'{c}: queue text != annotations'
        exp = os.path.join(C.ROOT, m['local_video_path'])
        if a.restore_from and not os.path.exists(exp):
            src = os.path.join(a.restore_from, c + '.mp4')
            if os.path.exists(src) and sha(src) == m['video_sha256']:
                os.makedirs(os.path.dirname(exp), exist_ok=True); shutil.copy2(src, exp)
        present = os.path.exists(exp)
        ok = present and sha(exp) == m['video_sha256']
        avail.append({'review_id': q['review_id'], 'clip_id': c, 'video_filename': c + '.mp4', 'expected_path': m['local_video_path'],
                      'present': present, 'sha256_matches_manifest': ok, 'manifest_video_sha256': m['video_sha256'],
                      'duration_s': m['duration_s'], 'status': 'AVAILABLE' if ok else ('SHA_MISMATCH' if present else 'MISSING')})
        packet.append({
            'review_id': q['review_id'], 'clip_id': c, 'video_filename': c + '.mp4', 'expected_video_path': m['local_video_path'],
            'video_status': avail[-1]['status'], 'duration_s': m['duration_s'],
            'queue_reasons': q['queue_reasons'], 'reference': r['reference'],
            'pred_A_official': r['predictions'][A], 'pred_C_ours_on_official_crop': r['predictions'][CN],
            'weak_linguistic_tags_true': ';'.join(k for k in LING if w[k]['value']),
            'weak_linguistic_tags_detail': ' | '.join(fmt_label(w, k) for k in LING),
            'manifest_heuristics': ' | '.join(f'{k}={v}' for k, v in r['manifest_heuristics'].items()),
            'visual_flags_true': ';'.join(k for k in VIS if w[k]['value']),
            'visual_flags_detail': ' | '.join(fmt_label(w, k) for k in VIS),
            'wer_A': sa['metrics']['wer'], 'chrf_A': sa['metrics']['chrf'], 'sentence_bleu_A': sa['metrics']['sentence_bleu'],
            'wer_C': sc['metrics']['wer'], 'chrf_C': sc['metrics']['chrf'], 'sentence_bleu_C': sc['metrics']['sentence_bleu'],
            'auto_primary_error_A': sa['primary_error_type'], 'auto_primary_error_C': sc['primary_error_type'],
            'auto_error_flags_A': ';'.join(k for k, v in sa['error_flags'].items() if v),
            'auto_content_recall_A': sa['content_recall'], 'auto_length_ratio_A': sa['length_ratio'],
            'auto_severity_A': severity(sa['metrics']['chrf']),
            'representative_failure': ' || '.join(rep.get(c, [])),
            'label_status': 'automatic weak labels only; manual review PENDING',
        })
        weak.append({'review_id': q['review_id'], 'clip_id': c, 'label_source': 'automatic_weak', 'status': 'candidate_unverified',
                     **{col: v for k in w for col, v in ((k, 'yes' if w[k]['value'] else 'no'),
                                                         (k + '__evidence', fmt_ev(w[k]['evidence'])))}})
        for role in ROLES:
            cols = role_columns(role)
            blank[role].append({**{k: '' for k in cols}, 'review_id': q['review_id'], 'clip_id': c, 'review_role': role})

    # guards: the two roles do not share a label; nothing manual is filled automatically
    fa, fb = ({f for f, _, _ in ROLES[r]['fields']} for r in ROLES)
    assert not fa & fb, f'roles share fields: {fa & fb}'
    assert not set(ASL_SPECIFIC) & set(weak[0]), 'an ASL-specific manual field collides with a weak-label column'
    for role, rows in blank.items():
        for b in rows:
            assert all(v == '' for k, v in b.items() if k not in ('review_id', 'clip_id', 'review_role')), f'{role}: prefilled field'
    C.write_csv(os.path.join(OUT, 'review_packet.csv'), packet)
    C.write_csv(os.path.join(OUT, 'weak_labels.csv'), weak)
    for role, rows in blank.items():
        C.write_csv(os.path.join(OUT, ROLES[role]['file']), rows, role_columns(role))
    C.write_csv(os.path.join(OUT, 'video_availability.csv'), avail)
    # restore list: the 45 required files, sha256sum format, paths relative to the repo root (`shasum -a 256 -c` from there)
    with open(os.path.join(OUT, 'required_videos.sha256'), 'w') as f:
        f.writelines(f"{x['manifest_video_sha256']}  {x['expected_path']}\n" for x in avail)

    rel_root = os.path.relpath(C.ROOT, OUT)  # page lives in OUT; videos are referenced relative to the repo root
    roles = {r: {'title': v['title'], 'file': v['file'], 'asl_fluent_required': v['asl_fluent_required'],
                 'columns': role_columns(r), 'fields': [{'name': f, 'options': o, 'question': t} for f, o, t in v['fields']]}
             for r, v in ROLES.items()}
    data = {'clips': packet, 'roles': roles,
            'video_prefix': rel_root.replace(os.sep, '/') + '/', 'severity_cut_chrf': qcut,
            'storage_key': 'unisign-taxonomy-manual-review-v2'}
    payload = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    tpl = open(os.path.join(HERE, 'manual_review_template.html'), encoding='utf-8').read()
    assert tpl.count('/*__DATA__*/null') == 1
    open(os.path.join(OUT, 'review.html'), 'w', encoding='utf-8').write(tpl.replace('/*__DATA__*/null', payload))

    n_ok = sum(x['status'] == 'AVAILABLE' for x in avail)
    print(f'packet: {len(packet)} clips | videos available (sha256 verified): {n_ok}/45 | severity chrF cuts {qcut}')
    for x in avail:
        if x['status'] != 'AVAILABLE':
            print(f"  {x['status']}: {x['review_id']} {x['video_filename']} (expected {x['expected_path']})")


if __name__ == '__main__':
    main()
