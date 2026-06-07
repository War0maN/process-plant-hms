# Open-Items Checklist — Process Plant Docs

**Generated:** 2026-05-22 · by Claude
**Purpose:** A single to-do list of every unanswered `[DUK INPUT NEEDED]`, `[VERIFY]`, and `[CLARIFY]` marker across the project docs, so nothing gets missed.
**How to use:** Tick a box when the item is resolved in the source doc. This file is a tracker — the real answers go back into docs 02 and 03.

---

## Summary

| Document | `[DUK INPUT NEEDED]` | `[VERIFY]` | `[CLARIFY]` | Total open |
|----------|:---:|:---:|:---:|:---:|
| 02 — Domain Knowledge (EN) | 19 | 7 | 0 | **26** |
| 02 — Domain Knowledge (MN) | 2 | 3 | 0 | **5** |
| 03 — Plant Profile (MN) | 40 | 1 | 2 | **43** |
| 01 — MVP Scope (EN / MN) | 0 | 0 | 0 | 0 |

> **Drift flag.** The English domain doc carries **26** open markers; the Mongolian one only **5**. The two versions are out of sync — the EN doc's whole §9 "Rules of Thumb" placeholder block (12 items) does not appear as markers in the MN version. Worth a proper section-by-section sync pass.

---

## 1. Doc 02 — Domain Knowledge (EN) — 26 items

### Process theory & cyclones

- [ ] **§1.2** `[VERIFY]` — Typical d₅₀ vs medium SG offset observed in your plant's cyclones
- [ ] **§1.3** `[VERIFY]` — Your plant's typical Ep (probable error)
- [ ] **§1.6** `[DUK]` — Which circuit configuration(s) do your target plants use (two-product / three-product)?
- [ ] **§3.4** `[VERIFY]` — Vortex finder service life (your experience, vs the 1,000–3,000 h reference)
- [ ] **§3.4** `[VERIFY]` — Spigot service life (your experience, vs the 500–1,500 h reference)
- [ ] **§3.5** `[DUK]` — Which vortex finder / spigot materials do your reference plants use, and what's worked best?

### Magnetite & media

- [ ] **§2.4** `[VERIFY]` — How is density controlled in your reference plant — manual top-up or automated make-up loop?
- [ ] **§2.5** `[DUK]` — Rough magnetite cost ($/tonne) and how bad losses get

### Pumps

- [ ] **§4.4** `[DUK]` — Any cavitation problems you've seen, and root causes

### Ash → density logic

- [ ] **§5.3** `[VERIFY]` — Typical NDM (near-density material) for your reference feed
- [ ] **§5.4** `[VERIFY]` — Yield/ash trade-off numbers (the ~1–3% yield / 0.3–0.8% ash per 0.02 g/cm³ figures)

### Feed variability & proxies

- [ ] **§6.2** `[DUK]` — How do sudden feed changes show up — what do operators notice?
- [ ] **§7.3** `[DUK]` — What other online proxies have you relied on from experience?

### §9 — Practitioner Rules of Thumb — highest-value items ("your 20 years")

- [ ] **§9.1** `[DUK]` — If feed ash rises 2%, raise media density by ___ g/cm³
- [ ] **§9.1** `[DUK]` — If feed moisture rises 2%+, do ___
- [ ] **§9.1** `[DUK]` — After a new ROM seam opens, hold an overdose strategy for the first ___ hours
- [ ] **§9.2** `[DUK]` — "Sufficient" vortex finder wear = pressure drops by ___ %
- [ ] **§9.2** `[DUK]` — Signs of accelerated spigot wear: ___
- [ ] **§9.2** `[DUK]` — Replace pump impellers at ___ hours, or when ___
- [ ] **§9.3** `[DUK]` — Minimum healthy make-up rate (kg/tonne coal): ___
- [ ] **§9.3** `[DUK]` — Threshold for "magnetite loss too high": ___
- [ ] **§9.3** `[DUK]` — How to detect slime contamination: ___
- [ ] **§9.4** `[DUK]` — Top-size change of ___ reduces cyclone throughput by ___
- [ ] **§9.4** `[DUK]` — What to do when feed fines % is high: ___
- [ ] **§9.5** `[DUK]` — Your standard list of "becoming suspicious" conditions

### Safety

- [ ] **§10.8** `[DUK]` — Most common emergency you've seen at plants you know

---

## 2. Doc 02 — Domain Knowledge (MN) — 5 items

