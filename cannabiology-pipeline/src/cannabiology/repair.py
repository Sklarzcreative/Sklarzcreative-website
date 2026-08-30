"""Four-way repair taxonomy with an explicit preserve contract.

VECTOR_EDIT does not consume a generative repair round: correcting a label in
the overlay never re-rolls scientific artwork.
"""
from . import config, verdict as V

VECTOR_EDIT = "VECTOR_EDIT"
IMAGE_EDIT = "IMAGE_EDIT"
REGENERATE = "REGENERATE"
HUMAN_CONFIRMATION = "HUMAN_CONFIRMATION"

# Issue categories that live entirely in the deterministic overlay layer.
VECTOR_ONLY = {"LABEL_READINESS", "GENERATED_TEXT"}
# Categories that mean the base art itself is wrong at a structural level.
STRUCTURAL = {"ANATOMY", "BOTANY", "COMPOSITION", "HIERARCHY", "PURPOSE_FIDELITY"}


def plan(review, computed_verdict, state_rec, cfg=None):
    """Choose the least destructive correction that can actually fix the findings."""
    cfg = cfg or config.load()
    max_repairs = cfg["pipeline"]["max_generative_repairs"]
    issues = review.get("issues", [])
    actionable = [i for i in issues if i["severity"] in ("BLOCKER", "MAJOR")]

    preserve = list(review.get("preserve", []))

    if computed_verdict in (V.HUMAN_CONFIRMATION_REQUIRED, V.SCIENTIFIC_VERIFICATION_REQUIRED):
        return _mk(HUMAN_CONFIRMATION, actionable, preserve,
                   "Automation must not resolve this; it needs a human decision.", False)

    if computed_verdict == V.REJECTED:
        return _mk(HUMAN_CONFIRMATION, actionable, preserve,
                   "Candidate rejected; a human decides whether to rebuild.", False)

    if not actionable:
        return _mk("NONE", [], preserve, "Nothing actionable.", False)

    cats = {i["category"] for i in actionable}
    recommended = {i["repair_type"] for i in actionable}

    # Every actionable finding lives in the overlay -> deterministic fix, no re-roll.
    if cats <= VECTOR_ONLY or recommended == {VECTOR_EDIT}:
        return _mk(VECTOR_EDIT, actionable, preserve,
                   "All findings are in the vector overlay; base art is untouched.", False)

    if REGENERATE in recommended or (cats & STRUCTURAL and len(actionable) >= 3):
        action = REGENERATE
        reason = "Structure or teaching idea is wrong; editing is less reliable than rebuilding."
    else:
        action = IMAGE_EDIT
        reason = "Base art is largely correct; apply a local correction."

    if state_rec.get("generative_repairs", 0) >= max_repairs:
        return _mk(HUMAN_CONFIRMATION, actionable, preserve,
                   f"Generative repair cap ({max_repairs}) reached.", False)

    return _mk(action, actionable, preserve, reason, True)


def _mk(action, issues, preserve, reason, consumes):
    return {
        "action": action,
        "reason": reason,
        "consumes_generative_round": consumes,
        "preserve": preserve,
        "issues": [
            {"category": i["category"], "severity": i["severity"],
             "description": i["description"], "repair_type": i["repair_type"]}
            for i in issues
        ],
    }


def build_repair_prompt(base_prompt, plan_obj):
    """An edit prompt must always restate what must NOT change."""
    parts = [base_prompt.strip()]
    if plan_obj["issues"]:
        parts.append("CORRECT THE FOLLOWING, AND NOTHING ELSE:\n" + "\n".join(
            f"- [{i['severity']}/{i['category']}] {i['description']}"
            for i in plan_obj["issues"]))
    if plan_obj["preserve"]:
        parts.append("PRESERVE EXACTLY - these were reviewed and accepted, do not "
                     "alter, restyle, move or re-render them:\n" + "\n".join(
                         f"- {p}" for p in plan_obj["preserve"]))
    return "\n\n".join(parts)
