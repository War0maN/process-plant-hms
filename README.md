# Process Plant — HMS зөвлөх систем (MVP)

Нүүрс баяжуулах үйлдвэрт зориулсан **AI-д суурилсан зөвлөх систем**. Phase 1 = HMS / Dense Medium Cyclone (DMC) дамжлага, **зөвхөн зөвлөмжийн (shadow) горим + гар оруулга**.

> ⚠️ Phase 1-д систем PLC руу автоматаар бичихгүй, PLC-ээс шууд уншихгүй. Бүх SP-ийн шийдвэрийг **оператор** гаргана, систем зөвхөн зөвлөнө. Энэ нь бодит ажиллаж буй үйлдвэр тул аюулгүй байдлын хатуу хязгаар.

## Бүтэц

### `docs/` — суурь баримтууд (MN үндсэн + EN толь)
- `00-open-items-checklist` — нээлттэй асуулт / `[DUK INPUT NEEDED]` backlog
- `01-MVP-scope-HMS` — Phase 1-д юу орох/гарах
- `02-domain-knowledge-HMS` — универсал DMC физик ("брэйн", washability, NDM/NGM, Ep, cut density)
- `03-plant-profile` — Reference Plant A-ийн тохиргоо (циклон, feed, медиа, тоног төхөөрөмж)
- `04-technical-architecture` — системийн архитектур

### `mocks/` — ажиллах HTML прототипүүд (browser-only, backend/PLC байхгүй, JSON + localStorage)
- **`operator-input.html`** — ээлж тутмын оператор оруулга (6 карт: тэжээлийн чанар, процессийн PV, SP, лаб, тоног төхөөрөмж, ээлжийн тэмдэглэл). NDM нь read-only — washability-аас тооцоологдоно.
- **`washability-input.html`** — seam тус бүрийн sink-float reference өгөгдөл. LIMN тайлантай нийцсэн нягтын алхам; cut density дээр yield-ash, **NGM (±w)** автоматаар тооцоолж муруй зурна.
- **`sp-recommendation.html`** — engine demo: blend washability → 2ц грэб үнсээр ash-pinning залруулга (масс шилжүүлэх, Doc 02 §5.1) → cut density / media SP **зөвлөмж**.

### `_skills-backup/` — төслийн persona / домэйн skill (Claude Code)

## Архитектурын зарчмууд
- **Engine нь өгөгдлийн эх үүсвэрээс үл хамаарна** — өнөөдөр гар оруулга, маргааш PLC tag, дотоод логик адил.
- **Хоёр давхаргат документ:** Doc 02 = универсал физик (ямар ч DMC үйлдвэрт), Doc 03 = тухайн үйлдвэрийн тоо.
- **Хоёр түвшний SP загвар:** washability = физик хязгаар (Tier 1); угаалтын түүхэн кейс сан = эмпирик залруулга (Tier 2).

## Статус
Phase 1 MVP — документ + интерактив прототип. Backend/engine хэрэгжүүлэлт дараагийн алхам.
