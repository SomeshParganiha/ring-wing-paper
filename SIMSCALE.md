# Running the Vyoma prototype on SimScale

Files: `vyoma.stl` (ring + cabin) and `vyoma_ring_only.stl` (fallback if
the two-body model gives meshing trouble). Full scale, metres.
Regenerate anytime with `python gen_stl.py`.

## 1. Account and upload

1. Create a free Community account at simscale.com (community plan =
   public projects, cloud compute included).
2. Dashboard -> New Project -> name it `vyoma-ring-wing`.
3. Import geometry -> upload `vyoma.stl` -> units **metres**.

## 2. Simulation setup (virtual wind tunnel)

- Create Simulation -> **Incompressible** (k-omega SST turbulence).
  We test at 60 m/s (Mach 0.18), so incompressible is valid; compressible
  cruise CFD can come later.
- **Flow region (External Flow Volume / enclosure)**, model at origin:
  - upstream (-x): 100 m, downstream (+x): 250 m
  - sides (+-y): 100 m each, below/above (z): 60 m / 100 m
- **Boundary conditions**:
  - Inlet (front face): velocity inlet, u = (59.77, 0, 5.23) m/s
    (= 60 m/s at 5 deg angle of attack — tilting the flow instead of the
    model keeps the setup simple)
  - Outlet (rear face): pressure outlet, 0 Pa gauge
  - All four side faces: slip walls
  - Aircraft surfaces: no-slip wall
- **Mesh**: Standard mesher, fineness ~5-6/10, add a region refinement
  box around the aircraft and one downstream (wake), surface refinement
  on the aircraft, 3 inflation (boundary) layers, y+ target 30-300
  (wall functions). Expect roughly 4-8 M cells — fine for the free plan.
- **Result control -> Forces and moments** on all aircraft surfaces:
  - reference area S = 345 m^2, reference length = 3.6 m,
    velocity 60 m/s, density 1.225 kg/m^3
- Steady-state, ~1000 iterations. Watch the force residuals flatten.

## 3. What to look at (and what would falsify the paper)

1. **Slice the wake** (post-processor: velocity slice ~2 spans behind):
   a conventional wing shows two concentrated tip-vortex cores; the ring
   should show a diffuse vorticity band around the loop trace instead.
   This is the whole thesis made visible.
2. **Surface pressure**: suction (blue/low pressure) on the outer-upper
   faces of both arcs; the loading should fade near the side arcs,
   qualitatively matching `optimal_loading_ring.png`.
3. **CL**: from the force report, CL = Fz / (0.5 * 1.225 * 60^2 * 345).
   Ballpark from our VLM at 5 deg: ~0.35-0.45. Same order = healthy.
4. **Drag caveat**: RANS drag = friction + induced combined; do NOT
   compare the raw CD against the paper's induced-only numbers. The
   meaningful CFD experiment is *relative*: run a planar wing of equal
   span and area at matched CL and compare total drag.

## 4. Known simplifications of this STL

- Cabin floats 0.7 m below the ring (no pylons/blend) for robust
  meshing; fine for a first look, not for junction-flow conclusions.
- No fans, no morphing surfaces, constant chord, NACA 0012 everywhere,
  no twist. It answers "does the closed loop diffuse the wake as
  predicted", nothing more.
