#!/usr/bin/env python3
"""Build the P0-1 Stage A Step 1 (blind) reviewer package for FSA-001 ... FSA-036.

Reads the frozen candidate set (results/p0_1_stage_a_candidate_set.json) for the blind-ID -> clip mapping only.
Clips are stream-copied from the frozen How2Sign v2 videos (sha256-verified against FREEZE_CHECKSUMS) with all
container metadata and any audio removed, and renamed to the blind ID.

  package_local/send_step1_blind/  sent to the reviewer: reviewer_instructions.md, blind_review.csv,
                                    review_blind.html, clips/FSA-###.mp4, SHA256SUMS
  package_local/internal/          team only: blind_mapping.csv (blind ID -> clip, source, hashes, tier),
                                    build_log.json, leakage_check.json
package_local/ stays out of git (local exclude), as for the 2026-10-23 package. The three reviewer-facing text files
are also written next to this script so they can be versioned.

The reviewer-facing files never contain: clip or source IDs, reference text, names, expected letters, any model output,
selection tiers or screen windows. `build` ends with an automatic leakage scan over the send folder; the reference
sentences are read ONLY for that scan.

usage: python3 -I build_stage_a_package.py --videos-dir DIR
"""
import argparse, csv, hashlib, json, re, shutil, subprocess, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CAND = REPO / "asl-translator/experiments/p0-2026-10-29/results/p0_1_stage_a_candidate_set.json"
PREREG = REPO / "asl-translator/experiments/p0-2026-10-29/results/p0_1_stage_a_preregistration.json"
BENCH = REPO / "asl-translator/data/public_benchmarks/how2sign_v2"
REFS = REPO / "docs/daily_report/10.13/asl-unisign-error-taxonomy/inputs_128.jsonl"
PKG = HERE / "package_local"
SEND = PKG / "send_step1_blind"
INTERNAL = PKG / "internal"
CSV_NAME = "blind_review.csv"
STORAGE_KEY = "p0_1_stage_a_step1_v1"
ITEM_FIELDS = ["fingerspelling_present", "multiple_spans_in_clip", "notes"]
SPAN_FIELDS = ["span_start_s", "span_end_s", "letters", "letters_confidence", "signing_hand", "visibility_issue",
               "occlusion_issue"]
FORBIDDEN_WORDS = ["positive", "negative", "random", "tier", "likely", "screen", "candidate", "openfs", "handreader",
                   "uni-sign", "unisign", "gemini", "openai", "reference", "how2sign", "rgb_front"]


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


