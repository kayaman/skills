# Meshes and export

Read this when the user hands over an STL or 3MF, or when you are exporting a model you wrote.

## Reviewing a mesh someone else made

Check these in order and stop at the first one that fails. Each is cheaper than the next.

1. **Units.** STL carries no units, and every slicer assumes millimetres. A part that is 25.4× too small was drawn in inches. One that is 10× or 1000× off was drawn in centimetres or metres. Read the bounding box before anything else and say what you found.
2. **Envelope.** Compare the bounding box against the profile envelope in every orientation you might use, not just the one it arrived in.
3. **Closed and manifold.** Open edges, flipped normals, and self-intersections make the slicer guess. A repair can fill a hole the user wanted or drop a thin wall. If the slicer reports a repair, or a tool below finds open edges, say so before discussing strength.
4. **Bed face.** A part with no flat face covering most of its footprint needs a new orientation or a split. The slicer's lay-on-face tool finds candidates; it does not know which face is cosmetic.
5. **Walls and overhangs.** Slice it and read the layer preview. Walls that preview as a single line or as gap fill are thinner than the profile wall. Overhang highlighting (Bambu Studio and OrcaSlicer show it in the prepare view) finds faces past the limit.
6. **Holes and fits.** Measure functional holes in the mesh. A vertical hole drawn at exactly the screw diameter will not take the screw.

Tools, if present. Do not claim a check ran when the tool is missing:

```bash
admesh part.stl
python3 -c "import trimesh; m = trimesh.load('part.stl'); print(m.extents, m.is_watertight, m.is_winding_consistent)"
```

`admesh` prints the size and repair counts. Non-zero edges fixed, facets added, or backwards edges mean the mesh was not closed. Without either tool, the slicer's repair warning is the check.

## Editing a mesh without the source

Small fixes do not need a rebuild. OpenSCAD imports a closed STL and applies booleans to it:

```openscad
difference() {
    import("bracket.stl");
    translate([12, 8, -0.01]) cylinder(d = 3.4 + 0.15, h = 10, $fn = 64);
}
```

That covers opening a hole, adding a chamfer by subtracting a wedge, cutting a split plane for the envelope, and adding dowel pockets. An import that is not manifold makes CGAL fail or produce garbage; repair it first. Anything beyond local edits is a rebuild, and the user should decide whether it is worth it.

## Exporting a model you wrote

- **One file per part**, each placed in its print orientation with the bed face on z = 0. The slicer should not need to rotate it. The export command lists every part.
- **Resolution.** A circle with `n` segments is a polygon inside the true circle, so a hole prints smaller before the plastic does anything. Across flats the diameter is `d · cos(180° / n)`. At `$fn = 32` that is about 0.5% under, at 64 about 0.1%. Use `$fa = 1` and `$fs = 0.2` or an explicit `$fn` ≥ 64 on functional holes for export. A low `$fn` in preview is fine.
- **Coincident faces.** Extend every subtracted solid past the faces it cuts by a small `eps` (0.01 mm). A difference that ends exactly on a face leaves a zero-thickness skin that some slicers print.
- **STL or 3MF.** STL is universal. 3MF carries units, several objects, and in Bambu Studio and OrcaSlicer a whole project with its settings. OpenSCAD writes 3MF only when it was built with lib3mf (`openscad --info` shows it); otherwise export STL and say so.
- **Render time.** OpenSCAD's CGAL backend on older releases takes minutes on parts with many holes or text. Newer builds with the Manifold backend are much faster. A slow export is not a broken model.

## Pausing to embed a part

For a captured magnet, nut, or insert that must sit inside the print, give the Z height of the first layer that closes the pocket, rounded up to a whole layer. That is the layer to pause before. In Bambu Studio and OrcaSlicer, right-click that layer on the preview slider and add a pause. PrusaSlicer uses the same slider with a colour-change or pause marker. Tell the user which parts go in and, for magnets, which way up.
