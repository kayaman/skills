---
name: 3d-printing
description: Design, review, calibrate, and prepare parts for FDM, resin, or SLS printing. Use for printability, materials, orientation, wall thickness, fits, fasteners, STL/3MF checks, slicer settings, and failed prints. For electronics enclosure geometry, use parametric-enclosures alongside this process skill.
---

# 3D printing

Printed parts fail in a few repeatable ways. A fit face is scarred by supports. A load peels the layers apart. A hole prints small and a screw will not start. A clip cracks because the plastic is filled and brittle. The part does not fit the machine. Fix those in the process choice and the geometry. A slicer setting is the second move, and only after the shape is printable.

Numbers in the references are starting points from printer vendors (Prusa, Bambu, Formlabs) and from desktop FDM practice. A fit coupon printed on the actual machine overrides every one of them.

## What this skill owns

This is the process skill: which machine, which material, which way up, what the slicer must do, and whether the shape can survive that.

Electronics enclosures, cases, housings, and "caixa" jobs belong to the parametric-enclosures skill. That skill already has the house printer profile, screw columns, PCB clearances, vents, the OpenSCAD library, and the wiring and power rules. Do not invent a second enclosure. If that skill is not available, say so and answer only the print-process part of the question.

Match the length of the reply to the question. A material comparison does not need a print plan. The full contract below is for a part you are designing or clearing to print.

## Read only what the job needs

| When the job involves… | Read |
|---|---|
| Critical dimensions, holes, mating parts or a fit coupon | `references/dimensions-and-calibration.md` |
| Any FDM part, before writing dimensions | `references/house-profile.md` — the printer and material override generic numbers |
| FDM walls, overhangs, holes, orientation, strength | `references/fdm.md` |
| Choosing or swapping a plastic | `references/materials.md` |
| Fits, inserts, screws, snaps, threads, hinges, magnets | `references/fits-and-fasteners.md` |
| A slicer plan, calibration, or a print that already failed | `references/slicer-and-troubleshooting.md` |
| Resin (SLA/MSLA), or a feature FDM cannot hold | `references/resin.md` |
| SLS or MJF, usually a bureau | `references/sls.md` |
| An STL or 3MF to review or fix, or a model you are exporting | `references/mesh-and-export.md`, then `scripts/check_stl.py` on every STL |

Copy `assets/fit-coupon.scad` when a clearance has to be measured rather than guessed. It sets `hole_comp`, `tol`, and the insert bore in one print of about 84 × 57 mm. Change its parameters for another nozzle or insert; do not redraw it.

## Workflow

1. **Classify the job.** New part, design review of an existing model, print plan for a mesh, failed print, or a material question. Failed prints start in `references/slicer-and-troubleshooting.md` and come back here only if the fix is geometry. A mesh starts with the units, envelope, and manifold checks in `references/mesh-and-export.md`.
2. **Pick the process.** Desktop FDM on the house profile unless the part cannot succeed there or the user names another process. See the table below.
3. **Load the profile** in `references/house-profile.md`. Use it without asking. A named printer or material replaces it; write the override down and recompute anything that came from extrusion width.
4. **Decide orientation before shape.** The bed face, the weak axis, and which face may be sacrificed determine the geometry. Infer the load from how the part is used and tag that inference as an assumption.
5. **Change the geometry** so the part prints without supports on a working face, so the load does not peel layers, and so the part is one solid with no island in the air. A warning in the reply is not a fix.
6. **Export and check.** One STL per part, bed face on z = 0. Run the standard-library `scripts/check_stl.py` with the selected envelope, layer height and `--require-bed`. Fix measured errors; resolve sampled warnings in the slicer. An `ok` result covers only the checks listed in the report; it does not certify printability.
7. **Deliver** the contract that matches the job, then run the self-check.

## Process choice

The house machine is an open-frame FDM printer. Recommend another process only when FDM cannot do the job, and say what the user must own or order.

| The part needs… | Use |
|---|---|
| A bracket, jig, fixture, replacement, or anything larger than a few centimetres | FDM, house profile |
| A feature thinner than one extrusion, crisp tiny text, or a smooth small cosmetic part | Resin, if they have a printer or will order one. Read `references/resin.md` |
| Enclosed channels, a batch of complex nylon parts, or no support scars on every face | SLS/MJF at a bureau. Read `references/sls.md` |
| A seal, grip, bumper, or flexure | FDM TPU. That is not the house material |
| A snap, clip, or living hinge | Unfilled PETG, nylon, PP, or TPU. Not house PETG-CF; switch the profile to unfilled PETG on the same printer |
| Outdoor UV | ASA on an enclosed printer, or unfilled PETG for mild exposure. PETG-CF is stiff, not a UV or high-heat material |
| Heat above about 70 °C (car cabin, near a heater) | Not PLA and not house PETG-CF. ABS, ASA, PC, or a higher-temp filled nylon/PET on an enclosed printer |

If the user already has a mesh, review it against the chosen process. Do not rebuild it in another CAD tool unless they ask.

## Rules that apply to every FDM part

The profile overrides the numbers. The reasons live in `references/fdm.md`.

