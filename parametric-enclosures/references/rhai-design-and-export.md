# enclosure-maker Rhai projects

Read this for an existing `.rhai` project or an enclosure-maker request. Preserve
its native source, imports, parameter names and emitted part names. Use the host's
current scripting API reference as the authority; do not invent OpenSCAD bindings.
`assets/linked-boss.rhai` is an executable dimension-linkage example, not a complete
load-validated enclosure. It exposes bore, length, wall, height, gussets and XY
position, derives OD, and rejects insufficient blind-floor thickness. Its ribs
have sharp junctions: a loaded enclosure still needs root treatment compatible
with the native API and load case; do not claim that this example supplies fillets.

## Numeric controls and frames

Use `param("Label", default, min, max)` with float dimensions for meaningful UI
inputs. Calculate related dimensions from those inputs, including bosses and
mating holes. Never replace a derived relationship with independent literals just
to expose another control. Read imported helpers before editing them. Use explicit
units and distinguish target dimensions from process compensation as described in
`dimensions-and-calibration.md`.

Rhai cuboids are centred; cylinders start at z=0. Preserve the project's coordinate
frame, convert PCB-local positions once, and explain movement relative to that
frame. Use numeric `if ... { throw "message"; }` constraints supported by Rhai.
Do not emit an invalid model merely because its input falls within a slider range.

Built-in hardware helpers may fix insert bore/length and curve segments. When
those do not match the required hardware, compose named project-local functions
from documented `cylinder`, `cone`, `cuboid` and CSG operations. Expose final CAD
bore and relief explicitly; do not claim `heat_set_bore` accepts custom dimensions.
Use integer segment counts of at least 64 for functional circles in final exports;
keep hexagonal nut pockets hexagonal. Inspect generated meshes even when evaluation
succeeds. `shell()` is an approximation on complex shapes, not a constant-thickness
operation; inspect critical wall dimensions in sections.

## Assembly, orientation and export

`emit("base", base)` and `emit("lid", lid)` declare printable parts.
`view("assembly", ...)`, `view("exploded", ...)` and `view("section", ...)`
are preview-only compositions. Define printable geometry in its print orientation
with bed face z=0, and build assembly views from copies in assembled positions.

The app may save manual part transforms in
`.enclosure-maker/<script filename>.transforms.json`. Read them when considering
placement, keep part names stable, and do not edit the metadata or duplicate its
transforms in code. They also affect exports: verify the actual final bed placement
and dimensions, including rotation and translation. A raw script section view does
not automatically include saved transforms.

When the CLI is available, its existing commands are:

```sh
enclosure-maker export --script main.rhai --part boss --output boss.stl
enclosure-maker export --script main.rhai --part boss --param 'Insert CAD bore diameter=5.0' --output boss-5mm.stl
enclosure-maker export --script main.rhai --parts base,lid --output enclosure.3mf
```

Use actual emitted names. From an enclosure-maker source checkout, prefix commands
with `cargo run -p em-preview --offline --`. Do not export assembly/section views
as printable parts. Verify STL with the 3d-printing skill checker and inspect slicer
layers. A 3MF export carries objects/units, not necessarily process settings.

When the host restricts tools to reading/editing files, edit the native source and
let its live preview evaluate it. Do not claim to have run the CLI, mesh checker,
slicer or a physical fit test. Report those checks as unverified and provide the
concrete export/check steps when useful. Do not broaden tool permissions.

## Deliverable

Deliver the updated `.rhai` source and any required project-local `.rhai` helpers,
critical dimension relationships, assumptions/calibration status, named part export
commands, print orientations and checks actually performed. Preserve project intent;
for a small iteration, report the changed dimensions and affected checks only.
