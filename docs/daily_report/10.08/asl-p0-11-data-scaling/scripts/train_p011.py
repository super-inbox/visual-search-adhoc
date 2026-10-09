"""
P0-11 = copy of scripts/train_p02.py (gloss-free-asl-translation 3906699). The ONLY intended variable is
the training-ID list (nested 25/50/100% subsets of the same How2Sign pool). Everything else is the P0.2
recipe. Changes vs train_p02.py (P011_DEVIATIONS, written to run_config.json):
  - train IDs come from --train-ids (not re-derived by split_by_signer); val = P0.2's pinned 366 IDs
  - texts come from a metadata CSV built from the official re-aligned train CSV (asserted identical to
    P0.2's subset_metadata.csv on all 3,117 P0.2 clips)
  - training budget is fixed in OPTIMIZER STEPS (max_steps = P0.2's 10,320) with evaluation/checkpoint/early
    stopping every 344 steps (= one P0.2 epoch), so the LR schedule, warmup, eval cadence and patience are
    identical to P0.2 for every subset size
  - save_total_limit 2 (best + latest) to bound disk; selection unchanged (eval_loss)

Original P0.2 docstring follows.

P0.2: multi-epoch training on the fixed 10% How2Sign subset (2,751 train / 366 val).

Mirrors ``src/train.py`` (model, augmentation, tokenizer, T5 dropout 0.1, Adafactor param
groups with 0.1x T5 lr, batch size 8, lr 1e-4, linear warmup 0.1, eval_loss early stopping
with patience 10, greedy generation max_length 30) plus the deviations the previous 1-epoch
run already used (gradient_accumulation 1, logging_steps 1, CPU). Additional deviations for
this run are listed in ``DEVIATIONS`` and written to run_config.json.

Per epoch it records train loss, the 366-example validation loss / generation metrics, and
greedy generation on the fixed 147-example frozen set. The frozen set is diagnostic only:
it never feeds early stopping or checkpoint selection.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from transformers import (  # noqa: E402
    EarlyStoppingCallback,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    T5TokenizerFast,
    TrainerCallback,
    set_seed,
)

from src.dataset import ASLLandmarkDataset, CollateLandmarks  # noqa: E402
from src.models.translation_model import ASLTranslationModel  # noqa: E402
from src.utils.metadata import load_metadata  # noqa: E402
from src.utils.splits import split_by_signer  # noqa: E402

T5_MODEL = "t5-small"
GEN_KWARGS = {"max_length": 30, "num_beams": 1, "do_sample": False}
P011_DEVIATIONS = [
    "train IDs from --train-ids (nested subset); val pinned to P0.2 holdout_split.json val (366)",
    "metadata CSV built from the official re-aligned train CSV; asserted equal to P0.2 texts",
    "compute-matched budget: max_steps 10320 (= P0.2 30 epochs x 344), eval/save/early-stop every 344 steps",
    "save_total_limit 2 (best + latest)",
    "no --baseline-checkpoint rescoring",
]
EVAL_EVERY = 344
DEVIATIONS = [
    "num_train_epochs 1 -> up to 30 (the variable under test); linear warmup 0.1 + decay is "
    "computed by HF over the full 30-epoch step count, so epoch 1 here is still in warmup and "
    "is NOT equivalent to the old 1-epoch run (whose lr decayed to 0 within 344 steps)",
    "save_total_limit 3 -> None: keep every epoch checkpoint so each table row has a checkpoint "
    "(~420 MB each); selection is still by eval_loss via load_best_model_at_end",
    "set_seed(seed) before model construction: upstream builds the model before the Trainer "
    "seeds, so the old run's initial weights are unseeded and cannot be reproduced",
    "train/val IDs are pinned to holdout_split.json (re-derived with upstream split_by_signer "
    "and asserted identical) instead of trusting a fresh split",
    "compute_metrics extended with chrF/CER, full-reference scoring and per-sample files; the "
    "upstream truncated-label BLEU/WER are kept as legacy_* for comparison",
    "report_to none (metrics are written to JSON/CSV instead of TensorBoard)",
    "per-epoch greedy generation on the 147 frozen examples (diagnostic only)",
]


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


def norm_text(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", t.lower())).strip()


def score(refs: list[str], hyps: list[str]) -> dict:
    import jiwer
    import sacrebleu

    safe = [h if h.strip() else " " for h in hyps]
    safe_r = [r if r.strip() else " " for r in refs]
    counts = Counter(h.strip() for h in hyps)
    top, top_n = counts.most_common(1)[0]
    return {
        "bleu": sacrebleu.corpus_bleu(safe, [safe_r]).score,
        "chrf": sacrebleu.corpus_chrf(safe, [safe_r]).score,
        "wer": jiwer.wer(safe_r, safe),
        "cer": jiwer.cer(safe_r, safe),
        "n": len(hyps),
        "unique_predictions": len(counts),
        "top1_prediction": top,
        "top1_count": top_n,
        "top1_fraction": top_n / len(hyps),
    }


def clean_id(path: str) -> str:
    return os.path.basename(path).replace("_holistic.npy", "").replace("_landmarks.npy", "")


# --------------------------------------------------------------------------- data checks
def build_sets(args, tokenizer) -> dict:
    split = json.load(open(args.split_json))
    metadata, video_to_signer = load_metadata(args.metadata)
    train_ids = [l.strip() for l in open(args.train_ids) if l.strip()]
    if set(train_ids) & set(split["val"]):
        raise SystemExit("STOP: train/val clip overlap")
    up_train = [str(Path(args.stage_dir) / f"{i}_holistic.npy") for i in train_ids]
    up_val = [str(Path(args.stage_dir) / f"{i}_holistic.npy") for i in sorted(split["val"])]
    missing = [p for p in up_train + up_val if not Path(p).exists()]
    if missing:
        raise SystemExit(f"STOP: {len(missing)} landmark files missing, e.g. {missing[:3]}")
    frozen_meta, _ = load_metadata(args.frozen_metadata)
    frozen_files = sorted(str(p) for p in Path(args.frozen_landmarks).glob("*_holistic.npy"))
    return {"metadata": metadata, "train_files": up_train, "val_files": up_val,
            "frozen_meta": frozen_meta, "frozen_files": frozen_files,
            "train_ids": [clean_id(p) for p in up_train],
            "val_ids": [clean_id(p) for p in up_val],
            "frozen_ids": [clean_id(p) for p in frozen_files]}


def overlap_report(sets: dict, args) -> dict:
    """Clip / source-video / normalised-text overlap between train, val and the frozen set."""
    official = {}  # SENTENCE_NAME -> (split, VIDEO_ID)
    for sp in ("train", "val", "test"):
        f = Path(args.raw_dir) / f"how2sign_realigned_{sp}.csv"
        with open(f, newline="") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                official[r["SENTENCE_NAME"]] = (sp, r["VIDEO_ID"])
    deny = json.load(open(args.frozen_denylist)) if args.frozen_denylist else None
    v2 = {}
    if args.how2sign_v2_manifest:
        with open(args.how2sign_v2_manifest, newline="") as fh:
            v2 = {r["how2sign_id"]: r["source_split"] for r in csv.DictReader(fh)}

    def video_of(cid: str) -> str:
        return official[cid][1] if cid in official else cid.rsplit("_", 1)[0]

    texts = {"train": {i: sets["metadata"][i] for i in sets["train_ids"]},
             "val": {i: sets["metadata"][i] for i in sets["val_ids"]},
             "frozen": {i: sets["frozen_meta"][i] for i in sets["frozen_ids"]}}
    ids = {k: set(v) for k, v in texts.items()}
    vids = {k: {video_of(i) for i in v} for k, v in ids.items()}
    ntext = {k: {norm_text(t) for t in v.values()} for k, v in texts.items()}
    pairs = [("train", "val"), ("frozen", "train"), ("frozen", "val")]
    rep = {"counts": {k: len(v) for k, v in ids.items()},
           "video_counts": {k: len(v) for k, v in vids.items()}}
    for a, b in pairs:
        rep[f"{a}_vs_{b}"] = {
            "clip_overlap": sorted(ids[a] & ids[b]),
            "video_overlap": sorted(vids[a] & vids[b]),
            "normalised_text_overlap": sorted(ntext[a] & ntext[b]),
        }
    per_frozen = []
    for cid in sets["frozen_ids"]:
        sp, vid = official.get(cid, (None, cid.rsplit("_", 1)[0]))
        per_frozen.append({
            "clip_id": cid, "official_how2sign_split": sp, "video_id": vid,
            "benchmark": "how2sign_v2" if cid in v2 else "pilot_v1 (not in how2sign_v2 manifest)",
            "how2sign_v2_manifest_source_split": v2.get(cid),
            "clip_in_train": cid in ids["train"], "clip_in_val": cid in ids["val"],
            "video_in_train": vid in vids["train"], "video_in_val": vid in vids["val"],
            "text_in_train_or_val": norm_text(texts["frozen"][cid]) in (ntext["train"] | ntext["val"]),
        })
    rep["frozen_official_split_counts"] = dict(Counter(
        f"{r['benchmark'].split(' ')[0]}|official_split={r['official_how2sign_split']}"
        for r in per_frozen))
    rep["frozen_rows"] = per_frozen
    rep["frozen_ids_with_any_overlap"] = [
        r["clip_id"] for r in per_frozen
        if r["clip_in_train"] or r["clip_in_val"] or r["video_in_train"] or r["video_in_val"]
        or r["text_in_train_or_val"]]
    if deny:
        rep["denylist_clip_ids_equal_frozen_ids"] = set(deny["clip_ids"]) == ids["frozen"]
        rep["denylist_sha256"] = deny.get("denylist_sha256")
    rep["landmark_provenance"] = {
        "train_val": "third-party Kaggle 'How2Sign Holistic' MediaPipe extraction (staged symlinks)",
        "frozen": "extracted locally with upstream src/data_pipeline.py (MediaPipe Holistic)",
    }
    return rep


# --------------------------------------------------------------------------- evaluation
def generate_rows(model, dataset, collate_fn, tokenizer, batch_size, with_loss=True) -> tuple:
    was = model.training
    model.eval()
    rows, nll, n_tok = [], 0.0, 0
    with torch.no_grad():
        for i in range(0, len(dataset), batch_size):
            items = [dataset[j] for j in range(i, min(i + batch_size, len(dataset)))]
            b = collate_fn(items)
            if with_loss:
                o = model(input_features=b["input_features"], attention_mask=b["attention_mask"],
                          labels=b["labels"], decoder_attention_mask=b["decoder_attention_mask"])
                k = int((b["labels"] != -100).sum())
                nll += float(o.loss) * k
                n_tok += k
            gen = model.generate(input_features=b["input_features"],
                                 attention_mask=b["attention_mask"], **GEN_KWARGS)
            preds = tokenizer.batch_decode(gen, skip_special_tokens=True)
            lab = torch.where(b["labels"] != -100, b["labels"], tokenizer.pad_token_id)
            legacy = tokenizer.batch_decode(lab, skip_special_tokens=True)
            for it, p, lr in zip(items, preds, legacy):
                rows.append({"sample_id": it["file_id"].replace("_holistic", ""),
                             "reference": it["text"], "reference_truncated_label": lr.strip(),
                             "prediction": p.strip()})
    if was:
        model.train()
    return rows, (nll / n_tok if n_tok else None)


def summarise(rows: list[dict], overlap_ids: set | None = None) -> dict:
    out = {"full_ref": score([r["reference"] for r in rows], [r["prediction"] for r in rows]),
           "legacy_truncated_ref": {k: v for k, v in score(
               [r["reference_truncated_label"] for r in rows],
               [r["prediction"] for r in rows]).items() if k in ("bleu", "chrf", "wer", "cer")}}
    if overlap_ids:
        for name, sel in (("overlapping", True), ("non_overlapping", False)):
            sub = [r for r in rows if (r["sample_id"] in overlap_ids) == sel]
            out[name] = score([r["reference"] for r in sub], [r["prediction"] for r in sub]) if sub else None
    return out


# --------------------------------------------------------------------------- callback
class EpochRecorder(TrainerCallback):
    def __init__(self, out: Path, frozen_ds, collate_fn, tokenizer, batch_size, overlap_ids):
        self.out = out
        self.frozen_ds = frozen_ds
        self.collate_fn = collate_fn
        self.tokenizer = tokenizer
        self.batch_size = batch_size
        self.overlap_ids = overlap_ids
        self.step_f = open(out / "step_log.jsonl", "w")
        self.epoch_f = open(out / "epoch_log.jsonl", "a")
        self.losses: list[float] = []
        self.t0 = time.time()
        self.t_epoch = time.time()
        self.pending: dict | None = None
        self.stop_reason = None
        self.val_holder: dict = {}

    def on_log(self, args, state, control, logs=None, **kw):
        if logs and "loss" in logs and "eval_loss" not in logs:
            gn = logs.get("grad_norm")
            if not math.isfinite(logs["loss"]) or (gn is not None and not math.isfinite(gn)):
                self.stop_reason = f"non-finite loss/grad_norm at step {state.global_step}"
                control.should_training_stop = True
            self.losses.append(logs["loss"])
            self.step_f.write(json.dumps({
                "global_step": state.global_step, "epoch": state.epoch, "loss": logs["loss"],
                "learning_rate": logs.get("learning_rate"), "grad_norm": gn,
                "elapsed_s": round(time.time() - self.t0, 2)}) + "\n")
            self.step_f.flush()

    def on_evaluate(self, args, state, control, metrics=None, model=None, **kw):
        epoch = state.global_step // EVAL_EVERY  # P0-11: eval index (= P0.2 epoch number)
        t = time.time()
        rows, floss = generate_rows(model, self.frozen_ds, self.collate_fn, self.tokenizer,
                                    self.batch_size)
        frozen = summarise(rows, self.overlap_ids)
        write_json(self.out / "frozen_predictions" / f"epoch_{epoch:02d}.json", rows)
        val = self.val_holder.pop("summary", None)
        self.pending = {
            "epoch": epoch, "global_step": state.global_step,
            "train_loss_mean": float(np.mean(self.losses)) if self.losses else None,
            "train_steps_in_epoch": len(self.losses),
            "lr_last_step": None,
            "val_loss": metrics.get("eval_loss"), "val": val,
            "frozen_loss": floss, "frozen": frozen,
            "frozen_eval_seconds": round(time.time() - t, 1),
            "val_eval_seconds": metrics.get("eval_runtime"),
            "epoch_wall_seconds": round(time.time() - self.t_epoch, 1),
        }
        self.losses = []
        f = frozen["full_ref"]
        print(f"[epoch {epoch}] train_loss={self.pending['train_loss_mean']:.4f} "
              f"val_loss={self.pending['val_loss']:.4f} val_BLEU={val['full_ref']['bleu']:.2f} "
              f"val_unique={val['full_ref']['unique_predictions']}/{val['full_ref']['n']} | "
              f"frozen BLEU={f['bleu']:.2f} chrF={f['chrf']:.2f} WER={f['wer']:.3f} "
              f"unique={f['unique_predictions']}/{f['n']} top1={f['top1_count']} "
              f"({f['top1_fraction']:.1%}) {f['top1_prediction'][:60]!r}", flush=True)

    def on_save(self, args, state, control, **kw):
        if self.pending is None:
            return
        ckpt = Path(args.output_dir) / f"checkpoint-{state.global_step}"
        self.pending["checkpoint"] = str(ckpt) if (ckpt / "model.safetensors").exists() else None
        self.pending["best_metric_so_far"] = state.best_metric
        self.pending["best_checkpoint_so_far"] = state.best_model_checkpoint
        self.epoch_f.write(json.dumps(self.pending, ensure_ascii=False) + "\n")
        self.epoch_f.flush()
        self.pending = None
        self.t_epoch = time.time()


class UpstreamOptimizerTrainer(Seq2SeqTrainer):
    """Copy of the Adafactor param grouping in src/train.py (CustomSeq2SeqTrainer)."""

    def create_optimizer(self):
        if self.optimizer is None:
            decay = self.get_decay_parameter_names(self.model)
            named = [(n, p) for n, p in self.model.named_parameters() if p.requires_grad]
            lr, wd = self.args.learning_rate, self.args.weight_decay
            groups = [
                {"params": [p for n, p in named if n in decay and "t5" not in n], "weight_decay": wd, "lr": lr},
                {"params": [p for n, p in named if n not in decay and "t5" not in n], "weight_decay": 0.0, "lr": lr},
                {"params": [p for n, p in named if n in decay and "t5" in n], "weight_decay": wd, "lr": lr * 0.1},
                {"params": [p for n, p in named if n not in decay and "t5" in n], "weight_decay": 0.0, "lr": lr * 0.1},
            ]
            from transformers.optimization import Adafactor

            self.optimizer = Adafactor(groups, scale_parameter=False, relative_step=False,
                                       warmup_init=False, lr=lr)
        return self.optimizer


def write_tables(out: Path, records: list[dict], best_ckpt: str | None) -> None:
    cols = ["epoch", "train_loss", "val_loss", "val_bleu", "val_chrf", "val_wer", "val_unique",
            "frozen_loss", "frozen_bleu", "frozen_chrf", "frozen_wer", "frozen_unique",
            "frozen_top1_count", "frozen_top1_pct", "frozen_top1_prediction",
            "val_bleu_legacy", "frozen_bleu_legacy", "is_best", "checkpoint"]
    rows = []
    for r in records:
        v, f = r["val"]["full_ref"], r["frozen"]["full_ref"]
        rows.append({
            "epoch": r["epoch"], "train_loss": round(r["train_loss_mean"], 4),
            "val_loss": round(r["val_loss"], 4), "val_bleu": round(v["bleu"], 2),
            "val_chrf": round(v["chrf"], 2), "val_wer": round(v["wer"], 4),
            "val_unique": f"{v['unique_predictions']}/{v['n']}",
            "frozen_loss": round(r["frozen_loss"], 4), "frozen_bleu": round(f["bleu"], 2),
            "frozen_chrf": round(f["chrf"], 2), "frozen_wer": round(f["wer"], 4),
            "frozen_unique": f"{f['unique_predictions']}/{f['n']}",
            "frozen_top1_count": f["top1_count"], "frozen_top1_pct": round(100 * f["top1_fraction"], 1),
            "frozen_top1_prediction": f["top1_prediction"],
            "val_bleu_legacy": round(r["val"]["legacy_truncated_ref"]["bleu"], 2),
            "frozen_bleu_legacy": round(r["frozen"]["legacy_truncated_ref"]["bleu"], 2),
            "is_best": r.get("checkpoint") is not None and r.get("checkpoint") == best_ckpt,
            "checkpoint": r.get("checkpoint"),
        })
    with open(out / "epoch_table.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    with open(out / "epoch_table.md", "w") as fh:
        fh.write("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n")
        for r in rows:
            fh.write("| " + " | ".join(str(r[c]).replace("|", "\\|") for c in cols) + " |\n")


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="P0-11 supervised-data scaling (P0.2 recipe, compute-matched)")
    ap.add_argument("--stage-dir", required=True)
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--split-json", required=True)
    ap.add_argument("--raw-dir", required=True, help="dir with how2sign_realigned_{train,val,test}.csv")
    ap.add_argument("--frozen-landmarks", required=True)
    ap.add_argument("--frozen-metadata", required=True)
    ap.add_argument("--frozen-denylist", default=None)
    ap.add_argument("--how2sign-v2-manifest", default=None)
    ap.add_argument("--baseline-checkpoint", default=None,
                    help="old 1-epoch checkpoint to re-score on val + frozen before training")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--train-limit", type=int, default=0, help="SMOKE ONLY: first N train files")
    ap.add_argument("--train-ids", required=True)
    ap.add_argument("--max-steps", type=int, default=10320)
    args = ap.parse_args()

    out = Path(args.output_dir)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"STOP: {out} exists and is not empty; refusing to overwrite.")
    out.mkdir(parents=True)
    t_start = time.time()

    tokenizer = T5TokenizerFast.from_pretrained(T5_MODEL)
    sets = build_sets(args, tokenizer)
    rep = overlap_report(sets, args)
    ids_dir = out / "ids"
    ids_dir.mkdir()
    for k in ("train", "val", "frozen"):
        (ids_dir / f"{k}_ids.txt").write_text("\n".join(sets[f"{k}_ids"]) + "\n")
    write_json(ids_dir / "overlap_report.json", rep)
    overlap_ids = set(rep["frozen_ids_with_any_overlap"])
    print("[sets]", json.dumps({**rep["counts"], "video_counts": rep["video_counts"],
                                "frozen_official_split": rep["frozen_official_split_counts"],
                                "frozen_with_any_overlap": len(overlap_ids),
                                **{f"{a}_{t}": len(rep[a][t]) for a in ("train_vs_val", "frozen_vs_train", "frozen_vs_val")
                                   for t in ("clip_overlap", "video_overlap", "normalised_text_overlap")}}),
          flush=True)

    train_files = sets["train_files"][: args.train_limit] if args.train_limit else sets["train_files"]
    common = dict(data_dir=args.stage_dir, metadata_dict=sets["metadata"], max_len=150,
                  include_face=True, i3d_dir=None)
    train_ds = ASLLandmarkDataset(file_list=train_files, training=True, **common)
    val_ds = ASLLandmarkDataset(file_list=sets["val_files"], training=False, **common)
    frozen_ds = ASLLandmarkDataset(data_dir=args.frozen_landmarks, metadata_dict=sets["frozen_meta"],
                                   file_list=sets["frozen_files"], max_len=150, include_face=True,
                                   training=False)
    assert len(val_ds) == 366 and len(frozen_ds) == 147, (len(val_ds), len(frozen_ds))
    assert len(train_ds) == len(train_files), (len(train_ds), len(train_files))
    collate_fn = CollateLandmarks(tokenizer=tokenizer, max_target_len=30)

    def build_model():
        m = ASLTranslationModel(input_dim=501, input_i3d_dim=None, d_model=512,
                                t5_model_name=T5_MODEL, num_layers=4, num_heads=4, kernel_size=31)
        m.generation_config.max_length = 30
        return m

    if args.baseline_checkpoint:
        raise SystemExit("P0-11: --baseline-checkpoint not supported")
        from safetensors.torch import load_file

        bm = build_model()
        bm.load_state_dict(load_file(str(Path(args.baseline_checkpoint) / "model.safetensors"), device="cpu"))
        res = {}
        for name, ds in (("val366", val_ds), ("frozen147", frozen_ds)):
            rows, loss = generate_rows(bm, ds, collate_fn, tokenizer, args.batch_size)
            write_json(out / "baseline_1epoch" / f"{name}_predictions.json", rows)
            res[name] = {"loss": loss, **summarise(rows, overlap_ids if name == "frozen147" else None)}
        res["checkpoint"] = args.baseline_checkpoint
        write_json(out / "baseline_1epoch" / "metrics.json", res)
        print("[baseline 1-epoch]", json.dumps({k: {"loss": v["loss"], **{m: v["full_ref"][m] for m in (
            "bleu", "chrf", "wer", "unique_predictions", "top1_count")}, "legacy_bleu": v["legacy_truncated_ref"]["bleu"]}
            for k, v in res.items() if k != "checkpoint"}), flush=True)
        del bm

    set_seed(args.seed)
    model = build_model()
    h = hashlib.sha256()
    for n, p in sorted(model.state_dict().items()):
        h.update(n.encode())
        h.update(p.detach().numpy().tobytes())
    init_hash = h.hexdigest()

    rec = EpochRecorder(out, frozen_ds, collate_fn, tokenizer, args.batch_size, overlap_ids)
    val_ids = [clean_id(p) for p in val_ds.filepaths]
    val_refs = [sets["metadata"][i] for i in val_ids]
    holder: dict = {}

    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        if isinstance(preds, tuple):
            preds = preds[0]
        preds = np.where(preds != -100, preds, tokenizer.pad_token_id)
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        dp = [p.strip() for p in tokenizer.batch_decode(preds, skip_special_tokens=True)]
        dl = [x.strip() for x in tokenizer.batch_decode(labels, skip_special_tokens=True)]
        assert len(dp) == len(val_ids)
        rows = [{"sample_id": i, "reference": r, "reference_truncated_label": lab, "prediction": p}
                for i, r, lab, p in zip(val_ids, val_refs, dl, dp)]
        epoch = holder["trainer"].state.global_step // EVAL_EVERY
        write_json(out / "val_predictions" / f"epoch_{epoch:02d}.json", rows)
        s = summarise(rows)
        rec.val_holder["summary"] = s
        return {"bleu": s["full_ref"]["bleu"], "chrf": s["full_ref"]["chrf"],
                "wer": s["full_ref"]["wer"], "unique": s["full_ref"]["unique_predictions"],
                "legacy_bleu": s["legacy_truncated_ref"]["bleu"],
                "legacy_wer": s["legacy_truncated_ref"]["wer"]}

    ckpt_dir = out / "checkpoints"
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(ckpt_dir),
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=1,
        learning_rate=args.lr,
        weight_decay=0.01,
        logging_steps=1,
        eval_strategy="steps",
        eval_steps=EVAL_EVERY,
        save_strategy="steps",
        save_steps=EVAL_EVERY,
        save_total_limit=2,
        predict_with_generate=True,
        generation_max_length=GEN_KWARGS["max_length"],
        generation_num_beams=GEN_KWARGS["num_beams"],
        fp16=False,
        report_to="none",
        remove_unused_columns=False,
        warmup_ratio=0.1,
        lr_scheduler_type="linear",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        optim="adafactor",
        gradient_checkpointing=True,
        dataloader_num_workers=1,
        dataloader_pin_memory=True,
        use_cpu=True,
        seed=args.seed,
    )
    trainer = UpstreamOptimizerTrainer(
        model=model, args=training_args, train_dataset=train_ds, eval_dataset=val_ds,
        data_collator=collate_fn, processing_class=tokenizer, compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=args.patience), rec],
    )
    holder["trainer"] = trainer
    import transformers

    steps_per_epoch = math.ceil(len(train_ds) / args.batch_size)
    write_json(out / "run_config.json", {
        "argv": sys.argv, "args": vars(args), "deviations_from_upstream_train_py": DEVIATIONS,
        "p011_deviations_from_train_p02": P011_DEVIATIONS,
        "train_ids_sha256": hashlib.sha256(open(args.train_ids, "rb").read()).hexdigest(),
        "deviations_shared_with_old_1epoch_run": [
            "gradient_accumulation_steps 8 -> 1", "logging_steps 10 -> 1", "CPU (use_cpu=True)"],
        "weights": {"conformer_and_bridge": f"fresh init after set_seed({args.seed})",
                    "t5": f"HF pretrained '{T5_MODEL}' (encoder deleted), dropout_rate "
                          f"{model.t5.config.dropout_rate} (unchanged)",
                    "checkpoint_loaded": None, "initial_state_dict_sha256": init_hash},
        "n_train": len(train_ds), "n_val": len(val_ds), "n_frozen": len(frozen_ds),
        "augmentation": {"train": True, "val": False, "frozen": False},
        "steps_per_epoch": steps_per_epoch, "planned_total_steps": args.max_steps,
        "planned_warmup_steps": math.ceil(0.1 * args.max_steps), "eval_every_steps": EVAL_EVERY,
        "data_epochs_in_budget": round(args.max_steps / steps_per_epoch, 3),
        "early_stopping": {"metric": "eval_loss (366 val)", "patience_epochs": args.patience,
                           "frozen_set_used_for_selection": False},
        "generate_kwargs": GEN_KWARGS,
        "effective_training_args": {k: str(getattr(trainer.args, k)) for k in [
            "gradient_accumulation_steps", "per_device_train_batch_size", "learning_rate",
            "weight_decay", "warmup_ratio", "lr_scheduler_type", "optim", "max_grad_norm",
            "gradient_checkpointing", "seed", "num_train_epochs", "save_total_limit",
            "load_best_model_at_end", "metric_for_best_model", "dataloader_num_workers",
            "generation_max_length", "generation_num_beams", "device"]},
        "versions": {"torch": torch.__version__, "transformers": transformers.__version__,
                     "python": sys.version.split()[0]},
    })
    print(f"[config] device={trainer.args.device} n_train={len(train_ds)} steps/epoch={steps_per_epoch} "
          f"planned_steps={args.max_steps} init={init_hash[:12]}", flush=True)

    result = trainer.train()
    rec.step_f.close()
    rec.epoch_f.close()

    records = [json.loads(line) for line in open(out / "epoch_log.jsonl")]
    best = trainer.state.best_model_checkpoint
    write_tables(out, records, best)
    best_rec = next((r for r in records if r.get("checkpoint") == best), None)
    write_json(out / "summary.json", {
        "stop_reason": rec.stop_reason,
        "epochs_completed": len(records),
        "global_step": trainer.state.global_step,
        "early_stopped": len(records) < args.max_steps // EVAL_EVERY and rec.stop_reason is None,
        "patience": args.patience,
        "best_epoch": best_rec["epoch"] if best_rec else None,
        "best_val_loss": trainer.state.best_metric,
        "best_checkpoint": best,
        "train_runtime_s_hf": result.metrics.get("train_runtime"),
        "wall_clock_total_s": round(time.time() - t_start, 1),
    })
    print("[done]", json.load(open(out / "summary.json")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
