"""
Trefftz-plane optimal span-efficiency solver for planar and nonplanar
(including closed) lifting systems.

Method
------
Far behind a lifting system, the wake trace in the Trefftz (y-z) plane fully
determines the minimum induced drag (Munk).  We discretise the trace into
panels of piecewise-constant circulation Gamma_i.  Each panel sheds a pair of
2-D point vortices (-Gamma_i at its start point, +Gamma_i at its end point);
shared edges between neighbouring panels then automatically carry the
difference Gamma_i - Gamma_{i+1}, and free ends carry the full tip vortex.

Induced drag and lift:
    D = (rho/2) * sum_i Gamma_i * w_n(c_i) * ds_i
    L = rho * V * sum_i Gamma_i * dy_i
with w_n the Trefftz-plane normal wash at the panel control point c_i.

Minimising the quadratic form D subject to fixed L gives the optimal loading
Gamma* = A^-1 b / (b^T A^-1 b) and the span efficiency
    e = L^2 / (pi * q * span^2 * D).

Units: rho = V = 1, so q = 1/2.  e is dimensionless and unit-independent.

Validation targets:
    planar wing                e = 1.000 (exact, Munk 1921)
    box wing, h/b = 0.2        e ~ 1.46  (Prandtl 1924 "best wing system")
"""

import numpy as np


class Component:
    """A single trace curve in the Trefftz plane."""

    def __init__(self, points, closed):
        self.points = np.asarray(points, dtype=float)  # (M, 2) of (y, z)
        self.closed = bool(closed)

    def panel_arrays(self):
        p = self.points
        if self.closed:
            a = p
            b = np.roll(p, -1, axis=0)
        else:
            a = p[:-1]
            b = p[1:]
        return a, b  # panel start / end points, shape (n_panels, 2)


def _induced_velocity(targets, sources):
    """2-D unit-vortex velocity at each target from each source.

    Returns uy, uz with shape (n_targets, n_sources) for counterclockwise
    unit vortices: u = (1 / 2 pi r^2) * (-(z_t - z_s), (y_t - y_s)).
    """
    dy = targets[:, 0][:, None] - sources[:, 0][None, :]
    dz = targets[:, 1][:, None] - sources[:, 1][None, :]
    r2 = dy * dy + dz * dz
    r2 = np.where(r2 < 1e-14, np.inf, r2)  # self-influence -> 0
    k = 1.0 / (2.0 * np.pi * r2)
    return -k * dz, k * dy


def build_system(components):
    """Assemble the Trefftz-plane quadratic form.

    Returns (A, bvec, aux) with induced drag D = Gamma^T A Gamma and lift
    L = bvec^T Gamma (rho = V = 1), plus geometry arrays in aux.
    """
    starts, ends, mids, normals, ds, dyv, slices = [], [], [], [], [], [], []
    offset = 0
    for comp in components:
        a, b = comp.panel_arrays()
        t = b - a
        length = np.linalg.norm(t, axis=1)
        that = t / length[:, None]
        starts.append(a)
        ends.append(b)
        mids.append(0.5 * (a + b))
        normals.append(np.column_stack([-that[:, 1], that[:, 0]]))
        ds.append(length)
        dyv.append(t[:, 0])
        slices.append(slice(offset, offset + len(length)))
        offset += len(length)
    starts = np.vstack(starts)
    ends = np.vstack(ends)
    mids = np.vstack(mids)
    normals = np.vstack(normals)
    ds = np.concatenate(ds)
    dyv = np.concatenate(dyv)

    # normal wash at control point i per unit Gamma_k:
    # panel k contributes vortex -1 at its start and +1 at its end.
    uy_s, uz_s = _induced_velocity(mids, starts)
    uy_e, uz_e = _induced_velocity(mids, ends)
    m_uy = uy_e - uy_s
    m_uz = uz_e - uz_s
    M = normals[:, 0][:, None] * m_uy + normals[:, 1][:, None] * m_uz

    # D = -(1/2) Gamma^T Q Gamma with Q_ik = ds_i * M_ik ; symmetrise.
    # (Minus sign: with counterclockwise-positive vortices and left-handed
    # panel normals, physical induced drag is the negative of the raw form.)
    Q = ds[:, None] * M
    A = -0.25 * (Q + Q.T)  # includes the rho/2 factor (rho = 1)
    bvec = dyv.copy()  # L = sum Gamma_i dy_i  (rho V = 1)

    ys = np.concatenate([c.points[:, 0] for c in components])
    span = ys.max() - ys.min()
    aux = {"mids": mids, "ds": ds, "slices": slices, "span": span}
    return A, bvec, aux


def evaluate(components, gamma):
    """Span efficiency of a GIVEN circulation distribution (no optimising).

    gamma must have one entry per panel, ordered like build_system's arrays
    (component by component, panel by panel), in the trace orientation
    (positive along the traversal direction of each component's points).
    """
    A, bvec, aux = build_system(components)
    gamma = np.asarray(gamma, dtype=float)
    D = gamma @ A @ gamma
    L = bvec @ gamma
    q = 0.5
    e = L * L / (np.pi * q * aux["span"] ** 2 * D)
    return {"e": e, "D": D, "L": L, "span": aux["span"], "mids": aux["mids"]}


