# FINAL AS-BUILT SPEC — WYKRESY V3 (ODZYSKANE)

**Zakres:** finalny szybki dashboard V3 oraz potwierdzony kontrakt renderera  
**Build końcowy:** `2026-08-16-r594`  
**Status:** `RECOVERED / OFFLINE VERIFIED`  
**Integracja produkcyjna:** `NOT IMPLEMENTED`

## 1. Artefakt wykonywalny

- dashboard: `v3-fast-segmentation/index.html`;
- payloady: `v3-fast-segmentation/payloads/*.json`;
- wynik: 6 spółek × 5 interwałów = `30/30` par;
- odbudowa z payloadów: `PASS`, 6,93 s, bez rynku i bez baz produkcyjnych.

## 2. Zestaw i interwały

Spółki: `RBLX`, `AAOI`, `INTU`, `NVDA`, `PLTR`, `ADTN`.

Interwały w przełączniku: `30m | 1H | 2H | 4H | 1D`.

- domyślny interwał: `1D`;
- wybór przechowywany w wersjonowanym kluczu lokalnym;
- przeglądarka nie wykonuje ponownego pobierania ani obliczania wskaźników;
- wszystkie przyciski TF mają pozostać widoczne.

## 3. Dane i zakres

- źródło providerowe w przebiegu generacyjnym: Massive;
- wykres 1D: dane kanoniczne;
- niższe TF: dane budowane ze źródła 30m zgodnie z odzyskanym pipeline;
- widok finalnego fast dashboardu: 250 świec;
- historia 1D do obliczeń: 1100 dni;
- historia niższych TF: 400 dni;
- wcześniejsza walidacja: 120 świec widocznych i produkcyjny pre-roll 500;
- feature schema: `V3_FEATURE_ATOMIC_1`, 39 kolumn;
- przeglądarka tylko prezentuje gotowy payload.

## 4. Panele i wskaźniki

1. cena OHLC + wolumen;
2. `WMA 9`, `EMA 20`, `EMA 50`, `EMA 100`, `EMA 200`;
3. MACD;
4. RSI 14 close;
5. Stochastic 14/3/3;
6. Accumulation/Distribution.

Kolory odzyskane dla kluczowych EMA:

- EMA20 — czerwony;
- EMA50 — pomarańczowy/złoty;
- EMA100 — turkusowy, linia subtelna 1 px.

Dokładne wartości HEX wszystkich elementów należy brać z zachowanego szablonu źródłowego; nie wolno odtwarzać ich z pamięci.

## 5. Proporcje i skale — finalne reguły

- punkt bazowy r554: cena 54%, MACD 17%, RSI 11,5%, Stoch 10,5%, A/D 7%;
- r559 nadpisuje wcześniejszą równość RSI/Stoch: panel RSI ma być 1,5× wyższy od Stoch, aby kanały 30–70 i 20–80 miały podobną wysokość pikselową;
- RSI: wypełnienie tylko poza 30/70;
- Stoch: poziomy 20/50/80;
- MACD: autoskala widocznego zakresu, wspólna oś, 10% zapasu, minimum 28% wysokości po każdej stronie zera;
- A/D: kumulacyjny CLV/MFV zgodnie z zachowanym szablonem.

Jeżeli wartości procentowe r554 kolidują z finalnym CSS r594, kod/szablon r594 ma pierwszeństwo jako późniejszy AS-BUILT.

## 6. Segmentacja i zdarzenia MACD

- zaakceptowany wariant segmentacji: `B`;
- próg: `0,25 × odchylenie standardowe MACD`;
- brak minimalnego odstępu między zdarzeniami;
- kropka wzrostowego przecięcia MACD/Signal jest umieszczana na barze zdarzenia `i`, dokładnie w osi crosshair/tooltip;
- r590 nadpisuje wcześniejszą interpolację położenia kropki;
- historyczne excursion są prezentowane tylko na `1D`;
- renderowana jest jedna największa historyczna excursion;
- lokalne doliny zasilają profil, średnią, medianę i ranking.

Wyniki dla finalnego zestawu:

| Symbol | Liczba dolin |
|---|---:|
| RBLX | 7 |
| AAOI | 7 |
| INTU | 6 |
| NVDA | 10 |
| PLTR | 8 |
| ADTN | 5 |

## 7. Zachowanie generatora

- przyrostowy, atomowy zapis dashboardu;
- usuwanie stale dashboard przed nową pełną generacją;
- build stamp;
- resume i pomijanie kompletnych symboli;
- self-repair/selective regeneration brakujących TF;
- tryb rebuild z gotowych payloadów;
- możliwość pracy na jednym symbolu w narzędziu walidacyjnym.

## 8. Testy i dowody

Finalny zapis regresji:

- `test_chart_validation`: `63 PASS / 0 FAIL`;
- `test_multi_tf`: `18 PASS / 0 FAIL`;
- `test_macd_excursions`: `30 PASS / 0 FAIL`;
- całość: `394 PASS / 0 FAIL`.

W ramach recovery parser AST przeszedł dla `config.py`, `chart_validation.py`, `fast_segmentation.py` i `chart_validation_template.py`.

## 9. Granica produkcyjna

Ten dokument nie stwierdza, że V3 działa w głównym interfejsie. Główne UI używa obecnie starszego `/candles/{symbol}`. Integracja wymaga osobnego SPEC/API contract i testu pionowego:

`wybór spółki → dane 5 TF → payload V3 → renderer → interakcja → last-good/error state`.

## 10. Źródła dowodowe

- `../SOURCE-SNAPSHOT/CHANGELOG-V3.md`;
- `../SOURCE-SNAPSHOT/WYMAGANIE-V3-1B-UI.md`;
- `../SOURCE-SNAPSHOT/RAPORT-V3-1B-KONTROLA-WYKRESOW.txt`;
- `../SOURCE-SNAPSHOT/chart_validation.py`;
- `../SOURCE-SNAPSHOT/chart_validation_template.py`;
- `../SOURCE-SNAPSHOT/fast_segmentation.py`;
- `../SOURCE-SNAPSHOT/test_chart_validation.py`;
- `../SOURCE-SNAPSHOT/test_tf_switcher.py`;
- payloady, `results.csv`, raport i progress w `v3-fast-segmentation/`.
