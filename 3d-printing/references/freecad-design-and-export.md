# FreeCAD projects (MCP connection)

Read this for an existing `.FCStd` project, or whenever the user asks for FreeCAD,
STEP, the FreeCAD MCP connection, or mechanical-CAD interchange — this is a full
third backend, usable for new designs too, not only "preserve an existing file."
Preserve an existing project's object names, document structure and parameter
values. New designs build from `assets/enclosure_lib.py` and
`assets/enclosure_template.py`, the FreeCAD analogs of `enclosure_lib.scad` and
`template.scad`. This skill operates FreeCAD through a live MCP connection, not a
CLI — there is no `openscad -D` equivalent. "Exporting a part" means running a
Python code block through `execute_code`, and there are three distinct execution
surfaces with different safety rules (next section).

## Numeric controls and parametrization

Keep every tunable in one top-level `PARAMS` dict in `enclosure_template.py`,
grouped with comment headers matching the SCAD Customizer group names (Process,
PCB, Cutouts, Wiring, Fasteners, Shell, Lip, Ventilation, Sensor chamber,
Mounting, Safety). Derive dependent dimensions in code immediately below it,
the same relationship the SCAD template expresses with `/* [Hidden] */`.

A FreeCAD `Spreadsheet` object with expression-bound properties is the closer
GUI analog of the Customizer, and is deliberately **not** used here: the real
interaction loop for this backend is "the agent edits Python text and re-runs it
through MCP," not "the user drags a slider." The ceremony of cell aliases and
expression bindings on every dependent object buys nothing in that loop. If the
user wants resolved dimensions visible in the GUI for inspection, mirror them
into a `Spreadsheet` after the fact — it is never the source of truth.

Millimetres throughout. Never move a derived dimension (a lid hole) independently
of the input it derives from (the boss OD) — same rule as the OpenSCAD and Rhai
docs. Use `references/dimensions-and-calibration.md` for the nominal / per-side
clearance / diameter compensation / final-CAD-dimension labeling discipline.

## Coordinate frame and the three execution surfaces

One coordinate frame: origin at the outer bottom-left-front corner of the base,
+Z up — the same convention as OpenSCAD, so the user's mental model transfers
directly. `face_frame(face, outer)` in `enclosure_lib.py` returns a
`FreeCAD.Matrix` (not a `Placement` — five of the six faces need a reflection to
get both the depth direction and the documented u/v axes right, and
`Placement` only accepts proper rotations) for one of the box's six faces, the
direct analog of the SCAD `multmatrix` table; apply it with
`shape.transformShape(matrix, True)`, never by assigning to `.Placement`.
Convert board-local positions once through a `to_world()` function, same as
the template's.

This backend exposes three different ways to run Python in FreeCAD. Picking the
wrong one risks a crashed or wedged session, not just a slow one.

