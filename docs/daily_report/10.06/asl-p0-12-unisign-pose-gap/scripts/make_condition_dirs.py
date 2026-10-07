# P0-12: lay out each pose condition in the exact directory/pkl format the UNMODIFIED official
# Uni-Sign loader expects (config.pose_dirs["How2Sign"].format("test") -> <cond>/test-pose-rtmpose-192/<clip>.pkl),
# plus a 128-clip subset of the official labels.test (official file is not modified).
#
#   A_official          official pkl (official crop, realigned timing, official extractor)
#   B_ours_5p39         our 5.39 pose path: rtmlib lightweight, full 1280x720 frame, original timing
#   B_aspect            B keypoints/frames unchanged, but normalised by the clip's official-crop (W,H) instead of (1280,720)
#                       -> isolates the (W,H) anisotropy; Uni-Sign's crop_scale is shift/isotropic-scale invariant,
#                          so only the H/W ratio of the normaliser matters
#   C_ours_on_official_crop  rtmlib lightweight on the official crop video (same frames/timing as A)
import sys, os, csv, gzip, pickle
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safe_pickle

labels_test, manifest, dirA, dirB, dirC, out_root = sys.argv[1:7]
ids = [r['how2sign_id'] for r in csv.DictReader(open(manifest))]
lab = safe_pickle.SafeUnpickler(gzip.open(labels_test)).load()
sub = {k: lab[k] for k in [i + '.mp4' for i in ids]}
os.makedirs(out_root, exist_ok=True)
with gzip.open(os.path.join(out_root, 'labels.test_p012_128'), 'wb') as f:
    pickle.dump(sub, f)
with gzip.open(os.path.join(out_root, 'labels.test_p012_smoke3'), 'wb') as f:
    pickle.dump({k: sub[k] for k in list(sub)[:3]}, f)

def emit(cond, cid, data):
    d = os.path.join(out_root, cond, 'test-pose-rtmpose-192'); os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, cid + '.pkl'), 'wb') as f:
        pickle.dump(data, f)

for cid in ids:
    A = safe_pickle.load(os.path.join(dirA, cid + '.pkl'))
    B = safe_pickle.load(os.path.join(dirB, cid + '.pkl'))
    C = safe_pickle.load(os.path.join(dirC, cid + '.pkl'))
    emit('A_official', cid, A)
    emit('B_ours_5p39', cid, {'keypoints': B['keypoints'], 'scores': B['scores'], 'w_h': list(B['frame_wh'])})
    Wb, Hb = B['frame_wh']; Wa, Ha = A['w_h']
    kp = [np.asarray(k) * np.array([Wb, Hb]) / np.array([Wa, Ha]) for k in B['keypoints']]
    emit('B_aspect', cid, {'keypoints': kp, 'scores': B['scores'], 'w_h': [Wa, Ha], 'note': 'B pixels / official-crop (W,H)'})
    emit('C_ours_on_official_crop', cid, {'keypoints': C['keypoints'], 'scores': C['scores'], 'w_h': list(C['frame_wh'])})
print('labels subset:', len(sub), '-> conditions written under', out_root)
