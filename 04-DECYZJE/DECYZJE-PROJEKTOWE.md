# DECYZJE PROJEKTOWE — append-only log
Format: D-xxx / DATE / STATUS / DECISION / RATIONALE / SUPERSEDES /
AFFECTED VERSION. Starych wpisow nie usuwamy.

## D-001
DATE: 2026-08-21
STATUS: ACCEPTED
DECISION: r599 wprowadza ONE CROSS-PROCESS MASSIVE TOKEN BUCKET
(refill 30 tok/s, capacity 90) w provider_state.db
(C:\skaner-dane\provider_state.db). NO RESERVATION TABLE. NO RESERVED
CAPACITY (dla zadnego priorytetu). provider_state.db jest CROSS-PROCESS
COORDINATION DATABASE z formalnym wyjatkiem multi-writer: kazdy proces
Massive pisze w krotkich transakcjach BEGIN IMMEDIATE. Wyjatek dotyczy
WYLACZNIE provider_state.db i NIE dotyczy zadnej bazy biznesowej
(market/core/companies/news/portfolio — nadal jeden wlasciciel zapisu).
RATIONALE: procesy nie widza sie nawzajem; centralny wlasciciel = zakazany
central IPC owner (single point of failure); pomiar r598
(20260819T200429Z-5c74e9) potwierdzil topologie i poziomy ruchu.
SUPERSEDES: ARCHITEKTURA-ZASOBOW-V4.md §C2 w czesci "token bucket na proces,
z rezerwacja: 60% W3..." (nigdy nie zaimplementowane).
AFFECTED VERSION: r599.

## D-003
DATE: 2026-08-21
STATUS: ACCEPTED
DECISION: Projekt otrzymuje kanoniczny, plikowy system źródła prawdy przy
kodzie. Obowiązkowe wejście każdej sesji to MASTER-PROJEKT.md,
STAN-AKTUALNY.md, ZASADY-PROJEKTU.md, niniejszy append-only log decyzji,
właściwy FINAL-AS-BUILT i aktywna paczka. Każda zmiana przechodzi pełny
workflow SPEC -> AUDIT -> CONFLICT REPORT -> USER DECISIONS ->
IMPLEMENTATION CONTRACT -> SMALL PACKAGE -> TEST -> ACCEPTANCE ->
AS-BUILT -> HASHES -> FREEZE -> ARCHIWUM. Git przechowuje historię kodu i
dokumentacji, ale remote/push wymaga osobnej decyzji. Frozen ARCHIWUM jest
immutable, a sekrety i bazy są wyłączone z Git.
RATIONALE: dotychczasowa wiedza była rozproszona między rozmowami, backendem,
raportami, backupami i paczkami, co zatrzymało proces inwestycyjny po utracie
ciągłości wykresów. Użytkownik zlecił przygotowanie pełnego flow informacji,
aktualizacji, dostępów i wersjonowania.
SUPERSEDES: —
AFFECTED VERSION: dokumentacja DOCS-2026-08-21-01; bez zmiany VERSION produktu.

## D-004
DATE: 2026-08-21
STATUS: ACCEPTED / RECOVERED
DECISION: Pakiet r599-MASSIVE-TRAFFIC-ACTIVATION-001 został zaakceptowany po
kontrolowanym live teście. Końcowy stan r599: manager ON,
massive_traffic_measurement_enabled=0, provider_state.db zdrowa, jeden proces
Uvicorn podczas testu, OVERALL PASS po starcie, około 13 i około 20 minutach,
count_429=0. Serwer został później zatrzymany, ale flaga pozostaje ON.
RATIONALE: odzyskany MASTER użytkownika zawiera finalne ACTIVATION ACCEPTED;
zapis jest zgodny z config.py, backupem, hashami BEFORE/AFTER i read-only
health provider_state.db.
SUPERSEDES: stan tymczasowy „r599 accepted manager OFF / activation pending”.
AFFECTED VERSION: 2026-08-21-r599; bez zmiany VERSION.

## D-002
DATE: 2026-08-21
STATUS: ACCEPTED
DECISION: parametry i semantyka r599 = BALANCED (r599-CONFIG-01=B):
refill 30 tok/s, capacity 90, TTL P0/P1/P2/P3 = 3/10/45/180 s; oraz
zamkniecia: CLOCK=A (wall epoch + klamra), SQLITE-TX=A (BEGIN IMMEDIATE,
WAL, NORMAL; busy 30000 dla baz biznesowych), CONNECTION=A (thread-local),
DB-CREATE=A (lazy), TOKEN-PRECISION=A (REAL), INITIAL-BUCKET=A (full 90),
WAIT=A (hint, 0.02-0.25 s, jitter +/-20%), TTL-EXPIRY=A (DENIED => None;
granica: now >= expires_at = EXPIRED), CANCEL=A (finally-delete),
STARVATION=A (bez agingu), HINTS=A (odrebne), 429=A (shared cooldown
13 s = POLYGON_PAUSE zastepuje lokalny sleep TYLKO gdy zapis cooldownu sie
powiodl; przy awarii zapisu fallback = lokalny sleep; Retry-After ignorowany;
GROUPED_PAUSE bez zmian), STATE-FAILURE=A (fail-open + licznik + log;
lock-timeout = nieudana iteracja w ramach TTL), METRICS=A, FLAG=A
(massive_traffic_manager_enabled), ROLLOUT=A (default OFF),
r598-TELEMETRY=A (zostaje), RULES=B (pliki utworzone w r599),
TM-BUSY=A (MASSIVE_TM_BUSY_TIMEOUT_S = 0.25 wylacznie dla provider_state.db;
lock po 250 ms = nieudana iteracja w ramach TTL; caly TTL bez zadnej udanej
tx => GRANT_FAIL_OPEN; business DB busy bez zmian).
RATIONALE: RAPORT-r599-SPEC-AUDIT.md BA.63/BA.68 + korekta C1-C9 +
odpowiedzi uzytkownika.
SUPERSEDES: —
AFFECTED VERSION: r599.

