// Dimension-linkage example for enclosure-maker, not a load-certified enclosure.
// House starting values are UNCALIBRATED. Bore is final CAD size, not insert OD.
let bore = param("Insert CAD bore diameter", 4.1, 2.0, 8.0);
let insert_len = param("Insert length", 5.7, 2.0, 12.0);
let relief = param("Insert depth relief", 1.0, 0.0, 3.0);
let height = param("Boss height", 12.0, 6.0, 25.0);
let wall = param("Boss radial wall", 2.52, 2.5, 5.0);
let requested_od = param("Boss minimum diameter", 9.5, 6.0, 20.0);
let gusset_height = param("Gusset height", 7.0, 2.0, 20.0);
let gusset_reach = param("Gusset reach", 4.0, 1.0, 8.0);
let gusset_width = param("Gusset thickness", 2.52, 1.2, 5.0);
let boss_x = param("Boss X", 0.0, -50.0, 50.0);
let boss_y = param("Boss Y", 0.0, -50.0, 50.0);
let diameter = max(9.5, max(requested_od, bore + 2.0 * wall));
let bore_depth = insert_len + relief;
let floor_min = 2.0;
if height - bore_depth < floor_min { throw "Insert bore leaves less than 2 mm of floor"; }
if gusset_height > height { throw "Gusset height exceeds boss height"; }
let radius = diameter / 2.0;
let eps = 0.01;
let segments = 64; // Final functional circles; no global OpenSCAD $fn in Rhai.
let boss = cylinder(radius, height, segments);
let taper = cone(radius + gusset_reach, radius, gusset_height, segments);
for angle in [0.0, 120.0, 240.0] {
    let rib = cuboid(radius + gusset_reach, gusset_width, gusset_height)
        .translate((radius + gusset_reach) / 2.0, 0.0, gusset_height / 2.0)
        .rotate(0.0, 0.0, angle).intersect(taper);
    boss = boss.union(rib);
}
let cutter = cylinder(bore / 2.0, bore_depth + eps, segments)
    .translate(0.0, 0.0, height - bore_depth);
boss = boss.subtract(cutter).translate(boss_x, boss_y, 0.0);
emit("boss", boss);
// Preview geometry never enters the printable parts list.
view("section", boss.intersect(cuboid(200.0, 200.0, 100.0).translate(100.0, 0.0, 50.0)));
