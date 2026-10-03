# Mesh verification and export

STL contains no unit metadata. Assume mm only when the source/export says so;
compare the bounding box to a known dimension. A factor of 25.4 suggests inches,
but never rescale an unknown part without a reference dimension.

## Run the checker

```sh
python3 scripts/check_stl.py --layer-height 0.2 --grid 0.4 --envelope 170 170 170 --require-bed part.stl
```

The checker uses standard-library Python. Coordinates are interpreted as mm.
Existing `check_stl.py part.stl [more.stl ...]` calls still work. Add `--strict-topology` to promote unmatched facet-edge references to errors in workflows that require exact triangle connectivity; CSG T-junctions can produce these without proving a printed gap. Optional
`--bed-tolerance` defaults to 0.05 mm. Envelope limits apply to extents in the
current orientation; check build-plate placement separately in the slicer.

- `FAIL` and exit 1: malformed/non-finite data, degenerate triangles, open or
  non-manifold edges, inconsistent/inward winding, unexpected separate bodies,
  specified envelope exceeded, or required bed placement failed.
- `WARN` and exit 0: suspected unsupported islands from sampled layers, off-bed
  placement when not required, or sampling skipped because its budget was exceeded.
  Investigate in the slicer; do not call the part print-ready based on this result.
- `ok` and exit 0: no issues found by the listed checks. This does **not** prove
  no self-intersections, sufficient wall thickness, bridge support, fit or strength.
- Invalid CLI options exit 2. Report tool absence or failure as unverified.

Topology uses 0.0001 mm vertex quantization. STL stores triangles without shared vertex indices, and CSG exporters can create T-junctions: unmatched facet-edge references are warnings by default, and become errors only in strict mode. Degenerate facets are reported and excluded while counting the remaining surface. Internal cavity shells are permitted
when contained and oppositely wound. Sampling uses the specified layer height and
XY grid; features smaller than the grid may be missed, and suspected islands can
be false positives. It is not a slicer or a complete solid-validity test. Report
the settings and findings, not a prediction that a particular slicer will repair it.

## Export and inspect

Export each intended printable part separately, in print orientation, bed face at
z=0. Assembly/exploded/check views are not printable exports. A multi-object 3MF
may contain several explicitly named parts; validate each part, not the assembly
as one solid. STL checks do not validate 3MF containers or slicer settings.

Run the native renderer, inspect its warnings, then check the actual export.
Fuse intended bosses/ribs into their parent with deliberate overlap and sufficient
load-bearing section. Let subtractive cutters overshoot cut faces by a small EPS;
measure the exported result because a source expression alone is not proof.
Repair can alter intended geometry. Prefer fixing generated source; for an imported
mesh, preserve the original and validate any repaired copy against critical sizes.

Use at least 64 segments for functional circular holes in final exports. A polygon
inscribed in a circle has across-flats diameter `d * cos(180/n)`; account for that
geometric error separately from print compensation. Preserve intentional polygons
such as hex nut traps. Coarser preview curves are fine when clearly identified.

Inspect slicer layers for missing/thin walls, islands, bridge endpoints/spans,
overhangs, bed contact, and support on fit/sealing faces. Check minimum walls from
source dimensions and section views; this checker does not measure them. Compare
critical exported dimensions against the design and leave physical fits unverified
until the coupon/part has actually been measured.

## Captured hardware

For an embedded magnet/nut, identify the layer before its pocket closes, the pause
height, clearance, and required orientation/polarity. Confirm the layer in the
chosen slicer rather than inferring a pause solely from nominal CAD height.
