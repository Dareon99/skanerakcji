# MASTER-PROJEKT — SKANER WYKRESÓW

**Status dokumentu:** pierwsza wersja odzyskana z bieżącej rozmowy  
**Data utworzenia:** 2026-08-21  
**Projekt:** Skaner wykresów  
**Lokalizacja projektu:** `C:\Skaner wykresów`  
**Backend:** `C:\Skaner wykresów\backend`  
**Dane:** `C:\skaner-dane`  
**Python projektu:** `C:\Skaner wykresów\backend\.venv\Scripts\python.exe`

---

# 0. ROLA TEGO DOKUMENTU

Ten dokument jest od teraz nadrzędnym źródłem prawdy o projekcie.

Historia rozmów z AI NIE jest źródłem prawdy i nie może być jedynym miejscem przechowywania ustaleń.

Każda nowa sesja z ChatGPT/Claude powinna zaczynać się od przeczytania:

1. `MASTER-PROJEKT.md`
2. `STAN-AKTUALNY.md`
3. `ZASADY-PROJEKTU.md`
4. `DECYZJE-PROJEKTOWE.md`
5. `FINAL-AS-BUILT-SPEC.md` poprzedniego sprintu
6. `SPEC.md` aktualnego sprintu

Jeżeli informacji nie ma w dokumentacji albo plikach projektu, AI ma oznaczyć ją jako:

- `UNVERIFIED`
- `TO RECOVER`
- `DECISION REQUIRED`

i NIE może odtwarzać jej z pamięci lub zgadywać.

---

# 1. CEL PRODUKTU

Docelowy system ma realizować przepływ:

`universe spółek` → `kwalifikacja i profil spółki` → `pobieranie danych` → `mechanizm skanera` → `ranking/listing spółek` → `wybór spółki` → `wykresy` → `analiza sygnału` → `alarm / decyzja użytkownika`

Główne obszary produktu:

1. stabilny universe spółek,
2. klasyfikacja spółek,
3. pipeline danych,
4. mechanizm skanera,
5. ranking/listing wyników,
6. szczegóły spółki,
7. wykresy techniczne,
8. scoring / etap / skuteczność,
9. alarmy,
10. stabilna warstwa dostępu do danych Massive/Polygon.

---

# 2. AKTUALNY STAN PROJEKTU

## 2.1. Aktualna wersja

`VERSION = 2026-08-21-r599`

## 2.2. Status r599

**FINAL STATUS: ACCEPTED + ACTIVATED**

r599 został:

- zainstalowany,
- poprawiony w zakresie narzędzi testowych/audytowych,
- zaakceptowany przy managerze OFF,
- następnie aktywowany kontrolowanie,
- sprawdzony na realnym ruchu,
- pozostawiony z managerem ON.

## 2.3. Końcowy stan managera

`massive_traffic_manager_enabled = 1`

**Manager: ON**

## 2.4. Telemetria r598

`massive_traffic_measurement_enabled = 0`

Pełna nowa telemetria 24h dla r599 NIE została uruchomiona.

## 2.5. provider_state.db

Po aktywacji managera i pierwszym realnym acquire:

`C:\skaner-dane\provider_state.db`

została utworzona lazy.

Końcowy health:

- `integrity_check = ok`
- `user_version = 1`
- `journal_mode = wal`
- tabele:
  - `priority_tickets`
  - `sqlite_sequence`
  - `traffic_state`
- `traffic_state rows = 1`
- `tokens = 89.000` w odczytach statusowych
- `cooldown_until = 0.0`
- `count_429 = 0`
- `priority_tickets = 0` w chwilach statusu

## 2.6. Serwer / proces

Po aktywacji:

- serwer działał na porcie 8000,
- dokładnie 1 PID,
- obserwowany PID: `12024`,
- Uvicorn działał poprawnie,
- skaner rozpoczął realny skan `5088` spółek.

## 2.7. Statusy aktywacji

