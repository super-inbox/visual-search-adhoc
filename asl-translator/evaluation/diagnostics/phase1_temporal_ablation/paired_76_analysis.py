#!/usr/bin/env python3
"""Strict PAIRED comparison of baseline A (2 fps target) vs. the partial
Experiment B (8 fps target) run, restricted to EXACTLY the 76 clip IDs that
Experiment B actually completed successfully before hitting the Gemini
billing cap (see docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md).

NO MODEL CALL IS MADE. This script only reads already-saved
per_clip_results.json/manifest.csv files and reuses the corpus-WER/CER
aggregation already defined in run_curify_how2sign_v2_benchmark.py
(imported, not reimplemented) so the paired-subset corpus numbers use
exactly the same formula as every other reported corpus_wer in this repo.

This is explicitly PRELIMINARY, not a clean causal fps experiment — see the
confounds section printed into PAIRED_76_PRELIMINARY_ANALYSIS.md and
PHASE1_SUMMARY.md §3/§7 for why (both configs use motion-weighted/adaptive
timestamp allocation; batching is independent 24-frame in both; a fixed
24-frame batch spans different amounts of video time at different target
fps).

Run:
    python3 asl-translator/evaluation/diagnostics/phase1_temporal_ablation/paired_76_analysis.py
"""
from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
EVAL_DIR = REPO_ROOT / "asl-translator" / "evaluation"
RESULTS_DIR = EVAL_DIR / "results" / "how2sign_v2"
BASELINE_DIR = RESULTS_DIR / "curify_gemini_3_6_2026_09_04"
EIGHTFPS_DIR = RESULTS_DIR / "curify_gemini_3_6_2026_09_06_8fps"
MANIFEST_PATH = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2" / "manifest.csv"

OUT_CSV = HERE / "paired_76_2fps_vs_8fps.csv"
OUT_MD = HERE / "PAIRED_76_PRELIMINARY_ANALYSIS.md"

sys.path.insert(0, str(EVAL_DIR))
import run_curify_how2sign_v2_benchmark as harness  # noqa: E402 reuse _corpus_wer_cer, not reimplement


def load_per_clip(path: Path) -> dict:
    return {r["how2sign_id"]: r for r in json.loads(path.read_text(encoding="utf-8"))}


def is_yes(v: str) -> bool:
    return (v or "").strip().lower().startswith("yes")


