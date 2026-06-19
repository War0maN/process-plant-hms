"""
Washability өгөгдөл ачаалагч.

`docs/05b-washability-template`-ийн бүтэцтэй CSV/xlsx эсвэл энгийн dict-ээс
seam бүрийн нягтын фракцыг engine-ийн Fraction жагсаалт болгон уншина.

Хүлээгдэх багана: нягтын дээд хязгаар (g/cm³), жингийн % (mass), үнс % (ash).
"""
from __future__ import annotations

import csv
from pathlib import Path

from .washability import DENS_HI, Fraction, grid_fractions


def seams_from_dict(raw: dict[str, dict]) -> dict[str, list[Fraction]]:
    """
    {seam: {"mass": [...], "ash": [...]}} → {seam: [Fraction,...]}.
    mass/ash жагсаалт нь DENS_HI торны дарааллаар байх ёстой.
    """
    return {code: grid_fractions(s["mass"], s["ash"]) for code, s in raw.items()}


def _parse_density_hi(text: str) -> float | None:
    """'1.40', '< 1.30', '> 2.00', 'sink' зэргийг дээд хязгаар болгон тайлах."""
    t = str(text).strip().lower().replace(",", ".")
    if not t:
        return None
    if "sink" in t or "живэг" in t or t.startswith(">"):
        return 99.0
    # "1.30 - 1.40" хэлбэрээс баруун (дээд) утгыг авна
    if "-" in t:
        parts = [p.strip() for p in t.split("-") if p.strip()]
        try:
            return float(parts[-1])
        except ValueError:
            return None
    t = t.lstrip("<").strip()
    try:
        return float(t)
    except ValueError:
        return None


def seam_from_rows(rows: list[tuple]) -> list[Fraction]:
    """
    (density_hi, mass_pct, ash_pct) гурвалсан мөрүүдээс нэг seam-ийн Fraction
    жагсаалтыг үүсгэх. Мөрүүд DENS_HI торонд буулгагдана.
    """
    mass = [0.0] * len(DENS_HI)
    ash_num = [0.0] * len(DENS_HI)
    has_ash = [False] * len(DENS_HI)
    for hi_raw, m_raw, a_raw in rows:
        hi = _parse_density_hi(hi_raw)
        if hi is None or m_raw in (None, ""):
            continue
        try:
            m = float(str(m_raw).replace(",", "."))
        except ValueError:
            continue
        # хамгийн ойрын торны нүд олох
        key = 99.0 if hi >= 99 else hi
        idx = next((i for i, h in enumerate(DENS_HI) if abs(h - key) < 1e-6), None)
        if idx is None:
            idx = next((i for i, h in enumerate(DENS_HI) if h >= key), len(DENS_HI) - 1)
        mass[idx] += m
        if a_raw not in (None, ""):
            try:
                a = float(str(a_raw).replace(",", "."))
                ash_num[idx] += m * a
                has_ash[idx] = True
            except ValueError:
                pass
    ash = [(ash_num[i] / mass[i]) if (has_ash[i] and mass[i] > 0) else None
           for i in range(len(DENS_HI))]
    return grid_fractions(mass, ash)


def seams_from_csv(path: str | Path) -> dict[str, list[Fraction]]:
    """
    Олон seam-ийн CSV ачаалах. Хүлээгдэх багана (толгойтой):
        seam, density_hi, mass_pct, ash_pct
    """
    by_seam: dict[str, list[tuple]] = {}
    with open(path, encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        # баганын нэрсийг уян хатан тааруулах
        cols = {c.lower().strip(): c for c in (reader.fieldnames or [])}

        def col(*names):
            for n in names:
                if n in cols:
                    return cols[n]
            return None

        c_seam = col("seam", "давхрага", "seam_code")
        c_hi = col("density_hi", "нягт", "density", "нягтын хязгаар")
        c_m = col("mass_pct", "mass", "жин", "жингийн хувь")
        c_a = col("ash_pct", "ash", "үнс", "үнслэг")
        for row in reader:
            seam = (row.get(c_seam) or "").strip() if c_seam else ""
            if not seam:
                continue
            by_seam.setdefault(seam, []).append(
                (row.get(c_hi), row.get(c_m), row.get(c_a))
            )
    return {seam: seam_from_rows(rows) for seam, rows in by_seam.items()}