Pierwszy STATUS po uruchomieniu:

- manager ON,
- 1 PID,
- provider_state.db istnieje,
- LAZY-CREATE = STAN D,
- SQLite HEALTH = PASS,
- BUSINESS DB safety = PASS,
- OVERALL = PASS,
- exit code 0.

Po ~13 minutach:

- nadal OVERALL PASS,
- ten sam PID,
- DB zdrowa,
- `count_429 = 0`,
- exit code 0.

Po ~20 minutach:

- nadal OVERALL PASS,
- manager ON,
- jeden PID,
- stan D,
- SQLite PASS,
- business DB PASS,
- `count_429 = 0`,
- exit code 0.

**Wniosek:** aktywacja r599 zakończona sukcesem.

---

# 3. ARCHITEKTURA — STAN POTWIERDZONY

## 3.1. Bazy danych

Architektura V4.4:

- `market.db` — W3
- `core.db` — core pipeline / universe
- `companies.db` — W0 / W8 / W11
- `news.db` — W10
- `portfolio.db` — W12
- `provider_state.db` — formalny wyjątek: multi-writer coordination DB dla traffic managera

Zasady:

- zero cross-DB write transaction dla business DB,
- jeden write executor per business SQLite DB,
- `provider_state.db` jest odrębną bazą koordynacyjną,
- nie należy mieszać jej z bazami biznesowymi.

## 3.2. Priorytety Massive

Finalne priorytety:

- `P0 INTERACTIVE_MARKET`
- `P1 SCANNER_CRITICAL`
- `P2 MAINTENANCE`
- `P3 COMPANY_BACKGROUND`

P3:

- bez zarezerwowanej capacity,
- ustępuje wyższym priorytetom.

`priority_hints`:

- osobny append-only,
- monotonic `hint_id`.

## 3.3. Last-good

Na błąd providera:

- konsument ma używać last-good,
- `NULL != 0`,
- brak danych nie może być sztucznie zamieniany na zero.

---

# 4. r599 — MASSIVE TRAFFIC MANAGER

## 4.1. Cel

r599 ma zabezpieczać współdzielony dostęp do Massive/Polygon pomiędzy procesami/wątkami i priorytetami.

Ma zapewnić:

- ograniczenie tempa requestów,
- wspólny token bucket,
- wspólny cooldown 429,
- priorytety,
- kolejkę ticketów,
- fail-open przy awarii coordination DB,
- brak niekontrolowanego retry storm,
- ochronę interaktywnych wykresów / rynku jako P0.

## 4.2. Konfiguracja finalna

Wybrana konfiguracja B — BALANCED:

- refill rate: `30 tokens/s`
- bucket capacity: `90`
- TTL:
  - P0 = `3 s`
  - P1 = `10 s`
  - P2 = `45 s`
  - P3 = `180 s`
- busy timeout dla provider_state.db: `0.25 s`
- cooldown 429: `13 s`

## 4.3. Mechanizm

- shared cross-process SQLite token bucket,
- DB: `C:\skaner-dane\provider_state.db`,
- brak centralnego IPC owner,
- brak reservation table,
- jeden wspólny bucket,
- token zużywany przy grant,
- brak refund,
- każda realna próba HTTP / retry zużywa token,
- shared cooldown 429,
- gate w:
  - `polygon_source._get`
  - `diag_raw`
- 18 aktywnych operation IDs,
- 1 zarezerwowany future ID:
  - `companies.classification`
- ok. 73 caller contexts,
- 5 operacji context-dependent.

## 4.4. SQLite

Traffic manager:

- `BEGIN IMMEDIATE`,
- WAL,
- synchronous NORMAL,
- thread-local persistent connections,
- lazy DB creation,
- `tokens REAL`,
- initial bucket full = 90,
- `user_version = 1`.

## 4.5. Wait

Finalna formuła:

`clamp(wait_hint*(1+0.4*(_rand()-0.5)), 0.02, 0.25)`

