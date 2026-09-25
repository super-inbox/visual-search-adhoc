"""
Diagnostics for the P0.1 tiny-set overfit checkpoints (no training).

For each final checkpoint and the fixed 32 clips:
  1. exact token-length accounting of every reference vs. the generate length cap
  2. greedy generate at max_length=30 and at the minimal cap that fits every reference
  3. eval-mode, no-grad teacher-forced loss / token accuracy, compared per sample with
     the free-running greedy output (first wrong token, and what happens after it)
  4. consistency of encoder outputs, masks and special tokens between the training
     forward path and model.generate, plus an uncached step-by-step greedy decode
"""

from __future__ import annotations

import argparse
import functools
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safetensors.torch import load_file  # noqa: E402
from transformers import T5TokenizerFast  # noqa: E402
from transformers.modeling_outputs import BaseModelOutput  # noqa: E402

from src.dataset import ASLLandmarkDataset, CollateLandmarks  # noqa: E402
from src.models.translation_model import ASLTranslationModel  # noqa: E402


def text_metrics(refs, hyps):
    import jiwer
    import sacrebleu

    return {
        "bleu": round(sacrebleu.corpus_bleu(hyps, [refs]).score, 2),
        "exact_match": sum(r.strip() == h.strip() for r, h in zip(refs, hyps)),
        "wer": round(jiwer.wer(refs, [h if h.strip() else " " for h in hyps]), 4),
        "n": len(refs),
    }


def load_model(ckpt: Path) -> ASLTranslationModel:
    model = ASLTranslationModel(input_dim=501, input_i3d_dim=None, d_model=512,
                                t5_model_name="t5-small", num_layers=4, num_heads=4,
                                kernel_size=31)
    missing, unexpected = model.load_state_dict(
        load_file(str(ckpt / "model.safetensors"), device="cpu"), strict=True)
    assert not missing and not unexpected
    model.eval()
    return model


def generated_body(seq: list[int], eos: int, pad: int) -> dict:
    """seq includes the decoder start token at index 0."""
    body = seq[1:]
    if eos in body:
        k = body.index(eos)
        return {"content": body[:k], "emitted_eos": True, "eos_index_in_body": k}
    # generate right-pads finished rows with pad; an unfinished row has no pad
    return {"content": [t for t in body if t != pad], "emitted_eos": False,
            "eos_index_in_body": None}


def classify(ref: list[int], gen: list[int], emitted_eos: bool, hit_cap: bool) -> dict:
    first = next((i for i, (a, b) in enumerate(zip(ref, gen)) if a != b), None)
    if first is None and len(ref) == len(gen):
        return {"first_error_pos": None, "error_types": []}
    if first is None:
        first = min(len(ref), len(gen))
    types = []
    tail = gen[first:]
    if emitted_eos and len(gen) < len(ref):
        types.append("early_eos")
    grams = Counter(tuple(gen[i:i + 3]) for i in range(len(gen) - 2))
    ref_grams = Counter(tuple(ref[i:i + 3]) for i in range(len(ref) - 2))
    if any(c >= 2 and c > ref_grams.get(g, 0) for g, c in grams.items()) or (
            hit_cap and len(ref) < len(gen)):
        types.append("repetition")
    # skip ahead: a 3-token window of the tail matches the reference later than `first`
    ref_later = {tuple(ref[j:j + 3]): j for j in range(first + 1, len(ref) - 2)}
    if any(tuple(tail[i:i + 3]) in ref_later for i in range(len(tail) - 2)):
        types.append("skip_ahead")
    if len(gen) > len(ref) and not hit_cap and "repetition" not in types:
        types.append("too_long")
    if not types:
        types.append("substitution_or_other")
    return {"first_error_pos": first, "error_types": types}


def run_generate(model, batches, max_length):
    out = []
    with torch.no_grad():
        for b in batches:
            g = model.generate(input_features=b["input_features"],
                               attention_mask=b["attention_mask"],
                               max_length=max_length, num_beams=1, do_sample=False)
            out.extend(g.tolist())
    return out


