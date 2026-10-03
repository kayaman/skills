---
name: "parametric-enclosures"
description: Design and revise parametric electronics enclosures with dimensioned fits, fasteners, PCB and connector clearances, print-oriented exports, and wiring guidance when needed. Preserve existing OpenSCAD or enclosure-maker Rhai projects; use OpenSCAD for new standalone designs. Pair with 3d-printing for process and calibration.
---

# Parametric enclosures for electronics

Enclosures fail in predictable ways: a screw boss cracks off the wall, a temperature
sensor reads the regulator instead of the room, a lid needs supports and comes out
scarred, a USB plug can't reach its socket because the wall is too thick, a Wi-Fi
module loses 10 dB because an insert sits next to the antenna, a pull on a cable rips
its solder joint. Every rule here exists to close one of those failure modes. Follow
them by default and say so when a brief forces an exception.

## Preserve the project format

Use the existing CAD language and parameter names. For `.rhai` projects read
`references/rhai-design-and-export.md`; do not replace them with OpenSCAD or use
OpenSCAD-only syntax. For an existing `.FCStd` project, or whenever the user asks
for FreeCAD, STEP, the FreeCAD MCP connection, or mechanical-CAD interchange, read
`references/freecad-design-and-export.md` and preserve that project the same way.
New standalone designs default to OpenSCAD when the user states no engine
preference. The Customizer, SCAD library and SCAD export contract below apply to
OpenSCAD only; the Rhai and FreeCAD references give the equivalent deliverables
for their engines. Process rules (fits, structural columns, ventilation, sensor
compartments, closures, safety) apply to all three.
Read `references/dimensions-and-calibration.md` for critical dimensions and fits.

## How this skill is organised — read only what the task needs

This file holds the workflow and the rules that apply to every enclosure. Detail lives
in `references/` and is loaded when the task touches it:

| When the task involves… | Read |
|---|---|
| **Any geometry** (always, before writing numbers) | `references/manufacturing-profiles.md` — the printer/material profile overrides generic numbers |
| Generic FDM limits, tolerances, holes, orientation, choosing a material, no profile applies | `references/fdm-design-rules.md` |
| Writing or debugging OpenSCAD: language, Customizer, libraries | `references/openscad-language.md` |
| Writing or debugging FreeCAD via the MCP connection: execute_code / _async / _headless choice, the parametric Python library, export, verification | `references/freecad-design-and-export.md` |
| File layout, assert/echo patterns, pitfalls that make bad STLs | `references/openscad-conventions.md` |
| Board footprints (Uno, Nano, ESP32, Pi, Pico, XIAO), holding the board, connector sizes, the USB plug trap | `references/pcb-and-components.md` |
| More than one module, a battery, a switched load or a cable leaving the box: power budget, pins, relays, MOSFETs, servos, LED strips, wire gauge, connectors, harness routing, the wiring bay | `references/electronics-and-wiring.md` |
| Any sensor in the brief | `references/sensors.md` — per-sensor chamber/aperture geometry |
| Lids, inserts, self-tapping, nuts, snap-fits, sliding lids, hinges, threads, magnets, split lines | `references/closures-and-fasteners.md` |
| Heat, vents, sealing/IP, outdoor/UV, RF, batteries, mains, children and pets | `references/environment-and-safety.md` |
| Buttons, LEDs/light pipes, displays, labels, wall/DIN/magnet mounting, feet, cable entry | `references/ui-and-mounting.md` |
| Rendering, exporting, interference checks, delivering in chat | `references/verification-and-export.md` |

