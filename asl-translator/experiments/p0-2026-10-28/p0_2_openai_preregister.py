#!/usr/bin/env python3
"""P0-2 Round 1 pre-registration: same-input OpenAI-vs-Gemini comparison, frozen before any API call (2026-10-28).

No model, no API, no network. CPU only:
  1. inventory   the 128-clip How2Sign v2 benchmark: dev-45 membership, H18/H19 guard, P0-15 sealed final split,
                 local video sha256 vs FREEZE_CHECKSUMS, prior research exposure (committed artifacts that name the clip)
  2. features    production preprocessing ONLY (motion probe, runs, budget, timestamps) on every eligible clip:
                 input-side characteristics, no model output, no reference text
  3. selection   deterministic stratified split of the eligible pool into the Round-1 pilot and a reserve
  4. freeze      production frame extraction for the pilot, run twice (determinism check), per-frame and per-batch
                 hashes, batch partition and timestamp labels
  5. estimates   call counts and token volume (Gemini volume from the committed production_45 usage records)

Production code is loaded read-only from an export of curify-studio 4220e03c and checked by sha256; nothing in it is
changed. Frames are written to --work (scratch) only; the committed outputs hold hashes, never frames or text.

usage: python3 -I p0_2_openai_preregister.py --videos-dir DIR --prod-src FILE --work DIR
"""
import argparse, csv, glob, hashlib, importlib.util, json, re, statistics, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BENCH = REPO / "asl-translator/data/public_benchmarks/how2sign_v2"
CASES45 = REPO / "asl-translator/asl-eval/production_45/production_45_cases.csv"
P45_RAW = REPO / "asl-translator/asl-eval/production_45/raw"
FUSION = REPO / "docs/daily_report/10.16/asl-unisign-high-precision-fusion/split"
GUARD = REPO / "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"
OUT = HERE / "results"
PROD_SHA = "90df95635fcb3297e2c2b0cd6bf15061d398f9ae2ea3c66543b982487c59ffa5"
PROD_COMMIT = "4220e03c0c0c5c4010ddc6ffc8c0d5379d0dc48b"
PROMPT_SHA = "ea8c5cb130d41c9a7bb2de0b567ba2c99ebf4ea8658c962ec855ed2be6477dda"
SALT = "P0-2-R1-2026-10-28"

