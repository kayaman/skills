# FDM design rules

Generic rules for a 0.4 mm nozzle, 0.2 mm layers, and a reasonably tuned desktop
printer. **A manufacturing profile (`manufacturing-profiles.md`) overrides everything
here** — use this file for the reasoning behind the rules, for printers and materials
without a profile, and to build a new profile. Put every tolerance in a named
parameter so one test print can retune the whole model.

Desktop FDM holds about a few tenths of a millimetre on a tuned machine, and worse
across a long part as plastic cools. Do not promise a tighter tolerance than the
profile's `tol` until a coupon has been measured. Critical bores get a pilot and a
drill or reamer.

## Contents
1. Walls and minimum features
2. Tolerances and fits
3. Holes
4. Overhangs, bridges, supports
5. Print orientation and strength
6. Edges, corners, first layer
7. Solid mass
8. Text and cosmetic faces
9. Materials
10. Calibration print
11. When FDM is the wrong process

## 1. Walls and minimum features

Extrusion width `ew` is about 0.42–0.45 mm on a 0.4 mm nozzle. Design widths as
`n * ew` (1.2 / 1.6 / 2.0 / 2.4 mm are all good) to avoid gap fill.

| Feature | Minimum | Working default | Why |
|---|---|---|---|
| Side wall | 1.2 mm (3 lines) | 2.0 mm, or the profile wall | Two perimeters with infill between them is the least that is stiff and opaque. One line is fragile and slicers sometimes drop it |
| Floor / roof / lid plate | 0.8 mm (4 layers at 0.2) | 1.2–2.0 mm | Fewer than four solid layers leaves infill visible and weak in bending |
| Rib / gusset | 0.8 mm (2 lines) | 1.2 mm | One-line features are fragile and may be dropped by the slicer |
| Screw boss wall | 2.0 mm | profile (2.5 mm PETG-CF) | See `fits-and-fasteners.md` |
| Free-standing pin | Ø 2 mm | Ø 3 mm | Thin pins wobble and snap at the layer line where they meet the body |
| Debossed text on a top face | 0.4 mm deep, ≥ 3 mm tall, stroke ≥ 2 lines | 0.6 mm deep, 5 mm tall, bold | Shallow detail disappears into layer lines |
| Embossed text on a side wall | 0.6 mm proud, 5 mm tall | — | Stroke ≥ 2 line widths |

A wall thinner than one `ew` will not print. Detect thin wall in the slicer is a
rescue, not a design.

A feature that only touches the body is not part of the body. Overlap bosses, ribs,
pins, and embossed letters into the solid, and keep that neck at least two extrusion
widths. The mesh rules in `mesh-and-export.md` are what keep the STL a single closed
solid.

## 2. Tolerances and fits

The fit table (press / snug / slip / loose, per side) and everything built on it —
lids, inserts, screws, snaps, hinges, magnets — live in `fits-and-fasteners.md`. The
profile's `tol` triple replaces the generic table when a profile is in force.

Printed part to a bought part: board-to-wall ≥ the slip tol (default 0.5 mm; board
outlines vary ±0.2 mm), connector bodies +0.5 mm per side, magnets and bearings
+0.1–0.2 mm on diameter.

## 3. Holes

- Vertical holes (axis along Z) print **undersized**, typically 0.1–0.3 mm on
  diameter, from polygon approximation plus extrusion squish. Add a `hole_comp`
  parameter (profile value, or 0.2 mm default) to functional diameters, or use
  `poly_d()` in OpenSCAD.
- Horizontal holes (axis in XY) print oval with a drooping crown. Above the profile's
  teardrop threshold (~5 mm), use a teardrop (hull of the circle and a point above at
  45°) or a flat bridged top. Small ones can be drilled or reamed if accuracy matters.
- Holes under about 2 mm are unreliable; print a pilot and drill.
- Holes that open through the first layer close up from elephant's foot. Chamfer the
  bed edge, or add about 0.2 mm, and do not use that face as a precision bore.

## 4. Overhangs, bridges, supports

Measure overhang from vertical. At 45° the new line is half supported by the line
below, which is why that angle is the usual unsupported limit (Prusa's modeling guide
and the Hubs FDM guide both use it); 50–55° is usually survivable with good cooling.
The house profile targets 40° in PETG-CF because that material sags sooner. Past the
limit, the slicer can add support, but the supported face looks worse and fit faces
get scarred. Redesign instead:

- Replace a horizontal ledge with a 45° chamfer.
- Replace a round horizontal hole with a teardrop or a flat top that bridges.
- Replace unsupported horizontal ceilings over cutouts with 45° chamfers or
  arch/teardrop tops. Rectangular cutouts in vertical walls bridge their top edge:
  keep the width modest or round or point the top.
- Keep real bridges within the profile limit. A clean unsupported bridge is on the
  order of 5 mm; 10 mm is often acceptable in PLA and starts to sag; longer than that
  needs a split or support. A lid printed face-down on the bed is not a bridge.

Design for **zero supports**: supports scar the surfaces, waste time, and trap in
small cavities. Supports on a fit, seal, or sliding face are a design failure. If a
support is truly needed, say where and why.