Assets and tools (copy, don't re-derive):

- `assets/enclosure_lib.scad` — reusable modules: chamfered rounded boxes, gusseted
  filleted columns, standoffs, tongue-and-groove and the rim band for thin walls,
  face-frame cutters with lead-in chamfers, vent patterns, teardrops, keyholes,
  nut traps, snap hooks, labels, zip-tie anchors, cable channels and chamfered
  cable exits.
  Reusing it keeps geometry consistent across the user's product line.
- `assets/template.scad` — complete base + lid enclosure on the default profile. You give the board in its
  own coordinates (outline, holes, antenna, heat sources) and each connector by
  board edge; the template lays out the box from that: board against every wall
  with a connector, corner columns in the other sides, zones stretched to clear the
  antenna keepout, lid split above the tallest cutout, vents on free faces. It also
  has plug recesses, roofed openings, rails for boards without holes, an optional
  sensor chamber, wiring bays with cable exits and tie anchors, feet, ears or
  keyholes, asserts, a fastener BOM echo, and `part` views (assembly, exploded,
  base, lid, section, check). Start every new design from it; most briefs are
  parameter edits.
- `assets/selftest.scad` — renders every library module; run after any library change.
- `scripts/check_scad.py` — static check that runs without OpenSCAD.
- `scripts/export_parts.sh` — renders parts, the interference check and PNG previews.
- `assets/enclosure_lib.py` — the same module set as `enclosure_lib.scad`, ported to
  FreeCAD's Part/Draft API for the live MCP connection: chamfered rounded boxes (real
  OCCT chamfers), gusseted filleted bosses (real B-rep fillets, not the SCAD ring
  workaround), standoffs, tongue-and-groove, face-frame placements, vent patterns,
  cutters and wiring helpers. Load it once per FreeCAD session with `execute_code`
  (see `references/freecad-design-and-export.md`); `execute_code_headless` does not
  share that session and must re-load it.
- `assets/enclosure_template.py` — complete base + lid build on the house profile,
  parameters in a top-level `PARAMS` dict grouped like the Customizer. Builds named
  `Part::Feature` objects per part and a `set_view(doc, mode)` helper (assembly,
  exploded, base, lid, section, check) — the FreeCAD equivalent of the SCAD `part`
  switch; there is no CLI `-D`, so parameters are edited in the script text.
- `assets/selftest.py` — exercises every `enclosure_lib.py` function once; run after
  any library change, the same discipline as `selftest.scad`.

## Workflow

1. **Fill the brief** (below). Don't interrogate the user — extract what the
   conversation already gives you, pick defensible defaults for the rest, and tag
   each one `// ASSUMPTION:` in the code and in the ASSUMPTIONS section of the reply.
2. **Load the manufacturing profile** from `references/manufacturing-profiles.md`.
   It overrides numbers in this file and in the generic references — wall thickness,
   bridge limits, hole compensation, envelope, whether elastic features are allowed.
3. **Read the references your brief touches** (table above) — every sensor in
   `sensors.md`; a known board in `pcb-and-components.md`; outdoor/battery/child
   contexts in `environment-and-safety.md`; more than one module, a battery, a
   switched load or a cable out in `electronics-and-wiring.md`.
4. **Write the .scad** from `assets/template.scad` using `assets/enclosure_lib.scad`.
5. **Verify** (`check_scad.py`; render with `export_parts.sh` if OpenSCAD is
   available), run the self-check, then deliver per the output contract.

## The brief

Ask for nothing the conversation already answers. Defaults in brackets.

**PCB** — outline X × Y × thickness [1.6 mm], mounting hole Ø and coordinates from
the board's bottom-left corner, tallest component on top and bottom, keepouts
(antenna, HV, moving parts). Known dev boards: use the footprint table. Measure the
board **as assembled**, including soldered header pins above and below the PCB.
Record which board edge each header occupies and which side of the PCB carries the
plastic spacer, solder joint, exposed pin and Dupont housing. Never assume the two
header rows or four board edges are symmetric.

**Interfaces** — connectors (board edge, position along it, height above the board,
overhang past the edge), display, buttons, LEDs, switches, cable exits.

**Sensors** — type and what each must sense (airflow, field of view, acoustic port,
light path).

