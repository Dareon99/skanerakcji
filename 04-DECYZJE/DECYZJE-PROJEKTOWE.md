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

## D-009
DATE: 2026-08-24
STATUS: ACCEPTED
SOURCE: `UD-01 — AKCEPTUJĘ`
DECISION: Pierwszy UNIVERSE SKOOP obejmuje pełny katalog aktywnych spółek
dostępnych w zatwierdzonym zakresie Massive. Każdy instrument otrzymuje jawną
klasyfikację typu, giełdy, kraju i waluty. Pierwszy import służy audytowi
kompletności zasobu i nie kwalifikuje automatycznie spółek do BASE. Stare mixed
universe OLD nie jest automatycznie kopiowane do nowego produktu.
RATIONALE: użytkownik chce widzieć cały dostępny zasób i oceniać kompletność oraz
założenia BASE na podstawie danych, bez przenoszenia błędnych mechanizmów OLD.
SUPERSEDES: brak; zamyka `C-03` i `UD-01` aktywnej paczki.
AFFECTED VERSION: dokumentacja `DOCS-2026-08-24-02-DRAFT`; runtime bez zmian.

## D-016
DATE: 2026-08-24
STATUS: ACCEPTED
SOURCE: `UD-09 — AKCEPTUJĘ`
DECISION: Harmonogram SKOOP rozdziela discovery, dane dzienne, IPO, BASE i listing.
UNIVERSE discovery działa raz dziennie około 04:00 ET. Finalne `1D` powstaje po
zamknięciu właściwej giełdy. Kalendarz IPO odświeża się raz po rozpoczęciu regularnej
sesji USA z opóźnieniem ustalonym smoke testem i retry po błędzie. BASE działa
ciągłą kolejką z docelowym cyklem około 5 minut podczas aktywnej sesji. PRE/POST są
oddzielone od REGULAR. Obowiązują T0–T4, płynna publikacja ostatnich poprawnych
danych oraz osobna ścieżka execution. Dokładne limity wynikają dopiero z testu planu
Massive.
RATIONALE: różne zbiory, giełdy i typy danych mają inne rytmy; użytkownik ma stale
dostępny listing bez oczekiwania na pełny przebieg, a koszt providera pozostaje
kontrolowany.
SUPERSEDES: IPO co 6 godzin, jeden kalendarz dla wszystkich giełd i blokowe
zatrzymywanie kolejki; zamyka `C-10` i `UD-09`.
AFFECTED VERSION: dokumentacja `DOCS-2026-08-24-02-DRAFT`; runtime bez zmian.

## D-015
DATE: 2026-08-24
STATUS: ACCEPTED
SOURCE: `UD-06 — AKCEPTUJĘ`
DECISION: Wartości źródłowe pozostają w natywnej walucie instrumentu. USD jest
oddzielną wartością porównawczą z zapisanym kursem, źródłem, czasem i wersją
metody. Cena akcji jest domyślnie prezentowana w walucie notowania; kapitalizacja,
obrót i ADV mogą być porównywane, sortowane i filtrowane w USD. Prawy panel pokazuje
obie wartości. Dane historyczne używają właściwego historycznego FX. Brak kursu
oznacza `PENDING_FX`, nigdy zero.
RATIONALE: globalny UNIVERSE wymaga porównywalności bez utraty oryginalnej wartości
i bez ukrytego przeliczania danych źródłowych.
SUPERSEDES: przechowywanie wyłącznie waluty natywnej albo wyłącznie USD; zamyka
`UD-06`.
AFFECTED VERSION: dokumentacja `DOCS-2026-08-24-02-DRAFT`; runtime bez zmian.

## D-014
DATE: 2026-08-24
STATUS: ACCEPTED
SOURCE: `UD-05 — AKCEPTUJĘ`
DECISION: Każde aktywne IPO otrzymuje po sesji aktualny wykres `1D` i przebieg od
debiutu. IPO będące w BASE korzysta z pełnej regularnej aktualizacji BASE. Dla IPO
poza BASE pełny intraday `30m/1H/2H/4H` uruchamia się priorytetem T0 po kliknięciu,
a wynik pozostaje w cache z jawnym czasem. Sygnał, obserwacja lub portfel uruchamia
odpowiednio priorytety T1–T3. Nieaktualny wykres jest wyraźnie oznaczony.
RATIONALE: każda spółka IPO zachowuje użyteczny wykres bez stałego pobierania
pełnego intraday dla wszystkich spółek poza BASE.
SUPERSEDES: pełną ciągłą aktualizację intraday każdego IPO niezależnie od użycia;
zamyka `UD-05`.
AFFECTED VERSION: dokumentacja `DOCS-2026-08-24-02-DRAFT`; runtime bez zmian.

