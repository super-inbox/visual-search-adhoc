"""Paired Uni-Sign decode. Fail closed on absent/wrong assets; no references read.
Run in the original Uni-Sign CPU environment with its dependencies installed.
"""
import argparse,hashlib,json,random,subprocess,sys
from pathlib import Path
CKPT='1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d'
UPSTREAM='eed438bcb49e30405cd6ccdfcccca330c134e830'
MT5='2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--unisign',type=Path,required=True);ap.add_argument('--checkpoint',type=Path,required=True);ap.add_argument('--mt5',type=Path,required=True);ap.add_argument('--pose-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--preflight-only',action='store_true');a=ap.parse_args()
    repo=Path(__file__).resolve().parents[3]
    canonical=repo/'asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/runs/full45/A_official/run1/candidates.jsonl'
    records=[json.loads(l) for l in canonical.read_text().splitlines()];assert len(records)==45
    absent=[str(p) for p in [a.unisign,a.checkpoint,a.mt5]+[a.pose_dir/(r['clip_id']+'.pkl') for r in records] if not p.exists()]
    if absent:
        a.out.write_text(json.dumps({'status':'BLOCKED_MISSING_ASSETS','missing':absent,'generation_executed':False},indent=2));raise SystemExit(2)
    assert digest(a.checkpoint)==CKPT
    assert subprocess.check_output(['git','-C',str(a.unisign),'rev-parse','HEAD'],text=True).strip()==UPSTREAM
    assert a.mt5.name==MT5
    for r in records:assert digest(a.pose_dir/(r['clip_id']+'.pkl'))==r['pose_sha256']
    if a.preflight_only:
        a.out.write_text(json.dumps({'status':'INPUT_PREFLIGHT_PASS','generation_executed':False}));return
    import torch
    torch.set_num_threads(4);sys.path.insert(0,str(a.unisign))
    import config
    config.mt5_path=str(a.mt5)
    import utils as U
    from models import Uni_Sign
    from datasets import S2T_Dataset
    U.set_seed(42)
    cfg=argparse.ArgumentParser(parents=[U.get_args_parser()]).parse_args([])
    cfg.dataset,cfg.rgb_support,cfg.seed='How2Sign',False,42
    model=Uni_Sign(args=cfg).float().cpu()
    model.load_state_dict(torch.load(a.checkpoint,map_location='cpu',weights_only=True)['model'],strict=True);model.eval()
    ds=S2T_Dataset.__new__(S2T_Dataset);ds.args=cfg;ds.rgb_support=False;ds.max_length=256;ds.phase='test';ds.pose_dir=str(a.pose_dir)
    results=[]
    for r in records:
        random.seed(r['clip_seed']);kps,_=ds.load_pose(r['clip_id']+'.mp4')
        kps={k:v.float() if torch.is_tensor(v) and v.is_floating_point() else v for k,v in kps.items()}
        kps_hash=hashlib.sha256(json.dumps({k:v.tolist() for k,v in sorted(kps.items()) if torch.is_tensor(v)}).encode()).hexdigest()
        assert kps_hash==r['kps_sha256'],'model input differs from canonical'
        src,_=ds.collate_fn([(r['clip_id'],kps,'','',{})]);result={'review_id':r['review_id'],'clip_id':r['clip_id'],'kps_sha256':kps_hash,'arms':{}}
        with torch.inference_mode():
            enc=model(src,{'gt_sentence':['']})
            for arm,ngrams in [('control',0),('no_repeat_token_trigram',3)]:
                seq=model.mt5_model.generate(inputs_embeds=enc['inputs_embeds'],attention_mask=enc['attention_mask'],num_beams=4,max_new_tokens=100,do_sample=False,no_repeat_ngram_size=ngrams)
                ids=seq[0].tolist();result['arms'][arm]={'text':model.mt5_tokenizer.decode(ids,skip_special_tokens=True),'token_ids':ids,'eos_present':model.mt5_tokenizer.eos_token_id in ids}
        result['control_matches_saved_cpu']=result['arms']['control']['text']==r['T']['text']
        results.append(result);a.out.write_text(json.dumps({'status':'RUNNING','generation_executed':True,'results':results},indent=2))
        if not result['control_matches_saved_cpu']:raise RuntimeError('Control mismatch: stop before interpreting treatment')
    a.out.write_text(json.dumps({'status':'COMPLETE','generation_executed':True,'checkpoint_sha256':CKPT,'upstream_commit':UPSTREAM,'results':results},indent=2))
if __name__=='__main__':main()
