#!/usr/bin/env python3
"""P0-2 Round 1 run harness: same-input Gemini (production) vs OpenAI gpt-6.1-sol on the frozen 24-case pilot.

Consumes the frozen pre-registration and subset manifest; never re-selects cases or frames.

Both arms run the production entry point `transcribe_asl()` from curify-studio 4220e03c, loaded read-only and
sha-checked. Only these are replaced, as pre-registered (protocol.harness):
  - `app.services.imagen_service`: stub mirroring production's client accessor (as run_production_45.py);
  - `_extract_frames`: returns the frozen JPEGs under production's own file names after asserting that production's
    probe/allocation chose exactly the frozen timestamps and that every byte hash matches;
  - `_call_vlm_openai` (arm O only): Responses API adapter for the frozen model;
  - `_call_vlm` is wrapped pass-through (arm G) to record the R03-aware batch outcome; production parsing unchanged.
Everything else (batch loop, segment parsing, empty filter, sort, dedup, degenerate flag) is production code.

Modes:
  --self-test   static tests (parser equivalence, status rules, error classes); no network, no key.
  --dry-run     builds all 29 + 29 requests through production code and the real SDKs, captured at the HTTP
                transport (never sent); a socket guard fails on any connection attempt; no key is loaded.
  --execute     real primary run. Refused unless a capability smoke record verifies the image-detail setting.
  --retry-view  separate, disabled by default: one retry per primary transport_failure batch, other batches replayed
                from stored primary raw responses. Never mixed into the primary result.

Harness choices frozen before execution (approved 2026-10-29; protocol.harness_choices_frozen_2026_10_29):
  - call order: even hash parity -> Gemini first (12 cases), odd -> OpenAI first (12 cases);
  - HTTP 400/422: run_blocking configuration error, halt immediately, never a transport_failure;
  - a reply that is not a JSON object: parse_failure, case kept in the denominator, run continues,
    production_would_crash = true recorded on the batch.

Credentials: only OPENAI_API_KEY and GEMINI_API_KEY are read from --env-file, passed straight to the SDK clients,
never put in os.environ, never printed, never written.

usage:
  python -I p0_2_same_input_comparison.py --self-test --prod-src FILE
  python -I p0_2_same_input_comparison.py --dry-run --prod-src FILE --frames-dir DIR --videos-dir DIR
  python -I p0_2_same_input_comparison.py --execute --capability-smoke FILE --env-file FILE ...   (BLOCKED)
"""
from __future__ import annotations

import argparse, base64, datetime as dt, hashlib, importlib.util, json, re, shutil, socket, sys, time, types
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
PREREG = RESULTS / "p0_2_openai_preregistration.json"
MANIFEST = RESULTS / "p0_2_subset_manifest.json"
OUT = RESULTS / "p0_2_same_input"                     # manifest.json, gemini/, openai/, comparison.json (later)
MANIFEST_SHA = "b3310230a0e2cb42247c8b0db852742fcd1d1f89cf9e707af2f3d33a0bbcf396"
PROD_SHA = "90df95635fcb3297e2c2b0cd6bf15061d398f9ae2ea3c66543b982487c59ffa5"
PROMPT_SHA = "ea8c5cb130d41c9a7bb2de0b567ba2c99ebf4ea8658c962ec855ed2be6477dda"
OPENAI_MODEL = "gpt-6.1-sol"
GEMINI_MODEL = "gemini-2.5-flash"
SALT = "P0-2-R1-2026-10-28"
EXPECT = {"cases": 24, "frames": 656, "batches": 29, "reserve": 23}
PILOT_IDS = [
    "-g0sqksgyc4_3-2-rgb_front", "FZCEymcpq7I_14-1-rgb_front", "FZd8Iv9ACVw_12-8-rgb_front",
    "Fz-N1S0swh8_2-8-rgb_front", "FzAIlhumvMA_4-2-rgb_front", "FzQPg4aqNYc_13-1-rgb_front",
    "FzoUVr98JmQ_6-8-rgb_front", "G05uFub3YFc_9-2-rgb_front", "G1hb5HugzVk_2-8-rgb_front",
    "G23G21G49dk_14-2-rgb_front", "G2T2WCuU39Y_5-10-rgb_front", "G3FhmHz_7hs_20-10-rgb_front",
    "fzOH00UZg84_30-8-rgb_front", "fzcsY2gm7t0_8-8-rgb_front", "fzrJBu2qsM8_5-10-rgb_front",
    "fzueHkUDyhE_1-8-rgb_front", "g0Abwige7MQ_2-8-rgb_front", "g1HvmBOR7Y4_15-3-rgb_front",
    "g1vUH8Iy4vw_8-3-rgb_front", "g1z6HOJ0yRw_2-3-rgb_front", "g2ELiaFjKfs_3-10-rgb_front",
    "g2QdwYqm8pg_13-3-rgb_front", "g3jQ5ecjGz8_6-3-rgb_front", "g3ushtMfLiY_2-3-rgb_front"]
GEMINI_TIMEOUT_MS = 60_000                                                   # production imagen_service
QUOTA_TOKENS = ("RESOURCE_EXHAUSTED", "429", "spend cap", "quota", "QUOTA")   # production imagen_service
OPENAI_TIMEOUT_S = 60
OPENAI_PRICE_PER_1M = {"input": 2.0, "cached_input": 0.10, "output": 10.0}     # docs 2026-10-29; ESTIMATE ONLY
RECIPE_KEYS = ("PROBE_FPS", "PROBE_WIDTH", "TARGET_FRAMES_PER_SEC", "MIN_FRAME_BUDGET", "MAX_FRAME_BUDGET",
               "DENSITY_FLOOR_FPS", "KEYFRAME_WIDTH", "MIN_FRAMES_PER_RUN", "BATCH_SIZE", "IDLE_QUANTILE",
               "ABS_MOTION_FLOOR", "DEDUP_MAX_GAP_S", "DEGENERATE_REPEAT_COUNT")