Jitter jest liczony przed finalnym clamp.

## 4.6. TTL

Granica:

- `now >= expires_at` = expired
- valid tylko gdy `expires_at > now`
- cleanup `<= now`

TTL expiry:

- `DENIED_TTL`
- istniejące zachowanie None / last-good

Brak cancel API.

## 4.7. Tickets

Finalny state machine:

- fast path tylko gdy:
  - cooldown inactive,
  - queue empty,
  - tokens >= 1,
- w przeciwnym razie:
  - INSERT dokładnie jednego ticketu w tym samym `BEGIN IMMEDIATE`,
- cooldown także tworzy ticket,
- kolejne iteracje reuse tego samego ticketu,
- strict priority + FIFO,
- grant:
  - atomic consume token,
  - delete/update ticket,
- jeden logical wait = jeden ticket.

## 4.8. Fail-open

Przy awarii provider_state.db:

- fail-open,
- manager nie może blokować aplikacji bez końca,
- `report_429` zwraca bool,
- jeśli persistence cooldown działa:
  - brak local sleep,
- jeśli persistence nie działa:
  - local sleep `POLYGON_PAUSE = 13 s` dokładnie raz,
  - brak retry storm.

## 4.9. Soft import

Legal absence kontrakt:

tylko:

`ModuleNotFoundError`

gdzie:

`exc.name == "core.massive_traffic"`

Wtedy:

- `_tm = None`
- `_tm_import_error = None`

Nested import failure lub RuntimeError:

- `_tm_import_error` ustawiony,
- nie traktować jako legal absence.

Finalnie naprawiono składnię importu w `polygon_source.py`:

OLD:

`from core import massive_traffic as _tm_mod`

NEW:

`import core.massive_traffic as _tm_mod`

Powód:

`from core import X` przy realnym braku submodułu finalnie daje `ImportError`, przez co kontrakt ModuleNotFoundError był martwy.

Zmiana soft-importu:

- tylko jedna linia,
- bez zmiany kontraktu,
- VERSION bez zmiany.

---

# 5. r598 — TELEMETRIA / KALIBRACJA RUCHU

## 5.1. Wersja przed r599

`2026-08-18-r598`

## 5.2. Finalny pomiar

Run:

`20260819T200429Z-5c74e9`

Formalnie 24h.

Start:

2026-08-19 20:04:29 UTC

W trakcie był znany environmental power outage.

Komputer po awarii wrócił ok. 10:17 lokalnie 2026-08-20.

Analyzer wykluczył downtime-affected events z clean latency/concurrency.

## 5.3. Finalna analiza r598

- lines/events: `250291`
- invalid JSON/schema: `0`
- clean: `250280`
- sample quality:
  - PASS WITH KNOWN ENVIRONMENTAL DOWNTIME
- sample:
  - sufficient with limitations
- mean clean:
  - ok. `4.08 req/s`
- hottest hour:
  - ok. `8.2/s`
- burst max 1s:
  - `43`
- p95 1s:
  - `30`
- p99 1s:
  - `34`
- 60s max:
  - `1906`
  - ok. `31.8/s`
- clean max concurrency:
  - `17`
- p99 time-weighted concurrency:
  - `11`
- latency:
  - p50 ~ `366ms`
  - p95 ~ `607.5ms`
  - p99 ~ `1174ms`
- 429:
  - `0`
- P2 dominował
- history.aggregates:
  - ok. `86%`

Ograniczenie:

`SINGLE OBSERVED PROCESS pid 22476`

czyli pełny ruch wszystkich procesów mógł być wyższy.

---

# 6. HISTORIA RELEASE / TESTÓW

## r595 / C0

- accepted
- `119 PASS / 0 FAIL`

## r596 / C1

- accepted
- `90 PASS / 0 FAIL`

## r597 / C2

- accepted
- `189 PASS / 0 FAIL`

## CORE

- `47 OK / 0 BŁĄD`

