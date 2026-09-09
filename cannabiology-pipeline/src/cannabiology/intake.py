"""Intake gate for artwork drawn outside this pipeline.

Base art for HYBRID figures is commissioned from an external illustrator or
image model. That artwork carries none of the guarantees the deterministic
builder provides: no per-node citation, no provenance, no test that measures
where its text lands. This module supplies the missing checks, so anything
arriving from outside is held to the same standard as anything built inside.

It refuses rather than repairs. A figure that fails here is reported, not
fixed, because the fix is a decision for the author or the illustrator.

Nothing here approves anything. Ingested artwork enters at CANDIDATE_READY,
whose only exit is OA_REVIEW.
"""
import hashlib
import json
import re
from datetime import date
from pathlib import Path

from . import canonical, routing, state as st, svgtext, workspace
from .vectorbuild import _norm

RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}

# Matches a number carrying a unit, which is the shape of the invented data the
# tracker's negative constraints forbid: "18%", "35 °C", "300 bar", "n=120".
UNIT_NUMBER = re.compile(
    r"\b\d[\d,.]*\s*(%|nm|µm|um|mm|cm|kDa|kb|bp|mg|ml|mL|µL|uL|g\b|kg|"
    r"°\s*[CF]|bar|psi|rpm|Hz|kHz|mM|µM|uM|nM|ppm|mol|kcal|kJ)", re.I)
SAMPLE_SIZE = re.compile(r"\bn\s*=\s*\d+", re.I)
# Four or more contiguous unambiguous bases reads as a real sequence.
SEQUENCE = re.compile(r"\b[ACGTU]{4,}\b")

# The decision record the commission brief asks the illustrator to return.
REQUIRED_RECORD_FIELDS = ("FIGURE", "DREW", "DEPARTURES", "NOT DRAWN")


class IntakeRefused(RuntimeError):
    pass


class Finding:
    __slots__ = ("level", "code", "detail")

    def __init__(self, level, code, detail):
        self.level, self.code, self.detail = level, code, detail

    def __repr__(self):
        return f"{self.level}: {self.code} - {self.detail}"

    def as_dict(self):
        return {"level": self.level, "code": self.code, "detail": self.detail}


def _fail(code, detail):
    return Finding("FAIL", code, detail)


def _warn(code, detail):
    return Finding("WARN", code, detail)


def parse_record(text):
    """Read the illustrator's decision record into a dict of FIELD -> value."""
    fields, current = {}, None
    for line in (text or "").splitlines():
        m = re.match(r"^([A-Z][A-Z ]{2,20}):\s*(.*)$", line)
        if m:
            current = m.group(1).strip()
            fields[current] = m.group(2).strip()
        elif current and line.strip():
            fields[current] += " " + line.strip()
    return fields


def check_record(record_text):
    """The record is the fix for silent substitution, so its absence is fatal."""
    if not (record_text or "").strip():
        return [_fail("record.missing",
                      "no decision record supplied. Artwork without a record "
                      "cannot be distinguished from artwork that silently "
                      "changed the brief.")]
    fields = parse_record(record_text)
    out = []
    for name in REQUIRED_RECORD_FIELDS:
        if name not in fields:
            out.append(_fail("record.field_missing", f"record has no {name}: field"))
        elif not fields[name]:
            out.append(_fail("record.field_empty", f"record field {name}: is empty"))
    dep = fields.get("DEPARTURES", "").strip().lower()
    if dep in ("none", "n/a", "-"):
        out.append(_warn("record.no_departures",
                         "record claims no departures from the brief. Verify "
                         "against the brief before trusting it."))
    return out


def check_geometry(svg, footer_reserve=96):
    """Text off the canvas, or inside the strip the caption is composited into."""
    out = []
    width, height = svgtext.canvas(svg)
    floor = height - footer_reserve
    for b in svgtext.text_boxes(svg):
        if b["left"] < 0:
            out.append(_fail("geometry.off_canvas_left",
                             f"{b['text']!r} starts at x={b['left']:.0f}"))
        if b["right"] > width:
            out.append(_fail("geometry.off_canvas_right",
                             f"{b['text']!r} ends at x={b['right']:.0f} "
                             f"of {width:.0f}"))
        if b["y"] > height or b["y"] < 0:
            out.append(_fail("geometry.off_canvas_vertical",
                             f"{b['text']!r} sits at y={b['y']:.0f} "
                             f"of {height:.0f}"))
        elif b["y"] > floor:
            out.append(_fail("geometry.in_caption_strip",
                             f"{b['text']!r} at y={b['y']:.0f} is inside the "
                             f"caption strip below y={floor:.0f}"))
    return out


def check_asserted_text(svg, required_labels):
    """Base art must not print the labels we overlay from verified sources.

    A label printed by the illustrator looks identical to one we verified, and
    nobody downstream can tell the difference. That is the whole reason HYBRID
    artwork is drawn wordless.
    """
    # Match against rejoined blocks as well as individual runs: a label wrapped
    # across two tspans is two runs but one phrase, and would otherwise pass.
    drawn = " | ".join(_norm(t) for t in
                       list(svgtext.all_text(svg)) + list(svgtext.text_blocks(svg)))
    out = []
    for label in required_labels:
        for part in [p.strip() for p in re.split(r"[/;,]", label) if p.strip()]:
            n = _norm(part)
            if len(n) >= 4 and n in drawn:
                out.append(_fail("text.asserted_label",
                                 f"artwork prints {part!r}, which is on the "
                                 "manual-label list and must be overlaid from "
                                 "a verified source"))
                break
    return out


