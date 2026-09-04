"""Concept diagrams built from a human-confirmed spec.

Topology is the scientific content of a mechanism, sequence or hierarchy, so it
is never inferred. The builder reads a spec a person wrote and confirmed against
the manuscript, and lays it out deterministically.

Six layouts, chosen by the spec's `layout` key (default "flow"):

  flow      boxes and arrows in columns      pipelines, mechanisms, pathways
  lanes     parallel tracks of stages        side-by-side workflow comparison
  timeline  dated events along an axis       histories, process evolution
  pyramid   stacked tiers, narrowing up      evidence hierarchies
  layers    stacked horizontal bands         multi-omics and systems stacks
  hub       centre with radiating spokes     network and convergence maps

Every layout shares one palette and type scale so the figures read as one
system across the book.
"""
import math
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

FONT = "IBM Plex Sans, Helvetica, Arial, sans-serif"
PALETTE = {
    "ink": "#14201a", "muted": "#3d4a41", "rule": "#c9d2c6",
    "fill": "#ffffff", "accent": "#1f4433", "band": "#f1f3ed",
}
# Tier fills for stacked layouts: one hue, stepped in lightness, so emphasis
# comes from position rather than from colour competing with the accent.
STEPS = ["#e8ede6", "#dbe4d8", "#cddaca", "#bfd0bc", "#b1c6ae", "#a3bca0"]

NODE_W, NODE_H, LINE_H = 190, 64, 16


class DiagramError(RuntimeError):
    pass


class UnconfirmedSpec(DiagramError):
    """Raised when no human-confirmed spec exists. Always fail closed."""


# ----------------------------------------------------------------- loading --
def load_spec(path, allow_unconfirmed=False):
    """Load a diagram spec. Unconfirmed specs load ONLY for preview rendering."""
    p = Path(path)
    if not p.exists():
        raise UnconfirmedSpec(
            f"No diagram spec at {p}.\n"
            "A mechanism diagram's topology is scientific content and is never "
            "inferred. Write the spec, confirm it against the manuscript, and set "
            "confirmed: true.")
    spec = yaml.safe_load(p.read_text()) or {}
    if spec.get("confirmed") is not True and not allow_unconfirmed:
        raise UnconfirmedSpec(
            f"Spec {p.name} is not marked confirmed. A human must check the "
            "topology against the manuscript and set confirmed: true.")
    for field in ("figure_id", "nodes", "source"):
        if not spec.get(field):
            raise DiagramError(f"Spec {p.name} is missing required field {field!r}")
    layout = spec.get("layout", "flow")
    if layout not in LAYOUTS:
        raise DiagramError(
            f"Spec {p.name} asks for layout {layout!r}; known layouts are "
            f"{', '.join(sorted(LAYOUTS))}")
    return spec


# ----------------------------------------------------------------- helpers --
def _wrap(text, chars):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= chars:
            cur = f"{cur} {w}".strip()
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def _text(x, y, s, size=13.5, weight=400, anchor="middle", fill=None,
          letter_spacing=None):
    ls = f' letter-spacing="{letter_spacing}"' if letter_spacing else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}"{ls} '
            f'fill="{fill or PALETTE["ink"]}">{escape(str(s))}</text>')


def _block(cx, cy, label, chars=24, size=13.5, weight=400, fill=None):
    """Vertically centred, wrapped text block."""
    lines = _wrap(label, chars)
    top = cy - (len(lines) - 1) * LINE_H / 2 + 5
    return [_text(cx, top + i * LINE_H, ln, size, weight, fill=fill)
            for i, ln in enumerate(lines)]


def _node_box(x, y, label, emphasis=False, w=NODE_W, h=NODE_H, fill=None):
    stroke = PALETTE["accent"] if emphasis else PALETTE["rule"]
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" '
           f'fill="{fill or PALETTE["fill"]}" stroke="{stroke}" '
           f'stroke-width="{2.2 if emphasis else 1.3}"/>']
    out += _block(x + w / 2, y + h / 2, label,
                  chars=max(12, round(w / 8)), weight=600 if emphasis else 400)
    return out


def _defs():
    return ('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{PALETTE["ink"]}"/></marker></defs>')


