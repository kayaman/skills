"""enclosure_lib.py -- reusable geometry for 3D-printed electronics enclosures
built on FreeCAD's Part/Draft API, for the 3d-printing skill's
FreeCAD (MCP) backend. v1.0. Units: mm.

Port of assets/enclosure_lib.scad. Same module names and parameter names as the
OpenSCAD library wherever the concept is identical, so the user's mental model
transfers. See references/freecad-design-and-export.md for the execute_code /
execute_code_async / execute_code_headless rules this library is loaded under.

Architecture: every function here returns a raw Part.Shape (a solid, or for the
`face` section a FreeCAD.Placement) -- never a committed document object.
Composition (fuse/cut) happens in plain Python on these raw shapes; the caller
adds exactly one Part::Feature per printable part once composition is done. This
keeps the document tree small and keeps execute_code_async safe to use for the
heavy booleans (no incremental document writes to route through commit()).

Load this file's text into an execute_code session once; its functions persist
in that session's namespace for later calls. execute_code_headless does not
share that namespace and must exec() this file itself every time.

Deliberate deviations from the 1:1 OpenSCAD module list:
  * fillet_lin / fillet_ring have no port -- OpenSCAD has no native fillet, so
    the .scad library hand-rolled ring/linear fillet substitutes. FreeCAD has
    real B-rep fillets (Shape.makeFillet), so every call site below uses that
    directly. fillet_edges_at_z() is the one small helper kept, for the
    recurring "select the floor-junction edges" case.
  * explode() is not here -- it mutated a document object's Placement in the
    .scad version, which has no equivalent on a bare Shape. It lives in
    enclosure_template.py's set_view() instead.
"""

import math

import FreeCAD
import Part
from FreeCAD import Vector

EPS = 0.01


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def poly_d(d, n):
    """Diameter to give an n-gon so its FLATS clear a round part of diameter d."""
    return d / math.cos(math.pi / n)


def tie_anchor_size(tie_w=2.5, tie_t=1.1, length=5, side=1.68,
                     roof=2.0, clear=0.5, flare=1.0):
    """Outer [x, y, z] size of tie_anchor() called with the same arguments."""
    return (length + 2 * flare,
            tie_w + clear + 2 * side + 2 * flare,
            tie_t + clear + roof)


# ---------------------------------------------------------------------------
# 2D primitives -- each returns a Part.Face (filled profile) in the XY plane
# at z = 0, unless noted. Extrude with .extrude(Vector(0, 0, h)).
# ---------------------------------------------------------------------------

def _rrect_wire(size, r=2.0):
    """Closed Part.Wire for a rounded rectangle, lower-left corner at origin.
    r = 0 gives a plain rectangle."""
    sx, sy = float(size[0]), float(size[1])
    if r <= 0:
        pts = [Vector(0, 0, 0), Vector(sx, 0, 0), Vector(sx, sy, 0),
               Vector(0, sy, 0), Vector(0, 0, 0)]
        return Part.Wire(Part.makePolygon(pts))
    if r > min(sx, sy) / 2:
        raise ValueError("rrect: corner radius too large")

    c_br = Vector(sx - r, r, 0)
    c_tr = Vector(sx - r, sy - r, 0)
    c_tl = Vector(r, sy - r, 0)
    c_bl = Vector(r, r, 0)

    edges = [
        Part.makeLine(Vector(r, 0, 0), Vector(sx - r, 0, 0)),
        Part.makeCircle(r, c_br, Vector(0, 0, 1), -90, 0),
        Part.makeLine(Vector(sx, r, 0), Vector(sx, sy - r, 0)),
        Part.makeCircle(r, c_tr, Vector(0, 0, 1), 0, 90),
        Part.makeLine(Vector(sx - r, sy, 0), Vector(r, sy, 0)),
        Part.makeCircle(r, c_tl, Vector(0, 0, 1), 90, 180),
        Part.makeLine(Vector(0, sy - r, 0), Vector(0, r, 0)),
        Part.makeCircle(r, c_bl, Vector(0, 0, 1), 180, 270),
    ]
    return Part.Wire(edges)


