# MVP Scope — HMS Circuit (Phase 1)

**Version:** v0.2
**Date:** 2026-05-18
**Authors:** Duk + AI advisor (process engineering perspective)
**Status:** DISCUSSION DRAFT — not approved

---

## 1. Context & Purpose

### 1.1 What we are building
An **AI-assisted advisory process optimization system** for coal and mineral beneficiation plants. The system works with PLC data (process variables in real time), manually entered laboratory results, and manually entered equipment measurements. Combining these sources, it provides operators with **real-time setpoint (SP) recommendations**, anomaly alerts, an equipment inspection checklist, a spare-parts list and registry (including replacement-timing predictions), production-loss early warnings, and energy-consumption optimization.

The first release operates in **advisory mode (shadow mode) only** — no automatic writes to the PLC. The operator makes every decision.

> **Note (Scope discipline).** The list above is the product's long-term **vision**. This MVP — **Phase 1** — includes only what is specified in **§4**. Energy-consumption optimization, the detailed equipment inspection checklist, and other vision items belong to **Phase 2–3** (see §5 OUT). §1.1 says "where we are going"; §4 says "what we are building now."

### 1.2 Why we start with the HMS circuit
Of all coal beneficiation circuits, the Heavy Media Separation (HMS) / Dense Medium Cyclone circuit is chosen first because:

- **Clean instrumentation:** media density, cyclone pressure, and pump speed are all reliably available on PLC tags
- **Few setpoints:** primarily media density and pump speed
- **Reasonably fast feedback loop:** lab ash analyses arrive within ~12 hours
- **Strong scientific foundation:** washability-curve → density-cut logic is well-studied and tractable
- **Visible ROI:** a 0.02 g/cm³ change in media density translates directly into measurable ash% and yield differences

Spirals and flotation are explicitly deferred to later phases.

### 1.3 What this MVP must prove
Within **30–90 days**, this MVP must demonstrate three things to us and to prospective users:

1. We can reliably connect to plant data, clean it, and present it to the operator in a useful way
2. **At least 50%** of our SP recommendations are accepted by operators
3. The system delivers **measurable value** — improved ash% consistency, lower media consumption, or quantifiable loss reduction

---

## 2. Target Users

| User | Need | Interaction frequency |
|------|------|------------------------|
| Control-room operator | Real-time monitoring, anomaly alerts, SP recommendations | All day. **The most important user.** |
| Beneficiation engineer / metallurgist | Take samples, run lab analyses, work with the data, derive optimization insights | Per shift / per week |
| Maintenance lead engineer | Check spare-parts inventory, monitor equipment wear | Weekly |
| Plant manager / owner | KPI overview, reports | Weekly |

**Design principle:** the first MVP optimizes for the **operator**. Other personas are tuned later.

---

## 3. Problem Statement

Typical pain points in HMS operation today (to be confirmed against the specific pilot plant):

- **Media density is adjusted manually** — operator intuition, but slow to respond when feed quality shifts
- **Lab ash results lag** — an upset is only known about **~12 hours later** (online proxies required)
- **Equipment wear** (cyclone spigot and vortex finder wear, pump impeller wear, etc.) is tracked from **memory or paper logs**, not predicted
- **Shift-to-shift variability** — each operator has their own "style," resulting in inconsistent ROI
- **Historical data is unprocessed** — recurring problems are rarely documented, so the same issues repeat

### 3.1 What success looks like
*"Six months in, HMS ash and yield are consistent; the spread of setpoint adjustments operators make on identical feed coal has dropped by 30% across shifts; magnetite (media) consumption is measurably lower; the system produces a maintenance task list for scheduled shutdowns and displays current spare-parts information."*

---

## 4. Scope — IN

### 4.1 Data layer
- Continuous read of HMS-related **PLC tags** (OPC UA or Modbus TCP, **read-only**)
- **Manual entry form** for lab data — ash%, moisture%, size distribution, washability results
- **Manual entry** for maintenance / equipment data — running hours, breakdowns, parts replacement, wear
- Time-series storage (TimescaleDB)
- ≥ 6 months of historical data retention

