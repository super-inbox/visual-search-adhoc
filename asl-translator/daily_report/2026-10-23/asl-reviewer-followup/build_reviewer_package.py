"""Build the local ASL-fluent reviewer package for the open P0-B (R02/R05/R35) and P0-C (R26/R29) blockers.

Cuts short full-frame clips from the How2Sign TEST raw videos and writes the clip manifest (`build`), then assembles a
two-stage local package (`package`, also run at the end of `build`):
  package_local/send_step1_blind/                  BLIND: clips + Step 1 instructions + blind_review.csv +
                                                    review_blind.html + SHA256SUMS. No reference text, targets, spans,
                                                    model output or internal metadata.
  package_local/send_step2_reference_conditioned/  REFERENCE-CONDITIONED FOLLOW-UP: Step 2 instructions +
                                                    reference_conditioned_followup.csv + review_reference_conditioned.html
                                                    + SHA256SUMS. Send only after the Step 1 file is returned.
Videos stay local (CC BY-NC 4.0; package_local/ is git-excluded). Never opens val / H18 / H19 material.

usage:
  python -I build_reviewer_package.py build           # cut clips into package_local/clips, write manifest, then package
  python -I build_reviewer_package.py package         # (re)assemble both stages from existing, sha256-verified clips
  python -I build_reviewer_package.py derive STEP2CSV # after review only: R26 containment (reference-conditioned)
"""
import csv, hashlib, json, os, shutil, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REPORT = os.path.dirname(HERE)
PKG = os.path.join(HERE, "package_local")
WORK = os.path.join(PKG, "_src")  # extracted raw videos, deleted after the build
TEST_ZIP = os.path.expanduser("~/Desktop/curify/p018-work/downloads/test_raw_videos.zip")
TEST_CSV = os.path.expanduser("~/Desktop/curify/p018-work/downloads/how2sign_test.csv")
PROV = os.path.join(REPORT, "p0a-candidate-rerank", "provenance", "case_provenance.csv")
P012 = "docs/daily_report/10.06/asl-p0-12-unisign-pose-gap/artifacts/prepared_inputs"

sys.path.insert(0, os.path.join(REPO, "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402

DOM_OLD = "B_ours_5p39: old preprocessing (original timing; full frame, as the model saw it)"
DOM_OFF = "A_official: official preprocessing (realigned timing; shown FULL FRAME; the official crop is not available as video)"
DOM_CTX = "source context: full-frame raw source span (no preprocessing window)"

# P0-B: both matched windows per case, read from case_provenance.csv. P0-C: fixed context spans (2026-10-24 request).
P0B = ["R02", "R05", "R35"]
P0C = {"R26": ("G3EfBFwsOpE_3-10-rgb_front", 11.75, 16.75), "R29": ("92V3oH63zbQ_5-1-rgb_front", 5.00, 25.80)}
P0C_NEIGHBOURS = {"R26": ("G3EfBFwsOpE_2", "G3EfBFwsOpE_4"), "R29": ("92V3oH63zbQ_4", "92V3oH63zbQ_6")}
# Team-side only (never written into the reviewer package): used by `derive` after the review.
R26_OFFICIAL_WINDOW = (15.15, 16.62)

LABEL_COLS = [
    # provenance (pre-filled)
    "row_id", "review_id", "task", "clip_id", "video_file", "preprocessing_domain", "source_video",
    "source_start_s", "source_end_s", "clip_duration_s", "source_video_sha256", "clip_sha256", "span_no",
    # STEP 1 - blind (P0-B rows)
    "fs_present", "fs_start_s", "fs_end_s", "letters_seen_blind", "fs_type", "hand_visibility",
    # STEP 1 - blind (P0-C rows)
    "utterance_boundaries_blind_s",
    "notes_blind",
    # STEP 2 - after opening step2_unblind (P0-B rows)
    "reference_name_after_unblind", "matches_reference_name",
    # STEP 2 - after opening step2_unblind (P0-C rows)
    "target_found", "target_start_s", "target_end_s", "target_confidence",
    "notes_after_unblind",
    # reviewer
    "reviewer_id", "asl_background", "step1_completed_at", "step2_completed_at",
]
PROV_COLS = LABEL_COLS[:LABEL_COLS.index("span_no")]
REVIEWER_COLS = LABEL_COLS[LABEL_COLS.index("span_no") + 1:]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def guard_path(p):
    low = os.path.basename(p).lower()
    if "val" in low or "h18" in low or "h19" in low:
        raise SystemExit(f"refusing to open holdout/val path: {p}")
    return p


def fix_text(s):  # the downloaded test CSV has cp1252/UTF-8 mojibake in apostrophes
    for enc in ("cp1252", "latin-1"):
        try:
            return s.encode(enc).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return s


def sentences():
    with open(guard_path(TEST_CSV), encoding="utf-8") as f:
        return {r["SENTENCE_ID"] + "|" + r["VIDEO_NAME"]: fix_text(r["SENTENCE"]) for r in csv.DictReader(f, delimiter="\t")}


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                          "stream=width,height,r_frame_rate,nb_read_frames", "-of", "json", path],
                         capture_output=True, check=True, text=True).stdout
    s = json.loads(out)["streams"][0]; n, d = map(int, s["r_frame_rate"].split("/"))
    return s["width"], s["height"], n / d, int(s["nb_read_frames"])