def rrect(size, r=2.0):
    """Rounded rectangle face, lower-left corner at origin."""
    return Part.Face(_rrect_wire(size, r))


def rrect_inset(size, r=2.0, d=0.0):
    """Rounded rectangle face inset by d on all sides, concentric with rrect(size, r)."""
    inset_size = (size[0] - 2 * d, size[1] - 2 * d)
    face = rrect(inset_size, max(r - d, 0.4))
    face.translate(Vector(d, d, 0))
    return face


def rrect_c(size, r=1.0):
    """Rounded rectangle face centred on the origin."""
    face = rrect(size, min(r, min(size[0], size[1]) / 2))
    face.translate(Vector(-size[0] / 2, -size[1] / 2, 0))
    return face


def teardrop_2d(d):
    """Teardrop for horizontal holes: circle with a 45 deg roof pointing +Y."""
    r = d / 2.0
    circle = Part.Face(Part.Wire(Part.makeCircle(r)))
    roof_pts = [Vector(0, 0, 0), Vector(r, 0, 0), Vector(r, r, 0), Vector(0, 0, 0)]
    # 45 deg right triangle, hypotenuse rotated 45 deg about the origin, matching
    # the .scad `rotate(45) square([r, r])` roof
    roof = Part.Face(Part.Wire(Part.makePolygon(roof_pts)))
    roof.rotate(Vector(0, 0, 0), Vector(0, 0, 1), 45)
    return circle.fuse(roof).removeSplitter()


def hole_2d(d, td=False):
    """Round hole profile, or a teardrop (roof toward +Y) when td = True."""
    if td:
        return teardrop_2d(d)
    return Part.Face(Part.Wire(Part.makeCircle(d / 2.0)))


def slot_pattern_2d(area, slot_w=2.0, pitch=5.0):
    """Vertical stadium slots filling area = (w, h), centred along w.
    Keep pitch >= slot_w + wall: the webs are structure. Returns a Part.Face
    (may be a Compound of faces fused), or None if nothing fits."""
    n = int(math.floor((area[0] - slot_w) / pitch)) + 1
    if n <= 0 or area[1] < slot_w:
        return None
    x0 = (area[0] - ((n - 1) * pitch + slot_w)) / 2.0
    slots = []
    for i in range(n):
        cx = x0 + i * pitch + slot_w / 2.0
        bottom = Vector(cx, slot_w / 2.0, 0)
        top = Vector(cx, area[1] - slot_w / 2.0, 0)
        edge = Part.makeLine(bottom, top)
        # stadium = hull of two circles -> approximate with a wire: two half
        # circles joined by two tangent lines, built via a 2-point wire offset
        wire = Part.Wire([
            Part.makeCircle(slot_w / 2.0, bottom, Vector(0, 0, 1), -180, 0),
            Part.makeLine(Vector(cx + slot_w / 2.0, bottom.y, 0), Vector(cx + slot_w / 2.0, top.y, 0)),
            Part.makeCircle(slot_w / 2.0, top, Vector(0, 0, 1), 0, 180),
            Part.makeLine(Vector(cx - slot_w / 2.0, top.y, 0), Vector(cx - slot_w / 2.0, bottom.y, 0)),
        ])
        slots.append(Part.Face(wire))
    result = slots[0]
    for s in slots[1:]:
        result = result.fuse(s)
    return result.removeSplitter()


