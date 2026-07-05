"""Generate a watertight STL of the Vyoma prototype for CFD (SimScale).

Geometry (metres, full scale):
- Ring: superellipse p=4 trace, span b=36 (a=18), height h=18 (h/b=0.5),
  NACA 0012 section (closed trailing edge), chord 3.6 m (c/b=0.1),
  stagger: upper arc aft / lower arc forward, +-4.5 m about mid-height.
- Cabin: lifting-body loft, 20 m long x 18 m wide x 3.5 m tall, centred
  low in the ring (z = 2.7 m = 0.15 h).  Left as a separate closed shell
  with a small clearance to the ring for robust meshing (pylons omitted
  at this fidelity).

Axes: x = downstream (flow direction), y = span, z = up.
Output: vyoma.stl (binary), plus vyoma_ring_only.stl
"""

import struct

import numpy as np

A = 18.0          # semispan
C = 9.0           # semiheight (h/b = 0.5)
CHORD = 3.6
STAGGER = 4.5     # x-offset amplitude, +-
THICK = 0.12      # NACA 0012
N_LOOP = 240
N_SECT = 120      # points around one airfoil section (even)

CAB_LEN, CAB_W, CAB_H = 20.0, 18.0, 3.5
CAB_X0, CAB_Z0 = 2.0, 2.7      # centre of cabin (x aft of ring origin, z)
N_CAB_X, N_CAB_PHI = 60, 80


def naca_thickness(xc, t=THICK):
    """Half-thickness of a closed-TE NACA 00xx section, per unit chord."""
    return 5.0 * t * (0.2969 * np.sqrt(xc) - 0.1260 * xc
                      - 0.3516 * xc ** 2 + 0.2843 * xc ** 3
                      - 0.1036 * xc ** 4)


def ring_grid():
    """(N_LOOP, N_SECT, 3) vertex grid, both indices periodic."""
    th = np.linspace(0.0, 2.0 * np.pi, N_LOOP, endpoint=False)
    ct, st = np.cos(th), np.sin(th)
    y = A * np.sign(ct) * np.abs(ct) ** 0.5
    z = C * (1.0 + np.sign(st) * np.abs(st) ** 0.5)
    x_off = STAGGER * (z - C) / C

    # loop tangent -> section normal (in y-z), matching the paper solvers
    dy = np.gradient(y, edge_order=2)
    dz = np.gradient(z, edge_order=2)
    norm = np.hypot(dy, dz)
    ny, nz = -dz / norm, dy / norm

    phi = 2.0 * np.pi * np.arange(N_SECT) / N_SECT
    xc = 0.5 * (1.0 + np.cos(phi))          # 1 at TE -> 0 at LE -> 1
    half = naca_thickness(np.clip(xc, 0.0, 1.0))
    side = np.where(phi < np.pi, 1.0, -1.0)  # upper then lower surface
    yn = side * half

    grid = np.empty((N_LOOP, N_SECT, 3))
    for i in range(N_LOOP):
        xs = x_off[i] + CHORD * (xc - 0.25)
        grid[i, :, 0] = xs
        grid[i, :, 1] = y[i] + CHORD * yn * ny[i]
        grid[i, :, 2] = z[i] + CHORD * yn * nz[i]
    return grid


def cabin_shells():
    """Closed lifting-body loft with pole caps.  Returns (verts, tris)."""
    xi = np.linspace(-1.0, 1.0, N_CAB_X)
    f = (1.0 - xi ** 2) ** 0.7
    phi = 2.0 * np.pi * np.arange(N_CAB_PHI) / N_CAB_PHI

    verts, rows = [], []
    for k in range(N_CAB_X):
        w, h = 0.5 * CAB_W * f[k], 0.5 * CAB_H * f[k]
        row = []
        for p in phi:
            row.append(len(verts))
            verts.append((CAB_X0 + 0.5 * CAB_LEN * xi[k],
                          w * np.cos(p), CAB_Z0 + h * np.sin(p)))
        rows.append(row)
    nose = len(verts)
    verts.append((CAB_X0 - 0.5 * CAB_LEN, 0.0, CAB_Z0))
    tail = len(verts)
    verts.append((CAB_X0 + 0.5 * CAB_LEN, 0.0, CAB_Z0))

    tris = []
    for k in range(N_CAB_X - 1):
        for j in range(N_CAB_PHI):
            j2 = (j + 1) % N_CAB_PHI
            a, b = rows[k][j], rows[k][j2]
            cc, d = rows[k + 1][j], rows[k + 1][j2]
            if f[k] > 1e-9:
                tris.append((a, b, d))
            if f[k + 1] > 1e-9:
                tris.append((a, d, cc))
    for j in range(N_CAB_PHI):                      # end caps
        j2 = (j + 1) % N_CAB_PHI
        tris.append((nose, rows[0][j2], rows[0][j]))
        tris.append((tail, rows[-1][j], rows[-1][j2]))
    return np.array(verts), tris


