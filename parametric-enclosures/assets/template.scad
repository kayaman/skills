// ============================================================================
// <PRODUCT> enclosure — v0.1
// Profile: Bambu Lab A1 Mini, 0.4 mm hardened nozzle, PETG-CF, 0.2 mm layers
//          (see references/manufacturing-profiles.md — change the Process group
//           when the profile changes)
// Parts:   base (floor on the plate) + lid (printed as modeled: groove side down)
// Frame:   origin = outer bottom-left-front corner of the base, +Z up.
//          Board features are given in BOARD coordinates (origin = board's
//          bottom-left corner, top view) and placed via pcb_origin.
// Layout along X: wall | column zone | clear | PCB | clear | [divider | sensor
//          chamber] or [column zone] | wall.  Connectors go on FRONT/BACK faces,
//          where the board edge is close to the wall.
// Along Y: wall | [bay_front] | clear | PCB | clear | [bay_back] | wall. A bay holds
//          wiring, tie anchors and cable exits; connectors use the face without one.
// Export:
//   openscad -D 'part="base"' -o base.stl <product>_enclosure.scad
//   openscad -D 'part="lid"'  -o lid.stl  <product>_enclosure.scad
// ============================================================================

use <enclosure_lib.scad>

/* [Part] */
part = "assembly";  // [assembly, exploded, base, lid, section, check]

/* [Project] */
product = "PRODUCT";
version = "v0.1";
lid_label = "";     // debossed on the lid top; "" = none

/* [Process] */
ew          = 0.42;   // extrusion width
layer       = 0.2;
wall_lines  = 6;      // [3:1:10] wall = wall_lines * ew
envelope    = 170;    // usable build envelope per axis
tol         = 0.25;   // calibrated slip fit for this printer/filament pair
hole_comp   = 0.15;   // added to the diameter of FUNCTIONAL holes only
max_bridge  = 5;      // mm
teardrop_min = 5;     // horizontal round holes >= this get a teardrop roof
antenna_keepout = 20; // mm, no inserts/metal inside this radius
elastic_ok  = false;  // snap-fits allowed by this material?

/* [PCB] */
pcb_x       = 50;                                     // ASSUMPTION
pcb_y       = 30;                                     // ASSUMPTION
pcb_t       = 1.6;
pcb_clear   = 0.5;    // per side (>= tol; clones vary ±0.2)
comp_top    = 8;      // tallest component, top side  // ASSUMPTION
comp_bot    = 2;      // tallest component, bottom side
standoff_h  = 4;      // clears through-hole solder tails
standoff_od = 6;
standoff_bore = 2.4;  // M3 self-tap pilot (2.1 for M2.5)
mount_holes = [[3.5, 3.5], [46.5, 3.5], [3.5, 26.5], [46.5, 26.5]]; // ASSUMPTION
antenna     = [];     // [x, y] antenna centre in board coords; [] = none
heat_sources = [[25, 15]]; // regulator / MCU positions, board coords // ASSUMPTION
heat_w      = 0.5;    // W dissipated inside, from the power budget   // ASSUMPTION

/* [Cutouts] */
// [face, pos, z_above_board_top, body_w, body_h, corner_r, user_facing, overmold]
//   face: "front" | "back" (pos = board X of the connector centre)
//   overmold: [w, h] of the mating plug's body, or [] — adds an outer recess
//             so the plug can reach a socket that sits behind a thick wall
cutouts = [
    ["front", 25, 1.6, 9.0, 3.2, 1.6, true, [12.5, 7.0]]  // USB-C // ASSUMPTION
];
cutout_clear    = 0.5;  // per side around connector bodies
user_port_extra = 0.25; // extra per side on user-facing ports
lead_in         = 1.0;  // 45° lead-in chamfer depth on user-facing ports