def hex_pattern_2d(area, cell=4.0, web=1.6):
    """Pointy-top honeycomb clipped to area = (w, h); cell = across-flats opening.
    A vertex points up (+Y), matching the .scad convention."""
    dx = cell + web
    dy = dx * math.sqrt(3) / 2.0
    cells = []
    n_rows = int(math.ceil(area[1] / dy)) + 1
    n_cols = int(math.ceil(area[0] / dx)) + 2
    for j in range(n_rows):
        for i in range(-1, n_cols):
            cx = i * dx + (j % 2) * dx / 2.0
            cy = j * dy
            hexagon = _regular_polygon_face(cell / math.cos(math.radians(30)), 6, rotation=30)
            hexagon.translate(Vector(cx, cy, 0))
            cells.append(hexagon)
    pattern = cells[0]
    for c in cells[1:]:
        pattern = pattern.fuse(c)
    pattern = pattern.removeSplitter()
    clip = rrect((area[0], area[1]), 0)
    return pattern.common(clip)


def _regular_polygon_face(circumradius, n, rotation=0.0):
    pts = []
    for k in range(n):
        ang = math.radians(rotation) + 2 * math.pi * k / n
        pts.append(Vector(circumradius * math.cos(ang), circumradius * math.sin(ang), 0))
    pts.append(pts[0])
    return Part.Face(Part.Wire(Part.makePolygon(pts)))


def keyhole_2d(d_big=7.0, d_small=3.5, length=8.0):
    """Keyhole: head opening at origin, slot runs toward -Y so the part hangs
    down onto the screw."""
    head = Part.Face(Part.Wire(Part.makeCircle(d_big / 2.0)))
    bottom = Vector(0, -length, 0)
    slot = Part.Face(Part.Wire([
        Part.makeCircle(d_small / 2.0, Vector(0, 0, 0), Vector(0, 0, 1), 0, 180),
        Part.makeLine(Vector(-d_small / 2.0, 0, 0), Vector(-d_small / 2.0, -length, 0)),
        Part.makeCircle(d_small / 2.0, bottom, Vector(0, 0, 1), 180, 360),
        Part.makeLine(Vector(d_small / 2.0, -length, 0), Vector(d_small / 2.0, 0, 0)),
    ]))
    return head.fuse(slot).removeSplitter()


def lip_2d(size, r=2.0, inset=1.2, w=1.2):
    """Tongue-and-groove ring face, inset from an outline of `size`."""
    outer = rrect_inset(size, r, inset)
    inner = rrect_inset(size, r, inset + w)
    return outer.cut(inner)


# ---------------------------------------------------------------------------
# 3D primitives
# ---------------------------------------------------------------------------

def rbox(size, r=2.0):
    """Rounded box, lower-left-front corner at origin."""
    return rrect((size[0], size[1]), r).extrude(Vector(0, 0, size[2]))


def rbox_c(size, r=2.0, cb=0.8, ct=0.8):
    """Rounded box with real chamfers: cb on the plate side (elephant-foot
    relief), ct on top. A genuine OCCT chamfer -- an upgrade over the .scad
    hull-of-three-slabs approximation, not just a literal translation."""
    if size[2] <= cb + ct:
        raise ValueError("rbox_c: chamfers exceed height")
    solid = rbox(size, r)
    bottom_edges = [e for e in solid.Edges if _edges_at_z(e, 0.0)]
    top_edges = [e for e in solid.Edges if _edges_at_z(e, size[2])]
    if cb > 0 and bottom_edges:
        solid = solid.makeChamfer(cb, bottom_edges)
    if ct > 0:
        top_edges = [e for e in solid.Edges if _edges_at_z(e, size[2])]
        solid = solid.makeChamfer(ct, top_edges)
    return solid


def _edges_at_z(edge, z, tol=1e-4):
    return all(abs(v.Point.z - z) < tol for v in edge.Vertexes)


def fillet_edges_at_z(shape, z, r, tol=1e-4):
    """Select the edges whose vertices all lie in the z = `z` plane and fillet
    them by radius r -- the recurring 'floor junction' case. The direct
    replacement for the .scad fillet_ring()/fillet_lin() workarounds, which
    have no port because FreeCAD has real B-rep fillets."""
    edges = [e for e in shape.Edges if _edges_at_z(e, z, tol)]
    if not edges:
        return shape
    return shape.makeFillet(r, edges)


