# Domain Knowledge Document — HMS Circuit

**Version:** v0.1 (initial draft)
**Date:** 2026-05-18
**Authors:** Duk (domain expertise) + AI advisor (engineering / scientific structure)
**Purpose:** The product's internal "brain" — all SP logic, rules, and explanations derive from this knowledge
**Primary focus:** Coking coal, HMS / Dense Medium Cyclone circuit

> **Markers:**
> `[DUK INPUT NEEDED]` — section requiring Duk's practical expertise
> `[VERIFY]` — written by AI but needs validation against actual plant numbers
> `[VISION]` — long-term vision, Phase 2+

---

## Contents

1. HMS process theory
2. Magnetite media
3. Cyclone mechanics
4. Pump speed × density × flow interactions
5. Ash target → density target logic
6. Feed quality variability
7. Online proxy catalog
8. Shift-to-shift variability drivers
9. Practitioner rules of thumb
10. Safety, abnormal conditions, emergencies

---

## 1. HMS Process Theory

### 1.1 Basic principle
Heavy Media Separation (HMS) is a density-based concentration method. A high-density slurry of magnetite (the "medium") is used to separate coal particles from rock by buoyancy.

- **Light fraction (overflow / float):** particles less dense than the medium → clean coal
- **Heavy fraction (underflow / sink):** particles denser than the medium → refuse

### 1.2 Cut point density (d₅₀)
*d₅₀* is the cut density — the density value at which 50% of particles of that density report to overflow and 50% to underflow.

In practice, the **actual d₅₀** of a cyclone is slightly higher than the medium suspension density (due to the hindered-settling effect inside the cyclone). This offset depends on cyclone diameter, spigot/vortex-finder ratio, and feed pressure.

`[VERIFY]` Document the typical d₅₀ vs medium SG offset observed in your plant's cyclones.

### 1.3 Probable error / Ecart probable (Ep)
A measure of separation sharpness:

$$ E_p = \frac{d_{75} - d_{25}}{2} $$

where d₇₅ and d₂₅ are the densities at which 75% and 25% of feed particles respectively report to underflow.

- **Low Ep** = sharp cut, clean separation (e.g., Ep = 0.02 is excellent)
- **High Ep** = blurred cut, "wrong-place" particles in both products

Typical Ep for coal DM cyclones: **0.02 – 0.05 g/cm³**. `[VERIFY]` Your plant's typical Ep?

### 1.4 Organic efficiency
Actual yield divided by theoretical (washability-derived) yield.
- 95–99% — good
- 90–95% — moderate
- < 90% — issue with cyclone, media, or feed

### 1.5 Bypass and short-circuit
A portion of feed "escapes" separation and reports to the wrong product. In cyclones, some feed can short-circuit directly to overflow or underflow. A high bypass produces a tail on the left side of the partition curve.

### 1.6 Circuit configurations
- **Two-product:** single cyclone, clean coal + reject
- **Three-product:** two-stage circuit producing clean coal + middlings + reject
- **Coking coal common practice:** primary HMS + secondary deshale, or a three-product cyclone (e.g., Larcodems)

`[DUK INPUT NEEDED]` What configuration(s) do your target plants use?

---

## 2. Magnetite Media

### 2.1 Composition and quality standards
- Chemistry: Fe₃O₄ (magnetite)
- Magnetic content: ≥ 90% recoverable on a wet drum
- Pure magnetite SG ~ 5.17, but **operating magnetite** has an effective SG ~ 4.9–5.0 g/cm³
- Typical spec: > 95% magnetite, < 5% gangue

### 2.2 Particle size
- HMS typical: **−45 μm (−325 mesh)** ground magnetite
- Heavy media bath / coarser DMS: −200 μm grades
- Finer is better for suspension stability but harder to recover; coarser is the opposite

### 2.3 Effective suspension density
$$ \rho_{slurry} = \rho_{magnetite} \times C_v + \rho_{water} \times (1 - C_v) $$

where C_v is the volumetric magnetite fraction.

Example: 1.50 g/cm³ medium ≈ 13 vol% magnetite; 1.80 g/cm³ medium ≈ 21 vol%.

### 2.4 Magnetite recovery system
Downstream of the HMS cyclone:
- **Drain & rinse screens** — separate medium from products
- **Magnetic separator** (wet low-intensity drum) — recovers magnetite from the dilute slurry
- **Density tank** — density control and fresh-medium make-up
- **Densifier cyclone** — additional thickening

`[VERIFY]` How is density controlled in your reference plant — manual top-up or automated make-up loop?

### 2.5 Magnetite losses
Loss sources:
- **Adherence loss** — magnetite carried out on coal / refuse particles (gravimetric rinse)
- **Slimes loss** — fine magnetite reporting to overflow of the magnetic separator
- **Spillage** — sumps, line leaks

