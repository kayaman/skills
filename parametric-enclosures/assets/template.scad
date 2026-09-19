// <PRODUCT> enclosure — v0.1
// Profile: Bambu Lab A1 Mini, 0.4 mm hardened nozzle, PETG-CF, 0.2 mm layers
//
// Export:
//   openscad -D 'part="base"' -o base.stl <product>_enclosure.scad
//   openscad -D 'part="lid"'  -o lid.stl  <product>_enclosure.scad

use <enclosure_lib.scad>

/* [Part] */
part = "all";  // [all, base, lid]

/* [Process] */
ew          = 0.42;   // extrusion width
layer       = 0.2;
envelope    = 170;    // usable build envelope per axis
tol         = 0.25;   // calibrated slip fit for this printer/filament pair
hole_comp   = 0.15;   // added to the diameter of functional holes

/* [PCB] */
pcb_x       = 50;
pcb_y       = 30;
pcb_t       = 1.6;
pcb_clear   = 0.25;   // per side
comp_top    = 8;      // tallest component, top side
comp_bot    = 2;      // tallest component, bottom side
standoff_h  = 4;      // clears through-hole solder tails
mount_holes = [[3.5, 3.5], [46.5, 3.5], [3.5, 26.5], [46.5, 26.5]];

/* [Fasteners] */
insert_bore = 4.1;
insert_len  = 5.7;
boss_od     = 9.5;
screw_clear = 3.4;
head_d      = 6.0;
head_h      = 3.0;

/* [Shell] */
wall        = 6 * ew;     // 2.52 mm — keep as a multiple of ew
floor_t     = 3.0;
ceil_t      = 3.0;
corner_r    = 3.0;
cb          = 0.8;        // bottom chamfer (elephant-foot relief)
ct          = 0.8;        // top chamfer

/* [Lip] */
lip_w       = 1.2;
lip_h       = 2.0;
lip_inset   = 1.2;

/* [Hidden] */
eps = 0.01;
$fa = 1;
$fs = $preview ? 0.6 : 0.25;

// --- derived -------------------------------------------------------------

cav_x   = pcb_x + 2 * pcb_clear;
cav_y   = pcb_y + 2 * pcb_clear;
cav_z   = standoff_h + pcb_t + comp_top + 2;   // 2 mm headroom above tallest part
outer_x = cav_x + 2 * wall;
outer_y = cav_y + 2 * wall;
base_h  = floor_t + cav_z;
lid_h   = ceil_t + lip_h;
boss_h  = cav_z;                               // floor to mating face

// --- validate ------------------------------------------------------------

assert(wall >= 3 * ew, str("wall ", wall, " is under 3 perimeters"));
assert(boss_od >= insert_bore + 2 * 2.5, "boss OD too small around the insert");
assert(standoff_h >= 4, "standoff too short to clear solder tails");
assert(comp_bot < standoff_h, "bottom-side components hit the floor");
assert(max(outer_x, outer_y, base_h) <= envelope, "base exceeds the build envelope");
assert(max(outer_x, outer_y, lid_h) <= envelope, "lid exceeds the build envelope");

echo(str("outer: ", outer_x, " x ", outer_y, " x ", base_h + lid_h - lip_h, " mm"));
echo(str("cavity: ", cav_x, " x ", cav_y, " x ", cav_z, " mm"));
echo(str("screw length: ", ceil_t + insert_len, " mm (M3)"));
echo(str("largest dimension vs envelope: ",
         max(outer_x, outer_y, base_h), " / ", envelope));

// --- parts ---------------------------------------------------------------

module base() {
    difference() {
        union() {
            difference() {
                rbox_c([outer_x, outer_y, base_h], corner_r, cb, 0);
                translate([wall, wall, floor_t])
                    rbox([cav_x, cav_y, cav_z + eps], max(corner_r - wall, 0.5));
            }

            // screw columns, one per PCB mounting hole
            for (p = mount_holes)
                translate([wall + pcb_clear + p[0], wall + pcb_clear + p[1], floor_t])
                    insert_boss(h = boss_h, od = boss_od, bore = insert_bore,
                                insert_len = insert_len, gussets = 3,
                                gusset_t = wall, fillet_r = 1.0);

            // tongue on the mating face
            translate([0, 0, base_h])
                lip_tongue([outer_x, outer_y], corner_r, lip_inset, lip_w, lip_h);
        }

        // rubber feet
        for (x = [12, outer_x - 12], y = [12, outer_y - 12])
            translate([x, y, 0]) foot_recess_cut(8, 1);

        translate([outer_x / 2, outer_y / 2, floor_t + 0.4])
            rotate([180, 0, 0]) label_cut("<PRODUCT> BASE v0.1", 4, 0.4);
    }
}

module lid() {
    difference() {
        rbox_c([outer_x, outer_y, lid_h], corner_r, 0, ct);

        // groove receiving the base tongue
        lip_groove_cut([outer_x, outer_y], corner_r, lip_inset, lip_w, lip_h, tol);

        // clearance holes above the columns
        for (p = mount_holes)
            translate([wall + pcb_clear + p[0], wall + pcb_clear + p[1], 0])
                screw_cut(d = screw_clear + hole_comp, t = lid_h,
                          type = "counterbore", head_d = head_d, head_h = head_h);
    }
}

// --- selector ------------------------------------------------------------

if (part == "base") base();
else if (part == "lid") lid();
else {
    base();
    explode(base_h + 25) lid();
}
