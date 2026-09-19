// enclosure_lib.scad — reusable geometry for 3D-printed electronics enclosures
// v1.0
//
// Usage:  use <enclosure_lib.scad>
// `use` imports modules but not variables, so the project file stays the single
// source of truth for every dimension. Pass parameters explicitly.
//
// Convention: all modules sit at the origin with +Z up and print-as-oriented,
// unless the comment says otherwise. Cutter modules are named *_cut or documented
// as cutters and already include eps overshoot.

EPS = 0.01;

// ---------------------------------------------------------------------------
// 2D primitives
// ---------------------------------------------------------------------------

// Rounded rectangle, lower-left corner at origin.
module rrect(size, r = 2) {
    assert(r <= min(size[0], size[1]) / 2, "rrect: corner radius too large");
    hull() for (x = [r, size[0] - r], y = [r, size[1] - r])
        translate([x, y]) circle(r = r);
}

// Rounded rectangle inset by d on all sides, concentric with rrect(size, r).
module rrect_inset(size, r = 2, d = 0) {
    translate([d, d]) rrect([size[0] - 2 * d, size[1] - 2 * d], max(r - d, 0.4));
}

// Teardrop profile for horizontal holes. The point faces +Y, so rotate the
// caller's coordinate system until +Y is up in the print orientation.
module teardrop_2d(d) {
    r = d / 2;
    union() {
        circle(r = r);
        rotate(45) square([r, r]);
    }
}

// ---------------------------------------------------------------------------
// 3D primitives
// ---------------------------------------------------------------------------

// Rounded box, lower-left-bottom corner at origin.
module rbox(size, r = 2) {
    linear_extrude(size[2]) rrect([size[0], size[1]], r);
}

// Rounded box with 45 degree chamfers top and bottom. cb is the plate-side
// chamfer (elephant-foot relief), ct the top one. Built as a hull of three
// convex prisms, which is cheap and always manifold.
module rbox_c(size, r = 2, cb = 0.8, ct = 0.8) {
    assert(size[2] > cb + ct, "rbox_c: chamfers exceed height");
    hull() {
        translate([0, 0, 0])
            linear_extrude(EPS) rrect_inset([size[0], size[1]], r, cb);
        translate([0, 0, cb])
            linear_extrude(size[2] - cb - ct) rrect([size[0], size[1]], r);
        translate([0, 0, size[2] - EPS])
            linear_extrude(EPS) rrect_inset([size[0], size[1]], r, ct);
    }
}

// Horizontal hole cutter with a teardrop roof. Axis along +Z, point toward +Y.
module teardrop_cut(d, h) {
    translate([0, 0, -EPS]) linear_extrude(h + 2 * EPS) teardrop_2d(d);
}

// ---------------------------------------------------------------------------
// Fillets — material added at concave junctions
// ---------------------------------------------------------------------------

// Fillet along a straight concave edge: the corner between the z=0 floor and a
// wall standing in the YZ plane at x=0, material extending toward +X and +Z,
// running along +Y for len.
module fillet_lin(r, len) {
    rotate([-90, 0, 0]) linear_extrude(len)
        difference() {
            square([r, r]);
            translate([r, r]) circle(r = r, $fn = 32);
        }
}

// Fillet ring at the base of a cylinder of radius R standing on z=0.
module fillet_ring(r, R) {
    rotate_extrude($fn = 64)
        translate([R, 0])
            difference() {
                square([r, r]);
                translate([r, r]) circle(r = r, $fn = 32);
            }
}

// ---------------------------------------------------------------------------
// Bosses and standoffs
// ---------------------------------------------------------------------------

