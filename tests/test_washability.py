"""
Engine портын баталгаажуулалт.

`mocks/sp-recommendation.html` доторх demo seam-уудыг (4A/0C/6B) ашиглаж,
Python порт нь JS engine-тэй ижил математик зарчмаар ажиллаж байгааг шалгана.
Тестүүд нь үр дүнгийн ДОТООД НИЙЦЛИЙГ (invariants) шалгана — учир нь bisection,
ash-pin зэрэг нь хатуу томьёонд тулгуурладаг тул эдгээр шинж нь зөв портыг батална.
"""
import math

import pytest

from engine import washability as w
from engine.washability import Fraction

# mocks/sp-recommendation.html EMBED_SEAMS-тэй яг ижил.
EMBED_SEAMS = {
    "4A": {"mass": [30, 14, 11, 9, 7, 6, 5, 4, 4, 3, 2, 2, 1.5, 1.5],
           "ash": [8, 10, 12, 14, 17, 20, 23, 28, 36, 45, 55, 63, 73, 83]},
    "0C": {"mass": [20, 12, 11, 9, 8, 8, 7, 6, 5, 3, 3, 3, 2.5, 2.5],
           "ash": [9, 11, 13, 16, 19, 22, 25, 30, 38, 47, 57, 64, 74, 84]},
    "6B": {"mass": [10, 7, 8, 9, 10, 10, 9, 8, 7, 4, 3, 3, 4, 8],
           "ash": [10, 13, 15, 18, 21, 24, 27, 32, 40, 49, 59, 65, 75, 85]},
}


def seams():
    return {c: w.grid_fractions(s["mass"], s["ash"]) for c, s in EMBED_SEAMS.items()}


def test_grid_has_full_density_ladder():
    fr = w.grid_fractions(EMBED_SEAMS["4A"]["mass"], EMBED_SEAMS["4A"]["ash"])
    assert len(fr) == len(w.DENS_HI)
    assert fr[0].lo == 0 and fr[0].hi == 1.30
    assert fr[-1].hi == 99  # нээлттэй sink фракц


def test_seam_mass_sums_to_100():
    for code, s in EMBED_SEAMS.items():
        assert sum(s["mass"]) == pytest.approx(100, abs=0.01), code


def test_blend_conserves_mass():
    picks = [{"code": "4A", "ratio": 50}, {"code": "0C", "ratio": 30}, {"code": "6B", "ratio": 20}]
    fr = w.blend_fractions(picks, seams())
    total = sum(f.mass for f in fr)
    assert total == pytest.approx(100, abs=0.01)


def test_blend_ash_between_component_ashes():
    picks = [{"code": "4A", "ratio": 50}, {"code": "6B", "ratio": 50}]
    fr = w.blend_fractions(picks, seams())
    blend_ash = w.weighted_ash(fr)
    ash_4a = w.weighted_ash(seams()["4A"])
    ash_6b = w.weighted_ash(seams()["6B"])
    assert min(ash_4a, ash_6b) <= blend_ash <= max(ash_4a, ash_6b)


def test_cut_for_product_ash_actually_hits_target():
    fr = w.blend_fractions([{"code": "4A", "ratio": 100}], seams())
    target = 10.5
    cut = w.cut_for_product_ash(fr, target)
    assert w.clean_ash_at(fr, cut) == pytest.approx(target, abs=0.05)


def test_higher_cut_gives_more_yield_and_more_ash():
    """Doc 02 §5.4 — cut өсгөхөд гарц ↑, баяжмалын үнс ↑."""
    fr = w.blend_fractions([{"code": "0C", "ratio": 100}], seams())
    y_lo, a_lo = w.yield_at(fr, 1.40), w.clean_ash_at(fr, 1.40)
    y_hi, a_hi = w.yield_at(fr, 1.55), w.clean_ash_at(fr, 1.55)
    assert y_hi > y_lo
    assert a_hi > a_lo


def test_ash_pin_raises_curve_when_measured_above_predicted():
    """Хэмжсэн үнс > таамаг → масс өндөр нягт руу налж, корр. үнс өснө."""
    fr = w.blend_fractions([{"code": "4A", "ratio": 100}], seams())
    pred = w.weighted_ash(fr)
    k = w.solve_tilt(fr, pred + 3.0)
    corrected = w.apply_tilt(fr, k)
    assert k > 0
    assert w.weighted_ash(corrected) == pytest.approx(pred + 3.0, abs=0.05)
    assert sum(f.mass for f in corrected) == pytest.approx(100, abs=0.01)


def test_partition_three_products_conserve_mass():
    fr = w.blend_fractions([{"code": "4A", "ratio": 60}, {"code": "0C", "ratio": 40}], seams())
    c1 = w.cut_for_product_ash(fr, 10.5)
    c2 = w.cut_for_middling_ash(fr, c1, 24.0)
    p = w.partition(fr, c1, c2)
    total_yield = p["coking"]["yield"] + p["thermal"]["yield"] + p["reject"]["yield"]
    assert total_yield == pytest.approx(100, abs=0.1)
    # коксжих хамгийн цэвэр, хаягдал хамгийн бохир
    assert p["coking"]["ash"] < p["thermal"]["ash"] < p["reject"]["ash"]


def test_recommend_default_demo_runs_and_is_consistent():
    picks = [{"code": "4A", "ratio": 50}, {"code": "0C", "ratio": 30}, {"code": "6B", "ratio": 20}]
    r = w.recommend(picks, seams(), measured_ash=None)
    # хэмжсэн үнсгүй → залруулга 0, base==corr
    assert r["tilt_k"] == 0.0
    assert r["primary"]["nudge"] == pytest.approx(0.0, abs=1e-9)
    assert 1.20 <= r["primary"]["corr_cut"] <= 2.30
    assert r["secondary"]["corr_cut"] > r["primary"]["corr_cut"]


def test_recommend_dirty_feed_lowers_primary_cut():
    """Тэжээл бохирдвол (хэмжсэн > таамаг) primary cut буурч ash-аа барина."""
    picks = [{"code": "4A", "ratio": 50}, {"code": "0C", "ratio": 30}, {"code": "6B", "ratio": 20}]
    base = w.recommend(picks, seams(), measured_ash=None)
    pred = base["pred_ash"]
    dirty = w.recommend(picks, seams(), measured_ash=pred + 2.0)
    assert dirty["tilt_k"] > 0
    assert dirty["primary"]["nudge"] < 0  # cut буурна
    assert dirty["primary"]["reco_sp"] < 1.33  # SP буурна


def test_ngm_window_is_a_percentage():
    fr = w.blend_fractions([{"code": "6B", "ratio": 100}], seams())
    ngm = w.ngm_at(fr, 1.45, 0.10)
    assert 0 <= ngm <= 100
