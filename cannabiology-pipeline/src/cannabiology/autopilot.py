"""Unattended batch execution and batch approval.

Autopilot removes the per-figure interruption, not the human gate. It drives
every runnable figure as far as automation is allowed to take it - which is
always PENDING_HUMAN_APPROVAL - and reports what it could not touch and why.

Approval stays a separate, explicit act. Batch approval exists so that act is
one decision over a contact sheet instead of forty interruptions, and it
refuses to sweep up anything the reviewer flagged.
"""
import traceback

from . import routing, runner, state as st, vectorbuild

SKIPPED = "skipped"
COMPLETED = "completed"
FAILED = "failed"


def blocked_reason(figure, decision, store):
    """Why this figure cannot run unattended right now, or None."""
    if decision.route in routing.BLOCKED_FROM_GENERATION:
        if decision.route == routing.VECTOR_BUILD:
            try:
                vectorbuild.load_build_spec(figure.figure_id)
                return None                      # buildable
            except vectorbuild.BuildSpecMissing:
                return "no confirmed build spec"
        return f"route {decision.route} is not automatable"
    if decision.needs_route_confirmation:
        return "route derived, needs --confirm-route"
    return None


def run_all(figures, decisions, store, cfg=None, dry_run=True, no_network=False,
            confirm_route=False, limit=None, log=print):
    """Drive every runnable figure. Never stops on one figure's failure."""
    results = []
    targets = sorted(figures)
    if limit:
        targets = targets[:limit]

    for fid in targets:
        fig, dec = figures[fid], decisions[fid]
        reason = blocked_reason(fig, dec, store)
        if reason and not (dec.needs_route_confirmation and confirm_route):
            results.append({"figure_id": fid, "outcome": SKIPPED, "detail": reason,
                            "route": dec.route})
            continue

        for asset in fig.assets:
            aid = asset["asset_id"]
            rec = store.get(aid)
            if rec["state"] in (st.HUMAN_APPROVED, st.PACKAGED,
                                st.PENDING_HUMAN_APPROVAL):
                results.append({"figure_id": aid, "outcome": SKIPPED,
                                "detail": f"already {rec['state']}", "route": dec.route})
                continue
            try:
                with st.figure_lock(aid):
                    if dec.route == routing.VECTOR_BUILD:
                        r = vectorbuild.run_asset(fig, asset, dec, store,
                                                  log=lambda *a: None)
                    else:
                        r = runner.run_asset(fig, asset, dec, store, cfg=cfg,
                                             dry_run=dry_run, no_network=no_network,
                                             confirm_route=confirm_route,
                                             log=lambda *a: None)
                results.append({"figure_id": aid, "outcome": COMPLETED,
                                "detail": r["state"], "route": dec.route})
                log(f"  {aid:14} {r['state']}")
            except Exception as e:                # one bad figure must not stop the run
                results.append({"figure_id": aid, "outcome": FAILED,
                                "detail": f"{type(e).__name__}: {e}",
                                "route": dec.route,
                                "traceback": traceback.format_exc()})
                log(f"  {aid:14} FAILED - {type(e).__name__}: {e}")
            finally:
                store.save()
    return results


def flag_reasons(rec):
    """Why this figure should not be swept up in a batch approval.

    An empty list means nothing about the automated pass asks for a second look.
    """
    reasons = []
    if rec["state"] != st.PENDING_HUMAN_APPROVAL:
        reasons.append(f"state is {rec['state']}, not awaiting approval")
    reviews = rec.get("reviews") or []
    if reviews:
        last = reviews[-1]
        if last.get("synthetic"):
            reasons.append("review was a dry-run placeholder, not a real OA review")
        counts = last.get("counts") or {}
        if counts.get("majors"):
            reasons.append(f"{counts['majors']} major finding(s)")
        if counts.get("minors"):
            reasons.append(f"{counts['minors']} minor finding(s)")
        if counts.get("preserve_damage"):
            reasons.append("repair damaged preserved elements")
        if last.get("verdict") and last["verdict"] != "PRODUCTION_READY_BASE_ART":
            reasons.append(f"last verdict {last['verdict']}")
    if rec.get("generative_repairs", 0) >= 3:
        reasons.append(f"{rec['generative_repairs']} generative repairs")
    return reasons


def approvable(store, only=None, exclude=None):
    """Split pending figures into clear and flagged."""
    clear, flagged = [], []
    for aid, rec in sorted(store.all().items()):
        if only and aid not in only:
            continue
        if exclude and aid in exclude:
            continue
        if rec["state"] != st.PENDING_HUMAN_APPROVAL:
            continue
        (flagged if flag_reasons(rec) else clear).append(aid)
    return clear, flagged


def approve_many(store, asset_ids, by):
    approved = []
    for aid in asset_ids:
        store.transition(aid, st.HUMAN_APPROVED, f"approved by {by} (batch)")
        store.get(aid)["human_approved"] = True
        approved.append(aid)
    store.save()
    return approved
