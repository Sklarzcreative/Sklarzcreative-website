"""Image-generation adapters (Agent 3 backend).

No provider SDK is required - everything goes over urllib so the pipeline runs
on a bare Python 3. Provider is selected in config.json.

STATUS IN THE AUTHORING ENVIRONMENT (2026-08-27): no image API key was present
and outbound calls to image endpoints were blocked, so 'dry-run' is the default.
Dry-run writes the exact request payload that WOULD be sent, so the prompt,
size and model are reviewable before a single credit is spent.
"""
import base64, json, os, urllib.request, urllib.error


class GenerationUnavailable(RuntimeError):
    pass


def _post(url, payload, headers, timeout=180):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise GenerationUnavailable(f"HTTP {e.code}: {e.read().decode()[:400]}")
    except Exception as e:
        raise GenerationUnavailable(f"{type(e).__name__}: {e}")


def generate(cfg, prompt, out_path, aspect_hint=""):
    """Returns (status, detail). status in {written, dry-run, unavailable}."""
    block = cfg["image_generation"]
    provider = block.get("provider", "dry-run")

    if provider == "dry-run":
        payload = {"_provider": "dry-run", "prompt": prompt, "aspect_hint": aspect_hint,
                   "would_write": out_path}
        with open(out_path + ".request.json", "w") as f:
            json.dump(payload, f, indent=2)
        return "dry-run", out_path + ".request.json"

    if provider == "manual":
        with open(out_path + ".prompt.txt", "w") as f:
            f.write(prompt)
        return "dry-run", out_path + ".prompt.txt"

    if provider == "openai":
        c = block["openai"]
        key = os.environ.get(c["api_key_env"])
        if not key:
            raise GenerationUnavailable(f"{c['api_key_env']} is not set")
        data = _post(c["endpoint"],
                     {"model": c["model"], "prompt": prompt,
                      "size": c.get("size", "1536x1024"),
                      "quality": c.get("quality", "high"), "n": 1},
                     {"Authorization": f"Bearer {key}"})
        b64 = data["data"][0]["b64_json"]
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(b64))
        return "written", out_path

    if provider == "gemini":
        c = block["gemini"]
        key = os.environ.get(c["api_key_env"])
        if not key:
            raise GenerationUnavailable(f"{c['api_key_env']} is not set")
        url = f"{c['endpoint']}/{c['model']}:generateContent?key={key}"
        data = _post(url, {"contents": [{"parts": [{"text": prompt}]}]}, {})
        for part in data["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(part["inlineData"]["data"]))
                return "written", out_path
        raise GenerationUnavailable("no image part in Gemini response")

    raise GenerationUnavailable(f"unknown provider {provider}")
