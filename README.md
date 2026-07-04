# Span efficiency of elliptical closed lifting systems with a loaded central body

Research project for a paper (target: Zenodo preprint + Journal of Emerging
Investigators / NHSJS submission). Author: Harshwardhan Parganiha.

## Research question

Closed ("box") wings are known since Prandtl (1924) to reduce induced drag.
Ring-wing aircraft concepts place the cabin as a lifting body *inside* the
ring. Two questions nobody has published numbers for together:

1. How does an **elliptical** closed wing compare with the rectangular box
   wing at equal height-to-span ratio?
2. What is the induced-drag **cost of forcing the central cabin body to
   carry lift**, as a function of its lift share?

## Method

Trefftz-plane minimum-induced-drag analysis (Munk). The wake trace is
discretised into panels of piecewise-constant circulation shedding 2-D point
vortices; induced drag is a quadratic form in the circulations, minimised
subject to lift-equality constraints via a KKT system. See `trefftz.py`.

## Validation (run `python run_study.py`)

| Case | Computed | Classical |
|---|---|---|
| Planar wing | 1.0031 | 1.0000 (Munk 1921) |
| Box wing, h/b = 0.2 | 1.4721 (converged n=64→512) | ≈1.46 (Prandtl 1924) |
| Circular ring wing | 2.0000 (4 digits) | 2.0 (classical) |

## Key results so far

- Elliptical ring follows **e ≈ 1 + h/b** across the whole sweep (matches
  the exact circular-ring value 2.0 at h/b = 1). Worth stating as a
  numerically-supported conjecture — possibly provable.
- The box wing beats the ellipse at every h/b (consistent with Prandtl's
  "best wing system"), e.g. 1.66 vs 1.30 at h/b = 0.3.
- Loading the central spine is always an efficiency penalty, mild below
  ~10% lift share, steep beyond: at h/b = 0.3, e falls 1.30 → 1.14 at 20%
  spine lift and below the planar wing (< 1.0) at ~30%.

## Files

- `trefftz.py` — solver (geometries: planar, box, ellipse, ellipse+spine)
- `run_study.py` — validation, sweeps, figures
- `results_sweep.csv`, `results_spine.csv` — data
- `efficiency_vs_hb.png`, `spine_penalty.png`, `optimal_loading_ring.png`

## Paper outline

1. Introduction — induced drag, closed wings, ring-wing concepts
2. Method — Trefftz plane, discretisation, constrained optimisation
3. Validation — the three classical targets above + convergence study
4. Results — e(h/b) for box vs ellipse; spine lift-fraction penalty
5. Discussion — design implication: cabin should be unloaded or nearly so;
   e ≈ 1 + h/b conjecture; limits (inviscid, optimal loading, rigid wake)
6. Future work — VLM with finite chord + trim; subscale flight demonstrator

## Integrity notes

- Methods must be fully understood and defensible by the author.
- Disclose AI assistance per venue policy.
- No pay-to-publish venues.