**Power and wiring** — supply (USB, adapter, battery, mains), every module and load
with its peak current, how they connect, and each cable that leaves the box [USB 5 V,
one board, no cables out]. Record whether devkits have soldered pins and whether
Dupont leads enter from above or from the side. The power budget sets `heat_w`, the
supply and the wiring bay.

**Thermal** — heat sources and rough dissipation, from the power budget [assume
< 0.3 W if nothing is said].

**Context** — indoor/outdoor, dust, moisture, and whether children or animals can
reach it. This changes the vent and battery rules, so raise it rather than silently
assuming.

**Mounting** — desk feet, wall, DIN rail, handheld [desk feet].

**Fasteners** — M3 heat-set inserts [default] or self-tapping screws.

**Limits** — maximum outer dimensions, aesthetics.

If the PCB dimensions are missing and it isn't a known board, that is the one thing
worth asking for. Everything else can be assumed and corrected later.

## Core rules

### Parametrisation and frames

Millimetres throughout. Every input lives in one Customizer block at the top of the
file, grouped with `/* [Group] */`; below `/* [Hidden] */` there are only derived
values — no magic numbers. That is what makes a design reusable at a different PCB size.

One coordinate frame: origin at the outer bottom-left-front corner of the base, +Z up.
Board features are given in board coordinates, as on the board's drawing, and
converted through `to_world()` (which applies `pcb_rot`), so every cutout is
dimensioned from the PCB origin, never from the wall (wall-referenced cutouts drift
when the wall changes). Expose `part` = assembly | exploded | base | lid |
section | check; only base/lid (and extra printable parts) are exported.

### Printability — supports are a defect, not an option

A part that needs supports has scarred internal surfaces exactly where the fits matter.
Every part prints on a flat face with nothing under it.

- Choose wall widths around ≥ 3 extrusion lines; verify actual paths in the slicer. Floor and ceiling
  at least as thick as the wall and ≥ 4 layers.
- No overhang steeper than 45° from vertical. Horizontal round holes above the
  profile's teardrop threshold get a teardrop or 45° roof. Downward-facing screw
  recesses get a 45° cone.
- Bridges stay under the profile's limit. Wider openings get a 45° roof (template
  `cutout_roof`); if you turn it off, say which tops will sag.
- Chamfer every plate-touching edge (elephant-foot relief) and visible top edges,
  unless the chamfer would eat a one-extrusion land (the lid's groove side). There,
  rely on the slicer's elephant-foot compensation and say so in the build notes.
- Nothing solid thicker than ~4 mm — hollow and rib it.
- Minimum feature 0.8 mm; minimum free-standing pin Ø 2 mm.

### Structural columns — the single most common failure

Every screw lands in a hollow column that runs floor to mating face, tied into the
shell. Never a thin flange, never a boss floating on a wall — that is a lever arm with
a layer line at its root.

- 2–4 triangular gussets per column, thickness = wall, height 60–80 % of the column,
  reaching about as far as they rise. The 45° is for stiffness: a rib standing on the
  floor prints at any slope, because each layer sits inside the one below. Route ribs
  away from the board (the template runs them along the wall of the zone that holds
  the column).
- Fillet gusset roots and the column-to-floor junction.
- Boss OD is at least the final CAD bore Ø + 2 × required radial wall and the profile minimum. Derive layout from the resulting OD.
- Heat-set inserts: use the actual insert manufacturer's hole shape, diameter,
  depth and installation guidance. Coupon-tested CAD bore dimensions already include
  process compensation. House M3 defaults are uncalibrated; straight bore, no mouth
  chamfer, and 1 mm relief are defaults for that example, not all insert products.
- Self-tapping: pilot ≈ 0.8 × major Ø (2.4 mm for M3), engagement ≥ 2 × Ø, boss wall ≥ 2 mm.
- Mating part: clearance hole (3.4 mm for M3, + hole_comp) plus counterbore/countersink.
- ≥ 4 columns up to a 100 mm span, one more per additional ~70 mm, plus one beside
  any connector that takes insertion force — a USB port pushed 200 times is a fatigue
  test of whatever holds that wall. The exception is the corner where two connector
  walls meet (Raspberry Pi): the board fills it, so three columns plus the register
  close the lid; add a fourth by hand if the lid must seal.
- Lid columns and PCB standoffs are separate: a column must never pass through the
  board's footprint.

### PCB fit and connectors

- Lateral clearance ≥ the profile's slip `tol` per side (template default 0.5 mm;
  clones vary), located by standoffs, or by rails and stops when the board has no
  holes (template `mount_holes = []`). Never press-fit a PCB.
