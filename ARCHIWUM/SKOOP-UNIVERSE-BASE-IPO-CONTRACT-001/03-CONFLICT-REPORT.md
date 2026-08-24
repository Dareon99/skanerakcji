# CONFLICT REPORT — SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001

```text
STATUS: CLOSED FOR CURRENT DECISION GATE — C-09 DEFERRED TO MARKET-SYNC PACKAGE
STOP ACTIVE: YES — UNTIL FINAL SPEC ACCEPTANCE AND SEPARATE IMPLEMENTATION CONTRACT
```

| ID | Źródło A | Źródło B | Konflikt | Wpływ | Opcje | Decyzja wymagana |
|---|---|---|---|---|---|---|
| C-01 | MASTER §4.1 | aktualne wymaganie użytkownika | MASTER wykluczał IPO z BASE; użytkownik dopuszcza nakładanie | model statusów i migracja | zachować stare / dopuścić overlap | `RESOLVED 2026-08-24 — UD-04 OPTION A`: IPO i BASE mogą się nakładać; koniec IPO nie zmienia samodzielnie BASE |
| C-02 | „po 180 sesjach zostają w BASE” | niezależna kwalifikacja BASE | nie było wiadomo, czy sesja 181 automatycznie nadaje BASE | jakość i liczebność BASE | automatycznie / tylko wg reguł | `RESOLVED 2026-08-24 — UD-04 OPTION A`: po sesji 180 ponowna ocena; BASE tylko według reguł, bez automatycznej kwalifikacji |
| C-03 | stary mixed universe ~9903 | Massive jako nowe źródło | dokładne rynki i typy instrumentów nie były zatwierdzone | wielkość, koszty, klasyfikacja | provider scope / USA / stary global | `RESOLVED 2026-08-24 — UD-01 OPTION A`: pełny katalog aktywnych spółek z zatwierdzonego zakresu Massive, jawna klasyfikacja; bez automatycznego kopiowania OLD |
| C-04 | historyczny fail-open przy braku mcap | potrzeba wiarygodnej BASE | brak mcap mógł pozostawić `base_ok=1` | fałszywe kwalifikacje | fail-open / reject / PENDING | `RESOLVED 2026-08-24 — UD-03 OPTION A`: `PENDING_DATA`, bez kwalifikacji i odrzucenia; ponowna ocena po uzupełnieniu |
| C-05 | OLD Investing search fallback | wymaganie prawidłowych URL | wyszukiwarka tickera nie jest bezpośrednim linkiem instrumentu | błędne przejścia | strict verified / search oznaczony | kierunek potwierdzony w SPEC |
| C-06 | jedna tabela `universe` | architektura V4.4 | stary model miesza właścicieli zapisu | locki, nadpisania, brak audytu | kopiować OLD / rozdzielić | SPEC rekomenduje rozdzielenie |
| C-07 | STAN: Git initialized | bieżący mirror | brak `.git` w dostępnej kopii | brak commit/tag w tej lokalizacji | odtworzyć Git później / pracować plikowo | `RESOLVED 2026-08-24`: dokumentacja ma repo i remote `Dareon99/skanerakcji`; nie dotyczy runtime OLD |
| C-08 | aktywny-packages README | D-006/D-008 | README nadal rekomendował anulowany CHARTS-RESTORE | ryzyko złego następnego kroku | aktualizacja indeksu | `RESOLVED`: indeks wskazuje aktualny kontrakt i roadmapę SKOOP |
| C-09 | użytkownik: BASE aktualizowane non stop | warstwowanie kosztów | dokładny cadence i definicja „non stop” nie należą do obecnego kontraktu | koszt Massive i świeżość | ustalić w pakiecie market sync | odroczone jawnie |
| C-10 | architektura V4.4: IPO co 6 h | sugestia użytkownika: 1× dziennie | różna częstotliwość kalendarza IPO | ruch Massive i świeżość korekt | 6 h / daily+retry | `RESOLVED 2026-08-24 — UD-09`: 1× po starcie regularnej sesji USA, opóźnienie po smoke teście, retry po błędzie |
| C-11 | odzyskany harmonogram ET/USA | wymaganie wielu giełd i pre/post USA | jeden kalendarz nie obsłuży wszystkich instrumentów ani zleceń | świece, liczniki sesji, egzekucja | per MIC/timezone/session phases | zapisane w §8.3; testy wymagane |
| C-12 | waga 800: otwarta pozycja | nowe zlecenie oczekujące | pending order nie jest jeszcze pozycją, ale wymaga pilnej ceny | kolejka i bezpieczeństwo egzekucji | wspólne 800 / osobne 900 | UD-11 |
| C-13 | wcześniejsza propozycja przełączania całego listingu naraz | korekta użytkownika: nie czekać na 5000 spółek | pełne przełączenie blokowałoby płynną pracę | UX i czas dostępności | cały zbiór / ostatnie poprawne dane per rekord | rozstrzygnięte: per rekord |
| C-14 | jeden globalny czas aktualizacji | wymaganie prostego czasu przy każdej spółce | globalny czas nie pokazuje wieku konkretnego rekordu | diagnostyka | globalny / per spółka | rozstrzygnięte: per spółka |
| C-15 | odzyskane wagi: portfel 800, cykl 500, IPO 400 | nowy porządek użytkownika | odzyskane wagi ustawiają portfel przed sygnałami i nie zawierają obserwacji | kolejność pracy nowego SKOOP | zachować r599 / nowe poziomy T0–T4 | rozstrzygnięte: nowe poziomy użytkownika |
| C-16 | czas giełdy przy aktualizacji | wymaganie użytkownika | czas giełdy jest mniej czytelny w codziennej pracy | prezentacja i diagnostyka | giełda / użytkownik | rozstrzygnięte: zawsze czas użytkownika |
| C-17 | próg lub limit liczby płynnych USA | wymaganie użytkownika | blok lub limit zatrzymałby aktualizację pozostałych spółek | kompletność i płynność procesu | bloki / ciągła kolejka | rozstrzygnięte: cała kolejka ADV20 malejąco |

## Bezpieczny stan podczas STOP

- `Stock Scanner OLD` i frozen bazy pozostają bez zmian;
- nie wykonujemy żądań Massive;
- nie tworzymy nowej bazy SKOOP;
- nie implementujemy importerów, workerów ani UI;
- aktywna paczka może zmieniać tylko dokumentację kontraktu;
- rollback runtime nie jest wymagany.

## Rozstrzygnięcia już wynikające z wymagań użytkownika

- trzy listy nie mogą powodować trzech kopii świec i profilu;
- IPO może być jednocześnie widoczne jako IPO i BASE;
- okno IPO liczymy w sesjach giełdowych;
- brak potwierdzonego linku nie może być przedstawiany jako prawidłowy direct URL;
- pola brakujące mają pozostać jawne, bez zgadywania.
- priorytet aktualizacji SKOOP: kliknięta → sygnały → obserwowane → portfele → płynne
  USA → pozostałe; odzyskane wagi r599 nie są tu źródłem prawdy.

`C-01` i `C-02` zamknięto decyzją UD-04 z 2026-08-24: zakończenie okna IPO nie
nadaje ani nie odbiera automatycznie BASE.
