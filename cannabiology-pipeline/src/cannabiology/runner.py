"""Orchestrator: route -> context -> prompt -> candidates -> OA -> repair ->
vector overlay -> final OA -> package -> PENDING_HUMAN_APPROVAL.

Nothing here can approve a figure. The terminal automated state is always
PENDING_HUMAN_APPROVAL.
"""
import json
import time
from pathlib import Path

from . import (config, context, prompts, repair as repair_mod, routing, schema,
               state as st, vector, verdict as V, workspace)
from .adapters import (dryrun, image_backend, review_backend,
                       openai_images, openai_review)


class RouteBlocked(RuntimeError):
    pass


def _now_slug():
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def tier_of(figure_id, cfg):
    t = cfg["tiers"]
    if figure_id in (t.get("tier1") or []):
        return "tier1"
    if figure_id in (t.get("tier3") or []):
        return "tier3"
    return t.get("default", "tier2")


def _dims(aspect, cfg, final=False):
    size = cfg["image"]["final_size" if final else "draft_size"]
    w, h = (int(x) for x in size.split("x"))
    return w, h, size


def guard_route(decision, confirm_route=False, force=False):
    """The routing gate. --force never opens it."""
    if decision.route in routing.BLOCKED_FROM_GENERATION:
        raise RouteBlocked(
            f"{decision.figure_id} is routed {decision.route} and must not enter "
            f"image generation.\n  Reasons: {'; '.join(decision.reasons)}")
    if decision.needs_route_confirmation and not confirm_route:
        raise RouteBlocked(
            f"{decision.figure_id} route {decision.route} was DERIVED, not stated by "
            "the tracker. A human must confirm it before generation.\n"
            f"  Reasons: {'; '.join(decision.reasons)}\n"
            "  Re-run with --confirm-route once confirmed.")
    return True


def build_brief(figure, asset, ctx, decision, candidate_id, review_round,
                prior_review=None, preserve=None):
    return {
        "asset_id": asset["asset_id"],
        "figure_id": figure.figure_id,
        "figure_title": figure.title,
        "route": decision.route,
        "educational_purpose": figure.purpose,
        "manuscript_section": figure.manuscript_section,
        "manuscript_context": (ctx.get("source") or {}).get("excerpt", ""),
        "figure_brief_from_manuscript": (ctx.get("source") or {}).get("figure_brief", ""),
        "production_prompt": asset["prompt"],
        "negative_constraints": asset["negative"],
        "scientific_accuracy_notes": asset["science_notes"],
        "manual_labels": asset.get("manual_labels", []),
        "caption_requirements": asset.get("caption", ""),
        "candidate_id": candidate_id,
        "review_round": review_round,
        "prior_review_summary": (prior_review or {}).get("summary", ""),
        "preserve": preserve or [],
    }


def _score(review):
    issues = review.get("issues", [])
    b = sum(1 for i in issues if i["severity"] == "BLOCKER")
    m = sum(1 for i in issues if i["severity"] == "MAJOR")
    mi = sum(1 for i in issues if i["severity"] == "MINOR")
    return (b, m, mi, -float(review.get("confidence", 0)))