/* [Wiring] */
// Floor between the board and a long wall for wires, connectors and tie anchors.
// Keep it 0 on a face with connector cutouts: a socket behind a bay is out of reach.
bay_front   = 0;      // mm between the board's front edge and the front wall
bay_back    = 0;      // mm between the board's back edge and the back wall
// [face, pos, z, cable_d]
//   face: "front" | "back", a side with a bay; pos = board X of the exit centre;
//   z = centre height above the floor. Each exit gets a hole of cable_d +
//   exit_clear with anti-chafe chamfers, and a zip-tie anchor in the bay.
cable_exits = [];     // e.g. [["back", 25, 6, 4.5]]
exit_clear  = 0.4;    // added to the cable diameter
exit_ch     = 0.6;    // anti-chafe chamfer on both faces
tie_w       = 2.5;    // strap width: 2.5 small, 3.6 standard
tie_t       = 1.1;    // strap thickness
tie_len     = 5;      // anchor length along its tunnel
tie_offset  = 6;      // inner wall to anchor centre

/* [Fasteners] */
insert_bore = 4.1;    // M3 heat-set insert — check the datasheet
insert_len  = 5.7;
boss_od     = 9.5;
gussets     = 3;
screw_clear = 3.4;    // M3 (hole_comp added)
head_d      = 6.0;
head_h      = 3.0;

/* [Shell] */
floor_t     = 3.0;
ceil_t      = 3.0;
corner_r    = 3.0;
cb          = 0.8;    // bottom chamfer (elephant-foot relief)
ct          = 0.8;    // top chamfer
inner_fillet = 1.0;   // wall/floor and column fillets

/* [Lip] */
lip_w       = 1.0;    // tongue width; leaves one extrusion plus slip each side of a 6-line wall
lip_h       = 2.0;

/* [Ventilation] */
vents        = "auto"; // [auto, on, off]  auto = on above 0.3 W
vent_in_face = "left"; // [left, right, back, front]
vent_out_face = "right"; // [left, right, back, front]
vent_slot_w  = 2.0;

/* [Sensor chamber] */
sensor_chamber = false; // divided, vented chamber at the +X end
chamber_len  = 20;      // interior length along X
chamber_gap  = 3;       // air gap between the divider's two skins
wire_pass    = [6, 4];  // notch (w, depth) at the divider top for wires

/* [Mounting] */
feet        = true;   // rubber-foot recesses
foot_d      = 8;
foot_depth  = 1;
wall_mount  = false;  // keyholes through the floor
keyhole     = [7, 3.5, 8]; // head Ø, shank Ø, travel

/* [Safety] */
child_pet_safe = false; // toddlers/pets can reach it: ≤ 4 mm openings

/* [Hidden] */
EPS = 0.01;
$fa = $preview ? 6 : 1;
$fs = $preview ? 0.6 : 0.25;

// --- derived -------------------------------------------------------------

wall      = wall_lines * ew;
lip_inset = (wall - lip_w) / 2;
boss_zone = boss_od + tol;
divider_t = 2 * wall + chamber_gap;
right_zone = sensor_chamber ? divider_t + chamber_len : boss_zone;

cav_x   = boss_zone + 2 * pcb_clear + pcb_x + right_zone;
cav_y   = pcb_y + 2 * pcb_clear + bay_front + bay_back;
cav_z   = standoff_h + pcb_t + comp_top + 2;   // 2 mm headroom
outer_x = cav_x + 2 * wall;
outer_y = cav_y + 2 * wall;
base_h  = floor_t + cav_z;                     // mating face
lid_h   = ceil_t + lip_h + tol;
outer   = [outer_x, outer_y, base_h];

pcb_origin = [wall + boss_zone + pcb_clear, wall + pcb_clear + bay_front, floor_t + standoff_h];
pcb_top    = pcb_origin[2] + pcb_t;
divider_x0 = pcb_origin[0] + pcb_x + pcb_clear;
chamber_x0 = divider_x0 + divider_t;

function to_world(p) = [pcb_origin[0] + p[0], pcb_origin[1] + p[1]];

