"""P0-11 copy of P0-13 scripts/diagnose_p013.py (logic unchanged; only the baseline arm is used here).
P0-13 diagnostics, identical for both arms (no training).

For one trained checkpoint and each eval set (val366, frozen147):
  - original pairing: eval-mode teacher-forced loss (token-weighted), greedy generation (P0.2 GEN_KWARGS),
    BLEU / chrF / WER (P0.2 score()), diversity (unique, top-1 share, distinct-1/2)
  - shuffled pairing: K fixed-seed derangements of the inputs (text stays with its sample), same metrics;
    definition follows gloss-free-asl-translation/scripts/diagnose_input_dependence.py
  - collapse statistics on mean-pooled representations at two points:
      input  = mean over valid frames of the per-frame input features (landmarks or Uni-Sign)
      enc    = mean over valid positions of the modality-bridge output (what the T5 decoder attends to)
Run inside gloss-free-asl-translation (cwd + PYTHONPATH) with its .venv.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from safetensors.torch import load_file
from transformers import T5TokenizerFast

sys.path.insert(0, str(Path.cwd()))
from src.dataset import ASLLandmarkDataset, CollateLandmarks  # noqa: E402
from src.models.translation_model import ASLTranslationModel  # noqa: E402
from src.utils.metadata import load_metadata  # noqa: E402

GEN_KWARGS = {"max_length": 30, "num_beams": 1, "do_sample": False}
BATCH = 8


def clean_id(p):
    return Path(p).name.replace("_holistic.npy", "").replace("_landmarks.npy", "")


class FeatDS(torch.utils.data.Dataset):
    def __init__(self, ids, texts, feat_dir, key="enc", max_len=150):
        self.ids, self.texts, self.dir, self.key, self.max_len = ids, texts, Path(feat_dir), key, max_len

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, i):
        f = np.load(self.dir / f"{self.ids[i]}.npz")[self.key].astype(np.float32)
        if len(f) > self.max_len:
            f = f[:: int(np.ceil(len(f) / self.max_len))][: self.max_len]
        return {"features": torch.tensor(f), "text": self.texts[self.ids[i]], "file_id": self.ids[i]}


def score(refs, hyps):
    import jiwer
    import sacrebleu
    safe = [h if h.strip() else " " for h in hyps]
    safe_r = [r if r.strip() else " " for r in refs]
    c = Counter(h.strip() for h in hyps)
    top, top_n = c.most_common(1)[0]
    toks = [h.split() for h in hyps]
    d1 = len({t for x in toks for t in x}) / max(1, sum(len(x) for x in toks))
    bi = [tuple(x[i:i + 2]) for x in toks for i in range(len(x) - 1)]
    d2 = len(set(bi)) / max(1, len(bi))
    return {"bleu": sacrebleu.corpus_bleu(safe, [safe_r]).score, "chrf": sacrebleu.corpus_chrf(safe, [safe_r]).score,
            "wer": jiwer.wer(safe_r, safe), "n": len(hyps), "unique_predictions": len(c),
            "top1_prediction": top, "top1_fraction": top_n / len(hyps), "distinct1": d1, "distinct2": d2}


def collapse_stats(X: np.ndarray) -> dict:
    X = X.astype(np.float64)
    Xn = X / np.linalg.norm(X, axis=1, keepdims=True)
    S = Xn @ Xn.T
    n = len(X)
    off = S[~np.eye(n, dtype=bool)]
    mu = X.mean(0)
    C = X - mu
    shared = float(np.sum(mu ** 2) / np.mean(np.sum(X ** 2, 1)))
    ev = np.linalg.svd(C, compute_uv=False) ** 2
    Cn = C / np.linalg.norm(C, axis=1, keepdims=True)
    # nearest-neighbour distinctness: how often a clip's closest other clip (centred cosine) is from the same source video
    return {"mean_pairwise_cos": float(off.mean()), "min_pairwise_cos": float(off.min()),
            "p05_pairwise_cos": float(np.percentile(off, 5)),
            "shared_component_energy": shared, "pc1_var_ratio_centred": float(ev[0] / ev.sum()),
            "participation_ratio_centred": float(ev.sum() ** 2 / np.sum(ev ** 2)),
            "mean_abs_centred_cos": float(np.abs((Cn @ Cn.T)[~np.eye(n, dtype=bool)]).mean())}


def derangement(n, seed):
    rng = random.Random(seed)
    while True:
        p = list(range(n))
        rng.shuffle(p)
        if all(p[i] != i for i in range(n)):
            return p


def run(model, items, perm, collate, tok):
    n = len(items)
    perm = perm or list(range(n))
    nll, ntok, preds, enc_pool, in_pool = 0.0, 0, [], [], []
    model.eval()
    with torch.no_grad():
        for s in range(0, n, BATCH):
            idx = list(range(s, min(n, s + BATCH)))
            b = collate([{"features": items[perm[i]]["features"], "text": items[i]["text"],
                          "file_id": items[i]["file_id"]} for i in idx])
            o = model(input_features=b["input_features"], attention_mask=b["attention_mask"],
                      labels=b["labels"], decoder_attention_mask=b["decoder_attention_mask"])
            k = int((b["labels"] != -100).sum())
            nll += float(o.loss) * k
            ntok += k
            g = model.generate(input_features=b["input_features"], attention_mask=b["attention_mask"], **GEN_KWARGS)
            preds += [p.strip() for p in tok.batch_decode(g, skip_special_tokens=True)]
            if perm == list(range(n)):
                h, kpm = model.encoder(b["input_features"], attention_mask=b["attention_mask"])
                h = model.modality_bridge(h)
                v = (~kpm).float().unsqueeze(-1)
                enc_pool.append((h * v).sum(1) / v.sum(1))
                m = b["attention_mask"].unsqueeze(-1)
                in_pool.append((b["input_features"] * m).sum(1) / m.sum(1))
    out = {"loss": nll / ntok, "preds": preds}
    if enc_pool:
        out["enc_pool"] = torch.cat(enc_pool).numpy()
        out["in_pool"] = torch.cat(in_pool).numpy()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["baseline", "treatment"], required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--ids-dir", required=True)
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--frozen-metadata", required=True)
    ap.add_argument("--stage-dir")
    ap.add_argument("--frozen-landmarks")
    ap.add_argument("--feat-root")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    torch.manual_seed(0)
    tok = T5TokenizerFast.from_pretrained("t5-small")
    meta, _ = load_metadata(a.metadata)
    fmeta, _ = load_metadata(a.frozen_metadata)
    model = ASLTranslationModel(input_dim=501 if a.arm == "baseline" else 768, input_i3d_dim=None, d_model=512,
                                t5_model_name="t5-small", num_layers=4, num_heads=4, kernel_size=31)
    model.generation_config.max_length = 30
    model.load_state_dict(load_file(str(Path(a.checkpoint) / "model.safetensors"), device="cpu"))
    collate = CollateLandmarks(tokenizer=tok, max_target_len=30)
    res = {"arm": a.arm, "checkpoint": a.checkpoint, "seeds": list(range(1, a.seeds + 1)), "sets": {}}
    for name, idfile, texts in (("val366", "val_ids.txt", meta), ("frozen147", "frozen_ids.txt", fmeta)):
        ids = [x.strip() for x in open(Path(a.ids_dir) / idfile) if x.strip()]
        if a.arm == "baseline":
            if name == "val366":
                files = [str(Path(a.stage_dir) / f"{i}_holistic.npy") for i in ids]
                ds = ASLLandmarkDataset(data_dir=a.stage_dir, metadata_dict=meta, file_list=files, max_len=150,
                                        include_face=True, training=False)
            else:
                files = [str(Path(a.frozen_landmarks) / f"{i}_holistic.npy") for i in ids]
                ds = ASLLandmarkDataset(data_dir=a.frozen_landmarks, metadata_dict=fmeta, file_list=files,
                                        max_len=150, include_face=True, training=False)
            assert [clean_id(p) for p in ds.filepaths] == ids, "order/id mismatch"
        else:
            ds = FeatDS(ids, texts, Path(a.feat_root) / ("val" if name == "val366" else "frozen"))
        items = [ds[i] for i in range(len(ds))]
        refs = [it["text"] for it in items]
        base = run(model, items, None, collate, tok)
        s = {"n": len(items), "original": {"loss": base["loss"], **score(refs, base["preds"])},
             "collapse_input": collapse_stats(base["in_pool"]), "collapse_encoder": collapse_stats(base["enc_pool"]),
             "shuffled": []}
        for seed in res["seeds"]:
            perm = derangement(len(items), seed)
            sh = run(model, items, perm, collate, tok)
            follows = sum(sh["preds"][i] == base["preds"][perm[i]] for i in range(len(items)))
            s["shuffled"].append({"seed": seed, "loss": sh["loss"], "delta_loss": sh["loss"] - base["loss"],
                                  "preds_follow_video": follows, "preds_unchanged": sum(
                                      sh["preds"][i] == base["preds"][i] for i in range(len(items))),
                                  **{k: v for k, v in score(refs, sh["preds"]).items() if k in ("bleu", "chrf", "wer")}})
            print(name, "seed", seed, json.dumps(s["shuffled"][-1]), flush=True)
        dl = [x["delta_loss"] for x in s["shuffled"]]
        s["shuffled_summary"] = {"delta_loss_mean": float(np.mean(dl)), "delta_loss_min": float(np.min(dl)),
                                 "delta_bleu_mean": float(np.mean([x["bleu"] for x in s["shuffled"]]) - s["original"]["bleu"]),
                                 "delta_chrf_mean": float(np.mean([x["chrf"] for x in s["shuffled"]]) - s["original"]["chrf"])}
        s["predictions"] = [{"id": it["file_id"], "reference": r, "prediction": p}
                            for it, r, p in zip(items, refs, base["preds"])]
        res["sets"][name] = s
        print(name, json.dumps({k: s[k] for k in ("original", "collapse_input", "collapse_encoder", "shuffled_summary")}),
              flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
