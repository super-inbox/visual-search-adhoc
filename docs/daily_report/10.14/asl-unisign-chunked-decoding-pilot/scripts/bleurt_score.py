# VM, after all arms ran: sentence-level BLEURT-20 for the 36 pilot clips, every arm (U36 + joined S1/S2/S3), against the
# full clip reference. Checkpoint: the BLEURT-20 directory the Uni-Sign eval already uses (worktree/BLEURT-20).
# BLEURT definition (frozen): bleurt.score.BleurtScorer(BLEURT-20).score(references=refs, candidates=hyps), one score per
# clip; analyze_pilot.py reports the mean over a subset and paired-bootstrap CIs on the mean difference.
# References: labels.test_p012_128 text (what the Uni-Sign scorer uses) passed through the same latin-1 -> utf-8
# mojibake fix as the manifest, so they equal manifest reference_text.
# Usage: python -I bleurt_score.py <BLEURT-20 dir> <run root> <plan dir> <labels.test_p012_128> <out.jsonl>
import gzip, json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pilot_join import arm_outputs, load_plan  # noqa: E402

ckpt, run_root, plan_dir, labels, out = sys.argv[1:6]


def fix(s):
    try:
        return s.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


lab = pickle.load(gzip.open(labels, 'rb'))  # trusted, checksum-verified by the runner
_, clips = load_plan(plan_dir)
ids = [c['clip_id'] for c in clips]
refs = [fix(lab[i + '.mp4']['text']) for i in ids]
from bleurt import score  # noqa: E402
scorer = score.BleurtScorer(ckpt)
with open(out, 'w') as f:
    for arm in ('U36', 'S1', 'S2', 'S3'):
        H = arm_outputs(run_root, plan_dir, arm)
        s = scorer.score(references=refs, candidates=[H[i] for i in ids], batch_size=16)
        for i, h, v in zip(ids, [H[i] for i in ids], s):
            f.write(json.dumps({'arm': arm, 'clip_id': i, 'bleurt': float(v), 'hyp': h}) + '\n')
        print(arm, 'mean BLEURT', sum(s) / len(s))