def cut(src, a, b, dst):
    # Re-encode (frame-accurate start), native resolution and fps, no audio, no overlays.
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-i", src, "-t", f"{b - a:.3f}", "-an",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", "-map_metadata", "-1", dst], check=True)


def rows_spec():
    prov = {r["review_id"]: r for r in csv.DictReader(open(PROV))}
    spec = []
    for rid in P0B:
        p = prov[rid]; vid = p["clip_id"].split("_")[0]; vn = p["clip_id"].split("-", 1)[1]
        src = f"{vid}-{vn}.mp4"
        spec.append(dict(row_id=f"{rid}-old", review_id=rid, task="P0-B", clip_id=p["clip_id"], src=src,
                         a=float(p["orig_start"]), b=float(p["orig_end"]), dom=DOM_OLD,
                         pkl=f"{P012}/B_ours_5p39/test-pose-rtmpose-192/{p['clip_id']}.pkl"))
        spec.append(dict(row_id=f"{rid}-official", review_id=rid, task="P0-B", clip_id=p["clip_id"], src=src,
                         a=float(p["realigned_start"]), b=float(p["realigned_end"]), dom=DOM_OFF,
                         pkl=f"{P012}/A_official/test-pose-rtmpose-192/{p['clip_id']}.pkl"))
    for rid, (cid, a, b) in P0C.items():
        vid = cid.split("_")[0]; vn = cid.split("-", 1)[1]
        spec.append(dict(row_id=f"{rid}-context", review_id=rid, task="P0-C", clip_id=cid, src=f"{vid}-{vn}.mp4",
                         a=a, b=b, dom=DOM_CTX, pkl=""))
    return spec


def labels_blank(path):
    if not os.path.exists(path):
        return True
    return all(not (r.get(c) or "").strip() for r in csv.DictReader(open(path)) for c in REVIEWER_COLS)


def build():
    spec = rows_spec()
    assert_not_holdout(sorted({s["clip_id"] for s in spec}))
    labels_path = os.path.join(HERE, "reviewer_labels.csv")
    if not labels_blank(labels_path):
        raise SystemExit("reviewer_labels.csv already has reviewer answers - refusing to overwrite")
    clips_dir = os.path.join(PKG, "clips")
    for d in (WORK, clips_dir):
        os.makedirs(d, exist_ok=True)

    srcs = sorted({s["src"] for s in spec})
    subprocess.run(["unzip", "-o", "-j", "-q", guard_path(TEST_ZIP)] + [f"raw_videos/{s}" for s in srcs] + ["-d", WORK],
                   check=True)
    src_sha = {s: sha256(os.path.join(WORK, s)) for s in srcs}

    manifest = []
    for s in spec:
        clip = f"{s['row_id']}.mp4"; dst = os.path.join(clips_dir, clip)
        cut(os.path.join(WORK, s["src"]), s["a"], s["b"], dst)
        w, h, fps, n = probe(dst)
        pkl_abs = os.path.join(REPO, s["pkl"]) if s["pkl"] else ""
        manifest.append(dict(
            row_id=s["row_id"], review_id=s["review_id"], task=s["task"], clip_id=s["clip_id"], video_file=f"clips/{clip}",
            preprocessing_domain=s["dom"], source_video=f"raw_videos/{s['src']}", source_zip=os.path.basename(TEST_ZIP),
            source_start_s=f"{s['a']:.2f}", source_end_s=f"{s['b']:.2f}", clip_duration_s=f"{n / fps:.3f}",
            clip_fps=f"{fps:g}", clip_w_h=f"{w}x{h}", clip_frames=n, source_video_sha256=src_sha[s["src"]],
            clip_sha256=sha256(dst), clip_bytes=os.path.getsize(dst), p012_model_input_pkl=s["pkl"],
            p012_model_input_pkl_sha256=sha256(pkl_abs) if pkl_abs and os.path.exists(pkl_abs) else ""))
    mcols = list(manifest[0])
    with open(os.path.join(HERE, "reviewer_package_manifest.csv"), "w", newline="") as f:  # INTERNAL ONLY
        w = csv.DictWriter(f, fieldnames=mcols, lineterminator="\n"); w.writeheader(); w.writerows(manifest)
    shutil.rmtree(WORK)
    package()