BATCH_OUTCOMES = ("ok", "valid_empty", "parse_failure", "transport_failure", "run_blocking")
CASE_STATUSES = ("success", "partial", "no_signing_detected", "parse_failure", "transport_failure")
SECRET_RE = re.compile(r"(sk-[A-Za-z0-9_\-*.]{6,}|AIza[0-9A-Za-z_\-]{10,}|Bearer\s+\S+)")


class Refused(SystemExit):
    """A frozen-input or configuration check failed: nothing is sent."""


class RunBlocking(BaseException):
    """Auth / model-not-found / quota / request-rejected: halts the whole run (escapes production's except)."""


class ModelMismatch(BaseException):
    """Returned model id differs from the frozen id: the run is invalid."""


class Captured(Exception):
    """Dry run: the serialized HTTP request was captured at the transport and not sent."""


class BatchParseFailure(Exception):
    """Parsed reply is not a JSON object (production would crash on data.get); recorded as parse_failure."""


def sha256b(b):
    return hashlib.sha256(b).hexdigest()


def shs(s):
    return sha256b(s.encode())


def scrub(s, n=200):
    return SECRET_RE.sub("[REDACTED]", str(s))[:n]


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def refuse(msg):
    raise Refused(f"REFUSED: {msg}")


# ---- network guard ------------------------------------------------------------------------------------------------
GUARD = {"installed": False, "attempts": []}


def install_network_guard():
    def blocked(name):
        def f(*a, **k):
            GUARD["attempts"].append(name)
            raise ConnectionRefusedError(f"network guard: {name} blocked in dry-run/self-test")
        return f
    socket.socket.connect = blocked("socket.connect")
    socket.socket.connect_ex = blocked("socket.connect_ex")
    socket.create_connection = blocked("socket.create_connection")
    socket.getaddrinfo = blocked("socket.getaddrinfo")
    GUARD["installed"] = True
    try:                                                           # prove the guard trips, then reset the counter
        socket.create_connection(("127.0.0.1", 9), timeout=1)
        refuse("network guard did not trip")
    except ConnectionRefusedError:
        pass
    GUARD["self_test_tripped"] = GUARD["attempts"] == ["socket.create_connection"]
    GUARD["attempts"].clear()


# ---- frozen inputs ------------------------------------------------------------------------------------------------
def load_frozen(frames_dir: Path | None):
    if sha256b(MANIFEST.read_bytes()) != MANIFEST_SHA:
        refuse("subset manifest sha256 differs from the frozen manifest")
    pre, man = json.loads(PREREG.read_text()), json.loads(MANIFEST.read_text())
    sel, prod, proto = pre["selection"], pre["production"], pre["protocol"]
    cases = man["pilot_frame_manifest"]
    if sorted(sel["pilot_ids"]) != sorted(PILOT_IDS) or [c["clip_id"] for c in cases] != sorted(PILOT_IDS):
        refuse("pilot IDs differ from the frozen 24")
    if len(sel["reserve_ids"]) != EXPECT["reserve"] or set(sel["reserve_ids"]) & set(PILOT_IDS):
        refuse("reserve IDs differ from the frozen 23")
    if prod["file_sha256"] != PROD_SHA or prod["prompt_sha256"] != PROMPT_SHA or prod["gemini_model"] != GEMINI_MODEL:
        refuse("production file / prompt / Gemini model differs from the pre-registration")
    om = proto["openai_model"]
    if om.get("status") != "FROZEN" or om.get("model_id") != OPENAI_MODEL:
        refuse(f"pre-registered OpenAI model is not FROZEN as {OPENAI_MODEL}")
    n_frames = sum(c["n_frames"] for c in cases); n_batches = sum(c["n_batches"] for c in cases)
    if (len(cases), n_frames, n_batches) != (EXPECT["cases"], EXPECT["frames"], EXPECT["batches"]):
        refuse(f"expected counts {EXPECT}, got cases={len(cases)} frames={n_frames} batches={n_batches}")
    checked = 0
    for c in cases:
        if len(c["frames"]) != c["n_frames"] or len(c["timestamps_s"]) != c["n_frames"]:
            refuse(f"{c['clip_id']}: frame/timestamp count mismatch")
        for i, (f, t) in enumerate(zip(c["frames"], c["timestamps_s"])):
            if f["file"] != f"f_{i:04d}_{t:07.2f}.jpg" or f["label"] != f"[t={float(f['file'][7:-4]):.2f}s]":
                refuse(f"{c['clip_id']}: frame {i} name/label does not follow production naming")
            if frames_dir is not None:
                p = frames_dir / c["clip_id"] / f["file"]
                if not p.exists() or sha256b(p.read_bytes()) != f["sha256"]:
                    refuse(f"{c['clip_id']}: frozen frame hash mismatch at {f['file']}")
                checked += 1
        for b in c["batches"]:
            bf = c["frames"][b["batch_index"] * 24:(b["batch_index"] + 1) * 24]
            if b["input_sha256"] != batch_hash([(f["label"], f["sha256"]) for f in bf]):
                refuse(f"{c['clip_id']}: batch {b['batch_index']} input hash mismatch")
    return pre, cases, checked


def batch_hash(label_sha_pairs):
    return shs(PROMPT_SHA + "".join(l + s for l, s in label_sha_pairs))


# ---- production module --------------------------------------------------------------------------------------------
def install_stub(state):
    app = types.ModuleType("app"); app.__path__ = []
    services = types.ModuleType("app.services"); services.__path__ = []
    utils = types.ModuleType("app.utils"); utils.__path__ = []
    stub = types.ModuleType("app.services.imagen_service")
    stub.is_quota_exhausted = lambda exc: any(tok in str(exc) for tok in QUOTA_TOKENS)
    stub.get_gemini_client = lambda: state["gemini_client"]()
    sys.modules.update({"app": app, "app.services": services, "app.utils": utils, "app.services.imagen_service": stub})


