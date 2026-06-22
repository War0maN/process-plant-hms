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
    # Спек UHG_MVHCC (Product Target): Sd<0.65 (db), VMdaf<27 (daf), CSN>=7
    SPEC = {"sulphur": {"max": 0.65}, "vol": {"max": 27.0, "basis": "daf"},
            "csn": {"min": 7.0}}
    print(f" {'Seam':<6}{'Үнс%':>6}{'cut':>7}{'Гарц%':>7}{'NGM%':>6}"
          f"{'Sd%':>6}{'VMdaf':>6}{'CSN*':>6}  Спек(S/VM/CSN)")
    print("─" * 74)
    rows = []
    for code, fr in sorted(seams.items()):
        cut = w.cut_for_product_ash(fr, TARGET_COKING)
        y = w.yield_at(fr, cut)
        ngm = w.ngm_at(fr, cut, NGM_HW)
        chk = w.check_specs(fr, cut, SPEC)
        s = chk["sulphur"]["value"] or 0
        vm = chk["vol"]["value"] or 0
        csn = chk["csn"]["value"]
        def mk(q):
            ok = chk[q]["ok"]
            return "—" if ok is None else ("✓" if ok else "✗")
        spec_str = f"{mk('sulphur')}/{mk('vol')}/{mk('csn')}"
        rows.append((code, y, ngm, s, vm, csn, chk))
        print(f" {code:<6}{w.weighted_ash(fr):>6.1f}{cut:>7.3f}{y:>7.1f}{ngm:>6.1f}"
              f"{s:>6.2f}{vm:>6.1f}{(csn or 0):>6.1f}  {spec_str}")
    print("─" * 74)
    # бүрэн спекд тэнцэх (S<1 ба VM<25; CSN лавлагаа тул тусад нь)
    pass_sv = [r for r in rows if r[6]["sulphur"]["ok"] and r[6]["vol"]["ok"] and r[1] >= 40]
    print(f" Гарц≥40 + Sd<0.65(db) + VMdaf<27 ({len(pass_sv)}): "
          f"{', '.join(r[0] for r in pass_sv) or '—'}")
    print(" * CSN аддитив биш — массаар дунджилсан ойролцоо утга (лаб баталгаажуулна).")
    print("   CSN>=7 нь нэг seam дээр ховор; blend/коксын зууханд эмпирик хянана.")
    print("═" * 74)


if __name__ == "__main__":
    main()
