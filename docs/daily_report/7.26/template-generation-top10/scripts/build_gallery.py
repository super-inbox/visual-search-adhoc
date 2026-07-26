#!/usr/bin/env python3
"""
build_gallery.py

Builds a single self-contained, offline-openable gallery.html from
template_manifest.json + example_manifest.json. Read-only against the
generated assets; writes only gallery.html.
"""
import json, os, html

OUT_ROOT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.26/template-generation-top10"

def esc(s):
    return html.escape(str(s), quote=True)

def main():
    tm = json.load(open(os.path.join(OUT_ROOT, "template_manifest.json")))
    em = json.load(open(os.path.join(OUT_ROOT, "example_manifest.json")))

    examples_by_tpl = {}
    for ex in em["examples"]:
        examples_by_tpl.setdefault(ex["template_id"], []).append(ex)
    for k in examples_by_tpl:
        examples_by_tpl[k].sort(key=lambda e: e["example_index"])

    total_planned = len(em["examples"])
    total_success = sum(1 for e in em["examples"] if e["status"] == "success")
    total_needs_review = sum(1 for e in em["examples"] if e["status"] == "needs_review")
    total_failed = sum(1 for e in em["examples"] if e["status"] == "failed")

    parts = []
    parts.append(f"""<title>Curify Top 10 Template Generation — Gallery</title>
<style>
  :root {{
    --bg: #fafafa; --fg: #1a1a1a; --card-bg: #ffffff; --border: #e2e2e2;
    --accent: #3457d5; --muted: #6b6b6b; --pass: #1e8e3e; --review: #b8860b; --fail: #c62828;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #121212; --fg: #ececec; --card-bg: #1c1c1c; --border: #333; --muted: #9a9a9a; }}
  }}
  :root[data-theme="dark"] {{ --bg: #121212; --fg: #ececec; --card-bg: #1c1c1c; --border: #333; --muted: #9a9a9a; }}
  :root[data-theme="light"] {{ --bg: #fafafa; --fg: #1a1a1a; --card-bg: #ffffff; --border: #e2e2e2; --muted: #6b6b6b; }}
  * {{ box-sizing: border-box; }}
  body {{
    background: var(--bg); color: var(--fg); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    margin: 0; padding: 0 0 4rem 0;
  }}
  header {{
    padding: 2rem 1.5rem 1rem; max-width: 1200px; margin: 0 auto;
  }}
  h1 {{ font-size: 1.6rem; margin: 0 0 .3rem; }}
  .subtitle {{ color: var(--muted); font-size: .95rem; margin-bottom: 1.2rem; }}
  .stats {{ display: flex; gap: .75rem; flex-wrap: wrap; margin-bottom: .5rem; }}
  .stat {{
    background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px;
    padding: .7rem 1rem; min-width: 110px; text-align: center;
  }}
  .stat .n {{ font-size: 1.4rem; font-weight: 700; }}
  .stat .l {{ font-size: .72rem; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }}
  .stat.pass .n {{ color: var(--pass); }}
  .stat.review .n {{ color: var(--review); }}
  .stat.fail .n {{ color: var(--fail); }}
  main {{ max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }}
  section.template {{
    border: 1px solid var(--border); border-radius: 14px; background: var(--card-bg);
    margin: 1.5rem 0; padding: 1.3rem 1.4rem 1.5rem; scroll-margin-top: 1rem;
  }}
  .tpl-head {{ display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: .5rem; }}
  .tpl-head h2 {{ margin: 0; font-size: 1.2rem; }}
  .tpl-rank {{ color: var(--accent); font-weight: 700; margin-right: .4rem; }}
  .tpl-meta {{ color: var(--muted); font-size: .85rem; margin: .3rem 0 .2rem; }}
  .tpl-purpose {{ font-size: .92rem; margin: .5rem 0; }}
  .tpl-rationale {{ font-size: .82rem; color: var(--muted); border-left: 3px solid var(--border); padding-left: .7rem; margin: .6rem 0 1rem; }}
  .tpl-links a {{ font-size: .8rem; margin-right: 1rem; color: var(--accent); text-decoration: none; }}
  .tpl-links a:hover {{ text-decoration: underline; }}
  .examples {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin-top: 1rem; }}
  .example {{ border: 1px solid var(--border); border-radius: 10px; overflow: hidden; background: var(--bg); }}
  .example img {{ width: 100%; display: block; aspect-ratio: 4/5; object-fit: cover; cursor: zoom-in; background: #eee; }}
  .example .body {{ padding: .6rem .7rem .7rem; }}
  .example .scenario {{ font-size: .78rem; margin: 0 0 .4rem; }}
  .badge {{ display: inline-block; font-size: .68rem; font-weight: 700; padding: .15rem .5rem; border-radius: 999px; text-transform: uppercase; letter-spacing: .03em; }}
  .badge.success {{ background: rgba(30,142,62,.15); color: var(--pass); }}
  .badge.needs_review {{ background: rgba(184,134,11,.15); color: var(--review); }}
  .badge.failed {{ background: rgba(198,40,40,.15); color: var(--fail); }}
  .example .links {{ margin-top: .4rem; }}
  .example .links a {{ font-size: .72rem; color: var(--accent); text-decoration: none; margin-right: .6rem; }}
  .example .links a:hover {{ text-decoration: underline; }}
  #lightbox {{
    display: none; position: fixed; inset: 0; background: rgba(0,0,0,.85); z-index: 999;
    align-items: center; justify-content: center; padding: 2rem; cursor: zoom-out;
  }}
  #lightbox.open {{ display: flex; }}
  #lightbox img {{ max-width: 100%; max-height: 100%; border-radius: 6px; }}
  nav.toc {{ max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; font-size: .82rem; color: var(--muted); }}
  nav.toc a {{ color: var(--accent); text-decoration: none; margin-right: .8rem; display: inline-block; margin-bottom: .3rem; }}
  nav.toc a:hover {{ text-decoration: underline; }}
</style>
""")

    parts.append("<header>")
    parts.append("<h1>Curify Top 10 Template Generation — Gallery</h1>")
    parts.append(f'<div class="subtitle">Discovery source: <code>{esc(tm["discovery_source"])}</code> &middot; generated {esc(tm["generated_at"])}</div>')
    parts.append('<div class="stats">')
    parts.append(f'<div class="stat"><div class="n">{len(tm["templates"])}</div><div class="l">Templates</div></div>')
    parts.append(f'<div class="stat"><div class="n">{total_planned}</div><div class="l">Planned examples</div></div>')
    parts.append(f'<div class="stat pass"><div class="n">{total_success}</div><div class="l">Successful</div></div>')
    parts.append(f'<div class="stat review"><div class="n">{total_needs_review}</div><div class="l">Needs review</div></div>')
    parts.append(f'<div class="stat fail"><div class="n">{total_failed}</div><div class="l">Failed</div></div>')
    parts.append('</div></header>')

    parts.append('<nav class="toc">')
    for t in tm["templates"]:
        parts.append(f'<a href="#{esc(t["dir"])}">#{t["order"]} {esc(t["template_id"])} {esc(t["template_name"])}</a>')
    parts.append('</nav>')

    parts.append("<main>")
    for t in tm["templates"]:
        tid = t["template_id"]
        exs = examples_by_tpl.get(tid, [])
        parts.append(f'<section class="template" id="{esc(t["dir"])}">')
        parts.append('<div class="tpl-head">')
        parts.append(f'<h2><span class="tpl-rank">#{t["order"]}</span>{esc(t["template_name"])} <span style="color:var(--muted);font-weight:400;font-size:.85rem;">({esc(tid)} &middot; {esc(t["zh_name"])})</span></h2>')
        parts.append('</div>')
        parts.append(f'<div class="tpl-meta">{esc(t["category"])} &middot; target user: {esc(t["target_user"])}</div>')
        parts.append(f'<div class="tpl-purpose"><strong>Purpose:</strong> {esc(t["purpose"])}</div>')
        parts.append(f'<div class="tpl-rationale"><strong>Discovery rationale:</strong> {esc(t["discovery_reason"])}<br><strong>Content gap:</strong> {esc(t["content_gap"])}</div>')
        parts.append('<div class="tpl-links">')
        parts.append(f'<a href="templates/{esc(t["dir"])}/TEMPLATE_SPEC.md">Template spec</a>')
        parts.append(f'<a href="templates/{esc(t["dir"])}/template.json">template.json</a>')
        parts.append('</div>')

        parts.append('<div class="examples">')
        for ex in exs:
            edir = ex["example_dir"]
            status = ex["status"]
            img_rel = f'{edir}/output.png'
            img_abs_exists = os.path.exists(os.path.join(OUT_ROOT, edir, "output.png"))
            parts.append('<div class="example">')
            if img_abs_exists:
                parts.append(f'<img src="{esc(img_rel)}" loading="lazy" alt="{esc(ex["example_id"])}" onclick="openLightbox(this.src)">')
            else:
                parts.append('<div style="aspect-ratio:4/5;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:.8rem;">no output</div>')
            parts.append('<div class="body">')
            parts.append(f'<span class="badge {esc(status)}">{esc(status.replace("_"," "))}</span>')
            parts.append(f'<p class="scenario">{esc(ex["scenario"])}</p>')
            parts.append('<div class="links">')
            parts.append(f'<a href="{esc(edir)}/input.json">input</a>')
            parts.append(f'<a href="{esc(edir)}/prompt.txt">prompt</a>')
            parts.append(f'<a href="{esc(edir)}/metadata.json">metadata</a>')
            parts.append('</div></div></div>')
        parts.append('</div>')
        parts.append('</section>')
    parts.append("</main>")

    parts.append("""
<div id="lightbox" onclick="this.classList.remove('open')"><img id="lightbox-img" src=""></div>
<script>
function openLightbox(src) {
  document.getElementById('lightbox-img').src = src;
  document.getElementById('lightbox').classList.add('open');
}
</script>
""")

    with open(os.path.join(OUT_ROOT, "gallery.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("wrote gallery.html")

if __name__ == "__main__":
    main()