def load_production(path: Path, recipe: dict):
    if sha256b(path.read_bytes()) != PROD_SHA:
        refuse("production asl_utils.py export does not match 4220e03c")
    spec = importlib.util.spec_from_file_location("app.utils.asl_utils", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["app.utils.asl_utils"] = mod
    spec.loader.exec_module(mod)
    if shs(mod._PROMPT) != PROMPT_SHA:
        refuse("production prompt hash differs")
    if mod.ASL_MODEL != GEMINI_MODEL or mod.ASL_TEMPERATURE != 0.0:
        refuse("production Gemini model/temperature differs")
    if recipe is not None and {k: getattr(mod, k) for k in RECIPE_KEYS} != recipe:
        refuse("production input recipe differs from the frozen pre-registration")
    return mod


def prod_parse(raw):
    """Production _call_vlm parsing, verbatim semantics (equivalence is checked in --self-test)."""
    raw = (raw or "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.S)
        if m:
            return json.loads(m.group(0))
        raise


def segment_counts(data):
    """Production's segment acceptance rule (transcribe_asl loop + empty filter)."""
    good = rejected = 0
    for s in data.get("segments", []):
        try:
            seg = (float(s["start"]), float(s["end"]), str(s.get("text", "")).strip())
        except (KeyError, TypeError, ValueError, AttributeError):
            rejected += 1; continue
        good += bool(seg[2])
    return good, rejected


# ---- error classification -----------------------------------------------------------------------------------------
def classify_error(provider, e):
    """-> (batch outcome, failure category). run_blocking halts the run."""
    name = type(e).__name__
    if provider == "openai":
        import openai
        if isinstance(e, (openai.AuthenticationError, openai.PermissionDeniedError)):
            return "run_blocking", "auth"
        if isinstance(e, openai.NotFoundError):
            return "run_blocking", "model_not_found"
        if isinstance(e, openai.RateLimitError):
            code = (e.body or {}).get("code") if isinstance(e.body, dict) else None
            return ("run_blocking", "insufficient_quota") if code == "insufficient_quota" or "insufficient_quota" \
                in str(e) else ("transport_failure", "rate_limit_429")
        if isinstance(e, (openai.BadRequestError, openai.UnprocessableEntityError)):
            return "run_blocking", "request_rejected_400_config"
        if isinstance(e, openai.APITimeoutError):
            return "transport_failure", "timeout"
        if isinstance(e, openai.APIConnectionError):
            return "transport_failure", "connection"
        if isinstance(e, openai.APIStatusError):
            return "transport_failure", f"http_{e.status_code}"
        return "transport_failure", f"exception_{name}"
    from google.genai import errors as gerr
    if isinstance(e, gerr.APIError):
        code, msg = getattr(e, "code", None), str(e).lower()
        if code in (401, 403):
            return "run_blocking", "auth"
        if code == 404:
            return "run_blocking", "model_not_found"
        if code == 429:
            return ("run_blocking", "spend_cap_or_quota") if any(t in msg for t in ("spending cap", "spend cap",
                                                                                    "billing")) \
                else ("transport_failure", "rate_limit_429")
        if code in (400, 422):
            return "run_blocking", "request_rejected_400_config"
        return "transport_failure", f"http_{code}"
    return "transport_failure", f"exception_{name}"


def case_status(outcomes, n_segments):
    """Pre-registered case status from batch outcomes (protocol.case_status)."""
    assert all(o in BATCH_OUTCOMES[:4] for o in outcomes)
    failed = [o for o in outcomes if o not in ("ok", "valid_empty")]
    if not failed:
        s = "success" if n_segments else "no_signing_detected"
    elif n_segments:
        s = "partial"                                              # never success
    elif "parse_failure" in failed:
        s = "parse_failure"
    else:
        s = "transport_failure"
    assert not (s == "success" and failed)
    return s


def openai_cost(u):
    if not u or u.get("input_tokens") is None:
        return None
    cached = u.get("cached_input_tokens") or 0
    p = OPENAI_PRICE_PER_1M
    return round(((u["input_tokens"] - cached) * p["input"] + cached * p["cached_input"]
                  + (u.get("output_tokens") or 0) * p["output"]) / 1e6, 6)


# ---- request content extraction (same-input proof) ----------------------------------------------------------------
def gemini_parts_sequence(parts):
    """gtypes parts (pre-send) -> (prompt, [(label, image_sha256)])."""
    texts, seq, pending = [], [], None
    for p in parts:
        if getattr(p, "inline_data", None) is not None:
            assert p.inline_data.mime_type == "image/jpeg" and pending is not None
            seq.append((pending, sha256b(p.inline_data.data))); pending = None
        else:
            texts.append(p.text); pending = p.text if len(texts) > 1 else None
    return texts[0], seq


def gemini_body_sequence(body):
    parts = body["contents"][0]["parts"]
    out, pending = [], None
    for p in parts[1:]:
        if "text" in p:
            pending = p["text"]
        else:
            d = p.get("inlineData") or p.get("inline_data")
            data = d["data"]                                         # genai serializes url-safe base64
            out.append((pending, sha256b(base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))))); pending = None
    return parts[0]["text"], out


def openai_content_sequence(content):
    out, pending = [], None
    for p in content[1:]:
        if p["type"] == "input_text":
            pending = p["text"]
        else:
            assert p["type"] == "input_image"
            url = p["image_url"]; assert url.startswith("data:image/jpeg;base64,")
            out.append((pending, sha256b(base64.b64decode(url.split(",", 1)[1])))); pending = None
    return content[0]["text"], out


