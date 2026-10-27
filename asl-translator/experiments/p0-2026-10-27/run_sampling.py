import argparse,csv,hashlib,json,random,subprocess
from pathlib import Path
import numpy as np
from sampling import coverage_motion,uniform

def probe(path):
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(path)]))
    pts=[float(f['best_effort_timestamp_time']) for f in data['frames']]
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vf','scale=160:90','-vsync','0','-pix_fmt','gray','-f','rawvideo','-'])
    frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,90,160)
    assert len(frames)==len(pts) and all(b>a for a,b in zip(pts,pts[1:])), 'PTS/frame mismatch'
    energy=np.r_[0,np.abs(np.diff(frames.astype(float),axis=0)).mean(axis=(1,2))]
    return np.array(pts),energy

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--videos',type=Path,required=True);ap.add_argument('--sheet',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    canonical=Path(__file__).resolve().parents[3]/'asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/case_list.csv'
    allowed={r['clip_id']:r['review_id'] for r in csv.DictReader(canonical.open())}
    cases=list(csv.DictReader(a.sheet.open()))
    assert len(cases)==len(allowed) and len({r['clip_id'] for r in cases})==len(allowed)
    assert all(allowed.get(r['clip_id'])==r['review_id'] for r in cases), 'not the frozen exploratory 45'
    rows=[]
    for c in cases:
        path=a.videos/(c['clip_id']+'.mp4');pts,e=probe(path);n=len(pts);k=min(n,256)
        seed=int(hashlib.sha256(c['clip_id'].encode()).hexdigest()[:8],16)
        arms={'random':sorted(random.Random(seed).sample(range(n),k)), 'uniform':uniform(n,k),'coverage_motion':coverage_motion(e,k)}
        result={'review_id':c['review_id'],'clip_id':c['clip_id'],'domain':'compressed_old_display_only','video_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'n_frames':n,'budget':k,'frame_pts_s':pts.tolist(),'arms':{}}
        for arm,idx in arms.items():
            result['arms'][arm]={'indices':idx,'timestamps_s':pts[idx].tolist(),'max_gap_s':float(np.diff(pts[idx]).max()) if k>1 else 0,'selected_motion_mean':float(e[idx].mean()) if k else 0,'r10_diagnostic_5_16_count':int(sum(5<=pts[i]<16 for i in idx)) if c['review_id']=='R10' else None}
        rows.append(result)
    a.out.write_text(json.dumps(rows,indent=2))
    print(json.dumps({'n_cases':len(rows),'n_over_256':sum(r['n_frames']>256 for r in rows),'R10':next({k:v for k,v in r.items() if k not in ['frame_pts_s','arms']}|{'arms':{a:{k:v for k,v in z.items() if k not in ['indices','timestamps_s']} for a,z in r['arms'].items()}} for r in rows if r['review_id']=='R10')},indent=2))
if __name__=='__main__':main()