// Gusseted screw column. This is the load-bearing element of the enclosure and
// the thing that most often fails, so it is deliberately opinionated:
//
//   - ribs are tapered by intersecting with a cone, which guarantees the rib's
//     top face slopes and never overhangs;
//   - the rib-to-column junction is filleted in plan view by a 2D morphological
//     closing (dilate then erode), which is exact and costs nothing;
//   - the column-to-floor junction gets a fillet ring.
//
// h            total column height (floor to mating face)
// od           column outer diameter
// bore         blind hole diameter (insert bore or pilot); 0 for none
// bore_depth   blind hole depth from the top face
// gussets      rib count (3 minimum on brittle filled materials)
// gusset_h     rib height at the column; default 0.7 * h
// gusset_l     rib reach from the column wall; default = gusset_h (45 degrees)
// gusset_t     rib thickness; use the wall thickness
// angle0       rotation of the first rib, to steer ribs away from obstacles
// fillet_r     plan-view and floor fillet radius
// mouth        lead-in chamfer at the bore mouth, so an insert starts straight
module boss(h, od, bore = 0, bore_depth = 0,
            gussets = 3, gusset_h = 0, gusset_l = 0, gusset_t = 2.52,
            angle0 = 0, fillet_r = 1.0, mouth = 1.0) {

    gh = (gusset_h > 0) ? gusset_h : 0.7 * h;
    gl = (gusset_l > 0) ? gusset_l : gh;

    assert(od > bore + 2, "boss: bore too close to the outer wall");
    assert(gh <= h, "boss: ribs taller than the column");
    assert(gh >= gl, "boss: rib slope shallower than 45 degrees — it will need support");

    difference() {
        union() {
            cylinder(d = od, h = h);
            if (fillet_r > 0) fillet_ring(fillet_r, od / 2);

            if (gussets > 0 && gl > 0)
                intersection() {
                    // Filleted rib footprint, with the column area removed.
                    linear_extrude(gh)
                        difference() {
                            offset(r = -fillet_r) offset(r = fillet_r)
                                union() {
                                    circle(d = od);
                                    for (i = [0 : gussets - 1])
                                        rotate(angle0 + i * 360 / gussets)
                                            translate([0, -gusset_t / 2])
                                                square([od / 2 + gl, gusset_t]);
                                }
                            circle(d = od - EPS);
                        }
                    // Cone that tapers the ribs; slope = atan(gh/gl).
                    cylinder(r1 = od / 2 + gl, r2 = od / 2, h = gh);
                }
        }

        if (bore > 0) {
            translate([0, 0, h - bore_depth])
                cylinder(d = bore, h = bore_depth + EPS);
            if (mouth > 0)
                translate([0, 0, h - mouth])
                    cylinder(d1 = bore, d2 = bore + 2 * mouth, h = mouth + EPS);
        }
    }
}

// Heat-set insert column. bore/depth come from the insert datasheet — the
// defaults suit a common M3 4.6 x 5.7 mm insert. depth includes 1 mm relief so
// the insert does not bottom out and split the column.
module insert_boss(h, od = 9.5, bore = 4.1, insert_len = 5.7,
                   gussets = 3, gusset_t = 2.52, angle0 = 0, fillet_r = 1.0) {
    boss(h = h, od = od, bore = bore, bore_depth = insert_len + 1.0,
         gussets = gussets, gusset_t = gusset_t, angle0 = angle0,
         fillet_r = fillet_r, mouth = 1.0);
}

// PCB standoff. Same family, smaller, usually fewer ribs because it carries
// almost no load — it only has to not snap when someone leans on the board.
module pcb_standoff(h, od = 6, bore = 2.4, bore_depth = 6,
                    gussets = 0, gusset_t = 2.52, fillet_r = 1.0) {
    boss(h = h, od = od, bore = bore, bore_depth = bore_depth,
         gussets = gussets, gusset_t = gusset_t, fillet_r = fillet_r, mouth = 0.5);
}

// ---------------------------------------------------------------------------
// Screw holes (cutters)
// ---------------------------------------------------------------------------

// Clearance hole through a plate of thickness t, with a head recess.
// type: "counterbore" for socket/cheese heads, "countersink" for flat heads,
//       "none" for a plain through hole.
// Head recess is cut from the top (+Z) face.
module screw_cut(d = 3.4, t = 3, type = "counterbore",
                 head_d = 6.0, head_h = 3.0) {
    translate([0, 0, -EPS]) cylinder(d = d, h = t + 2 * EPS);

    if (type == "counterbore")
        translate([0, 0, t - head_h])
            cylinder(d = head_d, h = head_h + EPS);

    if (type == "countersink")
        translate([0, 0, t - head_d / 2])
            cylinder(d1 = d, d2 = head_d, h = head_d / 2 + EPS);
}

