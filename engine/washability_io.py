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


# --------------------------------------------------------------------------
# ТҮҮХИЙ (raw) дата ачаалагч — ad үнс + чийг + граммаар жин
# --------------------------------------------------------------------------
def _num(v):
    try:
        return float(str(v).replace(",", ".").strip())
    except (ValueError, AttributeError):
        return None


def _col_resolver(fieldnames):
    cols = {str(c).lower().strip(): c for c in (fieldnames or []) if c is not None}

    def col(*names):
        for n in names:
            if n in cols:
                return cols[n]
        return None

    return col


def seams_from_raw_rows(rows: list[dict], col) -> dict[str, list[Fraction]]:
    """
    Түүхий лабын мөрүүдээс seam бүрийн Fraction жагсаалт үүсгэх (Doc 07).

      • жин граммаар бол seam дотор нийлбэрт хувааж % болгоно;
      • ash_ad + чийг (moisture) бол to_dry_basis-аар d суурьт хөрвүүлнэ;
      • density_hi-г DENS_HI торонд буулгана (бодит лабын ладдер тохирно).
    """
    from .washability import to_dry_basis

    c_seam = col("seam", "давхрага", "seam_code")
    c_hi = col("density_hi", "нягт_дээд", "density", "rd", "нягт")
    c_mass = col("mass_g", "mass", "жин", "mass_pct", "жин_г")
    c_ash = col("ash_ad", "ash_ad_pct", "үнс_ad", "ash", "үнс")
    c_moist = col("moisture_ad", "moisture_ad_pct", "im", "чийг", "moisture")
    c_dry = col("ash_dry", "ash_dry_pct", "үнс_dry")

    by_seam: dict[str, list[tuple]] = {}
    for row in rows:
        seam = (str(row.get(c_seam)).strip() if c_seam and row.get(c_seam) else "")
        if not seam:
            continue
        hi = row.get(c_hi) if c_hi else None
        mass = _num(row.get(c_mass)) if c_mass else None
        if hi is None or mass is None:
            continue
        ash = None
        if c_dry and _num(row.get(c_dry)) is not None:
            ash = _num(row.get(c_dry))
        elif c_ash and _num(row.get(c_ash)) is not None:
            ad = _num(row.get(c_ash))
            m = _num(row.get(c_moist)) if c_moist else None
            ash = to_dry_basis(ad, m) if m is not None else ad
        by_seam.setdefault(seam, []).append((hi, mass, ash))

    out = {}
    for seam, recs in by_seam.items():
        tot = sum(m for _, m, _ in recs) or 1.0
        out[seam] = seam_from_rows([(hi, m / tot * 100, a) for hi, m, a in recs])
    return out


def seams_from_raw_csv(path: str | Path) -> dict[str, list[Fraction]]:
    """Түүхий washability CSV (ad үнс + чийг + жин) ачаалах."""
    with open(path, encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        return seams_from_raw_rows(rows, _col_resolver(reader.fieldnames))


def seams_from_raw_xlsx(path: str | Path, sheet=None) -> dict[str, list[Fraction]]:
    """Түүхий washability xlsx ачаалах (эхний мөр = толгой)."""
    from openpyxl import load_workbook

    wb = load_workbook(path, data_only=True)
    ws = wb[sheet] if sheet else wb.worksheets[0]
    data = list(ws.iter_rows(values_only=True))
    header = [str(h).strip() if h is not None else "" for h in data[0]]
    rows = [dict(zip(header, r)) for r in data[1:]]
    return seams_from_raw_rows(rows, _col_resolver(header))
