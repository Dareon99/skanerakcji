# SPECYFIKACJA WYKONAWCZA DLA CLAUDE

```text
PACKAGE: SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001
DOCUMENT STATUS: READY FOR READ/AUDIT HANDOFF
CURRENT AUTHORIZATION: L0 — DOCUMENTATION AND READ-ONLY AUDIT ONLY
IMPLEMENTATION: BLOCKED — FINAL SPEC ACCEPTANCE AND SEPARATE IMPLEMENTATION CONTRACT REQUIRED
TARGET PRODUCT: C:\SKOOP Skaner wykresów
LEGACY PRODUCT: C:\Skaner wykresów — READ-ONLY REFERENCE / DO NOT START
```

## 1. Cel tego dokumentu

Ten dokument jest instrukcją bezpiecznego przejęcia zadania przez Claude. Nie jest
zgodą na kodowanie. Ma zapobiec rozpoczęciu pracy z niepełnego promptu, z pamięci
rozmowy albo na podstawie nieaktualnych mechanizmów OLD.

Claude ma najpierw odtworzyć stan projektu z dokumentów, sprawdzić zgodność źródeł
i respektować gate aktywnej paczki. Dopiero późniejszy, kompletny i zaakceptowany
`05-IMPLEMENTATION-CONTRACT.md` może upoważnić do zmiany kodu, bazy lub runtime.

Nie można zagwarantować braku wszystkich błędów samą treścią polecenia. Ryzyko ma
być ograniczone przez mały zakres, kontrolę przed zmianą, testy, acceptance i
możliwy rollback.

## 2. Źródła prawdy i kolejność ważności

Claude nie może traktować treści czatu ani własnej pamięci jako źródła prawdy.
Obowiązuje następująca kolejność:

1. jawne, najnowsze decyzje użytkownika zapisane w aktywnej paczce;
2. zaakceptowany `05-IMPLEMENTATION-CONTRACT.md` aktywnej paczki;
3. `01-SPEC.md`, `02-AUDIT.md`, `03-CONFLICT-REPORT.md` i
   `04-USER-DECISIONS.md` aktywnej paczki;
4. bieżące `MASTER-PROJEKT.md`, `STAN-AKTUALNY.md`, globalny log decyzji i zasady
   projektu;
5. właściwy `FINAL-AS-BUILT-SPEC.md` zaakceptowanej wcześniejszej paczki;
6. frozen OLD, odzyskane rozmowy, screenshoty i archiwalne roadmapy — wyłącznie
   jako materiał referencyjny.

Jeżeli dwa źródła są sprzeczne, Claude ma zatrzymać pracę, podać oba zapisy,
ich ścieżki i wpływ. Nie wolno samodzielnie wybierać wygodniejszej wersji.

## 3. Dokumenty obowiązkowe do pełnego odczytu

Kanoniczny katalog przekazania tej paczki:

`C:\Users\Asus\.codex\.chatgpt-projects\g-p-6a8036fc74548191a899074cdfb449a6\SYSTEM-PRACY-SKANERA\DOKUMENTACJA`

Jeżeli dokumentacja jest czytana przez GitHub, katalog główny repozytorium
`Dareon99/skanerakcji` zastępuje powyższą lokalną ścieżkę jako punkt startowy.
Brak dostępu Claude do dysku `C:` nie jest wtedy błędem projektu. Claude nadal nie
może zakładać dostępu do lokalnego runtime, OLD, baz ani sekretów.

Przed jakąkolwiek zmianą Claude ma przeczytać w całości:

1. `MASTER-PROJEKT.md`;
2. `STAN-AKTUALNY.md`;
3. `README.md`;
4. `00-STEROWANIE/ZASADY-PROJEKTU.md`;
5. `00-STEROWANIE/PROTOKOL-SESJI-AI.md`;
6. `04-DECYZJE/DECYZJE-PROJEKTOWE.md`;
7. wszystkie pliki `01`–`11` z aktywnej paczki
   `03-AKTYWNE-PACZKI/SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001`;
8. `C:\SKOOP Skaner wykresów\README-START-HERE.md`;
9. właściwe AS-BUILT wskazane w `STAN-AKTUALNY.md` — tylko te potrzebne do
   aktualnego zakresu.

Jeżeli pliku brakuje, jest pusty, nieczytelny albo ścieżka wskazuje inny stan niż
opisany, wynik brzmi `STOP — SOURCE MISSING OR DRIFTED`.

## 4. Obowiązkowy raport otwarcia sesji

Pierwsza odpowiedź Claude ma zawierać:

