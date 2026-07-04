"""
Finite-chord vortex-lattice method (VLM) for planar and ring wings.

Purpose: cross-check the Trefftz-plane *ideal* span efficiencies with what a
finite-chord surface actually achieves -- untwisted, and with an optimised
spanwise twist schedule.

Formulation (classical horseshoe VLM, Katz & Plotkin ch. 12):
- The lifting surface is a strip per spanwise station pair, extruded in +x
  from the trace curve (y, z); chordwise M panels per strip.
- Each panel carries a horseshoe vortex: bound segment at the panel quarter
  chord, trailing legs running downstream (legs are made effectively
  semi-infinite by extending 1e4 spans; the truncation error in induced
  velocity is O(1/L^2), i.e. ~1e-8).
- Collocation at panel three-quarter chord, mid-strip.  Boundary condition
  (V_inf + v_induced) . n = 0 with twist applied through the right-hand side
  (transpiration form), so the aerodynamic influence matrix is assembled
  once and the strip circulation is exactly linear in the twist angles.
- Local frame per strip: chordwise x_hat = (1,0,0), span direction s_hat
  along the trace, normal n_hat = x_hat x s_hat.  This matches the 2-D
  Trefftz kernel's orientation convention (n = (-t_z, t_y)), so the strip
  circulations feed straight into trefftz.evaluate() for induced drag --
  ideal and achieved efficiencies are measured by the same functionals.

Sanity targets (see run_vlm.py):
- elliptical planform, AR = 8: e ~ 1.0, CL_alpha ~ 2*pi/(1 + 2/AR)
- rectangular planform: e < elliptical; twist-optimised -> e ~ 1.0
"""

import numpy as np

import trefftz as tz

LEG_LENGTH_FACTOR = 1.0e4  # trailing-leg length in spans ("semi-infinite")
CUTOFF = 1.0e-10           # vortex-core guard on |r1 x r2|^2


def _segment_velocity(points, a, b):
    """Velocity at `points` from unit-strength straight vortex segments.

    points: (P, 3); a, b: (S, 3) segment endpoints (traversal a -> b).
    Returns (P, S, 3).  Katz & Plotkin eq. 10.115.
    """
    r1 = points[:, None, :] - a[None, :, :]          # (P, S, 3)
    r2 = points[:, None, :] - b[None, :, :]
    cr = np.cross(r1, r2)                            # (P, S, 3)
    cr2 = np.einsum("psk,psk->ps", cr, cr)
    r1n = np.linalg.norm(r1, axis=2)
    r2n = np.linalg.norm(r2, axis=2)
    r0 = b - a                                       # (S, 3)
    d1 = np.einsum("sk,psk->ps", r0, r1) / np.where(r1n < 1e-30, 1.0, r1n)
    d2 = np.einsum("sk,psk->ps", r0, r2) / np.where(r2n < 1e-30, 1.0, r2n)
    k = (d1 - d2) / (4.0 * np.pi * np.where(cr2 < CUTOFF, 1.0, cr2))
    k = np.where(cr2 < CUTOFF, 0.0, k)
    return cr * k[:, :, None]