# ---- arm runner ---------------------------------------------------------------------------------------------------
class Arm:
    """Runs transcribe_asl for one provider with recording wrappers; one instance per (provider, mode)."""

    def __init__(self, prod, provider, mode, detail, keys, capture_log, replay=None):
        self.prod, self.provider, self.mode, self.detail = prod, provider, mode, detail
        self.keys, self.capture_log, self.replay = keys, capture_log, replay or {}
        self.case = None; self.batch = 0; self.records = []; self._client = None; self._oa = None
        self.real_call_vlm = prod._call_vlm                         # captured once: wrappers never nest

    # transports ------------------------------------------------------------------------------------------------
    def _capture_transport(self):
        import httpx
        arm = self

        class Cap(httpx.BaseTransport):
            def handle_request(self, req):
                body = json.loads(req.content)
                arm.capture_log.append({"provider": arm.provider, "clip_id": arm.case["clip_id"],
                                        "batch_index": arm.batch, "method": req.method, "path": req.url.path,
                                        "body": body})
                raise Captured("dry run: request captured at transport, not sent")
        return httpx.Client(transport=Cap())

    def gemini_client(self):
        if self._client is None:
            from google import genai
            from google.genai import types as gt
            if self.mode == "dry_run":
                c = genai.Client(api_key="DRY-RUN-NO-KEY", http_options=gt.HttpOptions(
                    timeout=GEMINI_TIMEOUT_MS, httpx_client=self._capture_transport()))
            else:
                try:                                              # production _get_genai_client
                    c = genai.Client(api_key=self.keys["GEMINI_API_KEY"],
                                     http_options=gt.HttpOptions(timeout=GEMINI_TIMEOUT_MS))
                except Exception:
                    c = genai.Client(api_key=self.keys["GEMINI_API_KEY"])
            real = c.models.generate_content
            arm = self

            def recorded(*a, **kw):
                rec = arm.records[-1]
                prompt, seq = gemini_parts_sequence(kw["contents"][0].parts)
                arm.check_batch(prompt, seq, rec)
                cfg = kw.get("config")
                rec["request"] = {"model": kw.get("model"), "n_parts": len(kw["contents"][0].parts),
                                  "response_mime_type": getattr(cfg, "response_mime_type", None),
                                  "temperature": getattr(cfg, "temperature", None),
                                  "thinking_config": getattr(cfg, "thinking_config", None)}
                if arm.key() in arm.replay:
                    rec["replayed_from_primary"] = True
                    return types.SimpleNamespace(text=arm.replay[arm.key()])
                t0 = time.perf_counter(); rec["call_utc"] = now(); rec["api_attempted"] = True
                resp = real(*a, **kw)
                rec["latency_s"] = round(time.perf_counter() - t0, 3); rec["api_ok"] = True
                um = getattr(resp, "usage_metadata", None)
                cand = (getattr(resp, "candidates", None) or [None])[0]
                g = lambda k: getattr(um, k, None) if um else None
                rec.update(model_returned=getattr(resp, "model_version", None),
                           response_id=getattr(resp, "response_id", None),
                           finish=str(getattr(cand, "finish_reason", None)) if cand else None,
                           usage={"input_tokens": g("prompt_token_count"),
                                  "cached_input_tokens": g("cached_content_token_count"),
                                  "output_tokens": g("candidates_token_count"),
                                  "reasoning_tokens": g("thoughts_token_count"),
                                  "total_tokens": g("total_token_count")},
                           est_cost_usd=None, raw_text=resp.text,
                           raw_response=resp.model_dump(mode="json", exclude_none=True,
                                                        exclude={"sdk_http_response",
                                                                 "automatic_function_calling_history"}))
                rec["model_version_matches"] = str(rec["model_returned"] or "").startswith(GEMINI_MODEL)
                return resp
            c.models.generate_content = recorded
            self._client = c
        return self._client

    def openai_client(self):
        if self._oa is None:
            import openai
            if self.mode == "dry_run":
                self._oa = openai.OpenAI(api_key="DRY-RUN-NO-KEY", timeout=OPENAI_TIMEOUT_S, max_retries=0,
                                         http_client=self._capture_transport())
            else:
                self._oa = openai.OpenAI(api_key=self.keys["OPENAI_API_KEY"], timeout=OPENAI_TIMEOUT_S,
                                         max_retries=0)
        return self._oa

    # request builders ------------------------------------------------------------------------------------------
    def openai_request(self, frame_paths):
        content = [{"type": "input_text", "text": self.prod._PROMPT}]
        for p in frame_paths:                                          # production label source, same order
            ts = float(re.search(r"_(\d+\.\d+)\.jpg$", p).group(1))
            content.append({"type": "input_text", "text": f"[t={ts:.2f}s]"})
            b64 = base64.b64encode(Path(p).read_bytes()).decode()
            content.append({"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}",
                            "detail": self.detail})
        return {"model": OPENAI_MODEL, "input": [{"role": "user", "content": content}],
                "text": {"format": {"type": "json_object"}}, "store": False}

    def call_openai(self, frame_paths):
        """Replacement for production _call_vlm_openai: same contract (frame paths in, parsed dict out)."""
        rec = self.records[-1]
        kw = self.openai_request(frame_paths)
        prompt, seq = openai_content_sequence(kw["input"][0]["content"])
        self.check_batch(prompt, seq, rec)
        rec["request"] = {"model": kw["model"], "endpoint": "POST /v1/responses", "n_content_parts":
                          len(kw["input"][0]["content"]), "detail": self.detail, "text_format": "json_object",
                          "store": False, "temperature": "omitted", "reasoning": "omitted (model default)",
                          "timeout_s": OPENAI_TIMEOUT_S, "sdk_max_retries": 0}
        if self.key() in self.replay:
            rec["replayed_from_primary"] = True
            raw = self.replay[self.key()]
        else:
            t0 = time.perf_counter(); rec["call_utc"] = now(); rec["api_attempted"] = True
            resp = self.openai_client().responses.create(**kw)
            rec["latency_s"] = round(time.perf_counter() - t0, 3); rec["api_ok"] = True
            u = resp.usage
            rec.update(model_returned=resp.model, response_id=resp.id, finish=resp.status,
                       incomplete_reason=getattr(resp.incomplete_details, "reason", None),
                       reasoning_effort=getattr(resp.reasoning, "effort", None),
                       usage={"input_tokens": getattr(u, "input_tokens", None),
                              "cached_input_tokens": getattr(getattr(u, "input_tokens_details", None),
                                                             "cached_tokens", None),
                              "output_tokens": getattr(u, "output_tokens", None),
                              "reasoning_tokens": getattr(getattr(u, "output_tokens_details", None),
                                                          "reasoning_tokens", None),
                              "total_tokens": getattr(u, "total_tokens", None)},
                       raw_response=resp.model_dump(mode="json", exclude_none=True))
            rec["est_cost_usd"] = openai_cost(rec["usage"])
            if resp.model != OPENAI_MODEL:
                rec["model_mismatch"] = True
                raise ModelMismatch(f"returned model {resp.model!r} != frozen {OPENAI_MODEL!r}")
            texts, refusal = [], False
            for item in resp.output or []:
                if getattr(item, "type", None) == "message":
                    for c in item.content or []:
                        if c.type == "output_text":
                            texts.append(c.text)
                        elif c.type == "refusal":
                            refusal = True
            raw = "".join(texts); rec["refusal"] = refusal; rec["raw_text"] = raw
            if not raw:
                raise BatchParseFailure("no output text (refusal, null or incomplete)")
        return prod_parse(raw)

    def key(self):
        return (self.provider, self.case["clip_id"], self.batch)

    # same-input check ------------------------------------------------------------------------------------------
    def check_batch(self, prompt, seq, rec):
        b = self.case["batches"][self.batch]
        fr = self.case["frames"][self.batch * 24:(self.batch + 1) * 24]
        if shs(prompt) != PROMPT_SHA:
            raise RunBlocking("prompt hash mismatch in outgoing request")
        if [l for l, _ in seq] != [f["label"] for f in fr] or [s for _, s in seq] != [f["sha256"] for f in fr]:
            raise RunBlocking(f"outgoing request differs from frozen batch {self.batch} (labels/bytes/order)")
        if len(seq) != b["n_frames"] or batch_hash(seq) != b["input_sha256"]:
            raise RunBlocking(f"batch {self.batch} input hash mismatch")
        rec["same_input_verified"] = True

    # production hooks ------------------------------------------------------------------------------------------
    def install(self, frames_dir):
        prod, arm = self.prod, self
        real_call_vlm = self.real_call_vlm

        def extract(video_path, stamps, outdir):
            c = arm.case
            if [round(t, 6) for t in stamps] != c["timestamps_s"]:
                raise RunBlocking(f"{c['clip_id']}: production chose timestamps that differ from the frozen set")
            paths = []
            for i, (t, f) in enumerate(zip(stamps, c["frames"])):
                name = f"f_{i:04d}_{t:07.2f}.jpg"
                if name != f["file"]:
                    raise RunBlocking(f"{c['clip_id']}: production frame name differs: {name}")
                dst = Path(outdir) / name
                shutil.copyfile(frames_dir / c["clip_id"] / name, dst)
                if sha256b(dst.read_bytes()) != f["sha256"]:
                    raise RunBlocking(f"{c['clip_id']}: frozen frame bytes changed: {name}")
                paths.append(str(dst))
            return paths

        def batch_call(call):
            def wrapped(frame_paths, *a):
                arm.batch = len(arm.records)
                rec = {"provider": arm.provider, "mode": arm.mode, "clip_id": arm.case["clip_id"],
                       "batch_index": arm.batch, "n_frames": len(frame_paths),
                       "frame_sha256": [f["sha256"] for f in arm.case["frames"][arm.batch * 24:arm.batch * 24
                                                                                 + len(frame_paths)]],
                       "batch_input_sha256": arm.case["batches"][arm.batch]["input_sha256"],
                       "model_requested": OPENAI_MODEL if arm.provider == "openai" else GEMINI_MODEL,
                       "model_returned": None, "usage": None, "latency_s": None, "est_cost_usd": None,
                       "attempt": 2 if arm.mode == "retry_view" and (arm.provider, arm.case["clip_id"],
                                                                     arm.batch) not in arm.replay else 1,
                       "api_attempted": False, "api_ok": False, "outcome": None, "failure_category": None}
                arm.records.append(rec)
                try:
                    data = call(frame_paths, *a)
                except (RunBlocking, ModelMismatch):
                    rec["outcome"] = "run_blocking"; raise
                except Captured:
                    rec.update(outcome="dry_run_captured", failure_category=None)
                    raise
                except BatchParseFailure as e:
                    rec.update(outcome="parse_failure", failure_category="no_output_text", error=scrub(e))
                    raise
                except Exception as e:
                    if rec["api_ok"] or rec.get("replayed_from_primary"):           # reply came back; parser failed
                        rec.update(outcome="parse_failure", failure_category="malformed_json",
                                   error_class=type(e).__name__, error=scrub(e))
                    else:
                        out, cat = classify_error(arm.provider, e)
                        rec.update(outcome=out, failure_category=cat, error_class=type(e).__name__, error=scrub(e))
                        if out == "run_blocking":
                            raise RunBlocking(f"{cat}: {scrub(e)}") from None
                    raise
                if not isinstance(data, dict):
                    rec.update(outcome="parse_failure", failure_category="schema_top_level_not_object",
                               production_would_crash=True)
                    raise BatchParseFailure("parsed reply is not a JSON object")
                good, rejected = segment_counts(data)
                rec.update(outcome="ok" if good else "valid_empty", n_valid_segments=good,
                           n_rejected_segments=rejected)
                return data
            return wrapped

        prod._extract_frames = extract
        if self.provider == "gemini":
            prod._call_vlm = batch_call(real_call_vlm)
        else:
            prod._call_vlm_openai = batch_call(self.call_openai)
        return None

    def run_case(self, case, frames_dir, video):
        self.case, self.records = case, []
        t0 = time.perf_counter()
        res = self.prod.transcribe_asl(str(video), provider=self.provider)
        outcomes = [r["outcome"] for r in self.records]
        out = {"clip_id": case["clip_id"], "provider": self.provider, "mode": self.mode,
               "n_batches_expected": case["n_batches"], "n_batches_called": len(self.records),
               "wall_s": round(time.perf_counter() - t0, 3), "batches": self.records}
        if len(self.records) != case["n_batches"]:
            raise RunBlocking(f"{case['clip_id']}: {len(self.records)} batches called, {case['n_batches']} frozen")
        if self.mode == "dry_run":
            out["case_status"] = "dry_run_not_scored"
            return out
        out.update(case_status=case_status(outcomes, len(res.segments)), output_text=res.text,
                   segments=[s.to_dict() for s in res.segments], production_error=res.error,
                   quota_exhausted=res.quota_exhausted, had_transport_error=res.had_transport_error,
                   degenerate_repetition=res.degenerate_repetition, low_density=res.low_density,
                   frames_sampled=res.frames_sampled)
        return out


