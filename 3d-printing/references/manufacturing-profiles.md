# Manufacturing profiles

A profile is the printer + material pair the part will actually be made on. It overrides
the generic numbers in SKILL.md and in `fdm-design-rules.md`. Load the default unless the
user names a different one; the enclosure template's Process group mirrors this table, so
change both together. If the user names another printer or material, copy this structure,
fill the same fields, and recompute every dimension that came from extrusion width. Do
not keep 0.4 mm numbers on a 0.6 mm nozzle.

`references/enclosure-maker-agent.md` carries a verbatim-exportable copy of the
house numbers; keep it in sync when this profile changes.

Contents:
- [Default: Bambu Lab A1 Mini + PETG-CF](#default-bambu-lab-a1-mini--petg-cf)
- [Adding a profile](#adding-a-profile)
- [Calibrating `tol`](#calibrating-tol)
- [Calibration status and source](#calibration-status-and-source)

---

## Default: Bambu Lab A1 Mini + PETG-CF

Do not ask the user to confirm this profile. Use it unless they name another.

**Machine.** Bed-slinger (Y-moving bed), open frame, textured PEI plate.
Build volume 180 × 180 × 180 mm → design envelope **170 × 170 × 170 mm**.
Nozzle 0.4 mm hardened steel, extrusion width `ew = 0.42`, layer height 0.2 mm.

Bambu recommends a 0.6 mm hardened nozzle for this filament to cut clogs. Stay on
0.4 mm for design numbers unless the user says the nozzle changed. If the complaint
is clogging or a worn orifice, suggest 0.6 mm and recompute per
[Adding a profile](#adding-a-profile).

**Material behaviour to design around.** PETG-CF is stiff and dimensionally stable but
brittle and notch-sensitive — far lower elongation at break than unfilled PETG. It is
anisotropic and weakest in tension across layer lines. Bridges and overhangs droop more
than PLA. Holes come out undersized and the first layer spreads. HDT is roughly
75–85 °C, so it is not a high-temperature material. The carbon fill attenuates 2.4 GHz
more than neutral plastics; keep that in mind near antennas.

### Geometry overrides

| Parameter | Value | Why |
|---|---|---|
| `wall` | `6 * ew` = 2.52 mm | 6 perimeters; brittle material needs section, not ribs alone |
| floor / ceiling | 3.0 mm (15 layers at 0.2) | closes the surface and adds bending stiffness |
| max bridge | 5 mm | PETG-CF sags where PLA holds |
| max overhang | 45° from vertical, target 40° | |
| teardrop threshold | horizontal holes ≥ 5 mm | |
| bottom chamfer | 0.8 mm × 45°, every plate-touching edge | elephant foot |
| `hole_comp` | +0.15 mm on diameter | functional holes only, not cosmetic cutouts. Insert bores use the final CAD size selected on the coupon |
| internal fillet | R ≥ 1.0 mm, **everywhere** | a square internal corner is a crack initiator here. Keep the wall thickness through the bend |
| min insert boss OD | 9.5 mm for M3 | ≥ 2.5 mm plastic around a ~4.0–4.2 mm bore |
| gussets per column | 3 minimum, always root-filleted | |
| antenna keepout | 20 mm | CF attenuation |
| `tol` | press 0.15 / slip 0.25 / loose 0.40 | starting values; calibrate and record conditions |
| `lip_w` | 1.0 mm (≥ 2 × `ew`) | tongue that still leaves one extrusion of land beside the groove on a 6-line wall |

Use multiples of `ew` as a house wall target; verify actual slicer paths and overlap.

### No elastic features

Snap fits, cantilever latches, living hinges and flexing tabs are **forbidden**. They
work in PLA and PETG, and they crack on the second open in PETG-CF. All closures are
screwed; all alignment is tongue-and-groove or dowel pins.

If a brief explicitly demands a clip: arm length ≥ 10 × thickness, root fillet ≥ 1.5 mm,
deflection ≤ 1.5% of arm length, and state the fatigue risk in the build notes. For the
general snap-fit method (strain formula, orientation) see the snap-fit section of
`fits-and-fasteners.md`. Prefer switching to unfilled PETG instead of arguing the clip
into this material.

### Load paths

Never let a screw load a single layer plane in tension. The pull-out path runs through
the column body, not through a flat lid flange — that flange is a stack of layer bonds
being peeled apart.

### Envelope and orientation

- Assert every part fits 170 × 170 × 170 mm. If it does not, split it and join with M3
  bolts plus ≥ 2 dowel pins (Ø 4 mm printed pockets, 0.20 mm clearance per side). Never
  specify glue: PETG bonds poorly with cyanoacrylate and has no practical solvent weld.
- Each part needs a flat face covering ≥ 60% of its footprint to print on, support-free.
- Bed-slinger: if a part's height exceeds 2.5 × its smallest footprint dimension,
  reorient it, widen the base, or split it — and call for a brim in the build notes.
- The bottom face takes the plate texture. Never put a gasket seat, a sealing surface or
  fine debossed detail there.

### Operator notes to include in the print plan / BUILD NOTES

- Hardened nozzle is mandatory; carbon fiber abrades brass within a spool, and a worn
  nozzle silently changes every hole.
- Dry the filament before any long print — roughly 65 °C for 8 h in a dryer or
  convection oven. PETG is hygroscopic and the CF load makes it worse; wet filament
  produces brittle layer bonds, which is exactly the failure you do not want in a
  loaded part or a screw column.
- Do not run CF through the AMS Lite — feed from the spool holder to avoid abrading the
  filament path.
- Glue stick on the textured PEI acts as a release agent, not an adhesive. PETG bonds to
  bare smooth PEI hard enough to damage the sheet. The A1 Mini's textured plate is the
  right surface; still mention release if they swap to a smooth plate.
- Keep the part fan modest. Overcooling is a common reason PETG-CF splits between
  layers. Bambu's own note for this filament is that an open-frame printer and a high
  fan both hurt Z strength, so design the load path accordingly instead of expecting
  enclosed-printer layer bonds.
- Slice in Bambu Studio with printer `Bambu Lab A1 mini 0.4 nozzle`, process
  `0.20mm Standard @BBL A1M`, plate `Textured PEI Plate`, and the PETG-CF filament
  preset. The setting list is in `slicer-and-troubleshooting.md`. The generated part is
  intended to be one solid on z = 0. Confirm the exported STL in Studio; the mesh
  checker cannot guarantee that every slicer will accept it without repair.

---

## Adding a profile

When the user names a different printer or material, write a new section with the same
headings and the same override table. The fields that must be filled: build envelope,
`ew`, layer height, wall, max bridge, max overhang, teardrop threshold, `hole_comp`,
minimum internal fillet, insert boss OD, antenna keepout, `tol` triple, `lip_w`, and
whether elastic features are allowed.

Common variations worth knowing:

- **0.6 mm hardened nozzle on the same A1 Mini.** Set `ew = 0.62`, `wall_lines = 4`
  (wall 2.48 mm) and `lip_w = 1.24` (two lines); fewer, fatter perimeters actually
  improve part strength with filled materials and clog less. A centred tongue now needs
  `lip_w + 2·ew + 2·tol` = 2.98 mm of rim, so the enclosure template adds a rim band
  under it by itself. Recompute everything derived from `ew`; do not carry over the
  0.4 mm numbers.
- **Unfilled PETG or PLA on the same printer.** Elastic features become allowed;
  internal fillet can drop to R 0.5 mm; antenna keepout back to 15 mm; 3–4 wall lines
  are normal, and the template's rim band keeps the tongue-and-groove printable on
  them. Bridges can go to about 10 mm before sag matters. PLA's ~55 °C HDT makes it
  unsuitable for anything in a car, a window, or near a regulator or heat source.
- **ASA / ABS.** Enclosed printer only — the A1 Mini is open, so say that this profile
  cannot print them well. Add shrinkage compensation (~0.5–0.8%) to outer dimensions
  and expect warped large flat faces: round corners, add a brim, design with ribs and
  avoid a broad unbroken base.
- **Unknown printer/material.** Use the generic values in `fdm-design-rules.md` and
  the `materials.md` table, and say which numbers are unverified.

## Calibrating `tol`

Print `assets/fit-coupon.scad` once per printer-material pair, with the same walls,
layer height, and filament as the real part. It sets `hole_comp`, `tol` and the insert
bore in one print of about 84 × 57 mm. It has three rows: 3 mm holes that set
`hole_comp` against a drill shank, holes for a printed pin at each per-side clearance
(0.10–0.40 mm), and blind bores for the M3 insert. Read them in that order, because
the clearance row already includes `hole_comp`. The hole that gives the fit you want
by hand sets `tol` for every later part.

For a different printer, nozzle, or insert, edit the parameters at the top of the file
(`hole_comp`, `clearances`, `insert_bores`, `insert_len`, `boss_od`) and keep the
layout; do not redraw it. Feed the numbers into every project and do not change them
per project — this single number is the most common cause of assemblies that worked
last time and do not fit now. A hole that is tight on one part is almost never a
reason to change `tol` globally; check hole compensation and elephant's foot first.

## Calibration status and source

All fit/compensation numbers above are uncalibrated house starting values.
Manufacturer ratings, conservative house targets, and measured printer results
are different things. Label them accordingly. Use the dimension/calibration
reference and store measured results with the project; revalidate after material,
nozzle, orientation or process changes. A positive nominal gap does not guarantee
a press fit, and a perimeter-width calculation does not certify wall strength.

The default remains a 0.4 mm hardened nozzle. Bambu allows it for its PETG-CF and
recommends 0.6 mm to reduce clogging. Use the actual filament vendor's drying,
printing and plate guidance rather than treating all PETG-CF blends as identical.
[Bambu PETG-CF](https://us.store.bambulab.com/collections/bambu-lab-3d-printer-filament/products/petg-cf)

For inserts, 4.1 mm is a starting **final CAD bore**, not the insert OD and not a
universal manufacturer requirement. Do not apply general hole compensation on
it again. Bore geometry and lead-in follow the selected insert's drawing.
