"""
Tiny-set overfit experiment (P0.1).

Trains the unchanged Conformer -> T5 model on a fixed set of N training clips and
periodically runs real ``model.generate`` on the very same clips, to check that the
pipeline can memorise a small training set.

Reuses the upstream dataset, collator, tokenizer, model, loss (T5 cross-entropy via
``labels``) and optimizer/scheduler configuration from ``src/train.py``. Differences
from ``src/train.py`` are deliberate and limited to what the experiment needs:

- gradient_accumulation_steps 8 -> 1 (32 clips / batch 8 = 4 optimizer updates per epoch)
- random data augmentation disabled (``training=False``) so every epoch and every
  generate call sees identical inputs
- train set == generate set == the fixed N clips; no signer split, no Trainer eval,
  no EarlyStopping / load_best_model_at_end; only the final weights are saved
- seeded before model construction (upstream builds the model before the Trainer seeds)
- logging_steps 10 -> 1, dataloader_num_workers 1 -> 0
- ``--lr-scheduler`` (default ``linear`` = upstream) can switch to ``constant_with_warmup``
  for scheduler controls; warmup ratio, base lr and the 0.1x T5 group are unchanged
- ``--t5-dropout`` (default 0.1 = t5-small config) sets every dropout path inside the T5
  module; Conformer / bridge dropout are untouched
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from transformers import (  # noqa: E402
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    T5TokenizerFast,
    TrainerCallback,
    set_seed,
)

from src.dataset import ASLLandmarkDataset, CollateLandmarks  # noqa: E402
from src.models.translation_model import ASLTranslationModel  # noqa: E402

T5_MODEL = "t5-small"


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- sampling
def select_samples(args, tokenizer) -> dict:
    """Deterministically pick N clips from the train split of holdout_split.json."""
    split = json.load(open(args.split_json))
    train_ids = list(split["train"])
    val_ids = set(split["val"])
    with open(args.metadata, newline="") as f:
        refs = {r["SENTENCE_NAME"]: r["SENTENCE"] for r in csv.DictReader(f)}

    rows, reasons = [], Counter()
    for sid in sorted(train_ids):
        text = refs.get(sid, "")
        if not text.strip():
            reasons["empty_reference"] += 1
            continue
        if not (Path(args.stage_dir) / f"{sid}_holistic.npy").exists():
            reasons["missing_landmark_file"] += 1
            continue
        ids = tokenizer(text).input_ids  # includes </s>
        if len(ids) > args.max_target_len:
            reasons["would_be_truncated"] += 1
            continue
        if tokenizer.decode(ids, skip_special_tokens=True) != text:
            reasons["tokenizer_roundtrip_differs"] += 1
            continue
        rows.append((sid, text, len(ids)))

    rng = random.Random(args.seed)
    chosen = rng.sample(rows, args.n)
    assert not ({c[0] for c in chosen} & val_ids), "sampled a validation ID"
    assert all(c[0] in set(train_ids) for c in chosen)

    return {
        "rule": (
            f"Candidates = holdout_split.json['train'] ({len(train_ids)} IDs), sorted. "
            f"Drop: empty reference, missing landmark file, t5-small token length (incl. </s>) "
            f"> max_target_len={args.max_target_len} (would be truncated by the collator), and "
            f"references whose tokenize->decode round trip differs. Then "
            f"random.Random({args.seed}).sample(eligible, {args.n}); order kept as sampled."
        ),
        "seed": args.seed,
        "n": args.n,
        "split_json": str(args.split_json),
        "split_json_sha256": hashlib.sha256(open(args.split_json, "rb").read()).hexdigest(),
        "metadata": str(args.metadata),
        "train_ids_total": len(train_ids),
        "excluded_counts": dict(reasons),
        "eligible_count": len(rows),
        "tokenizer": T5_MODEL,
        "samples": [
            {"sample_id": s, "reference": t, "n_target_tokens": n} for s, t, n in chosen
        ],
    }


def load_or_create_selection(args, tokenizer) -> dict:
    manifest_path = Path(args.sample_dir) / f"tiny{args.n}_seed{args.seed}_manifest.json"
    ids_path = Path(args.sample_dir) / f"tiny{args.n}_seed{args.seed}_ids.txt"
    fresh = select_samples(args, tokenizer)
    if manifest_path.exists():
        saved = json.load(open(manifest_path))
        if [s["sample_id"] for s in saved["samples"]] != [
            s["sample_id"] for s in fresh["samples"]
        ]:
            raise SystemExit(f"STOP: {manifest_path} differs from a fresh re-selection.")
        return saved
    fresh["ids_sha256"] = sha256_text(
        "\n".join(s["sample_id"] for s in fresh["samples"]) + "\n"
    )
    write_json(manifest_path, fresh)
    ids_path.write_text("\n".join(s["sample_id"] for s in fresh["samples"]) + "\n")
    return fresh


# --------------------------------------------------------------------------- metrics
def text_metrics(refs: list[str], hyps: list[str]) -> dict:
    import jiwer
    import sacrebleu

    safe_h = [h if h.strip() else " " for h in hyps]
    counts = Counter(hyps)
    top_pred, top_n = counts.most_common(1)[0]
    return {
        "bleu": sacrebleu.corpus_bleu(hyps, [refs]).score,
        "chrf": sacrebleu.corpus_chrf(hyps, [refs]).score,
        "wer": jiwer.wer(refs, safe_h),
        "exact_match": sum(r.strip() == h.strip() for r, h in zip(refs, hyps)),
        "n": len(refs),
        "unique_predictions": len(counts),
        "top_prediction": top_pred,
        "top_prediction_fraction": top_n / len(hyps),
    }


GEN_KWARGS = {"max_length": 30, "num_beams": 1, "do_sample": False}


def run_generate(model, dataset, collate_fn, tokenizer, device, batch_size) -> list[dict]:
    """Real autoregressive generation; only features + mask are passed to the model."""
    was_training = model.training
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(dataset), batch_size):
            items = [dataset[j] for j in range(i, min(i + batch_size, len(dataset)))]
            batch = collate_fn(items)
            gen = model.generate(
                input_features=batch["input_features"].to(device),
                attention_mask=batch["attention_mask"].to(device),
                **GEN_KWARGS,
            )
            preds = tokenizer.batch_decode(gen, skip_special_tokens=True)
            for item, p, seq in zip(items, preds, gen.tolist()):
                body = seq[1:]  # drop decoder start token
                eos = tokenizer.eos_token_id
                content = body[: body.index(eos)] if eos in body else [
                    t for t in body if t != tokenizer.pad_token_id]
                out.append(
                    {
                        "sample_id": item["file_id"].replace("_holistic", ""),
                        "reference": item["text"],
                        "prediction": p.strip(),
                        "generated_ids": content,
                        "emitted_eos": eos in body,
                    }
                )
    if was_training:
        model.train()
    return out


def teacher_forced_eval(model, dataset, collate_fn, device, batch_size) -> list[dict]:
    """eval() + no_grad forward with gold decoder inputs; per-sample loss / token accuracy."""
    import torch.nn.functional as F

    was_training = model.training
    model.eval()
    rows = []
    with torch.no_grad():
        for i in range(0, len(dataset), batch_size):
            items = [dataset[j] for j in range(i, min(i + batch_size, len(dataset)))]
            b = collate_fn(items)
            o = model(input_features=b["input_features"].to(device),
                      attention_mask=b["attention_mask"].to(device),
                      labels=b["labels"].to(device),
                      decoder_attention_mask=b["decoder_attention_mask"].to(device))
            labels = b["labels"].to(device)
            ce = F.cross_entropy(o.logits.transpose(1, 2), labels, ignore_index=-100,
                                 reduction="none")
            pred = o.logits.argmax(-1)
            for k in range(labels.size(0)):
                v = labels[k] != -100
                lab, pr = labels[k][v].tolist(), pred[k][v].tolist()
                wrong = [j for j, (a, c) in enumerate(zip(lab, pr)) if a != c]
                rows.append({"tf_nll_sum": float(ce[k][v].sum()), "tf_n_tokens": len(lab),
                             "tf_wrong_positions": wrong})
    if was_training:
        model.train()
    return rows


def first_error_pos(ref_ids: list[int], gen_ids: list[int], emitted_eos: bool) -> int | None:
    """Index (in content tokens) of the first greedy token that differs from the reference."""
    for j, (a, c) in enumerate(zip(ref_ids, gen_ids)):
        if a != c:
            return j
    if len(ref_ids) == len(gen_ids) and emitted_eos:
        return None
    return min(len(ref_ids), len(gen_ids))


def dropout_inventory(module) -> dict:
    """Every dropout rate that can execute inside ``module``."""
    from transformers.models.t5.modeling_t5 import T5Attention

    inv = Counter()
    for m in module.modules():
        if isinstance(m, torch.nn.Dropout):
            inv[f"nn.Dropout(p={m.p})"] += 1
        if isinstance(m, T5Attention):
            inv[f"T5Attention.dropout(float, functional)={m.dropout}"] += 1
        if isinstance(m, torch.nn.MultiheadAttention):
            inv[f"nn.MultiheadAttention.dropout={m.dropout}"] += 1
    return dict(sorted(inv.items()))


def set_t5_dropout(t5, p: float) -> None:
    """T5 runs dropout via nn.Dropout modules AND a float in T5Attention (F.dropout on
    attention weights, modeling_t5.py:562); config.dropout_rate is only read at init."""
    from transformers.models.t5.modeling_t5 import T5Attention

    for m in t5.modules():
        if isinstance(m, torch.nn.Dropout):
            m.p = p
        if isinstance(m, T5Attention):
            m.dropout = p
    t5.config.dropout_rate = p


def dropout_runtime_check(model, batch) -> dict:
    """Max |logit| difference between two train-mode forwards (different RNG) with only one
    sub-module in train mode. Global RNG state is restored so training is unaffected."""
    state = torch.get_rng_state()
    inputs = {k: batch[k] for k in ("input_features", "attention_mask", "labels",
                                    "decoder_attention_mask")}

    def diff(enc_train: bool, t5_train: bool) -> float:
        model.eval()
        model.encoder.train(enc_train)
        model.modality_bridge.train(enc_train)
        model.t5.train(t5_train)
        torch.manual_seed(1)
        a = model(**inputs).logits
        torch.manual_seed(2)
        b = model(**inputs).logits
        return float((a - b).abs().max())

    try:
        with torch.no_grad():
            res = {"t5_train_only_logit_maxdiff": diff(False, True),
                   "encoder_bridge_train_only_logit_maxdiff": diff(True, False),
                   "all_train_logit_maxdiff": diff(True, True)}
    finally:
        torch.set_rng_state(state)
        model.train()
    res["t5_dropout_active"] = res["t5_train_only_logit_maxdiff"] > 0
    res["encoder_dropout_active"] = res["encoder_bridge_train_only_logit_maxdiff"] > 0
    return res


# --------------------------------------------------------------------------- callback
class RecorderCallback(TrainerCallback):
    def __init__(self, out_dir, dataset, collate_fn, tokenizer, device, args):
        self.out_dir = out_dir
        self.dataset = dataset
        self.collate_fn = collate_fn
        self.tokenizer = tokenizer
        self.device = device
        self.args = args
        self.optimizer_steps = 0
        self.t0 = None
        self.step_f = open(out_dir / "step_log.jsonl", "w")
        self.gen_f = open(out_dir / "generate_log.jsonl", "w")
        self.epoch_f = open(out_dir / "epoch_log.jsonl", "w")
        self.epoch_losses: list[float] = []
        self.eval_seconds = 0.0
        self.stop_reason = None
        self.last_batch_ids: list[str] = []

    def evaluate(self, model, epoch: int, global_step: int) -> dict:
        t = time.time()
        rows = run_generate(
            model, self.dataset, self.collate_fn, self.tokenizer, self.device,
            self.args.batch_size,
        )
        tf = teacher_forced_eval(model, self.dataset, self.collate_fn, self.device,
                                 self.args.batch_size)
        dt = time.time() - t
        self.eval_seconds += dt
        for r, f in zip(rows, tf):
            ref_ids = self.tokenizer(r["reference"]).input_ids[:-1]
            r["n_target_tokens_incl_eos"] = len(ref_ids) + 1
            r["is_long_ge20"] = len(ref_ids) + 1 >= 20
            r["exact"] = r["reference"].strip() == r["prediction"].strip()
            r["first_error_pos"] = first_error_pos(ref_ids, r["generated_ids"], r["emitted_eos"])
            r["tf_loss"] = round(f["tf_nll_sum"] / f["tf_n_tokens"], 5)
            r["tf_token_acc"] = round(1 - len(f["tf_wrong_positions"]) / f["tf_n_tokens"], 5)
            r["tf_wrong_positions"] = f["tf_wrong_positions"]
        m = text_metrics([r["reference"] for r in rows], [r["prediction"] for r in rows])
        n_tok = sum(f["tf_n_tokens"] for f in tf)
        long_rows = [r for r in rows if r["is_long_ge20"]]
        m.update({
            "tf_eval_loss": sum(f["tf_nll_sum"] for f in tf) / n_tok,
            "tf_eval_token_acc": 1 - sum(len(f["tf_wrong_positions"]) for f in tf) / n_tok,
            "tf_samples_all_correct": sum(not f["tf_wrong_positions"] for f in tf),
            "long_n": len(long_rows),
            "long_exact": sum(r["exact"] for r in long_rows),
        })
        rec = {"epoch": epoch, "global_step": global_step, "generate_seconds": round(dt, 2),
               **m}
        self.gen_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self.gen_f.flush()
        write_json(self.out_dir / "predictions" / f"epoch_{epoch:03d}.json", rows)
        print(
            f"[generate] epoch={epoch} step={global_step} BLEU={m['bleu']:.2f} "
            f"chrF={m['chrf']:.2f} WER={m['wer']:.3f} exact={m['exact_match']}/{m['n']} "
            f"unique={m['unique_predictions']} top_frac={m['top_prediction_fraction']:.3f} "
            f"tf_loss={m['tf_eval_loss']:.4f} tf_acc={m['tf_eval_token_acc']:.4f} "
            f"long_exact={m['long_exact']}/{m['long_n']} ({dt:.1f}s)",
            flush=True,
        )
        return rec

    def on_train_begin(self, args, state, control, model=None, **kw):
        self.t0 = time.time()
        if self.args.eval_every > 0:
            self.evaluate(model, 0, 0)

    def on_optimizer_step(self, args, state, control, **kw):
        self.optimizer_steps += 1

    def on_log(self, args, state, control, logs=None, **kw):
        if logs and "loss" in logs:
            if not all(math.isfinite(logs.get(k) or 0.0) for k in ("loss", "grad_norm")):
                self.stop_reason = f"non-finite loss/grad_norm at step {state.global_step}"
                control.should_training_stop = True
            self.epoch_losses.append(logs["loss"])
            rec = {"global_step": state.global_step, "epoch": state.epoch,
                   "loss": logs["loss"], "learning_rate": logs.get("learning_rate"),
                   "grad_norm": logs.get("grad_norm"),
                   "batch_ids": self.last_batch_ids,
                   "elapsed_s": round(time.time() - self.t0, 2)}
            self.step_f.write(json.dumps(rec) + "\n")
            self.step_f.flush()

    def on_epoch_end(self, args, state, control, model=None, **kw):
        epoch = int(round(state.epoch))
        rec = {"epoch": epoch, "global_step": state.global_step,
               "optimizer_steps": self.optimizer_steps,
               "mean_train_loss": float(np.mean(self.epoch_losses)) if self.epoch_losses else None,
               "n_logged_steps": len(self.epoch_losses),
               "elapsed_s": round(time.time() - self.t0, 2)}
        self.epoch_f.write(json.dumps(rec) + "\n")
        self.epoch_f.flush()
        print(f"[epoch] {rec}", flush=True)
        self.epoch_losses = []
        if self.args.eval_every > 0 and (
            epoch % self.args.eval_every == 0 or epoch == self.args.epochs
        ):
            self.evaluate(model, epoch, state.global_step)

    def close(self):
        for f in (self.step_f, self.gen_f, self.epoch_f):
            f.close()


# --------------------------------------------------------------------------- optimizer
class UpstreamOptimizerTrainer(Seq2SeqTrainer):
    """Copy of the Adafactor param grouping in src/train.py (CustomSeq2SeqTrainer)."""

    recorder = None

    def training_step(self, model, inputs, *a, **kw):
        if self.recorder is not None:
            self.recorder.last_batch_ids = [
                f.replace("_holistic", "") for f in inputs.get("file_ids", [])]
        return super().training_step(model, inputs, *a, **kw)

    def create_optimizer(self):
        if self.optimizer is None:
            decay = self.get_decay_parameter_names(self.model)
            named = [(n, p) for n, p in self.model.named_parameters() if p.requires_grad]
            lr = self.args.learning_rate
            wd = self.args.weight_decay
            groups = [
                {"params": [p for n, p in named if n in decay and "t5" not in n],
                 "weight_decay": wd, "lr": lr},
                {"params": [p for n, p in named if n not in decay and "t5" not in n],
                 "weight_decay": 0.0, "lr": lr},
                {"params": [p for n, p in named if n in decay and "t5" in n],
                 "weight_decay": wd, "lr": lr * 0.1},
                {"params": [p for n, p in named if n not in decay and "t5" in n],
                 "weight_decay": 0.0, "lr": lr * 0.1},
            ]
            from transformers.optimization import Adafactor

            self.optimizer = Adafactor(
                groups, scale_parameter=False, relative_step=False, warmup_init=False,
                lr=lr,
            )
        return self.optimizer


# --------------------------------------------------------------------------- checks
def preflight(dataset, collate_fn, tokenizer, manifest, args) -> dict:
    """Input / label / mask sanity checks on the exact tensors used for training."""
    expected = [s["sample_id"] for s in manifest["samples"]]
    got = [os.path.basename(p).replace("_holistic.npy", "") for p in dataset.filepaths]
    checks = {"loaded_ids_equal_manifest": got == expected, "n_loaded": len(got)}

    # Same inputs every time (no augmentation) and no silent zero-fallback on load.
    a, b = dataset[0], dataset[0]
    checks["deterministic_features"] = bool(torch.equal(a["features"], b["features"]))
    load_ok = []
    for i in range(len(dataset)):
        _, _, _, _, _, failed = dataset._load_landmarks(dataset.filepaths[i])
        load_ok.append(not failed)
    checks["all_landmarks_loaded"] = all(load_ok)

    per_sample, batch_shapes = [], []
    for i in range(0, len(dataset), args.batch_size):
        items = [dataset[j] for j in range(i, min(i + args.batch_size, len(dataset)))]
        batch = collate_fn(items)
        feats, mask, labels = batch["input_features"], batch["attention_mask"], batch["labels"]
        dec_mask = batch["decoder_attention_mask"]
        batch_shapes.append({
            "input_features": list(feats.shape), "attention_mask": list(mask.shape),
            "labels": list(labels.shape), "decoder_attention_mask": list(dec_mask.shape),
            "features_finite": bool(torch.isfinite(feats).all()),
            "features_abs_max": float(feats.abs().max()),
            "mask_values": sorted(set(mask.unique().tolist())),
            "mask_row_sums": mask.sum(1).int().tolist(),
            "padded_region_zero": bool((feats * (1 - mask).unsqueeze(-1)).abs().max() == 0),
            "labels_minus100_matches_dec_mask0": bool(((labels == -100) == (dec_mask == 0)).all()),
        })
        for k, item in enumerate(items):
            lab = labels[k]
            ids = lab[lab != -100].tolist()
            decoded = tokenizer.decode(ids, skip_special_tokens=True)
            direct = tokenizer(item["text"]).input_ids
            per_sample.append({
                "sample_id": item["file_id"].replace("_holistic", ""),
                "reference": item["text"],
                "target_token_ids": ids,
                "target_decoded": decoded,
                "n_frames_after_stride": int(mask[k].sum()),
                "target_ends_with_eos": ids[-1] == tokenizer.eos_token_id,
                "target_equals_direct_tokenization": ids == direct,
                "decoded_equals_reference": decoded == item["text"],
            })
    checks["all_targets_equal_reference"] = all(
        s["decoded_equals_reference"] and s["target_equals_direct_tokenization"]
        and s["target_ends_with_eos"] for s in per_sample
    )
    checks["batch_shapes"] = batch_shapes
    return {"checks": checks, "targets": per_sample}


def param_snapshot(model) -> dict[str, torch.Tensor]:
    return {n: p.detach().clone() for n, p in model.named_parameters()}


def param_hash(model) -> str:
    h = hashlib.sha256()
    for n, p in sorted(model.state_dict().items()):
        h.update(n.encode())
        h.update(p.detach().cpu().numpy().tobytes())
    return h.hexdigest()


def param_delta(model, before) -> dict:
    groups = {"encoder": 0.0, "modality_bridge": 0.0, "t5": 0.0}
    for n, p in model.named_parameters():
        key = n.split(".")[0]
        if key in groups:
            groups[key] += float((p.detach() - before[n]).pow(2).sum())
    return {k: math.sqrt(v) for k, v in groups.items()}


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--stage-dir", required=True, help="dir with <id>_holistic.npy files")
    ap.add_argument("--metadata", required=True, help="CSV with SENTENCE_NAME,SENTENCE")
    ap.add_argument("--split-json", required=True, help="holdout_split.json (uses 'train')")
    ap.add_argument("--sample-dir", default="experiments/tiny_overfit")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--seed", type=int, default=20260924)
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--eval-every", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--t5-dropout", type=float, default=0.1,
                    help="dropout for every path inside T5 (t5-small default 0.1)")
    ap.add_argument("--lr-scheduler", choices=["linear", "constant_with_warmup"],
                    default="linear", help="linear = upstream src/train.py")
    ap.add_argument("--max-len", type=int, default=150)
    ap.add_argument("--max-target-len", type=int, default=30)
    ap.add_argument("--device", choices=["cpu", "mps"], default="cpu")
    ap.add_argument("--no-save", action="store_true", help="skip saving final weights")
    args = ap.parse_args()

    out = Path(args.output_dir)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"STOP: {out} exists and is not empty; refusing to overwrite.")
    out.mkdir(parents=True, exist_ok=True)

    tokenizer = T5TokenizerFast.from_pretrained(T5_MODEL)
    manifest = load_or_create_selection(args, tokenizer)
    ids = [s["sample_id"] for s in manifest["samples"]]
    metadata = {s["sample_id"]: s["reference"] for s in manifest["samples"]}
    files = [str(Path(args.stage_dir) / f"{sid}_holistic.npy") for sid in ids]

    dataset = ASLLandmarkDataset(
        data_dir=args.stage_dir, metadata_dict=metadata, file_list=files,
        max_len=args.max_len, include_face=True, i3d_dir=None, training=False,
    )
    collate_fn = CollateLandmarks(tokenizer=tokenizer, max_target_len=args.max_target_len)

    pre = preflight(dataset, collate_fn, tokenizer, manifest, args)
    write_json(out / "preflight.json", pre["checks"])
    write_json(out / "targets.json", pre["targets"])
    c = pre["checks"]
    print("[preflight]", {k: v for k, v in c.items() if k != "batch_shapes"}, flush=True)
    if not (c["loaded_ids_equal_manifest"] and c["deterministic_features"]
            and c["all_landmarks_loaded"] and c["all_targets_equal_reference"]):
        raise SystemExit("STOP: preflight failed; see preflight.json")

    # Same construction as src/train.py:193-203. Conformer + bridge are freshly
    # initialised; T5 weights come from the Hugging Face "t5-small" checkpoint.
    set_seed(args.seed)
    input_dim = dataset[0]["features"].shape[1]
    model = ASLTranslationModel(
        input_dim=input_dim, input_i3d_dim=None, d_model=512, t5_model_name=T5_MODEL,
        num_layers=4, num_heads=4, kernel_size=31,
    )
    model.generation_config.max_length = args.max_target_len
    device = torch.device(args.device)
    before = param_snapshot(model)
    init_hash = param_hash(model)
    dropout_info = {"t5_before": dropout_inventory(model.t5)}
    set_t5_dropout(model.t5, args.t5_dropout)
    dropout_info.update({
        "t5_after": dropout_inventory(model.t5),
        "encoder_after": dropout_inventory(model.encoder),
        "modality_bridge_after": dropout_inventory(model.modality_bridge),
        "t5_config_dropout_rate": model.t5.config.dropout_rate,
        "runtime_check": dropout_runtime_check(model, collate_fn([dataset[j] for j in range(
            min(args.batch_size, len(dataset)))])),
    })
    print("[dropout]", json.dumps(dropout_info), flush=True)

    steps_per_epoch = math.ceil(len(dataset) / args.batch_size)
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(out / "trainer"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=1,
        learning_rate=args.lr,
        weight_decay=0.01,
        warmup_ratio=0.1,
        lr_scheduler_type=args.lr_scheduler,
        optim="adafactor",
        gradient_checkpointing=True,
        logging_steps=1,
        eval_strategy="no",
        save_strategy="no",
        report_to="none",
        remove_unused_columns=False,
        dataloader_num_workers=0,
        dataloader_pin_memory=False,
        use_cpu=args.device == "cpu",
        seed=args.seed,
        fp16=False,
    )

    rec = RecorderCallback(out, dataset, collate_fn, tokenizer, device, args)
    UpstreamOptimizerTrainer.recorder = rec
    trainer = UpstreamOptimizerTrainer(
        model=model, args=training_args, train_dataset=dataset,
        data_collator=collate_fn, processing_class=tokenizer, callbacks=[rec],
    )

    import transformers

    run_config = {
        "argv": sys.argv, "args": vars(args),
        "weights": {
            "conformer_encoder_and_modality_bridge": f"fresh random init (torch default), after set_seed({args.seed})",
            "t5": f"Hugging Face pretrained '{T5_MODEL}' (T5ForConditionalGeneration.from_pretrained); its encoder is deleted",
            "checkpoint_loaded": None,
            "initial_state_dict_sha256": init_hash,
        },
        "dropout": dropout_info,
        "input_dim": input_dim,
        "n_params": sum(p.numel() for p in model.parameters()),
        "steps_per_epoch_expected": steps_per_epoch,
        "optimizer_updates_expected": steps_per_epoch * args.epochs,
        "generate_kwargs": GEN_KWARGS,
        "effective_training_args": {k: getattr(trainer.args, k) for k in [
            "gradient_accumulation_steps", "per_device_train_batch_size", "learning_rate",
            "weight_decay", "warmup_ratio", "lr_scheduler_type", "optim", "max_grad_norm",
            "gradient_checkpointing", "seed", "num_train_epochs"]},
        "trainer_device": str(trainer.args.device),
        "versions": {"torch": torch.__version__, "transformers": transformers.__version__,
                     "python": sys.version.split()[0]},
    }
    write_json(out / "run_config.json", run_config)
    print(f"[config] device={trainer.args.device} input_dim={input_dim} "
          f"expected_updates={steps_per_epoch * args.epochs}", flush=True)

    t0 = time.time()
    result = trainer.train()
    wall = time.time() - t0
    rec.close()

    delta = param_delta(model, before)
    final_rows = run_generate(model, dataset, collate_fn, tokenizer, device, args.batch_size)
    final = text_metrics([r["reference"] for r in final_rows], [r["prediction"] for r in final_rows])
    write_json(out / "final_predictions.json", final_rows)
    with open(out / "final_predictions.tsv", "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["sample_id", "exact", "reference", "prediction"])
        for r in final_rows:
            w.writerow([r["sample_id"], int(r["reference"].strip() == r["prediction"].strip()),
                        r["reference"], r["prediction"]])

    summary = {
        "global_step": trainer.state.global_step,
        "stop_reason": rec.stop_reason,
        "optimizer_steps_counted": rec.optimizer_steps,
        "optimizer_updates_expected": steps_per_epoch * args.epochs,
        "train_runtime_s_hf": result.metrics.get("train_runtime"),
        "wall_clock_train_incl_periodic_generate_s": round(wall, 1),
        "periodic_generate_s": round(rec.eval_seconds, 1),
        "param_update_l2": delta,
        "final_generate": final,
        "generate_kwargs": GEN_KWARGS,
        "pass_bleu_gt_80": final["bleu"] > 80,
    }
    write_json(out / "summary.json", summary)
    print("[final]", json.dumps(summary, ensure_ascii=False), flush=True)

    if not args.no_save:
        trainer.save_model(str(out / "final_model"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
