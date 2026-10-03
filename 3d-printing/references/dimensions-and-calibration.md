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

See `fits-and-fasteners.md` for insert selection and `mesh-and-export.md` for verification.
