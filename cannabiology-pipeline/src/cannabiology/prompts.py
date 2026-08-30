"""Versioned prompt assembly. Prompt versions are never overwritten."""
import hashlib
import json
import time
from pathlib import Path

from . import workspace


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def assemble(asset, context=None, repair_prompt=None):
    """Base art prompt. Manual labels are RESERVED, never typeset by the model."""
    if repair_prompt:
        return repair_prompt
    parts = [asset["prompt"].strip()]
    if asset.get("manual_labels"):
        parts.append(
            "LAYOUT RESERVATION: leave clean, uncluttered callout space for these "
            "labels. They are applied afterwards as a deterministic vector layer and "
            "must NOT be typeset, lettered or hinted at in the generated image: "
            + "; ".join(asset["manual_labels"]) + ".")
    if context and context.get("scientific_cautions"):
        parts.append("SCIENTIFIC CONSTRAINTS: " + " ".join(context["scientific_cautions"]))
    if asset.get("negative"):
        parts.append("AVOID: " + asset["negative"].strip())
    return "\n\n".join(parts)


def save_version(run_dir, asset_id, text, meta):
    """Write an immutable prompt version and return its record."""
    d = workspace.assert_safe_write(Path(run_dir) / "prompts")
    d.mkdir(parents=True, exist_ok=True)
    existing = sorted(d.glob(f"{asset_id}_v*.json"))
    version = len(existing) + 1
    rec = {
        "asset_id": asset_id, "version": version, "created": _now(),
        "prompt_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "prompt": text, **meta,
    }
    path = d / f"{asset_id}_v{version:03d}.json"
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite prompt version {path}")
    with open(path, "w") as f:
        json.dump(rec, f, indent=2)
    rec["path"] = str(path)
    return rec
