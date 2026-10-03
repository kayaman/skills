#!/usr/bin/env python3
"""Inspect STL topology and sample layers for possible unsupported islands.

Exit 1 for measured errors, 2 for invalid arguments; warnings need slicer review.
This is not a self-intersection, minimum-wall, bridge-span or strength validator.
STL has no units: coordinates are interpreted as millimetres.
"""

import argparse
import math
import struct
import sys
from collections import defaultdict


LAYER_H = 0.2
GRID = 0.4
WELD = 1e-4
BED = 0.05


def load_stl(path):
    with open(path, "rb") as stream:
        data = stream.read()
    if len(data) >= 84:
        count = struct.unpack_from("<I", data, 80)[0]
        if 84 + count * 50 == len(data):
            tris = []
            for off in range(84, len(data), 50):
                nums = struct.unpack_from("<12fH", data, off)
                tris.append((nums[3:6], nums[6:9], nums[9:12]))
            return finite_triangles(tris)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as err:
        raise ValueError("malformed or truncated binary STL") from err
    tris, verts = [], None
    opened = closed = False
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        word = parts[0]
        if word == "solid" and not opened:
            opened = True
        elif word == "facet" and opened and not closed and verts is None:
            verts = []
        elif word == "vertex" and verts is not None and len(parts) == 4:
            verts.append(tuple(float(p) for p in parts[1:]))
        elif word == "endfacet" and verts is not None and len(verts) == 3:
            tris.append(tuple(verts))
            verts = None
        elif word == "endsolid" and opened and verts is None:
            closed = True
        elif word not in ("outer", "endloop"):
            raise ValueError("malformed ASCII STL")
    if not opened or not closed or verts is not None:
        raise ValueError("incomplete ASCII STL")
    return finite_triangles(tris)


def finite_triangles(tris):
    if any(not math.isfinite(c) for tri in tris for p in tri for c in p):
        raise ValueError("non-finite vertex coordinates")
    return tris


def weld(tris):
    index = {}
    verts = []
    faces = []

    def vid(p):
        key = tuple(int(round(c / WELD)) for c in p)
        if key not in index:
            index[key] = len(verts)
            verts.append(p)
        return index[key]

    for a, b, c in tris:
        faces.append((vid(a), vid(b), vid(c)))
    return verts, faces


def area2(verts, face):
    ax, ay, az = verts[face[0]]
    bx, by, bz = verts[face[1]]
    cx, cy, cz = verts[face[2]]
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    cross = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
    return cross[0] * cross[0] + cross[1] * cross[1] + cross[2] * cross[2]


def signed_volume(verts, faces):
    volume = 0.0
    for i, j, k in faces:
        ax, ay, az = verts[i]
        bx, by, bz = verts[j]
        cx, cy, cz = verts[k]
        volume += ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx)
    return volume / 6.0


