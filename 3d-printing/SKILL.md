---
name: 3d-printing
description: Design, review, calibrate, and prepare parts for FDM, resin, or SLS printing, and design 3D-printable electronics enclosures as parametric OpenSCAD, FreeCAD, or Rhai models. Use for printability, materials, orientation, wall thickness, fits, fasteners, STL/3MF checks, slicer settings, failed prints, and for any enclosure, case, housing, or "caixa" for a PCB, dev board (ESP32, Arduino, Raspberry Pi, Pico, STM32), or sensor node — including PCB standoffs, connector cutouts, vents, sensor chambers, antenna keepouts, wiring, and STL/3MF export.
---

# 3D printing and parametric enclosures

Printed parts fail in a few repeatable ways. A fit face is scarred by supports. A
load peels the layers apart. A hole prints small and a screw will not start. A clip
cracks because the plastic is filled and brittle. A screw boss cracks off the wall. A
temperature sensor reads the regulator instead of the room. A USB plug cannot reach
its socket because the wall is too thick. A Wi-Fi module loses 10 dB because an
insert sits next to the antenna. A pull on a cable rips its solder joint. Every rule
here exists to close one of those failure modes. Fix them in the process choice and
the geometry; a slicer setting is the second move, and only after the shape is
printable. Follow the rules by default and say so when a brief forces an exception.

Numbers in the references are starting points from printer vendors (Prusa, Bambu,
Formlabs) and from desktop FDM practice. A fit coupon printed on the actual machine
overrides every one of them.

## Scope

One skill, two job families that share the same profile, FDM rules, and
verification. **Process jobs**: which machine, which material, which way up, what
the slicer must do, and whether the shape can survive that — new parts, design
reviews, print plans for a mesh, failed prints, material questions. **Enclosure
jobs**: parametric electronics enclosures — PCB fit, connectors, closures, vents,
sensors, wiring, and their export as printable parts. A wiring or power question
with no box is still an enclosure-family job (the wiring reference is the whole
deliverable).

Match the length of the reply to the question. A material comparison does not need a
print plan. The full contracts below are for a part you are designing or clearing to
print.

## Preserve the project format

Use the existing CAD language and parameter names. For `.rhai` projects read
`references/rhai-design-and-export.md`; do not replace them with OpenSCAD or use
OpenSCAD-only syntax. For an existing `.FCStd` project, or whenever the user asks for
FreeCAD, STEP, the FreeCAD MCP connection, or mechanical-CAD interchange, read
`references/freecad-design-and-export.md` and preserve that project the same way. New
standalone enclosure designs default to OpenSCAD when the user states no engine
preference. The Customizer, SCAD library and SCAD export contract apply to OpenSCAD
only; the Rhai and FreeCAD references give the equivalent deliverables for their
engines. Process rules (fits, structural columns, ventilation, sensor compartments,
closures, safety) apply to all three. If the user already has a mesh, review it
against the chosen process; do not rebuild it in another CAD tool unless they ask.

## Read only what the job needs

This file holds the workflow and the rules that apply to every part. Detail lives in
`references/` and is loaded when the task touches it:

