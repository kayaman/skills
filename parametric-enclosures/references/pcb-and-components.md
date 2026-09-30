# PCBs, boards and connector cutouts

## Contents
1. Getting the board geometry
2. Vertical stack-up
3. Holding the board
4. Known board footprints
5. Connector cutouts (and the USB plug trap)
6. Antenna and keepouts

## 1. Getting the board geometry

In order of reliability:
1. The user's own measurements or KiCad/EasyEDA files. From KiCad, export the
   Edge.Cuts layer as DXF/SVG (1:1, mm) and `import()` it for the outline;
   export the 3D board as STL and show it with `%import("board.stl")` for fit.
2. The manufacturer's mechanical drawing (Raspberry Pi, Arduino and Espressif
   publish them).
3. The table in §4 — good starting values; clones differ. Always tag them
   `// ASSUMPTION: verify with calipers`.

What you need: outline X×Y, thickness, hole Ø and centers (from the
bottom-left corner, top view), connector positions/sizes/overhang past the
edge, tallest part above and below.

## 2. Vertical stack-up (base floor upward)

```
floor_t                     profile value (3.0 on PETG-CF; ≥ 1.2 generic)
standoff_h                  ≥ 4 mm (solder tails); more with bottom-side parts
pcb_t                       1.6 typical (1.0 Pico, ~1.4 Raspberry Pi)
comp_top                    measure; + 2 mm headroom (+ wire bend room if cables plug in from above)
lid                         ceil_t + tongue/groove
```

Headers with Dupont wires plugged from above need ~15–20 mm above the pins. Side-entry
headers, JST-XH (~15 mm) and JST-PH (~10 mm) need less. A wiring bay (template
`bay_front` / `bay_back`) holds the extra height without growing `comp_top` over the
whole board. Details: `electronics-and-wiring.md` §7.

## 3. Holding the board

| Method | When | Notes |
|---|---|---|
| Standoffs + screws | board has holes | default; M2.5 for Raspberry Pi, M3 for most others; self-tap pilot 2.1 (M2.5) / 2.4 (M3) |
| Standoffs + heat-set inserts | board removed often | insert hole per vendor spec; standoff Ø ≥ insert hole + 3 |
| Pins (locating) + lid posts | quick, no screws | pin Ø = hole − 0.3; lid posts press the board with 0.2 mm interference |
| Card-guide slots/rails | board without holes (ESP32 DevKit, XIAO) | slot width = pcb_t + 0.3; rails 2 mm deep; a stop at the end |
| Snap clips over the board edge | holes absent, board rarely removed | see closures reference for strain |
| Header sockets on a carrier board | dev boards | the carrier gets the holes |

Keep standoff diameter clear of pads and components near the holes (check
keepout rings on the board; typically Ø 5–6 mm is safe for M3 holes).

## 4. Known board footprints (verify before printing)

Coordinates: origin at the bottom-left corner of the board in top view.

| Board | Outline (mm) | Mounting holes | Notes |
|---|---|---|---|
| Arduino Uno R3 / R4 | 68.6 × 53.3 | Ø3.2 at (14.0, 2.5), (15.3, 50.7), (66.1, 7.6), (66.1, 35.5) | USB and DC jack on the x = 0 edge and overhang it by ~6 mm; R3 USB-B is ~12 × 11 mm tall, R4 uses USB-C |
| Arduino Nano (classic/clones) | 18 × 45 | four small holes (~Ø1.8) near the corners | usually held by headers or rails; USB on a short edge (Mini-USB, micro or USB-C by clone) |
| Arduino Nano ESP32 / Every | 18 × 45 | as Nano | USB-C/micro on a short edge |
| ESP32 DevKitC (38-pin) | ≈ 54–55 × 28 | none | antenna at the short end opposite the USB; clones vary (48–58 × 25–28) |
| ESP32 30-pin DevKit clones | ≈ 51–52 × 28 | none (some have 4 × Ø2.5) | measure |
| Wemos D1 mini | 34.2 × 25.6 | none | USB on a short edge |
| Seeed XIAO (all variants) | 21 × 17.8 | none | USB-C on the short edge; castellated |
| Raspberry Pi 4 B / 3 B+ / 5 | 85 × 56 | M2.5, Ø2.7 at (3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5) | USB/Ethernet stack ~16 mm tall and overhangs the x = 85 edge by ~2–3 mm; Pi 5 needs active cooling |
| Raspberry Pi Zero / Zero 2 W | 65 × 30 | M2.5, Ø2.75 at (3.5, 3.5), (61.5, 3.5), (3.5, 26.5), (61.5, 26.5) | ports on the long edge at y = 0 |
| Raspberry Pi Pico / Pico W / Pico 2 | 51 × 21 × 1.0 | Ø2.1, 47 × 11.4 pattern (2.0 mm from short edges, 4.8 from long edges) | USB on a short edge; Pico W antenna at the opposite end |

