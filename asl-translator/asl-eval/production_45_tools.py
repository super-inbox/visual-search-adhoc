#!/usr/bin/env python3
"""Production 45-case evaluation: manifest, scoring, comparison, inspection-sheet columns. No model calls.

  manifest  -> production_45/production_45_manifest.csv (all R01-R45, before any API call)
  score     -> production_45/production_45_predictions.json, production_45_scores.json, production_45_cases.csv
  sheet     -> writes the 10.18 sheet's augmented copy inspection_sheet_with_production.csv: every original row, column and
               value unchanged, production_* columns appended. The original inspection_sheet.csv is not modified: it is
               a generated artifact (build_inspection_sheet.py fixed FIELDS; the HTML Export writes the same filename
               from its embedded field list), so in-place columns would be lost on a rebuild or a reviewer export

Metrics are the P0-A frozen definitions used throughout the 45-case work (copied from
experiments/p0-2026-10-27/score_repetition.py): corpus chrF / BLEU-4 (sacrebleu defaults), WER (lowercase whitespace
tokens, x100), mean output/reference word-length ratio; sentence chrF / WER; loop_out (§1.4, output only).
References: 10.13 inputs_128.jsonl (identical to the inspection sheet ground_truth, checked).

usage: python3 -I production_45_tools.py manifest|score|sheet [--raw-dir DIR] [--dry-run-jsonl FILE]
"""
import argparse, csv, hashlib, json, re, statistics, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "production_45"
SHEET_DIR = REPO / "docs/daily_report/10.18/asl-review-inspection-sheet"
REFS = REPO / "docs/daily_report/10.13/asl-unisign-error-taxonomy/inputs_128.jsonl"
P0A = REPO / "asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/runs/full45"
PROV = REPO / "asl-translator/daily_report/2026-10-27/p0-input-provenance/input_manifest_45.csv"
SHORT_WORDS = 3

