#!/usr/bin/env python3
"""
Validate an event instance (JSON) against an event schema (JSON Schema draft 2020-12).

Usage:
  validate-event-schema.py <event.json> [<schema.json>]

If only one argument is given, validates the event against the canonical envelope
(assets/event-envelope.schema.json). If two arguments are given, validates against
the provided schema.

Exits 0 on success, 1 on validation failure, 2 on usage error.

Depends on the `jsonschema` package (pip install jsonschema) or falls back to a
minimal structural validator that checks the envelope shape only.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


REQUIRED_ENVELOPE_FIELDS = (
    "id",
    "type",
    "version",
    "source",
    "occurredAt",
    "correlationId",
    "data",
)


def envelope_schema_path() -> Path:
    # assets/event-envelope.schema.json, relative to this file
    return Path(__file__).resolve().parent.parent / "assets" / "event-envelope.schema.json"


def fallback_validate(event: dict, schema: dict) -> list[str]:
    """Minimal structural check if jsonschema is unavailable.

    Only the envelope is verified; per-event payloads need real jsonschema.
    """
    errors: list[str] = []
    if not isinstance(event, dict):
        return [f"top-level event must be an object, got {type(event).__name__}"]
    for field in REQUIRED_ENVELOPE_FIELDS:
        if field not in event:
            errors.append(f"missing required field: {field!r}")

    t = event.get("type")
    if isinstance(t, str):
        if not t[:1].isupper() or not t.replace("", "").isalnum():
            errors.append(f"`type` should be PascalCase past-tense: got {t!r}")

    v = event.get("version")
    if not (isinstance(v, int) and v >= 1):
        errors.append(f"`version` must be integer >= 1: got {v!r}")

    if "data" in event and not isinstance(event["data"], dict):
        errors.append("`data` must be an object")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        print(__doc__.strip(), file=sys.stderr)
        return 2

    event_path = Path(argv[1])
    schema_path = Path(argv[2]) if len(argv) == 3 else envelope_schema_path()

    if not event_path.exists():
        print(f"event file not found: {event_path}", file=sys.stderr)
        return 2
    if not schema_path.exists():
        print(f"schema file not found: {schema_path}", file=sys.stderr)
        return 2

    with event_path.open() as f:
        try:
            event = json.load(f)
        except json.JSONDecodeError as e:
            print(f"event file is not valid JSON: {e}", file=sys.stderr)
            return 1

    with schema_path.open() as f:
        try:
            schema = json.load(f)
        except json.JSONDecodeError as e:
            print(f"schema file is not valid JSON: {e}", file=sys.stderr)
            return 1

    try:
        from jsonschema import Draft202012Validator
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(event), key=lambda e: list(e.absolute_path))
        if errors:
            for err in errors:
                path = "/".join(str(p) for p in err.absolute_path) or "<root>"
                print(f"FAIL {path}: {err.message}")
            return 1
        print(f"OK  {event_path} validates against {schema_path.name}")
        return 0
    except ImportError:
        # Fallback: structural check only
        errors = fallback_validate(event, schema)
        if errors:
            print("jsonschema not installed; running structural fallback. Install with: pip install jsonschema", file=sys.stderr)
            for e in errors:
                print(f"FAIL {e}")
            return 1
        print(f"OK (structural only)  {event_path}")
        print("Install `jsonschema` for full validation: pip install jsonschema", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
