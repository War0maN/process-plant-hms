"""
Plant config ачаалагч + бэлэн байдлын шалгалт.

`config/*.yaml`-г уншиж, engine ажиллахад шаардлагатай талбарууд бөглөгдсөн
эсэхийг шалгана. Инженер өгөгдлөө оруулсны дараа "юу дутуу байна" гэдгийг
энэ модулиар шалгаж болно.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

# Engine SP зөвлөмж гаргахад ЗААВАЛ бөглөгдсөн байх ёстой талбарууд.
# (path, тайлбар) — path нь цэгээр тусгаарласан YAML гүн.
CRITICAL_FIELDS: list[tuple[str, str]] = [
    ("pumps.primary.has_vfd", "Primary насос VFD-тэй эсэх — SP логикийн суурь"),
    ("pumps.secondary.has_vfd", "Secondary насос VFD-тэй эсэх"),
    ("medium_density.primary.working_min", "Primary орчны нягт доод хязгаар"),
    ("medium_density.primary.working_max", "Primary орчны нягт дээд хязгаар"),
    ("medium_density.secondary.working_min", "Secondary орчны нягт доод хязгаар"),
    ("medium_density.secondary.working_max", "Secondary орчны нягт дээд хязгаар"),
    ("medium_density.measurement_method", "Нягт хэмжих арга"),
    ("product_targets.coking.target_ash_pct", "Коксжих нүүрсний зорилтот үнс"),
    ("product_targets.thermal.target_ash_pct", "Эрчим хүчний нүүрсний зорилтот үнс"),
    ("plc.brand", "PLC брэнд"),
    ("plc.opc_ua_available", "OPC UA сервер байгаа эсэх"),
]


def load_config(path: str | Path) -> dict[str, Any]:
    """YAML config файлыг dict болгож унших."""
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _get(cfg: dict, dotted: str) -> Any:
    """Цэгээр тусгаарласан гүн утгыг авах ('a.b.c')."""
    cur: Any = cfg
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def missing_critical(cfg: dict) -> list[tuple[str, str]]:
    """Бөглөгдөөгүй (null) эгзэгтэй талбаруудыг буцаах."""
    out = []
    for path, desc in CRITICAL_FIELDS:
        if _get(cfg, path) is None:
            out.append((path, desc))
    return out


def is_engine_ready(cfg: dict) -> bool:
    """Бүх эгзэгтэй талбар бөглөгдсөн бол engine бодит зөвлөмж гаргахад бэлэн."""
    return not missing_critical(cfg)


def readiness_report(path: str | Path) -> str:
    """Хүний унших бэлэн байдлын тайлан гаргах."""
    cfg = load_config(path)
    miss = missing_critical(cfg)
    lines = [f"Plant config: {cfg.get('plant', {}).get('name', '?')}"]
    if not miss:
        lines.append("✅ Бүх эгзэгтэй талбар бөглөгдсөн — engine бэлэн.")
    else:
        lines.append(f"⏳ {len(miss)}/{len(CRITICAL_FIELDS)} эгзэгтэй талбар дутуу:")
        for p, d in miss:
            lines.append(f"   • {p} — {d}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "config/reference_plant_a.yaml"
    print(readiness_report(cfg_path))