## D-013
DATE: 2026-08-24
STATUS: ACCEPTED
SOURCE: `UD-04 — AKCEPTUJĘ`
DECISION: Po zamknięciu 180. właściwej sesji kończy się aktywny status IPO, a
spółka jest ponownie oceniana według aktualnych reguł BASE. Spełniająca reguły
pozostaje albo wchodzi do BASE; niespełniająca pozostaje tylko w UNIVERSE.
Istniejący status BASE nie znika z powodu ukończenia okna IPO, a sesja 181 nie
nadaje BASE automatycznie.
RATIONALE: BASE pozostaje listą spółek zakwalifikowanych, a nie archiwum wszystkich
dawnych IPO; jednocześnie IPO i BASE mogą nakładać się podczas pierwszych 180 sesji.
SUPERSEDES: interpretację „po 180 sesjach każda spółka zostaje w BASE”; zamyka
`C-01`, `C-02` i `UD-04`.
AFFECTED VERSION: dokumentacja `DOCS-2026-08-24-02-DRAFT`; runtime bez zmian.

## D-012
DATE: 2026-08-24
STATUS: ACCEPTED
SOURCE: `UD-03 — AKCEPTUJĘ`
DECISION: Brak ceny, kapitalizacji lub ADV w danych wejściowych BASE daje status
`PENDING_DATA` i dokładny kod brakującego pola. Spółka pozostaje w UNIVERSE, nie
jest kwalifikowana ani odrzucana z BASE, trafia do kolejki uzupełnienia i zostaje
oceniona ponownie po opublikowaniu poprawnych danych. Brak nigdy nie jest zerem.
RATIONALE: niepełny rekord nie jest dowodem spełnienia ani niespełnienia kryteriów;
historyczny fail-open r599 powodował ryzyko fałszywych kwalifikacji.
SUPERSEDES: fail-open dla brakującego mcap/ADV/ceny; zamyka `C-04` i `UD-03`.
AFFECTED VERSION: dokumentacja `DOCS-2026-08-24-02-DRAFT`; runtime bez zmian.

## D-011
DATE: 2026-08-24
STATUS: ACCEPTED
SOURCE: `UD-02 — AKCEPTUJĘ`
DECISION: Pierwsza BASE nie jest kopiowana z r599 ani tworzona przed poznaniem
pełnego UNIVERSE. System najpierw przygotowuje raport jakości i kompletności,
następnie liczy próbne warianty progów bez nadawania członkostwa BASE. Raport
pokazuje wyniki i powody. Dopiero po jawnej akceptacji reguł przez użytkownika
powstaje pierwsza wersja `base_state`.
RATIONALE: progi muszą być ocenione na rzeczywistym pełnym zasobie, aby uniknąć
przeniesienia błędnych kwalifikacji OLD i nieświadomego zawężenia BASE.
SUPERSEDES: automatyczne kopiowanie `base_ok` r599 i tworzenie BASE przed raportem;
zamyka `UD-02`.
AFFECTED VERSION: dokumentacja `DOCS-2026-08-24-02-DRAFT`; runtime bez zmian.

## D-010
DATE: 2026-08-24
STATUS: ACCEPTED
SOURCE: wymaganie użytkownika dotyczące wyglądu listingu
DECISION: Przed implementacją listingów SKOOP powstaje osobna paczka projektu
graficznego `SKOOP-COMPANY-LISTING-DESIGN-001`. Obejmuje ona widoki UNIVERSE,
BASE i IPO, wspólny prawy panel, miniwykres i wykres powiększony, wszystkie stany,
interakcje, design tokens oraz jednoznaczne mapowanie na kontrakt danych. Projekt
zostaje przekazany Claude dopiero po wizualnej akceptacji użytkownika.
RATIONALE: wygląd i ergonomia są częścią produktu i nie mogą być improwizowane
podczas kodowania. OLD i V3 pozostają źródłami sprawdzonych inspiracji, ale nie
narzucają starej logiki ani nie zastępują nowego projektu.
SUPERSEDES: brak; ustanawia dodatkowy gate przed `SKOOP-COMPANY-LISTING-001`.
AFFECTED VERSION: dokumentacja `DOCS-2026-08-24-02-DRAFT`; runtime bez zmian.