PROTOCOL = {
    "arms": {
        "G": "production Gemini: asl_utils._call_vlm unchanged (gemini-2.5-flash, temperature 0, response_mime_type "
             "application/json, no thinking config = model default), fed the frozen frames",
        "O": "OpenAI: the same frozen frames, prompt, labels, batch partition and post-processing; only the model "
             "call differs (see openai_request)",
        "G_repeat_optional": "second Gemini pass on the same frames, for a run-to-run noise floor (needs approval)"},
    "harness": "load production asl_utils (sha-checked) read-only; replace only _extract_frames (returns copies of "
               "the frozen JPEGs under production's own file names, asserting the timestamps match) and, for O, "
               "_call_vlm_openai; everything else in transcribe_asl (batch loop, segment parsing, empty filter, sort, "
               "_merge_adjacent_duplicates, _has_degenerate_repetition) runs unchanged for both arms; per-batch "
               "outcomes are recorded by a pass-through wrapper (R03-aware status, production result unchanged)",
    "openai_model": {"status": "FROZEN", "model_id": "gpt-6.1-sol",
                     "frozen_on": "2026-10-29", "verification": "models.retrieve('gpt-6.1-sol') succeeded "
                                                                "2026-10-29T07:19:51Z; returned id 'gpt-6.1-sol'",
                     "preferred": "gpt-6.1-sol", "fallback": "gpt-6-astra (untested, not selected: the preferred "
                                                             "model succeeded, so no fallback check was made)",
                     "excluded_as_primary": "gpt-4o",
                     "snapshot_caveat": "the docs list no dated snapshot; 'gpt-6.1-sol' is the exact id returned, "
                                        "but whether it is a fixed version or an alias is not stated",
                     "requirements": ["exact model ID returned in the response equals the requested ID on every "
                                      "call, or the run is invalid", "image input", "JSON-object output",
                                      "Responses API endpoint", "id and call date recorded per request"],
                     "credential_source": "OPENAI_API_KEY from the user-approved local env file outside the repo "
                                          "(approved 2026-10-29; path not committed; only that variable is loaded; "
                                          "value never printed or stored)",
                     "production_dormant_default": "gpt-4o (asl_utils.OPENAI_ASL_MODEL), detail 'low', Chat "
                                                   "Completions, openai==1.63.2"},
    "openai_verification_2026_10_29": {
        "sdk": {"research_env": "isolated venv outside the repo (temporary session directory); "
                                "production dependencies untouched",
                "python": "3.11.7", "openai": "3.41.0 (pinned: openai==3.41.0)",
                "has_responses_create": True, "has_models_retrieve": True,
                "production_pin": "openai==1.63.2 (curify_background/requirements.txt; predates the Responses API)"},
        "account_access": {
            "method": "client.models.retrieve only (metadata; no generation, no images, no benchmark data); "
                      "max_retries=0, timeout 30 s",
            "gpt-6.1-sol": {"requested": "gpt-6.1-sol", "returned_id": "gpt-6.1-sol", "result": "success",
                            "owned_by": "system", "created": 1790552874,
                            "verified_at_utc": "2026-10-29T07:19:51+00:00"},
            "gpt-6-astra": "NOT CHECKED (fallback only on a model-unavailable error; not needed)"},
        "no_generation_check_limits": "models.retrieve returns only id, created, owned_by: it can confirm access "
                                      "and the exact id, not image input, detail behaviour, temperature or usage "
                                      "fields; those are from the docs until the first real call",
        "docs_read": ["models/gpt-6.1-sol", "models/gpt-6-astra", "models", "guides/images-vision",
                      "guides/reasoning", "guides/structured-outputs"],
        "gpt-6.1-sol": {"snapshot": "only 'gpt-6.1-sol' listed; no dated snapshot; alias vs fixed not stated",
                        "image_input": "yes (text + image in, text out)",
                        "multiple_images": "yes per the vision guide (up to 1,500 images, 512 MB per request)",
                        "responses_api": "supported", "chat_completions": "supported", "batch": "supported",
                        "structured_outputs": "listed; JSON mode not mentioned on the model page",
                        "detail_values": "NOT documented for this model (the vision guide's sizing table does not "
                                         "list gpt-6.1-sol)",
                        "temperature": "not documented",
                        "reasoning_effort": "low, medium, high, xhigh, max; default medium; no 'none'",
                        "context": "1,050,000 (max input 922,000), max output 128,000",
                        "price_per_1M": {"input": 2.0, "cached_input": 0.10, "output": 10.0}},
        "gpt-6-astra": {"snapshot": "only 'gpt-6-astra' listed; no dated snapshot; alias vs fixed not stated",
                        "image_input": "yes", "multiple_images": "yes (same guide limits)",
                        "responses_api": "supported", "chat_completions": "supported",
                        "structured_outputs": "listed; JSON mode not mentioned on the model page",
                        "detail_values": "low (fits 512x512), high (<= 2,500 patches, 65,535 px max), original, "
                                         "auto (= original); 32 px patches, multiplier 1.2",
                        "temperature": "not documented",
                        "reasoning_effort": "low, medium, high, xhigh, max; 'none' returns HTTP 400; default not "
                                            "stated",
                        "context": "1,050,000 (max input 922,000), max output 128,000",
                        "price_per_1M": {"input": 10.0, "cached_input": 1.0, "output": 50.0}},
        "usage_fields_responses_api": ["usage.input_tokens", "usage.input_tokens_details.cached_tokens",
                                       "usage.output_tokens", "usage.output_tokens_details.reasoning_tokens",
                                       "usage.total_tokens"],
        "reasoning_tokens_billed_as": "output tokens"},
    "openai_request": {
        "endpoint": "Responses API, POST /v1/responses (client.responses.create); changed from the production "
                    "dormant path's Chat Completions at the user's direction (2026-10-29)",
        "messages": "input = one user message; content = [input_text: production _PROMPT verbatim] + per frame "
                    "[input_text: '[t=X.XXs]', input_image: image_url data:image/jpeg;base64,<frozen frame bytes>, "
                    "detail 'high']",
        "detail": "high (FROZEN 2026-10-29, verified by the capability smoke test): a 512x288 frame (144 patches) "
                  "is within every documented 'high' budget and is sent unresized; production's dormant 'low' would "
                  "collapse each frame to the base tokens of tile-based models",
        "capability_smoke_2026_10_29": {
            "result": "PASS", "call_utc": "2026-10-29T08:04:00+00:00", "n_inference_calls": 1, "retries": 0,
            "image": "locally generated synthetic 512x288 JPEG (white canvas, one rectangle, one ellipse); no "
                     "photo, no ASL, no pilot/reserve/benchmark content; sha256 469dfe95...",
            "request": "POST /v1/responses; model gpt-6.1-sol; one user message [input_text instruction, input_text "
                       "'[t=0.00s]', input_image data URL detail 'high']; text.format json_object; store false; "
                       "temperature and reasoning omitted; SDK openai==3.41.0, max_retries 0, timeout 60 s",
            "verified": {"request_accepted": True, "model_returned": "gpt-6.1-sol", "image_input": True,
                         "detail_high_accepted": True, "status": "completed", "json_object_output_parsed": True,
                         "refusal": False, "reasoning_effort_reported": "medium"},
            "usage": {"input_tokens": 205, "cached_input_tokens": 0, "output_tokens": 13, "reasoning_tokens": 0,
                      "total_tokens": 218},
            "usage_fields_verified": ["usage.input_tokens", "usage.input_tokens_details.cached_tokens",
                                      "usage.output_tokens", "usage.output_tokens_details.reasoning_tokens",
                                      "usage.total_tokens"],
            "image_token_note": "205 input tokens is consistent with ~173 image tokens (144 patches x 1.2) plus "
                                "~30 text tokens; the API does not report image tokens separately",
            "latency_s": 3.761, "est_cost_usd": 0.00054,
            "est_cost_label": "ESTIMATE ONLY: docs prices read 2026-10-29",
            "answer": "not stored; only JSON-object validity was checked",
            "record": "results/p0_2_same_input/capability_smoke.json"},
        "response_format": "text.format = {type: json_object} (Responses equivalent of JSON mode; no schema, as "
                           "Gemini's application/json mode); the prompt already says 'STRICT JSON'",
        "temperature": "omitted: neither candidate documents temperature support and both are reasoning-only "
                       "(no 'none' effort); recorded as a difference from Gemini's temperature 0",
        "reasoning_effort": "not set (model default; documented as medium for gpt-6.1-sol, not stated for "
                            "gpt-6-astra), as production sets no Gemini thinking config; the effective value is "
                            "recorded from the response",
        "not_set": ["instructions / system message", "max_output_tokens", "seed", "tools", "top_p", "previous "
                    "response id"],
        "store": False,
        "incomplete": "status 'incomplete' is recorded with incomplete_details.reason; any returned text is parsed "
                      "as usual, no text = parse_failure",
        "timeout_s": 60,
        "parser": "production _call_vlm parsing for both arms: json.loads, else the first {...} span, else parse "
                  "failure (the dormant _call_vlm_openai uses json.loads only)",
        "refusal": "a refusal or null content is a parse_failure, with the refusal flag recorded"},
    "unavoidable_api_differences": [
        "different provider, model family, tokenizer and image encoder",
        "Gemini Part.from_text / Part.from_bytes vs OpenAI Responses input_text / input_image data-URL parts "
        "(same order and content)",
        "JSON mode: Gemini response_mime_type application/json vs OpenAI text.format json_object; neither "
        "imposes a schema",
        "image tokens per frame differ (Gemini ~258 observed via usage; OpenAI ~173 documented for 1.2x patch "
        "models) at the same pixels",
        "Gemini temperature 0 with default dynamic thinking; OpenAI temperature omitted with default reasoning "
        "effort (no non-reasoning mode on either candidate)",
        "neither provider guarantees determinism at temperature 0"],
    "no_extra_information": ["no reference text", "no target answer", "no Uni-Sign prediction", "no clip or video "
                             "name", "no ground-truth name", "no scoring hint", "no audio", "no system message"],
    "batch_outcomes": {
        "ok": "parsed dict with at least one valid non-empty segment",
        "valid_empty": "parsed dict with no valid non-empty segment",
        "parse_failure": "response received, not parseable by the production parser (includes refusal/null content)",
        "transport_failure": "the call raised (timeout, connection, 5xx, 429 rate limit)",
        "run_blocking": "auth error, model not found, insufficient quota or spend cap, or HTTP 400/422 request "
                        "configuration error: halt the whole run"},
    "case_status": {
        "success": "every batch ok or valid_empty, and at least one segment",
        "no_signing_detected": "every batch valid_empty",
        "partial": "at least one failed batch and at least one segment (never counted as success)",
        "parse_failure": "no segment, and at least one batch parse_failure",
        "transport_failure": "no segment, and every failed batch transport_failure"},
    "denominator": "all 24 pilot cases in every arm; a case without text is scored as the empty string",
    "retries": {
        "primary": "none: one attempt per batch, as production transcribe_asl",
        "secondary_view": "after the full pass, each transport_failure batch may be retried once after >= 60 s; "
                          "reported only as a separate 'transport-retried' view; retry calls, tokens and latency "
                          "count in cost and latency",
        "never_retried": ["parse_failure", "valid_empty", "no_signing_detected", "ok"],
        "run_blocking": "halt; no scoring of an incomplete arm; resume only with user approval; resumed cases "
                        "flagged"},
    "call_order": "for each pilot case in clip-id order, both arms back to back; which arm goes first = parity of "
                  "sha256('P0-2-R1-2026-10-28|order|'+clip_id)",
    "harness_choices_frozen_2026_10_29": {
        "status": "FROZEN before execution (user-approved harness review, 2026-10-29); must not change after any "
                  "output is seen",
        "harness": "p0_2_same_input_comparison.py",
        "call_order": "even parity of sha256('P0-2-R1-2026-10-28|order|'+clip_id) -> Gemini first, odd -> OpenAI "
                      "first; 12 cases Gemini-first, 12 OpenAI-first",
        "http_400_422": "run_blocking configuration error (request format/config): halt the run immediately; never "
                        "counted as transport_failure; no further calls are spent",
        "non_json_object_response": "a reply that parses but is not a JSON object is a parse_failure; the case stays "
                                    "in the denominator and the run continues with the next batch/case; the batch "
                                    "records production_would_crash = true when the current production parser would "
                                    "crash on it (transcribe_asl calls data.get on the parsed value)"},
    "request_log_fields": ["arm", "requested_model", "returned_model", "call_utc", "clip_id", "batch_index",
                           "n_images", "batch_input_sha256", "input_tokens", "cached_input_tokens", "output_tokens",
                           "reasoning_or_thinking_tokens", "total_tokens", "latency_s", "finish_reason",
                           "response_id", "attempt", "batch_outcome", "error_class", "error_message_200",
                           "raw_response_text"],
    "metrics": {
        "automatic": ["corpus chrF (primary)", "corpus BLEU-4", "WER (lowercase whitespace, x100)",
                      "mean output/reference word-length ratio", "loop_out count (P0-A §1.4)",
                      "degenerate_repetition count", "success / partial / no_signing_detected / parse_failure / "
                      "transport_failure counts", "empty-output count"],
        "implementation": "the P0-A frozen functions (score_repetition.py / production_45_tools.py), sacrebleu defaults",
        "paired": "per-case sentence chrF and WER, O minus G; mean, median, wins/losses/ties (|delta chrF| < 1 = "
                  "tie); 95 % paired bootstrap CI of mean delta sentence chrF, 10,000 resamples, seed 20261028, "
                  "case-level (one clip per source video); sensitivity: signer-proxy cluster bootstrap",
        "regression_gain": "regression = O sentence chrF <= G - 10; gain = O >= G + 10",
        "content_review": {"labels": ["omission of key content", "key-content error (entity, number, action)",
                                      "generic or hallucinated filler", "fingerspelling/name/number rendered "
                                      "correctly (yes/partial/no/NA)"],
                           "procedure": "blind sheet: reference plus the two outputs as X/Y in seeded random order; "
                                        "arm names hidden until labels are locked",
                           "who": "human reviewer; AI pre-annotation, if any, is labelled AI and cannot support "
                                  "verdict A",
                           "automatic_proxy": "an output repeated verbatim on 2+ different clips within an arm "
                                              "(descriptive)"},
        "uni_sign": "committed Uni-Sign predictions for these clips are reported as a separate reference column, "
                    "labelled not input-matched; never paired as 'only the model changed'",
        "not_claimed": "no semantic superiority from automatic metrics; Round 1 can name a candidate, not prove "
                       "semantic correctness (the 2x2 correctness table needs reliable labels)"},
    "decision_rule": {
        "gate_R_reliability": "non-answers (empty + no_signing_detected + parse_failure + transport_failure) "
                              "O <= G + 1, and partial O <= G + 1",
        "gate_Q_quality": "corpus chrF O - G >= +2.0, and paired bootstrap 95 % CI lower bound of mean delta "
                          "sentence chrF > 0, and corpus WER O <= G; if G_repeat ran, also corpus chrF gain > "
                          "|G_repeat - G|",
        "gate_S_safety": "regressions <= gains, and generic/hallucinated outputs O <= G (blind review; automatic "
                         "proxy only if review is absent, which makes the verdict provisional)",
        "gate_C_cost_latency": "median per-call latency O <= 2x G, and total cost O <= 3x G; cost uses token "
                               "counts and prices verified at run time; unverifiable prices leave C unresolved",
        "A_replacement_candidate": "R, Q, S and C all pass, and blind-review key-content errors O <= G; without "
                                   "human review it is 'A provisional'",
        "B_local_specialist_candidate": "not A, R passes, and in at least one pre-specified stratum with >= 5 "
                                        "cases (multi-batch clips; one signer proxy; Gemini non-answer/loop/"
                                        "degenerate cases; Uni-Sign loop_out or empty cases) O has mean delta "
                                        "sentence chrF >= +5 against the stratum's comparator and wins >= 2/3 of "
                                        "its cases",
        "C_pause": "anything else, including any R failure whatever the quality numbers",
        "continue_to_round_2": "A or B only. A -> confirm on the 23 reserve cases with the same frozen recipe plus "
                               "blind review; B -> Round 2 input work limited to that stratum. No production "
                               "change in any case",
        "fixed_before_outputs": "thresholds are fixed here and must not change after any output is seen"}}