## r598

- `177 PASS / 0 FAIL`
- C0/C1/C2/CORE jak wyżej
- acceptance gates:
  - `112 / 0 FAIL`
- final VERSION:
  - `2026-08-18-r598`

## r599 przed aktywacją

Pełny audyt:

- `PASS 181 / FAIL 0`
- `test_massive_traffic: kod 0 i FAIL 0`
- `test_massive_telemetry: kod 0 i FAIL 0`
- zero mutacji business DB
- provider_state.db absent przy OFF
- BAT ASCII/CRLF/NO BOM

Status:

**ACCEPTED WITH MANAGER OFF**

## r599 po aktywacji

Status:

**ACCEPTED + ACTIVATED**

---

# 7. r599 — HISTORIA FIXÓW I LEKCJE

## FIX-006 — UTF-8 audit output

Problem:

`UnicodeEncodeError` na Windows cp1250 przy `print(tail)` i U+FFFD.

Root cause:

- subprocess child pisał cp1250,
- audit dekodował jako UTF-8 z replace,
- powstawał U+FFFD,
- print przez cp1250 crashował.

Fix:

- `PYTHONUTF8=1`
- `PYTHONIOENCODING=utf-8`
- jawna polityka UTF-8 stdout/stderr/subprocess.

## FIX-007 — test UTF-8 fixture

Problem:

E1/E2/E3 padały przez błędnie zagnieżdżony newline:

- dziecko dostawało SyntaxError,
- stdout był pusty,
- część testów przechodziła vacuously / po tracebacku.

Fix:

- poprawione `\\n`,
- sprawdzanie returncode,
- zakaz vacuous PASS,
- meta-fixture compile generated child snippet.

Final:

E1-E10 PASS.

## FIX-008 — test_massive_traffic + telemetry legacy expectations

Problem 1:

`importlib` scope:

- global `import importlib`
- wewnątrz main:
  - `import importlib.abc`
  - `import importlib.util`
- przez binding w funkcji `importlib` stawał się local,
- wcześniejsze `importlib.reload(mt)`:
  - `UnboundLocalError`.

Problem 2:

telemetry test r598 miał hardcoded VERSION `2026-08-18-r598`.

Problem 3:

test import side-effect sprawdzał samo istnienie katalogu measurement zamiast delty.

Fix:

- importlib imports na poziom modułu,
- VERSION expectation aktualne r599,
- directory side-effect delta-based.

## FIX-009 — test_massive_traffic fixtures

Zdiagnozowane błędy testu:

1. off-by-one:
   - po reset do 90 wykonywano `range(89)`
2. 91st sleep:
   - bucket zostawał z 1 tokenem
3. T3:
   - fake sleep przesuwał fake clock,
   - refill pozwalał grant po ~1 iteracji
4. I1-I3:
   - `core.massive_traffic` nadal był atrybutem pakietu core,
   - hook był omijany.

Fix:

- 90 realnych grantów,
- 91st na tokens=0,
- deterministyczny T3,
- delattr/core attribute cleanup,
- hook-hit assertions,
- cleanup in finally.

Pozostał I1.

## FIX-010 — soft import production fix

I1 pokazał realny defect kontraktu/implementacji soft-import.

Diagnoza:

dla:

`from core import massive_traffic`

realny brak submodułu kończył się dla callera `ImportError`, nie `ModuleNotFoundError`.

Decyzja użytkownika:

**wariant A**

Zmiana:

`import core.massive_traffic as _tm_mod`

Kontrakt legal absence pozostaje bez zmian.

Finalnie:

- `test_massive_traffic` PASS / FAIL 0
- `test_massive_telemetry` PASS / FAIL 0
- pełny audit PASS 181 / FAIL 0.

---

# 8. AKTYWACJA r599

## 8.1. Package

`r599-MASSIVE-TRAFFIC-ACTIVATION-001`

## 8.2. Zmiana

Jedyny target:

`config.py`

