"""
Бүх seam-ийн лабын washability файлыг боловсруулж нэгдсэн дүгнэлт гаргах.

docs/refs/ доторх стандарт лабын workbook (Float sink хуудастай) бүрийг уншиж,
seam тус бүрийн чанар, коксжих боломжийг харьцуулна.

Ажиллуулах:  python -m engine.process_seams
"""
import glob
import os
import re
from pathlib import Path

from engine import washability as w
from engine import washability_io as wio

REFS = Path(__file__).resolve().parent.parent / "docs" / "refs"

# Баталгаажсан config-аас
TARGET_COKING = 10.5
TARGET_THERMAL = 22.5
NGM_HW = 0.05

SEAM_RE = re.compile(r"\b([0-9][A-Z]{1,3}[0-9]?)\b")


def seam_code(filename: str) -> str:
    """Файлын нэрнээс seam кодыг гаргах (ж: 4AU, 0CL1, 6A)."""
    base = os.path.basename(filename)
    # доод зураас/зайгаар салгаж seam-шинж токен хайх
    toks = re.split(r"[ _\-.]", base)
    for t in reversed(toks):
        if re.fullmatch(r"[0-9][A-Z]{1,3}[0-9]?", t):
            return t
    m = SEAM_RE.search(base)
    return m.group(1) if m else base


def load_all() -> dict:
    seams = {}
    for f in sorted(glob.glob(str(REFS / "#*.xlsx"))):
        try:
            fr = wio.lab_floatsink_seam(f)
            seams[seam_code(f)] = fr
        except Exception as e:
            print(f"  ⚠ {os.path.basename(f)}: {e}")
    return seams


def main():
    seams = load_all()
    print("═" * 74)
    print(f" БҮХ SEAM-ИЙН WASHABILITY ДҮГНЭЛТ ({len(seams)} давхрага)")
    print(f" Коксжих зорилт {TARGET_COKING}% үнс | NGM ±{NGM_HW}")
    print("═" * 74)
    print(f" {'Seam':<6}{'Тэж.үнс%':>9}{'cut@10.5':>9}{'Гарц%':>7}{'NGM%':>6}"
          f"{'S%':>6}{'CSN*':>6}  Үнэлгээ")
    print("─" * 74)
    rows = []
    for code, fr in sorted(seams.items()):
        ta = w.weighted_ash(fr)
        cut = w.cut_for_product_ash(fr, TARGET_COKING)
        y = w.yield_at(fr, cut)
        ngm = w.ngm_at(fr, cut, NGM_HW)
        s = w.cum_float_quality(fr, cut, "sulphur") or 0
        csn = w.cum_float_quality(fr, cut, "csn")
        if y < 5:
            verdict = "✗ коксжихгүй (үнс өндөр)"
        elif y >= 40 and ngm < 35:
            verdict = "✓ сайн коксжих"
        elif y >= 25:
            verdict = "• дунд (NGM хяна)"
        else:
            verdict = "△ сул"
        rows.append((code, ta, cut, y, ngm, s, csn, verdict))
        print(f" {code:<6}{ta:>9.1f}{cut:>9.3f}{y:>7.1f}{ngm:>6.1f}"
              f"{s:>6.2f}{(csn or 0):>6.1f}  {verdict}")
    print("─" * 74)
    good = [r for r in rows if r[3] >= 40]
    print(f" Сайн коксжих ({len(good)}): {', '.join(r[0] for r in good)}")
    print(" * CSN нь аддитив биш — зөвхөн лавлагаа (лаб баталгаажуулна)")
    print("═" * 74)


if __name__ == "__main__":
    main()
