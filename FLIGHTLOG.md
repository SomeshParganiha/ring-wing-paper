# Vyoma flight log

## Stage 0 — cardboard chuck glider

**Date:** 2026-07-07 · **Location:** indoors, still air

**Airframe:** 60 cm span, 30 cm height (h/b = 0.5), 8-facet approximation of
the p=4 superellipse ring, 6 cm chord, ~15 cm stagger (lower wing forward)
built into slanted side panels, ~3 mm decalage (top wing LE down).
Single-wall corrugated cardboard, bamboo-skewer spar reinforcement and
spine, modelling-clay nose ballast. Hand-thrown, unpowered.

**CG prediction vs measurement:**
- Predicted (vortex-lattice neutral point, `compute_np.py`, 10–20% static
  margin): balance point 7.5–8.0 cm behind the bottom wing's leading edge
  (i.e. ~1.5 cm behind its trailing edge, on the spine).
- Measured after trimming to a stable glide: **approximately as predicted**
  (owner-reported "about the same as calculated").

**Flight results:**
- Flights 1–2: released tray-flat / thrown too slowly → immediate pitch-up
  stall and flat fall. Lesson: ring must fly "window" upright; needs a
  firm, level launch.
- After re-trim and firm level throws: stable glides.
- Best measured glide: **4.0–4.5 m forward from 1.2 m release height →
  glide ratio ≈ 3.3–3.8 (L/D ≈ 3.5).**

**Caveats:** hand-launch kinetic energy inflates the apparent glide ratio;
single measurement; distances by floor tiles / tape measure. Flat-plate
sections and exposed skewers dominate profile drag at this Reynolds
number (~50k), masking the ring's induced-drag advantage.

**Next (Stage 2):** ~1 m span foam build with real airfoil sections,
2 motors + Pixhawk + pitot; measure the full glide polar (sink rate vs
airspeed) motor-off and compare against the VLM + profile-drag estimate.
