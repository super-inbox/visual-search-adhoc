# Shared by analyze_pilot.py (laptop) and bleurt_score.py / u36_gate.py (VM). Stdlib only.
# Parsing of Uni-Sign test_tmp_pres.txt and THE join rule for chunk outputs (frozen; see ../PILOT_PLAN.md §3):
#   for each clip, take its chunk predictions in temporal order k = 1..K, strip surrounding whitespace, drop chunks whose
#   prediction is empty, and join the rest with a single space. No de-duplication, re-casing or punctuation edits.
import csv, json, os, re

LINE_RE = re.compile(r'^sample: (.*?), prediction: (.*)$')
CHUNK_RE = re.compile(r'^(?P<clip>.+)__(?P<arm>S[123])c(?P<k>\d+)of(?P<K>\d+)$')


def read_pres(path):
    """Ordered list of (entry name without .mp4, prediction text) from a test_tmp_pres.txt."""
    out = []
    for line in open(path, encoding='utf-8'):
        m = LINE_RE.match(line.rstrip('\n'))
        if not m:
            raise ValueError(f'{path}: unparseable line {line[:80]!r}')
        out.append((m.group(1)[:-4] if m.group(1).endswith('.mp4') else m.group(1), m.group(2)))
    return out


def join_chunks(preds, plan_rows, arm):
    """preds: {chunk_name: text}. plan_rows: chunk_plan.csv rows. Returns {clip_id: joined text}; every planned chunk
    must be present exactly once."""
    rows = [r for r in plan_rows if r['arm'] == arm]
    names = [r['chunk_name'] for r in rows]
    if sorted(names) != sorted(preds):
        raise ValueError(f'{arm}: predicted entries != planned chunks '
                         f'({len(set(names) - set(preds))} missing, {len(set(preds) - set(names))} unexpected)')
    by_clip = {}
    for r in rows:
        by_clip.setdefault(r['clip_id'], []).append((int(r['k']), r['chunk_name']))
    out = {}
    for clip, ks in by_clip.items():
        ks.sort()
        assert [k for k, _ in ks] == list(range(1, len(ks) + 1)), (clip, ks)
        out[clip] = ' '.join(p for p in (preds[n].strip() for _, n in ks) if p)
    return out


def load_plan(plan_dir):
    return (list(csv.DictReader(open(os.path.join(plan_dir, 'chunk_plan.csv')))),
            list(csv.DictReader(open(os.path.join(plan_dir, 'pilot_clips.csv')))))


def arm_outputs(run_root, plan_dir, arm):
    """{clip_id: hypothesis} for the 36 pilot clips. U36: the unchunked 128-entry run restricted to the 36 clips."""
    plan, clips = load_plan(plan_dir)
    P = read_pres(os.path.join(run_root, arm, 'test_tmp_pres.txt'))
    d = dict(P)
    if len(d) != len(P):
        raise ValueError(f'{arm}: duplicate entries')
    if arm == 'U36':
        return {c['clip_id']: d[c['clip_id']] for c in clips}
    return join_chunks(d, plan, arm)
