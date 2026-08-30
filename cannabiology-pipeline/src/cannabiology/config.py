"""Configuration. Model IDs and thresholds live here, never inline in code."""
import os
from pathlib import Path

import yaml

PKG_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PKG_ROOT / "config"

_ENV_OVERRIDES = {
    "models.image_generate": "CANNABIOLOGY_IMAGE_MODEL",
    "models.image_edit": "CANNABIOLOGY_IMAGE_EDIT_MODEL",
    "models.oa_routine": "CANNABIOLOGY_OA_ROUTINE_MODEL",
    "models.oa_final": "CANNABIOLOGY_OA_FINAL_MODEL",
    "models.prompt_authoring": "CANNABIOLOGY_PROMPT_MODEL",
    "pipeline.max_concurrent_figures": "CANNABIOLOGY_MAX_CONCURRENT",
}


def _dig(d, dotted):
    cur = d
    for part in dotted.split("."):
        cur = cur[part]
    return cur


def _put(d, dotted, value):
    parts = dotted.split(".")
    for p in parts[:-1]:
        d = d.setdefault(p, {})
    d[parts[-1]] = value


def load(path=None):
    p = Path(path) if path else CONFIG_DIR / "pipeline.yaml"
    with open(p) as f:
        cfg = yaml.safe_load(f)
    for dotted, env in _ENV_OVERRIDES.items():
        val = os.environ.get(env)
        if val:
            try:
                cur = _dig(cfg, dotted)
                val = type(cur)(val) if isinstance(cur, int) else val
            except (KeyError, TypeError, ValueError):
                pass
            _put(cfg, dotted, val)
    return cfg


def routing_rules(path=None):
    p = Path(path) if path else CONFIG_DIR / "routing_rules.yaml"
    with open(p) as f:
        return yaml.safe_load(f)
