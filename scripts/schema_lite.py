#!/usr/bin/env python3
"""A small JSON Schema validator for the keyword subset used by this skill's schemas.

Why it exists: the skill must run anywhere Python 3 runs, with no packages to install.
The three schemas in ../schemas only use the keywords listed below, so a compact
validator keeps the schemas and the checks in sync without a third-party dependency.

Supported keywords:
  $ref (local "#/..." pointers only), type (string or list), enum, const,
  required, properties, additionalProperties (boolean only), items, minItems,
  maxItems, uniqueItems, minLength, maxLength, pattern, minimum, maximum, oneOf.

oneOf is validated by discriminator when every branch pins the same property with
`const` (for example `verdict` or `status`), which makes error messages point at the
branch the author meant. Otherwise exactly one branch must match.

Unsupported keywords raise ValueError so a schema change cannot silently weaken a check.
"""
from __future__ import annotations

import json
import re
from typing import Any

SUPPORTED = {
    "$schema", "$id", "title", "description", "$defs", "$ref", "type", "enum", "const",
    "required", "properties", "additionalProperties", "items", "minItems", "maxItems",
    "uniqueItems", "minLength", "maxLength", "pattern", "minimum", "maximum", "oneOf",
}


def load_schema(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _type_ok(value: Any, name: str) -> bool:
    if name == "object":
        return isinstance(value, dict)
    if name == "array":
        return isinstance(value, list)
    if name == "string":
        return isinstance(value, str)
    if name == "boolean":
        return isinstance(value, bool)
    if name == "null":
        return value is None
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    raise ValueError(f"unsupported type name: {name}")


def _same(a: Any, b: Any) -> bool:
    """Equality that does not treat True as 1."""
    return type(a) is type(b) and a == b


def _resolve(ref: str, root: dict) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"only local $ref pointers are supported: {ref}")
    node: Any = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _deref(schema: dict, root: dict) -> dict:
    while "$ref" in schema:
        schema = _resolve(schema["$ref"], root)
    return schema


def _discriminator(branches: list, root: dict) -> str | None:
    resolved = [_deref(b, root) for b in branches]
    first_props = resolved[0].get("properties", {})
    for name, sub in first_props.items():
        if "const" in sub and all("const" in b.get("properties", {}).get(name, {}) for b in resolved):
            return name
    return None


def validate(instance: Any, schema: dict, root: dict | None = None, path: str = "$") -> list[str]:
    """Return a list of human-readable error strings. An empty list means valid."""
    root = root if root is not None else schema
    schema = _deref(schema, root)
    unknown = set(schema) - SUPPORTED
    if unknown:
        raise ValueError(f"unsupported schema keyword(s) at {path}: {sorted(unknown)}")

    errors: list[str] = []

    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(instance, n) for n in names):
            errors.append(f"{path}: expected {' or '.join(names)}, got {type(instance).__name__}")
            return errors

    if "const" in schema and not _same(instance, schema["const"]):
        errors.append(f"{path}: must be {schema['const']!r}, got {instance!r}")
        return errors

    if "enum" in schema and not any(_same(instance, option) for option in schema["enum"]):
        errors.append(f"{path}: {instance!r} is not one of {schema['enum']}")
        return errors

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']} characters")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: longer than {schema['maxLength']} characters ({len(instance)})")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} does not match pattern {schema['pattern']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} is below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} is above maximum {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: needs at least {schema['minItems']} item(s), has {len(instance)}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: allows at most {schema['maxItems']} item(s), has {len(instance)}")
        if schema.get("uniqueItems"):
            seen = []
            for item in instance:
                if any(_same(item, other) for other in seen):
                    errors.append(f"{path}: items are not unique")
                    break
                seen.append(item)
        if "items" in schema:
            for index, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], root, f"{path}[{index}]"))

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in instance:
                errors.append(f"{path}: missing required field '{name}'")
        if schema.get("additionalProperties") is False:
            for name in instance:
                if name not in properties:
                    errors.append(f"{path}: unexpected field '{name}'")
        for name, sub in properties.items():
            if name in instance:
                errors.extend(validate(instance[name], sub, root, f"{path}.{name}"))

    if "oneOf" in schema:
        branches = schema["oneOf"]
        key = _discriminator(branches, root)
        if key is not None and isinstance(instance, dict):
            wanted = instance.get(key)
            chosen = None
            for branch in branches:
                resolved = _deref(branch, root)
                if _same(resolved["properties"][key]["const"], wanted):
                    chosen = branch
                    break
            if chosen is None:
                allowed = [_deref(b, root)["properties"][key]["const"] for b in branches]
                errors.append(f"{path}.{key}: {wanted!r} is not one of {allowed}")
            else:
                errors.extend(validate(instance, chosen, root, path))
        else:
            matches = [b for b in branches if not validate(instance, b, root, path)]
            if len(matches) != 1:
                errors.append(f"{path}: must match exactly one of {len(branches)} alternatives, matched {len(matches)}")

    return errors


def validate_file(instance_path: str, schema_path: str) -> list[str]:
    with open(instance_path, "r", encoding="utf-8") as handle:
        instance = json.load(handle)
    return validate(instance, load_schema(schema_path))


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("usage: schema_lite.py <instance.json> <schema.json>")
        sys.exit(2)
    problems = validate_file(sys.argv[1], sys.argv[2])
    for problem in problems:
        print(problem)
    sys.exit(1 if problems else 0)