def boss(h, od, bore=0.0, bore_depth=0.0,
         gussets=3, gusset_h=0.0, gusset_l=0.0, gusset_t=2.52,
         angle0=0.0, spread=0.0, fillet_r=1.0, mouth=0.0):
    """Gusseted, filleted screw column -- the load-bearing primitive. Sits on
    z = 0, axis +Z, same parameter names and convention as boss() in
    enclosure_lib.scad.

    h           column height (floor to mating face)
    od          column outer diameter
    bore        blind hole diameter (insert bore or pilot); 0 = none
    bore_depth  from the top face; >= h makes it a through hole
    gussets     rib count; rib i points at angle0 + i*spread
    gusset_h/l  rib height at the column / reach from the column wall
                (default 0.7h / = gusset_h, i.e. 45 deg)
    gusset_t    rib thickness (use the wall thickness)
    fillet_r    real B-rep fillet radius at the floor junction
    mouth       lead-in chamfer at the bore mouth; 0 on a heat-set insert
    """
    gh = gusset_h if gusset_h > 0 else 0.7 * h
    gl = gusset_l if gusset_l > 0 else gh
    sp = spread if spread > 0 else (360.0 / gussets if gussets > 0 else 0.0)

    if od <= bore + 2:
        raise ValueError("boss: bore too close to the outer wall")
    if gh > h:
        raise ValueError("boss: ribs taller than the column")
    if gh < gl:
        raise ValueError("boss: ribs reach further than they rise; raise gusset_h or shorten gusset_l")

    r = od / 2.0
    column = Part.makeCylinder(r, h)
    if fillet_r > 0:
        # Fillet the plain column's floor edge FIRST, before any rib is fused
        # on -- a single clean circular edge. Filleting the final fused
        # compound (a star-shaped floor profile of arcs, rib edges and tiny
        # cone-tip arcs) was tried and fails in OCCT (BRep_API: command not
        # done) on exactly this geometry; verified live via the FreeCAD MCP
        # connection. Filleting column and each rib separately, before fusing,
        # is the approach that actually survived that test.
        floor_edges = [e for e in column.Edges if _edges_at_z(e, 0.0)]
        column = column.makeFillet(fillet_r, floor_edges)
    solid = column

    if gussets > 0 and gl > 0:
        # Clipping cone: radius r+gl at z=0 tapering to r at z=gh, so every rib
        # layer sits inside the one below -- the same taper mechanism as the
        # .scad intersection(extruded_rib, cone) trick.
        clip_cone = Part.makeCone(r + gl, r, gh)
        half_t = gusset_t / 2.0
        base_pts = [Vector(0, -half_t, 0), Vector(r + gl, -half_t, 0),
                    Vector(r + gl, half_t, 0), Vector(0, half_t, 0),
                    Vector(0, -half_t, 0)]
        for i in range(gussets):
            ang_deg = angle0 + i * sp
            rib_face = Part.Face(Part.Wire(Part.makePolygon(base_pts)))
            rib_blank = rib_face.extrude(Vector(0, 0, gh))
            rib = rib_blank.common(clip_cone)
            if fillet_r > 0:
                rib_floor_edges = [e for e in rib.Edges if _edges_at_z(e, 0.0)]
                try:
                    rib = rib.makeFillet(min(fillet_r, gusset_t / 2.0 - 0.05), rib_floor_edges)
                except Part.OCCError:
                    pass  # keep the unfilleted rib rather than failing the whole boss
            rib.rotate(Vector(0, 0, 0), Vector(0, 0, 1), ang_deg)
            solid = solid.fuse(rib)
        solid = solid.removeSplitter()

    if bore > 0:
        bz = -EPS if bore_depth >= h else h - bore_depth
        cutter = Part.makeCylinder(bore / 2.0, h - bz + EPS, Vector(0, 0, bz))
        if mouth > 0:
            cutter = cutter.fuse(
                Part.makeCone(bore / 2.0, bore / 2.0 + mouth, mouth + EPS,
                               Vector(0, 0, h - mouth)))
        solid = solid.cut(cutter)

    return solid


