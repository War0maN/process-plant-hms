"""Нэмэлт чанарын үзүүлэлт (VM, S, CSN) ба спек шалгалтын тест."""
import pytest

from engine import washability as w
from engine.washability import Fraction


def _fr():
    # 3 фракц: хөнгөн (цэвэр), дунд, хүнд (чулуу)
    return [
        Fraction(0, 1.30, mass=40, ash=8.0, quals={"vol": 24, "sulphur": 0.5, "csn": 7}),
        Fraction(1.30, 1.40, mass=30, ash=14.0, quals={"vol": 22, "sulphur": 0.6, "csn": 4}),
        Fraction(1.40, 99, mass=30, ash=55.0, quals={"vol": 12, "sulphur": 0.9, "csn": 0}),
    ]


def test_cum_float_quality_is_mass_weighted():
    fr = _fr()
    # cut 1.40 → эхний 2 фракц (40+30=70 масс)
    vol = w.cum_float_quality(fr, 1.40, "vol")
    expect = (40 * 24 + 30 * 22) / 70
    assert vol == pytest.approx(expect, abs=0.01)


def test_product_qualities_includes_ash():
    fr = _fr()
    q = w.product_qualities(fr, 1.40, ["vol", "sulphur"])
    assert "ash" in q and "vol" in q and "sulphur" in q
    assert q["ash"] == pytest.approx((40 * 8 + 30 * 14) / 70, abs=0.01)


def test_check_specs_pass_and_fail():
    fr = _fr()
    # ash 10.57 — хатуу max 10.0 дээр УНАНА; sulphur/vol спекд таарна
    res = w.check_specs(fr, 1.40, {"ash": {"max": 10.0}, "sulphur": {"max": 0.8}, "vol": {"min": 20}})
    assert res["ash"]["ok"] is False        # 10.57 > 10.0
    assert res["sulphur"]["ok"] is True     # 0.543 ≤ 0.8
    assert res["vol"]["ok"] is True         # 23.14 ≥ 20


def test_ash_within_spec_true():
    fr = _fr()
    res = w.check_specs(fr, 1.40, {"ash": {"max": 12}})
    # (8*40+14*30)/70 = 10.57 ≤ 12
    assert res["ash"]["value"] == pytest.approx(10.571, abs=0.01)
    assert res["ash"]["ok"] is True


def test_csn_flagged_non_additive():
    fr = _fr()
    res = w.check_specs(fr, 1.40, {"csn": {"min": 5}})
    assert res["csn"]["additive"] is False  # CSN массаар дунджилж болохгүй