Jedyna zmiana semantyczna:

OLD:

`massive_traffic_manager_enabled = 0`

NEW:

`massive_traffic_manager_enabled = 1`

Bez zmiany:

- VERSION
- telemetry flag
- refill
- capacity
- TTL
- busy timeout
- POLYGON_PAUSE
- GROUPED_PAUSE
- DB paths
- priority
- operation IDs.

## 8.3. Preflight

P1-P20:

**PASS ALL**

Potwierdzone:

- ścieżki,
- VERSION,
- flagi,
- import,
- `_tm`,
- zero `_tm_import_error`,
- oba testy FAIL 0,
- compile/AST/warnings config,
- zero drift w 5 plikach r599,
- manager OFF przed write,
- port 8000 wolny,
- provider_state absence przy OFF dopuszczalna.

## 8.4. Backup

Backup:

`C:\Skaner wykresów\backend\_backup-r599-MASSIVE-TRAFFIC-ACTIVATION-001\config.py.przed-aktywacja`

SHA256 BEFORE == BACKUP:

`5a1acf63f355e84b6302035889a4aa914f714cbf7a3b0328c5539fbf28a675c9`

SHA256 AFTER:

`08e51f31fe33a924a5b8b01929e5b1a96e6124684559cfa6770d97d2b7e2ceb8`

Activation exit code:

`0`

## 8.5. Restart

Serwer był zatrzymany.

Po `URUCHOM.bat`:

- Uvicorn PID `12024`
- port 8000
- application startup complete
- pipeline loaded
- TECHNICAL_SCAN uruchomiony
- skan `5088` spółek.

## 8.6. Final activation acceptance

Po 20 minutach:

- manager ON
- telemetry 0
- 1 PID
- provider_state STAN D
- SQLite health PASS
- business DB safety PASS
- `count_429=0`
- `OVERALL: PASS`
- exit code 0

**ACTIVATION ACCEPTED**

---

# 9. ZASADY PROJEKTOWE — WORKFLOW

Dla większych zmian obowiązuje:

`SPEC` → `AUDIT` → `CONFLICT REPORT` → `USER DECISIONS` → `IMPLEMENTATION CONTRACT` → `SMALL PACKAGE` → `TEST` → `ACCEPTANCE` → `NEXT PACKAGE`

Nie wolno automatycznie przechodzić do następnego etapu bez zgody użytkownika.

Claude/AI nie może interpretować niejednoznaczności.

Jeżeli ambiguity:

`DECISION REQUIRED`

z:

- problem,
- opcja A,
- opcja B,
- rekomendacja,
- konsekwencje,
- STOP.

---

# 10. STOP RULE

Każdy nowy FAIL:

1. STOP.
2. Zero automatycznej poprawki.
3. READ-ONLY DIAGNOSIS.
4. Klasyfikacja:

- TEST DEFECT
- PRODUCTION DEFECT
- ENVIRONMENTAL DEFECT
- AUDIT/WRAPPER DEFECT
- ACTIVATION PROCEDURE DEFECT
- UNPROVEN

5. Nowa paczka dopiero po:
   - dowodzie,
   - diagnozie,
   - decyzji użytkownika.

Jeżeli `UNPROVEN`:

- zero fixa,
- `LOCAL EVIDENCE REQUIRED`,
- jeden minimalny krok diagnostyczny.

---

# 11. PACKAGE ISOLATION

Każda paczka:

- ma unikalny exact `PACKAGE_ID`,
- outer folder,
- inner folder,
- installer,
- README,
- report,
- headers

muszą używać identycznego ID.

Zero zależności od:

- starych FIX folders,
- starych `C:\Temp\...`,
- przypadkowych poprzednich paczek.

Paczka ma być samowystarczalna.

---

# 12. QUALITY GATE — OBOWIĄZKOWY

Po OSTATNIM source write:

