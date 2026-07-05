# Span efficiency of elliptical closed lifting systems with a loaded central body

Research project for a paper (target: Zenodo preprint + Journal of Emerging
Investigators / NHSJS submission). Author: Somesh Parganiha.

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

## Extended results (`run_extended.py`)

- **Superellipse family** |y/a|^p + |z/c|^p = 1 bridges ellipse (p=2) and
  box (p→∞). Benefit capture rises steeply then saturates: p=4 captures
  ~73–76% of the box benefit over planar, p=6 ~83–85%, p=12 ~93%.
  A gently squared "squircle" ring buys most of the box-wing gain.
- **Cabin height placement** (ellipse h/b=0.3, 15% lift share): the penalty
  curve is a symmetric U — **mid-height is the worst place** to carry lift
  (e=1.145); hugging the lower or upper arc is cheapest (e=1.226 at
  z/h=0.1). Design rule: blend the cabin into an arc, don't suspend it.
- **e = 1 + h/b law** (ellipse): max deviation 7.9e-4 at n=1536, shrinking
  with resolution and vanishing at the circle — consistent with an exact
  relation. Candidate for analytical proof (elliptic coordinates).
- **Design point**: p=4 squircle, h/b=0.5, cabin at z/h=0.15 carrying 15%
  of lift: **e = 1.61** — a 38% induced-drag cut vs an ideal planar wing,
  with realistic cabin loading included.

## Finite-chord cross-check (`run_vlm.py`)

Horseshoe-vortex VLM (Katz & Plotkin) on the same trace geometries, with
strip circulations evaluated by the same Trefftz functionals as the ideal
results. Validation gates: elliptical-planform AR=8 wing gives 99.9% of
same-grid ideal and CL_alpha=4.80/rad (Helmbold 5.03); Kutta-Joukowski vs
Trefftz lift agree to 0.4%; chordwise-resolution independent to 2e-4.

Result (144 strips, c/b=0.1, alpha=5 deg): **untwisted rings already
achieve 98.6-100% of the ideal efficiency** (circle: exactly optimal by
symmetry -- uniform incidence imposes Munk's criterion in near-field
form), and **< 1 degree of twist recovers the rest** (ellipse 0.76 deg,
superellipse p=4 0.63 deg). Chord sensitivity mild: 97.9-99.7% of ideal
across c/b = 0.05-0.20. So the Trefftz bounds are practically attainable.

## Robustness / red-team pass (`run_robustness.py`)

- Kernel bias is cleanly first-order (planar bias halves per grid
  doubling, ratio 2.00); production-resolution absolute e biased < +0.3%,
  same-grid ratios unaffected.
- e = 1 + h/b: deviation halves with n; Richardson extrapolation -> 1e-6.
  Effectively exact. Novelty caveat added: closed-form annular-wing
  analyses (Cone 1962; Demasi, J. Aircraft 2007) may contain it — check
  before submission.
- Superellipse corners converged (p=12: Δe = 1.6e-4 across 8x grids).
- Cabin conclusions robust to spine width (0.3–0.7b, ordering preserved).
  NEW finding: wider body = much cheaper lift (f=0.2 mid-height: e 0.88 at
  0.3b vs 1.23 at 0.7b) -> second design rule "if it must lift, make it wide".
- VLM untwisted near-optimality survives 0.5b stagger (99.1% -> 98.1%,
  twist-opt still 100% with 2.1 deg).

## Files

- `trefftz.py` — solver (geometries: planar, box, ellipse, ellipse+spine)
- `vlm.py` — finite-chord vortex-lattice method (shares Trefftz functionals)
- `run_study.py`, `run_extended.py`, `run_vlm.py` — validation, sweeps, figures
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

## Reproducing everything

```
pip install -r requirements.txt
python run_study.py        # validation + box/ellipse sweep + spine lift share
python run_extended.py     # superellipse family + cabin height + law test
python run_vlm.py          # finite-chord VLM gates + ring cross-check
python run_robustness.py   # grid convergence, Richardson, width/stagger checks
```

All results are deterministic; the four scripts regenerate every number and
figure in the paper. Compile the manuscript with `tectonic paper/main.tex`
(or upload `paper/` to Overleaf).

## Licensing and citation

Code and data: MIT (see LICENSE). Manuscript and figures: CC BY 4.0.
Cite via CITATION.cff (add the GitHub URL and Zenodo DOI after release).

## AI-assistance disclosure

The author conceived and directed this work, studied the underlying theory,
reproduced and verified all results, and is responsible for the final
manuscript. In support of that work, Anthropic's Claude served as a tutor
for the theory and provided assistance with the numerical implementation
and an initial manuscript draft, prepared under the author's direction and
subsequently reviewed and revised by the author. Venue policies on AI assistance vary
sharply — JEI in particular prohibits AI-conducted modelling and writing —
so venue fit must be checked before any journal submission.

## Integrity notes

- Methods must be fully understood and defensible by the author.
- Disclose AI assistance per venue policy; check each venue's AI rules
  BEFORE submitting (they differ drastically).
- No pay-to-publish venues.