def insert_boss(h, od=9.5, bore=4.1, insert_len=5.7,
                 gussets=3, gusset_h=0.0, gusset_l=0.0, gusset_t=2.52,
                 angle0=0.0, spread=0.0, fillet_r=1.0, mouth=0.0,
                 relief=1.0, min_floor=0.0):
    """Heat-set insert column. bore is final CAD diameter (no automatic
    compensation). Defaults are an uncalibrated house M3 example, not an
    insert outside diameter -- confirm bore shape, relief and mouth with the
    selected insert drawing/coupon."""
    if insert_len <= 0 or relief < 0 or min_floor < 0:
        raise ValueError("insert_boss: invalid insert depth inputs")
    if h - insert_len - relief < min_floor - EPS:
        raise ValueError("insert_boss: insert bore would exceed the available column depth")
    return boss(h=h, od=od, bore=bore, bore_depth=insert_len + relief,
                gussets=gussets, gusset_h=gusset_h, gusset_l=gusset_l,
                gusset_t=gusset_t, angle0=angle0, spread=spread,
                fillet_r=fillet_r, mouth=mouth)


def pcb_standoff(h, od=6.0, bore=2.4, bore_depth=6.0,
                  gussets=0, gusset_t=2.52, fillet_r=1.0):
    """PCB standoff: same family as boss(), light duty."""
    return boss(h=h, od=od, bore=bore, bore_depth=min(bore_depth, h),
                gussets=gussets, gusset_t=gusset_t, fillet_r=fillet_r, mouth=0.5)


# ---------------------------------------------------------------------------
# Closures
# ---------------------------------------------------------------------------

def lip_tongue(size, r=2.0, inset=1.2, w=1.2, h=2.0):
    """Raised tongue on the base's mating face."""
    return lip_2d(size, r, inset, w).extrude(Vector(0, 0, h))


def rim_band(size, r=2.0, wall=1.6, rim_w=2.5, h=1.5):
    """Inward thickening of a thin wall's rim so a tongue-and-groove still
    leaves one extrusion of land each side. Top at z = 0: place at the mating
    face."""
    ch = rim_w - wall
    outer = rrect_inset(size, r, wall - EPS)
    band = outer.extrude(Vector(0, 0, h + ch))
    inner_bottom = rrect_inset(size, r, wall)
    inner_top = rrect_inset(size, r, rim_w)
    inner_top.translate(Vector(0, 0, ch))
    cavity = Part.makeLoft([inner_bottom.OuterWire, inner_top.OuterWire], True)
    band = band.cut(cavity)
    band.translate(Vector(0, 0, -h - ch))
    return band


def lip_groove_cut(size, r=2.0, inset=1.2, w=1.2, h=2.0, tol=0.25):
    """Matching groove cutter for the lid underside (cuts from z=0 upward by
    h). `tol` is added to the groove width once and split across both flanks
    -- pass 2 * slip as tol for a per-side slip clearance, and h = tongue
    height + slip so the tongue does not bottom out."""
    profile = lip_2d(size, r, inset - tol / 2, w + tol)
    return profile.extrude(Vector(0, 0, h))


def snap_hook(length=12.0, thick=1.6, width=6.0, hook_depth=0.8, hook_h=2.0):
    """Cantilever snap hook on z=0, beam in XZ, hook toward +X. Check beam
    strain against the material limit; forbidden on the default PETG-CF
    profile."""
    pts = [
        Vector(0, 0, 0), Vector(thick, 0, 0),
        Vector(thick, length - hook_h, 0),
        Vector(thick + hook_depth, length - hook_h, 0),
        Vector(thick + hook_depth, length - 0.7 * hook_h, 0),
        Vector(thick, length, 0),
        Vector(0, length, 0), Vector(0, 0, 0),
    ]
    profile = Part.Face(Part.Wire(Part.makePolygon(pts)))
    solid = profile.extrude(Vector(0, 0, width))
    solid.translate(Vector(0, 0, -width / 2.0))
    solid.rotate(Vector(0, 0, 0), Vector(1, 0, 0), 90)
    return solid