`LAST WRITE` → `py_compile` → `AST` → `invalid escape / SyntaxWarning` → `undefined names/imports` → `control flow` → `data/types` → `Windows paths` → `exact names` → `tests` → `package integrity` → `hashes` → `FREEZE`

Każda zmiana po gate/hash:

- unieważnia wcześniejsze wyniki,
- wymaga ponowienia adekwatnych gate.

Żadnych „małych poprawek literówki” po hashach bez re-run.

Nie wolno pisać PASS, jeśli test nie został rzeczywiście uruchomiony.

Jeśli test nie może być uruchomiony w środowisku Claude:

`LOCAL REQUIRED`

---

# 13. BAT / WINDOWS CONTRACT

BAT:

- ASCII
- CRLF only
- NO BOM

Project path:

`C:\Skaner wykresów`

Backend:

`C:\Skaner wykresów\backend`

Python:

`C:\Skaner wykresów\backend\.venv\Scripts\python.exe`

W BAT:

- nie wpisywać literalnego Unicode hard target,
- używać `%~dp0`,
- pełne quoting,
- zero fallbacku:
  - `py`
  - `py -3`
  - `python`
  - `python3`

jeżeli nie jest to project `PYEXE`.

---

# 14. ARCHIWIZACJA — NOWA ZASADA BEZWZGLĘDNA

**SPRINT NIE JEST ZAKOŃCZONY, DOPÓKI NIE MA ARCHIWUM I FINAL AS-BUILT SPEC.**

Każdy sprint ma zostawić co najmniej:

- `01-SPEC.md`
- `02-AUDIT.md`
- `03-CONFLICT-REPORT.md`
- `04-DECISIONS.md`
- `05-IMPLEMENTATION-CONTRACT.md`
- `06-CHANGES.md`
- `07-TESTS-AND-RESULTS.md`
- `08-FINAL-AS-BUILT-SPEC.md`
- `09-ROLLBACK.md`
- `10-NEXT-STEPS.md`
- `HASHES.txt`

Dla UI / wykresów dodatkowo:

- `REFERENCES/`
- `CALIBRATION.md`
- zaakceptowane screenshoty referencyjne
- finalny generator/config
- lista testowych spółek
- porównania do referencji

---

# 15. PROPONOWANA STRUKTURA ARCHIWUM

```text
Skaner-wykresow/
│
├── MASTER-PROJEKT.md
├── ROADMAPA.md
├── STAN-AKTUALNY.md
├── ZASADY-PROJEKTU.md
├── DECYZJE-PROJEKTOWE.md
│
├── ARCHIWUM/
│   ├── r595/
│   ├── r596/
│   ├── r597/
│   ├── r598/
│   ├── r599/
│   │   ├── SPEC.md
│   │   ├── AUDIT.md
│   │   ├── DECISIONS.md
│   │   ├── IMPLEMENTATION-CONTRACT.md
│   │   ├── FIX-HISTORY.md
│   │   ├── ACTIVATION.md
│   │   ├── TESTS-AND-RESULTS.md
│   │   ├── FINAL-AS-BUILT-SPEC.md
│   │   ├── ROLLBACK.md
│   │   └── HASHES.txt
│   │
│   ├── SKANER-LISTING/
│   │   ├── RECOVERY-SOURCES.md
│   │   ├── SPEC.md
│   │   ├── UI-SPEC.md
│   │   ├── FINAL-AS-BUILT-SPEC.md
│   │   └── REFERENCES/
│   │
│   └── WYKRESY/
│       ├── RECOVERY-SOURCES.md
│       ├── SPEC.md
│       ├── CALIBRATION.md
│       ├── FINAL-AS-BUILT-SPEC.md
│       └── REFERENCES/
│
├── DOCS/
│   ├── ARCHITEKTURA.md
│   ├── BAZY-DANYCH.md
│   ├── API.md
│   └── PROCESS-TOPOLOGY.md
│
└── backend/
```

---

# 16. SKANER / LISTING — ODZYSKANY STAN

