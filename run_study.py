"""Validation + main study for the ring-wing span-efficiency paper."""

import csv

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import trefftz as tz


def main():
    print("=== 1. Validation against classical results ===")
    e_planar = tz.solve(tz.planar_wing(n=400))["e"]
    print(f"planar wing              e = {e_planar:.4f}   (theory: 1.0000)")

    for n in (64, 128, 256, 512):
        e = tz.solve(tz.box_wing(0.2, n_span=n))["e"]
        print(f"box h/b=0.20  n_span={n:4d}  e = {e:.4f}   (Prandtl approx ~1.46)")

    for n in (128, 256, 512, 1024):
        e = tz.solve(tz.ellipse_ring(1.0, n=n))["e"]
        print(f"circular ring n={n:5d}     e = {e:.4f}   (classical: 2.0000)")

    print("\n=== 2. Main sweep: e vs h/b ===")
    hbs = np.array([0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40,
                    0.50, 0.60, 0.75, 1.00])
    rows = []
    for hb in hbs:
        e_box = tz.solve(tz.box_wing(hb, n_span=256))["e"]
        e_ell = tz.solve(tz.ellipse_ring(hb, n=768))["e"]
        rows.append((hb, e_box, e_ell))
        print(f"h/b={hb:.2f}   box e={e_box:.4f}   ellipse e={e_ell:.4f}")

    with open("results_sweep.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["h_over_b", "e_box", "e_ellipse"])
        w.writerows(rows)

    r = np.array(rows)
    plt.figure(figsize=(7, 4.5))
    plt.plot(r[:, 0], r[:, 1], "o-", label="box wing")
    plt.plot(r[:, 0], r[:, 2], "s-", label="elliptical ring")
    plt.axhline(1.0, color="gray", lw=0.8, ls="--", label="planar wing")
    plt.xlabel("height / span  (h/b)")
    plt.ylabel("optimal span efficiency  e")
    plt.title("Minimum induced drag of closed lifting systems (Trefftz plane)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("efficiency_vs_hb.png", dpi=160)

    print("\n=== 3. Cabin-spine lift-fraction study (original contribution) ===")
    spine_rows = []
    for hb in (0.30, 0.50):
        comps = tz.ellipse_with_spine(hb, spine_frac=0.5, n=768)
        e_free = tz.solve(comps)["e"]
        for f in (0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40):
            res = tz.solve(comps, lift=1.0, component_lift={1: f})
            spine_rows.append((hb, f, res["e"], res["e"] / e_free))
            print(f"h/b={hb:.2f}  spine lift fraction={f:.2f}  "
                  f"e={res['e']:.4f}  (vs unconstrained {e_free:.4f})")

    with open("results_spine.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["h_over_b", "spine_lift_fraction", "e", "e_over_e_free"])
        w.writerows(spine_rows)

    sr = np.array(spine_rows)
    plt.figure(figsize=(7, 4.5))
    for hb, mark in ((0.30, "o-"), (0.50, "s-")):
        sel = sr[sr[:, 0] == hb]
        plt.plot(sel[:, 1], sel[:, 2], mark, label=f"ellipse h/b = {hb:.2f}")
    plt.xlabel("lift fraction carried by cabin spine")
    plt.ylabel("span efficiency  e")
    plt.title("Induced-drag cost of loading the central lifting body")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("spine_penalty.png", dpi=160)

    print("\n=== 4. Optimal loading picture (ellipse, h/b = 0.3) ===")
    res = tz.solve(tz.ellipse_ring(0.30, n=768))
    mids, gamma = res["mids"], res["gamma"]
    plt.figure(figsize=(6.5, 5))
    sc = plt.scatter(mids[:, 0], mids[:, 1], c=gamma, s=14, cmap="coolwarm")
    plt.colorbar(sc, label="optimal circulation  $\\Gamma$")
    plt.gca().set_aspect("equal")
    plt.xlabel("y / semispan")
    plt.ylabel("z / semispan")
    plt.title("Optimal circulation around the ring (h/b = 0.30)")
    plt.tight_layout()
    plt.savefig("optimal_loading_ring.png", dpi=160)
    print("wrote results_sweep.csv, results_spine.csv and 3 figures")


if __name__ == "__main__":
    main()
