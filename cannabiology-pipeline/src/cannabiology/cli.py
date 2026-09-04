"""Command-line interface."""
import argparse
import json
import sys

from . import (autopilot, canonical, config, doctor as doc, package,
               reconcile, routing, runner, state as st, vectorbuild, workspace)


def _load():
    figs = canonical.load_figures()
    dec = routing.Router().route_all(figs)
    return figs, dec


def _resolve(figures, ident):
    if ident in figures:
        return figures[ident]
    for f in figures.values():
        if any(a["asset_id"] == ident for a in f.assets):
            return f
    raise SystemExit(f"Unknown figure or asset: {ident}")


def cmd_doctor(a):
    rows = doc.run(init_workspace=a.init_workspace, check_network=a.network)
    width = max(len(r["check"]) for r in rows)
    bad = 0
    for r in rows:
        if r["status"] == doc.FAIL:
            bad += 1
        print(f"  [{r['status']:4}] {r['check']:<{width}}  {r['detail']}")
    print(f"\n{len(rows)} checks, {bad} failing")
    return 1 if bad else 0


def cmd_audit(a):
    figs, dec = _load()
    texts = []
    try:
        for p in (workspace.resolve() / "canonical" / "manuscript_sources").glob("*.md"):
            texts.append(p.read_text())
    except Exception:
        pass
    rep = reconcile.audit(figs, dec, manuscript_texts=texts)
    print(f"Canonical reconciliation  ({'OK' if rep['ok'] else 'FAILED'})\n")
    print(f"{'Route':<14}{'Figures':>9}{'Assets':>9}")
    print("-" * 32)
    for route in routing.Router().rules["strictness"]:
        if route in rep["by_route"]:
            print(f"{route:<14}{rep['by_route'][route]:>9}"
                  f"{rep['assets_by_route'][route]:>9}")
    print("-" * 32)
    print(f"{'TOTAL':<14}{rep['figures']:>9}{rep['assets']:>9}")
    print(f"{'expected':<14}{rep['expected_figures']:>9}{rep['expected_assets']:>9}\n")
    if rep["needs_route_confirmation"]:
        print(f"Derived routes needing human confirmation "
              f"({len(rep['needs_route_confirmation'])}):")
        print("  " + ", ".join(rep["needs_route_confirmation"]) + "\n")
    for key, label in (("duplicate_figure_ids", "Duplicate figure IDs"),
                       ("duplicate_asset_ids", "Duplicate asset IDs"),
                       ("approved_without_artifact", "Marked approved but no artifact"),
                       ("referenced_in_manuscript_not_in_tracker",
                        "In manuscript, absent from tracker")):
        if rep[key]:
            print(f"{label}: {', '.join(rep[key])}")
    if rep["problems"]:
        print("\nPROBLEMS:\n  - " + "\n  - ".join(rep["problems"]))
        return 1
    return 0


def cmd_route(a):
    figs, dec = _load()
    targets = [a.figure_id] if a.figure_id else sorted(figs)
    for fid in targets:
        f = _resolve(figs, fid)
        d = dec[f.figure_id]
        flag = "  [NEEDS CONFIRMATION]" if d.needs_route_confirmation else ""
        print(f"{d.figure_id}  {d.route}  ({d.confidence}){flag}")
        for r in d.reasons:
            print(f"    - {r}")
    return 0


def cmd_status(a):
    figs, dec = _load()
    store = st.Store()
    rows = store.all()
    if a.figure_id:
        f = _resolve(figs, a.figure_id)
        for asset in f.assets:
            rec = rows.get(asset["asset_id"])
            print(json.dumps(rec, indent=2) if rec
                  else f"{asset['asset_id']}: no pipeline state")
        return 0
    if not rows:
        print("No pipeline state yet. Run:  python -m cannabiology run <FIGURE_ID> --dry-run")
        return 0
    print(f"{'ASSET':<14}{'ROUTE':<14}{'STATE':<32}{'REP':>4}{'VEC':>4}")
    print("-" * 68)
    for aid, rec in sorted(rows.items()):
        print(f"{aid:<14}{str(rec.get('route')):<14}{rec['state']:<32}"
              f"{rec.get('generative_repairs', 0):>4}{rec.get('vector_edits', 0):>4}")
    return 0


