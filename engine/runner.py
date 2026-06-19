"""
Config-оор удирдагддаг SP зөвлөмжийн runner.

Plant config (Doc 03/06) + seam washability-г нэгтгэж, бүрэн SP зөвлөмж,
гэрээний шинжилгээ, монгол хэл дээрх тайлбар гаргана.

Энэ нь engine-ийн цөм (washability.py) ба бодит үйлдвэрийн тохиргоог
холбож, оператор/инженерт ойлгомжтой гаргалт өгөх давхарга.
"""
from __future__ import annotations

from typing import Optional

from .washability import (
    Fraction,
    blend_fractions,
    clean_ash_at,
    weighted_ash,
    yield_at,
)
from .washability import recommend as _recommend


def _cfg(d: dict, path: str, default=None):
    cur = d
    for p in path.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur if cur is not None else default


def contract_analysis(corrected: list[Fraction], contract: Optional[dict]) -> Optional[dict]:
    """
    Гэрээний bonus-penalty бүтэцтэй харьцуулсан gross-margin шинжилгээ.

    Үндсэн (base) ба торгуулийн (penalty) үнсэд харгалзах гарцыг бодож,
    "хэр их yield-ийг аюулгүйгээр авч болох" зөрүүг харуулна (Doc 02 §5.4).
    """
    if not contract:
        return None
    base = contract.get("base_ash_pct")
    penalty = contract.get("penalty_threshold_pct")
    reject = contract.get("rejection_threshold_pct")
    out: dict = {}
    if base is not None:
        out["yield_at_base_ash"] = yield_at(corrected, _cut_for(corrected, base))
    if penalty is not None:
        out["yield_at_penalty_ash"] = yield_at(corrected, _cut_for(corrected, penalty))
    if base is not None and penalty is not None:
        out["yield_gain_base_to_penalty"] = (
            out["yield_at_penalty_ash"] - out["yield_at_base_ash"]
        )
    out["base_ash"] = base
    out["penalty_ash"] = penalty
    out["reject_ash"] = reject
    out["penalty_usd_per_t"] = contract.get("penalty_usd_per_t")
    return out


def _cut_for(fr: list[Fraction], target_ash: float) -> float:
    """Дотоод туслах — target үнсэд хүрэх cut (washability.cut_for_product_ash)."""
    from .washability import cut_for_product_ash
    return cut_for_product_ash(fr, target_ash)


def build_recommendation(
    cfg: dict,
    picks: list[dict],
    seams: dict[str, list[Fraction]],
    *,
    measured_ash: Optional[float] = None,
) -> dict:
    """
    Plant config-оос зорилт, SP, NDM цонхыг уншиж бүрэн зөвлөмж гаргах.

    measured_ash: online ash analyzer (AIT_105) эсвэл лабын утга. None бол таамаг.
    """
    target_coking = _cfg(cfg, "product_targets.coking.target_ash_pct", 10.5)
    target_thermal = _cfg(cfg, "product_targets.thermal.target_ash_pct", 24.0)
    sp_primary = _cfg(cfg, "medium_density.primary.typical", 1.38)
    sp_secondary = _cfg(cfg, "medium_density.secondary.typical", 1.50)
    ngm_window = _cfg(cfg, "engine.ngm_half_width", _cfg(cfg, "engine.ngm_window", 0.10))
    ngm_warn = _cfg(cfg, "engine.ngm_warn_threshold_pct", 25)

    result = _recommend(
        picks, seams,
        target_coking=target_coking,
        target_thermal=target_thermal,
        sp_primary=sp_primary,
        sp_secondary=sp_secondary,
        measured_ash=measured_ash,
        ngm_window=ngm_window,
    )

    # Гэрээний шинжилгээ — залруулсан муруйн дээр
    nominal = blend_fractions(picks, seams)
    corrected = nominal
    if measured_ash:
        from .washability import apply_tilt, solve_tilt
        corrected = apply_tilt(nominal, solve_tilt(nominal, measured_ash))
    contract = _cfg(cfg, "product_targets.coking.contract")
    result["contract"] = contract_analysis(corrected, contract)
    result["ngm_warn_threshold"] = ngm_warn
    result["targets"] = {"coking": target_coking, "thermal": target_thermal}
    result["density_limits"] = {
        "primary": [_cfg(cfg, "medium_density.primary.working_min"),
                    _cfg(cfg, "medium_density.primary.working_max")],
        "secondary": [_cfg(cfg, "medium_density.secondary.working_min"),
                      _cfg(cfg, "medium_density.secondary.working_max")],
    }
    return result