## 5. Print orientation and strength

Each layer is a weld, and the weld is the weak plane. Filled filaments are often worse
in Z than the unfilled polymer, because the fibers do not cross the layers and they
reduce the bonded area. Do not quote a strength ratio. Orient so tension and bending
run in XY.

- A cantilever printed standing up snaps at the root along a layer. Lay the beam down
  so it bends across many lines. The same applies to snap-fit beams and flexure
  buttons: bending axis parallel to the layers.
- A screw pulling a thin flange along Z peels the flange off. Carry that load through
  a column of perimeters, or put the screw axis along Z so tightening compresses the
  layers; inserts spread the load.
- Enclosure base: floor on the bed. Lid: either face down prints without supports.
  The enclosure template prints it mating face down, so the screw counterbores open
  upward. Outer face down gives the better show face, but each counterbore then has a
  downward ledge: add a one-layer sacrificial bridge the user drills through.
- The bed face is the flattest, and on a textured plate it is also the roughest. Put
  the face that must be flat and accurate on the bed only if texture is acceptable.
  Put the face that people look at on the bed when a smooth plate is in use.
- Tall walls under about 1.6 mm and over about 60 mm wobble as they print. Thicken
  them or rib them.
- Sharp corners on a large base lift as the plastic shrinks, especially in ABS, ASA
  and PC. Round them (R ≥ 3 mm), use a brim on warp-prone materials, and avoid long
  sharp-cornered walls.

## 6. Edges, corners, first layer

Which edge treatment to use depends on the edge's direction, not on taste. Prusa's
modeling guide and ordinary FDM practice agree on the split.

- **Parallel to the bed: chamfer.** That includes the bed contact, the top lip, and
  the underside of any ledge. A fillet on those edges opens as a near-horizontal
  overhang and the curve shows every layer step. Bed contact is 0.4–0.8 mm × 45°. A
  downward-facing fillet is the same defect as a fillet on the bed. One exception:
  where a chamfer would eat a one-extrusion land (an enclosure lid's groove side on
  the bed), leave the edge square and keep the slicer's elephant-foot compensation
  on — and say so in the build notes.
- **Vertical: fillet.** The nozzle traces this edge. A sharp corner stops the head and
  leaves a ring. The radius has to be large enough to be a curve, about two extrusion
  widths (≈ 1 mm); smaller than that prints as a blob. On a large base that wants to
  warp, use R ≥ 3 mm.
- **A corner that carries a bend: fillet, and keep the wall thickness.** Inside radius
  at least R 0.5 mm in unfilled plastic and R 1 mm in filled or brittle plastic, and
  at least half the local wall thickness when that corner is the hinge of the load.
  The outside radius shares the same center, so it is the inside radius plus the wall
  thickness. A fillet that thins the wall moves the crack to the thin spot.
- **Inner corners where walls meet the floor: fillet, about 1 mm.** That corner is
  supported by the floor, and a square corner there is where a brittle wall cracks.

A chamfer on two parts that slide together is also the lead-in. It does not replace
the clearance.

The first layer is squashed on purpose so it sticks, so the part grows a foot. A
chamfer removes the foot from the mating profile. Slicer elephant-foot compensation
(often around 0.15–0.2 mm on a 0.4 mm nozzle) is the backup, not the design.

## 7. Solid mass

Regions thicker than about 4 mm hold heat, shrink unevenly, and waste time. Shell
them to a few perimeters and rib the span. Local thickening under a washer is fine; a
solid block is not.

## 8. Text and cosmetic faces

Deboss horizontal top faces (the nozzle traces them cleanly). Emboss vertical faces,
with a stroke of at least two extrusion widths, because a debossed side wall is a tiny
overhang. Avoid text on the bed face.

Seams leave a small ridge. Put the seam on a hidden corner, never on a sliding face.
The slicer does this; mention it in the print plan when the part moves.

## 9. Materials

The material table, selection order, shrinkage and drying guidance live in
`materials.md`. Shrink is mostly absorbed by sane clearances; it matters for long
parts with tight fits. None of the common filaments are flame-rated (UL94 V-0) unless
the spool says so — see `environment-and-safety.md` for mains and battery
implications.

## 10. Calibration print

When fits matter (sliding lid, snap-fits, press-fit magnets, inserts), offer a small
test coupon before the full print. It costs one short print and sets `tol`,
`hole_comp` and the insert bore for every future design on that printer/material.
Use `assets/fit-coupon.scad` and the reading order in `manufacturing-profiles.md`.

## 11. When FDM is the wrong process

Stop and switch process, or tell the user the feature must change, when the part
needs:

- walls or gaps below one extrusion width
- a tolerance tighter than `tol` on a bore that cannot be drilled
- support-free printing of a shape with no legal orientation
- a flexible hinge in a rigid filament
- isotropy that the load genuinely requires and orientation cannot provide

Resin and SLS rules are in `resin.md` and `sls.md`. They are not a way to dodge a
redesign that FDM could do with a chamfer.