## D-017
DATE: 2026-08-24
STATUS: ACCEPTED
SOURCE: UD-M-04 paczki SKOOP-MASSIVE-ACCESS-001 — AKCEPTUJĘ OPCJĘ A
DECISION: Aneks do D-007. Zakaz pobierania danych pozostaje bezterminowo w mocy
dla Stock Scanner OLD: OLD pozostaje zamrożony, offline i bez dostępu do
Massive. Nowy SKOOP na tym komputerze może korzystać z Massive wyłącznie w
ramach osobno zaakceptowanych paczek i ich Implementation Contract. Niniejszy
aneks nie uruchamia żadnego pobierania i nie jest samodzielną zgodą na
nieograniczony ruch sieciowy.
RATIONALE: D-007 dotyczył uzupełniania danych OLD; roadmapa SKOOP (STAN §5)
przewiduje kontrolowany dostęp Massive nowego produktu na tym komputerze.
Decyzja UD-M-04 zamyka konflikt CM-04 paczki SKOOP-MASSIVE-ACCESS-001.
SUPERSEDES: zakres D-007 wyłącznie w części odnoszącej się do nowego SKOOP;
zakaz dla OLD pozostaje bez zmian.
AFFECTED VERSION: dokumentacja; runtime bez zmian.



## D-018
DATE: 2026-08-25
STATUS: ACCEPTED
SOURCE: `WYNIKI GATE B — AKCEPTUJĘ`
DECISION: Paczka `SKOOP-MASSIVE-ACCESS-001` oraz wyniki Gate A/Gate B są
zaakceptowane. Kontrolowany test zakończył się licznikiem 29/50, bez importu
UNIVERSE, bez zapisów do OLD i ze stanem końcowym kill switch ON. Pakiet dostępu
zostaje zamrożony; akceptacja nie zezwala na stały ruch, import ani utworzenie
bazy produktu. Następny etap wymaga osobnej paczki `SKOOP-UNIVERSE-IMPORT-001`.
RATIONALE: dostęp, bezpieczeństwo, zakres planu i podstawowe endpointy zostały
sprawdzone realnym testem, a ograniczenia źródła są jawne i zaakceptowane.
SUPERSEDES: status Gate B BLOCKED oraz stan Massive nieautoryzowany dla nowego
SKOOP; nie zmienia zakazu dla OLD ani package isolation.
AFFECTED VERSION: `DOCS-2026-08-25-01`; lokalna paczka dostępu zainstalowana,
produktowa baza i import bez zmian.

## D-019
DATE: 2026-08-25
STATUS: ACCEPTED
SOURCE: korekty użytkownika po Gate B dotyczące historii i klasyfikacji
DECISION: SKOOP przechowuje i wykorzystuje historię do 5 lat; dłuższe okresy
użytkownik sprawdza w TradingView. Massive dostarcza surową informację
klasyfikacyjną, w tym SIC, lecz kanoniczne `canonical_sector` i
`canonical_industry` nadaje SKOOP. Nazwy i taksonomia są synchronizowane z
TradingView. Mapowanie przechowuje wersję, źródło, czas zmiany użytkownika,
historię i ręczny override; ręczna korekta ma pierwszeństwo do jawnego cofnięcia.
RATIONALE: pięć lat pokrywa potrzeby wykresów i strategii SKOOP bez zbędnego
kosztu, a zgodna z TradingView klasyfikacja zapewnia spójność pracy użytkownika
niezależnie od niepełnej taksonomii providera.
SUPERSEDES: traktowanie historii z 2010 r. jako wymagania produktu oraz
traktowanie sektora/branży Massive jako kanonicznej klasyfikacji SKOOP.
AFFECTED VERSION: `DOCS-2026-08-25-01`; runtime danych jeszcze nieutworzony.