def label(txt, size=5.0, depth=0.6, font_file=None):
    """Embossed text body on z = [0, depth]. font_file must be a real font
    file PATH on the machine running FreeCAD (not a family name) -- confirm
    the default below exists there; it is platform-dependent."""
    import Draft
    ff = font_file or "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    wires = Draft.make_shapestring(String=txt, FontFile=ff, Size=size, Tracking=0).Shape.Wires
    faces = [Part.Face(w) for w in wires]
    solid = faces[0]
    for f in faces[1:]:
        solid = solid.fuse(f)
    return solid.removeSplitter().extrude(Vector(0, 0, depth))


def label_cut(txt, size=4.0, depth=0.4, font_file=None):
    """Debossed text cutter: occupies z = [-depth, EPS]; place at the surface."""
    solid = label(txt, size, depth + EPS, font_file)
    solid.translate(Vector(0, 0, -depth))
    return solid


def tie_anchor(tie_w=2.5, tie_t=1.1, length=5.0, side=1.68,
               roof=2.0, clear=0.5, flare=1.0):
    """Zip-tie anchor standing on z = 0, centred on the origin. The bundle
    runs along Y over it; the strap threads a tunnel along X."""
    s = tie_anchor_size(tie_w, tie_t, length, side, roof, clear, flare)
    body = (length, s[1] - 2 * flare, s[2])
    base_box = Part.makeBox(s[0], s[1], EPS, Vector(-s[0] / 2, -s[1] / 2, 0))
    flare_top = Part.makeBox(body[0], body[1], EPS, Vector(-body[0] / 2, -body[1] / 2, flare))
    flare_solid = _loft_hull(base_box, flare_top)
    main_body = Part.makeBox(body[0], body[1], body[2], Vector(-body[0] / 2, -body[1] / 2, 0))
    solid = main_body.fuse(flare_solid).removeSplitter()
    tunnel = Part.makeBox(s[0] + 2, tie_w + clear, tie_t + clear + EPS,
                           Vector(-(s[0] + 2) / 2, -(tie_w + clear) / 2, -EPS))
    return solid.cut(tunnel)


def _loft_hull(box_a, box_b):
    """Convex hull-ish solid between two boxes at different Z via a ruled loft
    of their outer wires -- stands in for the .scad hull() of two slabs."""
    wire_a = box_a.Faces[0].OuterWire if box_a.BoundBox.ZMin == box_a.BoundBox.ZMax else box_a.Faces[4].OuterWire
    wire_b = box_b.Faces[0].OuterWire if box_b.BoundBox.ZMin == box_b.BoundBox.ZMax else box_b.Faces[4].OuterWire
    return Part.makeLoft([wire_a, wire_b], True)


def cable_channel(length, gap, h, rib=1.26, flare=1.0):
    """Two ribs along +Y bounding an open channel, centred on x = 0, standing
    on z = 0. gap is measured between the rib faces above the flare."""
    if h <= flare:
        raise ValueError("cable_channel: ribs shorter than their flare")
    ribs = []
    for sx in (-1, 1):
        cx = sx * (gap + rib) / 2.0
        body = Part.makeBox(rib, length, h, Vector(cx - rib / 2.0, 0, 0))
        base_face_wire = Part.Wire(Part.makePolygon([
            Vector(cx - rib / 2.0 - flare, 0, 0), Vector(cx + rib / 2.0 + flare, 0, 0),
            Vector(cx + rib / 2.0 + flare, length, 0), Vector(cx - rib / 2.0 - flare, length, 0),
            Vector(cx - rib / 2.0 - flare, 0, 0),
        ]))
        top_face_wire = Part.Wire(Part.makePolygon([
            Vector(cx - rib / 2.0, 0, flare), Vector(cx + rib / 2.0, 0, flare),
            Vector(cx + rib / 2.0, length, flare), Vector(cx - rib / 2.0, length, flare),
            Vector(cx - rib / 2.0, 0, flare),
        ]))
        flare_solid = Part.makeLoft([base_face_wire, top_face_wire], True)
        ribs.append(body.fuse(flare_solid).removeSplitter())
    return ribs[0].fuse(ribs[1]).removeSplitter()