These are the only markers still open in the Mongolian version. (See drift flag above — the MN doc is missing most of the EN doc's markers.)

- [ ] **§1.2** `[VERIFY]` — Cyclone d₅₀ vs media SG offset (draft guess in doc: ~0.002)
- [ ] **§1.3** `[VERIFY]` — Plant's typical Ep value
- [ ] **§2.4** `[VERIFY]` — Density control: manual top-up vs automated make-up loop
- [ ] **§7.3** `[DUK]` — Other proxies relied on from experience
- [ ] **§10.x** `[DUK]` — Most common emergency condition seen

---

## 3. Doc 03 — Plant Profile (MN) — 43 items (8 resolved in v0.2 ✅)

### §1 — Plant identification (5) — ✅ done

- [x] Plant name → CHPP — Coarse circuit
- [x] Location → Ömnögovi
- [x] Owner → MMC
- [x] Commissioning year → 2011
- [x] Nameplate capacity → 900 t/h

### §2 — Beneficiation scheme (1)

- [ ] How many cyclones run in parallel per stage (module/block count)? Pre-desliming/screens and crusher count? *(Duk note: see image.png, image-1.png, image-2.png — equipment list + flow diagram)*

### §3 — Cyclone geometry (1 `[CLARIFY]`)

- [ ] `[CLARIFY]` — D_o/D_c and D_u/D_c ratios come out higher than the universal 0.30–0.45 / 0.10–0.25 reference. Confirm whether the figures are inner diameters and are correct. *(Duk has partly responded: "doing it per theory is correct" — needs finalizing; see image-3.png, image-4.png for cyclone dimensions)*

### §4 — Mass balance / feed rate (2 `[DUK]` + 1 `[CLARIFY]`)

- [ ] **§4.2** `[DUK]` — Overflow Solids R.D. (Primary) — *Duk wrote "I don't really understand what to do here" → needs a walk-through*
- [ ] **§4.2** `[DUK]` — Overflow Medium R.D. (Primary) — *same: Duk flagged confusion here*
- [x] `[CLARIFY]` — Meaning of "Solids R.D." vs "Medium R.D." columns → definition integrated into §4 (v0.2)

### §5 — Size range (2) — ✅ done

- [x] Lower limit (<1.2 mm) → TBS (−1.2+0.25 mm) and flotation (−0.25 mm) — integrated into §5 (v0.2)
- [x] Upper limit (>50 mm) → +50 mm ≤5% rule, not re-crushed — integrated into §5 (v0.2)

### §6 — Media density & operating range (2 `[DUK]` + 1 `[CLARIFY]`)

- [ ] `[DUK]` — Density operating range (min/max)
- [ ] `[DUK]` — Density measurement method (γ-density gauge / U-tube / other)
- [ ] `[CLARIFY]` — Reconcile §1.1's 1.30–1.35 g/cm³ working density against §4's feed medium R.D. of 1.5, per Primary vs Secondary. **Critical — this is the core SP-logic input.** *(Duk note in §4.1: Primary density gauge typically reads 1.3–1.36, Secondary 1.48–1.55)*

### §7 — Magnetite (3 `[DUK]` + 1 `[VERIFY]`)

- [ ] `[DUK]` — Magnetic quality (% magnetically recoverable)
- [ ] `[DUK]` — Supplier / source
- [ ] `[DUK]` — Price ($/tonne)
- [ ] `[VERIFY]` — Is 600 g/t a stable consumption figure?

### §8 — Media recovery system (1)

- [ ] `[DUK]` — Number and size of magnetic separators; is density-tank make-up automatic or manual? (currently assumed manual)

### §9 — Pumps (8 — 4 fields × Primary/Secondary)

- [ ] Pump model / manufacturer — Primary
- [ ] Pump model / manufacturer — Secondary
- [ ] Motor power (kW) — Primary
- [ ] Motor power (kW) — Secondary
- [ ] Speed control method (VFD?) — Primary
- [ ] Speed control method (VFD?) — Secondary
- [ ] Working rpm range — Primary
- [ ] Working rpm range — Secondary

### §10 — Instrumentation & PLC tags (12) — *flagged "most important" in the doc*

- [ ] Media density (Primary) — measured? PLC tag?
- [ ] Media density (Secondary) — measured? PLC tag?
- [ ] Cyclone inlet pressure (Primary) — measured? PLC tag?
- [ ] Cyclone inlet pressure (Secondary) — measured? PLC tag?
- [ ] Feed flow — measured? PLC tag?
- [ ] Pump speed (VFD %) — measured? PLC tag?
- [ ] Pump motor current (A) — measured? PLC tag?
- [ ] Sump level — measured? PLC tag?
- [ ] Magnetic separator current — measured? PLC tag?
- [ ] Belt scale (feed t/h) — measured? PLC tag?
- [ ] Online ash analyzer — present? PLC tag?
- [ ] `[DUK]` — PLC brand/model (Siemens, Allen-Bradley, other)? Is there an OPC UA server?

### §11 — Product targets (6 — 3 fields × 2 products)

- [ ] Coking coal — target ash%
- [ ] Coking coal — other specs (CSN, moisture, sulphur, etc.)
- [ ] Coking coal — contract structure
- [ ] Thermal coal — target ash%
- [ ] Thermal coal — other specs (calorific value, etc.)
- [ ] Thermal coal — contract structure

### §12 — Washability (1)

- [ ] `[DUK]` — Attach per-seam washability tables (basis for NDM ±0.1 and cut-density calculations)

### §13 — Equipment wear baseline (4)

- [ ] Vortex finder (Alumina) service life — actual (reference: 8,000–12,000 h)
- [ ] Spigot / apex (Alumina) service life — actual (reference: 6,000–10,000 h)
- [ ] Pump impeller service life — actual (reference: 3,000–5,000 h)
- [ ] Cyclone cone liner service life — actual

---

## Needs attention first

A few items aren't simply "blank — fill in"; they need a conversation:

1. **§4.2 Primary overflow R.D. (×2)** — Duk wrote *"I don't really understand what I should do here."* These need explanation before they can be filled.
2. **§6 density reconciliation** — explicitly marked critical for SP logic; three different density figures need to be sorted out.
3. ✅ **Already-answered items now integrated (v0.2)** — §4 Solids/Medium R.D. definitions, §5 size-limit handling, and the §1 identification fields have been folded into `03-plant-profile_MN.md`.

---

*Source files: `02-domain-knowledge-HMS_EN.md`, `02-domain-knowledge-HMS_MN.md`, `03-plant-profile_MN.md` in this `docs/` folder.*