```text
SESSION OPENING REPORT
PROJECT: SKOOP Skaner wykresów
ACTIVE PACKAGE: SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001
TARGET ROOT: <sprawdzona ścieżka>
SOURCE-OF-TRUTH ROOT: <sprawdzona ścieżka>
PRODUCT STATE: <stan odczytany ze STAN>
PACKAGE GATE: <stan odczytany z README i 05>
IMPLEMENTATION AUTHORIZED: YES/NO
PENDING USER DECISIONS: <lista ID>
CONFLICTS/DRIFT: <lista albo NONE>
FILES CHANGED: NONE
NETWORK USED: NO
DATABASES WRITTEN: NO
NEXT ALLOWED ACTION: <dokładnie jedna czynność>
```

Aktualnie oczekiwany wynik to:

```text
IMPLEMENTATION AUTHORIZED: NO
PENDING USER DECISIONS: NONE
NEXT ALLOWED ACTION: przedstawić użytkownikowi finalny logiczny SPEC do acceptance
```

Inny wynik wymaga wskazania dowodu w pliku, a nie założenia.

## 5. Aktualny zakres dozwolony Claude

Dozwolone są wyłącznie:

- pełny odczyt dokumentacji i read-only preflight wskazanych katalogów;
- porównanie statusów, wersji, ścieżek i źródeł;
- raport konfliktów, braków i niejednoznaczności;
- przygotowanie pytań decyzyjnych dla użytkownika;
- uzupełnienie dokumentacji aktywnej paczki po jawnej odpowiedzi użytkownika;
- przygotowanie projektu Implementation Contract dopiero po zamknięciu wszystkich
  decyzji i konfliktów.

Nie są dozwolone:

- zmiany kodu SKOOP albo OLD;
- tworzenie lub migracja bazy SKOOP;
- uruchamianie workerów, schedulerów, skanów lub starego r599;
- użycie Massive, Yahoo ani innego providera;
- odczyt, kopiowanie lub ujawnianie sekretów poza kontrolą przewidzianą w osobnej
  paczce dostępu;
- modyfikowanie frozen danych, backupów, manifestów albo archiwum;
- kopiowanie starego runtime, schematu lub reguł biznesowych do nowego produktu;
- wykonywanie większego zakresu „przy okazji”.

## 6. Ustalenia, których nie wolno zgubić

### 6.1 Model spółki i dane

- istnieje jedna logiczna tożsamość spółki/instrumentu;
- UNIVERSE, BASE i IPO są statusami lub członkostwami, a nie trzema kopiami tej
  samej spółki;
- dane mogą być fizycznie rozdzielone na bazy według odpowiedzialności, ale profil,
  członkostwa i świece nie mogą się dublować;
- BASE i IPO mogą się nakładać;
- brak danych nie może być potajemnie zamieniany na zero ani wartość domyślną;
- finalna kwalifikacja przy brakujących danych zależy od UD-03;
- każda spółka ma wspólny prawy panel niezależnie od listingu;
- każda spółka ma ręczne korekty z historią: kto/co, czas, wartość poprzednia,
  wartość nowa i powód;
- surowe dane providera pozostają zachowane; korekta jest osobną warstwą;
- korekta cen lub świec wymaga osobnego, audytowanego procesu.

### 6.2 Trzy listingi

- UNIVERSE: pełny listing kontrolny do oceny kompletności zasobu, filtrowania i
  sortowania;
- BASE: listing inwestycyjny spółek zakwalifikowanych do obserwacji, strategii,
  sygnałów, newsów i wykresów;
- IPO: listing spółek od wejścia na giełdę przez 180 sesji z polami właściwymi dla
  IPO, odzyskanymi i zweryfikowanymi ze starego systemu;
- szczegółowe pola i status ich potwierdzenia określa `01-SPEC.md`;
- ergonomia OLD może być inspiracją, ale jego błędne mechanizmy nie przechodzą do
  SKOOP;
- TradingView i Investing otrzymują tylko zweryfikowane, prawidłowe linki; jeśli
  bezpośredniego linku brak, można pokazać osobno oznaczone wyszukiwanie.
- przed implementacją listingu obowiązuje osobna, wizualnie zaakceptowana paczka
  `SKOOP-COMPANY-LISTING-DESIGN-001`; Claude nie projektuje wyglądu przy okazji
  kodowania i nie zastępuje brakującego projektu własną interpretacją.

### 6.3 Udostępnianie aktualnych danych

- użytkownik od razu widzi ostatnie poprawne dane, zwykle z poprzedniej sesji;
- aktualizacja idzie spółka po spółce i nie blokuje pracy do czasu ukończenia
  całego uniwersum;
- nowy rekord najpierw przechodzi kontrolę, potem zastępuje poprzedni poprawny
  rekord tej spółki;
- błąd jednej spółki nie blokuje pozostałych;
- listing pokazuje postęp aktualizacji i ostatni błąd bez ukrywania poprzednich
  poprawnych danych;
