#!/usr/bin/env python3
"""Static sanity check for enclosure .scad files (no OpenSCAD needed).

Usage: python3 check_scad.py file.scad [more.scad ...]
Exit code 1 if any ERROR is found; warnings don't fail.
"""
import re
import sys


def strip_comments_and_strings(src):
    """Return src with comments and string contents blanked (newlines kept)."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j == -1 else j
            out.append(" " * (j - i)); i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j == -1 else j + 2
            out.append(re.sub(r"[^\n]", " ", src[i:j])); i = j
        elif c == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            out.append('"' + " " * max(0, j - i - 1) + '"'); i = j + 1
        else:
            out.append(c); i += 1
    return "".join(out)


def check(path):
    errors, warnings = [], []
    src = open(path, encoding="utf-8").read()
    code = strip_comments_and_strings(src)

    # bracket balance with line numbers
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ln, line in enumerate(code.splitlines(), 1):
        for ch in line:
            if ch in "([{":
                stack.append((ch, ln))
            elif ch in ")]}":
                if not stack or stack[-1][0] != pairs[ch]:
                    errors.append(f"line {ln}: unmatched '{ch}'")
                else:
                    stack.pop()
    for ch, ln in stack:
        errors.append(f"line {ln}: '{ch}' never closed")

    is_library = not re.search(r"^\s*part\s*=", code, re.M)
    if not is_library:
        if not re.search(r"^\s*wall(_lines)?\s*=", code, re.M):
            warnings.append("no top-level 'wall' parameter")
        if not re.search(r"^\s*(tol|fit_clear)\s*=", code, re.M):
            warnings.append("no top-level fit tolerance ('tol')")
        if "/* [Hidden] */" not in src:
            warnings.append("no '/* [Hidden] */' section: derived values will clutter the Customizer")
        if "assert(" not in code:
            warnings.append("no assert(): add fit/build-volume checks")
        if "ASSUMPTION" not in src:
            warnings.append("no '// ASSUMPTION:' tags: list chosen defaults so the user can correct them")
        for p in ("base", "lid"):
            if not re.search(rf'part\s*==\s*"{p}"', src):
                warnings.append(f'no part == "{p}" branch')
        if re.search(r"\bcable_exits\s*=", code) and not re.search(r"\btie_anchor\s*\(", code):
            warnings.append("cable_exits without a tie_anchor: a pull on the cable reaches the joint")

    if re.search(r"\buse\s*<", code):
        for v in ("EPS", "eps"):
            if re.search(rf"\b{v}\b", code) and not re.search(rf"^\s*{v}\s*=", code, re.M):
                errors.append(f"'use <...>' does not import variables: define {v} in this file")

    for m in re.finditer(r"\$fn\s*=\s*(\d+)", code):
        if int(m.group(1)) > 128:
            ln = code[: m.start()].count("\n") + 1
            warnings.append(f"line {ln}: $fn={m.group(1)} is slow and finer than a 0.4 mm nozzle can print")
    if re.search(r"\bminkowski\s*\(", code):
        warnings.append("minkowski() is very slow; prefer offset() on 2D profiles or hull()")
    if re.search(r"\bmirror\s*\(", code) and re.search(r"\btext\s*\(", code):
        warnings.append("mirror() in a file with text(): make sure no label is mirrored")

    return errors, warnings


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    failed = False
    for path in argv[1:]:
        errors, warnings = check(path)
        print(f"== {path}")
        for e in errors:
            print(f"  ERROR   {e}")
        for w in warnings:
            print(f"  WARNING {w}")
        if not errors and not warnings:
            print("  OK")
        failed |= bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