## D-005
DATE: 2026-08-21
STATUS: ACCEPTED
DECISION: Archiwum `Skaner-sygnalow-kupna-ARCHIWUM.zip` zostaje przyjęte jako
zaakceptowane źródło historyczne i dowód pochodzenia, a jego README, MASTER i
STAN zostają scalone z nowszą dokumentacją kanoniczną. Import nie może
nadpisywać późniejszych frozen AS-BUILT, stanu kodu ani odzyskanych artefaktów.
Oryginalny ZIP i komplet rozpakowanych plików mają zostać zachowane immutable z
hashami. Braki pozostają UNVERIFIED / TO RECOVER; pakiet nie jest traktowany
jako transcript rozmowy 1:1.
RATIONALE: użytkownik polecił ustawić te dokumenty jako źródło prawdy, najpierw
scalić dokumentację, a potem rozpocząć PROJECT RECOVERY & ARCHIVE. Conflict
report wykazał, że importowany MASTER jest wcześniejszym źródłem obecnego,
bogatszego MASTER-a i ma identyczny hash jak już zachowany MASTER użytkownika.
SUPERSEDES: równoległe traktowanie wielu plików MASTER jako równorzędnych.
AFFECTED VERSION: DOCS-2026-08-21-02; bez zmiany VERSION produktu r599.

## D-006
DATE: 2026-08-21
STATUS: ACCEPTED
DECISION: Stary projekt `C:\Skaner wykresów` i dane `C:\skaner-dane`
zostają zachowane jako `Stock Scanner OLD`, ale jego runtime, workery,
harmonogramy i dostęp do Massive mają pozostać wyłączone. Projekt i dane
zostają zamrożone w zewnętrznym archiwum 1:1. Nowy produkt powstanie w
oddzielnym katalogu `C:\SKOOP Skaner wykresów` i nie może automatycznie
dziedziczyć starych mechanizmów. Kolejność programu SKOOP: niezależny
fundament -> bezpieczny dostęp Massive -> pobranie uniwersum/zasobów -> model
i kwalifikacja spółek -> listing i zarządzanie -> wykresy V3 -> nowe
mechanizmy skanera -> alerty. Warstwa OLD w przyszłym interfejsie ma być
wyłącznie read-only demo na zamrożonych danych, bez sieci i aktualizacji.
RATIONALE: stary skaner zużywał znaczne zasoby, nadal wykonywał połączenia i
opiera część funkcji na nieaktualnych założeniach. Użytkownik chce zachować
wartościowe testy, wykresy, pomysły i rozwiązania, ale nie mieszać ich z
nowym modelem produktu.
SUPERSEDES: plan `CHARTS-RESTORE-20260821-001` polegający na ponownym
uruchomieniu starego runtime. Nie unieważnia historycznej akceptacji r599.
AFFECTED VERSION: DOCS-2026-08-21-03; produkt r599 staje się LEGACY/FROZEN;
nowy produkt jeszcze nie ma wersji.

## D-007
DATE: 2026-08-22
STATUS: ACCEPTED
DECISION: Istniejąca zamrożona próbka OLD jest wystarczająca dla tego
komputera. Nie pobieramy dalszych danych i nie uzupełniamy braków przez Massive.
Pełny żywy skaner z pełniejszymi zasobami pozostaje na drugim komputerze.
Na tym komputerze powstaje lokalna powłoka pod `localhost`: ekran SKOOP jako
placeholder oraz klikalny `Stock Scanner OLD` na frozen SQLite w trybie
immutable/read-only. Dotychczasowe launchery starego skanera mają uruchamiać
wyłącznie nową powłokę, nie stary `run.py` ani workery.
RATIONALE: użytkownik uznał obecną próbkę za wystarczającą i chce uniknąć
zbędnego ruchu, czasu i konfliktu ze starymi mechanizmami. Pełne zasoby można
sprawdzać na stale działającym drugim komputerze.
SUPERSEDES: proponowane masowe uzupełnianie braków D-007A; nie zmienia
historycznych danych ani wcześniejszego freeze.
AFFECTED VERSION: offline shell `2026-08-21-offline-old-001`;
dokumentacja `DOCS-2026-08-22-01`.

## D-008
DATE: 2026-08-22
STATUS: ACCEPTED
DECISION: `Stock Scanner OLD` oznacza zachowanie oryginalnego interfejsu r599
1:1: wyglądu, zakładek, paneli, projektów wykresów i lokalnych zasobów.
Uproszczony widok OLD nie spełniał tego kontraktu i zostaje zastąpiony.
Nowy SKOOP pozostaje domyślnym widokiem pod `localhost:8000`; kliknięcie OLD
otwiera oryginalny frontend r599 na porcie 8001. Dozwolone różnice OLD to
wyłącznie oznaczenie FROZEN/OLD, przejście do SKOOP oraz blokady bezpieczeństwa:
zero Massive/Yahoo, zero workerów, zero zapisu i mutacje HTTP 405.
RATIONALE: użytkownik wielokrotnie potwierdził, że OLD ma być pełnym,
zamrożonym źródłem doświadczeń i rozwiązań, a nie nową makietą inspirowaną OLD.
SUPERSEDES: implementację uproszczonego widoku OLD z D-007; nie unieważnia
decyzji o braku dalszych pobrań ani oddzieleniu nowego SKOOP.
AFFECTED VERSION: `OLD-r599-1TO1-FROZEN-001`;
dokumentacja `DOCS-2026-08-22-02`.