- przy spółce widoczny jest prosty zapis czasu, np.
  `Aktualizacja: 16:45, 12.07.2026`;
- czas jest zawsze prezentowany w lokalnej strefie użytkownika; wewnętrznie czas
  jest przechowywany jednoznacznie w UTC.

### 6.4 Kolejność aktualizacji

```text
T0 — spółka właśnie kliknięta/otwarta przez użytkownika
T1 — spółki z aktywnymi sygnałami
T2 — spółki obserwowane
T3 — spółki w aktywnych portfelach, w tym profil oczekującego zlecenia
T4 — wszystkie pozostałe spółki
```

- zadanie pilniejsze przerywa zwykłą kolejkę, a przerwana kolejka później wznawia
  pracę od miejsca zatrzymania;
- w T4 spółki USA idą płynnie od największego do najmniejszego `ADV20_USD`, bez
  sztucznych bloków, limitu top-N ani zatrzymania po pierwszej grupie;
- po USA system przechodzi przez pozostały zatwierdzony zakres giełd;
- kliknięcie nie może uruchamiać niekontrolowanego wielokrotnego pobierania;
- sprawdzanie ceny i wykonanie oczekującego zlecenia jest osobną krytyczną ścieżką,
  a nie zwykłą kolejką profili;
- kalendarz IPO jest osobnym procesem uruchamianym raz dziennie po rozpoczęciu
  regularnej sesji USA; dokładne opóźnienie ustala późniejszy test Massive.

### 6.5 Giełdy, sesje i wykresy

- każda giełda ma własny kalendarz i strefę czasu;
- wymagane stany obejmują co najmniej PRE, REGULAR, POST, CLOSED, HOLIDAY,
  EARLY_CLOSE, HALTED i UNKNOWN;
- rozszerzona sesja nie wchodzi domyślnie do wskaźników regularnej sesji;
- główne wykresy i potwierdzenia: `1D` oraz `1H`;
- `30m` wspiera i może wcześniej wskazać możliwość sygnału `1H`;
- `2H` i `4H` wspierają i mogą wcześniej wskazać możliwość sygnału `1D`;
- sygnał z interwału wspierającego pozostaje wczesny i niepotwierdzony do
  zamknięcia właściwej świecy głównego interwału;
- BASE ma wykresy stale aktualizowane według przyjętej kolejki;
- UNIVERSE poza BASE otrzymuje aktualny wykres po otwarciu przez użytkownika;
- sposób aktualizacji IPO poza BASE pozostaje decyzją UD-05.

## 7. Otwarte decyzje blokujące kodowanie

Claude ma odczytać pełne pytania i rekomendacje z `04-USER-DECISIONS.md`. Do
zamknięcia pozostają:

- `UD-01` — `ACCEPTED 2026-08-24 / OPTION A`: pełny katalog aktywnych spółek z zatwierdzonego zakresu Massive, jawna klasyfikacja, bez automatycznego kopiowania OLD;
- `UD-02` — `ACCEPTED 2026-08-24 / OPTION A`: pełny UNIVERSE i raport jakości, następnie próbne warianty progów bez członkostwa, akceptacja użytkownika i dopiero pierwsza BASE;
- `UD-03` — `ACCEPTED 2026-08-24 / OPTION A`: brak ceny, kapitalizacji lub ADV daje `PENDING_DATA`, jawny powód i ponowną ocenę po uzupełnieniu; nigdy zero, fail-open ani automatyczne odrzucenie;
- `UD-04` — `ACCEPTED 2026-08-24 / OPTION A`: po 180. sesji koniec aktywnego IPO i ponowna ocena BASE; BASE wyłącznie według reguł, bez automatycznego wejścia lub wyjścia;
- `UD-05` — `ACCEPTED 2026-08-24 / OPTION A`: IPO poza BASE ma sesyjny `1D` i przebieg od debiutu; intraday po kliknięciu T0 lub według T1–T3; IPO w BASE aktualizowane jak BASE;
- `UD-06` — `ACCEPTED 2026-08-24 / OPTION A`: wartość natywna pozostaje źródłowa, USD jest oddzielnym porównaniem z audytem FX; cena domyślnie natywna, kapitalizacja/obrót/ADV porównywalne w USD; brak FX = `PENDING_FX`;
- `UD-09` — `ACCEPTED 2026-08-24 / OPTION A WITH GUARDRAILS`: discovery 04:00 ET, 1D per giełda, IPO po starcie USA z opóźnieniem po smoke teście, BASE około 5 min, PRE/POST oddzielnie, T0–T4 i osobna execution path.

Claude nie może zamienić rekomendacji wpisanej w tabeli w decyzję użytkownika.
Wszystkie wymagane decyzje tej paczki są rozstrzygnięte. Implementacja nadal nie
jest dozwolona przed końcowym acceptance SPEC i osobnym kontraktem małej paczki.

