# Stage 2 checklist — 1 m powered Vyoma demonstrator

Tick top to bottom. Bold items are gates: do not pass without them.

## Phase 0 — before spending money
- [ ] Re-read STAGE2.md; re-run `python stage2_sizing.py` (numbers current?)
- [ ] **Ask a physics teacher / professor to be mentor + senior author**
- [ ] Register on DGCA Digital Sky portal (micro class, 250 g–2 kg)
- [ ] Pick the flying field (open, green-zone, no people/wires, <60 m ops)
- [ ] Confirm owned gear works: Pixhawk 6C, GPS, RC TX/RX, telemetry, charger
- [ ] Decide airfoil (thin 6–8% cambered low-Re section) — print templates

## Phase 1 — procurement (~₹9–13k)
- [ ] Depron/EPP foam sheets 5 mm (+1 spare sheet)
- [ ] Carbon rods: 4 mm (ring spar) + 6 mm (spine); thin ply scraps
- [ ] 2 × 2212-class motors (~1400 kV), 2 × 20 A ESC
- [ ] Props 7–8" — one CW + one CCW (plus 2 spares each)
- [ ] 3S 1300–1500 mAh LiPo (+LiPo-safe bag)
- [ ] 2 × 9 g servos + pushrods/horns
- [ ] **Digital airspeed sensor (pitot tube kit)** — the science instrument
- [ ] Foam-safe glue (UHU POR/hot glue), fibre tape, velcro straps

## Phase 2 — build: glider first (NO motors yet)
- [ ] Cut ring facets with airfoil section; assemble squircle, 15 cm stagger
- [ ] Spar the loop; spine along bottom-wing chord; elevons cut + hinged
- [ ] Weigh it; update `stage2_sizing.py` mass table with real grams
- [ ] Compute CG target from updated run; mark it on the spine
- [ ] Ballast to CG (battery-position first, clay only for trim)
- [ ] **Hand-glide test: repeatable straight flat glides before continuing**
- [ ] Log Stage-2-glider results in FLIGHTLOG.md

## Phase 3 — add power (manual RC only)
- [ ] Motor mounts on upper arc; motors, ESCs, battery in; re-balance CG
- [ ] Range check TX/RX; control throws set; elevon directions verified
- [ ] **Taxi/hand-launch at 1/3 throttle first flight — climb-out stable?**
- [ ] Trim for straight powered flight; note throttle for level cruise
- [ ] Crash kit packed: glue, tape, spare props, spare foam

## Phase 4 — instrument it
- [ ] Pixhawk in (ArduPlane, ELEVON config); servos + ESCs through FC
- [ ] Pitot mounted clear of prop wash (nose boom); airspeed calibrated
- [ ] Telemetry to Mission Planner (the mavp2p chain); logging at 10+ Hz
- [ ] FBWA mode test flight; failsafe (RTL/throttle-cut) verified

## Phase 5 — the experiment (calm morning air)
- [ ] Sawtooth glides: climb → throttle cut → hold steady V → repeat
- [ ] Speeds: ~7, 8, 9, 10, 12 m/s — 3+ good glides per speed
- [ ] Pull logs; compute sink rate + L/D per glide
- [ ] **Plot measured polar over stage2_predicted_polar.png**
- [ ] Repeat on a second day (repeatability check)
- [ ] All data + analysis script committed to repo

## Phase 6 — paper #2
- [ ] Student writes full draft (AI = tutor/proofread only, per JEI policy)
- [ ] Mentor reviews; both sign off on data integrity
- [ ] Figures: build photos, polar comparison, method diagram
- [ ] Submit to JEI (before university enrollment); log submission date
- [ ] Update MIT application materials with the result

## Standing rules
- Predict before you measure; log every flight in FLIGHTLOG.md same day
- One change at a time between flights
- Battery charged = flight day; LiPo storage-charge otherwise
- If a gate item fails, fix it before moving on — no gate-skipping
