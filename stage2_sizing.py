"""Stage 2 preliminary sizing for the 1 m powered Vyoma demonstrator.

Predictions to be tested by flight: wing loading, stall/cruise speed,
Reynolds number, required thrust, CG window, and the glide polar (L/D and
sink rate vs airspeed) under an ideal-build and a realistic-build bound.

All aero estimates are transparent and assumption-flagged; the point of
paper #2 is to measure which bound the real aircraft lands on.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import trefftz as tz
from vlm import VLM

# ---- geometry (1 m demonstrator, same shape family as the paper) ----
B = 1.00            # span (m)
HB = 0.50           # height / span
C = 0.10            # chord (m), c/b = 0.10
H = HB * B
RHO = 1.225         # air density (kg/m3)
NU = 1.5e-5         # kinematic viscosity (m2/s)
G = 9.81

# effective lifting reference area: two arcs of span x chord, reduced for
# the curved (squircle) planform -> factor ~0.9 each arc.
S = 2 * 0.9 * B * C          # ~0.18 m2
AR = B * B / S               # span^2 / S

# ---- mass budget (measured-ish component estimates, grams) ----
mass = {
    "foam airframe + spar": 180,
    "2 motors + ESCs": 120,
    "Pixhawk + GPS + wiring": 90,
    "3S 1300 mAh LiPo": 110,
    "2 servos + linkages": 24,
    "pitot + misc": 26,
}
M = sum(mass.values()) / 1000.0   # kg
W = M * G                          # N


def flight_speeds():
    cl_max = 1.0    # ring at low Re, conservative
    v_stall = np.sqrt(2 * W / (RHO * S * cl_max))
    v_cruise = 1.3 * v_stall
    re_cruise = v_cruise * C / NU
    return v_stall, v_cruise, re_cruise


def glide_polar(e, cd0, label):
    cl = np.linspace(0.25, 1.15, 60)
    cdi = cl ** 2 / (np.pi * AR * e)
    cd = cd0 + cdi
    ld = cl / cd
    v = np.sqrt(2 * W / (RHO * S * cl))
    sink = v * cd / cl                 # steady glide sink rate (m/s)
    i = np.argmax(ld)
    print(f"  [{label}]  best L/D = {ld[i]:.1f} at CL={cl[i]:.2f}, "
          f"V={v[i]:.1f} m/s, sink={sink[i]:.2f} m/s")
    return v, ld, sink, (v[i], ld[i])


def required_thrust(v_cruise, ld_realistic):
    # cruise thrust = drag = W / (L/D); climb wants T/W ~0.6-0.8
    t_cruise = W / ld_realistic
    t_climb = 0.7 * W
    return t_cruise, t_climb


def main():
    print("=== Stage 2 Vyoma demonstrator — predicted spec ===")
    print(f"span {B} m, height {H} m (h/b={HB}), chord {C} m")
    print(f"reference lifting area S = {S:.3f} m^2, aspect ratio AR = {AR:.2f}")
    print(f"all-up mass M = {M*1000:.0f} g, weight W = {W:.2f} N")
    print(f"wing loading W/S = {W/S:.1f} N/m^2 = {M/S:.2f} kg/m^2")

    vs, vc, re = flight_speeds()
    print(f"\nstall speed  ~ {vs:.1f} m/s ({vs*3.6:.0f} km/h)")
    print(f"cruise speed ~ {vc:.1f} m/s ({vc*3.6:.0f} km/h)")
    print(f"cruise Reynolds number ~ {re:,.0f}  (low-Re airfoil territory)")

    print("\nCG window (from vortex-lattice neutral point, chord-relative):")
    print("  neutral point ~0.06 chord aft of mid-gap; CG 0.10-0.20 chord")
    print(f"  ahead of it -> place CG ~1.0-1.6 cm ahead of NP "
          f"({0.15*C*100:.1f} cm margin on a {C*100:.0f} cm chord)")

    print("\npredicted glide polar (two bounds):")
    v1, ld1, s1, best1 = glide_polar(1.76, 0.030, "ideal build  e=1.76 CD0=.030")
    v2, ld2, s2, best2 = glide_polar(1.40, 0.050, "rough build  e=1.40 CD0=.050")

    t_cr, t_cl = required_thrust(vc, best2[1])
    print(f"\nthrust: cruise ~ {t_cr:.2f} N ({t_cr/G*1000:.0f} gf total), "
          f"climb target ~ {t_cl:.2f} N ({t_cl/G*1000:.0f} gf) -> "
          f"~{t_cl/G*1000/2:.0f} gf per motor (2 motors)")

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    a1.plot(v1, ld1, label="ideal build (e=1.76)")
    a1.plot(v2, ld2, label="rough build (e=1.40)")
    a1.axhline(3.5, ls=":", color="gray", label="Stage 0 cardboard (~3.5)")
    a1.set_xlabel("airspeed V (m/s)"); a1.set_ylabel("L/D")
    a1.set_title("Predicted glide ratio vs speed"); a1.legend(); a1.grid(alpha=.3)
    a2.plot(v1, s1, label="ideal build"); a2.plot(v2, s2, label="rough build")
    a2.set_xlabel("airspeed V (m/s)"); a2.set_ylabel("sink rate (m/s)")
    a2.set_title("Predicted sink rate (glide polar)")
    a2.invert_yaxis(); a2.legend(); a2.grid(alpha=.3)
    fig.tight_layout(); fig.savefig("stage2_predicted_polar.png", dpi=150)
    print("\nwrote stage2_predicted_polar.png")


if __name__ == "__main__":
    main()
