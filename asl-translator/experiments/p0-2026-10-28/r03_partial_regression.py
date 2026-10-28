#!/usr/bin/env python3
"""R03 partial-transcription offline regression (2026-10-28 PROGRESS_REVIEW item 2). No model or network call.

Everything replays the responses saved in asl-eval/production_45/raw/R03.json through a fake client:
  1. parser replay    : production `_call_vlm` (loaded by path, sha256-checked, not modified) on each saved raw_text
  2. end-to-end replay: production `transcribe_asl` on the same R03 video, fake client returning the 2 saved responses
                        in call order; checks the frame timestamps and batch sizes equal the recorded run
  3. current behaviour on scenario fixtures (same video, scripted responses) + a mirror of asl_pipeline's decision
  4. syntactic repair : exhaustive single-character edit search on the malformed batch (grammar-only and schema-valid)
  5. proposed policy  : reference implementation of the status taxonomy + controlled retry (NOT production code),
                        run against regression tests T1-T13
  6. cost / latency   : per-call usage from the 45-case raw records; retry overhead estimate
  7. score sensitivity: hypothetical 45-case corpus chrF if R03 had used the recovered batch (descriptive only)

usage: python3 -I r03_partial_regression.py --prod-src <read-only export root of curify-studio 4220e03c> [--out FILE]
The export holds curify_background/app/utils/asl_utils.py (sha256 90df9563...) as in the 2026-10-27 evaluation.
"""
from __future__ import annotations

import argparse, hashlib, importlib.util, json, re, string, sys, tempfile, types
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EVAL = REPO / "asl-translator/asl-eval"
RAW = EVAL / "production_45/raw"
OUT = HERE / "results/r03_partial_regression.json"
PROD_SHA = "90df95635fcb3297e2c2b0cd6bf15061d398f9ae2ea3c66543b982487c59ffa5"
R03_VIDEO_SHA = "76b1f143adf60fc064c3e83ef865abd0a3e0135011dd01e39f1df94e84b4d286"

