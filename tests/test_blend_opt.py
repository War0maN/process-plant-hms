"""Blend оновчлолын тест (жижиг синтетик seam дээр, хурдан)."""
import pytest

from engine.blend_opt import optimize
from engine.washability import grid_fractions


def _seam(ash_light, ash_heavy, s, vm, csn):
    # энгийн 4-бин seam: хөнгөн цэвэр, хүнд бохир
    mass = [40, 25, 20, 15] + [0] * 10
    ash = [ash_light, ash_light + 4, ash_heavy, ash_heavy + 20] + [None] * 10
    fr = grid_fractions(mass, ash)
    for f in fr:
        if f.mass:
            f.quals = {"sulphur": s, "vol": vm, "csn": csn}
    return fr


def _seams():
    return {
        "CLEAN": _seam(7, 12, 0.5, 22, 7),     # цэвэр, бага S/VM
        "DIRTY": _seam(9, 16, 0.9, 28, 5),     # бохир, өндөр S/VM
    }


SPEC = {"sulphur": {"max": 0.65}, "vol": {"max": 27.0, "basis": "daf"}, "csn": {"min": 7.0}}


def test_optimize_returns_spec_passing_sorted():
    best = optimize(_seams(), ["CLEAN", "DIRTY"], SPEC, 10.5, 0.05, step=25)
    assert best, "спекд тэнцэх blend олдох ёстой"
    # бүх үр дүн хатуу спек (S, VM) тэнцсэн байх
    for b in best:
        assert b["sulphur"] <= 0.65 + 1e-9
        assert b["vol_daf"] <= 27.0 + 1e-9
    # гарцаар буурахаар эрэмбэлэгдсэн
    ys = [b["yield"] for b in best]
    assert ys == sorted(ys, reverse=True)


def test_pure_dirty_excluded():
    """Зөвхөн бохир seam (S 0.9 > 0.65) хатуу спекд унах ёстой."""
    best = optimize({"DIRTY": _seams()["DIRTY"]}, ["DIRTY"], SPEC, 10.5, 0.05)
    assert best == []
