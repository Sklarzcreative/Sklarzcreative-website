#!/usr/bin/env python3
"""Cannabiology figure production pipeline.

Six agents, one command surface:

  queue                 Agent 1  Figure Tracker    ranked production queue
  status [--batch N]    Agent 1                    live state of every asset
  prompt  <ID>          Agent 2  Figure Prompt     final production prompt
  generate <ID>         Agent 3  Image Generation   draft (or dry-run payload)
  review  <ID>          Agent 4  OA Review          brief out / verdict in
  score   <ID> k=v..    Agent 4                     record scores -> verdict
  repair  <ID>          Agent 5  Repair             edit / regenerate / refine
  package --batch N     Agent 6  Packaging          Manny review packet
  run     --batch N                                 drive the whole loop

Client data lives in ../client-data and is never committed (public repo).
"""
import argparse, csv, glob, html, json, os, shutil, sys

import core
from adapters import imagegen, oareview


# ---------------------------------------------------------------- Agent 1 --
def cmd_queue(args):
    rows = core.build_queue()
    print(f"{'FIG ID':13} {'ROUTE':13} {'B':2} {'CH':10} TITLE")
    print("-" * 100)
    for r in rows:
        if args.route and r["_route"] != args.route:
            continue
        print(f"{r['Figure ID']:13} {r['_route']:13} {str(r['_batch']):2} "
              f"{r['Chapter']:10} {r['Figure Title'][:46]}")
    n = {}
    for r in rows:
        n[r["_route"]] = n.get(r["_route"], 0) + 1
    print("-" * 100)
    print("routes:", ", ".join(f"{k}={v}" for k, v in sorted(n.items())))
    print("\nOnly GENERATE-routed figures belong in this image pipeline.")
    print("VECTOR-BUILD -> Illustrator/Canva.  DATA-DRIVEN -> needs a verified"
          " dataset first.  HOLD -> blocked on an open author decision.")


def cmd_status(args):
    rows = {r["Figure ID"]: r for r in core.build_queue()}
    state = core.load_state()
    prompts = core.load_prompts()
    print(f"{'ASSET':14} {'STAGE':22} {'RND':3} {'LIGHT':7} TITLE")
    print("-" * 96)
    for aid, p in prompts.items():
        fig = rows.get(p["Figure ID"])
        if not fig or fig["_route"] != "GENERATE":
            continue
        if args.batch and fig["_batch"] != args.batch:
            continue
        s = state.get(aid, {})
        print(f"{aid:14} {s.get('stage','QUEUED'):22} {s.get('round',0):<3} "
              f"{s.get('stoplight','RED'):7} {p['Figure Title'][:40]}")


# ---------------------------------------------------------------- Agent 2 --
def assets_for(figure_id):
    prompts = core.load_prompts()
    return [a for a, r in prompts.items() if r["Figure ID"] == figure_id] or (
        [figure_id] if figure_id in prompts else [])


def build_prompt(prompt_row, repair_note=""):
    """Assemble the exact string sent to the generator.

    The tracker's Production Prompt is already production-grade; this appends the
    project-wide negative constraints and the manual-label reservation so no
    generator ever receives a prompt missing the book's hard rules.
    """
    parts = [prompt_row["Production Prompt"].strip()]
    labels = prompt_row.get("Manual Labels", "").strip()
    if labels:
        parts.append(
            "LAYOUT RESERVATION: leave clean, uncluttered callout space for these "
            "labels, which are applied manually after verification and must NOT be "
            f"typeset in the image: {labels}.")
    neg = prompt_row.get("Negative Constraints", "").strip()
    if neg:
        parts.append("AVOID: " + neg)
    if repair_note:
        parts.append("CORRECTION FOR THIS ROUND: " + repair_note.strip())
    return "\n\n".join(parts)


def cmd_prompt(args):
    prompts = core.load_prompts()
    for aid in assets_for(args.figure_id):
        row = prompts[aid]
        state = core.load_state()
        f = core.get_fig(state, aid)
        note = f["repairs"][-1]["prompt_note"] if f["repairs"] else ""
        text = build_prompt(row, note)
        core.set_stage(state, aid, "PROMPT_READY")
        core.save_state(state)
        print(f"\n{'='*78}\n{aid}  |  {row['Figure Title']}  |  "
              f"{row['Aspect Ratio']}\n{'='*78}\n{text}\n")