def arm_order(clip_id):
    """Pre-registered call order: parity of sha256(SALT|order|clip_id); even -> gemini first."""
    return ("gemini", "openai") if int(shs(f"{SALT}|order|{clip_id}"), 16) % 2 == 0 else ("openai", "gemini")


# ---- modes --------------------------------------------------------------------------------------------------------
def load_keys(env_file: Path):
    keys = {}
    for line in env_file.read_text().splitlines():
        k, sep, v = line.strip().removeprefix("export ").partition("=")
        if sep and k.strip() in ("OPENAI_API_KEY", "GEMINI_API_KEY"):
            keys[k.strip()] = v.strip().strip("'\"")
    for k in ("OPENAI_API_KEY", "GEMINI_API_KEY"):
        if not keys.get(k):
            refuse(f"{k} not found in --env-file")
    print("OPENAI_API_KEY loaded: yes; GEMINI_API_KEY loaded: yes (values not shown)", flush=True)
    return keys


def check_capability_smoke(path: Path | None, detail):
    if path is None or not path.exists():
        refuse("BLOCKED: image-detail behaviour for gpt-6.1-sol is not verified; the one-image synthetic capability "
               "smoke test must be approved and recorded (--capability-smoke) before --execute")
    s = json.loads(path.read_text())
    if not (s.get("status") == "verified" and s.get("model_returned") == OPENAI_MODEL and s.get("detail") == detail
            and s.get("synthetic_image_only") is True):
        refuse("capability smoke record does not verify this model/detail")