| When the job involves… | Read |
|---|---|
| **Any geometry** (always, before writing numbers) | `references/manufacturing-profiles.md` — the printer/material profile overrides generic numbers |
| Generic FDM limits, walls, overhangs, holes, orientation, strength, no profile applies | `references/fdm-design-rules.md` |
| Critical dimensions, mating parts, a fit coupon, parametric dimension discipline | `references/dimensions-and-calibration.md` |
| Fits, lids, inserts, screws, nuts, snaps, sliding lids, hinges, threads, magnets, split lines | `references/fits-and-fasteners.md` |
| Choosing or swapping a plastic | `references/materials.md` |
| A slicer plan, calibration, or a print that already failed | `references/slicer-and-troubleshooting.md` |
| Resin (SLA/MSLA), or a feature FDM cannot hold | `references/resin.md` |
| SLS or MJF, usually a bureau | `references/sls.md` |
| An STL or 3MF to review or fix, or a model you are exporting | `references/mesh-and-export.md`, then `scripts/check_stl.py` on every STL |
| Writing or debugging OpenSCAD: language, Customizer, libraries | `references/openscad-language.md` |
| SCAD file layout, assert/echo patterns, pitfalls that make bad STLs | `references/openscad-conventions.md` |
| FreeCAD via the MCP connection: execute_code choice, the parametric Python library, export | `references/freecad-design-and-export.md` |
| An existing enclosure-maker `.rhai` project; updating that app's printing-guidance resource | `references/rhai-design-and-export.md`, which routes to `references/enclosure-maker-agent.md` |
| Board footprints (Uno, Nano, ESP32, Pi, Pico, XIAO), holding the board, connector sizes, the USB plug trap | `references/pcb-and-components.md` |
| More than one module, a battery, a switched load or a cable leaving the box: power budget, pins, relays, wire gauge, harness routing, the wiring bay | `references/electronics-and-wiring.md` |
| Any sensor in the brief | `references/sensors.md` — per-sensor chamber/aperture geometry |
| Heat, vents, sealing/IP, outdoor/UV, RF, batteries, mains, children and pets | `references/environment-and-safety.md` |
| Buttons, LEDs/light pipes, displays, labels, wall/DIN/magnet mounting, feet, cable entry | `references/ui-and-mounting.md` |
| Rendering, exporting, interference checks, delivering SCAD/FreeCAD work in chat | `references/verification-and-export.md` |

