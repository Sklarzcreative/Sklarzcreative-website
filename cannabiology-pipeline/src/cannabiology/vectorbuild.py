"""VECTOR_BUILD execution: produce a figure's scientific content deterministically.

This is the lane that must never touch an image model. Everything here is built
from a cited source or a human-confirmed spec, and fails closed without one.
Like every other lane, it ends at PENDING_HUMAN_APPROVAL.
"""
import json
import time
from pathlib import Path

import yaml

import re

from . import routing, state as st, vector, workspace
from .builders import chem, diagram


def _norm(t):
    """Loose match for label coverage: case, punctuation, the multiplication
    sign the tracker uses for genotype x environment, and en/-ce spellings."""
    t = t.lower().replace("defence", "defense").replace("\u00d7", "x")
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def label_coverage(required, artwork_texts):
    """Split the tracker's required labels into those the artwork already
    prints and those still needing an overlay.

    A built diagram prints its own node text, so overlaying the same words again
    is duplication. A generated image prints nothing, so everything needs an
    overlay. Deciding this by inspection, rather than by route, keeps the
    tracker's label list authoritative either way.
    """
    haystack = " | ".join(_norm(t) for t in artwork_texts)
    covered, missing = [], []
    for label in required:
        parts = [p for p in re.split(r"[/,]", label) if p.strip()]
        hit = any(_norm(p) and _norm(p) in haystack for p in parts)
        (covered if hit else missing).append(label)
    return covered, missing


class BuildSpecMissing(RuntimeError):
    pass


def _now_slug():
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def build_spec_path(figure_id):
    return workspace.resolve() / "canonical" / "build_specs" / f"{figure_id}.yaml"


def chem_registry_path():
    return workspace.resolve() / "canonical" / "chem_sources.yaml"


def load_build_spec(figure_id):
    p = build_spec_path(figure_id)
    if not p.exists():
        raise BuildSpecMissing(
            f"No build spec for {figure_id} at {p}.\n"
            "A VECTOR_BUILD figure needs its scientific content stated by a human:\n"
            "  builder: chem     -> list the compounds (each must be in the "
            "verified chemical registry)\n"
            "  builder: diagram  -> a confirmed node/edge spec\n"
            "Nothing is inferred for this route.")
    spec = yaml.safe_load(p.read_text()) or {}
    if not spec.get("builder"):
        raise BuildSpecMissing(f"{p.name} does not name a builder")
    return spec


def run_asset(figure, asset, decision, store, log=print):
    """Build one VECTOR_BUILD asset. Refuses any other route."""
    if decision.route != routing.VECTOR_BUILD:
        raise RuntimeError(
            f"{figure.figure_id} is routed {decision.route}, not VECTOR_BUILD. "
            "Use `run` for generative routes.")

    aid = asset["asset_id"]
    rec = store.get(aid)
    rec["route"] = decision.route
    store.transition(aid, st.ROUTED, "vector build")

    spec = load_build_spec(figure.figure_id)
    run_dir = workspace.assert_safe_write(
        workspace.resolve() / "runs" / figure.figure_id / f"build_{_now_slug()}")
    for sub in ("vector", "package"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)
    store.transition(aid, st.CONTEXT_READY, f"build spec: {spec['builder']}")

    provenance = {"builder": spec["builder"], "figure_id": figure.figure_id}
    artwork_texts = []
    width = int(spec.get("width", 1200))
    height = int(spec.get("height", 720))

    if spec["builder"] == "chem":
        registry = chem.load_registry(chem_registry_path())
        names = spec.get("compounds") or []
        if not names:
            raise BuildSpecMissing(f"{figure.figure_id}: chem spec lists no compounds")
        svg, provs = chem.render_panel(
            names, registry, cols=int(spec.get("columns", 2)))
        provenance["compounds"] = provs
        artwork_texts = [p["display_name"] for p in provs]
        log(f"  chemistry: {len(provs)} structure(s) from cited sources")
    elif spec["builder"] == "diagram":
        dspec = diagram.load_spec(
            workspace.resolve() / "canonical" / "diagram_specs" / f"{figure.figure_id}.yaml")
        svg = diagram.build(dspec, width, height)
        artwork_texts = ([n["label"] for n in dspec["nodes"]]
                         + [b.get("label", "") for b in dspec.get("bands", [])])
        provenance["spec_source"] = dspec["source"]
        provenance["nodes"] = len(dspec["nodes"])
        log(f"  diagram: {len(dspec['nodes'])} nodes from confirmed spec")
    else:
        raise BuildSpecMissing(f"Unknown builder {spec['builder']!r}")

    store.transition(aid, st.BUILDING, "deterministic build - no model call")
    art_path = run_dir / "vector" / f"{aid}_structure.svg"
    art_path.write_text(svg)
    rec["candidates"].append({"candidate_id": "build001", "path": str(art_path),
                              "written": True, "deterministic": True})
    rec["selected_candidate"] = "build001"
    store.transition(aid, st.BUILT, "built deterministically")

    required = asset.get("manual_labels", [])
    covered, missing = label_coverage(required, artwork_texts)
    provenance["labels_required"] = required
    provenance["labels_already_in_artwork"] = covered
    provenance["labels_overlaid"] = missing
    if covered:
        log(f"  labels: {len(covered)}/{len(required)} already printed by the "
            f"artwork; overlaying {len(missing)}")
    # The diagram prints its own footer source line, so start the annotation
    # footer above it rather than on top of it.
    layer, manifest = vector.write_layer(
        run_dir, aid, missing, width, height,
        all_labels=required, covered=covered,
        figure_number=figure.figure_id,
        caption=asset.get("caption", ""),
        footer_top=height - 78)
    comp = _overlay(svg, Path(layer).read_text(), width, height)
    comp_path = run_dir / "package" / f"{aid}_composite.svg"
    comp_path.write_text(comp)
    # Written last, so it records the label decisions made above rather than a
    # half-filled record.
    prov_path = run_dir / "vector" / f"{aid}_provenance.json"
    prov_path.write_text(json.dumps(provenance, indent=2))
    rec["vector"] = {"layer": str(layer), "manifest": str(manifest),
                     "composite": str(comp_path), "label_count": len(missing),
                     "labels_already_in_artwork": len(covered),
                     "provenance": str(prov_path)}
    rec["run_dir"] = str(run_dir)

    # No image review: there is no generated art to second-guess. The content is
    # exactly what the cited source says, so a human confirms it directly.
    store.transition(aid, st.PRODUCTION_READY_BASE_ART,
                     "built deterministically from cited sources")
    store.transition(aid, st.PENDING_HUMAN_APPROVAL,
                     "awaiting human confirmation against the source")
    log("  -> PENDING_HUMAN_APPROVAL")
    return rec


def _overlay(base_svg, layer_svg, width, height):
    """Compose two SVG fragments. Both are vector, so the result stays vector."""
    inner_base = base_svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
    inner_layer = layer_svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
            f'{inner_base}{inner_layer}</svg>')
