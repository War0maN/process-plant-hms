"""
SP Recommendation Engine — Phase 1 цөм логик (хоёр шатлалт DMC).

Энэ модуль нь `mocks/sp-recommendation.html` доторх JavaScript engine-ийн
ШУУД ПОРТ. Логик, томьёо нэг мөр мөрөөр тааруулсан. Эх сурвалж:
  - Doc 02 §5   — washability → cut density логик
  - Doc 02 §5.1 — ash-pinning (масс шилжүүлэх залруулга)
  - Doc 02 §5.3 — NDM (near-density material)

Урсгал:
  blend washability → хэмжсэн үнсээр ash-pin залруулга
    → нэг залруулсан муруйг ХОЁР cut дээр хуваах:
        коксжих (float < ρ1), эрчим хүчний (ρ1..ρ2), хаягдал (> ρ2)
    → коксжих ash-д ρ1, эрчим хүчний ash-д ρ2 зөвлөх (одоогийн SP-ээс nudge).

Engine нь өгөгдлийн эх үүсвэрээс үл хамаарна (Doc 04 §1.2): washability
fraction-ууд ямар ч эх сурвалжаас ирж болно — embed, localStorage, эсвэл DB.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, isnan
from typing import Optional

# Нягтын торны дээд хязгаарууд (JS DENS_HI-тэй яг ижил).
DENS_HI: list[float] = [
    1.30, 1.325, 1.35, 1.375, 1.40, 1.425, 1.45,
    1.50, 1.60, 1.70, 1.80, 2.00, 2.20, 99,
]

# Нээлттэй (хязгааргүй) фракцын нэрлэсэн хил — дунд цэг тооцоход.
NOMINAL_LO = 1.15
NOMINAL_HI = 2.50


@dataclass
class Fraction:
    """Нягтын нэг фракц: [lo, hi) хязгаар, жингийн % (mass), үнс % (ash)."""
    lo: float
    hi: float
    mass: Optional[float] = None
    ash: Optional[float] = None


# --------------------------------------------------------------------------
# Фракцын суурь геометр
# --------------------------------------------------------------------------
def grid_fractions(mass: list, ash: list) -> list[Fraction]:
    """DENS_HI торон дээр fraction жагсаалт үүсгэх (JS gridFractions)."""
    fr: list[Fraction] = []
    lo = 0.0
    for i, hi in enumerate(DENS_HI):
        m = mass[i] if i < len(mass) else None
        a = ash[i] if i < len(ash) else None
        fr.append(Fraction(lo=lo, hi=hi, mass=m, ash=a))
        lo = hi
    return fr


def _eff(f: Fraction) -> tuple[float, float]:
    """Нээлттэй хязгаарыг нэрлэсэн хилээр орлуулсан effective [lo, hi]."""
    lo = NOMINAL_LO if f.lo <= 0 else f.lo
    hi = NOMINAL_HI if f.hi >= 99 else f.hi
    return lo, hi


def _mid(f: Fraction) -> float:
    lo, hi = _eff(f)
    return (lo + hi) / 2


def _fraction_below(f: Fraction, d: float) -> float:
    """Фракцын аль хувь нь d нягтаас доош (шугаман интерполяци)."""
    lo, hi = _eff(f)
    if d >= hi:
        return 1.0
    if d <= lo:
        return 0.0
    return (d - lo) / (hi - lo)


def _mass_within(f: Fraction, a: float, b: float) -> float:
    """[a, b] мужид багтах фракцын масс (NGM тооцоход)."""
    if f.mass is None:
        return 0.0
    lo, hi = _eff(f)
    lo2, hi2 = max(a, lo), min(b, hi)
    if hi2 <= lo2:
        return 0.0
    return f.mass * (hi2 - lo2) / (hi - lo)


# --------------------------------------------------------------------------
# Blend (хольц)
# --------------------------------------------------------------------------
def blend_fractions(picks: list[dict], seams: dict[str, list[Fraction]]) -> list[Fraction]:
    """
    Seam-уудыг харьцаагаар (ratio) жигнэж нэг blend муруй болгох.

    picks: [{"code": seam нэр, "ratio": хувь}, ...]
    seams: {seam нэр: [Fraction, ...]}
    """
    tot_ratio = sum(p.get("ratio", 0) or 0 for p in picks) or 1
    acc_mass = [0.0] * len(DENS_HI)
    acc_ash_num = [0.0] * len(DENS_HI)
    for p in picks:
        s = seams.get(p["code"])
        if not s:
            continue
        w = (p.get("ratio", 0) or 0) / tot_ratio
        for sf in s:
            key = 99 if sf.hi >= 99 else sf.hi
            try:
                idx = DENS_HI.index(key)
            except ValueError:
                idx = next((i for i, h in enumerate(DENS_HI) if h >= key), len(DENS_HI) - 1)
            if sf.mass is not None:
                acc_mass[idx] += w * sf.mass
                if sf.ash is not None:
                    acc_ash_num[idx] += w * sf.mass * sf.ash
    fr = grid_fractions([0.0] * len(DENS_HI), [None] * len(DENS_HI))
    for i, f in enumerate(fr):
        f.mass = acc_mass[i]
        f.ash = (acc_ash_num[i] / acc_mass[i]) if acc_mass[i] > 0 else None
    return fr


def weighted_ash(fr: list[Fraction]) -> float:
    """Массаар жигнэсэн дундаж үнс."""
    n = d = 0.0
    for f in fr:
        if f.mass is not None and f.ash is not None:
            n += f.mass * f.ash
            d += f.mass
    return n / d if d else 0.0


# --------------------------------------------------------------------------
# Ash-pinning — масс шилжүүлэх залруулга (Doc 02 §5.1)
# --------------------------------------------------------------------------
def _mid_mean(fr: list[Fraction]) -> float:
    n = d = 0.0
    for f in fr:
        if f.mass is not None:
            n += f.mass * _mid(f)
            d += f.mass
    return n / d if d else 1.5


def _tilt_ash(fr: list[Fraction], k: float, mm: float) -> float:
    """k коэффициентээр массыг налуулсан үед гарах жигнэсэн үнс."""
    num = den = 0.0
    for f in fr:
        if f.mass is None or f.ash is None:
            continue
        w = f.mass * exp(k * (_mid(f) - mm))
        num += w * f.ash
        den += w
    return num / den if den else 0.0


def solve_tilt(fr: list[Fraction], target: float) -> float:
    """Хэмжсэн үнсэд хүрэх tilt коэффициент k-г bisection-оор олох."""
    mm = _mid_mean(fr)
    lo, hi = -40.0, 40.0
    if target <= _tilt_ash(fr, lo, mm):
        return lo
    if target >= _tilt_ash(fr, hi, mm):
        return hi
    for _ in range(80):
        m = (lo + hi) / 2
        if _tilt_ash(fr, m, mm) < target:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def apply_tilt(fr: list[Fraction], k: float) -> list[Fraction]:
    """k налуугаар массыг дахин хуваарилж шинэ муруй буцаах (нийт 100%)."""
    mm = _mid_mean(fr)
    w = [(f.mass or 0) * exp(k * (_mid(f) - mm)) for f in fr]
    tot = sum(w)
    out = []
    for i, f in enumerate(fr):
        new_mass = (w[i] / tot * 100) if tot else f.mass
        out.append(Fraction(lo=f.lo, hi=f.hi, mass=new_mass, ash=f.ash))
    return out


# --------------------------------------------------------------------------
# Cumulative float (баяжмал) тооцоо
# --------------------------------------------------------------------------
def _clean_mass_ash(fr: list[Fraction], d: float) -> tuple[float, float]:
    """d нягтаас доош (float) массын нийлбэр ба үнс-numerator."""
    m = an = 0.0
    for f in fr:
        if f.mass is None:
            continue
        b = _fraction_below(f, d)
        m += f.mass * b
        if f.ash is not None:
            an += f.mass * b * f.ash
    return m, an


def _totals(fr: list[Fraction]) -> tuple[float, float]:
    m = an = 0.0
    for f in fr:
        if f.mass is None:
            continue
        m += f.mass
        if f.ash is not None:
            an += f.mass * f.ash
    return m, an


def clean_ash_at(fr: list[Fraction], d: float) -> float:
    """d дээр хагалбал баяжмалын (float) үнс."""
    m, an = _clean_mass_ash(fr, d)
    return an / m if m else 0.0


def yield_at(fr: list[Fraction], d: float) -> float:
    """d дээр хагалбал баяжмалын гарц (%)."""
    m, _ = _clean_mass_ash(fr, d)
    tm, _ = _totals(fr)
    return m / tm * 100 if tm else 0.0


def ngm_at(fr: list[Fraction], d: float, w: float) -> float:
    """d ± w мужид багтах материалын хувь — NDM (Doc 02 §5.3)."""
    tm, _ = _totals(fr)
    m = sum(_mass_within(f, d - w, d + w) for f in fr)
    return m / tm * 100 if tm else 0.0


# --------------------------------------------------------------------------
# Cut density сонгох (target ash → нягт)
# --------------------------------------------------------------------------
def cut_for_product_ash(fr: list[Fraction], target: float) -> float:
    """Коксжих (primary): зорилтот баяжмалын үнсэд хүрэх cut нягт."""
    lo, hi = 1.20, 2.30
    if clean_ash_at(fr, lo) >= target:
        return lo
    if clean_ash_at(fr, hi) <= target:
        return hi
    for _ in range(70):
        m = (lo + hi) / 2
        if clean_ash_at(fr, m) < target:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def middling_ash(fr: list[Fraction], c1: float, c2: float) -> float:
    """ρ1..ρ2 (дунд бүтээгдэхүүн = эрчим хүчний нүүрс)-ийн үнс."""
    a_m, a_an = _clean_mass_ash(fr, c1)
    b_m, b_an = _clean_mass_ash(fr, c2)
    m = b_m - a_m
    return (b_an - a_an) / m if m > 0 else 0.0


def cut_for_middling_ash(fr: list[Fraction], c1: float, target: float) -> float:
    """Эрчим хүчний (secondary): c1-ээс хойшхи зорилтот ash-д хүрэх ρ2."""
    lo, hi = c1 + 0.005, 2.30
    if middling_ash(fr, c1, lo) >= target:
        return lo
    if middling_ash(fr, c1, hi) <= target:
        return hi
    for _ in range(70):
        m = (lo + hi) / 2
        if middling_ash(fr, c1, m) < target:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def partition(fr: list[Fraction], c1: float, c2: float) -> dict:
    """Гурван бүтээгдэхүүний масс баланс: коксжих / эрчим хүчний / хаягдал."""
    tm, t_an = _totals(fr)
    m1_m, m1_an = _clean_mass_ash(fr, c1)
    m2_m, m2_an = _clean_mass_ash(fr, c2)
    c_mass = m1_m
    t_mass = m2_m - m1_m
    r_mass = tm - m2_m
    return {
        "coking": {
            "yield": c_mass / tm * 100 if tm else 0.0,
            "ash": m1_an / c_mass if c_mass > 0 else 0.0,
        },
        "thermal": {
            "yield": t_mass / tm * 100 if tm else 0.0,
            "ash": (m2_an - m1_an) / t_mass if t_mass > 0 else 0.0,
        },
        "reject": {
            "yield": r_mass / tm * 100 if tm else 0.0,
            "ash": (t_an - m2_an) / r_mass if r_mass > 0 else 0.0,
        },
    }


# --------------------------------------------------------------------------
# Дээд түвшний зөвлөмж (JS recompute()-ийн DOM-гүй хувилбар)
# --------------------------------------------------------------------------
def recommend(
    picks: list[dict],
    seams: dict[str, list[Fraction]],
    *,
    target_coking: float = 10.5,
    target_thermal: float = 24.0,
    sp_primary: float = 1.33,
    sp_secondary: float = 1.52,
    measured_ash: Optional[float] = None,
    ngm_window: float = 0.10,
) -> dict:
    """
    Бүрэн SP зөвлөмж тооцоолох.

    Буцаах: predAsh, tilt_k, corrAsh, primary/secondary cut+nudge+recoSP+ngm,
    мөн гурван бүтээгдэхүүний масс баланс (partition).
    """
    nominal = blend_fractions(picks, seams)
    pred_ash = weighted_ash(nominal)

    have_meas = measured_ash is not None and not isnan(measured_ash) and measured_ash > 0
    k = 0.0
    corrected = nominal
    if have_meas:
        k = solve_tilt(nominal, measured_ash)
        corrected = apply_tilt(nominal, k)
    corr_ash = weighted_ash(corrected)

    # Primary (коксжих)
    base_cut1 = cut_for_product_ash(nominal, target_coking)
    corr_cut1 = cut_for_product_ash(corrected, target_coking)
    nudge1 = corr_cut1 - base_cut1
    reco_sp1 = sp_primary + nudge1

    # Secondary (эрчим хүчний) — primary cut-аас хамаарна
    base_cut2 = cut_for_middling_ash(nominal, base_cut1, target_thermal)
    corr_cut2 = cut_for_middling_ash(corrected, corr_cut1, target_thermal)
    nudge2 = corr_cut2 - base_cut2
    reco_sp2 = sp_secondary + nudge2

    ngm1 = ngm_at(corrected, corr_cut1, ngm_window)
    ngm2 = ngm_at(corrected, corr_cut2, ngm_window)
    part = partition(corrected, corr_cut1, corr_cut2)

    return {
        "pred_ash": pred_ash,
        "measured_ash": measured_ash if have_meas else None,
        "tilt_k": k,
        "corr_ash": corr_ash,
        "primary": {
            "base_cut": base_cut1,
            "corr_cut": corr_cut1,
            "nudge": nudge1,
            "reco_sp": reco_sp1,
            "ngm": ngm1,
        },
        "secondary": {
            "base_cut": base_cut2,
            "corr_cut": corr_cut2,
            "nudge": nudge2,
            "reco_sp": reco_sp2,
            "ngm": ngm2,
        },
        "balance": part,
    }
