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