Typical total loss: **0.5–2 kg/tonne** of feed coal. A "good" target is ≤ 1 kg/tonne.

`[DUK INPUT NEEDED]` Roughly what magnetite cost ($/tonne) do plants you know face? How bad are losses?

### 2.6 Quality degradation
- **Slime** (clay, fine rock) contamination lowers effective magnetite content
- **Over-grinding** produces magnetite too fine to recover magnetically
- **Make-up frequency** depends on feed cleanliness

---

## 3. Cyclone Mechanics

### 3.1 Geometry
Standard DM cyclone components:
- **Inlet** (involute or tangential)
- **Cylindrical section** — upper barrel
- **Conical section** — tapered
- **Vortex finder** — overflow outlet
- **Spigot / apex** — underflow outlet

### 3.2 Key geometric ratios
- D_c (cyclone diameter): typical HMS range **500–1000 mm**, coal commonly 600–800 mm
- D_o / D_c (vortex finder / cyclone): **0.30–0.45**
- D_u / D_c (spigot / cyclone): **0.10–0.25**
- Cone angle: **20° (sharp)** or **70–90° (flat-bottom)** — sharp common for coal

### 3.3 Operating principle
1. Feed enters the inlet tangentially, generating a swirling flow
2. Centrifugal force throws heavy particles to the wall
3. An inner reverse vortex (with an air core) lifts light particles upward
4. Heavies → underflow via spigot
5. Lights → overflow via vortex finder

### 3.4 Vortex finder and spigot — primary wear points

**Vortex finder wear:**
- Inner surface polishes → diameter enlarges → vortex weakens → cut density drops (and blurs)
- Lip erosion at the lower tip → increased bypass
- Typical service life: **`[VERIFY]` your experience** (commonly 1,000–3,000 hours depending on material)

**Spigot wear:**
- Bore enlarges → cut density drops (shifts to lighter side), recovery rises but ash rises with it
- Wears faster than the vortex finder — sees the densest abrasive feed
- Typical service life: **`[VERIFY]` your experience** (commonly 500–1,500 hours)

### 3.5 Liner materials
- **Ceramic (alumina, silicon carbide)** — best abrasion resistance, brittle
- **Rubber-lined** — softer, resilient, heavier
- **Polyurethane** — middle ground, good service life

`[DUK INPUT NEEDED]` Which vortex finder / spigot materials do your reference plants use? What's worked best?

### 3.6 Cyclone diagnostic signals
| Symptom | Likely cause |
|---------|--------------|
| Underflow density drops, product ash rises | Spigot bore worn |
| Cyclone pressure drops abruptly | Vortex finder cracked / damaged |
| Cyclone pressure rises, flow drops | Spigot blockage or feed flow increase |
| "Rope" discharge at underflow | Underflow density too high — spigot near choking |

---

## 4. Pump Speed × Density × Flow Interactions

### 4.1 Centrifugal pump fundamentals
The HMS feed pump is a centrifugal slurry pump. Affinity laws:

- **Volumetric flow (Q)** ∝ rpm
- **Head (h)** ∝ rpm²
- **Power (P)** ∝ rpm³

For high-density slurries:
- Head loss increases relative to clear water (corrected for slurry SG)
- The real-world pump curve must use slurry-corrected affinity

### 4.2 Why pump speed is our SP (not pressure)
Cyclone pressure is the **result** of feed flow + slurry SG. Pump speed is the **input** the operator directly commands. Therefore:

- **SP1: media density** (controlled via magnetite make-up)
- **SP2: pump speed** (rpm or VFD setpoint)
- **PV (monitored): cyclone inlet pressure**

To target a cyclone pressure, you adjust pump speed. To target a density, you adjust make-up and sump dilution.

### 4.3 How density affects the pump
Higher density:
- Lower head at the same rpm (heavier slurry to lift)
- Greater cavitation risk
- Higher pipe wear (especially elbows)

### 4.4 Cavitation
- Adequate NPSH on the suction side is required
- Symptoms: pump noise change, increased vibration, accelerated impeller wear
- Sump level matters: too low → air ingestion

`[DUK INPUT NEEDED]` Any cavitation problems you've seen at plants you know? Root causes?

---

## 5. Ash Target → Density Target Logic

### 5.1 The washability curve
A washability (sink-and-float) test fractionates a coal sample at successive densities and measures the mass and ash of each fraction. Outputs:

- **Cumulative float curve** — yield and ash of all material below a given density
- **Cumulative sink curve** — yield and ash above a given density
- **Elementary ash curve** — ash of each narrow density fraction
- **±0.1 distribution curve** — proportion of near-density material (NDM) around d₅₀

### 5.2 Cut density selection logic
Goal: hit a target product ash% while **maximizing yield**.

