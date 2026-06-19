"""
Washability worksheet ба ad→d хөрвүүлэлт, NGM конвенцийн тест.

Book2-ын яг тоо ирэхэд энд ground-truth fixture нэмж тулгана. Одоогоор
стандарт томьёоны ДОТООД НИЙЦЛИЙГ (invariants) болон бие даан баталгаажих
утгуудыг (ISO 1170 ad→d) шалгана.
"""
import pytest

from engine import washability as w
from engine.washability import grid_fractions

# tests/test_washability.py-тай ижил demo seam
SEAM = {"mass": [30, 14, 11, 9, 7, 6, 5, 4, 4, 3, 2, 2, 1.5, 1.5],
        "ash": [8, 10, 12, 14, 17, 20, 23, 28, 36, 45, 55, 63, 73, 83]}


def fr():
    return grid_fractions(SEAM["mass"], SEAM["ash"])


def test_ad_to_dry_increases_ash():
    """ISO 1170: чийг хасахад үнс өснө. 11.45% @ 0.80% → 11.54%."""
    assert w.to_dry_basis(11.45, 0.80) == pytest.approx(11.542, abs=0.005)
    # чийг 0 бол өөрчлөгдөхгүй
    assert w.to_dry_basis(10.0, 0.0) == 10.0
    # үргэлж ad-аас их буюу тэнцүү
    assert w.to_dry_basis(15.0, 5.0) > 15.0


def test_ngm_convention_doubles_roughly():
    """±0.10 цонх нь ±0.05-аас (ойролцоогоор) их утга өгнө — конвенц чухал."""
    f = fr()
    narrow = w.ngm_at(f, 1.40, half_width=0.05)
    wide = w.ngm_at(f, 1.40, half_width=0.10)
    assert wide > narrow > 0


def test_ngm_interpolates_irregular_bins():
    """1.50-1.60 (0.1 өргөн) бин дээр ±0.05 цонх биний хагасыг авах ёстой."""
    f = fr()
    # 1.55 төвтэй ±0.05 → яг (1.50,1.60] бин бүхэлдээ
    full = w.ngm_at(f, 1.55, half_width=0.05)
    # тэр бин ганцаараа (mass=4) нийт 100-аас 4% байх ёстой орчим
    assert full == pytest.approx(4.0, abs=0.5)


def test_worksheet_columns_and_consistency():
    rows = w.washability_worksheet(fr(), ndm_half_width=0.10)
    assert len(rows) == len(w.DENS_HI)
    # cum_float_mass монотон өснө, эцэст нь ~100
    cfm = [r["cum_float_mass"] for r in rows]
    assert cfm == sorted(cfm)
    assert cfm[-1] == pytest.approx(100, abs=0.5)
    # cum_sink_mass эхэндээ ~100 (бүх материал хүнд талд)
    assert rows[0]["cum_sink_mass"] == pytest.approx(100, abs=0.5)
    # хамгийн доод фракцын cum_float_ash = нийт дундаж үнс
    total_ash = w.weighted_ash(fr())
    assert rows[-1]["cum_float_ash"] == pytest.approx(total_ash, abs=0.05)


def test_worksheet_inv_rd():
    rows = w.washability_worksheet(fr())
    # эхний фракц 0..1.30 → mid (1.15+1.30)/2=1.225 → 1/1.225=0.816
    assert rows[0]["inv_rd"] == pytest.approx(1 / ((1.15 + 1.30) / 2), abs=0.01)
