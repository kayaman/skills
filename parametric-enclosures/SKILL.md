---
name: parametric-enclosures
description: Design 3D-printable enclosures for electronics as parametric OpenSCAD and export them to STL. Produces a .scad file, per-part STL export commands, print/build notes and a fastener BOM, following hard rules for ribbed screw columns with heat-set inserts, PCB standoffs and clearances, ventilation, thermally isolated sensor compartments, antenna keepouts and support-free printability. Use this whenever the user mentions an enclosure, case, housing, shell, box or "caixa" for a PCB, board, ESP32/Arduino/Raspberry Pi/STM32 project, sensor node or any electronics device, and also when they ask for OpenSCAD, .scad or STL geometry for such a part, or ask to add ventilation, add a sensor bay, add mounting, or resize an existing enclosure. Trigger it even when the user does not explicitly say "OpenSCAD" or "3D printing" — "I need a case for this board" is enough.
---

# Parametric enclosures for electronics

Enclosures fail in predictable ways: a screw boss cracks off the wall, a temperature
sensor reads the regulator instead of the room, a lid needs supports and comes out
scarred, a Wi-Fi module loses 10 dB because an insert sits next to the antenna. Every
rule here exists to close one of those failure modes. Follow them by default and say so
when a brief forces an exception.

## Workflow

1. **Fill the brief** (below). Do not interrogate the user — extract what the
   conversation already gives you, pick defensible defaults for the rest, and tag each
   one `// ASSUMPTION:` in the code and in the ASSUMPTIONS section of the reply.
2. **Load the manufacturing profile** from `references/manufacturing-profiles.md`.
   The profile overrides numbers in this file — wall thickness, bridge limits, hole
   compensation, envelope. Never design against generic FDM values when a profile exists.
3. **Read the sensor rules** in `references/sensors.md` for every sensor in the brief.
   Getting a BME280 chamber wrong is not recoverable by slicer settings.
4. **Write the .scad** by copying `assets/template.scad` and using the modules in
   `assets/enclosure_lib.scad`. Reuse the library instead of re-deriving bosses, vents
   and rounded boxes — it keeps geometry consistent across the user's whole product line
   and makes project-to-project diffs readable.
5. **Self-check**, then deliver in the output contract below.

## The brief

Ask for nothing that the conversation already answers. Defaults in brackets.

**PCB** — outline X × Y × thickness [1.6 mm], mounting hole Ø and coordinates measured
from the PCB origin at its bottom-left corner, tallest component on top side and on
bottom side, keepout zones (antenna, HV, moving parts).

**Interfaces** — connectors and their position relative to the PCB origin, display,
buttons, LEDs, switches, cable exits.

**Sensors** — type and what each one needs to sense (airflow, field of view, acoustic
port, light path).

**Thermal** — heat sources and rough dissipation [assume < 0.3 W if nothing is said].

**Context** — indoor/outdoor, dust, moisture, and whether children or animals can reach
it. This last one changes the vent rules, so raise it rather than silently assuming.

**Mounting** — desk feet, wall, DIN rail, handheld [desk feet].

**Fasteners** — M3 heat-set inserts [default] or self-tapping screws.

**Limits** — maximum outer dimensions, aesthetic constraints.

If the PCB dimensions are missing, that is the one thing worth asking for. Everything
else can be assumed and corrected later.

## Core rules

### Parametrization

Millimetres throughout. Every input lives in one Customizer block at the top of the
file, grouped with `/* [Group] */`. Below that block there are no magic numbers — only
values derived from parameters. This is what makes a design reusable at a different PCB
size instead of a one-off.

Expose `part = "all" | "base" | "lid" | <extras>`. `"all"` renders an exploded preview
and is never exported. Set `$fa = 1; $fs = $preview ? 0.6 : 0.25;`.

### Printability — supports are a defect, not an option

A part that needs supports has scarred internal surfaces exactly where the fits matter.
Design so every part prints on a flat face with nothing under it.

- Wall thickness is an integer multiple of the extrusion width and at least 3
  perimeters. Floor and ceiling at least as thick as the wall and at least 4 layers.
- No overhang steeper than 45° from vertical. Horizontal holes above the profile's
  teardrop threshold get a teardrop or a 45° chamfered roof. Downward-facing screw
  recesses get a 45° cone.
- Bridges stay under the profile's limit.
- Chamfer every edge that touches the build plate (elephant-foot relief) and every
  visible top edge.
- Nothing solid thicker than ~4 mm — hollow it and rib it. Thick solid regions warp and
  waste time for no strength gain.
- Minimum feature 0.8 mm; minimum free-standing pin Ø 2 mm.

### Structural columns — the single most common failure

Every screw lands in a hollow column that runs floor to mating face, tied into the
shell. Never a thin flange, never a boss floating on a wall. A boss hanging off a wall
is a lever arm with a layer line at its root, and it will snap.

- 2–4 triangular gussets per column, thickness equal to the wall, height 60–80% of the
  column. The gusset's sloped top edge must be at least 45° from horizontal so it prints
  unsupported.
- Fillet the gusset roots and the column-to-floor junction. A sharp internal corner is a
  crack initiator; on stiff filled materials it is the crack initiator.
- Boss OD = hole Ø + 2 × wall, and at least the profile's minimum for M3.
- Heat-set inserts: check the actual insert datasheet. Typical M3 (4.6 × 5.7 mm) wants a
  blind bore of Ø 4.0–4.2 mm, depth = insert length + 1.0 mm relief, with a 0.5–1.0 mm
  lead-in chamfer so the insert starts straight.