- **`execute_code`** (runs on FreeCAD's GUI thread) — the default. Use it for
  almost everything: building and editing geometry, booleans on a handful of
  primitives, `doc.recompute()`, saving, screenshots. Stay inside the ~90 s
  default budget per call; raise `timeout` for one known-slow step rather than
  looping calls. Pass `include_screenshot=False` on intermediate, non-visual
  steps (parameter edits, property pokes) to save tokens; request a screenshot
  at milestones.
- **`execute_code_async`** (background thread) — only for CPU-heavy pure-geometry
  computation on shapes already fetched into Python variables (a costly
  multi-body fuse/cut/loft). Never call `doc.recompute()`, edit a property, or
  save from inside it directly — route any such mutation through the injected
  `commit(fn, timeout=120)` helper, which queues it onto the GUI thread. A direct
  document write from this thread can wedge FreeCAD's event loop; treat that as a
  bug, not a shortcut.
- **`execute_code_headless`** (separate `freecadcmd` process, no GUI) — for
  operations that can crash or block FreeCAD outright: helical threads
  (`makeHelix` + `makePipeShell`), lofts/sweeps over many sections, booleans with
  large face counts, long parametric rebuilds. Fresh namespace — it does **not**
  share state with `execute_code`'s session. It must open/save its own document
  from disk (`FreeCAD.openDocument(path)`, `doc.save()`/`saveAs()`, or export a
  bare `Shape` via `.exportBrep()`/STEP without even a document). After it edits
  a `.FCStd` also open in the live GUI session, call `reload_document(doc_name)`
  before the next `execute_code` call touches that document.

Library loading pattern: read `assets/enclosure_lib.py`'s text and send it as the
`code` argument to one `execute_code` call early in the session
(`include_screenshot=False`); later `execute_code` calls in that session can call
its functions because the namespace persists. `execute_code_headless` has no such
persistence — every headless call must `exec(open(LIB_PATH).read())` itself at
the top, where `LIB_PATH` is the library's absolute path on the machine running
FreeCAD. Never retype the library inline from memory; load the real file so a
library fix propagates everywhere.

If a previous `execute_code` call seems hung, call `get_rpc_status()` first — it
bypasses the GUI thread and answers even when a GUI op is wedged — before
retrying or asking the user to restart FreeCAD.

## Assembly, orientation and export

Build named `Part::Feature` objects per printable part (`Base`, `Lid`, ...), each
committed from a single composed `Part.Shape` (fuse/cut happens in Python on raw
shapes before the one `doc.addObject` call — keeps the document tree small and
avoids a GUI-thread recompute storm). A `set_view(doc, mode)` helper toggles
`Visibility`/`Placement` for `assembly | exploded | base | lid | section | check`
— the FreeCAD equivalent of the SCAD `part` switch, since there's no `-D`
override.

Printable geometry is defined in its print orientation, bed face at `Z = 0`,
exactly like the template; assembly/exploded/section are preview-only
compositions, never exported as parts — the same rule the Rhai doc states for
`view(...)`.

Export calls:

```python
import Part, Mesh
Part.export([doc.getObject("Base")], "/abs/out/base.step")   # STEP (AP214) — mechanical interchange
Mesh.export([doc.getObject("Base")], "/abs/out/base.stl")    # STL — check tessellation on small features (bosses/gussets) before calling it done
Mesh.export([doc.getObject("Base")], "/abs/out/base.3mf")    # 3MF carries objects/units, not process settings — same caveat as the Rhai doc
```

"Clean render" equivalent (there is no `Simple: yes/no` line in FreeCAD): after
every boolean, check `shape.isValid()`, `not shape.isNull()`, and
`shape.Volume > 0` and finite. A `Volume == 0` or negative solid is the FreeCAD
analog of OpenSCAD's "Current top level object is empty." A `doc.recompute()`
error state on any object is a hard failure, the same posture as
`--hardwarnings`.

Interference/fit check, the real equivalent of `part="check"`:
`inter = Base.Shape.common(Lid.Shape)`; pass condition is
`inter.isNull() or inter.Volume < 1e-3` — BRep booleans rarely return an
exactly-null shape the way OpenSCAD's CGAL kernel does, so state the epsilon
explicitly rather than asserting exact zero. Extend the same `.common()` +
volume pattern to other pairs (board keepout vs. standoffs, connector cutout vs.
wall) per `verification-and-export.md` §3's generic rule.

Visual delivery: a screenshot from `execute_code`'s own return
(`include_screenshot=True`) or an explicit `get_view(doc_name, view_name=...)`
call. There is no PNG file the way `export_parts.sh` writes one; the screenshot
*is* the delivered visual. Request a section-cut view for lip/boss fit checks,
mirroring `verification-and-export.md` §4's checklist.

Fasteners: use `get_parts_list()` / `insert_part_from_library(...)` for real
hardware (M3 heat-set inserts, etc.) the same way the SCAD docs point at actual
insert drawings instead of inventing dimensions.

Never claim an export, `isValid()`/`Volume` check, interference check, or
screenshot happened unless the corresponding tool call was actually made and
returned success. If the MCP connection is unavailable this session, say so and
describe the code the user would run, or default to OpenSCAD if nothing already
commits the user to FreeCAD. Do not broaden tool permissions to force a check
through; use `get_rpc_status()` before declaring a session stuck.

## Deliverable

The saved `.FCStd` (`doc.save()` if it already has a path, else
`doc.saveAs(path)`), any new or changed `enclosure_lib.py`/`enclosure_template.py`
content if a primitive had to change, the resolved critical dimensions (boss OD,
bore, radial wall, gusset reach — the same fields `dimensions-and-calibration.md`
asks for), the STEP/STL(/3MF) paths actually written, the screenshot/`get_view`
evidence, and assumptions. For a small iteration, report only the changed
parameters and affected checks, the same economy rule as the Rhai doc.
