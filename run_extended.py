"""Extended study: superellipse family, cabin height placement, and a
high-resolution test of the e = 1 + h/b law for elliptical rings."""

import csv

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import trefftz as tz


def main():
    print("=== 5. Superellipse family: ellipse -> box, h/b = 0.30 and 0.50 ===")
    ps = np.array([2.0, 2.5, 3.0, 4.0, 6.0, 8.0, 12.0])
    rows = []
    for hb in (0.30, 0.50):
        e_box = tz.solve(tz.box_wing(hb, n_span=256))["e"]
        e_p2 = tz.solve(tz.superellipse_ring(hb, 2.0, n=768))["e"]
        e_ell = tz.solve(tz.ellipse_ring(hb, n=768))["e"]
        print(f"h/b={hb:.2f}  consistency: superellipse p=2 e={e_p2:.4f} "
              f"vs ellipse e={e_ell:.4f}  | box e={e_box:.4f}")
        for p in ps:
            e = tz.solve(tz.superellipse_ring(hb, p, n=768))["e"]
            capture = (e - 1.0) / (e_box - 1.0)
            rows.append((hb, p, e, e_box, capture))
            print(f"  p={p:5.1f}  e={e:.4f}   captures {100*capture:5.1f}% "
                  f"of box benefit over planar")

    with open("results_superellipse.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["h_over_b", "p", "e", "e_box", "benefit_capture"])
        w.writerows(rows)

    r = np.array(rows)
    plt.figure(figsize=(7, 4.5))
    for hb, mark in ((0.30, "o-"), (0.50, "s-")):
        sel = r[r[:, 0] == hb]
        plt.plot(sel[:, 1], sel[:, 2], mark, label=f"superellipse h/b={hb:.2f}")
        plt.axhline(sel[0, 3], ls=":", lw=0.8, color="gray")
    plt.xlabel("superellipse exponent  p")
    plt.ylabel("optimal span efficiency  e")
    plt.title("From ellipse (p=2) toward box (p→∞): squaring the ring")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("efficiency_vs_p.png", dpi=160)

    print("\n=== 6. Where should the cabin sit? (h/b=0.30, 15% lift share) ===")
    zrows = []
    for zf in np.linspace(0.10, 0.90, 17):
        comps = tz.ellipse_with_spine(0.30, spine_frac=0.4, n=768, z_frac=zf)
        res = tz.solve(comps, lift=1.0, component_lift={1: 0.15})
        zrows.append((zf, res["e"]))
        print(f"  cabin z/h={zf:.2f}   e={res['e']:.4f}")

    with open("results_spine_height.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["z_frac", "e"])
        w.writerows(zrows)

    zr = np.array(zrows)
    plt.figure(figsize=(7, 4.5))
    plt.plot(zr[:, 0], zr[:, 1], "o-")
    plt.xlabel("cabin height inside ring  z/h")
    plt.ylabel("span efficiency  e  (cabin carries 15% of lift)")
    plt.title("Induced-drag cost vs vertical cabin placement (ellipse h/b=0.30)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("spine_height.png", dpi=160)

    print("\n=== 7. High-resolution test of e = 1 + h/b (ellipse) ===")
    dev_max = 0.0
    for hb in np.linspace(0.1, 1.0, 10):
        e = tz.solve(tz.ellipse_ring(hb, n=1536))["e"]
        dev = e - (1.0 + hb)
        dev_max = max(dev_max, abs(dev))
        print(f"  h/b={hb:.2f}   e={e:.5f}   e-(1+h/b)={dev:+.5f}")
    print(f"  max |deviation| = {dev_max:.5f}")

    print("\n=== 8. Design point: Vyoma squircle ring ===")
    hb, p = 0.50, 4.0
    ring = tz.superellipse_ring(hb, p, n=768)
    e_free = tz.solve(ring)["e"]
    comps = tz.superellipse_ring(hb, p, n=768)
    tz.add_spine(comps, hb, spine_frac=0.5, z_frac=0.15)
    res = tz.solve(comps, lift=1.0, component_lift={1: 0.15})
    e_box = tz.solve(tz.box_wing(hb, n_span=256))["e"]
    e_ell = tz.solve(tz.ellipse_ring(hb, n=768))["e"]
    print(f"  superellipse p=4, h/b=0.5, unloaded:            e = {e_free:.4f}")
    print(f"  same + low cabin (z/h=0.15) carrying 15% lift:  e = {res['e']:.4f}")
    print(f"  references: ellipse e={e_ell:.4f}, box e={e_box:.4f}, planar 1.0")

    mids, gamma = res["mids"], res["gamma"]
    plt.figure(figsize=(6.5, 5))
    sc = plt.scatter(mids[:, 0], mids[:, 1], c=gamma, s=14, cmap="coolwarm")
    plt.colorbar(sc, label="optimal circulation  $\\Gamma$")
    plt.gca().set_aspect("equal")
    plt.xlabel("y / semispan")
    plt.ylabel("z / semispan")
    plt.title("Vyoma design point: p=4 squircle, low cabin at 15% lift")
    plt.tight_layout()
    plt.savefig("design_point_loading.png", dpi=160)
    print("wrote results_superellipse.csv, results_spine_height.csv + 3 figures")


if __name__ == "__main__":
    main()
