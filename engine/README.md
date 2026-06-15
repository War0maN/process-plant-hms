# Engine — SP зөвлөх цөм (Phase 1)

Энэ бол төслийн "тархи" — Doc 02-ийн домэйн логикийг кодлосон Python модуль.
`mocks/sp-recommendation.html` прототипийн логикийн **шууд порт** (тестээр баталгаажсан).

## Бүтэц

| Файл | Үүрэг |
|------|-------|
| `washability.py` | Цөм логик: blend → ash-pin → two-cut partition → yield/ash/NDM |
| `config.py` | Plant config (Doc 03) ачаалагч + бэлэн байдлын шалгалт |

## Гол санаа (Doc 02 §5)

1. **Blend** — seam-уудын washability-г харьцаагаар жигнэх
2. **Ash-pin** — хэмжсэн үнсэд тааруулж массыг шилжүүлэх залруулга (§5.1)
3. **Two-cut** — нэг муруйг ρ1 (коксжих) ба ρ2 (эрчим хүчний) дээр хувааж SP зөвлөх
4. **NDM** — ялгалтын хүндрэлийн анхааруулга (§5.3)

## Ашиглах

```bash
pip install -r requirements.txt
python -m pytest tests/ -q          # тест ажиллуулах
python -m engine.config             # config бэлэн байдлын тайлан
```

```python
from engine import recommend, grid_fractions

seams = {"4A": grid_fractions(mass_list, ash_list)}
r = recommend(
    picks=[{"code": "4A", "ratio": 100}],
    seams=seams,
    target_coking=10.5,
    target_thermal=24.0,
    sp_primary=1.33,
    sp_secondary=1.52,
    measured_ash=11.2,   # лабын хэмжсэн үнс (байхгүй бол None)
)
print(r["primary"]["reco_sp"], r["secondary"]["reco_sp"])
```

## Статус

- ✅ Цөм логик портлогдсон, 15 тестээр баталгаажсан
- ✅ Plant config бүтэц (Doc 03 → YAML)
- ⏳ Дараагийн: инженерийн өгөгдөл ирмэгц config бөглөх → **түүхэн датан дээр backtest**
  (Doc 04 §7 — "хэрэв өнгөрсөнд ингэж зөвлөсөн бол зөв байх байсан уу")
- ⏳ Дараа: case library (Tier 2), элэгдлийн залруулга (Doc 03 §17)
