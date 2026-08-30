"""Dry-run adapter. Records the exact call that WOULD be made. Never fabricates
a model result: generation writes a request payload and no pixels; review
returns a deterministic, clearly-labelled synthetic finding set for plumbing
tests only."""
import json
from pathlib import Path

NAME = "dry-run"


def generate(prompt, out_path, model, size, quality, **kw):
    payload = {"_adapter": NAME, "_note": "no API call was made",
               "model": model, "size": size, "quality": quality,
               "prompt": prompt, "would_write": str(out_path)}
    p = Path(str(out_path) + ".request.json")
    p.write_text(json.dumps(payload, indent=2))
    return {"status": "dry-run", "image_written": False,
            "request_path": str(p), "path": str(out_path), "model": model}


def edit(prompt, base_image, out_path, model, **kw):
    payload = {"_adapter": NAME, "_note": "no API call was made", "model": model,
               "base_image": str(base_image), "prompt": prompt,
               "would_write": str(out_path)}
    p = Path(str(out_path) + ".editrequest.json")
    p.write_text(json.dumps(payload, indent=2))
    return {"status": "dry-run", "image_written": False,
            "request_path": str(p), "path": str(out_path), "model": model}


def review(brief, image_path, model, **kw):
    """Synthetic review for plumbing tests. Marked so it can never be mistaken
    for a real OA result."""
    return {
        "figure_id": brief["asset_id"],
        "candidate_id": brief.get("candidate_id", "v001"),
        "review_round": brief.get("review_round", 1),
        "visual_pass": True, "scientific_pass": True, "confidence": 0.0,
        "issues": [], "preserve": [], "manual_overlay_required": brief.get("manual_labels", []),
        "human_confirmation_required": False, "recommended_action": "NONE",
        "repair_instructions": "",
        "summary": "SYNTHETIC DRY-RUN REVIEW - not a real OA result.",
        "_adapter": NAME, "_synthetic": True, "model": model,
    }