- ≥ 2 mm above the tallest rigid top-side component. For a devkit with soldered
  headers and top-entry Dupont leads, use the **assembled wiring envelope**, not the
  bare-board component height: default `wiring_top_h = 28 mm` above the PCB top when
  no physical measurement exists, plus the normal 2 mm closure margin. Treat
  22 mm as a tight minimum only when the leads are pre-bent and restrained.
- Soldered pins below the PCB are part of the bottom stack, separately from
  `comp_bot`: default `pin_tail_h = 4 mm` when unmeasured. Set standoff height to
  at least pin-tail height + 1 mm; 5 mm is the normal minimum for pinned devkits.
  Pins and solder joints must not touch the floor, rails, keyhole heads or cable ties.
- Header placement is per board edge, before `pcb_rot`: `x0`, `x1`, `y0`, `y1`.
  One-sided soldering and right-angle headers are asymmetric geometry. Set
  `header_edge_clear = [x0, x1, y0, y1]` to the connector/harness projection beyond
  each edge; zero on unused edges. Expand only the affected face, and keep its
  envelope clear of rails, stops, columns, vents and the lid register. Do not centre
  the board to hide an asymmetric header unless that still preserves every port and
  antenna constraint.
- Cutouts +0.5 mm all round; +0.75 mm and a 1 mm lead-in chamfer on user-facing ports.
- **Plugs must reach their sockets.** A plug's overmold is wider than the socket; if
  the socket sits more than ~1.5 mm behind the outer surface, recess the outer face to
  overmold size so ≤ 1 mm of wall remains (template `overmold` field). A connector
  also needs its wall close to the board edge: the template puts the board against
  every wall that carries a connector and moves the columns to the other sides. Give
  each cutout by board edge and set `pcb_rot` to choose which wall that edge meets.
- Cutouts never cross the lid split unless deliberately split between both halves.
- Headers with Dupont wires plugged from above use `wiring_top_h`, independently of
  `comp_top`; do not hide connector and bend allowance inside a guessed component
  height. Top-entry Dupont defaults to 28 mm above the PCB top, while a measured,
  restrained side-entry harness may use less. Wiring that leaves the box, a second
  module, a battery or a switched load: the electronics and wiring reference. Give
  those runs a wiring bay (`bay_front` / `bay_back`) on the long side without
  connector cutouts, a zip-tie anchor at each exit, and a hole chamfered so the
  jacket cannot chafe. Keep a service loop to every part on the lid.

### Ventilation

Required when anything dissipates > ~0.3 W or the brief names a heat source.

- Slots 1.5–2.5 mm wide, ≤ 25 mm long, pitch ≥ slot + one wall — webs are structure.
- Vertical-wall slots print unsupported; on horizontal faces use short bridged slots
  or a vertex-up hex grid.
- Chimney: inlets in the lowest 25 % of one wall, outlets in the top 25 % of the
  opposite wall or the lid, so air crosses the heat source.
- Above 1 W maximise open area (aim ≥ 25 % of the vented wall) or add a fan.
- Children/animals: no opening > 4 mm in any direction, none directly above the PCB —
  offset louvres so there is no straight line from outside to electronics.

### Sensor compartments

Read `references/sensors.md` for per-sensor geometry. Universally: own chamber behind
a full-height divider with its own vents; ≥ 15 mm from any heat source plus a ≥ 3 mm
air gap or a slot through the divider (the template builds a two-skin divider); no dead
air pockets; serviceable without desoldering.

