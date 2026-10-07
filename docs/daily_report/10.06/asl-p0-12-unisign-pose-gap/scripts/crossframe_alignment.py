# P0-12: on the time span where our clip (original timing, full frame) and the official crop clip (re-aligned
# timing) show the SAME moments, map B (rtmlib on full frame) onto C (rtmlib on official crop) with a per-clip
# affine fit x' = sx*x + tx, y' = sy*y + ty (pixels), searching a frame offset of +-12 around the timestamp
# prediction. Answers:
#   (1) do How2Sign timestamps predict the frame correspondence? (best offset near 0)
#   (2) how much do crop pixels / detection resolution change keypoints beyond a pure crop+resize?
#       (residual / shoulder width; compare with A-vs-C extractor difference)
# Pose-only, no model inference.
import sys, os, csv, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safe_pickle

seg_json, ffprobe_csv, dirB, dirC, out_json = sys.argv[1:6]
seg = json.load(open(seg_json))
fps = {}
for line in open(ffprobe_csv):
    c, w, h, fr, dur, nb = line.strip().split(',')
    a, b = fr.split('/'); fps[c] = float(a) / float(b)
THR = 0.3
IDX = [0] + list(range(3, 11)) + list(range(91, 133))  # body 9 + both hands, as used by Uni-Sign


def load(p):
    d = safe_pickle.load(p); wh = np.array(d.get('w_h') or d.get('frame_wh'), float)
    k = np.stack([np.asarray(x, float)[0] for x in d['keypoints']]) * wh
    s = np.stack([np.asarray(x, float)[0] for x in d['scores']])
    return k, s


def fit(kb, kc, m):
    out = []
    for ax in (0, 1):
        X = np.stack([kb[..., ax][m], np.ones(m.sum())], 1)
        coef, *_ = np.linalg.lstsq(X, kc[..., ax][m], rcond=None); out.append(coef)
    return out


res = {}
for cid, s in seg.items():
    if s['iou'] == 0:
        continue
    f = fps[cid]
    kb, sb = load(os.path.join(dirB, cid + '.pkl')); kc, sc = load(os.path.join(dirC, cid + '.pkl'))
    shift = int(round((s['ours_start'] - s['realigned_start']) * f))  # C index = B index + shift
    best = None
    for off in range(-12, 13):
        ib = np.arange(len(kb)); ic = ib + shift + off
        ok = (ic >= 0) & (ic < len(kc))
        if ok.sum() < 10:
            continue
        b, c = kb[ib[ok]][:, IDX], kc[ic[ok]][:, IDX]
        m = (sb[ib[ok]][:, IDX] > THR) & (sc[ic[ok]][:, IDX] > THR)
        (sx, tx), (sy, ty) = fit(b, c, m)
        pred = np.stack([b[..., 0] * sx + tx, b[..., 1] * sy + ty], -1)
        sw = np.linalg.norm(c[:, 3] - c[:, 4], axis=-1)  # IDX positions 3,4 = COCO 5,6 shoulders
        err = np.linalg.norm(pred - c, axis=-1) / np.maximum(sw[:, None], 1)
        r = dict(offset_frames=off, n_frames=int(ok.sum()), sx=float(sx), sy=float(sy),
                 resid_body=float(np.median(err[:, :9][m[:, :9]])), resid_hands=float(np.median(err[:, 9:][m[:, 9:]])))
        if best is None or r['resid_body'] < best['resid_body']:
            best = r
    if best:
        best['iou'] = s['iou']; best['sx_over_sy'] = best['sx'] / best['sy']; res[cid] = best
v = list(res.values())
agg = {'n_clips_with_overlap': len(v),
       'best_offset_abs_le_1_frame': sum(abs(x['offset_frames']) <= 1 for x in v),
       'best_offset_abs_le_3_frames': sum(abs(x['offset_frames']) <= 3 for x in v),
       'best_offset_median': float(np.median([x['offset_frames'] for x in v])),
       'resid_body_over_shoulder_median': round(float(np.median([x['resid_body'] for x in v])), 4),
       'resid_body_over_shoulder_p90': round(float(np.percentile([x['resid_body'] for x in v], 90)), 4),
       'resid_hands_over_shoulder_median': round(float(np.median([x['resid_hands'] for x in v])), 4),
       'resid_hands_over_shoulder_p90': round(float(np.percentile([x['resid_hands'] for x in v], 90)), 4),
       'fitted_sx_over_sy_median': round(float(np.median([x['sx_over_sy'] for x in v])), 4),
       'fitted_scale_median': round(float(np.median([x['sx'] for x in v])), 4)}
json.dump({'aggregate': agg, 'per_clip': res}, open(out_json, 'w'), indent=1)
print(json.dumps(agg, indent=1))
