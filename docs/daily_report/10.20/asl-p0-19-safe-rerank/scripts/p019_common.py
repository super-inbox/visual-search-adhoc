"""P0-19 shared helpers: holdout guard + path tripwire, frozen P0-14 concept matcher, candidate-id trimming.

Layout assumption (same on the Mac and on the VM upload): this file lives in
  <root>/docs/daily_report/10.20/asl-p0-19-safe-rerank/scripts/
and the P0-14 / P0-16 folders are at their repository-relative paths under <root>/docs/daily_report/.
"""
import builtins, csv, hashlib, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
DAILY = os.path.dirname(os.path.dirname(EXP))
P014 = os.path.join(DAILY, "10.15", "asl-unisign-representation-probe")
P016 = os.path.join(DAILY, "10.16", "asl-p0-16-experimental-credibility")
CONFIG = os.path.join(EXP, "config", "stage0_config.json")

ARCHIVE_TEST_DIR = "test-pose-rtmpose-192/"          # the only official-archive directory Stage 0 may read

# Any path that names How2Sign val material or the sealed holdout lists. Opening one after the guard has run is a
# hard error (gate G3). The guard itself reads holdout/ once, before the tripwire is installed.
DENY = re.compile(r"(realigned_val|how2sign_val|val_raw_videos|val_rgb_front|crop_val|[/\\]holdout[/\\]|"
                  r"(^|[/\\_])H1[89][_.]|h18_oneshot|h19_oneshot)", re.I)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_config():
    return json.load(open(CONFIG))


# ------------------------------------------------------------------ holdout protection (gate G3)
_TRIP = {"installed": False}


def guard_and_trip(clip_ids):
    """P0-16 deny-list check on every clip id, then install an open() tripwire for holdout / val paths."""
    sys.path.insert(0, os.path.join(P016, "scripts"))
    from holdout_guard import assert_not_holdout
    assert_not_holdout(clip_ids)
    if not _TRIP["installed"]:
        real_open = builtins.open

        def tripped_open(file, *args, **kw):
            if isinstance(file, (str, bytes, os.PathLike)) and DENY.search(os.fsdecode(file)):
                raise PermissionError(f"P0-19 tripwire: holdout / val path refused: {os.fsdecode(file)}")
            return real_open(file, *args, **kw)
        builtins.open = tripped_open
        io.open = tripped_open
        _TRIP["installed"] = True
    return {"guard_checked_ids": len(clip_ids), "tripwire_installed": True}


# ------------------------------------------------------------------ frozen P0-14 matcher (no val CSV is read)
def load_matcher(train_csv, test_csv):
    """Execute the top half of P0-14 build_concepts.py unchanged. Lemma families depend on train only; the val slot
    is given the TEST csv so How2Sign val references are never opened. Returns (present(sent)->[30 ints],
    concept_rows, tierL_index, test_refs {SENTENCE_NAME: SENTENCE})."""
    src = open(os.path.join(P014, "scripts", "build_concepts.py")).read()
    src = src.split("# ---------------------------------------------------------------- per-clip annotations")[0]
    g = {"__name__": "bc"}
    argv = sys.argv
    sys.argv = ["bc", train_csv, test_csv, test_csv, P014]
    try:
        exec(compile(src, "build_concepts.py", "exec"), g)
    finally:
        sys.argv = argv
    rows = list(csv.DictReader(open(os.path.join(P014, "concepts", "concept_list_v1.csv"))))
    # only concept / tier / match / forms are used; the val_pos* aggregate columns are never read
    rows = [{k: r[k] for k in ("concept", "tier", "match", "forms")} for r in rows]
    lidx = [k for k, r in enumerate(rows) if r["tier"] == "L"]
    assert len(rows) == 30 and len(lidx) == 24

    def present(sent):
        lem, tok = g["lemmas"](sent), set(g["tokens"](sent))
        return [int((r["concept"].lower() in lem) if r["match"] == "lemma" else bool(tok & set(r["forms"].split())))
                for r in rows]
    refs = {r["SENTENCE_NAME"]: r["SENTENCE"] for r in g["splits"]["test"]}
    return present, rows, lidx, refs


# ------------------------------------------------------------------ token ids
def trim_ids(ids, eos=1, pad=0):
    """Decoder output ids -> [start .. first eos] (inclusive); without eos, strip trailing pad after position 0."""
    ids = list(ids)
    if eos in ids[1:]:
        return ids[: ids.index(eos, 1) + 1]
    while len(ids) > 1 and ids[-1] == pad:
        ids.pop()
    return ids
