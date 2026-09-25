"""
Input-correspondence diagnostics for one trained checkpoint (no training).

For each evaluation set (366 val, 147 frozen, a fixed train sample) and for the original
pairing plus K fixed-seed derangements of the video inputs (labels/references stay with
their own sample; each video's frames and attention mask move together), record:
  - eval-mode teacher-forced loss (HF-style batch mean and per-sample),
  - real greedy generate metrics vs. each sample's own reference,
  - prediction identity / chrF against the original-input predictions,
  - encoder-output checks (did the model actually see a different video?).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safetensors.torch import load_file  # noqa: E402
from transformers import T5TokenizerFast  # noqa: E402

from src.dataset import ASLLandmarkDataset, CollateLandmarks  # noqa: E402
from src.models.translation_model import ASLTranslationModel  # noqa: E402
from src.utils.metadata import load_metadata  # noqa: E402

GEN_KWARGS = {"max_length": 30, "num_beams": 1, "do_sample": False}
BATCH = 8


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


def gen_metrics(refs, hyps) -> dict:
    import jiwer
    import sacrebleu

    safe = [h if h.strip() else " " for h in hyps]
    c = Counter(h.strip() for h in hyps)
    top, n = c.most_common(1)[0]
    return {"bleu": sacrebleu.corpus_bleu(safe, [refs]).score,
            "chrf": sacrebleu.corpus_chrf(safe, [refs]).score,
            "wer": jiwer.wer(refs, safe), "unique": len(c), "top1": top,
            "top1_fraction": n / len(hyps)}


def derangement(n: int, seed: int) -> list[int]:
    rng = random.Random(seed)
    while True:
        p = list(range(n))
        rng.shuffle(p)
        if all(p[i] != i for i in range(n)):
            return p


def sign_test_p(k: int, n: int) -> float:
    """Two-sided exact binomial test, H0 p=0.5."""
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def bootstrap_ci(x: np.ndarray, seed: int = 0, n: int = 10000) -> list[float]:
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n, len(x)), replace=True).mean(1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def state_hash(model) -> str:
    h = hashlib.sha256()
    for k, v in sorted(model.state_dict().items()):
        h.update(k.encode())
        h.update(v.detach().cpu().numpy().tobytes())
    return h.hexdigest()


def run_condition(model, items, perm, collate_fn, tok) -> dict:
    """Sample i gets video perm[i] and keeps its own text. perm=None -> original."""
    n = len(items)
    perm = perm or list(range(n))
    enc_pooled = [None] * n
    captured = {}
    hook = model.modality_bridge.register_forward_hook(
        lambda _m, _i, o: captured.__setitem__("enc", o.detach()))
    per_loss, per_tokens, batch_losses, preds, label_rows, n_frames = [], [], [], [], [], []
    with torch.no_grad():
        for s in range(0, n, BATCH):
            idx = list(range(s, min(s + BATCH, n)))
            batch_items = [{"features": items[perm[i]]["features"], "text": items[i]["text"],
                            "file_id": items[i]["file_id"]} for i in idx]
            b = collate_fn(batch_items)
            o = model(input_features=b["input_features"], attention_mask=b["attention_mask"],
                      labels=b["labels"], decoder_attention_mask=b["decoder_attention_mask"])
            batch_losses.append((float(o.loss), len(idx)))
            ce = F.cross_entropy(o.logits.transpose(1, 2), b["labels"], ignore_index=-100,
                                 reduction="none")
            enc = captured["enc"]
            dmask = F.max_pool1d(b["attention_mask"].unsqueeze(1), 3, 2, 1).squeeze(1)[:, : enc.size(1)] >= 0.5
            for k, i in enumerate(idx):
                v = b["labels"][k] != -100
                per_loss.append(float(ce[k][v].mean()))
                per_tokens.append(int(v.sum()))
                label_rows.append(b["labels"][k][v].tolist())
                enc_pooled[i] = enc[k][dmask[k]].mean(0)
                n_frames.append(int(b["attention_mask"][k].sum()))
            g = model.generate(input_features=b["input_features"],
                               attention_mask=b["attention_mask"], **GEN_KWARGS)
            preds += [p.strip() for p in tok.batch_decode(g, skip_special_tokens=True)]
    hook.remove()
    return {"perm": perm, "per_loss": np.array(per_loss), "per_tokens": np.array(per_tokens),
            # HF Trainer.evaluate repeats every batch loss by the first batch size
            # (trainer.py:4677-4696), i.e. an unweighted mean over batch losses
            "hf_loss": float(np.mean([l for l, _ in batch_losses])),
            "sample_weighted_loss": sum(l * k for l, k in batch_losses) / sum(k for _, k in batch_losses),
            "token_loss": float((np.array(per_loss) * np.array(per_tokens)).sum() / sum(per_tokens)),
            "preds": preds, "labels": label_rows, "enc_pooled": torch.stack(enc_pooled),
            "n_frames": n_frames}


def analyse_set(name, model, ds, collate_fn, tok, seeds, out: Path, saved_preds=None,
                saved_loss=None) -> dict:
    import sacrebleu

    items = [ds[i] for i in range(len(ds))]
    ids = [it["file_id"].replace("_holistic", "") for it in items]
    refs = [it["text"] for it in items]
    base = run_condition(model, items, None, collate_fn, tok)
    base_gen = gen_metrics(refs, base["preds"])
    res = {"n": len(items), "original": {"hf_style_loss": base["hf_loss"],
                                          "sample_weighted_loss": base["sample_weighted_loss"],
                                          "token_weighted_loss": base["token_loss"], **base_gen}}
    if saved_preds is not None:
        res["reproduction"] = {
            "predictions_identical_to_saved": base["preds"] == [r["prediction"] for r in saved_preds],
            "ids_identical_to_saved": ids == [r["sample_id"] for r in saved_preds],
            "saved_loss": saved_loss}
    write_json(out / name / "original_predictions.json",
               [{"sample_id": i, "reference": r, "prediction": p, "tf_loss": float(lv)}
                for i, r, p, lv in zip(ids, refs, base["preds"], base["per_loss"])])

    runs = []
    for seed in seeds:
        perm = derangement(len(items), seed)
        c = run_condition(model, items, perm, collate_fn, tok)
        assert c["labels"] == base["labels"], "labels changed under video permutation"
        d = c["per_loss"] - base["per_loss"]  # >0: wrong video is worse for this sample
        # encoder checks: sample i now sees video perm[i]
        cos_own = F.cosine_similarity(c["enc_pooled"], base["enc_pooled"], dim=1)
        cos_moved = F.cosine_similarity(c["enc_pooled"], base["enc_pooled"][perm], dim=1)
        # the pooled bridge output has a large shared component; centre on the dataset mean
        mu = base["enc_pooled"].mean(0, keepdim=True)
        ccos_own = F.cosine_similarity(c["enc_pooled"] - mu, base["enc_pooled"] - mu, dim=1)
        ccos_moved = F.cosine_similarity(c["enc_pooled"] - mu, base["enc_pooled"][perm] - mu, dim=1)
        shared_frac = float((mu.norm() ** 2) / (base["enc_pooled"].norm(dim=1) ** 2).mean())
        moved_frames_ok = all(c["n_frames"][i] == base["n_frames"][perm[i]] for i in range(len(items)))
        same_pred = sum(a == b for a, b in zip(c["preds"], base["preds"]))
        follows_video = sum(c["preds"][i] == base["preds"][perm[i]] for i in range(len(items)))
        g = gen_metrics(refs, c["preds"])
        run = {
            "seed": seed,
            "hf_style_loss": c["hf_loss"], "token_weighted_loss": c["token_loss"],
            "delta_hf_loss": c["hf_loss"] - base["hf_loss"],
            "per_sample_delta_mean": float(d.mean()), "per_sample_delta_ci95": bootstrap_ci(d, seed),
            "n_correct_video_lower_loss": int((d > 0).sum()), "n_wrong_video_lower_loss": int((d < 0).sum()),
            "sign_test_p": sign_test_p(int((d > 0).sum()), int((d != 0).sum())),
            **{k: g[k] for k in ("bleu", "chrf", "wer", "unique", "top1", "top1_fraction")},
            "delta_bleu": g["bleu"] - base_gen["bleu"], "delta_chrf": g["chrf"] - base_gen["chrf"],
            "delta_wer": g["wer"] - base_gen["wer"],
            "same_prediction_as_original_same_id": same_pred,
            "prediction_equals_original_of_moved_video": follows_video,
            "chrf_shuffled_preds_vs_original_preds_same_id": sacrebleu.corpus_chrf(
                [p or " " for p in c["preds"]], [[p or " " for p in base["preds"]]]).score,
            "encoder_cos_vs_original_same_id_mean": float(cos_own.mean()),
            "encoder_cos_vs_original_of_moved_video_mean": float(cos_moved.mean()),
            "encoder_cos_vs_original_of_moved_video_min": float(cos_moved.min()),
            "encoder_centered_cos_vs_original_same_id_mean": float(ccos_own.mean()),
            "encoder_centered_cos_vs_original_of_moved_video_mean": float(ccos_moved.mean()),
            "encoder_pooled_shared_component_energy_fraction": shared_frac,
            "frames_and_mask_moved_with_video": moved_frames_ok,
        }
        runs.append(run)
        write_json(out / name / f"perm_seed{seed}.json", {
            "seed": seed,
            "mapping": [{"sample_id": ids[i], "video_from": ids[perm[i]]} for i in range(len(items))],
            "rows": [{"sample_id": ids[i], "video_from": ids[perm[i]], "reference": refs[i],
                      "prediction_original_input": base["preds"][i],
                      "prediction_mismatched_input": c["preds"][i],
                      "tf_loss_original": float(base["per_loss"][i]),
                      "tf_loss_mismatched": float(c["per_loss"][i])} for i in range(len(items))]})
        print(f"[{name} seed={seed}] dLoss={run['delta_hf_loss']:+.4f} "
              f"per-sample {run['per_sample_delta_mean']:+.4f} CI{[round(x, 4) for x in run['per_sample_delta_ci95']]} "
              f"correct-better {run['n_correct_video_lower_loss']}/{len(items)} p={run['sign_test_p']:.2g} | "
              f"BLEU {g['bleu']:.2f} ({run['delta_bleu']:+.2f}) chrF {g['chrf']:.2f} ({run['delta_chrf']:+.2f}) "
              f"WER {g['wer']:.3f} | same-pred {same_pred} follows-video {follows_video} "
              f"enc cos same-id {run['encoder_cos_vs_original_same_id_mean']:.4f} "
              f"(centred {run['encoder_centered_cos_vs_original_same_id_mean']:.3f}) "
              f"moved {run['encoder_cos_vs_original_of_moved_video_mean']:.4f} "
              f"(centred {run['encoder_centered_cos_vs_original_of_moved_video_mean']:.3f})", flush=True)

    def dist(key):
        v = np.array([r[key] for r in runs], dtype=float)
        return {"min": float(v.min()), "median": float(np.median(v)), "max": float(v.max()),
                "mean": float(v.mean())}

    res["shuffled_distribution"] = {k: dist(k) for k in (
        "delta_hf_loss", "per_sample_delta_mean", "n_correct_video_lower_loss", "bleu", "chrf",
        "wer", "delta_bleu", "delta_chrf", "delta_wer", "unique", "top1_fraction",
        "same_prediction_as_original_same_id", "prediction_equals_original_of_moved_video",
        "chrf_shuffled_preds_vs_original_preds_same_id",
        "encoder_cos_vs_original_same_id_mean", "encoder_cos_vs_original_of_moved_video_mean",
        "encoder_centered_cos_vs_original_same_id_mean",
        "encoder_centered_cos_vs_original_of_moved_video_mean")}
    res["n_shuffles_with_loss_at_or_below_original"] = sum(r["delta_hf_loss"] <= 0 for r in runs)
    res["n_shuffles_with_chrf_at_or_above_original"] = sum(r["chrf"] >= base_gen["chrf"] for r in runs)
    res["n_shuffles_with_bleu_at_or_above_original"] = sum(r["bleu"] >= base_gen["bleu"] for r in runs)
    res["all_labels_unchanged"] = True  # asserted per run
    res["all_frames_and_masks_moved_with_video"] = all(r["frames_and_mask_moved_with_video"] for r in runs)
    res["runs"] = runs
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--p02-dir", required=True, help="results/p02_10pct_e30 (ids, saved preds)")
    ap.add_argument("--epoch", type=int, default=18)
    ap.add_argument("--stage-dir", required=True)
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--frozen-landmarks", required=True)
    ap.add_argument("--frozen-metadata", required=True)
    ap.add_argument("--train-sample-n", type=int, default=366)
    ap.add_argument("--train-sample-seed", type=int, default=20260925)
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 11)))
    ap.add_argument("--sets", nargs="+", default=["val366", "frozen147", "train_sample"])
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    out = Path(args.output_dir)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"STOP: {out} exists and is not empty")
    out.mkdir(parents=True)
    p02 = Path(args.p02_dir)
    ckpt_file = Path(args.checkpoint) / "model.safetensors"
    file_sha_before = hashlib.sha256(ckpt_file.read_bytes()).hexdigest()

    tok = T5TokenizerFast.from_pretrained("t5-small")
    collate_fn = CollateLandmarks(tokenizer=tok, max_target_len=30)
    model = ASLTranslationModel(input_dim=501, input_i3d_dim=None, d_model=512,
                                t5_model_name="t5-small", num_layers=4, num_heads=4, kernel_size=31)
    model.generation_config.max_length = 30
    model.load_state_dict(load_file(str(ckpt_file), device="cpu"), strict=True)
    model.eval()
    hash_before = state_hash(model)

    meta, _ = load_metadata(args.metadata)
    fmeta, _ = load_metadata(args.frozen_metadata)
    read_ids = lambda f: [x for x in (p02 / "ids" / f).read_text().split("\n") if x]  # noqa: E731
    train_ids, val_ids, frozen_ids = read_ids("train_ids.txt"), read_ids("val_ids.txt"), read_ids("frozen_ids.txt")
    # train sample: fixed before any scoring; sorted pool, seeded sample
    train_sample = random.Random(args.train_sample_seed).sample(sorted(train_ids), args.train_sample_n)
    (out / "train_sample_ids.txt").write_text("\n".join(train_sample) + "\n")

    def mk(ids, root, md):
        return ASLLandmarkDataset(data_dir=root, metadata_dict=md, max_len=150, include_face=True,
                                  file_list=[str(Path(root) / f"{i}_holistic.npy") for i in ids],
                                  training=False)

    sets = {"val366": (mk(val_ids, args.stage_dir, meta),
                       json.load(open(p02 / "val_predictions" / f"epoch_{args.epoch:02d}.json"))),
            "frozen147": (mk(frozen_ids, args.frozen_landmarks, fmeta),
                          json.load(open(p02 / "frozen_predictions" / f"epoch_{args.epoch:02d}.json"))),
            "train_sample": (mk(train_sample, args.stage_dir, meta), None)}
    rec = next(json.loads(line) for line in open(p02 / "epoch_log.jsonl")
               if json.loads(line)["epoch"] == args.epoch)
    saved_loss = {"val366": {"trainer_eval_loss": rec["val_loss"], "saved_val_metrics": rec["val"]["full_ref"]},
                  "frozen147": {"token_weighted_loss": rec["frozen_loss"], "saved_metrics": rec["frozen"]["full_ref"]}}

    summary = {"checkpoint": str(ckpt_file), "epoch": args.epoch, "seeds": args.seeds,
               "generate_kwargs": GEN_KWARGS, "batch_size": BATCH,
               "train_sample": {"n": args.train_sample_n, "seed": args.train_sample_seed,
                                "rule": "random.Random(seed).sample(sorted(train_ids), n); chosen before any scoring"},
               "sets": {}}
    for name in args.sets:
        ds, saved = sets[name]
        summary["sets"][name] = analyse_set(name, model, ds, collate_fn, tok, args.seeds, out,
                                            saved_preds=saved, saved_loss=saved_loss.get(name))
        write_json(out / "summary.json", summary)

    summary["weights_unchanged_in_memory"] = state_hash(model) == hash_before
    summary["checkpoint_file_sha256_unchanged"] = (
        hashlib.sha256(ckpt_file.read_bytes()).hexdigest() == file_sha_before)
    summary["checkpoint_file_sha256"] = file_sha_before
    write_json(out / "summary.json", summary)
    print("[weights]", summary["weights_unchanged_in_memory"], summary["checkpoint_file_sha256_unchanged"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