### 4.2 Dashboard
- Real-time HMS circuit status: media density, pressure, flow, feed rate
- Trend charts — last 24 hours, 7 days, 30 days
- Latest lab results, with historical comparison
- Shift-to-shift comparison view
- Basic KPI panel (yield, ash recovery, media consumption)

### 4.3 Rule-based alerts
- Media density: out of bounds → alert
- Cyclone pressure: drift or step change → alert
- Feed flow vs SP: persistent deviation → alert
- Lab ash% out of spec → alert
- Equipment running hours past threshold → **spare-parts notification**

### 4.4 Shadow SP recommendations
- Based on current feed quality (ash%, size) and the washability curve, recommend an **optimal media density**
- The operator responds with Accept / Reject / Modify
- On Reject, the operator selects a reason from a predefined list (e.g., yield drops, media cost, other)
- **Every decision is logged** — this becomes training data for the future ML model
- An **explanation panel** shows the reasoning behind each recommendation ("why this value?")

### 4.5 Foundational features
- User login (3 role tiers: Operator, Engineer, Admin)
- Audit log of all user actions
- System health monitoring (data-feed uptime, latency)

---

## 5. Scope — OUT (just as important as IN)

The following are explicitly **NOT in this MVP**. Stating them clearly is the primary defence against scope creep.

- ❌ **PLC writes (closed-loop control).** Under no circumstances does the system write setpoints automatically. Advisory only.
- ❌ **Spirals circuit.** Phase 2 (3–6 months out)
- ❌ **Flotation circuit.** Phase 3 (6–12 months out)
- ❌ **Energy-consumption optimization.** Vision item, Phase 2+
- ❌ **Full equipment inspection-checklist module.** Phase 2 — basic spare-parts notifications are IN, full inspection-list management is OUT
- ❌ **Complex ML / Deep Learning models.** Phase 1 uses only rules + physics-based logic + simple statistics
- ❌ **Predictive maintenance / vibration analytics.** Phase 2 add-on
- ❌ **Multi-plant central management.** Phase 1 = single plant
- ❌ **Cloud storage.** Phase 1 = on-premise or hybrid (data ownership + network reliability)
- ❌ **Mobile app.** Web only
- ❌ **Integrations with external systems** (ERP, LIMS, CMMS). Later.
- ❌ **Multi-language UI.** Mongolian first, English later
- ❌ **Report export (PDF, etc.)** — possibly Phase 1.5

---

## 6. Success Metrics

### 6.1 Quantitative (by end of 90-day pilot)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Data uptime | ≥ 95% | System logs |
| Operator-accepted recommendation rate | ≥ 50% | Accept-button telemetry |
| Anomaly alert precision (low false alarm rate) | ≥ 70% | Operator feedback |
| Spare-parts alert timing accuracy | ±20% of actual running hours | Maintenance log comparison |
| HMS circuit ash% deviation from target | 15–20% improvement vs baseline | Lab averages |

### 6.2 Qualitative

- Operators trust the system enough to leave it open during the shift
- Engineers use the system for analysis instead of running a parallel Excel
- The plant manager reads KPIs from the system, not from a separate Excel sheet

### 6.3 Red-flag signals (trigger pivot)

- Operator acceptance rate **< 20%** → either the model or the UX is wrong
- **> 10 false alerts per week** → thresholds are mis-tuned
- Data uptime **< 80%** → infrastructure issue

In these cases, we will not be afraid to **pivot**.

---

## 7. Safety Boundaries

For industrial software these are not negotiable design preferences, they are **hard limits**:

1. **No PLC writes.** Phase 1 is fully read-only.
2. **Safety logic stays inside the PLC.** We never touch it.
3. **Failure of advisory → plant continues running.** A system outage must never stop production (graceful degradation).
4. **Audit log mandatory.** Every user action, including recommendation accept/reject, is persisted.
5. **Network sandbox.** The system sits on a separate VLAN with a one-way mirror from the PLC network.
6. **Failover.** If our server goes down, the existing SCADA must continue normally.

---

## 8. Assumptions & Constraints