Procedure:
1. Take a fresh washability sample (per shift or per shift if feed is unstable)
2. Find the float-cumulative ash corresponding to the target ash%
3. The density at that point is the target d₅₀
4. Set actual medium SG slightly below the d₅₀ to account for the cyclone's hindered-settling offset

### 5.3 NDM (near-density material)
- The proportion of feed within ±0.1 g/cm³ of d₅₀
- NDM > 25% → **difficult** separation; Ep must be tight
- NDM < 10% → easy separation; loose Ep is fine

`[VERIFY]` Typical NDM for your reference feed?

### 5.4 Yield–ash trade-off
Raising density by 0.02 g/cm³ → yield increases by ~1–3% (more coal saved), but ash by 0.3–0.8% `[VERIFY]`.

Business logic: marginal coal value (price × yield gain) vs ash-penalty (rejection or contract clauses).

### 5.5 Two operating modes
- **Yield-priority:** maximize yield, with ash as a soft constraint (flexible customer)
- **Ash-priority:** ash target is hard; take whatever yield comes (contract-bound supply)
- The system UX must let the operator switch modes

---

## 6. Feed Quality Variability

### 6.1 Sources of variability
- **Multiple seams** — different ash and mineralogy
- **Mine progression** — variability within a seam over time
- **Sub-feeder discipline** — how ROM stockpile is reclaimed
- **Moisture** — wet season, mine water, stockpile drainage
- **Particle size** — crushing condition, screen wear

### 6.2 Key variability parameters
| Parameter | Typical swing | Effect on model |
|-----------|---------------|------------------|
| Feed total ash% | ±3–7% | Shifts cut-density selection |
| Feed tonnage / hr | ±10–20% | Changes cyclone pressure |
| Top size | −50 mm vs −25 mm | Conveyance, cyclone capacity |
| Fines (< 0.5 mm) | 5–25% | Magnetite loss ↑ |
| Moisture | 5–12% | Crushing, volume |
| NDM (±0.1) | 8–30% | Ep requirement |

### 6.3 How to detect variability
- **Belt scale + regular sampling** — feed rate and ash
- **Online ash analyzer** (PGNAA, dual-energy γ-transmission) — gold standard if available
- **Visual / operator-flagged feed change** — capture in shift log
- **Lab samples: per-shift baseline + ad-hoc upset samples**

`[DUK INPUT NEEDED]` From your experience: how do sudden feed changes show up — what do operators notice?

---

## 7. Online Proxy Catalog

With lab ash arriving ~12 hours late, the SP engine must run on **online signals**. Practical proxies:

### 7.1 Directly measured (PLC tags)
| Tag | What it measures | Used for |
|-----|------------------|----------|
| Media density (γ-density gauge / U-tube) | Cyclone feed SG | Primary SP, real-time |
| Cyclone inlet pressure | Feed pressure | Combined flow + SG signal |
| Feed flow (mag-flow) | Volumetric flow | Throughput |
| Pump speed (VFD %) | Rotational speed | SP2 |
| Pump motor current | Pump load | Proxy for slurry SG |
| Underflow density (if measured) | Underflow SG | Spigot wear indicator |
| Overflow density (if measured) | Product SG | Vortex finder wear indicator |
| Magnetic separator current | Magnetite circulation state | Loss reduction |
| Sump level | Feed buffer | Cavitation risk |

### 7.2 Computed proxies
| Proxy | Computation | What it reveals |
|-------|-------------|------------------|
| **Differential pressure / density ratio** | ΔP / ρ | Unstable medium or air-core change |
| **Volumetric load** | Q × ρ | True throughput |
| **Pump–density consistency** | Deviation from (rpm, flow, pressure) model | Mechanical issues |
| **Vortex/spigot gap** | Δ between overflow and underflow density | Wear detection |

### 7.3 Example proxy-based logic
- **"Cyclone pressure dropped 8%+ steadily over 5 minutes with flow constant"** → likely vortex finder damage → maintenance alert
- **"Underflow density fell 0.05 g/cm³ over 24 hours, feed unchanged"** → spigot wear → schedule replacement
- **"Pump current up, flow down"** → pipe blockage or impeller wear

`[DUK INPUT NEEDED]` What other proxies have you relied on from experience?

---

## 8. Shift-to-Shift Variability Drivers

### 8.1 Main drift sources
1. **Operator habit** — one operator runs media 0.02 heavier "to be safe," another runs yield-priority
2. **Shift handover** — setpoint changes that don't get communicated
3. **Feed variability** — new stockpile opens, sub-feeder changes
4. **Magnetite make-up discipline** — one shift adds enough, the next under-adds
5. **Lab sampling timing** — morning vs evening samples
6. **Equipment wear** — interpreted differently by each shift
7. **Cultural conventions** — "we always raise density at night" type rules

### 8.2 System's role here
- Provide **consistent recommendations** across shift handover
- Anchor density target to **feed quality numbers** (not human style)
- Maintain a **decision log** between shifts — "what was tried last shift, what happened"

