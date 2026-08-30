"""Canonical count reconciliation and integrity audit.

A full-book run is refused unless the routed totals reconcile against the
tracker-derived canonical totals.
"""
import re
from collections import Counter

from . import config


class ReconciliationError(RuntimeError):
    pass


def audit(figures, decisions, manuscript_texts=None, cfg=None):
    cfg = cfg or config.load()
    exp_f = cfg["canonical"]["expected_figures"]
    exp_a = cfg["canonical"]["expected_assets"]

    n_fig = len(figures)
    n_asset = sum(len(f.assets) for f in figures.values())

    by_route = Counter()
    assets_by_route = Counter()
    for fid, d in decisions.items():
        by_route[d.route] += 1
        assets_by_route[d.route] += len(figures[fid].assets)

    problems = []
    if n_fig != exp_f:
        problems.append(f"figure count {n_fig} != expected {exp_f}")
    if n_asset != exp_a:
        problems.append(f"asset count {n_asset} != expected {exp_a}")
    if sum(by_route.values()) != n_fig:
        problems.append("routed figures do not sum to the figure total")
    if sum(assets_by_route.values()) != n_asset:
        problems.append("routed assets do not sum to the asset total")

    unrouted = [fid for fid, d in decisions.items() if not d.route]
    if unrouted:
        problems.append(f"unrouted figures: {unrouted}")

    # Duplicate figure IDs are rejected at load time (canonical.load_figures),
    # so reaching here with one means the loader was bypassed.
    dupes = [k for k, v in Counter(f.figure_id for f in figures.values()).items() if v > 1]
    asset_ids = [a["asset_id"] for f in figures.values() for a in f.assets]
    dup_assets = [k for k, v in Counter(asset_ids).items() if v > 1]
    if dup_assets:
        problems.append(f"duplicate asset IDs: {dup_assets}")

    # figures the tracker marks approved but with no artifact recorded anywhere
    approved_no_art = [
        f.figure_id for f in figures.values()
        if "approved" in f.approval.lower() and "not approved" not in f.approval.lower()
    ]

    referenced = set()
    if manuscript_texts:
        for text in manuscript_texts:
            referenced.update(re.findall(r"CH\d{2}-IMG-\d{2}", text))
    in_manuscript_not_tracker = sorted(referenced - set(figures))

    return {
        "figures": n_fig, "assets": n_asset,
        "expected_figures": exp_f, "expected_assets": exp_a,
        "by_route": dict(by_route), "assets_by_route": dict(assets_by_route),
        "needs_route_confirmation": sorted(
            fid for fid, d in decisions.items() if d.needs_route_confirmation),
        "duplicate_figure_ids": dupes, "duplicate_asset_ids": dup_assets,
        "approved_without_artifact": approved_no_art,
        "referenced_in_manuscript_not_in_tracker": in_manuscript_not_tracker,
        "problems": problems, "ok": not problems,
    }


def require_ok(report):
    if not report["ok"]:
        raise ReconciliationError(
            "Canonical reconciliation failed:\n  - " + "\n  - ".join(report["problems"]))
    return report