def run(a, mode):
    pre, cases, n_checked = load_frozen(a.frames_dir)
    if n_checked != EXPECT["frames"]:
        refuse(f"{n_checked} frames hash-checked, {EXPECT['frames']} expected")
    keys = {}
    if mode == "dry_run":
        install_network_guard()
    else:
        check_capability_smoke(a.capability_smoke, a.image_detail)
        keys = load_keys(a.env_file)
    state = {}
    install_stub(state)
    prod = load_production(a.prod_src, pre["recipe"])
    for c in cases:
        v = a.videos_dir / f"{c['clip_id']}.mp4"
        if not v.exists() or sha256b(v.read_bytes()) != c["video_sha256"]:
            refuse(f"{c['clip_id']}: source video missing or hash differs")
    capture_log, replay = [], {}
    if mode == "retry_view":
        replay = load_replay()
    arms = {p: Arm(prod, p, mode, a.image_detail, keys, capture_log, replay) for p in ("gemini", "openai")}
    state["gemini_client"] = arms["gemini"].gemini_client
    out_dir = OUT if mode == "primary" else OUT / "retry_view"
    if mode != "dry_run":
        for p in ("gemini", "openai"):
            (out_dir / p / "raw").mkdir(parents=True, exist_ok=True)
        if any(any((out_dir / p).glob("*.json")) for p in ("gemini", "openai")) and not a.resume:
            refuse(f"{out_dir} already has case files; --resume needs explicit approval")
        write_run_manifest(out_dir, mode, a, pre)
    results = {"gemini": [], "openai": []}
    cur = {"arm": None}
    try:
        if mode == "retry_view":
            time.sleep(60)                                         # pre-registered: retry after >= 60 s
        for c in cases:
            for p in arm_order(c["clip_id"]):
                if mode == "retry_view" and (p, c["clip_id"]) not in {k[:2] for k in replay["_retry"]}:
                    continue
                case_file = out_dir / p / f"{c['clip_id']}.json"
                if mode != "dry_run" and case_file.exists():
                    continue
                arm = cur["arm"] = arms[p]
                arm.install(a.frames_dir)
                r = arm.run_case(c, a.frames_dir, a.videos_dir / f"{c['clip_id']}.mp4")
                r["resumed"] = bool(a.resume) if mode != "dry_run" else False
                results[p].append(r)
                if mode != "dry_run":
                    for b in r["batches"]:
                        raw = {k: b.pop(k) for k in ("raw_text", "raw_response") if k in b}
                        if raw:
                            (out_dir / p / "raw" / f"{c['clip_id']}_b{b['batch_index']}.json").write_text(
                                json.dumps(raw, indent=1, ensure_ascii=False))
                    case_file.write_text(json.dumps(r, indent=1, ensure_ascii=False))
                print(p, c["clip_id"], r["case_status"], [b["outcome"] for b in r["batches"]], flush=True)
    except (RunBlocking, ModelMismatch) as e:
        halt = {"halted_utc": now(), "reason_class": type(e).__name__, "reason": scrub(e, 400),
                "note": "run halted; no scoring of an incomplete arm; resume only with user approval",
                "in_flight_case": cur["arm"].case["clip_id"] if cur["arm"] and cur["arm"].case else None,
                "in_flight_batches": [{k: v for k, v in b.items() if k not in ("raw_text", "raw_response")}
                                      for b in (cur["arm"].records if cur["arm"] else [])]}
        if mode != "dry_run":
            (out_dir / "HALTED.json").write_text(json.dumps(halt, indent=1))
        print(json.dumps(halt, indent=1)); sys.exit(2)
    if mode == "dry_run":
        return dry_run_report(results, capture_log, cases, prod)