def components(faces):
    edge_faces = defaultdict(list)
    for fi, (a, b, c) in enumerate(faces):
        for u, v in ((a, b), (b, c), (c, a)):
            edge_faces[(u, v) if u < v else (v, u)].append(fi)
    parent = list(range(len(faces)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    open_edges = 0
    nonmanifold = 0
    inconsistent = 0
    for (u, v), users in edge_faces.items():
        if len(users) == 1:
            open_edges += 1
        elif len(users) > 2:
            nonmanifold += 1
        else:
            union(users[0], users[1])
            fa = faces[users[0]]
            fb = faces[users[1]]
            a_dir = _directed(fa, u, v)
            b_dir = _directed(fb, u, v)
            if a_dir == b_dir:
                inconsistent += 1
    groups = defaultdict(list)
    for fi in range(len(faces)):
        groups[find(fi)].append(fi)
    return open_edges, nonmanifold, inconsistent, list(groups.values())


def _directed(face, u, v):
    a, b, c = face
    cycle = ((a, b), (b, c), (c, a))
    if (u, v) in cycle:
        return 1
    if (v, u) in cycle:
        return -1
    return 0


def ray_hits(origin, verts, faces):
    ox, oy, oz = origin
    dx, dy, dz = 1.0, 0.013, 0.017
    hits = 0
    for i, j, k in faces:
        ax, ay, az = verts[i]
        bx, by, bz = verts[j]
        cx, cy, cz = verts[k]
        abx, aby, abz = bx - ax, by - ay, bz - az
        acx, acy, acz = cx - ax, cy - ay, cz - az
        px, py, pz = dy * acz - dz * acy, dz * acx - dx * acz, dx * acy - dy * acx
        det = abx * px + aby * py + abz * pz
        if abs(det) < 1e-12:
            continue
        inv = 1.0 / det
        tx, ty, tz = ox - ax, oy - ay, oz - az
        u = (tx * px + ty * py + tz * pz) * inv
        if u < 0.0 or u > 1.0:
            continue
        qx, qy, qz = ty * abz - tz * aby, tz * abx - tx * abz, tx * aby - ty * abx
        v = (dx * qx + dy * qy + dz * qz) * inv
        if v < 0.0 or u + v > 1.0:
            continue
        t = (acx * qx + acy * qy + acz * qz) * inv
        if t > 1e-8:
            hits += 1
    return hits


def centroid(verts, face):
    xs = [verts[i][0] for i in face]
    ys = [verts[i][1] for i in face]
    zs = [verts[i][2] for i in face]
    return (sum(xs) / 3.0, sum(ys) / 3.0, sum(zs) / 3.0)


def classify_shells(verts, faces, groups):
    shells = []
    for group in groups:
        shell_faces = [faces[i] for i in group]
        shells.append((signed_volume(verts, shell_faces), shell_faces))
    shells.sort(key=lambda item: abs(item[0]), reverse=True)
    body_faces = shells[0][1]
    body_sign = 1.0 if shells[0][0] >= 0 else -1.0
    extra = []
    cavities = 0
    for volume, shell_faces in shells[1:]:
        point = centroid(verts, shell_faces[0])
        inside = ray_hits(point, verts, body_faces) % 2 == 1
        if inside and volume * body_sign < 0:
            cavities += 1
        else:
            extra.append(point)
    return cavities, extra


def plane_segments(verts, faces, z):
    segments = []
    for a, b, c in faces:
        pts = []
        for u, v in ((a, b), (b, c), (c, a)):
            z0 = verts[u][2]
            z1 = verts[v][2]
            lo, hi = (z0, z1) if z0 <= z1 else (z1, z0)
            if lo < z <= hi and z0 != z1:
                t = (z - z0) / (z1 - z0)
                p0 = verts[u]
                p1 = verts[v]
                pts.append((p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1])))
        if len(pts) >= 2:
            segments.append((pts[0], pts[1]))
    return segments


def filled_cells(segments, grid=GRID):
    rows = defaultdict(list)
    for (x0, y0), (x1, y1) in segments:
        if y0 == y1:
            continue
        y_lo, y_hi = (y0, y1) if y0 < y1 else (y1, y0)
        j0 = math.floor(y_lo / grid)
        j1 = math.floor(y_hi / grid)
        for j in range(j0, j1 + 1):
            y = (j + 0.5) * grid
            if y_lo < y <= y_hi:
                t = (y - y0) / (y1 - y0)
                rows[j].append(x0 + t * (x1 - x0))
    cells = set()
    for j, xs in rows.items():
        xs.sort()
        for left, right in zip(xs[0::2], xs[1::2]):
            i0 = math.floor(left / grid)
            i1 = math.floor(right / grid)
            for i in range(i0, i1 + 1):
                cells.add((i, j))
    return cells


def dilate(cells):
    out = set(cells)
    for x, y in cells:
        out.add((x + 1, y))
        out.add((x - 1, y))
        out.add((x, y + 1))
        out.add((x, y - 1))
    return out


def floating_islands(verts, faces, layer_height=LAYER_H, grid=GRID):
    zs = [p[2] for p in verts]
    if not zs:
        return ["empty mesh"]
    z0 = min(zs)
    z1 = max(zs)
    previous = set()
    islands = []
    z = z0 + layer_height * 0.5
    steps = 0
    first = True
    while z < z1 and steps < 4000:
        steps += 1
        cells = filled_cells(plane_segments(verts, faces, z), grid)
        if cells and not first:
            seen = set()
            supported = dilate(previous)
            for start in cells:
                if start in seen:
                    continue
                stack = [start]
                seen.add(start)
                touches = False
                while stack:
                    current = stack.pop()
                    if current in supported:
                        touches = True
                    x, y = current
                    for nxt in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if nxt in cells and nxt not in seen:
                            seen.add(nxt)
                            stack.append(nxt)
                if not touches:
                    islands.append(round(z - z0, 3))
                    if len(islands) >= 8:
                        return islands
        previous = cells
        first = False
        z += layer_height
    return islands


