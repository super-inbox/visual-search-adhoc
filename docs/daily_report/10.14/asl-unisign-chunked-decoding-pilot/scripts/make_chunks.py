# Chunked-decoding pilot: chunk plan (local, CPU) and chunk inputs (VM, CPU). Spec: ../PILOT_PLAN.md.
#   plan  : (laptop) reads the committed A_official source PKLs + taxonomy inputs, writes ../chunk_plan.csv (frozen frame
#           boundaries for S1/S2/S3) and ../pilot_clips.csv. Boundaries are integers, so the VM never recomputes them.
#   build : (VM) reads the frozen chunk_plan.csv and the fp16 RUNTIME PKLs ($P012/A_official/test-pose-rtmpose-192, checked
#           against the pinned runtime manifest by the runner), writes $PILOT/<ARM>/test-pose-rtmpose-192/*.pkl and
#           $PILOT/<ARM>/labels.test_pilot for ARM in SMOKE U36 S1 S2 S3, plus $PILOT/PILOT_INPUTS.sha256.
#           U36 = ALL 128 clips unchunked: runtime PKLs and labels.test_p012_128 copied byte for byte, so the loader's RNG
#           stream (random >256-frame subsampling, 8 workers) is the one of R100; the U36 gate is evaluated on the 36 pilot
#           clips. A 36-entry run would consume the RNG differently and could not reproduce R100.
# Chunk PKL = the same dict as the source ({'keypoints', 'scores', 'w_h'}) with keypoints/scores sliced to [start, end)
# and w_h unchanged. Nothing else is altered. Chunk names: <clip_id>__<ARM>c<k>of<K> (k is 1-based).
# Usage: python3 -I make_chunks.py plan
#        python -I make_chunks.py build --runtime-pose-dir $P012/A_official/test-pose-rtmpose-192 --labels $P012/labels.test_p012_128 --out $PILOT
import argparse, csv, gzip, hashlib, math, os, pickle, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..')
PLAN, CLIPS = os.path.join(D, 'chunk_plan.csv'), os.path.join(D, 'pilot_clips.csv')
MAXLEN = 256        # Uni-Sign max_length: longer inputs are randomly subsampled to 256 frames
SNAP = 24           # S3: a boundary may move at most +-24 frames from the equal split
MIN_CHUNK = 64      # S3: no chunk shorter than 64 frames after snapping
L_WRIST, R_WRIST, L_SH, R_SH = 9, 10, 5, 6   # COCO-WholeBody body indices
ARMS = ['U36', 'S1', 'S2', 'S3']


def equal_bounds(T, K):
    """K contiguous chunks, sizes differ by at most 1, earlier chunks get the extra frame."""
    q, r = divmod(T, K)
    b, s = [0], 0
    for k in range(K):
        s += q + (k < r); b.append(s)
    return b


def wrist_speed(kp):
    """Per-frame two-hand wrist speed in shoulder widths, 5-frame centred moving average. Index t = motion t-1 -> t."""
    import numpy as np
    P = np.stack([np.asarray(f)[0] for f in kp])            # T x 133 x 2
    sw = np.median(np.linalg.norm(P[:, L_SH] - P[:, R_SH], axis=1)) or 1.0
    v = np.zeros(len(P))
    v[1:] = (np.linalg.norm(np.diff(P[:, L_WRIST], axis=0), axis=1) + np.linalg.norm(np.diff(P[:, R_WRIST], axis=0), axis=1)) / sw
    return np.convolve(v, np.ones(5) / 5, mode='same')


def snap_bounds(T, K, speed):
    """S3: start from equal_bounds; move each internal boundary to the lowest-speed frame within +-SNAP, keeping every
    chunk in [MIN_CHUNK, MAXLEN]. Ties -> closest to the equal split, then earlier. Processed left to right."""
    b = equal_bounds(T, K)
    for j in range(1, K):
        lo = max(b[j] - SNAP, b[j - 1] + MIN_CHUNK, b[j + 1] - MAXLEN)
        hi = min(b[j] + SNAP, b[j + 1] - MIN_CHUNK, b[j - 1] + MAXLEN)
        cand = range(lo, hi + 1)
        b[j] = min(cand, key=lambda t: (round(float(speed[t]), 9), abs(t - b[j]), t))
    return b