def solve(components, lift=1.0, component_lift=None):
    """Optimal loading for a list of Components.

    component_lift: optional dict {component_index: absolute_lift} forcing a
    given component to carry a fixed share of the total lift (KKT equality
    constraints).  Returns dict of results.
    """
    A, bvec, aux = build_system(components)
    mids, ds, slices = aux["mids"], aux["ds"], aux["slices"]
    n = len(ds)
    dyv = bvec

    # equality constraints: total lift, plus optional per-component lift.
    cons_vecs = [bvec]
    cons_vals = [lift]
    if component_lift:
        for idx, value in component_lift.items():
            v = np.zeros(n)
            v[slices[idx]] = dyv[slices[idx]]
            cons_vecs.append(v)
            cons_vals.append(value)
    B = np.column_stack(cons_vecs)
    d = np.array(cons_vals)
    m = B.shape[1]

    # KKT system for  min Gamma^T A Gamma  s.t.  B^T Gamma = d
    K = np.zeros((n + m, n + m))
    K[:n, :n] = 2.0 * (A + 1e-12 * np.eye(n))
    K[:n, n:] = -B
    K[n:, :n] = B.T
    rhs = np.concatenate([np.zeros(n), d])
    sol = np.linalg.solve(K, rhs)
    gamma = sol[:n]
    D = gamma @ A @ gamma
    L = bvec @ gamma

    ys = np.concatenate([c.points[:, 0] for c in components])
    span = ys.max() - ys.min()
    q = 0.5
    e = L * L / (np.pi * q * span * span * D)
    return {
        "e": e,
        "D": D,
        "L": L,
        "span": span,
        "gamma": gamma,
        "mids": mids,
        "ds": ds,
        "slices": slices,
    }


# ---------------------------------------------------------------- geometries

def cosine_spaced(n):
    """n+1 points in [-1, 1] clustered at the ends (cosine spacing)."""
    th = np.linspace(0.0, np.pi, n + 1)
    return -np.cos(th)


def planar_wing(n=400, semispan=1.0):
    y = cosine_spaced(n) * semispan
    pts = np.column_stack([y, np.zeros_like(y)])
    return [Component(pts, closed=False)]


def _resample_closed_polygon(corners, n):
    """Uniform arc-length resampling of a closed polygon into n points.

    Equal panel lengths everywhere avoid the corner ill-conditioning that
    mixed spacings cause with point-vortex kernels.
    """
    corners = np.asarray(corners, dtype=float)
    seg = np.roll(corners, -1, axis=0) - corners
    seg_len = np.linalg.norm(seg, axis=1)
    perim = seg_len.sum()
    s_corner = np.concatenate([[0.0], np.cumsum(seg_len)])
    s = np.linspace(0.0, perim, n, endpoint=False)
    pts = np.empty((n, 2))
    for i, si in enumerate(s):
        k = np.searchsorted(s_corner, si, side="right") - 1
        k = min(k, len(corners) - 1)
        f = (si - s_corner[k]) / seg_len[k]
        pts[i] = corners[k] + f * seg[k]
    return pts


def box_wing(h_over_b, n_span=200, semispan=1.0):
    b = 2.0 * semispan
    h = h_over_b * b
    perim = 2.0 * b + 2.0 * h
    n_total = max(64, int(round(n_span * perim / b)))
    corners = [(-semispan, 0.0), (semispan, 0.0),
               (semispan, h), (-semispan, h)]
    pts = _resample_closed_polygon(corners, n_total)
    return [Component(pts, closed=True)]


def ellipse_ring(h_over_b, n=512, semispan=1.0):
    b = 2.0 * semispan
    h = h_over_b * b
    th = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    y = semispan * np.cos(th)
    z = 0.5 * h * (1.0 + np.sin(th))
    return [Component(np.column_stack([y, z]), closed=True)]


def superellipse_ring(h_over_b, p, n=768, semispan=1.0, n_dense=8192):
    """Superelliptical ring |y/a|^p + |z/c|^p = 1, resampled to uniform
    arc length.  p = 2 is the ellipse; p -> inf approaches the box."""
    b = 2.0 * semispan
    h = h_over_b * b
    c = 0.5 * h
    th = np.linspace(0.0, 2.0 * np.pi, n_dense, endpoint=False)
    ct, st = np.cos(th), np.sin(th)
    y = semispan * np.sign(ct) * np.abs(ct) ** (2.0 / p)
    z = c * (1.0 + np.sign(st) * np.abs(st) ** (2.0 / p))
    dense = np.column_stack([y, z])
    pts = _resample_closed_polygon(dense, n)
    return [Component(pts, closed=True)]


def add_spine(comps, h_over_b, spine_frac=0.5, z_frac=0.5, n_spine=96,
              semispan=1.0):
    """Append a detached central lifting-body element at height z_frac*h
    (the cabin joins the ring fore-aft, so its Trefftz trace is a free
    central segment)."""
    b = 2.0 * semispan
    h = h_over_b * b
    ys = cosine_spaced(n_spine) * (0.5 * spine_frac * b)
    spine = np.column_stack([ys, np.full_like(ys, z_frac * h)])
    comps.append(Component(spine, closed=False))
    return comps


def ellipse_with_spine(h_over_b, spine_frac=0.5, n=512, n_spine=96,
                       semispan=1.0, z_frac=0.5):
    comps = ellipse_ring(h_over_b, n=n, semispan=semispan)
    return add_spine(comps, h_over_b, spine_frac=spine_frac, z_frac=z_frac,
                     n_spine=n_spine, semispan=semispan)