# ---------------------------------------------------------------- Agent 3 --
def cmd_generate(args):
    cfg, prompts = core.load_config(), core.load_prompts()
    state = core.load_state()
    os.makedirs(core.TESTS, exist_ok=True)
    for aid in assets_for(args.figure_id):
        row = prompts[aid]
        f = core.get_fig(state, aid)
        f["round"] += 1
        rnd = f["round"]
        note = f["repairs"][-1]["prompt_note"] if f["repairs"] else ""
        text = build_prompt(row, note)
        out = os.path.join(core.TESTS, f"{aid}_r{rnd}.png")
        try:
            status, detail = imagegen.generate(cfg, text, out, row["Aspect Ratio"])
        except imagegen.GenerationUnavailable as e:
            print(f"  {aid}: GENERATION UNAVAILABLE - {e}")
            core.log(aid, "generate", "unavailable", str(e))
            continue
        f["files"].append({"round": rnd, "path": out, "artifact": detail,
                           "status": status, "at": core.now(), "prompt": text})
        core.set_stage(state, aid,
                       "GENERATED_DRAFT" if rnd == 1 else "REGENERATED",
                       f"round {rnd} via {cfg['image_generation']['provider']}")
        core.save_state(state)
        print(f"  {aid} r{rnd}: {status} -> {detail}")


# ---------------------------------------------------------------- Agent 4 --
def cmd_review(args):
    cfg, rubric = core.load_config(), core.load_rubric()
    tracker = {r["Figure ID"]: r for r in core.load_tracker()}
    prompts, state = core.load_prompts(), core.load_state()
    for aid in assets_for(args.figure_id):
        row = prompts[aid]
        f = core.get_fig(state, aid)
        if not f["files"]:
            print(f"  {aid}: nothing generated yet"); continue
        img = f["files"][-1]["path"]
        try:
            status, result = oareview.review(
                cfg, rubric, tracker.get(row["Figure ID"], {}), row, img)
        except oareview.ReviewUnavailable as e:
            print(f"  {aid}: REVIEW UNAVAILABLE - {e}"); continue
        if status == "brief-emitted":
            print(f"  {aid}: review brief -> {result}")
            print("       Score it with:  cannabiology.py score "
                  f"{aid} scientific_plausibility=5 concept_fidelity=4 ...")
        else:
            _record(state, aid, result, rubric)
            print(f"  {aid}: {result['verdict']}")
        core.save_state(state)


def cmd_score(args):
    rubric, state = core.load_rubric(), core.load_state()
    scores = {}
    for kv in args.scores:
        k, v = kv.split("=")
        scores[k] = int(v)
    result = oareview.score_to_verdict(rubric, scores)
    result["scores"] = scores
    result["findings"] = []
    result["summary"] = args.summary or ""
    result["open_scientific_flag"] = args.flag
    _record(state, args.asset_id, result, rubric)
    core.save_state(state)
    f = state[args.asset_id]
    print(f"{args.asset_id}: {result['verdict']}  "
          f"score={result['weighted_score']}  light={f['stoplight']}  "
          f"stage={f['stage']}")
    if result["gates_unmet"]:
        print("  gates unmet:", ", ".join(result["gates_unmet"]))


def _record(state, aid, result, rubric):
    f = core.get_fig(state, aid)
    result["round"] = f["round"]
    result["at"] = core.now()
    f["reviews"].append(result)
    v = result["verdict"]
    stage = "OA_REVIEW_1" if f["round"] <= 1 else "OA_REVIEW_2"
    if v in ("PASS", "PASS_WITH_MINOR_NOTES"):
        f["stoplight"] = ("YELLOW" if (v == "PASS_WITH_MINOR_NOTES"
                                       or result.get("open_scientific_flag")) else "GREEN")
        core.set_stage(state, aid, "APPROVED_FOR_MANNY", v)
    else:
        f["stoplight"] = "RED"
        core.set_stage(state, aid, stage, v)
        core.set_stage(state, aid, "REVISION_NEEDED", v)
    core.log(aid, "review", v, str(result.get("weighted_score", "")))