# ── two-stage package (2026-10-27): blind Step 1, reference-conditioned Step 2 ───────────────────────────────────────
# Step 1 sends only what an independent ASL judgement needs: clip file, duration, row type. No reference text, target
# word, source spans, domain names, model output or automatic labels. Step 2 adds a TARGET that the team selected after
# consulting the English reference; it is annotation refinement only, never evidence of reference-free localization.
STEP1_COLS = ["row_id", "video_file", "clip_duration_s", "row_type", "span_no",
              "fs_present", "fs_start_s", "fs_end_s", "fs_letters_or_word", "fs_confidence", "fs_type", "hand_visibility",
              "issue_flags", "utterance_boundaries_s", "boundaries_confidence", "notes",
              "reviewer_id", "asl_background", "step1_completed_at"]
STEP2_COLS = ["row_id", "video_file", "clip_duration_s", "row_type", "reference_conditioned_target",
              "target_selected_from", "reference_sentence_shown", "span_no",
              "target_visibly_signed", "corrected_start_s", "corrected_end_s", "corrected_letters", "target_confidence",
              "notes_step2", "reviewer_id", "step2_completed_at"]
STEP1_REVIEWER = STEP1_COLS[STEP1_COLS.index("span_no") + 1:]
STEP2_REVIEWER = STEP2_COLS[STEP2_COLS.index("span_no") + 1:]
# Reference-conditioned targets for P0-B: the person name in each English reference (as already listed in
# p0b-fingerspelling-feasibility/FEASIBILITY.md). Written ONLY into Step 2 files.
P0B_TARGET = {"R02": "Mike Camelin", "R05": "Les Whitley", "R35": "CarolAnn"}
SELECTED_FROM = "English reference text (How2Sign); target chosen by the research team after consulting the reference"
SEND1, SEND2 = os.path.join(PKG, "send_step1_blind"), os.path.join(PKG, "send_step2_reference_conditioned")

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
:root{--bg:#fff;--fg:#1d1d1f;--mut:#666;--line:#ddd;--acc:#0b57d0;--warn:#b3261e;--card:#fafafa}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--fg:#eee;--mut:#aaa;--line:#333;--acc:#8ab4f8;--warn:#f2b8b5;--card:#1c1c1c}}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;z-index:2}
header input{margin:2px 6px 2px 0}main{max-width:980px;margin:0 auto;padding:12px 16px}
.banner{border:2px solid var(--warn);color:var(--warn);padding:8px 12px;border-radius:6px;margin:8px 0;font-weight:600}
.card{border:1px solid var(--line);background:var(--card);border-radius:8px;padding:12px;margin:14px 0}
video{width:100%;max-height:360px;background:#000;border-radius:6px}.row{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:6px 0}
label{display:inline-flex;flex-direction:column;font-size:12.5px;color:var(--mut)}label>*{color:var(--fg);font-size:14px}
input[type=text]{min-width:90px}textarea{width:100%;min-height:38px}.t{font-variant-numeric:tabular-nums;color:var(--mut)}
.cue{border-left:4px solid var(--warn);padding:6px 10px;margin:8px 0}button{cursor:pointer}
</style></head><body><header><b>__TITLE__</b>__BANNER__
<div class="row"><label>Reviewer ID<input id="rid" type="text"></label>__BGFIELD__
<label>Clips<input id="files" type="file" accept="video/mp4" multiple></label>
<button id="exp">Export __CSV__</button><label>Import CSV<input id="imp" type="file" accept=".csv"></label></div></header>
<main id="m"></main><script>
const D=__DATA__, KEY='asl-review-'+D.stage, S=JSON.parse(localStorage.getItem(KEY)||'{}'), urls={};
const $=s=>document.querySelector(s), esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function save(){localStorage.setItem(KEY,JSON.stringify(S))}
S.__meta=S.__meta||{};$('#rid').value=S.__meta.reviewer_id||'';$('#rid').oninput=e=>{S.__meta.reviewer_id=e.target.value;save()};
if($('#bg')){$('#bg').value=S.__meta.asl_background||'';$('#bg').oninput=e=>{S.__meta.asl_background=e.target.value;save()}}
function field(k,f,r,sp){const id=r.row_id+'|'+sp+'|'+f.name,v=(S[id]??'');
 if(f.type==='select')return `<label>${esc(f.label)}<select data-id="${id}"><option value=""></option>${f.options.map(o=>`<option ${o===v?'selected':''}>${o}</option>`).join('')}</select></label>`;
 if(f.type==='time')return `<label>${esc(f.label)}<span><input type="text" size="6" data-id="${id}" value="${esc(v)}"> <button data-now="${id}" data-v="${r.row_id}">= now</button></span></label>`;
 if(f.type==='area')return `<label style="flex:1 1 100%">${esc(f.label)}<textarea data-id="${id}">${esc(v)}</textarea></label>`;
 return `<label>${esc(f.label)}<input type="text" data-id="${id}" value="${esc(v)}" size="${f.size||14}"></label>`}
function render(){$('#m').innerHTML=D.intro+D.rows.map(r=>{const n=S['spans|'+r.row_id]||1,fs=D.fields[r.row_type];
 let spans='';for(let sp=1;sp<=n;sp++)spans+=`<div class="row">${n>1?`<b>span ${sp}</b>`:''}${fs.map(f=>field(r.row_type,f,r,sp)).join('')}</div>`;
 return `<div class="card"><div class="row"><b>${esc(r.row_id)}</b><span class="t">${esc(r.row_type_label)} · ${esc(r.video_file)} · ${esc(r.clip_duration_s)} s</span></div>
 ${r.cue?`<div class="cue"><b>${esc(D.cue_label)}</b> ${esc(r.cue)}${r.sentence?`<br><span class="t">${esc(D.cue_sentence_label)} ${esc(r.sentence)}</span>`:''}</div>`:''}
 <video id="v-${esc(r.row_id)}" controls preload="metadata" ${urls[r.video_file.split('/').pop()]?`src="${urls[r.video_file.split('/').pop()]}"`:''}></video>
 <div class="row"><span class="t" id="t-${esc(r.row_id)}">0.0 s</span>${[1,0.5,0.25].map(x=>`<button data-rate="${x}" data-v="${esc(r.row_id)}">${x}×</button>`).join('')}
 <button data-back="${esc(r.row_id)}">−2 s</button>${D.multispan?`<button data-addspan="${esc(r.row_id)}">+ span</button>`:''}</div>${spans}</div>`}).join('');
 document.querySelectorAll('video').forEach(v=>v.ontimeupdate=()=>{$('#t-'+v.id.slice(2)).textContent=v.currentTime.toFixed(1)+' s'});}
document.addEventListener('input',e=>{const id=e.target.dataset.id;if(id){S[id]=e.target.value;save()}});
document.addEventListener('change',e=>{const id=e.target.dataset.id;if(id){S[id]=e.target.value;save()}});
document.addEventListener('click',e=>{const t=e.target,d=t.dataset;
 if(d.rate){const v=document.getElementById('v-'+d.v);v.playbackRate=+d.rate}
 if(d.back){const v=document.getElementById('v-'+d.back);v.currentTime=Math.max(0,v.currentTime-2)}
 if(d.now){const v=document.getElementById('v-'+d.v);S[d.now]=v.currentTime.toFixed(1);save();render()}
 if(d.addspan){S['spans|'+d.addspan]=(S['spans|'+d.addspan]||1)+1;save();render()}});
$('#files').onchange=e=>{for(const f of e.target.files)urls[f.name]=URL.createObjectURL(f);render()};
const cell=v=>/[",\n]/.test(v=String(v??''))?'"'+v.replace(/"/g,'""')+'"':v;
$('#exp').onclick=()=>{const L=[D.cols.join(',')],now=new Date().toISOString();
 for(const r of D.rows){const n=S['spans|'+r.row_id]||1;for(let sp=1;sp<=n;sp++){const o={...r.prefill,span_no:sp};
  for(const c of D.reviewer_cols){const v=S[r.row_id+'|'+sp+'|'+c];if(v!==undefined)o[c]=v}
  o.reviewer_id=S.__meta.reviewer_id||'';if('asl_background' in o||D.cols.includes('asl_background'))o.asl_background=S.__meta.asl_background||'';
  o[D.done_col]=now;L.push(D.cols.map(c=>cell(o[c])).join(','))}}
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([L.join('\r\n')+'\r\n'],{type:'text/csv'}));a.download=D.csv;a.click()};
$('#imp').onchange=async e=>{const t=await e.target.files[0].text(),rows=[];let row=[],c='',q=false;
 for(let i=0;i<t.length;i++){const ch=t[i];if(q){if(ch=='"'&&t[i+1]=='"'){c+='"';i++}else if(ch=='"')q=false;else c+=ch}
  else if(ch=='"')q=true;else if(ch==','){row.push(c);c=''}else if(ch=='\n'){row.push(c.replace(/\r$/,''));rows.push(row);row=[];c=''}else c+=ch}
 const h=rows.shift();for(const r of rows){if(r.length<h.length)continue;const o={};h.forEach((k,i)=>o[k]=r[i]);
  const sp=+o.span_no||1;S['spans|'+o.row_id]=Math.max(S['spans|'+o.row_id]||1,sp);
  for(const k of D.reviewer_cols)if(o[k])S[o.row_id+'|'+sp+'|'+k]=o[k];if(o.reviewer_id)S.__meta.reviewer_id=o.reviewer_id;if(o.asl_background)S.__meta.asl_background=o.asl_background}
 save();location.reload()};
render();
</script></body></html>"""

FS_FIELDS1 = [dict(name="fs_present", label="1. Fingerspelling present?", type="select", options=["yes", "no", "unsure"]),
              dict(name="fs_start_s", label="2. Start (s)", type="time"), dict(name="fs_end_s", label="End (s)", type="time"),
              dict(name="fs_letters_or_word", label="3. Letters / word (? = unreadable letter, or 'unsure')", size=22),
              dict(name="fs_confidence", label="4. Confidence", type="select", options=["high", "medium", "low"]),
              dict(name="fs_type", label="Type (optional)", type="select",
                   options=["fingerspelling", "name sign", "lexicalized fingerspelling", "unsure"]),
              dict(name="hand_visibility", label="Hand visibility (optional)", type="select", options=["good", "partial", "poor"]),
              dict(name="issue_flags", label="Issues (optional): occlusion; hand out of frame; fast signing; unclear letter; other", size=30),
              dict(name="notes", label="Notes (optional)", type="area")]
UB_FIELDS1 = [dict(name="utterance_boundaries_s", label="Boundary times (s), e.g. 1.2; 3.8; 7.5", size=30),
              dict(name="boundaries_confidence", label="Confidence", type="select", options=["high", "medium", "low"]),
              dict(name="notes", label="Notes (optional): rough gloss / summary of each part", type="area")]
FIELDS2 = [dict(name="target_visibly_signed", label="1. Target actually visible / signed?", type="select",
                options=["yes", "partly", "no", "unsure"]),
           dict(name="corrected_start_s", label="2. Start (s)", type="time"), dict(name="corrected_end_s", label="End (s)", type="time"),
           dict(name="corrected_letters", label="3. Letters as signed (R02/R05/R35; ? = unreadable)", size=22),
           dict(name="target_confidence", label="4. Confidence", type="select", options=["high", "medium", "low"]),
           dict(name="notes_step2", label="5. Notes", type="area")]


def write_html(path, stage, title, banner, rows, cols, reviewer_cols, fields, csv_name, done_col, intro, multispan, bgfield,
               target_label="", sentence_label=""):
    data = dict(stage=stage, rows=rows, cols=cols, reviewer_cols=reviewer_cols, fields=fields, csv=csv_name,
                done_col=done_col, intro=intro, multispan=multispan, cue_label=target_label, cue_sentence_label=sentence_label)
    page = (HTML.replace("__TITLE__", title).replace("__BANNER__", banner).replace("__CSV__", csv_name)
            .replace("__BGFIELD__", bgfield).replace("__DATA__", json.dumps(data, ensure_ascii=False)))
    open(path, "w", encoding="utf-8").write(page)


def write_template(path, cols, rows, reviewer_cols):
    """Blank template; refuses to overwrite a sheet that already holds reviewer answers."""
    if os.path.exists(path) and any((r.get(c) or "").strip() for r in csv.DictReader(open(path)) for c in reviewer_cols
                                    if c not in ("reviewer_id",)):
        raise SystemExit(f"{os.path.basename(path)} already has reviewer answers - refusing to overwrite")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def package():
    """Assemble both stages from the existing clips. Clips are verified against the committed manifest, never re-cut."""
    man = list(csv.DictReader(open(os.path.join(HERE, "reviewer_package_manifest.csv"))))
    assert_not_holdout(sorted({m["clip_id"] for m in man}))
    clips_dir = os.path.join(PKG, "clips")
    for m in man:
        got = sha256(os.path.join(clips_dir, os.path.basename(m["video_file"])))
        if got != m["clip_sha256"]:
            raise SystemExit(f"{m['row_id']}: clip sha256 {got} != manifest {m['clip_sha256']}")
    S = sentences()
    def sent(sid, cid): return S[sid + "|" + cid.split("_")[0] + "-" + cid.split("-", 1)[1]]
    rows1, rows2 = [], []
    for m in man:
        is_fs = m["task"] == "P0-B"
        base = dict(row_id=m["row_id"], video_file=m["video_file"], clip_duration_s=m["clip_duration_s"],
                    row_type="fingerspelling_check" if is_fs else "utterance_boundaries", span_no="1")
        rows1.append(dict(base))
        if is_fs:
            target, sentence = P0B_TARGET[m["review_id"]], sent(m["clip_id"].split("-")[0], m["clip_id"])
        else:
            prev, nxt = P0C_NEIGHBOURS[m["review_id"]]
            target = sent(m["clip_id"].split("-")[0], m["clip_id"])
            sentence = (f"Said before (orientation): {sent(prev, m['clip_id'])} | TARGET: {target} | "
                        f"Said after (orientation): {sent(nxt, m['clip_id'])}")
        rows2.append(dict(base, reference_conditioned_target=target, target_selected_from=SELECTED_FROM,
                          reference_sentence_shown=sentence))
    if not is_blank_text(rows1):
        raise SystemExit("step-1 rows contain text beyond clip metadata")
    write_template(os.path.join(HERE, "blind_review.csv"), STEP1_COLS, rows1, STEP1_REVIEWER)
    write_template(os.path.join(HERE, "reference_conditioned_followup.csv"), STEP2_COLS, rows2, STEP2_REVIEWER)
    lab = {"fingerspelling_check": "fingerspelling check", "utterance_boundaries": "utterance boundaries"}
    pre1 = lambda r: {c: r[c] for c in ("row_id", "video_file", "clip_duration_s", "row_type")}
    write_html(os.path.join(HERE, "review_blind.html"), "step1_blind", "ASL review · Step 1 (blind)", "",
               [dict(pre1(r), row_type_label=lab[r["row_type"]], prefill=pre1(r)) for r in rows1],
               STEP1_COLS, STEP1_REVIEWER, {"fingerspelling_check": FS_FIELDS1, "utterance_boundaries": UB_FIELDS1},
               "blind_review.csv", "step1_completed_at",
               "<p>Annotate only what is visible and signed. Mark <b>unsure</b> when uncertain. Times are seconds from "
               "the clip start. Load the 8 clips with <b>Clips</b> above. Progress autosaves in this browser; "
               "<b>Export</b> when done.</p>", True,
               '<label>ASL background<input id="bg" type="text" size="28"></label>')
    pre2 = lambda r: {c: r[c] for c in ("row_id", "video_file", "clip_duration_s", "row_type", "reference_conditioned_target",
                                        "target_selected_from", "reference_sentence_shown")}
    write_html(os.path.join(HERE, "review_reference_conditioned.html"), "step2_reference_conditioned",
               "ASL review · Step 2 · REFERENCE-CONDITIONED FOLLOW-UP",
               '<div class="banner">REFERENCE-CONDITIONED FOLLOW-UP. Targets were selected by the research team after '
               'consulting the English reference. Annotations here are refinement only and are not blind evidence. '
               'Open only after your Step 1 file has been returned; do not change Step 1 answers.</div>',
               [dict(pre2(r), row_type_label=lab[r["row_type"]], cue=r["reference_conditioned_target"],
                     sentence=r["reference_sentence_shown"], prefill=pre2(r)) for r in rows2],
               STEP2_COLS, STEP2_REVIEWER, {"fingerspelling_check": FIELDS2, "utterance_boundaries": FIELDS2},
               "reference_conditioned_followup.csv", "step2_completed_at",
               "<p>For each clip: is the reference-conditioned target actually signed, where, and how? Keep Step 1 "
               "answers unchanged.</p>", True, "",
               "Reference-conditioned target (selected by the research team after consulting the English reference; "
               "not detected in the video):", "Reference text:")
    stages = {SEND1: ["reviewer_instructions.md", "blind_review.csv", "review_blind.html"],
              SEND2: ["reviewer_instructions_step2.md", "reference_conditioned_followup.csv", "review_reference_conditioned.html"]}
    for d, docs in stages.items():
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        for f in docs:
            shutil.copy(os.path.join(HERE, f), os.path.join(d, f))
        if d == SEND1:
            os.makedirs(os.path.join(d, "clips"))
            for m in man:
                shutil.copy(os.path.join(clips_dir, os.path.basename(m["video_file"])), os.path.join(d, m["video_file"]))
        files = sorted(os.path.relpath(os.path.join(r, f), d) for r, _, fs in os.walk(d) for f in fs if f != "SHA256SUMS")
        open(os.path.join(d, "SHA256SUMS"), "w").write("".join(f"{sha256(os.path.join(d, f))}  {f}\n" for f in files))
        with zipfile.ZipFile(d + ".zip", "w", zipfile.ZIP_STORED) as z:
            for f in files + ["SHA256SUMS"]:  # fixed timestamp/permissions -> byte-identical rebuilds
                zi = zipfile.ZipInfo(os.path.join(os.path.basename(d), f), date_time=(2026, 10, 27, 0, 0, 0))
                zi.external_attr = 0o644 << 16
                with open(os.path.join(d, f), "rb") as fh:
                    z.writestr(zi, fh.read())
    print(json.dumps({"step1": sorted(os.listdir(SEND1)), "step2": sorted(os.listdir(SEND2)),
                      "step1_zip_bytes": os.path.getsize(SEND1 + ".zip"), "step2_zip_bytes": os.path.getsize(SEND2 + ".zip")},
                     indent=1))


def is_blank_text(rows):
    return all(set(r) <= {"row_id", "video_file", "clip_duration_s", "row_type", "span_no"} for r in rows)


def derive(labels):
    """After the review: is the reviewer-marked R26 target signing fully inside the official window (source seconds)?
    The span comes from Step 2, so the result is REFERENCE-CONDITIONED: a human located the sentence after reading it.
    It is annotation refinement / diagnosis only, never evidence of reference-free localization."""
    starts = {r["row_id"]: float(r["source_start_s"]) for r in csv.DictReader(open(os.path.join(HERE, "reviewer_package_manifest.csv")))}
    for r in csv.DictReader(open(labels)):
        if r["row_id"] != "R26-context":
            continue
        if not (r["corrected_start_s"].strip() and r["corrected_end_s"].strip()):
            print("R26: target span not marked"); continue
        off = starts["R26-context"]; a, b = off + float(r["corrected_start_s"]), off + float(r["corrected_end_s"])
        lo, hi = R26_OFFICIAL_WINDOW
        print(f"[REFERENCE-CONDITIONED] R26 target (source s) {a:.2f}-{b:.2f}; official {lo:.2f}-{hi:.2f}; "
              f"fully_contained={lo <= a and b <= hi}; overlap_s={max(0.0, min(b, hi) - max(a, lo)):.2f}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["build"]:
        build()
    elif sys.argv[1:2] == ["package"]:
        package()
    elif sys.argv[1:2] == ["derive"] and len(sys.argv) == 3:
        derive(sys.argv[2])
    else:
        raise SystemExit(__doc__)