def run_asset(figure, asset, decision, store, cfg=None, dry_run=True,
              no_network=False, confirm_route=False, max_iterations=None,
              candidate_count=None, log=print):
    """Drive one production asset as far as automation is allowed to take it."""
    cfg = cfg or config.load()
    guard_route(decision, confirm_route=confirm_route)

    aid = asset["asset_id"]
    rec = store.get(aid)
    rec["route"] = decision.route
    store.transition(aid, st.ROUTED, "routing gate passed")

    ws = workspace.resolve()
    run_dir = workspace.assert_safe_write(ws / "runs" / figure.figure_id / f"run_{_now_slug()}")
    for sub in ("prompts", "candidates", "oa", "vector", "package"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)

    ctx = context.extract(figure)
    cpath, cver = context.save(ctx, figure.figure_id)
    rec["context_version"] = cver
    store.transition(aid, st.CONTEXT_READY,
                     f"context v{cver} ({'source found' if ctx['source_found'] else 'no manuscript anchor'})")
    log(f"  context: v{cver} source={'yes' if ctx['source_found'] else 'NO ANCHOR'}")

    base_prompt = prompts.assemble(asset, ctx)
    pv = prompts.save_version(run_dir, aid, base_prompt, {
        "model": cfg["models"]["image_generate"], "route": decision.route,
        "context_version": cver, "parent_candidate": None, "repair_reason": None})
    rec["prompt_versions"].append({"version": pv["version"], "sha": pv["prompt_sha256"]})
    store.transition(aid, st.PROMPT_READY, f"prompt v{pv['version']}")

    tier = tier_of(figure.figure_id, cfg)
    n_cand = candidate_count or cfg["pipeline"]["candidate_counts"][tier]
    max_rep = max_iterations if max_iterations is not None else cfg["pipeline"]["max_generative_repairs"]

    img = image_backend(no_network=no_network, dry_run=dry_run)
    rev = review_backend(no_network=no_network, dry_run=dry_run)
    oa_schema = schema.load_schema("oa_review.schema.json")
    w, h, size = _dims(asset.get("aspect", "4:3"), cfg)

    # ---- initial candidates -------------------------------------------------
    store.transition(aid, st.GENERATING, f"{n_cand} candidate(s), tier {tier}")
    candidates = []
    for k in range(n_cand):
        cid = f"v{k + 1:03d}"
        out = run_dir / "candidates" / f"{aid}_{cid}.png"
        try:
            res = img.generate(base_prompt, out, cfg["models"]["image_generate"],
                               size, cfg["image"]["draft_quality"])
        except (openai_images.BackendUnavailable, Exception) as e:
            if isinstance(e, openai_images.BackendUnavailable):
                log(f"  generation unavailable: {e}")
                store.transition(aid, st.HUMAN_CONFIRMATION_REQUIRED,
                                 f"image backend unavailable: {e}", force=True)
                return rec
            raise
        candidates.append({"candidate_id": cid, **res})
        rec["candidates"].append({"candidate_id": cid, "path": res["path"],
                                  "written": res["image_written"],
                                  "prompt_version": pv["version"]})
        log(f"  candidate {cid}: {res['status']}")
    store.transition(aid, st.CANDIDATE_READY, f"{len(candidates)} candidate(s)")

    # ---- review + select ----------------------------------------------------
    store.transition(aid, st.OA_REVIEW, "initial review")
    reviewed = []
    for c in candidates:
        brief = build_brief(figure, asset, ctx, decision, c["candidate_id"], 1)
        try:
            r = rev.review(brief, c["path"], cfg["models"]["oa_routine"], schema=oa_schema)
        except Exception as e:
            log(f"  OA review unavailable: {e}")
            store.transition(aid, st.HUMAN_CONFIRMATION_REQUIRED,
                             f"OA backend unavailable: {e}", force=True)
            return rec
        schema.validate(r, oa_schema)
        (run_dir / "oa" / f"{aid}_{c['candidate_id']}_r1.json").write_text(
            json.dumps(r, indent=2))
        reviewed.append((c, r))

    best_c, best_r = min(reviewed, key=lambda pair: _score(pair[1]))
    rec["selected_candidate"] = best_c["candidate_id"]
    log(f"  selected {best_c['candidate_id']} of {len(reviewed)}")

    # ---- repair loop --------------------------------------------------------
    round_no = 1
    current = best_c
    review = best_r
    while True:
        vd, why, counts = V.compute(review, decision.route,
                                    rec["generative_repairs"], cfg)
        rec["reviews"].append({"round": round_no, "candidate": current["candidate_id"],
                               "verdict": vd, "why": why, "counts": counts,
                               "synthetic": bool(review.get("_synthetic"))})
        log(f"  OA round {round_no}: {vd} ({why})")

        if vd == V.PRODUCTION_READY_BASE_ART:
            store.transition(aid, st.PRODUCTION_READY_BASE_ART, why)
            break
        if vd == V.REJECTED:
            store.transition(aid, st.REJECTED, why)
            return rec
        if vd in (V.SCIENTIFIC_VERIFICATION_REQUIRED, V.HUMAN_CONFIRMATION_REQUIRED):
            store.transition(aid,
                             st.SCIENTIFIC_VERIFICATION_REQUIRED
                             if vd == V.SCIENTIFIC_VERIFICATION_REQUIRED
                             else st.HUMAN_CONFIRMATION_REQUIRED, why)
            return rec

        plan = repair_mod.plan(review, vd, rec, cfg)
        rec["repairs"].append({"round": round_no, **plan})
        log(f"  repair: {plan['action']} ({plan['reason'][:70]})")

        if plan["action"] == repair_mod.HUMAN_CONFIRMATION:
            store.transition(aid, st.HUMAN_CONFIRMATION_REQUIRED, plan["reason"])
            return rec

        if plan["action"] == repair_mod.VECTOR_EDIT:
            # Deterministic overlay fix: does NOT consume a generative round.
            rec["vector_edits"] += 1
            store.transition(aid, st.VECTOR_EDIT_REQUIRED, plan["reason"])
            store.transition(aid, st.PRODUCTION_READY_BASE_ART,
                             "base art unchanged; correction applied in vector layer",
                             force=True)
            break

        if rec["generative_repairs"] >= max_rep:
            store.transition(aid, st.HUMAN_CONFIRMATION_REQUIRED,
                             f"generative repair cap {max_rep} reached")
            return rec

        rec["generative_repairs"] += 1
        round_no += 1
        rp = repair_mod.build_repair_prompt(base_prompt, plan)
        pv2 = prompts.save_version(run_dir, aid, rp, {
            "model": cfg["models"]["image_edit"], "route": decision.route,
            "context_version": cver, "parent_candidate": current["candidate_id"],
            "repair_reason": plan["action"]})
        rec["prompt_versions"].append({"version": pv2["version"], "sha": pv2["prompt_sha256"]})

        cid = f"v{len(rec['candidates']) + 1:03d}"
        out = run_dir / "candidates" / f"{aid}_{cid}.png"
        store.transition(aid,
                         st.IMAGE_EDIT_REQUIRED if plan["action"] == repair_mod.IMAGE_EDIT
                         else st.REGENERATE_REQUIRED, plan["action"])
        store.transition(aid, st.GENERATING, f"repair round {round_no}")
        try:
            if plan["action"] == repair_mod.IMAGE_EDIT:
                res = img.edit(rp, current["path"], out, cfg["models"]["image_edit"])
            else:
                res = img.generate(rp, out, cfg["models"]["image_generate"],
                                   size, cfg["image"]["draft_quality"])
        except Exception as e:
            log(f"  repair generation unavailable: {e}")
            store.transition(aid, st.HUMAN_CONFIRMATION_REQUIRED, str(e), force=True)
            return rec
        current = {"candidate_id": cid, **res}
        rec["candidates"].append({"candidate_id": cid, "path": res["path"],
                                  "written": res["image_written"],
                                  "prompt_version": pv2["version"]})
        rec["selected_candidate"] = cid
        store.transition(aid, st.CANDIDATE_READY, f"repair candidate {cid}")
        store.transition(aid, st.OA_REVIEW, f"review round {round_no}")
        brief = build_brief(figure, asset, ctx, decision, cid, round_no,
                            prior_review=review, preserve=plan["preserve"])
        review = rev.review(brief, current["path"], cfg["models"]["oa_routine"],
                            schema=oa_schema)
        schema.validate(review, oa_schema)
        (run_dir / "oa" / f"{aid}_{cid}_r{round_no}.json").write_text(
            json.dumps(review, indent=2))

    # ---- vector overlay + composite ----------------------------------------
    labels = asset.get("manual_labels", [])
    svg_path, man_path = vector.write_layer(run_dir, aid, labels, w, h,
                                            figure_number=figure.figure_id,
                                            caption=asset.get("caption", "")[:110])
    comp = vector.composite(current["path"], Path(svg_path).read_text(), w, h)
    comp_path = run_dir / "package" / f"{aid}_composite.svg"
    comp_path.write_text(comp)
    rec["vector"] = {"layer": str(svg_path), "manifest": str(man_path),
                     "composite": str(comp_path), "label_count": len(labels)}
    log(f"  vector overlay: {len(labels)} labels -> composite")

    # ---- final OA on the composite -----------------------------------------
    if cfg["review"]["final_review_requires_composite"]:
        brief = build_brief(figure, asset, ctx, decision,
                            current["candidate_id"], round_no + 1)
        brief["note"] = "FINAL review of the composited artifact (base art + labels)."
        try:
            final = rev.review(brief, str(comp_path), cfg["models"]["oa_final"],
                               schema=oa_schema)
            schema.validate(final, oa_schema)
            (run_dir / "oa" / f"{aid}_final.json").write_text(json.dumps(final, indent=2))
            fvd, fwhy, fcounts = V.compute(final, decision.route,
                                           rec["generative_repairs"], cfg)
            rec["reviews"].append({"round": "final", "verdict": fvd, "why": fwhy,
                                   "counts": fcounts,
                                   "synthetic": bool(final.get("_synthetic"))})
            log(f"  final OA: {fvd}")
            if fvd != V.PRODUCTION_READY_BASE_ART:
                store.transition(aid, st.HUMAN_CONFIRMATION_REQUIRED,
                                 f"final review: {fwhy}", force=True)
                return rec
        except Exception as e:
            log(f"  final OA unavailable: {e}")

    rec["run_dir"] = str(run_dir)
    store.transition(aid, st.PENDING_HUMAN_APPROVAL,
                     "automation complete; awaiting human approval")
    log("  -> PENDING_HUMAN_APPROVAL")
    return rec
