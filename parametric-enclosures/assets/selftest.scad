// selftest.scad — renders every module in enclosure_lib.scad
//
// Run this after any library change, BEFORE touching product files:
//   openscad -o selftest.stl selftest.scad
//
// Expected: exits 0, prints no WARNING lines, produces a manifold STL.
// A "may not be a valid 2-manifold" warning means the slicer would be guessing.

use <enclosure_lib.scad>

$fa = 1;
$fs = 0.4;
P = 40;  // grid pitch

module cell(ix, iy) { translate([ix * P, iy * P, 0]) children(); }

// Row 0 — primitives
cell(0, 0) linear_extrude(2) rrect([25, 18], 3);
cell(1, 0) linear_extrude(2) rrect_inset([25, 18], 3, 2);
cell(2, 0) linear_extrude(2) teardrop_2d(8);
cell(3, 0) rbox([25, 18, 10], 3);
cell(4, 0) rbox_c([25, 18, 10], 3, 0.8, 0.8);

// Row 1 — fillets
cell(0, 1) union() {
    cube([2, 20, 12]);
    translate([2, 0, 0]) fillet_lin(1.5, 20);
}
cell(1, 1) union() {
    cylinder(d = 10, h = 12);
    fillet_ring(1.5, 5);
}

// Row 2 — bosses
cell(0, 2) insert_boss(h = 14, od = 9.5, bore = 4.1, insert_len = 5.7,
                       gussets = 3, gusset_t = 2.52);
cell(1, 2) insert_boss(h = 14, od = 9.5, gussets = 4, gusset_t = 2.52, angle0 = 45);
cell(2, 2) boss(h = 16, od = 9.5, bore = 4.1, bore_depth = 6.7,
                gussets = 2, gusset_h = 10, gusset_l = 8, gusset_t = 2.52);
cell(3, 2) pcb_standoff(h = 6, od = 6, bore = 2.4, bore_depth = 6);
cell(4, 2) pcb_standoff(h = 8, od = 7, bore = 2.4, bore_depth = 6,
                        gussets = 3, gusset_t = 2.0);

// Row 3 — screw cutters through a plate
cell(0, 3) difference() {
    translate([-10, -10, 0]) cube([20, 20, 4]);
    screw_cut(3.4, 4, "counterbore", 6.0, 3.0);
}
cell(1, 3) difference() {
    translate([-10, -10, 0]) cube([20, 20, 4]);
    screw_cut(3.4, 4, "countersink", 6.0);
}
cell(2, 3) difference() {
    translate([-10, -10, 0]) cube([20, 20, 4]);
    screw_cut(3.4, 4, "none");
}

// Row 4 — ventilation
cell(0, 4) difference() {
    translate([-15, -2.5, 0]) cube([30, 5, 28]);
    translate([0, 0, 14]) vent_slots_cut(n = 5, slot_w = 2, slot_l = 20,
                                         pitch = 5, t = 5);
}
cell(1, 4) difference() {
    translate([-15, -15, 0]) cube([30, 30, 3]);
    hex_vents_cut(cols = 5, rows = 5, cell = 4, web = 1.6, t = 3);
}

// Row 5 — closure and mounting
cell(0, 5) lip_tongue([28, 20], 3, 1.2, 1.2, 2);
cell(1, 5) difference() {
    rbox([28, 20, 4], 3);
    lip_groove_cut([28, 20], 3, 1.2, 1.2, 2, 0.25);
}
cell(2, 5) difference() {
    translate([-10, -14, 0]) cube([20, 20, 3]);
    keyhole_cut(7, 3.5, 8, 3);
}
cell(3, 5) difference() {
    translate([-10, -10, 0]) cube([20, 20, 4]);
    translate([0, 0, 4]) rotate([180, 0, 0]) foot_recess_cut(8, 1);
}
cell(4, 5) difference() {
    translate([-14, -6, 0]) cube([28, 12, 3]);
    translate([0, 0, 3]) label_cut("TEST v1", 4, 0.4);
}

echo("selftest: if you see this with no warnings above, the library rendered clean");