Assets and tools (copy, don't re-derive):

- `assets/fit-coupon.scad` — one print (~84 × 57 mm) that sets `hole_comp`, `tol`,
  and the insert bore for a printer-material pair. Edit its parameters for another
  nozzle or insert; do not redraw it.
- `assets/enclosure_lib.scad` — reusable modules: chamfered rounded boxes, gusseted
  filleted columns, standoffs, tongue-and-groove and the rim band, face-frame
  cutters, vent patterns, teardrops, keyholes, nut traps, snap hooks, labels,
  zip-tie anchors, cable channels and chamfered cable exits. Reusing it keeps
  geometry consistent across the user's product line.
- `assets/template.scad` — complete base + lid enclosure on the default profile.
  Give it the board in its own coordinates (outline, holes, antenna, heat sources)
  and each connector by board edge; it lays out the box from that: board against
  every connector wall, corner columns elsewhere, zones stretched to clear the
  antenna keepout, lid split above the tallest cutout, vents on free faces, plus
  plug recesses, roofed openings, rails, an optional sensor chamber, wiring bays,
  feet/ears/keyholes, asserts, a fastener BOM echo, and `part` views (assembly,
  exploded, base, lid, section, check). Start every new design from it; most briefs
  are parameter edits.
- `assets/selftest.scad` — renders every library module; run after any library change.
- `assets/enclosure_lib.py` — the same module set ported to FreeCAD's Part/Draft API
  for the live MCP connection (real OCCT chamfers and B-rep fillets). Load it once
  per FreeCAD session with `execute_code`; `execute_code_headless` does not share
  that session and must re-load it.
- `assets/enclosure_template.py` — the FreeCAD equivalent of `template.scad`:
  parameters in a top-level `PARAMS` dict, named `Part::Feature` objects per part,
  and a `set_view(doc, mode)` helper. There is no CLI `-D`; parameters are edited in
  the script text.
- `assets/selftest.py` — exercises every `enclosure_lib.py` function once; same
  discipline as `selftest.scad`.
- `scripts/check_stl.py` — standard-library STL topology/envelope/bed checker.
- `scripts/check_scad.py` — static SCAD check that runs without OpenSCAD.
- `scripts/export_parts.sh` — renders parts, the interference check and PNG previews.

## Workflow

1. **Classify the job.** Enclosure design or revision; new non-enclosure part; design
   review of an existing model; print plan for a mesh; failed print; material
   question; wiring question. Failed prints start in
   `references/slicer-and-troubleshooting.md` and come back here only if the fix is
   geometry. A mesh starts with the units, envelope, and manifold checks in
   `references/mesh-and-export.md`. An enclosure that is "too low", will not close,
   or does not fit after wiring is a geometry/measurement failure, not a slicer
   problem: rebuild the vertical stack from the assembled board (soldered pins below
   the devkit, standoff, PCB, seated Dupont housing, relaxed wire bend, closure
   margin), never scale Z or force the lid.
2. **Pick the process.** Desktop FDM on the house profile unless the part cannot
   succeed there or the user names another process. See the table below.
3. **Load the profile** from `references/manufacturing-profiles.md`. Use it without
   asking. A named printer or material replaces it; write the override down and
   recompute anything that came from extrusion width.
4. **For an enclosure: fill the brief** (below) and read the references it touches —
   every sensor in `sensors.md`; a known board in `pcb-and-components.md`;
   outdoor/battery/child contexts in `environment-and-safety.md`; more than one
   module, a battery, a switched load or a cable out in
   `electronics-and-wiring.md`. Then write the `.scad` from `assets/template.scad`
   using `assets/enclosure_lib.scad` (or the engine the project already uses).
5. **For any part: decide orientation before shape.** The bed face, the weak axis,
   and which face may be sacrificed determine the geometry. Infer the load from how
   the part is used and tag that inference as an assumption. Change the geometry so
   the part prints without supports on a working face, so the load does not peel
   layers, and so the part is one solid with no island in the air. A warning in the
   reply is not a fix.
6. **Verify and export.** Run `scripts/check_scad.py` on SCAD sources; render with
   `scripts/export_parts.sh` when OpenSCAD is available. One STL per part, bed face
   on z = 0. Run `scripts/check_stl.py` with the selected envelope, layer height and
   `--require-bed` on every STL. Fix measured errors; resolve sampled warnings in the
   slicer. An `ok` result covers only the checks listed in the report; it does not
   certify printability.
7. **Deliver** the contract that matches the job, then run the self-check.

## Process choice

The house machine is an open-frame FDM printer. Recommend another process only when
FDM cannot do the job, and say what the user must own or order.

| The part needs… | Use |
|---|---|
| A bracket, jig, fixture, enclosure, replacement, or anything larger than a few centimetres | FDM, house profile |
| A feature thinner than one extrusion, crisp tiny text, or a smooth small cosmetic part | Resin, if they have a printer or will order one. Read `references/resin.md` |
| Enclosed channels, a batch of complex nylon parts, or no support scars on every face | SLS/MJF at a bureau. Read `references/sls.md` |
| A seal, grip, bumper, or flexure | FDM TPU. That is not the house material |
| A snap, clip, or living hinge | Unfilled PETG, nylon, PP, or TPU. Not house PETG-CF; switch the profile to unfilled PETG on the same printer |
| Outdoor UV | ASA on an enclosed printer, or unfilled PETG for mild exposure. PETG-CF is stiff, not a UV or high-heat material |
| Heat above about 70 °C (car cabin, near a heater) | Not PLA and not house PETG-CF. ABS, ASA, PC, or a higher-temp filled nylon/PET on an enclosed printer |

## Rules that apply to every FDM part

The profile overrides the numbers. The reasons live in `references/fdm-design-rules.md`.

- Choose walls and ribs around whole extrusion widths, and floors around whole layer
  heights. Use this as a house design target; confirm actual perimeter coverage in
  the slicer, which may vary line width and overlap. Minimum feature 0.8 mm; minimum
  free-standing pin Ø 2 mm.
- Supports are a defect, not an option. Every part prints on a flat face with nothing
  under it. Overhangs stay at or under the profile limit, measured from vertical;
  steeper needs a chamfer, a teardrop, or a different orientation. Supports on a fit,
  seal, or sliding face are a design failure.
- Horizontal holes print oval. Above the profile's teardrop threshold, use a teardrop
  or a flat bridged top, or plan to drill. Downward-facing screw recesses get a 45°
  cone.
- Vertical holes print small. Add the profile's hole compensation on functional
  diameters only.
- Bridges stay under the profile's limit. Wider openings get a 45° roof (template
  `cutout_roof`); if you turn it off, say which tops will sag.