def main() -> None:
    baseline_all = load_per_clip(BASELINE_DIR / "per_clip_results.json")
    eightfps_all = load_per_clip(EIGHTFPS_DIR / "per_clip_results.json")
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        manifest = {r["how2sign_id"]: r for r in csv.DictReader(f)}

    paired_ids = sorted(cid for cid, r in eightfps_all.items() if r["status"] == "success")
    assert len(paired_ids) == 76, f"expected 76 completed 8fps clips, found {len(paired_ids)}"
    missing_from_baseline = [cid for cid in paired_ids if baseline_all.get(cid, {}).get("status") != "success"]
    assert not missing_from_baseline, f"baseline missing/failed for: {missing_from_baseline}"

    baseline_records = [baseline_all[cid] for cid in paired_ids]
    eightfps_records = [eightfps_all[cid] for cid in paired_ids]

    baseline_corpus = harness._corpus_wer_cer(baseline_records)
    eightfps_corpus = harness._corpus_wer_cer(eightfps_records)

    per_clip_rows = []
    deltas = []
    for cid in paired_ids:
        b = baseline_all[cid]
        e = eightfps_all[cid]
        m = manifest[cid]
        delta = round(e["wer"] - b["wer"], 4)
        deltas.append(delta)
        per_clip_rows.append({
            "clip_id": cid,
            "duration_s": b["duration_s"],
            "reference_words": b["reference_words"],
            "baseline_wer": b["wer"],
            "eightfps_wer": e["wer"],
            "wer_delta_8fps_minus_baseline": delta,
            "direction": "improved" if delta < 0 else ("worsened" if delta > 0 else "unchanged"),
            "baseline_frames_sampled": b["frames_sampled"],
            "eightfps_frames_sampled": e["frames_sampled"],
            "baseline_model_calls": b["model_calls"],
            "eightfps_model_calls": e["model_calls"],
            "baseline_sampling_density_fps": b["sampling_density_fps"],
            "eightfps_sampling_density_fps": e["sampling_density_fps"],
            "baseline_single_batch": b["model_calls"] == 1,
            "eightfps_single_batch": e["model_calls"] == 1,
            "hint_fingerspelling_candidate": is_yes(m["heuristic_proper_noun_or_acronym_fingerspelling_candidate"]),
            "hint_number_token": is_yes(m["heuristic_contains_number_token"]),
            "hint_fast_signing": is_yes(m["heuristic_fast_signing_wps_ge_p90"]),
            "hint_question": is_yes(m["official_ends_with_question_mark"]),
        })

    fieldnames = list(per_clip_rows[0].keys())
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(per_clip_rows)

    n_improved = sum(1 for d in deltas if d < 0)
    n_worsened = sum(1 for d in deltas if d > 0)
    n_unchanged = sum(1 for d in deltas if d == 0)
    mean_baseline_wer = round(statistics.mean(r["baseline_wer"] for r in per_clip_rows), 4)
    mean_eightfps_wer = round(statistics.mean(r["eightfps_wer"] for r in per_clip_rows), 4)
    median_delta = round(statistics.median(deltas), 4)
    abs_delta_corpus = round(eightfps_corpus["corpus_wer"] - baseline_corpus["corpus_wer"], 4)
    rel_delta_corpus = round(abs_delta_corpus / baseline_corpus["corpus_wer"] * 100, 2) if baseline_corpus["corpus_wer"] else None

    by_delta = sorted(per_clip_rows, key=lambda r: r["wer_delta_8fps_minus_baseline"])
    largest_improvements = by_delta[:5]
    largest_regressions = list(reversed(by_delta[-5:]))

    # ── stratification (paired 76 subset only) ──────────────────────────
    def strat(pred, label):
        rows = [r for r in per_clip_rows if pred(r)]
        if not rows:
            return {"label": label, "n": 0}
        ids = set(r["clip_id"] for r in rows)
        b_recs = [baseline_all[cid] for cid in ids]
        e_recs = [eightfps_all[cid] for cid in ids]
        bc = harness._corpus_wer_cer(b_recs)
        ec = harness._corpus_wer_cer(e_recs)
        return {
            "label": label, "n": len(rows),
            "baseline_corpus_wer": bc["corpus_wer"], "eightfps_corpus_wer": ec["corpus_wer"],
            "delta": round(ec["corpus_wer"] - bc["corpus_wer"], 4) if bc["corpus_wer"] is not None else None,
            "mean_per_clip_delta": round(statistics.mean(r["wer_delta_8fps_minus_baseline"] for r in rows), 4),
        }

    durations_sorted = sorted(r["duration_s"] for r in per_clip_rows)
    median_duration = statistics.median(durations_sorted)

    strata = [
        strat(lambda r: r["hint_fingerspelling_candidate"], "fingerspelling candidate"),
        strat(lambda r: r["hint_number_token"], "number token"),
        strat(lambda r: r["hint_fast_signing"], "fast signing"),
        strat(lambda r: r["hint_question"], "question"),
        strat(lambda r: not (r["hint_fingerspelling_candidate"] or r["hint_number_token"]
                              or r["hint_fast_signing"] or r["hint_question"]), "plain / no heuristic flag"),
        strat(lambda r: r["baseline_single_batch"], "single-batch at baseline (2 fps)"),
        strat(lambda r: not r["baseline_single_batch"], "multi-batch at baseline (2 fps)"),
        strat(lambda r: r["duration_s"] < median_duration, f"shorter clips (< median {median_duration:.2f}s)"),
        strat(lambda r: r["duration_s"] >= median_duration, f"longer clips (>= median {median_duration:.2f}s)"),
    ]

    def fmt_clip(r):
        return (f"`{r['clip_id']}` — baseline WER {r['baseline_wer']}, 8fps WER {r['eightfps_wer']}, "
                f"delta {r['wer_delta_8fps_minus_baseline']:+.4f} "
                f"(baseline {r['baseline_model_calls']} batch(es) @ {r['baseline_sampling_density_fps']} fps -> "
                f"8fps {r['eightfps_model_calls']} batch(es) @ {r['eightfps_sampling_density_fps']} fps)")

    strata_table = "\n".join(
        f"| {s['label']} | {s['n']} | {s.get('baseline_corpus_wer')} | {s.get('eightfps_corpus_wer')} | "
        f"{s.get('delta')} | {s.get('mean_per_clip_delta')} |"
        for s in strata
    )

    md = f"""# Paired 76-clip PRELIMINARY comparison — baseline A (2 fps) vs. Experiment B (8 fps)

**PRELIMINARY. This is NOT a clean causal fps experiment.** See "Confounds"
below before drawing any conclusion from these numbers. No model call was
made to produce this analysis — it reads only the already-saved
`per_clip_results.json` from both existing runs and reuses
`run_curify_how2sign_v2_benchmark.py`'s own `_corpus_wer_cer()` aggregation.

## Pairing

- Experiment B (`curify_gemini_3_6_2026_09_06_8fps`) has completed exactly
  **{len(paired_ids)}** of 128 frozen clips (the rest failed on `429
  RESOURCE_EXHAUSTED` — Gemini project monthly spend cap, an external billing
  block, not a code issue; see `docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md`).
- Baseline A (`curify_gemini_3_6_2026_09_04`) is scored on the **identical**
  {len(paired_ids)} clip IDs only — not its full 128 — so every number below
  compares the same clips under both configs.

## Headline numbers (paired {len(paired_ids)}-clip subset)

| metric | baseline A (2 fps) | Experiment B (8 fps) |
|---|---|---|
| corpus WER (pooled substitutions+deletions+insertions / reference words) | {baseline_corpus['corpus_wer']} | {eightfps_corpus['corpus_wer']} |
| mean per-clip WER | {mean_baseline_wer} | {mean_eightfps_wer} |
| corpus CER | {baseline_corpus['corpus_cer']} | {eightfps_corpus['corpus_cer']} |

- **Absolute corpus WER delta (8fps − baseline):** {abs_delta_corpus:+.4f}
- **Relative corpus WER delta:** {rel_delta_corpus:+.2f}% of baseline corpus WER
- **Median per-clip WER delta:** {median_delta:+.4f}
- **Clips improved** (8fps WER < baseline WER): {n_improved} / {len(paired_ids)}
- **Clips worsened** (8fps WER > baseline WER): {n_worsened} / {len(paired_ids)}
- **Clips unchanged** (exact WER tie): {n_unchanged} / {len(paired_ids)}

## Largest improvements (most negative delta)

{chr(10).join('- ' + fmt_clip(r) for r in largest_improvements)}

## Largest regressions (most positive delta)

{chr(10).join('- ' + fmt_clip(r) for r in largest_regressions)}

## Stratified by existing manifest/run metadata (paired subset only)

| stratum | n | baseline corpus WER | 8fps corpus WER | corpus WER delta | mean per-clip delta |
|---|---|---|---|---|---|
{strata_table}

"single-batch vs multi-batch" is stratified on **baseline's own** batch count
(2 fps): a clip's batch count can differ between configs since 8 fps samples
more frames from the same duration (see Confound 3 below) — per-clip
`baseline_model_calls` / `eightfps_model_calls` are both in
`paired_76_2fps_vs_8fps.csv` so this shift is visible per clip.

"shorter vs longer" splits the paired 76 at the median duration
({median_duration:.2f}s) within this subset, not the full 128-clip corpus.

## Confounds — why this is NOT a clean fps-only comparison

1. **Both configs use motion-weighted/adaptive timestamp allocation.**
   Neither baseline A nor Experiment B samples frames at a uniform rate —
   both spend their frame budget proportional to motion energy
   (`allocate_timestamps()` in `run_current_model.py`, unchanged between the
   two configs). Any change observed here reflects "more frames allocated by
   the same motion-weighted rule," not "denser uniform temporal sampling."
2. **Target frame density changes (2.0 -> 8.0 target_frames_per_sec)** is
   the one deliberate variable — but see confound 3, it does not act alone.
3. **A fixed 24-frame batch spans different amounts of video time at
   different target fps.** At 2 fps a 24-frame batch covers roughly 12s of
   video; at 8 fps the same 24 frames cover roughly 3s. So any WER delta
   conflates "denser motion-weighted sampling" with "shorter, more
   self-contained time span per independent model call" — these are not
   separated by this data.
4. **Independent batching is unchanged.** Both configs still send batches of
   24 frames to the model with zero shared context between batches
   (confirmed in `run_current_model.run_real()` — see `PHASE1_SUMMARY.md`
   §2). Any seam-crossing failure mode is present, unchanged in mechanism,
   in both arms; only how much time a given seam represents changes.
5. **Partial-corpus subset.** 76/128 is not a random sample of the
   benchmark — it is manifest-order prefix up to where the spend cap hit
   (see `run_curify_how2sign_v2_benchmark.py`'s frozen-manifest-order
   iteration). No claim here generalizes to the full 128 without the
   remaining 52 clips.

**Do not report any WER delta in this file as caused by fps.** It is
reported as an observed, confounded, paired difference on a partial corpus,
to be revisited once a controlled ablation (isolating sampling strategy,
frame density, and batch/context effects — see `PHASE1_SUMMARY.md` §7) is
actually run.

## Files

- `paired_76_2fps_vs_8fps.csv` — one row per paired clip, both configs' WER,
  frame/batch/density metadata, and manifest heuristic hints.
- This file (`PAIRED_76_PRELIMINARY_ANALYSIS.md`).

## No inference performed

This script imports only `run_curify_how2sign_v2_benchmark.py` for its
`_corpus_wer_cer()` aggregation helper (pure arithmetic, no I/O to Gemini)
and reads only already-saved `per_clip_results.json` / `manifest.csv` files.
`google.genai` is not imported anywhere in this script; `GEMINI_API_KEY` is
never read.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"Wrote {OUT_CSV} and {OUT_MD}")
    print(f"paired n={len(paired_ids)} baseline_corpus_wer={baseline_corpus['corpus_wer']} "
          f"8fps_corpus_wer={eightfps_corpus['corpus_wer']} delta={abs_delta_corpus:+.4f} "
          f"improved={n_improved} worsened={n_worsened} unchanged={n_unchanged}")


if __name__ == "__main__":
    main()
