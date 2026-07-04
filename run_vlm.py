"""Finite-chord VLM cross-check of the Trefftz-plane ideal efficiencies.

Gate 1  planar elliptical planform, AR = 8: e ~ 1.0, CL_alpha ~ Helmbold
Gate 2  planar rectangular planform, AR = 8: e < elliptical; twist-optimised
        recovers e ~ 1.0 (validates the twist machinery)
Gate 3  chordwise-resolution independence
Study   circle / ellipse / p=4 superellipse rings (h/b as in the paper):
        untwisted vs twist-optimised vs Trefftz ideal
"""

import csv

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import trefftz as tz
from vlm import VLM

ALPHA = np.deg2rad(5.0)


def planar_stations(n_strips, semispan):
    th = np.linspace(0.0, np.pi, n_strips + 1)
    y = -semispan * np.cos(th)
    return np.column_stack([y, np.zeros_like(y)])


def elliptical_chords(stations, semispan, c_root):
    mid = 0.5 * (stations[:-1, 0] + stations[1:, 0])
    return c_root * np.sqrt(np.clip(1.0 - (mid / semispan) ** 2, 1e-6, 1.0))


def ring_stations(kind, hb, n_strips):
    if kind == "circle":
        comp = tz.ellipse_ring(1.0, n=n_strips)
    elif kind == "ellipse":
        comp = tz.ellipse_ring(hb, n=n_strips)
    elif kind == "superellipse4":
        comp = tz.superellipse_ring(hb, 4.0, n=n_strips)
    else:
        raise ValueError(kind)
    return comp[0].points


def main():
    print("=== Gate 1: planar elliptical planform, AR = 8 ===")
    semispan, c_root = 4.0, 16.0 / (4.0 * np.pi)
    st = planar_stations(100, semispan)
    model = VLM(st, closed=False, chord=elliptical_chords(st, semispan, c_root),
                n_chord=8)
    res, _ = model.efficiency(model.solve(ALPHA))
    e_grid = tz.solve(model.trefftz_component())["e"]
    cl = res["L"] / (0.5 * model.area())
    cla = cl / ALPHA
    ar = res["span"] ** 2 / model.area()
    helmbold = 2.0 * np.pi / (1.0 + 2.0 / ar)
    l_kj = model.lift_kutta_joukowski(model.solve(ALPHA), ALPHA)
    print(f"  e = {res['e']:.4f} = {100*res['e']/e_grid:.1f}% of the "
          f"same-grid ideal ({e_grid:.4f})   (target ~100%)")
    print(f"  CL_alpha = {cla:.3f} /rad   (Helmbold {helmbold:.3f}; "
          f"lifting-surface values sit slightly below lifting-line)")
    print(f"  lift check: Trefftz {res['L']:.5f} vs Kutta-Joukowski "
          f"{l_kj:.5f}  ({100*abs(l_kj/res['L']-1):.2f}% apart)")

    print("\n=== Gate 2: planar rectangular planform, AR = 8 ===")
    st = planar_stations(100, semispan)
    model = VLM(st, closed=False, chord=1.0, n_chord=8)
    e_grid = tz.solve(model.trefftz_component())["e"]
    res0, _ = model.efficiency(model.solve(ALPHA))
    eps, res1 = model.optimise_twist(ALPHA)
    print(f"  untwisted        e = {res0['e']:.4f} "
          f"({100*res0['e']/e_grid:.1f}% of same-grid ideal)")
    print(f"  twist-optimised  e = {res1['e']:.4f} "
          f"({100*res1['e']/e_grid:.1f}%), "
          f"max twist {np.rad2deg(np.abs(eps).max()):.2f} deg")

    print("\n=== Gate 3: chordwise resolution (rectangular, untwisted) ===")
    for m in (4, 8, 12):
        model = VLM(st, closed=False, chord=1.0, n_chord=m)
        r, _ = model.efficiency(model.solve(ALPHA))
        print(f"  n_chord = {m:2d}   e = {r['e']:.4f}")

    print("\n=== Ring study: c/b = 0.1, 144 strips, 8 chordwise panels ===")
    cases = [("circle", 1.0), ("ellipse", 0.5), ("superellipse4", 0.5)]
    rows = []
    keep = {}
    for kind, hb in cases:
        pts = ring_stations(kind, hb, 144)
        span = np.ptp(pts[:, 0])
        model = VLM(pts, closed=True, chord=0.1 * span, n_chord=8)
        e_ideal = tz.solve(model.trefftz_component())["e"]
        res0, g0 = model.efficiency(model.solve(ALPHA))
        eps, res1 = model.optimise_twist(ALPHA)
        rec0 = res0["e"] / e_ideal
        rec1 = res1["e"] / e_ideal
        tw = np.rad2deg(np.abs(eps).max())
        rows.append((kind, hb, e_ideal, res0["e"], res1["e"],
                     rec0, rec1, tw))
        keep[kind] = (model, g0, res1, eps)
        print(f"  {kind:14s} h/b={hb:.1f}  ideal e={e_ideal:.4f}  "
              f"untwisted e={res0['e']:.4f} ({100*rec0:.1f}%)  "
              f"optimised e={res1['e']:.4f} ({100*rec1:.1f}%)  "
              f"max twist {tw:.2f} deg")

    with open("results_vlm.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case", "h_over_b", "e_ideal", "e_untwisted",
                    "e_twist_optimised", "recovery_untwisted",
                    "recovery_optimised", "max_twist_deg"])
        w.writerows(rows)

    print("\n=== Chord sensitivity: superellipse p=4, h/b=0.5, untwisted ===")
    pts = ring_stations("superellipse4", 0.5, 144)
    span = np.ptp(pts[:, 0])
    e_ideal = tz.solve([tz.Component(pts, closed=True)])["e"]
    for cb in (0.05, 0.10, 0.15, 0.20):
        m = VLM(pts, closed=True, chord=cb * span, n_chord=8)
        r, _ = m.efficiency(m.solve(ALPHA))
        print(f"  c/b = {cb:.2f}   e = {r['e']:.4f}   "
              f"({100*r['e']/e_ideal:.1f}% of ideal)")

    model, g0, res1, eps = keep["superellipse4"]
    s = np.concatenate([[0.0], np.cumsum(model.ds)])[:-1] + 0.5 * model.ds
    s = s / (model.ds.sum())
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
    ax1.plot(s, res1["target"], color="gray", lw=3.0, alpha=0.55,
             label="Trefftz ideal")
    ax1.plot(s, g0, color="#D85A30", lw=1.2, label="VLM untwisted")
    ax1.plot(s, res1["gamma_strips"], color="#1D9E75", lw=1.2, ls="--",
             label="VLM twist-optimised (coincides with ideal)")
    ax1.set_ylabel("strip circulation  $\\Gamma$")
    ax1.set_title("Superellipse ring (p=4, h/b=0.5): loading around the loop")
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax2.plot(s, np.rad2deg(eps), color="#534AB7", lw=1.2)
    ax2.set_xlabel("arc position around the loop  s / P")
    ax2.set_ylabel("optimised twist (deg)")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("vlm_loading.png", dpi=160)
    print("\nwrote results_vlm.csv, vlm_loading.png")


if __name__ == "__main__":
    main()