---

## 9. Practitioner Rules of Thumb

> **This section is where your 20 years of experience become the product's true value.** The below are placeholder templates; you fill them. We're framing each rule as "**if … then …**" — if we add ML later, these rules become initial feature engineering.

### 9.1 Density tuning (placeholder templates — you fill)
- `[DUK INPUT NEEDED]` If feed ash rises by 2%, raise media density by ____ g/cm³
- `[DUK INPUT NEEDED]` If feed moisture rises by 2%+, do ____
- `[DUK INPUT NEEDED]` After a new ROM seam is opened, hold an overdose strategy for the first ____ hours

### 9.2 Cyclone and equipment
- `[DUK INPUT NEEDED]` "Sufficient" vortex finder wear is when pressure drops by ____ %
- `[DUK INPUT NEEDED]` Signs of accelerated spigot wear: ____
- `[DUK INPUT NEEDED]` Replace pump impellers at ____ hours, or when ____

### 9.3 Magnetite
- `[DUK INPUT NEEDED]` Minimum healthy make-up rate (kg/tonne coal): ____
- `[DUK INPUT NEEDED]` Threshold for "magnetite loss too high": ____
- `[DUK INPUT NEEDED]` How to detect slime contamination: ____

### 9.4 Feed
- `[DUK INPUT NEEDED]` Top-size change of ____ reduces cyclone throughput by ____
- `[DUK INPUT NEEDED]` What to do when feed fines % is high: ____

### 9.5 Other
- `[DUK INPUT NEEDED]` Your standard list of "becoming suspicious" conditions

> We'll **keep extending this section**. Just jot a rule when one comes to mind — partial numbers are fine, we'll sharpen them later.

---

## 10. Safety, Abnormal Conditions, Emergencies

### 10.1 Density runaway
**Density too low** (medium lost, water added):
- No separation → all feed reports to overflow → product ash spikes
- Detection: density sensor drops 0.05+ below SP, ash rises

**Density too high** (over-added magnetite, water lost):
- Cyclone "rope" discharge → spigot choke
- Pressure ↑↑, flow ↓
- Risk of circuit trip

### 10.2 Pump choke
- Sump level low → air ingestion, cavitation, unstable operation
- Pump current spike → blockage or broken impeller

### 10.3 Magnetite shortage
- Magnetite sump runs dry → cannot meet density target
- Solution: emergency stockpile, "magnetite low" alarm upstream of density tank

### 10.4 Cyclone blockage
- Oversize particles enter the inlet → flow disrupted
- Mitigation: top-size control on feed screen, inlet right-flow geometry

### 10.5 Feed loss
- ROM supply stops → cyclone feed dries up
- Conveyor trip, sub-feeder cut-off
- Never run the pump empty for long

### 10.6 Power outage
- HMS shutdown priority: cyclone feed pump → media pump → screens last
- Restart sequence is strict: screens → media circuit → feed pump

### 10.7 Overflow flooding
- Sump overfills → spills on floor → magnetite loss, environmental issue
- High-level interlock on sump is mandatory

### 10.8 System's role
Core principle: we only **notify and warn**. Safety logic stays in the PLC. Our system:
- Issues alerts like "Density runaway risk — check density tank" when a threshold is crossed
- Logs every abnormal condition for postmortem analysis

`[DUK INPUT NEEDED]` What's the most common emergency you've seen at plants you know?

---

## 11. Glossary

| Term | Definition |
|------|------------|
| HMS / DMS | Heavy Media Separation / Dense Medium Separation |
| d₅₀ | Cut point density |
| Ep | Probable error (separation sharpness) |
| NDM | Near-density material (% within ±0.1 g/cm³ of d₅₀) |
| Vortex finder | Cyclone overflow outlet tube |
| Spigot (apex) | Cyclone underflow outlet |
| Magnetite | Fe₃O₄, primary media material |
| Make-up | Adding fresh magnetite to compensate loss |
| Rope discharge | Underflow "rope" pattern — sign of over-dense underflow |
| Spray discharge | Underflow spray pattern — normal density |
| Bypass | Particles that escape separation |
| Washability | Density-yield-ash characterization test |
| ROM | Run-of-Mine (uncrushed mined coal) |

---

## 12. Next Steps

- Fill in the `[DUK INPUT NEEDED]` sections — that's where your 20 years go
- Once we have real plant data, replace `[VERIFY]` markers with actual numbers
- This document feeds the upcoming **Data Specification** (which PLC tags, lab fields, calculations)
- Phase 1 SP recommendation engine will draw its logic directly from §5, §7, §9

---

## 13. Version History

| Version | Date | Change |
|---------|------|--------|
| v0.1 | 2026-05-18 | Initial draft — structure + general knowledge + Duk input markers |