def torus_triangles(grid):
    """Triangulate a doubly-periodic vertex grid."""
    n, m, _ = grid.shape
    verts = grid.reshape(-1, 3)
    tris = []
    for i in range(n):
        i2 = (i + 1) % n
        for j in range(m):
            j2 = (j + 1) % m
            a, b = i * m + j, i * m + j2
            cc, d = i2 * m + j, i2 * m + j2
            tris.append((a, b, d))
            tris.append((a, d, cc))
    return verts, tris


def signed_volume(verts, tris):
    v = verts[np.array(tris)]
    return np.einsum("ij,ij->i", v[:, 0],
                     np.cross(v[:, 1], v[:, 2])).sum() / 6.0


def orient_outward(verts, tris):
    if signed_volume(verts, tris) < 0.0:
        tris = [(a, c, b) for (a, b, c) in tris]
    return tris


def write_stl(path, shells):
    """shells: list of (verts, tris).  Binary STL.  Zero-area triangles
    (pole-cap degenerates) are dropped -- strict meshers reject them."""
    payload = []
    for verts, tris in shells:
        v = verts[np.array(tris)]
        nrm = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
        ln = np.linalg.norm(nrm, axis=1)
        good = ln > 1e-10
        with np.errstate(invalid="ignore"):
            unit = nrm / ln[:, None]
        payload.append((v[good], unit[good]))
    total = sum(len(v) for v, _ in payload)
    with open(path, "wb") as f:
        f.write(b"Vyoma ring-wing prototype".ljust(80, b"\0"))
        f.write(struct.pack("<I", total))
        for v, unit in payload:
            for k in range(len(v)):
                f.write(struct.pack("<3f", *unit[k]))
                for p in range(3):
                    f.write(struct.pack("<3f", *v[k, p]))
                f.write(struct.pack("<H", 0))
    return total


def main():
    rv, rt = torus_triangles(ring_grid())
    rt = orient_outward(rv, rt)
    cv, ct = cabin_shells()
    ct = orient_outward(cv, ct)

    write_stl("vyoma_ring_only.stl", [(rv, rt)])
    write_stl("vyoma.stl", [(rv, rt), (cv, ct)])

    vol_r = signed_volume(rv, rt)
    vol_c = signed_volume(cv, ct)
    allv = np.vstack([rv, cv])
    print(f"ring : {len(rt)} tris, enclosed volume {vol_r:8.1f} m^3")
    print(f"cabin: {len(ct)} tris, enclosed volume {vol_c:8.1f} m^3")
    print("bounding box (m):")
    for ax, name in enumerate("xyz"):
        print(f"  {name}: {allv[:, ax].min():7.2f} .. "
              f"{allv[:, ax].max():7.2f}")
    ring_lo = rv[:, 2].min()
    cab_lo = cv[:, 2].min()
    print(f"cabin lowest z = {cab_lo:.2f}; ring section band bottom "
          f"~ {ring_lo:.2f} (clearance kept for clean meshing)")

    # reference values for CFD force coefficients
    th = np.linspace(0.0, 2.0 * np.pi, 20000, endpoint=False)
    ct, st = np.cos(th), np.sin(th)
    y = A * np.sign(ct) * np.abs(ct) ** 0.5
    z = C * (1.0 + np.sign(st) * np.abs(st) ** 0.5)
    perim = np.hypot(np.diff(np.append(y, y[0])),
                     np.diff(np.append(z, z[0]))).sum()
    print(f"loop perimeter = {perim:.1f} m ; reference area "
          f"S = perimeter x chord = {perim * CHORD:.0f} m^2 ; "
          f"span b = {2 * A:.0f} m ; chord = {CHORD} m")


if __name__ == "__main__":
    main()