INSTRUCTIONS = """# Fingerspelling check · Step 1 (blind)

Thank you for helping. This step has 36 short video clips, named FSA-001 to FSA-036. Each clip shows one signer.
There is no sound.

## What to do for each clip

1. Watch the whole clip. You can slow it down (1×, 0.5×, 0.25×) and step back 2 seconds.
2. Answer **Is fingerspelling present?**: `yes`, `no` or `uncertain`.
3. **If yes**, for each fingerspelled stretch:
   - **start / end:** clip time in seconds where the fingerspelling starts and ends. Use the "= now" button to copy
     the current video time.
   - **letters:** the letters you see, in order, a–z, exactly as signed. Do not correct them to a word you think was
     meant. Write `?` for a letter you can see is there but cannot read.
   - **confidence** in the letters: `high`, `medium` or `low`.
   - **signing hand**, if you can tell: `left`, `right`, `both` or `unclear`.
   - **visibility** and **occlusion** problems, if any.
   - If a clip has more than one fingerspelled stretch, press **+ span** and fill in a row for each one, and set
     "more than one span" to `yes`.
4. **If no**, leave the span fields and letters blank.
5. **If uncertain**, write briefly why in **notes** (for example: hand partly out of frame, too fast, could be a
   lexical sign).

## Please

- Label only what you see in the clip. Don't look the video up, and don't discuss the clips with anyone until you
  have returned the file.
- Times are clip seconds from 0, as shown by the player.
- There is no expected number of fingerspelled clips. `no` is as useful an answer as `yes`.

## How to use the page

1. Open `review_blind.html` in Chrome, Edge, Firefox or Safari. It runs offline in the browser.
2. Use **Load clips** to select all files in the `clips/` folder.
3. Fill in your reviewer ID and ASL background at the top.
4. Your answers are saved in the browser as you type.
5. When done, press **Export** and send back the downloaded `blind_review.csv`.
6. To continue on another computer, use **Import** with a CSV you exported earlier.

You can also fill `blind_review.csv` directly in a spreadsheet: one row per span, with `span_no` 1, 2, ... for each
clip.
"""

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fingerspelling check · Step 1</title><style>
:root{--bg:#fff;--fg:#1d1d1f;--mut:#666;--line:#ddd;--acc:#0b57d0;--card:#fafafa}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--fg:#eee;--mut:#aaa;--line:#333;--acc:#8ab4f8;--card:#1c1c1c}}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;z-index:2}
main{max-width:980px;margin:0 auto;padding:12px 16px}.card{border:1px solid var(--line);background:var(--card);border-radius:8px;padding:12px;margin:14px 0}
video{width:100%;max-height:360px;background:#000;border-radius:6px}.row{display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin:6px 0}
label{display:inline-flex;flex-direction:column;font-size:12.5px;color:var(--mut)}label>*{color:var(--fg);font-size:14px}
textarea{width:100%;min-height:38px}.t{font-variant-numeric:tabular-nums;color:var(--mut)}button{cursor:pointer}
.span{border-top:1px dashed var(--line);padding-top:6px}.note{color:var(--mut);font-size:12.5px}
</style></head><body><header><b>Fingerspelling check · Step 1</b>
<div class="row"><label>Reviewer ID<input id="rid" type="text"></label><label>ASL background<input id="bg" type="text" size="28"></label>
<label>Load clips<input id="files" type="file" accept="video/mp4" multiple></label>
<button id="exp">Export __CSV__</button><label>Import CSV<input id="imp" type="file" accept=".csv"></label></div>
<div class="note">Answers are saved in this browser as you type. See reviewer_instructions.md.</div></header>
<main id="m"></main><script>
const D=__DATA__, KEY=D.key, urls={};
let S={};try{S=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){S={}}
const $=s=>document.querySelector(s), esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function save(){try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}}
S.__meta=S.__meta||{};
function meta(){$('#rid').value=S.__meta.reviewer_id||'';$('#bg').value=S.__meta.asl_background||''}
$('#rid').oninput=e=>{S.__meta.reviewer_id=e.target.value;save()};$('#bg').oninput=e=>{S.__meta.asl_background=e.target.value;save()};
function field(id,f){const v=S[id]??'';
 if(f.options)return `<label>${esc(f.label)}<select data-id="${id}"><option value=""></option>${f.options.map(o=>`<option ${o===v?'selected':''}>${o}</option>`).join('')}</select></label>`;
 if(f.time)return `<label>${esc(f.label)}<span><input type="text" size="6" data-id="${id}" value="${esc(v)}"> <button data-now="${id}">= now</button></span></label>`;
 if(f.area)return `<label style="flex:1 1 100%">${esc(f.label)}<textarea data-id="${id}">${esc(v)}</textarea></label>`;
 return `<label>${esc(f.label)}<input type="text" data-id="${id}" value="${esc(v)}" size="${f.size||14}"></label>`}
function nspans(b){return S['spans|'+b]||1}
function render(){$('#m').innerHTML=D.items.map(it=>{const b=it.blind_id;let sp='';
 for(let k=1;k<=nspans(b);k++)sp+=`<div class="row span"><b>span ${k}</b>${D.span_fields.map(f=>field(b+'|'+k+'|'+f.name,f)).join('')}</div>`;
 return `<div class="card" id="c-${b}"><div class="row"><b>${b}</b><span class="t">${esc(it.video_file)} · ${it.duration_s} s</span></div>
 <video id="v-${b}" controls preload="metadata" ${urls[it.video_file.split('/').pop()]?`src="${urls[it.video_file.split('/').pop()]}"`:''}></video>
 <div class="row"><span class="t" id="t-${b}">0.0 s</span>${[1,0.5,0.25].map(x=>`<button data-rate="${x}" data-v="${b}">${x}×</button>`).join('')}
 <button data-back="${b}">−2 s</button><button data-addspan="${b}">+ span</button>${nspans(b)>1?`<button data-delspan="${b}">− last span</button>`:''}</div>
 <div class="row">${D.item_fields.map(f=>field(b+'|0|'+f.name,f)).join('')}</div>${sp}</div>`}).join('');
 document.querySelectorAll('video').forEach(v=>v.ontimeupdate=()=>{$('#t-'+v.id.slice(2)).textContent=v.currentTime.toFixed(1)+' s'});}
document.addEventListener('input',e=>{const id=e.target.dataset.id;if(id){S[id]=e.target.value;save()}});
document.addEventListener('change',e=>{const id=e.target.dataset.id;if(id){S[id]=e.target.value;save()}});
document.addEventListener('click',e=>{const d=e.target.dataset;
 if(d.rate)document.getElementById('v-'+d.v).playbackRate=+d.rate;
 if(d.back){const v=document.getElementById('v-'+d.back);v.currentTime=Math.max(0,v.currentTime-2)}
 if(d.now){const b=d.now.split('|')[0],v=document.getElementById('v-'+b);S[d.now]=v.currentTime.toFixed(1);save();render()}
 if(d.addspan){S['spans|'+d.addspan]=nspans(d.addspan)+1;save();render()}
 if(d.delspan){const b=d.delspan,n=nspans(b);for(const f of D.span_fields)delete S[b+'|'+n+'|'+f.name];S['spans|'+b]=n-1;save();render()}});
$('#files').onchange=e=>{for(const f of e.target.files)urls[f.name]=URL.createObjectURL(f);render()};
const cell=v=>/[",\r\n]/.test(v=String(v??''))?'"'+v.replace(/"/g,'""')+'"':v;
function exportCSV(stamp){const L=[D.cols.join(',')],now=stamp||new Date().toISOString();
 for(const it of D.items){const b=it.blind_id;for(let k=1;k<=nspans(b);k++){const o={blind_id:b,video_file:it.video_file,span_no:k};
  for(const f of D.item_fields)o[f.name]=S[b+'|0|'+f.name]??'';for(const f of D.span_fields)o[f.name]=S[b+'|'+k+'|'+f.name]??'';
  o.reviewer_id=S.__meta.reviewer_id||'';o.asl_background=S.__meta.asl_background||'';o.labelled_at=now;
  L.push(D.cols.map(c=>cell(o[c])).join(','))}}return L.join('\r\n')+'\r\n'}
function parseCSV(t){const rows=[];let row=[],c='',q=false;
 for(let i=0;i<t.length;i++){const ch=t[i];if(q){if(ch=='"'&&t[i+1]=='"'){c+='"';i++}else if(ch=='"')q=false;else c+=ch}
  else if(ch=='"')q=true;else if(ch==','){row.push(c);c=''}else if(ch=='\n'){row.push(c.replace(/\r$/,''));rows.push(row);row=[];c=''}else c+=ch}
 if(c!==''||row.length){row.push(c);rows.push(row)}return rows}
function importCSV(t){const rows=parseCSV(t),h=rows.shift();const N={__meta:{}};
 for(const r of rows){if(r.length<h.length)continue;const o={};h.forEach((k,i)=>o[k]=r[i]);const b=o.blind_id,k=+o.span_no||1;
  if(!D.items.some(it=>it.blind_id===b))continue;N['spans|'+b]=Math.max(N['spans|'+b]||1,k);
  for(const f of D.item_fields)if(o[f.name])N[b+'|0|'+f.name]=o[f.name];for(const f of D.span_fields)if(o[f.name])N[b+'|'+k+'|'+f.name]=o[f.name];
  if(o.reviewer_id)N.__meta.reviewer_id=o.reviewer_id;if(o.asl_background)N.__meta.asl_background=o.asl_background}
 S=N;save();meta();render()}
window.stageA={exportCSV,importCSV,clear:()=>{S={__meta:{}};save();meta();render()}};
$('#exp').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([exportCSV()],{type:'text/csv'}));a.download=D.csv;a.click()};
$('#imp').onchange=async e=>{importCSV(await e.target.files[0].text())};
meta();render();
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--videos-dir", required=True, type=Path); a = ap.parse_args()
    cand = json.loads(CAND.read_text()); fields = json.loads(PREREG.read_text())["label_fields"]
    items = cand["items"]
    assert [i["blind_id"] for i in items] == [f"FSA-{k:03d}" for k in range(1, 37)]
    freeze = {l.split()[1]: l.split()[0] for l in open(BENCH / "FREEZE_CHECKSUMS.sha256") if l.strip()}
    if PKG.exists():
        shutil.rmtree(PKG)
    (SEND / "clips").mkdir(parents=True); INTERNAL.mkdir(parents=True)
    log, mapping, page_items = [], [], []
    for it in items:
        src = a.videos_dir / f"{it['clip_id']}.mp4"
        assert sha256(src) == freeze[f"videos/{it['clip_id']}.mp4"] == it["video_sha256"], it["blind_id"]
        dst = SEND / "clips" / f"{it['blind_id']}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-map", "0:v:0", "-c", "copy", "-an",
                        "-map_metadata", "-1", "-map_chapters", "-1", "-fflags", "+bitexact",
                        "-flags:v", "+bitexact", "-movflags", "+faststart", str(dst)], check=True)
        n_src = int(subprocess.check_output(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0",
                                             "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(src)]))
        probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-count_packets", "-show_entries",
                                                    "stream=codec_type,nb_read_packets,duration:format_tags",
                                                    "-of", "json", str(dst)]))
        streams = probe["streams"]; tags = probe.get("format", {}).get("tags", {})
        assert len(streams) == 1 and streams[0]["codec_type"] == "video" and int(streams[0]["nb_read_packets"]) == n_src
        dur = round(it["clip_window"]["end_s"], 3)
        page_items.append({"blind_id": it["blind_id"], "video_file": f"clips/{it['blind_id']}.mp4", "duration_s": dur})
        mapping.append({"blind_id": it["blind_id"], "clip_id": it["clip_id"], "source_video_id": it["source_video_id"],
                        "source_video_sha256": it["video_sha256"], "package_clip_sha256": sha256(dst),
                        "duration_s": dur, "n_frames": n_src, "selection_tier": it["selection_tier"]})
        log.append({"blind_id": it["blind_id"], "packets_src": n_src, "packets_dst": int(streams[0]["nb_read_packets"]),
                    "dst_streams": len(streams), "dst_format_tags": sorted(tags),
                    "decoded_frames": decoded_frames(dst)})
        assert log[-1]["decoded_frames"] == n_src, it["blind_id"]

    with open(SEND / CSV_NAME, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(fields)
        for p in page_items:
            w.writerow([p["blind_id"], p["video_file"], 1] + [""] * (len(fields) - 3))
    opt = lambda *o: list(o)
    data = {"key": STORAGE_KEY, "csv": CSV_NAME, "cols": fields, "items": page_items,
            "item_fields": [{"name": "fingerspelling_present", "label": "Is fingerspelling present?",
                             "options": opt("yes", "no", "uncertain")},
                            {"name": "multiple_spans_in_clip", "label": "More than one span?", "options": opt("yes", "no")},
                            {"name": "notes", "label": "Notes (if uncertain: why)", "area": True}],
            "span_fields": [{"name": "span_start_s", "label": "start (s)", "time": True},
                            {"name": "span_end_s", "label": "end (s)", "time": True},
                            {"name": "letters", "label": "letters (a–z, ? = unreadable)", "size": 18},
                            {"name": "letters_confidence", "label": "confidence", "options": opt("high", "medium", "low")},
                            {"name": "signing_hand", "label": "signing hand", "options": opt("left", "right", "both", "unclear")},
                            {"name": "visibility_issue", "label": "visibility",
                             "options": opt("none", "motion_blur", "out_of_frame", "low_resolution", "lighting", "other")},
                            {"name": "occlusion_issue", "label": "occlusion",
                             "options": opt("none", "other_hand", "body", "object", "other")}]}
    assert {f["name"] for f in data["item_fields"] + data["span_fields"]} | {"blind_id", "video_file", "span_no",
                                                                               "reviewer_id", "asl_background",
                                                                               "labelled_at"} == set(fields)
    (SEND / "review_blind.html").write_text(HTML.replace("__DATA__", json.dumps(data)).replace("__CSV__", CSV_NAME))
    (SEND / "reviewer_instructions.md").write_text(INSTRUCTIONS)
    sums = sorted(p for p in SEND.rglob("*") if p.is_file())
    (SEND / "SHA256SUMS").write_text("".join(f"{sha256(p)}  {p.relative_to(SEND).as_posix()}\n" for p in sums))
    for name in ("reviewer_instructions.md", CSV_NAME, "review_blind.html"):
        shutil.copyfile(SEND / name, HERE / name)

    with open(INTERNAL / "blind_mapping.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(mapping[0])); w.writeheader(); w.writerows(mapping)
    (INTERNAL / "build_log.json").write_text(json.dumps({"clips": log, "ffmpeg_remux": "stream copy of video stream "
                                                         "0 only, -an, -map_metadata -1, bitexact, +faststart"}, indent=1) + "\n")
    leak = leakage_scan(items)
    (INTERNAL / "leakage_check.json").write_text(json.dumps(leak, indent=1) + "\n")
    with zipfile.ZipFile(PKG / "send_step1_blind.zip", "w", zipfile.ZIP_STORED) as z:
        for p in sorted(SEND.rglob("*")):
            if p.is_file():
                z.write(p, f"send_step1_blind/{p.relative_to(SEND).as_posix()}")
    print(json.dumps({"items": len(page_items), "send_files": [p.relative_to(SEND).as_posix() for p in sums],
                      "leakage_check": leak["pass"]}, indent=1))
    assert leak["pass"], leak


def decoded_frames(p):
    """Full decode of the clip (proves it is playable end to end), counting decoded video frames."""
    return int(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                                        "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(p)]))


def leakage_scan(items):
    """Scan every reviewer-facing file for identifiers, tier words and reference-sentence fragments."""
    man = list(csv.DictReader(open(BENCH / "manifest.csv")))
    ids = {r["how2sign_id"] for r in man} | {r["source_video_id"] for r in man}
    ids |= {i.split("_")[0] for i in ids}
    ids = {i for i in ids if len(i) >= 8}                 # shorter fragments match by chance
    mine = {i["clip_id"] for i in items}
    refs = [json.loads(l)["reference"] for l in open(REFS) if json.loads(l)["clip_id"] in mine]
    grams = set()
    for r in refs:
        t = re.findall(r"[a-z']+", r.lower())
        grams |= {" ".join(t[k:k + 4]) for k in range(len(t) - 3)}
    hits = []
    for p in sorted(SEND.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix == ".mp4":
            tags = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format_tags:stream_tags",
                                                       "-of", "json", str(p)]))
            txt = json.dumps(tags).lower()
        else:
            txt = p.read_text().lower()
        for i in ids:
            if i.lower() in txt:
                hits.append([p.name, "identifier", i])
        for w in FORBIDDEN_WORDS:
            if re.search(r"\b" + re.escape(w) + r"\b", txt):
                hits.append([p.name, "forbidden_word", w])
        if p.suffix != ".mp4":
            words = re.findall(r"[a-z']+", txt)
            for k in range(len(words) - 3):
                g = " ".join(words[k:k + 4])
                if g in grams:
                    hits.append([p.name, "reference_4gram", g])
    return {"pass": not hits, "hits": hits[:50], "n_hits": len(hits), "identifiers_checked": len(ids),
            "reference_4grams_checked": len(grams), "forbidden_words": FORBIDDEN_WORDS}


if __name__ == "__main__":
    main()
