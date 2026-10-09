"""P0-13 interface check: decode cached Uni-Sign encoder features with Uni-Sign's OWN frozen mT5 decoder
(beam 4, max_new_tokens 100 = official) and compare with the authors' released predictions for the same clip.
If the cached `enc` is the true Uni-Sign encoder output, these decodes should closely track the authors'.
Usage: python -I validate_feature_interface.py UNISIGN_REPO MT5_DIR CKPT FEAT_DIR PER_CLIP_CSV OUT_JSON N"""
import sys, argparse, csv, json, numpy as np, torch
repo, mt5_dir, ckpt, feat_dir, per_clip, out_json, n = sys.argv[1:8]
sys.path.insert(0, repo); import config; config.mt5_path = mt5_dir
import utils as U; from models import Uni_Sign
from transformers.modeling_outputs import BaseModelOutput
args = argparse.ArgumentParser(parents=[U.get_args_parser()]).parse_args([]); args.dataset = "How2Sign"; args.rgb_support = False
m = Uni_Sign(args=args); m.load_state_dict(torch.load(ckpt, map_location="cpu")["model"], strict=True); m.eval()
rows = list(csv.DictReader(open(per_clip)))[: int(n)]
import sacrebleu
res = []
for r in rows:
    z = np.load(f"{feat_dir}/{r['clip_id']}.npz")
    enc = torch.tensor(np.asarray(z["enc"], dtype=np.float32).tolist())[None]
    # the decoder also attends to the 8 prefix positions; re-encode the prefix+pose_emb to get them exactly
    pe = torch.tensor(np.asarray(z["pose_emb"], dtype=np.float32).tolist())[None]
    tok = m.mt5_tokenizer(["Translate sign language video to English: "], return_tensors="pt")
    emb = torch.cat([m.mt5_model.encoder.embed_tokens(tok["input_ids"]), pe], 1)
    with torch.no_grad():
        full = m.mt5_model.encoder(inputs_embeds=emb).last_hidden_state
        cos = torch.nn.functional.cosine_similarity(full[0, tok["input_ids"].shape[1]:], enc[0], dim=-1)
        out = m.mt5_model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=full), max_new_tokens=100, num_beams=4)
    pred = m.mt5_tokenizer.batch_decode(out, skip_special_tokens=True)[0]
    res.append({"clip_id": r["clip_id"], "reference": r["reference"], "authors_prediction": r["authors_prediction"],
                "decode_from_cached_features": pred, "reencode_vs_cached_cos_min": float(cos.min()),
                "chrf_vs_authors_prediction": sacrebleu.sentence_chrf(pred, [r["authors_prediction"]]).score})
    print(json.dumps(res[-1], ensure_ascii=False)[:400], flush=True)
json.dump(res, open(out_json, "w"), indent=1, ensure_ascii=False)
print("mean chrF(decode vs authors) %.1f" % np.mean([x["chrf_vs_authors_prediction"] for x in res]))