### RF

No conductive material, insert, column or rib inside the profile's antenna keepout
radius. Antenna over open plastic near an edge, minimum plastic in front of it; set
`antenna` and the template stretches the column zones until the inserts clear it.
Filled materials attenuate 2.4 GHz — say so and recommend an RSSI check.

### Electrical and safety

Printed plastic is not a qualified insulator, especially filled grades. ≥ 3 mm
creepage from any mains/HV net to the wall; never rest a bare conductor on plastic.
For mains, tell the user the safe path is a certified supply so the printed enclosure
sees only low voltage. Anything reachable by children or pets: no detachable small
parts, battery compartments that need a tool, magnets fully captured.

### Body and lid must fit

The two halves are one assembly. A lid that copies the body's outer rectangle and
rests on the rim does not fit: nothing stops it sliding, and a zero gap in the
model binds or rattles once it is printed. Reject that shape the same way you
reject a boss with no gusset.

- A continuous register around the opening. Tongue-and-groove is the default
  (`lip_tongue` on the base, `lip_groove_cut` in the lid). An internal lip or a
  stepped lap also counts. A butt joint does not.
- One slip clearance, from the profile, on each mating face. House slip is
  0.25 mm per side, inside the published FDM band for a lid that seats by hand
  (about 0.2–0.4 mm per side). Under that, elephant's foot and the rounded
  inside corner bind the lid. Past about 0.5 mm per side it rattles and the seam
  leaks light. Fix the tongue and open only the groove.
- `lip_groove_cut` adds its `tol` argument to the groove width once, so each
  flank receives half. Pass `2 * tol` when `tol` is the per-side slip, and a
  depth of tongue height plus one slip so the tongue does not bottom. The
  plastic left on both sides of that groove must still be at least one
  extrusion: `rim >= lip_w + 2 * ew + 2 * tol`. On a thinner wall the template
  thickens the rim inward under the tongue (`rim_band`, 45° underside). Do not
  delete the clearance to save the land.
- Tongue about 1.0–1.2 mm wide and 2 mm tall, with a short 45° lead-in so the
  lid finds the opening before the screws do. Relieve the groove's inside
  corners; FDM rounds them and a sharp tongue corner binds.
- Outline, tongue, and screw holes on both parts come from the same parameters.
  A hole that is only near a column misses.
- Assembled, `intersection()` of body and lid is empty (`part = "check"`). A
  section shows the gap, and the lid cannot shift in XY without the register
  stopping it.
- A mating face that prints on the bed spreads on its first layer and closes
  the gap. Chamfer that edge when the land allows it; the template's lid prints
  groove side down with a one-extrusion land, so it relies on elephant-foot
  compensation instead, and the build notes must say to keep it on.

### Assembly and serviceability

- Default closure: lid screwed into insert columns and located by the register
  above. Other closures: closures reference — check the profile before any
  elastic feature.
- One `tol` drives the fit table (press / slip / loose). Measure and record it
  for the printer, material, and process; reuse it across mating pairs, then
  revalidate after process changes.
- Screws from the least visible face (the template drives them down through the
  lid; the closures reference covers screwing up through the floor). Hide the
  parting seam on a chamfer (template `seam_ch`).
- Rubber-foot recesses (Ø 8 × 1 mm). For a wall, ears (`wall_mount = "ears"`,
  nothing inside can collide with them) or keyholes (Ø 7 / 3.5 mm, hidden, need a
  board deep enough to leave floor between the standoffs).
- Strain relief on every cable exit: a zip-tie anchor 10–20 mm inside the wall, so a
  pull never reaches a solder joint. `tie_anchor()` and `cable_exit_cut()` are in the
  library; the template places one of each per `cable_exits` entry.
- Deboss part name + version 0.4 mm deep, ≥ 3 mm tall, on an internal face.

### Clean CSG