def load_replay():
    """Retry view: replay every primary batch from stored raw text except primary transport_failure batches."""
    replay, retry = {}, []
    for p in ("gemini", "openai"):
        for f in sorted((OUT / p).glob("*.json")):
            r = json.loads(f.read_text())
            for b in r["batches"]:
                key = (p, r["clip_id"], b["batch_index"])
                if b["outcome"] == "transport_failure":
                    retry.append(key)
                else:
                    rawf = OUT / p / "raw" / f"{r['clip_id']}_b{b['batch_index']}.json"
                    replay[key] = json.loads(rawf.read_text()).get("raw_text") if rawf.exists() else ""
    if not retry:
        refuse("retry view: no primary transport_failure batches")
    replay["_retry"] = retry
    return replay


def write_run_manifest(out_dir, mode, a, pre):
    import openai, google.genai
    (out_dir / "manifest.json").write_text(json.dumps({
        "stage": f"P0-2 Round 1 {mode}", "started_utc": now(), "openai_model": OPENAI_MODEL,
        "gemini_model": GEMINI_MODEL, "image_detail": a.image_detail, "pilot_ids": PILOT_IDS,
        "subset_manifest_sha256": MANIFEST_SHA, "production_file_sha256": PROD_SHA, "prompt_sha256": PROMPT_SHA,
        "sdk": {"openai": openai.__version__, "google-genai": google.genai.__version__,
                "python": sys.version.split()[0]},
        "retries": "none in primary (SDK max_retries=0; genai default no retry)" if mode == "primary"
        else "one retry per primary transport_failure batch; other batches replayed from primary raw",
        "credential_source": "OPENAI_API_KEY and GEMINI_API_KEY from the user-approved env file; values not stored"},
        indent=1))


def dry_run_report(results, capture_log, cases, prod):
    by = {"gemini": [], "openai": []}
    for cap in capture_log:
        by[cap["provider"]].append(cap)
    checks = {}
    for p, caps in by.items():
        ok = 0; meta = []
        for cap in caps:
            c = next(x for x in cases if x["clip_id"] == cap["clip_id"])
            fr = c["frames"][cap["batch_index"] * 24:(cap["batch_index"] + 1) * 24]
            body = cap["body"]
            prompt, seq = gemini_body_sequence(body) if p == "gemini" else \
                openai_content_sequence(body["input"][0]["content"])
            same = (shs(prompt) == PROMPT_SHA and seq == [(f["label"], f["sha256"]) for f in fr]
                    and batch_hash(seq) == c["batches"][cap["batch_index"]]["input_sha256"])
            ok += same
            m = {"clip_id": cap["clip_id"], "batch_index": cap["batch_index"], "method": cap["method"],
                 "path": cap["path"], "n_images": len(seq), "first_label": seq[0][0], "last_label": seq[-1][0],
                 "batch_input_sha256": batch_hash(seq), "serialized_matches_frozen": same}
            if p == "gemini":
                m["generation_config"] = body.get("generationConfig")
                m["top_level_keys"] = sorted(body)
            else:
                m.update(model=body["model"], store=body["store"], text=body["text"],
                         detail=sorted({x["detail"] for x in body["input"][0]["content"] if "detail" in x}),
                         top_level_keys=sorted(body), temperature_sent="temperature" in body,
                         reasoning_sent="reasoning" in body)
            meta.append(m)
        checks[p] = {"requests_constructed": len(caps), "serialized_requests_matching_frozen_input": ok,
                     "requests": meta}
    n_cases = {p: len(v) for p, v in results.items()}
    report = {
        "stage": "P0-2 Round 1 harness DRY RUN (no request sent, no key loaded, no model output)",
        "run_utc": now(), "pilot_cases_loaded": len(cases), "frames_hash_verified": sum(c["n_frames"] for c in cases),
        "cases_run_through_production_transcribe_asl": n_cases,
        "expected": EXPECT, "network_guard": {"installed": GUARD["installed"], "self_test_tripped":
                                             GUARD.get("self_test_tripped"), "connection_attempts":
                                             len(GUARD["attempts"])},
        "prompt_sha256": shs(prod._PROMPT), "requests": checks}
    assert report["network_guard"]["connection_attempts"] == 0
    for p in ("gemini", "openai"):
        assert checks[p]["requests_constructed"] == EXPECT["batches"], (p, checks[p]["requests_constructed"])
        assert checks[p]["serialized_requests_matching_frozen_input"] == EXPECT["batches"]
        assert n_cases[p] == EXPECT["cases"]
    (OUT / "dry_run").mkdir(parents=True, exist_ok=True)
    (OUT / "dry_run" / "dry_run_requests.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "requests"} |
                     {"requests": {p: {k: v for k, v in checks[p].items() if k != "requests"} for p in checks}},
                     indent=1))
    return report