def cmd_run(a):
    figs, dec = _load()
    fig = _resolve(figs, a.figure_id)
    store = st.Store()
    cfg = config.load()
    if a.model:
        cfg["models"]["image_generate"] = a.model
    rc = 0
    for asset in fig.assets:
        if a.asset and asset["asset_id"] != a.asset:
            continue
        print(f"\n{asset['asset_id']}  {fig.title}")
        try:
            with st.figure_lock(asset["asset_id"]):
                runner.run_asset(
                    fig, asset, dec[fig.figure_id], store, cfg=cfg,
                    dry_run=a.dry_run, no_network=a.no_network,
                    confirm_route=a.confirm_route,
                    max_iterations=a.max_iterations,
                    candidate_count=a.candidate_count)
        except runner.RouteBlocked as e:
            print(f"  ROUTE BLOCKED: {e}")
            rc = 2
        except st.LockError as e:
            print(f"  {e}")
            rc = 2
        finally:
            store.save()
    return rc


def cmd_batch(a):
    figs, dec = _load()
    store = st.Store()
    cfg = config.load()
    targets = [f for fid, f in sorted(figs.items()) if dec[fid].route == a.route]
    if a.limit:
        targets = targets[:a.limit]
    print(f"{len(targets)} figure(s) routed {a.route}\n")
    for fig in targets:
        for asset in fig.assets:
            print(f"\n{asset['asset_id']}  {fig.title}")
            try:
                with st.figure_lock(asset["asset_id"]):
                    runner.run_asset(fig, asset, dec[fig.figure_id], store, cfg=cfg,
                                     dry_run=a.dry_run, no_network=a.no_network,
                                     confirm_route=a.confirm_route)
            except (runner.RouteBlocked, st.LockError) as e:
                print(f"  SKIPPED: {str(e).splitlines()[0]}")
            finally:
                store.save()
    return 0


def cmd_build(a):
    """Deterministic build for VECTOR_BUILD figures. Never calls an image model."""
    figs, dec = _load()
    fig = _resolve(figs, a.figure_id)
    store = st.Store()
    rc = 0
    for asset in fig.assets:
        print(f"\n{asset['asset_id']}  {fig.title}")
        try:
            with st.figure_lock(asset["asset_id"]):
                vectorbuild.run_asset(fig, asset, dec[fig.figure_id], store,
                                      rebuild=a.rebuild)
        except (vectorbuild.BuildSpecMissing,) as e:
            print(f"  SPEC REQUIRED: {e}")
            rc = 2
        except Exception as e:
            print(f"  BUILD FAILED: {type(e).__name__}: {e}")
            rc = 2
        finally:
            store.save()
    return rc


def cmd_preview_diagram(a):
    """Render a diagram spec for review, confirmed or not. Never approves it."""
    from .builders import diagram
    from . import workspace
    path = workspace.resolve() / "canonical" / "diagram_specs" / f"{a.figure_id}.yaml"
    spec = diagram.load_spec(path, allow_unconfirmed=True)
    svg = diagram.build(spec, int(a.width), int(a.height), draft=True)
    out = workspace.resolve() / "runs" / "_previews" / f"{a.figure_id}_preview.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg)
    status = "CONFIRMED" if spec.get("confirmed") else "NOT CONFIRMED"
    print(f"preview: {out}\n  spec is {status} - {len(spec['nodes'])} nodes, "
          f"{len(spec.get('edges', []))} edges\n  source: {spec['source']}")
    return 0