// ---------------------------------------------------------------------------
// Ventilation (cutters)
// ---------------------------------------------------------------------------

// Array of rounded slots, long in Z, arrayed along X, cutting through Y.
// Drop this into a vertical wall: the slots print unsupported and the webs
// between them carry load, so keep pitch >= slot_w + one wall thickness.
module vent_slots_cut(n = 5, slot_w = 2, slot_l = 20, pitch = 5, t = 5) {
    assert(slot_l <= 25, "vent_slots_cut: slot longer than 25 mm weakens the wall");
    r = slot_w / 2;
    rotate([90, 0, 0]) translate([0, 0, -t / 2 - EPS])
        linear_extrude(t + 2 * EPS)
            for (i = [0 : n - 1])
                translate([(i - (n - 1) / 2) * pitch, 0])
                    hull() {
                        translate([0,  slot_l / 2 - r]) circle(r = r);
                        translate([0, -slot_l / 2 + r]) circle(r = r);
                    }
}

// Pointy-top hex grid through a plate of thickness t, cutting along +Z,
// centred on the origin. cell is the across-flats opening size.
module hex_vents_cut(cols = 5, rows = 5, cell = 4, web = 1.6, t = 3) {
    px = cell + web;
    py = px * sqrt(3) / 2;
    translate([0, 0, -EPS]) linear_extrude(t + 2 * EPS)
        for (r = [0 : rows - 1], c = [0 : cols - 1])
            translate([(c + (r % 2) / 2) * px - (cols - 1) * px / 2,
                       r * py - (rows - 1) * py / 2])
                rotate(30) circle(d = cell / cos(30), $fn = 6);
}

// ---------------------------------------------------------------------------
// Closures and mounting
// ---------------------------------------------------------------------------

// Tongue-and-groove lip profile: a closed ring inset from the outer outline.
module lip_2d(size, r = 2, inset = 1.2, w = 1.2) {
    difference() {
        rrect_inset(size, r, inset);
        rrect_inset(size, r, inset + w);
    }
}

// Raised tongue on the base's mating face.
module lip_tongue(size, r = 2, inset = 1.2, w = 1.2, h = 2) {
    linear_extrude(h) lip_2d(size, r, inset, w);
}

// Matching groove cutter for the lid. Grows the ring by tol on both sides so
// the halves close without a press fit.
module lip_groove_cut(size, r = 2, inset = 1.2, w = 1.2, h = 2, tol = 0.25) {
    translate([0, 0, -EPS])
        linear_extrude(h + EPS)
            lip_2d(size, r, inset - tol / 2, w + tol);
}

// Keyhole slot for wall mounting, cut through a plate of thickness t.
// The large opening is at the origin and the slot runs toward -Y, so the
// enclosure hangs downward onto the screw head.
module keyhole_cut(d_big = 7, d_small = 3.5, len = 8, t = 3) {
    translate([0, 0, -EPS]) linear_extrude(t + 2 * EPS)
        union() {
            circle(d = d_big);
            translate([0, -len]) circle(d = d_small);
            translate([-d_small / 2, -len]) square([d_small, len]);
        }
}

// Rubber foot recess, cut into the bottom face (cuts toward -Z from z=0).
module foot_recess_cut(d = 8, depth = 1) {
    translate([0, 0, -depth]) cylinder(d = d, h = depth + EPS);
}

// Debossed label. Cut this into an internal face so the part identifies itself
// after it has been on a shelf for six months.
module label_cut(txt, size = 4, depth = 0.4) {
    translate([0, 0, -depth])
        linear_extrude(depth + EPS)
            text(txt, size = size, halign = "center", valign = "center");
}

// ---------------------------------------------------------------------------
// Preview helper
// ---------------------------------------------------------------------------

// Offsets children along +Z for an exploded assembly view. Preview only —
// never export a part rendered through this.
module explode(dz = 30) {
    translate([0, 0, dz]) children();
}