# ---------------------------------------------------------------- Agent 5 --
def cmd_repair(args):
    rubric, state = core.load_rubric(), core.load_state()
    cap = rubric["cycle_cap"]
    for aid in assets_for(args.figure_id):
        f = core.get_fig(state, aid)
        if not f["reviews"]:
            print(f"  {aid}: no review to repair from"); continue
        r = f["reviews"][-1]
        v = r["verdict"]
        if v in ("PASS", "PASS_WITH_MINOR_NOTES"):
            print(f"  {aid}: {v} - nothing to repair"); continue
        if len(f["repairs"]) >= cap:
            core.set_stage(state, aid, "BLOCKED",
                           f"cycle cap {cap} reached after {v}; needs a human call")
            f["stoplight"] = "RED"
            core.save_state(state)
            print(f"  {aid}: CYCLE CAP REACHED -> escalated to human decision")
            continue

        blocking = [x for x in r.get("findings", [])
                    if x.get("severity") in ("blocking", "major")]
        if v == "REGENERATE":
            action = "regenerate-with-refined-prompt"
            note = ("Previous draft was structurally wrong. " +
                    " ".join(f"{x['criterion']}: {x['fix']}" for x in blocking))
        elif len(blocking) >= 3:
            action = "regenerate-with-refined-prompt"
            note = ("Too many blocking findings to edit. " +
                    " ".join(f"{x['criterion']}: {x['fix']}" for x in blocking))
        else:
            action = "targeted-edit"
            note = ("Preserve overall composition and style; change only: " +
                    " ".join(f"{x['criterion']}: {x['fix']}" for x in blocking))
        if not blocking:
            # A CLI/human review carries its correction in the summary rather than
            # as itemised findings - that text is the most useful repair signal.
            extra = r.get("summary", "").strip()
            note += (" " + extra) if extra else ""
            if r.get("gates_unmet"):
                note += (" Refine specifically against the unmet gates: "
                         + ", ".join(r["gates_unmet"]) + ".")
        f["repairs"].append({"at": core.now(), "after_round": f["round"],
                             "verdict": v, "action": action, "prompt_note": note})
        core.save_state(state)
        print(f"  {aid}: {action}\n       {note[:150]}")


