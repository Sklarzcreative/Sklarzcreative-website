"""Canonical tracker access. READ-ONLY.

The canonical tracker is authoritative input produced by the project team.
Nothing in the automated loop may mutate it. Pipeline state lives separately
(see state.py) and is reconciled back only by an explicit human-run operation.
"""
import csv
import re
from dataclasses import dataclass, field

from . import workspace

# Canonical identifiers are fixed by the manuscript, QA register and layout specs.
FIGURE_ID_RE = re.compile(r"^CH(\d{2})-IMG-(\d{2})$")
ASSET_ID_RE = re.compile(r"^CH(\d{2})-IMG-(\d{2})([A-Z])?$")

TRACKER_FILE = "master-figure-tracker.csv"
PROMPTS_FILE = "prompt-library.csv"


class CanonicalError(RuntimeError):
    pass


@dataclass
class Figure:
    figure_id: str
    chapter: str
    title: str
    purpose: str
    visual_type: str
    status: str
    prompt: str
    negative: str
    science_notes: str
    manual_labels: list
    caption: str
    aspect: str
    page_treatment: str
    approval: str
    manuscript_section: str
    source_manuscript: str
    assets: list = field(default_factory=list)


def canonical_dir():
    return workspace.resolve() / "canonical" / "tracker_snapshot"


def _labels(raw):
    return [x.strip() for x in (raw or "").split(";") if x.strip()]


def validate_figure_id(fid):
    if not FIGURE_ID_RE.match(fid or ""):
        raise CanonicalError(
            f"Invalid canonical figure ID {fid!r}. Canonical IDs are CHnn-IMG-nn "
            "and must never be renamed (they are embedded in the manuscript)."
        )
    return fid


def validate_asset_id(aid, parent):
    if not ASSET_ID_RE.match(aid or ""):
        raise CanonicalError(f"Invalid production asset ID {aid!r}.")
    if not aid.startswith(parent):
        raise CanonicalError(
            f"Asset {aid!r} does not carry its parent figure ID {parent!r}. "
            "Sub-assets must extend the canonical ID (e.g. CH01-IMG-02A)."
        )
    return aid


def load_figures(directory=None):
    """Return {figure_id: Figure} with production assets attached."""
    d = directory or canonical_dir()
    tpath, ppath = d / TRACKER_FILE, d / PROMPTS_FILE
    if not tpath.exists():
        raise CanonicalError(
            f"Canonical tracker not found at {tpath}.\n"
            "Import it from the project's Google Drive '00 Master Control' folder:\n"
            "  python -m cannabiology doctor --init-workspace"
        )
    figures = {}
    with open(tpath) as f:
        for row in csv.DictReader(f):
            fid = validate_figure_id(row["Figure ID"].strip())
            if fid in figures:
                raise CanonicalError(f"Duplicate figure ID in tracker: {fid}")
            figures[fid] = Figure(
                figure_id=fid,
                chapter=row["Chapter"].strip(),
                title=row["Figure Title"].strip(),
                purpose=row["Educational Purpose"].strip(),
                visual_type=row["Visual Type"].strip(),
                status=row["Current Status"].strip(),
                prompt=row["Exact Production Prompt"].strip(),
                negative=row["Negative Constraints"].strip(),
                science_notes=row["Scientific Accuracy Notes"].strip(),
                manual_labels=_labels(row["Labels to Add Manually"]),
                caption=row["Caption Requirements"].strip(),
                aspect=row["Aspect Ratio"].strip(),
                page_treatment=row["Intended Page Treatment"].strip(),
                approval=row["Approval Status"].strip(),
                manuscript_section=row["Manuscript Section"].strip(),
                source_manuscript=row["Source Manuscript"].strip(),
            )
    if ppath.exists():
        with open(ppath) as f:
            for row in csv.DictReader(f):
                fid = row["Figure ID"].strip()
                aid = row["Production Asset ID"].strip()
                if fid not in figures:
                    raise CanonicalError(f"Prompt asset {aid} has no parent figure {fid}")
                validate_asset_id(aid, fid)
                figures[fid].assets.append({
                    "asset_id": aid,
                    "asset_title": row.get("Asset Title", "").strip(),
                    "prompt": row["Production Prompt"].strip(),
                    "negative": row["Negative Constraints"].strip(),
                    "science_notes": row["Scientific Accuracy Notes"].strip(),
                    "manual_labels": _labels(row.get("Manual Labels", "")),
                    "caption": row.get("Caption Requirements", "").strip(),
                    "aspect": row.get("Aspect Ratio", "").strip(),
                })
    for fig in figures.values():
        if not fig.assets:
            fig.assets.append({
                "asset_id": fig.figure_id, "asset_title": fig.title,
                "prompt": fig.prompt, "negative": fig.negative,
                "science_notes": fig.science_notes,
                "manual_labels": fig.manual_labels, "caption": fig.caption,
                "aspect": fig.aspect,
            })
    return figures
