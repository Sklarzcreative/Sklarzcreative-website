"""Deterministic verdict engine.

The reviewing model supplies FINDINGS. Code computes the VERDICT. A model may
never declare a figure approved while blocking findings remain.
"""
from . import config, routing

PRODUCTION_READY_BASE_ART = "PRODUCTION_READY_BASE_ART"
REQUIRES_CORRECTION = "REQUIRES_CORRECTION"
SCIENTIFIC_VERIFICATION_REQUIRED = "SCIENTIFIC_VERIFICATION_REQUIRED"
HUMAN_CONFIRMATION_REQUIRED = "HUMAN_CONFIRMATION_REQUIRED"
REJECTED = "REJECTED"

# Findings that mean the artwork asserts science it is not entitled to assert.
FABRICATION_CATEGORIES = {"EMPIRICAL_DATA", "GENERATED_TEXT", "IMPLIED_PRECISION"}
SCIENCE_CATEGORIES = {"ANATOMY", "BOTANY", "CHEMISTRY", "GENETICS"} | FABRICATION_CATEGORIES


def compute(review, route, repair_count=0, cfg=None):
    """Return (verdict, rationale, counts). Pure function of the findings."""
    cfg = cfg or config.load()
    rc = cfg["review"]
    max_repairs = cfg["pipeline"]["max_generative_repairs"]

    issues = review.get("issues", [])
    blockers = [i for i in issues if i["severity"] in rc["blocker_severities"]]
    majors = [i for i in issues if i["severity"] in rc["major_severities"]]
    minors = [i for i in issues if i["severity"] == "MINOR"]

    fabrication = [i for i in issues
                   if i["category"] in FABRICATION_CATEGORIES
                   and i["severity"] in ("BLOCKER", "MAJOR")]
    science_major = [i for i in issues
                     if i["category"] in SCIENCE_CATEGORIES
                     and i["severity"] in ("BLOCKER", "MAJOR")]
    preserve_damage = [i for i in issues if i["category"] == "PRESERVE_DAMAGE"]
    needs_human = (review.get("human_confirmation_required")
                   or any(i["repair_type"] == "HUMAN_CONFIRMATION" for i in issues))

    counts = {"blockers": len(blockers), "majors": len(majors), "minors": len(minors),
              "fabrication": len(fabrication), "preserve_damage": len(preserve_damage)}

    # Fabricated data/text baked into a generated image is not repairable by editing.
    if fabrication:
        return REJECTED, (
            "Generated artwork asserts empirical data, scientific text or implied "
            "precision it is not entitled to assert."), counts

    if needs_human:
        return HUMAN_CONFIRMATION_REQUIRED, (
            "Reviewer flagged a decision that automation must not make."), counts

    if repair_count >= max_repairs and (blockers or majors):
        return REJECTED, (
            f"Generative repair cap ({max_repairs}) reached with unresolved issues."), counts

    if blockers:
        return REQUIRES_CORRECTION, "Blocking issues remain.", counts

    if science_major:
        return SCIENTIFIC_VERIFICATION_REQUIRED, (
            "Visually acceptable, but a scientific finding needs source "
            "confirmation before approval."), counts

    if len(majors) > rc["max_major_for_ready"]:
        return REQUIRES_CORRECTION, "Unresolved major issues.", counts

    if preserve_damage:
        return REQUIRES_CORRECTION, (
            "Repair damaged elements that were explicitly marked preserve."), counts

    # Route gate: a non-generative route can never be signed off by image review.
    if route in routing.BLOCKED_FROM_GENERATION:
        return HUMAN_CONFIRMATION_REQUIRED, (
            f"Route {route} is not approvable by image review alone."), counts

    if review.get("scientific_pass") is False:
        return SCIENTIFIC_VERIFICATION_REQUIRED, (
            "Reviewer withheld a scientific pass."), counts

    return PRODUCTION_READY_BASE_ART, "No blocking or major issues.", counts