boss_inset = wall + boss_od / 2 - 0.5;         // fuses the column into the corner
// [x, y, first-rib angle]: ribs run along the X-end walls, inside the column zone
screw_pts = [
    [boss_inset,           boss_inset,           90],
    [boss_inset,           outer_y - boss_inset, 90],
    [outer_x - boss_inset, boss_inset,           270],
    [outer_x - boss_inset, outer_y - boss_inset, 270]
];

vents_on  = vents == "on" || (vents == "auto" && heat_w > 0.3);
vent_pitch = vent_slot_w + wall;
vent_m    = boss_inset + boss_od / 2 + 1.5;    // keep vents clear of the columns
vout_face = (sensor_chamber && vent_out_face == "right") ? "back" : vent_out_face;
band_h    = 0.25 * cav_z;                      // chimney bands: lowest/highest 25 %

sensor_pos = [chamber_x0 + chamber_len / 2, outer_y / 2];

tie_side    = 4 * ew;
tie_roof    = 10 * layer;
tie_clear   = 0.5;
anchor_size = tie_anchor_size(tie_w, tie_t, tie_len, tie_side, tie_roof, tie_clear, inner_fillet);
col_clear   = boss_inset + boss_od / 2 + 1;   // exits keep this far from each X end

function bay(f) = f == "front" ? bay_front : f == "back" ? bay_back : 0;
function exit_x(e) = pcb_origin[0] + e[1];
function exit_r(e) = (e[3] + exit_clear) / 2 + exit_ch;
function exit_ext(e) = max(exit_r(e), anchor_size[0] / 2);
function anchor_xy(e) = [exit_x(e), e[0] == "front" ? wall + tie_offset
                                                    : outer_y - wall - tie_offset];
function exit_wall_xy(e) = [exit_x(e), e[0] == "front" ? wall : outer_y - wall];

// --- validate ------------------------------------------------------------

assert(wall >= 3 * ew, str("wall ", wall, " is under 3 perimeters"));
assert(lip_inset - tol >= ew, "outer land beside the groove is under one extrusion");
assert(wall - lip_inset - lip_w - tol >= ew, "inner land beside the groove is under one extrusion");
assert(boss_od >= insert_bore + 2 * 2.5, "column OD too small around the insert");
assert(standoff_h >= 4, "standoff too short to clear solder tails");
assert(comp_bot < standoff_h, "bottom-side components hit the floor");
assert(pcb_clear >= tol, "board clearance below the fit tolerance");
assert(cav_y >= boss_od + 2, "cavity too narrow in Y for corner columns");
assert(!sensor_chamber || chamber_len >= boss_zone + 5,
       "sensor chamber too short to hold the corner columns and a sensor");
assert(max(outer_x, outer_y, base_h) <= envelope,
       "base exceeds the build envelope — split it (bolts + dowels, no glue)");
