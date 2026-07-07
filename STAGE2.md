# Stage 2 — the 1 m powered Vyoma demonstrator

Goal: measure the **glide polar** (L/D and sink rate vs airspeed) of a
real, airfoiled ring wing and compare it against the vortex-lattice +
profile-drag prediction. This is the experiment behind **paper #2**, which
— unlike the Zenodo preprint — is designed to be the author's own work
(AI as tutor only), suitable for JEI with a mentor as senior author.

## Predicted spec (from `stage2_sizing.py` — verify by flight)

| Quantity | Prediction |
|---|---|
| Span / height / chord | 1.00 m / 0.50 m / 0.10 m (p=4 squircle, h/b=0.5) |
| All-up mass | ~550 g |
| Wing loading | ~30 N/m² (3.1 kg/m²) — gentle, forgiving |
| Stall speed | ~7 m/s (25 km/h) |
| Cruise speed | ~9 m/s (33 km/h) |
| Cruise Reynolds no. | ~60,000 (low-Re airfoil territory) |
| CG | ~1.5 cm ahead of the neutral point (10% margin) |
| **Predicted best L/D** | **11 (rough build) to 16 (clean build)** |
| Thrust needed | ~50 gf cruise; ~190 gf per motor for lively climb |

The predicted glide polar is `stage2_predicted_polar.png`. Stage 0 cardboard
measured L/D ≈ 3.5; real airfoil sections should roughly triple it — that
jump is the headline the flight test either confirms or corrects.

## Parts list (~₹9,000–13,000)

**Airframe (~₹800)**
- 5 mm depron / EPP foam sheets (low-Re friendly), or 3D-printed rib+skin
- 4 mm carbon rod (ring spar), 6 mm for spine, thin ply for motor mounts
- foam-safe glue (UHU POR / hot glue), fibre tape

**Propulsion (~₹3,500)**
- 2 × ~1400 kV brushless motors (e.g. 2212 class), ~200+ gf thrust each
- 2 × 20 A ESC, 2 × 7–8" props (one CW, one CCW to cancel torque)
- 3S 1300–1500 mAh LiPo + charger (if not owned)

**Avionics — mostly owned already (~₹2,500 new)**
- Pixhawk 6C (owned), GPS (owned), RC receiver + transmitter (owned?)
- **digital airspeed sensor (pitot + MS4525/analog)** — the key instrument
- 2 × 9 g servos for elevon/morph surfaces cut into the arcs
- telemetry radio (owned — the mavp2p / Mission Planner chain)

**Airfoil note:** at Re ≈ 60k, thick airfoils stall early. Use a **thin
(~6–8%) cambered low-Re section** (e.g. AG- or S-series style) or a simple
flat-bottom Clark-Y-ish curve. This is the single biggest jump from the
flat cardboard plates.

## Build stages (each flies before the next is added)

1. **Glider first (no motors).** Foam ring with real airfoil sections,
   spar, spine, elevons, CG at prediction. Hand-glide and trim exactly like
   Stage 0. Confirms the airfoil + CG before risking motors.
2. **Add propulsion.** Two motors on the upper arc, conventional throttle.
   Fly under manual RC. Confirm powered climb and control.
3. **Add the Pixhawk + pitot.** ArduPlane, elevon mixing, airspeed
   calibrated. Fly a few circuits; log airspeed + baro altitude.
4. **(Optional, later) differential-thrust control** — the concept's
   signature. Only after the airframe is fully trusted.

## The measurement (paper #2's data)

**Glide polar by the sawtooth-glide method:**
- Climb to safe altitude under power, then **cut throttle** and hold a
  steady glide at a fixed airspeed; repeat at several airspeeds
  (e.g. 7, 8, 9, 10, 12 m/s).
- ArduPlane logs airspeed and barometric altitude at 10+ Hz. For each
  steady glide, sink rate = d(altitude)/dt; L/D = V_horizontal / sink.
- Each glide → one polar point. The curve of L/D vs V is the aircraft's
  efficiency fingerprint — measured, then overlaid on the predicted band.

**Deliverable:** measured polar vs `stage2_predicted_polar.png`. Whether it
lands near the clean or rough bound (or misses both), the honest comparison
IS the paper.

## Legal (India, DGCA)

Keep all-up mass **under 250 g? no** (too small to instrument) — target the
**"micro" class (250 g–2 kg)**: register on the **Digital Sky** portal, fly
below 60 m AGL in uncontrolled/green-zone airspace (open fields, away from
airports), daylight, VLOS. Same rules the owner's existing drone flies
under. No remote-pilot licence needed for micro in the green zone.

## Paper #2 outline (JEI-eligible)

1. Intro — closed wings, the Zenodo preprint's predictions, the gap
   (ideal vs achieved at real Reynolds numbers)
2. Methods — the demonstrator, airfoil, instrumentation, sawtooth-glide
   protocol; **prediction from VLM + profile drag (this repo)**
3. Results — measured glide polar vs predicted band
4. Discussion — where and why they agree/differ (Re, junctions, build)
5. Conclusion + future work
Author: Somesh Parganiha (student) + mentor (senior author). AI: tutor only.

## Prediction-first discipline

Everything above is a **prediction to be tested**, generated before the
build — the same loop Stage 0 validated (predicted CG 7.5–8 cm → measured
"about the same"). Re-run `python stage2_sizing.py` after any design change.
