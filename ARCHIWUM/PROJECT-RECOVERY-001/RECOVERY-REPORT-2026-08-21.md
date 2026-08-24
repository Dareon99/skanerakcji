# PROJECT RECOVERY 001 — RAPORT ODZYSKANIA

**Projekt:** Skaner wykresów  
**Okres objęty odzyskiwaniem:** ostatnie 10 dni dostępnej historii i lokalnych artefaktów, ze szczególnym uwzględnieniem 2026-08-15–2026-08-21  
**Data wykonania:** 2026-08-21  
**Tryb:** read-only dla projektu i baz; zapis wyłącznie do niniejszego archiwum  
**Wynik:** `RECOVERED WITH KNOWN GAPS`

## 1. Wynik wykonawczy

Praca nad wykresami nie została utracona. Zachowane są kod, testy, raporty, payloady i referencje. Dashboard V3 został odbudowany offline z istniejących danych bez pobierania rynku i bez zapisu do baz produkcyjnych.

| Dowód | Wynik |
|---|---|
| Payloady | `30/30` |
| Zestaw spółek | `6/6` |
| Interwały na spółkę | `5/5` |
| Odbudowa dashboardu | `PASS`, kod wyjścia 0 |
| Czas odbudowy offline | 6,93 s |
| Finalna regresja zapisana w źródłach | `394 PASS / 0 FAIL` |
| Parser AST kluczowych plików | `PASS` |
| Modyfikacje projektu/baz | zero |

Odbudowany dashboard: `WYKRESY/v3-fast-segmentation/index.html`.

## 2. Ustalona przyczyna zatrzymania

### 2.1. Przyczyna operacyjna — `CONFIRMED`

- brak procesu nasłuchującego na porcie `8000`;
- brak zadań autostartu o nazwie `SkanerWykresow*`;
- główna aplikacja jest więc wyłączona;
- frontend żąda danych wykresowych z lokalnego API i bez niego nie może ich otrzymać.

### 2.2. Luka integracyjna — `CONFIRMED`

- główny frontend nadal korzysta z `/candles/{symbol}`;
- endpoint korzysta ze starszej ścieżki danych i wskaźników;
- V3 było rozwijane jako osobny dashboard walidacyjny;
- raporty V3 jawnie oznaczają brak integracji z produkcją;
- finalny renderer V3 i przełącznik pięciu interwałów nie są częścią głównego ekranu.

### 2.3. Co nie jest przyczyną potwierdzoną

Nie ma dowodu, że sam stan `massive_traffic_manager_enabled = 0` blokuje wykresy. Manager OFF był zaakceptowanym stanem r599. Serwer OFF jest stanem odrębnym.

## 3. Oś odzyskanych prac wykresowych

| Wersje | Odzyskany zakres |
|---|---|
| r541–r543 | kanoniczne dane 1D, kontrola jakości, produkcyjny pre-roll 500 |
| r544 | atomowy silnik cech, 39 kolumn, bez scoringu/fetch/persistence |
| r545 | walidacja wykresów dla 19 spółek |
| r546–r547 | korekta kanonicznych H/L przez porcjowane dane 30m |
| r549 | pierwszy dashboard UI |
| r552–r553 | naprawa VERSION/ścieżek, build stamp, usuwanie starego dashboardu, tryb jednego symbolu |
| r554 | panel A/D i zaakceptowany układ wizualny |
| r555 | przyrostowy, atomowy zapis dashboardu |
| r556–r560 | markery zdarzeń, proporcje paneli, skale MACD i dopracowanie renderera |
| r561–r594 | szybka segmentacja, próg B=0,25, korekty markerów, 5 TF, finalny CSS |

Pierwszy pełny przebieg walidacyjny wygenerował `19/19` wykresów 1D i `19/19` wykresów 1H. Późniejsza ciężka generacja UI została przerwana po trzech spółkach, ponieważ każda trwała 9–13 minut, a nie z powodu zawieszenia algorytmu. Następnie powstał szybki generator i jego finalny zestaw sześciu spółek.

## 4. Odzyskane zestawy spółek

### 4.1. Walidacja 19 spółek — `CONFIRMED`

`RBLX`, `INTU`, `NVDA`, `ADTN`, `PLTR`, `ORCL`, `NBIS`, `FIG`, `LITE`, `AAOI`, `ZS`, `DDOG`, `COHR`, `AAPL`, `SMCI`, `DAL`, `MS`, `BAC`, `NVO`.

### 4.2. Finalny szybki dashboard — `CONFIRMED`

`RBLX`, `AAOI`, `INTU`, `NVDA`, `PLTR`, `ADTN`.