## 5. Connector cutouts

Size the opening = connector body + `cutout_clear` (0.5 mm) per side (+0.25 more and a
1 mm 45° lead-in on user-facing ports), corner radius = body radius + clearance. In the
template each cutout is `[face, pos, z_above_board, w, h, r, user_facing, overmold]`,
with pos/z in board coordinates. Typical bodies (verify):

| Connector | Body opening W × H (mm) | Notes |
|---|---|---|
| USB-C receptacle | 8.9 × 3.3, r 1.6 | plug overmold ~10–13 × 5.5–7 |
| Micro-USB | 7.8 × 3.0 | plug overmold ~10 × 6 |
| Mini-USB | 7.7 × 4.0 | |
| USB-A (single) | 13.2 × 5.8 | |
| USB-B | 12.2 × 11 | |
| DC barrel jack (PCB, 5.5/2.1) | ≈ 9 × 11 | panel-mount versions use a round hole — check the datasheet thread |
| RJ45 | 16 × 13.5 | with LEDs: extend window |
| 3.5 mm audio | Ø6–6.5 | |
| microSD socket | 12 × 2 slot | add a finger notch Ø10 below |
| Toggle / rocker switches, panel pots | per datasheet (e.g. 6 mm or 7 mm shaft holes; 7 mm pots use Ø7.2) | add an anti-rotation tab slot if the part has one |

**The USB plug trap.** The plug's overmold is wider than the socket. If the
socket sits back from the outer surface by more than ~1.5 mm, the overmold
hits the wall and the plug never seats. Fix one of two ways:
1. Place the board so the socket face is within 0.5 mm of the inner wall, and
   keep the wall ≤ 1.5 mm at the socket, or
2. Recess the outer face around the opening to overmold size + tol per side,
   leaving ≤ 1 mm of wall at the socket — the template does this when a cutout's
   `overmold` is set (needed on the 2.52 mm PETG-CF wall).
Say which one you used. In the template the X-end walls sit a full column zone
(~10 mm) from the board, so connectors belong on the front/back faces — rotate the
board (swap pcb_x/pcb_y and the hole coordinates) if its ports are on a short edge.

Cutouts must not cross the lid split line unless you design them as notches
split between base and lid. The template asserts this.

When the connector overhangs the board edge (Uno USB/DC, Pi USB stack), shift
the board inward by the overhang and add the overhang to `pcb_gap` on that side.

## 6. Antennas and keepouts

- Wi-Fi/BLE modules with PCB antennas (ESP32-WROOM, Pico W, XIAO): place the
  antenna end near a wall, not in a corner packed with parts.
- Keep metal outside the profile's antenna keepout (15 mm generic, 20 mm on PETG-CF):
  screws, heat-set inserts, batteries, magnets. Carbon-fibre/metal-filled filament
  attenuates by itself. The template asserts inserts against `antenna`.
- No metal enclosures; plastic walls ≤ 3 mm are nearly transparent at 2.4 GHz.
- External antenna (u.FL → SMA): SMA bulkhead hole Ø6.5 with a D-flat if the
  connector has one.

A pin that looks free on the silkscreen can stop the board booting, corrupt its flash,
or read nothing while Wi-Fi is on. The pin map is in `electronics-and-wiring.md` §4.
Power budget, supplies, protection, wire gauge and connectors: the same file.
