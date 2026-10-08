# Fits, closures and fasteners

Clearances are per side unless a row says diameter. The house profile's `tol`
(press 0.15 / slip 0.25 / loose 0.40 mm) replaces the generic table when that profile
is in force. One coupon in `assets/fit-coupon.scad` sets `tol` for the printer-material
pair; after that, leave it alone.

Vertical gaps only exist in whole layers. A 0.25 mm step at 0.2 mm layers becomes 0.2
or 0.4. Design Z clearances as a multiple of the layer height.

## Contents
1. Fit table
2. Choosing a closure
3. Body and lid, screwed lids
4. Heat-set inserts
5. Self-tapping screws
6. Nuts, nut traps, clearance holes
7. Snap-fits
8. Sliding lids
9. Hinges
10. Threads and twist-lock
11. Magnets
12. Split lines and alignment

## 1. Fit table (generic 0.4 mm nozzle, per side)

| Fit | Clearance | Use |
|---|---|---|
| Press | 0.00–0.10 mm | Pins and magnets that must stay. Too much interference splits a brittle boss |
| Snug | 0.10–0.15 mm | Friction lids, light press of a cap, light-pipe inserts |
| Slip | 0.20–0.30 mm | Sliding lids, lid lips, shafts, buttons in holes |
| Loose / print-in-place | 0.30–0.50 mm | Hinges and parts printed already assembled. Below about 0.3 mm a 0.4 mm nozzle tends to fuse them |

Printed part against a bought part: leave the slip clearance, and a little more when
the bought part's own tolerance is unknown (board-to-wall ≥ 0.5 mm; board outlines
vary ±0.2 mm). A lead-in chamfer on the pin or the hole mouth stops the edge catching
on layer lines.

Elephant's foot eats a fit that includes the bed edge. Chamfer that edge or keep the
mating diameter off the first layer.

## 2. Choosing a closure

| Closure | Opens | Sealing | Strength | Tolerance sensitivity | Pick when |
|---|---|---|---|---|---|
| Screwed lid + inserts, tongue-and-groove | often | good (with gasket) | high | low | **default**; anything that gets serviced |
| Screwed lid, self-tap | rarely | good | medium | low | cheap, few openings |
| Snap-fit | often | poor | low–medium | high | toys, quick access, no tools wanted |
| Friction lid (lip only) | often | poor | low | high | dust covers, prototypes |
| Sliding lid | often | poor | low | medium | battery doors, pencil-box style |
| Hinged | often | poor–medium | medium | medium | display/keypad covers |
| Threaded / bayonet | often | good (O-ring) | high | medium | round sensors, outdoor pods |
| Magnetic | very often | poor | low | low | access panels |

Check the profile first: the default PETG-CF profile forbids elastic features
(snap-fits, living hinges, flexing tabs) — use screws, tongue-and-groove and dowels.
Children/pet products: battery compartments must need a tool (screw) — see
`environment-and-safety.md`.

## 3. Body and lid, screwed lids

A lid that is a copy of the body's outline, sitting on the rim, does not fit. Nothing
locates it sideways. A zero gap in CAD becomes a bind or a rattle after printing,
because the first layer spreads and inside corners come out round.

Give the pair a continuous register: a tongue in a groove, a lip that drops inside
the opening, or a stepped lap. A butt joint is not a fit.

Fix the male feature and open only the female, by the slip clearance on each face. On
the house profile that is 0.25 mm per side. Published FDM practice for a lid that
seats by hand is about 0.2–0.4 mm per side (tighter binds, past about 0.5 mm it
rattles and the seam leaks light). Leave the depth one slip deeper than the tongue so
it does not bottom out. Vertical gaps still have to land on a whole layer.

The wall has to afford that gap. Plastic left on both sides of the groove stays at
least one extrusion wide: `rim >= lip_w + 2 * ew + 2 * tol`. If it does not, narrow
the tongue toward 1.0 mm, add a perimeter, or thicken the rim inward under the tongue
(the enclosure template's `rim_band`, with a 45° underside so it prints without
support) — or hang a locating lip from the lid inside the cavity, notched around the
columns. Do not close the clearance to save the land. A short 45° lead-in lets the
lid find the opening. Relieve the groove's inside corners: FDM rounds them and a
sharp tongue corner binds.

Both parts share one set of dimensions. A screw hole that is merely near its boss
misses. In the assembled position the two solids do not intersect, a section shows
the gap, and the lid cannot shift sideways without the register stopping it. Chamfer
whichever mating edge is printed on the bed.

Screwed-lid specifics (the enclosure default):

- Screws along Z through the lid into gusseted insert columns in the base corners.
  Columns run floor to mating face and never pass through the board; the template
  only places one where a column zone can hold it, so a board with connectors on two
  adjacent walls gets three.