def plan():
    sys.dont_write_bytecode = True
    sys.path.insert(0, os.path.join(D, '..', '..', '10.13', 'asl-unisign-error-taxonomy', 'scripts'))
    import common as C
    inp = {r['clip_id']: r for r in C.read_jsonl(os.path.join(C.OUT, 'inputs_128.jsonl'))}
    refs = C.load_refs()
    ids = [i for i, _ in C.load_labels()]
    clips, rows = [], []
    for idx, c in enumerate(ids):
        T = int(inp[c]['pose']['A_official']['frames']); w = len(refs[c].split())
        if T <= MAXLEN:
            continue  # <= 256 frames: never chunked, not run in the pilot
        pk = C.safe_pickle.SafeUnpickler(open(os.path.join(C.POSE_DIRS['A_official'], c + '.pkl'), 'rb')).load()
        assert len(pk['keypoints']) == len(pk['scores']) == T, c
        grp = 'long_ref_ge35' if w >= 35 else 'control_gt256_ref_lt35'
        clips.append({'idx': idx, 'clip_id': c, 'group': grp, 'frames': T, 'ref_words': w})
        K2 = math.ceil(T / MAXLEN)
        sp = wrist_speed(pk['keypoints'])
        for arm, b in (('S1', equal_bounds(T, 2)), ('S2', equal_bounds(T, K2)), ('S3', snap_bounds(T, K2, sp))):
            K = len(b) - 1
            for k in range(K):
                rows.append({'arm': arm, 'clip_id': c, 'group': grp, 'frames': T, 'k': k + 1, 'K': K,
                             'start': b[k], 'end': b[k + 1], 'len': b[k + 1] - b[k],
                             'subsampled_by_loader': b[k + 1] - b[k] > MAXLEN,
                             'shift_vs_equal_split': b[k] - equal_bounds(T, K)[k] if arm == 'S3' else 0,
                             'chunk_name': f'{c}__{arm}c{k + 1}of{K}'})
    assert len(clips) == 36 and sum(x['group'] == 'long_ref_ge35' for x in clips) == 21
    C.write_csv(CLIPS, clips); C.write_csv(PLAN, rows)
    for arm in ('S1', 'S2', 'S3'):
        r = [x for x in rows if x['arm'] == arm]
        print(f"{arm}: {len(r)} chunks, len min/max {min(x['len'] for x in r)}/{max(x['len'] for x in r)}, "
              f"{sum(x['subsampled_by_loader'] for x in r)} chunks > {MAXLEN} frames (still subsampled)")


def build(a):
    rows = list(csv.DictReader(open(PLAN)))
    clips = list(csv.DictReader(open(CLIPS)))
    with gzip.open(a.labels, 'rb') as f:
        labels = pickle.load(f)  # trusted: the pinned labels.test_p012_128 (checksum verified by the runner)
    smoke = [r for r in rows if r['arm'] == 'S2'][:3]
    arms = {'U36': [(k.replace('.mp4', ''), k.replace('.mp4', ''), 0, None) for k in labels],  # all 128, verbatim
            **{arm: [(r['chunk_name'], r['clip_id'], int(r['start']), int(r['end'])) for r in rows if r['arm'] == arm]
               for arm in ('S1', 'S2', 'S3')},
            'SMOKE': [(r['chunk_name'], r['clip_id'], int(r['start']), int(r['end'])) for r in smoke]
                     + [(clips[0]['clip_id'], clips[0]['clip_id'], 0, None)]}
    sums = []
    for arm, ents in arms.items():
        pdir = os.path.join(a.out, arm, 'test-pose-rtmpose-192'); os.makedirs(pdir, exist_ok=False)
        lab = {}
        if arm == 'U36':  # byte-for-byte copies of the runtime inputs
            for name, *_ in ents:
                shutil.copyfile(os.path.join(a.runtime_pose_dir, name + '.pkl'), os.path.join(pdir, name + '.pkl'))
            shutil.copyfile(a.labels, os.path.join(a.out, arm, 'labels.test_pilot'))
        for name, src, s, e in ([] if arm == 'U36' else ents):
            pk = pickle.load(open(os.path.join(a.runtime_pose_dir, src + '.pkl'), 'rb'))
            T = len(pk['keypoints'])
            if e is None:
                e = T
            assert 0 <= s < e <= T and len(pk['scores']) == T, (name, s, e, T)
            out = {'keypoints': pk['keypoints'][s:e], 'scores': pk['scores'][s:e], 'w_h': pk['w_h']}
            with open(os.path.join(pdir, name + '.pkl'), 'wb') as f:
                pickle.dump(out, f)
            src_lab = labels[src + '.mp4']
            # the full clip reference is attached to every chunk; it is NOT used for chunk-level scoring
            lab[name + '.mp4'] = {**src_lab, 'name': name + '.mp4', 'video_path': name + '.mp4'}
        lp = os.path.join(a.out, arm, 'labels.test_pilot')
        if arm != 'U36':
            with gzip.open(lp, 'wb') as f:
                pickle.dump(lab, f)
        for p in [lp] + [os.path.join(pdir, n + '.pkl') for n, *_ in ents]:
            sums.append(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {os.path.relpath(p, a.out)}")
        print(f'{arm}: {len(ents)} entries')
    open(os.path.join(a.out, 'PILOT_INPUTS.sha256'), 'w').write('\n'.join(sums) + '\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['plan', 'build'])
    ap.add_argument('--runtime-pose-dir'); ap.add_argument('--labels'); ap.add_argument('--out')
    a = ap.parse_args()
    plan() if a.mode == 'plan' else build(a)