class VLM:
    """Horseshoe-vortex lattice on a trace curve extruded in x.

    trace_points: (K, 2) station positions (y, z) along the trace
    closed:       True for a ring (last station connects to the first)
    chord:        scalar or (n_strips,) chord per strip
    """

    def __init__(self, trace_points, closed, chord, n_chord=8,
                 x_offset=None):
        pts = np.asarray(trace_points, dtype=float)
        if closed:
            p0 = pts
            p1 = np.roll(pts, -1, axis=0)
        else:
            p0 = pts[:-1]
            p1 = pts[1:]
        self.closed = closed
        self.trace_points = pts
        self.n_strips = len(p0)
        self.n_chord = int(n_chord)
        chord = np.broadcast_to(np.asarray(chord, dtype=float),
                                (self.n_strips,)).copy()
        self.chord = chord

        sv = p1 - p0                                  # strip span vectors (2D)
        self.ds = np.linalg.norm(sv, axis=1)
        s_hat2 = sv / self.ds[:, None]
        # 3-D frames: x_hat = (1,0,0); s_hat = (0, sy, sz); n = x_hat x s_hat
        self.s_hat = np.column_stack(
            [np.zeros(self.n_strips), s_hat2[:, 0], s_hat2[:, 1]])
        self.n_hat = np.column_stack(
            [np.zeros(self.n_strips), -s_hat2[:, 1], s_hat2[:, 0]])

        M = self.n_chord
        K = self.n_strips
        # quarter-chord line of each strip at x = x_offset (default 0,
        # i.e. unstaggered; pass x_offset per strip to stagger the arcs)
        if x_offset is None:
            x_offset = np.zeros(K)
        x_offset = np.broadcast_to(np.asarray(x_offset, dtype=float),
                                   (K,)).copy()
        x_le = -0.25 * chord + x_offset
        edge0_3d = np.column_stack([np.zeros(K), p0[:, 0], p0[:, 1]])
        edge1_3d = np.column_stack([np.zeros(K), p1[:, 0], p1[:, 1]])

        bound_a, bound_b, colloc = [], [], []
        for m in range(M):
            xa = x_le + chord * (m + 0.25) / M   # bound vortex x per strip
            xc = x_le + chord * (m + 0.75) / M   # collocation x per strip
            a = edge0_3d.copy()
            a[:, 0] = xa
            b = edge1_3d.copy()
            b[:, 0] = xa
            c = 0.5 * (edge0_3d + edge1_3d)
            c[:, 0] = xc
            bound_a.append(a)
            bound_b.append(b)
            colloc.append(c)
        # panel index = m * K + k  (chord-major, strip-minor)
        self.bound_a = np.vstack(bound_a)
        self.bound_b = np.vstack(bound_b)
        self.colloc = np.vstack(colloc)
        self.n_panels = M * K
        self.panel_strip = np.tile(np.arange(K), M)
        self.panel_n_hat = np.vstack([self.n_hat] * M)

        span_len = np.ptp(pts[:, 0])
        leg = LEG_LENGTH_FACTOR * max(span_len, 1.0)
        far_a = self.bound_a.copy()
        far_a[:, 0] += leg
        far_b = self.bound_b.copy()
        far_b[:, 0] += leg

        # AIC: velocity at all collocation points from each panel's
        # horseshoe (leg far_a->a, bound a->b, leg b->far_b), unit Gamma.
        P = self.colloc
        v = np.zeros((self.n_panels, self.n_panels, 3))
        chunk = 256
        for lo in range(0, self.n_panels, chunk):
            hi = min(lo + chunk, self.n_panels)
            v[:, lo:hi, :] = (
                _segment_velocity(P, far_a[lo:hi], self.bound_a[lo:hi])
                + _segment_velocity(P, self.bound_a[lo:hi],
                                    self.bound_b[lo:hi])
                + _segment_velocity(P, self.bound_b[lo:hi], far_b[lo:hi])
            )
        self.aic = np.einsum("pqk,pk->pq", v, self.panel_n_hat)
        self._lu = None

    def solve(self, alpha, twist=None):
        """Panel circulations at freestream angle `alpha` (rad) with an
        optional per-strip twist array (rad, positive nose-up)."""
        rhs = self.rhs_alpha(alpha)
        if twist is not None:
            rhs = rhs + self.rhs_twist_matrix(alpha) @ np.asarray(twist)
        gamma = np.linalg.solve(self.aic, rhs)
        return gamma

    def rhs_alpha(self, alpha):
        """Right-hand side -V_inf . n per panel (no twist)."""
        v_inf = np.array([np.cos(alpha), 0.0, np.sin(alpha)])
        return -(self.panel_n_hat @ v_inf)

    def rhs_twist_matrix(self, alpha):
        """d(rhs)/d(twist): rotating a strip's sections nose-up by eps tilts
        each panel normal by eps * x_hat, adding -eps * (V_inf . x_hat) to
        the boundary condition.  Returns (n_panels, n_strips)."""
        T = np.zeros((self.n_panels, self.n_strips))
        T[np.arange(self.n_panels), self.panel_strip] = -np.cos(alpha)
        return T

    def strip_circulation(self, gamma):
        """Total shed circulation per strip (sum over chordwise panels),
        in the trace orientation."""
        g = np.zeros(self.n_strips)
        np.add.at(g, self.panel_strip, gamma)
        return g

    def lift_kutta_joukowski(self, gamma, alpha):
        """Near-field lift from rho * Gamma * (V_inf x l) on bound segments
        (independent check on the Trefftz lift)."""
        v_inf = np.array([np.cos(alpha), 0.0, np.sin(alpha)])
        l = self.bound_b - self.bound_a
        f = np.cross(np.broadcast_to(v_inf, l.shape), l) * gamma[:, None]
        return f[:, 2].sum()

    def area(self):
        return float(np.sum(self.chord * self.ds))

    def trefftz_component(self):
        return [tz.Component(self.trace_points, closed=self.closed)]

    def efficiency(self, gamma):
        """Span efficiency of this loading, via the shared Trefftz kernel."""
        g = self.strip_circulation(gamma)
        return tz.evaluate(self.trefftz_component(), g), g

    def optimise_twist(self, alpha, ridge=1e-4):
        """Least-squares twist schedule driving the strip loading toward the
        Trefftz-optimal distribution at the untwisted lift level.

        ridge is relative Tikhonov damping (scaled by mean diag of G^T G);
        it keeps low-influence strips (e.g. planar tips) from demanding
        unphysically large twist for negligible efficiency gain.
        Returns (twist, result_dict).  Linear: no iteration needed.
        """
        comp = self.trefftz_component()
        ideal = tz.solve(comp)               # unit-lift optimal loading
        g0_panels = self.solve(alpha)
        g0 = self.strip_circulation(g0_panels)
        A_t, bvec, _ = tz.build_system(comp)
        L0 = bvec @ g0
        target = ideal["gamma"] * (L0 / (bvec @ ideal["gamma"]))

        # strip loading is linear in twist: g(eps) = g0 + G eps
        ainv_t = np.linalg.solve(self.aic, self.rhs_twist_matrix(alpha))
        G = np.zeros((self.n_strips, self.n_strips))
        for k in range(self.n_strips):
            G[:, k] = self.strip_circulation(ainv_t[:, k])

        gtg = G.T @ G
        lam = ridge * np.trace(gtg) / self.n_strips
        rhs = G.T @ (target - g0)
        eps = np.linalg.solve(gtg + lam * np.eye(self.n_strips), rhs)
        gamma = self.solve(alpha, twist=eps)
        res, g = self.efficiency(gamma)
        res["twist"] = eps
        res["gamma_strips"] = g
        res["target"] = target
        return eps, res
