"""Бүх циклийн нэгтгэл (ширхэглэл × циклийн гарц) тест."""
import pytest

from engine.circuit import SizeSplit, plant_yield


def test_split_normalized():
    s = SizeSplit(coarse_pct=70, medium_pct=20, fine_pct=10, oversize_pct=0).normalized()
    assert s.coarse_pct + s.medium_pct + s.fine_pct == pytest.approx(100, abs=0.01)


def test_split_renormalizes_when_not_100():
    s = SizeSplit(coarse_pct=33, medium_pct=11, fine_pct=6).normalized()  # нийлбэр 50
    assert s.coarse_pct == pytest.approx(66, abs=0.1)


def test_plant_yield_weighted_sum():
    """Бүх циклийн гарц = ширхэг × циклийн гарцын жигнэсэн нийлбэр."""
    s = SizeSplit(coarse_pct=66, medium_pct=21, fine_pct=13)
    r = plant_yield(s, coarse_yield_pct=77.2, spiral_recovery_pct=75, flotation_recovery_pct=60)
    expect = 0.66 * 77.2 + 0.21 * 75 + 0.13 * 60
    assert r["total_yield_pct"] == pytest.approx(expect, abs=0.05)


def test_all_coarse_equals_dmc_yield():
    """100% coarse бол нийт гарц = ХСЦ-ийн гарц."""
    s = SizeSplit(coarse_pct=100, medium_pct=0, fine_pct=0)
    r = plant_yield(s, coarse_yield_pct=45.0)
    assert r["total_yield_pct"] == pytest.approx(45.0, abs=0.01)
