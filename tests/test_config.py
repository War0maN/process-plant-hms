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


def test_config_is_now_engine_ready():
    """Инженерийн өгөгдөл орсон тул бүх эгзэгтэй талбар бөглөгдсөн — engine бэлэн."""
    cfg = config.load_config(CFG_PATH)
    assert config.is_engine_ready(cfg), config.missing_critical(cfg)


def test_confirmed_operating_values():
    """Инженерийн баталгаажуулсан гол утгууд config-д орсон эсэх."""
    cfg = config.load_config(CFG_PATH)
    assert cfg["medium_density"]["primary"]["typical"] == 1.38
    assert cfg["plc"]["brand"] == "Allen-Bradley ControlLogix 5570"
    assert cfg["plc"]["opc_ua_available"] is True
    assert cfg["pumps"]["primary"]["has_vfd"] is True
    assert cfg["product_targets"]["coking"]["target_ash_pct"] == 10.5
    assert cfg["product_targets"]["coking"]["contract"]["penalty_threshold_pct"] == 10.5
    # online ash analyzer байгаа нь батлагдсан — real-time proxy
    assert cfg["plc"]["tags"]["online_ash_analyzer"]["measured"] is True


def test_missing_when_critical_nulled():
    """Эгзэгтэй талбарыг null болговол readiness буурахыг батлах (логик шалгалт)."""
    cfg = config.load_config(CFG_PATH)
    cfg["plc"]["brand"] = None
    assert not config.is_engine_ready(cfg)