# ---------------------------------------------------------------- Agent 6 --
def cmd_package(args):
    rows = {r["Figure ID"]: r for r in core.build_queue()}
    prompts, state = core.load_prompts(), core.load_state()
    os.makedirs(core.PACKETS, exist_ok=True)
    items = []
    for aid, p in prompts.items():
        fig = rows.get(p["Figure ID"])
        if not fig or fig["_route"] != "GENERATE" or fig["_batch"] != args.batch:
            continue
        s = state.get(aid, {})
        img = s.get("files", [{}])[-1].get("path", "") if s.get("files") else ""
        items.append({
            "asset_id": aid, "title": p["Figure Title"], "chapter": p["Chapter"],
            "purpose": rows[p["Figure ID"]].get("Educational Purpose", ""),
            "stage": s.get("stage", "QUEUED"), "light": s.get("stoplight", "RED"),
            "round": s.get("round", 0), "image": img,
            "verdict": (s.get("reviews") or [{}])[-1].get("verdict", "—"),
            "notes": (s.get("reviews") or [{}])[-1].get("summary", ""),
        })
    out = os.path.join(core.PACKETS, f"manny-review-packet-batch{args.batch}.html")
    with open(out, "w") as f:
        f.write(_packet_html(items, args.batch))
    with open(out.replace(".html", ".csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(items[0].keys()) if items else ["asset_id"])
        w.writeheader(); w.writerows(items)
    for it in items:
        if it["stage"] == "APPROVED_FOR_MANNY":
            core.set_stage(state, it["asset_id"], "PRESENTED_TO_MANNY",
                           f"batch {args.batch} packet")
    core.save_state(state)
    print(f"packet -> {out}  ({len(items)} assets)")


def _packet_html(items, batch):
    css = """body{font:15px/1.55 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    margin:0;padding:40px;background:#faf8f4;color:#1d2b1f}
    h1{font-size:26px;margin:0 0 4px}.sub{color:#5d6b5f;margin-bottom:28px}
    .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:22px}
    .card{background:#fff;border:1px solid #e2ded4;border-radius:10px;overflow:hidden}
    .thumb{aspect-ratio:4/3;background:#f0ece2;display:flex;align-items:center;
    justify-content:center;color:#8a9384;font-size:13px;text-align:center;padding:12px}
    .thumb img{width:100%;height:100%;object-fit:contain}
    .body{padding:14px 16px}.id{font:600 12px ui-monospace,monospace;color:#6d7a6f}
    .t{font-weight:650;margin:3px 0 6px}.p{font-size:13px;color:#4a574c;margin:0 0 10px}
    .pill{display:inline-block;font-size:11px;font-weight:700;padding:3px 9px;
    border-radius:99px;letter-spacing:.03em}
    .GREEN{background:#e3f2e5;color:#1f6b31}.YELLOW{background:#fdf3d8;color:#8a6a12}
    .RED{background:#fbe4e4;color:#95302f}
    .meta{font-size:12px;color:#6d7a6f;margin-top:8px}"""
    cards = []
    for it in items:
        thumb = (f'<img src="{html.escape(os.path.relpath(it["image"], core.PACKETS))}">'
                 if it["image"] and it["image"].endswith(".png")
                 and os.path.exists(it["image"])
                 else "not yet generated<br>(no image API configured)")
        cards.append(f"""<div class="card"><div class="thumb">{thumb}</div>
        <div class="body"><div class="id">{html.escape(it['asset_id'])} &middot;
        {html.escape(it['chapter'])}</div>
        <div class="t">{html.escape(it['title'])}</div>
        <p class="p">{html.escape(it['purpose'][:170])}</p>
        <span class="pill {it['light']}">{it['light']}</span>
        <div class="meta">Stage {html.escape(it['stage'])} &middot; round
        {it['round']} &middot; OA {html.escape(str(it['verdict']))}</div>
        </div></div>""")
    green = sum(1 for i in items if i["light"] == "GREEN")
    yellow = sum(1 for i in items if i["light"] == "YELLOW")
    red = len(items) - green - yellow
    return f"""<!doctype html><meta charset="utf-8"><title>Cannabiology - Manny
Review Packet - Batch {batch}</title><style>{css}</style>
<h1>Cannabiology &mdash; Manny Review Packet, Batch {batch}</h1>
<div class="sub">{len(items)} assets &middot; {green} green &middot; {yellow} yellow
&middot; {red} red &middot; generated {core.now()}</div>
<div class="grid">{''.join(cards)}</div>"""


# -------------------------------------------------------------------- run --
def cmd_run(args):
    rows = {r["Figure ID"]: r for r in core.build_queue()}
    prompts = core.load_prompts()
    figs = []
    for aid, p in prompts.items():
        fig = rows.get(p["Figure ID"])
        if fig and fig["_route"] == "GENERATE" and fig["_batch"] == args.batch:
            if p["Figure ID"] not in figs:
                figs.append(p["Figure ID"])
    print(f"Batch {args.batch}: {len(figs)} figures\n")
    for fid in figs:
        print(f"--- {fid} ---")
        cmd_generate(argparse.Namespace(figure_id=fid))
        cmd_review(argparse.Namespace(figure_id=fid))
    cmd_package(argparse.Namespace(batch=args.batch))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("queue"); q.add_argument("--route"); q.set_defaults(fn=cmd_queue)
    s = sub.add_parser("status"); s.add_argument("--batch", type=int); s.set_defaults(fn=cmd_status)
    for name, fn in (("prompt", cmd_prompt), ("generate", cmd_generate),
                     ("review", cmd_review), ("repair", cmd_repair)):
        p = sub.add_parser(name); p.add_argument("figure_id"); p.set_defaults(fn=fn)
    sc = sub.add_parser("score")
    sc.add_argument("asset_id"); sc.add_argument("scores", nargs="+")
    sc.add_argument("--summary", default=""); sc.add_argument("--flag", action="store_true")
    sc.set_defaults(fn=cmd_score)
    pk = sub.add_parser("package"); pk.add_argument("--batch", type=int, required=True)
    pk.set_defaults(fn=cmd_package)
    rn = sub.add_parser("run"); rn.add_argument("--batch", type=int, required=True)
    rn.set_defaults(fn=cmd_run)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