Every cutter overshoots the faces it cuts by `EPS`; use `$fa`/`$fs`, coarser in
preview; no `minkowski()`; `assert()` every invariant that would otherwise print fine
and fail in assembly (fit, minimums, envelope, keepouts, cutouts vs split).

## Self-check before answering

State the verdict on each: (a) no part needs supports; (b) no overhang beyond 45°;
(c) every screw has a gusseted, filleted column that avoids the board; (d) every
sensor has a vented, thermally decoupled chamber; (e) antenna keepout respected;
(f) all cutouts referenced to the PCB origin through their board edge, and plugs can
reach their sockets;
(g) `assert()` statements present and passing; (h) export commands match the `part` values;
(i) every part fits the profile's build envelope; (j) context rules applied
(heat/vents, sealing, batteries, children/pets) or not applicable; (k) body and
lid locate each other with the slip clearance on each mating face. A rim-to-rim
plate fails (k) even when the two solids do not intersect. (l) when the brief has
more than one module, a battery, a switched load or a cable out: a power budget,
a pin map, a wiring table, a fuse at the source, and a keyed/latched or screwed
power connection; each cable exit has a zip-tie anchor and an anti-chafe hole.
(m) the vertical stack uses the assembled board: bottom soldered-pin envelope,
standoffs, PCB, top header/Dupont envelope, bend radius, and 2 mm closure margin;
with the actual harness installed, a section/check view shows no contact with the
lid, seam, columns or floor. A bare-board height check fails (m). (n) every soldered
header is assigned to its actual PCB face and edge; asymmetric top/bottom and
`x0`/`x1`/`y0`/`y1` envelopes are preserved through `pcb_rot`, and unused sides do
not receive invented clearance. A single symmetric header allowance fails (n).

If a check fails, fix the design before replying. Don't ship a caveat where geometry
was the answer. If the native renderer or slicer was unavailable, identify the checks that remain unverified. Never infer a mesh or physical-fit pass from static source checks.

## Output contract

For a new design, deliver in this order:

1. `<product>_enclosure.scad` — parametric, using `enclosure_lib.scad`.
2. `enclosure_lib.scad` alongside it, unless the user already has this version. If
   the user needs a single self-contained file (online renderer, paste into the
   editor), inline the used modules instead and say so.
3. One CLI export line per part:
   `openscad -D 'part="base"' -o base.stl <product>_enclosure.scad`
4. **BUILD NOTES** — per part: orientation and why, brim yes/no, bounding box vs
   envelope; layer height, material, supports (must read "none"), profile operator
   notes; fastener BOM with quantities and lengths (the template echoes one).
5. **WIRING** — when the brief has more than one module, a battery, a switched load
   or a cable leaving the box: power budget, pin map, wiring table, protection, harness
   notes, as in `electronics-and-wiring.md` §9. For a wiring question with no box,
   this section is the whole deliverable.
6. **ASSUMPTIONS** — every value the user did not specify.
7. **SELF-CHECK** — the list above.

Write the files to disk and present them when file tools exist; don't paste a long
.scad into prose. Without file tools, use one fenced block per file.

## Chat iteration protocol

The user will iterate ("move the USB 3 mm left", "thinner", "add a button"):

1. Return the **complete** updated file, not a fragment (unless asked for a diff).
2. **Keep parameter names stable** so Customizer presets and `-D` overrides keep
   working. Add parameters; don't rename them.
3. **Change the minimum** — prefer a parameter or list entry over restructuring.
4. Re-run the static check and re-render what changed before replying.
5. Reply with a short **CHANGES** list naming the parameters touched, any new
   assumption, and the self-check items affected — not the full contract again.
6. If a request conflicts with a rule (1 mm walls, snap-fits in PETG-CF), do it if it
   is merely suboptimal and name the consequence; push back only when the part would
   fail to print or fail its job.

## OpenSCAD compatibility

Target OpenSCAD 2021.01 syntax; it runs unchanged in development snapshots, which
render far faster with the Manifold backend. Avoid experimental features unless the
user runs a snapshot. Docs: https://openscad.org/documentation.html
