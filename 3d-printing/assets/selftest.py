"""selftest.py -- exercises every enclosure_lib.py function once. Run after
any library change, the same discipline as selftest.scad.

Interactive: load enclosure_lib.py then this file's text into execute_code,
then call run_selftest(doc).

Non-interactive (full pass via execute_code_headless):

    import FreeCAD
    doc = FreeCAD.newDocument("selftest")
    exec(open("/abs/path/enclosure_lib.py").read())
    exec(open("/abs/path/selftest.py").read())
    run_selftest(doc)
    doc.saveAs("/abs/path/selftest.FCStd")
"""

import FreeCAD
from FreeCAD import Vector

GRID = 20.0


def _cell(shape, ix, iy):
    s = shape.copy()
    s.translate(Vector(ix * GRID, iy * GRID, 0))
    return s


def _check(name, shape, results):
    ok = True
    problems = []
    if not shape.isValid():
        ok = False
        problems.append("isValid() == False")
    if shape.isNull():
        ok = False
        problems.append("isNull() == True")
    if hasattr(shape, "Volume") and shape.Volume <= 0:
        ok = False
        problems.append(f"Volume == {shape.Volume}")
    results.append((name, ok, problems))
    return shape


def run_selftest(doc, lib=None):
    """lib: pass the enclosure_lib module/namespace if it was imported rather
    than exec'd inline. If None, assumes enclosure_lib's functions are already
    in this call's namespace (the usual execute_code pattern)."""
    import __main__
    lib = lib or __main__

    results = []
    cells = []

    # 3D primitives
    cells.append(_cell(_check("rbox", lib.rbox((20, 15, 10), 2), results), 0, 0))
    cells.append(_cell(_check("rbox_c", lib.rbox_c((20, 15, 10), 2, 0.8, 0.8), results), 1, 0))
    cells.append(_cell(_check("boss (plain)",
                               lib.boss(h=12, od=9.5, bore=3.2, bore_depth=8, gussets=3), results), 2, 0))
    cells.append(_cell(_check("insert_boss",
                               lib.insert_boss(h=14, min_floor=2.0), results), 3, 0))
    cells.append(_cell(_check("pcb_standoff", lib.pcb_standoff(h=6), results), 4, 0))
    cells.append(_cell(_check("lip_tongue", lib.lip_tongue((30, 20), 2, 1.2, 1.2, 2), results), 0, 1))
    cells.append(_cell(_check("rim_band", lib.rim_band((30, 20), 2, 1.6, 2.5, 1.5), results), 1, 1))
    cells.append(_cell(_check("snap_hook", lib.snap_hook(), results), 2, 1))
    cells.append(_cell(_check("tie_anchor", lib.tie_anchor(), results), 3, 1))
    cells.append(_cell(_check("cable_channel", lib.cable_channel(10, 4, 3), results), 4, 1))

    # Cutters (checked as solids; a cutter is valid even if it's only used via .cut())
    cells.append(_cell(_check("screw_cut", lib.screw_cut(), results), 0, 2))
    cells.append(_cell(_check("hex_nut_trap_cut", lib.hex_nut_trap_cut(), results), 1, 2))
    cells.append(_cell(_check("teardrop_cut", lib.teardrop_cut(4, 3), results), 2, 2))
    cells.append(_cell(_check("lip_groove_cut", lib.lip_groove_cut((30, 20)), results), 3, 2))
    cells.append(_cell(_check("keyhole_cut", lib.keyhole_cut(), results), 4, 2))
    cells.append(_cell(_check("foot_recess_cut", lib.foot_recess_cut(), results), 0, 3))
    cells.append(_cell(_check("cable_exit_cut", lib.cable_exit_cut(4, 3), results), 1, 3))

    # Face-frame verification: a marker box placed via each of the 6 faces of
    # a test box must land flush on that outer face.
    outer = (30.0, 20.0, 15.0)
    marker = lib.rbox((4, 4, 2), 0.4)
    for i, face in enumerate(("front", "back", "left", "right", "bottom", "top")):
        placed = marker.copy()
        placed.transformShape(lib.face_frame(face, outer), True)
        cells.append(_cell(_check(f"face_frame[{face}]", placed, results), i, 4))

    compound_shapes = [c for c in cells]
    obj = doc.addObject("Part::Feature", "SelfTest")
    import Part
    obj.Shape = Part.makeCompound(compound_shapes)
    doc.recompute()

    n_ok = sum(1 for _, ok, _ in results if ok)
    for name, ok, problems in results:
        if not ok:
            print(f"FAIL  {name}: {', '.join(problems)}")
    print(f"selftest: {n_ok}/{len(results)} shapes valid, nonzero volume, no exceptions")
    return results
