"""
НЭГДСЭН SP ЗӨВЛӨМЖ — washability + live variables + 7 хоногийн элэгдэл.

Энэ нь оператор юу харахыг бүрэн харуулна:
  washability (seam/blend) → зорилтот үнс + спек → cut density
    → online ash залруулга (ash-pin) → орчны нягт SP
    → элэгдлийн залруулга → насосны хурд SP
    → бүтээгдэхүүний урьдчилсан чанар + сэлбэгийн сануулга

Жишээ live/wear утга ашигласан (◀ PLACEHOLDER) — бодит утгаар солино.
Ажиллуулах:  python -m engine.full_sp
"""
from pathlib import Path

from engine import washability as w
from engine.config import load_config
from engine.process_seams import load_all
from engine.wear import assess_wear

CFG = Path(__file__).resolve().parent.parent / "config" / "reference_plant_a.yaml"


def line(c="─", n=68):
    print(c * n)


def main():
    cfg = load_config(CFG)
    ck = cfg["product_targets"]["coking"]
    target = ck["target_ash_pct"]
    spec = {k: v for k, v in ck["spec"].items() if k != "ash"}
    contract = ck["contract"]
    ngm_hw = cfg["engine"]["ngm_half_width"]
    baselines = cfg["wear_baseline_hours"]

    # === Сонгосон тэжээл (blend) ===
    seams = load_all()
    picks = [{"code": "3AU", "ratio": 60}, {"code": "4C", "ratio": 40}]  # ◀ жишээ blend
    fr = w.blend_fractions(picks, seams)
    feed_ash_wash = w.weighted_ash(fr)

    # === LIVE VARIABLES (◀ PLACEHOLDER — бодит PLC утгаар солино) ===
    live_density_sp = 1.380       # одоогийн орчны нягт (DIT_103)
    live_pump_speed = 85.0        # одоогийн насосны хурд % (SIT_104)
    online_feed_ash = 19.5        # AIT_105 тэжээлийн бодит үнс %

    # === WEEKLY WEAR (◀ PLACEHOLDER — 7 хоногийн хэмжилт) ===
    measured_wear = {
        "spigot": {"hours": 5200, "bore_mm": 561},     # baseline 4000-6000
        "vortex_finder": {"hours": 5200},
        "pump_impeller": {"hours": 3800},
        "cone_liner": {"hours": 9000},
    }

    line("═")
    print(" НЭГДСЭН SP ЗӨВЛӨМЖ — Ухаа Худаг ХСЦ (коксжих)")
    line("═")
    print(f" Тэжээл (blend): " + ", ".join(f"{p['code']} {p['ratio']}%" for p in picks))
    print(f" Washability үнс: {feed_ash_wash:.1f}%  |  Online ash (AIT_105): {online_feed_ash:.1f}%")
    print(f" Зорилт: коксжих үнс {target}%  |  Спек: Sd<{spec['sulphur']['max']}, "
          f"VMd<{spec['vol']['max']}, CSN≥{spec['csn']['min']}")
    print()

    # === 1. Cut density (washability) + ash-pin (online) ===
    base_cut = w.cut_for_product_ash(fr, target)
    k = w.solve_tilt(fr, online_feed_ash) if online_feed_ash > 0 else 0
    corr = w.apply_tilt(fr, k)
    corr_cut = w.cut_for_product_ash(corr, target)
    nudge_density = corr_cut - base_cut
    reco_density = live_density_sp + nudge_density

    line()
    print(" 1. ОРЧНЫ НЯГТ SP (washability + online ash)")
    line()
    print(f"   Washability cut: {base_cut:.3f}  →  online-залруулсан cut: {corr_cut:.3f}")
    print(f"   Орчны нягт SP:  {live_density_sp:.3f}  →  {reco_density:.3f}  "
          f"({nudge_density:+.3f})")

    # === 2. Бүтээгдэхүүний урьдчилсан чанар + спек ===
    y = w.yield_at(corr, corr_cut)
    ash = w.clean_ash_at(corr, corr_cut)
    ngm = w.ngm_at(corr, corr_cut, ngm_hw)
    chk = w.check_specs(corr, corr_cut, spec)
    line()
    print(" 2. БҮТЭЭГДЭХҮҮНИЙ УРЬДЧИЛСАН ЧАНАР")
    line()
    print(f"   Гарц: {y:.1f}%   Үнс: {ash:.2f}%   NGM(±{ngm_hw}): {ngm:.1f}%")
    def fmt(q, unit=""):
        v = chk[q]["value"]; ok = chk[q]["ok"]
        mark = "—" if ok is None else ("✓" if ok else "✗ СПЕК ЗӨРЧИВ")
        return f"{v:.2f}{unit} {mark}" if v is not None else "—"
    print(f"   Хүхэр Sd: {fmt('sulphur')}   |   VMd: {fmt('vol')}   |   CSN: {fmt('csn')} (лавлагаа)")
    # гэрээний бүс
    if ash > contract["rejection_threshold_pct"]:
        print(f"   ⚠ Үнс {ash:.2f}% > татгалзах {contract['rejection_threshold_pct']}% — БҮТЭЭГДЭХҮҮН ЭРСДЭЛТЭЙ")
    elif ash > contract["penalty_threshold_pct"]:
        print(f"   ⚠ Үнс {ash:.2f}% > penalty {contract['penalty_threshold_pct']}% — торгууль $!{contract['penalty_usd_per_t']}/т")
    if ngm > cfg["engine"]["ngm_warn_threshold_pct"]:
        print(f"   ⚠ NGM {ngm:.1f}% өндөр — нягтыг хатуу (±0.005) бариул")

    # === 3. Элэгдлийн залруулга + сэлбэгийн сануулга ===
    we = assess_wear(measured_wear, baselines)
    reco_pump = live_pump_speed + we["pump_speed_nudge_pct"]
    line()
    print(" 3. НАСОСНЫ ХУРД SP (элэгдлийн залруулга, Doc 03 §17)")
    line()
    print(f"   Насосны хурд: {live_pump_speed:.1f}%  →  {reco_pump:.1f}%  "
          f"({we['pump_speed_nudge_pct']:+.1f}%)  [spigot элэгдэлд даралт бариулна]")
    line()
    print(" 4. СЭЛБЭГИЙН САНУУЛГА (Doc 03 §13)")
    line()
    if we["alerts"]:
        for a in we["alerts"]:
            print(f"   • {a['msg']}")
    else:
        print("   Сануулга алга — бүх тоног төхөөрөмж хэвийн.")
    line("═")
    print(" ЗӨВЛӨМЖ: орчны нягт SP={:.3f}, насосны хурд SP={:.1f}%  → Accept/Reject/Modify"
          .format(reco_density, reco_pump))
    line("═")
    print(" ◀ Live/wear утгууд жишээ — бодит PLC + 7 хоногийн хэмжилтээр солино.")


if __name__ == "__main__":
    main()