### 4.3. Wcześniejsza „dziesiątka” referencyjna

Dokładny komplet dziesięciu nie jest już potrzebny do udowodnienia finalnego szybkiego zestawu, ale jego pierwotny skład pozostaje `PARTIAL/TO RECOVER`. Nie wolno mieszać tej grupy z potwierdzonym zestawem 19 ani finalnym zestawem 6.

## 5. Odzyskany mechanizm inwestycyjny

Odzyskano konkretną specyfikację listy `Cykle 1D`. Jej celem jest pokazanie spółki od pierwszego skracania ujemnego histogramu MACD, przez minimum i wzrostowe przecięcie MACD/Signal, maksymalnie do pięciu zamkniętych sesji po przecięciu, o ile dodatni histogram nadal rośnie.

Pełny kontrakt znajduje się w `SKANER-CYKLE-1D/RECOVERED-SPEC.md`. Najważniejsze rozstrzygnięcia:

- jeden status `Cykle 1D`, bez faz i bez etykiety BUY;
- porównanie głębokości bieżącego cyklu ze średnią i medianą zakończonych cykli historycznych;
- pamięć o `RSI <= 32` i `Stoch %K <= 22` w całym aktywnym cyklu;
- anulowanie wczesnego sygnału, jeżeli histogram znów się pogłębia przed przecięciem;
- sortowanie po względnej, znormalizowanej głębokości;
- wolumen jako kontekst/confidence, nie twardy filtr początkowy;
- `ADMA` jest przykładem szumu do odrzucenia, `RBLX` przykładem wzorca docelowego.

## 6. Odzyskana architektura zasobów

Finalny dokument V4.4 został wcześniej zaakceptowany przez użytkownika jako wersja ostateczna, gotowa do etapu E0. Ustalenia potwierdzone:

- pięć docelowych baz według właściciela zapisu: `market.db`, `core.db`, `companies.db`, `news.db`, `portfolio.db`;
- jeden executor zapisujący do każdego pliku DB, przy równoległym pobieraniu/obliczaniu przez workerów;
- publikacja wersjonowana/zdarzeniowa i zachowanie last complete version;
- moduł companies budowany od nowa;
- `scanner_worker` przepisywany dopiero na końcu, po wydzieleniu odpowiedzialności;
- zachowanie kalibracji TradingView, progów, kategorii i cooldownów przez golden-master/shadow mode;
- E0 jest wyłącznie diagnostyczne: writer audit oraz `/health/resources`, bez zmiany zachowania.

Snapshot źródłowy: `SOURCE-SNAPSHOT/ARCHITEKTURA-ZASOBOW-V4.4-FINAL.txt`.

## 7. Braki jawne

| Obszar | Status | Brak |
|---|---|---|
| Podłączenie V3 do głównego UI/API | `NOT IMPLEMENTED` | wymagany osobny kontrakt integracji |
| Alarmy | `TO RECOVER` | pełne warunki, kanały, deduplikacja, cooldown i trwałość |
| Confidence/skuteczność starego UI | `TO RECOVER` | formuła niepotwierdzona; nie używać jako kryterium inwestycyjnego |
| Pełny listing poza `Cykle 1D` | `PARTIAL` | część zakładek i UI widoczna, brak kompletnego kontraktu pól |
| Topologia uruchomienia produkcyjnego | `PARTIAL` | pliki start/stop istnieją, ale procesy są obecnie wyłączone |
| Zgodność finalnego V3 1:1 z TradingView | `PARTIAL` | kalibracja i referencje istnieją, brak formalnej końcowej akceptacji 1:1 dla całego universe |

## 8. Granice tej operacji

Nie uruchomiono serwera, workerów ani zadań cyklicznych. Nie wykonano ruchu sieciowego do providerów. Nie zmodyfikowano projektu `C:\Skaner wykresów` ani baz `C:\skaner-dane`. Odbudowa dashboardu korzystała wyłącznie z istniejących payloadów w archiwum.

## 9. Rekomendowany następny pakiet

`CHARTS-RESTORE-001`:

1. SPEC kontrolowanego wznowienia obecnej aplikacji przy managerze nadal OFF;
2. audit poleceń i skutków startu;
3. Conflict Report;
4. decyzja użytkownika;
5. Implementation Contract;
6. start i test jednego symbolu;
7. kontrola logów/baz;
8. ACCEPTANCE albo ROLLBACK;
9. FREEZE i archiwum.

Integracja V3 ma być kolejną, osobną paczką. Nie należy łączyć jej z aktywacją Massive Traffic Managera.