sys.path.insert(0, str(REPO / "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_by_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


WRAPPER = load_by_path("run_production_45", EVAL / "run_production_45.py")
TOOLS = load_by_path("production_45_tools", EVAL / "production_45_tools.py")
QUOTA_TOKENS = WRAPPER.QUOTA_TOKENS          # the 10/27 wrapper's mirror of production imagen_service


# ── fake provider ────────────────────────────────────────────────────────────
class Resp:
    def __init__(self, text):
        self.text = text


class FakeClient:
    """Plays back a script: each entry is a response text (str) or an exception instance to raise."""
    def __init__(self, script):
        self.script, self.calls = list(script), []
        self.models = types.SimpleNamespace(generate_content=self._gen)

    def _gen(self, **kw):
        parts = kw["contents"][0].parts
        self.calls.append({"n_images": sum(1 for p in parts if getattr(p, "inline_data", None) is not None)})
        item = self.script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return Resp(item)


def install_stub(state):
    app = types.ModuleType("app"); app.__path__ = []
    services = types.ModuleType("app.services"); services.__path__ = []
    utils = types.ModuleType("app.utils"); utils.__path__ = []
    stub = types.ModuleType("app.services.imagen_service")
    stub.get_gemini_client = lambda: state["client"]
    stub.is_quota_exhausted = lambda exc: any(tok in str(exc) for tok in QUOTA_TOKENS)
    sys.modules.update({"app": app, "app.services": services, "app.utils": utils, "app.services.imagen_service": stub})


def pipeline_decision(res):
    """Mirror of asl_pipeline.py's branch on the AslResult (lines 80-98 of the exported file)."""
    if res.quota_exhausted:
        return "GenerationQuotaExhaustedError (no queue retry)"
    if res.error and not res.segments:
        if res.had_transport_error:
            return "generic Exception -> job-queue retry of the whole video"
        return "NoSigningDetectedError (no retry)"
    if not res.segments:
        return "NoSigningDetectedError (no retry)"
    return "proceeds as a normal completed transcript (no partial flag; asl_low_confidence only from density/repetition)"


# ── 1-3: production replays ──────────────────────────────────────────────────
def parser_replay(prod, state, raw_text, n_images):
    with tempfile.TemporaryDirectory() as td:
        frames = []
        for i in range(n_images):
            p = Path(td) / f"f_{i:.3f}.jpg"; p.write_bytes(b"\xff\xd8\xff"); frames.append(str(p))
        state["client"] = FakeClient([raw_text])
        try:
            data = prod._call_vlm(frames, state["client"])
            return {"outcome": "parsed", "n_segments": len(data.get("segments", []))}
        except Exception as e:
            out = {"outcome": "raised", "exception": type(e).__name__, "message": str(e)}
            m = re.search(r"\{.*\}", raw_text, re.S)
            out["regex_fallback_span_is_whole_text"] = bool(m) and m.group(0) == raw_text.strip()
            return out


def e2e(prod, state, video, script):
    stamps = []
    real = prod._extract_frames

    def extract(vp, st, od):
        stamps.extend(st)
        return real(vp, st, od)
    prod._extract_frames = extract
    state["client"] = FakeClient(script)
    try:
        res = prod.transcribe_asl(str(video))
        crashed = None
    except Exception as e:
        res, crashed = None, f"{type(e).__name__}: {e}"
    finally:
        prod._extract_frames = real
    rec = {"calls": len(state["client"].calls), "batch_sizes": [c["n_images"] for c in state["client"].calls],
           "timestamps": [round(x, 3) for x in stamps]}
    if crashed:
        rec.update(crashed=crashed, pipeline="unhandled exception escapes transcribe_asl -> job-queue failure/retry")
        return rec
    rec.update(text=res.text, n_segments=len(res.segments), error=res.error, had_transport_error=res.had_transport_error,
               quota_exhausted=res.quota_exhausted, pipeline=pipeline_decision(res))
    return rec


def malformed_with_error_at(pos):
    """A malformed JSON reply whose JSONDecodeError position is exactly `pos` (for the '429' substring check)."""
    for n in range(0, 2000):
        s = '{"segments": [], "notes": "' + "x" * n + '", }'
        try:
            json.loads(s)
        except json.JSONDecodeError as e:
            if e.pos == pos:
                return s
    raise AssertionError(pos)


# ── 4: syntactic repair search ───────────────────────────────────────────────
TOP_KEYS = {"segments", "confidence", "notes"}
SEG_KEYS = {"start", "end", "text"}


class DupKey(ValueError):
    pass


def _no_dups(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise DupKey(keys)
    return dict(pairs)


def schema_ok(d):
    """Strict reading of the production prompt's 'Return STRICT JSON only' schema."""
    if not isinstance(d, dict) or not set(d) <= TOP_KEYS or not isinstance(d.get("segments"), list):
        return False
    for s in d["segments"]:
        if not isinstance(s, dict) or set(s) != SEG_KEYS or not isinstance(s["text"], str):
            return False
        if not all(isinstance(s[k], (int, float)) and not isinstance(s[k], bool) for k in ("start", "end")):
            return False
        if not 0 <= s["start"] <= s["end"]:
            return False
    return True


def canon(text):
    return json.dumps(json.loads(text, object_pairs_hook=lambda p: [list(x) for x in p]), sort_keys=False)


def tree_summary(t):
    """Pairs-preserving tree -> segment texts and duplicate-key count (duplicates are what grammar alone allows)."""
    pairs = json.loads(t)
    if not isinstance(pairs, list) or not pairs or not all(isinstance(p, list) and len(p) == 2 for p in pairs):
        return {"shape": type(pairs).__name__}
    segs = dict((k, v) for k, v in pairs).get("segments")
    if not isinstance(segs, list):
        return {"shape": "object without segments list"}
    out = {"n_segments": len(segs), "segment_texts": [], "segments_with_duplicate_keys": 0}
    for sp in segs:
        keys = [k for k, _ in sp] if isinstance(sp, list) else []
        out["segment_texts"].append([v for k, v in sp if k == "text"] if isinstance(sp, list) else sp)
        out["segments_with_duplicate_keys"] += len(keys) != len(set(keys))
    return out


def repair_search(raw):
    alphabet = [c for c in string.printable if c not in "\x0b\x0c"]
    variants = set()
    for i in range(len(raw) + 1):
        for c in alphabet:
            variants.add(("insert", i, c, raw[:i] + c + raw[i:]))
    for i in range(len(raw)):
        variants.add(("delete", i, raw[i], raw[:i] + raw[i + 1:]))
        for c in alphabet:
            if c != raw[i]:
                variants.add(("substitute", i, c, raw[:i] + c + raw[i + 1:]))
    grammar, schema = {}, {}
    for op, i, c, v in variants:
        try:
            tree = canon(v)
        except json.JSONDecodeError:
            continue
        grammar.setdefault(tree, []).append((op, i, c))
        try:
            d = json.loads(v, object_pairs_hook=_no_dups)
        except DupKey:
            continue
        if schema_ok(d):
            schema.setdefault(tree, []).append((op, i, c, v))
    return len(variants), grammar, schema


# ── 5: proposed policy (reference implementation, not production code) ───────
MAX_BATCH_RETRIES = 1        # one retry of the failed batch only
MAX_VIDEO_RETRIES = 2        # at most two retry calls per video


class TransportError(Exception):
    """Fixture exception; `kind` mimics what the SDK error would tell us."""
    def __init__(self, kind, msg=""):
        super().__init__(msg or kind)
        self.kind = kind


def classify_attempt(item):
    """One provider attempt -> (outcome, detail, data). Outcomes: ok | valid_empty | parse_failure | transport_failure."""
    if isinstance(item, TransportError):
        quota = item.kind == "quota"
        retryable = item.kind in ("timeout", "connection", "server_5xx", "rate_limit_429")
        return "transport_failure", {"kind": item.kind, "quota": quota, "retryable": retryable, "message": str(item)}, None
    text, finish = (item, "STOP") if isinstance(item, str) else item[:2]
    if finish not in ("STOP",):
        return "parse_failure", {"kind": f"finish_reason_{finish}", "retryable": finish == "MAX_TOKENS"}, None
    raw = (text or "").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        m = re.search(r"\{.*\}", raw, re.S)          # production's code-fence fallback, kept
        try:
            data = json.loads(m.group(0)) if m else None
        except json.JSONDecodeError:
            data = None
        if data is None:
            return "parse_failure", {"kind": "malformed_json", "retryable": True, "message": str(e),
                                     "pos": e.pos, "raw_len": len(raw)}, None
    if not isinstance(data, dict) or not isinstance(data.get("segments"), list):
        return "parse_failure", {"kind": "schema_top_level", "retryable": True}, None
    good, rejected = [], 0
    for s in data["segments"]:
        try:
            seg = {"start": float(s["start"]), "end": float(s["end"]), "text": str(s.get("text", "")).strip()}
            if not 0 <= seg["start"] <= seg["end"]:
                raise ValueError
        except (KeyError, TypeError, ValueError, AttributeError):
            rejected += 1
            continue
        if seg["text"]:
            good.append(seg)
    data = {"segments": good, "rejected_segments": rejected, "notes": data.get("notes", "")}
    return ("ok" if good else "valid_empty"), {}, data


def unique_repair(raw):
    """Fallback only: accept a repair iff exactly one schema-valid tree is one structural-character edit away."""
    structural = "{}[],:"
    trees = {}
    for i in range(len(raw) + 1):
        for c in structural:
            v = raw[:i] + c + raw[i:]
            try:
                d = json.loads(v, object_pairs_hook=_no_dups)
            except (json.JSONDecodeError, DupKey):
                continue
            if schema_ok(d):
                trees.setdefault(json.dumps(d), (i, c))
    for i in range(len(raw)):
        if raw[i] in structural:
            v = raw[:i] + raw[i + 1:]
            try:
                d = json.loads(v, object_pairs_hook=_no_dups)
            except (json.JSONDecodeError, DupKey):
                continue
            if schema_ok(d):
                trees.setdefault(json.dumps(d), (i, "delete " + raw[i]))
    if len(trees) != 1:
        return None, len(trees)
    tree, edit = next(iter(trees.items()))
    return {"data": json.loads(tree), "edit": edit}, 1


def run_policy(batches, repair_fallback=False):
    """batches: per batch, the list of attempt items in order (first = original call, rest = what a retry would get).
    Returns the machine-readable result proposed for production."""
    retries_used, out_batches, segments = 0, [], []
    for b, attempts in enumerate(batches):
        attempts = list(attempts)
        log = []
        while True:
            item = attempts.pop(0)
            outcome, detail, data = classify_attempt(item)
            usage = item[2] if isinstance(item, tuple) and len(item) > 2 else None
            log.append({"attempt": len(log), "outcome": outcome, **({"detail": detail} if detail else {}),
                        **({"usage": usage} if usage else {})})
            if outcome in ("ok", "valid_empty"):
                break
            if not detail.get("retryable") or len(log) > MAX_BATCH_RETRIES or retries_used >= MAX_VIDEO_RETRIES \
                    or not attempts:
                break
            retries_used += 1
        rec = {"batch": b, "attempts": log, "final": outcome, "retries": len(log) - 1}
        if outcome in ("ok", "valid_empty"):
            rec["rejected_segments"] = data["rejected_segments"]
            segments += [{**s, "batch": b, "recovered_by_repair": False} for s in data["segments"]]
        elif repair_fallback and outcome == "parse_failure" and detail.get("kind") == "malformed_json":
            raw = item if isinstance(item, str) else item[0]
            rep, n_trees = unique_repair(raw)
            rec["repair"] = {"applied": rep is not None, "schema_valid_trees_at_distance_1": n_trees}
            if rep:
                rec["final"] = "recovered_by_repair"
                segments += [{"start": float(s["start"]), "end": float(s["end"]), "text": s["text"], "batch": b,
                              "recovered_by_repair": True} for s in rep["data"]["segments"] if s["text"].strip()]
        out_batches.append(rec)
    finals = [r["final"] for r in out_batches]
    valid = [f in ("ok", "valid_empty") for f in finals]
    rejected = sum(r.get("rejected_segments", 0) for r in out_batches)
    if all(valid):
        status = "partial" if rejected else ("success" if segments else "no_signing_detected")
    elif any(valid):
        status = "partial"
    else:
        tf = [r for r in out_batches if r["final"] == "transport_failure"]
        status = "transport_failure" if tf else "parse_failure"
    if any(f == "recovered_by_repair" for f in finals) and status not in ("partial",):
        status = "partial"                     # a repaired batch is never a clean answer
    quota = bool(out_batches) and all(r["final"] == "transport_failure" and r["attempts"][-1]["detail"]["quota"]
                                      for r in out_batches)
    segments.sort(key=lambda s: s["start"])
    assert not (status == "success" and any(f != "ok" and f != "valid_empty" for f in finals))   # invariant
    return {"status": status, "quota_exhausted": quota,
            "batches_total": len(out_batches), "batches_succeeded": sum(valid),
            "batches_failed": len(out_batches) - sum(valid), "retry_calls": retries_used,
            "rejected_segments": rejected,
            "failures": [{"batch": r["batch"], "final": r["final"], "attempts": r["attempts"],
                          **({"repair": r["repair"]} if "repair" in r else {})}
                         for r in out_batches if r["final"] not in ("ok", "valid_empty")],
            "segments": segments, "text": " ".join(s["text"] for s in segments)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prod-src", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()

    prod_path = a.prod_src / "curify_background/app/utils/asl_utils.py"
    assert sha256(prod_path) == PROD_SHA, "production asl_utils.py export does not match the evaluated file"
    pipe_path = a.prod_src / "curify_background/app/pipelines/asl_pipeline.py"
    r03_path = RAW / "R03.json"
    r03 = json.loads(r03_path.read_text())
    assert r03["review_id"] == "R03" and len(r03["api_calls"]) == 2
    assert_not_holdout([r03["clip_id"]])
    video = REPO / r03["input_video"]
    assert sha256(video) == r03["input_video_sha256"] == R03_VIDEO_SHA

    state = {}
    install_stub(state)
    prod = load_by_path("app.utils.asl_utils", prod_path)
    raw0, raw1 = (c["raw_text"] for c in r03["api_calls"])
    res = {"inputs": {"r03_raw": str(r03_path.relative_to(REPO)), "r03_raw_sha256": sha256(r03_path),
                      "r03_video": r03["input_video"], "r03_video_sha256": R03_VIDEO_SHA,
                      "production_file": "curify-studio 4220e03c curify_background/app/utils/asl_utils.py",
                      "production_file_sha256": PROD_SHA,
                      "pipeline_file": "curify-studio 4220e03c curify_background/app/pipelines/asl_pipeline.py",
                      "pipeline_file_sha256": sha256(pipe_path) if pipe_path.exists() else None,
                      "quota_classifier": "mirror of production imagen_service.is_quota_exhausted from the 10/27 "
                                          f"wrapper: substring match on {list(QUOTA_TOKENS)}",
                      "model_calls": 0}}

    # 1. parser replay
    res["parser_replay"] = [dict(batch=i, n_images=c["n_images"], finish_reason=c["finish_reason"],
                                 usage=c["usage"], latency_s=c["latency_s"],
                                 **parser_replay(prod, state, c["raw_text"], c["n_images"]))
                            for i, c in enumerate(r03["api_calls"])]
    lines = raw0.split("\n")
    res["malformed_condition"] = {"batch": 0, "error_line": 8, "error_col": 5, "error_char": 110,
                                  "context_lines_4_to_9": lines[3:9],
                                  "description": "first segment object is never closed: after its last value "
                                                 "(\"text\": \"Support each other.\") the next line is ',' and then "
                                                 "'{' opens the second segment, so the parser, still inside object 1, "
                                                 "expects a property name and finds '{'"}

    # 2. end-to-end replay of the recorded run
    rep = e2e(prod, state, video, [raw0, raw1])
    rep["timestamps_equal_recorded"] = rep.pop("timestamps") == [round(x, 3) for x in r03["timestamps_sent_s"]]
    rep["batch_sizes_equal_recorded"] = rep["batch_sizes"] == [c["n_images"] for c in r03["api_calls"]]
    rep["text_equals_recorded"] = rep["text"] == r03["output_text_raw"]
    res["e2e_replay_current_production"] = rep

    # 3. current production on scenario fixtures (same video; 2 batches of 24 + 6 frames)
    valid = lambda *t: json.dumps({"segments": [{"start": 1.0 + i, "end": 1.5 + i, "text": x} for i, x in enumerate(t)],
                                   "confidence": "high", "notes": ""})
    empty_notes = json.dumps({"segments": [], "confidence": "low", "notes": "SYNTHETIC: no signing visible"})
    empty_silent = json.dumps({"segments": [], "confidence": "low", "notes": ""})
    bad429 = malformed_with_error_at(429)
    scen = {
        "S1_all_parse": [valid("SYNTHETIC A"), valid("SYNTHETIC B")],
        "S2_R03_recorded": [raw0, raw1],
        "S3_all_malformed": [raw0, raw0],
        "S4_valid_no_signing_with_notes": [empty_notes, empty_notes],
        "S4b_valid_no_signing_without_notes": [empty_silent, empty_silent],
        "S5_all_transport": [ConnectionError("SYNTHETIC connection reset"), TimeoutError("SYNTHETIC timeout")],
        "S5b_one_transport_one_valid": [ConnectionError("SYNTHETIC connection reset"), valid("SYNTHETIC B")],
        "S6_top_level_array": ["[]", valid("SYNTHETIC B")],
        "S7_parse_error_message_contains_429": [bad429, bad429],
        "S8_segment_missing_end": [json.dumps({"segments": [{"start": 1.0, "text": "SYNTHETIC dropped"},
                                                            {"start": 2.0, "end": 2.5, "text": "SYNTHETIC kept"}]}),
                                   valid("SYNTHETIC B")],
    }
    res["current_production_scenarios"] = {k: {kk: vv for kk, vv in e2e(prod, state, video, v).items()
                                               if kk != "timestamps"} for k, v in scen.items()}

    # 4. syntactic repair search on the malformed batch
    n_var, grammar, schema = repair_search(raw0)
    (tree, edits), = schema.items() if len(schema) == 1 else ((None, []),)
    rec = {"single_edit_variants_tested": n_var,
           "grammar_valid_variants": sum(len(v) for v in grammar.values()),
           "grammar_valid_distinct_trees": len(grammar),
           "grammar_valid_trees": [{"n_edits": len(v), "example_edit": list(sorted(v)[0]), **tree_summary(t)}
                                   for t, v in sorted(grammar.items(), key=lambda kv: (-len(kv[1]), kv[0]))],
           "schema_valid_distinct_trees": len(schema)}
    if tree:
        ops = sorted({(op, c) for op, i, c, v in edits})
        positions = sorted(i for op, i, c, v in edits)
        repaired = json.loads(edits[0][3])
        rec.update(schema_valid_edits=[list(o) for o in ops], schema_valid_insert_positions=positions,
                   positions_span_text=raw0[positions[0]:positions[-1]],
                   recovered=repaired,
                   all_recovered_strings_verbatim_in_raw=all(json.dumps(s["text"]) in raw0 for s in repaired["segments"]),
                   all_recovered_numbers_verbatim_in_raw=all(re.search(rf'"{k}": {s[k]}\b', raw0) is not None
                                                             for s in repaired["segments"] for k in ("start", "end")))
    rec["structural_rule_result"] = unique_repair(raw0)[1]
    res["repair_search"] = rec

    # 5. proposed policy on regression fixtures
    u0, u1 = (r03["api_calls"][i]["usage"] for i in (0, 1))
    retry_ok = valid("SYNTHETIC RETRY OK")
    tests = {
        "T1_all_batches_parse": ([[valid("SYNTHETIC A")], [valid("SYNTHETIC B")]], "success"),
        "T2_one_of_two_fails_no_retry_budget": ([[raw0], [raw1]], "partial"),
        "T3_all_batches_fail_parsing": ([[raw0, raw0], [raw0, raw0]], "parse_failure"),
        "T4_valid_no_signing": ([[empty_notes], [empty_silent]], "no_signing_detected"),
        "T5_transport_failure": ([[TransportError("server_5xx"), TransportError("server_5xx")],
                                  [TransportError("timeout"), TransportError("timeout")]], "transport_failure"),
        "T6_retry_succeeds": ([[raw0, retry_ok], [raw1]], "success"),
        "T7_retry_fails_again": ([[raw0, raw0], [raw1]], "partial"),
        "T8_quota_not_retried": ([[TransportError("quota", "RESOURCE_EXHAUSTED spend cap")],
                                  [TransportError("quota", "RESOURCE_EXHAUSTED spend cap")]], "transport_failure"),
        "T9_parse_error_text_429_is_not_quota": ([[bad429, bad429], [bad429, bad429]], "parse_failure"),
        "T10_top_level_array_no_crash": ([["[]", "[]"], [valid("SYNTHETIC B")]], "partial"),
        "T11_rejected_segment_is_partial": ([[json.dumps({"segments": [{"start": 1.0, "text": "SYNTHETIC x"},
                                                                       {"start": 2, "end": 3, "text": "SYNTHETIC y"}]})],
                                             [valid("SYNTHETIC B")]], "partial"),
        "T12_mixed_parse_and_transport": ([[raw0, raw0], [TransportError("timeout"), TransportError("timeout")]],
                                          "transport_failure"),
        "T13_truncated_max_tokens_retried": ([[(raw0[:200], "MAX_TOKENS"), retry_ok], [raw1]], "success"),
        "T14_video_retry_cap": ([[raw0, raw0], [raw0, raw0], [raw0, retry_ok]], "parse_failure"),
    }
    tres = {}
    for name, (batches, expect) in tests.items():
        r = run_policy(batches)
        tres[name] = {"expected": expect, "got": r["status"], "pass": r["status"] == expect,
                      "batches_succeeded": r["batches_succeeded"], "batches_failed": r["batches_failed"],
                      "retry_calls": r["retry_calls"], "quota_exhausted": r["quota_exhausted"]}
    res["policy_tests"] = tres
    assert all(t["pass"] for t in tres.values()), tres

    # R03 under each policy (no retry possible offline: a retry's response is unknown)
    usage0 = (raw0, "STOP", {"tokens": u0["total_token_count"], "latency_s": r03["api_calls"][0]["latency_s"]})
    usage1 = (raw1, "STOP", {"tokens": u1["total_token_count"], "latency_s": r03["api_calls"][1]["latency_s"]})
    res["r03_under_policies"] = {
        "A_current": {"status_reported": "none (indistinguishable from a full success)",
                      "text": rep["text"], "error": rep["error"], "had_transport_error": rep["had_transport_error"],
                      "pipeline": rep["pipeline"]},
        "B_C_explicit_status_no_retry": run_policy([[usage0], [usage1]]),
        "D_repair_fallback": run_policy([[usage0], [usage1]], repair_fallback=True),
    }

    # 6. cost / latency from the 45-case raw records
    calls, per_case = [], {}
    for p in sorted(RAW.glob("R[0-9][0-9].json")):
        d = json.loads(p.read_text())
        per_case[d["review_id"]] = d.get("latency_s")
        for c in d.get("api_calls", []):
            calls.append({"rid": d["review_id"], "tokens": (c.get("usage") or {}).get("total_token_count"),
                          "latency_s": c.get("latency_s"), "parses": TOOLS.parses(c.get("raw_text"))})
    tot = sum(c["tokens"] or 0 for c in calls)
    res["cost_latency"] = {
        "n_cases": len(per_case), "n_calls": len(calls), "parse_failures": sum(not c["parses"] for c in calls),
        "parse_failure_rate": round(sum(not c["parses"] for c in calls) / len(calls), 4),
        "total_tokens_45": tot,
        "r03_calls": [{"batch": i, "tokens": c["usage"]["total_token_count"], "prompt": c["usage"]["prompt_token_count"],
                       "output": c["usage"]["candidates_token_count"], "thoughts": c["usage"]["thoughts_token_count"],
                       "latency_s": c["latency_s"]} for i, c in enumerate(r03["api_calls"])],
        "r03_case_latency_s": r03["latency_s"],
        "estimate_r03_batch_retry": {"extra_calls": 1, "extra_tokens_if_like_original": u0["total_token_count"],
                                     "extra_latency_s_if_like_original": r03["api_calls"][0]["latency_s"],
                                     "whole_video_retry_tokens": u0["total_token_count"] + u1["total_token_count"]},
        "estimate_45_case_run_overhead_tokens_pct": round(100 * u0["total_token_count"] / tot, 2),
    }

    # 7. score sensitivity (descriptive only; the reported score is NOT changed)
    scores = json.loads((EVAL / "production_45/production_45_scores.json").read_text())
    rows = [c for c in scores["cases"] if c["production_status"] in ("ok", "empty", "no_signing_detected")]
    base = TOOLS.corpus([c["production_output"] for c in rows], [c["reference"] for c in rows])
    assert base == scores["summary"]["corpus_scored_cases"]["production"], "cannot reproduce saved 45-case score"
    hyp = e2e(prod, state, video, [json.dumps(res["repair_search"]["recovered"]), raw1])["text"]
    hyps = [hyp if c["review_id"] == "R03" else c["production_output"] for c in rows]
    r03ref = next(c["reference"] for c in rows if c["review_id"] == "R03")
    res["score_sensitivity_descriptive_only"] = {
        "reported_corpus": base,
        "hypothetical_r03_text_if_recovered_batch_kept": hyp,
        "r03_sentence_reported": TOOLS.sent(r03["output_text_raw"], r03ref),
        "r03_sentence_hypothetical": TOOLS.sent(hyp, r03ref),
        "hypothetical_corpus": TOOLS.corpus(hyps, [c["reference"] for c in rows]),
        "note": "what production actually returned stays the scored output; this only sizes the policy's effect",
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"parser_replay": [(r["outcome"], r.get("message")) for r in res["parser_replay"]],
                      "e2e": {k: rep[k] for k in ("text", "error", "had_transport_error", "timestamps_equal_recorded",
                                                  "batch_sizes_equal_recorded", "text_equals_recorded")},
                      "repair": {k: rec[k] for k in ("grammar_valid_distinct_trees", "schema_valid_distinct_trees",
                                                     "structural_rule_result")},
                      "tests_pass": sum(t["pass"] for t in tres.values()), "tests": len(tres)}, indent=1))


if __name__ == "__main__":
    main()