def uncached_greedy(model, b, steps, start, eos):
    """Greedy decode via the training-style T5 forward (full prefix each step, no cache)."""
    with torch.no_grad():
        enc, dmask = model.encoder(b["input_features"], attention_mask=b["attention_mask"])
        enc = model.modality_bridge(model._fuse_modalities(enc, None, dmask))
        valid = (~dmask).long()
        amask = torch.cat([torch.ones_like(valid[:, :1]), valid[:, 1:]], dim=1)
        dec = torch.full((enc.size(0), 1), start, dtype=torch.long)
        done = torch.zeros(enc.size(0), dtype=torch.bool)
        for _ in range(steps):
            logits = model.t5(encoder_outputs=BaseModelOutput(last_hidden_state=enc),
                              attention_mask=amask, decoder_input_ids=dec,
                              use_cache=False).logits[:, -1]
            nxt = logits.argmax(-1)
            nxt = torch.where(done, torch.zeros_like(nxt), nxt)
            dec = torch.cat([dec, nxt[:, None]], dim=1)
            done |= nxt == eos
            if done.all():
                break
    return dec.tolist()


def consistency(model, batch, tok):
    """Capture what reaches T5 in the training forward vs. in generate."""
    cap = {}

    def bridge_hook(name):
        def fn(_m, _i, o):
            cap.setdefault(name, []).append(o.detach().clone())
        return fn

    orig_t5_forward = model.t5.forward

    @functools.wraps(orig_t5_forward)  # generate() validates kwargs against this signature
    def spy(*a, **kw):
        tag = "gen" if cap.get("_mode") == "gen" else "fwd"
        cap.setdefault(f"{tag}_t5_attention_mask", []).append(kw.get("attention_mask"))
        cap.setdefault(f"{tag}_decoder_input_ids", []).append(kw.get("decoder_input_ids"))
        cap.setdefault(f"{tag}_encoder_hidden", []).append(
            kw["encoder_outputs"].last_hidden_state if kw.get("encoder_outputs") is not None else None)
        return orig_t5_forward(*a, **kw)

    model.t5.forward = spy
    try:
        with torch.no_grad():
            cap["_mode"] = "fwd"
            h = model.modality_bridge.register_forward_hook(bridge_hook("fwd_bridge"))
            model(input_features=batch["input_features"], attention_mask=batch["attention_mask"],
                  labels=batch["labels"], decoder_attention_mask=batch["decoder_attention_mask"])
            h.remove()
            cap["_mode"] = "gen"
            h = model.modality_bridge.register_forward_hook(bridge_hook("gen_bridge"))
            model.generate(input_features=batch["input_features"],
                           attention_mask=batch["attention_mask"], max_length=30, num_beams=1,
                           do_sample=False)
            h.remove()
    finally:
        model.t5.forward = orig_t5_forward

    fwd_enc, gen_enc = cap["fwd_bridge"][0], cap["gen_bridge"][0]
    fwd_mask = cap["fwd_t5_attention_mask"][0]
    gen_mask = cap["gen_t5_attention_mask"][0]
    gen_first_dec = cap["gen_decoder_input_ids"][0]
    shifted = model.t5._shift_right(batch["labels"])
    return {
        "input_features_shape": list(batch["input_features"].shape),
        "input_attention_mask_shape": list(batch["attention_mask"].shape),
        "encoder_output_shape_forward": list(fwd_enc.shape),
        "encoder_output_shape_generate": list(gen_enc.shape),
        "encoder_output_max_abs_diff": float((fwd_enc - gen_enc).abs().max()),
        "t5_encoder_attention_mask_shape_forward": list(fwd_mask.shape),
        "t5_encoder_attention_mask_shape_generate": list(gen_mask.shape),
        "t5_encoder_attention_mask_equal": bool(torch.equal(fwd_mask, gen_mask)),
        "generate_calls_t5_forward_with_encoder_hidden_identical": all(
            e is not None and torch.equal(e, gen_enc) for e in cap["gen_encoder_hidden"]),
        "n_generate_decoder_steps": len(cap["gen_decoder_input_ids"]),
        "generate_first_decoder_input_ids": gen_first_dec[:, 0].tolist() if gen_first_dec is not None else None,
        "forward_decoder_input_ids_col0": shifted[:, 0].tolist(),
        # None => T5ForConditionalGeneration.forward builds them as _shift_right(labels)
        "forward_decoder_input_ids_passed_explicitly": cap["fwd_decoder_input_ids"][0] is not None,
        "labels_example_row0": batch["labels"][0].tolist(),
        "shift_right_row0": shifted[0].tolist(),
        "decoder_attention_mask_row0": batch["decoder_attention_mask"][0].tolist(),
        "special_ids": {"tokenizer_pad": tok.pad_token_id, "tokenizer_eos": tok.eos_token_id,
                        "t5_config_pad": model.t5.config.pad_token_id,
                        "t5_config_eos": model.t5.config.eos_token_id,
                        "t5_config_decoder_start": model.t5.config.decoder_start_token_id,
                        "generation_config": model.generation_config.to_diff_dict()},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True, help="name=results/run_dir")
    ap.add_argument("--stage-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    out = Path(args.output_dir)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"STOP: {out} exists and is not empty")
    out.mkdir(parents=True)

    runs = dict(r.split("=", 1) for r in args.run)
    first_run = Path(next(iter(runs.values())))
    targets = json.load(open(first_run / "targets.json"))
    tok = T5TokenizerFast.from_pretrained("t5-small")
    start, eos, pad = 0, tok.eos_token_id, tok.pad_token_id

    # ---- 1. length accounting from token IDs
    CAP = 30
    length_rows = []
    for t in targets:
        ids = tok(t["reference"]).input_ids
        assert ids == t["target_token_ids"], t["sample_id"]
        assert ids[-1] == eos and eos not in ids[:-1]
        n_content = len(ids) - 1
        length_rows.append({
            "sample_id": t["sample_id"], "reference": t["reference"], "token_ids": ids,
            "n_content_tokens": n_content, "eos_index_in_target": len(ids) - 1,
            "decoder_start_token": start,
            "total_len_to_emit_content": 1 + n_content,
            "total_len_to_emit_content_and_eos": 1 + n_content + 1,
            "content_fits_max_length_30": 1 + n_content <= CAP,
            "content_and_eos_fit_max_length_30": 2 + n_content <= CAP,
        })
    need_cap = max(r["total_len_to_emit_content_and_eos"] for r in length_rows)
    length_summary = {
        "max_length_semantics": "HF MaxLengthCriteria stops when cur_len >= max_length; cur_len counts the decoder start token (generation/stopping_criteria.py:78)",
        "max_n_content_tokens": max(r["n_content_tokens"] for r in length_rows),
        "ids_content_cannot_fit_30": [r["sample_id"] for r in length_rows if not r["content_fits_max_length_30"]],
        "ids_eos_cannot_fit_30": [r["sample_id"] for r in length_rows if not r["content_and_eos_fit_max_length_30"]],
        "minimal_max_length_fitting_all_with_eos": need_cap,
    }
    write(out / "length_accounting.json", {"summary": length_summary, "rows": length_rows})
    print("[length]", json.dumps(length_summary), flush=True)

    meta = {t["sample_id"]: t["reference"] for t in targets}
    files = [str(Path(args.stage_dir) / f"{t['sample_id']}_holistic.npy") for t in targets]
    ds = ASLLandmarkDataset(data_dir=args.stage_dir, metadata_dict=meta, file_list=files,
                            max_len=150, include_face=True, training=False)
    col = CollateLandmarks(tokenizer=tok, max_target_len=30)
    batches = [col([ds[j] for j in range(i, min(i + 8, len(ds)))]) for i in range(0, len(ds), 8)]
    order = [r["sample_id"] for r in length_rows]
    ref_ids = {r["sample_id"]: r["token_ids"][:-1] for r in length_rows}

    summary = {"length": length_summary, "runs": {}}
    for name, run_dir in runs.items():
        model = load_model(Path(run_dir) / "final_model")
        res = {}

        # ---- 4. consistency (first batch) + uncached greedy for all batches
        res["consistency"] = consistency(model, batches[0], tok)
        unc = []
        for b in batches:
            unc.extend(uncached_greedy(model, b, steps=CAP - 1, start=start, eos=eos))

        # ---- 2. generate at two caps (inputs never contain labels)
        gens = {cap: run_generate(model, batches, cap) for cap in (CAP, need_cap)}

        # ---- 3. teacher-forced loss / accuracy in eval mode
        tf_rows = []
        with torch.no_grad():
            for b in batches:
                o = model(input_features=b["input_features"], attention_mask=b["attention_mask"],
                          labels=b["labels"], decoder_attention_mask=b["decoder_attention_mask"])
                logits, labels = o.logits, b["labels"]
                ce = F.cross_entropy(logits.transpose(1, 2), labels, ignore_index=-100,
                                     reduction="none")
                pred = logits.argmax(-1)
                for k in range(labels.size(0)):
                    valid = labels[k] != -100
                    lab = labels[k][valid].tolist()
                    pr = pred[k][valid].tolist()
                    wrong = [i for i, (a, c) in enumerate(zip(lab, pr)) if a != c]
                    tf_rows.append({
                        "loss": float(ce[k][valid].mean()), "n_tokens": len(lab),
                        "token_acc": 1 - len(wrong) / len(lab), "wrong_positions": wrong,
                        "argmax_ids": pr,
                        "batch_mean_loss_matches_model": None,
                    })
                # the model's own reduction (mean over all valid tokens in the batch)
                tf_rows[-1]["batch_mean_loss_matches_model"] = float(o.loss)
        all_tok = sum(r["n_tokens"] for r in tf_rows)
        tf_loss = sum(r["loss"] * r["n_tokens"] for r in tf_rows) / all_tok
        tf_acc = sum(r["token_acc"] * r["n_tokens"] for r in tf_rows) / all_tok

        per = []
        preds = {cap: [] for cap in gens}
        for i, sid in enumerate(order):
            ref = ref_ids[sid]
            row = {"sample_id": sid, "reference": meta[sid], "n_content_tokens": len(ref),
                   "tf_loss": round(tf_rows[i]["loss"], 4),
                   "tf_token_acc": round(tf_rows[i]["token_acc"], 4),
                   "tf_first_wrong_pos": (tf_rows[i]["wrong_positions"] or [None])[0],
                   "tf_wrong_positions": tf_rows[i]["wrong_positions"]}
            for cap, seqs in gens.items():
                g = generated_body(seqs[i], eos, pad)
                hit = not g["emitted_eos"] and len(seqs[i]) == cap
                text = tok.decode(g["content"], skip_special_tokens=True).strip()
                preds[cap].append(text)
                c = classify(ref, g["content"], g["emitted_eos"], hit)
                row[f"gen{cap}"] = {
                    "prediction": text, "exact": text == meta[sid].strip(),
                    "token_exact": g["content"] == ref and g["emitted_eos"],
                    "n_generated_content_tokens": len(g["content"]),
                    "emitted_eos": g["emitted_eos"], "hit_cap_without_eos": hit,
                    **c, "generated_ids": g["content"],
                }
            # a greedy token at the first divergence must equal the TF argmax there
            fp = row[f"gen{CAP}"]["first_error_pos"]
            gi = row[f"gen{CAP}"]["generated_ids"]
            if fp is not None and fp < len(gi) and fp < len(tf_rows[i]["argmax_ids"]):
                row["greedy_token_at_first_error_equals_tf_argmax"] = gi[fp] == tf_rows[i]["argmax_ids"][fp]
            elif fp is not None and fp == len(gi):  # greedy stopped/ended here
                row["greedy_token_at_first_error_equals_tf_argmax"] = (
                    (eos if row[f"gen{CAP}"]["emitted_eos"] else None) == tf_rows[i]["argmax_ids"][fp]
                    if fp < len(tf_rows[i]["argmax_ids"]) else None)
            else:
                row["greedy_token_at_first_error_equals_tf_argmax"] = None
            row["greedy_first_error_equals_tf_first_wrong"] = fp == row["tf_first_wrong_pos"]
            unc_body = generated_body(unc[i], eos, pad)
            row["uncached_greedy_equals_generate"] = (
                unc_body["content"] == generated_body(gens[CAP][i], eos, pad)["content"])
            per.append(row)

        refs = [meta[s] for s in order]
        res["metrics"] = {f"max_length_{cap}": text_metrics(refs, preds[cap]) for cap in gens}
        res["teacher_forced_eval"] = {"loss_token_weighted": round(tf_loss, 4),
                                      "token_acc": round(tf_acc, 4),
                                      "samples_tf_all_correct": sum(not r["tf_wrong_positions"] for r in per)}
        res["checks"] = {
            "uncached_greedy_equals_generate_all": all(r["uncached_greedy_equals_generate"] for r in per),
            "greedy_first_error_equals_tf_first_wrong_all": all(r["greedy_first_error_equals_tf_first_wrong"] for r in per),
            "greedy_token_at_first_error_equals_tf_argmax_all": all(
                r["greedy_token_at_first_error_equals_tf_argmax"] in (True, None) for r in per),
        }
        changed = []
        for r in per:
            a, b = r[f"gen{CAP}"], r[f"gen{need_cap}"]
            if a["prediction"] != b["prediction"]:
                if b["exact"] and not a["exact"]:
                    kind = "completed_previously_truncated"
                elif "repetition" in b["error_types"]:
                    kind = "still_repetition_longer"
                else:
                    kind = "other_change"
                changed.append({"sample_id": r["sample_id"], "kind": kind,
                                "pred_30": a["prediction"], f"pred_{need_cap}": b["prediction"]})
        res["cap_changes"] = changed
        long = [r for r in per if r["n_content_tokens"] + 1 >= 20]
        res["error_type_counts_cap30"] = dict(Counter(t for r in per for t in r[f"gen{CAP}"]["error_types"]))
        res["long14"] = {
            "n": len(long),
            "tf_token_acc": round(sum(r["tf_token_acc"] * (r["n_content_tokens"] + 1) for r in long)
                                  / sum(r["n_content_tokens"] + 1 for r in long), 4),
            "tf_all_correct": sum(not r["tf_wrong_positions"] for r in long),
            "greedy_exact": sum(r[f"gen{CAP}"]["exact"] for r in long),
            "first_error_pos": [r[f"gen{CAP}"]["first_error_pos"] for r in long],
        }
        write(out / f"{name}_per_sample.json", per)
        with open(out / f"{name}_per_sample.tsv", "w", newline="") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(["sample_id", "n_content_tok", "tf_loss", "tf_acc", "tf_first_wrong",
                        "gen30_exact", "gen30_first_err", "gen30_types", "gen30_eos",
                        f"gen{need_cap}_exact", "reference", "gen30", f"gen{need_cap}"])
            for r in per:
                a, b = r[f"gen{CAP}"], r[f"gen{need_cap}"]
                w.writerow([r["sample_id"], r["n_content_tokens"], r["tf_loss"], r["tf_token_acc"],
                            r["tf_first_wrong_pos"], int(a["exact"]), a["first_error_pos"],
                            ",".join(a["error_types"]), int(a["emitted_eos"]), int(b["exact"]),
                            r["reference"], a["prediction"], b["prediction"]])
        summary["runs"][name] = res
        print(f"[{name}]", json.dumps({k: v for k, v in res.items()
                                       if k not in ("consistency", "cap_changes")}), flush=True)
        print(f"[{name}] consistency", json.dumps({k: v for k, v in res["consistency"].items()
                                                   if not k.endswith("row0")}), flush=True)
        print(f"[{name}] cap_changes", json.dumps(changed, ensure_ascii=False), flush=True)
    write(out / "summary.json", summary)
    return 0


def write(path: Path, obj) -> None:
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    raise SystemExit(main())
