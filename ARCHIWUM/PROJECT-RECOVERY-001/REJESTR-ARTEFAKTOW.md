# REJESTR ARTEFAKTÓW — PROJECT-RECOVERY-001

Duże pliki, screenshoty, kod i logi pozostają osobnymi artefaktami. MASTER zawiera tylko ich opis i odwołanie.

## 1. Dokumenty recovery

| Artefakt | Status | Rola |
|---|---|---|
| `RECOVERY-REPORT-2026-08-21.md` | `CREATED` | zbiorczy raport dowodowy |
| `WYKRESY/FINAL-AS-BUILT-SPEC.md` | `CREATED` | odzyskany kontrakt wykresów V3 |
| `SKANER-CYKLE-1D/RECOVERED-SPEC.md` | `CREATED` | odzyskany mechanizm listy inwestycyjnej |
| `HASHES-SHA256.txt` | `CREATED AFTER LAST WRITE` | sumy kontrolne paczki z wyłączeniem samego manifestu |

## 2. Screenshoty i referencje

| Plik | Status | Opis |
|---|---|---|
| `REFERENCES/SCANNER-ADMA-NOISE-EXAMPLE.png` | `CONFIRMED` | główny lokalny UI; ADMA jako przykład zbyt płytkiego/szumowego wyniku |
| `REFERENCES/SCANNER-CYCLES-1D-LISTING.png` | `CONFIRMED` | ekran listingu z zakładkami Cycles/Trends/Sectors/Alarm/IPO/Data |
| `REFERENCES/TRADINGVIEW-RBLX-REFERENCE-A.png` | `CONFIRMED` | referencja głębokiego cyklu RBLX i pełnego stosu wskaźników |
| `REFERENCES/TRADINGVIEW-RBLX-REFERENCE-B.png` | `CONFIRMED` | druga referencja RBLX, widok hover/crosshair |
| `REFERENCES/TRADINGVIEW-AAOI-REFERENCE.png` | `CONFIRMED` | referencja AAOI |
| `REFERENCES/TRADINGVIEW-CRM-REFERENCE.png` | `CONFIRMED` | referencja CRM |
| `REFERENCES/TRADINGVIEW-INTU-REFERENCE.png` | `CONFIRMED` | referencja INTU |
| `REFERENCES/TRADINGVIEW-HUBS-REFERENCE.png` | `CONFIRMED` | referencja HUBS |

## 3. Źródła i raporty

Katalog `SOURCE-SNAPSHOT/` zawiera kopie dowodowe changelogu V3, wymagań UI, raportów generacji, finalnej architektury V4.4, generatorów/szablonów i testów. Ich dokładne sumy SHA-256 są zapisane w manifeście.

## 4. Dashboard i dane

| Artefakt | Status | Opis |
|---|---|---|
| `WYKRESY/v3-fast-segmentation/index.html` | `OFFLINE VERIFIED` | odbudowany dashboard 6 × 5 TF |
| `WYKRESY/v3-fast-segmentation/payloads/` | `30/30` | zachowane payloady gotowe do rebuild |
| `WYKRESY/v3-fast-segmentation/results.csv` | `RECOVERED` | wyniki generatora |
| `WYKRESY/v3-fast-segmentation/report.txt` | `RECOVERED` | raport finalnego przebiegu |
| `WYKRESY/v3-fast-segmentation/progress.json` | `RECOVERED` | stan/resume |

## 5. Pochodzenie i trwałość

Oryginały screenshotów znajdowały się w katalogu tymczasowym. Niniejsze kopie są trwałym archiwum projektu. Snapshoty kodu i raportów pochodzą z lokalnego projektu `C:\Skaner wykresów`; projekt źródłowy nie został zmieniony.