## 16.1. POTWIERDZONE

Z wcześniejszej pracy odzyskano kierunek:

- osobny moduł / ekran skanera,
- dark UI,
- wybór spółki,
- ticker + nazwa,
- giełda / kraj / branża,
- status typu `ODBIJA`,
- `ETAP`,
- `Skuteczność`,
- filtry:
  - cykle,
  - trendy,
  - branże,
  - alarmy,
  - IPO,
  - dane,
- wykresy na ekranie analizy spółki.

## 16.2. Fundament danych spółek

Potwierdzone:

- `companies.db`
- `BASE_OK`
- IPO osobno
- `BASE_OK = base_ok=1 AND ipo=0`
- klasyfikacja SIC
- katalog:
  - 20 sektorów
  - 129 branż
- `UNRESOLVED` jako jawny status
- brak automatycznego fallbacku do `Miscellaneous`

## 16.3. NIEODZYSKANE / TO RECOVER

Nie wolno zgadywać:

- dokładnych kolumn listingu,
- ich kolejności,
- szerokości,
- default sort,
- paginacji,
- kombinacji filtrów,
- badge/status behavior,
- hover,
- responsywności,
- dokładnego flow click → detail.

Te informacje trzeba odzyskać z:

- lokalnych plików,
- screenshotów,
- wcześniejszych specyfikacji,
- starych generatorów/UI.

---

# 17. WYKRESY — ODZYSKANY STAN

## 17.1. POTWIERDZONE

Kierunek wykresów był kalibrowany do możliwie wiernego wyglądu TradingView.

Zachowany zestaw:

- timeframe `1D`
- świece OHLC
- `WMA 9`
- `EMA 20`
- `EMA 50`
- `EMA 100`
- `EMA 200`
- wolumen
- `MACD`
- `RSI 14`
- `Stochastic 14/3/3`
- `Accumulation/Distribution`

Układ:

panel główny:

- candles
- WMA/EMA
- volume
- price axis po prawej
- dark background

panele poniżej:

1. MACD
2. RSI
3. Stochastic
4. Accumulation/Distribution

Były referencje dla wielu testowych spółek i generator był kalibrowany przez około tydzień.

## 17.2. POTENCJALNIE NA DYSKU — DO ODZYSKANIA

Lokalne pliki generatora mogą zawierać:

- finalne kolory,
- linewidth,
- alpha,
- panel ratios,
- `figsize`,
- DPI,
- liczba świec,
- padding,
- x-axis format,
- weekend gaps,
- right margin,
- candle width,
- exact viewport,
- tooltip behavior,
- save format,
- output naming,
- exact indicator calculation.

**Nie wolno kalibrować od zera przed read-only recovery tych plików.**

## 17.3. AS-BUILT cel

Po recovery musi powstać:

`ARCHIWUM/WYKRESY/FINAL-AS-BUILT-SPEC.md`

oraz:

`CALIBRATION.md`

z dokładnymi, finalnymi parametrami.

---

# 18. ROADMAPA OD OBECNEGO STANU

## DONE

- r595
- r596
- r597
- CORE
- r598 telemetry/calibration
- r599 implementation
- r599 audit
- r599 soft-import fix
- r599 activation
- r599 live activation PASS

## CURRENT

**PROJECT RECOVERY / ARCHIVE**

Cel:

- stworzyć trwałą pamięć projektu,
- odzyskać listing,
- odzyskać wykresy,
- odzyskać plan mechanizmu skanera,
- zapisać to jako AS-BUILT / SPEC.

## NEXT

1. Recovery lokalnych plików wykresów — READ-ONLY.
2. Recovery skanera/listingu — READ-ONLY.
3. Uzupełnienie MASTER.
4. Finalizacja `WYKRESY/FINAL-AS-BUILT-SPEC`.
5. Finalizacja `SKANER-LISTING/FINAL-AS-BUILT-SPEC`.
6. Mechanizm skanera.
7. Ranking/listing.
8. Integracja istniejących wykresów.
9. Analiza/scoring/etap/skuteczność.
10. Alarmy.
11. Finalne UX.

