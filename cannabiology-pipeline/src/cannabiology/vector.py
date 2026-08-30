"""Deterministic vector annotation and compositing.

Generated base art carries no authoritative text. Labels, leaders, panel letters,
scale bars and captions are built here as SVG and composited over the base image.

A spelling error therefore costs an SVG rewrite, never a regeneration.
Output is byte-deterministic: identical inputs produce identical SVG.
"""
import base64
import json
import mimetypes
from pathlib import Path
from xml.sax.saxutils import escape

from . import workspace

FONT = "IBM Plex Sans, Helvetica, Arial, sans-serif"


def default_layout(labels, width, height, margin=24, line_h=22):
    """Place labels down the right-hand reserve column, deterministically."""
    col_x = int(width * 0.72)
    out = []
    for i, text in enumerate(labels):
        y = margin + line_h * (i + 1)
        out.append({
            "text": text, "x": col_x, "y": min(y, height - margin),
            "leader": {"x1": col_x - 12, "y1": min(y, height - margin) - 5,
                       "x2": int(width * 0.55), "y2": min(y, height - margin) - 5},
        })
    return out


def build_layer(labels, width, height, layout=None, panel_letters=None,
                figure_number=None, caption=None, scale_bar=None):
    """Return the annotation-only SVG layer (no base image)."""
    items = layout or default_layout(labels, width, height)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<g id="annotations" font-family="{FONT}" font-size="13" fill="#14201a">',
    ]
    for it in items:
        ldr = it.get("leader")
        if ldr:
            parts.append(
                f'<line x1="{ldr["x1"]}" y1="{ldr["y1"]}" x2="{ldr["x2"]}" '
                f'y2="{ldr["y2"]}" stroke="#14201a" stroke-width="1"/>')
        parts.append(
            f'<text x="{it["x"]}" y="{it["y"]}">{escape(it["text"])}</text>')
    for pl in (panel_letters or []):
        parts.append(
            f'<text x="{pl["x"]}" y="{pl["y"]}" font-size="18" '
            f'font-weight="700">{escape(pl["text"])}</text>')
    if scale_bar:
        sb = scale_bar
        parts.append(
            f'<line x1="{sb["x"]}" y1="{sb["y"]}" x2="{sb["x"] + sb["length"]}" '
            f'y2="{sb["y"]}" stroke="#14201a" stroke-width="3"/>')
        parts.append(
            f'<text x="{sb["x"]}" y="{sb["y"] - 6}" font-size="12">'
            f'{escape(sb["label"])}</text>')
    if figure_number:
        parts.append(
            f'<text x="24" y="{height - 34}" font-size="13" font-weight="700">'
            f'{escape(figure_number)}</text>')
    if caption:
        parts.append(
            f'<text x="24" y="{height - 14}" font-size="12" fill="#3d4a41">'
            f'{escape(caption)}</text>')
    parts.append("</g></svg>")
    return "\n".join(parts)


def composite(base_image_path, layer_svg, width, height):
    """Self-contained SVG: base raster embedded as a data URI, overlay on top."""
    p = Path(base_image_path)
    if p.exists():
        mime = mimetypes.guess_type(str(p))[0] or "image/png"
        href = f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
    else:
        href = ""
    inner = layer_svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
    img = (f'<image href="{href}" x="0" y="0" width="{width}" height="{height}"/>'
           if href else
           f'<rect x="0" y="0" width="{width}" height="{height}" fill="#f1f3ed"/>'
           f'<text x="24" y="32" font-family="{FONT}" font-size="14" fill="#68746b">'
           f'base art not generated</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">{img}{inner}</svg>')


def write_layer(run_dir, asset_id, labels, width, height, **kw):
    """Write layer SVG + label manifest. Returns (svg_path, manifest_path)."""
    d = workspace.assert_safe_write(Path(run_dir) / "vector")
    d.mkdir(parents=True, exist_ok=True)
    version = len(list(d.glob(f"{asset_id}_labels_v*.svg"))) + 1
    svg = build_layer(labels, width, height, **kw)
    svg_path = d / f"{asset_id}_labels_v{version:03d}.svg"
    svg_path.write_text(svg)
    manifest = {
        "asset_id": asset_id, "version": version, "width": width, "height": height,
        "labels": labels, "label_count": len(labels),
        "source": "canonical tracker 'Labels to Add Manually'",
        "authoritative_text_in_base_art": False,
    }
    man_path = d / f"{asset_id}_labels_v{version:03d}.manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2))
    return svg_path, man_path
