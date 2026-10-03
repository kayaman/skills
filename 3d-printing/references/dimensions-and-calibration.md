# Dimensions, fits and calibration

## Dimension and calibration contract

Use millimetres and label each value as **nominal**, **per-side clearance**,
**diameter compensation**, or **final CAD dimension**. Show the relationship:
`female_CAD = male_nominal + 2 * clearance_per_side + hole_comp_diameter`.
For a rectangular lid use per-face clearance, not circular-hole compensation.
An insert bore selected directly from a printed coupon is already a final CAD
value: do not add `hole_comp` again. Document whether compensation lives in CAD
or the slicer; do not apply the same correction in both.

House dimensions are conservative design starting points, not calibrated machine
limits or strength guarantees. Nozzle line widths and perimeter overlap vary by
slicer: use the stated extrusion width to choose walls, then verify filled wall
paths in the layer preview. Never promise an exact perimeter count from a width
calculation alone.

A calibration record belongs with the project: printer, nozzle, filament brand
and material, drying state, layer height, orientation, slicer/profile version,
CAD trial dimensions, measured results, and selected values. Mark values
**uncalibrated** until a real coupon is printed and measured. Revalidate after a
change to those conditions; a successful fit is not universal to all hole sizes.

For each critical feature report the input and resulting dimension: outer size,
wall/floor thickness, boss OD, bore diameter/depth, material below the blind bore,
screw engagement, hole-centre spacing, and lid clearance. Distinguish calculation,
rendered-mesh measurement, slicer inspection, and physical measurement. A check
that could not run stays explicitly unverified.

## Parametric enclosures

For enclosures expose named independent inputs and derive mating geometry from
them. Preserve parameter names during edits. Never independently move a lid hole
and its boss. Increasing a bore grows its boss and placement clearance together,
or reports which envelope/PCB constraint prevents growth.

The template retains `boss_od` as the requested minimum. `boss_wall` is the
required radial material and `boss_min_od` the profile minimum; actual OD is
`max(boss_od, boss_min_od, insert_bore + 2 * boss_wall)`. `insert_bore` is a final
CAD value. `insert_relief` sets blind depth beyond `insert_len`; `boss_floor_min`
limits the remaining material under the bore. Check actual screw engagement and
bottom clearance against the selected hardware, not thread size alone.

Read `rhai-design-and-export.md` for enclosure-maker projects and
`freecad-design-and-export.md` for FreeCAD. OpenSCAD uses Customizer inputs above
Hidden; Rhai uses `param(...)` inputs and derived values; FreeCAD keeps inputs in a
top-level `PARAMS` dict in `enclosure_template.py`, grouped like the Customizer, with
derived values computed immediately below it.

See `fits-and-fasteners.md` for insert selection and `mesh-and-export.md` for
mesh verification.