def bounds(verts):
    xs = [p[0] for p in verts]
    ys = [p[1] for p in verts]
    zs = [p[2] for p in verts]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def check(path, *, layer_height=LAYER_H, grid=GRID, envelope=None,
          require_bed=False, bed_tolerance=BED, strict_topology=False):
    result = {"errors": [], "warnings": [], "size": None, "triangles": 0,
              "lowest_z": None, "cavities": 0}
    errors, warnings = result["errors"], result["warnings"]
    try:
        raw = load_stl(path)
        if not raw:
            raise ValueError("no triangles")
        verts, faces = weld(raw)
    except (OSError, ValueError, OverflowError, struct.error) as err:
        errors.append(str(err))
        return result
    valid_faces = [face for face in faces if len(set(face)) == 3 and area2(verts, face) >= 1e-24]
    if len(valid_faces) != len(faces):
        warnings.append(f"degenerate facets removed for inspection: {len(faces) - len(valid_faces)}")
    faces = valid_faces
    if not faces:
        errors.append("no non-degenerate triangles")
        return result
    x0, y0, z0, x1, y1, z1 = bounds(verts)
    size = (x1-x0, y1-y0, z1-z0)
    result.update(size=size, triangles=len(faces), lowest_z=z0)
    if envelope and any(s > e + WELD for s, e in zip(size, envelope)):
        errors.append("part exceeds the specified envelope in this orientation")
    if abs(z0) > bed_tolerance:
        message = f"lowest z={z0:.3f} mm; print orientation must place the bed face at z=0"
        (errors if require_bed else warnings).append(message)
    open_edges, nonmanifold, inconsistent, groups = components(faces)
    if open_edges:
        target = errors if strict_topology else warnings
        target.append(f"open facet-edge references: {open_edges}; may include unmatched triangulation/T-junctions; inspect the mesh in the target slicer")
    for label, count in (("non-manifold edges", nonmanifold), ("inconsistent winding", inconsistent)):
        if count:
            errors.append(f"{label}: {count}")
    if not open_edges and not errors:
        cavities, extra = classify_shells(verts, faces, groups)
        result["cavities"] = cavities
        if extra:
            errors.append(f"extra solids: {len(extra)}; export intended parts separately")
        outer = max(groups, key=lambda group: abs(signed_volume(verts, [faces[i] for i in group])))
        if signed_volume(verts, [faces[i] for i in outer]) <= 0:
            errors.append("outer shell has inward winding or zero volume")
    # Sample only meshes whose topology is sound. Sampling cannot certify
    # support, bridges or thin walls, and must never be described as doing so.
    if not errors:
        if size[2] / layer_height > 4000 or (size[0] / grid) * (size[1] / grid) > 1_000_000:
            warnings.append("layer sampling skipped: sampling budget exceeded; inspect in slicer")
        else:
            islands = floating_islands(verts, faces, layer_height, grid)
            if islands:
                shown = ", ".join(str(z) for z in islands)
                warnings.append(f"suspected unsupported islands at {shown} mm above lowest point; confirm in slicer")
    return result


def positive(value):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError("must be a finite positive number")
    return value


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    parser.add_argument("--layer-height", type=positive, default=LAYER_H)
    parser.add_argument("--grid", type=positive, default=GRID, help="XY sampling spacing in mm")
    parser.add_argument("--envelope", type=positive, nargs=3, metavar=("X", "Y", "Z"))
    parser.add_argument("--require-bed", action="store_true")
    parser.add_argument("--strict-topology", action="store_true",
                        help="treat open triangle-edge references as errors (may reject CSG T-junctions)")
    parser.add_argument("--bed-tolerance", type=positive, default=BED)
    args = parser.parse_args(argv[1:])
    failed = False
    for path in args.files:
        result = check(path, layer_height=args.layer_height, grid=args.grid,
                       envelope=args.envelope, require_bed=args.require_bed,
                       bed_tolerance=args.bed_tolerance, strict_topology=args.strict_topology)
        status = "FAIL" if result["errors"] else "WARN" if result["warnings"] else "ok"
        print(f"{status} {path}")
        if result["size"]:
            size = " x ".join(f"{v:.3f}" for v in result["size"])
            print(f"  size {size} mm, triangles {result['triangles']}, lowest z={result['lowest_z']:.3f}")
        for severity in ("errors", "warnings"):
            for message in result[severity]:
                print(f"  {severity[:-1]}: {message}")
        print("  Scope: topology after 0.0001 mm vertex quantization; unmatched facet-edge references are advisory unless --strict-topology is set; sampled layers only.")
        print("  Not checked: self-intersections, minimum wall thickness, bridge span, strength; confirm slicer layers.")
        failed |= bool(result["errors"])
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
