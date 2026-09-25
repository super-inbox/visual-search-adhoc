"""
Batch-context diagnostics: does the same video give different encoder outputs / greedy
predictions depending on which other videos share its batch (i.e. how much padding it gets)?

For each selected video and each context (alone, similar-length batch, much-longer batch,
different positions) it records every intermediate stage at the video's valid positions and
the per-step decoder logits, and reports the first stage whose values differ from the
single-video run. No training; weights are only read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safetensors.torch import load_file  # noqa: E402
from transformers import T5TokenizerFast  # noqa: E402
from transformers.modeling_outputs import BaseModelOutput  # noqa: E402

from src.dataset import ASLLandmarkDataset, CollateLandmarks  # noqa: E402
from src.models.translation_model import ASLTranslationModel  # noqa: E402
from src.utils.metadata import load_metadata  # noqa: E402

GEN = {"max_length": 30, "num_beams": 1, "do_sample": False}


def trace(model, batch, row: int) -> dict:
    """Run the encoder stage by stage (same ops as ConformerEncoder.forward / model.generate)
    and return the tensors for one batch row, plus greedy decoding with per-step logits."""
    enc = model.encoder
    x_in, am = batch["input_features"], batch["attention_mask"]
    st = {}
    with torch.no_grad():
        x = enc.projection(x_in)
        # mirrors the fixed ConformerEncoder.forward (padded frames zeroed after projection)
        x = x.masked_fill(am.unsqueeze(-1) < 0.5, 0.0)
        st["projection"] = x
        x = enc.downsample(x.transpose(1, 2)).transpose(1, 2)
        st["downsample"] = x
        x = enc.pos_encoding(x)
        st["pos_encoding"] = x
        kpm = (am[:, ::2] < 0.5)[:, : x.size(1)]
        for i, blk in enumerate(enc.blocks):
            x = blk(x, key_padding_mask=kpm)
            st[f"block{i}"] = x
        st["conformer_out"] = x
        # identical to model.forward/generate from here
        ref_out, ref_mask = enc(x_in, attention_mask=am)
        assert torch.equal(ref_out, x) and torch.equal(ref_mask, kpm)
        bridge = model.modality_bridge(model._fuse_modalities(x, None, kpm))
        st["bridge_out"] = bridge
        valid = (~kpm).long()
        t5_mask = torch.cat([torch.ones_like(valid[:, :1]), valid[:, 1:]], dim=1)
        g = model.t5.generate(encoder_outputs=BaseModelOutput(last_hidden_state=bridge[row:row + 1]),
                              attention_mask=t5_mask[row:row + 1],
                              bos_token_id=model.t5.config.decoder_start_token_id,
                              output_scores=True, return_dict_in_generate=True, **GEN)
        # also run the model's own generate on the full batch to confirm the same tokens
        full = model.generate(input_features=x_in, attention_mask=am, **GEN)
    n_in = int(am[row].sum())
    n_enc = int(valid[row].sum())
    out = {
        "n_frames_valid": n_in, "padded_len": int(am.size(1)),
        "input_valid": x_in[row, :n_in].clone(),
        "input_pad_all_zero": bool((x_in[row, n_in:] == 0).all()),
        "mask_row": am[row].clone(),
        "enc_valid_positions": n_enc, "enc_len": int(kpm.size(1)),
        "t5_mask_row": t5_mask[row].clone(),
        "stages": {k: v[row, :n_enc].clone() for k, v in st.items() if k != "projection"},
        "projection_valid": st["projection"][row, :n_in].clone(),
        "tokens": g.sequences[0].tolist(),
        "step_logits": torch.stack([s[0] for s in g.scores]),
        "tokens_full_batch_generate": [t for t in full[row].tolist()],
    }
    return out


def compare(a: dict, b: dict) -> dict:
    """b vs reference a (the single-video run)."""
    res = {"n_frames_valid": [a["n_frames_valid"], b["n_frames_valid"]],
           "padded_len": [a["padded_len"], b["padded_len"]],
           "enc_valid_positions": [a["enc_valid_positions"], b["enc_valid_positions"]],
           "input_valid_identical": bool(torch.equal(a["input_valid"], b["input_valid"])),
           "input_pad_all_zero": b["input_pad_all_zero"],
           "projection_max_abs_diff": float((a["projection_valid"] - b["projection_valid"]).abs().max())}
    n = min(a["enc_valid_positions"], b["enc_valid_positions"])
    first = None
    for k in a["stages"]:
        d = (a["stages"][k][:n] - b["stages"][k][:n]).abs()
        per_pos = d.max(1).values
        res[f"{k}_max_abs_diff"] = float(d.max())
        res[f"{k}_diff_positions_gt_1e-4"] = [int(i) for i in torch.nonzero(per_pos > 1e-4).flatten()]
        if first is None and float(d.max()) > 1e-5:
            first = k
    res["first_stage_diff_gt_1e-5"] = first
    # decoder: compare step by step while tokens agree
    ta, tb = a["tokens"], b["tokens"]
    res["tokens_identical"] = ta == tb
    res["full_batch_generate_matches_trace"] = (
        [t for t in b["tokens_full_batch_generate"] if t != 0] == [t for t in tb if t != 0])
    steps = []
    for s in range(min(len(a["step_logits"]), len(b["step_logits"]))):
        la, lb = a["step_logits"][s], b["step_logits"][s]
        top2 = torch.topk(la, 2).values
        steps.append({"step": s, "logit_max_abs_diff": float((la - lb).abs().max()),
                      "argmax_a": int(la.argmax()), "argmax_b": int(lb.argmax()),
                      "margin_top1_top2_a": float(top2[0] - top2[1])})
        if int(la.argmax()) != int(lb.argmax()):
            break
    res["decoder_steps"] = steps
    res["first_argmax_change_step"] = next((s["step"] for s in steps if s["argmax_a"] != s["argmax_b"]), None)
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--p02-dir", required=True)
    ap.add_argument("--perm-dir", required=True, help="results/p02_input_dependence/val366")
    ap.add_argument("--stage-dir", required=True)
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--n-inconsistent", type=int, default=6)
    ap.add_argument("--n-consistent", type=int, default=4)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"STOP: {out} exists and is not empty")
    out.mkdir(parents=True)
    (out / "tensors").mkdir()

    ck = Path(args.checkpoint) / "model.safetensors"
    sha_before = hashlib.sha256(ck.read_bytes()).hexdigest()
    tok = T5TokenizerFast.from_pretrained("t5-small")
    col = CollateLandmarks(tokenizer=tok, max_target_len=30)
    model = ASLTranslationModel(input_dim=501)
    model.generation_config.max_length = 30
    model.load_state_dict(load_file(str(ck), device="cpu"), strict=True)
    model.eval()

    meta, _ = load_metadata(args.metadata)
    val_ids = [x for x in (Path(args.p02_dir) / "ids" / "val_ids.txt").read_text().split("\n") if x]
    ds = ASLLandmarkDataset(data_dir=args.stage_dir, metadata_dict=meta, max_len=150, include_face=True,
                            file_list=[str(Path(args.stage_dir) / f"{i}_holistic.npy") for i in val_ids],
                            training=False)
    items = {i: ds[k] for k, i in enumerate(val_ids)}
    lengths = {i: int(items[i]["features"].shape[0]) for i in val_ids}
    raw_T = {i: int(np.load(Path(args.stage_dir) / f"{i}_holistic.npy", mmap_mode="r").shape[0]) for i in val_ids}

    # videos whose prediction did / did not follow them across the 10 permutations
    orig = {r["sample_id"]: r["prediction"] for r in json.load(open(Path(args.perm_dir) / "original_predictions.json"))}
    incons, seen = {}, {}
    for f in sorted(Path(args.perm_dir).glob("perm_seed*.json")):
        for r in json.load(open(f))["rows"]:
            v = r["video_from"]
            seen[v] = seen.get(v, 0) + 1
            if r["prediction_mismatched_input"] != orig[v]:
                incons[v] = incons.get(v, 0) + 1
    inconsistent = sorted(incons, key=lambda v: (-incons[v], v))[: args.n_inconsistent]
    consistent = sorted(v for v in seen if v not in incons)[: args.n_consistent]
    chosen = [(v, "inconsistent") for v in inconsistent] + [(v, "consistent") for v in consistent]

    order_by_len = sorted(val_ids, key=lambda i: (lengths[i], i))
    report = {"checkpoint": str(ck), "checkpoint_sha256": sha_before, "generate_kwargs": GEN,
              "selection": {"inconsistent_counts": {v: incons[v] for v in inconsistent},
                            "rule": "inconsistent = videos whose mismatched-input prediction differed from "
                                    "their original prediction in >=1 of 10 perms (most frequent first); "
                                    "consistent = first videos (sorted id) that always matched"},
              "videos": []}
    for v, kind in chosen:
        L = lengths[v]
        similar = [i for i in order_by_len if i != v and abs(lengths[i] - L) <= max(2, 0.05 * L)][:7]
        longer = [i for i in order_by_len if i != v and lengths[i] >= min(150, L + 40)][-7:]
        contexts = {
            "alone": [v],
            "similar_len_pos0": [v] + similar,
            "longer_pos0": [v] + longer,
            "longer_pos3": longer[:3] + [v] + longer[3:],
            "longer_pos7": longer + [v],
        }
        vid = {"video": v, "kind": kind, "raw_landmark_frames": raw_T[v], "frames_after_stride": L,
               "frames_even": L % 2 == 0, "original_prediction": orig[v], "contexts": {}}
        traces = {}
        for name, members in contexts.items():
            batch = col([items[i] for i in members])
            row = members.index(v)
            traces[name] = trace(model, batch, row)
            traces[name]["members"] = members
        ref = traces["alone"]
        vid["alone_text"] = tok.decode(ref["tokens"], skip_special_tokens=True)
        for name, t in traces.items():
            c = compare(ref, t) if name != "alone" else {"reference": True}
            c["text"] = tok.decode(t["tokens"], skip_special_tokens=True)
            c["members_frames"] = [lengths[i] for i in t["members"]]
            vid["contexts"][name] = c
            torch.save({k: t[k] for k in ("input_valid", "mask_row", "t5_mask_row", "stages",
                                          "projection_valid", "tokens", "step_logits")},
                       out / "tensors" / f"{v}__{name}.pt")
        report["videos"].append(vid)
        cs = vid["contexts"]
        print(f"[{kind}] {v} L={L} ({'even' if L % 2 == 0 else 'odd'}) | " + " | ".join(
            f"{n}: pad={cs[n]['padded_len'][1]} encpos={cs[n]['enc_valid_positions'][1]} first={cs[n]['first_stage_diff_gt_1e-5']} "
            f"bridge={cs[n]['bridge_out_max_abs_diff']:.2e} argmax@{cs[n]['first_argmax_change_step']}"
            for n in cs if n != "alone"), flush=True)

    report["checkpoint_sha256_unchanged"] = hashlib.sha256(ck.read_bytes()).hexdigest() == sha_before
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