- Choose walls and ribs around whole extrusion widths, and floors around whole layer heights. Use this as a house design target; confirm actual perimeter coverage in the slicer, which may vary line width and overlap.
- Overhangs stay at or under the profile limit, measured from vertical. Steeper than that needs a chamfer, a teardrop, or a different orientation. Supports on a fit, seal, or sliding face are a design failure.
- Horizontal holes print oval. Above the profile's teardrop threshold, use a teardrop or a flat bridged top, or plan to drill.
- Vertical holes print small. Add the profile's hole compensation on functional diameters only.
- Chamfer every edge that runs parallel to the bed, including the bed contact and the underside of a lip. A fillet there starts as a flat overhang. Fillet vertical edges, and fillet a loaded internal corner without thinning the wall. On filled or brittle plastic the inside radius is at least 1 mm. Details in `references/fdm.md`.
- Nothing solid thicker than about 4 mm. Hollow it and rib it. Thick lumps warp and do not get stronger in proportion.
- The part is weakest between layers. Tension and bending stay in the XY plane of the print. A screw that pulls a flange apart along Z is peeling the stack.
- Every part fits the profile envelope, or it is split and joined with fasteners and dowels. Do not specify cyanoacrylate on PETG or PETG-CF; it does not hold.
- One named clearance drives each fit. "Make it tight" is not a dimension.
- A body and a lid must fit. A plate the same size as the box, resting on the rim, is not a fit: it slides, and a zero gap binds once the first layer spreads. Give them a tongue, an internal lip, or a stepped lap, with the slip clearance on each mating face. Details in `references/fits-and-fasteners.md`.
- Each exported part is one solid. Fuse intended features with a deliberate overlap and check the exported topology. Keep a structural neck wide enough for its load; two extrusion widths is only a geometric starting minimum.
- Nothing starts in mid-air. In the print orientation every region has plastic under it, down to the bed, or it is a bridge within the profile limit whose ends land on walls. An island is a modeling error, including one that rejoins the body only higher up.
- The STL topology is checked before it reaches Bambu Studio. Every edge has two faces, windings agree, and there are no collapsed triangles. Clicking Repair is not a step in the plan. Repair can change intended holes or thin walls; inspect the result instead of assuming equivalence. Details and the checker are in `references/mesh-and-export.md`.

## Fasteners in one pass

Read `references/fits-and-fasteners.md` before drawing a boss. Short version, so a casual answer does not invent a hole:

- Repeated assembly: heat-set insert. Select bore shape and dimensions from the actual manufacturer and validate the final CAD bore on a coupon. House M3 starts at 9.5 mm boss OD and at least 2.5 mm radial plastic; grow the OD for larger bores. See `references/fits-and-fasteners.md`.
- A few assemblies, then never again: self-tapping or thread-forming screw. Pilot about 0.8 × major diameter, engagement at least 2 × diameter.
- Printed threads are for coarse, lightly loaded closures. Below about M5, use an insert.
- Snaps and living hinges follow the strain limit in the fasteners reference, and only in a material that can flex. On house PETG-CF, offer screws or a switch to unfilled PETG. If the user insists on a PETG-CF clip, apply the limits in `references/house-profile.md` and put the fatigue risk in Watch-out.

## Output contract

For a part being designed or cleared to print:

```
## Process
<FDM / resin / SLS> on <profile>. <Why this process.>

## Orientation
Bed face: <which face, and why>
Load path: <where tension and bending sit relative to the layers>
Sacrificed face: <none, or the face that may carry support scars>

## Geometry
<Walls, fits, fasteners, and the shapes changed so it prints and holds.>

## Mesh
<When a file was written: one solid, bed on z = 0, and the check_stl.py line. Report the actual Bambu Studio result; investigate any repair prompt or warning there, since the mesh checker is advisory for some edge patterns.>

## Print plan
<Layer height, walls, infill, brim, supports, nozzle, drying, and any pause-at-layer height. Use Bambu Studio setting names and the A1 Mini preset in references/slicer-and-troubleshooting.md unless the user named another slicer. Supports must read "none" unless a face was sacrificed on purpose. X-Y hole compensation is 0 when the model already has hole_comp. Make overhangs printable stays off.>

## Watch-out
<The single most likely failure, and the check that prevents it.>

## Assumptions
<Every value the user did not give.>
```

For a design review, replace Geometry with a punch list ordered as: will not print, will fail in use, will look bad. Quote the dimension that is wrong and the dimension to use.

For a failed print, use the diagnosis shape in `references/slicer-and-troubleshooting.md`: most likely cause, the observation that confirms it, one fix. Geometry first, then a single slicer change.

For a mesh review, report units, bounding box, and manifold status first, then the punch list. Say which checks ran with a tool and which were done by reading the model.

Write files to disk when the user asked for a model. Do not paste a long script into the reply when a file is what they will print. Export one file per part, bed face on z = 0, following `references/mesh-and-export.md`.

## Self-check

Before sending a design or a clearance:

- The critical load is not peeling layers, or the part was reoriented.
- No support lands on a fit, seal, or sliding face.
- FDM walls are a whole number of extrusion widths from the profile in force.
- Each fit has a named clearance. Every functional vertical hole carries `hole_comp` or a drill note, and not both `hole_comp` and slicer hole compensation.
- A body and a lid locate each other. A rim-to-rim plate fails this check.
- The part fits the envelope, or the split and the fasteners are specified.
- Profile bans are respected. On house PETG-CF that means no snaps, clips, or living hinges unless the user insisted, the house-profile limits are applied, and the risk is stated.
- Any exported file is one part per file, in print orientation, with functional holes at `$fn` ≥ 64.
- Every STL has passed the reported topology, envelope and bed checks. Sampled island findings have been inspected in the slicer; self-intersections, wall thickness and strength are not certified by this checker.
- The print plan names the Bambu Studio printer, process, and plate presets when that is the slicer, and it leaves hole compensation and overhang rewriting off.
- Heat, UV, food, and mains were either handled or marked not applicable. Printed plastic is not a certified insulator or a flame barrier unless the spool says so, and layer lines are not food-safe.

If a check fails, change the part. Do not ship the failure as a note.
