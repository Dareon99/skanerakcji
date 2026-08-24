# STAN AKTUALNY — SKANER WYKRESÓW

**Data snapshotu danych:** 2026-08-21  
**Data aktualizacji operacyjnej:** 2026-08-24
**Wersja kodu:** `2026-08-21-r599`  
**Status dokumentu:** `CONFIRMED — LEGACY FROZEN / SKOOP CONTRACT IN PROGRESS`  
**Wersja dokumentacji:** `DOCS-2026-08-24-02`

## 1. Najważniejszy stan operacyjny

| Obszar | Stan | Znaczenie |
|---|---|---|
| Kod projektu `C:\Skaner wykresów` | `PRESENT / LEGACY / NOT TO RESTART` | zachowane źródło doświadczeń; ręczne launchery istnieją, ale nie wolno ich uruchamiać |
| Dane `C:\skaner-dane` | `PRESENT / LEGACY` | zachowane; snapshot sprzed efektu połączenia backupowego znajduje się w `DATA-RAW` |
| Stary serwer r599 | `BLOCKED / NOT TO RESTART` | launchery nie wskazują już na stary `run.py` |
| Lokalna powłoka SKOOP/OLD | `INSTALLED / TESTED / CURRENTLY OFF` | `C:\SKOOP Skaner wykresów`; po uruchomieniu `127.0.0.1:8000` |
| Zadania autostartu `SkanerWykresow*` | `ABSENT` | nie znaleziono aktywnego mechanizmu automatycznego uruchomienia |
| Massive Traffic Manager — konfiguracja historyczna r599 | `ON IN CONFIG / RUNTIME OFF` | zaakceptowana flaga pozostaje faktem historycznym; zamrożony OLD nie może wykonywać żądań |
| Pomiar Massive Traffic | `OFF` | `massive_traffic_measurement_enabled = 0` |
| Audyt r599 | `PASS 181 / FAIL 0` | akceptacja techniczna dotyczy stanu manager OFF |
| `provider_state.db` | `PRESENT / INTEGRITY OK` | utworzony 2026-08-21 14:36:25; `user_version=1`, WAL, schema zgodna, `count_429=0` |
| Acceptance aktywacji managera | `ACCEPTED + ACTIVATED` | live status PASS po starcie, około 13 i 20 minutach; manager pozostawiony ON |
| Generator/dashboards V3 | `RECOVERED` | finalny szybki dashboard odbudowany offline z zachowanych payloadów |
| Integracja V3 z głównym UI | `NOT IMPLEMENTED / CONFIRMED` | narzędzia i raporty V3 były walidacją poza produkcją |
| Archiwum „Skaner sygnałów kupna” | `IMPORTED / MERGED / FROZEN` | 15 plików, manifest 14/14 PASS; ZIP SHA-256 `f2075b...529a` |
| Freeze OLD | `COMPLETED` | `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001` |
| Nowy produkt | `FOUNDATION PLACEHOLDER / DATA CONTRACT IN PROGRESS` | aktywna paczka `SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001`; bez Massive, workerów i bazy nowego produktu |
| Stock Scanner OLD UI | `IMPLEMENTED / READ ONLY` | listing, szczegół spółki i lokalne wykresy z frozen SQLite |
| Dalsze pobieranie na tym komputerze | `CANCELLED / NOT REQUIRED` | istniejąca próbka zaakceptowana; pełny żywy skaner działa na drugim komputerze |
| GitHub dokumentacji | `PUBLISHED / CONNECTED` | `Dareon99/skanerakcji`, branch `main`; Claude zaczyna od repozytoryjnego `CLAUDE.md` |

## 2. Decyzja operacyjna po diagnozie wykresów

Starego serwera nie przywracamy do pracy. Użytkownik zdecydował o odseparowaniu nowych założeń od starych, zasobożernych mechanizmów. Dlatego wcześniejszy plan uruchomienia starego `/candles/{symbol}` został zastąpiony przez:

1. zamrożenie starego systemu jako `Stock Scanner OLD`;
2. zachowanie jego projektu, danych, testów, V3 i pomysłów jako źródła referencyjnego;
3. budowę niezależnego `SKOOP Skaner wykresów`;
4. implementację trybu OLD jako lokalnego read-only demo bez Massive, workerów i aktualizacji — `DONE 2026-08-22`.

Odzyskany renderer V3 pozostaje wartościowym kontraktem do ponownej integracji w SKOOP. Nie wolno uruchamiać starej aplikacji tylko po to, aby odzyskać wykresy.

## 3. Co zostało odzyskane

