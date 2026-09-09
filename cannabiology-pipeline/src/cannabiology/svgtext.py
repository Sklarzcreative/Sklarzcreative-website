"""Measure where text actually lands in an SVG.

Text-based review cannot see geometry. Four figures reached APPROVED with text
running off the canvas or printing underneath the caption, because every check
compared strings and none measured position. This module is the shared
measurement used by the builder's tests and by the intake gate, so artwork drawn
outside the pipeline is held to the same standard as artwork drawn inside it.
"""
import re
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"

# Advance width per character as a fraction of font size. Deliberately generous:
# it is used to decide whether text fits, so overestimating raises a false alarm
# a human can dismiss, while underestimating ships a clipped figure.
EM = 0.66

# Default when a foreign SVG leaves font-size to inherit.
DEFAULT_FONT_SIZE = 13.0


class MalformedSVG(ValueError):
    pass


def _tag(el):
    return el.tag.split("}")[-1] if "}" in el.tag else el.tag


def _num(v, fallback=None):
    if v is None:
        return fallback
    m = re.match(r"\s*(-?[\d.]+)", str(v))
    return float(m.group(1)) if m else fallback


def canvas(svg):
    """Return (width, height) from the root element, preferring viewBox."""
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as e:
        raise MalformedSVG(f"not parseable as XML: {e}") from e
    vb = root.get("viewBox")
    if vb:
        parts = [p for p in re.split(r"[,\s]+", vb.strip()) if p]
        if len(parts) == 4:
            return float(parts[2]), float(parts[3])
    w, h = _num(root.get("width")), _num(root.get("height"))
    if w is None or h is None:
        raise MalformedSVG("no viewBox and no numeric width/height on <svg>")
    return w, h


def text_boxes(svg):
    """Every run of text with its approximate bounding box.

    Handles <tspan>, which foreign SVGs use for wrapped lines: sibling tspans
    stack by their dy, so each becomes its own measured line rather than the
    parent being measured as one long run. font-size and text-anchor inherit
    from ancestor <g> and <svg> elements, as they do when a renderer draws it.
    """
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as e:
        raise MalformedSVG(f"not parseable as XML: {e}") from e

    out = []
    INHERIT = ("font-size", "text-anchor")
    block = [0]   # runs from one <text> element share a block id

    def measure(body, size, x, anchor, y):
        w = len(body) * size * EM
        left = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
        out.append({"text": body, "size": size, "x": x, "y": y, "block": block[0],
                    "left": left, "right": left + w,
                    "top": y - size * 0.8, "bottom": y + size * 0.25})

    def handle_text(el, inherited):
        block[0] += 1
        style = {**inherited, **{k: el.get(k) for k in INHERIT if el.get(k) is not None}}
        size = _num(style.get("font-size"), DEFAULT_FONT_SIZE)
        anchor = style.get("text-anchor", "start")
        x = _num(el.get("x"), 0.0)
        y = _num(el.get("y"), 0.0)
        if (el.text or "").strip():
            measure(el.text.strip(), size, x, anchor, y)
        run_y = y
        for child in el:
            if _tag(child) != "tspan":
                continue
            c_size = _num(child.get("font-size"), size)
            c_anchor = child.get("text-anchor", anchor)
            c_x = _num(child.get("x"), x)
            if child.get("y") is not None:
                run_y = _num(child.get("y"), run_y)
            run_y += _num(child.get("dy"), 0.0) or 0.0
            if (child.text or "").strip():
                measure(child.text.strip(), c_size, c_x, c_anchor, run_y)
            # tail text after a nested tspan belongs to the parent run
            if (child.tail or "").strip():
                measure(child.tail.strip(), size, x, anchor, run_y)

    def walk(el, inherited):
        style = {**inherited,
                 **{k: el.get(k) for k in INHERIT if el.get(k) is not None}}
        if _tag(el) == "text":
            handle_text(el, inherited)
            return
        for child in el:
            walk(child, style)

    walk(root, {})
    return out


def all_text(svg):
    return [b["text"] for b in text_boxes(svg)]


def text_blocks(svg):
    """Runs rejoined per <text> element.

    A label wrapped across two tspans ("Independent" / "targets") is two runs
    but one phrase. Checks that look for a phrase must see the phrase, or a
    wrapped label slips through.
    """
    joined = {}
    for b in text_boxes(svg):
        joined.setdefault(b["block"], []).append(b["text"])
    return [" ".join(v) for _, v in sorted(joined.items())]
