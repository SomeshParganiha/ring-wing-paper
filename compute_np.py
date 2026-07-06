"""Neutral point of the staggered Vyoma ring (for the chuck-glider CG).

The neutral point is the aerodynamic centre of the whole configuration:
the lift-slope-weighted mean x of the strip lift centroids.  CG must sit
ahead of it; static margin is quoted in chords.

Geometry matches the STL/paper: superellipse p=4, h/b=0.5, c/b=0.1,
stagger 0.25b total (lower arc forward, upper aft), no twist.
Units: semispan = 1 (span b = 2).
"""

import numpy as np

import trefftz as tz
from vlm import VLM


def main():
    pts = tz.superellipse_ring(0.5, 4.0, n=144)[0].points
    span = np.ptp(pts[:, 0])
    h = np.ptp(pts[:, 1])
    z_mid = pts[:, 1].mean()
    strips_z = 0.5 * (pts[:, 1] + np.roll(pts[:, 1], -1))
    x_off = 0.25 * span * (strips_z - z_mid) / h   # +-0.125 b, as in the STL
    chord = 0.1 * span

    model = VLM(pts, closed=True, chord=chord, n_chord=6, x_offset=x_off)

    a1, a2 = np.deg2rad(2.0), np.deg2rad(4.0)
    g1, g2 = model.solve(a1), model.solve(a2)

    v_inf = np.array([1.0, 0.0, 0.0])   # small-angle: use axial flow for KJ
    l = model.bound_b - model.bound_a
    f_per_gamma_z = np.cross(np.broadcast_to(v_inf, l.shape), l)[:, 2]
    dfz = (g2 - g1) * f_per_gamma_z           # dF_z per panel (per dalpha)
    x_mid = 0.5 * (model.bound_a[:, 0] + model.bound_b[:, 0])

    x_np = float(np.sum(dfz * x_mid) / np.sum(dfz))
    print(f"span b = {span:.3f}, chord c = {chord:.3f}, "
          f"stagger = {0.25*span:.3f} (total, lower fwd / upper aft)")
    print(f"neutral point x_np = {x_np:+.4f} semispan units "
          f"({x_np/chord:+.2f} chords from mid-gap)")
    for margin in (0.10, 0.15, 0.20):
        x_cg = x_np - margin * chord
        print(f"  CG for {int(margin*100)}% static margin: "
              f"x_cg = {x_cg:+.4f}")

    # convert to a 60 cm-span chuck glider (unit = 30 cm)
    scale = 30.0  # cm per semispan unit
    x_le_bottom = (-0.25 * chord - 0.125 * span) * scale
    print(f"\n--- 60 cm-span chuck glider (chord {chord*scale:.1f} cm) ---")
    print(f"bottom-arc leading edge sits at x = {x_le_bottom:+.1f} cm")
    for margin in (0.10, 0.15, 0.20):
        x_cg = (x_np - margin * chord) * scale
        print(f"  {int(margin*100)}% margin: CG {x_cg - x_le_bottom:.1f} cm "
              f"behind the bottom-arc leading edge (x = {x_cg:+.1f} cm)")


if __name__ == "__main__":
    main()
