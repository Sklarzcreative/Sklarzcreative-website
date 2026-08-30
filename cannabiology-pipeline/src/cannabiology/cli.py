"""Command-line interface."""
import argparse
import json
import sys

from . import (canonical, config, doctor as doc, package, reconcile, routing,
               runner, state as st, workspace)


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


def cmd_approve(a):
    store = st.Store()
    rec = store.get(a.asset_id)
    if rec["state"] != st.PENDING_HUMAN_APPROVAL:
        print(f"{a.asset_id} is {rec['state']}, not {st.PENDING_HUMAN_APPROVAL}. "
              "Only a figure awaiting approval can be approved.")
        return 1
    store.transition(a.asset_id, st.HUMAN_APPROVED, f"approved by {a.by}")
    rec["human_approved"] = True
    store.save()
    print(f"{a.asset_id}: HUMAN_APPROVED")
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

    pk = sub.add_parser("package", help="build the human review packet")
    pk.add_argument("figure_id", nargs="?"); pk.add_argument("--batch", default="001")
    pk.set_defaults(fn=cmd_package)

    ap = sub.add_parser("approve", help="record explicit human approval")
    ap.add_argument("asset_id"); ap.add_argument("--by", default="Cassandra Sklarz")
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
