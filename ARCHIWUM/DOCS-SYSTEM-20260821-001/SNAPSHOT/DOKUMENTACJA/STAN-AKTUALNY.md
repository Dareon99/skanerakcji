# STAN AKTUALNY — SKANER WYKRESÓW

**Data snapshotu:** 2026-08-21  
**Wersja kodu:** `2026-08-21-r599`  
**Status dokumentu:** `CONFIRMED` na podstawie audytu plików, odzyskanego acceptance i stanu runtime

## 1. Najważniejszy stan operacyjny

| Obszar | Stan | Znaczenie |
|---|---|---|
| Kod projektu `C:\Skaner wykresów` | `PRESENT / READ-ONLY AUDITED` | źródła, testy, narzędzia V3 i raporty istnieją |
| Dane `C:\skaner-dane` | `PRESENT` | `scanner.db` i `market.db` istnieją; nie wykonywano mutacji w ramach recovery |
| Główny serwer aplikacji | `OFF` | brak procesu nasłuchującego na porcie 8000; główny interfejs nie może ładować wykresów |
| Zadania autostartu `SkanerWykresow*` | `ABSENT` | nie znaleziono aktywnego mechanizmu automatycznego uruchomienia |
| Massive Traffic Manager — bieżąca konfiguracja | `ON` | `massive_traffic_manager_enabled = 1`; zmiana pliku 2026-08-21 14:33:46 |
| Pomiar Massive Traffic | `OFF` | `massive_traffic_measurement_enabled = 0` |
| Audyt r599 | `PASS 181 / FAIL 0` | akceptacja techniczna dotyczy stanu manager OFF |
| `provider_state.db` | `PRESENT / INTEGRITY OK` | utworzony 2026-08-21 14:36:25; `user_version=1`, WAL, schema zgodna, `count_429=0` |
| Acceptance aktywacji managera | `ACCEPTED + ACTIVATED` | live status PASS po starcie, około 13 i 20 minutach; manager pozostawiony ON |
| Generator/dashboards V3 | `RECOVERED` | finalny szybki dashboard odbudowany offline z zachowanych payloadów |
| Integracja V3 z głównym UI | `NOT IMPLEMENTED / CONFIRMED` | narzędzia i raporty V3 były walidacją poza produkcją |

## 2. Diagnoza zatrzymania wykresów

Występują dwa różne problemy:

1. **Bloker natychmiastowy:** aplikacja jest wyłączona. Główny frontend korzysta z endpointu `/candles/{symbol}` na serwerze lokalnym, więc bez procesu na porcie 8000 nie załaduje żadnego wykresu.
2. **Bloker architektoniczny:** dopracowany renderer V3 z pięcioma interwałami nie został podłączony do głównego API/UI. Obecny endpoint `/candles/{symbol}` nadal używa starszej ścieżki pobierania danych i starszych obliczeń wskaźników.

Bieżąca i zaakceptowana flaga managera jest ON, ale serwer jest OFF. Sama flaga nie generuje wykresów bez uruchomionego procesu. Następny kontrolowany start powinien zachować manager ON; nie należy cofać zaakceptowanej aktywacji przy okazji przywracania wykresów.

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

## 4. Czego nie wykonano w ramach recovery i budowy dokumentacji

- nie uruchomiono aplikacji ani skanera;
- recovery nie włączyło managera; późniejsza zmiana flagi przez paczkę/operację `MASSIVE-TRAFFIC-ACTIVATION-001` została wykryta read-only;
- przed instalacją systemu dokumentacji nie zmieniono kodu produkcyjnego; instalacja dodała wyłącznie pliki sterowania i `DOKUMENTACJA`;
- nie zmieniono baz w `C:\skaner-dane`;
- nie podłączono V3 do głównego UI;
- nie uznano niepotwierdzonych elementów alarmów ani scoringu za odzyskane.

## 5. Najkrótsza bezpieczna droga do wznowienia procesu

Następny pakiet powinien mieć nazwę `CHARTS-RESTORE-20260821-001`:

1. preflight r599, manager ON i istniejącego zdrowego `provider_state.db`;
2. kontrolowany start bez zmiany konfiguracji;
3. test jednego symbolu przez `/candles/{symbol}` i główne UI;
4. kontrola logów, portu, managera i nieplanowanych mutacji;
5. acceptance albo kontrolowany stop/rollback operacyjny;
6. osobna paczka integracji finalnego V3.

Uruchomienie jest zmianą stanu produkcyjnego i wymaga jawnej zgody użytkownika oraz osobnego Implementation Contract.

## 6. Dokumenty obowiązkowe na początku kolejnej sesji

1. `MASTER-PROJEKT.md`
2. `STAN-AKTUALNY.md`
3. `ARCHIWUM/PROJECT-RECOVERY-001/RECOVERY-REPORT-2026-08-21.md`
4. `ARCHIWUM/PROJECT-RECOVERY-001/WYKRESY/FINAL-AS-BUILT-SPEC.md`
5. dla prac nad listą sygnałów: `ARCHIWUM/PROJECT-RECOVERY-001/SKANER-CYKLE-1D/RECOVERED-SPEC.md`

Braki należy oznaczać `UNVERIFIED` albo `TO RECOVER`; nie wolno ich uzupełniać przez zgadywanie.

## 7. System ciągłości projektu

| Pole | Stan |
|---|---|
| Wersja dokumentacji | `DOCS-2026-08-21-01` |
| Kanoniczna lokalizacja | `C:\Skaner wykresów\DOKUMENTACJA` |
| Decyzja systemowa | `D-003 ACCEPTED` |
| Protokół ChatGPT/Codex/Claude | zainstalowany |
| Szablony pełnego workflow | zainstalowane |
| Automatyczna kontrola systemu/hashów | PASS dla wymaganych plików i manifestów; WARN: Git nie jest jeszcze zainicjalizowany |
| Git w projekcie | `INITIALIZED`, branch `main`, brak pierwszego commitu |
| Git user.name / user.email | `TO CONFIGURE` |
| Git remote | brak; `TO CONFIGURE / DECISION REQUIRED` |
| Runtime/bazy przez instalację dokumentacji | bez zmian; zastany manager ON/provider DB zapisano jako fakt |

Każda sesja ma rozpoczynać się od dokumentów wskazanych w `DOKUMENTACJA/README.md` i kończyć handoffem oraz aktualizacją STAN albo jawnym `NO STATE CHANGE`.
