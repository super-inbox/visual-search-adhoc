"""
Evaluate one checkpoint (no training) on the fixed 366 val and 147 frozen sets with greedy
decoding (max_length=30), at a chosen batch size. Writes metrics + per-sample predictions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safetensors.torch import load_file  # noqa: E402
from transformers import T5TokenizerFast  # noqa: E402

from src.dataset import ASLLandmarkDataset, CollateLandmarks  # noqa: E402
from src.models.translation_model import ASLTranslationModel  # noqa: E402
from src.utils.metadata import load_metadata  # noqa: E402

GEN = {"max_length": 30, "num_beams": 1, "do_sample": False}


def metrics(refs, hyps) -> dict:
    import jiwer
    import sacrebleu

    safe = [h if h.strip() else " " for h in hyps]
    c = Counter(h.strip() for h in hyps)
    top, n = c.most_common(1)[0]
    return {"bleu": sacrebleu.corpus_bleu(safe, [refs]).score,
            "chrf": sacrebleu.corpus_chrf(safe, [refs]).score, "wer": jiwer.wer(refs, safe),
            "unique": len(c), "top1": top, "top1_count": n, "top1_fraction": n / len(hyps)}


def run(model, ds, col, tok, bs) -> tuple[list[dict], dict]:
    rows, batch_losses = [], []
    tot_nll = tot_tok = 0.0
    with torch.no_grad():
        for s in range(0, len(ds), bs):
            its = [ds[i] for i in range(s, min(s + bs, len(ds)))]
            b = col(its)
            o = model(input_features=b["input_features"], attention_mask=b["attention_mask"],
                      labels=b["labels"], decoder_attention_mask=b["decoder_attention_mask"])
            k = int((b["labels"] != -100).sum())
            batch_losses.append((float(o.loss), len(its)))
            tot_nll += float(o.loss) * k
            tot_tok += k
            g = model.generate(input_features=b["input_features"], attention_mask=b["attention_mask"], **GEN)
            for it, p in zip(its, tok.batch_decode(g, skip_special_tokens=True)):
                rows.append({"sample_id": it["file_id"].replace("_holistic", ""),
                             "reference": it["text"], "prediction": p.strip()})
    m = metrics([r["reference"] for r in rows], [r["prediction"] for r in rows])
    m.update({"loss_hf_style_batch_mean": float(np.mean([x for x, _ in batch_losses])),
              "loss_sample_weighted": sum(x * n for x, n in batch_losses) / sum(n for _, n in batch_losses),
              "loss_token_weighted": tot_nll / tot_tok, "n": len(rows)})
    return rows, m


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--p02-dir", required=True)
    ap.add_argument("--stage-dir", required=True)
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--frozen-landmarks", required=True)
    ap.add_argument("--frozen-metadata", required=True)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"STOP: {out} exists and is not empty")
    out.mkdir(parents=True)

    repo = Path(__file__).resolve().parents[1]
    enc_src = (repo / "src/models/manual_encoder.py").read_bytes()
    ck = Path(args.checkpoint) / "model.safetensors"
    sha = hashlib.sha256(ck.read_bytes()).hexdigest()
    tok = T5TokenizerFast.from_pretrained("t5-small")
    col = CollateLandmarks(tokenizer=tok, max_target_len=30)
    model = ASLTranslationModel(input_dim=501)
    model.generation_config.max_length = 30
    model.load_state_dict(load_file(str(ck), device="cpu"), strict=True)
    model.eval()

    meta, _ = load_metadata(args.metadata)
    fmeta, _ = load_metadata(args.frozen_metadata)
    ids = lambda f: [x for x in (Path(args.p02_dir) / "ids" / f).read_text().split("\n") if x]  # noqa: E731
    sets = {
        "val366": ASLLandmarkDataset(data_dir=args.stage_dir, metadata_dict=meta, max_len=150,
                                     file_list=[str(Path(args.stage_dir) / f"{i}_holistic.npy") for i in ids("val_ids.txt")]),
        "frozen147": ASLLandmarkDataset(data_dir=args.frozen_landmarks, metadata_dict=fmeta, max_len=150,
                                        file_list=[str(Path(args.frozen_landmarks) / f"{i}_holistic.npy") for i in ids("frozen_ids.txt")]),
    }
    summary = {"checkpoint": str(ck), "checkpoint_sha256": sha, "batch_size": args.batch_size,
               "generate_kwargs": GEN,
               "manual_encoder_sha256": hashlib.sha256(enc_src).hexdigest(),
               "git_diff_src": subprocess.run(["git", "diff", "--stat", "--", "src"], cwd=repo,
                                              capture_output=True, text=True).stdout.strip(),
               "sets": {}}
    for name, ds in sets.items():
        rows, m = run(model, ds, col, tok, args.batch_size)
        (out / f"{name}_predictions.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
        summary["sets"][name] = m
        print(f"[{name} bs={args.batch_size}] loss(hf)={m['loss_hf_style_batch_mean']:.4f} "
              f"loss(tok)={m['loss_token_weighted']:.4f} BLEU={m['bleu']:.3f} chrF={m['chrf']:.3f} "
              f"WER={m['wer']:.4f} unique={m['unique']} top1={m['top1_count']}", flush=True)
    summary["checkpoint_sha256_unchanged"] = hashlib.sha256(ck.read_bytes()).hexdigest() == sha
    (out / "metrics.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