# ---------------------------------------------------------------------------
# Cutters
# ---------------------------------------------------------------------------

def screw_cut(d=3.4, t=3.0, type="counterbore", head_d=6.0, head_h=3.0):
    """Clearance hole through a plate of thickness t; head recess cut from
    the top. type: 'counterbore' | 'countersink' | 'none'."""
    shaft = Part.makeCylinder(d / 2.0, t + 2 * EPS, Vector(0, 0, -EPS))
    if type == "counterbore":
        head = Part.makeCylinder(head_d / 2.0, head_h + EPS, Vector(0, 0, t - head_h))
        return shaft.fuse(head).removeSplitter()
    if type == "countersink":
        head = Part.makeCone(d / 2.0, head_d / 2.0, head_d / 2.0 + EPS, Vector(0, 0, t - head_d / 2.0))
        return shaft.fuse(head).removeSplitter()
    return shaft


def hex_nut_trap_cut(af=5.8, depth=2.6):
    """Hex nut pocket from z=0 up to depth; af = across flats incl. clearance."""
    hexagon = _regular_polygon_face(poly_d(af, 6) / 2.0, 6)
    return _translate_copy(hexagon.extrude(Vector(0, 0, depth + EPS)), Vector(0, 0, -EPS))


def _translate_copy(shape, vec):
    s = shape.copy()
    s.translate(vec)
    return s


def teardrop_cut(d, h):
    """Horizontal-hole cutter, axis +Z, roof point toward +Y."""
    return _translate_copy(teardrop_2d(d).extrude(Vector(0, 0, h + 2 * EPS)), Vector(0, 0, -EPS))


def keyhole_cut(d_big=7.0, d_small=3.5, length=8.0, t=3.0):
    """Keyhole through a plate of thickness t."""
    return _translate_copy(keyhole_2d(d_big, d_small, length).extrude(Vector(0, 0, t + 2 * EPS)), Vector(0, 0, -EPS))


def foot_recess_cut(d=8.0, depth=1.0):
    """Rubber-foot recess cut upward into a bottom face lying on z = 0."""
    return Part.makeCylinder(d / 2.0, depth + EPS, Vector(0, 0, -EPS))


def cable_exit_cut(d, t, ch=0.6, td=False):
    """Cable exit through a plate of thickness t along +Z: diameter d with a
    45 deg anti-chafe chamfer of ch on both faces."""
    if t <= 2 * ch:
        raise ValueError("cable_exit_cut: chamfers exceed the wall")
    shaft = _translate_copy(hole_2d(d, td).extrude(Vector(0, 0, t + 2 * EPS)), Vector(0, 0, -EPS))
    bottom_big = hole_2d(d + 2 * ch, td)
    bottom_small = _translate_copy(hole_2d(d, td), Vector(0, 0, ch))
    bottom_chamfer = Part.makeLoft([bottom_big.OuterWire, bottom_small.OuterWire], True)
    top_small = _translate_copy(hole_2d(d, td), Vector(0, 0, t - ch))
    top_big = _translate_copy(hole_2d(d + 2 * ch, td), Vector(0, 0, t))
    top_chamfer = Part.makeLoft([top_small.OuterWire, top_big.OuterWire], True)
    return shaft.fuse(bottom_chamfer).fuse(top_chamfer).removeSplitter()


