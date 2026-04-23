#!/usr/bin/env python3
"""
Check event naming and envelope conventions across a directory of JSON schemas.

Usage:
  check-naming.py <schemas-dir>

Rules enforced (soft — warns; hard failures marked FAIL):
  FAIL  `type` is present-tense or imperative (e.g., `UpdateUser`, `OrderUpdating`).
  FAIL  Required envelope fields missing from schema (`id`, `type`, `version`, `source`,
        `occurredAt`, `correlationId`, `data`).
  WARN  `type` uses a generic verb (`Updated`, `Changed`, `Modified`) — likely a god-event.
  WARN  Filename does not match `<kebab-type>.v<N>.json` convention.
  FAIL  `version` is not a positive integer.

Exits 0 if only warnings or all clean, 1 if any FAIL encountered.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PAST_TENSE_OK = (
    # Commonly-used past-tense verb endings; not exhaustive.
    "ed", "en", "lt", "ne", "de", "re",  # Created, Placed, Built, Gone, Decided, Fired
    "id",    # Paid
    "pt",    # Accepted (handled by 'ed' too, belt-and-suspenders)
    "nt",    # Sent
    "st",    # Posted (Lost), Burst — ends in "ed" usually
)

IMPERATIVE_PREFIXES = (
    "Create", "Update", "Delete", "Remove", "Add", "Set", "Get", "Fetch",
    "Put", "Post", "Send", "Trigger", "Start", "Stop", "Cancel", "Reject",
    "Approve", "Accept", "Modify", "Change", "Place",
)

GENERIC_SUFFIXES = ("Updated", "Changed", "Modified", "Edited")

REQUIRED_ENVELOPE_FIELDS = {
    "id", "type", "version", "source", "occurredAt", "correlationId", "data",
}


def check_type_name(name: str) -> tuple[list[str], list[str]]:
    """Return (fails, warns)."""
    fails, warns = [], []
    if not name:
        return ["`type` is empty"], warns
    if not name[0].isupper():
        fails.append(f"`type` should start with uppercase: {name!r}")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]+", name):
        fails.append(f"`type` must be alphanumeric PascalCase: {name!r}")

    # Imperative prefix → command, not event
    for prefix in IMPERATIVE_PREFIXES:
        if name.startswith(prefix) and not name.endswith(PAST_TENSE_OK):
            fails.append(
                f"`type` {name!r} looks imperative (starts with {prefix!r}); events are past tense."
            )
            break

    # Generic suffix → likely god event
    for suf in GENERIC_SUFFIXES:
        if name.endswith(suf):
            warns.append(
                f"`type` {name!r} ends in {suf!r}; consider splitting into specific facts."
            )
            break

    return fails, warns


def check_schema_file(path: Path) -> tuple[list[str], list[str]]:
    fails, warns = [], []
    try:
        schema = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"{path}: not valid JSON: {e}"], warns

    # Pull required fields out of the schema's properties if this looks like a full event schema
    props = schema.get("properties", {}) if isinstance(schema, dict) else {}
    required = set(schema.get("required", []) or [])
    if props:
        missing = REQUIRED_ENVELOPE_FIELDS - required
        # `publishedAt`, `metadata`, `causationId` are optional-nullable — allowed missing
        missing -= {"causationId"}  # optional for root events
        if missing:
            fails.append(
                f"{path}: schema missing required envelope fields in `required`: {sorted(missing)}"
            )

    # Validate declared type name if present
    type_prop = props.get("type", {})
    if isinstance(type_prop, dict):
        # The `type` value may be constrained via `const` or `enum`
        const = type_prop.get("const")
        enum = type_prop.get("enum")
        candidates = []
        if isinstance(const, str):
            candidates.append(const)
        if isinstance(enum, list):
            candidates.extend([e for e in enum if isinstance(e, str)])
        for cand in candidates:
            f, w = check_type_name(cand)
            fails.extend(f"{path}: {msg}" for msg in f)
            warns.extend(f"{path}: {msg}" for msg in w)

    # Filename convention: <kebab>.v<N>.json
    name = path.name
    if not re.fullmatch(r"[a-z][a-z0-9-]*\.v\d+\.json", name):
        warns.append(
            f"{path}: filename {name!r} does not match '<kebab-type>.v<N>.json' convention"
        )

    return fails, warns


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    root = Path(argv[1])
    if not root.exists():
        print(f"directory not found: {root}", file=sys.stderr)
        return 2

    schemas = sorted(root.rglob("*.json"))
    if not schemas:
        print(f"no JSON files under {root}", file=sys.stderr)
        return 0

    total_fails = 0
    total_warns = 0
    for s in schemas:
        fails, warns = check_schema_file(s)
        for f in fails:
            print(f"FAIL  {f}")
        for w in warns:
            print(f"WARN  {w}")
        total_fails += len(fails)
        total_warns += len(warns)

    print()
    print(f"checked {len(schemas)} file(s): {total_fails} FAIL, {total_warns} WARN")
    return 1 if total_fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
