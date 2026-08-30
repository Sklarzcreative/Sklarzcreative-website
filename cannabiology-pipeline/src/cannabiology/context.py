"""Deterministic manuscript context extraction.

A reviewer given only an image is judging plausibility, not manuscript accuracy.
This pulls the minimum relevant source text per figure - never whole chapters -
and persists it in the private workspace with a source hash.
"""
import hashlib
import json
import re
import time
from pathlib import Path

from . import workspace

ANCHOR_RE_TMPL = r"\*\*Image asset {fid}[a-zA-Z]?:?\*\*"
HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def manuscript_dir():
    return workspace.resolve() / "canonical" / "manuscript_sources"


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def find_anchor(lines, figure_id):
    pat = re.compile(ANCHOR_RE_TMPL.format(fid=re.escape(figure_id)), re.I)
    for i, ln in enumerate(lines):
        if pat.search(ln):
            return i
    return None


def enclosing_heading(lines, idx):
    for j in range(idx, -1, -1):
        m = HEADING_RE.match(lines[j])
        if m:
            return m.group(1).strip(), j
    return None, None


def extract(figure, before=40, after=12, sources=None):
    """Return a context extract dict for one canonical figure."""
    src_dir = manuscript_dir()
    files = sources or sorted(src_dir.glob("*.md")) if src_dir.exists() else []
    found = None
    for path in files:
        text = Path(path).read_text()
        lines = text.split("\n")
        idx = find_anchor(lines, figure.figure_id)
        if idx is None:
            continue
        heading, hidx = enclosing_heading(lines, idx)
        start = max(0, min(idx - before, hidx if hidx is not None else idx))
        excerpt = "\n".join(lines[start:idx + after]).strip()
        found = {
            "source_file": Path(path).name,
            "source_sha256_16": _sha(text),
            "anchor_line": idx + 1,
            "line_range": [start + 1, min(len(lines), idx + after)],
            "enclosing_heading": heading,
            "excerpt": excerpt,
            "figure_brief": lines[idx].strip(),
        }
        break

    return {
        "figure_id": figure.figure_id,
        "extracted_at": _now(),
        "manuscript_section": figure.manuscript_section,
        "educational_purpose": figure.purpose,
        "scientific_cautions": [figure.science_notes] if figure.science_notes else [],
        "manual_labels": figure.manual_labels,
        "caption_requirements": figure.caption,
        "source": found,
        "source_found": bool(found),
    }


def save(ctx, figure_id):
    d = workspace.assert_safe_write(workspace.resolve() / "context" / figure_id)
    d.mkdir(parents=True, exist_ok=True)
    version = len(list(d.glob("context_v*.json"))) + 1
    path = d / f"context_v{version:03d}.json"
    ctx["version"] = version
    with open(path, "w") as f:
        json.dump(ctx, f, indent=2)
    return path, version
