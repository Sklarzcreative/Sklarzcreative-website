"""OA (objective assessment) review adapters (Agent 4 backend).

Two paths, both real:

1. provider = "manual"  (default, works with zero API keys)
   Emits a review brief: the rubric, the figure's scientific requirements, the
   manual-label list and the negative constraints, next to the image file. A
   human - or a vision-capable model in the loop, e.g. an in-session Claude Code
   review of the image - fills in scores and drops back a verdict JSON.

2. provider = "anthropic" | "openai"
   Sends image + rubric to a vision model and parses a strict JSON verdict.
"""
import base64, json, mimetypes, os, urllib.request, urllib.error


class ReviewUnavailable(RuntimeError):
    pass


def build_brief(rubric, fig, prompt_row):
    """The single QA brief used by every reviewer, human or model."""
    return {
        "asset_id": prompt_row["Production Asset ID"],
        "figure_id": prompt_row["Figure ID"],
        "figure_title": prompt_row["Figure Title"],
        "chapter": prompt_row["Chapter"],
        "manuscript_section": prompt_row["Manuscript Section"],
        "educational_purpose": fig.get("Educational Purpose", ""),
        "visual_type": prompt_row["Visual Type"],
        "intended_page_treatment": prompt_row["Intended Page Treatment"],
        "aspect_ratio": prompt_row["Aspect Ratio"],
        "prompt_sent": prompt_row["Production Prompt"],
        "negative_constraints": prompt_row["Negative Constraints"],
        "scientific_accuracy_notes": prompt_row["Scientific Accuracy Notes"],
        "labels_to_add_manually": prompt_row["Manual Labels"],
        "rubric": rubric,
        "instructions": (
            "Score each rubric criterion 1-5. Return STRICT JSON only: "
            '{"scores":{"<key>":int,...},"findings":[{"criterion":str,"issue":str,'
            '"fix":str,"severity":"blocking|major|minor"}],"verdict":"PASS|'
            'PASS_WITH_MINOR_NOTES|REVISE|REGENERATE","summary":str,'
            '"open_scientific_flag":bool}. Apply verdict_rules exactly. '
            "Judge only what is visible in the image; do not assume intent."
        ),
    }


def _b64_image(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        return mime, base64.b64encode(f.read()).decode()


def review(cfg, rubric, fig, prompt_row, image_path):
    """Returns (status, verdict_dict_or_brief_path)."""
    block = cfg["oa_review"]
    provider = block.get("provider", "manual")
    brief = build_brief(rubric, fig, prompt_row)

    if provider == "manual":
        p = os.path.splitext(image_path)[0] + ".review-brief.json"
        with open(p, "w") as f:
            json.dump(brief, f, indent=2)
        return "brief-emitted", p

    if not os.path.exists(image_path):
        raise ReviewUnavailable(f"no image to review at {image_path}")
    mime, b64 = _b64_image(image_path)

    if provider == "anthropic":
        c = block["anthropic"]
        key = os.environ.get(c["api_key_env"])
        if not key:
            raise ReviewUnavailable(f"{c['api_key_env']} is not set")
        payload = {
            "model": c["model"], "max_tokens": 2000,
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64",
                 "media_type": mime, "data": b64}},
                {"type": "text", "text": json.dumps(brief)},
            ]}],
        }
        req = urllib.request.Request(
            c["endpoint"], data=json.dumps(payload).encode(), method="POST",
            headers={"Content-Type": "application/json", "x-api-key": key,
                     "anthropic-version": "2023-06-01"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode())
            text = "".join(b.get("text", "") for b in data["content"])
        except Exception as e:
            raise ReviewUnavailable(f"{type(e).__name__}: {e}")
        return "reviewed", _parse_json(text)

    raise ReviewUnavailable(f"unknown provider {provider}")


def _parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].lstrip("json").strip()
    return json.loads(text)


def score_to_verdict(rubric, scores):
    """Deterministic verdict from scores - the same rules a model is told to apply.

    Kept in code so a model's stated verdict can be cross-checked against the
    arithmetic, and so a human review needs only the numbers.
    """
    crit = {c["key"]: c for c in rubric["criteria"]}
    if any(k not in scores for k in crit):
        missing = sorted(set(crit) - set(scores))
        raise ValueError(f"missing scores for: {missing}")
    total_w = sum(c["weight"] for c in crit.values())
    weighted = sum(scores[k] * crit[k]["weight"] for k in crit) / (5.0 * total_w)
    gates_unmet = [k for k, c in crit.items() if scores[k] < c["hard_gate"]]

    if (any(scores[k] <= 2 for k in crit)
            or scores["scientific_plausibility"] <= 3
            or scores["concept_fidelity"] <= 2):
        verdict = "REGENERATE"
    elif gates_unmet:
        verdict = "REVISE"
    elif weighted >= 0.85:
        verdict = "PASS"
    else:
        verdict = "PASS_WITH_MINOR_NOTES"
    return {"verdict": verdict, "weighted_score": round(weighted, 3),
            "gates_unmet": gates_unmet}
