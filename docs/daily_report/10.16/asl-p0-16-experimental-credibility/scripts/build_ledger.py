"""P0-16: build the data-use ledger from committed ID lists (no model, no predictions read, no sentences printed).

Writes  DATA_USE_LEDGER.csv  one row per (dataset subset, experiment), with computed clip/video counts
        CLIP_STATUS.csv      one row per How2Sign test and val clip: which experiments touched it, and its status

Usage: python3 -I build_ledger.py
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
DR = os.path.dirname(os.path.dirname(EXP))                      # docs/daily_report
P = lambda *a: os.path.join(DR, *a)

man = {r["clip_id"]: r for r in csv.DictReader(open(P("10.15", "asl-unisign-representation-probe", "splits",
                                                       "manifest.csv")))}
c128 = [r["clip_id"] for r in csv.DictReader(open(P("10.06", "asl-p0-12-unisign-pose-gap", "per_clip_results.csv")))]
c147 = [x["sample_id"] for x in json.load(open(P("10.07", "asl-p0-13-representation-swap", "data",
                                                  "unisign_own_decoder_frozen147.json")))]
c36 = [r["clip_id"] for r in csv.DictReader(open(P("10.14", "asl-unisign-chunked-decoding-pilot", "pilot_clips.csv")))]
pilot430 = [r["clip_id"] for r in csv.DictReader(open(P("10.15", "asl-unisign-representation-probe", "local_gates",
                                                         "pilot_manifest.csv")))]
p15 = P("10.16", "asl-unisign-high-precision-fusion", "split")
p15dev = open(os.path.join(p15, "dev_clips.txt")).read().split()
p15fin = open(os.path.join(p15, "final_clips.txt")).read().split()
assert len(c128) == 128 and len(c147) == 147 and set(c128) < set(c147) and set(c36) < set(c128)
assert len(p15dev) == 1052 and len(p15fin) == 1157
c19 = sorted(set(c147) - set(c128))

role = lambda r: r["role"]
by_role = lambda rl: [c for c, r in man.items() if r["role"] == rl]
val = [c for c, r in man.items() if r["h2s_split"] == "val"]
test = [c for c, r in man.items() if r["h2s_split"] == "test"]
vids = lambda ids: len({man[c]["video_id"] for c in ids if c in man})

S = {
    "pilot19": c19, "bench128": c128, "chunk36": c36, "frozen147": c147, "pilot430_test": [c for c in pilot430 if man[c]["h2s_split"] == "test"],
    "pilot430_train": [c for c in pilot430 if man[c]["h2s_split"] == "train"],
    "test_clean": by_role("test_clean"), "test_dup_excluded": by_role("test_dup_excluded"),
    "test_no_pose": [c for c in test if man[c]["role"] == "no_official_pose"],
    "probe_train": by_role("probe_train"), "val": val, "p15_dev": p15dev, "p15_final": p15fin,
}
SRC = {
    "pilot19": "10.07/asl-p0-13-representation-swap/data/unisign_own_decoder_frozen147.json minus the 128",
    "bench128": "10.06/asl-p0-12-unisign-pose-gap/per_clip_results.csv",
    "chunk36": "10.14/asl-unisign-chunked-decoding-pilot/pilot_clips.csv",
    "frozen147": "10.07/asl-p0-13-representation-swap/data/unisign_own_decoder_frozen147.json",
    "pilot430_test": "10.15/asl-unisign-representation-probe/local_gates/pilot_manifest.csv (test rows)",
    "pilot430_train": "10.15/asl-unisign-representation-probe/local_gates/pilot_manifest.csv (train rows)",
    "test_clean": "10.15/asl-unisign-representation-probe/splits/manifest.csv role=test_clean",
    "test_dup_excluded": "10.15/asl-unisign-representation-probe/splits/manifest.csv role=test_dup_excluded",
    "test_no_pose": "10.15/asl-unisign-representation-probe/splits/manifest.csv h2s_split=test role=no_official_pose",
    "probe_train": "10.15/asl-unisign-representation-probe/splits/manifest.csv role=probe_train",
    "val": "10.15/asl-unisign-representation-probe/splits/manifest.csv h2s_split=val",
    "p15_dev": "10.16/asl-unisign-high-precision-fusion/split/dev_clips.txt",
    "p15_final": "10.16/asl-unisign-high-precision-fusion/split/final_clips.txt",
}
# (subset, h2s split, experiment, labels inspected, predictions inspected, influenced design, status, note)
ROWS = [
    ("pilot19", "test", "8.30-8.31 pilot_v1 / P0.2 frozen test", "per-clip", "per-clip", "yes", "exploratory",
     "first Uni-Sign/OpenSLT pilot clips; later part of the frozen 147"),
    ("bench128", "test", "9.2 How2Sign-v2 baseline (OpenSLT + Uni-Sign) and E0 reproduction", "per-clip", "per-clip", "yes", "exploratory",
     "128 clips, one per source video, deliberately skewed to hard categories; authors' released predictions compared per clip"),
    ("bench128", "test", "P0-12 preprocessing gap (A/B/B_aspect/C)", "per-clip", "per-clip", "yes", "exploratory",
     "single run per condition, T4/fp16"),
    ("bench128", "test", "Automated error taxonomy", "per-clip", "per-clip", "yes", "exploratory",
     "weak labels from references; generated the long-output, loop and name hypotheses"),
    ("bench128", "test", "Decode-length cap (R100/R150/R256)", "per-clip", "per-clip", "yes", "exploratory",
     "hypothesis came from the taxonomy on the same clips"),
    ("bench128", "test", "Repetition cleanup (rule v1)", "per-clip", "per-clip", "yes", "exploratory",
     "G1 applied the rule to the 128 references; G2 to predictions; metrics never computed"),
    ("chunk36", "test", "Chunked decoding pilot (U36/S1/S2/S3)", "per-clip", "per-clip", "yes", "exploratory",
     "21 targets + 15 controls, all inside the 128; thresholds frozen before GPU runs but hypothesis came from these clips"),
    ("frozen147", "test", "P0-11 data scaling and P0-13 representation swap (frozen test)", "per-clip", "per-clip", "yes", "exploratory",
     "called 'clean' there only in the sense that Uni-Sign never trained on them"),
    ("probe_train", "train", "P0-11 / P0-13 train and the 366-clip 'val' (all drawn from How2Sign train)", "per-clip (training)", "aggregate", "yes", "training-only",
     "Uni-Sign was fine-tuned on all How2Sign train clips"),
    ("probe_train", "train", "P0-14 probe training + concept vocabulary selection", "aggregate (training)", "none-exist", "yes", "training-only",
     "concepts selected from train references; probes trained on train"),
    ("pilot430_train", "train", "P0-14 local pilot gate", "aggregate (training)", "none-exist", "no", "training-only", "pipeline gate only"),
    ("pilot430_test", "test", "P0-14 local pilot gate", "aggregate", "aggregate", "no", "exploratory", "pipeline gate only; probe metrics on 108 test_clean clips"),
    ("test_clean", "test", "P0-14 full run (probes + Uni-Sign decode + fusion readiness)", "aggregate + per-concept", "all 2,209 decoded; aggregated (a few printed in logs)", "yes",
     "validation-used (not confirmatory)", "results shaped the P0-15 design; 127 of the 128 benchmark clips are inside"),
    ("test_dup_excluded", "test", "P0-14 duplicate audit (excluded from evaluation)", "reference text screened", "no (1 clip in the 128, 2 in the 147 were decoded earlier)", "no",
     "excluded", "exact/near duplicates of train references"),
    ("test_no_pose", "test", "P0-14 (no official pose; not used)", "counts only", "no", "no", "not eligible",
     "their source videos are already contaminated through other clips"),
    ("p15_dev", "test", "P0-15 dev (C/D fitting, D-vs-C decision)", "per-cell (fitting)", "per-cell (fitting)", "yes", "exploratory", ""),
    ("p15_final", "test", "P0-15 final half", "label COUNTS only in P0-15 (balance check); never read per cell in P0-15", "not in P0-15",
     "yes (through P0-14 and the 128)", "validation-used: unopened for P0-15 but previously observed; retired from confirmatory use by P0-16 (development allowed)",
     "all 1,157 were in the P0-14 aggregate analysis; 66 are 128-benchmark clips inspected per clip in P0-12/taxonomy"),
    ("val", "val", "P0-14 data audit only", "aggregate counts (split sizes, per-concept positive counts, duplicate-of-train counts)",
     "none-exist (never decoded; no poses)", "no (vocabulary selected from train only)", "confirmatory-eligible (proposed P0-16 holdout)",
     "Uni-Sign's How2Sign dev label path is empty upstream; never used by the authors or by us for any model output"),
]
with open(os.path.join(EXP, "DATA_USE_LEDGER.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["dataset_subset", "how2sign_split", "id_source", "n_clips", "n_source_videos", "experiment",
                "labels_inspected", "predictions_inspected", "influenced_hypothesis_or_design", "status", "notes"])
    for k, sp, ex, li, pi, inf, st, note in ROWS:
        w.writerow([k, sp, SRC[k], len(S[k]), vids(S[k]), ex, li, pi, inf, st, note])

# ---------------------------------------------------------------- per-clip status (test + val)
in_ = {k: set(v) for k, v in S.items()}
v147 = {man[c]["video_id"] for c in c147}
rows = []
for c in sorted(test + val):
    r = man[c]
    flags = {f"in_{k}": int(c in in_[k]) for k in ("pilot19", "bench128", "chunk36", "frozen147", "pilot430_test",
                                                    "p15_dev", "p15_final")}
    if r["h2s_split"] == "val":
        status, why = "confirmatory-eligible (subject to HOLDOUT_PLAN exclusions)", "never decoded; aggregate reference counts only"
    elif flags["in_frozen147"]:
        status, why = "exploratory", "inspected per clip (references and predictions)"
    elif r["role"] == "test_clean":
        status = "exploratory" if flags["in_p15_dev"] else "validation-used (not confirmatory)"
        why = ("P0-15 dev fitting" if flags["in_p15_dev"] else "P0-14 aggregate analysis") + \
              ("; source video also has a per-clip-inspected clip" if r["video_id"] in v147 else "")
    else:
        status, why = "excluded / not eligible", r["role"]
    rows.append({"clip_id": c, "video_id": r["video_id"], "how2sign_split": r["h2s_split"], "p014_role": r["role"],
                 **flags, "video_has_per_clip_inspected_clip": int(r["video_id"] in v147), "status": status, "reason": why})
with open(os.path.join(EXP, "CLIP_STATUS.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)

tv = {man[c]["video_id"] for c in test}
summary = {
    "test_clips": len(test), "test_videos": len(tv),
    "test_videos_with_per_clip_inspected_clip": len(tv & v147),
    "test_clips_in_videos_with_per_clip_inspected_clip": sum(1 for c in test if man[c]["video_id"] in v147),
    "test_clips_confirmatory_eligible": 0,
    "p15_final_clips_in_bench128": len(in_["p15_final"] & in_["bench128"]),
    "p15_final_clips_in_frozen147": len(in_["p15_final"] & in_["frozen147"]),
    "p15_final_videos_with_per_clip_inspected_clip": len({man[c]["video_id"] for c in p15fin} & v147),
    "p15_dev_clips_in_bench128": len(in_["p15_dev"] & in_["bench128"]),
    "val_clips": len(val), "val_videos": vids(val),
}
json.dump(summary, open(os.path.join(EXP, "ledger_summary.json"), "w"), indent=1)
print(json.dumps(summary, indent=1))