sys.path.insert(0, str(REPO / "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def loop_out(x):                                      # P0-A §1.4, output only
    t = re.findall(r"[a-z0-9']+", x.lower())
    g = [tuple(t[i:i + 3]) for i in range(len(t) - 2)]
    return bool(g) and 1 - len(set(g)) / len(g) >= 0.15


def edits(h, r):
    h, r = h.lower().split(), r.lower().split()
    d = list(range(len(r) + 1))
    for i, hw in enumerate(h, 1):
        prev, d[0] = d[0], i
        for j, rw in enumerate(r, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (hw != rw))
    return d[len(r)], len(r)


def parses(raw):
    """Production _call_vlm parsing: json.loads, else the first {...} span, else failure."""
    try:
        json.loads((raw or "").strip()); return True
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw or "", re.S)
        try:
            return bool(m) and (json.loads(m.group(0)) is not None)
        except json.JSONDecodeError:
            return False


def corpus(hyps, refs):
    import sacrebleu
    e = [edits(h, r) for h, r in zip(hyps, refs)]
    return {"n": len(refs), "chrF": round(sacrebleu.corpus_chrf(hyps, [refs]).score, 4),
            "BLEU4": round(sacrebleu.corpus_bleu(hyps, [refs]).score, 4),
            "WER": round(100 * sum(x for x, _ in e) / sum(n for _, n in e), 4),
            "mean_len_ratio": round(sum(len(h.split()) / max(len(r.split()), 1) for h, r in zip(hyps, refs)) / len(refs), 4),
            "loop_out": sum(loop_out(h) for h in hyps), "empty": sum(not h.strip() for h in hyps)}


def sent(h, r):
    import sacrebleu
    e, n = edits(h, r)
    return {"chrF": round(sacrebleu.sentence_chrf(h, [r]).score, 4), "WER": round(100 * e / n, 4),
            "words": len(h.split()), "loop_out": loop_out(h)}


def load_common():
    sheet = list(csv.DictReader(open(SHEET_DIR / "inspection_sheet.csv")))
    vids = {r["review_id"]: r for r in csv.DictReader(open(SHEET_DIR / "videos_manifest.csv"))}
    refs = {json.loads(l)["clip_id"]: json.loads(l)["reference"] for l in open(REFS)}
    t = {d: {json.loads(l)["review_id"]: json.loads(l)["T"]["text"] for l in open(P0A / d / "run1/candidates.jsonl")}
         for d in ("A_official", "B_ours_5p39")}
    prov = {(r["review_id"], r["preprocessing_domain"]): r["provenance_status"] for r in csv.DictReader(open(PROV))}
    assert [r["review_id"] for r in sheet] == [f"R{i:02d}" for i in range(1, 46)]
    assert all(refs[r["clip_id"]] == r["ground_truth"] for r in sheet)
    assert_not_holdout([r["clip_id"] for r in sheet])
    return sheet, vids, refs, t, prov


def cmd_manifest(a):
    sheet, vids, refs, t, prov = load_common()
    dry = {json.loads(l)["review_id"]: json.loads(l) for l in open(a.dry_run_jsonl)} if a.dry_run_jsonl else {}
    rows = []
    for r in sheet:
        rid, v, d = r["review_id"], vids[r["review_id"]], dry.get(r["review_id"], {})
        rows.append({
            "review_id": rid, "clip_id": r["clip_id"],
            "input_video": f"docs/daily_report/10.18/asl-review-inspection-sheet/{v['file']}", "input_video_sha256": v["sha256"],
            "input_source": v["source_path"],
            "input_domain": "inspection-sheet video = How2Sign v2 clip, full frame 1280x720 (B_ours_5p39 window)",
            "duration_s": v["duration_s"], "reference": refs[r["clip_id"]],
            "provenance_status_B_window": prov[(rid, "B_ours_5p39")],
            "provenance_note": ("timing-label MISMATCH: window is the measured re-aligned interval, not original timing"
                                if prov[(rid, "B_ours_5p39")] == "MISMATCH" else
                                "source interval UNRESOLVED (input video itself is fixed and sha256-verified)"
                                if prov[(rid, "B_ours_5p39")] == "UNRESOLVED" else ""),
            "existing_unisign_outputs": "sheet prod_output (B_ours_5p39, P0-12 T4/fp16); sheet unisign_output (A_official, "
                                        "P0-12 T4/fp16); P0-A CPU T (A_official, B_ours_5p39)",
            "planned_frame_budget": d.get("frame_budget_used", ""), "planned_frames": d.get("frames_sampled", ""),
            "planned_calls": d.get("n_batches", ""),
            "production_eval_eligible": "yes" if v["sha256"] == sha256(SHEET_DIR / v["file"]) else "no: video sha mismatch"})
    OUT.mkdir(exist_ok=True)
    with open(OUT / "production_45_manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print(len(rows), sum(r["production_eval_eligible"] == "yes" for r in rows), "eligible")


def cmd_score(a):
    sheet, vids, refs, t, prov = load_common()
    raw_dir = Path(a.raw_dir)
    meta = json.loads((raw_dir / "run_meta.json").read_text())
    preds, cases = [], []
    for r in sheet:
        rid, cid, ref = r["review_id"], r["clip_id"], refs[r["clip_id"]]
        p = raw_dir / f"{rid}.json"
        rec = json.loads(p.read_text()) if p.exists() else {"review_id": rid, "status": "not_run"}
        preds.append(rec)
        out = rec.get("output_text_raw") or ""
        status = rec.get("status")
        if status == "error" and not rec.get("had_transport_error") and not rec.get("quota_exhausted"):
            status = "no_signing_detected"   # the model answered with no segments; production raises NoSigningDetectedError
        scored = status in ("ok", "empty", "no_signing_detected")   # scored as the (possibly empty) production transcript
        calls_ = rec.get("api_calls", [])
        parse_fail = sum(1 for c in calls_ if "raw_text" in c and not parses(c["raw_text"]))
        row = {"review_id": rid, "clip_id": cid, "reference": ref, "ref_words": len(ref.split()),
               "production_status": status, "production_output": out, "batches_unparseable": parse_fail,
               "production_model_version": ";".join(sorted({c.get("model_version") or "" for c in rec.get("api_calls", [])})),
               "frames_sent": rec.get("frames_sampled"), "api_calls": len(rec.get("api_calls", [])),
               "low_density": rec.get("low_density"), "degenerate_repetition": rec.get("degenerate_repetition"),
               "latency_s": rec.get("latency_s"),
               "provenance_status_B_window": prov[(rid, "B_ours_5p39")]}
        srcs = {"production": out, "unisign_B_P0A_cpu": t["B_ours_5p39"][rid], "unisign_A_P0A_cpu": t["A_official"][rid],
                "sheet_prod_output_B_T4": r["prod_output"], "sheet_unisign_output_A_T4": r["unisign_output"]}
        for k, h in srcs.items():
            if k == "production" and not scored:
                continue
            s = sent(h, ref)
            row.update({f"{k}_text" if k != "production" else "_": h, f"{k}_chrF": s["chrF"], f"{k}_WER": s["WER"],
                        f"{k}_words": s["words"], f"{k}_loop_out": s["loop_out"]})
        row.pop("_", None)
        for k in ("sheet_prod_output_B_T4", "unisign_B_P0A_cpu", "unisign_A_P0A_cpu", "sheet_unisign_output_A_T4"):
            if scored:
                row[f"d_chrF_prod_minus_{k}"] = round(row["production_chrF"] - row[f"{k}_chrF"], 4)
                row[f"d_WER_prod_minus_{k}"] = round(row["production_WER"] - row[f"{k}_WER"], 4)
        for k in ("initial_error_category", "auto_error_type_prod", "auto_error_type_unisign", "review_status"):
            row[f"sheet_{k}"] = r[k]
        row["human_status"] = "pending"
        cases.append(row)

    ok = [c for c in cases if c["production_status"] in ("ok", "empty", "no_signing_detected")]
    def corp(key, rows):
        return corpus([c[f"{key}_text"] if key != "production" else c["production_output"] for c in rows],
                      [c["reference"] for c in rows])
    keys = ("production", "unisign_B_P0A_cpu", "unisign_A_P0A_cpu", "sheet_prod_output_B_T4", "sheet_unisign_output_A_T4")
    summ = {"production_meta": meta,
            "n_cases": len(cases), "status_counts": {s: sum(c["production_status"] == s for c in cases)
                                                     for s in sorted({c["production_status"] for c in cases})},
            "references": str(REFS.relative_to(REPO)), "references_sha256": sha256(REFS),
            "corpus_scored_cases": {k: corp(k, ok) for k in keys}}
    calls = [x for p in preds for x in p.get("api_calls", [])]
    summ["api"] = {"calls": len(calls), "transport_errors": sum("error" in x for x in calls),
                   "responses_unparseable_by_production": sum(c["batches_unparseable"] for c in cases),
                   "cases_with_unparseable_batch": [c["review_id"] for c in cases if c["batches_unparseable"]],
                   "frames_sent": sum(p.get("frames_sampled") or 0 for p in preds),
                   "requested_models": sorted({x.get("requested_model") or "" for x in calls}),
                   "model_versions": sorted({x.get("model_version") or "" for x in calls}),
                   "configs_seen": sorted({json.dumps(x.get("config"), sort_keys=True) for x in calls}),
                   "images_sent": sum(x.get("n_images") or 0 for x in calls),
                   "prompt_tokens": sum((x.get("usage") or {}).get("prompt_token_count") or 0 for x in calls),
                   "output_tokens": sum((x.get("usage") or {}).get("candidates_token_count") or 0 for x in calls),
                   "thought_tokens": sum((x.get("usage") or {}).get("thoughts_token_count") or 0 for x in calls),
                   "total_tokens": sum((x.get("usage") or {}).get("total_token_count") or 0 for x in calls),
                   "sum_case_latency_s": round(sum(p.get("latency_s") or 0 for p in preds), 1)}
    comp = {}
    for k in ("sheet_prod_output_B_T4", "unisign_B_P0A_cpu", "unisign_A_P0A_cpu", "sheet_unisign_output_A_T4"):
        dc = [c[f"d_chrF_prod_minus_{k}"] for c in ok]; dw = [c[f"d_WER_prod_minus_{k}"] for c in ok]
        comp[k] = {"n": len(ok), "prod_chrF_higher": sum(x > 0 for x in dc), "prod_chrF_lower": sum(x < 0 for x in dc),
                   "chrF_tie": sum(x == 0 for x in dc), "prod_WER_lower(better)": sum(x < 0 for x in dw),
                   "prod_WER_higher(worse)": sum(x > 0 for x in dw), "WER_tie": sum(x == 0 for x in dw),
                   "mean_d_chrF": round(statistics.mean(dc), 4) if dc else None,
                   "median_d_chrF": round(statistics.median(dc), 4) if dc else None,
                   "mean_d_WER": round(statistics.mean(dw), 4) if dw else None,
                   "median_d_WER": round(statistics.median(dw), 4) if dw else None}
        top = sorted(ok, key=lambda c: -c[f"d_chrF_prod_minus_{k}"])
        brief = lambda c: {"review_id": c["review_id"], "d_chrF": c[f"d_chrF_prod_minus_{k}"], "d_WER": c[f"d_WER_prod_minus_{k}"],
                           "production": c["production_output"], "unisign": c[f"{k}_text"], "reference": c["reference"]}
        comp[k]["largest_prod_gains"] = [brief(c) for c in top[:5]]
        comp[k]["largest_prod_losses"] = [brief(c) for c in top[::-1][:5]]
    summ["comparison_vs_unisign"] = comp
    pc = [c["production_chrF"] for c in ok]; pw = [c["production_WER"] for c in ok]
    summ["production_case_distribution"] = {
        "sentence_chrF": {"min": min(pc), "median": statistics.median(pc), "max": max(pc)} if pc else None,
        "sentence_WER": {"min": min(pw), "median": statistics.median(pw), "max": max(pw)} if pw else None,
        "words": {"min": min(c["production_words"] for c in ok), "median": statistics.median(c["production_words"] for c in ok),
                  "max": max(c["production_words"] for c in ok)} if ok else None,
        "ref_words_median": statistics.median(c["ref_words"] for c in ok) if ok else None,
        "empty_or_short(<=3 words)": [c["review_id"] for c in ok if c["production_words"] <= SHORT_WORDS],
        "loop_out": [c["review_id"] for c in ok if c["production_loop_out"]],
        "degenerate_repetition_flag": [c["review_id"] for c in ok if c["degenerate_repetition"]],
        "low_density_flag": [c["review_id"] for c in ok if c["low_density"]],
        "non_ok": [c["review_id"] for c in cases if c not in ok]}
    summ["automatic_metrics_only"] = True
    (OUT / "production_45_predictions.json").write_text(json.dumps({"production_meta": meta, "predictions": preds}, indent=1))
    (OUT / "production_45_scores.json").write_text(json.dumps({"summary": summ, "cases": cases}, indent=1))
    with open(OUT / "production_45_cases.csv", "w", newline="") as f:
        cols = list(dict.fromkeys(k for c in cases for k in c))
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(cases)
    print(json.dumps({k: summ[k] for k in ("status_counts", "corpus_scored_cases", "api")}, indent=1))


def cmd_sheet(a):
    path = SHEET_DIR / "inspection_sheet.csv"
    before = sha256(path)
    rows = list(csv.DictReader(open(path, newline="")))
    cols = list(rows[0])
    scores = {c["review_id"]: c for c in json.load(open(OUT / "production_45_scores.json"))["cases"]}
    meta = json.load(open(OUT / "production_45_scores.json"))["summary"]["production_meta"]
    new = ["production_model", "production_output", "production_chrF", "production_WER", "production_status", "production_source"]
    assert not set(new) & set(cols), "production_* columns already present"
    for r in rows:
        s = scores[r["review_id"]]
        r.update({"production_model": f"{meta['model']} (temperature {meta['temperature']})",
                  "production_output": s["production_output"],
                  "production_chrF": s.get("production_chrF", ""), "production_WER": s.get("production_WER", ""),
                  "production_status": s["production_status"],
                  "production_source": (f"curify-studio {meta['production_ref']} {meta['production_commit'][:8]} "
                                        f"asl_utils.transcribe_asl on the inspection-sheet video; 2026-10-27 run; "
                                        f"automatic metrics only")})
    dst = SHEET_DIR / "inspection_sheet_with_production.csv"
    with open(dst, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols + new, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    orig = list(csv.DictReader(open(path, newline=""))); aug = list(csv.DictReader(open(dst, newline="")))
    assert sha256(path) == before, "original sheet changed"
    assert [r["review_id"] for r in aug] == [r["review_id"] for r in orig] and list(aug[0])[:len(cols)] == cols
    assert all(all(a_[c] == o[c] for c in cols) for a_, o in zip(aug, orig)), "an original value differs"
    print("wrote", dst.name, "| original unchanged, 45 rows, all", len(cols), "original columns identical; appended", new)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["manifest", "score", "sheet"])
    ap.add_argument("--raw-dir"); ap.add_argument("--dry-run-jsonl")
    a = ap.parse_args()
    {"manifest": cmd_manifest, "score": cmd_score, "sheet": cmd_sheet}[a.cmd](a)


if __name__ == "__main__":
    main()
