"""
Бүх циклийн (whole-plant) нэгтгэл — ширхэглэлийн хуваарилалт × циклийн гарц.

ROM нүүрс ширхэгээр салж өөр цикл рүү ордог (Doc 03 §5, ТЭЗҮ Хүснэгт 6):
  • -50+1.2мм   → ХСЦ (DMC, coarse)       — washability-аас гарц
  • -1.2+0.25мм → шурган сепаратор (TBS)  — циклийн recovery
  • -0.25мм     → флотаци                  — циклийн recovery

Нийт гарц = Σ (ширхэгийн масс% × тухайн циклийн гарц).
Ширхэглэлийн шинжилгээгүйгээр зөвхөн coarse циклийн гарцыг л мэдэх тул бүх
циклийн тооцоонд ШИРХЭГЛЭЛИЙН ШИНЖИЛГЭЭ ЗААВАЛ хэрэгтэй.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SizeSplit:
    """Тэжээлийн ширхэглэлийн масс хуваарилалт (% — нийлбэр ~100)."""
    coarse_pct: float        # -50+1.2мм → ХСЦ
    medium_pct: float        # -1.2+0.25мм → шурган
    fine_pct: float          # -0.25мм → флотаци
    oversize_pct: float = 0.0   # +50мм (хаягдал/дахин бутлал)

    def normalized(self) -> "SizeSplit":
        tot = self.coarse_pct + self.medium_pct + self.fine_pct + self.oversize_pct
        if tot <= 0:
            return self
        return SizeSplit(self.coarse_pct / tot * 100, self.medium_pct / tot * 100,
                         self.fine_pct / tot * 100, self.oversize_pct / tot * 100)


def plant_yield(
    split: SizeSplit,
    coarse_yield_pct: float,
    *,
    spiral_recovery_pct: float = 75.0,    # ТЭЗҮ Хүснэгт 7 дизайн дундаж
    flotation_recovery_pct: float = 60.0,  # ТЭЗҮ Хүснэгт 7 дизайн дундаж
) -> dict:
    """
    Бүх циклийн нийт баяжмалын гарцыг (тэжээлийн нийт массд харьцангуй) тооцох.

    coarse_yield_pct — ХСЦ washability-аас гарсан гарц (тухайн coarse фракцид %).
    spiral/flotation_recovery — нарийн циклүүдийн гарц (тэдгээрийн фракцид %).
    Нягт нь ТЭЗҮ дизайн; бодит утга нь тус циклийн өөрийн туршилтаас гарна.
    """
    s = split.normalized()
    coarse = s.coarse_pct / 100 * coarse_yield_pct
    medium = s.medium_pct / 100 * spiral_recovery_pct
    fine = s.fine_pct / 100 * flotation_recovery_pct
    total = coarse + medium + fine
    return {
        "coarse_contrib": coarse,
        "medium_contrib": medium,
        "fine_contrib": fine,
        "total_yield_pct": total,
        "split": {"coarse": s.coarse_pct, "medium": s.medium_pct,
                  "fine": s.fine_pct, "oversize": s.oversize_pct},
    }
