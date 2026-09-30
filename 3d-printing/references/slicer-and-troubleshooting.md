# Slicer plan and failed prints

The slicer executes the design. It does not rescue a horizontal hole, a peel load, or a wall that is not a whole number of lines. Set the plan from the profile, then change one thing at a time when a print fails.

## Functional print plan (0.4 mm nozzle)

Use these unless the profile says otherwise. The house PETG-CF profile overrides walls, floors, bridges, and fan behavior.

| Setting | Working choice | Why |
|---|---|---|
| Layer height | 0.20 mm | Default. 0.12–0.16 mm when a vertical curve must look smooth. Up to about 75% of the nozzle (0.28 mm on a 0.4) for a draft. Stay at or above 0.16 mm on PETG-CF if the nozzle is collecting blobs |
| Walls | 4 for a normal functional part; 6 on house PETG-CF | Strength is in the perimeters. Raising infill from 20% to 80% does less than adding two walls, and it increases warp |
| Top / bottom | ≥ 4 solid layers | So infill does not show through and the skin can take a compressive load |
| Infill | 15–25% gyroid or cubic | Enough to support the top skins. Go denser only under a crushing load or a fastener. Do not fill a part 100% to "make it strong" |
| Supports | None | If a face was sacrificed on purpose, name it and paint support only there |
| Brim | When the profile says so, or the footprint is small | House rule: height > 2.5 × the smallest base dimension |
| Seam | A hidden corner, not a sliding face | The seam is a ridge |
| Elephant foot | Compensation around 0.2 mm if the slicer has it, after the CAD chamfer | Backup for the first-layer squish |
| Cooling | High on PLA. Modest on PETG, ABS, nylon, and filled PETG | Fan makes prettier overhangs and weaker layer bonds. On an open printer with PETG-CF, prefer the bond |

Outer walls slightly slower than infill. That is a surface setting, not a strength setting.

Arachne / variable line width can fill an awkward gap. Still design to `n * ew` so the part does not depend on it.

## Setting names by slicer

Write the print plan with the name the user's slicer shows. The house printer is a Bambu, so default to Bambu Studio names.

| Plan term | Bambu Studio / OrcaSlicer | PrusaSlicer | Cura |
|---|---|---|---|
| Walls | Wall loops | Perimeters | Wall Line Count |
| Top / bottom | Top shell layers / Bottom shell layers | Solid layers: Top / Bottom | Top Layers / Bottom Layers |
| Infill | Sparse infill density, Sparse infill pattern | Fill density, Fill pattern | Infill Density, Infill Pattern |
| Supports | Enable support, plus support painting | Generate support material, plus paint-on supports | Generate Support, plus support blockers |
| Brim | Brim type | Brim width | Build Plate Adhesion Type |
| Seam | Seam position | Seam position | Z Seam Alignment |
| Elephant foot | Elephant foot compensation | Elephant foot compensation | Initial Layer Horizontal Expansion (negative) |
| Hole compensation | X-Y hole compensation | None for holes only; do it in CAD | Hole Horizontal Expansion |

Prefer `hole_comp` in the model over the slicer's hole compensation. A slicer value applies to every hole, including the ones that were already sized, and it is invisible to whoever opens the model next. Use one or the other, never both.

## Calibration order

Do this once per material, not once per part. Stop at the first step that explains the error.

1. **Dry the spool.** Wet filament imitates every other fault.
2. **Flow.** A single-wall cube should measure as the extrusion width you set. Fix flow before any clearance.
3. **Pressure advance** (linear advance). Corners stop bulging, holes get rounder. This is why a "calibrated" printer suddenly misses fits after a nozzle change.
4. **Temperature.** Only for a new material. Too cold splits layers; too hot strings and sags.
5. **Fit coupon** (`assets/fit-coupon.scad`) for `hole_comp`, then `tol`, then the insert bore. The header of that file says how to read each row.

A single tight hole is hole compensation, elephant's foot, or a worn nozzle. It is not a reason to redo the whole calibration or to scale the STL.

## Diagnosing a failed print

Name one cause, the observation that would confirm it, and one fix. Geometry first when both could be true.

| What the user sees | Most likely cause | Confirm | Fix |
|---|---|---|---|
| Popping, stringing, cloudy or rough surface | Wet filament | Sound, or it got worse after the spool sat out | Dry it. Then drop nozzle temperature about 5 °C if hairs remain |
| Splits along layer lines, part is brittle | Weak welds: wet, too much fan, too cold, too fast, or the load is in Z | The crack is flat and between layers, not through a wall | Dry, less fan, +5–10 °C, slower. If the crack is where the design peels layers, reorient. On open-frame PETG-CF, do not expect enclosed-printer Z strength |
| Corners lift, base warped | Shrinkage plus a sharp, wide base | Worse in ABS/ASA/nylon; starts at the corners | Brim, round the corners, enclosure. Do not fight ABS on the open A1 Mini |
| Base flange, parts will not seat | Elephant's foot | Only the first layer is fat | CAD chamfer, then slicer compensation. Less first-layer squish if adhesion allows |
| Screws and pins too tight, outside dimensions OK | Vertical holes print small | A drilled hole of the same CAD size fits | `hole_comp`, or drill. Do not scale the whole part |
| PETG stuck to the sheet, sheet at risk | Bare smooth PEI | The part is fused, not just stuck | Glue stick as a release layer. Prefer the textured plate |
| Clogs, or dimensions drifting over a spool of filled filament | Brass nozzle wearing, wet filament, or a 0.2 mm nozzle | Orifice looks oval, or fiber filament was the change | Hardened steel, ≥ 0.4 mm, 0.6 mm if clogs continue. Dry |
| Echoes after corners | Speed and acceleration | The model is fine; the ghost follows direction changes | Slower outer wall. Input shaping is a printer calibration |
| Fit face is scarred and undersize | Support was on a working face | The bad face was an overhang | Reorient or chamfer so that face is a bed face or a vertical wall |
| Layer shift | Mechanical: belt, nozzle crash, warped part catching the nozzle | The shift is a single step in X or Y | Check the machine. A catching overhang is still a geometry problem |
| Spaghetti after the first layers | Lost adhesion, or a feature printed in air | The first layer let go, or a mid-air island exists | Brim or a cleaner plate for adhesion. An island with no support is a modeling error |

If the user sends a photo or a description that matches two rows, take the row that is fixed by drying or by orientation before the row that is fixed by a long calibration.

## What not to change

- Do not add a raft to hide a warped design.
- Do not raise infill to 100% to fix a layer split.
- Do not turn on supports for the whole part because one ledge is 50°.
- Do not recommend a different filament until the current one has been dried and the load path has been checked. A material swap is a real answer when the temperature or the toughness is wrong, and a stall when the part is wet.
