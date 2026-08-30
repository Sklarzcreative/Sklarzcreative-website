"""Human review package.

Client-facing. Shows the figure and what it needs - never prompts, OA chain,
internal repair logs or API data.
"""
import html
import json
import time
from pathlib import Path

from . import state as st, workspace


def _now():
    return time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())


def collect(figures, decisions, store, only=None):
    items = []
    for aid, rec in sorted(store.all().items()):
        fid = aid.rstrip("AB") if aid not in figures else aid
        fig = figures.get(fid) or figures.get(aid)
        if not fig:
            continue
        if only and fid not in only and aid not in only:
            continue
        last = rec["reviews"][-1] if rec["reviews"] else {}
        items.append({
            "asset_id": aid, "figure_id": fig.figure_id, "title": fig.title,
            "chapter": fig.chapter, "section": fig.manuscript_section,
            "purpose": fig.purpose, "route": rec.get("route"),
            "state": rec["state"],
            "composite": (rec.get("vector") or {}).get("composite", ""),
            "labels_remaining": (rec.get("vector") or {}).get("label_count", 0),
            "verdict": last.get("verdict", "-"),
            "synthetic_review": bool(last.get("synthetic")),
            "generative_repairs": rec.get("generative_repairs", 0),
            "vector_edits": rec.get("vector_edits", 0),
            "prompt_version": (rec["prompt_versions"][-1]["version"]
                               if rec["prompt_versions"] else None),
        })
    return items


def write(items, batch_name="001"):
    out_dir = workspace.assert_safe_write(workspace.resolve() / "runs" / "_packages")
    out_dir.mkdir(parents=True, exist_ok=True)
    hpath = out_dir / f"review-packet-{batch_name}.html"
    jpath = out_dir / f"review-packet-{batch_name}.json"
    hpath.write_text(_html(items, batch_name))
    jpath.write_text(json.dumps(items, indent=2))
    return hpath, jpath


def _html(items, batch):
    css = """body{font:15px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
margin:0;padding:40px;background:#f7f8f5;color:#14201a}
h1{font:600 26px/1.2 Georgia,serif;margin:0 0 4px}
.sub{color:#68746b;margin-bottom:28px;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px}
.card{background:#fff;border:1px solid #dde2d8;border-radius:4px;overflow:hidden}
.thumb{aspect-ratio:3/2;background:#f1f3ed;display:flex;align-items:center;
justify-content:center;color:#8b968c;font-size:13px;padding:12px;text-align:center}
.thumb img,.thumb object{width:100%;height:100%;object-fit:contain}
.b{padding:14px 16px}
.id{font:600 12px ui-monospace,monospace;color:#68746b}
.t{font-weight:650;margin:3px 0 6px}.p{font-size:13.5px;color:#3d4a41;margin:0 0 10px}
.pill{display:inline-block;font:700 10.5px ui-monospace,monospace;padding:4px 8px;
border-radius:2px;letter-spacing:.05em;margin-right:6px}
.ok{background:#e6f0e6;color:#2f6b41}.wait{background:#f6eed6;color:#8a6210}
.stop{background:#f7e4e2;color:#9b2f2c}
.meta{font-size:12px;color:#68746b;margin-top:8px}
.warn{background:#f7e4e2;border:1px solid #9b2f2c;border-radius:4px;padding:14px 18px;
margin-bottom:24px;font-size:14px}"""
    cards = []
    for it in items:
        light = ("ok" if it["state"] == st.PENDING_HUMAN_APPROVAL
                 else "wait" if it["state"] in (st.PRODUCTION_READY_BASE_ART,
                                                st.SCIENTIFIC_VERIFICATION_REQUIRED)
                 else "stop")
        comp = Path(it["composite"]) if it["composite"] else None
        thumb = (f'<object type="image/svg+xml" data="{html.escape(comp.name)}"></object>'
                 if comp and comp.exists() else "no composite yet")
        cards.append(f"""<div class="card"><div class="thumb">{thumb}</div><div class="b">
<div class="id">{html.escape(it['asset_id'])} &middot; {html.escape(it['chapter'])}</div>
<div class="t">{html.escape(it['title'])}</div>
<p class="p">{html.escape(it['purpose'][:180])}</p>
<span class="pill {light}">{html.escape(it['state'].replace('_',' '))}</span>
<span class="pill wait">{html.escape(str(it['route']))}</span>
<div class="meta">{it['labels_remaining']} labels applied as vector overlay &middot;
{it['generative_repairs']} generative repair(s) &middot; {it['vector_edits']} vector edit(s)</div>
</div></div>""")
    synth = any(i["synthetic_review"] for i in items)
    warn = ('<div class="warn"><strong>Dry run.</strong> These entries were produced '
            'without an image-generation or OA API call. Reviews shown are synthetic '
            'plumbing results, not real scientific review, and no artwork exists yet.'
            '</div>') if synth else ""
    return f"""<!doctype html><meta charset="utf-8">
<title>Cannabiology review packet {html.escape(batch)}</title><style>{css}</style>
<h1>Cannabiology &mdash; review packet {html.escape(batch)}</h1>
<div class="sub">{len(items)} asset(s) &middot; {_now()} &middot; nothing here is
approved until you approve it</div>{warn}<div class="grid">{''.join(cards)}</div>"""
