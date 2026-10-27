"""OpenFS CPU smoke adapter. Window proposals are NOT fingerspelling detections.
Uses upstream pretrained model via external checkout; no reference or lexicon input.
Research only under upstream license. Keep full frame PTS through dropped hands.
"""
import argparse,hashlib,json,subprocess,sys,time
from pathlib import Path
import numpy as np

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--openfs',type=Path,required=True);ap.add_argument('--checkpoint',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    sys.path.insert(0,str(args.openfs))
    import cv2,mediapipe as mp,torch
    # OpenFS imports a private helper absent from the last Intel-mac Torch wheel.
    # Shape validation only; no change to attention or model weights.
    if not hasattr(torch.nn.functional, '_check_key_padding_mask'):
        def check_mask(mask, src_len, bsz):
            assert mask.shape == (bsz, src_len), 'invalid key padding mask shape'
        torch.nn.functional._check_key_padding_mask = check_mask
    if not hasattr(torch.backends, 'mha'):
        from types import SimpleNamespace
        torch.backends.mha = SimpleNamespace(get_fastpath_enabled=lambda: False)
    from lib.models.recognizer import EncoderDecoderTransformer
    from lib.utils.dataset import normalize
    torch.set_num_threads(2);torch.manual_seed(42)
    chars="$abcdefghijklmnopqrstuvwxyz .&'@"
    # Downloaded recognizer's archived config is 2D / 42 inputs (not current default 63).
    model=EncoderDecoderTransformer(char_size=len(chars)+1,input_dim=42,max_len=1024,d_model=256,nhead=8,num_layers=3,dim_feedforward=2048,dropout=.1,activation='gelu',conventional_positional_encoding=False)
    model.load_state_dict(torch.load(args.checkpoint,map_location='cpu',weights_only=True));model.eval()
    results=[]
    for case in json.loads(args.manifest.read_text()):
        path=Path(case['video']);start=time.monotonic()
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time,pkt_duration_time','-of','json',str(path)]))['frames']
        pts=np.array([float(f['best_effort_timestamp_time']) for f in probe]);end=float(pts[-1])+float(probe[-1].get('pkt_duration_time') or (np.median(np.diff(pts)) if len(pts)>1 else 0))
        if not np.isfinite(end) or end<=0:raise ValueError('cannot establish last frame duration')
        hands=[[],[]];frame_ids=[[],[]]
        cap=cv2.VideoCapture(str(path));i=0
        # Single signer full-frame diagnostic: no YOLO/body crop. Explicit deviation.
        with mp.solutions.holistic.Holistic(model_complexity=1,refine_face_landmarks=False,min_detection_confidence=.5,min_tracking_confidence=.5) as holistic:
            while True:
                ok,frame=cap.read()
                if not ok:break
                r=holistic.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));h,w=frame.shape[:2]
                if r.pose_landmarks:
                    body=r.pose_landmarks.landmark
                    for side,(landmarks,elbow,wrist) in enumerate([(r.right_hand_landmarks,14,16),(r.left_hand_landmarks,13,15)]):
                        if landmarks and body[elbow].y>body[wrist].y:
                            hands[side].append([[v.x*w,v.y*h] for v in landmarks.landmark]);frame_ids[side].append(i)
                i+=1
        cap.release();assert i==len(pts),'frame/PTS mismatch'
        # Fixed full-clip + 2-second windows at 1-second stride, not selected from labels.
        spans=[(0.,end,'whole_clip')]+[(float(s),min(float(s)+2,end),'fixed_window') for s in range(max(0,int(end)-1))]
        outputs=[]
        for lo,hi,kind in spans:
            arrays=[];segments=[];indices=[];source=[]
            for side in range(2):
                ids=np.array(frame_ids[side],dtype=int);keep=(pts[ids]>=lo)&(pts[ids]<hi)
                if not keep.any():continue
                arr=np.array(hands[side],dtype=np.float32)[keep]
                arrays.append(normalize(arr.copy(),.5));segments.extend([side]*len(arr))
                # Match upstream training's per-hand compact index convention.
                indices.extend(range(len(arr)));source.extend(ids[keep].tolist())
            rec={'start_s':lo,'end_s':hi,'time_base':'clip_pts_seconds','proposal_method':kind,'fs_present':None,'status':'unverified_proposal','character_timestamps':None,'letters':None,'hand_frame_count':len(source)}
            if len(source)<8:
                rec['status']='insufficient_hand_observations';outputs.append(rec);continue
            poses=torch.from_numpy(np.concatenate(arrays))[None]
            with torch.inference_mode():
                decoded=model.generate(poses,torch.tensor([segments]),torch.tensor([indices]),max_len=32,bos_token_id=len(chars),eos_token_id=0,pad_token_id=len(chars)+1)
            tokens=decoded['output_ids'][0,1:].tolist();valid=[]
            for t in tokens:
                if t==0 or t>=len(chars):break
                valid.append(t)
            rec['letters']=''.join(chars[t] for t in valid)
            probs=decoded['out_features'][0]
            rec['mean_token_probability_uncalibrated']=float(np.mean([probs[j,t].item() for j,t in enumerate(valid)])) if valid else None
            rec['retained_source_frame_indices']=source
            outputs.append(rec)
        results.append({'case_id':case['case_id'],'input_domain':case.get('domain','unknown'),'video_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'n_frames':i,'hand_observations':[len(x) for x in hands],'seconds':time.monotonic()-start,'outputs':outputs})
        args.out.write_text(json.dumps({'model':'OpenFS recognizer Chicago','upstream_commit':subprocess.check_output(['git','-C',str(args.openfs),'rev-parse','HEAD'],text=True).strip(),'checkpoint_sha256':hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),'is_fs_detector':False,'is_rgb_recognizer':False,'preprocessing':'MediaPipe Holistic complexity=1; single full-frame signer; raised-hand filter; compact per-hand indices; 2D normalize from upstream','ground_truth_supplied':False,'results':results},indent=2))
        print(case['case_id'],[(o['start_s'],o['letters']) for o in outputs],flush=True)
if __name__=='__main__':main()
