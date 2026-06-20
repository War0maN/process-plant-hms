"""Түүхий (raw) washability ачаалагчийн тест — грамм→%, ad→d хөрвүүлэлт."""
import pytest

from engine import washability as w
from engine import washability_io as wio


RAW = [
    {"seam": "T1", "density_hi": "1.30", "mass_g": "154.5", "ash_ad": "11.45", "moisture_ad": "0.80"},
    {"seam": "T1", "density_hi": "1.325", "mass_g": "24.3", "ash_ad": "13.81", "moisture_ad": "0.73"},
    {"seam": "T1", "density_hi": "1.35", "mass_g": "139.2", "ash_ad": "16.35", "moisture_ad": "0.70"},
    {"seam": "T2", "density_hi": "1.30", "mass_g": "200", "ash_ad": "8.0", "moisture_ad": "1.0"},
    {"seam": "T2", "density_hi": "sink", "mass_g": "100", "ash_ad": "60.0", "moisture_ad": "1.0"},
]


def _load():
    col = wio._col_resolver(list(RAW[0].keys()))
    return wio.seams_from_raw_rows(RAW, col)


def test_two_seams_loaded():
    seams = _load()
    assert set(seams) == {"T1", "T2"}


def test_grams_normalized_to_percent():
    seams = _load()
    for code in seams:
        total = sum(f.mass for f in seams[code])
        assert total == pytest.approx(100, abs=0.01), code


def test_ad_to_dry_applied():
    """1.30 бин: 11.45% ad @0.80% чийг → 11.542% dry."""
    fr = _load()["T1"]
    b = next(f for f in fr if abs(f.hi - 1.30) < 1e-9)
    assert b.ash == pytest.approx(11.542, abs=0.01)


def test_dry_column_used_directly_if_present():
    rows = [{"seam": "X", "density_hi": "1.30", "mass_g": "100", "ash_dry": "9.99"}]
    seams = wio.seams_from_raw_rows(rows, wio._col_resolver(list(rows[0].keys())))
    b = next(f for f in seams["X"] if abs(f.hi - 1.30) < 1e-9)
    assert b.ash == pytest.approx(9.99, abs=0.001)