def format_mn(r: dict) -> str:
    """Зөвлөмжийг оператор/инженерт ойлгомжтой монгол текст болгох."""
    L = []
    L.append("═══ SP ЗӨВЛӨМЖ (shadow — оператор шийднэ) ═══")
    meas = r.get("measured_ash")
    L.append(f"Тэжээлийн таамаг үнс: {r['pred_ash']:.1f}%"
             + (f" | хэмжсэн (online/лаб): {meas:.1f}% (tilt k={r['tilt_k']:+.2f})"
                if meas else " | хэмжсэн үнс алга — таамаг муруй"))
    p, s = r["primary"], r["secondary"]
    L.append("")
    L.append(f"① КОКСЖИХ (зорилт {r['targets']['coking']}% үнс):")
    L.append(f"   Орчны нягт SP: {p['reco_sp']:.3f}  (одоо {p['reco_sp']-p['nudge']:.3f}, "
             f"шилжилт {p['nudge']:+.3f})")
    L.append(f"   Хагалах нягт (cut): {p['corr_cut']:.3f} | NDM(±0.1): {p['ngm']:.1f}%"
             + (f"  ⚠ NDM>{r['ngm_warn_threshold']}% — ялгалт хүндэрсэн" if p['ngm'] > r['ngm_warn_threshold'] else ""))
    L.append(f"② ЭРЧИМ ХҮЧНИЙ (зорилт {r['targets']['thermal']}% үнс):")
    L.append(f"   Орчны нягт SP: {s['reco_sp']:.3f}  (одоо {s['reco_sp']-s['nudge']:.3f}, "
             f"шилжилт {s['nudge']:+.3f})")
    L.append(f"   Хагалах нягт (cut): {s['corr_cut']:.3f} | NDM: {s['ngm']:.1f}%")
    b = r["balance"]
    L.append("")
    L.append("Гурван бүтээгдэхүүний баланс:")
    L.append(f"   Коксжих:    гарц {b['coking']['yield']:.1f}%  үнс {b['coking']['ash']:.1f}%")
    L.append(f"   Эрчим хүч:  гарц {b['thermal']['yield']:.1f}%  үнс {b['thermal']['ash']:.1f}%")
    L.append(f"   Хаягдал:    гарц {b['reject']['yield']:.1f}%  үнс {b['reject']['ash']:.1f}%")
    c = r.get("contract")
    if c and c.get("yield_gain_base_to_penalty") is not None:
        L.append("")
        L.append("Гэрээний шинжилгээ (gross margin):")
        L.append(f"   Үндсэн {c['base_ash']}% үнсэд гарц: {c['yield_at_base_ash']:.1f}%")
        L.append(f"   Торгуулийн {c['penalty_ash']}% үнсэд гарц: {c['yield_at_penalty_ash']:.1f}%")
        L.append(f"   → {c['base_ash']}%-аас {c['penalty_ash']}% хүртэл нэмж авах гарц: "
                 f"+{c['yield_gain_base_to_penalty']:.1f}% "
                 f"(торгууль {c.get('penalty_usd_per_t')}$/т-той тэнцвэрлэнэ)")
        if c.get("reject_ash"):
            L.append(f"   ⚠ {c['reject_ash']}%-аас дээш → татгалзах эрсдэл. Энэ хязгаарт хүрэхгүй.")
    return "\n".join(L)
