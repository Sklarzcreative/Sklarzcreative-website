"""OpenAI image generation / editing.

Uses the official SDK when installed, else a urllib fallback so the pipeline
runs on a bare Python 3. Never reads or stores a key beyond the environment.
"""
import base64
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

NAME = "openai"
API_BASE = "https://api.openai.com/v1"
KEY_ENV = "OPENAI_API_KEY"


class BackendUnavailable(RuntimeError):
    pass


def _key():
    k = os.environ.get(KEY_ENV)
    if not k:
        raise BackendUnavailable(
            f"{KEY_ENV} is not set. Run with --dry-run, or export the key in an "
            "authorized environment.")
    return k


def _post(path, payload):
    req = urllib.request.Request(
        f"{API_BASE}{path}", data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {_key()}"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise BackendUnavailable(f"HTTP {e.code}: {e.read().decode()[:400]}") from e
    except Exception as e:
        raise BackendUnavailable(f"{type(e).__name__}: {e}") from e


def _write_b64(data, out_path):
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(base64.b64decode(data))
    return p


def generate(prompt, out_path, model, size, quality, **kw):
    data = _post("/images/generations", {
        "model": model, "prompt": prompt, "size": size,
        "quality": quality, "n": 1})
    _write_b64(data["data"][0]["b64_json"], out_path)
    return {"status": "generated", "image_written": True,
            "path": str(out_path), "model": model,
            "usage": data.get("usage")}


def edit(prompt, base_image, out_path, model, size=None, **kw):
    """Image edit. Sends the prior candidate plus a preserve-constrained prompt."""
    b64 = base64.b64encode(Path(base_image).read_bytes()).decode()
    payload = {"model": model, "prompt": prompt,
               "image": [f"data:image/png;base64,{b64}"], "n": 1}
    if size:
        payload["size"] = size
    data = _post("/images/edits", payload)
    _write_b64(data["data"][0]["b64_json"], out_path)
    return {"status": "edited", "image_written": True,
            "path": str(out_path), "model": model}