def cmd_fetch_chem(a):
    """Fetch a structure from PubChem into the verified registry (needs network)."""
    import json as _json
    import urllib.request
    import urllib.error
    import yaml as _yaml
    from datetime import date

    url = (f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{a.cid}"
           f"/property/CanonicalSMILES,MolecularFormula,IUPACName/JSON")
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = _json.loads(r.read().decode())
    except Exception as e:
        print(f"Could not reach PubChem: {type(e).__name__}: {e}\n"
              "Run this in an environment with outbound access to "
              "pubchem.ncbi.nlm.nih.gov, or add the entry by hand.")
        return 2
    props = data["PropertyTable"]["Properties"][0]
    path = vectorbuild.chem_registry_path()
    reg = _yaml.safe_load(path.read_text()) if path.exists() else {"compounds": {}}
    reg.setdefault("compounds", {})[a.name] = {
        "display_name": a.display_name or a.name,
        "smiles": props.get("CanonicalSMILES") or props.get("SMILES"),
        "molecular_formula": props["MolecularFormula"],
        "iupac_name": props.get("IUPACName", ""),
        "source": "PubChem",
        "source_id": f"CID {a.cid}",
        "retrieved": date.today().isoformat(),
        "verified": False,
        "verified_by": "",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_yaml.safe_dump(reg, sort_keys=True))
    print(f"Added '{a.name}' ({props['MolecularFormula']}, CID {a.cid}) to {path}\n"
          "It will NOT render until a human checks it against the source and sets "
          "verified: true.")
    return 0


def cmd_package(a):
    figs, dec = _load()
    store = st.Store()
    only = [a.figure_id] if a.figure_id else None
    items = package.collect(figs, dec, store, only=only)
    if not items:
        print("Nothing to package.")
        return 0
    h, j = package.write(items, a.batch)
    print(f"packet: {h}\n        {j}\n{len(items)} asset(s)")
    return 0


def cmd_autopilot(a):
    """Run every runnable figure unattended. Stops at PENDING_HUMAN_APPROVAL."""
    figs, dec = _load()
    store, cfg = st.Store(), config.load()
    print(f"Autopilot over {len(figs)} figures "
          f"({'dry-run' if a.dry_run else 'live'})\n")
    results = autopilot.run_all(figs, dec, store, cfg=cfg, dry_run=a.dry_run,
                                no_network=a.no_network,
                                confirm_route=a.confirm_route, limit=a.limit)
    done = [r for r in results if r["outcome"] == autopilot.COMPLETED]
    failed = [r for r in results if r["outcome"] == autopilot.FAILED]
    skipped = [r for r in results if r["outcome"] == autopilot.SKIPPED]
    print(f"\n{len(done)} completed, {len(failed)} failed, {len(skipped)} skipped")
    if failed:
        print("\nFAILED:")
        for r in failed:
            print(f"  {r['figure_id']:14} {r['detail']}")
    if skipped:
        print("\nSKIPPED (nothing automation can do yet):")
        by_reason = {}
        for r in skipped:
            by_reason.setdefault(r["detail"], []).append(r["figure_id"])
        for reason, ids in sorted(by_reason.items()):
            print(f"  {reason}: {len(ids)}")
            print(f"      {', '.join(ids)}")
    clear, flagged = autopilot.approvable(store)
    print(f"\nAwaiting your approval: {len(clear)} clear, {len(flagged)} flagged")
    if clear or flagged:
        print("  Review them together:  python3 -m cannabiology package --batch auto")
        print("  Then approve in one go: python3 -m cannabiology approve --all")
    return 1 if failed else 0