assert(max(outer_x, outer_y, lid_h) <= envelope, "lid exceeds the build envelope");
assert(!child_pet_safe || vent_slot_w <= 4, "child/pet safe: vent slots must be ≤ 4 mm");
for (c = cutouts) {
    assert(c[0] == "front" || c[0] == "back",
           str("cutout on '", c[0], "': X-end walls sit a column zone away from the ",
               "board, so plugs can't reach. Use front/back or rotate the board."));
    ch = max(c[4], len(c[7]) == 2 ? c[7][1] : 0) / 2 + cutout_clear;
    assert(pcb_top + c[2] + ch < base_h - lead_in, str("cutout crosses the lid split: ", c));
    assert(pcb_top + c[2] - ch > floor_t, str("cutout cuts into the floor: ", c));
    assert(bay(c[0]) == 0,
           str("cutout on the ", c[0], " face behind a ", bay(c[0]), " mm wiring bay: ",
               "no plug reaches the socket. Put the bay on the other long side."));
}
for (e = cable_exits) {
    assert(e[0] == "front" || e[0] == "back",
           str("cable exit on '", e[0], "': exits go on the front/back face that has the bay"));
    assert(bay(e[0]) + pcb_clear >= tie_offset + anchor_size[1] / 2 + 1,
           str("bay_", e[0], " too narrow for the tie anchor: needs ",
               tie_offset + anchor_size[1] / 2 + 1 - pcb_clear, " mm"));
    assert(tie_offset >= anchor_size[1] / 2 + 1, "tie anchor touches the wall: raise tie_offset");
    assert(exit_x(e) - exit_ext(e) >= col_clear && exit_x(e) + exit_ext(e) <= outer_x - col_clear,
           str("cable exit or its anchor runs into a corner column: ", e));
    assert(e[2] - exit_r(e) >= inner_fillet, str("cable exit cuts into the floor: ", e));
    assert(floor_t + e[2] + exit_r(e) <= base_h - 1, str("cable exit crosses the lid split: ", e));
    if (sensor_chamber)
        assert(exit_x(e) + exit_ext(e) < divider_x0 - 1 || exit_x(e) - exit_ext(e) > chamber_x0 + 1,
               str("cable exit or its anchor hits the sensor chamber divider: ", e));
    if (len(antenna) == 2)
        for (p = [anchor_xy(e), exit_wall_xy(e)])
            assert(norm(p - to_world(antenna)) >= antenna_keepout,
                   str("cable run inside the antenna keepout: ", e));
    if (vents_on && e[0] == vent_in_face)
        assert(e[2] - exit_r(e) > 1 + band_h, str("cable exit cuts the inlet vent band: ", e));
    if (vents_on && e[0] == vout_face)
        assert(floor_t + e[2] + exit_r(e) < base_h - band_h - 1.5,
               str("cable exit cuts the outlet vent band: ", e));
    if (wall_mount)
        for (kx = [outer_x * 0.3, outer_x * 0.7])
            assert(norm(anchor_xy(e) - [kx, outer_y * 0.6])
                       >= norm([anchor_size[0], anchor_size[1]]) / 2 + keyhole[0] / 2 + keyhole[2] + 1,
                   "tie anchor sits over a keyhole: move the exit or the keyholes");
}
for (p = screw_pts) if (len(antenna) == 2)
    assert(norm([p[0], p[1]] - to_world(antenna)) >= antenna_keepout,
           "insert column inside the antenna keepout — move the antenna end or the board");
if (sensor_chamber) for (h = heat_sources)
    assert(norm(sensor_pos - to_world(h)) >= 15,
           "sensor chamber within 15 mm of a heat source — lengthen the chamber");
if (wall_mount) {
    assert(standoff_h - comp_bot >= 3, "keyhole screw heads need 3 mm under the board");
    for (x = [outer_x * 0.3, outer_x * 0.7], m = mount_holes)
        assert(norm([x, outer_y * 0.6] - to_world(m)) >= standoff_od / 2 + keyhole[0] / 2 + keyhole[2] + 1,
               "keyhole collides with a PCB standoff — move the keyholes");
}

// --- report --------------------------------------------------------------

echo(str("outer: ", outer_x, " x ", outer_y, " x ", base_h + lid_h, " mm"));
echo(str("cavity: ", cav_x, " x ", cav_y, " x ", cav_z, " mm"));
echo(str("wall: ", wall, " mm (", wall_lines, " lines)"));
echo(str("lid screws: 4 x M3 x ", ceil(lid_h - head_h + insert_len), " mm socket head"));
echo(str("largest dimension vs envelope: ", max(outer_x, outer_y, base_h), " / ", envelope));
if (max(outer_x, outer_y) > 100)
    echo("WARNING: span > 100 mm — add a column per ~70 mm (plan it against the board keepout)");
if (base_h > 2.5 * min(outer_x, outer_y))
    echo("WARNING: tall part on a bed-slinger — use a brim or reorient");
if (heat_w > 1)
    echo("WARNING: > 1 W — maximise open vent area or add a fan (environment-and-safety.md)");