def _open(width, height):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">',
            f'<rect width="{width}" height="{height}" fill="{PALETTE["fill"]}"/>',
            _defs()]


def _close(parts, spec, width, height, draft):
    confirmed = spec.get("confirmed") is True
    parts.append(_text(24, height - 16,
                       ("Built from confirmed spec" if confirmed
                        else "DRAFT - topology NOT confirmed") + f": {spec['source']}",
                       size=11, anchor="start", fill=PALETTE["muted"]))
    if draft or not confirmed:
        parts.append(f'<rect x="0" y="0" width="{width}" height="34" fill="#9b2f2c"/>')
        parts.append(_text(width / 2, 23,
                           "DRAFT FOR REVIEW - TOPOLOGY NOT YET CONFIRMED",
                           size=14, weight=700, fill="#ffffff"))
    parts.append("</svg>")
    return "\n".join(parts)


def _require(spec, key, per_node=None):
    for n in spec["nodes"]:
        if per_node and per_node not in n:
            raise DiagramError(
                f"{spec['figure_id']}: layout {spec.get('layout')} needs "
                f"'{per_node}' on every node; {n.get('id', n)} has none")


# ------------------------------------------------------------------ layouts --
def _flow(spec, width, height, pad=48):
    nodes, edges = spec["nodes"], spec.get("edges", [])
    cols = max(n.get("column", 0) for n in nodes) + 1
    by_col = {}
    for n in nodes:
        by_col.setdefault(n.get("column", 0), []).append(n)
    step_x = (width - 2 * pad - NODE_W) / max(1, cols - 1) if cols > 1 else 0
    placed = {}
    for col, group in by_col.items():
        group = sorted(group, key=lambda n: n.get("row", 0))
        span = height - 2 * pad - NODE_H
        step_y = span / max(1, len(group) - 1) if len(group) > 1 else 0
        for i, n in enumerate(group):
            placed[n["id"]] = {
                "x": pad + col * step_x,
                "y": pad + (i * step_y if len(group) > 1 else span / 2), "node": n}

    p = _open(width, height)
    for band in spec.get("bands", []):
        p.append(f'<rect x="{band["x"]}" y="{band["y"]}" width="{band["width"]}" '
                 f'height="{band["height"]}" fill="{PALETTE["band"]}" rx="4"/>')
        if band.get("label"):
            p.append(_text(band["x"] + 12, band["y"] + 22, band["label"].upper(),
                           size=12, weight=600, anchor="start",
                           fill=PALETTE["muted"], letter_spacing="0.06em"))
    for e in edges:
        a, b = placed.get(e["from"]), placed.get(e["to"])
        if not a or not b:
            raise DiagramError(f"Edge references unknown node: {e}")
        x1, y1 = a["x"] + NODE_W, a["y"] + NODE_H / 2
        x2, y2 = b["x"], b["y"] + NODE_H / 2
        mid = (x1 + x2) / 2
        dash = ' stroke-dasharray="5 4"' if e.get("style") == "dashed" else ""
        p.append(f'<path d="M {x1} {y1} C {mid} {y1}, {mid} {y2}, {x2} {y2}" '
                 f'fill="none" stroke="{PALETTE["ink"]}" stroke-width="1.6"{dash} '
                 f'marker-end="url(#arrow)"/>')
        if e.get("label"):
            p.append(_text(mid, (y1 + y2) / 2 - 7, e["label"], size=12,
                           fill=PALETTE["muted"]))
    for pl in placed.values():
        p += _node_box(pl["x"], pl["y"], pl["node"]["label"],
                       pl["node"].get("emphasis") == "primary")
    return p