sys.path.insert(0, str(GUARD))
from holdout_guard import assert_not_holdout  # noqa: E402


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def shs(s):
    return hashlib.sha256(s.encode()).hexdigest()


def lines(p):
    return [x.strip() for x in open(p) if x.strip()]


def load_prod(path):
    assert sha256(path) == PROD_SHA, "production asl_utils.py export does not match 4220e03c"
    spec = importlib.util.spec_from_file_location("asl_utils_4220e03c", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    assert shs(mod._PROMPT) == PROMPT_SHA
    return mod


def exposure(ids):
    """Committed artifacts (outside the benchmark folder itself) that name each clip id, grouped by study folder."""
    out = subprocess.run(["git", "-C", str(REPO), "grep", "-o", "-F", *sum((["-e", i] for i in ids), []), "--", ".",
                          ":!asl-translator/data/public_benchmarks/how2sign_v2"], capture_output=True, text=True).stdout
    exp = {i: set() for i in ids}
    for ln in out.splitlines():
        path, _, hit = ln.rpartition(":")
        p = path.split("/")
        key = "/".join(p[:4]) if p[0] == "docs" else "/".join(p[:3] if p[1] != "evaluation" else p[:4])
        if hit in exp:
            exp[hit].add(key)
    return {i: sorted(v) for i, v in exp.items()}


def features(prod, video):
    times, motion = prod._probe_motion(str(video))
    runs = prod._segment_runs(times, motion)
    dur = times[-1]
    budget = prod._budget_for_duration(dur)
    stamps = prod._allocate_timestamps(runs, budget)
    act = sum(r.duration for r in runs if r.active)
    return {"probe_duration_s": round(dur, 3), "frame_budget": budget, "planned_frames": len(stamps),
            "n_batches": -(-len(stamps) // prod.BATCH_SIZE), "n_runs": len(runs),
            "n_active_runs": sum(r.active for r in runs), "active_ratio": round(act / dur, 4) if dur else 0.0,
            "mean_motion": round(statistics.mean(motion), 4) if motion else 0.0}, stamps


def freeze_frames(prod, video, stamps, outdir):
    from PIL import Image
    outdir.mkdir(parents=True, exist_ok=True)
    for f in outdir.glob("*.jpg"):
        f.unlink()
    paths = prod._extract_frames(str(video), stamps, str(outdir))
    fr = []
    for p in paths:
        ts = float(re.search(r"_(\d+\.\d+)\.jpg$", p).group(1))       # production label source (_call_vlm)
        w, h = Image.open(p).size
        fr.append({"file": Path(p).name, "label": f"[t={ts:.2f}s]", "w": w, "h": h, "sha256": sha256(p)})
    return fr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos-dir", required=True, type=Path)
    ap.add_argument("--prod-src", required=True, type=Path, help="asl_utils.py exported from curify-studio 4220e03c")
    ap.add_argument("--work", required=True, type=Path, help="scratch directory for extracted frames")
    a = ap.parse_args()
    prod = load_prod(a.prod_src)

    # ---- 1. inventory -------------------------------------------------------------------------------------------
    man = list(csv.DictReader(open(BENCH / "manifest.csv")))
    freeze = {l.split()[1]: l.split()[0] for l in lines(BENCH / "FREEZE_CHECKSUMS.sha256")}
    dev45 = {r["clip_id"]: r["review_id"] for r in csv.DictReader(open(CASES45))}
    fin_units = lines(FUSION / "final_units.txt")
    dev_units = lines(FUSION / "dev_units.txt")
    fin_v = {v for u in fin_units for v in u.split("+")}
    dev_v = {v for u in dev_units for v in u.split("+")}
    ids = [r["how2sign_id"] for r in man]
    exp = exposure(ids)
    inv = []
    for r in man:
        cid, vid = r["how2sign_id"], r["source_video_id"]
        try:
            assert_not_holdout([cid]); h1819 = "clear (not How2Sign val; guard passed)"
        except RuntimeError:
            h1819 = "BLOCKED"
        vp = a.videos_dir / f"{cid}.mp4"
        local = vp.exists() and sha256(vp) == freeze[f"videos/{cid}.mp4"]
        p15 = "final_SEALED" if vid in fin_v else ("dev" if vid in dev_v else "none")
        e = exp[cid]
        inv.append({
            "clip_id": cid, "source_video_id": vid, "signer_proxy": re.search(r"-(\d+)-rgb_front$", cid).group(1),
            "official_duration_s": float(r["duration_s"]), "video_sha256": r["video_sha256"],
            "freeze_sha256_matches_manifest": freeze[f"videos/{cid}.mp4"] == r["video_sha256"],
            "local_video_verified": local, "dev45_review_id": dev45.get(cid),
            "h18_h19_status": h1819, "p0_15_fusion_split": p15,
            "prior_exposure": {
                "gemini_curify_2026_09_04_all128": True,       # TASK0_baseline_denominator.md: 128/128 predicted
                "unisign_any": any("unisign" in x or "p0-1" in x or "e0-unisign" in x or "9.2/asl-baselines" in x
                                   for x in e),
                "p0_12": any("p0-12" in x for x in e), "p0_13": any("p0-13" in x for x in e),
                "p0_15_fusion_dev_fitted": p15 == "dev",
                "manual_signcaption_or_human_review": any("signcaption" in x or "manual_signcaption" in x for x in e),
                "n_study_folders": len(e), "study_folders": e}})
    assert len(inv) == 128 and len({x["source_video_id"] for x in inv}) == 128
    assert all(x["freeze_sha256_matches_manifest"] for x in inv)

    elig = [x for x in inv if x["dev45_review_id"] is None and x["p0_15_fusion_split"] != "final_SEALED"
            and x["h18_h19_status"].startswith("clear") and x["local_video_verified"]]
    for x in inv:
        x["round1_eligible"] = x in elig
        x["ineligible_reason"] = None if x in elig else (
            "dev45" if x["dev45_review_id"] else "p0_15_sealed_final" if x["p0_15_fusion_split"] == "final_SEALED"
            else "holdout" if not x["h18_h19_status"].startswith("clear") else "video_not_verified")
    assert_not_holdout([x["clip_id"] for x in elig])

    # ---- 2. input-side features (production preprocessing only) -------------------------------------------------
    stamps = {}
    for x in elig:
        f, st = features(prod, a.videos_dir / f"{x['clip_id']}.mp4")
        x["input_features"] = f; stamps[x["clip_id"]] = st

    # ---- 3. deterministic selection ---------------------------------------------------------------------------
    # cells = signer proxy x batch bucket; cells in fixed order, hash order inside a cell; one systematic
    # alternation (pilot, reserve, pilot, ...) over the concatenated list balances both margins
    for x in elig:
        x["stratum"] = f"signer{x['signer_proxy']}_{'single' if x['input_features']['n_batches'] == 1 else 'multi'}_batch"
        x["selection_key"] = shs(f"{SALT}|{x['clip_id']}")
    order = sorted(elig, key=lambda x: (int(x["signer_proxy"]), x["input_features"]["n_batches"] > 1, x["selection_key"]))
    pilot, reserve = order[0::2], order[1::2]
    for x in elig:
        x["round1_role"] = "pilot" if x in pilot else "reserve"

    def desc(xs):
        f = lambda k: [x["input_features"][k] for x in xs]
        q = lambda v: {"min": min(v), "median": statistics.median(v), "max": max(v)}
        sp = {}
        for x in xs:
            sp[x["signer_proxy"]] = sp.get(x["signer_proxy"], 0) + 1
        return {"n": len(xs), "probe_duration_s": q(f("probe_duration_s")), "planned_frames": q(f("planned_frames")),
                "n_batches": {str(b): f("n_batches").count(b) for b in sorted(set(f("n_batches")))},
                "active_ratio": q(f("active_ratio")), "mean_motion": q(f("mean_motion")),
                "signer_proxy_counts": dict(sorted(sp.items())), "total_calls_per_arm": sum(f("n_batches"))}

    # ---- 4. frame freeze for the pilot (two extractions; must be byte-identical) --------------------------------
    subset = []
    for x in sorted(pilot, key=lambda x: x["clip_id"]):
        cid = x["clip_id"]; v = a.videos_dir / f"{cid}.mp4"; st = stamps[cid]
        fr1 = freeze_frames(prod, v, st, a.work / "pass1" / cid)
        fr2 = freeze_frames(prod, v, st, a.work / "pass2" / cid)
        assert [f["sha256"] for f in fr1] == [f["sha256"] for f in fr2], f"non-deterministic extraction: {cid}"
        assert len(fr1) == len(st), f"ffmpeg dropped a frame: {cid}"
        batches = []
        for b in range(0, len(fr1), prod.BATCH_SIZE):
            bf = fr1[b:b + prod.BATCH_SIZE]
            batches.append({"batch_index": b // prod.BATCH_SIZE, "n_frames": len(bf),
                            "first_label": bf[0]["label"], "last_label": bf[-1]["label"],
                            "input_sha256": shs(PROMPT_SHA + "".join(f["label"] + f["sha256"] for f in bf))})
        subset.append({"clip_id": cid, "source_video_id": x["source_video_id"], "signer_proxy": x["signer_proxy"],
                       "video_sha256": x["video_sha256"], "stratum": x["stratum"],
                       "source_window": {"kind": "whole How2Sign v2 clip (official sentence window, original timing)",
                                         "official_duration_s": x["official_duration_s"],
                                         "probe_duration_s": x["input_features"]["probe_duration_s"]},
                       "frame_budget": x["input_features"]["frame_budget"],
                       "timestamps_s": [round(t, 6) for t in st], "seek_args": [f"{t:.3f}" for t in st],
                       "n_frames": len(fr1), "n_batches": len(batches), "frames": fr1, "batches": batches,
                       "extraction_deterministic_2_passes": True})

    # ---- 5. estimates -------------------------------------------------------------------------------------------
    use = [c["usage"] for f in sorted(P45_RAW.glob("R*.json")) for c in json.load(open(f))["api_calls"] if c.get("usage")]
    full = [u for u, n in zip(use, [c.get("n_images") for f in sorted(P45_RAW.glob("R*.json"))
                                    for c in json.load(open(f))["api_calls"] if c.get("usage")]) if n == 24]
    med = lambda k, xs: statistics.median(u[k] or 0 for u in xs)
    calls = sum(s["n_batches"] for s in subset)
    frames_total = sum(s["n_frames"] for s in subset)
    w, h = subset[0]["frames"][0]["w"], subset[0]["frames"][0]["h"]
    assert all(f["w"] == w and f["h"] == h for s in subset for f in s["frames"])
    patches = -(-w // 32) * -(-h // 32)
    est = {"pilot_cases": len(subset), "pilot_frames": frames_total, "frame_size_px": [w, h],
           "openai_calls_primary": calls, "gemini_calls_primary": calls,
           "gemini_calls_optional_noise_floor_repeat": calls,
           "max_extra_calls_if_every_batch_transport_retried_once": calls,
           "gemini_observed_production_45": {"calls_with_usage": len(use), "full_24_frame_calls": len(full),
                                             "median_prompt_tokens_24_frames": med("prompt_token_count", full),
                                             "median_output_tokens": med("candidates_token_count", use),
                                             "median_thinking_tokens": med("thoughts_token_count", use),
                                             "median_total_tokens": med("total_token_count", use)},
           "gemini_est_prompt_tokens_pilot": round(frames_total * med("prompt_token_count", full) / 24),
           "openai_image_tokens_per_frame_by_family_docs_2026_10_28": {
               "patch_based_multiplier_1.2": -(-patches * 12 // 10), "tile_based_gpt_4o_4.1_high": 85 + 170,
               "tile_based_gpt_5.1_high": 70 + 140, "note": f"{w}x{h} = {patches} patches of 32 px, or 1 tile of 512 px; "
                                                           "not verified by an API call"},
           "dollar_cost": "see openai_cost_estimate (ESTIMATE ONLY)"}
    img_tok = -(-patches * 12 // 10)                                   # 1.2x patch multiplier (documented for astra)
    text_tok = 500                                                     # assumption: prompt + 24 labels per call
    out_lo = round(med("candidates_token_count", use) + med("thoughts_token_count", use))   # Gemini-like
    out_hi = 5 * out_lo                                                # assumption: heavier default reasoning
    inp = frames_total * img_tok + calls * text_tok
    est["openai_cost_estimate"] = {
        "label": "ESTIMATE ONLY: docs prices read 2026-10-29, account pricing and tokenizer unverified, no call made",
        "assumptions": {"image_tokens_per_frame": img_tok, "text_tokens_per_call": text_tok,
                        "output_plus_reasoning_tokens_per_call_low": out_lo,
                        "output_plus_reasoning_tokens_per_call_high": out_hi,
                        "low_basis": "Gemini production_45 median output + thinking tokens per call",
                        "high_basis": "5x the low value (default medium reasoning may think more)",
                        "no_cached_input": True, "primary_calls": calls},
        "input_tokens": inp, "output_tokens_low": calls * out_lo, "output_tokens_high": calls * out_hi}
    for m, pi, po in (("gpt-6.1-sol", 2.0, 10.0), ("gpt-6-astra", 10.0, 50.0)):
        lo = inp * pi / 1e6 + calls * out_lo * po / 1e6
        hi = inp * pi / 1e6 + calls * out_hi * po / 1e6
        est["openai_cost_estimate"][m] = {"price_per_1M_input_output": [pi, po], "primary_usd_low": round(lo, 2),
                                          "primary_usd_high": round(hi, 2),
                                          "worst_case_with_one_retry_per_batch_usd": round(2 * hi, 2)}

    pre = {"stage": "P0-2 Round 1 pre-registration (no API call made)", "date": "2026-10-28",
           "production": {"repo": "curify-studio", "commit": PROD_COMMIT, "file": "curify_background/app/utils/asl_utils.py",
                          "file_sha256": PROD_SHA, "prompt_sha256": PROMPT_SHA, "gemini_model": prod.ASL_MODEL,
                          "temperature": prod.ASL_TEMPERATURE, "dormant_openai_model_in_production": prod.OPENAI_ASL_MODEL},
           "ffmpeg": subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.splitlines()[0],
           "recipe": {k: getattr(prod, k) for k in ("PROBE_FPS", "PROBE_WIDTH", "TARGET_FRAMES_PER_SEC", "MIN_FRAME_BUDGET",
                                                    "MAX_FRAME_BUDGET", "DENSITY_FLOOR_FPS", "KEYFRAME_WIDTH",
                                                    "MIN_FRAMES_PER_RUN", "BATCH_SIZE", "IDLE_QUANTILE",
                                                    "ABS_MOTION_FLOOR", "DEDUP_MAX_GAP_S", "DEGENERATE_REPEAT_COUNT")},
           "pool": {"benchmark_clips": len(inv), "benchmark_freeze_sha256": lines(BENCH / "FREEZE.sha256")[0],
                    "dev45": sum(x["dev45_review_id"] is not None for x in inv),
                    "outside_dev45": sum(x["dev45_review_id"] is None for x in inv),
                    "outside_dev45_in_p0_15_sealed_final": sum(x["dev45_review_id"] is None and x["p0_15_fusion_split"]
                                                               == "final_SEALED" for x in inv),
                    "h18_h19_blocked": sum(not x["h18_h19_status"].startswith("clear") for x in inv),
                    "eligible": len(elig), "local_videos_verified": sum(x["local_video_verified"] for x in inv),
                    "eligible_prior_exposure": {k: sum(x["prior_exposure"][k] for x in elig) for k in
                                                ("gemini_curify_2026_09_04_all128", "unisign_any", "p0_12", "p0_13",
                                                 "p0_15_fusion_dev_fitted", "manual_signcaption_or_human_review")},
                    "clean_untouched_holdout": False},
           "selection": {"rule": "sort the eligible pool by (signer proxy ascending, multi-batch after single-batch, "
                                 f"sha256('{SALT}|'+clip_id)); take positions 0,2,4,... as pilot and 1,3,5,... as "
                                 "reserve; one draw, no redraw",
                         "rule_revision_before_freeze": "a first rule (batch-count strata only) gave signer proxy 8 "
                                                        "11 pilot vs 5 reserve; replaced once, before any model call "
                                                        "and using input-side fields only, by the signer x batch rule",
                         "inputs_used": "production preprocessing only (duration, budget, frames, batches); no model "
                                        "output, no reference text, no text-derived heuristic tag",
                         "pilot_ids": sorted(x["clip_id"] for x in pilot),
                         "reserve_ids": sorted(x["clip_id"] for x in reserve),
                         "pilot_balance": desc(pilot), "reserve_balance": desc(reserve), "eligible_balance": desc(elig)},
           "estimates": est, "protocol": PROTOCOL}
    OUT.mkdir(exist_ok=True)
    (OUT / "p0_2_subset_manifest.json").write_text(json.dumps(
        {"inventory": inv, "pilot_frame_manifest": subset}, indent=1, ensure_ascii=False) + "\n")
    (OUT / "p0_2_openai_preregistration.json").write_text(json.dumps(pre, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"pool": pre["pool"], "pilot": pre["selection"]["pilot_ids"],
                      "pilot_balance": pre["selection"]["pilot_balance"],
                      "reserve_balance": pre["selection"]["reserve_balance"], "estimates": est}, indent=1))


if __name__ == "__main__":
    main()
