"""Config-оор удирдагддаг runner ба washability ачаалагчийн тест."""
from pathlib import Path

import pytest

from engine import config, runner, washability_io as wio

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "reference_plant_a.yaml"
SAMPLE = ROOT / "config" / "sample_washability_DEMO.csv"


def test_load_seams_from_csv_roundtrip():
    seams = wio.seams_from_csv(SAMPLE)
    assert set(seams) == {"4A", "0C", "6B"}
    # seam бүрийн масс ~100%
    for code, fr in seams.items():
        assert sum(f.mass for f in fr) == pytest.approx(100, abs=0.5), code


def test_runner_hits_targets_from_config():
    cfg = config.load_config(CFG)
    seams = wio.seams_from_csv(SAMPLE)
    picks = [{"code": "4A", "ratio": 50}, {"code": "0C", "ratio": 30}, {"code": "6B", "ratio": 20}]
    r = runner.build_recommendation(cfg, picks, seams)
    # config-ийн зорилт (коксжих 10.5) дээр баланс таарах ёстой
    assert r["balance"]["coking"]["ash"] == pytest.approx(10.5, abs=0.1)
    assert r["balance"]["thermal"]["ash"] == pytest.approx(22.5, abs=0.1)
    assert r["targets"]["coking"] == 10.5


def test_runner_uses_config_density_as_sp_base():
    cfg = config.load_config(CFG)
    seams = wio.seams_from_csv(SAMPLE)
    r = runner.build_recommendation(cfg, [{"code": "4A", "ratio": 100}], seams)
    # хэмжсэн үнсгүй → шилжилт 0 → reco_sp = config typical (1.38)
    assert r["primary"]["reco_sp"] == pytest.approx(1.38, abs=1e-6)


def test_contract_analysis_yield_increases_with_ash():
    cfg = config.load_config(CFG)
    seams = wio.seams_from_csv(SAMPLE)
    r = runner.build_recommendation(cfg, [{"code": "4A", "ratio": 100}], seams)
    c = r["contract"]
    assert c is not None
    # 10.0% → 10.5% хүртэл үнс өсгөхөд гарц нэмэгдэнэ (Doc 02 §5.4)
    assert c["yield_gain_base_to_penalty"] > 0
    assert c["reject_ash"] == 11.5


def test_format_mn_produces_text():
    cfg = config.load_config(CFG)
    seams = wio.seams_from_csv(SAMPLE)
    r = runner.build_recommendation(cfg, [{"code": "0C", "ratio": 100}], seams, measured_ash=12.0)
    txt = runner.format_mn(r)
    assert "SP ЗӨВЛӨМЖ" in txt
    assert "КОКСЖИХ" in txt
    assert "Гэрээний шинжилгээ" in txt