def _lanes(spec, width, height, pad=48):
    """Parallel tracks of stages. Compares two or more workflows step by step."""
    _require(spec, "lanes", per_node="lane")
    lane_names = []
    for n in spec["nodes"]:
        if n["lane"] not in lane_names:
            lane_names.append(n["lane"])
    top = pad + 34
    lane_h = (height - top - pad - 40) / len(lane_names)
    steps = max(n.get("step", 0) for n in spec["nodes"]) + 1
    box_w = min(NODE_W, (width - 2 * pad - 170) / max(1, steps) - 18)
    step_x = (width - pad - 170 - box_w) / max(1, steps - 1) if steps > 1 else 0

    p = _open(width, height)
    for li, lane in enumerate(lane_names):
        ly = top + li * lane_h
        p.append(f'<rect x="{pad}" y="{ly}" width="{width - 2 * pad}" '
                 f'height="{lane_h - 14}" fill="{PALETTE["band"]}" rx="4"/>')
        p += _block(pad + 84, ly + (lane_h - 14) / 2, lane, chars=18,
                    size=13, weight=600, fill=PALETTE["muted"])
        row = sorted((n for n in spec["nodes"] if n["lane"] == lane),
                     key=lambda n: n.get("step", 0))
        for n in row:
            x = pad + 170 + n.get("step", 0) * step_x
            y = ly + (lane_h - 14) / 2 - NODE_H / 2
            p += _node_box(x, y, n["label"], n.get("emphasis") == "primary",
                           w=box_w)
        for a, b in zip(row, row[1:]):
            x1 = pad + 170 + a.get("step", 0) * step_x + box_w
            x2 = pad + 170 + b.get("step", 0) * step_x
            y = ly + (lane_h - 14) / 2
            p.append(f'<line x1="{x1 + 4}" y1="{y}" x2="{x2 - 4}" y2="{y}" '
                     f'stroke="{PALETTE["ink"]}" stroke-width="1.6" '
                     f'marker-end="url(#arrow)"/>')
    return p


def _timeline(spec, width, height, pad=64):
    """Dated events along one axis. Alternates above and below to stay legible."""
    _require(spec, "timeline", per_node="date")
    nodes = spec["nodes"]
    axis_y = height / 2
    span = width - 2 * pad
    step = span / max(1, len(nodes) - 1) if len(nodes) > 1 else 0

    p = _open(width, height)
    p.append(f'<line x1="{pad}" y1="{axis_y}" x2="{width - pad}" y2="{axis_y}" '
             f'stroke="{PALETTE["ink"]}" stroke-width="2" marker-end="url(#arrow)"/>')
    for i, n in enumerate(nodes):
        x = pad + i * step
        above = i % 2 == 0
        card_y = axis_y - 150 if above else axis_y + 44
        p.append(f'<circle cx="{x}" cy="{axis_y}" r="6" '
                 f'fill="{PALETTE["accent"] if n.get("emphasis") == "primary" else PALETTE["fill"]}" '
                 f'stroke="{PALETTE["accent"]}" stroke-width="2"/>')
        p.append(f'<line x1="{x}" y1="{axis_y + (-8 if above else 8)}" x2="{x}" '
                 f'y2="{card_y + (106 if above else 0)}" stroke="{PALETTE["rule"]}" '
                 f'stroke-width="1.2"/>')
        p.append(_text(x, card_y + (98 if above else 18), n["date"], size=13,
                       weight=700, fill=PALETTE["accent"]))
        p += _block(x, card_y + (48 if above else 62), n["label"], chars=20, size=13)
    return p


def _pyramid(spec, width, height, pad=64):
    """Stacked tiers narrowing upward. Position encodes rank, not colour."""
    _require(spec, "pyramid", per_node="tier")
    tiers = sorted(spec["nodes"], key=lambda n: n["tier"])
    n = len(tiers)
    tier_h = min(78, (height - 2 * pad - 40) / max(1, n))
    max_w = min(width * 0.52, 720)
    cx = width * 0.40

    p = _open(width, height)
    for i, node in enumerate(tiers):
        w = max_w * (0.30 + 0.70 * (i + 1) / n)
        y = pad + 20 + i * tier_h
        p.append(f'<path d="M {cx - w / 2} {y} L {cx + w / 2} {y} '
                 f'L {cx + w / 2 + tier_h * 0.32} {y + tier_h - 6} '
                 f'L {cx - w / 2 - tier_h * 0.32} {y + tier_h - 6} Z" '
                 f'fill="{STEPS[min(i, len(STEPS) - 1)]}" '
                 f'stroke="{PALETTE["rule"]}" stroke-width="1.2"/>')
        p += _block(cx, y + (tier_h - 6) / 2, node["label"], chars=34, size=13.5,
                    weight=600 if node.get("emphasis") == "primary" else 400)
        if node.get("note"):
            p += _block(width * 0.80, y + (tier_h - 6) / 2, node["note"],
                        chars=28, size=12, fill=PALETTE["muted"])
    if spec.get("axis_label"):
        p.append(_text(cx, pad + 6, spec["axis_label"], size=12, weight=600,
                       fill=PALETTE["muted"]))
    return p


