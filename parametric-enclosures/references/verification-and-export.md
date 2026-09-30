# Verification, export and delivery

## Contents
1. Static check (always)
2. Rendering and exporting from the CLI
3. Interference and fit checks
4. Visual checks
5. Pre-delivery checklist (use when OpenSCAD isn't available)
6. Delivering in chat
7. Slicer hand-off notes

## 1. Static check

```
python3 scripts/check_scad.py path/to/enclosure.scad
```

Catches unbalanced braces/brackets, missing `part` branches, tolerance or wall
parameters, `ASSUMPTION` tags and asserts, huge `$fn`, `minkowski()`, and `use`
without a local `EPS`. Not a substitute for rendering.

After any change to `enclosure_lib.scad`, render `assets/selftest.scad`
(`openscad -o selftest.stl selftest.scad`) before touching product files.

## 2. CLI rendering and export

```
# one part → STL (or .3mf)
openscad -o base.stl -D 'part="base"' enclosure.scad
openscad -o lid.3mf  -D 'part="lid"'  enclosure.scad

# stop on the first warning (e.g. undefined variable) — good for CI-style checks
openscad --hardwarnings -o base.stl -D 'part="base"' enclosure.scad

# preview image
openscad -o preview.png --imgsize=1200,900 --viewall --autocenter \
         --projection=p -D 'part="exploded"' enclosure.scad

# console output only (echo/assert messages)
openscad -o log.echo enclosure.scad
```

- **Renders must be clean.** Treat every WARNING as a defect —
  "Object may not be a valid 2-manifold" means the slicer is guessing.
- `-D var=value` overrides top-level variables (strings need quotes, escaped
  for the shell; on Windows `-D "part=\"lid\""`).
- PNG uses preview mode by default; add `--render` for an exact render.
- `--camera=tx,ty,tz,rx,ry,rz,dist` for fixed views.
- Development snapshots render far faster with the Manifold backend
  (`--backend=manifold` in recent snapshots; older snapshots used
  `--enable=manifold`). Stable 2021.01 doesn't have it.
- `scripts/export_parts.sh enclosure.scad [parts…]` wraps all of this and
  writes `out/<name>_<part>.stl` plus previews.

## 3. Interference and fit checks

- `part = "check"` renders `intersection(){ base(); lid_world(); }`. The
  result must be **empty** — OpenSCAD reports an empty top-level object. Any
  solid is a collision; render it to see where.
- Extend the same idea to other pairs: board keepout box vs. standoffs/bosses,
  button caps vs. lid, battery vs. walls.
- Use `assert()` for numeric invariants (fits, minimums, build volume). They
  fail loudly in both GUI and CLI.
- `part = "section"` cuts the assembly in half to inspect lip clearance,
  standoff heights and cutout alignment.
- `%` ghost geometry (board, battery, display) shows fit in preview without
  being exported.

## 4. Visual checks

With a PNG or the user's screenshot, look for: cutouts aligned with
connectors on the board ghost, lid lip clearing bosses, no floating parts
(everything touches the base), text readable, vents clear of bosses and
cutouts, lid part lying flat (outer face at z = 0).

## 5. Pre-delivery checklist (reason through it when you can't render)

This expands the SKILL.md self-check into things to trace in the code:

1. Every tunable is a top-level parameter; derived values computed; profile values
   in the Process group match `manufacturing-profiles.md`.
2. Every `difference()` cutter overshoots by EPS (library `*_cut` modules do).
3. Board fits: cavity ≥ board + 2 × pcb_clear (+ connector overhang); stack height
   covers comp_top + 2 mm; standoffs ≥ 4 mm and taller than comp_bot.
4. Each cutout traces to board coordinates, sits on a front/back face, doesn't cross
   the lid split, and its plug can reach the socket (overmold recess set if needed).
5. Columns: gusseted, filleted, fused to walls, ribs clear of the board, bore =
   insert length + 1.0; enough columns for the span.
6. Standoffs start at `floor_t − EPS`; no column passes through the board footprint.
7. Body and lid fit: a continuous tongue, lip, or lap, with the slip clearance on
   each mating face and one slip of depth past the tongue. A rim-to-rim plate fails
   even if the solids do not intersect. `part="check"` is empty, and a section
   shows the gap. The land beside the groove is still at least one extrusion.
8. Each part prints support-free in the stated orientation; bridges ≤ profile limit
   (or noted); teardrops on large horizontal holes.
9. Vents: chimney bands, slot ≤ 25 mm, pitch ≥ slot + wall, ≤ 4 mm if child/pet safe.
10. Sensors chambered per sensors.md; heat sources ≥ 15 mm (asserted); antenna
    keepout (asserted).
11. Fits the build envelope (asserted); tall parts flagged for a brim.
12. Every `part` value produces geometry, and `check` produces none.
13. More than one module, a battery, a switched load or a cable out: a power
    budget, a pin map, a wiring table (electronics-and-wiring.md §9); a fuse at
    the source; a keyed/latched or screwed power connection; each cable exit has
    a zip-tie anchor and an anti-chafe hole. `heat_w` matches the budget.

## 6. Delivering in chat

- Deliver the complete `.scad`; ship `enclosure_lib.scad` alongside if the
  file `use`s it, or inline the modules into one file (preferred for users who
  paste into the OpenSCAD editor or an online renderer — say which you did).
- When file tools exist, write the files to the outputs and present them;
  include exported STL/3MF/PNG only if you actually rendered them.
- Never claim a render/export succeeded if it didn't run. Say "not rendered
  here — run F6" when OpenSCAD isn't available.
- For follow-up edits, keep parameter names; list changed parameters.

## 7. Slicer hand-off notes (put in the reply)

Per part: orientation, "no supports", layer height (0.2 mm; 0.12–0.16 for fine
text), perimeters (3–4; 4+ around inserts), infill (15–25 % gyroid; 40 %+ for
bosses/snap roots via modifier), brim for ABS/ASA, material temperatures from
the spool. Mention any pause-at-height for captured magnets/nuts with the Z
value.
