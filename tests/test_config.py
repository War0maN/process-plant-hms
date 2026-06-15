"""Plant config ачаалагч ба бэлэн байдлын шалгалтын тест."""
from pathlib import Path

from engine import config

CFG_PATH = Path(__file__).resolve().parent.parent / "config" / "reference_plant_a.yaml"


def test_config_loads():
    cfg = config.load_config(CFG_PATH)
    assert cfg["plant"]["name"] == "CHPP — Coarse circuit"
    assert cfg["plant"]["nameplate_capacity_tph"] == 900


def test_confirmed_fields_present():
    cfg = config.load_config(CFG_PATH)
    assert cfg["cyclones"]["primary"]["diameter_mm"] == 1300
    assert cfg["operating_mode"] == "ash-priority"


def test_critical_fields_currently_missing():
    """Дата ороогүй тул бүх эгзэгтэй талбар дутуу — engine хараахан бэлэн биш."""
    cfg = config.load_config(CFG_PATH)
    assert not config.is_engine_ready(cfg)
    assert len(config.missing_critical(cfg)) == len(config.CRITICAL_FIELDS)


def test_filled_config_becomes_ready():
    """Эгзэгтэй талбаруудыг бөглөвөл engine бэлэн болохыг батлах."""
    cfg = config.load_config(CFG_PATH)
    for path, _ in config.CRITICAL_FIELDS:
        cur = cfg
        parts = path.split(".")
        for p in parts[:-1]:
            cur = cur[p]
        cur[parts[-1]] = "filled"
    assert config.is_engine_ready(cfg)
