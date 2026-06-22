"""Элэгдлийн үнэлгээ ба SP залруулгын тест (Doc 03 §13, §17)."""
from engine.wear import assess_wear, wear_status

BASE = {"spigot": [4000, 6000], "vortex_finder": [4000, 6000],
        "pump_impeller": [3000, 4500], "cone_liner": [12000, 15000]}


def test_status_bands():
    assert wear_status(3000, 4000, 6000) == "ok"
    assert wear_status(5000, 4000, 6000) == "soon"
    assert wear_status(6500, 4000, 6000) == "overdue"
    assert wear_status(None, 4000, 6000) == "unknown"


def test_overdue_alert():
    we = assess_wear({"spigot": {"hours": 6500}}, BASE)
    msgs = [a["status"] for a in we["alerts"]]
    assert "overdue" in msgs


def test_soon_alert_and_pump_nudge():
    we = assess_wear({"spigot": {"hours": 5200}}, BASE)
    assert any(a["status"] == "soon" for a in we["alerts"])
    assert we["pump_speed_nudge_pct"] > 0  # spigot элэгдвэл насос +


def test_fresh_equipment_no_alert_no_nudge():
    we = assess_wear({"spigot": {"hours": 1000}, "vortex_finder": {"hours": 1000},
                      "pump_impeller": {"hours": 500}, "cone_liner": {"hours": 2000}}, BASE)
    assert we["alerts"] == []
    assert we["pump_speed_nudge_pct"] == 0.0


def test_nudge_bounded():
    we = assess_wear({"spigot": {"hours": 99999}}, BASE)
    assert we["pump_speed_nudge_pct"] <= 2.0


def test_bore_wear_overdue():
    from engine.wear import bore_wear
    r = bore_wear(590, 540)  # spigot +9.3% (бодит Ухаа Худаг)
    assert r["status"] == "overdue"
    assert r["pump_speed_nudge_pct"] > 0


def test_bore_wear_fresh_ok():
    from engine.wear import bore_wear
    r = bore_wear(545, 540)  # бараг шинэ
    assert r["status"] == "ok"
    assert r["pump_speed_nudge_pct"] >= 0


def test_bore_wear_unknown():
    from engine.wear import bore_wear
    assert bore_wear(None, 540)["status"] == "unknown"
