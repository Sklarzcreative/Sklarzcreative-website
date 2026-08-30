"""Chemical structure rendering from verified sources.

The hard rule: a structure is drawn ONLY from a registry entry carrying a
citation. Nothing is drawn from a model's memory of what a molecule looks like.

Two independent integrity checks run before anything renders:
  1. The SMILES must parse.
  2. The formula RDKit computes from the SMILES must match the formula recorded
     from the source. A transcription slip changes the formula and is caught.
"""
from pathlib import Path

import yaml

REQUIRED_PROVENANCE = ("source", "source_id", "retrieved", "molecular_formula")


class ChemistryError(RuntimeError):
    pass


class UnverifiedCompound(ChemistryError):
    """Raised when a compound has no citation. Always fail closed."""


def _rdkit():
    try:
        from rdkit import Chem
        from rdkit.Chem import rdMolDescriptors
        from rdkit.Chem.Draw import rdMolDraw2D
        return Chem, rdMolDescriptors, rdMolDraw2D
    except ImportError as e:
        raise ChemistryError(
            "RDKit is required to build chemical structures.\n"
            "  pip install rdkit") from e


def load_registry(path):
    p = Path(path)
    if not p.exists():
        raise ChemistryError(
            f"Chemical source registry not found: {p}\n"
            "Populate it from an authoritative source before building chemistry "
            "figures:  python -m cannabiology fetch-chem <name> --cid <pubchem-cid>")
    data = yaml.safe_load(p.read_text()) or {}
    return data.get("compounds", {}) or {}


def verify(name, entry):
    """Return the entry, or raise. A compound without full provenance never draws."""
    if entry is None:
        raise UnverifiedCompound(
            f"'{name}' is not in the chemical source registry.\n"
            "Structures are never drawn from memory. Add a verified entry first.")
    if entry.get("verified") is not True:
        raise UnverifiedCompound(
            f"'{name}' is present but not marked verified. A human must confirm "
            "the structure against the cited source and set verified: true.")
    missing = [k for k in REQUIRED_PROVENANCE if not entry.get(k)]
    if missing:
        raise UnverifiedCompound(
            f"'{name}' is missing required provenance: {', '.join(missing)}")
    if not entry.get("smiles"):
        raise UnverifiedCompound(f"'{name}' has no SMILES string")
    return entry


def check_formula(smiles, expected_formula):
    """Cross-check the drawing against the source. Catches transcription errors."""
    Chem, rdMolDescriptors, _ = _rdkit()
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ChemistryError(f"SMILES does not parse: {smiles!r}")
    actual = rdMolDescriptors.CalcMolFormula(mol)
    norm = lambda s: s.replace("+", "").replace("-", "").strip()
    if norm(actual) != norm(expected_formula):
        raise ChemistryError(
            f"Formula mismatch: SMILES yields {actual}, source records "
            f"{expected_formula}. The structure does not match its citation.")
    return mol, actual


def render(name, registry, width=420, height=340, add_stereo=True):
    """Render one verified compound to SVG. Returns (svg, provenance)."""
    entry = verify(name, registry.get(name))
    Chem, _, rdMolDraw2D = _rdkit()
    mol, formula = check_formula(entry["smiles"], entry["molecular_formula"])

    d = rdMolDraw2D.MolDraw2DSVG(width, height)
    opts = d.drawOptions()
    opts.addStereoAnnotation = add_stereo
    opts.bondLineWidth = 2
    rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
    d.FinishDrawing()
    svg = d.GetDrawingText()
    # Strip the XML prolog so the fragment can be composited into a page.
    if svg.startswith("<?xml"):
        svg = svg.split("?>", 1)[1].lstrip()

    provenance = {
        "compound": name,
        "display_name": entry.get("display_name", name),
        "smiles": entry["smiles"],
        "molecular_formula": formula,
        "source": entry["source"],
        "source_id": entry["source_id"],
        "retrieved": entry["retrieved"],
        "verified_by": entry.get("verified_by", ""),
        "renderer": "RDKit",
    }
    return svg, provenance


def render_panel(names, registry, cell_w=420, cell_h=340, cols=2, gap=24):
    """Multi-compound comparison plate. Every panel carries its own citation."""
    rows = (len(names) + cols - 1) // cols
    W = cols * cell_w + (cols + 1) * gap
    H = rows * (cell_h + 34) + (rows + 1) * gap
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}">',
             f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    provs = []
    for i, name in enumerate(names):
        svg, prov = render(name, registry, cell_w, cell_h)
        provs.append(prov)
        cx = gap + (i % cols) * (cell_w + gap)
        cy = gap + (i // cols) * (cell_h + 34 + gap)
        inner = svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
        parts.append(f'<g transform="translate({cx},{cy})">{inner}</g>')
        parts.append(
            f'<text x="{cx + cell_w / 2}" y="{cy + cell_h + 20}" text-anchor="middle" '
            f'font-family="IBM Plex Sans, Helvetica, sans-serif" font-size="14" '
            f'font-weight="600" fill="#14201a">{prov["display_name"]}</text>')
    parts.append("</svg>")
    return "\n".join(parts), provs
