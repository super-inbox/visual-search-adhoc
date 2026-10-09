"""P0-13 context only (NOT part of the controlled comparison): decode the cached frozen-147 Uni-Sign features
with Uni-Sign's own frozen mT5-Base decoder. Two settings: P0.2-matched (greedy, max 30 new tokens) and
official (beam 4, max 100). References = the P0.2 frozen references (same strings both arms use).
Usage: python -I unisign_own_decoder_reference.py UNISIGN_REPO MT5_DIR CKPT FEAT_DIR P02_FROZEN_PRED_JSON OUT_JSON"""
import sys, argparse, json, numpy as np, torch
repo, mt5_dir, ckpt, feat_dir, p02, out_json = sys.argv[1:7]
sys.path.insert(0, repo); import config; config.mt5_path = mt5_dir
import utils as U; from models import Uni_Sign
torch.set_num_threads(3)
args = argparse.ArgumentParser(parents=[U.get_args_parser()]).parse_args([]); args.dataset = "How2Sign"; args.rgb_support = False
m = Uni_Sign(args=args); m.load_state_dict(torch.load(ckpt, map_location="cpu")["model"], strict=True); m.eval()
rows = json.load(open(p02))
tok = m.mt5_tokenizer(["Translate sign language video to English: "], return_tensors="pt")
pre = m.mt5_model.encoder.embed_tokens(tok["input_ids"])
out = []
for r in rows:
    z = np.load(f"{feat_dir}/{r['sample_id']}.npz")
    pe = torch.tensor(np.asarray(z["pose_emb"], dtype=np.float32).tolist())[None]
    with torch.no_grad():
        enc = m.mt5_model.encoder(inputs_embeds=torch.cat([pre, pe], 1)).last_hidden_state
        from transformers.modeling_outputs import BaseModelOutput
        e = BaseModelOutput(last_hidden_state=enc)
        g = m.mt5_model.generate(encoder_outputs=e, max_new_tokens=30, num_beams=1, do_sample=False)
        b = m.mt5_model.generate(encoder_outputs=e, max_new_tokens=100, num_beams=4)
    out.append({"sample_id": r["sample_id"], "reference": r["reference"],
                "greedy30": m.mt5_tokenizer.decode(g[0], skip_special_tokens=True).strip(),
                "beam4_100": m.mt5_tokenizer.decode(b[0], skip_special_tokens=True).strip()})
json.dump(out, open(out_json, "w"), indent=1, ensure_ascii=False)
print("done", len(out))