- Tongue on the base rim, about 1.0–1.2 mm wide × 2 mm tall. Groove in the lid,
  opened by the slip clearance on each face and one slip deeper than the tongue.
  `lip_groove_cut` adds its `tol` argument to the width once, so pass `2 * tol` for a
  full slip on each flank.
- The lid prints mating face down, so the groove mouth is on the bed and its first
  layer spreads into the groove. The land beside it is one extrusion, so there is no
  room for a chamfer: keep the slicer's elephant-foot compensation on (Bambu Studio
  default 0.15 mm) and say so in the build notes.
- Spacing ≤ 60–80 mm between screws for a stiff lid; ≤ 50 mm for a gasket.
- Counterbores (head recess) need `top_t ≥ head height + 1.2`; otherwise let pan
  heads sit on top.
- Screws in the bottom (through the base floor into the lid) hide the hardware;
  bosses then hang from the lid.

## 4. Heat-set inserts

Thread size does not identify the insert body. Record vendor/part number,
body and pilot diameters, length, recommended hole diameter/shape, and installation
method. Follow the selected product's drawing: some inserts require straight holes,
others tapered holes. Mouth relief and depth allowance are product-specific.
[SPIROL's hole-design guidance](https://my.spirol.com/resources/white-papers/how-to-design-the-proper-hole-for-heat-ultrasonic-inserts/)
explains why hole dimensions and surrounding plastic depend on the insert.

Determine whether a quoted dimension is a target manufactured hole or an already
compensated FDM CAD recommendation. Do not blindly add 0.2–0.3 mm or `hole_comp`.
A coupon-selected bore is the final CAD dimension. Use the same mouth treatment,
wall, depth, orientation and material in the coupon and production boss.

For the existing house M3 example only: final CAD bore starts at 4.1 mm,
insert length 5.7 mm, relief 1.0 mm, no mouth chamfer, boss OD at least 9.5 mm
and radial plastic at least 2.5 mm. These are **uncalibrated assumptions**, not
standard M3 dimensions. Confirm or replace them using the actual insert.
Grow OD to at least `bore + 2 * required_wall`, preserve the blind floor,
and brace loaded columns into the shell. Check screw engagement and bottom
clearance; thread size alone does not establish either.

Use the manufacturer's installation temperature/process and a trial boss.
Do not derive an iron temperature from nozzle temperature as a universal rule.
Inspect seating, cracking, spinning and application-appropriate pull-out/torque
before relying on the assembly. A visual fit test does not establish load capacity.

## 5. Self-tapping screws

For parts opened rarely.

- Pilot Ø ≈ 0.8 × thread major: M2 → 1.6, M2.5 → 2.0–2.1, M3 → 2.4–2.5, M4 → ~3.2.
- Engagement ≥ 2 × diameter. Boss OD ≈ 2.2–2.5 × thread diameter, boss wall ≥ 2 mm.
- Thread-forming screws for plastic (Plastite/PT) hold far better than a machine
  screw driven into a pilot.
- Expect a handful of reassemblies (~5–10), then stripped threads. That is the moment
  to switch to an insert.

## 6. Nuts, nut traps, clearance holes

| Thread | Clearance hole | Head Ø (socket/pan) | Hex nut AF / thickness | Printed trap AF / depth |
|---|---|---|---|---|
| M2 | 2.4 | 3.8 | 4.0 / 1.6 | 4.2 / 1.8 |
| M2.5 | 2.9 | 4.5 | 5.0 / 2.0 | 5.2 / 2.2 |
| M3 | 3.4 | 5.5–5.7 | 5.5 / 2.4 | 5.7–5.8 / 2.6 |
| M4 | 4.5 | 7.0 | 7.0 / 3.2 | 7.2–7.3 / 3.4 |
| M5 | 5.5 | 8.5 | 8.0 / 4.0 | 8.3 / 4.2 |

Nut trap: `cylinder(d = poly_d(af_trap, 6), $fn = 6)` (library:
`hex_nut_trap_cut(af, depth)`). Add the clearance hole plus counterbore or
countersink on the mating part.

A nut slot that opens on a vertical face (side-slide) prints clean. A hexagonal
pocket under a horizontal ceiling has to bridge: keep that span inside the profile's
bridge limit, open the pocket from the side, or add a sacrificial 0.2 mm layer the
user drills through.

## 7. Snap-fits (cantilever)

Only when the profile allows elastic features. Not on house PETG-CF: use screws, or
switch to unfilled PETG; if the user insists, the profile's clip limits apply and the
fatigue risk goes in the build notes. Allowed in PLA (barely), PETG, ABS, ASA, nylon,
and TPU.

Geometry: beam length L, thickness t (in the bending direction), hook depth y
(deflection needed to pass the catch). For a constant rectangular section:

```
strain ε = 1.5 · y · t / L²          (keep below the material limit)
```

| Material | Allowable ε (repeated use) |
|---|---|
| PLA | ≤ 1 % (brittle; single-use snaps up to ~2 %) |
| PETG, ABS, ASA | ≤ 2 % |
| Nylon | ≤ 3–4 % |

Example: t = 1.6, y = 0.8 → L ≥ sqrt(1.5 · 0.8 · 1.6 / 0.02) ≈ 9.8 mm for PETG. Make
the arm 12–15 mm to be safe.

Design rules:
- Beam in the XY plane when possible (bending across a single layer breaks beams). If
  it must stand vertically, go thicker/longer and use PETG or nylon.
- Root fillet ≥ 0.5 × t; tapering the beam (t at root → 0.5 t at tip) spreads the
  strain more evenly — or simply make the beam longer.
- Lead-in face around 30–45°; a 90° return face is permanent, 45–60° can be opened
  again. Provide a release slot for a screwdriver if the face angle is 90°, or the
  user will pry the arm off.
- Catch windows in the opposite wall: hook height + 0.3 mm clearance.
- Library: `snap_hook(length, thick, width, hook_depth, hook_h)`.

Living hinges that fold flat are a polypropylene (and sometimes nylon or TPU)
feature. PLA, PETG, and PETG-CF crack. Do not call a thin PETG bridge a living hinge.

## 8. Sliding lids

- Rails: 45° dovetail or a rectangular groove 1.5–2 mm deep in the walls, clearance
  0.25 mm per side.
- Print the lid flat (lid plate on the bed); print grooves with 45° upper flanks so
  the base needs no supports.
- Add a detent bump (0.3–0.5 mm) near the closed position and a finger grip.

## 9. Hinges

- Pin hinge with separate pin: knuckle OD ≥ pin Ø + 3; pin hole = pin + 0.3. A
  1.75 mm filament strand or an M2/M3 screw makes a good pin. Size the knuckle hole
  to the pin plus the slip clearance.
- Print-in-place hinge: 0.4–0.5 mm clearance, cone-shaped pin tips (45°) so the
  knuckles self-support; print with the hinge axis parallel to the bed.
- Living hinges only in PP/TPU/nylon, never PLA/PETG.
- Add a stop to limit the opening angle.

## 10. Threads and twist-lock

- Don't hand-write thread profiles; use BOSL2 `threaded_rod()/threaded_nut()` if the
  user has it, or a bayonet (2–3 L-slots with a detent bump), which is easy to model
  and prints well.
- Printed threads: pitch ≥ 2 mm, trapezoidal/buttress profile, 0.3–0.4 mm radial
  clearance, first turn chamfered. Fine machine threads below about M5 belong in an
  insert.
- Print the thread axis along Z when cosmetics and fit matter. A horizontal thread is
  a stack of overhangs.
- O-ring in a face groove for sealing (see `environment-and-safety.md`).

## 11. Magnets

- Round neodymium magnets: pocket Ø = magnet + 0.1–0.2 mm (press) or +0.3 mm with
  glue; depth = magnet thickness + 0.2 mm. Chamfer the mouth.
- On a brittle material, a press fit that is too tight cracks the pocket. Prefer the
  loose pocket plus a drop of glue, or a thin printed cap, over a heroic interference.
- Fully captured magnets: pause the print at the layer that closes the pocket, drop
  the magnet in, resume. Tell the user the Z height; confirming the pause layer is
  covered in `mesh-and-export.md`.
- Mark polarity; opposite poles on the two parts. Polarity is part of the design when
  two parts meet.
- Keep magnets away from compasses and hall sensors, and ≥ 15 mm from antennas.
- Products for children/pets: magnets must be fully enclosed, never glued in a pocket
  where they can come loose.

## 12. Split lines and alignment

- Horizontal split with the lid on top is the default: each half prints without
  supports.
- Split just above the tallest side connector so all side cutouts live in the base;
  or split through the connector and make matching half-notches in base and lid.
- Deep enclosures: a mid split (two shells) keeps each part short and gives full
  access to the board.
- Alignment is not optional. Tongue-and-groove (default; also helps sealing), an
  internal lip, or a stepped lap. A butt joint fails the fit rule. Dowel pins
  (printed Ø 4 mm pockets, 0.20 mm clearance per side) are for parts split to fit the
  envelope, in addition to the lid register, not instead of it.
- Parts too big for the envelope: split and join with M3 bolts + ≥ 2 dowels, never
  glue (PETG doesn't bond reliably).