- Chamfer every edge that runs parallel to the bed, including the bed contact and the
  underside of a lip — a fillet there starts as a flat overhang — unless the chamfer
  would eat a one-extrusion land (the lid's groove side); there, rely on the slicer's
  elephant-foot compensation and say so in the build notes. Fillet vertical edges,
  and fillet a loaded internal corner without thinning the wall. On filled or brittle
  plastic the inside radius is at least 1 mm.
- Nothing solid thicker than about 4 mm. Hollow it and rib it. Thick lumps warp and
  do not get stronger in proportion.
- The part is weakest between layers. Tension and bending stay in the XY plane of the
  print. A screw that pulls a flange apart along Z is peeling the stack.
- Every part fits the profile envelope, or it is split and joined with fasteners and
  dowels. Do not specify cyanoacrylate on PETG or PETG-CF; it does not hold.
- One named clearance drives each fit. "Make it tight" is not a dimension.
- Each exported part is one solid. Fuse intended features with a deliberate overlap
  and check the exported topology. Keep a structural neck wide enough for its load;
  two extrusion widths is only a geometric starting minimum.
- Nothing starts in mid-air. In the print orientation every region has plastic under
  it, down to the bed, or it is a bridge within the profile limit whose ends land on
  walls. An island is a modeling error, including one that rejoins the body only
  higher up.
- The STL topology is checked before it reaches the slicer. Every edge has two faces,
  windings agree, and there are no collapsed triangles. Clicking Repair is not a step
  in the plan; repair can change intended holes or thin walls, so inspect the result
  instead of assuming equivalence. Details and the checker are in
  `references/mesh-and-export.md`.

### Body and lid must fit

The two halves are one assembly. A lid that copies the body's outer rectangle and
rests on the rim does not fit: nothing stops it sliding, and a zero gap in the model
binds or rattles once printed. Reject that shape the same way you reject a boss with
no gusset. Give the pair a continuous register — tongue-and-groove (default), an
internal lip, or a stepped lap; a butt joint does not count — with one slip
clearance, from the profile, on each mating face. Fix the tongue and open only the
groove. Outline, tongue, and screw holes on both parts come from the same
parameters. Assembled, `intersection()` of body and lid is empty (`part = "check"`),
a section shows the gap, and the lid cannot shift in XY without the register
stopping it. The dimensions, the groove-land rule and the `lip_groove_cut`
semantics are in `references/fits-and-fasteners.md` §3.

## Fasteners in one pass

Read `references/fits-and-fasteners.md` before drawing a boss. Short version, so a
casual answer does not invent a hole:

- Repeated assembly: heat-set insert. Select bore shape and dimensions from the
  actual manufacturer and validate the final CAD bore on a coupon. House M3 starts at
  9.5 mm boss OD and at least 2.5 mm radial plastic; grow the OD for larger bores.
- A few assemblies, then never again: self-tapping or thread-forming screw. Pilot
  about 0.8 × major diameter, engagement at least 2 × diameter, boss wall ≥ 2 mm.
- Mating part: clearance hole (3.4 mm for M3, + `hole_comp`) plus
  counterbore/countersink.
- Printed threads are for coarse, lightly loaded closures. Below about M5, use an
  insert.
- Snaps and living hinges follow the strain limit in the fasteners reference, and
  only in a material that can flex. On house PETG-CF, offer screws or a switch to
  unfilled PETG. If the user insists on a PETG-CF clip, apply the limits in
  `references/manufacturing-profiles.md` and put the fatigue risk in Watch-out.

## Enclosure design

### The brief

Don't interrogate the user — extract what the conversation already gives, pick
defensible defaults for the rest, and tag each one `// ASSUMPTION:` in the code and
in the ASSUMPTIONS section of the reply. Defaults in brackets.

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

### Parametrisation and frames

Millimetres throughout. Every input lives in one Customizer block at the top of the
file, grouped with `/* [Group] */`; below `/* [Hidden] */` there are only derived
values — no magic numbers. That is what makes a design reusable at a different PCB
size. One coordinate frame: origin at the outer bottom-left-front corner of the base,
+Z up. Board features are given in board coordinates, as on the board's drawing, and
converted through `to_world()` (which applies `pcb_rot`), so every cutout is
dimensioned from the PCB origin, never from the wall (wall-referenced cutouts drift
when the wall changes). Expose `part` = assembly | exploded | base | lid | section |
check; only base/lid (and extra printable parts) are exported.

### Structural columns — the single most common failure

Every screw lands in a hollow column that runs floor to mating face, tied into the
shell. Never a thin flange, never a boss floating on a wall — that is a lever arm
with a layer line at its root.

- 2–4 triangular gussets per column, thickness = wall, height 60–80 % of the column,
  reaching about as far as they rise. The 45° is for stiffness: a rib standing on the
  floor prints at any slope, because each layer sits inside the one below. Route ribs
  away from the board (the template runs them along the wall of the zone that holds
  the column).
- Fillet gusset roots and the column-to-floor junction.
- Boss OD is at least the final CAD bore Ø + 2 × required radial wall and the profile
  minimum. Derive layout from the resulting OD.
- Heat-set inserts: use the actual insert manufacturer's hole shape, diameter, depth
  and installation guidance. Coupon-tested CAD bore dimensions already include
  process compensation. House M3 defaults are uncalibrated; straight bore, no mouth
  chamfer, and 1 mm relief are defaults for that example, not all insert products.
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
  headers and top-entry Dupont leads, use the **assembled wiring envelope**, never
  the bare-board component height: default `wiring_top_h = 28 mm` above the PCB top
  when no physical measurement exists (22 mm only for a pre-bent, restrained
  harness), plus the normal 2 mm closure margin. Soldered pins below the PCB are
  part of the bottom stack, separately from `comp_bot`: default `pin_tail_h = 4 mm`
  when unmeasured, standoffs ≥ pin-tail height + 1 mm (5 mm is the normal minimum
  for pinned devkits), and pins and solder joints must not touch the floor, rails,
  keyhole heads or cable ties. The full stack-up table is in
  `references/pcb-and-components.md` §2.
- Header placement is per board edge, before `pcb_rot`. One-sided soldering and
  right-angle headers are asymmetric geometry: set `header_edge_clear =
  [x0, x1, y0, y1]` to the connector/harness projection beyond each edge, zero on
  unused edges, expand only the affected face, and keep its envelope clear of rails,
  stops, columns, vents and the lid register. Do not centre the board to hide an
  asymmetric header unless that still preserves every port and antenna constraint.
- Cutouts +0.5 mm all round; +0.75 mm and a 1 mm lead-in chamfer on user-facing ports.
- **Plugs must reach their sockets.** A plug's overmold is wider than the socket; if
  the socket sits more than ~1.5 mm behind the outer surface, recess the outer face
  to overmold size so ≤ 1 mm of wall remains (template `overmold` field). A connector
  also needs its wall close to the board edge: the template puts the board against
  every wall that carries a connector and moves the columns to the other sides. Give
  each cutout by board edge and set `pcb_rot` to choose which wall that edge meets.
- Cutouts never cross the lid split unless deliberately split between both halves.
- Headers with Dupont wires plugged from above use `wiring_top_h`, independently of
  `comp_top`; do not hide connector and bend allowance inside a guessed component
  height. Wiring that leaves the box, a second module, a battery or a switched load:
  the electronics and wiring reference. Give those runs a wiring bay (`bay_front` /
  `bay_back`) on the long side without connector cutouts, a zip-tie anchor at each
  exit, and a hole chamfered so the jacket cannot chafe. Keep a service loop to every
  part on the lid.

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
air gap or a slot through the divider (the template builds a two-skin divider); no
dead air pockets; serviceable without desoldering.

### RF

No conductive material, insert, column or rib inside the profile's antenna keepout
radius. Antenna over open plastic near an edge, minimum plastic in front of it; set
`antenna` and the template stretches the column zones until the inserts clear it.
Filled materials attenuate 2.4 GHz — say so and recommend an RSSI check.

### Electrical and safety

Printed plastic is not a qualified insulator, especially filled grades, and layer
lines are not food-safe. ≥ 3 mm creepage from any mains/HV net to the wall; never
rest a bare conductor on plastic. For mains, tell the user the safe path is a
certified supply so the printed enclosure sees only low voltage. Anything reachable
by children or pets: no detachable small parts, battery compartments that need a
tool, magnets fully captured.

### Assembly and serviceability

- Default closure: lid screwed into insert columns and located by the register
  above. Other closures: `references/fits-and-fasteners.md` — check the profile
  before any elastic feature.
- One `tol` drives the fit table (press / slip / loose). Measure and record it for
  the printer, material, and process; reuse it across mating pairs, then revalidate
  after process changes.
- Screws from the least visible face (the template drives them down through the lid;
  the fasteners reference covers screwing up through the floor). Hide the parting
  seam on a chamfer (template `seam_ch`).
- Rubber-foot recesses (Ø 8 × 1 mm). For a wall, ears (`wall_mount = "ears"`, nothing
  inside can collide with them) or keyholes (Ø 7 / 3.5 mm, hidden, need a board deep
  enough to leave floor between the standoffs).
- Strain relief on every cable exit: a zip-tie anchor 10–20 mm inside the wall, so a
  pull never reaches a solder joint. `tie_anchor()` and `cable_exit_cut()` are in the
  library; the template places one of each per `cable_exits` entry.
- Deboss part name + version 0.4 mm deep, ≥ 3 mm tall, on an internal face.

### Clean CSG

Every cutter overshoots the faces it cuts by `EPS`; use `$fa`/`$fs`, coarser in
preview; no `minkowski()`; `assert()` every invariant that would otherwise print fine
and fail in assembly (fit, minimums, envelope, keepouts, cutouts vs split). Use at
least 64 segments for functional circular holes in final exports.

## Output contracts

Write files to disk when the user asked for a model; do not paste a long script into
the reply when a file is what they will print. Export one file per part, bed face on
z = 0, following `references/mesh-and-export.md`. Without file tools, use one fenced
block per file.

### Part being designed or cleared to print

```
## Process
<FDM / resin / SLS> on <profile>. <Why this process.>

## Orientation
Bed face: <which face, and why>
Load path: <where tension and bending sit relative to the layers>
Sacrificed face: <none, or the face that may carry support scars>

## Geometry
<Walls, fits, fasteners, and the shapes changed so it prints and holds.>

## Mesh
<When a file was written: one solid, bed on z = 0, and the check_stl.py line. Report the actual Bambu Studio result; investigate any repair prompt or warning there, since the mesh checker is advisory for some edge patterns.>

## Print plan
<Layer height, walls, infill, brim, supports, nozzle, drying, and any pause-at-layer height. Use Bambu Studio setting names and the A1 Mini preset in references/slicer-and-troubleshooting.md unless the user named another slicer. Supports must read "none" unless a face was sacrificed on purpose. X-Y hole compensation is 0 when the model already has hole_comp. Make overhangs printable stays off.>

## Watch-out
<The single most likely failure, and the check that prevents it.>

## Assumptions
<Every value the user did not give.>
```

For a design review, replace Geometry with a punch list ordered as: will not print,
will fail in use, will look bad. Quote the dimension that is wrong and the dimension
to use.

For a failed print, use the diagnosis shape in
`references/slicer-and-troubleshooting.md`: most likely cause, the observation that
confirms it, one fix. Geometry first, then a single slicer change.

For a mesh review, report units, bounding box, and manifold status first, then the
punch list. Say which checks ran with a tool and which were done by reading the model.

### New enclosure design

Deliver in this order:

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
   or a cable leaving the box: power budget, pin map, wiring table, protection,
   harness notes, as in `electronics-and-wiring.md` §9. For a wiring question with no
   box, this section is the whole deliverable.
6. **ASSUMPTIONS** — every value the user did not specify.
7. **SELF-CHECK** — the list below.

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

## Self-check before answering

For every part being designed or cleared:

- No part needs supports; no overhang beyond the profile limit; no support lands on a
  fit, seal, or sliding face.
- The critical load is not peeling layers, or the part was reoriented.
- FDM walls are a whole number of extrusion widths from the profile in force.
- Each fit has a named clearance. Every functional vertical hole carries `hole_comp`
  or a drill note, and not both `hole_comp` and slicer hole compensation.
- Body and lid locate each other with the slip clearance on each mating face. A
  rim-to-rim plate fails this check even when the two solids do not intersect.
- Every part fits the profile's build envelope, or the split and the fasteners are
  specified.
- Profile bans are respected. On house PETG-CF that means no snaps, clips, or living
  hinges unless the user insisted, the profile limits are applied, and the risk is
  stated.
- Any exported file is one part per file, in print orientation, with functional holes
  at `$fn` ≥ 64. Every STL has passed the reported topology, envelope and bed checks;
  sampled island findings have been inspected in the slicer. Self-intersections, wall
  thickness and strength are not certified by the checker.
- The print plan names the Bambu Studio printer, process, and plate presets when that
  is the slicer, and it leaves hole compensation and overhang rewriting off.
- Heat, UV, food, and mains were either handled or marked not applicable. Printed
  plastic is not a certified insulator or a flame barrier unless the spool says so.

For enclosures, additionally state the verdict on each:

(a) every screw has a gusseted, filleted column that avoids the board; (b) every
sensor has a vented, thermally decoupled chamber; (c) antenna keepout respected;
(d) all cutouts referenced to the PCB origin through their board edge, and plugs can
reach their sockets; (e) `assert()` statements present and passing; (f) export
commands match the `part` values; (g) context rules applied (heat/vents, sealing,
batteries, children/pets) or not applicable; (h) when the brief has more than one
module, a battery, a switched load or a cable out: a power budget, a pin map, a
wiring table, a fuse at the source, and a keyed/latched or screwed power connection;
each cable exit has a zip-tie anchor and an anti-chafe hole; (i) the vertical stack
uses the assembled board: bottom soldered-pin envelope, standoffs, PCB, top
header/Dupont envelope, bend radius, and 2 mm closure margin; with the actual harness
installed, a section/check view shows no contact with the lid, seam, columns or
floor — a bare-board height check fails (i); (j) every soldered header is assigned to
its actual PCB face and edge; asymmetric top/bottom and `x0`/`x1`/`y0`/`y1` envelopes
are preserved through `pcb_rot`, and unused sides do not receive invented clearance —
a single symmetric header allowance fails (j).

If a check fails, change the part before replying. Do not ship the failure as a note
or a caveat where geometry was the answer. If the native renderer or slicer was
unavailable, identify the checks that remain unverified. Never infer a mesh or
physical-fit pass from static source checks.

## OpenSCAD compatibility

Target OpenSCAD 2021.01 syntax; it runs unchanged in development snapshots, which
render far faster with the Manifold backend. Avoid experimental features unless the
user runs a snapshot. Docs: https://openscad.org/documentation.html