## 8. Warunki późniejszego odblokowania implementacji

Kodowanie jest dozwolone wyłącznie, gdy łącznie:

1. wszystkie decyzje aktywnej paczki mają status `CONFIRMED` lub `ACCEPTED`;
2. conflict report nie zawiera nierozstrzygniętego konfliktu wpływającego na zakres;
3. `05-IMPLEMENTATION-CONTRACT.md` ma dokładny zakres plików, wersję przed/po,
   backup, rollback, test contract i STOP conditions;
4. w kontrakcie widnieje jawna akceptacja użytkownika;
5. preflight potwierdził brak source/version drift;
6. paczka kodowa jest mała i odizolowana od kolejnego etapu roadmapy.

Sam prompt, roadmapa, rekomendacja Claude albo status `DRAFT` nie stanowią zgody.

## 9. Wymagany sposób wykonania przyszłej paczki

Po odblokowaniu Claude realizuje wyłącznie zaakceptowany kontrakt:

1. SPEC;
2. AUDIT;
3. CONFLICT REPORT;
4. USER DECISIONS;
5. IMPLEMENTATION CONTRACT;
6. SMALL PACKAGE;
7. TEST;
8. ACCEPTANCE;
9. NEXT PACKAGE.

Nie wolno rozpocząć kolejnej paczki przed acceptance bieżącej.

## 10. Obowiązkowa kontrola jakości po ostatnim zapisie

Po `LAST WRITE`, a nie przed nim, Claude wykonuje w podanej kolejności:

1. `py_compile` wszystkich zmienionych plików Python;
2. kontrolę AST;
3. kontrolę invalid escape, statyczną i sanity;
4. testy jednostkowe i integracyjne określone w kontrakcie;
5. kontrolę integralności paczki i zakazu zmian poza zakresem;
6. kontrolę baz, jeśli kontrakt zezwolił na ich zmianę;
7. wyliczenie hashy artefaktów;
8. zapis wyników testów;
9. FREEZE zaakceptowanej paczki i `FINAL-AS-BUILT-SPEC.md`.

Każdy FAIL oznacza STOP. Nie wolno omijać testu, zmieniać oczekiwanego wyniku po
fakcie ani opisywać częściowego powodzenia jako PASS.

## 11. Minimalne kryteria przyszłych testów

Kontrakt implementacyjny musi dobrać testy do zakresu. Dla fundamentu danych
muszą później istnieć testy co najmniej dla:

- jednej tożsamości instrumentu i braku duplikacji UNIVERSE/BASE/IPO;
- nakładania się BASE i IPO;
- rozróżnienia braku danych od zera;
- historii ręcznych korekt bez nadpisania raw;
- czasu UTC w danych i czasu lokalnego w widoku;
- udostępniania ostatnich poprawnych danych podczas trwającej aktualizacji;
- awarii jednego rekordu bez blokady kolejki;
- przerwania i wznowienia T0–T4;
- pełnego przejścia USA malejąco po ADV20, bez limitu top-N;
- kalendarzy, świąt i skróconych sesji różnych giełd;
- rozdzielenia regularnej i rozszerzonej sesji;
- hierarchii 30m→1H oraz 2H/4H→1D;
- braku ruchu Massive i zmian OLD w paczkach, które tego nie autoryzują.

## 12. STOP rule

Claude zatrzymuje pracę natychmiast, gdy:

- brakuje źródła prawdy albo wersje się rozchodzą;
- aktywny kontrakt nadal ma status blokady;
- decyzja użytkownika jest niepełna lub sprzeczna;
- potrzebna zmiana wychodzi poza listę plików kontraktu;
- wykryto nieplanowaną zmianę kodu, danych lub bazy;
- potrzebny jest ruch sieciowy bez osobnej autoryzacji;
- backup lub rollback nie są pewne;
- test lub quality gate kończy się FAIL;
- istnieje ryzyko modyfikacji OLD albo frozen archive.

Po STOP Claude podaje: przyczynę, dowód, czego nie zmienił, wpływ oraz jedno
konkretne pytanie lub następny krok. Nie kontynuuje na podstawie domysłu.

## 13. Raport zamknięcia sesji

Każda sesja kończy się raportem zgodnym z `PROTOKOL-SESJI-AI.md`, zawierającym:

- status paczki;
- dokładne zmienione pliki;
- rzeczywiście wykonane testy i ich wyniki;
- ruch sieciowy i zapis do baz;
- konflikty i otwarte decyzje;
- rollback;
- aktualizację `STAN-AKTUALNY.md` albo jawne `NO STATE CHANGE`;
- dokładnie jeden następny krok.