- Self-tapping: pilot Ø ≈ 0.8 × major Ø (2.4 mm for M3), engagement ≥ 2 × screw Ø, boss
  wall ≥ 2 mm.
- Mating part gets a clearance hole (3.4 mm for M3) plus counterbore or countersink to
  suit the head.
- At least 4 columns up to a 100 mm span, one more per additional ~70 mm, plus one
  beside any connector that takes insertion force. A USB port pushed 200 times is a
  fatigue test of whatever holds the wall.

### PCB fit

- 0.25 mm lateral clearance per side plus retention ribs. Never press-fit a PCB; FR4
  tolerances and print tolerances do not stack favourably.
- At least 2 mm above the tallest top-side component. Standoffs at least 4 mm so
  through-hole solder tails clear the floor.
- Connector cutouts +0.5 mm all round; +0.75 mm and a 1 mm lead-in chamfer for
  user-facing ports, because a USB plug has to find the hole without looking.
- Dimension every cutout from a single PCB origin, never from the enclosure wall.
  Wall-referenced cutouts drift the moment the wall thickness changes.

### Ventilation

Required whenever a component dissipates more than ~0.3 W or the brief names a heat
source.

- Slots 1.5–2.5 mm wide, ≤ 25 mm long, spaced at least one wall thickness apart — the
  webs between slots are structure.
- Vertical wall slots print unsupported. On horizontal faces use short bridged slots or
  a hex grid with a vertex pointing up.
- Build a chimney: inlets in the lowest 25% of one wall, outlets in the top 25% of the
  opposite wall or the lid, so the path crosses the heat source instead of short-
  circuiting.
- Open area ≥ 25% of the vented wall above 1 W.
- If children or animals can reach the device, no opening exceeds 4 mm in any direction
  and no opening sits directly above the PCB — use offset louvres so there is no
  straight line from outside to electronics.

### Sensor compartments

Read `references/sensors.md` for the per-sensor geometry. Universally:

- Every environmental sensor gets its own chamber, separated from the main cavity by a
  full-height internal wall, with its own vents.
- Thermal decoupling from any heat source: ≥ 15 mm, plus either a ≥ 3 mm air gap or a
  slot through the divider, so the divider itself is not a heat bridge.
- No dead air pockets — a chamber vented only at the top measures its own microclimate.
- Every chamber must be serviceable without desoldering.

### RF

No conductive material, no heat-set insert, no column and no rib inside the profile's
antenna keepout radius of a PCB or chip antenna. Keep the antenna over open plastic near
an enclosure edge, with minimum plastic thickness in front of it. Filled materials
attenuate 2.4 GHz noticeably — say so in the build notes and recommend an RSSI check
before freezing the design.

### Electrical

Do not treat printed plastic as a qualified insulator, especially filled grades. Keep
≥ 3 mm creepage from any mains or high-voltage net to the enclosure wall, and never rest
a bare conductor against a printed surface.

### Assembly and serviceability

- Lid-to-base tongue and groove: tongue ~1.2 mm wide × 2 mm tall, groove = tongue + the
  fit tolerance. It aligns the halves and blocks light and dust.
- One `tol` parameter drives a fit table: press / slip / loose. Calibrate it once per
  printer-material pair and keep it.
- Screws enter from the least visible face; hide the parting seam on a chamfer.
- Rubber foot recesses (Ø 8 × 1 mm) or keyhole slots (Ø 7 / 3.5 mm) for wall mounting.
- Strain relief on every cable exit: a zip-tie anchor or a two-screw clamp. The solder
  joint is not the strain relief.
- Deboss part name and version 0.4 mm deep, ≥ 3 mm tall, on an internal face. Future-you
  will be holding three similar lids.

## Self-check before answering

State the verdict on each: (a) no part needs supports; (b) no overhang beyond 45°;
(c) every screw has a gusseted, filleted column; (d) every sensor has a vented,
thermally decoupled chamber; (e) antenna keepout respected; (f) all cutouts referenced
to the PCB origin; (g) `assert()` statements present; (h) export commands match the
`part` values; (i) every part fits the profile's build envelope.

If any check fails, fix the design before replying. Do not ship a caveat where geometry
was the answer.

## Output contract

Deliver exactly this, in this order:

1. `<product>_enclosure.scad` — parametric, using `enclosure_lib.scad`.
2. `enclosure_lib.scad` alongside it, if the user does not have it yet.
3. One CLI export line per part:
   `openscad -D 'part="base"' -o base.stl <product>_enclosure.scad`
4. **BUILD NOTES** — per part: print orientation and why, brim yes/no, bounding box vs
   the build envelope; plus layer height, material, supports (must read "none"), and a
   fastener BOM with quantities and lengths.
5. **ASSUMPTIONS** — every value the user did not specify.
6. **SELF-CHECK** — the list above.

Write the files to disk and present them. Do not paste a long .scad into chat prose when
a file is what the user prints from.

## Reference files

- `references/manufacturing-profiles.md` — printer and material profiles. Read this
  before writing any geometry; it overrides the numbers above. Contains the default
  profile and a template for adding new ones.
- `references/sensors.md` — per-sensor chamber, aperture and port geometry.
- `references/openscad-conventions.md` — file layout, assertion patterns, export, and
  the mistakes that produce non-manifold STLs.
- `assets/enclosure_lib.scad` — reusable modules (rounded boxes, gusseted bosses,
  standoffs, vents, fillets, tongue-and-groove, keyholes).
- `assets/template.scad` — project skeleton. Copy and fill.
- `assets/selftest.scad` — renders every library module. Run it once after any library
  change to catch geometry errors before they reach a product file.
