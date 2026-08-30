"""Minimal JSON Schema validation.

Uses the `jsonschema` package when installed; otherwise falls back to a
stdlib validator covering the subset used by the OA schema. Keeping this
dependency-free means review output is always validated, never waved through.
"""
import json
import re
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"


class ValidationError(ValueError):
    pass


def load_schema(name):
    with open(SCHEMA_DIR / name) as f:
        return json.load(f)


def _check(node, schema, path="$"):
    t = schema.get("type")
    if t == "object":
        if not isinstance(node, dict):
            raise ValidationError(f"{path}: expected object")
        for req in schema.get("required", []):
            if req not in node:
                raise ValidationError(f"{path}: missing required field {req!r}")
        for k, sub in schema.get("properties", {}).items():
            if k in node:
                _check(node[k], sub, f"{path}.{k}")
    elif t == "array":
        if not isinstance(node, list):
            raise ValidationError(f"{path}: expected array")
        if "items" in schema:
            for i, item in enumerate(node):
                _check(item, schema["items"], f"{path}[{i}]")
    elif t == "string":
        if not isinstance(node, str):
            raise ValidationError(f"{path}: expected string")
        if "enum" in schema and node not in schema["enum"]:
            raise ValidationError(f"{path}: {node!r} not in {schema['enum']}")
        if "pattern" in schema and not re.match(schema["pattern"], node):
            raise ValidationError(f"{path}: {node!r} fails pattern {schema['pattern']}")
    elif t == "integer":
        if not isinstance(node, int) or isinstance(node, bool):
            raise ValidationError(f"{path}: expected integer")
        if "minimum" in schema and node < schema["minimum"]:
            raise ValidationError(f"{path}: {node} < minimum {schema['minimum']}")
    elif t == "number":
        if not isinstance(node, (int, float)) or isinstance(node, bool):
            raise ValidationError(f"{path}: expected number")
        if "minimum" in schema and node < schema["minimum"]:
            raise ValidationError(f"{path}: {node} < minimum")
        if "maximum" in schema and node > schema["maximum"]:
            raise ValidationError(f"{path}: {node} > maximum")
    elif t == "boolean":
        if not isinstance(node, bool):
            raise ValidationError(f"{path}: expected boolean")
    return True


def validate(instance, schema):
    try:
        import jsonschema
    except ImportError:
        return _check(instance, schema)
    try:
        jsonschema.validate(instance, schema)
    except Exception as e:  # jsonschema.ValidationError
        raise ValidationError(str(e)) from e
    return True
