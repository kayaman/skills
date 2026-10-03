"""enclosure_template.py -- parametric base + lid enclosure build for the
FreeCAD (MCP) backend. Port of assets/template.scad.

Load assets/enclosure_lib.py into the execute_code session first; this script
calls its functions by name. Edit PARAMS and re-run build_enclosure() to iterate
-- there is no CLI -D override for this backend, so parameters live in the
script text (see references/freecad-design-and-export.md).

Usage (inside one execute_code call, after enclosure_lib.py has been loaded):

    doc = FreeCAD.getDocument("MyEnclosure")  # or FreeCAD.newDocument(...)
    build_enclosure(doc)
    set_view(doc, "assembly")
"""

import FreeCAD
import Part
from FreeCAD import Vector

EPS = 0.01

# ---------------------------------------------------------------------------
# Parameters -- grouped like the OpenSCAD Customizer groups. Derived values
# are computed below, never hand-entered.
# ---------------------------------------------------------------------------

PARAMS = {
    # [Process] -- manufacturing-profiles.md house defaults
    "ew": 0.42,          # extrusion width
    "wall_lines": 3,
    "layer_h": 0.2,
    "tol": 0.25,         # per-side slip clearance

    # [PCB]
    "pcb_x": 55.0, "pcb_y": 40.0, "pcb_t": 1.6,
    "pcb_clear": 0.5,    # lateral clearance per side
    "comp_top": 8.0, "comp_bot": 3.0,

    # [Shell]
    "outer_x": 65.0, "outer_y": 50.0, "outer_z": 28.0,
    "corner_r": 2.0,

    # [Fasteners]
    "insert_bore": 4.1, "insert_len": 5.7, "insert_relief": 1.0,
    "boss_wall": 2.52, "boss_min_od": 9.5,
    "gussets": 3,

    # [Lip]
    "lip_w": 1.2, "lip_inset": 1.2, "lip_h": 2.0,

    # [Ventilation]
    "vent_cell": 4.0, "vent_web": 1.6,
}


def _derived(p):
    """Hidden/derived values -- the direct analog of the .scad template's
    /* [Hidden] */ block. Never hand-enter a value computable from PARAMS."""
    d = dict(p)
    d["wall"] = p["ew"] * p["wall_lines"]
    d["floor_t"] = max(d["wall"], p["layer_h"] * 4)
    d["boss_h"] = d["floor_t"] + p["comp_top"]
    d["boss_od"] = max(p["boss_min_od"], p["insert_bore"] + 2 * p["boss_wall"])
    d["cavity_x"] = p["pcb_x"] + 2 * p["pcb_clear"]
    d["cavity_y"] = p["pcb_y"] + 2 * p["pcb_clear"]
    return d


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_base(lib, p=None):
    """Returns the base part as a raw Part.Shape. `lib` is the enclosure_lib
    module/namespace (its functions, already loaded in this session)."""
    d = _derived(p or PARAMS)
    outer = (d["outer_x"], d["outer_y"], d["outer_z"])

    shell = lib.rbox_c(outer, d["corner_r"], cb=0.8, ct=0.0)
    cavity_h = d["outer_z"] - d["floor_t"]
    cavity = lib.rbox((d["cavity_x"], d["cavity_y"], cavity_h + EPS), max(d["corner_r"] - d["wall"], 0.4))
    cavity.translate(Vector((d["outer_x"] - d["cavity_x"]) / 2.0,
                             (d["outer_y"] - d["cavity_y"]) / 2.0,
                             d["floor_t"]))
    base = shell.cut(cavity)

    inset = d["wall"] + d["boss_od"] / 2.0 + 1.0
    corner_xy = [
        (inset, inset), (d["outer_x"] - inset, inset),
        (inset, d["outer_y"] - inset), (d["outer_x"] - inset, d["outer_y"] - inset),
    ]
    for cx, cy in corner_xy:
        column = lib.insert_boss(
            h=d["boss_h"], od=d["boss_od"], bore=p["insert_bore"] if p else PARAMS["insert_bore"],
            insert_len=d["insert_len"], relief=d["insert_relief"],
            gussets=d["gussets"], gusset_t=d["wall"], min_floor=d["floor_t"],
        )
        column.translate(Vector(cx, cy, d["floor_t"]))
        base = base.fuse(column)

    tongue = lib.lip_tongue((d["outer_x"], d["outer_y"]), d["corner_r"], d["lip_inset"], d["lip_w"], d["lip_h"])
    tongue.translate(Vector(0, 0, d["outer_z"]))
    base = base.fuse(tongue)

    # One free side wall gets a vent panel (the side opposite the corner
    # columns' widest span), cut via face_frame + a hex pattern cutter.
    vent_area = (d["outer_x"] - 4 * d["wall"], d["outer_z"] - d["floor_t"] - 2 * d["wall"])
    vent_profile = lib.hex_pattern_2d(vent_area, d["vent_cell"], d["vent_web"])
    vent_cutter = lib.wall_cut("front", (d["outer_x"], d["outer_y"], d["outer_z"]), d["wall"], vent_profile)
    vent_cutter.translate(Vector(2 * d["wall"], 0, d["floor_t"] + d["wall"]))
    base = base.cut(vent_cutter)

    return base.removeSplitter()


