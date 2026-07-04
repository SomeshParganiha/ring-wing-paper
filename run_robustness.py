"""Red-team pass: probe the paper's weakest claims.

R1  Discretisation bias of the kernel (planar e > 1) -- convergence order
R2  Is e = 1 + h/b exact?  Grid convergence + Richardson extrapolation
R3  Superellipse corner resolution at high p
R4  Do the cabin conclusions depend on the assumed spine width?
R5  Does VLM near-optimality of untwisted rings survive stagger?
"""

import numpy as np

import trefftz as tz
from vlm import VLM

ALPHA = np.deg2rad(5.0)


def main():
    print("=== R1: kernel bias, planar wing (theory e = 1 exactly) ===")
    prev = None
    for n in (200, 400, 800, 1600, 3200):
        e = tz.solve(tz.planar_wing(n=n))["e"]
        ratio = "" if prev is None else f"   bias ratio {prev/(e-1.0):.2f}"
        print(f"  n={n:5d}   e={e:.5f}   bias={e-1.0:+.5f}{ratio}")
        prev = e - 1.0

    print("\n=== R2: e = 1 + h/b, ellipse h/b = 0.30, grid convergence ===")
    devs = {}
    for n in (384, 768, 1536, 3072):
        e = tz.solve(tz.ellipse_ring(0.30, n=n))["e"]
        devs[n] = e - 1.30
        print(f"  n={n:5d}   e={e:.6f}   deviation={e-1.30:+.6f}")
    rich = 2.0 * devs[3072] - devs[1536]  # Richardson assuming O(1/n)
    print(f"  Richardson-extrapolated deviation (O(1/n)): {rich:+.6f}")

    print("\n=== R3: superellipse p = 12, h/b = 0.5, corner resolution ===")
    for n in (384, 768, 1536, 3072):
        e = tz.solve(tz.superellipse_ring(0.5, 12.0, n=n,
                                          n_dense=8 * n))["e"]
        print(f"  n={n:5d}   e={e:.5f}")

    print("\n=== R4: cabin conclusions vs spine width (h/b=0.3, f=0.15) ===")
    print("  arc-hugging check: e at z/h = 0.1 / 0.3 / 0.5 per width")
    for w in (0.3, 0.5, 0.7):
        es = []
        for zf in (0.1, 0.3, 0.5):
            comps = tz.ellipse_with_spine(0.30, spine_frac=w, n=768,
                                          z_frac=zf)
            es.append(tz.solve(comps, component_lift={1: 0.15})["e"])
        order = "OK (monotone toward arc)" if es[0] > es[1] > es[2] else \
            "VIOLATED"
        print(f"  width={w:.1f}b   e = {es[0]:.4f} / {es[1]:.4f} / "
              f"{es[2]:.4f}   {order}")
    print("  lift-share penalty check: e at f = 0.10 / 0.20 / 0.30, "
          "z/h = 0.5")
    for w in (0.3, 0.5, 0.7):
        es = []
        for f in (0.10, 0.20, 0.30):
            comps = tz.ellipse_with_spine(0.30, spine_frac=w, n=768,
                                          z_frac=0.5)
            es.append(tz.solve(comps, component_lift={1: f})["e"])
        print(f"  width={w:.1f}b   e = {es[0]:.4f} / {es[1]:.4f} / "
              f"{es[2]:.4f}")

    print("\n=== R5: VLM with stagger (superellipse p=4, h/b=0.5, "
          "c/b=0.1) ===")
    pts = tz.superellipse_ring(0.5, 4.0, n=144)[0].points
    span = np.ptp(pts[:, 0])
    h = np.ptp(pts[:, 1])
    z_mid = pts[:, 1].mean()
    e_ideal = tz.solve([tz.Component(pts, closed=True)])["e"]
    strips_z = 0.5 * (pts[:, 1] + np.roll(pts[:, 1], -1))
    for stag in (0.0, 0.25, 0.50):
        x_off = stag * span * (strips_z - z_mid) / h
        m = VLM(pts, closed=True, chord=0.1 * span, n_chord=8,
                x_offset=x_off)
        r0, _ = m.efficiency(m.solve(ALPHA))
        eps, r1 = m.optimise_twist(ALPHA)
        print(f"  stagger={stag:.2f}b   untwisted e={r0['e']:.4f} "
              f"({100*r0['e']/e_ideal:.1f}%)   optimised e={r1['e']:.4f} "
              f"({100*r1['e']/e_ideal:.1f}%)   max twist "
              f"{np.rad2deg(np.abs(eps).max()):.2f} deg")


if __name__ == "__main__":
    main()
