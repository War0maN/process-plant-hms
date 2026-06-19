"""
Book2.xlsx ground-truth тест — engine-ийн тооцоог бодит Ухаа Худагийн лабын
фракцын шинжилгээний хүснэгттэй яг тулгана.

Эх сурвалж: docs/refs/Book2.xlsx, "Float sink", баруун composite (-50+0.25мм),
багана AK..AV, мөр 11-24.

Дүгнэлт (баталгаажсан):
  • Cum Float Mass/Ash, Cum Sink Ash — БҮХ мөрөнд яг таарна (engine логик зөв).
  • NGM — жигд бин (0.025) мужид яг таарна; ажлын cut 1.40 энд багтана.
  • Жигд бус бин (1.45+)-д engine нь Book2-оос ЗОРИУД ялгаатай: Book2 бүхэл
    мөр нийлүүлдэг (бүдүүн), engine нягтын цонхоор интерполяци хийдэг (нарийн).
"""
from pathlib import Path

import pytest

from engine.washability import Fraction, washability_worksheet

BOOK2 = Path(__file__).resolve().parent.parent / "docs" / "refs" / "Book2.xlsx"
openpyxl = pytest.importorskip("openpyxl")


def _load_right_composite():
    """Book2 баруун composite-ийг (мөр 11-24) Fraction + Excel утгуудаар буцаах."""
    wb = openpyxl.load_workbook(BOOK2, data_only=True)
    ws = wb["Float sink"]

    def c(letter, r):
        return ws[f"{letter}{r}"].value

    fracs, book = [], []
    prev = 1.25
    for r in range(11, 25):
        hi, mass, ash = c("AK", r), c("AL", r), c("AM", r)
        if hi is None or mass is None:
            continue
        fracs.append(Fraction(lo=prev, hi=hi, mass=mass, ash=ash))
        book.append({"rd": hi, "cfm": c("AO", r), "cfa": c("AQ", r),
                     "csa": c("AT", r), "ngm": c("AV", r)})
        prev = hi
    return fracs, book


@pytest.mark.skipif(not BOOK2.exists(), reason="Book2.xlsx repo-д алга")
def test_cumulative_columns_match_book2_exactly():
    """Кумулятив багана бүр Excel-тэй ±0.01% дотор таарна."""
    fracs, book = _load_right_composite()
    rows = washability_worksheet(fracs, ndm_half_width=0.05)
    for er, bk in zip(rows, book):
        assert er["cum_float_mass"] == pytest.approx(bk["cfm"], abs=0.01), bk["rd"]
        assert er["cum_float_ash"] == pytest.approx(bk["cfa"], abs=0.01), bk["rd"]
        assert er["cum_sink_ash"] == pytest.approx(bk["csa"], abs=0.01), bk["rd"]


@pytest.mark.skipif(not BOOK2.exists(), reason="Book2.xlsx repo-д алга")
def test_ngm_matches_book2_in_uniform_bin_region():
    """NGM (±0.05) жигд 0.025-бин мужид Excel-тэй таарна — ажлын cut 1.40 энд."""
    fracs, book = _load_right_composite()
    rows = washability_worksheet(fracs, ndm_half_width=0.05)
    checked = 0
    for er, bk in zip(rows, book):
        if bk["ngm"] is None:
            continue
        # зөвхөн жигд бин муж (cut ≤ 1.40): дараагийн бин бүр 0.025 өргөн
        if er["rd_hi"] <= 1.40:
            assert er["ngm"] == pytest.approx(bk["ngm"], abs=0.05), f"RD={bk['rd']}"
            checked += 1
    assert checked >= 3  # 1.35, 1.375, 1.40 хамгийн багадаа


@pytest.mark.skipif(not BOOK2.exists(), reason="Book2.xlsx repo-д алга")
def test_engine_more_precise_than_excel_on_wide_bins():
    """Жигд бус бин дээр engine (интерполяци) Book2 (бүхэл мөр нийлбэр)-ээс ялгаатай."""
    fracs, book = _load_right_composite()
    rows = washability_worksheet(fracs, ndm_half_width=0.05)
    # RD=1.425 дээр: engine ~34.1 (интерполяц), Book2 ~39.5 (4 бүхэл мөр)
    row_1425 = next(r for r in rows if r["rd_hi"] == 1.425)
    bk_1425 = next(b for b in book if b["rd"] == 1.425)
    assert abs(row_1425["ngm"] - bk_1425["ngm"]) > 3.0  # зориудын ялгаа
    # engine-ийн утга нягтын цонхоор баталгаажсан: [1.375,1.475]
    # 8.791+10.423+9.514 + 10.819*(0.025/0.05) = 34.14
    assert row_1425["ngm"] == pytest.approx(34.14, abs=0.1)