def cmd_approve(a):
    store = st.Store()
    if not a.all and not a.asset_id:
        print("Name an asset, or use --all to approve every clear figure at once.")
        return 1

    if a.asset_id and not a.all:
        rec = store.get(a.asset_id)
        if rec["state"] != st.PENDING_HUMAN_APPROVAL:
            print(f"{a.asset_id} is {rec['state']}, not {st.PENDING_HUMAN_APPROVAL}. "
                  "Only a figure awaiting approval can be approved.")
            return 1
        reasons = autopilot.flag_reasons(rec)
        if reasons and not a.include_flagged:
            print(f"{a.asset_id} is flagged:")
            for r in reasons:
                print(f"  - {r}")
            print("Approve anyway with --include-flagged.")
            return 1
        autopilot.approve_many(store, [a.asset_id], a.by)
        print(f"{a.asset_id}: HUMAN_APPROVED")
        return 0

    exclude = set((a.exclude or "").split(",")) - {""}
    clear, flagged = autopilot.approvable(store, exclude=exclude)
    targets = clear + (flagged if a.include_flagged else [])
    if flagged and not a.include_flagged:
        print(f"HELD BACK - {len(flagged)} figure(s) the reviewer flagged:")
        for aid in flagged:
            print(f"  {aid}")
            for r in autopilot.flag_reasons(store.get(aid)):
                print(f"      - {r}")
        print("  Approve these deliberately, or add --include-flagged.\n")
    if not targets:
        print("Nothing clear to approve.")
        return 0
    print(f"About to approve {len(targets)} figure(s) as {a.by}:")
    for aid in targets:
        print(f"  {aid}")
    if not a.yes:
        print("\nRe-run with --yes to record these approvals.")
        return 0
    autopilot.approve_many(store, targets, a.by)
    print(f"\n{len(targets)} figure(s): HUMAN_APPROVED")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="cannabiology",
                                description="Cannabiology figure production pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("doctor", help="environment, privacy and integrity checks")
    d.add_argument("--init-workspace", action="store_true")
    d.add_argument("--network", action="store_true", help="probe API reachability")
    d.set_defaults(fn=cmd_doctor)

    a_ = sub.add_parser("audit", help="canonical count reconciliation")
    a_.set_defaults(fn=cmd_audit)

    r = sub.add_parser("route", help="show the production route and why")
    r.add_argument("figure_id", nargs="?")
    r.set_defaults(fn=cmd_route)

    s = sub.add_parser("status", help="pipeline state")
    s.add_argument("figure_id", nargs="?")
    s.set_defaults(fn=cmd_status)

    def gen_flags(x):
        x.add_argument("--dry-run", action="store_true")
        x.add_argument("--no-network", action="store_true")
        x.add_argument("--confirm-route", action="store_true",
                       help="confirm a DERIVED route before generating")
        x.add_argument("--force", action="store_true",
                       help="never bypasses HOLD, DATA_DRIVEN or privacy guards")

    ru = sub.add_parser("run", help="run one figure through the pipeline")
    ru.add_argument("figure_id"); ru.add_argument("--asset")
    ru.add_argument("--max-iterations", type=int); ru.add_argument("--candidate-count", type=int)
    ru.add_argument("--model")
    gen_flags(ru); ru.set_defaults(fn=cmd_run)

    b = sub.add_parser("batch", help="run every figure on one route")
    b.add_argument("--route", required=True); b.add_argument("--limit", type=int)
    gen_flags(b); b.set_defaults(fn=cmd_batch)

    bd = sub.add_parser("build", help="deterministic build (VECTOR_BUILD route)")
    bd.add_argument("figure_id")
    bd.add_argument("--rebuild", action="store_true",
                    help="re-run a figure already awaiting approval; refuses approved ones")
    bd.set_defaults(fn=cmd_build)

    pv = sub.add_parser("preview-diagram", help="render a spec for review (draft banner)")
    pv.add_argument("figure_id"); pv.add_argument("--width", default=1400)
    pv.add_argument("--height", default=800); pv.set_defaults(fn=cmd_preview_diagram)

    fc = sub.add_parser("fetch-chem", help="add a structure from PubChem to the registry")
    fc.add_argument("name"); fc.add_argument("--cid", required=True)
    fc.add_argument("--display-name", default="")
    fc.set_defaults(fn=cmd_fetch_chem)

    pk = sub.add_parser("package", help="build the human review packet")
    pk.add_argument("figure_id", nargs="?"); pk.add_argument("--batch", default="001")
    pk.set_defaults(fn=cmd_package)

    at = sub.add_parser("autopilot",
                        help="run every runnable figure unattended, stopping at approval")
    gen_flags(at); at.add_argument("--limit", type=int)
    at.set_defaults(fn=cmd_autopilot)

    ap = sub.add_parser("approve", help="record explicit human approval")
    ap.add_argument("asset_id", nargs="?")
    ap.add_argument("--all", action="store_true", help="approve every clear figure")
    ap.add_argument("--yes", action="store_true", help="actually record the approvals")
    ap.add_argument("--include-flagged", action="store_true",
                    help="also approve figures the reviewer flagged")
    ap.add_argument("--exclude", help="comma-separated asset IDs to hold back")
    ap.add_argument("--by", default="Cassandra Sklarz")
    ap.set_defaults(fn=cmd_approve)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except workspace.WorkspaceError as e:
        print(f"PRIVACY GUARD: {e}", file=sys.stderr)
        return 3
    except (canonical.CanonicalError, reconcile.ReconciliationError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 4