### 8.1 Assumptions (to be validated)
- A pilot plant can be found (active search required)
- PLC data can be reliably exported (an OPC UA server exists or can be installed)
- A lab technician is willing to enter daily lab results
- A modern web browser is available in the control room

### 8.2 Technical constraints
- An on-premise server (Windows or Linux) is required
- Internal network connectivity is needed
- Lab data is human-entered and arrives ~12 hours after sampling → SP recommendations cannot rely on lab-only feedback; they must use online proxies (density vs pressure correlations, pump speed drift, underflow/overflow imbalance, online size analyzers if available). Lab results are used for daily model calibration, not minute-by-minute control.

### 8.3 Business constraints
- No customer contract yet → working with a design partner on a voluntary basis
- The pilot is likely unpaid for us (exchange: data + experience for the customer's time)
- Data-ownership and IP terms must be agreed up front

---

## 9. Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-------------|
| No pilot plant found | Medium | Very high | Active search in first 30 days |
| Operator resistance / change management | High | High | Early operator interviews, involve them in UI design |
| Poor lab data quality | High | Medium | Form-level validation + sanity checks |
| PLC tag-naming variability across plants | Very high | Medium | Build a tag-mapping catalog |
| Over-engineering before customer validation | Medium | Medium | Hard 90-day timebox |
| MVP recommends a harmful density value | Low | High | Shadow mode + operator approval required |
| Regulatory / tender obstacles | Medium | High | Engage legal advice early |
| Lab feedback lag (~12h) makes recommendations stale | High | Medium | Use online proxies; treat lab as calibration source |

---

## 10. Next Steps & Open Questions

### 10.1 To resolve before approving this scope
1. **Design-partner plant.** Who, when, on what terms?
2. **Pilot duration.** 60 / 90 / 180 days? I propose 90.
3. **Regulatory environment.** Does Mongolian mining regulation require special approval to connect to plant PLCs?
4. **IP / data ownership.** Who owns data and models that accrue during the pilot?

### 10.2 Next documents to write (after this scope is approved)
1. **Domain Knowledge Document** — the coal beneficiation process knowledge base (HMS deep-dive: spigot/vortex finder wear, magnetite media chemistry, washability interpretation, etc.)
2. **Data Specification** — which PLC tags, lab fields, formats
3. **Operator Workflow / Wireframes** — initial UI sketches
4. **Technical Architecture** — server diagram, network topology

### 10.3 Decision ownership (RACI)
*To be filled in once the pilot is set up.*

---

## 11. Decision Log

| Date | Decision | Reason | Decided by |
|------|----------|--------|-------------|
| 2026-05-18 | Phase 1 = HMS circuit | Washability data available; clean instrumentation; visible ROI | Duk + AI advisor |
| 2026-05-18 | Shadow mode only (no PLC writes) | Safety; rebuild operator trust | Duk + AI advisor |
| 2026-05-18 | On-premise (not cloud) | Mining data sovereignty; network reliability | Duk + AI advisor |
| 2026-05-18 | Pilot duration: 90 days (proposed) | Not too short, not too long | Pending Duk's confirmation |
| 2026-05-18 | Scope discipline: §1.1 = vision, §4 = Phase 1 scope | Defend against scope creep; avoid blending vision with MVP | Duk (Option A) |
| 2026-05-18 | Lab ash feedback ~12 hours (not minutes) | Real plant reality; SP logic must rely on online proxies (density-vs-pressure, pump speed drift, etc.); lab data used for daily calibration | Duk |
| 2026-05-18 | SP variables = media density + pump speed | Cyclone pressure is a PV (result), not a setpoint — pump speed is the controlled variable | Duk |

---

## 12. Version History

| Version | Date | Change |
|---------|------|--------|
| v0.1 | 2026-05-18 | Initial draft |
| v0.2 | 2026-05-18 | Incorporated Duk's review edits (12-hour lab feedback, pump speed SP, cyclone spigot/vortex finder, magnetite, control-room terminology, etc.). Scope discipline clarified: §1.1 = vision, §4 = Phase 1 scope only (Option A). |