- komplet `30/30` payloadów: 6 spółek × 5 interwałów;
- działający offline dashboard: `ARCHIWUM/PROJECT-RECOVERY-001/WYKRESY/v3-fast-segmentation/index.html`;
- spółki: `RBLX`, `AAOI`, `INTU`, `NVDA`, `PLTR`, `ADTN`;
- interwały: `30m`, `1H`, `2H`, `4H`, `1D`;
- finalne testy V3 zapisane w źródłach: `394 PASS / 0 FAIL`;
- specyfikacja reguł listy `Cykle 1D` odzyskana z rozmów;
- osiem screenshotów/referencji zachowanych jako osobne artefakty;
- finalna architektura zasobów V4.4 zachowana w snapshotcie;
- źródła generatora, szablonu i testów zachowane w archiwum recovery.
- pakiet historycznej rekonstrukcji rozmowy, decyzji i r599 zachowany w `ARCHIWUM/PROJECT-RECOVERY-ARCHIVE-20260821-002/SOURCE-ARCHIVE/`;
- nazwy P0–P3 potwierdzone w pakiecie i kodzie: `INTERACTIVE_MARKET`, `SCANNER_CRITICAL`, `MAINTENANCE`, `COMPANY_BACKGROUND`.

## 4. Co wykonano i czego jeszcze nie wykonano

- wykryto rzeczywiście działający stary runtime, kontrolowanie zatrzymano endpoint skanera i trzy potwierdzone procesy;
- po stop potwierdzono stabilność baz, brak listenera 8000 i brak połączeń starego procesu;
- utworzono kopię projektu 1:1 i `DATA-RAW` 11/11 plików, 2535842688/2535842688 bajtów;
- utworzono logiczne backupy `scanner.db`, `market.db` i `provider_state.db`; wszystkie `integrity_check=ok` i `quick_check=ok`;
- połączenie narzędzia SQLite utworzyło/odświeżyło źródłowe pliki `-shm` i pusty `scanner.db-wal`; główne DB nie zostały zmienione, a `DATA-RAW` zachowuje stan sprzed tego efektu;
- nie zmieniono kodu produkcyjnego;
- nie podłączono V3 do głównego UI;
- utworzono `C:\SKOOP Skaner wykresów` z placeholderem SKOOP i OLD read-only; nowa baza SKOOP nadal nie istnieje;
- nie użyto klucza Massive i nie wykonano żądań nowego produktu;
- na decyzję użytkownika nie uzupełniano braków danych; próbka OLD jest finalnym zakresem tego komputera;
- nie uznano niepotwierdzonych elementów alarmów ani scoringu za odzyskane.

## 5. Najkrótsza bezpieczna droga do wznowienia procesu inwestycyjnego

Aktywna paczka: `SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001`, etap `USER DECISIONS`.

Kolejność programu:

1. `DONE` — niezależny fundament w `C:\SKOOP Skaner wykresów`, bez sieci i workerów;
2. `IN PROGRESS` — kontrakt UNIVERSE–BASE–IPO i pól listingu;
3. `SKOOP-MASSIVE-ACCESS-001`: lokalny sekret, maskowanie, jeden tani smoke request i weryfikacja bieżących limitów;
4. `SKOOP-UNIVERSE-IMPORT-001`: pobranie surowego uniwersum instrumentów;
5. `SKOOP-COMPANY-RESOURCES-001`: kwalifikacja spółek i arkusz/model każdej spółki;
6. `SKOOP-COMPANY-LISTING-DESIGN-001`: projekt graficzny UNIVERSE/BASE/IPO,
   wspólnego panelu i wykresów; obowiązkowe wizualne acceptance;
7. `SKOOP-COMPANY-LISTING-001`: implementacja zatwierdzonego projektu, filtrowania,
   sortowania, zarządzania i edycji;
8. `SKOOP-CHARTS-V3-INTEGRATION-001`: podpięcie odzyskanych wykresów do spółek;
9. izolowane paczki nowych mechanizmów skanera;
10. alerty dopiero po stabilizacji fundamentu, danych, listingu, wykresów i skanera.

Każdy krok jest osobną paczką i kończy się acceptance. `CHARTS-RESTORE-20260821-001` starego produktu jest `SUPERSEDED / CANCELLED` decyzją D-006.

## 6. Dokumenty obowiązkowe na początku kolejnej sesji

1. `MASTER-PROJEKT.md`
2. `STAN-AKTUALNY.md`
3. `ARCHIWUM/PROJECT-RECOVERY-001/RECOVERY-REPORT-2026-08-21.md`
4. `ARCHIWUM/PROJECT-RECOVERY-001/WYKRESY/FINAL-AS-BUILT-SPEC.md`
5. dla prac nad listą sygnałów: `ARCHIWUM/PROJECT-RECOVERY-001/SKANER-CYKLE-1D/RECOVERED-SPEC.md`
6. `ARCHIWUM/PROJECT-RECOVERY-ARCHIVE-20260821-002/FINAL-AS-BUILT-SPEC.md`
7. `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001\PACKAGE\FINAL-AS-BUILT-SPEC.md`
8. dla Claude: `CLAUDE-PROCESS-OLD-FREEZE.md` i `CLAUDE-ROADMAP-SKOOP.md` z tej samej paczki
9. `C:\SKOOP Skaner wykresów\README-START-HERE.md`
10. `LEGACY-DATA-COMPLETION-AND-OFFLINE-SHELL-20260821-001\FINAL-AS-BUILT-SPEC.md`

