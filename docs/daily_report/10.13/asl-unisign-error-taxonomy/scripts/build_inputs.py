# Step 1: assemble ../inputs_128.jsonl -- one row per frozen clip (labels.test_p012_128 order), with
#   - exact references (canonical manifest text + verbatim labels.test text)
#   - exact predictions of all four P0-12 T4/fp16 systems (verbatim strings from the restored prediction files)
#   - per-sample WER / chrF / sentence BLEU for every system
#   - manifest metadata + manifest heuristic flags (copied as-is; they are heuristics, unreviewed)
#   - pose features per pose source: pose_diagnostics.csv (A / B / C rows) + extra features computed here from the PKLs
#   - A-vs-C keypoint agreement (pose_diagnostics_aggregate.json) and segment alignment (segment_alignment_128.json)
# No model inference. Visual features are pose-derived proxies only (motion blur / true occlusion are not observable here).
import os, sys, json, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import safe_pickle

DIAG_NAME = {'A_official': 'A_official_pkl', 'C_ours_on_official_crop': 'C_rtmlib_lightweight_officialcrop',
             'B_ours_5p39': 'B_rtmlib_lightweight_fullframe'}  # B_aspect shares B's detections (rescaled), no own diag row
DIAG_KEEP = ['frames', 'frame_w', 'frame_h', 'frames_0_person', 'frames_multi_person', 'frames_gt_256',
             'left_mean_conf', 'right_mean_conf', 'left_missing_rate', 'right_missing_rate', 'body_mean_conf', 'face_all_mean_conf',
             'left_hand_jitter_model_units', 'right_hand_jitter_model_units', 'model_input_masked_frac']
HANDS = {'left': (slice(91, 112), 9), 'right': (slice(112, 133), 10)}  # COCO-WholeBody hand block, wrist index


def pkl_features(path):
    """Extra per-clip pose features from the raw PKL (normalized coords, first person per frame)."""
    d = safe_pickle.load(path)
    wh = np.array(d['w_h'], float)
    kp = np.stack([np.asarray(k, float)[0] if len(k) else np.full((133, 2), np.nan) for k in d['keypoints']])
    sc = np.stack([np.asarray(s, float)[0] if len(s) else np.zeros(133) for s in d['scores']])
    px = kp * wh
    sw = np.maximum(np.linalg.norm(px[:, 5] - px[:, 6], axis=-1), 1.0)  # shoulder width (px)
    f = {}
    for h, (sl, w) in HANDS.items():
        oof = ((kp[:, sl] < 0) | (kp[:, sl] > 1)).any(-1)  # keypoint outside the frame / crop
        f[f'{h}_hand_half_out_of_frame_rate'] = round(float((oof.mean(1) >= 0.5).mean()), 4)
        f[f'{h}_hand_any_out_of_frame_rate'] = round(float(oof.any(1).mean()), 4)
        f[f'{h}_hand_lowconf_frame_rate'] = round(float((sc[:, sl].mean(1) < 0.5).mean()), 4)
        f[f'{h}_wrist_speed_median_sw_per_frame'] = round(float(np.median(np.linalg.norm(np.diff(px[:, w], axis=0), axis=-1) / sw[1:])), 5)
        f[f'{h}_wrist_near_face_rate'] = round(float((np.linalg.norm(px[:, w] - px[:, 0], axis=-1) / sw < 0.5).mean()), 4)
    return f


def main():
    labels = C.load_labels()
    ids = [i for i, _ in labels]
    lab_refs = dict(labels)
    refs = C.load_refs()
    man = {r['how2sign_id']: r for r in C.load_manifest()}
    preds = {s: C.load_preds(s) for s in C.SYSTEMS}
    diag = {(r['clip_id'], r['extractor']): r for r in csv.DictReader(open(C.POSE_DIAG))}
    agree = {a['clip_id']: a for a in json.load(open(C.POSE_AGG))['A_vs_C_per_clip']}
    seg = json.load(open(C.SEG_ALIGN))
    rows = []
    for k, cid in enumerate(ids):
        m = man[cid]
        ref = refs[cid]
        r = {'idx': k, 'clip_id': cid, 'reference': ref, 'reference_labels_test': lab_refs[cid],
             'reference_n_words': len(ref.split()), 'duration_s': float(m['duration_s']), 'words_per_second': float(m['words_per_second']),
             'selection_reason': m['selection_reason'],
             'manifest_heuristics': {c: m[c] for c in ('official_ends_with_question_mark', 'heuristic_contains_number_token',
                                                       'heuristic_proper_noun_or_acronym_fingerspelling_candidate',
                                                       'heuristic_fast_signing_wps_ge_p90')},
             'predictions': {s: preds[s][cid] for s in C.SYSTEMS}, 'metrics': {}, 'pose': {}}
        for s in C.SYSTEMS:
            h = preds[s][cid]
            e, n = C.wer_p012(h, ref)
            S, D, I, _ = C.align(C.norm_tokens(h), C.norm_tokens(ref))
            nr = len(C.norm_tokens(ref))
            r['metrics'][s] = {'wer': round(e / n, 4), 'wer_edits': e, 'wer_ref_words': n,
                               'wer_norm': round((S + D + I) / nr, 4), 'sub': S, 'del': D, 'ins': I, 'ref_tokens_norm': nr,
                               'hyp_tokens_norm': len(C.norm_tokens(h)),
                               'chrf': round(C.sentence_chrf(h, ref), 3), 'sentence_bleu': round(C.sentence_bleu(h, ref), 3)}
        for s, ex in DIAG_NAME.items():
            dr = diag[(cid, ex)]
            p = {key: (dr[key] == 'True' if key == 'frames_gt_256' else float(dr[key])) for key in DIAG_KEEP}
            p['source'] = f'pose_diagnostics.csv[{ex}]'
            if s != 'B_ours_5p39':  # A / C share the official crop + timing; extra PKL features computed for them
                p.update(pkl_features(os.path.join(C.POSE_DIRS[s], cid + '.pkl')))
            r['pose'][s] = p
        a = agree[cid]
        r['pose_agreement_A_vs_C'] = {key: a[key] for key in a if key.endswith(('_err_over_shoulder_median', '_visibility_disagree_rate'))}
        r['segment_alignment_B_vs_official'] = seg[cid]
        rows.append(r)
    C.write_jsonl(os.path.join(C.OUT, 'inputs_128.jsonl'), rows)
    # self-check: predictions / references preserved byte-exact
    back = C.read_jsonl(os.path.join(C.OUT, 'inputs_128.jsonl'))
    assert [b['clip_id'] for b in back] == ids
    assert all(b['predictions'][s] == preds[s][b['clip_id']] for b in back for s in C.SYSTEMS)
    assert all(b['reference'] == refs[b['clip_id']] and b['reference_labels_test'] == lab_refs[b['clip_id']] for b in back)
    print(f'wrote inputs_128.jsonl: {len(rows)} rows; predictions/references round-trip exact')


if __name__ == '__main__':
    main()