for (c = cutouts) if (c[3] + 2 * cutout_clear > max_bridge)
    echo(str("NOTE: cutout ", c[3], " mm wide bridges more than ", max_bridge,
             " mm — expect slight sag on the top edge"));
for (e = cable_exits)
    echo(str("cable exit ", e, ": one ", tie_w, " mm zip tie; a straight run over its anchor ",
             "wants z = ", anchor_size[2] + e[3] / 2));

// --- helpers -------------------------------------------------------------

// 2D profile of a cutout grown by g per side (face coordinates, centred).
module cut_profile(c, g) {
    w = c[3] + 2 * g;
    h = c[4] + 2 * g;
    if (c[3] == c[4] && c[5] >= c[3] / 2) {
        if (w >= teardrop_min) teardrop_2d(w); else circle(d = w);
    } else rrect_c([w, h], c[5] + g);
}

function cut_centre(c) = [pcb_origin[0] + c[1], pcb_top + c[2]];

// Slot band on a face between u0..u1 at height v0 with height h.
module vent_band(face, u0, u1, v0, h) {
    if (u1 - u0 > vent_slot_w && h >= vent_slot_w)
        wall_cut(face, outer, wall)
            translate([u0, v0]) slot_pattern_2d([u1 - u0, h], vent_slot_w, vent_pitch);
}

function face_span(f) =
    (f == "left" || f == "right") ? [vent_m, outer_y - vent_m]
  : [vent_m, sensor_chamber ? divider_x0 - 1.5 : outer_x - vent_m];

// --- parts ---------------------------------------------------------------

module shell() {
    difference() {
        rbox_c([outer_x, outer_y, base_h], corner_r, cb, 0);
        translate([wall, wall, floor_t])
            rbox_c([cav_x, cav_y, cav_z + 1], max(corner_r - wall, 0.5), inner_fillet, 0);
    }
}

module base() {
    union() {
        difference() {
            shell();

            // connector cutouts, lead-ins and plug recesses
            for (c = cutouts) {
                g = cutout_clear + (c[6] ? user_port_extra : 0);
                wall_cut(c[0], outer, wall)
                    translate(cut_centre(c)) cut_profile(c, g);
                if (len(c[7]) == 2 && wall > 1.0 + EPS)
                    face_frame(c[0], outer)
                        translate([0, 0, -1]) linear_extrude(wall - 1.0 + 1)
                            translate(cut_centre(c)) rrect_c(c[7] + [2 * tol, 2 * tol], 1);
                else if (c[6] && lead_in > 0)
                    wall_cut_chamfer(c[0], outer, lead_in)
                        translate(cut_centre(c)) cut_profile(c, g);
            }

            // cable exits, chamfered on both faces so the jacket can't chafe
            for (e = cable_exits)
                face_frame(e[0], outer) translate([exit_x(e), floor_t + e[2], 0])
                    cable_exit_cut(e[3] + exit_clear, wall, exit_ch,
                                   e[3] + exit_clear >= teardrop_min);

            // chimney: inlet low on one face, outlet high on another
            if (vents_on) {
                si = face_span(vent_in_face);
                vent_band(vent_in_face, si[0], si[1], floor_t + 1, band_h);
                so = face_span(vout_face);
                vent_band(vout_face, so[0], so[1], base_h - band_h - 1.5, band_h);
            }

            // sensor chamber: its own bottom-in / top-out vents on the +X face
            if (sensor_chamber) {
                vent_band("right", vent_m, outer_y - vent_m, floor_t + 1, band_h);
                vent_band("right", vent_m, outer_y - vent_m, base_h - band_h - 1.5, band_h);
            }

            // feet, keyholes, internal ID label
            if (feet)
                for (x = [12, outer_x - 12], y = [12, outer_y - 12])
                    translate([x, y, 0]) foot_recess_cut(foot_d, foot_depth);
            if (wall_mount)
                for (x = [outer_x * 0.3, outer_x * 0.7])
                    translate([x, outer_y * 0.6, 0])
                        keyhole_cut(keyhole[0], keyhole[1], keyhole[2], floor_t);
            translate([pcb_origin[0] + pcb_x / 2, pcb_origin[1] + pcb_y / 2, floor_t])
                label_cut(str(product, " BASE ", version), 4, 0.4);
        }

