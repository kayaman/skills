#!/usr/bin/env bash
# Render each part of an enclosure to STL (or 3MF) plus PNG previews.
# Usage: export_parts.sh enclosure.scad [part ...]
#   default parts: base lid
#   FORMAT=3mf   export 3MF instead of STL
#   OUT=dir      output directory (default ./out)
#   BACKEND=manifold   pass --backend=manifold (development snapshots only)
set -euo pipefail

SCAD="${1:?usage: export_parts.sh file.scad [part ...]}"; shift || true
PARTS=("$@"); [ ${#PARTS[@]} -eq 0 ] && PARTS=(base lid)
FORMAT="${FORMAT:-stl}"; OUT="${OUT:-out}"
NAME="$(basename "${SCAD%.scad}")"

if ! command -v openscad >/dev/null 2>&1; then
  echo "openscad not found on PATH — install it or render in the GUI (F6)." >&2
  exit 127
fi
EXTRA=(); [ -n "${BACKEND:-}" ] && EXTRA+=("--backend=${BACKEND}")
mkdir -p "$OUT"

status=0
for p in "${PARTS[@]}"; do
  f="$OUT/${NAME}_${p}.${FORMAT}"
  echo "-- $p → $f"
  if ! openscad "${EXTRA[@]}" -o "$f" -D "part=\"$p\"" "$SCAD" 2>"$OUT/${NAME}_${p}.log"; then
    echo "   FAILED (see $OUT/${NAME}_${p}.log)"; status=1; continue
  fi
  grep -E "WARNING|ERROR" "$OUT/${NAME}_${p}.log" || true
done

# interference check: must be empty
if openscad "${EXTRA[@]}" -o "$OUT/${NAME}_check.stl" -D 'part="check"' "$SCAD" \
     2>"$OUT/${NAME}_check.log"; then
  if grep -qi "empty" "$OUT/${NAME}_check.log"; then
    echo "-- interference check: OK (empty)"
  else
    echo "-- interference check: parts overlap! open part=\"check\""; status=1
  fi
else
  grep -qi "empty" "$OUT/${NAME}_check.log" \
    && echo "-- interference check: OK (empty)" \
    || { echo "-- interference check could not run (see log)"; }
fi

for view in assembly exploded; do
  openscad "${EXTRA[@]}" -o "$OUT/${NAME}_${view}.png" --imgsize=1200,900 \
    --viewall --autocenter -D "part=\"$view\"" "$SCAD" 2>/dev/null \
    && echo "-- preview $OUT/${NAME}_${view}.png" || true
done
exit $status