def self_test(a):
    """Static tests only: no network (guard on), no key, no frames sent. Synthetic strings are labelled SYNTHETIC."""
    install_network_guard()
    state = {}
    install_stub(state)
    prod = load_production(a.prod_src, None)
    # 1. parser equivalence with production _call_vlm (fake client returns fixed text)
    fx = ['{"segments":[{"start":0,"end":1,"text":"SYNTHETIC"}]}', 'noise {"segments":[]} tail', '[]', 'not json',
          '{"a":1} x {"b":2}', '', '```json\n{"segments":[]}\n```']
    eq = []
    for raw in fx:
        fake = types.SimpleNamespace(models=types.SimpleNamespace(
            generate_content=lambda **kw: types.SimpleNamespace(text=raw)))
        try:
            p_out = ("ok", prod._call_vlm([], fake))
        except Exception as e:
            p_out = ("err", type(e).__name__)
        try:
            h_out = ("ok", prod_parse(raw))
        except Exception as e:
            h_out = ("err", type(e).__name__)
        eq.append(p_out == h_out)
    # 2. case status rules
    st = {
        "all_ok": case_status(["ok", "ok"], 3) == "success",
        "all_empty": case_status(["valid_empty"], 0) == "no_signing_detected",
        "partial_multibatch_never_success": case_status(["ok", "parse_failure"], 2) == "partial",
        "partial_transport": case_status(["transport_failure", "ok"], 1) == "partial",
        "parse_no_segments": case_status(["parse_failure", "transport_failure"], 0) == "parse_failure",
        "transport_only": case_status(["transport_failure", "valid_empty"], 0) == "transport_failure"}
    # 3. error classification (synthetic SDK exceptions, no request made)
    import httpx, openai
    from google.genai import errors as gerr
    req = httpx.Request("POST", "https://example.invalid/v1/responses")
    mk = lambda cls, code, body=None: cls("SYNTHETIC", response=httpx.Response(code, request=req), body=body)
    cls_ok = {
        "oa_auth": classify_error("openai", mk(openai.AuthenticationError, 401))[0] == "run_blocking",
        "oa_404": classify_error("openai", mk(openai.NotFoundError, 404))[0] == "run_blocking",
        "oa_429_rate": classify_error("openai", mk(openai.RateLimitError, 429, {"code": "rate_limit_exceeded"}))[0]
        == "transport_failure",
        "oa_429_quota": classify_error("openai", mk(openai.RateLimitError, 429, {"code": "insufficient_quota"}))[0]
        == "run_blocking",
        "oa_400": classify_error("openai", mk(openai.BadRequestError, 400))[0] == "run_blocking",
        "oa_500": classify_error("openai", mk(openai.InternalServerError, 500))[0] == "transport_failure",
        "oa_timeout": classify_error("openai", openai.APITimeoutError(request=req))[0] == "transport_failure",
        "g_429_rate": classify_error("gemini", gerr.ClientError(429, {"error": {"message": "SYNTHETIC rate",
                                                                              "status": "RESOURCE_EXHAUSTED"}}))[0]
        == "transport_failure",
        "g_429_cap": classify_error("gemini", gerr.ClientError(429, {"error": {
            "message": "SYNTHETIC project has exceeded its monthly spending cap", "status": "RESOURCE_EXHAUSTED"}}))[0]
        == "run_blocking",
        "g_403": classify_error("gemini", gerr.ClientError(403, {"error": {"message": "SYNTHETIC"}}))[0]
        == "run_blocking",
        "g_503": classify_error("gemini", gerr.ServerError(503, {"error": {"message": "SYNTHETIC"}}))[0]
        == "transport_failure"}
    # 4. scrub and order
    scrub_ok = "sk-" not in scrub("Incorrect API key provided: sk-proj-SYNTHETIC1234567890") and \
        "AIza" not in scrub("key=AIzaSYNTHETIC0123456789")
    orders = [arm_order(c)[0] for c in PILOT_IDS]
    out = {"parser_equivalence_with_production_call_vlm": f"{sum(eq)}/{len(eq)}", "case_status_rules": st,
           "error_classification": cls_ok, "secret_scrub": scrub_ok,
           "arm_order_gemini_first": orders.count("gemini"), "arm_order_openai_first": orders.count("openai"),
           "network_attempts": len(GUARD["attempts"])}
    print(json.dumps(out, indent=1))
    assert all(eq) and all(st.values()) and all(cls_ok.values()) and scrub_ok and not GUARD["attempts"]
    return out


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--self-test", action="store_true"); g.add_argument("--dry-run", action="store_true")
    g.add_argument("--execute", action="store_true"); g.add_argument("--retry-view", action="store_true")
    ap.add_argument("--prod-src", required=True, type=Path, help="asl_utils.py exported from curify-studio 4220e03c")
    ap.add_argument("--frames-dir", type=Path, help="frozen frames (pre-registration pass1 directory)")
    ap.add_argument("--videos-dir", type=Path)
    ap.add_argument("--image-detail", choices=("high", "low", "auto", "original"), default="high",
                    help="pre-registered 'high'; unverified for gpt-6.1-sol until the capability smoke test")
    ap.add_argument("--capability-smoke", type=Path, help="record of the approved one-image synthetic smoke test")
    ap.add_argument("--env-file", type=Path, help="only OPENAI_API_KEY and GEMINI_API_KEY are read")
    ap.add_argument("--resume", action="store_true", help="needs explicit user approval; resumed cases are flagged")
    a = ap.parse_args()
    if a.self_test:
        return self_test(a)
    if not (a.frames_dir and a.videos_dir):
        ap.error("--frames-dir and --videos-dir are required")
    if a.dry_run:
        return run(a, "dry_run")
    if not a.env_file:
        ap.error("--env-file is required for --execute / --retry-view")
    return run(a, "primary" if a.execute else "retry_view")


if __name__ == "__main__":
    main()