Braki należy oznaczać `UNVERIFIED` albo `TO RECOVER`; nie wolno ich uzupełniać przez zgadywanie.

## 7. System ciągłości projektu

| Pole | Stan |
|---|---|
| Wersja dokumentacji | `DOCS-2026-08-24-02` |
| Kanoniczna lokalizacja robocza | bieżący lokalny katalog `SYSTEM-PRACY-SKANERA\DOKUMENTACJA` |
| Zdalny mirror dokumentacji | `https://github.com/Dareon99/skanerakcji`, `main`, pierwszy commit `5218bf2` |
| Decyzje systemowe | `D-003 ACCEPTED`; `D-006 ACCEPTED`; `D-007 ACCEPTED`; `D-009–D-016 ACCEPTED` |
| Protokół ChatGPT/Codex/Claude | zainstalowany |
| Szablony pełnego workflow | zainstalowane |
| Automatyczna kontrola systemu/hashów | `FAIL=0 / WARN=2`; wymagane pliki i wszystkie frozen manifesty PASS; WARN: niezatwierdzone zmiany Git i brak remote |
| Git dokumentacji | `INITIALIZED / PUBLISHED`, branch `main`, tracking `origin/main` |
| Git identity dokumentacji | repo-local `Dareon99` / adres GitHub noreply |
| Git remote | `origin = https://github.com/Dareon99/skanerakcji.git` |
| Legacy runtime | `OFF / FROZEN / NOT TO RESTART` |
| Launcher użytkownika | przekierowany na `C:\SKOOP Skaner wykresów\URUCHOM-SKOOP.bat` |
| Offline shell | 4/4 testy PASS; HTTP 200; POST 405; external connections 0 |
| Snapshot OLD | `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001` |
| Bazy | RAW snapshot zachowany; 3 logiczne backupy SQLite PASS; efekt sidecar jawnie opisany |
| Import źródłowy | `PROJECT-RECOVERY-ARCHIVE-20260821-002`; źródło zamrożone, bez nadpisania nowszego MASTER-a |

Każda sesja ma rozpoczynać się od dokumentów wskazanych w `DOKUMENTACJA/README.md` i kończyć handoffem oraz aktualizacją STAN albo jawnym `NO STATE CHANGE`.

## 8. Korekta OLD 1:1 — 2026-08-22

| Pole | Stan potwierdzony |
|---|---|
| Domyślny widok | nowy SKOOP, `http://127.0.0.1:8000/` |
| Stock Scanner OLD | oryginalny frontend r599, `http://127.0.0.1:8001/` |
| Kod OLD runtime | `C:\SKOOP Skaner wykresów\OLD-r599-1TO1` |
| Dane OLD runtime | kopia frozen w `C:\SKOOP Skaner wykresów\OLD-RUNTIME-DATA` |
| Wygląd/zasoby | oryginalne zakładki, panele, listingi, portfele, cykle, IPO i wykresy r599 |
| Providerzy | Massive i Yahoo zablokowane |
| Workery | zablokowane |
| Zapis | SQLite immutable/query-only; mutacje HTTP 405 |
| Test wizualny | PASS 1920×1080; pełny ekran OLD i wykres NVDA widoczne |
| Połączenia zewnętrzne OLD | 0 |
| Hash baz runtime vs archive | 3/3 MATCH |
| Decyzje | D-003, D-006, D-007, D-008 ACCEPTED |
| AS-BUILT | `02-AS-BUILT/OLD-R599-1TO1-FROZEN-AS-BUILT.md` |

Poprzedni uproszczony ekran OLD jest `SUPERSEDED`. Nie jest już źródłem
prawdy o tym, co użytkownik otrzymuje po kliknięciu OLD.

## 9. Aktywny kontrakt nowego SKOOP — 2026-08-24

| Pole | Stan |
|---|---|
| Package ID | `SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001` |
| Etap workflow | `SPEC → AUDIT → CONFLICT REPORT → USER DECISIONS → ACCEPTANCE` wykonane; paczka frozen |
| Implementacja | `NOT AUTHORIZED`; zaakceptowano wyłącznie kontrakt logiczny |
| Massive | nie użyto; brak autoryzacji w tej paczce |
| Nowa baza SKOOP | nie utworzono |
| OLD/frozen DB | bez zmian; audit tylko read-only |
| Główne konflikty | brak konfliktu blokującego logiczny kontrakt; C-09 odroczony do market-sync |
| Następny krok | osobna paczka `SKOOP-MASSIVE-ACCESS-001` od SPEC/AUDIT; bez użycia klucza przed kontraktem |
| Przekazanie do Claude | finalny logiczny SPEC zaakceptowany; Claude nie ma zgody na kodowanie ani Massive |
| Dostęp Claude przez GitHub | `READY`; lokalna ścieżka Windows nie jest wymagana do odczytu dokumentacji |
