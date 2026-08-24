# USER DECISIONS — SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001

Dokument append-only w ramach paczki. Odpowiedzi użytkownika zostaną zapisane bez
zmiany sensu. Decyzje architektoniczne po akceptacji trafią także do globalnego logu.

| ID | Data | Pytanie | Opcje | Decyzja użytkownika | Rekomendacja / uzasadnienie | Wpływ |
|---|---|---|---|---|---|---|
| UD-01 | 2026-08-23 | Co dokładnie obejmuje pierwszy UNIVERSE? | A: aktywne spółki z zatwierdzonego zakresu Massive, z jawnym filtrem typów; B: tylko główne giełdy USA; C: od razu odtworzyć mixed global OLD | `PENDING` | **A** — najpierw zobaczymy pełny katalog źródła i jawnie oznaczymy typy; niczego nie odrzucimy bez raportu | koszt importu, liczba rekordów, giełdy i waluty |
| UD-02 | 2026-08-23 | Jak uruchomić pierwszą BASE? | A: najpierw pełny UNIVERSE i raport, progi jako symulacja; B: od razu skopiować r599; C: ustalić nowe progi przed importem | `PENDING` | **A** — odpowiada celowi użytkownika: najpierw sprawdzić pełność i wpływ założeń | kolejność paczek i brak pochopnej kwalifikacji |
| UD-03 | 2026-08-23 | Co robić przy braku mcap/ADV/ceny? | A: `PENDING_DATA`; B: historyczny fail-open; C: `NOT_QUALIFIED` | `PENDING` | **A** — brak danych nie jest ani pozytywną, ani negatywną oceną | jakość BASE i kolejka uzupełniania |
| UD-04 | 2026-08-23 | Co dokładnie dzieje się po 180. sesji IPO? | A: znika tylko odznaka IPO, a BASE nadal zależy od reguł; B: każda spółka IPO automatycznie wchodzi do BASE od sesji 181 | `PENDING` | **A** — chroni znaczenie BASE jako listy zakwalifikowanej; spółka już będąca BASE pozostaje w BASE | zamknięcie konfliktu C-01/C-02 |
| UD-05 | 2026-08-23 | Jak aktualizować wykres IPO, które nie jest w BASE? | A: codzienny 1D + intraday po otwarciu spółki; B: pełne ciągłe intraday jak BASE | `PENDING` | **A** — zapewnia wykres i ogranicza stałe zużycie zasobów | późniejszy market sync i Massive budget |
| UD-06 | 2026-08-23 | Jak pokazywać waluty? | A: przechowywać natywną i USD, listing domyślnie porównawczy USD; B: tylko natywna; C: tylko USD | `PENDING` | **A** — porównywalność bez utraty wartości źródłowej | pola, FX, sortowanie |
| UD-07 | 2026-08-23 | Czy link może być wyszukiwarką, gdy brak direct URL? | direct tylko `VERIFIED`; osobny przycisk `Szukaj` może istnieć i musi być oznaczony | `CONFIRMED FROM USER REQUIREMENT` | brak zmyślonych URL | resolver i UI |
| UD-08 | 2026-08-23 | Czy BASE i IPO mogą nakładać się? | tak; jedna spółka, dwa statusy | `CONFIRMED FROM USER REQUIREMENT` | brak duplikacji i zgodność z wymaganiem | model danych |
| UD-09 | 2026-08-23 | Czy przyjąć skorygowany harmonogram z §8.1 SPEC? | A: universe 04:00 ET, daily po finalnej sesji, BASE po wersjach/zmianie reguł, IPO 1× dziennie po starcie regularnej sesji USA z opóźnieniem ustalonym testem + retry po błędzie, BASE market co 5 min; B: wskazać korekty | `PENDING — UPDATED BY USER CORRECTION` | **A** — nowe IPO są wykrywane po rozpoczęciu handlu; nie zgadujemy dokładnej minuty bez testu źródła | scheduler i kolejność publikacji |
| UD-10 | 2026-08-23 | Jaki jest porządek aktualizacji spółek? | kliknięta → aktywne sygnały → obserwowane → aktywne portfele → najbardziej płynne USA → pozostałe | `CONFIRMED FROM USER REQUIREMENT` | zastępuje odzyskane wagi r599 dla nowego SKOOP | kolejki workerów i focus |
| UD-11 | 2026-08-23 | Jak traktować oczekujące zlecenie w priorytetach? | w profilu należy do poziomu portfela T3; kontrola ceny i wykonanie mają osobną najwyższą ścieżkę bezpieczeństwa | `RESOLVED BY ISOLATED EXECUTION CONTRACT` | nie udaje otwartej pozycji i nie czeka za profilami | portfolio/order queue |
| UD-12 | 2026-08-23 | Czy zatwierdzić trzy listingi i ich pola z §7? | UNIVERSE audytowy; BASE inwestycyjny z wykresem; IPO z odzyskanymi polami OLD | `CONFIRMED FROM USER REQUIREMENT` | użytkownik potwierdził trzy różne listingi | API i UI listingów |
| UD-13 | 2026-08-23 | Czy data/godzina ostatniego sukcesu ma być obowiązkowa przy każdej spółce? | tak, per blok danych, ze strefą czasu i osobnym ostatnim błędem | `CONFIRMED FROM USER REQUIREMENT` | diagnostyka danych i procesów | schema/API/UI/acceptance |
| UD-14 | 2026-08-23 | Czy zatwierdzić hierarchię TF z §8.5? | 1D/1H główne; 30m wyprzedza 1H; 2H/4H wspierają 1D | `CONFIRMED FROM USER REQUIREMENT` | zgodne z testami V3 i sugestią użytkownika | market sync, payloady i UI |
| UD-15 | 2026-08-23 | Czy każda spółka ma wspólny prawy panel z każdego listingu? | tak, ten sam `instrument_id`, sekcje zależne od statusów | `CONFIRMED FROM USER REQUIREMENT` | spójna praca w UNIVERSE/BASE/IPO | UI i API profilu |
| UD-16 | 2026-08-23 | Czy każda spółka ma ręczne korekty z historią? | tak, overlay bez niszczenia surowych danych; ceny/świece tylko przez audytowaną korektę danych | `CONFIRMED FROM USER REQUIREMENT` | bezpieczeństwo i ślad zmian | schema/API/UI/audit |
| UD-17 | 2026-08-23 | Czy listing ma aktualizować się rekordowo bez czekania na cały zbiór? | tak; poprzednia sesja od razu, postęp w nagłówku, ostatnie poprawne dane per spółka | `CONFIRMED FROM USER REQUIREMENT` | płynna praca bez blokowania 5000 spółek | publication/API/UI |
| UD-18 | 2026-08-23 | Jak opisujemy bezpieczne udostępnianie danych? | prosty opis: najpierw sprawdzamy nowy rekord, potem zastępujemy poprzedni; bez technicznego żargonu | `CONFIRMED FROM USER REQUIREMENT` | język zrozumiały dla użytkownika | dokumentacja i UI |
| UD-19 | 2026-08-23 | W jakiej strefie pokazujemy czas aktualizacji? | zawsze czas lokalny użytkownika; wewnętrznie UTC | `CONFIRMED FROM USER REQUIREMENT` | spójność i czytelność | schema/API/UI |
| UD-20 | 2026-08-23 | Jak działa kolejka płynności USA? | wszystkie pozostałe USA malejąco po ADV20, bez bloków i limitu liczby; proces idzie do końca i wznawia po pilniejszym zadaniu | `CONFIRMED FROM USER REQUIREMENT` | pełna, płynna aktualizacja | scheduler/queue/tests |

## Gate

- wszystkie pytania rozstrzygnięte: **NO — UD-01–UD-06 oraz UD-09**;
- decyzje globalne zarejestrowane: **NO — czeka na odpowiedzi**;
- można tworzyć Implementation Contract: **NO**.