def build_lid(lib, p=None):
    d = _derived(p or PARAMS)
    outer = (d["outer_x"], d["outer_y"], d["lip_h"] + d["tol"] + d["wall"])
    lid = lib.rbox_c(outer, d["corner_r"], cb=0.0, ct=0.8)
    groove = lib.lip_groove_cut((d["outer_x"], d["outer_y"]), d["corner_r"], d["lip_inset"],
                                 d["lip_w"], d["lip_h"] + d["tol"], 2 * d["tol"])
    lid = lid.cut(groove)
    return lid.removeSplitter()


def commit_parts(doc, lib, p=None):
    """Builds base + lid and adds exactly one Part::Feature per printable
    part. Run inside execute_code (GUI thread) -- see
    references/freecad-design-and-export.md for why this must not run
    through execute_code_async without routing the writes through commit()."""
    d = _derived(p or PARAMS)
    base_shape = build_base(lib, p)
    lid_shape = build_lid(lib, p)

    base_obj = doc.getObject("Base") or doc.addObject("Part::Feature", "Base")
    base_obj.Shape = base_shape

    lid_obj = doc.getObject("Lid") or doc.addObject("Part::Feature", "Lid")
    lid_obj.Shape = lid_shape
    lid_obj.Placement = FreeCAD.Placement(Vector(0, 0, d["outer_z"]), FreeCAD.Rotation())

    doc.recompute()
    return base_obj, lid_obj


# ---------------------------------------------------------------------------
# View / part selection -- the no-CLI equivalent of the .scad `part` switch
# ---------------------------------------------------------------------------

EXPLODE_DZ = 30.0


def set_view(doc, mode):
    """mode: assembly | exploded | base | lid | section | check.
    Toggles Visibility/Placement on the committed Base/Lid objects; no CLI -D
    equivalent exists for this backend, so this is how `part` selection is
    expressed on a live document."""
    base = doc.getObject("Base")
    lid = doc.getObject("Lid")
    check_obj = doc.getObject("CheckInterference")
    if check_obj:
        check_obj.Visibility = False

    if mode == "base":
        base.Visibility, lid.Visibility = True, False
    elif mode == "lid":
        base.Visibility, lid.Visibility = False, True
    elif mode == "assembly":
        base.Visibility, lid.Visibility = True, True
        lid.Placement.Base.z = PARAMS["outer_z"]
    elif mode == "exploded":
        base.Visibility, lid.Visibility = True, True
        lid.Placement.Base.z = PARAMS["outer_z"] + EXPLODE_DZ
    elif mode == "section":
        base.Visibility, lid.Visibility = True, True
        lid.Placement.Base.z = PARAMS["outer_z"]
        # A transient half-space cut for inspection; never exported.
        d = _derived(PARAMS)
        half = Part.makeBox(d["outer_x"], d["outer_y"] / 2.0, d["outer_z"] * 3,
                             Vector(0, 0, -d["outer_z"]))
        assembled = base.Shape.fuse(lid.Shape.transformGeometry(lid.Placement.toMatrix()))
        section_obj = doc.getObject("Section") or doc.addObject("Part::Feature", "Section")
        section_obj.Shape = assembled.cut(half)
        base.Visibility, lid.Visibility = False, False
        section_obj.Visibility = True
    elif mode == "check":
        world_lid = lid.Shape.transformGeometry(lid.Placement.toMatrix())
        inter = base.Shape.common(world_lid)
        check_obj = check_obj or doc.addObject("Part::Feature", "CheckInterference")
        check_obj.Shape = inter
        print(f"interference volume: {inter.Volume:.4f} mm^3 "
              f"({'PASS' if inter.isNull() or inter.Volume < 1e-3 else 'FAIL'})")
        base.Visibility, lid.Visibility = False, False
        check_obj.Visibility = not (inter.isNull() or inter.Volume < 1e-3)
    else:
        raise ValueError(f"set_view: unknown mode '{mode}'")

    doc.recompute()
