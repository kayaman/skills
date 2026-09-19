# OpenSCAD conventions

## File layout

Always this order. Anyone opening the file should reach the parameters in the first
screen and never need to scroll to change a dimension.

```
1. Header comment: product, version, profile, author, licence
2. use <enclosure_lib.scad>
3. /* [Group] */ Customizer parameters
4. Derived values (all computed, no literals)
5. assert() block — validate before rendering anything
6. echo() block — report dimensions, volumes, screw lengths
7. Project-specific modules
8. Part modules: base(), lid(), ...
9. Part selector: if (part == "base") base(); else if ...
```

## Assertions

`assert()` halts the render with a message. Use it for the invariants that silently
produce a bad part rather than an obviously broken one — those are the expensive ones,
because they print fine and fail in assembly.

```scad
assert(wall >= 3 * ew,
       str("wall ", wall, " is under 3 perimeters for ew=", ew));
assert(boss_od >= insert_bore + 2 * boss_min_wall,
       "boss OD too small for the insert — it will split");
assert(pcb_x + 2 * pcb_clear + 2 * wall <= outer_x,
       "PCB does not fit the cavity");
assert(max(outer_x, outer_y, outer_z) <= envelope,
       str("part exceeds the ", envelope, " mm build envelope"));
assert(sensor_gap >= 15,
       "sensor chamber is within 15 mm of a heat source");
assert(antenna_clear >= keepout,
       "structure inside the antenna keepout");
```

Write the assertion when you write the geometry, not afterwards. An assertion added
later encodes what the model happens to be, not what it should be.

## Echo

```scad
echo(str("outer: ", outer_x, " x ", outer_y, " x ", outer_z, " mm"));
echo(str("bounding box vs envelope: ", max(outer_x, outer_y, outer_z), " / ", envelope));
echo(str("screw length needed: ", lid_t + insert_len, " mm"));
echo(str("internal volume: ", cav_x * cav_y * cav_z / 1000, " cm3"));
```

The bounding-box echo pairs with the envelope assert and catches the split-the-part
decision before the slicer does.

## Geometry pitfalls that produce bad STLs

- **Coincident faces.** Every cutter in a `difference()` must overshoot both ends by
  `eps = 0.01`. Two faces at exactly the same Z produce a non-manifold result that
  slicers repair unpredictably.
- **`minkowski()` for rounding.** Never. It is orders of magnitude slower and produces
  dense meshes. Round with `hull()` of cylinders or spheres.
- **Low `$fn` on functional holes.** A 3.4 mm hole at `$fn=12` is a 3.28 mm hole at the
  flats. Use `$fa`/`$fs`, or set `$fn` per-object high enough for the diameter.
- **Rotations that leave geometry off-grid.** Rotating by non-multiples of 90° and then
  differencing can leave slivers. Prefer building in place.
- **`scale()` to fix fit.** It scales the tolerances too. Change the parameter.
- **2D `offset()` for concave fillets.** `offset(r=-r) offset(r=+r)` fillets concave
  corners of a 2D profile — useful, but it does not help on 3D concave edges between a
  wall and a floor. Use the library's `fillet_lin` / `fillet_ring` for those.

## Customizer syntax

```scad
/* [PCB] */
pcb_x = 50;        // [10:0.5:160]
pcb_y = 30;        // [10:0.5:160]

/* [Fasteners] */
fastener = "insert";  // [insert, self_tap]

/* [Hidden] */
eps = 0.01;
```

Anything below `/* [Hidden] */` stays out of the Customizer UI. Put `eps` and derived
values there.

## Export

One line per part. `part="all"` is preview only and is never exported.

```bash
openscad -D 'part="base"' -o base.stl product_enclosure.scad
openscad -D 'part="lid"'  -o lid.stl  product_enclosure.scad
```

Renders must be clean — no warnings. Treat a warning as a defect, because
`WARNING: Object may not be a valid 2-manifold` means the slicer is guessing.

Batch:

```bash
for p in base lid sensor_cover; do
  openscad -D "part=\"$p\"" -o "$p.stl" product_enclosure.scad || exit 1
done
```

## Library use

`use <enclosure_lib.scad>` imports modules but not variables, which is what you want —
the project file owns every number. Pass parameters explicitly rather than relying on
library defaults, so the project file remains the single source of truth.

Keep `enclosure_lib.scad` beside the project file. When the library changes, re-run
`selftest.scad` before touching product files.