# ---------------------------------------------------------------------------
# Face frames -- place/cut features into any face of a box of size `outer`
# ---------------------------------------------------------------------------

def face_frame(face, outer):
    """FreeCAD.Matrix mapping face-local (u, v, w) coords to world coords,
    where w = depth INTO the part from its outer surface. The direct analog of
    the .scad face_frame() multmatrix table.

    front/back : u = world X, v = world Z    left/right : u = world Y, v = world Z
    bottom/top : u = world X, v = world Y

    A FreeCAD.Matrix, not a Placement: five of the six faces need a parity
    flip (depth pointing into the solid, combined with u/v matching the
    documented positive world axes, is a reflection -- det = -1 -- for every
    face except bottom). FreeCAD.Placement only accepts proper rotations
    (det = +1) and silently cannot represent this; an earlier Placement-based
    version of this function put "front" cutouts at the wrong Z and was
    caught live via the FreeCAD MCP connection (a vent pattern landed below
    the floor instead of in the wall) before being replaced with this
    Matrix + transformShape() approach.
    """
    x, y, z = outer[0], outer[1], outer[2]
    if face == "front":    # y=0,       depth=+Y, u=+X, v=+Z
        return FreeCAD.Matrix(1, 0, 0, 0,  0, 0, 1, 0,  0, 1, 0, 0,  0, 0, 0, 1)
    if face == "back":     # y=outer_y, depth=-Y, u=+X, v=+Z
        return FreeCAD.Matrix(1, 0, 0, 0,  0, 0, -1, y,  0, 1, 0, 0,  0, 0, 0, 1)
    if face == "left":     # x=0,       depth=+X, u=+Y, v=+Z
        return FreeCAD.Matrix(0, 0, 1, 0,  1, 0, 0, 0,  0, 1, 0, 0,  0, 0, 0, 1)
    if face == "right":    # x=outer_x, depth=-X, u=+Y, v=+Z
        return FreeCAD.Matrix(0, 0, -1, x,  1, 0, 0, 0,  0, 1, 0, 0,  0, 0, 0, 1)
    if face == "bottom":   # z=0,       depth=+Z, u=+X, v=+Y
        return FreeCAD.Matrix(1, 0, 0, 0,  0, 1, 0, 0,  0, 0, 1, 0,  0, 0, 0, 1)
    if face == "top":      # z=outer_z, depth=-Z, u=+X, v=+Y
        return FreeCAD.Matrix(1, 0, 0, 0,  0, 1, 0, 0,  0, 0, -1, z,  0, 0, 0, 1)
    raise ValueError(f"face_frame: unknown face '{face}'")


def wall_cut(face, outer, wall, shape2d, extra=1.0):
    """Place a 2D cutter profile (already built, e.g. via hole_2d/rrect) on
    `face` using face_frame, and extrude it straight through a wall of
    thickness `wall`. Returns a cutter Part.Shape ready to .cut() from the
    body. Uses transformShape (not .Placement) because face_frame can return
    a reflection; .Placement cannot."""
    cutter = _translate_copy(shape2d, Vector(0, 0, -extra))
    cutter = cutter.extrude(Vector(0, 0, wall + 2 * extra))
    cutter.transformShape(face_frame(face, outer), True)
    return cutter


def wall_cut_chamfer(face, outer, shape2d, ch=1.0):
    """45 deg lead-in chamfer of depth ch around a convex 2D cutter profile on
    the outer surface, so a plug finds the hole without looking. Use
    alongside wall_cut()."""
    inner = _translate_copy(shape2d, Vector(0, 0, ch))
    outer_profile = shape2d.makeOffset2D(ch) if hasattr(shape2d, "makeOffset2D") else shape2d
    chamfer = Part.makeLoft([outer_profile.OuterWire, inner.OuterWire], True)
    chamfer.transformShape(face_frame(face, outer), True)
    return chamfer
