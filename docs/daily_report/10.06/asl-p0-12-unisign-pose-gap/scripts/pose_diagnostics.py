# P0-12 pose-level diagnostics. No model inference.
# Sources:
#   A = official Uni-Sign How2Sign pose pkl (test-pose-rtmpose-192), official crop video, official segment timing
#   B = our 5.39 pose path: rtmlib Wholebody lightweight on our full-frame 1280x720 How2Sign clip (original timing)
#   C = rtmlib Wholebody lightweight on the official crop video (same frames as A)
# Model-input statistics use load_part_kp/crop_scale copied verbatim from Uni-Sign datasets.py:18-104 @ eed438bc.
import sys, os, csv, json, copy
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safe_pickle

THR = 0.3
BODY = [0] + list(range(3, 11))
FACE = list(range(23, 23 + 17))[::2] + list(range(83, 83 + 8)) + [53]
PARTS = {'body': BODY, 'left': list(range(91, 112)), 'right': list(range(112, 133)), 'face_all': FACE}


# ---- verbatim from Uni-Sign datasets.py (torch.tensor() wrapper dropped; returns numpy) ----
def crop_scale(motion, thr):
    result = copy.deepcopy(motion)
    valid_coords = motion[motion[..., 2] > thr][:, :2]
    if len(valid_coords) < 4:
        return np.zeros(motion.shape), 0, None
    xmin = min(valid_coords[:, 0]); xmax = max(valid_coords[:, 0])
    ymin = min(valid_coords[:, 1]); ymax = max(valid_coords[:, 1])
    ratio = 1
    scale = max(xmax - xmin, ymax - ymin) * ratio
    if scale == 0:
        return np.zeros(motion.shape), 0, None
    xs = (xmin + xmax - scale) / 2
    ys = (ymin + ymax - scale) / 2
    result[..., :2] = (motion[..., :2] - [xs, ys]) / scale
    result[..., :2] = (result[..., :2] - 0.5) * 2
    result = np.clip(result, -1, 1)
    result[result[..., 2] <= thr] = 0
    return result, scale, [xs, ys]


def load_part_kp(skeletons, confs):
    thr = 0.3
    out = {}
    scale = None
    for part in ['body', 'left', 'right', 'face_all']:
        kps, cs = [], []
        for skeleton, conf in zip(skeletons, confs):
            skeleton = skeleton[0]; conf = conf[0]
            if part == 'body':
                k = skeleton[BODY, :]; c = conf[BODY]
            elif part == 'left':
                k = skeleton[91:112, :]; k = k - k[0, :]; c = conf[91:112]
            elif part == 'right':
                k = skeleton[112:133, :]; k = k - k[0, :]; c = conf[112:133]
            else:
                k = skeleton[FACE, :]; k = k - k[-1, :]; c = conf[FACE]
            kps.append(k); cs.append(c)
        kps = np.stack(kps, 0); cs = np.stack(cs, 0)
        if part == 'body':
            result, scale, _ = crop_scale(np.concatenate([kps, cs[..., None]], -1), thr)
        else:
            result = np.concatenate([kps, cs[..., None]], -1)
            if scale == 0:
                result = np.zeros(result.shape)
            else:
                result[..., :2] = result[..., :2] / scale
                result = np.clip(result, -1, 1)
                result[result[..., 2] <= thr] = 0
        out[part] = result
    return out, scale
# ---- end verbatim ----


def load_source(path):
    d = safe_pickle.load(path)
    kp, sc = d['keypoints'], d['scores']
    wh = d.get('w_h') or d.get('frame_wh')
    npers = np.array([np.asarray(k).shape[0] for k in kp])
    # frames with 0 detections would crash Uni-Sign's skeleton[0]; substitute zeros (conf 0 -> masked)
    sk = [np.asarray(k, dtype=np.float64)[:1] if np.asarray(k).shape[0] else np.zeros((1, 133, 2)) for k in kp]
    cf = [np.asarray(s, dtype=np.float64)[:1] if np.asarray(s).shape[0] else np.zeros((1, 133)) for s in sc]
    return np.concatenate(sk), np.concatenate(cf), tuple(wh), npers


def second_diff_jitter(x, valid):
    # median |x[t+1] - 2x[t] + x[t-1]| over keypoints valid in all three frames (model-input units)
    v = valid[2:] & valid[1:-1] & valid[:-2]
    acc = np.linalg.norm(x[2:] - 2 * x[1:-1] + x[:-2], axis=-1)
    return float(np.median(acc[v])) if v.any() else float('nan')


