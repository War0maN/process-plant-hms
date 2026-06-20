"""
Тоног төхөөрөмжийн элэгдлийн үнэлгээ ба SP залруулга (Doc 02 §3.4/§9.2, Doc 03 §17).

7 хоног тутмын зогсолтын хэмжилт (running hours, амсрын бор)-оос:
  • Сэлбэгийн солих сануулга (Doc 03 §13 baseline-тай тулгана).
  • SP залруулга: spigot элэгдвэл (амсар томорч d50 буурна) насосны хурдыг
    бага зэрэг нэмж даралт бариулна (Doc 03 §17). Зөвхөн зөвлөмж.

⚠ Pump-nudge нь дүрэмд суурилсан ойролцоо утга — бодит даралт-хариуны
калибровоор (online даралт өгөгдөл хуримтлагдсаны дараа) сайжруулна.
"""
from __future__ import annotations

from typing import Optional


def wear_status(hours: Optional[float], baseline_min: float, baseline_max: float) -> str:
    """running_hours-ийг baseline хүрээтэй тулгаж төлөв буцаах."""
    if hours is None:
        return "unknown"
    if hours >= baseline_max:
        return "overdue"      # яаралтай солих
    if hours >= baseline_min:
        return "soon"         # солилт төлөвлө
    return "ok"


def assess_wear(measured: dict, baselines: dict) -> dict:
    """
    measured: {"spigot": {"hours": .., "bore_mm": ..}, "vortex_finder": {...},
               "pump_impeller": {"hours": ..}, "cone_liner": {"hours": ..}}
    baselines: config.wear_baseline_hours, ж: {"spigot": [4000,6000], ...}

    Буцаах: {alerts: [...], pump_speed_nudge_pct: float}
    """
    alerts = []
    for comp, base in baselines.items():
        if not isinstance(base, (list, tuple)) or len(base) != 2:
            continue
        bmin, bmax = base
        m = measured.get(comp, {}) if measured else {}
        h = m.get("hours")
        st = wear_status(h, bmin, bmax)
        if st == "overdue":
            alerts.append({"component": comp, "hours": h, "status": st,
                           "msg": f"{comp}: {h:.0f}ц ≥ {bmax:.0f}ц — ЯАРАЛТАЙ СОЛИХ"})
        elif st == "soon":
            alerts.append({"component": comp, "hours": h, "status": st,
                           "msg": f"{comp}: {h:.0f}ц ({bmin:.0f}-{bmax:.0f}) — солилт төлөвлө"})

    # spigot элэгдлээс насосны хурдны зөвлөмж (Doc 03 §17)
    nudge = 0.0
    sp = (measured or {}).get("spigot", {})
    h = sp.get("hours")
    if h is not None:
        bmin, bmax = baselines.get("spigot", [4000, 6000])
        frac = h / bmax if bmax else 0
        # элэгдэл baseline_min давсны дараа аажмаар хүртэл +2% хүрэх
        if frac > (bmin / bmax):
            nudge = min(2.0, (frac - bmin / bmax) / (1 - bmin / bmax) * 2.0)
    return {"alerts": alerts, "pump_speed_nudge_pct": round(nudge, 2)}
