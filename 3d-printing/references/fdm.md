# FDM design rules

Generic rules for a 0.4 mm nozzle, 0.2 mm layers, and a tuned desktop printer. The house profile overrides this file. Use these numbers when no profile applies, and use the reasoning either way.

Desktop FDM holds about a few tenths of a millimetre on a tuned machine, and worse across a long part as plastic cools. Do not promise a tighter tolerance than the profile's `tol` until a coupon has been measured. Critical bores get a pilot and a drill or reamer.

## Walls and features

Extrusion width `ew` is about 0.42–0.45 mm on a 0.4 mm nozzle. Design widths as `n * ew`.

| Feature | Minimum | Working default | Why |
|---|---|---|---|
| Side wall | 1.2 mm (3 lines) | 2.0 mm, or the profile wall | Two perimeters with infill between them is the least that is stiff and opaque. One line is fragile and slicers sometimes drop it |
| Floor / roof | 0.8 mm (4 layers at 0.2) | 1.2–2.0 mm | Fewer than four solid layers leaves infill visible and weak in bending |
| Rib | 0.8 mm (2 lines) | 1.2 mm | |
| Free-standing pin | Ø 2 mm | Ø 3 mm | Thin pins snap at the layer line where they meet the body |
| Embossed or debossed text | 0.4 mm deep, ≥ 3 mm tall, stroke ≥ 2 lines | 5 mm tall on a side wall | Shallow detail disappears into layer lines |

A wall thinner than one `ew` will not print. Detect-thin-walls in the slicer is a rescue, not a design.

## Overhangs, bridges, holes

Measure overhang from vertical. At 45° the new line is half supported by the line below, which is why that angle is the usual unsupported limit (Prusa's modeling guide and the Hubs FDM guide both use it). The house profile targets 40° in PETG-CF because that material sags sooner. Past the limit, the slicer can add support, but the supported face looks worse and fit faces get scarred. Redesign:

- Replace a horizontal ledge with a 45° chamfer.
- Replace a round horizontal hole with a teardrop (circle plus a point above at 45°) or a flat top that bridges.
- Keep real bridges within the profile limit. A clean unsupported bridge is on the order of 5 mm; 10 mm is often acceptable in PLA and starts to sag; longer than that needs a split or support. A lid printed face-down on the bed is not a bridge.

Vertical holes (axis along Z) print small, typically a few tenths of a millimetre on diameter, from polygon approximation plus extrusion squish. Add `hole_comp` to functional diameters. Holes under about 2 mm are unreliable; print a pilot and drill.

Horizontal holes print oval, with a drooping crown. Small ones can be drilled. Large ones get a teardrop.

Holes that open through the first layer close up from elephant's foot. Chamfer the bed edge, or add about 0.2 mm, and do not use that face as a precision bore.

## Orientation and strength

Each layer is a weld, and the weld is the weak plane. Filled filaments are often worse in Z than the unfilled polymer, because the fibers do not cross the layers and they reduce the bonded area. Do not quote a strength ratio. Orient so tension and bending run in XY.

- A cantilever printed standing up snaps at the root along a layer. Lay the beam down so it bends across many lines.
- A screw pulling a thin flange along Z peels the flange off. Carry that load through a column of perimeters, or put the screw axis along Z so tightening compresses the layers.
- The bed face is the flattest, and on a textured plate it is also the roughest. Put the face that must be flat and accurate on the bed only if texture is acceptable. Put the face that people look at on the bed when a smooth plate is in use.
- Tall walls under about 1.6 mm and over about 60 mm wobble as they print. Thicken them or rib them.
- Sharp corners on a large base lift as the plastic shrinks. Round them (R ≥ 3 mm) and use a brim on warp-prone materials.

## Edges

- Bed contact: chamfer 0.4–0.8 mm × 45°. Never a fillet on the bed edge.
- Outer vertical corners: round them. They warp less and crack less.
- Internal corners: fillet, at least R 0.5 mm in unfilled plastics and R 1 mm in filled or brittle ones.
- Top edges: chamfer or fillet, both print.

## First layer and solid mass

The first layer is squashed on purpose so it sticks, so the part grows a foot. A chamfer removes the foot from the mating profile. Slicer elephant-foot compensation (often around 0.2 mm on a 0.4 mm nozzle in PrusaSlicer) is the backup, not the design.

Regions thicker than about 4 mm hold heat, shrink unevenly, and waste time. Shell them to a few perimeters and rib the span. Local thickening under a washer is fine; a solid block is not.

## Text and cosmetic faces

Deboss horizontal top faces (the nozzle traces them cleanly). Emboss vertical faces, with a stroke of at least two extrusion widths, because a debossed side wall is a tiny overhang. Avoid text on the bed face.

Seams leave a small ridge. Put the seam on a hidden corner, never on a sliding face. The slicer does this; mention it in the print plan when the part moves.

## When FDM is the wrong process

Stop and switch process, or tell the user the feature must change, when the part needs:

- walls or gaps below one extrusion width
- a tolerance tighter than `tol` on a bore that cannot be drilled
- support-free printing of a shape with no legal orientation
- a flexible hinge in a rigid filament
- isotropy that the load genuinely requires and orientation cannot provide

Resin and SLS rules are in their own files. They are not a way to dodge a redesign that FDM could do with a chamfer.