def clip_stats(sk, cf, wh, npers):
    T = len(sk)
    s = {'frames': T, 'frame_w': wh[0], 'frame_h': wh[1], 'aspect_h_over_w': round(wh[1] / wh[0], 4),
         'frames_0_person': int((npers == 0).sum()), 'frames_multi_person': int((npers > 1).sum()),
         'frames_gt_256': T > 256}
    for p, idx in PARTS.items():
        c = cf[:, idx]
        s[f'{p}_missing_rate'] = round(float((c <= THR).mean()), 4)
        s[f'{p}_mean_conf'] = round(float(c.mean()), 4)
        s[f'{p}_frame_absent_rate'] = round(float(((c > THR).sum(1) == 0).mean()), 4)  # whole part absent in frame
    s['conf_p50_all'] = round(float(np.median(cf)), 4)
    s['conf_p95_all'] = round(float(np.percentile(cf, 95)), 4)
    s['conf_max_all'] = round(float(cf.max()), 4)
    # model-input view: full sequence (no subsampling) through Uni-Sign's own normalization
    mi, scale = load_part_kp(sk[:, None], cf[:, None])
    s['body_scale_norm_units'] = round(float(scale), 4)
    b = mi['body']
    # BODY order (COCO ids 0,3..10): 0 nose, 1 l_ear, 2 r_ear, 3 l_shoulder, 4 r_shoulder, 5-6 elbows, 7-8 wrists
    lsh, rsh, nose = b[:, 3], b[:, 4], b[:, 0]
    ok = (lsh[:, 2] > 0) & (rsh[:, 2] > 0) & (nose[:, 2] > 0)
    if ok.any():
        sw = np.abs(lsh[ok, 0] - rsh[ok, 0])
        nh = np.abs((lsh[ok, 1] + rsh[ok, 1]) / 2 - nose[ok, 1])
        s['model_input_shoulder_w_over_neck_h'] = round(float(np.median(sw / np.maximum(nh, 1e-6))), 4)
    else:
        s['model_input_shoulder_w_over_neck_h'] = float('nan')
    for p in ['left', 'right']:
        x = mi[p][..., :2]; valid = mi[p][..., 2] > 0
        s[f'{p}_hand_jitter_model_units'] = round(second_diff_jitter(x, valid), 5)
    s['model_input_masked_frac'] = round(float(np.mean([(mi[p][..., 2] == 0).mean() for p in PARTS])), 4)
    return s


def agreement(skA, cfA, skC, cfC, wh):
    # A vs C on identical frames of the identical official crop: pixel error / shoulder width, both conf > THR
    T = min(len(skA), len(skC))
    pa = skA[:T] * np.array(wh); pc = skC[:T] * np.array(wh)
    sw = np.linalg.norm(pa[:, 5] - pa[:, 6], axis=-1)
    out = {'agree_frames': T}
    for p, idx in PARTS.items():
        both = (cfA[:T, idx] > THR) & (cfC[:T, idx] > THR) & (sw[:, None] > 1)
        err = np.linalg.norm(pa[:, idx] - pc[:, idx], axis=-1) / np.maximum(sw[:, None], 1)
        out[f'{p}_err_over_shoulder_median'] = round(float(np.median(err[both])), 4) if both.any() else float('nan')
        oneonly = (cfA[:T, idx] > THR) ^ (cfC[:T, idx] > THR)
        out[f'{p}_visibility_disagree_rate'] = round(float(oneonly.mean()), 4)
    return out


def main():
    manifest, dirA, dirB, dirC, out_csv, out_json = sys.argv[1:7]
    ids = [r['how2sign_id'] for r in csv.DictReader(open(manifest))]
    rows, agree = [], []
    for cid in ids:
        srcs = {}
        for name, d in (('A_official_pkl', dirA), ('B_rtmlib_lightweight_fullframe', dirB), ('C_rtmlib_lightweight_officialcrop', dirC)):
            p = os.path.join(d, cid + '.pkl')
            if os.path.exists(p):
                srcs[name] = load_source(p)
        for name, (sk, cf, wh, npers) in srcs.items():
            r = {'clip_id': cid, 'extractor': name}; r.update(clip_stats(sk, cf, wh, npers)); rows.append(r)
        if 'A_official_pkl' in srcs and 'C_rtmlib_lightweight_officialcrop' in srcs:
            skA, cfA, wh, _ = srcs['A_official_pkl']; skC, cfC, whC, _ = srcs['C_rtmlib_lightweight_officialcrop']
            a = {'clip_id': cid, 'frames_A': len(skA), 'frames_C': len(skC), 'wh_A': list(wh), 'wh_C': list(whC)}
            a.update(agreement(skA, cfA, skC, cfC, wh)); agree.append(a)
    keys = list(rows[0].keys())
    with open(out_csv, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    # aggregates
    agg = {}
    by = {}
    for r in rows: by.setdefault(r['clip_id'], set()).add(r['extractor'])
    common = {c for c, s in by.items() if len(s) == 3}
    agg['matched_clip_set'] = {'n_clips_with_all_three_sources': len(common)}
    for name in sorted(set(r['extractor'] for r in rows)):
        rs = [r for r in rows if r['extractor'] == name and r['clip_id'] in common]
        agg[name] = {'n_clips': len(rs), 'total_frames': int(sum(r['frames'] for r in rs))}
        for k in keys:
            if k in ('clip_id', 'extractor', 'frames_gt_256'): continue
            vals = np.array([r[k] for r in rs], dtype=float)
            agg[name][k + '_median'] = round(float(np.nanmedian(vals)), 4)
            agg[name][k + '_mean'] = round(float(np.nanmean(vals)), 4)
        agg[name]['clips_gt_256_frames'] = int(sum(r['frames_gt_256'] for r in rs))
    if agree:
        agg['A_vs_C_agreement'] = {k: round(float(np.nanmedian([a[k] for a in agree])), 4)
                                   for k in agree[0] if k not in ('clip_id', 'wh_A', 'wh_C')}
        agg['A_vs_C_agreement']['n_clips'] = len(agree)
        agg['A_vs_C_agreement']['frame_count_equal_clips'] = int(sum(a['frames_A'] == a['frames_C'] for a in agree))
        agg['A_vs_C_agreement']['wh_equal_clips'] = int(sum(a['wh_A'] == a['wh_C'] for a in agree))
    json.dump({'aggregate': agg, 'A_vs_C_per_clip': agree}, open(out_json, 'w'), indent=1)
    print(json.dumps(agg, indent=1))


if __name__ == '__main__':
    main()