        // lid columns, clipped to the outer envelope so wall-bound ribs merge in
        intersection() {
            rbox_c([outer_x, outer_y, base_h], corner_r, cb, 0);
            for (p = screw_pts)
                translate([p[0], p[1], floor_t - EPS])
                    insert_boss(h = base_h - floor_t + EPS, od = boss_od,
                                bore = insert_bore, insert_len = insert_len,
                                gussets = gussets, gusset_t = wall,
                                angle0 = p[2], spread = 90, fillet_r = inner_fillet);
        }

        // a zip-tie anchor in the bay behind each cable exit, so a pull stops there
        for (e = cable_exits)
            translate(concat(anchor_xy(e), [floor_t - EPS]))
                tie_anchor(tie_w, tie_t, tie_len, tie_side, tie_roof, tie_clear, inner_fillet);

        // PCB standoffs
        for (m = mount_holes)
            translate(concat(to_world(m), [floor_t - EPS]))
                pcb_standoff(h = standoff_h + EPS, od = standoff_od,
                             bore = standoff_bore, bore_depth = standoff_h,
                             fillet_r = inner_fillet);

        // sensor chamber divider: two skins with an air gap (thermal break)
        if (sensor_chamber)
            difference() {
                for (x = [divider_x0, divider_x0 + wall + chamber_gap])
                    translate([x, wall - EPS, floor_t - EPS])
                        cube([wall, cav_y + 2 * EPS, cav_z + EPS]);
                translate([divider_x0 - 1, outer_y / 2 - wire_pass[0] / 2, base_h - wire_pass[1]])
                    cube([divider_t + 2, wire_pass[0], wire_pass[1] + 1]);
            }

        // tongue on the mating face
        translate([0, 0, base_h - EPS])
            lip_tongue([outer_x, outer_y], corner_r, lip_inset, lip_w, lip_h + EPS);
    }
}

// Lid in print orientation: groove side on the plate, origin at its underside.
module lid() {
    difference() {
        rbox_c([outer_x, outer_y, lid_h], corner_r, 0, ct);
        lip_groove_cut([outer_x, outer_y], corner_r, lip_inset, lip_w, lip_h + tol, 2 * tol);
        for (p = screw_pts)
            translate([p[0], p[1], 0])
                screw_cut(d = screw_clear + hole_comp, t = lid_h,
                          type = "counterbore", head_d = head_d, head_h = head_h);
        if (lid_label != "")
            translate([outer_x / 2, outer_y / 2, lid_h]) label_cut(lid_label, 6, 0.6);
    }
}

module lid_world() { translate([0, 0, base_h]) lid(); }

// Board phantom: preview only (% is never rendered or exported).
module pcb_ghost() {
    %translate(pcb_origin) color("green", 0.5) cube([pcb_x, pcb_y, pcb_t]);
}

// --- selector ------------------------------------------------------------

if (part == "base") base();
else if (part == "lid") lid();
else if (part == "exploded") {
    color("DimGray") base();
    color("Silver") explode(base_h + 25) lid();
    pcb_ghost();
}
else if (part == "section") {           // front half removed: inspect fits
    difference() {
        union() { base(); lid_world(); }
        translate([-1, -1, -1]) cube([outer_x + 2, outer_y / 2 + 1, base_h + lid_h + 2]);
    }
    pcb_ghost();
}
else if (part == "check")               // must render EMPTY; any solid = interference
    intersection() { base(); translate([0, 0, 2 * EPS]) lid_world(); }
else {                                  // assembly
    color("DimGray") base();
    color("Silver", 0.85) lid_world();
    pcb_ghost();
}
