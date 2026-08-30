"""Concept diagrams built from a human-confirmed spec.

Topology is the scientific content of a mechanism or pathway diagram, so it is
never inferred. The builder reads a spec file that a person wrote and confirmed
against the manuscript, and lays it out deterministically.
"""
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

FONT = "IBM Plex Sans, Helvetica, Arial, sans-serif"
PALETTE = {
    "ink": "#14201a", "muted": "#3d4a41", "rule": "#c9d2c6",
    "fill": "#ffffff", "accent": "#1f4433", "band": "#f1f3ed",
}


class DiagramError(RuntimeError):
    pass


class UnconfirmedSpec(DiagramError):
    """Raised when no human-confirmed spec exists. Always fail closed."""


def load_spec(path):
    p = Path(path)
    if not p.exists():
        raise UnconfirmedSpec(
            f"No diagram spec at {p}.\n"
            "A mechanism diagram's topology is scientific content and is never "
            "inferred. Write the spec, confirm it against the manuscript, and set "
            "confirmed: true.")
    spec = yaml.safe_load(p.read_text()) or {}
    if spec.get("confirmed") is not True:
        raise UnconfirmedSpec(
            f"Spec {p.name} is not marked confirmed. A human must check the "
            "topology against the manuscript and set confirmed: true.")
    for field in ("figure_id", "nodes", "source"):
        if not spec.get(field):
            raise DiagramError(f"Spec {p.name} is missing required field {field!r}")
    return spec


def _layout(nodes, width, height, pad=48, node_w=190, node_h=64):
    cols = max(n.get("column", 0) for n in nodes) + 1
    rows_by_col = {}
    for n in nodes:
        rows_by_col.setdefault(n.get("column", 0), []).append(n)
    step_x = (width - 2 * pad - node_w) / max(1, cols - 1) if cols > 1 else 0
    placed = {}
    for col, group in rows_by_col.items():
        group = sorted(group, key=lambda n: n.get("row", 0))
        n_rows = len(group)
        span = height - 2 * pad - node_h
        step_y = span / max(1, n_rows - 1) if n_rows > 1 else 0
        for i, n in enumerate(group):
            x = pad + col * step_x
            y = pad + (i * step_y if n_rows > 1 else span / 2)
            placed[n["id"]] = {"x": x, "y": y, "w": node_w, "h": node_h, "node": n}
    return placed


def build(spec, width=1200, height=720):
    """Render the confirmed spec to SVG. Deterministic for a given spec."""
    nodes, edges = spec["nodes"], spec.get("edges", [])
    placed = _layout(nodes, width, height)

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
         f'viewBox="0 0 {width} {height}">',
         f'<rect width="{width}" height="{height}" fill="{PALETTE["fill"]}"/>',
         '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
         'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{PALETTE["ink"]}"/></marker></defs>']

    for band in spec.get("bands", []):
        p.append(f'<rect x="{band["x"]}" y="{band["y"]}" width="{band["width"]}" '
                 f'height="{band["height"]}" fill="{PALETTE["band"]}" rx="4"/>')
        if band.get("label"):
            p.append(f'<text x="{band["x"] + 12}" y="{band["y"] + 22}" '
                     f'font-family="{FONT}" font-size="12" font-weight="600" '
                     f'letter-spacing="0.06em" fill="{PALETTE["muted"]}">'
                     f'{escape(band["label"].upper())}</text>')

    for e in edges:
        a, b = placed.get(e["from"]), placed.get(e["to"])
        if not a or not b:
            raise DiagramError(f"Edge references unknown node: {e}")
        x1, y1 = a["x"] + a["w"], a["y"] + a["h"] / 2
        x2, y2 = b["x"], b["y"] + b["h"] / 2
        mid = (x1 + x2) / 2
        dash = ' stroke-dasharray="5 4"' if e.get("style") == "dashed" else ""
        p.append(f'<path d="M {x1} {y1} C {mid} {y1}, {mid} {y2}, {x2} {y2}" '
                 f'fill="none" stroke="{PALETTE["ink"]}" stroke-width="1.6"'
                 f'{dash} marker-end="url(#arrow)"/>')
        if e.get("label"):
            p.append(f'<text x="{mid}" y="{(y1 + y2) / 2 - 7}" text-anchor="middle" '
                     f'font-family="{FONT}" font-size="12" fill="{PALETTE["muted"]}">'
                     f'{escape(e["label"])}</text>')

    for pl in placed.values():
        n = pl["node"]
        emph = n.get("emphasis") == "primary"
        p.append(f'<rect x="{pl["x"]}" y="{pl["y"]}" width="{pl["w"]}" '
                 f'height="{pl["h"]}" rx="3" fill="{PALETTE["fill"]}" '
                 f'stroke="{PALETTE["accent"] if emph else PALETTE["rule"]}" '
                 f'stroke-width="{2.2 if emph else 1.3}"/>')
        for i, line in enumerate(_wrap(n["label"], 24)):
            p.append(f'<text x="{pl["x"] + pl["w"] / 2}" '
                     f'y="{pl["y"] + pl["h"] / 2 + 5 + (i - (len(_wrap(n["label"], 24)) - 1) / 2) * 16}" '
                     f'text-anchor="middle" font-family="{FONT}" font-size="13.5" '
                     f'font-weight="{600 if emph else 400}" fill="{PALETTE["ink"]}">'
                     f'{escape(line)}</text>')

    p.append(f'<text x="24" y="{height - 16}" font-family="{FONT}" font-size="11" '
             f'fill="{PALETTE["muted"]}">Built from confirmed spec: '
             f'{escape(str(spec["source"]))}</text>')
    p.append("</svg>")
    return "\n".join(p)


def _wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = f"{cur} {w}".strip()
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines or [""]