Nie rozpoczynać r600/C3A automatycznie bez świadomej decyzji.

---

# 19. WYKRESY A r599

r599 był fundamentem potrzebnym m.in. po to, aby:

- P0 interactive market miał pierwszeństwo,
- ciężkie zadania skanera nie blokowały wykresu,
- shared traffic nie przeciążał providera,
- wykresy mogły działać płynnie przy równoległym ruchu.

Dlatego r599 jest warstwą infrastrukturalną pod skaner/listing/wykresy, a nie samym mechanizmem skanera.

---

# 20. LEKCJE PROJEKTOWE

1. Testy nie są produktem.
2. Nie wolno pozwalać, aby testowanie infrastruktury stało się osobnym projektem bez końca.
3. Każdy nowy FAIL musi być najpierw sklasyfikowany.
4. Czat AI nie jest trwałą pamięcią projektu.
5. Źródłem prawdy ma być dysk/repo.
6. Każdy sprint kończy się AS-BUILT.
7. Wykresy kalibrowane tygodniami muszą mieć:
   - kod,
   - config,
   - screenshoty,
   - parametry,
   - accepted references,
   - listę test cases.
8. UI/listing musi mieć finalną specyfikację, nie tylko screenshot.
9. MASTER ma być aktualizowany po każdym sprincie.
10. Nowa sesja AI nie zaczyna od pamięci rozmowy, tylko od dokumentacji.

---

# 21. STAN DO PRZENIESIENIA DO WORK

Po utworzeniu tego dokumentu w repo/dysku:

**r599 jest zamknięty jako:**

`2026-08-21-r599`  
`ACCEPTED + ACTIVATED`  
`MANAGER ON`  
`TELEMETRY OFF`  
`provider_state HEALTHY`  
`live activation PASS after 20 min`

Następny etap:

**PROJECT RECOVERY & ARCHIVE**

Nie rozpoczynać nowych funkcji zanim:

- lokalne pliki wykresów nie zostaną zinwentaryzowane,
- listing/spec skanera nie zostaną odzyskane,
- MASTER nie zostanie uzupełniony o odzyskane dane.

---

# 22. CHECKLISTA STARTU KAŻDEJ NOWEJ SESJI AI

AI ma przed pracą odpowiedzieć sobie:

- Czy przeczytałem MASTER?
- Czy znam aktualną wersję?
- Czy znam aktualny sprint?
- Czy znam ostatni accepted state?
- Czy znam obowiązujące decyzje?
- Czy znam stop rule?
- Czy znam package isolation?
- Czy mam FINAL AS-BUILT poprzedniego etapu?
- Czy istnieją `UNVERIFIED` / `TO RECOVER`?
- Czy użytkownik zatwierdził bieżący etap?

Jeżeli nie:

STOP i uzupełnij kontekst z dokumentacji.

---

# 23. STATUS DOKUMENTU

Ta wersja MASTER została zrekonstruowana z bieżącej rozmowy.

Oznaczenia:

- informacje o r599/r598 i testach: `CONFIRMED`
- ogólny kierunek skanera/listingu: `PARTIALLY RECOVERED`
- parametry finalnej kalibracji wykresów: `TO RECOVER FROM LOCAL FILES`
- dokładne UI listingu: `TO RECOVER`
- przyszła roadmapa funkcjonalna: `PLANNED`

Po przeniesieniu do Work należy:

1. zapisać ten plik w projekcie,
2. utworzyć `STAN-AKTUALNY.md`,
3. utworzyć `ARCHIWUM/r599/FINAL-AS-BUILT-SPEC.md`,
4. przenieść tam pełne artefakty r599,
5. rozpocząć read-only recovery wykresów i listingu,
6. aktualizować MASTER po każdym zakończonym etapie.