def check_invented_data(svg):
    """Numbers with units, sample sizes and readable sequences."""
    out = []
    for t in svgtext.all_text(svg):
        for rx, code, what in ((UNIT_NUMBER, "data.unit_number", "a number with a unit"),
                               (SAMPLE_SIZE, "data.sample_size", "a sample size"),
                               (SEQUENCE, "data.sequence", "a readable base sequence")):
            m = rx.search(t)
            if m:
                out.append(_fail(code, f"artwork prints {m.group(0)!r} ({what}) "
                                       f"in: {t[:70]!r}"))
    return out


def check_route(figure, decision):
    """A figure on HOLD is waiting on a decision. Drawing it does not settle it."""
    out = []
    if decision.route == "HOLD":
        out.append(_fail("route.hold",
                         f"{figure.figure_id} is on HOLD: {figure.status!r}. The "
                         "hold is a question for the author; artwork does not "
                         "answer it."))
    elif decision.route not in ("HYBRID", "GENERATE"):
        out.append(_warn("route.unexpected",
                         f"{figure.figure_id} is routed {decision.route}, which "
                         "this pipeline draws itself. Ingesting external artwork "
                         "here duplicates work and bypasses per-node citation."))
    if decision.needs_route_confirmation:
        out.append(_warn("route.unconfirmed",
                         f"{figure.figure_id} is on a derived {decision.route} "
                         "route the author has not confirmed. The figure may "
                         "change before it is final."))
    return out


def inspect(path, figure, decision, record_text, footer_reserve=96):
    """Run every check that applies to this file. Returns a list of Findings."""
    path = Path(path)
    findings = list(check_route(figure, decision)) + list(check_record(record_text))
    suffix = path.suffix.lower()

    if suffix == ".svg":
        svg = path.read_text(errors="replace")
        try:
            findings += check_geometry(svg, footer_reserve)
            findings += check_asserted_text(svg, figure.manual_labels)
            findings += check_invented_data(svg)
        except svgtext.MalformedSVG as e:
            findings.append(_fail("file.malformed", str(e)))
    elif suffix in RASTER_SUFFIXES:
        findings.append(_warn(
            "file.raster_not_inspected",
            "raster artwork: the text, geometry and invented-data checks cannot "
            "run on pixels. A human must confirm by eye that the artwork prints "
            "no labels, no numbers and nothing in the caption strip."))
    else:
        findings.append(_fail("file.unsupported",
                              f"unsupported artwork format {suffix!r}"))
    return findings


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ingest(figure_id, art_path, record_path=None, drawn_by="external",
           store=None, log=print, force_notes=None):
    """Check externally drawn artwork and, if it passes, admit it for review.

    Never approves. On success the artifact sits at CANDIDATE_READY, whose only
    onward transition is OA_REVIEW.
    """
    art_path = Path(art_path)
    if not art_path.exists():
        raise IntakeRefused(f"no such artwork file: {art_path}")
    record_text = Path(record_path).read_text(errors="replace") if record_path else ""

    figures = canonical.load_figures()
    if figure_id not in figures:
        raise IntakeRefused(f"{figure_id} is not in the canonical tracker")
    figure = figures[figure_id]
    decision = routing.Router().route(figure)

    findings = inspect(art_path, figure, decision, record_text)
    fails = [f for f in findings if f.level == "FAIL"]
    for f in findings:
        log(f"  [{f.level}] {f.code}: {f.detail}")

    if fails:
        raise IntakeRefused(
            f"{figure_id}: {len(fails)} blocking finding(s). Artwork not admitted.")

    ws = workspace.resolve()
    dest_dir = ws / "inbound" / "accepted" / figure_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / art_path.name
    workspace.assert_safe_write(dest)
    dest.write_bytes(art_path.read_bytes())

    provenance = {
        "figure_id": figure_id,
        "drawn_by": drawn_by,
        "ingested_on": date.today().isoformat(),
        "source_filename": art_path.name,
        "sha256": digest(art_path),
        "route": decision.route,
        "route_confirmed": not decision.needs_route_confirmation,
        "decision_record": parse_record(record_text),
        "findings": [f.as_dict() for f in findings],
        "checks_that_could_not_run": [
            f.code for f in findings if f.code == "file.raster_not_inspected"],
        "notes": force_notes or "",
    }
    prov_path = dest_dir / f"{figure_id}_intake_provenance.json"
    workspace.assert_safe_write(prov_path)
    prov_path.write_text(json.dumps(provenance, indent=2))
    log(f"  accepted: {dest}")
    log(f"  provenance: {prov_path}")
    return {"artwork": dest, "provenance": prov_path, "findings": findings}
