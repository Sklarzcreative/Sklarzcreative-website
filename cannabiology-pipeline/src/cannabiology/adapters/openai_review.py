"""OA reviewer: a real OpenAI call with image input plus manuscript context.

Claude's own opinion is never an OA review. If this backend cannot run, the
pipeline reports that plainly rather than substituting a judgement.
"""
import base64
import json
import mimetypes
import os
import urllib.request
import urllib.error
from pathlib import Path

NAME = "openai"
API_BASE = "https://api.openai.com/v1"
KEY_ENV = "OPENAI_API_KEY"


class BackendUnavailable(RuntimeError):
    pass


SYSTEM = (
    "You are the OA reviewer for a university-level science textbook. You are "
    "given a candidate figure, the manuscript context it must serve, and the "
    "project's scientific rules. Judge only what is visible. Never approve a "
    "figure that asserts empirical values, chemical structures, gene names or "
    "regulatory facts it was not given a verified source for. Report findings; "
    "the pipeline computes the verdict. Return STRICT JSON only, matching the "
    "provided schema."
)


def _key():
    k = os.environ.get(KEY_ENV)
    if not k:
        raise BackendUnavailable(f"{KEY_ENV} is not set.")
    return k


def review(brief, image_path, model, schema=None, **kw):
    p = Path(image_path)
    if not p.exists():
        raise BackendUnavailable(
            f"No candidate image at {p}. OA review requires a real image; it will "
            "not review a request payload.")
    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode()

    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": SYSTEM}]},
            {"role": "user", "content": [
                {"type": "input_text", "text": json.dumps(brief, indent=2)},
                {"type": "input_image", "image_url": f"data:{mime};base64,{b64}"},
            ]},
        ],
    }
    if schema:
        payload["text"] = {"format": {"type": "json_schema", "name": "oa_review",
                                      "schema": schema, "strict": False}}

    req = urllib.request.Request(
        f"{API_BASE}/responses", data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {_key()}"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise BackendUnavailable(f"HTTP {e.code}: {e.read().decode()[:400]}") from e
    except Exception as e:
        raise BackendUnavailable(f"{type(e).__name__}: {e}") from e

    text = _extract_text(data)
    return _parse(text)


def _extract_text(data):
    if isinstance(data.get("output_text"), str):
        return data["output_text"]
    chunks = []
    for item in data.get("output", []):
        for c in item.get("content", []):
            if c.get("type") in ("output_text", "text") and c.get("text"):
                chunks.append(c["text"])
    if not chunks:
        raise BackendUnavailable("No text content in review response")
    return "".join(chunks)


def _parse(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        text = text[4:] if text.startswith("json") else text
    return json.loads(text.strip())