def _layers(spec, width, height, pad=56):
    """Stacked horizontal bands. For systems described as levels."""
    _require(spec, "layers", per_node="layer")
    rows = sorted(spec["nodes"], key=lambda n: n["layer"])
    band_h = min(84, (height - 2 * pad - 40) / max(1, len(rows)))
    x, w = pad, width * 0.56

    p = _open(width, height)
    for i, node in enumerate(rows):
        y = pad + 20 + i * band_h
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{band_h - 8}" rx="3" '
                 f'fill="{STEPS[min(i, len(STEPS) - 1)]}" '
                 f'stroke="{PALETTE["rule"]}" stroke-width="1.2"/>')
        p += _block(x + w / 2, y + (band_h - 8) / 2, node["label"], chars=40,
                    size=13.5, weight=600 if node.get("emphasis") == "primary" else 400)
        if node.get("note"):
            p += _block(x + w + 150, y + (band_h - 8) / 2, node["note"], chars=26,
                        size=12, fill=PALETTE["muted"])
        if i < len(rows) - 1:
            p.append(f'<line x1="{x + w / 2}" y1="{y + band_h - 8}" '
                     f'x2="{x + w / 2}" y2="{y + band_h}" '
                     f'stroke="{PALETTE["ink"]}" stroke-width="1.4" '
                     f'marker-end="url(#arrow)"/>')
    return p


def _hub(spec, width, height):
    """Centre with radiating spokes. For convergence and network maps."""
    hub = [n for n in spec["nodes"] if n.get("hub")]
    if len(hub) != 1:
        raise DiagramError(
            f"{spec['figure_id']}: layout hub needs exactly one node with "
            f"hub: true (found {len(hub)})")
    hub = hub[0]
    spokes = [n for n in spec["nodes"] if not n.get("hub")]
    cx, cy = width / 2, height / 2 + 10
    rx, ry = min(width * 0.34, 470), min(height * 0.33, 250)

    p = _open(width, height)
    for i, n in enumerate(spokes):
        ang = -math.pi / 2 + 2 * math.pi * i / max(1, len(spokes))
        x, y = cx + rx * math.cos(ang), cy + ry * math.sin(ang)
        p.append(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" '
                 f'stroke="{PALETTE["rule"]}" stroke-width="1.4"/>')
    for i, n in enumerate(spokes):
        ang = -math.pi / 2 + 2 * math.pi * i / max(1, len(spokes))
        x, y = cx + rx * math.cos(ang), cy + ry * math.sin(ang)
        p += _node_box(x - NODE_W / 2, y - NODE_H / 2, n["label"],
                       n.get("emphasis") == "primary")
    p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="132" ry="62" '
             f'fill="{PALETTE["band"]}" stroke="{PALETTE["accent"]}" stroke-width="2.2"/>')
    p += _block(cx, cy, hub["label"], chars=20, size=14.5, weight=700)
    return p


LAYOUTS = {"flow": _flow, "lanes": _lanes, "timeline": _timeline,
           "pyramid": _pyramid, "layers": _layers, "hub": _hub}


def build(spec, width=1200, height=720, draft=False):
    """Render the spec to SVG. Deterministic for a given spec.

    draft=True renders an unconfirmed spec for review, with an unmissable
    banner. A topology cannot be checked without being seen, but a draft must
    never be mistaken for an approved figure.
    """
    layout = spec.get("layout", "flow")
    if layout not in LAYOUTS:
        raise DiagramError(f"Unknown layout {layout!r}")
    parts = LAYOUTS[layout](spec, width, height)
    return _close(parts, spec, width, height, draft)
