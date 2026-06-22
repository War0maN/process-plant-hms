"""
Blend оновчлол — спекд багтаах хамгийн өндөр гарцтай seam хольцыг хайх.

Ганц seam бүх спекд (ash db, sulphur db, vol daf) ховор тэнцдэг тул хэд хэдэн
seam-ийг харьцаагаар хольж: зорилтот үнсэд хүрэх cut дээр БҮХ хатуу спек
(ash/sulphur/vol) тэнцэх ба гарцыг максимумчилна. CSN нь аддитив биш тул
зөвлөмжид зөвхөн лавлагаа болгон харуулна (хатуу шүүлтэнд оруулахгүй).

Ажиллуулах:  python -m engine.blend_opt
"""
import itertools
from pathlib import Path

from engine import washability as w
from engine.config import load_config
from engine.process_seams import load_all

CFG = Path(__file__).resolve().parent.parent / "config" / "reference_plant_a.yaml"


def _ratio_grid(n, step=20):
    """n seam-ийн хувь хуваарилалт (нийлбэр 100, step%-ийн алхамтай)."""
    levels = list(range(0, 101, step))
    for combo in itertools.product(levels, repeat=n):
        if sum(combo) == 100 and all(c > 0 for c in combo):
            yield combo


def optimize(seams, codes, spec, target_ash, ngm_hw, step=20):
    """codes доторх seam-уудын хослол + харьцааг хайж шилдэг blend буцаах."""
    best = []
    # 1..3 seam хослол
    for r in range(1, min(3, len(codes)) + 1):
        for combo in itertools.combinations(codes, r):
            for ratios in _ratio_grid(r, step) if r > 1 else [(100,)]:
                picks = [{"code": c, "ratio": rt} for c, rt in zip(combo, ratios)]
                fr = w.blend_fractions(picks, seams)
                cut = w.cut_for_product_ash(fr, target_ash)
                y = w.yield_at(fr, cut)
                if y < 1:
                    continue
                chk = w.check_specs(fr, cut, spec)
                hard_ok = all(chk[q]["ok"] for q in ("sulphur", "vol") if q in chk)
                if not hard_ok:
                    continue
                best.append({
                    "picks": picks, "yield": y, "cut": cut,
                    "ngm": w.ngm_at(fr, cut, ngm_hw),
                    "sulphur": chk["sulphur"]["value"],
                    "vol_daf": chk["vol"]["value"],
                    "csn": w.cum_float_quality(fr, cut, "csn"),
                })
    best.sort(key=lambda x: x["yield"], reverse=True)
    return best


def main():
    cfg = load_config(CFG)
    ck = cfg["product_targets"]["coking"]
    target = ck["target_ash_pct"]
    spec = {k: v for k, v in ck["spec"].items() if k != "ash"}
    ngm_hw = cfg["engine"]["ngm_half_width"]
    seams = load_all()
    codes = sorted(seams)

    print("═" * 72)
    print(f" BLEND ОНОВЧЛОЛ — {cfg.get('primary_grade','UHG_MVHCC')} спек")
    print(f" Зорилтот үнс {target}% | S<{spec['sulphur']['max']}(db) | "
          f"VM<{spec['vol']['max']}(daf) | гарц максимумчилна")
    print("═" * 72)
    best = optimize(seams, codes, spec, target, ngm_hw, step=20)
    if not best:
        print(" Хатуу спекд тэнцэх blend олдсонгүй (step=20%).")
        return
    print(f" {'Blend':<26}{'Гарц%':>7}{'cut':>7}{'S':>6}{'VMdaf':>7}{'CSN*':>6}{'NGM%':>6}")
    print("─" * 72)
    seen = set()
    shown = 0
    for b in best:
        key = tuple(sorted((p["code"], p["ratio"]) for p in b["picks"]))
        if key in seen:
            continue
        seen.add(key)
        blend = "+".join(f"{p['code']}:{p['ratio']}" for p in b["picks"])
        csn = b["csn"] or 0
        print(f" {blend:<26}{b['yield']:>7.1f}{b['cut']:>7.3f}{b['sulphur']:>6.2f}"
              f"{b['vol_daf']:>7.1f}{csn:>6.1f}{b['ngm']:>6.1f}")
        shown += 1
        if shown >= 12:
            break
    print("─" * 72)
    print(" * CSN аддитив биш — blend утга ойролцоо (лаб/коксын зуухаар баталгаажуулна).")
    print("═" * 72)


if __name__ == "__main__":
    main()
